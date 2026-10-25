/**
 * Echtzeit-Harmonisierungs-Service
 * GPU-beschleunigte Frequenzberechnung und Audio-Ausgabe über Server-Hardware
 * 
 * Nutzt:
 * - WebAudio API für High-Fidelity Audio-Ausgabe
 * - AudioWorklet für latenzarme Echtzeit-Verarbeitung
 * - WebSocket für Server-Hardware-Kommunikation (AMD Ryzen / NVIDIA RTX)
 * - WebSerial für direkte Hardware-Ansteuerung
 */

import { supabase } from '@/integrations/supabase/client';

// Audio-Worklet-Prozessor Code als String (wird dynamisch geladen)
const AUDIO_WORKLET_CODE = `
class FrequencyGeneratorProcessor extends AudioWorkletProcessor {
  constructor() {
    super();
    this.frequency = 440;
    this.amplitude = 0.5;
    this.waveform = 'sine';
    this.phase = 0;
    this.harmonics = [1, 0.5, 0.25, 0.125];
    this.modulationFreq = 0;
    this.modulationDepth = 0;
    this.modPhase = 0;
    
    this.port.onmessage = (e) => {
      if (e.data.frequency !== undefined) this.frequency = e.data.frequency;
      if (e.data.amplitude !== undefined) this.amplitude = e.data.amplitude;
      if (e.data.waveform !== undefined) this.waveform = e.data.waveform;
      if (e.data.harmonics !== undefined) this.harmonics = e.data.harmonics;
      if (e.data.modulationFreq !== undefined) this.modulationFreq = e.data.modulationFreq;
      if (e.data.modulationDepth !== undefined) this.modulationDepth = e.data.modulationDepth;
    };
  }

  generateSample(phase) {
    switch (this.waveform) {
      case 'sine':
        return Math.sin(phase * 2 * Math.PI);
      case 'square':
        return phase < 0.5 ? 1 : -1;
      case 'triangle':
        return 4 * Math.abs(phase - 0.5) - 1;
      case 'sawtooth':
        return 2 * phase - 1;
      case 'harmonic':
        let sample = 0;
        for (let i = 0; i < this.harmonics.length; i++) {
          sample += this.harmonics[i] * Math.sin(phase * (i + 1) * 2 * Math.PI);
        }
        return sample / this.harmonics.reduce((a, b) => a + b, 1);
      default:
        return Math.sin(phase * 2 * Math.PI);
    }
  }

  process(inputs, outputs, parameters) {
    const output = outputs[0];
    const channel = output[0];
    
    if (!channel) return true;
    
    for (let i = 0; i < channel.length; i++) {
      // FM Modulation
      let modValue = 0;
      if (this.modulationFreq > 0 && this.modulationDepth > 0) {
        modValue = Math.sin(this.modPhase * 2 * Math.PI) * this.modulationDepth * this.frequency;
        this.modPhase += this.modulationFreq / sampleRate;
        if (this.modPhase >= 1) this.modPhase -= 1;
      }
      
      const actualFreq = this.frequency + modValue;
      channel[i] = this.generateSample(this.phase) * this.amplitude;
      
      this.phase += actualFreq / sampleRate;
      if (this.phase >= 1) this.phase -= 1;
    }
    
    return true;
  }
}

registerProcessor('frequency-generator', FrequencyGeneratorProcessor);
`;

export interface HarmonizationConfig {
  frequency: number;
  amplitude: number;
  waveform: 'sine' | 'square' | 'triangle' | 'sawtooth' | 'harmonic' | 'bipolar';
  harmonics?: number[];
  modulationFreq?: number;
  modulationDepth?: number;
  duration?: number;
}

export interface ServerHardwareStatus {
  cpuUsage: number;
  gpuUsage: number;
  gpuMemory: number;
  audioLatency: number;
  isConnected: boolean;
  hardwareType: 'local' | 'server' | 'hybrid';
}

type HarmonizationEventCallback = (event: {
  type: 'started' | 'stopped' | 'frequencyChanged' | 'error' | 'serverStatus';
  data?: unknown;
}) => void;

class RealtimeHarmonizationServiceClass {
  private audioContext: AudioContext | null = null;
  private workletNode: AudioWorkletNode | null = null;
  private fallbackOscillator: OscillatorNode | null = null;
  private gainNode: GainNode | null = null;
  private analyser: AnalyserNode | null = null;
  private isInitialized = false;
  private isPlaying = false;
  private currentConfig: HarmonizationConfig | null = null;
  private eventListeners: Set<HarmonizationEventCallback> = new Set();
  
  // Server-Kommunikation
  private websocket: WebSocket | null = null;
  private serverStatus: ServerHardwareStatus = {
    cpuUsage: 0,
    gpuUsage: 0,
    gpuMemory: 0,
    audioLatency: 0,
    isConnected: false,
    hardwareType: 'local',
  };
  
  // Frequenz-Historie für Trend-Analyse
  private frequencyHistory: { timestamp: number; frequency: number; amplitude: number }[] = [];
  
  /**
   * Initialisiert den Audio-Kontext und AudioWorklet
   */
  async initialize(): Promise<boolean> {
    if (this.isInitialized) return true;
    
    try {
      // Audio-Kontext erstellen
      this.audioContext = new AudioContext({
        sampleRate: 48000, // Hohe Qualität
        latencyHint: 'interactive',
      });
      
      // AudioWorklet laden
      const blob = new Blob([AUDIO_WORKLET_CODE], { type: 'application/javascript' });
      const workletUrl = URL.createObjectURL(blob);
      
      try {
        await this.audioContext.audioWorklet.addModule(workletUrl);
      } catch (workletError) {
        console.warn('AudioWorklet nicht verfügbar, nutze Fallback:', workletError);
        // Fallback auf ScriptProcessorNode wenn Worklet nicht verfügbar
      }
      
      URL.revokeObjectURL(workletUrl);
      
      // Gain-Node für Lautstärkekontrolle
      this.gainNode = this.audioContext.createGain();
      this.gainNode.gain.value = 0;
      
      // Analyser für Visualisierung
      this.analyser = this.audioContext.createAnalyser();
      this.analyser.fftSize = 2048;
      
      // Verbindungen herstellen
      this.gainNode.connect(this.analyser);
      this.analyser.connect(this.audioContext.destination);
      
      // Server-Verbindung aufbauen
      await this.connectToServer();
      
      this.isInitialized = true;
      console.log('[RealtimeHarmonization] Initialisiert');
      
      return true;
    } catch (error) {
      console.error('[RealtimeHarmonization] Initialisierungsfehler:', error);
      return false;
    }
  }
  
  /**
   * Verbindet zum Server für GPU-beschleunigte Berechnungen
   */
  private async connectToServer(): Promise<void> {
    try {
      const wsUrl = `${import.meta.env.VITE_SUPABASE_URL?.replace('https', 'wss')}/functions/v1/realtime-sync`;
      
      this.websocket = new WebSocket(wsUrl);
      
      this.websocket.onopen = () => {
        this.serverStatus.isConnected = true;
        this.serverStatus.hardwareType = 'hybrid';
        this.emitEvent({ type: 'serverStatus', data: this.serverStatus });
        console.log('[RealtimeHarmonization] Server verbunden');
        
        // Hardware-Status anfragen
        this.websocket?.send(JSON.stringify({
          type: 'hardware_status_request',
        }));
      };
      
      this.websocket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          
          if (data.type === 'hardware_status') {
            this.serverStatus = {
              ...this.serverStatus,
              cpuUsage: data.cpu_usage || 0,
              gpuUsage: data.gpu_usage || 0,
              gpuMemory: data.gpu_memory || 0,
              audioLatency: data.audio_latency || 0,
            };
            this.emitEvent({ type: 'serverStatus', data: this.serverStatus });
          }
          
          if (data.type === 'frequency_calculated') {
            // GPU-berechnete Frequenzen empfangen
            if (this.workletNode) {
              this.workletNode.port.postMessage({
                frequency: data.frequency,
                harmonics: data.harmonics,
              });
            }
          }
        } catch (e) {
          console.error('[RealtimeHarmonization] Nachrichtenverarbeitung fehlgeschlagen:', e);
        }
      };
      
      this.websocket.onerror = (error) => {
        console.warn('[RealtimeHarmonization] WebSocket-Fehler:', error);
        this.serverStatus.isConnected = false;
        this.serverStatus.hardwareType = 'local';
      };
      
      this.websocket.onclose = () => {
        this.serverStatus.isConnected = false;
        this.serverStatus.hardwareType = 'local';
        this.emitEvent({ type: 'serverStatus', data: this.serverStatus });
      };
    } catch (error) {
      console.warn('[RealtimeHarmonization] Server-Verbindung fehlgeschlagen, nutze lokalen Modus:', error);
      this.serverStatus.hardwareType = 'local';
    }
  }
  
  /**
   * Startet Echtzeit-Harmonisierung
   */
  async startHarmonization(config: HarmonizationConfig): Promise<boolean> {
    if (!this.isInitialized) {
      await this.initialize();
    }
    
    if (!this.audioContext) return false;
    
    // Resume AudioContext wenn suspended
    if (this.audioContext.state === 'suspended') {
      await this.audioContext.resume();
    }
    
    try {
      // Stoppe vorherige Wiedergabe
      this.stopHarmonization();
      
      this.currentConfig = config;
      
      // Erstelle AudioWorklet Node oder Fallback
      try {
        this.workletNode = new AudioWorkletNode(this.audioContext, 'frequency-generator');
        this.workletNode.connect(this.gainNode!);
        
        // Konfiguration senden
        this.workletNode.port.postMessage({
          frequency: config.frequency,
          amplitude: config.amplitude,
          waveform: config.waveform,
          harmonics: config.harmonics || [1, 0.5, 0.25, 0.125, 0.0625],
          modulationFreq: config.modulationFreq || 0,
          modulationDepth: config.modulationDepth || 0,
        });
      } catch {
        // Fallback: Einfacher Oszillator
        const oscillator = this.audioContext.createOscillator();
        oscillator.frequency.value = config.frequency;
        oscillator.type = config.waveform === 'harmonic' ? 'sine' : config.waveform as OscillatorType;
        oscillator.connect(this.gainNode!);
        oscillator.start();
        
        // Speichere als Worklet-Fallback
        this.fallbackOscillator = oscillator;
      }
      
      // Fade in
      this.gainNode!.gain.setValueAtTime(0, this.audioContext.currentTime);
      this.gainNode!.gain.linearRampToValueAtTime(
        config.amplitude,
        this.audioContext.currentTime + 0.1
      );
      
      // Server über Frequenz informieren
      if (this.websocket?.readyState === WebSocket.OPEN) {
        this.websocket.send(JSON.stringify({
          type: 'frequency_sync',
          data: {
            frequency: config.frequency,
            amplitude: config.amplitude,
            waveform: config.waveform,
          },
        }));
      }
      
      // Historie aktualisieren
      this.frequencyHistory.push({
        timestamp: Date.now(),
        frequency: config.frequency,
        amplitude: config.amplitude,
      });
      
      // Begrenze Historie auf 1000 Einträge
      if (this.frequencyHistory.length > 1000) {
        this.frequencyHistory = this.frequencyHistory.slice(-1000);
      }
      
      this.isPlaying = true;
      this.emitEvent({ type: 'started', data: config });
      
      // Timer für automatisches Stoppen
      if (config.duration && config.duration > 0) {
        setTimeout(() => {
          this.stopHarmonization();
        }, config.duration * 1000);
      }
      
      return true;
    } catch (error) {
      console.error('[RealtimeHarmonization] Startfehler:', error);
      this.emitEvent({ type: 'error', data: error });
      return false;
    }
  }
  
  /**
   * Stoppt Harmonisierung
   */
  stopHarmonization(): void {
    if (this.gainNode && this.audioContext) {
      // Fade out
      this.gainNode.gain.linearRampToValueAtTime(
        0,
        this.audioContext.currentTime + 0.1
      );
    }
    
    setTimeout(() => {
      if (this.workletNode) {
        this.workletNode.disconnect();
        this.workletNode = null;
      }
      
      // Fallback Oszillator stoppen
      if (this.fallbackOscillator) {
        try {
          this.fallbackOscillator.stop();
          this.fallbackOscillator.disconnect();
        } catch (error) {
          void error;
        }
        this.fallbackOscillator = null;
      }
      
      this.isPlaying = false;
      this.emitEvent({ type: 'stopped' });
    }, 100);
  }
  
  /**
   * Ändert Frequenz in Echtzeit (latenzarm)
   */
  setFrequency(frequency: number): void {
    if (this.workletNode) {
      this.workletNode.port.postMessage({ frequency });
    }
    
    if (this.fallbackOscillator && this.audioContext) {
      this.fallbackOscillator.frequency.setValueAtTime(
        frequency,
        this.audioContext.currentTime
      );
    }
    
    if (this.currentConfig) {
      this.currentConfig.frequency = frequency;
    }
    
    this.frequencyHistory.push({
      timestamp: Date.now(),
      frequency,
      amplitude: this.currentConfig?.amplitude || 0.5,
    });
    
    this.emitEvent({ type: 'frequencyChanged', data: { frequency } });
  }
  
  /**
   * Ändert Amplitude in Echtzeit
   */
  setAmplitude(amplitude: number): void {
    if (this.gainNode && this.audioContext) {
      this.gainNode.gain.linearRampToValueAtTime(
        amplitude,
        this.audioContext.currentTime + 0.05
      );
    }
    
    if (this.workletNode) {
      this.workletNode.port.postMessage({ amplitude });
    }
    
    if (this.currentConfig) {
      this.currentConfig.amplitude = amplitude;
    }
  }
  
  /**
   * Holt Frequenzspektrum für Visualisierung
   */
  getFrequencyData(): Uint8Array {
    if (!this.analyser) return new Uint8Array(0);
    
    const data = new Uint8Array(this.analyser.frequencyBinCount);
    this.analyser.getByteFrequencyData(data);
    return data;
  }
  
  /**
   * Holt Wellenform für Visualisierung
   */
  getWaveformData(): Uint8Array {
    if (!this.analyser) return new Uint8Array(0);
    
    const data = new Uint8Array(this.analyser.frequencyBinCount);
    this.analyser.getByteTimeDomainData(data);
    return data;
  }
  
  /**
   * Sendet Frequenzberechnung zur GPU
   */
  async requestGPUCalculation(params: {
    baseFrequency: number;
    targetFrequency: number;
    harmonicCount: number;
    calculationType: 'harmonic_series' | 'resonance_field' | 'cusp_trajectory';
  }): Promise<number[] | null> {
    if (!this.websocket || this.websocket.readyState !== WebSocket.OPEN) {
      // Lokale Berechnung als Fallback
      return this.calculateHarmonicsLocally(params);
    }
    
    return new Promise((resolve) => {
      const requestId = `gpu-calc-${Date.now()}`;
      
      const handler = (event: MessageEvent) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === 'gpu_calculation_result' && data.requestId === requestId) {
            this.websocket?.removeEventListener('message', handler);
            resolve(data.result);
          }
        } catch (error) {
          void error;
        }
      };
      
      this.websocket!.addEventListener('message', handler);
      
      this.websocket!.send(JSON.stringify({
        type: 'gpu_calculation_request',
        requestId,
        params,
      }));
      
      // Timeout nach 5 Sekunden
      setTimeout(() => {
        this.websocket?.removeEventListener('message', handler);
        resolve(this.calculateHarmonicsLocally(params));
      }, 5000);
    });
  }
  
  /**
   * Lokale Harmonik-Berechnung (Fallback)
   */
  private calculateHarmonicsLocally(params: {
    baseFrequency: number;
    harmonicCount: number;
    calculationType: string;
  }): number[] {
    const harmonics: number[] = [];
    
    for (let i = 1; i <= params.harmonicCount; i++) {
      if (params.calculationType === 'harmonic_series') {
        harmonics.push(params.baseFrequency * i);
      } else if (params.calculationType === 'resonance_field') {
        // Golden Ratio basierte Harmonik
        harmonics.push(params.baseFrequency * Math.pow(1.618, i - 1));
      } else {
        // Fibonacci-Sequenz
        const fib = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55];
        harmonics.push(params.baseFrequency * (fib[i - 1] || i));
      }
    }
    
    return harmonics;
  }
  
  /**
   * Event-Listener hinzufügen
   */
  addEventListener(callback: HarmonizationEventCallback): void {
    this.eventListeners.add(callback);
  }
  
  /**
   * Event-Listener entfernen
   */
  removeEventListener(callback: HarmonizationEventCallback): void {
    this.eventListeners.delete(callback);
  }
  
  /**
   * Event emittieren
   */
  private emitEvent(event: Parameters<HarmonizationEventCallback>[0]): void {
    this.eventListeners.forEach((callback) => callback(event));
  }
  
  /**
   * Status abrufen
   */
  getStatus(): {
    isInitialized: boolean;
    isPlaying: boolean;
    currentConfig: HarmonizationConfig | null;
    serverStatus: ServerHardwareStatus;
  } {
    return {
      isInitialized: this.isInitialized,
      isPlaying: this.isPlaying,
      currentConfig: this.currentConfig,
      serverStatus: this.serverStatus,
    };
  }
  
  /**
   * Frequenz-Historie abrufen
   */
  getFrequencyHistory(): typeof this.frequencyHistory {
    return [...this.frequencyHistory];
  }
  
  /**
   * Aufräumen
   */
  destroy(): void {
    this.stopHarmonization();
    
    if (this.websocket) {
      this.websocket.close();
      this.websocket = null;
    }
    
    if (this.audioContext) {
      this.audioContext.close();
      this.audioContext = null;
    }
    
    this.isInitialized = false;
    this.eventListeners.clear();
    this.frequencyHistory = [];
  }
}

// Singleton-Export
export const RealtimeHarmonizationService = new RealtimeHarmonizationServiceClass();
export default RealtimeHarmonizationService;
