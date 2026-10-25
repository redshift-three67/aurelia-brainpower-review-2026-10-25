import copy
import json
import threading
import unittest

from governor_workbench.llm import ModelError, ModelCancelled


class FakeClient:
    def __init__(self, proposal, review=None):
        self.proposal = proposal
        self.review = review or dict(summary='Independent assessment', decision='REVIEW_ONLY', findings=[], required_evidence=[])
        self.calls = []

    def call(self, model, prompt, **kwargs):
        self.calls.append(dict(model=model, prompt=prompt, **kwargs))
        body = self.proposal if len(self.calls) == 1 else self.review
        return dict(text=json.dumps(body), success=True, model=model, requested_model=model)


class PlanningLLMTests(unittest.TestCase):
    def setUp(self):
        self.context = dict(plan_ready=True, review_scope=dict(kind='project', id='one'),
                            scope_hash='a'*64, registry_projects=[dict(id='one')],
                            evidence_marker='untrusted raw evidence')
        self.proposal = dict(summary='Read the bounded evidence', steps=[dict(
            id='first', title='Read contract', project_id='one', priority=10, depends_on=[],
            rationale='Understand current guarantees', scope=['README.md'],
            tests=['Confirm each assertion has current evidence'], action='review')])

    def run_plan(self, client, **kwargs):
        from governor_workbench.planning_llm import propose_plan
        return propose_plan(self.context, kwargs.pop('supervisor','gpt-5.6-sol'), client, **kwargs)

    def test_function_exists(self):
        import importlib.util
        self.assertIsNotNone(importlib.util.find_spec('governor_workbench.planning_llm'))

    def test_selected_supervisor_receives_exact_proposal_and_raw_context(self):
        prompts = []
        for supervisor in ('gpt-5.6-sol','gpt-6-astra'):
            client = FakeClient(self.proposal)
            result = self.run_plan(client, supervisor=supervisor)
            self.assertEqual([c['model'] for c in client.calls], ['gpt-5.6-terra',supervisor])
            self.assertFalse(result['approval_granted'])
            self.assertEqual(result['proposal'], self.proposal)
            self.assertIn(json.dumps(self.proposal,ensure_ascii=False,sort_keys=True), client.calls[1]['prompt'])
            for call in client.calls:
                self.assertIn('untrusted raw evidence', call['prompt'])
                self.assertIn('untrusted source', call['prompt'])
            prompts.append(client.calls[0]['prompt'])
        self.assertEqual(prompts[0],prompts[1])

    def test_incomplete_context_calls_no_models(self):
        self.context['plan_ready'] = False
        client = FakeClient(self.proposal)
        with self.assertRaises(ModelError): self.run_plan(client)
        self.assertEqual(client.calls, [])

    def test_malformed_foreign_and_cyclic_proposals_never_call_supervisor(self):
        malformed = copy.deepcopy(self.proposal)
        malformed['steps'][0]['command'] = 'unwanted command field'
        foreign = copy.deepcopy(self.proposal)
        foreign['steps'][0]['project_id'] = 'foreign'
        cycle = copy.deepcopy(self.proposal)
        cycle['steps'][0]['depends_on'] = ['first']
        for proposal in ({}, malformed, foreign, cycle):
            client = FakeClient(proposal)
            with self.subTest(proposal=proposal), self.assertRaises(ModelError): self.run_plan(client)
            self.assertEqual(len(client.calls), 1)

    def test_cancelled_before_start_has_zero_calls(self):
        cancel = threading.Event()
        cancel.set()
        client = FakeClient(self.proposal)
        with self.assertRaises(ModelCancelled): self.run_plan(client,cancel_event=cancel)
        self.assertEqual(client.calls, [])

    def test_unsupported_supervisor_and_oversized_context_have_zero_calls(self):
        client = FakeClient(self.proposal)
        with self.assertRaises(ModelError): self.run_plan(client,supervisor='other')
        self.context['big'] = 'x'*95000
        with self.assertRaises(ModelError): self.run_plan(client)
        self.assertEqual(client.calls, [])

    def test_supervisor_cannot_grant_permission_or_return_extra_fields(self):
        for review in (dict(summary='Approve',decision='ALLOW',findings=[],required_evidence=[]),
                       dict(summary='Approve',decision='REVIEW_ONLY',findings=[],required_evidence=[],approval_granted=True)):
            client = FakeClient(self.proposal,review)
            with self.assertRaises(ModelError): self.run_plan(client)

    def test_cancellation_after_terra_does_not_call_supervisor(self):
        cancel = threading.Event()
        client = FakeClient(self.proposal)
        original_call = client.call
        def call(*args, **kwargs):
            result = original_call(*args, **kwargs)
            cancel.set()
            return result
        client.call = call
        with self.assertRaises(ModelCancelled): self.run_plan(client,cancel_event=cancel)
        self.assertEqual(len(client.calls),1)

    def test_code_fence_and_failed_terra_never_call_supervisor(self):
        proposal = copy.deepcopy(self.proposal)
        proposal['steps'][0]['tests'] = ['```code```']
        client = FakeClient(proposal)
        with self.assertRaises(ModelError): self.run_plan(client)
        self.assertEqual(len(client.calls),1)
        client = FakeClient(self.proposal)
        original_call = client.call
        def failed(*args,**kwargs):
            return {**original_call(*args,**kwargs),'success':False}
        client.call = failed
        with self.assertRaises(ModelError): self.run_plan(client)
        self.assertEqual(len(client.calls),1)

    def test_combined_supervisor_prompt_budget_is_checked_before_call(self):
        self.context['additional_evidence'] = 'x'*80000
        proposal = copy.deepcopy(self.proposal)
        proposal['steps'] = [{**proposal['steps'][0], 'id':f's{i}', 'rationale':'x'*3000} for i in range(20)]
        client = FakeClient(proposal)
        with self.assertRaises(ModelError): self.run_plan(client)
        self.assertEqual(len(client.calls),1)


if __name__ == '__main__': unittest.main()
