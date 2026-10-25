/**
 * Session Table Router
 * 
 * Routing-Utility um basierend auf source_module die korrekte Tabelle zu verwenden.
 * Dies ermöglicht vollständige Datenisolation zwischen Modulen.
 * 
 * - morphic_field → morphic_field_sessions (separate Tabelle)
 * - word_energy, copen_v2, session_transfer → harmonization_sessions_v2 (gemeinsame Tabelle)
 */

export type SourceModule = 'morphic_field' | 'word_energy' | 'copen_v2' | 'session_transfer';

export type SessionTable = 'morphic_field_sessions' | 'harmonization_sessions_v2';

/**
 * Gibt die korrekte Datenbank-Tabelle für ein gegebenes Modul zurück
 */
export function getSessionTable(sourceModule: SourceModule): SessionTable {
  switch (sourceModule) {
    case 'morphic_field':
      return 'morphic_field_sessions';
    case 'word_energy':
    case 'copen_v2':
    case 'session_transfer':
    default:
      return 'harmonization_sessions_v2';
  }
}

/**
 * Prüft ob ein Modul die separate Morphic Field Tabelle verwendet
 */
export function usesMorphicFieldTable(sourceModule: SourceModule): boolean {
  return sourceModule === 'morphic_field';
}

/**
 * Standard Session Interface für beide Tabellen
 */
export interface SessionData {
  id?: string;
  user_id: string;
  patient_id: string;
  word: string;
  copen_rate?: string | null;
  tested_potency?: string | null;
  duration_seconds: number;
  remaining_seconds?: number | null;
  progress?: number;
  status: 'queued' | 'pending' | 'running' | 'paused' | 'completed' | 'cancelled';
  started_at?: string | null;
  completed_at?: string | null;
  job_started_at?: string | null;
  job_last_heartbeat?: string | null;
  pulse_seconds?: number | null;
  pause_seconds?: number | null;
  pulse_pause_active?: boolean;
  batch_id?: string | null;
  source_module?: string;
  // Morphic Field specific (optional)
  field_intensity?: number | null;
  coherence?: number | null;
  geometric_form?: string | null;
  intention_type?: string | null;
  created_at?: string;
  updated_at?: string;
}

/**
 * Konvertiert Session-Daten für Insert in die entsprechende Tabelle
 */
export function prepareSessionInsert(
  session: Omit<SessionData, 'id' | 'created_at' | 'updated_at'>,
  sourceModule: SourceModule
): Record<string, unknown> {
  const base = {
    user_id: session.user_id,
    patient_id: session.patient_id,
    word: session.word,
    copen_rate: session.copen_rate,
    tested_potency: session.tested_potency,
    duration_seconds: session.duration_seconds,
    remaining_seconds: session.remaining_seconds,
    progress: session.progress ?? 0,
    status: session.status,
    pulse_seconds: session.pulse_seconds,
    pause_seconds: session.pause_seconds,
    pulse_pause_active: session.pulse_pause_active ?? false,
    batch_id: session.batch_id,
  };

  if (sourceModule === 'morphic_field') {
    // Für morphic_field_sessions, kein source_module Feld nötig (implizit durch Tabelle)
    return {
      ...base,
      field_intensity: session.field_intensity,
      coherence: session.coherence,
      geometric_form: session.geometric_form,
      intention_type: session.intention_type,
    };
  } else {
    // Für harmonization_sessions_v2, source_module explizit setzen
    return {
      ...base,
      source_module: sourceModule,
    };
  }
}
