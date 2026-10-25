import { useState, useCallback, useMemo, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Input } from '@/components/ui/input';
import { Switch } from '@/components/ui/switch';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { 
  Loader2, 
  ListChecks, 
  Zap, 
  ArrowUpDown, 
  Layers, 
  Sparkles,
  Download,
  Filter,
  ArrowUp,
  ArrowDown,
  X,
  Archive,
  TrendingUp,
  TrendingDown,
  Minus,
  Clock,
  Save,
  History,
  Target,
  Atom,
  Info,
  Play,
  Square,
  Trash2,
  Timer,
  Activity,
  Heart,
  Gauge,
  MapPin,
  Database,
  FolderOpen,
  Plus,
  ChevronDown,
  ChevronUp,
  Brain,
  Bone,
  Utensils,
  Search
} from 'lucide-react';
import HarmonizationManager from './HarmonizationManager';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible';
import { calculateCopenRate } from '@/utils/copenRateGenerator';
import { calculateLevelResonance, LEVELS, LEVELS_DISPLAY, findHighestResonanceLevel, getLevelDisplayName } from '@/utils/levelResonance';
import { getSessionTable, type SourceModule, prepareSessionInsert } from '@/utils/sessionTableRouter';
import { calculateFokusResonanz, FOKUS_OPTIONS } from '@/utils/quantumFocusAlgorithm';
import { supabase } from '@/integrations/supabase/client';
import { useToast } from '@/hooks/use-toast';
import type { KlientenFeldErgebnis } from '@/utils/clientFieldAlgorithms';
import { MERIDIANS, getAllMeridianPointsFlat, getTotalPointCount, getMeridianStats } from '@/utils/meridianPointsDatabase';
import { ANATOMY_DATABASES, getEntriesForDatabase, getAnatomyStatistics } from '@/utils/anatomyDatabases';
import SymptomBrowser from '@/components/SymptomBrowser';
import AnatomyDatabaseOverview from '@/components/AnatomyDatabaseOverview';
import FrequencyDatabaseOverview from '@/components/FrequencyDatabaseOverview';

// Clarke Materia Medica Symptom-Mapping
interface ClarkeSymptomEntry {
  symptom: string;
  remedies: string[];
}

interface WordEnergyTestResult {
  word: string;
  copenRate: number;
  resonanz: number;
  resonanzBasis: number;
  fokusKorrelation: number;
  interferenzMuster: 'konstruktiv' | 'destruktiv' | 'neutral';
  intensität: number;
  polarität: 'positiv' | 'negativ' | 'neutral';
  polaritätWert: number;
  dominanteEbene: number;
  dominanteEbeneWert: number;
  ebenVerteilung: Record<string, number>;
  // Kohärente Harmonisierung Felder
  harmonisierungsWort: string;
  harmonisierungsRate: number;
  // Clarke Materia Medica Symptome (optional)
  clarkeSymptoms?: string[];
}

interface ArchivedTest {
  id: string;
  created_at: string;
  total_words: number;
  average_resonance: number;
  top_items: WordEnergyTestResult[];
  results: WordEnergyTestResult[];
}

interface TrendItem {
  word: string;
  currentResonance: number;
  previousResonance: number;
  trend: 'up' | 'down' | 'stable';
  trendValue: number;
  occurrences: number;
  // Erweiterte Trend-Daten
  currentIntensity?: number;
  currentPolarity?: number;
  currentLevel?: number;
  previousIntensity?: number;
  previousPolarity?: number;
  previousLevel?: number;
  fokusKorrelation?: number;
}

interface CategoryTrends {
  resonanz: TrendItem[];
  intensität: TrendItem[];
  polarität: TrendItem[];
  ebenen: TrendItem[];
}

interface HarmonizationState {
  isActive: boolean;
  isPaused: boolean;
  selectedItems: WordEnergyTestResult[];
  pulseDuration: number; // Sekunden
  pauseDuration: number; // Sekunden
  maxDuration: number; // Minuten
  elapsedSeconds: number;
  currentItemIndex: number;
  inPulsePhase: boolean;
  totalDurationSeconds: number; // Gesamtdauer in Sekunden
  remainingSeconds: number; // Verbleibende Zeit
}

type SortField = 'word' | 'resonanz' | 'intensität' | 'polaritätWert' | 'dominanteEbene' | 'copenRate' | 'symptomCount';
type SortDirection = 'asc' | 'desc';
type PolaritätFilter = 'alle' | 'positiv' | 'negativ' | 'neutral';
type TestMode = 'parallel' | 'sequentiell';

interface WordEnergyTesterProps {
  clientResult: KlientenFeldErgebnis | null;
  clientName: string;
  patientId?: string;
  sourceModule?: string; // 'morphic_field', 'word_energy', etc. - für Session-Isolation
}

const WordEnergyTester = ({ clientResult, clientName, patientId, sourceModule = 'morphic_field' }: WordEnergyTesterProps) => {
  // Bestimme die korrekte Tabelle basierend auf dem Modul
  const sessionTable = getSessionTable(sourceModule as SourceModule);
  const { toast } = useToast();
  const [wordInput, setWordInput] = useState('');
  const [isTesting, setIsTesting] = useState(false);
  const [currentWordIndex, setCurrentWordIndex] = useState(0);
  const [totalWords, setTotalWords] = useState(0);
  const [results, setResults] = useState<WordEnergyTestResult[]>([]);
  const [testMode, setTestMode] = useState<TestMode>('parallel');
  
  // Fokus-State (Quanteninspirierter Algorithmus)
  const [selectedFokus, setSelectedFokus] = useState<string | null>(null);
  const [customFokus, setCustomFokus] = useState('');
  const [fokusGewichtung, setFokusGewichtung] = useState(15); // 15% Standard
  const [customFokusHistory, setCustomFokusHistory] = useState<string[]>(() => {
    try {
      const stored = localStorage.getItem('fokusHistory');
      return stored ? JSON.parse(stored) : [];
    } catch { return []; }
  });
  const [showFokusHistory, setShowFokusHistory] = useState(false);
  
  // Archiv & Trend State
  const [archivedTests, setArchivedTests] = useState<ArchivedTest[]>([]);
  const [trendItems, setTrendItems] = useState<TrendItem[]>([]);
  const [categoryTrends, setCategoryTrends] = useState<CategoryTrends>({
    resonanz: [],
    intensität: [],
    polarität: [],
    ebenen: []
  });
  const [activeTrendCategory, setActiveTrendCategory] = useState<'resonanz' | 'intensität' | 'polarität' | 'ebenen'>('resonanz');
  const [isLoadingArchive, setIsLoadingArchive] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [activeTab, setActiveTab] = useState('test');

  // Harmonization State
  const [harmonization, setHarmonization] = useState<HarmonizationState>({
    isActive: false,
    isPaused: false,
    selectedItems: [],
    pulseDuration: 5,
    pauseDuration: 3,
    maxDuration: 30,
    elapsedSeconds: 0,
    currentItemIndex: 0,
    inPulsePhase: true,
    totalDurationSeconds: 0,
    remainingSeconds: 0
  });
  const [showHarmonization, setShowHarmonization] = useState(false);
  const [harmonizationItemCount, setHarmonizationItemCount] = useState<21 | 42 | 63>(21);
  const harmonizationIntervalRef = useState<ReturnType<typeof setInterval> | null>(null);

  // Schutz für Multi-Session-Harmonisierungen:
  // Steuer-/Abbruch-Buttons in diesem Tab dürfen nur Sessions beeinflussen,
  // die in DIESEM Fenster/Context erzeugt wurden.
  const [managedSessionIds, setManagedSessionIds] = useState<string[]>([]);
  
  // Sortier- und Filter-State
  const [sortField, setSortField] = useState<SortField>('resonanz');
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc');
  const [polaritätFilter, setPolaritätFilter] = useState<PolaritätFilter>('alle');
  const [minResonanz, setMinResonanz] = useState<number>(0);
  const [ebeneFilter, setEbeneFilter] = useState<number | null>(null);
  const [showFilters, setShowFilters] = useState(false);
  
  // Nur Wortenergien-Modus (ohne Rate-Berechnung)
  const [nurWortenergienModus, setNurWortenergienModus] = useState(false);
  
  // Wortlisten-Datenbank State
  const [savedWordLists, setSavedWordLists] = useState<{ id: string; name: string; entries: string[] }[]>([]);
  const [newListName, setNewListName] = useState('');
  const [showListManager, setShowListManager] = useState(false);
  const [isLoadingLists, setIsLoadingLists] = useState(false);
  const [isSavingList, setIsSavingList] = useState(false);
  
  // Clarke Materia Medica Symptom-Map (Remedy -> Symptoms)
  const [clarkeSymptomMap, setClarkeSymptomMap] = useState<Map<string, string[]>>(new Map());
  const [isClarkeLoaded, setIsClarkeLoaded] = useState(false);
  
  // Clarke Symptom-Suche
  const [clarkeSymptomSearch, setClarkeSymptomSearch] = useState('');
  const [allClarkeSymptoms, setAllClarkeSymptoms] = useState<string[]>([]);
  // Effektiver Fokus (Kategorie oder Custom Keywords)
  const effectiveFokus = useMemo(() => {
    if (customFokus.trim()) return customFokus.trim();
    return selectedFokus;
  }, [selectedFokus, customFokus]);

  // Load archived tests and word lists when patient changes
  useEffect(() => {
    if (patientId) {
      loadArchivedTests();
    }
    loadSavedWordLists();
  }, [patientId]);

  // Wortlisten laden
  const loadSavedWordLists = async () => {
    setIsLoadingLists(true);
    try {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) return;

      const { data, error } = await supabase
        .from('word_databases')
        .select('id, name, entries')
        .eq('user_id', user.id)
        .order('name', { ascending: true });

      if (error) throw error;
      setSavedWordLists(data || []);
    } catch (error) {
      console.error('Error loading word lists:', error);
    } finally {
      setIsLoadingLists(false);
    }
  };

  // Wortliste speichern
  const handleSaveWordList = async () => {
    const words = parseWords(wordInput);
    if (words.length === 0 || !newListName.trim()) {
      toast({
        title: "Speichern nicht möglich",
        description: "Geben Sie einen Namen ein und fügen Sie Wörter hinzu",
        variant: "destructive"
      });
      return;
    }

    setIsSavingList(true);
    try {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) throw new Error('Nicht authentifiziert');

      const { error } = await supabase
        .from('word_databases')
        .insert([{
          user_id: user.id,
          name: newListName.trim(),
          entries: words
        }]);

      if (error) throw error;

      toast({
        title: "Liste gespeichert",
        description: `"${newListName}" mit ${words.length} Einträgen gespeichert`,
      });

      setNewListName('');
      await loadSavedWordLists();
    } catch (error) {
      console.error('Error saving word list:', error);
      toast({
        title: "Fehler beim Speichern",
        description: "Wortliste konnte nicht gespeichert werden",
        variant: "destructive"
      });
    } finally {
      setIsSavingList(false);
    }
  };

  // Wortliste laden
  const loadWordList = (list: { name: string; entries: string[] }) => {
    setWordInput(list.entries.join('\n'));
    toast({
      title: "Liste geladen",
      description: `"${list.name}" mit ${list.entries.length} Einträgen`,
    });
  };

  // Wortliste löschen
  const deleteWordList = async (id: string, name: string) => {
    try {
      const { error } = await supabase
        .from('word_databases')
        .delete()
        .eq('id', id);

      if (error) throw error;

      toast({
        title: "Liste gelöscht",
        description: `"${name}" wurde entfernt`,
      });

      await loadSavedWordLists();
    } catch (error) {
      console.error('Error deleting word list:', error);
      toast({
        title: "Fehler beim Löschen",
        variant: "destructive"
      });
    }
  };

  const loadArchivedTests = async () => {
    if (!patientId) return;
    
    setIsLoadingArchive(true);
    try {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) return;

      const { data, error } = await supabase
        .from('word_energy_archives')
        .select('*')
        .eq('patient_id', patientId)
        .eq('user_id', user.id)
        .order('created_at', { ascending: false })
        .limit(20);

      if (error) throw error;

      const archives: ArchivedTest[] = (data || []).map(d => ({
        id: d.id,
        created_at: d.created_at,
        total_words: d.total_words,
        average_resonance: Number(d.average_resonance) || 0,
        top_items: (d.top_items as unknown as WordEnergyTestResult[]) || [],
        results: (d.results as unknown as WordEnergyTestResult[]) || []
      }));

      setArchivedTests(archives);
      calculateTrends(archives);
    } catch (error) {
      console.error('Error loading archives:', error);
    } finally {
      setIsLoadingArchive(false);
    }
  };

  // Normalisiert ebenVerteilung-Keys zu level_1, level_2, etc.
  const normalizeEbenVerteilung = (result: WordEnergyTestResult): number => {
    // FIRST: Check dominanteEbene directly if it's a valid value (1-12)
    if (result.dominanteEbene && result.dominanteEbene >= 1 && result.dominanteEbene <= 12) {
      return result.dominanteEbene;
    }
    
    // SECOND: Extract from ebenVerteilung - supports multiple key formats
    const ebenVerteilung = result.ebenVerteilung || {};
    let maxLevel = 0;
    let maxValue = -1;
    
    for (const [key, value] of Object.entries(ebenVerteilung)) {
      // Match multiple formats: level_1, level_1_physical_particles, etc.
      const match = key.match(/level_(\d+)/);
      if (match && typeof value === 'number') {
        const levelNum = parseInt(match[1]);
        // Only consider levels 1-12
        if (levelNum >= 1 && levelNum <= 12 && value > maxValue) {
          maxValue = value;
          maxLevel = levelNum;
        }
      }
    }
    
    // Return found level or default to 1 (never 0 or invalid)
    return maxLevel >= 1 ? maxLevel : 1;
  };

  const calculateTrends = (archives: ArchivedTest[]) => {
    if (archives.length < 2) {
      setTrendItems([]);
      setCategoryTrends({ resonanz: [], intensität: [], polarität: [], ebenen: [] });
      return;
    }

    // FIX: Count occurrences per SESSION (archive), not per word entry
    // For each word, track which sessions it appeared in and take the BEST value from each session
    const wordSessionMap = new Map<string, { 
      sessionValues: Map<string, {
        resonanz: number;
        intensität: number;
        polarität: number;
        level: number;
        fokusKorrelation: number;
      }>;
    }>();

    // Collect word data per session - take highest resonanz per word per session
    archives.forEach(archive => {
      const sessionId = archive.id;
      archive.results.forEach(result => {
        const existing = wordSessionMap.get(result.word) || { sessionValues: new Map() };
        
        const currentSessionValue = existing.sessionValues.get(sessionId);
        // FIX: Normalize level from ebenVerteilung for robust level tracking
        const normalizedLevel = normalizeEbenVerteilung(result);
        
        if (!currentSessionValue || result.resonanz > currentSessionValue.resonanz) {
          existing.sessionValues.set(sessionId, {
            resonanz: result.resonanz,
            intensität: result.intensität,
            polarität: result.polaritätWert,
            level: normalizedLevel,
            fokusKorrelation: result.fokusKorrelation || 0
          });
        }
        wordSessionMap.set(result.word, existing);
      });
    });

    // Calculate trends for items appearing in more than one SESSION
    const allTrends: TrendItem[] = [];
    wordSessionMap.forEach((data, word) => {
      const sessionCount = data.sessionValues.size;
      if (sessionCount >= 2) {
        // Get values ordered by session recency (archives are already ordered by created_at desc)
        const orderedArchiveIds = archives.map(a => a.id);
        const orderedValues = orderedArchiveIds
          .filter(id => data.sessionValues.has(id))
          .map(id => data.sessionValues.get(id)!);
        
        if (orderedValues.length >= 2) {
          const current = orderedValues[0];
          const previous = orderedValues[1];
          const trendValue = current.resonanz - previous.resonanz;
          
          let trend: 'up' | 'down' | 'stable' = 'stable';
          if (trendValue > 5) trend = 'up';
          else if (trendValue < -5) trend = 'down';

          allTrends.push({
            word,
            currentResonance: current.resonanz,
            previousResonance: previous.resonanz,
            trend,
            trendValue,
            occurrences: sessionCount, // Now correctly counts SESSIONS, not word entries
            currentIntensity: current.intensität,
            previousIntensity: previous.intensität,
            currentPolarity: current.polarität,
            previousPolarity: previous.polarität,
            currentLevel: current.level,
            previousLevel: previous.level,
            fokusKorrelation: current.fokusKorrelation
          });
        }
      }
    });

    // Kategorisierte Trends - Limit 25 statt 15
    const resonanz = [...allTrends]
      .sort((a, b) => Math.abs(b.trendValue) - Math.abs(a.trendValue))
      .slice(0, 25);

    const intensität = [...allTrends]
      .sort((a, b) => Math.abs((b.currentIntensity || 0) - (b.previousIntensity || 0)) - 
                       Math.abs((a.currentIntensity || 0) - (a.previousIntensity || 0)))
      .slice(0, 25);

    const polarität = [...allTrends]
      .sort((a, b) => Math.abs((b.currentPolarity || 0) - (b.previousPolarity || 0)) - 
                       Math.abs((a.currentPolarity || 0) - (a.previousPolarity || 0)))
      .slice(0, 25);

    // FIX: Include all items with valid levels (1-12), sort by level change then by current level
    const ebenen = [...allTrends]
      .filter(t => (t.currentLevel || 0) >= 1 && (t.currentLevel || 0) <= 12)
      .sort((a, b) => {
        // First by level change magnitude
        const aDiff = Math.abs((a.currentLevel || 0) - (a.previousLevel || 0));
        const bDiff = Math.abs((b.currentLevel || 0) - (b.previousLevel || 0));
        if (bDiff !== aDiff) return bDiff - aDiff;
        // Then by current level value (higher first)
        return (b.currentLevel || 0) - (a.currentLevel || 0);
      })
      .slice(0, 25);

    setCategoryTrends({ resonanz, intensität, polarität, ebenen });
    setTrendItems(resonanz);
  };

  // Gefilterte und sortierte Ergebnisse
  const filteredAndSortedResults = useMemo(() => {
    let filtered = [...results];
    
    if (polaritätFilter !== 'alle') {
      filtered = filtered.filter(r => r.polarität === polaritätFilter);
    }
    
    if (minResonanz > 0) {
      filtered = filtered.filter(r => r.resonanz >= minResonanz);
    }
    
    if (ebeneFilter !== null) {
      filtered = filtered.filter(r => r.dominanteEbene === ebeneFilter);
    }
    
    // Clarke Symptom-Suche Filter
    if (clarkeSymptomSearch.trim() && isClarkeLoaded) {
      const searchTerms = clarkeSymptomSearch.toLowerCase().split(',').map(s => s.trim()).filter(s => s);
      filtered = filtered.filter(r => {
        if (!r.clarkeSymptoms || r.clarkeSymptoms.length === 0) return false;
        const symptomsLower = r.clarkeSymptoms.map(s => s.toLowerCase());
        return searchTerms.some(term => 
          symptomsLower.some(symptom => symptom.includes(term))
        );
      });
    }
    
    filtered.sort((a, b) => {
      let comparison = 0;
      switch (sortField) {
        case 'word':
          comparison = a.word.localeCompare(b.word);
          break;
        case 'resonanz':
          comparison = a.resonanz - b.resonanz;
          break;
        case 'intensität':
          comparison = a.intensität - b.intensität;
          break;
        case 'polaritätWert':
          comparison = a.polaritätWert - b.polaritätWert;
          break;
        case 'dominanteEbene':
          comparison = a.dominanteEbene - b.dominanteEbene;
          break;
        case 'copenRate':
          comparison = a.copenRate - b.copenRate;
          break;
        case 'symptomCount':
          comparison = (a.clarkeSymptoms?.length || 0) - (b.clarkeSymptoms?.length || 0);
          break;
      }
      return sortDirection === 'desc' ? -comparison : comparison;
    });
    
    return filtered;
  }, [results, sortField, sortDirection, polaritätFilter, minResonanz, ebeneFilter, clarkeSymptomSearch, isClarkeLoaded]);

  const resetFilters = () => {
    setPolaritätFilter('alle');
    setMinResonanz(0);
    setEbeneFilter(null);
    setClarkeSymptomSearch('');
  };

  const hasActiveFilters = polaritätFilter !== 'alle' || minResonanz > 0 || ebeneFilter !== null || clarkeSymptomSearch.trim() !== '';

  const parseWords = (input: string): string[] => {
    return input
      .split('\n')
      .map(w => w.trim())
      .filter(w => w.length > 0);
  };

  const calculateResonanz = (copenRate: number, clientWellenfunktion: number): number => {
    const ratio = copenRate / (clientWellenfunktion || 1);
    const normalized = Math.abs(1 - (ratio % 1));
    // Deterministischer Jitter basierend auf Rate statt Math.random()
    const deterministicJitter = ((copenRate % 1000) / 1000) * 15;
    return Math.min(100, normalized * 100 + deterministicJitter);
  };

  const calculateIntensität = (copenRate: number, resonanz: number): number => {
    const rateStrength = Math.min(100, Math.log10(copenRate) * 15);
    return Math.min(100, (rateStrength * 0.6) + (resonanz * 0.4));
  };

  const calculatePolarität = (word: string, copenRate: number): { typ: 'positiv' | 'negativ' | 'neutral', wert: number } => {
    const letterSum = word.toUpperCase().split('').reduce((sum, ch) => {
      if (ch >= 'A' && ch <= 'Z') return sum + (ch.charCodeAt(0) - 64);
      return sum;
    }, 0);
    
    const polaritätRaw = ((copenRate * letterSum) % 200) - 100;
    const polaritätWert = polaritätRaw / 100;
    
    if (polaritätWert > 0.15) return { typ: 'positiv', wert: polaritätWert };
    if (polaritätWert < -0.15) return { typ: 'negativ', wert: polaritätWert };
    return { typ: 'neutral', wert: polaritätWert };
  };

  const testWordEnergy = useCallback((word: string, clientWellenfunktion: number): WordEnergyTestResult => {
    // Wenn nurWortenergienModus aktiv: Keine Rate-Berechnung, nur Wort durchreichen
    const copenRate = nurWortenergienModus ? 0 : calculateCopenRate(word, 0, 'D', 'latin').rate;
    const ebenVerteilung = calculateLevelResonance(copenRate, word);
    const { level: dominanteEbene, value: dominanteEbeneWert } = findHighestResonanceLevel(ebenVerteilung);
    const resonanzBasis = nurWortenergienModus ? 50 : calculateResonanz(copenRate, clientWellenfunktion);
    
    // Quanteninspirierte Fokus-Resonanz berechnen
    const fokusResult = calculateFokusResonanz(
      word,
      resonanzBasis,
      effectiveFokus,
      clientWellenfunktion,
      fokusGewichtung / 100 // Umrechnung von Prozent
    );
    
    const intensität = calculateIntensität(copenRate, fokusResult.kombinierteResonanz);
    const { typ: polarität, wert: polaritätWert } = calculatePolarität(word, copenRate);
    
    // harmonisierungsWort und harmonisierungsRate werden jetzt NICHT mehr automatisch berechnet
    // Die "Kohärente adaptive Regulation" Transformation erfolgt optional im HarmonizationManager
    const harmonisierungsWort = word; // Kein automatisches Präfix mehr
    const harmonisierungsRate = copenRate; // Standard-Rate ohne Transformation
    
    // Clarke Symptome zuordnen (case-insensitive) - NUR für Anzeige, nicht für Rate-Berechnung
    // FIX: Case-insensitive matching for Clarke symptom lookup
    let clarkeSymptoms: string[] = [];
    if (clarkeSymptomMap.size > 0) {
      // Try exact match first
      clarkeSymptoms = clarkeSymptomMap.get(word) || [];
      
      // If no exact match, try case-insensitive
      if (clarkeSymptoms.length === 0) {
        const wordLower = word.toLowerCase();
        for (const [remedy, symptoms] of clarkeSymptomMap.entries()) {
          if (remedy.toLowerCase() === wordLower) {
            clarkeSymptoms = symptoms;
            break;
          }
        }
      }
    }
    
    return {
      word,
      copenRate,
      resonanz: fokusResult.kombinierteResonanz,
      resonanzBasis: fokusResult.baseResonanz,
      fokusKorrelation: fokusResult.fokusKorrelation,
      interferenzMuster: fokusResult.interferenzMuster,
      intensität: Math.round(intensität * 10) / 10,
      polarität,
      polaritätWert: Math.round(polaritätWert * 100) / 100,
      dominanteEbene,
      dominanteEbeneWert: Math.round(dominanteEbeneWert * 10) / 10,
      ebenVerteilung,
      harmonisierungsWort,
      harmonisierungsRate,
      clarkeSymptoms: clarkeSymptoms.length > 0 ? clarkeSymptoms : undefined
    };
  }, [effectiveFokus, fokusGewichtung, clarkeSymptomMap, nurWortenergienModus]);

  // Custom Fokus zur Historie hinzufügen (persistent in localStorage)
  const addToFokusHistory = useCallback((fokus: string) => {
    if (!fokus.trim()) return;
    setCustomFokusHistory(prev => {
      const filtered = prev.filter(f => f !== fokus.trim());
      const updated = [fokus.trim(), ...filtered].slice(0, 10);
      try {
        localStorage.setItem('fokusHistory', JSON.stringify(updated));
      } catch (e) {
        console.error('Failed to save fokus history:', e);
      }
      return updated;
    });
  }, []);

  // PARALLEL TESTING - alle Wörter gleichzeitig
  const handleParallelTest = useCallback(async () => {
    const words = parseWords(wordInput);
    if (words.length === 0) return;

    // Custom Fokus zur Historie hinzufügen
    if (customFokus.trim()) {
      addToFokusHistory(customFokus.trim());
    }

    setIsTesting(true);
    setResults([]);
    setTotalWords(words.length);
    setCurrentWordIndex(0);

    const clientWellenfunktion = clientResult?.klientenWellenfunktion || 1;

    // Kleine Verzögerung für UI-Update
    await new Promise(resolve => setTimeout(resolve, 50));

    // Alle Wörter parallel berechnen
    const allResults = words.map(word => testWordEnergy(word, clientWellenfunktion));
    
    setResults(allResults);
    setCurrentWordIndex(words.length);
    setIsTesting(false);

    toast({
      title: "Parallele Analyse abgeschlossen",
      description: `${allResults.length} Wortenergien in < 1 Sekunde getestet`,
    });
  }, [wordInput, clientResult, testWordEnergy, toast, customFokus, addToFokusHistory]);

  // SEQUENTIELL TESTING - mit visueller Sequenz
  const handleSequentialTest = async () => {
    const words = parseWords(wordInput);
    if (words.length === 0) return;

    // Custom Fokus zur Historie hinzufügen
    if (customFokus.trim()) {
      addToFokusHistory(customFokus.trim());
    }

    setIsTesting(true);
    setResults([]);
    setCurrentWordIndex(0);
    setTotalWords(words.length);

    const clientWellenfunktion = clientResult?.klientenWellenfunktion || 1;
    const newResults: WordEnergyTestResult[] = [];

    for (let i = 0; i < words.length; i++) {
      setCurrentWordIndex(i + 1);
      await new Promise(resolve => setTimeout(resolve, 50)); // Reduziert von 150ms auf 50ms
      
      const result = testWordEnergy(words[i], clientWellenfunktion);
      newResults.push(result);
      setResults([...newResults]);
    }

    setIsTesting(false);
    toast({
      title: "Sequentielle Analyse abgeschlossen",
      description: `${newResults.length} Wortenergien getestet`,
    });
  };

  const handleStartTest = () => {
    if (testMode === 'parallel') {
      handleParallelTest();
    } else {
      handleSequentialTest();
    }
  };

  // ARCHIVIEREN
  const handleSaveToArchive = async () => {
    if (results.length === 0 || !patientId) {
      toast({
        title: "Speichern nicht möglich",
        description: "Keine Ergebnisse oder kein Klient verknüpft",
        variant: "destructive"
      });
      return;
    }

    setIsSaving(true);
    try {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) throw new Error('Nicht authentifiziert');

      const avgResonance = results.reduce((sum, r) => sum + r.resonanz, 0) / results.length;
      const topItems = [...results].sort((a, b) => b.resonanz - a.resonanz).slice(0, 5);

      const { error } = await supabase
        .from('word_energy_archives')
        .insert([{
          user_id: user.id,
          patient_id: patientId,
          client_name: clientName,
          client_wellenfunktion: clientResult?.klientenWellenfunktion || 0,
          results: JSON.parse(JSON.stringify(results)),
          total_words: results.length,
          average_resonance: avgResonance,
          top_items: JSON.parse(JSON.stringify(topItems))
        }]);

      if (error) throw error;

      toast({
        title: "Archiviert",
        description: `${results.length} Wortenergien für ${clientName} gespeichert`,
      });

      await loadArchivedTests();
    } catch (error) {
      console.error('Error saving archive:', error);
      toast({
        title: "Fehler beim Speichern",
        description: "Archivierung fehlgeschlagen",
        variant: "destructive"
      });
    } finally {
      setIsSaving(false);
    }
  };

  const loadArchivedResult = (archive: ArchivedTest) => {
    setResults(archive.results);
    setActiveTab('test');
    toast({
      title: "Archiv geladen",
      description: `${archive.total_words} Ergebnisse vom ${new Date(archive.created_at).toLocaleDateString('de-DE')}`,
    });
  };

  const exportToCSV = () => {
    if (results.length === 0) return;
    
    const headers = 'Wortenergie,Copen-Rate,Resonanz %,Intensität %,Polarität,Polarität-Wert,Dominante Ebene,Ebene-Wert %\n';
    const rows = results.map(r => 
      `"${r.word}",${r.copenRate},${r.resonanz},${r.intensität},${r.polarität},${r.polaritätWert},${getLevelDisplayName(r.dominanteEbene)},${r.dominanteEbeneWert}`
    ).join('\n');
    
    const csv = headers + rows;
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `wortenergie-test-${clientName || 'klient'}-${Date.now()}.csv`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const getPolaritätColor = (polarität: 'positiv' | 'negativ' | 'neutral') => {
    switch (polarität) {
      case 'positiv': return 'bg-green-500';
      case 'negativ': return 'bg-red-500';
      case 'neutral': return 'bg-gray-500';
    }
  };

  const getResonanzColor = (resonanz: number) => {
    if (resonanz >= 80) return 'text-green-500';
    if (resonanz >= 60) return 'text-emerald-500';
    if (resonanz >= 40) return 'text-yellow-500';
    return 'text-orange-500';
  };

  const getTrendIcon = (trend: 'up' | 'down' | 'stable') => {
    switch (trend) {
      case 'up': return <TrendingUp className="w-4 h-4 text-green-500" />;
      case 'down': return <TrendingDown className="w-4 h-4 text-red-500" />;
      case 'stable': return <Minus className="w-4 h-4 text-gray-500" />;
    }
  };

  // Persistente Harmonisierung starten (Cloud-basiert) - Sessions werden NICHT sofort gestartet
  // Der Benutzer muss explizit "Starten" drücken in der SessionStatusList
  const startHarmonization = async () => {
    const topItems = [...filteredAndSortedResults].slice(0, harmonizationItemCount);
    if (topItems.length === 0) {
      toast({
        title: "Keine Items",
        description: "Keine Ergebnisse zum Harmonisieren vorhanden",
        variant: "destructive"
      });
      return;
    }

    if (!patientId) {
      toast({
        title: "Kein Klient ausgewählt",
        description: "Bitte verknüpfen Sie einen Klienten für persistente Harmonisierung",
        variant: "destructive"
      });
      return;
    }

    try {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) {
        toast({
          title: "Nicht authentifiziert",
          description: "Bitte melden Sie sich an",
          variant: "destructive"
        });
        return;
      }

      // Calculate duration per item (total duration / number of items)
      const totalDurationSeconds = harmonization.maxDuration * 60;
      const durationPerItem = Math.floor(totalDurationSeconds / topItems.length);

      // Erzeuge eine eindeutige Batch-ID für diese Analyse-Session
      const batchId = crypto.randomUUID();

      // Create individual harmonization sessions for each item
      // Sessions are created with status 'queued' and NO job_started_at
      // → sie starten NICHT automatisch. Der Benutzer startet sie explizit in der SessionStatusList.
      const sessionsToCreate = topItems.map(item => {
        const baseSession = {
          user_id: user.id,
          patient_id: patientId,
          word: item.harmonisierungsWort,
          copen_rate: item.harmonisierungsRate?.toString() || item.copenRate.toString(),
          tested_potency: 'D0',
          duration_seconds: durationPerItem,
          remaining_seconds: durationPerItem,
          status: 'queued' as const,
          pulse_pause_active: harmonization.pulseDuration !== harmonization.pauseDuration || harmonization.pulseDuration !== 5,
          pulse_seconds: harmonization.pulseDuration,
          pause_seconds: harmonization.pauseDuration,
          progress: 0,
          batch_id: batchId,
        };
        
        // Für morphic_field: keine source_module, dafür optionale Morphic-Feld-Daten
        if (sourceModule === 'morphic_field') {
          return {
            ...baseSession,
            // field_intensity und coherence können später bei Bedarf ergänzt werden
          };
        }
        
        // Für andere Module: source_module explizit setzen
        return {
          ...baseSession,
          source_module: sourceModule,
        };
      });

      // Verwende die korrekte Tabelle basierend auf sourceModule
      const { data, error } = await supabase
        .from(sessionTable)
        .insert(sessionsToCreate)
        .select('id');

      if (error) throw error;

      // Speichere die IDs der erstellten Sessions für dieses Fenster
      const createdIds = (data || []).map((s: { id: string }) => s.id);
      setManagedSessionIds(prev => [...prev, ...createdIds]);

      // DO NOT trigger worker here - sessions should wait for explicit user action
      // The user will start sessions via the SessionStatusList "Starten" button

      toast({
        title: "Harmonisierung vorbereitet",
        description: `${topItems.length} Sessions erstellt (${Math.floor(durationPerItem / 60)}min je). Starten Sie diese über die Session-Status-Liste.`,
      });

      // Update local state to show harmonization is pending (not yet active)
      setHarmonization(prev => ({
        ...prev,
        isActive: true,
        isPaused: false,
        selectedItems: topItems,
        elapsedSeconds: 0,
        currentItemIndex: 0,
        inPulsePhase: false, // Not active yet
        totalDurationSeconds,
        remainingSeconds: totalDurationSeconds
      }));

    } catch (error) {
      console.error('Error creating harmonization sessions:', error);
      toast({
        title: "Fehler",
        description: "Harmonisierung konnte nicht vorbereitet werden",
        variant: "destructive"
      });
    }
  };

  // Harmonisierung pausieren/fortsetzen
  const stopHarmonization = async () => {
    if (!patientId) return;
    
    try {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) return;

      // Pause/Fortsetzen nur für Sessions, die in diesem Fenster erstellt wurden
      if (managedSessionIds.length === 0) {
        toast({
          title: "Hinweis",
          description: "Zum Schutz von Multi-Session-Harmonisierungen steuert dieser Button nur Sessions, die in diesem Fenster erstellt wurden. Bitte nutze den Harmonisierung-Tab zur Verwaltung.",
        });
        return;
      }

      const newStatus = harmonization.isPaused ? 'running' : 'paused';

      await supabase
        .from(sessionTable)
        .update({ status: newStatus })
        .eq('user_id', user.id)
        .in('id', managedSessionIds)
        .in('status', ['running', 'paused']);

      setHarmonization(prev => ({
        ...prev,
        isPaused: !prev.isPaused
      }));

      toast({
        title: harmonization.isPaused ? "Fortgesetzt" : "Pausiert",
        description: harmonization.isPaused ? "Harmonisierung wird fortgesetzt" : "Harmonisierung wurde pausiert",
      });
    } catch (error) {
      console.error('Error toggling harmonization:', error);
    }
  };

  // Harmonisierung löschen/abbrechen
  const cancelHarmonization = async () => {
    if (!patientId) {
      setHarmonization({
        isActive: false,
        isPaused: false,
        selectedItems: [],
        pulseDuration: harmonization.pulseDuration,
        pauseDuration: harmonization.pauseDuration,
        maxDuration: harmonization.maxDuration,
        elapsedSeconds: 0,
        currentItemIndex: 0,
        inPulsePhase: true,
        totalDurationSeconds: 0,
        remainingSeconds: 0
      });
      return;
    }

    try {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) return;

      // Nur Sessions abbrechen, die in DIESEM Fenster erstellt wurden
      if (managedSessionIds.length === 0) {
        toast({
          title: "Hinweis",
          description: "Keine Sessions zum Abbrechen. Nutze den Harmonisierung-Tab für globale Verwaltung.",
        });
        setHarmonization(prev => ({ ...prev, isActive: false }));
        return;
      }

      await supabase
        .from(sessionTable)
        .update({ status: 'cancelled', completed_at: new Date().toISOString() })
        .eq('user_id', user.id)
        .in('id', managedSessionIds)
        .in('status', ['queued', 'pending', 'running', 'paused']);

      // Clear managed IDs nach Abbruch
      setManagedSessionIds([]);

      setHarmonization({
        isActive: false,
        isPaused: false,
        selectedItems: [],
        pulseDuration: harmonization.pulseDuration,
        pauseDuration: harmonization.pauseDuration,
        maxDuration: harmonization.maxDuration,
        elapsedSeconds: 0,
        currentItemIndex: 0,
        inPulsePhase: true,
        totalDurationSeconds: 0,
        remainingSeconds: 0
      });

      toast({
        title: "Harmonisierung abgebrochen",
        description: "Die Sessions dieses Fensters wurden beendet",
      });
    } catch (error) {
      console.error('Error cancelling harmonization:', error);
    }
  };

  // Realtime subscription + Polling for harmonization updates
  // NUR für Sessions, die in DIESEM Fenster erstellt wurden (managedSessionIds)
  useEffect(() => {
    if (!patientId) return;

    // Wenn dieses Fenster keine Sessions verwaltet, NICHT den Zustand zurücksetzen!
    // Das würde parallele Analysen im anderen Fenster stören.
    // Wir zeigen einfach nichts im Test-Tab an.
    if (managedSessionIds.length === 0) {
      // KEIN Reset hier - nur Skip der Subscription
      return;
    }

    const loadActiveSessions = async () => {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) return;

      const { data: activeSessions } = await supabase
        .from(sessionTable)
        .select('*')
        .eq('user_id', user.id)
        .in('id', managedSessionIds)
        .in('status', ['queued', 'pending', 'running', 'paused'])
        .order('created_at', { ascending: true });

      if (activeSessions && activeSessions.length > 0) {
        // Reconstruct harmonization state from active sessions
        const topItems = activeSessions.map(s => ({
          word: s.word.replace('Kohärente adaptive Regulation ', ''),
          copenRate: parseInt(s.copen_rate || '0'),
          resonanz: 0,
          resonanzBasis: 0,
          fokusKorrelation: 0,
          interferenzMuster: 'neutral' as const,
          intensität: 0,
          polarität: 'neutral' as const,
          polaritätWert: 0,
          dominanteEbene: 1,
          dominanteEbeneWert: 0,
          ebenVerteilung: {},
          harmonisierungsWort: s.word,
          harmonisierungsRate: parseInt(s.copen_rate || '0')
        }));

        const runningSession = activeSessions.find(s => s.status === 'running');
        const pausedSession = activeSessions.find(s => s.status === 'paused');
        const currentSession = runningSession || pausedSession || activeSessions[0];
        const currentIndex = runningSession
          ? activeSessions.findIndex(s => s.id === runningSession.id)
          : pausedSession
            ? activeSessions.findIndex(s => s.id === pausedSession.id)
            : 0;

        // Calculate total duration and remaining across all sessions
        const totalDurationSeconds = activeSessions.reduce((sum, s) => sum + s.duration_seconds, 0);
        const totalRemainingSeconds = activeSessions.reduce((sum, s) => sum + (s.remaining_seconds ?? s.duration_seconds), 0);
        const elapsedSeconds = totalDurationSeconds - totalRemainingSeconds;

        setHarmonization(prev => ({
          ...prev,
          isActive: true,
          isPaused: !!pausedSession && !runningSession,
          selectedItems: topItems,
          currentItemIndex: currentIndex,
          pulseDuration: currentSession.pulse_seconds || 5,
          pauseDuration: currentSession.pause_seconds || 3,
          maxDuration: Math.ceil(totalDurationSeconds / 60),
          totalDurationSeconds,
          remainingSeconds: totalRemainingSeconds,
          elapsedSeconds,
          inPulsePhase: runningSession !== undefined
        }));
      } else {
        setHarmonization(prev => ({
          ...prev,
          isActive: false,
          selectedItems: [],
          elapsedSeconds: 0,
          remainingSeconds: 0,
          totalDurationSeconds: 0
        }));
      }
    };

    // Initial load
    loadActiveSessions();

    // Polling every 3 seconds for reliable timer updates
    const pollInterval = setInterval(loadActiveSessions, 3000);

    // Realtime subscription for instant updates
    const channel = supabase
      .channel(`harmonization-${sourceModule}-${patientId}`)
      .on(
        'postgres_changes',
        {
          event: '*',
          schema: 'public',
          table: sessionTable,
          filter: `patient_id=eq.${patientId}`
        },
        () => loadActiveSessions()
      )
      .subscribe();

    return () => {
      clearInterval(pollInterval);
      supabase.removeChannel(channel);
    };
  }, [patientId, managedSessionIds]);

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <Card className="border-primary/20 mt-6">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <ListChecks className="w-6 h-6 text-primary" />
          Wortenergie-Abtestung
        </CardTitle>
        <CardDescription>
          Analyse von Wortenergien im Bezug zum Klienten 
          {clientName && <span className="font-medium text-primary ml-1">({clientName})</span>}
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {!clientResult && (
          <div className="text-center py-6 text-muted-foreground bg-muted/30 rounded-lg">
            <Sparkles className="w-8 h-8 mx-auto mb-2 opacity-50" />
            <p>Bitte zuerst eine Klienten-Feldanalyse durchführen</p>
          </div>
        )}

        {clientResult && (
          <Tabs value={activeTab} onValueChange={setActiveTab}>
            <TabsList className="grid w-full grid-cols-7">
              <TabsTrigger value="test" className="flex items-center gap-2">
                <Zap className="w-4 h-4" />
                Test
              </TabsTrigger>
              <TabsTrigger value="harmonisierung" className="flex items-center gap-2">
                <Activity className="w-4 h-4" />
                Harmonisierung
              </TabsTrigger>
              <TabsTrigger value="anatomie" className="flex items-center gap-2">
                <Bone className="w-4 h-4" />
                Anatomie
              </TabsTrigger>
              <TabsTrigger value="frequenzen" className="flex items-center gap-2">
                <Sparkles className="w-4 h-4" />
                Frequenzen
              </TabsTrigger>
              <TabsTrigger value="symptome" className="flex items-center gap-2">
                <Search className="w-4 h-4" />
                Symptome
              </TabsTrigger>
              <TabsTrigger value="archiv" className="flex items-center gap-2">
                <Archive className="w-4 h-4" />
                Archiv
              </TabsTrigger>
              <TabsTrigger value="trends" className="flex items-center gap-2">
                <TrendingUp className="w-4 h-4" />
                Trends
              </TabsTrigger>
            </TabsList>

            {/* TEST TAB */}
            <TabsContent value="test" className="space-y-4">
              {/* Test Mode Toggle */}
              <div className="flex items-center justify-between p-3 bg-muted/30 rounded-lg flex-wrap gap-3">
                <div className="flex items-center gap-3">
                  <Label htmlFor="testMode" className="text-sm">Test-Modus:</Label>
                  <div className="flex items-center gap-2">
                    <span className={`text-xs ${testMode === 'sequentiell' ? 'text-primary font-medium' : 'text-muted-foreground'}`}>
                      Sequentiell
                    </span>
                    <Switch
                      id="testMode"
                      checked={testMode === 'parallel'}
                      onCheckedChange={(checked) => setTestMode(checked ? 'parallel' : 'sequentiell')}
                    />
                    <span className={`text-xs ${testMode === 'parallel' ? 'text-primary font-medium' : 'text-muted-foreground'}`}>
                      Parallel ⚡
                    </span>
                  </div>
                </div>
                
                {/* Nur Wortenergien Modus Toggle */}
                <div className="flex items-center gap-3 border-l border-border pl-3">
                  <Label htmlFor="nurWortenergien" className="text-sm flex items-center gap-1">
                    Nur Wortenergien
                    <span className="text-xs text-muted-foreground">(ohne Raten)</span>
                  </Label>
                  <Switch
                    id="nurWortenergien"
                    checked={nurWortenergienModus}
                    onCheckedChange={setNurWortenergienModus}
                  />
                  {nurWortenergienModus && (
                    <Badge variant="outline" className="bg-amber-500/10 text-amber-600 border-amber-500/30">
                      Aktiv
                    </Badge>
                  )}
                </div>
                
                <Badge variant={testMode === 'parallel' ? 'default' : 'secondary'}>
                  {testMode === 'parallel' ? '< 1s' : '~' + (parseWords(wordInput).length * 0.05).toFixed(1) + 's'}
                </Badge>
              </div>

              {/* Fokus-Auswahl (Quanteninspiriert) */}
              <Card className="border-primary/30 bg-gradient-to-r from-primary/5 to-transparent">
                <CardContent className="pt-4">
                  <div className="flex items-center gap-2 mb-3">
                    <Target className="w-5 h-5 text-primary" />
                    <Label className="font-medium">Symptom-Fokus</Label>
                    <TooltipProvider>
                      <Tooltip>
                        <TooltipTrigger>
                          <Info className="w-4 h-4 text-muted-foreground" />
                        </TooltipTrigger>
                        <TooltipContent className="max-w-xs">
                          <p className="text-xs">
                            <strong>Quanteninspirierter Algorithmus:</strong> Nutzt Grover-ähnliche Amplitude-Amplifikation 
                            für sanfte Priorisierung symptomrelevanter Wortenergien ohne die Klientenfeld-Präzision zu stören.
                          </p>
                        </TooltipContent>
                      </Tooltip>
                    </TooltipProvider>
                    {effectiveFokus && (
                      <Badge variant="secondary" className="ml-auto flex items-center gap-1">
                        <Atom className="w-3 h-3" />
                        Aktiv: {fokusGewichtung}%
                      </Badge>
                    )}
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                    <div className="space-y-1">
                      <Label className="text-xs text-muted-foreground">Kategorie</Label>
                      <Select 
                        value={selectedFokus ?? undefined}
                        onValueChange={(v) => {
                          if (v === '__none__') {
                            setSelectedFokus(null);
                            setCustomFokus('');
                            return;
                          }
                          setSelectedFokus(v);
                          setCustomFokus('');
                        }}
                      >
                        <SelectTrigger className="h-9">
                          <SelectValue placeholder="Fokus wählen..." />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="__none__">Kein Fokus</SelectItem>
                          {FOKUS_OPTIONS.map(f => (
                            <SelectItem key={f} value={f}>{f}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                    
                    <div className="space-y-1 relative">
                      <Label className="text-xs text-muted-foreground">Oder: Custom Keywords</Label>
                      <div className="relative">
                        <Input
                          placeholder="herz, rhythmus, blut..."
                          value={customFokus}
                          onChange={(e) => {
                            setCustomFokus(e.target.value);
                            if (e.target.value) setSelectedFokus(null);
                          }}
                          onFocus={() => customFokusHistory.length > 0 && setShowFokusHistory(true)}
                          onBlur={() => setTimeout(() => setShowFokusHistory(false), 200)}
                          className="h-9 text-sm pr-8"
                        />
                        {customFokusHistory.length > 0 && (
                          <Button
                            variant="ghost"
                            size="sm"
                            className="absolute right-0 top-0 h-9 w-8 p-0"
                            onClick={() => setShowFokusHistory(!showFokusHistory)}
                          >
                            <History className="w-4 h-4 text-muted-foreground" />
                          </Button>
                        )}
                        {showFokusHistory && customFokusHistory.length > 0 && (
                          <div className="absolute z-50 top-10 left-0 right-0 bg-popover border rounded-md shadow-lg p-1 max-h-40 overflow-y-auto">
                            {customFokusHistory.map((item, idx) => (
                              <button
                                key={idx}
                                className="w-full text-left px-2 py-1.5 text-sm rounded hover:bg-muted transition-colors"
                                onClick={() => {
                                  setCustomFokus(item);
                                  setSelectedFokus(null);
                                  setShowFokusHistory(false);
                                }}
                              >
                                {item}
                              </button>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                    
                    <div className="space-y-1">
                      <Label className="text-xs text-muted-foreground">Gewichtung: {fokusGewichtung}%</Label>
                      <div className="flex items-center gap-2">
                        <input
                          type="range"
                          min={5}
                          max={30}
                          value={fokusGewichtung}
                          onChange={(e) => setFokusGewichtung(Number(e.target.value))}
                          className="flex-1 h-2 bg-muted rounded-lg appearance-none cursor-pointer accent-primary"
                        />
                        <span className="text-xs text-muted-foreground w-8">{fokusGewichtung}%</span>
                      </div>
                      <p className="text-[10px] text-muted-foreground">Empfohlen: 10-20%</p>
                    </div>
                  </div>
                  
                  {effectiveFokus && (
                    <div className="mt-3 pt-3 border-t border-border/50">
                      <p className="text-xs text-muted-foreground flex items-center gap-2">
                        <Atom className="w-3 h-3" />
                        Fokus-Korrelation verstärkt symptomrelevante Ergebnisse durch Interferenzmuster-Analyse
                      </p>
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Wortlisten-Datenbank */}
              <Collapsible open={showListManager} onOpenChange={setShowListManager}>
                <Card className="border-primary/20">
                  <CollapsibleTrigger asChild>
                    <CardHeader className="cursor-pointer hover:bg-muted/30 transition-colors py-3">
                      <div className="flex items-center justify-between">
                        <CardTitle className="text-sm flex items-center gap-2">
                          <Database className="w-4 h-4 text-primary" />
                          Wortlisten-Datenbank
                          {savedWordLists.length > 0 && (
                            <Badge variant="secondary" className="ml-2">{savedWordLists.length}</Badge>
                          )}
                        </CardTitle>
                        {showListManager ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                      </div>
                    </CardHeader>
                  </CollapsibleTrigger>
                  <CollapsibleContent>
                    <CardContent className="pt-0 space-y-3">
                      {/* Speichern */}
                      <div className="flex gap-2">
                        <Input
                          placeholder="Name der Liste..."
                          value={newListName}
                          onChange={(e) => setNewListName(e.target.value)}
                          className="flex-1"
                          disabled={isSavingList}
                        />
                        <Button
                          onClick={handleSaveWordList}
                          disabled={isSavingList || parseWords(wordInput).length === 0 || !newListName.trim()}
                          size="sm"
                        >
                          {isSavingList ? (
                            <Loader2 className="w-4 h-4 animate-spin" />
                          ) : (
                            <>
                              <Plus className="w-4 h-4 mr-1" />
                              Speichern ({parseWords(wordInput).length})
                            </>
                          )}
                        </Button>
                      </div>

                      {/* Schnellzugriff-Buttons */}
                      <div className="space-y-2">
                        <Label className="text-xs text-muted-foreground">Schnellzugriff - Meridiane & Homöopathie</Label>
                        <div className="flex flex-wrap gap-2">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => {
                              const points = getAllMeridianPointsFlat();
                              setWordInput(points.join('\n'));
                              toast({
                                title: "Meridianpunkte geladen",
                                description: `${points.length} Akupunkturpunkte bereit zur Analyse`,
                              });
                            }}
                            disabled={isTesting}
                          >
                            <MapPin className="w-4 h-4 mr-1" />
                            Alle Meridianpunkte ({getTotalPointCount()})
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={async () => {
                              try {
                                const response = await fetch('/databases/clarkeMateriaMedica.json');
                                const data = await response.json();
                                
                                // Build symptom map: Remedy -> Symptoms[]
                                const symptomMap = new Map<string, string[]>();
                                const remediesSet = new Set<string>();
                                
                                data.clinicalSymptoms.forEach((item: ClarkeSymptomEntry) => {
                                  item.remedies.forEach(remedy => {
                                    remediesSet.add(remedy);
                                    const existing = symptomMap.get(remedy) || [];
                                    if (!existing.includes(item.symptom)) {
                                      existing.push(item.symptom);
                                    }
                                    symptomMap.set(remedy, existing);
                                  });
                                });
                                
                                // Alle einzigartigen Symptome sammeln für Autocomplete
                                const uniqueSymptoms = Array.from(new Set(
                                  data.clinicalSymptoms.map((item: ClarkeSymptomEntry) => item.symptom)
                                )).sort() as string[];
                                setAllClarkeSymptoms(uniqueSymptoms);
                                
                                setClarkeSymptomMap(symptomMap);
                                setIsClarkeLoaded(true);
                                
                                const remedies = Array.from(remediesSet).sort();
                                setWordInput(remedies.join('\n'));
                                toast({
                                  title: "Clarke Materia Medica geladen",
                                  description: `${remedies.length} Mittel, ${uniqueSymptoms.length} Symptome bereit`,
                                });
                              } catch (error) {
                                console.error('Error loading Clarke data:', error);
                                toast({
                                  title: "Fehler beim Laden",
                                  description: "Clarke Materia Medica konnte nicht geladen werden",
                                  variant: "destructive"
                                });
                              }
                            }}
                            disabled={isTesting}
                            className={isClarkeLoaded ? "border-green-500/50 bg-green-500/10" : ""}
                          >
                            <Database className="w-4 h-4 mr-1" />
                            Clarke Materia Medica {isClarkeLoaded && "✓"}
                          </Button>
                        </div>
                      </div>

                      {/* Anatomische Datenbanken - Kompaktansicht */}
                      <div className="space-y-2">
                        <div className="flex items-center justify-between">
                          <Label className="text-xs text-muted-foreground">Anatomische Datenbanken (Terminologia Anatomica)</Label>
                          <Button
                            variant="link"
                            size="sm"
                            className="h-auto p-0 text-xs"
                            onClick={() => setActiveTab('anatomie')}
                          >
                            Gesamtübersicht →
                          </Button>
                        </div>
                        <div className="flex flex-wrap gap-2">
                          {Object.entries(ANATOMY_DATABASES).slice(0, 4).map(([key, db]) => (
                            <Button
                              key={key}
                              variant="outline"
                              size="sm"
                              onClick={() => {
                                const entries = getEntriesForDatabase(key);
                                setWordInput(entries.join('\n'));
                                toast({
                                  title: `${db.name} geladen`,
                                  description: `${entries.length} anatomische Strukturen bereit zur Analyse`,
                                });
                              }}
                              disabled={isTesting}
                              className="border-primary/30 hover:border-primary"
                            >
                              {key === 'zns' && <Brain className="w-4 h-4 mr-1" />}
                              {key === 'herzKreislauf' && <Heart className="w-4 h-4 mr-1" />}
                              {key === 'verdauung' && <Utensils className="w-4 h-4 mr-1" />}
                              {key === 'bewegungsapparat' && <Bone className="w-4 h-4 mr-1" />}
                              {db.name} ({db.totalEntries})
                            </Button>
                          ))}
                          <Button
                            variant="secondary"
                            size="sm"
                            onClick={() => setActiveTab('anatomie')}
                          >
                            +{Object.keys(ANATOMY_DATABASES).length - 4} weitere...
                          </Button>
                        </div>
                      </div>

                      {/* Gespeicherte Listen */}
                      {savedWordLists.length > 0 && (
                        <div className="space-y-2">
                          <Label className="text-xs text-muted-foreground">Gespeicherte Listen</Label>
                          <div className="flex flex-wrap gap-2">
                            {savedWordLists.map(list => (
                              <div key={list.id} className="flex items-center gap-1">
                                <Button
                                  variant="secondary"
                                  size="sm"
                                  onClick={() => loadWordList(list)}
                                  disabled={isTesting}
                                >
                                  <FolderOpen className="w-3 h-3 mr-1" />
                                  {list.name} ({list.entries.length})
                                </Button>
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  className="h-8 w-8 p-0 text-destructive hover:text-destructive"
                                  onClick={() => deleteWordList(list.id, list.name)}
                                >
                                  <Trash2 className="w-3 h-3" />
                                </Button>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {isLoadingLists && (
                        <div className="flex items-center gap-2 text-sm text-muted-foreground">
                          <Loader2 className="w-4 h-4 animate-spin" />
                          Lade Listen...
                        </div>
                      )}
                    </CardContent>
                  </CollapsibleContent>
                </Card>
              </Collapsible>

              {/* Input Area */}
              <div className="space-y-2">
                <Label htmlFor="wordList" className="flex items-center gap-2">
                  <ListChecks className="w-4 h-4" />
                  Wortenergien (eine pro Zeile)
                </Label>
                <Textarea
                  id="wordList"
                  placeholder={"Arnica\nBelladonna\nCalcarea carbonica\nLycopodium\n..."}
                  value={wordInput}
                  onChange={(e) => setWordInput(e.target.value)}
                  rows={8}
                  className="font-mono text-sm"
                  disabled={isTesting}
                />
                <p className="text-xs text-muted-foreground">
                  Erkannte Wortenergien: {parseWords(wordInput).length}
                </p>
              </div>

              {/* Progress */}
              {isTesting && testMode === 'sequentiell' && (
                <Card className="bg-primary/5 border-primary/20">
                  <CardContent className="pt-4">
                    <div className="flex items-center gap-3 mb-2">
                      <Loader2 className="w-5 h-5 animate-spin text-primary" />
                      <span className="text-sm font-medium">
                        Teste: {currentWordIndex} / {totalWords}
                      </span>
                    </div>
                    <Progress value={(currentWordIndex / totalWords) * 100} className="h-2" />
                  </CardContent>
                </Card>
              )}

              {isTesting && testMode === 'parallel' && (
                <Card className="bg-primary/5 border-primary/20">
                  <CardContent className="pt-4">
                    <div className="flex items-center gap-3">
                      <Loader2 className="w-5 h-5 animate-spin text-primary" />
                      <span className="text-sm font-medium">
                        Parallele Berechnung von {totalWords} Wortenergien...
                      </span>
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Start Button */}
              <Button
                onClick={handleStartTest}
                disabled={isTesting || parseWords(wordInput).length === 0}
                className="w-full"
                size="lg"
              >
                {isTesting ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    {testMode === 'parallel' ? 'Berechne parallel...' : 'Teste sequentiell...'}
                  </>
                ) : (
                  <>
                    <Zap className="w-4 h-4 mr-2" />
                    {testMode === 'parallel' ? 'Parallel testen ⚡' : 'Sequentiell testen'}
                  </>
                )}
              </Button>

              {/* Results */}
              {results.length > 0 && (
                <div className="space-y-4 pt-4 border-t">
                  <div className="flex items-center justify-between flex-wrap gap-2">
                    <h4 className="font-semibold flex items-center gap-2">
                      <Layers className="w-5 h-5 text-primary" />
                      Testergebnisse ({filteredAndSortedResults.length}
                      {filteredAndSortedResults.length !== results.length && ` von ${results.length}`})
                    </h4>
                    <div className="flex items-center gap-2">
                      {patientId && (
                        <Button 
                          variant="default" 
                          size="sm" 
                          onClick={handleSaveToArchive}
                          disabled={isSaving}
                        >
                          {isSaving ? (
                            <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                          ) : (
                            <Save className="w-4 h-4 mr-2" />
                          )}
                          Archivieren
                        </Button>
                      )}
                      <Button 
                        variant={showFilters ? "secondary" : "outline"} 
                        size="sm" 
                        onClick={() => setShowFilters(!showFilters)}
                      >
                        <Filter className="w-4 h-4 mr-2" />
                        Filter
                        {hasActiveFilters && (
                          <Badge variant="destructive" className="ml-2 h-5 w-5 p-0 justify-center text-[10px]">
                            !
                          </Badge>
                        )}
                      </Button>
                      <Button variant="outline" size="sm" onClick={exportToCSV}>
                        <Download className="w-4 h-4 mr-2" />
                        CSV
                      </Button>
                    </div>
                  </div>

                  {/* Filter & Sort Controls */}
                  {showFilters && (
                    <Card className="bg-muted/30 border-primary/10">
                      <CardContent className="pt-4 space-y-4">
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                          <div className="space-y-1">
                            <Label className="text-xs">Sortieren nach</Label>
                            <Select value={sortField} onValueChange={(v) => setSortField(v as SortField)}>
                              <SelectTrigger className="h-9">
                                <SelectValue />
                              </SelectTrigger>
                              <SelectContent>
                                <SelectItem value="resonanz">Resonanz</SelectItem>
                                <SelectItem value="intensität">Intensität</SelectItem>
                                <SelectItem value="polaritätWert">Polarität</SelectItem>
                                <SelectItem value="dominanteEbene">Ebene</SelectItem>
                                <SelectItem value="copenRate">Copen-Rate</SelectItem>
                                <SelectItem value="word">Wort (A-Z)</SelectItem>
                                {isClarkeLoaded && <SelectItem value="symptomCount">Symptom-Anzahl</SelectItem>}
                              </SelectContent>
                            </Select>
                          </div>

                          <div className="space-y-1">
                            <Label className="text-xs">Richtung</Label>
                            <Button 
                              variant="outline" 
                              className="w-full h-9 justify-start"
                              onClick={() => setSortDirection(d => d === 'asc' ? 'desc' : 'asc')}
                            >
                              {sortDirection === 'desc' ? (
                                <><ArrowDown className="w-4 h-4 mr-2" />Absteigend</>
                              ) : (
                                <><ArrowUp className="w-4 h-4 mr-2" />Aufsteigend</>
                              )}
                            </Button>
                          </div>

                          <div className="space-y-1">
                            <Label className="text-xs">Polarität</Label>
                            <Select value={polaritätFilter} onValueChange={(v) => setPolaritätFilter(v as PolaritätFilter)}>
                              <SelectTrigger className="h-9">
                                <SelectValue />
                              </SelectTrigger>
                              <SelectContent>
                                <SelectItem value="alle">Alle</SelectItem>
                                <SelectItem value="positiv">+ Positiv</SelectItem>
                                <SelectItem value="neutral">○ Neutral</SelectItem>
                                <SelectItem value="negativ">− Negativ</SelectItem>
                              </SelectContent>
                            </Select>
                          </div>

                          <div className="space-y-1">
                            <Label className="text-xs">Min. Resonanz %</Label>
                            <Input 
                              type="number" 
                              min={0} 
                              max={100} 
                              value={minResonanz}
                              onChange={(e) => setMinResonanz(Math.max(0, Math.min(100, parseInt(e.target.value) || 0)))}
                              className="h-9"
                            />
                          </div>
                        </div>

                        <div className="space-y-1">
                          <Label className="text-xs">Dominante Ebene filtern</Label>
                          <div className="flex flex-wrap gap-1">
                            <Button
                              variant={ebeneFilter === null ? "default" : "outline"}
                              size="sm"
                              className="h-7 text-xs"
                              onClick={() => setEbeneFilter(null)}
                            >
                              Alle
                            </Button>
                            {LEVELS_DISPLAY.map(level => (
                              <Button
                                key={level.id}
                                variant={ebeneFilter === level.id ? "default" : "outline"}
                                size="sm"
                                className="h-7 text-xs px-2"
                                onClick={() => setEbeneFilter(level.id)}
                              >
                                {level.id}
                              </Button>
                            ))}
                          </div>
                        </div>

                        {/* Clarke Symptom-Suche */}
                        {isClarkeLoaded && (
                          <div className="space-y-2">
                            <Label className="text-xs flex items-center gap-1">
                              <Search className="w-3 h-3" />
                              Clarke Symptom-Suche
                            </Label>
                            <div className="relative">
                              <Input
                                placeholder="z.B. Kopfschmerz, Herz, Angst... (Komma-getrennt)"
                                value={clarkeSymptomSearch}
                                onChange={(e) => setClarkeSymptomSearch(e.target.value)}
                                className="h-9 pr-8"
                              />
                              {clarkeSymptomSearch && (
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  className="absolute right-0 top-0 h-9 w-8 p-0"
                                  onClick={() => setClarkeSymptomSearch('')}
                                >
                                  <X className="w-4 h-4 text-muted-foreground" />
                                </Button>
                              )}
                            </div>
                            <p className="text-[10px] text-muted-foreground">
                              {allClarkeSymptoms.length} verfügbare Symptome • Mehrere Suchbegriffe mit Komma trennen
                            </p>
                            {clarkeSymptomSearch && (
                              <div className="flex flex-wrap gap-1 max-h-20 overflow-y-auto">
                                {allClarkeSymptoms
                                  .filter(s => s.toLowerCase().includes(clarkeSymptomSearch.split(',')[clarkeSymptomSearch.split(',').length - 1]?.trim().toLowerCase() || ''))
                                  .slice(0, 10)
                                  .map((symptom, idx) => (
                                    <Badge 
                                      key={idx} 
                                      variant="secondary" 
                                      className="text-[10px] cursor-pointer hover:bg-primary/20"
                                      onClick={() => {
                                        const parts = clarkeSymptomSearch.split(',').map(s => s.trim()).filter(s => s);
                                        if (parts.length > 0) {
                                          parts[parts.length - 1] = symptom;
                                        } else {
                                          parts.push(symptom);
                                        }
                                        setClarkeSymptomSearch(parts.join(', '));
                                      }}
                                    >
                                      {symptom}
                                    </Badge>
                                  ))}
                              </div>
                            )}
                          </div>
                        )}

                        {hasActiveFilters && (
                          <Button variant="ghost" size="sm" onClick={resetFilters} className="text-muted-foreground">
                            <X className="w-4 h-4 mr-1" />
                            Filter zurücksetzen
                          </Button>
                        )}
                      </CardContent>
                    </Card>
                  )}

                  <ScrollArea className="h-[400px] rounded-md border">
                    <div className="p-4 space-y-3">
                      {filteredAndSortedResults.length === 0 ? (
                        <div className="text-center py-8 text-muted-foreground">
                          <Filter className="w-8 h-8 mx-auto mb-2 opacity-50" />
                          <p>Keine Ergebnisse mit aktuellen Filtern</p>
                        </div>
                      ) : (
                        filteredAndSortedResults.map((result, idx) => (
                        <Card key={idx} className="bg-muted/20 hover:bg-muted/30 transition-colors">
                          <CardContent className="pt-4">
                            <div className="flex items-start justify-between mb-3">
                              <div>
                                <h5 className="font-semibold text-base">{result.word}</h5>
                                <p className="text-xs text-muted-foreground">
                                  Copen-Rate: {result.copenRate.toLocaleString()}
                                </p>
                                {result.harmonisierungsRate !== undefined && (
                                  <p className="text-xs text-primary font-medium mt-1">
                                    Harmonisierung: {result.harmonisierungsRate.toLocaleString()}
                                  </p>
                                )}
                              </div>
                              <Badge className={`${getPolaritätColor(result.polarität)} text-white`}>
                                {result.polarität === 'positiv' ? '+' : result.polarität === 'negativ' ? '−' : '○'} {result.polarität}
                              </Badge>
                            </div>

                            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                              <div>
                                <p className="text-xs text-muted-foreground mb-1">
                                  Resonanz {effectiveFokus && <span className="text-primary">(+Fokus)</span>}
                                </p>
                                <div className="flex items-center gap-2">
                                  <Progress value={result.resonanz} className="h-2 flex-1" />
                                  <span className={`font-medium ${getResonanzColor(result.resonanz)}`}>
                                    {result.resonanz}%
                                  </span>
                                </div>
                                {effectiveFokus && result.fokusKorrelation > 0 && (
                                  <div className="mt-1 flex items-center gap-1 text-[10px] text-muted-foreground">
                                    <span>Basis: {result.resonanzBasis}%</span>
                                    <span className={result.interferenzMuster === 'konstruktiv' ? 'text-green-500' : result.interferenzMuster === 'destruktiv' ? 'text-red-400' : ''}>
                                      • {result.interferenzMuster === 'konstruktiv' ? '↑' : result.interferenzMuster === 'destruktiv' ? '↓' : '○'} 
                                      Fokus: {result.fokusKorrelation}%
                                    </span>
                                  </div>
                                )}
                              </div>

                              <div>
                                <p className="text-xs text-muted-foreground mb-1">Intensität</p>
                                <div className="flex items-center gap-2">
                                  <Progress value={result.intensität} className="h-2 flex-1" />
                                  <span className="font-medium">{result.intensität}%</span>
                                </div>
                              </div>

                              <div>
                                <p className="text-xs text-muted-foreground mb-1">Polarität-Wert</p>
                                <div className="flex items-center gap-1">
                                  <ArrowUpDown className="w-3 h-3" />
                                  <span className="font-medium">
                                    {result.polaritätWert > 0 ? '+' : ''}{result.polaritätWert}
                                  </span>
                                </div>
                              </div>

                              <div>
                                <p className="text-xs text-muted-foreground mb-1">Dom. Ebene</p>
                                <Badge variant="outline" className="text-xs">
                                  {result.dominanteEbene}. {getLevelDisplayName(result.dominanteEbene, 'de').split(' - ')[1] || getLevelDisplayName(result.dominanteEbene, 'de')}
                                </Badge>
                              </div>
                            </div>

                            {/* Clarke Symptome anzeigen */}
                            {result.clarkeSymptoms && result.clarkeSymptoms.length > 0 && (
                              <details className="mt-3 border-t pt-2">
                                <summary className="text-xs text-primary cursor-pointer hover:text-primary/80 flex items-center gap-1">
                                  <Database className="w-3 h-3" />
                                  Clarke-Symptome ({result.clarkeSymptoms.length})
                                </summary>
                                <div className="mt-2 flex flex-wrap gap-1">
                                  {result.clarkeSymptoms.slice(0, 20).map((symptom, sIdx) => (
                                    <Badge key={sIdx} variant="secondary" className="text-[10px] font-normal">
                                      {symptom}
                                    </Badge>
                                  ))}
                                  {result.clarkeSymptoms.length > 20 && (
                                    <Badge variant="outline" className="text-[10px]">
                                      +{result.clarkeSymptoms.length - 20} weitere
                                    </Badge>
                                  )}
                                </div>
                              </details>
                            )}

                            <details className="mt-3">
                              <summary className="text-xs text-muted-foreground cursor-pointer hover:text-foreground">
                                12 Ebenen-Verteilung anzeigen
                              </summary>
                              <div className="mt-2 grid grid-cols-2 md:grid-cols-4 gap-1 text-xs">
                                {LEVELS_DISPLAY.map(level => (
                                  <div key={level.id} className="flex items-center gap-1">
                                    <span className="text-muted-foreground w-4">{level.id}.</span>
                                    <Progress 
                                      value={result.ebenVerteilung[`level_${level.id}`] || 0} 
                                      className="h-1.5 flex-1"
                                    />
                                    <span className="w-8 text-right">
                                      {Math.round(result.ebenVerteilung[`level_${level.id}`] || 0)}%
                                    </span>
                                  </div>
                                ))}
                              </div>
                            </details>
                          </CardContent>
                        </Card>
                      ))
                      )}
                    </div>
                  </ScrollArea>

                  {/* Harmonisierung Section */}
                  {filteredAndSortedResults.length > 0 && (
                    <Card className="mt-4 border-primary/30 bg-gradient-to-r from-primary/5 to-transparent">
                      <CardContent className="pt-4">
                        <div className="flex items-center justify-between mb-3">
                          <div className="flex items-center gap-2">
                            <Activity className="w-5 h-5 text-primary" />
                            <Label className="font-medium">Harmonisierung (optional)</Label>
                          </div>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => setShowHarmonization(!showHarmonization)}
                          >
                            {showHarmonization ? 'Ausblenden' : 'Einblenden'}
                          </Button>
                        </div>

                        {showHarmonization && !harmonization.isActive && (
                          <div className="space-y-4">
                            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                              <div className="space-y-1">
                                <Label className="text-xs">Top Items</Label>
                                <Select 
                                  value={harmonizationItemCount.toString()} 
                                  onValueChange={(v) => setHarmonizationItemCount(parseInt(v) as 21 | 42 | 63)}
                                >
                                  <SelectTrigger className="h-9">
                                    <SelectValue />
                                  </SelectTrigger>
                                  <SelectContent>
                                    <SelectItem value="21">Top 21</SelectItem>
                                    <SelectItem value="42">Top 42</SelectItem>
                                    <SelectItem value="63">Top 63</SelectItem>
                                  </SelectContent>
                                </Select>
                              </div>
                              
                              <div className="space-y-1">
                                <Label className="text-xs">Impuls (Sek.)</Label>
                                <Input
                                  type="number"
                                  min={1}
                                  max={60}
                                  value={harmonization.pulseDuration}
                                  onChange={(e) => setHarmonization(prev => ({
                                    ...prev,
                                    pulseDuration: Math.max(1, Math.min(60, parseInt(e.target.value) || 5))
                                  }))}
                                  className="h-9"
                                />
                              </div>
                              
                              <div className="space-y-1">
                                <Label className="text-xs">Pause (Sek.)</Label>
                                <Input
                                  type="number"
                                  min={1}
                                  max={60}
                                  value={harmonization.pauseDuration}
                                  onChange={(e) => setHarmonization(prev => ({
                                    ...prev,
                                    pauseDuration: Math.max(1, Math.min(60, parseInt(e.target.value) || 3))
                                  }))}
                                  className="h-9"
                                />
                              </div>
                              
                              <div className="space-y-1">
                                <Label className="text-xs">Max. Laufzeit (Min.)</Label>
                                <Input
                                  type="number"
                                  min={1}
                                  max={360}
                                  value={harmonization.maxDuration}
                                  onChange={(e) => setHarmonization(prev => ({
                                    ...prev,
                                    maxDuration: Math.max(1, Math.min(360, parseInt(e.target.value) || 30))
                                  }))}
                                  className="h-9"
                                />
                              </div>
                            </div>
                            
                            <div className="flex items-center justify-between text-xs text-muted-foreground">
                              <span>
                                Verfügbar: {Math.min(harmonizationItemCount, filteredAndSortedResults.length)} von {filteredAndSortedResults.length} Items
                              </span>
                              <span>
                                Impuls/Pause: {harmonization.pulseDuration}s / {harmonization.pauseDuration}s
                              </span>
                            </div>
                            
                            <Button 
                              onClick={startHarmonization} 
                              className="w-full"
                              disabled={filteredAndSortedResults.length === 0}
                            >
                              <Play className="w-4 h-4 mr-2" />
                              Harmonisierung starten
                            </Button>
                          </div>
                        )}

                        {harmonization.isActive && (
                          <div className="space-y-4">
                            <div className="flex items-center justify-between">
                              <div className="flex items-center gap-3">
                                <div className={`w-3 h-3 rounded-full ${harmonization.inPulsePhase ? 'bg-green-500 animate-pulse' : 'bg-yellow-500'}`} />
                                <span className="text-sm font-medium">
                                  {harmonization.inPulsePhase ? 'Impuls' : 'Pause'}
                                </span>
                              </div>
                              <Badge variant="outline" className="font-mono">
                                {formatTime(harmonization.remainingSeconds || 0)} verbleibend
                              </Badge>
                            </div>
                            
                            <div className="flex items-center gap-2 text-xs text-muted-foreground mb-2">
                              <Timer className="w-3 h-3" />
                              <span>
                                Fortschritt: {formatTime(harmonization.elapsedSeconds)} / {formatTime(harmonization.totalDurationSeconds || harmonization.maxDuration * 60)}
                              </span>
                            </div>
                            
                            <Progress 
                              value={harmonization.totalDurationSeconds > 0 
                                ? ((harmonization.totalDurationSeconds - harmonization.remainingSeconds) / harmonization.totalDurationSeconds) * 100 
                                : 0} 
                              className="h-2"
                            />
                            
                            {/* Aktuelle Harmonisierung */}
                            {harmonization.selectedItems[harmonization.currentItemIndex] && (
                              <Card className="bg-primary/10 border-primary/30">
                                <CardContent className="py-3">
                                  <div className="flex items-center justify-between">
                                    <div>
                                      <p className="text-xs text-muted-foreground">Aktuelles Item ({harmonization.currentItemIndex + 1}/{harmonization.selectedItems.length})</p>
                                      <p className="font-semibold text-primary">
                                        {harmonization.selectedItems[harmonization.currentItemIndex].word}
                                      </p>
                                    </div>
                                    <div className="text-right">
                                      <p className="text-xs text-muted-foreground">Harmonisierungs-Rate</p>
                                      <p className="font-mono text-primary font-bold">
                                        {harmonization.selectedItems[harmonization.currentItemIndex].harmonisierungsRate?.toLocaleString() || 
                                         harmonization.selectedItems[harmonization.currentItemIndex].copenRate.toLocaleString()}
                                      </p>
                                    </div>
                                  </div>
                                </CardContent>
                              </Card>
                            )}
                            
                            {/* Vollständige Liste aller zu harmonisierenden Items */}
                            <details className="mt-2">
                              <summary className="text-xs text-muted-foreground cursor-pointer hover:text-foreground flex items-center gap-1">
                                <Layers className="w-3 h-3" />
                                Alle {harmonization.selectedItems.length} Harmonisierungs-Items anzeigen
                              </summary>
                              <ScrollArea className="h-[200px] mt-2 rounded border bg-muted/20">
                                <div className="p-2 space-y-1">
                                  {harmonization.selectedItems.map((item, idx) => (
                                    <div 
                                      key={idx} 
                                      className={`flex items-center justify-between p-2 rounded text-xs ${
                                        idx === harmonization.currentItemIndex 
                                          ? 'bg-primary/20 border border-primary/40' 
                                          : idx < harmonization.currentItemIndex 
                                            ? 'bg-green-500/10 text-muted-foreground' 
                                            : 'bg-muted/30'
                                      }`}
                                    >
                                      <div className="flex items-center gap-2">
                                        <span className="w-5 text-center font-mono text-muted-foreground">
                                          {idx < harmonization.currentItemIndex ? '✓' : idx === harmonization.currentItemIndex ? '▶' : (idx + 1)}
                                        </span>
                                        <span className={idx === harmonization.currentItemIndex ? 'font-medium text-primary' : ''}>
                                          {item.word}
                                        </span>
                                      </div>
                                      <span className="font-mono">
                                        {item.harmonisierungsRate?.toLocaleString() || item.copenRate.toLocaleString()}
                                      </span>
                                    </div>
                                  ))}
                                </div>
                              </ScrollArea>
                            </details>
                            
                            <div className="flex gap-2">
                              <Button 
                                variant={harmonization.isPaused ? "default" : "secondary"}
                                onClick={stopHarmonization}
                                className="flex-1"
                              >
                                {harmonization.isPaused ? (
                                  <><Play className="w-4 h-4 mr-2" />Fortsetzen</>
                                ) : (
                                  <><Square className="w-4 h-4 mr-2" />Stoppen</>
                                )}
                              </Button>
                              <Button 
                                variant="destructive"
                                onClick={cancelHarmonization}
                              >
                                <Trash2 className="w-4 h-4" />
                              </Button>
                            </div>
                          </div>
                        )}
                      </CardContent>
                    </Card>
                  )}
                </div>
              )}
            </TabsContent>

            {/* ANATOMIE TAB */}
            <TabsContent value="anatomie" className="space-y-4">
              <AnatomyDatabaseOverview
                onLoadDatabase={(entries, name, count) => {
                  setWordInput(entries.join('\n'));
                  setActiveTab('test');
                  toast({
                    title: `${name} geladen`,
                    description: `${count.toLocaleString()} anatomische Strukturen bereit zur Analyse`,
                  });
                }}
                disabled={isTesting}
              />
            </TabsContent>

            {/* HARMONISIERUNG TAB - Neue saubere Engine */}
            <TabsContent value="harmonisierung" className="space-y-4">
              {patientId ? (
                <HarmonizationManager
                  patientId={patientId}
                  clientName={clientName}
                  clientRate={clientResult?.klientenWellenfunktion?.toString()}
                  analysisResults={filteredAndSortedResults.map(r => ({
                    word: r.harmonisierungsWort,
                    rate: r.harmonisierungsRate,
                    potency: 'D0'
                  }))}
                  sourceModule={sourceModule}
                />
              ) : (
                <div className="text-center py-8 text-muted-foreground bg-muted/30 rounded-lg">
                  <Activity className="w-8 h-8 mx-auto mb-2 opacity-50" />
                  <p>Bitte einen Klienten verknüpfen für Harmonisierung</p>
                </div>
              )}
            </TabsContent>

            {/* FREQUENZEN TAB */}
            <TabsContent value="frequenzen" className="space-y-4">
              <FrequencyDatabaseOverview
                onLoadDatabase={(entries, name, count) => {
                  setWordInput(entries.join('\n'));
                  setActiveTab('test');
                  toast({
                    title: `${name} geladen`,
                    description: `${count.toLocaleString()} Frequenz-Einträge bereit zur Analyse`,
                  });
                }}
                disabled={isTesting}
              />
            </TabsContent>

            {/* SYMPTOME TAB - Clarke Symptom Browser */}
            <TabsContent value="symptome" className="space-y-4">
              {!isClarkeLoaded ? (
                <div className="text-center py-8 text-muted-foreground bg-muted/30 rounded-lg">
                  <Database className="w-8 h-8 mx-auto mb-2 opacity-50" />
                  <p className="mb-3">Bitte zuerst die Clarke Materia Medica laden</p>
                  <Button
                    variant="outline"
                    onClick={async () => {
                      try {
                        const response = await fetch('/databases/clarkeMateriaMedica.json');
                        const data = await response.json();
                        
                        const symptomMap = new Map<string, string[]>();
                        const remediesSet = new Set<string>();
                        
                        data.clinicalSymptoms.forEach((item: ClarkeSymptomEntry) => {
                          item.remedies.forEach(remedy => {
                            remediesSet.add(remedy);
                            const existing = symptomMap.get(remedy) || [];
                            if (!existing.includes(item.symptom)) {
                              existing.push(item.symptom);
                            }
                            symptomMap.set(remedy, existing);
                          });
                        });
                        
                        const uniqueSymptoms = Array.from(new Set(
                          data.clinicalSymptoms.map((item: ClarkeSymptomEntry) => item.symptom)
                        )).sort() as string[];
                        setAllClarkeSymptoms(uniqueSymptoms);
                        
                        setClarkeSymptomMap(symptomMap);
                        setIsClarkeLoaded(true);
                        
                        const remedies = Array.from(remediesSet).sort();
                        setWordInput(remedies.join('\n'));
                        toast({
                          title: "Clarke Materia Medica geladen",
                          description: `${remedies.length} Mittel, ${uniqueSymptoms.length} Symptome bereit`,
                        });
                      } catch (error) {
                        console.error('Error loading Clarke data:', error);
                        toast({
                          title: "Fehler beim Laden",
                          description: "Clarke Materia Medica konnte nicht geladen werden",
                          variant: "destructive"
                        });
                      }
                    }}
                  >
                    <Database className="w-4 h-4 mr-2" />
                    Clarke Materia Medica laden
                  </Button>
                </div>
              ) : (
                <SymptomBrowser
                  symptoms={allClarkeSymptoms}
                  symptomMap={clarkeSymptomMap}
                  onSymptomSelect={(symptom) => {
                    setClarkeSymptomSearch(symptom);
                    setActiveTab('test');
                    toast({
                      title: "Symptom-Filter gesetzt",
                      description: `Ergebnisse werden nach "${symptom}" gefiltert`,
                    });
                  }}
                  onRemediesSelect={(remedies) => {
                    setWordInput(remedies.join('\n'));
                    setActiveTab('test');
                    toast({
                      title: "Mittel geladen",
                      description: `${remedies.length} Mittel für das Symptom bereit zur Analyse`,
                    });
                  }}
                />
              )}
            </TabsContent>

            {/* ARCHIV TAB */}
            <TabsContent value="archiv" className="space-y-4">
              {!patientId ? (
                <div className="text-center py-8 text-muted-foreground bg-muted/30 rounded-lg">
                  <Archive className="w-8 h-8 mx-auto mb-2 opacity-50" />
                  <p>Bitte einen Klienten verknüpfen um das Archiv zu nutzen</p>
                </div>
              ) : isLoadingArchive ? (
                <div className="flex items-center justify-center py-8">
                  <Loader2 className="w-6 h-6 animate-spin text-primary" />
                </div>
              ) : archivedTests.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground bg-muted/30 rounded-lg">
                  <History className="w-8 h-8 mx-auto mb-2 opacity-50" />
                  <p>Noch keine archivierten Tests für diesen Klienten</p>
                </div>
              ) : (
                <ScrollArea className="h-[400px]">
                  <div className="space-y-3 pr-4">
                    {archivedTests.map(archive => (
                      <Card 
                        key={archive.id} 
                        className="cursor-pointer hover:bg-muted/30 transition-colors"
                        onClick={() => loadArchivedResult(archive)}
                      >
                        <CardContent className="pt-4">
                          <div className="flex items-center justify-between mb-2">
                            <div className="flex items-center gap-2">
                              <Clock className="w-4 h-4 text-muted-foreground" />
                              <span className="text-sm font-medium">
                                {new Date(archive.created_at).toLocaleDateString('de-DE', { 
                                  day: '2-digit', 
                                  month: '2-digit', 
                                  year: 'numeric',
                                  hour: '2-digit',
                                  minute: '2-digit'
                                })}
                              </span>
                            </div>
                            <Badge variant="secondary">{archive.total_words} Wörter</Badge>
                          </div>
                          <div className="flex items-center gap-4 text-sm text-muted-foreground">
                            <span>Ø Resonanz: <strong className="text-foreground">{archive.average_resonance.toFixed(1)}%</strong></span>
                          </div>
                          {archive.top_items.length > 0 && (
                            <div className="mt-2 flex flex-wrap gap-1">
                              {archive.top_items.slice(0, 10).map((item, idx) => (
                                <Badge key={idx} variant="outline" className="text-xs">
                                  {item.word}: {item.resonanz}%
                                </Badge>
                              ))}
                            </div>
                          )}
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                </ScrollArea>
              )}
            </TabsContent>

            {/* TRENDS TAB */}
            <TabsContent value="trends" className="space-y-4">
              {!patientId ? (
                <div className="text-center py-8 text-muted-foreground bg-muted/30 rounded-lg">
                  <TrendingUp className="w-8 h-8 mx-auto mb-2 opacity-50" />
                  <p>Bitte einen Klienten verknüpfen für Trendanalyse</p>
                </div>
              ) : categoryTrends.resonanz.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground bg-muted/30 rounded-lg">
                  <TrendingUp className="w-8 h-8 mx-auto mb-2 opacity-50" />
                  <p>Mindestens 2 archivierte Tests mit gemeinsamen Wörtern erforderlich</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {/* Header mit Reset-Button */}
                  <div className="flex items-center justify-between">
                    <h4 className="text-sm font-medium text-muted-foreground">
                      Longitudinale Trends für {clientName} (max. 25 Items)
                    </h4>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={async () => {
                        if (!patientId) return;
                        try {
                          const { data: { user } } = await supabase.auth.getUser();
                          if (!user) return;
                          
                          const { error } = await supabase
                            .from('word_energy_archives')
                            .delete()
                            .eq('patient_id', patientId)
                            .eq('user_id', user.id);
                          
                          if (error) throw error;
                          
                          setArchivedTests([]);
                          setCategoryTrends({ resonanz: [], intensität: [], polarität: [], ebenen: [] });
                          setTrendItems([]);
                          
                          toast({
                            title: "Trends zurückgesetzt",
                            description: `Alle archivierten Tests für ${clientName} wurden gelöscht`,
                          });
                        } catch (error) {
                          console.error('Error resetting trends:', error);
                          toast({
                            title: "Fehler",
                            description: "Trends konnten nicht zurückgesetzt werden",
                            variant: "destructive"
                          });
                        }
                      }}
                      className="text-destructive hover:text-destructive"
                    >
                      <Trash2 className="w-4 h-4 mr-1" />
                      Trends zurücksetzen
                    </Button>
                  </div>

                  {/* Kategorie-Tabs */}
                  <div className="flex flex-wrap gap-2">
                    <Button
                      variant={activeTrendCategory === 'resonanz' ? 'default' : 'outline'}
                      size="sm"
                      onClick={() => setActiveTrendCategory('resonanz')}
                      className="flex items-center gap-1"
                    >
                      <Target className="w-3 h-3" />
                      Resonanz ({categoryTrends.resonanz.length})
                    </Button>
                    <Button
                      variant={activeTrendCategory === 'intensität' ? 'default' : 'outline'}
                      size="sm"
                      onClick={() => setActiveTrendCategory('intensität')}
                      className="flex items-center gap-1"
                    >
                      <Gauge className="w-3 h-3" />
                      Intensität ({categoryTrends.intensität.length})
                    </Button>
                    <Button
                      variant={activeTrendCategory === 'polarität' ? 'default' : 'outline'}
                      size="sm"
                      onClick={() => setActiveTrendCategory('polarität')}
                      className="flex items-center gap-1"
                    >
                      <Heart className="w-3 h-3" />
                      Polarität ({categoryTrends.polarität.length})
                    </Button>
                    <Button
                      variant={activeTrendCategory === 'ebenen' ? 'default' : 'outline'}
                      size="sm"
                      onClick={() => setActiveTrendCategory('ebenen')}
                      className="flex items-center gap-1"
                    >
                      <Layers className="w-3 h-3" />
                      Ebenen ({categoryTrends.ebenen.length})
                    </Button>
                  </div>

                  <ScrollArea className="h-[350px]">
                    <div className="space-y-2 pr-4">
                      {categoryTrends[activeTrendCategory].map((item, idx) => (
                        <Card key={idx} className="bg-muted/20">
                          <CardContent className="py-3">
                            <div className="flex items-center justify-between">
                              <div className="flex items-center gap-3">
                                {getTrendIcon(item.trend)}
                                <div>
                                  <span className="font-medium">{item.word}</span>
                                  <p className="text-xs text-muted-foreground">
                                    {item.occurrences}x getestet
                                    {item.fokusKorrelation && item.fokusKorrelation > 0 && (
                                      <span className="ml-2 text-primary">• Fokus: {item.fokusKorrelation.toFixed(0)}%</span>
                                    )}
                                  </p>
                                </div>
                              </div>
                              <div className="text-right">
                                {activeTrendCategory === 'resonanz' && (
                                  <>
                                    <div className="flex items-center gap-2">
                                      <span className="text-muted-foreground text-sm">{item.previousResonance.toFixed(1)}%</span>
                                      <span className="text-muted-foreground">→</span>
                                      <span className={`font-medium ${getResonanzColor(item.currentResonance)}`}>
                                        {item.currentResonance.toFixed(1)}%
                                      </span>
                                    </div>
                                    <Badge 
                                      variant={item.trend === 'up' ? 'default' : item.trend === 'down' ? 'destructive' : 'secondary'}
                                      className="text-xs mt-1"
                                    >
                                      {item.trendValue > 0 ? '+' : ''}{item.trendValue.toFixed(1)}%
                                    </Badge>
                                  </>
                                )}
                                {activeTrendCategory === 'intensität' && (
                                  <>
                                    <div className="flex items-center gap-2">
                                      <span className="text-muted-foreground text-sm">{(item.previousIntensity || 0).toFixed(1)}%</span>
                                      <span className="text-muted-foreground">→</span>
                                      <span className="font-medium">{(item.currentIntensity || 0).toFixed(1)}%</span>
                                    </div>
                                    <Badge 
                                      variant={((item.currentIntensity || 0) - (item.previousIntensity || 0)) > 0 ? 'default' : 'secondary'}
                                      className="text-xs mt-1"
                                    >
                                      {((item.currentIntensity || 0) - (item.previousIntensity || 0)) > 0 ? '+' : ''}
                                      {((item.currentIntensity || 0) - (item.previousIntensity || 0)).toFixed(1)}%
                                    </Badge>
                                  </>
                                )}
                                {activeTrendCategory === 'polarität' && (
                                  <>
                                    <div className="flex items-center gap-2">
                                      <span className="text-muted-foreground text-sm">{(item.previousPolarity || 0).toFixed(2)}</span>
                                      <span className="text-muted-foreground">→</span>
                                      <span className={`font-medium ${(item.currentPolarity || 0) > 0 ? 'text-green-500' : (item.currentPolarity || 0) < 0 ? 'text-red-500' : ''}`}>
                                        {(item.currentPolarity || 0).toFixed(2)}
                                      </span>
                                    </div>
                                    <Badge 
                                      variant={((item.currentPolarity || 0) - (item.previousPolarity || 0)) > 0 ? 'default' : 'destructive'}
                                      className="text-xs mt-1"
                                    >
                                      {((item.currentPolarity || 0) - (item.previousPolarity || 0)) > 0 ? '+' : ''}
                                      {((item.currentPolarity || 0) - (item.previousPolarity || 0)).toFixed(2)}
                                    </Badge>
                                  </>
                                )}
                                {activeTrendCategory === 'ebenen' && (
                                  <>
                                    <div className="flex items-center gap-2">
                                      <Badge variant="outline" className="text-xs">{item.previousLevel}. Ebene</Badge>
                                      <span className="text-muted-foreground">→</span>
                                      <Badge variant="default" className="text-xs">{item.currentLevel}. Ebene</Badge>
                                    </div>
                                    <p className="text-xs text-muted-foreground mt-1">
                                      Shift: {((item.currentLevel || 0) - (item.previousLevel || 0)) > 0 ? '↑' : '↓'} 
                                      {Math.abs((item.currentLevel || 0) - (item.previousLevel || 0))} Ebenen
                                    </p>
                                  </>
                                )}
                              </div>
                            </div>
                          </CardContent>
                        </Card>
                      ))}
                    </div>
                  </ScrollArea>
                </div>
              )}
            </TabsContent>
          </Tabs>
        )}
      </CardContent>
    </Card>
  );
};

export default WordEnergyTester;
