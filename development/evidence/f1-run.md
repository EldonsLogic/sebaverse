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

Independent final F1 review and actual clean Ubuntu CI still pending at this checkpoint. F1 remains in_progress; F2–F8 not_started. No phase pass inferred from the local smoke alone.
