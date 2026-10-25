/**
 * Akupunkturpunkt-Suchkomponente
 * Suche nach Name, Indikation oder Frequenz aus der WHO-409-Datenbank
 */
import { useState, useMemo, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Search, 
  MapPin, 
  Zap, 
  Info,
  ChevronDown,
  ChevronUp,
  X,
  Filter
} from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from '@/components/ui/collapsible';
import { cn } from '@/lib/utils';
import { 
  COMPLETE_ACUPUNCTURE_DATABASE,
  searchPointsByName,
  getPointsByIndication,
  getCompletePointsByMeridian,
  getCompletePointsByElement,
  COMPLETE_DATABASE_STATS
} from '@/utils/meridianPoints';

interface AcupuncturePoint {
  id: string;
  nameChinese: string;
  nameEnglish: string;
  nameGerman: string;
  meridian: string;
  element: string;
  location: string;
  frequency: number;
  harmonicFrequencies?: number[];
  pointTypes?: string[];
  functions: string[];
  indications: string[];
}

interface AcupuncturePointSearchProps {
  onSelectPoint: (frequency: number, pointInfo: { id: string; name: string; element: string }) => void;
  compact?: boolean;
}

const MERIDIAN_NAMES: Record<string, string> = {
  LU: 'Lunge',
  LI: 'Dickdarm',
  ST: 'Magen',
  SP: 'Milz',
  HT: 'Herz',
  SI: 'Dünndarm',
  BL: 'Blase',
  KI: 'Niere',
  PC: 'Perikard',
  TE: 'Dreifacher Erwärmer',
  GB: 'Gallenblase',
  LR: 'Leber',
  DU: 'Du Mai',
  REN: 'Ren Mai',
  EX: 'Extra-Punkte',
};

const ELEMENT_COLORS: Record<string, string> = {
  wood: 'bg-green-500/20 text-green-400 border-green-500/30',
  fire: 'bg-red-500/20 text-red-400 border-red-500/30',
  earth: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
  metal: 'bg-slate-400/20 text-slate-300 border-slate-400/30',
  water: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
};

const POINT_TYPE_LABELS: Record<string, string> = {
  jing_well: 'Jing-Brunnen',
  ying_spring: 'Ying-Quelle',
  shu_stream: 'Shu-Bach',
  jing_river: 'Jing-Fluss',
  he_sea: 'He-Meer',
  yuan_source: 'Yuan-Quell',
  luo_connecting: 'Luo-Verbindung',
  xi_cleft: 'Xi-Spalt',
  back_shu: 'Rücken-Shu',
  front_mu: 'Front-Mu',
  hui_meeting: 'Hui-Versammlung',
  command_point: 'Meisterpunkt',
};

export function AcupuncturePointSearch({ onSelectPoint, compact = false }: AcupuncturePointSearchProps) {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterMeridian, setFilterMeridian] = useState<string>('all');
  const [filterElement, setFilterElement] = useState<string>('all');
  const [expandedPoint, setExpandedPoint] = useState<string | null>(null);
  const [showFilters, setShowFilters] = useState(false);

  // Suchlogik
  const searchResults = useMemo(() => {
    let results: AcupuncturePoint[] = [];

    // Basis-Filter
    if (filterMeridian !== 'all') {
      results = getCompletePointsByMeridian(filterMeridian);
    } else if (filterElement !== 'all') {
      results = getCompletePointsByElement(filterElement);
    } else {
      results = [...COMPLETE_ACUPUNCTURE_DATABASE];
    }

    // Textsuche
    if (searchTerm.trim()) {
      const term = searchTerm.toLowerCase();
      
      // Prüfe ob Frequenzsuche
      const freqMatch = term.match(/^(\d+(?:\.\d+)?)\s*(?:hz)?$/i);
      if (freqMatch) {
        const targetFreq = parseFloat(freqMatch[1]);
        results = results.filter(p => 
          Math.abs(p.frequency - targetFreq) < 5 ||
          p.harmonicFrequencies?.some(h => Math.abs(h - targetFreq) < 5)
        );
      } else {
        // Text-Suche
        results = results.filter(p =>
          p.nameChinese.toLowerCase().includes(term) ||
          p.nameEnglish.toLowerCase().includes(term) ||
          p.nameGerman.toLowerCase().includes(term) ||
          p.id.toLowerCase().includes(term) ||
          p.indications.some(i => i.toLowerCase().includes(term)) ||
          p.functions.some(f => f.toLowerCase().includes(term))
        );
      }
    }

    // Limit results
    return results.slice(0, 50);
  }, [searchTerm, filterMeridian, filterElement]);

  const handleSelectPoint = useCallback((point: AcupuncturePoint) => {
    onSelectPoint(point.frequency, {
      id: point.id,
      name: point.nameGerman,
      element: point.element,
    });
  }, [onSelectPoint]);

  const clearFilters = useCallback(() => {
    setSearchTerm('');
    setFilterMeridian('all');
    setFilterElement('all');
  }, []);

  return (
    <div className={cn("space-y-4", compact && "space-y-2")}>
      {/* Suchfeld */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
        <Input
          type="text"
          placeholder="Suche: Name, Indikation oder Frequenz (z.B. '136 Hz')"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="pl-10 pr-10"
        />
        {searchTerm && (
          <Button
            variant="ghost"
            size="icon"
            className="absolute right-1 top-1/2 -translate-y-1/2 h-7 w-7"
            onClick={() => setSearchTerm('')}
          >
            <X className="w-3 h-3" />
          </Button>
        )}
      </div>

      {/* Filter Toggle */}
      <div className="flex items-center justify-between">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setShowFilters(!showFilters)}
          className="text-muted-foreground"
        >
          <Filter className="w-4 h-4 mr-2" />
          Filter
          {showFilters ? <ChevronUp className="w-4 h-4 ml-1" /> : <ChevronDown className="w-4 h-4 ml-1" />}
        </Button>
        
        <span className="text-xs text-muted-foreground">
          {searchResults.length} von {COMPLETE_DATABASE_STATS.totalPoints} Punkten
        </span>
      </div>

      {/* Filter */}
      <AnimatePresence>
        {showFilters && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="overflow-hidden"
          >
            <div className="grid grid-cols-2 gap-3 p-3 bg-muted/30 rounded-lg">
              <div className="space-y-1">
                <label className="text-xs text-muted-foreground">Meridian</label>
                <Select value={filterMeridian} onValueChange={setFilterMeridian}>
                  <SelectTrigger className="h-8">
                    <SelectValue placeholder="Alle" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">Alle Meridiane</SelectItem>
                    {Object.entries(MERIDIAN_NAMES).map(([code, name]) => (
                      <SelectItem key={code} value={code}>
                        {code} - {name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-1">
                <label className="text-xs text-muted-foreground">Element</label>
                <Select value={filterElement} onValueChange={setFilterElement}>
                  <SelectTrigger className="h-8">
                    <SelectValue placeholder="Alle" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">Alle Elemente</SelectItem>
                    <SelectItem value="wood">Holz</SelectItem>
                    <SelectItem value="fire">Feuer</SelectItem>
                    <SelectItem value="earth">Erde</SelectItem>
                    <SelectItem value="metal">Metall</SelectItem>
                    <SelectItem value="water">Wasser</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {(filterMeridian !== 'all' || filterElement !== 'all' || searchTerm) && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={clearFilters}
                  className="col-span-2 text-xs"
                >
                  Filter zurücksetzen
                </Button>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Ergebnisse */}
      <ScrollArea className={cn("border rounded-lg", compact ? "h-[200px]" : "h-[300px]")}>
        <div className="p-2 space-y-1">
          {searchResults.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              <MapPin className="w-8 h-8 mx-auto mb-2 opacity-50" />
              <p className="text-sm">Keine Punkte gefunden</p>
            </div>
          ) : (
            searchResults.map((point) => (
              <Collapsible
                key={point.id}
                open={expandedPoint === point.id}
                onOpenChange={(open) => setExpandedPoint(open ? point.id : null)}
              >
                <div className="border border-border rounded-md overflow-hidden hover:border-primary/50 transition-colors">
                  <div className="flex items-center justify-between p-2 bg-muted/30">
                    <div className="flex items-center gap-2 flex-1 min-w-0">
                      <Badge variant="outline" className="shrink-0 font-mono text-xs">
                        {point.id}
                      </Badge>
                      <span className="text-sm font-medium truncate">
                        {point.nameGerman}
                      </span>
                      <Badge 
                        variant="outline" 
                        className={cn("shrink-0 text-xs", ELEMENT_COLORS[point.element])}
                      >
                        {point.element}
                      </Badge>
                    </div>
                    
                    <div className="flex items-center gap-1 shrink-0 ml-2">
                      <Button
                        size="sm"
                        variant="default"
                        className="h-7 px-2 text-xs"
                        onClick={() => handleSelectPoint(point)}
                      >
                        <Zap className="w-3 h-3 mr-1" />
                        {point.frequency.toFixed(1)} Hz
                      </Button>
                      
                      <CollapsibleTrigger asChild>
                        <Button variant="ghost" size="icon" className="h-7 w-7">
                          {expandedPoint === point.id ? (
                            <ChevronUp className="w-4 h-4" />
                          ) : (
                            <Info className="w-4 h-4" />
                          )}
                        </Button>
                      </CollapsibleTrigger>
                    </div>
                  </div>

                  <CollapsibleContent>
                    <motion.div
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      className="p-3 bg-background/50 border-t border-border space-y-3"
                    >
                      {/* Namen */}
                      <div className="text-xs">
                        <span className="text-muted-foreground">Namen: </span>
                        <span>{point.nameChinese} • {point.nameEnglish}</span>
                      </div>

                      {/* Lokalisation */}
                      <div className="text-xs">
                        <span className="text-muted-foreground">Lokalisation: </span>
                        <span>{point.location}</span>
                      </div>

                      {/* Punkttypen */}
                      {point.pointTypes && point.pointTypes.length > 0 && (
                        <div className="flex flex-wrap gap-1">
                          {point.pointTypes.map((type) => (
                            <Badge key={type} variant="secondary" className="text-xs">
                              {POINT_TYPE_LABELS[type] || type}
                            </Badge>
                          ))}
                        </div>
                      )}

                      {/* Funktionen */}
                      <div className="text-xs">
                        <span className="text-muted-foreground block mb-1">Funktionen:</span>
                        <ul className="list-disc list-inside space-y-0.5">
                          {point.functions.slice(0, 3).map((f, i) => (
                            <li key={i}>{f}</li>
                          ))}
                        </ul>
                      </div>

                      {/* Indikationen */}
                      <div className="text-xs">
                        <span className="text-muted-foreground block mb-1">Indikationen:</span>
                        <div className="flex flex-wrap gap-1">
                          {point.indications.slice(0, 5).map((ind, i) => (
                            <Badge key={i} variant="outline" className="text-xs">
                              {ind}
                            </Badge>
                          ))}
                          {point.indications.length > 5 && (
                            <Badge variant="outline" className="text-xs opacity-50">
                              +{point.indications.length - 5}
                            </Badge>
                          )}
                        </div>
                      </div>

                      {/* Harmonische Frequenzen */}
                      {point.harmonicFrequencies && point.harmonicFrequencies.length > 0 && (
                        <div className="text-xs">
                          <span className="text-muted-foreground">Harmonische: </span>
                          <span className="font-mono">
                            {point.harmonicFrequencies.slice(0, 4).map(h => h.toFixed(1)).join(' • ')} Hz
                          </span>
                        </div>
                      )}
                    </motion.div>
                  </CollapsibleContent>
                </div>
              </Collapsible>
            ))
          )}
        </div>
      </ScrollArea>
    </div>
  );
}

export default AcupuncturePointSearch;
