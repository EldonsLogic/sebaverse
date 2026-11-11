# ADR-006 — Versioned content with scoped retrieval

Status: **Selected technical baseline v1 under U11**, 11 November 2026. Author: project engineering agent. Supersedes initial proposed draft of 10 November (preserved in Git). Technical selection is not test validation, procurement approval or blanket G3 sign-off.

## Context and evidence

Founder U1/U2/U11/U12, preserved audits A01–A13 and global G04–G10; relevant limited primary checks E22–E32 in sources/architecture-primary-checks.md. Requirements: R035 R036 R037 R038 R039 R040 R041 R042 R044 R045 R046 R099.

## Decision

Shared provenance/version pipeline for built-in/private content, immutable collection/profile/edition manifests, PostgreSQL lexical + pgvector hybrid candidate ranking from authorized set. Citation resolution rechecks live rights.

## Alternatives considered

Shared upload corpus; unversioned chat; postfilter-only permissions; vector/graph service first.

## Consequences

Supports multiple subjects without school-specific core. Exact search first avoids assuming ANN plus filters preserves recall.

## Reversal / validation trigger

Change index technology after measured scoped recall/latency/cost need; never relax live authorization to improve metrics.

## Execution status

No product implemented or benchmark performed. Refer to architecture/technical-baseline.md and execution/subject-independent-poc.md. Founder/external audit feedback and applicable execution/rights/security/budget decisions remain required before the corresponding next phase. Do not label this ADR “founder approved” based solely on agent authorship.
