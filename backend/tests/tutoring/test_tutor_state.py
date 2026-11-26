"""AUTH-020: DB-free deterministic tutoring state-machine tests (DEV-013 sub-slice)."""

from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import pytest

from modules.learning.ledger import LedgerScope, project_objective_mastery
from modules.tutoring.state_machine import (
    MAX_HINTS_PER_ITEM,
    TutorCommand,
    TutorError,
    TutorScope,
    create_session,
    step_session,
)

ROOT = Path(__file__).resolve().parents[3]
T0 = datetime(2026, 11, 26, 12, 0, tzinfo=timezone.utc)


def _approved_bundle():
    bundle = json.loads((ROOT / 'evals/fixtures/curriculum-v1.json').read_text(encoding='utf-8'))
    for rec in bundle['records']:
        rec['status'] = 'approved'
        rec['reviewer_ref'] = 'reviewer.fixture'
    return bundle


def _find(bundle, kind, rec_id, version=1):
    return next(r for r in bundle['records'] if r['kind'] == kind and r['id'] == rec_id and r['version'] == version)


def _scope(**overrides) -> TutorScope:
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
    return TutorScope(**base)


def _teacher_scope(**overrides) -> TutorScope:
    base = dict(role='teacher', purpose='teacher_reporting')
    base.update(overrides)
    return _scope(**base)


def _ledger_scope(scope: TutorScope) -> LedgerScope:
    return LedgerScope(
        tenant_id=scope.tenant_id,
        learner_id=scope.learner_id,
        edition_id=scope.edition_id,
        edition_version=scope.edition_version,
        role=scope.role,
        purpose=scope.purpose,
        actor_active=scope.actor_active,
        member_active=scope.member_active,
        tenant_matches=scope.tenant_matches,
        learner_active=scope.learner_active,
        relationship_valid=scope.relationship_valid,
        consent_valid=scope.consent_valid,
        enrollment_valid=scope.enrollment_valid,
        entitlement_valid=scope.entitlement_valid,
        course_active=scope.course_active,
        edition_active=scope.edition_active,
    )


def _cmd(session, key, action, *, turn_id=None, sec=0, actor_role='learner', **kwargs) -> TutorCommand:
    ts = T0 + timedelta(seconds=sec)
    return TutorCommand(
        command_key=key,
        session_id=session.session_id,
        turn_id=turn_id or f'turn.{key}',
        expected_state=session.state,
        expected_turn_seq=session.turn_seq,
        action=action,
        actor_role=actor_role,
        occurred_at=ts,
        recorded_at=ts + timedelta(seconds=1),
        **kwargs,
    )


# --- 1. Negative security, scope revocation, actor-role binding, and turn/item guards ---


def test_revoked_consent_blocks_and_resume_returns_via_access_check():
    bundle = _approved_bundle()
    item = _find(bundle, 'item', 'item.quantitative')
    rubric = _find(bundle, 'rubric', 'rubric.quantitative')
    scope = _scope()

    s = create_session(session_id='sess.one', scope=scope, objective_id='objective.quantitative', objective_version=1)
    s = step_session(s, _cmd(s, 'cmd.a1', 'check_access', sec=1), scope=scope).session
    s = step_session(s, _cmd(s, 'cmd.p1', 'start_practice', sec=2, item=item), scope=scope).session

    # Consent revoked before answer submission -> transitions cleanly to blocked, emits zero evidence
    revoked = _scope(consent_valid=False)
    res = step_session(
        s,
        _cmd(s, 'cmd.sub1', 'submit_answer', sec=3, item=item, rubric=rubric, submission='7'),
        scope=revoked,
    )
    assert res.session.state == 'blocked'
    assert res.session.emitted_events == ()
    assert res.grade_decision is None

    # Cannot resume while consent is still revoked
    with pytest.raises(TutorError, match='^access_denied$'):
        step_session(res.session, _cmd(res.session, 'cmd.res-bad', 'resume_session', sec=4), scope=revoked)

    # Restored consent resumes cleanly via access_check -> select
    s_ac = step_session(res.session, _cmd(res.session, 'cmd.res-ok', 'resume_session', sec=5), scope=scope).session
    assert s_ac.state == 'access_check'
    s_sel = step_session(s_ac, _cmd(s_ac, 'cmd.a2', 'check_access', sec=6), scope=scope).session
    assert s_sel.state == 'select'


def test_model_actor_role_spoofing_cross_learner_and_stale_or_cancelled_turns_fail_closed():
    bundle = _approved_bundle()
    item = _find(bundle, 'item', 'item.quantitative')
    rubric = _find(bundle, 'rubric', 'rubric.quantitative')
    scope = _scope()

    s = create_session(session_id='sess.guard', scope=scope, objective_id='objective.quantitative', objective_version=1)

    # Model actor or mismatched command.actor_role != scope.role rejected
    with pytest.raises(TutorError, match='^invalid_actor$'):
        step_session(s, _cmd(s, 'cmd.m1', 'check_access', actor_role='model'), scope=scope)
    with pytest.raises(TutorError, match='^invalid_actor$'):
        step_session(s, _cmd(s, 'cmd.spoof', 'check_access', actor_role='teacher'), scope=scope)

    # Cross-learner scope mismatch rejected
    with pytest.raises(TutorError, match='^scope_mismatch$'):
        step_session(s, _cmd(s, 'cmd.x1', 'check_access'), scope=_scope(learner_id='fixture.learner-b'))

    # Wrong session_id rejected
    bad_sess_cmd = TutorCommand(
        command_key='cmd.ws',
        session_id='sess.other',
        turn_id='turn.ws',
        expected_state='access_check',
        expected_turn_seq=0,
        action='check_access',
        actor_role='learner',
        occurred_at=T0,
        recorded_at=T0,
    )
    with pytest.raises(TutorError, match='^session_mismatch$'):
        step_session(s, bad_sess_cmd, scope=scope)

    # Empty string target_state fails closed instead of falling back
    with pytest.raises(TutorError, match='^illegal_transition$'):
        step_session(s, _cmd(s, 'cmd.empty-t', 'check_access', target_state=''), scope=scope)

    s = step_session(s, _cmd(s, 'cmd.a1', 'check_access', sec=1), scope=scope).session

    # check_access is ONLY allowed from access_check
    with pytest.raises(TutorError, match='^illegal_transition$'):
        step_session(s, _cmd(s, 'cmd.jump', 'check_access', sec=2), scope=scope)

    # Out-of-edition / out-of-objective / cross-learner private / draft items rejected on start_practice
    other_item = _find(bundle, 'item', 'item.science')
    with pytest.raises(TutorError, match='^item_out_of_scope$'):
        step_session(s, _cmd(s, 'cmd.bad-ed', 'start_practice', sec=2, item=other_item), scope=scope)
    priv_other_item = _find(bundle, 'item', 'item.language.private')
    with pytest.raises(TutorError, match='^item_out_of_scope$'):
        step_session(s, _cmd(s, 'cmd.bad-priv', 'start_practice', sec=2, item=priv_other_item), scope=scope)
    draft_item = dict(item, status='draft')
    with pytest.raises(TutorError, match='^invalid_item$'):
        step_session(s, _cmd(s, 'cmd.bad-draft', 'start_practice', sec=2, item=draft_item), scope=scope)

    s = step_session(s, _cmd(s, 'cmd.p1', 'start_practice', sec=2, item=item), scope=scope).session

    # Wrong item_id cannot score active practice item
    other_rubric = _find(bundle, 'rubric', 'rubric.science')
    with pytest.raises(TutorError, match='^item_out_of_scope$'):
        step_session(
            s,
            _cmd(s, 'cmd.wi', 'submit_answer', sec=3, item=other_item, rubric=other_rubric, submission='physical'),
            scope=scope,
        )

    # Stale expected_turn_seq fails closed
    stale_cmd = TutorCommand(
        command_key='cmd.stale',
        session_id=s.session_id,
        turn_id='turn.stale',
        expected_state=s.state,
        expected_turn_seq=0,
        action='request_hint',
        actor_role='learner',
        occurred_at=T0 + timedelta(seconds=4),
        recorded_at=T0 + timedelta(seconds=5),
    )
    with pytest.raises(TutorError, match='^stale_turn$'):
        step_session(s, stale_cmd, scope=scope)

    # Pause records cancelled turn_id; late submission with that turn_id is rejected; resume works
    s_paused = step_session(s, _cmd(s, 'cmd.pause', 'pause_session', turn_id='turn.inflight', sec=5), scope=scope).session
    assert s_paused.state == 'paused'
    with pytest.raises(TutorError, match='^turn_cancelled$'):
        step_session(s_paused, _cmd(s_paused, 'cmd.late', 'resume_session', turn_id='turn.inflight', sec=6), scope=scope)
    s_resumed = step_session(s_paused, _cmd(s_paused, 'cmd.res', 'resume_session', sec=7), scope=scope).session
    assert s_resumed.state == 'access_check'

    # Cancel turn transitions to cancelled and can resume cleanly via access_check
    s_canc = step_session(s_resumed, _cmd(s_resumed, 'cmd.canc', 'cancel_turn', turn_id='turn.c1', sec=8), scope=scope).session
    assert s_canc.state == 'cancelled'
    s_canc_res = step_session(s_canc, _cmd(s_canc, 'cmd.canc-res', 'resume_session', sec=9), scope=scope).session
    assert s_canc_res.state == 'access_check'


def test_idempotent_command_replay_rechecks_live_scope_and_rejects_conflicts():
    scope = _scope()
    s0 = create_session(session_id='sess.idem', scope=scope, objective_id='objective.quantitative', objective_version=1)
    c1 = _cmd(s0, 'cmd.first', 'check_access', sec=1)
    r1 = step_session(s0, c1, scope=scope)
    assert r1.replayed is False
    assert r1.session.state == 'select'

    # Replaying exact same command_key returns replayed=True when live scope holds
    r1_dup = step_session(r1.session, c1, scope=scope)
    assert r1_dup.replayed is True
    assert r1_dup.session == r1.session

    # Replaying when live consent was revoked fails closed
    with pytest.raises(TutorError, match='^access_denied$'):
        step_session(r1.session, c1, scope=_scope(consent_valid=False))

    # Conflicting payload with same command_key fails closed
    c1_conflict = TutorCommand(
        command_key='cmd.first',
        session_id=s0.session_id,
        turn_id='turn.other',
        expected_state='access_check',
        expected_turn_seq=0,
        action='check_access',
        actor_role='learner',
        occurred_at=T0 + timedelta(seconds=1),
        recorded_at=T0 + timedelta(seconds=2),
        target_state='diagnose',
    )
    with pytest.raises(TutorError, match='^conflicting_command$'):
        step_session(r1.session, c1_conflict, scope=scope)


def test_safety_pause_requires_human_owner_and_server_teacher_scope_to_resume():
    scope = _scope()
    s = create_session(session_id='sess.safe', scope=scope, objective_id='objective.quantitative', objective_version=1)
    s = step_session(s, _cmd(s, 'cmd.a1', 'check_access', sec=1), scope=scope).session

    # Model ref rejected as safety escalation owner
    with pytest.raises(TutorError, match='^invalid_safety_owner$'):
        step_session(s, _cmd(s, 'cmd.sp-bad', 'trigger_safety_pause', sec=2, reviewer_ref='ai.bot'), scope=scope)

    # Human owner succeeds even if consent later drops
    s = step_session(
        s,
        _cmd(s, 'cmd.sp1', 'trigger_safety_pause', sec=2, reviewer_ref='reviewer.safety-lead'),
        scope=_scope(consent_valid=False),
    ).session
    assert s.state == 'safety_pause'
    assert s.safety_owner_ref == 'reviewer.safety-lead'

    # Learner scope cannot self-resume even if claiming actor_role='teacher' or 'learner'
    with pytest.raises(TutorError, match='^safety_resume_denied$'):
        step_session(s, _cmd(s, 'cmd.res-bad1', 'resume_from_safety', sec=3, actor_role='learner', reviewer_ref='teacher.amina'), scope=scope)
    with pytest.raises(TutorError, match='^invalid_actor$'):
        step_session(s, _cmd(s, 'cmd.res-bad2', 'resume_from_safety', sec=3, actor_role='teacher', reviewer_ref='teacher.amina'), scope=scope)

    # Server-derived teacher scope with human ref resumes cleanly
    s = step_session(
        s,
        _cmd(s, 'cmd.res-ok', 'resume_from_safety', sec=4, actor_role='teacher', reviewer_ref='teacher.safety-lead', target_state='select'),
        scope=_teacher_scope(),
    ).session
    assert s.state == 'select'


# --- 2. Hint ladder, reveal anti-gaming, diagnose, guided/prerequisite, and E2E ledger ---


def test_hint_and_reveal_anti_gaming_cannot_reset_to_independent_mastery():
    bundle = _approved_bundle()
    item = _find(bundle, 'item', 'item.quantitative')
    rubric = _find(bundle, 'rubric', 'rubric.quantitative')
    scope = _scope()

    s = create_session(session_id='sess.hint', scope=scope, objective_id='objective.quantitative', objective_version=1)
    s = step_session(s, _cmd(s, 'cmd.a1', 'check_access', sec=1), scope=scope).session
    # Entering guided without an active item cannot request hint or reveal answer
    s_ex = step_session(s, _cmd(s, 'cmd.ex', 'select_explain', sec=2, query='تساوي الطرفين'), scope=scope, bundle=bundle).session
    s_gd = step_session(s_ex, _cmd(s_ex, 'cmd.gd', 'start_guided', sec=3), scope=scope).session
    with pytest.raises(TutorError, match='^no_active_item$'):
        step_session(s_gd, _cmd(s_gd, 'cmd.h-none', 'request_hint', sec=4), scope=scope)
    with pytest.raises(TutorError, match='^no_active_item$'):
        step_session(s_gd, _cmd(s_gd, 'cmd.r-none', 'reveal_worked_answer', sec=4), scope=scope)

    # Prerequisite detour works cleanly
    s_pre = step_session(s_gd, _cmd(s_gd, 'cmd.pre', 'start_prerequisite', sec=5), scope=scope).session
    assert s_pre.state == 'prerequisite'

    s = step_session(s_pre, _cmd(s_pre, 'cmd.p1', 'start_practice', sec=6, item=item), scope=scope).session

    # Cannot reveal worked answer directly in independent practice
    with pytest.raises(TutorError, match='^illegal_transition$'):
        step_session(s, _cmd(s, 'cmd.rev-bad', 'reveal_worked_answer', sec=7), scope=scope)

    # Request up to MAX_HINTS_PER_ITEM hints; 4th hint rejected
    for i in range(MAX_HINTS_PER_ITEM):
        s = step_session(s, _cmd(s, f'cmd.h{i}', 'request_hint', sec=8 + i), scope=scope).session
        assert s.state == 'guided'
        assert s.active_attempt_hints == i + 1

    with pytest.raises(TutorError, match='^hint_limit_reached$'):
        step_session(s, _cmd(s, 'cmd.h-over', 'request_hint', sec=12), scope=scope)

    # Reveal worked answer in guided mode
    s = step_session(s, _cmd(s, 'cmd.rev-ok', 'reveal_worked_answer', sec=13), scope=scope).session
    assert s.active_answer_revealed is True

    # Anti-gaming: restarting practice on the SAME exposed item cannot earn 'independent' evidence!
    s_retry = step_session(s, _cmd(s, 'cmd.p2', 'start_practice', sec=14, item=item), scope=scope).session
    res = step_session(
        s_retry,
        _cmd(s_retry, 'cmd.sub', 'submit_answer', sec=15, item=item, rubric=rubric, submission='7'),
        scope=scope,
    )
    assert res.session.state == 'reflect'
    assert res.emitted_event.evidence_class == 'exposed'

    proj = project_objective_mastery(
        res.session.emitted_events,
        scope=_ledger_scope(scope),
        objective_id='objective.quantitative',
        objective_version=1,
    )
    assert proj.status == 'unassessed'
    assert proj.exposed_count == 1
    assert proj.independent_count == 0


def test_diagnose_grounded_explain_abstention_and_independent_practice_end_to_end():
    bundle = _approved_bundle()
    item = _find(bundle, 'item', 'item.quantitative')
    rubric = _find(bundle, 'rubric', 'rubric.quantitative')
    scope = _scope()

    # Diagnostic entry -> submit diagnostic answer -> select
    s_diag = create_session(session_id='sess.diag', scope=scope, objective_id='objective.quantitative', objective_version=1)
    s_diag = step_session(s_diag, _cmd(s_diag, 'cmd.d1', 'check_access', sec=1, target_state='diagnose', item=item), scope=scope).session
    assert s_diag.state == 'diagnose'
    r_diag = step_session(s_diag, _cmd(s_diag, 'cmd.d2', 'submit_answer', sec=2, item=item, rubric=rubric, submission='5'), scope=scope)
    assert r_diag.session.state == 'select'
    assert r_diag.emitted_event.evidence_class == 'independent'
    assert r_diag.emitted_event.outcome == 'incorrect'

    # Fresh session for explain -> practice -> reflect -> schedule -> done
    s = create_session(session_id='sess.e2e', scope=scope, objective_id='objective.quantitative', objective_version=1)
    s = step_session(s, _cmd(s, 'cmd.a1', 'check_access', sec=1), scope=scope).session

    # Off-topic query abstains honestly with zero citations
    r_abs = step_session(s, _cmd(s, 'cmd.ex-abs', 'select_explain', sec=2, query='فيزياء الكم'), scope=scope, bundle=bundle)
    assert r_abs.session.state == 'explain'
    assert r_abs.session.last_grounded is False
    assert r_abs.session.last_citations == ()
    assert r_abs.abstention_reason == 'no_authorized_evidence'

    # In-scope query returns verified citations
    r_gnd = step_session(r_abs.session, _cmd(r_abs.session, 'cmd.ex-ok', 'select_explain', sec=3, query='تساوي الطرفين'), scope=scope, bundle=bundle)
    assert r_gnd.session.last_grounded is True
    assert len(r_gnd.session.last_citations) == 1
    assert r_gnd.session.last_citations[0].material_id == 'material.quantitative'

    # Independent practice -> deterministic grade -> reflect -> schedule -> done
    s = step_session(r_gnd.session, _cmd(r_gnd.session, 'cmd.p1', 'start_practice', sec=4, item=item), scope=scope).session
    r_sub = step_session(s, _cmd(s, 'cmd.sub1', 'submit_answer', sec=5, item=item, rubric=rubric, submission='٧'), scope=scope)
    assert r_sub.session.state == 'reflect'
    assert r_sub.grade_decision.outcome == 'correct'
    assert r_sub.emitted_event.evidence_class == 'independent'

    s = step_session(r_sub.session, _cmd(r_sub.session, 'cmd.ref', 'reflect_next', sec=6, target_state='schedule'), scope=scope).session
    s = step_session(s, _cmd(s, 'cmd.fin', 'finish_session', sec=7), scope=scope).session
    assert s.state == 'done'

    # Emitted independent evidence advances ledger cleanly to developing
    proj = project_objective_mastery(
        s.emitted_events,
        scope=_ledger_scope(scope),
        objective_id='objective.quantitative',
        objective_version=1,
    )
    assert proj.status == 'developing'
    assert proj.independent_count == 1
    assert proj.independent_correct_families == (item['family_id'],)


def test_model_proposed_submission_routes_to_review_pending_and_requires_teacher_adjudication():
    bundle = _approved_bundle()
    item = _find(bundle, 'item', 'item.quantitative')
    rubric = _find(bundle, 'rubric', 'rubric.quantitative')
    scope = _scope()

    s = create_session(session_id='sess.rev', scope=scope, objective_id='objective.quantitative', objective_version=1)
    s = step_session(s, _cmd(s, 'cmd.a1', 'check_access', sec=1), scope=scope).session
    s = step_session(s, _cmd(s, 'cmd.p1', 'start_practice', sec=2, item=item), scope=scope).session

    res = step_session(
        s,
        _cmd(s, 'cmd.sub', 'submit_answer', sec=3, item=item, rubric=rubric, submission='7', model_proposal={'outcome': 'correct'}),
        scope=scope,
    )
    assert res.session.state == 'review_pending'
    assert res.grade_decision.outcome == 'pending_review'
    assert res.emitted_event.evidence_class == 'ambiguous'

    # Learner cannot escape review_pending via check_access or adjudicate_review
    with pytest.raises(TutorError, match='^illegal_transition$'):
        step_session(res.session, _cmd(res.session, 'cmd.esc1', 'check_access', sec=4), scope=scope)
    with pytest.raises(TutorError, match='^adjudication_denied$'):
        step_session(res.session, _cmd(res.session, 'cmd.esc2', 'adjudicate_review', sec=4, reviewer_ref='teacher.amina'), scope=scope)

    # Server-derived teacher scope adjudicates cleanly
    s_done_rev = step_session(
        res.session,
        _cmd(res.session, 'cmd.adj', 'adjudicate_review', sec=5, actor_role='teacher', reviewer_ref='teacher.amina', target_state='select'),
        scope=_teacher_scope(),
    ).session
    assert s_done_rev.state == 'select'

    proj = project_objective_mastery(
        res.session.emitted_events,
        scope=_ledger_scope(scope),
        objective_id='objective.quantitative',
        objective_version=1,
    )
    assert proj.status == 'unassessed'
    assert proj.ambiguous_count == 1
