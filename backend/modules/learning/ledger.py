"""AUTH-019: immutable learning-evidence ledger and deterministic mastery projection.

Keeps independent, assisted, exposed, ambiguous, and external-observation evidence
distinct; replays duplicate, out-of-order, and appeal/correction events
deterministically; never lets hints, exposed repeats, external marks, or models
promote mastery. Baseline thresholds are uncalibrated engineering hypotheses.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from hashlib import sha256
import json
import re

from modules.access import policy


PROJECTION_VERSION = 'learning.projection-preflight-v1'
STATUSES = ('unassessed', 'needs_support', 'developing', 'ready_for_review', 'retained')
EVIDENCE_CLASSES = frozenset({'independent', 'assisted', 'exposed', 'ambiguous', 'external_observation'})
OUTCOMES = frozenset({'correct', 'incorrect', 'pending_review'})
CORRECTION_ACTIONS = frozenset({'override_outcome', 'invalidate_item', 'reclassify_evidence'})
ALLOWED_ATTEMPT_ACTORS = frozenset({'learner', 'guardian', 'teacher', 'system'})
ALLOWED_CORRECTION_ACTORS = frozenset({'teacher', 'reviewer'})
REVIEW_INTERVAL_DAYS = (1, 3, 7, 14, 30)
DEFAULT_RETENTION_DELAY = timedelta(days=7)

_IDENTIFIER = re.compile(r'[a-z][a-z0-9._-]{1,95}')
_FORBIDDEN_MODEL_PREFIXES = ('model', 'llm', 'ai.')


class LedgerError(ValueError):
    """Fail-closed ledger error with fixed reason code and zero leaked data."""


@dataclass(frozen=True)
class LedgerScope:
    """Server-derived authorization scope for projecting one learner's evidence."""
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
            kind='edition',
        )


@dataclass(frozen=True)
class EvidenceEvent:
    """Immutable append-only learning evidence or appeal/correction lineage event."""
    event_id: str
    idempotency_key: str
    event_kind: str
    tenant_id: str
    learner_id: str
    edition_id: str
    edition_version: int
    objective_id: str
    objective_version: int
    occurred_at: datetime
    recorded_at: datetime
    actor_role: str
    # Attempt fields
    item_id: str | None = None
    item_version: int | None = None
    family_id: str | None = None
    rubric_id: str | None = None
    rubric_version: int | None = None
    evidence_class: str | None = None
    outcome: str | None = None
    hints_used: int = 0
    answer_revealed: bool = False
    # Correction / appeal lineage fields
    supersedes_event_id: str | None = None
    adjudicator_ref: str | None = None
    correction_action: str | None = None
    new_outcome: str | None = None
    new_evidence_class: str | None = None
    reason_code: str | None = None


@dataclass(frozen=True)
class ConceptProjection:
    """Deterministic mastery & review projection for one learner/objective version."""
    tenant_id: str
    learner_id: str
    edition_id: str
    edition_version: int
    objective_id: str
    objective_version: int
    status: str
    uncertainty: str
    independent_count: int
    independent_correct_families: tuple[str, ...]
    assisted_count: int
    exposed_count: int
    ambiguous_count: int
    external_observation_count: int
    invalidated_count: int
    recent_failures: int
    last_independent_at: datetime | None
    review_due_at: datetime | None
    event_cursor: str
    applied_event_count: int
    projection_version: str = field(default=PROJECTION_VERSION, init=False)
    is_calibrated: bool = field(default=False, init=False)


def _to_utc(dt: datetime, *, code: str = 'invalid_time') -> datetime:
    try:
        if type(dt) is not datetime or dt.utcoffset() is None:
            raise ValueError
        return dt.astimezone(timezone.utc)
    except (ValueError, OverflowError, TypeError):
        raise LedgerError(code) from None


def _check_id(value: object, *, code: str = 'invalid_event') -> str:
    if type(value) is not str or not _IDENTIFIER.fullmatch(value):
        raise LedgerError(code)
    return value


def _check_pos_int(value: object, *, code: str = 'invalid_event') -> int:
    if type(value) is not int or value < 1:
        raise LedgerError(code)
    return value


def _validate_scope(scope: LedgerScope) -> None:
    if not isinstance(scope, LedgerScope):
        raise LedgerError('invalid_scope')
    for val in (scope.tenant_id, scope.learner_id, scope.edition_id):
        _check_id(val, code='invalid_scope')
    _check_pos_int(scope.edition_version, code='invalid_scope')
    if type(scope.role) is not str or type(scope.purpose) is not str:
        raise LedgerError('invalid_scope')
    if not policy.allowed(scope.to_access_scope()):
        raise LedgerError('access_denied')


def validate_event(event: EvidenceEvent) -> tuple[datetime, datetime]:
    """Validate one immutable evidence or correction event; return UTC timestamps."""
    if not isinstance(event, EvidenceEvent):
        raise LedgerError('invalid_event')
    _check_id(event.event_id)
    _check_id(event.idempotency_key)
    _check_id(event.tenant_id)
    _check_id(event.learner_id)
    _check_id(event.edition_id)
    _check_pos_int(event.edition_version)
    _check_id(event.objective_id)
    _check_pos_int(event.objective_version)
    occurred = _to_utc(event.occurred_at, code='invalid_event')
    recorded = _to_utc(event.recorded_at, code='invalid_event')

    if type(event.actor_role) is not str or event.actor_role == 'model':
        raise LedgerError('invalid_event')

    if event.event_kind == 'attempt':
        if event.actor_role not in ALLOWED_ATTEMPT_ACTORS:
            raise LedgerError('invalid_event')
        _check_id(event.item_id)
        _check_pos_int(event.item_version)
        _check_id(event.family_id)
        _check_id(event.rubric_id)
        _check_pos_int(event.rubric_version)
        if type(event.evidence_class) is not str or event.evidence_class not in EVIDENCE_CLASSES:
            raise LedgerError('invalid_event')
        if type(event.outcome) is not str or event.outcome not in OUTCOMES:
            raise LedgerError('invalid_event')
        if type(event.hints_used) is not int or event.hints_used < 0:
            raise LedgerError('invalid_event')
        if type(event.answer_revealed) is not bool:
            raise LedgerError('invalid_event')
        # A hint or revealed answer ends independence immediately.
        if (event.hints_used > 0 or event.answer_revealed) and event.evidence_class == 'independent':
            raise LedgerError('invalid_event')
        # Pending human review can never be recorded as independent evidence.
        if event.outcome == 'pending_review' and event.evidence_class != 'ambiguous':
            raise LedgerError('invalid_event')
        return occurred, recorded

    if event.event_kind == 'correction':
        if event.actor_role not in ALLOWED_CORRECTION_ACTORS:
            raise LedgerError('invalid_correction')
        _check_id(event.supersedes_event_id, code='invalid_correction')
        adj = _check_id(event.adjudicator_ref, code='invalid_correction')
        if any(adj == p or adj.startswith(p + '.') or adj.startswith(p + '-') for p in _FORBIDDEN_MODEL_PREFIXES):
            raise LedgerError('invalid_correction')
        if type(event.correction_action) is not str or event.correction_action not in CORRECTION_ACTIONS:
            raise LedgerError('invalid_correction')
        _check_id(event.reason_code, code='invalid_correction')
        if event.correction_action == 'override_outcome':
            if type(event.new_outcome) is not str or event.new_outcome not in OUTCOMES:
                raise LedgerError('invalid_correction')
            if event.new_evidence_class is not None and (
                type(event.new_evidence_class) is not str or event.new_evidence_class not in EVIDENCE_CLASSES
            ):
                raise LedgerError('invalid_correction')
        elif event.correction_action == 'reclassify_evidence':
            if type(event.new_evidence_class) is not str or event.new_evidence_class not in EVIDENCE_CLASSES:
                raise LedgerError('invalid_correction')
        return occurred, recorded

    raise LedgerError('invalid_event')


def _canonical_event_digest(event: EvidenceEvent, occurred: datetime, recorded: datetime) -> str:
    payload = {
        'event_id': event.event_id,
        'idempotency_key': event.idempotency_key,
        'event_kind': event.event_kind,
        'tenant_id': event.tenant_id,
        'learner_id': event.learner_id,
        'edition_id': event.edition_id,
        'edition_version': event.edition_version,
        'objective_id': event.objective_id,
        'objective_version': event.objective_version,
        'occurred_at': occurred.isoformat(),
        'recorded_at': recorded.isoformat(),
        'actor_role': event.actor_role,
        'item_id': event.item_id,
        'item_version': event.item_version,
        'family_id': event.family_id,
        'rubric_id': event.rubric_id,
        'rubric_version': event.rubric_version,
        'evidence_class': event.evidence_class,
        'outcome': event.outcome,
        'hints_used': event.hints_used,
        'answer_revealed': event.answer_revealed,
        'supersedes_event_id': event.supersedes_event_id,
        'adjudicator_ref': event.adjudicator_ref,
        'correction_action': event.correction_action,
        'new_outcome': event.new_outcome,
        'new_evidence_class': event.new_evidence_class,
        'reason_code': event.reason_code,
    }
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
    return sha256(raw).hexdigest()


def project_objective_mastery(
    events: list[EvidenceEvent] | tuple[EvidenceEvent, ...],
    *,
    scope: LedgerScope,
    objective_id: str,
    objective_version: int,
    retention_delay: timedelta = DEFAULT_RETENTION_DELAY,
) -> ConceptProjection:
    """Replay immutable events deterministically for one authorized learner/objective."""
    _validate_scope(scope)
    _check_id(objective_id, code='invalid_scope')
    _check_pos_int(objective_version, code='invalid_scope')
    if not isinstance(retention_delay, timedelta) or retention_delay <= timedelta(0):
        raise LedgerError('invalid_time')

    # 1. Filter strictly to authorized learner/tenant/edition/objective and deduplicate idempotently.
    by_event_id: dict[str, tuple[str, datetime, datetime, EvidenceEvent]] = {}
    by_idem_key: dict[str, str] = {}

    for event in events:
        if not isinstance(event, EvidenceEvent):
            raise LedgerError('invalid_event')
        # Strict learner/tenant/edition/objective isolation: ignore events outside this scope.
        if (
            event.tenant_id != scope.tenant_id
            or event.learner_id != scope.learner_id
            or event.edition_id != scope.edition_id
            or event.edition_version != scope.edition_version
            or event.objective_id != objective_id
            or event.objective_version != objective_version
        ):
            continue
        occurred, recorded = validate_event(event)
        digest = _canonical_event_digest(event, occurred, recorded)

        if event.event_id in by_event_id:
            if by_event_id[event.event_id][0] != digest:
                raise LedgerError('conflicting_duplicate')
            continue
        if event.idempotency_key in by_idem_key:
            if by_idem_key[event.idempotency_key] != digest:
                raise LedgerError('conflicting_duplicate')
            continue
        by_event_id[event.event_id] = (digest, occurred, recorded, event)
        by_idem_key[event.idempotency_key] = digest

    # 2. Order deterministically regardless of arrival order.
    ordered = sorted(
        by_event_id.values(),
        key=lambda item: (item[1], item[2], item[3].event_id),
    )

    # 3. Build effective attempt map and apply append-only correction lineage.
    attempts: dict[str, dict] = {}
    attempt_order: list[str] = []
    corrections: list[tuple[datetime, datetime, EvidenceEvent]] = []

    for _, occurred, recorded, ev in ordered:
        if ev.event_kind == 'attempt':
            attempts[ev.event_id] = {
                'event': ev,
                'occurred_at': occurred,
                'outcome': ev.outcome,
                'evidence_class': ev.evidence_class,
                'invalidated': False,
            }
            attempt_order.append(ev.event_id)
        else:
            corrections.append((occurred, recorded, ev))

    for _, _, corr in corrections:
        target = attempts.get(corr.supersedes_event_id)
        if target is None:
            raise LedgerError('invalid_correction')
        orig: EvidenceEvent = target['event']
        if corr.correction_action == 'invalidate_item':
            target['invalidated'] = True
        elif corr.correction_action == 'override_outcome':
            target['outcome'] = corr.new_outcome
            if corr.new_evidence_class is not None:
                if corr.new_evidence_class == 'independent' and (orig.hints_used > 0 or orig.answer_revealed):
                    raise LedgerError('invalid_correction')
                target['evidence_class'] = corr.new_evidence_class
            elif corr.new_outcome == 'pending_review':
                target['evidence_class'] = 'ambiguous'
        elif corr.correction_action == 'reclassify_evidence':
            if corr.new_evidence_class == 'independent' and (
                orig.hints_used > 0 or orig.answer_revealed or target['outcome'] == 'pending_review'
            ):
                raise LedgerError('invalid_correction')
            target['evidence_class'] = corr.new_evidence_class

    # 4. Replay effective attempts chronologically to compute mastery & review schedule.
    independent_count = 0
    assisted_count = 0
    exposed_count = 0
    ambiguous_count = 0
    external_observation_count = 0
    invalidated_count = 0
    recent_failures = 0
    consecutive_independent_successes = 0
    probe_needed = False
    retained_achieved = False
    ready_for_review_at: datetime | None = None
    last_independent_at: datetime | None = None
    independent_correct_families: list[str] = []
    exposed_items: set[tuple[str, int]] = set()

    for ev_id in attempt_order:
        state = attempts[ev_id]
        ev: EvidenceEvent = state['event']
        occurred_at: datetime = state['occurred_at']
        item_key = (ev.item_id, ev.item_version)

        if state['invalidated']:
            invalidated_count += 1
            continue

        ev_class = state['evidence_class']
        outcome = state['outcome']

        if ev_class == 'assisted':
            assisted_count += 1
            exposed_items.add(item_key)
            continue
        if ev_class == 'exposed':
            exposed_count += 1
            exposed_items.add(item_key)
            continue
        if ev_class == 'ambiguous':
            ambiguous_count += 1
            exposed_items.add(item_key)
            continue
        if ev_class == 'external_observation':
            external_observation_count += 1
            continue

        # ev_class == 'independent'
        if outcome == 'pending_review':
            ambiguous_count += 1
            exposed_items.add(item_key)
            continue

        if outcome == 'correct':
            # Repeated or previously exposed items never qualify as independent success.
            if item_key in exposed_items:
                exposed_count += 1
                continue
            exposed_items.add(item_key)
            independent_count += 1
            last_independent_at = occurred_at
            consecutive_independent_successes += 1
            probe_needed = False

            if ev.family_id not in independent_correct_families:
                if (
                    ready_for_review_at is not None
                    and len(independent_correct_families) >= 2
                    and (occurred_at - ready_for_review_at) >= retention_delay
                ):
                    retained_achieved = True
                independent_correct_families.append(ev.family_id)
                if len(independent_correct_families) == 2 and ready_for_review_at is None:
                    ready_for_review_at = occurred_at
        elif outcome == 'incorrect':
            exposed_items.add(item_key)
            independent_count += 1
            last_independent_at = occurred_at
            recent_failures += 1
            consecutive_independent_successes = 0
            if len(independent_correct_families) >= 2:
                # Marks uncertainty without erasing prior independent successes.
                probe_needed = True

    if independent_count == 0:
        status = 'unassessed'
    elif len(independent_correct_families) == 0:
        status = 'needs_support'
    elif len(independent_correct_families) == 1:
        status = 'developing'
    elif retained_achieved and not probe_needed:
        status = 'retained'
    else:
        status = 'ready_for_review'

    if independent_count == 0 and ambiguous_count == 0:
        uncertainty = 'no_evidence'
    elif ambiguous_count > 0:
        uncertainty = 'pending_review'
    elif probe_needed:
        uncertainty = 'probe_needed'
    else:
        uncertainty = 'low'

    if status == 'unassessed' or last_independent_at is None:
        review_due_at = None
    elif status == 'needs_support' or probe_needed or consecutive_independent_successes == 0:
        review_due_at = last_independent_at
    else:
        idx = min(consecutive_independent_successes - 1, len(REVIEW_INTERVAL_DAYS) - 1)
        review_due_at = last_independent_at + timedelta(days=REVIEW_INTERVAL_DAYS[idx])

    cursor_source = ','.join(item[3].event_id for item in ordered)
    event_cursor = sha256(cursor_source.encode('utf-8')).hexdigest()

    return ConceptProjection(
        tenant_id=scope.tenant_id,
        learner_id=scope.learner_id,
        edition_id=scope.edition_id,
        edition_version=scope.edition_version,
        objective_id=objective_id,
        objective_version=objective_version,
        status=status,
        uncertainty=uncertainty,
        independent_count=independent_count,
        independent_correct_families=tuple(independent_correct_families),
        assisted_count=assisted_count,
        exposed_count=exposed_count,
        ambiguous_count=ambiguous_count,
        external_observation_count=external_observation_count,
        invalidated_count=invalidated_count,
        recent_failures=recent_failures,
        last_independent_at=last_independent_at,
        review_due_at=review_due_at,
        event_cursor=event_cursor,
        applied_event_count=len(ordered),
    )
