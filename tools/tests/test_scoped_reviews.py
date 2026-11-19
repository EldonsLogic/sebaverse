"""Scope/expiry/code-drift tests; synthetic source only, no native or DB use."""
from datetime import datetime, timezone, timedelta
import copy
import hashlib
import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('review_scope_tests', ROOT / 'tools/security/check_reports.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class ScopedReviewTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        for name in m.SCOPED_WORKLOAD_FILES:
            p = self.root / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text('synthetic source, never executed')
        self.now = datetime.now(timezone.utc)
        self.row = {'disposition': 'restricted_synthetic_ci_only', 'scope_id': 'DEV-006-synthetic-ci', 'reviewed_at_utc': self.now.isoformat(),
                    'expires_at_utc': (self.now + timedelta(days=30)).isoformat(),
                    'scope_inputs': {name: hashlib.sha256(path.read_bytes()).hexdigest()
                                     for name, path in m.scoped_workload_paths(self.root).items()}}

    def bind(self, path, expected):
        m.require(hashlib.sha256(path.read_bytes()).hexdigest() == expected, 'Scoped source bytes changed')

    def check(self, row=None, runtime=None):
        m.validate_scoped_review(row or self.row, runtime or {'type': 'derived-oci'}, self.root, self.bind, self.now)

    def test_exact_current_short_lived_review_passes(self):
        self.check()

    def test_missing_authority_wrong_scope_or_expired_review_fails(self):
        with self.assertRaisesRegex(ValueError, 'authority'):
            m.validate_scoped_review(self.row, None, self.root, self.bind, self.now)
        for field, value in [('disposition', 'unscoped'), ('scope_id', 'production'), ('expires_at_utc', (self.now - timedelta(seconds=1)).isoformat()),
                             ('expires_at_utc', (self.now + timedelta(days=30, seconds=1)).isoformat()),
                             ('reviewed_at_utc', (self.now - timedelta(days=31)).isoformat())]:
            row = copy.deepcopy(self.row)
            row[field] = value
            with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                self.check(row)

    def test_changed_runtime_surface_requires_fresh_review(self):
        for name in m.SCOPED_WORKLOAD_FILES:
            source = self.root / name
            original = source.read_bytes()
            source.write_text('changed database driver or connection behavior')
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, 'bytes'):
                self.check()
            source.write_bytes(original)

    def test_application_feature_code_does_not_invalidate_review(self):
        new = self.root / 'backend/modules/new_feature.py'
        new.parent.mkdir(parents=True)
        new.write_text('new synthetic feature')
        self.check()

    def test_missing_runtime_surface_file_fails(self):
        (self.root / 'backend/config/settings.py').unlink()
        with self.assertRaisesRegex(ValueError, 'missing'):
            self.check()
