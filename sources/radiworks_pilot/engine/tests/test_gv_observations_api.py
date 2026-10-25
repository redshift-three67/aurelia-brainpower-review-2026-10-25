from cryptography.fernet import Fernet
import pytest
from radiworks.api.routes import STATE

def prepared(home, monkeypatch):
    state = STATE.state
    monkeypatch.setattr(state.broadcast, '_start_thread', lambda: None)
    assert home.post('/cases', json={'name': 'Synthetic GV2'}).status_code == 200
    analysis = home.post('/analysis', json={'database': 'HOMEOPATHY_Test', 'seed': 42}).json()
    draft = analysis['draft']['id']
    assert home.post(f'/drafts/{draft}/transition', json={'status': 'ready'}).status_code == 200
    response = home.post(f'/drafts/{draft}/promote', json={'max_rates': 1})
    assert response.status_code == 200
    entry = response.json()['broadcastEntries'][0]
    state.broadcast._promote_from_queue()
    return state, entry

def test_api_default_off_explicit_enable_and_key_gate(home, monkeypatch):
    state, entry = prepared(home, monkeypatch)
    response = home.get('/gv-observations')
    assert response.status_code == 200, 'GV2 API missing'
    assert not response.json()['controls']
    monkeypatch.delenv('RADIOWORKS_JOURNAL_KEY', raising=False)
    path = '/gv-observations/' + entry['broadcastId']
    assert home.post(path, json={'enabled': True}).status_code == 503
    monkeypatch.setenv('RADIOWORKS_JOURNAL_KEY', Fernet.generate_key().decode())
    enabled = home.post(path, json={'enabled': True})
    assert enabled.status_code == 200
    assert enabled.json()['controls'][0]['nextInSeconds'] == 1260
    assert home.post(path, json={'enabled': 1}).status_code == 422
    assert home.post(path, json={'enabled': True, 'caseRef': 'fake'}).status_code == 422
    assert home.post(path, json={'enabled': False}).status_code == 200
    assert not home.get('/gv-observations').json()['controls'][0]['enabled']

def test_api_history_filter_never_reassigns_current_case(home, monkeypatch):
    state, entry = prepared(home, monkeypatch)
    monkeypatch.setenv('RADIOWORKS_JOURNAL_KEY', Fernet.generate_key().decode())
    now = [0.0]
    state.observations._clock = lambda: now[0]
    assert home.post('/gv-observations/' + entry['broadcastId'], json={'enabled': True}).status_code == 200
    original = state.case_store.current.copy()
    assert home.post('/cases', json={'name': 'Other synthetic case'}).status_code == 200
    now[0] = 1260
    state.observations.tick()
    rows = home.get('/gv-observations/history', params={'session_id': entry['observationBinding']['sessionId']}).json()['records']
    assert len(rows) == 1
    assert rows[0]['binding'] == entry['observationBinding']
    assert rows[0]['entropy']['activeSource'] == 'os'
    assert home.get('/gv-observations/history', params={'case_ref': '0'*64}).json()['records'] == []
    assert home.get('/gv-observations/history', params={'session_id': '../escape'}).status_code == 422
    assert state.case_store.current['name'] == 'Other synthetic case'
    assert home.get('/gv-observations', headers={'Origin': 'https://invalid.example'}).status_code == 400


def test_independent_observation_entropy_keeps_legacy_receipt_schema(tmp_path,monkeypatch):
    from radiworks.core.gv_observations import journaled_os_draw, validate_entropy
    monkeypatch.setenv('RADIOWORKS_JOURNAL_KEY',Fernet.generate_key().decode())
    sample=journaled_os_draw(tmp_path)
    validate_entropy(sample['entropy'])
    assert sample['entropy']['activeSource']=='os'
