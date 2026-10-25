import copy
import json
import sqlite3
import tempfile
import threading
import unittest
from unittest.mock import patch
from pathlib import Path

from governor_workbench.evidence import fingerprint
from governor_workbench.execution_workspace import _root, _sha
from governor_workbench.store import Store


class ChangeJournalTests(unittest.TestCase):
    def setUp(self):
        from governor_workbench.change_journal import ChangeJournal
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.base=Path(self.tmp.name).resolve();self.root=self.base/'pilot';self.root.mkdir()
        (self.root/'a.py').write_bytes(b'a0');(self.root/'b.py').write_bytes(b'b0')
        self.store=Store(self.base/'journal.db');self.journal=ChangeJournal(self.store)
        self.binding=dict(candidate_id='candidate',selection_id='selection',step_ids=['a','b'],
            step_hashes={'a':'1'*64,'b':'2'*64},step_scopes={'a':['a.py'],'b':['b.py']},
            root=str(self.root),root_identity=_root(self.root)[1],scope_hash='0'*64,
            sources={'a.py':_sha(b'a0'),'b.py':_sha(b'b0')},adapter_hash='3'*64)
        self.chain=self.journal.create(self.binding,'Approved internal fixture')

    def evidence(self,step,before,after,source,target):
        path=step+'.py';seal_files=[dict(path=path,original_sha256=_sha(before),staged_sha256=_sha(after),staged_bytes=len(after),diff='fixture')]
        manifest=dict(version=1,id='stage_'+step,original_root=str(self.root),root_identity=self.binding['root_identity'],
            files=seal_files,execution_enabled=False,apply_back_enabled=False)
        seal=_sha(json.dumps(manifest,ensure_ascii=False,sort_keys=True,indent=2).encode())
        tx=dict(id='tx_'+step,stage_id=manifest['id'],manifest_hash=seal,scope_hash=source,
            original_root=str(self.root),root_identity=self.binding['root_identity'],status='completed',
            files=[dict(path=path,before=_sha(before),after=_sha(after),intent=True,written=True)])
        binding=dict(transaction_id=tx['id'],verified_test_job_id='test_'+step,stage_job_id='patch_'+step,
            stage_id=manifest['id'],manifest_hash=seal,candidate_id='candidate',step_id=step,
            step_hash=self.binding['step_hashes'][step],selection_id='selection',plan_scope_hash=source,
            observed_scope_hash=target,test_adapter_hash='4'*64,completion_adapter_hash='5'*64)
        receipt=dict(id='receipt_'+step,transaction_id=tx['id'],binding=binding,status='recorded',
            kind='isolated_change_transfer_completion',scope_observation_acknowledged=True,
            execution_enabled=False,product_gate_approved=False,target_tests_executed=False)
        return dict(transaction=tx,manifest=manifest,technical_receipt=receipt)

    def apply_a(self):
        evidence=self.evidence('a',b'a0',b'a1','0'*64,'a'*64)
        (self.root/'a.py').write_bytes(b'a1')
        event=self.journal.transition(self.chain['id'],None,evidence,'Confirm A')
        return event,evidence

    def apply_b(self):
        a,ea=self.apply_a();evidence=self.evidence('b',b'b0',b'b1','a'*64,'b'*64)
        (self.root/'b.py').write_bytes(b'b1')
        b=self.journal.transition(self.chain['id'],a['id'],evidence,'Confirm B')
        return a,b,ea,evidence

    def inspect(self,scope):
        return self.journal.inspect(self.chain['id'],scope,'3'*64)

    def test_two_edges_reconstruct_history_separately_from_tip(self):
        a,b,ea,eb=self.apply_b();report=self.inspect('b'*64)
        self.assertTrue(report['history_valid']);self.assertTrue(report['tip_current'])
        self.assertEqual([a['id'],b['id']],report['active_transition_ids'])
        self.assertEqual({'a.py':_sha(b'a1'),'b.py':_sha(b'b1')},report['files'])
        self.assertEqual(3,len(report['states']))
        self.assertFalse(report['execution_authorized'])
        (self.root/'a.py').write_bytes(b'foreign')
        report=self.inspect('b'*64)
        self.assertTrue(report['history_valid']);self.assertFalse(report['tip_current'])

    def test_only_tip_rollback_no_reactivation_and_no_automatic_writes(self):
        a,b,ea,eb=self.apply_b();ra=copy.deepcopy(ea['transaction']);ra['status']='rolled_back'
        with self.assertRaises(ValueError):self.journal.rollback(self.chain['id'],b['id'],a['id'],ra,'Wrong order')
        self.assertEqual(b'a1',(self.root/'a.py').read_bytes())
        rb=copy.deepcopy(eb['transaction']);rb['status']='rolled_back'
        with self.assertRaises(ValueError):self.journal.rollback(self.chain['id'],b['id'],b['id'],rb,'Not restored')
        (self.root/'b.py').write_bytes(b'b0')
        event=self.journal.rollback(self.chain['id'],b['id'],b['id'],rb,'Restore B confirmed')
        report=self.inspect('a'*64);self.assertTrue(report['tip_current']);self.assertTrue(report['requires_new_plan'])
        self.assertEqual([a['id']],report['active_transition_ids'])
        (self.root/'b.py').write_bytes(b'b1')
        with self.assertRaises(ValueError):self.journal.transition(self.chain['id'],event['id'],eb,'Never revive')
        (self.root/'b.py').write_bytes(b'b0');(self.root/'a.py').write_bytes(b'a0')
        self.journal.rollback(self.chain['id'],event['id'],a['id'],ra,'Restore A confirmed')
        report=self.inspect('0'*64);self.assertTrue(report['tip_current']);self.assertTrue(report['requires_new_plan'])
        self.assertEqual([],report['active_transition_ids'])

    def test_idempotent_retry_and_stale_head(self):
        a,ea=self.apply_a()
        self.assertEqual(a,self.journal.transition(self.chain['id'],None,ea,'Confirm A'))
        with self.assertRaises(ValueError):self.journal.transition(self.chain['id'],None,ea,'Different consent')
        eb=self.evidence('b',b'b0',b'b1','a'*64,'b'*64);(self.root/'b.py').write_bytes(b'b1')
        with self.assertRaises(ValueError):self.journal.transition(self.chain['id'],None,eb,'Stale head')

    def test_partial_or_mismatching_receipt_cannot_append(self):
        evidence=self.evidence('a',b'a0',b'a1','0'*64,'a'*64);(self.root/'a.py').write_bytes(b'a1')
        for area,field,value in [('transaction','status','interrupted'),('transaction','status','rolling_back'),
                ('transaction','root_identity',{'device':0,'inode':0}),('technical_receipt','status','failed')]:
            bad=copy.deepcopy(evidence);bad[area][field]=value
            with self.subTest(field=field,value=value),self.assertRaises(ValueError):
                self.journal.transition(self.chain['id'],None,bad,'Invalid')
        for field,value in [('selection_id','other'),('candidate_id','other'),('step_hash','f'*64),('plan_scope_hash','d'*64),('transaction_id','other')]:
            bad=copy.deepcopy(evidence);bad['technical_receipt']['binding'][field]=value
            with self.subTest(field=field),self.assertRaises(ValueError):self.journal.transition(self.chain['id'],None,bad,'Invalid')
        self.assertEqual([],self.journal.read(self.chain['id'])['events'])

    def test_manifest_tampering_or_unsealed_files_block(self):
        evidence=self.evidence('a',b'a0',b'a1','0'*64,'a'*64);(self.root/'a.py').write_bytes(b'a1')
        bad=copy.deepcopy(evidence);bad['manifest']['files'][0]['diff']='tampered'
        with self.assertRaises(ValueError):self.journal.transition(self.chain['id'],None,bad,'Invalid')
        bad=copy.deepcopy(evidence);bad['transaction']['files'][0]['written']=False
        with self.assertRaises(ValueError):self.journal.transition(self.chain['id'],None,bad,'Invalid')
        (self.root/'b.py').write_bytes(b'foreign')
        with self.assertRaises(ValueError):self.journal.transition(self.chain['id'],None,evidence,'Unrelated drift')

    def test_swapped_step_wrong_predecessor_and_third_edge_block(self):
        b=self.evidence('b',b'b0',b'b1','0'*64,'b'*64)
        with self.assertRaises(ValueError):self.journal.transition(self.chain['id'],None,b,'B cannot precede A')
        a,ea=self.apply_a()
        b=self.evidence('b',b'b0',b'b1','0'*64,'b'*64);(self.root/'b.py').write_bytes(b'b1')
        with self.assertRaises(ValueError):self.journal.transition(self.chain['id'],a['id'],b,'Wrong H0')
        b=self.evidence('b',b'b0',b'b1','a'*64,'b'*64)
        event=self.journal.transition(self.chain['id'],a['id'],b,'B')
        with self.assertRaises(ValueError):self.journal.transition(self.chain['id'],event['id'],ea,'Third edge')

    def test_inspect_root_replacement_preserves_only_historical_validity(self):
        self.apply_a();root,identity=_root(self.root)
        with patch('governor_workbench.change_journal._root',return_value=(root,dict(identity,inode=identity['inode']+1))):
            report=self.inspect('a'*64)
        self.assertTrue(report['history_valid']);self.assertFalse(report['tip_current'])

    def test_baseline_overlapping_scope_and_false_hash_types_rejected(self):
        for mutate in (lambda b:b['step_scopes'].update(b=['a.py']),lambda b:b['sources'].update({'a.py':False})):
            value=copy.deepcopy(self.binding);value['candidate_id']='different';mutate(value)
            with self.assertRaises(ValueError):self.journal.create(value,'Invalid baseline')

    def test_immutable_tables_and_restart_without_replay(self):
        a,ea=self.apply_a()
        with self.store.db() as db:
            for table in ('dependent_change_chains','dependent_change_events'):
                for sql in ('UPDATE '+table+' SET body=body','DELETE FROM '+table):
                    with self.assertRaises(sqlite3.IntegrityError):db.execute(sql)
        from governor_workbench.change_journal import ChangeJournal
        restarted=ChangeJournal(Store(self.store.path))
        self.assertEqual([a],restarted.read(self.chain['id'])['events'])
        self.assertEqual(b'a1',(self.root/'a.py').read_bytes());self.assertEqual([],self.store.jobs())

    def test_concurrent_append_has_one_winner(self):
        from governor_workbench.change_journal import ChangeJournal
        from types import SimpleNamespace
        other_store=SimpleNamespace(path=self.store.path,lock=threading.RLock())
        other_store.db=lambda:Store.db(other_store)
        other=ChangeJournal(other_store);e=self.evidence('a',b'a0',b'a1','0'*64,'a'*64)
        (self.root/'a.py').write_bytes(b'a1');barrier=threading.Barrier(2);results=[]
        def run(journal,note):
            barrier.wait()
            try:journal.transition(self.chain['id'],None,e,note);results.append('ok')
            except ValueError:results.append('blocked')
        threads=[threading.Thread(target=run,args=(j,n)) for j,n in ((self.journal,'one'),(other,'two'))]
        for t in threads:t.start()
        for t in threads:t.join(10);self.assertFalse(t.is_alive())
        self.assertCountEqual(['ok','blocked'],results)
        self.assertEqual(1,len(self.journal.read(self.chain['id'])['events']))

    def test_selection_and_adapter_drift_do_not_destroy_history(self):
        self.apply_a();report=self.journal.inspect(self.chain['id'],'a'*64,'9'*64)
        self.assertTrue(report['history_valid']);self.assertFalse(report['tip_current'])
        self.assertFalse(self.inspect('f'*64)['tip_current'])
        changed=copy.deepcopy(self.binding);changed['selection_id']='different'
        with self.assertRaises(ValueError):self.journal.create(changed,'No second activation')

    def test_legacy_receipts_not_imported(self):
        with self.store.db() as db:
            db.execute('CREATE TABLE plan_scope_transitions(id TEXT PRIMARY KEY, body TEXT)')
            db.execute('INSERT INTO plan_scope_transitions VALUES(?,?)',('legacy','{}'))
        from governor_workbench.change_journal import ChangeJournal
        again=ChangeJournal(self.store)
        self.assertEqual([],again.read(self.chain['id'])['events'])
        with self.store.db() as db:self.assertEqual('{}',db.execute('SELECT body FROM plan_scope_transitions').fetchone()[0])

    def test_hash_tampering_detected_even_if_db_trigger_removed(self):
        self.apply_a()
        with self.store.db() as db:
            db.execute('DROP TRIGGER dependent_change_events_no_update')
            row=db.execute('SELECT id,body FROM dependent_change_events').fetchone()
            body=json.loads(row['body']);body['note']='changed'
            db.execute('UPDATE dependent_change_events SET body=? WHERE id=?',(json.dumps(body),row['id']))
        report=self.inspect('a'*64);self.assertFalse(report['history_valid']);self.assertFalse(report['tip_current'])

    def test_database_insert_failure_keeps_old_head_and_does_not_replay_files(self):
        with self.store.db() as db:
            db.execute("CREATE TRIGGER injected_failure BEFORE INSERT ON dependent_change_events BEGIN SELECT RAISE(ABORT,'disk fixture'); END")
        e=self.evidence('a',b'a0',b'a1','0'*64,'a'*64);(self.root/'a.py').write_bytes(b'a1')
        with self.assertRaises(sqlite3.IntegrityError):self.journal.transition(self.chain['id'],None,e,'A')
        self.assertEqual([],self.journal.read(self.chain['id'])['events'])
        self.assertFalse(self.inspect('0'*64)['tip_current'])
        self.assertEqual(b'a1',(self.root/'a.py').read_bytes())
        with self.store.db() as db:db.execute('DROP TRIGGER injected_failure')
        self.journal.transition(self.chain['id'],None,e,'A')
        self.assertEqual(1,len(self.journal.read(self.chain['id'])['events']))

    def test_journal_change_during_inspection_is_not_current(self):
        a,ea=self.apply_a();original=self.journal.read;count=0
        def changed(key):
            nonlocal count
            value=original(key);count+=1
            if count>1:value['head_hash']='f'*64
            return value
        with patch.object(self.journal,'read',side_effect=changed):
            self.assertFalse(self.inspect('a'*64)['tip_current'])

    def test_actual_legacy_transaction_and_technical_receipt_snapshot(self):
        from tests import test_technical_completion
        from governor_workbench.change_journal import ChangeJournal
        fixture=test_technical_completion.TechnicalCompletionTests();fixture.setUp();self.addCleanup(fixture.doCleanups)
        journal=ChangeJournal(fixture.store)
        binding=dict(candidate_id=fixture.candidate['id'],selection_id=fixture.result['plan_selection_id'],
            step_ids=['fix','future'],step_hashes={'fix':fingerprint(fixture.step),'future':'f'*64},
            step_scopes={'fix':['main.py'],'future':['future.py']},root=str(fixture.root),root_identity=_root(fixture.root)[1],
            scope_hash='a'*64,sources={'main.py':_sha(b'old WIP\r\n'),'future.py':None},adapter_hash='3'*64)
        chain=journal.create(binding,'Internal archival compatibility fixture, not dependent plan authorization')
        job=fixture.verified_job();receipt=fixture.complete(job)
        evidence=dict(transaction=fixture.tx,manifest=fixture.store.job(fixture.source['id'])['result']['stage']['manifest'],technical_receipt=receipt)
        event=journal.transition(chain['id'],None,evidence,'Archive actual isolated transfer receipt')
        self.assertTrue(journal.inspect(chain['id'],'b'*64,'3'*64)['tip_current'])
        from governor_workbench.pilot_actions import rollback
        restored=rollback(fixture.app,fixture.tx['id'],None)
        archived=journal.read(chain['id'])
        self.assertEqual(len(archived['events']),2)
        self.assertEqual(archived['events'][-1]['kind'],'rollback')
        self.assertEqual(archived['events'][-1]['target_id'],event['id'])
        self.assertEqual(restored['status'],'rolled_back')
        report=journal.inspect(chain['id'],'a'*64,'3'*64)
        self.assertTrue(report['history_valid']);self.assertTrue(report['tip_current']);self.assertTrue(report['requires_new_plan'])
