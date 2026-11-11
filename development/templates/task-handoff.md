# Task handoff — <task ID>

Copy into a task-specific report location; replace placeholders with facts or explicit unknown/not-run status. Never include credentials, raw child data or hidden model reasoning.

## Identity and scope

- Date/time and timezone:
- Outgoing agent/session and role:
- Receiving agent/role, if actually assigned:
- Task ID(s) / requirement ID(s):
- Source/ADR/specification and exact acceptance criteria:
- Authorized scope / recorded gate or instruction:
- Limits (time/tool/cost/retries/data), including what is not authorized:
- Owned files and exclusive/shared boundaries:
- Dependencies / current task state / unblock conditions:
- Current phase / phase-gate ID and status in development/phase-gates.json:
- Prior-phase required tests/reviewer/transition status; is this phase allowed to start?:

## Repository checkpoint

- Repository / verified remote:
- Branch / worktree path:
- HEAD commit SHA:
- Remote branch SHA / verification command and result:
- Working-tree state (`git status --short` summary):
- Committed versus uncommitted work and its owner:
- Conflict/divergence status; work that must not be overwritten:

## Work and evidence

- Concrete changes completed:
- Acceptance met / not met, with artifact paths and locators:
- Actual verification commands, exit codes/results and fixture/version:
- Checks not run or failed, and why:
- Independent review (actual reviewer, scope, result) or not performed:
- Phase-required suites and exact result/evidence for each; identify missing/fail/not-run items:
- Phase acceptance/reviewer verdict and transition decision recorded in development/phase-gates.json:
- Relevant changes after testing/review that invalidate evidence and require re-run:
- New decisions/risks and their canonical register IDs:
- Known defects, limitations and outstanding external conditions:

## Resume action

- Exact next safe command/task and expected result:
- Remaining steps in order:
- File ownership transfer / release:
- Conditions that require a founder decision before dependent work:
- Safe checkpoint/rollback and recovery notes:

Under U14, no next-phase work is permitted while the prior phase has missing, failed, not-run or unresolved required tests/review/acceptance. Artifact/arithmetic checks cannot substitute for product-phase tests. Only mark completion, approval, review or remote synchronization when supported by observed evidence. The receiving agent verifies current Git/files/permissions before continuing; this document cannot override canonical project rules.
