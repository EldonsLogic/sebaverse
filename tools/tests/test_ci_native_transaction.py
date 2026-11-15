"""Synthetic signed-index metadata/parser tests; no package/network operations."""
import copy
import importlib.util
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


if __name__ == '__main__':
    unittest.main()
