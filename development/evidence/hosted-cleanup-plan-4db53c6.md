# Hosted consent cleanup planning checks at `4db53c6`

21 November 2026 · DEV-010 / F3 · R046. GitHub recorded three completed automatic push runs for `4db53c639f4e110416724e316e603dd6d8334fe1` on `main`. All three completed on attempt 1. This receipt uses the existing runs. [Commit](https://github.com/EldonsLogic/sebaverse/commit/4db53c639f4e110416724e316e603dd6d8334fe1) · [Pinned skeleton workflow](https://github.com/EldonsLogic/sebaverse/blob/4db53c639f4e110416724e316e603dd6d8334fe1/.github/workflows/skeleton.yml)

| Hosted workflow | Observed conclusion |
| --- | --- |
| [Local skeleton phase checks](https://github.com/EldonsLogic/sebaverse/actions/runs/44900310668/attempts/1) | Failed at the native/image pre-use policy. On `ubuntu-24.04` with CPython 3.12.13, `pytest backend/tests -q -k 'not postgres_integration'` recorded **585 passed, 1 deselected in 4.62 seconds**. The web typecheck and build passed with 140 modules transformed. [Job](https://github.com/EldonsLogic/sebaverse/actions/runs/44900310668/job/136834626751) |
| [Foundation checks](https://github.com/EldonsLogic/sebaverse/actions/runs/44900310650/attempts/1) | Passed. |
| [Dependency readiness](https://github.com/EldonsLogic/sebaverse/actions/runs/44900310632/attempts/1) | Passed. |

The native/image pre-use policy exited `1` at 11:44:02 UTC after advisory capture. It reported 19 unresolved high, critical or unknown image advisories, 15 image findings requiring explicit review, 10 previously reviewed image findings requiring a pin update and re-review because fixes were released, and 15 system-native findings requiring explicit review. These counts are the policy's reported categories.

The skeleton job skipped real PostgreSQL migration/readiness/teardown, browser setup, desktop/mobile loopback browser checks and its final foundation/dependency/phase regressions. This commit covered cleanup planning. Cleanup implementation and acceptance, DEV-010 and F3 remained open.

GitHub reported a successful evidence upload for [f2-evidence](https://github.com/EldonsLogic/sebaverse/actions/runs/44900310668/artifacts/14705074794), 1,810,434 bytes, with metadata digest `sha256:a782add4bc43744b76db4b136f2f86338c0b6e4e7049ca3c708b1e4f7e81b4bf`. Verification used `gh run list --commit`, `gh run view` for job status and selected attempt 1 log lines, and the GitHub Actions artifact metadata endpoint. There was no dispatch, rerun or artifact download.
