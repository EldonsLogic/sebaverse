# Developer workflow improvement ledger

This ledger concerns developer workflow; production tutor/model changes still follow architecture/release gates. No measured speed, cost or educational gain is implied.

## IMP-001 — Make phase progression checkable (U14)

Observed baseline: prior phase plan described gates but had no development task/phase consistency checker. Change: phase-gates.json plus check_foundation.py and adversarial negative fixtures reject missing test/review evidence and premature next-phase starts. Measurement: actual negative-fixture results and independent review go in evidence/foundation-run.md; until run these are proposed checks, not measured outcomes. Acceptance: each defined invalid transition fixture is rejected, valid foundation state passes, and later work remains planned. Rollback is the prior Git commit, but removing the U14 requirement itself needs founder instruction; a checker defect is fixed rather than bypassed.

## IMP-002 — Prevent stale instructions after handover

Observed issue from fresh reviewer: frozen audit export contains historical AGENTS.md and folder migration record predates shortcut removal. Change: root instructions mark snapshots historical; dated correction preserves the old event and records current path. Verification: exact current rules, source note and checker results; no claim another client has loaded them until actually observed.

## IMP-003 — Reject a completed task with nonexistent proof

Fresh independent review found that a nonempty evidence string could mark a task done even if the file did not exist. Root reproduced the precise invalid fixture: accepted before fix = true. Change: require existing evidence files for completed tasks and add a permanent negative test. After change the invalid fixture is rejected and 14 contract/phase tests pass. This is a measured one-case correctness improvement, not a speed/cost/product-efficacy claim. Reviewer rechecks the final implementation; actual run evidence goes in foundation-run.md.

## IMP-004 — Tiered context loading (U18)

Observed baseline, 16 November 2026: the session read order in WORKFLOW.md section 1 named 18 files totalling 309,440 bytes, including tasks.json (53,310) and requirements.json (66,732), before any task work. Change: QUALITY-BAR.md section 1 defines always, per-task and on-demand tiers; `tools/brief.py` prints a task with its requirement rows and phase gate. Measured: `python3 tools/brief.py DEV-007` outputs 3,017 bytes; the always tier (AGENTS.md, CURRENT-STATE.md, QUALITY-BAR.md) is about 23 KB. Token counts and effects on agent accuracy were not measured. Risk: an agent misses a rule it no longer reads; mitigation is that AGENTS.md still carries every standing rule and the per-task brief carries the acceptance criteria. Rollback: restore the previous read-order sentences from Git.

## IMP-005 — Effort proportional to risk (U18)

Observed baseline: F2 (commits b40a304 to f952d7f) took 19 commits and about 130,000 inserted lines, about 1,600 of them under backend/ and web/, to exit a synthetic loopback-only skeleton; most effort went on native and image advisory triage. Change: QUALITY-BAR.md section 2 requires a stated threat and budget before hardening work, a baseline for synthetic stages, and escalation to the founder after two failed attempts. No gate or threshold is changed. Measurement to collect: commits and elapsed days per phase from F3 onward, and what a user can do at each exit. No improvement is claimed yet.
