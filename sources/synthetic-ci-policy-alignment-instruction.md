# U34 — Synthetic-CI pre-use policy alignment and DEV-010 PostgreSQL verification authorization

26 November 2026. Founder responses in the current Antigravity chat following read-only verification that `postgres:17-alpine` (`linux/amd64`) still ships `libssl3`/`libcrypto3` `3.5.9-r0` and `postgres:17-bookworm` carries 221 packages.

Founder selected verbatim (decision 1): “(Recommended) Authorize AUTH-022 — refine AUTH-011 for synthetic-only loopback tests so a reviewed finding expires when the official Docker image (not just upstream apk) publishes the fix, capped at 30 days, and run DEV-010's 37 PostgreSQL tests”.

Founder selected verbatim (decision 2): “(Recommended) Align synthetic-ci gate with QUALITY-BAR §2 — for loopback fake-data CI only, block KEV & unreviewed High/Critical in app-called code (don't block on Low/Medium/unreached OS CVEs), keeping the full strict standard gate mandatory before real data or deployment, and run the 37 PostgreSQL tests”.

Scope (`AUTH-022`): Applies strictly to `execution_scope == "synthetic-ci"` (disposable loopback fake-data CI and local synthetic test runs only). The full strict `execution_scope == "standard"` gate remains 100% unchanged and mandatory before any real data, user traffic, or deployment. Preserves the original 30-day `AUTH-007` OpenSSL expiry (`2026-12-18`) without extending it, keeps all KEV, Critical, Unknown, `postgres-core`, `system-native` High, and unlisted image High findings blocking, records all unreviewed Low/Medium OS findings and listed unused-feature image High packages (`libcrypto3`, `libssl3`, `libxml2`) explicitly in the report, and authorizes running DEV-010's 37 synthetic PostgreSQL integration cases on a disposable loopback PostgreSQL 17 instance with independent review before PR merge.
