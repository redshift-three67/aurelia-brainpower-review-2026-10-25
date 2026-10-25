const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const source=fs.readFileSync('governor_workbench/static/app.js','utf8');
const fields=['requirements','test-strategy','dependencies','open-evidence'];
function fixture(){
  const elements=new Map();
  function el(id){if(!elements.has(id))elements.set(id,{value:'',children:[],elements:[],dataset:{},textContent:'',hidden:false,
    replaceChildren(...xs){this.children=xs;},append(...xs){this.children.push(...xs);},scrollIntoView(){},
    reset(){if(id==='scope-intake-form'){fields.forEach(f=>el('scope-intake-'+f).value='');el('scope-intake-project').value='';}},
    querySelector(){return el(id+'-submit');}});return elements.get(id);}
  const calls=[],notices=[],responses=new Map();
  const c={console,Date,Map,Set,encodeURIComponent,intakeScope:null,intakeProject:'',intakeDrafts:new Map(),intakeSelections:new Map(),
    loadedIntakeDraft:null,scopeStrategies:[],strategiesScope:null,scopePlans:[],plansScope:null,intakeRequest:0,pending:new Set(),state:{registry:{observations:[]}},
    $:el,set:(id,text)=>el(id).textContent=text,node:(tag,cls,text)=>({tag,textContent:text,append(){}}),
    scopeName:(kind,id)=>kind+':'+id,stamp:x=>x,readable:x=>x,scopeBlocked:()=>false,registryControls(){},intakeControls(){},
    renderStrategies(){},renderPlanOptions(){c.scopePlansRendered=c.scopePlans;},planControls(){},renderWorkflowGuide(){},
    registryOptions(id,items){if(!items.some(x=>x.id===el(id).value))el(id).value='';},
    notify:(...x)=>notices.push(x),activateTab(){},loadState:async()=>{},
    api:async(path,body)=>{calls.push({path,body});return await responses.get(path);}};
  vm.createContext(c);
  for(const name of ['intakeDraftKey','rememberIntakeDraft','restoreIntakeDraft','changeIntakeProject','prepareIntakeForms','runScope','loadScopePlans','scopeSourceCurrent','intakeControls','saveScopeRecord']){
    const pattern=new RegExp('^  (?:async )?function '+name+'\\(','m'),match=pattern.exec(source);if(!match)continue;
    const rest=source.slice(match.index),next=/\n  (?:async )?function /.exec(rest);
    vm.runInContext(next?rest.slice(0,next.index):rest,c);
  }
  const show=(kind,id,hash=id)=>c.prepareIntakeForms(kind,id,{scope_hash:hash,intake:[{project_id:kind==='group'?'a':id,memories_present:true,evidence_complete:true},...(kind==='group'?[{project_id:'b',memories_present:true,evidence_complete:true}]:[])],vault_sources:[]});
  const select=id=>{el('scope-intake-project').value=id;if(c.changeIntakeProject)c.changeIntakeProject();};
  return {c,el,calls,notices,responses,show,select};
}
function deferred(){let resolve;const promise=new Promise(r=>resolve=r);return {promise,resolve};}
async function main(){
  {
    const f=fixture();f.show('project','a');f.select('a');f.el('scope-intake-requirements').value='Only A';
    f.show('project','b');f.select('b');assert.equal(f.el('scope-intake-requirements').value,'');
    f.el('scope-intake-requirements').value='Only B';f.show('project','a');
    assert.equal(f.el('scope-intake-project').value,'a');assert.equal(f.el('scope-intake-requirements').value,'Only A','A draft survives switch');
    f.show('group','g');f.select('a');assert.equal(f.el('scope-intake-requirements').value,'','Same member in group has separate draft');
    f.el('scope-intake-requirements').value='Group A';f.show('project','a');assert.equal(f.el('scope-intake-requirements').value,'Only A');
    f.show('group','g');f.select('b');assert.equal(f.el('scope-intake-requirements').value,'');
    f.el('scope-intake-requirements').value='Group B';f.select('a');assert.equal(f.el('scope-intake-requirements').value,'Group A');
    f.show('project','a');
    f.c.loadedIntakeDraft={loaded_scope_hash:'a'};
    f.show('project','a','new-hash');assert.equal(f.el('scope-intake-requirements').value,'Only A');
    assert.equal(f.c.loadedIntakeDraft.loaded_scope_hash,'a','Restored fields keep original source binding');
    fields.forEach(field=>f.el('scope-intake-'+field).value='Reviewed text');f.c.intakeControls();
    assert.equal(f.el('scope-intake-form-submit').disabled,true,'Actual controls block stale server draft');
  }
  {
    const f=fixture();f.show('project','a');f.select('a');fields.forEach(field=>f.el('scope-intake-'+field).value='Reviewed text');
    f.c.rememberIntakeDraft();f.responses.set('/api/intake',{});
    f.responses.set('/api/scope?kind=project&id=a',{scope_hash:'a',intake:[{project_id:'a',memories_present:true,evidence_complete:true}]});
    await f.c.saveScopeRecord('intake',f.el('scope-intake-form'));
    assert.equal(f.calls[0].body.project_id,'a');assert.equal(f.calls[0].body.scope_hash,'a');
    assert.equal(f.c.intakeDrafts.size,0,'Confirmed draft is not resurrected');
    f.show('project','b');f.show('project','a');f.select('a');assert.equal(f.el('scope-intake-requirements').value,'');
  }
  {
    const f=fixture(),a=deferred(),b=deferred();
    f.responses.set('/api/scope?kind=project&id=a',a.promise);f.responses.set('/api/scope?kind=project&id=b',b.promise);
    const old=f.c.runScope('intake','project','a'),fresh=f.c.runScope('intake','project','b');
    b.resolve({scope_hash:'b',intake:[]});await fresh;a.resolve({scope_hash:'a',intake:[]});await old;
    assert.equal(f.c.intakeScope.id,'b','Late A response must not replace B');assert.equal(f.c.pending.size,0);
  }
  {
    const f=fixture(),plans=deferred();f.show('project','a');f.responses.set('/api/plans?kind=project&id=a',plans.promise);
    f.responses.set('/api/strategies?kind=project&id=a',{scope_hash:'a',revisions:[]});
    const old=f.c.loadScopePlans();f.show('project','b');plans.resolve({plans:[{id:'A-only'}]});await old;
    assert.equal(f.c.intakeScope.id,'b');assert.equal(f.c.scopePlans.length,0,'Late A plans cannot activate B actions');
  }
  {
    const f=fixture(),review=deferred();f.el('supervisor').value='gpt-6-astra';f.show('project','a');f.responses.set('/api/actions',review.promise);
    const running=f.c.runScope('scope_review','project','a');f.show('project','b');review.resolve({job:{id:'job-a'}});await running;
    assert.equal(f.calls[0].body.scope_id,'a');assert.equal(f.calls[0].body.supervisor,'gpt-6-astra');assert.equal(f.c.intakeScope.id,'b');
  }
  console.log('Scope UI: separated drafts, source binding, late replies and running-job target verified.');
}
main().catch(e=>{console.error(e);process.exitCode=1;});
