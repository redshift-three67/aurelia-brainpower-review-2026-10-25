/** Fixed signal planning only; never maps analytical scores or consumes job entropy. */
export const FIXED_AUDIO_PROFILES = Object.freeze({
 'fixed-432': Object.freeze([432]),
 'fixed-528': Object.freeze([528]),
 'fixed-42962': Object.freeze([429.62]),
 'solfeggio-9': Object.freeze([174,285,396,417,528,639,741,852,963]),
});

export function planFixedAudio(profile, actualSampleRate) {
 if(!profile || typeof profile !== 'object' || Array.isArray(profile) ||
    Object.keys(profile).sort().join(',') !== 'id,repeat,stageSeconds')
  throw new Error('Audioprofil ist ungültig.');
 const {id,stageSeconds,repeat}=profile;
 if(typeof id !== 'string' || !Object.hasOwn(FIXED_AUDIO_PROFILES,id))
  throw new Error('Audioprofil ist nicht verfügbar.');
 if(!Number.isInteger(stageSeconds) || stageSeconds<1 || stageSeconds>600)
  throw new Error('Dauer je Frequenz: 1 bis 600 ganze Sekunden.');
 if(typeof repeat !== 'boolean')throw new Error('Wiederholung muss ausdrücklich gewählt werden.');
 if(!Number.isFinite(actualSampleRate) || actualSampleRate<=0)
  throw new Error('Die tatsächliche Audio-Samplerate ist nicht verfügbar.');
 const frequencies=FIXED_AUDIO_PROFILES[id];
 if(frequencies.some(hz=>hz>actualSampleRate*.45))
  throw new Error('Eine Frequenz überschreitet die Grenze dieses Audiogeräts.');
 const stageFrames=Math.round(stageSeconds*actualSampleRate);
 const cycleFrames=stageFrames*frequencies.length;
 if(!Number.isSafeInteger(stageFrames)||!Number.isSafeInteger(cycleFrames))
  throw new Error('Audiolaufzeit überschreitet die präzise Planungsgrenze.');
 return Object.freeze({version:1,id,frequencies,stageSeconds,stageFrames,cycleFrames,sampleRate:actualSampleRate,repeat});
}