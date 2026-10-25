/**
 * TCM-Trendanalytik-Komponente
 * Phase 6: Longitudinale Analyse von Meridian-Dysregulationen über Sitzungen
 * mit Wu-Xing Element-Zyklus-Visualisierung
 */
import { useState, useEffect, useCallback, useMemo } from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, Calendar, Layers, RefreshCw } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
} from 'recharts';
import { supabase } from '@/integrations/supabase/client';
import type { Database, Json } from '@/integrations/supabase/types';

type TreatmentSessionRow = Database['public']['Tables']['treatment_sessions']['Row'];

interface TCMImbalanceSnapshot {
  element?: string;
  imbalanceScore?: number;
}

interface TCMDiagnosisSnapshot {
  imbalances?: TCMImbalanceSnapshot[];
}

interface TCMVectorSnapshot {
  stability?: number;
}

interface TCMTrendData {
  sessionDate: string;
  sessionNumber: number;
  wood: number; // Holz (Leber/Gallenblase)
  fire: number; // Feuer (Herz/Dünndarm)
  earth: number; // Erde (Milz/Magen)
  metal: number; // Metall (Lunge/Dickdarm)
  water: number; // Wasser (Niere/Blase)
  overallStability: number;
}

interface TCMTrendAnalyticsProps {
  clientId: string | null;
}

const ELEMENT_COLORS: Record<string, string> = {
  wood: '#22c55e',
  fire: '#ef4444',
  earth: '#eab308',
  metal: '#94a3b8',
  water: '#3b82f6',
};

const ELEMENT_LABELS: Record<string, string> = {
  wood: 'Holz (木)',
  fire: 'Feuer (火)',
  earth: 'Erde (土)',
  metal: 'Metall (金)',
  water: 'Wasser (水)',
};

// Sheng-Zyklus (Nährungs-Zyklus): Holz→Feuer→Erde→Metall→Wasser→Holz
const SHENG_CYCLE = ['wood', 'fire', 'earth', 'metal', 'water'];
// Ke-Zyklus (Kontroll-Zyklus): Holz→Erde, Feuer→Metall, Erde→Wasser, Metall→Holz, Wasser→Feuer
const KE_RELATIONS: [string, string][] = [
  ['wood', 'earth'], ['fire', 'metal'], ['earth', 'water'], ['metal', 'wood'], ['water', 'fire'],
];

const isRecord = (value: unknown): value is { [key: string]: Json | undefined } =>
  typeof value === 'object' && value !== null && !Array.isArray(value);

const toNumber = (value: unknown, fallback: number): number =>
  typeof value === 'number' ? value : fallback;

const parseDiagnosisSnapshot = (snapshot: Json | null): TCMDiagnosisSnapshot => {
  if (!isRecord(snapshot) || !Array.isArray(snapshot.imbalances)) return {};

  const imbalances = snapshot.imbalances
    .filter(isRecord)
    .map((imbalance) => ({
      element: typeof imbalance.element === 'string' ? imbalance.element : undefined,
      imbalanceScore: toNumber(imbalance.imbalanceScore, 0),
    }));

  return { imbalances };
};

const parseVectorSnapshot = (snapshot: Json | null): TCMVectorSnapshot => {
  if (!isRecord(snapshot)) return {};
  return { stability: toNumber(snapshot.stability, 0.5) };
};

const TCMTrendAnalytics = ({ clientId }: TCMTrendAnalyticsProps) => {
  const [trendData, setTrendData] = useState<TCMTrendData[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const loadTrends = useCallback(async () => {
    if (!clientId) return;
    setIsLoading(true);
    try {
      // Load sessions with diagnosis snapshots
      const { data: sessions, error } = await supabase
        .from('treatment_sessions')
        .select('*')
        .eq('client_id', clientId)
        .eq('status', 'completed')
        .order('session_date', { ascending: true })
        .limit(50);

      if (error) throw error;

      const trends: TCMTrendData[] = (sessions || []).map((session: TreatmentSessionRow) => {
        const diag = parseDiagnosisSnapshot(session.diagnosis_snapshot);
        const vector = parseVectorSnapshot(session.vector_snapshot);

        // Extract element scores from diagnosis or compute from vector
        const elementScores = { wood: 0.5, fire: 0.5, earth: 0.5, metal: 0.5, water: 0.5 };

        if (diag.imbalances) {
          for (const imb of diag.imbalances) {
            const el = (imb.element || '').toLowerCase();
            const score = imb.imbalanceScore || 0;
            if (el.includes('holz') || el.includes('wood')) elementScores.wood = Math.max(elementScores.wood, score);
            if (el.includes('feuer') || el.includes('fire')) elementScores.fire = Math.max(elementScores.fire, score);
            if (el.includes('erde') || el.includes('earth')) elementScores.earth = Math.max(elementScores.earth, score);
            if (el.includes('metall') || el.includes('metal')) elementScores.metal = Math.max(elementScores.metal, score);
            if (el.includes('wasser') || el.includes('water')) elementScores.water = Math.max(elementScores.water, score);
          }
        }

        const stability = vector?.stability ?? 0.5;

        return {
          sessionDate: new Date(session.session_date).toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit' }),
          sessionNumber: session.session_number,
          ...elementScores,
          overallStability: stability,
        };
      });

      setTrendData(trends);
    } catch (err) {
      console.error('TCM trend load error:', err);
    } finally {
      setIsLoading(false);
    }
  }, [clientId]);

  useEffect(() => {
    loadTrends();
  }, [loadTrends]);

  // Latest element balance for radar chart
  const latestRadar = useMemo(() => {
    if (trendData.length === 0) return null;
    const latest = trendData[trendData.length - 1];
    return SHENG_CYCLE.map(el => ({
      element: ELEMENT_LABELS[el],
      value: (latest[el as keyof TCMTrendData] as number) * 100,
      fullMark: 100,
    }));
  }, [trendData]);

  // Wu-Xing cycle analysis
  const cycleAnalysis = useMemo(() => {
    if (trendData.length === 0) return null;
    const latest = trendData[trendData.length - 1];

    const shengIssues: string[] = [];
    const keIssues: string[] = [];

    // Check Sheng (nourishing) cycle imbalances
    for (let i = 0; i < SHENG_CYCLE.length; i++) {
      const mother = SHENG_CYCLE[i];
      const child = SHENG_CYCLE[(i + 1) % 5];
      const motherVal = latest[mother as keyof TCMTrendData] as number;
      const childVal = latest[child as keyof TCMTrendData] as number;
      if (motherVal < 0.3 && childVal < 0.3) {
        shengIssues.push(`${ELEMENT_LABELS[mother]} nährt ${ELEMENT_LABELS[child]} nicht ausreichend`);
      }
    }

    // Check Ke (control) cycle
    for (const [controller, controlled] of KE_RELATIONS) {
      const cVal = latest[controller as keyof TCMTrendData] as number;
      const dVal = latest[controlled as keyof TCMTrendData] as number;
      if (cVal > 0.7 && dVal > 0.7) {
        keIssues.push(`${ELEMENT_LABELS[controller]} überkonrolliert ${ELEMENT_LABELS[controlled]}`);
      }
    }

    return { shengIssues, keIssues };
  }, [trendData]);

  if (!clientId) return null;

  return (
    <section className="py-8 px-4">
      <div className="container mx-auto max-w-7xl">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="bg-card rounded-xl border border-border p-6"
        >
          {/* Header */}
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-3">
              <TrendingUp className="w-5 h-5 text-primary" />
              <h2 className="font-display text-xl text-foreground">TCM-Trendanalytik</h2>
              <Badge variant="outline" className="text-xs">{trendData.length} Sitzungen</Badge>
            </div>
            <Button variant="outline" size="sm" onClick={loadTrends} disabled={isLoading}>
              <RefreshCw className={`w-4 h-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
              Aktualisieren
            </Button>
          </div>

          {trendData.length === 0 ? (
            <div className="text-center text-muted-foreground py-12">
              <Layers className="w-12 h-12 mx-auto mb-4 opacity-30" />
              <p>Noch keine abgeschlossenen Sitzungen für die Trendanalyse.</p>
              <p className="text-xs mt-2">Schließen Sie mindestens 2 Sitzungen ab, um Trends zu sehen.</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Line Chart: Element-Trends über Sessions */}
              <div className="lg:col-span-2">
                <h3 className="text-sm font-medium text-foreground mb-3 flex items-center gap-2">
                  <Calendar className="w-4 h-4" />
                  Element-Balance über Sitzungen
                </h3>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={trendData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                    <XAxis dataKey="sessionDate" tick={{ fontSize: 10, fill: 'hsl(var(--muted-foreground))' }} />
                    <YAxis tick={{ fontSize: 10, fill: 'hsl(var(--muted-foreground))' }} domain={[0, 1]} />
                    <Tooltip
                      contentStyle={{
                        background: 'hsl(var(--popover))',
                        border: '1px solid hsl(var(--border))',
                        borderRadius: '8px',
                        fontSize: '12px',
                      }}
                    />
                    <Legend wrapperStyle={{ fontSize: '11px' }} />
                    {SHENG_CYCLE.map(el => (
                      <Line
                        key={el}
                        type="monotone"
                        dataKey={el}
                        name={ELEMENT_LABELS[el]}
                        stroke={ELEMENT_COLORS[el]}
                        strokeWidth={2}
                        dot={{ r: 3 }}
                      />
                    ))}
                  </LineChart>
                </ResponsiveContainer>
              </div>

              {/* Radar Chart: Aktuelle Element-Balance */}
              <div>
                <h3 className="text-sm font-medium text-foreground mb-3">Aktuelle Balance</h3>
                {latestRadar && (
                  <ResponsiveContainer width="100%" height={250}>
                    <RadarChart data={latestRadar}>
                      <PolarGrid stroke="hsl(var(--border))" />
                      <PolarAngleAxis dataKey="element" tick={{ fontSize: 9, fill: 'hsl(var(--muted-foreground))' }} />
                      <PolarRadiusAxis angle={90} domain={[0, 100]} tick={{ fontSize: 8 }} />
                      <Radar
                        name="Balance"
                        dataKey="value"
                        stroke="hsl(var(--primary))"
                        fill="hsl(var(--primary))"
                        fillOpacity={0.2}
                      />
                    </RadarChart>
                  </ResponsiveContainer>
                )}

                {/* Wu-Xing Zyklus-Analyse */}
                {cycleAnalysis && (cycleAnalysis.shengIssues.length > 0 || cycleAnalysis.keIssues.length > 0) && (
                  <div className="mt-4 space-y-2">
                    <h4 className="text-xs font-medium text-foreground">Wu-Xing Zyklusstörungen</h4>
                    {cycleAnalysis.shengIssues.map((issue, i) => (
                      <div key={`s-${i}`} className="text-[10px] bg-yellow-500/10 text-yellow-400 p-2 rounded">
                        Sheng: {issue}
                      </div>
                    ))}
                    {cycleAnalysis.keIssues.map((issue, i) => (
                      <div key={`k-${i}`} className="text-[10px] bg-red-500/10 text-red-400 p-2 rounded">
                        Ke: {issue}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}
        </motion.div>
      </div>
    </section>
  );
};

export default TCMTrendAnalytics;
