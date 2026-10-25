"""Protected route-B admission and exact per-call routing with real job receipts."""
import json
import threading
import unittest
from unittest.mock import patch

from tests import test_server


class RouteBHttpTests(unittest.TestCase):
    setUp=test_server.ServerTests.setUp
    cleanup=test_server.ServerTests.cleanup
    auth=test_server.ServerTests.auth
    wait_terminal=test_server.ServerTests.wait_terminal

    def stable_scope(self):
        # Git subprocess timing is tested elsewhere; keep this fixture's source bytes and HEAD stable.
        from pathlib import Path
        from governor_workbench.evidence import Observer, digest, fingerprint, now
        self.server.app.store.set_setting('monitor_enabled',False)
        note=Path(self.tmp.name)/'repo'/'project_memories'/'note.md'
        git=dict(head='f'*40,branch='test',git_status='',git_observed_at=now(),
                 committed={'project_memories/note.md'},staged=set(),
                 committed_hashes={'project_memories/note.md':digest(note.read_bytes())},
                 staged_hashes={},incomplete=False,error='',tracked_diff_hash=fingerprint([]))
        patcher=patch.object(Observer,'git_state',return_value=git)
        patcher.start(); self.addCleanup(patcher.stop)
        first=self.server.app.scope_context('project','test')
        second=self.server.app.scope_context('project','test')
        self.assertTrue(first['evidence_complete'])
        self.assertEqual(first['scope_hash'],second['scope_hash'])
        return second

    def request(self,method,path,data=None,headers=None):
        # Windows fixture Git observation can exceed the UI deadline; this test targets routing and receipts.
        return test_server.ServerTests.request(self,method,path,data,headers,timeout=90)

    def test_explicit_scope_permission_and_astra_receipts(self):
        app=self.server.app
        from pathlib import Path
        marker='MIDDLE_GATE_ROUTE_B_HTTP'
        note=Path(self.tmp.name)/'repo'/'project_memories'/'note.md'
        note.write_text('\n'.join(['start']+['ordinary']*40+[marker]+['ordinary']*40+['end']),encoding='utf-8')
        body=dict(action='scope_route_b_review',scope_kind='project',scope_id='test',critical_review=True)
        self.assertEqual(403,self.request('POST','/api/actions',body)[0])
        self.assertEqual(400,self.request('POST','/api/actions',body,self.auth())[0])
        self.assertEqual(400,self.request('POST','/api/actions',dict(body,critical_review='yes'),self.auth())[0])
        status,_,_=self.request('POST','/api/registry/policy',
                                dict(project_id='test',requirements='Review fixture',model_egress=True),self.auth())
        self.assertEqual(201,status)
        self.stable_scope()
        safe=dict(critical_decision=False,material_contradiction=False,reason='Synthetic classification')
        review=dict(summary='Read evidence',decision='REVIEW_ONLY',findings=[],required_evidence=[])
        outputs=[dict(plan=dict(summary='Read',steps=['Inspect current evidence'],blockers=[]),risk=safe),
                 dict(review=review,risk=safe),dict(review=review,risk=safe)]
        calls=[]
        def transport(client,model,prompt,**kwargs):
            calls.append((model,kwargs['reasoning'],prompt))
            return dict(text=json.dumps(outputs[len(calls)-1]),success=True,model=model,
                        requested_model=model,actual_model=model,usage=dict(input_tokens=10,output_tokens=2,total_tokens=12))
        with patch('governor_workbench.jobs.RouterClient.call',new=transport):
            status,response,_=self.request('POST','/api/actions',body,self.auth())
            self.assertEqual(202,status,response)
            job=self.wait_terminal(lambda:app.store.job(response['job']['id']),('queued','running'))
        self.assertEqual('completed',job['status'],job.get('error'))
        self.assertEqual([('gpt-6-sol','high'),('gpt-6-luna','max'),('gpt-6-astra','medium')],
                         [(m,e) for m,e,_ in calls])
        self.assertEqual('b_v1',job['result']['route_variant'])
        self.assertEqual('full',job['result']['memory_coverage']['status'])
        self.assertEqual(1,len(job['result']['memory_coverage']['files']))
        self.assertEqual(64,len(job['result']['model_context_hash']))
        self.assertTrue(all(marker in prompt for _,_,prompt in calls))
        self.assertFalse(job['result']['approval_granted'])
        self.assertFalse(job['result']['product_files_changed'])
        self.assertEqual(['orchestrator','worker_review','critical_independent_review'],
                         [item['routing']['role'] for item in job['token_usage']['calls']])
        self.assertFalse(app.settings()['auto_review'])

    def test_legacy_review_receives_complete_memory_on_real_job_path(self):
        from pathlib import Path
        app=self.server.app
        app.registry.set_project_policy('test',requirements='Review fixture',model_egress=True)
        marker='MIDDLE_GATE_LEGACY_HTTP'
        note=Path(self.tmp.name)/'repo'/'project_memories'/'note.md'
        note.write_text('\n'.join(['start']+['ordinary']*40+[marker]+['ordinary']*40+['end']),encoding='utf-8')
        self.stable_scope()
        calls=[]
        def terra(adapter,prompt,model='gpt-5.6-terra',**kwargs):
            calls.append((model,prompt))
            return dict(text=json.dumps(dict(summary='Read',steps=['Inspect'],blockers=[])),
                        success=True,model=model,actual_model=model,usage={})
        def supervisor(client,model,prompt,**kwargs):
            calls.append((model,prompt))
            return dict(text=json.dumps(dict(summary='Checked',decision='REVIEW_ONLY',
                                             findings=[],required_evidence=[])),
                        success=True,model=model,actual_model=model,usage={})
        with patch('governor_workbench.jobs.HermesAdapter.review',new=terra),\
             patch('governor_workbench.jobs.RouterClient.call',new=supervisor):
            status,response,_=self.request('POST','/api/actions',dict(action='scope_review',
                scope_kind='project',scope_id='test'),self.auth())
            self.assertEqual(202,status,response)
            job=self.wait_terminal(lambda:app.store.job(response['job']['id']),('queued','running'))
        self.assertEqual('completed',job['status'],job.get('error'))
        self.assertEqual(2,len(calls))
        self.assertTrue(all(marker in prompt for _,prompt in calls))
        self.assertEqual('full',job['result']['memory_coverage']['status'])
        self.assertEqual(64,len(job['result']['model_context_hash']))

    def test_oversized_memory_stages_through_both_review_job_routes(self):
        from pathlib import Path
        app=self.server.app
        app.registry.set_project_policy('test',requirements='Review fixture',model_egress=True)
        marker='MIDDLE_GATE_REQUIRES_OPERATOR_REVIEW'
        note=Path(self.tmp.name)/'repo'/'project_memories'/'note.md'
        note.write_text('ordinary evidence\n'*3000+marker+'\n'+'ordinary evidence\n'*3000,encoding='utf-8')
        self.stable_scope()
        safe=dict(critical_decision=False,material_contradiction=False,reason='Synthetic only')
        review=dict(summary='Checked',decision='REVIEW_ONLY',findings=[],required_evidence=[])
        for action in ('scope_review','scope_route_b_review'):
            calls=[]
            def response(model,prompt):
                calls.append((model,prompt))
                if 'SOURCE:\n' in prompt:
                    quote=marker if marker in prompt else 'ordinary evidence'
                    body=dict(summary='Current gate remains open',quotes=[quote],open_questions=[])
                elif model=='gpt-5.6-terra':
                    body=dict(summary='Inspect',steps=['Check gate'],blockers=[])
                elif model=='gpt-6-sol':
                    body=dict(plan=dict(summary='Inspect',steps=['Check gate'],blockers=[]),risk=safe)
                elif model=='gpt-6-luna':
                    body=dict(review=review,risk=safe)
                else:
                    body=review
                return dict(text=json.dumps(body),success=True,model=model,actual_model=model,
                            usage=dict(input_tokens=10,output_tokens=2,total_tokens=12))
            def terra(adapter,prompt,model='gpt-5.6-terra',**kwargs):
                return response(model,prompt)
            def router(client,model,prompt,**kwargs):
                return response(model,prompt)
            with patch('governor_workbench.jobs.HermesAdapter.review',new=terra),\
                 patch('governor_workbench.jobs.RouterClient.call',new=router):
                status,value,_=self.request('POST','/api/actions',dict(action=action,
                    scope_kind='project',scope_id='test'),self.auth())
                self.assertEqual(202,status,value)
                job=self.wait_terminal(lambda:app.store.job(value['job']['id']),('queued','running'))
            self.assertEqual('completed',job['status'],job.get('error'))
            self.assertEqual('staged',job['result']['memory_coverage']['status'])
            from governor_workbench.model_memory import stage_coverage_complete
            self.assertTrue(stage_coverage_complete(job['result']['memory_coverage']))
            self.assertTrue(any(marker in prompt for _,prompt in calls if 'SOURCE:\n' in prompt))
            self.assertTrue(any(marker in prompt for _,prompt in calls if 'SOURCE:\n' not in prompt))
            self.assertFalse(job['result']['approval_granted'])

    def test_changed_bound_settings_block_before_first_call(self):
        app=self.server.app
        app.registry.set_project_policy('test',requirements='Fixture',model_egress=True)
        self.stable_scope()
        with patch.object(app.runner.pending,'put'):
            job=app.runner.submit('scope_route_b_review',scope_kind='project',scope_id='test')
        app.update_settings({'reasoning_mode':'high'})
        sent=[]
        with patch('governor_workbench.jobs.RouterClient.call',side_effect=lambda *a,**k:sent.append(1)):
            from governor_workbench.llm import ModelError
            with self.assertRaises(ModelError):
                app.runner.execute(job,app.settings()['supervisor'],threading.Event())
        self.assertEqual([],sent)
        self.assertFalse(app.store.job(job['id'])['token_usage']['recorded'])
        app.store.update_job(job['id'],status='cancelled')

    def test_route_b_plan_can_be_selected_without_execution_permission(self):
        app=self.server.app
        app.store.set_setting('monitor_enabled',False)
        app.registry.set_project_policy('test',requirements='Review fixture',model_egress=True)
        context=self.stable_scope()
        fields=dict(requirements='Review fixture',test_strategy='Inspect fixture',
                    dependencies='None',open_evidence='No runtime claims')
        status,_,_=self.request('POST','/api/intake',dict(scope_kind='project',scope_id='test',
                                scope_hash=context['scope_hash'],project_id='test',fields=fields),self.auth())
        self.assertEqual(201,status)
        proposal=dict(summary='Review fixture',steps=[dict(id='read_note',title='Read note',project_id='test',
            priority=1,depends_on=[],rationale='Establish source',scope=['project_memories/note.md'],
            tests=['Verify note'],action='review')])
        safe=dict(critical_decision=False,material_contradiction=False,reason='Synthetic advisory only')
        review=dict(summary='Evidence checked',decision='REVIEW_ONLY',findings=[],required_evidence=[])
        replies=[dict(proposal=proposal,risk=safe),dict(review=review,risk=safe),
                 dict(review=review,risk=safe)]
        calls=[]
        def transport(client,model,prompt,**kwargs):
            calls.append((model,kwargs['reasoning']))
            return dict(text=json.dumps(replies[len(calls)-1]),success=True,model=model,
                        requested_model=model,actual_model=model,
                        usage=dict(input_tokens=10,output_tokens=2,total_tokens=12))
        with patch('governor_workbench.jobs.RouterClient.call',new=transport):
            status,value,_=self.request('POST','/api/actions',dict(action='scope_route_b_plan',
                scope_kind='project',scope_id='test'),self.auth())
            self.assertEqual(202,status,value)
            job=self.wait_terminal(lambda:app.store.job(value['job']['id']),('queued','running'))
        self.assertEqual('completed',job['status'],job.get('error'))
        self.assertEqual([('gpt-6-sol','high'),('gpt-6-luna','max'),
                          ('gpt-6-astra','medium')],calls)
        self.assertEqual('b_plus_v1',job['result']['route_variant'])
        self.assertEqual('mandatory_plan',job['result']['critical_review_reason'])
        candidate=job['result']['candidate']
        self.assertFalse(candidate.get('execution_enabled',False))
        status,value,_=self.request('POST','/api/strategies/adopt',dict(scope_kind='project',scope_id='test',
            candidate_id=candidate['id'],scope_hash=candidate['scope_hash'],expected_previous_id=None),self.auth())
        self.assertEqual(201,status,value)
        self.assertFalse(value['revision']['execution_enabled'])

    def test_revoked_egress_blocks_queued_route_before_any_model_call(self):
        app=self.server.app
        app.store.set_setting('monitor_enabled',False)
        app.registry.set_project_policy('test',requirements='Review fixture',model_egress=True)
        with patch.object(app.runner.pending,'put'):
            job=app.runner.submit('scope_route_b_review',scope_kind='project',scope_id='test')
        app.registry.set_project_policy('test',model_egress=False)
        sent=[]
        with patch('governor_workbench.jobs.RouterClient.call',side_effect=lambda *a,**k:sent.append(1)):
            with self.assertRaises(ValueError):
                app.runner.execute(job,app.settings()['supervisor'],threading.Event())
        self.assertEqual([],sent)
        app.store.update_job(job['id'],status='cancelled')


if __name__=='__main__': unittest.main()
