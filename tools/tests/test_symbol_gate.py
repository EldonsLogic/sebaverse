"""Synthetic hashed importer evidence; no native object loading or database."""
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

m = load('symbol_gate_tests', ROOT / 'tools/security/check_reports.py')
symbols = load('symbol_gate_parser', ROOT / 'tools/security/native_symbols.py')

class SymbolGateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.folder = self.root / 'work/f2-security'
        (self.folder / 'native-symbols').mkdir(parents=True)
        helper = self.root / 'tools/security/native_symbols.py'
        helper.parent.mkdir(parents=True)
        shutil.copyfile(ROOT / 'tools/security/native_symbols.py', helper)
        self.native = {'libraries': []}
        self.objects = []
        self.now = datetime.now(timezone.utc)
        (self.root / '.python-version').write_text('3.12.13')
        venv = self.root / 'backend/.venv'
        (venv / 'lib/python3.12/site-packages').mkdir(parents=True)
        (venv / 'pyvenv.cfg').write_text('home = ' + str(venv / 'bin') + '\ninclude-system-site-packages = false\n')
        for name, category, symbol in [('libkrb5.so.3.3', 'reviewed_libpq_closure', 'regcomp@GLIBC_2.2.5'),
                ('backend/.venv/bin/python', 'python_executable', 'synthetic_nontarget')]:
            p = self.root / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(b'synthetic object, never loaded: ' + name.encode())
            digest = hashlib.sha256(p.read_bytes()).hexdigest()
            raw = self.folder / 'native-symbols' / (digest + '.symbols.txt')
            text = '  1: 00000000 0 FUNC GLOBAL DEFAULT UND ' + symbol + '\n'
            raw.write_text(text)
            self.objects.append({'path': str(p), 'sha256': digest, 'category': category,
                'symbol_output': str(raw), 'symbol_output_sha256': hashlib.sha256(raw.read_bytes()).hexdigest(),
                **symbols.parse_symbols(text)})
            if category == 'reviewed_libpq_closure':
                self.native['libraries'].append({'path': str(p), 'canonical_path': str(p), 'owner': 'libkrb5-3:amd64', 'sha256': digest})
        path = self.folder / 'system-native.json'
        path.write_text(json.dumps(self.native))
        self.report = {'schema_version': 1, 'created_at_utc': self.now.isoformat(),
                      'native_manifest_sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'objects': self.objects}

    def bind(self, path, expected=None):
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if expected is not None and expected != digest:
            raise ValueError('Bound source bytes changed')
        return digest

    def check(self):
        (self.folder / 'native-symbols.json').write_text(json.dumps(self.report))
        m.validate_symbol_evidence(self.folder, self.root, self.native, self.bind, self.now)

    def test_complete_static_boundary_passes(self):
        self.check()

    def test_forged_classification_or_changed_native_object_rejects(self):
        self.objects[0]['target_imports'] = []
        with self.assertRaisesRegex(ValueError, 'classification'):
            self.check()
        self.objects[0]['target_imports'] = ['regcomp@GLIBC_2.2.5']
        Path(self.objects[0]['path']).write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError, 'bytes'):
            self.check()

    def test_wide_scanf_or_different_regex_importer_requires_re_review(self):
        raw = Path(self.objects[0]['symbol_output'])
        text = '  1: 00000000 0 FUNC GLOBAL DEFAULT UND __isoc99_swscanf@GLIBC_2.7\n'
        raw.write_text(text)
        self.objects[0].update(symbol_output_sha256=hashlib.sha256(raw.read_bytes()).hexdigest(), **symbols.parse_symbols(text))
        with self.assertRaisesRegex(ValueError, 'Wide-scanf'):
            self.check()

    def test_new_available_extension_invalidates_object_set(self):
        extra = self.root / 'backend/.venv/lib/python3.12/site-packages/new_native.so'
        extra.write_bytes(b'synthetic extension, never executed')
        digest = hashlib.sha256(extra.read_bytes()).hexdigest()
        raw = self.folder / 'native-symbols' / (digest + '.symbols.txt')
        text = '  1: 00000000 0 FUNC GLOBAL DEFAULT UND synthetic_nontarget\n'
        raw.write_text(text)
        item = {'path': str(extra), 'sha256': digest, 'category': 'available_python_extension_not_observed_loaded',
                'symbol_output': str(raw), 'symbol_output_sha256': hashlib.sha256(raw.read_bytes()).hexdigest(),
                **symbols.parse_symbols(text)}
        self.objects.append(item)
        self.check()
        self.objects.pop()
        with self.assertRaisesRegex(ValueError, 'coverage'):
            self.check()

    def test_missing_python_or_native_coverage_rejects(self):
        self.objects.pop()
        with self.assertRaisesRegex(ValueError, 'coverage'):
            self.check()
