# Released-fix runtime recovery choice

20 November 2026 · DEV-010 / R040/R081. Prepared scope, not approval or an image change. The original database image and the latest same-baseline official build still carry OpenSSL 3.5.9-r0; Alpine's package/security metadata publishes 3.5.9-r1 fixing the four High and one Medium CVEs. AUTH-011 correctly ends the previous exception. [20 November metadata](postgres-fix-recheck-2026-11-20.md), [original released-fix evidence](integration-2026-11-19.md).

Threat and proposed budget: an incorrect package overlay could misrepresent the runtime or introduce vulnerable code; current exposure is disposable synthetic CI, no user data or external service. One exact fixed-package derivative of the existing parent, one engineering day and at most two correction cycles. No unrelated image search, source compilation, severity exception, expiry renewal, real data, deployment or paid service.

## Option A — assess and adopt only if independently qualified (recommended)

Prepare an offline, immutable derivative of the CURRENT pinned official PostgreSQL parent, changing only the three exact Alpine OpenSSL 3.5.9-r1 package payloads (libcrypto3, libssl3, openssl) needed to replace r0. Pin exact official archives/checksums and source/notice metadata from the trusted target-distribution index. No arbitrary package upgrade or extra dependencies. If the exact release is unavailable, has incompatible dependencies, requires unreviewed scripts or cannot be represented honestly, stop rather than changing versions/approaches silently.

Static acquisition and inspection precede use. Verify vendor signature/metadata and package bytes; preserve notices and exact backport provenance. Build/repack without executing the held parent or package maintainer scripts, using the existing static-image boundary. Reconcile filesystem ownership/links and installed-package metadata with the exact archive contents; a version label alone never establishes fixed bytes. If correct static assembly cannot be established within budget, hold the option.

Independently inspect the final artifact and source/config diff. Produce actual SBOM/native/core/advisory and known-exploited results for the exact derived digest with all present thresholds intact. No High, Critical, unknown-severity, KEV or unreviewed finding may be waived by this proposal. The expired/superseded AUTH-007 exception cannot be reused or renewed. Record any required new artifact review against actual evidence; do not re-date or silently alter old review findings. Make only the specific pin/build/binding changes independently justified for this fixed artifact and preserve old review history. If extra conditions or a new finding block, stop with options.

Only after those checks pass, use the fixed artifact for the existing disposable synthetic PostgreSQL suite, including the new fifteenth ingestion scenario and teardown. No product phase pass is inferred. Actual scanner/PDFium/worker-image/isolation/fidelity qualification remains separate.

Expected benefit is restoring database CI without waiting for supplier image publication. That is a proposal, not a benchmark or guarantee. Cost is one bounded static-image/package review plus normal CI; no provider fees. Any measured time/storage/compute belongs in the execution report.

## Option B — wait for a fixed supplier image

Keep the current pin and failed-closed gate. Recheck at a meaningful later supplier update rather than repeatedly dispatching CI. Continue only independent work already authorized within F3. This minimizes custom packaging work but gives no confirmed unblock date and leaves the required database suite unavailable.

## Why a founder choice is needed

Previous runtime attempts were explicitly bounded and the 19 November instruction barred re-dating/rebinding reviews except AUTH-012's two helper hashes. A new fixed-package artifact is outside those scopes. QUALITY-BAR.md section 2 requires a choice before another approach. Selecting option A authorizes only this bounded fixed-artifact route with the above independent checks, not a blanket exception or relaxed phase gate.

Founder selected Option A on 20 November under AUTH-014. The scope above is now authorized conditionally; no artifact has been adopted, no existing exception renewed and no gate passed at this checkpoint.

## Assessment correction — exact parent differs from supplier metadata

Static inspection of the digest-verified original parent on 20 November finds installed libcrypto3 and libssl3 at r0 but no openssl command-line package. The three-package replacement assumption above was incorrect for that exact parent. Adding the CLI would expand the installed surface and match BusyBox's existing trigger path. No assembly/adoption has occurred. A founder clarification to narrow the assessment to the two installed libraries is pending; the original plan and approval wording are preserved as history.
