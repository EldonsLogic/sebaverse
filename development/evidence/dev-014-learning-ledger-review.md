# Independent Security, Learning-Quality, and Architecture Review — AUTH-019 (DEV-014 Learning Ledger Preflight)

- **Date:** 26 November 2026
- **Branch:** `antigravity/dev-014-learning-ledger-2026-11-26`
- **Commit SHA reviewed:** `8bd154d25bcfe5b7240e2f5dccfa49955b3a59de`
- **Authorization scope:** U31 / [AUTH-019](../APPROVALS.md#L94-L96) (bounded DB-free, synthetic-fixture sub-slice of DEV-014; zero new dependencies, zero paid/provider calls, zero DB or UI execution)
- **Verdict:** `CHANGES REQUESTED`

## Scope and what was verified

Reviewed all AUTH-019 implementation, test, specification, Makefile, and authorization files on `8bd154d25bcfe5b7240e2f5dccfa49955b3a59de`:
- `backend/modules/assessment/__init__.py` (`L1-13`)
- `backend/modules/assessment/grader.py` (`L1-188`)
- `backend/modules/learning/__init__.py` (`L1-29`)
- `backend/modules/learning/ledger.py` (`L1-497`)
- `backend/tests/learning/test_learning_ledger.py` (`L1-382`)
- [offline-learning-ledger-instruction.md](../../sources/offline-learning-ledger-instruction.md) (`L1-7`), [APPROVALS.md](../APPROVALS.md#L94-L96) (`L94-96`), [03-learning-intelligence.md](../../docs/03-learning-intelligence.md) (`L1-55`), and `Makefile` (`L39-48`).

Deterministic grading (`choice.v1`, `exact-set.v1`, `numeric.v1`, `human-review.v1`), answer-key exclusion (`GradeDecision.answer_key_included=False`, fixed-code `AssessmentError`), safe finite `Decimal` parsing without `eval()`, holding `human-review.v1` / `uncertain` / `model_proposal` submissions for review, live `policy.allowed` gating on `LedgerScope`, cross-learner/cross-tenant/cross-edition/cross-objective event isolation, conflicting-duplicate rejection, out-of-order replay sorting, non-promotion of unassessed/assisted/exposed/ambiguous/external evidence, delayed-retention family separation, failure-induced `probe_needed` without erasing prior successes, and explicit uncalibrated baseline marking (`is_calibrated=False`) are structurally sound. Three concrete validation/lineage defects below should be fixed in round 1 of AUTH-019's two-cycle correction budget before PR review completes.

## Findings

### Blockers

None observed for answer-key leakage, cross-learner/cross-tenant scope leakage, raw expression execution, or direct model-written mastery within AUTH-019's DB-free scope.

### Should-fix

1. **Human corrections can reclassify `external_observation` (and `exposed`/`assisted`) attempts into `independent` mastery-raising evidence** — `backend/modules/learning/ledger.py:348-361`, `backend/tests/learning/test_learning_ledger.py:373-377`
   - [docs/03-learning-intelligence.md](../../docs/03-learning-intelligence.md#L55) (and [athar-derived-refinements.md](../../architecture/athar-derived-refinements.md#L15)) specifies that external marks and parent/teacher notes retain `external_observation` provenance and unknown assistance/exposure unless independently established, and that *"import or human confirmation alone never raises mastery."*
   - In `project_objective_mastery`, both `override_outcome` (`L350-353`) and `reclassify_evidence` (`L356-361`) only block setting `evidence_class='independent'` when `orig.hints_used > 0 or orig.answer_revealed` (plus `target['outcome'] == 'pending_review'` for `reclassify_evidence`). Neither checks `orig.evidence_class`.
   - Because an `external_observation` event defaults to `hints_used=0` and `answer_revealed=False` and can carry `outcome='correct'`, a `teacher` or `reviewer` `reclassify_evidence` (or `override_outcome`) correction converts it to `'independent'`, promoting mastery from an external mark. Similarly, an `exposed` attempt with `answer_revealed=False` (such as a repeated item) or an `assisted` attempt created with `hints_used=0` (allowed by `validate_event` at `L205`) can be reclassified to `'independent'`.
   - **Fix:** Restrict `new_evidence_class == 'independent'` in both `override_outcome` and `reclassify_evidence` so it is permitted only when `orig.evidence_class in ('independent', 'ambiguous')` (in addition to `hints_used == 0`, `not answer_revealed`, and resulting `outcome != 'pending_review'`), raising `LedgerError('invalid_correction')` otherwise. Add negative tests in `backend/tests/learning/test_learning_ledger.py` covering `external_observation`, `exposed`, and zero-hint `assisted` attempts.

2. **`override_outcome` permits pairing `new_outcome='pending_review'` with `new_evidence_class='independent'`** — `backend/modules/learning/ledger.py:222-228`, `backend/modules/learning/ledger.py:348-355`
   - `validate_event` enforces for attempts that `outcome == 'pending_review'` requires `evidence_class == 'ambiguous'` (`L208-209`).
   - However, `validate_event` for `override_outcome` (`L222-228`) allows `new_outcome='pending_review'` alongside `new_evidence_class='independent'`, and `project_objective_mastery` (`L350-355`) only sets `target['evidence_class'] = 'ambiguous'` in the `elif` branch when `corr.new_evidence_class is None`.
   - While replay (`L409-412`) prevents a single `pending_review` state from raising mastery, the mutated attempt retains `evidence_class='independent'` while `outcome='pending_review'`; a subsequent `override_outcome(new_outcome='correct', new_evidence_class=None)` then inherits `'independent'` without an explicit evidence-class decision.
   - **Fix:** In `validate_event` (`L222-228`), reject `override_outcome` when `event.new_outcome == 'pending_review'` and `event.new_evidence_class not in (None, 'ambiguous')` with `LedgerError('invalid_correction')`, and reject `corr.new_outcome == 'pending_review'` whenever `corr.new_evidence_class == 'independent'` during replay (`L351`). Add a regression test.

3. **`_FORBIDDEN_MODEL_PREFIXES` fails to block `'ai.*'` / `'ai-*'` and underscore-separated model identifiers on `adjudicator_ref`** — `backend/modules/learning/ledger.py:29`, `backend/modules/learning/ledger.py:216-218`
   - `_FORBIDDEN_MODEL_PREFIXES = ('model', 'llm', 'ai.')` includes a trailing dot on `'ai.'`, while `L217` tests `adj == p or adj.startswith(p + '.') or adj.startswith(p + '-')`. That builds `'ai..'`, `'ai.-'`, so `'ai.gpt'`, `'ai-assistant'`, and `'ai'` pass validation.
   - Because `_IDENTIFIER` (`L28`) also allows `'_'`, `'model_1'` and `'llm_grader'` bypass `startswith(p + '.') or startswith(p + '-')`.
   - **Fix:** Normalize `_FORBIDDEN_MODEL_PREFIXES = ('model', 'llm', 'ai')` and check `.` / `-` / `_` separators (e.g., `adj == p or adj.startswith((p + '.', p + '-', p + '_'))`), with negative tests for `'ai.gpt'` and `'model_1'`.

### Notes

1. **Unitless `numeric.v1` ignores unexpected `submitted_unit` and `model_proposal` bypasses choice/numeric rubric checks** — `backend/modules/assessment/grader.py:138-140,180-183`:
   - When `rubric['config']['unit']` is `None`, passing a non-empty `submitted_unit` (e.g., `'kg'`) is ignored rather than treated as `numeric_unit_mismatch`.
   - Returning `pending_review` at `L138` before running `choice.v1` (`L146-151`) or `numeric.v1` (`L173-176`) consistency checks is fail-closed for grading, though a malformed choice rubric paired with `model_proposal` yields `pending_review` rather than `invalid_item`/`invalid_rubric`.
   - `_NUMERIC_LITERAL` (`L20`) uses `\d` without `re.ASCII`, so non-ASCII decimal digits outside `_NUMERIC_TRANS` also parse via `Decimal`; still bounded and safe (no `eval()`).

2. **Ledger edge cases and replay behaviors (non-blocking baseline choices)** — `backend/modules/learning/ledger.py:188-233,385-471`:
   - `validate_event` does not reject unused attempt fields on `correction` events (or `new_outcome`/`new_evidence_class` on `invalidate_item`), and does not require `recorded_at >= occurred_at` or `corr.occurred_at >= orig.occurred_at` (all fields remain covered by `_canonical_event_digest`, and replay sorts deterministically).
   - `external_observation` (`L404-406`) and invalidated attempts (`L385-387`) do not add `item_key` to `exposed_items`; if an internal `item_id` were ever logged on an `external_observation` or a non-defective attempt was invalidated after learner exposure, a later attempt on the same `(item_id, item_version)` would not be marked exposed.
   - On a single independent failure (`status='needs_support'`, `L447-448`), `uncertainty` reports `'low'` rather than `'probe_needed'` (`L460-463`), though `review_due_at` is set immediately to `last_independent_at` (`L467-468`). `recent_failures` (`L439`) accumulates across the full event log without decay, and an unresolved `ambiguous` attempt sets `uncertainty='pending_review'` without altering `status` or `review_due_at`.

3. **Additional non-blocking test coverage gaps** — `backend/tests/learning/test_learning_ledger.py:219-382`:
   - Scope isolation is tested for `tenant_id` and `learner_id`, but not yet for mismatched `edition_id`, `edition_version`, `objective_id`, `objective_version`, invalid `(role, purpose)` pairs (e.g., `learner` with `teacher_reporting`), or permitted `teacher`/`guardian` reporting scopes.
   - Replay tests do not yet assert: (a) `conflicting_duplicate` when two distinct `event_id`s reuse the same `idempotency_key`; (b) that a delayed success after `>= retention_delay` on an *already-seen* family does NOT promote `ready_for_review` to `retained`, nor does a new family before `retention_delay`; and (c) `draft`/`withdrawn` rubric or mismatched item/rubric `audience` rejection in `grade_submission`.

4. **Scope discipline:** Confirmed zero new dependencies (`requirements.txt` / lockfiles unchanged), zero DB models/migrations, zero LLM/provider or UI execution, no relaxation of existing gates (`test-learning-ledger-preflight` added separately from gated `test-learning-ledger`), and explicit `is_calibrated=False` uncalibrated baseline notice in `backend/modules/learning/ledger.py:6,134`.

## Exact command results observed

1. `make test-learning-ledger-preflight`: **PASS** (exit `0`) — `pytest backend/tests/learning/test_learning_ledger.py -q` passed `17 passed in 0.11s`.
2. `make backend-check`: **PASS** (exit `0`) — `pytest backend/tests -q -k 'not postgres_integration'` passed `762 passed, 1 deselected in 5.16s`; `backend/manage.py check` reported `System check identified no issues (0 silenced)`.
3. `make foundation-check`: **PASS** (exit `0`) — `tools/model_economics.py`, `tools/validate_project.py` (PASS, 0 errors, 0 warnings), `tools/check_foundation.py` (PASS), and `python3 -m unittest discover -s tools/tests -p 'test_*.py'` (`179` tests, OK), re-run after writing this review file.
4. `git status --short`: **PASS** — only `?? development/evidence/dev-014-learning-ledger-review.md` untracked; no source, test, Makefile, or handoff files modified.
- **Not run:** 37 DEV-010 PostgreSQL integration cases (`postgres_integration`, held on AUTH-014), web/demo test suites (no web/demo changes), and live DB/provider/UI execution (outside AUTH-019 scope).
