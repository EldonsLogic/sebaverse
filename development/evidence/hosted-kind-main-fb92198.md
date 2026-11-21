# Hosted resource-kind integration at `fb92198`

21 November 2026 · DEV-010 / F3 · R037, R038, R040, R041, R046. GitHub recorded three automatic push runs on `main` for commit `fb92198aa6f3cf693682db65d42f3c96978f0ac9`. All three completed on attempt 1. [Pinned skeleton workflow](https://github.com/EldonsLogic/sebaverse/blob/fb92198aa6f3cf693682db65d42f3c96978f0ac9/.github/workflows/skeleton.yml).

| Hosted workflow | Observed conclusion |
| --- | --- |
| [Local skeleton phase checks](https://github.com/EldonsLogic/sebaverse/actions/runs/44894277975/attempts/1) | Failed at the native/image pre-use policy. The [skeleton job](https://github.com/EldonsLogic/sebaverse/actions/runs/44894277975/job/136816473820) reported **571 passed, 1 deselected in 4.86s** on Ubuntu Linux for `pytest backend/tests -q -k 'not postgres_integration'`. Web typecheck and build passed with 140 modules transformed. |
| [Foundation checks](https://github.com/EldonsLogic/sebaverse/actions/runs/44894277983/attempts/1) | Passed. |
| [Dependency readiness](https://github.com/EldonsLogic/sebaverse/actions/runs/44894278133/attempts/1) | Passed. |

The skeleton job completed static scanner setup, derived image inspection, the reviewed CI native patch, cataloging and advisory capture before database startup. The native/image pre-use policy stopped the job with exit code 1 at 10:27:52 UTC. Its summary reported 19 unresolved high, critical or unknown image advisories, 15 image findings requiring explicit review, 10 reviewed image findings with released fixes requiring a pin update and new review, and 15 system-native findings requiring explicit review. These are policy-reported categories.

GitHub marked PostgreSQL migration/readiness/teardown, browser setup, desktop/mobile loopback smoke and the skeleton job’s foundation/dependency/phase regression step as skipped. The 24 staged PostgreSQL scenarios lack runtime results on this commit.

The job reported a successful upload of [f2-evidence](https://github.com/EldonsLogic/sebaverse/actions/runs/44894277975/artifacts/14702254991), 1,810,436 bytes. This receipt uses the original workflow metadata, step results and selected log lines. DEV-010 and F3 remain in progress.
