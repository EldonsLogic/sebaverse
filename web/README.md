# Web dependency foundation — F1 / DEV-005

This directory contains the exact frontend dependency manifest and lock, not the product UI. No pages, API calls, app configuration, build script or tutoring behavior are implemented in F1. The selected architecture remains a React/TypeScript/Vite static client with React Router and TanStack Query against the same-origin Django API. Root AGENTS.md and the recorded phase gate remain authoritative.

## Toolchain

Use Node 24 LTS, at least 24.22.1 and below 25, with npm 10.8.2 as pinned by package.json. The existing Codex bundled Node 24.22.1 was used for local F1 checks; no runtime download or global package installation was performed by this task. System Node 20.19.0 was not used because the official Node release table lists v20 as end-of-life at the 11 November 2026 check. Package compatibility is separately constrained by engines and peers.

Select the approved Node runtime in PATH before invoking npm. The repository-level toolchain/Make target records the portable entry point. Keep local npm cache under the ignored `work/cache/npm` directory; do not commit the cache or node_modules.

From the repository root, the reproducible dependency checks are:

```sh
npm --prefix web ci --ignore-scripts --engine-strict --no-fund --no-audit
npm --prefix web ls --all
npm --prefix web audit --json
```

Set `npm_config_cache` to a local ignored path when needed. Clean `npm ci` removes and recreates only web/node_modules from package-lock.json. It must not be run in another contributor's uncoordinated active checkout. No lifecycle scripts are permitted by this F1 installation. Do not silently remove `--ignore-scripts`, execute an upstream setup workflow or add an install-time script exception to force a build to work.

## Pins and provenance

Direct versions in package.json are exact, without ranges. package-lock.json fixes the resolved transitive closure and npm tarball integrity values. Official registry metadata captured before installation is in development/evidence/f1-web-registry.json; package/license inventory is in third-party/web-licenses.json. Actual command results and advisory status are recorded in the F1 web evidence files. Those records, rather than this README alone, establish what was run and whether it passed.

The dependency set contains React, ReactDOM, React Router, TanStack Query, TypeScript, Vite and the corresponding React/DOM/Node type packages. No whole DeepTutor, LearnHouse, EduStudio or additional agent/LMS framework is imported. Parser, model, evaluation and backend dependencies are separate environments.

## What F1 does not prove

A lockfile, successful script-disabled install or clean registry advisory response does not prove the product builds, is secure, meets accessibility requirements or improves learning. No application source exists yet. A subsequent phase must define meaningful app type/build/UI tests and explicitly review any native tool/runtime or package script needed to run them. For Vite/native dependencies, optional platform packages and skipped lifecycle behavior must be considered before build readiness is claimed.

Never add an override merely to hide an advisory. Record vulnerable packages, dependency paths, remediation choices, unresolved risk and phase blocking status. Relevant dependency changes require re-running F1 checks, inventory and independent review before crossing the next phase boundary.

## License boundary observed in F1

All 81 lock entries declare a license; 31 packages were installed on darwin-arm64. The lightningcss build-tool family declares MPL-2.0. The native Rolldown platform tarball declares MIT but has no standalone license file; the matching-version Rolldown wrapper ships LICENSE and THIRD-PARTY-LICENSE, both preserved in the inventory. These observations require distribution/notice review before shipping the affected tools or images; they are not a missing-version override or a claim of blanket commercial clearance. Other target-platform optional packages are recorded from the lock but their shipped notice text is not locally inspected.
