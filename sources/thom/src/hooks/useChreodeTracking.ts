/**
 * Chreode-Pfad-Tracking Hook
 * Speichert und lädt Vektor-Trajektorien über mehrere Sessions
 */
import { useState, useCallback } from 'react';
import { supabase } from '@/integrations/supabase/client';
import type { Database } from '@/integrations/supabase/types';
import type { VectorAnalysis } from '@/services/feldengine';

type ChreodeTrajectoryRow = Database['public']['Tables']['chreode_trajectories']['Row'];
type ChreodeTrajectoryInsert = Database['public']['Tables']['chreode_trajectories']['Insert'];

export interface ChreodeTrajectoryPoint {
  id: string;
  clientId: string;
  sessionId: string;
  timestamp: Date;
  dimensions: number[];
  entropyModulation: number[];
  bifurcationRisk: number | null;
  stability: number | null;
  phase: string | null;
  chreodeAlignment: number | null;
  attractorDistance: number | null;
}

export function useChreodeTracking() {
  const [trajectories, setTrajectories] = useState<ChreodeTrajectoryPoint[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const recordPoint = useCallback(async (
    clientId: string,
    sessionId: string,
    analysis: VectorAnalysis,
    entropyModulation?: number[]
  ) => {
    try {
      const trajectory: ChreodeTrajectoryInsert = {
        client_id: clientId,
        session_id: sessionId,
        dimensions: analysis.clientVector.dimensions,
        entropy_modulation: entropyModulation || [],
        bifurcation_risk: analysis.attractorState.bifurcationRisk,
        stability: analysis.attractorState.stability,
        phase: analysis.attractorState.phase,
        chreode_alignment: analysis.attractorState.chreodeAlignment,
        attractor_distance: Math.sqrt(
          analysis.clientVector.dimensions.reduce((s, d) => s + d * d, 0)
        ),
      };

      const { error } = await supabase
        .from('chreode_trajectories')
        .insert(trajectory);

      if (error) console.error('Chreode tracking error:', error);
    } catch (err) {
      console.error('Chreode tracking error:', err);
    }
  }, []);

  const loadTrajectories = useCallback(async (clientId: string, limit = 200) => {
    setIsLoading(true);
    try {
      const { data, error } = await supabase
        .from('chreode_trajectories')
        .select('*')
        .eq('client_id', clientId)
        .order('timestamp', { ascending: true })
        .limit(limit);

      if (error) throw error;

      const mapped = (data || []).map((row: ChreodeTrajectoryRow): ChreodeTrajectoryPoint => ({
        id: row.id,
        clientId: row.client_id,
        sessionId: row.session_id,
        timestamp: new Date(row.timestamp),
        dimensions: row.dimensions,
        entropyModulation: row.entropy_modulation || [],
        bifurcationRisk: row.bifurcation_risk,
        stability: row.stability,
        phase: row.phase,
        chreodeAlignment: row.chreode_alignment,
        attractorDistance: row.attractor_distance,
      }));

      setTrajectories(mapped);
      return mapped;
    } catch (err) {
      console.error('Load trajectories error:', err);
      return [];
    } finally {
      setIsLoading(false);
    }
  }, []);

  return {
    trajectories,
    isLoading,
    recordPoint,
    loadTrajectories,
  };
}

export default useChreodeTracking;
