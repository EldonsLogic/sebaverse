# Test-only database image remediation draft

DEV-006; R054/R075/R078/R094/R097/R098. This recipe is **not built, scanned, approved or used**. It does not replace the current evaluated pin or authorize PostgreSQL startup.

Both official candidates were blocked by actual scans. The Alpine candidate's High/Critical matches come from Go1.24.6 embedded in `/usr/local/bin/gosu`. This draft replaces that helper in the merged runtime filesystem with a deterministic authored script that always fails126, and selects the existing `postgres` user. It adds no package, language runtime or privilege-switching implementation. The upstream entrypoint and existing explicit runner `--user postgres` still need real startup verification only after the derived image passes its own pre-use gate.

The Dockerfile deliberately has no RUN instruction. A future controlled build may statically unpack/copy image content without executing the base. Do not use ordinary app startup to inspect an unapproved image. The exact parent linux/amd64 manifest is immutable; its index and original reports remain preserved in development/evidence/f2-alpine-candidate-43596204128/.

Before use: review the complete recipe/entrypoint path, build provenance and resulting immutable platform digest; catalog and scan the actual merged derived filesystem; verify the old Go binary is absent from that runtime view; retain notices and exact base provenance; bind the derived source identity/digest to both verifier and runner without relabeling it as the official upstream image. Add negative tests for parent/derived substitution. Every remaining native/core finding still needs review or remediation, followed by actual migrations/readiness and task-owned teardown.

Replacing a path does not remove its historical bytes from lower OCI layers. No whole-archive eradication, safe redistribution, licensing clearance or production hardening is claimed. The derived artifact is a scoped synthetic-development proposal; root startup is intentionally unsupported.
