"""Offline structural review of authored shared-fixture publication candidates."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from hashlib import sha256
import re

from rest_framework.exceptions import ValidationError

from .contracts import SERIALIZERS, canonical, key, source_key, validate_bundle


_MAX_RECORDS = 500
_MAX_VERSION = 2**31 - 1
_MAX_DEPTH = 8
_MAX_NODES = 50_000
_MAX_TEXT = 2_000_000
_IDENTIFIER = re.compile(r'[a-z][a-z0-9._-]{1,95}')
_DIGEST = re.compile(r'[0-9a-f]{64}')
_DEPENDENCIES = {
    'item': (('edition', 'edition'), ('rubric', 'rubric'), ('objectives', 'objective'), ('source', 'material')),
    'objective': (('edition', 'edition'), ('source', 'material')),
    'edition': (('profile', 'profile'), ('collection', 'collection')),
    'collection': (('materials', 'material'),),
    'material': (('rights', 'rights'),),
}


class PreflightError(ValueError):
    """A fixed failure reason containing no input values."""


@dataclass(frozen=True)
class AssessmentHold:
    item_id: str
    item_version: int
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class PublicationPreflightReport:
    assessment_holds: tuple[AssessmentHold, ...]
    status: str = field(default='structure_valid_assessment_held', init=False)


def _bounded_json(value):
    """Reject non-JSON objects, cycles and excess data before validation or hashing."""
    pending = [(value, 0)]
    nodes = text = 0
    while pending:
        current, depth = pending.pop()
        nodes += 1
        if nodes > _MAX_NODES or depth > _MAX_DEPTH:
            raise ValueError
        kind = type(current)
        if kind is dict:
            if len(current) > 32 or any(type(name) is not str or len(name) > 96 for name in current):
                raise ValueError
            text += sum(map(len, current))
            pending.extend((child, depth + 1) for child in current.values())
        elif kind is list:
            if len(current) > _MAX_RECORDS:
                raise ValueError
            pending.extend((child, depth + 1) for child in current)
        elif kind is str:
            if len(current) > 20_000:
                raise ValueError
            text += len(current)
        elif kind is int:
            if not 1 <= current <= _MAX_VERSION:
                raise ValueError
        elif current is not None and kind is not bool:
            raise ValueError
        if text > _MAX_TEXT:
            raise ValueError


def _reference(kind, ref):
    return (kind, *source_key(ref))


def _reachable(rows, items):
    pending = list(items)
    pins = {}
    while pending:
        identity = pending.pop()
        if identity in pins:
            continue
        record = rows[identity]
        if record['status'] != 'approved':
            raise ValueError
        pins[identity] = sha256(canonical(record)).hexdigest()
        for field, kind in _DEPENDENCIES.get(record['kind'], ()):
            refs = record[field]
            if type(refs) is list:
                pending.extend(_reference(kind, ref) for ref in refs)
            else:
                pending.append(_reference(kind, refs))
    return pins


def _inspect_bundle(bundle, *, now, failure, previous=None):
    try:
        _bounded_json(bundle)
        for record in bundle['records']:
            if record['kind'] == 'rights' and datetime.fromisoformat(record['expires_at']).utcoffset() is None:
                raise ValueError
        rows = validate_bundle(bundle, previous=previous, now=now)
        if previous is not None and rows.keys() - previous.keys():
            raise ValueError
        if any(record['audience']['type'] != 'shared_fixture' or record.get('specification_id') is not None
               for record in rows.values()):
            raise ValueError
        items = sorted(key(record) for record in rows.values()
                       if record['kind'] == 'item' and record['status'] == 'approved')
        if not items:
            raise ValueError
        pins = _reachable(rows, items)
        holds = []
        for identity in items:
            item = rows[identity]
            grader = rows[_reference('rubric', item['rubric'])]['grader_id']
            if grader == 'choice.v1' and len(item['options']) < 2:
                raise ValueError
            semantic_review = 'human_review_only' if grader == 'human-review.v1' else 'actual_grader_review_required'
            holds.append(AssessmentHold(item['id'], item['version'], (semantic_review, 'educator_review_required')))
        return rows, pins, tuple(holds)
    except (ValidationError, ValueError, KeyError, TypeError, OverflowError):
        raise PreflightError(failure) from None


def _manifest_pins(manifest):
    try:
        _bounded_json(manifest)
    except ValueError:
        raise PreflightError('invalid_manifest') from None
    if (type(manifest) is not dict or manifest.keys() != {'schema_version', 'records'}
            or type(manifest['schema_version']) is not str or manifest['schema_version'] != '1.0'
            or type(manifest['records']) is not list or not 1 <= len(manifest['records']) <= _MAX_RECORDS):
        raise PreflightError('invalid_manifest')
    pins = {}
    for entry in manifest['records']:
        if type(entry) is not dict or entry.keys() != {'kind', 'id', 'version', 'sha256'}:
            raise PreflightError('invalid_manifest')
        kind, record_id, version = key(entry)
        digest = entry['sha256']
        if (type(kind) is not str or len(kind) > 32 or kind not in SERIALIZERS
                or type(record_id) is not str or len(record_id) > 96 or not _IDENTIFIER.fullmatch(record_id)
                or type(version) is not int or not 1 <= version <= _MAX_VERSION
                or type(digest) is not str or len(digest) != 64 or not _DIGEST.fullmatch(digest)):
            raise PreflightError('invalid_manifest')
        identity = (kind, record_id, version)
        if identity in pins:
            raise PreflightError('invalid_manifest')
        pins[identity] = digest
    return pins


def validate_publication_preflight(candidate_bundle, candidate_manifest, *, inventory_bundle, now):
    """Check one shared fixture candidate against an independently sourced, trusted inventory."""
    try:
        if type(now) is not datetime or now.utcoffset() is None:
            raise ValueError
        now = now.astimezone(timezone.utc)
    except (ValueError, OverflowError, TypeError):
        raise PreflightError('invalid_time') from None
    if candidate_bundle is inventory_bundle:
        raise PreflightError('invalid_inventory')

    manifest_pins = _manifest_pins(candidate_manifest)
    inventory, expected_pins, holds = _inspect_bundle(inventory_bundle, now=now, failure='invalid_inventory')
    _, candidate_pins, _ = _inspect_bundle(candidate_bundle, previous=inventory, now=now, failure='invalid_candidate')
    if candidate_pins != expected_pins or manifest_pins != expected_pins:
        raise PreflightError('manifest_mismatch')
    return PublicationPreflightReport(assessment_holds=holds)
