# Current development handover

This is the live entry point for the next agent. Update it after each meaningful checkpoint and before interruption/context handoff. It complements development/tasks.json and task reports; it does not replace root AGENTS.md, requirements, ADRs or recorded gate approvals.

## Current objective

Establish the development foundation and step-by-step roadmap, integrate the user-selected coding/orchestration guidance with Sebaverse’s rules, and commit/push coherent work to [EldonsLogic/sebaverse](https://github.com/EldonsLogic/sebaverse). The owner has explicitly authorized GitHub commits/pushes. Root orchestration is checking and integrating the foundation; this file must not imply that integration or remote publication has already succeeded.

## Verified context versus current-session work

- Canonical project: `/Users/eldon/Documents/Sebaverse`; original repository/history retained. The former TBD shortcut was removed in the prior session.
- Architecture selected: Django/DRF + React/TypeScript/Vite + PostgreSQL; subject-independent profiles/content/adapters; isolated ingestion; no whole tutoring/LMS adopted. DeepTutor remains reference-only baseline.
- Brand selected: C visual identity + B blue/orange; Latin Sebaverse logo; no permanent slogan or recurring door-based wording selected.
- Baseline prior to this foundation task: architecture audit v1 and 99 requirements. New requirement counts must be read from the current register, not assumed from this historical snapshot.
- Root verified this session that the named GitHub repository is private and push permission is available; it was empty at inspection. Remote contents can change; fetch/inspect before integration. No worker should infer it remains empty.
- No product implementation, paid model benchmark, real-minor pilot or deployment is established by this handover. Current source/architecture and applicable execution gates remain authoritative.

## Live state and durable protocol

[CURRENT-STATE.md](CURRENT-STATE.md) is the single live session checkpoint: actual branch/HEAD, dirty files and ownership, DEV task IDs, tests, review, phase-gate status and remote synchronization evidence. This file records the durable handover protocol and context; do not maintain a competing copy of live Git/task status here. On resume, compare CURRENT-STATE.md with actual Git/files before trusting it.

The integrating agent must update CURRENT-STATE.md before stopping, using the [task-handoff template](templates/task-handoff.md) for any scoped transfer. Record unknown/not-run conditions instead of inventing SHAs, completed reviews or approvals. development/tasks.json uses planned, ready, in_progress, review, blocked and done; state changes require the evidence described in WORKFLOW.md. Under U14, development/phase-gates.json separately records required tests, actual evidence, reviewer and transition readiness for each phase. No new agent may start the next phase while prior required tests/review are missing, failing, not-run or unresolved. Documentation checks do not establish product-phase readiness.

## Exact next safe steps

1. Root integrates roadmap/tasks, canonical agent rules, guidance provenance/image extraction and foundation tooling. Resolve references and status vocabulary consistently across files.
2. Run `python3 tools/model_economics.py` and `python3 tools/validate_project.py`; run `python3 tools/check_foundation.py` when its file exists. Record actual results, including failures/not-run checks. These verify documents/tooling only.
3. Perform independent review where available; correct findings within scope. Review staged changes and preserve immutable research/frozen outputs.
4. Commit scoped coherent changes, push to the verified Sebaverse branch without overwriting remote history, and verify remote SHA. Root must update CURRENT-STATE.md with actual task IDs, commit/branch, checks and synchronization evidence.
5. At the end of every phase, run its required meaningful tests against the final changes, record actual test evidence and reviewer result in development/phase-gates.json, and hold the boundary until every required acceptance/test/review condition passes. Only then select a ready task from the next phase. Before product implementation, verify the applicable actual gate record and dependency/license closure; do not interpret foundation completion or an attractive diagram as all approvals.

## Resume protocol for a different agent

Follow [WORKFLOW.md](WORKFLOW.md), beginning with the exact read order and Git inspection. Use [task-handoff template](templates/task-handoff.md) for a transfer with specific scope. Record any divergence from this handover before editing. Do not ask the founder to repeat information already in the current source/decision registers, and do not block subject-independent architecture on a particular German upload.
