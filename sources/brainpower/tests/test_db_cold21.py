import importlib.util
import io
from pathlib import Path
import tarfile
import tempfile
import unittest


class ColdBackupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location('cold', Path(__file__).resolve().parents[1]/'artifacts/server-db-backup21.py')
        cls.m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.m)

    def test_manifest_detects_content_change(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d); (p/'a').write_bytes(b'abc')
            before=self.m.tree(p)
            (p/'a').write_bytes(b'abd')
            self.assertNotEqual(before,self.m.tree(p))

    def test_size_limit_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d); (p/'a').write_bytes(b'abc')
            with self.assertRaises(ValueError): self.m.tree(p,byte_limit=2)

    def test_archive_rejects_escape_and_links(self):
        for name,kind in [('../escape',tarfile.REGTYPE),('var/lib/postgresql/16/main/link',tarfile.SYMTYPE),('/absolute',tarfile.REGTYPE)]:
            with tempfile.TemporaryDirectory() as d:
                p=Path(d)/'test.tar'
                with tarfile.open(p,'w') as t:
                    info=tarfile.TarInfo(name); info.type=kind; info.linkname='/etc/shadow' if kind==tarfile.SYMTYPE else ''
                    t.addfile(info,io.BytesIO(b''))
                with self.assertRaises(ValueError): self.m.cluster_members(p)

    def test_archive_requires_cluster(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'test.tar'
            with tarfile.open(p,'w'): pass
            with self.assertRaises(ValueError): self.m.cluster_members(p)

    def test_only_cluster_members_selected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'test.tar'
            with tarfile.open(p,'w') as t:
                for name in ['var/lib/postgresql/16/main','etc/postgresql']:
                    info=tarfile.TarInfo(name); info.type=tarfile.DIRTYPE; t.addfile(info)
            self.assertEqual(self.m.cluster_members(p),['var/lib/postgresql/16/main'])

    def test_checksum_failure_not_accepted(self):
        with self.assertRaises(ValueError): self.m.checksum_summary('Bad checksums: 1\nBlocks scanned: 20\nData checksum version: 1\n')
        with self.assertRaises(ValueError): self.m.checksum_summary('unrecognized')
