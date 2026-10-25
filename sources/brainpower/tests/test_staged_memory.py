"""Oversized, hash-bound memory is staged without silently losing source coverage."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from governor_workbench.llm import ModelError, _review_input
from governor_workbench.model_memory import stage_memories, stage_coverage_complete


class StageClient:
    def __init__(self):
        self.calls = []

    def prompt_limit(self, model):
        return 95_000

    def call(self, model, prompt, **kwargs):
        self.calls.append((model, prompt))
        quote = 'MIDDLE_GATE_REQUIRES_OPERATOR_REVIEW' if 'MIDDLE_GATE_REQUIRES_OPERATOR_REVIEW' in prompt else 'ordinary evidence'
        return {'success': True, 'text': json.dumps({
            'summary': 'The source records a gated project state.',
            'quotes': [quote], 'open_questions': ['No independent implementation approval.']})}


class StagedMemoryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.roots = []
        projects = []
        files = []
        for key in ('one', 'two'):
            root = self.base / key
            folder = root / 'project_memories'
            folder.mkdir(parents=True)
            body = 'ordinary evidence\n' * 2400
            if key == 'two':
                body += 'MIDDLE_GATE_REQUIRES_OPERATOR_REVIEW\n'
            body += 'ordinary evidence\n' * 200
            raw = body.encode()
            (folder / 'state.md').write_bytes(raw)
            sha = hashlib.sha256(raw).hexdigest()
            item = {'name': 'state.md', 'sha256': sha, 'size': len(raw),
                    'excerpt': body, 'truncated': False}
            projects.append({'id': key, 'memories': [item]})
            files.append({'project_id': key, 'name': 'state.md', 'sha256': sha,
                          'source_bytes': len(raw), 'included_chars': len(body)})
            self.roots.append({'id': key, 'path': str(root)})
        self.context = {'projects': projects, 'memory_coverage': {
            'version': 'full-project-memory-v1', 'status': 'full',
            'projects': [{'project_id': k, 'status': 'full', 'file_count': 1} for k in ('one', 'two')],
            'files': files}, 'limits': []}

    def test_both_models_read_all_originals_then_final_context_fits(self):
        client = StageClient()
        staged = stage_memories(self.context, self.roots, client,
                                ('gpt-6-sol', 'gpt-6-luna'), cache_dir=self.base / 'cache')
        self.assertEqual('staged', staged['memory_coverage']['status'])
        self.assertEqual(8, len(client.calls))
        self.assertEqual(8, len(staged['memory_coverage']['stages']))
        self.assertTrue(all(len(prompt) <= 95_000 for _, prompt in client.calls))
        self.assertTrue(all('ordinary evidence' in prompt for _, prompt in client.calls))
        self.assertEqual(2, sum('MIDDLE_GATE_REQUIRES_OPERATOR_REVIEW' in p for _, p in client.calls))
        _, evidence = _review_input(staged)
        self.assertIn('MIDDLE_GATE_REQUIRES_OPERATOR_REVIEW', evidence)
        self.assertLess(len(evidence), 95_000)
        self.assertTrue(stage_coverage_complete(staged['memory_coverage']))
        damaged = json.loads(json.dumps(staged['memory_coverage']))
        damaged['stages'].pop()
        self.assertFalse(stage_coverage_complete(damaged))
        self.assertEqual(self.context['projects'][0]['memories'][0]['excerpt'].count('ordinary evidence'), 2600)

    def test_verified_cache_reuse_and_changed_source_fail_closed(self):
        client = StageClient()
        stage_memories(self.context, self.roots, client,
                       ('gpt-5.6-terra', 'gpt-5.6-sol'), cache_dir=self.base / 'cache')
        second = StageClient()
        staged = stage_memories(self.context, self.roots, second,
                                ('gpt-5.6-terra', 'gpt-5.6-sol'), cache_dir=self.base / 'cache')
        self.assertEqual([], second.calls)
        self.assertTrue(all(row['cache_hit'] for row in staged['memory_coverage']['stages']))
        (self.base / 'two' / 'project_memories' / 'state.md').write_text('changed', encoding='utf-8')
        with self.assertRaises(ModelError):
            stage_memories(self.context, self.roots, StageClient(),
                           ('gpt-5.6-terra', 'gpt-5.6-sol'), cache_dir=self.base / 'cache')

    def test_hallucinated_quote_blocks_before_final_review(self):
        class BadClient(StageClient):
            def call(self, model, prompt, **kwargs):
                self.calls.append((model, prompt))
                return {'success': True, 'text': json.dumps({
                    'summary': 'unsupported', 'quotes': ['never present'], 'open_questions': []})}

        with self.assertRaises(ModelError):
            stage_memories(self.context, self.roots, BadClient(),
                           ('gpt-6-sol', 'gpt-6-luna'))

    def test_staged_evidence_supports_both_group_planning_routes(self):
        from governor_workbench.planning_llm import propose_plan
        from governor_workbench.route_b import run
        from tests.test_planning_llm import FakeClient
        from tests.test_route_b import Client, REVIEW, SAFE, PLAN

        base = dict(self.context, plan_ready=True, scope_hash='a'*64,
                    review_scope={'kind': 'group', 'id': 'whole'},
                    registry_projects=[{'id': 'one'}, {'id': 'two'}])
        old_stage = stage_memories(base, self.roots, StageClient(),
                                   ('gpt-5.6-terra', 'gpt-5.6-sol'))
        new_stage = stage_memories(base, self.roots, StageClient(),
                                   ('gpt-6-sol', 'gpt-6-luna'))
        old = FakeClient(PLAN)
        self.assertEqual(PLAN, propose_plan(old_stage, 'gpt-5.6-sol', old)['proposal'])
        new = Client([{'proposal': PLAN, 'risk': SAFE},
                      {'review': REVIEW, 'risk': SAFE}, {'review': REVIEW, 'risk': SAFE}])
        self.assertEqual(PLAN, run(new_stage, new, plan=True)['proposal'])
        self.assertTrue(all('MIDDLE_GATE_REQUIRES_OPERATOR_REVIEW' in call['prompt'] for call in old.calls))
        self.assertTrue(all('MIDDLE_GATE_REQUIRES_OPERATOR_REVIEW' in call[1] for call in new.calls))


if __name__ == '__main__':
    unittest.main()
