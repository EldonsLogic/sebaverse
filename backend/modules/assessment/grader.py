"""AUTH-019: deterministic grading over reviewed item/rubric contracts.

Never executes untrusted expressions, never allows a model proposal to write an
accepted grade directly, holds human-review and ambiguous submissions for review,
and never leaks answer keys in decisions or error messages.
"""

from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
import re

from rest_framework.exceptions import ValidationError

from modules.curriculum.contracts import SERIALIZERS


_MAX_SUBMISSION_CHARS = 4000
_MAX_NUMERIC_CHARS = 64
_MAX_UNIT_CHARS = 64
_NUMERIC_LITERAL = re.compile(r'^[+-]?(?:[0-9]+(?:\.[0-9]+)?|\.[0-9]+)$')
_NUMERIC_TRANS = str.maketrans({
    '٠': '0',
    '١': '1',
    '٢': '2',
    '٣': '3',
    '٤': '4',
    '٥': '5',
    '٦': '6',
    '٧': '7',
    '٨': '8',
    '٩': '9',
    '٫': '.',
    '−': '-',
})


class AssessmentError(ValueError):
    """Fail-closed grading error with fixed reason code and zero leaked keys."""


@dataclass(frozen=True)
class GradeDecision:
    """Answer-key-free grading decision for one reviewed item/rubric pair."""
    outcome: str
    grader_id: str
    item_id: str
    item_version: int
    rubric_id: str
    rubric_version: int
    needs_human_review: bool
    reason_code: str
    answer_key_included: bool = field(default=False, init=False)


def _validate_item_and_rubric(item: dict, rubric: dict) -> tuple[dict, dict]:
    if not isinstance(item, dict) or item.get('kind') != 'item':
        raise AssessmentError('invalid_item')
    if not isinstance(rubric, dict) or rubric.get('kind') != 'rubric':
        raise AssessmentError('invalid_rubric')
    try:
        item_ser = SERIALIZERS['item'](data=item)
        item_ser.is_valid(raise_exception=True)
    except (ValidationError, ValueError, TypeError):
        raise AssessmentError('invalid_item') from None
    try:
        rubric_ser = SERIALIZERS['rubric'](data=rubric)
        rubric_ser.is_valid(raise_exception=True)
    except (ValidationError, ValueError, TypeError):
        raise AssessmentError('invalid_rubric') from None

    if item['status'] != 'approved':
        raise AssessmentError('invalid_item')
    if rubric['status'] != 'approved':
        raise AssessmentError('invalid_rubric')
    if (
        item['rubric']['id'] != rubric['id']
        or item['rubric']['version'] != rubric['version']
        or item['audience'] != rubric['audience']
    ):
        raise AssessmentError('grader_mismatch')
    return item, rubric


def _parse_finite_decimal(raw: str) -> Decimal | None:
    if len(raw) > _MAX_NUMERIC_CHARS:
        return None
    normalized = raw.translate(_NUMERIC_TRANS).strip()
    if not _NUMERIC_LITERAL.fullmatch(normalized):
        return None
    try:
        val = Decimal(normalized)
    except InvalidOperation:
        return None
    if not val.is_finite():
        return None
    return val


def grade_submission(
    item: dict,
    rubric: dict,
    submission: str,
    *,
    submitted_unit: str | None = None,
    uncertain: bool = False,
    model_proposal: dict | None = None,
) -> GradeDecision:
    """Deterministically grade one submission against an approved item and rubric."""
    item, rubric = _validate_item_and_rubric(item, rubric)

    if type(submission) is not str or not submission.strip() or len(submission) > _MAX_SUBMISSION_CHARS:
        raise AssessmentError('invalid_submission')
    if submitted_unit is not None and (type(submitted_unit) is not str or len(submitted_unit) > _MAX_UNIT_CHARS):
        raise AssessmentError('invalid_submission')
    if type(uncertain) is not bool:
        raise AssessmentError('invalid_submission')

    grader_id = rubric['grader_id']
    config = rubric['config']

    def _decision(outcome: str, needs_review: bool, reason: str) -> GradeDecision:
        return GradeDecision(
            outcome=outcome,
            grader_id=grader_id,
            item_id=item['id'],
            item_version=item['version'],
            rubric_id=rubric['id'],
            rubric_version=rubric['version'],
            needs_human_review=needs_review,
            reason_code=reason,
        )

    # Validate grader-specific rubric/item consistency BEFORE any hold or grading.
    if grader_id == 'choice.v1':
        option_ids = [opt['id'] for opt in item['options']]
        if len(option_ids) < 2 or len(set(option_ids)) != len(option_ids):
            raise AssessmentError('invalid_item')
        if config['correct_option'] not in option_ids:
            raise AssessmentError('grader_mismatch')
    elif grader_id == 'numeric.v1':
        expected_pre = _parse_finite_decimal(config['expected'])
        tolerance_pre = _parse_finite_decimal(config['tolerance'])
        if expected_pre is None or tolerance_pre is None or tolerance_pre < 0:
            raise AssessmentError('invalid_rubric')

    # Human-review rubrics NEVER receive an invented deterministic grade.
    if grader_id == 'human-review.v1':
        return _decision('pending_review', True, 'human_review_required')

    # Unvalidated model proposals are always held for human review; models never write grades.
    if model_proposal is not None:
        return _decision('pending_review', True, 'model_proposal_held')

    # Uncertain submissions (e.g., low-confidence speech or ambiguous response) wait for review.
    if uncertain:
        return _decision('pending_review', True, 'ambiguous_submission')

    if grader_id == 'choice.v1':
        option_ids = [opt['id'] for opt in item['options']]
        correct_opt = config['correct_option']
        picked = submission.strip()
        if picked not in option_ids:
            raise AssessmentError('invalid_submission')
        if picked == correct_opt:
            return _decision('correct', False, 'choice_match')
        return _decision('incorrect', False, 'choice_mismatch')

    if grader_id == 'exact-set.v1':
        case_sensitive = config['case_sensitive']
        candidate = submission.strip()
        accepted = config['accepted']
        if not case_sensitive:
            candidate = candidate.casefold()
            accepted = [variant.strip().casefold() for variant in accepted]
        else:
            accepted = [variant.strip() for variant in accepted]
        if candidate in accepted:
            return _decision('correct', False, 'exact_match')
        return _decision('incorrect', False, 'exact_mismatch')

    if grader_id == 'numeric.v1':
        expected = _parse_finite_decimal(config['expected'])
        tolerance = _parse_finite_decimal(config['tolerance'])
        parsed = _parse_finite_decimal(submission)
        if parsed is None:
            return _decision('incorrect', False, 'numeric_unparseable')
        expected_unit = config['unit']
        if expected_unit is not None:
            if submitted_unit is None or submitted_unit.strip() != expected_unit.strip():
                return _decision('incorrect', False, 'numeric_unit_mismatch')
        elif submitted_unit is not None and submitted_unit.strip():
            return _decision('incorrect', False, 'numeric_unit_mismatch')
        if abs(parsed - expected) <= tolerance:
            return _decision('correct', False, 'numeric_within_tolerance')
        return _decision('incorrect', False, 'numeric_outside_tolerance')

    raise AssessmentError('invalid_rubric')
