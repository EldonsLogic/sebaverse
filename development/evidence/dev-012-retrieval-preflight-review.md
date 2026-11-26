# Independent Security and Quality Review — AUTH-018 (DEV-012 Retrieval & Citation Preflight)

- **Date:** 26 November 2026
- **Branch:** `antigravity/dev-012-retrieval-preflight-2026-11-26`
- **Commit SHA reviewed:** `98015c451086a07ba6e63f1186adae9ff160b725`
- **Authorization scope:** U30 / [AUTH-018](../APPROVALS.md#L90-L92) (bounded DB-free, synthetic-fixture DEV-012 sub-slice; zero new dependencies, zero DB/pgvector/provider calls)
- **Verdict:** `CHANGES REQUESTED`

## Scope and what was verified

Reviewed all changed retrieval code, unit tests, synthetic evaluation harness, Makefile target, and authorization records:
- `backend/modules/retrieval/__init__.py` (`L1-29`)
- `backend/modules/retrieval/preflight.py` (`L1-506`)
- `backend/tests/retrieval/test_retrieval_preflight.py` (`L1-321`)
- `evals/retrieval/run_preflight_eval.py` (`L1-188`)
- `Makefile` (`L39-45`), `development/APPROVALS.md` (`L90-92`), `sources/offline-retrieval-preflight-instruction.md` (`L1-7`), and `docs/04-curriculum-and-rag.md` (`L26-40`).

Core pre-ranking ACL/edition/material isolation, rubric/item exclusion (`_authorized_chunks` only indexes `collection['materials']`), `untrusted_data=True` marking, fixed reason-code errors without leaked inputs (`RetrievalError`), live citation re-verification (`resolve_citation`), private cache partitioning (`build_cache_key`), and query/top-k/context bounds are structurally sound. Three concrete defects below should be fixed before PR review completes (round 1 of AUTH-018's two-cycle correction budget).

## Findings

### Blockers

None observed for cross-learner data exposure, rubric leakage, or forged-citation acceptance within AUTH-018's synthetic-fixture scope.

### Should-fix

1. **Arabic punctuation is glued onto tokens, causing false abstentions on Arabic text and questions** — `backend/modules/retrieval/preflight.py:30`, `backend/modules/retrieval/preflight.py:159-167`
   - `_TOKEN_RE = re.compile(r'[\u0600-\u06ff]+|[a-z0-9]+')` spans the full Arabic Unicode block, which includes Arabic punctuation (`،` `U+060C`, `؛` `U+061B`, `؟` `U+061F`, `٪` `U+066A`).
   - Observed directly against `evals/fixtures/curriculum-v1.json`: `material.language.private` contains `"تتعلمه،"` (`L1267`), so querying `'تتعلمه'` via `retrieve_scoped` returns `abstain` while `'تتعلمه،'` returns `grounded`; querying `'الثلج؟'` against `edition.science` likewise returns `abstain`. `material.quantitative` (`L493`) only matched `'الطرفين'` in the eval because the word appears a second time without `،`.
   - Fix: restrict the Arabic token class to Arabic letters (excluding punctuation/diacritics, or strip punctuation in `normalize_search_text` / `_tokenize`), and add regression tests in `backend/tests/retrieval/test_retrieval_preflight.py` for Arabic words adjacent to `،`, `؛`, and `؟`.

2. **Pinned edition does not verify `profile['status'] == 'approved'`** — `backend/modules/retrieval/preflight.py:259-271`
   - `_authorized_chunks` enforces `status == 'approved'` on `edition` (`L260`), `collection` (`L267`), `material` (`L276`), and `rights` (`L281`), but never resolves `edition['profile']` to check `profile['status'] == 'approved'` (and `_audience_allows`). `validate_bundle` only checks that the profile exists and is not `withdrawn` (`backend/modules/curriculum/contracts.py:309`), whereas `publication_preflight.py:90-93` requires an approved profile.
   - Fix: resolve `('profile', *source_key(edition['profile']))`, require `status == 'approved'` (and compatible audience), and add a negative test for a `'draft'` profile.

3. **Bundle-wide `validate_bundle` call couples unrelated learners/editions and makes per-material live-rights checks unreachable** — `backend/modules/retrieval/preflight.py:249-258`, `backend/modules/retrieval/preflight.py:280-292`, `backend/tests/retrieval/test_retrieval_preflight.py:141-150`
   - Calling `validate_bundle(bundle, now=now)` (`L255`) rejects the entire bundle if any record anywhere in `bundle` has `status='withdrawn'`, `expires_at <= now`, or `permissions.display=False` (`contracts.py:276-277, 299-302`).
   - In a shared in-memory bundle carrying both shared and private fixtures, withdrawing or expiring learner A's `material.language.private` / `rights.language.private` causes learner B's unrelated `edition.language` query to raise `RetrievalError('invalid_bundle')` (a cross-record availability coupling / state-existence signal). It also makes the per-material checks at `L283-292` unreachable in `retrieve_scoped`, and surfaces expired/non-displayable rights on the target edition as `'invalid_bundle'` (`test_retrieval_preflight.py:144, 149`) rather than `'access_denied'` or skipping that material.
   - Fix: separate structural schema validation from per-scope live status/rights/expiry enforcement (or validate/filter the reachable edition subgraph without letting unrelated records fail valid scopes), and add a negative test verifying that withdrawing/expiring `material.language.private` does not break `edition.language`.

### Notes

1. **Non-string `role`/`purpose` or extreme timezone edge cases can leak `TypeError`/`OverflowError`** — `backend/modules/retrieval/preflight.py:170-185`: `_validate_scope` does not check `type(scope.role) is str and type(scope.purpose) is str` before `policy.allowed(...)`, so an unhashable value (such as a `list`) raises `TypeError` instead of `RetrievalError('invalid_scope')`. `now.astimezone(timezone.utc)` at `L173` can also raise `OverflowError` at `datetime.min`/`datetime.max` boundaries.
2. **German umlauts and `ß` are split/dropped by `_TOKEN_RE`** — `backend/modules/retrieval/preflight.py:30`: `[a-z0-9]+` drops non-ASCII Latin characters (`ä`, `ö`, `ü`, `ß`). Current `curriculum-v1.json` German text uses ASCII-only letters, so AUTH-018 tests pass, but full DEV-012 will need Unicode Latin letter/diacritic handling for `language: "de"`.
3. **Public export signature mismatch and overridable `untrusted_data` default** — `backend/modules/retrieval/__init__.py:11,25`, `backend/modules/retrieval/preflight.py:116,138,298`: `build_cache_key` is exported in `__all__` while typing `authorized_chunks: list[_Chunk]` against a private class; `RetrievalHit.untrusted_data` and `ResolvedCitation.untrusted_data` use `= True` instead of `field(default=True, init=False)`.
4. **Multi-anchor fallback and context-budget skipping** — `backend/modules/retrieval/preflight.py:209-216`, `L435-452`: when `len(anchors) > 1` and `\n\n` splitting does not equal `len(anchors)`, `_chunk_material` collapses to `[content]` on `anchors[0]`; when all positive-scoring chunks exceed `max_context_chars`, `retrieve_scoped` returns `abstention_reason='no_authorized_evidence'` (safe fail-closed, though budget-caused).
5. **Synthetic eval reporting granularity and missing negative test slices** — `evals/retrieval/run_preflight_eval.py:78,94,169-182`, `backend/tests/retrieval/test_retrieval_preflight.py:218-261`: `run_preflight_eval.py` groups `edition.language` v1 and v2 under `'language:ar-de'` and labels `edition.language.private` as `'language.private:ar'` even though its `curriculum_key.language` is `'de'` (`curriculum-v1.json:1326`). `test_retrieval_preflight.py` does not yet test `resolve_citation` against a mismatched `edition_version`/`edition_id` or `rights.permissions.display=False`, nor `teacher`/`guardian` reporting purposes permitted by `policy.py`.
6. **Scope discipline:** Confirmed zero new dependencies, zero DB/pgvector/provider calls, no gate/threshold relaxation, and explicit synthetic-only framing in `evals/retrieval/run_preflight_eval.py:1-5,169,181`.

## Exact command results observed

- `make test-retrieval-preflight`: **PASS** (exit `0`) — `pytest backend/tests/retrieval/test_retrieval_preflight.py -q` passed `27 passed in 0.44s`; `evals/retrieval/run_preflight_eval.py` exited `0` with `recall_at_5: 1.0`, `abstention_accuracy: 1.0`, `fabricated_citations: 0`, `unauthorized_access: 0` (`language:ar-de` 2/2, 1/1; `quantitative:ar` 1/1, 1/1; `science:ar` 1/1, 1/1; `language.private:ar` 1/1, 0/0).
- `make backend-check`: **PASS** (exit `0`) — `744 passed, 1 deselected in 5.50s` (`-k 'not postgres_integration'`); `backend/manage.py check` reported `0` issues.
- `make foundation-check`: **PASS** (exit `0`) — `tools/model_economics.py`, `tools/validate_project.py` (PASS, 0 errors, 0 warnings), `tools/check_foundation.py` (PASS), and `python3 -m unittest discover -s tools/tests -p 'test_*.py'` (`179` tests, OK), re-run after writing this review file.
- `git status --short`: **PASS** — only `development/evidence/dev-012-retrieval-preflight-review.md` is untracked (`??`); no source, test, Makefile, or handoff files modified.
- **Not run:** `postgres_integration` / 37 DEV-010 PostgreSQL cases (held under AUTH-014), web/demo test suites (unrelated to backend retrieval preflight), and live pgvector/LLM retrieval (excluded from AUTH-018).

## Re-review, correction round 1 — 26 November 2026

- **Commit SHA reviewed:** `35f119892977da76409f4d3fdbea9807b35bf88f` (diff `98015c4..35f1198`)
- **Verdict:** `ACCEPTED WITH NOTES`

### Resolution check against round 1 findings

- **Should-fix 1 (Arabic punctuation tokenization) — RESOLVED:** `backend/modules/retrieval/preflight.py:32` restricts Arabic tokens in `_TOKEN_RE` to Arabic letters (`[\u0621-\u063a\u0641-\u064a\u0671-\u06d3\u06fa-\u06ff]+|[a-zäöüß0-9]+`), excluding `،`, `؛`, and `؟`, and adds German `ä/ö/ü/ß`. Covered by `backend/tests/retrieval/test_retrieval_preflight.py:325-341` (`'تتعلمه'`, `'الثلج؟'`, `'übung straße groß'`) and `evals/retrieval/run_preflight_eval.py:77-78`.
- **Should-fix 2 (`profile` approval enforcement) — RESOLVED:** `backend/modules/retrieval/preflight.py:307-319` validates `edition['profile']` via `SERIALIZERS['profile']`, requiring `status == 'approved'`, `_audience_allows`, and matching `edition['audience']` when non-shared. Covered by negative test at `backend/tests/retrieval/test_retrieval_preflight.py:137-140`.
- **Should-fix 3 (bundle-wide `validate_bundle` coupling & unreachable live-rights checks) — RESOLVED:** `backend/modules/retrieval/preflight.py:207-240,284-388` replaces whole-bundle `validate_bundle` with `_index_bundle_records` (envelope + unique `(kind, id, version)` indexing) and per-record validation/live rights/expiry/hash checks scoped to the target edition, profile, collection, and each material (`continue` on ineligible materials, deduplicated `seen_materials`). Verified by `backend/tests/retrieval/test_retrieval_preflight.py:150-168,256-275` (withdrawn/expired private material no longer breaks `edition.science`).
- **Round 1 minor notes resolved:**
  - `preflight.py:172-190`: `_validate_now` catches `OverflowError`/`TypeError`/`ValueError`, and `_validate_scope` checks `type(role) is str` and `type(purpose) is str` (`test_retrieval_preflight.py:126-129`).
  - `__init__.py:1-27` & `preflight.py:118,130,140,391`: `_build_cache_key` is internal; `untrusted_data` and `policy_version` use `field(default=..., init=False)`.
  - `preflight.py:540-545`: distinguishes `'context_budget_exceeded'` from `'no_authorized_evidence'` (`test_retrieval_preflight.py:342-345`).
  - `evals/retrieval/run_preflight_eval.py:73-85` & `test_retrieval_preflight.py:267-275`: splits eval reporting by edition/version and language tag (`de` vs `ar`), and adds `resolve_citation` negative tests for `permissions.display=False` and wrong `edition_id`/`edition_version`.

### Remaining non-blocking notes (`file:line`)

1. `backend/modules/retrieval/preflight.py:252-260`: multi-anchor chunking still collapses to `[content]` on `anchors[0]` whenever `len(anchors) > 1` and `\n\n` paragraph count differs from `len(anchors)` (carryover for full DEV-012 chunking).
2. `backend/tests/retrieval/test_retrieval_preflight.py:100-109` & `evals/retrieval/run_preflight_eval.py:81-85`: `teacher` (`teacher_reporting`) and `guardian` (`guardian_reporting`/`tutoring`) scopes allowed by `policy.py` are not exercised in retrieval tests, and `language:v2:de` / `language.private:v1:de` have `0` unanswerable cases in the 8-case synthetic eval.
3. Scope boundary unchanged: AUTH-018 remains a bounded DB-free synthetic-fixture preflight only; full DEV-012 (pgvector/hybrid indexing, 100-question PoC corpus, DEV-010/DEV-011 prerequisites, and F3 exit) stays gated.

### Exact command results observed on `35f1198`

- `make test-retrieval-preflight`: **PASS** (exit `0`) — `pytest backend/tests/retrieval/test_retrieval_preflight.py -q` passed `28 passed in 0.18s`; `evals/retrieval/run_preflight_eval.py` exited `0` (`recall_at_5: 1.0`, `abstention_accuracy: 1.0`, `fabricated_citations: 0`, `unauthorized_access: 0` across `language:v1:de`, `language:v2:de`, `quantitative:v1:ar`, `science:v1:ar`, `language.private:v1:de`).
- `make backend-check`: **PASS** (exit `0`) — `745 passed, 1 deselected in 5.95s` (`-k 'not postgres_integration'`); `backend/manage.py check` reported `0` issues.
- `make foundation-check`: **PASS** (exit `0`) — `tools/model_economics.py`, `tools/validate_project.py` (PASS, 0 errors, 0 warnings), `tools/check_foundation.py` (PASS), and `python3 -m unittest discover -s tools/tests -p 'test_*.py'` (`179` tests, OK), re-run after appending this re-review section.
- `git status --short`: **PASS** — only `M development/evidence/dev-012-retrieval-preflight-review.md` modified; no source, test, Makefile, or handoff files touched.
- **Not run:** `postgres_integration` / 37 DEV-010 PostgreSQL cases (held under AUTH-014), web/demo suites, and live pgvector/LLM retrieval.
