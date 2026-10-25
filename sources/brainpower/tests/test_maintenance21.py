import importlib.util
from pathlib import Path
import unittest


class MaintenanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec=importlib.util.spec_from_file_location('maint',Path(__file__).resolve().parents[1]/'artifacts/server-maintenance21.py')
        cls.m=importlib.util.module_from_spec(spec); spec.loader.exec_module(cls.m)

    def test_only_random_restrict_marker_is_ignored(self):
        self.assertEqual(self.m.normalize_dump(b'\\restrict abc\nSELECT 1;\n\\unrestrict abc\n'),b'SELECT 1;\n')
        self.assertNotEqual(self.m.normalize_dump(b'SELECT 1;\n'),self.m.normalize_dump(b'SELECT 2;\n'))
        self.assertEqual(self.m.normalize_dump(b'\\restrict bad token\n'),b'\\restrict bad token\n')

    def test_database_inventory_rejects_closed_or_excess(self):
        self.assertEqual(self.m.databases([{'name':'postgres','allow':True}]),['postgres'])
        for rows in ([],[{'name':'x','allow':False}],[{'name':'x','allow':True}]*17,[{'name':'-d attack','allow':True}]):
            with self.assertRaises(ValueError): self.m.databases(rows)

    def test_socket_only_configuration(self):
        config=self.m.configuration(Path('/tmp/lab/source'),Path('/tmp/lab/socket'),Path('/tmp/lab/auth'))
        self.assertIn("listen_addresses = ''",config)
        self.assertIn("shared_preload_libraries = ''",config)
        self.assertIn("archive_mode = off",config)
        self.assertIn("ssl = off",config)

    def test_recovery_role_collision_rejected(self):
        with self.assertRaises(ValueError): self.m.roles(['postgres',self.m.ADMIN])
        self.m.roles(['postgres'])

    def test_only_default_builtin_grantor_is_normalized(self):
        row=dict(role='pg_read_all_settings',member='pg_monitor',grantor='postgres',admin_option=False,inherit_option=True,set_option=True)
        target=dict(row,grantor=self.m.ADMIN)
        self.assertEqual(self.m.memberships([row],'postgres'),self.m.memberships([target],self.m.ADMIN))
        changed=dict(target,admin_option=True)
        self.assertNotEqual(self.m.memberships([row],'postgres'),self.m.memberships([changed],self.m.ADMIN))
        custom=dict(row,role='custom_role')
        self.assertNotEqual(self.m.memberships([custom],'postgres'),self.m.memberships([dict(custom,grantor=self.m.ADMIN)],self.m.ADMIN))
