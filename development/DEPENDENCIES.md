# F1 dependency setup and verification

Scope: exact backend/web dependency readiness under U15/AUTH-002, not a runnable product. Toolchains are pinned in .python-version and .node-version; npm10.8.2 and uv0.11.14 are recorded. No changes to your global Node/Python selection are required. Current host may use the already bundled compatible Node explicitly; a new machine must provide the pinned versions rather than assume its global defaults.

## Reproduce

1. Read backend/README.md and web/README.md, exact manifests/locks and third-party inventories. Review registry origins, license/notices and latest known-advisory results before adoption. Source-build and npm lifecycle hooks are disabled in this phase.
2. Use Python3.12.13 with uv0.11.14. Point cache and managed Python installs to ignored local work paths. If provisioning Python with uv, use --no-bin to avoid creating a global executable link. Sync backend using its documented --locked --no-build command; do not install the virtual project as a source package.
3. Use Node24.22.1/npm10.8.2. Run the documented clean `npm ci --ignore-scripts --engine-strict` in web. Do not run a postinstall/prepare workaround or a broad npm audit fix. Any necessary explicit vetted build step belongs to its later task with recorded approval/verification.
4. Run `make dependency-check`, document/foundation checks and the raw vulnerability commands in worker evidence. Repeat clean installs in CI on Linux; local observations are macOS arm64. Windows optional locks are not a Windows runtime certification.
5. Record actual checks/review and pass F1 before F2. Failures or missing evidence hold the boundary. No app source, DB connection, parser/model download or production behavior is tested here.

The root artifact validator excludes installed/scratch directories; third-party README/JSON files inside ignored environments are not project specifications or live instructions. Historical research/export files remain unchanged. Lock drift invalidates evidence and requires reinspection/rescan, not a manual status override.

## Disabled future integrations

Docling/scanner/OCR is held at DEV-010/F3. Embedding/voice/model assets, eval runners, FSRS/specialist reuse and optional extraction each need separate exact release/rights/security/runtime evidence before enabling. No model assets used means N/A for this phase, not clearance. PostgreSQL image manifest is pinned in infra/images.lock.json without pulling/running/scanning it; F2 must perform applicable image/runtime/startup checks before use. Private storage/provider/region and all real-data/legal/pilot conditions remain gated.

Native boundary: Psycopg’s binary wheel is currently for ignored local import/compatibility checks. Its bundled libraries’ complete notice/version/native advisory closure is not established by pip-audit. F2 has a mandatory before-use native/image check; release packaging/distribution is blocked until applicable notices/source/license obligations and target-platform security evidence are resolved. Upstream describes binary vs system-linked alternatives at https://www.psycopg.org/psycopg3/docs/basic/install.html ; no production binding strategy is silently certified here.
