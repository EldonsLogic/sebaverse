# Current development checkpoint

20 November 2026. PUBLIC canonical repo https://github.com/EldonsLogic/sebaverse, workspace /Users/eldon/Documents/Sebaverse. Working checkpoint based on `37e39e1`; inspect Git/remote. F0–F2 passed; F3 / DEV-010 remains in progress. No real uploads, native activation, paid calls or deployment.

Broker correction: recheck live/owned dispatch after scanning before parser handoff; never overwrite a newer dispatch when old work finishes or fails; pass a copied primitive binding to parser and validate against the broker-owned original. Stable adapter identities recorded. Final publication fence retained. Callbacks run outside locks: revocation can overlap already-started parsing, so this is not instantaneous worker cancellation. [Correction/evidence](evidence/dev-010-dispatch-fence.md).

Six focused regressions genuinely failed against the prior broker: three wrongful parser calls, two newer dispatches overwritten and one forged provenance result accepted. Final local tests and independent review are recorded in the correction evidence. Authored in-memory ORM boundaries exercise actual process(), not PostgreSQL locking. Staged opt-in PostgreSQL scenarios now total 21; six newly added plus the previously unrun fifteenth scenario remain NOT RUN. Earlier 14-scenario hosted evidence is historical, not acceptance of this patch.

Hosted prior commit `37e39e1` passed 494 Linux backend tests (PostgreSQL deselected), foundation and dependency-readiness workflows. Static native gate still failed; database/browser steps skipped. [Exact hosted receipt](evidence/hosted-transport-37e39e1.md). No rerun or policy change in this checkpoint; current broker changes have local evidence only until committed CI runs.

Three actual Sol subagents handled implementation/planning, independent tests/PG fixtures and hosted evidence/independent review; root integrated. The proposed 8 MiB input transport remains unimplemented. [Input proposal](../workers/parser/input-transport-plan.md), [remaining F3 work](evidence/f3-remaining-work-2026-11-20.md).

AUTH-014 supplier wait persists: only installed libcrypto3/libssl3 r1 were approved, CLI absent. No owned writer, alternate hunt, source build, pin, exception, review binding/date or gate change. Noble scanner, native PDFium, worker OS isolation and actual Arabic/bilingual extraction remain unqualified.

Next: qualified scanner/parser/isolated composition and fidelity work only within existing scopes/budgets; supplier reassessment only on a meaningful update. Finish all mandatory F3 exit tests and independent review before F4. This correction protects future private parsing but adds no learner-facing feature.
