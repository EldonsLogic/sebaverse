"""Offline checks of the text comparator using authored, non-PDF controls."""

import hashlib
import json
import unicodedata
from pathlib import Path

import pytest

from evals.extraction_fidelity import compare_extraction
from modules.ingestion.contracts import validate_result


REFERENCE_PATH = Path(__file__).resolve().parents[3] / "evals/fixtures/extraction-reference-v1.json"
TEXT_CASE = "arabic-german-math-v1"
HOLD_CASE = "readable-prefix-unreadable-page-v1"
PRIVATE_MARKER = "authored private text marker"


@pytest.fixture
def references():
    vectors = json.loads(REFERENCE_PATH.read_text(encoding="utf-8"))
    assert vectors["source_binding_status"] == "pending_reviewed_pdf_mapping"
    return {case["reference"]["fixture_id"]: case["reference"] for case in vectors["cases"]}


def control_provenance(fixture_id):
    # The digest binds an authored test marker. Future runs supply the reviewed PDF's hash.
    source_marker = f"non-PDF fidelity control/{fixture_id}".encode("ascii")
    return {
        "object_id": "11111111-1111-4111-8111-111111111111",
        "source_sha256": hashlib.sha256(source_marker).hexdigest(),
        "generation": 3,
        "dispatch_id": "22222222-2222-4222-8222-222222222222",
        "parser_id": "offline-authored-control-v1",
        "media_type": "application/pdf",
    }


def result_for(reference, binding):
    return {
        **binding,
        "page_count": len(reference["pages"]),
        "quality": "needs_review",
        "blocks": [
            {"page": number, "anchor": f"authored-{number}", "text": page["text"]}
            for number, page in enumerate(reference["pages"], start=1)
            if page["text"]
        ],
    }


def check(reference, candidate, binding):
    return compare_extraction(reference, candidate, expected_provenance=binding)


def assert_issue(report, code, page=None):
    assert report.matches is False
    assert (code, page) in {(issue.code, issue.page) for issue in report.diagnostics}


def test_exact_authored_result_matches(references):
    reference = references[TEXT_CASE]
    binding = control_provenance(TEXT_CASE)
    report = check(reference, result_for(reference, binding), binding)
    assert report.matches is True
    assert report.diagnostics == ()


def test_split_blocks_preserve_text_and_explicit_crlf_variation(references):
    reference = references[TEXT_CASE]
    binding = control_provenance(TEXT_CASE)
    candidate = result_for(reference, binding)
    first, second = candidate["blocks"][0]["text"].split("\n", 1)
    # Deliberately split CRLF across blocks, and split a grapheme in the second line.
    assert second.startswith("قِ")
    candidate["blocks"][0:1] = [
        {"page": 1, "anchor": "first-fragment", "text": first + "\r"},
        {"page": 1, "anchor": "second-fragment", "text": "\n" + second[:1]},
        {"page": 1, "anchor": "third-fragment", "text": second[1:]},
    ]
    assert check(reference, candidate, binding).matches is True
    assert_issue(check({**reference, "line_endings": "exact"}, candidate, binding), "text_mismatch", 1)


@pytest.mark.parametrize("replacement", ["\r", "\n ", "\n\n"], ids=["bare-cr", "space", "extra-line"])
def test_lf_policy_rejects_other_whitespace_changes(references, replacement):
    reference = references[TEXT_CASE]
    binding = control_provenance(TEXT_CASE)
    candidate = result_for(reference, binding)
    first_block = candidate["blocks"][0]
    first_block["text"] = first_block["text"].replace("\n", replacement, 1)
    assert_issue(check(reference, candidate, binding), "text_mismatch", 1)


def test_swapped_bilingual_columns_fail_with_all_tokens_present(references):
    reference = references[TEXT_CASE]
    binding = control_provenance(TEXT_CASE)
    candidate = result_for(reference, binding)
    second_block = candidate["blocks"][1]
    lines = second_block["text"].splitlines()
    second_block["text"] = "\n".join(lines[2:] + lines[:2])
    validate_result(candidate, binding)
    report = check(reference, candidate, binding)
    assert_issue(report, "text_mismatch", 2)
    assert_issue(report, "critical_notation_mismatch", 2)


@pytest.mark.parametrize(
    "token,replacement",
    [
        pytest.param("−", "-", id="ascii-minus"),
        pytest.param("−", " ", id="missing-negative-sign"),
        pytest.param("٫", ".", id="ascii-decimal-separator"),
        pytest.param("٫", " ", id="missing-decimal-separator"),
        pytest.param("²", "2", id="flattened-exponent"),
        pytest.param("²", " ", id="missing-exponent"),
        pytest.param("٣", "3", id="ascii-digit"),
    ],
)
def test_meaning_changing_notation_mutations_pass_schema_but_fail_fidelity(references, token, replacement):
    reference = references[TEXT_CASE]
    binding = control_provenance(TEXT_CASE)
    candidate = result_for(reference, binding)
    math_block = candidate["blocks"][2]
    original = math_block["text"]
    assert original.count(token) == 1
    math_block["text"] = original.replace(token, replacement)
    assert len(math_block["text"]) == len(original)
    validate_result(candidate, binding)
    assert_issue(check(reference, candidate, binding), "critical_notation_mismatch", 3)


def test_swapped_digits_fail_even_when_critical_symbol_counts_match(references):
    reference = references[TEXT_CASE]
    binding = control_provenance(TEXT_CASE)
    candidate = result_for(reference, binding)
    math_block = candidate["blocks"][2]
    math_block["text"] = math_block["text"].replace("٣٫٥", "٥٫٣")
    validate_result(candidate, binding)
    assert_issue(check(reference, candidate, binding), "critical_notation_mismatch", 3)


def test_one_critical_token_cannot_mask_loss_of_an_overlapping_token():
    fixture_id = "overlapping-token-control-v1"
    reference = {
        "fixture_id": fixture_id,
        "expected_outcome": "needs_review",
        "line_endings": "exact",
        "pages": [{"text": "ABAAX", "critical_tokens": ["ABA", "BAA"]}],
    }
    binding = control_provenance(fixture_id)
    candidate = result_for(reference, binding)
    candidate["blocks"][0]["text"] = "ABAXX"
    validate_result(candidate, binding)
    assert_issue(check(reference, candidate, binding), "critical_notation_mismatch", 1)


def test_canonically_equivalent_unicode_still_differs_from_authored_text(references):
    reference = references[TEXT_CASE]
    binding = control_provenance(TEXT_CASE)
    candidate = result_for(reference, binding)
    second_block = candidate["blocks"][1]
    original = second_block["text"]
    decomposed = unicodedata.normalize("NFD", original)
    assert original != decomposed
    assert unicodedata.normalize("NFC", decomposed) == original
    second_block["text"] = decomposed
    validate_result(candidate, binding)
    report = check(reference, candidate, binding)
    assert report.matches is False
    assert any(issue.page == 2 for issue in report.diagnostics)


def test_missing_page_fails_even_with_declared_page_count_intact(references):
    reference = references[TEXT_CASE]
    binding = control_provenance(TEXT_CASE)
    candidate = result_for(reference, binding)
    del candidate["blocks"][1]
    validate_result(candidate, binding)
    assert_issue(check(reference, candidate, binding), "page_missing", 2)


def test_in_range_page_count_that_omits_final_page_fails(references):
    reference = references[TEXT_CASE]
    binding = control_provenance(TEXT_CASE)
    candidate = result_for(reference, binding)
    candidate["blocks"].pop()
    candidate["page_count"] -= 1
    validate_result(candidate, binding)
    assert_issue(check(reference, candidate, binding), "page_count_mismatch")


def test_out_of_order_pages_fail_even_with_correct_page_labels(references):
    reference = references[TEXT_CASE]
    binding = control_provenance(TEXT_CASE)
    candidate = result_for(reference, binding)
    candidate["blocks"].reverse()
    validate_result(candidate, binding)
    report = check(reference, candidate, binding)
    assert report.matches is False
    assert "page_order_mismatch" in {issue.code for issue in report.diagnostics}


def test_duplicate_anchors_fail_even_with_correct_text(references):
    reference = references[TEXT_CASE]
    binding = control_provenance(TEXT_CASE)
    candidate = result_for(reference, binding)
    candidate["blocks"][1]["anchor"] = candidate["blocks"][0]["anchor"]
    assert_issue(check(reference, candidate, binding), "invalid_result")


@pytest.mark.parametrize(
    "field,value",
    [
        ("source_sha256", "0" * 64),
        ("object_id", "33333333-3333-4333-8333-333333333333"),
        ("dispatch_id", "44444444-4444-4444-8444-444444444444"),
        ("generation", 4),
        ("parser_id", "different-offline-control-v1"),
        ("media_type", "image/png"),
    ],
)
def test_candidate_cannot_rebind_independent_expected_identity(references, field, value):
    reference = references[TEXT_CASE]
    binding = control_provenance(TEXT_CASE)
    candidate = result_for(reference, binding)
    candidate[field] = value
    assert_issue(check(reference, candidate, binding), "provenance_mismatch")


def test_missing_expected_source_binding_is_rejected(references):
    reference = references[TEXT_CASE]
    binding = control_provenance(TEXT_CASE)
    candidate = result_for(reference, binding)
    del binding["source_sha256"]
    assert_issue(check(reference, candidate, binding), "invalid_provenance")


def test_missing_critical_token_in_reference_is_rejected(references):
    reference = references[TEXT_CASE]
    binding = control_provenance(TEXT_CASE)
    candidate = result_for(reference, binding)
    reference["pages"][2]["critical_tokens"].append(PRIVATE_MARKER)
    report = check(reference, candidate, binding)
    assert_issue(report, "invalid_reference")
    assert PRIVATE_MARKER not in repr(report)


def test_partial_unreadable_document_requires_the_explicit_matching_hold(references):
    reference = references[HOLD_CASE]
    binding = control_provenance(HOLD_CASE)
    partial = result_for(reference, binding)
    validate_result(partial, binding)
    assert_issue(check(reference, partial, binding), "unexpected_result")
    assert_issue(check(reference, None, binding), "invalid_result")

    hold = {"hold_reason": "page_without_text", "provenance": dict(binding)}
    report = check(reference, hold, binding)
    assert report.matches is True
    assert report.diagnostics == ()
    assert_issue(check(reference, {**hold, "hold_reason": "deadline_exceeded"}, binding), "hold_reason_mismatch")
    hold["provenance"]["source_sha256"] = control_provenance(TEXT_CASE)["source_sha256"]
    assert_issue(check(reference, hold, binding), "provenance_mismatch")


def test_readable_document_cannot_pass_by_holding(references):
    reference = references[TEXT_CASE]
    binding = control_provenance(TEXT_CASE)
    hold = {"hold_reason": "page_without_text", "provenance": dict(binding)}
    assert_issue(check(reference, hold, binding), "unexpected_hold")


def test_candidate_content_is_absent_from_bounded_diagnostics(references):
    reference = references[TEXT_CASE]
    binding = control_provenance(TEXT_CASE)
    candidate = result_for(reference, binding)
    candidate["blocks"][0]["text"] = PRIVATE_MARKER * 30
    validate_result(candidate, binding)
    report = check(reference, candidate, binding)
    assert report.matches is False
    assert report.diagnostics
    assert PRIVATE_MARKER not in repr(report)
    assert len(repr(report)) < 500

    candidate["blocks"][0]["text"] = PRIVATE_MARKER * 10000
    report = check(reference, candidate, binding)
    assert_issue(report, "invalid_result")
    assert PRIVATE_MARKER not in repr(report)
    assert len(repr(report)) < 500
