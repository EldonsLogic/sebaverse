# GitHub source of truth and commit workflow

Canonical remote: https://github.com/EldonsLogic/sebaverse (private, push access verified 11 November 2026). Preserve the original local main history; initial remote was empty. Never publish secrets, real child data, ignored scratch or another project's files. Private repository status is not a secrets control. Do not change visibility.

1. Inspect branch, HEAD, working tree and remote. Claim task/files; do not discard another agent's changes.
2. Fetch and compare before integrating. If shared work diverged, preserve both histories through reviewed merge/PR; never force push. Never amend or rewrite published commits by default.
3. Implement a small coherent task, update docs/task state, run relevant checks and obtain the required review. Commit reviewable milestones and checkpoints; do not wait for an entire product phase or commit every keystroke.
4. Stage explicit intended files, inspect staged diff and file list, run credential/privacy checks, commit with task IDs. The orchestrator handles initial main push; concurrent work uses task branches/PRs or isolated worktrees with explicit integration owner.
5. Push to the authorized repo, then compare local HEAD and remote branch SHA. A local commit is not a verified push. Record branch/SHA and actual checks in current state/handoff. Failed/offline push remains pending and must be reported honestly.
6. At phase boundary rerun the phase's complete required suite, record results/reviewer and blockers, and advance phase-gates.json only after pass. Fixes rerun affected checks plus applicable phase suite; no fabricated results or lowered threshold.

The initial foundation workflow runs read-only checks on push/PR. It does not deploy, mutate code, call models, send messages or run uploaded/research scripts. Official Actions revisions are SHA-pinned. Hosted actions require repository availability/allowance; no purchase or paid live comparison is implied. Instructions for a new agent are in START-HERE.md and HANDOVER.md.
