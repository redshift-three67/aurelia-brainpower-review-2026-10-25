# Bruce Copen Algorithmus V2 - Vollständige Wiederherstellungsdokumentation

## 1. ÜBERSICHT

Diese Dokumentation ermöglicht eine **1:1 Rekonstruktion** des "Bruce Copen Algorithmus V2" Views mit allen Komponenten:
- **Hauptseite**: CopenVisualizationV2Page
- **Visualisierung**: CopenAlgorithmVisualizationV2
- **Datenbankmanager**: DatabaseManager
- **Patientenverwaltung**: PatientManagerCloudV2
- **Harmonisierungsarchiv**: HarmonizationArchiveCloud
- **Harmonisierungsvorlagen**: HarmonizationTemplates
- **Worker-Monitor**: WorkerStatusMonitor, SessionStatusList
- **Analysearchiv**: AnalysisArchiveCloud
- **Edge Function**: harmonization-worker

---

## 2. DATEISTRUKTUR

```
src/
├── pages/
│   └── CopenVisualizationV2Page.tsx          # Hauptseite
├── components/
│   ├── CopenAlgorithmVisualizationV2.tsx     # Hauptkomponente (~1479 Zeilen)
│   ├── DatabaseManager.tsx                    # Datenbankanalyse (~1593 Zeilen)
│   ├── PatientManagerCloudV2.tsx             # Patientenverwaltung V2 (~664 Zeilen)
│   ├── HarmonizationArchiveCloud.tsx         # Harmonisierungsarchiv (~441 Zeilen)
│   ├── HarmonizationTemplates.tsx            # Vorlagenverwaltung (~378 Zeilen)
│   ├── AnalysisArchiveCloud.tsx              # Analysearchiv (~353 Zeilen)
│   ├── WorkerStatusMonitor.tsx               # System-Monitor (~196 Zeilen)
│   ├── SessionStatusList.tsx                 # Session-Status (~125 Zeilen)
│   ├── KozyrevIndicators.tsx                 # Kozyrev-Anzeigen
│   └── HardwareAlgorithmSettings.tsx         # Hardware-Einstellungen
├── utils/
│   ├── copenRateGenerator.ts                 # Bruce Copen Rate V4 Algorithmus
│   ├── resonanceAnalysis.ts                  # Java-Resonanzanalyse Engine
│   ├── levelResonance.ts                     # 12+1 Ebenen-Modell
│   ├── hardwareAlgorithms.ts                 # Hardware-Metriken (Kozyrev)
│   ├── alphabetSystems.ts                    # Alphabetsysteme
│   ├── potencyText.ts                        # Potenz-Konvertierung
│   └── analysisInterpreter.ts                # LLM-Interpretation
├── hooks/
│   ├── useWordEnergyHistory.ts               # Wortenergie-Historie
│   └── useAuth.ts                            # Authentifizierung
└── types/
    └── patient.ts                            # Patient-Interfaces

supabase/
├── functions/
│   └── harmonization-worker/
│       └── index.ts                          # Edge Function (~203 Zeilen)
└── config.toml                               # Supabase-Konfiguration
```

---

## 3. SUPABASE DATENBANK-SCHEMA

### 3.1 Tabelle: `patients_v2`
```sql
CREATE TABLE public.patients_v2 (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL,
  first_name TEXT NOT NULL,
  last_name TEXT NOT NULL,
  birth_date TEXT NOT NULL,
  birth_place TEXT NOT NULL,
  image_signature TEXT,
  image_signature_active BOOLEAN DEFAULT true,
  hardware_config JSONB,
  personal_rate TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- RLS Policies
ALTER TABLE public.patients_v2 ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own patients v2" 
  ON public.patients_v2 FOR SELECT 
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own patients v2" 
  ON public.patients_v2 FOR INSERT 
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own patients v2" 
  ON public.patients_v2 FOR UPDATE 
  USING (auth.uid() = user_id) 
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete their own patients v2" 
  ON public.patients_v2 FOR DELETE 
  USING (auth.uid() = user_id);

CREATE POLICY "Admins can view all patients v2" 
  ON public.patients_v2 FOR SELECT 
  USING (has_role(auth.uid(), 'admin'::app_role));
```

### 3.2 Tabelle: `harmonization_sessions_v2`
```sql
CREATE TABLE public.harmonization_sessions_v2 (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID,
  patient_id UUID NOT NULL,
  word TEXT NOT NULL,
  copen_rate TEXT,
  tested_potency TEXT,
  duration_seconds INTEGER NOT NULL,
  remaining_seconds INTEGER,
  progress INTEGER DEFAULT 0,
  status TEXT NOT NULL DEFAULT 'pending',
  started_at TIMESTAMPTZ,
  completed_at TIMESTAMPTZ,
  job_started_at TIMESTAMPTZ,
  job_last_heartbeat TIMESTAMPTZ,
  pulse_seconds INTEGER,
  pause_seconds INTEGER,
  pulse_pause_active BOOLEAN DEFAULT false,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Status-Werte: 'pending', 'running', 'paused', 'completed', 'cancelled'

-- RLS Policies (analog zu patients_v2)
ALTER TABLE public.harmonization_sessions_v2 ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own harmonization sessions v2" 
  ON public.harmonization_sessions_v2 FOR SELECT 
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own harmonization sessions v2" 
  ON public.harmonization_sessions_v2 FOR INSERT 
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own harmonization sessions v2" 
  ON public.harmonization_sessions_v2 FOR UPDATE 
  USING (auth.uid() = user_id) 
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete their own harmonization sessions v2" 
  ON public.harmonization_sessions_v2 FOR DELETE 
  USING (auth.uid() = user_id);

CREATE POLICY "Admins can view all harmonization sessions v2" 
  ON public.harmonization_sessions_v2 FOR SELECT 
  USING (has_role(auth.uid(), 'admin'::app_role));
```

### 3.3 Tabelle: `word_databases`
```sql
CREATE TABLE public.word_databases (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL,
  name TEXT NOT NULL,
  entries TEXT[] NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- RLS Policies (analog)
```

### 3.4 Tabelle: `analysis_archives_v2`
```sql
CREATE TABLE public.analysis_archives_v2 (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL,
  patient_id UUID,
  word TEXT NOT NULL,
  copen_rate TEXT NOT NULL,
  tested_potency TEXT,
  database_entries TEXT[],
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
  patient_data JSONB,
  analysis_timestamp TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### 3.5 Tabelle: `harmonization_templates_v2`
```sql
CREATE TABLE public.harmonization_templates_v2 (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL,
  patient_id UUID NOT NULL,
  name TEXT NOT NULL,
  description TEXT,
  sessions JSONB NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

---

## 4. BRUCE COPEN RATE V4 ALGORITHMUS

### 4.1 Kernformel (copenRateGenerator.ts)

```typescript
/**
 * Bruce Copen Klassik V4 Algorithmus
 * 7 Schritte zur Raten-Berechnung
 */

// SCHRITT 1: Normalisierung
const normalize = (word: string): string => {
  return word
    .toUpperCase()
    .replace(/Ä/g, 'AE')
    .replace(/Ö/g, 'OE')
    .replace(/Ü/g, 'UE')
    .replace(/ß/g, 'SS')
    .replace(/\s*[DCLMF]+\d+/g, '')  // Potenzangaben entfernen
    .replace(/[^A-Z0-9]/g, '')        // Nur A-Z und 0-9
    .trim();
};

// SCHRITT 2: Zeichenwerte
const getCharValue = (char: string): number => {
  if (char >= 'A' && char <= 'Z') return char.charCodeAt(0) - 64; // A=1..Z=26
  if (char >= '0' && char <= '9') return parseInt(char, 10);      // 0-9
  return 0;
};

// SCHRITT 3: Positionsgewichtete Primärsumme
const computePrimarySum = (text: string): number => {
  let sum = 0;
  let position = 1;
  for (const char of text) {
    sum += getCharValue(char) * position;
    position++;
  }
  return sum;
};

// SCHRITT 4: Bildsignatur (optional)
// Wenn aktiv: Mittelwert aus Wort- und Signatur-Primärsumme
if (useImageSignature && imageSignature) {
  const imgPrimary = computePrimarySum(normalize(imageSignature));
  primarySum = Math.floor((primarySum + imgPrimary) / 2);
}

// SCHRITT 5: Baserate
const baseRate = primarySum * 1000;

// SCHRITT 6: Fibonacci-Modulation
// FEST (Original Copen):
const fibonacciRate = Math.floor((baseRate / 21) * 34);

// ODER ADAPTIV (wortlängenabhängig):
const getAdaptiveFibonacciPair = (wordLength: number) => {
  if (wordLength <= 0) return { div: 21, mult: 34 };
  if (wordLength >= 1 && wordLength <= 4) return { div: 13, mult: 21 };
  if (wordLength >= 5 && wordLength <= 10) return { div: 21, mult: 34 };
  if (wordLength >= 11 && wordLength <= 20) return { div: 34, mult: 55 };
  return { div: 55, mult: 89 };
};

// SCHRITT 7: Potenz-Bonus
const getPotencyBonus = (fibRate: number, potency: number, type: string): number => {
  switch (type) {
    case 'D':  return Math.floor(fibRate * (potency / 10));  // Dezimal
    case 'C':  return Math.floor(fibRate * (potency / 5));   // Centesimal
    case 'LM': return Math.floor(fibRate * (potency / 2));   // 50-Millesimal
    case 'M':  return Math.floor(fibRate * potency);         // Millennial
    case 'F1': return Math.floor(fibRate * (potency / 6));   // F-Spektrum 1
    case 'F2': return Math.floor(fibRate * (potency / 4));   // F-Spektrum 2
    case 'F3': return Math.floor(fibRate * (potency / 3));   // F-Spektrum 3
    default:   return 0;
  }
};

// FINALE RATE
const finalRate = fibonacciRate + potencyBonus;
```

### 4.2 Berechnungsbeispiel

**Eingabe**: "ARNICA", Potenz D6

```
1. Normalisierung: "ARNICA" → "ARNICA"
2. Zeichenwerte:
   A(1)*1 = 1
   R(18)*2 = 36
   N(14)*3 = 42
   I(9)*4 = 36
   C(3)*5 = 15
   A(1)*6 = 6
   
3. Primärsumme: 1 + 36 + 42 + 36 + 15 + 6 = 136

4. Baserate: 136 * 1000 = 136.000

5. Fibonacci (21/34): floor((136.000 / 21) * 34) = 220.190

6. Potenz-Bonus D6: floor(220.190 * (6 / 10)) = 132.114

7. Finale Rate: 220.190 + 132.114 = 352.304
```

---

## 5. KLIENTEN-RATE BERECHNUNG

```typescript
const calculateClientRate = (patient: CloudPatient): number => {
  // Wenn personalisierte Rate vorhanden (8-12 Stellen)
  if (patient.personal_rate && patient.personal_rate.length >= 8) {
    return parseInt(patient.personal_rate, 10);
  }
  
  // Standard-Berechnung aus Patientendaten
  const clientData = `${patient.first_name} ${patient.last_name} ${patient.birth_date} ${patient.birth_place}`;
  const cleanData = normalizeWordEnergy(clientData);
  
  let sum = 0;
  let position = 1;
  for (const char of cleanData) {
    sum += getCharValue(char) * position;
    position++;
  }
  
  const clientBaseRate = sum * 1000;
  return Math.floor((clientBaseRate / 21) * 34); // Fibonacci 21/34
};
```

---

## 6. RESONANZ-ANALYSE ENGINE (Java-Algorithmus)

### 6.1 Konfiguration

```typescript
interface AnalysisConfig {
  selectionFraction: number;   // 0.1 = 10%
  minSelection: number;        // 1
  maxSelection: number;        // 100
  chargingThreshold: number;   // 100
  maxEntries?: number;         // 35
}

const DEFAULT_ANALYSIS_CONFIG: AnalysisConfig = {
  selectionFraction: 0.1,
  minSelection: 1,
  maxSelection: 100,
  chargingThreshold: 100,
  maxEntries: 35,
};
```

### 6.2 Level-Gewichte (1-12)

```typescript
const LEVEL_WEIGHTS = [
  { level: 1, weight: 15 },  // Physical Particles
  { level: 2, weight: 14 },  // Physical Structure
  { level: 3, weight: 13 },  // Etheric Prana
  { level: 4, weight: 12 },  // Etheric Meridians
  { level: 5, weight: 11 },  // Astral Emotions
  { level: 6, weight: 10 },  // Astral Thoughts
  { level: 7, weight: 9 },   // Mental Time
  { level: 8, weight: 8 },   // Mental Constructs
  { level: 9, weight: 7 },   // Causal Blueprints
  { level: 10, weight: 6 },  // Causal Alchemy
  { level: 11, weight: 3 },  // Atmic Identity
  { level: 12, weight: 2 },  // Atmic Love
];
// TOTAL_WEIGHT = 110
```

### 6.3 Analyse-Pipeline

```typescript
function analyzeRates(rates: Array<{name: string; copenRate: number}>, config: AnalysisConfig): AnalysisResult {
  // 1. SELEKTION (Fisher-Yates Shuffle)
  const selected = selectRates(rates, config);
  
  // 2. ENERGETISCHES LADEN
  const { energies, trials } = chargeRates(selected, config.chargingThreshold);
  
  // 3. POTENZ & LEVEL ZUWEISUNG
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
  
  // 4. SORTIERUNG (absteigend nach energeticValue)
  rateObjects.sort((a, b) => b.energeticValue - a.energeticValue);
  
  // 5. LIMITIERUNG
  return {
    rateObjects: rateObjects.slice(0, config.maxEntries || rateObjects.length),
    numberOfTrials: trials,
  };
}
```

### 6.4 Gewichtete Level-Auswahl

```typescript
function weightedPickLevel(): number {
  const r = Math.random() * TOTAL_WEIGHT; // 0 - 110
  let cumulative = 0;
  
  for (const { level, weight } of LEVEL_WEIGHTS) {
    cumulative += weight;
    if (r < cumulative) return level;
  }
  return 1; // Fallback
}
```

### 6.5 Potenztyp-Ermittlung

```typescript
function assignPotencyAndLevels(rateName: string) {
  const potencyTypes = ['D', 'C', 'LM', 'M', 'F1', 'F2', 'F3'];
  const weights = [30, 25, 20, 15, 5, 3, 2]; // Gewichtet
  
  // Gewichtete Auswahl
  const totalWeight = 100;
  const r = Math.random() * totalWeight;
  let cumulative = 0;
  let selectedType = 'D';
  
  for (let i = 0; i < potencyTypes.length; i++) {
    cumulative += weights[i];
    if (r < cumulative) {
      selectedType = potencyTypes[i];
      break;
    }
  }
  
  // Potenzwert nach Typ
  let potency: number;
  switch (selectedType) {
    case 'D':  potency = Math.floor(Math.random() * 100) + 1; break;
    case 'C':  potency = Math.floor(Math.random() * 200) + 1; break;
    case 'LM': potency = Math.floor(Math.random() * 30) + 1; break;
    case 'M':  potency = Math.floor(Math.pow(10, Math.random() * 8)); break;
    case 'F1': potency = Math.floor(Math.pow(10, 6 + Math.random() * 7)); break;
    case 'F2': potency = Math.floor(Math.pow(10, 8 + Math.random() * 7)); break;
    case 'F3': potency = Math.floor(Math.pow(10, 10 + Math.random() * 6)); break;
  }
  
  // Level-Verteilung (100 Ziehungen)
  const levelDistribution: Record<number, number> = {};
  for (let i = 1; i <= 12; i++) levelDistribution[i] = 0;
  for (let i = 0; i < 100; i++) levelDistribution[weightedPickLevel()]++;
  
  // Dominante Ebene = Maximum
  let dominantLevel = 1;
  let maxCount = 0;
  for (let level = 1; level <= 12; level++) {
    if (levelDistribution[level] > maxCount) {
      maxCount = levelDistribution[level];
      dominantLevel = level;
    }
  }
  
  return { potency, potencyType: selectedType, levelDistribution, dominantLevel };
}
```

---

## 7. 12+1 EBENEN-MODELL

### 7.1 Ebenen-Definition

```typescript
const LEVELS = [
  {
    id: 1,
    name: "Physical Realm - Particles",
    germanName: "Physische Ebene - Partikel",
    description: "Materielle Ebene: Atome, Partikel, Elemente",
    keywords: ["atom", "partikel", "molekül", "dna", "materie"],
    frequencyRange: { min: 1, max: 100000 }
  },
  {
    id: 2,
    name: "Physical Realm - Structure",
    germanName: "Physische Ebene - Struktur",
    description: "Physische Struktur: Gewebe, Organe, Körper",
    keywords: ["körper", "organ", "gewebe", "struktur"],
    frequencyRange: { min: 100000, max: 500000 }
  },
  {
    id: 3,
    name: "Etheric Realm - Prana",
    germanName: "Ätherische Ebene - Prana",
    description: "Lebenskraft-Ebene: Qi, Prana, Atmung",
    keywords: ["prana", "qi", "lebenskraft", "energie"],
    frequencyRange: { min: 500000, max: 1000000 }
  },
  {
    id: 4,
    name: "Etheric Realm - Meridians",
    germanName: "Ätherische Ebene - Meridiane",
    description: "Energiekanäle: Meridiane, Chakren",
    keywords: ["meridian", "chakra", "nadis", "akupunktur"],
    frequencyRange: { min: 1000000, max: 2000000 }
  },
  {
    id: 5,
    name: "Astral Realm - Emotions",
    germanName: "Astrale Ebene - Emotionen",
    description: "Emotionale Ebene: Gefühle",
    keywords: ["emotion", "gefühl", "empfindung"],
    frequencyRange: { min: 2000000, max: 3500000 }
  },
  {
    id: 6,
    name: "Astral Realm - Thought-Forms",
    germanName: "Astrale Ebene - Gedankenformen",
    description: "Gedankenformen: Magnetische Felder",
    keywords: ["gedanke", "thought", "magnetisch"],
    frequencyRange: { min: 3500000, max: 5000000 }
  },
  {
    id: 7,
    name: "Mental Realm - Time",
    germanName: "Mentale Ebene - Zeit",
    description: "Zeitliche Konstrukte: Raum, Form",
    keywords: ["zeit", "time", "raum", "form"],
    frequencyRange: { min: 5000000, max: 7000000 }
  },
  {
    id: 8,
    name: "Mental Realm - Mental Constructs",
    germanName: "Mentale Ebene - Mentale Konstrukte",
    description: "Mentale Konstrukte: Konzepte",
    keywords: ["konzept", "mental", "idee"],
    frequencyRange: { min: 7000000, max: 9000000 }
  },
  {
    id: 9,
    name: "Causal Plane - Blueprints",
    germanName: "Kausale Ebene - Blaupausen",
    description: "Akasha-Chronik: Destiny Scripts",
    keywords: ["akasha", "blueprint", "destiny"],
    frequencyRange: { min: 9000000, max: 11000000 }
  },
  {
    id: 10,
    name: "Causal Plane - Alchemy",
    germanName: "Kausale Ebene - Alchemie",
    description: "Intention: Alchemische Transformation",
    keywords: ["intention", "alchemie", "transformation"],
    frequencyRange: { min: 11000000, max: 13000000 }
  },
  {
    id: 11,
    name: "Atmic Plane - Identity",
    germanName: "Atmische Ebene - Identität",
    description: "Reine Essenz: Unfragmentierte Identität",
    keywords: ["identität", "essenz", "incarnation"],
    frequencyRange: { min: 13000000, max: 16000000 }
  },
  {
    id: 12,
    name: "Atmic Plane - Love & Unity",
    germanName: "Atmische Ebene - Liebe & Einheit",
    description: "Einheit: Liebe, Archetypal Thinking",
    keywords: ["liebe", "einheit", "love", "unity"],
    frequencyRange: { min: 16000000, max: 20000000 }
  },
  {
    id: 13,
    name: "Creator - Divinity",
    germanName: "Schöpfer - Göttlichkeit",
    description: "Göttliche Ebene: Ewigkeit",
    keywords: ["creator", "schöpfer", "göttlich", "divinity"],
    frequencyRange: { min: 20000000, max: Infinity }
  }
];
```

### 7.2 Level-Resonanz-Berechnung

```typescript
function calculateLevelResonance(copenRate: number, word: string): Record<string, number> {
  const resonance: Record<string, number> = {};
  const normalizedWord = word.toLowerCase();

  LEVELS.forEach(level => {
    let baseResonance = 0;
    const { min, max } = level.frequencyRange;
    
    // 1. Frequenzbasierte Resonanz
    if (max === Infinity) {
      baseResonance = copenRate >= min ? 100 : (copenRate / min) * 50;
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

    // 2. Keyword-Bonus
    let keywordBonus = 0;
    level.keywords.forEach(keyword => {
      if (normalizedWord.includes(keyword)) keywordBonus += 25;
    });

    resonance[`level_${level.id}`] = Math.min(100, baseResonance + keywordBonus);
  });

  return resonance;
}
```

---

## 8. HARDWARE-ALGORITHMEN (Kozyrev-Theorie)

### 8.1 Metriken

```typescript
interface HardwareMetrics {
  cpuQuantumJitter: number;      // +2-3% Akkuranz
  ramEntropy: number;            // +1-2% Akkuranz
  timeSourceCoherence: number;   // +3-4% Akkuranz (Kozyrev: Zeit = Energie)
  gpuRenderingEntropy: number;   // +2-3% Akkuranz
  networkLatency: number;        // +1-2% Akkuranz
  combinedScore: number;         // +3-5% Akkuranz (gewichtet)
}

interface HardwareConfig {
  cpuQuantumJitter: 'auto' | 'on' | 'off';
  ramEntropy: 'auto' | 'on' | 'off';
  timeSourceCoherence: 'auto' | 'on' | 'off';
  gpuRenderingEntropy: 'auto' | 'on' | 'off';
  networkLatency: 'auto' | 'on' | 'off';
  combinedAlgorithm: 'auto' | 'on' | 'off';
}
```

### 8.2 Gewichtung (Combined Score)

```typescript
const weights = {
  timeSourceCoherence: 0.30,   // Höchste Priorität
  cpuQuantumJitter: 0.25,
  gpuRenderingEntropy: 0.20,
  ramEntropy: 0.15,
  networkLatency: 0.10
};

const combinedScore = (
  metrics.timeSourceCoherence * 0.30 +
  metrics.cpuQuantumJitter * 0.25 +
  metrics.gpuRenderingEntropy * 0.20 +
  metrics.ramEntropy * 0.15 +
  metrics.networkLatency * 0.10
);
```

---

## 9. EDGE FUNCTION: harmonization-worker

### 9.1 Vollständiger Code

```typescript
import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
};

serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response(null, { headers: corsHeaders });
  }

  const supabaseUrl = Deno.env.get('SUPABASE_URL')!;
  const supabaseKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!;
  const supabase = createClient(supabaseUrl, supabaseKey);

  // 1. PENDING → RUNNING
  const { data: pendingSessions } = await supabase
    .from('harmonization_sessions_v2')
    .select('*')
    .eq('status', 'pending')
    .is('job_started_at', null)
    .limit(25);

  for (const session of pendingSessions || []) {
    const now = new Date().toISOString();
    await supabase
      .from('harmonization_sessions_v2')
      .update({
        status: 'running',
        job_started_at: now,
        job_last_heartbeat: now,
        remaining_seconds: session.duration_seconds,
        started_at: now,
        progress: 0,
      })
      .eq('id', session.id);
  }

  // 2. AKTIVE SESSIONS TICKEN
  const { data: activeSessions } = await supabase
    .from('harmonization_sessions_v2')
    .select('*')
    .eq('status', 'running')
    .limit(100);

  for (const session of activeSessions || []) {
    const now = new Date();
    const last = session.job_last_heartbeat 
      ? new Date(session.job_last_heartbeat) 
      : new Date(session.started_at);
    
    let elapsed = Math.floor((now.getTime() - last.getTime()) / 1000);
    if (elapsed < 1) elapsed = 1;

    // Impuls/Pausen-Modus
    let effectiveElapsed = elapsed;
    if (session.pulse_pause_active && session.pulse_seconds && session.pause_seconds) {
      const cycleLength = session.pulse_seconds + session.pause_seconds;
      const cycles = Math.floor(elapsed / cycleLength);
      const remainder = elapsed % cycleLength;
      effectiveElapsed = cycles * session.pulse_seconds;
      if (remainder <= session.pulse_seconds) {
        effectiveElapsed += remainder;
      } else {
        effectiveElapsed += session.pulse_seconds;
      }
    }

    const remaining = Math.max(0, (session.remaining_seconds || 0) - effectiveElapsed);
    const progress = Math.min(100, Math.floor(((session.duration_seconds - remaining) / session.duration_seconds) * 100));

    if (remaining <= 0) {
      // ABSCHLUSS
      await supabase
        .from('harmonization_sessions_v2')
        .update({
          status: 'completed',
          remaining_seconds: 0,
          progress: 100,
          completed_at: now.toISOString(),
          job_last_heartbeat: now.toISOString(),
        })
        .eq('id', session.id);
    } else {
      // HEARTBEAT
      await supabase
        .from('harmonization_sessions_v2')
        .update({
          remaining_seconds: remaining,
          progress,
          job_last_heartbeat: now.toISOString(),
        })
        .eq('id', session.id);
    }
  }

  return new Response(JSON.stringify({ success: true }), {
    headers: { ...corsHeaders, 'Content-Type': 'application/json' }
  });
});
```

### 9.2 supabase/config.toml

```toml
project_id = "pybrcpnoryoabuxqtgau"

[functions.harmonization-worker]
verify_jwt = false
```

---

## 10. HAUPTSEITE: CopenVisualizationV2Page.tsx

```tsx
import { Button } from "@/components/ui/button";
import { useNavigate } from "react-router-dom";
import CopenAlgorithmVisualizationV2 from "@/components/CopenAlgorithmVisualizationV2";
import { WorkerStatusMonitor } from "@/components/WorkerStatusMonitor";
import { SessionStatusList } from "@/components/SessionStatusList";
import AnalysisArchiveCloud from "@/components/AnalysisArchiveCloud";

const CopenVisualizationV2Page = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-indigo-900">
      <div className="container mx-auto px-4 py-8">
        <Button 
          variant="outline" 
          onClick={() => navigate("/")}
          className="mb-6 bg-white/10 border-white/20 text-white hover:bg-white/20"
        >
          ← Zurück zur Übersicht
        </Button>
        
        <CopenAlgorithmVisualizationV2 />
        
        <div className="mt-6 space-y-4">
          <AnalysisArchiveCloud />
          <SessionStatusList />
          <WorkerStatusMonitor />
        </div>
      </div>
    </div>
  );
};

export default CopenVisualizationV2Page;
```

---

## 11. INTERFACES & TYPES

### 11.1 Patient-Interface

```typescript
interface CloudPatient {
  id: string;
  user_id: string;
  first_name: string;
  last_name: string;
  birth_date: string;
  birth_place: string;
  image_signature?: string | null;
  image_signature_active?: boolean;
  hardware_config?: HardwareConfig | null;
  personal_rate?: string | null;
  created_at: string;
  updated_at: string;
}
```

### 11.2 Harmonisierung-Interface

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
  remainingSeconds?: number;
}
```

### 11.3 Resonanz-Result

```typescript
interface ResonanceResult {
  word: string;
  potency: number;
  potencyType: 'D' | 'C' | 'LM' | 'M' | 'F1' | 'F2' | 'F3';
  rate: number;
  resonanceScore: number;
  clientResonance: number;
  levelResonance?: Record<string, number>;
  highestLevel?: number;
  highestLevelValue?: number;
}
```

---

## 12. UI-KOMPONENTEN STRUKTUR

### 12.1 CopenAlgorithmVisualizationV2 (Hauptkomponente)

**Enthält:**
1. PatientManagerCloudV2 (Patientenauswahl)
2. HardwareAlgorithmSettings (Globale Schalter)
3. KozyrevIndicators (bei aktiviertem Kozyrev)
4. Wortenergie-Eingabe mit Historie-Dropdown
5. Potenz-Auswahl (D/C/LM/M/F1/F2/F3)
6. Auto-Potenz-Toggle
7. Adaptive Fibonacci-Toggle
8. Live-Preview der Rate
9. Klienten-Rate Anzeige
10. Parallele Harmonisierungen Grid
11. Impuls/Pausen-Modus
12. DatabaseManager (eingebettet)
13. HarmonizationArchiveCloud
14. HarmonizationTemplates

### 12.2 DatabaseManager

**Tabs:**
1. **DB-Analyse**: Import, Fokus-Wort, Analyse, Ergebnistabelle
2. **Direkte Raten**: Manuelle Raten-Eingabe für Harmonisierung

**Ergebnistabelle:**
- Spalten: Checkbox, Wortenergie, Potenz, Copen-Rate, Resonanz, Höchste Ebene, Aktionen
- Spaltenbreiten per Drag resizebar
- Sortierung nach Resonanz/Level/Potenz

---

## 13. REALTIME-SUBSCRIPTIONS

```typescript
// Session-Updates
const channel = supabase
  .channel('harmonization_changes_v2')
  .on(
    'postgres_changes',
    {
      event: '*',
      schema: 'public',
      table: 'harmonization_sessions_v2',
      filter: `patient_id=eq.${patient.id}`
    },
    (payload) => loadActiveHarmonizations()
  )
  .subscribe();

// Cleanup
return () => supabase.removeChannel(channel);
```

---

## 14. LOCAL STORAGE KEYS

```typescript
// Hardware-Algorithmen Global
'hardwareAlgorithms_rateGenerator_enabled_v2'  // boolean
'hardwareAlgorithms_analysis_enabled_v2'       // boolean
```

---

## 15. WIEDERHERSTELLUNGS-CHECKLISTE

### 15.1 Datenbank
- [ ] Tabelle `patients_v2` erstellen
- [ ] Tabelle `harmonization_sessions_v2` erstellen
- [ ] Tabelle `word_databases` erstellen
- [ ] Tabelle `analysis_archives_v2` erstellen
- [ ] Tabelle `harmonization_templates_v2` erstellen
- [ ] RLS Policies für alle Tabellen
- [ ] `has_role()` Funktion erstellen

### 15.2 Edge Function
- [ ] `supabase/functions/harmonization-worker/index.ts`
- [ ] `supabase/config.toml` mit `verify_jwt = false`
- [ ] Deployment der Edge Function

### 15.3 Utils
- [ ] `src/utils/copenRateGenerator.ts`
- [ ] `src/utils/resonanceAnalysis.ts`
- [ ] `src/utils/levelResonance.ts`
- [ ] `src/utils/hardwareAlgorithms.ts`
- [ ] `src/utils/alphabetSystems.ts`
- [ ] `src/utils/potencyText.ts`
- [ ] `src/utils/analysisInterpreter.ts`

### 15.4 Komponenten
- [ ] `src/pages/CopenVisualizationV2Page.tsx`
- [ ] `src/components/CopenAlgorithmVisualizationV2.tsx`
- [ ] `src/components/DatabaseManager.tsx`
- [ ] `src/components/PatientManagerCloudV2.tsx`
- [ ] `src/components/HarmonizationArchiveCloud.tsx`
- [ ] `src/components/HarmonizationTemplates.tsx`
- [ ] `src/components/AnalysisArchiveCloud.tsx`
- [ ] `src/components/WorkerStatusMonitor.tsx`
- [ ] `src/components/SessionStatusList.tsx`
- [ ] `src/components/KozyrevIndicators.tsx`
- [ ] `src/components/HardwareAlgorithmSettings.tsx`

### 15.5 Hooks & Types
- [ ] `src/hooks/useWordEnergyHistory.ts`
- [ ] `src/hooks/useAuth.ts`
- [ ] `src/types/patient.ts`

### 15.6 Routing
- [ ] Route `/copen-visualisierung-v2` in `App.tsx`

### 15.7 Dependencies
```json
{
  "@supabase/supabase-js": "^2.75.1",
  "jspdf": "^3.0.3",
  "jspdf-autotable": "^5.0.2",
  "zod": "^3.23.8"
}
```

---

## 16. DATUMS-INFORMATION

- **Erstellungsdatum**: 2025-12-21
- **Basierend auf**: Bruce Copen Klassik V4 Algorithmus (1978-1995)
- **Erweitert mit**: Kozyrev-Zeitenergie, Hardware-Algorithmen, 12+1 Ebenen-Modell

---

**ENDE DER DOKUMENTATION**
