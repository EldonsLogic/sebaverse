"""Regression coverage for the local receiver/cleanup guard and proof."""

from contextlib import contextmanager
import errno
import json
import os
from pathlib import Path
import select
import subprocess
import sys
from types import SimpleNamespace
from unittest.mock import Mock
from uuid import UUID, uuid4

import pytest

from modules.ingestion import cleanup, service, storage
from modules.ingestion.storage import PrivateObjects

from .fixtures.writer_recovery_child import SOURCE as PARTIAL_SOURCE
from .test_cleanup_consumer import MANIFEST, SOURCE, assert_files, scenario


CHILD = Path(__file__).parent / 'fixtures' / 'writer_recovery_child.py'
CHILD_TIMEOUT = 10


def await_child_output(child):
    assert select.select([child.stdout], [], [], CHILD_TIMEOUT)[0], 'Writer fixture did not respond'
    return child.stdout.readline()


@contextmanager
def authored_writer(store, key, stage):
    child = subprocess.Popen(
        [sys.executable, str(CHILD), str(store.root), str(key), stage],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE,
    )
    try:
        binding = json.loads(await_child_output(child))
        yield child, binding
    finally:
        child.stdin.close()
        try:
            if child.poll() is None:
                child.kill()
            child.wait(timeout=CHILD_TIMEOUT)
        finally:
            child.stdout.close()


@pytest.fixture
def recovery(scenario):
    scenario.store = PrivateObjects(scenario.store.root, writer_recovery=True)
    scenario.run = lambda limit=25: cleanup.run_batch(scenario.store, limit=limit)
    return scenario


def active_row(scenario, *, key=None, charge=len(SOURCE)):
    row = scenario.add_upload(key=key, writer_active=True)
    scenario.quota.reserved_bytes += charge - row.held_bytes
    row.declared_bytes = row.held_bytes = charge
    row.writer_binding = None
    return row


def new_binding(store, row):
    with store.source_writer(str(row.pk)) as guard:
        return guard.binding(row.generation, uuid4())


def assert_recovery_blocked(scenario, row):
    assert row.status == 'withdrawn' and row.writer_active and not row.purge_confirmed
    assert scenario.quota.reserved_bytes == row.held_bytes > 0
    scenario.quota.save.assert_not_called()


def assert_recovered(scenario, row):
    assert row.status == 'deleted' and row.purge_confirmed and not row.writer_active
    assert row.writer_binding is None
    assert row.stored_bytes == row.manifest_bytes == row.held_bytes == 0
    assert scenario.quota.used_bytes == scenario.quota.reserved_bytes == 0
    scenario.quota.save.assert_called_once()
    assert_files(scenario, row, present=False)


@pytest.mark.parametrize('stage', ['before-open', 'partial', 'after-close'])
def test_abrupt_child_exit_releases_writer_guard_for_restart_and_purge(recovery, stage):
    row = active_row(recovery, charge=len(PARTIAL_SOURCE) + (stage == 'partial'))
    source = recovery.store.path(str(row.pk))
    source.unlink()
    if stage != 'before-open':
        # A synthetic orphaned derived file must also be removed on recovery.
        recovery.store.path(str(row.pk), 'manifest').write_bytes(MANIFEST)

    with authored_writer(recovery.store, row.pk, stage) as (child, binding):
        row.writer_binding = binding
        assert os.path.lexists(source) == (stage != 'before-open')
        if stage != 'before-open':
            assert source.read_bytes() == PARTIAL_SOURCE
        assert recovery.run().status == 'pending'
        assert_recovery_blocked(recovery, row)
        assert row.writer_binding == binding
        child.kill()
        assert child.wait(timeout=CHILD_TIMEOUT) < 0
        assert os.path.lexists(source) == (stage != 'before-open')

    # Reopen the adapter as a fresh consumer on the same storage root.
    recovery.store = PrivateObjects(recovery.store.root, writer_recovery=True)
    recovery.clock.now = recovery.intent.due_at
    assert recovery.run().status == 'complete'
    assert recovery.run() is None
    assert_recovered(recovery, row)


@pytest.mark.skipif(not hasattr(os, 'fork'), reason='Requires POSIX descriptor inheritance')
def test_inherited_open_file_description_still_blocks_after_receiver_exits(recovery):
    row = active_row(recovery)
    with authored_writer(recovery.store, row.pk, 'inherited') as (child, binding):
        row.writer_binding = binding
        assert child.wait(timeout=CHILD_TIMEOUT) == 0
        assert recovery.run().status == 'pending'
        assert_recovery_blocked(recovery, row)
        child.stdin.close()
        assert await_child_output(child) == b''

    recovery.clock.now = recovery.intent.due_at
    assert recovery.run().status == 'complete'
    assert_recovered(recovery, row)


def test_legacy_writer_remains_blocked_even_without_a_file(recovery):
    row = active_row(recovery)
    recovery.store.path(str(row.pk)).unlink()
    assert recovery.run().status == 'pending'
    assert_recovery_blocked(recovery, row)
    assert row.writer_binding is None


@pytest.mark.parametrize('fault', [
    'disabled', 'unsupported', 'wrong-root', 'wrong-uuid', 'wrong-generation', 'wrong-protocol',
])
def test_invalid_or_unsupported_writer_proof_retains_source_and_charge(recovery, tmp_path, monkeypatch, fault):
    row = active_row(recovery)
    store = recovery.store
    row.writer_binding = new_binding(store, row)
    if fault == 'disabled':
        recovery.store = PrivateObjects(store.root)
    elif fault == 'unsupported':
        monkeypatch.setattr(storage.fcntl, 'flock', Mock(side_effect=OSError('Unsupported test lock')))
    elif fault == 'wrong-root':
        recovery.store = PrivateObjects(tmp_path / 'another-private-root', writer_recovery=True)
    elif fault == 'wrong-uuid':
        # Use a distinct UUID on the same lock stripe to isolate identity validation.
        row.writer_binding = new_binding(store, SimpleNamespace(pk=UUID(int=row.pk.int ^ 64), generation=1))
    elif fault == 'wrong-generation':
        row.generation += 1
    else:
        row.writer_binding['protocol'] = 'another-protocol'
    assert recovery.run().status == 'pending'
    assert_recovery_blocked(recovery, row)
    assert store.path(str(row.pk)).read_bytes() == SOURCE[:8]


@pytest.mark.parametrize('fault', ['missing-stripe', 'replaced-stripe', 'symlink-stripe', 'changed-namespace'])
def test_changed_lock_namespace_leaves_writer_blocked(recovery, tmp_path, fault):
    row = active_row(recovery)
    store = recovery.store
    row.writer_binding = new_binding(store, row)
    stripe = store.root / store._stripe(row.pk.int % storage._STRIPES)
    if fault == 'changed-namespace':
        (store.root / storage._NAMESPACE).write_text(str(uuid4()))
    else:
        previous = tmp_path / 'original-fixture-lock'
        stripe.rename(previous)
        if fault == 'replaced-stripe':
            stripe.touch(mode=0o600)
            assert stripe.stat().st_ino != previous.stat().st_ino
        elif fault == 'symlink-stripe':
            stripe.symlink_to(previous)

    recovery.store = PrivateObjects(store.root, writer_recovery=True)
    assert recovery.run().status == 'pending'
    assert_recovery_blocked(recovery, row)
    assert store.path(str(row.pk)).read_bytes() == SOURCE[:8]
    if fault == 'missing-stripe':
        assert not os.path.lexists(stripe)


def test_purge_preserves_fixed_lock_namespace_without_per_upload_metadata(recovery):
    root = recovery.store.root
    marker = root / storage._NAMESPACE
    stripe_names = {recovery.store._stripe(index) for index in range(64)}
    entries = set(root.iterdir())
    assert {path.name for path in entries} == stripe_names | {marker.name}
    assert all((root / name).stat().st_size == 0 for name in stripe_names)
    namespace = marker.read_bytes()
    inodes = {path: path.stat().st_ino for path in entries}
    row = active_row(recovery)
    row.writer_binding = new_binding(recovery.store, row)

    assert recovery.run().status == 'complete'
    assert_recovered(recovery, row)
    assert set(root.iterdir()) == entries
    assert {path: path.stat().st_ino for path in entries} == inodes
    assert marker.read_bytes() == namespace
    assert all((root / name).stat().st_size == 0 for name in stripe_names)


def test_opted_in_storage_rejects_unguarded_source_writes(recovery):
    store = recovery.store
    key = str(uuid4())
    with pytest.raises(RuntimeError, match='requires a writer guard'):
        store.put(key, [SOURCE], len(SOURCE))
    assert not os.path.lexists(store.path(key))


class AuthoredStreamInterrupted(BaseException):
    pass


@pytest.mark.parametrize('error', [OSError, AuthoredStreamInterrupted])
def test_stream_initialization_failure_closes_raw_descriptor_before_guard_release(recovery, monkeypatch, error):
    store = recovery.store
    key = str(uuid4())
    opened = []

    def fail_fdopen(fd, mode, **options):
        assert mode == 'wb'
        assert os.fstat(fd).st_ino == store.path(key).stat().st_ino
        opened.append(fd)
        raise error('Fixture stream initialization failed')

    with store.source_writer(key) as guard:
        binding = guard.binding(1, uuid4())
        with monkeypatch.context() as fault:
            fault.setattr(storage.os, 'fdopen', fail_fdopen)
            with pytest.raises(error, match='Fixture stream initialization failed'):
                guard.put([SOURCE], len(SOURCE))
        assert len(opened) == 1
        with pytest.raises(OSError) as closed:
            os.fstat(opened[0])
        assert closed.value.errno == errno.EBADF
        assert not os.path.lexists(store.path(key))
        with pytest.raises(storage.WriterClosureUnavailable), store.closed_writer(key, binding):
            pytest.fail('Receiver guard released before the receiver acknowledged')

    with store.closed_writer(key, binding) as closure:
        assert closure.purge_confirmed() is True


def test_busy_stripe_defers_only_colliding_recovery_targets(recovery):
    row = active_row(recovery, key=UUID(int=1))
    other_stripe = active_row(recovery, key=UUID(int=2))
    row.writer_binding = new_binding(recovery.store, row)
    other_stripe.writer_binding = new_binding(recovery.store, other_stripe)
    colliding_uuid = UUID(int=65)

    with recovery.store.source_writer(str(colliding_uuid)):
        # Receivers can share the same stripe and obtain independent descriptors.
        with recovery.store.source_writer(str(row.pk)):
            assert recovery.run(limit=1).cursor == row.pk
        assert recovery.run(limit=1).status == 'pending'
        assert other_stripe.purge_confirmed and not other_stripe.writer_active
        assert recovery.quota.reserved_bytes == row.held_bytes == len(SOURCE)
        assert recovery.store.path(str(row.pk)).read_bytes() == SOURCE[:8]
        assert_files(recovery, other_stripe, present=False)

    recovery.clock.now = recovery.intent.due_at
    assert recovery.run().status == 'complete'
    assert recovery.quota.reserved_bytes == 0 and row.purge_confirmed
    assert recovery.quota.save.call_count == 2


def test_partial_purge_preserves_writer_binding_until_absence_is_confirmed(recovery, monkeypatch):
    row = active_row(recovery)
    binding = row.writer_binding = new_binding(recovery.store, row)
    key = str(row.pk)
    manifest = recovery.store.path(key, 'manifest')
    manifest.write_bytes(MANIFEST)
    unlink = os.unlink

    def fail_manifest(name, *, dir_fd):
        if name == manifest.name:
            raise OSError('Fixture manifest unlink interruption')
        return unlink(name, dir_fd=dir_fd)

    with monkeypatch.context() as fault:
        fault.setattr(os, 'unlink', fail_manifest)
        assert recovery.run().status == 'pending'
    assert_recovery_blocked(recovery, row)
    assert row.writer_binding == binding
    assert not os.path.lexists(recovery.store.path(key))
    assert manifest.read_bytes() == MANIFEST

    recovery.clock.now = recovery.intent.due_at
    assert recovery.run().status == 'complete'
    assert_recovered(recovery, row)


def test_lost_lease_after_purge_retains_active_binding_and_reservation(recovery):
    row = active_row(recovery)
    binding = row.writer_binding = new_binding(recovery.store, row)
    source = recovery.store.path(str(row.pk))

    def replace_lease_at_settlement():
        if not os.path.lexists(source):
            recovery.clock.now = recovery.intent.lease_until
            recovery.intent.lease_until += cleanup.LEASE_DURATION
            recovery.intent.fence += 1

    recovery.before_intent_lock.side_effect = replace_lease_at_settlement
    assert recovery.run() is None
    assert recovery.intent.fence == 2 and recovery.intent.status == 'pending'
    assert_files(recovery, row, present=False)
    assert_recovery_blocked(recovery, row)
    assert row.writer_binding == binding

    recovery.before_intent_lock.side_effect = None
    recovery.clock.now = recovery.intent.lease_until
    assert recovery.run().status == 'complete'
    assert_recovered(recovery, row)


def test_cleanup_cannot_settle_if_exact_writer_attempt_changes_after_confirmation(recovery):
    row = active_row(recovery)
    row.writer_binding = new_binding(recovery.store, row)
    replacement_attempt = str(uuid4())
    source = recovery.store.path(str(row.pk))

    def change_attempt_at_settlement():
        if not os.path.lexists(source):
            row.writer_binding = {**row.writer_binding, 'attempt': replacement_attempt}

    recovery.before_intent_lock.side_effect = change_attempt_at_settlement
    assert recovery.run().status == 'pending'
    assert_files(recovery, row, present=False)
    assert_recovery_blocked(recovery, row)
    assert row.writer_binding['attempt'] == replacement_attempt


@pytest.fixture
def receiver(recovery, monkeypatch):
    row = recovery.add_upload(generation=9, deleted=True)
    row.status = 'awaiting_bytes'
    row.id = row.pk
    row.writer_binding = None
    row.held_bytes = row.declared_bytes
    row.media_type = 'application/pdf'
    recovery.quota.reserved_bytes = row.held_bytes
    actor = SimpleNamespace(pk=row.actor_id, is_authenticated=True, is_active=True)

    def get(*, pk):
        assert pk == row.pk
        return row

    def values(*fields):
        return SimpleNamespace(get=lambda pk: {field: getattr(get(pk=pk), field) for field in fields})

    def lifecycle_lock(key):
        assert not service.transaction.get_autocommit()
        return recovery.quota, get(pk=key)

    objects = service.Upload.objects
    monkeypatch.setattr(objects, 'select_related', lambda *fields: SimpleNamespace(get=get), raising=False)
    monkeypatch.setattr(objects, 'values', values, raising=False)
    monkeypatch.setattr(service, 'locked', lifecycle_lock)
    monkeypatch.setattr(service, 'live', lambda upload: True)
    monkeypatch.setattr(service, 'connection', SimpleNamespace(in_atomic_block=False))
    return actor, row


def test_receiver_paused_before_guard_cannot_recreate_purged_source(recovery, receiver, monkeypatch):
    actor, row = receiver
    store = recovery.store
    start_writer = store.source_writer

    @contextmanager
    def pause_before_guard(key):
        assert service.withdraw(actor, row.pk, store).purge_confirmed
        with start_writer(key) as guard:
            yield guard

    monkeypatch.setattr(store, 'source_writer', pause_before_guard)
    with pytest.raises(service.Conflict):
        service.accept_bytes(actor, row.pk, [SOURCE], store)
    assert_recovered(recovery, row)


def test_receiver_paused_after_active_commit_holds_guard_before_source_open(recovery, receiver, monkeypatch):
    actor, row = receiver
    store = recovery.store
    write_source = store._put_source

    def withdraw_before_open(key, chunks, expected_bytes, directory):
        assert row.writer_active and row.writer_binding['generation'] == row.generation
        assert not os.path.lexists(store.path(key))
        assert service.withdraw(actor, row.pk, store).status == 'withdrawn'
        assert_recovery_blocked(recovery, row)
        assert not os.path.lexists(store.path(key))
        return write_source(key, chunks, expected_bytes, directory)

    monkeypatch.setattr(store, '_put_source', withdraw_before_open)
    with pytest.raises(service.Conflict):
        service.accept_bytes(actor, row.pk, [SOURCE], store)
    assert_recovered(recovery, row)


def test_receiver_releases_matching_active_binding_on_normal_completion(recovery, receiver):
    actor, row = receiver
    store = recovery.store

    def chunks():
        assert row.writer_active and row.writer_binding['generation'] == row.generation
        with pytest.raises(storage.WriterClosureUnavailable), store.closed_writer(str(row.pk), row.writer_binding):
            pytest.fail('Receiver guard released before streaming completed')
        yield SOURCE

    assert service.accept_bytes(actor, row.pk, chunks(), store).status == 'quarantined'
    assert not row.writer_active and row.writer_binding is None
    assert recovery.quota.reserved_bytes == row.held_bytes == 0
    assert recovery.quota.used_bytes == row.stored_bytes == len(SOURCE)
    assert store.read(str(row.pk)) == SOURCE


def test_receiver_cannot_acknowledge_a_different_writer_binding(recovery, receiver, monkeypatch):
    actor, row = receiver
    store = recovery.store
    write_source = store._put_source
    replacement_attempt = str(uuid4())

    def replace_binding_after_write(key, chunks, expected_bytes, directory):
        result = write_source(key, chunks, expected_bytes, directory)
        row.writer_binding = {**row.writer_binding, 'attempt': replacement_attempt}
        return result

    monkeypatch.setattr(store, '_put_source', replace_binding_after_write)
    with pytest.raises(service.Conflict):
        service.accept_bytes(actor, row.pk, [SOURCE], store)
    assert row.status == 'receiving' and row.writer_active
    assert row.writer_binding['attempt'] == replacement_attempt
    assert recovery.quota.reserved_bytes == row.held_bytes == len(SOURCE)
    recovery.quota.save.assert_not_called()
    assert store.read(str(row.pk)) == SOURCE
