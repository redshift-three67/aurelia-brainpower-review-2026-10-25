import {planFixedAudio} from './broadcast-audio-profile.js';
import {isPulseProfile,planPinkPulse} from './pink-pulse-profile.js';
const labels=Object.freeze({'original':'Original-Ereignistöne','off':'Audio aus','fixed-432':'432 Hz','fixed-528':'528 Hz','fixed-42962':'429,62 Hz','solfeggio-9':'Solfeggio-Folge','pink':'Rosa Rauschen','pink-pulse-v1':'Rosa Rauschen · gleichmäßige Pulse','pink-phi-v1':'Rosa Rauschen · Phi','pink-fibonacci-v1':'Rosa Rauschen · Fibonacci'});
export const audioProfileLabel=id=>labels[id]??'Profil nicht prüfbar';
// Reports only frozen assignments; never claims a physical sound or starts/replays audio.
export function describeAudioAssignment(rows,originalEnabled,sampleRate=48000){
 if(!rows.length)return 'Kein aktiver Broadcast. Der Testton ist auch ohne Broadcast nutzbar.';
 const reasons=new Map();
 for(const row of rows){
  const p=row.profile??{audioProfile:'original'},id=p.audioProfile;let reason;
  if(id==='original')reason=originalEnabled?'Original-Ereignistöne: erst beim nächsten Resonanzereignis.':'Original-Ereignistöne: Toneinstellung ausgeschaltet.';
  else if(id==='off')reason='Audio aus: im Broadcastprofil ausgewählt.';
  else try{
   if(!Number.isFinite(row.elapsed)||row.elapsed<0||!Number.isFinite(row.seconds)||row.seconds<=0)throw Error('duration');
   const cycle=isPulseProfile(id)?planPinkPulse(p,sampleRate).cycleSeconds:id==='pink'?p.stageSeconds:planFixedAudio({id,stageSeconds:p.stageSeconds,repeat:p.repeat},sampleRate).frequencies.length*p.stageSeconds;
   if(!Number.isFinite(cycle)||cycle<=0||typeof p.repeat!=='boolean')throw Error('profile');
   reason=row.elapsed>=row.seconds?'Broadcast abgeschlossen.':!p.repeat&&row.elapsed>=cycle?`${audioProfileLabel(id)}: Einmalfolge beendet; ein laufender Broadcast verlängert sie nicht.`:`${audioProfileLabel(id)}: zugeordnet${p.repeat?' · Wiederholung':''}.`;
  }catch{reason='Profil oder Dauer nicht prüfbar; keine Wiedergabe zugesagt.';}
  reasons.set(reason,(reasons.get(reason)??0)+1);
 }
 return [...reasons].map(([reason,count])=>`${count} × ${reason}`).join(' ')+' Gespeicherte Profiländerungen gelten erst für neue Broadcasts.';
}
