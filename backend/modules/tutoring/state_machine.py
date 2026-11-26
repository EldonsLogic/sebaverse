"""AUTH-020: pure DB-free deterministic tutoring state machine.

Enforces allowed state transitions, live server-derived access/consent checks,
bounded hint ladders that end independence immediately, stale/cancelled-turn and
wrong-item guards, idempotent command replay, human-only resume from safety_pause,
and integration with DB-free retrieval, grading, and learning-evidence modules.
No database, HTTP/SSE, AG-UI SDK, or model calls occur here.
"""

from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from hashlib import sha256
import json
import re

from modules.access import policy
from modules.assessment.grader import AssessmentError, GradeDecision, grade_submission
from modules.learning.ledger import EvidenceEvent
from modules.retrieval.preflight import CitationRef, RetrievalError, RetrievalScope, retrieve_scoped


POLICY_VERSION = 'tutor.state-preflight-v1'
MAX_HINTS_PER_ITEM = 3
STATES = frozenset({
    'access_check',
    'diagnose',
    'select',
    'explain',
    'guided',
    'prerequisite',
    'practice',
    'grade',
    'reflect',
    'schedule',
    'review_pending',
    'safety_pause',
    'paused',
    'cancelled',
    'blocked',
    'done',
})
ALLOWED_TRANSITIONS: dict[str, frozenset[str]] = {
    'access_check': frozenset({'diagnose', 'select', 'blocked', 'safety_pause', 'paused', 'cancelled'}),
    'diagnose': frozenset({'select', 'review_pending', 'blocked', 'safety_pause', 'paused', 'cancelled'}),
    'select': frozenset({'explain', 'practice', 'review_pending', 'blocked', 'safety_pause', 'paused', 'cancelled'}),
    'explain': frozenset({'guided', 'practice', 'explain', 'blocked', 'safety_pause', 'paused', 'cancelled'}),
    'guided': frozenset({'guided', 'prerequisite', 'practice', 'blocked', 'safety_pause', 'paused', 'cancelled'}),
    'prerequisite': frozenset({'guided', 'practice', 'review_pending', 'blocked', 'safety_pause', 'paused', 'cancelled'}),
    'practice': frozenset({'grade', 'guided', 'blocked', 'safety_pause', 'paused', 'cancelled'}),
    'grade': frozenset({'reflect', 'review_pending', 'blocked', 'safety_pause', 'paused', 'cancelled'}),
    'reflect': frozenset({'select', 'schedule', 'review_pending', 'blocked', 'safety_pause', 'paused', 'cancelled'}),
    'schedule': frozenset({'done', 'blocked', 'safety_pause', 'paused', 'cancelled'}),
    'review_pending': frozenset({'grade', 'select', 'schedule', 'blocked', 'safety_pause', 'paused', 'cancelled'}),
    'safety_pause': frozenset({'select', 'done', 'cancelled'}),
    'paused': frozenset({'access_check', 'cancelled'}),
    'blocked': frozenset({'access_check', 'cancelled'}),
    'cancelled': frozenset(),
    'done': frozenset(),
}
ALLOWED_ACTORS = frozenset({'learner', 'guardian', 'teacher', 'reviewer', 'system'})
HUMAN_SAFETY_REVIEWERS = frozenset({'teacher', 'reviewer'})
_FORBIDDEN_MODEL_TOKENS = frozenset({'model', 'llm', 'ai'})
_IDENTIFIER = re.compile(r'[a-z][a-z0-9._-]{1,95}')


class TutorError(ValueError):
    """Fail-closed tutoring state-machine error with fixed code and zero leaked data."""


@dataclass(frozen=True)
class TutorScope:
    """Live server-derived authorization and curriculum scope for one session."""
    tenant_id: str
    learner_id: str
    edition_id: str
    edition_version: int
    role: str
    purpose: str
    actor_active: bool
    member_active: bool
    tenant_matches: bool
    learner_active: bool
    relationship_valid: bool
    consent_valid: bool
    enrollment_valid: bool
    entitlement_valid: bool
    course_active: bool
    edition_active: bool

    def to_access_scope(self) -> policy.Scope:
        return policy.Scope(
            actor_active=self.actor_active,
            member_active=self.member_active,
            role=self.role,
            tenant_matches=self.tenant_matches,
            learner_active=self.learner_active,
            relationship_valid=self.relationship_valid,
            consent_valid=self.consent_valid,
            enrollment_valid=self.enrollment_valid,
            entitlement_valid=self.entitlement_valid,
            course_active=self.course_active,
            edition_active=self.edition_active,
            resource_active=True,
            version_matches=True,
            purpose=self.purpose,
            kind='course',
        )

    def to_retrieval_scope(self) -> RetrievalScope:
        return RetrievalScope(
            tenant_id=self.tenant_id,
            learner_id=self.learner_id,
            edition_id=self.edition_id,
            edition_version=self.edition_version,
            role=self.role,
            purpose=self.purpose,
            actor_active=self.actor_active,
            member_active=self.member_active,
            tenant_matches=self.tenant_matches,
            learner_active=self.learner_active,
            relationship_valid=self.relationship_valid,
            consent_valid=self.consent_valid,
            enrollment_valid=self.enrollment_valid,
            entitlement_valid=self.entitlement_valid,
            course_active=self.course_active,
            edition_active=self.edition_active,
        )


@dataclass(frozen=True)
class TutorSession:
    """Immutable deterministic tutoring session checkpoint."""
    session_id: str
    tenant_id: str
    learner_id: str
    edition_id: str
    edition_version: int
    objective_id: str
    objective_version: int
    state: str = 'access_check'
    turn_seq: int = 0
    active_item_id: str | None = None
    active_item_version: int | None = None
    active_family_id: str | None = None
    active_attempt_hints: int = 0
    active_answer_revealed: bool = False
    cancelled_turn_ids: frozenset[str] = field(default_factory=frozenset)
    command_digests: tuple[tuple[str, str], ...] = ()
    emitted_events: tuple[EvidenceEvent, ...] = ()
    last_reason_code: str = 'session_initialized'
    last_citations: tuple[CitationRef, ...] = ()
    last_grounded: bool | None = None
    safety_owner_ref: str | None = None
    policy_version: str = field(default=POLICY_VERSION, init=False)


@dataclass(frozen=True)
class TutorCommand:
    """Validated command driving one deterministic state transition."""
    command_key: str
    session_id: str
    turn_id: str
    expected_state: str
    expected_turn_seq: int
    action: str
    actor_role: str
    occurred_at: datetime
    recorded_at: datetime
    # Action-specific optional fields
    query: str | None = None
    item: dict | None = None
    rubric: dict | None = None
    submission: str | None = None
    submitted_unit: str | None = None
    uncertain: bool = False
    model_proposal: dict | None = None
    target_state: str | None = None
    reviewer_ref: str | None = None
    reason_code: str | None = None


@dataclass(frozen=True)
class TutorStepResult:
    """Deterministic outcome of applying one TutorCommand to a TutorSession."""
    session: TutorSession
    replayed: bool
    grade_decision: GradeDecision | None = None
    emitted_event: EvidenceEvent | None = None
    abstention_reason: str | None = None


def _check_id(value: object, *, code: str = 'invalid_command') -> str:
    if type(value) is not str or not _IDENTIFIER.fullmatch(value):
        raise TutorError(code)
    return value


def _check_pos_int(value: object, *, code: str = 'invalid_command') -> int:
    if type(value) is not int or value < 1:
        raise TutorError(code)
    return value


def _to_utc(dt: datetime, *, code: str = 'invalid_time') -> datetime:
    try:
        if type(dt) is not datetime or dt.utcoffset() is None:
            raise ValueError
        return dt.astimezone(timezone.utc)
    except (ValueError, OverflowError, TypeError):
        raise TutorError(code) from None


def _validate_scope_structure(scope: TutorScope) -> None:
    if not isinstance(scope, TutorScope):
        raise TutorError('invalid_scope')
    for val in (scope.tenant_id, scope.learner_id, scope.edition_id):
        _check_id(val, code='invalid_scope')
    _check_pos_int(scope.edition_version, code='invalid_scope')
    if type(scope.role) is not str or type(scope.purpose) is not str:
        raise TutorError('invalid_scope')


def _is_human_ref(ref: object) -> bool:
    if type(ref) is not str or not _IDENTIFIER.fullmatch(ref):
        return False
    return re.split(r'[._-]', ref, maxsplit=1)[0] not in _FORBIDDEN_MODEL_TOKENS


def _command_digest(cmd: TutorCommand, occurred: datetime, recorded: datetime) -> str:
    payload = {
        'command_key': cmd.command_key,
        'session_id': cmd.session_id,
        'turn_id': cmd.turn_id,
        'expected_state': cmd.expected_state,
        'expected_turn_seq': cmd.expected_turn_seq,
        'action': cmd.action,
        'actor_role': cmd.actor_role,
        'occurred_at': occurred.isoformat(),
        'recorded_at': recorded.isoformat(),
        'query': cmd.query,
        'item_id': cmd.item.get('id') if isinstance(cmd.item, dict) else None,
        'item_version': cmd.item.get('version') if isinstance(cmd.item, dict) else None,
        'rubric_id': cmd.rubric.get('id') if isinstance(cmd.rubric, dict) else None,
        'rubric_version': cmd.rubric.get('version') if isinstance(cmd.rubric, dict) else None,
        'submission': cmd.submission,
        'submitted_unit': cmd.submitted_unit,
        'uncertain': cmd.uncertain,
        'has_model_proposal': cmd.model_proposal is not None,
        'target_state': cmd.target_state,
        'reviewer_ref': cmd.reviewer_ref,
        'reason_code': cmd.reason_code,
    }
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
    return sha256(raw).hexdigest()


def _assert_transition(current: str, target: str) -> None:
    if target not in ALLOWED_TRANSITIONS.get(current, frozenset()):
        raise TutorError('illegal_transition')


def create_session(
    *,
    session_id: str,
    scope: TutorScope,
    objective_id: str,
    objective_version: int,
) -> TutorSession:
    """Create a new tutoring session starting at access_check."""
    _check_id(session_id, code='invalid_session')
    _validate_scope_structure(scope)
    _check_id(objective_id, code='invalid_session')
    _check_pos_int(objective_version, code='invalid_session')
    return TutorSession(
        session_id=session_id,
        tenant_id=scope.tenant_id,
        learner_id=scope.learner_id,
        edition_id=scope.edition_id,
        edition_version=scope.edition_version,
        objective_id=objective_id,
        objective_version=objective_version,
    )


def step_session(
    session: TutorSession,
    command: TutorCommand,
    *,
    scope: TutorScope,
    bundle: dict | None = None,
) -> TutorStepResult:
    """Apply one deterministic tutoring command with live scope and turn guards."""
    if not isinstance(session, TutorSession) or session.state not in STATES:
        raise TutorError('invalid_session')
    if not isinstance(command, TutorCommand):
        raise TutorError('invalid_command')
    _validate_scope_structure(scope)

    _check_id(command.command_key)
    _check_id(command.session_id)
    _check_id(command.turn_id)
    if type(command.expected_state) is not str or command.expected_state not in STATES:
        raise TutorError('invalid_command')
    if type(command.expected_turn_seq) is not int or command.expected_turn_seq < 0:
        raise TutorError('invalid_command')
    if type(command.actor_role) is not str or command.actor_role == 'model' or command.actor_role not in ALLOWED_ACTORS:
        raise TutorError('invalid_actor')

    occurred = _to_utc(command.occurred_at)
    recorded = _to_utc(command.recorded_at)
    if recorded < occurred:
        raise TutorError('invalid_time')

    # Session & scope binding check (never cross-learner, cross-tenant, or cross-edition).
    if command.session_id != session.session_id:
        raise TutorError('session_mismatch')
    if (
        scope.tenant_id != session.tenant_id
        or scope.learner_id != session.learner_id
        or scope.edition_id != session.edition_id
        or scope.edition_version != session.edition_version
    ):
        raise TutorError('scope_mismatch')

    # Idempotent command replay check BEFORE sequence/state rejection.
    digest = _command_digest(command, occurred, recorded)
    prior_map = dict(session.command_digests)
    if command.command_key in prior_map:
        if prior_map[command.command_key] != digest:
            raise TutorError('conflicting_command')
        return TutorStepResult(session=session, replayed=True)

    # Cancelled turn or stale sequence/state check.
    if command.turn_id in session.cancelled_turn_ids:
        raise TutorError('turn_cancelled')
    if command.expected_state != session.state or command.expected_turn_seq != session.turn_seq:
        raise TutorError('stale_turn')

    new_digests = session.command_digests + ((command.command_key, digest),)
    next_seq = session.turn_seq + 1
    action = command.action

    # Safety pause and turn cancellation always fail safe even if live scope dropped.
    if action == 'trigger_safety_pause':
        _assert_transition(session.state, 'safety_pause')
        if not _is_human_ref(command.reviewer_ref):
            raise TutorError('invalid_safety_owner')
        reason = _check_id(command.reason_code or 'safety.escalation')
        updated = replace(
            session,
            state='safety_pause',
            turn_seq=next_seq,
            command_digests=new_digests,
            safety_owner_ref=command.reviewer_ref,
            last_reason_code=reason,
        )
        return TutorStepResult(session=updated, replayed=False)

    if action == 'cancel_turn':
        _assert_transition(session.state, 'cancelled')
        updated = replace(
            session,
            state='cancelled',
            turn_seq=next_seq,
            cancelled_turn_ids=session.cancelled_turn_ids | {command.turn_id},
            command_digests=new_digests,
            last_reason_code='turn_cancelled',
        )
        return TutorStepResult(session=updated, replayed=False)

    if action == 'resume_from_safety':
        if session.state != 'safety_pause':
            raise TutorError('illegal_transition')
        if command.actor_role not in HUMAN_SAFETY_REVIEWERS or not _is_human_ref(command.reviewer_ref):
            raise TutorError('safety_resume_denied')
        target = command.target_state or 'select'
        _assert_transition('safety_pause', target)
        if not policy.allowed(scope.to_access_scope()):
            raise TutorError('access_denied')
        updated = replace(
            session,
            state=target,
            turn_seq=next_seq,
            command_digests=new_digests,
            last_reason_code='safety_approved_resume',
        )
        return TutorStepResult(session=updated, replayed=False)

    # Live server-derived access/consent check on every normal tutoring action.
    if not policy.allowed(scope.to_access_scope()):
        if 'blocked' in ALLOWED_TRANSITIONS.get(session.state, frozenset()):
            blocked_session = replace(
                session,
                state='blocked',
                turn_seq=next_seq,
                command_digests=new_digests,
                last_reason_code='scope_revoked',
            )
            return TutorStepResult(session=blocked_session, replayed=False)
        raise TutorError('access_denied')

    if action == 'check_access':
        target = command.target_state or 'select'
        if target not in ('select', 'diagnose'):
            raise TutorError('illegal_transition')
        _assert_transition(session.state, target)
        updated = replace(
            session,
            state=target,
            turn_seq=next_seq,
            command_digests=new_digests,
            last_reason_code='access_verified',
        )
        return TutorStepResult(session=updated, replayed=False)

    if action == 'pause_session':
        _assert_transition(session.state, 'paused')
        updated = replace(
            session,
            state='paused',
            turn_seq=next_seq,
            cancelled_turn_ids=session.cancelled_turn_ids | {command.turn_id},
            command_digests=new_digests,
            last_reason_code='session_paused',
        )
        return TutorStepResult(session=updated, replayed=False)

    if action == 'select_explain':
        _assert_transition(session.state, 'explain')
        if bundle is None or type(command.query) is not str or not command.query.strip():
            raise TutorError('invalid_command')
        try:
            ret = retrieve_scoped(bundle, scope.to_retrieval_scope(), command.query, now=occurred)
        except RetrievalError:
            raise TutorError('retrieval_denied') from None
        citations = tuple(hit.citation for hit in ret.hits)
        grounded = ret.status == 'grounded'
        updated = replace(
            session,
            state='explain',
            turn_seq=next_seq,
            command_digests=new_digests,
            last_citations=citations,
            last_grounded=grounded,
            last_reason_code='explain_grounded' if grounded else 'explain_abstained',
        )
        return TutorStepResult(
            session=updated,
            replayed=False,
            abstention_reason=ret.abstention_reason,
        )

    if action == 'start_guided':
        _assert_transition(session.state, 'guided')
        updated = replace(
            session,
            state='guided',
            turn_seq=next_seq,
            command_digests=new_digests,
            last_reason_code='guided_step',
        )
        return TutorStepResult(session=updated, replayed=False)

    if action == 'start_prerequisite':
        _assert_transition(session.state, 'prerequisite')
        updated = replace(
            session,
            state='prerequisite',
            turn_seq=next_seq,
            command_digests=new_digests,
            last_reason_code='prerequisite_check',
        )
        return TutorStepResult(session=updated, replayed=False)

    if action == 'start_practice':
        _assert_transition(session.state, 'practice')
        if not isinstance(command.item, dict):
            raise TutorError('invalid_command')
        item_id = _check_id(command.item.get('id'))
        item_ver = _check_pos_int(command.item.get('version'))
        family_id = _check_id(command.item.get('family_id'))
        updated = replace(
            session,
            state='practice',
            turn_seq=next_seq,
            active_item_id=item_id,
            active_item_version=item_ver,
            active_family_id=family_id,
            active_attempt_hints=0,
            active_answer_revealed=False,
            command_digests=new_digests,
            last_reason_code='independent_practice_started',
        )
        return TutorStepResult(session=updated, replayed=False)

    if action == 'request_hint':
        if session.state not in ('practice', 'guided'):
            raise TutorError('illegal_transition')
        _assert_transition(session.state, 'guided')
        if session.active_attempt_hints >= MAX_HINTS_PER_ITEM:
            raise TutorError('hint_limit_reached')
        updated = replace(
            session,
            state='guided',
            turn_seq=next_seq,
            active_attempt_hints=session.active_attempt_hints + 1,
            command_digests=new_digests,
            last_reason_code='hint_granted_assistance_recorded',
        )
        return TutorStepResult(session=updated, replayed=False)

    if action == 'reveal_worked_answer':
        if session.state != 'guided':
            raise TutorError('illegal_transition')
        updated = replace(
            session,
            state='guided',
            turn_seq=next_seq,
            active_answer_revealed=True,
            command_digests=new_digests,
            last_reason_code='worked_answer_exposed',
        )
        return TutorStepResult(session=updated, replayed=False)

    if action == 'submit_answer':
        if session.state not in ('practice', 'guided'):
            raise TutorError('illegal_transition')
        if not isinstance(command.item, dict) or not isinstance(command.rubric, dict):
            raise TutorError('invalid_command')
        # Guard: late or mismatched submission can NEVER score the wrong item.
        if (
            session.active_item_id is None
            or command.item.get('id') != session.active_item_id
            or command.item.get('version') != session.active_item_version
            or command.item.get('family_id') != session.active_family_id
        ):
            raise TutorError('item_mismatch')
        try:
            decision = grade_submission(
                command.item,
                command.rubric,
                command.submission,
                submitted_unit=command.submitted_unit,
                uncertain=command.uncertain,
                model_proposal=command.model_proposal,
            )
        except AssessmentError:
            raise TutorError('grading_failed') from None

        if decision.outcome == 'pending_review':
            evidence_class = 'ambiguous'
            next_state = 'review_pending'
        elif session.active_answer_revealed:
            evidence_class = 'exposed'
            next_state = 'reflect'
        elif session.active_attempt_hints > 0 or session.state == 'guided':
            evidence_class = 'assisted'
            next_state = 'reflect'
        else:
            evidence_class = 'independent'
            next_state = 'reflect'

        event = EvidenceEvent(
            event_id=f'ev.{session.session_id}.{next_seq}',
            idempotency_key=f'idem.{command.command_key}',
            event_kind='attempt',
            tenant_id=session.tenant_id,
            learner_id=session.learner_id,
            edition_id=session.edition_id,
            edition_version=session.edition_version,
            objective_id=session.objective_id,
            objective_version=session.objective_version,
            occurred_at=occurred,
            recorded_at=recorded,
            actor_role=command.actor_role,
            item_id=decision.item_id,
            item_version=decision.item_version,
            family_id=session.active_family_id,
            rubric_id=decision.rubric_id,
            rubric_version=decision.rubric_version,
            evidence_class=evidence_class,
            outcome=decision.outcome,
            hints_used=session.active_attempt_hints,
            answer_revealed=session.active_answer_revealed,
        )
        updated = replace(
            session,
            state=next_state,
            turn_seq=next_seq,
            active_item_id=None,
            active_item_version=None,
            active_family_id=None,
            active_attempt_hints=0,
            active_answer_revealed=False,
            command_digests=new_digests,
            emitted_events=session.emitted_events + (event,),
            last_reason_code=decision.reason_code,
        )
        return TutorStepResult(
            session=updated,
            replayed=False,
            grade_decision=decision,
            emitted_event=event,
        )

    if action == 'reflect_next':
        if session.state != 'reflect':
            raise TutorError('illegal_transition')
        target = command.target_state or 'select'
        if target not in ('select', 'schedule', 'review_pending'):
            raise TutorError('illegal_transition')
        _assert_transition('reflect', target)
        updated = replace(
            session,
            state=target,
            turn_seq=next_seq,
            command_digests=new_digests,
            last_reason_code='reflect_advanced',
        )
        return TutorStepResult(session=updated, replayed=False)

    if action == 'finish_session':
        _assert_transition(session.state, 'done')
        updated = replace(
            session,
            state='done',
            turn_seq=next_seq,
            command_digests=new_digests,
            last_reason_code='session_completed',
        )
        return TutorStepResult(session=updated, replayed=False)

    raise TutorError('unknown_action')
