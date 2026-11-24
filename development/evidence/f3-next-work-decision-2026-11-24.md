# Next useful F3 work: founder decision

24 November 2026 · Base `6a72add` · R041/R042/R043/R099. The risk is spending more time on peripheral hardening while no tutoring capability is demonstrated, or silently bypassing a task/runtime gate. Budget for this assessment: one document review and independent scope check. No new implementation, packages, runtime execution or gate changes.

## Current critical path

The latest original [skeleton run 45140735323](https://github.com/EldonsLogic/sebaverse/actions/runs/45140735323) passed 683 DB-free backend cases (one PostgreSQL test deselected) and built 140 web modules, but failed native/image pre-use checks. PostgreSQL and browser steps were skipped. The gate reports 19 unresolved image matches, 15 image matches requiring review, 10 released fixes ending reviewed findings and 15 system-native matches requiring review. These categories overlap. Separate [foundation 45140735356](https://github.com/EldonsLogic/sebaverse/actions/runs/45140735356) and [dependency 45140735290](https://github.com/EldonsLogic/sebaverse/actions/runs/45140735290) runs passed. No rerun was requested. Existing pins and AUTH-014 supplier wait remain.

DEV-010 remains incomplete. A qualified database supplier update would not by itself finish F3: scanner/runtime qualification, one-source worker authority/ADR disposition, storage/concurrency and actual Arabic/bilingual R039 extraction fidelity also remain. The source-writer and manual-cleanup increments have authored evidence, not real database qualification. There is no newly identified bounded code fix that removes those held execution dependencies. Do not invent another hardening task to keep activity visible.

DEV-011 currently depends on DEV-007 and complete DEV-010, and AUTH-004 covers DEV-007–010 rather than granting DEV-011 execution. Existing curriculum code is strict record/bundle validation, not a publication service. The 23 November external review P02/P08 gives a useful next component, but is a proposal, not authorization. QUALITY-BAR section 2 and WORKFLOW sections 2/5 require a decision before changing this sequencing. All F3 exits and later-phase boundaries remain mandatory.

## Option A — authorize one offline publication-preflight slice (recommended)

Explicitly authorize a narrowly bounded DEV-011 structural preflight increment in the **same F3**, before DEV-010 completes. Record the exception as a new founder approval before implementation. Preserve full DEV-011's original dependencies/readiness and every existing F3 exit; track only the independent sub-slice as eligible. No claim that DEV-010 or DEV-011 is done.

Deliver one pure, bounded candidate-release preflight using original three-subject fixtures and the current strict versioned curriculum contracts. Proposed owned implementation paths are `backend/modules/curriculum/publication_preflight.py`, its independent `backend/tests/curriculum/test_publication_preflight.py`, and a small contract/acceptance note. No new endpoint, UI, database model/migration or dependency. Exact file/API selection follows the approved scope and independent design review.

Acceptance:

1. Enumerate the exact item/rubric/source/objective/profile/edition versions selected by the candidate manifest and validate their immutable bindings against a separately validated authored-fixture inventory, not a roster invented by the candidate itself. Fail empty, missing, extra, duplicate, stale or unvalidated candidates; no automatic “latest” lookup or hash inferred from metadata.
2. Reuse current audience, provenance, expiry/rights and cross-version checks. A private overlay cannot silently become a shared source. Reviewer labels remain metadata, never server-derived authority or proof of legal clearance.
3. Structural output is explicitly non-authorizing. It cannot mark content approved, publish or index it, grant access, change grades/mastery, schedule processing, or return an assessment-ready decision. No source text or answer key in diagnostic output.
4. Record actual-grader and educator review obligations for each affected item. An unavailable/unexecuted semantic self-check leaves that item blocked for assessment publication; never replace the production grader with substring matching or a fake successful callback. Human-review modes retain review, not an invented deterministic grade.
5. Tests include three authored subject profiles, separate private/shared candidates, immutable-version changes, rights drift, incomplete manifest coverage and fail-closed unknown capability. Frozen assessment holdouts remain separate; no private uploads or child data enter CI.
6. Run relevant curriculum tests and existing backend/document/foundation checks, record actual failures/results and independent source review, then commit/push the verified increment. Do not treat these as a phase pass or runtime result.

Bound: one engineering day and at most two correction cycles. Zero paid calls. No native SDK, scanner, image or database execution; no provider/audio, real content/minors, deployment, scheduler, new credential/language policy, source build, renewed exception, review rebinding or threshold change. If it cannot fit these limits, stop with concrete options rather than expand it.

This component makes candidate validation executable ahead of integration. It does **not** create a live tutor or resolve the supplier blocker. Semantic grading and a learner-facing vertical slice still follow their authorized task/phase gates. Current DEV-011 names `make test-curriculum`, but that target is absent; an approved slice must define a real focused test command and run existing contract/content-isolation checks, never label a nonexistent target passed.

## Option B — retain the current dependency and wait

Keep DEV-011 ineligible. Preserve the supplier-wait decision and the current qualified-use restrictions. Resume the held path only on a meaningful supplier update and the already-required reviews. No further arbitrary hardening, fresh runtime route, repeated CI dispatch or silent phase bypass. Unblock date is unknown; no new learner capability can be promised under this option.

## Decision status

**Pending founder choice.** This document proposes scope only. It does not amend approvals, task dependencies, phase statuses or ADRs. Independent critical-path/scope review is recorded separately before presenting the choice. The actual founder response must be captured verbatim with a new stable source/approval ID before any Option A code starts.
