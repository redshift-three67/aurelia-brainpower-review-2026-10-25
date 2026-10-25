from pathlib import Path
import concurrent.futures,datetime,difflib,hashlib,json,urllib.request,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parent.parent
R=ROOT/'runtime/rw-vf3-20261004'
P=ROOT/'runtime/rw-vf2b-20261004'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def drift(base,items): return [v['path'] for v in items if not (base/v['path']).is_file() or sha(base/v['path'])!=v['sha256']]
parent=read(R/'PARENT_PRODUCT_MANIFEST.json')['files']
assert not drift(P,parent),'VF2-B parent drift'
vf2=read(P/'PARENT_PRODUCT_MANIFEST.json')['files']
V=ROOT/'runtime/rw-vf2-20261004'
assert not drift(V,vf2),'VF2-A parent drift'
gv=read(V/'PARENT_PRODUCT_MANIFEST.json')['files']
assert not drift(ROOT/'runtime/rw-gv2-20261004',gv),'GV2 parent drift'
extra=['engine/src/radiworks/core/catalog_suggestions.py','engine/src/radiworks/core/catalog_suggestion_sources.py','engine/tests/test_catalog_suggestions.py','engine/tests/test_database_suggestions.py','webapp/js/views/catalog_suggestions.js']
paths=sorted([v['path'] for v in parent]+extra)
assert len(paths)==len(set(paths))==114
files=[{'path':v,'sha256':sha(R/v)} for v in paths]
changed=[v['path'] for v in parent if sha(R/v['path'])!=v['sha256']]
assert set(changed)=={'engine/src/radiworks/api/routes.py','webapp/js/views/analyze.js','webapp/js/api.js','webapp/index.html','webapp/css/app.css','engine/tests/test_webapp_database_persistence.py'},changed
core=read(V/'FINAL_VERIFY.json')['numericalCoreFilesUnchanged']
assert all(sha(R/v['path'])==v['sha256'] for v in core),'Numerical kernel drift'
refs=read(V/'PARENT_REFERENCE_SOURCES.json')
assert all(Path(v['path']).is_file() and sha(Path(v['path']))==v['sha256'] for v in refs),'Reference source drift'
suite=next(ET.parse(R/'engine-final.xml').getroot().iter('testsuite'))
stats={k:int(suite.attrib[k]) for k in ('tests','failures','errors','skipped')}
stats['passed']=stats['tests']-stats['skipped']-stats['failures']-stats['errors']
assert stats['passed']>=525 and stats['skipped']==3 and stats['failures']==stats['errors']==0,stats
browser=(R/'browser-final.log').read_text(encoding='utf-8-sig')
sections=sum(line.startswith('PASS ') for line in browser.splitlines())
assert sections==36 and 'FAIL ' not in browser and 'CLEANUP' in browser,(sections,browser[-1000:])
assert 'PASS: 19 files' in (R/'js-syntax.log').read_text(encoding='utf-8-sig')
assert (R/'encoding-green.log').read_text(encoding='utf-8-sig').startswith('PASS ')
assert sum(v.startswith('PASS ') for v in (R/'release-integrity-green.log').read_text(encoding='utf-8-sig').splitlines())==2
review=read(R/'REVIEW.json')
assert review['openConfirmedFindings']==0 and review['helperReviewed'] is True
listeners=read(R/'LIVE_LISTENERS.json');old=read(R/'LIVE_LISTENERS_BEFORE.json')
assert sorted(listeners,key=lambda v:v['LocalPort'])==sorted(old,key=lambda v:v['LocalPort']),'Protected PID/listener changed'
def ping(port):
 with urllib.request.urlopen('http://127.0.0.1:'+str(port)+'/ping',timeout=5) as response:
  assert json.load(response)['result']=='pong'
 return {'port':port,'pong':True}
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool: pongs=list(pool.map(ping,range(8103,8111)))
now=datetime.datetime.now().astimezone().isoformat()
(R/'PRODUCT_MANIFEST.json').write_text(json.dumps({'createdAt':now,'files':files},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
patch=[]
for name in paths:
 if name not in changed and name not in extra: continue
 before=(P/name).read_text(encoding='utf-8').splitlines(keepends=True) if (P/name).is_file() else []
 after=(R/name).read_text(encoding='utf-8').splitlines(keepends=True)
 patch.extend(difflib.unified_diff(before,after,fromfile='parent/'+name,tofile='candidate/'+name))
(R/'PRODUCT_DIFF.patch').write_text(''.join(patch),encoding='utf-8')
record={'createdAt':now,'candidateFiles':114,'parentFiles':len(parent),'parentDrift':[],'vf2ParentFiles':len(vf2),'vf2ParentDrift':[],'gv2ParentFiles':len(gv),'gv2ParentDrift':[],'changedParentFiles':changed,'newFiles':extra,'numericalCoreUnchanged':[v['path'] for v in core],'referenceSourcesUnchanged':[v['name'] for v in refs],'engine':stats,'boundBrowserSections':sections,'jsSyntaxFiles':19,'protectedListeners':listeners,'pongs':pongs,'liveMutation':False,'hostIntegrationRelease':False}
(R/'FINAL_VERIFY.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(record,ensure_ascii=False))
