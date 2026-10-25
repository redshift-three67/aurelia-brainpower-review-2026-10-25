import copy,hashlib,json
from pathlib import Path
import pytest
from radiworks.api.routes import STATE

def catalog():
 state=STATE.state
 d=state.rate_repository.data_dir
 (d/'BIOLOGICAL_Focus.txt').write_text('Pflanzen Ruhe\nHeilt garantiert Pflanzen\n',encoding='utf-8')
 (d/'BIOLOGICAL_Focus_Extra.txt').write_text('Unrelated extra\n',encoding='utf-8')
 (d/'ENERGY_Neutral.txt').write_text('Pflanzen\n',encoding='utf-8')
 state.rate_repository.refresh()
 return d

def bound(home,focus='Pflanzen',topics='',**extra):
 response=home.post('/cases',json={'name':'Synthetic Search A','focus':focus,'personalContext':{'firstName':'Arnica','place':'AEsculus'}})
 assert response.status_code==200
 ref=response.headers['X-RadiWorks-Case-Ref']
 return {'topics':topics,'use_focus':True,'expected_case_ref':ref,'expected_context_version':response.json()['contextVersion'],**extra}

def request(home,body):
 res=home.post('/database-suggestions',json=body)
 assert res.status_code==200,res.text
 return res.json()

def test_suggestions_explain_exact_content_and_preserve_original_state(home):
 catalog();body=bound(home,topics='Ruhe')
 state=STATE.state;before=copy.deepcopy(state.case_store.current)
 queue=home.get('/broadcast/queue').json()
 files={p.relative_to(state.case_store.cases_dir).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in state.case_store.cases_dir.rglob('*') if p.is_file()}
 got=request(home,body)
 assert got['ruleVersion']=='catalog-lexical-v1'
 assert got['queryTerms']==['pflanzen','ruhe']
 assert got['totalMatches']==2
 chosen=got['suggestions'][0]
 assert chosen['selector']==chosen['exactId']
 assert chosen['exactId'].startswith('catalog-')
 assert chosen['catalogId'].startswith('catalog-')
 assert chosen['rateTerms']==['pflanzen','ruhe']
 assert chosen['matchedRateCount']==1
 assert 'Heilt' not in json.dumps(got)
 assert state.case_store.current==before
 assert home.get('/broadcast/queue').json()==queue
 assert files=={p.relative_to(state.case_store.cases_dir).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in state.case_store.cases_dir.rglob('*') if p.is_file()}
 confirmed=home.post('/database-suggestions/confirm',json={**body,'catalogSnapshotDigest':got['catalogSnapshotDigest'],'selector':chosen['selector']})
 assert confirmed.status_code==200,confirmed.text
 assert confirmed.json()['selector']==chosen['exactId']
 assert confirmed.json()['catalogId']==chosen['catalogId']
 # Exact candidate selector excludes prefix sibling.
 analyzed=home.post('/analysis',json={'database':confirmed.json()['selector'],'seed':42,'mode':'seeded'})
 assert analyzed.status_code==200
 names=[rate['nameOrRate'] for rate in analyzed.json()['result']['rateObjects']]
 assert 'Unrelated extra' not in names

def test_personal_identity_is_not_a_search_term(home):
 catalog();got=request(home,bound(home,focus='',topics=''))
 assert got['queryTerms']==[] and got['suggestions']==[]

def test_topics_only_without_case_and_no_case_mutation(home):
 catalog()
 got=request(home,{'topics':'Pflanzen','use_focus':False})
 assert got['totalMatches']==2 and got['caseRef'] is None
 assert not STATE.state.case_store.current

@pytest.mark.parametrize('change',[{'expected_case_ref':'a'*64},{'expected_context_version':99},{'expected_case_ref':None},{'expected_context_version':None}])
def test_missing_or_stale_case_binding_rejected(home,change):
 catalog();body=bound(home)
 res=home.post('/database-suggestions',json={**body,**change})
 assert res.status_code==409

@pytest.mark.parametrize('extra',[{'topics':'x'*241},{'use_focus':'yes'},{'limit':9},{'limit':True},{'unknown':'value'},{'topics':'Diagnose sicher'},{'topics':'a\x00b'}])
def test_invalid_request_has_bounded_generic_error(home,extra):
 catalog()
 res=home.post('/database-suggestions',json={'use_focus':False,**extra})
 assert res.status_code==422
 assert 'Diagnose' not in res.text and 'x'*100 not in res.text

def test_confirm_detects_changed_catalog(home):
 d=catalog();body=bound(home);got=request(home,body)
 (d/'BIOLOGICAL_Focus.txt').write_text('Pflanzen changed\n',encoding='utf-8')
 res=home.post('/database-suggestions/confirm',json={**body,'catalogSnapshotDigest':got['catalogSnapshotDigest'],'selector':'BIOLOGICAL_Focus.txt'})
 assert res.status_code==409

def test_confirm_detects_changed_case(home):
 catalog();body=bound(home);got=request(home,body)
 home.post('/cases',json={'name':'Synthetic Search B','focus':'Ruhe'})
 res=home.post('/database-suggestions/confirm',json={**body,'catalogSnapshotDigest':got['catalogSnapshotDigest'],'selector':'BIOLOGICAL_Focus.txt'})
 assert res.status_code==409

def test_confirm_rejects_unknown_and_pathlike_selectors(home):
 catalog();body=bound(home);got=request(home,body)
 for selector in ('../outside.txt','HOMEOPATHY_Test.txt','BIOLOGICAL_Focus'):
  res=home.post('/database-suggestions/confirm',json={**body,'catalogSnapshotDigest':got['catalogSnapshotDigest'],'selector':selector})
  assert res.status_code in (409,422)

def test_body_size_rejected_without_parsing(home):
 assert home.post('/database-suggestions',content=b'x'*4097).status_code==413


def sources_module():
 import importlib.util,importlib
 assert importlib.util.find_spec('radiworks.core.catalog_suggestion_sources') is not None, 'Missing bounded catalog snapshot'
 return importlib.import_module('radiworks.core.catalog_suggestion_sources')

def test_source_snapshot_detects_between_read_mutation(home,monkeypatch):
 d=catalog();m=sources_module();original=m._read;seen={}
 def changing(path):
  seen[path]=seen.get(path,0)+1
  if seen[path]==2 and path.name=='BIOLOGICAL_Focus.txt':
   path.write_text('Pflanzen changed\n',encoding='utf-8')
  return original(path)
 monkeypatch.setattr(m,'_read',changing)
 with pytest.raises(m.CatalogSearchDrift): m.catalog_snapshot(STATE.state.rate_repository)

def test_source_file_total_and_line_limits(home,monkeypatch):
 catalog();m=sources_module()
 for key,value in [('MAX_FILES',1),('MAX_FILE_BYTES',4),('MAX_TOTAL_BYTES',5),('MAX_LINES',1)]:
  with monkeypatch.context() as patch:
   patch.setattr(m,key,value)
   with pytest.raises(m.CatalogSearchBoundsError): m.catalog_snapshot(STATE.state.rate_repository)

def test_changed_unindexed_inventory_fails_closed(home):
 d=catalog();m=sources_module()
 (d/'New_Unindexed.txt').write_text('Pflanzen\n',encoding='utf-8')
 with pytest.raises(m.CatalogSearchDrift): m.catalog_snapshot(STATE.state.rate_repository)

def test_duplicate_database_names_fail_closed(home):
 d=catalog();m=sources_module()
 child=d/'nested';child.mkdir()
 (child/'BIOLOGICAL_Focus.txt').write_text('Pflanzen duplicate\n',encoding='utf-8')
 with pytest.raises(m.CatalogSearchDrift): m.catalog_snapshot(STATE.state.rate_repository)

def test_api_rechecks_context_after_catalog_read(home,monkeypatch):
 catalog();body=bound(home);m=sources_module()
 from radiworks.api import routes
 original=m.catalog_snapshot
 def switched(repo):
  result=original(repo)
  STATE.state.case_store.current['focus']='Changed'
  return result
 monkeypatch.setattr(routes,'catalog_snapshot',switched)
 response=home.post('/database-suggestions',json=body)
 assert response.status_code==409


def test_published_catalog_is_bound_and_rejects_changed_bytes(tmp_path):
 from radiworks.core.catalog_release import publish_catalog_release
 from radiworks.core.rates import RateRepository
 m=sources_module();source=tmp_path/'source';source.mkdir()
 (source/'BIOLOGICAL_A.txt').write_bytes(b'Pflanzen Ruhe\n')
 release=publish_catalog_release(source,tmp_path/'releases')
 repo=RateRepository(release/'data');repo.refresh()
 docs,digest=m.catalog_snapshot(repo)
 assert docs==[{'name':'BIOLOGICAL_A','text':'Pflanzen Ruhe\n'}]
 assert len(digest)==64
 (release/'data'/'BIOLOGICAL_A.txt').write_text('Pflanzen changed\n',encoding='utf-8')
 with pytest.raises(m.CatalogSearchDrift): m.catalog_snapshot(repo)

def test_original_utf8_replacement_is_disclosed_and_missing_catalog_controlled(home):
 d=catalog();(d/'BIOLOGICAL_Focus.txt').write_bytes(b'Pflanzen\xff Ruhe\n')
 response=home.post('/database-suggestions',json={'use_focus':False,'topics':'Pflanzen'})
 assert response.status_code==200
 assert response.json()['catalogWarnings']['utf8ReplacementFiles']==1
 (d/'BIOLOGICAL_Focus.txt').unlink()
 assert home.post('/database-suggestions',json={'use_focus':False,'topics':'Pflanzen'}).status_code==409

def test_source_digest_binds_text_paths_and_canonical_order(home):
 d=catalog();m=sources_module();repo=STATE.state.rate_repository
 first=m.catalog_snapshot(repo)
 assert m.catalog_snapshot(repo)==first
 (d/'ENERGY_Neutral.txt').write_text('Pflanzen changed\n',encoding='utf-8')
 assert m.catalog_snapshot(repo)[1]!=first[1]

def test_non_object_and_malformed_json_are_generic(home):
 for raw in (b'[]',b'null',b'{',b'"private raw text"'):
  response=home.post('/database-suggestions',content=raw)
  assert response.status_code==422
  assert 'private raw text' not in response.text


@pytest.mark.parametrize('filename',['helper.rscript','FUNCTION_Extra.txt'])
def test_published_catalog_rejects_mutated_nonselected_release_files(tmp_path,filename):
 from radiworks.core.catalog_release import publish_catalog_release
 from radiworks.core.rates import RateRepository
 m=sources_module();source=tmp_path/'source';source.mkdir()
 (source/'BIOLOGICAL_A.txt').write_bytes(b'Pflanzen Ruhe\n')
 (source/filename).write_text('Original helper\n',encoding='utf-8')
 release=publish_catalog_release(source,tmp_path/'releases')
 repo=RateRepository(release/'data');repo.refresh()
 m.catalog_snapshot(repo)
 (release/'data'/filename).write_text('Changed helper\n',encoding='utf-8')
 with pytest.raises(m.CatalogSearchDrift): m.catalog_snapshot(repo)


def test_tree_entry_and_depth_bounds(home,monkeypatch):
 d=catalog();m=sources_module();(d/'nested').mkdir();(d/'nested'/'deep').mkdir()
 for key,value in [('MAX_ENTRIES',1),('MAX_DEPTH',1)]:
  with monkeypatch.context() as patch:
   patch.setattr(m,key,value)
   with pytest.raises(m.CatalogSearchBoundsError): m.catalog_snapshot(STATE.state.rate_repository)

def test_reparse_source_flag_is_rejected(home,monkeypatch):
 from types import SimpleNamespace
 d=catalog();m=sources_module();original=Path.lstat
 def tagged(path,*args,**kwargs):
  info=original(path,*args,**kwargs)
  if path.name=='BIOLOGICAL_Focus.txt': return SimpleNamespace(st_file_attributes=0x400,st_mode=info.st_mode)
  return info
 monkeypatch.setattr(Path,'lstat',tagged)
 with pytest.raises(m.CatalogSearchDrift): m.catalog_snapshot(STATE.state.rate_repository)
