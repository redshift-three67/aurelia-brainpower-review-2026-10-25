"""C1 synthetic numerical/context guards, no real case or catalog."""
import copy
import hashlib
import importlib.util
import pytest
from radiworks.core.personal_context import ContextSnapshot,prepare_identity
from radiworks.core.experimental_context import prepare_experimental_context
from radiworks.core.experimental_matrix import (MatrixError,CPU_PROFILE,PROBE_PROFILE,prepare_catalog_context,rank_experimental_rates)


def snapshot(focus='Ruhe',**fields):
    case={'name':'Synthetic C1','focus':focus,'personalContext':{'firstName':'Ada','lastName':'Example','birthDate':'1980-02-29',**fields}}
    prepare_identity(case)
    return ContextSnapshot.capture(case,None).payload()


def catalog(content='Synthetic Rate A\nSynthetic Rate B\nRuhe\n'):
    return {'name':'TEST_C1.txt','sha256':hashlib.sha256(content.encode('utf-8')).hexdigest(),'content':content}


def test_catalog_focus_uses_exact_original_substring_and_components():
    snap=snapshot();cat=catalog();before=copy.deepcopy((snap,cat))
    prepared=prepare_catalog_context(snap,cat)
    base=prepare_experimental_context(snap)
    assert prepared['catalog']['sha256']==cat['sha256']
    assert prepared['catalog']['name']==cat['name']
    assert prepared['focusMatch']=={'matched':True,'applied':True,'method':'literal-substring-lower-v1'}
    freq=base['signature']['frequency']
    # Actual Radi144 formula for Ruhe: r/h alphabetic, u165/e330 + alpha sum.
    extra=(sum(ord(c) for c in 'ruhe')+ord('r')*2+165+ord('h')*2+330)/2%1000
    assert prepared['signature']['frequency']==(freq+extra)/2
    assert prepared['signature']['components']['db_frequency_hz']==extra
    assert prepared['signature']['components']['db_source']=='TEST_C1.txt'
    assert (snap,cat)==before


@pytest.mark.parametrize('focus,content,matched',[('ruHE','Ruhe',True),('Ruhe Bewegung','Ruhe und Bewegung',False),('', 'Ruhe',False),('123','123',True)])
def test_nonmatch_empty_and_zero_frequency_do_not_invent_context(focus,content,matched):
    snap=snapshot(focus);prepared=prepare_catalog_context(snap,catalog(content))
    assert prepared['focusMatch']['matched']==matched
    applied=matched and focus not in ('','123')
    assert prepared['focusMatch']['applied']==applied
    if not applied: assert prepared['signature']==prepare_experimental_context(snap)['signature']


@pytest.mark.parametrize('change',[{'name':'../TEST.txt'},{'name':'TEST'},{'sha256':'0'*64},{'content':[]},{'extra':1}])
def test_invalid_catalog_binding_is_controlled(change):
    cat=catalog();cat.update(change)
    with pytest.raises(MatrixError):prepare_catalog_context(snapshot(),cat)


def test_snapshot_tamper_rejected_before_compute():
    snap=snapshot();snap['context']['personal']['firstName']='Other'
    with pytest.raises(MatrixError):prepare_catalog_context(snap,catalog())


@pytest.mark.parametrize('rates',[[],['Missing'],['Synthetic Rate A']*22,[None],['']])
def test_invalid_rate_subset_rejected(rates):
    with pytest.raises(MatrixError):rank_experimental_rates(snapshot(),catalog(),rates,profile=PROBE_PROFILE)


def test_invalid_weight_rejected_instead_of_default_fallback():
    with pytest.raises(MatrixError):rank_experimental_rates(snapshot(),catalog(),['Synthetic Rate A'],weight='Unknown',profile=PROBE_PROFILE)


def test_original_import_does_not_require_or_import_torch():
    # Matrix module must stay dependency-lazy; checked in a clean subprocess elsewhere.
    assert CPU_PROFILE.candidate_count==80000
    assert PROBE_PROFILE.candidate_count==64 and PROBE_PROFILE.purpose=='test-only'


@pytest.fixture
def cpu():
    if importlib.util.find_spec('torch') is None: pytest.skip('optional isolated CPU dependency profile not loaded')
    import torch
    assert torch.get_num_threads()==1
    return torch


def test_repeatability_duplicate_rates_frozen_input_and_rng_preservation(cpu):
    snap=snapshot();cat=catalog();inputs=copy.deepcopy((snap,cat))
    state=cpu.get_rng_state().clone()
    first=rank_experimental_rates(snap,cat,['Synthetic Rate A','Synthetic Rate B','Synthetic Rate A'],profile=PROBE_PROFILE)
    second=rank_experimental_rates(snap,cat,['Synthetic Rate A','Synthetic Rate B','Synthetic Rate A'],profile=PROBE_PROFILE)
    assert first==second
    assert (snap,cat)==inputs
    assert cpu.equal(state,cpu.get_rng_state())
    assert len(first['results'])==3
    duplicate=[r for r in first['results'] if r['rate']=='Synthetic Rate A']
    assert duplicate[0]['score']==duplicate[1]['score']
    assert sorted(r['originalIndex'] for r in duplicate)==[0,2]
    for r in first['results']:
        assert -1<=r['score']<=1
        assert len(r['matrix'])==12 and all(len(row)==12 for row in r['matrix'])
        assert all(type(n) is int and 0<=n<=9 for row in r['matrix'] for n in row)
    assert first['parameters']['candidateCount']==64
    assert first['parameters']['purpose']=='test-only'
    assert first['contextDigest']==snap['digest']


def test_identity_variation_and_catalog_source_affect_results(cpu):
    first=rank_experimental_rates(snapshot(),catalog(),['Synthetic Rate A'],profile=PROBE_PROFILE)
    second=rank_experimental_rates(snapshot(firstName='Synthetic Other'),catalog(),['Synthetic Rate A'],profile=PROBE_PROFILE)
    assert first['results'][0]['score']!=second['results'][0]['score']
    cat=catalog();cat['name']='TEST_C1_ALT.txt'
    third=rank_experimental_rates(snapshot(),cat,['Synthetic Rate A'],profile=PROBE_PROFILE)
    assert first['results'][0]['score']!=third['results'][0]['score']


def test_focus_weight_is_explicit_separate_parameter(cpu):
    a=rank_experimental_rates(snapshot(),catalog(),['Synthetic Rate A'],weight='Deaktiviert',profile=PROBE_PROFILE)
    b=rank_experimental_rates(snapshot(),catalog(),['Synthetic Rate A'],weight='Stark',profile=PROBE_PROFILE)
    assert a['results'][0]['score']!=b['results'][0]['score']


def test_missing_dependency_is_visible_without_original_mutation(monkeypatch):
    import builtins
    real_import=builtins.__import__
    def unavailable(name,*args,**kwargs):
        if name=='torch': raise ImportError('synthetic optional dependency unavailable')
        return real_import(name,*args,**kwargs)
    monkeypatch.setattr(builtins,'__import__',unavailable)
    with pytest.raises(MatrixError,match='CPU'):
        rank_experimental_rates(snapshot(),catalog(),['Synthetic Rate A'],profile=PROBE_PROFILE)


@pytest.mark.parametrize('profile',[{'candidate_count':64},None,True])
def test_profile_type_is_not_coerced(profile):
    with pytest.raises(MatrixError):rank_experimental_rates(snapshot(),catalog(),['Synthetic Rate A'],profile=profile)


def test_profile_numeric_float_is_not_accepted_as_integer():
    from radiworks.core.experimental_matrix import MatrixProfile
    with pytest.raises(MatrixError):rank_experimental_rates(snapshot(),catalog(),['Synthetic Rate A'],profile=MatrixProfile(80000.0,'product-cpu'))


def test_precision_retains_reference_top10_selection(cpu,monkeypatch):
    real=cpu.topk;seen=[]
    def topk(*args,**kw):
        seen.append(args[1] if len(args)>1 else kw['k'])
        return real(*args,**kw)
    monkeypatch.setattr(cpu,'topk',topk)
    rank_experimental_rates(snapshot(),catalog(),['Synthetic Rate A'],profile=PROBE_PROFILE)
    assert seen==[10]


def test_concurrent_calls_keep_global_rng_and_match_isolated_result(cpu):
    from concurrent.futures import ThreadPoolExecutor
    snap=snapshot();cat=catalog()
    expected=rank_experimental_rates(snap,cat,['Synthetic Rate A'],profile=PROBE_PROFILE)
    before=cpu.get_rng_state().clone()
    with ThreadPoolExecutor(max_workers=2) as pool:
        jobs=[pool.submit(rank_experimental_rates,snap,cat,['Synthetic Rate A'],profile=PROBE_PROFILE) for _ in range(2)]
        assert all(j.result()==expected for j in jobs)
    assert cpu.equal(before,cpu.get_rng_state())


def test_mid_computation_error_cannot_return_partial_success(cpu,monkeypatch):
    import radiworks.core.experimental_matrix as matrix_module
    real=matrix_module._score;calls=[]
    def fail_second(*args,**kwargs):
        calls.append(1)
        if len(calls)==2:raise RuntimeError('synthetic allocation failure')
        return real(*args,**kwargs)
    monkeypatch.setattr(matrix_module,'_score',fail_second)
    snap=snapshot();cat=catalog();saved=copy.deepcopy((snap,cat));before=cpu.get_rng_state().clone()
    with pytest.raises(MatrixError,match='kein vollständiges Ergebnis'):
        rank_experimental_rates(snap,cat,['Synthetic Rate A','Synthetic Rate B'],profile=PROBE_PROFILE)
    assert (snap,cat)==saved and cpu.equal(before,cpu.get_rng_state())


def test_unsupported_runtime_thread_config_is_visible(cpu,monkeypatch):
    monkeypatch.setattr(cpu,'get_num_threads',lambda:2)
    with pytest.raises(MatrixError,match='Thread'):
        rank_experimental_rates(snapshot(),catalog(),['Synthetic Rate A'],profile=PROBE_PROFILE)


def test_dependency_version_drift_is_rejected(cpu,monkeypatch):
    monkeypatch.setattr(cpu,'__version__','0.0')
    with pytest.raises(MatrixError,match='version'):
        rank_experimental_rates(snapshot(),catalog(),['Synthetic Rate A'],profile=PROBE_PROFILE)


def test_caller_list_mutation_during_computation_cannot_change_frozen_subset(cpu,monkeypatch):
    import radiworks.core.experimental_matrix as matrix_module
    real=matrix_module._score
    rates=['Synthetic Rate A','Synthetic Rate B'];seen=[]
    def mutate(*args,**kwargs):
        seen.append(args[3])
        if len(seen)==1:
            rates[1]='Not in catalog'
            rates.append('Another unchecked rate')
        return real(*args,**kwargs)
    monkeypatch.setattr(matrix_module,'_score',mutate)
    result=rank_experimental_rates(snapshot(),catalog(),rates,profile=PROBE_PROFILE)
    assert seen==['Synthetic Rate A','Synthetic Rate B']
    assert result['inputRates']==['Synthetic Rate A','Synthetic Rate B']
    assert len(result['results'])==2


def test_float32_profile_is_independent_of_global_default_dtype(cpu):
    previous=cpu.get_default_dtype()
    snap=snapshot();cat=catalog()
    expected=rank_experimental_rates(snap,cat,['Synthetic Rate A'],profile=PROBE_PROFILE)
    try:
        cpu.set_default_dtype(cpu.float64)
        actual=rank_experimental_rates(snap,cat,['Synthetic Rate A'],profile=PROBE_PROFILE)
        assert actual==expected
        assert cpu.get_default_dtype()==cpu.float64
    finally:
        cpu.set_default_dtype(previous)
