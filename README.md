# TBD — AI-native adaptive tutoring master project

Version 0.2 • 10 November 2026 • documentation and planning only.

Egypt-first, solo-founder, affordability-critical, globally extensible. The platform name is undecided. This repository belongs in the founder's existing Documents/TBD project; rename that project after a reviewed brand selection. No application, paid model benchmark, deployment or real-student pilot has been implemented.

## Read first

1. [Context audit](docs/00-context-completeness-audit.md): both full research packs recovered; original conversation still partial. Founder restoration preserved; historical completeness is not certified.
2. [Product vision / PRD](docs/01-product-vision-prd.md) and [requirements register](registers/requirements.md), with editable [JSON](registers/requirements.json).
3. [Research reconciliation / evidence ledger](docs/02-research-reconciliation.md) and [source catalog](sources/source-catalog.md).
4. [Naming / brand / design / flows](design/brand-and-design-system.md), [editable tokens](design/design-tokens.json).
5. [Learning state machine](docs/03-learning-intelligence.md), [curriculum / uploads / RAG](docs/04-curriculum-and-rag.md), [routing / Jev / voice](docs/05-model-routing-and-voice.md).
6. [Architecture / data model](architecture/system-and-data-model.md), eight [ADRs](architecture/adr/ADR-001-owned-modular-monolith.md), [safety / privacy / licensing](docs/06-safety-privacy-security.md).
7. [Economics](economics/README.md), [editable inputs](economics/inputs.json), [sensitivity](economics/sensitivity.md).
8. [QA / delivery / operations](docs/07-qa-evals-and-operations.md), [roadmap / gates](execution/roadmap-and-gates.md), [decisions / risks](registers/decisions-risks-unknowns.md).
9. [Codex instructions](AGENTS.md) and [phased prompts](execution/phased-codex-prompts.md).

## Research preservation

All 13 global research files and 14 open-source audit files are preserved unchanged, plus nine supporting evidence files (36 research artifacts total). Original citations, source registers and immutable repository links remain in place. The manifest records SHA-256; no research finding is promoted to a verified product behavior. The full older conversation remains GAP-001; accept the current founder restatement as baseline only through an explicit recorded decision or reconcile an eventual export.

## Current starting scope

German for a student at a national language school, using her uploaded curriculum first ([scope](docs/08-german-upload-first.md), U4). Naming, logo, slogan and brand guidelines come next (U5). Grade/level/edition and explanation language remain open.

## Decisions to review next

Remaining grade/level/edition/buyer and content-rights route; monthly vs course/semester plan and cost ceiling; shortlist/name/design direction; data-processing/guardian/safeguarding route; stack/provider benchmarks and bounded PoC budget. All gate approval records remain pending. Pricing inputs are hypotheses, not validated margin. No current name/domain/mark clearance is claimed.

## Reproduce artifact checks

`python3 tools/model_economics.py` rebuilds illustrative costs; unknown full-margin inputs stay null. `python3 tools/validate_project.py` verifies report inventory, hashes, requirement references, links and arithmetic. See [validation report](VALIDATION.md). These are document checks, not security certification or measured tutoring results.

Project files are editable Markdown/JSON with local Git history. No remote repository or publishing is created. Later code starts only after product, brand/design and architecture gates, and a bounded technical PoC precedes real-student use.
