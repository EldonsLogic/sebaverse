# Current development checkpoint

16 November 2026. Shared private repository: https://github.com/EldonsLogic/sebaverse.

**F0, F1 and F2 passed. F3 not started. F4 to F8 not started.** DEV-001 to DEV-006 are done. The next task is DEV-007.

Check the actual branch, HEAD and remote before trusting any commit named here.

## What exists

A local Arabic-first shell (Django and React) with home, materials, practice and progress routes, health and readiness endpoints, and a PostgreSQL foundation proven on disposable CI with synthetic data only. There are no accounts, uploads, tutoring, grading or model calls yet. No real learner data, paid provider or deployment has been used.

## F2 exit, 15 November 2026

- Hosted run 43730557172 at commit f952d7f succeeded: 83 backend tests without a database, 1 real PostgreSQL integration case (migrations, SCRAM, readiness, teardown), the native and image pre-use policy, typecheck and build, desktop and mobile browser checks, and 138 foundation and helper tests.
- Independent review verdict: PASS for the synthetic technical scope. See [evidence/f2-phase-review.md](evidence/f2-phase-review.md) and [evidence/f2-passed-43730557172/run.json](evidence/f2-passed-43730557172/run.json).
- Findings kept open, not fixed: 3 in the image, 66 native, 1 supplier-core. Their reviews are scoped to this source, artifact and workload and expire; they need fresh review before any reuse.
- The local macOS database path stays held behind its own native prerequisites.

## Since F2

- 16 November: founder instruction U18 added [QUALITY-BAR.md](QUALITY-BAR.md) and `tools/brief.py`. An engineering review is in [evidence/review-2026-11-16.md](evidence/review-2026-11-16.md); its findings 7 to 14 are to be handled inside the F3 tasks that touch those files.
- 16 November: GitHub moved `ubuntu-latest` to 26.04 and the native patch step refused it (run 43946770491). All workflows are now pinned to `ubuntu-24.04`, the reviewed baseline. Run 43947283433 at 63b66c3 then passed in full, including the real PostgreSQL case.

## Next action

1. Run `python3 tools/brief.py DEV-007`.
2. Define real commands for the four F3 gate suites in phase-gates.json before writing feature code.
3. Implement DEV-007: versioned subject, curriculum, item and rubric contracts with authored language, quantitative and science fixtures. Synthetic data only.

Authority for F3 is AUTH-004 (U17) in [APPROVALS.md](APPROVALS.md): existing reviewed dependencies, zero paid providers, no real child records, no copyrighted textbook ingestion, no deployment. Each new dependency, parser, scanner or model asset still needs its own review.

## Known limits

- The runner pin is a holding measure. Ubuntu 24.04 runners will be retired eventually; plan the native review for the next baseline before then, sized by QUALITY-BAR.md section 2.
- No security, legal or educational certification is claimed. The 15 November database result was read from retained CI records and has not been reproduced locally.
