"""AUTH-021: metadata-only telemetry redaction and deletion-tombstone replay (DEV-016 preflight).

Enforces strict allowlist telemetry redaction (identifier-only labels, validated
ISO-8601 timestamps, non-negative ints; no child prompts, audio, transcripts,
free text, or personal identifiers in logs/metric labels, R059/R079) and
deterministic backup-restore deletion-tombstone replay with explicit target_kind
disambiguation so deleted learner data is never resurrected on restore (R061).
No database or network calls occur here.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from hashlib import sha256
import json
import re


PRIVACY_POLICY_VERSION = 'operations.privacy-preflight-v1'
ALLOWED_TELEMETRY_ID_FIELDS = frozenset({
    'event_type',
    'service',
    'outcome',
    'reason_code',
    'edition_id',
    'subject_tag',
})
ALLOWED_TELEMETRY_INT_FIELDS = frozenset({
    'status_code',
    'latency_ms',
    'token_count_in',
    'token_count_out',
    'cached_units',
    'edition_version',
})
ALLOWED_TOMBSTONE_KINDS = frozenset({'learner_all', 'upload', 'session'})
SCOPED_TARGET_KINDS = frozenset({'upload', 'session'})
ALLOWED_RECORD_KINDS = frozenset({'upload', 'session', 'cache', 'chunk', 'job', 'evidence'})
_IDENTIFIER = re.compile(r'[a-z][a-z0-9._-]{1,95}')
_FORBIDDEN_MODEL_TOKENS = frozenset({'model', 'llm', 'ai'})


class PrivacyError(ValueError):
    """Fail-closed privacy/tombstone error with fixed code and zero leaked PII."""


@dataclass(frozen=True)
class SanitizedTelemetry:
    """Allowlisted metadata-only telemetry record; never eligible for auto-training."""
    fields: tuple[tuple[str, str | int], ...]
    dropped_field_count: int
    policy_version: str = field(default=PRIVACY_POLICY_VERSION, init=False)
    training_corpus_eligible: bool = field(default=False, init=False)

    def as_dict(self) -> dict[str, str | int | bool]:
        out: dict[str, str | int | bool] = dict(self.fields)
        out['policy_version'] = self.policy_version
        out['training_corpus_eligible'] = self.training_corpus_eligible
        return out


@dataclass(frozen=True)
class DeletionTombstone:
    """Immutable deletion tombstone replayed across restored snapshots and derived stores."""
    tombstone_id: str
    tenant_id: str
    learner_id: str
    target_kind: str
    deleted_at: datetime
    reason_code: str
    authority_ref: str
    target_id: str | None = None


@dataclass(frozen=True)
class RestorableRecord:
    """Snapshot record subject to deletion-tombstone enforcement on restore."""
    record_id: str
    tenant_id: str
    learner_id: str
    record_kind: str
    created_at: datetime
    target_kind: str | None = None
    target_id: str | None = None


@dataclass(frozen=True)
class TombstoneReplayReport:
    retained_record_ids: tuple[str, ...]
    purged_record_ids: tuple[str, ...]
    applied_tombstone_count: int
    replay_digest: str
    policy_version: str = field(default=PRIVACY_POLICY_VERSION, init=False)


def _check_id(value: object, *, code: str = 'invalid_input') -> str:
    if type(value) is not str or not _IDENTIFIER.fullmatch(value):
        raise PrivacyError(code)
    return value


def _to_utc(dt: datetime, *, code: str = 'invalid_time') -> datetime:
    try:
        if type(dt) is not datetime or dt.utcoffset() is None:
            raise ValueError
        return dt.astimezone(timezone.utc)
    except (ValueError, OverflowError, TypeError):
        raise PrivacyError(code) from None


def _is_non_model_authority(ref: object) -> bool:
    if type(ref) is not str or not _IDENTIFIER.fullmatch(ref):
        return False
    return re.split(r'[._-]', ref, maxsplit=1)[0] not in _FORBIDDEN_MODEL_TOKENS


def _parse_iso_utc(raw: object) -> str | None:
    if type(raw) is not str or len(raw) > 64:
        return None
    try:
        dt = datetime.fromisoformat(raw)
        if dt.utcoffset() is None:
            return None
        return dt.astimezone(timezone.utc).isoformat()
    except (ValueError, OverflowError, TypeError):
        return None


def sanitize_telemetry_record(raw: dict) -> SanitizedTelemetry:
    """Keep only allowlisted, identifier/timestamp/int metadata; drop all free text & PII."""
    if not isinstance(raw, dict):
        raise PrivacyError('invalid_telemetry')

    kept: list[tuple[str, str | int]] = []
    dropped = 0
    for key_name in sorted(raw.keys(), key=str):
        val = raw[key_name]
        if key_name in ALLOWED_TELEMETRY_ID_FIELDS:
            if type(val) is not str or not _IDENTIFIER.fullmatch(val):
                dropped += 1
                continue
            kept.append((key_name, val))
        elif key_name == 'occurred_at':
            iso_val = _parse_iso_utc(val)
            if iso_val is None:
                dropped += 1
                continue
            kept.append((key_name, iso_val))
        elif key_name in ALLOWED_TELEMETRY_INT_FIELDS:
            if type(val) is not int or val < 0:
                dropped += 1
                continue
            kept.append((key_name, val))
        else:
            dropped += 1

    return SanitizedTelemetry(fields=tuple(kept), dropped_field_count=dropped)


def _validate_tombstone(t: DeletionTombstone) -> tuple[str, datetime]:
    if not isinstance(t, DeletionTombstone):
        raise PrivacyError('invalid_tombstone')
    _check_id(t.tombstone_id, code='invalid_tombstone')
    _check_id(t.tenant_id, code='invalid_tombstone')
    _check_id(t.learner_id, code='invalid_tombstone')
    _check_id(t.reason_code, code='invalid_tombstone')
    if not _is_non_model_authority(t.authority_ref):
        raise PrivacyError('invalid_tombstone')
    if type(t.target_kind) is not str or t.target_kind not in ALLOWED_TOMBSTONE_KINDS:
        raise PrivacyError('invalid_tombstone')
    if t.target_kind == 'learner_all':
        if t.target_id is not None:
            raise PrivacyError('invalid_tombstone')
    else:
        _check_id(t.target_id, code='invalid_tombstone')
    deleted_utc = _to_utc(t.deleted_at, code='invalid_tombstone')
    payload = {
        'tombstone_id': t.tombstone_id,
        'tenant_id': t.tenant_id,
        'learner_id': t.learner_id,
        'target_kind': t.target_kind,
        'target_id': t.target_id,
        'deleted_at': deleted_utc.isoformat(),
        'reason_code': t.reason_code,
        'authority_ref': t.authority_ref,
    }
    digest = sha256(json.dumps(payload, sort_keys=True, separators=(',', ':')).encode('utf-8')).hexdigest()
    return digest, deleted_utc


def _validate_record(rec: RestorableRecord) -> datetime:
    if not isinstance(rec, RestorableRecord):
        raise PrivacyError('invalid_record')
    _check_id(rec.record_id, code='invalid_record')
    _check_id(rec.tenant_id, code='invalid_record')
    _check_id(rec.learner_id, code='invalid_record')
    if type(rec.record_kind) is not str or rec.record_kind not in ALLOWED_RECORD_KINDS:
        raise PrivacyError('invalid_record')
    if (rec.target_kind is None) != (rec.target_id is None):
        raise PrivacyError('invalid_record')
    if rec.target_kind is not None:
        if type(rec.target_kind) is not str or rec.target_kind not in SCOPED_TARGET_KINDS:
            raise PrivacyError('invalid_record')
        _check_id(rec.target_id, code='invalid_record')
        if rec.record_kind in SCOPED_TARGET_KINDS and rec.target_kind != rec.record_kind:
            raise PrivacyError('invalid_record')
    elif rec.record_kind in SCOPED_TARGET_KINDS:
        raise PrivacyError('invalid_record')
    return _to_utc(rec.created_at, code='invalid_record')


def replay_deletion_tombstones(
    records: list[RestorableRecord] | tuple[RestorableRecord, ...],
    tombstones: list[DeletionTombstone] | tuple[DeletionTombstone, ...],
) -> TombstoneReplayReport:
    """Deterministically purge restored records covered by deletion tombstones."""
    if not isinstance(records, (list, tuple)) or not isinstance(tombstones, (list, tuple)):
        raise PrivacyError('invalid_input')

    # Deduplicate tombstones idempotently and fail closed on conflicting duplicates.
    dedup_tombstones: dict[str, tuple[str, datetime, DeletionTombstone]] = {}
    for tomb in tombstones:
        digest, deleted_utc = _validate_tombstone(tomb)
        if tomb.tombstone_id in dedup_tombstones:
            if dedup_tombstones[tomb.tombstone_id][0] != digest:
                raise PrivacyError('conflicting_tombstone')
            continue
        dedup_tombstones[tomb.tombstone_id] = (digest, deleted_utc, tomb)

    ordered_tombstones = sorted(
        dedup_tombstones.values(),
        key=lambda item: (item[1], item[2].tombstone_id),
    )

    seen_record_ids: set[str] = set()
    validated_records: list[tuple[RestorableRecord, datetime]] = []
    for rec in records:
        created_utc = _validate_record(rec)
        if rec.record_id in seen_record_ids:
            raise PrivacyError('duplicate_record')
        seen_record_ids.add(rec.record_id)
        validated_records.append((rec, created_utc))

    validated_records.sort(key=lambda pair: (pair[1], pair[0].record_id))

    retained: list[str] = []
    purged: list[str] = []

    for rec, created_utc in validated_records:
        should_purge = False
        for _, deleted_utc, tomb in ordered_tombstones:
            if rec.tenant_id != tomb.tenant_id or rec.learner_id != tomb.learner_id:
                continue
            if created_utc > deleted_utc:
                continue
            if tomb.target_kind == 'learner_all':
                should_purge = True
                break
            if rec.target_kind == tomb.target_kind and rec.target_id == tomb.target_id:
                should_purge = True
                break
        if should_purge:
            purged.append(rec.record_id)
        else:
            retained.append(rec.record_id)

    replay_payload = {
        'tombstones': [item[2].tombstone_id for item in ordered_tombstones],
        'purged': purged,
        'retained': retained,
    }
    replay_digest = sha256(json.dumps(replay_payload, sort_keys=True, separators=(',', ':')).encode('utf-8')).hexdigest()

    return TombstoneReplayReport(
        retained_record_ids=tuple(retained),
        purged_record_ids=tuple(purged),
        applied_tombstone_count=len(ordered_tombstones),
        replay_digest=replay_digest,
    )
