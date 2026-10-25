/**
 * Klienten-Dashboard
 * Dedizierte Unterseite für umfassendes Klienten-Management
 * Session-Timeline, Trends, Remedies, Berichte
 */
import { useState, useEffect, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Helmet } from 'react-helmet-async';
import { motion } from 'framer-motion';
import {
  ArrowLeft,
  User,
  Calendar,
  Activity,
  TrendingUp,
  FileText,
  Pill,
  Clock,
  ChevronRight,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ThemeToggle } from '@/components/ThemeToggle';
import TCMTrendAnalytics from '@/components/TCMTrendAnalytics';
import SessionReportGenerator from '@/components/SessionReportGenerator';
import RemedyDatabasePanel from '@/components/RemedyDatabasePanel';
import Footer from '@/components/Footer';
import { supabase } from '@/integrations/supabase/client';
import { toast } from 'sonner';
import type { Json } from '@/integrations/supabase/types';

interface ClientInfo {
  id: string;
  firstName: string;
  lastName: string;
  birthDate: string;
  birthPlace: string;
  photoUrl: string | null;
  fieldSignature: string | null;
  notes: string | null;
  createdAt: string;
}

interface SnapshotRecord {
  [key: string]: Json | undefined;
}

interface DiagnosisSnapshot extends SnapshotRecord {
  imbalanceCount?: Json;
}

interface TreatmentSummarySnapshot extends SnapshotRecord {
  pointsProcessed?: Json;
  beforeDimensions?: Json;
  afterDimensions?: Json;
}

interface SessionSummary {
  id: string;
  sessionNumber: number;
  sessionDate: string;
  status: string;
  durationSeconds: number | null;
  vectorSnapshot: SnapshotRecord | null;
  diagnosisSnapshot: DiagnosisSnapshot | null;
  treatmentSummary: TreatmentSummarySnapshot | null;
  notes: string | null;
}

const formatDate = (dateStr: string) =>
  new Date(dateStr).toLocaleDateString('de-DE', {
    day: '2-digit', month: '2-digit', year: 'numeric',
  });

const formatDuration = (seconds: number | null) => {
  if (!seconds) return '–';
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m}:${s.toString().padStart(2, '0')}`;
};

const DIMENSION_LABELS = ['Körperlich', 'Emotional', 'Mental', 'Energie', 'Stress'];

const isSnapshotRecord = (value: Json | null): value is SnapshotRecord =>
  typeof value === 'object' && value !== null && !Array.isArray(value);

const parseSnapshotRecord = (value: Json | null): SnapshotRecord | null =>
  isSnapshotRecord(value) ? value : null;

const parseDiagnosisSnapshot = (value: Json | null): DiagnosisSnapshot | null =>
  isSnapshotRecord(value) ? value : null;

const parseTreatmentSummary = (value: Json | null): TreatmentSummarySnapshot | null =>
  isSnapshotRecord(value) ? value : null;

const formatSnapshotCount = (value: unknown): string | number =>
  typeof value === 'string' || typeof value === 'number' ? value : '?';

const getDimensionValue = (value: unknown, index: number): number =>
  Array.isArray(value) && typeof value[index] === 'number' ? value[index] : 50;

const KlientDashboard = () => {
  const { id: clientId } = useParams<{ id: string }>();
  const [client, setClient] = useState<ClientInfo | null>(null);
  const [sessions, setSessions] = useState<SessionSummary[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('timeline');

  const loadClient = useCallback(async () => {
    if (!clientId) return;
    setIsLoading(true);
    try {
      const { data, error } = await supabase
        .from('clients')
        .select('*')
        .eq('id', clientId)
        .single();
      if (error) throw error;
      setClient({
        id: data.id,
        firstName: data.first_name,
        lastName: data.last_name,
        birthDate: data.birth_date,
        birthPlace: data.birth_place,
        photoUrl: data.photo_url,
        fieldSignature: data.field_signature,
        notes: data.notes,
        createdAt: data.created_at,
      });
    } catch (error) {
      console.error('Error loading client:', error);
      toast.error('Klient konnte nicht geladen werden');
    }
  }, [clientId]);

  const loadSessions = useCallback(async () => {
    if (!clientId) return;
    try {
      const { data, error } = await supabase
        .from('treatment_sessions')
        .select('*')
        .eq('client_id', clientId)
        .order('session_date', { ascending: false })
        .limit(100);
      if (error) throw error;
      setSessions((data || []).map(s => ({
        id: s.id,
        sessionNumber: s.session_number,
        sessionDate: s.session_date,
        status: s.status,
        durationSeconds: s.duration_seconds,
        vectorSnapshot: parseSnapshotRecord(s.vector_snapshot),
        diagnosisSnapshot: parseDiagnosisSnapshot(s.diagnosis_snapshot),
        treatmentSummary: parseTreatmentSummary(s.treatment_summary),
        notes: s.notes,
      })));
    } catch (error) {
      console.error('Error loading sessions:', error);
    } finally {
      setIsLoading(false);
    }
  }, [clientId]);

  useEffect(() => {
    loadClient();
    loadSessions();
  }, [loadClient, loadSessions]);

  const completedSessions = sessions.filter(s => s.status === 'completed');
  const totalDuration = completedSessions.reduce((sum, s) => sum + (s.durationSeconds || 0), 0);

  if (!clientId) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <p className="text-muted-foreground">Kein Klient ausgewählt</p>
      </div>
    );
  }

  return (
    <>
      <Helmet>
        <title>{client ? `${client.firstName} ${client.lastName}` : 'Klient'} | Feldengine</title>
        <meta name="description" content="Klienten-Dashboard mit Session-Timeline, Trendanalyse und Sitzungsberichten." />
      </Helmet>

      <main className="min-h-screen bg-background">
        {/* Header */}
        <header className="sticky top-0 z-50 bg-background/80 backdrop-blur-md border-b border-border">
          <div className="container mx-auto px-4 py-4 flex items-center justify-between">
            <Link to="/analyse">
              <Button variant="ghost" className="gap-2">
                <ArrowLeft className="w-4 h-4" />
                Zurück zur Analyse
              </Button>
            </Link>
            <div className="flex items-center gap-2">
              <ThemeToggle />
            </div>
          </div>
        </header>

        <div className="container mx-auto px-4 py-8 max-w-6xl">
          {/* Klienten-Info Header */}
          {client && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-8"
            >
              <div className="flex items-start gap-6">
                {/* Avatar */}
                <div className="w-20 h-20 rounded-full bg-primary/10 flex items-center justify-center border-2 border-primary/20 shrink-0">
                  {client.photoUrl ? (
                    <img src={client.photoUrl} alt="" className="w-full h-full rounded-full object-cover" />
                  ) : (
                    <User className="w-10 h-10 text-primary" />
                  )}
                </div>

                <div className="flex-1">
                  <h1 className="font-display text-3xl text-foreground mb-1">
                    {client.firstName} <span className="text-gradient-primary">{client.lastName}</span>
                  </h1>
                  <div className="flex items-center gap-4 text-sm text-muted-foreground">
                    <span className="flex items-center gap-1">
                      <Calendar className="w-4 h-4" />
                      {formatDate(client.birthDate)}
                    </span>
                    <span>{client.birthPlace}</span>
                  </div>
                  {client.fieldSignature && (
                    <Badge variant="secondary" className="mt-2 font-mono text-xs">
                      Signatur: {client.fieldSignature}
                    </Badge>
                  )}
                </div>

                {/* Stats */}
                <div className="flex gap-4 shrink-0">
                  <div className="text-center p-3 rounded-lg bg-card border border-border">
                    <p className="text-2xl font-bold text-primary">{completedSessions.length}</p>
                    <p className="text-xs text-muted-foreground">Sitzungen</p>
                  </div>
                  <div className="text-center p-3 rounded-lg bg-card border border-border">
                    <p className="text-2xl font-bold text-primary">{Math.floor(totalDuration / 60)}</p>
                    <p className="text-xs text-muted-foreground">Minuten</p>
                  </div>
                </div>
              </div>
            </motion.div>
          )}

          {/* Tabs */}
          <Tabs value={activeTab} onValueChange={setActiveTab}>
            <TabsList className="grid w-full grid-cols-4 mb-6">
              <TabsTrigger value="timeline" className="gap-2">
                <Clock className="w-4 h-4" />
                Timeline
              </TabsTrigger>
              <TabsTrigger value="trends" className="gap-2">
                <TrendingUp className="w-4 h-4" />
                Trends
              </TabsTrigger>
              <TabsTrigger value="remedies" className="gap-2">
                <Pill className="w-4 h-4" />
                Mittel
              </TabsTrigger>
              <TabsTrigger value="reports" className="gap-2">
                <FileText className="w-4 h-4" />
                Berichte
              </TabsTrigger>
            </TabsList>

            {/* Timeline */}
            <TabsContent value="timeline">
              <div className="space-y-4">
                {isLoading ? (
                  <div className="flex items-center justify-center py-12">
                    <div className="animate-spin w-8 h-8 border-2 border-primary border-t-transparent rounded-full" />
                  </div>
                ) : sessions.length === 0 ? (
                  <Card>
                    <CardContent className="py-12 text-center">
                      <Activity className="w-12 h-12 mx-auto text-muted-foreground mb-3" />
                      <p className="text-muted-foreground">Noch keine Sitzungen vorhanden</p>
                      <Link to="/analyse">
                        <Button className="mt-4">Erste Analyse starten</Button>
                      </Link>
                    </CardContent>
                  </Card>
                ) : (
                  sessions.map((session) => (
                    <motion.div
                      key={session.id}
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                    >
                      <Card className="hover:border-primary/30 transition-colors">
                        <CardContent className="p-4">
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-4">
                              <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                                session.status === 'completed'
                                  ? 'bg-green-100 dark:bg-green-500/20 text-green-600 dark:text-green-400'
                                  : session.status === 'active'
                                    ? 'bg-primary/10 text-primary'
                                    : 'bg-muted text-muted-foreground'
                              }`}>
                                <span className="font-bold text-sm">#{session.sessionNumber}</span>
                              </div>
                              <div>
                                <p className="font-medium text-foreground">
                                  Sitzung #{session.sessionNumber}
                                </p>
                                <p className="text-sm text-muted-foreground">
                                  {formatDate(session.sessionDate)} • {formatDuration(session.durationSeconds)}
                                </p>
                              </div>
                            </div>
                            <div className="flex items-center gap-3">
                              <Badge variant={session.status === 'completed' ? 'default' : 'secondary'}>
                                {session.status === 'completed' ? 'Abgeschlossen' : session.status === 'active' ? 'Aktiv' : 'Abgebrochen'}
                              </Badge>

                              {/* Diagnosis info */}
                              {session.diagnosisSnapshot && (
                                <span className="text-xs text-muted-foreground">
                                  {formatSnapshotCount(session.diagnosisSnapshot.imbalanceCount)} Imbalancen
                                </span>
                              )}

                              {/* Treatment info */}
                              {session.treatmentSummary && (
                                <span className="text-xs text-muted-foreground">
                                  {formatSnapshotCount(session.treatmentSummary.pointsProcessed)} Punkte
                                </span>
                              )}

                              <ChevronRight className="w-4 h-4 text-muted-foreground" />
                            </div>
                          </div>

                          {/* Vector dimensions comparison */}
                          {session.treatmentSummary && Array.isArray(session.treatmentSummary.beforeDimensions) && (
                            <div className="mt-3 pt-3 border-t border-border">
                              <div className="grid grid-cols-5 gap-2">
                                {DIMENSION_LABELS.map((label, i) => {
                                  const before = getDimensionValue(session.treatmentSummary.beforeDimensions, i);
                                  const after = getDimensionValue(session.treatmentSummary.afterDimensions, i);
                                  const diff = after - before;
                                  const improved = Math.abs(after - 50) < Math.abs(before - 50);
                                  return (
                                    <div key={label} className="text-center">
                                      <p className="text-[10px] text-muted-foreground">{label}</p>
                                      <p className={`text-xs font-mono ${improved ? 'text-green-500' : 'text-muted-foreground'}`}>
                                        {diff > 0 ? '+' : ''}{diff.toFixed(0)}
                                      </p>
                                    </div>
                                  );
                                })}
                              </div>
                            </div>
                          )}

                          {session.notes && (
                            <p className="mt-2 text-xs text-muted-foreground italic">{session.notes}</p>
                          )}
                        </CardContent>
                      </Card>
                    </motion.div>
                  ))
                )}
              </div>
            </TabsContent>

            {/* Trends */}
            <TabsContent value="trends">
              <TCMTrendAnalytics clientId={clientId} />
            </TabsContent>

            {/* Remedies */}
            <TabsContent value="remedies">
              <RemedyDatabasePanel onSelectFrequency={() => {}} />
            </TabsContent>

            {/* Reports */}
            <TabsContent value="reports">
              <SessionReportGenerator
                clientId={clientId}
                clientName={client ? `${client.firstName} ${client.lastName}` : undefined}
              />
            </TabsContent>
          </Tabs>
        </div>

        <Footer />
      </main>
    </>
  );
};

export default KlientDashboard;
