# Current development checkpoint

21 November 2026. PUBLIC canonical repo https://github.com/EldonsLogic/sebaverse; workspace /Users/eldon/Documents/Sebaverse. Planning checkpoint based on `ed4d840`; inspect Git/remote. F0–F2 passed; F3 / DEV-010 in progress. No new cleanup implementation, real data, native activation, provider call or deployment.

Consent cleanup now has a concrete implementation/acceptance proposal and independent design review. Founder choices are required before implementation: exact cohort when guardians' consents overlap, and whole-source-plus-derived purge versus derived-only retention. [Decision memo](evidence/consent-cleanup-founder-choice.md), [plan](evidence/consent-cleanup-implementation-plan.md), [acceptance](evidence/consent-cleanup-acceptance.md), [review](evidence/consent-cleanup-plan-review.md). No option is approved by silence.

Recommended cohort targets actual loss of qualifying tutoring consent, not generation alone; other purpose/tenant/learner and post-regrant objects remain protected. Uploads lack specific consent-record attribution. Retained original purpose and timetable, cleanup/consent/upload audit minimum fields and retention remain unapproved G3/privacy decisions. No legal clearance or automatic historical sweep is inferred.

Technical plan uses a narrow durable cleanup intent, because existing provider/usage jobs require live actor entitlements. Preserve current manifest serialization; cleanup file I/O is outside transactions. Verify writer closure, persistent blocked-target tracking, exact cutoff/scope, storage deletion durability and once-only credit. All cleanup acceptance cases are PLANNED, NOT RUN; RISK-F3-005 stays open. No model, migration, event or worker was added.

Original hosted `ed4d840` passed 585 Linux backend tests (PostgreSQL deselected), web and separate foundation/dependency workflows. Native pre-use gate failed; database/browser skipped. [Receipt](evidence/hosted-return-ed4d840.md). This turn changes planning documents only; current product test counts are historical, not new cleanup evidence. Closing artifact checks are recorded in the decision memo.

Three actual Sol subagents prepared implementation and acceptance plans plus hosted/design verification; root integrated technical clarifications and the founder memo. Existing staged PostgreSQL suite remains 27, pending qualified execution. Historical 14-scenario evidence does not cover later patches. Production authority design requires revisions and RISK-F3-004 remains open.

Next: obtain founder cleanup choices, then implement one bounded reviewed slice under that explicit policy. Do not start destructive cleanup or invent retention rules first. AUTH-014 supplier wait, all runtime qualification and F3 exit requirements remain unchanged; no F4 work or new learner-facing feature.
