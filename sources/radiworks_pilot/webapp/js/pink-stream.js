// Numerical port of user-supplied Audigenerator_v1 pink-noise v0.8. Float64 FFT, Float32 output.
/**
 * Vertrag der Rosa-Rauschen-Synthese v0.8.
 * Keine Pegel-Nachmessung: der Crest-Abstand ist eine Konstante, kein gemessener Peak.
 */

export const PINK_FFT_SIZE = 8192;

export const PINK_HOP_FRAMES = 4096;

/** Bandgrenze, dieselbe 45-%-Decke wie der übrige Generator. */
export const PINK_BAND_LIMIT_FACTOR = 0.45;

/**
 * Fester Abstand unter dem Zielpegel.
 * Der Zielpegel skaliert den Block-Effektivwert; 12 dB bleiben für die Spitzen frei.
 * Der Puffer wird dafür nicht gemessen und nicht nachträglich normalisiert.
 */
export const PINK_CREST_GUARD_DB = 12;

export const PINK_NOISE_POLICY_TEXT =
  "Rosa Rauschen wird als deterministische, bandbegrenzte FFT-Spektralsynthese mit dem gespeicherten Seed gerendert. Die Dateilänge bleibt die Preset-Gesamtdauer.";

export const PINK_SAMPLE_RANGE_MESSAGE =
  "Der Samplewert liegt außerhalb von [−1, 1]. Der Render wurde nicht still begrenzt.";

export function fnv1a32(text) {
  let hash = 0x811c9dc5;
  for (let index = 0; index < text.length; index += 1) {
    hash ^= text.charCodeAt(index);
    hash = Math.imul(hash, 0x01000193);
  }
  return hash >>> 0;
}

export function pinkNoiseSeedToken(seed) {
  return fnv1a32(seed).toString(16).padStart(8, "0");
}

export function mulberry32(seed) {
  let state = seed >>> 0;
  return () => {
    state = (state + 0x6d2b79f5) >>> 0;
    let value = state;
    value = Math.imul(value ^ (value >>> 15), value | 1);
    value ^= value + Math.imul(value ^ (value >>> 7), value | 61);
    return ((value ^ (value >>> 14)) >>> 0) / 4294967296;
  };
}

export function pinkHighestBin() {
  return Math.floor(PINK_BAND_LIMIT_FACTOR * PINK_FFT_SIZE);
}

/** Periodisches Hann-Fenster. Bei 50 % Überlappung gilt w[n] + w[n + Hop] = 1. */
export function pinkHann(index, size) {
  return 0.5 * (1 - Math.cos((2 * Math.PI * index) / size));
}

/**
 * Exaktes mittleres Quadrat eines ungefalteten IFFT-Blocks.
 * |X[k]| = 1/sqrt(f) hängt nicht von der Phase ab.
 */
export function pinkBlockMeanSquare(sampleRateHz) {
  const size = PINK_FFT_SIZE;
  const highest = pinkHighestBin();
  let harmonic = 0;
  for (let bin = 1; bin <= highest; bin += 1) harmonic += 1 / bin;
  return (2 * harmonic) / (size * sampleRateHz);
}

export function writePinkSpectrum(
  real,
  imag,
  sampleRateHz,
  random,
) {
  real.fill(0);
  imag.fill(0);
  const highest = pinkHighestBin();
  for (let bin = 1; bin <= highest; bin += 1) {
    const frequency = (bin * sampleRateHz) / PINK_FFT_SIZE;
    if (frequency > sampleRateHz * PINK_BAND_LIMIT_FACTOR) continue;
    const magnitude = 1 / Math.sqrt(frequency);
    const phase = random() * 2 * Math.PI;
    const binReal = magnitude * Math.cos(phase);
    const binImag = magnitude * Math.sin(phase);
    real[bin] = binReal;
    imag[bin] = binImag;
    real[PINK_FFT_SIZE - bin] = binReal;
    imag[PINK_FFT_SIZE - bin] = -binImag;
  }
}

export function fftRadix2(real, imag, inverse) {
  const size = real.length;
  if (imag.length !== size || size < 2 || (size & (size - 1)) !== 0) {
    throw new Error("Die FFT-Länge muss eine Zweierpotenz sein.");
  }
  for (let i = 1, j = 0; i < size; i += 1) {
    let bit = size >> 1;
    for (; (j & bit) !== 0; bit >>= 1) j ^= bit;
    j ^= bit;
    if (i < j) {
      const left = real[i] ?? 0;
      real[i] = real[j] ?? 0;
      real[j] = left;
      const leftImag = imag[i] ?? 0;
      imag[i] = imag[j] ?? 0;
      imag[j] = leftImag;
    }
  }
  const sign = inverse ? 1 : -1;
  for (let length = 2; length <= size; length <<= 1) {
    const angle = (sign * 2 * Math.PI) / length;
    const stepReal = Math.cos(angle);
    const stepImag = Math.sin(angle);
    const half = length >> 1;
    for (let start = 0; start < size; start += length) {
      let twiddleReal = 1;
      let twiddleImag = 0;
      for (let offset = 0; offset < half; offset += 1) {
        const evenReal = real[start + offset] ?? 0;
        const evenImag = imag[start + offset] ?? 0;
        const oddReal = real[start + offset + half] ?? 0;
        const oddImag = imag[start + offset + half] ?? 0;
        const rotatedReal = oddReal * twiddleReal - oddImag * twiddleImag;
        const rotatedImag = oddReal * twiddleImag + oddImag * twiddleReal;
        real[start + offset] = evenReal + rotatedReal;
        imag[start + offset] = evenImag + rotatedImag;
        real[start + offset + half] = evenReal - rotatedReal;
        imag[start + offset + half] = evenImag - rotatedImag;
        const nextReal = twiddleReal * stepReal - twiddleImag * stepImag;
        twiddleImag = twiddleReal * stepImag + twiddleImag * stepReal;
        twiddleReal = nextReal;
      }
    }
  }
  if (inverse) {
    for (let index = 0; index < size; index += 1) {
      real[index] = (real[index] ?? 0) / size;
      imag[index] = (imag[index] ?? 0) / size;
    }
  }
}


export class PinkStream {
 constructor(sampleRate,seed,{bounded=false}={}){
  if(!Number.isFinite(sampleRate)||sampleRate<8000||sampleRate>192000||typeof seed!=='string'||!seed||seed.length>256)throw new Error('Rauschquelle benötigt Geräte-Samplerate und eigenen Audioseed.');
  this.sampleRate=sampleRate;this.random=mulberry32(fnv1a32(seed));this.real=new Float64Array(PINK_FFT_SIZE);this.imag=new Float64Array(PINK_FFT_SIZE);this.tail=new Float64Array(PINK_HOP_FRAMES);this.pending=null;this.offset=0;
  this.gain=Math.pow(10,-PINK_CREST_GUARD_DB/20)/Math.sqrt(pinkBlockMeanSquare(sampleRate));
  // Live gain is constant: IFFT triangle bound, preserved by nonnegative Hann overlap.
  if(bounded){let peakBound=0;for(let k=1;k<=pinkHighestBin();k++)peakBound+=2/PINK_FFT_SIZE/Math.sqrt(k*sampleRate/PINK_FFT_SIZE);this.gain=Math.min(this.gain,.95/peakBound);}
  this.block();for(let i=0;i<PINK_HOP_FRAMES;i++)this.tail[i]=this.real[i+PINK_HOP_FRAMES]*pinkHann(i+PINK_HOP_FRAMES,PINK_FFT_SIZE);
 }
 block(){writePinkSpectrum(this.real,this.imag,this.sampleRate,this.random);fftRadix2(this.real,this.imag,true);}
 hop(){this.block();const output=new Float32Array(PINK_HOP_FRAMES);for(let i=0;i<PINK_HOP_FRAMES;i++){const value=this.gain*(this.tail[i]+this.real[i]*pinkHann(i,PINK_FFT_SIZE));if(!Number.isFinite(value)||Math.abs(value)>1)throw new Error(PINK_SAMPLE_RANGE_MESSAGE);output[i]=value;this.tail[i]=this.real[i+PINK_HOP_FRAMES]*pinkHann(i+PINK_HOP_FRAMES,PINK_FFT_SIZE);}return output;}
 chunk(frames){if(!Number.isInteger(frames)||frames<1||frames>65536)throw new Error('Rauschblock überschreitet die feste Speichergrenze.');const output=new Float32Array(frames);let written=0;while(written<frames){if(!this.pending||this.offset===this.pending.length){this.pending=this.hop();this.offset=0;}const n=Math.min(frames-written,this.pending.length-this.offset);output.set(this.pending.subarray(this.offset,this.offset+n),written);written+=n;this.offset+=n;}return output;}
}
