# Hosted extraction fidelity controls at `8a413d8`

20 November 2026 · DEV-010 / F3 · R039, R040, R041. GitHub recorded three automatic push runs from commit `8a413d8a23e036261ef8b66f19abacb9527b51c7`. This receipt records attempt 1 of each run, using read-only workflow metadata, step results and selected skeleton job logs. [Pinned workflow](https://github.com/EldonsLogic/sebaverse/blob/8a413d8a23e036261ef8b66f19abacb9527b51c7/.github/workflows/skeleton.yml) · [Skeleton run 44794098397](https://github.com/EldonsLogic/sebaverse/actions/runs/44794098397/attempts/1) · [Job 136489009326](https://github.com/EldonsLogic/sebaverse/actions/runs/44794098397/job/136489009326).

| Hosted check | Observed result |
| --- | --- |
| Database-free backend and web | The Ubuntu Linux runner reported **565 passed, 1 deselected in 5.26s** for `pytest backend/tests -q -k 'not postgres_integration'`. Web typecheck and build passed with 140 modules transformed. |
| Static native and image assessment | Scanner download, inspection of the derived image, the reviewed CI native patch, package cataloging and advisory capture completed before database startup. |
| Native and image pre-use policy | Failed with exit code 1 at 18:37:35 UTC. The policy reported eight unresolved high, critical or unknown image advisories, ten reviewed image findings with released fixes that require a pin update and new review, and 15 system-native findings requiring explicit review. |
| Gated runtime steps | PostgreSQL migration/readiness/teardown, browser setup, desktop/mobile loopback smoke and the skeleton job's foundation/dependency/phase regressions were skipped. The 21 staged PostgreSQL scenarios lack results on this commit. |
| Separate workflows | [Foundation checks, job 136489008647](https://github.com/EldonsLogic/sebaverse/actions/runs/44794098119/job/136489008647) and [Dependency readiness, job 136489008557](https://github.com/EldonsLogic/sebaverse/actions/runs/44794098123/job/136489008557) passed on the same commit. |

The database-free suite covers the offline comparison of authored Arabic/German/math reference text against synthetic result dictionaries. Native PDFium extraction, upload malware scanning, worker isolation, and Arabic and bilingual PDF fidelity still require qualification. [Comparator and local review evidence](dev-010-fidelity-controls.md).

The job logged the upload of [f2-evidence](https://github.com/EldonsLogic/sebaverse/actions/runs/44794098397/artifacts/14658481304), 1,801,886 bytes. This receipt relies on the original workflow results and selected logs. Artifact contents were outside the review.

DEV-010 and F3 remain in progress. Supplier reassessment awaits a qualifying update under [AUTH-014](auth-014-recovery-checkpoint.md).
