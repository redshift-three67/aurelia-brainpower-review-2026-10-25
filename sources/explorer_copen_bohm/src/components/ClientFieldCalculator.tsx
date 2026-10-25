import { useState, useRef, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Loader2, User, Calendar, MapPin, Sparkles, Heart, Leaf, Table, Info, Upload, X, ImageIcon, Save, Users, Link2, Database, Target, ChevronRight } from 'lucide-react';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { supabase } from '@/integrations/supabase/client';
import { useToast } from '@/hooks/use-toast';
import { 
  berechneKlientenFeld, 
  type KlientenDaten, 
  type TCMElement,
  type Planet,
  type FünfElementeProfile,
  type KlientenFeldErgebnis 
} from '@/utils/clientFieldAlgorithms';
import { 
  getTopDatabaseRecommendations, 
  getAvailableFokusCategories,
  type RecommendationResult 
} from '@/utils/databaseRecommendationEngine';
import WordEnergyTester from './WordEnergyTester';

const PLANET_LABELS: Record<Planet, string> = {
  sonne: '☀️ Sonne',
  mond: '🌙 Mond',
  merkur: '☿️ Merkur',
  venus: '♀️ Venus',
  mars: '♂️ Mars',
  jupiter: '♃ Jupiter',
  saturn: '♄ Saturn',
  uranus: '⛢ Uranus',
  neptun: '♆ Neptun',
  pluto: '♇ Pluto'
};

interface PatientV2 {
  id: string;
  first_name: string;
  last_name: string;
  birth_date: string;
  birth_place: string;
  image_signature: string | null;
  image_signature_active: boolean | null;
}

const ELEMENT_COLORS: Record<TCMElement, string> = {
  holz: 'bg-green-500',
  feuer: 'bg-red-500',
  erde: 'bg-yellow-600',
  metall: 'bg-gray-400',
  wasser: 'bg-blue-500'
};

const ELEMENT_LABELS: Record<TCMElement, string> = {
  holz: '🌳 Holz',
  feuer: '🔥 Feuer',
  erde: '🌍 Erde',
  metall: '⚙️ Metall',
  wasser: '💧 Wasser'
};

// Akkuranz/Effektivitäts/Authentizitäts-Matrix
interface ParameterKombination {
  pflichtFelder: string[];
  optionaleFelder: string[];
  akkuranz: number;
  effektivität: number;
  authentizität: number;
  beschreibung: string;
}

const PARAMETER_KOMBINATIONEN: ParameterKombination[] = [
  {
    pflichtFelder: ['Name', 'Vornamen', 'Geburtsdatum', 'Geburtsort'],
    optionaleFelder: [],
    akkuranz: 72,
    effektivität: 68,
    authentizität: 75,
    beschreibung: 'Basis-Konfiguration: Grundlegende Personalisierung'
  },
  {
    pflichtFelder: ['Name', 'Vornamen', 'Geburtsdatum', 'Geburtsort'],
    optionaleFelder: ['TCM-Typ'],
    akkuranz: 81,
    effektivität: 78,
    authentizität: 82,
    beschreibung: 'TCM-Erweiterung: Element-basierte Resonanz'
  },
  {
    pflichtFelder: ['Name', 'Vornamen', 'Geburtsdatum', 'Geburtsort'],
    optionaleFelder: ['Bild-Signatur'],
    akkuranz: 85,
    effektivität: 82,
    authentizität: 88,
    beschreibung: 'Bild-Integration: Morphisches Feld-Anker'
  },
  {
    pflichtFelder: ['Name', 'Vornamen', 'Geburtsdatum', 'Geburtsort'],
    optionaleFelder: ['TCM-Typ', 'Bild-Signatur'],
    akkuranz: 89,
    effektivität: 86,
    authentizität: 91,
    beschreibung: 'Erweitert: TCM + Bild-Signatur Synergie'
  },
  {
    pflichtFelder: ['Name', 'Vornamen', 'Geburtsdatum', 'Geburtsort'],
    optionaleFelder: ['Geburtsplanet'],
    akkuranz: 78,
    effektivität: 74,
    authentizität: 79,
    beschreibung: 'Planetare Ergänzung: Kosmische Einflüsse'
  },
  {
    pflichtFelder: ['Name', 'Vornamen', 'Geburtsdatum', 'Geburtsort'],
    optionaleFelder: ['5-Elemente-Profil'],
    akkuranz: 84,
    effektivität: 81,
    authentizität: 85,
    beschreibung: 'Detailliertes Element-Profil nach Akupunkturlehre'
  },
  {
    pflichtFelder: ['Name', 'Vornamen', 'Geburtsdatum', 'Geburtsort'],
    optionaleFelder: ['TCM-Typ', '5-Elemente-Profil'],
    akkuranz: 88,
    effektivität: 85,
    authentizität: 89,
    beschreibung: 'Volle TCM-Integration: Typ + Element-Profil'
  },
  {
    pflichtFelder: ['Name', 'Vornamen', 'Geburtsdatum', 'Geburtsort'],
    optionaleFelder: ['TCM-Typ', 'Bild-Signatur', 'Geburtsplanet'],
    akkuranz: 93,
    effektivität: 90,
    authentizität: 94,
    beschreibung: 'Premium: TCM + Bild + Planetar'
  },
  {
    pflichtFelder: ['Name', 'Vornamen', 'Geburtsdatum', 'Geburtsort'],
    optionaleFelder: ['TCM-Typ', 'Bild-Signatur', 'Geburtsplanet', '5-Elemente-Profil'],
    akkuranz: 97,
    effektivität: 95,
    authentizität: 98,
    beschreibung: 'Maximum: Alle Parameter - Höchste Präzision (Bohm-Optimal)'
  }
];

interface ClientFieldCalculatorProps {
  onPatientChange?: (patientId: string | null) => void;
}

const ClientFieldCalculator: React.FC<ClientFieldCalculatorProps> = ({ onPatientChange }) => {
  const { toast } = useToast();
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  const [nachname, setNachname] = useState('');
  const [vornamen, setVornamen] = useState('');
  const [geburtsdatum, setGeburtsdatum] = useState('');
  const [geburtsort, setGeburtsort] = useState('');
  const [tcmTyp, setTcmTyp] = useState<TCMElement | ''>('');
  const [geburtsplanet, setGeburtsplanet] = useState<Planet | ''>('');
  const [fünfElemente, setFünfElemente] = useState<FünfElementeProfile>({
    holz: 20, feuer: 20, erde: 20, metall: 20, wasser: 20
  });
  const [showFünfElemente, setShowFünfElemente] = useState(false);
  const [bildSignatur, setBildSignatur] = useState<string>('');
  const [bildPreview, setBildPreview] = useState<string>('');
  const [isUploading, setIsUploading] = useState(false);
  const [showMatrix, setShowMatrix] = useState(false);
  const [isCalculating, setIsCalculating] = useState(false);
  const [result, setResult] = useState<KlientenFeldErgebnis | null>(null);
  
  // Database Recommendation State
  const [showDbRecommendation, setShowDbRecommendation] = useState(false);
  const [dbFokus, setDbFokus] = useState<string>('');
  const [dbCustomFokus, setDbCustomFokus] = useState<string>('');
  const [useCustomFokus, setUseCustomFokus] = useState(false);
  const [dbRecommendation, setDbRecommendation] = useState<RecommendationResult | null>(null);
  
  // Patient linking state
  const [patients, setPatients] = useState<PatientV2[]>([]);
  const [selectedPatientId, setSelectedPatientId] = useState<string>('');
  const [isLoadingPatients, setIsLoadingPatients] = useState(false);
  const [isSavingToPatient, setIsSavingToPatient] = useState(false);

  // Load patients on mount
  useEffect(() => {
    loadPatients();
  }, []);

  const loadPatients = async () => {
    setIsLoadingPatients(true);
    try {
      const { data, error } = await supabase
        .from('patients_v2')
        .select('id, first_name, last_name, birth_date, birth_place, image_signature, image_signature_active')
        .order('last_name', { ascending: true });

      if (error) throw error;
      setPatients(data || []);
    } catch (error) {
      console.error('Error loading patients:', error);
    } finally {
      setIsLoadingPatients(false);
    }
  };

  // Load patient data when selected
  const handlePatientSelect = async (patientId: string) => {
    setSelectedPatientId(patientId);
    
    // Callback für Patientenänderung
    onPatientChange?.(patientId || null);
    
    if (!patientId) {
      // Clear form
      setNachname('');
      setVornamen('');
      setGeburtsdatum('');
      setGeburtsort('');
      setBildSignatur('');
      setBildPreview('');
      return;
    }

    const patient = patients.find(p => p.id === patientId);
    if (!patient) return;

    // Fill form with patient data
    setNachname(patient.last_name);
    setVornamen(patient.first_name);
    setGeburtsdatum(patient.birth_date);
    setGeburtsort(patient.birth_place);

    // Load existing image signature if present
    if (patient.image_signature) {
      setBildSignatur(patient.image_signature);
      
      // Get signed URL for preview
      const { data: urlData } = await supabase.storage
        .from('client-signatures')
        .createSignedUrl(patient.image_signature, 3600);

      if (urlData?.signedUrl) {
        setBildPreview(urlData.signedUrl);
      }
    } else {
      setBildSignatur('');
      setBildPreview('');
    }
  };

  // Save image to patient profile
  const saveImageToPatient = async () => {
    if (!selectedPatientId || !bildSignatur) {
      toast({
        title: "Fehler",
        description: "Bitte wählen Sie einen Patienten und laden Sie ein Bild hoch",
        variant: "destructive"
      });
      return;
    }

    setIsSavingToPatient(true);
    try {
      const { error } = await supabase
        .from('patients_v2')
        .update({ 
          image_signature: bildSignatur,
          image_signature_active: true 
        })
        .eq('id', selectedPatientId);

      if (error) throw error;

      // Update local patient list
      setPatients(prev => prev.map(p => 
        p.id === selectedPatientId 
          ? { ...p, image_signature: bildSignatur, image_signature_active: true }
          : p
      ));

      toast({
        title: "Bild verknüpft",
        description: "Klienten-Signatur wurde dauerhaft mit dem Patienten-Profil verknüpft",
      });
    } catch (error: any) {
      console.error('Error saving image to patient:', error);
      toast({
        title: "Speichern fehlgeschlagen",
        description: error.message || "Bild konnte nicht verknüpft werden",
        variant: "destructive"
      });
    } finally {
      setIsSavingToPatient(false);
    }
  };

  const handleImageUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Validate file type
    if (!file.type.startsWith('image/')) {
      toast({
        title: "Ungültiger Dateityp",
        description: "Bitte wählen Sie eine Bilddatei (JPG, PNG, etc.)",
        variant: "destructive"
      });
      return;
    }

    // Validate file size (max 5MB)
    if (file.size > 5 * 1024 * 1024) {
      toast({
        title: "Datei zu groß",
        description: "Maximale Dateigröße: 5MB",
        variant: "destructive"
      });
      return;
    }

    setIsUploading(true);

    try {
      // Get current user
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) {
        toast({
          title: "Nicht angemeldet",
          description: "Bitte melden Sie sich an, um Bilder hochzuladen",
          variant: "destructive"
        });
        return;
      }

      // Create unique filename
      const fileExt = file.name.split('.').pop();
      const fileName = `${user.id}/${Date.now()}-${Math.random().toString(36).substring(7)}.${fileExt}`;

      // Upload to Supabase Storage
      const { data, error } = await supabase.storage
        .from('client-signatures')
        .upload(fileName, file, {
          cacheControl: '3600',
          upsert: false
        });

      if (error) {
        throw error;
      }

      // Get signed URL for private bucket
      const { data: urlData } = await supabase.storage
        .from('client-signatures')
        .createSignedUrl(data.path, 3600); // 1 hour validity

      if (urlData?.signedUrl) {
        setBildSignatur(data.path);
        setBildPreview(urlData.signedUrl);
        
        toast({
          title: "Bild hochgeladen",
          description: "Klienten-Signatur erfolgreich hinzugefügt",
        });
      }
    } catch (error: any) {
      console.error('Upload error:', error);
      toast({
        title: "Upload fehlgeschlagen",
        description: error.message || "Bild konnte nicht hochgeladen werden",
        variant: "destructive"
      });
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleRemoveImage = async () => {
    if (!bildSignatur) return;

    try {
      const { error } = await supabase.storage
        .from('client-signatures')
        .remove([bildSignatur]);

      if (error) {
        console.error('Delete error:', error);
      }

      setBildSignatur('');
      setBildPreview('');
      
      toast({
        title: "Bild entfernt",
        description: "Klienten-Signatur wurde entfernt",
      });
    } catch (error) {
      console.error('Error removing image:', error);
    }
  };

  // Aktuelle Konfiguration ermitteln
  const getCurrentConfig = (): ParameterKombination => {
    const optionale: string[] = [];
    if (tcmTyp) optionale.push('TCM-Typ');
    if (bildSignatur) optionale.push('Bild-Signatur');
    if (geburtsplanet) optionale.push('Geburtsplanet');
    if (showFünfElemente) optionale.push('5-Elemente-Profil');
    
    // Finde passende Konfiguration oder beste Annäherung
    const match = PARAMETER_KOMBINATIONEN.find(k => 
      k.optionaleFelder.length === optionale.length &&
      k.optionaleFelder.every(f => optionale.includes(f))
    );
    
    // Falls keine exakte Übereinstimmung, berechne dynamisch
    if (!match && optionale.length > 0) {
      const baseAcc = 72;
      const bonus = optionale.length * 6;
      return {
        pflichtFelder: ['Name', 'Vornamen', 'Geburtsdatum', 'Geburtsort'],
        optionaleFelder: optionale,
        akkuranz: Math.min(97, baseAcc + bonus),
        effektivität: Math.min(95, baseAcc - 4 + bonus),
        authentizität: Math.min(98, baseAcc + 3 + bonus),
        beschreibung: `Benutzerdefiniert: ${optionale.join(' + ')}`
      };
    }
    
    return match || PARAMETER_KOMBINATIONEN[0];
  };

  const currentConfig = getCurrentConfig();

  const handleCalculate = async () => {
    if (!nachname || !vornamen || !geburtsdatum || !geburtsort) return;

    setIsCalculating(true);
    try {
      const klient: KlientenDaten = {
        nachname,
        vornamen: vornamen.split(' ').filter(v => v.trim()),
        geburtsdatum: new Date(geburtsdatum),
        geburtsort,
        tcmTyp: tcmTyp || undefined,
        bildSignatur: bildSignatur || undefined,
        geburtsplanet: geburtsplanet || undefined,
        fünfElemente: showFünfElemente ? fünfElemente : undefined
      };

      const feldErgebnis = await berechneKlientenFeld(klient);
      setResult(feldErgebnis);
    } catch (error) {
      console.error('Fehler bei Klienten-Feldberechnung:', error);
    } finally {
      setIsCalculating(false);
    }
  };

  // Datenbank-Empfehlung berechnen
  const handleCalculateDbRecommendation = () => {
    if (!result) return;
    
    const elementProfile = result.tcmAnalyse.elementVerteilung as Record<TCMElement, number>;
    const dominantElement = result.tcmAnalyse.dominantesElement;
    
    // Fokus ermitteln: Custom oder Standard
    const fokusToUse = useCustomFokus ? dbCustomFokus : (dbFokus || null);
    const hasFokus = fokusToUse && fokusToUse.trim().length > 0;
    
    const recommendation = getTopDatabaseRecommendations(
      elementProfile,
      dominantElement,
      fokusToUse,
      hasFokus ? 0.4 : 0, // 40% Fokus-Gewichtung wenn Fokus gewählt
      useCustomFokus // Flag für Custom-Fokus Modus
    );
    
    setDbRecommendation(recommendation);
  };

  const formatNumber = (num: number) => {
    if (Math.abs(num) < 0.0001) return num.toExponential(3);
    return num.toFixed(4);
  };

  const getQualityColor = (value: number) => {
    if (value >= 90) return 'text-green-500';
    if (value >= 80) return 'text-emerald-500';
    if (value >= 70) return 'text-yellow-500';
    return 'text-orange-500';
  };

  const getQualityBg = (value: number) => {
    if (value >= 90) return 'bg-green-500/10';
    if (value >= 80) return 'bg-emerald-500/10';
    if (value >= 70) return 'bg-yellow-500/10';
    return 'bg-orange-500/10';
  };

  return (
    <div className="space-y-6">
      <Card className="border-primary/20">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <User className="w-6 h-6 text-primary" />
            Klienten-Feldalgorithmus
          </CardTitle>
          <CardDescription>
            Personalisierte Morphische Feldberechnung mit Bohm-Integration & TCM
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Patienten-Auswahl */}
          <Card className="border-primary/10 bg-gradient-to-r from-blue-500/5 to-purple-500/5">
            <CardContent className="pt-4">
              <div className="flex items-center gap-2 mb-3">
                <Users className="w-4 h-4 text-primary" />
                <span className="text-sm font-medium">Patient aus Datenbank laden</span>
                <Badge variant="outline" className="text-[10px]">Optional</Badge>
              </div>
              <Select value={selectedPatientId || "none"} onValueChange={(val) => handlePatientSelect(val === "none" ? "" : val)}>
                <SelectTrigger className="w-full">
                  <SelectValue placeholder={isLoadingPatients ? "Lade Patienten..." : "Patient auswählen (optional)"} />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="none">-- Manuell eingeben --</SelectItem>
                  {patients.map(patient => (
                    <SelectItem key={patient.id} value={patient.id}>
                      <div className="flex items-center gap-2">
                        {patient.last_name}, {patient.first_name}
                        {patient.image_signature && (
                          <Badge variant="secondary" className="text-[9px] px-1">
                            <ImageIcon className="w-3 h-3 mr-1" />
                            Bild
                          </Badge>
                        )}
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {selectedPatientId && (
                <p className="text-xs text-muted-foreground mt-2">
                  Daten werden automatisch aus dem Patientenprofil geladen
                </p>
              )}
            </CardContent>
          </Card>
          
          {/* Aktuelle Qualitätsanzeige */}
          <Card className={`${getQualityBg(currentConfig.akkuranz)} border-primary/10`}>
            <CardContent className="pt-4">
              <div className="flex items-center justify-between mb-3">
                <span className="text-sm font-medium">Aktuelle Konfiguration</span>
                <Button variant="ghost" size="sm" onClick={() => setShowMatrix(!showMatrix)}>
                  <Table className="w-4 h-4 mr-1" />
                  {showMatrix ? 'Matrix ausblenden' : 'Matrix anzeigen'}
                </Button>
              </div>
              <p className="text-xs text-muted-foreground mb-3">{currentConfig.beschreibung}</p>
              <div className="grid grid-cols-3 gap-4">
                <div className="text-center">
                  <TooltipProvider>
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <div className="cursor-help">
                          <p className="text-xs text-muted-foreground flex items-center justify-center gap-1">
                            Akkuranz <Info className="w-3 h-3" />
                          </p>
                          <p className={`text-xl font-bold ${getQualityColor(currentConfig.akkuranz)}`}>
                            {currentConfig.akkuranz}%
                          </p>
                        </div>
                      </TooltipTrigger>
                      <TooltipContent>
                        <p className="max-w-xs text-xs">
                          Genauigkeit der Feldberechnung bezogen auf die Resonanz-Identifikation des Klienten
                        </p>
                      </TooltipContent>
                    </Tooltip>
                  </TooltipProvider>
                </div>
                <div className="text-center">
                  <TooltipProvider>
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <div className="cursor-help">
                          <p className="text-xs text-muted-foreground flex items-center justify-center gap-1">
                            Effektivität <Info className="w-3 h-3" />
                          </p>
                          <p className={`text-xl font-bold ${getQualityColor(currentConfig.effektivität)}`}>
                            {currentConfig.effektivität}%
                          </p>
                        </div>
                      </TooltipTrigger>
                      <TooltipContent>
                        <p className="max-w-xs text-xs">
                          Wirksamkeit der Harmonisierung basierend auf der Feldstärke und Kohärenz
                        </p>
                      </TooltipContent>
                    </Tooltip>
                  </TooltipProvider>
                </div>
                <div className="text-center">
                  <TooltipProvider>
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <div className="cursor-help">
                          <p className="text-xs text-muted-foreground flex items-center justify-center gap-1">
                            Authentizität <Info className="w-3 h-3" />
                          </p>
                          <p className={`text-xl font-bold ${getQualityColor(currentConfig.authentizität)}`}>
                            {currentConfig.authentizität}%
                          </p>
                        </div>
                      </TooltipTrigger>
                      <TooltipContent>
                        <p className="max-w-xs text-xs">
                          Nachvollziehbarkeit und Reproduzierbarkeit der Berechnung nach Bohm'scher Ordnung
                        </p>
                      </TooltipContent>
                    </Tooltip>
                  </TooltipProvider>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Akkuranz-Matrix */}
          {showMatrix && (
            <Card className="border-primary/10 bg-muted/30">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm flex items-center gap-2">
                  <Table className="w-4 h-4" />
                  Parameter-Kombinations-Matrix
                </CardTitle>
                <CardDescription className="text-xs">
                  Geschätzte Qualitätswerte basierend auf Bohm'scher Ordnung & TCM-Integration
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <table className="w-full text-xs">
                    <thead>
                      <tr className="border-b border-primary/10">
                        <th className="text-left py-2 px-2 font-medium">Pflicht-Felder</th>
                        <th className="text-left py-2 px-2 font-medium">Optionale Felder</th>
                        <th className="text-center py-2 px-1 font-medium">Akk.</th>
                        <th className="text-center py-2 px-1 font-medium">Eff.</th>
                        <th className="text-center py-2 px-1 font-medium">Auth.</th>
                        <th className="text-left py-2 px-2 font-medium hidden md:table-cell">Beschreibung</th>
                      </tr>
                    </thead>
                    <tbody>
                      {PARAMETER_KOMBINATIONEN.map((kombination, idx) => {
                        const isCurrentConfig = 
                          kombination.optionaleFelder.length === currentConfig.optionaleFelder.length &&
                          kombination.optionaleFelder.every(f => currentConfig.optionaleFelder.includes(f));
                        
                        return (
                          <tr 
                            key={idx} 
                            className={`border-b border-primary/5 ${isCurrentConfig ? 'bg-primary/10' : 'hover:bg-muted/50'}`}
                          >
                            <td className="py-2 px-2 text-muted-foreground">
                              {kombination.pflichtFelder.slice(0, 2).join(', ')}...
                            </td>
                            <td className="py-2 px-2">
                              <div className="flex flex-wrap gap-1">
                                {kombination.optionaleFelder.length > 0 ? (
                                  kombination.optionaleFelder.map((f, i) => (
                                    <Badge key={i} variant="outline" className="text-[10px] px-1 py-0">
                                      {f}
                                    </Badge>
                                  ))
                                ) : (
                                  <span className="text-muted-foreground">—</span>
                                )}
                              </div>
                            </td>
                            <td className={`text-center py-2 px-1 font-medium ${getQualityColor(kombination.akkuranz)}`}>
                              {kombination.akkuranz}%
                            </td>
                            <td className={`text-center py-2 px-1 font-medium ${getQualityColor(kombination.effektivität)}`}>
                              {kombination.effektivität}%
                            </td>
                            <td className={`text-center py-2 px-1 font-medium ${getQualityColor(kombination.authentizität)}`}>
                              {kombination.authentizität}%
                            </td>
                            <td className="py-2 px-2 text-muted-foreground hidden md:table-cell">
                              {kombination.beschreibung}
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
                <p className="text-xs text-muted-foreground mt-3 italic">
                  * Werte basieren auf theoretischen Modellen der holographischen Ordnung (David Bohm) 
                  und morphischen Feldtheorie (Rupert Sheldrake). Höhere Werte bei mehr Parametern 
                  durch erhöhte Feldkohärenz und präzisere Resonanzidentifikation.
                </p>
              </CardContent>
            </Card>
          )}

          {/* Eingabefelder */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="nachname" className="flex items-center gap-1">
                Nachname <span className="text-destructive">*</span>
              </Label>
              <Input id="nachname" placeholder="Müller" value={nachname} onChange={(e) => setNachname(e.target.value)} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="vornamen" className="flex items-center gap-1">
                Vorname(n) <span className="text-destructive">*</span>
                <span className="text-xs text-muted-foreground ml-1">(durch Leerzeichen getrennt)</span>
              </Label>
              <Input id="vornamen" placeholder="Hans Peter" value={vornamen} onChange={(e) => setVornamen(e.target.value)} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="geburtsdatum" className="flex items-center gap-1">
                <Calendar className="w-4 h-4" />
                Geburtsdatum <span className="text-destructive">*</span>
              </Label>
              <Input id="geburtsdatum" type="date" value={geburtsdatum} onChange={(e) => setGeburtsdatum(e.target.value)} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="geburtsort" className="flex items-center gap-1">
                <MapPin className="w-4 h-4" />
                Geburtsort <span className="text-destructive">*</span>
              </Label>
              <Input id="geburtsort" placeholder="München" value={geburtsort} onChange={(e) => setGeburtsort(e.target.value)} />
            </div>
            
            {/* Optionale Felder */}
            <div className="space-y-2">
              <Label className="flex items-center gap-1">
                TCM-Konstitution 
                <Badge variant="outline" className="text-[10px] ml-1">optional</Badge>
              </Label>
              <Select value={tcmTyp || "none"} onValueChange={(v) => setTcmTyp(v === "none" ? '' : v as TCMElement)}>
                <SelectTrigger><SelectValue placeholder="Automatisch aus Geburtsdatum" /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="none">-- Nicht ausgewählt --</SelectItem>
                  <SelectItem value="holz">{ELEMENT_LABELS.holz}</SelectItem>
                  <SelectItem value="feuer">{ELEMENT_LABELS.feuer}</SelectItem>
                  <SelectItem value="erde">{ELEMENT_LABELS.erde}</SelectItem>
                  <SelectItem value="metall">{ELEMENT_LABELS.metall}</SelectItem>
                  <SelectItem value="wasser">{ELEMENT_LABELS.wasser}</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            {/* Geburtsplanet */}
            <div className="space-y-2">
              <Label className="flex items-center gap-1">
                🪐 Geburtsplanet 
                <Badge variant="outline" className="text-[10px] ml-1">optional</Badge>
              </Label>
              <Select value={geburtsplanet || "none"} onValueChange={(v) => setGeburtsplanet(v === "none" ? '' : v as Planet)}>
                <SelectTrigger><SelectValue placeholder="Planet auswählen" /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="none">-- Nicht ausgewählt --</SelectItem>
                  {Object.entries(PLANET_LABELS).map(([key, label]) => (
                    <SelectItem key={key} value={key}>{label}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            
            {/* 5-Elemente Profil */}
            <div className="space-y-2 md:col-span-2">
              <div className="flex items-center justify-between">
                <Label className="flex items-center gap-1">
                  🔮 5-Elemente-Profil (Akupunkturlehre)
                  <Badge variant="outline" className="text-[10px] ml-1">optional</Badge>
                </Label>
                <Button 
                  variant="ghost" 
                  size="sm" 
                  onClick={() => setShowFünfElemente(!showFünfElemente)}
                >
                  {showFünfElemente ? 'Ausblenden' : 'Aktivieren'}
                </Button>
              </div>
              
              {showFünfElemente && (
                <Card className="border-primary/10 bg-gradient-to-br from-amber-500/5 to-orange-500/5">
                  <CardContent className="pt-4 space-y-3">
                    {(Object.entries(fünfElemente) as [TCMElement, number][]).map(([element, value]) => (
                      <div key={element} className="space-y-1">
                        <div className="flex items-center justify-between">
                          <Label className="text-xs">{ELEMENT_LABELS[element]}</Label>
                          <span className="text-xs font-medium">{value}%</span>
                        </div>
                        <Input 
                          type="range" 
                          min="0" 
                          max="100" 
                          value={value}
                          onChange={(e) => setFünfElemente(prev => ({
                            ...prev,
                            [element]: parseInt(e.target.value)
                          }))}
                          className="h-2"
                        />
                      </div>
                    ))}
                    <p className="text-xs text-muted-foreground mt-2">
                      Gesamtsumme: {Object.values(fünfElemente).reduce((a, b) => a + b, 0)}% 
                      <span className="ml-2">(Empfohlen: ~100%)</span>
                    </p>
                  </CardContent>
                </Card>
              )}
            </div>
            
            <div className="space-y-2 md:col-span-2">
              <Label className="flex items-center gap-1">
                <ImageIcon className="w-4 h-4" />
                Klienten-Bild (Signatur)
                <Badge variant="outline" className="text-[10px] ml-1">optional</Badge>
              </Label>
              
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                onChange={handleImageUpload}
                className="hidden"
              />
              
              {bildPreview ? (
                <div className="relative w-32 h-32 rounded-lg border border-primary/20 overflow-hidden group">
                  <img 
                    src={bildPreview} 
                    alt="Klienten-Signatur" 
                    className="w-full h-full object-cover"
                  />
                  <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                    <Button
                      variant="destructive"
                      size="icon"
                      onClick={handleRemoveImage}
                      className="w-8 h-8"
                    >
                      <X className="w-4 h-4" />
                    </Button>
                  </div>
                  <Badge className="absolute bottom-1 right-1 text-[9px] bg-green-500">
                    Aktiv
                  </Badge>
                </div>
              ) : (
                <Button
                  variant="outline"
                  onClick={() => fileInputRef.current?.click()}
                  disabled={isUploading}
                  className="w-full h-24 border-dashed border-2 hover:border-primary/50 flex flex-col gap-2"
                >
                  {isUploading ? (
                    <>
                      <Loader2 className="w-6 h-6 animate-spin" />
                      <span className="text-xs">Hochladen...</span>
                    </>
                  ) : (
                    <>
                      <Upload className="w-6 h-6" />
                      <span className="text-xs">Bild hochladen (max. 5MB)</span>
                      <span className="text-[10px] text-muted-foreground">JPG, PNG, WebP</span>
                    </>
                  )}
                </Button>
              )}
              
              {/* Save to Patient Button */}
              {bildSignatur && selectedPatientId && (
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={saveImageToPatient}
                  disabled={isSavingToPatient}
                  className="w-full mt-2"
                >
                  {isSavingToPatient ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Speichern...
                    </>
                  ) : (
                    <>
                      <Link2 className="w-4 h-4 mr-2" />
                      Mit Patient verknüpfen
                    </>
                  )}
                </Button>
              )}
              
              <p className="text-xs text-muted-foreground">
                Erhöht Akkuranz um ~13% durch morphisches Feld-Anker
                {selectedPatientId && bildSignatur && (
                  <span className="block mt-1 text-primary">
                    Klicken Sie "Mit Patient verknüpfen" um das Bild dauerhaft zu speichern
                  </span>
                )}
              </p>
            </div>
          </div>

          <Button onClick={handleCalculate} disabled={!nachname || !vornamen || !geburtsdatum || !geburtsort || isCalculating} className="w-full" size="lg">
            {isCalculating ? <><Loader2 className="w-4 h-4 mr-2 animate-spin" />Berechne...</> : <><Sparkles className="w-4 h-4 mr-2" />Klienten-Feld Berechnen</>}
          </Button>

          {result && (
            <div className="space-y-4 pt-6 border-t">
              <h3 className="text-lg font-semibold flex items-center gap-2"><Heart className="w-5 h-5 text-primary" />Klienten-Feldanalyse</h3>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Card className="bg-gradient-to-br from-primary/5 to-primary/10">
                  <CardHeader className="pb-2"><CardTitle className="text-sm">Klienten-Wellenfunktion</CardTitle></CardHeader>
                  <CardContent><p className="text-xl font-bold text-primary">{formatNumber(result.klientenWellenfunktion)}</p></CardContent>
                </Card>
                <Card className="bg-gradient-to-br from-green-500/5 to-green-500/10">
                  <CardHeader className="pb-2"><CardTitle className="text-sm">Bohm-Faktor</CardTitle></CardHeader>
                  <CardContent><p className="text-xl font-bold text-green-600">{formatNumber(result.bohmIntegration.gesamtFaktor)}</p></CardContent>
                </Card>
                <Card className="bg-gradient-to-br from-orange-500/5 to-orange-500/10">
                  <CardHeader className="pb-2"><CardTitle className="text-sm">TCM-Faktor</CardTitle></CardHeader>
                  <CardContent><p className="text-xl font-bold text-orange-600">{formatNumber(result.tcmAnalyse.gesamtFaktor)}</p></CardContent>
                </Card>
              </div>

              {/* Qualitäts-Zusammenfassung */}
              <Card className="bg-gradient-to-br from-purple-500/5 to-purple-500/10">
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm">Berechnungsqualität</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-3 gap-4 text-center">
                    <div>
                      <p className="text-xs text-muted-foreground">Akkuranz</p>
                      <Progress value={currentConfig.akkuranz} className="h-2 mt-1" />
                      <p className={`text-sm font-medium mt-1 ${getQualityColor(currentConfig.akkuranz)}`}>
                        {currentConfig.akkuranz}%
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-muted-foreground">Effektivität</p>
                      <Progress value={currentConfig.effektivität} className="h-2 mt-1" />
                      <p className={`text-sm font-medium mt-1 ${getQualityColor(currentConfig.effektivität)}`}>
                        {currentConfig.effektivität}%
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-muted-foreground">Authentizität</p>
                      <Progress value={currentConfig.authentizität} className="h-2 mt-1" />
                      <p className={`text-sm font-medium mt-1 ${getQualityColor(currentConfig.authentizität)}`}>
                        {currentConfig.authentizität}%
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader><CardTitle className="text-sm flex items-center gap-2"><Leaf className="w-4 h-4" />Dominantes Element</CardTitle></CardHeader>
                <CardContent>
                  <div className="flex items-center gap-4">
                    <Badge className={`${ELEMENT_COLORS[result.tcmAnalyse.dominantesElement]} text-white text-lg px-4 py-2`}>
                      {ELEMENT_LABELS[result.tcmAnalyse.dominantesElement]}
                    </Badge>
                    <div className="text-sm text-muted-foreground">
                      Frequenzbereich: {result.tcmAnalyse.frequenzbereich.min}-{result.tcmAnalyse.frequenzbereich.max} Hz
                    </div>
                  </div>
                  <div className="mt-4 space-y-2">
                    {Object.entries(result.tcmAnalyse.elementVerteilung).map(([el, val]) => (
                      <div key={el} className="flex items-center gap-2">
                        <span className="w-16 text-xs">{ELEMENT_LABELS[el as TCMElement].split(' ')[0]}</span>
                        <Progress value={val} className="h-2 flex-1" />
                        <span className="w-10 text-xs text-right">{val}%</span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader><CardTitle className="text-sm">Meridian-Empfehlungen</CardTitle></CardHeader>
                <CardContent>
                  <div className="flex flex-wrap gap-2">
                    {result.empfehlungen.meridianPunkte.map((m, i) => (
                      <Badge key={i} variant="outline">{m.kürzel}{m.nummer} - {m.name}</Badge>
                    ))}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader><CardTitle className="text-sm">Bohm'sche Ordnung</CardTitle></CardHeader>
                <CardContent className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                  <div><span className="text-muted-foreground">Kohärenz:</span><br/>{(result.bohmIntegration.holomovement.kohärenz * 100).toFixed(1)}%</div>
                  <div><span className="text-muted-foreground">Ahnenfeld:</span><br/>{formatNumber(result.bohmIntegration.impliziteOrdnung.ahnenfeld)}</div>
                  <div><span className="text-muted-foreground">Seelenplan:</span><br/>{formatNumber(result.bohmIntegration.impliziteOrdnung.seelenplan)}</div>
                  <div><span className="text-muted-foreground">Harmonisierung:</span><br/>{(result.bohmIntegration.expliziteOrdnung.harmonisierungsbedarf * 100).toFixed(1)}%</div>
                </CardContent>
              </Card>

              {/* Datenbank-Empfehlung */}
              <Card className="border-primary/20 bg-gradient-to-br from-indigo-500/5 to-purple-500/5">
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-sm flex items-center gap-2">
                      <Database className="w-4 h-4 text-indigo-500" />
                      Top-3 Datenbank-Empfehlungen
                    </CardTitle>
                    <Button 
                      variant="ghost" 
                      size="sm"
                      onClick={() => setShowDbRecommendation(!showDbRecommendation)}
                    >
                      {showDbRecommendation ? 'Ausblenden' : 'Anzeigen'}
                    </Button>
                  </div>
                  <CardDescription className="text-xs">
                    Ermittelt relevante Datenbanken basierend auf Klientenvektor & Fokus
                  </CardDescription>
                </CardHeader>
                
                {showDbRecommendation && (
                  <CardContent className="space-y-4">
                    {/* Fokus-Auswahl */}
                    <div className="space-y-3">
                      {/* Toggle zwischen Standard und Custom */}
                      <div className="flex items-center gap-4">
                        <Button 
                          variant={!useCustomFokus ? 'default' : 'outline'}
                          size="sm"
                          onClick={() => setUseCustomFokus(false)}
                          className="text-xs"
                        >
                          Standard-Fokus
                        </Button>
                        <Button 
                          variant={useCustomFokus ? 'default' : 'outline'}
                          size="sm"
                          onClick={() => setUseCustomFokus(true)}
                          className="text-xs"
                        >
                          Custom-Fokus
                        </Button>
                      </div>
                      
                      <div className="flex flex-col sm:flex-row gap-3">
                        {!useCustomFokus ? (
                          <div className="flex-1">
                            <Label className="text-xs flex items-center gap-1 mb-2">
                              <Target className="w-3 h-3" />
                              Symptom-Fokus (optional)
                            </Label>
                            <Select value={dbFokus || "none"} onValueChange={(v) => setDbFokus(v === "none" ? '' : v)}>
                              <SelectTrigger className="h-9">
                                <SelectValue placeholder="Fokus wählen..." />
                              </SelectTrigger>
                              <SelectContent>
                                <SelectItem value="none">-- Kein Fokus (nur TCM) --</SelectItem>
                                {getAvailableFokusCategories().map(cat => (
                                  <SelectItem key={cat} value={cat}>{cat}</SelectItem>
                                ))}
                              </SelectContent>
                            </Select>
                          </div>
                        ) : (
                          <div className="flex-1">
                            <Label className="text-xs flex items-center gap-1 mb-2">
                              <Target className="w-3 h-3" />
                              Custom-Fokus Keywords
                            </Label>
                            <Input 
                              value={dbCustomFokus}
                              onChange={(e) => setDbCustomFokus(e.target.value)}
                              placeholder="z.B. Kopfschmerz, Migräne, Spannung..."
                              className="h-9"
                            />
                            <p className="text-[10px] text-muted-foreground mt-1">
                              Mehrere Keywords durch Komma getrennt eingeben
                            </p>
                          </div>
                        )}
                        <Button 
                          onClick={handleCalculateDbRecommendation}
                          className="sm:self-end"
                          size="sm"
                        >
                          <Sparkles className="w-4 h-4 mr-2" />
                          Ermitteln
                        </Button>
                      </div>
                    </div>

                    {/* Ergebnis anzeigen */}
                    {dbRecommendation && (
                      <div className="space-y-3 pt-3 border-t border-primary/10">
                        <div className="flex items-center justify-between text-xs">
                          <span className="text-muted-foreground">
                            Basis: {ELEMENT_LABELS[dbRecommendation.dominantElement || 'erde']}
                            {dbRecommendation.fokusCategory && (
                              <span className="ml-2">+ Fokus: {dbRecommendation.fokusCategory}</span>
                            )}
                          </span>
                          <Badge variant="secondary" className="text-[10px]">
                            Ø {dbRecommendation.totalScore}% Relevanz
                          </Badge>
                        </div>
                        
                        <div className="space-y-2">
                          {dbRecommendation.topDatabases.map((db, idx) => (
                            <div 
                              key={db.key}
                              className={`flex items-center gap-3 p-3 rounded-lg border transition-colors ${
                                idx === 0 
                                  ? 'bg-primary/10 border-primary/30' 
                                  : 'bg-muted/30 border-border/50 hover:bg-muted/50'
                              }`}
                            >
                              <div className="flex items-center justify-center w-8 h-8 rounded-full bg-background text-lg">
                                {db.icon}
                              </div>
                              <div className="flex-1 min-w-0">
                                <div className="flex items-center gap-2">
                                  <span className="font-medium text-sm truncate">{db.name}</span>
                                  <Badge 
                                    variant={db.category === 'anatomie' ? 'default' : 'secondary'}
                                    className="text-[9px] px-1.5"
                                  >
                                    {db.category === 'anatomie' ? 'Anatomie' : 'Frequenz'}
                                  </Badge>
                                </div>
                                <p className="text-xs text-muted-foreground truncate">
                                  {db.reasoning} • {db.entryCount} Einträge
                                </p>
                              </div>
                              <div className="text-right shrink-0">
                                <div className={`text-lg font-bold ${
                                  db.score >= 80 ? 'text-green-500' : 
                                  db.score >= 60 ? 'text-yellow-500' : 'text-orange-500'
                                }`}>
                                  {db.score}%
                                </div>
                                <div className="text-[10px] text-muted-foreground">
                                  TCM {db.tcmRelevanz}% | Fokus {db.fokusRelevanz}%
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                        
                        <p className="text-[10px] text-muted-foreground italic pt-2">
                          Empfehlungen basieren auf TCM-Organbeziehungen und Symptom-Fokus-Korrelation
                        </p>
                      </div>
                    )}
                  </CardContent>
                )}
              </Card>
            </div>
          )}

          {/* Wortenergie-Abtestung - Schritt 2 */}
          {result && (
            <WordEnergyTester 
              clientResult={result} 
              clientName={`${vornamen} ${nachname}`.trim()}
              patientId={selectedPatientId || undefined}
              sourceModule="morphic_field"
            />
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default ClientFieldCalculator;