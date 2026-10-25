import tempfile
import threading
import sqlite3
import unittest
from pathlib import Path

from governor_workbench.store import Store, JobBusy
from governor_workbench.operator_questions import OperatorQuestions


class OperatorQuestionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'journal.sqlite'
        self.store = Store(self.path)
        self.questions = OperatorQuestions(self.store)
        self.job = self.store.create_job('scope_review', None, {'scope_kind': 'project', 'scope_id': 'p'})
        self.store.update_job(self.job['id'], status='running', result={'evidence': 'retained'})

    def ask(self, **kwargs):
        return self.questions.ask(self.job['id'], {'text': '  Which target?  ', 'reason': 'Ambiguous target'},
                                  'a' * 64, 'project', 'p', 'gpt-5.6-sol', **kwargs)

    def answer(self, question, **kwargs):
        return self.questions.answer(question['id'], '  target one  ',
                                     kwargs.get('expected', 'a' * 64), kwargs.get('current', 'a' * 64))

    def test_wait_persists_and_answer_resumes_without_mutating_request(self):
        question = self.ask(result={'review': 'partial'})
        self.assertEqual('pending', question['status'])
        self.assertEqual('  Which target?  ', question['question']['text'])
        self.assertEqual('waiting_for_operator', self.store.job(self.job['id'])['status'])
        self.assertEqual('retained', self.store.job(self.job['id'])['result']['evidence'])
        restarted = Store(self.path)
        self.assertEqual('waiting_for_operator', restarted.job(self.job['id'])['status'])
        result = OperatorQuestions(restarted).answer(question['id'], '  target one  ', 'a' * 64, 'a' * 64)
        self.assertEqual('queued', result['job']['status'])
        self.assertEqual(self.job['request'], result['job']['request'])
        self.assertIsNone(result['job']['ended_at'])
        self.assertEqual('  target one  ', result['answer']['answer'])
        self.assertFalse(result['answer']['continuation_authorized'])
        self.assertEqual([{k: v for k, v in result['answer'].items() if k != 'review_evidence'}],
                         self.questions.answers(self.job['id']))
        with self.assertRaises(ValueError): self.answer(question)

    def test_drift_or_wrong_expected_hash_retains_pending_question(self):
        q = self.ask()
        for hashes in ({'expected': 'b' * 64}, {'current': 'b' * 64}, {'expected': '', 'current': ''}):
            with self.assertRaises(ValueError): self.answer(q, **hashes)
            self.assertEqual('pending', self.questions.get(q['id'])['status'])
            self.assertEqual('waiting_for_operator', self.store.job(self.job['id'])['status'])

    def test_other_active_job_blocks_answer_atomically(self):
        q = self.ask()
        other = self.store.create_job('refresh', None)
        with self.assertRaises(JobBusy): self.answer(q)
        self.assertEqual('pending', self.questions.get(q['id'])['status'])
        self.store.update_job(other['id'], status='completed')
        self.assertEqual('queued', self.answer(q)['job']['status'])

    def test_single_pending_and_max_three_immutable_rounds(self):
        history = []
        for revision in range(1, 4):
            q = self.ask()
            self.assertEqual(revision, q['revision'])
            with self.assertRaises(ValueError): self.ask()
            history.append(self.answer(q)['answer'])
            self.store.update_job(self.job['id'], status='running')
        with self.assertRaises(ValueError): self.ask()
        self.assertEqual([{k: v for k, v in item.items() if k != 'review_evidence'} for item in history],
                         self.questions.answers(self.job['id']))
        self.assertEqual(history[0], self.questions.get(history[0]['id']))

    def test_cancel_preserves_question_and_cannot_resume(self):
        q = self.ask()
        self.assertEqual('cancelled', self.questions.cancel(self.job['id'])['status'])
        saved = self.questions.get(q['id'])
        self.assertEqual('cancelled', saved['status'])
        self.assertEqual(q['question'], saved['question'])
        with self.assertRaises(ValueError): self.answer(q)
        self.assertEqual([], self.questions.answers(self.job['id']))

    def test_invalid_question_and_answer_bounds_leave_state_unchanged(self):
        for question in ({'text': '', 'reason': 'x'}, {'text': 'x' * 2001, 'reason': 'x'},
                         {'text': 'x', 'reason': 'x' * 2001}, {'text': 'x', 'reason': 'x', 'command': 'x'}):
            with self.assertRaises(ValueError):
                self.questions.ask(self.job['id'], question, 'a' * 64, 'project', 'p', 'gpt-5.6-sol')
        q = self.ask()
        for answer in (' ', 'x' * 4001, None, {'text': 'x'}):
            with self.assertRaises(ValueError):
                self.questions.answer(q['id'], answer, 'a' * 64, 'a' * 64)
        self.assertEqual('pending', self.questions.get(q['id'])['status'])

    def test_listing_filters_and_missing_records(self):
        q = self.ask()
        self.assertEqual([q], self.questions.list(status='pending', job_id=self.job['id']))
        self.assertEqual([], self.questions.list(status='answered'))
        with self.assertRaises(ValueError): self.questions.get('missing')
        with self.assertRaises(ValueError): self.questions.cancel('missing')

    def test_concurrent_double_submission_records_exactly_one_answer(self):
        q = self.ask()
        barrier = threading.Barrier(2)
        outcomes = []

        def submit():
            barrier.wait()
            try:
                self.answer(q)
                outcomes.append('accepted')
            except ValueError:
                outcomes.append('rejected')

        threads = [threading.Thread(target=submit) for _ in range(2)]
        for thread in threads: thread.start()
        for thread in threads: thread.join(timeout=5)
        self.assertTrue(all(not thread.is_alive() for thread in threads))
        self.assertCountEqual(['accepted', 'rejected'], outcomes)
        self.assertEqual(1, len(self.questions.answers(self.job['id'])))

    def test_invalid_identifiers_rejected_before_sqlite_binding(self):
        for value in ([], {}, None, 3, 'bad', 'a' * 33):
            for call in (lambda: self.questions.get(value), lambda: self.questions.cancel(value),
                         lambda: self.questions.answer(value, 'x', 'a' * 64, 'a' * 64),
                         lambda: self.questions.answers(value)):
                with self.assertRaises(ValueError): call()

    def test_invalid_scope_metadata_is_rejected(self):
        for scope_hash, kind, supervisor in [('bad', 'project', 'gpt-5.6-sol'),
                                             ('a' * 64, 'other', 'gpt-5.6-sol'),
                                             ('a' * 64, 'project', 'other')]:
            with self.assertRaises(ValueError):
                self.questions.ask(self.job['id'], {'text': 'x', 'reason': 'y'},
                                   scope_hash, kind, 'p', supervisor)

    def test_review_evidence_preserved_but_excluded_from_answer_context(self):
        q = self.ask(result={'review': {'verdict': 'ASK_USER'}, 'operator_question': {'ignore': True}})
        self.assertEqual({'review': {'verdict': 'ASK_USER'}}, q['review_evidence'])
        self.answer(q)
        self.assertEqual(q['review_evidence'], self.questions.get(q['id'])['review_evidence'])
        self.assertNotIn('review_evidence', self.questions.answers(self.job['id'])[0])

    def test_review_evidence_bound_is_atomic(self):
        with self.assertRaises(ValueError): self.ask(result={'review': 'x' * 160001})
        self.assertEqual('running', self.store.job(self.job['id'])['status'])
        self.assertEqual([], self.questions.list())

    def test_resolved_history_database_update_and_delete_are_rejected(self):
        q = self.ask()
        self.answer(q)
        for statement in ('DELETE FROM operator_questions WHERE id=?',
                          "UPDATE operator_questions SET body='{}' WHERE id=?"):
            with self.assertRaises(sqlite3.IntegrityError):
                with self.store.db() as c: c.execute(statement, (q['id'],))


if __name__ == '__main__': unittest.main()
