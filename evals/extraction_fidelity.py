"""Compare an authored reference to one captured extraction outcome offline."""

import re
from dataclasses import dataclass
from itertools import zip_longest
from uuid import UUID

from modules.ingestion.contracts import MAX_PAGES, MAX_TEXT, MIMES, validate_result

_PROVENANCE_FIELDS = {"object_id", "source_sha256", "generation", "dispatch_id", "parser_id", "media_type"}
_RESULT_FIELDS = _PROVENANCE_FIELDS | {"page_count", "quality", "blocks"}
_REFERENCE_FIELDS = {"fixture_id", "expected_outcome", "line_endings", "pages"}
_HOLD_FIELDS = {"hold_reason", "provenance"}
_MAX_BLOCKS = 1000
_MAX_BLOCK_TEXT = 2000
_MAX_CRITICAL_TOKENS = 16
_MAX_TOKEN_TEXT = 64


@dataclass(frozen=True)
class FidelityDiagnostic:
    code: str
    page: int | None = None


@dataclass(frozen=True)
class FidelityReport:
    diagnostics: tuple[FidelityDiagnostic, ...]

    @property
    def matches(self) -> bool:
        return not self.diagnostics


def _has_fields(value, fields):
    return type(value) is dict and len(value) == len(fields) and value.keys() == fields


def _matches(pattern, value, maximum):
    return type(value) is str and len(value) <= maximum and re.fullmatch(pattern, value) is not None


def _bounded_integer(value, maximum):
    return type(value) is int and 1 <= value <= maximum


def _valid_uuid(value):
    if type(value) is not str or len(value) != 36:
        return False
    try:
        return str(UUID(value)) == value
    except ValueError:
        return False


def _valid_provenance(value):
    return (
        _valid_uuid(value["object_id"])
        and _valid_uuid(value["dispatch_id"])
        and _matches(r"[0-9a-f]{64}", value["source_sha256"], 64)
        and _bounded_integer(value["generation"], 2**31 - 1)
        and _matches(r"[A-Za-z0-9._-]{1,96}", value["parser_id"], 96)
        and type(value["media_type"]) is str
        and len(value["media_type"]) <= 96
        and value["media_type"] in MIMES
    )


def _valid_text(value, maximum):
    return type(value) is str and len(value) <= maximum and all(
        (ord(char) >= 32 or char in "\r\n\t") and not 0xD800 <= ord(char) <= 0xDFFF
        for char in value
    )


def _valid_reference(reference):
    if type(reference) is not dict:
        return False
    outcome = reference.get("expected_outcome")
    if type(outcome) is not str or len(outcome) > 12 or outcome not in ("hold", "needs_review"):
        return False
    held = outcome == "hold"
    fields = _REFERENCE_FIELDS | {"hold_reason"} if held else _REFERENCE_FIELDS
    if not _has_fields(reference, fields):
        return False
    if held and (
        type(reference["hold_reason"]) is not str or reference["hold_reason"] != "page_without_text"
    ):
        return False
    if not _matches(r"[a-z0-9][a-z0-9._-]{0,63}", reference["fixture_id"], 64):
        return False
    mode = reference["line_endings"]
    if type(mode) is not str or len(mode) > 13 or mode not in ("exact", "lf_equivalent"):
        return False
    pages = reference["pages"]
    if type(pages) is not list or not 1 <= len(pages) <= MAX_PAGES:
        return False

    remaining_text = MAX_TEXT
    for index, page in enumerate(pages):
        if not _has_fields(page, {"text", "critical_tokens"}):
            return False
        page_text, tokens = page["text"], page["critical_tokens"]
        if not _valid_text(page_text, remaining_text):
            return False
        remaining_text -= len(page_text)
        if type(tokens) is not list or len(tokens) > _MAX_CRITICAL_TOKENS:
            return False
        if held and index == len(pages) - 1:
            return page_text == "" and not tokens
        if not page_text.strip():
            return False
        if any(
            not _valid_text(token, _MAX_TOKEN_TEXT) or not token.strip()
            or "\r" in token or "\n" in token or token not in page_text
            for token in tokens
        ) or len(tokens) != len(set(tokens)):
            return False
    return True


def _valid_result_shape(result):
    """Bound data before the shared validator canonicalizes a result."""
    if not _has_fields(result, _RESULT_FIELDS) or not _valid_provenance(result):
        return False
    if not _bounded_integer(result["page_count"], MAX_PAGES):
        return False
    if type(result["quality"]) is not str or result["quality"] != "needs_review":
        return False
    blocks = result["blocks"]
    if type(blocks) is not list or not 1 <= len(blocks) <= _MAX_BLOCKS:
        return False

    remaining_text = MAX_TEXT
    for block in blocks:
        if not _has_fields(block, {"page", "anchor", "text"}):
            return False
        if not _bounded_integer(block["page"], result["page_count"]):
            return False
        if not _matches(r"[a-z0-9._-]{1,64}", block["anchor"], 64):
            return False
        if not _valid_text(block["text"], min(_MAX_BLOCK_TEXT, remaining_text)) or not block["text"]:
            return False
        remaining_text -= len(block["text"])
    return True


def _token_values(pattern, text):
    return (match.group(1) for match in pattern.finditer(text))


def _critical_tokens_match(tokens, reference_text, observed_text):
    if not tokens:
        return True
    # Check every start position, with the longest token first at a shared start.
    alternatives = "|".join(re.escape(token) for token in sorted(tokens, key=len, reverse=True))
    pattern = re.compile(f"(?=({alternatives}))")
    return all(
        expected == observed
        for expected, observed in zip_longest(
            _token_values(pattern, reference_text), _token_values(pattern, observed_text)
        )
    )


def _page_diagnostics(reference, result):
    diagnostics = []
    if result["page_count"] != len(reference["pages"]):
        diagnostics.append(FidelityDiagnostic("page_count_mismatch"))
    chunks = {}
    previous_page = 0
    found_order_error = False
    for block in result["blocks"]:
        page = block["page"]
        if page < previous_page and not found_order_error:
            diagnostics.append(FidelityDiagnostic("page_order_mismatch", page))
            found_order_error = True
        chunks.setdefault(page, []).append(block["text"])
        previous_page = page

    for page, expected in enumerate(reference["pages"], start=1):
        if page not in chunks:
            diagnostics.append(FidelityDiagnostic("page_missing", page))
            continue
        expected_text = expected["text"]
        observed_text = "".join(chunks[page])
        if reference["line_endings"] == "lf_equivalent":
            expected_text = expected_text.replace("\r\n", "\n")
            observed_text = observed_text.replace("\r\n", "\n")
        if expected_text != observed_text:
            diagnostics.append(FidelityDiagnostic("text_mismatch", page))
            if not _critical_tokens_match(expected["critical_tokens"], expected_text, observed_text):
                diagnostics.append(FidelityDiagnostic("critical_notation_mismatch", page))
    return tuple(diagnostics)


def _failure(code):
    return FidelityReport((FidelityDiagnostic(code),))


def compare_extraction(reference, candidate, *, expected_provenance) -> FidelityReport:
    """Evaluate one JSON-shaped outcome using an independent job binding."""
    if not _valid_reference(reference):
        return _failure("invalid_reference")
    if not _has_fields(expected_provenance, _PROVENANCE_FIELDS) or not _valid_provenance(expected_provenance):
        return _failure("invalid_provenance")

    if _has_fields(candidate, _HOLD_FIELDS):
        binding = candidate["provenance"]
        if not _has_fields(binding, _PROVENANCE_FIELDS) or not _valid_provenance(binding):
            return _failure("invalid_result")
        reason = candidate["hold_reason"]
        if not _matches(r"[a-z][a-z0-9_]{0,63}", reason, 64):
            return _failure("invalid_result")
        if binding != expected_provenance:
            return _failure("provenance_mismatch")
        if reference["expected_outcome"] != "hold":
            return _failure("unexpected_hold")
        if reason != reference["hold_reason"]:
            return _failure("hold_reason_mismatch")
        return FidelityReport(())

    if not _valid_result_shape(candidate):
        return _failure("invalid_result")
    if any(candidate[field] != expected_provenance[field] for field in _PROVENANCE_FIELDS):
        return _failure("provenance_mismatch")
    try:
        result = validate_result(candidate, expected_provenance)
    except ValueError:
        return _failure("invalid_result")
    if reference["expected_outcome"] == "hold":
        return _failure("unexpected_result")
    return FidelityReport(_page_diagnostics(reference, result))
