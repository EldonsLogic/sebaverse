# AUTH-014 narrowed assessment checkpoint

20 November 2026 · DEV-010 / R040/R081. Founder approved replacing only installed libcrypto3/libssl3 3.5.9-r1 and keeping openssl CLI absent. The original one-day/two-correction budget and every security threshold remain. No package, image pin, review date/binding or phase gate changed.

The chosen static package-manager assembly method is held at its build-tool qualification boundary. [Exact tool review](../../infra/local/postgres-fixed-packages/build-tool-review.md) and [independent assessment](auth-014-independent-assessment.md) distinguish observed build inputs from unproven vulnerability reachability. No held executable or parent image ran and no candidate image was assembled. There is no fresh artifact scan or database result.

## Concrete next options

1. **Wait for a qualified official build tool or fixed supplier image.** Preserve current pins and the closed runtime gate. Cost: no custom package writer; unblock date unknown. Recheck only on a meaningful supplier update, not repeated CI dispatch. This is the conservative default while the founder considers another method.
2. **Separately authorize an owned static overlay writer assessment, capped at four engineering hours within the original AUTH-014 day and two-correction limit.** The writer would consume only the exact already-authenticated two library APKs and exact parent as data. No package-manager/parent execution, source compilation, extra installed package or exception. Require byte/metadata comparisons for all target payloads, preserved non-target records and world constraints, honest package identities/dependencies/ownership/checksums, and independent negative tests plus exact final filesystem/SBOM/native/core/advisory/KEV/rights checks before adoption. Cost/risk: new authored package-database transformation logic can misrepresent installed files; independent reconstruction from signed inputs and untouched-parent comparisons must catch that. A locally plausible archive or passing unit test cannot qualify a runtime. This is a proposal, not authorization or an implementation guarantee. If the remaining original budget cannot contain it, stop without renewal.

The prior plan explicitly requires stopping with options for additional blockers. No alternate tool hunt, source build, hand-written package database or renewed exception is being started without that choice. The original three-package proposal is retained as history; the narrowed set is authoritative.

## Independent hosted blocker

The latest checkpoint's GitHub jobs did not start because GitHub reported an account payment/spending-limit problem. [Independent assessment](auth-014-independent-assessment.md) records exact run IDs and annotations. Hosted Linux guard, dependency/security, database and browser checks are NOT RUN. The founder must review the account's billing/spending configuration directly; no spending change, purchase or repeated rerun is authorized here. Resolving billing alone does not qualify the database image or build tool.

Current learning outcome remains unchanged: ingestion foundation work is not a usable learner feature and F3 is still open. Local Darwin results from the prior reviewed checkpoint remain historical, not new tests for this documentation-only assessment.

## Closing verification

Root ran `make foundation-check` on the integrated documentation/assessment working tree based on `8cec5b3`: exit 0; economics/artifact/foundation checks and 179 helper tests passed. `git diff --check` passed. No product code, dependency lock, runtime pin, policy or old security review changed; no new backend/native/database/browser test was needed or run for these documentation-only changes. Reviewer runtime_fix_recheck independently accepted the receipts, hold and recovery options; both subagents released file ownership. The tests' expected negative-fixture report is not a live npm failure or hosted result.
