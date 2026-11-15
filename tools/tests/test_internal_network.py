"""Pure endpoint-ownership checks; real relay I/O is separately smoke-tested."""
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('internal_network_tests', Path(__file__).parents[1] / 'run_postgres_smoke.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class InternalNetworkTests(unittest.TestCase):
    def test_owned_internal_endpoint(self):
        network = {'Id': 'synthetic-owned', 'Internal': True, 'IPAM': {'Config': [{'Subnet': '172.22.0.0/16'}]}}
        endpoints = {'test-net': {'NetworkID': 'synthetic-owned', 'IPAddress': '172.22.0.2'}}
        self.assertEqual(m.internal_database_address(endpoints, 'test-net', network), '172.22.0.2')
        for field, value in [('NetworkID', 'other'), ('IPAddress', '8.8.8.8'), ('IPAddress', '127.0.0.1'), ('IPAddress', '172.23.0.2')]:
            original = endpoints['test-net'][field]
            endpoints['test-net'][field] = value
            with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                m.internal_database_address(endpoints, 'test-net', network)
            endpoints['test-net'][field] = original
        network['Internal'] = False
        with self.assertRaises(ValueError):
            m.internal_database_address(endpoints, 'test-net', network)
