import test from 'node:test';
import assert from 'node:assert/strict';
import { personalRequest, personalPage } from './personal-selection.js';
test('two selection axes retain explicit personal context, mode and seed',()=>{
 const binding={ref:'a'.repeat(64),contextVersion:3};
 const params={database:'Synthetic.txt',mode:'seeded',seed:0,weight:'Normal',requestId:'b'.repeat(32)};
 assert.deepEqual(personalRequest(binding,params),{expected_case_ref:binding.ref,expected_context_version:3,request_id:params.requestId,database:params.database,mode:'seeded',seed:0,weight:'Normal'});
 assert.equal(personalRequest(binding,{...params,mode:'stochastic',seed:null}).seed,null);
 for(const invalid of [null,{...binding,contextVersion:null}])assert.throws(()=>personalRequest(invalid,params),/Fall/);
 assert.throws(()=>personalRequest(binding,{...params,mode:'automatic'}),/Zufallsmodus/);
});
test('only complete personal jobs expose ranked pages',()=>{
 const rows=Array.from({length:24},(_,i)=>({inputIndex:i}));
 assert.deepEqual(personalPage({status:'running',rows},1),[]);
 assert.equal(personalPage({status:'completed',rows},1).length,21);
 assert.equal(personalPage({status:'completed',rows},2).length,3);
});
