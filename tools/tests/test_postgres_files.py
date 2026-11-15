"""Synthetic static-layer boundary checks; no Docker or shell execution."""
import hashlib
import io
from pathlib import Path
import sys
import tarfile
import unittest
from unittest.mock import patch

with patch.object(sys, 'path', [str(Path(__file__).parents[1] / 'security'), *sys.path]):
    from inspect_postgres_files import inspect_layer


def layer(entries):
    data = io.BytesIO()
    with tarfile.open(fileobj=data, mode='w:gz') as archive:
        for name, content, mode in entries:
            item = tarfile.TarInfo(name)
            item.mode = mode
            item.size = len(content)
            archive.addfile(item, io.BytesIO(content))
    data.seek(0)
    return data


class FilesystemProofTests(unittest.TestCase):
    def test_exact_authored_delta_is_accepted_without_execution(self):
        stub = b'authored fixture, never executed'
        self.assertIsNone(inspect_layer(layer([('usr/local/bin/gosu', stub, 0o755)]), True,
                                        hashlib.sha256(stub).hexdigest()))

    def test_different_content_mode_or_extra_payload_rejected(self):
        expected = hashlib.sha256(b'expected').hexdigest()
        for entries in [[('usr/local/bin/gosu', b'wrong', 0o755)],
                        [('usr/local/bin/gosu', b'expected', 0o777)],
                        [('usr/local/bin/gosu', b'expected', 0o755), ('extra', b'payload', 0o644)],
                        [('usr/local/bin/gosu', b'expected', 0o755)] * 2, []]:
            with self.subTest(entries=entries), self.assertRaises(ValueError):
                inspect_layer(layer(entries), True, expected)

    def test_entrypoint_is_retained_as_data(self):
        source = b'foreign source, never executed'
        result = inspect_layer(layer([('usr/local/bin/docker-entrypoint.sh', source, 0o755)]), False, '')
        self.assertEqual(result, source)

    def test_unreviewed_initdb_inputs_and_debian_wrappers_are_recorded(self):
        observed = {}
        payload = layer([('docker-entrypoint-initdb.d/injected.sql', b'not executed', 0o644),
                         ('usr/bin/pg_ctlcluster', b'not executed', 0o755)])
        inspect_layer(payload, False, '', observed)
        self.assertEqual(observed['initdb_inputs'], {'docker-entrypoint-initdb.d/injected.sql'})
        self.assertEqual(observed['debian_wrappers'], {'usr/bin/pg_ctlcluster'})

    def test_initdb_directory_link_or_file_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'directory'):
            inspect_layer(layer([('docker-entrypoint-initdb.d', b'x', 0o755)]), False, '', {})

    def test_path_escape_and_entrypoint_whiteout(self):
        with self.assertRaises(ValueError):
            inspect_layer(layer([('../escape', b'x', 0o644)]), False, '')
        self.assertEqual(inspect_layer(layer([('usr/local/bin/.wh.docker-entrypoint.sh', b'', 0o644)]), False, ''), b'')
