
from pathlib import Path
import json, hashlib, difflib, xml.etree.ElementTree as ET, urllib.request
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
ROOT=Path(__file__).resolve().parents[1]
PARENT=ROOT/'runtime/rw-gv2-20261004'
TARGET=ROOT/'runtime/rw-vf2-20261004'
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,d): (TARGET/n).write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
entries=json.loads((TARGET/'PARENT_PRODUCT_MANIFEST.json').read_text(encoding='utf-8-sig'))['files']
drift=[e['path'] for e in entries if digest(PARENT/e['path'])!=e['sha256']]
assert not drift, drift
paths=[e['path'] for e in entries]+['engine/src/radiworks/core/personal_context.py','engine/tests/test_personal_context.py']
for rel in paths:
 assert (TARGET/rel).resolve().is_relative_to(TARGET.resolve())
 assert (TARGET/rel).is_file(), rel
files=[{'path':rel,'sha256':digest(TARGET/rel)} for rel in sorted(paths)]
write('PRODUCT_MANIFEST.json',{'createdAt':datetime.now().astimezone().isoformat(),'files':files})
changed=[e['path'] for e in entries if digest(TARGET/e['path'])!=e['sha256']]
web=[e for e in entries if e['path'].startswith('webapp/')]
assert all(digest(TARGET/e['path'])==e['sha256'] for e in web)
core=json.loads((PARENT/'CORE_ALGORITHM_VERIFY.json').read_text(encoding='utf-8-sig'))
for e in core:
 assert digest(TARGET/e['path'])==e['sha256'], e['path']
refs=json.loads((TARGET/'PARENT_REFERENCE_SOURCES.json').read_text(encoding='utf-8-sig'))
reference_status=[{'name':e['name'],'existsNow':Path(e['path']).exists(),
 'unchanged':Path(e['path']).is_file() and digest(Path(e['path']))==e.get('sha256')} for e in refs if e.get('exists')]
assert all(e['unchanged'] for e in reference_status),reference_status
suites=ET.parse(TARGET/'vf2-engine-verified.xml').getroot().findall('testsuite')
tests=sum(int(e.get('tests',0)) for e in suites)
skips=sum(int(e.get('skipped',0)) for e in suites)
assert all(e.get('failures')=='0' and e.get('errors')=='0' for e in suites)
def ping(port):
 request=urllib.request.Request(f'http://127.0.0.1:{port}/ping',headers={'Connection':'close'})
 with urllib.request.urlopen(request,timeout=10) as response:
  body=json.load(response)
 assert body.get('result')=='pong',port
 return {'port':port,'pong':True}
with ThreadPoolExecutor(max_workers=8) as pool: live=list(pool.map(ping,range(8103,8111)))
result={'createdAt':datetime.now().astimezone().isoformat(),'parentFiles':len(entries),'parentDrift':drift,
 'candidateFiles':len(files),'changedParentFiles':changed,'newFiles':paths[-2:],
 'webappFilesUnchanged':len(web),'numericalCoreFilesUnchanged':core,
 'referenceSources':reference_status,'engine':{'total':tests,'passed':tests-skips,'skipped':skips,'failures':0,'errors':0},
 'pongPorts':live,'liveHomesRead':False,'keysRead':False,'liveProcessesMutated':False,
 'scope':'VF2-A backend only; no UI migration, no release, no canonical or F synchronization'}
write('FINAL_VERIFY.json',result)
patch=[]
for rel in changed+paths[-2:]:
 old=(PARENT/rel).read_text(encoding='utf-8-sig').splitlines(keepends=True) if (PARENT/rel).exists() else []
 new=(TARGET/rel).read_text(encoding='utf-8-sig').splitlines(keepends=True)
 patch.extend(difflib.unified_diff(old,new,fromfile='parent/'+rel if old else '/dev/null',tofile='candidate/'+rel))
(TARGET/'PRODUCT_DIFF.patch').write_text(''.join(patch),encoding='utf-8')
print(json.dumps({k:result[k] for k in ['parentFiles','parentDrift','candidateFiles','changedParentFiles','webappFilesUnchanged','engine','pongPorts']}))

