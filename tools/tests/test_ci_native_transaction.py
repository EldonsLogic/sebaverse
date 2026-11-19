"""Synthetic signed-index metadata/parser tests; no package/network operations."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

SPEC = importlib.util.spec_from_file_location('prepare_native', Path(__file__).parents[1] / 'security/prepare_ci_native.py')
m = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(m)


class TransactionTests(unittest.TestCase):
    def setUp(self):
        self.line = 'Inst libc6 [2.39-0ubuntu8.9] (2.39-0ubuntu8.12 Ubuntu:24.04/noble-updates [amd64])'
        self.row = m.parse_transaction(self.line)[0]
        self.metadata = {'installed': '2.39-0ubuntu8.9', 'candidate': m.MINIMUM, 'architecture': 'amd64',
                         'sha256': 'a' * 64, 'filename': 'pool/main/g/glibc/libc6.deb',
                         'origins': [{'trusted': True, 'origin': 'Ubuntu', 'label': 'Ubuntu', 'archive': 'noble-updates', 'component': 'main'}]}

    def test_positive_transaction(self):
        rows = m.parse_transaction(self.line + '\n' + self.line.replace('libc6 ', 'libc-bin '))
        self.assertEqual([r['name'] for r in rows], ['libc6', 'libc-bin'])
        m.validate_metadata(self.row, self.metadata, lambda a, b: True)

    def test_observed_apt_companion_status_suffix(self):
        # Actual apt simulation in CI43690540793 has optional empty breakage lists.
        plan = self.line + '\n' + self.line.replace('libc6 ', 'libc6-i386 ') + ' []'
        rows = m.parse_transaction(plan)
        self.assertEqual([r['name'] for r in rows], ['libc6', 'libc6-i386'])
        with self.assertRaises(RuntimeError):
            m.parse_transaction(self.line + ' [unrecognized status]')

    def test_reject_transactions(self):
        for text in ['', self.line + '\nRemv bash [1]', self.line + '\nPurg bash [1]',
                     self.line.replace('libc6 ', 'bash '), self.line.replace(' [2.39-0ubuntu8.9]', ''),
                     self.line + '\n' + self.line, 'Inst libc6 malformed']:
            with self.subTest(text=text), self.assertRaises(RuntimeError):
                m.parse_transaction(text)

    def test_metadata_fail_closed(self):
        changes = [('candidate', '2.39-0ubuntu8.11'), ('installed', 'unexpected'), ('sha256', ''),
                   ('filename', 'pool/main/g/glibc/../evil.deb'), ('origins', [])]
        for key, value in changes:
            metadata = copy.deepcopy(self.metadata)
            metadata[key] = value
            with self.subTest(key=key), self.assertRaises(RuntimeError):
                m.validate_metadata(self.row, metadata, lambda a, b: True)

    def test_downgrade_rejected(self):
        with self.assertRaisesRegex(RuntimeError, 'downgrade'):
            m.validate_metadata(self.row, self.metadata, lambda a, b: False)

    def test_architecture_mismatch(self):
        row = dict(self.row, architecture='arm64')
        with self.assertRaisesRegex(RuntimeError, 'architecture'):
            m.validate_metadata(row, self.metadata, lambda a, b: True)

    def test_untrusted_origin_rejected(self):
        self.metadata['origins'][0]['trusted'] = False
        with self.assertRaisesRegex(RuntimeError, 'trusted'):
            m.validate_metadata(self.row, self.metadata, lambda a, b: True)

    def test_observed_already_fixed_runner_gets_exact_reinstall_simulation(self):
        receipt = json.loads((Path(__file__).with_name('fixtures') / 'native-already-fixed-44510517163.json').read_text())
        approval = json.loads((Path(__file__).parents[2] / 'infra/local/native-patch-approval.json').read_text())
        libc6 = next(item for item in approval['packages'] if item['name'] == 'libc6')
        self.assertEqual(receipt['candidate_metadata']['sha256'], libc6['archive_sha256'])
        self.assertEqual(receipt['simulation_command'], m.simulation_command({'installed': self.row['installed'], 'candidate': m.MINIMUM})[1])
        with self.assertRaisesRegex(RuntimeError, 'complete libc6'):
            m.parse_transaction(receipt['simulation'])
        mode, retry = m.simulation_command(receipt['candidate_metadata'])
        self.assertEqual(mode, 'reinstall')
        self.assertIn('--reinstall', retry)
        self.assertIn('--simulate', retry)
        self.assertIn('--only-upgrade', retry)
        self.assertEqual(set(retry[retry.index('install') + 1:]), {p['name'] + '=' + p['version'] for p in approval['packages']})

    def test_reinstall_requires_exact_reviewed_package_versions(self):
        rows = [dict(self.row, name=name, installed=m.MINIMUM) for name in m.REVIEWED_PACKAGES]
        m.validate_reinstall_rows(rows)
        for invalid in [rows[:-1], rows + [rows[0]], rows + [dict(rows[0], name='libc-devtools')],
                        [*rows[:-1], dict(rows[-1], installed='2.39-0ubuntu8.9')],
                        [*rows[:-1], dict(rows[-1], candidate='2.39-0ubuntu8.13')]]:
            with self.subTest(invalid=invalid), self.assertRaises(RuntimeError):
                m.validate_reinstall_rows(invalid)
        with self.assertRaisesRegex(RuntimeError, 'reviewed'):
            m.simulation_command({'installed': '2.39-0ubuntu8.13', 'candidate': '2.39-0ubuntu8.13'})


if __name__ == '__main__':
    unittest.main()
