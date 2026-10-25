import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch


class RuntimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec=importlib.util.spec_from_file_location('runtime23',Path(__file__).resolve().parents[1]/'artifacts/server-backup-runtime23.py')
        cls.m=importlib.util.module_from_spec(spec);spec.loader.exec_module(cls.m)

    def test_age_boundaries_and_future(self):
        m=self.m
        for hours,expected in [(0,'healthy'),(7.99,'healthy'),(8,'warning'),(11,'critical'),(12,'rpo_exceeded')]:
            self.assertEqual(m.assess({'captured_at':1000},None,1000+hours*3600)['level'],expected)
        self.assertEqual(m.assess(None,None,1000)['level'],'missing')
        self.assertEqual(m.assess({'captured_at':2000},None,1000)['level'],'invalid')

    def test_failed_run_reported_even_with_recent_good_backup(self):
        self.assertEqual(self.m.assess({'captured_at':1000},{'ok':False},1100)['level'],'failed')
        self.assertEqual(self.m.assess({'captured_at':1000},{'ok':False},1000+12*3600)['level'],'rpo_exceeded')

    def test_success_requires_all_integrity_and_cleanup_flags(self):
        good={'status':'cold_operations_restore_verified','snapshot_id':'a'*64,
              **{key:True for key in self.m.SUCCESS_FLAGS}}
        self.assertTrue(self.m.is_success(good))
        for key in self.m.SUCCESS_FLAGS:
            bad=dict(good);bad[key]=False
            self.assertFalse(self.m.is_success(bad),key)
        self.assertFalse(self.m.is_success(dict(good,snapshot_id='bad')))

    def test_failed_attempt_preserves_last_good_timestamp(self):
        with tempfile.TemporaryDirectory() as directory:
            base=Path(directory)
            self.m.atomic_json(base/'success.json',{'captured_at':1,'snapshot_id':'a'*64})
            self.m.record(base,{'ok':False,'captured_at':2})
            self.assertEqual(self.m.read_json(base/'success.json')['captured_at'],1)
            self.assertFalse(self.m.read_json(base/'latest.json')['ok'])

    def test_notification_attempt_is_throttled_but_escalation_immediate(self):
        self.assertFalse(self.m.should_alert({'level':'healthy'},None,1000))
        self.assertTrue(self.m.should_alert({'level':'critical'},{'level':'warning','attempted_at':999},1000))
        self.assertFalse(self.m.should_alert({'level':'warning'},{'level':'warning','attempted_at':999},1000))
        self.assertTrue(self.m.should_alert({'level':'warning'},{'level':'warning','attempted_at':1},3601))

    def test_unparseable_state_is_not_silently_missing(self):
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/'bad.json';p.write_text('{')
            with self.assertRaises(ValueError): self.m.read_json(p)

    def test_failed_backup_keeps_good_state_and_removes_own_staging(self):
        with tempfile.TemporaryDirectory() as directory:
            base=Path(directory);state=base/'state';state.mkdir()
            self.m.atomic_json(state/'success.json',{'captured_at':1,'snapshot_id':'a'*64})
            def command(args,*a):
                if 'postgresql@16-main.service' in args:return 'pg-stopped'
                if 'aurelia-backup-files.timer' in args:return 'ActiveState=inactive\nUnitFileState=disabled'
                return ''
            h={'command':Mock(side_effect=command),'secure':Mock(),'mount_guard':Mock(),'SOURCE':'fixture'}
            ops={'ENV':{},'DATA':'fixture','REPO':'fixture','SCOPES':[],
                 'require_stopped':Mock(),'roundtrip':Mock(side_effect=ValueError('backup_failed'))}
            with patch.object(self.m,'BASE',base),patch.object(self.m,'STATE',state),patch.object(self.m.os.path,'ismount',return_value=False):
                self.assertEqual(self.m.run(ops,h,{}),1)
            self.assertEqual(self.m.read_json(state/'success.json')['captured_at'],1)
            self.assertTrue(self.m.read_json(state/'latest.json')['staging_removed'])
            self.assertEqual(list(base.glob('runtime-*')),[])

    def test_failed_unmount_never_deletes_workspace_or_records_success(self):
        with tempfile.TemporaryDirectory() as directory:
            base=Path(directory);state=base/'state';state.mkdir()
            def command(args,*a):
                if args[0]=='umount':raise RuntimeError('busy')
                if 'postgresql@16-main.service' in args:return 'pg-stopped'
                if 'aurelia-backup-files.timer' in args:return 'ActiveState=inactive\nUnitFileState=disabled'
                return ''
            h={'command':Mock(side_effect=command),'secure':Mock(),'mount_guard':Mock(),'SOURCE':'fixture'}
            ops={'ENV':{},'DATA':'fixture','REPO':'fixture','SCOPES':[],
                 'require_stopped':Mock(),'roundtrip':Mock(side_effect=ValueError('backup_failed'))}
            with patch.object(self.m,'BASE',base),patch.object(self.m,'STATE',state),patch.object(self.m.os.path,'ismount',side_effect=[False,True,True,False]),patch.object(self.m.shutil,'rmtree') as remove:
                self.assertEqual(self.m.run(ops,h,{}),1)
                remove.assert_not_called()
            self.assertIsNone(self.m.read_json(state/'success.json'))
            self.assertIn('retained_workspace',self.m.read_json(state/'latest.json'))

    def test_complete_roundtrip_promotes_success_only_after_cleanup(self):
        with tempfile.TemporaryDirectory() as directory:
            base=Path(directory);state=base/'state';state.mkdir()
            def command(args,*a):
                if 'postgresql@16-main.service' in args:return 'pg-stopped'
                if 'aurelia-backup-files.timer' in args:return 'ActiveState=inactive\nUnitFileState=disabled'
                return ''
            h={'command':Mock(side_effect=command),'secure':Mock(),'mount_guard':Mock(),'SOURCE':'fixture'}
            proof={key:True for key in self.m.SUCCESS_FLAGS};proof['snapshot_id']='b'*64
            ops={'ENV':{},'DATA':'fixture','REPO':'fixture','SCOPES':[],
                 'require_stopped':Mock(),'roundtrip':Mock(return_value=proof)}
            with patch.object(self.m,'BASE',base),patch.object(self.m,'STATE',state),patch.object(self.m.os.path,'ismount',return_value=False):
                self.assertEqual(self.m.run(ops,h,{}),0)
            self.assertEqual(self.m.read_json(state/'success.json')['snapshot_id'],'b'*64)
            self.assertTrue(self.m.read_json(state/'latest.json')['staging_removed'])
            self.assertEqual(list(base.glob('runtime-*')),[])
