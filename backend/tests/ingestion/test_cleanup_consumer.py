"""Exercise the consumer with authored files and in-memory ORM boundaries."""

from contextlib import contextmanager
from copy import copy
from datetime import datetime, timedelta, timezone
import os
from types import SimpleNamespace
from unittest.mock import Mock
from uuid import UUID, uuid4

import pytest

from modules.ingestion import cleanup, service
from modules.ingestion.storage import PrivateObjects


SOURCE = b'%PDF-authored fixture'
MANIFEST = b'{"text":"authored fixture"}'
CHARGE = len(SOURCE) + len(MANIFEST)


class Rows:
    """Minimal lazy query stand-in. PostgreSQL query/transaction checks live in the probe."""

    def __init__(self, read, *, locking_read=None):
        self.read = read
        self.locking_read = locking_read

    def filter(self, *conditions, **filters):
        def matches_field(row, field, expected):
            parts = field.split('__')
            compare = parts.pop() if parts[-1] in ('gt', 'lte') else 'exact'
            value = row
            for part in parts:
                value = value.get(part) if isinstance(value, dict) else getattr(value, part)
            if compare == 'gt':
                return value is not None and value > expected
            if compare == 'lte':
                return value <= expected
            return value == expected

        def matches_condition(row, condition):
            results = [
                matches_field(row, *child) if isinstance(child, tuple) else matches_condition(row, child)
                for child in condition.children
            ]
            assert not condition.negated
            return any(results) if condition.connector == 'OR' else all(results)

        return Rows(lambda: [row for row in self.read()
                             if all(matches_condition(row, cond) for cond in conditions)
                             and all(matches_field(row, field, value) for field, value in filters.items())],
                    locking_read=self.locking_read)

    def select_for_update(self):
        def read_locked():
            self.locking_read()
            return self.read()

        return Rows(read_locked)

    def order_by(self, field):
        return Rows(lambda: sorted(self.read(), key=lambda row: getattr(row, field)))

    def values_list(self, field, *, flat):
        assert flat
        return Rows(lambda: [getattr(row, field) for row in self.read()])

    def __getitem__(self, index):
        return self.read()[index]

    def first(self):
        rows = self.read()
        return rows[0] if rows else None

    def exists(self):
        return bool(self.read())

    def update(self, **changes):
        rows = self.read()
        for row in rows:
            vars(row).update(changes)
        return len(rows)


@pytest.fixture
def scenario(tmp_path, monkeypatch):
    now = datetime(2026, 11, 22, tzinfo=timezone.utc)
    clock = SimpleNamespace(now=now)
    tenant = uuid4()
    learner = SimpleNamespace(pk=uuid4(), tenant_id=tenant, authorization_generation=9)
    course = SimpleNamespace(pk=uuid4(), tenant_id=tenant)
    relationship = SimpleNamespace(learner_id=learner.pk, guardian_id=10)
    consent = SimpleNamespace(purpose='tutoring', relationship=relationship, withdrawn_at=now,
                              granted_at=now - timedelta(hours=1), expires_at=now + timedelta(hours=1))
    intent = SimpleNamespace(
        pk=uuid4(), consent=consent, consent_id=uuid4(), tenant_id=tenant, learner=learner, learner_id=learner.pk,
        purpose='tutoring', uploader_id=relationship.guardian_id, cutoff_generation=8,
        policy_version='effective-loss-v1', disposition='full_purge',
        status='pending', fence=0, due_at=now, cursor=None, lease_until=None, attempts=0, failure_code='',
    )
    quota = SimpleNamespace(pk=1, learner_id=learner.pk, course_id=course.pk,
                            used_bytes=0, reserved_bytes=0, save=Mock())
    uploads = {}
    atomic_depth = 0
    before_intent_lock = Mock()

    @contextmanager
    def atomic_boundary():
        nonlocal atomic_depth
        atomic_depth += 1
        try:
            yield
        finally:
            atomic_depth -= 1

    def claim_at_boundary():
        if (intent.status != 'pending' or intent.due_at > clock.now
                or (intent.lease_until is not None and intent.lease_until > clock.now)):
            return None
        intent.fence += 1
        intent.lease_until = clock.now + cleanup.LEASE_DURATION
        return copy(intent)

    def lock_intent_at_boundary():
        assert atomic_depth == 1
        before_intent_lock()

    def load_locked(key):
        assert atomic_depth == 1
        return uploads[key].quota, uploads[key]

    class FixtureStore(PrivateObjects):
        def purge_confirmed(self, object_id):
            assert atomic_depth == 0
            return super().purge_confirmed(object_id)

    store = FixtureStore(tmp_path / 'private')
    monkeypatch.setattr(cleanup, '_claim_intent', claim_at_boundary)
    monkeypatch.setattr(cleanup, 'locked', load_locked)
    monkeypatch.setattr(cleanup.transaction, 'atomic', atomic_boundary)
    monkeypatch.setattr(cleanup.transaction, 'get_autocommit', lambda: atomic_depth == 0)
    monkeypatch.setattr(cleanup.timezone, 'now', lambda: clock.now)
    monkeypatch.setattr(cleanup.Upload, 'objects', Rows(lambda: list(uploads.values())))
    monkeypatch.setattr(cleanup.ConsentCleanupIntent, 'objects',
                        Rows(lambda: [intent], locking_read=lock_intent_at_boundary))

    def add_upload(*, key=None, generation=8, actor_id=10, purpose='tutoring', cohort='local',
                   writer_active=False, deleted=False):
        key = key or uuid4()
        row_learner, row_course, row_quota = learner, course, quota
        if cohort != 'local':
            row_tenant = uuid4() if cohort == 'other-tenant' else tenant
            row_learner = SimpleNamespace(pk=uuid4(), tenant_id=row_tenant)
            row_course = SimpleNamespace(pk=uuid4(), tenant_id=row_tenant)
            row_quota = SimpleNamespace(pk=uuid4(), learner_id=row_learner.pk, course_id=row_course.pk,
                                        used_bytes=0, reserved_bytes=0, save=Mock())
        resource = SimpleNamespace(
            learner=row_learner, learner_id=row_learner.pk, course=row_course, course_id=row_course.pk,
            kind='file', purpose=purpose, edition_id='fixture.edition', edition_version=1,
        )
        upload = SimpleNamespace(
            pk=key, quota=row_quota, quota_id=row_quota.pk, resource=resource, actor_id=actor_id,
            scope={'learner': str(row_learner.pk), 'course': str(row_course.pk),
                   'edition': 'fixture.edition', 'version': 1, 'purpose': purpose},
            authorization_generation=generation, generation=1, purge_confirmed=False,
            declared_bytes=len(SOURCE), stored_bytes=len(SOURCE), manifest_bytes=len(MANIFEST), held_bytes=0,
            status='private_ready', writer_active=writer_active, save=Mock(),
        )
        if writer_active:
            upload.status = 'receiving'
            upload.stored_bytes = upload.manifest_bytes = 0
            upload.held_bytes = len(SOURCE)
            store.path(str(key)).write_bytes(SOURCE[:8])
        elif deleted:
            upload.status = 'deleted'
            upload.stored_bytes = upload.manifest_bytes = 0
        else:
            store.put(str(key), [SOURCE], len(SOURCE))
            store.put_manifest(str(key), MANIFEST)
        row_quota.used_bytes += upload.stored_bytes + upload.manifest_bytes
        row_quota.reserved_bytes += upload.held_bytes
        uploads[key] = upload
        return upload

    def run(limit=25):
        return cleanup.run_batch(store, limit=limit)

    return SimpleNamespace(intent=intent, consent=consent, clock=clock, quota=quota, store=store,
                           add_upload=add_upload, atomic=atomic_boundary, run=run,
                           before_intent_lock=before_intent_lock)


def assert_files(scenario, upload, *, present):
    for suffix, payload in [('blob', SOURCE), ('manifest', MANIFEST)]:
        path = scenario.store.path(str(upload.pk), suffix)
        if present:
            assert path.read_bytes() == payload
        else:
            assert not os.path.lexists(path)


def test_exact_guardian_cohort_cutoff_preserves_same_byte_regrant_and_other_scopes(scenario):
    eligible = [scenario.add_upload(generation=8), scenario.add_upload(generation=0)]
    retained = [scenario.add_upload(generation=9), scenario.add_upload(actor_id=11),
                scenario.add_upload(purpose='guardian_reporting'), scenario.add_upload(cohort='other-learner'),
                scenario.add_upload(cohort='other-tenant')]

    assert scenario.run().status == 'complete'
    assert scenario.run() is None

    for upload in eligible:
        assert upload.status == 'deleted' and upload.purge_confirmed and upload.generation == 2
        assert upload.stored_bytes == upload.manifest_bytes == upload.held_bytes == 0
        assert_files(scenario, upload, present=False)
    for upload in retained:
        assert upload.status == 'private_ready' and upload.generation == 1
        assert_files(scenario, upload, present=True)
    assert scenario.quota.used_bytes == 3 * CHARGE
    assert all(upload.quota.used_bytes == CHARGE for upload in retained[-2:])
    assert scenario.quota.save.call_count == 2


@pytest.mark.parametrize('tamper', ['live-consent', 'other-guardian', 'wrong-tenant', 'widened-cutoff'])
def test_inconsistent_intent_cannot_purge(scenario, tamper):
    upload = scenario.add_upload()
    if tamper == 'live-consent':
        scenario.consent.withdrawn_at = None
    elif tamper == 'other-guardian':
        scenario.intent.uploader_id = 11
    elif tamper == 'wrong-tenant':
        scenario.intent.tenant_id = uuid4()
    else:
        scenario.intent.cutoff_generation = scenario.intent.learner.authorization_generation

    assert scenario.run().status == 'blocked'
    assert scenario.intent.failure_code == 'integrity_error'
    assert_files(scenario, upload, present=True)
    assert scenario.quota.used_bytes == CHARGE
    upload.save.assert_not_called()


def test_worker_rejects_external_scope_and_an_enclosing_atomic_block(scenario):
    upload = scenario.add_upload()
    with pytest.raises(TypeError):
        cleanup.run_batch(scenario.store, upload_id=upload.pk)
    with scenario.atomic(), pytest.raises(RuntimeError, match='autocommit'):
        scenario.run()
    assert scenario.intent.fence == 0
    assert_files(scenario, upload, present=True)


@pytest.mark.parametrize('operation', ['accept_bytes', 'withdraw'])
@pytest.mark.parametrize('in_atomic_block', [True, False], ids=['atomic-block', 'manual-autocommit-off'])
def test_byte_mutations_reject_enclosing_transactions_before_lifecycle_work(
    scenario, monkeypatch, operation, in_atomic_block,
):
    upload = scenario.add_upload()
    lock = Mock(side_effect=AssertionError('Upload queried before checking autocommit'))
    store = Mock(spec=PrivateObjects)
    actor = SimpleNamespace(pk=upload.actor_id, is_authenticated=True, is_active=True)
    monkeypatch.setattr(service, 'locked', lock)
    monkeypatch.setattr(service, 'connection', SimpleNamespace(in_atomic_block=in_atomic_block))
    monkeypatch.setattr(service.transaction, 'get_autocommit', lambda: False)
    args = (actor, upload.pk, [SOURCE], store) if operation == 'accept_bytes' else (actor, upload.pk, store)

    with pytest.raises(service.Conflict, match='autocommit'):
        getattr(service, operation)(*args)

    lock.assert_not_called()
    assert not store.mock_calls
    assert_files(scenario, upload, present=True)


def test_disputed_binding_retains_bytes_and_blocks_credit(scenario):
    upload = scenario.add_upload()
    upload.resource.course_id = uuid4()

    assert scenario.run().failure_code == 'integrity_error'
    assert scenario.intent.status == 'pending'
    assert_files(scenario, upload, present=True)
    assert scenario.quota.used_bytes == CHARGE
    upload.save.assert_not_called()


def test_open_writer_does_not_starve_later_page_and_is_revisited_after_close(scenario):
    writer = scenario.add_upload(key=UUID(int=1), writer_active=True)
    later = scenario.add_upload(key=UUID(int=2))

    assert scenario.run(limit=1).cursor == writer.pk
    assert writer.status == 'withdrawn' and writer.generation == 2 and writer.writer_active
    assert scenario.store.path(str(writer.pk)).read_bytes() == SOURCE[:8]
    assert scenario.run(limit=1).status == 'pending'
    assert later.purge_confirmed
    assert_files(scenario, later, present=False)
    assert scenario.quota.used_bytes == 0
    assert scenario.quota.reserved_bytes == writer.held_bytes == len(SOURCE)
    assert scenario.intent.cursor is None
    assert scenario.run() is None

    # Fixture acknowledges closure before retry; expiry alone cannot prove closure.
    writer.writer_active = False
    scenario.clock.now = scenario.intent.due_at
    assert scenario.run(limit=1).status == 'complete'
    assert writer.purge_confirmed and writer.generation == 2
    assert scenario.quota.reserved_bytes == 0
    assert_files(scenario, writer, present=False)


def test_retries_exhaust_without_force_closing_a_writer_and_replay_preserves_scope(scenario):
    writer = scenario.add_upload(writer_active=True)
    new = scenario.add_upload(generation=9)
    for _ in range(cleanup.MAX_ATTEMPTS):
        scenario.run()
        scenario.clock.now = scenario.intent.due_at + timedelta(minutes=2)

    assert scenario.run() is None
    assert scenario.intent.status == 'blocked' and scenario.intent.failure_code == 'writer_active'
    assert writer.writer_active and scenario.quota.reserved_bytes == len(SOURCE)
    assert not cleanup.retry_blocked_intent(uuid4())
    writer.writer_active = False
    assert cleanup.retry_blocked_intent(scenario.intent.pk)
    assert scenario.run().status == 'complete'
    assert scenario.intent.cutoff_generation == 8
    assert_files(scenario, writer, present=False)
    assert_files(scenario, new, present=True)


def test_partial_purge_keeps_full_charge_until_successful_replay(scenario, monkeypatch):
    upload = scenario.add_upload()
    key = str(upload.pk)
    manifest = scenario.store.path(key, 'manifest')
    unlink = os.unlink

    def fail_manifest(name, *, dir_fd):
        if name == manifest.name:
            raise OSError('fixture manifest unlink error')
        return unlink(name, dir_fd=dir_fd)

    with monkeypatch.context() as fault:
        fault.setattr(os, 'unlink', fail_manifest)
        receipt = scenario.run()
    assert receipt.status == 'pending' and receipt.failure_code == 'purge_failed'
    assert upload.status == 'withdrawn' and not upload.purge_confirmed
    assert not scenario.store.path(key).exists() and manifest.read_bytes() == MANIFEST
    assert scenario.quota.used_bytes == CHARGE
    scenario.quota.save.assert_not_called()

    scenario.clock.now = scenario.intent.due_at
    assert scenario.run().status == 'complete'
    assert scenario.run() is None
    assert_files(scenario, upload, present=False)
    assert scenario.quota.used_bytes == 0 and upload.purge_confirmed
    scenario.quota.save.assert_called_once()


def test_interruption_after_unlink_reconfirms_absence_before_refund(scenario, monkeypatch):
    upload = scenario.add_upload()
    purge = scenario.store.purge_confirmed

    def interrupted(key):
        assert purge(key) is True
        raise RuntimeError('fixture interruption before settlement')

    with monkeypatch.context() as fault:
        fault.setattr(scenario.store, 'purge_confirmed', interrupted)
        with pytest.raises(RuntimeError, match='fixture interruption'):
            scenario.run()
    assert_files(scenario, upload, present=False)
    assert scenario.quota.used_bytes == CHARGE and not upload.purge_confirmed
    assert scenario.run() is None

    scenario.clock.now = scenario.intent.lease_until
    confirmation = Mock(wraps=purge)
    monkeypatch.setattr(scenario.store, 'purge_confirmed', confirmation)
    assert scenario.run().status == 'complete'
    confirmation.assert_called_once_with(str(upload.pk))
    assert scenario.quota.used_bytes == 0 and upload.purge_confirmed
    scenario.quota.save.assert_called_once()


def test_stale_lease_cannot_settle_after_replacement_worker(scenario, monkeypatch):
    upload = scenario.add_upload()
    purge = scenario.store.purge_confirmed

    def takeover(key):
        result = purge(key)
        with monkeypatch.context() as replacement:
            replacement.setattr(scenario.store, 'purge_confirmed', purge)
            scenario.clock.now = scenario.intent.lease_until
            assert scenario.run().status == 'complete'
        return result

    monkeypatch.setattr(scenario.store, 'purge_confirmed', takeover)
    assert scenario.run() is None
    assert scenario.intent.status == 'complete' and scenario.intent.fence == 2
    assert scenario.quota.used_bytes == 0 and upload.purge_confirmed
    scenario.quota.save.assert_called_once()


def test_takeover_after_pre_io_check_but_before_settlement_lock_retains_charge(scenario):
    upload = scenario.add_upload()
    source = scenario.store.path(str(upload.pk))

    def take_over_during_settlement():
        if not source.exists():
            scenario.clock.now = scenario.intent.lease_until
            scenario.intent.lease_until += cleanup.LEASE_DURATION
            scenario.intent.fence += 1

    scenario.before_intent_lock.side_effect = take_over_during_settlement
    assert scenario.run() is None
    assert scenario.intent.fence == 2 and scenario.intent.status == 'pending'
    assert_files(scenario, upload, present=False)
    assert upload.status == 'withdrawn' and not upload.purge_confirmed
    assert scenario.quota.used_bytes == CHARGE
    scenario.quota.save.assert_not_called()


def test_legacy_deleted_row_needs_confirmation_without_a_second_refund(scenario, monkeypatch):
    upload = scenario.add_upload(deleted=True)
    unrelated = scenario.add_upload(generation=9)

    with monkeypatch.context() as fault:
        fault.setattr(scenario.store, 'purge_confirmed', Mock(return_value=False))
        receipt = scenario.run()
    assert receipt.status == 'pending' and receipt.failure_code == 'purge_failed'
    assert upload.status == 'deleted' and not upload.purge_confirmed
    assert scenario.quota.used_bytes == CHARGE

    scenario.clock.now = scenario.intent.due_at
    confirmation = Mock(wraps=scenario.store.purge_confirmed)
    monkeypatch.setattr(scenario.store, 'purge_confirmed', confirmation)
    assert scenario.run().status == 'complete'
    confirmation.assert_called_once_with(str(upload.pk))
    assert upload.purge_confirmed and upload.generation == 1
    assert scenario.quota.used_bytes == CHARGE
    assert_files(scenario, unrelated, present=True)
    scenario.quota.save.assert_not_called()
