# AG-UI integration contract — R105

18 November 2026. Founder instruction U19 approves integration as it fits. Engineering direction: a small protocol adapter at the tutor interface boundary, preserving Django/DRF, React/TypeScript/Vite and server-owned state. This document defines work for DEV-013; product activation has not begun, and F3 remains held.

## Pinned evidence and dependencies

Upstream reference: ag-ui-protocol/ag-ui commit `3416b86da4b3288e87f827c7f2759a7fa18b5231`. See [assessment](candidates/ag-ui.md) and [ADR-013](adr/ADR-013-ag-ui-integration.md). The pinned manifests declare Python ag-ui-protocol 1.0.0 (MIT, pydantic >=2.11.2), @ag-ui/core 1.0.5 (MIT, Zod peer) and @ag-ui/client 1.0.5 (MIT, additional reactive/JSON-patch/UUID dependencies). These are source-manifest observations, not proof that an identical published artifact is audited or installed. Do not copy workspace:* into a lockfile.

Prefer the smallest reviewed upstream types/schema package and a first-party authenticated transport adapter. Existing Django serializers may encode conformant events without introducing Pydantic just for encoding. Compare the full @ag-ui/client before adopting its transport/state machinery. SDK, lock, notices, provenance, vulnerability closure and bundle measurements are required before installation/reuse. CopilotKit, Next.js, an agent framework and paid hosted services are not part of this selected scope.

## Event mapping

| Sebaverse event | AG-UI envelope direction | Authority and payload restriction |
| --- | --- | --- |
| Durable turn accepted | RunStarted | Server-derived run/thread mapping; never trust client scope IDs |
| Safe processing status | StepStarted / StepFinished | Allowlisted public status only; no hidden reasoning or private trace |
| Validated teaching block | TextMessageStart / TextMessageContent / TextMessageEnd | Emit only after safety, grounding and answer-exposure validation; source locators retained |
| Authorized citation / activity card | Custom or reviewed activity event | Versioned first-party typed payload; unknown schemas rejected |
| Current learner-safe UI projection | StateSnapshot | Minimal authorized projection; no rubric key, raw consent evidence or private transcript |
| Validated presentation changes | StateDelta, only if needed | Allowlisted UI paths only; cannot update learning/business authority |
| Turn complete / safe failure | RunFinished / RunError | Completion requires current fence/scope; error message contains no private data |
| Cancellation/reconnect | Existing server commands and durable event cursor | Transport abort alone does not cancel a provider or settle billing |

The exact protocol 1.0 JSON Schema and event fields must be pinned/checked in the implementation task. The mapping above is a design, not an assertion that a current SDK provides Sebaverse's durability or cancellation semantics.

## Transport and state boundaries

Keep REST commands plus authenticated ASGI SSE with durable turn IDs and cursor replay. The upstream sample's streaming POST run differs from this split contract; use a compatible adapter rather than replacing durability with a convenience client. Preserve same-origin session cookies, deliberate CSRF bootstrap for writes, expected versions and idempotency keys. A reconnect replays eligible validated events; it must not rerun generation or accept a client-supplied history as authoritative.

Client messages, tool results, state patches, run IDs and metadata are untrusted. Never accept role, consent, paid, mastery, grade, scope, model budget or provider eligibility from them. Frontend tools are absent by default; any later action needs a typed allowlist and server authorization. No arbitrary generated HTML, JavaScript, network call or tool execution. Review SDK logging as well: errors must not print raw messages, shared state, patches or child content to the browser console or server/vendor traces. Never forward rawEvent, reasoning events, model token streams, answer keys or unrestricted state snapshots to children.

Cancellation and revocation use existing durable jobs, authorization generations and live server checks before each event batch. A late output/receipt can reconcile legitimate usage but cannot reopen a cancelled activity. The wire protocol must not become a second source of truth for learner progress or accounting.

## DEV-013 implementation and tests

1. Review exact published SDK/schema artifacts and minimal dependency delta, notices and security before installing. Record whether core/schema only or client is selected, with measured bundle/runtime implications; no invented savings.
2. Add a versioned allowlisted encoder and client decoder with generated/shared types. Use synthetic three-subject tutor events first. Validate incoming and outgoing bounds, unknown types and invalid event order.
3. Implement the same-origin authenticated adapter to the durable REST/SSE surface. Test CSRF, anonymous/other-learner access, stolen run IDs, revoked consent, changed edition, duplicate/out-of-order frames, cursor gaps and safe resnapshot.
4. Test cancellation, disconnect/reconnect and process restart: no repeated paid dispatch, stale teaching output, double usage finalization or authority mutation. Hold content until validation, even if that costs first-token latency.
5. Verify Arabic RTL at 360/390/768/1440, keyboard/focus, accessibility, loading/error/offline/partial states and the existing asset budget. Inspect screenshots for each changed screen.
6. Compare with the planned small native event adapter on the same cases. Record benefits, failures, dependency size and maintenance cost. Activate only after relevant gates and independent review; keep a reversible server-side transport switch.

## Limits

No package has been installed and no AG-UI product feature is implemented at this checkpoint. This is an approved integration direction attached to DEV-013, with traceable tests and prerequisites, not a claim that the upstream repository supplies pedagogy, consent, rights, model routing or a complete Sebaverse interface.


Independent planning review, 18 November: /root/independent_reviewer found no concrete planning blocker. Foundation/economics/artifact validation and 152 helper tests passed. This verifies the plan/traceability only; package compatibility and protocol/runtime tests have not run.
