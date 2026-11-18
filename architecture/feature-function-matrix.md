# Complete feature/function and phase map

U12 · Every current requirement R001–R104 appears below, including future/rejected/deferred paths. **No product function is implemented by this document.** Phase entries are the selected architecture delivery sequence, not deletion or readiness claims. Exact sources, dependencies, original acceptance criteria and status are in [editable JSON](feature-function-matrix.json), exported from the authoritative requirement register. A0–A7 are defined in the [phase plan](../execution/subject-independent-poc.md).

| Requirement / feature | Functions | Phase | Build / ready-component boundary |
|---|---|---|---|
| R001 — Audit context completeness before final specifications | Inventory sources, disclose historical gaps, append reconciliations | A0/A1 | Owned product/application logic |
| R002 — Preserve research originals and citations | Hash and preserve all research originals and citations | A0/A1 | Owned product/application logic |
| R003 — Trace every available founder requirement without silently dropping future scope | Maintain IDs, source/phase/dependency coverage and change control | A0/A1 | Owned product/application logic |
| R004 — Product vision, target users and jobs | Maintain user/job/outcome and service scope contracts | A0/A1 | Owned product/application logic |
| R005 — Choose first Egypt curriculum/age/subject unit | Configure pilot content/age/buyer; not architecture prerequisite | A0/A1 | Owned product/application logic |
| R006 — Solo-founder maintainability | Keep single domain and minimal operations footprint | A0/A1 | Owned product/application logic |
| R007 — Affordability and pricing hypotheses | Model plans, quotas and willingness-to-pay hypotheses | A0/A1 | Owned product/application logic |
| R008 — Preserve ~100 prospects and supervised family/friends pilot context | Manage permitted prospect/pilot readiness; no assumed conversion | A3–A6 | Owned product/application logic |
| R009 — Brand naming strategy and candidate screening | Manage selected name and clearance evidence | A0/A1 | Design/documentation; React UI later |
| R010 — Identity/design system | Version design tokens, components and branding rules | A0/A1 | Design/documentation; React UI later |
| R011 — UX journeys | Compose student/parent/upload/voice/teacher journeys | A0/A1 | Design/documentation; React UI later |
| R012 — Use existing TBD project folder; rename after chosen brand | Preserve canonical project path and local history | A0/A1 | Design/documentation; React UI later |
| R013 — Egyptian Arabic conversational text | Explain/converse in Egyptian Arabic with rubric slices | A3–A6 | Owned product/application logic |
| R014 — MSA text and academic terminology | Support MSA academic terminology and formal notices | A3–A6 | Owned product/application logic |
| R015 — English and code-switching text | Handle English and language switching with bidi isolation | A3–A6 | Owned product/application logic |
| R016 — Egyptian Arabic/MSA/English voice | Record/transcribe/synthesize/cancel speech with text fallback | A4; rollout conditional | Owned product/application logic |
| R017 — Adaptive explanations | Select explanation strategy from evidence and subject profile | A3–A6 | Owned product/application logic |
| R018 — Interactive lessons and visual manipulatives | Render reviewed interactive learning representations | A7; contracts now | Owned product/application logic |
| R019 — Guided problem-solving and hint ladder | Offer bounded hints and track assistance/exposure | A3–A6 | Owned product/application logic |
| R020 — Exercises and quizzes | Serve reviewed items, collect attempts and validate grading | A3–A6 | Owned product/application logic |
| R021 — Timed mock exams | Build reviewed exam blueprint, timer/accommodations and post-exam remediation | A7 | Owned product/application logic |
| R022 — Personalized exam preparation | Plan revision from objectives, time availability and uncertainty | A7 | Owned product/application logic |
| R023 — Persistent progress across sessions | Resume checkpoints and preserve evidence across sessions | A3–A6 | Owned product/application logic |
| R024 — Mastery tracking with uncertainty | Project evidence-backed status and uncertainty | A3–A6 | Owned product/application logic |
| R025 — Immutable evidence ledger and correction lineage | Append/deduplicate/correct/replay assessment evidence | A3–A6 | Owned product/application logic |
| R026 — Misconception diagnosis | Maintain expiring misconception hypotheses and disambiguating probes | A3–A6 | Owned product/application logic |
| R027 — Prerequisite knowledge graph | Review prerequisite edges and validate graph | A3–A6 | Owned product/application logic |
| R028 — Explainable adaptive learning paths | Rank eligible next actions with reason codes and safe choice | A3–A6 | Owned product/application logic |
| R029 — Active recall and independent assessment | Select unseen item families and track independent checks | A3–A6 | Owned product/application logic |
| R030 — Spaced repetition and delayed retention | Schedule/review recall with versioned strategy | A3–A6 | Owned schedule boundary + fixed rule / py-fsrs comparison |
| R031 — Individual adaptation loop | Update learner policy inputs after validated events | A3–A6 | Owned product/application logic |
| R032 — System-wide evaluated feedback loop | Triage failure categories and promote reviewed fixes after regression | A3–A6 | Owned product/application logic |
| R033 — Optional controlled model improvement | Curate separately authorized training data and gated model release | A7; contracts now | Owned product/application logic |
| R034 — Compare rules/BKT/logistic/IRT/deep KT | Run offline estimator comparisons with lawful adequate data | A4; rollout conditional | Owned product/application logic |
| R035 — Built-in versioned Egyptian curricula | Publish rights-reviewed built-in Egyptian editions | A3 core; A5 reviewed content | Owned product/application logic |
| R036 — National/language/IGCSE/IB/American and global curricula | Configure multiple systems/specifications/curricula without hardcoding | A3 core; A5 reviewed content | Owned product/application logic |
| R037 — Student-uploaded materials/custom curriculum | Upload private learner materials and custom objectives | A3 core; A5 reviewed content | Owned product/application logic |
| R038 — Parent-uploaded textbooks/notes/worksheets | Verify parent upload authority and learner sharing scope | A3 core; A5 reviewed content | Owned product/application logic |
| R039 — OCR/layout/math/table/diagram extraction | Extract layout/text/table/equation/image anchors and quality flags | A3 core; A5 reviewed content | Own controls + isolated Docling; OCR fallback conditional |
| R040 — Safe upload ingestion and quotas | Reserve upload quota, quarantine, scan, parse, cancel/retry safely | A3 core; A5 reviewed content | Own controls + isolated Docling; OCR fallback conditional |
| R041 — Content rights/provenance/permissions | Record processing/display/derivative rights and restrictions | A3 core; A5 reviewed content | Owned product/application logic |
| R042 — Versioning, curriculum mapping and supersession | Version editions, mappings and supersession/migration manifests | A3 core; A5 reviewed content | Owned product/application logic |
| R043 — Original reviewed item bank/rubrics | Review original items, variants, rubrics and answer-key scope | A3 core; A5 reviewed content | Owned product/application logic |
| R044 — RAG retrieval architecture | Index scoped chunks; compare lexical/dense/hybrid retrieval | A3 core; A5 reviewed content | Own scope/citations + PostgreSQL/pgvector |
| R045 — Document-grounded answers and exact citations | Resolve exact authorized source/version/page citations and abstain | A3 core; A5 reviewed content | Owned product/application logic |
| R046 — Private upload isolation and deletion | Isolate/purge originals, derived indexes/cache and pending jobs | A3 core; A5 reviewed content | Owned product/application logic |
| R047 — Parent dashboard and meaningful progress | Render permitted parent progress and uncertainty summaries | A3–A6 | Owned product/application logic |
| R048 — WhatsApp progress reports | Queue minimal opt-in WhatsApp message with authenticated portal link | A6; external actions gated | Owned product/application logic |
| R049 — Notification preferences and revocation | Manage notification purpose/channel/opt-out and revocation | A6; external actions gated | Owned product/application logic |
| R050 — Future teacher/classroom functionality | Add scoped educator/class/course authoring and reports | A7 | Owned product/application logic |
| R051 — Subscriptions/course-semester entitlements | Enforce course/term/subscription grants and quotas | A3–A6 | Owned product/application logic |
| R052 — Payment integration and refunds | Validate signed payment/refund events and reconcile entitlements | A6; external actions gated | Owned product/application logic |
| R053 — Child safety and age-appropriate interactions | Apply age-appropriate safety policy, pause/report/review workflow | A0/A1 | Owned product/application logic |
| R054 — Accessibility and low-bandwidth/mobile UX | Responsive/low-bandwidth keyboard/screen-reader UI and text fallback | A3–A6 | Owned product/application logic |
| R055 — RTL/LTR and accessible mathematics | Render RTL/LTR text and accessible equations/alternatives | A3–A6 | Owned product/application logic |
| R056 — Child understandable notices and student agency | Explain limits/privacy in child-understandable copy and allow correction/skip | A3–A6 | Owned product/application logic |
| R057 — Guardian verification and consent lifecycle | Verify guardian edge and purpose-scoped consent/revocation | A0/A1 | Owned product/application logic |
| R058 — Privacy/data processing and transfer review | Review processor/region/transfer and minimize disclosure | A0/A1 | Owned product/application logic |
| R059 — No automatic training on identifiable child chat | Exclude child chat from automatic training and default fixtures | A0/A1 | Owned product/application logic |
| R060 — Secure data/tenant/object/tool isolation | Authorize all object/query/tool/job/stream/file boundaries | A3–A6 | Owned product/application logic |
| R061 — Retention/export/deletion/backups | Export/delete/expire records and replay purge after restore | A3–A6 | Owned product/application logic |
| R062 — Provider-agnostic adapters | Normalize text/embed/STT/TTS capabilities, errors, usage and cancellation | A3–A6 | Owned adapters/policy + qualified vendor/library interfaces |
| R063 — Benchmark OpenAI/Claude/Gemini | Compare eligible OpenAI/Claude/Gemini routes on matched tasks | A4; rollout conditional | Owned adapters/policy + qualified vendor/library interfaces |
| R064 — Benchmark Qwen/DeepSeek/Chinese model options | Compare eligible Qwen/DeepSeek/other hosted Chinese routes | A4; rollout conditional | Owned adapters/policy + qualified vendor/library interfaces |
| R065 — Open-weight/local inference path | Benchmark local/open-weight serving behind same adapter | A4; rollout conditional | Owned adapters/policy + qualified vendor/library interfaces |
| R066 — Jev-style classifier experiment | Compare rules/classifier/small LLM/Jev in shadow | A4; rollout conditional | Owned adapters/policy + qualified vendor/library interfaces |
| R067 — Deterministic state/business authority | Validate authority/state transitions and own score acceptance | A3–A6 | Owned product/application logic |
| R068 — Model routing and qualified fallback | Route only eligible qualified options with bounded retries/fallback | A3–A6 | Owned adapters/policy + qualified vendor/library interfaces |
| R069 — Token/context/cache optimization | Bound context/history, summarize checkpoints and scope caches | A3–A6 | Owned product/application logic |
| R070 — Token/audio usage accounting and limits | Reserve/reconcile exact units, quota/concurrency and cancelled cost | A3–A6 | Owned product/application logic |
| R071 — Voice economics and quotas | Compare cascade/realtime bills and enforce voice caps | A4; rollout conditional | Owned product/application logic |
| R072 — GPU/self-hosting sensitivity at 100/1k/10k users | Model GPU idle/peak/operations at 100/1k/10k active workloads | A4; rollout conditional | Owned product/application logic |
| R073 — Operating cost/unit economics sensitivity | Compute full variable/fixed/review/rights/support economics | A0/A1 | Owned product/application logic |
| R074 — Optimize cost per successful learning outcome | Measure cost per valid independent activity/retained skill | A3–A6 | Owned product/application logic |
| R075 — Domain/data model and API contracts | Version entities, commands/events and integrity constraints | A0/A1 | Owned product/application logic |
| R076 — QA/evals and language slices | Maintain frozen grounding/grading/safety/language holdouts | A3–A6 | Own fixtures + pytest/Playwright/Promptfoo |
| R077 — Architecture ADRs and decisions | Record stack choices, evidence, alternatives and reversal triggers | A0/A1 | Owned product/application logic |
| R078 — CI/CD and release lineage | Build/test/promote immutable release lineage with rollback | A3–A6 | Owned product/application logic |
| R079 — Observability and redacted incident/cost metrics | Emit redacted latency/error/cost/job metrics and restricted audit | A3–A6 | Own allowlisted fields + OpenTelemetry |
| R080 — Operational runbooks/recovery/support | Operate recovery/dead-letter/support/deletion/incident runbooks | A3–A6 | Owned product/application logic |
| R081 — Security/licensing source findings | Resolve exact dependency/security/license/model-rights findings | A0/A1 | Owned product/application logic |
| R082 — Quarantine inspected EduStudio revision | Prevent execution/reuse of quarantined EduStudio pin | A0/A1 | Excluded/quarantined audited pin |
| R083 — Selective DeepTutor reuse only | Reference DeepTutor; optional bounded extraction with closure proof | A4; rollout conditional | DeepTutor reference only; no baseline runtime dependency |
| R084 — LearnHouse LMS fallback with AGPL/EE review | Keep LearnHouse fallback separate pending AGPL/EE decision | A7 | LearnHouse deferred; no baseline integration |
| R085 — Framework choice remains reversible | Use selected stack; revise only with evidence-backed ADR | A0/A1 | Owned product/application logic |
| R086 — Roadmap/milestones/work breakdown | Phase work with dependencies, bounded tasks and honest not-run results | A0/A1 | Owned product/application logic |
| R087 — Risks/unknowns/decision log | Track risk owners, unknown triggers and decision lineage | A0/A1 | Owned product/application logic |
| R088 — Codex instructions and phased prompts | Give agents requirement-linked gated implementation prompts | A0/A1 | Owned product/application logic |
| R089 — Version-controlled editable master artifacts | Version editable artifacts and reproducible checks locally | A0/A1 | Owned product/application logic |
| R090 — No premature implementation; bounded PoC after gates | Separate finalized technical design from permission to execute/deploy | A0/A1 | Owned product/application logic |
| R091 — Multimodal/photo/diagram tutoring | Interpret authorized images/diagrams with uncertainty and source anchors | A7; contracts now | Owned product/application logic |
| R092 — Independent assessment/grade appeal and teacher correction | Hold disputed grades, adjudicate and replay affected projections | A3–A6 | Owned product/application logic |
| R093 — Learning outcomes without unsupported efficacy claims | Measure independent delayed transfer/retention without unsupported claims | A3–A6 | Owned product/application logic |
| R094 — Global-ready architecture without premature breadth | Separate subject profiles, curriculum versions and providers from core | A0/A1 | Owned product/application logic |
| R095 — German tutoring using the learner-uploaded school curriculum | Configure initial German example through ordinary subject/content path | A5 initial content example; not architecture dependency | Owned product/application logic |
| R096 — Brand name, logo, slogan and guidelines before implementation | Apply selected identity and review wording independently | A0/A1 | Design/documentation; React UI later |
| R097 — Arabic-first brand/product experience | Lead with Arabic typography/navigation and mixed-language layouts | A0/A1 | Design/documentation; React UI later |
| R098 — Latin-only Sebaverse logo | Use Latin Sebaverse vector logo without mirroring | A0/A1 | Design/documentation; React UI later |
| R099 — Subject-independent platform architecture and audit handoff | Deliver auditor-ready maps, feature coverage, repo boundaries and phases | A0/A1 | Owned product/application logic |

## Development foundation additions U13/U14

F0–F8 are the development view of A1–A7, defined in development/ROADMAP.md; the original architecture phase scope is retained. The frozen v1 audit export remains the 99-requirement historical snapshot.

| Requirement | Functions | Phase | Build/reuse |
|---|---|---|---|
| R100 — Shared private GitHub source of truth and verified milestone pushes | Verify remote identity/privacy; commit/review/push and reconcile local/remote SHA | F0 and every subsequent phase | Owned workflow/check tooling; pinned source ideas adapted, no external source runtime |
| R101 — Agent-neutral roadmap, task graph and durable handover | Claim task/file ownership; checkpoint evidence and exact next step across agents | F0 and every subsequent phase | Owned workflow/check tooling; pinned source ideas adapted, no external source runtime |
| R102 — Pinned coding-discipline guidance in shared project rules | Apply concise assumption/simplicity/focused-change/observable-success discipline | F0 and every subsequent phase | Owned workflow/check tooling; pinned source ideas adapted, no external source runtime |
| R103 — Extract and execute bounded verifiable agent-team guidance | Maintain contracts/real roster; delegate independent files; test/review/record actual outputs | F0 and every subsequent phase | Owned workflow/check tooling; pinned source ideas adapted, no external source runtime |
| R104 — Tests and review must pass after every phase before progression | Declare/run phase tests; reject premature advancement; record evidence, reviewer and blockers | F0 and every subsequent phase | Owned workflow/check tooling; pinned source ideas adapted, no external source runtime |

## U19 protocol integration addition

| Requirement | Functions | Phase | Build/reuse |
|---|---|---|---|
| R105 — AG-UI tutor/interface protocol integration | Map reviewed events; preserve live authorization, validated blocks, replay and cancellation | F4 / A3, DEV-013 after F3 exit | Owned adapter plus exact reviewed upstream schema/SDK; no whole scaffold |
