"""Complete synthetic OCI authority/replay/import fixtures; never execute an image."""
import base64
import copy
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import sys
import tarfile
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


contract = load('derived_contract_tests', ROOT / 'tools/security/derived_image_contract.py')
builder = load('derived_fixture_builder', ROOT / 'tools/security/build_postgres_candidate.py')
runner = load('derived_fixture_runner', ROOT / 'tools/run_postgres_smoke.py')


def encoded(value):
    return json.dumps(value, sort_keys=True).encode()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def desc(data):
    return {'digest': 'sha256:' + sha(data), 'size': len(data)}


def layer(name, data, mode=0o755):
    result = io.BytesIO()
    with tarfile.open(fileobj=result, mode='w') as archive:
        info = tarfile.TarInfo(name)
        info.size, info.mode = len(data), mode
        archive.addfile(info, io.BytesIO(data))
    return result.getvalue()


class DerivedContractTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.directory = self.root / 'work/f2-security'
        self.directory.mkdir(parents=True)
        context = self.root / 'infra/local/postgres'
        context.mkdir(parents=True)
        tools = self.root / 'tools/security'
        tools.mkdir(parents=True)
        for name in ['derived_image_contract.py', 'build_postgres_candidate.py', 'inspect_postgres_files.py']:
            shutil.copyfile(ROOT / 'tools/security' / name, tools / name)
        parent_layer = layer('usr/local/bin/docker-entrypoint.sh', b'synthetic source, never executed')
        parent_config = {'architecture': 'amd64', 'os': 'linux', 'config': {
            'Entrypoint': ['docker-entrypoint.sh'], 'Cmd': ['postgres']},
            'rootfs': {'type': 'layers', 'diff_ids': ['sha256:' + sha(parent_layer)]}}
        parent_config_bytes = encoded(parent_config)
        parent = {'schemaVersion': 2, 'config': desc(parent_config_bytes), 'layers': [desc(parent_layer)]}
        parent_bytes = encoded(parent)
        parent_id = desc(parent_bytes)['digest']
        stub = b'authored synthetic replacement, never executed'
        dockerfile = ('FROM docker.io/library/postgres@' + parent_id + '\n'
                      'COPY --chmod=0755 gosu-disabled.sh /usr/local/bin/gosu\nUSER postgres\n').encode()
        (context / 'Dockerfile').write_bytes(dockerfile)
        (context / 'gosu-disabled.sh').write_bytes(stub)
        proposal = {'platform': 'linux/amd64', 'parent_platform_manifest': parent_id,
                    'recipe_sha256': sha(dockerfile), 'authored_replacement_sha256': sha(stub)}
        self.write(context / 'proposal.json', proposal)
        pin = {'index_digest': 'sha256:' + '1' * 64, 'platforms': [
            {'platform': {'os': 'linux', 'architecture': 'amd64'}, 'digest': parent_id}]}
        self.write(self.root / 'infra/images.lock.json', {'postgres': pin})
        policy = {'schema_version': 1, 'type': 'derived-oci', 'platform': {'os': 'linux', 'architecture': 'amd64'},
                  'user': 'postgres', **{k: proposal[k] for k in ['parent_platform_manifest', 'recipe_sha256', 'authored_replacement_sha256']}, **contract.PATHS}
        self.write(context / 'runtime-source.json', policy)
        replacement = layer('usr/local/bin/gosu', stub)
        config = copy.deepcopy(parent_config)
        config['config']['User'] = 'postgres'
        config['rootfs']['diff_ids'].append('sha256:' + sha(replacement))
        self.config_bytes = encoded(config)
        manifest = {'schemaVersion': 2, 'config': desc(self.config_bytes), 'layers': [*parent['layers'], desc(replacement)]}
        self.manifest_bytes = encoded(manifest)
        descriptor = {**desc(self.manifest_bytes), 'platform': {'os': 'linux', 'architecture': 'amd64'}}
        members = {'oci-layout': encoded({'imageLayoutVersion': '1.0.0'}),
                   'index.json': encoded({'schemaVersion': 2, 'manifests': [descriptor]})}
        for blob in [parent_layer, replacement, self.config_bytes, self.manifest_bytes]:
            members['blobs/sha256/' + sha(blob)] = blob
        self.archive = self.directory / 'postgres-derived.oci.tar'
        with tarfile.open(self.archive, 'w') as archive:
            for name, data in members.items():
                info = tarfile.TarInfo(name)
                info.size = len(data)
                archive.addfile(info, io.BytesIO(data))
        (self.directory / 'postgres-parent-manifest.json').write_bytes(parent_bytes)
        (self.directory / 'postgres-parent-config.json').write_bytes(parent_config_bytes)
        receipt = builder.inspect_archive(self.archive, parent, parent_config)
        inputs = ['infra/local/postgres/Dockerfile', 'infra/local/postgres/gosu-disabled.sh',
                  'infra/local/postgres/proposal.json', 'infra/images.lock.json']
        receipt.update(schema_version=1, status='built_static_not_cleared', archive_path=contract.PATHS['archive'],
                       archive_sha256=builder.digest(self.archive), input_hashes={n: builder.digest(self.root / n) for n in inputs},
                       **{k: proposal[k] for k in ['parent_platform_manifest', 'recipe_sha256', 'authored_replacement_sha256']},
                       parent_index_digest=pin['index_digest'], parent_config_digest=parent['config']['digest'],
                       parent_manifest_path=contract.PATHS['parent_manifest'], parent_config_path=contract.PATHS['parent_config'])
        self.write(self.directory / 'postgres-derived-build.json', receipt)
        with patch.object(sys, 'path', [str(tools), *sys.path]):
            inspector = load('fixture_inspector', tools / 'inspect_postgres_files.py')
            inspector.inspect_artifact(self.directory)

    def write(self, path, value):
        path.write_text(json.dumps(value))

    def bind(self, path, expected=None):
        actual = builder.digest(path)
        if expected is not None and actual != expected:
            raise ValueError('Bound byte hash differs')
        return actual

    def validate(self):
        return contract.validate(self.root, self.directory, self.bind)

    def metadata(self, runtime):
        return {'manifestDigest': runtime['platform_manifest_digest'], 'imageID': runtime['config_digest'],
                'os': 'linux', 'architecture': 'amd64', 'userInput': runtime['reference'],
                'manifest': base64.b64encode(self.manifest_bytes).decode(),
                'config': base64.b64encode(self.config_bytes).decode()}

    def test_complete_offline_authority_replay_and_scanner_identity(self):
        before = (self.directory / 'postgres-derived-files.json').read_bytes()
        runtime = self.validate()
        contract.validate_source(self.metadata(runtime), runtime, self.root)
        self.assertEqual((self.directory / 'postgres-derived-files.json').read_bytes(), before)
        self.assertTrue(runtime['reference'].startswith('oci-archive:'))

    def test_archive_or_parent_bytes_changed(self):
        for path in [self.archive, self.directory / 'postgres-parent-manifest.json']:
            data = path.read_bytes()
            path.write_bytes(data + b'x')
            with self.subTest(path=path), self.assertRaises(ValueError):
                self.validate()
            path.write_bytes(data)

    def test_forged_files_receipt_or_entrypoint_rejected(self):
        for name in ['postgres-derived-files.json', 'postgres-entrypoint-source.txt']:
            path = self.directory / name
            original = path.read_bytes()
            if name.endswith('.json'):
                value = json.loads(original)
                value['initdb_inputs'] = ['unreviewed.sql']
                self.write(path, value)
            else:
                path.write_bytes(b'changed source')
            with self.subTest(name=name), self.assertRaises(ValueError):
                self.validate()
            path.write_bytes(original)

    def test_runtime_user_or_recipe_changes_fail(self):
        path = self.root / contract.POLICY_PATH
        data = path.read_bytes()
        value = json.loads(data)
        value['user'] = 'root'
        self.write(path, value)
        with self.assertRaisesRegex(ValueError, 'User'):
            self.validate()
        path.write_bytes(data)
        (self.root / 'infra/local/postgres/gosu-disabled.sh').write_bytes(b'changed stub')
        with self.assertRaisesRegex(ValueError, 'hashes'):
            self.validate()

    def test_scanner_source_or_raw_config_substitution(self):
        runtime = self.validate()
        for field, value in [('userInput', 'docker.io/library/postgres:17'), ('imageID', 'sha256:' + 'f' * 64),
                             ('config', base64.b64encode(b'changed').decode()), ('architecture', 'arm64')]:
            metadata = self.metadata(runtime)
            metadata[field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                contract.validate_source(metadata, runtime, self.root)

    def test_client_environment_drops_ambient_services_and_plugins(self):
        ambient = {'PGSERVICE': 'untrusted', 'PGOPTIONS': 'untrusted', 'KRB5_CONFIG': 'untrusted',
                   'LDAPURI': 'untrusted', 'PYTHONPATH': 'untrusted', 'OPENSSL_CONF': 'untrusted'}
        with patch.dict(os.environ, ambient):
            env = runner.client_environment(self.root, 'abc1234567', 'synthetic-only', 5432)
        self.assertNotIn('PGSERVICE', env)
        self.assertNotIn('PGOPTIONS', env)
        self.assertNotIn('LDAPURI', env)
        self.assertNotIn('PYTHONPATH', env)
        self.assertEqual(env['OPENSSL_CONF'], '/dev/null')
        self.assertEqual(env['KRB5_CONFIG'], '/dev/null')
        self.assertEqual(env['LDAPNOINIT'], '1')
        self.assertEqual(env['POSTGRES_HOST'], '127.0.0.1')
        self.assertTrue(Path(env['HOME']).is_relative_to(self.root))
        with self.assertRaises(ValueError):
            runner.client_environment(self.root, '../escape', 'synthetic-only', 5432)

    def test_static_docker_import_verifies_exact_config_and_rootfs(self):
        runtime = self.validate()
        commands = []
        class Result:
            stdout = ''
        def execute(command, **kwargs):
            commands.append(command)
            result = Result()
            if command[2] == 'inspect':
                result.stdout = json.dumps({'Id': runtime['config_digest'], 'Os': 'linux', 'Architecture': 'amd64',
                    'Config': {'User': 'postgres'}, 'RootFS': {'Layers': runtime['rootfs_diff_ids']}})
            return result
        self.assertEqual(runner.load_derived_image(runtime, self.root, execute), runtime['config_digest'])
        self.assertEqual(len(commands), 2)
        self.assertTrue(all('run' not in command for command in commands))
        def wrong(command, **kwargs):
            result = Result()
            result.stdout = '{}'
            return result
        with self.assertRaisesRegex(ValueError, 'imported'):
            runner.load_derived_image(runtime, self.root, wrong)
