"""Synthetic CI patch authorization tests; never invoke system commands."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location('native_apply', Path(__file__).parents[1] / 'security/apply_ci_native_patch.py')
m = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(m)


class PatchTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        self.approval = {'schema_version': 1, 'status': 'approved_ci_only',
                         'scope': 'ubuntu24.04-amd64-glibc-six-package-patch', 'packages': []}
        self.candidate = {'status': 'candidate_recorded_review_required', 'transaction': []}
        self.downloads = {'status': 'downloaded_not_installed', 'packages': []}
        for name in sorted(m.PACKAGES):
            directory = self.folder / 'candidate-archives' / name
            directory.mkdir(parents=True)
            archive, notice = directory / (name + '.deb'), directory / 'copyright'
            archive.write_bytes(b'synthetic archive ' + name.encode())
            notice.write_text('synthetic rights')
            version = '2.39-0ubuntu8.12'
            self.approval['packages'].append({'name': name, 'version': version, 'archive_sha256': m.sha(archive), 'copyright_sha256': m.sha(notice)})
            self.candidate['transaction'].append({'name': name, 'candidate': version, 'installed': '2.39-0ubuntu8.9', 'metadata': {'sha256': m.sha(archive)}})
            self.downloads['packages'].append({'name': name, 'version': version, 'path': str(archive), 'sha256': m.sha(archive),
                                              'copyright': {'copied_path': str(notice), 'sha256': m.sha(notice)}})
        (self.folder / 'ubuntu-native-candidate.json').write_text(json.dumps(self.candidate))
        self.downloads['candidate_record_sha256'] = m.sha(self.folder / 'ubuntu-native-candidate.json')

    def verify(self):
        return m.verify_transaction(self.approval, self.candidate, self.downloads, self.folder)

    def test_approved_six(self):
        with patch.object(m.subprocess, 'run', side_effect=AssertionError('No command allowed')):
            planned, candidates = self.verify()
        self.assertEqual(len(planned), 6)
        text = '\n'.join('Inst ' + name + ' [2.39-0ubuntu8.9] (2.39-0ubuntu8.12 Ubuntu [amd64])' for name in m.PACKAGES)
        m.verify_simulation(text, planned, candidates)
        with self.assertRaisesRegex(RuntimeError, 'removals'):
            m.verify_simulation(text + '\nRemv bash [1]', planned, candidates)
        with self.assertRaisesRegex(ValueError, 'differs'):
            m.verify_simulation(next(line for line in text.splitlines() if line.startswith('Inst libc6 ')), planned, candidates)

    def test_absent_or_changed_approval(self):
        self.approval['status'] = 'planned'
        with self.assertRaisesRegex(ValueError, 'approval'):
            self.verify()

    def test_version_and_hash_changes(self):
        original = copy.deepcopy(self.approval)
        for field in ['version', 'archive_sha256', 'copyright_sha256']:
            self.approval = copy.deepcopy(original)
            self.approval['packages'][0][field] = 'changed'
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.verify()

    def test_archive_bytes_changed(self):
        Path(self.downloads['packages'][0]['path']).write_bytes(b'tampered')
        with self.assertRaisesRegex(ValueError, 'Archive bytes'):
            self.verify()

    def test_duplicate_or_missing_package(self):
        self.approval['packages'].pop()
        with self.assertRaisesRegex(ValueError, 'six'):
            self.verify()

    def test_runner_scope(self):
        m.require_platform({'GITHUB_ACTIONS': 'true'}, {'ID': 'ubuntu', 'VERSION_ID': '24.04'}, 'x86_64')
        for env, release, arch in [({}, {'ID': 'ubuntu', 'VERSION_ID': '24.04'}, 'x86_64'),
                                   ({'GITHUB_ACTIONS': 'true'}, {'ID': 'debian', 'VERSION_ID': '13'}, 'x86_64'),
                                   ({'GITHUB_ACTIONS': 'true'}, {'ID': 'ubuntu', 'VERSION_ID': '24.04'}, 'arm64')]:
            with self.assertRaisesRegex(ValueError, 'Only'):
                m.require_platform(env, release, arch)

    def test_reinstall_keeps_archive_notice_and_fresh_simulation_checks(self):
        self.candidate['transaction_mode'] = 'reinstall'
        for row in self.candidate['transaction']:
            row['installed'] = row['candidate']
        (self.folder / 'ubuntu-native-candidate.json').write_text(json.dumps(self.candidate))
        self.downloads['candidate_record_sha256'] = m.sha(self.folder / 'ubuntu-native-candidate.json')
        for missing_opt_in in (None, False, 'true'):
            self.approval['allow_same_version_reinstall'] = missing_opt_in
            with self.subTest(opt_in=missing_opt_in), self.assertRaisesRegex(ValueError, 'reinstall approval'):
                self.verify()
        self.approval['allow_same_version_reinstall'] = True
        planned, candidates = self.verify()
        self.assertIn('--reinstall', m.apt_base(self.candidate))
        self.assertNotIn('--reinstall', m.apt_base({}))
        text = '\n'.join('Inst ' + name + ' [2.39-0ubuntu8.12] (2.39-0ubuntu8.12 local-deb [amd64])' for name in m.PACKAGES)
        m.verify_simulation(text, planned, candidates)
        with self.assertRaisesRegex(ValueError, 'Installed baseline changed'):
            m.verify_simulation(text.replace('[2.39-0ubuntu8.12]', '[2.39-0ubuntu8.9]', 1), planned, candidates)
        with self.assertRaisesRegex(RuntimeError, 'complete libc6'):
            m.verify_simulation('0 upgraded, 0 newly installed, 0 to remove', planned, candidates)
        Path(self.downloads['packages'][0]['copyright']['copied_path']).write_text('tampered')
        with self.assertRaisesRegex(ValueError, 'Notice bytes'):
            self.verify()

    def test_reinstall_cannot_upgrade_companions_or_use_unknown_mode(self):
        self.approval['allow_same_version_reinstall'] = True
        for mode, message in [('no-op', 'Unknown native transaction mode'), ('reinstall', 'same-version')]:
            self.candidate['transaction_mode'] = mode
            (self.folder / 'ubuntu-native-candidate.json').write_text(json.dumps(self.candidate))
            self.downloads['candidate_record_sha256'] = m.sha(self.folder / 'ubuntu-native-candidate.json')
            with self.subTest(mode=mode), self.assertRaisesRegex((ValueError, RuntimeError), message):
                self.verify()


if __name__ == '__main__':
    unittest.main()
