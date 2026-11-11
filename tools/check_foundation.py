"""Check development contracts and phase barriers. Does not execute task commands."""
from pathlib import Path
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
ACTIVE = {'in_progress', 'review', 'done'}
STATUSES = {'planned', 'ready', 'in_progress', 'blocked', 'review', 'done'}


def validate_contracts(tasks, phases, roles, requirements, root):
    errors = []
    by_task = {x.get('id'): x for x in tasks}
    by_phase = {x.get('id'): x for x in phases}
    if len(by_task) != len(tasks):
        errors.append('Duplicate task ID')
    if len(by_phase) != len(phases):
        errors.append('Duplicate phase ID')
    if len(roles) != 30 or len({x.get('id') for x in roles}) != 30:
        errors.append('Exactly 30 unique role contracts required; not 30 active agents')
    groups = {x.get('function') for x in roles}
    if groups != {'leadership', 'engineering', 'quality', 'research', 'evaluation', 'operations'}:
        errors.append('Six role functions required')
    for role in roles:
        for key in ['id', 'name', 'mission', 'tools', 'file_scope', 'inputs', 'outputs', 'tests', 'handoff', 'escalation']:
            if not role.get(key):
                errors.append('Incomplete role contract: ' + str(role.get('id')) + '/' + key)
    for task in tasks:
        tid = task.get('id', '<missing>')
        for key in ['id', 'title', 'phase', 'owner_role', 'files', 'acceptance_criteria', 'verification', 'requirements']:
            if not task.get(key):
                errors.append(tid + ' missing ' + key)
        if task.get('status') not in STATUSES:
            errors.append(tid + ' invalid status')
        if task.get('phase') not in by_phase:
            errors.append(tid + ' unknown phase')
        for req in task.get('requirements', []):
            if req not in requirements:
                errors.append(tid + ' unknown requirement ' + req)
        for dep in task.get('dependencies', []):
            if dep not in by_task:
                errors.append(tid + ' unknown dependency ' + dep)
        if task.get('status') == 'done' and not task.get('evidence'):
            errors.append(tid + ' done without evidence')
        if task.get('status') == 'done':
            for evidence in task.get('evidence', []):
                if not (root / evidence).is_file():
                    errors.append(tid + ' done evidence file missing: ' + evidence)
        if task.get('status') == 'done' and any(by_task[d].get('status') != 'done' for d in task.get('dependencies', []) if d in by_task):
            errors.append(tid + ' done before task dependencies completed')
    visiting, visited = set(), set()

    def visit(tid):
        if tid in visiting:
            errors.append('Task dependency cycle: ' + tid)
            return
        if tid in visited or tid not in by_task:
            return
        visiting.add(tid)
        for dep in by_task[tid].get('dependencies', []):
            visit(dep)
        visiting.remove(tid)
        visited.add(tid)
    for tid in by_task:
        visit(tid)
    for index, phase in enumerate(phases):
        pid = phase.get('id', '<missing>')
        if phase.get('status') not in {'not_started', 'in_progress', 'passed', 'blocked'}:
            errors.append(pid + ' invalid phase status')
        declared = set(phase.get('depends_on', []))
        if index and phases[index - 1]['id'] not in declared:
            errors.append(pid + ' missing preceding phase dependency')
        for dep in declared:
            if dep not in by_phase:
                errors.append(pid + ' unknown phase dependency')
            elif dep not in {p['id'] for p in phases[:index]}:
                errors.append(pid + ' invalid forward/self phase dependency')
        preceding = phases[:index]
        started = phase.get('status') in {'in_progress', 'passed'} or any(
            t.get('phase') == pid and t.get('status') in ACTIVE for t in tasks)
        if started and any(p.get('status') != 'passed' for p in preceding):
            errors.append(pid + ' started before previous phases passed')
        if phase.get('status') == 'passed':
            if any(t.get('phase') == pid and t.get('status') != 'done' for t in tasks):
                errors.append(pid + ' passed with unfinished phase tasks')
            required = [t for t in phase.get('tests', []) if t.get('required')]
            if not required:
                errors.append(pid + ' passed without required tests')
            for test in required:
                if test.get('result') != 'pass' or not test.get('command') or test.get('availability') != 'existing':
                    errors.append(pid + ' required test is not a real passing existing check: ' + test.get('id', '?'))
                if not test.get('evidence'):
                    errors.append(pid + ' required test missing evidence')
                for evidence in test.get('evidence', []):
                    if not (root / evidence).is_file():
                        errors.append(pid + ' evidence file missing: ' + evidence)
            review = phase.get('review', {})
            if review.get('result') != 'pass' or not review.get('reviewer') or not review.get('evidence'):
                errors.append(pid + ' passed without recorded independent review')
            for evidence in review.get('evidence', []):
                if not (root / evidence).is_file():
                    errors.append(pid + ' review evidence file missing')
            if phase.get('blockers'):
                errors.append(pid + ' passed with required blockers')
    return errors


def main():
    required_files = [
        'AGENTS.md', 'CLAUDE.md', '.agents/rules/sebaverse.md',
        '.github/workflows/foundation.yml', 'development/START-HERE.md',
        'development/CURRENT-STATE.md', 'development/ROADMAP.md',
        'development/WORKFLOW.md', 'development/HANDOVER.md',
        'development/ENGINEERING_RULES.md', 'development/GITHUB-WORKFLOW.md',
        'development/APPROVALS.md', 'sources/agent-guidance/agent-team-transcription.md',
    ]
    errors = ['Missing ' + f for f in required_files if not (ROOT / f).is_file()]
    try:
        read = lambda f: json.loads((ROOT / f).read_text())
        tasks = read('development/tasks.json')['tasks']
        phases = read('development/phase-gates.json')['phases']
        roles = read('development/agents/roles.json')['roles']
        reqs = {x['id'] for x in read('registers/requirements.json')}
        errors += validate_contracts(tasks, phases, roles, reqs, ROOT)
        repo = read('development/repository.json')
        if repo['url'] != 'https://github.com/EldonsLogic/sebaverse':
            errors.append('Unexpected canonical GitHub repository')
        provenance = read('sources/agent-guidance/provenance.json')
        import hashlib
        source = provenance['image']
        if hashlib.sha256((ROOT / source['file']).read_bytes()).hexdigest() != source['sha256']:
            errors.append('Original prompt image hash mismatch')
        if '@AGENTS.md' not in (ROOT / 'CLAUDE.md').read_text():
            errors.append('Claude entry point must import canonical AGENTS.md')
        if 'trigger: always_on' not in (ROOT / '.agents/rules/sebaverse.md').read_text():
            errors.append('Antigravity always_on rule missing')
        workflow = (ROOT / '.github/workflows/foundation.yml').read_text()
        for action in re.findall(r'uses:\s*([^\s#]+)', workflow):
            if not re.fullmatch(r'[^@]+@[a-f0-9]{40}', action):
                errors.append('Unpinned third-party workflow action')
        if 'contents: read' not in workflow or 'persist-credentials: false' not in workflow:
            errors.append('Foundation workflow permission/credential safeguards missing')
        if 'pull_request_target:' in workflow:
            errors.append('Privileged PR trigger not allowed in foundation workflow')
        coverage = {x['requirement_id'] for x in read('architecture/feature-function-matrix.json')}
        if coverage != reqs:
            errors.append('Live feature/function matrix does not match requirement register')
        roster = read('development/agents/roster.json')
        if len(roster['agents']) > roster['max_concurrent_including_orchestrator']:
            errors.append('Recorded initial agent roster exceeds its bounded slot count')
    except (OSError, ValueError, KeyError) as exc:
        errors.append('Foundation document error: ' + str(exc))
    if errors:
        print('Foundation checks: FAIL')
        for error in errors:
            print('- ' + error)
        return 1
    print('Foundation checks: PASS')
    print(f'- {len(tasks)} tasks; {len(phases)} ordered phase gates; 30 role contracts in six functions.')
    print('- Requirement coverage, source image, client entry points and SHA-pinned CI checked.')
    print('- Passing gates require existing passing checks, evidence and independent review.')
    print('- No product tests, provider benchmarks or other-client loading inferred.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
