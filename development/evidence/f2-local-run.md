# F2 local evidence — 14 November2026

Task DEV-006, U16/AUTH-003. F2 **in progress**, not a phase pass.

Actual local macOS arm64 worktree checks:
- `make backend-check`:83 DB-free tests passed,1 PostgreSQL integration case deselected; Django check0 issues.
- Pinned Node24.22.1:TypeScript and Vite8.3.8 production build passed,140 modules. Vendor module-level `use client` warnings retained; no claim of SSR support.
- `make foundation-check`:36 preserved evidence hashes,104 requirement rows, artifact arithmetic/links and22 existing phase/dependency regression tests passed.
- `make dependency-check`:locked dependency evidence and local import/render smoke passed.
- Actual temporary-loopback browser run:Chromium156.0.8078.4 / Playwright1.62.1. Four routes at1440px/390px widths, Arabic/RTL, skip-first-tab, main-focus, no horizontal overflow, no UI exceptions/missing assets, client404/API404 and health200. Unconfigured readiness503. Screenshots complete:1314/1872px document and image heights match. Task-owned server stopped and port unreachable. Raw browser report/screenshots:outputs/f2-local-skeleton/.
- Python compile checks for phase helpers passed using project-local bytecode cache.

The first strengthened browser run failed because its not-found expectation looked for the wrong heading; corrected to actual explicit heading/title and rerun passed. Failure was in test expectation, not masked by loosening route checks.

## Native/CI evidence and holds

Syft1.57.1 cached Darwin archive SHA256:e0a74a5d2688d1254b4e17b71f068a83215e3625f846265bf6614c7ba06f3a96 verified against official release checksum. Extracted executable reports version1.57.1 commit a0c0d3890a9d79421c403e8fcadec50a2e55bf21. No install script used. This is tool verification, not a vulnerability verdict.

Actual first Linux run43595688495 at b40a304 passed dependency installation, frontend build,83 DB-free tests, checksum-verified scanners and actual native inventory (24 library files/20 Debian package owners). Stopped before DB startup:Syft exact cataloger name was incorrectly passed to tag-selection flag. Local actual CLI validation confirmed `--override-default-catalogers dpkg-db-cataloger`; fixed in915d0c6 and rerun. Original run:https://github.com/EldonsLogic/sebaverse/actions/runs/43595688495. No PG integration result may be inferred from those steps.

Independent reviewer found missing report schema/source/evidence binding in pre-use checker; hardening and synthetic negative fixtures underway. No native gate pass exists. No actual database, tutoring, account, upload, grading, model, commercial, privacy or complete accessibility result claimed. F3 has not started.
