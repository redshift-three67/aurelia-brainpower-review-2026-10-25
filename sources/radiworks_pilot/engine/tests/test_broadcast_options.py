import time
import pytest
from radiworks.core.broadcast import BroadcastManager
from radiworks.core.broadcast_policy import ExecutionPolicy
from radiworks.core.broadcast_target import BroadcastTargetStore
from radiworks.entropy import EntropyProvider
from test_broadcast_policy import target,config

def manager(monkeypatch,**kw):
 m=BroadcastManager(EntropyProvider(seed=0),lambda *a:None,**kw);monkeypatch.setattr(m,'_start_thread',lambda:None);return m

def test_queue_single_mode_waits_for_existing_active_without_stopping(monkeypatch):
 limit=[8];m=manager(monkeypatch,capacity=lambda:limit[0])
 for i in range(4):m.enqueue('Synthetic '+str(i),60)
 m._promote_from_queue();assert len(m._active)==4
 limit[0]=1;m.enqueue('Waiting',60);m._promote_from_queue();assert len(m._active)==4 and len(m._queue)==1
 for e in list(m._active):e.start=time.monotonic()-100;m._finish(e)
 m._promote_from_queue();assert len(m._active)==1 and not m._queue

def test_policy_is_frozen_at_acceptance_and_receipt_survives_restart(tmp_path,monkeypatch):
 t=target();opts=config(**{'broadcast.delta.time':True});store=BroadcastTargetStore(tmp_path,t.payload_scope if hasattr(t,'payload_scope') else __import__('radiworks.scope',fromlist=['ScopeContext']).ScopeContext(**t.payload()['scope']))
 m=manager(monkeypatch,policy_factory=lambda t,s,allow_delta=True:ExecutionPolicy.capture(opts,t,s,500,allow_delta=allow_delta),on_accept=store.accept,on_abort=store.terminal)
 payload=m.enqueue('Synthetic',900,target=t);assert payload['seconds']==400
 opts['booleans']['broadcast.delta.time']=False
 assert m._queue[0].execution_policy.seconds==400
 receipt=store.get(t.payload()['jobId']);assert receipt['executionPolicy']['requestedSeconds']==900
 restarted=BroadcastTargetStore(tmp_path,__import__('radiworks.scope',fromlist=['ScopeContext']).ScopeContext(**t.payload()['scope']))
 assert restarted.get(t.payload()['jobId'])['executionPolicy']==receipt['executionPolicy']

class LowGv(EntropyProvider):
 def get_integer(self,lo,hi):return 1

def test_dynamic_followup_is_bounded_pinned_and_journalled_before_queue(monkeypatch):
 t=target();opts=config(**{'dynamic.adjustments':True});events=[];decisions=[]
 m=manager(monkeypatch,policy_factory=lambda t,s,allow_delta=True:ExecutionPolicy.capture(opts,t,s,500,allow_delta=allow_delta),entropy_factory=lambda t:LowGv(seed=0),on_entropy=lambda p:events.append('checkpoint'),on_adjustment=lambda p:decisions.append(p))
 m.enqueue('Synthetic',300,target=t);m._promote_from_queue();parent=m._active[0];parent.start=time.monotonic()-400;m._finish(parent)
 assert not m._active and len(m._queue)==1;child=m._queue[0]
 assert child.seconds==250 and child.target.payload()['contextSnapshot']==t.payload()['contextSnapshot']
 assert child.target.payload()['jobId']!=t.payload()['jobId'] and child.entropy_provider is not parent.entropy_provider
 assert decisions[-1]['reason']=='followup' and decisions[-1]['measuredGv']==1
 m._promote_from_queue();child.start=time.monotonic()-400;m._finish(child);assert not m._queue

def test_stop_never_generates_adjustment(monkeypatch):
 decisions=[];t=target();m=manager(monkeypatch,on_adjustment=decisions.append,policy_factory=lambda t,s,allow_delta=True:ExecutionPolicy.capture(config(**{'dynamic.adjustments':True}),t,s,500))
 m.enqueue('Synthetic',300,target=t);m._promote_from_queue();m.stop_all();assert not decisions and not m._queue


def test_adjustment_crash_before_admission_is_explicit_after_restart(tmp_path,monkeypatch):
 from radiworks.scope import ScopeContext
 t=target();scope=ScopeContext(**t.payload()['scope']);store=BroadcastTargetStore(tmp_path,scope)
 m=manager(monkeypatch,policy_factory=lambda t,s,allow_delta=True:ExecutionPolicy.capture(config(**{'dynamic.adjustments':True}),t,s,800),on_accept=store.accept)
 parent=m.enqueue('Synthetic',600,target=t);p=parent['executionPolicy']
 store.record_adjustment({'parentBroadcastId':parent['broadcastId'],'parentJobId':t.payload()['jobId'],'rootJobId':p['rootJobId'],'depth':0,'referenceGv':800,'measuredGv':700,'seconds':500,'reason':'followup','childJobId':'a'*32})
 reopened=BroadcastTargetStore(tmp_path,scope);r=reopened.adjustments()[0]
 assert r['childAdmission']=='interrupted-before-acceptance' and r['childState'] is None
 assert reopened.get('a'*32) is None
