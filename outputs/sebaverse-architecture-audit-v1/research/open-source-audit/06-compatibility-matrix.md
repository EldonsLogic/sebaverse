# Compatibility and dependency matrix

Assessment date: 10 November 2026. “Compatible” means a plausible integration boundary; no end-to-end integration has been executed. See [02](02-deeptutor-audit.md), [03](03-learnhouse-audit.md) and [04](04-adaptive-learning-libraries.md) for source evidence.

| Combination | Technical feasibility | Data/identity mismatch | License / operational consequence | Verdict |
|---|---|---|---|---|
| LearnHouse + DeepTutor by HTTP | Feasible with custom adapter | Courses, orgs, memberships, tutor users/workspaces/sessions and progress are different models | AGPL + Apache code may form an AGPL-covered combined work depending on integration; two products to secure/upgrade | Avoid for pilot |
| LearnHouse native AI + custom learner state | Feasible; existing RAG/AI makes second tutor optional | Activity completion != assessed concept mastery; guardian consent custom | AGPL and EE payment/analytics boundaries | Conditional LMS-first option |
| Custom platform + full DeepTutor | Feasible using supported API/SDK boundary | Must prevent direct unentitled bypass; choose one owner of sessions and learner evidence | Apache favorable, but tools/plugins/exec surface and runtime-home storage require extensive hardening | Reference first; bounded extraction only |
| DeepTutor selected modules + custom monolith | Plausible after dependency closure test | Map schemas into owned contracts, never treat inferred memory as grades | Preserve Apache notices; transitive optional tools separately reviewed | Preferred selective reuse path |
| LearnHouse source extracted into proprietary monolith | Technically possible | Tight coupling to LMS models/permissions | Copying AGPL source can impose copyleft; EE code unavailable without rights | Reject unless open-sourcing affected work or commercial permission |
| Django + Postgres + pgvector | Straightforward architecture candidate | Own authorization on ORM and raw SQL; extension migration ownership | BSD framework / PostgreSQL licenses; one database | Preferred platform baseline |
| Docling + OCR within same API environment | Installable in principle | Structured parse output needs owned provenance schema | Heavy ML deps/native binaries/model downloads | Separate worker environment, same application domain |
| pyBKT + application state | Fit offline; lightweight inference adapter | Skill mappings and event semantics must match training | MIT; compiled/numerical environment separate | Optional later; start explicit rules/BKT priors |
| pyKT/EduStudio/PyEdmine in request-serving app | Poor fit | Benchmark sequences and IDs != live student events | Torch dependencies, train/test leakage risk; EduStudio provenance concern | Offline research only; quarantine EduStudio pin |
| FSRS + mastery | Complementary | Recall/review schedule != skill competence | MIT; low CPU cost | Separate schedule field, never overwrite mastery |
| SymPy + public answer input | Possible with restricted grammar | Domain/units assumptions matter | BSD; unsafe free-form parsing and CPU denial of service | Bound worker; no raw eval parser |
| Chatterbox + monolith | Only through a separate ML worker if reconsidered | Whole-waveform output and mutable per-instance voice conditioning | MIT code; model/voice rights and unmaintained runtime, Torch/transformers/direct Git dependency burden | Reject default; no assumed streaming/Arabic dialect quality |
| Pipecat + Django | Separate asynchronous media worker justified if continuous audio | Session auth, cancellation and budget must share IDs | BSD; transport/provider version churn | P1 optional, not microservices by default |
| Langfuse + OpenTelemetry | Optional exporter / UI | Redaction and deletion must follow authoritative records | MIT core / EE exclusions; current self-host stack is substantial | Defer full stack; retain OTel IDs now |
| Moodle + custom tutoring API | Supported webservices are a plausible boundary | User, course and grade mapping; tutor must not impersonate global admin | GPLv3+ plugin/distribution obligations; separate PHP ops | Fallback if teacher/LMS need dominates |
| Frappe LMS + custom tutor | API integration plausible | DocTypes and roles need mapping | AGPLv3 + Frappe environment; current Python 3.14 requirement | Lower-priority alternative |

## Runtime boundaries

| Component | Verified manifest / platform fact | Proposed environment / implication |
|---|---|---|
| DeepTutor | See pinned root `pyproject.toml`, requirements and modular packages in 02 | Do not merge its full optional dependency set into the platform |
| LearnHouse | FastAPI/Python backend; Next/React frontend; Postgres and Redis; detailed versions in 03 | Keep upstream environment intact if evaluating; no shared database writes |
| Docling | `pyproject.toml` 2.150.0, Python >=3.10,<4, Pydantic 2 range | Python 3.12 worker first; engine/model extras locked independently |
| Pipecat | Python >=3.11; Pydantic >=2.10.6,<3 (higher floor on 3.14) | Python 3.12 audio worker; pin providers and transport together |
| Frappe LMS | Python >=3.14,<3.15 at this commit | Do not assume it fits the proposed 3.12 application environment |
| Promptfoo | Node >=22.22.0 | Offline tooling container; no production runtime dependency |
| Langfuse | Node 24 at pin; Compose multiple stateful dependencies | Separate optional observability deployment |
| Adaptive libraries | Different Torch/NumPy/version constraints; see 04 | Offline environment, export a versioned inference contract |
| Primary application proposal | Django 5.2 LTS supported through April 2028 per [official support table](https://www.djangoproject.com/download/#supported-versions) | Python 3.12; re-resolve current security patch and extensions before building |
| Database proposal | PostgreSQL 17 or 18 supported per [official policy](https://www.postgresql.org/support/versioning/) | Prefer managed supported major with pgvector, backups and chosen legal processing region |

These are proposals, not a successfully resolved lockfile. Version compatibility must be proven by the experiment in [11](11-integration-proof-of-concept-plan.md). Default-branch pins can be development revisions; choose stable deployment releases after review.

## Owned contracts that prevent lock-in

Define `TutorRequest` with authenticated actor, learner, course-version, session, locale, permitted tools, budget reservation and policy version. Return a typed stream of text/citations/tool results/usage/final status. Define `AssessmentEvidence` with event ID, item and rubric versions, concept mapping, independent/hinted status, score, grading confidence and timestamp. Define `KnowledgeState` with model version, evidence cursor, uncertainty and prerequisite status. Define a `DocumentChunk` with immutable curriculum/academic-year version, page/block, provenance, owner and visibility. Include schema version in each contract.

HTTP adapters translate external identifiers through mapping tables. Never let an AI service write enrollment, consent, entitlements or final grades directly. The platform remains authoritative; delivery retries must be idempotent and resumable. Use an outbox for assessment processing and payment notifications, not distributed transactions.
