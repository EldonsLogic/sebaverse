"""AUTH-022: end-to-end evaluate() tests for synthetic-ci vs strict standard scope."""

from datetime import timedelta
import importlib.util
import json
from pathlib import Path
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
_checker_spec = importlib.util.spec_from_file_location('auth022_checker', ROOT / 'tools/security/check_reports.py')
m = importlib.util.module_from_spec(_checker_spec)
_checker_spec.loader.exec_module(m)

_base_spec = importlib.util.spec_from_file_location('auth022_base_tests', ROOT / 'tools/tests/test_security_reports.py')
_base_mod = importlib.util.module_from_spec(_base_spec)
_base_spec.loader.exec_module(_base_mod)


class Auth022EvaluatePolicyTests(unittest.TestCase):
    def setUp(self):
        self.fx = _base_mod.SecurityReportPolicyTests('test_unreviewed_medium_fails')
        self.fx.setUp()
        self.addCleanup(self.fx.doCleanups)
        self.addCleanup(self.fx.temp.cleanup)

    def _eval(self, scope='standard'):
        return m.evaluate(self.fx.directory, root=self.fx.root, now=self.fx.now, execution_scope=scope)

    def _report(self, output, filename):
        return next(r for r in output['reports'] if r['file'] == filename)

    def test_unreviewed_medium_os_finding_fails_standard_but_records_nonblocking_in_synthetic_ci(self):
        self.fx.finding(self.fx.match(severity='Medium', package='libpq5', version='17.11-1'), report='system-native-cves.json', reviewed=False)

        std = self._eval('standard')
        self.assertEqual(std['status'], 'fail')
        self.assertIn('findings require explicit review', ' '.join(std['errors']))

        syn = self._eval('synthetic-ci')
        self.assertEqual(syn['status'], 'pass', syn['errors'])
        self.assertEqual(self._report(syn, 'system-native-cves.json')['unreviewed_nonblocking'], 1)
        self.assertIn('AUTH-022 synthetic-ci', syn['policy'])

    def test_reviewed_medium_with_released_fix_fails_standard_but_records_in_synthetic_ci(self):
        match = self.fx.match(severity='Medium', package='libpq5', version='17.11-1')
        match['vulnerability']['fix'] = {'state': 'fixed', 'versions': ['17.11-2']}
        self.fx.finding(match, report='system-native-cves.json', reviewed=True)

        std = self._eval('standard')
        self.assertEqual(std['status'], 'fail')
        self.assertIn('fix released', ' '.join(std['errors']))

        syn = self._eval('synthetic-ci')
        self.assertEqual(syn['status'], 'pass', syn['errors'])
        self.assertEqual(self._report(syn, 'system-native-cves.json')['superseded_awaiting_image_rebuild'], 1)

    def test_synthetic_ci_still_blocks_kev_critical_native_high_unlisted_image_high_and_postgres_core(self):
        # 1. System-native High still blocks in synthetic-ci
        self.fx.finding(self.fx.match(severity='High', package='libpq5', version='17.11-1'), report='system-native-cves.json', reviewed=False)
        res_native = self._eval('synthetic-ci')
        self.assertEqual(res_native['status'], 'fail')
        self.assertIn('unresolved high/critical/unknown', ' '.join(res_native['errors']))

        # 2. Unlisted image package High (libc6) still blocks in synthetic-ci
        self.fx.mutate('work/f2-security/system-native-cves.json', lambda d: d.update(matches=[]))
        self.fx.finding(self.fx.match(severity='High', package='libc6', version='1.0-1'), report='image-cves.json', reviewed=False)
        res_unlisted = self._eval('synthetic-ci')
        self.assertEqual(res_unlisted['status'], 'fail')
        self.assertIn('unresolved high/critical/unknown', ' '.join(res_unlisted['errors']))

        # 3. Critical on listed image package (libssl3) still blocks in synthetic-ci
        self.fx.finding(self.fx.match(severity='Critical', package='libssl3', version='1.0-1'), report='image-cves.json', reviewed=False)
        res_crit = self._eval('synthetic-ci')
        self.assertEqual(res_crit['status'], 'fail')
        self.assertIn('unresolved high/critical/unknown', ' '.join(res_crit['errors']))

        # 4. KEV on listed image package (libssl3) still blocks in synthetic-ci
        kev_id = json.loads((self.fx.directory / 'kev.json').read_text())['vulnerabilities'][0]['cveID']
        self.fx.finding(self.fx.match(severity='High', identifier=kev_id, package='libssl3', version='1.0-1'), report='image-cves.json', reviewed=False)
        res_kev = self._eval('synthetic-ci')
        self.assertEqual(res_kev['status'], 'fail')
        self.assertIn('known-exploited', ' '.join(res_kev['errors']))

        # 5. Unreviewed Medium in postgres-core-cves.json still blocks in synthetic-ci
        self.fx.mutate('work/f2-security/image-cves.json', lambda d: d.update(matches=[]))
        core_match = self.fx.match(severity='Medium', identifier='CVE-2026-77777', package='postgresql', version='17.11')
        self.fx.finding(core_match, report='postgres-core-cves.json', reviewed=False)
        res_core = self._eval('synthetic-ci')
        self.assertEqual(res_core['status'], 'fail')
        self.assertIn('findings require explicit review', ' '.join(res_core['errors']))

    def test_listed_unused_feature_image_high_requires_active_auth007_window_and_stays_blocked_in_standard(self):
        match = self.fx.match(severity='High', identifier='CVE-2026-124709', package='libssl3', version='1.0-1')
        match['vulnerability']['fix'] = {'state': 'fixed', 'versions': ['1.0-2']}
        self.fx.finding(match, report='image-cves.json', reviewed=False)

        # Without active AUTH-007 exception_summary (no synthetic-openssl-review.json), synthetic-ci MUST fail
        res_no_auth007 = self._eval('synthetic-ci')
        self.assertEqual(res_no_auth007['status'], 'fail')

        # With valid AUTH-007 exception_summary, synthetic-ci passes and records synthetic_unreached_image_high
        self.fx.write('infra/synthetic-openssl-review.json', {'expires_at_utc': (self.fx.now + timedelta(days=1)).isoformat()})
        with patch.object(m, 'validate_openssl_exception', return_value=set()):
            syn = self._eval('synthetic-ci')
            self.assertEqual(syn['status'], 'pass', syn['errors'])
            img = self._report(syn, 'image-cves.json')
            self.assertEqual(img['synthetic_unreached_image_high'], 1)
            self.assertEqual(img['unreviewed_nonblocking'], 1)

            # Standard scope STILL fails even with the review file present
            std = self._eval('standard')
            self.assertEqual(std['status'], 'fail')

    def test_review_max_age_and_package_list_bounds(self):
        self.assertEqual(m.REVIEW_MAX_AGE, timedelta(days=30))
        self.assertEqual(m.SYNTHETIC_CI_UNREACHED_IMAGE_PACKAGES, frozenset({'libcrypto3', 'libssl3', 'libxml2'}))
        self.assertNotIn('postgresql', m.SYNTHETIC_CI_UNREACHED_IMAGE_PACKAGES)
        self.assertNotIn('libpq5', m.SYNTHETIC_CI_UNREACHED_IMAGE_PACKAGES)
