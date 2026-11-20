"""Bounded SDP1 stdin framing for the authored PDF worker fixture."""

import json

from modules.ingestion.contracts import MAX_BYTES, canonical

_MAGIC = b"SDP1"
_PREFIX_BYTES = 8
MAX_HEADER_BYTES = 4096
MAX_FRAME_BYTES = _PREFIX_BYTES + MAX_HEADER_BYTES + MAX_BYTES

_METADATA_FIELDS = {"expected", "job_envelope", "scan_envelope"}
_EXPECTED_FIELDS = {
    "object_id": str,
    "source_sha256": str,
    "generation": int,
    "dispatch_id": str,
    "parser_id": str,
    "media_type": str,
    "byte_count": int,
    "scope_digest": str,
}
_JOB_FIELDS = _EXPECTED_FIELDS | {"expires_at": int}
_SCAN_FIELDS = _JOB_FIELDS | {"scanner_id": str, "status": str}


class InputTransportError(ValueError):
    """Malformed or oversized worker input held without source details."""


def _unique_members(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError
        result[key] = value
    return result


def _bounded_integer(token):
    # Reject long numerals before conversion. Validate the value separately.
    if len(token.removeprefix("-")) > 19:
        raise ValueError
    return int(token)


def _reject_number(_token):
    raise ValueError


def _validate_string(value):
    if type(value) is not str or len(value) > MAX_HEADER_BYTES:
        raise ValueError
    value.encode("utf-8", errors="strict")


def _validate_fields(record, fields):
    if type(record) is not dict or record.keys() != fields.keys():
        raise ValueError
    for key, field_type in fields.items():
        value = record[key]
        if field_type is str:
            _validate_string(value)
        elif type(value) is not int or not -(2**63) <= value < 2**63:
            raise ValueError


def _validate_envelope(envelope, payload_fields):
    if type(envelope) is not dict or envelope.keys() != {"payload", "signature"}:
        raise ValueError
    _validate_fields(envelope["payload"], payload_fields)
    _validate_string(envelope["signature"])


def _validate_metadata(metadata):
    if type(metadata) is not dict or metadata.keys() != _METADATA_FIELDS:
        raise ValueError
    expected = metadata["expected"]
    _validate_fields(expected, _EXPECTED_FIELDS)
    _validate_envelope(metadata["job_envelope"], _JOB_FIELDS)
    _validate_envelope(metadata["scan_envelope"], _SCAN_FIELDS)
    size = expected["byte_count"]
    if not 1 <= size <= MAX_BYTES:
        raise ValueError
    return size


def encode_request(data, *, expected, job_envelope, scan_envelope) -> bytes:
    """Frame source bytes and metadata supplied by trusted fixture code."""
    metadata = {
        "expected": expected,
        "job_envelope": job_envelope,
        "scan_envelope": scan_envelope,
    }
    try:
        if type(data) is not bytes or len(data) != _validate_metadata(metadata):
            raise ValueError
        header = canonical(metadata)
        if len(header) > MAX_HEADER_BYTES:
            raise ValueError
        return b"".join((_MAGIC, len(header).to_bytes(4, "big"), header, data))
    except (KeyError, RecursionError, ValueError):
        pass
    raise InputTransportError("invalid_worker_input")


def _read_exact(stream, size):
    data = stream.read(size)
    if type(data) is not bytes or len(data) != size:
        raise ValueError
    return data


def read_request(stream) -> tuple[bytes, dict, dict, dict]:
    """Read one complete frame from a blocking buffered binary stream."""
    try:
        prefix = _read_exact(stream, _PREFIX_BYTES)
        header_size = int.from_bytes(prefix[4:], "big")
        if prefix[:4] != _MAGIC or not 1 <= header_size <= MAX_HEADER_BYTES:
            raise ValueError
        metadata = json.loads(
            _read_exact(stream, header_size).decode("utf-8", errors="strict"),
            object_pairs_hook=_unique_members,
            parse_int=_bounded_integer,
            parse_float=_reject_number,
            parse_constant=_reject_number,
        )
        data = _read_exact(stream, _validate_metadata(metadata))
        trailer = stream.read(1)
        if type(trailer) is not bytes or trailer:
            raise ValueError
        return data, metadata["expected"], metadata["job_envelope"], metadata["scan_envelope"]
    except (OSError, RecursionError, ValueError):
        # Raise outside the handler so a decoder error holding input cannot escape.
        pass
    raise InputTransportError("invalid_worker_input")
