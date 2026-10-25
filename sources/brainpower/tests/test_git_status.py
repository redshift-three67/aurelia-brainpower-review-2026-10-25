import unittest
from governor_workbench.git_status import parse_status

class GitStatusTests(unittest.TestCase):
    header='# branch.oid '+'a'*40+'\0# branch.head main\0'
    def row(self,xy,path):return '1 '+xy+' N... 100644 100644 100644 '+'b'*40+' '+'c'*40+' '+path+'\0'
    def test_clean_has_no_dirty_indicator(self):
        result=parse_status(self.header);self.assertEqual('',result['status']);self.assertEqual([],result['names'])
    def test_staged_and_worktree_are_separate_and_spaced_names_survive(self):
        result=parse_status(self.header+self.row('M.','project_memories/a b.md')+self.row('.M','source.py'))
        self.assertEqual({'project_memories/a b.md'},result['staged'])
        self.assertEqual(['project_memories/a b.md','source.py'],result['names'])
    def test_deleted_and_added_paths_remain_distinct(self):
        result=parse_status(self.header+self.row('D.','old.py')+self.row('A.','new.py'))
        self.assertEqual(['new.py','old.py'],result['names'])
    def test_malformed_ambiguous_or_escaping_records_fail_closed(self):
        for raw in ('',self.header[:-1],self.header+self.header,self.header+'? unknown\0',self.header+self.row('M.','../escape')):
            with self.subTest(raw=raw),self.assertRaises(ValueError):parse_status(raw)
    def test_unborn_and_detached_are_explicit(self):
        self.assertEqual('',parse_status('# branch.oid (initial)\0# branch.head main\0')['head'])
        self.assertEqual('',parse_status(self.header.replace('main','(detached)'))['branch'])
    def test_merge_conflict_is_not_clean(self):
        row='u UU N... 100644 100644 100644 100644 '+' '.join(['b'*40]*3)+' conflict.py\0'
        self.assertTrue(parse_status(self.header+row)['conflict'])
