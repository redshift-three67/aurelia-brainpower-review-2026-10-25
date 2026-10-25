const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const source=fs.readFileSync('governor_workbench/static/app.js','utf8');
const start=source.indexOf('  function workflowHint('),end=source.indexOf('\n  function renderWorkflowGuide(',start);
assert.ok(start>=0 && end>start,'Workflow guidance must use a testable decision rule');
const c={};vm.createContext(c);vm.runInContext(source.slice(start,end),c);
const ready={scope:true,current:true,ready:true,plansLoaded:true,planCount:1,plan:true,planCurrent:true,validPlan:true};
for(const [input,step,target] of [
  [{},1,null], [{scope:true,busy:true},1,null], [{scope:true,current:false},1,'intake'],
  [{scope:true,current:true,ready:false},2,'scope-intake-project'],
  [{scope:true,current:true,ready:false,member:true,proofs:false},2,null],
  [{scope:true,current:true,ready:false,member:true,proofs:true,canConfirm:true},2,'intake-confirm'],
  [{scope:true,current:true,ready:false,member:true,proofs:true,staleDraft:true},2,'scope-intake-draft-load'],
  [{scope:true,current:true,ready:true},3,'scope-plans-load'],
  [{...ready,plan:false},3,'scope-plan-candidate'],
  [{...ready,planCurrent:false},3,'scope-plans-load'],
  [{...ready,validPlan:false},3,null],
  [ready,4,'scope-plan-detail'],
]){const result=c.workflowHint(input);assert.equal(result.step,step);assert.equal(result.target,target);assert.ok(result.title&&result.reason);}
const empty=c.workflowHint({...ready,plan:false,planCount:0});assert.equal(empty.target,'plan');
const elements=new Map(),marks=new Set();
function el(id){if(!elements.has(id))elements.set(id,{disabled:false,classList:{add:()=>marks.add(id),remove:()=>marks.delete(id)},querySelector:()=>el('submit')});return elements.get(id);}
const scope={kind:'group',id:'g',result:{scope_hash:'h',plan_ready:true,intake:[]}};
const button=el('plan-button');button.dataset={scopeAction:'scope_plan',scopeKind:'group',scopeId:'g'};button.disabled=true;
Object.assign(c,{$:el,set:(id,text)=>el(id).textContent=text,intakeScope:scope,selectedPlan:()=>null,pending:new Set(),
  scopeSourceCurrent:h=>h==='h',scopeName:()=> 'Fixture Group',plansScope:{kind:'group',id:'g'},strategiesScope:scope,scopePlans:[],loadedIntakeDraft:null,
  document:{querySelectorAll:selector=>selector==='.workflow-next'?[...marks].map(el):[button]}});
vm.runInContext(source.slice(end,source.indexOf('\n  function planControls(',end)),c);
c.renderWorkflowGuide();assert.equal(button.disabled,true);assert.equal(marks.size,0,'Disabled action is never highlighted');
assert.match(el('scope-guide-reason').textContent,/gesperrt/);assert.match(el('scope-guide-context').textContent,/keine allgemeine Gruppenausführung/);
button.disabled=false;c.renderWorkflowGuide();assert.deepEqual([...marks],['plan-button']);
c.strategiesScope=null;c.renderWorkflowGuide();assert.deepEqual([...marks],['scope-plans-load'],'Missing current strategy requires common reload');
c.pending.add('scope:intake:project:b');c.renderWorkflowGuide();assert.equal(marks.size,0,'Pending context removes previous highlight');
console.log('Workflow guide: 13 decision cases plus disabled/enabled/pending rendering; no action dispatch.');
