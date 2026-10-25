/**
 * Hook für den automatischen NLS-Scan-Durchlauf
 * Scannt sequenziell alle konfigurierten Punkte mit Fortschrittsanzeige
 */
import { useState, useCallback, useRef, useEffect } from 'react';
import type { OrganScanPoint } from '@/hooks/useOrganScanPoints';
import type { NLSScanConfig } from '@/components/NLSScanConfigPanel';

export interface ScanResult {
  pointId: string;
  pointName: string;
  organSystem: string;
  scanFrequency: number;
  dysregulationScore: number; // 0-6
  timestamp: number;
}

export interface AutoScanState {
  isScanning: boolean;
  isPaused: boolean;
  currentIndex: number;
  totalPoints: number;
  currentPoint: OrganScanPoint | null;
  progress: number; // 0-1
  results: ScanResult[];
  elapsedMs: number;
  estimatedRemainingMs: number;
}

const SPEED_MS: Record<string, number> = {
  slow: 1500,
  normal: 800,
  fast: 400,
};

export function useNLSAutoScan() {
  const [state, setState] = useState<AutoScanState>({
    isScanning: false,
    isPaused: false,
    currentIndex: 0,
    totalPoints: 0,
    currentPoint: null,
    progress: 0,
    results: [],
    elapsedMs: 0,
    estimatedRemainingMs: 0,
  });

  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const startTimeRef = useRef<number>(0);
  const pointsRef = useRef<OrganScanPoint[]>([]);
  const configRef = useRef<NLSScanConfig | null>(null);
  const scoresRef = useRef<Map<string, number>>(new Map());
  const onPointScannedRef = useRef<((point: OrganScanPoint) => void) | null>(null);

  const clearTimer = useCallback(() => {
    if (timerRef.current) {
      clearTimeout(timerRef.current);
      timerRef.current = null;
    }
  }, []);

  const scanNextPoint = useCallback((index: number) => {
    const points = pointsRef.current;
    const config = configRef.current;
    if (!config || index >= points.length) {
      // Scan complete
      setState(prev => ({
        ...prev,
        isScanning: false,
        isPaused: false,
        progress: 1,
        currentPoint: null,
        estimatedRemainingMs: 0,
      }));
      return;
    }

    const point = points[index];
    const elapsed = Date.now() - startTimeRef.current;
    const avgPerPoint = index > 0 ? elapsed / index : SPEED_MS[config.scanSpeed];
    const remaining = (points.length - index) * avgPerPoint;

    // Get dysregulation score from the live scores map
    const dysScore = scoresRef.current.get(point.id) || 0;

    const result: ScanResult = {
      pointId: point.id,
      pointName: point.pointName,
      organSystem: point.organSystem,
      scanFrequency: point.scanFrequency,
      dysregulationScore: dysScore,
      timestamp: Date.now(),
    };

    setState(prev => ({
      ...prev,
      currentIndex: index,
      currentPoint: point,
      progress: (index + 1) / points.length,
      results: [...prev.results, result],
      elapsedMs: elapsed,
      estimatedRemainingMs: remaining,
    }));

    // Notify parent to highlight this point
    onPointScannedRef.current?.(point);

    // Schedule next
    const delay = SPEED_MS[config.scanSpeed] || 800;
    timerRef.current = setTimeout(() => scanNextPoint(index + 1), delay);
  }, []);

  const startScan = useCallback((
    points: OrganScanPoint[],
    config: NLSScanConfig,
    dysregulationScores: Map<string, number>,
    onPointScanned?: (point: OrganScanPoint) => void,
  ) => {
    clearTimer();
    pointsRef.current = points;
    configRef.current = config;
    scoresRef.current = dysregulationScores;
    onPointScannedRef.current = onPointScanned || null;
    startTimeRef.current = Date.now();

    setState({
      isScanning: true,
      isPaused: false,
      currentIndex: 0,
      totalPoints: points.length,
      currentPoint: points[0] || null,
      progress: 0,
      results: [],
      elapsedMs: 0,
      estimatedRemainingMs: points.length * (SPEED_MS[config.scanSpeed] || 800),
    });

    scanNextPoint(0);
  }, [clearTimer, scanNextPoint]);

  const pauseScan = useCallback(() => {
    clearTimer();
    setState(prev => ({ ...prev, isPaused: true }));
  }, [clearTimer]);

  const resumeScan = useCallback(() => {
    setState(prev => {
      if (!prev.isPaused) return prev;
      scanNextPoint(prev.currentIndex + 1);
      return { ...prev, isPaused: false };
    });
  }, [scanNextPoint]);

  const stopScan = useCallback(() => {
    clearTimer();
    setState(prev => ({
      ...prev,
      isScanning: false,
      isPaused: false,
      currentPoint: null,
    }));
  }, [clearTimer]);

  // Update live scores during scan
  const updateScores = useCallback((scores: Map<string, number>) => {
    scoresRef.current = scores;
  }, []);

  // Cleanup on unmount
  useEffect(() => () => clearTimer(), [clearTimer]);

  return {
    scanState: state,
    startScan,
    pauseScan,
    resumeScan,
    stopScan,
    updateScores,
  };
}
