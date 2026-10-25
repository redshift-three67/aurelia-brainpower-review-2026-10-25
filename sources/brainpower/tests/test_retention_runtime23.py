import importlib.util
import json
from pathlib import Path
import types
import unittest
import tempfile
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]


def load(path):
    if not path.exists():
        return types.SimpleNamespace()
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class MaintenanceTests(unittest.TestCase):
    def setUp(self):
        self.m = load(ROOT/'artifacts/server-retention-runtime23.py')
        self.r = vars(load(ROOT/'artifacts/server-retention23.py'))
        self.assertTrue(callable(getattr(self.m, 'cycle', None)), 'maintenance cycle missing')
        self.rows = [dict(id=c*64, hostname='aureliaserver', tags=[tag],
                          time='2026-09-23T'+hour+':00:00Z') for c, tag, hour in
                     [('a', 'operations-cold', '18'), ('b', 'operations-cold', '20'),
                      ('c', 'preparation-synthetic', '19')]]
        self.calls = []

    def restic(self, label, *args):
        self.calls.append((label, args))
        if args[0] == 'snapshots': return json.dumps(self.rows)
        if label == 'policy_preview':
            return json.dumps([dict(host='aureliaserver', tags=['operations-cold'],
                                    keep=[self.rows[1]], remove=[self.rows[0]])])
        if args[0] == 'forget': self.rows = [r for r in self.rows if r['id'] not in args[1:]]
        return ''

    def test_prune_checks_and_restore_preserve_foreign_snapshot(self):
        restored = []
        result = self.m.cycle(self.r, self.restic, 'b'*64, lambda ident: restored.append(ident))
        self.assertEqual(result['plan']['remove'], ['a'*64])
        self.assertEqual(restored, ['b'*64])
        self.assertEqual([r['id'] for r in self.rows], ['b'*64, 'c'*64])
        self.assertIn(('prune', '--max-repack-size', '128M', '--max-unused', '10%'),
                      [args for _, args in self.calls])
        labels = [label for label, _ in self.calls]
        self.assertLess(labels.index('check_before'), labels.index('forget_reviewed_ids'))
        self.assertLess(labels.index('prune_bounded'), labels.index('check_after'))

    def test_failed_precheck_never_deletes(self):
        def failed(label, *args):
            if label == 'check_before': raise RuntimeError('bad_repository')
            return self.restic(label, *args)
        with self.assertRaisesRegex(RuntimeError, 'bad_repository'):
            self.m.cycle(self.r, failed, 'b'*64, lambda ident: None)
        self.assertFalse(self.calls)

    def test_drift_after_forget_prevents_prune(self):
        def drift(label, *args):
            if label == 'snapshots_after': self.rows.append(dict(self.rows[0], id='d'*64))
            return self.restic(label, *args)
        with self.assertRaisesRegex(ValueError, 'post_delete_snapshot_set_changed'):
            self.m.cycle(self.r, drift, 'b'*64, lambda ident: None)
        self.assertNotIn('prune_bounded', [label for label, _ in self.calls])

    def test_prune_cannot_change_snapshot_metadata(self):
        def drift(label, *args):
            if label == 'snapshots_after_prune': self.rows[1]['hostname'] = 'changed'
            return self.restic(label, *args)
        with self.assertRaisesRegex(ValueError, 'prune_snapshot_set_changed'):
            self.m.cycle(self.r, drift, 'b'*64, lambda ident: self.fail('restore after drift'))

    def test_restore_failure_propagates(self):
        def failed(ident): raise RuntimeError('restore_failed')
        with self.assertRaisesRegex(RuntimeError, 'restore_failed'):
            self.m.cycle(self.r, self.restic, 'b'*64, failed)

    def test_monitor_missing_failed_stale_and_valid(self):
        good = dict(ok=True, finished_at=1000)
        for state, unit, now, expected in [(None, 'success', 1100, 'missing'),
            (good, 'exit-code', 1100, 'failed'), (dict(good, ok=False), 'success', 1100, 'failed'),
            (good, 'success', 1000+36*3600, 'stale'), (good, 'success', 1100, 'healthy'),
            (dict(good, finished_at=float('nan')), 'success', 1100, 'invalid')]:
            with self.subTest(expected=expected):
                self.assertEqual(self.m.assess(state, unit, now)['level'], expected)

    def test_mount_cleanup_failure_preserves_workspace(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            h = dict(command=Mock(side_effect=RuntimeError('busy')), secure=Mock(), mount_guard=Mock())
            rt = dict(read_json=Mock(return_value=None))
            with patch.object(self.m, 'BASE', base), patch.object(self.m.os.path, 'ismount',
                side_effect=[False, True, True, False]), patch.object(self.m.shutil, 'rmtree') as remove:
                result = self.m.run(self.r, h, rt)
            self.assertFalse(result['ok'])
            self.assertFalse(result['temporary_mount_detached'])
            self.assertIn('retained_workspace', result)
            remove.assert_not_called()

    def test_failed_freshness_removes_only_own_unmounted_workspace(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory); unrelated = base/'unrelated'; unrelated.mkdir()
            h = dict(command=Mock(), secure=Mock(), mount_guard=Mock())
            with patch.object(self.m, 'BASE', base), patch.object(self.m.os.path, 'ismount', return_value=False):
                result = self.m.run(self.r, h, dict(read_json=Mock(return_value=None)))
            self.assertFalse(result['ok'])
            self.assertTrue(result['staging_removed'])
            h['command'].assert_not_called()
            self.assertEqual(list(base.iterdir()), [unrelated])

    def test_monitor_does_not_repeat_mail_within_hour_or_send_healthy_mail(self):
        rt = vars(load(ROOT/'artifacts/server-backup-runtime23.py'))
        with tempfile.TemporaryDirectory() as directory:
            state = Path(directory)
            result = types.SimpleNamespace(stdout='exit-code')
            with patch.object(self.m, 'STATE', state), patch.object(self.m.subprocess, 'run', return_value=result), \
                 patch.object(self.m, 'notify') as notify:
                self.assertEqual(self.m.watch(self.r, {}, rt, {}), 1)
                self.assertEqual(self.m.watch(self.r, {}, rt, {}), 1)
                notify.assert_called_once()
                result.stdout = 'success'
                rt['atomic_json'](state/'maintenance-latest.json', dict(ok=True, finished_at=self.m.time.time()))
                self.assertEqual(self.m.watch(self.r, {}, rt, {}), 0)
                notify.assert_called_once()


class InstallerTests(unittest.TestCase):
    def test_timer_installation_is_separate_from_activation(self):
        m = load(ROOT/'artifacts/server-retention-install23.py')
        self.assertTrue(hasattr(m, 'UNITS'), 'installer units missing')
        self.assertEqual(len(m.UNITS), 4)
        self.assertIn('01:00:00 UTC', m.UNITS['aurelia-retention23.timer'])
        self.assertIn('OnFailure=aurelia-retention-watch23.service', m.UNITS['aurelia-retention23.service'])
        self.assertIn('TimeoutStartSec=20min', m.UNITS['aurelia-retention23.service'])
        for content in m.UNITS.values():
            self.assertNotIn('ExecStartPost=', content)
            self.assertNotIn('enable', content)


if __name__ == '__main__': unittest.main()
