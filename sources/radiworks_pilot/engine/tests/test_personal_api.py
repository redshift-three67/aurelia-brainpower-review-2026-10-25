"""Personal API stays separate from confirmed Original/EXP1 sessions."""
import json
import time
import pytest
from radiworks.api.routes import STATE


def client_context(home):
    r=home.post('/cases',json={'titleMode':'context','personalContext':{'firstName':'Synthetic','birthDate':'1980-02-29','place':'Exampleton','placeKind':'birth'},'focus':'Rate'})
    assert r.status_code==200,r.text
    return r.json(),r.headers['X-RadiWorks-Case-Ref']


def ready(monkeypatch):
    ctrl=STATE.state.personal
    monkeypatch.setattr(ctrl,'capability',lambda:{'configured':True})
    # API assertions use a real bounded stream child with artificial numeric rows.
    # Numerical equality is proved separately against the real CPU worker.
    from test_personal_controller import attach_child, stream_script
    script,args=stream_script()
    attach_child(monkeypatch,ctrl,script,args)
    return ctrl


def command(case,ref,request='a'*32,mode='seeded'):
    return {'expected_case_ref':ref,'expected_context_version':case['contextVersion'],'request_id':request,'database':'HOMEOPATHY_Test.txt','mode':mode,'seed':0 if mode=='seeded' else None}


def finished(home,job,ref):
    end=time.monotonic()+5
    while time.monotonic()<end:
        r=home.get(f"/personal-analyses/{job['id']}",params={'case_ref':ref})
        assert r.status_code==200,r.text
        if r.json()['status'] in {'completed','failed'}:return r.json()
        time.sleep(.01)
    pytest.fail('personal job did not complete')


def test_complete_personal_api_does_not_mutate_original_sessions_or_gv(home,monkeypatch):
    case,ref=client_context(home);ready(monkeypatch)
    before=home.get('/cases/current').json()
    response=home.post('/personal-analyses',json=command(case,ref))
    assert response.status_code==200,response.text
    result=finished(home,response.json(),ref)
    assert result['status']=='completed' and result['totalRates']==5
    assert len(result['rows'])==5 and result['rows'][0]['inputIndex']==4
    assert result['procedure']=='radi144-personal-v1' and result['mode']=='seeded'
    assert home.get('/cases/current').json()==before
    assert 'contextSnapshot' not in result and 'catalog' not in str(result['rows'])
    assert all('gv' not in r and 'energeticValue' not in r for r in result['rows'])


def test_stochastic_api_has_own_journal_and_idempotent_retry_draws_nothing(home,monkeypatch):
    from cryptography.fernet import Fernet
    monkeypatch.setenv('RADIOWORKS_JOURNAL_KEY',Fernet.generate_key().decode('ascii'))
    case,ref=client_context(home);ctrl=ready(monkeypatch)
    STATE.state.entropy_feed.feed(list(range(100,110)))
    body=command(case,ref,mode='stochastic')
    response=home.post('/personal-analyses',json=body)
    assert response.status_code==200,response.text
    result=finished(home,response.json(),ref)
    stored=ctrl.store.get(result['id'])['input']
    assert result['entropy']['sources']==['webcam'] and stored['entropy']['journalCursor']==5
    remaining=len(STATE.state.entropy_feed)
    repeated=home.post('/personal-analyses',json=body)
    assert repeated.status_code==200 and repeated.json()['id']==result['id']
    assert len(STATE.state.entropy_feed)==remaining
    assert home.get('/cases/current').json()['sessionList']==[]


def test_stale_context_and_missing_stochastic_key_do_not_admit_personal_job(home,monkeypatch):
    monkeypatch.delenv('RADIOWORKS_JOURNAL_KEY',raising=False)
    case,ref=client_context(home);ctrl=ready(monkeypatch)
    body=command(case,ref);body['expected_context_version']+=1
    assert home.post('/personal-analyses',json=body).status_code==409
    assert home.post('/personal-analyses',json=command(case,ref,mode='stochastic')).status_code==503
    assert ctrl.store.list()==[]


def test_personal_job_cannot_be_read_or_cancelled_from_another_case(home,monkeypatch):
    case,ref=client_context(home);ready(monkeypatch)
    response=home.post('/personal-analyses',json=command(case,ref))
    assert response.status_code==200,response.text
    job=finished(home,response.json(),ref)
    other=home.post('/cases',json={'name':'Other Synthetic'});other_ref=other.headers['X-RadiWorks-Case-Ref']
    assert home.get(f"/personal-analyses/{job['id']}",params={'case_ref':other_ref}).status_code==404
    assert home.post(f"/personal-analyses/{job['id']}/cancel",json={'expected_case_ref':other_ref}).status_code==404


@pytest.mark.parametrize('mode',['seeded','stochastic'])
def test_personal_selected_rate_broadcast_binds_completed_job_context(home,monkeypatch,mode):
    if mode=='stochastic':
        from cryptography.fernet import Fernet
        monkeypatch.setenv('RADIOWORKS_JOURNAL_KEY',Fernet.generate_key().decode('ascii'))
        STATE.state.entropy_feed.feed(list(range(100,120)))
    case,ref=client_context(home);ctrl=ready(monkeypatch)
    monkeypatch.setattr(STATE.state.broadcast,'_start_thread',lambda:None)
    started=home.post('/personal-analyses',json=command(case,ref,mode=mode))
    assert started.status_code==200,started.text
    job=finished(home,started.json(),ref);original=ctrl.store.get(job['id'])['input']['contextSnapshot']
    assert home.post('/cases/current/metadata',json={'focus':'After','expected_case_ref':ref,'expected_context_version':case['contextVersion']}).status_code==200
    r=home.post('/broadcast',json={'signature':job['rows'][0]['rate'],'seconds':5,'source_personal_job_id':job['id'],'source_personal_input_index':job['rows'][0]['inputIndex']})
    assert r.status_code==200,r.text
    reference=r.json()['targetReference']
    stored=STATE.state.broadcast_targets.get(reference['jobId'])
    assert stored['target']['procedure']=='radi144-personal-v1'
    assert stored['target']['entropyMode']==mode
    assert stored['target']['contextSnapshot']==original
    assert stored['target']['source']['personalJobId']==job['id']
    assert 'entropyCheckpoint' not in r.json() and 'contextSnapshot' not in r.json()
    wrong=home.post('/broadcast',json={'signature':'Not selected','seconds':5,'source_personal_job_id':job['id'],'source_personal_input_index':job['rows'][0]['inputIndex']})
    assert wrong.status_code==409


def test_original_stochastic_draft_rate_keeps_mode_in_separate_broadcast(home,monkeypatch):
    from cryptography.fernet import Fernet
    monkeypatch.setenv('RADIOWORKS_JOURNAL_KEY',Fernet.generate_key().decode('ascii'))
    client_context(home);monkeypatch.setattr(STATE.state.broadcast,'_start_thread',lambda:None)
    from radiworks.entropy import RandomOrgSource
    STATE.state.random_org=RandomOrgSource(http_get=None)
    result=home.post('/analysis',json={'database':'HOMEOPATHY_Test','mode':'stochastic'})
    assert result.status_code==200,result.text
    r=home.post('/broadcast',json={'signature':'Synthetic','seconds':5,'source_draft_id':result.json()['draft']['id']})
    assert r.status_code==200,r.text
    assert r.json()['targetReference']['entropyMode']=='stochastic'


def test_personal_duplicate_rate_broadcast_binds_exact_input_index(home,monkeypatch):
    from cryptography.fernet import Fernet
    monkeypatch.setenv('RADIOWORKS_JOURNAL_KEY',Fernet.generate_key().decode('ascii'))
    case,ref=client_context(home);ctrl=ready(monkeypatch)
    STATE.state.random_org._http_get=None
    catalog=STATE.state.rate_repository.data_dir / 'DUPLICATE.txt'
    catalog.write_text('Synthetic duplicate\nSynthetic duplicate\n',encoding='utf8')
    STATE.state.rate_repository.refresh()
    body=command(case,ref,mode='stochastic');body['database']='DUPLICATE.txt'
    started=home.post('/personal-analyses',json=body)
    assert started.status_code==200,started.text
    job=finished(home,started.json(),ref)
    monkeypatch.setattr(STATE.state.broadcast,'_start_thread',lambda:None)
    for row in job['rows']:
        response=home.post('/broadcast',json={'signature':row['rate'],'seconds':5,'source_personal_job_id':job['id'],'source_personal_input_index':row['inputIndex']})
        assert response.status_code==200,response.text
        stored=STATE.state.broadcast_targets.get(response.json()['targetReference']['jobId'])
        assert stored['target']['source']['personalInputIndex']==row['inputIndex']
    assert home.post('/broadcast',json={'signature':job['rows'][0]['rate'],'seconds':5,'source_personal_job_id':job['id']}).status_code==409
    assert home.post('/broadcast',json={'signature':job['rows'][0]['rate'],'seconds':5,'source_personal_job_id':job['id'],'source_personal_input_index':20}).status_code==409


def test_promoted_original_stochastic_draft_keeps_own_mode_and_journal(home,monkeypatch):
    from cryptography.fernet import Fernet
    from radiworks.entropy import RandomOrgSource
    monkeypatch.setenv('RADIOWORKS_JOURNAL_KEY',Fernet.generate_key().decode('ascii'))
    client_context(home);state=STATE.state
    monkeypatch.setattr(state.broadcast,'_start_thread',lambda:None)
    state.random_org=RandomOrgSource(http_get=None)
    response=home.post('/analysis',json={'database':'HOMEOPATHY_Test','mode':'stochastic'})
    assert response.status_code==200,response.text
    draft=response.json()['draft']['id']
    assert home.post(f'/drafts/{draft}/transition',json={'status':'ready'}).status_code==200
    promoted=home.post(f'/drafts/{draft}/promote',json={'max_rates':1})
    assert promoted.status_code==200,promoted.text
    entry=promoted.json()['broadcastEntries'][0]
    assert entry['targetReference']['entropyMode']=='stochastic'
    stored=state.broadcast_targets.get(entry['targetReference']['jobId'])
    assert stored['entropyCheckpoint']['checkpoint']['journalId']
    assert stored['entropyCheckpoint']['checkpoint']['journalId']!=state.case_store.current['sessionList'][-1]['entropyCheckpoint']['journalId']
