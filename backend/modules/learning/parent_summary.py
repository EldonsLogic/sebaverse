"""AUTH-021: guardian-scoped parent progress summary (DEV-015 backend preflight).

Enforces live guardian_reporting authority via modules.access.policy, projects
evidence honestly from modules.learning.ledger without raw child chat, answer
keys, personal labels, or fabricated attainment percentages, and exposes explicit
uncertainty and recommended next-step codes (R047, R056).
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta

from modules.access import policy
from modules.learning.ledger import (
    DEFAULT_RETENTION_DELAY,
    EvidenceEvent,
    LedgerError,
    LedgerScope,
    project_objective_mastery,
)


SUMMARY_VERSION = 'parent.summary-preflight-v1'
_MAX_OBJECTIVES = 100


class ParentSummaryError(ValueError):
    """Fail-closed parent summary error with fixed code and zero leaked data."""


@dataclass(frozen=True)
class ObjectiveSummaryItem:
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
    recommended_next_action: str
    review_due_at: datetime | None
    is_calibrated: bool = field(default=False, init=False)


@dataclass(frozen=True)
class ParentProgressSummary:
    tenant_id: str
    learner_id: str
    edition_id: str
    edition_version: int
    objectives: tuple[ObjectiveSummaryItem, ...]
    summary_version: str = field(default=SUMMARY_VERSION, init=False)
    raw_chat_included: bool = field(default=False, init=False)
    fabricated_percentage_included: bool = field(default=False, init=False)


def _next_action(status: str, uncertainty: str) -> str:
    if uncertainty == 'pending_review':
        return 'await_educator_review'
    if uncertainty == 'probe_needed':
        return 'schedule_probe_check'
    if status == 'unassessed':
        return 'start_diagnostic_or_practice'
    if status == 'needs_support':
        return 'guided_support_needed'
    if status == 'developing':
        return 'practice_new_item_family'
    if status == 'ready_for_review':
        return 'schedule_delayed_review'
    return 'maintain_periodic_review'


def build_parent_progress_summary(
    events: list[EvidenceEvent] | tuple[EvidenceEvent, ...],
    *,
    scope: LedgerScope,
    objectives: list[tuple[str, int]] | tuple[tuple[str, int], ...],
    retention_delay: timedelta = DEFAULT_RETENTION_DELAY,
) -> ParentProgressSummary:
    """Build an authorized, chat-free, uncertainty-honest parent progress summary."""
    if not isinstance(scope, LedgerScope):
        raise ParentSummaryError('invalid_scope')
    if scope.role != 'guardian' or scope.purpose != 'guardian_reporting':
        raise ParentSummaryError('access_denied')
    if not policy.allowed(scope.to_access_scope()):
        raise ParentSummaryError('access_denied')

    if not isinstance(objectives, (list, tuple)) or not 1 <= len(objectives) <= _MAX_OBJECTIVES:
        raise ParentSummaryError('invalid_objectives')

    seen: set[tuple[str, int]] = set()
    items: list[ObjectiveSummaryItem] = []
    for entry in objectives:
        if not isinstance(entry, tuple) or len(entry) != 2:
            raise ParentSummaryError('invalid_objectives')
        obj_id, obj_ver = entry
        if (obj_id, obj_ver) in seen:
            raise ParentSummaryError('duplicate_objective')
        seen.add((obj_id, obj_ver))
        try:
            proj = project_objective_mastery(
                events,
                scope=scope,
                objective_id=obj_id,
                objective_version=obj_ver,
                retention_delay=retention_delay,
            )
        except LedgerError as exc:
            code = str(exc)
            if code == 'access_denied':
                raise ParentSummaryError('access_denied') from None
            if code == 'invalid_scope':
                raise ParentSummaryError('invalid_objectives') from None
            raise ParentSummaryError('invalid_evidence') from None

        items.append(
            ObjectiveSummaryItem(
                objective_id=proj.objective_id,
                objective_version=proj.objective_version,
                status=proj.status,
                uncertainty=proj.uncertainty,
                independent_count=proj.independent_count,
                independent_correct_families=proj.independent_correct_families,
                assisted_count=proj.assisted_count,
                exposed_count=proj.exposed_count,
                ambiguous_count=proj.ambiguous_count,
                external_observation_count=proj.external_observation_count,
                recommended_next_action=_next_action(proj.status, proj.uncertainty),
                review_due_at=proj.review_due_at,
            )
        )

    return ParentProgressSummary(
        tenant_id=scope.tenant_id,
        learner_id=scope.learner_id,
        edition_id=scope.edition_id,
        edition_version=scope.edition_version,
        objectives=tuple(items),
    )
