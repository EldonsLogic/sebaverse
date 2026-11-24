# Hosted manual cleanup command checkpoint

24 November 2026 · Exact commit `6a72adda9e89b86ec47b542022c6e763fb0d502f`. Root read the original completed jobs; no rerun or artifact execution.

[Run 45140735323](https://github.com/EldonsLogic/sebaverse/actions/runs/45140735323) built 140 web modules and passed 683 DB-free backend tests with one PostgreSQL test deselected. Advisory capture passed. Native/image pre-use failed: 19 unresolved image High/Critical/unknown matches, 15 image findings requiring explicit review, 10 released fixes ending reviewed findings and 15 system-native findings requiring review. The categories overlap. PostgreSQL migration/readiness/teardown and browser/loopback UI steps were skipped; the later combined regressions step was skipped. Separate [Foundation 45140735356](https://github.com/EldonsLogic/sebaverse/actions/runs/45140735356) and [Dependency readiness 45140735290](https://github.com/EldonsLogic/sebaverse/actions/runs/45140735290) completed successfully.

The first log extraction found test results but could not parse the gate JSON because GitHub labeled the archived rows `UNKNOWN STEP`. A bounded read of the failed-step log then recovered the exact checker errors. This was a read-only evidence correction, not another workflow run or repair attempt.

No database-backed command, native scanner/parser, supplier route or new security exception ran. All 37 staged PostgreSQL scenarios remain NOT RUN; AUTH-014 supplier wait and F3 remain open.
