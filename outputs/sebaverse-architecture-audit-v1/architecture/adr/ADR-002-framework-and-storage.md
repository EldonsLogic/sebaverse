# ADR-002 — Framework and persistence

Status: **Selected technical baseline v1 under U11**, 11 November 2026. Author: project engineering agent. Supersedes initial proposed draft of 10 November (preserved in Git). Technical selection is not test validation, procurement approval or blanket G3 sign-off.

## Context and evidence

Founder U1/U2/U11/U12, preserved audits A01–A13 and global G04–G10; relevant limited primary checks E22–E32 in sources/architecture-primary-checks.md. Requirements: R054 R075 R085 R094.

## Decision

Python 3.12, Django 5.2 LTS, DRF, PostgreSQL 17 and private S3-compatible storage. React/TypeScript/Vite client under same origin; transactional services remain server-side.

## Alternatives considered

FastAPI/custom admin; TypeScript-only backend; Django templates-only; separate vector service.

## Consequences

Established admin/auth/review workflow plus typed interactive UI. Accept JS build overhead, keep one runtime backend; no separate Node backend. Exact patched dependency locks follow install-readiness review.

## Reversal / validation trigger

Change framework only on demonstrated maintainability/compatibility/runtime failure; document migration before code spread.

## Execution status

No product implemented or benchmark performed. Refer to architecture/technical-baseline.md and execution/subject-independent-poc.md. Founder/external audit feedback and applicable execution/rights/security/budget decisions remain required before the corresponding next phase. Do not label this ADR “founder approved” based solely on agent authorship.
