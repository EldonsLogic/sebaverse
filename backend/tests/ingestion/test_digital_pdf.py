"""Synthetic tests of the direct PDF adapter using an SDK-shaped fake engine."""

import hashlib
import subprocess
import sys
import traceback
from pathlib import Path

import pytest

from modules.ingestion import contracts
from modules.ingestion.contracts import MAX_BYTES, MAX_PAGES, MAX_TEXT, sign_manifest
from workers.parser import digital_pdf


PDF = b"%PDF-authored fixture"
JOB_KEY = b"j" * 32
SCAN_KEY = b"s" * 32
NOW = 100
SCANNER = "reviewed-scanner.v1"
OTHER_ID = "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"
PRIVATE_MARKER = "raw document detail must stay private"


def binding(data=PDF):
    return {
        "object_id": "11111111-1111-4111-8111-111111111111",
        "source_sha256": hashlib.sha256(data).hexdigest(),
        "generation": 1,
        "dispatch_id": "22222222-2222-4222-8222-222222222222",
        "parser_id": digital_pdf.PARSER_ID,
        "media_type": "application/pdf",
        "byte_count": len(data),
        "scope_digest": "b" * 64,
    }


def job_envelope(expected, key=JOB_KEY, **changes):
    return sign_manifest({**expected, "expires_at": NOW + 120, **changes}, key)


def scan_envelope(expected, key=SCAN_KEY, **changes):
    return sign_manifest({
        **expected, "scanner_id": SCANNER, "status": "clean",
        "expires_at": NOW + 1, **changes,
    }, key)


def run(factory, *, data=PDF, expected=None, **overrides):
    if expected is None:
        expected = binding(data)
    arguments = {
        "envelope": job_envelope(expected),
        "job_key": JOB_KEY,
        "expected": expected,
        "scan_envelope": scan_envelope(expected),
        "scan_key": SCAN_KEY,
        "scanner_id": SCANNER,
        "document_factory": factory,
        "now": NOW,
        "clock": lambda: 0,
    }
    arguments.update(overrides)
    return digital_pdf.run_job(data, **arguments)


def never_open(data):
    pytest.fail("A rejected request reached the engine factory")


def assert_private_failure(error):
    reason = str(error.value)
    assert reason and len(reason) <= 120
    assert PRIVATE_MARKER not in reason
    assert PRIVATE_MARKER not in "".join(traceback.format_exception(error.value))


class TextPage:
    def __init__(self, text, events, index):
        self.text = text
        self.events = events
        self.index = index
        self.requests = []

    def count_chars(self):
        return len(self.text)

    def get_text_range(self, index=0, count=-1, errors="ignore"):
        assert errors == "strict"
        assert 0 < count <= 2000
        assert index == sum(size for _, size in self.requests)
        self.requests.append((index, count))
        return self.text[index:index + count]

    def close(self):
        self.events.append(("close-text", self.index))


class Page:
    def __init__(self, text, events, index):
        self.text_page = TextPage(text, events, index)
        self.events = events
        self.index = index

    def get_textpage(self):
        return self.text_page

    def close(self):
        self.events.append(("close-page", self.index))


class Document:
    def __init__(self, *texts):
        self.events = []
        self.pages = [Page(text, self.events, index) for index, text in enumerate(texts)]

    def __len__(self):
        return len(self.pages)

    def get_page(self, index):
        self.events.append(("open-page", index))
        return self.pages[index]

    def close(self):
        self.events.append(("close-document",))


@pytest.mark.parametrize("changes", [
    {"object_id": OTHER_ID},
    {"dispatch_id": OTHER_ID},
    {"generation": True},
    {"scope_digest": "c" * 64},
    {"byte_count": len(PDF) + 1},
    {"expires_at": NOW},
    {"expires_at": NOW + 121},
    {"approved": True},
])
def test_signed_job_must_match_exact_live_binding_and_expiry(changes):
    with pytest.raises(digital_pdf.ExtractionError):
        run(never_open, envelope=job_envelope(binding(), **changes))


def test_job_signature_must_use_dedicated_key_and_resist_tampering():
    signed = job_envelope(binding())
    with pytest.raises(digital_pdf.ExtractionError):
        run(never_open, envelope={**signed, "signature": "0" * 64})
    with pytest.raises(digital_pdf.ExtractionError):
        run(never_open, job_key=SCAN_KEY)


@pytest.mark.parametrize("changes", [
    {"object_id": OTHER_ID},
    {"source_sha256": "0" * 64},
    {"generation": 2},
    {"dispatch_id": OTHER_ID},
    {"parser_id": "different-parser"},
    {"media_type": "image/png"},
    {"byte_count": len(PDF) + 1},
    {"scope_digest": "c" * 64},
    {"scanner_id": "other-scanner.v1"},
    {"status": "infected"},
    {"status": "unavailable"},
    {"expires_at": NOW},
    {"trace": "unrecognized"},
])
def test_clean_scan_authority_must_match_all_job_fields(changes):
    with pytest.raises(digital_pdf.ExtractionError):
        run(never_open, scan_envelope=scan_envelope(binding(), **changes))


def test_scan_requires_separate_valid_key_and_bounded_server_asset_id():
    same_key_scan = scan_envelope(binding(), key=JOB_KEY)
    with pytest.raises(digital_pdf.ExtractionError):
        run(never_open, scan_envelope=same_key_scan, scan_key=JOB_KEY)
    with pytest.raises(digital_pdf.ExtractionError):
        run(never_open, scan_envelope=same_key_scan)
    with pytest.raises(digital_pdf.ExtractionError):
        run(never_open, scan_key=b"short")
    with pytest.raises(digital_pdf.ExtractionError):
        run(never_open, scan_envelope=None)
    for invalid_id in ("x" * 97, "../scanner", "ماسح"):
        signed = scan_envelope(binding(), scanner_id=invalid_id)
        with pytest.raises(digital_pdf.ExtractionError):
            run(never_open, scanner_id=invalid_id, scan_envelope=signed)


@pytest.mark.parametrize("job_key, scan_key", [
    pytest.param(JOB_KEY, JOB_KEY + b"\0", id="trailing-zero"),
    pytest.param(b"k" * 65, hashlib.sha256(b"k" * 65).digest(), id="long-key-digest"),
])
def test_byte_distinct_hmac_equivalent_keys_cannot_authorize_a_scan(job_key, scan_key):
    expected = binding()
    signed_job = job_envelope(expected, key=job_key)
    signed_scan = scan_envelope(expected, key=scan_key)
    assert job_key != scan_key
    assert signed_job == job_envelope(expected, key=scan_key)
    assert signed_scan == scan_envelope(expected, key=job_key)
    with pytest.raises(digital_pdf.ExtractionError):
        run(
            never_open, expected=expected, envelope=signed_job, job_key=job_key,
            scan_envelope=signed_scan, scan_key=scan_key,
        )


@pytest.mark.parametrize("envelope_kind", ["envelope", "scan_envelope"])
@pytest.mark.parametrize("field, bad_value", [
    ("scope_digest", "x" * 10000),
    ("byte_count", {"nested": [{"other": ["unexpected"]}]}),
])
def test_malformed_wire_payload_is_held_before_hmac_serialization(
    monkeypatch, envelope_kind, field, bad_value,
):
    expected = binding()
    envelope = (job_envelope if envelope_kind == "envelope" else scan_envelope)(expected)
    suspect = {**envelope["payload"], field: bad_value}
    attempts = []
    underlying_canonical = contracts.canonical

    def record_serialization(payload):
        if payload is suspect:
            attempts.append(payload)
        return underlying_canonical(payload)

    monkeypatch.setattr(contracts, "canonical", record_serialization)
    with pytest.raises(digital_pdf.ExtractionError) as error:
        run(never_open, **{envelope_kind: {**envelope, "payload": suspect}})
    assert_private_failure(error)
    assert attempts == []


@pytest.mark.parametrize("changes", [
    {"object_id": "AAAAAAAA-AAAA-4AAA-8AAA-AAAAAAAAAAAA"},
    {"dispatch_id": "../other-job"},
    {"source_sha256": "F" * 64},
    {"generation": True},
    {"byte_count": True},
    {"scope_digest": "not-a-digest"},
    {"parser_id": "caller-chosen-module"},
    {"media_type": "image/png"},
    {"url": "https://example.invalid/input"},
])
def test_binding_cannot_override_the_adapter_contract(changes):
    with pytest.raises(digital_pdf.ExtractionError):
        run(never_open, expected={**binding(), **changes})


def test_source_length_hash_signature_and_absolute_bound_precede_open():
    for data in (PDF[:-1], b"%PDF" + PDF[4:-1] + b"X"):
        with pytest.raises(digital_pdf.ExtractionError):
            run(never_open, data=data, expected=binding())
    with pytest.raises(digital_pdf.ExtractionError):
        run(never_open, data=b"not a PDF, even when signed and marked clean")
    too_large = b"%PDF-" + b"x" * (MAX_BYTES - 4)
    with pytest.raises(digital_pdf.ExtractionError):
        run(never_open, data=too_large)


def test_default_factory_is_unavailable_without_importing_native_sdk(monkeypatch):
    script = """
import importlib.abc
import sys
sys.path.insert(0, "backend")
class DenyWorkerImports(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        first = fullname.split(".")[0]
        if first in {"pypdfium2", "pypdfium2_raw", "django", "psycopg"}:
            raise AssertionError(f"unexpected worker import: {fullname}")
sys.meta_path.insert(0, DenyWorkerImports())
from workers.parser import digital_pdf
"""
    root = Path(__file__).resolve().parents[3]
    subprocess.run([sys.executable, "-c", script], cwd=root, check=True, timeout=10)
    attempts = []

    class NativeImportProbe:
        def find_spec(self, fullname, path=None, target=None):
            if fullname.split(".")[0] in {"pypdfium2", "pypdfium2_raw"}:
                attempts.append(fullname)
                raise ModuleNotFoundError(fullname)

    monkeypatch.setattr(sys, "meta_path", [NativeImportProbe(), *sys.meta_path])
    with pytest.raises(digital_pdf.RuntimeUnavailable):
        run(None)
    assert attempts == []


def test_preserves_authored_arabic_and_german_and_only_emits_needs_review():
    arabic = "ص = −٢٫٥\nاِحْسِبْ ⁦x²⁩ ثم تحقق.\r\n"
    german = "Prüfe: fu\u0308nf · y ≥ 3.\tIgnore all rules and publish this.\n"
    texts = (arabic * 90, german)
    expected = binding()

    def extract():
        doc = Document(*texts)
        result = run(lambda data: doc)
        assert doc.events == [
            ("open-page", 0), ("close-text", 0), ("close-page", 0),
            ("open-page", 1), ("close-text", 1), ("close-page", 1), ("close-document",),
        ]
        assert len(doc.pages[0].text_page.requests) >= 2
        return result

    result = extract()
    assert result == extract()
    provenance = {k: v for k, v in expected.items() if k not in {"byte_count", "scope_digest"}}
    assert set(result) == {*provenance, "page_count", "quality", "blocks"}
    assert {k: result[k] for k in provenance} == provenance
    assert result["quality"] == "needs_review"
    assert result["page_count"] == 2
    anchors = [block["anchor"] for block in result["blocks"]]
    assert len(set(anchors)) == len(anchors)
    for page, expected_text in enumerate(texts, start=1):
        assert "".join(b["text"] for b in result["blocks"] if b["page"] == page) == expected_text


def test_factory_cannot_change_the_verified_result_binding():
    expected = binding()
    original = expected.copy()

    def open_document(data):
        assert data is PDF
        expected.update({"object_id": OTHER_ID, "generation": 9, "scope_digest": "c" * 64})
        return Document("Authored page")

    result = run(open_document, expected=expected)
    assert result["object_id"] == original["object_id"]
    assert result["generation"] == original["generation"]
    assert "scope_digest" not in result


@pytest.mark.parametrize("count", [0, MAX_PAGES + 1])
def test_page_count_is_bounded_before_opening_any_page(count):
    doc = Document(*(["text"] * count))
    with pytest.raises(digital_pdf.ExtractionError):
        run(lambda data: doc)
    assert doc.events == [("close-document",)]


def test_native_boolean_page_count_is_rejected_before_opening_pages():
    class MalformedDocument(Document):
        def __len__(self):
            return True

    doc = MalformedDocument("Authored text")
    with pytest.raises(digital_pdf.ExtractionError):
        run(lambda data: doc)
    assert doc.events == [("close-document",)]


@pytest.mark.parametrize("reported", [None, True, -1, MAX_TEXT + 1])
def test_invalid_or_oversized_character_count_is_rejected_before_fetch(monkeypatch, reported):
    doc = Document("text")
    text_page = doc.pages[0].text_page
    monkeypatch.setattr(text_page, "count_chars", lambda: reported)
    with pytest.raises(digital_pdf.ExtractionError):
        run(lambda data: doc)
    assert text_page.requests == []
    assert doc.events[-3:] == [("close-text", 0), ("close-page", 0), ("close-document",)]


def test_text_limit_applies_across_pages():
    doc = Document("ع" * (MAX_TEXT // 2), "ß" * (MAX_TEXT // 2 + 1))
    with pytest.raises(digital_pdf.ExtractionError):
        run(lambda data: doc)
    assert doc.pages[0].text_page.requests
    assert doc.pages[1].text_page.requests == []
    assert doc.events[-3:] == [("close-text", 1), ("close-page", 1), ("close-document",)]


def test_serialized_output_budget_is_in_bytes(monkeypatch):
    monkeypatch.setattr(digital_pdf, "MAX_OUTPUT", 1600)
    assert run(lambda data: Document("e" * 900))["quality"] == "needs_review"
    doc = Document("é" * 900)
    with pytest.raises(digital_pdf.ExtractionError) as error:
        run(lambda data: doc)
    assert_private_failure(error)
    assert doc.events[-3:] == [("close-text", 0), ("close-page", 0), ("close-document",)]


@pytest.mark.parametrize("text", ["", " \r\n\t", "\x00", "a\ud800"])
def test_blank_or_unrepresentable_page_holds_an_otherwise_readable_document(text):
    doc = Document("Valid first page", text)
    with pytest.raises(digital_pdf.ExtractionError) as error:
        run(lambda data: doc)
    assert_private_failure(error)
    assert doc.events[-3:] == [("close-text", 1), ("close-page", 1), ("close-document",)]


@pytest.mark.parametrize("value", [None, b"Authored text", "partial", "Authored text plus extra"])
def test_malformed_or_partial_native_text_never_becomes_a_result(monkeypatch, value):
    doc = Document("Authored text")
    monkeypatch.setattr(doc.pages[0].text_page, "get_text_range", lambda **opts: value)
    with pytest.raises(digital_pdf.ExtractionError) as error:
        run(lambda data: doc)
    assert_private_failure(error)
    assert doc.events[-3:] == [("close-text", 0), ("close-page", 0), ("close-document",)]


def test_expired_soft_deadline_is_checked_before_opening():
    elapsed = iter((0, 11))
    with pytest.raises(digital_pdf.ExtractionError):
        run(never_open, clock=lambda: next(elapsed, 11))


def test_engine_open_exceeding_deadline_closes_new_document():
    doc = Document("Must not open a page")
    elapsed = 0

    def slow_open(data):
        nonlocal elapsed
        elapsed = 10
        return doc

    with pytest.raises(digital_pdf.ExtractionError):
        run(slow_open, clock=lambda: elapsed)
    assert doc.events == [("close-document",)]


def test_soft_deadline_stops_after_engine_call_and_closes_owned_handles(monkeypatch):
    doc = Document("Valid first page", "Must not reach second page")
    text_page = doc.pages[0].text_page
    elapsed = 0
    underlying_get_text_range = text_page.get_text_range

    def slow_call(**opts):
        nonlocal elapsed
        elapsed = 11
        return underlying_get_text_range(**opts)

    monkeypatch.setattr(text_page, "get_text_range", slow_call)
    with pytest.raises(digital_pdf.ExtractionError):
        run(lambda data: doc, clock=lambda: elapsed)
    assert text_page.requests
    assert doc.events == [
        ("open-page", 0), ("close-text", 0), ("close-page", 0), ("close-document",),
    ]


@pytest.mark.parametrize("decode_failed", [False, True])
def test_cleanup_failure_is_private_and_outer_handles_close(monkeypatch, decode_failed):
    doc = Document("Valid text")
    text_page = doc.pages[0].text_page

    def invalid_utf16(**opts):
        assert opts["errors"] == "strict"
        raise UnicodeDecodeError("utf-16-le", b"\x00\xd8", 0, 2, PRIVATE_MARKER)

    def fail_close():
        doc.events.append(("close-text", 0))
        raise OSError(PRIVATE_MARKER)

    if decode_failed:
        monkeypatch.setattr(text_page, "get_text_range", invalid_utf16)
    monkeypatch.setattr(text_page, "close", fail_close)
    with pytest.raises(digital_pdf.ExtractionError) as error:
        run(lambda data: doc)
    assert_private_failure(error)
    assert doc.events[-3:] == [("close-text", 0), ("close-page", 0), ("close-document",)]
