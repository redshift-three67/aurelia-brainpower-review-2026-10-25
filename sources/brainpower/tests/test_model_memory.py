"""Full, source-bound project memories reach both advisory model routes."""
import hashlib
from pathlib import Path
import tempfile
import unittest

from governor_workbench.evidence import MemoryConflict
from governor_workbench.llm import ModelError, hybrid_review
from governor_workbench.route_b import run
from tests.test_llm import ReviewClient
from tests.test_route_b import Client, REVIEW, SAFE


class ModelMemoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        folder = self.root / 'one' / 'project_memories'
        folder.mkdir(parents=True)
        self.memory = folder / 'state.md'
        self.roots = [{'id': 'one', 'path': str(self.root / 'one')}]

    def context(self, content):
        self.memory.write_text(content, encoding='utf-8')
        raw = self.memory.read_bytes()
        item = dict(name='state.md', sha256=hashlib.sha256(raw).hexdigest(),
                    size=len(raw), excerpt='opening and ending only', truncated=True)
        return dict(projects=[dict(id='one', memories=[item])],
                    limits=['Memory excerpts are partial; absence is not proof. Untracked source trees not fully scanned.'])

    def test_hidden_middle_reaches_both_model_routes_with_full_coverage(self):
        from governor_workbench.model_memory import complete_memories

        marker = 'MIDDLE_GATE_REQUIRES_SEPARATE_OPERATOR_REVIEW'
        context = self.context('\n'.join(['opening'] + ['ordinary'] * 40 + [marker]
                                         + ['ordinary'] * 40 + ['ending']))
        full = complete_memories(context, self.roots)
        self.assertNotIn(marker, context['projects'][0]['memories'][0]['excerpt'])
        self.assertIn(marker, full['projects'][0]['memories'][0]['excerpt'])
        self.assertFalse(full['projects'][0]['memories'][0]['truncated'])
        self.assertEqual('full', full['memory_coverage']['status'])
        self.assertEqual(1, len(full['memory_coverage']['files']))

        old = ReviewClient()
        hybrid_review(full, 'gpt-5.6-sol', old)
        new = Client([dict(plan=dict(summary='Inspect', steps=['Review'], blockers=[]), risk=SAFE),
                      dict(review=REVIEW, risk=SAFE)])
        run(full, new)
        self.assertEqual(2, len(old.calls))
        self.assertEqual(2, len(new.calls))
        for _, prompt in old.calls:
            self.assertIn(marker, prompt)
        for _, prompt, _ in new.calls:
            self.assertIn(marker, prompt)
        self.assertIn('Untracked source trees are not fully scanned', full['limits'][0])

    def test_changed_memory_is_rejected_before_any_model_use(self):
        from governor_workbench.model_memory import complete_memories

        context = self.context('original')
        self.memory.write_text('changed after observation', encoding='utf-8')
        with self.assertRaises(MemoryConflict):
            complete_memories(context, self.roots)

    def test_new_unobserved_memory_file_blocks_instead_of_claiming_full_coverage(self):
        from governor_workbench.model_memory import complete_memories

        context = self.context('known')
        (self.memory.parent / 'later.md').write_text('new gate', encoding='utf-8')
        with self.assertRaises(MemoryConflict):
            complete_memories(context, self.roots)

    def test_missing_memory_folder_is_explicitly_not_full(self):
        from governor_workbench.model_memory import complete_memories

        self.memory.parent.rmdir()
        context = dict(projects=[dict(id='one', memories=[])], limits=[])
        result = complete_memories(context, self.roots)
        self.assertEqual('missing', result['memory_coverage']['status'])
        self.assertEqual([], result['memory_coverage']['files'])

    def test_oversize_full_context_blocks_both_routes_before_dispatch(self):
        from governor_workbench.model_memory import complete_memories

        full = complete_memories(self.context('x' * 100_000), self.roots)
        old = ReviewClient()
        new = Client([])
        with self.assertRaises(ModelError):
            hybrid_review(full, 'gpt-5.6-sol', old)
        with self.assertRaises(ModelError):
            run(full, new)
        self.assertEqual([], old.calls)
        self.assertEqual([], new.calls)


if __name__ == '__main__':
    unittest.main()
