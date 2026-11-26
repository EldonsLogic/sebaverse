# U32 — Bounded offline tutoring state machine authorization

26 November 2026. Founder response in the current Antigravity chat following PR 10 (`89e0241`) approval and Option #2 offer.

Founder selected verbatim: “Shoot”.

Scope: Bounded DB-free synthetic-fixture sub-slice of DEV-013 while DEV-010 remains held on AUTH-014 (recorded as `AUTH-020`). One engineering day, at most two correction cycles, zero new dependencies, zero paid calls, and no database, SSE/HTTP endpoint, AG-UI SDK, model-provider, or UI execution. Permits a pure Python deterministic tutoring state machine (`backend/modules/tutoring/`) enforcing allowed state transitions, live server-derived access/consent checks, hint-ladder independence tracking, stale/cancelled-turn and wrong-item guards, idempotent command replay, safety-pause human-only resume, and integration with the merged DB-free retrieval, grading, and learning-ledger modules (`R017`, `R019`, `R023`, `R028`, `R053`, `R067`). Full DEV-013 dependencies (`DEV-009`, `DEV-012`), AG-UI/SSE transport (`R105`), F3/F4 phase exits, AUTH-014 supplier wait, and all runtime/security gates remain unchanged.
