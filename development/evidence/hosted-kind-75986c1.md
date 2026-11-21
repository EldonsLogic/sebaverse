# Hosted resource-kind fence at `75986c1`

20 November 2026 · DEV-010 / F3 · R037, R038, R040, R041, R046. GitHub recorded three automatic push runs on `codex/resource-kind-review` for commit `75986c145a8562583424dcd34b1fd89a9b62ed9c`. All three completed on attempt 1. [Pinned skeleton workflow](https://github.com/EldonsLogic/sebaverse/blob/75986c145a8562583424dcd34b1fd89a9b62ed9c/.github/workflows/skeleton.yml).

| Hosted workflow | Observed conclusion |
| --- | --- |
| [Local skeleton phase checks](https://github.com/EldonsLogic/sebaverse/actions/runs/44802269560/attempts/1) | Failed at the native/image pre-use policy. The [skeleton job](https://github.com/EldonsLogic/sebaverse/actions/runs/44802269560/job/136517166866) reported **571 passed, 1 deselected in 4.39s** on Ubuntu Linux for `pytest backend/tests -q -k 'not postgres_integration'`. Web typecheck and build passed with 140 modules transformed. |
| [Foundation checks](https://github.com/EldonsLogic/sebaverse/actions/runs/44802269557/attempts/1) | Passed. |
| [Dependency readiness](https://github.com/EldonsLogic/sebaverse/actions/runs/44802269522/attempts/1) | Passed. |

The skeleton job completed static scanner setup, derived image inspection, the reviewed CI native patch, cataloging and advisory capture before database startup. The native/image pre-use policy failed with exit code 1 at 19:29:43 UTC. It reported eight unresolved high, critical or unknown image advisories, ten reviewed image findings with released fixes requiring a pin update and new review, and 15 system-native findings requiring explicit review.

GitHub marked real PostgreSQL migration/readiness/teardown, browser setup, desktop/mobile loopback smoke, and the skeleton job's foundation/dependency/phase regression step as skipped. The 24 staged PostgreSQL scenarios lack runtime results on this commit.

The job logged the successful upload of [f2-evidence](https://github.com/EldonsLogic/sebaverse/actions/runs/44802269560/artifacts/14662270221), 1,801,928 bytes. This receipt draws on workflow metadata, step results and selected log lines.

The [resource-kind fence report](dev-010-resource-kind-fence.md) records the separate local tests. DEV-010 and F3 remain in progress.
