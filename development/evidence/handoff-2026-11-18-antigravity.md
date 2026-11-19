# Task handoff — DEV-010 (Antigravity to Codex)

> [!NOTE]
> Historical 18 November handoff. Reviewed on 19 November: AUTH-011 now supersedes the expiry prompts below. Current authority and next steps are in CURRENT-STATE.md. Binary observations do not prove unreachable code; source review found unrelated CMS_encrypt mentions. No scanner exception is authorized.

> [!IMPORTANT]
> **Founder decisions needed before CI breaks on 20 November 2026:**
> 1. **AUTH-007 (OpenSSL High exception in disposable synthetic PostgreSQL CI):** expires **20 November 2026 at 11:39:06 UTC** (`infra/synthetic-openssl-review.json`). Not extended.
> 2. **AUTH-005 (development-only npm `picomatch` exception):** expires **20 November 2026 at 19:38:23 UTC**. Not extended.
> 3. **Older native finding reviews (`infra/security-reviewed-findings.json`):** expire **21 November 2026**. Not extended.
> 4. **AUTH-010 scanner hold on OpenSSL `CVE-2026-107496` (`libssl3t64` `3.0.13-0ubuntu3.16` on Ubuntu 24.04 LTS Noble):** requires a founder choice among the recorded options in [dev-010.md](dev-010.md#prepared-founder-options-for-the-auth-010-scanner-hold) before any scanner package installation, definition download or container execution can proceed.

## Identity and scope

- Date/time and timezone: 18 November 2026, 19:32 EET (`UTC+02:00`; `2026-11-18T17:32:00Z`).
- Outgoing agent/session and role: Antigravity (`/antigravity`, roles: `Security`, `Infrastructure`, `Documentation`), taking over temporarily after Codex hit a usage limit mid-task on DEV-010.
- Receiving agent/role, if actually assigned: Codex (`/root`, main agent / `Orchestrator`, `Infrastructure`, `Integration`).
- Task ID(s) / requirement ID(s): `DEV-010` (`R037`, `R038`, `R039`, `R040`, `R041`, `R042`, `R046`).
- Source/ADR/specification and exact acceptance criteria:
  - Specs: `docs/04-curriculum-and-rag.md`, `architecture/technical-baseline.md`, `architecture/repository-adoption.json`, `execution/subject-independent-poc.md`.
  - Acceptance criteria (`python3 tools/brief.py DEV-010`):
    1. Allocate private quarantined objects with byte/type/page/time limits and scope-bound job manifests.
    2. Scanner failure/unavailability never bypasses into parsing; parser has no learner DB credentials or broad egress.
    3. Broker validates output provenance/quality and handles cancel/retry/delete/withdraw without stale publication.
    4. Record actual task checks for the mandatory phase exit gate; do not advance to the next phase until every required check passes and evidence/review is recorded.
- Authorized scope / recorded gate or instruction: `AUTH-004` (F3 synthetic implementation), `AUTH-008` (one alternate Docling PDF backend assessment, 1-day cap), `AUTH-009` (one alternate official ClamAV image assessment, 1-day cap), and `AUTH-010` (one distribution-maintained ClamAV package/runtime assessment on Ubuntu 24.04 LTS Noble amd64, 1-day cap, unchanged gates).
- Limits (time/tool/cost/retries/data), including what is not authorized:
  - One engineering day maximum for `AUTH-010`; zero paid provider calls (`$0`), zero new dependencies installed, zero scanner/parser/model installation or execution, zero local macOS database execution, zero gate/threshold/approval/expiry changes, zero work on `DEV-011` or later tasks, and no push/merge to `main`.
- Owned files and exclusive/shared boundaries:
  - Commit 1 (`baa2db0`): checkpointed Codex's 19 modified/untracked files on `antigravity/dev-010-handover` without modification (`architecture/repository-adoption.json`, `architecture/repository-adoption.md`, `development/APPROVALS.md`, `development/CURRENT-STATE.md`, `development/evidence/dev-010.md`, `development/evidence/dev-010-github-resources.md`, `development/evidence/dev-010-scanner-next-decision.md`, `infra/scanner/alternate-candidate.json`, `infra/scanner/alternate-review.md`, `infra/scanner/package-route-candidate.json`, `infra/scanner/package-route-review.md`, `infra/scanner/review-plan.md`, `infra/scanner/static-review.json`, `registers/requirements.json`, `registers/requirements.md`, `sources/github-resource-reuse-instruction.md`, `sources/source-catalog.md`, `workers/parser/alternate-candidate.json`, `workers/parser/alternate-review.md`).
  - Commit 2 (Antigravity handover commit): touched only `development/evidence/dev-010.md`, `development/CURRENT-STATE.md`, `development/agents/roster.json`, and `development/evidence/handoff-2026-11-18-antigravity.md`.
- Dependencies / current task state / unblock conditions:
  - `DEV-007`, `DEV-008`, `DEV-009` are `done`.
  - `DEV-010` is `in_progress` and **held** on the AUTH-010 scanner OpenSSL finding (`CVE-2026-107496` in `libssl3t64` `3.0.13-0ubuntu3.16`) and remaining parser/scanner asset qualification.
- Current phase / phase-gate ID and status in `development/phase-gates.json`:
  - `F3` (`Identity, consent, curriculum and safe upload`): `in_progress`.
- Prior-phase required tests/reviewer/transition status; is this phase allowed to start?:
  - `F0`, `F1`, and `F2` are `passed` with recorded evidence and independent review. `F3` is allowed to run under `AUTH-004`. `F4`–`F8` are `not_started` and blocked until `F3` passes all exit suites and independent review.

## Repository checkpoint

- Repository / verified remote: `https://github.com/EldonsLogic/sebaverse` (`origin`).
- Branch / worktree path: `antigravity/dev-010-handover` at `/Users/eldon/Documents/Sebaverse` (branched from `main` at `bff322a00cdc824496dd262907b0ceb61116d573`).
- HEAD commit SHA:
  - Prior `main` HEAD: `bff322a00cdc824496dd262907b0ceb61116d573` (`Record bounded parser and scanner holds and authorized alternate assessments`).
  - Codex checkpoint commit on `antigravity/dev-010-handover`: `baa2db0` (`DEV-010: checkpoint Codex in-progress scanner review as found`).
  - Handover commit on `antigravity/dev-010-handover`: `dc1b9ba` (`DEV-010: record AUTH-010 OpenSSL CVE-2026-107496 hold and Antigravity handover`), followed by a one-line PR/SHA reference update commit.
- Remote branch SHA / verification command and result:
  - Command: `git push -u origin antigravity/dev-010-handover` and `gh pr create --base main --head antigravity/dev-010-handover --title "DEV-010: Antigravity handover" ...`
  - Result: Opened Pull Request **#4** (`https://github.com/EldonsLogic/sebaverse/pull/4`) into `main` (not merged).
- Working-tree state (`git status --short` summary):
  - Clean (`git status --short` produces empty output after committing the handover records). Ignored scratch files under `work/dev-010/` remain untouched on disk.
- Committed versus uncommitted work and its owner:
  - All 19 files from Codex's unfinished session were committed verbatim in `baa2db0` (`owner: /root` / Codex & its Sol subagents).
  - All 4 handover/evidence files from Antigravity were committed in the subsequent commit (`owner: /antigravity`).
  - Zero uncommitted tracked files remain.
- Conflict/divergence status; work that must not be overwritten:
  - `antigravity/dev-010-handover` is a clean fast-forward descendant of `main` (`bff322a00cdc824496dd262907b0ceb61116d573`). Do not overwrite `baa2db0` or the ignored local artifacts in `work/dev-010/`.

## Work and evidence

- Concrete changes completed:
  1. Created branch `antigravity/dev-010-handover` from `main` (`bff322a`) and verified that Codex's 19 modified/new files passed all four validation/foundation/economics/unit-test suites before committing them verbatim as `baa2db0` (`DEV-010: checkpoint Codex in-progress scanner review as found`).
  2. Investigated the open AUTH-010 package-route item (`CVE-2026-107496` on Ubuntu 24.04 LTS Noble `libssl3t64` `3.0.13-0ubuntu3.16` for ClamAV `1.5.4+dfsg-0ubuntu0.24.04.1`) using primary upstream/Canonical advisories, Launchpad archive API metadata, signed Debian source patch archives, and static ELF symbol/disassembly analysis of the extracted binaries in `work/dev-010/scanner-package-route/`:
     - Verified live `https://security.ubuntu.com/ubuntu/dists/noble-security/InRelease` is unchanged from `Wed, 18 Nov 2026 14:10:15 UTC` (SHA-256 `473f6353b8a017c8ad783a92c13875f0d8ef33a38c0df55547ce14804056fbf8`).
     - Verified live `https://ubuntu.com/security/cves/CVE-2026-107496.json` still lists `openssl` on `noble` as `needs-triage` ("Needs evaluation"), Ubuntu priority `Medium`, CVSS v3.1 `7.5 High`, with no USN.
     - Verified via Launchpad API (`getPublishedSources` for `openssl` in `noble`) that `Security` and `Updates` remain at `3.0.13-0ubuntu3.16` (all 79 patches in `openssl_3.0.13-0ubuntu3.16.debian.tar.xz` checked; no named CVE-2026-107496 patch or relevant EC group order-1 fix identified; unrelated CMS_encrypt references exist), and `Proposed` has `3.0.13-0ubuntu3.17` (which only adds `d/p/revert-engine-legacy-key-detection.patch` for `LP: #2158304`, not `CVE-2026-107496`).
     - Verified from `https://openssl-library.org/news/secadv/20261110.txt` that `CVE-2026-107496` (OpenSSL severity `Low`, CWE-835 infinite loop in `CMS_encrypt()` / `CMS_encrypt_ex()` when encrypting to an attacker-supplied EC certificate with explicit group order 1) has public fixes scheduled for 1 December 2026 (`3.0.24` is listed as premium support only).
     - Performed static ELF symbol and `.text` disassembly check on `/usr/bin/clamscan` (`3c9a2ab59a256988dac497bbb7c5e3dd98180cef846b32088a304dc604d2a3ee`) and `/usr/lib/x86_64-linux-gnu/libclamav.so.12.1.0` (`9b343754e2c867b15871711828d8a25191f679b01ff8e5ac3016d1efd5205ded`) via `llvm-objdump`:
       - `clamscan` imports zero `CMS_*` or `PKCS7_*` symbols.
       - `libclamav.so.12.1.0` imports `CMS_encrypt` (`0000000000c795b8 R_X86_64_GLOB_DAT CMS_encrypt`), which is referenced at only one call instruction (`0x90b151: callq *0x36e461(%rip) # 0xc795b8`) inside a Rust `openssl::cms::CmsContentInfo::encrypt` wrapper function at `0x90b0e0`.
       - Full disassembly search across `libclamav.so.12.1.0` found no direct references (`callq`, `jmp`, `leaq`, or data relocations) to `0x90b0e0` (or the adjacent `CMS_verify` wrapper at `0x90aea0`).
     - Concluded that because the package-level finding on `libssl3t64` `3.0.13-0ubuntu3.16` remains unfixed (`needs-triage`, CVSS 7.5 High) and AUTH-010 forbids scanner exceptions or custom compilation, the Noble package route must remain on **hold** pending a founder decision.
  3. Appended the full investigation, exact source locators/hashes, open items, and three prepared founder options to [development/evidence/dev-010.md](dev-010.md).
  4. Rewrote [development/CURRENT-STATE.md](../CURRENT-STATE.md) concisely (under 5 KB and 10 lines/bullets) reflecting the 18 November 2026 checkpoint on `antigravity/dev-010-handover`.
  5. Updated [development/agents/roster.json](../agents/roster.json) with `/antigravity`'s actual roles, status, and touched files.
- Acceptance met / not met, with artifact paths and locators:
  - `DEV-010` overall acceptance: **Not met yet (`in_progress` / held).**
  - Met earlier in `DEV-010` (at `6093bff` / `bff322a`): private upload broker allocation, quotas, manifests, withdrawal/purge, 31 ingestion unit tests, 366 database-free backend tests, and hosted PostgreSQL broker probe (14 scenarios + 30 injection fixtures) in [development/evidence/dev-010.md](dev-010.md).
  - Not met yet: qualified scanner runtime/definitions (`infra/scanner/package-route-review.md`, `infra/scanner/approved-assets.json` still empty), qualified parser native/notice/runtime closure (`workers/parser/alternate-review.md`), and F3 phase-exit test suites (`make test-authorization`, `make test-consent`, `make test-ingestion`, `make test-content-isolation`).
- Actual verification commands, exit codes/results and fixture/version:
  1. `python3 tools/brief.py DEV-010` -> exit code `0` (printed DEV-010 task contract, R037–R042/R046, and F3 gate status).
  2. `python3 tools/validate_project.py` -> exit code `0` (`Status: PASS`, 36 preserved files match SHA-256 manifest, 13 global + 14 audit Markdown deliverables present, 105 requirement rows checked, 0 errors, 0 warnings).
  3. `python3 tools/check_foundation.py` -> exit code `0` (`Foundation checks: PASS`, 26 tasks, 9 ordered phase gates, 30 role contracts in six functions).
  4. `python3 tools/model_economics.py` -> exit code `0` (`Recomputed planning scenarios; unknown full-cost inputs remain explicit.`).
  5. `python3 -m unittest discover -s tools/tests -p 'test_*.py'` -> exit code `0` (`Ran 163 tests in 5.586s — OK`; re-run after handover edits also passed `163` tests with `OK`).
  6. Static binary inspection commands (read-only on extracted artifacts in `work/dev-010/scanner-package-route/`):
     - `/Library/Developer/CommandLineTools/usr/bin/llvm-objdump --dynamic-syms work/dev-010/scanner-package-route/clamscan` -> exit code `0` (0 `CMS_*`/`PKCS7_*` symbols).
     - `/Library/Developer/CommandLineTools/usr/bin/llvm-objdump --dynamic-syms work/dev-010/scanner-package-route/libclamav.so.12.1.0` -> exit code `0` (9 `CMS_*`/`PKCS7_*` symbols including `CMS_encrypt`).
     - `/Library/Developer/CommandLineTools/usr/bin/llvm-objdump -R work/dev-010/scanner-package-route/libclamav.so.12.1.0` -> exit code `0` (`0000000000c795b8 R_X86_64_GLOB_DAT CMS_encrypt`).
     - `/Library/Developer/CommandLineTools/usr/bin/llvm-objdump -d work/dev-010/scanner-package-route/libclamav.so.12.1.0` -> exit code `0` (verified single `CMS_encrypt` call site at `0x90b151` inside the inspected wrapper `0x90b0e0` with no direct references found).
- Checks not run or failed, and why:
  - No failure occurred in any run check.
  - Did **not** run scanner, parser, model, or local macOS PostgreSQL database tests (`make test-authorization`, `make test-consent`, `make test-ingestion`, `make test-content-isolation`), per explicit instruction and existing holds (`local macOS database use remains held`; scanner and parser assets are not approved or installed).
- Independent review (actual reviewer, scope, result) or not performed:
  - Not performed for this handover documentation checkpoint; Codex will review the PR (`DEV-010: Antigravity handover`) upon resuming.
- Phase-required suites and exact result/evidence for each; identify missing/fail/not-run items:
  - `F3` phase gate (`development/phase-gates.json`) remains `in_progress`; all four phase exit suites remain `not_run` at the phase-gate level (`make test-authorization`, `make test-consent`, `make test-ingestion`, `make test-content-isolation`).
- Phase acceptance/reviewer verdict and transition decision recorded in `development/phase-gates.json`:
  - `F3` status: `in_progress`, review result: `pending`. No phase transition claimed or recorded.
- Relevant changes after testing/review that invalidate evidence and require re-run:
  - None. No files bound by `infra/security-reviewed-findings.json` or `infra/synthetic-openssl-review.json` (`backend/`, `tools/`, `infra/images.lock.json`, `infra/local/postgres/`, `.github/workflows/skeleton.yml`) were modified on `antigravity/dev-010-handover`.
- New decisions/risks and their canonical register IDs:
  - No register IDs were modified beyond Codex's checkpointed changes in `baa2db0`. The AUTH-010 scanner hold and options are recorded in [development/evidence/dev-010.md](dev-010.md).
- Known defects, limitations and outstanding external conditions:
  - Ubuntu 24.04 LTS Noble `libssl3t64` `3.0.13-0ubuntu3.16` remains `needs-triage` for `CVE-2026-107496` (CVSS 7.5 High / OpenSSL Low), and upstream OpenSSL public fix releases are scheduled for 1 December 2026 (`3.0.24` is listed as premium support only).
  - Full Noble runtime dependency SBOM/advisory/KEV scan, `clamav-freshclam`/`clamav-data` offline definition bundle verification, bundled Rust/native notice closure, and AUTH-008 alternate parser (`pypdfium2` `libpdfium.so`) native/shared-wheel closure remain open.
  - `AUTH-007` and `AUTH-005` expire on **20 November 2026** (`11:39:06 UTC` and `19:38:23 UTC` respectively).

## Resume action

- Exact next safe command/task and expected result:
  ```bash
  git status --short && git log -3 --oneline && python3 tools/brief.py DEV-010
  ```
  Expected result: clean working tree on `antigravity/dev-010-handover` (or after Codex reviews and merges PR into `main`), showing the two commits above `bff322a` and `DEV-010` `in_progress`.
- Remaining steps in order:
  1. **Codex reviews PR `"DEV-010: Antigravity handover"`** (`antigravity/dev-010-handover` -> `main`), verifies the verbatim checkpoint commit `baa2db0` and the handover commit, and merges or cherry-picks into `main`.
  2. **Founder decisions needed:**
     - Decide on expiring CI exceptions before **20 November 2026**: `AUTH-007` (`11:39:06 UTC`) and `AUTH-005` (`19:38:23 UTC`), plus native reviews expiring 21 November 2026.
     - Choose one of the three scanner options in [development/evidence/dev-010.md](dev-010.md#prepared-founder-options-for-the-auth-010-scanner-hold):
       - **Option 1 (proposal requiring a new scanner-specific decision and independent applicability review):** Authorize a hash-bound, expiring synthetic-CI applicability exception for `CVE-2026-107496` on Noble `libssl3t64` `3.0.13-0ubuntu3.16` based on OpenSSL's Low severity and static ELF observations that `CMS_encrypt` in `libclamav.so.12.1.0` (`0x90b0e0` -> `0x90b151`) has no direct references identified; this does not prove it is unreachable.
       - **Option 2:** Keep the scanner on hold until Canonical publishes a Noble `libssl3t64` fix or triage decision (or after the 1 December 2026 OpenSSL release window), while continuing AUTH-008 parser native/notice closure.
       - **Option 3:** Authorize an ADR amendment and assessment for a non-OpenSSL-CMS scanner alternative (not recommended).
  3. **Continue AUTH-008 parser assessment (within remaining 1-day budget):** Complete static provenance/notice inspection for `pypdfium2` (`libpdfium.so`) and shared wheels in `workers/parser/alternate-review.md`.
  4. **After scanner and parser holds are resolved and independently reviewed:** Run isolated synthetic execution tests, complete `DEV-010`, and run mandatory `F3` exit suites (`make test-authorization`, `make test-consent`, `make test-ingestion`, `make test-content-isolation`).
- File ownership transfer / release:
  - `/antigravity` status in `development/agents/roster.json` is marked `completed` and all file ownership is released back to `/root` (Codex).
- Conditions that require a founder decision before dependent work:
  - Expiring `AUTH-007` (20 Nov 11:39 UTC) and `AUTH-005` (20 Nov 19:38 UTC) exceptions.
  - Scanner `CVE-2026-107496` hold resolution (Option 1 vs. Option 2 vs. Option 3).
  - Question/uncertainty recorded for founder/Codex: none of Codex's files or `infra/scanner/package-route-review.md` were edited after `baa2db0` so that Codex's checkpoint remained strictly separated from Antigravity's additions in `development/evidence/dev-010.md`; if Codex wants the static `llvm-objdump` disassembly note (`0x90b0e0` -> `0x90b151` inspected `CMS_encrypt` wrapper) mirrored directly inside `infra/scanner/package-route-review.md` and `infra/scanner/package-route-candidate.json`, Codex can fold that in after reviewing this PR.
- Safe checkpoint/rollback and recovery notes:
  - `main` is untouched at `bff322a00cdc824496dd262907b0ceb61116d573`.
  - Commit `baa2db0` on `antigravity/dev-010-handover` has Codex's exact working tree as found. Use a reviewed revert of the specific documentation commit if needed; preserve later work and shared history.
