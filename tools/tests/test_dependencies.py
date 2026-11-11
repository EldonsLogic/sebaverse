"""Dependency evidence fails closed on drift, unreviewed sources and advisories."""
from pathlib import Path
import importlib.util
import json
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('dependencies', ROOT / 'tools/check_dependencies.py')
dependencies = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dependencies)


class DependencyEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        manifest = json.loads((ROOT / 'development/evidence/f1-dependency-snapshot.json').read_text())
        paths = list(manifest['sha256']) + ['development/evidence/f1-dependency-snapshot.json', 'development/dependency-scope.json']
        for file in paths:
            p = self.root / file
            p.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / file, p)

    def tearDown(self):
        self.temp.cleanup()

    def change(self, file, mutate):
        p = self.root / file
        data = json.loads(p.read_text())
        mutate(data)
        p.write_text(json.dumps(data))

    def errors(self):
        return dependencies.check_snapshot(self.root)

    def test_actual_snapshot_valid(self):
        self.assertEqual([], self.errors())

    def test_lock_drift_invalidates_evidence(self):
        p = self.root / 'backend/uv.lock'
        p.write_text(p.read_text() + '\n# unexpected drift\n')
        self.assertTrue(any('drift' in e for e in self.errors()))

    def test_web_unpinned_range_rejected(self):
        self.change('web/package.json', lambda d: d['dependencies'].update(react='^19.3.1'))
        self.assertTrue(any('Unpinned' in e for e in self.errors()))

    def test_untrusted_registry_rejected(self):
        def mutate(d):
            next(v for k,v in d['packages'].items() if k)['resolved'] = 'https://untrusted.invalid/package.tgz'
        self.change('web/package-lock.json', mutate)
        self.assertTrue(any('Unexpected web artifact' in e for e in self.errors()))

    def test_python_advisory_blocks_gate(self):
        self.change('development/evidence/f1-backend-audit.json', lambda d: d['dependencies'][0].update(vulns=[{'id':'TEST-ADVISORY'}]))
        self.assertTrue(any('Unresolved backend advisory' in e for e in self.errors()))

    def test_incomplete_audit_coverage_rejected(self):
        self.change('development/evidence/f1-backend-audit.json', lambda d: d['dependencies'].pop())
        self.assertTrue(any('exact locked graph' in e for e in self.errors()))

    def test_npm_advisory_blocks_gate(self):
        self.change('development/evidence/f1-web-audit.json', lambda d: d['metadata']['vulnerabilities'].update(total=1))
        self.assertTrue(any('web audit result' in e for e in self.errors()))

    def test_ungated_model_asset_rejected(self):
        self.change('development/dependency-scope.json', lambda d: d.update(model_assets_used=['unexpected-weights']))
        self.assertTrue(any('Unexpected enabled model' in e for e in self.errors()))


if __name__ == '__main__':
    unittest.main()
