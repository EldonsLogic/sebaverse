# DEV-010 direct text-only adapter checkpoint

19 November 2026 · R039/R040/R041/R046 · U23 / AUTH-013 / ADR-014. Founder explicitly chose the direct PyPDFium2 adapter. Threat/budget: malformed jobs or output could expose unauthorized content or unbounded native work; one owned-core implementation and independent review with bounded corrections, no native execution.

## Implemented behavior

The new workers/parser/digital_pdf.py is importable without the SDK or Django. run_job validates bounded scalar manifests, separate job and clean-scan signing keys, expiry and every job/object/source/dispatch/generation/scope field, then verifies source bytes before any document factory call. The default factory is absent and raises RuntimeUnavailable. Resource handles close in reverse order; engine failures become bounded reasons. Native-reported pages/characters are checked before bounded strict text-range requests; output preserves text, page/offset anchors and needs_review under existing schema/byte limits. No public API, approved runtime registry, broker path, image or security-review binding changed.

The cached SDK warns of native range versus returned string length differences and UCS-2 limitations. The core holds mismatches and blank/image-only pages instead of dropping notation. It may reject legitimate PDFs. Actual extraction fidelity is not established. The ten-second limit is a soft check of calls that return; hard native memory/process/hang/cancellation protection remains a separate qualified-worker requirement.

## Actual agent work

Root owns architecture/authority, contract, integration and QA. Three actual gpt-6.2-sol medium-effort agents handled independent files: parser_semantic_review implemented only the worker core; shared_wheel_completion authored only fake-engine tests; runtime_fix_recheck independently reviewed both after its one same-route Canonical metadata check. The session capacity is four including root, not five simultaneous subagents. No unmeasured token savings or artificial work are claimed.

The review caught effective HMAC key equivalence and swallowed output-limit reason handling. The implementation corrected both. Two added regression tests fail against raw byte-key equality, demonstrating the key-boundary correction. [Independent review and exact source hashes](dev-010-direct-adapter-review.md) accepted only the disabled core and fake-engine tests, not a runtime or F3 pass.

## Validation and limits

Independent checks: make test-ingestion passed 96 tests (64 new), make backend-check passed 431 tests with one PostgreSQL integration test deselected and Django checks clean. Root final combined foundation/backend checks are recorded at the closing checkpoint. Fixtures are authored PDF markers and SDK-shaped fakes, never real child data or actual PDFium. No package, scanner, model, database or worker isolation runtime executed. Earlier 15-scenario PostgreSQL probe remains unrun while the fixed database image is unavailable. Separate Canonical Noble scanner status still needs triage for the previously recorded CMS advisory; no scanner exception was granted.

Native PDFium core/component advisory and rights qualification, pinned worker image, qualified scanner/definitions, hard OS/watchdog/egress/filesystem controls, worker cancellation/transport, reviewed asset activation and real authored Arabic/bilingual/fidelity tests remain open. OCR/layout/math/table/diagram requirements are retained. Docling remains the advanced extraction direction; the first digital-text route changed through the founder-selected ADR rather than a silent scope omission. DEV-010/F3 remain in progress.

Root closing checks completed: artifact/economics/foundation PASS, 179 helper tests passed, 431 database-free backend tests passed with one PostgreSQL integration deselected, and Django system check clean. No code change followed the independent adapter/test hashes. Canonical architecture/register/approval/continuity records reflect the explicit founder selection; runtime gates remain held.
