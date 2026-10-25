/**
 * NLS Auto-Scan Fortschritts-Overlay
 * Zeigt den aktuellen Scan-Fortschritt, gescannten Punkt und Dysregulations-Ergebnisse
 */
import { useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Play, Pause, Square, Activity, AlertTriangle, CheckCircle2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { getOrganColor } from '@/hooks/useOrganScanPoints';
import type { AutoScanState } from '@/hooks/useNLSAutoScan';

interface NLSAutoScanOverlayProps {
  scanState: AutoScanState;
  onPause: () => void;
  onResume: () => void;
  onStop: () => void;
}

function formatTime(ms: number): string {
  const s = Math.round(ms / 1000);
  const m = Math.floor(s / 60);
  const sec = s % 60;
  return m > 0 ? `${m}:${sec.toString().padStart(2, '0')}` : `${sec}s`;
}

export function NLSAutoScanOverlay({ scanState, onPause, onResume, onStop }: NLSAutoScanOverlayProps) {
  const { isScanning, isPaused, currentIndex, totalPoints, currentPoint, progress, results, elapsedMs, estimatedRemainingMs } = scanState;

  const dysregulatedCount = useMemo(() =>
    results.filter(r => r.dysregulationScore > 2.5).length,
  [results]);

  const organSummary = useMemo(() => {
    const map = new Map<string, { count: number; dysCount: number }>();
    results.forEach(r => {
      const entry = map.get(r.organSystem) || { count: 0, dysCount: 0 };
      entry.count++;
      if (r.dysregulationScore > 2.5) entry.dysCount++;
      map.set(r.organSystem, entry);
    });
    return Array.from(map.entries())
      .sort((a, b) => b[1].dysCount - a[1].dysCount)
      .slice(0, 6);
  }, [results]);

  const isComplete = !isScanning && results.length > 0 && progress >= 1;

  if (!isScanning && !isComplete) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: 20 }}
        className="absolute top-16 right-4 z-20 w-72 bg-card/95 backdrop-blur-md rounded-lg border border-border shadow-lg overflow-hidden"
      >
        {/* Header */}
        <div className="px-3 py-2 bg-primary/10 border-b border-border flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Activity className="w-4 h-4 text-primary animate-pulse" />
            <span className="text-xs font-semibold text-foreground">
              {isComplete ? 'Scan abgeschlossen' : isPaused ? 'Scan pausiert' : 'NLS-Scan läuft…'}
            </span>
          </div>
          <div className="flex gap-1">
            {isScanning && (
              <>
                <Button variant="ghost" size="icon" className="h-6 w-6" onClick={isPaused ? onResume : onPause}>
                  {isPaused ? <Play className="w-3 h-3" /> : <Pause className="w-3 h-3" />}
                </Button>
                <Button variant="ghost" size="icon" className="h-6 w-6 text-destructive" onClick={onStop}>
                  <Square className="w-3 h-3" />
                </Button>
              </>
            )}
            {isComplete && (
              <Button variant="ghost" size="icon" className="h-6 w-6" onClick={onStop}>
                <CheckCircle2 className="w-3 h-3 text-primary" />
              </Button>
            )}
          </div>
        </div>

        {/* Progress */}
        <div className="px-3 py-2 space-y-2">
          <div className="flex items-center justify-between text-[10px] text-muted-foreground">
            <span>{currentIndex + (isComplete ? 0 : 1)} / {totalPoints} Punkte</span>
            <span>{formatTime(elapsedMs)}{!isComplete && ` • ~${formatTime(estimatedRemainingMs)} verbl.`}</span>
          </div>
          <Progress value={progress * 100} className="h-1.5" />

          {/* Current point */}
          {currentPoint && isScanning && (
            <motion.div
              key={currentPoint.id}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              className="flex items-center gap-2 p-1.5 rounded bg-muted/40"
            >
              <div className="w-2.5 h-2.5 rounded-full animate-pulse" style={{ backgroundColor: getOrganColor(currentPoint.organSystem) }} />
              <div className="flex-1 min-w-0">
                <p className="text-[11px] font-medium text-foreground truncate">{currentPoint.pointName}</p>
                <p className="text-[9px] text-muted-foreground">{currentPoint.organNameDe} • {currentPoint.scanFrequency.toFixed(1)} Hz</p>
              </div>
            </motion.div>
          )}

          {/* Dysregulation summary */}
          {results.length > 0 && (
            <div className="space-y-1.5">
              <div className="flex items-center justify-between">
                <span className="text-[10px] text-muted-foreground">Dysregulationen</span>
                <Badge variant={dysregulatedCount > 0 ? 'destructive' : 'secondary'} className="text-[9px] px-1.5 py-0 h-4">
                  {dysregulatedCount > 0 && <AlertTriangle className="w-2.5 h-2.5 mr-0.5" />}
                  {dysregulatedCount} / {results.length}
                </Badge>
              </div>

              {/* Organ breakdown */}
              <div className="flex flex-wrap gap-1">
                {organSummary.map(([organ, { count, dysCount }]) => (
                  <div
                    key={organ}
                    className="flex items-center gap-1 px-1.5 py-0.5 rounded-full bg-muted/50 text-[9px]"
                  >
                    <div className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: getOrganColor(organ) }} />
                    <span className="text-foreground">{count}</span>
                    {dysCount > 0 && (
                      <span className="text-destructive font-medium">({dysCount}⚠)</span>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </motion.div>
    </AnimatePresence>
  );
}

export default NLSAutoScanOverlay;
