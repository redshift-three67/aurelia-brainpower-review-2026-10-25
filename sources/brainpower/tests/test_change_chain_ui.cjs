const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync('governor_workbench/static/app.js', 'utf8');
const start = source.indexOf('  async function runChangeChainTransition(');
assert.notEqual(start, -1, 'Explicit chain transition router must exist');
const end = source.indexOf('\n  async function runPilotTransfer(', start);
async function check(chains, fail = false) {
  const calls = [], notices = [], pending = new Set();
  const context = {pending, pilotBusy: () => pending.size > 0, renderJobs(){}, registryControls(){},
    activateTab(){}, loadState: async()=>{}, notify: message => notices.push(message),
    api: async(path, payload) => { calls.push([path,payload]); if (fail) throw Error('State unavailable'); return {chains}; }};
  vm.createContext(context); vm.runInContext(source.slice(start,end),context);
  await context.runChangeChainTransition({candidate_id:'candidate',selection_id:'selection',observed_scope_hash:'H1'},
    {id:'receipt'}, 'Operator note', {disabled:false});
  assert.equal(pending.size,0);
  return {calls,notices};
}
async function dialogChecks() {
  class Element {
    constructor(tag, text='') {this.tag=tag;this.textContent=text;this.children=[];this.handlers={};this.value='';this.disabled=false;this.isConnected=true;}
    append(...items){this.children.push(...items);}
    replaceChildren(...items){this.children=items;}
    setAttribute(name,value){this[name]=value;}
    addEventListener(name,handler){this.handlers[name]=handler;}
    querySelectorAll(selector){return this.children.flatMap(child=>[child,...child.querySelectorAll('*')]).filter(child=>selector==='*' || child.tag==='input' && (selector==='input' || child.checked));}
    showModal(){}
    close(){this.handlers.close?.();}
    remove(){this.isConnected=false;}
    emit(type){if(type!=='click' || !this.disabled)this.handlers[type]?.();}
  }
  const body=new Element('body'),calls=[],pending=new Set();
  let snapshot=null,consents=[];
  const h1={eligible:true,binding_hash:'h1-binding',binding:{original_scope_hash:'H0',effective_scope_hash:'H1',predecessor_event_id:'a-event',step_id:'B'}};
  const context={node:(tag,cls,text)=>new Element(tag,text),document:{body,createTextNode:text=>new Element('text',text)},
    pending,pilotBusy:()=>pending.size>0,notify(){},activateTab(){},loadState:async()=>{},
    api:async(path,payload)=>{
      calls.push([path,payload]);
      if(path.endsWith('/state'))return {chains:snapshot?[snapshot]:[],consents};
      if(path.endsWith('/preview'))return {eligible:true,binding:{scope_hash:'H0',step_ids:['A','B']},binding_hash:'baseline-binding',steps:[]};
      if(path.endsWith('/begin')){snapshot={chain:{id:'chain',binding:{scope_hash:'H0',step_ids:['A','B']},note:payload.note},events:[],transition_count:0};return {chain:snapshot.chain};}
      if(path.endsWith('/successor-preview'))return h1;
      if(path.endsWith('/acknowledge')){const consent={id:'consent',binding_hash:h1.binding_hash,note:payload.note};consents=[consent];return {consent};}
      if(path.endsWith('/propose'))return {job:{id:'proposal'}};
      throw Error('Unexpected route '+path);
    }};
  vm.createContext(context);
  const from=source.indexOf('  function showChangeChainPreview('),to=source.indexOf('\n  function showTestChain(',from);
  vm.runInContext(source.slice(from,to),context);
  context.showChangeChainPreview({id:'candidate',proposal:{steps:[{id:'A',action:'change'},{id:'B',action:'change'}]}});
  const settle=()=>new Promise(resolve=>setImmediate(resolve));await settle();
  const dialog=body.children[0],all=()=>dialog.querySelectorAll('*');
  const button=text=>all().find(item=>item.tag==='button' && item.textContent===text);
  const field=label=>all().find(item=>item['aria-label']===label);
  assert.deepEqual(calls.map(c=>c[0]),['/api/change-chains/state'],'Opening only reads history');
  for(const input of all().filter(item=>item.tag==='input')){input.checked=true;input.emit('change');}
  button('Änderungsfolge prüfen').emit('click');await settle();
  const note=field('Begründung zum Ausgangsstand H0');note.value='Baseline note';note.emit('input');
  button('Ausgangsstand H0 ausdrücklich festhalten').emit('click');await settle();
  assert.equal(calls.find(c=>c[0].endsWith('/begin'))[1].note,'Baseline note');
  assert.equal(calls.filter(c=>c[0].endsWith('/propose')).length,0);
  snapshot={...snapshot,transition_count:1,events:[{kind:'transition',id:'a-event',note:'A complete',evidence:{technical_receipt:{binding:{observed_scope_hash:'H1'}},transaction:{id:'tx-a'}}}],active_transition_ids:['a-event'],scope_hash:'H1'};
  const successorNote=field('Begründung zur H1-Bestätigung');successorNote.value='H1 note';successorNote.emit('input');
  button('Kettenhistorie aktualisieren').emit('click');await settle();
  assert.equal(successorNote.value,'H1 note','History refresh preserves operator draft');
  assert.ok(all().some(item=>String(item.textContent).includes('H1: H1')),'Real technical receipt shape displays H1 hash');
  button('H1 für B frisch prüfen').emit('click');await settle();
  button('Diesen H1-Stand ausdrücklich bestätigen').emit('click');await settle();
  assert.equal(calls.filter(c=>c[0].endsWith('/acknowledge')).length,1);
  assert.equal(calls.filter(c=>c[0].endsWith('/propose')).length,0,'H1 acknowledgement never starts model job');
  button('B mit Modellen im Arbeitsbereich vorschlagen').emit('click');await settle();
  assert.equal(calls.filter(c=>c[0].endsWith('/propose')).length,1);
  assert.equal(calls.at(-1)[1].consent_id,'consent');
  snapshot={...snapshot,requires_new_plan:true,transition_count:2,events:[...snapshot.events,
    {kind:'transition',id:'b-event',note:'B complete',evidence:{technical_receipt:{binding:{observed_scope_hash:'H2'}},transaction:{id:'tx-b'}}},
    {kind:'rollback',id:'rollback-b',note:'Rollback B'}]};
  const before=calls.length;
  context.showChangeChainPreview({id:'candidate',proposal:{steps:[]}});await settle();
  const reopened=body.children.at(-1).querySelectorAll('*');
  assert.deepEqual(calls.slice(before).map(c=>c[0]),['/api/change-chains/state'],'Reload never replays prior proposal');
  assert.ok(reopened.some(item=>String(item.textContent).includes('H2: H2')));
  assert.ok(reopened.some(item=>String(item.textContent).includes('Neue Planrevision erforderlich')));
  assert.equal(reopened.find(item=>item.textContent==='H1 für B frisch prüfen').disabled,true);
  assert.equal(reopened.find(item=>item.textContent==='B mit Modellen im Arbeitsbereich vorschlagen').disabled,true);
  console.log('Change-chain dialog: explicit baseline/H1/proposal and draft preservation passed');
}
(async()=>{
  const chain=await check([{chain:{id:'chain'},head_id:'fresh-head'}]);
  assert.equal(chain.calls[1][0],'/api/change-chains/confirm');
  assert.equal(chain.calls[1][1].expected_head,'fresh-head');
  assert.equal(chain.calls[1][1].technical_receipt_id,'receipt');
  assert.equal(chain.calls[1][1].note,'Operator note');
  const legacy=await check([]);
  assert.equal(legacy.calls[1][0],'/api/pilot/transition');
  const failed=await check([],true);
  assert.equal(failed.calls.length,1,'Failure must never fall back to legacy transition');
  assert.equal(failed.notices.length,1);
  console.log('Change-chain UI transition routing: 3 cases passed');
  await dialogChecks();
  const fixture=fs.readFileSync('docs/verification/S3c_C4_browser_fixture.html','utf8');
  const script=fixture.slice(fixture.indexOf('<script>')+8,fixture.indexOf('</script>'));
  new vm.Script(script);
  const productionStart=source.indexOf('  function showChangeChainPreview(');
  const production=source.slice(productionStart,source.indexOf('  function showTestChain(',productionStart)).trimEnd();
  assert.ok(script.includes(production),'Browser fixture contains unchanged production dialog function');
  assert.ok(fixture.includes("connect-src 'none'"),'Fixture forbids network requests');
  console.log('Browser fixture: script syntax and exact production function parity passed');
})().catch(error=>{console.error(error);process.exitCode=1;});
