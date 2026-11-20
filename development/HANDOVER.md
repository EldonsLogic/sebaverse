# Current development handover

This is the live entry point for the next agent. Update it after each meaningful checkpoint and before interruption/context handoff. It complements development/tasks.json and task reports; it does not replace root AGENTS.md, requirements, ADRs or recorded gate approvals.

## Current objective

Build the F3 slice (DEV-007 onward) on the passed F2 skeleton, to the standard in [QUALITY-BAR.md](QUALITY-BAR.md). The live phase, task and next action are in [CURRENT-STATE.md](CURRENT-STATE.md); this file holds only the durable protocol and background.

## Background established during the foundation phase (11 November 2026)

- Canonical project: `/Users/eldon/Documents/Sebaverse`; original repository/history retained. The former TBD shortcut was removed in the prior session.
- Architecture selected: Django/DRF + React/TypeScript/Vite + PostgreSQL; subject-independent profiles/content/adapters; isolated ingestion; no whole tutoring/LMS adopted. DeepTutor remains reference-only baseline.
- Brand selected: C visual identity + B blue/orange; Latin Sebaverse logo; no permanent slogan or recurring door-based wording selected.
- Baseline prior to this foundation task: architecture audit v1 and 99 requirements. New requirement counts must be read from the current register, not assumed from this historical snapshot.
- The GitHub repository was private and empty when first connected on 11 November 2026. The founder made it public on 20 November under U24. It now holds the project history; fetch and inspect before integrating.
- No paid model benchmark, real-minor pilot or deployment is established by this handover. Implemented scope is whatever CURRENT-STATE.md and the passed phase gates record. Current source/architecture and applicable execution gates remain authoritative.

## Live state and durable protocol

[CURRENT-STATE.md](CURRENT-STATE.md) is the single live session checkpoint: actual branch/HEAD, dirty files and ownership, DEV task IDs, tests, review, phase-gate status and remote synchronization evidence. This file records the durable handover protocol and context; do not maintain a competing copy of live Git/task status here. On resume, compare CURRENT-STATE.md with actual Git/files before trusting it.

The integrating agent must update CURRENT-STATE.md before stopping, using the [task-handoff template](templates/task-handoff.md) for any scoped transfer. Record unknown/not-run conditions instead of inventing SHAs, completed reviews or approvals. development/tasks.json uses planned, ready, in_progress, review, blocked and done; state changes require the evidence described in WORKFLOW.md. Under U14, development/phase-gates.json separately records required tests, actual evidence, reviewer and transition readiness for each phase. No new agent may start the next phase while prior required tests/review are missing, failing, not-run or unresolved. Documentation checks do not establish product-phase readiness.

## Steps for every checkpoint

1. Run the checks the task and phase require, plus `make foundation-check` for foundation or document changes. Record actual results, including failures and checks not run.
2. Get independent review where the change warrants it and correct findings within scope.
3. Commit coherent changes, push without rewriting remote history and verify the remote SHA.
4. Update CURRENT-STATE.md so it is true and short. Remove what is no longer current.
5. At a phase exit, run the full required suite against the final changes, record evidence and reviewer in development/phase-gates.json, and hold the boundary until every required condition passes.

## Resume protocol for a different agent

Follow [WORKFLOW.md](WORKFLOW.md), beginning with the exact read order and Git inspection. Use [task-handoff template](templates/task-handoff.md) for a transfer with specific scope. Record any divergence from this handover before editing. Do not ask the founder to repeat information already in the current source/decision registers, and do not block subject-independent architecture on a particular German upload.
