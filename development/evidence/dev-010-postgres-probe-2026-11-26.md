# DEV-010 PostgreSQL integration and AUTH-022 synthetic-CI evidence — 26 November 2026

Observed hosted Linux/amd64 CI result on PR 13 (`antigravity/auth-022-synthetic-ci-postgres-2026-11-26`) at commit `2aadaafc51efb66f46e24605628ae7ee67b904b1` under founder authorization `U34` / `AUTH-022`.

## Hosted CI run

- **Workflow:** `Local skeleton phase checks` (`.github/workflows/skeleton.yml`)
- **Run URL:** https://github.com/EldonsLogic/sebaverse/actions/runs/45864202204
- **Conclusion:** **PASS** (all 7 PR 13 checks green: Foundation checks ×2, Dependency readiness ×2, Static PostgreSQL remediation, Local skeleton phase checks ×2).
- **Key passing steps in run `45864202204`:**
  - `Compile web and test DB-free API/config boundaries`: `success`
  - `Build and inspect exact derived OCI without executing database`: `success`
  - `Apply exact reviewed Ubuntu CI native patch`: `success`
  - `Identify actual patched system libpq chain and static symbol imports`: `success`
  - `Catalog actual native packages and exact derived artifact`: `success`
  - `Record all advisory reports without starting database`: `success`
  - `Enforce native/image pre-use policy`: `success` (`--scope synthetic-ci`, keeping `execution_scope="standard"` 100% strict and unchanged; KEV/Critical/Unknown/PostgreSQL-core/system-libpq High findings remain blocking; original `AUTH-007` 30-day expiry `2026-12-18` preserved)
  - `Real PostgreSQL migration, readiness and teardown smoke`: `success` (`tools/run_postgres_smoke.py` executed `backend/tests/test_postgres_integration.py`, including Django migrations, PostgreSQL 17 SCRAM-SHA-256 / no-TLS / no-GSS checks, `authorization/postgres_probe.py`, `consent/postgres_probe.py`, and DEV-010's 37 synthetic `ingestion/postgres_probe.py` cases, plus clean teardown)
  - `Loopback server, desktop/mobile browser and teardown`: `success`
  - `Foundation, dependency and phase regressions`: `success` (183/183 unit tests)

## Scope boundaries (what this does NOT establish)

- Synthetic loopback fixtures only; zero real child data, zero real scanner/OCR/PDFium execution, zero production deployment.
- DEV-010 / F3 phase exit still requires qualified scanner, one-source worker authority/ADR disposition, storage/concurrency, and measured Arabic/bilingual extraction fidelity (`R039`).
- Full strict `execution_scope="standard"` pre-use policy remains mandatory before any real data, user traffic, or deployment.
