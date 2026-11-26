# AUTH-021 / DEV-015 & DEV-016 Bounded Parent Summary and Privacy Preflight — Independent Review

- **Date:** 26 November 2026
- **Branch:** `antigravity/dev-015-016-parent-privacy-2026-11-26`
- **Commit SHA reviewed:** `7b84372ddce9f212602792c94d29ffd3eaf9daaf`
- **Scope authority:** [U33](../../sources/offline-parent-privacy-instruction.md) / `AUTH-021` in [APPROVALS.md](../APPROVALS.md#L102-L104) (bounded DB-free, synthetic-fixture backend sub-slice of `DEV-015` and `DEV-016`).
- **Verdict:** **CHANGES REQUESTED** (2 blockers, 4 should-fix items, 2 notes).
- **Next action:** Fix both blockers and the actionable should-fix items in [`backend/modules/operations/privacy.py`](../../backend/modules/operations/privacy.py), [`backend/modules/learning/parent_summary.py`](../../backend/modules/learning/parent_summary.py), and [`backend/tests/operations/test_parent_privacy_preflight.py`](../../backend/tests/operations/test_parent_privacy_preflight.py), re-run the test suite, and request correction round 1 of 2 re-review.

## Scope & Integrity Summary

Commit `7b84372ddce9f212602792c94d29ffd3eaf9daaf` stays strictly inside the `AUTH-021` boundary: zero new dependencies, zero database, UI, HTTP, or provider calls, and no edits to phase gates or thresholds ([`Makefile`](../../Makefile#L39-L54) adds only `test-parent-privacy-preflight`).

In [`parent_summary.py`](../../backend/modules/learning/parent_summary.py), live `guardian` + `guardian_reporting` + `policy.allowed` gating, distinct evidence counts (independent, assisted, exposed, ambiguous, external), `unassessed` preservation, `is_calibrated=False`, `raw_chat_included=False`, `fabricated_percentage_included=False`, and absence of raw chat, answer keys, personal labels, and fabricated attainment percentages are sound. In [`privacy.py`](../../backend/modules/operations/privacy.py), strict allowlist key filtering, exact `type(val) is int` boolean rejection, `training_corpus_eligible=False`, tenant/learner isolation, post-delete preservation (`created_at > deleted_at`), conflicting-duplicate rejection, and model-authority rejection work as intended for the tested inputs, but two material defects in [`privacy.py`](../../backend/modules/operations/privacy.py) block acceptance.

## Findings

### Blockers

1. **Cross-kind `target_id` collision lets an `upload` tombstone purge `session`/`evidence` records and vice versa ([`backend/modules/operations/privacy.py`](../../backend/modules/operations/privacy.py#L35-L36), [lines 77–85](../../backend/modules/operations/privacy.py#L77-L85), [lines 233–239](../../backend/modules/operations/privacy.py#L233-L239); [`backend/tests/operations/test_parent_privacy_preflight.py`](../../backend/tests/operations/test_parent_privacy_preflight.py#L184-L224))**
   - `replay_deletion_tombstones` matches non-`learner_all` tombstones solely with `rec.target_id == tomb.target_id` ([`privacy.py:236`](../../backend/modules/operations/privacy.py#L236)) without checking `tomb.target_kind` (`'upload'` vs `'session'`) against `rec.record_kind`, and `RestorableRecord` ([`privacy.py:77-85`](../../backend/modules/operations/privacy.py#L77-L85)) carries no `target_kind` field to disambiguate derived `'cache'`/`'job'` records.
   - Verified directly against commit `7b84372`: a `DeletionTombstone` with `target_kind='upload'` and `target_id='shared.id'` purges `RestorableRecord(..., record_kind='session', target_id='shared.id')` and `record_kind='evidence'`; conversely, a `session` tombstone purges `upload` and `chunk` records sharing that `target_id`. Meanwhile, `test_parent_privacy_preflight.py` has no test for `target_kind='session'` or cross-kind `target_id` separation.
   - Fix: Enforce kind compatibility between `DeletionTombstone.target_kind` and `RestorableRecord` (for example by adding and validating a `target_kind` / owner-kind field on `RestorableRecord` for targeted records, mapping each `record_kind` to permitted `target_kind`s, and requiring `target_id` on `upload`, `session`, and `chunk` records), and add negative/isolation tests covering `upload` vs `session` tombstones with matching `target_id` values (`R061`).

2. **`_PHONE_LIKE` regex unconditionally drops ISO-8601 `occurred_at` timestamps and date-stamped labels ([`backend/modules/operations/privacy.py`](../../backend/modules/operations/privacy.py#L17-L26), [line 40](../../backend/modules/operations/privacy.py#L40), [lines 126–133](../../backend/modules/operations/privacy.py#L126-L133); [`backend/tests/operations/test_parent_privacy_preflight.py`](../../backend/tests/operations/test_parent_privacy_preflight.py#L145-L179))**
   - `occurred_at` is explicitly allowlisted in `ALLOWED_TELEMETRY_STR_FIELDS` ([`privacy.py:25`](../../backend/modules/operations/privacy.py#L25)), yet `_PHONE_LIKE = re.compile(r'(?:\+?\d[\d\s\-()]{7,}\d)')` ([`privacy.py:40`](../../backend/modules/operations/privacy.py#L40)) matches any `YYYY-MM-DD` date substring (for example `'2026-11-26'`).
   - Verified directly against commit `7b84372`: `sanitize_telemetry_record({'event_type': 'tutor.turn', 'occurred_at': '2026-11-26T16:00:00+00:00'})` silently drops `occurred_at` (`dropped_field_count=1`), and any date-suffixed identifier (such as `'policy-2026-11-26'`) in `policy_version` or `edition_id` is likewise dropped. `test_parent_privacy_preflight.py` never exercises `occurred_at`, `policy_version`, or `subject_tag`.
   - Fix: Parse and normalize `occurred_at` separately as an aware ISO-8601 UTC timestamp instead of running `_PHONE_LIKE` against it, and enforce explicit metadata syntax on the remaining allowlisted string fields (`R079`).

### Should-fix

1. **Allowlisted telemetry string fields accept arbitrary non-email, non-phone free text ([`backend/modules/operations/privacy.py`](../../backend/modules/operations/privacy.py#L17-L26), [lines 126–133](../../backend/modules/operations/privacy.py#L126-L133))**
   - Beyond `len <= 128`, `_EMAIL_LIKE`, and `_PHONE_LIKE`, `sanitize_telemetry_record` accepts arbitrary free text (including spaces, newlines, URLs, or child utterances such as `'أنا اسمي عمر'`) in `event_type`, `service`, `policy_version`, `outcome`, `reason_code`, `edition_id`, and `subject_tag`. Restrict these metadata fields to controlled identifier/label characters (no whitespace or control characters) so free-text PII cannot slip through (`R059`, `R079`).

2. **`'policy_version'` in `ALLOWED_TELEMETRY_STR_FIELDS` collides with `SanitizedTelemetry.as_dict()` ([`backend/modules/operations/privacy.py`](../../backend/modules/operations/privacy.py#L20), [lines 53–60](../../backend/modules/operations/privacy.py#L53-L60))**
   - Verified at runtime: passing `'policy_version': 'custom.policy-v1'` retains `('policy_version', 'custom.policy-v1')` inside `SanitizedTelemetry.fields`, while `as_dict()` ([`privacy.py:58`](../../backend/modules/operations/privacy.py#L58)) unconditionally overwrites `out['policy_version']` with `PRIVACY_POLICY_VERSION` (`'operations.privacy-preflight-v1'`). Separate the redactor's own policy field name (e.g. `redaction_policy_version`) or remove `'policy_version'` from `ALLOWED_TELEMETRY_STR_FIELDS`.

3. **Error-code masking and non-sequence `events` / unhashable `objectives` handling in `build_parent_progress_summary` ([`backend/modules/learning/parent_summary.py`](../../backend/modules/learning/parent_summary.py#L75-L117))**
   - Invalid `scope` identifiers (such as `scope.tenant_id=''` or `scope.edition_version=0`) pass lines `83–88`, trigger `LedgerError('invalid_scope')` inside `project_objective_mastery`, and are remapped at lines `114–115` to `ParentSummaryError('invalid_objectives')` (verified at runtime).
   - Passing a generator/iterator for `events` exhausts it on the first objective and silently leaves subsequent objectives `'unassessed'`, while non-iterables or unhashable `obj_id` entries (`99`) raise raw `TypeError` instead of `ParentSummaryError`. Validate `isinstance(events, (list, tuple))` and `type(obj_id) is str` / `type(obj_ver) is int` upfront.

4. **Missing negative and state coverage in [`backend/tests/operations/test_parent_privacy_preflight.py`](../../backend/tests/operations/test_parent_privacy_preflight.py)**
   - Add tests for: `target_kind='session'` tombstones and cross-kind `target_id` isolation; `sanitize_telemetry_record` with `occurred_at`, `policy_version`, `bool` (`True`/`False`) in integer fields, negative integers, floats/bytes/None in allowlisted fields, and free-text rejection; and `parent_summary` coverage of `pending_review` (`ambiguous_count`), `probe_needed`, `needs_support`, `ready_for_review`, `retained`, `exposed_count`, `external_observation_count`, and the remaining `LedgerScope` denial flags (`member_active`, `learner_active`, `enrollment_valid`, `entitlement_valid`, `course_active`, `edition_active`).

### Notes

1. **`_is_non_model_authority` token check ([`backend/modules/operations/privacy.py`](../../backend/modules/operations/privacy.py#L38), [lines 111–114](../../backend/modules/operations/privacy.py#L111-L114)):** Checking only `re.split(r'[._-]', ref, maxsplit=1)[0]` matches `ledger.py:220` and rejects `model.*`, `llm.*`, and `ai.*`, though requiring an explicit non-model authority prefix allowlist (such as `guardian.`, `teacher.`, `reviewer.`, `admin.`, `counsel.`, `system.`) or rejecting any forbidden token segment would also block references like `auto.model`.
2. **Scope and dependency compliance (`AUTH-021`):** `parent_summary.py` and `privacy.py` use only the Python standard library plus `modules.access.policy` and `modules.learning.ledger`, with zero new dependencies, zero DB/UI/HTTP/provider execution, and untouched phase gates/thresholds.

## Verification Commands Observed

All commands below were executed directly on branch `antigravity/dev-015-016-parent-privacy-2026-11-26` at commit `7b84372ddce9f212602792c94d29ffd3eaf9daaf`:

| Command | Outcome | Observed Result |
|---|---|---|
| `make test-parent-privacy-preflight` | PASS (exit 0) | `12 passed in 0.02s` |
| `make backend-check` | PASS (exit 0) | `782 passed, 1 deselected in 5.28s`; `backend/manage.py check`: `System check identified no issues (0 silenced).` |
| `make foundation-check` | PASS (exit 0) | `model_economics.py` PASS; `validate_project.py` PASS (`0` errors, `0` warnings); `check_foundation.py` PASS; `tools/tests`: `Ran 179 tests in 3.369s`, `OK` |
| `git status --short` | PASS (exit 0) | Confirmed only `?? development/evidence/dev-015-016-parent-privacy-review.md` added; source, tests, `Makefile`, and handoff files untouched |

- **Not run in this review:** 37 `DEV-010` PostgreSQL integration cases (`AUTH-014` supplier wait), `make dependency-check`, `make smoke-local`, web/demo suites (no web edits), and live DB/HTTP/provider execution (outside `AUTH-021` scope).
