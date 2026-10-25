/**
 * BifurcationWarningWidget – Echtzeit-Warnsignal für Bifurkationsrisiko
 * Zeigt Risiko-Gauge, Varianz/Autokorrelation und empfohlene Stabilisierungsmaßnahmen
 */
import { useState, useEffect, useRef, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { AlertTriangle, Activity, Shield, TrendingUp, TrendingDown, Minus, Zap } from 'lucide-react';
import { BifurcationDetector } from '@/services/feldengine/BifurcationDetector';
import type { BifurcationEvent, DetectorStatistics } from '@/services/feldengine/BifurcationDetector';
import type { VectorAnalysis } from '@/services/feldengine';

interface BifurcationWarningWidgetProps {
  vectorAnalysis: VectorAnalysis | null;
}

const ACTION_LABELS: Record<string, { label: string; color: string; icon: typeof Shield }> = {
  'stabilize_with_10hz_alpha': { label: '10 Hz Alpha-Stabilisierung', color: 'text-blue-400', icon: Shield },
  'reduce_frequency_intensity': { label: 'Frequenzintensität reduzieren', color: 'text-yellow-400', icon: TrendingDown },
  'apply_schumann_grounding': { label: 'Schumann-Erdung (7.83 Hz)', color: 'text-green-400', icon: Zap },
  'pause_and_reassess': { label: 'Pause & Neubewertung', color: 'text-red-400', icon: AlertTriangle },
  'continue_monitoring': { label: 'Weiter beobachten', color: 'text-muted-foreground', icon: Activity },
};

const TYPE_LABELS: Record<string, string> = {
  'cusp_bifurcation': 'Kuspen-Bifurkation',
  'fold_bifurcation': 'Falten-Bifurkation',
  'critical_slowing_down': 'Kritische Verlangsamung',
  'flickering': 'Flickering',
};

const DIMENSION_NAMES = ['Körperlich', 'Emotional', 'Mental', 'Energie', 'Stress'];

const BifurcationWarningWidget = ({ vectorAnalysis }: BifurcationWarningWidgetProps) => {
  const detectorRef = useRef<BifurcationDetector>(new BifurcationDetector());
  const [stats, setStats] = useState<DetectorStatistics | null>(null);
  const [currentEvent, setCurrentEvent] = useState<BifurcationEvent | null>(null);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // Feed vector data into detector
  useEffect(() => {
    if (!vectorAnalysis) {
      detectorRef.current.reset();
      setStats(null);
      setCurrentEvent(null);
      return;
    }

    // Sample every 500ms with slight noise to simulate real-time
    intervalRef.current = setInterval(() => {
      const dims = vectorAnalysis.clientVector.dimensions;
      // Add micro-noise to simulate live sampling
      const noisyDims = dims.map(d => d + (Math.random() - 0.5) * 0.02);
      
      const event = detectorRef.current.detect(noisyDims);
      setStats(detectorRef.current.getStatistics());
      if (event) setCurrentEvent(event);
    }, 500);

    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [vectorAnalysis]);

  const risk = stats?.lastEvent?.risk ?? detectorRef.current.getCurrentRisk();
  const riskPercent = Math.round(risk * 100);

  const riskColor = risk > 0.7 ? 'text-red-400' : risk > 0.4 ? 'text-yellow-400' : 'text-green-400';
  const riskBg = risk > 0.7 ? 'border-red-500/30' : risk > 0.4 ? 'border-yellow-500/20' : 'border-border';
  const trendIcon = stats?.riskTrend === 'increasing' ? TrendingUp :
                    stats?.riskTrend === 'decreasing' ? TrendingDown : Minus;
  const TrendIcon = trendIcon;

  if (!vectorAnalysis) return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={`bg-card rounded-lg border ${riskBg} p-4 transition-colors duration-500`}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <AlertTriangle className={`w-4 h-4 ${riskColor}`} />
          <h3 className="font-medium text-foreground text-sm">Bifurkations-Detektor</h3>
        </div>
        <div className="flex items-center gap-1">
          <TrendIcon className={`w-3 h-3 ${
            stats?.riskTrend === 'increasing' ? 'text-red-400' :
            stats?.riskTrend === 'decreasing' ? 'text-green-400' : 'text-muted-foreground'
          }`} />
          <span className="text-xs text-muted-foreground">
            {stats?.samplesCollected ?? 0} Samples
          </span>
        </div>
      </div>

      {/* Risk Gauge */}
      <div className="mb-3">
        <div className="flex justify-between text-xs mb-1">
          <span className="text-muted-foreground">Bifurkationsrisiko</span>
          <span className={`font-mono font-bold ${riskColor}`}>{riskPercent}%</span>
        </div>
        <div className="h-2 bg-muted rounded-full overflow-hidden">
          <motion.div
            className={`h-full rounded-full ${
              risk > 0.7 ? 'bg-gradient-to-r from-orange-500 to-red-500' :
              risk > 0.4 ? 'bg-gradient-to-r from-yellow-500 to-orange-500' :
              'bg-gradient-to-r from-green-500 to-emerald-400'
            }`}
            initial={{ width: 0 }}
            animate={{ width: `${riskPercent}%` }}
            transition={{ duration: 0.5 }}
          />
        </div>
      </div>

      {/* 3 Indicators */}
      <div className="grid grid-cols-3 gap-2 mb-3">
        <div className="bg-muted/30 rounded p-2 text-center">
          <div className="text-[10px] text-muted-foreground mb-1">Varianz</div>
          <div className="text-xs font-mono text-foreground">
            {stats?.currentVariance.length
              ? (stats.currentVariance.reduce((a, b) => a + b, 0) / stats.currentVariance.length).toFixed(3)
              : '—'}
          </div>
        </div>
        <div className="bg-muted/30 rounded p-2 text-center">
          <div className="text-[10px] text-muted-foreground mb-1">Autokorr.</div>
          <div className="text-xs font-mono text-foreground">
            {stats?.currentAutocorrelation.length
              ? (stats.currentAutocorrelation.reduce((a, b) => a + b, 0) / stats.currentAutocorrelation.length).toFixed(3)
              : '—'}
          </div>
        </div>
        <div className="bg-muted/30 rounded p-2 text-center">
          <div className="text-[10px] text-muted-foreground mb-1">Flickering</div>
          <div className="text-xs font-mono text-foreground">
            {stats?.currentFlickering?.toFixed(3) ?? '—'}
          </div>
        </div>
      </div>

      {/* Active Event */}
      <AnimatePresence>
        {currentEvent && currentEvent.risk > 0.3 && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="border-t border-border pt-3 space-y-2"
          >
            <div className="flex items-center gap-2">
              <span className="text-xs font-medium text-foreground">
                {TYPE_LABELS[currentEvent.type] ?? currentEvent.type}
              </span>
              {currentEvent.estimatedTimeToEvent < Infinity && (
                <span className="text-[10px] text-muted-foreground bg-muted/50 px-1.5 py-0.5 rounded">
                  ~{Math.round(currentEvent.estimatedTimeToEvent)}s
                </span>
              )}
            </div>

            {/* Affected Dimensions */}
            {currentEvent.affectedDimensions.length > 0 && (
              <div className="flex gap-1 flex-wrap">
                {currentEvent.affectedDimensions.map(idx => (
                  <span key={idx} className="text-[10px] bg-red-500/10 text-red-400 px-1.5 py-0.5 rounded">
                    {DIMENSION_NAMES[idx] ?? `D${idx}`}
                  </span>
                ))}
              </div>
            )}

            {/* Recommended Action */}
            {(() => {
              const actionInfo = ACTION_LABELS[currentEvent.recommendedAction];
              if (!actionInfo) return null;
              const ActionIcon = actionInfo.icon;
              return (
                <div className={`flex items-center gap-2 p-2 bg-muted/20 rounded ${actionInfo.color}`}>
                  <ActionIcon className="w-3 h-3" />
                  <span className="text-xs">{actionInfo.label}</span>
                </div>
              );
            })()}
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};

export default BifurcationWarningWidget;
