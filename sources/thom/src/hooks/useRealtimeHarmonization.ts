/**
 * Hook für Echtzeit-Harmonisierung
 * Nutzt den RealtimeHarmonizationService für GPU-beschleunigte Frequenzausgabe
 */
import { useState, useEffect, useCallback, useRef } from 'react';
import { 
  RealtimeHarmonizationService, 
  type HarmonizationConfig,
  type ServerHardwareStatus 
} from '@/services/realtime/RealtimeHarmonizationService';
import { toast } from 'sonner';

export interface RealtimeHarmonizationState {
  isInitialized: boolean;
  isPlaying: boolean;
  currentFrequency: number;
  currentAmplitude: number;
  serverStatus: ServerHardwareStatus;
  frequencySpectrum: Uint8Array;
  waveform: Uint8Array;
}

export function useRealtimeHarmonization() {
  const [state, setState] = useState<RealtimeHarmonizationState>({
    isInitialized: false,
    isPlaying: false,
    currentFrequency: 0,
    currentAmplitude: 0.5,
    serverStatus: {
      cpuUsage: 0,
      gpuUsage: 0,
      gpuMemory: 0,
      audioLatency: 0,
      isConnected: false,
      hardwareType: 'local',
    },
    frequencySpectrum: new Uint8Array(0),
    waveform: new Uint8Array(0),
  });
  
  const animationFrameRef = useRef<number | null>(null);
  const isRunningRef = useRef(false);

  // Initialisierung
  const initialize = useCallback(async () => {
    const success = await RealtimeHarmonizationService.initialize();
    if (success) {
      const status = RealtimeHarmonizationService.getStatus();
      setState(prev => ({
        ...prev,
        isInitialized: true,
        serverStatus: status.serverStatus,
      }));
    }
    return success;
  }, []);

  // Harmonisierung starten
  const startHarmonization = useCallback(async (config: HarmonizationConfig) => {
    if (!state.isInitialized) {
      await initialize();
    }
    
    const success = await RealtimeHarmonizationService.startHarmonization(config);
    
    if (success) {
      setState(prev => ({
        ...prev,
        isPlaying: true,
        currentFrequency: config.frequency,
        currentAmplitude: config.amplitude,
      }));
      
      toast.success('Echtzeit-Harmonisierung gestartet', {
        description: `${config.frequency.toFixed(2)} Hz • ${config.waveform}`,
      });
    }
    
    return success;
  }, [state.isInitialized, initialize]);

  // Harmonisierung stoppen
  const stopHarmonization = useCallback(() => {
    RealtimeHarmonizationService.stopHarmonization();
    setState(prev => ({
      ...prev,
      isPlaying: false,
      currentFrequency: 0,
    }));
  }, []);

  // Frequenz in Echtzeit ändern
  const setFrequency = useCallback((frequency: number) => {
    RealtimeHarmonizationService.setFrequency(frequency);
    setState(prev => ({
      ...prev,
      currentFrequency: frequency,
    }));
  }, []);

  // Amplitude in Echtzeit ändern
  const setAmplitude = useCallback((amplitude: number) => {
    RealtimeHarmonizationService.setAmplitude(amplitude);
    setState(prev => ({
      ...prev,
      currentAmplitude: amplitude,
    }));
  }, []);

  // GPU-Berechnung anfordern
  const requestGPUCalculation = useCallback(async (params: {
    baseFrequency: number;
    targetFrequency: number;
    harmonicCount: number;
    calculationType: 'harmonic_series' | 'resonance_field' | 'cusp_trajectory';
  }) => {
    return RealtimeHarmonizationService.requestGPUCalculation(params);
  }, []);

  // Visualisierungs-Loop
  const updateVisualization = useCallback(() => {
    if (!isRunningRef.current) return;
    
    const spectrum = RealtimeHarmonizationService.getFrequencyData();
    const waveform = RealtimeHarmonizationService.getWaveformData();
    
    setState(prev => ({
      ...prev,
      frequencySpectrum: spectrum,
      waveform: waveform,
    }));
    
    animationFrameRef.current = requestAnimationFrame(updateVisualization);
  }, []);

  // Event-Listener
  useEffect(() => {
    const handleEvent = (event: {
      type: 'started' | 'stopped' | 'frequencyChanged' | 'error' | 'serverStatus';
      data?: unknown;
    }) => {
      switch (event.type) {
        case 'started':
          setState(prev => ({ ...prev, isPlaying: true }));
          break;
        case 'stopped':
          setState(prev => ({ ...prev, isPlaying: false }));
          break;
        case 'serverStatus':
          setState(prev => ({
            ...prev,
            serverStatus: event.data as ServerHardwareStatus,
          }));
          break;
        case 'error':
          toast.error('Harmonisierungsfehler', {
            description: String(event.data),
          });
          break;
      }
    };
    
    RealtimeHarmonizationService.addEventListener(handleEvent);
    
    return () => {
      RealtimeHarmonizationService.removeEventListener(handleEvent);
    };
  }, []);

  // Visualisierungs-Loop starten/stoppen
  useEffect(() => {
    if (state.isPlaying) {
      isRunningRef.current = true;
      updateVisualization();
    } else {
      isRunningRef.current = false;
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    }
    
    return () => {
      isRunningRef.current = false;
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, [state.isPlaying, updateVisualization]);

  // Cleanup
  useEffect(() => {
    return () => {
      isRunningRef.current = false;
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, []);

  return {
    state,
    initialize,
    startHarmonization,
    stopHarmonization,
    setFrequency,
    setAmplitude,
    requestGPUCalculation,
    getFrequencyHistory: () => RealtimeHarmonizationService.getFrequencyHistory(),
  };
}

export default useRealtimeHarmonization;
