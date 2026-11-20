# Decision log, risks and unknowns

Decisions below distinguish founder instruction (binding within task) from proposed architecture (pending). No approval is inferred from delivery of a document.

| ID | Type/status | Statement | Resolution owner / trigger |
|---|---|---|---|
| D001 | Founder instruction | Preserve all requirements, phase scope, do not implement before baseline/architecture | Founder; all work |
| D002 | Founder instruction | Egypt-first, solo, affordability, global-ready | Founder; product/economics gate |
| D003 | Founder instruction | Use Documents/TBD; rename after chosen brand | Founder; name selected at G2 |
| D004 | Technical baseline selected under U11 | Owned modular monolith; Django/DRF + React/TypeScript/Vite + PostgreSQL | ADR001/002/010; execution gates separate |
| D005 | Technical baseline selected under U11 | Transparent evidence rules and fixed review before complex tracing | ADR003, G3/G4 |
| D006 | Technical baseline selected under U11 | Early voice benchmark, gated capped pilot | ADR005, G4 |
| D007 | Required risk containment | Quarantine inspected EduStudio pin | Independent provenance resolution; no execution meanwhile |
| D008 | Partially decided by founder (U4) | German at a national language school; learner-uploaded curriculum first. Grade/level/term/edition, explanation language and buyer remain open | Founder + educator; inspect actual uploaded materials |
| D009 | Open | Platform name and trademark/domain clearance | Founder/native review/counsel at G2 |
| D010 | Open | Monthly vs prepaid price, quotas, refund/renewal rules | Actual economics and prospect buying test |
| D011 | Open | Hosting/processing/transfer route and consent verification | Qualified Egyptian review at G3/G5 |
| D012 | Open | Model/speech providers, fallback eligibility and retention | Current terms + matched evals at G4 |
| D013 | Open | Jev adoption vs rules/small LLM | Frozen held-out comparison; stay optional |
| D014 | Open | Frontend, realtime transport, payments and CI host | G3 tradeoff and account terms |
| D015 | Open | Retention windows, incident coverage, staffing budget | G3/G5; no legal time invented |

| Risk | Severity / likelihood (judgment, not statistics) | Mitigation / trigger | Owner |
|---|---|---|---|
| Missing older context | High / known partial | GAP-001 before baseline sign-off; U2 already restored | Founder |
| Scope exceeds solo capacity | High / high | One unit, gates, review capacity and explicit future phases | Founder |
| Content or weight/dataset rights unavailable | High / unknown | Artifact rights ledger; replace or narrow sources | Founder/counsel |
| Cross-child data leak or invalid consent | Critical / unknown | Deny-by-default tests, legal route; block minors on failure | Founder/security/privacy |
| Incorrect grade/hint inflates progress | High / plausible | Reviewed keys, assistance types, appeals/quarantine/replay | Educator |
| Arabic OCR/math/voice failure | High / unknown | Critical notation benchmark, confirmation and text/cleaned-source fallback | Educator/engineering |
| Voice/FX/heavy-tail costs destroy margin | High / plausible | Caps, actual billing, sensitivities and plan redesign | Founder |
| Dependency compromise/license conflict | Critical / plausible | Exact pins/provenance, quarantine, resolved scans and license review | Engineering/counsel |
| Cold-start learned classifier/KT unreliable | Medium/high / plausible | Rules baseline, calibration and optional shadow use | Educator/engineering |
| Safeguarding workload beyond availability | High / unknown | Named coverage/protocol and truthful service hours | Founder/safeguarding owner |
| Market interest fails to convert | High / unknown | Paid pilot proposition after lawful readiness; track refunds/active ratio | Founder |
| Unproven efficacy marketing | High / avoidable | Independent delayed outcomes, uncertainty and claims review | Founder/educator |

Unknown register resolution must attach evidence, date and affected requirement/ADR. Financial unknowns are machine-readable nulls in economics/inputs.json. Technical unknowns become bounded tests; legal and rights unknowns require owning-source/qualified review, not a model's guess. No task duration estimate resolves external lead times.

## Founder update — 10 November 2026

D016 — Confirmed instruction U5: name the platform, choose logo and slogan, and create brand guidelines next. Explore brand directions now; no final name/artwork is selected. Branding is for the broader adaptive tutoring platform, with German as the first use case.

## Brand exploration update — 11 November 2026

D017 — U6: Maat is the active exploration, including Maat AI / The Maat and related descriptor forms. Not selected, cleared or approved. Earlier round-1 naming/logo directions were rejected; preserve them as history rather than an active shortlist. [Exploration](../outputs/maat-exploration/README.md). Domain status unresolved; current education uses require review. TBD remains the project name.

## Founder-selected name — 11 November 2026

D018 — U7: Sebaverse selected for brand development, superseding Maat as active exploration. Egyptian N14 star inspiration requested. Both generated logo rounds rejected (coastal/diving; Converse/sportswear associations). Palette, logo and slogan remain open; full G2 not approved. No domain purchased or name clearance established. Physical folder remains TBD pending safe app-project path update, not a second project.

D019 — U8 confirmed: Arabic-first experience and Latin-only Sebaverse wordmark. Three new independent identity trials delivered; full G2 and choice of logo, type, palette and slogan remain pending.

## D020 — C identity direction selected (U9)

Founder selected Claude C / Bāb as the identity direction, rejecting its original palette. Compare B blue/orange with the attached blue/lime palette using identical C geometry, typography and layouts. Final palette and full G2 approval remain open. No product implementation authorized.

## D021 — Blue/orange selected; visual metaphor is not wording (U10)

Founder selects B blue/orange for C visual identity. Supersedes the open palette question in D020. “كل سؤال باب” and door-based product terminology are not selected. Brand-system v1 documents this combination; new copy and component details remain proposals. No permanent slogan or full G2 approval inferred. Founder authorizes rename of existing folder to Sebaverse, preserving Git history.

## D022 — Subject-independent finalized technical baseline (U11/U12)

Founder instructs finalization now and rejects dependence on a German curriculum. Engineering selects architecture/technical-baseline.md and ADR-001–012 as concrete technical decisions for audit. Finalized means design choices/boundaries, not test results, founder endorsement of unseen details or approval of whole execution/legal/deployment gates. R095 retained as one first-use example.

D023 — React/TypeScript/Vite static web app with React Router/TanStack Query, same-origin Django/DRF backend, REST/SSE selected; supersedes D014 frontend/text-transport uncertainty. Payment gateway and production host/region remain unresolved.

D024 — Ready libraries and all 22 audit dispositions fixed in repository-adoption.json. No entire tutoring/LMS adopted; DeepTutor reference-only baseline; bounded optional extraction. Exact install releases, transitive/model/data rights and security closure remain pre-install conditions, not unspecified application architecture.

D025 — External audit handoff U12 covers all 99 requirements, data/runtime diagrams, feature/functions, phases, source lineage, decisions and unknowns. No external message sent.

Current unknown separation: exact dependency locks (before install); live-call time/spend cap and eligible processor/data mode (before live PoC); region/provider/retention/guardian process, actual rights and operational coverage (before affected real data/pilot); production model winners and Jev/voice/local GPU choices (after matched evidence). None requires a specific school textbook to complete platform design.

## D026 — Shared development foundation and GitHub authorization (U13)

Founder accepts current direction for foundation work and names private EldonsLogic/sebaverse as shared Git source of truth. Roadmap/task/handover/check tooling and verified commits/pushes are authorized. Preserve local history; do not invent wider execution/legal/live-spend/deploy/minor approvals. development/APPROVALS.md records exact scope.

D027 — Incorporate pinned multica coding principles and user image into shared root rules; source license unknown so four ideas are paraphrased, not vendored. Image transcribed and original/hash retained. Thirty contracts are capabilities; only actual needed agents are activated and reported. Frozen exported rules do not govern active development.

D028 — U14 requires tests/review after EVERY phase, with recorded actual evidence and no next-phase start until pass. development/phase-gates.json and tools/check_foundation.py make missing/failing/not-run evidence and premature progression checkable. Never lower gates to manufacture progress. Product phase test suites remain required and unrun until implemented.

D029 — F0 foundation verification complete, 11 November 2026: 14 local contract/negative tests, document/economics/foundation checks and actual independent review passed. Private GitHub main publication matched local SHA 98590747ba7f04be28c4dbb704a92e373706620d; hosted run 43047681839 succeeded. All four foundation tasks complete and phase F0 passed; F1–F8 not started. This grants no additional legal, paid-provider, deployment or minor-processing permission. Evidence: development/evidence/.

D030 — U15 starts F1 under AUTH-002: exact minimal backend/web locks, public registry/notice/advisory inspection, isolated wheel-only/lifecycle-disabled local installs and compatibility checks. F0 was passed before DEV-005 started. Parser/OCR/models remain disabled at original adoption phases, not falsely cleared. Native DB/network/image version/CVE/notice closure is a required F2-before-use check, and distribution obligations remain release blockers. F1 is not passed until actual clean Linux CI and final review evidence exist.

D031 — Scoped F1 passed on11 November2026: DEV-005 exact backend/web locks, actual local smoke/known-advisory checks,22 regressions, independent review and clean Ubuntu CI43052547533 succeeded on ba2edb2df95ce584f9408e4a3822b7ec91a60f8c. Native DB/network/image notice/version/CVE closure remains before F2 use; redistribution and parser/model/real-data gates remain separate. F2–F8 not started. No blanket legal/security/production approval.


RISK-F3-001 — 17 November 2026: current dependency readiness regressed during DEV-007 integration. Existing picomatch 4.0.7 is affected by GHSA-fc5q-39xc-vjpf (upstream lists no patch); native pre-use scanning also requires review of 24 new findings. No exploit or child-data exposure is established. DEV-007 remains in review and DEV-008 is held pending compatible fixes or an explicitly reviewed scoped decision. Owner: engineering for patch/impact assessment; founder for any proposed exception. Evidence and exact hosted runs: development/evidence/dev-007.md. Historical F1/F2 results are not refreshed clearance. Update, 17 November: AUTH-005 exact temporary synthetic-only exceptions passed independent review and all hosted checks at c38bb04; DEV-007 is done and DEV-008 may start. Advisories remain unresolved, expiry and real-data/production restrictions remain in force. See development/evidence/auth-005-advisory-review.md.


RISK-F3-002 — 18 November 2026: DEV-009 hosted integration is held by newly observed High OpenSSL matches in the pinned PostgreSQL image. Compatible current official amd64 image/Alpine package paths still contain 3.5.9; upstream lists 3.5.10 fixed. AUTH-005 does not waive these High matches. No database/resilience execution or DEV-010 progression is allowed. Engineering prepared a bounded alternative official PostgreSQL 17 image assessment versus waiting for Alpine fixes; founder chooses the next approach after the current repair budget. Evidence: development/evidence/dev-009-runtime-recovery.md. No compromise or real learner exposure is established.


ADR-013 / U19 — 18 November 2026: founder requested AG-UI integration. R105, architecture/ag-ui-integration.md and DEV-013 define a minimal adapter while preserving Django/React, validated content, deterministic authority and durable REST/SSE. Exact SDK/lock adoption and activation remain gated; no package or product integration has run. Upstream evidence is pinned at 3416b86da4b3288e87f827c7f2759a7fa18b5231; benefits and dependency delta are unmeasured.


RISK-F3-002 update — AUTH-006 static assessment completed on 18 November in run 44294630688; both allowed official PG17 alternatives contain blocking matches, including native non-Go components. No pin/gate change or database use. DEV-009 remains in review; no third candidate is authorized under this budget. See development/evidence/runtime-candidate-assessment.md.


RISK-F3-002 update — 18 November: AUTH-007 explicitly permitted the exact independently reviewed synthetic-only OpenSSL exception. Hosted gate/actual PostgreSQL/browser tests at bc211558 passed, and independent execution review released DEV-009. Findings remain unresolved; exact expiry/source/artifact/CI constraints remain. This supersedes the integration hold, not the historical scan findings, candidate rejections or production restrictions. See development/evidence/auth-007-openssl-review.md.


RISK-F3-001 update — 19 November 2026: live npm audits in production and synthetic-development report zero findings after the advisory withdrawal. AUTH-005 is unused. A reviewed fail-closed checker correction does not change or rebind its policy; recurrence would invalidate the dormant source binding until separately authorized review. Evidence: development/evidence/integration-2026-11-19.md.

AUTH-011 / U21 — Founder-approved expiry and runtime/build binding amendment is merged in PR #3. Existing dates/findings/scopes are preserved; released fixes end reviews immediately with a 30-day backstop. Active dates are in CURRENT-STATE.md and the original JSON, not superseded historical expiry prompts. No scanner exception is granted.

RISK-F3-003 — 19 November 2026: the hosted runner already has the exact approved libc6 version, but the upgrade-only preparation script rejects an empty transaction. Actual run 44510517163 failed before database use. Push plus pull_request triggers duplicate checks/notifications. This is synthetic CI availability/noise, not established application breakage or exposure. A narrow exact-package repair is being prepared in scratch; bound security helpers and source maps remain unchanged pending reconciliation of the founder’s no-rebind instruction. No checks are suppressed or counted as passing. Owner: root engineering; evidence: development/evidence/integration-2026-11-19.md.


RISK-F3-003 update — Founder AUTH-012 explicitly authorizes the prepared exact six-package same-version reinstall repair and only its two AUTH-007 helper source hashes. Dates/expiry/findings/pins/thresholds stay unchanged. Local 179 helper tests pass; actual hosted repair is pending. Duplicate triggers are still present and no notification settings were changed. See development/evidence/ci-native-reinstall-proposal.md.


RISK-F3-002 update — 19 November: AUTH-011 fix trigger is active and correctly blocks the original image after official Alpine package/security metadata confirms OpenSSL 3.5.9-r1. Run 44512249851 ended eight High and two Medium package matches; actual PostgreSQL/browser skipped. Package availability does not qualify an image or authorize renewing the old exception. See integration-2026-11-19.md.


ADR-014 / U23 / AUTH-013 — 19 November: founder selected a same-engine direct PyPDFium2 adapter for the first authored text-only PoC. The disabled owned core and fake-engine tests received independent review. The SDK range API’s UCS-2/index limits cause conservative holds; soft deadlines do not stop native hangs. Runtime/native/scanner/OS/fidelity qualification and all R039 capabilities remain required. Evidence: development/evidence/dev-010-direct-adapter.md. No phase approval or SDK activation.


RISK-F3-004 — 20 November 2026: production worker signing/verification and job credential provisioning remain unresolved. The authored stdin experiment uses fixed synthetic HMAC keys; sharing a verification key also confers signing ability. Those fixtures do not establish independent scan authority in an untrusted production worker. Before activation, preserve parent/broker authority and independently qualify one-object input capability, verification and credential provisioning. Owner: architecture/security; status: open, runtime activation blocked; evidence: development/evidence/dev-010-authored-input.md and workers/parser/input-transport-plan.md. No production design or exception approved.
