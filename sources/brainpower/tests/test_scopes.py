import json
from pathlib import Path
import tempfile
import unittest
from governor_workbench.store import Store
from governor_workbench.registry import Registry


class ScopeTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name); self.store=Store(self.root/'journal.db')
        self.registry=Registry(self.store,[])
        self.config={'projects':[],'governor_dir':'','snapshot_dir':'','git_interval':60}

    def project(self,name,permission=True):
        root=self.root/name; (root/'project_memories').mkdir(parents=True)
        (root/'project_memories'/'strategy.md').write_text(name+' private requirements',encoding='utf-8')
        return self.registry.register(name,str(root),model_egress=permission,requirements=name+' target')

    def scope(self,kind,key):
        from governor_workbench.scopes import ScopeService
        return ScopeService(self.registry,self.config).context(kind,key)

    def test_single_excludes_other_projects_and_governance(self):
        a=self.project('alpha'); self.project('SECRET_BETA')
        context=self.scope('project',a['id'])
        self.assertNotIn('SECRET_BETA',json.dumps(context))
        self.assertEqual([],context['governance_sources'])
        self.assertEqual([a['id']],[p['id'] for p in context['projects']])

    def test_group_membership_roles_and_missing_member(self):
        a=self.project('alpha'); b=self.project('beta'); g=self.registry.create_group('Group')
        self.registry.assign(a['id'],g['id'],'parent'); self.registry.assign(b['id'],g['id'],'module')
        context=self.scope('group',g['id'])
        self.assertEqual(2,len(context['projects']))
        self.assertEqual('parent',next(p['role'] for p in context['registry_projects'] if p['id']==a['id']))
        self.registry.archive(b['id'])
        with self.assertRaisesRegex(ValueError,'archiviert'): self.scope('group',g['id'])

    def test_permission_is_required_for_every_member(self):
        a=self.project('alpha',False)
        with self.assertRaisesRegex(ValueError,'Modell'): self.scope('project',a['id'])

    def test_unrelated_changes_do_not_invalidate_scope(self):
        a=self.project('alpha'); b=self.project('beta')
        first=self.scope('project',a['id'])['scope_hash']
        (Path(b['path'])/'project_memories/strategy.md').write_text('changed beta')
        self.assertEqual(first,self.scope('project',a['id'])['scope_hash'])
        (Path(a['path'])/'project_memories/strategy.md').write_text('changed alpha')
        self.assertNotEqual(first,self.scope('project',a['id'])['scope_hash'])

    def test_group_member_project_review_excludes_central_documents(self):
        a=self.project('alpha'); g=self.registry.create_group('Other')
        # A selected member must not load the group's full central document set.
        self.registry.assign(a['id'],g['id'])
        from unittest.mock import patch
        from governor_workbench.scopes import ScopeService
        selected=self.registry.list_projects(); selected[0]['group_id']='aurelia-integration'
        central=self.root/'central'; central.mkdir()
        (central/'goals.json').write_text('{"foreign":"SECRET_FOREIGN_PROJECT"}')
        self.config['governor_dir']=str(central)
        with patch.object(self.registry,'list_projects',return_value=selected):
            result=ScopeService(self.registry,self.config).context('project',a['id'])
        self.assertNotIn('SECRET_FOREIGN_PROJECT',json.dumps(result))

    def save_draft(self,context,project_id,text='Unconfirmed requirements'):
        from governor_workbench.intake import Intake
        from governor_workbench.intake_drafts import IntakeDrafts
        project=next(p for p in context['projects'] if p['id']==project_id)
        memory=project['memories'][0]
        fields={key:text+' '+key for key in Intake.FIELDS}
        return IntakeDrafts(self.store).save(context,context['scope_hash'],project_id,fields,
            [{'name':memory['name'],'sha256':memory['sha256']}])

    def test_current_draft_is_reference_and_changes_only_review_hash(self):
        a=self.project('alpha'); before=self.scope('project',a['id'])
        draft=self.save_draft(before,a['id'])
        after=self.scope('project',a['id'])
        self.assertEqual([{'id':draft['id'],'project_id':a['id'],'source_hash':draft['source_hash'],
            'fields':draft['fields'],'status':'unconfirmed_draft'}],after['intake_proposals'])
        self.assertNotEqual(before['scope_hash'],after['scope_hash'])
        self.assertEqual(before['intake_source_hash'],after['intake_source_hash'])
        self.assertEqual(after['scope_hash'],self.scope('project',a['id'])['scope_hash'])
        self.assertFalse(after['intake'][0]['intake_accepted'])
        self.assertFalse(after['plan_ready'])
        self.assertEqual([],after['intake_records'])
        self.assertEqual(before['operator_decisions'],after['operator_decisions'])
        newer=self.save_draft(after,a['id'],'Revised requirements')
        revised=self.scope('project',a['id'])
        self.assertEqual(newer['id'],revised['intake_proposals'][0]['id'])
        self.assertNotEqual(after['scope_hash'],revised['scope_hash'])

    def test_acceptance_removes_proposal_and_retains_assessed_fields(self):
        from governor_workbench.intake import Intake
        a=self.project('alpha'); context=self.scope('project',a['id'])
        draft=self.save_draft(context,a['id'])
        context=self.scope('project',a['id'])
        # This fixture has no Git repository; supply synthetic complete evidence
        # to exercise the intake lifecycle without claiming product verification.
        context['intake'][0]['evidence_complete']=True
        Intake(self.store).accept(context,context['scope_hash'],a['id'],draft['fields'])
        accepted=self.scope('project',a['id'])
        self.assertEqual([],accepted['intake_proposals'])
        self.assertTrue(accepted['intake'][0]['intake_accepted'])
        self.assertEqual(draft['fields'],accepted['intake_records'][0]['body'])
        self.assertEqual(context['intake_source_hash'],accepted['intake_source_hash'])

    def test_foreign_scope_and_stale_drafts_are_excluded(self):
        a=self.project('alpha'); b=self.project('beta')
        first=self.scope('project',a['id'])
        self.save_draft(self.scope('project',b['id']),b['id'],'SECRET_BETA_DRAFT')
        self.assertEqual(first['scope_hash'],self.scope('project',a['id'])['scope_hash'])
        self.save_draft(first,a['id'])
        (Path(a['path'])/'project_memories/strategy.md').write_text('changed alpha')
        stale=self.scope('project',a['id'])
        self.assertEqual([],stale['intake_proposals'])
        self.assertNotIn('SECRET_BETA_DRAFT',json.dumps(stale))
        group=self.registry.create_group('Team')
        self.registry.assign(a['id'],group['id'],'parent')
        self.save_draft(self.scope('group',group['id']),a['id'],'GROUP_ONLY_DRAFT')
        single=self.scope('project',a['id'])
        self.assertEqual([],single['intake_proposals'])
        self.assertNotIn('GROUP_ONLY_DRAFT',json.dumps(single))

    def test_draft_does_not_bypass_egress_permission(self):
        from governor_workbench.scopes import ScopeService
        a=self.project('alpha',False)
        local=ScopeService(self.registry,self.config).context('project',a['id'],require_egress=False)
        self.save_draft(local,a['id'])
        with self.assertRaisesRegex(ValueError,'Modell'): self.scope('project',a['id'])

    def test_legacy_report_matches_decisions_and_rejects_decision_drift(self):
        from unittest.mock import patch
        from governor_workbench.evidence import Observer, fingerprint
        from governor_workbench.scopes import ScopeService
        self.project('alpha')
        selected=self.registry.list_projects()
        selected[0]['group_id']='aurelia-integration'
        decisions=[{'step_id':'reconcile_sources','kind':'authorize',
            'reason':'Explicit synthetic authorization.','actor':'operator'}]
        jobs=[]
        original_scan=Observer.scan

        def synthetic_complete(observer,*args,**kwargs):
            # Temporary fixtures are not Git repositories. Supply completeness
            # solely for this isolated report/decision binding regression.
            result=original_scan(observer,*args,**kwargs)
            result['evidence_complete']=True
            for project in result['projects']: project['evidence_complete']=True
            return result

        def reconciliation(context):
            return next(s for s in context['governor_matrix']['steps'] if s['id']=='reconcile_sources')

        with patch.object(self.registry,'list_projects',return_value=selected), \
                patch.object(self.registry,'list_groups',return_value=[{'id':'aurelia-integration'}]), \
                patch.object(self.store,'decisions',return_value=decisions), \
                patch.object(self.store,'jobs',return_value=jobs), \
                patch('governor_workbench.vault.Vault.list_sources',return_value=[]), \
                patch.object(Observer,'scan',synthetic_complete):
            service=ScopeService(self.registry,self.config)
            before=service.context('group','aurelia-integration')
            initial=reconciliation(before)
            self.assertTrue(initial['can_run'])
            jobs.append({'id':'existing-report','action':'governance_report','status':'completed',
                'result':{'step_id':'reconcile_sources','evidence_hash':initial['evidence_hash'],
                    'decision_hash':fingerprint(decisions),'success':True}})
            current=service.context('group','aurelia-integration')
            reported=reconciliation(current)
            self.assertEqual(initial['evidence_hash'],reported['evidence_hash'])
            self.assertEqual('review_required',reported['status'])
            self.assertFalse(reported['can_run'])
            self.assertFalse(reported['accepted'])
            decisions.append({'step_id':'reconcile_sources','kind':'authorize',
                'reason':'New synthetic operator decision.','actor':'operator'})
            changed=service.context('group','aurelia-integration')
            drifted=reconciliation(changed)
            self.assertEqual(initial['evidence_hash'],drifted['evidence_hash'])
            self.assertNotEqual(current['decision_hash'],changed['decision_hash'])
            self.assertEqual('ready',drifted['status'])
            self.assertTrue(drifted['can_run'])
            self.assertFalse(drifted['accepted'])
