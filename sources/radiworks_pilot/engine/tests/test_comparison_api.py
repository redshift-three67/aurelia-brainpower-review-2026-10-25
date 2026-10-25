import copy, json, time, os
from pathlib import Path
import pytest
from radiworks.api.routes import STATE
from test_comparison_basis import PERSONAL


def original(home):
    saved=home.post('/cases',json={'name':'Synthetic comparison','focus':'Arnica','personalContext':PERSONAL})
    assert saved.status_code==200,saved.text
    analyzed=home.post('/analysis',json={'database':'HOMEOPATHY_Test','mode':'seeded','seed':29,'max_hits':100})
    assert analyzed.status_code==200,analyzed.text
    case=home.get('/cases/current');ref=case.headers['X-RadiWorks-Case-Ref']
    return case.json(),ref


def test_original_captures_private_source_atomically_without_public_catalog(home):
    case,ref=original(home);session=case['sessionList'][-1]
    assert 'comparisonBasis' in session
    assert 'content' not in json.dumps(session['comparisonBasis'])
    reply=home.get('/comparisons/sources',params={'case_ref':ref})
    assert reply.status_code==200,reply.text
    assert reply.json()['sources'][0]['sessionId']==session['sessionId']
    assert 'Abrotanum' not in reply.text
    state=STATE.state
    source=state.comparisons.root.parent/'comparison_sources'/(session['sessionId']+'.json')
    assert source.is_file()
    assert 'Abrotanum' in source.read_text(encoding='utf-8')


def test_comparison_api_case_binding_and_missing_cpu_fail_closed(home):
    case,ref=original(home);session=case['sessionList'][-1];before=copy.deepcopy(case)
    body={'expected_case_ref':ref,'source_session_id':session['sessionId'],'page_start':0,'weight':'Normal','request_id':'a'*32}
    assert home.post('/comparisons',json={**body,'expected_case_ref':'0'*64}).status_code==409
    response=home.post('/comparisons',json=body)
    assert response.status_code==503,response.text
    assert home.get('/cases/current').json()==before
    assert home.get('/comparisons',params={'case_ref':ref}).json()['jobs']==[]
    assert home.get('/comparisons/sources',params={'case_ref':'0'*64}).status_code==409


def test_legacy_or_catalog_tamper_visible_without_original_mutation(home):
    case,ref=original(home);state=STATE.state;session=case['sessionList'][-1]
    source=state.comparisons.root.parent/'comparison_sources'/(session['sessionId']+'.json')
    source.write_text('{}',encoding='utf-8')
    response=home.get('/comparisons/sources',params={'case_ref':ref})
    assert response.status_code==200,response.text
    assert response.json()['sources'][0]['eligible'] is False
    assert home.get('/cases/current').json()==case


def test_true_cpu_api_comparison_has_private_inputs_and_own_session(home,monkeypatch):
    deps=os.environ.get('RADIOWORKS_EXP1_TEST_DEPS')
    if not deps:pytest.skip('explicit CPU test profile not configured')
    state=STATE.state;state.comparisons.deps_dir=Path(deps)
    case,ref=original(home);session=case['sessionList'][-1]
    body={'expected_case_ref':ref,'source_session_id':session['sessionId'],'page_start':0,'weight':'Normal','request_id':'b'*32}
    reply=home.post('/comparisons',json=body);assert reply.status_code==200,reply.text
    job=reply.json();limit=time.monotonic()+30
    while job['status'] in ('queued','running') and time.monotonic()<limit:
        time.sleep(.05);reply=home.get('/comparisons/'+job['id'],params={'case_ref':ref});assert reply.status_code==200;job=reply.json()
    assert job['status']=='completed',job
    assert job['comparisonSessionId']!=session['sessionId']
    assert 'contextSnapshot' not in job and 'content' not in json.dumps(job)
    assert 'preparedContext' not in job['result']
    assert job['result']['parameters']['candidateCount']==80000
    assert home.get('/cases/current').json()==case
    assert len(home.get('/comparisons',params={'case_ref':ref}).json()['jobs'])==1
    home.post('/cases',json={'name':'Other synthetic','personalContext':PERSONAL})
    otherref=home.get('/cases/current').headers['X-RadiWorks-Case-Ref']
    assert home.get('/comparisons/'+job['id'],params={'case_ref':otherref}).status_code==404

def test_stochastic_original_subset_compares_without_consuming_original_entropy(home,monkeypatch,tmp_path):
    from cryptography.fernet import Fernet
    from radiworks.entropy import RandomOrgSource
    deps=os.environ.get('RADIOWORKS_EXP1_TEST_DEPS')
    if not deps:pytest.skip('explicit CPU test profile not configured')
    monkeypatch.setenv('RADIOWORKS_JOURNAL_KEY',Fernet.generate_key().decode())
    state=STATE.state;state.comparisons.deps_dir=Path(deps);state.random_org=RandomOrgSource(http_get=None)
    assert home.post('/cases',json={'name':'Synthetic stochastic comparison','personalContext':PERSONAL,'focus':'Arnica'}).status_code==200
    analyzed=home.post('/analysis',json={'database':'HOMEOPATHY_Test','mode':'stochastic','max_hits':100})
    assert analyzed.status_code==200,analyzed.text
    response=home.get('/cases/current');case=response.json();ref=response.headers['X-RadiWorks-Case-Ref'];session=case['sessionList'][-1]
    assert session['passport']['entropy_mode']=='stochastic'
    before={p.name:p.read_bytes() for p in state.journal_dir.glob('*') if p.is_file()}
    queue_before=state.broadcast.queue_state()
    def forbidden(*a,**kw):raise AssertionError('comparison consumed Original entropy')
    monkeypatch.setattr(state,'new_provider',forbidden)
    started=home.post('/comparisons',json={'expected_case_ref':ref,'source_session_id':session['sessionId'],'page_start':0,'weight':'Normal','request_id':'d'*32})
    assert started.status_code==200,started.text
    job=started.json();limit=time.monotonic()+30
    while job['status'] in ('queued','running') and time.monotonic()<limit:
        time.sleep(.05);job=home.get('/comparisons/'+job['id'],params={'case_ref':ref}).json()
    assert job['status']=='completed',job
    assert job['result']['inputRates']==[r['nameOrRate'] for r in session['analysisBaseline']['rateObjects'][:21]]
    assert home.get('/cases/current').json()==case
    assert {p.name:p.read_bytes() for p in state.journal_dir.glob('*') if p.is_file()}==before
    assert state.broadcast.queue_state()==queue_before
