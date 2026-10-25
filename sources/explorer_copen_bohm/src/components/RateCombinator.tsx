import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Plus, Trash2, Calculator, Zap, Copy, Download, ArrowRight, Info } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { 
  calculateCopenRate, 
  combineCopenRates, 
  combineCopenRatesWithEntropy,
  getRecommendedCombination,
  type CombinedRateInput,
  type CombinationMethod,
  type QuantumCombinedRateResult
} from '@/utils/copenRateGenerator';

interface RateEntry {
  id: string;
  word: string;
  potency: number;
  potencyType: 'D' | 'C' | 'LM' | 'M' | 'F1' | 'F2' | 'F3';
  rate: number | null;
  calculated: boolean;
}

const MAX_RATES = 10;

const RateCombinator: React.FC = () => {
  const { toast } = useToast();
  
  // Raten-Einträge (bis zu 10)
  const [entries, setEntries] = useState<RateEntry[]>([
    { id: crypto.randomUUID(), word: '', potency: 0, potencyType: 'D', rate: null, calculated: false }
  ]);
  
  // Kombinationsergebnis
  const [combinedResult, setCombinedResult] = useState<QuantumCombinedRateResult | null>(null);
  const [recommendedResult, setRecommendedResult] = useState<ReturnType<typeof getRecommendedCombination> | null>(null);
  const [selectedMethod, setSelectedMethod] = useState<CombinationMethod>('harmonic');
  const [useQuantum, setUseQuantum] = useState(true);

  // Wortenergie normalisieren
  const normalizeWord = (word: string): string => {
    return word
      .toUpperCase()
      .replace(/Ä/g, 'AE')
      .replace(/Ö/g, 'OE')
      .replace(/Ü/g, 'UE')
      .replace(/ß/g, 'SS')
      .replace(/\s*[DCLMF]+\d+/g, '')
      .replace(/[^A-Z0-9\s]/g, '')
      .trim();
  };

  // Neue Rate hinzufügen
  const addEntry = () => {
    if (entries.length >= MAX_RATES) {
      toast({
        title: "Maximum erreicht",
        description: `Maximal ${MAX_RATES} Raten können kombiniert werden`,
        variant: "destructive"
      });
      return;
    }
    setEntries([...entries, {
      id: crypto.randomUUID(),
      word: '',
      potency: 0,
      potencyType: 'D',
      rate: null,
      calculated: false
    }]);
  };

  // Rate entfernen
  const removeEntry = (id: string) => {
    if (entries.length <= 1) return;
    setEntries(entries.filter(e => e.id !== id));
    setCombinedResult(null);
    setRecommendedResult(null);
  };

  // Eintrag aktualisieren
  const updateEntry = (id: string, field: keyof RateEntry, value: any) => {
    setEntries(entries.map(e => {
      if (e.id !== id) return e;
      const updated = { ...e, [field]: value };
      // Rate neu berechnen wenn relevante Felder geändert werden
      if (field === 'word' || field === 'potency' || field === 'potencyType') {
        updated.calculated = false;
        updated.rate = null;
      }
      return updated;
    }));
    setCombinedResult(null);
    setRecommendedResult(null);
  };

  // Einzelne Rate berechnen
  const calculateSingleRate = (id: string) => {
    const entry = entries.find(e => e.id === id);
    if (!entry || !entry.word.trim()) {
      toast({
        title: "Fehler",
        description: "Bitte geben Sie eine Wortenergie ein",
        variant: "destructive"
      });
      return;
    }

    const result = calculateCopenRate(
      entry.word,
      entry.potency,
      entry.potencyType,
      'latin'
    );

    setEntries(entries.map(e => 
      e.id === id 
        ? { ...e, rate: result.rate, calculated: true }
        : e
    ));

    toast({
      title: "Rate berechnet",
      description: `${entry.word} ${entry.potencyType}${entry.potency} → ${result.rate.toLocaleString('de-DE')}`
    });
  };

  // Alle Raten berechnen
  const calculateAllRates = () => {
    const validEntries = entries.filter(e => e.word.trim());
    if (validEntries.length === 0) {
      toast({
        title: "Fehler",
        description: "Bitte geben Sie mindestens eine Wortenergie ein",
        variant: "destructive"
      });
      return;
    }

    const updatedEntries = entries.map(e => {
      if (!e.word.trim()) return e;
      const result = calculateCopenRate(e.word, e.potency, e.potencyType, 'latin');
      return { ...e, rate: result.rate, calculated: true };
    });

    setEntries(updatedEntries);
    toast({
      title: "Raten berechnet",
      description: `${validEntries.length} Rate(n) nach Bruce Copen V2 berechnet`
    });
  };

  // Raten kombinieren
  const combineRates = () => {
    const validEntries = entries.filter(e => e.calculated && e.rate !== null);
    
    if (validEntries.length < 2) {
      toast({
        title: "Fehler",
        description: "Mindestens 2 berechnete Raten erforderlich",
        variant: "destructive"
      });
      return;
    }

    const inputs: CombinedRateInput[] = validEntries.map(e => ({
      rate: e.rate!,
      word: e.word,
      potency: e.potency,
      potencyType: e.potencyType
    }));

    try {
      // Berechne mit Quantum-Enhancement
      const result = combineCopenRatesWithEntropy(inputs, selectedMethod, useQuantum);
      setCombinedResult(result);

      // Empfohlene Kombination berechnen
      const recommended = getRecommendedCombination(inputs, useQuantum);
      setRecommendedResult(recommended);

      toast({
        title: "Kombination berechnet",
        description: `${validEntries.length} Raten erfolgreich kombiniert`
      });
    } catch (error: any) {
      toast({
        title: "Fehler",
        description: error.message,
        variant: "destructive"
      });
    }
  };

  // Rate in Zwischenablage kopieren
  const copyToClipboard = (rate: number, label: string) => {
    navigator.clipboard.writeText(rate.toString());
    toast({
      title: "Kopiert",
      description: `${label}: ${rate.toLocaleString('de-DE')}`
    });
  };

  // Ergebnis als Text exportieren
  const exportResults = () => {
    if (!combinedResult || !recommendedResult) return;

    const lines = [
      '╔══════════════════════════════════════════════════════════════╗',
      '║          BRUCE COPEN V2 RATEN-KOMBINATOR                     ║',
      '╠══════════════════════════════════════════════════════════════╣',
      '',
      '─── EINGABE-RATEN ───',
      ...combinedResult.inputRates.map((r, i) => 
        `${i + 1}. ${r.word} ${r.potencyType}${r.potency === 0 ? '0' : r.potency} → ${r.rate.toLocaleString('de-DE')}`
      ),
      '',
      '─── EMPFOHLENE METHODE ───',
      `Methode: ${recommendedResult.method}`,
      `Kombinierte Rate: ${recommendedResult.formattedRate}`,
      '',
      recommendedResult.rationale,
      '',
      '─── ALLE KOMBINATIONSMETHODEN ───',
      ...combinedResult.allMethods.map(m => 
        `${m.method}: ${m.rate.toLocaleString('de-DE')}`
      ),
      '',
      '─── QUANTEN-ERWEITERT ───',
      `Quanten-Rate: ${combinedResult.quantumEnhancedRate?.toLocaleString('de-DE') || 'N/A'}`,
      `Digital (10-stellig): ${combinedResult.digitalQuantumRate?.toLocaleString('de-DE') || 'N/A'}`,
      '',
      `Berechnet: ${new Date().toLocaleString('de-DE')}`,
      '╚══════════════════════════════════════════════════════════════╝'
    ];

    const blob = new Blob([lines.join('\n')], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `Raten_Kombination_${Date.now()}.txt`;
    a.click();
    URL.revokeObjectURL(url);

    toast({
      title: "Exportiert",
      description: "Ergebnis als Textdatei gespeichert"
    });
  };

  const validEntriesCount = entries.filter(e => e.calculated && e.rate !== null).length;

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Calculator className="h-5 w-5 text-primary" />
          Raten-Kombinator (Bruce Copen V2)
          <Badge variant="outline" className="ml-2">
            {entries.length}/{MAX_RATES} Raten
          </Badge>
        </CardTitle>
        <p className="text-sm text-muted-foreground">
          Kombiniert bis zu 10 Wortenergien mit oder ohne Potenz (D0 = keine Potenz) zu einer vereinigten Rate
        </p>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Eingabe-Raten */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <Label className="text-base font-semibold">Wortenergien</Label>
            <div className="flex gap-2">
              <Button 
                variant="outline" 
                size="sm" 
                onClick={calculateAllRates}
                disabled={entries.every(e => !e.word.trim())}
              >
                <Calculator className="h-4 w-4 mr-1" />
                Alle berechnen
              </Button>
              <Button 
                variant="outline" 
                size="sm" 
                onClick={addEntry}
                disabled={entries.length >= MAX_RATES}
              >
                <Plus className="h-4 w-4 mr-1" />
                Hinzufügen
              </Button>
            </div>
          </div>

          <ScrollArea className="max-h-[400px]">
            <div className="space-y-3 pr-4">
              {entries.map((entry, index) => (
                <div 
                  key={entry.id} 
                  className={`flex items-center gap-2 p-3 rounded-lg border transition-colors ${
                    entry.calculated 
                      ? 'bg-primary/5 border-primary/30' 
                      : 'bg-muted/30 border-border'
                  }`}
                >
                  <span className="text-sm font-mono text-muted-foreground w-6">
                    {index + 1}.
                  </span>
                  
                  {/* Wortenergie */}
                  <Input
                    placeholder="Wortenergie eingeben..."
                    value={entry.word}
                    onChange={(e) => updateEntry(entry.id, 'word', e.target.value)}
                    className="flex-1 min-w-[200px]"
                  />
                  
                  {/* Potenztyp */}
                  <Select
                    value={entry.potencyType}
                    onValueChange={(v) => updateEntry(entry.id, 'potencyType', v)}
                  >
                    <SelectTrigger className="w-20">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="D">D</SelectItem>
                      <SelectItem value="C">C</SelectItem>
                      <SelectItem value="LM">LM</SelectItem>
                      <SelectItem value="M">M</SelectItem>
                      <SelectItem value="F1">F1</SelectItem>
                      <SelectItem value="F2">F2</SelectItem>
                      <SelectItem value="F3">F3</SelectItem>
                    </SelectContent>
                  </Select>
                  
                  {/* Potenzzahl (0 = ohne Potenz) */}
                  <Input
                    type="number"
                    min={0}
                    max={200}
                    value={entry.potency}
                    onChange={(e) => updateEntry(entry.id, 'potency', parseInt(e.target.value) || 0)}
                    className="w-20"
                    placeholder="0"
                  />
                  
                  {/* Berechnete Rate */}
                  {entry.calculated && entry.rate !== null && (
                    <div className="flex items-center gap-1 min-w-[120px]">
                      <ArrowRight className="h-4 w-4 text-primary" />
                      <Badge 
                        variant="secondary" 
                        className="font-mono cursor-pointer hover:bg-primary/20"
                        onClick={() => copyToClipboard(entry.rate!, entry.word)}
                      >
                        {entry.rate.toLocaleString('de-DE')}
                      </Badge>
                    </div>
                  )}
                  
                  {/* Aktionen */}
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => calculateSingleRate(entry.id)}
                    disabled={!entry.word.trim()}
                    title="Rate berechnen"
                  >
                    <Calculator className="h-4 w-4" />
                  </Button>
                  
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => removeEntry(entry.id)}
                    disabled={entries.length <= 1}
                    className="text-destructive hover:text-destructive"
                    title="Entfernen"
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              ))}
            </div>
          </ScrollArea>
        </div>

        <Separator />

        {/* Kombinationseinstellungen */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label>Kombinationsmethode</Label>
            <Select value={selectedMethod} onValueChange={(v) => setSelectedMethod(v as CombinationMethod)}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="harmonic">Harmonisches Mittel (empfohlen)</SelectItem>
                <SelectItem value="fibonacci">Fibonacci-Moduliert (Copen)</SelectItem>
                <SelectItem value="geometric">Geometrisches Mittel</SelectItem>
                <SelectItem value="arithmetic">Arithmetisches Mittel</SelectItem>
                <SelectItem value="weighted_potency">Potenz-gewichtet</SelectItem>
                <SelectItem value="malcolm_rae">Malcolm Rae (Phi)</SelectItem>
                <SelectItem value="copen_digital">Digital (10-stellig)</SelectItem>
              </SelectContent>
            </Select>
          </div>
          
          <div className="flex items-center justify-between p-3 rounded-lg border bg-muted/30">
            <div className="space-y-1">
              <Label className="flex items-center gap-2">
                <Zap className="h-4 w-4 text-yellow-500" />
                Quanten-Enhancement
              </Label>
              <p className="text-xs text-muted-foreground">
                Hardware-Entropie integrieren
              </p>
            </div>
            <Button
              variant={useQuantum ? "default" : "outline"}
              size="sm"
              onClick={() => setUseQuantum(!useQuantum)}
            >
              {useQuantum ? "Aktiv" : "Inaktiv"}
            </Button>
          </div>
        </div>

        {/* Kombinieren Button */}
        <Button 
          className="w-full" 
          size="lg"
          onClick={combineRates}
          disabled={validEntriesCount < 2}
        >
          <Calculator className="h-5 w-5 mr-2" />
          {validEntriesCount} Rate{validEntriesCount !== 1 ? 'n' : ''} kombinieren
        </Button>

        {/* Ergebnis */}
        {combinedResult && recommendedResult && (
          <div className="space-y-4 pt-4">
            <Separator />
            
            {/* Empfohlene Rate */}
            <Card className="border-primary/50 bg-primary/5">
              <CardHeader className="pb-2">
                <CardTitle className="text-lg flex items-center gap-2">
                  <Info className="h-5 w-5 text-primary" />
                  Empfohlene Kombination
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex items-center justify-between">
                  <div>
                    <Badge variant="secondary" className="mb-1">
                      {recommendedResult.method === 'harmonic_resonance' && 'Harmonische Resonanz'}
                      {recommendedResult.method === 'fibonacci_balanced' && 'Fibonacci-Balanciert'}
                      {recommendedResult.method === 'quantum_enhanced' && 'Quanten-Erweitert'}
                    </Badge>
                    <p className="text-3xl font-bold font-mono text-primary">
                      {recommendedResult.formattedRate}
                    </p>
                  </div>
                  <Button 
                    variant="outline" 
                    size="icon"
                    onClick={() => copyToClipboard(recommendedResult.combinedRate, 'Empfohlene Rate')}
                  >
                    <Copy className="h-4 w-4" />
                  </Button>
                </div>
                <p className="text-sm text-muted-foreground whitespace-pre-line">
                  {recommendedResult.rationale}
                </p>
              </CardContent>
            </Card>

            {/* Alle Methoden */}
            <div className="space-y-2">
              <Label className="text-base font-semibold">Alle Kombinationsmethoden</Label>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                {combinedResult.allMethods.map((m) => (
                  <div 
                    key={m.method}
                    className={`p-3 rounded-lg border flex justify-between items-center cursor-pointer hover:bg-muted/50 ${
                      m.method === selectedMethod ? 'border-primary bg-primary/5' : ''
                    }`}
                    onClick={() => copyToClipboard(m.rate, m.method)}
                  >
                    <div>
                      <p className="text-sm font-medium capitalize">{m.method.replace('_', ' ')}</p>
                      <p className="text-xs text-muted-foreground truncate max-w-[200px]">
                        {m.description.split(':')[0]}
                      </p>
                    </div>
                    <Badge variant="outline" className="font-mono">
                      {m.rate.toLocaleString('de-DE')}
                    </Badge>
                  </div>
                ))}
              </div>
            </div>

            {/* Quanten-Raten */}
            {useQuantum && combinedResult.quantumEnhancedRate && (
              <div className="space-y-2">
                <Label className="text-base font-semibold flex items-center gap-2">
                  <Zap className="h-4 w-4 text-yellow-500" />
                  Quanten-erweiterte Raten
                </Label>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  <div 
                    className="p-3 rounded-lg border bg-gradient-to-r from-purple-500/10 to-blue-500/10 cursor-pointer hover:opacity-80"
                    onClick={() => copyToClipboard(combinedResult.quantumEnhancedRate!, 'Quanten-Rate')}
                  >
                    <p className="text-sm font-medium">Quanten-Rate</p>
                    <p className="text-xl font-mono font-bold text-purple-600 dark:text-purple-400">
                      {combinedResult.quantumEnhancedRate?.toLocaleString('de-DE')}
                    </p>
                  </div>
                  {combinedResult.digitalQuantumRate && (
                    <div 
                      className="p-3 rounded-lg border bg-gradient-to-r from-blue-500/10 to-cyan-500/10 cursor-pointer hover:opacity-80"
                      onClick={() => copyToClipboard(combinedResult.digitalQuantumRate!, 'Digital 10-stellig')}
                    >
                      <p className="text-sm font-medium">Digital (10-stellig)</p>
                      <p className="text-xl font-mono font-bold text-blue-600 dark:text-blue-400">
                        {combinedResult.digitalQuantumRate?.toLocaleString('de-DE')}
                      </p>
                    </div>
                  )}
                </div>
                
                {/* Entropie-Details */}
                {combinedResult.entropyMetrics && (
                  <div className="text-xs text-muted-foreground space-y-1 p-2 bg-muted/30 rounded">
                    <p>CPU Jitter: {(combinedResult.entropyMetrics.cpuJitter * 100).toFixed(2)}%</p>
                    <p>Zeit-Kohärenz: {(combinedResult.entropyMetrics.timeCoherence * 100).toFixed(2)}%</p>
                    <p>System-Entropie: {(combinedResult.entropyMetrics.systemEntropy * 100).toFixed(2)}%</p>
                  </div>
                )}
              </div>
            )}

            {/* Export Button */}
            <Button variant="outline" className="w-full" onClick={exportResults}>
              <Download className="h-4 w-4 mr-2" />
              Ergebnis exportieren
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default RateCombinator;
