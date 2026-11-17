# Current development checkpoint

17 November 2026. Private canonical repository: https://github.com/EldonsLogic/sebaverse. Verify actual Git HEAD/remote before trusting a named commit.

**F0–F2 passed. F3 is in progress; F4–F8 have not started. DEV-001–007 are done. DEV-008 is in review: identity/access code passed independent review; actual PostgreSQL and hosted integration are pending.**

The Arabic-first local shell is available at http://127.0.0.1:8030 while its task-owned preview process is running. It has home, materials, practice and progress routes. There is a new server-side identity/access foundation and CSRF bootstrap; no signup UI, uploads, tutoring, grading or model calls. DEV-007 adds subject-independent versioned contracts and 52 authored draft records across three subjects, two editions each and a private overlay; no visible feature was added.

At c38bb04, hosted dependency run 44161448859, foundation run 44161448845 and full skeleton run 44161448815 all passed, including actual native pre-use, PostgreSQL, browser and teardown checks. Local results: 33 contract tests, 116 database-free backend tests and 152 helper tests passed. Independent review approved DEV-007 and AUTH-005's exact restricted recovery. See [evidence/dev-007.md](evidence/dev-007.md) and [evidence/auth-005-advisory-review.md](evidence/auth-005-advisory-review.md).

AUTH-005 is temporary synthetic-only residual-risk acceptance: npm expires 20 November at 19:38:23 UTC; the added native rows keep the 21 November expiry. Findings are unresolved; new findings/inputs, expiry, production, exposed services and real-data use are not cleared. The local macOS database path remains held. F3's four exit suites remain not run; official curriculum approval and the educator-reviewed item bank remain outstanding. AUTH-004/005 grant no paid calls, deployment, copyrighted textbook ingestion or real-minor use.

DEV-008 local results: 310 database-free backend tests, including 162 authorization and 32 consent cases, passed; 152 foundation/helper tests passed. The native-gated PostgreSQL probe adds 120 scope negatives plus focused actor/revocation/constraint cases, not yet executed. See [evidence/dev-008.md](evidence/dev-008.md). No next task starts before its required integration result.
