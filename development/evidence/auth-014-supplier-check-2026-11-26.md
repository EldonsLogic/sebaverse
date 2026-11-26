# AUTH-014 supplier check — 26 November 2026

One manual, read-only check under the AUTH-014 "wait for supplier" decision. No image was pulled or executed; no polling job was created; no pin, exception, threshold or review changed.

- **Why checked:** hosted `Local skeleton phase checks` fails on main at "Enforce native/image pre-use policy" (runs 45411297208, 45412576435): image-cves.json 19 blocking, of which 10 are reviewed findings whose fix is now released, so AUTH-011 requires a new pinned artifact and re-review. This is the gate working as designed.
- **Command:** `docker buildx imagetools inspect docker.io/library/postgres:17-alpine` (registry metadata), then `--format '{{json .SBOM}}'` on the returned digest (supplier SBOM attestation, read as data).
- **Result:** the tag now resolves to index `sha256:f9cf3e1f0066f0eb0c48707d864f0ac5941e9ff454a072077d97a4d278d07d73` (source `docker-library/postgres` revision `ac9627dcf544a8454f212a12ddeebfcdc0803d3e`, `17/alpine3.24`), not the pinned `sha256:d3244e8c…`. Its SBOM shows `libssl3`/`libcrypto3` **3.5.9-r0** on linux/amd64, arm64, 386, arm/v7, ppc64le and s390x; only linux/riscv64 has 3.5.9-r1. busybox is still 1.37.0-r31.
- **Conclusion:** not a meaningful qualified supplier update for the CI platform (linux/amd64). AUTH-014 hold remains; no reassessment started. The 37 PostgreSQL DEV-010 cases remain NOT RUN.
- **Recheck guidance:** recheck once, manually, when the official amd64 image's SBOM shows libssl3/libcrypto3 3.5.9-r1 or later. Adoption would then still need a fresh SBOM/native/core/advisory/KEV/rights scan, a pin change and independent review.

The SBOM copy is in ignored `work/supplier-check-2026-11-26/sbom.json` (5.9 MB, not committed).
