# Hosted worker transport checks at `37e39e1`

20 November 2026 · DEV-010 / F3 · R039, R040, R046, R081. The automatic push workflow tested `37e39e19efa1feb16ebe81c9348a364e6af41907` on GitHub-hosted Ubuntu 24.04. It passed the database-free backend checks and failed at the native and image pre-use policy. [Workflow at tested commit](https://github.com/EldonsLogic/sebaverse/blob/37e39e19efa1feb16ebe81c9348a364e6af41907/.github/workflows/skeleton.yml) · [Run 44785151437, attempt 1](https://github.com/EldonsLogic/sebaverse/actions/runs/44785151437/attempts/1).

| Hosted check | Observed result |
| --- | --- |
| Database-free API and configuration boundaries | Web typecheck and build passed with 140 modules transformed. `pytest backend/tests -q -k 'not postgres_integration'` reported **494 passed, 1 deselected in 3.80s**, with no skips reported. The curriculum structural schema matched runtime serializers. |
| Static native and OCI assessment | Pinned scanners downloaded, exact derived OCI built and inspected, reviewed CI native patch applied, and package cataloging and advisory capture completed before database startup. |
| Native and image pre-use policy | Failed at 17:41:09 UTC with exit code 1. The policy reported 8 unresolved high/critical/unknown image advisories, 10 reviewed image findings with released fixes requiring an updated pin and re-review, and 15 system-native findings requiring explicit review. |
| Runtime steps gated by the pre-use policy | GitHub recorded the PostgreSQL migration/readiness/teardown, browser runtime installation, desktop/mobile loopback smoke, and skeleton job's foundation/dependency/phase regressions as skipped. The fifteenth retained-partial PostgreSQL scenario still has no run result. |
| Separate automatic workflows | [Foundation checks](https://github.com/EldonsLogic/sebaverse/actions/runs/44785151380) and [Dependency readiness](https://github.com/EldonsLogic/sebaverse/actions/runs/44785151536) both succeeded on the same commit. |

The aggregate Linux selection included the authored POSIX echo and malformed-output cases in the [worker result transport suite](https://github.com/EldonsLogic/sebaverse/blob/37e39e19efa1feb16ebe81c9348a364e6af41907/backend/tests/ingestion/test_result_transport.py). Native PDF extraction, scanner and OS isolation, and Arabic or bilingual extraction fidelity still need qualification. No learner-facing capability changed.

Read-only `gh run list` and `gh run view --attempt 1` (job state and `--log`) supplied these observations. The [skeleton job log](https://github.com/EldonsLogic/sebaverse/actions/runs/44785151437/job/136457916056) records the upload of [f2-evidence](https://github.com/EldonsLogic/sebaverse/actions/runs/44785151437/artifacts/14654631104), 1,801,887 bytes. No artifact contents were audited and no workflow was dispatched or rerun for this receipt.

DEV-010 and F3 remain in progress. Resume supplier assessment after a qualifying update under the [AUTH-014 supplier hold](auth-014-recovery-checkpoint.md).
