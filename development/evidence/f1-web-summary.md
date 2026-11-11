# F1 frontend dependency readiness — DEV-005

11 November 2026. Requirements R006/R075/R081/R085. Owned scope: web manifest/lock/readme, frontend license inventory and f1-web evidence only. No product source, Git action, deployment, paid call or child data.

## Actual environment and selected pins

Existing bundled Node 24.22.1 plus installed npm CLI 10.8.2; local npm cache under ignored work/cache/npm. Official Node release policy lists 24 as LTS and 20 as EOL at retrieval. No runtime download/global installation. React/DOM 19.3.1; React Router 8.5.1; TanStack Query 5.107.1; TypeScript 7.0.2; Vite 8.3.8; React/DOM types 19.3.0; Node types 24.19.2. Exact peers/engines/licenses/integrities were read from registry.npmjs.org before install.

## Actual commands and results

1. Lock-only resolution with --ignore-scripts --engine-strict completed, producing lockfile v3 and 81 resolved entries. Optional Vite peer metadata for additional tools was fetched by npm, but no Vitest/browser/devtools package entered the lock.
2. Clean npm --prefix web ci --ignore-scripts --engine-strict --no-fund --no-audit: exit 0, 31 packages installed. No lifecycle scripts executed; optional fsevents install script remained disabled.
3. npm --prefix web ls --all --json: exit 0. Actual installed graph in f1-web-commands.json.
4. npm --prefix web audit --json: exit 0. Zero info/low/moderate/high/critical advisories in the dated registry response. Raw response in f1-web-audit.json. No overrides or advisory suppression used.

## License observations and limits

All 81 lock entries have declared licenses: MIT 44, Apache-2.0 22, MPL-2.0 12, ISC 1, BSD-3-Clause 1, 0BSD 1. Actual installed notice/license files, including third-party notices, are preserved with hashes/text in third-party/web-licenses.json. Noninstalled optional platform entries are explicitly declaration-only observations.

MPL-2.0 entries belong to lightningcss build tooling. The matching-version Rolldown wrapper carries LICENSE and THIRD-PARTY-LICENSE associated with its native binding; the native tarball itself omits a standalone license file. Applicable notices/target-platform/source obligations must be reviewed before actual tool/image/application distribution; no blanket legal clearance claimed. Mozilla's official MPL FAQ distinguishes local use from distribution obligations: https://www.mozilla.org/en-US/MPL/2.0/FAQ/ .

## Phase result

Frontend dependency commands pass; independent/root review and full F1 integration remain pending. No next phase is authorized by this worker report. A dated zero-advisory response does not prove comprehensive security. No app build, typecheck of app code, UI/RTL, accessibility, product runtime or learning test performed. Future build/native behavior must be verified with lifecycle scripts still disabled or an explicitly reviewed exception; none granted here.

Machine-readable versions, command evidence, hashes/counts and limitations: f1-web-registry.json, f1-web-commands.json, f1-web-summary.json and f1-web-audit.json.
