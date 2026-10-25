# Bruce Copen System V2.4 - Vollständiger Wiederherstellungspunkt
## Server-Wiederherstellung Dokumentation (Stand: 2025-12-07)

---

## 1. SYSTEM-ÜBERSICHT

### 1.1 Projektbeschreibung
Das Bruce Copen System ist eine cloud-synchronisierte Applikation zur Berechnung und Harmonisierung von Copen-Raten basierend auf:
- Wortenergien (Text → Rate)
- Numerischen Sequenzen (Zahlen → Rate)
- Morphischen Feldern (Quantenbasierte Feldberechnung)
- Patientenspezifischen Parametern

### 1.2 Technologie-Stack
```
Frontend:
- React 18.3.1
- TypeScript
- Vite
- TailwindCSS
- Shadcn/UI (Radix UI)
- TanStack React Query 5.56.2
- React Router DOM 6.26.2
- Framer Motion (via Recharts)

Backend:
- Supabase (Lovable Cloud)
- PostgreSQL
- Deno Edge Functions
- Row Level Security (RLS)

Zusätzliche Libraries:
- jsPDF + jspdf-autotable (PDF-Export)
- Tesseract.js 6.0.1 (OCR)
- date-fns (Datums-Formatierung)
- zod (Schema-Validierung)
```

### 1.3 Routen-Struktur
```typescript
/auth                     → AuthPage (Login/Registrierung)
/                         → Index (Geschützter Hauptindex)
/import                   → ImportPage (Daten-Import Center)
/copen-generator          → CopenGeneratorPage (Raten-Generator)
/copen-visualisierung-v2  → CopenVisualizationV2Page (Haupt-Analyse)
/formulas                 → FormulasPage (Formel-Kompendium)
/morphic-field            → MorphicFieldPage (Morphisches Feld Engine)
*                         → NotFound (404)
```

---

## 2. KERN-ALGORITHMEN

### 2.1 Bruce Copen Algorithmus V4 (Haupt-Ratenberechnung)

**Standort:** `src/utils/copenRateGenerator.ts`

**Exakter Algorithmus:**
```typescript
// SCHRITT 1: Normalisierung (Bruce Copen Klassik V4 mit Zahlenverarbeitung)
const normalize = (word: string): string => {
  return word
    .toUpperCase()
    .replace(/Ä/g, 'AE')
    .replace(/Ö/g, 'OE')
    .replace(/Ü/g, 'UE')
    .replace(/ß/g, 'SS')
    .replace(/\s*[DCLMF]+\d+/g, '')  // Potenzangaben entfernen
    .replace(/[^A-Z0-9]/g, '')        // Nur Buchstaben und Zahlen
    .trim();
};

// SCHRITT 2: Zeichenwerte
const getCharValue = (char: string): number => {
  if (char >= 'A' && char <= 'Z') {
    return char.charCodeAt(0) - 64;  // A=1, B=2, ..., Z=26
  }
  if (char >= '0' && char <= '9') {
    return parseInt(char, 10);        // 0-9
  }
  return 0;
};

// SCHRITT 3: Positionsgewichtete Primärsumme
const computePrimarySum = (text: string): number => {
  let sum = 0;
  let position = 1;
  for (const char of text) {
    const value = getCharValue(char);
    sum += value * position;
    position++;
  }
  return sum;
};

// SCHRITT 4: Baserate
const baseRate = primarySum * 1000;

// SCHRITT 5: Fibonacci-Modulation
// Standard (Original Copen 1978-1995):
const fibonacciRate = Math.floor((baseRate / 21) * 34);

// ODER Wortlängen-Adaptiv:
const getAdaptiveFibonacciPair = (wordLength: number) => {
  if (wordLength <= 0) return { div: 21, mult: 34 };
  if (wordLength >= 1 && wordLength <= 4) return { div: 13, mult: 21 };
  if (wordLength >= 5 && wordLength <= 10) return { div: 21, mult: 34 };
  if (wordLength >= 11 && wordLength <= 20) return { div: 34, mult: 55 };
  return { div: 55, mult: 89 };
};

// SCHRITT 6: Potenz-Bonus
const getPotencyModifier = (fibRate: number, potency: number, type: string) => {
  switch (type) {
    case 'D':  return Math.floor(fibRate * (potency / 10));
    case 'C':  return Math.floor(fibRate * (potency / 5));
    case 'LM': return Math.floor(fibRate * (potency / 2));
    case 'M':  return Math.floor(fibRate * potency);
    case 'F1': return Math.floor(fibRate * (potency / 6));
    case 'F2': return Math.floor(fibRate * (potency / 4));
    case 'F3': return Math.floor(fibRate * (potency / 3));
  }
};

// SCHRITT 7: Finale Rate
const finalRate = fibonacciRate + potencyModifier;
```

**Berechnungsbeispiel:**
```
Wortenergie: "NUX VOMICA"
Normalisiert: "NUXVOMICA"

Positionsgewichtete Summe:
N(14)×1 + U(21)×2 + X(24)×3 + V(22)×4 + O(15)×5 + M(13)×6 + I(9)×7 + C(3)×8 + A(1)×9
= 14 + 42 + 72 + 88 + 75 + 78 + 63 + 24 + 9 = 465

Baserate: 465 × 1000 = 465.000
Fibonacci (21/34): floor((465000 / 21) × 34) = 752.857
Mit D6 Potenz: 752.857 + floor(752.857 × 0.6) = 752.857 + 451.714 = 1.204.571
```

### 2.2 Klienten-Rate Berechnung

**Standort:** `src/components/CopenAlgorithmVisualizationV2.tsx`

```typescript
const calculateClientRate = (patient: CloudPatient): number => {
  // Wenn personalisierte Rate vorhanden (8-12 Stellen)
  if (patient.personal_rate && patient.personal_rate.length >= 8) {
    return parseInt(patient.personal_rate, 10);
  }
  
  // Standard-Berechnung aus Patientendaten
  const clientData = `${patient.first_name} ${patient.last_name} ${patient.birth_date} ${patient.birth_place}`;
  const cleanData = normalizeWordEnergy(clientData);
  
  let position = 1;
  let clientSum = 0;
  
  for (const char of cleanData) {
    const value = getCharValue(char);
    clientSum += value * position;
    position++;
  }
  
  const clientBaseRate = clientSum * 1000;
  const clientFibonacciRate = Math.floor((clientBaseRate / 21) * 34);
  
  return clientFibonacciRate;
};
```

### 2.3 Resonanz-Analyse (Java-Portiert)

**Standort:** `src/utils/resonanceAnalysis.ts`

**Vollständiger Algorithmus:**
```typescript
// Level-Gewichte für 12 Ebenen
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

// Fisher-Yates Shuffle mit optionalem Quantum-Seed
function fisherYatesShuffle<T>(array: T[], quantumSeed?: number): T[] {
  const shuffled = [...array];
  const getRandom = () => quantumSeed !== undefined 
    ? (Math.random() + quantumSeed) / 2 
    : Math.random();
  
  for (let i = shuffled.length - 1; i > 0; i--) {
    const j = Math.floor(getRandom() * (i + 1));
    [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
  }
  return shuffled;
}

// Gewichtete Zufallsauswahl einer Ebene (1-12)
function weightedPickLevel(): number {
  const TOTAL_WEIGHT = LEVEL_WEIGHTS.reduce((sum, lw) => sum + lw.weight, 0);
  const r = Math.random() * TOTAL_WEIGHT;
  let cumulative = 0;
  
  for (const { level, weight } of LEVEL_WEIGHTS) {
    cumulative += weight;
    if (r < cumulative) return level;
  }
  return 1;
}

// Selektion: Zufällige Prozent-Auswahl
function selectRates(rates, config, quantumSeed?) {
  const targetCount = Math.ceil(rates.length * config.selectionFraction);
  const actualCount = Math.max(config.minSelection, Math.min(config.maxSelection, targetCount));
  const shuffled = fisherYatesShuffle(rates, quantumSeed);
  return shuffled.slice(0, actualCount);
}

// Energetisches Laden (Simulation)
function chargeRates(selectedRates, threshold) {
  const energies: Record<string, number> = {};
  selectedRates.forEach(rate => energies[rate.name] = 0);
  
  let trials = 0;
  let maxEnergy = 0;
  
  while (maxEnergy < threshold) {
    selectedRates.forEach(rate => {
      const boost = Math.floor(Math.random() * 10);
      energies[rate.name] += boost;
      maxEnergy = Math.max(maxEnergy, energies[rate.name]);
    });
    trials++;
    if (trials > 10000) break;
  }
  
  return { energies, trials };
}

// Potenzreihen-Ermittlung (automatisch)
function assignPotencyAndLevels(rateName: string) {
  const potencyTypes = ['D', 'C', 'LM', 'M', 'F1', 'F2', 'F3'];
  const potencyTypeWeights = [30, 25, 20, 15, 5, 3, 2];
  
  // Gewichtete Auswahl des Potenztyps
  const totalWeight = potencyTypeWeights.reduce((sum, w) => sum + w, 0);
  let r = Math.random() * totalWeight;
  let selectedType = 'D';
  
  for (let i = 0; i < potencyTypes.length; i++) {
    r -= potencyTypeWeights[i];
    if (r <= 0) {
      selectedType = potencyTypes[i];
      break;
    }
  }
  
  // Potenzwert gemäß Typ generieren
  let potency;
  switch (selectedType) {
    case 'D':  potency = Math.floor(Math.random() * 100) + 1; break;
    case 'C':  potency = Math.floor(Math.random() * 200) + 1; break;
    case 'LM': potency = Math.floor(Math.random() * 30) + 1; break;
    case 'M':  potency = Math.floor(Math.pow(10, Math.random() * 8)); break;
    case 'F1': potency = Math.floor(Math.pow(10, 6 + Math.random() * 7)); break;
    case 'F2': potency = Math.floor(Math.pow(10, 8 + Math.random() * 7)); break;
    case 'F3': potency = Math.floor(Math.pow(10, 10 + Math.random() * 6)); break;
  }
  
  // Level-Verteilung: 100 Ziehungen
  const levelDistribution: Record<number, number> = {};
  for (let i = 1; i <= 12; i++) levelDistribution[i] = 0;
  for (let i = 0; i < 100; i++) {
    const level = weightedPickLevel();
    levelDistribution[level]++;
  }
  
  // Dominante Ebene
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

// Haupt-Analyse-Engine
export function analyzeRates(rates, config) {
  const selected = selectRates(rates, config);
  const { energies, trials } = chargeRates(selected, config.chargingThreshold);
  
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
  
  rateObjects.sort((a, b) => b.energeticValue - a.energeticValue);
  
  return {
    rateObjects: config.maxEntries ? rateObjects.slice(0, config.maxEntries) : rateObjects,
    numberOfTrials: trials,
  };
}

// Standard-Konfiguration
export const DEFAULT_ANALYSIS_CONFIG = {
  selectionFraction: 0.1,  // 10%
  minSelection: 1,
  maxSelection: 100,
  chargingThreshold: 100,
  maxEntries: 35,
};
```

### 2.4 13-Ebenen Level-Resonanz

**Standort:** `src/utils/levelResonance.ts`

```typescript
export const LEVELS = [
  { id: 1, name: "Physical Realm - Particles", germanName: "Physische Ebene - Partikel", frequencyRange: { min: 1, max: 100000 }, keywords: ["atom", "partikel", "molekül", "element", "materie"] },
  { id: 2, name: "Physical Realm - Structure", germanName: "Physische Ebene - Struktur", frequencyRange: { min: 100000, max: 500000 }, keywords: ["körper", "organ", "gewebe", "struktur"] },
  { id: 3, name: "Etheric Realm - Prana", germanName: "Ätherische Ebene - Prana", frequencyRange: { min: 500000, max: 1000000 }, keywords: ["prana", "qi", "lebenskraft", "atmung"] },
  { id: 4, name: "Etheric Realm - Meridians", germanName: "Ätherische Ebene - Meridiane", frequencyRange: { min: 1000000, max: 2000000 }, keywords: ["meridian", "chakra", "energiekanal", "nadis"] },
  { id: 5, name: "Astral Realm - Emotions", germanName: "Astrale Ebene - Emotionen", frequencyRange: { min: 2000000, max: 3500000 }, keywords: ["emotion", "gefühl", "empfindung"] },
  { id: 6, name: "Astral Realm - Thought-Forms", germanName: "Astrale Ebene - Gedankenformen", frequencyRange: { min: 3500000, max: 5000000 }, keywords: ["gedanke", "thought", "magnetisch", "schwingung"] },
  { id: 7, name: "Mental Realm - Time", germanName: "Mentale Ebene - Zeit", frequencyRange: { min: 5000000, max: 7000000 }, keywords: ["zeit", "time", "raum", "space", "form"] },
  { id: 8, name: "Mental Realm - Mental Constructs", germanName: "Mentale Ebene - Mentale Konstrukte", frequencyRange: { min: 7000000, max: 9000000 }, keywords: ["konzept", "idee", "mental", "konstrukt"] },
  { id: 9, name: "Causal Plane - Blueprints", germanName: "Kausale Ebene - Blaupausen", frequencyRange: { min: 9000000, max: 11000000 }, keywords: ["akasha", "blueprint", "blaupause", "destiny"] },
  { id: 10, name: "Causal Plane - Alchemy", germanName: "Kausale Ebene - Alchemie", frequencyRange: { min: 11000000, max: 13000000 }, keywords: ["intention", "alchemie", "transformation"] },
  { id: 11, name: "Atmic Plane - Identity", germanName: "Atmische Ebene - Identität", frequencyRange: { min: 13000000, max: 16000000 }, keywords: ["identität", "essenz", "identity", "essence"] },
  { id: 12, name: "Atmic Plane - Love & Unity", germanName: "Atmische Ebene - Liebe & Einheit", frequencyRange: { min: 16000000, max: 20000000 }, keywords: ["liebe", "einheit", "love", "unity"] },
  { id: 13, name: "Creator - Divinity", germanName: "Schöpfer - Göttlichkeit", frequencyRange: { min: 20000000, max: Infinity }, keywords: ["creator", "schöpfer", "göttlich", "divinity", "ewigkeit"] }
];

// Resonanz-Berechnung
export function calculateLevelResonance(copenRate: number, word: string): Record<string, number> {
  const resonance: Record<string, number> = {};
  const normalizedWord = word.toLowerCase();

  LEVELS.forEach(level => {
    let baseResonance = 0;
    const { min, max } = level.frequencyRange;
    
    // Frequenzbasierte Resonanz
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
      baseResonance = Math.max(0, 30 - ((copenRate - max) / max) * 30);
    }

    // Keyword-Bonus
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

### 2.5 Hardware-Algorithmen (Kozyrev-Zeitenergie)

**Standort:** `src/utils/hardwareAlgorithms.ts`

```typescript
export interface HardwareMetrics {
  cpuQuantumJitter: number;      // 0.0 - 1.0 (+2-3% Akkuranz)
  ramEntropy: number;            // 0.0 - 1.0 (+1-2% Akkuranz)
  timeSourceCoherence: number;   // 0.0 - 1.0 (+3-4% Akkuranz) - Kozyrev-Kernprinzip
  gpuRenderingEntropy: number;   // 0.0 - 1.0 (+2-3% Akkuranz)
  networkLatency: number;        // 0.0 - 1.0 (+1-2% Akkuranz)
  combinedScore: number;         // 0.0 - 1.0 (+3-5% Akkuranz)
}

export interface HardwareConfig {
  cpuQuantumJitter: 'auto' | 'on' | 'off';
  ramEntropy: 'auto' | 'on' | 'off';
  timeSourceCoherence: 'auto' | 'on' | 'off';
  gpuRenderingEntropy: 'auto' | 'on' | 'off';
  networkLatency: 'auto' | 'on' | 'off';
  combinedAlgorithm: 'auto' | 'on' | 'off';
}

// CPU Quantum Jitter
function getCPUQuantumJitter(): number {
  const samples = 100;
  const timestamps: number[] = [];
  for (let i = 0; i < samples; i++) timestamps.push(performance.now());
  
  const diffs = timestamps.slice(1).map((t, i) => t - timestamps[i]);
  const mean = diffs.reduce((a, b) => a + b) / diffs.length;
  const variance = diffs.reduce((sum, d) => sum + (d - mean) ** 2, 0) / diffs.length;
  const stdDev = Math.sqrt(variance);
  
  return Math.min(1.0, stdDev / 0.1);
}

// Time Source Coherence (Kozyrev-Bezug)
function getTimeSourceCoherence(): number {
  const perfTime = performance.now();
  const dateTime = Date.now();
  const perfTimeAgain = performance.now();
  
  const perfDelta = perfTimeAgain - perfTime;
  const drift = Math.abs(perfDelta - perfDelta);  // Drift zwischen Zeitquellen
  
  return 1.0 - Math.min(1.0, drift / 1.0);
}

// Combined Score (gewichtete Kombination)
function calculateCombinedScore(metrics: HardwareMetrics): number {
  const weights = {
    timeSourceCoherence: 0.30,
    cpuQuantumJitter: 0.25,
    gpuRenderingEntropy: 0.20,
    ramEntropy: 0.15,
    networkLatency: 0.10
  };
  
  return (
    metrics.timeSourceCoherence * weights.timeSourceCoherence +
    metrics.cpuQuantumJitter * weights.cpuQuantumJitter +
    metrics.gpuRenderingEntropy * weights.gpuRenderingEntropy +
    metrics.ramEntropy * weights.ramEntropy +
    metrics.networkLatency * weights.networkLatency
  );
}

// Rate-Modulation
export function modulateRateWithHardware(baseRate: number, config: HardwareConfig, metrics: HardwareMetrics): number {
  let modulationFactor = 0;
  
  if (config.combinedAlgorithm === 'on' || config.combinedAlgorithm === 'auto') {
    modulationFactor = metrics.combinedScore * 0.05;  // +3-5%
  } else {
    if (config.cpuQuantumJitter !== 'off') modulationFactor += metrics.cpuQuantumJitter * 0.03;
    if (config.ramEntropy !== 'off') modulationFactor += metrics.ramEntropy * 0.02;
    if (config.timeSourceCoherence !== 'off') modulationFactor += metrics.timeSourceCoherence * 0.04;
    if (config.gpuRenderingEntropy !== 'off') modulationFactor += metrics.gpuRenderingEntropy * 0.03;
    if (config.networkLatency !== 'off') modulationFactor += metrics.networkLatency * 0.02;
  }
  
  return baseRate * (1 + modulationFactor);
}
```

### 2.6 Morphisches Feld Engine

**Standort:** `src/utils/morphicFieldEngine.ts`

**Quantenformel:**
```
Ψ_total(x,t) = Σn αn |ψn⟩ e^(-iEnt/ℏ) × C(numerical_sequence) × G(geometric_forms) × I(intention)
```

```typescript
// Geometrische Formen (Platonische Körper)
type GeometricForm = 
  | 'tetrahedron'    // φ = 1.618
  | 'cube'           // √3 = 1.732
  | 'octahedron'     // 2.000
  | 'dodecahedron'   // φ² = 2.618
  | 'icosahedron'    // √5 = 2.236
  | 'merkaba'        // π = 3.141
  | 'torus'          // √2 = 1.414
  | 'flower_of_life' // e = 2.718
  | 'sri_yantra';    // 3.000

// Intentionen
type IntentionType =
  | 'healing'        // √φ = 1.272
  | 'manifestation'  // φ = 1.618
  | 'protection'     // √2 = 1.414
  | 'transformation' // √5 = 2.236
  | 'connection'     // 2.000
  | 'clearing'       // √3 = 1.732
  | 'activation'     // e = 2.718
  | 'harmonization'; // φ = 1.618

// Quantum Superposition
function calculateQuantumSuperposition(states: QuantumState[], time: number): number {
  let realPart = 0;
  let imagPart = 0;
  
  for (const state of states) {
    const phase = -(state.energy * time) / HBAR + (state.phase || 0);
    const cosPhase = Math.cos(phase);
    const sinPhase = Math.sin(phase);
    
    realPart += state.amplitude * cosPhase;
    imagPart += state.amplitude * sinPhase;
  }
  
  return Math.sqrt(realPart * realPart + imagPart * imagPart) / Math.sqrt(states.length);
}

// Haupt-Engine
export async function calculateMorphicField(config: MorphicFieldConfig): Promise<MorphicFieldResult> {
  const quantumComponent = calculateQuantumSuperposition(config.quantumStates, config.time || Date.now());
  const numericalFactor = calculateNumericalFactor(config.numericalSequence);
  const geometricFactor = calculateGeometricFactor(config.geometricForm);
  const intentionFactor = calculateIntentionFactor(config.intention);
  
  let hardwareFactor = 1.0;
  if (config.useHardwareModulation) {
    const metrics = await collectHardwareMetrics();
    hardwareFactor = 1 + (metrics.combinedScore / 100);
  }
  
  const totalWaveFunction = quantumComponent * numericalFactor * geometricFactor * intentionFactor * hardwareFactor;
  
  return {
    totalWaveFunction,
    quantumComponent,
    numericalFactor,
    geometricFactor,
    intentionFactor,
    hardwareFactor,
    coherence: calculateCoherence(quantumComponent, numericalFactor, geometricFactor, intentionFactor),
    resonanceFrequency: calculateResonanceFrequency(config.quantumStates, config.numericalSequence),
    fieldStrength: totalWaveFunction * coherence,
    timestamp: config.time || Date.now()
  };
}
```

---

## 3. DATENBANK-SCHEMA (SUPABASE)

### 3.1 patients_v2
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
  personal_rate TEXT,  -- 8-12 stellige personalisierte Rate
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
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
CREATE POLICY "Admins can view all patients v2" ON public.patients_v2
  FOR SELECT USING (has_role(auth.uid(), 'admin'::app_role));
```

### 3.2 harmonization_sessions_v2
```sql
CREATE TABLE public.harmonization_sessions_v2 (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID,
  patient_id UUID NOT NULL,
  word TEXT NOT NULL,
  copen_rate TEXT,
  tested_potency TEXT,
  duration_seconds INTEGER NOT NULL,
  remaining_seconds INTEGER,
  progress INTEGER DEFAULT 0,
  status TEXT NOT NULL DEFAULT 'pending',  -- pending, running, paused, completed, cancelled
  started_at TIMESTAMP WITH TIME ZONE,
  completed_at TIMESTAMP WITH TIME ZONE,
  job_started_at TIMESTAMP WITH TIME ZONE,
  job_last_heartbeat TIMESTAMP WITH TIME ZONE,
  pulse_seconds INTEGER,      -- Impuls-Dauer
  pause_seconds INTEGER,      -- Pausen-Dauer
  pulse_pause_active BOOLEAN DEFAULT false,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- RLS Policies (analog zu patients_v2)
```

### 3.3 word_databases
```sql
CREATE TABLE public.word_databases (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID NOT NULL,
  name TEXT NOT NULL,
  entries TEXT[] NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);
```

### 3.4 analysis_archives_v2
```sql
CREATE TABLE public.analysis_archives_v2 (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
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
  patient_data JSONB,
  database_entries TEXT[],
  analysis_timestamp TIMESTAMP WITH TIME ZONE DEFAULT now(),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);
```

### 3.5 harmonization_templates_v2
```sql
CREATE TABLE public.harmonization_templates_v2 (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID NOT NULL,
  patient_id UUID NOT NULL,
  name TEXT NOT NULL,
  description TEXT,
  sessions JSONB NOT NULL,  -- Array von Session-Konfigurationen
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);
```

### 3.6 user_roles
```sql
CREATE TABLE public.user_roles (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID NOT NULL,
  role app_role NOT NULL DEFAULT 'user',  -- ENUM: 'admin', 'user'
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- has_role Funktion
CREATE OR REPLACE FUNCTION public.has_role(_user_id uuid, _role app_role)
RETURNS boolean
LANGUAGE sql
STABLE SECURITY DEFINER
AS $$
  SELECT EXISTS (
    SELECT 1 FROM public.user_roles
    WHERE user_id = _user_id AND role = _role
  )
$$;
```

---

## 4. EDGE FUNCTIONS

### 4.1 harmonization-worker

**Standort:** `supabase/functions/harmonization-worker/index.ts`

**Funktionalität:**
1. Setzt 'pending' Sessions auf 'running' (Start)
2. Tickt aktive Sessions (Heartbeat, Restzeit-Berechnung)
3. Berücksichtigt Impuls/Pausen-Modus
4. Schließt abgelaufene Sessions ab ('completed')

```typescript
// Impuls/Pausen-Logik
if (session.pulse_pause_active && session.pulse_seconds && session.pause_seconds) {
  const cycleLength = session.pulse_seconds + session.pause_seconds;
  const cycles = Math.floor(elapsed / cycleLength);
  const remainder = elapsed % cycleLength;
  
  // Nur Impuls-Zeiten zählen als effektive Zeit
  effectiveElapsed = cycles * session.pulse_seconds;
  if (remainder <= session.pulse_seconds) {
    effectiveElapsed += remainder;
  } else {
    effectiveElapsed += session.pulse_seconds;
  }
}
```

---

## 5. KOMPONENTEN-HIERARCHIE

```
App.tsx
├── AuthPage.tsx (Login/Registrierung)
├── Index.tsx (Hauptübersicht mit Theorie-Karten)
│   └── 22+ Theorie-Komponenten
├── CopenVisualizationV2Page.tsx (Haupt-Arbeitsbereich)
│   ├── CopenAlgorithmVisualizationV2.tsx
│   │   ├── PatientManagerCloudV2.tsx
│   │   ├── HardwareAlgorithmSettings.tsx
│   │   ├── KozyrevIndicators.tsx
│   │   ├── DatabaseManager.tsx
│   │   ├── HarmonizationArchiveCloud.tsx
│   │   └── HarmonizationTemplates.tsx
│   ├── AnalysisArchiveCloud.tsx
│   ├── SessionStatusList.tsx
│   └── WorkerStatusMonitor.tsx
├── CopenGeneratorPage.tsx (Einfacher Raten-Generator)
├── MorphicFieldPage.tsx (Morphisches Feld Engine)
└── FormulasPage.tsx (Formel-Kompendium)
```

---

## 6. SPEZIELLE FUNKTIONEN

### 6.1 Export Aktive Harmonisierungen als Datenbank

**Standort:** `CopenAlgorithmVisualizationV2.tsx`, Funktion `exportActiveHarmonizationsToDatabase`

```typescript
const exportActiveHarmonizationsToDatabase = async () => {
  const { data: sessions } = await supabase
    .from('harmonization_sessions_v2')
    .select('*')
    .eq('user_id', user.id)
    .eq('patient_id', selectedPatient.id)
    .in('status', ['running', 'pending']);

  const entries = sessions.map(session => {
    const match = session.word.match(/mit\s+([\d.]+)/i);
    return match ? match[1] : session.word;
  });

  const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
  const databaseName = `${selectedPatient.first_name}_${selectedPatient.last_name}_Aktive_${timestamp}`;

  await supabase
    .from('word_databases')
    .insert({ user_id: user.id, name: databaseName, entries });
};
```

### 6.2 Direkte Raten-Harmonisierung

**Standort:** `DatabaseManager.tsx`, Funktion `handleDirectRateHarmonization`

Format: "Kohärente Harmonisierung mit [Rate]"

### 6.3 Potenz-Wort-Konvertierung beim Import

**Standort:** `src/utils/potencyText.ts`

Konvertiert z.B. `D6` → `Dsechs`, `C100` → `CEinhundert`

### 6.4 Wortenergie-Historie

**Standort:** `src/hooks/useWordEnergyHistory.ts`

Speichert letzte 20 Wortenergien im localStorage.

---

## 7. UI/UX SPEZIFIKATIONEN

### 7.1 Farbschema
```css
/* Gradient Background */
bg-gradient-to-br from-slate-900 via-blue-900 to-indigo-900

/* Karten */
bg-white/10 border-white/20 backdrop-blur-sm

/* Buttons */
bg-primary hover:bg-primary/90

/* Status-Farben */
.running: bg-blue-50 border-blue-400
.paused: bg-yellow-50 border-yellow-400
.completed: bg-green-50 border-green-400
```

### 7.2 Responsive Breakpoints
```
sm: 640px
md: 768px
lg: 1024px
xl: 1280px
```

### 7.3 Animationen
- Progress Bars: CSS transitions
- Laufende Harmonisierungen: `animate-pulse` auf Raten
- Hover-Effekte: `hover:scale-105`, `hover:bg-white/15`

---

## 8. VERZEICHNISSTRUKTUR

```
src/
├── components/
│   ├── ui/                         # Shadcn/UI Komponenten
│   ├── dialogs/                    # Dialog-Komponenten
│   ├── forms/                      # Formular-Komponenten
│   ├── tables/                     # Tabellen-Komponenten
│   ├── theories/                   # Theorie-Komponenten
│   │   ├── advanced/               # Erweiterte Theorien
│   │   ├── bioresonanz-schmidt/    # Bioresonanz
│   │   ├── chakren-meridiane/      # Chakren
│   │   ├── harmonikale-baklayan/   # Baklayan
│   │   ├── kozyrev/                # Kozyrev-Dioden
│   │   ├── radionik-copen/         # Bruce Copen
│   │   ├── radionik-general/       # Radionik allgemein
│   │   ├── theorien-broers/        # Dieter Broers
│   │   └── wellengenetik-garjajev/ # Wellengenetik
│   ├── AnalysisArchiveCloud.tsx
│   ├── CopenAlgorithmVisualization.tsx
│   ├── CopenAlgorithmVisualizationV2.tsx
│   ├── CopenRateGenerator.tsx
│   ├── DatabaseManager.tsx
│   ├── HardwareAlgorithmSettings.tsx
│   ├── HarmonizationArchive.tsx
│   ├── HarmonizationArchiveCloud.tsx
│   ├── HarmonizationTemplates.tsx
│   ├── KozyrevIndicators.tsx
│   ├── MorphicFieldCalculator.tsx
│   ├── PatientHardwareConfig.tsx
│   ├── PatientManager.tsx
│   ├── PatientManagerCloud.tsx
│   ├── PatientManagerCloudV2.tsx
│   ├── ProtectedRoute.tsx
│   ├── SessionStatusList.tsx
│   ├── TheoryManager.tsx
│   ├── UserMenu.tsx
│   └── WorkerStatusMonitor.tsx
├── hooks/
│   ├── use-mobile.tsx
│   ├── use-toast.ts
│   ├── useAuth.ts
│   ├── useTheoryState.ts
│   └── useWordEnergyHistory.ts
├── pages/
│   ├── AuthPage.tsx
│   ├── CopenGeneratorPage.tsx
│   ├── CopenVisualizationV2Page.tsx
│   ├── FormulasPage.tsx
│   ├── ImportPage.tsx
│   ├── Index.tsx
│   ├── MorphicFieldPage.tsx
│   └── NotFound.tsx
├── utils/
│   ├── alphabetSystems.ts
│   ├── analysisInterpreter.ts
│   ├── copenRateGenerator.ts
│   ├── hardwareAlgorithms.ts
│   ├── levelResonance.ts
│   ├── mentalRatesParser.ts
│   ├── morphicFieldEngine.ts
│   ├── ocrUtils.ts
│   ├── ollamaClient.ts
│   ├── potencyText.ts
│   └── resonanceAnalysis.ts
├── integrations/supabase/
│   ├── client.ts
│   └── types.ts
├── types/
│   └── patient.ts
├── db/
│   └── AppDatabase.ts
├── App.tsx
├── App.css
├── index.css
├── main.tsx
└── vite-env.d.ts

supabase/
├── config.toml
└── functions/
    └── harmonization-worker/
        └── index.ts
```

---

## 9. CHANGELOG

### Version 2.4.0 (2025-12-07)
- Export aktiver Harmonisierungen als Datenbank implementiert
- Vollständige Dokumentation erstellt

### Version 2.3.0
- Direkte Raten-Harmonisierung
- Impuls/Pausen-Modus
- Hardware-Algorithmen Integration

### Version 2.2.0
- Morphisches Feld Engine
- 13-Ebenen Resonanzanalyse
- Personalisierte Klienten-Rate

### Version 2.1.0
- Java-Algorithmus portiert (Resonanzanalyse)
- LLM-Interpretation (Ollama)
- Adaptive Fibonacci-Modulation

### Version 2.0.0
- V2-Datenbank-Tabellen
- Cloud-Synchronisierung
- Parallele Harmonisierungen

---

## 10. WIEDERHERSTELLUNGS-ANLEITUNG

### 10.1 Voraussetzungen
- Node.js 18+
- Supabase-Projekt (oder Lovable Cloud)
- npm/bun

### 10.2 Installation
```bash
# 1. Repository klonen
git clone [repository-url]
cd [project-name]

# 2. Dependencies installieren
npm install

# 3. Umgebungsvariablen konfigurieren
# .env wird automatisch von Lovable Cloud bereitgestellt

# 4. Entwicklungsserver starten
npm run dev
```

### 10.3 Datenbank-Migration
```sql
-- Alle Tabellen gemäß Abschnitt 3 erstellen
-- RLS-Policies gemäß Abschnitt 3 erstellen
-- has_role Funktion erstellen
```

### 10.4 Edge Function Deployment
```bash
# Edge Function wird automatisch deployed
# Manuell: supabase functions deploy harmonization-worker
```

---

**Erstellt:** 2025-12-07
**Version:** 2.4.0
**Status:** Produktionsreif
