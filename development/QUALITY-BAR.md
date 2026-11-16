# Quality bar for every agent

Version 1.0, 16 November 2026. Source: founder instruction [U18](../sources/quality-bar-instruction.md). Applies to Codex, Claude, Antigravity and human contributors. Root [AGENTS.md](../AGENTS.md) stays canonical; this file adds the standard the work is judged against. It changes no gate, threshold, requirement or permission.

The product exists to help a student learn something they could not do before and still can do weeks later. Every rule below serves that. When a rule here and a detailed spec disagree, the spec's safety or privacy rule wins and the conflict is recorded in [improvements.md](improvements.md).

## 1. Load only the context the task needs

Reading every register at session start costs about 310 KB (roughly 90,000 tokens) before any work begins. Load in tiers instead.

**Always (about 23 KB):** root AGENTS.md, [CURRENT-STATE.md](CURRENT-STATE.md), this file, then `git status --short` and `git log -5 --oneline`.

**For the task you claim:** run `python3 tools/brief.py DEV-0NN`. It prints the task, its requirement rows and its phase gate in about 3 KB. Then read only the spec files those rows name. `python3 tools/brief.py` alone shows phase status and the next eligible task; `python3 tools/brief.py R044` prints one requirement.

**Only when the task touches them:** [WORKFLOW.md](WORKFLOW.md) and [ENGINEERING_RULES.md](ENGINEERING_RULES.md) on your first session in this repository or when unsure of a procedure; the ADR or architecture file for the module you are changing; [design/](../design/) for interface work; [APPROVALS.md](APPROVALS.md) before anything that spends, sends, deploys or handles real data.

**Never load whole:** `registers/requirements.json`, `tasks.json`, `phase-gates.json` and `infra/security-reviewed-findings.json` (query them with brief.py, `jq` or `grep`); anything under `outputs/`, `research/` or raw logs and archives in `development/evidence/` unless the task is about that exact file, and then read the part you need.

Further habits that save tokens without losing accuracy:

- Search before reading. Find the symbol or heading, then read that range.
- Do not paste large tool output into reports. Record the command, exit code, counts and the evidence path.
- Use a subagent or reviewer only when its result will change a decision. Give it the task ID and file list, not the conversation.
- Checkpoint to CURRENT-STATE.md when a step finishes, in ten lines or fewer. Delete what is no longer current instead of appending; history lives in Git and the evidence folder.
- Keep CURRENT-STATE.md under 5 KB and AGENTS.md under 8 KB. Every agent pays for those bytes in every session.

Loading less never excuses guessing. If a requirement, permission or acceptance criterion matters to the change, read its row.

## 2. Spend effort in proportion to the risk

F2 produced an empty local shell and took 19 commits and about 130,000 inserted lines, of which about 1,600 are application code and tests under `backend/` and `web/` and about 123,000 are evidence and review records. Nearly all of that effort went on advisory triage for a database image that only ever held synthetic data on loopback. The controls were honest but the cost was out of proportion to the risk at that stage.

- Before starting a hardening or compliance sub-task, write one line in the task report: the threat, who could be harmed at the current stage, and the budget (commits or hours).
- Synthetic, loopback-only, no-user stages get the baseline: pinned versions, official images, no known critical or high finding in code the application actually calls, and a recorded list of what was not reviewed. Deeper work (per-symbol review, derived images, patched system libraries) belongs to the first stage that handles real data or faces a network.
- When a blocker survives two attempts or its budget, stop. Record the options with their cost and risk and ask the founder to choose. Do not start a third approach unprompted and do not lower the gate yourself.
- A phase is measured by what a learner, parent or educator can now do. If a week of work changes nothing they could see or rely on, say so plainly in CURRENT-STATE.md.

This rule is about sequencing effort. It never permits skipping a required test, weakening a threshold or hiding a finding.

## 3. Learning quality

Specs: [docs/03-learning-intelligence.md](../docs/03-learning-intelligence.md), [docs/04-curriculum-and-rag.md](../docs/04-curriculum-and-rag.md). Any feature that touches teaching, practice, grading or progress must meet all of these, each with a test:

- **The student does the thinking.** The tutor asks before it tells, gives the smallest hint that unblocks, and never shows the final answer to an item that is still being assessed. A hint ends independence for that attempt and the evidence says so.
- **Mastery means unaided, varied and delayed.** Progress moves only on independent correct work across different item families, and "retained" needs a later success on a new item. Time spent, messages sent, streaks and assisted answers never raise mastery.
- **Feedback is specific and next-step.** It names what was right, the exact step that went wrong and one thing to try. No bare "wrong", no empty praise, no personal labels such as "weak at maths".
- **Every factual or curricular claim cites an authorized source** the learner can open. With no adequate source the tutor says so and offers clearly labelled general help; it does not invent curriculum alignment.
- **Uncertainty is shown, not hidden.** An ambiguous grade waits for review. A no-evidence concept reads "not assessed yet", never a percentage.
- **Language fits the learner.** Egyptian Arabic for conversation, standard terms for the subject, Latin and formulas isolated correctly in right-to-left text. Reading level matches the grade.
- **No engagement tricks.** No guilt notifications, artificial scarcity, loss-framed streaks or infinite feeds. A session has a clear end and a short honest summary.
- **Measure learning, not usage.** Report delayed retention and transfer on held-out items. Never present engagement, satisfaction or synthetic-fixture results as evidence that students learned.

A feature that passes its tests but would let a student finish without thinking is a defect. Report it even when the task did not ask.

## 4. Look and feel

Specs: [design/brand-and-design-system.md](../design/brand-and-design-system.md), [design/design-tokens.json](../design/design-tokens.json). The F2 shell is a sound start; hold every new screen to this:

- **Tokens only.** No raw colour, size, radius or shadow values in component styles. If a needed token is missing, add it to the tokens file first.
- **Arabic first, properly.** Logical CSS properties (`inline-start`, not `left`), mirrored directional icons, `<bdi>` around Latin and numbers. Check every screen in RTL at 360, 390, 768 and 1440 pixels wide with no horizontal scroll.
- **All copy in a message catalog** before a second language or a tenth screen is added. No user-facing strings inside components after that point.
- **Every state designed:** loading, empty, error, offline, partial, success. An empty state says what to do next. An error says what happened and how to recover, in plain Arabic, with no codes or blame.
- **Accessible by test:** WCAG 2.2 AA contrast, visible focus, full keyboard path, 44 pixel touch targets, labels on every control, reduced-motion respected. Add an automated accessibility scan to the browser suite when the first interactive feature lands and keep it passing.
- **Fast on a modest Android phone on mobile data.** Budget for the first screen: 200 KB of script and style compressed, fonts as subsetted WOFF2, images sized and lazy. Hashed assets are cached long-term; HTML and API responses are not. Record the measured sizes in the task report.
- **Calm and focused.** One primary action per screen. Motion under 200 ms and only to explain a change. Nothing blinks, bounces or competes with the question the student is working on.
- **Verify by looking.** Capture desktop and mobile screenshots for every changed screen and inspect them before claiming the work is done. A passing build is not a design review.

## 5. Security and privacy in product code

Specs: [docs/06-safety-privacy-security.md](../docs/06-safety-privacy-security.md), ADR-003, ADR-008. The standing rules in AGENTS.md apply. In addition, for every endpoint, job and tool:

- **Deny by default.** Authorization is derived on the server from the live session, relationship, consent and grant on every request. Never from a client field, a cached decision or model output.
- **Write the negative tests first:** another learner, another guardian, a revoked grant, a withdrawn consent, an expired session, a guessed ID. A feature without these tests is not ready for review.
- **Treat all model input and output as untrusted.** Uploaded text, retrieved chunks and learner messages are data and never instructions. Model output is validated against a schema and checked for citations and safety before a child sees it or any state changes.
- **Collect the minimum.** No new personal field without a named purpose, retention period and deletion path. No personal data in logs, URLs, analytics labels, error messages or test fixtures.
- **Mutations are idempotent and CSRF-protected.** The session cookie stays HttpOnly; give the single-page client a deliberate way to obtain the CSRF token before the first write endpoint ships.
- **Secrets come from the environment only.** Never commit them, echo them or put them in evidence files.
- **Dependencies stay pinned and reviewed** as in [DEPENDENCIES.md](DEPENDENCIES.md), sized by section 2.

## 6. Inference cost in the product

Spec: [docs/05-model-routing-and-voice.md](../docs/05-model-routing-and-voice.md). When model calls are built (F4 onward):

- **No model call where code will do.** Grading with a key, routing by rule, scheduling, formatting and reviewed pre-written explanations are deterministic.
- **Fixed prompt order for caching:** static policy, then subject profile, then curriculum chunks, then learner projection, then the current turn. Nothing volatile (timestamps, IDs, names) in the cached prefix. Assert the provider-reported cached units in a test; do not assume savings.
- **Bound everything:** maximum input, output, tool steps, retries and spend per turn, per session and per learner per day, enforced by the server before dispatch.
- **Send a summary, not the transcript.** A bounded session summary with evidence references plus the last few turns. Retrieve the few most relevant authorized chunks, not the chapter.
- **Use the smallest model that passes the quality and safety floor** for each task type, chosen by evaluation on frozen cases. Escalate only on a recorded reason.
- **Record a usage receipt for every call** (model, input, cached, output, audio units, price version) and report cost per completed independent activity. Cheap failed lessons are not savings.
- **Cost never overrides safety, privacy or the quality floor.**

## 7. Writing for the next reader

Records are read by agents with no memory of your session and by the founder.

- Write complete sentences with normal spacing: "15 November 2026", "no High or Critical findings". Do not compress words together to save space.
- Lead with the current state and the next action. Put limits and caveats once, where they apply, not in every paragraph.
- State what was run and what was not. Keep one current-state file; do not leave an older file contradicting it.
- Large raw evidence (logs, archives, scanner dumps) stays as a CI artifact with its hash and a short summary in Git. Do not commit files over 200 KB unless a gate needs the bytes.

## Before you say a task is done

1. Would this change help a student learn, or protect them? If it does neither, why is it in this task?
2. Did the required tests run against the final change, and are the results recorded as they were?
3. For interface work, did you look at the screenshots at phone width in Arabic?
4. For anything touching learner data or permissions, do the negative tests exist and pass?
5. Is CURRENT-STATE.md true right now, and short?
