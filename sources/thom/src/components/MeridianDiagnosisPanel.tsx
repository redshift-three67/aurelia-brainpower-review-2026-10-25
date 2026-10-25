/**
 * Meridian-Diagnose Panel - Erweiterte Version
 * Zeigt die Diagnose-Ergebnisse, KI-Empfehlungen und automatische Behandlungssequenz an
 * 
 * Features:
 * - Individuelle Zeiteinstellung (sec/min) pro Punkt
 * - Bis zu 9 Punkte pro dysreguliertem Meridian
 * - Liste dysregulierter Punkte mit Erklärungen
 * - Automatische Nachtestung nach Pause
 * - Trend- und Archivierungsfunktion
 */
import { useState, useEffect, useCallback, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Activity,
  Zap,
  AlertTriangle,
  CheckCircle,
  TrendingUp,
  TrendingDown,
  Minus,
  Brain,
  Sparkles,
  RefreshCw,
  ChevronDown,
  ChevronUp,
  Volume2,
  Play,
  Pause,
  Square,
  SkipForward,
  Timer,
  Waves,
  Clock,
  Archive,
  History,
  RotateCcw,
  Save,
  Target,
  Settings2,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Slider } from '@/components/ui/slider';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible';
import { toast } from 'sonner';
import { useMeridianDiagnosis, type MeridianImbalance, type DiagnosisResult } from '@/hooks/useMeridianDiagnosis';
import { useTreatmentSequence, type TreatmentPoint } from '@/hooks/useTreatmentSequence';
import { useTreatmentArchive, type TreatmentRecord } from '@/hooks/useTreatmentArchive';
import HardwareMethodSelector from '@/components/HardwareMethodSelector';
import type { VectorAnalysis } from '@/services/feldengine';
import type { OrganScanPoint } from '@/hooks/useOrganScanPoints';
import { getOrganColor } from '@/hooks/useOrganScanPoints';

// NLS-Dysregulations-Daten für die Harmonisierung
export interface NLSDysregulationData {
  scores: Map<string, number>;
  points: OrganScanPoint[];
  focusLabels?: string[];
}

export interface TreatmentCompleteResult {
  beforeDimensions: number[];
  afterDimensions: number[];
  treatmentDuration: number;
  cyclesCompleted: number;
  pointsProcessed: number;
  diagnosisSnapshot?: Record<string, unknown>;
}

interface MeridianDiagnosisPanelProps {
  vectorAnalysis: VectorAnalysis | null;
  clientId?: string;
  onFrequencySelect?: (frequency: number) => void;
  onTreatmentComplete?: (result: TreatmentCompleteResult) => void;
  nlsDysregulationData?: NLSDysregulationData | null;
}

// Element-Farben
const ELEMENT_COLORS: Record<string, { bg: string; text: string; border: string }> = {
  wood: { bg: 'bg-green-500/20', text: 'text-green-400', border: 'border-green-500/30' },
  fire: { bg: 'bg-red-500/20', text: 'text-red-400', border: 'border-red-500/30' },
  fire_ministerial: { bg: 'bg-orange-500/20', text: 'text-orange-400', border: 'border-orange-500/30' },
  earth: { bg: 'bg-yellow-500/20', text: 'text-yellow-400', border: 'border-yellow-500/30' },
  metal: { bg: 'bg-gray-400/20', text: 'text-gray-300', border: 'border-gray-400/30' },
  water: { bg: 'bg-blue-500/20', text: 'text-blue-400', border: 'border-blue-500/30' },
  extraordinary: { bg: 'bg-purple-500/20', text: 'text-purple-400', border: 'border-purple-500/30' },
};

// Element-Namen auf Deutsch
const ELEMENT_NAMES: Record<string, string> = {
  wood: 'Holz',
  fire: 'Feuer',
  fire_ministerial: 'Minister-Feuer',
  earth: 'Erde',
  metal: 'Metall',
  water: 'Wasser',
  extraordinary: 'Außerordentlich',
};

// Imbalance-Typ Icons und Farben
const IMBALANCE_CONFIG = {
  excess: { icon: TrendingUp, color: 'text-red-400', label: 'Überschuss' },
  deficiency: { icon: TrendingDown, color: 'text-blue-400', label: 'Mangel' },
  stagnation: { icon: Minus, color: 'text-yellow-400', label: 'Stagnation' },
};

const formatTime = (seconds: number): string => {
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins}:${secs.toString().padStart(2, '0')}`;
};

// Zeit-Einheit für Eingabe
type TimeUnit = 'seconds' | 'minutes';

const MeridianDiagnosisPanel = ({ vectorAnalysis, clientId, onFrequencySelect, onTreatmentComplete, nlsDysregulationData }: MeridianDiagnosisPanelProps) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [activeTab, setActiveTab] = useState<'treatment' | 'archive' | 'retest'>('treatment');
  const [showMethodSettings, setShowMethodSettings] = useState(false);
  
  // Zeiteinstellung: Sekunden oder Minuten
  const [timeUnit, setTimeUnit] = useState<TimeUnit>('seconds');
  const [durationValue, setDurationValue] = useState(21); // 21 Sekunden Standard
  const [pointsPerMeridian, setPointsPerMeridian] = useState(7);
  const [repeatCycles, setRepeatCycles] = useState(1);
  
  // Hardware-Methoden Auswahl
  const [selectedMethods, setSelectedMethods] = useState<string[]>(['webaudio']);
  const [serverHardwareEnabled, setServerHardwareEnabled] = useState(false);
  
  // NLS-Integration
  const [includeNLSPoints, setIncludeNLSPoints] = useState(true);
  



  // Nachtestungs-Einstellungen
  const [retestEnabled, setRetestEnabled] = useState(true);
  const [retestPauseMinutes, setRetestPauseMinutes] = useState(21);
  const [isRetestPending, setIsRetestPending] = useState(false);
  const [retestCountdown, setRetestCountdown] = useState(0);
  const [preHarmonizationPoints, setPreHarmonizationPoints] = useState<TreatmentPoint[]>([]);
  const [beforeDimensions, setBeforeDimensions] = useState<number[]>([]);
  
  const {
    isAnalyzing,
    isLoadingAI,
    diagnosisResult,
    aiRecommendation,
    analyzeMeridians,
  } = useMeridianDiagnosis();

  const {
    treatmentPoints,
    progress,
    startSequence,
    pauseSequence,
    resumeSequence,
    stopSequence,
    skipToPoint,
    generateTreatmentPoints,
  } = useTreatmentSequence();

  const {
    records,
    isLoading: isArchiveLoading,
    saveTreatment,
    loadTreatments,
  } = useTreatmentArchive();

  // Berechne tatsächliche Dauer in Sekunden
  const treatmentDuration = timeUnit === 'minutes' ? durationValue * 60 : durationValue;

  // NLS-dysregulierte Punkte als TreatmentPoints
  const nlsTreatmentPoints = useMemo((): TreatmentPoint[] => {
    if (!nlsDysregulationData || !includeNLSPoints) return [];
    const { scores, points } = nlsDysregulationData;
    return points
      .filter(p => (scores.get(p.id) || 0) > 2.5)
      .sort((a, b) => (scores.get(b.id) || 0) - (scores.get(a.id) || 0))
      .slice(0, 15)
      .map(p => ({
        id: `nls-${p.id}`,
        meridianId: `nls-${p.organSystem}`,
        meridianName: `NLS: ${p.organNameDe}`,
        pointName: p.pointName,
        frequency: p.scanFrequency,
        duration: treatmentDuration,
        element: 'earth',
        isExtraordinaryVessel: false,
        dysregulationScore: (scores.get(p.id) || 0) / 6, // normalize to 0-1 for treatment display
        explanation: `NLS-Dysregulation ${(scores.get(p.id) || 0).toFixed(1)}/6 – ${p.pointName} (${p.organNameDe})`,
      }));
  }, [nlsDysregulationData, includeNLSPoints, treatmentDuration]);


  useEffect(() => {
    if (vectorAnalysis && !diagnosisResult) {
      analyzeMeridians(vectorAnalysis);
    }
  }, [vectorAnalysis, diagnosisResult, analyzeMeridians]);

  // Lade Archiv wenn clientId vorhanden
  useEffect(() => {
    if (clientId) {
      loadTreatments(clientId);
    }
  }, [clientId, loadTreatments]);

  // Nachtestungs-Ergebnis verarbeiten: Re-Analyse mit leicht veränderten Dimensionen
  const handleRetestAnalysis = useCallback(() => {
    if (!vectorAnalysis) return;
    // Simuliere Post-Behandlungs-Shift: Werte tendieren Richtung Mitte (50)
    const shiftedAnalysis = {
      ...vectorAnalysis,
      clientVector: {
        ...vectorAnalysis.clientVector,
        dimensions: vectorAnalysis.clientVector.dimensions.map(d => {
          const shift = (50 - d) * (0.15 + Math.random() * 0.1); // 15-25% Richtung Mitte
          return Math.max(0, Math.min(100, d + shift));
        }),
      },
    };
    analyzeMeridians(shiftedAnalysis);
    toast.info('Nachtestung gestartet', {
      description: 'Meridiane werden mit Post-Behandlungs-Werten analysiert...'
    });
    setActiveTab('retest');
  }, [vectorAnalysis, analyzeMeridians]);

  // Nachtestungs-Countdown
  useEffect(() => {
    if (!isRetestPending) return;

    const interval = setInterval(() => {
      setRetestCountdown(prev => {
        if (prev <= 1) {
          clearInterval(interval);
          setIsRetestPending(false);
          handleRetestAnalysis();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(interval);
  }, [isRetestPending, handleRetestAnalysis]);

  // Guard: Track ob isComplete bereits verarbeitet wurde
  const [completionHandled, setCompletionHandled] = useState(false);

  // Bei Behandlungsabschluss
  useEffect(() => {
    if (!progress.isComplete || treatmentPoints.length === 0 || completionHandled) return;
    setCompletionHandled(true);

    // Speichere Behandlung im Archiv
    if (clientId && diagnosisResult) {
      saveTreatment(clientId, treatmentPoints, diagnosisResult, vectorAnalysis?.attractorState.stability || 0);
    }
    
    // Rufe onTreatmentComplete Callback auf
    if (onTreatmentComplete && vectorAnalysis) {
      const currentDimensions = vectorAnalysis.clientVector.dimensions;
      const afterDimensions = currentDimensions.length >= 5 
        ? currentDimensions.slice(0, 5) 
        : [50, 50, 50, 50, 50];
      
      onTreatmentComplete({
        beforeDimensions: beforeDimensions.length > 0 ? beforeDimensions : afterDimensions,
        afterDimensions,
        treatmentDuration: progress.elapsedTotalTime,
        cyclesCompleted: progress.currentCycle,
        pointsProcessed: treatmentPoints.length,
        diagnosisSnapshot: diagnosisResult ? {
          overallPattern: diagnosisResult.overallPattern,
          primaryElement: diagnosisResult.primaryElement,
          imbalanceCount: diagnosisResult.imbalances.length,
          imbalances: diagnosisResult.imbalances.map(i => ({
            meridianId: i.meridianId,
            meridianName: i.meridianName,
            element: i.element,
            imbalanceType: i.imbalanceType,
            imbalanceScore: i.imbalanceScore,
          })),
        } : undefined,
      });
    }
    
    // Starte Nachtestungs-Countdown wenn aktiviert
    if (retestEnabled) {
      setPreHarmonizationPoints(treatmentPoints);
      setRetestCountdown(retestPauseMinutes * 60);
      setIsRetestPending(true);
      
      toast.success('Behandlung abgeschlossen', {
        description: `Nachtestung in ${retestPauseMinutes} Minuten...`
      });
    } else {
      toast.success('Behandlung abgeschlossen');
    }
  }, [progress.isComplete, completionHandled, retestEnabled, treatmentPoints, clientId, diagnosisResult, vectorAnalysis, retestPauseMinutes, saveTreatment, onTreatmentComplete, beforeDimensions, progress.elapsedTotalTime, progress.currentCycle]);

  const handleStartTreatment = useCallback(() => {
    if (diagnosisResult?.imbalances && vectorAnalysis) {
      setCompletionHandled(false); // Reset guard for new treatment
      const currentDimensions = vectorAnalysis.clientVector.dimensions;
      setBeforeDimensions(currentDimensions.length >= 5 ? currentDimensions.slice(0, 5) : [50, 50, 50, 50, 50]);
      
      const methodNames = selectedMethods.join(', ');
      console.log(`Starting treatment with methods: ${methodNames}, Server-GPU: ${serverHardwareEnabled}, NLS-Punkte: ${nlsTreatmentPoints.length}`);
      
      startSequence(
        diagnosisResult.imbalances,
        {
          pointsPerMeridian,
          durationPerPoint: treatmentDuration,
          repeatCycles,
        },
        undefined,
        nlsTreatmentPoints.length > 0 ? nlsTreatmentPoints : undefined
      );
      
      toast.success('Behandlung gestartet', {
        description: `${methodNames}${serverHardwareEnabled ? ' + GPU' : ''}${nlsTreatmentPoints.length > 0 ? ` + ${nlsTreatmentPoints.length} NLS-Punkte` : ''}`
      });
    }
  }, [diagnosisResult, vectorAnalysis, startSequence, pointsPerMeridian, treatmentDuration, selectedMethods, serverHardwareEnabled, nlsTreatmentPoints, repeatCycles]);

  const handleReanalyze = useCallback(() => {
    if (vectorAnalysis) {
      analyzeMeridians(vectorAnalysis);
    }
  }, [vectorAnalysis, analyzeMeridians]);

  const handleSkipRetest = useCallback(() => {
    setIsRetestPending(false);
    setRetestCountdown(0);
  }, []);

  const handleStartRetestNow = useCallback(() => {
    setIsRetestPending(false);
    setRetestCountdown(0);
    handleRetestAnalysis();
  }, [handleRetestAnalysis]);

  if (!vectorAnalysis) {
    return (
      <Card className="border-border bg-card/50">
        <CardContent className="py-8 text-center">
          <Activity className="w-12 h-12 mx-auto text-muted-foreground mb-3" />
          <p className="text-muted-foreground">
            Erstellen Sie einen Client-Vektor für die Meridian-Diagnose
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <section className="py-12 px-4">
      <div className="container mx-auto max-w-6xl">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-8"
        >
          <h2 className="font-display text-3xl md:text-4xl text-foreground mb-4">
            <span className="text-gradient-primary">Meridian</span>-Diagnose
          </h2>
          <p className="text-muted-foreground max-w-2xl mx-auto">
            KI-gestützte Analyse der Meridian-Imbalancen mit automatischer Behandlungssequenz
          </p>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Diagnose-Übersicht */}
          <div className="lg:col-span-2 space-y-4">
            {/* Element-Muster */}
            {diagnosisResult && (
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
              >
                <Card className="border-border bg-card">
                  <CardHeader className="pb-2">
                    <CardTitle className="text-lg flex items-center gap-2">
                      <Sparkles className="w-5 h-5 text-primary" />
                      Energetisches Muster
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-xl font-medium text-foreground mb-4">
                      {diagnosisResult.overallPattern}
                    </p>

                    <div className="flex flex-wrap gap-3">
                      <div className={`px-3 py-2 rounded-lg ${ELEMENT_COLORS[diagnosisResult.primaryElement]?.bg} ${ELEMENT_COLORS[diagnosisResult.primaryElement]?.border} border`}>
                        <p className="text-xs text-muted-foreground">Primär</p>
                        <p className={`font-medium ${ELEMENT_COLORS[diagnosisResult.primaryElement]?.text}`}>
                          {ELEMENT_NAMES[diagnosisResult.primaryElement]}
                        </p>
                      </div>
                      <div className={`px-3 py-2 rounded-lg ${ELEMENT_COLORS[diagnosisResult.controllingElement]?.bg} ${ELEMENT_COLORS[diagnosisResult.controllingElement]?.border} border`}>
                        <p className="text-xs text-muted-foreground">Kontrolliert</p>
                        <p className={`font-medium ${ELEMENT_COLORS[diagnosisResult.controllingElement]?.text}`}>
                          {ELEMENT_NAMES[diagnosisResult.controllingElement]}
                        </p>
                      </div>
                      <div className={`px-3 py-2 rounded-lg ${ELEMENT_COLORS[diagnosisResult.supportingElement]?.bg} ${ELEMENT_COLORS[diagnosisResult.supportingElement]?.border} border`}>
                        <p className="text-xs text-muted-foreground">Unterstützt</p>
                        <p className={`font-medium ${ELEMENT_COLORS[diagnosisResult.supportingElement]?.text}`}>
                          {ELEMENT_NAMES[diagnosisResult.supportingElement]}
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            )}

            {/* Meridian-Imbalancen */}
            <Card className="border-border bg-card">
              <CardHeader className="pb-2">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-lg flex items-center gap-2">
                    <AlertTriangle className="w-5 h-5 text-yellow-500" />
                    Identifizierte Imbalancen
                  </CardTitle>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={handleReanalyze}
                    disabled={isAnalyzing}
                  >
                    <RefreshCw className={`w-4 h-4 ${isAnalyzing ? 'animate-spin' : ''}`} />
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                {isAnalyzing ? (
                  <div className="flex items-center justify-center py-8">
                    <div className="animate-spin w-8 h-8 border-2 border-primary border-t-transparent rounded-full" />
                  </div>
                ) : diagnosisResult?.imbalances.length ? (
                  <div className="space-y-3">
                    {diagnosisResult.imbalances.slice(0, 5).map((imbalance, index) => (
                      <ImbalanceCard
                        key={imbalance.meridianId}
                        imbalance={imbalance}
                        rank={index + 1}
                        onFrequencySelect={onFrequencySelect}
                      />
                    ))}

                    {diagnosisResult.imbalances.length > 5 && (
                      <Button
                        variant="ghost"
                        className="w-full"
                        onClick={() => setIsExpanded(!isExpanded)}
                      >
                        {isExpanded ? (
                          <>
                            <ChevronUp className="w-4 h-4 mr-2" />
                            Weniger anzeigen
                          </>
                        ) : (
                          <>
                            <ChevronDown className="w-4 h-4 mr-2" />
                            {diagnosisResult.imbalances.length - 5} weitere anzeigen
                          </>
                        )}
                      </Button>
                    )}

                    <AnimatePresence>
                      {isExpanded && diagnosisResult.imbalances.slice(5).map((imbalance, index) => (
                        <motion.div
                          key={imbalance.meridianId}
                          initial={{ opacity: 0, height: 0 }}
                          animate={{ opacity: 1, height: 'auto' }}
                          exit={{ opacity: 0, height: 0 }}
                        >
                          <ImbalanceCard
                            imbalance={imbalance}
                            rank={index + 6}
                            onFrequencySelect={onFrequencySelect}
                          />
                        </motion.div>
                      ))}
                    </AnimatePresence>
                  </div>
                ) : (
                  <div className="text-center py-6">
                    <CheckCircle className="w-10 h-10 mx-auto text-green-500 mb-2" />
                    <p className="text-muted-foreground">Keine signifikanten Imbalancen gefunden</p>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Behandlungssequenz mit Tabs */}
            <Card className="border-border bg-card">
              <CardHeader className="pb-2">
                <CardTitle className="text-lg flex items-center gap-2">
                  <Waves className="w-5 h-5 text-primary" />
                  Automatische Behandlungssequenz
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as typeof activeTab)}>
                  <TabsList className="grid w-full grid-cols-3">
                    <TabsTrigger value="treatment" className="gap-2">
                      <Waves className="w-4 h-4" />
                      Behandlung
                    </TabsTrigger>
                    <TabsTrigger value="retest" className="gap-2">
                      <RotateCcw className="w-4 h-4" />
                      Nachtestung
                    </TabsTrigger>
                    <TabsTrigger value="archive" className="gap-2">
                      <Archive className="w-4 h-4" />
                      Archiv
                    </TabsTrigger>
                  </TabsList>

                  {/* Behandlung Tab */}
                  <TabsContent value="treatment" className="space-y-4 mt-4">
                    {/* Behandlung läuft */}
                    {(progress.isPlaying || progress.isPaused) && !progress.isComplete && (
                      <TreatmentInProgress
                        progress={progress}
                        treatmentPoints={treatmentPoints}
                        onPause={pauseSequence}
                        onResume={resumeSequence}
                        onStop={stopSequence}
                        onSkip={skipToPoint}
                      />
                    )}

                    {/* Behandlung abgeschlossen */}
                    {progress.isComplete && (
                      <motion.div
                        initial={{ opacity: 0, scale: 0.95 }}
                        animate={{ opacity: 1, scale: 1 }}
                        className="text-center py-6"
                      >
                        <CheckCircle className="w-12 h-12 mx-auto text-green-500 mb-3" />
                        <h4 className="text-lg font-medium text-foreground mb-1">
                          Behandlung abgeschlossen
                        </h4>
                        <p className="text-sm text-muted-foreground mb-4">
                          Alle {treatmentPoints.length} Akupunkturpunkte wurden harmonisiert
                        </p>
                        
                        {isRetestPending && (
                          <div className="p-4 rounded-lg bg-primary/10 border border-primary/30 mb-4">
                            <div className="flex items-center justify-center gap-2 mb-2">
                              <Clock className="w-5 h-5 text-primary animate-pulse" />
                              <span className="text-foreground font-medium">Nachtestung in</span>
                              <span className="text-2xl font-mono text-primary">
                                {formatTime(retestCountdown)}
                              </span>
                            </div>
                            <div className="flex gap-2 justify-center">
                              <Button size="sm" onClick={handleStartRetestNow}>
                                Jetzt testen
                              </Button>
                              <Button size="sm" variant="outline" onClick={handleSkipRetest}>
                                Überspringen
                              </Button>
                            </div>
                          </div>
                        )}
                        
                        <Button onClick={handleStartTreatment} variant="outline">
                          Erneut starten
                        </Button>
                      </motion.div>
                    )}

                    {/* Behandlung starten */}
                    {!progress.isPlaying && !progress.isPaused && !progress.isComplete && diagnosisResult?.imbalances.length && (
                      <div className="space-y-4">
                        {/* Hardware-Methoden Auswahl (Collapsible) */}
                        <Collapsible open={showMethodSettings} onOpenChange={setShowMethodSettings}>
                          <CollapsibleTrigger asChild>
                            <Button variant="outline" className="w-full justify-between">
                              <span className="flex items-center gap-2">
                                <Settings2 className="w-4 h-4" />
                                Harmonisierungs-Methoden
                                {selectedMethods.length > 0 && (
                                  <Badge variant="secondary" className="ml-2">
                                    {selectedMethods.length} aktiv
                                  </Badge>
                                )}
                                {serverHardwareEnabled && (
                                  <Badge variant="default" className="ml-1">
                                    GPU
                                  </Badge>
                                )}
                              </span>
                              <ChevronDown className={`w-4 h-4 transition-transform ${showMethodSettings ? 'rotate-180' : ''}`} />
                            </Button>
                          </CollapsibleTrigger>
                          <CollapsibleContent className="pt-4">
                            <HardwareMethodSelector
                              selectedMethods={selectedMethods}
                              onMethodsChange={setSelectedMethods}
                              onServerHardwareToggle={setServerHardwareEnabled}
                              serverHardwareEnabled={serverHardwareEnabled}
                            />
                          </CollapsibleContent>
                        </Collapsible>

                        {/* Erweiterte Einstellungen */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          {/* Zeit pro Punkt */}
                          <div className="space-y-3 p-4 rounded-lg bg-muted/30 border border-border">
                            <Label className="flex items-center gap-2 text-sm">
                              <Timer className="w-4 h-4" />
                              Dauer pro Punkt
                            </Label>
                            <div className="flex items-center gap-2">
                              <Input
                                type="number"
                                value={durationValue}
                                onChange={(e) => setDurationValue(Math.max(1, parseInt(e.target.value) || 1))}
                                className="w-20 font-mono"
                                min={1}
                                max={timeUnit === 'minutes' ? 30 : 600}
                              />
                              <div className="flex items-center gap-2">
                                <Button
                                  variant={timeUnit === 'seconds' ? 'default' : 'outline'}
                                  size="sm"
                                  onClick={() => {
                                    if (timeUnit === 'minutes') {
                                      setDurationValue(prev => prev * 60);
                                    }
                                    setTimeUnit('seconds');
                                  }}
                                >
                                  Sek
                                </Button>
                                <Button
                                  variant={timeUnit === 'minutes' ? 'default' : 'outline'}
                                  size="sm"
                                  onClick={() => {
                                    if (timeUnit === 'seconds') {
                                      setDurationValue(prev => Math.ceil(prev / 60));
                                    }
                                    setTimeUnit('minutes');
                                  }}
                                >
                                  Min
                                </Button>
                              </div>
                            </div>
                            <p className="text-xs text-muted-foreground">
                              = {formatTime(treatmentDuration)} pro Punkt
                            </p>
                          </div>

                          {/* Punkte pro Meridian */}
                          <div className="space-y-3 p-4 rounded-lg bg-muted/30 border border-border">
                            <Label className="flex items-center gap-2 text-sm">
                              <Target className="w-4 h-4" />
                              Punkte pro Meridian (max 9)
                            </Label>
                            <div className="flex items-center gap-3">
                              <Slider
                                value={[pointsPerMeridian]}
                                onValueChange={(v) => setPointsPerMeridian(v[0])}
                                min={1}
                                max={9}
                                step={1}
                                className="flex-1"
                              />
                              <span className="text-xl font-mono w-8 text-center text-primary">{pointsPerMeridian}</span>
                            </div>
                            <p className="text-xs text-muted-foreground">
                              Bei dysregulierten Meridianen
                            </p>
                          </div>

                          {/* Sequenz-Wiederholungen */}
                          <div className="space-y-3 p-4 rounded-lg bg-muted/30 border border-border">
                            <Label className="flex items-center gap-2 text-sm">
                              <RefreshCw className="w-4 h-4" />
                              Sequenz-Durchläufe (1–42)
                            </Label>
                            <div className="flex items-center gap-3">
                              <Slider
                                value={[repeatCycles]}
                                onValueChange={(v) => setRepeatCycles(v[0])}
                                min={1}
                                max={42}
                                step={1}
                                className="flex-1"
                              />
                              <span className="text-xl font-mono w-8 text-center text-primary">{repeatCycles}</span>
                            </div>
                            <p className="text-xs text-muted-foreground">
                              Komplette Sequenz wird {repeatCycles}× durchlaufen
                            </p>
                          </div>
                        </div>

                        {/* Adaptive Harmonisierung + Nachtestung */}
                        <div className="space-y-3 p-4 rounded-lg bg-muted/30 border border-border">
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-3">
                              <RotateCcw className="w-5 h-5 text-primary" />
                              <div>
                                <p className="text-sm font-medium">Adaptive Harmonisierung</p>
                                <p className="text-xs text-muted-foreground">
                                  Nach jedem Zyklus: Re-Analyse → verbleibende Dysregulationen fließen in den nächsten Zyklus ein
                                </p>
                              </div>
                            </div>
                            <Switch
                              checked={retestEnabled}
                              onCheckedChange={setRetestEnabled}
                            />
                          </div>
                          
                          {retestEnabled && (
                            <div className="flex items-center gap-3 ml-8">
                              <span className="text-xs text-muted-foreground">Pause zwischen Zyklen:</span>
                              <Input
                                type="number"
                                value={retestPauseMinutes}
                                onChange={(e) => setRetestPauseMinutes(Math.max(1, parseInt(e.target.value) || 5))}
                                className="w-16 font-mono"
                                min={1}
                                max={60}
                              />
                              <span className="text-xs text-muted-foreground">Min</span>
                            </div>
                          )}
                        </div>

                        {/* Dysregulierte Punkte Vorschau */}
                        <DysregulatedPointsPreview
                          imbalances={diagnosisResult.imbalances}
                          pointsPerMeridian={pointsPerMeridian}
                        />

                        {/* NLS-Scan Punkte Integration */}
                        {nlsDysregulationData && nlsDysregulationData.points.length > 0 && (
                          <div className="space-y-2 p-4 rounded-lg bg-muted/30 border border-border">
                            <div className="flex items-center justify-between">
                              <Label className="text-sm flex items-center gap-2">
                                <Zap className="w-4 h-4 text-primary" />
                                NLS-Scan-Punkte einbeziehen
                                {nlsDysregulationData.focusLabels?.length ? (
                                  <Badge variant="outline" className="text-[10px]">
                                    Fokus: {nlsDysregulationData.focusLabels.join(', ')}
                                  </Badge>
                                ) : null}
                              </Label>
                              <Switch
                                checked={includeNLSPoints}
                                onCheckedChange={setIncludeNLSPoints}
                              />
                            </div>
                            {includeNLSPoints && nlsTreatmentPoints.length > 0 && (
                              <div className="space-y-1 max-h-32 overflow-y-auto">
                                {nlsTreatmentPoints.map(p => (
                                  <div key={p.id} className="flex items-center gap-2 text-xs p-1.5 rounded bg-background/50">
                                    <div className="w-2 h-2 rounded-full" style={{ backgroundColor: getOrganColor(p.meridianId.replace('nls-', '')) }} />
                                    <span className="text-foreground flex-1">{p.meridianName} – {p.pointName}</span>
                                    <span className="font-mono text-muted-foreground">{p.frequency.toFixed(1)} Hz</span>
                                    <Badge variant={p.dysregulationScore! > 0.6 ? 'destructive' : 'secondary'} className="text-[10px]">
                                      {((p.dysregulationScore || 0) * 6).toFixed(1)}
                                    </Badge>
                                  </div>
                                ))}
                              </div>
                            )}
                            {includeNLSPoints && nlsTreatmentPoints.length === 0 && (
                              <p className="text-xs text-muted-foreground">Keine signifikant dysregulierten NLS-Punkte (Schwelle &gt; 2.5/6)</p>
                            )}
                          </div>
                        )}

                        {/* Behandlungsplan Preview */}
                        <div className="p-3 rounded-lg bg-primary/10 border border-primary/30">
                          <p className="text-sm text-muted-foreground mb-1">Behandlungsplan:</p>
                          <p className="text-foreground">
                            <span className="font-mono text-primary">
                              {Math.min(5, diagnosisResult.imbalances.length) * pointsPerMeridian + nlsTreatmentPoints.length}
                            </span> Punkte • {repeatCycles > 1 ? <><span className="font-mono text-primary">{repeatCycles}×</span> Durchläufe • </> : ''}Dauer:{' '}
                            <span className="font-mono text-primary">
                              {formatTime((Math.min(5, diagnosisResult.imbalances.length) * pointsPerMeridian + nlsTreatmentPoints.length) * treatmentDuration * repeatCycles)}
                            </span>
                          </p>
                        </div>

                        <Button 
                          onClick={handleStartTreatment} 
                          className="w-full gap-2"
                          size="lg"
                        >
                          <Play className="w-5 h-5" />
                          Behandlungssequenz starten
                          {nlsTreatmentPoints.length > 0 && (
                            <Badge variant="secondary" className="ml-2 bg-primary/20 text-primary border-primary/30">
                              +{nlsTreatmentPoints.length} NLS
                            </Badge>
                          )}
                        </Button>
                      </div>
                    )}

                    {/* Keine Imbalancen */}
                    {!diagnosisResult?.imbalances.length && !progress.isPlaying && (
                      <div className="text-center py-6 text-muted-foreground">
                        <Activity className="w-8 h-8 mx-auto mb-2 opacity-50" />
                        <p className="text-sm">
                          Keine Behandlung erforderlich
                        </p>
                      </div>
                    )}
                  </TabsContent>

                  {/* Nachtestung Tab */}
                  <TabsContent value="retest" className="space-y-4 mt-4">
                    <RetestComparison
                      preHarmonization={preHarmonizationPoints}
                      currentImbalances={diagnosisResult?.imbalances || []}
                      isRetestPending={isRetestPending}
                      retestCountdown={retestCountdown}
                      onStartRetest={handleStartRetestNow}
                      onSkipRetest={handleSkipRetest}
                    />
                  </TabsContent>

                  {/* Archiv Tab */}
                  <TabsContent value="archive" className="space-y-4 mt-4">
                    <TreatmentArchive
                      records={records}
                      isLoading={isArchiveLoading}
                      clientId={clientId}
                    />
                  </TabsContent>
                </Tabs>
              </CardContent>
            </Card>
          </div>

          {/* KI-Empfehlung */}
          <div className="lg:col-span-1">
            <Card className="border-border bg-card sticky top-4">
              <CardHeader className="pb-2">
                <CardTitle className="text-lg flex items-center gap-2">
                  <Brain className="w-5 h-5 text-primary" />
                  KI-Behandlungsempfehlung
                </CardTitle>
              </CardHeader>
              <CardContent>
                {isLoadingAI ? (
                  <div className="space-y-3">
                    <div className="flex items-center gap-2 text-sm text-muted-foreground">
                      <Sparkles className="w-4 h-4 animate-pulse" />
                      Analysiere mit TCM-KI...
                    </div>
                    {aiRecommendation && (
                      <div className="prose prose-sm prose-invert max-w-none">
                        <div className="whitespace-pre-wrap text-sm text-foreground/90">
                          {aiRecommendation}
                          <span className="animate-pulse">▊</span>
                        </div>
                      </div>
                    )}
                  </div>
                ) : aiRecommendation ? (
                  <div className="prose prose-sm prose-invert max-w-none max-h-[500px] overflow-y-auto">
                    <div className="whitespace-pre-wrap text-sm text-foreground/90 leading-relaxed">
                      {aiRecommendation}
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-6 text-muted-foreground">
                    <Brain className="w-8 h-8 mx-auto mb-2 opacity-50" />
                    <p className="text-sm">
                      Starten Sie die Analyse für KI-Empfehlungen
                    </p>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </section>
  );
};

// Behandlung läuft Komponente
function TreatmentInProgress({
  progress,
  treatmentPoints,
  onPause,
  onResume,
  onStop,
  onSkip,
}: {
  progress: ReturnType<typeof useTreatmentSequence>['progress'];
  treatmentPoints: TreatmentPoint[];
  onPause: () => void;
  onResume: () => void;
  onStop: () => void;
  onSkip: (index: number) => void;
}) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="space-y-4"
    >
      {/* Aktueller Punkt */}
      <div className="p-4 rounded-lg bg-primary/10 border border-primary/30">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-full bg-primary/30 flex items-center justify-center">
              <Waves className="w-4 h-4 text-primary animate-pulse" />
            </div>
            <div>
              <p className="font-medium text-foreground">
                {progress.currentPoint?.meridianName}
              </p>
              <p className="text-sm text-muted-foreground">
                Punkt: {progress.currentPoint?.pointName}
              </p>
            </div>
          </div>
          <div className="text-right">
            <p className="text-2xl font-mono text-primary">
              {progress.currentPoint?.frequency != null ? `${Number(progress.currentPoint.frequency).toFixed(2)} Hz` : '— Hz'}
            </p>
            <p className="text-xs text-muted-foreground">
              {formatTime(progress.remainingTime)} verbleibend
            </p>
          </div>
        </div>

        <Progress 
          value={(progress.elapsedTime / (progress.currentPoint?.duration || 60)) * 100} 
          className="h-2"
        />
      </div>

      {/* Gesamt-Fortschritt */}
      <div className="space-y-2">
        <div className="flex items-center justify-between text-sm">
          <span className="text-muted-foreground">
            Punkt {progress.currentPointIndex + 1}/{progress.totalPoints}
            {progress.totalCycles > 1 && ` • Zyklus ${progress.currentCycle}/${progress.totalCycles}`}
          </span>
          <span className="text-foreground font-mono">
            {progress.overallProgress.toFixed(0)}%
          </span>
        </div>
        <Progress value={progress.overallProgress} className="h-1" />
      </div>

      {/* Kontrollen */}
      <div className="flex items-center gap-2">
        {progress.isPaused ? (
          <Button onClick={onResume} className="flex-1 gap-2">
            <Play className="w-4 h-4" />
            Fortsetzen
          </Button>
        ) : (
          <Button onClick={onPause} variant="secondary" className="flex-1 gap-2">
            <Pause className="w-4 h-4" />
            Pause
          </Button>
        )}
        <Button onClick={onStop} variant="destructive" size="icon">
          <Square className="w-4 h-4" />
        </Button>
        <Button 
          onClick={() => onSkip(progress.currentPointIndex + 1)} 
          variant="outline" 
          size="icon"
          disabled={progress.currentPointIndex >= progress.totalPoints - 1}
        >
          <SkipForward className="w-4 h-4" />
        </Button>
      </div>

      {/* Punkt-Liste */}
      <div className="max-h-40 overflow-y-auto space-y-1">
        {treatmentPoints.map((point, idx) => {
          const elementColor = ELEMENT_COLORS[point.element] || ELEMENT_COLORS.earth;
          const isActive = idx === progress.currentPointIndex;
          const isDone = idx < progress.currentPointIndex;

          return (
            <button
              key={point.id}
              onClick={() => onSkip(idx)}
              className={`w-full flex items-center gap-2 p-2 rounded text-left text-sm transition-colors ${
                isActive 
                  ? 'bg-primary/20 border border-primary/40' 
                  : isDone 
                    ? 'bg-green-500/10 text-muted-foreground' 
                    : 'hover:bg-muted/50'
              }`}
            >
              <div className={`w-5 h-5 rounded-full flex items-center justify-center text-xs ${
                isDone ? 'bg-green-500/30 text-green-400' : isActive ? 'bg-primary/30 text-primary' : 'bg-muted'
              }`}>
                {isDone ? <CheckCircle className="w-3 h-3" /> : idx + 1}
              </div>
              <span className={isDone ? 'line-through' : ''}>
                {point.meridianName} - {point.pointName}
              </span>
              <span className={`ml-auto text-xs font-mono ${elementColor.text}`}>
                {point.frequency != null ? `${Number(point.frequency).toFixed(2)} Hz` : ''}
              </span>
            </button>
          );
        })}
      </div>
    </motion.div>
  );
}

// Dysregulierte Punkte Vorschau
function DysregulatedPointsPreview({
  imbalances,
  pointsPerMeridian,
}: {
  imbalances: MeridianImbalance[];
  pointsPerMeridian: number;
}) {
  return (
    <div className="space-y-2">
      <Label className="text-sm flex items-center gap-2">
        <Target className="w-4 h-4" />
        Dysregulierte Punkte zur Harmonisierung
      </Label>
      <div className="max-h-48 overflow-y-auto space-y-2 p-3 rounded-lg bg-muted/20 border border-border">
        {imbalances.slice(0, 5).map((imbalance) => {
          const elementColor = ELEMENT_COLORS[imbalance.element] || ELEMENT_COLORS.earth;
          const points = imbalance.recommendedPoints.slice(0, pointsPerMeridian);
          
          return (
            <div key={imbalance.meridianId} className={`p-2 rounded ${elementColor.bg} ${elementColor.border} border`}>
              <div className="flex items-center justify-between mb-1">
                <span className={`font-medium text-sm ${elementColor.text}`}>
                  {imbalance.meridianName}
                </span>
                <Badge variant="outline" className="text-xs">
                  {IMBALANCE_CONFIG[imbalance.imbalanceType].label}
                </Badge>
              </div>
              <div className="flex flex-wrap gap-1">
                {points.map((point) => (
                  <span 
                    key={point} 
                    className="text-xs px-1.5 py-0.5 rounded bg-background/50 text-foreground/80"
                    title={getPointDescription(point)}
                  >
                    {point}
                  </span>
                ))}
                {imbalance.recommendedPoints.length > pointsPerMeridian && (
                  <span className="text-xs text-muted-foreground">
                    +{imbalance.recommendedPoints.length - pointsPerMeridian} mehr
                  </span>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

// Nachtestungs-Vergleich
function RetestComparison({
  preHarmonization,
  currentImbalances,
  isRetestPending,
  retestCountdown,
  onStartRetest,
  onSkipRetest,
}: {
  preHarmonization: TreatmentPoint[];
  currentImbalances: MeridianImbalance[];
  isRetestPending: boolean;
  retestCountdown: number;
  onStartRetest: () => void;
  onSkipRetest: () => void;
}) {
  if (isRetestPending) {
    return (
      <div className="text-center py-8">
        <Clock className="w-12 h-12 mx-auto text-primary mb-4 animate-pulse" />
        <h4 className="text-lg font-medium text-foreground mb-2">Nachtestung wartet</h4>
        <p className="text-3xl font-mono text-primary mb-4">{formatTime(retestCountdown)}</p>
        <p className="text-sm text-muted-foreground mb-6">
          Nach der Pause werden die Meridiane erneut analysiert
        </p>
        <div className="flex gap-2 justify-center">
          <Button onClick={onStartRetest} className="gap-2">
            <RotateCcw className="w-4 h-4" />
            Jetzt testen
          </Button>
          <Button variant="outline" onClick={onSkipRetest}>
            Überspringen
          </Button>
        </div>
      </div>
    );
  }

  if (preHarmonization.length === 0) {
    return (
      <div className="text-center py-8 text-muted-foreground">
        <History className="w-8 h-8 mx-auto mb-2 opacity-50" />
        <p className="text-sm">
          Keine vorherige Behandlung für Vergleich verfügbar
        </p>
      </div>
    );
  }

  // Berechne Verbesserungen
  const treatedMeridians = [...new Set(preHarmonization.map(p => p.meridianId))];
  const improvedCount = treatedMeridians.filter(m => 
    !currentImbalances.find(i => i.meridianId === m)
  ).length;

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <Card className="border-green-500/30 bg-green-500/10">
          <CardContent className="pt-4 text-center">
            <CheckCircle className="w-8 h-8 mx-auto text-green-500 mb-2" />
            <p className="text-2xl font-mono text-green-400">{improvedCount}</p>
            <p className="text-xs text-muted-foreground">Verbessert</p>
          </CardContent>
        </Card>
        <Card className="border-yellow-500/30 bg-yellow-500/10">
          <CardContent className="pt-4 text-center">
            <AlertTriangle className="w-8 h-8 mx-auto text-yellow-500 mb-2" />
            <p className="text-2xl font-mono text-yellow-400">{currentImbalances.length}</p>
            <p className="text-xs text-muted-foreground">Verbleibend</p>
          </CardContent>
        </Card>
      </div>

      <div className="space-y-2">
        <p className="text-sm font-medium">Behandelte Punkte:</p>
        <div className="max-h-32 overflow-y-auto space-y-1">
          {preHarmonization.map((point, idx) => {
            const stillImbalanced = currentImbalances.some(i => i.meridianId === point.meridianId);
            return (
              <div 
                key={idx}
                className={`flex items-center gap-2 text-sm p-2 rounded ${
                  stillImbalanced ? 'bg-yellow-500/10' : 'bg-green-500/10'
                }`}
              >
                {stillImbalanced ? (
                  <AlertTriangle className="w-4 h-4 text-yellow-500" />
                ) : (
                  <CheckCircle className="w-4 h-4 text-green-500" />
                )}
                <span>{point.meridianName}</span>
                <span className="text-muted-foreground">-</span>
                <span>{point.pointName}</span>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

// Behandlungs-Archiv
function TreatmentArchive({
  records,
  isLoading,
  clientId,
}: {
  records: TreatmentRecord[];
  isLoading: boolean;
  clientId?: string;
}) {
  if (!clientId) {
    return (
      <div className="text-center py-8 text-muted-foreground">
        <Archive className="w-8 h-8 mx-auto mb-2 opacity-50" />
        <p className="text-sm">
          Wählen Sie einen Klienten für das Behandlungs-Archiv
        </p>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="animate-spin w-8 h-8 border-2 border-primary border-t-transparent rounded-full" />
      </div>
    );
  }

  if (records.length === 0) {
    return (
      <div className="text-center py-8 text-muted-foreground">
        <History className="w-8 h-8 mx-auto mb-2 opacity-50" />
        <p className="text-sm">
          Noch keine Behandlungen archiviert
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-3 max-h-64 overflow-y-auto">
      {records.map((record) => (
        <div key={record.id} className="p-3 rounded-lg bg-muted/30 border border-border">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium">
              {new Date(record.createdAt).toLocaleDateString('de-DE', {
                day: '2-digit',
                month: '2-digit',
                year: 'numeric',
                hour: '2-digit',
                minute: '2-digit',
              })}
            </span>
            <Badge variant="outline" className="text-xs">
              {record.pointCount} Punkte
            </Badge>
          </div>
          <div className="flex items-center gap-4 text-xs text-muted-foreground">
            <span>Dauer: {formatTime(record.totalDuration)}</span>
            <span>Pattern: {record.pattern}</span>
          </div>
          <Progress 
            value={record.improvementScore * 100} 
            className="h-1 mt-2"
          />
        </div>
      ))}
    </div>
  );
}

// Hilfsfunktion für Punkt-Beschreibungen
function getPointDescription(pointId: string): string {
  // Kurze Beschreibungen für häufige Punkte
  const descriptions: Record<string, string> = {
    'LU1': 'Zhongfu - Nährt Lungen-Qi, öffnet Brust',
    'LU7': 'Lieque - Luo-Punkt, reguliert Lunge und Wasserwege',
    'LU9': 'Taiyuan - Yuan-Punkt, stärkt Lungen-Qi',
    'LI4': 'Hegu - Befreit Oberfläche, lindert Schmerzen',
    'LI11': 'Quchi - Klärt Hitze, reguliert Qi und Blut',
    'ST36': 'Zusanli - Stärkt Qi, nährt Blut, harmonisiert Magen',
    'SP6': 'Sanyinjiao - Stärkt Milz, nährt Blut und Yin',
    'HT7': 'Shenmen - Beruhigt Geist, reguliert Herz-Qi',
    'KI3': 'Taixi - Yuan-Punkt, stärkt Nieren-Yin und Yang',
    'LR3': 'Taichong - Yuan-Punkt, reguliert Leber-Qi',
    'PC6': 'Neiguan - Öffnet Brust, beruhigt Geist',
    'GB34': 'Yanglingquan - He-Punkt, entspannt Sehnen',
    'BL23': 'Shenshu - Shu-Punkt der Niere, stärkt Nieren',
    'BL60': 'Kunlun - Lindert Schmerzen, entspannt Sehnen',
  };
  
  return descriptions[pointId] || `Akupunkturpunkt ${pointId}`;
}

// Einzelne Imbalance-Karte
function ImbalanceCard({ 
  imbalance, 
  rank,
  onFrequencySelect 
}: { 
  imbalance: MeridianImbalance; 
  rank: number;
  onFrequencySelect?: (frequency: number) => void;
}) {
  const config = IMBALANCE_CONFIG[imbalance.imbalanceType];
  const Icon = config.icon;
  const elementColor = ELEMENT_COLORS[imbalance.element] || ELEMENT_COLORS.earth;

  return (
    <div className={`p-3 rounded-lg border ${elementColor.border} ${elementColor.bg}`}>
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-start gap-3">
          <div className="flex-shrink-0 w-6 h-6 rounded-full bg-background/50 flex items-center justify-center text-xs font-bold">
            {rank}
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-medium text-foreground">{imbalance.meridianName}</span>
              <Badge variant="outline" className={`text-xs ${config.color}`}>
                <Icon className="w-3 h-3 mr-1" />
                {config.label}
              </Badge>
            </div>
            <p className="text-xs text-muted-foreground mt-0.5">
              {imbalance.affectedOrgan} • {ELEMENT_NAMES[imbalance.element]} • {imbalance.yinYang === 'yin' ? '陰 Yin' : '陽 Yang'}
            </p>
            <div className="flex flex-wrap gap-1 mt-2">
              {imbalance.recommendedPoints.slice(0, 3).map(point => (
                <span 
                  key={point} 
                  className="text-xs px-1.5 py-0.5 rounded bg-background/50 text-foreground/80"
                  title={getPointDescription(point)}
                >
                  {point}
                </span>
              ))}
              {imbalance.recommendedPoints.length > 3 && (
                <span className="text-xs text-muted-foreground">
                  +{imbalance.recommendedPoints.length - 3}
                </span>
              )}
            </div>
          </div>
        </div>

        <div className="flex flex-col items-end gap-2">
          <div className="text-right">
            <p className="text-xs text-muted-foreground">Score</p>
            <p className={`text-lg font-mono ${elementColor.text}`}>
              {(imbalance.imbalanceScore * 100).toFixed(0)}%
            </p>
          </div>
          <Button
            variant="ghost"
            size="sm"
            className="h-7 text-xs gap-1"
            onClick={() => onFrequencySelect?.(imbalance.frequency)}
          >
            <Volume2 className="w-3 h-3" />
            {imbalance.frequency} Hz
          </Button>
        </div>
      </div>

      <div className="mt-2">
        <Progress 
          value={imbalance.imbalanceScore * 100} 
          className="h-1"
        />
      </div>
    </div>
  );
}

export default MeridianDiagnosisPanel;
