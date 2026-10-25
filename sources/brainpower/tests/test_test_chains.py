import copy
import unittest
from unittest.mock import patch

from tests import test_plan_tests


class TestChainPreviewTests(unittest.TestCase):
    def setUp(self):
        test_plan_tests.PlanTestCompletionTests.setUp(self)
        steps=copy.deepcopy(self.candidate['proposal']['steps'])
        steps[2].update(action='test',id='second')
        self.candidate=self.book.save_candidate(self.context,dict(summary='Chain',steps=steps),
            dict(summary='Clean',decision='REVIEW_ONLY',findings=[],required_evidence=[]),'fixture')
        self.selection=self.book.approve(self.candidate['id'],'a'*64,self.context,['before','test','second'],'sequence')
        self.before=self.book.complete_step(self.candidate['id'],'before',self.context,'a'*64,self.selection['id'],'Reviewed')

    def preview(self,ids=None):
        from governor_workbench.test_chains import preview
        return preview(self.app,self.candidate['id'],ids or ['second','test'])

    def test_stable_topological_preview_is_read_only_and_conditional(self):
        with self.store.db() as db:before='\n'.join(db.iterdump())
        source=(self.root/'tests/test_ok.py').read_bytes()
        with patch('governor_workbench.jobs.RouterClient') as client:
            first=self.preview();second=self.preview(['test','second'])
            client.assert_not_called()
        self.assertTrue(first['eligible'],first)
        self.assertEqual(first['binding_hash'],second['binding_hash'])
        self.assertEqual(['test','second'],first['binding']['step_ids'])
        self.assertEqual(['ready','conditional'],[r['readiness'] for r in first['steps']])
        self.assertFalse(first['execution_authorized']);self.assertFalse(first['model_transmission_required'])
        with self.store.db() as db:self.assertEqual(before,'\n'.join(db.iterdump()))
        self.assertEqual(source,(self.root/'tests/test_ok.py').read_bytes())

    def test_missing_external_predecessor_and_non_test_block(self):
        self.assertFalse(self.preview(['before','test'])['eligible'])
        self.book.withdraw_completion(self.candidate['id'],'before',self.before['id'],'Revoked')
        self.assertFalse(self.preview()['eligible'])

    def test_selection_and_bytes_change_binding(self):
        original=self.preview()['binding_hash']
        (self.root/'tests/test_ok.py').write_text('changed bytes')
        self.assertNotEqual(original,self.preview()['binding_hash'])
        first=self.preview()['binding_hash']
        self.book.approve(self.candidate['id'],'a'*64,self.context,['before','test','second'],'sequence')
        self.assertFalse(self.preview()['eligible'])
        self.book.complete_step(self.candidate['id'],'before',self.context,'a'*64,
            self.book.dependency_report(self.candidate['id'],self.context)['selection_id'],'Reviewed again')
        self.assertNotEqual(first,self.preview()['binding_hash'])

    def test_budget_and_new_attempt_change_or_block_preview(self):
        first=self.preview()['binding_hash']
        for number in range(3):
            job=self.store.create_job('plan_test',None,dict(candidate_id=self.candidate['id'],step_id='test'))
            self.store.update_job(job['id'],status='failed')
            result=self.preview()
            if number<2:self.assertTrue(result['eligible']);self.assertNotEqual(first,result['binding_hash'])
            else:self.assertFalse(result['eligible'])

    def test_bad_lists_scope_and_missing_files_fail_closed(self):
        for ids in (['test'],['test','test'],['test','missing'],['test']*6):
            self.assertFalse(self.preview(ids)['eligible'])
        self.config['staging_pilot_roots']=[]
        self.assertFalse(self.preview()['eligible'])
        self.config['staging_pilot_roots']=[str(self.root)]
        (self.root/'tests/test_ok.py').unlink()
        self.assertFalse(self.preview()['eligible'])

    def test_no_egress_required_and_mid_observation_drift_blocks(self):
        original=self.app.scope_context;calls=[]
        def context(*a,**kw):
            calls.append(kw)
            value=original(*a,**kw)
            if len(calls)>1:value['scope_hash']='b'*64
            return value
        self.app.scope_context=context
        self.assertFalse(self.preview()['eligible'])
        self.assertTrue(all(c['require_egress'] is False and c['force'] is True for c in calls))

    def test_adapter_drift_changes_binding_and_errors_are_sanitized(self):
        original=self.preview()['binding_hash']
        with patch('governor_workbench.test_chains.adapter_hash',return_value='b'*64):
            self.assertNotEqual(original,self.preview()['binding_hash'])
        with patch('governor_workbench.test_chains._read',side_effect=OSError('SECRET location')):
            value=self.preview();self.assertFalse(value['eligible']);self.assertNotIn('SECRET',str(value))

    def test_active_attempt_blocks_without_consuming_budget(self):
        self.store.create_job('plan_test',None,dict(candidate_id=self.candidate['id'],step_id='second'))
        before=self.store.jobs();self.assertFalse(self.preview()['eligible']);self.assertEqual(before,self.store.jobs())

    def test_branch_order_uses_plan_order_for_ties(self):
        steps=copy.deepcopy(self.candidate['proposal']['steps'])
        steps.insert(2,dict(steps[1],id='parallel'))
        steps[-1]['depends_on']=['test','parallel']
        self.candidate=self.book.save_candidate(self.context,dict(summary='Branch',steps=steps),
            dict(summary='Clean',decision='REVIEW_ONLY',findings=[],required_evidence=[]),'fixture')
        selection=self.book.approve(self.candidate['id'],'a'*64,self.context,['before','test','parallel','second'],'sequence')
        self.book.complete_step(self.candidate['id'],'before',self.context,'a'*64,selection['id'],'Reviewed')
        result=self.preview(['second','parallel','test'])
        self.assertTrue(result['eligible'],result)
        self.assertEqual(['test','parallel','second'],result['binding']['step_ids'])
        self.assertEqual(['ready','ready','conditional'],[r['readiness'] for r in result['steps']])
        self.assertEqual(['test','parallel'],result['steps'][-1]['waiting_for'])

    def test_already_completed_test_not_reproposed(self):
        test_plan_tests.PlanTestCompletionTests.run_test(self)
        self.assertFalse(self.preview()['eligible'])

    def test_grouped_or_archived_pilot_blocks(self):
        project=self.context['registry_projects'][0]
        project['archived']=True
        self.assertFalse(self.preview()['eligible'])
        project['archived']=False;project['group_id']='fixture-group'
        self.assertFalse(self.preview()['eligible'])

    def test_empty_journal_does_not_initialize_plan_schema(self):
        from governor_workbench.store import Store
        self.app.store=Store(self.root.parent/'empty.db')
        with self.app.store.db() as db:before='\n'.join(db.iterdump())
        self.assertFalse(self.preview()['eligible'])
        with self.app.store.db() as db:self.assertEqual(before,'\n'.join(db.iterdump()))
