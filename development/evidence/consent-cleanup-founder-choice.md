# Consent cleanup — founder choices

21 November 2026 · DEV-010 / R046 / RISK-F3-005. This is a reviewed proposal, not deletion authority or a retention policy. No cleanup product code has been implemented or run. [Implementation plan](consent-cleanup-implementation-plan.md), [acceptance cases](consent-cleanup-acceptance.md), [independent review](consent-cleanup-plan-review.md).

## 1. Which uploads become cleanup targets?

**A — Narrow cleanup when effective tutoring consent ends (recommended).** If no qualifying tutoring consent remains for the learner, select that learner's older tutoring uploads across courses and editions. If another guardian still provides valid consent, select only the withdrawing guardian's older uploads, and only when that guardian has no other qualifying consent. Duplicate, ineffective/expired and reporting-only withdrawals do not trigger tutoring cleanup. Other guardians' and learner-authored objects are not deleted solely because the learner-wide access generation changed. Some preserved old objects remain access-fenced; preservation does not restore access.

**B — All older tutoring uploads whenever a qualifying tutoring consent is withdrawn.** Select all older uploads for that learner and tutoring purpose, including uploads by another guardian who still consents. This is broader deletion and must be chosen explicitly. Duplicate, ineffective and reporting-only records still do not trigger it.

Uploads after the captured withdrawal cutoff, unrelated learners/tenants/purposes and new objects created after regrant are protected under either choice. Current uploads do not record a specific consent ID, so the system cannot infer historical reliance on a particular consent record. The intent captures an explicit approved cohort at the withdrawal event; it never uses generation alone as authority.

## 2. Which stored files should selected targets lose?

**A — Original source and derived manifest (recommended).** Matches existing uploader-initiated whole-object deletion, removes stranded source files and releases their charges only after confirmed deletion. A later grant does not restore them; the uploader must submit a new object.

**B — Derived manifest only.** The accepted original stays inaccessible and charged. Before enabling this option, approve the retained source's purpose, retention/deletion route and user visibility. Those decisions are currently unknown; choosing this option alone does not permit indefinite retention.

## What either choice does not approve

No real-data use, public deletion endpoint, arbitrary worker targets, relaxed gates or new retention timetable. Exact minimum fields and retention/access rules for operational intent, upload tombstone and consent/audit records remain a separate G3/privacy decision before real-data release. This synthetic implementation can test mechanics without inventing that policy. No legal clearance is inferred.

The technical proposal preserves existing manifest lock serialization, keeps cleanup file I/O outside transactions, persists committed intents, retries blocked writers and partial purges, prevents duplicate refunds and requires qualified deletion durability before terminal credit. Acceptance scenarios are planned, not passed. F3 and RISK-F3-005 remain open until implementation, relevant policy decisions, meaningful tests and independent acceptance are recorded.

## Verification of this planning checkpoint

Root `make foundation-check` exited 0: artifact/economics/foundation checks and 179 helper tests passed. `git diff --check` passed. The independent review rechecked the final cohort/file choices; root applied the remaining manifest-serialization wording and blocked-page acceptance clarifications. These checks validate the planning artifacts only. No cleanup code, migration, queue or deletion ran, and no policy choice is approved until the founder answers.

## Founder selection — 21 November 2026

Founder selected narrow loss-of-consent targeting and removal of originals plus derived files, recorded in U25/AUTH-015. These two choices are resolved; no other alternative is active. Retained operational/audit fields and lifetime remain unapproved before real-data release. Implementation starts with atomic intent capture; file purge and quota settlement are not implemented by that slice.
