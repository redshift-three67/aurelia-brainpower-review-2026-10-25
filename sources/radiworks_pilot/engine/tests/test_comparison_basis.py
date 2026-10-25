import copy,importlib.util,json
import pytest
from radiworks.core.rates import RateRepository
from radiworks.core.cases import CaseStore,SessionError
from radiworks.scope import ScopeContext
from radiworks import copyguard
from radiworks.persistence import document_digest

SCOPE=ScopeContext('synthetic','operator','exp-c23')
PERSONAL={'firstName':'Ada','lastName':'Example','birthDate':'1980-02-29','place':'Berlin','placeKind':'birth'}

def module():
    assert importlib.util.find_spec('radiworks.core.comparison_basis') is not None, 'C2 comparison basis missing'
    from radiworks.core import comparison_basis
    return comparison_basis


def fixture(tmp_path,count=25):
    data=tmp_path/'data';data.mkdir()
    content=''.join(f'Synthetic Rate {i}\n' for i in range(count))
    (data/'SYNTHETIC.txt').write_text(content,encoding='utf-8')
    repo=RateRepository(data);repo.refresh();rates=repo.find_all_by_source_name('SYNTHETIC')
    cases=CaseStore(tmp_path/'cases',scope=SCOPE)
    cases.save({'name':'Synthetic C2','personalContext':PERSONAL,'focus':'Synthetic'})
    baseline={'generalVitality':850,'rateObjects':[{'nameOrRate':r.name,'energeticValue':100-i} for i,r in enumerate(rates)]}
    passport={'copyguard_digest':copyguard.digest(copyguard.visible_rate_texts(baseline)),'run_id':'original-run','entropy_mode':'stochastic','seed':None,'kernel':'radiworks.engine','kernel_version':'0.2.0'}
    case,session=cases.plan_attach_analysis(baseline,passport)
    return repo,rates,cases,case,session


def test_capture_catalog_and_separate_source_input_are_frozen(tmp_path):
    m=module();repo,rates,cases,case,session=fixture(tmp_path)
    cat=m.capture_catalog(repo,'SYNTHETIC',rates)
    source=m.make_source(session,cat,SCOPE)
    session['comparisonBasis']=m.source_reference(source)
    cases.save(case,allow_new_context=True)
    original=copy.deepcopy(case)
    request=m.build_comparison_input(source,session,case,SCOPE,page_start=21,weight='Normal',implementation_hash='a'*64)
    assert request['rates']==[r['nameOrRate'] for r in session['analysisBaseline']['rateObjects'][21:]]
    assert len(request['rates'])==4 and request['pageStart']==21
    assert request['originalProvenance']['entropy_mode']=='stochastic'
    assert request['contextSnapshot']==session['contextSnapshot']
    assert case==original
    request['rates'].clear();assert len(source['baseline']['rateObjects'])==25


def test_exact_catalog_required_without_breaking_original_prefix(tmp_path):
    m=module();repo,rates,*_=fixture(tmp_path)
    (repo.data_dir/'SYNTHETIC_EXTRA.txt').write_text('Extra\n',encoding='utf-8');repo.refresh()
    original=repo.find_all_by_source_name('SYNTHETIC');assert len(original)==26
    with pytest.raises(m.ComparisonBasisError):m.capture_catalog(repo,'SYNTHETIC',original)
    assert m.capture_catalog(repo,'SYNTHETIC.txt',rates)['name']=='SYNTHETIC.txt'


def test_catalog_drift_between_analysis_and_capture_rejected(tmp_path):
    m=module();repo,rates,*_=fixture(tmp_path)
    (repo.data_dir/'SYNTHETIC.txt').write_text('Changed\n',encoding='utf-8')
    with pytest.raises(m.ComparisonBasisError):m.capture_catalog(repo,'SYNTHETIC',rates)


@pytest.mark.parametrize('page',[True,-1,1,42,21.0])
def test_page_boundaries_strict(tmp_path,page):
    m=module();repo,rates,cases,case,session=fixture(tmp_path)
    source=m.make_source(session,m.capture_catalog(repo,'SYNTHETIC',rates),SCOPE)
    session['comparisonBasis']=m.source_reference(source)
    with pytest.raises(m.ComparisonBasisError):m.build_comparison_input(source,session,case,SCOPE,page_start=page,weight='Normal',implementation_hash='a'*64)


def test_source_digest_case_context_and_copyguard_drift_rejected(tmp_path):
    m=module();repo,rates,cases,case,session=fixture(tmp_path)
    source=m.make_source(session,m.capture_catalog(repo,'SYNTHETIC',rates),SCOPE)
    session['comparisonBasis']=m.source_reference(source)
    bad=copy.deepcopy(source);bad['catalog']['content']+='Changed'
    with pytest.raises(m.ComparisonBasisError):m.build_comparison_input(bad,session,case,SCOPE,page_start=0,weight='Normal',implementation_hash='a'*64)
    session['analysisBaseline']['rateObjects'][0]['nameOrRate']='Forged'
    with pytest.raises(m.ComparisonBasisError):m.build_comparison_input(source,session,case,SCOPE,page_start=0,weight='Normal',implementation_hash='a'*64)
    session['analysisBaseline']=copy.deepcopy(source['baseline']);case['caseId']='f'*32
    with pytest.raises(m.ComparisonBasisError):m.build_comparison_input(source,session,case,SCOPE,page_start=0,weight='Normal',implementation_hash='a'*64)


def test_source_file_is_digest_bound_and_does_not_follow_redirect(tmp_path):
    m=module();repo,rates,cases,case,session=fixture(tmp_path)
    source=m.make_source(session,m.capture_catalog(repo,'SYNTHETIC',rates),SCOPE)
    sources=tmp_path/'sources';sources.mkdir();(sources/(source['sourceSessionId']+'.json')).write_text(json.dumps(source),encoding='utf-8')
    reference=m.source_reference(source)
    assert m.read_source(sources,reference)==source
    source['catalog']['content']='tampered'
    (sources/(source['sourceSessionId']+'.json')).write_text(json.dumps(source),encoding='utf-8')
    with pytest.raises(m.ComparisonBasisError):m.read_source(sources,reference)


def test_case_save_cannot_inject_or_mutate_comparison_basis(tmp_path):
    m=module();repo,rates,cases,case,session=fixture(tmp_path)
    source=m.make_source(session,m.capture_catalog(repo,'SYNTHETIC',rates),SCOPE)
    session['comparisonBasis']=m.source_reference(source)
    with pytest.raises(SessionError):cases.save(copy.deepcopy(case))
    cases.save(case,allow_new_context=True)
    bad=copy.deepcopy(case);bad['sessionList'][0]['comparisonBasis']['digest']='b'*64
    with pytest.raises(SessionError):cases.save(bad)
    bad=copy.deepcopy(case);bad['sessionList'][0]['analysisBaseline']['rateObjects'][0]['energeticValue']=999
    with pytest.raises(SessionError):cases.save(bad)

def test_case_save_cannot_change_frozen_passport(tmp_path):
    m=module();repo,rates,cases,case,session=fixture(tmp_path)
    source=m.make_source(session,m.capture_catalog(repo,'SYNTHETIC',rates),SCOPE)
    session['comparisonBasis']=m.source_reference(source)
    cases.save(case,allow_new_context=True)
    bad=copy.deepcopy(case);bad['sessionList'][0]['passport']['seed']=1234
    with pytest.raises(SessionError):cases.save(bad)
