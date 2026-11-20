"""Strict parser stdin framing and guarded round trips with authored bytes."""

import hashlib
import io
import os
import signal
import subprocess
import sys
import time
import traceback
from pathlib import Path

import pytest

from modules.ingestion.contracts import MAX_BYTES, canonical, sign_manifest
from workers.parser.input_transport import InputTransportError, encode_request, read_request
from workers.parser.process_guard import WorkerError, WorkerLimits, WorkerProgram, run_worker
from workers.parser.result_transport import ResultTransportError, decode_result

from .fixtures import pdf_worker_fixture
from .test_digital_pdf import binding
from .test_process_guard import assert_cleaned, authored_program, spawned


HEADER_LIMIT = 4096
FRAME_LIMIT = 8 + HEADER_LIMIT + MAX_BYTES
PDF_PROFILE = "pdf_fixture_v1"
MARKER = "ص = −٢٫٥ · Prüfe fu\u0308nf."
PRIVATE_MARKER = "synthetic-input-private-marker"
OTHER_DISPATCH = "33333333-3333-4333-8333-333333333333"
PDF = b"%PDF-1.0\n" + MARKER.encode("utf-8")
POSIX_ONLY = pytest.mark.skipif(os.name != "posix", reason="Authored guard fixtures require POSIX")


def frame(header, data=b""):
    return b"SDP1" + len(header).to_bytes(4, "big") + header + data


def maximum_pdf():
    return PDF.replace(b"\n", b"\n" + b"x" * (MAX_BYTES - len(PDF) - 1) + b"\n", 1)


def request(data=PDF, *, expected=None, job_changes=None, scan_changes=None):
    expected = binding(data) if expected is None else expected
    expiry = {"expires_at": pdf_worker_fixture.NOW + 1}
    return {
        "expected": expected,
        "job_envelope": sign_manifest(
            {**expected, **expiry, **(job_changes or {})}, pdf_worker_fixture.JOB_KEY,
        ),
        "scan_envelope": sign_manifest({
            **expected, **expiry, "scanner_id": pdf_worker_fixture.SCANNER_ID,
            "status": "clean", **(scan_changes or {}),
        }, pdf_worker_fixture.SCAN_KEY),
    }


def padded_header(metadata):
    header = canonical(metadata)
    assert len(header) < HEADER_LIMIT
    return header.ljust(HEADER_LIMIT)


@pytest.fixture
def pdf_program():
    script = Path(pdf_worker_fixture.__file__).resolve()
    return WorkerProgram(sys.executable, script, hashlib.sha256(script.read_bytes()).hexdigest())


def run_pdf(wire, program, *, output_bytes=65536, error_bytes=4096):
    return run_worker(
        wire, program=program, input_profile=PDF_PROFILE,
        limits=WorkerLimits(
            timeout_seconds=3, input_bytes=FRAME_LIMIT,
            output_bytes=output_bytes, error_bytes=error_bytes,
        ),
    )


def assert_private(error, reason):
    assert str(error) == reason
    details = "".join(traceback.format_exception(error))
    for private in (
        PRIVATE_MARKER, MARKER, pdf_worker_fixture.JOB_KEY.decode().strip(),
        pdf_worker_fixture.SCAN_KEY.decode().strip(),
    ):
        assert private not in details
    assert error.__cause__ is None
    assert error.__context__ is None


def reject_read(stream):
    with pytest.raises(InputTransportError) as caught:
        read_request(stream)
    assert_private(caught.value, "invalid_worker_input")


@POSIX_ONLY
@pytest.mark.parametrize("maximum", [False, True], ids=["small", "exact-full-frame"])
def test_real_child_preserves_authored_source_and_provenance(pdf_program, spawned, maximum):
    data = maximum_pdf() if maximum else PDF
    server_expected = binding(data)
    metadata = request(data)
    wire = encode_request(data, **metadata)
    assert wire == frame(canonical(metadata), data)
    if maximum:
        wire = frame(padded_header(metadata), data)
        assert len(data) == MAX_BYTES
        assert len(wire) == FRAME_LIMIT

    child = run_pdf(wire, pdf_program)
    provenance = {
        key: value for key, value in server_expected.items() if key not in {"byte_count", "scope_digest"}
    }
    assert decode_result(child.output, server_expected) == {
        **provenance, "page_count": 1, "quality": "needs_review",
        "blocks": [{"page": 1, "anchor": "p1-c0", "text": MARKER}],
    }
    assert child.stderr_bytes == 0
    assert 0 <= child.elapsed_seconds < 3
    assert_cleaned(spawned)


@POSIX_ONLY
def test_larger_fixture_ceiling_requires_explicit_profile_and_rejects_overflow(pdf_program, spawned):
    data = maximum_pdf()
    metadata = request(data)
    wire = frame(padded_header(metadata), data)
    with pytest.raises(WorkerError) as caught:
        run_worker(wire, program=pdf_program, limits=WorkerLimits(input_bytes=1024 * 1024))
    assert_private(caught.value, "invalid_input")
    with pytest.raises(WorkerError) as caught:
        run_worker(wire, program=pdf_program, limits=WorkerLimits(input_bytes=FRAME_LIMIT))
    assert_private(caught.value, "invalid_limits")
    with pytest.raises(WorkerError) as caught:
        run_pdf(wire + b"x", pdf_program)
    assert_private(caught.value, "invalid_input")
    with pytest.raises(WorkerError) as caught:
        run_worker(
            b"", program=pdf_program, input_profile=PDF_PROFILE,
            limits=WorkerLimits(input_bytes=FRAME_LIMIT + 1),
        )
    assert_private(caught.value, "invalid_limits")
    with pytest.raises(WorkerError) as caught:
        run_worker(b"", program=pdf_program, input_profile="pdf_fixture_v2")
    assert_private(caught.value, "invalid_input_profile")
    assert spawned == []


def test_encoder_rejects_source_one_byte_over_ingress_limit():
    data = maximum_pdf() + b"x"
    with pytest.raises(InputTransportError) as caught:
        encode_request(data, **request(data))
    assert_private(caught.value, "invalid_worker_input")


def test_encoder_rejects_source_length_disagreement():
    with pytest.raises(InputTransportError) as caught:
        encode_request(PDF, **request(PDF + b"x"))
    assert_private(caught.value, "invalid_worker_input")


@pytest.mark.parametrize("prefix", [
    pytest.param(b"SDP2\x00\x00\x00\x01", id="unknown-version"),
    pytest.param(b"SDP1\x00\x00", id="partial-length"),
    pytest.param(b"SDP1\x00\x00\x00\x00", id="empty-header"),
    pytest.param(b"SDP1" + (HEADER_LIMIT + 1).to_bytes(4, "big"), id="oversized-header"),
])
def test_frame_prefix_rejected_before_header_or_body_read(prefix):
    stream = io.BytesIO(prefix)
    reads = []
    original = stream.read

    def record_read(size=-1):
        reads.append(size)
        return original(size)

    stream.read = record_read
    reject_read(stream)
    assert reads and all(0 < size <= 8 for size in reads)
    assert sum(reads) <= 8


@pytest.mark.parametrize("build_header", [
    pytest.param(lambda header: b'{"expected":null,' + header[1:], id="duplicate-root"),
    pytest.param(lambda header: header.replace(b'"generation":1', b'"generation":2,"generation":1', 1),
                 id="duplicate-nested"),
    pytest.param(lambda header: header.replace(b'"byte_count":' + str(len(PDF)).encode(), b'"byte_count":true', 1),
                 id="boolean-count"),
    pytest.param(lambda header: header.replace(b'"expires_at":101', b'"expires_at":101.0', 1), id="float-expiry"),
    pytest.param(lambda header: header.replace(b'"generation":1', b'"generation":NaN', 1), id="nonfinite-number"),
    pytest.param(lambda header: header.replace(b'"generation":1', b'"generation":' + b'9' * 100, 1),
                 id="oversized-number"),
    pytest.param(lambda header: b'{"invalid":"synthetic-input-private-marker\xff"}', id="invalid-utf8"),
    pytest.param(lambda header: header[:-1], id="truncated-json"),
    pytest.param(lambda header: b"[" * 1200 + b"]" * 1200, id="excessive-depth"),
    pytest.param(lambda header: header[:-1] + b',"input_profile":"pdf_fixture_v1"}', id="frame-selected-profile"),
])
def test_malformed_metadata_is_rejected_before_source_read(build_header):
    wire_header = canonical(request())
    invalid = build_header(wire_header)
    assert invalid != wire_header
    stream = io.BytesIO(frame(invalid, PDF))
    reject_read(stream)
    assert stream.tell() == 8 + len(invalid)


@pytest.mark.parametrize("source_tail", [PDF[:-1], PDF + b"x"], ids=["short", "trailing"])
def test_source_size_and_eof_are_required(source_tail):
    reject_read(io.BytesIO(frame(canonical(request()), source_tail)))


def test_reader_rejects_over_limit_claim_with_short_header_before_reading_body():
    expected = {**binding(PDF), "byte_count": MAX_BYTES + 1}
    header = canonical(request(expected=expected))
    stream = io.BytesIO(frame(header, PDF))
    reject_read(stream)
    assert stream.tell() == len(header) + 8


@POSIX_ONLY
@pytest.mark.parametrize("invalid", ["source-hash", "scan-job", "expired-job", "expired-scan"])
def test_semantic_rejections_produce_no_guarded_result(pdf_program, spawned, invalid):
    data = PDF[:-1] + b"x" if invalid == "source-hash" else PDF
    job_changes = {"expires_at": pdf_worker_fixture.NOW} if invalid == "expired-job" else {}
    scan_changes = {"expires_at": pdf_worker_fixture.NOW} if invalid == "expired-scan" else {}
    if invalid == "scan-job":
        scan_changes["dispatch_id"] = OTHER_DISPATCH
    wire = encode_request(data, **request(job_changes=job_changes, scan_changes=scan_changes))
    with pytest.raises(WorkerError) as caught:
        run_pdf(wire, pdf_program, output_bytes=0, error_bytes=0)
    assert_private(caught.value, "worker_failed")
    assert spawned[0][0].returncode == 2
    assert_cleaned(spawned)


@POSIX_ONLY
def test_fixture_rejects_malformed_input_with_empty_raw_output(pdf_program, tmp_path):
    child = subprocess.run(
        [str(Path(pdf_program.executable).resolve()), "-I", "-u", str(pdf_program.script)],
        input=frame(b'{"unexpected":"' + PRIVATE_MARKER.encode() + b'"}', PDF),
        capture_output=True, cwd=tmp_path, env={"LC_ALL": "C"}, timeout=3, check=False,
    )
    assert (child.returncode, child.stdout, child.stderr) == (2, b"", b"")


@POSIX_ONLY
def test_parent_provenance_cannot_be_replaced_by_another_valid_framed_job(pdf_program, spawned):
    job_a = binding(PDF)
    job_b = {**job_a, "dispatch_id": OTHER_DISPATCH}
    wire = encode_request(PDF, **request(expected=job_b))
    child = run_pdf(wire, pdf_program)
    assert decode_result(child.output, job_b)["dispatch_id"] == OTHER_DISPATCH
    with pytest.raises(ResultTransportError) as caught:
        decode_result(child.output, job_a)
    assert_private(caught.value, "invalid_worker_output")
    assert_cleaned(spawned)


@POSIX_ONLY
@pytest.mark.parametrize("cancel", [True, False], ids=["cancel", "deadline"])
def test_pdf_profile_stops_stalled_guarded_child_with_pending_input(authored_program, spawned, cancel):
    data = maximum_pdf()
    # This existing fixture signals readiness and stops reading after the mode line.
    payload = b"sleep\n" + encode_request(data, **request(data))
    ready = False

    def observe():
        nonlocal ready
        if spawned and (Path(spawned[0][2]["cwd"]) / "ready").is_file():
            ready = True
        return cancel and ready

    start = time.monotonic()
    with pytest.raises(WorkerError) as caught:
        run_worker(
            payload, program=authored_program, input_profile=PDF_PROFILE,
            limits=WorkerLimits(timeout_seconds=3 if cancel else 0.8, input_bytes=FRAME_LIMIT),
            cancelled=observe,
        )
    assert ready
    assert time.monotonic() - start < 3
    assert_private(caught.value, "worker_cancelled" if cancel else "worker_timeout")
    assert spawned[0][0].returncode == -signal.SIGKILL
    assert_cleaned(spawned)
