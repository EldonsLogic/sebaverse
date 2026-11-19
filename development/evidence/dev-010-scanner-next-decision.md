# DEV-010 scanner recovery after AUTH-009

18 November 2026 · R040/R041/R046 · prepared decision, not new authority.

The two assessed official ClamAV 1.5.4 images remain disabled. The initial Debian image has unresolved imported libxml2 findings. The one authorized Alpine alternate has different libxml2 but imports OpenSSL packages matching eight High findings in existing exact-package evidence. Vendor severity context remains recorded; the PostgreSQL exception cannot transfer. No scanner or definitions ran. Full direct advisory coverage and remaining provenance/notice review are incomplete. [Original](../../infra/scanner/review-plan.md), [alternate](../../infra/scanner/alternate-review.md).

The authorized alternate allowance is exhausted. QUALITY-BAR.md section 2 requires a founder choice before another approach. GitHub discovery found useful extraction, OCR and isolation repositories; none established a qualified free scanner runtime by itself. A wrapper retains the engine/library findings. A hardened supplier listing exists but free access/cost is unconfirmed and no contact or purchase is authorized. [Shortlist](dev-010-github-resources.md).

1. **Assess one distribution-maintained ClamAV package route (recommended).** One focused review capped at one engineering day, one package/runtime combination, with exact signed package identity, maintained source/patches/notices and native dependencies reviewed before any use. This changes packaging, not the selected malware engine or private broker. A distribution may supply fixed dependencies independently of Cisco's existing images; this is a proposal, not an observed fix or guaranteed qualification. No source compilation, scanner waiver, extra candidate hunt, paid service or execution before review. If it fails, record evidence and stop.
2. **Wait for a qualifying official supplier update.** Keep scanner and actual uploads disabled. No new dependency effort now; DEV-010 and F3 remain open on an unknown timeline. No next-phase work begins to bypass the hold.

Both options preserve safety/quality/privacy thresholds, real-data/deployment restrictions and independent review. The already authorized parser assessment can continue independently within AUTH-008's remaining budget. Neither option approves a gate or transfers AUTH-007.

Founder selected option 1 under [AUTH-010](../APPROVALS.md#auth-010--founder-distribution-maintained-scanner-package-assessment-18-november-2026). The existing image holds remain; only one package/runtime combination may be assessed.
