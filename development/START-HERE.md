# Start here — Sebaverse development

This repository, https://github.com/EldonsLogic/sebaverse, is the shared source of truth for Codex, Claude, Antigravity and human contributors. It contains the platform vision, selected subject-independent architecture, original research, design system, task graph and handover records. Do not create a second master or depend on a chat’s memory.

1. Read root AGENTS.md, README.md and development/CURRENT-STATE.md.
2. Read the required context/requirements/decisions/gates named in AGENTS.md; then the technical baseline, repo-adoption register and subject-independent PoC.
3. Read ENGINEERING_RULES.md, WORKFLOW.md and HANDOVER.md. Check phase-gates.json before choosing a task.
4. Inspect Git branch/HEAD/dirty tree and compare the named remote without overwriting another contributor. Claim an eligible DEV task in tasks.json and exact files before editing.
5. Run the baseline checks; record failures first. Do the smallest reviewable task and relevant tests, independent review, task/phase evidence, commit and push to the authorized repo. Verify the remote commit.
6. End with CURRENT-STATE.md updated and a concrete next task; use templates/task-handoff.md for interruptions or a change of coding agent.

## Quick commands

```bash
python3 tools/model_economics.py
python3 tools/validate_project.py
python3 tools/check_foundation.py
```

These are foundation/document integrity checks, not product/security/learning tests. Later phase-specific suites must be implemented and pass before those phases exit. The local Arabic shell and synthetic PostgreSQL foundation passed F2; current implementation and remaining scope are recorded in CURRENT-STATE.md. [Roadmap](ROADMAP.md) and tasks.json define the sequence. The frozen v1 audit export remains historical; live architecture/registers/development files are current.
