"""AUTH-021: parent progress summary and privacy/tombstone replay tests (R047/R056/R059/R061/R079)."""

from datetime import datetime, timedelta, timezone
import pytest

from modules.learning.ledger import EvidenceEvent, LedgerScope
from modules.learning.parent_summary import ParentSummaryError, build_parent_progress_summary
from modules.operations.privacy import (
    PRIVACY_POLICY_VERSION,
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
    {'member_active': False},
    {'learner_active': False},
    {'enrollment_valid': False},
    {'entitlement_valid': False},
    {'course_active': False},
    {'edition_active': False},
])
def test_parent_summary_denies_unauthorized_roles_purposes_or_revoked_scope(overrides):
    with pytest.raises(ParentSummaryError, match='^access_denied$'):
        build_parent_progress_summary(
            [],
            scope=_guardian_scope(**overrides),
            objectives=[('objective.quantitative', 1)],
        )


def test_parent_summary_reports_all_statuses_uncertainty_and_next_steps_honestly():
    events = [
        # obj.dev: 1 assisted + 1 independent success -> developing
        _attempt('ev.h1', day=0, objective_id='objective.dev', item_id='item.q1', family_id='family.a', evidence_class='assisted', hints_used=1),
        _attempt('ev.s1', day=1, objective_id='objective.dev', item_id='item.q2', family_id='family.b', evidence_class='independent', outcome='correct'),
        # obj.support: 1 independent failure -> needs_support
        _attempt('ev.f1', day=0, objective_id='objective.support', item_id='item.q3', family_id='family.a', evidence_class='independent', outcome='incorrect'),
        # obj.ready: 2 distinct families -> ready_for_review
        _attempt('ev.r1', day=0, objective_id='objective.ready', item_id='item.q4', family_id='family.a', evidence_class='independent', outcome='correct'),
        _attempt('ev.r2', day=1, objective_id='objective.ready', item_id='item.q5', family_id='family.b', evidence_class='independent', outcome='correct'),
        # obj.ret: 2 families + delayed 3rd family -> retained
        _attempt('ev.t1', day=0, objective_id='objective.ret', item_id='item.q6', family_id='family.a', evidence_class='independent', outcome='correct'),
        _attempt('ev.t2', day=1, objective_id='objective.ret', item_id='item.q7', family_id='family.b', evidence_class='independent', outcome='correct'),
        _attempt('ev.t3', day=10, objective_id='objective.ret', item_id='item.q8', family_id='family.c', evidence_class='independent', outcome='correct'),
        # obj.probe: ready_for_review then later failure -> probe_needed
        _attempt('ev.p1', day=0, objective_id='objective.probe', item_id='item.q9', family_id='family.a', evidence_class='independent', outcome='correct'),
        _attempt('ev.p2', day=1, objective_id='objective.probe', item_id='item.q10', family_id='family.b', evidence_class='independent', outcome='correct'),
        _attempt('ev.p3', day=5, objective_id='objective.probe', item_id='item.q11', family_id='family.c', evidence_class='independent', outcome='incorrect'),
        # obj.pend: ambiguous pending_review -> await_educator_review
        _attempt('ev.a1', day=0, objective_id='objective.pend', item_id='item.q12', family_id='family.a', evidence_class='ambiguous', outcome='pending_review'),
        # Other learner's event must never appear
        _attempt('ev.other', day=1, objective_id='objective.unassessed', item_id='item.q99', family_id='family.z', learner_id='fixture.learner-b'),
    ]
    summary = build_parent_progress_summary(
        events,
        scope=_guardian_scope(),
        objectives=[
            ('objective.dev', 1),
            ('objective.support', 1),
            ('objective.ready', 1),
            ('objective.ret', 1),
            ('objective.probe', 1),
            ('objective.pend', 1),
            ('objective.unassessed', 1),
        ],
    )
    assert summary.raw_chat_included is False
    assert summary.fabricated_percentage_included is False
    by_id = {item.objective_id: item for item in summary.objectives}

    assert by_id['objective.dev'].status == 'developing'
    assert by_id['objective.dev'].assisted_count == 1
    assert by_id['objective.dev'].recommended_next_action == 'practice_new_item_family'
    assert by_id['objective.dev'].is_calibrated is False

    assert by_id['objective.support'].status == 'needs_support'
    assert by_id['objective.support'].recommended_next_action == 'guided_support_needed'

    assert by_id['objective.ready'].status == 'ready_for_review'
    assert by_id['objective.ready'].recommended_next_action == 'schedule_delayed_review'

    assert by_id['objective.ret'].status == 'retained'
    assert by_id['objective.ret'].recommended_next_action == 'maintain_periodic_review'

    assert by_id['objective.probe'].uncertainty == 'probe_needed'
    assert by_id['objective.probe'].recommended_next_action == 'schedule_probe_check'

    assert by_id['objective.pend'].uncertainty == 'pending_review'
    assert by_id['objective.pend'].recommended_next_action == 'await_educator_review'

    assert by_id['objective.unassessed'].status == 'unassessed'
    assert by_id['objective.unassessed'].uncertainty == 'no_evidence'
    assert by_id['objective.unassessed'].recommended_next_action == 'start_diagnostic_or_practice'
    assert by_id['objective.unassessed'].review_due_at is None


def test_parent_summary_distinguishes_invalid_scope_objectives_and_events():
    with pytest.raises(ParentSummaryError, match='^invalid_scope$'):
        build_parent_progress_summary([], scope=_guardian_scope(tenant_id='BAD TENANT'), objectives=[('objective.quantitative', 1)])
    with pytest.raises(ParentSummaryError, match='^invalid_evidence$'):
        build_parent_progress_summary('not-a-list', scope=_guardian_scope(), objectives=[('objective.quantitative', 1)])
    with pytest.raises(ParentSummaryError, match='^invalid_objectives$'):
        build_parent_progress_summary([], scope=_guardian_scope(), objectives=[])
    with pytest.raises(ParentSummaryError, match='^invalid_objectives$'):
        build_parent_progress_summary([], scope=_guardian_scope(), objectives=[('BAD ID', 1)])
    with pytest.raises(ParentSummaryError, match='^duplicate_objective$'):
        build_parent_progress_summary(
            [],
            scope=_guardian_scope(),
            objectives=[('objective.quantitative', 1), ('objective.quantitative', 1)],
        )


# --- 2. Telemetry redaction tests (R059, R079) ---


def test_telemetry_redactor_preserves_iso_timestamp_and_strips_free_text_pii_and_bad_types():
    raw = {
        'event_type': 'tutor.turn',
        'service': 'sebaverse-api',
        'occurred_at': '2026-11-26T16:20:00Z',
        'status_code': 200,
        'latency_ms': 142,
        'token_count_in': 320,
        'token_count_out': 95,
        'cached_units': 280,
        'edition_id': 'edition.quantitative',
        'edition_version': 1,
        # Spoofed policy_version must be dropped (not override sanitizer policy_version)
        'policy_version': 'spoofed.v9',
        # Forbidden PII / child content fields:
        'prompt': 'أنا اسمي عمر ومش فاهم الكسور',
        'transcript': 'child audio transcript',
        'audio': b'raw-bytes',
        'learner_id': 'fixture.learner-a',
        'tenant_id': 'fixture.tenant-a',
        'email': 'parent@example.com',
        'answer_key': '7',
        # Free text / PII smuggled into allowlisted identifier fields must be dropped:
        'reason_code': 'Omar lives in Cairo',
        'outcome': 'contact parent@example.com',
        # Bool and negative values in int fields must be dropped:
        'subject_tag': 'INVALID SPACE',
    }
    sanitized = sanitize_telemetry_record(raw)
    out = sanitized.as_dict()

    assert sanitized.training_corpus_eligible is False
    assert out['training_corpus_eligible'] is False
    assert out['policy_version'] == PRIVACY_POLICY_VERSION
    assert out['event_type'] == 'tutor.turn'
    assert out['occurred_at'] == '2026-11-26T16:20:00+00:00'
    assert out['latency_ms'] == 142
    assert out['cached_units'] == 280
    for forbidden in ('prompt', 'transcript', 'audio', 'learner_id', 'tenant_id', 'email', 'answer_key', 'reason_code', 'outcome', 'subject_tag'):
        assert forbidden not in out
    assert sanitized.dropped_field_count == 11

    # Bool, negative, and naive occurred_at rejected
    bad_types = sanitize_telemetry_record({
        'latency_ms': True,
        'token_count_in': -5,
        'occurred_at': '2026-11-26T16:20:00',  # naive timestamp
    })
    assert bad_types.fields == ()
    assert bad_types.dropped_field_count == 3


# --- 3. Backup-restore deletion-tombstone replay tests (R061) ---


def test_deletion_tombstone_replay_disambiguates_target_kind_and_preserves_unrelated_or_post_delete():
    records = [
        RestorableRecord('rec.u1-orig', 'fixture.tenant-a', 'fixture.learner-a', 'upload', T0, target_kind='upload', target_id='shared.id'),
        RestorableRecord('rec.u1-chunk', 'fixture.tenant-a', 'fixture.learner-a', 'chunk', T0 + timedelta(minutes=1), target_kind='upload', target_id='shared.id'),
        RestorableRecord('rec.u1-cache', 'fixture.tenant-a', 'fixture.learner-a', 'cache', T0 + timedelta(minutes=2), target_kind='upload', target_id='shared.id'),
        # Session and evidence sharing the SAME target_id='shared.id' must NOT be purged by an upload tombstone!
        RestorableRecord('rec.s1-sess', 'fixture.tenant-a', 'fixture.learner-a', 'session', T0, target_kind='session', target_id='shared.id'),
        RestorableRecord('rec.s1-evid', 'fixture.tenant-a', 'fixture.learner-a', 'evidence', T0 + timedelta(minutes=1), target_kind='session', target_id='shared.id'),
        RestorableRecord('rec.u2-post', 'fixture.tenant-a', 'fixture.learner-a', 'upload', T0 + timedelta(days=5), target_kind='upload', target_id='upload.two'),
        RestorableRecord('rec.other-learner', 'fixture.tenant-a', 'fixture.learner-b', 'upload', T0, target_kind='upload', target_id='shared.id'),
        RestorableRecord('rec.other-tenant', 'fixture.tenant-b', 'fixture.learner-a', 'upload', T0, target_kind='upload', target_id='shared.id'),
    ]
    tomb_upload = DeletionTombstone(
        tombstone_id='tomb.u1',
        tenant_id='fixture.tenant-a',
        learner_id='fixture.learner-a',
        target_kind='upload',
        target_id='shared.id',
        deleted_at=T0 + timedelta(days=1),
        reason_code='guardian.withdrawal',
        authority_ref='guardian.nadia',
    )

    # Shuffled/duplicate tombstones produce identical deterministic replay and respect target_kind
    r1 = replay_deletion_tombstones(records, [tomb_upload])
    r2 = replay_deletion_tombstones(list(reversed(records)), [tomb_upload, tomb_upload])
    assert r1 == r2
    assert set(r1.purged_record_ids) == {'rec.u1-orig', 'rec.u1-chunk', 'rec.u1-cache'}
    assert set(r1.retained_record_ids) == {'rec.s1-sess', 'rec.s1-evid', 'rec.u2-post', 'rec.other-learner', 'rec.other-tenant'}

    # Session tombstone purges only target_kind='session' records matching shared.id
    tomb_session = DeletionTombstone(
        tombstone_id='tomb.s1',
        tenant_id='fixture.tenant-a',
        learner_id='fixture.learner-a',
        target_kind='session',
        target_id='shared.id',
        deleted_at=T0 + timedelta(days=1),
        reason_code='session.erasure',
        authority_ref='guardian.nadia',
    )
    r_sess = replay_deletion_tombstones(records, [tomb_session])
    assert set(r_sess.purged_record_ids) == {'rec.s1-sess', 'rec.s1-evid'}
    assert 'rec.u1-orig' in r_sess.retained_record_ids

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
    assert set(r_all.purged_record_ids) == {'rec.u1-orig', 'rec.u1-chunk', 'rec.u1-cache', 'rec.s1-sess', 'rec.s1-evid'}
    assert set(r_all.retained_record_ids) == {'rec.u2-post', 'rec.other-learner', 'rec.other-tenant'}


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
