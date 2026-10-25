import importlib.util
from pathlib import Path
import unittest


class PrepareTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location('prepare23', Path(__file__).resolve().parents[1] / 'artifacts/server-backup-prepare23.py')
        cls.m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.m)

    def test_prior_snapshot_must_match_exactly(self):
        self.m.verify_prior([{'id': self.m.PRIOR_SNAPSHOT}])
        for rows in ([], [{'id': 'a'*64}], [{'id': self.m.PRIOR_SNAPSHOT}]*2):
            with self.assertRaises(ValueError): self.m.verify_prior(rows)

    def test_existing_repository_cannot_be_initialized(self):
        import tempfile
        with tempfile.TemporaryDirectory() as root:
            target = Path(root)/'repository'
            self.m.new_repository(target)
            (target/'keep').write_text('existing')
            with self.assertRaises(FileExistsError): self.m.new_repository(target)
            self.assertEqual((target/'keep').read_text(), 'existing')

    def test_candidate_does_not_enable_backup_or_claim_rto(self):
        value = self.m.candidate('a'*64, '/protected/key')
        self.assertFalse(value['automatic_backup_enabled'])
        self.assertEqual(value['rto_target_hours'], 12)
        self.assertFalse(value['rto_demonstrated'])
        self.assertIsNone(value['rpo_target_hours'])
        with self.assertRaises(ValueError): self.m.candidate('wrong', '/protected/key')
