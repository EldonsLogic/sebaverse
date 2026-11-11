# Sebaverse — AI-native adaptive tutoring master project

Version 1.1 • 11 November 2026 • development foundation; product runtime not implemented.

Egypt-first, solo-founder, affordability-critical, globally extensible. The founder selected **Sebaverse** for brand development (U7). The project folder is Documents/Sebaverse; the existing repository and history are preserved. C visual identity with B blue/orange is selected (U10). No permanent slogan is selected; detailed brand/design review remains open. No application, paid model benchmark, deployment or real-student pilot has been implemented.

## Read first

1. [Context audit](docs/00-context-completeness-audit.md): both full research packs recovered; original conversation still partial. Founder restoration preserved; historical completeness is not certified.
2. [Product vision / PRD](docs/01-product-vision-prd.md) and [requirements register](registers/requirements.md), with editable [JSON](registers/requirements.json).
3. [Research reconciliation / evidence ledger](docs/02-research-reconciliation.md) and [source catalog](sources/source-catalog.md).
4. [Naming / brand / design / flows](design/brand-and-design-system.md), [editable tokens](design/design-tokens.json).
5. [Learning state machine](docs/03-learning-intelligence.md), [curriculum / uploads / RAG](docs/04-curriculum-and-rag.md), [routing / Jev / voice](docs/05-model-routing-and-voice.md).
6. [Architecture / data model](architecture/system-and-data-model.md), twelve [ADRs](architecture/adr/ADR-001-owned-modular-monolith.md), [safety / privacy / licensing](docs/06-safety-privacy-security.md).
7. [Economics](economics/README.md), [editable inputs](economics/inputs.json), [sensitivity](economics/sensitivity.md).
8. [QA / delivery / operations](docs/07-qa-evals-and-operations.md), [roadmap / gates](execution/roadmap-and-gates.md), [decisions / risks](registers/decisions-risks-unknowns.md).
9. [Codex instructions](AGENTS.md) and [phased prompts](execution/phased-codex-prompts.md).

## Research preservation

All 13 global research files and 14 open-source audit files are preserved unchanged, plus nine supporting evidence files (36 research artifacts total). Original citations, source registers and immutable repository links remain in place. The manifest records SHA-256; no research finding is promoted to a verified product behavior. The full older conversation remains GAP-001; accept the current founder restatement as baseline only through an explicit recorded decision or reconcile an eventual export.

## Current starting scope

German for a student at a national language school, using her uploaded curriculum first ([scope](docs/08-german-upload-first.md), U4). This is an initial content example only; U11 makes the platform architecture subject-independent and does not require this upload to proceed.

## Decisions to review next

Technical architecture is selected under U11/U12. Next: audit the concrete baseline and resolve PoC execution budget/dependency/security conditions. Grade/edition choices apply to pilot content, not core design. Production processor/rights/guardian/retention and commercial decisions remain gated. Pricing inputs are hypotheses, not validated margin. No current name/domain/mark clearance is claimed.

## Reproduce artifact checks

`python3 tools/model_economics.py` rebuilds illustrative costs; unknown full-margin inputs stay null. `python3 tools/validate_project.py` verifies report inventory, hashes, requirement references, links and arithmetic. See [validation report](VALIDATION.md). These are document checks, not security certification or measured tutoring results.

Project files are editable Markdown/JSON with preserved Git history. The founder designated https://github.com/EldonsLogic/sebaverse as the shared private remote under U13; verified milestone commits/pushes are authorized. Later code starts only after product, brand/design and architecture gates, and a bounded technical PoC precedes real-student use.

## Arabic-first identity trials

[Three new brand trial systems](outputs/sebaverse-brand-trial-v3/README.md): visual boards, editable guidelines and tokens, RTL reading previews. Arabic leads; logo stays Latin Sebaverse. Historical trials; superseded by the current brand system below.

## Current brand system

[Brand and design system v1](outputs/sebaverse-brand-system-v1/README.md): editable visual reference, guidelines, components, tokens, SVG assets and licensed fonts. This supersedes earlier palette trials; “كل سؤال باب” is not adopted.

## Selected architecture and audit handoff

[Technical baseline](architecture/technical-baseline.md), [all 104 features/functions](architecture/feature-function-matrix.md), [all 22 repo decisions](architecture/repository-adoption.md), and [subject-independent phases/PoC](execution/subject-independent-poc.md). [Shareable audit package](outputs/sebaverse-architecture-audit-v1/README.md). Design selected; no product or paid benchmarks built.

## Development starts here — U13/U14

[START-HERE](development/START-HERE.md) → [current checkpoint](development/CURRENT-STATE.md) → [step-by-step roadmap](development/ROADMAP.md) → [task graph](development/tasks.json) → [phase test gates](development/phase-gates.json). [Shared coding rules](development/ENGINEERING_RULES.md), [workflow](development/WORKFLOW.md) and [handover protocol](development/HANDOVER.md) keep Codex, Claude and Antigravity aligned. Root AGENTS.md is canonical; CLAUDE.md and the Antigravity rule point to it.

Every phase must pass its relevant required tests and independent review before the next begins. `python3 tools/check_foundation.py` and `python3 -m unittest discover -s tools/tests -p test_foundation.py` verify the development task/phase contracts; these do not replace product phase tests. No paid provider use, deployment or real-minor handling is implied by the foundation authorization.

## Dependency readiness

[Dependency setup](development/DEPENDENCIES.md), backend/uv.lock and web/package-lock.json define the minimal locked environments. `make dependency-check` validates committed closure/evidence and local library smoke; `make foundation-check` runs document, phase and evidence regressions. F1 status and actual Linux/local results are recorded in development/CURRENT-STATE.md and evidence files; installed dependencies are ignored, not committed. No product app is implied by dependency readiness.
