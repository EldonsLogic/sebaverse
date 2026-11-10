# ADR-002 — Framework and persistence

Status: proposed, not approved. Date: 2026-11-10.

## Context and evidence

Sources: A06;A12;C1. Founder requires affordability, preserved scope, provider independence and controlled implementation. Research findings remain bounded by their stated audit limits.

## Proposed decision

Django/Postgres is proposed baseline, private object storage; compare thin FastAPI alternative; pgvector conditional.

## Alternatives

FastAPI/custom admin; TypeScript stack; external vector/graph databases.

## Rationale and consequences

Auth/admin/content review and solo operations matter; framework decision stays reversible before code. This adds owned domain and review work; it does not eliminate educator/security/operations cost.

## Reversal / validation trigger

Revisit if PoC demonstrates unacceptable streaming/runtime or maintainability cost.

## Approval

Pending G3. Record approver, date, reviewed commit and conditions; no approval inferred from this draft.
