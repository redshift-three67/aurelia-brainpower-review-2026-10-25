/**
 * Hook für Behandlungs-Archivierung
 * Speichert und lädt Behandlungshistorie für Klienten
 */
import { useState, useCallback } from 'react';
import { supabase } from '@/integrations/supabase/client';
import { toast } from 'sonner';
import type { TreatmentPoint } from './useTreatmentSequence';
import type { DiagnosisResult } from './useMeridianDiagnosis';

export interface TreatmentRecord {
  id: string;
  clientId: string;
  pointCount: number;
  totalDuration: number;
  pattern: string;
  improvementScore: number;
  meridianIds: string[];
  createdAt: Date;
}

export function useTreatmentArchive() {
  const [records, setRecords] = useState<TreatmentRecord[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const saveTreatment = useCallback(async (
    clientId: string,
    points: TreatmentPoint[],
    diagnosis: DiagnosisResult,
    stabilityScore: number
  ): Promise<TreatmentRecord | null> => {
    try {
      const totalDuration = points.reduce((sum, p) => sum + p.duration, 0);
      const meridianIds = [...new Set(points.map(p => p.meridianId))];

      const { data, error } = await supabase
        .from('harmonization_jobs')
        .insert({
          client_id: clientId,
          job_type: 'meridian_sequence',
          status: 'completed',
          progress: 100,
          target_frequencies: points.map(p => p.frequency),
          result_data: {
            pointCount: points.length,
            totalDuration,
            pattern: diagnosis.overallPattern,
            meridianIds,
            points: points.map(p => ({ id: p.id, meridianId: p.meridianId, frequency: p.frequency })),
          },
          completed_at: new Date().toISOString(),
        })
        .select()
        .single();

      if (error) throw error;

      const record: TreatmentRecord = {
        id: data.id,
        clientId: data.client_id,
        pointCount: points.length,
        totalDuration,
        pattern: diagnosis.overallPattern,
        improvementScore: stabilityScore,
        meridianIds,
        createdAt: new Date(data.created_at),
      };

      setRecords(prev => [record, ...prev]);
      return record;
    } catch (error) {
      console.error('Error saving treatment:', error);
      return null;
    }
  }, []);

  const loadTreatments = useCallback(async (clientId: string): Promise<TreatmentRecord[]> => {
    setIsLoading(true);
    try {
      const { data, error } = await supabase
        .from('harmonization_jobs')
        .select('*')
        .eq('client_id', clientId)
        .eq('job_type', 'meridian_sequence')
        .eq('status', 'completed')
        .order('created_at', { ascending: false })
        .limit(20);

      if (error) throw error;

      const mappedRecords: TreatmentRecord[] = (data || []).map((job) => {
        const resultData = job.result_data as Record<string, unknown> || {};
        return {
          id: job.id,
          clientId: job.client_id,
          pointCount: (resultData.pointCount as number) || 0,
          totalDuration: (resultData.totalDuration as number) || 0,
          pattern: (resultData.pattern as string) || 'Unbekannt',
          improvementScore: job.progress ? job.progress / 100 : 0,
          meridianIds: (resultData.meridianIds as string[]) || [],
          createdAt: new Date(job.created_at),
        };
      });

      setRecords(mappedRecords);
      return mappedRecords;
    } catch (error) {
      console.error('Error loading treatments:', error);
      return [];
    } finally {
      setIsLoading(false);
    }
  }, []);

  return {
    records,
    isLoading,
    saveTreatment,
    loadTreatments,
  };
}

export default useTreatmentArchive;
