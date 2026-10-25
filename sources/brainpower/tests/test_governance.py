import copy
import unittest

from governor_workbench.governance import STEPS, build_matrix, validate_decision


def observation(value='source-a', complete=True):
    return {'evidence_hash': value, 'evidence_complete': complete, 'decision_hash': 'decisions-a',
            'observed_at': '2026-09-12T00:00:00+00:00', 'projects': [
                {'id': key, 'name': key, 'evidence_complete': complete, 'memories': [], 'sources': [],
                 'documented_statuses': {}} for key in
                ('aurelia', 'radiworks', 'radi144', 'morphic_v1', 'modul_templates')]}


def decision(step, kind, evidence='source-a'):
    return {'step_id': step, 'kind': kind, 'reason': 'Explicit operator decision.',
            'evidence_hash': evidence, 'actor': 'operator'}


def accept(step):
    return [decision(step, 'authorize'), decision(step, 'accept')]


def by_id(matrix, key):
    return next(step for step in matrix['steps'] if step['id'] == key)


class GovernanceTests(unittest.TestCase):
    def test_intake_has_no_ground_zero_dependency(self):
        decisions = accept('reconcile_sources') + [decision('radiworks_intake', 'authorize')]
        matrix = build_matrix(observation(), decisions, [])
        self.assertEqual('ready', by_id(matrix, 'radiworks_intake')['status'])
        self.assertEqual('blocked', by_id(matrix, 'aurelia_ground_zero')['status'])
        self.assertEqual('blocked', by_id(matrix, 'radiworks_adapter')['status'])

    def test_authorization_alone_does_not_accept_step(self):
        matrix = build_matrix(observation(), [decision('reconcile_sources', 'authorize')], [])
        step = by_id(matrix, 'reconcile_sources')
        self.assertEqual('ready', step['status'])
        self.assertFalse(step['accepted'])
        self.assertTrue(step['can_run'])

    def test_current_report_requires_operator_acceptance(self):
        job = {'id': 'report', 'action': 'governance_report', 'status': 'completed',
               'result': {'step_id': 'reconcile_sources', 'evidence_hash': 'source-a', 'success': True}}
        matrix = build_matrix(observation(), [decision('reconcile_sources', 'authorize')], [job])
        self.assertEqual('review_required', by_id(matrix, 'reconcile_sources')['status'])
        self.assertFalse(by_id(matrix, 'reconcile_sources')['accepted'])

    def test_report_decision_drift_allows_fresh_report(self):
        job = {'id': 'report', 'action': 'governance_report', 'status': 'completed',
               'result': {'step_id': 'reconcile_sources', 'evidence_hash': 'source-a',
                          'decision_hash': 'old-decisions', 'success': True}}
        matrix = build_matrix(observation(), [decision('reconcile_sources', 'authorize')], [job])
        self.assertTrue(by_id(matrix, 'reconcile_sources')['can_run'])
        record = next(r for r in matrix['knowledge'] if r['kind'] == 'execution_record')
        self.assertFalse(record['current'])

    def test_product_test_evidence_survives_governance_rule_change(self):
        obs = observation('new-rule-bound-hash')
        obs['source_hash'] = 'same-product-sources'
        jobs = [{'id': 'legacy-test', 'action': 'radiworks_tests', 'status': 'completed',
                 'result': {'evidence_hash': 'same-product-sources', 'success': True}}]
        record = next(r for r in build_matrix(obs, [], jobs)['knowledge'] if r['kind'] == 'execution_record')
        self.assertTrue(record['current'])
        self.assertEqual('same-product-sources', record['sha256'])

    def test_source_drift_invalidates_acceptance_but_not_read_only_authorization(self):
        matrix = build_matrix(observation('source-b'), accept('reconcile_sources'), [])
        step = by_id(matrix, 'reconcile_sources')
        self.assertEqual('stale', step['status'])
        self.assertTrue(step['authorized'])
        self.assertTrue(step['acceptance_eligible'])
        self.assertFalse(step['accepted'])
        self.assertTrue(step['can_run'])

    def test_incomplete_evidence_blocks_every_step(self):
        matrix = build_matrix(observation(complete=False), accept('reconcile_sources'), [])
        self.assertTrue(all(s['status'] == 'blocked' for s in matrix['steps']))
        self.assertFalse(matrix['next_steps'])

    def test_revoke_invalidates_accepted_step_and_dependents(self):
        decisions = accept('reconcile_sources') + accept('radiworks_intake')
        decisions.append(decision('reconcile_sources', 'revoke'))
        matrix = build_matrix(observation(), decisions, [])
        self.assertFalse(by_id(matrix, 'reconcile_sources')['accepted'])
        self.assertFalse(by_id(matrix, 'radiworks_intake')['accepted'])
        self.assertEqual('blocked', by_id(matrix, 'radiworks_intake')['status'])

    def test_reject_overrides_earlier_acceptance(self):
        decisions = accept('reconcile_sources') + [decision('reconcile_sources', 'reject')]
        step = by_id(build_matrix(observation(), decisions, []), 'reconcile_sources')
        self.assertFalse(step['accepted'])

    def test_model_report_never_grants_gate(self):
        job = {'id': 'model', 'action': 'hybrid_review', 'status': 'completed',
               'result': {'evidence_hash': 'source-a', 'decision_hash': 'decisions-a',
                          'approval_granted': True, 'review': {'decision': 'GO', 'summary': 'Implement now.'}}}
        matrix = build_matrix(observation(), [], [job])
        self.assertTrue(all(not s['accepted'] for s in matrix['steps']))
        self.assertFalse(matrix['review_summary']['approval_granted'])
        self.assertNotEqual('current', matrix['review_summary']['status'])

    def test_implementation_block_does_not_block_authorized_read_only_work(self):
        job = {'id': 'review', 'action': 'hybrid_review', 'status': 'completed',
               'result': {'evidence_hash': 'source-a', 'decision_hash': 'decisions-a',
                          'review': {'decision': 'BLOCK', 'summary': 'Implementation approval absent.',
                                     'findings': ['Implementation needs approval.'], 'required_evidence': []}}}
        matrix = build_matrix(observation(), [decision('reconcile_sources', 'authorize')], [job])
        self.assertEqual('ready', by_id(matrix, 'reconcile_sources')['status'])
        self.assertEqual('current', matrix['review_summary']['status'])
        self.assertEqual(['Implementation needs approval.'], matrix['review_summary']['findings'])

    def test_review_decision_drift_is_stale(self):
        job = {'id': 'review', 'action': 'hybrid_review', 'status': 'completed',
               'result': {'evidence_hash': 'source-a', 'decision_hash': 'old-decisions',
                          'review': {'decision': 'BLOCK', 'summary': 'Historical.', 'findings': [], 'required_evidence': []}}}
        self.assertEqual('stale', build_matrix(observation(), [], [job])['review_summary']['status'])

    def test_comparison_carries_both_scoped_reviews_without_gate_approval(self):
        reports = {model: {'decision': 'BLOCK', 'summary': model + ' assessment',
                           'findings': [model + ' finding'], 'required_evidence': []}
                   for model in ('gpt-5.6-sol', 'gpt-6-astra')}
        job = {'id': 'comparison', 'project_id': 'radiworks', 'action': 'compare_reviews', 'status': 'completed',
               'result': {'evidence_hash': 'source-a', 'decision_hash': 'decisions-a', 'success': True,
                          'reviews': reports, 'comparison': {'complete': True}}}
        summary = build_matrix(observation(), [], [job])['review_summary']
        self.assertEqual('current', summary['status'])
        self.assertEqual('project', summary['scope'])
        self.assertEqual('radiworks', summary['project_id'])
        self.assertEqual(2, len(summary['reviews']))
        self.assertTrue(all(r['provenance'] == 'comparison' for r in summary['reviews']))
        self.assertFalse(summary['approval_granted'])

    def test_partial_comparison_cannot_be_current(self):
        job = {'id': 'comparison', 'action': 'compare_reviews', 'status': 'failed',
               'result': {'evidence_hash': 'source-a', 'decision_hash': 'decisions-a', 'success': False,
                          'reviews': {'gpt-5.6-sol': {'summary': 'Partial', 'decision': 'BLOCK'}, 'gpt-6-astra': None},
                          'comparison': {'complete': False}}}
        self.assertEqual('failed', build_matrix(observation(), [], [job])['review_summary']['status'])

    def test_pending_review_preserves_job_lifecycle(self):
        for status in ('queued', 'running'):
            job = {'id': 'pending', 'action': 'compare_reviews', 'status': status, 'result': None}
            summary = build_matrix(observation(), [], [job])['review_summary']
            self.assertEqual(status, summary['status'])
            self.assertFalse(summary['approval_granted'])

    def test_pending_attempt_does_not_replace_prior_current_review(self):
        previous = {'id': 'current', 'action': 'hybrid_review', 'status': 'completed',
                    'created_at': '2026-09-12T01:00:00+00:00',
                    'result': {'evidence_hash': 'source-a', 'decision_hash': 'decisions-a',
                               'review': {'decision': 'BLOCK', 'summary': 'Existing assessment.'}}}
        pending = {'id': 'pending', 'action': 'compare_reviews', 'status': 'running',
                   'created_at': '2026-09-12T02:00:00+00:00', 'result': None}
        summary = build_matrix(observation(), [], [pending, previous])['review_summary']
        self.assertEqual('current', summary['status'])
        self.assertEqual('current', summary['job_id'])
        self.assertEqual({'job_id': 'pending', 'status': 'running'}, summary['latest_attempt'])

    def test_old_snapshot_pause_is_knowledge_not_current_authority(self):
        obs = observation()
        obs['projects'][0]['sources'] = [{'name': 'session_state_freeze.json', 'path': 'snapshot.json',
                                        'sha256': 'proof', 'content': '{"status":"PAUSED"}'}]
        obs['projects'][0]['documented_statuses'] = {'Snapshot': 'PAUSED'}
        matrix = build_matrix(obs, [decision('reconcile_sources', 'authorize')], [])
        self.assertEqual('ready', by_id(matrix, 'reconcile_sources')['status'])
        claims = [row for row in matrix['knowledge'] if row['kind'] == 'source_declaration']
        self.assertTrue(any(row['sha256'] == 'proof' and row['provenance'] for row in claims))
        self.assertTrue(all(not row['accepted'] for row in claims))

    def test_absent_projects_omit_steps_but_never_satisfy_missing_dependencies(self):
        obs = observation()
        obs['projects'] = [p for p in obs['projects'] if p['id'] == 'radiworks']
        decisions = accept('reconcile_sources') + accept('radiworks_intake') + [decision('radiworks_adapter', 'authorize')]
        matrix = build_matrix(obs, decisions, [])
        self.assertNotIn('aurelia_ground_zero', [s['id'] for s in matrix['steps']])
        self.assertEqual('blocked', by_id(matrix, 'radiworks_adapter')['status'])

    def test_planned_projects_remain_unapproved(self):
        planned = [{'id': 'planned-one', 'name': 'Future', 'description': 'Later', 'depends_on': ['radiworks']}]
        matrix = build_matrix(observation(), [], [], planned)
        row = next(p for p in matrix['projects'] if p['id'] == 'planned-one')
        self.assertEqual('blocked', row['status'])

    def test_inputs_are_unchanged_and_ranking_is_deterministic(self):
        obs = observation()
        decisions = accept('reconcile_sources') + [decision(s, 'authorize') for s in ('radiworks_intake', 'radi144_checkpoint', 'morphic_authority')]
        original = copy.deepcopy((obs, decisions, STEPS))
        one = build_matrix(obs, decisions, [])
        two = build_matrix(obs, decisions, [])
        self.assertEqual(one, two)
        self.assertEqual(original, (obs, decisions, STEPS))
        self.assertEqual('radiworks_intake', one['next_steps'][0]['id'])

    def test_validate_accept_rejects_wrong_or_incomplete_evidence(self):
        for obs in (observation('other'), observation(complete=False)):
            with self.assertRaises(ValueError):
                validate_decision(decision('reconcile_sources', 'accept'), obs)

    def test_validate_rejects_model_author_and_empty_reason(self):
        for bad in ({**decision('reconcile_sources', 'accept'), 'actor': 'model'},
                    {**decision('reconcile_sources', 'authorize'), 'reason': '  '}):
            with self.assertRaises(ValueError):
                validate_decision(bad, observation())

    def test_validate_normalizes_authorization_and_disallows_unknown_step(self):
        row = validate_decision({'step_id': 'reconcile_sources', 'kind': 'authorize', 'reason': ' Review only. '}, observation())
        self.assertEqual('operator', row['actor'])
        self.assertEqual('source-a', row['evidence_hash'])
        self.assertEqual('Review only.', row['reason'])
        with self.assertRaises(ValueError):
            validate_decision(decision('invented', 'accept'), observation())


if __name__ == '__main__':
    unittest.main()
