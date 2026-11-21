# Current development checkpoint

21 November 2026. PUBLIC canonical repo https://github.com/EldonsLogic/sebaverse; workspace /Users/eldon/Documents/Sebaverse. Working checkpoint based on `fb92198`; inspect Git/remote. F0–F2 passed; F3 / DEV-010 in progress. No native activation, real data, live uploads, provider calls or deployment.

Manifest resolution and reviewer reads now capture immutable scope/hash/provenance before bounded storage I/O, then reload and recheck caller-specific live authorization, rights/status and unchanged binding before returning. No locks across I/O. A revocation that commits after the final check can still race the response. [Correction/evidence](evidence/dev-010-manifest-return-fence.md), [independent review](evidence/dev-010-manifest-return-review.md).

Root and independent reviewer passed 585 backend tests (one PostgreSQL deselected), Django clean; reviewer passed 250 ingestion and 20 focused checks. Final 14 manifest tests against the old broker reproduced 12 negative failures and two positives. An in-place saved-scope mutation is caught by the immutable snapshot. PostgreSQL probe now stages 27 scenarios, all pending execution on a qualified runtime; historical 14-scenario evidence is not acceptance of this patch.

RISK-F3-005 is open: canonical consent withdrawal denies access but does not currently schedule source/derived purge. Authored files and quota remain until uploader cleanup. This read fix does not close deletion/retention requirements. Define cleanup authority, retries/accounting and approved minimal retention before F3 closure; no retention period is invented.

The production authority proposal received independent design review: CHANGES REQUIRED, not adopted. Signer/scanner trust, one-shot release/revocation ordering, dispatch deadline and isolation for both engines remain unresolved. RISK-F3-004 stays open; no FD/crypto/credential implementation or ADR amendment. [Design review](../workers/parser/production-authority-review.md).

Prior main `fb92198` passed 571 Linux backend tests/web and separate foundation/dependency workflows. Native pre-use gate failed with current advisory findings; database/browser skipped. [Exact receipt](evidence/hosted-kind-main-fb92198.md). Current read-fence source has local evidence only until committed CI runs. Three actual Sol subagents handled implementation/audit, design/tests and hosted/independent review; root integrated.

AUTH-014 supplier wait persists; no alternate hunt, owned writer, source build, pin/exception/review date or gate change. Native/scanner/OS isolation, real PDF mapping/fidelity and all F3 exit suites remain pending. No F4 work or new learner-facing feature. Closing artifact checks are in the correction evidence.
