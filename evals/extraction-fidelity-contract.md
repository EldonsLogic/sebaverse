# Authored extraction fidelity comparator v1

20 November 2026 · DEV-010 · R039. The comparator checks an authored reference against one offline outcome using an independent job binding. The initial vectors exercise comparison and hold behavior with synthetic text and markers. Qualified source artifacts, their hash-to-reference mapping and measured extraction fidelity are pending. [Curriculum evaluation protocol](../docs/04-curriculum-and-rag.md#evaluation-protocol) · [DEV-010 fidelity controls](../development/evidence/dev-010-fidelity-controls.md)

## Inputs

Call `compare_extraction(reference, candidate, expected_provenance=...)` from `evals.extraction_fidelity` with plain decoded JSON objects. The comparator performs no I/O. The caller owns bounded input decoding, including rejection of duplicate JSON members. Supply exactly these reference fields.

| Field | Contract |
| --- | --- |
| `fixture_id` | Authored fixture locator, 1–64 lowercase ASCII letters, digits, dots, underscores or hyphens. Starts with a letter or digit. |
| `expected_outcome` | `needs_review` or `hold`. |
| `line_endings` | `exact` or `lf_equivalent`. |
| `pages` | 1–30 ordered page objects, numbered implicitly from one. Each has `text` and `critical_tokens`. |
| `hold_reason` | Required on a hold reference and otherwise omitted. The current reference reason is `page_without_text`. The final reference page has empty text and no tokens. Any preceding pages contain readable reference text. |

Reference text is bounded by the shared 200,000-character result ceiling. Each page has up to 16 distinct, present, single-line critical tokens of 1–64 characters. A `needs_review` reference has nonblank text on every page. References should be authored independently of extractor output. The initial job bindings use actual digests of authored non-PDF marker bytes. Future fixture authors should hash the finalized source artifacts and review the source-to-reference mapping before a qualified runtime run.

For a `needs_review` candidate, supply the existing [worker result object](../backend/modules/ingestion/contracts.py). The independent `expected_provenance` supplies exactly `object_id`, `source_sha256`, `generation`, `dispatch_id`, `parser_id` and `media_type` from the fixture's attempted job. The binding uses canonical UUIDs, a lowercase SHA-256 digest, a positive signed-32-bit generation, a bounded asset ID and a supported media type. The offline harness pairs the independently reviewed reference with its source hash and supplies the job binding independently of the result. The comparator checks this binding by equality. Source-byte verification and job authentication belong to the harness.

For a held candidate, supply exactly `hold_reason` and `provenance`. The latter uses the same six fields. The offline observer records the bounded reason and binds it to the attempted job only when it observed that hold without a result. This record carries no cryptographic authority. An absent or malformed outcome, a wrong reason, or a partial result cannot satisfy the expected hold. A capture of the real worker remains pending. [Text-only adapter hold behavior](../workers/parser/digital-pdf-contract.md#extraction-and-limits)

## Comparison and reporting

Check bounded shapes before passing successful candidates to the existing validator. That validator also enforces serialized size, unique anchors and `needs_review`. Read blocks in the reported order and concatenate their exact text within each page without inserting separators. Check declared count, page coverage and nondecreasing page order. Anchors may use any valid unique value. Chunk boundaries and anchor spelling can vary across runs.

By default compare the complete page as exact Unicode. `lf_equivalent` permits only CRLF to LF conversion after concatenation, on both sides. Bare CR, spaces, combining marks, bidi controls, digits and notation remain literal. On a text mismatch, additionally compare critical token occurrences in logical page-text order. Occurrences can overlap. At a shared start position the longest annotated token takes precedence. The complete text comparison still detects differences outside the critical token sequence.

`FidelityReport.matches` is true when its diagnostic tuple is empty, including for a correctly observed expected hold. Each diagnostic carries a fixed code and, for page-level issues, a one-based page number. The caller can associate it with the fixture locator it already holds. Reports contain no text, token strings, anchors, provenance values or exception details.

| Codes | Meaning |
| --- | --- |
| `invalid_reference`, `invalid_provenance`, `invalid_result` | An input was malformed, unsupported or over its bound. |
| `provenance_mismatch` | A candidate's valid binding differed from the independent binding. |
| `unexpected_hold`, `unexpected_result`, `hold_reason_mismatch` | The observed outcome or reason differed from the expected one. |
| `page_count_mismatch`, `page_missing`, `page_order_mismatch` | Declared count, coverage or reported ordering differed. |
| `text_mismatch`, `critical_notation_mismatch` | Page text or its ordered critical token occurrences differed. |

A match to the authored synthetic outcome verifies comparator behavior. An actual digital PDF run requires a qualified runtime and authorized source files. Scanned pages, OCR, layout, tables, diagrams, formulas and the full representative Arabic and bilingual corpus remain part of R039. A match conveys no publication authority, grading result, mastery update or phase pass. [R039 evaluation protocol](../docs/04-curriculum-and-rag.md#evaluation-protocol)
