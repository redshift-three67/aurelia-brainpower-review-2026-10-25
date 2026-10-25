import copy
import json
import sqlite3
import unittest
from unittest.mock import patch

from tests import test_change_journal
from governor_workbench.execution_workspace import WorkspaceStager, _sha
from governor_workbench.pilot_apply import PilotApply
from governor_workbench.staged_tests import adapter_identity


class ChangeRollbackTests(unittest.TestCase):
    setUp=test_change_journal.ChangeJournalTests.setUp
    evidence=test_change_journal.ChangeJournalTests.evidence

    def transfer(self,step,scope,target,head,record=True):
        stager=WorkspaceStager(self.base/'data')
        path=step+'.py';before=(self.root/path).read_bytes();after=(step+'1').encode()
        stage=stager.stage(str(self.root),[path],[dict(path=path,content=after.decode())],{path:_sha(before)})
        source=self.store.create_job('scope_patch','pilot',{})
        self.store.update_job(source['id'],status='completed',result=dict(stage=stage,scope_hash=scope))
        test=self.store.create_job('stage_test','pilot',dict(stage_job_id=source['id']))
        identity=adapter_identity()
        self.store.update_job(test['id'],status='completed',result=dict(stage_job_id=source['id'],stage_id=stage['id'],
            manifest_hash=stage['manifest_hash'],scope_hash=scope,verified=True,success=True,completion_verified=True,
            sources_verified=True,adapter_verified=True,adapter_before=identity,adapter_after=identity))
        pilot=PilotApply(self.store,stager,[str(self.root)])
        proposal=pilot.prepare(stage['id'],stage['manifest_hash'],test['id'],scope)
        tx=pilot.apply(proposal['id'],stage['manifest_hash'],scope)
        evidence=self.evidence(step,before,after,scope,target)
        evidence.update(transaction=tx,manifest=stage['manifest'])
        receipt=evidence['technical_receipt'];receipt['transaction_id']=tx['id']
        receipt['binding'].update(transaction_id=tx['id'],stage_id=stage['id'],manifest_hash=stage['manifest_hash'],
                                  verified_test_job_id=test['id'],stage_job_id=source['id'])
        event=self.journal.transition(self.chain['id'],head,evidence,'Fixture explicit '+step) if record else None
        return pilot,tx,event

    def pair(self):
        self.pa,self.a,self.ea=self.transfer('a','0'*64,'a'*64,None)
        self.pb,self.b,self.eb=self.transfer('b','a'*64,'b'*64,self.ea['id'])

    def test_non_tip_denied_before_any_write_then_b_and_a_restored(self):
        self.pair()
        with self.assertRaises(ValueError):self.pa.rollback(self.a['id'])
        self.assertEqual(b'a1',(self.root/'a.py').read_bytes());self.assertEqual(b'b1',(self.root/'b.py').read_bytes())
        self.assertEqual('completed',self.pa.transaction(self.a['id'])['status'])
        self.pb.rollback(self.b['id'])
        middle=self.journal.read(self.chain['id'])
        self.assertEqual([self.ea['id']],middle['active_transition_ids']);self.assertTrue(middle['requires_new_plan'])
        self.pa.rollback(self.a['id'])
        self.assertEqual(b'a0',(self.root/'a.py').read_bytes());self.assertEqual(b'b0',(self.root/'b.py').read_bytes())
        result=self.journal.read(self.chain['id']);self.assertEqual(4,len(result['events']))
        self.pa.rollback(self.a['id']);self.pb.rollback(self.b['id'])
        self.assertEqual(result,self.journal.read(self.chain['id']))

    def test_newer_unconfirmed_transfer_blocks_older_rollback(self):
        pa,a,ea=self.transfer('a','0'*64,'a'*64,None)
        pb,b,_=self.transfer('b','a'*64,'b'*64,ea['id'],record=False)
        with self.assertRaises(ValueError):pa.rollback(a['id'])
        self.assertEqual(b'a1',(self.root/'a.py').read_bytes())

    def test_terminal_event_failure_is_explicitly_recoverable_without_replay(self):
        self.pair()
        with self.store.db() as db:
            db.execute("CREATE TRIGGER fail_rollback_event BEFORE INSERT ON dependent_change_events WHEN json_extract(NEW.body,'$.kind')='rollback' BEGIN SELECT RAISE(ABORT,'fixture'); END")
        with self.assertRaises(sqlite3.IntegrityError):self.pb.rollback(self.b['id'])
        self.assertEqual('recovery_needed',self.pb.transaction(self.b['id'])['status'])
        self.assertEqual(2,len(self.journal.read(self.chain['id'])['events']))
        self.assertEqual(b'b0',(self.root/'b.py').read_bytes())
        with self.store.db() as db:db.execute('DROP TRIGGER fail_rollback_event')
        with patch.object(self.pb,'_replace',side_effect=AssertionError('No restored file replay')):
            self.pb.rollback(self.b['id'])
        self.assertEqual('rolled_back',self.pb.transaction(self.b['id'])['status'])
        self.assertEqual(3,len(self.journal.read(self.chain['id'])['events']))

    def test_changed_other_chain_file_blocks_before_restore(self):
        self.pair();(self.root/'a.py').write_bytes(b'foreign')
        with self.assertRaises(ValueError):self.pb.rollback(self.b['id'])
        self.assertEqual(b'b1',(self.root/'b.py').read_bytes())
        self.assertEqual('completed',self.pb.transaction(self.b['id'])['status'])

    def test_changed_transaction_proof_blocks_before_restore(self):
        self.pair()
        with self.store.db() as db:
            tx=copy.deepcopy(self.b);tx['scope_hash']='f'*64
            db.execute('UPDATE pilot_apply_transactions SET body=? WHERE id=?',(json.dumps(tx),tx['id']))
        with self.assertRaises(ValueError):self.pb.rollback(self.b['id'])
        self.assertEqual(b'b1',(self.root/'b.py').read_bytes())

    def test_journal_cannot_advance_during_physical_claim(self):
        self.pair();original=self.pb._recover
        def recover(tx,partial):
            forged=copy.deepcopy(self.b);forged['status']='rolled_back'
            # Even after bytes match the before-state, the durable claim must block journal appends.
            original(tx,partial)
            with self.assertRaises(ValueError):
                self.journal.rollback(self.chain['id'],self.eb['id'],self.eb['id'],forged,'Concurrent mutation')
        with patch.object(self.pb,'_recover',side_effect=recover):self.pb.rollback(self.b['id'])
        self.assertEqual(3,len(self.journal.read(self.chain['id'])['events']))
