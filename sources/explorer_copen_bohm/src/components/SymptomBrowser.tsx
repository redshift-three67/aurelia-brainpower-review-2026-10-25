import { useState, useMemo } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Label } from '@/components/ui/label';
import { 
  Search, 
  Database, 
  ChevronRight, 
  ArrowRight,
  X,
  Filter,
  Pill
} from 'lucide-react';

interface SymptomBrowserProps {
  symptoms: string[];
  symptomMap: Map<string, string[]>;
  onSymptomSelect: (symptom: string) => void;
  onRemediesSelect: (remedies: string[]) => void;
}

// Symptom -> Remedies Map invertieren
const invertSymptomMap = (symptomMap: Map<string, string[]>): Map<string, string[]> => {
  const inverted = new Map<string, string[]>();
  
  symptomMap.forEach((symptoms, remedy) => {
    symptoms.forEach(symptom => {
      const existing = inverted.get(symptom) || [];
      if (!existing.includes(remedy)) {
        existing.push(remedy);
      }
      inverted.set(symptom, existing);
    });
  });
  
  return inverted;
};

// Alphabetische Gruppierung erstellen
const groupByFirstLetter = (items: string[]): Map<string, string[]> => {
  const groups = new Map<string, string[]>();
  
  items.forEach(item => {
    const firstLetter = item.charAt(0).toUpperCase();
    const existing = groups.get(firstLetter) || [];
    existing.push(item);
    groups.set(firstLetter, existing);
  });
  
  // Sortieren
  const sorted = new Map([...groups.entries()].sort());
  sorted.forEach((items, key) => {
    sorted.set(key, items.sort());
  });
  
  return sorted;
};

const SymptomBrowser = ({ 
  symptoms, 
  symptomMap, 
  onSymptomSelect, 
  onRemediesSelect 
}: SymptomBrowserProps) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedLetter, setSelectedLetter] = useState<string | null>(null);
  const [selectedSymptom, setSelectedSymptom] = useState<string | null>(null);

  // Symptom -> Remedies Map
  const symptomToRemedies = useMemo(() => invertSymptomMap(symptomMap), [symptomMap]);

  // Alphabetisch gruppierte Symptome
  const groupedSymptoms = useMemo(() => groupByFirstLetter(symptoms), [symptoms]);

  // Gefilterte Symptome basierend auf Suche
  const filteredSymptoms = useMemo(() => {
    if (!searchQuery.trim()) {
      if (selectedLetter) {
        return groupedSymptoms.get(selectedLetter) || [];
      }
      return symptoms;
    }
    
    const query = searchQuery.toLowerCase();
    return symptoms.filter(s => s.toLowerCase().includes(query));
  }, [symptoms, searchQuery, selectedLetter, groupedSymptoms]);

  // Gefilterte und gruppierte Symptome
  const displaySymptoms = useMemo(() => {
    if (searchQuery.trim()) {
      return groupByFirstLetter(filteredSymptoms);
    }
    if (selectedLetter) {
      return new Map([[selectedLetter, groupedSymptoms.get(selectedLetter) || []]]);
    }
    return groupedSymptoms;
  }, [filteredSymptoms, selectedLetter, searchQuery, groupedSymptoms]);

  // Alphabet für schnelle Navigation
  const alphabet = useMemo(() => Array.from(groupedSymptoms.keys()), [groupedSymptoms]);

  // Mittel für ausgewähltes Symptom
  const selectedRemedies = useMemo(() => {
    if (!selectedSymptom) return [];
    return symptomToRemedies.get(selectedSymptom) || [];
  }, [selectedSymptom, symptomToRemedies]);

  const handleSymptomClick = (symptom: string) => {
    setSelectedSymptom(symptom === selectedSymptom ? null : symptom);
  };

  const handleFilterBySymptom = (symptom: string) => {
    onSymptomSelect(symptom);
  };

  const handleLoadRemedies = (remedies: string[]) => {
    onRemediesSelect(remedies);
  };

  return (
    <div className="space-y-4">
      {/* Such-Header */}
      <Card className="border-primary/20">
        <CardHeader className="pb-3">
          <CardTitle className="text-sm flex items-center gap-2">
            <Search className="w-4 h-4 text-primary" />
            Clarke Symptom-Browser
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <Input
              placeholder="Symptom suchen..."
              value={searchQuery}
              onChange={(e) => {
                setSearchQuery(e.target.value);
                setSelectedLetter(null);
              }}
              className="pl-9 pr-8"
            />
            {searchQuery && (
              <Button
                variant="ghost"
                size="sm"
                className="absolute right-0 top-0 h-full w-8 p-0"
                onClick={() => setSearchQuery('')}
              >
                <X className="w-4 h-4 text-muted-foreground" />
              </Button>
            )}
          </div>
          
          {/* Alphabet-Navigation */}
          <div className="flex flex-wrap gap-1">
            <Button
              variant={selectedLetter === null && !searchQuery ? "default" : "outline"}
              size="sm"
              className="h-7 w-7 p-0 text-xs"
              onClick={() => setSelectedLetter(null)}
            >
              *
            </Button>
            {alphabet.map(letter => (
              <Button
                key={letter}
                variant={selectedLetter === letter ? "default" : "outline"}
                size="sm"
                className="h-7 w-7 p-0 text-xs"
                onClick={() => {
                  setSelectedLetter(letter === selectedLetter ? null : letter);
                  setSearchQuery('');
                }}
              >
                {letter}
              </Button>
            ))}
          </div>

          <div className="flex items-center justify-between text-xs text-muted-foreground">
            <span>
              {filteredSymptoms.length} von {symptoms.length} Symptomen
            </span>
            {selectedLetter && (
              <Badge variant="secondary" className="text-xs">
                Buchstabe: {selectedLetter}
              </Badge>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Symptom-Liste und Detail-Ansicht */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Symptom-Liste */}
        <Card className="border-primary/10">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm flex items-center gap-2">
              <Database className="w-4 h-4" />
              Symptome
            </CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            <ScrollArea className="h-[400px]">
              <div className="p-4 space-y-4">
                {Array.from(displaySymptoms.entries()).map(([letter, items]) => (
                  <div key={letter}>
                    <div className="sticky top-0 bg-background/95 backdrop-blur-sm z-10 py-1 mb-2">
                      <Badge variant="outline" className="font-bold">
                        {letter} ({items.length})
                      </Badge>
                    </div>
                    <div className="space-y-1">
                      {items.map((symptom, idx) => {
                        const remedyCount = symptomToRemedies.get(symptom)?.length || 0;
                        const isSelected = selectedSymptom === symptom;
                        
                        return (
                          <div
                            key={idx}
                            className={`flex items-center justify-between p-2 rounded-md cursor-pointer transition-colors ${
                              isSelected 
                                ? 'bg-primary/20 border border-primary/40' 
                                : 'hover:bg-muted/50'
                            }`}
                            onClick={() => handleSymptomClick(symptom)}
                          >
                            <div className="flex items-center gap-2 min-w-0">
                              <ChevronRight className={`w-4 h-4 text-muted-foreground shrink-0 transition-transform ${isSelected ? 'rotate-90' : ''}`} />
                              <span className="text-sm truncate">{symptom}</span>
                            </div>
                            <Badge variant="secondary" className="shrink-0 text-xs">
                              {remedyCount} Mittel
                            </Badge>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                ))}
                
                {filteredSymptoms.length === 0 && (
                  <div className="text-center py-8 text-muted-foreground">
                    <Search className="w-8 h-8 mx-auto mb-2 opacity-50" />
                    <p className="text-sm">Keine Symptome gefunden</p>
                  </div>
                )}
              </div>
            </ScrollArea>
          </CardContent>
        </Card>

        {/* Detail-Ansicht für ausgewähltes Symptom */}
        <Card className={`border-primary/10 ${selectedSymptom ? 'border-primary/30' : ''}`}>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm flex items-center gap-2">
              <Pill className="w-4 h-4" />
              {selectedSymptom ? 'Zugehörige Mittel' : 'Symptom auswählen'}
            </CardTitle>
          </CardHeader>
          <CardContent>
            {!selectedSymptom ? (
              <div className="text-center py-12 text-muted-foreground">
                <ArrowRight className="w-8 h-8 mx-auto mb-2 opacity-50" />
                <p className="text-sm">Wählen Sie ein Symptom aus der Liste</p>
              </div>
            ) : (
              <div className="space-y-4">
                {/* Symptom Header */}
                <div className="p-3 bg-primary/10 rounded-lg">
                  <Label className="text-xs text-muted-foreground">Ausgewähltes Symptom</Label>
                  <p className="font-semibold text-primary">{selectedSymptom}</p>
                </div>

                {/* Aktions-Buttons */}
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleFilterBySymptom(selectedSymptom)}
                    className="flex-1"
                  >
                    <Filter className="w-4 h-4 mr-1" />
                    Ergebnisse filtern
                  </Button>
                  <Button
                    variant="default"
                    size="sm"
                    onClick={() => handleLoadRemedies(selectedRemedies)}
                    className="flex-1"
                  >
                    <Database className="w-4 h-4 mr-1" />
                    {selectedRemedies.length} Mittel laden
                  </Button>
                </div>

                {/* Mittel-Liste */}
                <div className="space-y-1">
                  <Label className="text-xs text-muted-foreground">
                    {selectedRemedies.length} Mittel für dieses Symptom:
                  </Label>
                  <ScrollArea className="h-[280px] rounded border bg-muted/20">
                    <div className="p-2 space-y-1">
                      {selectedRemedies.sort().map((remedy, idx) => {
                        const symptomCount = symptomMap.get(remedy)?.length || 0;
                        return (
                          <div 
                            key={idx} 
                            className="flex items-center justify-between p-2 rounded hover:bg-muted/50"
                          >
                            <span className="text-sm font-medium">{remedy}</span>
                            <span className="text-xs text-muted-foreground">
                              {symptomCount} Symptome
                            </span>
                          </div>
                        );
                      })}
                    </div>
                  </ScrollArea>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default SymptomBrowser;
