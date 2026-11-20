# Public repository CI recheck

20 November 2026 · DEV-010 / F3 · R040, R046, R081. The GitHub-hosted skeleton job started after the founder made the repository public under [U24](../../sources/public-repository-instruction.md). The database-free checks passed on Linux. The native and image pre-use policy rejected the scan results and stopped the PostgreSQL and browser checks. This recheck was limited to one disposable synthetic CI attempt and read-only inspection of its result. [Prior jobs that did not start](auth-014-independent-assessment.md#hosted-checks-at-8cec5b3).

## Observed run

The `Local skeleton phase checks` push workflow for `main` checked out `0a9a3ff44663a2c733ee315d8aa2419ae9171ac9`. Attempt 2 of run `44733660486` completed with failure. The `skeleton` job (`136281294860`) took 2m14s on the Ubuntu 24.04 runner. `gh run view 44733660486 --repo EldonsLogic/sebaverse --attempt 2`, `--log` and `--log-failed` supplied the results below. [Run attempt](https://github.com/EldonsLogic/sebaverse/actions/runs/44733660486/attempts/2) · [Job log](https://github.com/EldonsLogic/sebaverse/actions/runs/44733660486/job/136281294860).

| Step | Result |
| --- | --- |
| Set up job, check out the commit, set up Python, Node and uv, and install the locked packages | Passed |
| Compile web and test DB-free API/config boundaries | Passed. Web typecheck and build passed, with 140 modules transformed. `pytest backend/tests -q -k 'not postgres_integration'` reported 462 passed, 1 deselected in 2.95s. Curriculum schema matched its runtime serializers. |
| Download the pinned scanners and enable OCI storage on the disposable runner | Passed |
| Build and inspect the existing derived OCI, apply the reviewed CI native patch, inspect the system libpq chain and symbol imports, catalog both targets and capture advisory scans | Passed through static assessment. The database image stayed unstarted. |
| Enforce native/image pre-use policy | Failed, exit 1. See exact report output below. |
| Run real PostgreSQL migration/readiness/teardown, install browser runtime, run desktop/mobile browser smoke, and run the skeleton job's foundation/dependency/phase regressions | Skipped. The hosted database scenarios, including the retained-partial case, have no new result. |
| Preserve actual phase evidence even on failure and complete the job | Artifact uploaded and job finalized. |

The 462-case selection included the authored POSIX worker guard tests in `backend/tests/ingestion/test_process_guard.py` at the checked-out commit. The hosted log reported no skips and one deselection under the PostgreSQL filter. It reported the aggregate pass count only. This exercises the guard fixtures on Linux. Worker integration, native PDF extraction, operating system isolation and Arabic or bilingual extraction still require their own evidence. [Guard test at tested commit](https://github.com/EldonsLogic/sebaverse/blob/0a9a3ff44663a2c733ee315d8aa2419ae9171ac9/backend/tests/ingestion/test_process_guard.py).

## Pre-use policy rejection

At 12:17:09 UTC, `python3 tools/security/check_reports.py --scope synthetic-ci` reported three errors.

```text
image-cves.json: unresolved high/critical/unknown advisories=8
image-cves.json: fix released for reviewed findings; update the pinned artifact and re-review=10
system-native-cves.json: findings require explicit review=15
```

These are the policy's reported category counts. Advisory capture passed and the enforcement step blocked runtime use. The job uploaded `f2-evidence` (1,801,980 bytes). The uploaded ZIP SHA-256 reported in the log is `d4e4dc5d16acb78c5b815b237fff4ee7554305b0c6ef00051d08ed6d01bc28a1`. [Artifact 14627268628](https://github.com/EldonsLogic/sebaverse/actions/runs/44733660486/artifacts/14627268628).

DEV-010 and F3 remain in progress. Keep the [AUTH-014 supplier hold](auth-014-recovery-checkpoint.md) and resume assessment only after a qualifying supplier update. The result establishes that this hosted job could start and reach its runtime pre-use boundary. No account or spending diagnosis is implied. No further dispatch, pin change, gate change, deployment or billing action was taken in this evidence review.
