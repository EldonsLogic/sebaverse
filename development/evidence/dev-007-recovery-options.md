# DEV-007 integration recovery decision

17 November 2026. Status: proposal, not an approved exception. Requirements: R060, R075, R099. Scope: restore synthetic local/CI development after the DEV-007 integration failures. No production, learner data or deployment is involved.

## Verified findings

- The npm registry `https://registry.npmjs.org/picomatch/latest` still returns 4.0.7. The current exact web lock also contains 4.0.7. [GHSA-fc5q-39xc-vjpf](https://github.com/advisories/GHSA-fc5q-39xc-vjpf) lists this version as affected and no patched version. Four audit entries reflect the same underlying regex denial-of-service issue propagated through fdir, tinyglobby and Vite; they are not four independent vulnerabilities.
- Vite imports picomatch and tinyglobby in its installed Node build code. It would be false to call the affected package unused. The checked-in Vite config uses a loopback development server and static build. No upload parser or user-controlled glob feature exists. Whether every internal pattern is safe has not been exhaustively established; a development-only review could bound the input path, but it cannot claim the package is fixed.
- The hosted native scan's 24 new matches are six Medium advisories repeated across libgssapi-krb5-2, libk5crypto3, libkrb5-3 and libkrb5support0, all version 1.20.1-6ubuntu2.10. Every new match has an empty fix-version list and `not-fixed` scanner state. That is scanner evidence, not independent publisher confirmation or a non-reachability verdict.
- Publisher-page retrieval through the web tool timed out for these six native advisories. They remain unreviewed. No source or disposition has been invented.

| Native advisory | Scanner severity | Scanner fix state |
| --- | --- | --- |
| CVE-2026-107364 | Medium | Not fixed; no version listed |
| CVE-2026-107884 | Medium | Not fixed; no version listed |
| CVE-2026-111423 | Medium | Not fixed; no version listed |
| CVE-2026-118380 | Medium | Not fixed; no version listed |
| CVE-2026-71199 | Medium | Not fixed; no version listed |
| CVE-2026-71200 | Medium | Not fixed; no version listed |

## Decision options

1. **Proposed: bounded development-only review and exception.** Authorize a maximum of two review/correction cycles to assess trusted repository build inputs and the six native advisories, then prepare exact, expiring dispositions only where evidence supports them. The npm audit would retain all findings and fail on any new or changed finding; only the reviewed exact advisory/version/build scope could receive a temporary development-only exception. The native gate would retain its existing thresholds and require explicit per-advisory review. No exception applies to learner uploads, exposed services, production or real data. This has the smallest proposed code scope but accepts residual development availability risk. It cannot promise every finding will qualify.
2. **Keep the current zero-advisory build gate and replace affected components.** Prepare an evidence-backed ADR for replacing the frontend build path and, if required, the native database client/runtime path. Review exact new dependencies, notices and vulnerability closure before installation, then repeat compatibility, browser and database tests. This avoids an advisory exception but reopens settled architecture and has substantially greater, currently unestimated effort. No replacement has been selected or validated.
3. **Wait for verified upstream fixes.** Leave DEV-007 in review and DEV-008 held. Recheck only when a compatible upstream patch is available. This needs no gate change or dependency migration, but the unblock date is unknown.

The first option is a recommendation for founder review, not permission inferred from “continue.” No gate, threshold, lock, dependency, native disposition or application code has been changed by this assessment. The bounded assessment budget is exhausted because no compatible patch is available; do not launch another approach without a decision.

## Evidence and validation

Canonical failed hosted runs: [dependency readiness 44158414630](https://github.com/EldonsLogic/sebaverse/actions/runs/44158414630), [skeleton 44158414853](https://github.com/EldonsLogic/sebaverse/actions/runs/44158414853). Source implementation remains independently reviewed at 30cc0be. The downloaded f2-evidence artifact is retained under ignored work/dev-007/advisory-followup; raw evidence remains in hosted CI rather than being duplicated in Git.

Native scan SHA-256: `ee3fb888f00fa954bf9158a17fb81c61d2b967601497c148861f8cd8f2a871ee`. Latest registry response SHA-256: `f5b19326b62bc9009139f82d9b3400421edf9fc0ade0212d49d1bac349659d77`.
