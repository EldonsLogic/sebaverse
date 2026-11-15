"""Static ELF symbol inventory only: never loads inspected objects or connects to DB."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import sys
import sysconfig

ROOT = Path(__file__).resolve().parents[2]
TARGET = re.compile(r'^(?:(?:__isoc(?:99|23)_|__|_IO_)?(?:v?wscanf|v?fwscanf|v?swscanf)(?:_chk|_internal)?)$|^reg(?:comp|exec)$')
DYNAMIC = {'dlopen', 'dlmopen', 'dlsym', '__libc_dlopen_mode'}


def digest(path):
    value = hashlib.sha256()
    with path.open('rb') as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b''):
            value.update(block)
    return value.hexdigest()


def parse_symbols(text):
    imports, definitions = set(), set()
    for line in text.splitlines():
        match = re.match(r'^\s*\d+:\s+\S+\s+\d+\s+\S+\s+\S+\s+\S+\s+(\S+)\s+(\S+)', line)
        if match:
            section, name = match.groups()
            (imports if section == 'UND' else definitions).add(name)
    if not imports and not definitions:
        raise ValueError('No parseable ELF symbols')
    base = lambda name: name.split('@', 1)[0]
    return {'undefined': sorted(imports), 'target_imports': sorted(n for n in imports if TARGET.fullmatch(base(n))),
            'target_definitions': sorted(n for n in definitions if TARGET.fullmatch(base(n))),
            'dynamic_lookup_imports': sorted(n for n in imports if base(n) in DYNAMIC)}


def inspect(path, output):
    path = path.resolve(strict=True)
    if not path.is_file() or path.stat().st_size > 128 * 1024 * 1024:
        raise ValueError('Non-file or oversized ELF')
    with path.open('rb') as handle:
        if handle.read(4) != b'\x7fELF':
            raise ValueError('Expected ELF file')
    before = digest(path)
    result = subprocess.run(['/usr/bin/readelf', '-WsW', str(path)], check=True, capture_output=True, timeout=30)
    if len(result.stdout) > 32 * 1024 * 1024 or digest(path) != before:
        raise ValueError('Symbol output oversized or inspected file changed')
    raw = output / (before + '.symbols.txt')
    raw.write_bytes(result.stdout)
    return dict(path=str(path), sha256=before, symbol_output=str(raw), symbol_output_sha256=digest(raw),
                **parse_symbols(result.stdout.decode('utf-8', errors='strict')))


def discover_objects(root, native):
    """Recompute the full reviewed Linux layout without loading any object."""
    root = Path(root).resolve()
    version = (root / '.python-version').read_text().strip()
    if not re.fullmatch(r'3\.12\.\d+', version):
        raise ValueError('Unsupported scoped Python version')
    series = '.'.join(version.split('.')[:2])
    venv = root / 'backend/.venv'
    executable = (venv / 'bin/python').resolve(strict=True)
    base = executable.parent.parent
    stdlib = (base / 'lib' / ('python' + series)).resolve(strict=True)
    platlib = (venv / 'lib' / ('python' + series) / 'site-packages').resolve(strict=True)
    cfg = dict(line.split('=', 1) for line in (venv / 'pyvenv.cfg').read_text().splitlines() if '=' in line)
    cfg = {key.strip(): value.strip() for key, value in cfg.items()}
    if cfg.get('include-system-site-packages') != 'false' or Path(cfg.get('home', '')).resolve() != executable.parent:
        raise ValueError('Unexpected virtual environment source/layout')
    paths, categories = set(), {}
    for row in native['libraries']:
        path = Path(row.get('canonical_path', row['path'])).resolve(strict=True)
        if digest(path) != row['sha256']:
            raise ValueError('Reviewed native library hash mismatch')
        paths.add(path)
        categories[str(path)] = 'reviewed_libpq_closure'
    paths.add(executable)
    categories[str(executable)] = 'python_executable'
    for name in ('libpython' + series + '.so', 'libpython' + series + '.so.1.0'):
        if (base / 'lib' / name).is_file():
            path = (base / 'lib' / name).resolve()
            paths.add(path)
            categories[str(path)] = 'libpython'
    for tree in {stdlib, platlib}:
        for file in tree.rglob('*.so'):
            path = file.resolve(strict=True)
            if not path.is_relative_to(tree):
                raise ValueError('Extension symlink escapes interpreter tree')
            paths.add(path)
            categories[str(path)] = 'available_python_extension_not_observed_loaded'
            if len(paths) > 2000:
                raise ValueError('Extension inventory exceeds bound')
    return paths, categories, stdlib, platlib


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-root', default='work/f2-security')
    args = parser.parse_args()
    if platform.system() != 'Linux' or any(v for k, v in os.environ.items() if k.startswith(('LD_', 'DYLD_'))):
        raise ValueError('Linux runner with no loader overrides required')
    if Path(sys.prefix).resolve() != (ROOT / 'backend/.venv').resolve():
        raise ValueError('Run using the reviewed backend virtualenv interpreter')
    output = (ROOT / args.output_root).resolve()
    if not output.is_relative_to((ROOT / 'work').resolve()):
        raise ValueError('Output outside repository work')
    manifest_path = output / 'system-native.json'
    native = json.loads(manifest_path.read_text())
    paths, categories, stdlib, platlib = discover_objects(ROOT, native)
    if Path(sysconfig.get_path('stdlib')).resolve() != stdlib or Path(sysconfig.get_path('platlib')).resolve() != platlib:
        raise ValueError('Actual interpreter discovery differs from scoped layout')
    raw = output / 'native-symbols'
    raw.mkdir(exist_ok=True)
    entries = [dict(category=categories[str(path)], **inspect(path, raw)) for path in sorted(paths)]
    report = {'schema_version': 1, 'created_at_utc': datetime.now(timezone.utc).isoformat(),
              'native_manifest_sha256': digest(manifest_path), 'python_version': sys.version,
              'objects': entries, 'limitations': ['Static imports/definitions only, not a runtime call graph or safety verdict.',
              'Available Python extensions inventoried without import; their transitive dependencies are not a complete process closure.',
              'Dynamic lookup, internal direct calls, plugins, subprocesses and input-dependent reachability remain unresolved.',
              'No database connection or inspected-object execution was performed.']}
    (output / 'native-symbols.json').write_text(json.dumps(report, indent=2) + '\n')


if __name__ == '__main__':
    main()
