# Hosted parser dispatch checks at `2ecb5c9`

20 November 2026 · DEV-010 / F3 · R037, R038, R040, R041, R046. GitHub recorded three automatic push runs for `2ecb5c9bf3c5e39c054c9e60e378ffc67f94721a`. The skeleton run passed the database-free backend and web checks. Its native and image pre-use policy failed before database or browser execution. [Workflow at tested commit](https://github.com/EldonsLogic/sebaverse/blob/2ecb5c9bf3c5e39c054c9e60e378ffc67f94721a/.github/workflows/skeleton.yml) · [Skeleton run 44786949237, attempt 1](https://github.com/EldonsLogic/sebaverse/actions/runs/44786949237/attempts/1).

| Hosted check | Observed result |
| --- | --- |
| Database-free API and configuration boundaries | `pytest backend/tests -q -k 'not postgres_integration'` reported **504 passed, 1 deselected in 3.87s**. Web typecheck and build passed with 140 modules transformed. |
| Static native and OCI assessment | Downloaded the pinned scanners, built and inspected the exact derived OCI, applied the reviewed CI native patch, and completed package cataloging and advisory capture before database startup. |
| Native and image pre-use policy | Failed at 17:52:44 UTC. The policy reported eight unresolved high/critical/unknown image advisories, ten reviewed image findings with released fixes requiring a pin update and re-review, and 15 system-native findings requiring explicit review. |
| Gated runtime checks | GitHub skipped PostgreSQL migration/readiness/teardown, browser runtime installation, desktop/mobile loopback smoke and the skeleton job's foundation/dependency/phase regressions. The 21 staged PostgreSQL scenarios have no run result on this commit. |
| Separate automatic workflows | [Foundation checks](https://github.com/EldonsLogic/sebaverse/actions/runs/44786949352) and [Dependency readiness](https://github.com/EldonsLogic/sebaverse/actions/runs/44786949303) succeeded on the same commit. |

The aggregate backend run covered the in-memory broker dispatch regressions. PostgreSQL locking behavior, scanner and native parser qualification, OS isolation, and Arabic or bilingual extraction fidelity still require their own evidence. [Dispatch correction and local evidence](dev-010-dispatch-fence.md).

Read-only `gh run list` and `gh run view --attempt 1` supplied the workflow state and job log. The [skeleton job](https://github.com/EldonsLogic/sebaverse/actions/runs/44786949237/job/136464202269) recorded upload of [f2-evidence](https://github.com/EldonsLogic/sebaverse/actions/runs/44786949237/artifacts/14655111955), 1,801,906 bytes. The artifact contents were outside this review. This receipt used the original push runs.

DEV-010 and F3 remain in progress. Supplier reassessment awaits a qualifying update under the [AUTH-014 supplier hold](auth-014-recovery-checkpoint.md).
