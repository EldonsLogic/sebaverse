# Current development checkpoint

14 November 2026. Shared private repo: https://github.com/EldonsLogic/sebaverse. **F0/F1 passed; F2 in_progress under U16/AUTH-003. F3–F8 not_started.** DEV-001–005 complete. Local skeleton implementation started; no real learner/model/paid/deployment use.

## Verified latest work

F1 U15/AUTH-002: exact backend/web manifests and hashed locks, isolated wheel-only/lifecycle-disabled local installs, official metadata/license inventories, raw published-advisory reports, toolchain pins and dependency integrity checker. Python3.12.13/uv0.11.14, Node24.22.1/npm10.8.2. Root and independent reviewer verified import/render/exact-version checks plus22 phase/dependency regressions. Both local macOS arm64 and actual clean Ubuntu CI succeeded. Original36 research files remain hash-identical.

Tested work commit: ba2edb2df95ce584f9408e4a3822b7ec91a60f8c. Dependency CI43052547533 and foundation CI43052547439 passed. Exact evidence: f1-run.md, f1-independent-review.md, f1-github-ci.json and f1-dependency-snapshot.json under evidence/. Later status checkpoint SHA comes from actual Git/remote; do not assume a stored SHA is latest.

## Next action — DEV-006 / F2

Implemented local Django/React empty skeleton. Actual 14 November rerun:83 DB-free tests pass; TypeScript and production build pass;22 existing foundation/dependency regressions pass. Desktop/mobile browser checks pass with complete screenshots (1314/1872px), keyboard/main-focus/RTL/routes/no-overflow and actual local server teardown. Evidence:outputs/f2-local-skeleton/. No real content, model, account or learner feature enabled.

F2 remains in progress. Independent review identified scanner-report identity/schema/evidence-binding gaps; fixes and negative regression fixtures are underway. No pre-use pass or PostgreSQL integration result exists yet. First clean Linux workflow must inventory actual system-libpq linked packages/notices, scan the pinned image/core/native inventory, enforce unchanged pre-use policy, then run real PG migrations/readiness/cleanup. macOS DB stays held; no SQLite fallback.

Previous 12 November scanner verification command was not executed because automatic approval review hit the account usage limit. The completed Syft archive is cached but not claimed verified/executed. No security/legal/educational certification claimed.

## Resume and gate rules

Read START-HERE.md, AGENTS.md, engineering/workflow/handover docs, tasks.json and phase-gates.json. Inspect actual Git branch/HEAD/dirty tree before claiming files. F2 is active; native DB/image use is held until pre-use evidence passes. At every phase exit run meaningful required tests, record actual evidence and independent review, clear blockers and only then advance. Frozen audit/brand exports are historical, not active instructions. Avoid a competing master, untracked progress, force pushes or false test claims.
