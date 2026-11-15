# Current development checkpoint

15 November 2026. Shared private repo: https://github.com/EldonsLogic/sebaverse. **F0/F1 passed; F2 in_progress under U16/AUTH-003. F3–F8 not_started.** DEV-001–005 complete. Local skeleton implementation started; no real learner/model/paid/deployment use.

## Verified latest work

F1 U15/AUTH-002: exact backend/web manifests and hashed locks, isolated wheel-only/lifecycle-disabled local installs, official metadata/license inventories, raw published-advisory reports, toolchain pins and dependency integrity checker. Python3.12.13/uv0.11.14, Node24.22.1/npm10.8.2. Root and independent reviewer verified import/render/exact-version checks plus22 phase/dependency regressions. Both local macOS arm64 and actual clean Ubuntu CI succeeded. Original36 research files remain hash-identical.

Tested work commit: ba2edb2df95ce584f9408e4a3822b7ec91a60f8c. Dependency CI43052547533 and foundation CI43052547439 passed. Exact evidence: f1-run.md, f1-independent-review.md, f1-github-ci.json and f1-dependency-snapshot.json under evidence/. Later status checkpoint SHA comes from actual Git/remote; do not assume a stored SHA is latest.

## Next action — DEV-006 / F2

Implemented local Django/React empty skeleton. Actual 14 November rerun:83 DB-free tests pass; TypeScript and production build pass;22 existing foundation/dependency regressions pass. Desktop/mobile browser checks pass with complete screenshots (1314/1872px), keyboard/main-focus/RTL/routes/no-overflow and actual local server teardown. Evidence:outputs/f2-local-skeleton/. No real content, model, account or learner feature enabled.

F2 remains in progress. Scanner-report identity/schema/evidence-binding gaps were hardened;46 targeted synthetic policy regressions now pass locally and independently. Actual hardened Linux run43596679254 successfully captured bound scanner receipts and reached the findings gate; the known image/native findings correctly blocked it. Exact reports/receipts/patch metadata preserved in development/evidence/f2-hardened-run-43596679254/. Independent review recorded in development/evidence/f2-independent-review.md; F2 remains held. Loader overrides are now rejected before inventory/replay;8 targeted guard tests pass, and all76 foundation/policy regressions pass locally. Local synthetic DB options explicitly disable GSS encryption and require SCRAM-SHA-256;83 DB-free backend tests pass. Real negotiation is not yet tested. Actual Linux scan43595873985 identified24 native library files/20 owner packages, then blocked the original Debian image:582 total matches including221 High/Critical. System client had72 Medium/Negligible matches and supplier core had1 Medium match, all still unreviewed. Raw evidence preserved in development/evidence/f2-rejected-image-43595873985/. Official PostgreSQL17-alpine17.12 replacement also blocked in actual run43596204128:65 matches, including32 High+3 Critical, all blocking matches from Go1.24.6 embedded in /usr/local/bin/gosu. Raw replacement evidence:development/evidence/f2-alpine-candidate-43596204128/. No findings suppressed. No pre-use pass or PostgreSQL integration result exists. Native policy is unchanged; scanner matches are observed advisory evidence, not independently confirmed exploitability. macOS DB stays held; no SQLite fallback.

Previous 12 November scanner verification command was not executed because automatic approval review hit the account usage limit. The completed Syft archive is cached but not claimed verified/executed. No security/legal/educational certification claimed.

## Resume and gate rules

Read START-HERE.md, AGENTS.md, engineering/workflow/handover docs, tasks.json and phase-gates.json. Inspect actual Git branch/HEAD/dirty tree before claiming files. F2 is active; native DB/image use is held until pre-use evidence passes. At every phase exit run meaningful required tests, record actual evidence and independent review, clear blockers and only then advance. Frozen audit/brand exports are historical, not active instructions. Avoid a competing master, untracked progress, force pushes or false test claims.

## Bounded remediation draft —15 November

`infra/local/postgres/` contains an unbuilt test-only recipe:immutable official Alpine parent, no RUN, replace merged gosu path with deterministic fail126 script, USER postgres. Root verified the script exits126. This is not a scanned/approved image, and current verifier/runner are deliberately not relabeled to accept it. Next implementation must bind the actual derived digest/provenance and scan its effective filesystem; lower-layer bytes and release rights remain explicit. See development/F2-REMEDIATION.md.

## Latest verified source checkpoint

87ba3f9 pushed to origin/main15November; GitHub foundation43689700548 and dependency43689700711 passed. Skeleton43689700627 completed and correctly failed at the unchanged native/image findings gate; no DB step ran. Exact final-run evidence retained in development/evidence/f2-linux-43689700627.zip with SHA256/source metadata in its companionJSON. Latest Git/remote must be checked rather than assuming this storedSHA is current.33-ID native advisory review register saved in development/evidence/f2-native-findings-review.md, with every unapproved finding retained. No exceptions/blanket reviews added.
