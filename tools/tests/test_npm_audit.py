"""AUTH-005 cannot silently cover changed findings, inputs, time or production."""
import copy
from datetime import datetime, timedelta
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('npm_review', ROOT/'tools/check_npm_audit.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class AuditBoundary(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.report = json.loads((ROOT/'tools/tests/fixtures/npm-auth005-audit.json').read_text())
        self.policy = json.loads((ROOT/'infra/development-npm-review.json').read_text())
        for name in self.policy['source_inputs']:
            p = self.root/name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes((ROOT/name).read_bytes())
        self.policy['source_inputs'] = m.source_inputs(self.root)
        self.policy['review_status'] = 'reviewed'
        self.now = datetime.fromisoformat(self.policy['reviewed_at_utc']) + timedelta(seconds=1)

    def check(self, **kwargs):
        return m.validate(self.report, kwargs.get('code', 1), self.policy, self.root,
                          kwargs.get('scope', 'synthetic-development'), kwargs.get('now', self.now))

    def test_exact_review_retains_explicit_exception_status(self):
        self.assertEqual(self.check()['status'], 'pass_with_temporary_development_exception')

    def test_production_never_inherits_exception(self):
        with self.assertRaises(ValueError): self.check(scope='production')

    def test_expiry_and_future_review_fail_closed(self):
        for when in [datetime.fromisoformat(self.policy['expires_at_utc']), self.now-timedelta(days=1)]:
            with self.subTest(when=when), self.assertRaises(ValueError): self.check(now=when)

    def test_review_window_cannot_be_extended_beyond_three_days(self):
        self.policy['expires_at_utc'] = (self.now + timedelta(days=4)).isoformat()
        with self.assertRaises(ValueError): self.check()

    def test_changed_version_severity_or_advisory_is_not_covered(self):
        original = copy.deepcopy(self.report)
        for key, value in [('severity', 'critical'), ('via', ['different-advisory']), ('nodes', ['node_modules/other'])]:
            self.report = copy.deepcopy(original)
            self.report['vulnerabilities']['picomatch'][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError): self.check()

    def test_new_finding_is_not_covered(self):
        self.report['vulnerabilities']['another-package'] = {'severity': 'low'}
        self.report['metadata']['vulnerabilities']['total'] += 1
        with self.assertRaises(ValueError): self.check()

    def test_changed_source_lock_or_added_file_invalidates_review(self):
        p = self.root/'web/src/unreviewed.ts'
        p.write_text('export const change = true;')
        with self.assertRaises(ValueError): self.check()

    def test_audit_error_or_process_failure_is_not_a_pass(self):
        with self.assertRaises(ValueError): self.check(code=2)
        self.report['error'] = {'code': 'ENOAUDIT'}
        with self.assertRaises(ValueError): self.check()

    def test_incomplete_report_is_not_a_clean_pass(self):
        self.report = {'auditReportVersion': 2, 'vulnerabilities': {}, 'metadata': {}}
        with self.assertRaises(ValueError): self.check(code=0)

    def test_clean_report_needs_no_exception(self):
        self.report = {'auditReportVersion': 2, 'vulnerabilities': {}, 'metadata': {'vulnerabilities':
            {'info': 0, 'low': 0, 'moderate': 0, 'high': 0, 'critical': 0, 'total': 0}}}
        self.assertEqual(self.check(code=0, scope='production')['exceptions'], 0)
