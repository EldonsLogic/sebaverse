# ADR-001 — Owned modular monolith

Status: **Selected technical baseline v1 under U11**, 11 November 2026. Author: project engineering agent. Supersedes initial proposed draft of 10 November (preserved in Git). Technical selection is not test validation, procurement approval or blanket G3 sign-off.

## Context and evidence

Founder U1/U2/U11/U12, preserved audits A01–A13 and global G04–G10; relevant limited primary checks E22–E32 in sources/architecture-primary-checks.md. Requirements: R006 R060 R067 R075 R077.

## Decision

One owned Django domain/repository with typed modules and separately isolated parsing/scanning processes. No whole tutoring/LMS application foundation.

## Alternatives considered

Whole DeepTutor/LearnHouse; microservices.

## Consequences

Single authority for consent, evidence and entitlements; no distributed business transaction burden. Module boundaries require tests.

## Reversal / validation trigger

Reconsider LMS boundary only if validated institutional workflows outweigh integration/rights cost.

## Execution status

No product implemented or benchmark performed. Refer to architecture/technical-baseline.md and execution/subject-independent-poc.md. Founder/external audit feedback and applicable execution/rights/security/budget decisions remain required before the corresponding next phase. Do not label this ADR “founder approved” based solely on agent authorship.
