# DEV-006 / F2 remaining work

Requirements:R054,R075,R078,R094,R097,R098. Acceptance remains DEV-006 + F2-SCOPE; no phase waiver. Arabic shell is implemented and checked. F3 has not started.

## Measured progress

Actual static experiment43691875268 at51d17a4 successfully built/inspected the authored nonroot OCI derivative, scanned46packages with3Medium findings and noHigh/Critical/Unknown, installed six exact reviewed Ubuntu archives only on disposable CI, then inventoried/scanned the linked native chain. Six targeted libc6 matches disappeared;66other native matches remain (65Medium+1Negligible). Independent raw-evidence review is in f2-derived-review.md; complete compact evidence is preserved under development/evidence/f2-static-patched-43691875268/. No database started.112 local foundation/policy/helper tests and83 DB-free backend tests pass.

## Remaining ordered steps

1. Review remaining3image/66native and supplier-core findings against exact primary evidence/component/platform. Retain all matches and case-specific rationale. BusyBox1.37.0-r31 remains possibly vulnerable in Alpine; no patched-image claim. A constrained synthetic mitigation needs verified workload/network containment, not nonroot alone. Supplier-coreCVE-2017-8806 concerns Debian helper scripts; verify exact component applicability rather than guessing from server version. High/Critical/Unknown remain blocked; no blanket Medium/Low acceptance.
2. Bind the actual derived artifact into pre-use validation and runtime. The current contract accepts the official upstream reference only; do not relabel a derivative as that image. Require actual archive/manifest/config/parent lineage/recipe/stub/source and scan-byte identity, exact import/run identity and negative drift/substitution tests. Future fresh builds require their own receipts; source-equivalent runs produced differing digests and reproducible-release output is not established.
3. Keep the CI patch exact:committed versions/archive/notice hashes, fresh dry-run, no added/removed companions, actual postinstall versions and fresh linked-native inventory/scans. Its existing approval is dependency review for disposable Ubuntu24.04 amd64 CI only, not founder phase/production/redistribution approval. Changed packages/notices/versions require new review.
4. Recheck synthetic startup inputs, including absence/review of executable initdb scripts and bounded environment/network. Retained entrypoint invokes gosu only at UID0; the actual archive verifies Userpostgres and exact fail126 stub replacement. Actual initialization/read-only-root compatibility is not yet tested. Lower OCI layers retain original helper bytes; no archive-erasure claim.
5. Only after full actual pre-use pass, run real PostgreSQL17 migrations, no-pending-migrations check, explicit SCRAM authentication/readiness200, synthetic session roundtrip and task-owned cleanup on Linux. Existing mocks/83 DB-free tests cannot substitute. macOS database remains separately gated.
6. Run relevant backend/browser/foundation tests, obtain fresh independent phase review, record actual evidence and verified GitHub sync. Only then mark F2 passed and advance. Static experiment success is not phase approval.

No paid provider, real child records, deployment, release certification or new commercial/legal approval is included. Original failures/research remain preserved. Exact binary OCI payloads stay in ignored work/ and short-lived hosted artifacts; committed recipes, hashes, raw reports and notices do not imply permanent hosting of the binary archive.
