import threading
import unittest


class RegistryFixture:
    def __init__(self):
        self.groups = [{'id': 'g', 'archived': False}]
        self.projects = [{'id': 'member', 'group_id': 'g', 'archived': False},
                         {'id': 'single', 'group_id': None, 'archived': False}]

    def list_groups(self): return list(self.groups)
    def list_projects(self): return list(self.projects)


class ScopeMonitorTests(unittest.TestCase):
    def setUp(self):
        from governor_workbench.scope_monitor import ScopeMonitor
        self.registry = RegistryFixture()
        self.calls = []
        def observe(kind, key):
            self.calls.append((kind, key))
            return {'scope_hash': 'hash-' + key, 'plan_ready': True,
                    'intake': [{'project_id': key, 'intake_accepted': True}]}
        self.observe = observe
        self.monitor = ScopeMonitor(self.registry, observe)

    def test_observes_one_scope_per_tick_in_fair_rotation(self):
        for count in range(5):
            self.monitor.tick()
            self.assertEqual(len(self.calls), count + 1)
        self.assertEqual(self.calls, [('group','g'), ('project','single'), ('group','g'),
                                      ('project','single'), ('group','g')])
        state = self.monitor.state()
        self.assertEqual([(x['kind'], x['id']) for x in state], [('group','g'), ('project','single')])
        self.assertTrue(all(not row['stale'] and row['error'] is None for row in state))

    def test_failure_keeps_last_known_data_and_sanitizes_error(self):
        self.monitor.tick()
        before = self.monitor.state()[0]
        def fail(kind, key): raise ValueError('secret token and private path')
        self.monitor.observe_callback = fail
        self.monitor.tick()
        self.monitor.tick()
        after = self.monitor.state()[0]
        self.assertEqual(after['scope_hash'], before['scope_hash'])
        self.assertEqual(after['observed_at'], before['observed_at'])
        self.assertTrue(after['stale'])
        self.assertTrue(after['error'])
        self.assertNotIn('secret', str(after))

    def test_archived_member_does_not_remove_group_but_archived_scopes_are_skipped(self):
        self.registry.projects[0]['archived'] = True
        self.registry.projects.append({'id':'archived', 'group_id':None, 'archived':True})
        self.registry.groups.append({'id':'old', 'archived':True})
        def observe(kind, key):
            if kind == 'group': raise ValueError('Missing member')
            return self.observe(kind, key)
        self.monitor.observe_callback = observe
        self.monitor.tick()
        self.assertEqual(self.monitor.state()[0]['id'], 'g')
        self.assertTrue(self.monitor.state()[0]['error'])
        self.assertEqual(len(self.monitor.state()), 2)

    def test_new_scope_and_membership_changes_preserve_fairness_without_duplicates(self):
        self.monitor.tick()
        self.registry.groups.append({'id':'new', 'archived':False})
        self.registry.projects[1]['group_id'] = 'new'
        self.registry.projects.append({'id':'fresh', 'group_id':None, 'archived':False})
        for _ in range(4): self.monitor.tick()
        self.assertIn(('group','new'), self.calls)
        self.assertIn(('project','fresh'), self.calls)
        self.assertNotIn(('project','single'), self.calls)
        self.assertEqual([row['id'] for row in self.monitor.state()], ['g','new','fresh'])

    def test_concurrent_tick_skips_and_state_does_not_wait_for_callback(self):
        entered = threading.Event()
        release = threading.Event()
        def observe(kind, key):
            entered.set()
            release.wait(3)
            return self.observe(kind, key)
        self.monitor.observe_callback = observe
        thread = threading.Thread(target=self.monitor.tick)
        thread.start()
        try:
            self.assertTrue(entered.wait(1))
            self.assertIsNone(self.monitor.tick())
            self.assertEqual(len(self.monitor.state()), 2)
        finally:
            release.set()
            thread.join(3)
        self.assertFalse(thread.is_alive())
        self.assertEqual(len(self.calls), 1)

    def test_state_is_copy_and_catalog_is_bounded(self):
        self.registry.groups = [{'id':str(i), 'archived':False} for i in range(120)]
        self.monitor.tick()
        state = self.monitor.state()
        self.assertEqual(len(state), 100)
        state[0]['intake'][0]['project_id'] = 'tampered'
        self.assertNotEqual(self.monitor.state()[0]['intake'][0]['project_id'], 'tampered')

    def test_callback_receives_only_scope_identity_and_no_model_options(self):
        self.monitor.tick()
        self.assertEqual(self.calls, [('group','g')])

    def test_catalog_failure_preserves_records_and_recovery_clears_error(self):
        from unittest.mock import patch
        self.monitor.tick()
        before = self.monitor.state()[0]
        with patch.object(self.registry, 'list_groups', side_effect=RuntimeError('private value')):
            self.assertIsNone(self.monitor.tick())
        after = self.monitor.state()[0]
        self.assertEqual(after['scope_hash'], before['scope_hash'])
        self.assertTrue(after['stale'])
        self.assertNotIn('private value', str(after))
        self.monitor.tick()
        self.monitor.tick()
        self.assertFalse(self.monitor.state()[0]['stale'])
        self.assertIsNone(self.monitor.state()[0]['error'])

    def test_empty_registry_and_malformed_callback_are_safe(self):
        self.monitor.observe_callback = lambda kind, key: {'scope_hash': 'bad'}
        self.assertTrue(self.monitor.tick()['error'])
        self.registry.groups = []
        self.registry.projects = []
        self.assertIsNone(self.monitor.tick())
        self.assertEqual(self.monitor.state(), [])
