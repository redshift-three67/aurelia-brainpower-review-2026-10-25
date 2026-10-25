import test from 'node:test';
import assert from 'node:assert/strict';
import {describeAudioAssignment} from './broadcast-audio-assignment.js';
const row=(audioProfile,elapsed=0,extra={})=>({seconds:300,elapsed,profile:{audioProfile,stageSeconds:60,repeat:false,...extra}});
test('original disabled is distinct from device activation and no broadcast',()=>{
 assert.match(describeAudioAssignment([],false),/Kein aktiver Broadcast/);
 assert.match(describeAudioAssignment([row('original')],false),/Original-Ereignistöne.*ausgeschaltet/);
 assert.match(describeAudioAssignment([row('original')],true),/Original-Ereignistöne.*Resonanzereignis/);
});
test('frozen profiles, expired one-pass and repeat are explicit',()=>{
 assert.match(describeAudioAssignment([row('fixed-432')],false),/432 Hz.*zugeordnet/);
 assert.match(describeAudioAssignment([row('fixed-432',90)],false),/Einmalfolge beendet/);
 assert.doesNotMatch(describeAudioAssignment([row('fixed-432',90,{repeat:true})],false),/Einmalfolge beendet/);
 assert.match(describeAudioAssignment([row('off')],false),/Audio aus/);
});
test('pulse full coupled cycle and damaged profile are handled without replay',()=>{
 assert.match(describeAudioAssignment([row('pink-fibonacci-v1',10,{stageSeconds:1,modulationDepthPercent:50})],false),/zugeordnet/);
 assert.match(describeAudioAssignment([row('pink-fibonacci-v1',33,{stageSeconds:1,modulationDepthPercent:50})],false),/Einmalfolge beendet/);
 assert.match(describeAudioAssignment([row('not-valid')],false),/nicht prüfbar/);
});
