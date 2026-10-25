import copy
from concurrent.futures import ThreadPoolExecutor
import sqlite3
import tempfile
import unittest
from pathlib import Path

from governor_workbench.evidence import fingerprint
from governor_workbench.intake import Intake
from governor_workbench.plans import PlanBook
from governor_workbench.store import Store


class StrategyTests(unittest.TestCase):
    def setUp(self):
        from governor_workbench.strategies import StrategyBook
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.store = Store(Path(self.tmp.name) / 'journal.db')
        self.plans = PlanBook(self.store)
        self.book = StrategyBook(self.store)
        self.context = dict(plan_ready=True, scope_hash='a'*64,
                            review_scope=dict(kind='project', id='alpha'),
                            registry_projects=[dict(id='alpha')],
                            projects=[dict(id='alpha', evidence_hash='b'*64)],
                            intake_records=[dict(id='intake1', project_id='alpha', source_hash='b'*64,
                                                 body=dict(requirements='Assessed'))])
        Intake(self.store)
        with self.store.db() as c:
            c.execute('INSERT INTO reg_intake VALUES(?,?,?,?,?)',
                      ('intake1', 'alpha', 'b'*64, '{"requirements":"Assessed"}', 'before'))
        self.context['intake_records'] = Intake(self.store).records(['alpha'])
        self.proposal = dict(summary='Review strategy', steps=[dict(id='first', title='Review',
            project_id='alpha', priority=1, depends_on=[], rationale='Check facts',
            scope=['src/main.py'], tests=['Run unit tests'], action='change')])
        self.review = dict(summary='Independently reviewed', decision='REVIEW_ONLY', findings=[], required_evidence=[])

    def candidate(self):
        from governor_workbench.model_memory import VERSION
        job = self.store.create_job('scope_plan', None)
        candidate = self.plans.save_candidate(self.context, self.proposal, self.review, job['id'])
        self.store.update_job(job['id'], status='completed', result=dict(candidate=candidate,
            proposal=self.proposal, review=self.review, stale=False, scope_hash=self.context['scope_hash'],
            review_scope=self.context['review_scope'], plan_ready=True,
            memory_coverage=dict(version=VERSION,status='full',files=[]),model_context_hash='c'*64))
        return candidate

    def adopt(self, candidate, previous=None, context=None, source_hash=None):
        return self.book.adopt(candidate['id'], source_hash or self.context['scope_hash'], previous,
                               context or self.context)

    def test_adoption_snapshots_provenance_without_granting_permission(self):
        candidate = self.candidate()
        revision = self.adopt(candidate)
        self.assertEqual(revision['version'], 1)
        self.assertIsNone(revision['previous_revision_id'])
        self.assertEqual(revision['candidate_id'], candidate['id'])
        self.assertEqual(revision['candidate_hash'], fingerprint(candidate))
        self.assertEqual(revision['proposal_hash'], candidate['proposal_hash'])
        self.assertEqual(revision['proposal'], self.proposal)
        self.assertEqual(revision['review'], self.review)
        self.assertEqual(revision['project_hashes'], {'alpha': 'b'*64})
        self.assertEqual(revision['intake_records'], self.context['intake_records'])
        self.assertEqual(revision['actor'], 'operator')
        self.assertFalse(revision['execution_enabled'])
        self.assertFalse(self.plans.execution_permission(candidate['id'], 'first', self.context)['plan_selection_approved'])
        revision['proposal']['summary'] = 'Caller mutation'
        self.assertEqual(self.book.list('project', 'alpha')[0]['proposal'], self.proposal)
        self.assertEqual(self.store.decisions(), [])

    def test_stale_hash_scope_and_false_readiness_rejected(self):
        candidate = self.candidate()
        for change in ({'scope_hash': 'c'*64}, {'plan_ready': False},
                       {'review_scope': dict(kind='group', id='other')}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                self.adopt(candidate, context={**self.context, **change})
        with self.assertRaises(ValueError): self.adopt(candidate, source_hash='c'*64)
        self.assertEqual(self.book.list('project', 'alpha'), [])

    def test_old_candidate_and_duplicate_rejected(self):
        first = self.candidate()
        second = self.candidate()
        with self.assertRaises(ValueError): self.adopt(first)
        revision = self.adopt(second)
        for previous in (None, revision['id']):
            with self.assertRaises(ValueError): self.adopt(second, previous)

    def test_compare_and_swap_retains_immutable_history(self):
        first = self.adopt(self.candidate())
        second_candidate = self.candidate()
        for previous in (None, 'unknown'):
            with self.assertRaises(ValueError): self.adopt(second_candidate, previous)
        second = self.adopt(second_candidate, first['id'])
        self.assertEqual(second['previous_revision_id'], first['id'])
        self.assertEqual(second['version'], 2)
        self.assertEqual(self.book.list('project', 'alpha'), [second, first])
        with self.store.db() as c:
            for sql in ('DELETE FROM strategy_revisions', 'UPDATE strategy_revisions SET body=body'):
                with self.assertRaises(sqlite3.IntegrityError): c.execute(sql)

    def test_missing_failed_and_wrong_action_job_rejected(self):
        candidate = self.candidate()
        for status in ('queued', 'running', 'failed', 'interrupted', 'cancelled'):
            self.store.update_job(candidate['job_id'], status=status)
            with self.subTest(status=status), self.assertRaises(ValueError): self.adopt(candidate)
        self.store.update_job(candidate['job_id'], status='completed')
        with self.store.db() as c:
            c.execute("UPDATE jobs SET action='scope_review' WHERE id=?", (candidate['job_id'],))
        with self.assertRaises(ValueError): self.adopt(candidate)
        with self.store.db() as c: c.execute('DELETE FROM jobs WHERE id=?', (candidate['job_id'],))
        with self.assertRaises(ValueError): self.adopt(candidate)

    def test_job_result_must_match_stored_candidate_and_clean_review(self):
        candidate = self.candidate()
        original = self.store.job(candidate['job_id'])['result']
        invalid = [None, {}, {**original, 'stale': True}, {**original, 'stale': None},
                   {key:value for key,value in original.items() if key!='memory_coverage'},
                   {**original, 'memory_coverage':dict(version='partial-old',status='full',files=[])},
                   {**original, 'memory_coverage':dict(version=original['memory_coverage']['version'],status='missing',files=[])},
                   {**original, 'candidate': {**candidate, 'id': 'wrong'}},
                   {**original, 'review': {**self.review, 'findings': ['Unresolved']}},
                   {**original, 'proposal': {**self.proposal, 'summary': 'Other'}},
                   {**original, 'scope_hash': 'c'*64}, {**original, 'plan_ready': False}]
        for result in invalid:
            self.store.update_job(candidate['job_id'], result=result)
            with self.subTest(result=result), self.assertRaises(ValueError): self.adopt(candidate)

    def test_staged_memory_plan_requires_every_source_for_both_readers(self):
        from governor_workbench.model_memory import VERSION, STAGE_VERSION
        candidate = self.candidate()
        original = self.store.job(candidate['job_id'])['result']
        source = dict(project_id='alpha',name='state.md',sha256='d'*64,
                      source_bytes=10,included_chars=10)
        stages = [dict(project_id='alpha',name='state.md',sha256='d'*64,
                       char_start=0,char_end=10,model=model)
                  for model in ('gpt-5.6-terra','gpt-5.6-sol')]
        coverage = dict(version=VERSION,status='staged',stage_version=STAGE_VERSION,
                        stage_models=['gpt-5.6-terra','gpt-5.6-sol'],files=[source],stages=stages)
        self.store.update_job(candidate['job_id'], result={**original,'memory_coverage':coverage})
        broken = copy.deepcopy(coverage)
        broken['stages'][1]['char_start'] = 1
        self.store.update_job(candidate['job_id'], result={**original,'memory_coverage':broken})
        with self.assertRaises(ValueError): self.adopt(candidate)
        self.store.update_job(candidate['job_id'], result={**original,'memory_coverage':coverage})
        self.assertEqual(1,self.adopt(candidate)['version'])

    def test_route_b_strategy_requires_independent_mandatory_astra_plan(self):
        candidate = self.candidate()
        with self.store.db() as c:
            c.execute("UPDATE jobs SET action='scope_route_b_plan' WHERE id=?", (candidate['job_id'],))
        original = self.store.job(candidate['job_id'])['result']
        for extra in ({}, {'route_variant':'b_v1'},
                      {'route_variant':'b_plus_v1','critical_reviewer':None},
                      {'route_variant':'b_plus_v1','critical_reviewer':'gpt-6-astra',
                       'critical_review_reason':'operator_selected'}):
            self.store.update_job(candidate['job_id'], result={**original, **extra})
            with self.subTest(extra=extra), self.assertRaises(ValueError):
                self.adopt(candidate)
        self.store.update_job(candidate['job_id'], result={**original,
            'route_variant':'b_plus_v1','critical_reviewer':'gpt-6-astra',
            'critical_review_reason':'mandatory_plan', 'critical_review_required':True,
            'critical_report':self.review})
        self.assertEqual(1,self.adopt(candidate)['version'])

    def test_scope_isolation_and_bounded_listing(self):
        first = self.adopt(self.candidate())
        self.context['review_scope'] = dict(kind='group', id='group1')
        self.context['scope_hash'] = 'c'*64
        candidate = self.candidate()
        with self.assertRaises(ValueError): self.adopt(candidate, first['id'])
        group = self.adopt(candidate)
        self.assertEqual(group['version'], 1)
        self.assertEqual(self.book.list('project', 'alpha'), [first])
        self.assertEqual(self.book.list('group', 'group1'), [group])
        for limit in (0, 101, True, '1'):
            with self.assertRaises(ValueError): self.book.list('group', 'group1', limit)

    def test_reopen_preserves_jobs_and_history(self):
        from governor_workbench.strategies import StrategyBook
        revision = self.adopt(self.candidate())
        job = self.store.create_job('refresh', None)
        self.assertEqual(StrategyBook(self.store).list('project', 'alpha'), [revision])
        self.assertEqual(self.store.job(job['id'])['status'], 'queued')

    def test_missing_or_foreign_provenance_is_rejected_atomically(self):
        candidate = self.candidate()
        for change in ({'projects': []}, {'intake_records': []},
                       {'projects': [dict(id='foreign', evidence_hash='b'*64)]},
                       {'intake_records': [dict(project_id='alpha', source_hash='c'*64)]}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                self.adopt(candidate, context={**self.context, **change})
        self.assertEqual(self.book.list('project', 'alpha'), [])
        self.assertEqual(self.adopt(candidate)['version'], 1)

    def test_concurrent_adoption_commits_only_one_revision(self):
        from governor_workbench.strategies import StrategyBook
        candidate = self.candidate()
        books = [StrategyBook(self.store), StrategyBook(self.store)]
        def adopt(book):
            try:
                return book.adopt(candidate['id'], 'a'*64, None, self.context)
            except ValueError:
                return None
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(adopt, books))
        self.assertEqual(sum(result is not None for result in results), 1)
        self.assertEqual(len(self.book.list('project', 'alpha')), 1)

    def test_intake_change_after_context_scan_blocks_adoption(self):
        candidate = self.candidate()
        with self.store.db() as c:
            c.execute('INSERT INTO reg_intake VALUES(?,?,?,?,?)',
                      ('intake2', 'alpha', 'b'*64, '{"requirements":"Changed"}', 'after'))
        with self.assertRaises(ValueError): self.adopt(candidate)
        self.assertEqual(self.book.list('project', 'alpha'), [])

    def test_intake_body_change_with_same_id_and_source_blocks_adoption(self):
        candidate = self.candidate()
        with self.store.db() as c:
            c.execute('UPDATE reg_intake SET body=? WHERE id=?',
                      ('{"requirements":"Changed"}', 'intake1'))
        with self.assertRaises(ValueError): self.adopt(candidate)
        self.assertEqual(self.book.list('project', 'alpha'), [])
