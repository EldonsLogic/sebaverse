"""AUTH-021: parent progress summary and privacy/tombstone replay tests (R047/R056/R059/R061/R079)."""

from datetime import datetime, timedelta, timezone
import pytest

from modules.learning.ledger import EvidenceEvent, LedgerScope
from modules.learning.parent_summary import ParentSummaryError, build_parent_progress_summary
from modules.operations.privacy import (
    DeletionTombstone,
    PrivacyError,
    RestorableRecord,
    replay_deletion_tombstones,
    sanitize_telemetry_record,
)

T0 = datetime(2026, 11, 1, 10, 0, tzinfo=timezone.utc)


def _guardian_scope(**overrides) -> LedgerScope:
    base = dict(
        tenant_id='fixture.tenant-a',
        learner_id='fixture.learner-a',
        edition_id='edition.quantitative',
        edition_version=1,
        role='guardian',
        purpose='guardian_reporting',
        actor_active=True,
        member_active=True,
        tenant_matches=True,
        learner_active=True,
        relationship_valid=True,
        consent_valid=True,
        enrollment_valid=True,
        entitlement_valid=True,
        course_active=True,
        edition_active=True,
    )
    base.update(overrides)
    return LedgerScope(**base)


def _attempt(
    event_id: str,
    *,
    day: int = 0,
    objective_id: str = 'objective.quantitative',
    item_id: str = 'item.q1',
    family_id: str = 'family.a',
    evidence_class: str = 'independent',
    outcome: str = 'correct',
    hints_used: int = 0,
    learner_id: str = 'fixture.learner-a',
) -> EvidenceEvent:
    ts = T0 + timedelta(days=day)
    return EvidenceEvent(
        event_id=event_id,
        idempotency_key=f'idem.{event_id}',
        event_kind='attempt',
        tenant_id='fixture.tenant-a',
        learner_id=learner_id,
        edition_id='edition.quantitative',
        edition_version=1,
        objective_id=objective_id,
        objective_version=1,
        occurred_at=ts,
        recorded_at=ts + timedelta(seconds=5),
        actor_role='learner',
        item_id=item_id,
        item_version=1,
        family_id=family_id,
        rubric_id='rubric.quantitative',
        rubric_version=1,
        evidence_class=evidence_class,
        outcome=outcome,
        hints_used=hints_used,
        answer_revealed=False,
    )


# --- 1. Parent progress summary authorization & honesty tests (R047, R056) ---


@pytest.mark.parametrize('overrides', [
    {'role': 'learner', 'purpose': 'tutoring'},
    {'role': 'teacher', 'purpose': 'teacher_reporting'},
    {'role': 'guardian', 'purpose': 'tutoring'},
    {'consent_valid': False},
    {'relationship_valid': False},
    {'tenant_matches': False},
    {'actor_active': False},
])
def test_parent_summary_denies_unauthorized_roles_purposes_or_revoked_scope(overrides):
    with pytest.raises(ParentSummaryError, match='^access_denied$'):
        build_parent_progress_summary(
            [],
            scope=_guardian_scope(**overrides),
            objectives=[('objective.quantitative', 1)],
        )


def test_parent_summary_reports_uncertainty_assistance_and_next_step_without_chat_or_percentages():
    events = [
        # Objective 1: 1 assisted + 1 independent success -> developing
        _attempt('ev.h1', day=0, objective_id='objective.quantitative', item_id='item.q1', family_id='family.a', evidence_class='assisted', hints_used=1),
        _attempt('ev.s1', day=1, objective_id='objective.quantitative', item_id='item.q2', family_id='family.b', evidence_class='independent', outcome='correct'),
        # Other learner's event must never appear
        _attempt('ev.other', day=1, objective_id='objective.unassessed', item_id='item.q9', family_id='family.z', learner_id='fixture.learner-b'),
    ]
    summary = build_parent_progress_summary(
        events,
        scope=_guardian_scope(),
        objectives=[('objective.quantitative', 1), ('objective.unassessed', 1)],
    )
    assert summary.raw_chat_included is False
    assert summary.fabricated_percentage_included is False
    assert len(summary.objectives) == 2

    obj1, obj2 = summary.objectives
    assert obj1.status == 'developing'
    assert obj1.independent_count == 1
    assert obj1.assisted_count == 1
    assert obj1.recommended_next_action == 'practice_new_item_family'
    assert obj1.is_calibrated is False

    assert obj2.status == 'unassessed'
    assert obj2.uncertainty == 'no_evidence'
    assert obj2.recommended_next_action == 'start_diagnostic_or_practice'
    assert obj2.review_due_at is None


def test_parent_summary_rejects_empty_or_duplicate_objectives():
    with pytest.raises(ParentSummaryError, match='^invalid_objectives$'):
        build_parent_progress_summary([], scope=_guardian_scope(), objectives=[])
    with pytest.raises(ParentSummaryError, match='^duplicate_objective$'):
        build_parent_progress_summary(
            [],
            scope=_guardian_scope(),
            objectives=[('objective.quantitative', 1), ('objective.quantitative', 1)],
        )


# --- 2. Telemetry redaction tests (R059, R079) ---


def test_telemetry_redactor_strips_child_prompts_pii_and_marks_not_training_eligible():
    raw = {
        'event_type': 'tutor.turn',
        'service': 'sebaverse-api',
        'status_code': 200,
        'latency_ms': 142,
        'token_count_in': 320,
        'token_count_out': 95,
        'cached_units': 280,
        'edition_id': 'edition.quantitative',
        'edition_version': 1,
        # Forbidden PII / child content fields that must be dropped:
        'prompt': 'أنا اسمي عمر ومش فاهم الكسور',
        'transcript': 'child audio transcript',
        'audio': b'raw-bytes',
        'learner_id': 'fixture.learner-a',
        'tenant_id': 'fixture.tenant-a',
        'email': 'parent@example.com',
        'answer_key': '7',
        # Email/phone smuggled into an allowlisted string field must also be dropped:
        'reason_code': 'contact parent@example.com or +201001234567',
        'outcome': 'x' * 200,  # exceeds max label length
    }
    sanitized = sanitize_telemetry_record(raw)
    out = sanitized.as_dict()

    assert sanitized.training_corpus_eligible is False
    assert out['training_corpus_eligible'] is False
    assert out['event_type'] == 'tutor.turn'
    assert out['latency_ms'] == 142
    assert out['cached_units'] == 280
    for forbidden in ('prompt', 'transcript', 'audio', 'learner_id', 'tenant_id', 'email', 'answer_key', 'reason_code', 'outcome'):
        assert forbidden not in out
    assert sanitized.dropped_field_count == 9


# --- 3. Backup-restore deletion-tombstone replay tests (R061) ---


def test_deletion_tombstone_replay_purges_deleted_data_and_preserves_unrelated_or_post_delete():
    records = [
        RestorableRecord('rec.u1-orig', 'fixture.tenant-a', 'fixture.learner-a', 'upload', T0, target_id='upload.one'),
        RestorableRecord('rec.u1-chunk', 'fixture.tenant-a', 'fixture.learner-a', 'chunk', T0 + timedelta(minutes=1), target_id='upload.one'),
        RestorableRecord('rec.u1-cache', 'fixture.tenant-a', 'fixture.learner-a', 'cache', T0 + timedelta(minutes=2), target_id='upload.one'),
        RestorableRecord('rec.u2-keep', 'fixture.tenant-a', 'fixture.learner-a', 'upload', T0 + timedelta(days=5), target_id='upload.two'),
        RestorableRecord('rec.other-learner', 'fixture.tenant-a', 'fixture.learner-b', 'upload', T0, target_id='upload.one'),
        RestorableRecord('rec.other-tenant', 'fixture.tenant-b', 'fixture.learner-a', 'upload', T0, target_id='upload.one'),
    ]
    tomb_upload = DeletionTombstone(
        tombstone_id='tomb.u1',
        tenant_id='fixture.tenant-a',
        learner_id='fixture.learner-a',
        target_kind='upload',
        target_id='upload.one',
        deleted_at=T0 + timedelta(days=1),
        reason_code='guardian.withdrawal',
        authority_ref='guardian.nadia',
    )

    # Shuffled/duplicate tombstones produce identical deterministic replay
    r1 = replay_deletion_tombstones(records, [tomb_upload])
    r2 = replay_deletion_tombstones(list(reversed(records)), [tomb_upload, tomb_upload])
    assert r1 == r2
    assert set(r1.purged_record_ids) == {'rec.u1-orig', 'rec.u1-chunk', 'rec.u1-cache'}
    assert set(r1.retained_record_ids) == {'rec.u2-keep', 'rec.other-learner', 'rec.other-tenant'}

    # learner_all tombstone purges all records <= deleted_at for that learner, preserving post-delete and other learners
    tomb_all = DeletionTombstone(
        tombstone_id='tomb.all',
        tenant_id='fixture.tenant-a',
        learner_id='fixture.learner-a',
        target_kind='learner_all',
        deleted_at=T0 + timedelta(days=2),
        reason_code='account.erasure',
        authority_ref='guardian.nadia',
    )
    r_all = replay_deletion_tombstones(records, [tomb_all])
    assert set(r_all.purged_record_ids) == {'rec.u1-orig', 'rec.u1-chunk', 'rec.u1-cache'}
    assert set(r_all.retained_record_ids) == {'rec.u2-keep', 'rec.other-learner', 'rec.other-tenant'}


def test_tombstone_replay_rejects_model_authority_naive_timestamps_and_conflicts():
    bad_model = DeletionTombstone(
        tombstone_id='tomb.m',
        tenant_id='fixture.tenant-a',
        learner_id='fixture.learner-a',
        target_kind='learner_all',
        deleted_at=T0,
        reason_code='erasure.auto',
        authority_ref='model.gpt',
    )
    with pytest.raises(PrivacyError, match='^invalid_tombstone$'):
        replay_deletion_tombstones([], [bad_model])

    naive = DeletionTombstone(
        tombstone_id='tomb.n',
        tenant_id='fixture.tenant-a',
        learner_id='fixture.learner-a',
        target_kind='learner_all',
        deleted_at=datetime(2026, 11, 1),
        reason_code='erasure.req',
        authority_ref='guardian.nadia',
    )
    with pytest.raises(PrivacyError, match='^invalid_tombstone$'):
        replay_deletion_tombstones([], [naive])

    t1 = DeletionTombstone('tomb.dup', 'fixture.tenant-a', 'fixture.learner-a', 'learner_all', T0, 'reason.a', 'guardian.nadia')
    t2 = DeletionTombstone('tomb.dup', 'fixture.tenant-a', 'fixture.learner-a', 'learner_all', T0 + timedelta(days=1), 'reason.b', 'guardian.nadia')
    with pytest.raises(PrivacyError, match='^conflicting_tombstone$'):
        replay_deletion_tombstones([], [t1, t2])
