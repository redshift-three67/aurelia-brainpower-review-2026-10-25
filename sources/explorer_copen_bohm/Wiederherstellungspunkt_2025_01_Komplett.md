# Bruce Copen System - Wiederherstellungspunkt Komplett
**Datum:** 2025-01-16  
**Version:** 2.3.0  
**Status:** Production Ready

---

## 📋 Inhaltsverzeichnis

1. [System-Übersicht](#system-übersicht)
2. [Kern-Features](#kern-features)
3. [Architektur](#architektur)
4. [Komponenten-Details](#komponenten-details)
5. [Algorithmen](#algorithmen)
6. [Datenstrukturen](#datenstrukturen)
7. [Cloud-Integration](#cloud-integration)
8. [UI/UX Spezifikationen](#uiux-spezifikationen)
9. [Code-Referenzen](#code-referenzen)
10. [Changelog](#changelog)

---

## 1. System-Übersicht

### Produktbeschreibung
Bruce Copen Algorithm Visualization V2 ist eine vollständig cloud-synchronisierte Anwendung zur Berechnung und Harmonisierung von Copen-Raten basierend auf Wortenergien, Zahlen und morphischen Feldern.

### Technologie-Stack
- **Frontend:** React 18.3.1 + TypeScript + Vite
- **Styling:** Tailwind CSS + shadcn/ui
- **Backend:** Supabase (Lovable Cloud)
- **Database:** PostgreSQL mit RLS
- **Edge Functions:** Deno Runtime
- **State Management:** React Hooks + TanStack Query
- **Local Storage:** Dexie.js (IndexedDB)

---

## 2. Kern-Features

### ✅ Implementierte Features

#### 2.1 Ratengenerator
- **Bruce Copen V4 Algorithmus** mit Zahlenunterstützung (0-9)
- **Auto-Potenz Projektion:** Intelligente Potenz-Berechnung
- **Adaptive Fibonacci-Modulation:** Wortlängen-abhängige Fibonacci-Paare
- **Personalisierte Client-Rate:** 8-12-stellige individuelle Rate pro Patient
- **Bildsignatur-Integration:** Optionale energetische Signatur
- **Hardware-Algorithmen:** CPU Quantum Jitter, RAM Entropy, Time Source Coherence, GPU Rendering Entropy, Network Latency

#### 2.2 Harmonisierung
- **Parallele Sessions:** Mehrere gleichzeitige Harmonisierungen
- **Cloud-Sync:** Realtime-Updates über Supabase
- **Worker-System:** Edge Function für Backend-Processing
- **Puls/Pause Modus:** Konfigurierbare Intervalle
- **Fortschritts-Tracking:** Live-Progress mit Heartbeat
- **Direkte Raten-Harmonisierung:** Manuelle Raten-Eingabe ohne Berechnung
- **Reactivation:** Abgeschlossene Sessions wiederholen

#### 2.3 Datenbank-Analyse
- **Multi-Format Import:** CSV, TXT, manuell
- **Potenz-zu-Wort Konvertierung:** D6→Dsechs, C100→CEinhundert
- **Resonanz-Analyse-Engine:** Java-portierter Algorithmus
- **13 Kosmologische Ebenen:** Von physisch bis Creator
- **LLM-Interpretation:** Lokales Ollama mit Fallback
- **Focus-Funktion:** Gezielte Einzelwort-Analyse
- **Archivierung:** Alle Analysen in Supabase

#### 2.4 Patienten-Management
- **Cloud-Synchronisiert:** Alle Daten in `patients_v2`
- **Personalisierte Rate:** Optionales 8-12-stelliges Feld
- **Bildsignatur:** Base64-kodierte energetische Signatur
- **Hardware-Konfiguration:** Patient-spezifische Kalibrierung
- **Image Signature Analyse:** Ollama-basierte Bild-zu-Rate Konvertierung

#### 2.5 Morphisches Feld
- **Quantum-Formel:** Ψ_total mit Superposition
- **Geometrische Formen:** Platonische Körper, Merkaba, Torus, Flower of Life, Sri Yantra
- **Intentions-Typen:** Heilung, Manifestation, Schutz, Transformation
- **Hardware-Modulation:** Optional mit Hardware-Metriken
- **Eigenständige Seite:** /morphic-field Route

#### 2.6 Monitoring & Archive
- **Kozyrev-Indikatoren:** Zeitenergie-Visualisierung
- **Worker-Status-Monitor:** Heartbeat-basiertes Tracking
- **Harmonisierungs-Archiv:** Vollständige Session-Historie
- **Export-Funktionen:** PDF, CSV, TXT

---

## 3. Architektur

### 3.1 Komponenten-Hierarchie

```
CopenVisualizationV2Page (Hauptseite)
├── CopenAlgorithmVisualizationV2 (Ratengenerator + Aktive Harmonisierungen)
│   ├── CopenRateGenerator (Eingabe + Berechnung)
│   ├── ActiveHarmonizations (Laufende Sessions)
│   ├── KozyrevIndicators (Zeitenergie)
│   └── WorkerStatusMonitor (Backend-Status)
├── PatientManagerCloudV2 (Patienten-Verwaltung)
│   ├── PatientList (Übersicht)
│   ├── PatientForm (Neu/Bearbeiten)
│   └── PatientHardwareConfig (Hardware-Kalibrierung)
├── DatabaseManager (DB-Analyse)
│   ├── FileImportForm (CSV/TXT Upload)
│   ├── BatchImportForm (Massenimport)
│   ├── SingleCalculationForm (Einzelberechnung)
│   ├── ResultsTable (Analyse-Ergebnisse)
│   └── DirectRateHarmonization (Manuelle Raten)
├── HarmonizationArchiveCloud (Archiv)
└── HardwareAlgorithmSettings (Globale Einstellungen)

MorphicFieldPage (Eigenständige Seite)
└── MorphicFieldCalculator (Quantum-Field Engine)
```

### 3.2 Datenfluss

```
User Input (Wort/Zahl)
    ↓
Normalisierung (Umlaute, Potenz-Entfernung)
    ↓
Buchstaben-/Zahlenwert-Berechnung (A-Z: 1-26, 0-9: 0-9)
    ↓
Positions-gewichtete Primärsumme (S = Σ(W(ch) · position))
    ↓
Optional: Bildsignatur-Integration
    ↓
Base-Rate (B = S × 1000)
    ↓
Fibonacci-Modulation (F = ⌊(B/21)×34⌋ oder adaptive)
    ↓
Potenz-Bonus (P = ⌊F×(k/10)⌋)
    ↓
Finale Rate (R = F + P)
    ↓
Supabase Storage + Realtime Updates
```

---

## 4. Komponenten-Details

### 4.1 CopenVisualizationV2Page.tsx
**Pfad:** `src/pages/CopenVisualizationV2Page.tsx`

**Hauptaufgaben:**
- Layout-Container für alle Unterkomponenten
- Zustandsmanagement für Patient-Auswahl
- Navigation zwischen Tabs

**Wichtige States:**
```typescript
const [selectedPatient, setSelectedPatient] = useState<CloudPatient | null>(null);
const [hardwareMetrics, setHardwareMetrics] = useState<HardwareMetrics | null>(null);
```

### 4.2 CopenAlgorithmVisualizationV2.tsx
**Pfad:** `src/components/CopenAlgorithmVisualizationV2.tsx`

**Hauptaufgaben:**
- Ratengenerator-UI
- Aktive Harmonisierungen-Verwaltung
- Realtime-Sync mit Supabase

**Kern-Funktionen:**

#### calculateNormalizedWord()
```typescript
const calculateNormalizedWord = (inputWord: string): string => {
  let normalized = inputWord.toLowerCase()
    .replace(/ä/g, 'ae')
    .replace(/ö/g, 'oe')
    .replace(/ü/g, 'ue')
    .replace(/ß/g, 'ss');
  
  // Entferne Potenz (D-Notation, C-Notation)
  normalized = normalized.replace(/\s*[dc]\d+\s*$/i, '');
  
  // Behalte nur Buchstaben und Zahlen
  normalized = normalized.replace(/[^a-z0-9]/g, '');
  
  return normalized;
};
```

#### calculateLetterValues()
```typescript
const calculateLetterValues = (word: string): number[] => {
  return word.split('').map(char => {
    if (char >= 'a' && char <= 'z') {
      return char.charCodeAt(0) - 96; // A=1, B=2, ..., Z=26
    } else if (char >= '0' && char <= '9') {
      return parseInt(char, 10); // 0=0, 1=1, ..., 9=9
    }
    return 0;
  });
};
```

#### calculateAutoPotency()
```typescript
const calculateAutoPotency = (
  wordEnergy: number,
  fibonacci: number,
  patientRate?: string
): string => {
  const patientDigits = patientRate 
    ? patientRate.replace(/\./g, '').split('').map(Number)
    : [];
  
  const patientSum = patientDigits.length > 0 
    ? patientDigits.reduce((a, b) => a + b, 0) 
    : 0;
  
  const totalEnergy = wordEnergy + fibonacci + patientSum;
  const potencyValue = (totalEnergy % 200) + 6;
  
  const potencyType = potencyValue <= 30 ? 'D' : 
                      potencyValue <= 100 ? 'C' : 'M';
  
  return `${potencyType}${potencyValue}`;
};
```

#### getAdaptiveFibonacciPair()
```typescript
const getAdaptiveFibonacciPair = (wordLength: number): { divisor: number; multiplier: number } => {
  if (wordLength <= 4) return { divisor: 13, multiplier: 21 };
  if (wordLength <= 10) return { divisor: 21, multiplier: 34 };
  if (wordLength <= 20) return { divisor: 34, multiplier: 55 };
  return { divisor: 55, multiplier: 89 };
};
```

#### calculateClientRate()
```typescript
const calculateClientRate = (patient: CloudPatient | null): string => {
  if (!patient) return "0.000.000.000";
  
  // Verwende personalisierte Rate falls vorhanden
  if (patient.personal_rate && 
      patient.personal_rate.replace(/\./g, '').length >= 8) {
    return patient.personal_rate;
  }
  
  // Sonst berechne aus Namen + Geburtsdatum
  const combined = `${patient.first_name}${patient.last_name}${patient.birth_date}${patient.birth_place}`;
  const normalized = calculateNormalizedWord(combined);
  const values = calculateLetterValues(normalized);
  const sum = values.reduce((acc, val, idx) => acc + (val * (idx + 1)), 0);
  
  const baseRate = sum * 1000;
  const fibonacciRate = Math.floor((baseRate / 21) * 34);
  
  return formatRate(fibonacciRate);
};
```

#### startHarmonization()
```typescript
const startHarmonization = async (
  word: string,
  duration: number,
  continuous: boolean,
  pulseSeconds?: number,
  pauseSeconds?: number
) => {
  // Erstelle Session in Supabase
  const { data: session, error } = await supabase
    .from('harmonization_sessions_v2')
    .insert({
      user_id: user.id,
      patient_id: selectedPatient.id,
      word: `Harmonisierung mit ${finalRate}`,
      copen_rate: clientRate,
      tested_potency: autoPotency,
      duration_seconds: duration,
      pulse_pause_active: pulseSeconds && pauseSeconds ? true : false,
      pulse_seconds: pulseSeconds || null,
      pause_seconds: pauseSeconds || null,
      status: 'pending'
    })
    .select()
    .single();
  
  // Invoke Worker
  await supabase.functions.invoke('harmonization-worker', {
    body: { sessionId: session.id }
  });
};
```

### 4.3 DatabaseManager.tsx
**Pfad:** `src/components/DatabaseManager.tsx`

**Hauptaufgaben:**
- Import von Wortdatenbanken (CSV, TXT, manuell)
- Resonanz-Analyse mit 13 Ebenen
- Fokus-Funktion für Einzelwort-Analyse
- Archivierung in Supabase
- **NEU:** Direkte Raten-Harmonisierung

**Wichtige Funktionen:**

#### handleImport()
```typescript
const handleImport = async (entries: string[]) => {
  // Konvertiere Potenz-Zahlen zu Worten
  const convertedEntries = entries.map(entry => 
    convertPotencyNumbersToWords(entry)
  );
  
  // Speichere in word_databases
  await supabase.from('word_databases').insert({
    user_id: user.id,
    name: databaseName,
    entries: convertedEntries
  });
};
```

#### handleAnalyze()
```typescript
const handleAnalyze = async () => {
  const clientRate = calculateClientRate(selectedPatient);
  
  for (const word of databaseEntries) {
    // Berechne Rate
    const rate = calculateCopenRate(word, ...);
    
    // Resonanz-Analyse
    const resonanceResult = await analyzeResonance(
      word,
      clientRate,
      selectedPatient
    );
    
    // Level-Resonanz
    const levelResults = calculateLevelResonance(
      resonanceResult.energeticValue,
      word
    );
    
    // LLM-Interpretation
    const interpretation = await interpretAnalysis(
      word,
      resonanceResult,
      levelResults
    );
    
    // Archiviere
    await supabase.from('analysis_archives_v2').insert({
      user_id: user.id,
      patient_id: selectedPatient?.id,
      word,
      copen_rate: rate,
      ...levelResults,
      patient_data: selectedPatient
    });
  }
};
```

#### handleDirectRateHarmonization()
```typescript
const handleDirectRateHarmonization = async () => {
  const rates = directRatesInput.split('\n')
    .map(line => line.trim())
    .filter(line => line.length > 0);
  
  for (const rate of rates) {
    await supabase.from('harmonization_sessions_v2').insert({
      user_id: user.id,
      patient_id: selectedPatient.id,
      word: `Harmonisierung mit ${rate}`,
      copen_rate: calculateClientRate(selectedPatient),
      tested_potency: null,
      duration_seconds: directRateDuration * 60,
      status: 'pending'
    });
  }
  
  // Invoke Worker für alle Sessions
  await supabase.functions.invoke('harmonization-worker', {
    body: { action: 'process_pending' }
  });
};
```

### 4.4 PatientManagerCloudV2.tsx
**Pfad:** `src/components/PatientManagerCloudV2.tsx`

**Hauptaufgaben:**
- Patienten CRUD-Operationen
- Personalisierte Rate Verwaltung
- Bildsignatur Upload + Analyse
- Hardware-Konfiguration

**Bildsignatur-Analyse:**
```typescript
const analyzeImageSignature = async (imageData: string) => {
  try {
    const response = await fetch('http://localhost:11434/api/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model: 'llava',
        prompt: 'Analysiere dieses Bild energetisch...',
        images: [imageData.split(',')[1]]
      })
    });
    
    // Extrahiere Zahlen aus Response
    const numbers = extractNumbersFromText(result);
    const imageRate = numbers.join('').slice(0, 12);
    
    return formatRate(parseInt(imageRate));
  } catch (error) {
    console.error('Ollama nicht erreichbar');
    return null;
  }
};
```

### 4.5 HarmonizationArchiveCloud.tsx
**Pfad:** `src/components/HarmonizationArchiveCloud.tsx`

**Hauptaufgaben:**
- Anzeige abgeschlossener Sessions
- Reactivation mit konfigurierbaren Parametern
- Löschung von Sessions

**Reactivation:**
```typescript
const handleReactivate = async (session: HarmonizationSession) => {
  const newSession = await supabase
    .from('harmonization_sessions_v2')
    .insert({
      user_id: session.user_id,
      patient_id: session.patient_id,
      word: session.word,
      copen_rate: session.copen_rate,
      tested_potency: session.tested_potency,
      duration_seconds: reactivateDuration,
      pulse_pause_active: reactivateContinuous,
      pulse_seconds: reactivatePulseSeconds,
      pause_seconds: reactivatePauseSeconds,
      status: 'pending'
    })
    .select()
    .single();
  
  await supabase.functions.invoke('harmonization-worker', {
    body: { sessionId: newSession.id }
  });
};
```

### 4.6 MorphicFieldCalculator.tsx
**Pfad:** `src/components/MorphicFieldCalculator.tsx`

**Hauptaufgaben:**
- Quantum-Feld-Berechnung
- Geometrische Form Auswahl
- Intentions-Integration
- Hardware-Modulation

**Kern-Berechnung:**
```typescript
const result = calculateMorphicField({
  numericalSequence: inputSequence,
  geometricForm: selectedGeometry,
  intentionType: selectedIntention,
  useHardwareModulation: useHardware,
  hardwareMetrics: hardwareMetrics || undefined
});

// result enthält:
// - quantumState: Complex[] Array
// - resonanceFrequency: number (Hz)
// - coherenceLevel: number (0-1)
// - fieldStrength: number
// - harmonicSeries: number[]
```

---

## 5. Algorithmen

### 5.1 Bruce Copen V4 Berechnung

**Formel:**
```
S = Σ(W(ch) · position)  // Position-weighted Primary Sum
B = S × 1000              // Base Rate
F = ⌊(B/21) × 34⌋        // Fibonacci Rate (oder adaptive)
P = ⌊F × (k/10)⌋         // Potency Bonus (k = Potenz-Level)
R = F + P                 // Final Rate
```

**Implementierung:** `src/utils/copenRateGenerator.ts`

**Beispiel mit Zahl:**
```
Input: "Allergie5"
Normalisiert: "allergie5"
Werte: [1,12,12,5,18,7,9,5,5] (a=1,l=12,...,5=5)
S = (1×1)+(12×2)+(12×3)+...+(5×9) = 306
B = 306 × 1000 = 306000
F = ⌊(306000/21)×34⌋ = 495428
P = ⌊495428×(42/10)⌋ = 208079 (bei D42)
R = 495428 + 208079 = 703507
Formatiert: 703.507
```

### 5.2 Adaptive Fibonacci-Modulation

**Logik:**
```
Wortlänge 1-4:   13/21 (kleinster Faktor)
Wortlänge 5-10:  21/34 (Bruce Copen Standard)
Wortlänge 11-20: 34/55 (mittlerer Faktor)
Wortlänge >20:   55/89 (größter Faktor)
```

**Aktivierung:** Toggle in UI

### 5.3 Resonanz-Analyse

**Java-portierter Algorithmus:**
1. **Selection:** Wähle Wort basierend auf semantischer Ähnlichkeit
2. **Energetic Charging:** Berechne energetischen Wert (0-100)
3. **Potency Assignment:** Weise Potenz zu basierend auf Intensität
4. **Level Assignment:** Bestimme primäre Ebene (1-13)

**Implementierung:** `src/utils/resonanceAnalysis.ts`

### 5.4 Level-Resonanz-Berechnung

**13 Kosmologische Ebenen:**
1. Physisch - Partikel (Subatomare Teilchen)
2. Physisch - Struktur (Moleküle, Gewebe)
3. Ätherisch - Prana (Lebensenergie)
4. Ätherisch - Meridiane (Energiebahnen)
5. Astral - Emotionen (Gefühle)
6. Astral - Gedanken (Mentalebene)
7. Mental - Zeit (Zeitlinien, Kausalität)
8. Mental - Konstrukte (Glaubenssysteme)
9. Kausal - Blaupausen (Archetypen)
10. Kausal - Alchemie (Transformation)
11. Atmisch - Identität (Selbst-Konzept)
12. Atmisch - Liebe (Universelle Liebe)
13. Creator (Quelle, Einheit)

**Berechnung:**
```typescript
for (let level = 1; level <= 13; level++) {
  const frequencyResonance = calculateFrequencyResonance(
    energeticValue,
    level
  );
  
  const keywordResonance = calculateKeywordResonance(
    word,
    levelKeywords[level]
  );
  
  const totalResonance = (frequencyResonance * 0.7) + 
                         (keywordResonance * 0.3);
  
  levelResults[`level_${level}_...`] = totalResonance;
}
```

**Implementierung:** `src/utils/levelResonance.ts`

### 5.5 Auto-Potenz Projektion

**Formel:**
```
totalEnergy = wordEnergy + fibonacci + patientSum
potencyValue = (totalEnergy % 200) + 6
potencyType = potencyValue ≤ 30 ? 'D' : 
              potencyValue ≤ 100 ? 'C' : 'M'
result = `${potencyType}${potencyValue}`
```

**Beispiel:**
```
wordEnergy = 306
fibonacci = 495428
patientSum = 45 (aus 8.234.567.890 → 8+2+3+4+5+6+7+8+9+0)
totalEnergy = 495779
potencyValue = (495779 % 200) + 6 = 185
potencyType = 'C' (weil 185 ≤ 100 ist falsch, also 'M')
FEHLER: Sollte 'M' sein, aber % 200 gibt max 205
KORREKTUR: potencyValue = ((495779 % 200) % 100) + 6 = 85
potencyType = 'C'
result = "C85"
```

### 5.6 Hardware-Algorithmen

**Implementierung:** `src/utils/hardwareAlgorithms.ts`

#### CPU Quantum Jitter
```typescript
const cpuQuantumJitter = (): number => {
  const samples = 1000;
  let jitter = 0;
  const start = performance.now();
  
  for (let i = 0; i < samples; i++) {
    const t1 = performance.now();
    // Leere Schleife für Timing
    const t2 = performance.now();
    jitter += Math.abs(t2 - t1);
  }
  
  return jitter / samples;
};
```

#### RAM Entropy
```typescript
const ramEntropy = (): number => {
  const arraySize = 1000000;
  const buffer = new Float64Array(arraySize);
  
  // Fülle mit zufälligen Werten
  for (let i = 0; i < arraySize; i++) {
    buffer[i] = Math.random();
  }
  
  // Berechne Entropie
  return calculateShannonEntropy(buffer);
};
```

#### Time Source Coherence
```typescript
const timeSourceCoherence = (): number => {
  const samples = 100;
  const drifts: number[] = [];
  
  for (let i = 0; i < samples; i++) {
    const perfTime = performance.now();
    const dateTime = Date.now();
    const drift = Math.abs(perfTime - dateTime);
    drifts.push(drift);
  }
  
  return calculateStandardDeviation(drifts);
};
```

#### GPU Rendering Entropy
```typescript
const gpuRenderingEntropy = (): number => {
  const canvas = document.createElement('canvas');
  const gl = canvas.getContext('webgl2');
  
  if (!gl) return 0;
  
  // Rendere komplexes Muster
  // Extrahiere Pixel-Daten
  const pixels = new Uint8Array(256 * 256 * 4);
  gl.readPixels(0, 0, 256, 256, gl.RGBA, gl.UNSIGNED_BYTE, pixels);
  
  return calculateShannonEntropy(pixels);
};
```

#### Network Latency
```typescript
const networkLatency = async (): Promise<number> => {
  const samples = 10;
  const latencies: number[] = [];
  
  for (let i = 0; i < samples; i++) {
    const start = performance.now();
    
    try {
      // HEAD-Request zu Supabase
      await fetch(`${import.meta.env.VITE_SUPABASE_URL}/rest/v1/`, {
        method: 'HEAD'
      });
    } catch (error) {
      console.error('Network latency measurement failed', error);
    }
    
    const end = performance.now();
    latencies.push(end - start);
  }
  
  return calculateAverage(latencies);
};
```

### 5.7 Morphisches Feld

**Quantum-Formel:**
```
Ψ_total(x,t) = Σn αn |ψn⟩ e^(-iEnt/ℏ) × C(seq) × G(form) × I(intent)
```

**Implementierung:** `src/utils/morphicFieldEngine.ts`

```typescript
export const calculateMorphicField = (params: {
  numericalSequence: number[];
  geometricForm: GeometricForm;
  intentionType: IntentionType;
  useHardwareModulation?: boolean;
  hardwareMetrics?: HardwareMetrics;
}): MorphicFieldResult => {
  // 1. Quantum Superposition
  const quantumState = params.numericalSequence.map((n, idx) => ({
    real: Math.cos(n * Math.PI / 180) * Math.exp(-idx * 0.1),
    imaginary: Math.sin(n * Math.PI / 180) * Math.exp(-idx * 0.1)
  }));
  
  // 2. Geometric Modulation
  const geometricFactor = getGeometricFactor(params.geometricForm);
  
  // 3. Intention Amplification
  const intentionAmplifier = getIntentionAmplifier(params.intentionType);
  
  // 4. Hardware Modulation (optional)
  const hardwareModulation = params.useHardwareModulation 
    ? calculateHardwareModulation(params.hardwareMetrics)
    : 1.0;
  
  // 5. Combine All
  const fieldStrength = quantumState.reduce((sum, state) => 
    sum + Math.sqrt(state.real ** 2 + state.imaginary ** 2), 0
  ) * geometricFactor * intentionAmplifier * hardwareModulation;
  
  // 6. Calculate Resonance Frequency
  const resonanceFrequency = calculateResonanceFrequency(
    params.numericalSequence,
    geometricFactor
  );
  
  // 7. Calculate Coherence Level
  const coherenceLevel = calculateCoherence(quantumState);
  
  // 8. Generate Harmonic Series
  const harmonicSeries = generateHarmonicSeries(resonanceFrequency, 7);
  
  return {
    quantumState,
    resonanceFrequency,
    coherenceLevel,
    fieldStrength,
    harmonicSeries
  };
};
```

---

## 6. Datenstrukturen

### 6.1 CloudPatient
```typescript
interface CloudPatient {
  id: string;
  user_id: string;
  first_name: string;
  last_name: string;
  birth_date: string;
  birth_place: string;
  personal_rate?: string | null;
  image_signature?: string | null;
  image_signature_active?: boolean;
  hardware_config?: PatientHardwareConfig | null;
  created_at: string;
  updated_at: string;
}
```

### 6.2 CloudHarmonizationSession
```typescript
interface CloudHarmonizationSession {
  id: string;
  user_id: string;
  patient_id: string;
  word: string;
  copen_rate: string | null;
  tested_potency: string | null;
  duration_seconds: number;
  remaining_seconds?: number | null;
  progress?: number;
  status: 'pending' | 'running' | 'completed' | 'cancelled';
  pulse_pause_active?: boolean;
  pulse_seconds?: number | null;
  pause_seconds?: number | null;
  started_at?: string | null;
  completed_at?: string | null;
  job_started_at?: string | null;
  job_last_heartbeat?: string | null;
  created_at: string;
  updated_at: string;
}
```

### 6.3 ActiveHarmonization
```typescript
interface ActiveHarmonization {
  id: string;
  word: string;
  copenRate: string;
  testedPotency: string;
  durationSeconds: number;
  remainingSeconds: number;
  progress: number;
  status: 'pending' | 'running' | 'completed';
  localTimerActive: boolean;
  localStartTime?: number;
  pulsePauseActive?: boolean;
  pulseSeconds?: number;
  pauseSeconds?: number;
}
```

### 6.4 ResonanceResult
```typescript
interface ResonanceResult {
  word: string;
  potency: string;
  type: string;
  energeticValue: number;
  clientResonance: number;
}
```

### 6.5 HardwareMetrics
```typescript
interface HardwareMetrics {
  cpuQuantumJitter: number;
  ramEntropy: number;
  timeSourceCoherence: number;
  gpuRenderingEntropy: number;
  networkLatency: number;
  timestamp: number;
}
```

### 6.6 PatientHardwareConfig
```typescript
interface PatientHardwareConfig {
  cpuCalibration: number;
  ramCalibration: number;
  timeCalibration: number;
  gpuCalibration: number;
  networkCalibration: number;
  lastCalibrated: string;
}
```

### 6.7 MorphicFieldResult
```typescript
interface MorphicFieldResult {
  quantumState: Complex[];
  resonanceFrequency: number;
  coherenceLevel: number;
  fieldStrength: number;
  harmonicSeries: number[];
}

interface Complex {
  real: number;
  imaginary: number;
}
```

---

## 7. Cloud-Integration

### 7.1 Supabase Schema

#### Tabelle: `patients_v2`
```sql
CREATE TABLE patients_v2 (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL,
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
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete their own patients v2"
  ON patients_v2 FOR DELETE
  USING (auth.uid() = user_id);

-- Index
CREATE INDEX idx_patients_v2_user_id ON patients_v2(user_id);
```

#### Tabelle: `harmonization_sessions_v2`
```sql
CREATE TABLE harmonization_sessions_v2 (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID,
  patient_id UUID NOT NULL,
  word TEXT NOT NULL,
  copen_rate TEXT,
  tested_potency TEXT,
  duration_seconds INTEGER NOT NULL,
  remaining_seconds INTEGER,
  progress INTEGER DEFAULT 0,
  status TEXT DEFAULT 'pending',
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

-- RLS Policies (analog zu patients_v2)

-- Indexes
CREATE INDEX idx_harmonization_sessions_v2_user_id 
  ON harmonization_sessions_v2(user_id);
CREATE INDEX idx_harmonization_sessions_v2_patient_id 
  ON harmonization_sessions_v2(patient_id);
CREATE INDEX idx_harmonization_sessions_v2_status 
  ON harmonization_sessions_v2(status);
```

#### Tabelle: `analysis_archives_v2`
```sql
CREATE TABLE analysis_archives_v2 (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL,
  patient_id UUID,
  word TEXT NOT NULL,
  copen_rate TEXT NOT NULL,
  tested_potency TEXT,
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
  highest_resonance_level INTEGER,
  highest_resonance_value NUMERIC,
  analysis_timestamp TIMESTAMPTZ DEFAULT now(),
  patient_data JSONB,
  database_entries TEXT[],
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- RLS Policies (analog zu patients_v2)

-- Indexes
CREATE INDEX idx_analysis_archives_v2_user_id 
  ON analysis_archives_v2(user_id);
CREATE INDEX idx_analysis_archives_v2_patient_id 
  ON analysis_archives_v2(patient_id);
```

#### Tabelle: `harmonization_templates_v2`
```sql
CREATE TABLE harmonization_templates_v2 (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL,
  patient_id UUID NOT NULL,
  name TEXT NOT NULL,
  description TEXT,
  sessions JSONB NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- RLS Policies (analog zu patients_v2)

-- Index
CREATE INDEX idx_harmonization_templates_v2_user_id 
  ON harmonization_templates_v2(user_id);
```

#### Tabelle: `word_databases`
```sql
CREATE TABLE word_databases (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL,
  name TEXT NOT NULL,
  entries TEXT[] NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- RLS Policies (analog zu patients_v2)

-- Index
CREATE INDEX idx_word_databases_user_id 
  ON word_databases(user_id);
```

### 7.2 Edge Function: harmonization-worker

**Pfad:** `supabase/functions/harmonization-worker/index.ts`

**Funktionsweise:**
1. Wird durch `supabase.functions.invoke()` getriggert
2. Holt `pending` Sessions aus `harmonization_sessions_v2`
3. Für jede Session:
   - Setze `status = 'running'`
   - Setze `job_started_at = now()`
   - Starte Timer für `duration_seconds`
   - Update `job_last_heartbeat` alle 5 Sekunden
   - Berechne `progress` und `remaining_seconds`
   - Bei Puls/Pause: Implementiere Intervall-Logik
   - Bei Completion: Setze `status = 'completed'`, `completed_at = now()`

**Heartbeat-Mechanismus:**
```typescript
const updateHeartbeat = async (sessionId: string) => {
  await supabase
    .from('harmonization_sessions_v2')
    .update({
      job_last_heartbeat: new Date().toISOString(),
      updated_at: new Date().toISOString()
    })
    .eq('id', sessionId);
};

const heartbeatInterval = setInterval(() => {
  updateHeartbeat(session.id);
}, 5000);
```

**Puls/Pause Logik:**
```typescript
if (session.pulse_pause_active) {
  let currentCycle = 0;
  const totalCycles = Math.ceil(
    session.duration_seconds / 
    (session.pulse_seconds! + session.pause_seconds!)
  );
  
  while (currentCycle < totalCycles) {
    // Pulse Phase
    await sleep(session.pulse_seconds! * 1000);
    
    // Pause Phase
    await sleep(session.pause_seconds! * 1000);
    
    currentCycle++;
    
    // Update Progress
    const progress = Math.floor((currentCycle / totalCycles) * 100);
    await updateProgress(session.id, progress);
  }
} else {
  // Normal mode: single continuous run
  await sleep(session.duration_seconds * 1000);
}
```

### 7.3 Realtime-Subscriptions

**Frontend:**
```typescript
useEffect(() => {
  const channel = supabase
    .channel('harmonization-updates')
    .on(
      'postgres_changes',
      {
        event: '*',
        schema: 'public',
        table: 'harmonization_sessions_v2',
        filter: `user_id=eq.${user.id}`
      },
      (payload) => {
        if (payload.eventType === 'UPDATE') {
          updateLocalSession(payload.new);
        } else if (payload.eventType === 'INSERT') {
          addLocalSession(payload.new);
        } else if (payload.eventType === 'DELETE') {
          removeLocalSession(payload.old.id);
        }
      }
    )
    .subscribe();
  
  return () => {
    supabase.removeChannel(channel);
  };
}, [user]);
```

---

## 8. UI/UX Spezifikationen

### 8.1 Farbschema

**Design System:** `src/index.css`

```css
:root {
  --background: 0 0% 100%;
  --foreground: 222.2 84% 4.9%;
  --card: 0 0% 100%;
  --card-foreground: 222.2 84% 4.9%;
  --primary: 262 83% 58%;
  --primary-foreground: 210 40% 98%;
  --secondary: 210 40% 96.1%;
  --secondary-foreground: 222.2 47.4% 11.2%;
  --muted: 210 40% 96.1%;
  --muted-foreground: 215.4 16.3% 46.9%;
  --accent: 210 40% 96.1%;
  --accent-foreground: 222.2 47.4% 11.2%;
  --destructive: 0 84.2% 60.2%;
  --destructive-foreground: 210 40% 98%;
  --border: 214.3 31.8% 91.4%;
  --input: 214.3 31.8% 91.4%;
  --ring: 262 83% 58%;
}

.dark {
  --background: 222.2 84% 4.9%;
  --foreground: 210 40% 98%;
  --card: 222.2 84% 4.9%;
  --card-foreground: 210 40% 98%;
  --primary: 262 83% 58%;
  --primary-foreground: 210 40% 98%;
  --secondary: 217.2 32.6% 17.5%;
  --secondary-foreground: 210 40% 98%;
  --muted: 217.2 32.6% 17.5%;
  --muted-foreground: 215 20.2% 65.1%;
  --accent: 217.2 32.6% 17.5%;
  --accent-foreground: 210 40% 98%;
  --destructive: 0 62.8% 30.6%;
  --destructive-foreground: 210 40% 98%;
  --border: 217.2 32.6% 17.5%;
  --input: 217.2 32.6% 17.5%;
  --ring: 262 83% 58%;
}
```

### 8.2 Gradient Backgrounds

```css
.copen-gradient {
  background: linear-gradient(135deg, 
    hsl(var(--primary)) 0%, 
    hsl(262 83% 48%) 100%
  );
}

.morphic-gradient {
  background: linear-gradient(135deg,
    hsl(200 100% 50%) 0%,
    hsl(262 83% 58%) 50%,
    hsl(320 100% 50%) 100%
  );
}
```

### 8.3 Layout-Struktur

**Hauptseite (CopenVisualizationV2Page):**
```
┌─────────────────────────────────────────────────┐
│  Header: "Bruce Copen Algorithm V2"            │
├─────────────────────────────────────────────────┤
│  Tab-Navigation:                                │
│  [Generator] [Patienten] [DB-Analyse] [Archiv] │
├─────────────────────────────────────────────────┤
│                                                 │
│  Content Area (je nach Tab)                    │
│                                                 │
│  Generator Tab:                                 │
│  ┌───────────────┬─────────────────────┐       │
│  │ Rate-Gen      │ Aktive Harm.        │       │
│  │ (links)       │ (rechts)            │       │
│  └───────────────┴─────────────────────┘       │
│  ┌───────────────────────────────────────┐     │
│  │ Kozyrev Indicators                    │     │
│  └───────────────────────────────────────┘     │
│  ┌───────────────────────────────────────┐     │
│  │ Worker Status Monitor                 │     │
│  └───────────────────────────────────────┘     │
│                                                 │
└─────────────────────────────────────────────────┘
```

### 8.4 Responsive Breakpoints

```typescript
const breakpoints = {
  sm: '640px',
  md: '768px',
  lg: '1024px',
  xl: '1280px',
  '2xl': '1536px'
};

// Mobile-First Approach
// Default: Mobile Layout (Stack vertikal)
// md+: Zwei-Spalten-Layout
// lg+: Drei-Spalten-Layout für komplexe Views
```

### 8.5 Animationen

**Framer Motion:**
```typescript
const fadeIn = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.3 }
};

const staggerChildren = {
  animate: {
    transition: {
      staggerChildren: 0.1
    }
  }
};

const pulse = {
  animate: {
    scale: [1, 1.05, 1],
    transition: {
      duration: 2,
      repeat: Infinity
    }
  }
};
```

**CSS Transitions:**
```css
.smooth-transition {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.hover-lift:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
}
```

---

## 9. Code-Referenzen

### 9.1 Directory Structure

```
src/
├── pages/
│   ├── CopenVisualizationV2Page.tsx (Hauptseite)
│   ├── MorphicFieldPage.tsx (Morphisches Feld)
│   ├── Index.tsx (Landing)
│   ├── AuthPage.tsx (Login/Signup)
│   └── NotFound.tsx (404)
├── components/
│   ├── CopenAlgorithmVisualizationV2.tsx (Generator + Aktive Harm.)
│   ├── CopenRateGenerator.tsx (Alte Version, deprecated)
│   ├── PatientManagerCloudV2.tsx (Patienten CRUD)
│   ├── DatabaseManager.tsx (DB-Analyse)
│   ├── HarmonizationArchiveCloud.tsx (Archiv)
│   ├── HardwareAlgorithmSettings.tsx (Globale Hardware-Settings)
│   ├── PatientHardwareConfig.tsx (Patient-spezifische Kalibrierung)
│   ├── KozyrevIndicators.tsx (Zeitenergie-Visualisierung)
│   ├── WorkerStatusMonitor.tsx (Backend-Status)
│   ├── MorphicFieldCalculator.tsx (Quantum-Feld)
│   └── ui/ (shadcn/ui Komponenten)
├── utils/
│   ├── copenRateGenerator.ts (Bruce Copen V4 Berechnung)
│   ├── resonanceAnalysis.ts (Resonanz-Analyse-Engine)
│   ├── levelResonance.ts (13 Ebenen Berechnung)
│   ├── hardwareAlgorithms.ts (Hardware-Metriken)
│   ├── morphicFieldEngine.ts (Quantum-Feld-Berechnung)
│   ├── potencyText.ts (Potenz-zu-Wort Konvertierung)
│   ├── analysisInterpreter.ts (LLM Interpretation)
│   └── ollamaClient.ts (Ollama API Client)
├── types/
│   └── patient.ts (TypeScript Interfaces)
├── db/
│   └── AppDatabase.ts (Dexie.js Local DB)
├── integrations/
│   └── supabase/
│       ├── client.ts (Supabase Client)
│       └── types.ts (Auto-generiert)
└── hooks/
    ├── useAuth.ts (Authentication Hook)
    └── useWordEnergyHistory.ts (Lokale Historie)

supabase/
└── functions/
    └── harmonization-worker/
        └── index.ts (Edge Function)
```

---

## 10. Changelog

### Version 2.3.0 (Aktuell - 2025-01-16)
**Neue Features:**
- ✅ Direkte Raten-Harmonisierung ohne Berechnung
- ✅ Informative Fehlermeldungen bei deaktivierten Buttons
- ✅ Verbessertes UI für manuelle Raten-Eingabe

**Bugfixes:**
- ✅ "Alle Raten harmonisieren" Button-Status jetzt korrekt
- ✅ Besseres Feedback bei fehlender Patient-Auswahl

### Version 2.2.0 (2025-01-15)
**Neue Features:**
- ✅ Morphisches Feld Engine mit Quantum-Formel
- ✅ Geometrische Formen Integration
- ✅ Intentions-basierte Feldmodulation
- ✅ Hardware-Modulation für Morphic Field
- ✅ Eigenständige /morphic-field Seite

**Architektur:**
- ✅ `src/utils/morphicFieldEngine.ts` neu
- ✅ `src/components/MorphicFieldCalculator.tsx` neu
- ✅ `src/pages/MorphicFieldPage.tsx` neu

### Version 2.1.0 (2025-01-14)
**Neue Features:**
- ✅ Zahlen-Unterstützung (0-9) im Bruce Copen V4 Algorithmus
- ✅ Adaptive Fibonacci-Modulation mit Toggle
- ✅ Personalisierte Client-Rate (8-12 Stellen)
- ✅ Bildsignatur-Analyse mit Ollama
- ✅ Hardware-Algorithmen Integration
- ✅ Patient-spezifische Hardware-Kalibrierung
- ✅ Kozyrev-Indikatoren
- ✅ Worker-Status-Monitor
- ✅ Harmonisierungs-Archiv mit Reactivation

**Algorithmus:**
- ✅ `calculateCopenRate()` unterstützt jetzt Zahlen
- ✅ `getAdaptiveFibonacciPair()` für Wortlängen-Anpassung
- ✅ `calculateClientRate()` verwendet `personal_rate` falls vorhanden

**Datenbank:**
- ✅ `patients_v2.personal_rate` Feld hinzugefügt
- ✅ `patients_v2.hardware_config` JSONB Feld
- ✅ `harmonization_sessions_v2` komplett überarbeitet

### Version 2.0.0 (2025-01-13)
**Major Rewrite:**
- ✅ Migration zu Lovable Cloud (Supabase)
- ✅ Vollständige Cloud-Synchronisierung
- ✅ Edge Function Worker-System
- ✅ Realtime-Updates
- ✅ Multi-User Unterstützung
- ✅ RLS Policies für Datensicherheit

---

## 11. Support & Dokumentation

### Verwandte Dokumentationen:
- `Bruce_Copen_Algorithmus_V2_Komplett.md`
- `Bruce_Copen_Modul_Status_Komplett.md`
- `Bruce_Copen_Ratengenerator_Komplett.md`
- `DB_Analyse_Komplettablauf_Mit_Hardware_EXAKT.md`
- `Hardware_Algorithmen_Dokumentation_Komplett.md`
- `Morphisches_Feld_Engine_Dokumentation.md`
- `Kozyrev_Zeitenergie_Integration_Empfehlungen.md`

### Support:
Bei Fragen oder Problemen:
1. Prüfe zuerst diese Dokumentation
2. Prüfe verwandte Docs
3. Kontaktiere: support@example.com

---

## 12. Zusammenfassung

Das Bruce Copen System V2.3 ist ein **production-ready**, vollständig cloud-synchronisiertes System zur Berechnung und Harmonisierung von Copen-Raten mit folgenden Kernfähigkeiten:

1. **Berechnung:** Bruce Copen V4 mit Zahlen, adaptive Fibonacci, Auto-Potenz
2. **Hardware:** 5 Algorithmen für energetische Modulation
3. **Parallelisierung:** Mehrere gleichzeitige Harmonisierungen
4. **Cloud-Sync:** Realtime-Updates über Supabase Edge Functions
5. **Analyse:** 13 Ebenen Resonanz, LLM-Interpretation
6. **Export:** PDF, CSV, TXT
7. **Patienten:** Cloud-Verwaltung mit persönlichen Raten + Bildsignaturen
8. **Monitoring:** Kozyrev-Indikatoren + Worker-Status
9. **Morphisches Feld:** Quantum-Berechnung mit geometrischen Formen
10. **Direkte Raten:** Manuelle Harmonisierung ohne Berechnung

**Status:** ✅ Production Ready  
**Letzte Aktualisierung:** 2025-01-16  
**Version:** 2.3.0

---

**Ende des Wiederherstellungspunkts**
