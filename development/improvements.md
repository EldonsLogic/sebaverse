# Developer workflow improvement ledger

This ledger concerns developer workflow; production tutor/model changes still follow architecture/release gates. No measured speed, cost or educational gain is implied.

## IMP-001 — Make phase progression checkable (U14)

Observed baseline: prior phase plan described gates but had no development task/phase consistency checker. Change: phase-gates.json plus check_foundation.py and adversarial negative fixtures reject missing test/review evidence and premature next-phase starts. Measurement: actual negative-fixture results and independent review go in evidence/foundation-run.md; until run these are proposed checks, not measured outcomes. Acceptance: each defined invalid transition fixture is rejected, valid foundation state passes, and later work remains planned. Rollback is the prior Git commit, but removing the U14 requirement itself needs founder instruction; a checker defect is fixed rather than bypassed.

## IMP-002 — Prevent stale instructions after handover

Observed issue from fresh reviewer: frozen audit export contains historical AGENTS.md and folder migration record predates shortcut removal. Change: root instructions mark snapshots historical; dated correction preserves the old event and records current path. Verification: exact current rules, source note and checker results; no claim another client has loaded them until actually observed.

## IMP-003 — Reject a completed task with nonexistent proof

Fresh independent review found that a nonempty evidence string could mark a task done even if the file did not exist. Root reproduced the precise invalid fixture: accepted before fix = true. Change: require existing evidence files for completed tasks and add a permanent negative test. After change the invalid fixture is rejected and 14 contract/phase tests pass. This is a measured one-case correctness improvement, not a speed/cost/product-efficacy claim. Reviewer rechecks the final implementation; actual run evidence goes in foundation-run.md.
