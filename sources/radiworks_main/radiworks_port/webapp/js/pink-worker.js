import { PinkStream } from './pink-stream.js';
import { planPinkPulse, pulseGainAtFrame } from './pink-pulse-profile.js';
let stream=null,sequence=0,pulse=null,nextFrame=null;
self.onmessage=event=>{
 try{
  const m=event.data;
  if(m?.type==='init'&&!stream){pulse=m.pulseProfile?planPinkPulse(m.pulseProfile,m.sampleRate):null;stream=new PinkStream(m.sampleRate,m.seed,{bounded:true});self.postMessage({type:'ready'});return;}
  if(m?.type!=='chunk'||!stream||m.sequence!==sequence||m.frames!==32768)throw new Error('Rauschworker-Auftrag oder Reihenfolge ungültig.');
  if(pulse&&(!Number.isInteger(m.startFrame)||m.startFrame<0||m.startFrame>86400*pulse.sampleRate||(nextFrame!==null&&m.startFrame!==nextFrame)))throw new Error('Pulsposition oder Reihenfolge ungültig.');
  const samples=stream.chunk(m.frames);
  if(pulse){for(let i=0;i<samples.length;i++){const frame=m.startFrame+i;samples[i]*=frame<=86400*pulse.sampleRate?pulseGainAtFrame(pulse,frame):0;}nextFrame=m.startFrame+samples.length;}
  self.postMessage({type:'chunk',sequence:sequence++,samples},[samples.buffer]);
 }catch(error){self.postMessage({type:'error',message:error.message});stream=null;self.close();}
};
