# Bruce Copen Visualisierung V2 - Komplette Wiederherstellungs-Dokumentation

**Version:** 2.4.0  
**Datum:** 2025-01-16  
**Zweck:** Exakte Wiederherstellung auf anderen Plattformen

---

## Inhaltsverzeichnis

1. [Bruce Copen Algorithmus V2](#1-bruce-copen-algorithmus-v2)
2. [Patientenmanagement V2](#2-patientenmanagement-v2)
3. [Datenbank-Manager](#3-datenbank-manager)
4. [Datenbank-Analyse](#4-datenbank-analyse)
5. [Parallele Harmonisierungen V2](#5-parallele-harmonisierungen-v2)
6. [13-Ebenen Resonanzmodell](#6-13-ebenen-resonanzmodell)
7. [Hardware-Algorithmen (Kozyrev)](#7-hardware-algorithmen-kozyrev)
8. [LLM-Interpretation](#8-llm-interpretation)
9. [Supabase Cloud-Integration](#9-supabase-cloud-integration)
10. [UI/UX Layout-Struktur](#10-uiux-layout-struktur)
11. [Wiederherstellungsanleitung](#11-wiederherstellungsanleitung)

---

## 1. Bruce Copen Algorithmus V2

### 1.1 Datei-Lokation
```
src/components/CopenAlgorithmVisualizationV2.tsx (1479 Zeilen)
```

### 1.2 Kernkonzept
Der Bruce Copen Algorithmus V2 berechnet eine eindeutige "Copen-Rate" basierend auf:
- Wortenergie (Text-Input)
- Potenz und Potenztyp
- Klientendaten (Name, Geburtsdatum, Geburtsort)
- Optionale Fibonacci-Modulation (adaptiv oder fest)

### 1.3 Schritt-für-Schritt Berechnungsalgorithmus

#### Schritt 1: Normalisierung
```typescript
const normalizeWordEnergy = (word: string): string => {
  return word
    .toUpperCase()
    .replace(/Ä/g, 'AE')
    .replace(/Ö/g, 'OE') 
    .replace(/Ü/g, 'UE')
    .replace(/ß/g, 'SS')
    .replace(/\s*[DCLMF]+\d+/g, '') // Entferne Potenz-Suffixe
    .replace(/[^A-Z0-9]/g, '')       // Nur Buchstaben und Zahlen
    .trim();
};
```

#### Schritt 2: Zeichenwert-Berechnung
```typescript
const getCharValue = (char: string): number => {
  if (char >= 'A' && char <= 'Z') {
    return char.charCodeAt(0) - 64; // A=1, B=2, ... Z=26
  }
  if (char >= '0' && char <= '9') {
    return parseInt(char, 10);       // 0-9
  }
  return 0;
};
```

#### Schritt 3: Positionsgewichtete Primärsumme
```typescript
let position = 1;
let primarySum = 0;

for (let i = 0; i < cleanWord.length; i++) {
  const char = cleanWord[i];
  const value = getCharValue(char);
  primarySum += value * position;  // S = Σ(W(ch) × position)
  position++;
}
```

#### Schritt 4: Basisrate
```typescript
const baseRate = primarySum * 1000;  // B = S × 1000
```

#### Schritt 5: Fibonacci-Modulation

**Standard (Authentisch 1978-1995):**
```typescript
const fibonacciRate = Math.floor((baseRate / 21) * 34);
```

**Adaptiv (Wortlängen-basiert):**
```typescript
const getAdaptiveFibonacciPair = (wordLength: number): { div: number; mult: number } => {
  if (wordLength <= 0) return { div: 21, mult: 34 };
  if (wordLength >= 1 && wordLength <= 4) return { div: 13, mult: 21 };
  if (wordLength >= 5 && wordLength <= 10) return { div: 21, mult: 34 };
  if (wordLength >= 11 && wordLength <= 20) return { div: 34, mult: 55 };
  return { div: 55, mult: 89 };
};
```

#### Schritt 6: Potenz-Modifikation
```typescript
const getPotencyModifier = () => {
  switch (effectiveType) {
    case 'D':  return Math.floor(fibonacciRate * (effectivePotency / 10));
    case 'C':  return Math.floor(fibonacciRate * (effectivePotency / 5));
    case 'LM': return Math.floor(fibonacciRate * (effectivePotency / 2));
    case 'M':  return Math.floor(fibonacciRate * effectivePotency);
    case 'F1': return Math.floor(fibonacciRate * (effectivePotency / 6));
    case 'F2': return Math.floor(fibonacciRate * (effectivePotency / 4));
    case 'F3': return Math.floor(fibonacciRate * (effectivePotency / 3));
    default:   return 0;
  }
};
```

#### Schritt 7: Finale Rate
```typescript
const finalRate = fibonacciRate + potencyModifier;  // R = F + P
```

### 1.4 Potenztypen-Spezifikation

| Typ | Name | Bereich | Divisor |
|-----|------|---------|---------|
| D | Dezimal | 1-100 | /10 |
| C | Centesimal | 1-200 | /5 |
| LM | 50-Millesimal | 1-30 | /2 |
| M | Millennial | 1-100.000.000 | ×1 |
| F1 | Frequenz 1 | 30-100 | /6 |
| F2 | Frequenz 2 | 50-100 | /4 |
| F3 | Frequenz 3 | 80-100 | /3 |

### 1.5 Beispielberechnung

**Input:** "NUX VOMICA" mit D6

```
Normalisiert: NUXVOMICA
N(14)×1 = 14
U(21)×2 = 42
X(24)×3 = 72
V(22)×4 = 88
O(15)×5 = 75
M(13)×6 = 78
I(9)×7  = 63
C(3)×8  = 24
A(1)×9  = 9

Primärsumme: 465
Basisrate: 465.000
Fibonacci-Rate: ⌊(465.000 / 21) × 34⌋ = 752.857
Potenz-Bonus: ⌊752.857 × (6/10)⌋ = 451.714
Finale Rate: 752.857 + 451.714 = 1.204.571
```

### 1.6 Klienten-Rate Berechnung

```typescript
const calculateClientRate = () => {
  if (!selectedPatient) return 0;

  // Wenn personalisierte Rate vorhanden (8-12 Stellen)
  if (selectedPatient.personal_rate && selectedPatient.personal_rate.length >= 8) {
    return parseInt(selectedPatient.personal_rate, 10);
  }

  const clientData = `${selectedPatient.first_name} ${selectedPatient.last_name} ${selectedPatient.birth_date} ${selectedPatient.birth_place}`;
  const cleanClientData = normalizeWordEnergy(clientData);
  
  let position = 1;
  let clientSum = 0;
  
  for (let i = 0; i < cleanClientData.length; i++) {
    const char = cleanClientData[i];
    const value = getCharValue(char);
    clientSum += value * position;
    position++;
  }
  
  const clientBaseRate = clientSum * 1000;
  return Math.floor((clientBaseRate / 21) * 34);
};
```

### 1.7 Auto-Potenz Berechnung

Die Auto-Potenz ermittelt automatisch die optimale Potenz und den Potenztyp basierend auf:
- Wortenergie
- Klientendaten (Name, Geburtsdatum, Geburtsort)
- Kozyrev-Modulatoren (falls aktiviert)

```typescript
const calculateAutoPotency = (): { type: PotencyType, potency: number } => {
  if (!selectedPatient) return { type: 'D', potency: 6 };

  const combinedData = `${word} ${selectedPatient.first_name} ${selectedPatient.last_name} ${selectedPatient.birth_date} ${selectedPatient.birth_place}`;
  
  const normalizedData = combinedData
    .toUpperCase()
    .replace(/Ä/g, 'AE').replace(/Ö/g, 'OE').replace(/Ü/g, 'UE').replace(/ß/g, 'SS')
    .replace(/[^A-Z0-9]/g, '');
  
  let sum = 0;
  for (const char of normalizedData) {
    if (char >= 'A' && char <= 'Z') sum += char.charCodeAt(0) - 64;
    else if (char >= '0' && char <= '9') sum += parseInt(char, 10);
  }

  // Kozyrev-Modulatoren
  const birthYear = parseInt(selectedPatient.birth_date.split('-')[0]);
  const age = new Date().getFullYear() - birthYear;
  const ageModulator = kozyrevEnabled ? (1 + (age % 7) / 20) : 1;
  
  const placeEnergy = selectedPatient.birth_place.replace(/[^A-Z]/gi, '').length;
  const placeModulator = kozyrevEnabled ? (1 + (placeEnergy % 10) / 30) : 1;
  
  const modulatedSum = Math.round(sum * ageModulator * placeModulator);

  // Beste Potenz finden über alle Bereiche
  const allRanges = [
    { type: 'D', min: 1, max: 100, divisor: 4 },
    { type: 'C', min: 1, max: 200, divisor: 3 },
    { type: 'LM', min: 1, max: 30, divisor: 12 },
    { type: 'M', min: 1, max: 100, divisor: 6 },
    { type: 'F1', min: 30, max: 100, divisor: 3.5 },
    { type: 'F2', min: 50, max: 100, divisor: 2.5 },
    { type: 'F3', min: 80, max: 100, divisor: 1.8 },
  ];

  let bestMatch = { type: 'D', potency: 1, score: Infinity };
  
  for (const range of allRanges) {
    const calculated = Math.max(range.min, Math.min(range.max, Math.floor(modulatedSum / range.divisor)));
    const score = Math.abs(modulatedSum - calculated * range.divisor);
    
    if (score < bestMatch.score) {
      bestMatch = { type: range.type, potency: calculated, score };
    }
  }
  
  return bestMatch;
};
```

---

## 2. Patientenmanagement V2

### 2.1 Datei-Lokation
```
src/components/PatientManagerCloudV2.tsx (664 Zeilen)
```

### 2.2 Datenstruktur

```typescript
interface Patient {
  id: string;
  user_id: string;
  first_name: string;
  last_name: string;
  birth_date: string;          // Format: YYYY-MM-DD
  birth_place: string;
  image_signature?: string | null;
  image_signature_active?: boolean;
  hardware_config?: HardwareConfig | null;
  personal_rate?: string | null;  // 8-12 stellige personalisierte Rate
  created_at: string;
  updated_at: string;
}
```

### 2.3 Supabase Tabelle: `patients_v2`

```sql
CREATE TABLE public.patients_v2 (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID NOT NULL,
  first_name TEXT NOT NULL,
  last_name TEXT NOT NULL,
  birth_date TEXT NOT NULL,
  birth_place TEXT NOT NULL,
  image_signature TEXT,
  image_signature_active BOOLEAN DEFAULT true,
  hardware_config JSONB,
  personal_rate TEXT,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- RLS Policies
ALTER TABLE public.patients_v2 ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own patients v2" ON public.patients_v2
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own patients v2" ON public.patients_v2
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own patients v2" ON public.patients_v2
  FOR UPDATE USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete their own patients v2" ON public.patients_v2
  FOR DELETE USING (auth.uid() = user_id);
```

### 2.4 Funktionen

| Funktion | Beschreibung |
|----------|--------------|
| `loadPatients()` | Lädt alle Patienten des Users |
| `handleAdd()` | Erstellt neuen Patienten |
| `handleEdit(patient)` | Bearbeitet Patienten |
| `handleUpdate()` | Speichert Änderungen |
| `handleDelete(id)` | Löscht Patienten (DSGVO-konform) |
| `handleImageUpload(e)` | Analysiert Bild mit Ollama llava |

### 2.5 Bildsignatur-Integration

Die Bildsignatur wird via Ollama llava erstellt und optional in Resonanzanalysen verwendet:

```typescript
const handleImageUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
  const file = e.target.files?.[0];
  const result = await analyzeImageWithOllama(file);
  setFormData(prev => ({ ...prev, image_signature: result.signature }));
};
```

### 2.6 Hardware-Konfiguration pro Patient

Jeder Patient kann individuelle Hardware-Algorithmus-Einstellungen haben:

```typescript
interface HardwareConfig {
  cpuQuantumJitter: 'auto' | 'on' | 'off';
  ramEntropy: 'auto' | 'on' | 'off';
  timeSourceCoherence: 'auto' | 'on' | 'off';
  gpuRenderingEntropy: 'auto' | 'on' | 'off';
  networkLatency: 'auto' | 'on' | 'off';
  combinedAlgorithm: 'auto' | 'on' | 'off';
}
```

### 2.7 Personalisierte Rate (personal_rate)

Optionales 8-12 stelliges Feld für individuelle Klienten-Rate:
- Wenn vorhanden und gültig (8-12 Stellen): wird anstelle berechneter Raten verwendet
- Visueller Indikator (Zap-Icon) in der Patientenliste

---

## 3. Datenbank-Manager

### 3.1 Datei-Lokation
```
src/components/DatabaseManager.tsx (1593 Zeilen)
```

### 3.2 Haupt-Tabs

| Tab | Funktion |
|-----|----------|
| **DB-Analyse** | Importiert und analysiert Wortenergie-Datenbanken |
| **Direkte Raten** | Harmonisiert Raten direkt ohne Analyse |

### 3.3 Datenimport-Formate

#### CSV-Format:
```csv
Wortenergie,Potenz,Typ,Alphabet
ARNICA,30,D,latin
NUX VOMICA,6,C,latin
```

#### TXT-Format (eine Zeile = ein Datensatz):
```txt
ARNICA
Chronische Kopfschmerzen
NUX VOMICA D30
```

### 3.4 Import-Parser

```typescript
const parseImportData = (data: string): string[] => {
  const lines = data.trim().split('\n');
  const entries: string[] = [];

  // Erkennt automatisch CSV oder TXT Format
  const looksLikeCsvRecord = (line: string) => {
    const parts = line.split(',').map(p => p.trim());
    if (parts.length < 3) return false;
    const potencyNum = parseInt(parts[1], 10);
    const type = (parts[2] || '').toUpperCase();
    const validType = ['D', 'C', 'LM', 'M'].includes(type);
    return !isNaN(potencyNum) && validType;
  };

  const anyCsv = lines.some(l => looksLikeCsvRecord(l));

  for (const raw of lines) {
    const line = raw.trim();
    if (line.length === 0) continue;

    if (anyCsv) {
      // CSV-Modus: Konvertiere Potenz-Zahlen
      const parts = line.split(',').map(p => p.trim());
      const convertedWord = convertPotencyNumbersToWords(parts[0]);
      parts[0] = convertedWord;
      entries.push(parts.join(','));
    } else {
      // TXT-Modus: Konvertiere Potenz-Zahlen
      const convertedLine = convertPotencyNumbersToWords(line);
      entries.push(convertedLine);
    }
  }

  return [...new Set(entries)]; // Deduplizieren
};
```

### 3.5 Potenz-Wort-Konvertierung

```typescript
// src/utils/potencyText.ts
export function convertPotencyNumbersToWords(text: string): string {
  // D6 → Dsechs, C100 → CEinhundert
  const numberWords: Record<number, string> = {
    1: 'eins', 2: 'zwei', 3: 'drei', 4: 'vier', 5: 'fünf',
    6: 'sechs', 7: 'sieben', 8: 'acht', 9: 'neun', 10: 'zehn',
    // ... weitere Zahlen
    100: 'Einhundert', 200: 'Zweihundert'
  };
  // Implementierung...
}
```

### 3.6 Datenbank-Speicherung

**Supabase Tabelle: `word_databases`**

```sql
CREATE TABLE public.word_databases (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID NOT NULL,
  name TEXT NOT NULL,
  entries TEXT[] NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- RLS Policies
ALTER TABLE public.word_databases ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own databases" ON public.word_databases
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can create their own databases" ON public.word_databases
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own databases" ON public.word_databases
  FOR UPDATE USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete their own databases" ON public.word_databases
  FOR DELETE USING (auth.uid() = user_id);
```

### 3.7 Direkte Raten-Harmonisierung

Ermöglicht das Harmonisieren von Raten ohne vorherige Analyse:

```typescript
const handleDirectRateHarmonization = async () => {
  // Parse Raten (eine pro Zeile)
  const rates = directRatesInput
    .split('\n')
    .map(line => line.trim().replace(/\./g, '').replace(/,/g, ''))
    .filter(line => line.length > 0 && !isNaN(Number(line)))
    .map(line => Number(line));

  const inserts = rates.map(rate => ({
    user_id: user.id,
    patient_id: selectedPatient.id,
    word: `Kohärente Harmonisierung mit ${rate.toLocaleString('de-DE')}`,
    copen_rate: rate.toString(),
    duration_seconds: durationSeconds,
    status: 'pending',
    pulse_seconds: pulseInSeconds,
    pause_seconds: pauseInSeconds,
    pulse_pause_active: pulsePauseActive,
  }));

  await supabase.from('harmonization_sessions_v2').insert(inserts);
};
```

---

## 4. Datenbank-Analyse

### 4.1 Java-Algorithmus Portierung

Die Analyse basiert auf dem originalen Java-Algorithmus mit folgenden Komponenten:

#### Datei-Lokation:
```
src/utils/resonanceAnalysis.ts (321 Zeilen)
```

### 4.2 Analyse-Konfiguration

```typescript
export interface AnalysisConfig {
  selectionFraction: number;  // Standard: 1 (100% für DB-Analyse)
  minSelection: number;       // Minimum: 1
  maxSelection: number;       // Maximum: 10000
  chargingThreshold: number;  // Standard: 100
  maxEntries?: number;        // Standard: 200 für DB-Analyse
}

export const DEFAULT_ANALYSIS_CONFIG: AnalysisConfig = {
  selectionFraction: 0.1,
  minSelection: 1,
  maxSelection: 100,
  chargingThreshold: 100,
  maxEntries: 35,
};
```

### 4.3 Ebenen-Gewichte

```typescript
const LEVEL_WEIGHTS = [
  { level: 1, weight: 15 },   // Physical Particles
  { level: 2, weight: 14 },   // Physical Structure
  { level: 3, weight: 13 },   // Etheric Prana
  { level: 4, weight: 12 },   // Etheric Meridians
  { level: 5, weight: 11 },   // Astral Emotions
  { level: 6, weight: 10 },   // Astral Thoughts
  { level: 7, weight: 9 },    // Mental Time
  { level: 8, weight: 8 },    // Mental Constructs
  { level: 9, weight: 7 },    // Causal Blueprints
  { level: 10, weight: 6 },   // Causal Alchemy
  { level: 11, weight: 3 },   // Atmic Identity
  { level: 12, weight: 2 },   // Atmic Love
];
```

### 4.4 Analyse-Pipeline

```typescript
export function analyzeRates(
  rates: Array<{ name: string; copenRate: number }>,
  config: AnalysisConfig
): AnalysisResult {
  // 1. Selektion (Fisher-Yates Shuffle)
  const selected = selectRates(rates, config);
  
  // 2. Energetisches Laden
  const { energies, trials } = chargeRates(selected, config.chargingThreshold);
  
  // 3. Potenz- und Level-Zuweisung
  const rateObjects = selected.map(rate => {
    const { potency, potencyType, levelDistribution, dominantLevel } = assignPotencyAndLevels(rate.name);
    return {
      rateName: rate.name,
      copenRate: rate.copenRate,
      energeticValue: energies[rate.name],
      potency,
      potencyType,
      levelDistribution,
      dominantLevel,
    };
  });
  
  // 4. Sortieren nach energeticValue
  rateObjects.sort((a, b) => b.energeticValue - a.energeticValue);
  
  // 5. Auf maxEntries begrenzen
  return {
    rateObjects: config.maxEntries ? rateObjects.slice(0, config.maxEntries) : rateObjects,
    numberOfTrials: trials,
  };
}
```

### 4.5 Energetisches Laden

```typescript
function chargeRates(
  selectedRates: Array<{ name: string; copenRate: number }>,
  threshold: number
): { energies: Record<string, number>; trials: number } {
  const energies: Record<string, number> = {};
  selectedRates.forEach(rate => {
    energies[rate.name] = 0;
  });
  
  let trials = 0;
  let maxEnergy = 0;
  
  while (maxEnergy < threshold) {
    selectedRates.forEach(rate => {
      const boost = Math.floor(Math.random() * 10); // 0-9
      energies[rate.name] += boost;
      maxEnergy = Math.max(maxEnergy, energies[rate.name]);
    });
    trials++;
    if (trials > 10000) break;
  }
  
  return { energies, trials };
}
```

### 4.6 Potenz- und Level-Zuweisung

```typescript
function assignPotencyAndLevels(rateName: string): {
  potency: number;
  potencyType: 'D' | 'C' | 'LM' | 'M' | 'F1' | 'F2' | 'F3';
  levelDistribution: Record<number, number>;
  dominantLevel: number;
} {
  // 1. Gewichtete Ebene ermitteln
  const levelValue = weightedPickLevel();
  
  // 2. Potenzreihe gewichtet auswählen
  const potencyTypes = ['D', 'C', 'LM', 'M', 'F1', 'F2', 'F3'];
  const potencyTypeWeights = [30, 25, 20, 15, 5, 3, 2]; // D häufigster
  
  const r = Math.random() * 100;
  let cumulative = 0;
  let selectedPotencyType = 'D';
  
  for (let i = 0; i < potencyTypes.length; i++) {
    cumulative += potencyTypeWeights[i];
    if (r < cumulative) {
      selectedPotencyType = potencyTypes[i];
      break;
    }
  }
  
  // 3. Realistische Potenzwerte generieren
  let actualPotency: number;
  switch (selectedPotencyType) {
    case 'D':  actualPotency = Math.floor(Math.random() * 100) + 1;  break;
    case 'C':  actualPotency = Math.floor(Math.random() * 200) + 1;  break;
    case 'LM': actualPotency = Math.floor(Math.random() * 30) + 1;   break;
    case 'M':  actualPotency = Math.floor(Math.pow(10, Math.random() * 8)); break;
    case 'F1': actualPotency = Math.floor(Math.pow(10, 6 + Math.random() * 7)); break;
    case 'F2': actualPotency = Math.floor(Math.pow(10, 8 + Math.random() * 7)); break;
    case 'F3': actualPotency = Math.floor(Math.pow(10, 10 + Math.random() * 6)); break;
    default:   actualPotency = 1;
  }
  
  // 4. Level-Verteilung: 100 Ziehungen
  const levelDistribution: Record<number, number> = {};
  for (let i = 1; i <= 12; i++) levelDistribution[i] = 0;
  
  for (let i = 0; i < 100; i++) {
    const level = weightedPickLevel();
    levelDistribution[level]++;
  }
  
  // 5. Dominante Ebene = Maximum
  let dominantLevel = 1;
  let maxCount = 0;
  for (let level = 1; level <= 12; level++) {
    if (levelDistribution[level] > maxCount) {
      maxCount = levelDistribution[level];
      dominantLevel = level;
    }
  }
  
  return { potency: actualPotency, potencyType: selectedPotencyType, levelDistribution, dominantLevel };
}
```

### 4.7 Fokus-Wortenergie

Optionale Referenz zur priorisierten Analyse:

```typescript
if (focusWord.trim()) {
  const trimmedFocus = focusWord.trim();
  words = [trimmedFocus, ...words.filter(w => w.toLowerCase() !== trimmedFocus.toLowerCase())];
}
```

### 4.8 Harmonisierungs-Output-Syntax

Nach der Analyse werden selektierte Einträge mit folgender Syntax harmonisiert:
```
Harmonisierung mit {RATE}
```

Beispiel: `Harmonisierung mit 1.549.788.000`

---

## 5. Parallele Harmonisierungen V2

### 5.1 Supabase Tabelle: `harmonization_sessions_v2`

```sql
CREATE TABLE public.harmonization_sessions_v2 (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID,
  patient_id UUID NOT NULL,
  word TEXT NOT NULL,
  copen_rate TEXT,
  tested_potency TEXT,
  status TEXT NOT NULL DEFAULT 'pending',
  duration_seconds INTEGER NOT NULL,
  remaining_seconds INTEGER,
  progress INTEGER DEFAULT 0,
  started_at TIMESTAMP WITH TIME ZONE,
  completed_at TIMESTAMP WITH TIME ZONE,
  job_started_at TIMESTAMP WITH TIME ZONE,
  job_last_heartbeat TIMESTAMP WITH TIME ZONE,
  pulse_seconds INTEGER,
  pause_seconds INTEGER,
  pulse_pause_active BOOLEAN DEFAULT false,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- RLS Policies
ALTER TABLE public.harmonization_sessions_v2 ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own harmonization sessions v2" ON public.harmonization_sessions_v2
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own harmonization sessions v2" ON public.harmonization_sessions_v2
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own harmonization sessions v2" ON public.harmonization_sessions_v2
  FOR UPDATE USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete their own harmonization sessions v2" ON public.harmonization_sessions_v2
  FOR DELETE USING (auth.uid() = user_id);
```

### 5.2 Session-Status

| Status | Beschreibung |
|--------|--------------|
| `pending` | Warten auf Start |
| `running` | Aktiv laufend |
| `paused` | Pausiert |
| `completed` | Abgeschlossen |
| `cancelled` | Abgebrochen |

### 5.3 Impuls/Pausen-Modus

```typescript
interface ActiveHarmonization {
  id: string;
  patientId: string;
  word: string;
  potency: number;
  potencyType: 'D' | 'C' | 'LM' | 'M' | 'F1' | 'F2' | 'F3';
  wordRate: number;
  clientRate: number;
  duration: number;
  durationUnit: 'seconds' | 'minutes' | 'hours' | 'days';
  status: 'running' | 'paused' | 'completed';
  elapsedTime: number;
  progress: number;
  continuous?: boolean;
  pulseSeconds?: number;
  pauseSeconds?: number;
  pulsePauseActive?: boolean;
}
```

### 5.4 Edge Function: harmonization-worker

```typescript
// supabase/functions/harmonization-worker/index.ts
Deno.serve(async (req) => {
  // 1. Holt 'pending' Sessions
  // 2. Startet Sessions (status → 'running')
  // 3. Dekrementiert remaining_seconds
  // 4. Handhabt Impuls/Pausen-Logik
  // 5. Markiert abgeschlossene Sessions
});
```

### 5.5 Backend-Synchronisation

```typescript
// Alle 2 Sekunden Backend-Sync
useEffect(() => {
  const syncTimer = setInterval(async () => {
    const { data: sessions } = await supabase
      .from('harmonization_sessions_v2')
      .select('*')
      .eq('patient_id', selectedPatient.id)
      .in('status', ['running', 'pending']);
    
    // Update lokale State mit Backend-Daten
    setHarmonizations(prev => 
      prev.map(harm => {
        const backendSession = sessions.find(s => s.id === harm.id);
        if (backendSession) {
          const remainingTime = backendSession.remaining_seconds || 0;
          const elapsedTime = backendSession.duration_seconds - remainingTime;
          const progress = (elapsedTime / backendSession.duration_seconds) * 100;
          return { ...harm, elapsedTime, progress, remainingSeconds: remainingTime };
        }
        return harm;
      })
    );
  }, 2000);
  
  return () => clearInterval(syncTimer);
}, [selectedPatient]);
```

### 5.6 Export Aktive Harmonisierungen als DB

```typescript
const exportActiveHarmonizationsToDatabase = async () => {
  if (!selectedPatient) return;

  const { data: sessions } = await supabase
    .from('harmonization_sessions_v2')
    .select('*')
    .eq('user_id', user.id)
    .eq('patient_id', selectedPatient.id)
    .in('status', ['running', 'pending']);

  // Extrahiere Wortenergien/Raten
  const entries = sessions.map(session => {
    const match = session.word.match(/mit\s+([\d.]+)/i);
    return match ? match[1] : session.word;
  });

  // Erstelle Datenbank-Eintrag
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
  const databaseName = `${selectedPatient.first_name}_${selectedPatient.last_name}_Aktive_${timestamp}`;
  
  await supabase.from('word_databases').insert({
    user_id: user.id,
    name: databaseName,
    entries: entries,
  });
};
```

---

## 6. 13-Ebenen Resonanzmodell

### 6.1 Datei-Lokation
```
src/utils/levelResonance.ts (216 Zeilen)
```

### 6.2 Ebenen-Definition

```typescript
export const LEVELS: Level[] = [
  {
    id: 1,
    name: "Physical Realm - Particles",
    germanName: "Physische Ebene - Partikel",
    keywords: ["atom", "partikel", "molekül", "element", "materie", "dna", "struktur"],
    frequencyRange: { min: 1, max: 100000 }
  },
  {
    id: 2,
    name: "Physical Realm - Structure",
    germanName: "Physische Ebene - Struktur",
    keywords: ["körper", "organ", "gewebe", "struktur", "fascia"],
    frequencyRange: { min: 100000, max: 500000 }
  },
  {
    id: 3,
    name: "Etheric Realm - Prana",
    germanName: "Ätherische Ebene - Prana",
    keywords: ["prana", "qi", "lebenskraft", "atmung", "energie"],
    frequencyRange: { min: 500000, max: 1000000 }
  },
  {
    id: 4,
    name: "Etheric Realm - Meridians",
    germanName: "Ätherische Ebene - Meridiane",
    keywords: ["meridian", "chakra", "energiekanal", "nadis", "akupunktur"],
    frequencyRange: { min: 1000000, max: 2000000 }
  },
  {
    id: 5,
    name: "Astral Realm - Emotions",
    germanName: "Astrale Ebene - Emotionen",
    keywords: ["emotion", "gefühl", "empfindung"],
    frequencyRange: { min: 2000000, max: 3500000 }
  },
  {
    id: 6,
    name: "Astral Realm - Thought-Forms",
    germanName: "Astrale Ebene - Gedankenformen",
    keywords: ["gedanke", "thought", "magnetisch", "schwingung"],
    frequencyRange: { min: 3500000, max: 5000000 }
  },
  {
    id: 7,
    name: "Mental Realm - Time",
    germanName: "Mentale Ebene - Zeit",
    keywords: ["zeit", "time", "raum", "space", "form", "farbe"],
    frequencyRange: { min: 5000000, max: 7000000 }
  },
  {
    id: 8,
    name: "Mental Realm - Mental Constructs",
    germanName: "Mentale Ebene - Mentale Konstrukte",
    keywords: ["konzept", "idee", "mental", "konstrukt"],
    frequencyRange: { min: 7000000, max: 9000000 }
  },
  {
    id: 9,
    name: "Causal Plane - Blueprints",
    germanName: "Kausale Ebene - Blaupausen",
    keywords: ["akasha", "blueprint", "blaupause", "destiny"],
    frequencyRange: { min: 9000000, max: 11000000 }
  },
  {
    id: 10,
    name: "Causal Plane - Alchemy",
    germanName: "Kausale Ebene - Alchemie",
    keywords: ["intention", "alchemie", "transformation"],
    frequencyRange: { min: 11000000, max: 13000000 }
  },
  {
    id: 11,
    name: "Atmic Plane - Identity",
    germanName: "Atmische Ebene - Identität",
    keywords: ["identität", "essenz", "incarnation"],
    frequencyRange: { min: 13000000, max: 16000000 }
  },
  {
    id: 12,
    name: "Atmic Plane - Love & Unity",
    germanName: "Atmische Ebene - Liebe & Einheit",
    keywords: ["liebe", "einheit", "love", "unity"],
    frequencyRange: { min: 16000000, max: 20000000 }
  },
  {
    id: 13,
    name: "Creator - Divinity",
    germanName: "Schöpfer - Göttlichkeit",
    keywords: ["creator", "schöpfer", "göttlich", "eternity"],
    frequencyRange: { min: 20000000, max: Infinity }
  }
];
```

### 6.3 Resonanzberechnung

```typescript
export function calculateLevelResonance(
  copenRate: number,
  word: string
): Record<string, number> {
  const resonance: Record<string, number> = {};
  const normalizedWord = word.toLowerCase();

  LEVELS.forEach(level => {
    let baseResonance = 0;
    const { min, max } = level.frequencyRange;

    // 1. Frequenzbasierte Resonanz
    if (max === Infinity) {
      baseResonance = copenRate >= min ? 100 : Math.max(0, (copenRate / min) * 50);
    } else if (copenRate >= min && copenRate <= max) {
      const midpoint = (min + max) / 2;
      const distance = Math.abs(copenRate - midpoint);
      const range = (max - min) / 2;
      baseResonance = Math.max(0, 100 - (distance / range) * 50);
    } else if (copenRate < min) {
      baseResonance = Math.max(0, (copenRate / min) * 40);
    } else {
      const overshoot = (copenRate - max) / max;
      baseResonance = Math.max(0, 30 - overshoot * 30);
    }

    // 2. Keyword-basierte Resonanz (+25 pro Treffer)
    let keywordBonus = 0;
    level.keywords.forEach(keyword => {
      if (normalizedWord.includes(keyword.toLowerCase())) {
        keywordBonus += 25;
      }
    });

    resonance[`level_${level.id}`] = Math.min(100, baseResonance + keywordBonus);
  });

  return resonance;
}
```

---

## 7. Hardware-Algorithmen (Kozyrev)

### 7.1 Datei-Lokation
```
src/utils/hardwareAlgorithms.ts (412 Zeilen)
```

### 7.2 Hardware-Metriken

```typescript
export interface HardwareMetrics {
  cpuQuantumJitter: number;      // 0.0 - 1.0 (+2-3% Akkuranz)
  ramEntropy: number;            // 0.0 - 1.0 (+1-2% Akkuranz)
  timeSourceCoherence: number;   // 0.0 - 1.0 (+3-4% Akkuranz)
  gpuRenderingEntropy: number;   // 0.0 - 1.0 (+2-3% Akkuranz)
  networkLatency: number;        // 0.0 - 1.0 (+1-2% Akkuranz)
  combinedScore: number;         // 0.0 - 1.0 (+3-5% Akkuranz)
}
```

### 7.3 Algorithmus-Implementierungen

#### CPU Quantum Jitter (+2-3%)
```typescript
function getCPUQuantumJitter(): number {
  const samples = 100;
  const timestamps: number[] = [];
  
  for (let i = 0; i < samples; i++) {
    timestamps.push(performance.now());
  }
  
  const diffs = timestamps.slice(1).map((t, i) => t - timestamps[i]);
  const mean = diffs.reduce((a, b) => a + b) / diffs.length;
  const variance = diffs.reduce((sum, d) => sum + (d - mean) ** 2, 0) / diffs.length;
  const stdDev = Math.sqrt(variance);
  
  return Math.min(1.0, stdDev / 0.1);
}
```

#### RAM Entropy (+1-2%)
```typescript
function getRAMEntropy(): number {
  const arrays: Float64Array[] = [];
  const sampleSize = 1000;
  
  for (let i = 0; i < 10; i++) {
    const arr = new Float64Array(sampleSize);
    for (let j = 0; j < sampleSize; j++) arr[j] = Math.random();
    arrays.push(arr);
  }
  
  const startTime = performance.now();
  arrays.forEach(arr => {
    for (let i = 0; i < sampleSize; i += 10) void arr[i];
  });
  const accessTime = performance.now() - startTime;
  
  return Math.min(1.0, accessTime / 10);
}
```

#### Time Source Coherence (+3-4%, Kozyrev-Bezug)
```typescript
function getTimeSourceCoherence(): number {
  const perfTime = performance.now();
  const perfTimeAgain = performance.now();
  const perfDelta = perfTimeAgain - perfTime;
  const drift = Math.abs(perfDelta - perfDelta);
  
  return 1.0 - Math.min(1.0, drift / 1.0);
}
```

#### GPU Rendering Entropy (+2-3%)
```typescript
async function getGPURenderingEntropy(): Promise<number> {
  const canvas = document.createElement('canvas');
  const gl = canvas.getContext('webgl');
  if (!gl) return 0.5;
  
  const vertices = new Float32Array(1000);
  for (let i = 0; i < vertices.length; i++) vertices[i] = Math.random() * 2 - 1;
  
  const times: number[] = [];
  for (let i = 0; i < 10; i++) {
    const start = performance.now();
    gl.drawArrays(gl.TRIANGLES, 0, vertices.length / 2);
    gl.finish();
    times.push(performance.now() - start);
  }
  
  const mean = times.reduce((a, b) => a + b) / times.length;
  const variance = times.reduce((sum, t) => sum + (t - mean) ** 2, 0) / times.length;
  
  canvas.remove();
  return Math.min(1.0, Math.sqrt(variance) / 1.0);
}
```

### 7.4 Combined Score (Gewichtung nach Kozyrev-Relevanz)

```typescript
function calculateCombinedScore(metrics: HardwareMetrics): number {
  const weights = {
    timeSourceCoherence: 0.30,    // Höchste: Zeit = Energie (Kozyrev)
    cpuQuantumJitter: 0.25,       // Quantum-Effekte
    gpuRenderingEntropy: 0.20,    // Morphogenetisches Feld
    ramEntropy: 0.15,             // System-Zustand
    networkLatency: 0.10          // Torsionsfeld
  };
  
  return (
    metrics.timeSourceCoherence * weights.timeSourceCoherence +
    metrics.cpuQuantumJitter * weights.cpuQuantumJitter +
    metrics.gpuRenderingEntropy * weights.gpuRenderingEntropy +
    metrics.ramEntropy * weights.ramEntropy +
    metrics.networkLatency * weights.networkLatency
  );
}
```

### 7.5 Rate-Modulation

```typescript
export function modulateRateWithHardware(
  baseRate: number,
  config: HardwareConfig,
  metrics: HardwareMetrics
): number {
  let modulationFactor = 0;
  
  if (config.combinedAlgorithm === 'on' || config.combinedAlgorithm === 'auto') {
    modulationFactor = metrics.combinedScore * 0.05; // +3-5%
  } else {
    if (config.cpuQuantumJitter === 'on') modulationFactor += metrics.cpuQuantumJitter * 0.03;
    if (config.ramEntropy === 'on') modulationFactor += metrics.ramEntropy * 0.02;
    if (config.timeSourceCoherence === 'on') modulationFactor += metrics.timeSourceCoherence * 0.04;
    if (config.gpuRenderingEntropy === 'on') modulationFactor += metrics.gpuRenderingEntropy * 0.03;
    if (config.networkLatency === 'on') modulationFactor += metrics.networkLatency * 0.02;
  }
  
  return baseRate * (1 + modulationFactor);
}
```

---

## 8. LLM-Interpretation

### 8.1 Datei-Lokation
```
src/utils/analysisInterpreter.ts
```

### 8.2 Hybrid-Ansatz

```typescript
export interface AnalysisInterpretation {
  summary: string;
  insights: string[];
  recommendations: string[];
}

export async function interpretAnalysisResults(
  results: Array<{
    word: string;
    resonanceScore: number;
    highestLevel: number;
    testedPotency: string;
  }>,
  patientName?: string
): Promise<AnalysisInterpretation> {
  // 1. Versuche Ollama LLM
  try {
    const response = await fetch('http://localhost:11434/api/generate', {
      method: 'POST',
      body: JSON.stringify({ model: 'llama2', prompt: buildPrompt(results, patientName) })
    });
    // Parse und return
  } catch {
    // 2. Fallback: Regelbasierter Algorithmus
    return generateRuleBasedInterpretation(results, patientName);
  }
}
```

---

## 9. Supabase Cloud-Integration

### 9.1 Tabellen-Übersicht

| Tabelle | Zweck |
|---------|-------|
| `patients_v2` | Patientendaten |
| `harmonization_sessions_v2` | Aktive und archivierte Sessions |
| `word_databases` | Gespeicherte Wortenergie-Datenbanken |
| `analysis_archives_v2` | Archivierte Analyse-Ergebnisse |
| `harmonization_templates_v2` | Wiederverwendbare Templates |
| `user_roles` | Benutzerrollen (admin/user) |

### 9.2 Realtime-Subscriptions

```typescript
const channel = supabase
  .channel('harmonization_changes_v2')
  .on(
    'postgres_changes',
    {
      event: '*',
      schema: 'public',
      table: 'harmonization_sessions_v2',
      filter: `patient_id=eq.${selectedPatient.id}`,
    },
    (payload) => {
      loadActiveHarmonizations();
    }
  )
  .subscribe();
```

---

## 10. UI/UX Layout-Struktur

### 10.1 Seiten-Hierarchie

```
/copen-visualisierung-v2
├── PatientManagerCloudV2
│   └── Patientenliste mit Edit/Delete/Select
├── HardwareAlgorithmSettings
│   ├── Ratengenerator Toggle
│   └── Analyse Toggle
├── KozyrevIndicators (wenn aktiviert)
├── Bruce Copen Algorithmus V2 Card
│   ├── Wortenergie Input (mit Historie-Dropdown)
│   ├── Potenz Slider (0-200)
│   ├── Potenztyp Selector (D/C/LM/M/F1/F2/F3)
│   ├── Adaptive Fibonacci Toggle
│   ├── Live-Preview (Rate + höchste Ebene)
│   └── Klienten-Rate Anzeige
├── Parallele Harmonisierungen V2 Card
│   ├── Dauer/Einheit Konfiguration
│   ├── Dauerbesendung Toggle
│   ├── Impuls/Pausen-Modus
│   ├── "Als DB speichern" Button
│   └── Aktive Sessions Grid (3 Spalten)
├── DatabaseManager Card
│   ├── Tab: DB-Analyse
│   │   ├── Import Textarea
│   │   ├── Fokus-Wortenergie Input
│   │   ├── Gespeicherte DBs Liste
│   │   ├── Analyse-Button
│   │   ├── Export-Buttons (CSV/TXT/PDF)
│   │   └── Ergebnis-Tabelle (resizable)
│   └── Tab: Direkte Raten
│       ├── Raten Textarea
│       └── Harmonisierung starten
├── AnalysisArchiveCloud
├── SessionStatusList
└── WorkerStatusMonitor
```

### 10.2 Responsive Breakpoints

```css
/* Mobile: 1 Spalte */
@media (max-width: 640px) { grid-template-columns: 1fr; }

/* Tablet: 2 Spalten */
@media (min-width: 641px) and (max-width: 1024px) { grid-template-columns: repeat(2, 1fr); }

/* Desktop: 3 Spalten */
@media (min-width: 1025px) { grid-template-columns: repeat(3, 1fr); }
```

### 10.3 Farbschema

```css
/* Seiten-Hintergrund */
.bg-gradient-to-br from-slate-900 via-blue-900 to-indigo-900

/* Harmonisierung Status */
.bg-green-50.border-green-400   /* Abgeschlossen */
.bg-yellow-50.border-yellow-400 /* Pausiert */
.bg-blue-50.border-blue-400     /* Laufend */

/* Resonanz-Ergebnisse */
.bg-green-50   /* ≥80% Resonanz */
.bg-yellow-50  /* ≥60% Resonanz */
```

---

## 11. Wiederherstellungsanleitung

### 11.1 Voraussetzungen

- Node.js ≥ 18
- npm oder bun
- Supabase-Projekt (Cloud oder Self-hosted)
- Optional: Ollama für LLM-Funktionen (`ollama serve`)

### 11.2 Installation

```bash
# 1. Repository klonen
git clone <repository-url>
cd bruce-copen-visualization

# 2. Abhängigkeiten installieren
npm install

# 3. Umgebungsvariablen konfigurieren
cp .env.example .env
# Bearbeiten:
# VITE_SUPABASE_URL=https://your-project.supabase.co
# VITE_SUPABASE_PUBLISHABLE_KEY=eyJ...

# 4. Entwicklungsserver starten
npm run dev
```

### 11.3 Supabase-Migration

Führen Sie alle SQL-Statements aus Abschnitt 2.3, 3.6, 5.1 und 9.1 aus:

1. `patients_v2` Tabelle + RLS
2. `harmonization_sessions_v2` Tabelle + RLS
3. `word_databases` Tabelle + RLS
4. `analysis_archives_v2` Tabelle + RLS
5. `harmonization_templates_v2` Tabelle + RLS
6. `user_roles` Tabelle + RLS
7. `has_role()` Funktion

### 11.4 Edge Function Deployment

```bash
# harmonization-worker deployen
supabase functions deploy harmonization-worker

# Konfiguration in supabase/config.toml
[functions.harmonization-worker]
verify_jwt = false
```

### 11.5 Verifizierungs-Checkliste

Nach der Installation sollten folgende Funktionen verfügbar sein:

- [ ] Login/Registrierung funktioniert
- [ ] Patientenverwaltung (Anlegen, Bearbeiten, Löschen)
- [ ] Wortenergie-Eingabe mit Live-Preview
- [ ] Potenz-Auswahl (D/C/LM/M/F1/F2/F3)
- [ ] Adaptive Fibonacci Toggle
- [ ] Auto-Potenz Berechnung
- [ ] Klienten-Rate Anzeige
- [ ] Parallele Harmonisierungen starten/pausieren/stoppen
- [ ] Impuls/Pausen-Modus
- [ ] Dauerbesendung
- [ ] Datenbank-Import (CSV/TXT)
- [ ] Resonanzanalyse mit 13 Ebenen
- [ ] LLM-Interpretation (oder Fallback)
- [ ] Export (CSV, TXT, PDF)
- [ ] Hardware-Algorithmen Toggle
- [ ] Realtime-Updates funktionieren
- [ ] Export aktive Harmonisierungen als DB

---

**Dokumentations-Version:** 2.4.0  
**Erstellt:** 2025-01-16  
**Autor:** Bruce Copen Visualization System  
**Komponenten:** CopenAlgorithmVisualizationV2, DatabaseManager, PatientManagerCloudV2, resonanceAnalysis, levelResonance, hardwareAlgorithms
