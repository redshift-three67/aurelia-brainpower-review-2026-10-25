
import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useToast } from '@/hooks/use-toast';
import {
  calculateCopenRate,
  batchCalculateCopenRates,
  parseWordEnergyData,
  exportCopenRatesToCSV,
  validateWordEnergy,
  type CopenRateResult
} from '@/utils/copenRateGenerator';
import { type AlphabetType } from '@/utils/alphabetSystems';
import SingleCalculationForm from '@/components/forms/SingleCalculationForm';
import BatchImportForm from '@/components/forms/BatchImportForm';
import FileImportForm from '@/components/forms/FileImportForm';
import ResultsTable from '@/components/tables/ResultsTable';

const CopenRateGenerator: React.FC = () => {
  const [singleWord, setSingleWord] = useState('');
  const [singlePotency, setSinglePotency] = useState(6);
  const [singlePotencyType, setSinglePotencyType] = useState<'D' | 'C' | 'LM' | 'M'>('D');
  const [singleAlphabetType, setSingleAlphabetType] = useState<AlphabetType>('latin');
  const [useAdaptiveFibonacci, setUseAdaptiveFibonacci] = useState(false);
  const [results, setResults] = useState<CopenRateResult[]>([]);
  const [csvInput, setCsvInput] = useState('');
  const { toast } = useToast();

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

    const result = calculateCopenRate(
      singleWord, 
      singlePotency, 
      singlePotencyType, 
      singleAlphabetType,
      undefined,
      false,
      useAdaptiveFibonacci
    );
    setResults(prev => [result, ...prev]);
    
    toast({
      title: 'Rate berechnet',
      description: `${result.word} ${result.potencyType}${result.potency}: ${result.rate}${result.isAdaptive ? ' (adaptiv)' : ''}`
    });
  };

  const handleBatchCalculation = () => {
    if (!csvInput.trim()) {
      toast({
        title: 'Fehler',
        description: 'Bitte CSV-Daten eingeben',
        variant: 'destructive'
      });
      return;
    }

    try {
      const inputs = parseWordEnergyData(csvInput);
      if (inputs.length === 0) {
        toast({
          title: 'Fehler',
          description: 'Keine gültigen Daten gefunden',
          variant: 'destructive'
        });
        return;
      }

      const batchResults = batchCalculateCopenRates(inputs);
      setResults(prev => [...batchResults, ...prev]);
      
      toast({
        title: 'Batch-Berechnung abgeschlossen',
        description: `${batchResults.length} Raten erfolgreich berechnet`
      });
    } catch (error) {
      toast({
        title: 'Verarbeitungsfehler',
        description: 'Fehler beim Verarbeiten der CSV-Daten',
        variant: 'destructive'
      });
    }
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
      const content = e.target?.result as string;
      setCsvInput(content);
    };
    reader.readAsText(file);
  };

  const handleFileImportData = (extractedData: string) => {
    setCsvInput(extractedData);
    toast({
      title: 'Daten importiert',
      description: 'Extrahierte Daten wurden in das CSV-Feld eingefügt'
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

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="text-2xl text-center text-blue-800">
            Bruce Copen Raten-Generator
          </CardTitle>
          <p className="text-center text-gray-600">
            Authentische Umwandlung von Wortenergien nach Original Copen-Algorithmus (1978-1995)
          </p>
        </CardHeader>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
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
        />

        <FileImportForm onDataExtracted={handleFileImportData} />
      </div>

      <BatchImportForm
        csvInput={csvInput}
        onCsvInputChange={setCsvInput}
        onFileUpload={handleFileUpload}
        onBatchCalculate={handleBatchCalculation}
      />

      <ResultsTable
        results={results}
        onExport={handleExport}
        onClear={clearResults}
      />
    </div>
  );
};

export default CopenRateGenerator;
