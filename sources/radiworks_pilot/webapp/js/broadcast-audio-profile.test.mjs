import test from 'node:test';
import assert from 'node:assert/strict';
import { planFixedAudio, FIXED_AUDIO_PROFILES } from './broadcast-audio-profile.js';

test('approved single frequencies are preserved exactly',()=>{
 for(const [id,hz] of [['fixed-432',432],['fixed-528',528],['fixed-42962',429.62]]){
  const p=planFixedAudio({id,stageSeconds:10,repeat:false},48000);
  assert.deepEqual(p.frequencies,[hz]);assert.equal(p.stageFrames,480000);assert.equal(p.version,1);
 }
});
test('approved nine-stage sequence has sample-based duration and explicit repeat',()=>{
 const p=planFixedAudio({id:'solfeggio-9',stageSeconds:7,repeat:true},44100);
 assert.deepEqual(p.frequencies,[174,285,396,417,528,639,741,852,963]);
 assert.equal(p.stageFrames,308700);assert.equal(p.cycleFrames,2778300);assert.equal(p.repeat,true);
 assert.equal(Object.isFrozen(p),true);assert.equal(Object.isFrozen(p.frequencies),true);
});
test('unsupported profiles and malformed parameters fail explicitly',()=>{
 for(const bad of [{id:'unknown',stageSeconds:10,repeat:false},{id:'solfeggio-9',stageSeconds:0,repeat:false},{id:'fixed-432',stageSeconds:601,repeat:false},{id:'fixed-432',stageSeconds:1.5,repeat:false},{id:'fixed-432',stageSeconds:10,repeat:'yes'},{id:'fixed-432',stageSeconds:10,repeat:false,gv:800}])assert.throws(()=>planFixedAudio(bad,48000));
});
test('frequencies are checked against actual context sample rate',()=>{
 assert.throws(()=>planFixedAudio({id:'solfeggio-9',stageSeconds:10,repeat:false},2000));
 for(const rate of [undefined,NaN,Infinity,0,-1])assert.throws(()=>planFixedAudio({id:'fixed-432',stageSeconds:10,repeat:false},rate));
 assert.equal(FIXED_AUDIO_PROFILES['fixed-42962'][0],429.62);
});
test('planning neither mutates input nor receives analytical random values',()=>{
 const input={id:'fixed-528',stageSeconds:20,repeat:false};const before=structuredClone(input);planFixedAudio(input,48000);assert.deepEqual(input,before);
});