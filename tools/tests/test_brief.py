"""The working brief must stay small and must not misreport eligibility."""
from pathlib import Path
import importlib.util
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('brief', ROOT / 'tools/brief.py')
brief = importlib.util.module_from_spec(spec)
spec.loader.exec_module(brief)

PHASES = [
    {'id': 'F0', 'name': 'Foundation', 'status': 'passed', 'depends_on': [], 'tests': [], 'blockers': []},
    {'id': 'F1', 'name': 'Next', 'status': 'not_started', 'depends_on': ['F0'], 'blockers': ['waiting'],
     'tests': [{'id': 'F1-1', 'suite': 'Negatives', 'command': None, 'result': 'not_run'}]},
    {'id': 'F2', 'name': 'Later', 'status': 'not_started', 'depends_on': ['F1'], 'tests': [], 'blockers': []},
]
TASKS = [
    {'id': 'DEV-001', 'phase': 'F0', 'status': 'done', 'title': 'Done work', 'requirements': ['R001'], 'dependencies': []},
    {'id': 'DEV-002', 'phase': 'F1', 'status': 'planned', 'title': 'Eligible work', 'requirements': ['R001'],
     'dependencies': ['DEV-001'], 'acceptance_criteria': ['It works'], 'verification': ['make x'], 'files': ['a/']},
    {'id': 'DEV-003', 'phase': 'F2', 'status': 'planned', 'title': 'Held work', 'requirements': ['R001'], 'dependencies': ['DEV-002']},
]
REQUIREMENTS = {'R001': {'id': 'R001', 'requirement': 'Scope', 'priority': 'P0',
                         'acceptance_criteria': 'Scoped before ranking', 'specification': 'docs/x.md'}}


class BriefTests(unittest.TestCase):
    def test_overview_lists_only_eligible_or_active_work(self):
        text = '\n'.join(brief.brief([], TASKS, PHASES, REQUIREMENTS)[0])
        self.assertIn('DEV-002', text)
        self.assertIn('dependencies met', text)
        self.assertNotIn('DEV-001', text)
        self.assertNotIn('DEV-003', text)

    def test_task_brief_includes_requirements_and_gate(self):
        lines, status = brief.brief(['DEV-002'], TASKS, PHASES, REQUIREMENTS)
        text = '\n'.join(lines)
        self.assertEqual(0, status)
        self.assertIn('Scoped before ranking', text)
        self.assertIn('command not yet defined', text)
        self.assertIn('blocker: waiting', text)

    def test_unknown_id_fails(self):
        lines, status = brief.brief(['DEV-999'], TASKS, PHASES, REQUIREMENTS)
        self.assertEqual(1, status)
        self.assertIn('Unknown', lines[0])

    def test_real_registers_produce_a_small_brief(self):
        tasks, phases, requirements = brief.load()
        lines, status = brief.brief([tasks[-1]['id']], tasks, phases, requirements)
        self.assertEqual(0, status)
        self.assertLess(len('\n'.join(lines)), 8000)
        self.assertLess(len('\n'.join(brief.brief([], tasks, phases, requirements)[0])), 4000)


if __name__ == '__main__':
    unittest.main()
