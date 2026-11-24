# DEV-011 offline publication preflight

24 November 2026 · AUTH-016/U26 · R041/R042/R043/R099. A candidate could omit intended items or bind changed/stale/private dependencies while looking structurally complete. Current scope is original shared-fixture metadata only. Budget one engineering day and at most two review correction cycles. No live publication, grading, rights grant, native/database/provider execution or F3 transition.

Founder explicitly approved Option A of the independently reviewed critical-path plan. Full DEV-011 remains planned with DEV-010 as an unmet dependency. Only the independent `preflight-v1` sub-slice is active. Exact structural contract and tests will use a trusted separately validated inventory; candidate and intended set cannot establish each other's completeness by circular comparison. Existing DEV-007 record contracts remain authoritative for strict versions and rights.

Three subagents own implementation/contract, independent authored tests and independent review. Root owns source/approval/task records, test target, continuity and verified integration. Design and test results follow source release; no future success is assumed.

## Implemented contract

`validate_publication_preflight` compares independently validated shared-fixture inventory and candidate payloads with a strict exact-version/hash manifest. All intended approved inventory items and their active edition/profile/rubric/objective/collection/material/rights closure must match. Removing an item from both candidate artifacts still fails against the trusted inventory. Every candidate context record must retain its inventory version's exact bytes. Historical `supersedes` context is not automatically an active publication pin. Official/private claims, malformed/bounded input and unsupported empty/source-only cases fail closed.

The caller must supply a stable, independently sourced trusted inventory and explicit aware decision time. Python object separation is not authentication. Success is only `structure_valid_assessment_held`, with exact shared item versions and fixed actual-grader/educator holds (human-review mode retains human review). No content, answer key, ready flag or grant is returned. The function does no I/O, mutation, grading, approval, publication or indexing. Existing contracts and original fixture bytes are unchanged. [Contract](../../architecture/publication-preflight-contract.md).

## Actual verification and correction

The first test collection failed because the curriculum test directory is not an import package; the test author changed only their fixture-loading seam. An initial guessed test-target spelling was absent; the actual added target is `make test-publication-preflight`. No missing target was marked passed.

The first 28 focused cases passed. Independent review then reproduced a real ambient-timezone defect: the same naive rights expiry passed under UTC and failed under Cairo at a fixed UTC instant. Correction 1 of the allowed two requires explicit timezone offsets or `Z` on every rights expiry before the legacy validator. Raw canonical strings stay unchanged. Six regressions verify deterministic UTC/Cairo decisions and strict equality expiry. Expired historical rights can still conservatively hold the preflight under the unchanged base validator.

Final root `make backend-check`: exit 0, 717 passed with one PostgreSQL integration test deselected, Django clean. Test owner and independent reviewer passed 34 focused preflight cases; full curriculum 67 and authorization 162 passed with unchanged exported schema. Independent exact-source [review](dev-011-preflight-review.md) accepted source, test and contract hashes. Root and reviewer `make foundation-check` passed artifact/economics/foundation validation and 179 helper tests. The helper suite's deliberate timeout fixture is not a live npm failure. Whitespace checks passed.

Only `preflight-v1` is complete. Full DEV-011 remains planned with its original dependencies; no task or phase is falsely passed. Thirty-seven staged PostgreSQL scenarios remain NOT RUN. Actual publication, private ingestion, semantic item validation, educator decisions, retrieval/UI and F3 runtime/rights/retention gates remain held. No new supplier assessment, exception, security review binding, package or threshold changed.

The earlier pending-choice proposal is preserved as the exact independently reviewed historical artifact; U26/AUTH-016 record the later founder selection and supersede that pending status. Closing integration retains both decision lineage and the original phase boundaries.
