// Presentation unit test; no browser, network, model calls or real journal.
const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const source = fs.readFileSync('governor_workbench/static/app.js','utf8');
const start = source.indexOf('  function tokenUsage(');
const end = source.indexOf('  function renderJobs()',start);
assert(start >= 0 && end > start);
function node(tag, cls, text) {
  return {tag,cls,text,dataset:{},children:[],append(...children){this.children.push(...children);}};
}
const context = vm.createContext({node,Set});
vm.runInContext(source.slice(start,end),context);
const text = item => [item.text,...item.children.map(text)].filter(v=>v !== undefined).join(' ');
assert.match(text(context.tokenUsage({})),/nicht erfasst/);
const job={id:'fixture',token_usage:{recorded:true,complete:false,input_tokens:120,output_tokens:30,total_tokens:150,call_count:2,calls:[{model:'gpt-5.6-terra',status:'completed',input_tokens:120,output_tokens:30,total_tokens:150},{model:'gpt-5.6-sol',status:'failed',input_tokens:null,output_tokens:null,total_tokens:null}]}};
const first=context.tokenUsage(job,new Set(['usage-fixture']));
assert.match(text(first),/Gesamt: 150/);
assert.match(text(first),/Teilsummen/);
assert.match(text(first),/Fehlgeschlagen/);
assert.match(text(first),/unbekannt/);
assert.equal(first.children.at(-1).open,true);
assert.equal(text(first),text(context.tokenUsage(job)));
assert.equal(job.token_usage.total_tokens,150);
job.token_usage.calls[0].routing={requested:'auto',effective:'low',role:'orchestrator',reason:'Bestätigte Routine',version:'rh1-v1'};
assert.match(text(context.tokenUsage(job)),/auto.*low/);
assert.match(text(context.tokenUsage(job)),/Bestätigte Routine/);
assert.match(text(context.tokenUsage(job)),/rh1-v1/);
assert.match(text(context.tokenUsage(job)),/Auswahl nicht erfasst/);
job.token_usage.cached_tokens=70;
job.token_usage.reasoning_tokens=20;
job.token_usage.calls[0].cached_tokens=70;
job.token_usage.calls[0].reasoning_tokens=20;
assert.match(text(context.tokenUsage(job)),/Cache-Eingang: 70/);
assert.match(text(context.tokenUsage(job)),/Reasoning-Ausgang: 20/);
console.log('Token UI: legacy, partial failure, unknown values, stable totals and expanded details passed.');
