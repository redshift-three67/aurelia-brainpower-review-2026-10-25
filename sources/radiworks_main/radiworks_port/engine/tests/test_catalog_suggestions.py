import importlib.util
import pytest

def helper():
 assert importlib.util.find_spec('radiworks.core.catalog_suggestions') is not None, 'Missing lexical helper'
 from radiworks.core import catalog_suggestions
 return catalog_suggestions

def doc(name,text): return {'name':name,'text':text}

def test_unicode_normalization_unique_and_stopwords():
 assert helper().query_terms('Für Pflanzen, RUHE und Äther','the aether Ruhe 123')==['pflanzen','ruhe','ather','aether']

@pytest.mark.parametrize('bad',['a\x00b','a\u200bb','Diagnose sicher','heilt_garantiert',' '.join('wort'+chr(97+i) for i in range(13))])
def test_invalid_queries_reject_without_echo(bad):
 with pytest.raises(ValueError) as exc: helper().query_terms(bad,'')
 assert bad not in str(exc.value)

def test_empty_short_and_numeric_terms():
 assert helper().query_terms('21 zu an the','12')==[]
 assert helper().rank_catalog([doc('BIOLOGICAL_A','Pflanzen')],[])=={'totalMatches':0,'suggestions':[]}

def test_exact_explanations_and_no_raw_content():
 got=helper().rank_catalog([doc('BIOLOGICAL_Pflanzen','Ruhe\turl diagnosis\nRuhe repeated\nHeilt garantiert Pflanzen\n')],['pflanzen','ruhe'])
 chosen=got['suggestions'][0]
 assert chosen=={'name':'BIOLOGICAL_Pflanzen','selector':'BIOLOGICAL_Pflanzen.txt','nameTerms':['pflanzen'],'groupTerms':[],'rateTerms':['ruhe'],'matchedRateCount':2}
 assert got['totalMatches']==1

def test_content_matching_excludes_url_and_blocked_lines():
 got=helper().rank_catalog([doc('OTHER_A','Allowed\tPflanzen\nHeilt garantiert Pflanzen\n')],['pflanzen'])
 assert got['totalMatches']==0

@pytest.mark.parametrize('name',['BIOLOGICAL_heilt_garantiert','BIOLOGICAL_Diagnose_sicher'])
def test_blocked_names_excluded_after_separator_normalization(name):
 assert helper().rank_catalog([doc(name,'Pflanzen')],['pflanzen'])['suggestions']==[]

def test_fixed_group_explanation():
 got=helper().rank_catalog([doc('BIOLOGICAL_Neutral','Pflanzen')],['biologisch'])
 assert got['suggestions'][0]['groupTerms']==['biologisch']

@pytest.mark.parametrize('prefix,word',[('HOMEOPATHY','homeopathie'),('SYMBOLISM','symbolik'),('ESSENCES','essenzen'),('CHEMICAL','chemie'),('ENERGY','energie'),('AGRICULTURE','agriculture'),('ANALYSIS','analyse')])
def test_existing_group_terms(prefix,word):
 got=helper().rank_catalog([doc(prefix+'_A','Nothing')],[word])
 assert got['suggestions'][0]['groupTerms']==[word]

def test_rank_coverage_before_name_and_stable_tie():
 documents=[doc('Z_Ruhe',''),doc('B_Content','Pflanzen Ruhe'),doc('A_Content','Pflanzen Ruhe'),doc('OTHER_Pflanzen','')]
 got=helper().rank_catalog(documents,['pflanzen','ruhe'])
 assert [v['name'] for v in got['suggestions']]==['A_Content','B_Content','OTHER_Pflanzen','Z_Ruhe']
 assert helper().rank_catalog(list(reversed(documents)),['pflanzen','ruhe'])==got

def test_repeated_rates_do_not_inflate_rank_and_limit_is_explicit():
 documents=[doc('A_Content','Ruhe\n'),doc('Z_Content','Ruhe\n'*100)]
 got=helper().rank_catalog(documents,['ruhe'],1)
 assert got['totalMatches']==2 and len(got['suggestions'])==1
 assert got['suggestions'][0]['name']=='A_Content'

@pytest.mark.parametrize('limit',[0,9,True,'8'])
def test_invalid_limits(limit):
 with pytest.raises(ValueError): helper().rank_catalog([],[],limit)

def test_extra_source_metadata_is_ignored():
 got=helper().rank_catalog([{'name':'BIOLOGICAL_A','text':'Pflanzen','encodingReplacement':True}],['pflanzen'])
 assert got['totalMatches']==1
