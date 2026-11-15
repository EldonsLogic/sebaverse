"""Synthetic archive fixtures: no APT, network, extraction or installation."""
import importlib.util
import io
from pathlib import Path
import tarfile
import unittest

SPEC = importlib.util.spec_from_file_location('native_download', Path(__file__).parents[1] / 'security/download_ci_native.py')
m = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(m)


def fixture(entries):
    out = io.BytesIO()
    with tarfile.open(fileobj=out, mode='w') as archive:
        for name, value, kind in entries:
            info = tarfile.TarInfo(name)
            if kind == 'symlink':
                info.type, info.linkname = tarfile.SYMTYPE, value
                archive.addfile(info)
            else:
                data = value.encode()
                info.size = len(data)
                archive.addfile(info, io.BytesIO(data))
    return out.getvalue()


class NoticeTests(unittest.TestCase):
    def test_regular_and_cross_package_symlink(self):
        one = fixture([('./usr/share/doc/libc6/copyright', 'license example', 'file')])
        two = fixture([('usr/share/doc/libc-bin', 'libc6', 'symlink')])
        notices = m.read_notices([one, two], ['libc6', 'libc-bin'])
        self.assertEqual(notices['libc-bin']['data'], b'license example')
        self.assertEqual(notices['libc6']['sha256'], notices['libc-bin']['sha256'])

    def test_file_symlink(self):
        payload = fixture([('usr/share/doc/libc6/copyright', 'rights', 'file'),
                           ('usr/share/doc/libc-bin/copyright', '../libc6/copyright', 'symlink')])
        self.assertEqual(m.read_notices([payload], ['libc-bin'])['libc-bin']['bytes'], 6)

    def test_missing_empty_duplicate_and_escape(self):
        cases = [[], [('usr/share/doc/libc6/copyright', '', 'file')],
                 [('usr/share/doc/libc6/copyright', 'a', 'file')] * 2,
                 [('../etc/evil', 'a', 'file')],
                 [('usr/share/doc/libc6', '/etc', 'symlink')],
                 [('usr/share/doc/libc6', '../../../../etc', 'symlink')],
                 [('usr/share/doc/libc6/copyright', 'copyright', 'symlink')]]
        for entries in cases:
            with self.subTest(entries=entries), self.assertRaises(ValueError):
                m.read_notices([fixture(entries)], ['libc6'])

    def test_notice_size_bound(self):
        from unittest.mock import patch
        with patch.object(m, 'MAX_NOTICE', 2), self.assertRaisesRegex(ValueError, 'Oversized'):
            m.read_notices([fixture([('usr/share/doc/libc6/copyright', 'large', 'file')])], ['libc6'])

    def test_metadata_binding(self):
        row = {'name': 'libc6', 'candidate': '2.39-0ubuntu8.12', 'metadata': {
            'candidate': '2.39-0ubuntu8.12', 'sha256': 'a' * 64,
            'origins': [{'trusted': True, 'origin': 'Ubuntu', 'label': 'Ubuntu', 'archive': 'noble-security', 'component': 'main'}]}}
        self.assertEqual(m.validate_row(row)[0], 'libc6')
        row['metadata']['origins'][0]['trusted'] = False
        with self.assertRaisesRegex(ValueError, 'trusted'):
            m.validate_row(row)
        row['name'] = 'arbitrary'
        with self.assertRaisesRegex(ValueError, 'Unexpected'):
            m.validate_row(row)


if __name__ == '__main__':
    unittest.main()
