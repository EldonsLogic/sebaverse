# DeepTutor source audit

Audit date: 2026-11-10. Source pin: `60fb3bdfddb30b7740c7ce3bd9b28d908f2af6db`, upstream default `main`. Isolated sparse checkout: `work/repos/DeepTutor-sparse`. References below are repository-relative at this SHA; [pinned source](https://github.com/HKUDS/DeepTutor/tree/60fb3bdfddb30b7740c7ce3bd9b28d908f2af6db). Root AGENTS.md read as project context, not executed. No upstream source modifications.

## Decision

Use as a reference implementation initially; selectively extract small Apache-2.0 modules only after dependency and provenance review. Do not deploy the complete general-purpose agent workspace as the commercial child-facing backend. Its reusable functionality is considerably broader than early DeepTutor versions: memory, mastery, guardian relationships, durable sessions and speech are implemented. Their existence does not establish educational validity, tenant isolation or production suitability for minors.

## Architecture and contracts

`deeptutor/app/service.py:21` defines `TurnApplicationService`; `start_turn` at 113, `subscribe_turn` at 248, `cancel_turn` at 398 and `submit_user_input` at 602 expose durable turn control. `deeptutor/app/engine.py`, `runtime/orchestrator.py` and tool/capability registries implement the turn engine and orchestration. CLI, WebSocket and SDK share the application layer. Integration should wrap this service behind a constrained adapter, rather than expose arbitrary upstream tools to children.

Sessions use `services/session/protocol.py` with SQLite and PocketBase stores (`sqlite_store.py`, `pocketbase_store.py`), plus turn lifecycle/executor/context assembly modules. This is not the proposed platform's PostgreSQL learner-state schema. Integration requires authoritative user/course/entitlement mapping and idempotent learning-event export.

`pyproject.toml:16` requires Python >=3.11,<3.15; core dependencies include OpenAI SDK, MCP, Pydantic 2, aiosqlite and HTTP clients. Optional equal-version distributions provide server, knowledge, providers, questions, memory and mastery. This modular installation helps, but the full workspace brings many unrelated capabilities. Numerous lower-bound dependency ranges require a separately resolved deployment lock and SBOM. Apache-2.0 is declared in pyproject and root LICENSE; THIRD_PARTY_NOTICES.md must accompany extraction review.

## Verified capability classification

No capability is classified production-ready for this particular child-facing SaaS without deployment, security and pedagogical validation.

| Capability | Classification | Source and integration implication |
|---|---|---|
| Tutor orchestration | Reusable with modification | `app/service.py`, `app/engine.py`, `runtime/orchestrator.py`; constrain tools and budget |
| Interaction/session persistence | Reusable with modification | `services/session/protocol.py`, `sqlite_store.py`, `turns/executor.py`; adapt identities and events |
| Persistent learner memory | Reusable with modification | `services/memory/store.py:69` MemoryStore, trace/recall/consolidator modules; narrative memory is distinct from assessed mastery |
| Retrieval | Reusable with modification | `services/rag/smart_retriever.py`, kb_paths, embedding binding/signature and `services/rag/eval/`; benchmark Arabic grounding |
| Question generation | Reusable with modification | questions optional module and practice storage; require curriculum-tagged reviewed items and validated grading |
| Personalized practice | Prototype/experimental for target use | `services/practice/storage.py`, mastery capability; outcome validity unproven |
| Learning path | Reusable with modification | `api/routers/mastery_path.py`, `capabilities/mastery/pipeline.py`; map to versioned curriculum prerequisites |
| Mastery estimation | Reusable with modification | `learning/mastery.py:24` compute_mastery; transparent heuristic, not BKT or deep KT |
| Misconception identification | Claimed but not verified as calibrated diagnosis | Memory/mastery context can retain observations; no validated Egyptian misconception taxonomy established |
| Adaptive instruction | Prototype/experimental | `capabilities/mastery/loop.py`, tools/memory/choices; no controlled learning-gain evidence established |
| Feedback loops | Reusable with modification | memory consolidation and mastery updates; not a safe automatic model-training system |
| Multi-agent workflows | Reusable with modification | subagent services and orchestrator; defer for latency, safety and cost |
| Voice | Reusable with modification | `api/routers/voice.py:40,70` POST tts/stt; `services/voice/adapters/` OpenAI-compatible, Gemini, DashScope etc. No Egyptian dialect quality or full duplex latency verified |
| Provider abstraction | Reusable with modification | services/providers ecosystem and voice adapters; verify each provider's data handling separately |
| Evaluation/observability | Reusable with modification | `services/rag/eval/`, `services/memory/evaluation.py`, session usage statistics and recovery; learning outcomes and billing ledger remain custom |

## Mastery algorithm: concrete finding

`learning/mastery.py:17–36` uses five most recent outcomes with weights (0.5, 0.7, 0.85, 0.95, 1.0), bounds partial credit to 0..1 and caps one/two observations at 0.5/0.8. Empty history returns zero. Three correct attempts can return 1.0. It is explainable and cheap, but conflates missing evidence with low mastery and lacks item difficulty, forgetting, uncertainty intervals and independently calibrated skill evidence. Reuse its replaceable-function pattern; define product semantics before adopting its thresholds.

## Security findings and limits

`services/auth.py:85,92` implements bcrypt password operations; token creation/decoding is at 260/286. Multi-user identity and learner profiles exist; `multi_user/guardians.py:95,161,203` implements authorization, revocation and access checks. This disproves a blanket claim that guardian support is missing. It does not verify real-world guardian identity or legally adequate consent.

Voice is documented in `api/routers/voice.py:1–6` as shared infrastructure available to authenticated users without per-user LLM grants. Add server-side subscription checks and per-student voice budgets. STT reads the whole upload at line 75 before checking its 25MB limit: enforce request-body and stream limits at ingress to avoid memory pressure. TTS text has minimum length but no maximum in TTSRequest; cap synthesis input and reserve spend before dispatch. These are source-observed hardening needs, not a proven remotely exploitable vulnerability in a configured deployment.

The agent workspace includes execution, external fetching, MCP and partner integrations. Disable them by default in the child-facing surface; retrieval documents must never grant tool authority. Audit every route's organization/student scope and every storage path before production. Separate arbitrary code/document processing from credentials and learner records. No penetration test, comprehensive authorization review or compliance certification was performed.

## Tests, delivery and maintenance

Tests cover many domains (agents, api, app, architecture, capabilities etc.). `.github/workflows/tests.yml`, `memory-evaluation.yml`, `modules.yml`, docker/pypi release workflows demonstrate CI infrastructure; their existence is not evidence that all checks passed at this pin. Dockerfile and multiple compose variants exist. No full dependency install, Docker launch, paid inference or production load test was performed.

Reviewed dependency-free mastery smoke passed five assertions under available Python 3.11: empty history, one/two/three correct outcomes and five incorrect outcomes. An initial invocation with older host python3 failed on zip(strict=True); selecting the supported interpreter resolved this environment mismatch. No full unit-suite pass is claimed. Exact command/results: work/deeptutor-test-results.md.

Current upstream web README advertises v1.7.2 (2026-11-06), indicating recent releases; public GitHub listing showed substantial open issues/PRs, but exhaustive triage and historical maintainer concentration were not established. Fast evolution is an upgrade burden. Freeze the SHA, avoid a broad fork, record copied provenance, and test any future upstream update against Arabic safety, grounding, isolation and budget regression fixtures.

## Additional source inspection and boundaries

`api/routers/question.py:33` exposes the deferred `mimic_exam_questions(*args, **kwargs)` seam into `tools.question.mimic_exam_questions`. The `/mimic` WebSocket accepts paper-generation requests. `_mimic_output_dir` deliberately resolves get_path_service per call (not module import) so generated papers follow the authenticated user context. This shows intentional scoping work, but every websocket's authentication and context propagation still requires adversarial testing. Generation from uploaded exams creates copyright and source-injection review requirements. No quality claim follows merely from having generation code.

`api/routers/practice.py` imports `check_answer`, `Rating`, `day_bounds`, `PracticeStore` and `ReviewConflict`; its Pydantic contracts include PracticeSummary (due, overdue, timezone), PracticeQuestion and daily/source analytics. Existing practice is richer than a quiz generator: it has scheduling, answer checking and review storage. Preserve its distinction between assessed correctness and scheduling rating. Do not interpret due-card counts as learning efficacy. A product integration would export immutable scored-attempt events linked to curriculum version, concept and item revision, rather than silently mirror two independent mastery databases.

`services/llm/provider_registry.py`, `provider_factory.py`, `factory.py`, `types.py`, `traffic_control.py`, `request_cache.py` and `telemetry.py` provide relevant provider/routing/cache/instrumentation seams. Their presence makes the implementation worth studying, but these modules have not undergone an end-to-end provider compatibility or cost-accounting audit. A provider adapter must normalize retries, timeouts, usage and cancellation and preserve model/prompt versions. Upstream request telemetry is not a subscription billing ledger.

Guardian implementation at `multi_user/guardians.py:95–136` validates account presets, rejects self-guardianship, duplicate active relationships and reverse guardian cycles, filters permissions against an allowlist and records grant/revocation metadata. `guardian_can_access:203–223` rechecks current identities and requires an active relationship and matching permission. This is actual authorization plumbing, not proof of verified guardianship or consent. Inspect route caller authority before adopting these functions.

`services/memory/store.py:69–110` separates L1 trace events from L2/L3 document reads and manual editing. Per-path asyncio write locks serialize writes inside one process; they do not themselves establish transactional multi-process correctness. Learner memory is persisted document content, rather than a normalized psychometric state with calibrated uncertainty. An authoritative commercial schema needs explicit organization/student/content-version keys, consent scope, retention timestamps and event provenance even when using upstream memory summaries.

Background turn execution includes asyncio.create_task in `services/session/turns/executor.py:403` and a durable turn runtime. It should not be assumed equivalent to a distributed queue with global quotas and worker isolation. Validate restart recovery and concurrent updates under the intended process layout. A simple custom database outbox plus worker can handle ingestion, notifications and evaluation independently from conversational turn streaming.

Dockerfile pins frontend/runtime Node image tags to `22.23.4-slim` (lines 23/59), with Python `3.11-slim` base/production stages (64/106). These are mutable tags, not immutable digests. Reviewed tests workflow uses `actions/checkout@v4` and `actions/setup-node@v4`, likewise tag references rather than full action SHAs. Production supply-chain work should pin images/actions and resolve dependency locks. A follow-up `git show` inspection of pinned `web/package.json` confirms Next `^16.2.3`, React/React DOM `^19.0.0`, Tailwind `^3.4.17`, TypeScript `^5`, Vitest `^4.1.11`, KaTeX `0.16.27` and Playwright `^1.53.2`; these are declared ranges, not a verified installed resolution. The manifest defines contract generation/checks, architecture dependency checks, type checking, node/unit/E2E tests and UI/performance audits. No frontend build or test suite was run. CI includes scheduled, push and PR triggers and cancellation of superseded runs. No CI success assertion is made.

The source-level scope verifies the specific files above; it does not cover every endpoint, frontend, transitive dependency, migration or dynamic tenancy path. The safe extraction target is a small reviewed pure function or adapter pattern. A broad fork entails configuration, storage, plugin, frontend and release coupling far beyond the tutoring workflow.

Pinned code: [deeptutor/app/service.py](https://github.com/HKUDS/DeepTutor/blob/60fb3bdfddb30b7740c7ce3bd9b28d908f2af6db/deeptutor/app/service.py).

Pinned code: [deeptutor/learning/mastery.py](https://github.com/HKUDS/DeepTutor/blob/60fb3bdfddb30b7740c7ce3bd9b28d908f2af6db/deeptutor/learning/mastery.py).

Pinned code: [deeptutor/services/auth.py](https://github.com/HKUDS/DeepTutor/blob/60fb3bdfddb30b7740c7ce3bd9b28d908f2af6db/deeptutor/services/auth.py).

Pinned code: [deeptutor/api/routers/voice.py](https://github.com/HKUDS/DeepTutor/blob/60fb3bdfddb30b7740c7ce3bd9b28d908f2af6db/deeptutor/api/routers/voice.py).

## Additional schema and retrieval evidence

Pinned [server requirements](https://github.com/HKUDS/DeepTutor/blob/60fb3bdfddb30b7740c7ce3bd9b28d908f2af6db/requirements/modules/server.txt#L3) declare FastAPI >=0.100.0, Uvicorn >=0.24.0, PocketBase >=0.12.0 and Redis >=5,<7. These lower bounds are not installed versions; resolve and scan a minimal lock instead of inheriting old floors. [Frontend manifest](https://github.com/HKUDS/DeepTutor/blob/60fb3bdfddb30b7740c7ce3bd9b28d908f2af6db/web/package.json) was retrieved at the same commit.

[SQLiteSessionStore](https://github.com/HKUDS/DeepTutor/blob/60fb3bdfddb30b7740c7ce3bd9b28d908f2af6db/deeptutor/services/session/sqlite_store.py#L245) initializes private data paths, migrations and an asyncio lock. Its schema stores sessions, messages (including branch parents and JSON attachment/metadata), turns with owner/fencing/state version, client submission IDs/request digests and turn events. This is evidence of durable conversation machinery; user directory scope and every caller still require deployment-specific testing. The schema is not an Egyptian course/consent/entitlement ledger.

[SmartRetriever.retrieve](https://github.com/HKUDS/DeepTutor/blob/60fb3bdfddb30b7740c7ce3bd9b28d908f2af6db/deeptutor/services/rag/smart_retriever.py#L22) wraps an injected asynchronous search function, generates up to three query variants by default, searches concurrently and aggregates with another model call. This can amplify latency/cost beyond one request. This helper's returned `sources` contain query/provider metadata rather than complete immutable page-level evidence; preserve underlying passage locators in a commercial citation contract. This observation applies to this helper, not all DeepTutor retrieval backends. Arabic correctness and source integrity require a target-corpus test.
