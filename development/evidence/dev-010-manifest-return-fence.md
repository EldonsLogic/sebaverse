# DEV-010 manifest return authorization fence

21 November 2026 · R040/R041/R046 · existing authored F3 scope. A request authorized before storage I/O can return content after consent, rights or reviewer permission changes during that I/O. Current exposure is synthetic private objects only. Budget: one shared read helper, independent negative/positive tests and review, at most two corrections. No native runtime, database, model, provider or supplier recovery.

The broker captures an immutable saved scope/resource/authorization-generation tuple, manifest SHA and primitive provenance before reading. It validates the read bytes against that pinned identity, then reloads the upload and repeats the caller-specific access checks before returning. Current manifest binding must still match. Reviewer reads recheck reviewer grants; learner/guardian resolution retains requester-derived permissions and checks current rights expiry. No lock is held across storage work. Changes after the final check remain possible; this is a return fence, not instantaneous network-response cancellation.

Three initial cases reproduced late returns after canonical consent withdrawal/regrant, rights expiry and reviewer grant removal. Independent final baseline replay covers all 14 unit cases: 12 negative cases fail on fb92198 while the two unchanged-read positives pass. The corrected worktree passes all 14; private-data diagnostics remain bounded. Root backend checks report 585 passed, one PostgreSQL test deselected, Django clean. Final independent review and closing checks follow below.

The staged PostgreSQL probe/wrapper now expect 27 scenarios. Three new fixtures exercise canonical consent withdrawal followed by synthetic-record regrant during read, rights expiry during read and reviewer revocation during read when a qualified database is available. They are NOT RUN. Previous pending kind/dispatch/retained-partial scenarios remain unrun and historical 14-scenario evidence is not acceptance of this patch.

RISK-F3-005 separately records that consent withdrawal currently has no automatic source/derived purge path; access denial does not prove deletion. No purge workflow or retention period is invented here. The production-authority review requires revisions and RISK-F3-004 remains open. AUTH-014 supplier wait and all gates/pins/reviews remain unchanged. [Audit](dev-010-next-step-2026-11-21.md), [hosted prior main result](hosted-kind-main-fb92198.md), [design review](../../workers/parser/production-authority-review.md).

## Independent acceptance and remaining scope

[Independent reviewer](dev-010-manifest-return-review.md) accepted the exact final broker/test delta and passed 585 backend tests (one PostgreSQL deselected), 250 ingestion tests and 20 focused kind/read checks. It independently replayed the final 14 manifest cases against the exact old fb92198 broker: all 12 negatives failed while both unchanged-read positives passed. Root separately passed 585 backend tests and Django checks. The source fix required one immutable-snapshot refinement before final review; no security threshold changed.

The staged PostgreSQL cases and both Python files were statically reviewed/parsed, not executed. The separate deletion gap and production authority design cannot be counted as resolved by these tests. Root closing document/foundation checks follow final integration.

Root final `make foundation-check` exited 0: artifact/economics/foundation checks and 179 helper tests passed. `git diff --check` passed. The fifth-stream handoff audit confirmed the recorded limits and requested two clarity edits, applied without source changes. No pins, old security reviews, thresholds, approved assets or phase gates changed. All file owners released their work.
