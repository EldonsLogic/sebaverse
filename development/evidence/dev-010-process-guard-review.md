# DEV-010 independent worker process guard review

20 November 2026 at 11:40 UTC · AUTH-013 · R040/R046. **Accepted as an unconnected process watchdog for authored standard-library fixtures.** This bounded review covered a stalled worker, excess or exposed pipe data, failed cleanup and accidental signaling outside the owned group. Current fixtures contain synthetic data with no learner exposure. [Worker contract](../../workers/parser/process-guard-contract.md) · [Authorization](../APPROVALS.md#auth-013--founder-direct-pypdfium2-text-only-poc-direction-19-november-2026).

The guard denies before spawn when the program is absent, paths or script bytes fail verification, or input and limits are invalid. It starts the reviewed absolute executable with fixed arguments, a private temporary directory, closed inherited descriptors, a new session and a minimal environment. All three pipes are nonblocking, with bounded partial writes, capped stdout and counted/discarded stderr. A successful result is untrusted bytes for separate validation at composition time. [Implementation](../../workers/parser/process_guard.py).

The controller observes the direct child's exit before reaping it. This keeps its process group identifier reserved through cleanup. A kqueue exit event is used on the tested macOS host. The `waitid` path was reviewed statically. Tests exercise a held descendant pipe and verify that the descendant releases a lock. A separate authored process remains alive while the target is killed. Tests also verify direct-child reaping, pipe closure and temporary directory removal. [Subprocess tests](../../backend/tests/ingestion/test_process_guard.py).

During review, cancellation callback coverage was extended to `SystemExit` and `KeyboardInterrupt`. The final implementation converts those callback failures into the same bounded `controller_failed` result as ordinary callback exceptions. Tests confirm cleanup and that a synthetic private marker is absent from both the error string and formatted traceback. No outstanding finding blocks this authored-fixture increment.

## Independent checks

| Check | Actual result |
| --- | --- |
| `make test-ingestion` | Exit 0. 127 passed, including 31 process-guard cases. |
| `make backend-check` | Exit 0. 462 passed, PostgreSQL integration deselected, Django checks clean. |
| `git diff --check` | Exit 0. |
| Diff against HEAD for ingestion service, backend settings, digital PDF core and scanner approved assets | Empty. |

Codex agent `runtime_fix_recheck` reviewed the implementation and tests without authoring either. Checks ran on Darwin arm64 with Python 3.12.13 against the working tree based on `d481eb5`. The [guard](../../workers/parser/process_guard.py) SHA-256 is `73b9835b3f0904120ac1833900875b026b9ee867d4afd229e178b2ae4911a5ea`. The [tests](../../backend/tests/ingestion/test_process_guard.py) SHA-256 is `0ede2dea802a18040aee383e7463c4b002f711ecbad6d1951738eec6ef8cde03`. The [authored child](../../backend/tests/ingestion/fixtures/process_guard_child.py) SHA-256 is `aa43bfeb3d082cbfeaab166b47b043e42f9b30831c4a94bc5bf7cef2b5c669f7`.

The guard assumes an immutable reviewed program location, exclusive direct-child reaping and a promptly returning cancellation predicate. Process groups and the wall-clock watchdog leave OS filesystem, network, process, CPU and memory isolation to a qualified composition. The target Linux watchdog path, native PDFium worker, scanner, actual extraction fidelity and F3 exit remain unverified.

## Final checkpoint review

20 November 2026. Independently reconciled the checkpoint, parser README, DEV-010 evidence, roster and AUTH-014 scope against reviewed code, test records and static package receipts. The three guard/test hashes above still match. Root's reported closing results were 179 helper tests and 462 database-free backend tests. The existing PostgreSQL and native holds, Darwin-only watchdog execution, and F3 in-progress status are accurately stated.

Read-only spot checks matched the three APK and signed-index lengths and SHA-256 values to the package receipt. The cached archive hash and all ten original parent layer sizes and SHA-256 digests also matched. Its 45-row installed database confirms libcrypto3 and libssl3 at `3.5.9-r0` and the absence of an `openssl` package or `/usr/bin/openssl`. This confirms the reported scope discrepancy. The three-package gate design describes the original proposal. Any narrowed profile needs the pending founder decision and should demonstrate that the absent CLI stays absent. Package signatures are reported in the package review and were outside this consistency check. No assembly, package execution, image use, adoption or gate change occurred.

**Checkpoint verdict.** The authored watchdog and static assessment can be recorded with the explicit AUTH-014 scope hold. I flagged wording about the held Noble scanner candidate and matching an existing BusyBox trigger path for the integrator. No additional runtime qualification is implied.
