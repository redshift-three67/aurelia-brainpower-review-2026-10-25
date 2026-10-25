"""Registry tests use only temporary directories and a temporary journal."""
from pathlib import Path
import os
import sqlite3
import tempfile
import unittest
from governor_workbench.store import Store


class RegistryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.store = Store(self.root / 'journal.sqlite')

    def registry(self, configured=(), **kwargs):
        from governor_workbench.registry import Registry
        return Registry(self.store, configured, **kwargs)

    def directory(self, name):
        path = self.root / name
        path.mkdir(parents=True)
        return str(path)

    def test_module_exists(self):
        import importlib.util
        self.assertIsNotNone(importlib.util.find_spec('governor_workbench.registry'))

    def test_known_migration_is_durable_and_preserves_sources(self):
        ids = ('aurelia', 'radiworks', 'modul_templates', 'radi144', 'morphic_v1')
        config = [dict(id=i, name=i, path=self.directory(i), sources=['existing.md']) for i in ids]
        reg = self.registry(config, legacy_egress_authorized=True)
        projects = reg.list_projects()
        self.assertEqual({p['id'] for p in projects}, set(ids))
        self.assertEqual({p['group_id'] for p in projects}, {'aurelia-integration'})
        self.assertEqual({p['id']: p['role'] for p in projects}, dict(zip(ids, ('parent','module','contracts','module','module'))))
        self.assertTrue(all(p['model_egress'] for p in projects))
        self.assertEqual(projects[0]['source_config']['sources'], ['existing.md'])
        self.assertEqual(self.registry(config).list_projects(), projects)

    def test_known_ids_do_not_grant_egress_on_new_installation(self):
        ids = ('aurelia', 'radiworks', 'modul_templates', 'radi144', 'morphic_v1')
        reg = self.registry([dict(id=i, name=i, path=self.directory(i)) for i in ids])
        self.assertTrue(all(not p['model_egress'] for p in reg.list_projects()))

    def test_only_one_parent_in_group_even_after_archive(self):
        reg = self.registry()
        p = reg.register('One', self.directory('one'))
        p2 = reg.register('Two', self.directory('two'))
        group = reg.create_group('Group')
        reg.assign(p['id'], group['id'], 'parent')
        reg.archive(p['id'])
        with self.assertRaises(ValueError): reg.assign(p2['id'], group['id'], 'parent')

    def test_registry_counts_remain_bounded_after_archive(self):
        reg = self.registry()
        for n in range(50):
            p = reg.register(str(n), self.directory(str(n)))
            reg.archive(p['id'])
            reg.create_group(str(n))
        with self.assertRaises(ValueError): reg.register('Extra', self.directory('extra'))
        with self.assertRaises(ValueError): reg.create_group('Extra')

    def test_unknown_config_remains_single_and_can_be_missing(self):
        reg = self.registry([dict(id='demo', name='Demo', path=str(self.root/'missing'))])
        p = reg.list_projects()[0]
        self.assertIsNone(p['group_id'])
        self.assertFalse(p['model_egress'])
        self.assertEqual(reg.list_groups(), [])

    def test_register_and_restart_preserve_fields_without_filesystem_writes(self):
        path = self.directory('project')
        reg = self.registry()
        p = reg.register(' Project ', path, requirements='Do the thing')
        self.assertEqual(p['name'], 'Project')
        self.assertEqual(p['requirements'], 'Do the thing')
        self.assertFalse(p['model_egress'])
        self.assertEqual(p['memory_provisioning'], 'pending')
        self.assertEqual(list(Path(path).iterdir()), [])
        self.assertEqual(self.registry().list_projects(), [p])

    def test_alias_and_nested_paths_rejected_even_after_archive(self):
        reg = self.registry()
        parent = self.directory('parent')
        child = self.directory('parent/child')
        p = reg.register('One', child)
        reg.archive(p['id'])
        for path in (child, str(Path(child)/'..'/'child'), parent):
            with self.subTest(path=path), self.assertRaises(ValueError):
                reg.register('Two', path)
        self.assertEqual(len(reg.list_projects()), 1)

    def test_descendant_rejected(self):
        reg = self.registry()
        parent = self.directory('parent')
        child = self.directory('parent/child')
        reg.register('One', parent)
        with self.assertRaises(ValueError):
            reg.register('Two', child)

    def test_validation_and_explicit_egress(self):
        reg = self.registry()
        path = self.directory('valid')
        for kwargs in (dict(name=''), dict(name='x'*81), dict(path='relative'), dict(path=str(self.root/'missing')), dict(model_egress='true'), dict(requirements=[])):
            args = dict(name='Project', path=path)
            args.update(kwargs)
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                reg.register(**args)
        self.assertTrue(reg.register('Valid', path, model_egress=True)['model_egress'])

    def test_membership_is_permanent_and_archiving_retains_it(self):
        reg = self.registry()
        p = reg.register('One', self.directory('one'))
        group = reg.create_group('Group')
        other = reg.create_group('Other')
        assigned = reg.assign(p['id'], group['id'], 'parent')
        self.assertEqual(assigned['group_id'], group['id'])
        with self.assertRaises(ValueError): reg.assign(p['id'], other['id'])
        with self.assertRaises(ValueError): reg.assign(p['id'], group['id'], 'module')
        archived = reg.archive(p['id'])
        self.assertEqual(archived['group_id'], group['id'])
        self.assertEqual(reg.list_projects(include_archived=False), [])
        self.assertEqual(reg.list_groups()[0]['members'][0]['project_id'], p['id'])
        with self.store.db() as c:
            with self.assertRaises(sqlite3.IntegrityError):
                c.execute('DELETE FROM reg_memberships WHERE project_id=?', (p['id'],))

    def test_invalid_assignment_does_not_change_registry(self):
        reg = self.registry()
        p = reg.register('One', self.directory('one'))
        g = reg.create_group('Group')
        for project, group, role in (('missing',g['id'],'member'),(p['id'],'missing','member'),(p['id'],g['id'],'admin')):
            with self.assertRaises(ValueError): reg.assign(project, group, role)
        self.assertIsNone(reg.list_projects()[0]['group_id'])
        for name in ('', 'Group', ' group ', 'x'*81):
            with self.assertRaises(ValueError): reg.create_group(name)

    @unittest.skipUnless(os.name == 'nt', 'Windows case-insensitive path rules')
    def test_windows_case_alias_rejected(self):
        reg = self.registry()
        path = self.directory('MixedCase')
        reg.register('One', path)
        with self.assertRaises(ValueError):
            reg.register('Two', path.upper())

    def test_migration_failure_rolls_back_all_rows_and_can_retry(self):
        path = self.directory('one')
        config = [dict(id='one', name='One', path=path), dict(id='two', name='Two', path=path)]
        with self.assertRaises(ValueError): self.registry(config)
        self.assertNotIn('registry_migration_v1', self.store.settings())
        reg = self.registry(config[:1])
        self.assertEqual([p['id'] for p in reg.list_projects()], ['one'])

    def test_constructor_does_not_interrupt_existing_job(self):
        job = self.store.create_job('refresh', None)
        self.registry()
        self.assertEqual(self.store.job(job['id'])['status'], 'queued')

    def test_database_rejects_membership_role_update(self):
        reg = self.registry()
        p = reg.register('One', self.directory('one'))
        group = reg.create_group('Group')
        reg.assign(p['id'], group['id'])
        with self.store.db() as c:
            with self.assertRaises(sqlite3.IntegrityError):
                c.execute("UPDATE reg_memberships SET role='parent' WHERE project_id=?", (p['id'],))

    def test_malformed_ids_raise_validation_errors_before_database_binding(self):
        reg = self.registry()
        p = reg.register('One', self.directory('one'))
        group = reg.create_group('Group')
        for value in ([], {}, None, 42, '', ' ', 'x'*65):
            with self.subTest(value=value):
                with self.assertRaises(ValueError): reg.archive(value)
                with self.assertRaises(ValueError): reg.assign(value, group['id'])
                with self.assertRaises(ValueError): reg.assign(p['id'], value)

    def test_policy_updates_are_explicit_partial_and_persisted(self):
        reg = self.registry()
        self.assertTrue(callable(getattr(reg, 'set_project_policy', None)))
        p = reg.register('One', self.directory('one'), requirements='Initial')
        granted = reg.set_project_policy(p['id'], model_egress=True)
        self.assertTrue(granted['model_egress'])
        self.assertEqual(granted['requirements'], 'Initial')
        changed = reg.set_project_policy(p['id'], requirements='Updated')
        self.assertTrue(changed['model_egress'])
        self.assertEqual(self.registry().list_projects(), [changed])
        revoked = reg.set_project_policy(p['id'], model_egress=False, requirements='')
        self.assertFalse(revoked['model_egress'])
        self.assertEqual(revoked['requirements'], '')
        for kwargs in ({}, {'model_egress': None}, {'model_egress': 1}, {'requirements': None}, {'requirements': 'x'*4001}):
            with self.assertRaises(ValueError): reg.set_project_policy(p['id'], **kwargs)
        self.assertEqual(reg.list_projects(), [revoked])


if __name__ == '__main__':
    unittest.main()
