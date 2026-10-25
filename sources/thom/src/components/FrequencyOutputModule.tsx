/**
 * Frequency Output Module
 * Unterstützt verschiedene Therapie-Modi für Frequenzausgabe
 *
 * Modi:
 * - Bipolar-Resonanz: Bipolare Wellenformen nach dem Prinzip gegenpoliger Schwingungen
 * - Harmonikale Modulation: Frequenztherapie mit harmonischen Obertönen und Modulationen
 */
import { useState, useCallback, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Play,
  Square,
  Volume2,
  VolumeX,
  Radio,
  Waves,
  Settings2,
  Zap,
  Activity,
  Check,
  Timer,
  BarChart3,
  Search
} from 'lucide-react';
import { SpectrumVisualizer } from './SpectrumVisualizer';
import { Button } from '@/components/ui/button';
import { Slider } from '@/components/ui/slider';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { toast } from 'sonner';
import { cn } from '@/lib/utils';
import type { FrequencyOutput } from '@/types/hardware';
import { AcupuncturePointSearch } from './AcupuncturePointSearch';

type WaveformType = 'sine' | 'square' | 'triangle' | 'sawtooth' | 'bipolar_sine' | 'harmonic_complex';

// Therapie-Modi (ohne echte Markenbezeichnungen)
type TherapyMode = 'bipolar_resonance' | 'harmonic_modulation';

interface TherapyModeConfig {
  id: TherapyMode;
  name: string;
  description: string;
  icon: typeof Waves;
  waveforms: WaveformType[];
  defaultWaveform: WaveformType;
  supportsModulation: boolean;
  bipolar: boolean;
  harmonics: number[];
}

const THERAPY_MODES: TherapyModeConfig[] = [
  {
    id: 'bipolar_resonance',
    name: 'Bipolar-Resonanz',
    description: 'Gegenphasige Schwingungen für tiefgreifende Regulation',
    icon: Radio,
    waveforms: ['bipolar_sine', 'square', 'triangle'],
    defaultWaveform: 'bipolar_sine',
    supportsModulation: false,
    bipolar: true,
    harmonics: [1],
  },
  {
    id: 'harmonic_modulation',
    name: 'Harmonikale Modulation',
    description: 'Mehrstufige Frequenztherapie mit Obertönen',
    icon: Waves,
    waveforms: ['harmonic_complex', 'sine', 'triangle'],
    defaultWaveform: 'harmonic_complex',
    supportsModulation: true,
    bipolar: false,
    harmonics: [1, 2, 3, 4, 5, 6, 7, 8],
  },
];

// Vordefinierte therapeutische Frequenzen
const THERAPEUTIC_FREQUENCIES = [
  { name: 'Schumann-Resonanz', frequency: 7.83, description: 'Erdresonanz' },
  { name: 'Alpha-Wellen', frequency: 10, description: 'Entspannung' },
  { name: 'Theta-Wellen', frequency: 6, description: 'Meditation' },
  { name: 'Detox-Frequenz', frequency: 727, description: 'Entgiftung' },
  { name: 'Immun-Stärkung', frequency: 880, description: 'Immunsystem' },
  { name: 'Befreiung', frequency: 396, description: 'Lösung von Blockaden' },
  { name: 'Regeneration', frequency: 528, description: 'Zellerneuerung' },
  { name: 'Harmonie', frequency: 639, description: 'Balance' },
];

interface FrequencyOutputModuleProps {
  onFrequencyChange?: (config: FrequencyOutput) => void;
}

// Helper: Map WaveformType to OscillatorType
const getOscillatorType = (wf: WaveformType): OscillatorType => {
  switch (wf) {
    case 'bipolar_sine':
    case 'harmonic_complex':
      return 'sine';
    default:
      return wf as OscillatorType;
  }
};

// AudioWorklet Processor Code
const WORKLET_CODE = `
class FreqProcessor extends AudioWorkletProcessor {
  constructor() {
    super();
    this.freq = 440; this.amp = 0.5; this.wf = 'sine'; this.phase = 0;
    this.harmonics = [1,0.5,0.25,0.125]; this.modFreq = 0; this.modDepth = 0; this.modPhase = 0;
    this.port.onmessage = (e) => {
      const d = e.data;
      if (d.frequency !== undefined) this.freq = d.frequency;
      if (d.amplitude !== undefined) this.amp = d.amplitude;
      if (d.waveform !== undefined) this.wf = d.waveform;
      if (d.harmonics !== undefined) this.harmonics = d.harmonics;
      if (d.modFreq !== undefined) this.modFreq = d.modFreq;
      if (d.modDepth !== undefined) this.modDepth = d.modDepth;
    };
  }
  gen(p) {
    switch(this.wf) {
      case 'sine': return Math.sin(p*2*Math.PI);
      case 'square': return p<0.5?1:-1;
      case 'triangle': return 4*Math.abs(p-0.5)-1;
      case 'sawtooth': return 2*p-1;
      case 'bipolar_sine': return Math.sin(p*2*Math.PI)*Math.cos(p*Math.PI);
      case 'harmonic_complex': {
        let s=0;
        for(let i=0;i<this.harmonics.length;i++) s+=this.harmonics[i]*Math.sin(p*(i+1)*2*Math.PI);
        return s/this.harmonics.reduce((a,b)=>a+b,1);
      }
      default: return Math.sin(p*2*Math.PI);
    }
  }
  process(inputs,outputs) {
    const ch = outputs[0][0];
    if(!ch) return true;
    for(let i=0;i<ch.length;i++){
      let mod=0;
      if(this.modFreq>0&&this.modDepth>0){
        mod=Math.sin(this.modPhase*2*Math.PI)*this.modDepth*this.freq;
        this.modPhase+=this.modFreq/sampleRate;
        if(this.modPhase>=1)this.modPhase-=1;
      }
      ch[i]=this.gen(this.phase)*this.amp;
      this.phase+=(this.freq+mod)/sampleRate;
      if(this.phase>=1)this.phase-=1;
    }
    return true;
  }
}
registerProcessor('freq-gen',FreqProcessor);
`;

const FrequencyOutputModule = ({ onFrequencyChange }: FrequencyOutputModuleProps) => {
  // Therapy Mode
  const [therapyMode, setTherapyMode] = useState<TherapyMode>('bipolar_resonance');

  // Audio State
  const [isPlaying, setIsPlaying] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [frequency, setFrequency] = useState(7.83);
  const [amplitude, setAmplitude] = useState(0.5);
  const [waveform, setWaveform] = useState<WaveformType>('bipolar_sine');

  // Timer
  const [duration, setDuration] = useState(180);
  const [elapsedTime, setElapsedTime] = useState(0);
  const [isTimerEnabled, setIsTimerEnabled] = useState(true);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // Additional oscillators for bipolar/harmonic modes
  const oscillatorsRef = useRef<OscillatorNode[]>([]);

  // Modulation
  const [modulationEnabled, setModulationEnabled] = useState(false);
  const [modulationFreq, setModulationFreq] = useState(1);
  const [modulationDepth, setModulationDepth] = useState(0.3);

  // EM-Feld Output
  const [emOutputEnabled, setEmOutputEnabled] = useState(false);
  const [serialConnected, setSerialConnected] = useState(false);

  // WebAudio Refs
  const audioContextRef = useRef<AudioContext | null>(null);
  const oscillatorRef = useRef<OscillatorNode | null>(null);
  const gainNodeRef = useRef<GainNode | null>(null);
  const modulatorRef = useRef<OscillatorNode | null>(null);
  const modulationGainRef = useRef<GainNode | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const workletNodeRef = useRef<AudioWorkletNode | null>(null);
  const [workletReady, setWorkletReady] = useState(false);
  const [analyserNode, setAnalyserNode] = useState<AnalyserNode | null>(null);

  // Serial Port Ref
  const serialPortRef = useRef<SerialPort | null>(null);

  // Audio initialisieren (mit AudioWorklet + AnalyserNode)
  const initAudio = useCallback(async () => {
    if (!audioContextRef.current) {
      audioContextRef.current = new AudioContext({ sampleRate: 48000, latencyHint: 'interactive' });
    }
    const ctx = audioContextRef.current;

    // AnalyserNode erstellen
    if (!analyserRef.current) {
      const an = ctx.createAnalyser();
      an.fftSize = 2048;
      an.smoothingTimeConstant = 0.8;
      analyserRef.current = an;
      setAnalyserNode(an);
    }

    // AudioWorklet laden (einmalig)
    if (!workletReady) {
      try {
        const blob = new Blob([WORKLET_CODE], { type: 'application/javascript' });
        const url = URL.createObjectURL(blob);
        await ctx.audioWorklet.addModule(url);
        URL.revokeObjectURL(url);
        setWorkletReady(true);
        console.log('[FreqOutput] AudioWorklet geladen – sub-1ms Latenz aktiv');
      } catch (e) {
        console.warn('[FreqOutput] AudioWorklet Fallback:', e);
      }
    }

    return ctx;
  }, [workletReady]);

  // Current therapy mode config
  const currentModeConfig = THERAPY_MODES.find(m => m.id === therapyMode)!;

  // Audio stoppen
  const stopAudio = useCallback(() => {
    // WorkletNode stoppen
    if (workletNodeRef.current) {
      workletNodeRef.current.disconnect();
      workletNodeRef.current = null;
    }

    // Stop all oscillators
    oscillatorsRef.current.forEach(osc => {
      try { osc.stop(); osc.disconnect(); } catch (error) { void error; }
    });
    oscillatorsRef.current = [];

    try { oscillatorRef.current?.stop(); oscillatorRef.current?.disconnect(); } catch (error) { void error; }
    try { modulatorRef.current?.stop(); modulatorRef.current?.disconnect(); } catch (error) { void error; }

    oscillatorRef.current = null;
    modulatorRef.current = null;

    // Analyser trennen (aber nicht zerstören)
    if (analyserRef.current) {
      try { analyserRef.current.disconnect(); } catch (error) { void error; }
    }

    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }

    setIsPlaying(false);
  }, []);

  // Update waveform when therapy mode changes
  useEffect(() => {
    setWaveform(currentModeConfig.defaultWaveform);
    setModulationEnabled(currentModeConfig.supportsModulation);
  }, [therapyMode, currentModeConfig]);

  // Timer effect
  useEffect(() => {
    if (isPlaying && isTimerEnabled) {
      timerRef.current = setInterval(() => {
        setElapsedTime(prev => {
          if (prev >= duration) {
            stopAudio();
            toast.success('Harmonisierung abgeschlossen', {
              description: `${Math.floor(duration / 60)} Minuten @ ${frequency} Hz`
            });
            return 0;
          }
          return prev + 1;
        });
      }, 1000);
    }

    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    };
  }, [isPlaying, isTimerEnabled, duration, frequency, stopAudio]);

  // Format time helper
  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  // Fallback: Standard-Oszillatoren (wenn AudioWorklet nicht verfügbar)
  const startOscillatorFallback = useCallback((ctx: AudioContext, gain: GainNode) => {
    if (currentModeConfig.bipolar && waveform === 'bipolar_sine') {
      const osc1 = ctx.createOscillator();
      const osc2 = ctx.createOscillator();
      osc1.frequency.value = frequency;
      osc2.frequency.value = frequency;
      const gain1 = ctx.createGain();
      const gain2 = ctx.createGain();
      gain1.gain.value = 0.5;
      gain2.gain.value = -0.5;
      osc1.connect(gain1); osc2.connect(gain2);
      gain1.connect(gain); gain2.connect(gain);
      osc1.start(); osc2.start();
      oscillatorsRef.current = [osc1, osc2];
      oscillatorRef.current = osc1;
    } else if (waveform === 'harmonic_complex') {
      const oscs: OscillatorNode[] = [];
      currentModeConfig.harmonics.forEach((harmonic) => {
        const harmonicFreq = frequency * harmonic;
        if (harmonicFreq < 20000) {
          const osc = ctx.createOscillator();
          osc.frequency.value = harmonicFreq;
          osc.type = 'sine';
          const harmonicGain = ctx.createGain();
          harmonicGain.gain.value = (1 / (harmonic * 1.5)) * amplitude;
          osc.connect(harmonicGain);
          harmonicGain.connect(gain);
          osc.start();
          oscs.push(osc);
        }
      });
      oscillatorsRef.current = oscs;
      oscillatorRef.current = oscs[0] || null;
    } else {
      const osc = ctx.createOscillator();
      osc.type = getOscillatorType(waveform);
      osc.frequency.value = frequency;
      osc.connect(gain);
      osc.start();
      oscillatorRef.current = osc;
      oscillatorsRef.current = [osc];
    }

    if (modulationEnabled && currentModeConfig.supportsModulation) {
      const modulator = ctx.createOscillator();
      modulator.frequency.value = modulationFreq;
      modulatorRef.current = modulator;
      const modGain = ctx.createGain();
      modGain.gain.value = modulationDepth * amplitude;
      modulationGainRef.current = modGain;
      modulator.connect(modGain);
      modGain.connect(gain.gain);
      modulator.start();
    }
  }, [frequency, amplitude, waveform, modulationEnabled, modulationFreq, modulationDepth, currentModeConfig]);

  // Audio starten (AudioWorklet mit AnalyserNode)
  const startAudio = useCallback(async () => {
    const ctx = await initAudio();

    // Gain-Node für Amplitude
    const gain = ctx.createGain();
    gain.gain.value = isMuted ? 0 : amplitude;
    gainNodeRef.current = gain;

    // Audio-Kette: Source → Gain → Analyser → Destination
    const analyser = analyserRef.current!;
    gain.connect(analyser);
    analyser.connect(ctx.destination);

    // Versuche AudioWorklet, Fallback auf OscillatorNode
    if (workletReady) {
      try {
        const worklet = new AudioWorkletNode(ctx, 'freq-gen');
        worklet.connect(gain);
        worklet.port.postMessage({
          frequency,
          amplitude: 0.8, // Konstante Amplitude gemäß Audio-Engine-Spec
          waveform,
          harmonics: currentModeConfig.harmonics.map((h, i) => 1 / (h * 1.5)),
          modFreq: modulationEnabled ? modulationFreq : 0,
          modDepth: modulationEnabled ? modulationDepth : 0,
        });
        workletNodeRef.current = worklet;
        oscillatorsRef.current = [];
        oscillatorRef.current = null;
        console.log('[FreqOutput] AudioWorklet aktiv – Latenz:',
          Math.round((ctx.baseLatency || 0) * 1000), 'ms');
      } catch {
        console.warn('[FreqOutput] Worklet-Start fehlgeschlagen, nutze Oszillator-Fallback');
        startOscillatorFallback(ctx, gain);
      }
    } else {
      startOscillatorFallback(ctx, gain);
    }

    setIsPlaying(true);
    setElapsedTime(0);

    // Callback
    const config: FrequencyOutput = {
      type: emOutputEnabled ? 'dual' : 'audio',
      frequency,
      amplitude,
      waveform: getOscillatorType(waveform) as 'sine' | 'square' | 'triangle' | 'sawtooth',
      modulation: modulationEnabled ? {
        type: 'fm',
        frequency: modulationFreq,
        depth: modulationDepth,
      } : undefined,
    };
    onFrequencyChange?.(config);

    toast.success(`${currentModeConfig.name} gestartet`, {
      description: `${frequency} Hz • ${waveform}${workletReady ? ' • AudioWorklet' : ''}`
    });
  }, [frequency, amplitude, waveform, modulationEnabled, modulationFreq, modulationDepth, isMuted, emOutputEnabled, initAudio, onFrequencyChange, currentModeConfig, workletReady, startOscillatorFallback]);

  // Frequenz live aktualisieren (WorkletNode + Fallback)
  useEffect(() => {
    if (!isPlaying) return;
    if (workletNodeRef.current) {
      workletNodeRef.current.port.postMessage({ frequency });
    } else if (oscillatorRef.current) {
      oscillatorRef.current.frequency.setValueAtTime(
        frequency, audioContextRef.current?.currentTime || 0
      );
    }
  }, [frequency, isPlaying]);

  // Amplitude live aktualisieren
  useEffect(() => {
    if (gainNodeRef.current) {
      gainNodeRef.current.gain.setValueAtTime(
        isMuted ? 0 : amplitude,
        audioContextRef.current?.currentTime || 0
      );
    }
    if (workletNodeRef.current) {
      workletNodeRef.current.port.postMessage({ amplitude: isMuted ? 0 : 0.8 });
    }
  }, [amplitude, isMuted]);

  // Waveform aktualisieren
  useEffect(() => {
    if (!isPlaying) return;
    if (workletNodeRef.current) {
      workletNodeRef.current.port.postMessage({ waveform });
    } else if (oscillatorRef.current && waveform !== 'bipolar_sine' && waveform !== 'harmonic_complex') {
      oscillatorRef.current.type = getOscillatorType(waveform);
    }
  }, [waveform, isPlaying]);

  // Toggle Mute
  const toggleMute = useCallback(() => {
    setIsMuted(prev => !prev);
  }, []);

  // Serial verbinden (für EM-Feld-Generatoren)
  const connectSerial = useCallback(async () => {
    if (!('serial' in navigator)) {
      toast.error('WebSerial wird nicht unterstützt');
      return;
    }

    try {
      const port = await navigator.serial.requestPort();
      await port.open({ baudRate: 115200 });
      serialPortRef.current = port;
      setSerialConnected(true);
      toast.success('Serial-Port verbunden');
    } catch (error) {
      console.error('Serial connection error:', error);
      toast.error('Verbindung fehlgeschlagen');
    }
  }, []);

  // Serial trennen
  const disconnectSerial = useCallback(async () => {
    if (serialPortRef.current) {
      await serialPortRef.current.close();
      serialPortRef.current = null;
      setSerialConnected(false);
    }
  }, []);

  // Cleanup bei Unmount
  useEffect(() => {
    return () => {
      stopAudio();
      void disconnectSerial();
    };
  }, [stopAudio, disconnectSerial]);

  // Frequenz an Serial senden
  const sendFrequencyToSerial = useCallback(async (freq: number) => {
    if (!serialPortRef.current || !serialConnected) return;

    const encoder = new TextEncoder();
    const writer = serialPortRef.current.writable?.getWriter();

    if (writer) {
      const command = `FREQ:${freq.toFixed(2)}\n`;
      await writer.write(encoder.encode(command));
      writer.releaseLock();
    }
  }, [serialConnected]);

  // Frequenz an EM senden wenn aktiv
  useEffect(() => {
    if (emOutputEnabled && serialConnected && isPlaying) {
      sendFrequencyToSerial(frequency);
    }
  }, [frequency, emOutputEnabled, serialConnected, isPlaying, sendFrequencyToSerial]);

  // Preset auswählen
  const selectPreset = useCallback((preset: typeof THERAPEUTIC_FREQUENCIES[0]) => {
    setFrequency(preset.frequency);
    toast.info(`${preset.name}: ${preset.description}`);
  }, []);

  return (
    <section className="py-16 px-4 bg-gradient-to-b from-muted/20 to-background">
      <div className="container mx-auto max-w-6xl">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-12"
        >
          <h2 className="font-display text-3xl md:text-4xl text-foreground mb-4">
            Frequenz-<span className="text-gradient-primary">Output</span>
          </h2>
          <p className="text-muted-foreground max-w-2xl mx-auto">
            Audio- und elektromagnetische Frequenz-Harmonisierung
          </p>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Frequenz-Steuerung */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            className="lg:col-span-2 bg-card rounded-lg border border-border p-6 shadow-card"
          >
            <div className="flex items-center gap-3 mb-6">
              <Waves className="w-6 h-6 text-primary" />
              <h3 className="font-display text-xl text-foreground">Frequenz-Steuerung</h3>
            </div>

            {/* Main Controls */}
            <div className="space-y-6">
              {/* Frequenz */}
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <Label>Frequenz</Label>
                  <span className="text-2xl font-mono font-bold text-primary">
                    {frequency.toFixed(2)} Hz
                  </span>
                </div>
                <Slider
                  value={[frequency]}
                  onValueChange={(vals) => setFrequency(vals[0])}
                  min={0.1}
                  max={20000}
                  step={0.01}
                  className="w-full"
                />
                <div className="flex justify-between text-xs text-muted-foreground">
                  <span>0.1 Hz</span>
                  <span>20 kHz</span>
                </div>
              </div>

              {/* Amplitude */}
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <Label>Amplitude</Label>
                  <span className="text-sm font-mono text-muted-foreground">
                    {Math.round(amplitude * 100)}%
                  </span>
                </div>
                <Slider
                  value={[amplitude]}
                  onValueChange={(vals) => setAmplitude(vals[0])}
                  min={0}
                  max={1}
                  step={0.01}
                  className="w-full"
                />
              </div>

              {/* Waveform */}
              <div className="space-y-3">
                <Label>Wellenform</Label>
                <div className="grid grid-cols-4 gap-2">
                  {(['sine', 'square', 'triangle', 'sawtooth'] as const).map((wf) => (
                    <Button
                      key={wf}
                      variant={waveform === wf ? 'default' : 'outline'}
                      size="sm"
                      onClick={() => setWaveform(wf)}
                      className="capitalize"
                    >
                      {wf === 'sine' && '∿'}
                      {wf === 'square' && '⊓'}
                      {wf === 'triangle' && '△'}
                      {wf === 'sawtooth' && '⩘'}
                      <span className="ml-1 text-xs">{wf}</span>
                    </Button>
                  ))}
                </div>
              </div>

              {/* Modulation */}
              <div className="p-4 bg-muted/30 rounded-lg space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Settings2 className="w-4 h-4 text-muted-foreground" />
                    <Label>FM-Modulation</Label>
                  </div>
                  <Switch
                    checked={modulationEnabled}
                    onCheckedChange={setModulationEnabled}
                  />
                </div>

                {modulationEnabled && (
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label className="text-xs">Mod-Frequenz</Label>
                      <Slider
                        value={[modulationFreq]}
                        onValueChange={(vals) => setModulationFreq(vals[0])}
                        min={0.1}
                        max={20}
                        step={0.1}
                        className="mt-2"
                      />
                      <span className="text-xs text-muted-foreground">{modulationFreq} Hz</span>
                    </div>
                    <div>
                      <Label className="text-xs">Mod-Tiefe</Label>
                      <Slider
                        value={[modulationDepth]}
                        onValueChange={(vals) => setModulationDepth(vals[0])}
                        min={0}
                        max={1}
                        step={0.01}
                        className="mt-2"
                      />
                      <span className="text-xs text-muted-foreground">{Math.round(modulationDepth * 100)}%</span>
                    </div>
                  </div>
                )}
              </div>

              {/* Play Controls */}
              <div className="flex items-center gap-4 pt-4 border-t border-border">
                <Button
                  size="lg"
                  onClick={isPlaying ? stopAudio : startAudio}
                  className={cn(
                    "flex-1",
                    isPlaying && "bg-destructive hover:bg-destructive/90"
                  )}
                >
                  {isPlaying ? (
                    <>
                      <Square className="w-5 h-5 mr-2" />
                      Stopp
                    </>
                  ) : (
                    <>
                      <Play className="w-5 h-5 mr-2" />
                      Start
                    </>
                  )}
                </Button>
                <Button
                  variant="outline"
                  size="lg"
                  onClick={toggleMute}
                >
                  {isMuted ? (
                    <VolumeX className="w-5 h-5" />
                  ) : (
                    <Volume2 className="w-5 h-5" />
                  )}
                </Button>
              </div>

              {/* Echtzeit-Spektrum-Visualisierung */}
              <div className="mt-6 space-y-2">
                <div className="flex items-center gap-2">
                  <BarChart3 className="w-4 h-4 text-primary" />
                  <Label className="text-sm">FFT-Spektrum & Wellenform</Label>
                  {workletReady && (
                    <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-primary/10 text-primary">
                      AudioWorklet
                    </span>
                  )}
                </div>
                <SpectrumVisualizer
                  analyser={analyserNode}
                  isPlaying={isPlaying}
                  mode="both"
                  height={140}
                  className="border border-border"
                />
                {isPlaying && audioContextRef.current && (
                  <p className="text-[10px] font-mono text-muted-foreground">
                    Latenz: {Math.round((audioContextRef.current.baseLatency || 0) * 1000)}ms •
                    Sample-Rate: {audioContextRef.current.sampleRate} Hz •
                    {workletReady ? 'AudioWorklet' : 'Oszillator-Fallback'}
                  </p>
                )}
              </div>
            </div>
          </motion.div>

          {/* Presets & Punktsuche */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            className="space-y-6"
          >
            {/* Tabs für Presets und Akupunkturpunkt-Suche */}
            <div className="bg-card rounded-lg border border-border p-6 shadow-card">
              <Tabs defaultValue="presets" className="w-full">
                <TabsList className="w-full mb-4">
                  <TabsTrigger value="presets" className="flex-1">
                    <Zap className="w-4 h-4 mr-2" />
                    Presets
                  </TabsTrigger>
                  <TabsTrigger value="acupoints" className="flex-1">
                    <Search className="w-4 h-4 mr-2" />
                    Akupunktur
                  </TabsTrigger>
                </TabsList>

                <TabsContent value="presets" className="mt-0">
                  <div className="space-y-2 max-h-64 overflow-y-auto">
                    {THERAPEUTIC_FREQUENCIES.map((preset) => (
                      <button
                        key={preset.name}
                        onClick={() => selectPreset(preset)}
                        className={cn(
                          "w-full p-3 rounded-lg text-left transition-colors",
                          "bg-muted/30 hover:bg-primary/10 border border-transparent",
                          frequency === preset.frequency && "border-primary/50 bg-primary/10"
                        )}
                      >
                        <div className="flex items-center justify-between">
                          <span className="text-sm font-medium text-foreground">{preset.name}</span>
                          <span className="text-xs font-mono text-primary">{preset.frequency} Hz</span>
                        </div>
                        <p className="text-xs text-muted-foreground mt-1">{preset.description}</p>
                      </button>
                    ))}
                  </div>
                </TabsContent>

                <TabsContent value="acupoints" className="mt-0">
                  <AcupuncturePointSearch
                    compact
                    onSelectPoint={(freq, pointInfo) => {
                      setFrequency(freq);
                      toast.success(`${pointInfo.id}: ${pointInfo.name}`, {
                        description: `Frequenz: ${freq.toFixed(2)} Hz • Element: ${pointInfo.element}`
                      });
                    }}
                  />
                </TabsContent>
              </Tabs>
            </div>

            {/* EM Output */}
            <div className="bg-card rounded-lg border border-border p-6 shadow-card">
              <div className="flex items-center gap-3 mb-4">
                <Radio className="w-5 h-5 text-secondary" />
                <h4 className="font-medium text-foreground">EM-Feld Output</h4>
              </div>

              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Aktiviert</span>
                  <Switch
                    checked={emOutputEnabled}
                    onCheckedChange={setEmOutputEnabled}
                  />
                </div>

                {emOutputEnabled && (
                  <>
                    <div className="flex items-center justify-between p-3 bg-muted/30 rounded-lg">
                      <div className="flex items-center gap-2">
                        <div className={cn(
                          "w-2 h-2 rounded-full",
                          serialConnected ? "bg-green-400 animate-pulse" : "bg-muted-foreground"
                        )} />
                        <span className="text-sm text-foreground">
                          {serialConnected ? 'Verbunden' : 'Nicht verbunden'}
                        </span>
                      </div>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={serialConnected ? disconnectSerial : connectSerial}
                      >
                        {serialConnected ? 'Trennen' : 'Verbinden'}
                      </Button>
                    </div>

                    <p className="text-xs text-muted-foreground">
                      Verbinden Sie einen Frequenzgenerator (Spooky2, etc.) über WebSerial
                      für elektromagnetische Feldausgabe.
                    </p>
                  </>
                )}
              </div>
            </div>

            {/* Status Display */}
            {isPlaying && (
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="bg-primary/10 border border-primary/30 rounded-lg p-4"
              >
                <div className="flex items-center gap-3">
                  <Activity className="w-5 h-5 text-primary animate-pulse" />
                  <div>
                    <p className="text-sm font-medium text-foreground">Aktive Ausgabe</p>
                    <p className="text-xs text-muted-foreground">
                      {emOutputEnabled ? 'Audio + EM-Feld' : 'Nur Audio'}
                    </p>
                  </div>
                </div>
              </motion.div>
            )}
          </motion.div>
        </div>
      </div>
    </section>
  );
};

export default FrequencyOutputModule;
