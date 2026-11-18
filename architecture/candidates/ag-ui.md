# CAND-AGUI-001 — Agent/interface protocol candidate

18 November 2026. Status: integration direction approved by founder U19; exact SDK/activation not adopted or installed. Founder asked whether https://github.com/ag-ui-protocol/ag-ui could help. Requirements touched: R062, R067, R075, R094. This is a new follow-up source, not a retroactive addition to either preserved research pack.

## Observed upstream evidence

Repository revision observed: `3416b86da4b3288e87f827c7f2759a7fa18b5231`. [Pinned repository](https://github.com/ag-ui-protocol/ag-ui/tree/3416b86da4b3288e87f827c7f2759a7fa18b5231), [pinned license](https://github.com/ag-ui-protocol/ag-ui/blob/3416b86da4b3288e87f827c7f2759a7fa18b5231/LICENSE). The repository license is MIT; exact selected SDK, transitive dependencies and any optional frontend packages still require separate review. No commercial/legal/security clearance is inferred.

[Official overview](https://docs.ag-ui.com/introduction) describes an event-based agent-to-interface protocol, typed events, shared state and frontend/backend tool interactions. Those are upstream capabilities/claims, not measured Sebaverse results. The repository includes TypeScript and Python SDKs and an HTTP streaming example. No example, installation script, external agent instruction or paid-model scaffold has been executed here.

## Fit inference and recommendation

Potential fit is the tutor interface boundary: normalize run/message/status/citation events, render reviewed activity cards and reduce custom client/backend wiring. Keep Django/React, durable jobs, scoped source access and deterministic state authority. An adapter could map Sebaverse's validated events into a selected AG-UI subset. The protocol is not a curriculum engine, adaptive learner model, grader, RAG evaluator, guardian verification workflow or cost-control service.

Current Sebaverse text transport is REST commands plus authenticated GET SSE over ASGI, with durable turn IDs and validated blocks. The upstream HTTP example starts a run through a streaming POST. Therefore integration is not assumed drop-in: session cookies, CSRF, reconnect cursors, durable cancellation and replay need explicit compatibility tests. Standard event names alone do not establish persistence or security.

## Required bounded comparison before adoption

At the tutor-interface phase, compare the existing small REST/SSE implementation with an AG-UI adapter on the same synthetic cases. Measure dependency/bundle change, implementation effort, reconnect correctness, cancellation/stale-output rejection and Arabic RTL integration. Do not reopen the stack just to use its scaffold.

- Only validated content blocks may reach a learner. Raw token deltas, hidden reasoning, answer keys and sensitive traces must not be forwarded merely because an upstream event type permits them.
- Client messages, state patches, thread/run IDs, tools and tool results remain untrusted data. The server derives live learner/course/consent/entitlement scope and rejects unknown events and unauthorized mutations.
- Shared UI state is a projection, never the authority for mastery, grading, consent, roles, payments or usage. Frontend tools must not broaden permissions or execute arbitrary generated code.
- Verify same-origin sessions and CSRF, schema limits, ordering/duplication, reconnect without re-running a provider call, revocation during delivery, bounded event sizes, cancellation generations and no unauthorized replay.
- Pin and review exact SDK licenses/security/dependencies before installation. CopilotKit or another renderer is a separate adoption decision; no paid hosted service is required by this proposal.

## Decision and unknowns

Recommendation: shortlist a small protocol adapter experiment, not wholesale repository reuse. Founder subsequently instructed integration under U19. ADR-013 and R105 now assign the bounded adapter to DEV-013. Package locks, runtime gates and current implementation phase remain unchanged. Unknowns: selected SDK version and dependency delta, fit with our split command/SSE contract, actual reconnect guarantees, Arabic UI effort and whether maintenance savings exceed the adapter cost. Runtime recovery under AUTH-006 continues independently.
