# U21 — Synthetic security exceptions end on a released fix

18 November 2026. Founder decision in an active Claude Code session. The founder asked why the security exceptions expire and to fix it, then chose this option from three presented:

> "Expire on fix (Recommended): Exception ends automatically the day a fixed version is released, with a 30-day backstop instead of 3. Bind only to the files that matter (lock files, build config, DB image), not every app file. Exact versions, test-only scope and production block stay."

The rejected options were renewing both exceptions for another three days unchanged, and letting them expire so CI fails from 20 November.

Recorded as AUTH-011 in [development/evidence/auth-011-exception-expiry.md](../development/evidence/auth-011-exception-expiry.md). It amends the expiry and file-binding rules of AUTH-005, AUTH-007 and the DEV-006 scoped finding reviews. It does not clear any finding, change a severity threshold, admit a new finding, or permit production, real data, an exposed service or deployment.
