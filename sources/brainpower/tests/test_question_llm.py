import hashlib
import json
import unittest

from governor_workbench.llm import ModelError
from governor_workbench.planning_llm import propose_plan
from governor_workbench.patch_llm import propose_patch
from governor_workbench.question_llm import assess_answer


class Client:
    def __init__(self, *values):
        self.values = list(values)
        self.calls = []

    def call(self, model, prompt, **kwargs):
        self.calls.append((model, prompt))
        value = self.values.pop(0)
        return dict(success=True, model=model, requested_model=model,
                    text=value if isinstance(value, str) else json.dumps(value))


class QuestionLLMTests(unittest.TestCase):
    def setUp(self):
        self.context = dict(plan_ready=True, review_scope=dict(kind='project', id='one'),
                            scope_hash='a'*64, registry_projects=[dict(id='one', model_egress=True)],
                            operator_answers=[{'answer': 'previous clarification marker'}],
                            current_request={'phase': 'patch preflight marker'})
        self.question = dict(text='Which existing fixture is authoritative?', reason='Two fixture names disagree.')
        self.review = dict(summary='Relevant bounded clarification', decision='REVIEW_ONLY',
                           findings=[], required_evidence=[])
        self.record = dict(question=self.question, answer='The documented fixture.')
        self.step = dict(id='fix', project_id='one', action='change', scope=['main.py'])
        self.sources = [dict(path='main.py', content='raw full source marker',
                             sha256=hashlib.sha256(b'raw full source marker').hexdigest())]

    def propose(self, client, patch=False):
        if patch:
            return propose_patch(self.context, self.step, self.sources, 'gpt-5.6-sol', client)
        return propose_plan(self.context, 'gpt-5.6-sol', client)

    def test_question_requires_independent_clean_review_for_both_actions(self):
        for patch in (False, True):
            client = Client({'question': self.question}, self.review)
            result = self.propose(client, patch)
            self.assertEqual(result['operator_question'], self.question)
            self.assertFalse(result['approval_granted'])
            self.assertNotIn('proposal', result)
            self.assertNotIn('patch', result)
            self.assertEqual([c[0] for c in client.calls], ['gpt-5.6-terra', 'gpt-5.6-sol'])
            for _, prompt in client.calls:
                self.assertIn('previous clarification marker', prompt)
                self.assertIn('patch preflight marker', prompt)
                if patch:
                    self.assertIn('raw full source marker', prompt)
                    self.assertIn(self.sources[0]['sha256'], prompt)

    def test_blocked_and_nonempty_reviews_preserved_without_waiting_question(self):
        for changes in ({'decision': 'BLOCK'}, {'findings': ['irrelevant']},
                        {'required_evidence': ['scope unclear']}):
            review = {**self.review, **changes}
            result = self.propose(Client({'question': self.question}, review))
            self.assertTrue(result['question_blocked'])
            self.assertEqual(result['review'], review)
            self.assertNotIn('operator_question', result)

    def test_malformed_questions_never_call_supervisor(self):
        for value in ({'question': {**self.question, 'permission': True}},
                      {'question': {**self.question, 'text': 'x'*2001}},
                      {'question': {**self.question, 'reason': ''}},
                      {'question': self.question, 'summary': 'mixed'},
                      '{"question":{"text":"first","text":"second","reason":"x"}}'):
            for patch in (False, True):
                client = Client(value)
                with self.assertRaises(ModelError):
                    self.propose(client, patch)
                self.assertEqual(len(client.calls), 1)

    def test_duplicate_review_fields_cannot_erase_findings(self):
        client = Client({'question': self.question},
                        '{"summary":"ok","decision":"REVIEW_ONLY","findings":["block"],'
                        '"findings":[],"required_evidence":[]}')
        with self.assertRaises(ModelError):
            self.propose(client)

    def test_duplicate_final_review_fields_block_plan_and_patch(self):
        plan = {'summary': 'Bounded plan', 'steps': [dict(id='step', title='Read', project_id='one',
            priority=1, depends_on=[], rationale='Review target', scope=['main.py'], tests=['Check target'], action='review')]}
        replacement = {'summary': 'Bounded patch', 'files': [{'path': 'main.py', 'content': 'changed'}]}
        for patch_mode, proposal in ((False, plan), (True, replacement)):
            client = Client(proposal, '{"summary":"x","decision":"BLOCK","decision":"REVIEW_ONLY",'
                            '"findings":["unsafe"],"findings":[],"required_evidence":[]}')
            with self.assertRaises(ModelError): self.propose(client, patch_mode)

    def test_answers_require_two_true_assessments_with_independent_same_sources(self):
        for terra, supervisor in ((True, True), (True, False), (False, True), (False, False)):
            client = Client(dict(within_scope=terra, reason='Terra reason'),
                            dict(within_scope=supervisor, reason='Supervisor reason'))
            result = assess_answer(self.context, self.record, 'gpt-6-astra', client,
                                   step=self.step, sources=self.sources)
            self.assertEqual(result['within_scope'], terra and supervisor)
            self.assertFalse(result['approval_granted'])
            for _, prompt in client.calls:
                self.assertIn('raw full source marker', prompt)
                self.assertIn(self.question['text'], prompt)
                self.assertIn(self.record['answer'], prompt)
                self.assertIn('patch preflight marker', prompt)
                self.assertIn('test criteria', prompt)
            self.assertIn('TERRA_ASSESSMENT', client.calls[1][1])

    def test_bad_assessment_never_silently_overwrites_or_coerces(self):
        for value in ({'within_scope': 'true', 'reason': 'wrong type'},
                      {'within_scope': True, 'reason': 'x', 'permission': True},
                      {'within_scope': True, 'reason': ''},
                      '{"within_scope":false,"within_scope":true,"reason":"x"}'):
            client = Client(value)
            with self.assertRaises(ModelError):
                assess_answer(self.context, self.record, 'gpt-5.6-sol', client)
            self.assertEqual(len(client.calls), 1)

    def test_incomplete_context_and_missing_patch_sources_call_no_models(self):
        client = Client()
        with self.assertRaises(ModelError):
            assess_answer({**self.context, 'plan_ready': False}, self.record, 'gpt-5.6-sol', client)
        with self.assertRaises(ModelError):
            assess_answer(self.context, self.record, 'gpt-5.6-sol', client, step=self.step)
        self.assertEqual(client.calls, [])
