import copy
import hashlib
import json
import unittest

from governor_workbench.llm import ModelError


class FakeClient:
    def __init__(self,review=None):
        self.calls=[]
        self.review=review or dict(summary='Independent review',decision='REVIEW_ONLY',findings=[],required_evidence=[])

    def call(self,model,prompt,**kwargs):
        self.calls.append(dict(model=model,prompt=prompt))
        return dict(model=model,success=True,text=json.dumps(self.review))


class PostTestReviewTests(unittest.TestCase):
    def setUp(self):
        self.context=dict(plan_ready=True,review_scope=dict(kind='project',id='one'),scope_hash='a'*64,
            registry_projects=[dict(id='one',path='C:/synthetic/project',model_egress=True)],vault_sources=[],
            source_marker='exact raw context')
        self.manifest=dict(version=1,id='b'*32,original_root='C:/synthetic/project',root_identity=dict(device=1,inode=2),
            execution_enabled=False,apply_back_enabled=False,files=[dict(path='app.py',original_sha256='c'*64,
            staged_sha256=hashlib.sha256(b'new\n').hexdigest(),staged_bytes=4,diff='--- a/app.py\n+++ b/app.py\n-old\n+new\n')])
        self.sources=[dict(path='app.py',content='new\n',sha256=hashlib.sha256(b'new\n').hexdigest())]
        self.result=dict(success=True,exit_code=0,count=3,errors=0,failures=0,skipped=0,sources_verified=True,completion_verified=True,output='Ran 3 tests; exact observed output')

    def review(self,client,supervisor='gpt-5.6-sol'):
        from governor_workbench.post_test_review import review_staged
        return review_staged(self.context,self.manifest,self.result,supervisor,client,staged_sources=self.sources)

    def test_module_exists(self):
        import importlib.util
        self.assertIsNotNone(importlib.util.find_spec('governor_workbench.post_test_review'))

    def test_valid_selected_supervisor_receives_actual_evidence(self):
        for model in ('gpt-5.6-sol','gpt-6-astra'):
            client=FakeClient()
            report=self.review(client,model)
            self.assertTrue(report['verified'])
            self.assertFalse(report['approval_granted'])
            self.assertEqual([c['model'] for c in client.calls],[model])
            prompt=client.calls[0]['prompt']
            for text in ('exact raw context','-old','+new','c'*64,self.sources[0]['sha256'],'exact observed output','untrusted source'):
                self.assertIn(text,prompt)

    def test_unchanged_test_assertions_are_included_in_full(self):
        content='def test_result(self): self.assertEqual(calculate(3), 42)\n'
        digest=hashlib.sha256(content.encode('utf-8')).hexdigest()
        self.manifest['files'].append(dict(path='tests/test_calc.py',original_sha256=digest,
            staged_sha256=digest,staged_bytes=len(content.encode('utf-8')),diff=''))
        self.sources.append(dict(path='tests/test_calc.py',content=content,sha256=digest))
        client=FakeClient()
        self.assertTrue(self.review(client)['verified'])
        prompt=client.calls[0]['prompt']
        self.assertIn('self.assertEqual(calculate(3), 42)',prompt)
        self.assertIn('THIS isolated staged verification',prompt)

    def test_missing_tampered_duplicate_and_oversized_sources_never_call_model(self):
        original=copy.deepcopy(self.sources)
        for sources in (None,[],original+original,[{**original[0],'content':'tampered'}],
                [{**original[0],'sha256':'a'*64}],[{**original[0],'content':'x'*(256*1024+1)}]):
            self.sources=sources
            client=FakeClient()
            with self.assertRaises(ModelError): self.review(client)
            self.assertEqual(client.calls,[])

    def test_failed_tests_cannot_be_upgraded_by_model(self):
        self.result.update(success=False,exit_code=1,failures=1)
        client=FakeClient()
        self.assertFalse(self.review(client)['verified'])
        self.assertEqual(len(client.calls),1)

    def test_all_skipped_or_invalid_skip_counts_never_verify(self):
        for skipped in (3,4,-1,None,False):
            self.result['skipped']=skipped
            self.assertFalse(self.review(FakeClient())['verified'])

    def test_missing_runner_completion_cannot_be_upgraded_by_model(self):
        self.result['completion_verified']=False
        self.assertFalse(self.review(FakeClient())['verified'])
        del self.result['completion_verified']
        self.assertFalse(self.review(FakeClient())['verified'])

    def test_missing_proof_and_zero_tests_never_verify(self):
        original=copy.deepcopy(self.result)
        for field,value in (('sources_verified',False),('count',0),('errors',1),('success',None),('exit_code',False)):
            self.result={**original,field:value}
            self.assertFalse(self.review(FakeClient())['verified'])
        self.result={k:v for k,v in original.items() if k!='count'}
        self.assertFalse(self.review(FakeClient())['verified'])

    def test_supervisor_findings_or_missing_evidence_prevent_verification(self):
        for review in (dict(summary='Blocked',decision='BLOCK',findings=[],required_evidence=[]),
            dict(summary='Concern',decision='REVIEW_ONLY',findings=['Missing assertion'],required_evidence=[]),
            dict(summary='Evidence',decision='REVIEW_ONLY',findings=[],required_evidence=['Independent fixture'])):
            self.assertFalse(self.review(FakeClient(review))['verified'])

    def test_denied_egress_or_unready_context_calls_no_model(self):
        for mutation in ('project','vault','readiness'):
            context=copy.deepcopy(self.context)
            if mutation=='project': self.context['registry_projects'][0]['model_egress']=False
            elif mutation=='vault': self.context['vault_sources']=[dict(model_egress=False)]
            else: self.context['plan_ready']=False
            client=FakeClient()
            with self.assertRaises(ModelError): self.review(client)
            self.assertEqual(client.calls,[])
            self.context=context

    def test_oversized_prompt_calls_no_model(self):
        self.manifest['files'][0]['diff']='x'*120000
        client=FakeClient()
        with self.assertRaises(ModelError): self.review(client)
        self.assertEqual(client.calls,[])

    def test_output_is_bounded_and_explicitly_truncated(self):
        self.result['output']='x'*100000
        client=FakeClient()
        self.review(client)
        self.assertLess(len(client.calls[0]['prompt']),120000)
        self.assertIn('"output_truncated": true',client.calls[0]['prompt'])

    def test_supervisor_cannot_add_permission_field(self):
        review=dict(summary='Not permission',decision='REVIEW_ONLY',findings=[],required_evidence=[],approval_granted=True)
        with self.assertRaises(ModelError): self.review(FakeClient(review))


if __name__=='__main__': unittest.main()
