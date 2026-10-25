
import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ArrowLeft, Calculator, Zap, Play } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useToast } from '@/hooks/use-toast';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Checkbox } from '@/components/ui/checkbox';
import { supabase } from '@/integrations/supabase/client';
import { useAuth } from '@/hooks/useAuth';
import { calculateCopenRate, validateWordEnergy, exportCopenRatesToCSV, type CopenRateResult } from '@/utils/copenRateGenerator';
import { type AlphabetType } from '@/utils/alphabetSystems';
import { analyzeRates, DEFAULT_ANALYSIS_CONFIG } from '@/utils/resonanceAnalysis';
import SingleCalculationForm from '@/components/forms/SingleCalculationForm';
import ResultsTable from '@/components/tables/ResultsTable';
import PatientManagerCloud from '@/components/PatientManagerCloud';
import HarmonizationArchiveCloud from '@/components/HarmonizationArchiveCloud';
import AnalysisArchiveCloud from '@/components/AnalysisArchiveCloud';
import UserMenu from '@/components/UserMenu';

// Cloud Patient Type (from database)
interface CloudPatient {
  id: string;
  user_id: string;
  first_name: string;
  last_name: string;
  birth_date: string;
  birth_place: string;
  created_at: string;
  updated_at: string;
  image_signature?: string | null;
  image_signature_active?: boolean;
}

const CopenGeneratorPage: React.FC = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const { user } = useAuth();
  const [singleWord, setSingleWord] = useState('');
  const [singlePotency, setSinglePotency] = useState(6);
  const [singlePotencyType, setSinglePotencyType] = useState<'D' | 'C' | 'LM' | 'M'>('D');
  const [singleAlphabetType, setSingleAlphabetType] = useState<AlphabetType>('latin');
  const [useAdaptiveFibonacci, setUseAdaptiveFibonacci] = useState(false);
  const [results, setResults] = useState<CopenRateResult[]>([]);
  const [selectedPatient, setSelectedPatient] = useState<CloudPatient | null>(null);
  const [currentCalculatedRate, setCurrentCalculatedRate] = useState<number | undefined>(undefined);
  const [currentHighestLevel, setCurrentHighestLevel] = useState<{ level: number; value: number } | undefined>(undefined);
  
  // Harmonisierungs-Optionen
  const [harmonizationDuration, setHarmonizationDuration] = useState(5);
  const [harmonizationUnit, setHarmonizationUnit] = useState<'seconds' | 'minutes' | 'hours' | 'days'>('minutes');
  const [continuousMode, setContinuousMode] = useState(false);
  const [pulsePauseActive, setPulsePauseActive] = useState(false);
  const [pulseSeconds, setPulseSeconds] = useState(3);
  const [pauseSeconds, setPauseSeconds] = useState(7);

  const handleSingleCalculation = () => {
    const validation = validateWordEnergy(singleWord);
    if (!validation.valid) {
      toast({
        title: 'Eingabefehler',
        description: validation.error,
        variant: 'destructive'
      });
      return;
    }

    // Bildsignatur nutzen, wenn Klient ausgewählt und aktiv
    const useImgSig = selectedPatient?.image_signature_active ?? false;
    const imgSig = selectedPatient?.image_signature ?? undefined;
    
    const result = calculateCopenRate(
      singleWord, 
      singlePotency, 
      singlePotencyType, 
      singleAlphabetType,
      imgSig,
      useImgSig,
      useAdaptiveFibonacci
    );
    
    // Berechne Ebenen-Resonanz mit gleichem Algorithmus wie DB-Analyse
    const analysisResult = analyzeRates(
      [{ name: result.word, copenRate: result.rate }],
      { ...DEFAULT_ANALYSIS_CONFIG, maxEntries: 1 }
    );
    
    const rateObject = analysisResult.rateObjects[0];
    const highestLevel = {
      level: rateObject.dominantLevel,
      value: rateObject.levelDistribution[rateObject.dominantLevel]
    };
    
    // Speichere für Anzeige
    setCurrentCalculatedRate(result.rate);
    setCurrentHighestLevel(highestLevel);
    
    setResults(prev => [result, ...prev]);
    
    const imgInfo = useImgSig ? ' (mit Bildsignatur)' : '';
    toast({
      title: 'Rate berechnet',
      description: `${result.word} ${result.potencyType}${result.potency}: ${result.rate.toLocaleString('de-DE')} (Ebene ${highestLevel.level})${imgInfo}`
    });
  };

  const handleExport = () => {
    if (results.length === 0) {
      toast({
        title: 'Keine Daten',
        description: 'Keine Ergebnisse zum Exportieren vorhanden',
        variant: 'destructive'
      });
      return;
    }

    const csvContent = exportCopenRatesToCSV(results);
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `copen-raten-${new Date().toISOString().split('T')[0]}.csv`;
    link.click();
    
    toast({
      title: 'Export erfolgreich',
      description: `${results.length} Raten exportiert`
    });
  };

  const clearResults = () => {
    setResults([]);
    toast({
      title: 'Ergebnisse gelöscht',
      description: 'Alle berechneten Raten wurden entfernt'
    });
  };

  const getDurationInSeconds = (duration: number, unit: 'seconds' | 'minutes' | 'hours' | 'days'): number => {
    const multipliers = { seconds: 1, minutes: 60, hours: 3600, days: 86400 };
    return duration * multipliers[unit];
  };

  const startHarmonization = async () => {
    if (!user) {
      toast({
        title: 'Fehler',
        description: 'Bitte melden Sie sich an',
        variant: 'destructive'
      });
      return;
    }

    if (!selectedPatient) {
      toast({
        title: 'Fehler',
        description: 'Bitte wählen Sie zuerst einen Patienten aus',
        variant: 'destructive'
      });
      return;
    }

    if (currentCalculatedRate === undefined || !singleWord) {
      toast({
        title: 'Fehler',
        description: 'Bitte berechnen Sie zuerst eine Rate',
        variant: 'destructive'
      });
      return;
    }

    const durationSeconds = continuousMode ? 999999999 : getDurationInSeconds(harmonizationDuration, harmonizationUnit);

    const sessionData = {
      user_id: user.id,
      patient_id: selectedPatient.id,
      word: singleWord,
      copen_rate: currentCalculatedRate.toString(),
      tested_potency: `${singlePotencyType}${singlePotency}`,
      duration_seconds: durationSeconds,
      remaining_seconds: durationSeconds,
      status: 'pending' as const,
      pulse_seconds: pulsePauseActive ? pulseSeconds : null,
      pause_seconds: pulsePauseActive ? pauseSeconds : null,
      pulse_pause_active: pulsePauseActive,
      source_module: 'copen_v2'
    };

    const { error } = await supabase
      .from('harmonization_sessions_v2')
      .insert([sessionData]);

    if (error) {
      toast({
        title: 'Fehler',
        description: error.message,
        variant: 'destructive'
      });
      return;
    }

    try {
      await supabase.functions.invoke('harmonization-worker');
    } catch (_) {}

    toast({
      title: 'Harmonisierung gestartet',
      description: continuousMode 
        ? 'Dauerbesendung wurde gestartet'
        : `Harmonisierung für ${harmonizationDuration} ${harmonizationUnit} gestartet`
    });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-indigo-900">
      <div className="container mx-auto px-4 py-8">
        <div className="flex justify-between items-center mb-6">
          <Button 
            variant="outline" 
            onClick={() => navigate('/')}
            className="bg-white/10 border-white/20 text-white hover:bg-white/20"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Zurück zur Übersicht
          </Button>
          <UserMenu />
        </div>

        <Card className="mb-8 bg-white/10 border-white/20 backdrop-blur-sm">
          <CardHeader>
            <CardTitle className="text-3xl text-center text-white flex items-center justify-center gap-3">
              <Zap className="h-8 w-8 text-blue-300" />
              Bruce Copen Raten-Generator
            </CardTitle>
            <p className="text-center text-blue-200 text-lg">
              Authentische Umwandlung von Wortenergien nach Original Copen-Algorithmus (1978-1995)
            </p>
          </CardHeader>
        </Card>

        <div className="max-w-4xl mx-auto space-y-8">
          <Card className="bg-white/10 border-white/20 backdrop-blur-sm">
            <CardContent className="p-6">
              <SingleCalculationForm
                word={singleWord}
                potency={singlePotency}
                potencyType={singlePotencyType}
                alphabetType={singleAlphabetType}
                useAdaptiveFibonacci={useAdaptiveFibonacci}
                onWordChange={setSingleWord}
                onPotencyChange={setSinglePotency}
                onPotencyTypeChange={setSinglePotencyType}
                onAlphabetTypeChange={setSingleAlphabetType}
                onAdaptiveFibonacciChange={setUseAdaptiveFibonacci}
                onCalculate={handleSingleCalculation}
                calculatedRate={currentCalculatedRate}
                highestLevel={currentHighestLevel}
              />

              {/* Harmonisierung starten Sektion */}
              {currentCalculatedRate !== undefined && selectedPatient && (
                <div className="mt-6 pt-6 border-t border-white/20">
                  <h4 className="text-white font-semibold mb-4 flex items-center gap-2">
                    <Play className="h-5 w-5" />
                    Harmonisierung starten
                  </h4>
                  <div className="space-y-4">
                    {/* Dauer und Einheit */}
                    <div className="flex items-end gap-3">
                      <div className="flex-1">
                        <Label className="text-white text-xs">Dauer</Label>
                        <Input
                          type="number"
                          value={harmonizationDuration}
                          onChange={(e) => setHarmonizationDuration(parseInt(e.target.value) || 1)}
                          min={1}
                          className="bg-white/10 border-white/20 text-white h-9"
                        />
                      </div>
                      <div className="flex-1">
                        <Label className="text-white text-xs">Einheit</Label>
                        <Select value={harmonizationUnit} onValueChange={(v) => setHarmonizationUnit(v as any)}>
                          <SelectTrigger className="bg-white/10 border-white/20 text-white h-9">
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
                      <div className="flex items-center gap-2 pb-2">
                        <Checkbox
                          id="continuous-mode"
                          checked={continuousMode}
                          onCheckedChange={(checked) => setContinuousMode(checked === true)}
                        />
                        <Label htmlFor="continuous-mode" className="text-white text-xs cursor-pointer">
                          Dauerbesendung
                        </Label>
                      </div>
                    </div>

                    {/* Impuls/Pausen-Modus */}
                    <div className="flex items-end gap-3 pt-2 border-t border-white/10">
                      <div className="flex items-center gap-2 pb-2">
                        <Checkbox
                          id="pulse-pause-active"
                          checked={pulsePauseActive}
                          onCheckedChange={(checked) => setPulsePauseActive(checked === true)}
                        />
                        <Label htmlFor="pulse-pause-active" className="text-white text-xs cursor-pointer">
                          Impuls/Pausen-Modus
                        </Label>
                      </div>
                      {pulsePauseActive && (
                        <>
                          <div className="flex-1">
                            <Label className="text-white text-xs">Impuls (Sek.)</Label>
                            <Input
                              type="number"
                              value={pulseSeconds}
                              onChange={(e) => setPulseSeconds(parseInt(e.target.value) || 1)}
                              min={1}
                              max={60}
                              className="bg-white/10 border-white/20 text-white h-9"
                            />
                          </div>
                          <div className="flex-1">
                            <Label className="text-white text-xs">Pause (Sek.)</Label>
                            <Input
                              type="number"
                              value={pauseSeconds}
                              onChange={(e) => setPauseSeconds(parseInt(e.target.value) || 1)}
                              min={1}
                              max={60}
                              className="bg-white/10 border-white/20 text-white h-9"
                            />
                          </div>
                          <div className="text-xs text-blue-200 pb-2">
                            Zyklus: {pulseSeconds}s / {pauseSeconds}s
                          </div>
                        </>
                      )}
                    </div>

                    {/* Start Button */}
                    <Button 
                      onClick={startHarmonization}
                      className="w-full bg-green-600 hover:bg-green-700 text-white"
                    >
                      <Play className="h-4 w-4 mr-2" />
                      Harmonisierung starten
                    </Button>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          <ResultsTable
            results={results}
            onExport={handleExport}
            onClear={clearResults}
          />

          {/* Cloud-Patientenverwaltung */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mt-8">
            <PatientManagerCloud
              selectedPatient={selectedPatient}
              onSelectPatient={setSelectedPatient}
            />
            <HarmonizationArchiveCloud
              patientId={selectedPatient?.id}
              sourceModule="copen_v2"
            />
          </div>

          {/* Analysearchiv (12+1 Ebenen) */}
          <AnalysisArchiveCloud />
        </div>
      </div>
    </div>
  );
};

export default CopenGeneratorPage;
