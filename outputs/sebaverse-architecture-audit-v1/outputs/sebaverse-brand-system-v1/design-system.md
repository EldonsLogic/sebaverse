# Sebaverse product design system — v1.0

Applies to R010, R095–R098; requirement register remains authoritative. Source U10. Specification and static component documentation only. No product implementation or gate approval.

## Foundations and layout

Use tokens.json as the canonical role map and system.css as the reference implementation. 4px spacing base; 8/16/24/32px common gaps. Page gutters 16px mobile, 24px tablet, 32px desktop; max container 1200px. Mobile single column; tablet 8-column planning grid; desktop 12, with 24px gaps. Keep the study canvas primary, source/help supplementary. Mobile navigation has at most four primary destinations and descriptive labels. Sticky composer must not cover content or keyboard controls.

RTL is document direction; use logical properties (inline-start/end), never mirror Latin logos, media play icons, German words or numerical equations blindly. Use bdi/dir=ltr for German and Latin IDs. Maintain DOM reading order for assistive technology. Directional back/next arrows follow navigation context. Dates and numbers follow locale while curriculum quotations preserve original notation. Never manually reverse strings.

## Component contracts

| Component | Variants / states | Required behavior and acceptance |
|---|---|---|
| Button | Primary, secondary, quiet, destructive; default/hover/focus/pressed/loading/disabled | 48px recommended height, 44px target minimum; explicit verb; one dominant primary per task; loading keeps width and label; prevent duplicate submit; disabled is explained nearby |
| Link | Inline, navigation, external | Underline in prose; focus visible; external destination clear; no generic “click here” |
| Input / textarea | Empty, entered, focus, invalid, disabled, read-only | Persistent label; hint and error associated programmatically; do not rely on placeholder; preserve input after failure; min 16px font |
| Select / checkbox / radio | Default, checked, focus, invalid | Native semantics; full label target; consent never prechecked or bundled with marketing |
| Upload | Idle, selected, uploading, scanning, needs review, ready, failed, cancelled | Disclose supported formats/limits from actual configuration; show filename/progress; cancel; no learning/retrieval until quarantine and permission checks pass; separate scan from OCR readiness |
| Curriculum card | Not started, in progress, version changed, unavailable | Name/edition/version/source visible; resume targets last eligible step; do not claim upload completion equals learning |
| Source citation | Collapsed, expanded, missing, version mismatch | File + page/section + version; opens accessible excerpt; distinguish tutor inference from quoted source; invalid locator cannot appear verified |
| Tutor message | Tutor, learner, hint, feedback, unknown, error | Sender label and logical order; German isolated; source shown where relevant; no fabricated citations; feedback marks assisted vs independent |
| Composer / voice | Idle, permission request, listening, transcribing, sending, stopped, failed | Text alternative always available; explicit start/stop; visible recording state; no auto recording; preserve draft; quotas and cancellation visible |
| Progress | No evidence, independent, assisted, exposed, ambiguous | Label evidence type; no fake mastery percentage; deterministic projection contract; never color alone; parent view separates engagement from demonstrated learning |
| Alert / toast | Info, success, warning, error | Inline for task blockers; toast for nonblocking confirmation; aria-live polite for status, assertive only urgent errors; no auto-dismiss critical actions |
| Dialog / sheet | Confirm, destructive, source, settings | Accessible name, focus trap, Escape where safe, restore focus, keyboard reachable close; destructive action names object; drawer stacks at mobile |
| Tabs / navigation | Selected, focus, unavailable | Semantic roles and keyboard behavior; active state text/icon plus color; no hidden focusable content |
| Card / table | Loading, empty, populated, error | Skeleton respects reduced motion; table headers/caption; horizontal overflow accessible; mobile card view preserves labels |
| Pagination / filter | Default, active, empty | Query state restorable; clear filters; announce result count without noisy live updates |

## Student journeys and failure recovery

1. Entry and appropriate account/guardian route → choose German → upload owned/authorized curriculum → quarantine/scan → extraction review → confirm level/edition/units → ready. Acceptance: each stage has a recoverable error and accessible status; uncertain OCR/pages are flagged, not accepted silently. Consent and permission state server-owned.
2. Select a reviewed lesson → see source version and goal → short diagnostic → explanation/hint/practice → reviewed feedback → independent follow-up → recap. Acceptance: assistance evidence stays distinct; an answer shown or hinted cannot become independent evidence; learner can open the cited page.
3. Voice: choose microphone → appropriate permission → recording indicator → stop/cancel → editable transcript → send → response. Acceptance: denied/failed speech falls back to text; no hidden recording or implied unlimited voice. Processing/retention disclosure comes from approved policy, not draft branding.
4. Parent: authorized child switch → curriculum/status → independent/assisted evidence → practical suggested next step → privacy/consent settings. Acceptance: no cross-child leakage, no unsupported attainment claims, no default raw transcript feed. Teacher interfaces remain future scope and use explicit permission boundaries.

## Accessibility and interaction criteria

Target WCAG 2.2 AA, pending product audit. Normal text contrast at least 4.5:1, large text and meaningful UI boundaries at least 3:1. See contrast-report.json for measured candidate pairs; this is color arithmetic, not complete accessibility testing. Focus 3px blue with 3px offset on light surfaces; on blue/dark use a white inner ring plus blue outer ring. Never obscure focused controls. Support keyboard, screen reader names, 200% zoom, reflow at 320 CSS px, reduced motion and error summaries. Avoid drag-only actions and timed learning penalties. No confetti or streak guilt by default. Illustrative UI may show draft/static values; production data must be derived from authorized records.

## Implementation handoff and release checks

Use semantic HTML before ARIA. Adopt framework components only after G3; no framework chosen here. Token names are stable API; avoid raw hex in feature code. Each future task cites requirement IDs and acceptance criteria from registers/requirements.json. Component props should express state, accessible label, action and error; never let a model choose authorization, consent, price or mastery state.

Before implementation: founder reviews copy/logo optical refinements; educator reviews German examples; confirm upload limits and source inspection; complete G1–G3. Before pilot: full RTL/screen reader/contrast/keyboard/mobile audit, consent/privacy and rights approvals, provider/cost limits, QA/evals. Documentation acceptance: asset files open, tokens parse, local links resolve, source hashes preserved, both required project checks pass.
