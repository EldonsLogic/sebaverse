"""Start only a pre-reviewed ephemeral loopback PG, run real tests, then remove it."""
from pathlib import Path
import json
import hashlib
import os
import secrets
import subprocess
import sys
import tempfile
import time
import uuid

ROOT=Path(__file__).resolve().parents[1]


def run(command,**kwargs):
    return subprocess.run(command,cwd=ROOT,check=True,text=True,**kwargs)


def main():
    report_path=ROOT/'work/f2-security/preuse-result.json'
    report=json.loads(report_path.read_text())
    pin=json.loads((ROOT/'infra/images.lock.json').read_text())['postgres']
    if report.get('status')!='pass' or report.get('image_reference')!=pin['reference']:
        raise SystemExit('Native/image pre-use gate has not passed for this pin')
    native=json.loads((ROOT/'work/f2-security/system-native.json').read_text())
    for library in native['libraries']:
        path=Path(library.get('canonical_path',library['path']))
        if hashlib.sha256(path.read_bytes()).hexdigest()!=library['sha256']:
            raise SystemExit('System native files changed since review; rerun the pre-use gate')
    for evidence in report['reports']:
        if hashlib.sha256((ROOT/'work/f2-security'/evidence['file']).read_bytes()).hexdigest()!=evidence['sha256']:
            raise SystemExit('Native advisory evidence changed; rerun review')
    if not sys.platform.startswith('linux'):
        raise SystemExit('Approved system-libpq integration currently targets tested Linux; macOS DB remains gated')
    suffix=uuid.uuid4().hex[:10];name='sebaverse-f2-'+suffix
    password=secrets.token_urlsafe(24)
    envdir=ROOT/'.local/f2';envdir.mkdir(parents=True,exist_ok=True)
    envfile=envdir/(suffix+'.env');envfile.write_text('POSTGRES_DB=sebaverse_f2\nPOSTGRES_USER=postgres\nPOSTGRES_PASSWORD='+password+'\nPGDATA=/tmp/pgdata\n');envfile.chmod(0o600)
    container=None
    try:
        container=run(['docker','run','-d','--name',name,'--label','dev.sebaverse.task=DEV-006','--user','postgres','--read-only','--tmpfs','/tmp:rw,mode=1777','--tmpfs','/var/run/postgresql:rw,mode=3777','--cap-drop','ALL','--security-opt','no-new-privileges','--publish','127.0.0.1::5432','--env-file',str(envfile),'--platform','linux/amd64',pin['reference'],'postgres','-c','unix_socket_directories=/tmp'],capture_output=True).stdout.strip()
        ready=False
        for _ in range(60):
            if subprocess.run(['docker','exec',container,'pg_isready','-U','postgres','-d','sebaverse_f2'],capture_output=True).returncode==0:
                ready=True;break
            time.sleep(1)
        if not ready:raise RuntimeError('Ephemeral PostgreSQL did not become ready')
        port=run(['docker','port',container,'5432/tcp'],capture_output=True).stdout.strip().split(':')[-1]
        env=dict(os.environ,SEBAVERSE_ENV='local',DJANGO_DEBUG='1',PSYCOPG_IMPL='python',POSTGRES_DB='sebaverse_f2',POSTGRES_USER='postgres',POSTGRES_PASSWORD=password,POSTGRES_HOST='127.0.0.1',POSTGRES_PORT=port,SEBAVERSE_TEST_POSTGRES='1')
        run([str(ROOT/'backend/.venv/bin/python'),'-m','pytest','backend/tests/test_postgres_integration.py','-q'],env=env)
        output={'status':'pass','task':'DEV-006','database':'PostgreSQL17 real instance','image':pin['reference'],'native_preuse_report':'work/f2-security/preuse-result.json','binding':'PSYCOPG_IMPL=python with reviewed system libpq','checks':['actual framework migrations','server major17','no pending migrations','synthetic session roundtrip/cleanup','database readiness200'],'teardown':'pending'}
    finally:
        if container:
            run(['docker','rm','-f','-v',container],capture_output=True)
        envfile.unlink(missing_ok=True)
    output['teardown']='task-owned container and anonymous volumes removed; synthetic env removed'
    (ROOT/'work/f2-security/postgres-integration.json').write_text(json.dumps(output,indent=2)+'\n')
    print(json.dumps(output,indent=2))


if __name__=='__main__':main()
