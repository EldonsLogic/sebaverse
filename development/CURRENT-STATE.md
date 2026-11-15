# Current development checkpoint

15 November 2026. Shared private repo: https://github.com/EldonsLogic/sebaverse. **F0/F1 passed; F2 in_progress under U16/AUTH-003. F3–F8 not_started.** DEV-001–005 complete. Local skeleton implementation started; no real learner/model/paid/deployment use.

## Verified latest work

F1 U15/AUTH-002: exact backend/web manifests and hashed locks, isolated wheel-only/lifecycle-disabled local installs, official metadata/license inventories, raw published-advisory reports, toolchain pins and dependency integrity checker. Python3.12.13/uv0.11.14, Node24.22.1/npm10.8.2. Root and independent reviewer verified import/render/exact-version checks plus22 phase/dependency regressions. Both local macOS arm64 and actual clean Ubuntu CI succeeded. Original36 research files remain hash-identical.

Tested work commit: ba2edb2df95ce584f9408e4a3822b7ec91a60f8c. Dependency CI43052547533 and foundation CI43052547439 passed. Exact evidence: f1-run.md, f1-independent-review.md, f1-github-ci.json and f1-dependency-snapshot.json under evidence/. Later status checkpoint SHA comes from actual Git/remote; do not assume a stored SHA is latest.

## Current F2 results and next action —DEV-006

Local authored Arabic Django/React empty shell is implemented.83 DB-free backend tests pass; realPG integration still deselected. Desktop/mobile browser, TypeScript/build and loopback lifecycle evidence remain in outputs/f2-local-skeleton/. No learner/model/account/upload/grading features enabled.112 current foundation/policy/helper tests pass locally; original36 research files remain unchanged.

Static remediation and exact CI patch are now measured, not drafts. Successful run43691875268 at51d17a4:
- Derived OCI46packages,3Medium matches; noHigh/Critical/Unknown. Original official Alpine candidate had35High/Critical matches in the overwritten Go helper. Lower layers retain original bytes.
- Exact authored0755 stub delta, immutable parent/config/layer lineage and retained entrypoint source checked. The root UID branch calls gosu; Userpostgres avoids that branch by design, not yet proven by actual startup.
- Six exact signed Ubuntu glibc package archives reviewed/installed only on disposable CI, allpostinstall2.39-0ubuntu8.12. Fresh linked-native inventory/rescan66matches (65Medium+1Negligible), six targeted libc6 findings absent versus72before. Remaining findings stay unapproved.

Evidence:development/evidence/f2-static-patched-43691875268/ and f2-static-experiment.md. Independent actual/helper review:f2-derived-review.md. Main phase status remains F2 in_progress/held; F3–F8 untouched. No DB container/startup/migration, realchilddata, paidmodel or deployment use occurred.

Next: resolve remaining image/native/core applicability reviews under unchanged policy; bind the actual derived artifact and its provenance/import/runtime identity into the pre-use validator/runner with negative tests; then run real PostgreSQL migrations/authentication/readiness/teardown only after full pre-use pass. The current official-only runtime gate deliberately does not accept a local derivative. CI experiment success is not a phase pass. Source-equivalent builds produced differing digests, so each actual artifact needs its own binding; reproducible-release output is not established.

Historical official-image failures and raw findings remain preserved, never relabeled clean.12November scanner verification was blocked by account usage; cached Syft was later checksum/version verified14November, recorded in f2-local-run.md. No security/legal/educational certification claimed.

## Resume and gate rules

Read START-HERE.md, AGENTS.md, engineering/workflow/handover docs, tasks.json and phase-gates.json. Inspect actual Git branch/HEAD/dirty tree before claiming files. F2 is active; native DB/image use is held until pre-use evidence passes. At every phase exit run meaningful required tests, record actual evidence and independent review, clear blockers and only then advance. Frozen audit/brand exports are historical, not active instructions. Avoid a competing master, untracked progress, force pushes or false test claims.

## Current review pointers

Read development/F2-REMEDIATION.md, f2-static-experiment.md and f2-derived-review.md before changing runtime selection or finding dispositions. infra/local/postgres/proposal.json records an observed artifact identity, not permission to execute. CI-only native patch approval is exact dependency review, not founder phase/product/production approval. Check actual Git/remote for latest checkpoint rather than trusting a stored SHA.
