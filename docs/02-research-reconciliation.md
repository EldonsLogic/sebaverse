# Research reconciliation and evidence ledger

Evidence labels: OBS = observed by this consolidation (file existence, hashes, arithmetic or readable official page); REP = reported observation in preserved research, not independently rerun; VENDOR = published claim; INF = inference; PROP = proposed decision; UNK = unresolved. A filename or assistant statement is not independent corroboration. Research source IDs resolve in sources/source-catalog.md; global W/A/G/R/T IDs resolve inside G11, not the Axx audit namespace.

| ID | Claim and type | Source / locator | Reconciliation and consequence |
|---|---|---|---|
| E01 | OBS: 27 Markdown reports/READMEs and nine audit evidence files available | research manifest | Both full packs preserved; no attachment gap remains |
| E02 | OBS: five recent conversation turns returned, no older cursor | C1 raw response | Cannot assert full historical coverage; U2 restores many requirements, GAP-001 stays open |
| E03 | PROP: owned modular monolith, one bounded orchestrator | G10; A07/A12/A13 | Convergent design recommendations, not proof of best stack; ADR-001/002 remain proposed |
| E04 | REP: DeepTutor has memory, mastery, guardians, retrieval and voice | A02 Verified capability classification; pinned source links | Reject outdated assumption it is merely a stateless chatbot. Capability existence does not establish learning validity or safe commercial deployment |
| E05 | REP: DeepTutor mastery is a recent-attempt heuristic | A02 mastery source; evidence/test-results.md | May study/extract a small module; do not equate heuristic score with calibrated mastery |
| E06 | REP: LearnHouse duplicates LMS/AI/RAG and has AGPL/EE boundaries | A03; A06; A08 | LMS fallback only; do not copy AGPL code under a proprietary assumption |
| E07 | REP: EduStudio inspected workflow exposes reversible publishing-secret encoding if secret exists | A08 Findings; pinned exfil.yml link | Quarantine exact revision. Actual token exposure, maintainer intent and package compromise unknown; no blanket accusation |
| E08 | REP: LearnHouse header-based CSRF exemption in narrow tests | A08; evidence/test-results.md | Hardening concern; no demonstrated account-takeover chain claimed |
| E09 | REP: limited smoke tests and eight-version OSV query only | A01/A08; evidence/dependency-check.json | Neither a full-runtime validation nor a clean security bill; resolved dependency/container scan required |
| E10 | PROP: evidence rules before complex KT/RL | G04/G05; A04/A12 | Keep BKT/logistic/IRT/DKT benchmark path; prediction AUC alone cannot promote teaching policy |
| E11 | REP: REA source-reviewed, not executed | G03 | No recovered private backend, authenticated competitor session or proprietary algorithm is claimed |
| E12 | REP/VENDOR: current competitor packaging and efficacy vary | G02/G07/G11 | Eedi near-transfer vs broad scores, Synthesis DARPA attribution, historical Duolingo algorithms and changing tiers cannot be pooled into a winner score |
| E13 | INF: locally reliable evidence-led tutoring may differentiate | G08; G01/G02 regional profiles | Arabic/local competitors exist. No first-Arabic-tutor or proven-grade-improvement claim |
| E14 | REP: audit cost estimates use assumptions and dated rates | A09; evidence/cost-scenarios.json | $0.475 text, $5.575 cascade, $25.475 live are illustrative per-active-learner scenarios, not bills or full COGS |
| E15 | PROP: voice is central enough to test early but capped | U2; C1; G06; A11 | Resolves text-first vs voice-first tension: benchmark early, ship only after quality/privacy/economic gates |
| E16 | OBS/VENDOR: Jev describes a structured decision API with probabilities | https://jev-ai.org/docs/ opened 2026-11-10 | Decision-classifier candidate, not dialogue replacement. Vendor calibration/latency claims not locally validated; no educational benchmark yet |
| E17 | UNK: Jev independent 37-dataset claim quoted by prior assistant | C1 only; underlying paper absent from packs | Do not repeat as verified evidence; retrieve actual study before relying on it |
| E18 | UNK: Egyptian regulatory implementation and provider-specific minor terms | A08; regulator home page unreadable in this session | Counsel/official-source confirmation before real-minor processing; no checkbox-compliance claim |
| E19 | Founder-reported: ~100 prospects, EGP hypotheses, family/friends pilot | U2 | Useful planning constraints; not independently verified conversion or authorization |
| E20 | PROP: Django/Postgres baseline | A12 vs C1 caution | Compare Django with a thin alternative during architecture review; preserve modular application regardless of framework |
| E21 | REP: Chatterbox retired at inspected source, model rights separate | A01/A05; evidence/chatterbox-source-audit.md | Not a maintained pilot default; any later status requires fresh owning-source verification |

## Build/reuse disposition

Own: curriculum/version/rights domain, assessment events, learner projections, consent/guardian scopes, next-action policy, entitlements, usage accounting and release lineage. Candidate reusable tools: Django, Postgres, pgvector if useful, Docling/OCR worker, SymPy with safe typed inputs, FSRS later, pyBKT offline, OTel, optional eval tooling. Preserve each dependency's license and transitive/model/data rights. Never auto-run copied research workflows or untrusted package scripts.

Conditional: DeepTutor extraction limited by dependency closure and rights; LearnHouse/Moodle only if actual buyer needs an LMS. Defer: neural KT/RL, autonomous agent teams, model training and always-on GPUs. Exclude inspected EduStudio pin from execution pending independent provenance resolution. Full disposition matrix and exact pins remain in A01/A06/A10; this summary does not replace them.

## Evidence maintenance

New claim row requires proposition, exact source/version/date/locator, type, confidence scope, contradiction, decision affected and owner. Separate publication certainty from effect size/generalization. Record negative results and inaccessible sources. Promotion from research recommendation to project decision requires a dated ADR/gate; a repeated assistant assertion never promotes evidence.
