# AUTH-020 / DEV-013 Bounded Tutoring State Machine — Independent Review

- **Date:** 26 November 2026
- **Branch:** `antigravity/dev-013-tutor-state-2026-11-26`
- **Commit SHA reviewed:** `849019f160fd36f1818204d8df0f639bbc4bffb1`
- **Scope authority:** [U32](../../sources/offline-tutor-state-instruction.md) / `AUTH-020` in [APPROVALS.md](../APPROVALS.md#L98-L100) (bounded DB-free, provider-free synthetic-fixture sub-slice of `DEV-013`).
- **Verdict:** **CHANGES REQUESTED** (4 blockers, 3 should-fix items, 4 notes).
- **Next action:** Fix the 4 blockers in `backend/modules/tutoring/state_machine.py`, update `backend/tests/tutoring/test_tutor_state.py` with negative and resume tests covering each fix, commit on `antigravity/dev-013-tutor-state-2026-11-26`, and request correction round 1 of 2 re-review.

## Scope & Integrity Summary

Commit `849019f160fd36f1818204d8df0f639bbc4bffb1` stays strictly within the `AUTH-020` scope boundary: zero new dependencies, zero database/HTTP/SSE/AG-UI/LLM calls, and no changes to phase gates or thresholds (`Makefile` lines `39-51` add `test-tutor-state-preflight` only). Live `policy.allowed` gating, model-actor rejection, hint-limit enforcement (`MAX_HINTS_PER_ITEM = 3`), `practice` reveal blocking, grounded `select_explain` retrieval/abstention, and `uncertain`/`model_proposal` routing to `review_pending` (`ambiguous`) work in the tested happy and basic negative paths, but four material defects block acceptance.

## Findings

### Blockers

1. **Deadlocked `paused` / `blocked` resume path and unintended `check_access` bypass out of `review_pending` (`backend/modules/tutoring/state_machine.py:53-56`, `402-414`; `backend/tests/tutoring/test_tutor_state.py:114,179-182`)**
   - `ALLOWED_TRANSITIONS` (`state_machine.py:55-56`) permits `'paused'` and `'blocked'` to transition only to `{'access_check', 'cancelled'}`, matching `docs/03-learning-intelligence.md:19,31` and `R023`. However, `check_access` (`state_machine.py:402-406`) rejects every `target_state` outside `('select', 'diagnose')`, and no other action in `step_session` transitions to `'access_check'`. Once a session enters `'paused'` or `'blocked'`, it can never resume, even after consent/entitlement restoration.
   - Conversely, `check_access` does not restrict the source `session.state` to `('access_check', 'paused', 'blocked')`. Because `'select'` appears in `ALLOWED_TRANSITIONS['review_pending']` (`state_machine.py:53`), a learner can invoke `check_access(target_state='select')` while in `'review_pending'` and bypass human adjudication completely (and likewise jump out of `'reflect'` or `'diagnose'`).
   - Fix: Add an explicit resume transition to `'access_check'` (or allow `check_access` from `'paused'`/`'blocked'` via `'access_check'` before re-entering `'select'`/`'diagnose'`), restrict `check_access` to entry/resume states, forbid learner-initiated exits from `'review_pending'`, and test both `'paused'` and `'blocked'` resume end-to-end.

2. **Missing item schema, edition, objective, and audience binding on `start_practice` and `submit_answer` (`backend/modules/tutoring/state_machine.py:475-494,525-585`; `backend/modules/assessment/grader.py:71-80`; `backend/tests/tutoring/test_tutor_state.py:153-161`)**
   - `start_practice` (`state_machine.py:479-481`) inspects only `item['id']`, `item['version']`, and `item['family_id']`. It does not validate `command.item` against `SERIALIZERS['item']`, require `status == 'approved'`, verify `item['edition'] == {'id': session.edition_id, 'version': session.edition_version}`, verify `{'id': session.objective_id, 'version': session.objective_version}` is in `item['objectives']`, or verify `item['audience']` permits `(session.tenant_id, session.learner_id)`.
   - `submit_answer` (`state_machine.py:531-546`) checks only `active_item_id`/`version`/`family_id` and delegates to `grade_submission`, which checks `item['audience'] == rubric['audience']` (`grader.py:78`) but has no session `edition`, `objective`, `tenant_id`, or `learner_id`. Consequently, an approved item from another edition/objective (such as `item.science` / `rubric.science` inside an `edition.quantitative` / `objective.quantitative` session) or another learner's approved `learner_private` item is graded and emitted in `EvidenceEvent` (`state_machine.py:563-585`) stamped with the session's `edition_id`, `objective_id`, and `learner_id`, corrupting downstream mastery projections in `modules.learning.ledger`.
   - Fix: Validate item schema, approval status, `edition`, `objectives` membership, and `audience` scope against the `TutorSession` in both `start_practice` and `submit_answer`, with negative tests for cross-edition, cross-objective, unapproved, and cross-learner private items.

3. **Guided-to-practice reset allows erasing hint and worked-answer exposure on the same item (`backend/modules/tutoring/state_machine.py:47,475-493,496-523,553-561`)**
   - `ALLOWED_TRANSITIONS['guided']` (`state_machine.py:47`) allows `'practice'`, and `start_practice` (`489-490`) unconditionally clears `active_attempt_hints=0` and `active_answer_revealed=False` without recording prior item exposure or emitting an attempt event for the abandoned active item.
   - Because `request_hint` (`496-510`) and `reveal_worked_answer` (`512-523`) emit no `EvidenceEvent`, a learner can start `item_A`, take hints (`practice -> guided`), reveal the worked answer (`active_answer_revealed=True`), then immediately call `start_practice` with `item_A` again (`guided -> practice`) and submit the revealed answer. `submit_answer` (`560-561`) emits `evidence_class='independent'`, `hints_used=0`, `answer_revealed=False`, allowing `project_objective_mastery` to treat an exposed/assisted item as independent mastery (`QUALITY-BAR.md` §3 defect; `docs/03-learning-intelligence.md:11`).
   - Fix: Track exposed/assisted `(item_id, item_version)` pairs across the session (or emit an `exposed`/`assisted` evidence event when abandoning a hinted/revealed active item, and prevent `start_practice` on a revealed/hinted item from emitting `'independent'`) and add a regression test proving `start_practice -> request_hint -> reveal_worked_answer -> start_practice(same item) -> submit_answer` cannot emit `'independent'`.

4. **`command.actor_role` is not bound to server-derived `TutorScope.role` (`backend/modules/tutoring/state_machine.py:306-307,371-387`; `backend/modules/access/policy.py:5-6`; `backend/tests/tutoring/test_tutor_state.py:238-242`)**
   - `step_session` checks `command.actor_role in ALLOWED_ACTORS` (`306`) and, in `resume_from_safety`, checks `command.actor_role in HUMAN_SAFETY_REVIEWERS` (`374`) alongside `policy.allowed(scope.to_access_scope())` (`378`), without verifying that `scope.role` authorizes `command.actor_role`.
   - Because `policy.PURPOSES` (`policy.py:5-6`) does not even list `'reviewer'` or allow `'teacher'` for `'tutoring'`, passing a learner's `TutorScope(role='learner', purpose='tutoring')` with `TutorCommand(actor_role='reviewer', reviewer_ref='reviewer.safety-lead')` satisfies both line `374` and line `378` — demonstrated directly in `test_tutor_state.py:238-242`. Any learner-scoped session could similarly stamp `actor_role='teacher'` or `'system'` onto `EvidenceEvent` or self-resume from `safety_pause` (`QUALITY-BAR.md` §5, `R053`, `R067`).
   - Fix: Derive/verify the acting role from a server-derived scope (for example, bind normal tutoring `command.actor_role` to `scope.role`, and model human safety resume with an explicit server-verified safety-reviewer scope/grant rather than trusting `command.actor_role` under a learner scope), and add negative tests proving a learner scope with `actor_role='reviewer'` is denied.

### Should-fix

1. **Unimplemented or dead transitions in `ALLOWED_TRANSITIONS` (`backend/modules/tutoring/state_machine.py:42-59,359-369,525-562`)**
   - `diagnose` has no diagnostic submission/review action (exiting only incidentally via `check_access(target_state='select')`); `'grade'` is never entered (`submit_answer` skips straight to `'reflect'` or `'review_pending'`); `'prerequisite'` cannot submit a check; `'review_pending'` has no human adjudication/appeal action (`grade`/`schedule` transitions are unreachable); and `cancel_turn` (`359-369`) puts the entire session into terminal `'cancelled'` (`ALLOWED_TRANSITIONS['cancelled'] = frozenset()`) rather than cancelling an in-flight turn or allowing resume via `access_check` (`docs/03-learning-intelligence.md:31`). Either implement the intended bounded actions or narrow `ALLOWED_TRANSITIONS` to match the implemented slice.

2. **`request_hint` and `reveal_worked_answer` succeed in `guided` without an active item (`backend/modules/tutoring/state_machine.py:496-523`)**
   - Entering `'guided'` via `select -> select_explain -> start_guided` leaves `active_item_id=None`, yet `request_hint` and `reveal_worked_answer` both succeed and mutate item-attempt flags (`active_attempt_hints`, `active_answer_revealed`). Guard both actions with `session.active_item_id is not None`.

3. **Idempotent command replay omits original step outputs and skips live scope check (`backend/modules/tutoring/state_machine.py:241-248,325-331`)**
   - Line `331` returns `TutorStepResult(session=session, replayed=True)` with `grade_decision=None`, `emitted_event=None`, and `abstention_reason=None`, and runs before `policy.allowed(scope.to_access_scope())` (`390`), so replaying an old `command_key` after consent revocation returns `replayed=True` on an unblocked session without re-checking live scope. In addition, `_command_digest` (`241-248`) hashes only `item` ID/version, `rubric` ID/version, and `has_model_proposal` boolean rather than full canonical `item`/`rubric`/`model_proposal` payloads.

### Notes

1. **Identifier prefix overflow into `EvidenceEvent` (`backend/modules/tutoring/state_machine.py:63,564-565`; `backend/modules/learning/ledger.py:28`)**
   - `_check_id` accepts `session_id` and `command_key` up to 96 characters, so `f'ev.{session.session_id}.{next_seq}'` or `f'idem.{command.command_key}'` exceeds `ledger.validate_event`'s 96-character `_IDENTIFIER` limit whenever `session_id` or `command_key` is >= 91 characters.

2. **Empty-string fallback via `or` (`backend/modules/tutoring/state_machine.py:348,376,403,609`)**
   - `command.target_state or 'select'` and `command.reason_code or 'safety.escalation'` treat `""` as `None` instead of rejecting an explicit empty string as invalid input.

3. **Untested paths in `backend/tests/tutoring/test_tutor_state.py`**
   - The 7 existing tests cover core happy paths and several negative checks, but do not exercise `diagnose`, `start_guided`, `start_prerequisite`, `cancel_turn`, `reveal_worked_answer` in `guided`, `paused`/`blocked` resume, or cross-edition/cross-objective item binding.

4. **Dependency/scope compliance**
   - `backend/modules/tutoring/` imports only Python stdlib plus `modules.access.policy`, `modules.assessment.grader`, `modules.learning.ledger`, and `modules.retrieval.preflight`.

## Verification Commands Observed

All commands below were executed directly on branch `antigravity/dev-013-tutor-state-2026-11-26` at commit `849019f160fd36f1818204d8df0f639bbc4bffb1`:

| Command | Outcome | Observed Result |
|---|---|---|
| `make test-tutor-state-preflight` | PASS (exit 0) | `7 passed in 0.14s` |
| `make backend-check` | PASS (exit 0) | `770 passed, 1 deselected in 6.65s`; `backend/manage.py check`: `System check identified no issues (0 silenced).` |
| `make foundation-check` | PASS (exit 0) | `model_economics.py` PASS; `validate_project.py` PASS (0 errors, 0 warnings); `check_foundation.py` PASS; `tools/tests`: `Ran 179 tests in 3.878s`, `OK` |
| `git status --short` | PASS (exit 0) | Before creating this review: clean (`""`). After creating this review: only `?? development/evidence/dev-013-tutor-state-review.md` |

- **Not run in this review:** 37 `DEV-010` PostgreSQL integration cases (`AUTH-014` supplier wait), `make dependency-check`, `make smoke-local`, web/demo builds and Playwright checks (no web edits), and live DB/provider/AG-UI execution (outside `AUTH-020` scope).


## Re-review, correction round 1 — 26 November 2026

- **Commit SHA reviewed:** `07bae3c72fde55c2b606faf6d2ecfd3c1e886ff2` (`git diff 849019f..07bae3c` on branch `antigravity/dev-013-tutor-state-2026-11-26`)
- **Verdict:** **ACCEPTED WITH NOTES** (0 blockers, 0 should-fix items, 3 minor non-blocking notes).
- **Next action:** Commit `development/evidence/dev-013-tutor-state-review.md` and proceed with `AUTH-020` PR/handover under `U32` scope (full `DEV-013`, `R105` AG-UI/SSE, `DEV-010`, and `F4` phase exit remain gated).

### Resolution Verification

All 4 blockers and the actionable should-fix/note items from `849019f` are resolved in `07bae3c72fde55c2b606faf6d2ecfd3c1e886ff2` without regressions or scope drift:

1. **Blocker 1 (`paused` / `blocked` / `cancelled` resume & `check_access` source guard):** Resolved in `backend/modules/tutoring/state_machine.py:59-61,453-495` (`resume_session` transitions `paused`/`blocked`/`cancelled` -> `access_check` only after live `policy.allowed`, and `check_access` is restricted to `session.state == 'access_check'`). Verified in `backend/tests/tutoring/test_tutor_state.py:124-132,174-176,216-227,435-436`.
2. **Blocker 2 (Item schema, approval, edition, objective, and audience binding):** Resolved in `backend/modules/tutoring/state_machine.py:235-262,474,558,615` (`_validate_session_item` enforces `SERIALIZERS['item']`, `status == 'approved'`, matching `edition`, `objectives` membership, and `learner_private`/`shared_fixture` audience across `diagnose`, `start_practice`, and `submit_answer`). Verified in `backend/tests/tutoring/test_tutor_state.py:179-198`.
3. **Blocker 3 (Hint/reveal anti-gaming reset):** Resolved in `backend/modules/tutoring/state_machine.py:152,581,598,636-650,684` (persistent `exposed_items` set prevents a hinted or answer-revealed item restarted via `guided -> start_practice` from emitting `'independent'` evidence). Verified in `backend/tests/tutoring/test_tutor_state.py:336-357`.
4. **Blocker 4 (Server-derived role binding & human adjudication):** Resolved in `backend/modules/tutoring/state_machine.py:64-65,344-350,425-430,664,696-712` (`command.actor_role == scope.role` in `ALLOWED_ROLES`, `EvidenceEvent.actor_role=scope.role`, and both `resume_from_safety` and `adjudicate_review` require server-derived `scope.role in HUMAN_ADJUDICATOR_ROLES` plus live `policy.allowed`). Verified in `backend/tests/tutoring/test_tutor_state.py:144-147,282-294,435-446`.
5. **Should-fix & notes resolved:** Implemented `diagnose` item/submit flow (`473-487,611,644,650`; `test_tutor_state.py:366-374`), `adjudicate_review` (`696-712`; `test_tutor_state.py:440-446`), `cancel_turn` active-item cleanup (`411-415`), `no_active_item` guards on `request_hint`/`reveal_worked_answer` (`576-577,596-597`; `test_tutor_state.py:309-314`), live `policy.allowed` check on replay (`376`; `test_tutor_state.py:243-245`), full canonical `_command_digest` (`265-291`), `_SHORT_ID_MAX = 80` (`68,307,336-337`), and explicit `is None` defaults (`394,427,469,701,717`; `test_tutor_state.py:169-170`).

### Remaining Non-Blocking Notes

1. **Unused transition edges (`backend/modules/tutoring/state_machine.py:49,52-54`):** `ALLOWED_TRANSITIONS` still lists `'grade'` (`53-54`) and `'select'`/`'prerequisite' -> 'review_pending'` (`49,52`) with no actions entering `'grade'` or transitioning directly from `'select'`/`'prerequisite'` to `'review_pending'`.
2. **Active-item state across pause/block resume (`backend/modules/tutoring/state_machine.py:443-450,488-495,499-507`):** Unlike `cancel_turn` (`411-415`), `pause_session`, `blocked`, and `check_access(target='select')` keep `active_item_*` populated until `start_practice` or `check_access(target='diagnose')` runs; `exposed_items` still prevents independence bypass.
3. **Replay `TutorStepResult` metadata (`backend/modules/tutoring/state_machine.py:378,642-647`):** Idempotent replay returns `grade_decision=None`, `emitted_event=None`, and `abstention_reason=None` (callers inspect `session.emitted_events` and `session.last_citations`), and a previously revealed item retried with a new hint (`request_hint`) classifies as `'assisted'` rather than `'exposed'` (both are non-independent in `modules.learning.ledger`).

### Round 1 Verification Commands Observed

All commands below were executed directly on `antigravity/dev-013-tutor-state-2026-11-26` at commit `07bae3c72fde55c2b606faf6d2ecfd3c1e886ff2`:

| Command | Outcome | Observed Result |
|---|---|---|
| `make test-tutor-state-preflight` | PASS (exit 0) | `7 passed in 0.13s` |
| `make backend-check` | PASS (exit 0) | `770 passed, 1 deselected in 6.43s`; `backend/manage.py check`: `System check identified no issues (0 silenced).` |
| `make foundation-check` | PASS (exit 0) | `model_economics.py` PASS; `validate_project.py` PASS (0 errors, 0 warnings); `check_foundation.py` PASS; `tools/tests`: `Ran 179 tests in 4.157s`, `OK` |
| `git status --short` | PASS (exit 0) | Clean before review append; after append: only ` M development/evidence/dev-013-tutor-state-review.md` |

- **Not run in this re-review:** 37 `DEV-010` PostgreSQL integration cases (`AUTH-014` supplier wait), `make dependency-check`, `make smoke-local`, web/demo suites, and live DB/provider/AG-UI execution.
