"""Parser stdout decoding tests with authored local echo and synthetic inputs."""

import hashlib
import json
import os
import traceback

import pytest

from modules.ingestion.contracts import MAX_OUTPUT, canonical
from workers.parser import result_transport
from workers.parser.process_guard import WorkerLimits, run_worker

from .test_process_guard import assert_cleaned, authored_program, spawned


PRIVATE_MARKER = "synthetic-result-private-marker"
OTHER_ID = "33333333-3333-4333-8333-333333333333"


@pytest.fixture
def expected():
    return {
        "object_id": "11111111-1111-4111-8111-111111111111",
        "source_sha256": hashlib.sha256(b"authored fixture").hexdigest(),
        "generation": 1,
        "dispatch_id": "22222222-2222-4222-8222-222222222222",
        "parser_id": "fixture-parser.v1",
        "media_type": "application/pdf",
    }


def authored_result(expected):
    return {
        **expected, "page_count": 1, "quality": "needs_review",
        "blocks": [{"page": 1, "anchor": "p1.b1", "text": "ص = −٢٫٥ · Prüfe fu\u0308nf.\r\n"}],
    }


def reject(output, expected):
    with pytest.raises(result_transport.ResultTransportError) as caught:
        result_transport.decode_result(output, expected)
    assert str(caught.value) == "invalid_worker_output"
    assert PRIVATE_MARKER not in "".join(traceback.format_exception(caught.value))


@pytest.mark.skipif(os.name != "posix", reason="Process guard requires POSIX")
@pytest.mark.parametrize("poisoned", [False, True], ids=["exact-unicode", "ambiguous-quality"])
def test_real_authored_stdout_must_pass_broker_result_boundary(expected, authored_program, spawned, poisoned):
    fixture = authored_result(expected)
    wire = canonical(fixture)
    if poisoned:
        wire = b'{"quality":"approved",' + wire[1:]
    child = run_worker(b"echo\n" + wire, program=authored_program, limits=WorkerLimits(timeout_seconds=2))
    assert child.output == wire
    assert child.stderr_bytes == 0
    assert_cleaned(spawned)
    if poisoned:
        # Ordinary JSON decoding would discard the first member, hiding it from validation.
        assert json.loads(wire) == fixture
        reject(child.output, expected)
    else:
        assert result_transport.decode_result(child.output, expected) == fixture


def test_well_formed_object_allows_standard_json_whitespace(expected):
    fixture = authored_result(expected)
    wire = b" \r\n" + canonical(fixture) + b"\t\n"
    assert result_transport.decode_result(wire, expected) == fixture


@pytest.mark.parametrize("alternate_wire", [
    pytest.param(b"", id="empty"),
    pytest.param(b'{"text":"synthetic-result-private-marker\xff"}', id="invalid-utf8"),
    pytest.param(b'{"text":"synthetic-result-private-marker', id="truncated"),
    pytest.param(b"[" * 1200 + b"]" * 1200, id="excessive-depth"),
    pytest.param(b"null", id="non-object"),
    pytest.param("synthetic-result-private-marker", id="str-instead-of-bytes"),
    pytest.param(bytearray(b"{}"), id="mutable-bytes"),
])
def test_malformed_or_wrong_type_outputs_fail_closed(expected, alternate_wire):
    reject(alternate_wire, expected)


def test_non_utf8_wires_boms_and_extra_records_are_rejected(expected):
    wire = canonical(authored_result(expected))
    for bad_wire in (wire.decode().encode("utf-16"), b"\xef\xbb\xbf" + wire, wire + b"{}"):
        reject(bad_wire, expected)


def test_raw_output_byte_cap_precedes_json_parsing(expected, monkeypatch):
    def parsing_started(*args, **kwargs):
        pytest.fail("Oversized wire reached JSON parsing")

    monkeypatch.setattr(result_transport.json, "loads", parsing_started)
    raw = ("ع" * (MAX_OUTPUT // 2 + 1)).encode("utf-8")
    assert len(raw) > MAX_OUTPUT
    reject(raw, expected)


@pytest.mark.parametrize("member, duplicate", [
    pytest.param(b'"generation":1', b'"generation":1,"generation":1', id="identical-root"),
    pytest.param(b'"anchor":"p1.b1"', b'"anchor":"wrong-page","anchor":"p1.b1"', id="nested-anchor"),
])
def test_duplicate_keys_are_rejected_even_if_final_result_would_match(expected, member, duplicate):
    fixture = authored_result(expected)
    original = canonical(fixture)
    wire = original.replace(member, duplicate)
    assert wire != original and json.loads(wire) == fixture
    reject(wire, expected)


@pytest.mark.parametrize("constant", [b"NaN", b"Infinity", b"-Infinity"])
def test_nonfinite_constants_cannot_return_a_result(expected, constant):
    wire = canonical(authored_result(expected)).replace(b'"page_count":1', b'"page_count":' + constant)
    reject(wire, expected)


def test_surrogate_escape_and_unsafe_anchors_fail_without_echoing_text(expected):
    fixture = authored_result(expected)
    fixture["blocks"][0]["text"] = PRIVATE_MARKER + "\ud800"
    reject(json.dumps(fixture, ensure_ascii=True).encode("ascii"), expected)

    fixture = authored_result(expected)
    fixture["blocks"].append(fixture["blocks"][0].copy())
    reject(canonical(fixture), expected)
    fixture["blocks"][1]["anchor"] = "../other-artifact"
    reject(canonical(fixture), expected)


@pytest.mark.parametrize("field, replacement", [
    ("object_id", OTHER_ID),
    ("dispatch_id", OTHER_ID),
    ("generation", 2),
    ("source_sha256", "a" * 64),
    ("parser_id", "fixture-parser.other"),
    ("media_type", "image/png"),
    ("quality", "approved"),
])
def test_otherwise_valid_result_cannot_drift_from_broker_dispatch_or_grant_approval(expected, field, replacement):
    reject(canonical({**authored_result(expected), field: replacement}), expected)


@pytest.mark.parametrize("changed", [
    {"generation": True},
    {"object_id": {"untrusted": "nested"}},
    {"source_sha256": "a" * 65},
    {"parser_id": PRIVATE_MARKER * 100},
    {"media_type": "application/zip"},
])
def test_expected_binding_preflights_required_bounded_fields(expected, changed):
    reject(canonical(authored_result(expected)), {**expected, **changed})


def test_expected_job_extras_cannot_supply_missing_provenance_or_expand_output(expected):
    fixture = authored_result(expected)
    job_binding = {**expected, "byte_count": 123, "scope_digest": "a" * 64}
    assert result_transport.decode_result(canonical(fixture), job_binding) == fixture
    reject(canonical({**fixture, "scope_digest": job_binding["scope_digest"]}), job_binding)
    del job_binding["dispatch_id"]
    reject(canonical(fixture), job_binding)


def test_expected_dispatch_is_snapshotted_before_decoding(expected, monkeypatch):
    wire = canonical({**authored_result(expected), "dispatch_id": OTHER_ID})
    loads = result_transport.json.loads

    def load_after_dispatch_changes(*args, **kwargs):
        expected["dispatch_id"] = OTHER_ID
        return loads(*args, **kwargs)

    monkeypatch.setattr(result_transport.json, "loads", load_after_dispatch_changes)
    reject(wire, expected)
    assert expected["dispatch_id"] == OTHER_ID
