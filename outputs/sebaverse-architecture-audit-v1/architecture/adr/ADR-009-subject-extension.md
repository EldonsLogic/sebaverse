# ADR-009 — Subject-independent extension

Status: Selected technical baseline v1 under U11/U12, 11 November 2026; engineering decision for audit, not founder blanket approval.

## Context

Requirements: R036 R075 R094 R099. See technical-baseline.md, associated subject/API/deployment contracts and dated source checks E22–E32.

## Decision

Curriculum editions, collection manifests, subject profiles, graders and representation adapters are versioned extensions of a common core. No first textbook/subject dependency. Adding supported subjects uses content/config; new specialist capability needs reviewed adapter, not arbitrary uploaded code.

## Alternatives and consequence

Hard-coded German/math schemas; unvalidated dynamic plugins. Selected design keeps ownership and scope testable but requires explicit integration/evaluation work. No runtime results claimed.

## Reversal and execution

Change only through a dated ADR amendment with measured failure/benefit and migration/rights review. Implementation/deployment and real-data permissions remain separate.
