"""Server-owned observation references must never follow an unrelated case."""
import copy

import pytest

from radiworks.api.routes import STATE
from radiworks.core.broadcast import BroadcastError, BroadcastManager
from radiworks.entropy import EntropyProvider
from radiworks.persistence import document_digest


def prepared_case(home, monkeypatch):
    assert home.post('/cases', json={'name': 'Synthetic binding case'}).status_code == 200
    run = home.post('/analysis', json={'database': 'HOMEOPATHY_Test', 'seed': 42}).json()
    draft_id = run['draft']['id']
    assert home.post(f'/drafts/{draft_id}/transition', json={'status': 'ready'}).status_code == 200
    state = STATE.state
    monkeypatch.setattr(state.broadcast, '_start_thread', lambda: None)
    return state, draft_id


def test_promoted_rates_keep_original_indices_and_case_session(home, monkeypatch):
    state, draft_id = prepared_case(home, monkeypatch)
    before = copy.deepcopy(state.case_store.current)
    session = before['sessionList'][-1]
    rates = session['analysisResult']['rateObjects']
    promoted = home.post(f'/drafts/{draft_id}/promote', json={'max_rates': 3})
    assert promoted.status_code == 200
    entries = promoted.json()['broadcastEntries']
    assert entries
    for entry in entries:
        binding = entry.get('observationBinding')
        assert binding is not None, 'Eligible promoted rate lost its server-owned session identity'
        assert binding['sessionId'] == session['sessionId']
        assert binding['draftId'] == draft_id
        assert binding['scope'] == state.scope.to_dict()
        assert binding['caseRef'] == state.case_store.reference_for_name(before['name'])
        assert binding['analysisDigest'] == document_digest(session['analysisResult'])
        assert entry['signature'].startswith(rates[binding['rateIndex']]['nameOrRate'])
        assert before['name'] not in str(binding)
    assert state.case_store.current == before
    assert [e['observationBinding'] for e in state.broadcast.queue_state()['queued']] == [
        e['observationBinding'] for e in entries
    ]


@pytest.mark.parametrize('change', ['case', 'revision', 'payload', 'draft'])
def test_unavailable_source_preserves_promotion_without_observation(home, monkeypatch, change):
    state, draft_id = prepared_case(home, monkeypatch)
    if change == 'case':
        assert home.post('/cases', json={'name': 'Other synthetic case'}).status_code == 200
    else:
        session = state.case_store.current['sessionList'][-1]
        if change == 'revision':
            session['revision'] += 1
        elif change == 'payload':
            session['analysisResult']['generalVitality'] += 1
        else:
            session['draftId'] = 'another-draft'
        state.case_store.save(state.case_store.current)
    response = home.post(f'/drafts/{draft_id}/promote', json={'max_rates': 1})
    assert response.status_code == 200
    assert response.json()['broadcastEntries']
    assert all('observationBinding' not in e for e in response.json()['broadcastEntries'])


def test_direct_broadcast_does_not_accept_client_observation_identity(home, monkeypatch):
    state = STATE.state
    monkeypatch.setattr(state.broadcast, '_start_thread', lambda: None)
    response = home.post('/broadcast', json={
        'signature': 'synthetic direct', 'seconds': 60,
        'observationBinding': {'caseRef': 'forged'},
    })
    assert response.status_code == 200
    assert 'observationBinding' not in response.json()
    assert 'observationBinding' not in state.broadcast.queue_state()['queued'][0]


def test_invalid_batch_identity_is_rejected_before_any_entry_is_accepted(monkeypatch):
    manager = BroadcastManager(EntropyProvider(42, 'seeded'), lambda *_: None)
    monkeypatch.setattr(manager, '_start_thread', lambda: None)
    accepted = []
    with pytest.raises(BroadcastError):
        manager.enqueue_batch([
            {'signature': 'synthetic first', 'seconds': 60},
            {'signature': 'synthetic invalid', 'seconds': 60, 'observationBinding': {'caseRef': 'forged'}},
        ], on_accepted=accepted.append)
    assert manager.queue_state()['queued'] == []
    assert not accepted


def test_duplicate_rate_names_keep_distinct_original_indices_after_sorting(home, monkeypatch):
    state, draft_id = prepared_case(home, monkeypatch)
    draft = state.draft_store.get(draft_id)
    rates = draft['payload']['rateObjects'][:2]
    for index, rate in enumerate(rates):
        rate.update(nameOrRate='synthetic duplicate', gv=800 + index * 100)
    draft['payload']['rateObjects'] = rates
    draft['payload']['generalVitality'] = 0
    session = state.case_store.current['sessionList'][-1]
    session['analysisResult'] = copy.deepcopy(draft['payload'])
    state.case_store.save(state.case_store.current)
    state.draft_store._write(draft)
    result = home.post(f'/drafts/{draft_id}/promote', json={'max_rates': 2})
    assert result.status_code == 200
    entries = result.json()['broadcastEntries']
    assert [e['observationBinding']['rateIndex'] for e in entries] == [1, 0]


def test_resonance_events_keep_the_pinned_identity(home, monkeypatch):
    state, draft_id = prepared_case(home, monkeypatch)
    response = home.post(f'/drafts/{draft_id}/promote', json={'max_rates': 1})
    assert response.status_code == 200
    binding = response.json()['broadcastEntries'][0]['observationBinding']
    with state.broadcast._lock:
        element = state.broadcast._queue.popleft()
        state.broadcast._active.append(element)
    monkeypatch.setattr(element.entropy_provider, 'get_integer', lambda lower, upper: upper)
    state.broadcast._resonance_draw(element)
    event = next(e for e in reversed(state.event_history) if e['type'] == 'broadcast.resonance')
    assert event['payload']['observationBinding'] == binding
    assert event['payload']['broadcastId'] == element.broadcast_id
    # Public snapshots are copies, not mutable aliases into an active element.
    snapshot = state.broadcast.queue_state()
    snapshot['active'][0]['observationBinding']['scope']['job_id'] = 'forged'
    assert element.payload()['observationBinding'] == binding


def test_copied_session_does_not_move_observation_to_another_case(home, monkeypatch):
    state, draft_id = prepared_case(home, monkeypatch)
    copied = copy.deepcopy(state.case_store.current)
    copied['name'] = 'Copied synthetic case'
    assert home.post('/cases', json=copied).status_code == 200
    result = home.post(f'/drafts/{draft_id}/promote', json={'max_rates': 1})
    assert result.status_code == 200
    assert result.json()['broadcastEntries']
    assert all('observationBinding' not in e for e in result.json()['broadcastEntries'])


@pytest.mark.parametrize('invalid', ['[]', 'null', '3'])
def test_invalid_optional_case_document_keeps_legacy_promotion(home, monkeypatch, invalid):
    state, draft_id = prepared_case(home, monkeypatch)
    case_file = state.case_store._case_path(state.case_store.current['name'])
    case_file.write_text(invalid, encoding='utf-8')
    result = home.post(f'/drafts/{draft_id}/promote', json={'max_rates': 1})
    assert result.status_code == 200
    assert result.json()['broadcastEntries']
    assert all('observationBinding' not in e for e in result.json()['broadcastEntries'])


def test_entry_cannot_reassign_the_pinned_identity(home, monkeypatch):
    state, draft_id = prepared_case(home, monkeypatch)
    assert home.post(f'/drafts/{draft_id}/promote', json={'max_rates': 1}).status_code == 200
    element = state.broadcast._queue[0]
    assert element.observation_binding is not None
    with pytest.raises(AttributeError):
        element.observation_binding = None


def test_entry_cannot_delete_the_pinned_identity(home, monkeypatch):
    state, draft_id = prepared_case(home, monkeypatch)
    assert home.post(f'/drafts/{draft_id}/promote', json={'max_rates': 1}).status_code == 200
    element = state.broadcast._queue[0]
    binding = element.observation_binding
    with pytest.raises(AttributeError):
        del element.observation_binding
    assert element.observation_binding is binding
