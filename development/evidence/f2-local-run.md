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

Second actual run43595873985 completed scanner reports and correctly blocked original image:582 matches,217 High+4 Critical. Native-system report72 matches (71 Medium+1 Negligible); supplier-core1 Medium (CVE-2017-8806, applicability requires review). These are scanner matches, not confirmed exploitability. Raw reports+SBOMs+KEV+original pin preserved at f2-rejected-image-43595873985/. Advisory DBv6.1.10 built2026-11-14T06:19:25Z; scanner receipts include actual tool/version/DB provenance. No database was started.

Per predeclared F2 scope, immutable official PostgreSQL17-alpine candidate17.12-alpine3.24 replaces rejected17.11 Debian candidate for evaluation; registry indexd3244e8ce3f165ee3c93d9c4a4b1d0fe48b3a89e2287b717fdcbbde92d405065, linux/amd64 leaf005c5c37db96c1e6652a79ea31f9886402fba81ac95dc2db897739121dd7f8f2. Same database family; no new stack choice or pre-use waiver. Actual candidate scan43596204128 also failed:65 matches,32 High+3 Critical, blocking matches from embeddedGo1.24.6 in /usr/local/bin/gosu. Full raw evidence preserved in f2-alpine-candidate-43596204128/. No gate passed or database started.

## Hardened verifier regression evidence

Root reran34 synthetic policy regressions:allpassed. Positive fixtures are complete synthetic inventories/receipts, never reported as real scanner results. Negative cases assert their specific expected policy error, covering missing/malformed reports, nestedDBvalidity/freshness, source/digest/OS/architecture substitutions, suppressions, KEV, severity/explicitreview, changed native/notices/inventory and scanreceipt hashes. Whole foundation suite now56passed (22existing+34new). Dependency checker and compile checks passed.

Verifier now captures actual bounded Grype execution receipts, checks actual tool/schema/DB/source identities and rejects unreviewed/blocked matches. PostgreSQL runner replays the current verifier and all evidence/policy hashes before allocating credentials or starting a container. This is an improvement to phase verification; it does not make either blocked image acceptable. Fresh clean-CI capture/schema path remains to be checked.

##15 November continuation

Root and fresh independent reviewer ran the completed policy suite:46 tests pass. Root whole foundation run:68 tests pass (22 foundation/dependency+46 policy/runner tests). Backend rerun83pass/1integrationdeselected; Django0issues. `make dependency-check` passes.

The final14November hardened CI43596679254 reached its findings gate using real scan-execution receipts and returned the expected held matches, without a report-schema/capture failure:36 High/Critical/Unknown image matches,65 unreviewed image matches,72 unreviewed system-native and1 suppliercore. Raw receipts/config, native notices/status, authenticated Ubuntu candidate metadata and reports now preserved in f2-hardened-run-43596679254/. This does not approve the findings.

Independent review saved in f2-independent-review.md. Test-only static derivative drafted in infra/local/postgres/:no RUN, exact official platformparent, authored fail126 replacement for effective gosu path, USERpostgres. Stub actualshellcheck exits126; no image built or executed. Derived digest/provenance/source binding and fresh scans still required. Lower OCI layers retain original bytes. Loader-environment integrity was independently flagged; fixes/negative tests are being completed before any future native use.

Final local15November checks:8 loader-environment guard tests pass; whole foundation/policy suite76pass (22existing+46policy/replay+8loader). Inventory and runner reject LD_LIBRARY_PATH/LD_PRELOAD/LD_AUDIT and all nonempty DYLD_* before evidence/native access; messages never include values. CI explicitly removes those three Linux loader overrides for native inventory and replay. Synthetic positive fixtures deliberately start from a clean loader environment; separate hostile tests preserve negative coverage.46 policy tests also pass when launched with a synthetic inherited LD_LIBRARY_PATH.

Local DB options now explicitly set gssencmode=disable and require_auth=scram-sha-256, retaining loopback-only purewrapper configuration.83 backend tests and Django system check pass after that change. This is configuration proof, not actual handshake or native safety proof.

Final actual Linux run43689700627 at87ba3f9:foundation43689700548 and dependency43689700711 succeeded. Hardened skeleton workflow reached the findings gate and failed on unchanged36High/Critical/Unknown image matches plus65/72/1unreviewed image/native/core matches. PG startup/integration skipped. Full exact artifact retained in f2-linux-43689700627.zip with SHA256/source/run metadata in its companionJSON. No schema/capture/loader regression was reported before the policy stop.
