import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Archive, Trash2, Eye, Play } from 'lucide-react';
import { HarmonizationSession } from '@/types/patient';
import { useToast } from '@/hooks/use-toast';

interface HarmonizationArchiveProps {
  patientId?: string;
  onReactivate?: (session: HarmonizationSession) => void;
}

const HarmonizationArchive: React.FC<HarmonizationArchiveProps> = ({ patientId, onReactivate }) => {
  const [sessions, setSessions] = useState<HarmonizationSession[]>([]);
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const { toast } = useToast();

  useEffect(() => {
    loadSessions();
  }, [patientId]);

  const loadSessions = () => {
    const stored = localStorage.getItem('copen-harmonization-archive');
    if (stored) {
      let allSessions: HarmonizationSession[] = JSON.parse(stored);
      if (patientId) {
        allSessions = allSessions.filter(s => s.patientId === patientId);
      }
      setSessions(allSessions.sort((a, b) => 
        new Date(b.completedAt || b.id).getTime() - new Date(a.completedAt || a.id).getTime()
      ));
    }
  };

  const handleDelete = (id: string) => {
    if (confirm('Sitzung wirklich löschen?')) {
      const stored = localStorage.getItem('copen-harmonization-archive');
      if (stored) {
        const allSessions: HarmonizationSession[] = JSON.parse(stored);
        const updated = allSessions.filter(s => s.id !== id);
        localStorage.setItem('copen-harmonization-archive', JSON.stringify(updated));
        loadSessions();
        toast({
          title: "Erfolg",
          description: "Sitzung gelöscht"
        });
      }
    }
  };

  const formatDuration = (duration: number, unit: 'seconds' | 'minutes' | 'hours' | 'days') => {
    if (unit === 'days') return `${duration} Tage`;
    if (unit === 'seconds') return `${duration}s`;
    if (unit === 'minutes') return `${duration}min`;
    if (unit === 'hours') return `${duration}h`;
    return `${duration}`;
  };

  const getStatusBadge = (status: string) => {
    const badges = {
      completed: 'bg-green-100 text-green-800',
      stopped: 'bg-yellow-100 text-yellow-800',
      paused: 'bg-orange-100 text-orange-800',
      active: 'bg-blue-100 text-blue-800'
    };
    return badges[status as keyof typeof badges] || badges.completed;
  };

  const getStatusText = (status: string) => {
    const texts = {
      completed: 'Abgeschlossen',
      stopped: 'Gestoppt',
      paused: 'Pausiert',
      active: 'Aktiv'
    };
    return texts[status as keyof typeof texts] || status;
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Archive className="h-5 w-5" />
          Harmonisierungs-Archiv
          <span className="text-sm font-normal text-muted-foreground ml-2">
            ({sessions.length} Sitzungen)
          </span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        {sessions.length === 0 ? (
          <p className="text-center text-muted-foreground py-4">
            Keine archivierten Sitzungen vorhanden
          </p>
        ) : (
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {sessions.map(session => (
              <div key={session.id} className="border rounded-lg p-3">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="font-medium">{session.word}</span>
                      <span className="text-sm text-muted-foreground">
                        {session.potencyType}{session.potency}
                      </span>
                      <span className={`text-xs px-2 py-0.5 rounded ${getStatusBadge(session.status)}`}>
                        {getStatusText(session.status)}
                      </span>
                    </div>
                    <div className="text-sm text-muted-foreground">
                      Dauer: {formatDuration(session.duration, session.durationUnit as 'seconds' | 'minutes' | 'hours' | 'days')} •{' '}
                      {session.completedAt && new Date(session.completedAt).toLocaleString('de-DE')}
                    </div>
                    {expandedId === session.id && (
                      <div className="mt-2 p-2 bg-muted rounded text-sm space-y-1">
                        <div>Wortenergie-Rate: <strong>{session.wordRate.toLocaleString()}</strong></div>
                        <div>Klienten-Rate: <strong>{session.clientRate.toLocaleString()}</strong></div>
                        {session.testedPotency && (
                          <div className="pt-1 border-t border-border">
                            Getestete Potenz: <strong className="text-primary">{session.potencyType}{session.testedPotency}</strong>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                  <div className="flex gap-1">
                    {onReactivate && (
                      <Button
                        onClick={() => onReactivate(session)}
                        variant="ghost"
                        size="sm"
                        title="Harmonisierung reaktivieren"
                      >
                        <Play className="h-4 w-4" />
                      </Button>
                    )}
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
    </Card>
  );
};

export default HarmonizationArchive;
