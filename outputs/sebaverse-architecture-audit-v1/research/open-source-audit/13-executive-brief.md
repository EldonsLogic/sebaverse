# Founder executive brief

10 November 2026. **Build a small owned modular monolith. Use neither DeepTutor nor LearnHouse wholesale for the initial pilot.** Study DeepTutor and selectively reuse small Apache-licensed components only if extraction is demonstrably simple. Keep LearnHouse as an LMS fallback if its AGPL/enterprise terms fit the business. Do not force the two together.

## Why

DeepTutor has real orchestration, durable sessions, memory, guardian links, retrieval, practice, voice and mastery features. Its inspected mastery estimator is a recent-attempt heuristic, not validated knowledge tracing. Hardening its general-purpose tools and commercial/child-data boundaries would consume substantial effort.

LearnHouse has real accounts, courses, assignments, progress, Arabic localization, headless APIs and its own AI/RAG. Adding DeepTutor duplicates key functionality. Payments, full analytics and multi-organization behavior have enterprise boundaries; private learner intelligence and verified guardian consent still need building. Copying its AGPL code into a proprietary product is a licensing decision, not a shortcut.

The inspected EduStudio revision contains a workflow that exposes an encoded publishing secret if present. Quarantine it. Actual token exposure/package compromise was not established. pyKT and PyEdmine are useful research harnesses, not ready-made personalized tutoring backends.

## Foundation and reuse

Use Django auth/admin, Postgres, private file storage, one restricted document worker and a bounded provider-neutral tutor loop. Add pgvector only if retrieval tests justify it. Own curriculum editions, assessments, learner evidence/state, guardian consent, next-action policy and course/semester entitlements. Begin with explicit mastery rules, prerequisite graphs and spaced revision; optional pooled BKT later, deep KT/IRT only when representative data and held-out tests support them.

Separate learner state, tutoring decisions and improvement releases. Use reviewed items and independent answers to update state; prompts/models/policies change only through offline tests, human review, feature flags and rollback. Never auto-train on identifiable student conversations or allow a self-modifying tutor.

## Effort and operating cost

First validate one unit with the [10–15 engineer-day experiment](11-integration-proof-of-concept-plan.md). A supervised narrow pilot then plausibly needs **10–16 engineer-weeks**, plus educator, curriculum-rights, legal and support work. This is a planning range, not a delivery promise. Broader commercial rollout is a multi-quarter undertaking for a solo founder.

[Illustrative monthly costs](09-ai-infrastructure-and-economics.md), including assumed fixed infrastructure and a 25% AI reserve:

| Active learners | Text-heavy | Voice-heavy with verified Live minute rate* |
|---:|---:|---:|
| 20 | ~$110 | ~$610 |
| 100 | ~$248 | ~$2,748 |
| 1,000 | ~$1,075 | ~$26,075 |
| 10,000 | ~$7,750 | ~$257,750 |

*400 voice minutes/learner/month plus assumed backend text usage. Model mix, workload and hosting are assumptions; vendor minute/token rates were checked. A separately modeled cascade could be cheaper, but its per-minute prices are explicitly unverified placeholders. Costs exclude staff, educator review, content, tax, payments, messaging and acquisition. Voice quotas and measured unit economics are essential. No final EGP selling price is recommended.

## Major launch risks

- AGPL/enterprise boundaries and curriculum/model/dataset rights.
- Egyptian sensitive-child-data consent, processing/transfer requirements and provider contracts. Current regulations and official procedures need local legal verification; a pilot is not assumed exempt.
- Cross-student retrieval/access leaks, unsafe uploads, document prompt injection and unbounded voice/tool costs.
- Confusing engagement or generated explanations with demonstrated independent learning.
- Fast-moving upstream dependencies and limited full-runtime verification. Narrow smoke checks passed; complete application/security/load suites did not run.

## Decisions before development

Choose the first education system, grade, age band, subject/unit and semester; secure content and educator review. Confirm acceptable source-license strategy, child-data processing/hosting routes and pilot consent process. Decide text-first versus capped voice, prepaid course/semester grants versus enabled recurring billing, success metrics and budget.

Use the separate competitive/customer research to settle buyer, differentiation, voice value, teacher workflow demand, willingness to pay and distribution/support economics. If schools require a full LMS immediately, reconsider a supported stable Moodle release plus the owned tutor/state module; do not deploy the audited Moodle development branch.

First implementation milestone: one supervised course unit with guardian onboarding, approved sources/items, grounded text tutoring, independent practice, explainable learner state, due revision, a minimal parent summary, usage caps and tested deletion/backup procedures. Keep broad teacher tools and unlimited voice outside that milestone.

Start with [repository inventory](01-repository-inventory.md), [architecture options](07-integration-architecture-options.md), [security/licensing](08-security-and-licensing.md) and [recommended foundation](12-recommended-technical-foundation.md). No product or PoC was implemented, services deployed, messages sent or paid infrastructure used.
