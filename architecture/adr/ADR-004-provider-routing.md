# ADR-004 — Provider eligibility and routing

Status: **Selected technical baseline v1 under U11**, 11 November 2026. Author: project engineering agent. Supersedes initial proposed draft of 10 November (preserved in Git). Technical selection is not test validation, procurement approval or blanket G3 sign-off.

## Context and evidence

Founder U1/U2/U11/U12, preserved audits A01–A13 and global G04–G10; relevant limited primary checks E22–E32 in sources/architecture-primary-checks.md. Requirements: R062 R063 R064 R065 R066 R068 R069 R070.

## Decision

Owned capability adapters with live eligibility, safety/task quality before cost; one qualified default and fallback per task. Jev/classifiers shadow-only until benchmarked. No mandatory proxy framework.

## Alternatives considered

Vendor SDK throughout domain; cost-only routing; local GPUs first.

## Consequences

Portable usage/cancel contracts without hiding provider privacy/billing semantics. Endpoint/model selection is an eval/terms release decision.

## Reversal / validation trigger

Promote/change model route only with versioned matched evaluation, terms/data eligibility and cost receipts.

## Execution status

No product implemented or benchmark performed. Refer to architecture/technical-baseline.md and execution/subject-independent-poc.md. Founder/external audit feedback and applicable execution/rights/security/budget decisions remain required before the corresponding next phase. Do not label this ADR “founder approved” based solely on agent authorship.
