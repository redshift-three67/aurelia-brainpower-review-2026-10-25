"""Independent personal procedure: no changes to Original or EXP1 contracts."""
import copy
import hashlib
import pytest
from radiworks.core.personal_analysis import freeze_personal_input, PersonalAnalysisError, MAX_PERSONAL_RATES
from radiworks.core.cases import CaseStore
from radiworks.core.personal_context import ContextSnapshot
from radiworks.entropy import EntropyProvider, RandomOrgSource, WebcamFeedSource
from radiworks.scope import ScopeContext

SCOPE=ScopeContext('synthetic','client','job')

def basis(tmp_path, count=24):
    case=CaseStore(tmp_path/'cases',scope=SCOPE).save({'name':'Synthetic','focus':'Rate', 'personalContext':{'firstName':'Ada','lastName':'Example','birthDate':'1980-02-29','placeKind':'birth','place':'Exampleton'}})
    snapshot=ContextSnapshot.capture(case,SCOPE).payload()
    rates=[f'Rate {i}' for i in range(count)]
    content='\n'.join(rates)+'\n'
    catalog={'name':'Synthetic.txt','sha256':hashlib.sha256(content.encode()).hexdigest(),'content':content}
    return snapshot,catalog,rates

def freeze(snapshot,catalog,rates,mode='seeded',seed=0,provider=None):
    return freeze_personal_input(SCOPE,snapshot,catalog,rates,mode=mode,job_seed=seed,entropy=provider or EntropyProvider(seed=seed,mode=mode,random_org=RandomOrgSource(http_get=None)),implementation_hash='a'*64)

def test_all_catalog_rates_are_frozen_beyond_first_21_and_default_seed_matches_exp1_basis(tmp_path):
    from radiworks.core.experimental_matrix import _seed
    snap,cat,rates=basis(tmp_path)
    source=copy.deepcopy((snap,cat,rates));payload=freeze(snap,cat,rates)
    assert len(payload['rates'])==24
    assert payload['candidateSeeds']==[_seed('Ada1980-02-29'+r) for r in rates]
    assert payload['procedure']=='radi144-personal-v1'
    assert payload['contextSnapshot']==snap
    assert payload['catalog']==cat
    assert (snap,cat,rates)==source
    assert payload['entropy']['drawCount']==0

def test_nonzero_reproducible_job_seed_is_independent_of_batching_and_request_id(tmp_path):
    snap,cat,rates=basis(tmp_path)
    first=freeze(snap,cat,rates,seed=123);second=freeze(snap,cat,rates,seed=123)
    assert first==second
    assert first['candidateSeeds']!=freeze(snap,cat,rates)['candidateSeeds']
    assert first['entropy']['drawCount']==len(rates)

@pytest.mark.parametrize('change', ['foreign-scope','catalog-hash','missing-rate','duplicate-rate','too-many','bad-mode'])
def test_invalid_input_is_rejected_before_any_random_draw(tmp_path,change):
    snap,cat,rates=basis(tmp_path)
    mode='seeded'
    if change=='foreign-scope': snap['scope']['tenant_id']='foreign'
    elif change=='catalog-hash':cat['sha256']='0'*64
    elif change=='missing-rate':rates[-1]='Not in catalog'
    elif change=='duplicate-rate':rates[-1]=rates[0]
    elif change=='too-many':rates=rates*(MAX_PERSONAL_RATES//len(rates)+1)
    elif change=='bad-mode':mode='automatic'
    provider=EntropyProvider(seed=0)
    with pytest.raises(PersonalAnalysisError): freeze(snap,cat,rates,mode=mode,provider=provider)
    assert provider.checkpoint()['drawCount']==0

def test_stochastic_requires_durable_journal_before_any_draw(tmp_path):
    snap,cat,rates=basis(tmp_path)
    provider=EntropyProvider(mode='stochastic',random_org=RandomOrgSource(http_get=None))
    with pytest.raises(PersonalAnalysisError,match='Journal'):freeze(snap,cat,rates,mode='stochastic',seed=None,provider=provider)
    assert provider.checkpoint()['drawCount']==0

def test_stochastic_frozen_seeds_are_replayable_and_use_full_catalog_context(tmp_path,monkeypatch):
    from cryptography.fernet import Fernet
    from radiworks.entropy_journal import EntropyJournalStore
    monkeypatch.setenv('RADIOWORKS_JOURNAL_KEY',Fernet.generate_key().decode('ascii'))
    snap,cat,rates=basis(tmp_path)
    feed=WebcamFeedSource();feed.feed(list(range(1000,1024)))
    journal=EntropyJournalStore(tmp_path/'journals').create()
    provider=EntropyProvider(mode='stochastic',feed=feed,random_org=RandomOrgSource(http_get=None),journal=journal)
    payload=freeze(snap,cat,rates,mode='stochastic',seed=None,provider=provider)
    assert len(payload['candidateSeeds'])==24
    assert payload['entropy']['journalCursor']==24
    assert payload['entropy']['journalId']==journal.journal_id
    assert all(source=='webcam' for source in payload['drawSources'])
    assert payload['candidateSeeds']!=freeze(snap,cat,rates)['candidateSeeds']
    assert EntropyJournalStore(tmp_path/'journals').open(journal.journal_id).cursor==24
    assert payload['catalog']==cat


def test_seeds_and_bound_parameters_cannot_be_relabelled_by_rehashing(tmp_path):
    from radiworks.core.personal_analysis import validate_personal_input
    from radiworks.persistence import document_digest
    snap,cat,rates=basis(tmp_path)
    payload=freeze(snap,cat,rates)
    for field, value in [('candidateSeeds',[0]*24),('weight','Stark'),('seedScheme','other')]:
        bad=copy.deepcopy(payload);bad[field]=value
        bad['inputDigest']=document_digest({k:v for k,v in bad.items() if k!='inputDigest'})
        with pytest.raises(PersonalAnalysisError):validate_personal_input(bad)


def test_personal_block_preserves_exp1_scores_with_real_cpu_profile(tmp_path):
    import os
    if not os.environ.get('RADIOWORKS_EXP1_TEST_DEPS'):pytest.skip('separate pinned CPU profile required')
    from radiworks.core.personal_analysis import rank_personal_block
    from radiworks.core.experimental_matrix import rank_experimental_rates, CPU_PROFILE
    snap,cat,rates=basis(tmp_path,count=2)
    payload=freeze(snap,cat,rates)
    old=rank_experimental_rates(snap,cat,rates,profile=CPU_PROFILE)
    new=rank_personal_block(payload,[0,1],profile=CPU_PROFILE)
    assert {r['rate']:r['score'] for r in new}=={r['rate']:r['score'] for r in old['results']}
    assert {r['rate']:r['matrix'] for r in new}=={r['rate']:r['matrix'] for r in old['results']}
    assert [r['inputIndex'] for r in new]==[0,1]
    assert all('gv' not in row and 'energeticValue' not in row for row in new)


def test_block_size_never_changes_personal_score_and_indices_are_global(tmp_path):
    import os
    if not os.environ.get('RADIOWORKS_EXP1_TEST_DEPS'):pytest.skip('separate pinned CPU profile required')
    from radiworks.core.personal_analysis import rank_personal_block
    from radiworks.core.experimental_matrix import PROBE_PROFILE
    snap,cat,rates=basis(tmp_path,count=24)
    payload=freeze(snap,cat,rates,seed=123)
    full=[]
    for i in range(0,24,6):full.extend(rank_personal_block(payload,list(range(i,min(i+6,24))),profile=PROBE_PROFILE))
    split=rank_personal_block(payload,list(range(21)),profile=PROBE_PROFILE)+rank_personal_block(payload,list(range(21,24)),profile=PROBE_PROFILE)
    assert full==split
    assert [r['inputIndex'] for r in full]==list(range(24))
    with pytest.raises(PersonalAnalysisError):rank_personal_block(payload,[0,0],profile=PROBE_PROFILE)
