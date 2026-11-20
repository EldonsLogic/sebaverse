# Independent review of the upload dispatch fence

20 November 2026 · DEV-010 / F3 · R040, R046. Reviewer `latest_ci`, a separate Codex subagent with ownership of this evidence only. Reviewed the working patch against `37e39e19efa1feb16ebe81c9348a364e6af41907`. No blocking finding in the broker correction for the authored fixtures. F3 remains in progress.

- The broker validates the clean scanner receipt, then reloads the locked upload and learner to check live authorization before calling the parser. Generation and dispatch mismatches return without changing the newer owner's row. Loss of permission withdraws the current dispatch and increments its generation.
- The same check runs before publication and before an adapter failure can return the upload to quarantine. The parser gets a copy of the primitive expected fields. The broker validates against its own values and records the asset IDs that cleared review. The authorized fixture still writes a scoped `needs_review` manifest and charges derived bytes.
- The broker releases its transaction before either adapter callback. A revocation visible to the check blocks parser handoff. Revocation may still happen after the pre-parser transaction releases, and an adapter may already be running when it happens. The final check protects publication in that case. Process cancellation and operating system isolation require separate evidence before activation.

| Independent check on macOS 26.5.1, Python 3.12.13 | Observed result |
| --- | --- |
| `pytest backend/tests/ingestion/test_dispatch_fence.py -q` | 10 passed in 0.05 s |
| `make test-ingestion` | 169 passed in 1.77 s |
| `pytest backend/tests -q -k 'not postgres_integration'` | 504 passed, 1 deselected in 2.50 s |
| Python AST parse of the broker and three changed test files | Passed |
| PostgreSQL integration | NOT RUN. Statically reviewed the six new persisted-state scenarios and the wrapper's 21-scenario expectation. The retained-partial scenario and the six new scenarios still lack execution results. The [hosted pre-use failure](hosted-transport-37e39e1.md) gates native runtime use. |

The tests use authored scanner/parser callbacks, a local private store and mocked database locks for the database-free suite. They cover withdrawal and consent changes during scanning, old dispatches replaced during scanning or parsing, mutation of expected provenance and adapter IDs, revocation while the parser returns or raises, and an authorized result. Real PostgreSQL lock behavior, native scanner and PDF extraction, Arabic or bilingual extraction fidelity, and operating system controls remain unqualified. The correction protects a future upload path and adds no learner-facing capability.

Reviewed Git blobs for the [service](../../backend/modules/ingestion/service.py), [database-free tests](../../backend/tests/ingestion/test_dispatch_fence.py), [PostgreSQL scenarios](../../backend/tests/ingestion/postgres_probe.py) and [wrapper](../../backend/tests/test_postgres_integration.py), respectively `8970950608e986ec4b437e3de9e09ec451d6d205`, `f8298eeb86a0793f74fdab50e053e3eba5e36e4c`, `94ece580fba688e5f88dd316e4abadf8682cffee` and `fbd5b2166dd0125fa8c3ce4e82794ab5def98afc`.
