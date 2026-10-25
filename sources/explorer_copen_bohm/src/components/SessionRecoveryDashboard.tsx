import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Activity, Clock, Zap, AlertTriangle, ChevronRight, X, CheckCircle2, Pause, Play, Square } from 'lucide-react';
import { supabase } from '@/integrations/supabase/client';
import { useNavigate } from 'react-router-dom';
import { format, formatDistanceToNow } from 'date-fns';
import { de } from 'date-fns/locale';
import { toast } from 'sonner';

interface ActiveSession {
  id: string;
  word: string;
  status: string;
  duration_seconds: number;
  remaining_seconds: number | null;
  progress: number;
  patient_id: string;
  source_module: string | null;
  created_at: string;
  started_at: string | null;
  job_last_heartbeat: string | null;
  pulse_pause_active: boolean | null;
}

interface PatientInfo {
  id: string;
  first_name: string;
  last_name: string;
}

export type SourceModuleFilter = 'all' | 'morphic_field' | 'copen_v2' | 'word_energy' | 'session_transfer';

interface SessionRecoveryDashboardProps {
  onDismiss?: () => void;
  sourceModuleFilter?: SourceModuleFilter | SourceModuleFilter[];
  showControls?: boolean;
  title?: string;
  description?: string;
  compact?: boolean;
  patientFilter?: string | null; // Wenn gesetzt, nur Sessions dieses Patienten anzeigen
}

const SessionRecoveryDashboard: React.FC<SessionRecoveryDashboardProps> = ({ 
  onDismiss, 
  sourceModuleFilter = 'all',
  showControls = false,
  title = 'Aktive Harmonisierungen',
  description,
  compact = false,
  patientFilter = null
}) => {
  const navigate = useNavigate();
  const [sessions, setSessions] = useState<ActiveSession[]>([]);
  const [patients, setPatients] = useState<Record<string, PatientInfo>>({});
  const [loading, setLoading] = useState(true);
  const [dismissed, setDismissed] = useState(false);

  useEffect(() => {
    loadActiveSessions();
    
    // Realtime subscription für Updates
    const channel = supabase
      .channel('session-recovery-updates')
      .on('postgres_changes', { event: '*', schema: 'public', table: 'harmonization_sessions_v2' }, () => {
        loadActiveSessions();
      })
      .on('postgres_changes', { event: '*', schema: 'public', table: 'morphic_field_sessions' }, () => {
        loadActiveSessions();
      })
      .subscribe();
    
    return () => {
      supabase.removeChannel(channel);
    };
  }, [sourceModuleFilter, patientFilter]);

  const loadActiveSessions = async () => {
    try {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) return;

      // Lade Sessions aus beiden Tabellen
      const [harmonizationResult, morphicResult] = await Promise.all([
        supabase
          .from('harmonization_sessions_v2')
          .select('*')
          .eq('user_id', user.id)
          .in('status', ['running', 'pending', 'queued', 'paused'])
          .order('created_at', { ascending: false }),
        supabase
          .from('morphic_field_sessions')
          .select('*')
          .eq('user_id', user.id)
          .in('status', ['running', 'pending', 'queued', 'paused'])
          .order('created_at', { ascending: false })
      ]);

      let allSessions = [
        ...(harmonizationResult.data || []),
        ...(morphicResult.data || []).map(s => ({ ...s, source_module: 'morphic_field' }))
      ];

      // Filter nach source_module wenn angegeben
      if (sourceModuleFilter !== 'all') {
        const filters = Array.isArray(sourceModuleFilter) ? sourceModuleFilter : [sourceModuleFilter];
        allSessions = allSessions.filter(s => {
          const module = s.source_module || 'word_energy';
          return filters.includes(module as SourceModuleFilter);
        });
      }

      // Filter nach Patient wenn angegeben
      if (patientFilter) {
        allSessions = allSessions.filter(s => s.patient_id === patientFilter);
      }

      setSessions(allSessions);

      // Lade Patienten-Info
      const patientIds = [...new Set(allSessions.map(s => s.patient_id))];
      if (patientIds.length > 0) {
        const { data: patientsData } = await supabase
          .from('patients_v2')
          .select('id, first_name, last_name')
          .in('id', patientIds);

        if (patientsData) {
          const patientMap: Record<string, PatientInfo> = {};
          patientsData.forEach(p => {
            patientMap[p.id] = p;
          });
          setPatients(patientMap);
        }
      }
    } catch (error) {
      console.error('Fehler beim Laden der Sessions:', error);
    } finally {
      setLoading(false);
    }
  };

  const getModuleLabel = (source: string | null) => {
    switch (source) {
      case 'morphic_field': return 'Morphisches Feld';
      case 'word_energy': return 'Wortenergie';
      case 'copen_v2': return 'Copen V2';
      case 'session_transfer': return 'Transfer';
      default: return 'Harmonisierung';
    }
  };

  const getModuleRoute = (source: string | null) => {
    switch (source) {
      case 'morphic_field': return '/morphic-field';
      case 'copen_v2': return '/copen-visualisierung-v2';
      default: return '/copen-visualisierung-v2';
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'running':
        return <Badge className="bg-green-500/20 text-green-400 border-green-500/30">Aktiv</Badge>;
      case 'pending':
        return <Badge className="bg-yellow-500/20 text-yellow-400 border-yellow-500/30">Wartend</Badge>;
      case 'queued':
        return <Badge className="bg-blue-500/20 text-blue-400 border-blue-500/30">Eingereiht</Badge>;
      case 'paused':
        return <Badge className="bg-orange-500/20 text-orange-400 border-orange-500/30">Pausiert</Badge>;
      default:
        return <Badge variant="secondary">{status}</Badge>;
    }
  };

  const formatDuration = (seconds: number) => {
    if (seconds >= 86400) {
      return `${Math.floor(seconds / 86400)}d ${Math.floor((seconds % 86400) / 3600)}h`;
    } else if (seconds >= 3600) {
      return `${Math.floor(seconds / 3600)}h ${Math.floor((seconds % 3600) / 60)}m`;
    } else {
      return `${Math.floor(seconds / 60)}m ${seconds % 60}s`;
    }
  };

  const handleDismiss = () => {
    setDismissed(true);
    onDismiss?.();
  };

  const handleNavigate = (session: ActiveSession) => {
    navigate(getModuleRoute(session.source_module));
  };

  // Session-Steuerungsfunktionen
  const getTableForSession = (session: ActiveSession) => {
    return session.source_module === 'morphic_field' ? 'morphic_field_sessions' : 'harmonization_sessions_v2';
  };

  const handlePauseSession = async (session: ActiveSession) => {
    const table = getTableForSession(session);
    const { error } = await supabase
      .from(table)
      .update({ status: 'paused' })
      .eq('id', session.id);
    
    if (error) {
      toast.error('Fehler beim Pausieren');
    } else {
      toast.success('Session pausiert');
      loadActiveSessions();
    }
  };

  const handleResumeSession = async (session: ActiveSession) => {
    const table = getTableForSession(session);
    const { error } = await supabase
      .from(table)
      .update({ status: 'running', started_at: new Date().toISOString() })
      .eq('id', session.id);
    
    if (error) {
      toast.error('Fehler beim Fortsetzen');
    } else {
      toast.success('Session fortgesetzt');
      loadActiveSessions();
    }
  };

  const handleCancelSession = async (session: ActiveSession) => {
    const table = getTableForSession(session);
    const { error } = await supabase
      .from(table)
      .update({ status: 'cancelled' })
      .eq('id', session.id);
    
    if (error) {
      toast.error('Fehler beim Abbrechen');
    } else {
      toast.success('Session abgebrochen');
      loadActiveSessions();
    }
  };

  if (dismissed) {
    return null;
  }

  // Zeige Ladezustand oder leeren Zustand wenn showControls aktiv ist (für Modul-spezifische Dashboards)
  if (!showControls && (loading || sessions.length === 0)) {
    return null;
  }

  const runningSessions = sessions.filter(s => s.status === 'running');
  const pendingSessions = sessions.filter(s => s.status === 'pending' || s.status === 'queued');
  const pausedSessions = sessions.filter(s => s.status === 'paused');

  const totalRemaining = sessions.reduce((acc, s) => {
    if (s.status === 'running' && s.remaining_seconds) {
      return Math.max(acc, s.remaining_seconds);
    }
    if (['pending', 'queued', 'paused'].includes(s.status)) {
      return acc + (s.remaining_seconds ?? s.duration_seconds);
    }
    return acc;
  }, 0);

  const dynamicDescription = description || `${sessions.length} Session${sessions.length !== 1 ? 's' : ''} ${sourceModuleFilter === 'all' ? 'laufen im Hintergrund weiter' : 'in diesem Modul'}`;

  return (
    <Card className={`border-primary/30 bg-gradient-to-br from-primary/5 to-background shadow-lg animate-in slide-in-from-top-2 duration-500 ${compact ? 'p-2' : ''}`}>
      <CardHeader className={compact ? 'pb-2 pt-3 px-3' : 'pb-3'}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="relative">
              <Activity className={`${compact ? 'w-5 h-5' : 'w-6 h-6'} text-primary animate-pulse`} />
              {runningSessions.length > 0 && (
                <div className="absolute -top-1 -right-1 w-3 h-3 bg-green-500 rounded-full animate-ping" />
              )}
            </div>
            <div>
              <CardTitle className={compact ? 'text-base' : 'text-lg'}>{title}</CardTitle>
              <CardDescription className={compact ? 'text-xs' : ''}>
                {dynamicDescription}
              </CardDescription>
            </div>
          </div>
          {onDismiss && (
            <Button variant="ghost" size="icon" onClick={handleDismiss}>
              <X className="w-4 h-4" />
            </Button>
          )}
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {loading ? (
          <div className="flex items-center justify-center py-8">
            <Activity className="w-6 h-6 animate-spin text-muted-foreground" />
            <span className="ml-2 text-muted-foreground">Lade Sessions...</span>
          </div>
        ) : sessions.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-8 text-center">
            <CheckCircle2 className="w-12 h-12 text-muted-foreground/50 mb-3" />
            <p className="text-muted-foreground">Keine aktiven Sessions</p>
            <p className="text-xs text-muted-foreground/70 mt-1">
              {patientFilter ? 'Starten Sie eine neue Berechnung für diesen Klienten' : 'Alle Sessions wurden abgeschlossen'}
            </p>
          </div>
        ) : (
          <>
            {/* Zusammenfassung */}
            <div className="grid grid-cols-3 gap-3 text-center">
              <div className="bg-green-500/10 rounded-lg p-2">
                <div className="text-2xl font-bold text-green-400">{runningSessions.length}</div>
                <div className="text-xs text-muted-foreground">Aktiv</div>
              </div>
              <div className="bg-yellow-500/10 rounded-lg p-2">
                <div className="text-2xl font-bold text-yellow-400">{pendingSessions.length}</div>
                <div className="text-xs text-muted-foreground">Wartend</div>
              </div>
              <div className="bg-orange-500/10 rounded-lg p-2">
                <div className="text-2xl font-bold text-orange-400">{pausedSessions.length}</div>
                <div className="text-xs text-muted-foreground">Pausiert</div>
              </div>
            </div>

            {/* Gesamtzeit */}
            {totalRemaining > 0 && (
              <div className="flex items-center gap-2 text-sm bg-muted/50 rounded-lg p-2">
                <Clock className="w-4 h-4 text-muted-foreground" />
                <span className="text-muted-foreground">Geschätzte Restzeit:</span>
                <span className="font-semibold text-primary">{formatDuration(totalRemaining)}</span>
              </div>
            )}

            {/* Session-Liste */}
            <ScrollArea className={compact ? 'h-64' : 'h-96'}>
              <div className="space-y-2 pr-3">
                {sessions.map((session) => {
                  const patient = patients[session.patient_id];
                  const patientName = patient 
                    ? `${patient.first_name} ${patient.last_name}` 
                    : 'Unbekannt';

                  return (
                    <div 
                      key={session.id}
                      className="flex items-center justify-between p-2 rounded-lg bg-muted/30 hover:bg-muted/50 transition-colors group"
                    >
                      <div 
                        className="flex items-center gap-3 flex-1 min-w-0 cursor-pointer"
                        onClick={() => handleNavigate(session)}
                      >
                        {session.status === 'running' ? (
                          <Zap className="w-4 h-4 text-green-400 flex-shrink-0" />
                        ) : session.status === 'paused' ? (
                          <AlertTriangle className="w-4 h-4 text-orange-400 flex-shrink-0" />
                        ) : (
                          <Clock className="w-4 h-4 text-muted-foreground flex-shrink-0" />
                        )}
                        <div className="min-w-0 flex-1">
                          <div className="text-sm font-medium truncate">{session.word}</div>
                          <div className="text-xs text-muted-foreground flex items-center gap-2">
                            <span>{patientName}</span>
                            {sourceModuleFilter === 'all' && (
                              <>
                                <span>•</span>
                                <span>{getModuleLabel(session.source_module)}</span>
                              </>
                            )}
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        {getStatusBadge(session.status)}
                        {session.pulse_pause_active && (
                          <Badge variant="outline" className="text-[10px]">P/P</Badge>
                        )}
                        
                        {/* Steuerungsbuttons wenn showControls aktiv */}
                        {showControls && (
                          <div className="flex items-center gap-1 ml-2">
                            {session.status === 'running' && (
                              <Button 
                                variant="ghost" 
                                size="icon" 
                                className="h-7 w-7"
                                onClick={(e) => { e.stopPropagation(); handlePauseSession(session); }}
                              >
                                <Pause className="w-3 h-3" />
                              </Button>
                            )}
                            {session.status === 'paused' && (
                              <Button 
                                variant="ghost" 
                                size="icon" 
                                className="h-7 w-7"
                                onClick={(e) => { e.stopPropagation(); handleResumeSession(session); }}
                              >
                                <Play className="w-3 h-3" />
                              </Button>
                            )}
                            <Button 
                              variant="ghost" 
                              size="icon" 
                              className="h-7 w-7 text-destructive hover:text-destructive"
                              onClick={(e) => { e.stopPropagation(); handleCancelSession(session); }}
                            >
                              <Square className="w-3 h-3" />
                            </Button>
                          </div>
                        )}
                        
                        {!showControls && (
                          <ChevronRight className="w-4 h-4 text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity" />
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </ScrollArea>

            {/* Info */}
            <div className="flex items-start gap-2 text-xs text-muted-foreground bg-blue-500/5 rounded-lg p-2 border border-blue-500/10">
              <CheckCircle2 className="w-4 h-4 text-blue-400 flex-shrink-0 mt-0.5" />
              <span>
                Alle Sessions werden serverseitig fortgesetzt, auch wenn der Browser geschlossen wird. 
                Klicken Sie auf eine Session, um zum entsprechenden Modul zu navigieren.
              </span>
            </div>
          </>
        )}
      </CardContent>
    </Card>
  );
};

export default SessionRecoveryDashboard;
