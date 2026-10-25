"""Synthetic exclusive place-kind and immutable context regression tests."""
import copy
import pytest
from radiworks.api.routes import STATE
from radiworks.core.personal_context import ContextSnapshot, ContextError, normalize_personal, prepare_identity

@pytest.mark.parametrize('kind',['residence','birth'])
def test_optional_explicit_kind_is_normalized(kind):
    data=normalize_personal({'place':' Berlin ','placeKind':kind})
    assert data['place']=='Berlin' and data['placeKind']==kind

@pytest.mark.parametrize('kind',[None,True,1,'','Birth','work',[],{}])
def test_invalid_kind_is_rejected(kind):
    with pytest.raises(ContextError): normalize_personal({'placeKind':kind})

def test_legacy_snapshot_remains_byte_equivalent():
    case={'name':'Synthetic Legacy','personalContext':{'place':'Berlin'}}
    prepare_identity(case)
    old=ContextSnapshot.capture(case,None).payload()
    assert 'placeKind' not in old['context']['personal']
    assert ContextSnapshot.from_payload(copy.deepcopy(old)).payload()==old

@pytest.mark.parametrize('hidden',['birthPlace','residencePlace'])
def test_no_inactive_second_place_allowed(hidden):
    with pytest.raises(ContextError): normalize_personal({'place':'Berlin','placeKind':'birth',hidden:'Paris'})

def create(home,kind=None):
    personal={'firstName':'Synthetic','lastName':'Example','birthDate':'1980-02-29','place':'Berlin'}
    if kind is not None: personal['placeKind']=kind
    reply=home.post('/cases',json={'name':'Synthetic Place','personalContext':personal,'focus':'Pflanzen'})
    assert reply.status_code==200,reply.text
    return reply.json()

def binding(home):
    now=home.get('/cases/current/ref').json()
    current=home.get('/cases/current').json()
    return dict(expected_case_ref=now['ref'],expected_context_version=current['contextVersion'])

def analyze(home):
    response=home.post('/analysis',json={'database':'HOMEOPATHY_Test','seed':42,'mode':'seeded'})
    assert response.status_code==200,response.text
    return response.json()

def test_api_type_only_patch_cannot_reinterpret_saved_place(home):
    create(home)
    before=copy.deepcopy(STATE.state.case_store.current)
    response=home.post('/cases/current/metadata',json={**binding(home),'personalContextChanges':{'placeKind':'birth'}})
    assert response.status_code==409,response.text
    assert STATE.state.case_store.current==before

def test_api_paired_kind_change_preserves_old_session_and_original_numbers(home):
    case=create(home)
    first=analyze(home)
    old=copy.deepcopy(STATE.state.case_store.current['sessionList'][0])
    response=home.post('/cases/current/metadata',json={**binding(home),'personalContextChanges':{'placeKind':'birth','place':'Paris'}})
    assert response.status_code==200,response.text
    changed=response.json()
    assert changed['personalContext']['placeKind']=='birth'
    assert changed['personalContext']['place']=='Paris'
    assert changed['contextVersion']==case['contextVersion']+1
    assert changed['sessionList'][0]==old
    assert 'placeKind' not in old['contextSnapshot']['context']['personal']
    second=analyze(home)
    assert first['result']==second['result'], 'original numeric path must ignore kind and context'
    new=STATE.state.case_store.current['sessionList'][-1]
    assert new['contextSnapshot']['context']['personal']['placeKind']=='birth'
    assert new['contextSnapshot']['context']['personal']['place']=='Paris'
    assert STATE.state.case_store.current['sessionList'][0]==old

def test_residence_and_birth_creation_both_keep_original_analysis(home):
    create(home,'residence'); first=analyze(home)
    saved=home.post('/cases/current/metadata',json={**binding(home),'personalContextChanges':{'placeKind':'birth','place':'Berlin'}})
    assert saved.status_code==200,saved.text
    assert analyze(home)['result']==first['result']

def test_place_update_retains_explicit_current_kind(home):
    create(home,'birth')
    response=home.post('/cases/current/metadata',json={**binding(home),'personalContextChanges':{'place':'Paris'}})
    assert response.status_code==200,response.text
    assert response.json()['personalContext']['placeKind']=='birth'

def test_full_replacement_type_change_requires_explicit_place(home):
    create(home,'residence')
    before=copy.deepcopy(STATE.state.case_store.current)
    response=home.post('/cases/current/metadata',json={**binding(home),'personalContext':{'placeKind':'birth'}})
    assert response.status_code==422,response.text
    assert STATE.state.case_store.current==before

def test_case_save_type_change_requires_explicit_place(home):
    create(home,'residence')
    before=copy.deepcopy(STATE.state.case_store.current)
    response=home.post('/cases',json={'name':'Synthetic Place','personalContext':{'placeKind':'birth'}})
    assert response.status_code==422,response.text
    assert STATE.state.case_store.current==before

def test_explicit_type_clear_is_valid_and_no_hidden_value_retained(home):
    create(home,'residence')
    response=home.post('/cases/current/metadata',json={**binding(home),'personalContextChanges':{'placeKind':'birth','place':None}})
    assert response.status_code==200,response.text
    personal=response.json()['personalContext']
    assert personal['place'] is None and personal['placeKind']=='birth'
    assert set(personal)=={'firstName','lastName','birthDate','place','image','placeKind'}

def test_direct_planning_cannot_retype_with_omitted_place():
    old={'name':'Synthetic','personalContext':{'place':'Berlin','placeKind':'residence'}}
    prepare_identity(old)
    changed=copy.deepcopy(old); changed['personalContext']={'placeKind':'birth'}
    with pytest.raises(ContextError): prepare_identity(changed,old)
