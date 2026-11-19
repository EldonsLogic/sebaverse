# Ubuntu Noble scanner OpenSSL recheck

At 20:00:25 UTC on 19 November 2026, Canonical still listed CVE-2026-107496 as `needs-triage` for `openssl` in Noble Security. The record was last updated on 18 November at 09:55:27 UTC and lists Medium Ubuntu priority, a CVSS score of 7.5 (High) and no Ubuntu Security Notice. The advisory response SHA-256 was `1bf10858008c3f6923cea7a048058af8ad64461330eaf88e8ce7fa07631cf53a`. [Canonical advisory](https://ubuntu.com/security/CVE-2026-107496) · [Canonical JSON record](https://ubuntu.com/security/cves/CVE-2026-107496.json).

The Ubuntu Primary Archive returned one published record in each queried pocket for the `openssl` source and each corresponding Noble amd64 `libssl3t64` binary.

| Noble pocket | Published version | Publication records |
| --- | --- | --- |
| Security | `3.0.13-0ubuntu3.16` | [Source](https://api.launchpad.net/1.0/ubuntu/+archive/primary/+sourcepub/18805670) · [amd64 binary](https://api.launchpad.net/1.0/ubuntu/+archive/primary/+binarypub/250497468) |
| Updates | `3.0.13-0ubuntu3.16` | [Source](https://api.launchpad.net/1.0/ubuntu/+archive/primary/+sourcepub/18805779) · [amd64 binary](https://api.launchpad.net/1.0/ubuntu/+archive/primary/+binarypub/250499590) |
| Proposed | `3.0.13-0ubuntu3.17` | [Source](https://api.launchpad.net/1.0/ubuntu/+archive/primary/+sourcepub/18960981) · [amd64 binary](https://api.launchpad.net/1.0/ubuntu/+archive/primary/+binarypub/253745785) |

The same Proposed source version was already inspected on 18 November and had no fix for this CVE. The AUTH-010 scanner route stays on hold for DEV-010. A supplier fix or applicability decision still needs reconciliation against the exact signed artifact and scanner workload. Full runtime security and notice closure, definition rights and isolation validation remain open. [18 November follow-up](../../development/evidence/dev-010.md#auth-010-noble-package-route-follow-up-and-hold-antigravity-18-november-2026) · [Package route review](package-route-review.md).

This was a single, metadata-only follow-up on the route for scanning untrusted uploads. All seven metadata requests returned HTTP 200. Current evaluation is limited to authored fixtures, with no learner exposure. No package archive, scanner runtime or definitions were acquired or executed.
