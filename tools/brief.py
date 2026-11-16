#!/usr/bin/env python3
"""Print a compact working brief so an agent need not load the full registers.

    python3 tools/brief.py            # phase status and the next eligible tasks
    python3 tools/brief.py DEV-007    # one task, its requirement rows and its phase gate
    python3 tools/brief.py R044 R045  # specific requirement rows

Read-only. It reports what the registers say; it does not verify that work was done.
"""
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]


def load(root=ROOT):
    read = lambda name: json.loads((root / name).read_text())
    return (read('development/tasks.json')['tasks'],
            read('development/phase-gates.json')['phases'],
            {row['id']: row for row in read('registers/requirements.json')})


def requirement_line(row):
    return (f"{row['id']} [{row.get('priority', '?')}] {row['requirement']}: "
            f"{row.get('acceptance_criteria', '')} (spec: {row.get('specification', 'none')})")


def gate_lines(phase):
    lines = [f"{phase['id']} {phase['name']}: {phase['status']}"]
    for test in phase.get('tests', []):
        lines.append(f"  - {test.get('suite') or test.get('id')}: {test.get('result')}"
                     f" ({test.get('command') or 'command not yet defined'})")
    for blocker in phase.get('blockers', []):
        lines.append(f"  ! blocker: {blocker}")
    return lines


def overview(tasks, phases):
    lines = ['Phases: ' + ', '.join(f"{p['id']}={p['status']}" for p in phases)]
    passed = {p['id'] for p in phases if p['status'] == 'passed'}
    done = {t['id'] for t in tasks if t['status'] == 'done'}
    by_id = {p['id']: p for p in phases}
    for task in tasks:
        if task['status'] == 'done':
            continue
        prior = by_id[task['phase']].get('depends_on', [])
        eligible = set(prior) <= passed and set(task.get('dependencies', [])) <= done
        if task['status'] != 'planned' or eligible:
            lines.append(f"{task['id']} {task['phase']} {task['status']}"
                         f"{' (dependencies met)' if eligible else ''}: {task['title']}")
    return lines


def task_brief(task, phases, requirements):
    lines = [f"{task['id']} {task['phase']} {task['status']}: {task['title']}",
             'Depends on: ' + (', '.join(task.get('dependencies', [])) or 'none'),
             'Files: ' + ', '.join(task.get('files', [])),
             'Condition: ' + task.get('execution_condition', 'none recorded'),
             'Acceptance:']
    lines += ['  - ' + item for item in task.get('acceptance_criteria', [])]
    lines.append('Checks: ' + ', '.join(task.get('verification', [])))
    lines.append('Requirements:')
    lines += ['  ' + requirement_line(requirements[r]) for r in task['requirements'] if r in requirements]
    lines.append('Phase gate:')
    lines += ['  ' + line for p in phases if p['id'] == task['phase'] for line in gate_lines(p)]
    return lines


def brief(arguments, tasks, phases, requirements):
    if not arguments:
        return overview(tasks, phases), 0
    lines, status = [], 0
    tasks_by_id = {t['id']: t for t in tasks}
    for name in arguments:
        if name in tasks_by_id:
            lines += task_brief(tasks_by_id[name], phases, requirements)
        elif name in requirements:
            lines.append(requirement_line(requirements[name]))
        else:
            lines.append(f'Unknown task or requirement ID: {name}')
            status = 1
    return lines, status


def main():
    lines, status = brief(sys.argv[1:], *load())
    print('\n'.join(lines))
    return status


if __name__ == '__main__':
    sys.exit(main())
