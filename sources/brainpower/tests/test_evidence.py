import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from governor_workbench.config import load_config
from governor_workbench.evidence import Observer, MemoryConflict


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root / 'repo'
        (self.repo / 'project_memories').mkdir(parents=True)
        self.memory = self.repo / 'project_memories' / 'state.md'
        self.memory.write_text('original', encoding='utf-8')
        self.git('init', '-q')
        self.config_path = self.root / 'config.json'
        self.config_path.write_text(json.dumps({'version':1,'data_dir':'runtime','projects':[
            {'id':'demo','name':'Demo','path':str(self.repo),'gate':'Blocked','depends_on':[]}]}))
        self.config = load_config(self.config_path)
        self.observer = Observer(self.config)

    def git(self, *args):
        return subprocess.run(['git','-C',str(self.repo),*args],check=True,capture_output=True)

    def test_staging_does_not_mean_committed(self):
        self.git('add','project_memories/state.md')
        memory = self.observer.scan(force_git=True)['projects'][0]['memories'][0]
        self.assertTrue(memory['staged'])
        self.assertFalse(memory['committed'])
        self.git('-c','user.name=Test','-c','user.email=test@example.invalid','commit','-qm','baseline')
        memory = self.observer.scan(force_git=True)['projects'][0]['memories'][0]
        self.assertTrue(memory['committed'])
        self.assertFalse(memory['staged'])

    def test_replace_refs_do_not_change_exact_commit_evidence(self):
        self.git('add','.')
        self.git('-c','user.name=Test','-c','user.email=test@example.invalid','commit','-qm','original')
        original=self.git('rev-parse','HEAD').stdout.decode().strip()
        self.memory.write_text('replacement',encoding='utf-8')
        self.git('add','.')
        self.git('-c','user.name=Test','-c','user.email=test@example.invalid','commit','-qm','replacement')
        replacement=self.git('rev-parse','HEAD').stdout.decode().strip()
        self.git('checkout','--detach',original)
        self.git('replace',original,replacement)
        self.assertEqual(b'replacement',self.git('show','HEAD:project_memories/state.md').stdout)
        for remove in (False,True):
            if remove:self.git('replace','-d',original)
            result=self.observer.scan(force_git=True)['projects'][0]
            self.assertTrue(result['evidence_complete'],result)
            self.assertTrue(result['memories'][0]['committed'],result)
            self.assertEqual('',result['git_status'])

    def test_edit_conflict_preserves_external_change(self):
        old = self.observer.read_memory('demo','state.md')
        self.memory.write_text('external', encoding='utf-8')
        with self.assertRaises(MemoryConflict):
            self.observer.save_memory('demo','state.md','overwrite',old['sha256'])
        self.assertEqual('external',self.memory.read_text())

    def test_save_backs_up_original(self):
        old = self.observer.read_memory('demo','state.md')
        result = self.observer.save_memory('demo','state.md','updated',old['sha256'])
        self.assertEqual('original',Path(result['backup']).read_text())
        self.assertEqual('updated',self.observer.read_memory('demo','state.md')['content'])

    def test_path_escape_rejected(self):
        for name in ['../outside.md','nested/file.md','..\\outside.md','state.md:stream','STATE.txt']:
            with self.assertRaises(ValueError): self.observer.read_memory('demo',name)

    def test_missing_project_is_not_green(self):
        self.config['projects'][0]['path'] = str(self.root/'absent')
        p = Observer(self.config).scan()['projects'][0]
        self.assertEqual('Nicht erreichbar',p['status'])
        self.assertTrue(p['warnings'])

    def test_nested_directory_does_not_inherit_parent_repository(self):
        self.git('add','.'); self.git('-c','user.name=Test','-c','user.email=test@example.invalid','commit','-qm','baseline')
        nested=self.repo/'child'; nested.mkdir()
        self.config['projects'][0]['path']=str(nested)
        p=Observer(self.config).scan(force_git=True)['projects'][0]
        self.assertEqual('',p['head'])
        self.assertFalse(p['evidence_complete'])

    def test_memory_drift_changes_evidence_hash(self):
        first = self.observer.scan(force_git=True)['projects'][0]['evidence_hash']
        self.memory.write_text('different', encoding='utf-8')
        second = self.observer.scan()['projects'][0]['evidence_hash']
        self.assertNotEqual(first,second)

    def test_changed_memory_is_not_committed_content(self):
        self.git('add','.'); self.git('-c','user.name=Test','-c','user.email=test@example.invalid','commit','-qm','baseline')
        self.memory.write_text('not in commit',encoding='utf-8')
        memory=self.observer.scan(force_git=True)['projects'][0]['memories'][0]
        self.assertFalse(memory['committed'])

    def test_large_tracked_drift_changes_hash(self):
        p=self.repo/'large.txt'; p.write_bytes(b'a'*2100000)
        self.git('add','.'); self.git('-c','user.name=Test','-c','user.email=test@example.invalid','commit','-qm','baseline')
        p.write_bytes(b'b'*2100000)
        first=self.observer.scan(force_git=True)['projects'][0]['evidence_hash']
        p.write_bytes(b'c'*2100000)
        self.assertNotEqual(first,self.observer.scan(force_git=True)['projects'][0]['evidence_hash'])

    def test_no_invented_conflict_when_sources_absent(self):
        self.config['projects'][0]['id']='radi144'
        p=Observer(self.config).scan()['projects'][0]
        self.assertFalse(any('Snapshot und goals' in w for w in p['warnings']))

    def test_stage_then_edit_is_not_current_staged_content(self):
        self.git('add','.')
        self.memory.write_text('after staging',encoding='utf-8')
        memory=self.observer.scan(force_git=True)['projects'][0]['memories'][0]
        self.assertFalse(memory['staged'])
        self.assertTrue(memory['has_staged_changes'])

    def test_plan_metadata_invalidates_review(self):
        first=self.observer.scan(force_git=True)['evidence_hash']
        self.config['projects'][0]['next_step']='different decision'
        self.assertNotEqual(first,self.observer.scan()['evidence_hash'])

    def test_config_rejects_unknown_dependency(self):
        data=json.loads(self.config_path.read_text())
        data['projects'][0]['depends_on']=['missing']
        self.config_path.write_text(json.dumps(data))
        with self.assertRaises(ValueError): load_config(self.config_path)

    def test_config_rejects_external_router(self):
        data=json.loads(self.config_path.read_text()); data['router_url']='https://example.com/v1'
        self.config_path.write_text(json.dumps(data))
        with self.assertRaises(ValueError): load_config(self.config_path)


if __name__ == '__main__': unittest.main()
