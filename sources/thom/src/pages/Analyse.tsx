/**
 * Analyse-Seite
 * Enthält die Klienten-Feldanalyse, Meridian-Diagnose und Frequenz-Output
 * Ausgelagert von der Hauptseite für bessere Performance
 */
import { useState, useCallback, useEffect, useRef } from 'react';
import type { NLSDysregulationData } from '@/components/MeridianDiagnosisPanel';
import { Link } from 'react-router-dom';
import { Helmet } from 'react-helmet-async';
import { ArrowLeft, Activity, X } from 'lucide-react';
import { ThemeToggle } from '@/components/ThemeToggle';
import { motion, AnimatePresence } from 'framer-motion';
import { Button } from '@/components/ui/button';
import ClientVectorInterface from '@/components/ClientVectorInterface';
import ClientVectorTrajectory3D from '@/components/ClientVectorTrajectory3D';
import AnatomyResonanceViewer from '@/components/AnatomyResonanceViewer';
import MeridianDiagnosisPanel from '@/components/MeridianDiagnosisPanel';
import FrequencyOutputModule from '@/components/FrequencyOutputModule';
import RealtimeStatusWidget from '@/components/RealtimeStatusWidget';
import TreatmentTrendAnalysis from '@/components/TreatmentTrendAnalysis';
import BifurcationWarningWidget from '@/components/BifurcationWarningWidget';
import RemedyDatabasePanel from '@/components/RemedyDatabasePanel';
import TCMTrendAnalytics from '@/components/TCMTrendAnalytics';
import SessionReportGenerator from '@/components/SessionReportGenerator';
import SessionManagementPanel from '@/components/SessionManagementPanel';
import Footer from '@/components/Footer';
import Spooky2Panel from '@/components/Spooky2Panel';
import { useSessionManagement } from '@/hooks/useSessionManagement';
import { useChreodeTracking } from '@/hooks/useChreodeTracking';
import type { VectorAnalysis } from '@/services/feldengine';
import type { NLSScanConfig } from '@/components/NLSScanConfigPanel';

export interface TreatmentResult {
  beforeDimensions: number[];
  afterDimensions: number[];
  treatmentDuration: number;
  cyclesCompleted: number;
  pointsProcessed: number;
  diagnosisSnapshot?: Record<string, unknown>;
}

const Analyse = () => {
  const [currentVectorAnalysis, setCurrentVectorAnalysis] = useState<VectorAnalysis | null>(null);
  const [selectedClientId, setSelectedClientId] = useState<string | null>(null);
  const [selectedFrequency, setSelectedFrequency] = useState<number | null>(null);
  const [treatmentResult, setTreatmentResult] = useState<TreatmentResult | null>(null);
  const [scanConfig, setScanConfig] = useState<NLSScanConfig | null>(null);
  const [nlsDysregulationData, setNlsDysregulationData] = useState<NLSDysregulationData | null>(null);
  const [sessionElapsed, setSessionElapsed] = useState(0);
  const sessionTimerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // Session-Management
  const {
    sessions,
    activeSession,
    isLoading: sessionsLoading,
    loadSessions,
    startSession,
    completeSession,
  } = useSessionManagement();

  // Chreode-Tracking
  const { recordPoint: recordChreodePoint } = useChreodeTracking();

  // Session-Timer
  useEffect(() => {
    if (activeSession) {
      const startTime = activeSession.createdAt.getTime();
      sessionTimerRef.current = setInterval(() => {
        setSessionElapsed(Math.floor((Date.now() - startTime) / 1000));
      }, 1000);
    } else {
      setSessionElapsed(0);
    }
    return () => {
      if (sessionTimerRef.current) clearInterval(sessionTimerRef.current);
    };
  }, [activeSession]);

  // Bei Klientenwahl: Sessions laden und neue Session starten
  const handleClientSelected = useCallback(async (clientId: string | null) => {
    setSelectedClientId(clientId);
    if (clientId) {
      await loadSessions(clientId);
    }
  }, [loadSessions]);

  // Auto-Start Session bei Vektor-Erstellung
  const handleVectorCreated = useCallback(async (analysis: VectorAnalysis) => {
    setCurrentVectorAnalysis(analysis);
    if (selectedClientId && !activeSession) {
      const session = await startSession(selectedClientId, analysis);
      // Chreode-Punkt aufzeichnen
      if (session) {
        recordChreodePoint(selectedClientId, session.id, analysis);
      }
    } else if (selectedClientId && activeSession) {
      recordChreodePoint(selectedClientId, activeSession.id, analysis);
    }
  }, [selectedClientId, activeSession, startSession, recordChreodePoint]);

  const handleFrequencySelect = useCallback((frequency: number) => {
    setSelectedFrequency(frequency);
  }, []);

  const handleTreatmentComplete = useCallback(async (result: TreatmentResult) => {
    setTreatmentResult(result);
    // Session automatisch abschließen mit diagnosis_snapshot
    if (activeSession) {
      await completeSession(activeSession.id, undefined, {
        beforeDimensions: result.beforeDimensions,
        afterDimensions: result.afterDimensions,
        cyclesCompleted: result.cyclesCompleted,
        pointsProcessed: result.pointsProcessed,
        ...(result.diagnosisSnapshot || {}),
      }, result.treatmentDuration);
    }
  }, [activeSession, completeSession]);

  const handleCompleteSession = useCallback(async () => {
    if (activeSession) {
      await completeSession(activeSession.id, undefined, undefined, sessionElapsed);
    }
  }, [activeSession, completeSession, sessionElapsed]);

  const dismissTrendAnalysis = useCallback(() => {
    setTreatmentResult(null);
  }, []);

  return (
    <>
      <Helmet>
        <title>Klienten-Feldanalyse | Feldengine</title>
        <meta 
          name="description" 
          content="Klienten-Feldanalyse mit Vektor-Berechnung, Meridian-Diagnose nach TCM und Frequenz-Harmonisierung basierend auf René Thoms Katastrophentheorie." 
        />
        <meta name="keywords" content="Feldanalyse, Meridian-Diagnose, TCM, Akupunktur, Frequenztherapie, Vektor-Analyse" />
      </Helmet>

      <main className="min-h-screen bg-background">
        {/* Header mit Navigation */}
        <header className="sticky top-0 z-50 bg-background/80 backdrop-blur-md border-b border-border">
          <div className="container mx-auto px-4 py-4 flex items-center justify-between">
            <Link to="/">
              <Button variant="ghost" className="gap-2">
                <ArrowLeft className="w-4 h-4" />
                Zurück zur Übersicht
              </Button>
            </Link>
            
            <motion.div 
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex items-center gap-3"
            >
              <Activity className="w-5 h-5 text-primary" />
              <h1 className="font-display text-lg md:text-xl text-foreground">
                Klienten-<span className="text-gradient-primary">Feldanalyse</span>
              </h1>
            </motion.div>

            <div className="flex items-center gap-2">
              <ThemeToggle />
              <div className="w-[80px]" />
            </div>
          </div>
        </header>

        {/* Trend-Analyse Overlay nach Behandlungsabschluss */}
        <AnimatePresence>
          {treatmentResult && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 z-50 bg-background/80 backdrop-blur-sm flex items-center justify-center p-4"
            >
              <motion.div
                initial={{ scale: 0.9, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                exit={{ scale: 0.9, opacity: 0 }}
                className="relative max-w-2xl w-full max-h-[90vh] overflow-y-auto"
              >
                <Button
                  variant="ghost"
                  size="icon"
                  className="absolute top-2 right-2 z-10"
                  onClick={dismissTrendAnalysis}
                >
                  <X className="w-4 h-4" />
                </Button>
                <TreatmentTrendAnalysis
                  beforeDimensions={treatmentResult.beforeDimensions}
                  afterDimensions={treatmentResult.afterDimensions}
                  treatmentDuration={treatmentResult.treatmentDuration}
                  cyclesCompleted={treatmentResult.cyclesCompleted}
                  pointsProcessed={treatmentResult.pointsProcessed}
                />
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Session-Management */}
        {selectedClientId && (
          <div className="container mx-auto px-4 pt-4">
            <SessionManagementPanel
              activeSession={activeSession}
              sessions={sessions}
              isLoading={sessionsLoading}
              onCompleteSession={activeSession ? handleCompleteSession : undefined}
              sessionElapsed={sessionElapsed}
            />
          </div>
        )}

        {/* Bifurkations-Warnung */}
        {currentVectorAnalysis && (
          <div className="container mx-auto px-4 pt-4">
            <BifurcationWarningWidget vectorAnalysis={currentVectorAnalysis} />
          </div>
        )}

        {/* Analyse-Komponenten */}
        <ClientVectorInterface onVectorCreated={handleVectorCreated} onClientSelected={handleClientSelected} />
        <ClientVectorTrajectory3D vectorAnalysis={currentVectorAnalysis} />
        <AnatomyResonanceViewer 
          vectorAnalysis={currentVectorAnalysis} 
          onFrequencySelect={handleFrequencySelect}
          onScanConfigChange={setScanConfig}
          onNLSDysregulationData={setNlsDysregulationData}
        />
        <MeridianDiagnosisPanel
          vectorAnalysis={currentVectorAnalysis}
          clientId={selectedClientId || undefined}
          onFrequencySelect={handleFrequencySelect}
          onTreatmentComplete={handleTreatmentComplete}
          nlsDysregulationData={nlsDysregulationData}
        />
        <FrequencyOutputModule />
        
        {/* Hardware-Ausgabe */}
        <div className="container mx-auto px-4 py-4">
          <Spooky2Panel currentFrequency={selectedFrequency || undefined} />
        </div>
        
        <RemedyDatabasePanel onSelectFrequency={handleFrequencySelect} />
        <TCMTrendAnalytics clientId={selectedClientId} />
        <SessionReportGenerator clientId={selectedClientId} />

        <Footer />
        <RealtimeStatusWidget />
      </main>
    </>
  );
};

export default Analyse;
