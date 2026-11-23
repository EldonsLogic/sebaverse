"""Exercise the internal one-shot cleanup command without connecting to PostgreSQL."""

from io import StringIO
import os
from pathlib import Path
import stat
import traceback
from types import SimpleNamespace
from unittest.mock import Mock
from uuid import uuid4

import pytest
from django.conf import settings
from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import OperationalError
from django.db.backends.base.base import BaseDatabaseWrapper

from modules.ingestion import cleanup
from modules.ingestion.management.commands import run_consent_cleanup
from modules.ingestion.storage import PrivateObjects


COMMAND = 'run_consent_cleanup'
PRIVATE_MARKER = 'authored-private-test-marker'


@pytest.fixture
def configured(tmp_path, monkeypatch):
    objects = PrivateObjects(tmp_path.resolve() / PRIVATE_MARKER)
    db = {'ENGINE': 'django.db.backends.postgresql', 'HOST': '127.0.0.1'}
    monkeypatch.setattr(settings, 'LOCAL_MODE', True)
    monkeypatch.setattr(settings, 'CONSENT_CLEANUP_ENABLED', True, raising=False)
    monkeypatch.setattr(settings, 'CONSENT_CLEANUP_STORE', objects, raising=False)
    monkeypatch.setattr(settings, 'DATABASES', {'default': db})
    batch = Mock(return_value=None)
    monkeypatch.setattr(run_consent_cleanup, 'run_batch', batch)
    connect = Mock(side_effect=AssertionError('The authored test must not open a database'))
    monkeypatch.setattr(BaseDatabaseWrapper, 'ensure_connection', connect)
    replay = Mock(side_effect=AssertionError('The runner must not reopen a blocked intent'))
    monkeypatch.setattr(cleanup, 'retry_blocked_intent', replay)
    yield objects, db, batch
    connect.assert_not_called()
    replay.assert_not_called()


@pytest.mark.parametrize(('name', 'value'), [
    ('LOCAL_MODE', False),
    ('LOCAL_MODE', 1),
    ('CONSENT_CLEANUP_ENABLED', False),
    ('CONSENT_CLEANUP_ENABLED', 'yes'),
    ('CONSENT_CLEANUP_STORE', None),
    ('CONSENT_CLEANUP_STORE', PRIVATE_MARKER),
])
def test_cleanup_rejects_ineligible_settings_before_work(configured, monkeypatch, name, value):
    root, _, batch = configured
    monkeypatch.setattr(settings, name, value)
    with pytest.raises(CommandError) as rejected:
        call_command(COMMAND)
    assert PRIVATE_MARKER not in str(rejected.value)
    assert list(root.root.iterdir()) == []
    batch.assert_not_called()


@pytest.mark.parametrize(('field', 'value'), [
    ('ENGINE', 'django.db.backends.dummy'),
    ('HOST', ''),
    ('HOST', '/var/run/postgresql'),
    ('HOST', 'nonlocal-fixture.invalid'),
])
def test_cleanup_requires_explicit_local_postgresql_settings(configured, field, value):
    _, db, batch = configured
    db[field] = value
    with pytest.raises(CommandError):
        call_command(COMMAND)
    batch.assert_not_called()


@pytest.mark.parametrize('ambiguous', ['alias', 'router'])
def test_cleanup_rejects_ambiguous_database_routing(configured, monkeypatch, ambiguous):
    _, db, batch = configured
    if ambiguous == 'alias':
        monkeypatch.setattr(settings, 'DATABASES', {'default': db, 'second': db})
    else:
        monkeypatch.setattr(settings, 'DATABASE_ROUTERS', ['authored-router-fixture'])
    with pytest.raises(CommandError):
        call_command(COMMAND)
    batch.assert_not_called()


@pytest.mark.parametrize('fault', ['missing', 'relative', 'file', 'leaf-link', 'parent-link', 'open-mode'])
def test_unsafe_root_is_neither_created_nor_fixed(configured, monkeypatch, fault):
    objects, _, batch = configured
    original = objects.root
    if fault == 'missing':
        original.rmdir()
    elif fault == 'relative':
        monkeypatch.chdir(original.parent)
        objects.root = Path(original.name)
    elif fault == 'file':
        original.rmdir()
        original.write_text('authored fixture')
    elif fault in ('leaf-link', 'parent-link'):
        alias = original.parent / 'alias'
        if fault == 'leaf-link':
            alias.symlink_to(original, target_is_directory=True)
            objects.root = alias
        else:
            alias.symlink_to(original.parent, target_is_directory=True)
            objects.root = alias / original.name
    else:
        original.chmod(0o755)

    observed = original.stat() if original.exists() else None
    with pytest.raises(CommandError) as rejected:
        call_command(COMMAND)
    assert PRIVATE_MARKER not in str(rejected.value)
    if observed is None:
        assert not os.path.lexists(original)
    else:
        assert original.stat().st_mode == observed.st_mode
        assert original.stat().st_ino == observed.st_ino
    batch.assert_not_called()


def test_cleanup_refuses_opted_in_writer_recovery(configured, monkeypatch):
    objects, _, batch = configured
    protected = PrivateObjects(objects.root, writer_recovery=True)
    monkeypatch.setattr(settings, 'CONSENT_CLEANUP_STORE', protected)
    lock_entries = {entry.name: entry.stat().st_ino for entry in objects.root.iterdir()}

    with pytest.raises(CommandError):
        call_command(COMMAND)

    assert {entry.name: entry.stat().st_ino for entry in objects.root.iterdir()} == lock_entries
    batch.assert_not_called()


def test_unprotected_store_view_cannot_run_over_protected_namespace(configured):
    objects, _, batch = configured
    marker = objects.root / '.source-writer-v1'
    marker.write_text('authored marker')
    marker.chmod(0o600)

    with pytest.raises(CommandError):
        call_command(COMMAND)

    assert marker.read_text() == 'authored marker'
    batch.assert_not_called()


@pytest.mark.parametrize(('option', 'value'), [
    ('limit', 101),
    ('limit', True),
    ('max_batches', 'many'),
    ('root', PRIVATE_MARKER),
    ('intent_id', PRIVATE_MARKER),
    ('learner_id', PRIVATE_MARKER),
    ('uploader_id', PRIVATE_MARKER),
    ('retry_blocked', True),
    ('writer_recovery', True),
])
def test_command_has_no_scope_or_control_overrides(configured, option, value):
    _, _, batch = configured
    with pytest.raises(TypeError, match='Unknown option'):
        call_command(COMMAND, **{option: value})
    batch.assert_not_called()


def test_command_rejects_cli_batch_limit_override(configured):
    _, _, batch = configured
    with pytest.raises(CommandError, match=r'^Error: Invalid consent cleanup arguments\.$'):
        call_command(COMMAND, '--limit', '101')
    batch.assert_not_called()


@pytest.mark.parametrize('command_line', [True, False])
def test_unsupported_arguments_redact_identifiers_and_paths(configured, capsys, command_line):
    objects, _, batch = configured
    object_id = str(uuid4())
    source = objects.path(object_id)
    source.write_bytes(b'authored source')
    arguments = ['--intent-id', object_id, '--root', str(objects.root)]

    if command_line:
        with pytest.raises(SystemExit) as rejected:
            run_consent_cleanup.Command().run_from_argv(['manage.py', COMMAND, *arguments])
        assert rejected.value.code == 2
        error = capsys.readouterr()
        assert error.out == ''
        message = error.err
    else:
        with pytest.raises(CommandError) as rejected:
            call_command(COMMAND, *arguments)
        message = str(rejected.value)

    assert 'Invalid consent cleanup arguments.' in message
    assert object_id not in message and PRIVATE_MARKER not in message
    assert source.read_bytes() == b'authored source'
    assert list(objects.root.iterdir()) == [source]
    batch.assert_not_called()


def receipt(status):
    return SimpleNamespace(
        status=status, pk=PRIVATE_MARKER, cursor=PRIVATE_MARKER, failure_code=PRIVATE_MARKER,
    )


@pytest.mark.parametrize(('results', 'expected'), [
    ([None], 'Cleanup batches=0 complete=0 pending=0 blocked=0 stop=no_result'),
    ([receipt('pending'), receipt('complete'), None],
     'Cleanup batches=2 complete=1 pending=1 blocked=0 stop=no_result'),
    ([receipt('pending'), receipt('blocked'), receipt('complete'), receipt('pending')],
     'Cleanup batches=4 complete=1 pending=2 blocked=1 stop=limit'),
])
def test_cleanup_uses_fixed_limits_and_reports_only_aggregate_status(configured, results, expected):
    _, _, batch = configured
    batch.side_effect = results
    stdout, stderr = StringIO(), StringIO()

    call_command(COMMAND, stdout=stdout, stderr=stderr)

    assert stdout.getvalue().strip() == expected
    assert stderr.getvalue() == ''
    assert batch.call_count == len(results)
    stores = [called.args[0] for called in batch.call_args_list]
    assert all(store is stores[0] for store in stores)
    assert getattr(stores[0], 'writer_recovery', False) is False
    assert all(len(called.args) == 1 and called.kwargs == {'limit': 25} for called in batch.call_args_list)


def test_command_passes_a_pinned_purge_only_store(configured):
    objects, _, batch = configured
    object_id = str(uuid4())
    source, manifest = objects.path(object_id), objects.path(object_id, 'manifest')
    source.write_bytes(b'authored source')
    manifest.write_bytes(b'authored manifest')
    captured = objects.root.with_name('captured-fixture-root')
    unrelated = objects.root / 'unrelated'
    unrelated.write_text('keep this fixture')

    def run(store, *, limit):
        assert not hasattr(store, 'read')
        assert not hasattr(store, 'put')
        assert not hasattr(store, 'closed_writer')
        objects.root.rename(captured)
        objects.root.mkdir(mode=0o700)
        source.write_bytes(b'replacement source')
        manifest.write_bytes(b'replacement manifest')
        assert store.purge_confirmed(object_id) is True
        return None

    batch.side_effect = run
    stdout = StringIO()
    call_command(COMMAND, stdout=stdout)
    assert not os.path.lexists(captured / source.name) and not os.path.lexists(captured / manifest.name)
    assert source.read_bytes() == b'replacement source' and manifest.read_bytes() == b'replacement manifest'
    assert (captured / unrelated.name).read_text() == 'keep this fixture'
    assert stat.S_IMODE(captured.stat().st_mode) == 0o700
    assert object_id not in stdout.getvalue()


@pytest.mark.parametrize('failure', [OSError, OperationalError])
def test_command_failure_is_bounded_content_free_and_not_retried(configured, caplog, failure):
    _, _, batch = configured
    batch.side_effect = [receipt('complete'), failure(PRIVATE_MARKER)]
    stdout, stderr = StringIO(), StringIO()

    with pytest.raises(CommandError) as rejected:
        call_command(COMMAND, stdout=stdout, stderr=stderr)

    error_text = ''.join(traceback.format_exception(rejected.value))
    assert PRIVATE_MARKER not in error_text + stdout.getvalue() + stderr.getvalue() + caplog.text
    assert stdout.getvalue() == ''
    assert batch.call_count == 2
