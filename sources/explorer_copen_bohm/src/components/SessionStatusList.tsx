import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from '@/components/ui/alert-dialog';
import { Activity, Clock, Zap, Timer, Pause, Play, User, Square, RotateCcw } from 'lucide-react';
import { supabase } from '@/integrations/supabase/client';
import { useAuth } from '@/hooks/useAuth';
import { useToast } from '@/hooks/use-toast';

interface SessionStatus {
  id: string;
  word: string;
  status: string;
  job_last_heartbeat: string | null;
  job_started_at: string | null;
  progress: number;
  patient_id: string;
  remaining_seconds: number | null;
  duration_seconds: number;
  pulse_pause_active: boolean | null;
  pulse_seconds: number | null;
  pause_seconds: number | null;
  copen_rate: string | null;
  tested_potency: string | null;
  created_at: string;
}

interface PatientInfo {
  id: string;
  first_name: string;
  last_name: string;
}

export const SessionStatusList: React.FC = () => {
  const [sessions, setSessions] = useState<SessionStatus[]>([]);
  const [selectedSession, setSelectedSession] = useState<SessionStatus | null>(null);
  const [patientInfo, setPatientInfo] = useState<PatientInfo | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [cancelDialogOpen, setCancelDialogOpen] = useState(false);
  const [isUpdating, setIsUpdating] = useState(false);
  const [nowTs, setNowTs] = useState(() => Date.now());
  const { user } = useAuth();
  const { toast } = useToast();

  useEffect(() => {
    if (!user) return;

    const loadSessions = async () => {
      const { data, error } = await supabase
        .from('harmonization_sessions_v2')
        .select('id, word, status, job_last_heartbeat, job_started_at, progress, patient_id, remaining_seconds, duration_seconds, pulse_pause_active, pulse_seconds, pause_seconds, copen_rate, tested_potency, created_at')
        .eq('user_id', user.id)
        .in('status', ['running', 'pending', 'paused', 'queued'])
        .order('created_at', { ascending: false });

      if (!error && data) {
        setSessions(data as SessionStatus[]);
      }
    };

    loadSessions();
    const interval = setInterval(loadSessions, 5000);

    // Realtime subscription
    const channel = supabase
      .channel('session-status-list')
      .on(
        'postgres_changes',
        {
          event: '*',
          schema: 'public',
          table: 'harmonization_sessions_v2',
          filter: `user_id=eq.${user.id}`
        },
        () => loadSessions()
      )
      .subscribe();

    return () => {
      clearInterval(interval);
      supabase.removeChannel(channel);
    };
  }, [user]);

  useEffect(() => {
    const t = setInterval(() => setNowTs(Date.now()), 1000);
    return () => clearInterval(t);
  }, []);

  // Lade Patienteninfo wenn Session ausgewählt wird
  useEffect(() => {
    if (!selectedSession) {
      setPatientInfo(null);
      return;
    }

    const loadPatient = async () => {
      const { data } = await supabase
        .from('patients_v2')
        .select('id, first_name, last_name')
        .eq('id', selectedSession.patient_id)
        .maybeSingle();

      if (data) {
        setPatientInfo(data);
      }
    };

    loadPatient();
  }, [selectedSession]);

  const getWorkerStatus = (session: SessionStatus): 'active' | 'idle' | 'pending' | 'paused' | 'queued' => {
    if (session.status === 'queued') return 'queued';
    if (session.status === 'pending') return 'pending';
    if (session.status === 'paused') return 'paused';
    if (!session.job_last_heartbeat) return 'idle';

    const heartbeat = new Date(session.job_last_heartbeat);
    const now = new Date();
    const diff = now.getTime() - heartbeat.getTime();

    return diff < 120000 ? 'active' : 'idle';
  };

  const getStatusBadge = (status: 'active' | 'idle' | 'pending' | 'paused' | 'queued') => {
    const colors = {
      active: 'bg-green-500',
      idle: 'bg-yellow-500',
      pending: 'bg-blue-500',
      queued: 'bg-slate-500',
      paused: 'bg-orange-500'
    };
    const labels = {
      active: 'Aktiv',
      idle: 'Inaktiv',
      pending: 'Wartet',
      queued: 'Bereit',
      paused: 'Pausiert'
    };
    return <Badge className={colors[status]}>{labels[status]}</Badge>;
  };

  const formatDuration = (seconds: number | null): string => {
    if (seconds === null || seconds === undefined) return '--:--:--';

    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;

    if (hours > 0) {
      return `${hours}h ${minutes}m ${secs}s`;
    }
    return `${minutes}m ${secs}s`;
  };

  const getEffectiveElapsedSeconds = (elapsed: number, session: SessionStatus) => {
    if (!session.pulse_pause_active || !session.pulse_seconds || !session.pause_seconds) return elapsed;

    const cycleLength = session.pulse_seconds + session.pause_seconds;
    const cycles = Math.floor(elapsed / cycleLength);
    const remainder = elapsed % cycleLength;

    // Nur die Impuls-Zeiten zählen als effektive Zeit
    let effectiveElapsed = cycles * session.pulse_seconds;
    if (remainder <= session.pulse_seconds) {
      effectiveElapsed += remainder;
    } else {
      effectiveElapsed += session.pulse_seconds;
    }

    return effectiveElapsed;
  };

  // Determine if currently in pulse or pause phase
  const getPulsePhase = (session: SessionStatus): 'pulse' | 'pause' | null => {
    if (!session.pulse_pause_active || !session.pulse_seconds || !session.pause_seconds) return null;
    if (session.status !== 'running' || !session.job_last_heartbeat) return null;

    const heartbeatTs = new Date(session.job_last_heartbeat).getTime();
    const elapsed = Math.max(0, Math.floor((nowTs - heartbeatTs) / 1000));
    const cycleLength = session.pulse_seconds + session.pause_seconds;
    const positionInCycle = elapsed % cycleLength;

    return positionInCycle < session.pulse_seconds ? 'pulse' : 'pause';
  };

  // UI-Countdown: zeigt Restzeit auch zwischen Worker-Ticks sauber an
  const getDisplayRemainingSeconds = (session: SessionStatus) => {
    const base = session.remaining_seconds ?? session.duration_seconds;
    if (session.status !== 'running') return base;
    if (!session.job_last_heartbeat) return base;

    const heartbeatTs = new Date(session.job_last_heartbeat).getTime();
    const elapsed = Math.max(0, Math.floor((nowTs - heartbeatTs) / 1000));
    const effectiveElapsed = getEffectiveElapsedSeconds(elapsed, session);

    return Math.max(0, base - effectiveElapsed);
  };

  const handleSessionClick = (session: SessionStatus) => {
    setSelectedSession(session);
    setDialogOpen(true);
  };

  // Session pausieren
  const handlePauseSession = async (sessionId: string) => {
    setIsUpdating(true);
    try {
      const { error } = await supabase
        .from('harmonization_sessions_v2')
        .update({ status: 'paused' })
        .eq('id', sessionId);

      if (error) throw error;

      toast({
        title: "Session pausiert",
        description: "Die Harmonisierung wurde pausiert.",
      });
      
      // Session aktualisieren
      if (selectedSession) {
        setSelectedSession({ ...selectedSession, status: 'paused' });
      }
    } catch (error) {
      console.error('Fehler beim Pausieren:', error);
      toast({
        title: "Fehler",
        description: "Session konnte nicht pausiert werden.",
        variant: "destructive",
      });
    } finally {
      setIsUpdating(false);
    }
  };

  // Session fortsetzen
  const handleResumeSession = async (sessionId: string) => {
    setIsUpdating(true);
    try {
      const { error } = await supabase
        .from('harmonization_sessions_v2')
        .update({ status: 'running' })
        .eq('id', sessionId);

      if (error) throw error;

      toast({
        title: "Session fortgesetzt",
        description: "Die Harmonisierung läuft weiter.",
      });
      
      if (selectedSession) {
        setSelectedSession({ ...selectedSession, status: 'running' });
      }
    } catch (error) {
      console.error('Fehler beim Fortsetzen:', error);
      toast({
        title: "Fehler",
        description: "Session konnte nicht fortgesetzt werden.",
        variant: "destructive",
      });
    } finally {
      setIsUpdating(false);
    }
  };

  // Session sofort starten (queued/pending -> running)
  const handleStartSession = async (sessionId: string) => {
    setIsUpdating(true);
    try {
      const nowIso = new Date().toISOString();
      
      // Hole aktuelle Session-Daten für korrekte Initialisierung
      const { data: currentSession } = await supabase
        .from('harmonization_sessions_v2')
        .select('duration_seconds, remaining_seconds')
        .eq('id', sessionId)
        .maybeSingle();

      const { error } = await supabase
        .from('harmonization_sessions_v2')
        .update({ 
          status: 'running',
          job_started_at: nowIso,
          job_last_heartbeat: nowIso,
          started_at: nowIso,
          remaining_seconds: currentSession?.remaining_seconds ?? currentSession?.duration_seconds ?? 60,
          progress: 0
        })
        .eq('id', sessionId);

      if (error) throw error;

      // Worker triggern
      await supabase.functions.invoke('harmonization-worker');

      toast({
        title: "Session gestartet",
        description: "Die Harmonisierung wurde gestartet.",
      });
      
      if (selectedSession) {
        setSelectedSession({ ...selectedSession, status: 'running', progress: 0 });
      }
    } catch (error) {
      console.error('Fehler beim Starten:', error);
      toast({
        title: "Fehler",
        description: "Session konnte nicht gestartet werden.",
        variant: "destructive",
      });
    } finally {
      setIsUpdating(false);
    }
  };

  // Session abbrechen
  const handleCancelSession = async (sessionId: string) => {
    setIsUpdating(true);
    try {
      const { error } = await supabase
        .from('harmonization_sessions_v2')
        .update({ 
          status: 'cancelled',
          completed_at: new Date().toISOString()
        })
        .eq('id', sessionId);

      if (error) throw error;

      toast({
        title: "Session abgebrochen",
        description: "Die Harmonisierung wurde beendet.",
      });
      
      setCancelDialogOpen(false);
      setDialogOpen(false);
      setSelectedSession(null);
    } catch (error) {
      console.error('Fehler beim Abbrechen:', error);
      toast({
        title: "Fehler",
        description: "Session konnte nicht abgebrochen werden.",
        variant: "destructive",
      });
    } finally {
      setIsUpdating(false);
    }
  };

  if (sessions.length === 0) {
    return (
      <Card className="w-full">
        <CardHeader className="py-3">
          <CardTitle className="text-base flex items-center gap-2">
            <Activity className="w-4 h-4" />
            Session-Status
          </CardTitle>
        </CardHeader>
        <CardContent className="py-3">
          <div className="text-sm text-muted-foreground">Keine aktiven Harmonisierungen.</div>
        </CardContent>
      </Card>
    );
  }

  return (
    <>
      <Card className="w-full">
        <CardHeader className="py-3">
          <CardTitle className="text-base flex items-center gap-2">
            <Activity className="w-4 h-4" />
            Session-Status ({sessions.length} aktiv)
          </CardTitle>
        </CardHeader>
        <CardContent className="py-3">
          <div className="space-y-1">
          {sessions.map(session => {
              const workerStatus = getWorkerStatus(session);
              const pulsePhase = getPulsePhase(session);
              return (
                <div 
                  key={session.id} 
                  className="flex items-center justify-between py-2 px-3 bg-muted/50 rounded text-xs cursor-pointer hover:bg-muted/80 transition-colors"
                  onClick={() => handleSessionClick(session)}
                >
                  <div className="flex-1 min-w-0 mr-2">
                    <div className="font-medium break-words line-clamp-1">{session.word}</div>
                    <div className="text-muted-foreground flex items-center gap-2 mt-0.5">
                      <span>{session.progress}%</span>
                      <span className="flex items-center gap-1">
                        <Timer className="w-3 h-3" />
                        {formatDuration(getDisplayRemainingSeconds(session))}
                      </span>
                      {session.pulse_pause_active && (
                        <span className="flex items-center gap-1">
                          {pulsePhase === 'pulse' ? (
                            <Zap className="w-3 h-3 text-green-400 animate-pulse" />
                          ) : pulsePhase === 'pause' ? (
                            <Pause className="w-3 h-3 text-orange-400 animate-pulse" />
                          ) : (
                            <Zap className="w-3 h-3 text-purple-400" />
                          )}
                          <span className={pulsePhase === 'pulse' ? 'text-green-400' : pulsePhase === 'pause' ? 'text-orange-400' : 'text-purple-400'}>
                            P/P
                          </span>
                        </span>
                      )}
                    </div>
                  </div>
                  <div>
                    {getStatusBadge(workerStatus)}
                  </div>
                </div>
              );
            })}
          </div>
          <div className="text-xs text-muted-foreground mt-2 text-center">
            Klicken für Details
          </div>
        </CardContent>
      </Card>

      {/* Session Detail Dialog */}
      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Activity className="w-5 h-5" />
              Session-Details
            </DialogTitle>
          </DialogHeader>
          
          {selectedSession && (
            <div className="space-y-4">
              {/* Wort/Rate */}
              <div className="p-3 bg-muted/30 rounded-lg">
                <div className="text-xs text-muted-foreground mb-1">Wort / Rate</div>
                <div className="font-medium break-words">{selectedSession.word}</div>
              </div>

              {/* Patient */}
              {patientInfo && (
                <div className="flex items-center gap-2 p-3 bg-muted/30 rounded-lg">
                  <User className="w-4 h-4 text-blue-500" />
                  <div>
                    <div className="text-xs text-muted-foreground">Patient</div>
                    <div className="font-medium">{patientInfo.first_name} {patientInfo.last_name}</div>
                  </div>
                </div>
              )}

              {/* Fortschritt */}
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Fortschritt</span>
                  <span className="font-semibold">{selectedSession.progress}%</span>
                </div>
                <Progress value={selectedSession.progress} className="h-3" />
              </div>

              {/* Zeit-Informationen */}
              <div className="grid grid-cols-2 gap-3">
                <div className="p-3 bg-muted/30 rounded-lg">
                  <div className="flex items-center gap-1.5 text-xs text-muted-foreground mb-1">
                    <Timer className="w-3 h-3" />
                    Verbleibend
                  </div>
                  <div className="font-semibold text-lg">{formatDuration(getDisplayRemainingSeconds(selectedSession))}</div>
                </div>
                <div className="p-3 bg-muted/30 rounded-lg">
                  <div className="flex items-center gap-1.5 text-xs text-muted-foreground mb-1">
                    <Clock className="w-3 h-3" />
                    Gesamtdauer
                  </div>
                  <div className="font-semibold text-lg">{formatDuration(selectedSession.duration_seconds)}</div>
                </div>
              </div>

              {/* Pulse/Pause Modus */}
              <div className="p-3 bg-muted/30 rounded-lg">
                <div className="flex items-center gap-2 mb-2">
                  <Zap className={`w-4 h-4 ${selectedSession.pulse_pause_active ? 'text-purple-500' : 'text-muted-foreground'}`} />
                  <span className="text-sm font-medium">Pulse/Pause Modus</span>
                  <Badge className={selectedSession.pulse_pause_active ? 'bg-purple-500' : 'bg-muted'}>
                    {selectedSession.pulse_pause_active ? 'Aktiv' : 'Inaktiv'}
                  </Badge>
                </div>
                
                {selectedSession.pulse_pause_active && (
                  <div className="grid grid-cols-2 gap-3 mt-2">
                    <div className="flex items-center gap-2 text-sm">
                      <Play className="w-4 h-4 text-green-500" />
                      <span>Impuls: {selectedSession.pulse_seconds}s</span>
                    </div>
                    <div className="flex items-center gap-2 text-sm">
                      <Pause className="w-4 h-4 text-orange-500" />
                      <span>Pause: {selectedSession.pause_seconds}s</span>
                    </div>
                  </div>
                )}
              </div>

              {/* Zusätzliche Infos */}
              <div className="grid grid-cols-2 gap-3 text-sm">
                {selectedSession.copen_rate && (
                  <div className="p-2 bg-muted/30 rounded">
                    <div className="text-xs text-muted-foreground">Klienten-Rate</div>
                    <div className="font-mono font-medium">{selectedSession.copen_rate}</div>
                  </div>
                )}
                {selectedSession.tested_potency && (
                  <div className="p-2 bg-muted/30 rounded">
                    <div className="text-xs text-muted-foreground">Potenz</div>
                    <div className="font-medium">{selectedSession.tested_potency}</div>
                  </div>
                )}
              </div>

              {/* Worker-Status */}
              <div className="flex items-center justify-between p-3 bg-muted/30 rounded-lg">
                <div className="text-sm">Worker-Status</div>
                {getStatusBadge(getWorkerStatus(selectedSession))}
              </div>

              {/* Letzter Heartbeat */}
              {selectedSession.job_last_heartbeat && (
                <div className="text-xs text-muted-foreground text-center">
                  Letzter Heartbeat: {new Date(selectedSession.job_last_heartbeat).toLocaleString('de-DE')}
                </div>
              )}

              {/* Aktions-Buttons */}
              <DialogFooter className="flex-col sm:flex-row gap-2 pt-4 border-t">
                {selectedSession.status === 'running' && (
                  <Button 
                    variant="outline" 
                    onClick={() => handlePauseSession(selectedSession.id)}
                    disabled={isUpdating}
                    className="w-full sm:w-auto"
                  >
                    <Pause className="w-4 h-4 mr-2" />
                    Pausieren
                  </Button>
                )}
                
                {selectedSession.status === 'paused' && (
                  <Button 
                    variant="outline" 
                    onClick={() => handleResumeSession(selectedSession.id)}
                    disabled={isUpdating}
                    className="w-full sm:w-auto"
                  >
                    <Play className="w-4 h-4 mr-2" />
                    Fortsetzen
                  </Button>
                )}
                
                {(selectedSession.status === 'pending' || selectedSession.status === 'queued') && (
                  <Button 
                    variant="outline" 
                    onClick={() => handleStartSession(selectedSession.id)}
                    disabled={isUpdating}
                    className="w-full sm:w-auto"
                  >
                    <RotateCcw className="w-4 h-4 mr-2" />
                    Sofort starten
                  </Button>
                )}
                
                <Button 
                  variant="destructive" 
                  onClick={() => setCancelDialogOpen(true)}
                  disabled={isUpdating}
                  className="w-full sm:w-auto"
                >
                  <Square className="w-4 h-4 mr-2" />
                  Abbrechen
                </Button>
              </DialogFooter>
            </div>
          )}
        </DialogContent>
      </Dialog>

      {/* Cancel Confirmation Dialog */}
      <AlertDialog open={cancelDialogOpen} onOpenChange={setCancelDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Session abbrechen?</AlertDialogTitle>
            <AlertDialogDescription>
              Möchten Sie diese Harmonisierungs-Session wirklich abbrechen? 
              Diese Aktion kann nicht rückgängig gemacht werden.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Zurück</AlertDialogCancel>
            <AlertDialogAction 
              onClick={() => selectedSession && handleCancelSession(selectedSession.id)}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              Abbrechen
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  );
};
