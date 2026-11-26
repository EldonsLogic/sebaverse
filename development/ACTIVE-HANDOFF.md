# Active cross-agent handoff

26 November 2026 · integrator `/root` · canonical `/Users/eldon/Documents/Sebaverse` · origin `https://github.com/EldonsLogic/sebaverse`. **Read this with actual Git.** Last main baseline `df12e3150c545c3558799af485d44464ce747d0b`. Recovery branch: `codex/handoff-recovery-2026-11-26`. Its checkpoint is pending verification, not an accepted main release. Use actual Git/remote SHA.

## Resume without losing work

1. Read AGENTS.md, CURRENT-STATE.md and QUALITY-BAR.md, then inspect `git status --short`, `git log -5 --oneline`, `git branch --show-current` and the remote. Use the checkpoint branch containing this file; do not reset/stash/discard source to match main.
2. Run `python3 tools/brief.py DEV-013`. Only its `local-teaching-demo-v1` exception is active under U27/AUTH-017. Full DEV-013/014/015 and F3/F4 transitions remain held. DEV-010 is in progress; 37 PostgreSQL cases remain NOT RUN; AUTH-014 supplier wait is unchanged.
3. Live dependency metadata was reconciled for only the reviewed Node patch and demo scripts; foundation179 and full local dependency/import smoke now pass. Preserve historical/security records. Finish the exact pending demo verification below. Read the immutable evidence receipts rather than rerunning all research. No upstream Athar execution or real child/provider/database use.

## Work preserved on disk

- **Approved demo:** `web/demo/index.html`, `web/src/demo/{Demo.tsx,main.tsx,messages.ts,demo.css,lesson.ts,state.ts,state.test.ts}`. Original Arabic fraction lesson, memory-only choices/hint/fresh practice/summary/reset. Authors released ownership; root changed footer copy. No responses, accepted grades or mastery are persisted.
- **Integrator tooling:** `web/vite.demo.config.mjs`, scripts in `web/package.json`, `tools/browser/demo-smoke.mjs`, `tools/demo/check-isolation.mjs`, `tools/demo/measure-bundle.mjs`. New strict contrast/44px assertions and resolved-mode/host guard were edited AFTER the last browser pass; rerun before claiming final acceptance.
- **Node security patch candidate:** `.node-version` is now `24.22.3`; live DEPENDENCIES.md and `third-party/node-runtime-24.22.3.json` describe it. Same existing component, no new dependency/global installation. Official Darwin archive was compared with the publisher checksum, and its executable passed Apple Developer ID signature verification and independently accepted for local compatibility. Current source/metadata pin edits still need final integration checks. Historical F1 receipts remain `24.22.1`; do not rewrite them or rebind old database reviews.
- **Athar review:** `research/athar-review/`, `architecture/athar-derived-refinements.md`, appended architecture/docs/source/catalog and repository registry changes. Pin `a2e52a22fcc9e639a08c2e2040ac58479676ee24`, 43 files as data, no code/tests/packages executed. Independent acceptance is `development/evidence/athar-review-acceptance.md`. No source/content/model adopted.
- **Authority:** U27/AUTH-017 approved the isolated mock; U28 requested Athar review; U29 requires handover first. These records and task metadata were not yet committed at initial recovery. Keep them with the matching work.

## Actual evidence and its limits

- Official Node candidate: `work/demo-toolchain/24.22.3/node`; version 24.22.3; binary SHA-256 `ba7073582822078d8c90bca3facacc46690bc5366fab4b815aeef9148cd6e854`. `demo-node-toolchain.md` and `demo-node-patch-review.md` distinguish the Codex variant and official artifact. No OpenPGP verification claimed. Work/ is ignored and NOT available in a fresh clone; re-provision only from the recorded official checksum/signature evidence, never assume this path exists.
- Nine transition tests passed under official Node. Full web TypeScript check passed. Default Vite build passed, with existing upstream `use client` directive warnings. Default-build exclusion check passed; default script/style gzip was 94,874 bytes. These were before the newest host guard and strict audit assertion edits.
- `work/demo-browser/report.json` and `work/demo-browser-independent/report.json` contain matching prior reports (the tracked copy is `development/evidence/local-demo-qa/browser-before-strict-rerun.json`). The integrator report contains the earlier passing 29-entry browser report: 28 stage/width checks plus a fully asserted keyboard/reset/isolation trace at 360/390/768/1440. No external/API requests, storage writes, cookies or browser errors were observed in those flows. Root inspected desktop explanation and mobile intro/practice screenshots. Strict 44px/contrast checks still require rerun after the last harness edit.
- Independent reviewer ran a full keyboard/no-hint path and nine model tests; disposable demo bundle measured 75,787 gzip bytes. Root's canonical `bundle-report.json` is not yet present. Existing local TTF fonts total 692,292 raw bytes; WOFF2/subsetting is unresolved release-quality work. No mobile-network readiness or full WCAG certification is claimed.
- Final `local-teaching-demo-review.md` is MISSING. Prior reviewer stopped at a usage limit after useful observations. Do not fabricate its verdict. Get an independent final source/UI/test receipt or keep the demo pending review.
- Last committed backend evidence: 717 passed / one PostgreSQL deselected, foundation179. Current recovery audit: `make foundation-check` FAILS (178 of 179 helper cases pass; `test_actual_snapshot_valid` fails); `check_dependencies.py` fails because `.node-version` and `web/package.json` hashes differ from `third-party/dependency-snapshot.json`. Artifact/economics/foundation structure checks pass. Do not carry forward a green foundation claim. No new hosted result is claimed.

## Exact next operations

From repository root, with the independently qualified exact Node path (or a separately qualified matching runtime):

```sh
mkdir -p work/demo-browser
work/demo-toolchain/24.22.3/node tools/demo/measure-bundle.mjs
```

For UI: start `node web/node_modules/vite/bin/vite.js --config web/vite.demo.config.mjs --mode demonstration` from the root with the exact qualified Node binary. It must bind only `127.0.0.1:5174`. If a task-owned server already exists, identify/reuse it; never kill unrelated processes. Verify current availability rather than trusting a prior link. Run the browser script with existing reviewed Chrome/Playwright, inspect fresh screenshots, and test host/mode override refusal. Browser/startup may require ordinary host approval; a restricted-process failure is not a product pass.

Compile the model files using the recipe below, then run Node's built-in test runner. The old content note's pending wording is historical and must not be taken as the current verification status.

```sh
mkdir -p work/demo-state-tests
printf '{"type":"module"}\n' > work/demo-state-tests/package.json
work/demo-toolchain/24.22.3/node web/node_modules/typescript/bin/tsc --target ES2022 --module NodeNext --strict --verbatimModuleSyntax --noUnusedLocals --noUnusedParameters --types node --typeRoots web/node_modules/@types --outDir work/demo-state-tests web/src/demo/state.test.ts
work/demo-toolchain/24.22.3/node --test work/demo-state-tests/state.test.js
```
 Run web typecheck and the default web build first, then `work/demo-toolchain/24.22.3/node tools/demo/check-isolation.mjs` against the freshly generated web/dist, and relevant foundation checks. The bundle measurement script now creates its output parent; this recovery fix also needs verification. Do not install dependencies or change quality thresholds to hide failures. After final independent acceptance, integrate reviewed work normally; no force push or phase pass.

## Ownership and stop conditions

Root owns integration and checkpoint records. Previous source authors are released, not running background workers. Review availability must be checked afresh; old agent names/roster are historical. No current locks on source are inferred. If a budget, review, runtime or test blocks progress, record the precise condition and safe next action here BEFORE ending. Preserve a recoverable commit/remote branch even if incomplete; pending review is a valid handoff state.

## Final wrap checkpoint — 26 November

User reported 1% weekly allowance and requested wrap/log. Stopped new work. Recovery commit `3b0f801` is already pushed on `codex/handoff-recovery-2026-11-26`; the subsequent log/snapshot commit contains this final update (use actual Git SHA). Only two live dependency hashes were reconciled with dated evidence. Final foundation179 PASS and dependency evidence/local import/render smoke PASS under the authenticated official Node24.22.3 PATH. No new browser or demo acceptance. Earlier red snapshot result remains historical evidence; final demo review is still missing. Main stays at `df12e31`. Resume on recovery branch; do not merge it as reviewed product code.

## Session start — 26 November 2026, Claude (Opus 5.5) integrator

Verified before work: branch `codex/handoff-recovery-2026-11-26`, HEAD `a637951aa862a3b0e75abce0b2cdcc9cc30333a5` equal to origin, clean tree, main `df12e31`. Qualified Node `work/demo-toolchain/24.22.3/node` present, SHA-256 matches the record. Port 5174 free (no task-owned server running). Plan: (1) foundation179 + dependency checks; (2) model tests, web typecheck, default build, isolation, bundle report; (3) demo server on 127.0.0.1:5174 and strict browser rerun with fresh screenshots; (4) independent reviewer subagent writes `development/evidence/local-teaching-demo-review.md`; (5) record results, commit, push. Results will be appended below as each step finishes. If this section has no results after it, the session stopped before step 1 finished.

### Results — steps 1–2 (Claude, 26 November, on `f154390` source, no source edits)

All under `work/demo-toolchain/24.22.3/node` (SHA-256 verified) on PATH.
- `make foundation-check`: exit 0, 179/179. The `npm view timed out` JSON in its output is printed by a negative-fixture test, not a failure.
- `python3 tools/check_dependencies.py`: PASS (evidence + local import/render smoke).
- Demo model tests (recipe above): tsc exit 0; `node --test` 9/9 pass.
- `web` typecheck exit 0; default `vite build` succeeded (only upstream `use client` directive warnings).
- `tools/demo/check-isolation.mjs`: default build excludes demo; script/style gzip 94,874 bytes.
- `tools/demo/measure-bundle.mjs`: exit 0, created `work/demo-browser/bundle-report.json`; demo script/style gzip 75,787 bytes (max 200,000). Fonts still unsubsetted TTF (692,292 bytes) — known open item, not fixed.
Next: step 3, demo server on 127.0.0.1:5174 and strict browser rerun.

### Results — step 3 (Claude, 26 November, same source as `efc6a1c`, no source edits)

- Demo server: qualified Node, `vite --config web/vite.demo.config.mjs --mode demonstration`; `lsof` shows it bound only on 127.0.0.1:5174. Task-owned (started this session); stop it when review ends.
- `tools/browser/demo-smoke.mjs` (current strict 44px/contrast assertions): PASS, 29/29 (28 stage/width checks at 360/390/768/1440, 21–37 text nodes contrast-checked each, plus keyboard/reset/route isolation trace). Tracked copy: `development/evidence/local-demo-qa/browser-strict-2026-11-26.json`; bundle report copied to `bundle-report-2026-11-26.json`.
- Guard refusal: `--host 0.0.0.0`, `--mode development`, `--port 5177` and `vite build` with the demo config all exit with "The teaching demo requires its dedicated loopback-only development invocation."; no stray listeners left.
- Root inspected fresh screenshots 360 guided-hint, practice-feedback, summary and 1440 explanation: no overflow or clipping seen. Observation for review (not changed): equations render in left-to-right order with Eastern Arabic digits, so in RTL reading the result/`؟` comes first; Egyptian Arabic-medium textbooks usually write equations right-to-left.
Next: step 4, independent reviewer subagent writes `development/evidence/local-teaching-demo-review.md`. Until that file exists, the demo stays pending review.

### Step 4 in progress — independent review launched

A real independent Claude subagent (general-purpose, not an author) was launched 26 November to review source, content math, run the model tests itself, drive the demo at 360/1440 (hint path, keyboard no-hint path, wrong answers, reset, network/storage/console), and write `development/evidence/local-teaching-demo-review.md`. It owns only that file plus scratch `work/demo-review-2026-11-26/`; source is read-only to it. If this session ends before the file exists, the review did NOT complete: keep the demo pending and relaunch a reviewer with the same scope. The demo server on 127.0.0.1:5174 is task-owned and must be stopped after review.

### Results — step 4 (independent review complete)

`development/evidence/local-teaching-demo-review.md` written by the independent subagent at HEAD `b93f858`. Verdict: **ACCEPTED WITH NOTES** for the AUTH-017 local scope, no blockers. Reviewer ran model tests 9/9, its own Playwright paths at 360/1440 (hint path, keyboard no-hint path, wrong answers, reset; storage/cookies/IndexedDB empty, only 127.0.0.1:5174 requests, no console errors, CSP served), guard refusal via `resolveConfig`, and isolation check. Root confirmed finding 2 in source. Should-fix: (1) equation/bars LTR in RTL lesson, `Demo.tsx:42,55`; (2) wrong-answer headings "حجم القطعة مظبوط"/"عدد القطع صح" at `lesson.ts:73,97` with outcome only shown by colour; (3) picked answer not shown on feedback. Notes: no same-question retry (must not carry into DEV-013/014), wording inconsistencies, isolation marker only in `main.tsx`, font budget open. Reviewer did not run 390/768 widths, full a11y scan or screen reader.

Demo server (PID 44499) stopped by root; port 5174 free. Source unchanged since `a637951`.

## Exact next step (26 November, end of Claude session)

Waiting on the founder: either (a) one correction round for should-fix 1–3 in `web/src/demo/{lesson.ts,Demo.tsx,state.ts,demo.css}`, then rerun model tests, typecheck, default build, isolation, bundle, `tools/browser/demo-smoke.mjs` and a fresh independent re-review; or (b) open a PR from `codex/handoff-recovery-2026-11-26` to main with the should-fix items listed as known issues. Never merge without the founder's word for that PR.
