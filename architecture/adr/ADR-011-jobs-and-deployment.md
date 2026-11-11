# ADR-011 — Jobs and process topology

Status: Selected technical baseline v1 under U11/U12, 11 November 2026; engineering decision for audit, not founder blanket approval.

## Context

Requirements: R040 R060 R070 R078 R080. See technical-baseline.md, associated subject/API/deployment contracts and dated source checks E22–E32.

## Decision

PostgreSQL jobs/outbox with leased/fenced workers, short transactions and idempotent effects. Separate scanner/parser credentials. OCI deployment and GitHub Actions design; no initial Redis/Celery/Kubernetes.

## Alternatives and consequence

In-request parsing; distributed broker from first release; worker trusted with all secrets. Selected design keeps ownership and scope testable but requires explicit integration/evaluation work. No runtime results claimed.

## Reversal and execution

Change only through a dated ADR amendment with measured failure/benefit and migration/rights review. Implementation/deployment and real-data permissions remain separate.
