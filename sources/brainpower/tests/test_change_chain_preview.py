import unittest
from unittest.mock import patch

from tests import test_plan_tests


class ChangeChainPreviewTests(unittest.TestCase):
    def setUp(self):
        test_plan_tests.PlanTestCompletionTests.setUp(self)
        (self.root/'a.py').write_text('a = 1\n')
        (self.root/'b.py').write_text('b = 1\n')
        template=self.candidate['proposal']['steps'][0]
        self.steps=[dict(template,id='a',action='change',scope=['a.py'],depends_on=[]),
                    dict(template,id='b',action='change',scope=['b.py'],depends_on=['a'])]
        self.save()

    def save(self):
        self.candidate=self.book.save_candidate(self.context,dict(summary='Two changes',steps=self.steps),
            dict(summary='Clean',decision='REVIEW_ONLY',findings=[],required_evidence=[]),'fixture')
        self.selection=self.book.approve(self.candidate['id'],'a'*64,self.context,[s['id'] for s in self.steps],'sequence')

    def preview(self,ids=None):
        from governor_workbench.change_chain_preview import preview
        return preview(self.app,self.candidate['id'],['b','a'] if ids is None else ids)

    def test_canonical_conditional_preview_without_side_effects_or_permission(self):
        with self.store.db() as db:before='\n'.join(db.iterdump())
        source=(self.root/'a.py').read_bytes()
        with patch('governor_workbench.jobs.RouterClient') as client:
            value=self.preview();again=self.preview(['a','b']);client.assert_not_called()
        self.assertTrue(value['eligible'],value)
        self.assertEqual(value['binding_hash'],again['binding_hash'])
        self.assertEqual(['a','b'],value['binding']['step_ids'])
        self.assertEqual(['prerequisites_observed','conditional'],[s['readiness'] for s in value['steps']])
        self.assertEqual(['a'],value['steps'][1]['waiting_for'])
        for name in ('execution_authorized','model_transmission_required','creates_jobs_or_receipts'):
            self.assertIs(False,value[name])
        with self.store.db() as db:self.assertEqual(before,'\n'.join(db.iterdump()))
        self.assertEqual(source,(self.root/'a.py').read_bytes())
        from governor_workbench.execution_policy import require_staging_pilot
        with self.assertRaises(ValueError):
            require_staging_pilot(self.config,self.context,self.candidate,'b',{'plan_selection_approved':True})

    def test_invalid_requests_and_parallel_changes_block(self):
        for ids in (None,'ab',[],['a'],['a','a'],['a','b','c'],['a','unknown'],[{},'b']):
            if ids is None:continue
            self.assertFalse(self.preview(ids)['eligible'],ids)
        self.steps[1]['depends_on']=[];self.save()
        self.assertEqual('chain_shape',self.preview()['reason_code'])

    def test_overlap_case_alias_and_ancestor_path_block(self):
        for path in ('a.py','A.py','a.py/child.py'):
            self.steps[1]['scope']=[path];self.save()
            self.assertEqual('overlapping_scope',self.preview()['reason_code'])

    def test_external_predecessor_requires_current_receipt(self):
        before=dict(self.steps[0],id='before',action='review')
        self.steps.insert(0,before);self.steps[2]['depends_on']=['a','before'];self.save()
        self.assertEqual('missing_predecessor',self.preview()['reason_code'])
        receipt=self.book.complete_step(self.candidate['id'],'before',self.context,'a'*64,self.selection['id'],'Reviewed')
        self.assertTrue(self.preview()['eligible'])
        self.book.withdraw_completion(self.candidate['id'],'before',receipt['id'],'Withdrawn')
        self.assertEqual('missing_predecessor',self.preview()['reason_code'])

    def test_source_and_selection_and_adapter_bound(self):
        original=self.preview()['binding_hash']
        (self.root/'a.py').write_text('a = 2\n')
        self.assertNotEqual(original,self.preview()['binding_hash'])
        original=self.preview()['binding_hash']
        self.book.approve(self.candidate['id'],'a'*64,self.context,['a','b'],'sequence')
        self.assertNotEqual(original,self.preview()['binding_hash'])
        original=self.preview()['binding_hash']
        with patch('governor_workbench.change_chain_preview.adapter_identity',return_value={'changed':True}):
            self.assertNotEqual(original,self.preview()['binding_hash'])

    def test_new_file_absence_is_explicitly_bound(self):
        (self.root/'b.py').unlink();value=self.preview()
        self.assertTrue(value['eligible'],value)
        self.assertIsNone(value['binding']['sources']['b.py'])
        (self.root/'b.py').write_text('new')
        self.assertNotEqual(value['binding_hash'],self.preview()['binding_hash'])

    def test_root_and_registry_restrictions(self):
        self.config['staging_pilot_roots']=[]
        self.assertEqual('pilot_scope',self.preview()['reason_code'])
        self.config['staging_pilot_roots']=[str(self.root)]
        for field,value in (('archived',True),('group_id','group')):
            old=self.context['registry_projects'][0][field]
            self.context['registry_projects'][0][field]=value
            self.assertEqual('pilot_scope',self.preview()['reason_code'])
            self.context['registry_projects'][0][field]=old

    def test_mid_observation_drift_and_sanitized_io_error(self):
        original=self.app.scope_context;calls=[]
        def context(*args,**kw):
            calls.append(kw)
            if len(calls)==2:(self.root/'a.py').write_text('drift')
            return original(*args,**kw)
        self.app.scope_context=context
        self.assertEqual('observation_drift',self.preview()['reason_code'])
        self.assertTrue(all(c==dict(require_egress=False,force=True) for c in calls))
        with patch('governor_workbench.change_chain_preview._read',side_effect=OSError('PRIVATE')):
            value=self.preview();self.assertFalse(value['eligible']);self.assertNotIn('PRIVATE',str(value))

    def test_stale_plan_and_unselected_step_block(self):
        self.book.approve(self.candidate['id'],'a'*64,self.context,['a'],'single')
        self.assertEqual('selection',self.preview()['reason_code'])
        self.context['scope_hash']='b'*64
        self.assertEqual('stale_plan',self.preview()['reason_code'])

    def test_empty_journal_not_initialized(self):
        from governor_workbench.store import Store
        self.app.store=Store(self.root.parent/'empty.db')
        with self.app.store.db() as db:before='\n'.join(db.iterdump())
        self.assertEqual('missing_plan',self.preview()['reason_code'])
        with self.app.store.db() as db:self.assertEqual(before,'\n'.join(db.iterdump()))

    def test_existing_transition_does_not_imply_historical_chain_support(self):
        original=self.book.dependency_report(self.candidate['id'],self.context)
        original['source_transition']={'id':'historical'}
        with patch('governor_workbench.plans.PlanBook.dependency_report',return_value=original):
            self.assertEqual('transition_pending',self.preview()['reason_code'])

    def test_intermediate_dependency_and_duplicate_paths_block(self):
        review=dict(self.steps[0],id='review',action='review',depends_on=['a'])
        self.steps.insert(1,review);self.steps[2]['depends_on']=['a','review'];self.save()
        self.assertEqual('chain_shape',self.preview()['reason_code'])
        self.steps.pop(1);self.steps[1]['depends_on']=['a'];self.steps[0]['scope']=['a.py','A.py'];self.save()
        self.assertEqual('overlapping_scope',self.preview()['reason_code'])

    def test_source_size_and_nonregular_files_block(self):
        (self.root/'a.py').write_bytes(b'a'*(256*1024+1))
        self.assertEqual('source_unreadable',self.preview()['reason_code'])
        (self.root/'a.py').unlink();(self.root/'a.py').mkdir()
        self.assertEqual('source_unreadable',self.preview()['reason_code'])

    def test_changed_root_identity_during_observation_blocks(self):
        from governor_workbench.execution_workspace import _root
        calls=[]
        def changed(value):
            root,identity=_root(value);calls.append(value)
            if len(calls)>2:identity=dict(identity,inode=identity['inode']+1)
            return root,identity
        with patch('governor_workbench.change_chain_preview._root',side_effect=changed):
            self.assertEqual('observation_drift',self.preview()['reason_code'])
