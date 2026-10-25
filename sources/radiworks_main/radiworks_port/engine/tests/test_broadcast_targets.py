"""BC1 immutable target/receipt contract, synthetic contexts only."""
import copy
import json
import pytest
from radiworks.core.personal_context import ContextSnapshot, prepare_identity
from radiworks.scope import ScopeContext
from radiworks.core.broadcast_target import BroadcastTarget, BroadcastTargetError, BroadcastTargetStore

SCOPE=ScopeContext('test','client','job')
def snap(label='Synthetic A'):
    case={'name':label,'personalContext':{'firstName':'Ada','birthDate':'1980-02-29'},'focus':'Ruhe'}
    prepare_identity(case)
    return ContextSnapshot.capture(case,SCOPE).payload()
def bound(**kw):
    return BroadcastTarget.capture(scope=SCOPE,source={'kind':'direct'},snapshot=snap(),**kw)
def entry(target):
    return {'broadcastId':'b'*32,'signature':'Synthetic Rate','seconds':5,'multiplier':1,'clear':False,'delayMs':25,'repeat':1,'target':target.payload()}

def test_target_freezes_original_context_and_returns_detached_copies():
    source=snap();before=copy.deepcopy(source)
    target=BroadcastTarget.capture(scope=SCOPE,source={'kind':'direct'},snapshot=source)
    source['context']['caseLabel']='Modified'
    output=target.payload();output['contextSnapshot']['context']['caseLabel']='Modified'
    assert target.payload()['contextSnapshot']==before
    assert target.payload()['binding']=='bound'
    assert target.payload()['source']=={'kind':'direct'}
    with pytest.raises(AttributeError):target._serialized='changed'

def test_job_id_is_not_a_fake_analysis_session_or_draft_id():
    one,two=bound(),bound()
    assert one.payload()['jobId']!=two.payload()['jobId']
    assert set(one.payload()['source'])=={'kind'}

def test_no_case_and_legacy_are_explicitly_distinct():
    no_case=BroadcastTarget.capture(scope=SCOPE,source={'kind':'direct'})
    legacy=BroadcastTarget.capture(scope=SCOPE,source={'kind':'promote','draftId':'12345678-1234-1234-1234-123456789012'},legacy=True)
    assert no_case.payload()['binding']=='no-case'
    assert legacy.payload()['binding']=='legacy-unbound'

@pytest.mark.parametrize('legacy',[False,True])
def test_personal_procedure_rejects_unbound_target(legacy):
    with pytest.raises(BroadcastTargetError):
        BroadcastTarget.capture(scope=SCOPE,source={'kind':'direct'},legacy=legacy,procedure='radi144-personal-v1')

@pytest.mark.parametrize('change',[{'digest':'0'*64},{'caseId':'bad'},{'scope':None}])
def test_bad_existing_snapshot_is_never_downgraded(change):
    value=snap();value.update(change)
    with pytest.raises(BroadcastTargetError,match='Fallkontext|Scope'):
        BroadcastTarget.capture(scope=SCOPE,source={'kind':'promote','draftId':'12345678-1234-1234-1234-123456789012'},snapshot=value,legacy=True)

def test_summary_is_not_a_reusable_canonical_personal_payload():
    target=bound();summary=target.summary()
    assert 'contextSnapshot' not in summary
    assert summary['caseId']==target.payload()['contextSnapshot']['caseId']
    assert 'Ada' not in json.dumps(summary)
    with pytest.raises(BroadcastTargetError):BroadcastTarget.from_payload(summary)

@pytest.mark.parametrize('changes',[{'source':{'kind':'unknown'}},{'jobId':'bad'},{'binding':'no-case'},{'entropyMode':'unknown'},{'procedure':'unknown'}])
def test_target_tamper_rejected(changes):
    value=bound().payload();value.update(changes)
    with pytest.raises(BroadcastTargetError):BroadcastTarget.from_payload(value)

def test_receipt_preserves_original_and_restart_marks_interrupted_without_requeue(tmp_path):
    store=BroadcastTargetStore(tmp_path,SCOPE);target=bound();accepted=entry(target)
    store.accept([accepted]);before=store.get(target.payload()['jobId'])
    accepted['target']['contextSnapshot']['context']['caseLabel']='Modified'
    restarted=BroadcastTargetStore(tmp_path,SCOPE)
    assert restarted.get(target.payload()['jobId'])['target']==before['target']
    assert restarted.get(target.payload()['jobId'])['state']=='interrupted'
    assert restarted.get(target.payload()['jobId'])['broadcastId']=='b'*32

def test_receipt_invalid_or_scope_mismatched_is_rejected_before_write(tmp_path):
    store=BroadcastTargetStore(tmp_path,SCOPE);bad=entry(bound());bad['target']['digest']='0'*64
    with pytest.raises(BroadcastTargetError):store.accept([bad])
    assert not list(tmp_path.glob('*.json'))

def test_terminal_record_is_idempotent_and_cannot_reopen(tmp_path):
    store=BroadcastTargetStore(tmp_path,SCOPE);target=bound();store.accept([entry(target)])
    store.terminal({'broadcastId':'b'*32,'finished':True})
    store.terminal({'broadcastId':'b'*32,'failed':True})
    assert store.get(target.payload()['jobId'])['state']=='finished'
    assert BroadcastTargetStore(tmp_path,SCOPE).get(target.payload()['jobId'])['state']=='finished'

from radiworks.persistence import document_digest

def test_unknown_receipt_schema_is_rejected_without_creating_status(tmp_path):
    store=BroadcastTargetStore(tmp_path,SCOPE);store.accept([entry(bound())])
    path=next(tmp_path.glob('*.receipt.json'));record=json.loads(path.read_text())
    record['schemaVersion']=2
    record['digest']=document_digest({k:v for k,v in record.items() if k!='digest'})
    path.write_text(json.dumps(record),encoding='utf-8')
    with pytest.raises(BroadcastTargetError):BroadcastTargetStore(tmp_path,SCOPE)
    assert not list(tmp_path.glob('*.state.json'))

def test_bad_receipt_time_is_rejected_even_with_matching_digest(tmp_path):
    store=BroadcastTargetStore(tmp_path,SCOPE);store.accept([entry(bound())])
    path=next(tmp_path.glob('*.receipt.json'));record=json.loads(path.read_text())
    record['acceptedAt']='not-a-time'
    record['digest']=document_digest({k:v for k,v in record.items() if k!='digest'})
    path.write_text(json.dumps(record),encoding='utf-8')
    with pytest.raises(BroadcastTargetError):BroadcastTargetStore(tmp_path,SCOPE)

@pytest.mark.parametrize('source',[{'kind':'auto'},{'kind':'promote'},{'kind':'image'},{'kind':'direct','generationId':'a'*32}])
def test_incomplete_or_inappropriate_source_is_rejected_with_valid_digest(source):
    value=bound().payload();value['source']=source
    value['digest']=document_digest({k:v for k,v in value.items() if k!='digest'})
    with pytest.raises(BroadcastTargetError):BroadcastTarget.from_payload(value)

def test_foreign_scope_rejected_with_valid_digest(tmp_path):
    store=BroadcastTargetStore(tmp_path,SCOPE)
    foreign=BroadcastTarget.capture(scope=ScopeContext('other','client','job'),source={'kind':'direct'})
    with pytest.raises(BroadcastTargetError):store.accept([entry(foreign)])
    assert not list(tmp_path.glob('*.json'))

def test_duplicate_batch_is_not_partially_accepted(tmp_path):
    store=BroadcastTargetStore(tmp_path,SCOPE);one=entry(bound());two=entry(bound())
    with pytest.raises(BroadcastTargetError):store.accept([one,two])
    assert not list(tmp_path.glob('*.json'))
    assert store.get(one['target']['jobId']) is None

def test_io_failure_leaves_no_index_or_receipt(tmp_path,monkeypatch):
    import radiworks.core.broadcast_target as module
    store=BroadcastTargetStore(tmp_path,SCOPE);row=entry(bound())
    def fail(*a,**kw):raise OSError('synthetic write failure')
    monkeypatch.setattr(module,'atomic_json_replace',fail)
    with pytest.raises(OSError):store.accept([row])
    assert store.get(row['target']['jobId']) is None
    assert not list(tmp_path.glob('*.json'))

def test_corrupt_terminal_state_is_rejected(tmp_path):
    store=BroadcastTargetStore(tmp_path,SCOPE);row=entry(bound());store.accept([row])
    (tmp_path/(row['target']['jobId']+'.state.json')).write_text('{bad',encoding='utf-8')
    with pytest.raises(BroadcastTargetError):BroadcastTargetStore(tmp_path,SCOPE)

from radiworks.core.broadcast import BroadcastElement, BroadcastManager, BroadcastError
from radiworks.entropy import EntropyProvider

def manager(store, events):
    mgr=BroadcastManager(entropy=EntropyProvider(seed=0),emit=lambda t,p:events.append((t,p)),on_accept=store.accept,on_abort=store.terminal)
    mgr._start_thread=lambda:None
    return mgr

def test_manager_freezes_target_and_persists_before_event(tmp_path):
    store=BroadcastTargetStore(tmp_path,SCOPE);events=[];mgr=manager(store,events);target=bound()
    def emit(kind,payload):
        assert store.get(target.payload()['jobId']) is not None
        events.append((kind,payload))
    mgr._emit=emit
    result=mgr.enqueue('Synthetic Rate',5,target=target)
    assert result['targetReference']==target.summary()
    assert 'target' not in result and 'contextSnapshot' not in result
    queued=mgr._queue[0]
    with pytest.raises(AttributeError):queued.target=None
    with pytest.raises(AttributeError):del queued.target
    assert store.get(target.payload()['jobId'])['clear'] is False

def test_persistence_failure_has_no_executable_job_or_event(tmp_path,monkeypatch):
    store=BroadcastTargetStore(tmp_path,SCOPE);events=[];mgr=manager(store,events)
    def fail(rows):raise OSError('synthetic IO')
    mgr._on_accept=fail
    with pytest.raises(OSError):mgr.enqueue('Synthetic Rate',5,target=bound())
    assert mgr.queue_state()['queued']==[]
    assert events==[]

def test_start_failure_marks_accepted_job_failed_and_rolls_back(tmp_path):
    store=BroadcastTargetStore(tmp_path,SCOPE);events=[];mgr=manager(store,events);target=bound()
    def fail():raise RuntimeError('synthetic start')
    mgr._start_thread=fail
    with pytest.raises(RuntimeError):mgr.enqueue('Synthetic Rate',5,target=target)
    assert store.get(target.payload()['jobId'])['state']=='failed'
    assert mgr.queue_state()['queued']==[] and events==[]

def test_batch_target_and_historical_context_reference_must_agree(tmp_path):
    store=BroadcastTargetStore(tmp_path,SCOPE);events=[];mgr=manager(store,events)
    first=ContextSnapshot.from_payload(snap());second=ContextSnapshot.from_payload(snap('Other'))
    session='c'*32;draft='12345678-1234-1234-1234-123456789012'
    target=BroadcastTarget.capture(scope=SCOPE,source={'kind':'promote','sessionId':session,'draftId':draft},snapshot=first.payload())
    row={'signature':'Synthetic','seconds':5,'target':target.payload(),'contextReference':second.reference(session,draft).payload()}
    with pytest.raises(BroadcastError):mgr.enqueue_batch([row],on_accepted=lambda ids:None)
    assert events==[] and mgr.queue_state()['queued']==[]

def test_batch_keeps_original_context_reference_additively(tmp_path):
    store=BroadcastTargetStore(tmp_path,SCOPE);events=[];mgr=manager(store,events)
    snapshot=ContextSnapshot.from_payload(snap());session='c'*32;draft='12345678-1234-1234-1234-123456789012'
    target=BroadcastTarget.capture(scope=SCOPE,source={'kind':'promote','sessionId':session,'draftId':draft},snapshot=snapshot.payload())
    reference=snapshot.reference(session,draft).payload()
    rows=mgr.enqueue_batch([{'signature':'Synthetic','seconds':5,'target':target.payload(),'contextReference':reference}],on_accepted=lambda ids:None)
    assert rows[0]['contextReference']==reference
    assert rows[0]['targetReference']==target.summary()
    assert store.get(target.payload()['jobId'])['target']['contextSnapshot']==snapshot.payload()

from radiworks.core.automode import AutoModeController
from radiworks.core.analysis import AnalysisResult, Rate, RateObject

def test_auto_pins_provider_and_context_for_its_generation(monkeypatch):
    import radiworks.core.automode as module
    pinned=EntropyProvider(seed=42);replacement=EntropyProvider(seed=999);targets=[];seen=[]
    template=BroadcastTarget.capture(scope=SCOPE,source={'kind':'auto','generationId':'d'*32},snapshot=snap())
    def analyze(rates,entropy):
        seen.append(entropy._provider)
        return AnalysisResult(rate_objects=[RateObject(name_or_rate='Synthetic Rate',energetic_value=5)])
    controller=AutoModeController(enqueue=lambda *a:None,enqueue_target=lambda sig,seconds,multiplier,target: targets.append(target) or {},emit=lambda *a:None,find_rates=lambda db:[Rate(name='Synthetic Rate')],analyse=analyze,live_entropy=lambda:replacement,queue_state=lambda:{'active':[],'queued':[]})
    monkeypatch.setattr(module,'check_general_vitality',lambda entropy:1500)
    controller.start('Synthetic.txt',target_template=template,entropy_provider=pinned)
    controller._analyse_worker(controller._generation,'Synthetic.txt',1)
    controller._analyse_worker(controller._generation,'Synthetic.txt',1)
    assert seen==[pinned,pinned]
    assert len(targets)==2 and targets[0].payload()['jobId']!=targets[1].payload()['jobId']
    assert targets[0].payload()['contextSnapshot']==template.payload()['contextSnapshot']
    assert targets[0].payload()['source']==template.payload()['source']
    old=controller._generation;controller.stop();controller._analyse_worker(old,'Synthetic.txt',1)
    assert len(targets)==2

@pytest.mark.parametrize('kind,mode,procedure',[('direct','seeded','original-aetherone-v1'),('auto','stochastic','original-aetherone-v1'),('auto','seeded','radi144-personal-v1')])
def test_auto_inconsistent_template_rejected_before_generation_or_events(kind,mode,procedure):
    events=[]
    source={'kind':kind,**({'generationId':'d'*32} if kind=='auto' else {})}
    target=BroadcastTarget.capture(scope=SCOPE,source=source,snapshot=snap(),entropy_mode=mode,procedure=procedure)
    ctl=AutoModeController(enqueue=lambda *a:None,enqueue_target=lambda *a:None,emit=lambda *a:events.append(a),find_rates=lambda db:[],analyse=lambda *a:AnalysisResult(),live_entropy=lambda:EntropyProvider(seed=0),queue_state=lambda:{'active':[],'queued':[]})
    with pytest.raises(ValueError):ctl.start('Test',target_template=target,entropy_provider=EntropyProvider(seed=0))
    assert ctl._generation==0 and not ctl.state.enabled and events==[]

def test_acceptance_callback_cannot_observe_unaccepted_queue(tmp_path):
    events=[];store=BroadcastTargetStore(tmp_path,SCOPE);mgr=manager(store,events)
    def accept(rows):
        assert mgr.queue_state()['queued']==[]
        store.accept(rows)
    mgr._on_accept=accept
    mgr.enqueue('Synthetic',5,target=bound())
    assert len(mgr.queue_state()['queued'])==1

def test_batch_promotion_commit_failure_rolls_back_and_marks_targets_failed(tmp_path):
    store=BroadcastTargetStore(tmp_path,SCOPE);events=[];mgr=manager(store,events);target=bound()
    def fail(ids):raise OSError('synthetic draft commit')
    with pytest.raises(OSError):mgr.enqueue_batch([{'signature':'Synthetic','seconds':5,'target':target.payload()}],on_accepted=fail)
    assert mgr.queue_state()['queued']==[] and events==[]
    assert store.get(target.payload()['jobId'])['state']=='failed'

def test_auto_stop_restart_during_analysis_never_enqueues_old_target(monkeypatch):
    import threading
    import radiworks.core.automode as module
    entered=threading.Event();release=threading.Event();targets=[]
    def analyze(rates,entropy):
        entered.set();assert release.wait(3)
        return AnalysisResult(rate_objects=[RateObject(name_or_rate='Synthetic Rate',energetic_value=5)])
    ctl=AutoModeController(enqueue=lambda *a:None,enqueue_target=lambda *a:targets.append(a),emit=lambda *a:None,find_rates=lambda db:[Rate(name='Synthetic Rate')],analyse=analyze,live_entropy=lambda:EntropyProvider(seed=0),queue_state=lambda:{'active':[],'queued':[]})
    old=BroadcastTarget.capture(scope=SCOPE,source={'kind':'auto','generationId':'a'*32},snapshot=snap())
    new=BroadcastTarget.capture(scope=SCOPE,source={'kind':'auto','generationId':'b'*32},snapshot=snap('Synthetic B'))
    monkeypatch.setattr(module,'check_general_vitality',lambda e:1500)
    ctl.start('Test',target_template=old,entropy_provider=EntropyProvider(seed=0))
    thread=threading.Thread(target=ctl._analyse_worker,args=(ctl._generation,'Test',1));thread.start()
    try:
        assert entered.wait(3)
        ctl.stop();ctl.start('Test',target_template=new,entropy_provider=EntropyProvider(seed=1))
    finally:
        release.set();thread.join(3)
    assert not thread.is_alive() and targets==[]
    assert ctl._target_template.payload()==new.payload()
