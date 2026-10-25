import queue
import tempfile
import threading
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from governor_workbench.jobs import JobRunner
from governor_workbench.operator_questions import OperatorQuestions
from governor_workbench.store import Store
from governor_workbench.execution_workspace import _sha, _root


class QuestionSourceDriftTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()
        self.root = self.base / 'project'
        self.root.mkdir()
        self.path = self.root / 'main.py'
        self.path.write_bytes(b'original')
        self.store = Store(self.base / 'journal.db')
        self.questions = OperatorQuestions(self.store)
        self.context = dict(scope_hash='a' * 64, review_scope={'kind': 'project', 'id': 'p'},
                            registry_projects=[{'id': 'p', 'path': str(self.root)}],
                            intake=[], plan_ready=True, decision_hash='b' * 64)
        self.app = SimpleNamespace(store=self.store, questions=self.questions,
            settings=lambda: dict(reasoning_mode='medium',supervisor='gpt-5.6-sol'),
            scope_context=Mock(return_value=self.context), event=Mock(),
            config=dict(router_url='http://127.0.0.1:3000/v1', model_timeout=1,
                        router_api_key_env='', orchestrator_transport='router', data_dir=str(self.base)))
        self.runner = JobRunner.__new__(JobRunner)
        self.runner.app = self.app
        self.runner.lock = threading.Lock()
        self.runner.pending = queue.Queue()
        self.runner.cancellations = {}
        self.job = self.store.create_job('scope_patch', None,
            {'scope_kind': 'project', 'scope_id': 'p', 'scope_hash': 'a' * 64,
             'candidate_id': 'candidate', 'step_id': 'step'})
        self.store.update_job(self.job['id'], status='running')
        self.question = {'text': 'Which target?', 'reason': 'Ambiguous target'}

    def binding(self, absent=False):
        return {'root': str(self.root), 'root_identity': _root(str(self.root))[1],
                'hashes': {'main.py': None if absent else _sha(b'original')}}

    def ask(self, absent=False):
        return self.questions.ask(self.job['id'], self.question, 'a' * 64, 'project', 'p',
            'gpt-5.6-sol', result={'question_source_binding': self.binding(absent)})

    def test_existing_untracked_drift_rejected_before_answer_saved(self):
        q = self.ask()
        self.path.write_bytes(b'changed untracked')
        with patch('governor_workbench.jobs.RouterClient') as client:
            with self.assertRaises(ValueError):
                self.runner.answer_question(q['id'], 'The existing target', 'a' * 64)
            client.assert_not_called()
        self.assertEqual('pending', self.questions.get(q['id'])['status'])
        self.assertEqual('waiting_for_operator', self.store.job(self.job['id'])['status'])
        self.assertTrue(self.runner.pending.empty())

    def test_absent_file_created_while_waiting_rejects_answer(self):
        self.path.unlink()
        q = self.ask(absent=True)
        self.path.write_bytes(b'new file')
        with self.assertRaises(ValueError):
            self.runner.answer_question(q['id'], 'Target', 'a' * 64)
        self.assertEqual('pending', self.questions.get(q['id'])['status'])

    def test_drift_after_saved_answer_rejected_before_model_call(self):
        q = self.ask()
        self.runner.answer_question(q['id'], 'Target', 'a' * 64)
        self.path.write_bytes(b'changed after queuing')
        with patch('governor_workbench.question_llm.assess_answer') as assess:
            with self.assertRaisesRegex(ValueError, 'Quellen'):
                self.runner.execute(self.store.job(self.job['id']), 'gpt-5.6-sol', threading.Event())
            assess.assert_not_called()

    def test_question_result_seals_original_sources_and_detects_model_time_drift(self):
        step = {'id': 'step', 'project_id': 'p', 'scope': ['main.py'], 'action': 'change'}
        candidate = {'id': 'candidate', 'proposal': {'steps': [step]}}
        def propose(*args, **kwargs):
            self.path.write_bytes(b'changed during review')
            return {'operator_question': self.question, 'review': {}, 'calls': []}
        with patch('governor_workbench.plans.PlanBook') as book, \
             patch('governor_workbench.change_execution.PlanBook', book), \
             patch('governor_workbench.execution_policy.require_staging_pilot', return_value=step), \
             patch('governor_workbench.execution_policy.pilot_model_context', return_value=self.context), \
             patch('governor_workbench.patch_llm.propose_patch', side_effect=propose):
            book.return_value.get.return_value = candidate
            result = self.runner.execute(self.job, 'gpt-5.6-sol', threading.Event())
        self.assertTrue(result['stale'])
        self.assertEqual(_sha(b'original'), result['question_source_binding']['hashes']['main.py'])
        self.assertEqual([], self.questions.list())

    def test_drift_between_execute_and_waiting_insertion_creates_no_question(self):
        result = {'operator_question': self.question, 'scope_hash': 'a' * 64,
                  'question_source_binding': self.binding(), 'stale': False}
        self.path.write_bytes(b'changed before waiting insertion')
        self.app.stop_event = threading.Event()
        self.app.bump = Mock()
        def execute(*args):
            self.app.stop_event.set()
            return result
        self.runner.execute = Mock(side_effect=execute)
        self.runner.cancellations[self.job['id']] = threading.Event()
        self.runner.pending.put((self.job, 'gpt-5.6-sol'))
        self.runner.worker()
        self.assertEqual('failed', self.store.job(self.job['id'])['status'])
        self.assertEqual([], self.questions.list())
        self.assertEqual(result, self.store.job(self.job['id'])['result'])

    def test_old_patch_question_without_exact_binding_fails_closed(self):
        q = self.questions.ask(self.job['id'], self.question, 'a' * 64, 'project', 'p', 'gpt-5.6-sol')
        with self.assertRaises(ValueError):
            self.runner.answer_question(q['id'], 'Target', 'a' * 64)
        self.assertEqual('pending', self.questions.get(q['id'])['status'])


if __name__ == '__main__': unittest.main()
