import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Archive, Trash2, Eye, Play, Loader2 } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { supabase } from '@/integrations/supabase/client';
import { useAuth } from '@/hooks/useAuth';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Checkbox } from '@/components/ui/checkbox';

interface HarmonizationSession {
  id: string;
  user_id: string;
  patient_id: string;
  word: string;
  copen_rate: string | null;
  tested_potency: string | null;
  duration_seconds: number;
  status: string;
  started_at: string | null;
  completed_at: string | null;
  created_at: string;
  pulse_seconds?: number | null;
  pause_seconds?: number | null;
  pulse_pause_active?: boolean | null;
}

interface HarmonizationArchiveCloudProps {
  patientId?: string;
  sourceModule?: string; // Filter für source_module (z.B. 'copen_v2', 'word_energy', 'morphic_field')
}

const HarmonizationArchiveCloud: React.FC<HarmonizationArchiveCloudProps> = ({ 
  patientId,
  sourceModule
}) => {
  const [sessions, setSessions] = useState<HarmonizationSession[]>([]);
  const [loading, setLoading] = useState(true);
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const { toast } = useToast();
  const { user } = useAuth();

  // Reaktivierungs-Dialog State
  const [reactivateDialogOpen, setReactivateDialogOpen] = useState(false);
  const [selectedSession, setSelectedSession] = useState<HarmonizationSession | null>(null);
  const [reactivateDuration, setReactivateDuration] = useState<number>(42);
  const [reactivateUnit, setReactivateUnit] = useState<'seconds' | 'minutes' | 'hours' | 'days'>('minutes');
  const [reactivateContinuous, setReactivateContinuous] = useState(false);
  const [reactivatePulsePauseActive, setReactivatePulsePauseActive] = useState(false);
  const [reactivatePulseSeconds, setReactivatePulseSeconds] = useState<number>(21);
  const [reactivatePauseSeconds, setReactivatePauseSeconds] = useState<number>(42);
  const [reactivatePulseUnit, setReactivatePulseUnit] = useState<'seconds' | 'minutes'>('seconds');
  const [reactivatePauseUnit, setReactivatePauseUnit] = useState<'seconds' | 'minutes'>('seconds');
  const [isReactivating, setIsReactivating] = useState(false);

  useEffect(() => {
    if (user) {
      loadSessions();

      // Realtime-Updates
      const channel = supabase
        .channel('harmonization-sessions-changes')
        .on(
          'postgres_changes',
          {
            event: '*',
            schema: 'public',
            table: 'harmonization_sessions_v2',
          },
          () => {
            loadSessions();
          }
        )
        .subscribe();

      return () => {
        supabase.removeChannel(channel);
      };
    }
  }, [user, patientId, sourceModule]);

  const loadSessions = async () => {
    try {
      let query = supabase
        .from('harmonization_sessions_v2')
        .select('*')
        .in('status', ['completed', 'cancelled', 'running', 'pending'])
        .order('created_at', { ascending: false });

      if (patientId) {
        query = query.eq('patient_id', patientId);
      }

      // Filter nach source_module wenn angegeben
      if (sourceModule) {
        query = query.eq('source_module', sourceModule);
      }

      const { data, error } = await query;

      if (error) throw error;
      setSessions(data || []);
    } catch (error: any) {
      toast({
        variant: "destructive",
        title: "Fehler",
        description: error.message,
      });
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Sitzung wirklich löschen? (DSGVO-konform)')) return;

    try {
      const { error } = await supabase
        .from('harmonization_sessions_v2')
        .delete()
        .eq('id', id);

      if (error) throw error;

      toast({
        title: "Erfolg",
        description: "Sitzung gelöscht",
      });
    } catch (error: any) {
      toast({
        variant: "destructive",
        title: "Fehler",
        description: error.message,
      });
    }
  };

  const openReactivateDialog = (session: HarmonizationSession) => {
    setSelectedSession(session);
    setReactivateDialogOpen(true);
  };

  const getDurationInSeconds = (duration: number, unit: 'seconds' | 'minutes' | 'hours' | 'days') => {
    if (unit === 'days') return duration * 86400;
    if (unit === 'hours') return duration * 3600;
    if (unit === 'minutes') return duration * 60;
    return duration;
  };

  const handleReactivate = async () => {
    if (!selectedSession || !user) return;

    setIsReactivating(true);
    try {
      const durationSeconds = reactivateContinuous ? 0 : getDurationInSeconds(reactivateDuration, reactivateUnit);

      // Konvertiere Impuls und Pause in Sekunden
      const pulseInSeconds = reactivatePulsePauseActive ? (reactivatePulseUnit === 'minutes' ? reactivatePulseSeconds * 60 : reactivatePulseSeconds) : null;
      const pauseInSeconds = reactivatePulsePauseActive ? (reactivatePauseUnit === 'minutes' ? reactivatePauseSeconds * 60 : reactivatePauseSeconds) : null;

      const { error } = await supabase
        .from('harmonization_sessions_v2')
        .insert({
          user_id: user.id,
          patient_id: selectedSession.patient_id,
          word: selectedSession.word,
          copen_rate: selectedSession.copen_rate,
          tested_potency: selectedSession.tested_potency,
          duration_seconds: durationSeconds,
          status: 'pending',
          pulse_seconds: pulseInSeconds,
          pause_seconds: pauseInSeconds,
          pulse_pause_active: reactivatePulsePauseActive,
          source_module: 'archive_reactivation'
        });

      if (error) throw error;

      // Invoke Worker
      await supabase.functions.invoke('harmonization-worker', {
        body: { action: 'tick' }
      });

      toast({
        title: "Erfolg",
        description: "Harmonisierung reaktiviert und gestartet",
      });

      setReactivateDialogOpen(false);
      setSelectedSession(null);
    } catch (error: any) {
      toast({
        variant: "destructive",
        title: "Fehler",
        description: error.message,
      });
    } finally {
      setIsReactivating(false);
    }
  };

  const formatDuration = (seconds: number) => {
    if (seconds < 60) return `${seconds}s`;
    if (seconds < 3600) return `${Math.round(seconds / 60)}min`;
    if (seconds < 86400) return `${Math.round(seconds / 3600)}h`;
    return `${Math.round(seconds / 86400)} Tage`;
  };

  const getStatusBadge = (status: string) => {
    const badges = {
      completed: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-100',
      cancelled: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-100',
      paused: 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-100',
      running: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-100'
    };
    return badges[status as keyof typeof badges] || badges.completed;
  };

  const getStatusText = (status: string) => {
    const texts = {
      completed: 'Abgeschlossen',
      cancelled: 'Abgebrochen',
      paused: 'Pausiert',
      running: 'Läuft'
    };
    return texts[status as keyof typeof texts] || status;
  };

  if (loading) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center py-8">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader className="py-3">
        <CardTitle className="text-sm flex items-center gap-2">
          <Archive className="h-4 w-4" />
          Harmonisierungs-Archiv (Cloud)
          <span className="text-xs font-normal text-muted-foreground ml-2">
            ({sessions.length} Sitzungen)
          </span>
        </CardTitle>
      </CardHeader>
      <CardContent className="py-3">
        {sessions.length === 0 ? (
          <p className="text-center text-muted-foreground py-2 text-xs">
            Keine archivierten Sitzungen vorhanden
          </p>
        ) : (
          <div className="space-y-2 max-h-80 overflow-y-auto">
            {sessions.map(session => (
              <div key={session.id} className="border rounded-lg p-3">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="font-medium">{session.word}</span>
                      <span className={`text-xs px-2 py-0.5 rounded ${getStatusBadge(session.status)}`}>
                        {getStatusText(session.status)}
                      </span>
                    </div>
                    <div className="text-sm text-muted-foreground">
                      Dauer: {formatDuration(session.duration_seconds)} •{' '}
                      {session.completed_at && new Date(session.completed_at).toLocaleString('de-DE')}
                    </div>
                    {expandedId === session.id && (
                      <div className="mt-2 p-2 bg-muted rounded text-sm space-y-1">
                        <div>Status: <strong>{getStatusText(session.status)}</strong></div>
                        {session.tested_potency && (
                          <div className="pt-1 border-t border-border">
                            Getestete Potenz: <strong className="text-primary">{session.tested_potency}</strong>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                  <div className="flex gap-1">
                    <Button
                      onClick={() => openReactivateDialog(session)}
                      variant="ghost"
                      size="sm"
                      title="Harmonisierung reaktivieren"
                    >
                      <Play className="h-4 w-4" />
                    </Button>
                    <Button
                      onClick={() => setExpandedId(expandedId === session.id ? null : session.id)}
                      variant="ghost"
                      size="sm"
                    >
                      <Eye className="h-4 w-4" />
                    </Button>
                    <Button
                      onClick={() => handleDelete(session.id)}
                      variant="ghost"
                      size="sm"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>

      {/* Reaktivierungs-Dialog */}
      <Dialog open={reactivateDialogOpen} onOpenChange={setReactivateDialogOpen}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Harmonisierung reaktivieren</DialogTitle>
          </DialogHeader>
          
          {selectedSession && (
            <div className="space-y-4">
              <div className="p-3 bg-muted rounded-lg">
                <div className="font-medium">{selectedSession.word}</div>
                <div className="text-sm text-muted-foreground">
                  {selectedSession.tested_potency && `Potenz: ${selectedSession.tested_potency}`}
                </div>
              </div>

              <div className="grid grid-cols-[auto_1fr] gap-3 items-center">
                <Label className="text-right">Dauer:</Label>
                <div className="flex gap-2">
                  <Input
                    type="number"
                    value={reactivateDuration}
                    onChange={(e) => setReactivateDuration(Number(e.target.value))}
                    disabled={reactivateContinuous}
                    className="w-20 h-8"
                    min="1"
                  />
                  <Select
                    value={reactivateUnit}
                    onValueChange={(v: any) => setReactivateUnit(v)}
                    disabled={reactivateContinuous}
                  >
                    <SelectTrigger className="w-32 h-8">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="seconds">Sekunden</SelectItem>
                      <SelectItem value="minutes">Minuten</SelectItem>
                      <SelectItem value="hours">Stunden</SelectItem>
                      <SelectItem value="days">Tage</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <Label className="text-right">Dauersendung:</Label>
                <Checkbox
                  checked={reactivateContinuous}
                  onCheckedChange={(checked) => setReactivateContinuous(!!checked)}
                />

                <Label className="text-right">Impuls/Pause:</Label>
                <Checkbox
                  checked={reactivatePulsePauseActive}
                  onCheckedChange={(checked) => setReactivatePulsePauseActive(!!checked)}
                />

                {reactivatePulsePauseActive && (
                  <>
                    <Label className="text-right">Impuls:</Label>
                    <div className="flex gap-1">
                      <Input
                        type="number"
                        value={reactivatePulseSeconds}
                        onChange={(e) => setReactivatePulseSeconds(Number(e.target.value))}
                        className="w-16 h-8"
                        min="1"
                        max="999"
                      />
                      <Select value={reactivatePulseUnit} onValueChange={(v: any) => setReactivatePulseUnit(v)}>
                        <SelectTrigger className="w-20 h-8">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="seconds">Sek.</SelectItem>
                          <SelectItem value="minutes">Min.</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>

                    <Label className="text-right">Pause:</Label>
                    <div className="flex gap-1">
                      <Input
                        type="number"
                        value={reactivatePauseSeconds}
                        onChange={(e) => setReactivatePauseSeconds(Number(e.target.value))}
                        className="w-16 h-8"
                        min="1"
                        max="999"
                      />
                      <Select value={reactivatePauseUnit} onValueChange={(v: any) => setReactivatePauseUnit(v)}>
                        <SelectTrigger className="w-20 h-8">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="seconds">Sek.</SelectItem>
                          <SelectItem value="minutes">Min.</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </>
                )}
              </div>
            </div>
          )}

          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setReactivateDialogOpen(false)}
              disabled={isReactivating}
            >
              Abbrechen
            </Button>
            <Button
              onClick={handleReactivate}
              disabled={isReactivating}
            >
              {isReactivating && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Reaktivieren
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </Card>
  );
};

export default HarmonizationArchiveCloud;
