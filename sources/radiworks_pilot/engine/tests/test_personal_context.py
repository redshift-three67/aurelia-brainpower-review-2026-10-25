"""VF2 synthetic context identity, validation and preservation contracts."""
import copy
import json
import re
import pytest
from radiworks.api.routes import STATE
from radiworks.core.cases import CaseStore
from radiworks.scope import ScopeContext

PERSONAL = {'firstName': '  Zoë  ', 'lastName': 'Mu\u0308ller', 'birthDate': '1980-02-29', 'place': ' Berlin '}

def create(home, name='Synthetic Context', personal=None):
    body = {'name': name, 'focus': 'Pflanzen'}
    if personal is not None:
        body['personalContext'] = personal
    response = home.post('/cases', json=body)
    assert response.status_code == 200, response.text
    return response.json()

def analyze(home):
    response = home.post('/analysis', json={'database': 'HOMEOPATHY_Test', 'seed': 42, 'mode': 'seeded'})
    assert response.status_code == 200, response.text
    return response.json()

def test_server_identity_normalization_original_and_no_identity_guess(home):
    created = create(home, personal=PERSONAL)
    assert re.fullmatch('[0-9a-f]{32}', created.get('caseId', '')), 'missing server-owned case identity'
    assert created['contextVersion'] == 1
    assert created['personalContext']['firstName'] == 'Zoë'
    assert created['personalContext']['lastName'] == 'Müller'
    assert created['personalContext']['place'] == 'Berlin'
    assert created['personalContextOriginal'] == PERSONAL
    blank = create(home, 'Synthetic Legacy Name 1980')
    assert all(value is None for value in blank['personalContext'].values())
    assert blank['caseId'] != created['caseId']

@pytest.mark.parametrize('personal', [
    {'birthDate': '2023-02-29'}, {'birthDate': '29.02.1980'},
    {'firstName': 'x'*161}, {'place': ['Berlin']}, {'firstName': 'A\x00B'},
    {'birthDate': True}, {'unknown': 'value'}, 'not an object',
    {'image': {'sha256': 'a'*64, 'mediaType': 'image/svg+xml', 'byteLength': 5}},
    {'image': {'sha256': 'a'*64, 'mediaType': 'image/png', 'byteLength': True}},
])
def test_invalid_context_rejected_without_creating_case(home, personal):
    result = home.post('/cases', json={'name': 'Synthetic Invalid', 'personalContext': personal})
    assert result.status_code == 422
    assert home.get('/cases').json()['entries'] == []

def test_context_update_version_noop_and_old_analysis_preserved(home):
    created = create(home, personal=PERSONAL)
    first = analyze(home)
    original = copy.deepcopy(STATE.state.case_store.current['sessionList'][0])
    snapshot = first['draft'].get('contextSnapshot')
    assert snapshot is not None, 'new analysis lacks pinned personal context'
    assert snapshot == original['contextSnapshot']
    ref = home.get('/cases/current/ref').json()['ref']
    edit = home.post('/cases/current/metadata', json={
        'personalContext': {'firstName': 'Other', 'birthDate': '1991-01-02'},
        'focus': 'Mineralien', 'expected_case_ref': ref,
        'expected_context_version': created['contextVersion'],
    })
    assert edit.status_code == 200, edit.text
    assert edit.json()['caseId'] == created['caseId']
    assert edit.json()['contextVersion'] == 2
    assert STATE.state.case_store.current['sessionList'][0] == original
    second = analyze(home)
    assert first['result'] == second['result']
    newer = second['draft']['contextSnapshot']
    assert newer['context']['personal']['firstName'] == 'Other'
    assert newer['digest'] != snapshot['digest']
    noop = home.post('/cases/current/metadata', json={'focus': 'Mineralien', 'expected_case_ref': ref, 'expected_context_version': 2})
    assert noop.status_code == 200
    assert noop.json()['contextVersion'] == 2
    stale = home.post('/cases/current/metadata', json={'focus': 'stale', 'expected_case_ref': ref, 'expected_context_version': 1})
    assert stale.status_code == 409
    assert home.get(f"/drafts/{first['draft']['id']}").json()['contextSnapshot'] == snapshot

def test_legacy_load_does_not_write_or_guess_identity(tmp_path):
    path = tmp_path/'Legacy.json'
    doc = {'name': 'Legacy', 'sessionList': [{'analysisResult': {'rateObjects': []}}]}
    path.write_text(json.dumps(doc), encoding='utf-8')
    before = path.read_bytes()
    store = CaseStore(tmp_path)
    loaded = store.load('Legacy', record_recent=False)
    assert loaded == doc
    assert path.read_bytes() == before
    planned = store.plan_attach_analysis({'rateObjects': []}, {})
    assert 'caseId' in planned[0], 'new legacy-case analysis requires stable identity'
    assert 'contextSnapshot' in planned[1]
    assert loaded == doc
    assert planned[0]['sessionList'][0] == doc['sessionList'][0]

def test_gv_successor_inherits_snapshot_not_edited_context(home):
    create(home, personal=PERSONAL)
    analysis = analyze(home)
    state = STATE.state
    original = copy.deepcopy(state.case_store.current['sessionList'][0].get('contextSnapshot'))
    assert original is not None
    assert home.post('/cases/current/metadata', json={'focus': 'New focus'}).status_code == 200
    for _ in range(7):
        assert home.post('/analysis/gv-round', json={}).status_code == 200
    sessions = state.case_store.current['sessionList']
    assert len(sessions) == 2
    assert sessions[0]['contextSnapshot'] == original
    assert sessions[1]['contextSnapshot'] == original
    childdraft = state.draft_store.get(sessions[1]['draftId'])
    assert childdraft['contextSnapshot'] == original

def test_promoted_queue_has_only_detached_immutable_context_reference(home, monkeypatch):
    create(home, personal=PERSONAL)
    result = analyze(home)
    snapshot = result['draft'].get('contextSnapshot')
    assert snapshot is not None
    state = STATE.state
    monkeypatch.setattr(state.broadcast, '_start_thread', lambda: None)
    draftid = result['draft']['id']
    assert home.post(f'/drafts/{draftid}/transition', json={'status': 'ready'}).status_code == 200
    promoted = home.post(f'/drafts/{draftid}/promote', json={'max_rates': 1})
    assert promoted.status_code == 200, promoted.text
    entry = promoted.json()['broadcastEntries'][0]
    assert entry['contextReference']['digest'] == snapshot['digest']
    assert entry['contextReference']['caseId'] == snapshot['caseId']
    assert 'Zoë' not in json.dumps(entry, ensure_ascii=False)
    element = state.broadcast._queue[0]
    entry['contextReference']['digest'] = '0'*64
    assert element.payload()['contextReference']['digest'] == snapshot['digest']
    with pytest.raises(AttributeError):
        element.context_reference = None
    assert home.post('/cases/current/metadata', json={'focus': 'Changed'}).status_code == 200
    assert element.payload()['contextReference']['digest'] == snapshot['digest']

def test_valid_image_metadata_reference_is_retained_but_not_a_decoded_image_claim(home):
    image = {'sha256': 'b'*64, 'mediaType': 'image/png', 'byteLength': 1000}
    created = create(home, personal={'image': image})
    assert created['personalContext']['image'] == image
    result = analyze(home)
    assert result['draft']['contextSnapshot']['context']['personal']['image'] == image


def test_new_case_rejects_injected_server_identity(home):
    response = home.post('/cases', json={'name': 'Synthetic Forged', 'caseId': 'a'*32, 'contextVersion': 9})
    assert response.status_code == 422, 'caller may inject server identity/version'

def test_raw_update_preserves_context_when_fields_are_omitted(home):
    created = create(home, personal=PERSONAL)
    response = home.post('/cases', json={'name': created['name'], 'description': 'Changed via legacy caller'})
    assert response.status_code == 200, response.text
    assert response.json()['caseId'] == created['caseId']
    assert response.json()['personalContext'] == created['personalContext']

def test_context_scope_and_digest_tamper_blocks_promotion(home):
    from radiworks.core.personal_context import ContextSnapshot
    from radiworks.core.draft import DraftError
    created = create(home, personal=PERSONAL)
    response = analyze(home)
    draft = STATE.state.draft_store.get(response['draft']['id'])
    snapshot = draft['contextSnapshot']
    broken = copy.deepcopy(snapshot)
    broken['context']['personal']['firstName'] = 'Changed'
    with pytest.raises(ValueError):
        ContextSnapshot.from_payload(broken)
    altered = ContextSnapshot.from_payload(snapshot).payload()
    altered['context']['personal']['firstName'] = 'Copy changed'
    assert ContextSnapshot.from_payload(snapshot).payload()['context']['personal']['firstName'] == 'Zoë'
    draft['status'] = 'ready'
    draft['contextSnapshot'] = broken
    STATE.state.draft_store.write_planned(draft)
    with pytest.raises(DraftError, match='Auftragskontext'):
        STATE.state.draft_store.prepare_promotion(draft['id'])

def test_context_identity_persists_after_case_store_restart(tmp_path):
    scope = ScopeContext('tenant','client','job')
    store = CaseStore(tmp_path, scope=scope)
    created = store.save({'name': 'Synthetic Restart', 'focus': 'Plants', 'personalContext': PERSONAL})
    original = copy.deepcopy(created)
    reloaded = CaseStore(tmp_path, scope=scope).load('Synthetic Restart', record_recent=False)
    assert reloaded == original
    changed = CaseStore(tmp_path, scope=scope)
    changed.load('Synthetic Restart', record_recent=False)
    doc = copy.deepcopy(changed.current)
    doc['focus'] = 'Other'
    updated = changed.save(doc)
    assert updated['caseId'] == original['caseId']
    assert updated['contextVersion'] == original['contextVersion'] + 1

def test_snapshot_reference_cannot_be_deleted(home, monkeypatch):
    create(home)
    result = analyze(home)
    state = STATE.state
    monkeypatch.setattr(state.broadcast, '_start_thread', lambda: None)
    identifier = result['draft']['id']
    assert home.post(f'/drafts/{identifier}/transition', json={'status':'ready'}).status_code == 200
    assert home.post(f'/drafts/{identifier}/promote', json={'max_rates':1}).status_code == 200
    with pytest.raises(AttributeError):
        del state.broadcast._queue[0].context_reference


def test_metadata_rename_preserves_single_identity_monotone_version_and_old_context(home):
    created = create(home, personal=PERSONAL)
    result = analyze(home)
    assert home.post('/cases/current/metadata', json={'focus':'Minerals'}).status_code == 200
    before = copy.deepcopy(STATE.state.case_store.current)
    ref = home.get('/cases/current/ref').json()['ref']
    renamed = home.post('/cases/current/metadata', json={'name':'Synthetic Renamed', 'expected_case_ref':ref})
    assert renamed.status_code == 200, renamed.text
    assert renamed.json()['caseId'] == created['caseId']
    assert renamed.json()['contextVersion'] == before['contextVersion'] + 1
    assert len(home.get('/cases').json()['entries']) == 1
    assert home.get('/cases/current/ref').json()['ref'] == ref
    assert STATE.state.case_store.current['sessionList'] == before['sessionList']
    assert home.post('/cases/ref/'+ref+'/activate').status_code == 200

@pytest.mark.parametrize('mutation', ['edit','remove','stale'])
def test_raw_case_save_cannot_rewrite_or_drop_session_snapshot(home, mutation):
    create(home, personal=PERSONAL)
    first = analyze(home)
    before = copy.deepcopy(STATE.state.case_store.current)
    incoming = copy.deepcopy(before)
    if mutation == 'edit':
        from radiworks.persistence import document_digest
        snap = incoming['sessionList'][0]['contextSnapshot']
        snap['context']['focus'] = 'Forged'
        snap['digest'] = document_digest({key:value for key,value in snap.items() if key != 'digest'})
    elif mutation == 'remove':
        incoming['sessionList'][0].pop('contextSnapshot')
    else:
        second = analyze(home)
        before = copy.deepcopy(STATE.state.case_store.current)
    response = home.post('/cases', json=incoming)
    assert response.status_code in (409,422), response.text
    assert STATE.state.case_store.current == before

def test_null_personal_context_is_controlled_and_empty(home):
    response = home.post('/cases', json={'name':'Synthetic Null','personalContext':None})
    assert response.status_code == 200, response.text
    assert all(value is None for value in response.json()['personalContext'].values())

def test_explicit_clone_mints_new_case_identity_preserving_historical_provenance(home):
    original = create(home, personal=PERSONAL)
    result = analyze(home)
    source = copy.deepcopy(STATE.state.case_store.current)
    cloned = copy.deepcopy(source)
    cloned['name'] = 'Synthetic Clone'
    response = home.post('/cases', json=cloned)
    assert response.status_code == 200, response.text
    assert response.json()['caseId'] != original['caseId']
    assert response.json()['contextVersion'] == 1
    assert response.json()['sessionList'][0]['contextSnapshot']['caseId'] == original['caseId']
    assert len(home.get('/cases').json()['entries']) == 2


def test_clone_cannot_forge_historical_source_context(home):
    from radiworks.persistence import document_digest
    create(home, personal=PERSONAL)
    analyze(home)
    before = copy.deepcopy(STATE.state.case_store.current)
    clone = copy.deepcopy(before)
    clone['name'] = 'Synthetic Forged Clone'
    snap = clone['sessionList'][0]['contextSnapshot']
    snap['context']['focus'] = 'Forged source'
    snap['digest'] = document_digest({key:value for key,value in snap.items() if key != 'digest'})
    response = home.post('/cases', json=clone)
    assert response.status_code in (409,422), response.text
    assert STATE.state.case_store.current == before
    assert len(home.get('/cases').json()['entries']) == 1

def test_legacy_session_cannot_be_enriched_afterwards(home):
    create(home, personal=PERSONAL)
    response = analyze(home)
    snapshot = copy.deepcopy(response['draft']['contextSnapshot'])
    legacy = home.post('/cases', json={'name':'Synthetic Legacy Session',
        'sessionList':[{'sessionId':'a'*32, 'analysisResult':{'rateObjects':[]}}]})
    assert legacy.status_code == 200
    before = copy.deepcopy(STATE.state.case_store.current)
    tampered = copy.deepcopy(before)
    tampered['sessionList'][0]['contextSnapshot'] = snapshot
    response = home.post('/cases', json=tampered)
    assert response.status_code in (409,422), response.text
    assert STATE.state.case_store.current == before

def test_direct_attach_helper_pins_context_and_fork_checkpoint(tmp_path):
    store = CaseStore(tmp_path)
    store.save({'name':'Synthetic Core Context', 'personalContext':PERSONAL})
    session = store.attach_analysis({'rateObjects':[{'nameOrRate':'Rate', 'gv':50}]}, {})
    assert session.get('contextSnapshot') is not None, 'attach helper omits context'
    checkpoint = {'mode':'seeded','drawCount':123}
    _, child = store.plan_fork_session_for_new_round(session['sessionId'], entropy_checkpoint=checkpoint)
    assert child['entropyCheckpoint'] == checkpoint, 'fork lost entropy checkpoint'
    assert child['draftId'] is None

def test_new_raw_case_cannot_inject_historical_context(home):
    create(home)
    analyzed = analyze(home)
    response = home.post('/cases', json={'name':'Synthetic Injected History',
        'sessionList':[{'sessionId':'b'*32, 'contextSnapshot': analyzed['draft']['contextSnapshot']}]})
    assert response.status_code in (409,422)


def test_planned_gv_fork_keeps_explicit_checkpoint(tmp_path):
    store = CaseStore(tmp_path)
    store.save({'name':'Synthetic Planned GV'})
    document, parent = store.plan_attach_analysis({'rateObjects':[{'nameOrRate':'Rate','gv':50}]}, {})
    store.apply_planned_case(document)
    checkpoint = {'mode':'seeded','drawCount':123}
    _, child = store.plan_fork_session_for_new_round(parent['sessionId'], entropy_checkpoint=checkpoint)
    assert child['entropyCheckpoint'] == checkpoint
    assert child['draftId'] is None

def test_legacy_metadata_rename_does_not_duplicate_file(home):
    state = STATE.state
    path = state.case_store.cases_dir / 'LegacyOld.json'
    path.write_text(json.dumps({'name':'Legacy Old', 'scope':state.scope.to_dict(), 'sessionList':[]}), encoding='utf-8')
    assert home.post('/cases/LegacyOld/activate').status_code == 200
    ref = home.get('/cases/current/ref').json()['ref']
    response = home.post('/cases/current/metadata', json={'name':'Legacy New', 'expected_case_ref':ref})
    assert response.status_code == 200, response.text
    assert len(home.get('/cases').json()['entries']) == 1
    assert home.get('/cases/current/ref').json()['ref'] == ref


def test_direct_gv_fork_inherits_exact_parent_context(tmp_path):
    store = CaseStore(tmp_path)
    store.save({'name':'Synthetic Direct Fork', 'personalContext':PERSONAL, 'focus':'Original focus'})
    parent = store.attach_analysis({'rateObjects':[{'nameOrRate':'Rate','gv':50}]}, {})
    original = copy.deepcopy(parent)
    store.save({**copy.deepcopy(store.current), 'focus':'Changed focus'})
    child = store.fork_session_for_new_round(parent['sessionId'])
    assert child.get('contextSnapshot') == original['contextSnapshot']
    assert store.session_by_id(parent['sessionId']) == original
    assert child['analysisResult']['rateObjects'][0]['gv'] == 0

def test_direct_legacy_gv_fork_stays_unbound(tmp_path):
    store = CaseStore(tmp_path)
    legacy = {'sessionId':'c'*32, 'analysisResult':{'rateObjects':[{'nameOrRate':'Rate','gv':50}]}}
    store.save({'name':'Synthetic Legacy Fork', 'sessionList':[legacy]})
    before = copy.deepcopy(store.current['sessionList'][0])
    child = store.fork_session_for_new_round(legacy['sessionId'])
    assert child.get('contextSnapshot') is None
    assert store.session_by_id(legacy['sessionId']) == before

def test_direct_gv_fork_of_clone_retains_original_provenance(tmp_path):
    store = CaseStore(tmp_path)
    store.save({'name':'Synthetic Source Fork', 'personalContext':PERSONAL})
    parent = store.attach_analysis({'rateObjects':[{'nameOrRate':'Rate','gv':50}]}, {})
    original = copy.deepcopy(parent['contextSnapshot'])
    clone = copy.deepcopy(store.current)
    clone['name'] = 'Synthetic Clone Fork'
    store.save(clone)
    assert store.current['caseId'] != original['caseId']
    child = store.fork_session_for_new_round(parent['sessionId'])
    assert child['contextSnapshot'] == original
    assert store.session_by_id(parent['sessionId'])['contextSnapshot'] == original

def test_inherited_context_requires_persisted_matching_parent(tmp_path):
    from radiworks.core.cases import SessionError
    store = CaseStore(tmp_path)
    store.save({'name':'Synthetic Inherited Guard', 'personalContext':PERSONAL})
    parent = store.attach_analysis({'rateObjects':[{'nameOrRate':'Rate','gv':50}]}, {})
    forged = copy.deepcopy(store.current)
    forged['sessionList'].append({'sessionId':'d'*32,'parentSessionId':'e'*32,
        'contextSnapshot':copy.deepcopy(parent['contextSnapshot'])})
    before = copy.deepcopy(store.current)
    with pytest.raises(SessionError):
        store.save(forged, allow_inherited_context=True)
    assert store.current == before

def test_personal_patch_preserves_unmentioned_original_values(home):
    created = create(home,personal=PERSONAL)
    ref=home.get('/cases/current/ref').json()['ref']
    response=home.post('/cases/current/metadata',json={'expected_case_ref':ref,'expected_context_version':1,
        'personalContextChanges':{'place':'Hamburg'}})
    assert response.status_code==200,response.text
    saved=STATE.state.case_store.current
    assert saved['personalContext']['firstName']=='Zoë'
    assert saved['personalContextOriginal']['firstName']==PERSONAL['firstName']
    assert saved['personalContext']['place']=='Hamburg'
    assert saved['contextVersion']==2

def test_personal_patch_preserves_copyguard_protected_unedited_value(home):
    state=STATE.state
    created=state.case_store.save({'name':'Synthetic Protected Personal','personalContext':{'firstName':'Heilt garantiert','place':'Berlin'}})
    ref=home.get('/cases/current/ref').json()['ref']
    response=home.post('/cases/current/metadata',json={'expected_case_ref':ref,'expected_context_version':1,
        'personalContextChanges':{'place':'Hamburg'}})
    assert response.status_code==200,response.text
    assert state.case_store.current['personalContext']['firstName']=='Heilt garantiert'
    assert state.case_store.current['personalContext']['place']=='Hamburg'

def test_personal_patch_requires_binding_and_disallows_ambiguous_full_replace(home):
    create(home,personal=PERSONAL)
    ref=home.get('/cases/current/ref').json()['ref']
    for body in [
       {'personalContextChanges':{'place':'Hamburg'}},
       {'personalContextChanges':{'place':'Hamburg'},'expected_case_ref':ref},
       {'personalContextChanges':{'place':'Hamburg'},'personalContext':{},'expected_case_ref':ref,'expected_context_version':1},
    ]:
        assert home.post('/cases/current/metadata',json=body).status_code in (409,422)
    assert STATE.state.case_store.current['contextVersion']==1
