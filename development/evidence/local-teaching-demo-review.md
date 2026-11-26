# Independent review of the local teaching demo

26 November 2026 · U27/AUTH-017 · Reviewer: an independent Claude subagent (general-purpose) launched by the root integrator. I did not author any of the demo source, content, tests or tooling. I edited no source file. My only tracked write is this file; scratch scripts, screenshots and reports are in `work/demo-review-2026-11-26/` (ignored, not available in a fresh clone).

**Verdict: ACCEPTED WITH NOTES for the AUTH-017 local demonstration scope.** There are no blockers. Three should-fix items concern Arabic equation direction and how clearly feedback states the outcome. They are listed below. This verdict covers only the isolated loopback demo described in [the scope record](local-teaching-demo.md). It does not certify WCAG conformance, learning efficacy, curriculum alignment or any DEV-013/014/015, F3 or F4 phase exit.

## Reviewed snapshot

Branch `codex/handoff-recovery-2026-11-26`, HEAD `b93f858` with a clean tree. SHA-256 prefixes of the reviewed files are as follows. `web/demo/index.html` 6fd80c80a1e8, `Demo.tsx` 1bd4ccc3b1cb, `demo.css` 62f7b7aece21, `lesson.ts` 514c744ee6a0 (matches the full hash recorded in [local-demo-content.md](local-demo-content.md)), `main.tsx` be6d5c47e61c, `messages.ts` 4711ced223ea, `state.test.ts` d59caa02daa4, `state.ts` 32841c72c12d, `web/vite.demo.config.mjs` 92862a2b7af3, `tools/browser/demo-smoke.mjs` 7788a5e0a6d5, `tools/demo/check-isolation.mjs` da3638dfc7f0 and `tools/demo/measure-bundle.mjs` e829599653d4. All commands used `work/demo-toolchain/24.22.3/node`. Its SHA-256 `ba7073…e854` matched the record, and it reported v24.22.3.

## Commands run and actual results

1. **Model tests.** I followed the ACTIVE-HANDOFF recipe with output in `work/demo-review-2026-11-26/state-tests`. `tsc` with strict, NodeNext and noUnused flags exited 0. `node --test` reported 9 tests, 9 passed, 0 failed.
2. **Browser run.** `work/demo-review-2026-11-26/review.mjs` used existing Playwright with system Chrome against the already running server. `lsof` showed a single listener on `127.0.0.1:5174`. I did not start or stop that server. The run passed on the second attempt. The first attempt failed only in my own assertion, which matched the word تلميح inside the practice title "سؤال جديد من غير تلميح". I narrowed it to the hint text and reran. The report is `review-report.json`. Each of the following ran at 360×800 and 1440×1000:
   - **Path A (pointer, hint used).** Notation start, then wrong guided answer ٣/٧ after opening the hint, then wrong practice answer ٣/٨, then summary, then reset. After reset I re-entered the guided step.
   - **Path B (keyboard only, no hint).** Skip link, visual start, wrong guided answer ٥/١٤, correct practice answer ٤/٨, summary, then reset.
3. **Guard check.** `guard.mjs` calls Vite `resolveConfig` on the demo config and starts no server. Serve in demonstration mode resolved. Development mode, build, host `0.0.0.0`, host `true`, port 5177 and an added proxy were each refused with the dedicated-invocation error.
4. **Isolation check.** `tools/demo/check-isolation.mjs` against the existing `web/dist` (built 26 Nov 12:11) exited 0: `defaultBuildExcludesDemo: true`, default script/style gzip 94,874 bytes. A grep of `web/dist` found neither the demo marker nor the Arabic page title. I did not rebuild `web/dist` or rerun `measure-bundle.mjs`. I read the existing `work/demo-browser/bundle-report.json`: demo script/style gzip 75,787 of 200,000 bytes, and unsubsetted TTF fonts of 692,292 bytes.

## What I verified independently

- **No skipping the thinking step.** The primary button is disabled until a choice is made. Pressing Enter on an unchecked radio left the stage at `intro`. The model rejects `advance` from `guided` or `practice`, as well as stale, unknown or cross-step actions (`state.ts`, guarded by step and revision). Before commitment, the guided DOM contains no feedback text, result, tone attribute or hint text (leak scan empty). The practice step renders no hint control, source excerpt or feedback, and the model rejects a `hint` action there.
- **Hint use and summary.** Choosing an answer and then opening the hint keeps the selection. The summary read "استخدمت تلميح في السؤال الموجّه." after path A and "جرّبت السؤال الموجّه من غير تلميح." after path B. Both paths showed "جاوبت على سؤال جديد من غير تلميح." for practice and "مفيش درجة أو نتيجة محفوظة." Each matched what I had actually done. No copy claims a grade, mastery, readiness or learning. The footer states that responses are not recorded.
- **Reset.** After reset no radio was checked. On re-entering the guided step the hint button read "عايز تلميح؟", no hint text was shown and no previous choice carried over.
- **Privacy and network.** After every path, `localStorage` and `sessionStorage` were empty. There were no cookies (document or context), no IndexedDB databases, no Cache Storage entries and no service workers. All 18 requests per run were GET requests to `http://127.0.0.1:5174`. The single WebSocket was Vite HMR at `ws://127.0.0.1:5174`. I recorded zero console errors, warnings or page errors. The source contains no storage, cookie, fetch, XHR, beacon or external URL use, and fonts and logo are self-hosted. The served CSP was `default-src 'none'; script-src 'self'; … connect-src 'self' ws://127.0.0.1:5174; form-action 'none'; frame-ancestors 'none'`.
- **Route isolation.** `/index.html`, `/src/app/App.tsx`, `/api/v1/health/`, `/.env`, `/@fs/etc/hosts` and `/node_modules/../package.json` each returned 404. `/src/demo/state.ts` returned 200, which is expected because the dev server serves demo source. This is acceptable for a loopback-only demo.
- **Mathematics.** 1/5 + 2/5 = 3/5, 2/7 + 3/7 = 5/7 and 3/8 + 1/8 = 4/8 (unsimplified, and the stem asks for the sum before simplification). Each question has exactly one correct option, and the model test also checks this. The distractors model real misconceptions:
  - ٥/١٤ and ٤/١٦ come from adding the denominators.
  - ٣/٧ counts only the second group.
  - ٣/٨ counts only the first group.

  Each feedback text names what was right, the wrong step and one thing to try, without stating the answer outright. The hint does not give the answer. All Arabic arithmetic in feedback ("٣ زائد ١ يساوي ٤", "٢ زائد ٣") is correct. The fraction bars match each equation.
- **Screenshots.** I read the 360px intro, explanation, guided-with-hint, guided wrong feedback, practice wrong feedback and summary screenshots, plus the 1440px guided screenshot. There was no horizontal scroll or clipping, the layout is RTL, there is one clear primary action per screen and the next arrow points correctly for RTL. In my guided-with-hint captures the primary button looked pale. Measuring it after settling showed it enabled with `rgb(35,71,214)`, so the pale look was the 120 ms transition caught by my own capture timing, not a defect.

## Findings

1. **Should-fix: the equation reads in reverse for an RTL learner.** `Demo.tsx:42` (`<bdi dir="ltr" className="demo-equation__parts">`) and `Demo.tsx:55` (`FractionBar dir="ltr"`) cause this. The equation renders "٢/٧ + ٣/٧ = ؟" left to right, so a learner reading right to left meets "؟ =" first and the operands in reverse order. My measured x-positions confirm the order ٢/٧ < + < ٣/٧ < = < ؟. The Arabic sentences use the opposite order, for example "هنا ١ زائد ٢ يساوي ٣" in `lesson.ts:40` and "معاك سُبعين، وزوّدت عليهم تلات أسباع". The equation is not mathematically wrong, because equality and this addition are symmetric, and the screen-reader text is in the natural order. However, it mixes Eastern Arabic digits with a left-to-right layout. From my general knowledge, not checked against a cited textbook here, Egyptian Arabic-medium primary materials usually write such expressions right to left. For a young learner this adds reading load at exactly the step being taught. QUALITY-BAR §3 requires formulas isolated correctly in RTL text. Choose one convention (RTL expression order with Eastern digits, or LTR with Western digits), then apply it to the equation and the bar fill direction. Record that choice as a content/design decision. It is not a blocker for a local demo.
2. **Should-fix: wrong-answer feedback does not state the outcome in plain text.** `lesson.ts:73` ("حجم القطعة مظبوط") and `lesson.ts:97` ("عدد القطع صح") become the focused `<h1>` after a wrong answer. A learner or screen-reader user first hears that something is correct. Whether the answer was right is otherwise shown only by amber versus green colour (`demo.css:296–303`, `Demo.tsx:293`). The body text implies the error but never says plainly that the answer needs another look. Naming what was right first follows QUALITY-BAR §3. A short explicit outcome phrase that does not rely on colour, for example "قربت، بس المقام…", would remove the ambiguity and the colour-only cue.
3. **Should-fix (minor): the chosen answer disappears on the feedback screen.** The equation keeps "؟" even after a correct answer, and nothing shows which option the learner picked (`state.ts` `guided-feedback`/`practice-feedback` views omit choices, and `Demo.tsx:245` renders the unresolved equation). The learner reads feedback about "٣" or "١٤" without seeing their own choice. Echoing the selected fraction would make the feedback easier to connect to the choice.
4. **Note: there is no retry on the same item.** After a wrong guided answer the learner moves on to the fresh practice item, which serves as the "one thing to try". The summary is identical whether answers were right or wrong. This is truthful, since the summary reports only hint use and makes no grade claim, and it is within the approved scope. A learner can still click through by guessing and reach "خلصت التجربة". This would be a defect in a real tutoring flow (QUALITY-BAR §3 "finish without thinking") and must not be carried into DEV-013/014 as is.
5. **Note: some wording is inconsistent.**
   - The summary row label "الخطوة مع الشرح" (`messages.ts:34`) differs from the stage name "خطوة مع بعض".
   - Eighths are written three ways: "تمنات" (`lesson.ts:93`), "أثمان" (`lesson.ts:98`, `:103`) and "تُمن".
   - At 360px the stage label "خطوة مع بعض" wraps onto two lines.
6. **Note: the isolation check depends on a marker in `main.tsx`.** `check-isolation.mjs` searches for `SEBAVERSE_LOCAL_TEACHING_DEMO_ONLY`, which only `main.tsx:11` sets. A future production import of `Demo.tsx`/`lesson.ts` without `main.tsx` would not be caught. Adding an Arabic lesson string to the check, or the marker to `lesson.ts`, would close this gap.
7. **Note: some items remain open and are recorded honestly elsewhere.** Fonts are unsubsetted TTF (692,292 bytes), not WOFF2, so the first-screen budget is met for script and style only. Design tokens are restated locally in `demo.css:16–52`. Every hex value appears in `design/design-tokens.json`.

## Not run or not verified by me

- I ran no full automated accessibility scan (axe or similar), no screen-reader session and no 390/768 widths. The integrator's strict smoke covers those widths, and I did not rerun it.
- I did not rebuild `web/dist`, rerun the web typecheck or rerun `measure-bundle.mjs`.
- I did not start or stop any server or run CLI refusal tests. I checked the guard only through `resolveConfig`.
- I did not verify Egyptian textbook equation conventions against a source.
- There was no learner, educator or real-minor involvement.

## Re-review, correction round 1 — 26 November 2026

The same independent Claude subagent performed this re-review at the coordinator's request. I edited no source. Scratch files are in `work/demo-review-2026-11-26/round1/`.

**Verdict after correction round 1: ACCEPTED WITH NOTES for the AUTH-017 local demonstration scope.** Should-fix findings 1–3 are resolved. I found no regression and no blocker. The remaining notes are minor or carried over from the first review. This verdict still certifies no WCAG conformance, learning efficacy or phase exit.

**Reviewed snapshot.** I reviewed `git diff 46f8593 2ccbf9c -- web/src/demo` with the working tree clean at `2ccbf9c`. The source change is in `100d5ad`. SHA-256 prefixes:

| File | SHA-256 prefix |
| --- | --- |
| `Demo.tsx` | a71beeb480e8 |
| `demo.css` | f6557e447211 |
| `lesson.ts` | bb945ce41a41 |
| `messages.ts` | 1dd3803650f7 |
| `state.ts` | 9b9c71824ec3 |
| `state.test.ts` | ee54b296c5b2 |
| `main.tsx` | be6d5c47e61c (unchanged) |

**Commands and results**

- **Model tests.** I followed the same ACTIVE-HANDOFF recipe, with output in `round1/state-tests`. `tsc` exited 0 and `node --test` reported 10 tests, 10 passed, 0 failed. The new test 10 checks every option of both questions. It confirms that the chosen fraction is carried into the view and that only the true sum is marked positive. It also confirms that no non-sum heading contains صح or مظبوط.
- **Browser run.** `round1/review1.mjs` ran against the running server, which listened only on `127.0.0.1:5174`. I did not start or stop it. The result was PASS for all six runs, and the report is `round1/review1-report.json`. Each path ran at 360×800 and at 1440×1000:
  - **Path A (pointer, hint used).** Wrong ٣/٧ and wrong ٣/٨, then the summary, then reset and re-entry.
  - **Path B (keyboard only, no hint).** Wrong ٥/١٤ and correct ٤/٨.
  - **Path C (pointer, hint used).** Correct ٥/٧ and wrong ٤/١٦.
- **Clean-run checks.** After every run, storage, cookies, IndexedDB, Cache Storage and service workers were all empty. All 17–18 requests were GET requests to `http://127.0.0.1:5174`. The only WebSocket was Vite HMR on `ws://127.0.0.1:5174`. There were no console errors, warnings or page errors.
- **Leak scans.** I scanned the guided step before the hint, after the hint and after reset, and the practice step before commitment. None contained outcome text, "اخترت", tone attributes, the new headings or the correct-sum wording.
- **Screenshots.** I read the 360px guided-wrong, guided-correct and visual explanation screenshots, and the 1440px practice-correct screenshot.

**Status of earlier findings**

1. **Finding 1 (equation direction): resolved.** `Demo.tsx:42` and `:55` now use `dir="rtl"`.
   - Measured x-positions decrease strictly in DOM order, for example ٢/٧ at 223, + at 197, ٣/٧ at 163, = at 138 and ؟ at 114 at 360px. The expression now reads "٢/٧ + ٣/٧ = ؟" from the right, matching the Arabic sentences.
   - Each stacked fraction is still isolated LTR, so the numerator sits correctly over the denominator.
   - Bars fill from the right, with the first group to the right of the second, on the intro and visual explanation screens.
2. **Finding 2 (outcome stated only by colour): resolved.**
   - The focused `<h1>` now begins with "لسه مش الإجابة الصحيحة" or "إجابتك صحيحة" (`Demo.tsx:243`, `messages.ts:37–38`). Its accessible name includes that outcome on every wrong and correct path.
   - The wrong-answer headings at `lesson.ts` guided-size, guided-second, practice-first and practice-size now name the error. They are mathematically accurate: ٣/٧ and ٣/٨ do miss a group, and ٥/١٤ and ٤/١٦ do change the denominator.
   - The outcome badge contrast is 6.06:1 (warning) and 5.45:1 (green), by my own computation from the token hex values.
3. **Finding 3 (chosen answer not shown): resolved.** A visible "اخترت" line shows the picked stacked fraction, and screen readers hear "اخترت ٣ على ٧" and similar (`Demo.tsx:297`). The equation keeps "؟" instead of showing a false equality, which I agree with.
4. **Finding 5 (wording): resolved.** The summary row label is now "الخطوة مع بعض", and eighths now use "أثمان".

Findings 4, 6 and 7 from the first review are unchanged notes: no same-item retry, the marker-only isolation check, and unsubsetted TTF fonts.

**New notes (not blockers)**

- **The heading's accessible name runs on.** Screen readers hear the outcome and title as one unbroken phrase, for example "لسه مش الإجابة الصحيحة المقام اتغيّر", because the badge is a block `<span>` with no punctuation (`Demo.tsx:243`). A trailing "،" or "." in the outcome text, or a visually hidden one, would give screen readers a pause.
- **The outcome badge uses raw values instead of tokens.** `demo.css:311–312` sets a literal `font-family` and `font-size: 1rem` rather than `var(--text-body)`. This is a small tokens-only deviation.
- **The side panel says to review the step even after a correct answer.** The feedback aside still reads "راجع الخطوة / اقرأ الملاحظة وبعدين كمّل" (`messages.ts:30–31`). This is acceptable but could be tuned. The wording predates this round.
- **"إجابتك صحيحة" is a per-item judgement on an authored fixture.** The summary still makes no grade, mastery or readiness claim, and none was added, so this stays within scope.

**Not run in this round.** I did not rerun the web typecheck, default build, isolation check, bundle measurement or the integrator's strict smoke. I checked the 390 and 768 widths only through the root's reported 29/29 smoke, not myself. I ran no axe scan and no real screen reader.

## Re-review, correction round 2 — 26 November 2026

The same independent Claude subagent performed this re-review. I edited no source. Scratch files are in `work/demo-review-2026-11-26/round2/`.

**Verdict after correction round 2: ACCEPTED WITH NOTES for the AUTH-017 local demonstration scope.** All three new notes from round 1 are resolved. I found no blocker or regression. This verdict does not certify WCAG conformance, learning efficacy or any phase exit.

**Snapshot reviewed.** I reviewed branch `claude/demo-correction-round-2`, with the tree clean at `ca09314`, and the source diff `git diff 6ca1577 4945489 -- web/src/demo`. Files changed between `2ccbf9c` and `6ca1577`: none. The changed files' SHA-256 prefixes are `Demo.tsx` 112fa1ffc29d, `demo.css` 84be279b86a2 and `messages.ts` 712bc77fda0e. `lesson.ts`, `state.ts` and `state.test.ts` are unchanged.

**What I ran**

- **Model tests.** I used the same recipe, writing output to `round2/state-tests`. `tsc` exited 0 and `node --test` passed 10/10.
- **Browser paths.** I ran `round2/review2.mjs`, which is my round-1 script plus checks on the side panel and on the heading's accessible name. I ran it against the running server and did not start or stop that server. It passed all six runs: paths A, B and C at both 360 and 1440 pixels wide.
  - The first attempt failed only because my own check expected `outcome + ". "`. Chrome reports the name as `outcome + " . "`, with an extra space, so I relaxed the check to allow optional whitespace before the full stop.
  - The checks cover wrong guided and practice answers, correct guided and practice answers, the hint path, the keyboard-only path and reset.
  - No outcome text, side-panel feedback copy or pause span appeared before an answer was committed.
  - Storage, cookies, IndexedDB, cache and service workers were empty. Every request was a GET to `127.0.0.1:5174`, and the only WebSocket was the dev server's own. There were no console errors.
- **Screenshots.** I looked at the 360px correct guided answer and the 1440px wrong practice answer.

**Round-1 notes**

1. **Heading pause: resolved.** `Demo.tsx:245` adds a hidden `". "` (`messages.ts:34`). The heading's accessible name is now, for example, "لسه مش الإجابة الصحيحة . المقام اتغيّر" and "إجابتك صحيحة . جمعت البسطين وثبّتّ المقام".
2. **Tokens: resolved for the outcome label.** `demo.css:58` and `:312` use `--font-body`, and the outcome label uses `var(--text-body)`.
3. **Side-panel copy: resolved.** `Demo.tsx:190` shows "فكرتك مظبوطة / اقرأ ليه الطريقة دي صح وبعدين كمّل." after both correct answers. It shows "راجع الخطوة / اقرأ الملاحظة وبعدين كمّل." after all four wrong answers.

**Remaining notes (not blockers)**

- **Headings font not tokenised.** `demo.css:74` still writes out `h1, h2 { font-family: Alexandria, … }` instead of using a token.
- **Side panel looks the same for right and wrong answers.** The positive side panel keeps the same peach `demo-aside--quiet` background (`demo.css:397`). This is only cosmetic, because the heading states the outcome in text.
- **Earlier notes unchanged.** There is still no retry on the same question, which is deliberately out of scope. The isolation check still relies only on the marker string, and the TTF fonts are still not subsetted.

**Not run.** I did not run the web typecheck, the default build, `check-isolation.mjs`, the bundle measurement or the integrator's strict smoke script. I checked no 390 or 768 widths myself. I ran no axe scan and no real screen reader.
