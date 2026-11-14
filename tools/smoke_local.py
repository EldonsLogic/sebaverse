"""Real loopback app/browser lifecycle, without DB credentials or external services."""
from pathlib import Path
import json
import os
import shutil
import socket
import subprocess
import time
import urllib.error
import urllib.request

ROOT=Path(__file__).resolve().parents[1]


def main():
    with socket.socket() as probe:
        probe.bind(('127.0.0.1',0));port=probe.getsockname()[1]
    base=f'http://127.0.0.1:{port}'
    env={k:v for k,v in os.environ.items() if not k.startswith('POSTGRES_') and k not in ['DJANGO_SECRET_KEY','DJANGO_ALLOWED_HOSTS','SEBAVERSE_TEST_POSTGRES']}
    env.update(SEBAVERSE_ENV='local',DJANGO_DEBUG='1',PYTHONPATH=str(ROOT/'backend'),SEBAVERSE_BASE_URL=base)
    log=ROOT/'work/f2-app.log';log.parent.mkdir(exist_ok=True)
    with log.open('w') as output:
        child=subprocess.Popen([str(ROOT/'backend/.venv/bin/python'),'-m','uvicorn','config.asgi:application','--host','127.0.0.1','--port',str(port),'--no-access-log'],cwd=ROOT,env=env,stdout=output,stderr=subprocess.STDOUT)
        try:
            live=False
            for _ in range(100):
                if child.poll() is not None:raise RuntimeError('Task-owned app exited before startup; inspect work/f2-app.log')
                try:
                    with urllib.request.urlopen(base+'/api/v1/health/',timeout=1) as response:
                        live=json.load(response)=={'status':'ok'}
                except (urllib.error.URLError,TimeoutError):pass
                if live:break
                time.sleep(.1)
            if not live:raise RuntimeError('Local health did not become available')
            try:
                urllib.request.urlopen(base+'/api/v1/ready/',timeout=2)
                raise AssertionError('Unconfigured DB must not report ready')
            except urllib.error.HTTPError as error:
                assert error.code==503
            node=shutil.which('node')
            candidates=[node,'/Users/eldon/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node']
            required=(ROOT/'.node-version').read_text().strip()
            selected=next((p for p in candidates if p and Path(p).is_file() and subprocess.check_output([p,'--version'],text=True).strip()=='v'+required),None)
            if not selected:raise RuntimeError('Pinned Node runtime unavailable')
            subprocess.run([selected,'tools/browser/smoke.mjs'],cwd=ROOT,env=env,check=True)
        finally:
            child.terminate()
            try:child.wait(timeout=10)
            except subprocess.TimeoutExpired:child.kill();child.wait(timeout=5)
    with socket.socket() as check:
        assert check.connect_ex(('127.0.0.1',port))!=0,'Task-owned server remained reachable after teardown'
    report={'status':'pass','bind':'127.0.0.1','health':200,'unconfigured_database_readiness':503,'browser_report':'outputs/f2-local-skeleton/browser-report.json','teardown':'Only task-owned process terminated; port no longer reachable','scope':'No DB credentials, external API keys, real data or deployment required'}
    directory=ROOT/'work/f2-security';directory.mkdir(parents=True,exist_ok=True)
    (directory/'local-lifecycle.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
