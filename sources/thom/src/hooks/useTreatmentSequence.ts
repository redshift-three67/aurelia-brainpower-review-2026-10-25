/**
 * Extended Treatment Sequence Hook
 * Erweitert um: Dauerbesendung nach Nachtestung und Trendanalyse
 */
import { useState, useCallback, useRef, useEffect } from 'react';
import { toast } from 'sonner';
import { MeridianImbalance, EXTRAORDINARY_VESSELS } from './useMeridianDiagnosis';
import { 
  COMPLETE_ACUPUNCTURE_DATABASE, 
  getCompletePointsByMeridian,
} from '@/utils/meridianPoints';

export interface TreatmentPoint {
  id: string;
  meridianId: string;
  meridianName: string;
  pointName: string;
  frequency: number;
  duration: number;
  element: string;
  isExtraordinaryVessel?: boolean;
  dysregulationScore?: number;
  explanation?: string;
}

export interface TreatmentProgress {
  currentPointIndex: number;
  totalPoints: number;
  currentPoint: TreatmentPoint | null;
  elapsedTime: number;
  remainingTime: number;
  isPlaying: boolean;
  isPaused: boolean;
  isComplete: boolean;
  overallProgress: number;
  isImpulsePhase: boolean;
  currentCycle: number;
  totalCycles: number;
  totalTreatmentTime: number;
  elapsedTotalTime: number;
  // NEU: Continuous-Mode Felder
  isContinuousMode: boolean;
  continuousEndTime: Date | null;
  awaitingRetest: boolean;
  retestPauseRemaining: number;
}

export interface TreatmentOptions {
  pointsPerMeridian?: number;
  durationPerPoint?: number;
  totalTreatmentMinutes?: number;
  impulseSeconds?: number;
  pauseSeconds?: number;
  includeExtraordinaryVessels?: boolean;
  // NEU: Continuous-Mode Optionen
  continuousMode?: boolean;
  continuousEndTime?: Date;
  retestPauseMinutes?: number;
  // Sequenz-Wiederholungen (1-42)
  repeatCycles?: number;
}

export interface TreatmentSnapshot {
  dimensions: number[];
  timestamp: Date;
  phase: 'before' | 'after_cycle' | 'after_retest' | 'final';
}

const DEFAULT_IMPULSE_SECONDS = 21;
const DEFAULT_PAUSE_SECONDS = 0;
const DEFAULT_TOTAL_TREATMENT_MINUTES = 60;
const DEFAULT_RETEST_PAUSE_MINUTES = 21;

const VESSEL_INDICATIONS: Record<string, string[]> = {
  DU: ['stress', 'mental', 'spine', 'yang_deficiency'],
  REN: ['emotional', 'yin_deficiency', 'fertility', 'breathing'],
  CHONG: ['blood_deficiency', 'heart', 'menstruation'],
  DAI: ['hip', 'lower_body', 'leukorrhea'],
  YANGQIAO: ['insomnia', 'epilepsy', 'eye', 'yang_excess'],
  YINQIAO: ['hypersomnia', 'yin_deficiency', 'eye'],
  YANGWEI: ['fever', 'external_pathogen', 'neck'],
  YINWEI: ['anxiety', 'heart', 'chest', 'emotional'],
};

export function useTreatmentSequence() {
  const [treatmentPoints, setTreatmentPoints] = useState<TreatmentPoint[]>([]);
  const [progress, setProgress] = useState<TreatmentProgress>({
    currentPointIndex: 0,
    totalPoints: 0,
    currentPoint: null,
    elapsedTime: 0,
    remainingTime: 0,
    isPlaying: false,
    isPaused: false,
    isComplete: false,
    overallProgress: 0,
    isImpulsePhase: true,
    currentCycle: 1,
    totalCycles: 1,
    totalTreatmentTime: 0,
    elapsedTotalTime: 0,
    isContinuousMode: false,
    continuousEndTime: null,
    awaitingRetest: false,
    retestPauseRemaining: 0,
  });

  // NEU: Snapshots für Trendanalyse
  const [snapshots, setSnapshots] = useState<TreatmentSnapshot[]>([]);
  const [onRetestCallback, setOnRetestCallback] = useState<(() => Promise<number[]>) | null>(null);

  const audioContextRef = useRef<AudioContext | null>(null);
  const oscillatorRef = useRef<OscillatorNode | null>(null);
  const gainNodeRef = useRef<GainNode | null>(null);
  // For sub-audible NLS frequencies: carrier oscillator + AM modulation
  const carrierOscRef = useRef<OscillatorNode | null>(null);
  const modulatorOscRef = useRef<OscillatorNode | null>(null);
  const modulatorGainRef = useRef<GainNode | null>(null);
  const isAMMode = useRef(false);
  const intervalRef = useRef<number | null>(null);
  const treatmentOptionsRef = useRef<TreatmentOptions>({});
  const imbalancesRef = useRef<MeridianImbalance[]>([]);
  // Refs to avoid stale closures in setInterval
  const treatmentPointsRef = useRef<TreatmentPoint[]>([]);
  const tickRef = useRef<() => void>(() => {});

  const stopOscillator = useCallback(() => {
    // Stop AM modulator nodes
    if (modulatorOscRef.current) {
      try { modulatorOscRef.current.stop(); modulatorOscRef.current.disconnect(); } catch (error) { void error; }
      modulatorOscRef.current = null;
    }
    if (modulatorGainRef.current) {
      try { modulatorGainRef.current.disconnect(); } catch (error) { void error; }
      modulatorGainRef.current = null;
    }
    if (carrierOscRef.current && carrierOscRef.current !== oscillatorRef.current) {
      try { carrierOscRef.current.stop(); carrierOscRef.current.disconnect(); } catch (error) { void error; }
    }
    carrierOscRef.current = null;

    if (oscillatorRef.current) {
      try { oscillatorRef.current.stop(); oscillatorRef.current.disconnect(); } catch (error) { void error; }
      oscillatorRef.current = null;
    }
    if (gainNodeRef.current) {
      try { gainNodeRef.current.disconnect(); } catch (error) { void error; }
      gainNodeRef.current = null;
    }
    isAMMode.current = false;
  }, []);

  useEffect(() => {
    // Auto-resume AudioContext when tab regains focus (prevents 3D view interaction breakage)
    const handleVisibilityChange = () => {
      if (document.visibilityState === 'visible' && audioContextRef.current?.state === 'suspended') {
        audioContextRef.current.resume().catch(() => {});
      }
    };
    // Protect against AudioContext suspension during heavy rendering
    const handleFocus = () => {
      if (audioContextRef.current?.state === 'suspended') {
        audioContextRef.current.resume().catch(() => {});
      }
    };
    document.addEventListener('visibilitychange', handleVisibilityChange);
    window.addEventListener('focus', handleFocus);

    return () => {
      stopOscillator();
      if (intervalRef.current) clearInterval(intervalRef.current);
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      window.removeEventListener('focus', handleFocus);
    };
  }, [stopOscillator]);

  const selectExtraordinaryVessels = useCallback((imbalances: MeridianImbalance[]): string[] => {
    const vesselScores: Record<string, number> = {};
    imbalances.forEach((imbalance) => {
      Object.entries(VESSEL_INDICATIONS).forEach(([vesselId]) => {
        let score = 0;
        if (imbalance.imbalanceType === 'excess' && ['DU', 'YANGWEI', 'YANGQIAO'].includes(vesselId)) {
          score += imbalance.imbalanceScore * 0.3;
        }
        if (imbalance.imbalanceType === 'deficiency' && ['REN', 'YINQIAO', 'CHONG', 'YINWEI'].includes(vesselId)) {
          score += imbalance.imbalanceScore * 0.3;
        }
        vesselScores[vesselId] = (vesselScores[vesselId] || 0) + score;
      });
    });
    return Object.entries(vesselScores)
      .filter(([_, score]) => score > 0.1)
      .sort(([, a], [, b]) => b - a)
      .slice(0, 3)
      .map(([id]) => id);
  }, []);

  const generatePointExplanation = useCallback((
    point: typeof COMPLETE_ACUPUNCTURE_DATABASE[number],
    imbalance: MeridianImbalance
  ): string => {
    const typeLabels = { excess: 'Überschuss', deficiency: 'Mangel', stagnation: 'Stagnation' };
    return `${typeLabels[imbalance.imbalanceType]} im ${imbalance.meridianName}. Punkt ${point.id} bei ${point.frequency.toFixed(1)} Hz.`;
  }, []);

  const generateTreatmentPoints = useCallback((
    imbalances: MeridianImbalance[],
    pointsPerMeridian: number = 3,
    durationPerPoint: number = 35,
    includeExtraordinaryVessels: boolean = true
  ): TreatmentPoint[] => {
    const points: TreatmentPoint[] = [];
    const effectivePointsPerMeridian = Math.min(9, Math.max(1, pointsPerMeridian));
    const topImbalances = imbalances.slice(0, 5);

    topImbalances.forEach((imbalance) => {
      const meridianPoints = getCompletePointsByMeridian(imbalance.meridianId);
      let selectedPoints = meridianPoints;
      
      if (imbalance.imbalanceType === 'excess') {
        selectedPoints = meridianPoints.filter(p => 
          p.pointTypes?.some(t => ['he_sea', 'xi_cleft', 'luo_connecting'].includes(t))
        );
      } else if (imbalance.imbalanceType === 'deficiency') {
        selectedPoints = meridianPoints.filter(p => 
          p.pointTypes?.some(t => ['yuan_source', 'shu_stream', 'jing_well'].includes(t))
        );
      }
      
      if (selectedPoints.length === 0) {
        selectedPoints = meridianPoints.filter(p => imbalance.recommendedPoints.includes(p.id));
      }
      
      const finalPoints = selectedPoints.length > 0 
        ? selectedPoints.slice(0, effectivePointsPerMeridian)
        : meridianPoints.slice(0, effectivePointsPerMeridian);

      finalPoints.forEach((point) => {
        points.push({
          id: point.id,
          meridianId: imbalance.meridianId,
          meridianName: imbalance.meridianName,
          pointName: `${point.id} - ${point.nameGerman}`,
          frequency: point.frequency,
          duration: durationPerPoint,
          element: point.element,
          isExtraordinaryVessel: false,
          dysregulationScore: imbalance.imbalanceScore,
          explanation: generatePointExplanation(point, imbalance),
        });
      });
    });

    if (includeExtraordinaryVessels) {
      const relevantVessels = selectExtraordinaryVessels(imbalances);
      relevantVessels.forEach((vesselId) => {
        const vessel = EXTRAORDINARY_VESSELS[vesselId];
        if (vessel) {
          points.push({
            id: `${vesselId}-opening`,
            meridianId: vesselId,
            meridianName: vessel.name,
            pointName: `${vessel.openingPoint} (Öffnungspunkt)`,
            frequency: vessel.frequency,
            duration: durationPerPoint,
            element: 'extraordinary',
            isExtraordinaryVessel: true,
            explanation: `Außerordentliches Gefäß ${vessel.name}`,
          });
        }
      });
    }

    return points;
  }, [selectExtraordinaryVessels, generatePointExplanation]);

  /**
   * Sub-audible threshold (Hz). Frequencies below this use AM modulation
   * with a 432 Hz carrier to make them audible while preserving the
   * therapeutic information frequency.
   */
  const SUB_AUDIBLE_THRESHOLD = 20;
  const AM_CARRIER_FREQUENCY = 432; // Natürliche Stimmung als Träger

  const startOscillator = useCallback(async (frequency: number) => {
    try {
      if (!audioContextRef.current) {
        audioContextRef.current = new AudioContext({
          sampleRate: 48000,
          latencyHint: 'playback',
        });
      }
      if (audioContextRef.current.state === 'suspended') {
        await audioContextRef.current.resume();
      }

      const ctx = audioContextRef.current;
      const needsAM = frequency < SUB_AUDIBLE_THRESHOLD && frequency > 0;

      // === AM-Modus für sub-audible Frequenzen (NLS-Punkte 1-20 Hz) ===
      if (needsAM) {
        // Wenn bereits im AM-Modus: nur Modulator-Frequenz ändern
        if (isAMMode.current && carrierOscRef.current && modulatorOscRef.current && gainNodeRef.current) {
          modulatorOscRef.current.frequency.setValueAtTime(frequency, ctx.currentTime);
          gainNodeRef.current.gain.setValueAtTime(0.8, ctx.currentTime);
          return;
        }

        // Bestehenden Standard-Oszillator stoppen
        stopOscillator();

        if (ctx.state !== 'running') return;

        // Carrier: hörbarer Sinus-Ton (432 Hz)
        const carrier = ctx.createOscillator();
        carrier.type = 'sine';
        carrier.frequency.setValueAtTime(AM_CARRIER_FREQUENCY, ctx.currentTime);

        // Modulator: NLS-Frequenz steuert die Amplitude des Carriers
        const modulator = ctx.createOscillator();
        modulator.type = 'sine';
        modulator.frequency.setValueAtTime(frequency, ctx.currentTime);

        // ModulatorGain: Tiefe der Amplitudenmodulation (0.5 = 50%)
        const modGain = ctx.createGain();
        modGain.gain.setValueAtTime(0.4, ctx.currentTime);

        // Output-Gain
        const outputGain = ctx.createGain();
        outputGain.gain.setValueAtTime(0.8, ctx.currentTime);

        // AM-Verschaltung: modulator → modGain → carrier.gain
        // Carrier → outputGain → destination
        modulator.connect(modGain);
        
        // Carrier mit konstantem Basis-Gain + Modulation
        const carrierGain = ctx.createGain();
        carrierGain.gain.setValueAtTime(0.5, ctx.currentTime); // Basis-Amplitude
        modGain.connect(carrierGain.gain); // AM: Modulator moduliert Carrier-Amplitude

        carrier.connect(carrierGain);
        carrierGain.connect(outputGain);
        outputGain.connect(ctx.destination);

        carrier.start();
        modulator.start();

        carrierOscRef.current = carrier;
        modulatorOscRef.current = modulator;
        modulatorGainRef.current = modGain;
        gainNodeRef.current = outputGain;
        oscillatorRef.current = carrier; // Für stopOscillator-Kompatibilität
        isAMMode.current = true;
        return;
      }

      // === Standard-Modus für hörbare Frequenzen (Meridian-Punkte) ===
      if (isAMMode.current) {
        // War im AM-Modus → komplett stoppen und neu aufbauen
        stopOscillator();
        isAMMode.current = false;
      }

      // Reuse existing oscillator if possible
      if (oscillatorRef.current && gainNodeRef.current && !isAMMode.current) {
        oscillatorRef.current.frequency.setValueAtTime(frequency, ctx.currentTime);
        gainNodeRef.current.gain.setValueAtTime(0.8, ctx.currentTime);
        return;
      }
      stopOscillator();
      if (ctx.state !== 'running') return;

      const oscillator = ctx.createOscillator();
      oscillator.type = 'sine';
      oscillator.frequency.setValueAtTime(frequency, ctx.currentTime);
      const gainNode = ctx.createGain();
      gainNode.gain.setValueAtTime(0.8, ctx.currentTime);
      oscillator.connect(gainNode);
      gainNode.connect(ctx.destination);
      oscillator.start();
      oscillatorRef.current = oscillator;
      gainNodeRef.current = gainNode;
    } catch (error) {
      console.warn('[Treatment] Oscillator error (auto-recovering):', error);
      oscillatorRef.current = null;
      gainNodeRef.current = null;
      carrierOscRef.current = null;
      modulatorOscRef.current = null;
      isAMMode.current = false;
    }
  }, [stopOscillator]);

  // NEU: Retest und Continuous-Mode Handler
  const handleRetestComplete = useCallback(async (newDimensions: number[]) => {
    setSnapshots(prev => [...prev, {
      dimensions: newDimensions,
      timestamp: new Date(),
      phase: 'after_retest',
    }]);

    const options = treatmentOptionsRef.current;
    const continuousEndTime = options.continuousEndTime;
    const points = treatmentPointsRef.current; // Use ref

    // Prüfen ob Endzeit noch nicht erreicht (Continuous-Mode)
    if (options.continuousMode && continuousEndTime && new Date() < continuousEndTime) {
      toast.info('Retest abgeschlossen - Starte nächsten Behandlungszyklus');
      
      // Neue Behandlung starten
      setProgress(prev => ({
        ...prev,
        awaitingRetest: false,
        currentPointIndex: 0,
        elapsedTime: 0,
        currentCycle: prev.currentCycle + 1,
        isPlaying: true,
      }));

      const firstPoint = points[0];
      if (firstPoint) {
        startOscillator(firstPoint.frequency);
      }
    } else {
      // Endzeit erreicht - finale Analyse
      setSnapshots(prev => [...prev, {
        dimensions: newDimensions,
        timestamp: new Date(),
        phase: 'final',
      }]);
      
      setProgress(prev => ({
        ...prev,
        isComplete: true,
        isPlaying: false,
        awaitingRetest: false,
        isContinuousMode: false,
      }));

      toast.success('Dauerbehandlung abgeschlossen!', {
        description: 'Trendanalyse verfügbar'
      });
    }
  }, [startOscillator]);

  // Keep ref in sync with state
  useEffect(() => {
    treatmentPointsRef.current = treatmentPoints;
  }, [treatmentPoints]);

  const moveToNextPoint = useCallback(() => {
    setProgress((prev) => {
      const options = treatmentOptionsRef.current;
      const points = treatmentPointsRef.current; // Use ref, not stale closure
      const nextIndex = prev.currentPointIndex + 1;

      // Zyklus beendet
      if (nextIndex >= prev.totalPoints) {
        // Im Continuous-Mode: Retest-Pause starten
        if (prev.isContinuousMode && prev.continuousEndTime && new Date() < prev.continuousEndTime) {
          stopOscillator();
          const retestPauseSeconds = (options.retestPauseMinutes || DEFAULT_RETEST_PAUSE_MINUTES) * 60;
          
          toast.info('Zyklus abgeschlossen - Retest-Pause gestartet', {
            description: `${options.retestPauseMinutes || DEFAULT_RETEST_PAUSE_MINUTES} Minuten bis zum Retest`
          });

          return {
            ...prev,
            awaitingRetest: true,
            retestPauseRemaining: retestPauseSeconds,
            isPlaying: false,
          };
        }

        // Normaler Modus: Prüfe Zyklen-Limit
        const maxCycles = options.repeatCycles || 1;
        if (prev.currentCycle >= maxCycles) {
          stopOscillator();
          if (intervalRef.current) {
            clearInterval(intervalRef.current);
            intervalRef.current = null;
          }
          toast.success(`Behandlungssequenz abgeschlossen! (${prev.currentCycle}/${maxCycles} Zyklen)`);
          return { ...prev, isPlaying: false, isComplete: true, overallProgress: 100 };
        }

        // Neuer Zyklus
        const firstPoint = points[0];
        if (firstPoint) startOscillator(firstPoint.frequency);
        
        toast.info(`Zyklus ${prev.currentCycle + 1}/${maxCycles} gestartet`);
        
        return {
          ...prev,
          currentPointIndex: 0,
          currentPoint: firstPoint || null,
          elapsedTime: 0,
          currentCycle: prev.currentCycle + 1,
          totalCycles: maxCycles,
          isImpulsePhase: true,
        };
      }

      const nextPoint = points[nextIndex];
      if (nextPoint) startOscillator(nextPoint.frequency);

      return {
        ...prev,
        currentPointIndex: nextIndex,
        currentPoint: nextPoint || null,
        elapsedTime: 0,
        isImpulsePhase: true,
      };
    });
  }, [startOscillator, stopOscillator]);

  const tick = useCallback(() => {
    setProgress((prev) => {
      // Retest-Pause Countdown
      if (prev.awaitingRetest && prev.retestPauseRemaining > 0) {
        const newRemaining = prev.retestPauseRemaining - 1;
        if (newRemaining <= 0) {
          // Retest-Callback ausführen
          if (onRetestCallback) {
            onRetestCallback().then(handleRetestComplete);
          }
        }
        return { ...prev, retestPauseRemaining: newRemaining };
      }

      if (!prev.isPlaying || prev.isPaused || prev.isComplete) return prev;

      const options = treatmentOptionsRef.current;
      const impulseSeconds = options.impulseSeconds || DEFAULT_IMPULSE_SECONDS;
      const pauseSeconds = options.pauseSeconds || DEFAULT_PAUSE_SECONDS;
      const pointDuration = impulseSeconds + pauseSeconds;

      const newElapsed = prev.elapsedTime + 1;
      const newTotalElapsed = prev.elapsedTotalTime + 1;
      const isImpulsePhase = newElapsed <= impulseSeconds;

      // Audio-Steuerung: Konstante Amplitude, kein Fading
      if (!isImpulsePhase && prev.isImpulsePhase && gainNodeRef.current && audioContextRef.current) {
        gainNodeRef.current.gain.setValueAtTime(0, audioContextRef.current.currentTime);
      } else if (isImpulsePhase && !prev.isImpulsePhase && gainNodeRef.current && audioContextRef.current) {
        gainNodeRef.current.gain.setValueAtTime(0.8, audioContextRef.current.currentTime);
      }

      if (newElapsed >= pointDuration) {
        setTimeout(() => moveToNextPoint(), 0);
        return { ...prev, elapsedTotalTime: newTotalElapsed };
      }

      // Continuous-Mode Fortschritt
      let overallProgress = 0;
      if (prev.isContinuousMode && prev.continuousEndTime) {
        const totalMs = prev.continuousEndTime.getTime() - (prev.continuousEndTime.getTime() - prev.totalTreatmentTime * 1000);
        const elapsedMs = newTotalElapsed * 1000;
        overallProgress = Math.min(100, (elapsedMs / (prev.totalTreatmentTime * 1000)) * 100);
      } else {
        const maxCycles = options.repeatCycles || 1;
        const totalPointsAllCycles = prev.totalPoints * maxCycles;
        const completedPoints = (prev.currentCycle - 1) * prev.totalPoints + prev.currentPointIndex;
        overallProgress = (completedPoints / totalPointsAllCycles) * 100;
      }

      return {
        ...prev,
        elapsedTime: newElapsed,
        remainingTime: pointDuration - newElapsed,
        elapsedTotalTime: newTotalElapsed,
        overallProgress: Math.min(100, overallProgress),
        isImpulsePhase,
      };
    });
  }, [moveToNextPoint, onRetestCallback, handleRetestComplete]);

  // Keep tickRef in sync so the interval always calls the latest tick
  useEffect(() => {
    tickRef.current = tick;
  }, [tick]);

  // Stable interval callback that delegates to tickRef
  const stableTick = useCallback(() => {
    tickRef.current();
  }, []);

  const startSequence = useCallback((
    imbalances: MeridianImbalance[], 
    options?: TreatmentOptions,
    retestCallback?: () => Promise<number[]>,
    extraPoints?: TreatmentPoint[]
  ) => {
    const effectiveOptions: TreatmentOptions = {
      pointsPerMeridian: options?.pointsPerMeridian ?? 7,
      durationPerPoint: (options?.impulseSeconds || DEFAULT_IMPULSE_SECONDS) + (options?.pauseSeconds || DEFAULT_PAUSE_SECONDS),
      totalTreatmentMinutes: options?.totalTreatmentMinutes ?? DEFAULT_TOTAL_TREATMENT_MINUTES,
      impulseSeconds: options?.impulseSeconds ?? DEFAULT_IMPULSE_SECONDS,
      pauseSeconds: options?.pauseSeconds ?? DEFAULT_PAUSE_SECONDS,
      includeExtraordinaryVessels: options?.includeExtraordinaryVessels ?? true,
      continuousMode: options?.continuousMode ?? false,
      continuousEndTime: options?.continuousEndTime,
      retestPauseMinutes: options?.retestPauseMinutes ?? DEFAULT_RETEST_PAUSE_MINUTES,
      repeatCycles: options?.repeatCycles ?? 1,
    };
    
    treatmentOptionsRef.current = effectiveOptions;
    imbalancesRef.current = imbalances;
    if (retestCallback) setOnRetestCallback(() => retestCallback);
    
    const points = generateTreatmentPoints(
      imbalances,
      effectiveOptions.pointsPerMeridian,
      effectiveOptions.durationPerPoint,
      effectiveOptions.includeExtraordinaryVessels
    );

    // Append extra points (e.g. NLS scan points)
    if (extraPoints && extraPoints.length > 0) {
      points.push(...extraPoints);
    }

    if (points.length === 0) {
      toast.warning('Keine Behandlungspunkte verfügbar');
      return;
    }

    setTreatmentPoints(points);
    setSnapshots([]);

    const firstPoint = points[0];
    startOscillator(firstPoint.frequency);
    
    const totalTreatmentSeconds = effectiveOptions.continuousMode && effectiveOptions.continuousEndTime
      ? Math.floor((effectiveOptions.continuousEndTime.getTime() - Date.now()) / 1000)
      : (effectiveOptions.totalTreatmentMinutes || DEFAULT_TOTAL_TREATMENT_MINUTES) * 60;

    setProgress({
      currentPointIndex: 0,
      totalPoints: points.length,
      currentPoint: firstPoint,
      elapsedTime: 0,
      remainingTime: (effectiveOptions.impulseSeconds || DEFAULT_IMPULSE_SECONDS) + (effectiveOptions.pauseSeconds || DEFAULT_PAUSE_SECONDS),
      isPlaying: true,
      isPaused: false,
      isComplete: false,
      overallProgress: 0,
      isImpulsePhase: true,
      currentCycle: 1,
      totalCycles: effectiveOptions.repeatCycles || 1,
      totalTreatmentTime: totalTreatmentSeconds,
      elapsedTotalTime: 0,
      isContinuousMode: effectiveOptions.continuousMode || false,
      continuousEndTime: effectiveOptions.continuousEndTime || null,
      awaitingRetest: false,
      retestPauseRemaining: 0,
    });

    const modeName = effectiveOptions.continuousMode ? 'Dauerbehandlung' : 'Behandlung';
    toast.success(`${modeName} gestartet`, {
      description: `${points.length} Punkte${effectiveOptions.continuousMode ? ' bis Endzeit' : ''}`
    });

    if (intervalRef.current) clearInterval(intervalRef.current);
    intervalRef.current = window.setInterval(stableTick, 1000);
  }, [generateTreatmentPoints, startOscillator, stableTick]);

  const pauseSequence = useCallback(() => {
    stopOscillator();
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
    setProgress((prev) => ({ ...prev, isPaused: true, isPlaying: false }));
    toast.info('Behandlung pausiert');
  }, [stopOscillator]);

  const resumeSequence = useCallback(() => {
    if (progress.currentPoint) startOscillator(progress.currentPoint.frequency);
    setProgress((prev) => ({ ...prev, isPaused: false, isPlaying: true }));
    // Restart the tick interval
    if (intervalRef.current) clearInterval(intervalRef.current);
    intervalRef.current = window.setInterval(stableTick, 1000);
    toast.info('Behandlung fortgesetzt');
  }, [progress.currentPoint, startOscillator, stableTick]);

  const stopSequence = useCallback(() => {
    stopOscillator();
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
    setProgress({
      currentPointIndex: 0,
      totalPoints: 0,
      currentPoint: null,
      elapsedTime: 0,
      remainingTime: 0,
      isPlaying: false,
      isPaused: false,
      isComplete: false,
      overallProgress: 0,
      isImpulsePhase: true,
      currentCycle: 1,
      totalCycles: 1,
      totalTreatmentTime: 0,
      elapsedTotalTime: 0,
      isContinuousMode: false,
      continuousEndTime: null,
      awaitingRetest: false,
      retestPauseRemaining: 0,
    });
    setTreatmentPoints([]);
    toast.info('Behandlung beendet');
  }, [stopOscillator]);

  const skipToPoint = useCallback((index: number) => {
    const points = treatmentPointsRef.current;
    if (index < 0 || index >= points.length) return;
    const point = points[index];
    startOscillator(point.frequency);
    setProgress((prev) => ({
      ...prev,
      currentPointIndex: index,
      currentPoint: point,
      elapsedTime: 0,
      remainingTime: point.duration,
      isImpulsePhase: true,
    }));
  }, [startOscillator]);

  const addSnapshot = useCallback((dimensions: number[], phase: TreatmentSnapshot['phase']) => {
    setSnapshots(prev => [...prev, { dimensions, timestamp: new Date(), phase }]);
  }, []);

  return {
    treatmentPoints,
    progress,
    snapshots,
    startSequence,
    pauseSequence,
    resumeSequence,
    stopSequence,
    skipToPoint,
    generateTreatmentPoints,
    addSnapshot,
    handleRetestComplete,
  };
}
