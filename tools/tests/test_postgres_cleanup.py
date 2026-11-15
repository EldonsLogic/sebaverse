"""Failure-injected task-owned cleanup; no Docker or network use."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('cleanup_tests', Path(__file__).parents[1] / 'run_postgres_smoke.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class CleanupTests(unittest.TestCase):
    def test_relay_failure_does_not_skip_container_network_or_credentials(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            credential = root / 'synthetic.env'
            credential.write_text('synthetic-only')
            home = root / 'owned-home'
            home.mkdir()
            class Relay:
                def close(self):raise RuntimeError('synthetic relay close failure')
            commands = []
            errors = m.cleanup_owned_resources(Relay(), 'owned-container', 'owned-network', credential, home,
                                               lambda command, **kwargs: commands.append(command))
            self.assertEqual([e['step'] for e in errors], ['relay'])
            self.assertEqual(commands, [['docker', 'rm', '-f', '-v', 'owned-container'],
                                        ['docker', 'network', 'rm', 'owned-network']])
            self.assertFalse(credential.exists())
            self.assertFalse(home.exists())

    def test_container_failure_still_attempts_network_and_private_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            credential = root / 'synthetic.env'
            credential.write_text('synthetic-only')
            calls = []
            def execute(command, **kwargs):
                calls.append(command)
                if command[1] == 'rm':raise RuntimeError('synthetic container cleanup failure')
            errors = m.cleanup_owned_resources(None, 'owned-container', 'owned-network', credential, root / 'absent', execute)
            self.assertEqual([e['step'] for e in errors], ['container'])
            self.assertEqual(len(calls), 2)
            self.assertFalse(credential.exists())
