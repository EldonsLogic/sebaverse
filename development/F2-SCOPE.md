# F2 runnable skeleton and pre-use native policy

U16/AUTH-003, 12 November2026. Scope: selected Django/React stack, public liveness and database-readiness distinction, fail-closed nonlocal configuration, same-origin built shell, accessible Arabic navigation and honest empty states. No domain models, real accounts, uploads, tutor/model calls, scores, payments or deployment. PG default framework migrations are tested only after native pre-use gate.

## Native/image policy declared before scanner results

Record exact platform/wheel/image digests, supplier sources, identified native component versions and notice/license provenance. Use checksum-pinned official scanner tools and date/version of advisory DB. Static artifact download is allowed; image execution/DB connections are not until review. All findings remain visible: no severity suppression/ignore list. Block runtime on unresolved Critical/High known advisories, KEV findings, or unknown identification/version/provenance of loaded DB native components. Medium/Low findings require documented review/mitigation and an update decision; a clean scan is never safety certification. New fixable or unclear findings must be corrected or held, not hidden by changing policy. Actual distribution/source/license obligations remain release conditions; local development does not certify commercial compliance.

Default DB candidate is the existing immutable PostgreSQL17 image pin. If evidence shows it unsuitable, inspect a patched official same-major variant, record the change and rerun the same policy; never change database family or use SQLite to pass. Python binary wheel closure is separate from image closure. Pure-wrapper/system-libpq is an alternative only with a separately pinned/reviewed native chain and fresh lock/scan checks.

## Required phase evidence

Backend health/method/security/config tests; real PostgreSQL migration/readiness proof; frontend TypeScript/production build/desktop+mobile RTL/navigation/keyboard assertions; setup/teardown process proof; no credential/provider/realdata requirement; native pre-use policy and exact artifacts; meaningful regression checks and independent review. Hosted PostgreSQL must be started in explicit steps AFTER its native/image scan gate, not GitHub services startup before review. If local Docker unavailable, do not claim local DB proof; use real clean CI PG integration and state the local prerequisite. F3 stays blocked until every required F2 check and review passes.
