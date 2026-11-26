# Post-PR 7 options note — 26 November 2026

Base: `main` at `c51f84b` (PR 7 merged on 26 November 2026). This note adds no execution authority, changes no gate or threshold, and starts no new implementation.

## Why work is paused

F0 through F2 have passed, AUTH-016 (bounded DEV-011 offline preflight) is complete, and AUTH-017 (local teaching demo) is accepted with notes and merged with its two-round correction budget exhausted. F3/DEV-010 remains in progress but blocked on the AUTH-014 supplier wait: the 26 November read-only check ([auth-014-supplier-check-2026-11-26.md](auth-014-supplier-check-2026-11-26.md)) confirmed that `postgres:17-alpine` on `linux/amd64` still ships `libssl3`/`libcrypto3` `3.5.9-r0`, leaving the 37 PostgreSQL DEV-010 tests unrun and hosted `skeleton` CI red. Full DEV-011, DEV-012, DEV-013 and later tasks are gated behind DEV-010 and F3 exit. No eligible implementation work remains within current authority.

## Options for the founder

### Option A — Continue waiting for the AUTH-014 supplier update (recommended for strict critical-path discipline)

Hold implementation until an official `postgres:17-alpine` `linux/amd64` rebuild ships `libssl3`/`libcrypto3` `3.5.9-r1` or later, then run one manual read-only check and full qualification review before reopening DEV-010's PostgreSQL suite.

- **Cost:** Zero engineering effort, zero token spend, and zero rework now.
- **Risk:** Unknown wait duration; no new backend or learner-facing capability advances in the meantime. Even after PostgreSQL unblocks, DEV-010 still requires scanner, worker-authority, storage, and Arabic/bilingual fidelity qualification.

### Option B — Authorize one bounded DB-free DEV-012 retrieval and citation preflight slice

Issue a new founder approval (modeled on AUTH-016) for a pure in-memory, synthetic-fixture sub-slice of DEV-012 inside F3: lexical retrieval, live permission/edition/approval filtering, answer-key and private-chunk exclusion, and exact citation resolution over the existing three-subject fixtures (`backend/modules/retrieval/` and `evals/retrieval/`). Full DEV-012 (pgvector/hybrid indexing and F3 exit) stays gated on DEV-010 and DEV-011.

- **Cost:** One engineering day, at most two correction cycles, zero new dependencies, zero paid calls, and independent review before PR.
- **Risk:** Low technical risk (pure domain logic with negative ACL tests), but it does not unblock DEV-010, adds no visible learner UI yet, and must be re-verified when wired to PostgreSQL later.

### Option C — Authorize evaluating an alternative official PostgreSQL base image under the same strict gate

Amend AUTH-014 to permit a bounded, read-only qualification check of an alternative official PostgreSQL 17 image (for example, `postgres:17-bookworm` on `linux/amd64`) under the exact same SBOM, native, core, advisory, KEV, and rights pre-use gate and independent review — without relaxing any threshold, adding exceptions, or building custom images.

- **Cost:** Half to one engineering day for read-only registry inspection, full pre-use scan, pin update if clean, and independent review.
- **Risk:** Medium. The alternative official Debian image may also carry blocking CVEs, which would still leave DEV-010 held after spending the review budget. Even if it passes, DEV-010's remaining scanner/worker/fidelity items still need qualification.

### Option D — Authorize a new bounded learner-facing demo slice (only if UX testing is the priority)

Open a new founder approval beyond AUTH-017 for specific, bounded demo work (for example, resolving the remaining non-blocking review notes such as WOFF2 subsetted fonts, same-question retry, or a second subject) while keeping it isolated from the production app.

- **Cost:** One engineering day, at most two correction cycles, plus independent review.
- **Risk:** Does not advance F3 backend readiness and risks investing further in throwaway mock UI before real APIs and grading exist.

## Recommendation

- Choose **Option A** if you want zero speculative work and strict adherence to the AUTH-014 supplier wait.
- Choose **Option C** if unblocking DEV-010's 37 PostgreSQL tests and greening `skeleton` CI now is the highest priority (accepting the risk that an alternative official image may also fail the gate).
- Choose **Option B** if you want to keep AUTH-014 strictly on wait while making bounded, reusable DB-free F3 progress on scoped retrieval and citation enforcement.

## Decision status

**Decided — Option A selected on 26 November 2026.** Founder responded verbatim: `"go with the recommended"`, confirming **Option A** (continue waiting for the AUTH-014 supplier update on `postgres:17-alpine` `linux/amd64` `libssl3`/`libcrypto3` `3.5.9-r1` or later). No new implementation slice, alternative image evaluation, demo work, supplier polling, or gate change is authorized. Recheck the supplier manually once there is reason to expect an updated amd64 SBOM.
