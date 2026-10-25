import copy
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


class ExecutionPolicyTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name).resolve(); self.project=self.root/'pilot'; self.project.mkdir()
        self.config={'staging_pilot_roots':[str(self.project)]}
        self.context={'plan_ready':True,'scope_hash':'a'*64,
                      'review_scope':{'kind':'project','id':'pilot'},
                      'registry_projects':[{'id':'pilot','path':str(self.project),'group_id':None}]}
        self.step={'id':'fix','title':'Fix isolated fixture','project_id':'pilot','priority':1,
                   'depends_on':[],'rationale':'Pilot validation','scope':['main.py'],
                   'tests':['Run fixture tests'],'action':'change'}
        self.candidate={'scope_kind':'project','scope_id':'pilot','scope_hash':'a'*64,
                        'proposal':{'summary':'Isolated pilot','steps':[self.step]}}
        self.permission={'plan_selection_approved':True,'execution_enabled':False}

    def check(self):
        from governor_workbench.execution_policy import require_staging_pilot
        return require_staging_pilot(self.config,self.context,self.candidate,'fix',self.permission)

    def test_explicit_isolated_independent_pilot_is_allowed_without_mutation(self):
        before=copy.deepcopy((self.config,self.context,self.candidate,self.permission))
        result=self.check()
        self.assertEqual(result,self.step)
        result['title']='Returned copy changed'
        self.assertEqual((self.config,self.context,self.candidate,self.permission),before)

    def test_missing_empty_or_unmatched_policy_is_denied(self):
        for config in ({},{'staging_pilot_roots':[]},{'staging_pilot_roots':str(self.project)},
                       {'staging_pilot_roots':[str(self.root)]}):
            self.config=config
            with self.subTest(config=config),self.assertRaises(ValueError): self.check()

    def test_selection_readiness_and_change_action_are_required(self):
        for mutate in (lambda:self.permission.update(plan_selection_approved=False),
                       lambda:self.permission.update(plan_selection_approved='true'),
                       lambda:self.context.update(plan_ready=False),
                       lambda:self.step.update(action='review')):
            self.setUp(); mutate()
            with self.assertRaises(ValueError): self.check()

    def test_dependency_execution_is_unavailable(self):
        self.step['depends_on']=['previous']
        previous={**copy.deepcopy(self.step),'id':'previous','depends_on':[]}
        self.candidate['proposal']['steps'].insert(0,previous)
        with self.assertRaisesRegex(ValueError,'Voraussetzung|Abhängigkeit'): self.check()

    def test_grouped_and_legacy_projects_remain_denied_even_when_allowlisted(self):
        self.context['registry_projects'][0]['group_id']='matrix'
        with self.assertRaises(ValueError): self.check()
        self.context['registry_projects'][0]['group_id']=None
        for project_id in ('aurelia','radiworks','modul_templates','radi144','morphic_v1'):
            self.context['registry_projects'][0]['id']=project_id
            self.context['review_scope']['id']=project_id
            self.candidate['scope_id']=project_id
            self.step['project_id']=project_id
            with self.subTest(project_id=project_id),self.assertRaises(ValueError): self.check()

    def test_canonical_path_and_existing_root_are_required(self):
        self.context['registry_projects'][0]['path']=str(self.project/'..'/'pilot')
        with self.assertRaises(ValueError): self.check()
        self.context['registry_projects'][0]['path']=str(self.root/'missing')
        self.config['staging_pilot_roots']=[str(self.root/'missing')]
        with self.assertRaises(ValueError): self.check()

    def test_redirected_root_is_denied(self):
        alias=self.root/'alias'
        try: alias.symlink_to(self.project,target_is_directory=True)
        except OSError: self.skipTest('Host cannot create directory symlinks')
        self.config['staging_pilot_roots']=[str(alias)]
        self.context['registry_projects'][0]['path']=str(alias)
        with self.assertRaises(ValueError): self.check()

    def test_stale_and_wrong_scope_candidate_are_denied(self):
        self.candidate['scope_hash']='b'*64
        with self.assertRaises(ValueError): self.check()
        self.candidate['scope_hash']='a'*64
        self.candidate['scope_id']='other'
        with self.assertRaises(ValueError): self.check()

    @unittest.skipUnless(os.name == 'nt', 'Windows junction check')
    def test_windows_junction_pilot_is_denied(self):
        alias=self.root/'junction'
        subprocess.run(['cmd.exe','/d','/c','mklink','/J',str(alias),str(self.project)],
                       check=True,capture_output=True,
                       creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        self.config['staging_pilot_roots']=[str(alias)]
        self.context['registry_projects'][0]['path']=str(alias)
        with self.assertRaises(ValueError): self.check()

    def test_controller_model_authority_is_exactly_scoped_and_does_not_mutate_inputs(self):
        from governor_workbench.execution_policy import pilot_model_context
        self.candidate['id']='candidate_fixture'
        self.context['current_request']={'authorized':True,'scope':'read_only_advisory'}
        before=copy.deepcopy((self.context,self.candidate,self.step))
        validated=self.check()
        for phase in ('patch_preflight','post_test_review'):
            value=pilot_model_context(self.context,self.candidate,validated,phase)
            request=value['current_request']
            self.assertEqual(request['phase'],phase)
            self.assertEqual(request['project_id'],'pilot')
            self.assertEqual(request['candidate_id'],'candidate_fixture')
            self.assertEqual(request['step_id'],'fix')
            self.assertEqual(request['source_scope_hash'],self.context['scope_hash'])
            self.assertEqual(request['allowed_paths'],['main.py'])
            for field in ('staging_copy_authorized','restricted_staged_unittest_authorized',
                          'plan_selection_verified','pilot_allowlist_verified'):
                self.assertIs(request[field],True)
            for field in ('original_file_changes_authorized','product_implementation_authorized',
                          'apply_back_authorized','automatic_sequence_authorized'):
                self.assertIs(request[field],False)
            request['allowed_paths'].append('foreign.py')
        self.assertEqual((self.context,self.candidate,self.step),before)
        with self.assertRaises(ValueError): pilot_model_context(self.context,self.candidate,validated,'apply_back')
