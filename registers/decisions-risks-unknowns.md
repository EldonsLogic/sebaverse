# Decision log, risks and unknowns

Decisions below distinguish founder instruction (binding within task) from proposed architecture (pending). No approval is inferred from delivery of a document.

| ID | Type/status | Statement | Resolution owner / trigger |
|---|---|---|---|
| D001 | Founder instruction | Preserve all requirements, phase scope, do not implement before baseline/architecture | Founder; all work |
| D002 | Founder instruction | Egypt-first, solo, affordability, global-ready | Founder; product/economics gate |
| D003 | Founder instruction | Use Documents/TBD; rename after chosen brand | Founder; name selected at G2 |
| D004 | Proposed | Owned modular monolith, selective reuse; Django/Postgres candidate | ADR001/002, G3 |
| D005 | Proposed | Transparent evidence rules and fixed review before complex tracing | ADR003, G3/G4 |
| D006 | Proposed | Early voice benchmark, gated capped pilot | ADR005, G4 |
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
