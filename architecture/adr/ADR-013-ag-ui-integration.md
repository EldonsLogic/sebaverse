# ADR-013 — AG-UI at the tutor/interface boundary

18 November 2026. Status: accepted integration direction under founder U19; exact package adoption, comparison and activation are gated.

## Context

R105, R062, R067 and R075. The founder explicitly requested AG-UI integration after its role was assessed. [Pinned assessment](../candidates/ag-ui.md) records upstream claims, source revision, MIT repository license and unresolved SDK/transport questions.

## Decision

Implement a minimal schema-conformant AG-UI adapter during DEV-013, retaining the existing Django/React architecture and durable REST/SSE semantics. Use only reviewed allowlisted events and validated learner-safe projections. SDK/state/tool conveniences never own permissions, grading, mastery, consent, payments or usage. See [integration contract](../ag-ui-integration.md).

## Consequences and validation

This standardizes a candidate wire boundary while adding compatibility/dependency work. Maintenance or performance savings are hypotheses until the bounded comparison runs. It does not approve wholesale repository reuse, CopilotKit/Next.js, Pydantic installation, paid services or upstream scaffolds. Exact release/security/notice closure comes before reuse. Existing phase gates, real-data restrictions and independent review remain unchanged.

## Rollback

Keep the server's durable event model and transport adapter separable. If the evaluated SDK is unsuitable, preserve required protocol conformance through a smaller reviewed adapter, recording the reason. No reversal of deterministic authority or safety requirements is permitted.
