# Current development checkpoint

20 November 2026. PUBLIC canonical repo https://github.com/EldonsLogic/sebaverse; workspace /Users/eldon/Documents/Sebaverse. On review branch `codex/resource-kind-review`, based on `8a413d8`; inspect Git/remote. Main remains at the last independently reviewed checkpoint. F0–F2 passed; F3 / DEV-010 in progress. No native activation, real data, live uploads, provider calls or deployment.

Current correction enforces current resource kind=file in both uploader live checks and requester resolution, without changing stored scope or schema. Five true baseline regressions and one positive were verified by root; the corrected code passes 571 backend tests (PostgreSQL deselected), Django clean and 236 ingestion tests. [Evidence and recovery](evidence/dev-010-resource-kind-fence.md).

All three subagents stopped at account usage limits after saving audit/tests/hosted/design files. Root inspected and completed the small broker correction and mock coverage. INDEPENDENT REVIEW PENDING: no assigned reviewer examined the final correction, and root verification is not independent acceptance. Do not mark DEV-010/F3 done or promote this checkpoint on those results alone.

Three new genuine PostgreSQL scenarios are staged; wrapper now expects 24. Those three, the six recent dispatch cases and retained-partial case are NOT RUN. Historical 14-scenario results do not cover this patch. No SQLite or mock-to-database substitution.

Hosted prior `8a413d8` passed 565 Linux backend tests with PostgreSQL deselected and separate foundation/dependency workflows; native pre-use gate failed, database/browser skipped. [Exact receipt](evidence/hosted-fidelity-8a413d8.md). Current resource-kind correction has local results only. [Audit](evidence/dev-010-next-boundary-audit.md).

The [production authority proposal](../workers/parser/production-authority-proposal.md) is design-only and has not received independent architecture/security acceptance. It does not implement descriptors/signers, change ADR-014, resolve RISK-F3-004 or qualify a runtime. Real PDF mapping/fidelity corpus and native/scanner/OS isolation remain pending.

Next: obtain independent review of the kind fence and staged scenarios, run the final native-gated PostgreSQL suite only after qualification. AUTH-014 supplier wait persists; no alternate hunt, owned writer, source build, pin/exception/review or gate changes. All mandatory F3 tests and independent review must pass before F4. No new learner-facing feature in this checkpoint.
