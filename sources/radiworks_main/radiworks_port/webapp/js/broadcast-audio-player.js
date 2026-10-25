import { planFixedAudio } from './broadcast-audio-profile.js';
import { isPulseProfile, planPinkPulse } from './pink-pulse-profile.js';
// Presentation only: no analysis entropy, scores or broadcast decisions enter this player.
const TEST_TONE=Symbol("local-audio-test");
// At master <= .2: two validated noise voices (PCM <= 1) * 2 + six tone voices * 1/8 => peak <= .95 per channel.
const MAX_VOICES=8, VOICE_GAIN=1/MAX_VOICES, NOISE_GAIN=2, FADE=.02, LOOK_AHEAD=.75;
export class BroadcastAudioPlayer {
 constructor({contextFactory=()=>new (window.AudioContext||window.webkitAudioContext)(),workerFactory=()=>new Worker(new URL("./pink-worker.js",import.meta.url),{type:"module"}),setTimer=(...args)=>setTimeout(...args),clearTimer=id=>clearTimeout(id),onStatus=()=>{}}={}) {
  Object.assign(this,{contextFactory,workerFactory,setTimer,clearTimer,onStatus});this.ctx=null;this.master=null;this.enabled=false;this.generation=0;this.timer=null;this.voices=new Set();this.jobs=new Map();this.seen=new Set();this.level=.1;this.closing=null;this.blockedContext=null;
 }
 get voiceCount(){return this.voices.size;}
 get sampleRate(){return this.ctx?.sampleRate??null;}
 status(text){this.onStatus(text);}
 async activate(){
  if(this.enabled)return;const ticket=++this.generation;
  if(this.closing)await this.closing;if(ticket!==this.generation)return;if(this.blockedContext)throw new Error("Audiogerät konnte nicht geschlossen werden. Browser neu laden oder Audio-Stopp erneut prüfen.");
  const ctx=this.contextFactory();this.ctx=ctx;
  try {await ctx.resume();if(ticket!==this.generation){await ctx.close();return;}
   if(ctx.state!=='running')throw new Error('Audiogerät ist nicht aktiv.');
   this.master=ctx.createGain();this.master.gain.setValueAtTime(this.level,ctx.currentTime);this.master.connect(ctx.destination);this.enabled=true;this.seen.clear();this.status(`Audio bewusst aktiviert · ${ctx.sampleRate} Hz Samplerate.`);this.schedule();
  }catch(error){if(this.ctx===ctx){this.enabled=false;this.ctx=null;this.master=null;}await ctx.close().catch(()=>{});throw error;}
 }
 setLevel(value){if(!Number.isFinite(value)||value<0||value>.2)throw new Error('Audiostärke: 0 bis 20 %.');this.level=value;if(this.enabled)this.master.gain.linearRampToValueAtTime(value,this.ctx.currentTime+FADE);}
 schedule(){if(this.timer!==null||!this.enabled)return;this.timer=this.setTimer(()=>{this.timer=null;this.pump();this.schedule();},100);}
 release(voice){if(!this.voices.delete(voice))return;if(voice.worker){voice.worker.onmessage=null;voice.worker.onerror=null;voice.worker.terminate();}for(const node of voice.nodes){try{node.disconnect();}catch{}}}
 stopVoice(voice,soft=false){
  if(voice.worker){voice.worker.onmessage=null;voice.worker.onerror=null;voice.worker.terminate();}
  if(soft&&this.ctx?.state==='running'&&voice.gain){const now=this.ctx.currentTime;voice.retired=true;voice.end=now+FADE;voice.gain.gain.cancelScheduledValues(now);voice.gain.gain.setValueAtTime(voice.gain.gain.value??VOICE_GAIN,now);voice.gain.gain.linearRampToValueAtTime(0,voice.end);for(const source of voice.sources){try{source.stop(voice.end);}catch{}}return;}
  for(const source of voice.sources){try{source.stop(this.ctx?.currentTime??0);}catch{}}this.release(voice);
 }
 stopJob(id){this.jobs.delete(id);for(const v of [...this.voices])if(v.job===id)this.stopVoice(v,true);}
 async stopAll(){
  ++this.generation;this.enabled=false;if(this.timer!==null)this.clearTimer(this.timer);this.timer=null;
  if(this.closing)return this.closing;
  const ctx=this.ctx||this.blockedContext,master=this.master;this.jobs.clear();this.seen.clear();this.ctx=null;this.master=null;
  if(!ctx){this.status('Audio aus. Broadcast-Aufträge laufen unabhängig weiter.');return;}
  const closing=Promise.resolve().then(async()=>{try{
   if(master&&ctx.state==='running'){master.gain.cancelScheduledValues(ctx.currentTime);master.gain.setValueAtTime(master.gain.value??this.level,ctx.currentTime);master.gain.linearRampToValueAtTime(0,ctx.currentTime+FADE);await new Promise(resolve=>setTimeout(resolve,30));}
   for(const v of [...this.voices])this.stopVoice(v);await ctx.close();this.blockedContext=null;
   if(!this.enabled)this.status('Audio aus. Broadcast-Aufträge laufen unabhängig weiter.');
  }catch(error){this.blockedContext=ctx;throw error;}finally{if(this.closing===closing)this.closing=null;}});
  this.closing=closing;return closing;
 }
 validateFrequency(hz){if(!Number.isFinite(hz)||hz<=0||hz>this.ctx.sampleRate*.45)throw new Error('Frequenz liegt außerhalb der Grenze dieses Audiogeräts.');}
 tone(job,hz,start,end,volume=1,channel=null){
  if(this.voices.size>=MAX_VOICES)return false;
  const ctx=this.ctx,source=ctx.createOscillator(),gain=ctx.createGain();source.frequency.setValueAtTime(hz,start);
  const duration=end-start,fade=Math.min(FADE,duration/2),amp=VOICE_GAIN*volume;
  gain.gain.setValueAtTime(0,start);gain.gain.linearRampToValueAtTime(amp,start+fade);gain.gain.setValueAtTime(amp,end-fade);gain.gain.linearRampToValueAtTime(0,end);
  source.connect(gain);const nodes=[source,gain];if(channel!==null){const merger=ctx.createChannelMerger(2);gain.connect(merger,0,channel);merger.connect(this.master);nodes.push(merger);}else gain.connect(this.master);
  const voice={job,sources:[source],nodes,gain,end};this.voices.add(voice);source.onended=()=>this.release(voice);
  try{source.start(start);source.stop(end);}catch(error){this.stopVoice(voice);throw error;}return true;
 }
 playTestTone(){
  if(!this.enabled){this.status('Testton nicht gestartet: Audio zuerst bewusst aktivieren.');return false;}
  if(this.level===0){this.status('Testton bleibt stumm: Audiostärke steht auf 0 %.');return false;}
  if([...this.voices].some(v=>v.job===TEST_TONE)){this.status('Der zweisekündige Testton läuft bereits.');return false;}
  if(this.voices.size>=MAX_VOICES){this.status('Testton nicht gestartet: Alle acht Audiostimmen sind belegt.');return false;}
  this.validateFrequency(432);const start=this.ctx.currentTime+.02;
  const started=this.tone(TEST_TONE,432,start,start+2);
  if(started)this.status(`Testton 432 Hz · 2 Sekunden · Audiostärke ${Math.round(this.level*100)} % · ${this.ctx.sampleRate} Hz Samplerate. Hörbarkeit bitte selbst prüfen.`);
  return started;
 }
 playOriginal(job,params){
  if(!this.enabled)return false;this.validateFrequency(params?.left_freq);this.validateFrequency(params?.right_freq);
  if(!Number.isFinite(params.volume)||params.volume<0||params.volume>1)throw new Error('Original-Audiopegel ist ungültig.');
  if(this.voices.size+2>MAX_VOICES){this.status('Audio-Stimmengrenze erreicht; dieser Ereigniston wurde ausgelassen.');return false;}
  const start=this.ctx.currentTime+.02,end=start+3;this.tone(job,params.left_freq,start,end,params.volume,0);this.tone(job,params.right_freq,start,end,params.volume,1);return true;
 }
 startProfile(id,profile,seconds,elapsed=0){
  if(!this.enabled||this.seen.has(id))return false;
  if(typeof id!=='string'||!id||!Number.isFinite(seconds)||seconds<=0||!Number.isFinite(elapsed)||elapsed<0||elapsed>=seconds)throw new Error('Audio-Auftragsdauer ist ungültig.');
  const plan=planFixedAudio(profile,this.ctx.sampleRate);const cycle=plan.stageSeconds*plan.frequencies.length;
  if(this.seen.size>=512){this.status('Audio-Sitzungsgrenze erreicht. Audio bitte bewusst aus- und erneut einschalten.');return false;}
  this.seen.add(id);if(!plan.repeat&&elapsed>=cycle)return false;
  const now=this.ctx.currentTime+.02,index=Math.floor(elapsed/plan.stageSeconds);
  const job={id,plan,anchor:now-elapsed,end:now+seconds-elapsed,index,next:now,first:true};this.jobs.set(id,job);this.pump();return true;
 }
 startPink(id,profile,seconds,elapsed,seed){
  if(!this.enabled||this.seen.has(id))return false;
  if(typeof id!=='string'||!id||!Number.isFinite(seconds)||seconds<=0||seconds>86400||!Number.isFinite(elapsed)||elapsed<0||elapsed>=seconds||!Number.isInteger(profile.stageSeconds)||profile.stageSeconds<1||profile.stageSeconds>600||typeof profile.repeat!=='boolean'||typeof seed!=='string'||!seed||seed.length>256||this.ctx.sampleRate<8000||this.ctx.sampleRate>192000)throw new Error('Rauschprofil oder Geräte-Samplerate ist ungültig.');
  if(this.voices.size>=MAX_VOICES||[...this.voices].filter(v=>v.worker).length>=2||this.seen.size>=512){this.status('Rausch-Stimmengrenze erreicht (maximal zwei). Auftrag bleibt stumm.');return false;}
  const pulse=isPulseProfile(profile.audioProfile)?planPinkPulse(profile,this.ctx.sampleRate):null;
  this.seen.add(id);const remaining=Math.min(seconds-elapsed,profile.repeat?seconds-elapsed:Math.max(0,(pulse?.cycleSeconds??profile.stageSeconds)-elapsed));if(remaining<=0)return false;const ctx=this.ctx,gain=ctx.createGain(),end=ctx.currentTime+remaining;
  const worker=this.workerFactory(),voice={job:id,worker,nodes:[gain],sources:new Set(),buffers:new Map(),gain,end,pulse,anchor:ctx.currentTime-elapsed,frameOrigin:null,next:null,ready:false,pending:false,sequence:0,requestedAt:performance.now(),audioStarted:false};
  gain.gain.setValueAtTime(0,ctx.currentTime);gain.connect(this.master);this.voices.add(voice);
  const fail=message=>{this.stopVoice(voice);this.status(`Rauschsignal angehalten: ${message}`);};
  worker.onerror=()=>fail('Browserworker konnte nicht ausgeführt werden.');
  worker.onmessage=event=>{
   if(!this.enabled||this.ctx!==ctx||!this.voices.has(voice))return;
   try{const m=event.data;
    if(m?.type==='error')throw new Error('Numerischer Rauschblock konnte nicht erzeugt werden.');
    if(m?.type==='ready'&&!voice.ready){voice.ready=true;voice.next=ctx.currentTime+.1;voice.pending=false;if(voice.next>=voice.end){this.stopVoice(voice);return;}if(voice.pulse)voice.frameOrigin=Math.round((voice.next-voice.anchor)*ctx.sampleRate);this.requestPink(voice);return;}
    if(m?.type!=='chunk'||!voice.pending||m.sequence!==voice.sequence||!(m.samples instanceof Float32Array)||m.samples.length!==32768||!m.samples.every(v=>Number.isFinite(v)&&Math.abs(v)<=1))throw new Error('Rauschblock oder Reihenfolge ungültig.');
    voice.pending=false;voice.sequence++;
    if(voice.next<ctx.currentTime-.02)throw new Error('Browserpause: kein automatisches Aufholen.');
    const frames=Math.min(m.samples.length,Math.floor((end-voice.next)*ctx.sampleRate));if(frames<=0){this.stopVoice(voice);return;}
    const buffer=ctx.createBuffer(1,frames,ctx.sampleRate);buffer.copyToChannel(m.samples.subarray(0,frames),0);
    const source=ctx.createBufferSource();source.buffer=buffer;source.connect(gain);const start=voice.next,until=start+frames/ctx.sampleRate;if(!voice.audioStarted){const fade=Math.min(FADE,(end-start)/2);gain.gain.setValueAtTime(0,start);gain.gain.linearRampToValueAtTime(NOISE_GAIN,start+fade);gain.gain.setValueAtTime(NOISE_GAIN,end-fade);gain.gain.linearRampToValueAtTime(0,end);voice.audioStarted=true;}voice.sources.add(source);voice.buffers.set(source,until);source.onended=()=>{source.disconnect();voice.sources.delete(source);voice.buffers.delete(source);};source.start(start);source.stop(until);voice.next=until;
    this.requestPink(voice);
   }catch(error){fail(error.message);}
  };
  const init={type:'init',sampleRate:ctx.sampleRate,seed};if(pulse)init.pulseProfile={audioProfile:profile.audioProfile,stageSeconds:profile.stageSeconds,repeat:profile.repeat,modulationDepthPercent:profile.modulationDepthPercent};worker.postMessage(init);return true;
 }
 requestPink(voice){
  if(!this.voices.has(voice)||!voice.ready||voice.pending||voice.buffers.size>=2||voice.next>=voice.end)return;
  voice.pending=true;voice.requestedAt=performance.now();const request={type:'chunk',sequence:voice.sequence,frames:32768};if(voice.pulse)request.startFrame=voice.frameOrigin+voice.sequence*32768;voice.worker.postMessage(request);
 }
 pump(){
  if(!this.enabled)return;
  if(this.ctx.state!=='running'){this.status('Audiogerät unterbrochen. Audio erneut bewusst aktivieren.');void this.stopAll().catch(e=>this.status(e.message));return;}
  const now=this.ctx.currentTime;
  for(const voice of [...this.voices]){
   if(voice.end<=now){this.release(voice);continue;}
   if(voice.worker&&!voice.retired){for(const [source,until]of voice.buffers)if(until<=now){source.disconnect();voice.sources.delete(source);voice.buffers.delete(source);}
    if((!voice.ready||voice.pending)&&performance.now()-voice.requestedAt>5000){this.stopVoice(voice);this.status('Rauschworker antwortet nicht; Audio dieses Auftrags angehalten.');continue;}
    this.requestPink(voice);
   }
  }
  for(const job of [...this.jobs.values()]){
   if(job.end<=now){this.stopJob(job.id);continue;}
   if(job.next<now-.25){this.stopJob(job.id);this.status('Audiofolge wegen einer Browserpause angehalten. Bewusst neu aktivieren.');continue;}
   while(job.next<now+LOOK_AHEAD){
    const p=job.plan;if(!p.repeat&&job.index>=p.frequencies.length){this.jobs.delete(job.id);break;}
    const end=Math.min(job.anchor+(job.index+1)*p.stageSeconds,job.end);
    if(end<=now){this.stopJob(job.id);break;}
    if(this.voices.size>=MAX_VOICES){this.stopJob(job.id);this.status('Audio-Stimmengrenze erreicht; diese Folge wurde angehalten.');break;}
    const start=Math.max(now,job.next);this.tone(job.id,p.frequencies[job.index%p.frequencies.length],start,end);
    job.index++;job.next=job.anchor+job.index*p.stageSeconds;job.first=false;
    if(job.next>=job.end){this.jobs.delete(job.id);break;}
   }
  }
 }
}
