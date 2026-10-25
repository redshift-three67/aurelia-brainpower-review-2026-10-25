from pathlib import Path
import concurrent.futures,datetime,hashlib,json,urllib.request,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parent.parent
R=ROOT/'runtime/rw-vf2b-20261004'
P=ROOT/'runtime/rw-vf2-20261004'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def drift(base,items): return [v['path'] for v in items if not (base/v['path']).is_file() or sha(base/v['path'])!=v['sha256']]
parent=read(R/'PARENT_PRODUCT_MANIFEST.json')['files']
assert not drift(P,parent),'VF2-A parent drift'
gv=read(P/'PARENT_PRODUCT_MANIFEST.json')['files']
assert not drift(ROOT/'runtime/rw-gv2-20261004',gv),'GV2 parent drift'
extra=['engine/src/radiworks/core/context_images.py','engine/tests/test_context_images.py','webapp/js/case-personal.js','webapp/js/context-image.js']
paths=sorted([v['path'] for v in parent]+extra)
assert len(paths)==len(set(paths))==109
files=[{'path':v,'sha256':sha(R/v)} for v in paths]
changed=[v['path'] for v in parent if sha(R/v['path'])!=v['sha256']]
core=read(P/'FINAL_VERIFY.json')['numericalCoreFilesUnchanged']
assert all(sha(R/v['path'])==v['sha256'] for v in core),'Numerical kernel drift'
refs=read(P/'PARENT_REFERENCE_SOURCES.json')
assert all(Path(v['path']).is_file() and sha(Path(v['path']))==v['sha256'] for v in refs),'Reference source drift'
suite=next(ET.parse(R/'engine-final.xml').getroot().iter('testsuite'))
stats={k:int(suite.attrib[k]) for k in ('tests','failures','errors','skipped')}
stats['passed']=stats['tests']-stats['skipped']-stats['failures']-stats['errors']
assert stats['passed']==494 and stats['skipped']==3 and stats['failures']==stats['errors']==0
browser=(R/'browser-final.log').read_text(encoding='utf-8-sig')
assert sum(line.startswith('PASS ') for line in browser.splitlines())==28 and 'FAIL ' not in browser and 'CLEANUP' in browser
race=(R/'race-metadata-green.log').read_text(encoding='utf-8-sig')
assert sum(line.startswith('PASS ') for line in race.splitlines())==2 and 'FAIL ' not in race
assert (R/'image-browser-final.log').read_text(encoding='utf-8-sig').startswith('PASS ')
assert 'PASS: 18 files' in (R/'js-syntax.log').read_text(encoding='utf-8-sig')
now=datetime.datetime.now().astimezone().isoformat()
listeners=read(R/'LIVE_LISTENERS.json')
old=read(P/'LIVE_LISTENERS.json')
assert sorted(listeners,key=lambda v:v['LocalPort'])==sorted(old,key=lambda v:v['LocalPort']),'Protected PID/listener changed'
def ping(port):
 with urllib.request.urlopen('http://127.0.0.1:'+str(port)+'/ping',timeout=5) as resp:
  assert json.load(resp)['result']=='pong'
 return {'port':port,'pong':True}
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool: pongs=list(pool.map(ping,range(8103,8111)))
manifest={'createdAt':now,'files':files}
(R/'PRODUCT_MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
record={'createdAt':now,'candidateFiles':109,'parentFiles':len(parent),'parentDrift':[],'gv2ParentFiles':len(gv),'gv2ParentDrift':[],'changedParentFiles':changed,'newFiles':extra,'numericalCoreUnchanged':[v['path'] for v in core],'referenceSourcesUnchanged':[v['name'] for v in refs],'engine':stats,'boundBrowserSections':28,'raceSections':2,'imageBrowserPassed':True,'jsSyntaxFiles':18,'protectedListeners':listeners,'pongs':pongs,'liveMutation':False,'hostIntegrationRelease':False}
(R/'FINAL_VERIFY.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(record,ensure_ascii=False))
