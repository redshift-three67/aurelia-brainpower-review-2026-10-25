import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';

test('random choice shows only reproducible and stochastic; server default is not a third algorithm',()=>{
 const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
 const select=html.match(/<select id="mode-select"[^>]*>([\s\S]*?)<\/select>/)[1];
 assert.deepEqual([...select.matchAll(/<option value="([^"]*)"/g)].map(m=>m[1]),['seeded','stochastic']);
});
function harness() {
 const callbacks=[];const select={value:'seeded',addEventListener:(type,fn)=>callbacks.push(fn)};
 const status={textContent:''};
 return {select,status,choose(value){select.value=value;callbacks.forEach(fn=>fn());}};
}
test('a server stochastic default is displayed explicitly and later defaults do not alter the selection',async()=>{
 const {initRandomModeSelection}=await import('./random-mode-selection.js');
 const h=harness();const choice=initRandomModeSelection(h.select,h.status);
 assert.equal(h.select.value,'');assert.equal(choice.ready(),false);
 choice.adopt('stochastic');assert.equal(h.select.value,'stochastic');assert.equal(choice.ready(),true);
 assert.match(h.status.textContent,/Stochastisch/);
 choice.adopt('seeded');assert.equal(h.select.value,'stochastic');
});
test('manual selection wins against a delayed server reply and case status refresh',async()=>{
 const {initRandomModeSelection}=await import('./random-mode-selection.js');
 const h=harness();const choice=initRandomModeSelection(h.select,h.status);
 h.choose('seeded');choice.adopt('stochastic');assert.equal(h.select.value,'seeded');
 h.choose('stochastic');choice.adopt('seeded');assert.equal(h.select.value,'stochastic');
});
test('failed or unsupported default requires a visible explicit choice; later user choice is retained',async()=>{
 const {initRandomModeSelection}=await import('./random-mode-selection.js');
 const h=harness();const choice=initRandomModeSelection(h.select,h.status);
 for(const unknown of [null,'other',undefined]){choice.adopt(unknown);assert.equal(choice.ready(),false);assert.match(h.status.textContent,/auswählen/);}
 h.choose('seeded');assert.equal(choice.ready(),true);choice.adopt('stochastic');assert.equal(h.select.value,'seeded');
});
test('personal start cannot fall back silently while a random choice is unresolved',async()=>{
 const {analyzeStartReadiness}=await import('./views/analyze.js');
 assert.equal(analyzeStartReadiness({procedure:'personal',mode:'',entropyStatus:null,analysisBusy:false,catalogsReady:true}).disabled,true);
 assert.equal(analyzeStartReadiness({procedure:'personal',mode:'seeded',entropyStatus:null,analysisBusy:false,catalogsReady:true}).disabled,false);
});
