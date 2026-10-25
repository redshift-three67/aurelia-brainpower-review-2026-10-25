import copy
import tempfile
import threading
import unittest
from pathlib import Path
from types import SimpleNamespace

from governor_workbench import pilot_actions
from governor_workbench.execution_workspace import WorkspaceStager, _sha
from governor_workbench.jobs import JobCancelled
from governor_workbench.plans import PlanBook
from governor_workbench.store import Store


class PilotActionsTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        base=Path(self.temp.name).resolve(); self.root=base/'fixture'; self.root.mkdir()
        (self.root/'main.py').write_bytes(b'old WIP\r\n')
        self.store=Store(base/'data'/'journal.db')
        self.project=dict(id='pilot',path=str(self.root),group_id=None,archived=False)
        self.context=dict(plan_ready=True,scope_hash='a'*64,review_scope=dict(kind='project',id='pilot'),registry_projects=[self.project])
        self.calls=[]
        def context(kind,key,require_egress=True,force=True):
            self.calls.append((kind,key,require_egress,force)); return copy.deepcopy(self.context)
        self.app=SimpleNamespace(store=self.store,config=dict(data_dir=str(base/'data'),staging_pilot_roots=[str(self.root)],projects=[]),
            scope_context=context,registry=SimpleNamespace(list_projects=lambda:[copy.deepcopy(self.project)]))
        self.book=PlanBook(self.store)
        self.step=dict(id='fix',title='Fix fixture',project_id='pilot',priority=1,depends_on=[],rationale='Check pilot',
                       scope=['main.py'],tests=['unittest'],action='change')
        self.review=dict(summary='Checked',decision='REVIEW_ONLY',findings=[],required_evidence=[])
        self.candidate=self.book.save_candidate(self.context,dict(summary='Fixture',steps=[self.step]),self.review,'f'*32)
        self.book.approve(self.candidate['id'],'a'*64,self.context,['fix'])
        stage=WorkspaceStager(base/'data').stage(str(self.root),['main.py'],[dict(path='main.py',content='new\n')],{'main.py':_sha(b'old WIP\r\n')})
        self.source=self.store.create_job('scope_patch',None,dict(scope_kind='project',scope_id='pilot',scope_hash='a'*64,candidate_id=self.candidate['id'],step_id='fix'))
        self.store.update_job(self.source['id'],status='completed',result=dict(stage=stage,scope_hash='a'*64))
        self.test=self.store.create_job('stage_test',None,dict(stage_job_id=self.source['id']))
        self.result=dict(stage_id=stage['id'],manifest_hash=stage['manifest_hash'],stage_job_id=self.source['id'],scope_hash='a'*64,
            completion_verified=True,sources_verified=True,verified=True,success=True,stale=False,exit_code=0,count=1,skipped=0,errors=0,failures=0,
            post_test_review=dict(verified=True,review=self.review))
        from governor_workbench.staged_tests import adapter_identity
        identity=adapter_identity()
        self.result.update(adapter_verified=True,adapter_before=identity,adapter_after=identity)
        self.result['plan_selection_id']=self.book.execution_permission(self.candidate['id'],'fix',self.context).get('plan_selection_id')
        self.store.update_job(self.test['id'],status='completed',result=self.result)

    def prepare(self): return pilot_actions.prepare(self.app,self.test['id'])
    def execute(self,p,cancel=None): return pilot_actions.execute(self.app,p['id'],p['proposal_hash'],cancel)

    def test_missing_adapter_evidence_blocks_preparation(self):
        result={k:v for k,v in self.result.items() if not k.startswith('adapter_')}
        self.store.update_job(self.test['id'],result=result)
        with self.assertRaisesRegex(ValueError,'Adapter'): self.prepare()

    def test_reselection_invalidates_previous_test_before_apply(self):
        p=self.prepare()
        self.book.approve(self.candidate['id'],'a'*64,self.context,['fix'])
        with self.assertRaisesRegex(ValueError,'Planauswahl'): self.execute(p)
        self.assertEqual(b'old WIP\r\n',(self.root/'main.py').read_bytes())

    def test_missing_selection_proof_requires_retest(self):
        result={k:v for k,v in self.result.items() if k!='plan_selection_id'}
        self.store.update_job(self.test['id'],result=result)
        with self.assertRaisesRegex(ValueError,'Planauswahl'): self.prepare()

    def test_assessment_reports_checks_without_creating_proposal(self):
        report=pilot_actions.assess(self.app,self.test['id'])
        self.assertTrue(report['evidence_usable'])
        self.assertFalse(report['approval_granted'])
        self.assertEqual(['passed']*3,[c['status'] for c in report['checks']])
        self.assertEqual(b'old WIP\r\n',(self.root/'main.py').read_bytes())
        with self.store.db() as db:
            self.assertIsNone(db.execute("SELECT name FROM sqlite_master WHERE name='pilot_apply_proposals'").fetchone())

    def test_assessment_explains_block_and_does_not_claim_remaining_checks(self):
        self.store.update_job(self.test['id'],result={**self.result,'adapter_verified':False})
        report=pilot_actions.assess(self.app,self.test['id'])
        self.assertFalse(report['evidence_usable'])
        self.assertEqual(['blocked','not_checked','not_checked'],[c['status'] for c in report['checks']])
        self.assertIn('Adapter',report['checks'][0]['reason'])

    def test_assessment_detects_file_drift(self):
        (self.root/'main.py').write_bytes(b'changed after test')
        report=pilot_actions.assess(self.app,self.test['id'])
        self.assertFalse(report['evidence_usable'])
        self.assertEqual('blocked',report['checks'][-1]['status'])

    def test_newer_attempt_invalidates_old_success_for_every_status(self):
        p=self.prepare()
        newer=self.store.create_job('stage_test',None,{'stage_job_id':self.source['id']})
        for status in ('queued','running','failed','cancelled','interrupted','completed'):
            self.store.update_job(newer['id'],status=status,result=self.result)
            with self.subTest(status=status):
                with self.assertRaisesRegex(ValueError,'neuerer'): self.prepare()
                with self.assertRaisesRegex(ValueError,'neuerer'): self.execute(p)
                self.assertEqual(b'old WIP\r\n',(self.root/'main.py').read_bytes())

    def test_newest_success_can_prepare_and_unrelated_attempt_does_not_supersede(self):
        other=self.store.create_job('stage_test',None,{'stage_job_id':'b'*32})
        self.store.update_job(other['id'],status='failed')
        self.prepare()
        newest=self.store.create_job('stage_test',None,{'stage_job_id':self.source['id']})
        self.store.update_job(newest['id'],status='completed',result=self.result)
        p=pilot_actions.prepare(self.app,newest['id'])
        self.assertEqual(newest['id'],p['verified_test_job_id'])

    def test_adapter_change_after_proposal_blocks_writes(self):
        from unittest.mock import patch
        p=self.prepare()
        with patch('governor_workbench.staged_tests.adapter_identity',return_value={'hash':'changed'}):
            with self.assertRaisesRegex(ValueError,'Adapter'): self.execute(p)
        self.assertEqual(b'old WIP\r\n',(self.root/'main.py').read_bytes())

    def test_adapter_proof_requires_exact_types_and_both_observations(self):
        for field in ('adapter_before','adapter_after'):
            changed=copy.deepcopy(self.result)
            changed[field]['schema_version']=True
            self.store.update_job(self.test['id'],result=changed)
            with self.subTest(field=field), self.assertRaisesRegex(ValueError,'Adapter'):
                self.prepare()

    def test_adapter_change_does_not_block_recovery(self):
        from unittest.mock import patch
        tx=self.execute(self.prepare())
        with patch('governor_workbench.staged_tests.adapter_identity',side_effect=AssertionError('rollback must not need test adapter')):
            pilot_actions.rollback(self.app,tx['id'],None)
        self.assertEqual(b'old WIP\r\n',(self.root/'main.py').read_bytes())

    def test_apply_and_rollback_after_scope_becomes_stale(self):
        p=self.prepare(); tx=self.execute(p)
        self.assertEqual('completed',tx['status'])
        self.context.update(scope_hash='b'*64,plan_ready=False)
        pilot_actions.rollback(self.app,tx['id'],None)
        self.assertEqual(b'old WIP\r\n',(self.root/'main.py').read_bytes())
        self.assertTrue(all(call[2:] == (False,True) for call in self.calls))

    def test_cancel_before_writes(self):
        p=self.prepare(); cancel=threading.Event(); cancel.set()
        with self.assertRaises(JobCancelled): self.execute(p,cancel)
        self.assertEqual(b'old WIP\r\n',(self.root/'main.py').read_bytes())

    def test_changed_scope_revision_hash_or_eligibility_rejected(self):
        p=self.prepare()
        with self.assertRaises(ValueError): pilot_actions.execute(self.app,p['id'],'0'*64,None)
        self.context['scope_hash']='b'*64
        with self.assertRaises(ValueError): self.execute(p)
        self.context['scope_hash']='a'*64; self.project['group_id']='group'
        with self.assertRaises(ValueError): self.execute(p)
        self.project['group_id']=None
        self.book.save_candidate(self.context,dict(summary='New revision',steps=[self.step]),self.review,'e'*32)
        with self.assertRaises(ValueError): self.execute(p)

    def test_false_count_or_review_cannot_hide_behind_verified_flag(self):
        for change in [dict(count=0),dict(skipped=1),dict(exit_code=True),dict(completion_verified=False),
                       dict(post_test_review=dict(verified=True,review={**self.review,'decision':'BLOCK'}))]:
            self.store.update_job(self.test['id'],result={**self.result,**change})
            with self.subTest(change=change),self.assertRaises(ValueError): self.prepare()

    def test_registry_path_must_equal_staged_original(self):
        other=self.root.parent/'other'; other.mkdir()
        self.app.config['staging_pilot_roots'].append(str(other))
        self.project['path']=str(other)
        with self.assertRaises(ValueError): self.prepare()

    def test_rollback_rejects_changed_registry_membership(self):
        tx=self.execute(self.prepare()); self.project['group_id']='group'
        with self.assertRaises(ValueError): pilot_actions.rollback(self.app,tx['id'],None)
        self.assertEqual(b'new\n',(self.root/'main.py').read_bytes())

    def test_proposal_tamper_is_detected_by_content_hash(self):
        p=self.prepare(); p['diff']='different'
        import json
        with self.store.db() as db:
            db.execute('UPDATE pilot_apply_proposals SET body=? WHERE id=?',(json.dumps(p),p['id']))
        with self.assertRaises(ValueError): self.execute(p)

    def test_historical_root_overlap_is_rejected_under_new_id(self):
        self.app.config['projects']=[dict(id='radiworks',path=str(self.root))]
        with self.assertRaises(ValueError): self.prepare()

    def test_selected_step_scope_must_match_manifest(self):
        step={**self.step,'scope':['main.py','other.py']}
        candidate=self.book.save_candidate(self.context,dict(summary='Scope changed',steps=[step]),self.review,'d'*32)
        self.book.approve(candidate['id'],'a'*64,self.context,['fix'])
        import json
        request={**self.source['request'],'candidate_id':candidate['id']}
        with self.store.db() as db:
            db.execute('UPDATE jobs SET request=? WHERE id=?',(json.dumps(request),self.source['id']))
        with self.assertRaises(ValueError): self.prepare()

    def test_actual_runner_report_fields_are_accepted(self):
        from governor_workbench.staged_tests import run_staged_tests
        (self.root/'tests').mkdir()
        source='import unittest\nclass Check(unittest.TestCase):\n def test_ok(self): self.assertEqual(2,2)\n'
        (self.root/'tests/test_fixture.py').write_text(source)
        stager=WorkspaceStager(self.app.config['data_dir'])
        stage=stager.stage(str(self.root),['tests/test_fixture.py'],[dict(path='tests/test_fixture.py',content=source)],
            {'tests/test_fixture.py':_sha((self.root/'tests/test_fixture.py').read_bytes())})
        observed=run_staged_tests(stager,stage['id'],stage['manifest_hash'],threading.Event(),None)
        self.assertTrue(observed['completion_verified'])
        self.assertTrue(observed['sources_verified'])
        self.assertTrue(observed['success'])
        step={**self.step,'scope':['tests/test_fixture.py']}
        candidate=self.book.save_candidate(self.context,dict(summary='Actual runner check',steps=[step]),self.review,'c'*32)
        self.book.approve(candidate['id'],'a'*64,self.context,['fix'])
        import json
        request={**self.source['request'],'candidate_id':candidate['id']}
        with self.store.db() as db:
            db.execute('UPDATE jobs SET request=? WHERE id=?',(json.dumps(request),self.source['id']))
        self.store.update_job(self.source['id'],result=dict(stage=stage,scope_hash='a'*64))
        self.store.update_job(self.test['id'],result={**observed,'verified':True,'stale':False,'scope_hash':'a'*64,
            'stage_job_id':self.source['id'],'plan_selection_id':self.book.execution_permission(candidate['id'],'fix',self.context)['plan_selection_id'],
            'post_test_review':dict(verified=True,review=self.review)})
        self.assertEqual(stage['id'],self.prepare()['stage_id'])

    def test_recovery_receipt_preserves_unknown_file_state_and_transaction(self):
        from unittest.mock import patch
        from governor_workbench.pilot_apply import PilotApply
        p=self.prepare()
        original=PilotApply._replace
        def write_then_fail(pilot,root,path,data,expected):
            original(pilot,root,path,data,expected)
            (root/path).write_bytes(b'external during write')
            raise OSError('injected')
        with patch.object(PilotApply,'_replace',write_then_fail):
            with self.assertRaises(ValueError): self.execute(p)
        job=dict(action='pilot_apply',request=dict(proposal_id=p['id'],proposal_hash=p['proposal_hash']))
        result=pilot_actions.recovery_receipt(self.app,job)
        self.assertFalse(result['success'])
        self.assertIsNone(result['product_files_changed'])
        self.assertEqual('unknown_requires_inspection',result['file_state'])
        self.assertEqual('recovery_needed',result['pilot_transaction']['status'])
        self.assertEqual(b'external during write',(self.root/'main.py').read_bytes())
        rollback=dict(action='pilot_rollback',request=dict(transaction_id=result['pilot_transaction']['id']))
        self.assertEqual(result['pilot_transaction'],pilot_actions.recovery_receipt(self.app,rollback)['pilot_transaction'])

    def test_receipt_missing_reference_is_none_and_snapshot_initially_empty(self):
        self.assertEqual([],pilot_actions.transaction_snapshot(self.app))
        self.assertIsNone(pilot_actions.recovery_receipt(self.app,dict(action='pilot_apply',request={'proposal_id':'0'*32})))
        self.assertIsNone(pilot_actions.recovery_receipt(self.app,dict(action='pilot_prepare',request={})))
        p=self.prepare()
        self.assertIsNone(pilot_actions.recovery_receipt(self.app,dict(action='pilot_apply',request={'proposal_id':p['id']})))

    def test_snapshot_is_bounded_and_unresolved_precedes_recent_completed(self):
        import json
        self.prepare()
        with self.store.db() as db:
            for index in range(6):
                status='interrupted' if index==0 else 'completed'
                value=dict(id=str(index),stage_id='stage'+str(index),status=status,files=[])
                db.execute('INSERT INTO pilot_apply_transactions VALUES(?,?,?,?)',
                    (value['id'],value['stage_id'],status,json.dumps(value)))
        rows=pilot_actions.transaction_snapshot(self.app,limit=3)
        self.assertEqual(['0','5','4'],[row['id'] for row in rows])
        for limit in (0,101,True,'4'):
            with self.subTest(limit=limit),self.assertRaises(ValueError): pilot_actions.transaction_snapshot(self.app,limit)
