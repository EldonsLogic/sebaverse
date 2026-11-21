# DEV-010 independent resource-kind test audit

21 November 2026 · Reviewer `kind_test_audit` (Codex subagent) · Source `75986c145a8562583424dcd34b1fd89a9b62ed9c` · R037/R038/R040/R041/R046.

A stale file classification can let a private upload proceed or expose its manifest. This review covered the broker and authored test fixtures, with a 15-minute budget. The focused tests passed, and source inspection found no setup defect or false pass requiring a test change. The PostgreSQL cases remain staged for the qualified runtime.

- The focused fixture changes only the kind and verifies that the five saved scope fields and learner authorization generation still match. Its negative cases exercise byte intake, processing before scanning, drift during scanning or parsing, and private resolution. They check the relevant side effects, including no storage write at rejected intake and no manifest read on rejected resolution. [Focused cases](../../backend/tests/ingestion/test_resource_kind_fence.py#L15-L107)
- The independent requester has a different ID from the uploader. The positive case checks that the authorization lookup receives the requester and the saved resource ID. The same requester is denied when that lookup returns no resource. This catches a regression that substitutes uploader authority or imposes uploader-only access. [Requester case](../../backend/tests/ingestion/test_resource_kind_fence.py#L110-L125)
- The PostgreSQL fixture uses `material`, a valid kind under generic access policy. The staged scan and parse callbacks update the existing resource row, and the review/approval case uses the earlier valid scoped reviewer grant. Each scenario restores `file`, and the private-read case proves that both the learner and guardian can resolve the guardian’s upload while it is a file. The wrapper requires all three case names and a total of 24. [Access policy](../../backend/modules/access/policy.py#L4-L28) · [Reviewer grant](../../backend/tests/ingestion/postgres_probe.py#L107-L117) · [Staged cases](../../backend/tests/ingestion/postgres_probe.py#L251-L295) · [Wrapper](../../backend/tests/test_postgres_integration.py#L80-L100)

The review-manifest and approval kind denials are covered by the staged PostgreSQL probe. Executed focused coverage establishes behavior through the shared live guard but does not establish either separate review entry point. Database execution and locking, the scanner and parser runtimes, and process isolation are outside this result. The production authority proposal was outside the scope of review. DEV-010 and F3 remain in progress.

Executed from the repository root with the project’s local Python and authored fixtures. Exit 0, 16 passed.

```sh
SEBAVERSE_ENV=local DJANGO_DEBUG=1 backend/.venv/bin/python -m pytest backend/tests/ingestion/test_resource_kind_fence.py backend/tests/ingestion/test_dispatch_fence.py -q
```

`make foundation-check` exited 0. The artifact, economics, and foundation validators passed, and all 179 helper tests passed.
