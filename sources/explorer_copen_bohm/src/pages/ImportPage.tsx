
import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ArrowLeft, FileText, Upload } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import FileImportForm from '@/components/forms/FileImportForm';
import BatchImportForm from '@/components/forms/BatchImportForm';
import { useToast } from '@/hooks/use-toast';
import { parseWordEnergyData, batchCalculateCopenRates, exportCopenRatesToCSV, type CopenRateResult } from '@/utils/copenRateGenerator';
import ResultsTable from '@/components/tables/ResultsTable';

const ImportPage: React.FC = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [csvInput, setCsvInput] = useState('');
  const [results, setResults] = useState<CopenRateResult[]>([]);

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
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-indigo-900">
      <div className="container mx-auto px-4 py-8">
        <Button 
          variant="outline" 
          onClick={() => navigate('/')}
          className="mb-6 bg-white/10 border-white/20 text-white hover:bg-white/20"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Zurück zur Übersicht
        </Button>

        <Card className="mb-8 bg-white/10 border-white/20 backdrop-blur-sm">
          <CardHeader>
            <CardTitle className="text-3xl text-center text-white flex items-center justify-center gap-3">
              <FileText className="h-8 w-8 text-blue-300" />
              Daten Import Center
            </CardTitle>
            <p className="text-center text-blue-200 text-lg">
              PDF, Bilder und CSV-Dateien importieren und verarbeiten
            </p>
          </CardHeader>
        </Card>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          <div className="space-y-6">
            <Card className="bg-white/10 border-white/20 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="text-white flex items-center gap-2">
                  <Upload className="h-5 w-5 text-blue-300" />
                  PDF & Bild Import mit OCR
                </CardTitle>
              </CardHeader>
              <CardContent>
                <FileImportForm onDataExtracted={handleFileImportData} />
              </CardContent>
            </Card>
          </div>

          <div className="space-y-6">
            <Card className="bg-white/10 border-white/20 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="text-white flex items-center gap-2">
                  <FileText className="h-5 w-5 text-blue-300" />
                  CSV & Excel Import
                </CardTitle>
              </CardHeader>
              <CardContent>
                <BatchImportForm
                  csvInput={csvInput}
                  onCsvInputChange={setCsvInput}
                  onFileUpload={handleFileUpload}
                  onBatchCalculate={handleBatchCalculation}
                />
              </CardContent>
            </Card>
          </div>
        </div>

        <ResultsTable
          results={results}
          onExport={handleExport}
          onClear={clearResults}
        />
      </div>
    </div>
  );
};

export default ImportPage;
