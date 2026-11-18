# ADR-010 — Web client and transport

Status: Selected technical baseline v1 under U11/U12, 11 November 2026; engineering decision for audit, not founder blanket approval.

## Context

Requirements: R054 R055 R060 R075 R097. See technical-baseline.md, associated subject/API/deployment contracts and dated source checks E22–E32.

## Decision

React/TypeScript/Vite static client with React Router/TanStack Query, same-origin Django sessions/CSRF, REST commands and native ASGI SSE. Durable turns/jobs, validated block replay, cancellation generation and scope rechecks.

## Alternatives and consequence

Separate Node backend; WebSocket for ordinary text; localStorage bearer tokens. Selected design keeps ownership and scope testable but requires explicit integration/evaluation work. No runtime results claimed.

## Reversal and execution

Change only through a dated ADR amendment with measured failure/benefit and migration/rights review. Implementation/deployment and real-data permissions remain separate.

## U19 integration direction — 18 November 2026

[ADR-013](ADR-013-ag-ui-integration.md) adds AG-UI protocol compatibility at the existing tutor/interface boundary. Django/React and durable REST/SSE remain selected; no measured performance benefit or replacement transport is claimed. Execution and exact dependency adoption follow the integration contract and DEV-013 gates.
