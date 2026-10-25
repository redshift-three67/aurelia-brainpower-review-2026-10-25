import importlib.util
from pathlib import Path
import unittest


class RetentionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec=importlib.util.spec_from_file_location('retention23',Path(__file__).resolve().parents[1]/'artifacts/server-retention23.py')
        cls.m=importlib.util.module_from_spec(spec);spec.loader.exec_module(cls.m)

    def snapshot(self,char,when='2026-09-23T20:00:00Z',tag='operations-cold'):
        return {'id':char*64,'time':when,'hostname':'aureliaserver','tags':[tag]}

    def case(self):
        old=self.snapshot('a','2026-09-23T19:00:00Z');new=self.snapshot('b');foreign=self.snapshot('c',tag='preparation-synthetic')
        preview=[{'host':'aureliaserver','tags':['operations-cold'],'keep':[new],'remove':[old]}]
        return [old,new,foreign],preview

    def test_only_reviewed_profile_candidates_returned(self):
        rows,preview=self.case()
        self.assertEqual(self.m.review(rows,preview,'b'*64),['a'*64])

    def test_latest_verified_may_never_be_removed(self):
        rows,preview=self.case();preview[0]['keep'],preview[0]['remove']=preview[0]['remove'],preview[0]['keep']
        with self.assertRaises(ValueError):self.m.review(rows,preview,'b'*64)

    def test_missing_duplicate_foreign_or_modified_snapshot_blocks(self):
        rows,preview=self.case()
        for changed in [[],preview+preview,[dict(preview[0],remove=[rows[2]])],
                        [dict(preview[0],remove=[dict(rows[0],time='2000-01-01T00:00:00Z')])],
                        [dict(preview[0],keep=preview[0]['keep']+preview[0]['remove'])]]:
            with self.assertRaises(ValueError):self.m.review(rows,changed,'b'*64)

    def test_newer_unverified_snapshot_blocks_deletion(self):
        rows,preview=self.case();rows.append(self.snapshot('d','2026-09-23T21:00:00Z'))
        preview[0]['keep'].append(rows[-1])
        with self.assertRaises(ValueError):self.m.review(rows,preview,'b'*64)

    def test_stale_failed_or_mismatched_success_is_rejected(self):
        good={'ok':True,'snapshot_id':'b'*64,'captured_at':1000}
        success={'snapshot_id':'b'*64,'captured_at':1000}
        self.assertEqual(self.m.verified_snapshot(good,success,1100),'b'*64)
        for latest,stamp,now in [(dict(good,ok=False),success,1100),(good,success,1000+8*3600),
                                  (good,dict(success,snapshot_id='a'*64),1100),(good,success,1)]:
            with self.assertRaises(ValueError):self.m.verified_snapshot(latest,stamp,now)

    def test_source_drift_blocks_before_forget(self):
        rows,preview=self.case();calls=[]
        def restic(label,*args):
            calls.append(args)
            if label=='snapshots_before':return self.m.json.dumps(rows)
            if label=='policy_preview':return self.m.json.dumps(preview)
            if label=='snapshots_recheck':return '[]'
            return ''
        approved={'protected_snapshot':'b'*64,'snapshot_set_hash':self.m.signature(self.m.index(rows)),
                  'remove':['a'*64],'keep':['b'*64,'c'*64]}
        with self.assertRaisesRegex(ValueError,'repository_drift'):self.m.execute(restic,'b'*64,True,approved)
        self.assertFalse(any(args and args[0]=='forget' and '--dry-run' not in args for args in calls))

    def test_preview_never_issues_real_forget(self):
        rows,preview=self.case();calls=[]
        def restic(label,*args):
            calls.append(args)
            return self.m.json.dumps(preview if label=='policy_preview' else rows)
        plan=self.m.execute(restic,'b'*64,False)
        self.assertEqual(plan['remove'],['a'*64])
        self.assertFalse(any(args[0]=='forget' and '--dry-run' not in args for args in calls))

    def test_apply_removes_only_approved_ids_and_preserves_foreign_profile(self):
        rows,preview=self.case();calls=[]
        def restic(label,*args):
            calls.append(args)
            if label=='policy_preview':return self.m.json.dumps(preview)
            if label=='snapshots_after':return self.m.json.dumps(rows[1:])
            if label=='forget_reviewed_ids':return ''
            return self.m.json.dumps(rows)
        plan=self.m.execute(restic,'b'*64,False)
        self.m.execute(restic,'b'*64,True,plan)
        self.assertEqual([args for args in calls if args[0]=='forget' and '--dry-run' not in args],[('forget','a'*64)])
