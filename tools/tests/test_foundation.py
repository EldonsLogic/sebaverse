"""Negative fixtures exercise the phase barrier without running product code."""
from pathlib import Path
import importlib.util
import json
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('foundation', ROOT / 'tools/check_foundation.py')
foundation = importlib.util.module_from_spec(spec)
spec.loader.exec_module(foundation)


class FoundationGuardTests(unittest.TestCase):
    def setUp(self):
        read = lambda f: json.loads((ROOT / f).read_text())
        self.tasks = read('development/tasks.json')['tasks']
        self.phases = read('development/phase-gates.json')['phases']
        self.roles = read('development/agents/roles.json')['roles']
        self.reqs = {x['id'] for x in read('registers/requirements.json')}

    def errors(self):
        return foundation.validate_contracts(self.tasks, self.phases, self.roles, self.reqs, ROOT)

    def test_actual_contracts_valid(self):
        self.assertEqual([], self.errors())

    def test_unknown_requirement_rejected(self):
        self.tasks[0]['requirements'] = ['R-NOT-REAL']
        self.assertTrue(any('unknown requirement' in e for e in self.errors()))

    def test_task_cycle_rejected(self):
        self.tasks[0]['dependencies'] = [self.tasks[1]['id']]
        self.tasks[1]['dependencies'] = [self.tasks[0]['id']]
        self.assertTrue(any('cycle' in e for e in self.errors()))

    def test_next_phase_cannot_start_before_prior_passes(self):
        self.phases[0]['status'] = 'in_progress'
        next(t for t in self.tasks if t['phase'] == 'F1')['status'] = 'in_progress'
        self.assertTrue(any('started before' in e for e in self.errors()))

    def test_not_run_suite_cannot_pass_phase(self):
        self.phases[0]['status'] = 'passed'
        self.phases[0]['tests'][0]['result'] = 'not_run'
        self.assertTrue(any('not a real passing' in e for e in self.errors()))

    def test_absent_evidence_cannot_pass_phase(self):
        self.phases[0]['status'] = 'passed'
        self.phases[0]['tests'][0]['evidence'] = []
        self.assertTrue(any('missing evidence' in e for e in self.errors()))

    def test_no_review_cannot_pass_phase(self):
        self.phases[0]['status'] = 'passed'
        self.phases[0]['review']['result'] = 'pending'
        self.assertTrue(any('independent review' in e for e in self.errors()))

    def test_done_task_without_evidence_rejected(self):
        self.tasks[0]['status'] = 'done'
        self.tasks[0]['evidence'] = []
        self.assertTrue(any('done without evidence' in e for e in self.errors()))

    def test_done_task_with_nonexistent_evidence_rejected(self):
        self.tasks[0]['status'] = 'done'
        self.tasks[0]['evidence'] = ['development/evidence/nonexistent-review-fixture.md']
        self.assertTrue(any('done evidence file missing' in e for e in self.errors()))

    def test_passed_phase_requires_completed_tasks(self):
        self.phases[0]['status'] = 'passed'
        self.tasks[0]['status'] = 'in_progress'
        self.assertTrue(any('unfinished phase tasks' in e for e in self.errors()))

    def test_forward_phase_dependency_rejected(self):
        self.phases[0]['depends_on'] = ['F1']
        self.assertTrue(any('forward/self' in e for e in self.errors()))

    def test_done_dependency_not_completed_rejected(self):
        self.tasks[0]['status'] = 'in_progress'
        self.tasks[1]['status'] = 'done'
        self.tasks[1]['dependencies'] = [self.tasks[0]['id']]
        self.tasks[1]['evidence'] = ['fixture evidence']
        self.assertTrue(any('dependencies completed' in e for e in self.errors()))

    def test_missing_contract_rejected(self):
        self.roles.pop()
        self.assertTrue(any('30 unique' in e for e in self.errors()))

    def test_blocker_prevents_gate_pass(self):
        self.phases[0]['status'] = 'passed'
        self.phases[0]['blockers'] = ['required unresolved blocker']
        self.assertTrue(any('required blockers' in e for e in self.errors()))


if __name__ == '__main__':
    unittest.main()
