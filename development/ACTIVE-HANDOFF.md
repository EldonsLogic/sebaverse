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

## Correction round 1 of 2 — started 26 November (founder: "Fix them first")

Founder chose to fix should-fix 1–3 before a PR. Root (Claude) owns `web/src/demo/{lesson.ts,Demo.tsx,state.ts,state.test.ts,demo.css,messages.ts}` for this round. Plan: (2) feedback states the outcome in text, not only colour; (1) equations and bars read right to left; (3) chosen answer shown on feedback. Then rerun model tests, typecheck, build, isolation, bundle, strict browser smoke, and a fresh independent re-review. Until results are appended below, the accepted-with-notes verdict applies only to commit `46f8593` and any later source edits are UNVERIFIED.

### Correction round 1 — source edited (UNVERIFIED in browser at this commit)

Edited: `lesson.ts` (four wrong-answer headings no longer say correct; "أثمان" spelling), `messages.ts` (outcome and "you chose" strings; summary label now matches stage "خطوة مع بعض"), `state.ts` (feedback view carries `chosen` fraction), `Demo.tsx` (outcome label inside the focused h1; "اخترت" line with the picked fraction, not written into the equation; equation and fraction bars `dir="rtl"`), `demo.css` (outcome and chosen styles), `state.test.ts` (new test 10). Model tests: tsc exit 0, 10/10 pass. Still to run: typecheck, default build, isolation, bundle, strict browser smoke, screenshots, independent re-review.

### Correction round 1 — verification results (on `100d5ad` source)

Model tests 10/10; web typecheck 0; default build 0; isolation PASS (94,874); demo bundle 76,061 of 200,000 gzip bytes; strict browser smoke 29/29 (`local-demo-qa/browser-strict-round1-2026-11-26.json`). Root inspected 360 guided-feedback (correct), 360 practice-feedback (wrong, 4/16) and 1440 explanation: outcome badge, "اخترت" line and right-to-left equations/bars render as intended, no overflow. Demo server PID 47496 on 127.0.0.1:5174 is task-owned; stop after re-review. Next: independent re-review appends a dated "Re-review, correction round 1" section to `local-teaching-demo-review.md`.

### Correction round 1 — independent re-review complete

Reviewer appended "Re-review, correction round 1 — 26 November 2026" to `local-teaching-demo-review.md`: **ACCEPTED WITH NOTES**, should-fix 1–3 and wording note resolved, no regressions, no blockers. Reviewer ran model tests 10/10 and six browser runs (three paths × 360/1440) with clean storage/network/console. New non-blocking notes: heading outcome+title read without a pause (`Demo.tsx:243`), raw font values in `demo.css:311–312`, feedback aside copy after correct answers (`messages.ts:30–31`). Demo server PID 47496 stopped; port 5174 free.

## Exact next step (end of correction round 1)

Waiting on the founder: open a PR from `codex/handoff-recovery-2026-11-26` to main listing the notes as known issues, or use the last allowed correction round on the notes (then rerun model tests, typecheck, build, isolation, bundle, `tools/browser/demo-smoke.mjs`, and re-review). Never merge without the founder's word for that PR.

## PR to main — started 26 November (founder: "then shoot")

Founder approved opening a PR from `codex/handoff-recovery-2026-11-26` to main with the minor notes as known issues. Merge is NOT approved; it needs the founder's word for that PR. If no PR link is recorded below, the PR was not opened.

### PR opened

https://github.com/EldonsLogic/sebaverse/pull/5 (head `codex/handoff-recovery-2026-11-26`, base main `df12e31`, mergeable). Hosted checks at open time: Vercel `sebaverse` pass, `foundation` and `locked-install-and-audit` pass on the push run; `skeleton` pending. Vercel `sebaverse-sqcg` FAILS, but it also fails on main `df12e31`, so it is pre-existing and not caused by this PR. `skeleton` also failed on main `df12e31`; check this PR's result before merge. Next: founder reviews and decides on merge. Do not merge without the founder's word for PR 5.

## Session continuation — 26 November (founder: "continue")

PR 5 open, not merged. Hosted `Local skeleton phase checks` has FAILED on main since at least 24 November (runs 45411297208, 45412576435) at step "Enforce native/image pre-use policy": image-cves.json 19 blocking (15 need explicit review, 10 reviewed findings now have a released fix → AUTH-011 requires updating the pinned artifact and re-review); system-native-cves.json 15 need review. This is the gate working as designed, not a flake. PR 5's skeleton run was still in progress at this note. Investigating which pinned artifact and findings are involved before deciding the fix; no thresholds or exceptions will be relaxed.

Finding: the main `skeleton` failure is the known AUTH-014 hold (PostgreSQL parent image OpenSSL findings; founder chose "wait for a qualified supplier tool or image" on 20 November). No workaround, exception, threshold change or custom build will be attempted. Next: one manual read-only check for a meaningful supplier update (official image identity), plus a scan of tasks.json statuses for other eligible unblocked work.

### Supplier check result

[auth-014-supplier-check-2026-11-26.md](evidence/auth-014-supplier-check-2026-11-26.md): official `postgres:17-alpine` was rebuilt (`f9cf3e1f…`) but linux/amd64 still ships libssl3/libcrypto3 3.5.9-r0. Not a meaningful supplier update; AUTH-014 hold stays. PR 5's `skeleton` check is expected to fail for the same pre-existing reason. With DEV-010 blocked on this hold and DEV-011+ gated, no further eligible implementation work exists within current authority (consistent with the 24 November critical-path review). Waiting on founder: merge decision for PR 5; optionally a decision on how to proceed while the supplier wait continues.

## Merge of PR 5 — founder approved 26 November ("Merge PR 5")

Founder approved merging https://github.com/EldonsLogic/sebaverse/pull/5 into main with a merge commit (history preserved, no force). Known pre-existing failures at merge: Vercel `sebaverse-sqcg` and `skeleton` (AUTH-014 hold), both also failing on main. After the merge, post-merge records go on a separate branch and PR because agents never push to main directly. If main does not contain this note, the merge did not happen.

### PR 5 merged

Merged 26 November as merge commit `625794546322054499cace7867a2ea3f5d0fb836` on main (head `d502ccf`, `--match-head-commit`, no force). Hosted Foundation checks and Dependency readiness passed on that head before merge; `skeleton` (AUTH-014 hold) and Vercel `sebaverse-sqcg` are known pre-existing failures. The recovery branch is fully contained in main. This record lives on branch `claude/post-merge-records-2026-11-26` and its PR, because agents do not push to main directly.

## Exact next step (after merge)

Resume from main. No eligible implementation work exists within current authority: DEV-010 is blocked on the AUTH-014 supplier wait, and DEV-011+ are gated. Recheck the supplier manually (see `evidence/auth-014-supplier-check-2026-11-26.md`) only when there is reason to expect amd64 OpenSSL 3.5.9-r1. Otherwise wait for a founder decision. The recovery branch can be deleted once this records PR merges.

Founder approved merging records PR https://github.com/EldonsLogic/sebaverse/pull/6 on 26 November ("Merge PR 6"). If main lacks this line, that merge did not happen.

## Correction round 2 of 2 — started 26 November (founder: "let's do the next task")

DEV-010 is blocked (AUTH-014), so the only remaining authorized implementation work is the last AUTH-017 demo correction round. Branch `claude/demo-correction-round-2` from main `6ca1577`. Root (Claude) owns `web/src/demo/{Demo.tsx,messages.ts,demo.css,state.ts,state.test.ts}`. Scope: (a) audible pause between outcome and heading for screen readers; (b) outcome label uses design tokens instead of raw font values; (c) feedback side panel copy fits correct answers too. Out of scope: same-question retry (new behaviour, belongs to DEV-013/014), font subsetting. After this round no further demo corrections are authorized. Any later source edit is UNVERIFIED until results are appended below.

### Correction round 2 — source edited

`Demo.tsx`: hidden ". " after the outcome inside the h1 (pause for screen readers); side panel copy depends on feedback tone. `messages.ts`: positive-feedback aside copy ("فكرتك مظبوطة" / "اقرأ ليه الطريقة دي صح وبعدين كمّل.") and `headingPause`. `demo.css`: new `--font-body` token used by body and outcome label; outcome size uses `--text-body`. Results: model tests 10/10, typecheck 0, build 0, isolation PASS (94,874), demo bundle 76,138 of 200,000, foundation exit 0. Still to run: strict browser smoke, screenshots, independent re-review.

### Correction round 2 — browser results (source `4945489`)

Strict `demo-smoke.mjs` 29/29 (`local-demo-qa/browser-strict-round2-2026-11-26.json`). Root inspected 360 guided-feedback (correct): positive aside copy shown, no overflow. Demo server PID 52574 on 127.0.0.1:5174, task-owned; stop after re-review. Next: independent re-review appends "Re-review, correction round 2".

### Correction round 2 — independent re-review complete

Reviewer appended "Re-review, correction round 2 — 26 November 2026": **ACCEPTED WITH NOTES**, all three round-1 notes fixed, no regressions, no blockers; model 10/10 and six browser runs at 360/1440 with clean storage/network/console. Remaining notes: h1/h2 font family not tokenised (`demo.css:74`), same side-panel background for right and wrong (`demo.css:397`), plus the earlier retry/marker/font notes. Demo server stopped; port 5174 free. AUTH-017 correction budget is now used up.

## Exact next step (after round 2)

PR from `claude/demo-correction-round-2` to main is opened next; merge needs the founder's word. After that, development waits on the AUTH-014 supplier fix (amd64 OpenSSL 3.5.9-r1) or a founder decision.
