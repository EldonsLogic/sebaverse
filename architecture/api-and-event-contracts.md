# API, event and transaction contracts

Selected technical design v1 · U11/U12 · R025/R040/R046/R057/R060/R062/R067/R070/R075/R078. Specification only; no endpoint implemented.

## Common protocol

Same-origin HTTPS, Django server sessions in Secure/HttpOnly cookies, CSRF protection on mutations including login, Origin checks and no permissive credentialed CORS. Browser localStorage holds no bearer credential or child transcript. Staff MFA and object policies are required. Internal UUIDs are identifiers, not authorization. Version API under /api/v1 and serialize contracts in OpenAPI/JSON Schema during implementation; generate TypeScript types rather than maintain competing definitions.

Every mutation accepts an idempotency key scoped to actor + command + body hash, expected aggregate version and correlation ID. Reusing a key with a different body is a conflict. Errors have stable code, localized safe message, field errors where relevant, retryability and correlation ID; no private filename/stack trace leaked. Cursor pagination and quotas are bounded. 401 unauthenticated, 403 denied, 404 concealed missing/out-of-scope resource, 409 version/key conflict, 422 invalid domain input, 429 quota/rate limit; API contract fixes exact use case at implementation.

## Command surface

| Surface | Commands / functions | Server checks |
|---|---|---|
| /account, /relationships, /consents | Sign in/out, verified link workflow, record/revoke scoped consent | Actor verification, relationship authority, purpose and policy version |
| /courses, /enrollments | List permitted curricula, enroll/resume course | Current course visibility, grant, consent, curriculum availability |
| /uploads | Initiate, finalize checksum, status, cancel, delete request | Bytes/pages/types, uploader scope, rights claim, quota reservation |
| /materials, /sources/{id} | Inspect extraction, confirm private-ready, resolve citation | Material/source version and live audience rights; answer keys excluded |
| /admin/curricula | Review mappings/items/profile, publish/withdraw edition | Staff capability, rights/content approval, immutable release manifest |
| /sessions | Create/resume with curriculum/profile version | Subject capabilities and access; client cannot override policy |
| /sessions/{id}/turns | Start turn, cancel, subscribe to events | Idempotency, expected state/turn, spend reserve, ownership |
| /attempts | Submit answer, request hint, report/appeal grade | Server-owned item/rubric/exposure state; browser supplies no trusted score |
| /progress, /reviews | Fetch evidence projection, due items, summarize | Learner/guardian scope; unknown and assistance remain distinct |
| /voice | Authorize bounded upload/transcription/TTS or cancel | Explicit mic action, privacy eligibility, media quotas, transient assets |
| /entitlements, /payments/webhook | Read access, staff grant, reconcile signed gateway event | No client paid flag, provider signature/dedup; real collection gated |
| /privacy | Export/delete request and status | Verified requester, lawful scope, active revocation and purge lineage |
| /notifications | Read/update preferences, future outbox send | Recipient authority, purpose/opt-out, approved channel and send workflow |

## Tutor event stream

POST start returns turn_id and current version; worker executes from durable job. Authenticated GET events uses SSE with event sequence cursor, not credentials in query strings. Event envelope: schema_version, event_id, turn_id, session_version, sequence, type, occurred_at, safe payload. Types: accepted, status, validated_content_block, citation, usage_status, completed, cancelled, failed. No raw provider reasoning, hidden prompt, answer key or internal safety classifier text.

Persist bounded validated blocks/checkpoints for reconnect; raw token deltas are not a permanent append-only transcript. Authorize before subscription and recheck access before each batch and after revocation notification; event IDs do not convey permission. Send only actor-scoped events, heartbeat under proxy timeout and stop denied/cancelled streams. Bounded DB polling is baseline; tune interval/retention with measured load. Native EventSource auto reconnect does not restart generation. Text reconnect replays eligible stored events then status; media replay requires separate consent/asset eligibility.

## Transactions, jobs and reconciliation

Start turn: short transaction validates state and scope, reserves maximum estimated units/spend, creates turn/job/outbox, commits. Never hold DB transaction open during network inference. Unique expected-active-turn constraint or explicit serialized session version prevents competing actions. Lease token/generation fences reject stale worker results; heartbeats extend leases only within job limit.

A provider call can succeed before a worker crashes. Record call attempt ID/provider receipt where possible, mark unknown billing and reconcile; do not promise external exactly-once billing. Unknown billable attempts hold a bounded outstanding reservation and block unbounded retries. Grading/evidence effects are once per accepted event using unique keys. Outbox delivery and job execution are at least once, retries capped with jitter/dead-letter review. Recovery never reuses an unverified paid flag or duplicates an independent success.

Cancel: mark durable cancellation generation, cancel upstream if supported, stop media/obsolete work, reconcile already billed units. Completion must compare expected version and cancellation generation; late output cannot score a new item or resume an old turn. Consent/access revocation increments scope generation and invalidates pending jobs/cache; all consumers recheck live scope before effects.

Deletion: deny access immediately, schedule purge of originals/derived chunks/embeddings/cache/media/transcripts/provider-side deletable assets, record minimal purge evidence. Restored backups replay deletion tombstones before service access. Retention and deletion obligations are reviewed separately; append-only learning history does not override legitimate deletion/minimization.
