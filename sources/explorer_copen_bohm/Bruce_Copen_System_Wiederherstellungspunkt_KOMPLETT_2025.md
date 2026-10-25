# Bruce Copen Algorithmus Visualisierung V2 - Kompletter Wiederherstellungspunkt 2025

## 📋 Dokument-Informationen

**Version:** 2.2 (Aktuell)  
**Datum:** 2025-01-16  
**Status:** Production Ready  
**Letzte Änderung:** Wortlängen-Adaptive Fibonacci Modulation hinzugefügt

---

## 🎯 System-Übersicht

Das Bruce Copen Algorithmus Visualisierung V2 System ist eine vollständig Cloud-synchronisierte Applikation zur Berechnung, Verwaltung und Harmonisierung von Copen-Raten basierend auf Wort-Energien.

### Kern-Features

1. **Ratengenerator mit Auto-Potenz-Projektion**
   - Berechnung von Copen-Raten basierend auf Wort-Energien
   - Automatische Potenz-Optimierung mit Hardware-Algorithmen
   - **NEU:** Wortlängen-adaptive Fibonacci-Modulation (optional)
   - Kozyrev-Spiegel Integration
   - Client-spezifische Raten-Berechnung

2. **Parallel Harmonisierungs-Sessions (Cloud-Sync)**
   - Bis zu 10 parallele Sessions pro Patient
   - Echtzeit-Synchronisation über Supabase
   - Pulse/Pause-Modus
   - Fortschritts-Tracking mit UI-Timer

3. **Datenbank-Analyse mit Fokus-Funktion**
   - Import von Wort-Datenbanken (CSV, PDF, TXT)
   - Batch-Harmonisierung
   - Focus-Word Analyse
   - Potenz-Nummern zu Worten Konversion

4. **Harmonisierungs-Archiv**
   - Cloud-basierte Speicherung
   - Reaktivierungs-Funktion
   - Filter- und Suchfunktionen

5. **Worker-Status-Monitoring**
   - Echtzeit-Heartbeat-Überwachung
   - Automatische Synchronisation

6. **Kozyrev-Indikatoren**
   - Zeitenergie-Visualisierung
   - Morphogenetische Feld-Resonanz
   - Real-time Updates

7. **Export-Funktionen**
   - PDF mit deutscher Lokalisierung
   - CSV für Datenanalyse
   - TXT mit Fokus-Word Highlighting

8. **Patient-Management V2**
   - Persönliche Raten
   - Bild-Signatur Integration (Ollama llava)
   - Hardware-Algorithmus-Konfiguration pro Patient

---

## 🏗️ Architektur

### Komponenten-Hierarchie

```
CopenVisualizationV2Page (Root)
├── CopenAlgorithmVisualizationV2 (Hauptsteuerung)
│   ├── PatientManagerCloudV2 (Patient-Management)
│   ├── HardwareAlgorithmSettings (Globale Hardware-Config)
│   ├── PatientHardwareConfig (Patienten-Hardware-Config)
│   ├── KozyrevIndicators (Zeitenergie-Anzeige)
│   ├── DatabaseManager (Datenbank-Import & Analyse)
│   ├── HarmonizationTemplates (Session-Templates)
│   └── HarmonizationArchiveCloud (Archiv-Verwaltung)
├── AnalysisArchiveCloud (Analyse-Historie)
├── SessionStatusList (Session-Übersicht)
└── WorkerStatusMonitor (Worker-Überwachung)
```

### Datenfluss

```
Benutzer-Eingabe (Wort)
    ↓
Normalisierung & Validierung
    ↓
Buchstaben-Wert-Berechnung
    ↓
Primärsumme × 1000
    ↓
[OPTION A: Authentic Copen]     [OPTION B: Adaptive Fibonacci]
Fibonacci-Modulation (21/34)     Wortlängen-adaptive Modulation
    ↓                                   ↓
Auto-Potenz-Berechnung          Auto-Potenz-Berechnung
(mit Hardware-Algorithmen)      (mit Hardware-Algorithmen)
    ↓                                   ↓
Kozyrev-Modulation (optional)   Kozyrev-Modulation (optional)
    ↓                                   ↓
        Finale Copen-Rate
            ↓
    Speicherung in Supabase
            ↓
    Edge Function Worker
            ↓
Echtzeit-Updates via Realtime-Channel
```

---

## 📦 Komponenten-Details

### 1. CopenVisualizationV2Page.tsx

**Pfad:** `src/pages/CopenVisualizationV2Page.tsx`

**Zweck:** Root-Container für die gesamte Visualisierungs-Seite

**Struktur:**
```typescript
- Navigation (Zurück-Button)
- CopenAlgorithmVisualizationV2 (Hauptkomponente)
- AnalysisArchiveCloud (Analyse-Historie)
- SessionStatusList (Session-Übersicht)
- WorkerStatusMonitor (Worker-Status)
```

**Styling:**
- Gradient-Hintergrund: `from-slate-900 via-blue-900 to-indigo-900`
- Container: `mx-auto px-4 py-8`
- Responsive Layout

---

### 2. CopenAlgorithmVisualizationV2.tsx

**Pfad:** `src/components/CopenAlgorithmVisualizationV2.tsx`

**Zweck:** Hauptsteuerungs-Komponente für Raten-Berechnung und Harmonisierung

#### State-Management

```typescript
// Basis-States
const [wordEnergy, setWordEnergy] = useState("");
const [potency, setPotency] = useState(12);
const [potencyType, setPotencyType] = useState<'D' | 'C'>('D');
const [autoCalculate, setAutoCalculate] = useState(true);
const [useAdaptiveFibonacci, setUseAdaptiveFibonacci] = useState(false); // NEU

// Kozyrev-Integration
const [useKozyrevMirror, setUseKozyrevMirror] = useState(false);
const [kozyrevIntensity, setKozyrevIntensity] = useState(0.5);
const [useAdaptiveKozyrev, setUseAdaptiveKozyrev] = useState(false);

// Harmonisierungen
const [activeHarmonizations, setActiveHarmonizations] = useState<ActiveHarmonization[]>([]);
const [selectedPatient, setSelectedPatient] = useState<CloudPatient | null>(null);

// UI-Control
const [showDetails, setShowDetails] = useState(false);
const [showArchive, setShowArchive] = useState(false);
const [showTemplates, setShowTemplates] = useState(false);
const [showDatabase, setShowDatabase] = useState(false);
```

#### Algorithmus-Funktionen

##### 1. Normalisierung

```typescript
const normalizeWordEnergy = (input: string): string => {
  return input
    .toLowerCase()
    .replace(/[^a-zäöüß\s]/g, '')
    .trim()
    .replace(/\s+/g, ' ');
};
```

##### 2. Buchstaben-Wert-Berechnung

```typescript
const getLetterValue = (letter: string, position: number): number => {
  const alphabetMap: { [key: string]: number } = {
    'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5,
    'f': 6, 'g': 7, 'h': 8, 'i': 9, 'j': 10,
    'k': 11, 'l': 12, 'm': 13, 'n': 14, 'o': 15,
    'p': 16, 'q': 17, 'r': 18, 's': 19, 't': 20,
    'u': 21, 'v': 22, 'w': 23, 'x': 24, 'y': 25,
    'z': 26, 'ä': 27, 'ö': 28, 'ü': 29, 'ß': 30
  };
  
  const baseValue = alphabetMap[letter] || 0;
  const positionWeight = 1 + (position * 0.1);
  
  return Math.round(baseValue * positionWeight);
};
```

##### 3. Auto-Potenz-Berechnung

```typescript
const calculateAutoPotency = (
  word: string,
  patient: CloudPatient | null,
  hardwareMetrics?: any
): { potency: number; type: 'D' | 'C' } => {
  
  // Basis-Energie berechnen
  const baseEnergy = word.split('').reduce((sum, letter, index) => {
    return sum + getLetterValue(letter, index);
  }, 0);
  
  // Hardware-Modulation
  let hardwareBoost = 1.0;
  if (hardwareMetrics?.combinedScore) {
    hardwareBoost = 1 + (hardwareMetrics.combinedScore * 0.2);
  }
  
  // Patient-spezifische Modulation
  let patientModulation = 1.0;
  if (patient?.hardware_config) {
    const config = patient.hardware_config;
    patientModulation = 1 + (
      (config.cpuJitter || 0) * 0.05 +
      (config.ramEntropy || 0) * 0.05 +
      (config.timeCoherence || 0) * 0.05
    );
  }
  
  // Kozyrev-Boost
  let kozyrevBoost = 1.0;
  if (useKozyrevMirror) {
    const timeField = Math.sin(Date.now() * 0.001) * kozyrevIntensity;
    kozyrevBoost = 1 + (timeField * 0.15);
  }
  
  // Finale Potenz berechnen
  const finalEnergy = baseEnergy * hardwareBoost * patientModulation * kozyrevBoost;
  
  // Potenz-Typ bestimmen
  let potency = 12;
  let type: 'D' | 'C' = 'D';
  
  if (finalEnergy < 100) {
    potency = 30;
    type = 'D';
  } else if (finalEnergy < 300) {
    potency = 12;
    type = 'D';
  } else if (finalEnergy < 600) {
    potency = 6;
    type = 'C';
  } else if (finalEnergy < 1000) {
    potency = 30;
    type = 'C';
  } else if (finalEnergy < 2000) {
    potency = 200;
    type = 'C';
  } else {
    potency = 1000;
    type = 'C';
  }
  
  return { potency, type };
};
```

##### 4. Wortlängen-Adaptive Fibonacci-Modulation (NEU)

```typescript
// Adaptive Fibonacci-Pair-Auswahl basierend auf Wortlänge
const getAdaptiveFibonacciPair = (wordLength: number): { multiplier: number; divisor: number } => {
  if (wordLength <= 4) {
    return { multiplier: 13, divisor: 21 }; // Kurze Wörter
  } else if (wordLength <= 10) {
    return { multiplier: 21, divisor: 34 }; // Mittlere Wörter (Standard)
  } else if (wordLength <= 20) {
    return { multiplier: 34, divisor: 55 }; // Lange Wörter
  } else {
    return { multiplier: 55, divisor: 89 }; // Sehr lange Wörter
  }
};

// Fibonacci-Modulation (mit optionaler Adaption)
let fibonacciRate: number;
if (useAdaptiveFibonacci) {
  const fibPair = getAdaptiveFibonacciPair(normalizedWord.length);
  fibonacciRate = Math.round(baseRate * (fibPair.multiplier / fibPair.divisor));
} else {
  // Authentic Copen: Festes 21/34 Verhältnis
  fibonacciRate = Math.round(baseRate * (21 / 34));
}
```

##### 5. Finale Raten-Berechnung

```typescript
// Berechnung der finalen Rate
const letterValues = normalizedWord.split('').map((letter, index) => ({
  letter,
  position: index + 1,
  value: getLetterValue(letter, index)
}));

const primarySum = letterValues.reduce((sum, item) => sum + item.value, 0);
const baseRate = primarySum * 1000;

// Fibonacci-Modulation (siehe oben)
let fibonacciRate = ...;

// Potenz-Modifier
const potencyModifier = potencyType === 'D' 
  ? potency * 100 
  : potency * 1000;

// Finale Rate
const finalRate = fibonacciRate + potencyModifier;
```

##### 6. Client-Rate-Berechnung

```typescript
const calculateClientRate = (patient: CloudPatient | null): string => {
  if (!patient) return "---";
  
  // Persönliche Rate hat Priorität
  if (patient.personal_rate) {
    return patient.personal_rate;
  }
  
  // Berechnung basierend auf Geburtsdaten
  const birthDate = patient.birth_date || "";
  const birthPlace = patient.birth_place || "";
  const fullName = `${patient.first_name} ${patient.last_name}`;
  
  const combinedString = `${fullName}${birthDate}${birthPlace}`.toLowerCase();
  
  const letterSum = combinedString.split('').reduce((sum, char, index) => {
    return sum + getLetterValue(char, index);
  }, 0);
  
  const baseClientRate = letterSum * 1000;
  const clientFibonacci = Math.round(baseClientRate * (21 / 34));
  const clientRate = clientFibonacci + 12000; // Default D12
  
  return `${Math.floor(clientRate / 1000)}-${(clientRate % 1000).toString().padStart(3, '0')}`;
};
```

#### Cloud-Integration

##### Supabase-Anbindung

```typescript
// Aktive Harmonisierungen laden
useEffect(() => {
  const loadActiveHarmonizations = async () => {
    if (!selectedPatient) return;
    
    const { data, error } = await supabase
      .from('harmonization_sessions_v2')
      .select('*')
      .eq('patient_id', selectedPatient.id)
      .in('status', ['active', 'paused'])
      .order('created_at', { ascending: false });
    
    if (data) {
      const harmonizations = data.map(session => ({
        id: session.id,
        word: session.word,
        rate: session.copen_rate || '',
        potency: session.tested_potency || '',
        duration: session.duration_seconds,
        progress: session.progress || 0,
        status: session.status as 'active' | 'paused',
        isPulsePause: session.pulse_pause_active || false,
        pulseSeconds: session.pulse_seconds || 30,
        pauseSeconds: session.pause_seconds || 30,
        uiProgress: session.progress || 0,
        lastUpdate: Date.now()
      }));
      
      setActiveHarmonizations(harmonizations);
    }
  };
  
  loadActiveHarmonizations();
}, [selectedPatient]);
```

##### Realtime-Subscription

```typescript
useEffect(() => {
  if (!selectedPatient) return;
  
  const channel = supabase
    .channel('harmonization_updates')
    .on(
      'postgres_changes',
      {
        event: '*',
        schema: 'public',
        table: 'harmonization_sessions_v2',
        filter: `patient_id=eq.${selectedPatient.id}`
      },
      (payload) => {
        if (payload.eventType === 'UPDATE') {
          const updated = payload.new;
          setActiveHarmonizations(prev => 
            prev.map(h => h.id === updated.id ? {
              ...h,
              progress: updated.progress || 0,
              status: updated.status,
              lastUpdate: Date.now()
            } : h)
          );
        }
      }
    )
    .subscribe();
  
  return () => {
    supabase.removeChannel(channel);
  };
}, [selectedPatient]);
```

##### Backend-Synchronisation

```typescript
// Periodische Sync mit Backend (alle 5 Sekunden)
useEffect(() => {
  const syncInterval = setInterval(async () => {
    const activeIds = activeHarmonizations
      .filter(h => h.status === 'active')
      .map(h => h.id);
    
    if (activeIds.length === 0) return;
    
    const { data } = await supabase
      .from('harmonization_sessions_v2')
      .select('id, progress, status')
      .in('id', activeIds);
    
    if (data) {
      setActiveHarmonizations(prev =>
        prev.map(h => {
          const backendData = data.find(d => d.id === h.id);
          if (backendData) {
            return {
              ...h,
              progress: backendData.progress || h.progress,
              status: backendData.status,
              lastUpdate: Date.now()
            };
          }
          return h;
        })
      );
    }
  }, 5000);
  
  return () => clearInterval(syncInterval);
}, [activeHarmonizations]);
```

##### UI-Timer für flüssige Anzeige

```typescript
// Lokaler UI-Timer für Fortschritt (alle 100ms)
useEffect(() => {
  const uiTimer = setInterval(() => {
    setActiveHarmonizations(prev =>
      prev.map(h => {
        if (h.status !== 'active') return h;
        
        const timeSinceUpdate = Date.now() - h.lastUpdate;
        const estimatedProgress = h.progress + (timeSinceUpdate / (h.duration * 10));
        
        return {
          ...h,
          uiProgress: Math.min(estimatedProgress, 100)
        };
      })
    );
  }, 100);
  
  return () => clearInterval(uiTimer);
}, []);
```

#### Session-Management-Funktionen

```typescript
// Neue Harmonisierung starten
const startNewHarmonization = async () => {
  const { data, error } = await supabase
    .from('harmonization_sessions_v2')
    .insert({
      patient_id: selectedPatient.id,
      word: normalizedWord,
      copen_rate: formattedRate,
      tested_potency: `${potency}${potencyType}`,
      duration_seconds: harmonizationDuration,
      pulse_pause_active: isPulsePause,
      pulse_seconds: pulseSeconds,
      pause_seconds: pauseSeconds,
      status: 'active',
      progress: 0
    })
    .select()
    .single();
  
  if (data) {
    setActiveHarmonizations(prev => [...prev, {
      id: data.id,
      word: data.word,
      rate: data.copen_rate,
      potency: data.tested_potency,
      duration: data.duration_seconds,
      progress: 0,
      status: 'active',
      isPulsePause: data.pulse_pause_active,
      pulseSeconds: data.pulse_seconds,
      pauseSeconds: data.pause_seconds,
      uiProgress: 0,
      lastUpdate: Date.now()
    }]);
  }
};

// Session pausieren
const pauseHarmonization = async (sessionId: string) => {
  await supabase
    .from('harmonization_sessions_v2')
    .update({ status: 'paused' })
    .eq('id', sessionId);
};

// Session fortsetzen
const resumeHarmonization = async (sessionId: string) => {
  await supabase
    .from('harmonization_sessions_v2')
    .update({ status: 'active' })
    .eq('id', sessionId);
};

// Session stoppen
const stopHarmonization = async (sessionId: string) => {
  await supabase
    .from('harmonization_sessions_v2')
    .update({ 
      status: 'completed',
      completed_at: new Date().toISOString(),
      progress: 100
    })
    .eq('id', sessionId);
};

// Session entfernen
const removeHarmonization = async (sessionId: string) => {
  await supabase
    .from('harmonization_sessions_v2')
    .delete()
    .eq('id', sessionId);
};

// Session aus Archiv reaktivieren
const reactivateSession = async (archivedSession: any) => {
  const { data } = await supabase
    .from('harmonization_sessions_v2')
    .insert({
      patient_id: archivedSession.patient_id,
      word: archivedSession.word,
      copen_rate: archivedSession.copen_rate,
      tested_potency: archivedSession.tested_potency,
      duration_seconds: archivedSession.duration_seconds,
      pulse_pause_active: archivedSession.pulse_pause_active,
      pulse_seconds: archivedSession.pulse_seconds,
      pause_seconds: archivedSession.pause_seconds,
      status: 'active',
      progress: 0
    })
    .select()
    .single();
};
```

---

### 3. DatabaseManager.tsx

**Pfad:** `src/components/DatabaseManager.tsx`

**Zweck:** Import, Analyse und Export von Wort-Datenbanken

#### Kern-Funktionen

##### 1. Datenbank-Import

```typescript
// Unterstützte Formate
- CSV (comma-separated)
- PDF (mit OCR)
- TXT (line-separated)

// Import-Funktion
const handleImport = async (file: File) => {
  let entries: string[] = [];
  
  if (file.name.endsWith('.csv')) {
    const text = await file.text();
    entries = text.split(/[,\n]/).map(e => e.trim()).filter(e => e);
  } else if (file.name.endsWith('.pdf')) {
    const arrayBuffer = await file.arrayBuffer();
    const pdf = await pdfjsLib.getDocument({ data: arrayBuffer }).promise;
    // ... PDF-Text-Extraktion
  } else if (file.name.endsWith('.txt')) {
    const text = await file.text();
    entries = text.split('\n').map(e => e.trim()).filter(e => e);
  }
  
  // In Supabase speichern
  await supabase
    .from('word_databases')
    .insert({
      name: file.name,
      entries: entries
    });
};
```

##### 2. Focus-Word Analyse (NEU)

```typescript
const analyzeFocusWord = async (focusWord: string, database: string[]) => {
  const results = [];
  
  for (const word of database) {
    // Berechne Rate für jedes Wort
    const rate = calculateCopenRate(word, potency, potencyType, useAdaptiveFibonacci);
    
    // Resonanz-Analyse
    const resonance = analyzeResonance(word, focusWord);
    
    results.push({
      word,
      rate: rate.finalRate,
      resonance: resonance.highestLevel,
      similarity: calculateSimilarity(word, focusWord)
    });
  }
  
  // Sortiere nach Resonanz
  return results.sort((a, b) => b.resonance - a.resonance);
};
```

##### 3. Potenz-Nummern zu Worten Konversion

```typescript
const convertPotencyToWords = (potency: number, type: 'D' | 'C'): string => {
  const mapping = {
    'D6': 'Sechs D',
    'D12': 'Zwölf D',
    'D30': 'Dreißig D',
    'C6': 'Sechs C',
    'C12': 'Zwölf C',
    'C30': 'Dreißig C',
    'C200': 'Zweihundert C',
    'C1000': 'Eintausend C'
  };
  
  return mapping[`${type}${potency}`] || `${potency} ${type}`;
};
```

##### 4. Batch-Harmonisierung

```typescript
const startBatchHarmonization = async (words: string[]) => {
  const batchDuration = words.length * 180; // 3 Minuten pro Wort
  
  for (const word of words) {
    await supabase
      .from('harmonization_sessions_v2')
      .insert({
        patient_id: selectedPatient.id,
        word: word,
        copen_rate: calculateRate(word),
        tested_potency: `${potency}${potencyType}`,
        duration_seconds: 180,
        status: 'pending',
        progress: 0
      });
  }
  
  toast.success(`${words.length} Sessions gestartet`);
};
```

#### Export-Funktionen

##### PDF-Export

```typescript
const exportToPDF = (results: ResonanceResult[], focusWord: string) => {
  const doc = new jsPDF();
  
  // Header
  doc.setFontSize(20);
  doc.text('Bruce Copen Datenbank-Analyse', 14, 20);
  
  // Focus-Word
  doc.setFontSize(12);
  doc.text(`Fokus-Wort: ${focusWord}`, 14, 30);
  doc.text(`Datum: ${new Date().toLocaleDateString('de-DE')}`, 14, 37);
  
  // Tabelle
  autoTable(doc, {
    startY: 45,
    head: [['Wort', 'Copen-Rate', 'Potenz', 'Höchste Resonanz']],
    body: results.map(r => [
      r.word === focusWord ? `>>> ${r.word} <<<` : r.word,
      r.copenRate,
      r.testedPotency,
      `Ebene ${r.highestResonanceLevel}: ${r.highestResonanceValue.toFixed(2)}`
    ]),
    styles: {
      fontSize: 10,
      cellPadding: 3
    },
    headStyles: {
      fillColor: [30, 58, 138],
      textColor: 255,
      fontStyle: 'bold'
    },
    alternateRowStyles: {
      fillColor: [240, 247, 255]
    }
  });
  
  doc.save(`Copen_Analyse_${focusWord}_${Date.now()}.pdf`);
};
```

##### CSV-Export

```typescript
const exportToCSV = (results: ResonanceResult[]) => {
  const headers = ['Wort', 'Copen-Rate', 'Potenz', 'Höchste Resonanz', 'Resonanz-Wert'];
  const rows = results.map(r => [
    r.word,
    r.copenRate,
    r.testedPotency,
    `Ebene ${r.highestResonanceLevel}`,
    r.highestResonanceValue.toFixed(4)
  ]);
  
  const csv = [
    headers.join(','),
    ...rows.map(row => row.join(','))
  ].join('\n');
  
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.download = `Copen_Export_${Date.now()}.csv`;
  link.click();
};
```

##### TXT-Export mit Focus-Highlighting

```typescript
const exportToTXT = (results: ResonanceResult[], focusWord: string) => {
  let text = 'BRUCE COPEN DATENBANK-ANALYSE\n';
  text += '='.repeat(50) + '\n\n';
  text += `Fokus-Wort: ${focusWord}\n`;
  text += `Datum: ${new Date().toLocaleString('de-DE')}\n`;
  text += `Anzahl Einträge: ${results.length}\n\n`;
  text += '='.repeat(50) + '\n\n';
  
  results.forEach((result, index) => {
    const isFocusWord = result.word === focusWord;
    
    if (isFocusWord) {
      text += `>>> FOKUS-WORT <<<\n`;
    }
    
    text += `${index + 1}. ${result.word}\n`;
    text += `   Copen-Rate: ${result.copenRate}\n`;
    text += `   Potenz: ${result.testedPotency}\n`;
    text += `   Höchste Resonanz: Ebene ${result.highestResonanceLevel} (${result.highestResonanceValue.toFixed(4)})\n`;
    
    if (isFocusWord) {
      text += `>>> FOKUS-WORT <<<\n`;
    }
    
    text += '\n';
  });
  
  const blob = new Blob([text], { type: 'text/plain;charset=utf-8;' });
  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.download = `Copen_Analyse_${focusWord}_${Date.now()}.txt`;
  link.click();
};
```

---

### 4. HardwareAlgorithmSettings.tsx

**Pfad:** `src/components/HardwareAlgorithmSettings.tsx`

**Zweck:** Globale Hardware-Algorithmus-Konfiguration

#### Hardware-Metriken

##### 1. CPU Quantum Jitter

```typescript
const measureCPUJitter = (): number => {
  const measurements: number[] = [];
  const iterations = 100;
  
  for (let i = 0; i < iterations; i++) {
    const start = performance.now();
    // Intensive Berechnung
    let sum = 0;
    for (let j = 0; j < 10000; j++) {
      sum += Math.sqrt(j) * Math.sin(j);
    }
    const end = performance.now();
    measurements.push(end - start);
  }
  
  // Standardabweichung berechnen
  const mean = measurements.reduce((a, b) => a + b) / measurements.length;
  const variance = measurements.reduce((sum, val) => 
    sum + Math.pow(val - mean, 2), 0
  ) / measurements.length;
  const stdDev = Math.sqrt(variance);
  
  // Normalisieren auf 0-1 Skala
  return Math.min(stdDev / 10, 1);
};
```

##### 2. RAM Entropy

```typescript
const measureRAMEntropy = (): number => {
  if (!performance.memory) return Math.random();
  
  const mem = performance.memory;
  const used = mem.usedJSHeapSize;
  const total = mem.totalJSHeapSize;
  const limit = mem.jsHeapSizeLimit;
  
  // Entropy aus Memory-Pattern
  const usageRatio = used / total;
  const limitRatio = total / limit;
  const entropy = Math.abs(Math.sin(usageRatio * Math.PI)) * limitRatio;
  
  return Math.min(entropy, 1);
};
```

##### 3. Time Source Coherence

```typescript
const measureTimeCoherence = (): number => {
  const samples = 50;
  const deltas: number[] = [];
  
  let lastTime = performance.now();
  for (let i = 0; i < samples; i++) {
    const currentTime = performance.now();
    deltas.push(currentTime - lastTime);
    lastTime = currentTime;
  }
  
  // Kohärenz aus Zeitstempel-Konsistenz
  const avgDelta = deltas.reduce((a, b) => a + b) / deltas.length;
  const variance = deltas.reduce((sum, delta) => 
    sum + Math.pow(delta - avgDelta, 2), 0
  ) / deltas.length;
  
  const coherence = 1 - Math.min(variance / 100, 1);
  return coherence;
};
```

##### 4. GPU Rendering Entropy

```typescript
const measureGPUEntropy = (): number => {
  const canvas = document.createElement('canvas');
  canvas.width = 64;
  canvas.height = 64;
  const ctx = canvas.getContext('2d');
  
  if (!ctx) return Math.random();
  
  // Rendering-Performance messen
  const start = performance.now();
  
  for (let i = 0; i < 100; i++) {
    ctx.fillStyle = `rgb(${i*2}, ${i*3}, ${i*5})`;
    ctx.fillRect(Math.random() * 64, Math.random() * 64, 10, 10);
  }
  
  const end = performance.now();
  const renderTime = end - start;
  
  // Normalisieren
  return Math.min(renderTime / 100, 1);
};
```

##### 5. Network Latency

```typescript
const measureNetworkLatency = async (): Promise<number> => {
  const iterations = 5;
  const latencies: number[] = [];
  
  for (let i = 0; i < iterations; i++) {
    const start = performance.now();
    try {
      await fetch('https://www.google.com/favicon.ico', { mode: 'no-cors' });
      const end = performance.now();
      latencies.push(end - start);
    } catch (error) {
      latencies.push(1000); // Fallback bei Fehler
    }
  }
  
  const avgLatency = latencies.reduce((a, b) => a + b) / latencies.length;
  
  // Invertiert und normalisiert (niedrige Latenz = hoher Score)
  return Math.max(0, 1 - (avgLatency / 1000));
};
```

#### Combined Score Berechnung

```typescript
const calculateCombinedScore = (metrics: HardwareMetrics): number => {
  const weights = {
    cpuJitter: 0.25,
    ramEntropy: 0.20,
    timeCoherence: 0.20,
    gpuEntropy: 0.20,
    networkLatency: 0.15
  };
  
  const score = 
    (metrics.cpuJitter * weights.cpuJitter) +
    (metrics.ramEntropy * weights.ramEntropy) +
    (metrics.timeCoherence * weights.timeCoherence) +
    (metrics.gpuEntropy * weights.gpuEntropy) +
    (metrics.networkLatency * weights.networkLatency);
  
  return Math.min(Math.max(score, 0), 1);
};
```

#### Quantum Seed Generation

```typescript
const generateQuantumSeed = (metrics: HardwareMetrics): string => {
  const timestamp = Date.now();
  const random = Math.random();
  
  const seedComponents = [
    timestamp.toString(36),
    (metrics.cpuJitter * 1000000).toString(36),
    (metrics.ramEntropy * 1000000).toString(36),
    (metrics.timeCoherence * 1000000).toString(36),
    (metrics.gpuEntropy * 1000000).toString(36),
    (metrics.networkLatency * 1000000).toString(36),
    random.toString(36).substring(2)
  ];
  
  return seedComponents.join('-').toUpperCase();
};
```

---

### 5. PatientHardwareConfig.tsx

**Pfad:** `src/components/PatientHardwareConfig.tsx`

**Zweck:** Patienten-spezifische Hardware-Konfiguration

#### Konfiguration pro Patient

```typescript
interface PatientHardwareConfig {
  cpuJitter: number;
  ramEntropy: number;
  timeCoherence: number;
  gpuEntropy: number;
  networkLatency: number;
  combinedScore: number;
  quantumSeed: string;
  lastCalibration: string;
}

// Speichern der Konfiguration
const savePatientConfig = async (config: PatientHardwareConfig) => {
  await supabase
    .from('patients_v2')
    .update({
      hardware_config: config
    })
    .eq('id', patient.id);
};

// Laden der Konfiguration
const loadPatientConfig = async (): Promise<PatientHardwareConfig | null> => {
  const { data } = await supabase
    .from('patients_v2')
    .select('hardware_config')
    .eq('id', patient.id)
    .single();
  
  return data?.hardware_config || null;
};
```

#### Kalibrierung pro Patient

```typescript
const calibratePatientHardware = async () => {
  // Alle Metriken messen
  const metrics = {
    cpuJitter: await measureCPUJitter(),
    ramEntropy: await measureRAMEntropy(),
    timeCoherence: await measureTimeCoherence(),
    gpuEntropy: await measureGPUEntropy(),
    networkLatency: await measureNetworkLatency()
  };
  
  // Combined Score berechnen
  const combinedScore = calculateCombinedScore(metrics);
  
  // Quantum Seed generieren
  const quantumSeed = generateQuantumSeed(metrics);
  
  // Konfiguration zusammenstellen
  const config: PatientHardwareConfig = {
    ...metrics,
    combinedScore,
    quantumSeed,
    lastCalibration: new Date().toISOString()
  };
  
  // In Datenbank speichern
  await savePatientConfig(config);
  
  toast.success('Hardware-Kalibrierung abgeschlossen');
};
```

---

### 6. PatientManagerCloudV2.tsx

**Pfad:** `src/components/PatientManagerCloudV2.tsx`

**Zweck:** Erweiterte Patient-Verwaltung mit persönlichen Raten und Bild-Signatur

#### Patienten-Datenstruktur

```typescript
interface CloudPatient {
  id: string;
  user_id: string;
  first_name: string;
  last_name: string;
  birth_date: string;
  birth_place: string;
  personal_rate: string | null;
  image_signature: string | null;
  image_signature_active: boolean;
  hardware_config: PatientHardwareConfig | null;
  created_at: string;
  updated_at: string;
}
```

#### Persönliche Rate

```typescript
// Persönliche Rate setzen
const setPersonalRate = async (patientId: string, rate: string) => {
  await supabase
    .from('patients_v2')
    .update({ personal_rate: rate })
    .eq('id', patientId);
};

// Persönliche Rate verwenden
const getEffectiveRate = (patient: CloudPatient, calculatedRate: string): string => {
  if (patient.personal_rate && patient.personal_rate.trim() !== '') {
    return patient.personal_rate;
  }
  return calculatedRate;
};
```

#### Bild-Signatur Integration (Ollama llava)

```typescript
// Bild hochladen und analysieren
const uploadImageSignature = async (file: File, patientId: string) => {
  // Bild zu Base64 konvertieren
  const base64 = await fileToBase64(file);
  
  // Optional: Ollama llava Analyse
  try {
    const analysis = await analyzeImageWithOllama(base64);
    console.log('Bild-Analyse:', analysis);
  } catch (error) {
    console.error('Ollama-Analyse fehlgeschlagen:', error);
  }
  
  // Bild-Signatur speichern
  await supabase
    .from('patients_v2')
    .update({
      image_signature: base64,
      image_signature_active: true
    })
    .eq('id', patientId);
  
  toast.success('Bild-Signatur gespeichert');
};

// Ollama llava Integration
const analyzeImageWithOllama = async (base64Image: string): Promise<string> => {
  const response = await fetch('http://localhost:11434/api/generate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      model: 'llava',
      prompt: 'Analysiere dieses Bild im Kontext von bioenergetischen Signaturen.',
      images: [base64Image.split(',')[1]]
    })
  });
  
  const data = await response.json();
  return data.response;
};

// Bild-Signatur aktivieren/deaktivieren
const toggleImageSignature = async (patientId: string, active: boolean) => {
  await supabase
    .from('patients_v2')
    .update({ image_signature_active: active })
    .eq('id', patientId);
};
```

---

### 7. KozyrevIndicators.tsx

**Pfad:** `src/components/KozyrevIndicators.tsx`

**Zweck:** Visualisierung von Kozyrev Zeitenergie-Feldern

#### Kozyrev-Berechnungen

```typescript
// Zeitenergie-Feld berechnen
const calculateTimeField = (intensity: number): number => {
  const timestamp = Date.now();
  const sineWave = Math.sin(timestamp * 0.001);
  const cosineWave = Math.cos(timestamp * 0.0007);
  
  return (sineWave + cosineWave) / 2 * intensity;
};

// Morphogenetisches Feld
const calculateMorphogenetic = (wordEnergy: string): number => {
  const letterSum = wordEnergy.split('').reduce((sum, char) => {
    return sum + char.charCodeAt(0);
  }, 0);
  
  const normalized = (letterSum % 100) / 100;
  return Math.sin(normalized * Math.PI * 2);
};

// Torsionsfeld-Resonanz
const calculateTorsion = (timeField: number, morphoField: number): number => {
  return (timeField * 0.6) + (morphoField * 0.4);
};
```

#### Echtzeit-Visualisierung

```typescript
const KozyrevIndicators = ({ 
  intensity, 
  wordEnergy, 
  isActive 
}: Props) => {
  const [timeField, setTimeField] = useState(0);
  const [morphoField, setMorphoField] = useState(0);
  const [torsionField, setTorsionField] = useState(0);
  
  useEffect(() => {
    if (!isActive) return;
    
    const interval = setInterval(() => {
      const tf = calculateTimeField(intensity);
      const mf = calculateMorphogenetic(wordEnergy);
      const tor = calculateTorsion(tf, mf);
      
      setTimeField(tf);
      setMorphoField(mf);
      setTorsionField(tor);
    }, 100);
    
    return () => clearInterval(interval);
  }, [isActive, intensity, wordEnergy]);
  
  return (
    <div className="space-y-2">
      <div>
        <Label>Zeitenergie-Feld</Label>
        <Progress value={(timeField + 1) * 50} />
        <span>{timeField.toFixed(3)}</span>
      </div>
      
      <div>
        <Label>Morphogenetisches Feld</Label>
        <Progress value={(morphoField + 1) * 50} />
        <span>{morphoField.toFixed(3)}</span>
      </div>
      
      <div>
        <Label>Torsionsfeld-Resonanz</Label>
        <Progress value={(torsionField + 1) * 50} />
        <span>{torsionField.toFixed(3)}</span>
      </div>
    </div>
  );
};
```

---

### 8. WorkerStatusMonitor.tsx

**Pfad:** `src/components/WorkerStatusMonitor.tsx`

**Zweck:** Überwachung des Edge Function Workers

#### Heartbeat-Überwachung

```typescript
const WorkerStatusMonitor = () => {
  const [workerStatus, setWorkerStatus] = useState<'online' | 'offline' | 'unknown'>('unknown');
  const [lastHeartbeat, setLastHeartbeat] = useState<Date | null>(null);
  const [activeSessions, setActiveSessions] = useState(0);
  
  useEffect(() => {
    const checkWorkerStatus = async () => {
      const { data } = await supabase
        .from('harmonization_sessions_v2')
        .select('job_last_heartbeat, status')
        .eq('status', 'active');
      
      if (data && data.length > 0) {
        const latestHeartbeat = data
          .map(s => new Date(s.job_last_heartbeat))
          .sort((a, b) => b.getTime() - a.getTime())[0];
        
        const timeSinceHeartbeat = Date.now() - latestHeartbeat.getTime();
        
        if (timeSinceHeartbeat < 30000) {
          setWorkerStatus('online');
        } else {
          setWorkerStatus('offline');
        }
        
        setLastHeartbeat(latestHeartbeat);
        setActiveSessions(data.length);
      } else {
        setWorkerStatus('offline');
        setActiveSessions(0);
      }
    };
    
    checkWorkerStatus();
    const interval = setInterval(checkWorkerStatus, 10000);
    
    return () => clearInterval(interval);
  }, []);
  
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Activity className={workerStatus === 'online' ? 'text-green-500' : 'text-red-500'} />
          Worker Status: {workerStatus}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <p>Aktive Sessions: {activeSessions}</p>
        {lastHeartbeat && (
          <p>Letzter Heartbeat: {lastHeartbeat.toLocaleTimeString('de-DE')}</p>
        )}
      </CardContent>
    </Card>
  );
};
```

---

### 9. HarmonizationArchiveCloud.tsx

**Pfad:** `src/components/HarmonizationArchiveCloud.tsx`

**Zweck:** Cloud-basiertes Archiv abgeschlossener Harmonisierungen

#### Archiv-Verwaltung

```typescript
// Abgeschlossene Sessions laden
const loadCompletedSessions = async () => {
  const { data } = await supabase
    .from('harmonization_sessions_v2')
    .select('*')
    .eq('status', 'completed')
    .order('completed_at', { ascending: false })
    .limit(50);
  
  return data || [];
};

// Session reaktivieren
const reactivateSession = async (session: HarmonizationSession) => {
  const { data } = await supabase
    .from('harmonization_sessions_v2')
    .insert({
      patient_id: session.patient_id,
      word: session.word,
      copen_rate: session.copen_rate,
      tested_potency: session.tested_potency,
      duration_seconds: session.duration_seconds,
      pulse_pause_active: session.pulse_pause_active,
      pulse_seconds: session.pulse_seconds,
      pause_seconds: session.pause_seconds,
      status: 'active',
      progress: 0
    })
    .select()
    .single();
  
  if (data) {
    toast.success('Session reaktiviert');
  }
};

// Session löschen
const deleteSession = async (sessionId: string) => {
  await supabase
    .from('harmonization_sessions_v2')
    .delete()
    .eq('id', sessionId);
  
  toast.success('Session gelöscht');
};
```

---

## 📊 Datenstrukturen

### CloudPatient (V2)

```typescript
interface CloudPatient {
  id: string;                              // UUID
  user_id: string;                         // Auth User ID
  first_name: string;                      // Vorname
  last_name: string;                       // Nachname
  birth_date: string;                      // Geburtsdatum
  birth_place: string;                     // Geburtsort
  personal_rate: string | null;            // Persönliche Rate (optional)
  image_signature: string | null;          // Bild-Signatur (Base64)
  image_signature_active: boolean;         // Bild-Signatur aktiv?
  hardware_config: PatientHardwareConfig | null; // Hardware-Konfiguration
  created_at: string;                      // Erstellungsdatum
  updated_at: string;                      // Aktualisierungsdatum
}
```

### CloudHarmonizationSession (V2)

```typescript
interface CloudHarmonizationSession {
  id: string;                    // UUID
  user_id: string;               // Auth User ID
  patient_id: string;            // Patienten-ID
  word: string;                  // Harmonisierungs-Wort
  copen_rate: string;            // Berechnete Rate (Format: "XX-XXX")
  tested_potency: string;        // Potenz (z.B. "12D", "30C")
  duration_seconds: number;      // Gesamtdauer in Sekunden
  remaining_seconds: number;     // Verbleibende Zeit
  progress: number;              // Fortschritt (0-100)
  status: 'pending' | 'active' | 'paused' | 'completed' | 'cancelled';
  pulse_pause_active: boolean;   // Pulse/Pause aktiviert?
  pulse_seconds: number;         // Pulse-Dauer
  pause_seconds: number;         // Pause-Dauer
  started_at: string | null;     // Startzeitpunkt
  completed_at: string | null;   // Abschlusszeitpunkt
  job_started_at: string | null; // Worker-Start
  job_last_heartbeat: string | null; // Letzter Heartbeat
  created_at: string;            // Erstellungsdatum
  updated_at: string;            // Aktualisierungsdatum
}
```

### ActiveHarmonization (Frontend)

```typescript
interface ActiveHarmonization {
  id: string;              // Session-ID
  word: string;            // Wort
  rate: string;            // Rate
  potency: string;         // Potenz
  duration: number;        // Dauer (Sekunden)
  progress: number;        // Backend-Fortschritt
  status: 'active' | 'paused'; // Status
  isPulsePause: boolean;   // Pulse/Pause?
  pulseSeconds: number;    // Pulse-Zeit
  pauseSeconds: number;    // Pause-Zeit
  uiProgress: number;      // UI-Fortschritt (interpoliert)
  lastUpdate: number;      // Letztes Backend-Update (Timestamp)
}
```

### ResonanceResult (Analyse)

```typescript
interface ResonanceResult {
  word: string;                    // Analysiertes Wort
  copenRate: string;               // Berechnete Rate
  testedPotency: string;           // Verwendete Potenz
  highestResonanceLevel: number;   // Höchste Resonanz-Ebene (1-13)
  highestResonanceValue: number;   // Höchster Resonanz-Wert
  level1_physical_particles: number;
  level2_physical_structure: number;
  level3_etheric_prana: number;
  level4_etheric_meridians: number;
  level5_astral_emotions: number;
  level6_astral_thoughts: number;
  level7_mental_time: number;
  level8_mental_constructs: number;
  level9_causal_blueprints: number;
  level10_causal_alchemy: number;
  level11_atmic_identity: number;
  level12_atmic_love: number;
  level13_creator: number;
}
```

### HardwareMetrics

```typescript
interface HardwareMetrics {
  cpuJitter: number;           // 0-1
  ramEntropy: number;          // 0-1
  timeCoherence: number;       // 0-1
  gpuEntropy: number;          // 0-1
  networkLatency: number;      // 0-1
  combinedScore: number;       // 0-1
  quantumSeed: string;         // Eindeutiger Seed
  timestamp: number;           // Messzeitpunkt
}
```

### PatientHardwareConfig

```typescript
interface PatientHardwareConfig {
  cpuJitter: number;
  ramEntropy: number;
  timeCoherence: number;
  gpuEntropy: number;
  networkLatency: number;
  combinedScore: number;
  quantumSeed: string;
  lastCalibration: string;     // ISO-8601 Datum
}
```

---

## 🧮 Algorithmen

### 1. Wort-Energie-Normalisierung

```
EINGABE: Beliebiger String
AUSGABE: Normalisierter String

SCHRITTE:
1. Zu Kleinbuchstaben konvertieren
2. Entferne alle Zeichen außer: a-z, ä, ö, ü, ß, Leerzeichen
3. Trim (Entferne führende/folgende Leerzeichen)
4. Mehrfache Leerzeichen zu einzelnen reduzieren

BEISPIEL:
"Hallo Welt! 123" → "hallo welt"
```

### 2. Buchstaben-Wert-Berechnung

```
ALPHABET-MAPPING:
a=1, b=2, c=3, ..., z=26, ä=27, ö=28, ü=29, ß=30

POSITIONS-GEWICHTUNG:
Wert = Basis-Wert × (1 + Position × 0.1)

BEISPIEL:
"abc"
a (Position 0): 1 × (1 + 0 × 0.1) = 1
b (Position 1): 2 × (1 + 1 × 0.1) = 2.2 → 2
c (Position 2): 3 × (1 + 2 × 0.1) = 3.6 → 4

Summe: 1 + 2 + 4 = 7
```

### 3. Fibonacci-Modulation

#### A) Authentic Copen (Standard)

```
Fibonacci-Rate = Basis-Rate × (21 / 34)

BEISPIEL:
Basis-Rate = 7000
Fibonacci-Rate = 7000 × 0.617647 = 4323.53 → 4324
```

#### B) Wortlängen-Adaptive Modulation (NEU)

```
WORTLÄNGE → FIBONACCI-PAIR

1-4 Zeichen:    13/21  (0.619048)
5-10 Zeichen:   21/34  (0.617647) ← Standard
11-20 Zeichen:  34/55  (0.618182)
>20 Zeichen:    55/89  (0.617978)

BEISPIEL:
Wort: "Liebe" (5 Zeichen)
→ 21/34 Pair
Fibonacci-Rate = 7000 × 0.617647 = 4324

Wort: "Transformation" (14 Zeichen)
→ 34/55 Pair
Fibonacci-Rate = 7000 × 0.618182 = 4327
```

### 4. Raten-Formatierung

```
EINGABE: Numerische Rate (z.B. 16324)
AUSGABE: Formatierte Rate (z.B. "16-324")

ALGORITHMUS:
1. Ganzzahl-Teil = Rate ÷ 1000 (gerundet nach unten)
2. Rest = Rate % 1000
3. Format: "{Ganzzahl}-{Rest mit 3 Ziffern}"

BEISPIELE:
16324 → "16-324"
5678  → "5-678"
123   → "0-123"
```

### 5. Auto-Potenz-Berechnung

```
EINGABE: 
- Normalisiertes Wort
- Patient-Daten (optional)
- Hardware-Metriken (optional)
- Kozyrev-Einstellungen (optional)

BERECHNUNG:

1. BASIS-ENERGIE
   baseEnergy = Σ(Buchstaben-Werte)

2. HARDWARE-BOOST
   IF hardwareMetrics EXISTS:
     hardwareBoost = 1 + (combinedScore × 0.2)
   ELSE:
     hardwareBoost = 1.0

3. PATIENTEN-MODULATION
   IF patient.hardware_config EXISTS:
     patientMod = 1 + (
       cpuJitter × 0.05 +
       ramEntropy × 0.05 +
       timeCoherence × 0.05
     )
   ELSE:
     patientMod = 1.0

4. KOZYREV-BOOST
   IF useKozyrevMirror:
     timeField = sin(timestamp × 0.001) × intensity
     kozyrevBoost = 1 + (timeField × 0.15)
   ELSE:
     kozyrevBoost = 1.0

5. FINALE ENERGIE
   finalEnergy = baseEnergy × hardwareBoost × patientMod × kozyrevBoost

6. POTENZ-BESTIMMUNG
   IF finalEnergy < 100:
     → 30D
   ELSE IF finalEnergy < 300:
     → 12D
   ELSE IF finalEnergy < 600:
     → 6C
   ELSE IF finalEnergy < 1000:
     → 30C
   ELSE IF finalEnergy < 2000:
     → 200C
   ELSE:
     → 1000C

AUSGABE: { potency: Zahl, type: 'D' | 'C' }
```

### 6. Potenz-Nummern zu Worten Konversion

```
MAPPING:
D6    → "Sechs D"
D12   → "Zwölf D"
D30   → "Dreißig D"
C6    → "Sechs C"
C12   → "Zwölf C"
C30   → "Dreißig C"
C200  → "Zweihundert C"
C1000 → "Eintausend C"

VERWENDUNG:
Wird in PDF/TXT-Exporten und Datenbank-Analyse-Berichten verwendet.
```

---

## ☁️ Cloud-Integration

### Supabase-Schema

#### Tabelle: `patients_v2`

```sql
CREATE TABLE patients_v2 (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id),
  first_name TEXT NOT NULL,
  last_name TEXT NOT NULL,
  birth_date TEXT NOT NULL,
  birth_place TEXT NOT NULL,
  personal_rate TEXT,
  image_signature TEXT,
  image_signature_active BOOLEAN DEFAULT true,
  hardware_config JSONB,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- RLS Policies
ALTER TABLE patients_v2 ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own patients v2"
  ON patients_v2 FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own patients v2"
  ON patients_v2 FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own patients v2"
  ON patients_v2 FOR UPDATE
  USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own patients v2"
  ON patients_v2 FOR DELETE
  USING (auth.uid() = user_id);

-- Indexes
CREATE INDEX idx_patients_v2_user_id ON patients_v2(user_id);
CREATE INDEX idx_patients_v2_created_at ON patients_v2(created_at DESC);
```

#### Tabelle: `harmonization_sessions_v2`

```sql
CREATE TABLE harmonization_sessions_v2 (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id),
  patient_id UUID NOT NULL REFERENCES patients_v2(id) ON DELETE CASCADE,
  word TEXT NOT NULL,
  copen_rate TEXT,
  tested_potency TEXT,
  duration_seconds INTEGER NOT NULL,
  remaining_seconds INTEGER,
  progress INTEGER DEFAULT 0,
  status TEXT NOT NULL DEFAULT 'pending',
  pulse_pause_active BOOLEAN DEFAULT false,
  pulse_seconds INTEGER,
  pause_seconds INTEGER,
  started_at TIMESTAMPTZ,
  completed_at TIMESTAMPTZ,
  job_started_at TIMESTAMPTZ,
  job_last_heartbeat TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- RLS Policies
ALTER TABLE harmonization_sessions_v2 ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own sessions v2"
  ON harmonization_sessions_v2 FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own sessions v2"
  ON harmonization_sessions_v2 FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own sessions v2"
  ON harmonization_sessions_v2 FOR UPDATE
  USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own sessions v2"
  ON harmonization_sessions_v2 FOR DELETE
  USING (auth.uid() = user_id);

-- Indexes
CREATE INDEX idx_sessions_v2_patient_id ON harmonization_sessions_v2(patient_id);
CREATE INDEX idx_sessions_v2_status ON harmonization_sessions_v2(status);
CREATE INDEX idx_sessions_v2_created_at ON harmonization_sessions_v2(created_at DESC);
```

#### Tabelle: `analysis_archives_v2`

```sql
CREATE TABLE analysis_archives_v2 (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id),
  patient_id UUID REFERENCES patients_v2(id) ON DELETE SET NULL,
  word TEXT NOT NULL,
  copen_rate TEXT NOT NULL,
  tested_potency TEXT,
  highest_resonance_level INTEGER,
  highest_resonance_value NUMERIC,
  level_1_physical_particles NUMERIC,
  level_2_physical_structure NUMERIC,
  level_3_etheric_prana NUMERIC,
  level_4_etheric_meridians NUMERIC,
  level_5_astral_emotions NUMERIC,
  level_6_astral_thoughts NUMERIC,
  level_7_mental_time NUMERIC,
  level_8_mental_constructs NUMERIC,
  level_9_causal_blueprints NUMERIC,
  level_10_causal_alchemy NUMERIC,
  level_11_atmic_identity NUMERIC,
  level_12_atmic_love NUMERIC,
  level_13_creator NUMERIC,
  database_entries TEXT[],
  patient_data JSONB,
  analysis_timestamp TIMESTAMPTZ DEFAULT now(),
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- RLS + Indexes ähnlich wie oben
```

#### Tabelle: `harmonization_templates_v2`

```sql
CREATE TABLE harmonization_templates_v2 (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id),
  patient_id UUID NOT NULL REFERENCES patients_v2(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  description TEXT,
  sessions JSONB NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- RLS + Indexes
```

#### Tabelle: `word_databases`

```sql
CREATE TABLE word_databases (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id),
  name TEXT NOT NULL,
  entries TEXT[] NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- RLS + Indexes
```

### Edge Function: `harmonization-worker`

**Pfad:** `supabase/functions/harmonization-worker/index.ts`

**Zweck:** Backend-Worker zur Verarbeitung aktiver Harmonisierungs-Sessions

#### Workflow

```
1. STARTUP
   - Supabase-Client initialisieren
   - Aktive Sessions abfragen (status = 'active')

2. SESSION PROCESSING LOOP
   FOR EACH active_session:
     a) Berechne Fortschritt:
        elapsed = now - session.started_at
        progress = (elapsed / duration) × 100
     
     b) Pulse/Pause-Logik:
        IF pulse_pause_active:
          cycle = pulse_seconds + pause_seconds
          position = elapsed % cycle
          IF position > pulse_seconds:
            → SKIP (Pause-Phase)
     
     c) Update Session:
        UPDATE harmonization_sessions_v2
        SET 
          progress = calculated_progress,
          remaining_seconds = duration - elapsed,
          job_last_heartbeat = now()
        WHERE id = session.id
     
     d) Completion Check:
        IF progress >= 100:
          UPDATE status = 'completed',
                 completed_at = now(),
                 progress = 100

3. HEARTBEAT
   - Alle 10 Sekunden
   - Setze job_last_heartbeat für alle aktiven Jobs

4. SLEEP
   - Warte 1 Sekunde
   - Gehe zu Schritt 2

5. ERROR HANDLING
   - Bei Fehler: Logge und fahre fort
   - Kritischer Fehler: Markiere Session als 'cancelled'
```

#### Code-Struktur

```typescript
import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2';

serve(async (req) => {
  const supabaseUrl = Deno.env.get('SUPABASE_URL')!;
  const supabaseKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!;
  const supabase = createClient(supabaseUrl, supabaseKey);
  
  while (true) {
    try {
      // Aktive Sessions laden
      const { data: sessions } = await supabase
        .from('harmonization_sessions_v2')
        .select('*')
        .eq('status', 'active');
      
      if (sessions && sessions.length > 0) {
        for (const session of sessions) {
          await processSession(session, supabase);
        }
      }
      
      // 1 Sekunde warten
      await new Promise(resolve => setTimeout(resolve, 1000));
      
    } catch (error) {
      console.error('Worker error:', error);
      await new Promise(resolve => setTimeout(resolve, 5000));
    }
  }
});

async function processSession(session: any, supabase: any) {
  const now = new Date();
  const started = new Date(session.started_at || session.created_at);
  const elapsed = (now.getTime() - started.getTime()) / 1000;
  
  let progress = Math.min((elapsed / session.duration_seconds) * 100, 100);
  
  // Pulse/Pause-Logik
  if (session.pulse_pause_active) {
    const cycle = session.pulse_seconds + session.pause_seconds;
    const positionInCycle = elapsed % cycle;
    
    if (positionInCycle > session.pulse_seconds) {
      // In Pause-Phase, Fortschritt nicht erhöhen
      return;
    }
  }
  
  const remaining = Math.max(session.duration_seconds - elapsed, 0);
  
  // Update Session
  await supabase
    .from('harmonization_sessions_v2')
    .update({
      progress: Math.round(progress),
      remaining_seconds: Math.round(remaining),
      job_last_heartbeat: now.toISOString(),
      ...(progress >= 100 && {
        status: 'completed',
        completed_at: now.toISOString()
      })
    })
    .eq('id', session.id);
}
```

#### Deployment

**WICHTIG:** Die Edge Function wird automatisch deployed!

```bash
# Manuelles Deployment (falls nötig)
supabase functions deploy harmonization-worker
```

---

## 🎨 Features & Funktionalitäten

### ✅ Implementierte Features

#### 1. Ratengenerator
- ✅ Wort-Energie-Eingabe mit Validierung
- ✅ Manuelle Potenz-Einstellung (6-1000, D/C)
- ✅ Auto-Potenz-Berechnung mit Hardware-Algorithmen
- ✅ **Wortlängen-adaptive Fibonacci-Modulation (optional)**
- ✅ Kozyrev-Spiegel Integration
- ✅ Echtzeit-Rate-Berechnung
- ✅ Live-Vorschau der Berechnungsschritte

#### 2. Auto-Potenz-Projektion
- ✅ Automatische Potenz-Optimierung
- ✅ Patient-spezifische Anpassung
- ✅ Hardware-Metriken-Integration
- ✅ Kozyrev-Verstärkung
- ✅ Adaptive Algorithmen

#### 3. Parallel Harmonisierungs-Sessions
- ✅ Bis zu 10 parallele Sessions
- ✅ Echtzeit-Fortschritts-Tracking
- ✅ Pause/Resume-Funktionalität
- ✅ Pulse/Pause-Modus
- ✅ Session-Archivierung
- ✅ Reaktivierung aus Archiv

#### 4. Datenbank-Analyse
- ✅ CSV/PDF/TXT-Import
- ✅ **Focus-Word Analyse**
- ✅ **Potenz-Nummern zu Worten Konversion**
- ✅ Batch-Harmonisierung
- ✅ Resonanz-Analyse auf 13 Ebenen
- ✅ Sortierung nach Resonanz

#### 5. Harmonisierungs-Archiv
- ✅ Cloud-basierte Speicherung
- ✅ Filter nach Patient/Datum/Status
- ✅ Reaktivierungs-Funktion
- ✅ Lösch-Funktion
- ✅ Detailansicht

#### 6. Worker-Status-Monitoring
- ✅ Echtzeit-Heartbeat-Überwachung
- ✅ Online/Offline-Status
- ✅ Aktive Sessions Counter
- ✅ Letzter Heartbeat Timestamp

#### 7. Patient-Management V2
- ✅ Persönliche Raten
- ✅ Bild-Signatur Integration
- ✅ Ollama llava Analyse
- ✅ Hardware-Konfiguration pro Patient
- ✅ Client-spezifische Rate-Berechnung

#### 8. Kozyrev-Indikatoren
- ✅ Zeitenergie-Feld-Visualisierung
- ✅ Morphogenetisches Feld
- ✅ Torsionsfeld-Resonanz
- ✅ Echtzeit-Updates (100ms)

#### 9. Export-Funktionen
- ✅ **PDF-Export mit deutscher Lokalisierung**
- ✅ **CSV-Export für Datenanalyse**
- ✅ **TXT-Export mit Focus-Word Highlighting**
- ✅ Resonanz-Daten inklusive
- ✅ Zeitstempel und Metadaten

---

## ⚙️ Standard-Werte

### Harmonisierungs-Dauer

```typescript
// Einzelne Harmonisierung
const DEFAULT_HARMONIZATION_DURATION = 300; // 5 Minuten

// Batch-Harmonisierung (Datenbank-Analyse)
const BATCH_HARMONIZATION_DURATION_PER_WORD = 180; // 3 Minuten pro Wort

// Verwendung
const totalDuration = wordCount * BATCH_HARMONIZATION_DURATION_PER_WORD;
```

### Pulse/Pause-Einstellungen

```typescript
// Standard-Werte
const DEFAULT_PULSE_SECONDS = 30;  // 30 Sekunden Pulse
const DEFAULT_PAUSE_SECONDS = 30;  // 30 Sekunden Pause
const DEFAULT_PULSE_PAUSE_ACTIVE = false; // Deaktiviert per Standard

// Verwendung in Code
const [pulseSeconds, setPulseSeconds] = useState(DEFAULT_PULSE_SECONDS);
const [pauseSeconds, setPauseSeconds] = useState(DEFAULT_PAUSE_SECONDS);
const [isPulsePause, setIsPulsePause] = useState(DEFAULT_PULSE_PAUSE_ACTIVE);
```

### Potenz-Standards

```typescript
// Auto-Potenz Standard-Werte
const DEFAULT_POTENCY = 12;
const DEFAULT_POTENCY_TYPE = 'D';

// Verwendung
const [potency, setPotency] = useState(DEFAULT_POTENCY);
const [potencyType, setPotencyType] = useState<'D' | 'C'>(DEFAULT_POTENCY_TYPE);
```

---

## 📤 Export-Funktionen

### PDF-Export

**Features:**
- Deutsche Lokalisierung
- Tabellarische Darstellung
- Focus-Word Highlighting (>>> FOKUS-WORT <<<)
- Resonanz-Daten auf 13 Ebenen
- Zeitstempel und Metadaten
- Professional Layout

**Beispiel-Code:**
```typescript
const exportToPDF = (results: ResonanceResult[], focusWord: string) => {
  const doc = new jsPDF();
  
  // Header
  doc.setFontSize(20);
  doc.text('Bruce Copen Datenbank-Analyse', 14, 20);
  
  // Meta
  doc.setFontSize(12);
  doc.text(`Fokus-Wort: ${focusWord}`, 14, 30);
  doc.text(`Datum: ${new Date().toLocaleDateString('de-DE')}`, 14, 37);
  doc.text(`Patient: ${patient?.first_name} ${patient?.last_name}`, 14, 44);
  
  // Tabelle
  autoTable(doc, {
    startY: 50,
    head: [['Wort', 'Copen-Rate', 'Potenz', 'Höchste Resonanz']],
    body: results.map(r => [
      r.word === focusWord ? `>>> ${r.word} <<<` : r.word,
      r.copenRate,
      r.testedPotency,
      `Ebene ${r.highestResonanceLevel}: ${r.highestResonanceValue.toFixed(2)}`
    ])
  });
  
  doc.save(`Copen_Analyse_${focusWord}_${Date.now()}.pdf`);
};
```

### CSV-Export

**Features:**
- Standard CSV-Format
- Alle Resonanz-Ebenen
- Header-Zeile
- Komma-separiert
- UTF-8 Encoding

**Format:**
```csv
Wort,Copen-Rate,Potenz,Höchste Resonanz,Resonanz-Wert,Ebene 1,Ebene 2,...,Ebene 13
Liebe,16-324,12D,Ebene 12,0.8734,0.23,0.45,...,0.87
Heilung,18-567,30C,Ebene 10,0.9123,0.34,0.56,...,0.78
```

### TXT-Export

**Features:**
- Lesbares Plain-Text-Format
- Focus-Word Highlighting mit >>> <<<
- Vollständige Resonanz-Daten
- Deutsche Beschriftungen
- Zeitstempel

**Format:**
```
BRUCE COPEN DATENBANK-ANALYSE
==================================================

Fokus-Wort: Liebe
Datum: 16.01.2025, 14:30:15
Patient: Max Mustermann
Anzahl Einträge: 150

==================================================

>>> FOKUS-WORT <<<
1. Liebe
   Copen-Rate: 16-324
   Potenz: 12D
   Höchste Resonanz: Ebene 12 (0.8734)
   
   Resonanz-Details:
   Ebene 1 (Physisch - Teilchen): 0.2345
   Ebene 2 (Physisch - Struktur): 0.4567
   ...
   Ebene 13 (Schöpfer): 0.8734
>>> FOKUS-WORT <<<

2. Heilung
   Copen-Rate: 18-567
   Potenz: 30C
   ...
```

---

## 🔄 Worker-System

### Workflow

```
1. SESSION START (Frontend)
   ↓
   INSERT in harmonization_sessions_v2
   status = 'active'
   ↓
   
2. EDGE FUNCTION PROCESSING
   ↓
   WHILE session.status = 'active':
     - Berechne Progress
     - Prüfe Pulse/Pause
     - Update Session
     - Setze Heartbeat
     - Sleep 1s
   ↓
   
3. REALTIME UPDATES
   ↓
   Supabase Realtime Channel
   ↓
   Frontend empfängt Update
   ↓
   UI aktualisiert Fortschritt
   ↓
   
4. BACKEND SYNC (alle 5s)
   ↓
   Frontend fragt Backend ab
   ↓
   Gleicht Daten ab
   ↓
   
5. UI TIMER (alle 100ms)
   ↓
   Interpoliert Fortschritt
   ↓
   Smooth Progress-Bar
   ↓
   
6. COMPLETION
   ↓
   progress = 100
   status = 'completed'
   completed_at = now()
```

### Heartbeat-Mechanismus

```typescript
// Backend (Edge Function)
const updateHeartbeat = async (sessionId: string) => {
  await supabase
    .from('harmonization_sessions_v2')
    .update({ job_last_heartbeat: new Date().toISOString() })
    .eq('id', sessionId);
};

// Frontend (Monitoring)
const checkWorkerStatus = () => {
  const lastHeartbeat = session.job_last_heartbeat;
  const timeSinceHeartbeat = Date.now() - new Date(lastHeartbeat).getTime();
  
  if (timeSinceHeartbeat < 30000) {
    return 'online';
  } else {
    return 'offline';
  }
};
```

---

## 🎨 UI/UX-Spezifikationen

### Farbschema

```css
/* Primärfarben */
--primary: 217 91% 60%;        /* Blau */
--primary-foreground: 0 0% 100%;

/* Sekundärfarben */
--secondary: 217 33% 17%;      /* Dunkelblau */
--secondary-foreground: 0 0% 100%;

/* Akzentfarben */
--accent: 217 91% 60%;
--accent-foreground: 0 0% 100%;

/* Hintergrund */
--background: 222 47% 11%;     /* Dunkel */
--foreground: 213 31% 91%;     /* Hell */

/* Karten */
--card: 217 33% 17%;
--card-foreground: 213 31% 91%;

/* Borders */
--border: 217 33% 27%;

/* Muted */
--muted: 223 47% 11%;
--muted-foreground: 215 20% 65%;

/* Destructive */
--destructive: 0 63% 31%;
--destructive-foreground: 210 40% 98%;
```

### Gradient-Hintergründe

```css
/* Haupt-Gradient */
.bg-gradient-main {
  background: linear-gradient(135deg, 
    hsl(217, 33%, 17%) 0%,
    hsl(217, 91%, 30%) 50%,
    hsl(262, 52%, 47%) 100%
  );
}

/* Seiten-Gradient */
.bg-gradient-page {
  background: linear-gradient(to bottom right,
    #0f172a,  /* slate-900 */
    #1e3a8a,  /* blue-900 */
    #3730a3   /* indigo-900 */
  );
}

/* Karten-Gradient */
.bg-gradient-card {
  background: linear-gradient(135deg,
    rgba(255, 255, 255, 0.05) 0%,
    rgba(255, 255, 255, 0.02) 100%
  );
}
```

### Layout-Struktur

```
┌─────────────────────────────────────────────────┐
│ Navigation Bar (Zurück-Button, User-Menu)      │
├─────────────────────────────────────────────────┤
│ Header (Titel, Beschreibung)                    │
├─────────────────────────────────────────────────┤
│ ┌─────────────────┬─────────────────────────┐  │
│ │ Linke Spalte    │ Rechte Spalte          │  │
│ │                 │                         │  │
│ │ - Patient-      │ - Aktive               │  │
│ │   Auswahl       │   Harmonisierungen     │  │
│ │ - Hardware-     │   (Grid 2x5)           │  │
│ │   Settings      │                         │  │
│ │ - Input-Felder  │ - Session-Controls     │  │
│ │ - Berechnung    │                         │  │
│ │                 │                         │  │
│ └─────────────────┴─────────────────────────┘  │
├─────────────────────────────────────────────────┤
│ Erweiterte Bereiche (collapsible)              │
│ - Berechnungs-Details                           │
│ - Datenbank-Manager                             │
│ - Harmonisierungs-Templates                     │
│ - Archiv                                        │
├─────────────────────────────────────────────────┤
│ Untere Bereiche                                 │
│ - Analyse-Archiv                                │
│ - Session-Status-Liste                          │
│ - Worker-Status-Monitor                         │
└─────────────────────────────────────────────────┘
```

### Responsive Breakpoints

```typescript
// Tailwind Breakpoints
sm: '640px'   // Small devices
md: '768px'   // Medium devices (Tablets)
lg: '1024px'  // Large devices (Desktops)
xl: '1280px'  // Extra large devices
2xl: '1536px' // 2X Extra large devices

// Layout-Anpassungen
< 768px:  Einspaltiges Layout
≥ 768px:  Zweispaltiges Layout
≥ 1024px: Grid-Layout für Harmonisierungen
```

### Animationen

```css
/* Fade-In */
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* Slide-In */
@keyframes slideIn {
  from { 
    transform: translateY(-10px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

/* Progress-Pulse */
@keyframes progressPulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* Verwendung */
.animate-fadeIn {
  animation: fadeIn 0.3s ease-in;
}

.animate-slideIn {
  animation: slideIn 0.3s ease-out;
}

.animate-pulse {
  animation: progressPulse 2s ease-in-out infinite;
}
```

---

## 📁 Code-Referenzen

### Seiten

```
src/pages/
├── CopenVisualizationV2Page.tsx     - Haupt-Visualisierungs-Seite
├── CopenGeneratorPage.tsx           - Legacy Generator-Seite
├── Index.tsx                         - Landing Page
├── AuthPage.tsx                      - Login/Signup
├── FormulasPage.tsx                  - Theorien & Formeln
├── ImportPage.tsx                    - Datenbank-Import
└── NotFound.tsx                      - 404-Seite
```

### Komponenten

```
src/components/
├── CopenAlgorithmVisualizationV2.tsx      - Hauptkomponente (NEU)
├── DatabaseManager.tsx                    - Datenbank-Analyse
├── HardwareAlgorithmSettings.tsx          - Hardware-Config (Global)
├── PatientHardwareConfig.tsx              - Hardware-Config (Patient)
├── PatientManagerCloudV2.tsx              - Patient-Management V2
├── HarmonizationArchiveCloud.tsx          - Harmonisierungs-Archiv
├── HarmonizationTemplates.tsx             - Session-Templates
├── AnalysisArchiveCloud.tsx               - Analyse-Archive
├── KozyrevIndicators.tsx                  - Kozyrev-Visualisierung
├── WorkerStatusMonitor.tsx                - Worker-Überwachung
├── SessionStatusList.tsx                  - Session-Liste
└── UserMenu.tsx                           - Benutzer-Menü
```

### Utilities

```
src/utils/
├── copenRateGenerator.ts            - Raten-Berechnung
├── hardwareAlgorithms.ts            - Hardware-Metriken
├── resonanceAnalysis.ts             - Resonanz-Analyse
├── levelResonance.ts                - 13-Ebenen-Modell
├── alphabetSystems.ts               - Alphabet-Mappings
├── potencyText.ts                   - Potenz-Konversion
├── mentalRatesParser.ts             - Mental-Rates-Parser
├── ocrUtils.ts                      - OCR-Funktionen
└── ollamaClient.ts                  - Ollama-Integration
```

### Types

```
src/types/
└── patient.ts                       - Patient & Session Types
```

### Datenbank

```
src/db/
└── AppDatabase.ts                   - Dexie (IndexedDB)
```

### Supabase

```
src/integrations/supabase/
├── client.ts                        - Supabase-Client
└── types.ts                         - Auto-generated Types

supabase/functions/
└── harmonization-worker/
    └── index.ts                     - Edge Function Worker
```

---

## ✅ Wiederherstellungs-Checkliste

### 1. Komponenten

- [x] CopenVisualizationV2Page
- [x] CopenAlgorithmVisualizationV2
- [x] DatabaseManager mit Focus-Word & Konversion
- [x] HardwareAlgorithmSettings
- [x] PatientHardwareConfig
- [x] PatientManagerCloudV2
- [x] HarmonizationArchiveCloud
- [x] HarmonizationTemplates
- [x] AnalysisArchiveCloud
- [x] KozyrevIndicators
- [x] WorkerStatusMonitor
- [x] SessionStatusList

### 2. Datenbank (Supabase)

- [x] patients_v2 Tabelle
- [x] harmonization_sessions_v2 Tabelle
- [x] analysis_archives_v2 Tabelle
- [x] harmonization_templates_v2 Tabelle
- [x] word_databases Tabelle
- [x] RLS Policies für alle Tabellen
- [x] Indexes für Performance

### 3. Edge Functions

- [x] harmonization-worker deployed
- [x] Heartbeat-Mechanismus
- [x] Pulse/Pause-Logik
- [x] Auto-Completion

### 4. Features

- [x] Ratengenerator mit Auto-Potenz
- [x] **Wortlängen-adaptive Fibonacci (optional)**
- [x] Parallel Harmonisierungen (max 10)
- [x] Datenbank-Analyse mit Focus-Word
- [x] Potenz-zu-Worten Konversion
- [x] Export (PDF/CSV/TXT)
- [x] Patient-Management V2
- [x] Persönliche Raten
- [x] Bild-Signatur
- [x] Hardware-Algorithmen (global & patient)
- [x] Kozyrev-Integration
- [x] Worker-Monitoring

### 5. Standard-Werte

- [x] Harmonisierungs-Dauer: 300s
- [x] Batch-Dauer: 180s pro Wort
- [x] Pulse: 30s
- [x] Pause: 30s
- [x] Standard-Potenz: 12D

### 6. UI/UX

- [x] Gradient-Hintergründe
- [x] Responsive Layout
- [x] Dark Mode
- [x] Animationen
- [x] Progress-Bars
- [x] Toast-Notifications

### 7. Cloud-Synchronisation

- [x] Realtime-Subscription
- [x] Backend-Sync (5s)
- [x] UI-Timer (100ms)
- [x] Heartbeat-Monitoring
- [x] Auto-Archivierung

---

## 📊 Technische Details

### Performance-Metriken

```
Berechnungszeit:
- Einzelne Rate: < 10ms
- Batch (100 Wörter): < 1s
- Hardware-Kalibrierung: 2-5s

Memory-Footprint:
- Komponente: ~2-5 MB
- Aktive Session: ~100 KB
- IndexedDB Cache: ~10-50 MB

Netzwerk-Latenz:
- Supabase Query: 50-200ms
- Realtime-Update: 100-500ms
- Edge Function: 200-800ms
```

### Browser-Kompatibilität

```
✅ Chrome/Edge: 90+
✅ Firefox: 88+
✅ Safari: 14+
⚠️ IE: Nicht unterstützt
```

### Dependencies

```json
{
  "@supabase/supabase-js": "^2.75.1",
  "react": "^18.3.1",
  "react-dom": "^18.3.1",
  "dexie": "^4.2.1",
  "jspdf": "^3.0.3",
  "jspdf-autotable": "^5.0.2",
  "lucide-react": "^0.462.0",
  "tailwindcss": "^3.4.0",
  "typescript": "^5.0.0"
}
```

---

## 📝 Changelog

### Version 2.2 (Aktuell) - 2025-01-16

#### Neue Features
- ✨ **Wortlängen-adaptive Fibonacci-Modulation**
  - Optionaler Toggle im UI
  - Dynamische Fibonacci-Pair-Auswahl (13/21, 21/34, 34/55, 55/89)
  - Basiert auf Wortlänge (1-4, 5-10, 11-20, >20 Zeichen)
  - Parallele Nutzung zum authentischen Copen-Algorithmus möglich

#### Verbesserungen
- 🔧 Hardware-Algorithmen-Dokumentation vervollständigt
- 📚 Komplette Wiederherstellungs-Dokumentation erstellt
- 🎯 Code-Referenzen aktualisiert

---

### Version 2.1 - 2025-01-15

#### Neue Features
- ✨ Focus-Word Analyse in DatabaseManager
- ✨ Potenz-Nummern zu Worten Konversion
- ✨ Erweiterte PDF/CSV/TXT-Exporte
- ✨ Focus-Word Highlighting in Exporten

#### Verbesserungen
- 🔧 Deutsche Lokalisierung aller Exporte
- 📊 Verbesserte Resonanz-Darstellung
- 🎨 UI-Verbesserungen im DatabaseManager

---

### Version 2.0 (Initial V2) - 2025-01-10

#### Neue Features
- ✨ Parallel Harmonisierungen (bis zu 10)
- ✨ Cloud-Synchronisation via Supabase
- ✨ Edge Function Worker
- ✨ Realtime-Updates
- ✨ Patient-Management V2
- ✨ Persönliche Raten
- ✨ Bild-Signatur Integration
- ✨ Hardware-Algorithmen (global & patient)
- ✨ Kozyrev-Integration
- ✨ Worker-Status-Monitoring
- ✨ Harmonisierungs-Archiv
- ✨ Templates-System

#### Verbesserungen
- 🔧 Vollständiges Redesign der Architektur
- 📊 Neue Datenbank-Struktur (_v2 Tabellen)
- 🎨 Modernes UI mit Gradient-Hintergründen
- ⚡ Optimierte Performance

---

## 🆘 Support & Dokumentation

### Verwandte Dokumentation

- `Bruce_Copen_Algorithmus_Dokumentation.md` - Algorithmus-Details
- `Bruce_Copen_Algorithmus_V2_Komplett.md` - V2 Algorithmus
- `Bruce_Copen_Modul_Status_Komplett.md` - Modul-Status
- `Bruce_Copen_Ratengenerator_Komplett.md` - Ratengenerator-Details
- `Hardware_Algorithmen_Dokumentation_Komplett.md` - Hardware-Algorithmen
- `Kozyrev_Zeitenergie_Integration_Empfehlungen.md` - Kozyrev-Details
- `Kompendium_Alle_Frequenztheorien_2025.md` - Frequenz-Theorien

### Support-Kontakt

Bei Problemen oder Fragen:
1. Prüfe diese Dokumentation
2. Überprüfe die Code-Referenzen
3. Konsultiere die verwandte Dokumentation
4. Kontaktiere den Support

---

## 📌 Zusammenfassung

Dieses Dokument stellt einen **kompletten Wiederherstellungspunkt** des Bruce Copen Algorithmus Visualisierung V2 Systems dar.

### Kern-Kapazitäten

✅ **Berechnung:** Präzise Copen-Raten mit authentischem oder adaptivem Algorithmus  
✅ **Hardware-Integration:** Quantum-Computing-Metriken für enhanced Berechnungen  
✅ **Parallelisierung:** Bis zu 10 gleichzeitige Harmonisierungen  
✅ **Cloud-Sync:** Echtzeit-Synchronisation über Supabase  
✅ **Analyse:** 13-Ebenen Resonanz-Analyse mit Focus-Word  
✅ **Export:** Professional PDF/CSV/TXT mit deutscher Lokalisierung  
✅ **Patient-Management:** Erweitert mit persönlichen Raten und Bild-Signaturen  
✅ **Monitoring:** Lückenlose Worker- und Session-Überwachung  

### Status

🟢 **Production Ready**  
🔄 **Aktiv in Entwicklung**  
📈 **Kontinuierliche Verbesserungen**

---

**Ende des Wiederherstellungspunkts**

*Dokumentation erstellt: 2025-01-16*  
*Version: 2.2*  
*Autor: System*