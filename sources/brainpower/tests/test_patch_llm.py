import copy
import hashlib
import json
import threading
import unittest

from governor_workbench.llm import ModelError, ModelCancelled


class FakePatchClient:
    def __init__(self, patch, review=None):
        self.patch = patch
        self.review = review or {'summary':'Independent review', 'decision':'REVIEW_ONLY',
                                 'findings':[], 'required_evidence':[]}
        self.calls = []

    def call(self, model, prompt, **kwargs):
        self.calls.append((model, prompt))
        value = self.patch if len(self.calls) == 1 else self.review
        return {'success':True, 'model':model, 'requested_model':model,
                'text':value if isinstance(value,str) else json.dumps(value)}


class PatchLLMTests(unittest.TestCase):
    def setUp(self):
        self.context = {'plan_ready':True, 'review_scope':{'kind':'project','id':'one'},
                        'scope_hash':'a'*64, 'registry_projects':[{'id':'one','model_egress':True}]}
        self.step = {'id':'edit', 'title':'Fix fixture', 'project_id':'one', 'priority':1,
                     'depends_on':[], 'rationale':'Requested fix', 'scope':['src/main.py'],
                     'tests':['Check fixture'], 'action':'change'}
        self.sources = [{'path':'src/main.py','content':'before\n',
                         'sha256':hashlib.sha256(b'before\n').hexdigest()}]
        self.patch = {'summary':'Fixture change','files':[{'path':'src/main.py','content':'after\n'}]}

    def propose(self, client, **kwargs):
        from governor_workbench.patch_llm import propose_patch
        return propose_patch(self.context,self.step,self.sources,
                             kwargs.pop('supervisor','gpt-5.6-sol'),client,**kwargs)

    def test_supervisors_receive_exact_sources_patch_and_diff(self):
        for model in ('gpt-5.6-sol','gpt-6-astra'):
            client = FakePatchClient(self.patch)
            result = self.propose(client,supervisor=model)
            self.assertEqual([call[0] for call in client.calls],['gpt-5.6-terra',model])
            self.assertEqual(result['patch'],self.patch)
            self.assertFalse(result['approval_granted'])
            self.assertIn(self.sources[0]['sha256'],client.calls[1][1])
            self.assertIn('-before',client.calls[1][1])
            self.assertIn('+after',client.calls[1][1])
            self.assertIn(json.dumps(self.patch,ensure_ascii=False,sort_keys=True),client.calls[1][1])

    def test_unready_unauthorized_foreign_step_and_nonchange_call_no_models(self):
        for mutate in (lambda: self.context.update(plan_ready=False),
                       lambda: self.context['registry_projects'][0].update(model_egress=False),
                       lambda: self.step.update(project_id='foreign'),
                       lambda: self.step.update(action='review')):
            self.setUp(); mutate(); client=FakePatchClient(self.patch)
            with self.assertRaises(ModelError): self.propose(client)
            self.assertEqual(client.calls,[])

    def test_invalid_patch_does_not_call_supervisor(self):
        for patch in ('not json', {'summary':'Bad','files':[{'path':'foreign.py','content':'new'}]},
                      {'summary':'Bad','files':[{'path':'src/main.py','content':None}]},
                      {'summary':'No change','files':[{'path':'src/main.py','content':'before\n'}]},
                      {**self.patch,'command':'execute'}, {'summary':'Empty','files':[]}):
            client=FakePatchClient(patch)
            with self.subTest(patch=patch),self.assertRaises(ModelError): self.propose(client)
            self.assertEqual(len(client.calls),1)

    def test_incomplete_duplicate_or_mismatched_sources_fail_before_models(self):
        for sources in ([], self.sources*2, [{'path':'foreign.py','content':None,'sha256':None}],
                        [{**self.sources[0],'sha256':'b'*64}],
                        [{'path':'src/main.py','content':None,'sha256':'b'*64}]):
            self.sources=sources; client=FakePatchClient(self.patch)
            with self.subTest(sources=sources),self.assertRaises(ModelError): self.propose(client)
            self.assertEqual(client.calls,[])

    def test_absent_source_permits_new_file_but_no_deletion(self):
        self.sources=[{'path':'src/main.py','content':None,'sha256':None}]
        result=self.propose(FakePatchClient(self.patch))
        self.assertEqual(result['patch'],self.patch)

    def test_source_and_response_size_limits(self):
        self.sources[0]['content']='x'*95001
        self.sources[0]['sha256']=hashlib.sha256(self.sources[0]['content'].encode()).hexdigest()
        client=FakePatchClient(self.patch)
        with self.assertRaises(ModelError): self.propose(client)
        self.assertEqual(client.calls,[])
        self.setUp()
        self.patch['files'][0]['content']='x'*(256*1024+1)
        client=FakePatchClient(self.patch)
        with self.assertRaises(ModelError): self.propose(client)
        self.assertEqual(len(client.calls),1)

    def test_cancelled_request_has_zero_calls_and_supervisor_cannot_approve(self):
        cancel=threading.Event(); cancel.set(); client=FakePatchClient(self.patch)
        with self.assertRaises(ModelCancelled): self.propose(client,cancel_event=cancel)
        self.assertEqual(client.calls,[])
        review={'summary':'Approve','decision':'ALLOW','findings':[],'required_evidence':[]}
        with self.assertRaises(ModelError): self.propose(FakePatchClient(self.patch,review))

    def test_windows_aliases_duplicates_and_excess_files_are_rejected(self):
        self.step['scope']=['src/main.py','SRC/main.py']
        self.sources.append({'path':'SRC/main.py','content':None,'sha256':None})
        client=FakePatchClient(self.patch)
        with self.assertRaises(ModelError): self.propose(client)
        self.assertEqual(client.calls,[])
        self.setUp()
        self.patch['files']*=2
        client=FakePatchClient(self.patch)
        with self.assertRaises(ModelError): self.propose(client)
        self.assertEqual(len(client.calls),1)
        self.setUp()
        self.step['scope']=['f'+str(i)+'.py' for i in range(21)]
        self.sources=[{'path':p,'content':None,'sha256':None} for p in self.step['scope']]
        client=FakePatchClient(self.patch)
        with self.assertRaises(ModelError): self.propose(client)
        self.assertEqual(client.calls,[])

    def test_blocked_supervisor_report_is_retained_without_permission(self):
        review={'summary':'Unsafe proposal','decision':'BLOCK','findings':['Boundary concern'],
                'required_evidence':['Tests required']}
        result=self.propose(FakePatchClient(self.patch,review))
        self.assertEqual(result['review'],review)
        self.assertFalse(result['approval_granted'])
