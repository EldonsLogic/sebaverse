"""AUTH-019: DB-free deterministic grading and replayable learning-evidence ledger tests."""

from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import pytest

from modules.assessment.grader import AssessmentError, grade_submission
from modules.learning.ledger import (
    EvidenceEvent,
    LedgerError,
    LedgerScope,
    project_objective_mastery,
    validate_event,
)

ROOT = Path(__file__).resolve().parents[3]
T0 = datetime(2026, 11, 1, 10, 0, tzinfo=timezone.utc)


def _approved_fixture():
    bundle = json.loads((ROOT / 'evals/fixtures/curriculum-v1.json').read_text(encoding='utf-8'))
    for rec in bundle['records']:
        rec['status'] = 'approved'
        rec['reviewer_ref'] = 'reviewer.fixture'
    return bundle


def _find(bundle, kind, rec_id, version=1):
    return next(r for r in bundle['records'] if r['kind'] == kind and r['id'] == rec_id and r['version'] == version)


def _scope(**overrides) -> LedgerScope:
    base = dict(
        tenant_id='fixture.tenant-a',
        learner_id='fixture.learner-a',
        edition_id='edition.quantitative',
        edition_version=1,
        role='learner',
        purpose='tutoring',
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
    day_offset: int = 0,
    item_id: str = 'item.q1',
    item_version: int = 1,
    family_id: str = 'family.a',
    evidence_class: str = 'independent',
    outcome: str = 'correct',
    hints_used: int = 0,
    answer_revealed: bool = False,
    learner_id: str = 'fixture.learner-a',
    tenant_id: str = 'fixture.tenant-a',
    edition_id: str = 'edition.quantitative',
    edition_version: int = 1,
    objective_id: str = 'objective.quantitative',
    objective_version: int = 1,
    actor_role: str = 'learner',
    idempotency_key: str | None = None,
) -> EvidenceEvent:
    ts = T0 + timedelta(days=day_offset)
    return EvidenceEvent(
        event_id=event_id,
        idempotency_key=idempotency_key or f'idem.{event_id}',
        event_kind='attempt',
        tenant_id=tenant_id,
        learner_id=learner_id,
        edition_id=edition_id,
        edition_version=edition_version,
        objective_id=objective_id,
        objective_version=objective_version,
        occurred_at=ts,
        recorded_at=ts + timedelta(seconds=5),
        actor_role=actor_role,
        item_id=item_id,
        item_version=item_version,
        family_id=family_id,
        rubric_id='rubric.quantitative',
        rubric_version=1,
        evidence_class=evidence_class,
        outcome=outcome,
        hints_used=hints_used,
        answer_revealed=answer_revealed,
    )


def _correction(
    event_id: str,
    supersedes_event_id: str,
    *,
    day_offset: int = 1,
    action: str = 'override_outcome',
    new_outcome: str | None = 'correct',
    new_evidence_class: str | None = 'independent',
    actor_role: str = 'teacher',
    adjudicator_ref: str = 'teacher.amina',
    reason_code: str = 'appeal.upheld',
) -> EvidenceEvent:
    ts = T0 + timedelta(days=day_offset)
    return EvidenceEvent(
        event_id=event_id,
        idempotency_key=f'idem.{event_id}',
        event_kind='correction',
        tenant_id='fixture.tenant-a',
        learner_id='fixture.learner-a',
        edition_id='edition.quantitative',
        edition_version=1,
        objective_id='objective.quantitative',
        objective_version=1,
        occurred_at=ts,
        recorded_at=ts + timedelta(seconds=5),
        actor_role=actor_role,
        supersedes_event_id=supersedes_event_id,
        adjudicator_ref=adjudicator_ref,
        correction_action=action,
        new_outcome=new_outcome,
        new_evidence_class=new_evidence_class,
        reason_code=reason_code,
    )


# --- 1. Deterministic grader tests (negative security & rubric fidelity first) ---


def test_grader_rejects_draft_mismatch_and_never_leaks_answer_keys():
    bundle = _approved_fixture()
    item = _find(bundle, 'item', 'item.science')
    rubric = _find(bundle, 'rubric', 'rubric.science')

    # Valid choice grade returns decision without answer key
    dec_ok = grade_submission(item, rubric, 'physical')
    assert dec_ok.outcome == 'correct'
    assert dec_ok.needs_human_review is False
    assert dec_ok.answer_key_included is False
    assert 'correct_option' not in repr(dec_ok)

    dec_bad = grade_submission(item, rubric, 'chemical')
    assert dec_bad.outcome == 'incorrect'
    assert 'physical' not in repr(dec_bad)

    # Unknown choice option rejected without leaking correct option
    with pytest.raises(AssessmentError, match='^invalid_submission$') as exc:
        grade_submission(item, rubric, 'invented-option')
    assert 'physical' not in str(exc.value)

    # Draft item or mismatched rubric rejected
    draft_item = dict(item, status='draft')
    with pytest.raises(AssessmentError, match='^invalid_item$'):
        grade_submission(draft_item, rubric, 'physical')

    other_rubric = _find(bundle, 'rubric', 'rubric.quantitative')
    with pytest.raises(AssessmentError, match='^grader_mismatch$'):
        grade_submission(item, other_rubric, 'physical')


def test_exact_set_numeric_and_human_review_graders_and_model_proposal_hold():
    bundle = _approved_fixture()

    # exact-set.v1 (case_sensitive=False)
    lang_item = _find(bundle, 'item', 'item.language')
    lang_rubric = _find(bundle, 'rubric', 'rubric.language')
    assert grade_submission(lang_item, lang_rubric, '  LERNE ').outcome == 'correct'
    assert grade_submission(lang_item, lang_rubric, 'spiele').outcome == 'incorrect'

    # numeric.v1: Eastern Arabic digits, tolerance, no eval(), rejects NaN/Infinity/expressions
    num_item = _find(bundle, 'item', 'item.quantitative')
    num_rubric = _find(bundle, 'rubric', 'rubric.quantitative')
    assert grade_submission(num_item, num_rubric, '7').outcome == 'correct'
    assert grade_submission(num_item, num_rubric, '٧').outcome == 'correct'
    assert grade_submission(num_item, num_rubric, '2+5').outcome == 'incorrect'
    assert grade_submission(num_item, num_rubric, '2+5').reason_code == 'numeric_unparseable'
    assert grade_submission(num_item, num_rubric, 'NaN').outcome == 'incorrect'
    assert grade_submission(num_item, num_rubric, 'Infinity').outcome == 'incorrect'

    # numeric.v1 with unit check
    unit_rubric = json.loads(json.dumps(num_rubric))
    unit_rubric['config']['unit'] = 'cm'
    unit_rubric['config']['tolerance'] = '0.5'
    assert grade_submission(num_item, unit_rubric, '7.4', submitted_unit='cm').outcome == 'correct'
    assert grade_submission(num_item, unit_rubric, '7.4', submitted_unit='m').reason_code == 'numeric_unit_mismatch'
    assert grade_submission(num_item, unit_rubric, '8.0', submitted_unit='cm').reason_code == 'numeric_outside_tolerance'

    # human-review.v1 ALWAYS holds for review
    priv_item = _find(bundle, 'item', 'item.language.private')
    priv_rubric = _find(bundle, 'rubric', 'rubric.language.private')
    hr = grade_submission(priv_item, priv_rubric, 'Ich lerne Deutsch.')
    assert hr.outcome == 'pending_review'
    assert hr.needs_human_review is True
    assert hr.reason_code == 'human_review_required'

    # Model proposal or uncertain input ALWAYS holds for review
    held_model = grade_submission(num_item, num_rubric, '7', model_proposal={'outcome': 'correct', 'confidence': 0.99})
    assert held_model.outcome == 'pending_review'
    assert held_model.reason_code == 'model_proposal_held'

    held_uncertain = grade_submission(num_item, num_rubric, '7', uncertain=True)
    assert held_uncertain.outcome == 'pending_review'
    assert held_uncertain.reason_code == 'ambiguous_submission'


# --- 2. Ledger negative authorization, learner isolation, and anti-gaming invariants ---


@pytest.mark.parametrize('flag', [
    'actor_active',
    'member_active',
    'tenant_matches',
    'learner_active',
    'relationship_valid',
    'consent_valid',
    'enrollment_valid',
    'entitlement_valid',
    'course_active',
    'edition_active',
])
def test_ledger_projection_denies_when_any_policy_flag_is_false(flag):
    with pytest.raises(LedgerError, match='^access_denied$'):
        project_objective_mastery(
            [],
            scope=_scope(**{flag: False}),
            objective_id='objective.quantitative',
            objective_version=1,
        )


def test_hints_revealed_answers_models_and_pending_cannot_be_independent():
    with pytest.raises(LedgerError, match='^invalid_event$'):
        validate_event(_attempt('ev.hint', hints_used=1, evidence_class='independent'))
    with pytest.raises(LedgerError, match='^invalid_event$'):
        validate_event(_attempt('ev.rev', answer_revealed=True, evidence_class='independent'))
    with pytest.raises(LedgerError, match='^invalid_event$'):
        validate_event(_attempt('ev.model', actor_role='model'))
    with pytest.raises(LedgerError, match='^invalid_event$'):
        validate_event(_attempt('ev.pend', outcome='pending_review', evidence_class='independent'))
    with pytest.raises(LedgerError, match='^invalid_correction$'):
        validate_event(_correction('ev.badc', 'ev.a', actor_role='learner'))
    with pytest.raises(LedgerError, match='^invalid_correction$'):
        validate_event(_correction('ev.badm', 'ev.a', adjudicator_ref='model.gpt'))


def test_unassessed_and_non_independent_evidence_never_raise_mastery():
    # Zero events -> unassessed
    empty = project_objective_mastery([], scope=_scope(), objective_id='objective.quantitative', objective_version=1)
    assert empty.status == 'unassessed'
    assert empty.uncertainty == 'no_evidence'
    assert empty.review_due_at is None
    assert empty.is_calibrated is False

    # Assisted, exposed, ambiguous, external_observation, and other-learner events never promote mastery
    events = [
        _attempt('ev.assisted', item_id='item.q1', family_id='family.a', evidence_class='assisted', hints_used=1),
        _attempt('ev.exposed', item_id='item.q2', family_id='family.b', evidence_class='exposed', answer_revealed=True),
        _attempt('ev.ambig', item_id='item.q3', family_id='family.c', evidence_class='ambiguous', outcome='pending_review'),
        _attempt('ev.ext', item_id='item.q4', family_id='family.d', evidence_class='external_observation', outcome='correct'),
        _attempt('ev.other-learner', learner_id='fixture.learner-b', item_id='item.q5', family_id='family.e'),
        _attempt('ev.other-tenant', tenant_id='fixture.tenant-b', item_id='item.q6', family_id='family.f'),
        # Repeated attempt on previously assisted item.q1 does NOT count as independent success
        _attempt('ev.repeat-q1', day_offset=1, item_id='item.q1', family_id='family.a', evidence_class='independent'),
    ]
    proj = project_objective_mastery(events, scope=_scope(), objective_id='objective.quantitative', objective_version=1)
    assert proj.status == 'unassessed'
    assert proj.independent_count == 0
    assert proj.independent_correct_families == ()
    assert proj.assisted_count == 1
    assert proj.exposed_count == 2  # ev.exposed + downgraded ev.repeat-q1
    assert proj.ambiguous_count == 1
    assert proj.external_observation_count == 1
    assert proj.uncertainty == 'pending_review'


# --- 3. Mastery progression, delayed retention, later failure, replay, and corrections ---


def test_mastery_progression_delayed_retention_and_later_failure_preserves_success():
    # 1 independent failure -> needs_support
    e1 = _attempt('ev.f1', day_offset=0, item_id='item.q1', family_id='family.a', outcome='incorrect')
    p1 = project_objective_mastery([e1], scope=_scope(), objective_id='objective.quantitative', objective_version=1)
    assert p1.status == 'needs_support'
    assert p1.review_due_at == T0

    # 1 independent success -> developing
    e2 = _attempt('ev.s1', day_offset=1, item_id='item.q2', family_id='family.a', outcome='correct')
    p2 = project_objective_mastery([e1, e2], scope=_scope(), objective_id='objective.quantitative', objective_version=1)
    assert p2.status == 'developing'
    assert p2.independent_correct_families == ('family.a',)
    assert p2.review_due_at == T0 + timedelta(days=2)  # 1-day expanding interval

    # 2nd independent success on a DISTINCT family -> ready_for_review
    e3 = _attempt('ev.s2', day_offset=2, item_id='item.q3', family_id='family.b', outcome='correct')
    p3 = project_objective_mastery([e1, e2, e3], scope=_scope(), objective_id='objective.quantitative', objective_version=1)
    assert p3.status == 'ready_for_review'
    assert p3.independent_correct_families == ('family.a', 'family.b')
    assert p3.review_due_at == T0 + timedelta(days=5)  # 3-day expanding interval

    # Delayed success on a NEW family after 7 days -> retained
    e4 = _attempt('ev.s3', day_offset=10, item_id='item.q4', family_id='family.c', outcome='correct')
    p4 = project_objective_mastery([e1, e2, e3, e4], scope=_scope(), objective_id='objective.quantitative', objective_version=1)
    assert p4.status == 'retained'
    assert p4.uncertainty == 'low'
    assert p4.independent_correct_families == ('family.a', 'family.b', 'family.c')

    # Later failure marks uncertainty='probe_needed' WITHOUT erasing prior families
    e5 = _attempt('ev.f2', day_offset=12, item_id='item.q5', family_id='family.d', outcome='incorrect')
    p5 = project_objective_mastery([e1, e2, e3, e4, e5], scope=_scope(), objective_id='objective.quantitative', objective_version=1)
    assert p5.status == 'ready_for_review'
    assert p5.uncertainty == 'probe_needed'
    assert p5.independent_correct_families == ('family.a', 'family.b', 'family.c')
    assert p5.review_due_at == T0 + timedelta(days=12)


def test_duplicate_and_out_of_order_replay_is_deterministic_and_rejects_conflicts():
    e1 = _attempt('ev.s1', day_offset=1, item_id='item.q1', family_id='family.a', outcome='correct')
    e2 = _attempt('ev.s2', day_offset=3, item_id='item.q2', family_id='family.b', outcome='correct')
    e3 = _attempt('ev.s3', day_offset=11, item_id='item.q3', family_id='family.c', outcome='correct')

    in_order = project_objective_mastery([e1, e2, e3], scope=_scope(), objective_id='objective.quantitative', objective_version=1)
    shuffled_with_dups = project_objective_mastery(
        [e3, e1, e2, e1, e3],
        scope=_scope(),
        objective_id='objective.quantitative',
        objective_version=1,
    )
    assert in_order == shuffled_with_dups

    # Conflicting duplicate with same event_id fails closed
    conflict = _attempt('ev.s1', day_offset=1, item_id='item.q1', family_id='family.a', outcome='incorrect')
    with pytest.raises(LedgerError, match='^conflicting_duplicate$'):
        project_objective_mastery([e1, conflict], scope=_scope(), objective_id='objective.quantitative', objective_version=1)


def test_appeal_correction_and_item_invalidation_replay_lineage():
    # Ambiguous pending_review attempt upheld by teacher -> becomes developing
    ambig = _attempt('ev.a1', day_offset=0, item_id='item.q1', family_id='family.a', evidence_class='ambiguous', outcome='pending_review')
    corr_upheld = _correction('ev.c1', 'ev.a1', day_offset=1, action='override_outcome', new_outcome='correct', new_evidence_class='independent')
    e2 = _attempt('ev.a2', day_offset=2, item_id='item.q2', family_id='family.b', evidence_class='independent', outcome='correct')

    proj_ready = project_objective_mastery(
        [e2, corr_upheld, ambig],
        scope=_scope(),
        objective_id='objective.quantitative',
        objective_version=1,
    )
    assert proj_ready.status == 'ready_for_review'
    assert proj_ready.independent_correct_families == ('family.a', 'family.b')

    # Invalidating faulty item.q2 via appended correction demotes back to developing without mutating history
    corr_inv = _correction('ev.c2', 'ev.a2', day_offset=3, action='invalidate_item', new_outcome=None, new_evidence_class=None, reason_code='item.defective')
    proj_after_inv = project_objective_mastery(
        [ambig, corr_upheld, e2, corr_inv],
        scope=_scope(),
        objective_id='objective.quantitative',
        objective_version=1,
    )
    assert proj_after_inv.status == 'developing'
    assert proj_after_inv.invalidated_count == 1
    assert proj_after_inv.independent_correct_families == ('family.a',)

    # Teacher cannot reclassify a hinted attempt as independent
    hinted = _attempt('ev.h1', day_offset=0, item_id='item.q3', family_id='family.c', evidence_class='assisted', hints_used=2)
    bad_reclass = _correction('ev.c3', 'ev.h1', day_offset=1, action='reclassify_evidence', new_outcome=None, new_evidence_class='independent')
    with pytest.raises(LedgerError, match='^invalid_correction$'):
        project_objective_mastery([hinted, bad_reclass], scope=_scope(), objective_id='objective.quantitative', objective_version=1)

    # Dangling correction referencing unknown event fails closed
    dangling = _correction('ev.c4', 'ev.missing', day_offset=1, action='invalidate_item', new_outcome=None, new_evidence_class=None)
    with pytest.raises(LedgerError, match='^invalid_correction$'):
        project_objective_mastery([dangling], scope=_scope(), objective_id='objective.quantitative', objective_version=1)
