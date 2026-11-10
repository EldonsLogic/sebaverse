# 09 — Reproducible technical patterns

These are candidates for original engineering, not permission to copy proprietary content. No components were installed for the tutoring product. Repository versions and licenses below are observed leads, not a completed dependency/security review. See the [source register](11-sources-and-evidence.md).

| Priority | Pattern | Starting point | Pilot test | Rights/maintenance boundary |
|---|---|---|---|---|
| 1 | Original diagnostic item and misconception taxonomy | educator-authored schema; inspiration W01 | errors distinguish alternative explanations | do not copy question banks or graph labels wholesale |
| 2 | Evidence ledger and transparent mastery rules | original relational model; compare W15 | assisted success cannot inflate independent status | record schema/state versions and correction lineage |
| 3 | Small prerequisite DAG | original expert review; compare G07 | remediation resolves prerequisite failure | edges need provenance; a graph database is unnecessary initially |
| 4 | Bounded tutor state machine | original implementation; compare W16 | hints, explanations and independent checks obey lesson policy | private prompts/code unavailable |
| 5 | Reliable answer checks | [SymPy](https://github.com/sympy/sympy) candidate, T12 | domain/units/equivalence edge cases | BSD code observed; reviewed solutions still needed |
| 6 | Delayed retrieval queue | original fixed intervals, later [ts-fsrs](https://github.com/open-spaced-repetition/ts-fsrs), G16 | retention compared with simpler queue | MIT candidate; recall scheduling ≠ concept mastery |
| 7 | BKT baseline | [pyBKT](https://github.com/CAHLR/pyBKT), G14–G15 | calibrated prediction versus rules | MIT code; dataset permissions separate |
| 8 | Recall-decay experiment | [HLR](https://github.com/duolingo/halflife-regression), A07 | local delay-aware recall prediction | historical language model; no assumed math transfer |
| 9 | Page-aware curriculum retrieval | original ingestion and provenance schema | exact page and syllabus hit rate, isolation tests | textbook/upload rights and OCR quality are gates |
| 10 | Worked-step misconception analysis | original schema informed by A15 | same wrong answer with different reasoning | cache approved cases only under relevant versioned context |
| 11 | Human review and evaluation corpus | original educator-adjudicated cases | regressions caught before release | preserve held-out set and legitimate processing purpose |
| 12 | Streaming voice and model routing | interchangeable provider adapters | measured quality/cost/latency frontier | current tariffs, processing terms and retention verified later |

## Clean-room implementation record

For every candidate technique, keep a short note with source, public idea, independently written design, code provenance, dependency license, dataset license and material-rights decision. Public papers can describe reproducible ideas without granting rights to their evaluation data, art or lesson text. EdNet's noncommercial restriction is particularly relevant [G05].

Do not import competitor bundles, inferred private prompts or decompiled code into the product. This investigation obtained none. If future authorized binary inspection reveals code, keep it in a separate research area and obtain a rights review before any reuse. Prefer published mechanisms and original implementations.

## Deferred research candidates

SAINT and other neural tracers are useful benchmark references [G04], but require a justified dataset and evaluation plan. Learned question-selection policies need safe action spaces and delayed outcome measures. Fine-tuning needs a stable error class, sufficient authorized labeled examples and independent release gates. Multi-agent coordination needs a measured advantage over one orchestrator. None is an initial feature merely because a large competitor uses related research.
