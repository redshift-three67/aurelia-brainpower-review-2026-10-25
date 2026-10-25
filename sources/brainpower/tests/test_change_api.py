import unittest
from unittest.mock import patch

from tests import test_server, test_change_execution


class ChangeApiTests(unittest.TestCase):
    setUp=test_server.ServerTests.setUp
    cleanup=test_server.ServerTests.cleanup
    request=test_server.ServerTests.request
    auth=test_server.ServerTests.auth

    def test_mutations_strict_and_session_origin_csrf_protected(self):
        cases={
            'begin':dict(candidate_id='a'*32,step_ids=['a','b'],binding_hash='b'*64,note='Explicit'),
            'acknowledge':dict(chain_id='a'*32,binding_hash='b'*64,note='Explicit'),
            'confirm':dict(chain_id='a'*32,expected_head=None,technical_receipt_id='b'*32,observed_scope_hash='c'*64,selection_id='d'*32,note='Explicit'),
            'propose':dict(consent_id='a'*32),
            'state':dict(candidate_id='a'*32),
            'successor-preview':dict(chain_id='a'*32)}
        for route,body in cases.items():
            path='/api/change-chains/'+route
            for field,value in (('Origin','https://evil.example'),('Cookie',''),('X-CSRF-Token','wrong')):
                headers=self.auth();headers[field]=value
                with self.subTest(route=route,field=field):self.assertEqual(403,self.request('POST',path,body,headers)[0])
            self.assertEqual(400,self.request('POST',path,dict(body,command='forbidden'),self.auth())[0])

    def test_real_temp_baseline_a_h1_b_h2_and_reverse_rollback_http(self):
        # Stop fixture observers before replacing their shared app dependencies.
        self.server.app.close()
        for worker in (self.server.app.monitor_thread,self.server.app.runner.thread):
            worker.join(30)
            self.assertFalse(worker.is_alive())
        fixture=test_change_execution.ChangeExecutionTests();fixture.setUp();self.addCleanup(fixture.doCleanups)
        # Keep all product operations in the temporary fixture, not the real server.
        with patch.object(self.server.app,'store',fixture.store),patch.object(self.server.app,'config',fixture.app.config),patch.object(self.server.app,'scope_context',fixture.app.scope_context),patch.object(self.server.app,'registry',fixture.app.registry):
            shown=fixture.pair_plan()
            status,value,_=self.request('POST','/api/change-chains/begin',dict(candidate_id=fixture.candidate['id'],step_ids=['fix','next'],binding_hash=shown['binding_hash'],note='Explicit baseline'),self.auth())
            self.assertEqual(200,status,value);fixture.chain=value['chain']
            receipt=fixture.complete(fixture.verified_job());fixture.receipt=receipt
            status,value,_=self.request('POST','/api/change-chains/confirm',dict(chain_id=fixture.chain['id'],expected_head=None,technical_receipt_id=receipt['id'],observed_scope_hash='b'*64,selection_id=fixture.selection['id'],note='Explicit H1'),self.auth())
            self.assertEqual(200,status,value);fixture.edge=value['event']
            status,shown,_=self.request('POST','/api/change-chains/successor-preview',dict(chain_id=fixture.chain['id']),self.auth())
            self.assertEqual(200,status,shown);self.assertTrue(shown['eligible'])
            status,value,_=self.request('POST','/api/change-chains/acknowledge',dict(chain_id=fixture.chain['id'],binding_hash=shown['binding_hash'],note='Explicit B preparation'),self.auth())
            self.assertEqual(200,status,value)
            fixture.consent=value['consent']
            # Propose is a separate operator action, never part of acknowledge.
            self.assertFalse(any(j['action']=='scope_patch' and j['request'].get('step_id')=='next' for j in fixture.store.jobs()))
            with patch.object(self.server.app.runner,'submit',return_value={'id':'fixture'}) as submit:
                status,value,_=self.request('POST','/api/change-chains/propose',dict(consent_id=value['consent']['id']),self.auth())
                self.assertEqual(202,status,value);self.assertEqual('next',submit.call_args.kwargs['step_id'])
            status,state,_=self.request('POST','/api/change-chains/state',dict(candidate_id=fixture.candidate['id']),self.auth())
            self.assertEqual(200,status,state);self.assertEqual(1,len(state['chains']));self.assertEqual(1,len(state['consents']))
            fixture.successor=lambda:dict(scope_kind='project',scope_id='pilot',scope_hash='b'*64,
                candidate_id=fixture.candidate['id'],step_id='next',successor_consent_id=fixture.consent['id'])
            fixture.applied_b()
            from governor_workbench.pilot_verification import verify
            from governor_workbench.technical_completion import complete
            report=verify(fixture.app,fixture.btx['id']);self.assertTrue(report['evidence_usable'],report)
            job=fixture.store.create_job('pilot_verify',None,dict(transaction_id=fixture.btx['id']))
            fixture.store.update_job(job['id'],status='completed',result=dict(success=True,post_apply_verification=report))
            b_receipt=complete(fixture.app,job['id'],'c'*64,'Explicit B completion')
            status,value,_=self.request('POST','/api/change-chains/confirm',dict(chain_id=fixture.chain['id'],expected_head=fixture.edge['id'],technical_receipt_id=b_receipt['id'],observed_scope_hash='c'*64,selection_id=fixture.selection['id'],note='Explicit H2'),self.auth())
            self.assertEqual(200,status,value)
            from governor_workbench.pilot_actions import rollback
            with self.assertRaises(ValueError):rollback(fixture.app,fixture.tx['id'],None)
            rollback(fixture.app,fixture.btx['id'],None);rollback(fixture.app,fixture.tx['id'],None)
            status,state,_=self.request('POST','/api/change-chains/state',dict(candidate_id=fixture.candidate['id']),self.auth())
            self.assertEqual(200,status,state);self.assertTrue(state['chains'][0]['requires_new_plan'])
            self.assertEqual(4,len(state['chains'][0]['events']))
            self.assertEqual(b'old WIP\r\n',(fixture.root/'main.py').read_bytes())
            self.assertFalse((fixture.root/'future.py').exists())
