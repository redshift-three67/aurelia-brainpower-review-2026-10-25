/**
 * Session-Management Hook
 * Erstellt, lädt und verwaltet Behandlungssitzungen für Klienten
 */
import { useState, useCallback } from 'react';
import { supabase } from '@/integrations/supabase/client';
import { toast } from 'sonner';
import type { VectorAnalysis } from '@/services/feldengine';
import type { DiagnosisResult } from '@/hooks/useMeridianDiagnosis';

export interface TreatmentSession {
  id: string;
  clientId: string;
  sessionNumber: number;
  sessionDate: Date;
  status: 'active' | 'completed' | 'cancelled';
  notes: string | null;
  vectorSnapshot: Record<string, unknown> | null;
  diagnosisSnapshot: Record<string, unknown> | null;
  treatmentSummary: Record<string, unknown> | null;
  durationSeconds: number | null;
  createdAt: Date;
}

export function useSessionManagement() {
  const [sessions, setSessions] = useState<TreatmentSession[]>([]);
  const [activeSession, setActiveSession] = useState<TreatmentSession | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const mapRow = (row: Record<string, unknown>): TreatmentSession => ({
    id: row.id as string,
    clientId: row.client_id as string,
    sessionNumber: row.session_number as number,
    sessionDate: new Date(row.session_date as string),
    status: row.status as 'active' | 'completed' | 'cancelled',
    notes: row.notes as string | null,
    vectorSnapshot: row.vector_snapshot as Record<string, unknown> | null,
    diagnosisSnapshot: row.diagnosis_snapshot as Record<string, unknown> | null,
    treatmentSummary: row.treatment_summary as Record<string, unknown> | null,
    durationSeconds: row.duration_seconds as number | null,
    createdAt: new Date(row.created_at as string),
  });

  const loadSessions = useCallback(async (clientId: string): Promise<TreatmentSession[]> => {
    setIsLoading(true);
    try {
      const { data, error } = await supabase
        .from('treatment_sessions')
        .select('*')
        .eq('client_id', clientId)
        .order('session_date', { ascending: false })
        .limit(50);

      if (error) throw error;

      const mapped = (data || []).map((d) => mapRow(d as unknown as Record<string, unknown>));
      setSessions(mapped);
      return mapped;
    } catch (error) {
      console.error('Error loading sessions:', error);
      return [];
    } finally {
      setIsLoading(false);
    }
  }, []);

  const startSession = useCallback(async (
    clientId: string,
    vectorAnalysis?: VectorAnalysis | null,
    notes?: string,
  ): Promise<TreatmentSession | null> => {
    try {
      // Determine next session number
      const { count } = await supabase
        .from('treatment_sessions')
        .select('*', { count: 'exact', head: true })
        .eq('client_id', clientId);

      const sessionNumber = (count || 0) + 1;

      const vectorSnapshot = vectorAnalysis ? {
        dimensions: vectorAnalysis.clientVector.dimensions,
        stability: vectorAnalysis.attractorState.stability,
        phase: vectorAnalysis.attractorState.phase,
        bifurcationRisk: vectorAnalysis.attractorState.bifurcationRisk,
      } : null;

      const { data, error } = await supabase
        .from('treatment_sessions')
        .insert({
          client_id: clientId,
          session_number: sessionNumber,
          status: 'active',
          notes: notes || null,
          vector_snapshot: vectorSnapshot,
        })
        .select()
        .single();

      if (error) throw error;

      const session = mapRow(data as unknown as Record<string, unknown>);
      setActiveSession(session);
      setSessions(prev => [session, ...prev]);
      toast.success(`Sitzung #${sessionNumber} gestartet`);
      return session;
    } catch (error) {
      console.error('Error starting session:', error);
      toast.error('Fehler beim Starten der Sitzung');
      return null;
    }
  }, []);

  const completeSession = useCallback(async (
    sessionId: string,
    diagnosisResult?: DiagnosisResult | null,
    treatmentSummary?: Record<string, unknown>,
    durationSeconds?: number,
  ): Promise<boolean> => {
    try {
      const updates: Record<string, unknown> = {
        status: 'completed',
        completed_at: new Date().toISOString(),
      };

      if (diagnosisResult) {
        updates.diagnosis_snapshot = {
          overallPattern: diagnosisResult.overallPattern,
          imbalanceCount: diagnosisResult.imbalances.length,
          imbalances: diagnosisResult.imbalances.map(i => ({
            meridianId: i.meridianId,
            meridianName: i.meridianName,
            element: i.element,
            imbalanceType: i.imbalanceType,
            imbalanceScore: i.imbalanceScore,
          })),
        };
      }

      if (treatmentSummary) updates.treatment_summary = treatmentSummary;
      if (durationSeconds) updates.duration_seconds = durationSeconds;

      const { error } = await supabase
        .from('treatment_sessions')
        .update(updates)
        .eq('id', sessionId);

      if (error) throw error;

      setSessions(prev => prev.map(s =>
        s.id === sessionId ? { ...s, status: 'completed' as const, durationSeconds: durationSeconds || null } : s
      ));

      if (activeSession?.id === sessionId) {
        setActiveSession(null);
      }

      toast.success('Sitzung abgeschlossen');
      return true;
    } catch (error) {
      console.error('Error completing session:', error);
      return false;
    }
  }, [activeSession]);

  return {
    sessions,
    activeSession,
    isLoading,
    loadSessions,
    startSession,
    completeSession,
    setActiveSession,
  };
}

export default useSessionManagement;
