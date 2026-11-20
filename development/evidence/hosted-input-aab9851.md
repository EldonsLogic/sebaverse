# Hosted authored parser input checks at `aab9851`

20 November 2026 · DEV-010 / F3 · R037, R038, R039, R040, R041, R046. GitHub recorded three automatic push runs for `aab98518bc750e0e8d7ce8783c3d8e735c718e7e`. The skeleton run passed the database-free backend and web checks. The native and image pre-use policy failed before database or browser execution. [Workflow at tested commit](https://github.com/EldonsLogic/sebaverse/blob/aab98518bc750e0e8d7ce8783c3d8e735c718e7e/.github/workflows/skeleton.yml) · [Skeleton run 44788429816, attempt 1](https://github.com/EldonsLogic/sebaverse/actions/runs/44788429816/attempts/1).

| Hosted check | Observed result |
| --- | --- |
| Database-free API and configuration boundaries | `pytest backend/tests -q -k 'not postgres_integration'` reported **534 passed, 1 deselected in 4.29s**. Web typecheck and build passed with 140 modules transformed. |
| Static native and image assessment | Pinned scanner download, derived image inspection, reviewed CI native patch, package cataloging and advisory capture completed on the hosted runner before database startup. |
| Native and image pre-use policy | Failed with exit code 1 at 18:01:26 UTC. The policy reported eight unresolved high, critical or unknown image advisories, ten reviewed image findings with released fixes requiring a pin update and re-review, and 15 system-native findings requiring explicit review. |
| Gated runtime checks | PostgreSQL migration/readiness/teardown, browser setup, desktop/mobile loopback smoke, and the skeleton job's foundation/dependency/phase regressions were skipped. The 21 staged PostgreSQL scenarios have no run result on this commit. |
| Separate automatic workflows | [Foundation checks](https://github.com/EldonsLogic/sebaverse/actions/runs/44788429853) and [Dependency readiness](https://github.com/EldonsLogic/sebaverse/actions/runs/44788429759) passed on the same commit. |

The database-free result covers the guarded authored input and fake extraction regressions. Native PDFium, the malware scanner, worker isolation, Arabic and bilingual PDF fidelity, and PostgreSQL integration still require separate evidence. [Authored input evidence](dev-010-authored-input.md).

The receipt uses read-only `gh run list` and `gh run view` for the original push runs and attempt 1 of the [skeleton job](https://github.com/EldonsLogic/sebaverse/actions/runs/44788429816/job/136469392327). The job logged upload of [f2-evidence](https://github.com/EldonsLogic/sebaverse/actions/runs/44788429816/artifacts/14654977839), 1,801,920 bytes. Artifact contents were outside this review. The original workflows were left as recorded.

DEV-010 and F3 remain in progress. Supplier reassessment awaits a qualifying update under the [AUTH-014 supplier hold](auth-014-recovery-checkpoint.md).
