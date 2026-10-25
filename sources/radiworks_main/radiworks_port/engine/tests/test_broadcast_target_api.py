"""BC1 whole ingress routes, using artificial clients and one isolated app."""
import copy
import pytest
from radiworks.api.routes import STATE

def new_case(home,name='Synthetic A'):
    response=home.post('/cases',json={'name':name,'personalContext':{'firstName':'Ada','birthDate':'1980-02-29'},'focus':'Ruhe'})
    assert response.status_code==200,response.text
    return response.json()

def disable_worker(monkeypatch):monkeypatch.setattr(STATE.state.broadcast,'_start_thread',lambda:None)

@pytest.mark.parametrize('path,body,kind',[('/broadcast',{'signature':'Synthetic Rate','seconds':5},'direct'),('/images/broadcast',{'md5':'a'*64,'seconds':5},'image')])
def test_direct_and_image_bind_context_durably_and_keep_private_names_out_of_queue(home,monkeypatch,path,body,kind):
    case=new_case(home);disable_worker(monkeypatch)
    response=home.post(path,json=body)
    assert response.status_code==200,response.text
    reference=response.json()['targetReference']
    assert reference['binding']=='bound' and reference['caseId']==case['caseId']
    record=STATE.state.broadcast_targets.get(reference['jobId'])
    assert record['target']['contextSnapshot']['context']['personal']['firstName']=='Ada'
    assert record['target']['source']['kind']==kind
    assert 'contextSnapshot' not in response.json()
    original=copy.deepcopy(record['target'])
    assert home.post('/cases/current/metadata',json={'focus':'Other'}).status_code==200
    assert STATE.state.broadcast_targets.get(reference['jobId'])['target']==original

@pytest.mark.parametrize('path,body',[('/broadcast',{'signature':'Synthetic','seconds':5}),('/images/broadcast',{'md5':'b'*64,'seconds':5}),('/auto-mode/on',{'database':'HOMEOPATHY_Test'})])
def test_stale_selected_client_is_rejected_before_queue_or_auto(home,monkeypatch,path,body):
    new_case(home);disable_worker(monkeypatch)
    body={**body,'expected_case_ref':'0'*64,'expected_context_version':1}
    response=home.post(path,json=body)
    assert response.status_code==409,response.text
    assert STATE.state.broadcast.queue_state()['queued']==[]
    assert not STATE.state.auto.state.enabled

def test_accepted_old_draft_preserves_context_after_client_switch(home,monkeypatch):
    first=new_case(home);disable_worker(monkeypatch)
    analysis=home.post('/analysis',json={'database':'HOMEOPATHY_Test','seed':42}).json()
    snapshot=copy.deepcopy(analysis['draft']['contextSnapshot']);draft=analysis['draft']['id']
    assert home.post(f'/drafts/{draft}/transition',json={'status':'ready'}).status_code==200
    new_case(home,'Synthetic B')
    response=home.post(f'/drafts/{draft}/promote',json={'max_rates':1})
    assert response.status_code==200,response.text
    row=response.json()['broadcastEntries'][0]
    assert row['targetReference']['caseId']==first['caseId']
    assert STATE.state.broadcast_targets.get(row['targetReference']['jobId'])['target']['contextSnapshot']==snapshot

def test_no_case_is_explicit_and_acceptance_io_failure_leaves_no_queue(home,monkeypatch):
    disable_worker(monkeypatch)
    response=home.post('/broadcast',json={'signature':'Synthetic','seconds':5})
    assert response.status_code==200,response.text
    assert response.json()['targetReference']['binding']=='no-case'
    STATE.state.broadcast.stop_all()
    def fail(rows):raise OSError('synthetic acceptance IO')
    monkeypatch.setattr(STATE.state.broadcast_targets,'accept',fail)
    response=home.post('/broadcast',json={'signature':'Synthetic','seconds':5})
    assert response.status_code==503,response.text
    assert STATE.state.broadcast.queue_state()['queued']==[]

def test_auto_start_pins_context_and_provider_instead_of_rebinding(home,monkeypatch):
    case=new_case(home);disable_worker(monkeypatch)
    response=home.post('/auto-mode/on',json={'database':'HOMEOPATHY_Test'})
    assert response.status_code==200,response.text
    template=STATE.state.auto._target_template
    assert template.payload()['contextSnapshot']['caseId']==case['caseId']
    provider=STATE.state.auto._generation_provider
    assert provider is not None and provider is not STATE.state.live_provider
    assert home.post('/cases/current/metadata',json={'focus':'Other'}).status_code==200
    assert STATE.state.auto._target_template is template
    assert template.payload()['contextSnapshot']['context']['focus']=='Ruhe'
    assert home.post('/auto-mode/off').status_code==200


def test_rate_button_from_saved_analysis_uses_its_original_context_not_later_edits(home,monkeypatch):
    new_case(home);disable_worker(monkeypatch)
    analysis=home.post('/analysis',json={'database':'HOMEOPATHY_Test','seed':42}).json()
    snapshot=copy.deepcopy(analysis['draft']['contextSnapshot'])
    session=analysis['draft']['sessionId']
    current=home.get('/cases/current').json()
    ref=home.get('/cases/current/ref').json()['ref']
    changed=home.post('/cases/current/metadata',json={'personalContextChanges':{'firstName':'New'},'expected_case_ref':ref,'expected_context_version':current['contextVersion']})
    assert changed.status_code==200,changed.text
    response=home.post('/broadcast',json={'signature':'Synthetic Rate','seconds':5,'source_session_id':session})
    assert response.status_code==200,response.text
    target=STATE.state.broadcast_targets.get(response.json()['targetReference']['jobId'])['target']
    assert target['contextSnapshot']==snapshot
    assert target['source']['sessionId']==session


def test_unknown_analysis_origin_cannot_rebind_to_current_case(home,monkeypatch):
    new_case(home);disable_worker(monkeypatch)
    response=home.post('/broadcast',json={'signature':'Synthetic Rate','seconds':5,'source_session_id':'0'*32})
    assert response.status_code==409,response.text
    assert STATE.state.broadcast.queue_state()['queued']==[]


@pytest.mark.parametrize("initial_case", [True, False])
def test_result_draft_keeps_original_binding_without_session_status(home, monkeypatch, initial_case):
    if initial_case:
        new_case(home)
    disable_worker(monkeypatch)
    analysis = home.post("/analysis", json={"database": "HOMEOPATHY_Test", "seed": 42}).json()
    snapshot = copy.deepcopy(analysis["draft"]["contextSnapshot"])
    new_case(home, "Later Client")
    response = home.post("/broadcast", json={"signature": "Synthetic Rate", "seconds": 5, "source_draft_id": analysis["draft"]["id"]})
    assert response.status_code == 200, response.text
    target = STATE.state.broadcast_targets.get(response.json()["targetReference"]["jobId"])["target"]
    assert target["contextSnapshot"] == snapshot
    assert target["binding"] == ("bound" if initial_case else "no-case")
    assert target["source"]["draftId"] == analysis["draft"]["id"]


def test_unknown_or_conflicting_draft_source_never_rebinds(home, monkeypatch):
    new_case(home); disable_worker(monkeypatch)
    analysis = home.post("/analysis", json={"database": "HOMEOPATHY_Test", "seed": 42}).json()
    for origin in [{"source_draft_id": "00000000-0000-0000-0000-000000000000"},
                   {"source_draft_id": analysis["draft"]["id"], "source_session_id": "0" * 32}]:
        response = home.post("/broadcast", json={"signature": "Synthetic Rate", "seconds": 5, **origin})
        assert response.status_code == 409, response.text
    assert STATE.state.broadcast.queue_state()["queued"] == []
