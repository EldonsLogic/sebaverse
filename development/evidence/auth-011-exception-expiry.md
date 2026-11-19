# AUTH-011 — Synthetic security exceptions end on a released fix

18 November 2026. Founder decision [U21](../../sources/exception-expiry-instruction.md). Implemented by Claude Code (claude-opus-5-5) on branch `claude/exception-expire-on-fix`.

## Why this was needed

Three groups of security reviews let CI run the disposable synthetic database while known findings stay open:

| Review | Findings | Old expiry | Old binding |
|---|---|---|---|
| AUTH-005 npm (`infra/development-npm-review.json`) | picomatch ReDoS, GHSA-fc5q-39xc-vjpf, 4 High audit rows | 20 Nov 19:38 UTC, 3-day cap | package files, build config and every file under `web/src` |
| AUTH-007 OpenSSL (`infra/synthetic-openssl-review.json`) | 4 CVEs in Alpine `libssl3`/`libcrypto3` 3.5.9-r0, 8 High matches | 20 Nov 11:39 UTC, 3-day cap | every backend `.py` file and every `tools/**/*.py` |
| DEV-006 scoped reviews (`infra/security-reviewed-findings.json`) | 105 Medium/Negligible image and native findings | 20 and 21 Nov, 7-day cap | every backend `.py` file |

The short caps were meant to force a re-check for fixes. In practice no fix existed on 18 November (npm's latest picomatch was 4.0.7, the affected maximum; Alpine 3.22 and 3.23 still shipped `libssl3` 3.5.9-r0; the scanner reported fix state `unknown` for all 8 OpenSSL matches and `not-fixed`/`wont-fix` for every native finding), so each expiry only meant re-dating the same review. The per-file bindings also meant any new backend or web feature broke CI until the reviews were rebound.

## What changed

- **Ends on a released fix.** `tools/security/check_reports.py` now ends a reviewed finding or AUTH-007 exception as soon as the scanner reports `fix.state == "fixed"` with versions. CI then fails with "fix released for reviewed findings; update the pinned artifact and re-review". `tools/check_npm_audit.py` asks the npm registry for releases above the reviewed highest affected version (`fix_watch`), and fails closed if the lookup fails.
- **30-day backstop** after the review date, replacing 3 days (AUTH-005, AUTH-007) and 7 days (scoped reviews). New expiries: npm 17 December, OpenSSL 18 December, scoped reviews 15 to 18 December 2026.
- **Bindings narrowed to the runtime surface.** Scoped and OpenSSL reviews bind `backend/pyproject.toml`, `backend/uv.lock`, `backend/config/environment.py`, `backend/config/settings.py`, `backend/manage.py` and `tools/run_postgres_smoke.py`; OpenSSL also binds the image lock, `infra/local/postgres/`, `.github/workflows/skeleton.yml` and `tools/security/*.py`. The npm review binds the package files, `vite.config.ts`, the dependency workflow and its checker. Application modules and UI files no longer invalidate the reviews, under the founder-approved binding scope. This is not a proof that feature code cannot reach new native paths: the bound runner still executes application probes. Such behavior changes retain their ordinary code, dependency and safety review requirements.

Unchanged: exact finding identities, versions and severities; synthetic CI only; production and standard scope refused; Critical, unknown-severity, known-exploited and unreviewed findings block; no finding is cleared.

## Advisory withdrawn

GitHub withdrew GHSA-fc5q-39xc-vjpf at 15:38:56 UTC on 18 November 2026. From then, `npm audit` reports zero findings for `web/`, so the AUTH-005 exception is not used. It stays on file and would apply only if the same exact findings return.

## Verification

| Command | Result |
|---|---|
| `python3 -m unittest discover -s tools/tests -p 'test_*.py'` | 172 passed (163 before; 11 new tests and 2 replaced) |
| `python3 tools/check_npm_audit.py --scope synthetic-development` and `--scope production` | pass, 0 findings (advisory withdrawn) |
| `python3 tools/validate_project.py`, `check_foundation.py`, `model_economics.py` | PASS, PASS, exit 0 |
| Hosted CI on this branch | recorded in the pull request |

New negative tests: a released fix ends a reviewed finding and the npm exception; missing registry data or fix watch fails closed; a window over 30 days fails; changes to the image pin, driver lock, connection settings, smoke runner or security tools still invalidate the reviews; a new application module does not.

## For the next agent

Add AUTH-011 to `development/APPROVALS.md` and U21 to `sources/source-catalog.md`, and correct the expiry dates in `CURRENT-STATE.md`. Those files were being edited on `antigravity/dev-010-handover` when this was written, so this change left them alone to avoid conflicts.
