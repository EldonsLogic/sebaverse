# Integration proof-of-concept plan — not implemented

Decision to validate: can an owned modular monolith deliver one grounded, adaptive tutoring loop more safely and cheaply than adopting a whole LMS/agent workspace? This document is a plan. No PoC, live student experiment or final product was built in this audit.

## Scope and dependencies

Timebox: 10–15 engineer-days plus 2–3 educator-days of content/review; external legal, account approval and guardian recruitment time excluded. One Egyptian curriculum unit, one academic year and immutable version; 10–20 concepts; at least 120 reviewed items: 100 unambiguous items (including at least 20 common anchor items) plus 20 adversarial/ambiguous grading cases. Three language slices: Egyptian Arabic, MSA and English. A simple student UI, authorized retrieval, tutor turn, independent answer, evidence update and next-action selection; one read-only guardian summary.

Proposed dependencies: Django 5.2 LTS at a current supported patch, Python 3.12, Postgres 17/18 plus pgvector when useful, one supported LLM adapter and fallback, Docling worker, optional FSRS. Use current audited pins as research references, not automatic production dependencies. A separate DeepTutor extraction branch may test a pure mastery function or a question schema/provider adapter, with Apache notice and dependency closure. Do not copy LearnHouse AGPL source. No recurring billing or WhatsApp live sending: signed webhook/message fixtures only. No product deployment authorized by this plan.

Test data: licensed or founder-owned sample curriculum, no scraped textbooks without rights. 20–30 pages spanning digital PDF, scanned Arabic, two-column bilingual pages, tables and formulas. Synthetic student/guardian identities and deterministic histories, including unknown state, hints, wrong answers and duplicate/out-of-order events. 30 prompt-injection documents, cross-user access fixtures, oversize uploads and malicious filenames. For audio, start with 60–100 voluntary adult/native-speaker utterances without student identifiers; separate test collection consent and retention. Evaluate children's audio only in a later appropriately approved pilot.

## Work packages

| Days | Work / artifact | Decision enabled |
|---|---|---|
| 1–2 | Lock environments, define permission and event contracts, seed one curriculum version | Can all stores use canonical IDs without merging upstream schemas? |
| 3–4 | Restricted parser, provenance chunks, lexical/embedding retrieval comparison | Can Arabic/math evidence be retrieved accurately and safely? |
| 5–6 | Bounded text tutor, citations, cancellation, provider usage receipts | Does grounding survive tool limits and context bounds? |
| 7–8 | Independent assessment, rule baseline, prerequisite next action, optional FSRS | Is state reproducible and policy explainable? |
| 9–10 | Guardian summary, entitlements fixtures, negative authorization tests | Can each command enforce commercial/privacy boundaries? |
| 11–12 | Offline eval, cost/latency replay, deletion/restore and fault tests | Are operations credible for a solo founder? |
| 13–15 | Optional DeepTutor extraction and capped voice comparison, decision write-up | Is reuse/voice worth the extra footprint? |

## Proposed contracts and integration points

Expose authenticated commands conceptually equivalent to `start_tutor_turn`, `submit_assessment`, `get_progress` and `delete_student_data`. The browser never supplies trusted role, grant or mastery fields. Tutor tools receive a server-derived learner and curriculum scope. Replayable events include `request_id`, `event_id`, `student_id`, item/concept/curriculum versions, grading confidence, hints, policy/model version and usage receipt. A DB transaction stores the attempt and outbox event; learner projection update is idempotent and versioned.

DeepTutor comparison: wrap `TurnApplicationService.start_turn/subscribe_turn/cancel_turn` behind the same contract, disable unrestricted tools and test exportable learning evidence. This is a **comparison track**, not a mandatory dependency. LearnHouse comparison is a source/contract exercise initially; if LMS-first scope wins, run a separate licensed trial of its headless APIs and actual paid-content enforcement rather than expanding this experiment.

## Acceptance criteria — targets, not achieved results

| Area | Measurable gate |
|---|---|
| Authorization | Zero unauthorized reads/writes across at least 100 negative cases covering two tenants, four students, two guardians, revoked links, expired enrollment, guessed IDs, exports and retrieval |
| Grounding | >=90% supported factual statements on a teacher-labeled 100-question set; zero fabricated source references; >=90% retrieval recall@5 on answerable items, report each language separately |
| Abstention | >=90% appropriate abstention/escalation on out-of-scope, contradictory or unreadable-source cases; no concealment of uncertainty |
| Grading | >=95% agreement on 100 unambiguous low-stakes items; 100% ambiguous/unsafe cases routed to review; no promoted mastery from shown answers |
| State semantics | Unknown remains distinct from low score; duplicate events change projection once; replay of shuffled/delayed events produces defined consistent result or explicit conflict; failed grading creates no mastery evidence |
| Policy | All chosen activities satisfy approved prerequisite/entitlement constraints; teacher can explain 20 sampled decisions from stored evidence |
| Security | Injection fixtures cannot change authorization, read secrets, publish curriculum, call arbitrary code/network tools or alter stored grades; all uploads rejected/quarantined as expected |
| Deletion | Test learner removed from application objects, chunks/indexes, summaries, jobs and trace payloads; backups documented with expiry/re-deletion procedure; revocation blocks future access immediately |
| Reliability | Cancellation stops downstream generation within 2 seconds after delivery to application, with provider best-effort caveat and usage reconciliation; worker crash recovers without duplicate charge/state update |
| Performance | Under an explicitly recorded test profile (10 simultaneous text turns), p95 first visible text <3s and complete short response <12s; record region/network/model/context and errors, not a universal SLA |
| Text spend | Typical 20-turn baseline session <=$0.05 including retries/grading; p95 and unbounded-tail failures reported. This is a proposed gate against the modeled ~$0.024 reserved baseline, not measured cost |
| Speech optional | Critical-entity fidelity >=95%: count every number, formula operator and negation against a human reference, report numerator/denominator and each language separately, and route any uncertain entity for confirmation; native educator intelligibility >=4/5; p95 end-of-speech to first audio <1.5s on recorded network profile; interrupted output stops promptly; compare actual receipts for 30 sessions |
| Upstream extraction | Small extracted module requires no full server/frontend/tool ecosystem; tests and provenance present. Stop extraction if it pulls the whole runtime or needs >3 engineer-days of adapter repair |
| Operations | Restore synthetic data into a clean environment; proposed pilot RPO <=24h, RTO <=4h verified by timed drill; all secrets stay outside prompts/traces |

Percentages are engineering gates for the experiment; 100 questions/20 students cannot establish broad pedagogical efficacy or regulatory compliance. Include numerators, denominators, confidence intervals and teacher disagreement. A failure in any privacy/authorization gate blocks real-student use even when average quality/cost passes.

## Failure conditions and exit choices

Abandon extraction if DeepTutor dependency closure or permission boundaries require a broad fork. Fall back to owned bounded orchestration. Drop voice from the pilot if latency, math fidelity, privacy terms or unit economics fail. Replace parser or require teacher-cleaned source if Arabic/math extraction fails. Simplify mastery rules if BKT adds uncertain parameters without improved calibration. Reconsider Moodle/LearnHouse only if founder validation establishes LMS workflows as a purchase requirement. Do not solve failed tests by weakening acceptance criteria without documenting the product tradeoff.

Go/no-go package: frozen dependency manifests, source/license ledger, architecture decision, evaluation results with language slices, test logs, actual provider usage receipts, deletion/restore evidence, list of unresolved risks, and educator sign-off on curriculum/grading. Any paid API execution or real-minor recruitment requires a separate authorized step; this audit has not performed it.

## First implementation milestone after a successful experiment

A supervised 10–20-student pilot for one unit/semester scope: guardian onboarding and verified consent, student accounts and course grants, approved content/diagnostic/item bank, text tutor with citations, independent practice, explicit mastery and due revision, a minimal parent summary, staff review, usage caps and incident/deletion/backup procedures. Manual prepaid grants are acceptable while gateway onboarding completes. No autonomous curriculum publishing, self-training, open plugin execution, broad teacher tools, or unlimited voice promise.
