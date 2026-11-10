# Product vision and PRD v0.1

Status: proposed specification for review. Founder sources U1 (master request), U2 (context restoration), U3 (TBD project-folder instruction). Research sources G04–G10 and A07–A13 inform recommendations; they do not override founder scope. No brand, first curriculum or stack is finally selected.

## Product promise and strategy

An affordable, curriculum-grounded tutor that helps a learner understand a problem, practice independently, remember it later and know what to study next. The conversational tutor is the interface to an adaptive learning platform; its learner evidence, curriculum identity and teaching policy persist independently of whichever generative provider answers a turn.

Start in Egypt. Use Egyptian Arabic for approachable explanation, MSA for formal academic language, and English for language-school terminology and chosen instruction. Keep one concept layer with explicit mappings to distinct curricula. National Arabic, national language, IGCSE, IB and American pathways require separate reviewed mappings, content rights and assessment practices. An English translation does not establish international alignment.

Founder constraints: solo operation, affordability, approximately 100 interested prospects, supervised family/friends pilot, pricing hypotheses EGP 300/month or EGP 300–500/course/semester. These are founder-reported inputs and hypotheses, not verified revenue, commitments or market evidence. Protect a narrow first learning loop from feature breadth while retaining all future requirements in the register.

## Users and jobs

| User | Job / trigger | Successful outcome | Boundary |
|---|---|---|---|
| School student, exact age/grade open | I am stuck and need an explanation in my language | Can solve a different problem unaided and explain a step | Support without presenting generated praise as mastery |
| Student preparing for exams | I need a realistic plan and practice | Approved objectives covered; timed practice and independent follow-up | Mock-exam claims require actual syllabus and marking alignment |
| Parent/guardian, initial buyer hypothesis | I need affordable help and trustworthy progress | Understands evidence, uncertainty, next step, usage and charge | Does not receive unrestricted private chat by default |
| Educator/content reviewer | I need to correct bad materials and grading | Review queue, affected-version quarantine and replay of corrections | Staff access is scoped and audited |
| Teacher/school, future segment | I need assignments and class support | Scoped roster, assignment, override and aggregate progress | Institutional authorization and tenant model must be agreed |
| Founder/operator | I must sustain safe service alone | Cost caps, incident queues, restores and support load are manageable | No claim of continuous human monitoring |

## Narrow pilot candidate and scope

Candidate: one Egyptian curriculum, one grade/age band, one subject, one unit/semester edition, 10–20 supervised learners. Mathematics is a useful PoC candidate because reviewed answers can be checked, but is not selected on the founder's behalf. Choose based on rights, educator access, prospect needs and operational budget at G1.

Pilot core: verified guardian/student relationship; onboarding and consent; approved content; diagnostic and explicit unknown state; bounded grounded text dialogue; original reviewed exercises; independent checks; prerequisite remediation; simple mastery/evidence view; fixed expanding review schedule; minimal parent dashboard; manual course grants if gateway approval pending; upload ingestion with human approval; usage/incident/deletion/backup controls. Voice is tested in the PoC from the outset and included as capped pilot functionality only if its gates pass. This preserves voice as a core requirement while making exposure conditional on evidence.

Future retained scope: larger interactive lesson/manipulative library; photo and diagram interpretation; advanced personalized exam planning and mock exams; automated but reviewed custom curriculum mapping; WhatsApp delivery; broader teacher/class/school workflows; international curriculum authoring; BKT/IRT/deep KT benchmarks; Jev production use; local GPU deployment; optional separately controlled model training. None is silently removed.

## Functional specifications

Each tutoring activity has a syllabus objective, reviewed item/content versions, accessibility needs, language, activity mode and valid next actions. A student can ask for a hint, explanation, worked example or prerequisite check; a shown answer marks subsequent evidence assisted. Independent mode clearly announces that hints are unavailable for that check and permits skip/I don't know. The student can dispute a grade or report unclear/unsafe content. Failed or ambiguous scoring does not change mastery.

Progress shows evidence-backed statuses, last check and what is due, with an understandable reason for the next activity. Confidence volunteered by the student is separate from model uncertainty. Parent summaries describe demonstrated skills and suggested support, avoiding intelligence scores or permanent labels. An exam plan covers approved objectives, student availability, due review and uncertainty; timing and accommodations are explicit.

Uploads remain private by default. The uploader sees rights declaration, page/size quota, processing/review status, mapping uncertainty, accepted version and deletion control. Replacing a document creates a new version and never silently changes the sources of earlier answers.

## Nonfunctional product requirements

Mobile-first responsive browser experience, low-bandwidth text fallback, RTL/LTR mixed mathematical content, keyboard/screen-reader operation, explicit recording controls, bounded latency and cancellation, resumable lesson checkpoints, and accessible error messages. Proposed quality/performance targets live in the QA plan; they are acceptance gates, not existing measurements. Payments, consent and mastery authority stay server-side. Feature flags allow disabling a faulty topic/provider/voice mode without deleting evidence.

## Success and failure

Primary educational endpoint: independent delayed performance on unseen item families aligned to approved objectives. Proposed observation windows: baseline, near-transfer same session, delayed 7-day and 21-day checks where feasible; educator decides final protocol. Operational endpoints: grounded correctness, grading agreement, parent comprehension, completed independent activities, cost per such activity, support minutes/learner and retention/attrition. Engagement is diagnostic, not proof of learning.

Pilot continuation requires no unresolved critical safety/privacy failures, acceptable content/grading in each language, actual economics within a founder-approved ceiling and an educator-reviewed learning result. Tiny samples produce descriptive uncertainty, not claims of causal grade improvement. Stop an affected topic for a material answer-key error; stop real-student use for isolation/consent failures.

## Commercial hypotheses

Compare monthly plan against prepaid course/semester entitlement. State the course, active months, included text/page/voice quotas, renewal/refund rules and expiry before payment. Validate buying intent with the existing prospects rather than count interest as conversion. Avoid unlimited premium voice and hidden overages. Growth candidates are trusted parent referrals and educator-supported pilot expansion; no unverified acquisition-cost target is assumed. Use manual prepaid grants if recurring collection is unavailable, with clear receipts and reconciliation.

## Review gates

G0 source audit complete except GAP-001. G1 founder baseline, first slice, buyer, budget and metrics approved. G2 naming/brand/design reviewed. G3 architecture, rights/privacy and PoC protocol approved. G4 bounded synthetic/adult PoC passes. G5 real-student pilot permission/readiness. G6 commercial readiness. Implementation is not part of v0.1 delivery.
