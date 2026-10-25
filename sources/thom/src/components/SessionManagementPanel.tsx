/**
 * Session-Management Panel
 * Zeigt aktive Sitzung, Session-Historie und ermöglicht Session-Verwaltung
 */
import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Clock,
  Play,
  CheckCircle,
  History,
  ChevronDown,
  ChevronUp,
  FileText,
  Activity,
  Timer,
  Calendar,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible';
import { Textarea } from '@/components/ui/textarea';
import { cn } from '@/lib/utils';
import type { TreatmentSession } from '@/hooks/useSessionManagement';

interface SessionManagementPanelProps {
  activeSession: TreatmentSession | null;
  sessions: TreatmentSession[];
  isLoading: boolean;
  onCompleteSession?: () => void;
  sessionElapsed: number; // seconds since session start
}

const formatDuration = (seconds: number): string => {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m}:${s.toString().padStart(2, '0')}`;
};

const formatDate = (date: Date): string => {
  return date.toLocaleDateString('de-DE', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
};

const SessionManagementPanel = ({
  activeSession,
  sessions,
  isLoading,
  onCompleteSession,
  sessionElapsed,
}: SessionManagementPanelProps) => {
  const [showHistory, setShowHistory] = useState(false);
  const completedSessions = sessions.filter(s => s.status === 'completed');

  return (
    <div className="space-y-3">
      {/* Aktive Sitzung */}
      {activeSession && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <Card className="border-primary/30 bg-primary/5">
            <CardContent className="p-3">
              <div className="flex items-center justify-between gap-2">
                <div className="flex items-center gap-2 min-w-0">
                  <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse shrink-0" />
                  <span className="text-sm font-medium text-foreground truncate">
                    Sitzung #{activeSession.sessionNumber}
                  </span>
                  <Badge variant="outline" className="text-xs shrink-0">
                    <Timer className="w-3 h-3 mr-1" />
                    {formatDuration(sessionElapsed)}
                  </Badge>
                </div>
                {onCompleteSession && (
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={onCompleteSession}
                    className="text-xs gap-1 shrink-0"
                  >
                    <CheckCircle className="w-3 h-3" />
                    Abschließen
                  </Button>
                )}
              </div>
            </CardContent>
          </Card>
        </motion.div>
      )}

      {/* Session-Historie */}
      {completedSessions.length > 0 && (
        <Collapsible open={showHistory} onOpenChange={setShowHistory}>
          <CollapsibleTrigger asChild>
            <Button variant="ghost" size="sm" className="w-full justify-between text-xs text-muted-foreground">
              <span className="flex items-center gap-1">
                <History className="w-3 h-3" />
                {completedSessions.length} abgeschlossene Sitzung{completedSessions.length !== 1 ? 'en' : ''}
              </span>
              {showHistory ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
            </Button>
          </CollapsibleTrigger>
          <CollapsibleContent>
            <div className="space-y-1.5 mt-1">
              {completedSessions.slice(0, 10).map((session) => (
                <div
                  key={session.id}
                  className="flex items-center justify-between p-2 rounded-md bg-muted/30 text-xs"
                >
                  <div className="flex items-center gap-2 min-w-0">
                    <FileText className="w-3 h-3 text-muted-foreground shrink-0" />
                    <span className="truncate">#{session.sessionNumber}</span>
                  </div>
                  <div className="flex items-center gap-2 shrink-0 text-muted-foreground">
                    {session.durationSeconds && (
                      <span>{formatDuration(session.durationSeconds)}</span>
                    )}
                    <span>{formatDate(session.sessionDate)}</span>
                  </div>
                </div>
              ))}
            </div>
          </CollapsibleContent>
        </Collapsible>
      )}
    </div>
  );
};

export default SessionManagementPanel;
