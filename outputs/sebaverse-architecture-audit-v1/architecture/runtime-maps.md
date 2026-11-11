# Detailed runtime and lifecycle maps

U11/U12 · Selected design, not implementation. [System topology](technical-baseline.md) and [entity map](system-and-data-model.md) complement these editable Mermaid diagrams.

## Curriculum ingestion and publication

![Curriculum ingestion lifecycle](ingestion-map.svg)

```mermaid
flowchart TD
 A[Actor + learner + scope + quota + rights purpose] --> B[Allocate upload and quarantine object]
 B --> C[Verify bytes/type/hash/limits]
 C --> D[Isolated malware scanner]
 D -->|fail/unavailable| X[Hold or reject: no parser bypass]
 D -->|accepted| E[Isolated Docling parse]
 E --> F[Broker validates scoped extraction manifest]
 F --> G[Quality/mapping review; uncertain regions flagged]
 G --> P{Publication audience}
 P -->|private| H[Permitted private-ready source version]
 P -->|built-in| I[Rights + educator publication review]
 I --> J[Shared approved edition]
 H --> K[Versioned collection + lexical/dense indexes]
 J --> K
 K --> L[Authorized retrieval and source inspection]
 L --> M[Replace / withdraw / revoke / delete]
 M --> N[Invalidate access, jobs, caches and derived indexes]
```

## Tutoring and assessment state machine

![Tutor and evidence lifecycle](tutor-learning-map.svg)

```mermaid
stateDiagram-v2
 [*] --> access_check
 access_check --> blocked: scope/consent/grant/budget fails
 access_check --> diagnose: eligible new session
 access_check --> select: resume valid checkpoint
 diagnose --> select: validated diagnostic evidence
 select --> explain
 select --> practice
 select --> schedule
 explain --> guided
 guided --> prerequisite
 prerequisite --> guided
 guided --> practice: new independent item
 practice --> grade: answer submitted
 practice --> guided: hint requested / independence ends
 grade --> review_pending: uncertain or disputed
 grade --> reflect: validated result appended once
 review_pending --> reflect: reviewed correction and replay
 reflect --> select
 schedule --> done
 done --> [*]
 explain --> safety_pause: safety policy event
 guided --> safety_pause
 practice --> safety_pause
 safety_pause --> access_check: authorized resume
 explain --> paused: cancel / outage
 guided --> paused
 practice --> paused
 paused --> access_check
 blocked --> [*]
```

Any state can be cancelled/denied on live revocation; diagram omits repeated arrows for legibility. Cursor/version/cancellation generation fences reject late output. No autonomous model transition or write to learner projections.

## Request, model and evidence sequence

Browser command → Django authorization and atomic spend reservation → durable worker lease → scoped retrieval → eligible provider call → validated content blocks and usage receipts → authorized SSE replay. Independent answers enter the separate reviewed grading/evidence path. Cancellation or revocation fences all later effects.

```mermaid
sequenceDiagram
 participant UI as Browser
 participant API as Django services
 participant DB as Postgres/outbox
 participant W as Worker
 participant R as Scoped retrieval
 participant M as Eligible model adapter
 UI->>API: start turn (expected version, idempotency)
 API->>API: live authorization + action constraints
 API->>DB: reserve spend + turn + job atomically
 API-->>UI: turn ID / subscription cursor
 W->>DB: claim job lease + fence
 W->>R: retrieve from allowed pinned sources
 R-->>W: chunks + exact locators
 W->>M: bounded request / call attempt ID
 M-->>W: content proposals + actual usage
 W->>W: validate structured content/citations/safety
 W->>DB: accepted blocks / checkpoint / receipts
 UI->>API: authorized SSE subscription
 API->>DB: read eligible validated blocks
 API-->>UI: replay/status/validated blocks
 UI->>API: independent attempt or hint request
 API->>DB: attempt + assistance record + job
 W->>W: reviewed grader validation
 W->>DB: evidence + projection transaction
 Note over API,DB: Any revocation/cancel invalidates later effects
```

## Release and controlled improvement

Validated evidence updates the learner projection and next permitted activity. Separately, minimized failure categories go through educator/engineering triage, frozen evaluation and reviewed versioned release with rollback. Optional model training uses separately authorized curated data and the same release gate, never automatic child-chat ingestion.

```mermaid
flowchart LR
 E[Validated learning events] --> P[Deterministic learner projection]
 P --> A[Permitted next activity]
 E --> F[Minimized failure categories]
 F --> H[Educator/engineering triage]
 H --> T[Frozen offline eval + safety/rights tests]
 T --> V[Reviewed versioned release]
 V --> C[Controlled rollout / rollback]
 C --> A
 D[Separately authorized curated training data] --> O[Optional offline model experiment]
 O --> T
```

No raw identifiable child conversation automatically enters training or evaluation fixtures. A positive engagement signal is not evidence of mastery or efficacy.
