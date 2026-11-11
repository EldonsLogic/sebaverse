# F1 dependency readiness run — 11 November 2026

Scope: U15/AUTH-002, exact minimal backend/web toolchains and ignored local environments only. F0 passed before DEV-005 started. No product app, DB connection, model/assets, paid calls, external data or deployment.

## Observed local results

- Python3.12.13/uv0.11.14: exact hashed official PyPI graph18; wheel-only locked sync16 applicable packages; uv pip check/lock and DRF/Uvicorn/Psycopg compatibility smoke passed.
- pip-audit2.10.1: every18 locked Python package queried, no published Python advisories; raw audit and exact command evidence preserved.
- Node24.22.1/npm10.8.2: exact npm graph81 entries, clean lifecycle-disabled install31 applicable packages; npm ls and audit exit0, zero reported advisories.
- Root make dependency-check: evidence/lock/license/raw-audit integrity and actual import/render/exact-version smoke passed.
- Root make foundation-check: artifacts/economics/phase checks and22 tests passed (14 phase/contract +8 dependency negatives). Original36 research hashes unchanged.

## Explicit limitations and held boundaries

Metadata/notice inspection is not blanket legal clearance. Mac native Psycopg libraries and optional target-platform/rolldown/lightningcss artifacts have release/native notice and security limitations recorded in inventories. F2 requires native/container closure before DB/network/image use and release needs distribution obligations resolved; pip-audit/npm audit do not certify OS/native/CPython or app safety. PostgreSQL manifest pinned only; not pulled/started/scanned. Docling/OCR/scanner and all model/eval assets disabled until their own gates.

Python bootstrap initially created a task-owned executable shortcut outside project; worker removed only that verified shortcut and documented --no-bin for repeatable setup. No persistent global runtime configuration is claimed changed.

## Remaining before F1 exit

Actual clean Ubuntu CI passed on ba2edb2df95ce584f9408e4a3822b7ec91a60f8c: Dependency readiness run43052547533 and Foundation checks run43052547439. Exact hosted job/step evidence is in f1-github-ci.json. Independent closing review passed; F1 is closed for its explicitly scoped backend/web readiness. F2–F8 remain not_started. Original local/remote main SHA matched at publication; later metadata checkpoints are tracked in Git and separately verified on push.
