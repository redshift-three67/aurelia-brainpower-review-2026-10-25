from __future__ import annotations

from html.parser import HTMLParser
import subprocess
from pathlib import Path

import pytest

from apps.web.reports import ReportCatalog


ROOT = Path(__file__).resolve().parents[1]
APP_JS = ROOT / "apps" / "web" / "static" / "app.js"
API_JS = ROOT / "apps" / "web" / "static" / "workbench-api.js"
INDEX_HTML = ROOT / "apps" / "web" / "static" / "index.html"
APP_CSS = ROOT / "apps" / "web" / "static" / "app.css"


def _run_node(script: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["node", "-e", script],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def test_health_bootstrap_renders_structured_health_payload_without_false_error() -> None:
    script = f"""
const fs = require('fs');
const vm = require('vm');
function node() {{ return {{textContent:'', className:'', children:[], replaceChildren(){{this.children=[];}}, appendChild(x){{this.children.push(x);}}}}; }}
const nodes = {{
 '#python-version': node(), '#profile-count': node(), '#database-count': node(), '#health-status': node(),
 '#health-pill': node(), '#source-pill': node(), '#health-list': node(), '#source-list': node(), '#source-summary': node(),
}};
global.window = {{
 MorphicWorkbenchApi: {{
  async loadHealth() {{ return {{ok:true, python:{{version:'3.11.12'}}, profiles:{{total_profiles:502}}, databases:{{databases:{{a:{{name:'a',size_bytes:10}},b:{{name:'b',size_bytes:20}}}}}}}}; }},
  async loadSources() {{ return {{count:0,status_counts:{{}},sources:[]}}; }},
 }},
 MorphicWorkbenchState: {{}}, addEventListener() {{}},
}};
global.document = {{querySelector(s){{return nodes[s] || null;}},querySelectorAll(){{return [];}},createElement(tag){{return node();}}}};
vm.runInThisContext(fs.readFileSync({str(APP_JS)!r}, 'utf8'));
(async()=>{{
 await loadHealthAndSources();
 const actual={{pill:nodes['#health-pill'].textContent,profiles:nodes['#profile-count'].textContent,databases:nodes['#database-count'].textContent,items:nodes['#health-list'].children.length}};
 const expected={{pill:'Health: OK',profiles:502,databases:2,items:2}};
 if(JSON.stringify(actual)!==JSON.stringify(expected)) throw new Error(JSON.stringify(actual));
}})().catch(e=>{{console.error(e);process.exit(1);}});
"""
    result = _run_node(script)
    assert result.returncode == 0, result.stderr


def test_client_context_reload_finds_form_associated_controls() -> None:
    script = f"""
const fs=require('fs'); const vm=require('vm');
const controls={{birth_time:{{value:''}},email:{{value:''}},notes:{{value:''}}}};
global.window={{MorphicWorkbenchApi:{{async loadDraft(){{return {{draft:{{birth_time:'10:30',email:'qa@example.invalid',notes:'QA'}}}};}}}},MorphicWorkbenchState:{{}},addEventListener(){{}}}};
global.document={{querySelector(s){{if(!s.startsWith('[form="scan-form"]'))return null; const m=s.match(/name=\\"([^\\"]+)\\"/); return m ? controls[m[1]] || null : null;}},querySelectorAll(){{return[];}}}};
vm.runInThisContext(fs.readFileSync({str(APP_JS)!r},'utf8'));
(async()=>{{await loadClientContextDraft(); if(controls.birth_time.value!=='10:30'||controls.email.value!=='qa@example.invalid'||controls.notes.value!=='QA') throw new Error(JSON.stringify(controls));}})().catch(e=>{{console.error(e);process.exit(1);}});
"""
    result = _run_node(script)
    assert result.returncode == 0, result.stderr


def test_api_error_flattens_fastapi_validation_details() -> None:
    script = f"""
const fs=require('fs'); const vm=require('vm');
global.window={{}};
global.fetch=async()=>({{ok:false,status:422,async json(){{return {{detail:[{{loc:['body','image_path'],msg:'must be a .jpg/.jpeg file'}}]}};}}}});
vm.runInThisContext(fs.readFileSync({str(API_JS)!r},'utf8'));
(async()=>{{try{{await window.MorphicWorkbenchApi.loadScanPreview({{}});throw new Error('resolved');}}catch(e){{if(!e.message.includes('image_path')||!e.message.includes('.jpg/.jpeg'))throw e;}}}})().catch(e=>{{console.error(e);process.exit(1);}});
"""
    result = _run_node(script)
    assert result.returncode == 0, result.stderr


def test_api_error_exposes_start_operation_disposition() -> None:
    script = f"""
const fs=require('fs'); const vm=require('vm');
global.window={{MorphicWorkbenchState:{{}}}};
global.document={{querySelector(){{return null;}}}};
global.fetch=async()=>({{
 ok:false,
 status:404,
 headers:{{get(name){{return {{
  'x-morphic-start-operation':'safe-to-replace',
  'x-morphic-scan-profile-pool':'stale',
 }}[name] || null;}}}},
 async json(){{return {{detail:'report not found'}};}}
}});
vm.runInThisContext(fs.readFileSync({str(API_JS)!r},'utf8'));
(async()=>{{
 try{{await window.MorphicWorkbenchApi.startHarmonization({{}},'harm-operation-12345678');throw new Error('resolved');}}
 catch(e){{
  if(e.status!==404)throw e;
  if(e.message!=='report not found')throw e;
  if(e.startOperationDisposition!=='safe-to-replace')throw new Error(JSON.stringify(e));
  if(e.scanProfilePoolDisposition!=='stale')throw new Error(JSON.stringify(e));
 }}
}})().catch(e=>{{console.error(e);process.exit(1);}});
"""
    result = _run_node(script)
    assert result.returncode == 0, result.stderr


def test_start_operation_retention_uses_only_server_disposition() -> None:
    script = f"""
const fs=require('fs'); const vm=require('vm');
global.window={{MorphicWorkbenchState:{{}},addEventListener(){{}}}};
global.document={{querySelector(){{return null;}},querySelectorAll(){{return[];}}}};
vm.runInThisContext(fs.readFileSync({str(APP_JS)!r},'utf8'));
const cases=[
 [{{status:422,payload:{{detail:'ambiguous validation'}}}},true,'ambiguous-422'],
 [{{status:403,startOperationDisposition:'safe-to-replace'}},false,'safe-403'],
 [{{status:404,startOperationDisposition:'safe-to-replace'}},false,'safe-404'],
 [{{message:'network loss'}},true,'network'],
 [{{status:409,payload:{{detail:'identity mismatch'}}}},true,'identity-409'],
 [{{status:500}},true,'server-500'],
 [{{status:418}},true,'unknown'],
];
for(const [error,expected,label] of cases){{
 const actual=shouldRetainStartOperation(error);
 if(actual!==expected)throw new Error(`${{label}}: ${{actual}}`);
}}
"""
    result = _run_node(script)
    assert result.returncode == 0, result.stderr


def test_explicit_scan_stop_clears_only_a_terminal_response() -> None:
    script = f"""
const fs=require('fs'); const vm=require('vm');
function node() {{ return {{textContent:'',className:'',disabled:false,style:{{}},setAttribute(){{}},replaceChildren(){{}},appendChild(){{}}}}; }}
const nodes={{
 '#job-status-label':node(), '#scan-refresh-button':node(), '#scan-stop-button':node(),
 '#start-analysis-button':node(), '#preview-state':node(),
}};
global.window={{
 MorphicWorkbenchState:{{
  activeJobId:'scan-stop-contract',scanRunActive:true,
  scanProfileCatalogStatus:'ready',scanProfileCatalogLevel:3,
   scanProfileCatalog:{{profile_level:3,pool_authority:{{fingerprint:'a'.repeat(64)}},internal:{{count:9,profiles:Array.from({{length:9}},(_,i)=>({{id:`p-${{i}}`,label:`P ${{i}}`}}))}}}},
 }},
 MorphicWorkbenchApi:{{}}, MorphicWorkbenchRender:{{renderSubstepTimeline(){{}}}}, addEventListener(){{}},
}};
global.document={{querySelector(s){{if(s.includes('name="top_n"'))return {{value:'5'}};return nodes[s]||null;}},querySelectorAll(){{return[];}},createElement(){{return node();}}}};
global.setTimeout=()=>1; global.clearTimeout=()=>{{}};
vm.runInThisContext(fs.readFileSync({str(APP_JS)!r},'utf8'));

(async()=>{{
 const jobId='scan-stop-contract';
 window.MorphicWorkbenchApi.stopScanJob=async()=>({{status:'rollback_failed'}});
 await stopActiveScanJob();
 if(window.MorphicWorkbenchState.activeJobId!==jobId || !window.MorphicWorkbenchState.scanRunActive)
   throw new Error('unresolved stop response released authority');

 window.MorphicWorkbenchApi.stopScanJob=async()=>{{throw new TypeError('network failed');}};
 await stopActiveScanJob();
 if(window.MorphicWorkbenchState.activeJobId!==jobId || !window.MorphicWorkbenchState.scanRunActive)
   throw new Error('failed stop request released authority');

 window.MorphicWorkbenchApi.stopScanJob=async()=>{{throw Object.assign(new Error('auth'),{{status:403}});}};
 await stopActiveScanJob();
 if(window.MorphicWorkbenchState.activeJobId!==jobId || !window.MorphicWorkbenchState.scanRunActive)
   throw new Error('authentication pause released authority');
 if(!nodes['#job-status-label'].textContent.includes('Anmeldung erforderlich'))
   throw new Error(nodes['#job-status-label'].textContent);

 window.MorphicWorkbenchApi.stopScanJob=async()=>({{status:'stopped'}});
 await stopActiveScanJob();
 const actual={{
  activeJobId:window.MorphicWorkbenchState.activeJobId,
  active:window.MorphicWorkbenchState.scanRunActive,
  startDisabled:nodes['#start-analysis-button'].disabled,
  refreshDisabled:nodes['#scan-refresh-button'].disabled,
  stopDisabled:nodes['#scan-stop-button'].disabled,
 }};
 if(JSON.stringify(actual)!==JSON.stringify({{activeJobId:null,active:false,startDisabled:false,refreshDisabled:true,stopDisabled:true}}))
   throw new Error(JSON.stringify(actual));
}})().catch(e=>{{console.error(e);process.exit(1);}});
"""
    result = _run_node(script)
    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize("terminal_status", ["completed", "failed"])
def test_explicit_scan_stop_finalizes_terminal_scan_state(terminal_status: str) -> None:
    script = f"""
const fs=require('fs'); const vm=require('vm');
function node() {{ return {{textContent:'',className:'',disabled:false,style:{{}},setAttribute(){{}},replaceChildren(){{}},appendChild(){{}}}}; }}
const nodes={{
 '#job-status-label':node(), '#scan-refresh-button':node(), '#scan-stop-button':node(),
 '#start-analysis-button':node(), '#preview-state':node(),
}};
const terminalStatus={terminal_status!r};
const jobId=`scan-stop-${{terminalStatus}}`;
const calls={{sync:0,results:0,reports:0}};
global.window={{
 MorphicWorkbenchState:{{
  activeJobId:jobId,scanRunActive:true,
  scanProfileCatalogStatus:'ready',scanProfileCatalogLevel:3,
   scanProfileCatalog:{{profile_level:3,pool_authority:{{fingerprint:'a'.repeat(64)}},internal:{{count:9,profiles:Array.from({{length:9}},(_,i)=>({{id:`p-${{i}}`,label:`P ${{i}}`}}))}}}},
 }},
 MorphicWorkbenchApi:{{
  async stopScanJob(){{return {{status:terminalStatus}};}},
  async syncScanRunTrace(){{calls.sync+=1;return {{}};}},
  async loadScanResults(){{calls.results+=1;return {{top_profiles:[{{label:'ready'}}]}};}},
  async loadRunTrace(){{return {{status:terminalStatus}};}},
  async loadReports(){{calls.reports+=1;return {{clients:[]}};}},
 }},
 MorphicWorkbenchRender:{{renderSubstepTimeline(){{}},renderResults(){{}},renderRunTrace(){{}}}},
 addEventListener(){{}},
}};
global.document={{querySelector(s){{if(s.includes('name="top_n"'))return {{value:'5'}};return nodes[s]||null;}},querySelectorAll(){{return[];}},createElement(){{return node();}}}};
global.setTimeout=()=>1; global.clearTimeout=()=>{{}};
vm.runInThisContext(fs.readFileSync({str(APP_JS)!r},'utf8'));

(async()=>{{
 const finalized=await stopActiveScanJob();
 const expectedCalls=terminalStatus==='completed'
  ? {{sync:1,results:1,reports:1}}
  : {{sync:1,results:0,reports:0}};
 const actual={{
  finalized,
  calls,
  hasResults:Boolean(window.MorphicWorkbenchState.scanResults),
  activeJobId:window.MorphicWorkbenchState.activeJobId,
  active:window.MorphicWorkbenchState.scanRunActive,
  startDisabled:nodes['#start-analysis-button'].disabled,
  refreshDisabled:nodes['#scan-refresh-button'].disabled,
  stopDisabled:nodes['#scan-stop-button'].disabled,
 }};
 if(!actual.finalized || JSON.stringify(actual.calls)!==JSON.stringify(expectedCalls))
  throw new Error(`${{terminalStatus}} finalization: ${{JSON.stringify(actual)}}`);
 if(actual.hasResults!==(terminalStatus==='completed'))
  throw new Error(`${{terminalStatus}} results: ${{JSON.stringify(actual)}}`);
 if(
  actual.activeJobId!==jobId || actual.active
  || actual.startDisabled || !actual.refreshDisabled || !actual.stopDisabled
 ) throw new Error(`${{terminalStatus}} reservation: ${{JSON.stringify(actual)}}`);
}})().catch(e=>{{console.error(e);process.exit(1);}});
"""
    result = _run_node(script)
    assert result.returncode == 0, result.stderr


def test_stale_scan_stop_response_cannot_release_a_newer_reservation() -> None:
    script = f"""
const fs=require('fs'); const vm=require('vm');
function node() {{ return {{textContent:'',className:'',disabled:false,style:{{}},setAttribute(){{}},replaceChildren(){{}},appendChild(){{}}}}; }}
const nodes={{'#job-status-label':node(),'#scan-refresh-button':node(),'#scan-stop-button':node(),'#start-analysis-button':node(),'#preview-state':node()}};
let release;
global.window={{
 MorphicWorkbenchState:{{activeJobId:'scan-old-stop',scanRunActive:true}},
 MorphicWorkbenchApi:{{stopScanJob:async()=>new Promise(resolve=>{{release=resolve;}})}},
 MorphicWorkbenchRender:{{renderSubstepTimeline(){{}}}}, addEventListener(){{}},
}};
global.document={{querySelector(s){{if(s.includes('name="top_n"'))return {{value:'5'}};return nodes[s]||null;}},querySelectorAll(){{return[];}},createElement(){{return node();}}}};
global.setTimeout=()=>1; global.clearTimeout=()=>{{}};
vm.runInThisContext(fs.readFileSync({str(APP_JS)!r},'utf8'));
(async()=>{{
 const pending=stopActiveScanJob();
 await Promise.resolve();
 caseGeneration+=1;
 window.MorphicWorkbenchState.activeJobId='scan-new-stop';
 window.MorphicWorkbenchState.scanRunActive=true;
 release({{status:'stopped'}});
 await pending;
 if(window.MorphicWorkbenchState.activeJobId!=='scan-new-stop'||!window.MorphicWorkbenchState.scanRunActive)
  throw new Error(JSON.stringify(window.MorphicWorkbenchState));
}})().catch(e=>{{console.error(e);process.exit(1);}});
"""
    result = _run_node(script)
    assert result.returncode == 0, result.stderr


def test_first_terminal_response_wins_across_poll_and_stop_channels() -> None:
    script = f"""
const fs=require('fs'); const vm=require('vm');
function node() {{ return {{textContent:'',className:'',disabled:false,style:{{}},setAttribute(){{}},replaceChildren(){{}},appendChild(){{}}}}; }}
const nodes={{
 '#job-status-label':node(), '#scan-refresh-button':node(), '#scan-stop-button':node(),
 '#start-analysis-button':node(), '#preview-state':node(),
}};
global.window={{
 MorphicWorkbenchState:{{
  activeJobId:null,scanRunActive:false,
  scanProfileCatalogStatus:'ready',scanProfileCatalogLevel:3,
   scanProfileCatalog:{{profile_level:3,pool_authority:{{fingerprint:'a'.repeat(64)}},internal:{{count:9,profiles:Array.from({{length:9}},(_,i)=>({{id:`p-${{i}}`,label:`P ${{i}}`}}))}}}},
 }},
 MorphicWorkbenchApi:{{}},
 MorphicWorkbenchRender:{{renderSubstepTimeline(){{}},renderResults(){{}},renderRunTrace(){{}}}},
 addEventListener(){{}},
}};
global.document={{querySelector(s){{if(s.includes('name="top_n"'))return {{value:'5'}};return nodes[s]||null;}},querySelectorAll(){{return[];}},createElement(){{return node();}}}};
global.setTimeout=()=>1; global.clearTimeout=()=>{{}};
vm.runInThisContext(fs.readFileSync({str(APP_JS)!r},'utf8'));

async function runRace(terminalOwner) {{
 const jobId=`scan-race-${{terminalOwner}}`;
 let resolveLate;
 const lateResponse=new Promise(resolve=>{{resolveLate=resolve;}});
 window.MorphicWorkbenchState.activeJobId=jobId;
 window.MorphicWorkbenchState.scanRunActive=true;
 window.MorphicWorkbenchState.scanResults=null;
 window.MorphicWorkbenchApi={{
  async pollScanJob(){{
   return terminalOwner==='stop'
    ? lateResponse
    : {{status:'completed',progress_percent:100,completed_substeps:[],completed_stage_ids:[]}};
  }},
  async stopScanJob(){{
   return terminalOwner==='poll' ? lateResponse : {{status:'completed'}};
  }},
  async syncScanRunTrace(){{return {{}};}},
  async loadScanResults(){{return {{top_profiles:[{{label:terminalOwner}}]}};}},
  async loadRunTrace(){{return {{status:'completed'}};}},
  async loadReports(){{return {{clients:[]}};}},
 }};
 const late=terminalOwner==='stop'
  ? pollScanJob(jobId,caseGeneration,0)
  : stopActiveScanJob(caseGeneration);
 await Promise.resolve();
 const terminal=terminalOwner==='stop'
  ? stopActiveScanJob(caseGeneration)
  : pollScanJob(jobId,caseGeneration,0);
 await terminal;
 resolveLate({{status:'running',progress_percent:25,completed_substeps:[],completed_stage_ids:[]}});
 await late;
 const actual={{
  active:window.MorphicWorkbenchState.scanRunActive,
  hasResults:Boolean(window.MorphicWorkbenchState.scanResults),
  status:nodes['#job-status-label'].textContent,
  startDisabled:nodes['#start-analysis-button'].disabled,
  refreshDisabled:nodes['#scan-refresh-button'].disabled,
  stopDisabled:nodes['#scan-stop-button'].disabled,
 }};
 if(
  actual.active || !actual.hasResults || actual.status!=='abgeschlossen'
  || actual.startDisabled || !actual.refreshDisabled || !actual.stopDisabled
 ) throw new Error(`${{terminalOwner}}-first: ${{JSON.stringify(actual)}}`);
}}

(async()=>{{
 await runRace('stop');
 await runRace('poll');
 caseGeneration+=1;
 const newJobId='scan-race-new-generation';
 window.MorphicWorkbenchState.activeJobId=newJobId;
 window.MorphicWorkbenchState.scanRunActive=true;
 window.MorphicWorkbenchApi.pollScanJob=async()=>({{
  status:'running',progress_percent:10,completed_substeps:[],completed_stage_ids:[],
 }});
 await pollScanJob(newJobId,caseGeneration,0);
 if(!window.MorphicWorkbenchState.scanRunActive || nodes['#job-status-label'].textContent!=='laeuft')
  throw new Error(`new-key: ${{JSON.stringify(window.MorphicWorkbenchState)}}`);
 window.MorphicWorkbenchApi.pollScanJob=async()=>({{
  status:'completed',progress_percent:100,completed_substeps:[],completed_stage_ids:[],
 }});
 await pollScanJob(newJobId,caseGeneration,0);
 if(
  !nodes['#preview-state'].textContent.includes('erfolgreich')
  || nodes['#preview-state'].textContent.includes('Analyse laeuft')
 ) throw new Error(`running-completed: ${{nodes['#preview-state'].textContent}}`);
}})().catch(e=>{{console.error(e);process.exit(1);}});
"""
    result = _run_node(script)
    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize("first_owner", ["poll", "stop"])
def test_terminal_poll_and_stop_share_one_finalization_flight(first_owner: str) -> None:
    script = r"""
const fs = require("fs");
const vm = require("vm");
function node() {
  return {
    textContent: "", className: "", disabled: false, style: {},
    setAttribute() {}, replaceChildren() {}, appendChild() {},
  };
}
function deferred() {
  let resolve;
  const promise = new Promise(done => { resolve = done; });
  return {promise, resolve};
}
const firstOwner = __FIRST_OWNER__;
const jobId = `scan-terminal-flight-${firstOwner}`;
const nodes = {
  "#job-status-label": node(), "#job-returncode": node(),
  "#job-progress-fill": node(), "#job-progress-label": node(),
  "#job-phase-label": node(), "#job-substep-label": node(),
  "#job-log-tail": node(), "#job-substep-list": node(),
  "#scan-refresh-button": node(), "#scan-stop-button": node(),
  "#start-analysis-button": node(), "#preview-state": node(),
  "#report-list": node(), "#reports-state": node(),
};
const storage = new Map();
let operationKeyClears = 0;
const pollResponse = deferred();
const stopResponse = deferred();
const syncEntered = deferred();
const syncGate = deferred();
const calls = {sync: 0, results: 0, runTrace: 0, reports: 0};
global.window = {
  localStorage: {
    getItem(key) { return storage.get(key) || null; },
    setItem(key, value) { storage.set(key, String(value)); },
    removeItem(key) {
      if (key === "morphic_scan_start_operation_id") operationKeyClears += 1;
      storage.delete(key);
    },
  },
  MorphicWorkbenchState: {
    activeJobId: jobId, scanRunActive: true, scanStartOperationId: "scan-terminal-key",
    scanProfileCatalogStatus: "ready", scanProfileCatalogLevel: 3,
    scanProfileCatalog: {
      profile_level: 3,
      pool_authority: {fingerprint: "a".repeat(64)},
      internal: {count: 9, profiles: Array.from({length: 9}, (_, i) => ({id: `p-${i}`}))},
    },
  },
  MorphicWorkbenchApi: {
    async pollScanJob() { return pollResponse.promise; },
    async stopScanJob() { return stopResponse.promise; },
    async syncScanRunTrace() {
      calls.sync += 1;
      if (calls.sync === 1) syncEntered.resolve();
      await syncGate.promise;
      return {};
    },
    async loadScanResults() { calls.results += 1; return {top_profiles: []}; },
    async loadRunTrace() { calls.runTrace += 1; return {status: "completed"}; },
    async loadReports() { calls.reports += 1; return {clients: []}; },
  },
  MorphicWorkbenchRender: {
    renderSubstepTimeline() {}, renderResults() {}, renderRunTrace() {},
  },
  addEventListener() {},
};
storage.set("morphic_scan_start_operation_id", "scan-terminal-key");
global.document = {
  querySelector(selector) {
    if (selector.includes('name="top_n"')) return {value: "5"};
    return nodes[selector] || null;
  },
  querySelectorAll() { return []; },
  createElement() { return node(); },
};
global.setTimeout = () => 1;
global.clearTimeout = () => {};
vm.runInThisContext(fs.readFileSync(__APP_JS__, "utf8"));

(async () => {
  const poll = pollScanJob(jobId, caseGeneration, 0);
  const stop = stopActiveScanJob(caseGeneration);
  await Promise.resolve();
  const completed = {
    status: "completed", progress_percent: 100,
    completed_substeps: [], completed_stage_ids: [],
  };
  const failed = {
    status: "failed", progress_percent: 100,
    completed_substeps: [], completed_stage_ids: [],
  };
  if (firstOwner === "poll") pollResponse.resolve(completed);
  else stopResponse.resolve(failed);
  await syncEntered.promise;
  if (firstOwner === "poll") stopResponse.resolve(failed);
  else pollResponse.resolve(completed);
  await Promise.resolve();
  syncGate.resolve();
  await Promise.all([poll, stop]);

  const expectedStatus = firstOwner === "poll" ? "completed" : "failed";
  const expectedCalls = expectedStatus === "completed"
    ? {sync: 1, results: 1, runTrace: 1, reports: 1}
    : {sync: 1, results: 0, runTrace: 0, reports: 0};
  const actual = {
    calls,
    status: nodes["#job-status-label"].textContent,
    authority: terminalScanAuthorityStatus(jobId, caseGeneration),
    operationKey: readExistingStartOperationId("scan"),
    operationKeyClears,
    active: window.MorphicWorkbenchState.scanRunActive,
  };
  if (JSON.stringify(actual.calls) !== JSON.stringify(expectedCalls)) {
    throw new Error(`${firstOwner} duplicated terminal follow-up: ${JSON.stringify(actual)}`);
  }
  if (
    actual.status !== statusLabel(expectedStatus) || actual.authority !== expectedStatus
    || actual.operationKey !== null || actual.operationKeyClears !== 1 || actual.active
  ) throw new Error(`${firstOwner} terminal authority drift: ${JSON.stringify(actual)}`);
})().catch(error => { console.error(error); process.exit(1); });
""".replace("__APP_JS__", repr(str(APP_JS))).replace("__FIRST_OWNER__", repr(first_owner))

    result = _run_node(script)

    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize("render_target", ["results", "run-trace"])
def test_terminal_followup_exception_keeps_authority_released_and_enables_retry(
    render_target: str,
) -> None:
    script = f"""
const fs=require('fs'); const vm=require('vm');
function node() {{ return {{textContent:'',className:'',disabled:false,style:{{}},setAttribute(){{}},replaceChildren(){{}},appendChild(){{}}}}; }}
const nodes={{
 '#job-status-label':node(), '#scan-refresh-button':node(), '#scan-stop-button':node(),
 '#start-analysis-button':node(), '#preview-state':node(),
}};
const renderTarget={render_target!r};
const jobId='scan-render-failure';
let reportCalls=0;
global.window={{
 MorphicWorkbenchState:{{
  activeJobId:jobId,scanRunActive:true,
  scanProfileCatalogStatus:'ready',scanProfileCatalogLevel:3,
   scanProfileCatalog:{{profile_level:3,pool_authority:{{fingerprint:'a'.repeat(64)}},internal:{{count:9,profiles:Array.from({{length:9}},(_,i)=>({{id:`p-${{i}}`,label:`P ${{i}}`}}))}}}},
 }},
 MorphicWorkbenchApi:{{
  async pollScanJob(){{return {{status:'completed',progress_percent:100,completed_substeps:[],completed_stage_ids:[]}};}},
  async syncScanRunTrace(){{return {{}};}},
  async loadScanResults(){{return {{unexpected:'payload'}};}},
  async loadRunTrace(){{return {{status:'completed'}};}},
  async loadReports(){{reportCalls+=1;return {{clients:[]}};}},
 }},
 MorphicWorkbenchRender:{{
  renderSubstepTimeline(){{}},
  renderResults(){{if(renderTarget==='results')throw new Error('malformed result payload');}},
  renderRunTrace(){{if(renderTarget==='run-trace')throw new Error('malformed trace payload');}},
 }},
 addEventListener(){{}},
}};
global.document={{querySelector(s){{if(s.includes('name="top_n"'))return {{value:'5'}};return nodes[s]||null;}},querySelectorAll(){{return[];}},createElement(){{return node();}}}};
global.setTimeout=()=>1; global.clearTimeout=()=>{{}};
vm.runInThisContext(fs.readFileSync({str(APP_JS)!r},'utf8'));

(async()=>{{
 await pollScanJob(jobId,caseGeneration,0);
 const actual={{
  activeJobId:window.MorphicWorkbenchState.activeJobId,
  active:window.MorphicWorkbenchState.scanRunActive,
  startDisabled:nodes['#start-analysis-button'].disabled,
  refreshDisabled:nodes['#scan-refresh-button'].disabled,
  stopDisabled:nodes['#scan-stop-button'].disabled,
  message:nodes['#preview-state'].textContent,
  reportCalls,
 }};
 if(
  actual.activeJobId!==jobId || actual.active || actual.startDisabled
  || actual.refreshDisabled || !actual.stopDisabled || actual.reportCalls!==0
  || !actual.message.includes('Abschlussdaten') || !actual.message.includes('erneut')
 ) throw new Error(JSON.stringify(actual));
}})().catch(e=>{{console.error(e);process.exit(1);}});
"""
    result = _run_node(script)
    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize("failure_target", ["results", "reports"])
def test_terminal_followup_request_failure_enables_retry(failure_target: str) -> None:
    script = f"""
const fs=require('fs'); const vm=require('vm');
function node() {{ return {{textContent:'',className:'',disabled:false,style:{{}},setAttribute(){{}},replaceChildren(){{}},appendChild(){{}}}}; }}
const nodes={{
 '#job-status-label':node(), '#scan-refresh-button':node(), '#scan-stop-button':node(),
 '#start-analysis-button':node(), '#preview-state':node(), '#reports-state':node(),
}};
const failureTarget={failure_target!r};
const jobId=`scan-${{failureTarget}}-failure`;
let reportCalls=0;
global.window={{
 MorphicWorkbenchState:{{
  activeJobId:jobId,scanRunActive:true,
  scanProfileCatalogStatus:'ready',scanProfileCatalogLevel:3,
   scanProfileCatalog:{{profile_level:3,pool_authority:{{fingerprint:'a'.repeat(64)}},internal:{{count:9,profiles:Array.from({{length:9}},(_,i)=>({{id:`p-${{i}}`,label:`P ${{i}}`}}))}}}},
 }},
 MorphicWorkbenchApi:{{
  async pollScanJob(){{return {{status:'completed',progress_percent:100,completed_substeps:[],completed_stage_ids:[]}};}},
  async syncScanRunTrace(){{return {{}};}},
  async loadScanResults(){{
   if(failureTarget==='results')throw Object.assign(new Error('results unavailable'),{{status:500}});
   return {{top_profiles:[{{label:'ready'}}]}};
  }},
  async loadRunTrace(){{return {{status:'completed'}};}},
  async loadReports(){{
   reportCalls+=1;
   if(failureTarget==='reports')throw Object.assign(new Error('reports unavailable'),{{status:500}});
   return {{clients:[]}};
  }},
 }},
 MorphicWorkbenchRender:{{renderSubstepTimeline(){{}},renderResults(){{}},renderRunTrace(){{}}}},
 addEventListener(){{}},
}};
global.document={{querySelector(s){{if(s.includes('name="top_n"'))return {{value:'5'}};return nodes[s]||null;}},querySelectorAll(){{return[];}},createElement(){{return node();}}}};
global.setTimeout=()=>1; global.clearTimeout=()=>{{}};
vm.runInThisContext(fs.readFileSync({str(APP_JS)!r},'utf8'));

(async()=>{{
 await pollScanJob(jobId,caseGeneration,0);
 const actual={{
  active:window.MorphicWorkbenchState.scanRunActive,
  startDisabled:nodes['#start-analysis-button'].disabled,
  refreshDisabled:nodes['#scan-refresh-button'].disabled,
  stopDisabled:nodes['#scan-stop-button'].disabled,
  message:nodes['#preview-state'].textContent,
  reportCalls,
 }};
 const expectedReportCalls=failureTarget==='results'?0:1;
 if(
  actual.active || actual.startDisabled || actual.refreshDisabled || !actual.stopDisabled
  || !actual.message.includes('Abschlussdaten') || !actual.message.includes('erneut')
  || actual.reportCalls!==expectedReportCalls
 ) throw new Error(`${{failureTarget}}: ${{JSON.stringify(actual)}}`);
}})().catch(e=>{{console.error(e);process.exit(1);}});
"""
    result = _run_node(script)
    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize("auth_target", ["sync", "run-trace"])
def test_terminal_auth_pause_keeps_authority_released_and_retries_followup(
    auth_target: str,
) -> None:
    script = f"""
const fs=require('fs'); const vm=require('vm');
function node() {{ return {{textContent:'',className:'',disabled:false,style:{{}},setAttribute(){{}},replaceChildren(){{}},appendChild(){{}}}}; }}
const nodes={{
 '#job-status-label':node(), '#scan-refresh-button':node(), '#scan-stop-button':node(),
 '#start-analysis-button':node(), '#preview-state':node(),
}};
const authTarget={auth_target!r};
const jobId=`scan-auth-${{authTarget}}`;
const calls={{poll:0,sync:0,results:0,runTrace:0,reports:0}};
let authPending=true;
let holdFollowup=false;
let releaseFollowup=null;
let rejectAfterHold=false;
let pendingEndpoint=null;
const authError=()=>Object.assign(new Error('authentication required'),{{status:403}});
global.window={{
 MorphicWorkbenchState:{{
  activeJobId:jobId,scanRunActive:true,
  scanProfileCatalogStatus:'ready',scanProfileCatalogLevel:3,
   scanProfileCatalog:{{profile_level:3,pool_authority:{{fingerprint:'a'.repeat(64)}},internal:{{count:9,profiles:Array.from({{length:9}},(_,i)=>({{id:`p-${{i}}`,label:`P ${{i}}`}}))}}}},
 }},
 MorphicWorkbenchApi:{{
  async pollScanJob(){{calls.poll+=1;return {{status:'completed',progress_percent:100,completed_substeps:[],completed_stage_ids:[]}};}},
  async syncScanRunTrace(){{
   calls.sync+=1;
   if(authTarget==='sync'&&authPending){{authPending=false;throw authError();}}
   if(holdFollowup&&authTarget==='sync'){{
    pendingEndpoint='sync';
    await new Promise(resolve=>{{releaseFollowup=resolve;}});
    if(rejectAfterHold)throw authError();
   }}
   return {{}};
  }},
  async loadScanResults(){{calls.results+=1;return {{top_profiles:[{{label:'ready'}}]}};}},
  async loadRunTrace(){{
   calls.runTrace+=1;
   if(authTarget==='run-trace'&&authPending){{authPending=false;throw authError();}}
   if(holdFollowup&&authTarget==='run-trace'){{
    pendingEndpoint='run-trace';
    await new Promise(resolve=>{{releaseFollowup=resolve;}});
    if(rejectAfterHold)throw authError();
   }}
   return {{status:'completed'}};
  }},
  async loadReports(){{calls.reports+=1;return {{clients:[]}};}},
 }},
 MorphicWorkbenchRender:{{renderSubstepTimeline(){{}},renderResults(){{}},renderRunTrace(){{}}}},
 addEventListener(){{}},
}};
global.document={{querySelector(s){{if(s.includes('name="top_n"'))return {{value:'5'}};return nodes[s]||null;}},querySelectorAll(){{return[];}},createElement(){{return node();}}}};
global.setTimeout=()=>1; global.clearTimeout=()=>{{}};
vm.runInThisContext(fs.readFileSync({str(APP_JS)!r},'utf8'));

(async()=>{{
 await pollScanJob(jobId,caseGeneration,0);
 const paused={{
  activeJobId:window.MorphicWorkbenchState.activeJobId,
  active:window.MorphicWorkbenchState.scanRunActive,
  startDisabled:nodes['#start-analysis-button'].disabled,
  refreshDisabled:nodes['#scan-refresh-button'].disabled,
  stopDisabled:nodes['#scan-stop-button'].disabled,
  status:nodes['#job-status-label'].textContent,
  message:nodes['#preview-state'].textContent,
 }};
 if(
  paused.activeJobId!==jobId || paused.active || paused.startDisabled
  || paused.refreshDisabled || !paused.stopDisabled
  || !paused.status.includes('Anmeldung erforderlich')
  || !paused.message.includes('Anmeldung')
 ) throw new Error(`${{authTarget}} pause: ${{JSON.stringify(paused)}}`);

 await pollScanJob(jobId,caseGeneration,0);
 const expectedResults=authTarget==='sync'?1:2;
 const expectedRunTrace=authTarget==='sync'?1:2;
 if(
  calls.poll!==2 || calls.sync!==2 || calls.results!==expectedResults
  || calls.runTrace!==expectedRunTrace || calls.reports!==1
  || window.MorphicWorkbenchState.scanRunActive
 ) throw new Error(`${{authTarget}} retry: ${{JSON.stringify(calls)}}`);
 const completedMessage=nodes['#preview-state'].textContent;
 if(
  !completedMessage.includes('erfolgreich')
  || completedMessage.includes('Anmeldung') || completedMessage.includes('erneut')
 ) throw new Error(`${{authTarget}} completed: ${{completedMessage}}`);

 holdFollowup=true;
 rejectAfterHold=true;
 const pending=pollScanJob(jobId,caseGeneration,0);
 while(!releaseFollowup)await Promise.resolve();
 if(pendingEndpoint!==authTarget)
  throw new Error(`${{authTarget}} pending endpoint: ${{pendingEndpoint}}`);
 showInlineState('NEUER START', 'neutral');
 releaseFollowup();
 await pending;
 if(
  nodes['#preview-state'].textContent!=='NEUER START'
  || !nodes['#job-status-label'].textContent.includes('Anmeldung erforderlich')
  || nodes['#scan-refresh-button'].disabled
 ) throw new Error(`${{authTarget}} newer: ${{JSON.stringify({{
  message:nodes['#preview-state'].textContent,
  status:nodes['#job-status-label'].textContent,
  refreshDisabled:nodes['#scan-refresh-button'].disabled,
 }})}}`);
}})().catch(e=>{{console.error(e);process.exit(1);}});
"""
    result = _run_node(script)
    assert result.returncode == 0, result.stderr


class _ElementByIdParser(HTMLParser):
    def __init__(self, target_id: str) -> None:
        super().__init__()
        self.target_id = target_id
        self.element: tuple[str, dict[str, str | None]] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if attributes.get("id") == self.target_id:
            self.element = (tag, attributes)


def test_scan_stop_control_uses_existing_accessible_action_pattern() -> None:
    parser = _ElementByIdParser("scan-stop-button")
    parser.feed(INDEX_HTML.read_text(encoding="utf-8"))

    assert parser.element is not None
    tag, attributes = parser.element
    assert tag == "button"
    assert attributes["type"] == "button"
    assert "secondary-button" in str(attributes["class"]).split()
    assert "disabled" in attributes


def test_template_feedback_uses_inline_state_helper_signature() -> None:
    source = APP_JS.read_text(encoding="utf-8")
    template_block = source.split('const saveTemplate = $("#save-template-button")', 1)[1].split(
        'const newCase = $("#new-case-button")', 1
    )[0]
    assert 'showInlineState("#preview-state"' not in template_block
    assert 'showInlineState("Template lokal gespeichert.", "ok")' in template_block
    assert 'apiErrorMessage(e, "Template konnte nicht gespeichert werden.")' in template_block


def test_source_list_and_textareas_use_semantic_responsive_markup() -> None:
    html = INDEX_HTML.read_text(encoding="utf-8")
    css = APP_CSS.read_text(encoding="utf-8")
    assert '<ul id="source-list"' in html
    assert "textarea" in css
    assert "input,\nselect,\ntextarea {\n  width: 100%;" in css


def test_report_preview_shell_uses_self_hosted_css_without_inline_style(tmp_path: Path) -> None:
    root = tmp_path / "reports"
    report = root / "Client" / "20260101_010101_report.html"
    report.parent.mkdir(parents=True)
    report.write_text("<h1>Bericht</h1>", encoding="utf-8")
    catalog = ReportCatalog([root])
    entry = catalog.list(include_all_formats=True)["reports"][0]
    preview = catalog.preview(str(entry["id"]))
    content = str(preview["content"])
    assert preview["title"] == report.name
    assert preview["size"] == report.stat().st_size
    assert "<style" not in content
    assert 'href="/static/report-preview.css"' in content
    assert (ROOT / "apps" / "web" / "static" / "report-preview.css").is_file()


def test_workbench_pages_use_self_contained_favicon_without_404_request() -> None:
    for relative_path in (
        "apps/web/static/index.html",
        "apps/web/static/workflow-stepping.html",
    ):
        html = (ROOT / relative_path).read_text(encoding="utf-8")
        assert 'rel="icon"' in html
        assert 'href="data:image/svg+xml,' in html
