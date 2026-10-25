"""One combined metadata read; exact-root and incomplete-evidence guards."""
from pathlib import Path
import unittest
from unittest.mock import patch
from governor_workbench.evidence import Observer

class GitObservationBatchTests(unittest.TestCase):
    def test_metadata_uses_at_most_three_git_processes(self):
        observer=Observer({'git_interval':60,'projects':[]});root=Path.cwd().resolve()
        def git(folder,args):
            if args==['rev-parse','--show-toplevel']:return 0,str(root),''
            if args[0]=='status':return 0,'# branch.oid '+'a'*40+'\0# branch.head main\0',''
            if args[0]=='ls-tree':
                self.assertIn('a'*40,args)
                return 0,'',''
            self.fail('Redundant Git subprocess: '+repr(args))
        with patch.object(observer,'git',side_effect=git) as calls:result=observer.git_state(root,True)
        self.assertFalse(result['incomplete']);self.assertEqual('main',result['branch'])
        self.assertEqual('',result['git_status']);self.assertLessEqual(calls.call_count,3)

    def test_invalid_root_does_not_start_metadata_queries(self):
        observer=Observer({'git_interval':60,'projects':[]})
        with patch.object(observer,'git',return_value=(1,'','not a root')) as git:result=observer.git_state(Path.cwd(),True)
        self.assertTrue(result['incomplete']);self.assertEqual(1,git.call_count)

    def test_failed_status_keeps_observation_incomplete(self):
        observer=Observer({'git_interval':60,'projects':[]});root=Path.cwd().resolve()
        def git(folder,args):
            if args==['rev-parse','--show-toplevel']:return 0,str(root),''
            return 1,'','injected status failure'
        with patch.object(observer,'git',side_effect=git):result=observer.git_state(root,True)
        self.assertTrue(result['incomplete']);self.assertIn('injected status failure',result['error'])

    def test_force_refresh_reuses_only_immutable_commit_reads(self):
        observer=Observer({'git_interval':60,'projects':[]});root=Path.cwd().resolve();head=['a'*40]
        def git(folder,args):
            if args==['rev-parse','--show-toplevel']:return 0,str(root),''
            if args[0]=='status':return 0,'# branch.oid '+head[0]+'\0# branch.head main\0',''
            if args[0]=='ls-tree':return 0,'',''
            self.fail('Unexpected command')
        with patch.object(observer,'git',side_effect=git) as calls:
            observer.git_state(root,True);calls.reset_mock()
            observer.git_state(root,True)
            self.assertEqual(['rev-parse','status'],[c.args[1][0] for c in calls.call_args_list])
            head[0]='b'*40;calls.reset_mock();observer.git_state(root,True)
            self.assertIn('ls-tree',[c.args[1][0] for c in calls.call_args_list])

    def test_failed_commit_content_is_retried_and_index_never_cached(self):
        from governor_workbench.evidence import digest
        observer=Observer({'git_interval':60,'projects':[]});root=Path.cwd().resolve();attempt=[0]
        def git(folder,args):
            if args==['rev-parse','--show-toplevel']:return 0,str(root),''
            if args[0]=='status':return 0,'# branch.oid '+'a'*40+'\0# branch.head main\0'+'1 M. N... 100644 100644 100644 '+'b'*40+' '+'c'*40+' project_memories/note.md\0',''
            if args[0]=='ls-tree':return 0,'project_memories/note.md\0',''
            if args[0]=='show' and args[1].startswith(':'):return 0,'index '+str(attempt[0]),''
            if args[0]=='show':
                attempt[0]+=1
                return (1,'','injected') if attempt[0]==1 else (0,'committed','')
            self.fail('Unexpected command')
        with patch.object(observer,'git',side_effect=git) as calls:
            self.assertTrue(observer.git_state(root,True)['incomplete'])
            self.assertFalse(observer.commit_cache)
            second=observer.git_state(root,True);calls.reset_mock()
            third=observer.git_state(root,True)
        self.assertEqual(digest(b'committed'),second['committed_hashes']['project_memories/note.md'])
        self.assertEqual(second['committed_hashes'],third['committed_hashes'])
        self.assertEqual([['show',':project_memories/note.md']],[c.args[1] for c in calls.call_args_list if c.args[1][0]=='show'])
