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
