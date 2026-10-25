import http.client
import json
from pathlib import Path
import tempfile
import threading
import unittest
from governor_workbench.config import load_config
from governor_workbench.server import make_server


class ServerTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        root=Path(self.tmp.name); repo=root/'repo'; (repo/'project_memories').mkdir(parents=True)
        (repo/'project_memories'/'note.md').write_text('original')
        import subprocess
        for args in (['init','-q'],['add','.'],['-c','user.name=Test','-c','user.email=test@example.invalid','commit','-qm','fixture']):
            subprocess.run(['git','-C',str(repo),*args],check=True,capture_output=True)
        path=root/'config.json'; path.write_text(json.dumps({'version':1,'projects':[{'id':'test','name':'Test','path':str(repo)}]}))
        self.server=make_server(load_config(path),port=0)
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True); self.thread.start()
        self.addCleanup(self.cleanup)
        self.port=self.server.server_port; self.host=f'127.0.0.1:{self.port}'
        _,self.state,headers=self.request('GET','/api/state')
        self.cookie=dict(headers)['Set-Cookie'].split(';')[0]

    def cleanup(self):
        self.server.shutdown(); self.server.app.close(); self.server.server_close(); self.thread.join(2)
        # Application.close has bounded joins; fixtures must release DB owners before deleting their directory.
        for worker in (self.server.app.monitor_thread,self.server.app.runner.thread,self.thread):
            worker.join(30)
            self.assertFalse(worker.is_alive(),'Test background thread did not stop: '+worker.name)

    def request(self,method,path,data=None,headers=None,timeout=25):
        # Match the shipped UI's 25-second request deadline; job waits are separate.
        client=http.client.HTTPConnection('127.0.0.1',self.port,timeout=timeout)
        body=json.dumps(data) if data is not None else None
        try:
            client.request(method,path,body=body,headers=headers or {})
            r=client.getresponse(); content=r.read(); response_headers=r.getheaders(); status=r.status
            return status,json.loads(content),response_headers
        finally:
            client.close()

    def test_request_helper_closes_connection_and_preserves_transport_errors(self):
        from unittest.mock import patch
        for stage in ('request','getresponse','read'):
            with self.subTest(stage=stage), patch('http.client.HTTPConnection') as connection:
                client=connection.return_value
                target=client.getresponse.return_value if stage=='read' else client
                failure=TimeoutError('transport fixture')
                getattr(target,stage).side_effect=failure
                with self.assertRaises(TimeoutError) as raised:
                    self.request('GET','/api/state')
                self.assertIs(raised.exception,failure)
                client.close.assert_called_once_with()

    def auth(self): return {'Cookie':self.cookie,'Origin':'http://'+self.host,'X-CSRF-Token':self.state['csrf_token'],'Content-Type':'application/json'}

    def wait_terminal(self,fetch,active,timeout=60):
        import time
        deadline=time.monotonic()+timeout
        while True:
            result=fetch()
            if result['status'] not in active:return result
            if time.monotonic()>=deadline:self.fail('Kein terminaler Testzustand innerhalb der Frist: '+result['status'])
            time.sleep(.1)

    def test_terminal_wait_handles_delayed_completion_and_reports_timeout(self):
        from unittest.mock import patch
        clock=[0.0]
        def sleep(seconds):clock[0]+=seconds
        with patch('time.monotonic',side_effect=lambda:clock[0]),patch('time.sleep',side_effect=sleep):
            result=self.wait_terminal(lambda:dict(status='running' if clock[0]<7 else 'completed'),('running',),timeout=10)
            self.assertEqual('completed',result['status'])
            with self.assertRaises(AssertionError):self.wait_terminal(lambda:dict(status='running'),('running',),timeout=1)

    def test_sequence_preview_is_protected_strict_and_does_not_enqueue(self):
        body={'stage_job_id':'a'*32}
        for field,value in (('Origin','https://evil.example'),('X-CSRF-Token','wrong'),('Cookie','')):
            headers=self.auth();headers[field]=value
            self.assertEqual(403,self.request('POST','/api/sequences/preview',body,headers)[0])
        for extra in ('command','steps','supervisor'):
            self.assertEqual(400,self.request('POST','/api/sequences/preview',{**body,extra:'forbidden'},self.auth())[0])
        before=self.server.app.store.jobs()
        status,value,_=self.request('POST','/api/sequences/preview',body,self.auth())
        self.assertEqual(200,status,value)
        self.assertFalse(value['eligible']);self.assertFalse(value['execution_authorized'])
        self.assertEqual(before,self.server.app.store.jobs())

    def test_cross_origin_mutation_denied(self):
        headers=self.auth(); headers['Origin']='https://evil.example'
        status,_,_=self.request('POST','/api/settings',{'monitor_enabled':False},headers)
        self.assertEqual(403,status)

    def test_sequence_start_cancel_are_strict_and_guarded(self):
        for path,body in (('/api/sequences/start',dict(stage_job_id='a'*32,binding_hash='b'*64,note='fixture')),
                          ('/api/sequences/cancel',dict(sequence_id='a'*32))):
            for field,value in (('Origin','https://evil.example'),('X-CSRF-Token','wrong'),('Cookie','')):
                headers=self.auth();headers[field]=value
                self.assertEqual(403,self.request('POST',path,body,headers)[0])
            self.assertEqual(400,self.request('POST',path,dict(body,command='forbidden'),self.auth())[0])
            self.assertEqual(400,self.request('POST',path,body,self.auth())[0])

    def test_change_chain_preview_is_strict_guarded_and_read_only(self):
        body=dict(candidate_id='a'*32,step_ids=['a','b'])
        path='/api/change-chains/preview'
        for field,value in (('Origin','https://evil.example'),('Cookie',''),('X-CSRF-Token','wrong')):
            headers=self.auth();headers[field]=value
            self.assertEqual(403,self.request('POST',path,body,headers)[0])
        self.assertEqual(400,self.request('POST',path,dict(body,command='forbidden'),self.auth())[0])
        before=self.server.app.store.jobs()
        status,result,_=self.request('POST',path,body,self.auth())
        self.assertEqual(200,status,result);self.assertFalse(result['eligible'])
        self.assertFalse(result['execution_authorized'])
        self.assertEqual(before,self.server.app.store.jobs())

    def test_change_chain_preview_valid_fixture_over_http(self):
        from tests.test_change_chain_preview import ChangeChainPreviewTests
        from unittest.mock import patch
        fixture=ChangeChainPreviewTests();fixture.setUp();self.addCleanup(fixture.doCleanups)
        with patch.object(self.server.app,'store',fixture.store), patch.object(self.server.app,'config',fixture.config), patch.object(self.server.app,'scope_context',fixture.app.scope_context):
            status,value,_=self.request('POST','/api/change-chains/preview',
                dict(candidate_id=fixture.candidate['id'],step_ids=['b','a']),self.auth())
        self.assertEqual(200,status,value);self.assertTrue(value['eligible'],value)
        self.assertEqual(['a','b'],value['binding']['step_ids'])
        self.assertEqual([],fixture.store.jobs())

    def test_test_chain_preview_is_strict_guarded_and_read_only(self):
        body=dict(candidate_id='a'*32,step_ids=['one','two'])
        path='/api/test-chains/preview'
        for field,value in (('Origin','https://evil.example'),('Cookie',''),('X-CSRF-Token','wrong')):
            headers=self.auth();headers[field]=value
            self.assertEqual(403,self.request('POST',path,body,headers)[0])
        self.assertEqual(400,self.request('POST',path,dict(body,command='forbidden'),self.auth())[0])
        before=self.server.app.store.jobs()
        status,result,_=self.request('POST',path,body,self.auth())
        self.assertEqual(200,status,result);self.assertFalse(result['eligible'])
        self.assertFalse(result['execution_authorized']);self.assertFalse(result['model_transmission_required'])
        self.assertEqual(before,self.server.app.store.jobs())

    def test_forbidden_post_consumes_bounded_body_before_reply(self):
        import io
        from unittest.mock import Mock
        from governor_workbench.server import Handler
        handler=object.__new__(Handler)
        handler.headers={'Content-Length':'7'};handler.command='POST'
        handler.rfile=io.BytesIO(b'payload');handler.connection=Mock()
        handler.connection.gettimeout.return_value=None
        handler.valid_host=lambda:False
        positions=[];handler.reply=lambda *args:positions.append(handler.rfile.tell())
        self.assertFalse(handler.guard(write=True))
        self.assertEqual([7],positions)
        self.assertTrue(handler.close_connection)
        for headers in ({'Content-Length':'1048577'},{'Content-Length':'invalid'},
                        {'Content-Length':'7','Transfer-Encoding':'chunked'}):
            handler.headers=headers;handler.rfile=io.BytesIO(b'payload')
            self.assertFalse(handler.guard(write=True))
            self.assertEqual(0,handler.rfile.tell())

    def test_forbidden_partial_body_has_bounded_wait(self):
        import socket,time
        with socket.create_connection(('127.0.0.1',self.port),timeout=3) as client:
            client.sendall((f'POST /api/sequences/start HTTP/1.0\r\nHost: {self.host}\r\nContent-Length: 100\r\nOrigin: https://evil.example\r\n\r\n'+'x').encode())
            start=time.monotonic();response=client.recv(4096)
            self.assertIn(b'403',response);self.assertLess(time.monotonic()-start,2)

    def test_runtime_actions_reject_foreign_origin_and_extra_commands(self):
        profile = self.state['runtime_profiles']['profiles'][0]
        body = {'profile_id': profile['id'], 'profile_hash': profile['hash']}
        headers = self.auth(); headers['Origin'] = 'https://evil.example'
        status, _, _ = self.request('POST', '/api/runtime/start', body, headers)
        self.assertEqual(status, 403)
        status, _, _ = self.request('POST', '/api/runtime/start', dict(body, command='whoami'), self.auth())
        self.assertEqual(status, 400)
        status, _, _ = self.request('POST', '/api/runtime/start', dict(body, profile_hash='0'*64), self.auth())
        self.assertEqual(status, 400)

    def test_runtime_check_rejects_untrusted_requests(self):
        body = {'instance_id':'a'*32}
        headers = self.auth(); headers['Origin'] = 'https://evil.example'
        self.assertEqual(self.request('POST','/api/runtime/check',body,headers)[0],403)
        self.assertEqual(self.request('POST','/api/runtime/check',dict(body,url='http://example.invalid'),self.auth())[0],400)
        self.assertEqual(self.request('POST','/api/runtime/check',{'instance_id':'bad'},self.auth())[0],400)

    def test_pilot_assessment_is_protected_and_reports_missing_evidence(self):
        import time
        body={'verified_test_job_id':'a'*32}
        headers=self.auth(); headers['Origin']='https://evil.example'
        self.assertEqual(self.request('POST','/api/pilot/assess',body,headers)[0],403)
        self.assertEqual(self.request('POST','/api/pilot/assess',dict(body,command='bad'),self.auth())[0],400)
        status,value,_=self.request('POST','/api/pilot/assess',body,self.auth())
        self.assertEqual(status,202)
        job=self.wait_terminal(lambda:self.server.app.store.job(value['job']['id']),('queued','running'))
        self.assertEqual(job['status'],'completed',job)
        self.assertFalse(job['result']['pilot_assessment']['evidence_usable'])
        self.assertFalse(job['result']['approval_granted'])

    def test_post_apply_verification_is_protected_and_persisted(self):
        import time
        body={'transaction_id':'a'*32}
        headers=self.auth(); headers['Origin']='https://evil.example'
        self.assertEqual(self.request('POST','/api/pilot/verify',body,headers)[0],403)
        self.assertEqual(self.request('POST','/api/pilot/verify',dict(body,command='bad'),self.auth())[0],400)
        self.assertEqual(self.request('POST','/api/pilot/verify',{'transaction_id':'bad'},self.auth())[0],400)
        status,value,_=self.request('POST','/api/pilot/verify',body,self.auth())
        self.assertEqual(status,202)
        job=self.wait_terminal(lambda:self.server.app.store.job(value['job']['id']),('queued','running'))
        self.assertEqual(job['status'],'completed',job)
        self.assertFalse(job['result']['post_apply_verification']['evidence_usable'])
        self.assertFalse(job['result']['post_apply_verification']['step_completion_granted'])
        self.assertFalse(job['result']['product_files_changed'])

    def test_explicit_test_chain_over_http(self):
        import time
        from unittest.mock import patch
        from tests.test_test_chains import TestChainPreviewTests
        from governor_workbench.plans import PlanBook
        from governor_workbench.test_chain_store import TestChainJournal
        fixture=TestChainPreviewTests();fixture.setUp();self.addCleanup(fixture.doCleanups)
        app=self.server.app;app.config['staging_pilot_roots']=[str(fixture.root)]
        book=PlanBook(app.store,app.config)
        candidate=book.save_candidate(fixture.context,fixture.candidate['proposal'],fixture.candidate['review'],'fixture')
        selection=book.approve(candidate['id'],'a'*64,fixture.context,['before','test','second'],'sequence')
        book.complete_step(candidate['id'],'before',fixture.context,'a'*64,selection['id'],'Reviewed')
        body=dict(candidate_id=candidate['id'],step_ids=['second','test'])
        with patch.object(app,'scope_context',return_value=fixture.context),patch('governor_workbench.jobs.RouterClient') as models:
            status,p,_=self.request('POST','/api/test-chains/preview',body,self.auth())
            self.assertEqual(200,status);self.assertTrue(p['eligible'],p)
            payload=dict(body,binding_hash=p['binding_hash'],note='Explicit chain')
            bad=self.auth();bad['Origin']='https://evil.example'
            self.assertEqual(403,self.request('POST','/api/test-chains/start',payload,bad)[0])
            self.assertEqual(400,self.request('POST','/api/test-chains/start',dict(payload,command='bad'),self.auth())[0])
            status,value,_=self.request('POST','/api/test-chains/start',payload,self.auth())
            self.assertEqual(202,status,value)
            journal=TestChainJournal(app.store)
            row=self.wait_terminal(lambda:journal.get(value['chain']['id']),('testing','checking'))
            self.assertEqual('completed',row['status'],row);self.assertEqual(2,len(row['children']))
            status,again,_=self.request('POST','/api/test-chains/start',payload,self.auth())
            self.assertEqual(202,status);self.assertEqual(row['id'],again['chain']['id'])
            self.assertEqual(400,self.request('POST','/api/test-chains/cancel',{'chain_id':row['id'],'extra':1},self.auth())[0])
            self.assertEqual(403,self.request('POST','/api/test-chains/cancel',{'chain_id':row['id']},bad)[0])
            self.assertEqual(200,self.request('POST','/api/test-chains/cancel',{'chain_id':row['id']},self.auth())[0])
            models.assert_not_called()

    def test_standalone_plan_test_and_chain_over_http(self):
        import time
        from unittest.mock import patch
        from tests.test_plan_tests import PlanTestCompletionTests
        from governor_workbench.plans import PlanBook
        fixture=PlanTestCompletionTests(); fixture.setUp(); self.addCleanup(fixture.doCleanups)
        app=self.server.app
        app.config['staging_pilot_roots']=[str(fixture.root)]
        book=PlanBook(app.store,app.config)
        candidate=book.save_candidate(fixture.context,fixture.candidate['proposal'],fixture.candidate['review'],'fixture')
        selection=book.approve(candidate['id'],'a'*64,fixture.context,['before','test','after'],'sequence')
        book.complete_step(candidate['id'],'before',fixture.context,'a'*64,selection['id'],'Reviewed')
        body=dict(candidate_id=candidate['id'],step_id='test',scope_hash='a'*64,selection_id=selection['id'])
        with patch.object(app,'scope_context',return_value=fixture.context):
            headers=self.auth(); headers['Origin']='https://evil.example'
            self.assertEqual(403,self.request('POST','/api/plans/test',body,headers)[0])
            self.assertEqual(400,self.request('POST','/api/plans/test',dict(body,command='bad'),self.auth())[0])
            status,value,_=self.request('POST','/api/plans/test',body,self.auth())
            self.assertEqual(202,status,value)
            job=self.wait_terminal(lambda:app.store.job(value['job']['id']),('queued','running'))
            self.assertEqual('completed',job['status'],job)
            self.assertTrue(job['result']['success'],job)
            data=dict(scope_kind='project',scope_id='pilot',candidate_id=candidate['id'])
            status,value,_=self.request('POST','/api/plans/dependencies',data,self.auth())
            self.assertEqual(200,status,value)
            rows={r['id']:r for r in value['report']['steps']}
            self.assertEqual('accepted',rows['test']['completion_status'])
            self.assertEqual([],rows['after']['missing_completion_ids'])
            payload=dict(data,step_id='after',scope_hash='a'*64,selection_id=selection['id'],note='Reviewed')
            self.assertEqual(201,self.request('POST','/api/plans/complete-step',payload,self.auth())[0])
            for _ in range(2):
                status,value,_=self.request('POST','/api/plans/test',body,self.auth())
                self.assertEqual(202,status,value)
                attempt=self.wait_terminal(lambda:app.store.job(value['job']['id']),('queued','running'))
                self.assertEqual('completed',attempt['status'],attempt)
                self.assertTrue(attempt['result']['success'])
            self.assertEqual(400,self.request('POST','/api/plans/test',body,self.auth())[0])
            _,value,_=self.request('POST','/api/plans/dependencies',data,self.auth())
            row=next(r for r in value['report']['steps'] if r['id']=='test')
            self.assertEqual(3,row['test_attempts']['used'])
            self.assertFalse(row['test_run_available'])
            self.assertEqual('accepted',row['completion_status'])
            (fixture.root/'tests/test_ok.py').write_text('changed')
            _,value,_=self.request('POST','/api/plans/dependencies',data,self.auth())
            self.assertEqual('stale',next(r for r in value['report']['steps'] if r['id']=='after')['completion_status'])

    def test_failure_diagnosis_over_http(self):
        import time
        from unittest.mock import patch
        from tests.test_plan_tests import PlanTestCompletionTests
        from governor_workbench.plans import PlanBook
        fixture=PlanTestCompletionTests();fixture.setUp();self.addCleanup(fixture.doCleanups)
        (fixture.root/'tests/test_ok.py').write_text('import unittest\nclass Test(unittest.TestCase):\n def test_bad(self):self.fail("expected")\n')
        app=self.server.app;app.config['staging_pilot_roots']=[str(fixture.root)]
        book=PlanBook(app.store,app.config)
        candidate=book.save_candidate(fixture.context,fixture.candidate['proposal'],fixture.candidate['review'],'fixture')
        selection=book.approve(candidate['id'],'a'*64,fixture.context,['before','test','after'],'sequence')
        book.complete_step(candidate['id'],'before',fixture.context,'a'*64,selection['id'],'Reviewed')
        def wait(value):
            return self.wait_terminal(lambda:app.store.job(value['job']['id']),('queued','running'))
        with patch.object(app,'scope_context',return_value=fixture.context):
            status,value,_=self.request('POST','/api/plans/test',dict(candidate_id=candidate['id'],step_id='test',scope_hash='a'*64,selection_id=selection['id']),self.auth())
            self.assertEqual(202,status,value);source=wait(value)
            self.assertFalse(source['result']['success'])
            body=dict(job_id=source['id']);headers=self.auth();headers['Origin']='https://evil.example'
            self.assertEqual(403,self.request('POST','/api/plans/test-failure',body,headers)[0])
            self.assertEqual(400,self.request('POST','/api/plans/test-failure',dict(body,repair=True),self.auth())[0])
            status,value,_=self.request('POST','/api/plans/test-failure',body,self.auth())
            self.assertEqual(202,status,value);diagnosis=wait(value)
            self.assertEqual('completed',diagnosis['status'],diagnosis)
            self.assertTrue(diagnosis['result']['test_failure']['evidence_usable'])
            self.assertFalse(diagnosis['result']['test_failure']['repair_authorized'])
            (fixture.root/'tests/test_ok.py').write_text('changed')
            status,value,_=self.request('POST','/api/plans/test-failure',body,self.auth())
            self.assertEqual(202,status,value)
            self.assertFalse(wait(value)['result']['test_failure']['evidence_usable'])
            report=book.dependency_report(candidate['id'],fixture.context)
            self.assertEqual(1,report['steps'][1]['test_attempts']['used'])
            (fixture.root/'tests/test_ok.py').write_text('import unittest\nclass Test(unittest.TestCase):\n def test_bad(self):self.fail("expected")\n')
            _,value,_=self.request('POST','/api/plans/test-failure',body,self.auth())
            diagnosis=wait(value)
            fixture.context.update(intake={},decision_hash='d'*64)
            repair=dict(diagnosis_job_id=diagnosis['id'],note='Begrenzte Reparaturplanung und Modellversand bestätigt')
            self.assertEqual(403,self.request('POST','/api/plans/repair',repair,headers)[0])
            self.assertEqual(400,self.request('POST','/api/plans/repair',dict(repair,execute=True),self.auth())[0])
            change=dict(fixture.candidate['proposal']['steps'][1],id='fix',action='change',depends_on=[])
            check=dict(change,id='check',action='test',depends_on=['fix'])
            proposal=dict(summary='Bounded repair',steps=[change,check])
            invalid=dict(summary='Out of scope',steps=[dict(change,scope=['outside.py']),check])
            with patch('governor_workbench.planning_llm.propose_plan',return_value=dict(proposal=invalid,review=fixture.candidate['review'])):
                status,value,_=self.request('POST','/api/plans/repair',repair,self.auth())
                self.assertEqual(202,status,value);blocked=wait(value)
                self.assertIn('candidate_blocked',blocked['result'])
                self.assertNotIn('candidate',blocked['result'])
            with patch('governor_workbench.planning_llm.propose_plan',return_value=dict(proposal=proposal,review=fixture.candidate['review'])) as model:
                status,value,_=self.request('POST','/api/plans/repair',repair,self.auth())
                self.assertEqual(202,status,value)
                planned=wait(value)
            self.assertEqual('completed',planned['status'],planned)
            self.assertIn('candidate',planned['result'])
            self.assertFalse(planned['result']['approval_granted'])
            self.assertEqual(model.call_args.args[0]['repair_evidence']['binding']['source_job_id'],source['id'])
            new=planned['result']['candidate']
            self.assertFalse(book.execution_permission(new['id'],'fix',fixture.context)['plan_selection_approved'])

    def test_dependency_report_is_protected_and_does_not_approve(self):
        from tests.test_plans import PlanTests
        from governor_workbench.plans import PlanBook
        from unittest.mock import patch
        fixture=PlanTests(); fixture.setUp(); self.addCleanup(fixture.doCleanups)
        book=PlanBook(self.server.app.store)
        candidate=book.save_candidate(fixture.context,fixture.proposal,fixture.review,'fixture')
        body={'scope_kind':'project','scope_id':'alpha','candidate_id':candidate['id']}
        headers=self.auth(); headers['Origin']='https://evil.example'
        self.assertEqual(self.request('POST','/api/plans/dependencies',body,headers)[0],403)
        self.assertEqual(self.request('POST','/api/plans/dependencies',dict(body,execute=True),self.auth())[0],400)
        with patch.object(self.server.app,'scope_context',return_value=fixture.context):
            status,value,_=self.request('POST','/api/plans/dependencies',body,self.auth())
        self.assertEqual(status,200,value)
        self.assertTrue(value['report']['current'])
        self.assertFalse(value['report']['execution_enabled'])
        self.assertFalse(book.execution_permission(candidate['id'],'first',fixture.context)['plan_selection_approved'])

    def test_completion_api_requires_explicit_protected_fields(self):
        from tests.test_plans import PlanTests
        from governor_workbench.plans import PlanBook
        from unittest.mock import patch
        fixture=PlanTests(); fixture.setUp(); self.addCleanup(fixture.doCleanups)
        book=PlanBook(self.server.app.store)
        candidate=book.save_candidate(fixture.context,fixture.proposal,fixture.review,'fixture')
        selection=book.approve(candidate['id'],'a'*64,fixture.context,['first'])
        body=dict(scope_kind='project',scope_id='alpha',candidate_id=candidate['id'],step_id='first',scope_hash='a'*64,selection_id=selection['id'],note='Fachlich geprüft')
        headers=self.auth(); headers['Origin']='https://evil.example'
        self.assertEqual(self.request('POST','/api/plans/complete-step',body,headers)[0],403)
        self.assertEqual(self.request('POST','/api/plans/complete-step',dict(body,execute=True),self.auth())[0],400)
        with patch.object(self.server.app,'scope_context',return_value=fixture.context):
            status,value,_=self.request('POST','/api/plans/complete-step',body,self.auth())
        self.assertEqual(status,201,value)
        self.assertFalse(value['receipt']['product_gate_approved'])
        withdraw=dict(candidate_id=candidate['id'],step_id='first',expected_receipt_id=value['receipt']['id'],note='Zurückgenommen')
        self.assertEqual(self.request('POST','/api/plans/withdraw-completion',withdraw,headers)[0],403)
        self.assertEqual(self.request('POST','/api/plans/withdraw-completion',withdraw,self.auth())[0],201)

    @unittest.skipUnless(__import__('os').name == 'nt', 'Windows runtime profile')
    def test_runtime_start_stop_through_single_worker(self):
        import socket, time
        with socket.socket() as sock:
            sock.bind(('127.0.0.1',0)); port = sock.getsockname()[1]
        self.server.app.config['runtime_probe_port'] = port
        profile = self.server.app.runtime_profiles.profile()
        status, value, _ = self.request('POST', '/api/runtime/start',
            {'profile_id':profile['id'],'profile_hash':profile['hash']}, self.auth())
        self.assertEqual(status,202)
        def wait(key):
            return self.wait_terminal(lambda:self.server.app.store.job(key),('queued','running'))
        job = wait(value['job']['id'])
        self.assertEqual(job['status'],'completed',job)
        row = job['result']['runtime_instance']
        self.assertEqual(row['status'],'running')
        status, value, _ = self.request('POST','/api/runtime/check',{'instance_id':row['id']},self.auth())
        self.assertEqual(status,202)
        checked = wait(value['job']['id'])
        self.assertEqual(checked['status'],'completed',checked)
        self.assertTrue(checked['result']['runtime_instance']['last_check']['success'])
        status, value, _ = self.request('POST','/api/runtime/stop',{'instance_id':row['id']},self.auth())
        self.assertEqual(status,202)
        job = wait(value['job']['id'])
        self.assertEqual(job['result']['runtime_instance']['status'],'stopped')

    def test_session_cookie_is_separate_for_each_local_port(self):
        self.assertTrue(self.cookie.startswith('governor_session_'+str(self.port)+'='))

    def test_registry_group_and_single_registration(self):
        repo=Path(self.tmp.name)/'single'; repo.mkdir()
        status,value,_=self.request('POST','/api/registry/projects',{'name':'Single','path':str(repo),'requirements':'Local checks','model_egress':False},self.auth())
        self.assertEqual(201,status,value)
        project=value['project']; self.assertIsNone(project['group_id'])
        status,value,_=self.request('POST','/api/registry/groups',{'name':'New group'},self.auth())
        self.assertEqual(201,status,value)
        group=value['group']
        status,value,_=self.request('POST','/api/registry/memberships',{'project_id':project['id'],'group_id':group['id'],'role':'parent'},self.auth())
        self.assertEqual(201,status,value)
        _,current,_=self.request('GET','/api/state')
        self.assertEqual(group['id'],next(p for p in current['registry']['projects'] if p['id']==project['id'])['group_id'])
        self.assertEqual(1,len(list((repo/'project_memories').glob('strategy_project*.md'))))
        self.assertIn('incomplete',next((repo/'project_memories').glob('*.md')).read_text())

    def test_registry_rejects_cross_origin(self):
        headers=self.auth(); headers['Origin']='https://evil.example'
        status,_,_=self.request('POST','/api/registry/groups',{'name':'Bad'},headers)
        self.assertEqual(403,status)

    def test_matrix_keeps_current_report_outside_visible_job_window(self):
        from governor_workbench.evidence import fingerprint
        app=self.server.app
        observation=app.refresh(force_git=True)
        app.add_decision(dict(step_id='reconcile_sources',kind='authorize',reason='Synthetic read-only scope',evidence_hash=observation['evidence_hash']))
        observation=app.refresh(force_git=True)
        report=app.store.create_job('governance_report',None)
        app.store.update_job(report['id'],status='completed',result=dict(step_id='reconcile_sources',success=True,
            evidence_hash=observation['evidence_hash'],decision_hash=fingerprint(app.store.decisions()),stale=False))
        for _ in range(40):
            item=app.store.create_job('refresh',None)
            app.store.update_job(item['id'],status='completed',result={})
        state=app.state()
        self.assertNotIn(report['id'],[j['id'] for j in state['jobs']])
        row=next(s for s in state['governor']['steps'] if s['id']=='reconcile_sources')
        self.assertEqual('review_required',row['status'])
        self.assertFalse(row['can_run'])

    def test_scoped_review_requires_saved_permission(self):
        status,value,_=self.request('POST','/api/actions',{'action':'scope_review','scope_kind':'project','scope_id':'test'},self.auth())
        self.assertEqual(400,status,value)
        self.assertIn('Modell',value['error'])

    def test_invalid_registry_id_returns_client_error(self):
        status,_,_=self.request('POST','/api/registry/archive',{'project_id':[]},self.auth())
        self.assertEqual(400,status)

    def test_scoped_plan_intake_review_and_selection_end_to_end(self):
        import time
        from unittest.mock import patch
        app=self.server.app; app.config['orchestrator_transport']='router'
        status,_,_=self.request('POST','/api/registry/policy',{'project_id':'test','requirements':'Review note','model_egress':True},self.auth())
        self.assertEqual(201,status)
        context=app.scope_context('project','test',False)
        self.assertFalse(context['plan_ready'])
        fields={'requirements':'Review note','test_strategy':'Read known fixture','dependencies':'None','open_evidence':'No runtime claims'}
        draft_payload={'scope_kind':'project','scope_id':'test','scope_hash':context['scope_hash'],'project_id':'test',
            'fields':fields,'sources':[{'name':m['name'],'sha256':m['sha256']} for m in context['projects'][0]['memories']]}
        status,_,_=self.request('POST','/api/intake/drafts',draft_payload,{'Content-Type':'application/json'})
        self.assertEqual(403,status)
        status,value,_=self.request('POST','/api/intake/drafts',draft_payload,self.auth())
        self.assertEqual(201,status,value)
        context=app.scope_context('project','test',False)
        self.assertFalse(context['plan_ready'])
        status,_,_=self.request('POST','/api/intake',{'scope_kind':'project','scope_id':'test','scope_hash':context['scope_hash'],'project_id':'test',
            'fields':{'requirements':'Review note','test_strategy':'Read known fixture','dependencies':'None','open_evidence':'No runtime claims'}},self.auth())
        self.assertEqual(201,status)
        proposal={'summary':'Review fixture','steps':[{'id':'read_note','title':'Read note','project_id':'test','priority':1,'depends_on':[],
            'rationale':'Establish source','scope':['project_memories/note.md'],'tests':['Verify note'],'action':'review'}]}
        review={'summary':'No unsupported claims','decision':'REVIEW_ONLY','findings':[],'required_evidence':[]}
        class Client:
            def call(self,model,prompt,**kwargs):
                return {'text':json.dumps(proposal if model=='gpt-5.6-terra' else review),'success':True,'model':model}
        with patch('governor_workbench.jobs.RouterClient',return_value=Client()):
            status,value,_=self.request('POST','/api/actions',{'action':'scope_plan','scope_kind':'project','scope_id':'test'},self.auth())
            self.assertEqual(202,status,value)
            job=self.wait_terminal(lambda:app.store.job(value['job']['id']),('queued','running'))
        self.assertEqual('completed',job['status'],job.get('error'))
        candidate=job['result']['candidate']
        status,value,_=self.request('POST','/api/plans/approve',{'scope_kind':'project','scope_id':'test','candidate_id':candidate['id'],
            'scope_hash':candidate['scope_hash'],'selected_step_ids':['read_note'],'mode':'single'},self.auth())
        self.assertEqual(201,status,value)
        self.assertFalse(value['approval']['execution_enabled'])
        status,value,_=self.request('GET','/api/intake/drafts?kind=project&id=test',headers=self.auth())
        self.assertEqual(200,status,value)
        self.assertTrue(value['drafts'][0]['current'],'Confirming intake must not stale unchanged-source drafts')
        payload={'scope_kind':'project','scope_id':'test','candidate_id':candidate['id'],
                 'scope_hash':candidate['scope_hash'],'expected_previous_id':None}
        status,_,_=self.request('POST','/api/strategies/adopt',payload,{'Content-Type':'application/json'})
        self.assertEqual(403,status)
        status,value,_=self.request('POST','/api/strategies/adopt',payload,self.auth())
        self.assertEqual(201,status,value)
        self.assertFalse(value['revision']['execution_enabled'])
        self.assertEqual(1,value['revision']['version'])
        status,value,_=self.request('GET','/api/strategies?kind=project&id=test',headers=self.auth())
        self.assertEqual(200,status,value)
        self.assertTrue(value['revisions'][0]['current'])
        status,_,_=self.request('POST','/api/strategies/adopt',payload,self.auth())
        self.assertEqual(400,status)
        self.assertEqual('original',(Path(self.tmp.name)/'repo/project_memories/note.md').read_text())
        (Path(self.tmp.name)/'repo/project_memories/note.md').write_text('drift')
        status,value,_=self.request('GET','/api/strategies?kind=project&id=test',headers=self.auth())
        self.assertEqual(200,status,value)
        self.assertFalse(value['revisions'][0]['current'])

    def test_pilot_patch_test_and_independent_review_end_to_end(self):
        self._pilot_pipeline(False)

    def test_explicit_pilot_apply_and_rollback_over_http(self):
        self._pilot_pipeline(False,apply_back=True)

    def test_repair_from_real_failure_through_apply_followup_and_rollback(self):
        self._pilot_pipeline(False,apply_back=True,repair=True)

    def test_approved_sequence_halts_then_manual_transfer_still_works(self):
        self._pilot_pipeline(False,apply_back=True,sequence=True)

    def test_operator_answer_resumes_same_job_after_both_reviews(self):
        self._question_pipeline(True)

    def test_changed_scope_answer_stops_for_new_review(self):
        self._question_pipeline(False)

    def _question_pipeline(self,within_scope):
        import time
        from unittest.mock import patch
        from governor_workbench.intake import Intake
        app=self.server.app; app.store.set_setting('monitor_enabled',False)
        app.config['orchestrator_transport']='router'
        app.registry.set_project_policy('test',requirements='Read fixture note',model_egress=True)
        context=app.scope_context('project','test',False)
        Intake(app.store).accept(context,context['scope_hash'],'test',dict(requirements='Read note',test_strategy='Read known fixture',dependencies='None',open_evidence='No runtime claim'))
        proposal=dict(summary='Review note',steps=[dict(id='read',title='Read note',project_id='test',priority=1,depends_on=[],rationale='Read current fixture',scope=['project_memories/note.md'],tests=['Read fixture'],action='review')])
        review=dict(summary='Valid within phase',decision='REVIEW_ONLY',findings=[],required_evidence=[])
        calls=[]
        class Client:
            asked=False
            def call(self,model,prompt,**kwargs):
                calls.append((model,prompt))
                if 'ORIGINAL_QUESTION_AND_SAVED_ANSWER:' in prompt:
                    value=dict(within_scope=within_scope,reason='Clarification only' if within_scope else 'New requirements')
                elif model=='gpt-5.6-terra':
                    value=proposal if self.asked else dict(question=dict(text='Welche Notiz ist gemeint?',reason='Bezug eindeutig bestätigen.'))
                    self.asked=True
                else: value=review
                return dict(success=True,model=model,text=json.dumps(value))
        def wait(key):
            return self.wait_terminal(lambda:app.store.job(key),('queued','running'))
        with patch('governor_workbench.jobs.RouterClient',return_value=Client()):
            status,value,_=self.request('POST','/api/actions',dict(action='scope_plan',scope_kind='project',scope_id='test'),self.auth())
            self.assertEqual(202,status,value)
            key=value['job']['id']; job=wait(key)
            self.assertEqual('waiting_for_operator',job['status'],job)
            question=app.questions.list(status='pending')[0]
            status,state,_=self.request('GET','/api/state')
            self.assertEqual(question['id'],state['operator_questions'][0]['id'])
            status,value,_=self.request('POST','/api/questions/answer',dict(question_id=question['id'],answer='Die vorhandene note.md.',scope_hash=question['scope_hash']),self.auth())
            self.assertEqual(202,status,value)
            self.assertEqual(key,value['job']['id'])
            final=wait(key)
        self.assertEqual('completed' if within_scope else 'review_required',final['status'],final)
        self.assertEqual(within_scope,'candidate' in final['result'])
        self.assertEqual(6 if within_scope else 4,len(calls))
        self.assertEqual(1,len(app.questions.answers(key)))
        self.assertFalse(app.questions.list(status='pending'))
        self.assertTrue(app.runner.thread.is_alive())
        self.assertFalse(final['result']['approval_granted'])
        self.assertEqual('original',(Path(self.tmp.name)/'repo/project_memories/note.md').read_text())

    def test_cancel_after_local_tests_preserves_actual_evidence(self):
        self._pilot_pipeline(True)

    def _pilot_pipeline(self,cancel_after_tests,apply_back=False,repair=False,sequence=False):
        import time
        from unittest.mock import patch
        from governor_workbench.plans import PlanBook
        from governor_workbench.intake import Intake
        app=self.server.app; app.store.set_setting('monitor_enabled',False)
        app.config['orchestrator_transport']='router'
        repo=Path(self.tmp.name)/'repo'
        (repo/'calc.py').write_text('def value(): return 1\n')
        (repo/'tests').mkdir()
        test_content='import unittest\nfrom calc import value\nclass Check(unittest.TestCase):\n def test_value(self): self.assertEqual(value(),2)\n'
        (repo/'tests/test_calc.py').write_text(test_content)
        app.config['staging_pilot_roots']=[str(repo.resolve())]
        app.registry.set_project_policy('test',requirements='Return two',model_egress=True)
        context=app.scope_context('project','test',False)
        Intake(app.store).accept(context,context['scope_hash'],'test',dict(requirements='Return two',test_strategy='unittest',dependencies='None',open_evidence='Pilot only'))
        context=app.scope_context('project','test')
        proposal=dict(summary='Fix synthetic value',steps=[dict(id='fix',title='Return two',project_id='test',priority=1,depends_on=[],rationale='Fixture check',scope=['calc.py','tests/test_calc.py'],tests=['unittest test_value'],action='change')])
        if apply_back:
            proposal['steps'].append(dict(proposal['steps'][0],id='check',title='Check after transition',action='test',depends_on=['fix']))
            proposal['steps'].append(dict(proposal['steps'][0],id='review',title='Review chain',action='review',depends_on=['check']))
        review=dict(summary='No open findings',decision='REVIEW_ONLY',findings=[],required_evidence=[])
        initial=dict(summary='Observe actual failure',steps=[dict(proposal['steps'][0],id='baseline',action='test')]) if repair else proposal
        book=PlanBook(app.store); candidate=book.save_candidate(context,initial,review,'a'*32)
        selection=book.approve(candidate['id'],context['scope_hash'],context,['baseline'] if repair else (['fix','check','review'] if apply_back else ['fix']),'single' if repair or not apply_back else 'sequence')
        calls=[]
        class Client:
            def call(self,model,prompt,**kwargs):
                calls.append(model)
                if cancel_after_tests and 'OBSERVED_TEST_RESULT:' in prompt:
                    kwargs['cancel_event'].set()
                value=dict(summary='Fix value',files=[dict(path='calc.py',content='def value(): return 2\n')]) if model=='gpt-5.6-terra' else review
                if repair and model=='gpt-5.6-terra' and '"steps":[{"id":string' in prompt:value=proposal
                return dict(success=True,model=model,text=json.dumps(value))
        def wait(key,timeout=60):
            return self.wait_terminal(lambda:app.store.job(key),('queued','running'),timeout=timeout)
        with patch('governor_workbench.jobs.RouterClient',return_value=Client()):
            if repair:
                baseline=candidate['id']
                status,value,_=self.request('POST','/api/plans/test',dict(candidate_id=baseline,step_id='baseline',scope_hash=context['scope_hash'],selection_id=selection['id']),self.auth())
                self.assertEqual(202,status,value);failed=wait(value['job']['id'])
                self.assertEqual('failed',failed['status'],failed)
                self.assertEqual(1,failed['result']['test_evidence']['test']['failures'])
                status,value,_=self.request('POST','/api/plans/test-failure',dict(job_id=failed['id']),self.auth())
                self.assertEqual(202,status,value);diagnosed=wait(value['job']['id'])
                self.assertTrue(diagnosed['result']['test_failure']['evidence_usable'])
                status,value,_=self.request('POST','/api/plans/repair',dict(diagnosis_job_id=diagnosed['id'],note='Synthetic repair planning and model transmission authorized'),self.auth())
                # Repair planning revalidates the failure both before and after model planning.
                self.assertEqual(202,status,value);planned=wait(value['job']['id'],timeout=120)
                self.assertEqual('completed',planned['status'],planned)
                candidate=planned['result']['candidate']
                self.assertEqual(baseline,planned['result']['repair_binding']['candidate_id'])
                self.assertEqual(failed['id'],planned['result']['repair_binding']['source_job_id'])
                self.assertFalse(planned['result']['approval_granted'])
                status,_,_=self.request('POST','/api/actions',dict(action='scope_patch',scope_kind='project',scope_id='test',candidate_id=candidate['id'],step_id='fix'),self.auth())
                self.assertEqual(400,status)
                status,value,_=self.request('POST','/api/plans/approve',dict(scope_kind='project',scope_id='test',candidate_id=candidate['id'],scope_hash=context['scope_hash'],selected_step_ids=['fix','check','review'],mode='sequence'),self.auth())
                self.assertEqual(201,status,value)
            status,value,_=self.request('POST','/api/actions',dict(action='scope_patch',scope_kind='project',scope_id='test',candidate_id=candidate['id'],step_id='fix'),self.auth())
            self.assertEqual(202,status,value)
            staged=wait(value['job']['id'])
            self.assertEqual('completed',staged['status'],staged)
            self.assertIn('stage',staged['result'])
            if repair:
                before_jobs=app.store.jobs();before_calls=list(calls)
                status,preview,_=self.request('POST','/api/sequences/preview',dict(stage_job_id=staged['id']),self.auth())
                self.assertEqual(200,status,preview);self.assertTrue(preview['eligible'],preview)
                self.assertFalse(preview['execution_authorized'])
                self.assertEqual(candidate['id'],preview['binding']['candidate_id'])
                self.assertEqual(before_jobs,app.store.jobs());self.assertEqual(before_calls,calls)
                app.registry.set_project_policy('test',model_egress=False)
                status,blocked,_=self.request('POST','/api/sequences/preview',dict(stage_job_id=staged['id']),self.auth())
                self.assertEqual(200,status);self.assertFalse(blocked['eligible'])
                self.assertEqual(before_calls,calls)
                app.registry.set_project_policy('test',model_egress=True)
            if sequence:
                from governor_workbench.sequence_store import SequenceJournal
                status,preview,_=self.request('POST','/api/sequences/preview',dict(stage_job_id=staged['id']),self.auth())
                self.assertTrue(preview['eligible'],preview)
                body=dict(stage_job_id=staged['id'],binding_hash=preview['binding_hash'],note='Explicit bounded sequence')
                status,value,_=self.request('POST','/api/sequences/start',body,self.auth())
                self.assertEqual(202,status,value);key=value['sequence']['id']
                # This sequence owns two serial jobs, each with its own bounded test wait.
                row=self.wait_terminal(lambda:SequenceJournal(app.store).get(key),('testing','assessing'),timeout=120)
                self.assertEqual('awaiting_transfer_decision',row['status'],row)
                self.assertEqual(2,len(row['children']))
                tested=app.store.job(row['children'][0]['job_id'])
                assessed=app.store.job(row['children'][1]['job_id'])
                self.assertTrue(assessed['result']['pilot_assessment']['evidence_usable'])
                self.assertFalse(any(j['action'].startswith('pilot_') and j['action']!='pilot_assess' for j in app.store.jobs()))
                before=app.store.jobs();before_calls=list(calls)
                status,retry,_=self.request('POST','/api/sequences/start',body,self.auth())
                self.assertEqual(key,retry['sequence']['id']);self.assertEqual(before,app.store.jobs());self.assertEqual(before_calls,calls)
                status,state,_=self.request('GET','/api/state')
                self.assertEqual(key,state['sequences'][0]['id'])
            else:
                status,value,_=self.request('POST','/api/actions',dict(action='stage_test',stage_job_id=staged['id']),self.auth())
                self.assertEqual(202,status,value)
                tested=wait(value['job']['id'])
        if cancel_after_tests:
            self.assertEqual('cancelled',tested['status'],tested)
            self.assertEqual(1,tested['result']['count'])
            self.assertTrue(tested['result']['completion_verified'])
            self.assertFalse(tested['result']['verified'])
            return
        self.assertEqual('completed',tested['status'],tested)
        self.assertTrue(tested['result']['verified'])
        self.assertEqual(1,tested['result']['count'])
        self.assertEqual((['gpt-5.6-terra','gpt-5.6-sol'] if repair else [])+['gpt-5.6-terra','gpt-5.6-sol','gpt-5.6-sol'],calls)
        self.assertEqual('def value(): return 1\n',(repo/'calc.py').read_text())
        self.assertFalse(tested['result']['apply_back_enabled'])
        if apply_back:
            forbidden=self.auth(); forbidden['Origin']='https://evil.example'
            status,_,_=self.request('POST','/api/pilot/prepare',dict(verified_test_job_id=tested['id']),forbidden)
            self.assertEqual(403,status)
            status,value,_=self.request('POST','/api/pilot/prepare',dict(verified_test_job_id=tested['id']),self.auth())
            self.assertEqual(202,status,value)
            prepared=wait(value['job']['id']); self.assertEqual('completed',prepared['status'],prepared)
            approval=prepared['result']['apply_proposal']
            self.assertFalse(approval['approval_granted'])
            self.assertEqual('def value(): return 1\n',(repo/'calc.py').read_text())
            status,value,_=self.request('POST','/api/pilot/apply',dict(proposal_id=approval['id'],proposal_hash='0'*64),self.auth())
            self.assertEqual(202,status,value); rejected=wait(value['job']['id'])
            self.assertEqual('failed',rejected['status'],rejected)
            self.assertEqual('def value(): return 1\n',(repo/'calc.py').read_text())
            status,value,_=self.request('POST','/api/pilot/apply',dict(proposal_id=approval['id'],proposal_hash=approval['proposal_hash']),self.auth())
            self.assertEqual(202,status,value); applied=wait(value['job']['id'])
            self.assertEqual('completed',applied['status'],applied)
            tx=applied['result']['pilot_transaction']; self.assertEqual('completed',tx['status'])
            self.assertEqual('def value(): return 2\n',(repo/'calc.py').read_text())
            self.assertEqual(test_content,(repo/'tests/test_calc.py').read_text())
            refreshed=app.scope_context('project','test',False,force=True)
            Intake(app.store).accept(refreshed,refreshed['scope_hash'],'test',dict(requirements='Return two',test_strategy='unittest',dependencies='None',open_evidence='Pilot only'))
            status,value,_=self.request('POST','/api/pilot/verify',dict(transaction_id=tx['id']),self.auth())
            self.assertEqual(202,status,value); checked=wait(value['job']['id'])
            self.assertEqual('completed',checked['status'],checked)
            report=checked['result']['post_apply_verification']
            self.assertTrue(report['evidence_usable'],report)
            self.assertFalse(report['step_completion_granted'])
            self.assertFalse(report['target_tests_executed'])
            completion_body=dict(verified_job_id=checked['id'],observed_scope_hash=report['observed_scope_hash'],note='Nachher-Stand im Test bestätigt.')
            forbidden=self.auth(); forbidden['Origin']='https://evil.example'
            self.assertEqual(403,self.request('POST','/api/pilot/complete',completion_body,forbidden)[0])
            self.assertEqual(400,self.request('POST','/api/pilot/complete',{**completion_body,'command':'bad'},self.auth())[0])
            self.assertEqual(400,self.request('POST','/api/pilot/complete',{**completion_body,'note':''},self.auth())[0])
            status,value,_=self.request('POST','/api/pilot/complete',completion_body,self.auth())
            self.assertEqual(202,status,value); completed=wait(value['job']['id'])
            self.assertEqual('completed',completed['status'],completed)
            receipt=completed['result']['technical_completion']
            self.assertEqual(tx['id'],receipt['transaction_id'])
            self.assertFalse(receipt['plan_rebased'])
            self.assertFalse(receipt['execution_enabled'])
            transition_body=dict(technical_receipt_id=receipt['id'],observed_scope_hash=report['observed_scope_hash'],selection_id=report['selection_id'],note='Quellenübergang geprüft.')
            self.assertEqual(403,self.request('POST','/api/pilot/transition',transition_body,forbidden)[0])
            self.assertEqual(400,self.request('POST','/api/pilot/transition',{**transition_body,'command':'bad'},self.auth())[0])
            status,value,_=self.request('POST','/api/pilot/transition',transition_body,self.auth())
            self.assertEqual(202,status,value); changed=wait(value['job']['id'])
            self.assertEqual('completed',changed['status'],changed)
            chain_body=dict(scope_kind='project',scope_id='test',candidate_id=candidate['id'])
            status,value,_=self.request('POST','/api/plans/dependencies',chain_body,self.auth())
            self.assertEqual(200,status,value); chain=value['report']
            self.assertTrue(chain['current']); self.assertEqual('accepted',chain['steps'][0]['completion_status'])
            self.assertTrue(chain['steps'][1]['test_run_available'])
            status,value,_=self.request('POST','/api/plans/test',dict(candidate_id=candidate['id'],step_id='check',scope_hash=chain['scope_hash'],selection_id=chain['selection_id']),self.auth())
            self.assertEqual(202,status,value); follow_test=wait(value['job']['id'])
            self.assertEqual('completed',follow_test['status'],follow_test)
            self.assertTrue(follow_test['result']['success'],follow_test)
            status,value,_=self.request('POST','/api/plans/complete-step',{**chain_body,'step_id':'review','scope_hash':chain['scope_hash'],'selection_id':chain['selection_id'],'note':'Folgekette geprüft.'},self.auth())
            self.assertEqual(201,status,value)
            status,value,_=self.request('POST','/api/pilot/rollback',dict(transaction_id=tx['id']),self.auth())
            self.assertEqual(202,status,value); restored=wait(value['job']['id'])
            self.assertEqual('completed',restored['status'],restored)
            self.assertEqual('rolled_back',restored['result']['pilot_transaction']['status'])
            status,value,_=self.request('POST','/api/plans/dependencies',chain_body,self.auth())
            self.assertFalse(value['report']['current'])
            self.assertEqual(['stale']*3,[r['completion_status'] for r in value['report']['steps']])
            self.assertEqual('def value(): return 1\n',(repo/'calc.py').read_text())
            status,value,_=self.request('POST','/api/pilot/verify',dict(transaction_id=tx['id']),self.auth())
            self.assertEqual(202,status,value); checked=wait(value['job']['id'])
            self.assertFalse(checked['result']['post_apply_verification']['evidence_usable'])
            self.assertEqual('stale',checked['result']['post_apply_verification']['technical_completion']['status'])
        app.scope_cache.clear()
        displayed=next(j for j in app.state()['jobs'] if j['id']==tested['id'])['result']
        self.assertTrue(displayed['historical_verified'])
        self.assertFalse(displayed['verified'])
        self.assertTrue(displayed['stale'])
        self.assertTrue(app.store.job(tested['id'])['result']['verified'])

    def test_forged_host_denied(self):
        status,_,_=self.request('GET','/api/state',headers={'Host':'evil.example'})
        self.assertEqual(403,status)

    def test_memory_save_and_conflict(self):
        status,value,_=self.request('GET','/api/memory?project=test&name=note.md',headers={'Cookie':self.cookie})
        self.assertEqual(200,status)
        payload={'project':'test','name':'note.md','expected_sha256':value['sha256'],'content':'new'}
        status,_,_=self.request('POST','/api/memory',payload,self.auth()); self.assertEqual(200,status)
        status,_,_=self.request('POST','/api/memory',payload,self.auth()); self.assertEqual(409,status)

    def test_unknown_shell_action_rejected(self):
        status,_,_=self.request('POST','/api/actions',{'action':'shell','command':'echo x'},self.auth())
        self.assertEqual(400,status)

    def test_planned_project_and_supervisor_setting(self):
        status,p,_=self.request('POST','/api/projects',{'name':'Future','description':'future requirement','depends_on':['test']},self.auth())
        self.assertEqual(201,status); self.assertEqual('planned',p['project']['kind'])
        status,p,_=self.request('POST','/api/settings',{'supervisor':'gpt-6-astra'},self.auth())
        self.assertEqual(200,status); self.assertEqual('gpt-6-astra',p['supervisor'])

    def test_governance_decisions_and_stale_acceptance(self):
        self.server.app.refresh(force_git=True)
        status,state,_=self.request('GET','/api/state')
        self.assertIn('governor',state)
        payload={'step_id':'reconcile_sources','kind':'authorize','reason':'Explicit local review','evidence_hash':state['evidence_hash']}
        status,value,_=self.request('POST','/api/decisions',payload,self.auth())
        self.assertEqual(201,status)
        status,new,_=self.request('GET','/api/state')
        self.assertEqual(state['evidence_hash'],new['evidence_hash'])
        self.assertNotEqual(state['decision_hash'],new['decision_hash'])
        payload.update(kind='accept',evidence_hash='old')
        status,value,_=self.request('POST','/api/decisions',payload,self.auth())
        self.assertEqual(409,status)

    def test_report_requires_authorized_step(self):
        self.server.app.refresh(force_git=True)
        status,value,_=self.request('POST','/api/actions',{'action':'governance_report','step_id':'reconcile_sources'},self.auth())
        self.assertEqual(400,status)

    def test_review_request_authority_is_explicit(self):
        observation=self.server.app.refresh(force_git=True)
        context=self.server.app.review_context(observation)
        self.assertTrue(context['current_request']['authorized'])
        self.assertFalse(context['current_request']['product_implementation_authorized'])
        self.assertIn('steps',context['governor_matrix'])

    def test_authorized_report_records_hash_without_accepting_gate(self):
        import time
        self.server.app.refresh(force_git=True)
        status,value,_=self.request('POST','/api/decisions',{'step_id':'reconcile_sources','kind':'authorize','reason':'Read sources'},self.auth())
        self.assertEqual(201,status)
        status,value,_=self.request('POST','/api/actions',{'action':'governance_report','step_id':'reconcile_sources'},self.auth())
        self.assertEqual(202,status)
        key=value['job']['id']
        job=self.wait_terminal(lambda:self.server.app.store.job(key),('queued','running'))
        self.assertEqual('completed',job['status'],job)
        self.assertTrue(Path(job['result']['report']).is_file())
        self.assertFalse(job['result']['approval_granted'])
        matrix=self.server.app.governance()
        self.assertFalse(next(s for s in matrix['steps'] if s['id']=='reconcile_sources')['accepted'])

    def test_automatic_review_only_changed_complete_evidence_and_budget(self):
        from unittest.mock import patch
        app=self.server.app
        app.store.set_setting('monitor_enabled',False)
        app.store.set_setting('auto_review',True)
        app.store.set_setting('_last_auto_evidence','old')
        with patch.object(app.runner,'submit') as submit:
            app.auto_review({'evidence_hash':'new','evidence_complete':False})
            submit.assert_not_called()
            app.auto_review({'evidence_hash':'new','evidence_complete':True})
            submit.assert_called_once_with('hybrid_review')
            app.auto_review({'evidence_hash':'newer','evidence_complete':True})
            submit.assert_called_once()
            self.assertEqual(1,app.store.settings()['_auto_count'])

    def test_enabling_auto_review_baselines_current_decisions(self):
        from unittest.mock import patch
        app=self.server.app
        app.store.set_setting('monitor_enabled',False)
        observation=app.refresh(force_git=True)
        app.update_settings({'auto_review':True})
        with patch.object(app.runner,'submit') as submit:
            app.auto_review(observation)
            submit.assert_not_called()
            app.store.add_decision({'step_id':'reconcile_sources','kind':'authorize','reason':'Current scope','actor':'operator','evidence_hash':observation['evidence_hash']})
            app.auto_review(observation)
            submit.assert_called_once_with('hybrid_review')


class ServerCleanupTests(unittest.TestCase):
    def test_cleanup_waits_for_background_threads_before_directory_removal(self):
        from types import SimpleNamespace
        release=threading.Event()
        def background():
            release.wait()
            threading.Event().wait(.15)
        workers=[threading.Thread(target=background) for _ in range(2)]
        self.thread=threading.Thread(target=lambda:None);self.thread.start()
        self.server=SimpleNamespace(shutdown=lambda:None,server_close=lambda:None,
            app=SimpleNamespace(close=release.set,monitor_thread=workers[0],
                                runner=SimpleNamespace(thread=workers[1])))
        for worker in workers:worker.start()
        try:
            ServerTests.cleanup(self)
            self.assertFalse(any(worker.is_alive() for worker in workers),
                             'Temporary-directory cleanup must not race background owners')
        finally:
            release.set()
            for worker in workers:worker.join(2)


if __name__=='__main__': unittest.main()
