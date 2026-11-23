# DEV-010 bounded manual cleanup runner

23 November 2026 · R040/R046 · AUTH-015/U25. Threat: an unbounded or miscomposed operator invocation could delete the wrong namespace or bypass blocked cleanup policy. Current scope is authored local fixtures. Budget one disabled-by-default command slice, at most two review corrections. No daemon, real database/native activation, deployment or retention-policy change.

The current consumer already selects server-persisted consent intents and enforces cohort, lease, quota and purge checks. This increment adds a bounded manual entry point, not a new destructive authority. It must accept no upload/learner/intent selectors, preserve blocked states and never enable source-writer recovery implicitly. Trusted local composition, exact private-store/database pairing and all applicable runtime gates remain prerequisites. No actual operator invocation against a database is authorized by this code change.

Three real subagents own the command/contract, independent negative-first tests and independent review. Root owns this evidence, shared task/roster/checkpoint and integration. Product evidence will come from database-free command tests with fake consumer boundaries and authored temporary roots. This cannot qualify PostgreSQL transactions or production storage. Final API, results, corrections and limitations follow integration.

## Selected bounded interface

Root selected `run_consent_cleanup` with no custom command options. It requires exact enabled/local flags, explicitly configured loopback PostgreSQL and a trusted already-composed plain `PrivateObjects` instance. It must not instantiate storage or enable writer recovery. Validate and pin the existing private directory for the invocation, reject symlink/ownership/mode/namespace mismatches, then reuse the existing confirmed-purge primitive through a purge-only wrapper. This does not certify the pairing of a database with its source directory: trusted composition and runtime qualification remain separately required.

At most four calls with 25 targets per call; stop on the first consumer `None`. That means no result, not proof of an empty queue. Report coarse batch outcomes only, not unique intents or deleted-object counts. The command must not wrap file work in an outer transaction or replay blocked intents. No root/actor/object/scope/limit/recovery overrides are exposed. Root approval here is the implementation selection within the existing synthetic scope, not permission to invoke it against a database.

## Actual local results

Root `make backend-check` exited 0 on the released source/tests: 681 passed, one PostgreSQL integration test deselected, Django system check clean. The test owner passed 36 new command cases and all 334 ingestion cases. Tests use a fake consumer, refuse any `ensure_connection` call and assert blocked-intent replay is never invoked. Authored temporary roots demonstrate that a pathname replacement after pinning does not redirect deletion: only the original descriptor's files disappear. No real PostgreSQL query, migration, scheduler or native engine was invoked.

Implementation includes explicit disabling of implicit Django system/migration checks before its own prerequisite checks. A disabled command smoke invocation returned the expected fixed error and no work. Runtime errors expose no payload/IDs and warn that earlier batches may have committed. The work cap is not a wall-clock bound. Existing protected-writer roots are refused rather than losing their locking protocol. Final independent receipt and root foundation result follow.

One independent review correction removed Django's echo of unsupported CLI argument values. The command now preserves Django parser behavior while substituting one fixed message. Two new regression cases verify both native command-line parsing and `call_command`; cleanup does not start, source bytes remain unchanged, and supplied UUID/path markers do not reach output. Final root `make backend-check`: 683 passed, one PostgreSQL test deselected, Django clean. The new command suite is 38 cases. No production fence or test assertion was weakened.

## Final review and closing checks

[Independent review](dev-010-cleanup-runner-review.md) accepted the final exact command, tests and contract hashes after the one parser-privacy correction. Reviewer independently passed backend 683 (one PostgreSQL deselected), ingestion 336 including 38 command cases, consent 44 and foundation 179. Root closing `make foundation-check` passed artifact/economics/foundation validation and 179 helper tests. Its deliberate npm-timeout negative fixture is not a live network failure. Whitespace checks passed. All 37 staged PostgreSQL cases remain NOT RUN; F3 and RISK-F3-005 stay open. No source/test changed after final review.
