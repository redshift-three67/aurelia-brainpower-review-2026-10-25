export const PHI=(1+Math.sqrt(5))/2;
const LIMITS=Object.freeze({'pink-pulse-v1':600,'pink-phi-v1':87,'pink-fibonacci-v1':46});
const plans=new WeakSet();
export const isPulseProfile=id=>Object.hasOwn(LIMITS,id);
export function pulseBaseLimit(id){if(!isPulseProfile(id))throw new Error('Unbekanntes Pulsprofil.');return LIMITS[id];}
export function planPinkPulse(profile,sampleRate){
 const id=profile?.audioProfile,limit=pulseBaseLimit(id);
 if(!Number.isInteger(sampleRate)||sampleRate<8000||sampleRate>192000||!Number.isInteger(profile.stageSeconds)||profile.stageSeconds<1||profile.stageSeconds>limit||!Number.isInteger(profile.modulationDepthPercent)||profile.modulationDepthPercent<0||profile.modulationDepthPercent>100||typeof profile.repeat!=='boolean')throw new Error('Pulsprofil, Basisschrittdauer oder Modulationstiefe ungültig.');
 const factors=id==='pink-phi-v1'?Array.from({length:5},(_,k)=>PHI**k):id==='pink-fibonacci-v1'?[1,2,3,5,8,13]:[1];
 let cycleFrames=0,cycleCycles=0,seconds=0;
 const stages=factors.map(factor=>{const duration=profile.stageSeconds*factor,pulseHz=(id==='pink-fibonacci-v1'?.5:1)*factor,frames=Math.round(duration*sampleRate);const s=Object.freeze({pulseHz,seconds:duration,frames,startFrame:cycleFrames,endFrame:cycleFrames+frames,startCycles:cycleCycles});cycleFrames+=frames;cycleCycles+=pulseHz*frames/sampleRate;seconds+=duration;return s;});
 const plan=Object.freeze({version:1,audioProfile:id,sampleRate,repeat:profile.repeat,depth:profile.modulationDepthPercent/100,stages:Object.freeze(stages),seconds,cycleFrames,cycleSeconds:cycleFrames/sampleRate,cycleCycles});plans.add(plan);return plan;
}
export function pulseGainAtFrame(plan,frame){
 if(!plans.has(plan)||!Number.isInteger(frame)||frame<0||frame>86400*plan.sampleRate)throw new Error('Pulsposition außerhalb des Auftragsbudgets.');
 if(!plan.repeat&&frame>=plan.cycleFrames)return 0;
 if(plan.depth===0)return 1;
 const cycle=Math.floor(frame/plan.cycleFrames),local=frame%plan.cycleFrames,stage=plan.stages.find(s=>local<s.endFrame);
 // Quantized stage lengths and completed cycles retain phase at every boundary.
 const cycles=cycle*plan.cycleCycles+stage.startCycles+stage.pulseHz*(local-stage.startFrame)/plan.sampleRate;
 const phase=cycles-Math.floor(cycles);
 return (1-plan.depth)+plan.depth*(.5-.5*Math.cos(2*Math.PI*phase));
}
