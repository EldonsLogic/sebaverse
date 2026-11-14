"""Verify the F1 dependency snapshot; no installation or task-command execution."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def check_snapshot(root):
    errors = []
    try:
        read = lambda p: json.loads((root / p).read_text())
        snapshot='third-party/dependency-snapshot.json' if (root/'third-party/dependency-snapshot.json').is_file() else 'development/evidence/f1-dependency-snapshot.json'
        manifest=read(snapshot)
        for file, expected in manifest['sha256'].items():
            path = root / file
            if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
                errors.append('Dependency evidence/lock drift: ' + file)
        package = read('web/package.json')
        lock = read('web/package-lock.json')
        if not package.get('private') or lock.get('lockfileVersion') != 3:
            errors.append('Web private package/lock contract invalid')
        for group in ['dependencies', 'devDependencies']:
            if package.get(group, {}) != lock['packages'][''].get(group, {}):
                errors.append('Web manifest differs from lock: ' + group)
            for name, version in package.get(group, {}).items():
                if not re.fullmatch(r'\d+\.\d+\.\d+', version):
                    errors.append('Unpinned direct web dependency: ' + name)
        for name, entry in lock.get('packages', {}).items():
            if not name:
                continue
            if not entry.get('integrity') or not entry.get('resolved', '').startswith('https://registry.npmjs.org/'):
                errors.append('Unexpected web artifact/integrity: ' + name)
            if not entry.get('license'):
                errors.append('Missing declared package license: ' + name)
        uvlock = (root / 'backend/uv.lock').read_text()
        locked_python = set()
        canon = lambda value: re.sub(r'[-_.]+', '-', value).lower()
        for block in uvlock.split('[[package]]')[1:]:
            if 'source = { registry' in block:
                name = re.search(r'^name = "([^"]+)"', block, re.M)
                version = re.search(r'^version = "([^"]+)"', block, re.M)
                if name and version:
                    locked_python.add((canon(name[1]), version[1]))
        backend_audit = read('development/evidence/f1-backend-audit.json')
        audited_python = {(canon(x['name']), x['version']) for x in backend_audit.get('dependencies', [])}
        if not locked_python or audited_python != locked_python:
            errors.append('Backend audit does not cover the exact locked graph')
        if not backend_audit.get('dependencies'):
            errors.append('Missing backend audit coverage')
        if any(x.get('vulns') for x in backend_audit.get('dependencies', [])):
            errors.append('Unresolved backend advisory')
        web_audit = read('development/evidence/f1-web-audit.json')
        if web_audit.get('metadata', {}).get('vulnerabilities', {}).get('total') != 0:
            errors.append('Unresolved or missing web audit result')
        if not read('third-party/backend-licenses.json').get('packages'):
            errors.append('Missing backend license inventory')
        if not read('third-party/web-licenses.json').get('packages'):
            errors.append('Missing web license inventory')
        scope = read('development/dependency-scope.json')
        if scope.get('model_assets_used') != []:
            errors.append('Unexpected enabled model assets in F1')
        if not scope.get('disabled_until_own_gate'):
            errors.append('Deferred dependency gates missing')
        uvlock = (root / 'backend/uv.lock').read_text()
        if 'https://pypi.org/simple' not in uvlock or 'hash = "sha256:' not in uvlock:
            errors.append('Backend lock registry/hashes missing')
        for forbidden in ['edustudio', 'deeptutor', 'learnhouse', 'docling']:
            if re.search(r'name\s*=\s*"' + forbidden + '"', uvlock, re.I):
                errors.append('Disabled upstream component in backend lock: ' + forbidden)
    except (OSError, ValueError, KeyError) as exc:
        errors.append('Dependency evidence unavailable: ' + str(exc))
    return errors


def runtime_checks(root):
    errors = []
    python = root / 'backend/.venv/bin/python'
    if not python.exists():
        return ['Backend isolated environment absent; run documented locked wheel-only sync']
    required_python = tuple(map(int, (root / '.python-version').read_text().strip().split('.')))
    smoke = 'import sys,django,rest_framework,uvicorn,psycopg; assert sys.version_info[:3]==' + repr(required_python) + '; print(django.get_version(),rest_framework.VERSION,uvicorn.__version__,psycopg.__version__)'
    result = subprocess.run([str(python), '-c', smoke], capture_output=True, text=True)
    if result.returncode:
        errors.append('Backend import/version smoke failed: ' + result.stderr[-500:])
    expected = {p['name'].lower().replace('_','-'): p['version'] for p in json.loads((root / 'third-party/backend-licenses.json').read_text())['packages'] if p.get('installed_here')}
    query = 'import importlib.metadata as m,json;print(json.dumps({d.metadata["Name"].lower().replace("_","-"):d.version for d in m.distributions()}))'
    actual = subprocess.run([str(python), '-c', query], capture_output=True, text=True)
    if actual.returncode or json.loads(actual.stdout or '{}') != expected:
        errors.append('Installed backend graph differs from inspected locked environment')
    required = (root / '.node-version').read_text().strip()
    candidates = [shutil.which('node'), '/Users/eldon/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node']
    node = None
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            result = subprocess.run([candidate, '--version'], capture_output=True, text=True)
            if result.returncode == 0 and result.stdout.strip() == 'v' + required:
                node = candidate
                break
    if not node:
        errors.append('Required Node ' + required + ' unavailable; global runtime is not changed automatically')
    else:
        npm = shutil.which('npm')
        environment = dict(os.environ, PATH=str(Path(node).parent) + os.pathsep + os.environ.get('PATH', ''))
        required_npm = json.loads((root / 'web/package.json').read_text())['packageManager'].split('@')[-1]
        actual_npm = subprocess.run([npm, '--version'], env=environment, capture_output=True, text=True) if npm else None
        if actual_npm is None or actual_npm.returncode or actual_npm.stdout.strip() != required_npm:
            errors.append('Required exact npm toolchain unavailable: ' + required_npm)
        smoke = "import React from 'react'; import {renderToStaticMarkup} from 'react-dom/server'; import {QueryClient} from '@tanstack/react-query'; import {createMemoryRouter} from 'react-router'; if(renderToStaticMarkup(React.createElement('span',null,'fixture'))!=='<span>fixture</span>')throw Error('render');new QueryClient();createMemoryRouter([{path:'/',element:null}]);"
        direct = json.loads((root / 'web/package.json').read_text())
        expected_web = dict(direct.get('dependencies', {}), **direct.get('devDependencies', {}))
        smoke += "import fs from 'node:fs';const expected=" + json.dumps(expected_web) + ";for(const [name,version] of Object.entries(expected)){if(JSON.parse(fs.readFileSync('node_modules/'+name+'/package.json','utf8')).version!==version)throw Error('version drift: '+name);}"
        result = subprocess.run([node, '--input-type=module', '-e', smoke], cwd=root / 'web', capture_output=True, text=True)
        if result.returncode:
            errors.append('Web library smoke failed: ' + result.stderr[-500:])
    return errors


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--static', action='store_true', help='Verify committed closure/evidence without local installations')
    args = parser.parse_args()
    errors = check_snapshot(ROOT)
    if not args.static and not errors:
        errors += runtime_checks(ROOT)
    if errors:
        print('Dependency checks: FAIL')
        for error in errors:
            print('- ' + error)
        return 1
    print('Dependency checks: PASS (' + ('static evidence' if args.static else 'evidence + local import/render smoke') + ')')
    print('- Exact locks, integrity, license inventories and known-advisory reports match recorded snapshot.')
    print('- No model assets or deferred parser/LMS/tutor runtime enabled; no app behavior/security certification claimed.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
