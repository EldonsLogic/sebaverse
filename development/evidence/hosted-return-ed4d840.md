# Hosted manifest return checks at `ed4d840`

21 November 2026 · DEV-010 / F3 · R037, R038, R040, R041, R046. GitHub recorded three completed automatic push runs for `ed4d8404d627ff100cac31bff7311c4e044f49fc` on `main`. All three completed on attempt 1. This receipt reads the original runs without a dispatch or rerun. [Pinned skeleton workflow](https://github.com/EldonsLogic/sebaverse/blob/ed4d8404d627ff100cac31bff7311c4e044f49fc/.github/workflows/skeleton.yml).

| Hosted workflow | Observed conclusion |
| --- | --- |
| [Local skeleton phase checks](https://github.com/EldonsLogic/sebaverse/actions/runs/44898982292/attempts/1) | Failed at the native/image pre-use policy. The [skeleton job](https://github.com/EldonsLogic/sebaverse/actions/runs/44898982292/job/136830626567) recorded **585 passed, 1 deselected in 4.38 seconds** for `pytest backend/tests -q -k 'not postgres_integration'` on Ubuntu 24.04 with CPython 3.12.13. Web typecheck and build passed with 140 modules transformed. |
| [Foundation checks](https://github.com/EldonsLogic/sebaverse/actions/runs/44898982266) | Passed. |
| [Dependency readiness](https://github.com/EldonsLogic/sebaverse/actions/runs/44898982219) | Passed. |

Static scanner setup, derived image inspection, native patch, cataloging and advisory capture completed before the native/image pre-use policy exited `1` at 11:27:15 UTC. The policy reported 19 unresolved high, critical or unknown image advisories, 15 image findings requiring explicit review, 10 reviewed image findings with released fixes requiring a pin update and new review, and 15 system-native findings requiring explicit review. These are the policy’s reported categories.

The hosted job skipped PostgreSQL migration/readiness/teardown, browser setup, desktop/mobile loopback smoke and the skeleton job’s foundation/dependency/phase regressions. The staged 27 PostgreSQL scenarios lack runtime results for this commit. DEV-010 and F3 remain open. [Current PostgreSQL test scope](https://github.com/EldonsLogic/sebaverse/blob/ed4d8404d627ff100cac31bff7311c4e044f49fc/backend/tests/test_postgres_integration.py).

The job uploaded [f2-evidence](https://github.com/EldonsLogic/sebaverse/actions/runs/44898982292/artifacts/14705087221), 1,810,330 bytes. GitHub’s artifact metadata returned SHA-256 `0a914c63f4024fa7f581e973cce17e11a94ff500749f4319d84abe1734a43da1`. The receipt uses `gh run list`, the attempt 1 jobs endpoint, selected attempt 1 log lines and artifact metadata. The artifact itself was not downloaded.
