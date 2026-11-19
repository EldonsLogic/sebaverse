"""Offline digital-PDF extraction core for a qualified worker composition.

The soft deadline checks calls that return. A parent watchdog must enforce the
hard process, CPU, memory and output limits, including a stalled native call.
"""

import hashlib
import hmac
import re
import time
from contextlib import contextmanager
from uuid import UUID

from modules.ingestion.contracts import (
    MAX_BYTES,
    MAX_OUTPUT,
    MAX_PAGES,
    MAX_TEXT,
    canonical,
    detect_type,
    integer,
    validate_result,
    verify_manifest,
)

PARSER_ID = "pypdfium2-5.15.2-pdfium-159.0.8149.0-text-v1"
WHEEL_SHA256 = "dc31aea5b0fb9fefc9b537a65f4113980b2c40798445736a7e6565bc85161e37"

_PDF = "application/pdf"
_SHA256 = re.compile(r"[0-9a-f]{64}")
_SCANNER_ID = re.compile(r"[A-Za-z0-9._-]{1,96}")
_PROVENANCE = ("object_id", "source_sha256", "generation", "dispatch_id", "parser_id", "media_type")
_EXPECTED = set(_PROVENANCE) | {"byte_count", "scope_digest"}
_CHUNK_CHARS = 2000
_MAX_BLOCKS = 1000
_SOFT_TIMEOUT = 10


class ExtractionError(ValueError):
    """Extraction held with a bounded, content-free reason code."""


class RuntimeUnavailable(ExtractionError):
    """The isolated composition has no qualified document factory."""


def _matches(pattern, value):
    return type(value) is str and pattern.fullmatch(value) is not None


def _validated_expected(expected):
    if type(expected) is not dict or len(expected) != len(_EXPECTED) or expected.keys() != _EXPECTED:
        raise ExtractionError("invalid_expected")
    expected = dict(expected)
    for field in ("object_id", "dispatch_id"):
        value = expected[field]
        if type(value) is not str or len(value) != 36:
            raise ExtractionError("invalid_expected")
        try:
            normalized = str(UUID(value))
        except ValueError:
            raise ExtractionError("invalid_expected") from None
        if normalized != value:
            raise ExtractionError("invalid_expected")
    if not all(_matches(_SHA256, expected[field]) for field in ("source_sha256", "scope_digest")):
        raise ExtractionError("invalid_expected")
    if type(expected["parser_id"]) is not str or expected["parser_id"] != PARSER_ID:
        raise ExtractionError("invalid_expected")
    if type(expected["media_type"]) is not str or expected["media_type"] != _PDF:
        raise ExtractionError("invalid_expected")
    try:
        integer(expected["byte_count"], 1, MAX_BYTES)
        integer(expected["generation"], 1, 2**31 - 1)
    except ValueError:
        raise ExtractionError("invalid_expected") from None
    return expected


def _same_signing_key(job_key, scan_key):
    # HMAC compares the effective keys, including any hashing or zero padding.
    marker = b"sebaverse-digital-pdf-key-separation-v1"
    return hmac.compare_digest(
        hmac.digest(job_key, marker, "sha256"), hmac.digest(scan_key, marker, "sha256")
    )


def _verify(envelope, key, expected, now, error_code):
    # The shared verifier canonicalizes the payload to check its HMAC. Bound
    # it to known scalar values before allowing serialization of untrusted data.
    if type(envelope) is not dict or len(envelope) != 2 or envelope.keys() != {"payload", "signature"}:
        raise ExtractionError(error_code)
    payload = envelope["payload"]
    if type(payload) is not dict or len(payload) != len(expected) + 1:
        raise ExtractionError(error_code)
    if payload.keys() != expected.keys() | {"expires_at"} or not _matches(_SHA256, envelope["signature"]):
        raise ExtractionError(error_code)
    for field, value in expected.items():
        supplied = payload[field]
        if type(supplied) is not type(value) or supplied != value:
            raise ExtractionError(error_code)
    try:
        integer(payload["expires_at"], now + 1, now + 120)
        verify_manifest(envelope, key, expected, now)
    except ValueError:
        raise ExtractionError(error_code) from None


def _native_call(operation, error_code="native_failure"):
    try:
        return operation()
    except Exception:
        # Raise outside the exception handler so the native error is not attached.
        pass
    raise ExtractionError(error_code)


def _timed_call(operation, check_deadline):
    check_deadline()
    result = _native_call(operation)
    check_deadline()
    return result


@contextmanager
def _resource(open_resource, check_deadline):
    check_deadline()
    resource = _native_call(open_resource)
    try:
        # Check inside the cleanup scope. Opening may itself run past the limit.
        check_deadline()
        yield resource
    finally:
        try:
            check_deadline()
        finally:
            _native_call(lambda: resource.close(), "cleanup_failed")
        check_deadline()


def _extract(document, check_deadline):
    # Read the uncoerced native count. len() would coerce a bool or int subclass.
    page_count = _timed_call(lambda: document.__len__(), check_deadline)
    if type(page_count) is not int or not 1 <= page_count <= MAX_PAGES:
        raise ExtractionError("invalid_page_count")

    blocks = []
    total_chars = 0
    for page_index in range(page_count):
        with _resource(lambda: document.get_page(page_index), check_deadline) as page:
            with _resource(lambda: page.get_textpage(), check_deadline) as textpage:
                count = _timed_call(lambda: textpage.count_chars(), check_deadline)
                if type(count) is not int or not 0 <= count <= MAX_TEXT - total_chars:
                    raise ExtractionError("invalid_character_count")
                total_chars += count
                page_has_text = False
                for offset in range(0, count, _CHUNK_CHARS):
                    if len(blocks) >= _MAX_BLOCKS:
                        raise ExtractionError("too_many_blocks")
                    chunk_count = min(_CHUNK_CHARS, count - offset)
                    text = _timed_call(
                        lambda: textpage.get_text_range(index=offset, count=chunk_count, errors="strict"),
                        check_deadline,
                    )
                    # This UCS-2-limited SDK method can return unequal lengths
                    # for native range mappings. Hold the page if preservation is uncertain.
                    if type(text) is not str or len(text) != chunk_count:
                        raise ExtractionError("unpreserved_text_range")
                    page_has_text = page_has_text or not text.isspace()
                    blocks.append({"page": page_index + 1, "anchor": f"p{page_index + 1}-c{offset}", "text": text})
                if not page_has_text:
                    raise ExtractionError("page_without_text")
    return page_count, blocks


def run_job(
    data, envelope, job_key, expected, scan_envelope, scan_key, scanner_id, *,
    document_factory=None, now=None, clock=time.monotonic,
):
    """Verify the source, job and clean scan before opening a document."""
    deadline = clock() + _SOFT_TIMEOUT

    def check_deadline():
        if clock() >= deadline:
            raise ExtractionError("deadline_exceeded")

    expected = _validated_expected(expected)
    if any(type(key) is not bytes or len(key) < 32 for key in (job_key, scan_key)):
        raise ExtractionError("invalid_keys")
    if _same_signing_key(job_key, scan_key):
        raise ExtractionError("invalid_keys")
    if not _matches(_SCANNER_ID, scanner_id):
        raise ExtractionError("invalid_scanner")
    timestamp = int(time.time() if now is None else now)
    _verify(envelope, job_key, expected, timestamp, "invalid_job")
    _verify(scan_envelope, scan_key, {**expected, "scanner_id": scanner_id, "status": "clean"}, timestamp, "invalid_scan")

    if type(data) is not bytes or len(data) != expected["byte_count"]:
        raise ExtractionError("source_size_mismatch")
    try:
        detect_type(data, _PDF)
    except ValueError:
        raise ExtractionError("source_type_mismatch") from None
    if not hmac.compare_digest(hashlib.sha256(data).hexdigest(), expected["source_sha256"]):
        raise ExtractionError("source_hash_mismatch")
    if document_factory is None:
        raise RuntimeUnavailable("runtime_unavailable")

    with _resource(lambda: document_factory(data), check_deadline) as document:
        page_count, blocks = _extract(document, check_deadline)
    result = {field: expected[field] for field in _PROVENANCE}
    result.update(page_count=page_count, quality="needs_review", blocks=blocks)
    try:
        output_size = len(canonical(result))
    except ValueError:
        raise ExtractionError("invalid_result") from None
    if output_size > MAX_OUTPUT:
        raise ExtractionError("output_too_large")
    try:
        validate_result(result, expected)
    except ValueError:
        raise ExtractionError("invalid_result") from None
    check_deadline()
    return result
