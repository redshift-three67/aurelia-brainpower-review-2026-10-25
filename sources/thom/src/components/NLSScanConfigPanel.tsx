/**
 * NLS Scan Configuration Panel
 * Allows the client to configure scan parameters before starting:
 * - Model selection
 * - Organ/point selection
 * - Optional focus/multi-focus definition
 */
import { useState, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Target,
  Zap,
  Settings2,
  ChevronDown,
  ChevronUp,
  Play,
  X,
  Plus,
  Search,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible';
import { type OrganScanPoint, type OrganGroup, getOrganColor } from '@/hooks/useOrganScanPoints';
import type { AnatomyModel } from '@/hooks/useAnatomyModels';

// Scan focus definition
export interface ScanFocus {
  id: string;
  label: string;
  description: string;
  type: 'symptom' | 'organ' | 'region' | 'custom';
  relatedOrgans?: string[];
  priority: number;
}

// Complete scan configuration
export interface NLSScanConfig {
  selectedModelId: string | null;
  selectedOrgans: string[];
  selectedPointIds: string[];
  scanAllPoints: boolean;
  focusList: ScanFocus[];
  scanSpeed: 'slow' | 'normal' | 'fast';
  includeHarmonics: boolean;
}

// Predefined focus templates
const FOCUS_TEMPLATES: ScanFocus[] = [
  { id: 'digestion', label: 'Verdauung', description: 'Magen, Darm, Leber, Bauchspeicheldrüse', type: 'symptom', relatedOrgans: ['stomach', 'intestine', 'liver', 'pancreas'], priority: 1 },
  { id: 'cardiac', label: 'Herz-Kreislauf', description: 'Herz, Gefäße, Blutdruck', type: 'organ', relatedOrgans: ['heart'], priority: 1 },
  { id: 'nervous', label: 'Nervensystem', description: 'Gehirn, Neurologie, Stress', type: 'organ', relatedOrgans: ['brain', 'sensory'], priority: 1 },
  { id: 'respiratory', label: 'Atemwege', description: 'Lunge, Bronchien, Schilddrüse', type: 'organ', relatedOrgans: ['lung', 'thyroid'], priority: 2 },
  { id: 'urogenital', label: 'Urogenital', description: 'Nieren, Blase, Nebennieren, Becken', type: 'organ', relatedOrgans: ['kidney', 'urogenital', 'adrenal'], priority: 2 },
  { id: 'immune', label: 'Immunsystem', description: 'Milz, Lymphe, Thymus', type: 'organ', relatedOrgans: ['spleen', 'lymph'], priority: 2 },
  { id: 'metabolic', label: 'Stoffwechsel', description: 'Leber, Pankreas, Schilddrüse, Nebennieren', type: 'symptom', relatedOrgans: ['liver', 'pancreas', 'thyroid', 'adrenal'], priority: 3 },
  { id: 'stress', label: 'Stress & Burnout', description: 'Nebennieren, Gehirn, Herz', type: 'symptom', relatedOrgans: ['brain', 'heart', 'adrenal'], priority: 1 },
  { id: 'musculoskeletal', label: 'Bewegungsapparat', description: 'Wirbelsäule (HWS/BWS/LWS)', type: 'organ', relatedOrgans: ['spine'], priority: 2 },
  { id: 'sensory', label: 'Sinnesorgane', description: 'Augen, Ohren, Geruch, Geschmack', type: 'organ', relatedOrgans: ['sensory'], priority: 3 },
];

interface NLSScanConfigPanelProps {
  organGroups: OrganGroup[];
  organSystems: string[];
  allPoints: OrganScanPoint[];
  models: AnatomyModel[];
  selectedModel: AnatomyModel | null;
  onConfigConfirm: (config: NLSScanConfig) => void;
  onCancel: () => void;
  isOpen: boolean;
}

export function NLSScanConfigPanel({
  organGroups,
  organSystems,
  allPoints,
  models,
  selectedModel,
  onConfigConfirm,
  onCancel,
  isOpen,
}: NLSScanConfigPanelProps) {
  const [selectedOrgans, setSelectedOrgans] = useState<Set<string>>(new Set());
  const [scanAllPoints, setScanAllPoints] = useState(true);
  const [selectedPointIds, setSelectedPointIds] = useState<Set<string>>(new Set());
  const [activeFocusList, setActiveFocusList] = useState<ScanFocus[]>([]);
  const [scanSpeed, setScanSpeed] = useState<'slow' | 'normal' | 'fast'>('normal');
  const [includeHarmonics, setIncludeHarmonics] = useState(true);
  const [customFocusInput, setCustomFocusInput] = useState('');
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [focusSearch, setFocusSearch] = useState('');

  // Filter available organ systems based on selected model
  const availableOrgans = useMemo(() => {
    if (selectedModel?.applicableOrganSystems && selectedModel.applicableOrganSystems.length > 0) {
      return organSystems.filter(os => selectedModel.applicableOrganSystems!.includes(os));
    }
    return organSystems;
  }, [selectedModel, organSystems]);

  // Filter points based on selection
  const relevantPoints = useMemo(() => {
    let pts = allPoints;

    // Filter by model's applicable organs
    if (selectedModel?.applicableOrganSystems?.length) {
      pts = pts.filter(p => selectedModel.applicableOrganSystems!.includes(p.organSystem));
    }

    // Filter by selected organs
    if (selectedOrgans.size > 0) {
      pts = pts.filter(p => selectedOrgans.has(p.organSystem));
    }

    // Filter by focus-related organs
    if (activeFocusList.length > 0) {
      const focusOrgans = new Set(activeFocusList.flatMap(f => f.relatedOrgans || []));
      if (focusOrgans.size > 0 && selectedOrgans.size === 0) {
        pts = pts.filter(p => focusOrgans.has(p.organSystem));
      }
    }

    return pts;
  }, [allPoints, selectedModel, selectedOrgans, activeFocusList]);

  const filteredFocusTemplates = useMemo(() => {
    if (!focusSearch) return FOCUS_TEMPLATES;
    const q = focusSearch.toLowerCase();
    return FOCUS_TEMPLATES.filter(f =>
      f.label.toLowerCase().includes(q) || f.description.toLowerCase().includes(q)
    );
  }, [focusSearch]);

  const toggleOrgan = (organ: string) => {
    setSelectedOrgans(prev => {
      const next = new Set(prev);
      if (next.has(organ)) next.delete(organ);
      else next.add(organ);
      return next;
    });
  };

  const toggleFocus = (focus: ScanFocus) => {
    setActiveFocusList(prev => {
      const exists = prev.find(f => f.id === focus.id);
      if (exists) return prev.filter(f => f.id !== focus.id);
      return [...prev, focus];
    });
  };

  const addCustomFocus = () => {
    if (!customFocusInput.trim()) return;
    const custom: ScanFocus = {
      id: `custom-${Date.now()}`,
      label: customFocusInput.trim(),
      description: 'Benutzerdefinierter Fokus',
      type: 'custom',
      priority: 1,
    };
    setActiveFocusList(prev => [...prev, custom]);
    setCustomFocusInput('');
  };

  const togglePointId = (id: string) => {
    setSelectedPointIds(prev => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const handleConfirm = () => {
    onConfigConfirm({
      selectedModelId: selectedModel?.id || null,
      selectedOrgans: Array.from(selectedOrgans),
      selectedPointIds: scanAllPoints ? relevantPoints.map(p => p.id) : Array.from(selectedPointIds),
      scanAllPoints,
      focusList: activeFocusList,
      scanSpeed,
      includeHarmonics,
    });
  };

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: 20 }}
        className="bg-card rounded-lg border border-border p-5 space-y-5"
      >
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Settings2 className="w-5 h-5 text-primary" />
            <h3 className="font-display text-lg text-foreground">NLS-Scan Konfiguration</h3>
          </div>
          <Button variant="ghost" size="icon" onClick={onCancel}>
            <X className="w-4 h-4" />
          </Button>
        </div>

        {/* 1. Focus / Multi-Focus (Optional) */}
        <Card className="border-primary/20">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm flex items-center gap-2">
              <Target className="w-4 h-4 text-primary" />
              Scan-Fokus <span className="text-muted-foreground font-normal">(optional)</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {/* Active focus badges */}
            {activeFocusList.length > 0 && (
              <div className="flex flex-wrap gap-1.5">
                {activeFocusList.map(f => (
                  <Badge
                    key={f.id}
                    variant="default"
                    className="gap-1 cursor-pointer"
                    onClick={() => toggleFocus(f)}
                  >
                    {f.label}
                    <X className="w-3 h-3" />
                  </Badge>
                ))}
              </div>
            )}

            {/* Search + Templates */}
            <Input
              placeholder="Fokus suchen oder eigenen eingeben..."
              value={focusSearch || customFocusInput}
              onChange={e => {
                setFocusSearch(e.target.value);
                setCustomFocusInput(e.target.value);
              }}
              onKeyDown={e => {
                if (e.key === 'Enter') addCustomFocus();
              }}
              className="h-8 text-sm"
            />

            <div className="grid grid-cols-2 gap-1.5">
              {filteredFocusTemplates.map(f => {
                const isActive = activeFocusList.some(af => af.id === f.id);
                return (
                  <button
                    key={f.id}
                    onClick={() => toggleFocus(f)}
                    className={`text-left p-2 rounded-lg border transition-colors ${
                      isActive
                        ? 'bg-primary/15 border-primary/40 text-foreground'
                        : 'bg-muted/30 border-transparent hover:bg-muted/50 text-muted-foreground'
                    }`}
                  >
                    <p className="text-xs font-medium">{f.label}</p>
                    <p className="text-[10px] text-muted-foreground">{f.description}</p>
                  </button>
                );
              })}
            </div>

            {customFocusInput && !FOCUS_TEMPLATES.some(f => f.label.toLowerCase() === customFocusInput.toLowerCase()) && (
              <Button variant="outline" size="sm" onClick={addCustomFocus} className="gap-1">
                <Plus className="w-3 h-3" />
                „{customFocusInput}" als Fokus hinzufügen
              </Button>
            )}
          </CardContent>
        </Card>

        {/* 2. Organ Selection */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm flex items-center gap-2">
              <Zap className="w-4 h-4 text-primary" />
              Organsysteme
              <span className="text-muted-foreground font-normal ml-auto text-xs">
                {selectedOrgans.size === 0 ? 'Alle' : `${selectedOrgans.size} ausgewählt`}
              </span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-1.5">
              {availableOrgans.map(organ => {
                const group = organGroups.find(g => g.organSystem === organ);
                const isSelected = selectedOrgans.has(organ);
                const isFocusRelated = activeFocusList.some(f => f.relatedOrgans?.includes(organ));
                return (
                  <button
                    key={organ}
                    onClick={() => toggleOrgan(organ)}
                    className={`text-xs px-2.5 py-1 rounded-full transition-colors flex items-center gap-1.5 border ${
                      isSelected
                        ? 'bg-primary text-primary-foreground border-primary'
                        : isFocusRelated
                        ? 'bg-primary/10 text-foreground border-primary/30'
                        : 'bg-muted/40 text-muted-foreground border-transparent hover:bg-muted/60'
                    }`}
                  >
                    <div className="w-2 h-2 rounded-full" style={{ backgroundColor: getOrganColor(organ) }} />
                    {group?.organNameDe || organ}
                    {isFocusRelated && !isSelected && (
                      <Target className="w-2.5 h-2.5 text-primary" />
                    )}
                  </button>
                );
              })}
            </div>
          </CardContent>
        </Card>

        {/* 3. Advanced: Point Selection */}
        <Collapsible open={showAdvanced} onOpenChange={setShowAdvanced}>
          <CollapsibleTrigger asChild>
            <Button variant="ghost" size="sm" className="w-full gap-2 text-muted-foreground">
              Erweiterte Punktauswahl
              {showAdvanced ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
            </Button>
          </CollapsibleTrigger>
          <CollapsibleContent className="space-y-3 pt-3">
            <div className="flex items-center gap-3">
              <Switch
                id="scan-all"
                checked={scanAllPoints}
                onCheckedChange={setScanAllPoints}
              />
              <Label htmlFor="scan-all" className="text-sm">
                Alle {relevantPoints.length} relevanten Punkte scannen
              </Label>
            </div>

            {!scanAllPoints && (
              <div className="max-h-[200px] overflow-y-auto space-y-1 border border-border rounded-lg p-2">
                {relevantPoints.map(p => (
                  <label
                    key={p.id}
                    className="flex items-center gap-2 p-1.5 rounded hover:bg-muted/40 cursor-pointer"
                  >
                    <input
                      type="checkbox"
                      checked={selectedPointIds.has(p.id)}
                      onChange={() => togglePointId(p.id)}
                      className="rounded border-border"
                    />
                    <div className="w-2 h-2 rounded-full" style={{ backgroundColor: getOrganColor(p.organSystem) }} />
                    <span className="text-xs text-foreground flex-1">{p.pointName}</span>
                    <span className="text-[10px] font-mono text-muted-foreground">{p.scanFrequency.toFixed(1)} Hz</span>
                  </label>
                ))}
              </div>
            )}

            {/* Scan Speed */}
            <div className="flex items-center gap-3">
              <Label className="text-xs text-muted-foreground w-24">Scan-Tempo</Label>
              <div className="flex gap-1">
                {(['slow', 'normal', 'fast'] as const).map(speed => (
                  <button
                    key={speed}
                    onClick={() => setScanSpeed(speed)}
                    className={`text-xs px-3 py-1 rounded-full transition-colors ${
                      scanSpeed === speed
                        ? 'bg-primary text-primary-foreground'
                        : 'bg-muted/40 text-muted-foreground hover:bg-muted/60'
                    }`}
                  >
                    {speed === 'slow' ? 'Langsam' : speed === 'normal' ? 'Normal' : 'Schnell'}
                  </button>
                ))}
              </div>
            </div>

            {/* Harmonics */}
            <div className="flex items-center gap-3">
              <Switch
                id="harmonics"
                checked={includeHarmonics}
                onCheckedChange={setIncludeHarmonics}
              />
              <Label htmlFor="harmonics" className="text-sm">
                Harmonische Frequenzen einbeziehen
              </Label>
            </div>
          </CollapsibleContent>
        </Collapsible>

        {/* Summary + Start */}
        <div className="bg-muted/30 rounded-lg p-3 space-y-2">
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Scan-Punkte:</span>
            <span className="font-mono text-foreground font-medium">
              {scanAllPoints ? relevantPoints.length : selectedPointIds.size}
            </span>
          </div>
          {activeFocusList.length > 0 && (
            <div className="flex items-center justify-between text-sm">
              <span className="text-muted-foreground">Fokus:</span>
              <span className="text-foreground">{activeFocusList.map(f => f.label).join(', ')}</span>
            </div>
          )}
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Modell:</span>
            <span className="text-foreground">{selectedModel?.name || 'Standard'}</span>
          </div>
        </div>

        <div className="flex gap-2">
          <Button variant="outline" onClick={onCancel} className="flex-1">
            Abbrechen
          </Button>
          <Button
            onClick={handleConfirm}
            className="flex-1 gap-2"
            disabled={!scanAllPoints && selectedPointIds.size === 0}
          >
            <Play className="w-4 h-4" />
            Scan starten ({scanAllPoints ? relevantPoints.length : selectedPointIds.size} Punkte)
          </Button>
        </div>
      </motion.div>
    </AnimatePresence>
  );
}

export default NLSScanConfigPanel;
