# Hosted consent cleanup consumer checks at `dceee32`

22 November 2026 · DEV-010 / F3 · R040 and R046. GitHub recorded three automatic push runs for `dceee327e556da01e28899c3c0c6de9109c8da3c`, all completed on attempt 1. [Commit](https://github.com/EldonsLogic/sebaverse/commit/dceee327e556da01e28899c3c0c6de9109c8da3c) · [Pinned skeleton workflow](https://github.com/EldonsLogic/sebaverse/blob/dceee327e556da01e28899c3c0c6de9109c8da3c/.github/workflows/skeleton.yml#L39-L44)

| Hosted workflow | Observed conclusion |
| --- | --- |
| [Local skeleton phase checks](https://github.com/EldonsLogic/sebaverse/actions/runs/45015749187/attempts/1) | Failed at native/image pre-use policy. On `ubuntu-24.04` with CPython 3.12.13, `pytest backend/tests -q -k 'not postgres_integration'` recorded **618 passed, 1 deselected in 4.68 seconds**. Web typecheck, build (140 modules transformed) and curriculum schema check also passed. [Job](https://github.com/EldonsLogic/sebaverse/actions/runs/45015749187/job/137187566899) |
| [Foundation checks](https://github.com/EldonsLogic/sebaverse/actions/runs/45015749252/attempts/1) | Passed. |
| [Dependency readiness](https://github.com/EldonsLogic/sebaverse/actions/runs/45015749229/attempts/1) | Passed. |

The native/image pre-use policy exited `1` at 11:09:47 UTC. It reported 19 unresolved high, critical or unknown image advisories, 15 image findings requiring explicit review, 10 previously reviewed image findings requiring a pin update and re-review because fixes were released, and 15 system-native findings requiring explicit review. These counts are the policy's reported categories.

The skeleton job skipped real PostgreSQL migration/readiness/teardown, browser setup, desktop/mobile loopback browser checks and its in-job foundation/dependency/phase regressions. The hosted test receipt covers the checked-in, DB-free consumer snapshot. DEV-010 and F3 remain open. The 36 staged PostgreSQL scenarios remain unrun.

GitHub reported successful upload of [f2-evidence](https://github.com/EldonsLogic/sebaverse/actions/runs/45015749187/artifacts/14751851665), 1,810,885 bytes, with metadata digest `sha256:a5827bcbfa3a3627f3c5fcc8725f846307f70126cd02962e3a0bbd2ebd93bdd1`. Verification used `gh run list`, attempt 1 job steps and log lines, and artifact metadata. The initial sandboxed `gh` request could not connect. Read-only access succeeded after approval. No run was dispatched or rerun and no artifact was downloaded.
