# Sebaverse web shell — F2 / DEV-006

This directory now contains the actual Arabic-first React/TypeScript/Vite local application shell, its configuration/build scripts, approved public brand assets and the exact dependency manifest/lock. The selected blue/orange roles, Latin vector Sebaverse logo and local Alexandria/Rubik fonts come from the current brand kit; original OFL notices and copied-asset hashes are retained under public/brand/. Frozen source assets and logo geometry are unchanged. No permanent slogan or door-based product wording is adopted.

Root AGENTS.md, the current authorization and development/phase-gates.json remain authoritative. This README describes current startup and limitations; it does not grant deployment, real-data or next-phase permission.

## Start and check the current shell

Select the pinned Node 24/npm 10 toolchain first, then run from the repository root:

```sh
npm --prefix web run typecheck
npm --prefix web run build
npm --prefix web run dev
```

Development binds only 127.0.0.1:5173 and proxies `/api` to 127.0.0.1:8000. This dev path uses a separate local Vite origin; the intended same-origin F2 check builds `web/dist/` and serves it through Django's guarded local file-serving routes. Follow [backend F2 startup instructions](../backend/README.md) for that entry point. `/assets/**` and `/brand/**` are public build/brand resources; API routes are separate. There is no Node production backend, deployed service or source map output.

`npm --prefix web run preview` optionally serves the static build on loopback port 4173. It is a local preview, not production hosting or an API implementation. Stop a foreground dev/preview server with Ctrl-C. Remove generated dist/ only when no active consumer is using that build. Keep node_modules, generated builds and local caches out of Git.

## Current routes and honest feature boundaries

- `/`: home and navigation to the learning spaces.
- `/materials`: materials empty state and a native disclosure explaining future upload considerations.
- `/practice`: practice empty state; no generated or assessed question is presented.
- `/progress`: progress empty state; no fabricated score, learner history or mastery percentage.
- Unknown client-side route: explicit not-found view. Django's direct HTTP route whitelist is intentionally narrower; unknown server routes return JSON 404 rather than exposing arbitrary files or falling back to the shell.

These views contain no fake learner, source, syllabus, grade or activity history. Uploads, tutoring, authentication and progress mutations remain unavailable and are described as such. All account/learning authority remains a future server implementation. The shell makes no API polling requests, loads no remote assets, needs no provider keys and stores no private data in the client. TanStack Query is configured without active queries.

## Accessibility and verification boundaries

The shell uses `<html lang="ar" dir="rtl">`, native semantic navigation/links/details, aria-current on the active route, a skip link to `#main-content`, route titles/focus, visible focus, a non-mirrored Latin logo and reduced-motion styles. Decorative SVGs are aria-hidden; meaningful content remains in the DOM. Useful browser-test anchors are nav[aria-label="التنقّل الرئيسي"], #main-content, .brand-logo, main h1 and the materials details summary.

The frontend builder observed typecheck and static build exit 0 under Node24.22.1. Integrated browser, backend, native/database and phase results are recorded separately in development/evidence/ and development/phase-gates.json; later relevant edits require fresh verification. Do not infer full accessibility, product security, educational behavior or phase approval from a generated bundle or this README.

Vite emits MODULE_LEVEL_DIRECTIVE warnings for dependency `use client` directives in React Router/TanStack Query. This shell is a client-only SPA with no React Server Components; warnings remain visible and are not suppressed or treated as product validation. F2 adds application code/configuration and approved explicit type/build commands, not dependency installation lifecycle hooks. No new dependencies, lock changes, real data or deployment are part of this frontend increment.

## Historical F1 dependency-readiness record — DEV-005

The following preserves the earlier dependency-only checkpoint. Its package/license/audit observations remain useful provenance, but its no-application/build limitation applies to F1, not the current F2 shell.

### F1 toolchain

Use Node 24 LTS, at least 24.22.1 and below 25, with npm 10.8.2 as pinned by package.json. The existing Codex bundled Node 24.22.1 was used for local F1 checks; no runtime download or global package installation was performed by this task. System Node 20.19.0 was not used because the official Node release table lists v20 as end-of-life at the 11 November 2026 check. Package compatibility is separately constrained by engines and peers.

Select the approved Node runtime in PATH before invoking npm. The repository-level toolchain/Make target records the portable entry point. Keep local npm cache under the ignored `work/cache/npm` directory; do not commit the cache or node_modules.

From the repository root, the reproducible dependency checks are:

```sh
npm --prefix web ci --ignore-scripts --engine-strict --no-fund --no-audit
npm --prefix web ls --all
npm --prefix web audit --json
```

Set `npm_config_cache` to a local ignored path when needed. Clean `npm ci` removes and recreates only web/node_modules from package-lock.json. It must not be run in another contributor's uncoordinated active checkout. No lifecycle scripts are permitted by this F1 installation. Do not silently remove `--ignore-scripts`, execute an upstream setup workflow or add an install-time script exception to force a build to work.

### F1 pins and provenance

Direct versions in package.json are exact, without ranges. package-lock.json fixes the resolved transitive closure and npm tarball integrity values. Official registry metadata captured before installation is in development/evidence/f1-web-registry.json; package/license inventory is in third-party/web-licenses.json. Actual command results and advisory status are recorded in the F1 web evidence files. Those records, rather than this README alone, establish what was run and whether it passed.

The dependency set contains React, ReactDOM, React Router, TanStack Query, TypeScript, Vite and the corresponding React/DOM/Node type packages. No whole DeepTutor, LearnHouse, EduStudio or additional agent/LMS framework is imported. Parser, model, evaluation and backend dependencies are separate environments.

### F1 verification limits

A lockfile, successful script-disabled install or clean registry advisory response does not prove the product builds, is secure, meets accessibility requirements or improves learning. At the F1 checkpoint no application source existed and no app build was tested. F2 now supplies the shell described above; its current type/build/UI results and native pre-use reviews are separate phase evidence, not retroactive F1 claims. For Vite/native dependencies, optional platform packages and skipped lifecycle behavior must be considered before build readiness is claimed.

Never add an override merely to hide an advisory. Record vulnerable packages, dependency paths, remediation choices, unresolved risk and phase blocking status. Relevant dependency changes require re-running F1 checks, inventory and independent review before crossing the next phase boundary.

### F1 license observations

All 81 lock entries declare a license; 31 packages were installed on darwin-arm64. The lightningcss build-tool family declares MPL-2.0. The native Rolldown platform tarball declares MIT but has no standalone license file; the matching-version Rolldown wrapper ships LICENSE and THIRD-PARTY-LICENSE, both preserved in the inventory. These observations require distribution/notice review before shipping the affected tools or images; they are not a missing-version override or a claim of blanket commercial clearance. Other target-platform optional packages are recorded from the lock but their shipped notice text is not locally inspected.
