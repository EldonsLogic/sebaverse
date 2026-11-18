# Sebaverse development roadmap

Version 1.0 · 11 November 2026. U14 requires actual tests after every phase and a passed, evidence-backed exit gate before the next phase. Current work establishes the development foundation and GitHub-backed handover system under U13. The selected technical architecture remains Django/DRF, a static React/TypeScript/Vite client, PostgreSQL/pgvector and private object storage with isolated parsing. No product implementation or paid/live test is claimed by this roadmap.

The [task register](tasks.json) is the execution queue. The [requirements register](../registers/requirements.json) remains the authority for scope and acceptance; the [complete feature/function matrix](../architecture/feature-function-matrix.md) retains every existing and future feature. Do not restart stack selection or wait for a particular German textbook. A new supported subject uses reviewed versioned profiles, content and grading configuration; specialist capabilities use reviewed adapters.

## Mandatory phase test gates

The execution stages F0–F8 below map to the existing architectural A phases without renumbering them. [Phase gates](phase-gates.json) are the authority for required exit checks and recorded status. **After every phase, run its required tests, review the results and record evidence. Do not begin the next phase until that gate passes.** A future test command, a generated report template or an agent assertion is not a pass. A failure/missing test keeps the gate unpassed; fix and rerun the affected checks before promotion. Do not weaken a required safety/privacy/quality check to move forward.

| Stage | Architectural equivalent | Tasks | Exit verification category |
|---|---|---|---|
| F0 Development foundation | A1 documentation/workflow | DEV-001–004 | Source/requirement/task/agent-rule validation, handover consistency, actual GitHub sync evidence |
| F1 Execution readiness | A1 dependency/approval readiness | DEV-005 | Resolved dependency/notice/security/model-rights checks and recorded applicable execution scope |
| F2 Runnable skeleton | A2 initial scaffold | DEV-006 | Reproducible clean local startup, backend health/client build and smoke checks |
| F3 Identity and content | A2–A3 contracts, access, jobs, upload/retrieval | DEV-007–012 | Contract tests, authorization negatives, ingestion/versions and scoped retrieval/citation checks |
| F4 Tutor and evidence | A3 learning loop/UI/operations | DEV-013–016 | State/cancellation/replay/grading/projection, accessible UI, privacy/restore and regression checks |
| F5 Comparisons and voice | A4 | DEV-017–021 | Matched eligible comparisons, actual receipts, language/voice slices and PoC exit review; honest not-run optional work |
| F6 Supervised pilot | A5 | DEV-022 | Actual G5 readiness plus authorized content/consent/support/privacy/learning-outcome review |
| F7 Commercial hardening | A6 | DEV-023 | Actual G6 readiness plus payment/refund/messaging/load/security/operations checks |
| F8 Expansion | A7 | DEV-024–026 | Feature-specific regression/rights/quality/cost and controlled-release checks |

All product-phase results are currently untested, not passed. Work may prepare later documentation, but no implementation task in a later stage becomes active or complete before the preceding required gate passes. The orchestrator records scope, exact commands, date, output/verdict, reviewer, failures and the gate decision. Tests appropriate to the phase are mandatory; documentation arithmetic alone cannot satisfy a product runtime test.

## How development proceeds

Use small vertical slices with observable acceptance, not a large code dump. Before work, read the current handover, task and relevant requirement/ADR; inspect the checkout and claim a bounded file scope. Implement only that task, run its actual checks, request independent review where warranted, record evidence and commit a coherent change. Verify the pushed branch and SHA separately from the local commit. Another agent should be able to resume from committed state without relying on this chat.

The task states are `planned`, `ready`, `in_progress`, `review`, `blocked` and `done`. A ready task has its dependencies, applicable authorization and input contracts satisfied. A completed task has the promised artifacts and actual acceptance evidence, not merely a generated plan. Failure, not-run comparisons and limitations stay visible. Future test commands in the register are specifications to implement; they are not currently available or passed checks.

Current authorization covers development documentation, project rules, repository connection and commit/push workflow. It is not a silent approval of every G1–G3 execution condition, paid provider calls, production deployment, external messaging or real-minor data. [Gate records](../execution/roadmap-and-gates.md) distinguish those choices. Readiness work should make the next permitted slice concrete, rather than manufacture sign-off or repeatedly ask the founder to restate settled decisions.

## 1. Development foundation — F0 / A1, DEV-001 to DEV-004

First connect the original repository to the specified private GitHub project, preserving its existing local history and any remote work. Establish one source of truth rather than a duplicate master. Record how agents fetch, branch, claim work, commit, push and recover from conflicts without force overwriting another agent.

Incorporate the requested coding principles and image-based orchestration guidance with exact provenance and limitations. The operational rules must be agent-neutral: Codex, Claude, Antigravity or another agent follows the same project authority and handover contract. Thirty role contracts describe available responsibilities; only the actual workload justifies active agents. Independent tasks may run in parallel with disjoint ownership, while dependencies and integration remain sequential. F0’s four preparation deliverables have no task-to-task dependency; the orchestrator integrates all four, verifies the private push and closes the common phase gate before F1.

Prepare the development queue, session checkpoints, evidence records and approval boundaries. Exit: repository identity and pushed state verified; one documented startup route; consistent task states and file ownership; clear next task, blockers and actual checks. These are documentation/workflow results, not a product or live agent platform.

## 2. Dependency and execution readiness — F1 / A1, DEV-005

Resolve exact compatible dependency releases and container/toolchain versions within the selected architecture. Separate the lightweight web runtime, parser environment and offline evaluation tools. Record notices, transitive dependency/security review and model/data/asset rights. The repository-adoption register fixes integration boundaries: no wholesale tutoring/LMS foundation, DeepTutor reference-only unless a bounded extraction proves useful, and the audited EduStudio pin remains quarantined.

Confirm the authorized local synthetic scope and timebox. Keep live-call spending null until an explicit cap and eligible providers/data are recorded. Local fixtures do not require a real school textbook. Exit: reviewed reproducible dependency plan plus applicable execution decisions. The task does not approve production providers, legal processing or commercial terms.

## 3. Runnable local foundation — F2–F3 / A2, DEV-006 to DEV-009

After the applicable execution decisions, create the smallest runnable backend and Arabic-first client shell, local services and documented start/check/teardown commands. Keep business authority in Django, use same-origin session/CSRF controls and serve static React assets without adding a second Node backend.

Define versioned subject, curriculum, source, item and rubric contracts using three authored subject fixtures. Build actor/learner separation, guardian/consent and course-grant boundaries before private data flows. Then implement durable jobs, usage reservations, lease fencing and cancellation with mock provider adapters. Exit: repeatable local startup and meaningful contract, authorization, state and crash/replay tests. No real children, real payments or paid model key is needed for this stage.

## 4. Multi-subject learning slice — F3–F4 / A3, DEV-010 to DEV-016

Implement private upload through quarantine, scanner and restricted parser before curriculum publication. Record source versions, page anchors, extraction confidence and rights; the coordinator validates parser output. Private-ready material and shared built-in publication have different approval paths. Preserve edition/profile versions and live access checks even when sessions are pinned.

Build scoped lexical/dense retrieval and citation resolution, then the bounded tutor state machine. Keep diagnostic, explanation, guided help, independent practice, grading, review and cancellation explicit. Models propose content and allowed tool inputs; they never write permissions, payments, consent or mastery.

Add reviewed assessment and a replayable evidence ledger. Independent, assisted, exposed and ambiguous responses stay distinct; uncertain grading waits for review. Recall scheduling is separate from mastery. Complete learner and permitted parent views with source inspection, Arabic/German/English isolation, keyboard/focus behavior and responsive layouts. Add privacy export/deletion, minimized telemetry and restore/release procedures.

Exit: the same loop runs language, quantitative and science fixtures without subject-specific schema/state-machine changes. Test private overlay, two scopes, old/withdrawn editions, prompt injection, cancellation, duplicate grading, projection correction and deletion/recovery. Engineering targets and failures are reported by subject/language; no claim follows that all global curricula work.

## 5. Comparative evidence — F5 / A4, DEV-017 to DEV-021

Only within separately authorized data and spending limits, compare qualified provider routes and actual context/cache/token costs. Benchmark rules against eligible classifiers/small LLMs/Jev on frozen adjudicated cases; keep the decision layer in shadow until its quality, safety, cost and maintenance benefit is demonstrated.

Voice starts with explicit push-to-talk and text fallback. Use licensed/consented adult fixtures before any child speech. Measure dialect/code-switching, critical entities, cancellation, latency and actual bills. Native realtime or local serving is a comparator, not an assumed bargain. A bounded DeepTutor extraction or specialist-grading spike must retain exact source/notice/dependency evidence and stop if it drags in the full runtime or exceeds its approved timebox.

Prioritize a safe runnable baseline over fitting every optional experiment into the proposed 15-engineering-day PoC envelope. Record an authorized not-run disposition when a comparison cannot execute; never synthesize a result. Exit: a concrete PoC report with task-level passed/failed/not-run evidence, costs, unresolved blockers and a pilot recommendation. Critical privacy, isolation or safety failure blocks pilot despite favorable averages.

## 6. Supervised pilot — F6 / A5, DEV-022

Real content and users require the applicable G4/G5 evidence and permissions: reviewed materials, verified guardian/consent route, eligible processing, grants/quotas, privacy/deletion/recovery, safeguarding and support ownership. The first course can be any approved subject. German remains an initial example, not a platform dependency.

Pilot outcomes separate independent delayed learning from engagement. Report support effort, failures, attrition and uncertainty rather than promises of grade improvement. A prototype or synthetic benchmark does not establish educational efficacy. Exit: recorded readiness, authorized cohort scope and actual evidence supporting continuation or revision.

## 7. Commercial hardening — F7 / A6, DEV-023

Add the approved payment gateway, signed deduplicated collection/refund events, explicit entitlement rules, opt-in minimal notifications and commercial operations. Verify load, security, accessibility, backup/restore, deletion and incident coverage before the corresponding release. Prices, voice/page/token quotas, renewal/refund terms and full unit economics must use current account terms and measured costs. No hidden unlimited voice promise or assumed merchant enablement.

## 8. Expansion and controlled improvement — F8 / A7, DEV-024 to DEV-026

Keep richer interactive lessons, mock exams, exam preparation, multimodal source interpretation, teacher/classroom tools and more curricula visible. Revisit an LMS only if institutional demand justifies its integration/rights burden. Evaluate local/realtime voice, statistical learner models and optional model training only when representative lawful data and matched evidence support them.

Maintain three separate loops: individual adaptation from validated evidence; system corrections through triage, frozen evaluation and reviewed releases; and separately authorized offline model improvement. No automatic identifiable child-chat training or self-modifying production tutor. Promotion requires measured benefit and rollback. The complete requirements/function matrix remains the coverage check, so a future phase never becomes a silent omission.

## Immediate next action and handover

Finish and verify DEV-001 to DEV-004, recording actual evidence and pushed state. Run and pass the complete F0 exit gate before activating DEV-005. Pass F1 readiness checks before installing/scaffolding the product under the recorded execution scope, and continue the same test-before-next-phase rule through F8. Every session ends with the task state, changed files, actual checks, branch/commit/push status, unresolved risks and one exact next step. Dates and completion estimates are planning inputs, not a fixed launch promise.

## U19 integration direction — 18 November 2026

DEV-013 includes R105/ADR-013: integrate AG-UI at the tutor/interface boundary after its existing dependencies and F3 exit. Read architecture/ag-ui-integration.md before package selection or implementation. No current phase or gate is bypassed; SDK provenance/rights/security and the compatibility comparison precede activation.
