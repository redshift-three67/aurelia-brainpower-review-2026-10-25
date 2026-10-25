import copy
import sqlite3
import tempfile
import unittest
from pathlib import Path

from governor_workbench.store import Store


class PlanTests(unittest.TestCase):
    def setUp(self):
        from governor_workbench.plans import PlanBook
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.store = Store(Path(self.tmp.name) / 'journal.db')
        self.book = PlanBook(self.store)
        self.context = {'plan_ready': True, 'scope_hash': 'a' * 64,
                        'review_scope': {'kind': 'project', 'id': 'alpha'},
                        'registry_projects': [{'id': 'alpha'}]}
        self.review = {'summary': 'Ready for operator review', 'decision': 'REVIEW_ONLY',
                       'findings': [], 'required_evidence': []}
        self.proposal = {'summary': 'Bounded proposal', 'steps': [self.step('first')]}

    def step(self, key, dependencies=None):
        return {'id': key, 'title': 'Check source', 'project_id': 'alpha', 'priority': 1,
                'depends_on': dependencies or [], 'rationale': 'Verify requested behavior',
                'scope': ['src/main.py'], 'tests': ['Run unit tests'], 'action': 'review'}

    def save(self):
        return self.book.save_candidate(self.context, self.proposal, self.review, 'fixture-job')

    def test_candidate_requires_explicit_operator_approval(self):
        candidate = self.save()
        self.assertEqual(candidate['status'], 'candidate')
        self.assertFalse(candidate['execution_enabled'])
        self.assertFalse(self.book.execution_permission(candidate['id'], 'first', self.context)['plan_selection_approved'])
        approval = self.book.approve(candidate['id'], self.context['scope_hash'], self.context, ['first'])
        self.assertFalse(approval['execution_enabled'])
        permission = self.book.execution_permission(candidate['id'], 'first', self.context)
        self.assertTrue(permission['plan_selection_approved'])
        self.assertFalse(permission['execution_enabled'])

    def test_chain_report_resolves_transitive_dependencies_without_completion_claim(self):
        self.proposal['steps']=[self.step('end',['left','right']),self.step('right',['start']),self.step('left',['start']),self.step('start')]
        candidate=self.save()
        self.book.approve(candidate['id'],'a'*64,self.context,['start','left','right','end'],mode='sequence')
        report=self.book.dependency_report(candidate['id'],self.context)
        rows={r['id']:r for r in report['steps']}
        self.assertEqual(set(rows['end']['all_predecessors']),{'start','left','right'})
        self.assertEqual(rows['end']['missing_completion_ids'],rows['end']['all_predecessors'])
        self.assertTrue(rows['end']['selected'])
        self.assertFalse(report['execution_enabled'])
        self.assertEqual(rows['start']['all_predecessors'],[])
        self.assertEqual(rows['start']['completion_status'],'not_proven')

    def test_chain_report_marks_stale_context(self):
        candidate=self.save()
        context={**self.context,'scope_hash':'b'*64}
        report=self.book.dependency_report(candidate['id'],context)
        self.assertFalse(report['current'])
        self.assertFalse(report['steps'][0]['selected'])

    def test_chain_report_latest_test_failure_is_not_hidden(self):
        candidate=self.save()
        source=self.store.create_job('scope_patch',None,{'candidate_id':candidate['id'],'step_id':'first'})
        self.store.update_job(source['id'],status='completed')
        for status in ('completed','failed'):
            test=self.store.create_job('stage_test',None,{'stage_job_id':source['id']})
            self.store.update_job(test['id'],status=status,result={'success':True})
        row=self.book.dependency_report(candidate['id'],self.context)['steps'][0]
        self.assertEqual(row['latest_test']['id'],test['id'])
        self.assertEqual(row['latest_test']['status'],'failed')
        self.assertEqual(row['completion_status'],'not_proven')

    def test_operator_completion_requires_predecessors_and_is_invalidated_by_reselection(self):
        self.proposal['steps']=[self.step('first'),self.step('second',['first'])]
        candidate=self.save()
        selection=self.book.approve(candidate['id'],'a'*64,self.context,['first','second'],mode='sequence')
        def accept(step): return self.book.complete_step(candidate['id'],step,self.context,'a'*64,selection['id'],'Fachlich geprüft.')
        with self.assertRaises(ValueError): accept('second')
        first=accept('first'); second=accept('second')
        report=self.book.dependency_report(candidate['id'],self.context)
        self.assertEqual([r['completion_status'] for r in report['steps']],['accepted','accepted'])
        self.assertEqual(second['predecessor_receipts'],{'first':first['id']})
        self.assertFalse(report['execution_enabled'])
        self.book.approve(candidate['id'],'a'*64,self.context,['first','second'],mode='sequence')
        self.assertEqual(self.book.dependency_report(candidate['id'],self.context)['steps'][1]['completion_status'],'stale')

    def test_completion_cannot_accept_changes_or_tests(self):
        for action in ('change','test'):
            self.proposal['steps']=[{**self.step('first'),'action':action}]
            candidate=self.save(); selection=self.book.approve(candidate['id'],'a'*64,self.context,['first'])
            with self.assertRaises(ValueError):
                self.book.complete_step(candidate['id'],'first',self.context,'a'*64,selection['id'],'Keine technische Abnahme ersetzen.')

    def test_withdrawal_invalidates_descendants_and_preserves_history(self):
        self.proposal['steps']=[self.step('first'),self.step('second',['first'])]
        candidate=self.save(); selection=self.book.approve(candidate['id'],'a'*64,self.context,['first','second'],mode='sequence')
        first=self.book.complete_step(candidate['id'],'first',self.context,'a'*64,selection['id'],'Geprüft')
        self.book.complete_step(candidate['id'],'second',self.context,'a'*64,selection['id'],'Geprüft')
        self.book.withdraw_completion(candidate['id'],'first',first['id'],'Abnahme zurückgenommen')
        report=self.book.dependency_report(candidate['id'],self.context)
        self.assertEqual([r['completion_status'] for r in report['steps']],['withdrawn','stale'])
        self.book.complete_step(candidate['id'],'first',self.context,'a'*64,selection['id'],'Erneut geprüft')
        self.assertEqual(self.book.dependency_report(candidate['id'],self.context)['steps'][1]['completion_status'],'stale')
        with self.store.db() as db:
            self.assertEqual(db.execute('SELECT COUNT(*) FROM step_completions').fetchone()[0],4)
            with self.assertRaises(sqlite3.IntegrityError): db.execute('DELETE FROM step_completions')

    def test_completion_requires_note_current_scope_and_selection(self):
        candidate=self.save(); selection=self.book.approve(candidate['id'],'a'*64,self.context,['first'])
        for scope,choice,note in [('b'*64,selection['id'],'Geprüft'),('a'*64,'f'*32,'Geprüft'),('a'*64,selection['id'],' ')]:
            with self.subTest(scope=scope,choice=choice,note=note), self.assertRaises(ValueError):
                self.book.complete_step(candidate['id'],'first',self.context,scope,choice,note)

    def test_invalid_structure_and_foreign_projects_rejected(self):
        mutations = [('project_id', 'foreign'), ('priority', True), ('action', 'shell'),
                     ('id', '../bad'), ('scope', ['../secret']), ('scope', ['C:/secret']),
                     ('scope', ['.git/config']), ('scope', ['src/.env']),
                     ('scope', ['credentials.json']), ('scope', ['src\\..\\secret'])]
        for key, value in mutations:
            with self.subTest(key=key, value=value):
                self.proposal['steps'] = [self.step('first')]
                self.proposal['steps'][0][key] = value
                with self.assertRaises(ValueError): self.save()
        self.assertEqual(self.book.list('project', 'alpha'), [])

    def test_cycles_duplicates_unknown_dependencies_and_extra_fields(self):
        for steps in ([self.step('a', ['b']), self.step('b', ['a'])],
                      [self.step('a'), self.step('a')], [self.step('a', ['missing'])],
                      [{**self.step('a'), 'command': 'unsafe'}]):
            self.proposal['steps'] = steps
            with self.assertRaises(ValueError): self.save()

    def test_readiness_and_supervisor_findings_block_candidates(self):
        for field in ('findings', 'required_evidence'):
            self.review[field] = ['Unresolved']
            with self.assertRaises(ValueError): self.save()
            self.review[field] = []
        self.review['decision'] = 'BLOCK'
        with self.assertRaises(ValueError): self.save()
        self.review['decision'] = 'REVIEW_ONLY'
        self.context['plan_ready'] = False
        with self.assertRaises(ValueError): self.save()

    def test_stale_approval_and_different_scope_rejected(self):
        candidate = self.save()
        current = copy.deepcopy(self.context)
        current['scope_hash'] = 'b' * 64
        with self.assertRaises(ValueError): self.book.approve(candidate['id'], 'a'*64, current, ['first'])
        current = copy.deepcopy(self.context)
        current['review_scope']['id'] = 'foreign'
        with self.assertRaises(ValueError): self.book.approve(candidate['id'], 'a'*64, current, ['first'])

    def test_sequence_requires_complete_dependencies_and_order(self):
        self.proposal['steps'] = [self.step('first'), self.step('second', ['first'])]
        candidate = self.save()
        for selection, mode in [(['second'], 'single'), (['second', 'first'], 'sequence'),
                                (['first', 'second'], 'single'), ([], 'sequence'),
                                (['first', 'outside'], 'sequence')]:
            with self.assertRaises(ValueError):
                self.book.approve(candidate['id'], 'a'*64, self.context, selection, mode)
        approval = self.book.approve(candidate['id'], 'a'*64, self.context, ['first', 'second'], 'sequence')
        self.assertEqual(approval['selected_step_ids'], ['first', 'second'])

    def test_append_only_history_and_new_revision_invalidates_selection(self):
        first = self.save()
        self.book.approve(first['id'], 'a'*64, self.context, ['first'])
        second = self.save()
        self.assertEqual(second['version'], 2)
        self.assertEqual(second['previous_candidate_id'], first['id'])
        self.assertFalse(self.book.execution_permission(first['id'], 'first', self.context)['plan_selection_approved'])
        with self.assertRaises(ValueError): self.book.approve(first['id'], 'a'*64, self.context, ['first'])
        self.assertEqual(len(self.book.list('project', 'alpha')), 2)
        with self.store.db() as c:
            for table in ('plan_candidates', 'plan_approvals'):
                for command in ('DELETE FROM ' + table, 'UPDATE ' + table + ' SET id=id'):
                    with self.assertRaises(sqlite3.IntegrityError): c.execute(command)

    def test_change_selection_never_enables_execution(self):
        self.proposal['steps'][0]['action'] = 'change'
        candidate = self.save()
        self.book.approve(candidate['id'], 'a'*64, self.context, ['first'])
        self.assertFalse(self.book.execution_permission(candidate['id'], 'first', self.context)['execution_enabled'])

    def test_credential_variants_and_resource_bounds_rejected(self):
        for path in ('config/credentials.local.json', 'config/api_token.txt', '.config/secrets.yaml'):
            self.proposal['steps'][0]['scope'] = [path]
            with self.subTest(path=path), self.assertRaises(ValueError): self.save()
        self.proposal['steps'] = [self.step('s'+str(i)) for i in range(51)]
        with self.assertRaises(ValueError): self.save()
        self.proposal['steps'] = [self.step('first')]
        self.proposal['steps'][0]['title'] = 'x'*161
        with self.assertRaises(ValueError): self.save()

    def test_restart_preserves_snapshot_and_does_not_interrupt_jobs(self):
        from governor_workbench.plans import PlanBook
        candidate = self.save()
        job = self.store.create_job('refresh', None)
        self.proposal['steps'][0]['title'] = 'Changed caller object'
        self.review['summary'] = 'Changed caller review'
        reopened = PlanBook(self.store)
        self.assertEqual(reopened.list('project', 'alpha'), [candidate])
        self.assertEqual(self.store.job(job['id'])['status'], 'queued')

    def test_new_selection_replaces_previous_selection_without_erasing_history(self):
        self.proposal['steps'].append(self.step('second'))
        candidate = self.save()
        self.book.approve(candidate['id'], 'a'*64, self.context, ['first'])
        self.book.approve(candidate['id'], 'a'*64, self.context, ['second'])
        self.assertFalse(self.book.execution_permission(candidate['id'], 'first', self.context)['plan_selection_approved'])
        self.assertTrue(self.book.execution_permission(candidate['id'], 'second', self.context)['plan_selection_approved'])
        with self.store.db() as c:
            self.assertEqual(c.execute('SELECT COUNT(*) FROM plan_approvals').fetchone()[0], 2)
