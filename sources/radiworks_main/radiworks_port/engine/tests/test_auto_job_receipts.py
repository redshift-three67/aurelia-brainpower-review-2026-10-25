"""Auto generations have durable entropy provenance before visible GV values."""
import copy
import pytest
from radiworks.api.routes import STATE
from radiworks.core.auto_jobs import AutoJobStore
from radiworks.core.broadcast_target import BroadcastTarget
from radiworks.entropy import EntropyProvider
from radiworks.scope import ScopeContext


def test_auto_generation_receipt_survives_restart_without_resuming(tmp_path):
    scope=ScopeContext('synthetic','client','job');store=AutoJobStore(tmp_path/'auto',scope)
    target=BroadcastTarget.capture(scope=scope,source={'kind':'auto','generationId':'a'*32})
    provider=EntropyProvider(seed=0);store.accept(target,'Synthetic',1,[],provider.checkpoint())
    provider.get_integer_bound(100);store.checkpoint(target,provider.checkpoint())
    receipt=store.get('a'*32)
    assert receipt['state']=='active' and receipt['entropy']['drawCount']==1
    restored=AutoJobStore(tmp_path/'auto',scope)
    after=restored.get('a'*32)
    assert after['state']=='interrupted' and after['entropy']==receipt['entropy']
    assert after['target']==target.payload()


def test_auto_entropy_receipt_commits_before_gv_event(home,monkeypatch):
    monkeypatch.setattr(STATE.state.broadcast,'ensure_running',lambda:None)
    response=home.post('/auto-mode/on',json={'database':'HOMEOPATHY_Test','seed':0})
    assert response.status_code==200,response.text
    target=STATE.state.auto._target_template
    identifier=target.payload()['source']['generationId']
    assert STATE.state.auto_jobs.get(identifier)['entropy']['drawCount']==0
    events=[]
    original=STATE.state.auto._emit
    def capture(kind,payload):
        if kind=='gv.update':
            assert STATE.state.auto_jobs.get(identifier)['entropy']['drawCount']>0
            events.append(payload)
        original(kind,payload)
    monkeypatch.setattr(STATE.state.auto,'_emit',capture)
    STATE.state.auto.tick()
    assert events
    assert home.post('/auto-mode/off').status_code==200
    assert STATE.state.auto_jobs.get(identifier)['state']=='stopped'


def test_failed_auto_checkpoint_stops_generation_without_publishing_uncommitted_gv(home,monkeypatch):
    monkeypatch.setattr(STATE.state.broadcast,'ensure_running',lambda:None)
    assert home.post('/auto-mode/on',json={'database':'HOMEOPATHY_Test','seed':0}).status_code==200
    def fail(*args):raise OSError('synthetic checkpoint failure')
    monkeypatch.setattr(STATE.state.auto_jobs,'checkpoint',fail)
    events=[];monkeypatch.setattr(STATE.state.auto,'_emit',lambda kind,payload:events.append((kind,payload)))
    STATE.state.auto.tick()
    assert not STATE.state.auto.state.enabled
    assert not any(kind=='gv.update' for kind,payload in events)
    assert any(kind=='auto.error' for kind,payload in events)


def test_auto_bound_generation_uses_captured_rate_list(home,monkeypatch):
    monkeypatch.setattr(STATE.state.broadcast,'ensure_running',lambda:None)
    assert home.post('/auto-mode/on',json={'database':'HOMEOPATHY_Test','seed':0}).status_code==200
    auto=STATE.state.auto;frozen=copy.deepcopy(auto._rates_snapshot)
    assert len(frozen)==5
    monkeypatch.setattr(auto,'_find_rates',lambda db: (_ for _ in ()).throw(AssertionError('live catalog was used')))
    called=[]
    def analyse(rates,entropy):
        called.append(rates)
        from radiworks.core.analysis import AnalysisResult
        return AnalysisResult()
    monkeypatch.setattr(auto,'_analyse',analyse)
    auto._analyse_worker(auto._generation,'HOMEOPATHY_Test',1)
    assert called==[frozen]
