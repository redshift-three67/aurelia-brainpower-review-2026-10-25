import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
};

interface HarmonizationSession {
  id: string;
  user_id: string;
  patient_id: string;
  status: string;
  duration_seconds: number;
  remaining_seconds: number | null;
  job_started_at: string | null;
  job_last_heartbeat: string | null;
  started_at: string | null;
  pulse_seconds: number | null;
  pause_seconds: number | null;
  pulse_pause_active: boolean | null;
}

serve(async (req) => {
  // Handle CORS preflight
  if (req.method === 'OPTIONS') {
    return new Response(null, { headers: corsHeaders });
  }

  try {
    const supabaseUrl = Deno.env.get('SUPABASE_URL')!;
    const supabaseKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!;
    const supabase = createClient(supabaseUrl, supabaseKey);

    console.log('🔄 Harmonization Worker gestartet');

    // ============================================
    // 0. AUTO-CLEANUP: Abgelaufene Sessions bereinigen (PULSE/PAUSE-sicher)
    // ============================================
    // Wichtig: remaining_seconds repräsentiert bei Pulse/Pause die *effektive* Behandlungszeit.
    // Daher dürfen wir NICHT stumpf (heartbeat + remaining_seconds) als Endzeit annehmen.
    // Stattdessen berechnen wir die UI-konforme effektive Restzeit seit letztem Heartbeat.
    const STALE_THRESHOLD_SECONDS = 5 * 60; // erst nach 5 Minuten „überfällig“ hart abschließen

    const getEffectiveElapsedSeconds = (elapsedRealSeconds: number, session: any): number => {
      if (!session.pulse_pause_active || !session.pulse_seconds || !session.pause_seconds) return elapsedRealSeconds;
      const cycleLength = session.pulse_seconds + session.pause_seconds;
      const cycles = Math.floor(elapsedRealSeconds / cycleLength);
      const remainder = elapsedRealSeconds % cycleLength;
      return cycles * session.pulse_seconds + Math.min(remainder, session.pulse_seconds);
    };

    const completeExpiredRunning = async (table: 'harmonization_sessions_v2' | 'morphic_field_sessions') => {
      const { data, error } = await supabase
        .from(table)
        .select('id, word, remaining_seconds, duration_seconds, job_last_heartbeat, pulse_pause_active, pulse_seconds, pause_seconds')
        .eq('status', 'running')
        .not('job_last_heartbeat', 'is', null)
        .limit(500);

      if (error) {
        console.error(`❌ Cleanup: Fehler beim Abrufen (${table}):`, error);
        return 0;
      }

      const nowMs = Date.now();
      const expired = (data || []).filter((s: any) => {
        if (!s.job_last_heartbeat) return false;
        const base = (s.remaining_seconds ?? s.duration_seconds) ?? 0;
        if (base <= 0) return false;

        const hbMs = new Date(s.job_last_heartbeat).getTime();
        const elapsedRealSeconds = Math.max(0, Math.floor((nowMs - hbMs) / 1000));
        if (elapsedRealSeconds < STALE_THRESHOLD_SECONDS) return false;

        const effectiveElapsed = getEffectiveElapsedSeconds(elapsedRealSeconds, s);
        const displayRemaining = Math.max(0, base - effectiveElapsed);
        return displayRemaining <= 0;
      });

      if (expired.length === 0) return 0;

      console.log(`🧹 Cleanup: ${expired.length} überfällige Sessions in ${table} → completed`);
      const completedAt = new Date().toISOString();

      await Promise.all(
        expired.map((s: any) =>
          supabase
            .from(table)
            .update({
              status: 'completed',
              remaining_seconds: 0,
              progress: 100,
              completed_at: completedAt,
            })
            .eq('id', s.id)
        )
      );

      return expired.length;
    };

    await completeExpiredRunning('harmonization_sessions_v2');
    await completeExpiredRunning('morphic_field_sessions');

    // ============================================
    // 1. Pending Sessions auf "running" setzen (Start)
    // ============================================
    const { data: pendingSessions, error: fetchPendingError } = await supabase
      .from('harmonization_sessions_v2')
      .select('*')
      .eq('status', 'pending')
      .is('job_started_at', null)
      .order('created_at', { ascending: true })
      .limit(25);

    if (fetchPendingError) {
      console.error('❌ Fehler beim Abrufen der Pending-Sessions:', fetchPendingError);
      throw fetchPendingError;
    }

    console.log(`📊 Pending Sessions: ${pendingSessions?.length || 0}`);

    const startResults = await Promise.all(
      (pendingSessions || []).map(async (session: HarmonizationSession) => {
        try {
          console.log(`⚡ Starte Session ${session.id}`);
          const nowIso = new Date().toISOString();

          const { error: updateError } = await supabase
            .from('harmonization_sessions_v2')
            .update({
              status: 'running',
              job_started_at: nowIso,
              job_last_heartbeat: nowIso,
              remaining_seconds: session.duration_seconds,
              started_at: nowIso,
              progress: 0,
            })
            .eq('id', session.id);

          if (updateError) {
            console.error(`❌ Update-Fehler für ${session.id}:`, updateError);
            throw updateError;
          }

          console.log(`✅ Session ${session.id} gestartet`);
          return { id: session.id, status: 'started' };
        } catch (error: any) {
          console.error(`❌ Fehler bei Session ${session.id}:`, error);
          return { id: session.id, status: 'error', error: error.message };
        }
      })
    );

    // 2. Aktive Sessions ticken lassen (Heartbeat, Restzeit, Abschluss)
    // WICHTIG: "Continuous" Sessions nutzen extrem große duration_seconds (z.B. 10 Jahre),
    // um unbegrenzte Harmonisierung zu simulieren. Diese dürfen die Tick-Pipeline nicht verstopfen.
    // Daher priorisieren wir "finite" Sessions und behandeln sehr lange Sessions separat.
    const CONTINUOUS_THRESHOLD_SECONDS = 31_536_000; // 1 Jahr

    const { data: finiteSessions, error: fetchFiniteError } = await supabase
      .from('harmonization_sessions_v2')
      .select('*')
      .eq('status', 'running')
      .lt('duration_seconds', CONTINUOUS_THRESHOLD_SECONDS)
      .order('job_last_heartbeat', { ascending: true, nullsFirst: true })
      .order('created_at', { ascending: true })
      .limit(100);

    if (fetchFiniteError) {
      console.error('❌ Fehler beim Abrufen der aktiven (finite) Sessions:', fetchFiniteError);
      throw fetchFiniteError;
    }

    const { data: continuousSessions, error: fetchContinuousError } = await supabase
      .from('harmonization_sessions_v2')
      .select('*')
      .eq('status', 'running')
      .gte('duration_seconds', CONTINUOUS_THRESHOLD_SECONDS)
      .order('job_last_heartbeat', { ascending: true, nullsFirst: true })
      .order('created_at', { ascending: true })
      .limit(25);

    if (fetchContinuousError) {
      console.error('❌ Fehler beim Abrufen der aktiven (continuous) Sessions:', fetchContinuousError);
      throw fetchContinuousError;
    }

    console.log(`⏱️ Aktive Sessions (finite): ${finiteSessions?.length || 0}`);
    console.log(`♾️ Aktive Sessions (continuous): ${continuousSessions?.length || 0}`);

    const allRunning = [...(finiteSessions || []), ...(continuousSessions || [])] as HarmonizationSession[];

    // 2a. Sessions die "running" sind aber noch keinen Heartbeat haben, initialisieren
    const uninitializedSessions = allRunning.filter((s) => !s.job_last_heartbeat);

    for (const session of uninitializedSessions) {
      const nowIso = new Date().toISOString();
      console.log(`🔧 Initialisiere Session ${session.id} mit erstem Heartbeat`);

      await supabase
        .from('harmonization_sessions_v2')
        .update({
          job_last_heartbeat: nowIso,
          job_started_at: session.job_started_at || nowIso,
          remaining_seconds: session.remaining_seconds ?? session.duration_seconds,
        })
        .eq('id', session.id);
    }

    // 2b. Continuous Sessions: nur Heartbeat aktualisieren (keine Restzeit-Berechnung)
    // → verhindert "Hängen" bei kurzen Sessions durch Worker-Limit.
    for (const session of (continuousSessions || []) as HarmonizationSession[]) {
      const nowIso = new Date().toISOString();
      await supabase
        .from('harmonization_sessions_v2')
        .update({
          job_last_heartbeat: nowIso,
        })
        .eq('id', session.id);
    }

    // Nur finite Sessions mit Heartbeat ticken
    const sessionsToTick = (finiteSessions || []).filter(
      (s: HarmonizationSession) => s.job_last_heartbeat !== null
    );

    const tickResults = await Promise.all(
      sessionsToTick.map(async (session: HarmonizationSession) => {
        try {
          const now = new Date();
          const last = new Date(session.job_last_heartbeat!);

          let elapsed = Math.floor((now.getTime() - last.getTime()) / 1000);
          if (!Number.isFinite(elapsed) || elapsed < 1) elapsed = 1;

          // Berücksichtige Impuls/Pausen-Modus
          let effectiveElapsed = elapsed;
          if (session.pulse_pause_active && session.pulse_seconds && session.pause_seconds) {
            const cycleLength = session.pulse_seconds + session.pause_seconds;
            const cycles = Math.floor(elapsed / cycleLength);
            const remainder = elapsed % cycleLength;
            
            // Nur die Impuls-Zeiten zählen als effektive Zeit
            effectiveElapsed = cycles * session.pulse_seconds;
            if (remainder <= session.pulse_seconds) {
              effectiveElapsed += remainder;
            } else {
              effectiveElapsed += session.pulse_seconds;
            }
            
            console.log(`⚡ Impuls/Pausen-Modus für ${session.id}: ${elapsed}s real → ${effectiveElapsed}s effektiv (Impuls: ${session.pulse_seconds}s, Pause: ${session.pause_seconds}s)`);
          }

          const prevRemaining = session.remaining_seconds ?? session.duration_seconds;
          const remaining = Math.max(0, (prevRemaining || 0) - effectiveElapsed);
          const duration = session.duration_seconds || 1;
          const progress = Math.min(100, Math.floor(((duration - remaining) / duration) * 100));

          if (remaining <= 0) {
            // Abschluss
            const { error: completeError } = await supabase
              .from('harmonization_sessions_v2')
              .update({
                status: 'completed',
                remaining_seconds: 0,
                progress: 100,
                completed_at: now.toISOString(),
                job_last_heartbeat: now.toISOString(),
              })
              .eq('id', session.id);

            if (completeError) {
              console.error(`❌ Abschluss-Fehler für ${session.id}:`, completeError);
              throw completeError;
            }

            console.log(`✅ Session ${session.id} abgeschlossen`);

            // Sequenziell weiterlaufen: nächstes queued Item (gleicher User + Patient) automatisch starten
            const { data: nextQueued } = await supabase
              .from('harmonization_sessions_v2')
              .select('id, duration_seconds')
              .eq('status', 'queued')
              .eq('user_id', session.user_id)
              .eq('patient_id', session.patient_id)
              .order('created_at', { ascending: true })
              .limit(1)
              .maybeSingle();

            if (nextQueued?.id) {
              const nowIso = now.toISOString();
              console.log(`➡️ Starte nächstes queued Item: ${nextQueued.id}`);

              await supabase
                .from('harmonization_sessions_v2')
                .update({
                  status: 'running',
                  job_started_at: nowIso,
                  job_last_heartbeat: nowIso,
                  started_at: nowIso,
                  remaining_seconds: nextQueued.duration_seconds,
                  progress: 0,
                })
                .eq('id', nextQueued.id);
            }

            return { id: session.id, status: 'completed' };
          } else {
            // Heartbeat + Fortschritt
            const { error: hbError } = await supabase
              .from('harmonization_sessions_v2')
              .update({
                remaining_seconds: remaining,
                progress,
                job_last_heartbeat: now.toISOString(),
              })
              .eq('id', session.id);

            if (hbError) {
              console.error(`❌ Heartbeat-Fehler für ${session.id}:`, hbError);
              throw hbError;
            }

            return { id: session.id, status: 'ticked', remaining, progress } as any;
          }
        } catch (error: any) {
          console.error(`❌ Tick-Fehler bei Session ${session.id}:`, error);
          return { id: session.id, status: 'error', error: error.message };
        }
      })
    );

    const started = startResults.filter(r => r.status === 'started').length;
    const completed = tickResults.filter(r => r.status === 'completed').length;
    const ticked = tickResults.filter(r => r.status === 'ticked').length;
    const initialized = uninitializedSessions.length;

    console.log(`✅ Worker abgeschlossen: gestartet=${started}, initialisiert=${initialized}, getickt=${ticked}, abgeschlossen=${completed}`);

    return new Response(
      JSON.stringify({
        message: 'Harmonization Worker abgeschlossen',
        started,
        initialized,
        ticked,
        completed,
        startResults,
        tickResults,
      }),
      { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );

  } catch (error) {
    console.error('❌ Worker Fehler:', error);
    return new Response(
      JSON.stringify({ error: error.message }),
      {
        status: 500,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      }
    );
  }
});
