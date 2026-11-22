# Hosted consent cleanup intent checks at `89ce415`

21 November 2026 · DEV-010 / F3 · R046. GitHub recorded three completed automatic push runs on `main` for `89ce415884ae1480360283e1b8dae9fd2c6fabda`. All completed on attempt 1. [Commit](https://github.com/EldonsLogic/sebaverse/commit/89ce415884ae1480360283e1b8dae9fd2c6fabda) · [Pinned skeleton workflow](https://github.com/EldonsLogic/sebaverse/blob/89ce415884ae1480360283e1b8dae9fd2c6fabda/.github/workflows/skeleton.yml)

| Hosted workflow | Observed conclusion |
| --- | --- |
| [Local skeleton phase checks](https://github.com/EldonsLogic/sebaverse/actions/runs/44928622053/attempts/1) | Failed at the native/image pre-use policy. On `ubuntu-24.04` with CPython 3.12.13, `pytest backend/tests -q -k 'not postgres_integration'` recorded **597 passed, 1 deselected in 4.18 seconds**. Web typecheck and build passed with 140 modules transformed. [Job](https://github.com/EldonsLogic/sebaverse/actions/runs/44928622053/job/136920128469) |
| [Foundation checks](https://github.com/EldonsLogic/sebaverse/actions/runs/44928622175/attempts/1) | Passed. |
| [Dependency readiness](https://github.com/EldonsLogic/sebaverse/actions/runs/44928622185/attempts/1) | Passed. |

The native/image pre-use policy exited `1` at 17:13:19 UTC. It reported 19 unresolved high, critical or unknown image advisories, 15 image findings requiring explicit review, 10 previously reviewed image findings requiring a pin update and re-review because fixes were released, and 15 system-native findings requiring explicit review. These are the policy's reported categories.

The skeleton job skipped real PostgreSQL migration/readiness/teardown, browser setup, desktop/mobile loopback browser checks and its final foundation/dependency/phase regressions. This run covers consent cleanup intent capture. File purge, quota settlement, DEV-010 and F3 remained open.

GitHub reported a successful upload for [f2-evidence](https://github.com/EldonsLogic/sebaverse/actions/runs/44928622053/artifacts/14717220035), 1,810,424 bytes, with metadata digest `sha256:579b041a6e446809881b672ec7b172227a29264e37f79aee53199f8a0c704119`. Verification used the original `gh run list`, attempt 1 jobs and targeted log lines, and the GitHub Actions artifact metadata endpoint. No run was dispatched or rerun and no artifact was downloaded.
