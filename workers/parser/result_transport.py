"""Strict wire decoding for bounded, untrusted parser output."""

import json

from modules.ingestion.contracts import MAX_OUTPUT, MIMES, integer, validate_result

_TEXT_BOUNDS = {
    "object_id": (36, 36),
    "source_sha256": (64, 64),
    "dispatch_id": (36, 36),
    "parser_id": (1, 96),
    "media_type": (1, 96),
}


class ResultTransportError(ValueError):
    """Malformed or mismatched worker output held for the current job."""


def _snapshot_provenance(expected):
    if type(expected) is not dict:
        raise ValueError
    binding = {field: expected[field] for field in _TEXT_BOUNDS}
    for field, (minimum, maximum) in _TEXT_BOUNDS.items():
        value = binding[field]
        if type(value) is not str or not minimum <= len(value) <= maximum:
            raise ValueError
    if binding["media_type"] not in MIMES:
        raise ValueError
    generation = expected["generation"]
    integer(generation, 1, 2**31 - 1)
    binding["generation"] = generation
    return binding


def _unique_members(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError
        result[key] = value
    return result


def _bounded_integer(token):
    # The result schema's largest integer is a signed 32-bit generation.
    # Reject oversized numerals before invoking Python's integer conversion.
    if len(token) > 11:
        raise ValueError
    return int(token)


def _reject_number(_token):
    raise ValueError


def decode_result(output: bytes, expected: dict) -> dict:
    """Decode one bounded result against a caller-owned job binding."""
    if type(output) is not bytes or len(output) > MAX_OUTPUT:
        raise ResultTransportError("invalid_worker_output")

    try:
        binding = _snapshot_provenance(expected)
        result = json.loads(
            output.decode("utf-8", errors="strict"),
            object_pairs_hook=_unique_members,
            parse_int=_bounded_integer,
            parse_float=_reject_number,
            parse_constant=_reject_number,
        )
        return validate_result(result, binding)
    except (KeyError, RecursionError, ValueError):
        # Raise outside the handler so decoding errors cannot attach source text.
        pass
    raise ResultTransportError("invalid_worker_output")
