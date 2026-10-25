import { isPulseProfile, pulseBaseLimit } from './pink-pulse-profile.js';
const AUDIO_IDS=new Set(['original','off','fixed-432','fixed-528','fixed-42962','solfeggio-9','pink','pink-pulse-v1','pink-phi-v1','pink-fibonacci-v1']);
function validateDraft(d){
 if(isPulseProfile(d.audioProfile)&&(!Number.isInteger(d.modulationDepthPercent)||d.modulationDepthPercent<0||d.modulationDepthPercent>100))throw new Error('Modulationstiefe: ganze Zahl zwischen 0 und 100 %.');
 if(!AUDIO_IDS.has(d.audioProfile)||!Number.isInteger(d.stageSeconds)||d.stageSeconds<1||d.stageSeconds>(isPulseProfile(d.audioProfile)?pulseBaseLimit(d.audioProfile):600)||typeof d.repeat!=='boolean'||!Array.isArray(d.images)||d.images.length>5||new Set(d.images).size!==d.images.length||d.images.some(x=>typeof x!=='string'||!/^[0-9a-f]{64}$/.test(x)))throw new Error('Medienprofil ist ungültig: maximal fünf verschiedene Bilder und 1–600 Sekunden je Audiostufe.');
}
export class PresentationEditor {
 constructor({load,save}){this.loadApi=load;this.saveApi=save;this.epoch=0;this.invalidate();}
 invalidate(){this.epoch++;this.binding=null;this._profile=null;this._draft=null;this.dirty=false;this.busy=false;}
 invalidatePending(){this.epoch++;this.busy=false;this.binding=null;}
 get profile(){return this._profile?structuredClone(this._profile):null;}
 get draft(){return this._draft?structuredClone(this._draft):null;}
 apply(p){if(!p||!Number.isInteger(p.version)||p.version<0)throw new Error('Profilversion fehlt.');validateDraft(p);this._profile=structuredClone(p);this._draft={audioProfile:p.audioProfile,stageSeconds:p.stageSeconds,repeat:p.repeat,images:[...p.images]};if(isPulseProfile(p.audioProfile))this._draft.modulationDepthPercent=p.modulationDepthPercent;this.dirty=false;}
 async load(binding,discard=false){
  if(this.dirty&&!discard)throw new Error('Ungespeicherte Medienänderungen vorhanden. Bewusst neu laden oder speichern.');
  if(!binding||!/^[0-9a-f]{64}$/.test(binding.ref)||!Number.isInteger(binding.contextVersion)||binding.contextVersion<1)throw new Error('Bitte zuerst einen Fall speichern oder laden.');
  const ticket=++this.epoch;this.busy=true;
  try{const result=await this.loadApi(binding);if(ticket!==this.epoch)return false;this.apply(result.profile);this.binding={...binding};return true;}
  finally{if(ticket===this.epoch)this.busy=false;}
 }
 edit(changes){if(this.busy||!this.binding||!this._draft)throw new Error('Profil ist noch nicht geladen.');const draft={...this._draft,...changes};if(!isPulseProfile(draft.audioProfile))delete draft.modulationDepthPercent;validateDraft(draft);this._draft=structuredClone(draft);this.dirty=true;}
 async save(){
  if(this.busy||!this.binding||!this._draft)throw new Error('Profil ist noch nicht geladen.');const ticket=++this.epoch,d=this.draft;this.busy=true;
  const body={expected_case_ref:this.binding.ref,expected_context_version:this.binding.contextVersion,expected_profile_version:this._profile.version,audio_profile:d.audioProfile,stage_seconds:d.stageSeconds,repeat:d.repeat,images:d.images};if(isPulseProfile(d.audioProfile))body.modulation_depth_percent=d.modulationDepthPercent;
  try{const result=await this.saveApi(body);if(ticket!==this.epoch)return false;this.apply(result.profile);return true;}
  finally{if(ticket===this.epoch)this.busy=false;}
 }
}
