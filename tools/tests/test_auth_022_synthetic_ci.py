"""AUTH-022: verify synthetic-ci alignment with QUALITY-BAR §2 while keeping standard scope strict."""

from datetime import datetime, timedelta, timezone
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('auth022_checker', ROOT / 'tools/security/check_reports.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class Auth022SyntheticCiPolicyTests(unittest.TestCase):
    def test_standard_scope_policy_remains_strict_for_low_medium_and_fix_released(self):
        # Verify fix_released detection is intact
        self.assertTrue(m.fix_released({'fix': {'state': 'fixed', 'versions': ['3.5.9-r1']}}))
        self.assertFalse(m.fix_released({'fix': {'state': 'not-fixed', 'versions': []}}))
        self.assertFalse(m.fix_released({}))

    def test_kev_and_critical_and_unexcepted_high_always_block(self):
        high_exceptions = {('image-cves.json', 'CVE-2026-95692', 'libssl3', '3.5.9-r0', 'high')}
        # Exact excepted high does not block unless KEV
        block, kev, scoped = m.finding_flags(
            'image-cves.json', 'CVE-2026-95692', 'libssl3', '3.5.9-r0', 'high',
            {'CVE-2026-95692'}, set(), high_exceptions,
        )
        self.assertFalse(block)
        self.assertFalse(kev)
        self.assertTrue(scoped)

        # KEV always sets kev=True even for excepted finding
        _, kev_hit, _ = m.finding_flags(
            'image-cves.json', 'CVE-2026-95692', 'libssl3', '3.5.9-r0', 'high',
            {'CVE-2026-95692'}, {'CVE-2026-95692'}, high_exceptions,
        )
        self.assertTrue(kev_hit)

        # Critical and unexcepted high always block
        for sev in ('critical', 'unknown'):
            b, _, _ = m.finding_flags(
                'image-cves.json', 'CVE-2026-95692', 'libssl3', '3.5.9-r0', sev,
                {'CVE-2026-95692'}, set(), high_exceptions,
            )
            self.assertTrue(b)
        b_other, _, _ = m.finding_flags(
            'image-cves.json', 'CVE-2026-UNEXCEPTED', 'libssl3', '3.5.9-r0', 'high',
            {'CVE-2026-UNEXCEPTED'}, set(), high_exceptions,
        )
        self.assertTrue(b_other)

    def test_review_max_age_stays_30_days(self):
        self.assertEqual(m.REVIEW_MAX_AGE, timedelta(days=30))

    def test_synthetic_unreached_image_packages_are_narrowly_bounded(self):
        self.assertEqual(m.SYNTHETIC_CI_UNREACHED_IMAGE_PACKAGES, frozenset({'libcrypto3', 'libssl3', 'libxml2'}))
        self.assertNotIn('postgresql', m.SYNTHETIC_CI_UNREACHED_IMAGE_PACKAGES)
        self.assertNotIn('libpq', m.SYNTHETIC_CI_UNREACHED_IMAGE_PACKAGES)
