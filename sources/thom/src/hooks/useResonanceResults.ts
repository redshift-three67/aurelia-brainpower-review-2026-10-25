/**
 * Hook für Resonanz-Ergebnis-Persistenz (Phase 4)
 * Speichert und lädt NLS-Scan-Ergebnisse pro Session
 */
import { useState, useCallback } from 'react';
import { supabase } from '@/integrations/supabase/client';
import { toast } from 'sonner';

export interface ResonanceResult {
  id: string;
  sessionId: string;
  clientId: string;
  scanPointId: string | null;
  organSystem: string;
  organName: string;
  bodyRegion: string;
  scanFrequency: number;
  intensity: number;
  polarity: 'neutral' | 'excess' | 'deficiency';
  dysregulationScore: number;
  harmonicPattern: number[];
  notes: string | null;
  createdAt: Date;
}

export interface ResonanceSummary {
  totalPoints: number;
  avgIntensity: number;
  maxDysregulation: number;
  affectedSystems: string[];
  dominantPolarity: string;
}

export function useResonanceResults() {
  const [results, setResults] = useState<ResonanceResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const mapRow = (row: Record<string, unknown>): ResonanceResult => ({
    id: row.id as string,
    sessionId: row.session_id as string,
    clientId: row.client_id as string,
    scanPointId: row.scan_point_id as string | null,
    organSystem: row.organ_system as string,
    organName: row.organ_name as string,
    bodyRegion: row.body_region as string,
    scanFrequency: row.scan_frequency as number,
    intensity: row.intensity as number,
    polarity: row.polarity as 'neutral' | 'excess' | 'deficiency',
    dysregulationScore: row.dysregulation_score as number,
    harmonicPattern: (row.harmonic_pattern as number[]) || [],
    notes: row.notes as string | null,
    createdAt: new Date(row.created_at as string),
  });

  const saveResults = useCallback(async (
    sessionId: string,
    clientId: string,
    scanResults: Array<{
      scanPointId?: string;
      organSystem: string;
      organName: string;
      bodyRegion: string;
      scanFrequency: number;
      intensity: number;
      polarity: string;
      dysregulationScore: number;
      harmonicPattern?: number[];
    }>,
  ): Promise<boolean> => {
    if (scanResults.length === 0) return true;

    try {
      const rows = scanResults.map(r => ({
        session_id: sessionId,
        client_id: clientId,
        scan_point_id: r.scanPointId || null,
        organ_system: r.organSystem,
        organ_name: r.organName,
        body_region: r.bodyRegion,
        scan_frequency: r.scanFrequency,
        intensity: r.intensity,
        polarity: r.polarity,
        dysregulation_score: r.dysregulationScore,
        harmonic_pattern: r.harmonicPattern || [],
      }));

      const { error } = await supabase
        .from('resonance_results')
        .insert(rows);

      if (error) throw error;

      toast.success(`${scanResults.length} Resonanz-Ergebnisse gespeichert`);
      return true;
    } catch (error) {
      console.error('Error saving resonance results:', error);
      toast.error('Fehler beim Speichern der Resonanz-Ergebnisse');
      return false;
    }
  }, []);

  const loadBySession = useCallback(async (sessionId: string): Promise<ResonanceResult[]> => {
    setIsLoading(true);
    try {
      const { data, error } = await supabase
        .from('resonance_results')
        .select('*')
        .eq('session_id', sessionId)
        .order('created_at', { ascending: true });

      if (error) throw error;

      const mapped = (data || []).map(d => mapRow(d as unknown as Record<string, unknown>));
      setResults(mapped);
      return mapped;
    } catch (error) {
      console.error('Error loading resonance results:', error);
      return [];
    } finally {
      setIsLoading(false);
    }
  }, []);

  const loadByClient = useCallback(async (clientId: string): Promise<ResonanceResult[]> => {
    setIsLoading(true);
    try {
      const { data, error } = await supabase
        .from('resonance_results')
        .select('*')
        .eq('client_id', clientId)
        .order('created_at', { ascending: false })
        .limit(500);

      if (error) throw error;

      const mapped = (data || []).map(d => mapRow(d as unknown as Record<string, unknown>));
      setResults(mapped);
      return mapped;
    } catch (error) {
      console.error('Error loading client resonance results:', error);
      return [];
    } finally {
      setIsLoading(false);
    }
  }, []);

  const getSummary = useCallback((data: ResonanceResult[]): ResonanceSummary => {
    if (data.length === 0) {
      return { totalPoints: 0, avgIntensity: 0, maxDysregulation: 0, affectedSystems: [], dominantPolarity: 'neutral' };
    }

    const avgIntensity = data.reduce((sum, r) => sum + r.intensity, 0) / data.length;
    const maxDysregulation = Math.max(...data.map(r => r.dysregulationScore));
    const affectedSystems = [...new Set(data.filter(r => r.dysregulationScore > 1.5).map(r => r.organSystem))];
    
    const polarityCounts = { neutral: 0, excess: 0, deficiency: 0 };
    data.forEach(r => { polarityCounts[r.polarity] = (polarityCounts[r.polarity] || 0) + 1; });
    const dominantPolarity = Object.entries(polarityCounts).sort((a, b) => b[1] - a[1])[0][0];

    return { totalPoints: data.length, avgIntensity, maxDysregulation, affectedSystems, dominantPolarity };
  }, []);

  return {
    results,
    isLoading,
    saveResults,
    loadBySession,
    loadByClient,
    getSummary,
  };
}
