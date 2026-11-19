# ADR-014 — Minimal digital-PDF PoC adapter

Status: **Proposed, awaiting founder choice**, 19 November 2026. No architecture selection, dependency adoption or phase gate is changed by this file. Requirements: R039, R040, R041, R046. Related: ADR-006, ADR-007, AUTH-008 and DEV-010.

## Problem and observed evidence

The Docling Slim 2.150.1/PyPDFium2 candidate resolves 43 Python packages. Shared wheels include NumPy, pandas, lxml, Pillow and native Rust extensions; all eight shared wheel archives are now hash verified. In contrast, the exact PyPDFium2 5.15.2 wheel’s METADATA declares no Requires-Dist entries. The package itself includes native PDFium and bundled components. One Python package is not one native dependency or a security clearance. [Candidate](../../workers/parser/alternate-candidate.json), [shared inventory](../../workers/parser/shared-wheel-inventory.md), [native evidence](../../workers/parser/native-closure-review.md), [component findings and independent review](../../workers/parser/component-independent-review.md).

## Proposed bounded change

For the initial authored digital-PDF PoC only, implement an owned adapter directly against the same exact reviewed PyPDFium2 backend instead of installing the full Docling wrapper. Keep the selected web/backend/database, private broker, job authority and untrusted-result contract. Docling remains the selected advanced extraction direction pending its separate qualification; it is not installed or removed by this proposal.

The adapter would accept a broker-issued local read-only PDF and bounded signed job manifest in an isolated worker, never a client URL or arbitrary filesystem path. No learner database credentials, broad egress or implicit assets. Preserve source hash, object/dispatch/generation, parser version, page identity and stable anchors; review any contract extension for geometry before implementing it. Enforce byte/page/text/output/time/process limits, cancellation and deletion. Parsing also requires a verified clean scan attestation bound to the exact object, source hash, dispatch and generation. Recheck live authorization, consent, edition and rights at broker publication/resolution. Results remain needs_review until the existing scoped rights/extraction approval path succeeds. Source text grants no tools or authority.

This scope covers embedded digital text only. Scanned/image-only, malformed, partial and over-limit documents stay held with actionable states. Arabic and bilingual order, critical notation, rotated pages, anchors and source fidelity must be measured on authored fixtures, not assumed. OCR, tables, formulas and diagrams remain visible R039 requirements. A text-only PoC does not complete DEV-010 or pass F3 by itself.

## Choices and tradeoffs

1. **Approve the direct adapter for the bounded PoC (recommended).** Removes 42 Python package versions from the proposed parser dependency set; the final image/runtime footprint remains unmeasured. Reduced review, startup, storage or runtime cost is an inference until measured. Adds a small owned extraction/provenance adapter and may offer less layout structure than Docling. Retains native PDFium, licensing/advisory, worker image, malware scanner, isolation and execution checks. No new package candidate, rights waiver or scanner exception.
2. **Keep the full Docling wrapper for the PoC.** Preserves the current SDK path and richer document representation. Complete applicable reviews of all 43 packages before installation, import or execution; imports occur only after dependency and execution permissions qualify. More dependency work; no claim that quality or performance will be better until tested.

No implementation work under the changed approach starts before the choice is recorded. Either approach needs independent artifact review and actual tests before enablement. No paid services, source build, production, deployment or real-minor data is authorized.

## Reviewable next increment if selected

Pin the one exact wheel in a separate worker boundary after its review qualifies; implement the minimal adapter with synthetic tests for limits, provenance, unavailable scanner and stale jobs. Obtain independent review. Run an authored-fixture process only after runtime/scanner/isolation gates clear, record actual fidelity and resource use, then compare whether Docling is needed for the next extraction capability. Do not advance to F4 while F3 remains held.
