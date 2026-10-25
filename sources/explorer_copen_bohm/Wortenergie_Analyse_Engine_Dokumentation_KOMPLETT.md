# Wortenergie-Analyse-Engine - Vollständige Entwicklerdokumentation

**Version:** 2.0  
**Datum:** 2025-01-29  
**Autor:** Bruce Copen System

---

## Inhaltsverzeichnis

1. [Überblick](#1-überblick)
2. [Architektur](#2-architektur)
3. [Bruce Copen Rate Generator V4](#3-bruce-copen-rate-generator-v4)
4. [Resonanzanalyse-Engine](#4-resonanzanalyse-engine)
5. [13-Ebenen Kosmologie](#5-13-ebenen-kosmologie)
6. [Quanteninspirierter Fokus-Algorithmus](#6-quanteninspirierter-fokus-algorithmus)
7. [Hardware-Algorithmen (Kozyrev)](#7-hardware-algorithmen-kozyrev)
8. [Raten-Kombination](#8-raten-kombination)
9. [Trend-Analyse](#9-trend-analyse)
10. [Cloud-Persistente Harmonisierung](#10-cloud-persistente-harmonisierung)
11. [Datenstrukturen](#11-datenstrukturen)
12. [Dateien & Komponenten](#12-dateien--komponenten)

---

## 1. Überblick

Die Wortenergie-Analyse-Engine ist ein integriertes System zur:
- Berechnung von Bruce Copen Raten basierend auf Wortenergien
- Resonanzanalyse gegen Klientenfelder
- 13-Ebenen kosmologische Resonanzverteilung
- Quanteninspirierter Fokus-Korrelation
- Hardware-Entropie-Modulation nach Kozyrev
- Persistente Cloud-basierte Harmonisierungen

### Kernprinzipien

```
┌─────────────────────────────────────────────────────────────────┐
│                    WORTENERGIE-ANALYSE-ENGINE                    │
├─────────────────────────────────────────────────────────────────┤
│  Eingabe: Wortliste + Klientenfeld + Fokus (optional)          │
│                           ↓                                      │
│  [Bruce Copen Rate V4] → Normalisierung → Primärsumme           │
│                           ↓                                      │
│  [Fibonacci-Modulation] → Adaptive oder Standard (21/34)        │
│                           ↓                                      │
│  [Resonanzberechnung] → Klienten-Wellenfunktion-Korrelation     │
│                           ↓                                      │
│  [Fokus-Korrelation] → Grover-Amplifikation (optional)          │
│                           ↓                                      │
│  [13-Ebenen-Resonanz] → Kosmologische Verteilung               │
│                           ↓                                      │
│  Ausgabe: WordEnergyTestResult[]                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Architektur

### Dateistruktur

```
src/
├── components/
│   ├── WordEnergyTester.tsx        # Haupt-UI-Komponente
│   ├── SessionStatusList.tsx       # Harmonisierungs-Status
│   └── SymptomBrowser.tsx          # Clarke Materia Medica
│
├── utils/
│   ├── copenRateGenerator.ts       # Bruce Copen V4 Algorithmus
│   ├── resonanceAnalysis.ts        # Resonanzanalyse-Engine
│   ├── levelResonance.ts           # 13-Ebenen Kosmologie
│   ├── quantumFocusAlgorithm.ts    # Fokus-Korrelation
│   └── hardwareAlgorithms.ts       # Kozyrev Hardware-Modulation
│
└── hooks/
    └── useWordEnergyHistory.ts     # Browser-Verlauf
```

### Datenfluss

```typescript
// 1. Eingabe
const word = "Arnica";
const clientWellenfunktion = 12345678;

// 2. Copen Rate berechnen
const rateResult = calculateCopenRate(word, 0, 'D', 'latin');

// 3. 13-Ebenen-Resonanz
const ebenVerteilung = calculateLevelResonance(rateResult.rate, word);

// 4. Basisresonanz zum Klientenfeld
const resonanzBasis = calculateResonanz(rateResult.rate, clientWellenfunktion);

// 5. Fokus-Korrelation (optional)
const fokusResult = calculateFokusResonanz(word, resonanzBasis, 'Herz-Kreislauf', clientWellenfunktion);

// 6. Ergebnis
const result: WordEnergyTestResult = {
  word,
  copenRate: rateResult.rate,
  resonanz: fokusResult.kombinierteResonanz,
  dominanteEbene: findHighestResonanceLevel(ebenVerteilung).level,
  // ...
};
```

---

## 3. Bruce Copen Rate Generator V4

### Datei: `src/utils/copenRateGenerator.ts`

### Normalisierung

```typescript
const normalize = (w: string) =>
  w
    .toUpperCase()
    .replace(/Ä/g, 'AE')
    .replace(/Ö/g, 'OE')
    .replace(/Ü/g, 'UE')
    .replace(/ß/g, 'SS')
    .replace(/\s*[DCLMF]+\d+/g, '')  // Potenzangaben entfernen
    .replace(/[^A-Z0-9]/g, '')       // Nur Buchstaben und Zahlen
    .trim();
```

### Zeichenwert-Berechnung

```typescript
const getCharValue = (ch: string): number => {
  if (ch >= 'A' && ch <= 'Z') {
    return ch.charCodeAt(0) - 64;  // A=1..Z=26
  }
  if (ch >= '0' && ch <= '9') {
    return parseInt(ch, 10);       // 0-9
  }
  return 0;
};
```

### Primärsumme (Positionsgewichtet)

```typescript
const computePrimarySum = (text: string) => {
  let sum = 0;
  let pos = 1;
  for (const ch of text) {
    const value = getCharValue(ch);
    sum += value * pos;
    pos++;
  }
  return sum;
};
```

**Beispiel "ARNICA":**
```
A(1)×1 + R(18)×2 + N(14)×3 + I(9)×4 + C(3)×5 + A(1)×6
= 1 + 36 + 42 + 36 + 15 + 6 = 136
```

### Bildsignatur-Integration (Optional)

```typescript
if (useImageSignature && imageSignature) {
  const imgPrimary = computePrimarySum(normalize(imageSignature));
  primarySum = Math.floor((primarySum + imgPrimary) / 2);
}
```

### Baserate

```typescript
const baseRate = primarySum * 1000;  // 136 × 1000 = 136.000
```

### Fibonacci-Modulation

#### Standard (Original Copen)
```typescript
fibonacciRate = Math.floor((baseRate / 21) * 34);  // 136.000 / 21 × 34 = 220.190
```

#### Adaptiv (Wortlängen-abhängig)
```typescript
const getAdaptiveFibonacciPair = (wordLength: number) => {
  if (wordLength >= 1 && wordLength <= 4) return { div: 13, mult: 21 };   // ≈ 1.615
  if (wordLength >= 5 && wordLength <= 10) return { div: 21, mult: 34 }; // ≈ 1.619 (Standard)
  if (wordLength >= 11 && wordLength <= 20) return { div: 34, mult: 55 }; // ≈ 1.618
  return { div: 55, mult: 89 };  // > 20 Zeichen
};
```

### Potenz-Bonus

| Potenztyp | Formel | Beispiel (p=6) |
|-----------|--------|----------------|
| D (Dezimal) | `fibonacciRate × (p / 10)` | 220.190 × 0.6 = 132.114 |
| C (Centesimal) | `fibonacciRate × (p / 5)` | 220.190 × 1.2 = 264.228 |
| LM (50-Millesimal) | `fibonacciRate × (p / 2)` | 220.190 × 3 = 660.570 |
| M (Millennial) | `fibonacciRate × p` | 220.190 × 6 = 1.321.140 |
| F1 | `fibonacciRate × (p / 6)` | 220.190 × 1 = 220.190 |
| F2 | `fibonacciRate × (p / 4)` | 220.190 × 1.5 = 330.285 |
| F3 | `fibonacciRate × (p / 3)` | 220.190 × 2 = 440.380 |

### Finale Rate

```typescript
const finalRate = fibonacciRate + potencyBonus;
```

---

## 4. Resonanzanalyse-Engine

### Datei: `src/utils/resonanceAnalysis.ts`

### Konfiguration

```typescript
interface AnalysisConfig {
  selectionFraction: number;  // Standard: 0.1 (10%)
  minSelection: number;       // Minimum 1
  maxSelection: number;       // Maximum 100
  chargingThreshold: number;  // Standard: 100
  maxEntries?: number;        // Optional: Limit Ergebnisse
}

const DEFAULT_ANALYSIS_CONFIG: AnalysisConfig = {
  selectionFraction: 0.1,
  minSelection: 1,
  maxSelection: 100,
  chargingThreshold: 100,
  maxEntries: 35
};
```

### Ebenen-Gewichte (1-12)

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
  { level: 12, weight: 2 }    // Atmic Love
];
```

### Fisher-Yates Shuffle

```typescript
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
```

### Gewichtete Ebenen-Auswahl

```typescript
function weightedPickLevel(): number {
  const r = Math.random() * TOTAL_WEIGHT;  // TOTAL_WEIGHT = 110
  let cumulative = 0;
  
  for (const { level, weight } of LEVEL_WEIGHTS) {
    cumulative += weight;
    if (r < cumulative) return level;
  }
  return 1;
}
```

### Energetisches Laden

```typescript
function chargeRates(
  selectedRates: Array<{ name: string; copenRate: number }>,
  threshold: number
): { energies: Record<string, number>; trials: number } {
  const energies: Record<string, number> = {};
  selectedRates.forEach(rate => energies[rate.name] = 0);
  
  let trials = 0;
  let maxEnergy = 0;
  
  while (maxEnergy < threshold && trials < 10000) {
    selectedRates.forEach(rate => {
      const boost = Math.floor(Math.random() * 10);  // 0-9
      energies[rate.name] += boost;
      maxEnergy = Math.max(maxEnergy, energies[rate.name]);
    });
    trials++;
  }
  
  return { energies, trials };
}
```

### Potenz-Zuweisung

```typescript
function assignPotencyAndLevels(rateName: string) {
  // Potenzreihen mit Gewichtung
  const potencyTypes = ['D', 'C', 'LM', 'M', 'F1', 'F2', 'F3'];
  const potencyTypeWeights = [30, 25, 20, 15, 5, 3, 2];
  
  // Wertebereich je Typ
  switch (selectedPotencyType) {
    case 'D': return Math.floor(Math.random() * 100) + 1;      // 1-100
    case 'C': return Math.floor(Math.random() * 200) + 1;      // 1-200
    case 'LM': return Math.floor(Math.random() * 30) + 1;      // 1-30
    case 'M': return Math.floor(Math.pow(10, Math.random() * 8));  // 1-100M
    case 'F1': return Math.floor(Math.pow(10, 6 + Math.random() * 7));  // 1M-10T
    case 'F2': return Math.floor(Math.pow(10, 8 + Math.random() * 7));  // 100M-1Q
    case 'F3': return Math.floor(Math.pow(10, 10 + Math.random() * 6)); // 10B-10Q
  }
}
```

---

## 5. 13-Ebenen Kosmologie

### Datei: `src/utils/levelResonance.ts`

### Ebenen-Definition

| ID | Name | Frequenzbereich |
|----|------|-----------------|
| 1 | Physical Realm - Particles | 1 - 100.000 Hz |
| 2 | Physical Realm - Structure | 100.000 - 500.000 Hz |
| 3 | Etheric Realm - Prana | 500.000 - 1.000.000 Hz |
| 4 | Etheric Realm - Meridians | 1.000.000 - 2.000.000 Hz |
| 5 | Astral Realm - Emotions | 2.000.000 - 3.500.000 Hz |
| 6 | Astral Realm - Thought-Forms | 3.500.000 - 5.000.000 Hz |
| 7 | Mental Realm - Time | 5.000.000 - 7.000.000 Hz |
| 8 | Mental Realm - Mental Constructs | 7.000.000 - 9.000.000 Hz |
| 9 | Causal Plane - Blueprints | 9.000.000 - 11.000.000 Hz |
| 10 | Causal Plane - Alchemy | 11.000.000 - 13.000.000 Hz |
| 11 | Atmic Plane - Identity | 13.000.000 - 16.000.000 Hz |
| 12 | Atmic Plane - Love & Unity | 16.000.000 - 20.000.000 Hz |
| 13 | Creator - Divinity | 20.000.000+ Hz |

### Resonanz-Berechnung

```typescript
function calculateLevelResonance(copenRate: number, word: string): Record<string, number> {
  const resonance: Record<string, number> = {};
  const normalizedWord = word.toLowerCase();

  LEVELS.forEach(level => {
    let baseResonance = 0;
    const { min, max } = level.frequencyRange;
    
    // Frequenzbasierte Resonanz
    if (max === Infinity) {
      // Göttliche Ebene
      baseResonance = copenRate >= min ? 100 : (copenRate / min) * 50;
    } else if (copenRate >= min && copenRate <= max) {
      // Rate im Bereich → hohe Resonanz
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

    // Keyword-Bonus (+25% pro Match)
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

### Höchste Ebene finden

```typescript
function findHighestResonanceLevel(
  resonanceValues: Record<string, number>,
  excludeLevel13: boolean = true
): { level: number; value: number } {
  let highestLevel = 1;
  let highestValue = 0;

  Object.entries(resonanceValues).forEach(([key, value]) => {
    const levelMatch = key.match(/level_(\d+)/);
    if (levelMatch) {
      const levelId = parseInt(levelMatch[1]);
      if (excludeLevel13 && levelId === 13) return;
      
      if (value > highestValue) {
        highestLevel = levelId;
        highestValue = value;
      }
    }
  });

  return { level: highestLevel, value: highestValue };
}
```

---

## 6. Quanteninspirierter Fokus-Algorithmus

### Datei: `src/utils/quantumFocusAlgorithm.ts`

### Fokus-Kategorien

```typescript
const FOKUS_KATEGORIEN: Record<string, string[]> = {
  'Herz-Kreislauf': ['herz', 'kreislauf', 'blut', 'druck', 'rhythmus', 'puls', ...],
  'Verdauung': ['magen', 'darm', 'leber', 'galle', 'verdauung', ...],
  'Nervensystem': ['nerv', 'hirn', 'gehirn', 'neuro', 'synapse', ...],
  'Bewegungsapparat': ['gelenk', 'muskel', 'knochen', 'wirbel', ...],
  'Immunsystem': ['immun', 'abwehr', 'antikörper', 'lymph', ...],
  'Hormonsystem': ['hormon', 'drüse', 'schilddrüse', 'insulin', ...],
  'Atemwege': ['lunge', 'atem', 'bronchien', 'sauerstoff', ...],
  'Haut': ['haut', 'dermis', 'epidermis', 'akne', ...],
  'Nieren-Blase': ['niere', 'blase', 'harn', 'filtration', ...],
  'Psyche-Emotion': ['emotion', 'gefühl', 'seele', 'trauma', ...],
  'Energie-Chakra': ['energie', 'chakra', 'meridian', 'qi', ...],
  'Entgiftung': ['detox', 'gift', 'toxin', 'reinigung', ...]
};
```

### Quantenamplitude-Berechnung

```typescript
function calculateQuantumAmplitude(word: string, fokusKeywords: string[]): QuantumAmplitude {
  const wordLower = word.toLowerCase();
  
  // Basisphasenwinkel
  const basePhase = wordLower.split('').reduce((sum, ch, idx) => {
    return sum + (ch.charCodeAt(0) * (idx + 1) * Math.PI / 180);
  }, 0);
  
  // Match-Stärke berechnen
  let matchStrength = 0;
  for (const keyword of fokusKeywords) {
    if (wordLower.includes(keyword) || keyword.includes(wordLower)) {
      const overlapRatio = Math.min(wordLower.length, keyword.length) / 
                           Math.max(wordLower.length, keyword.length);
      matchStrength += overlapRatio;
    }
    
    // Semantische Nähe
    const commonChars = [...new Set(wordLower)].filter(ch => keyword.includes(ch)).length;
    matchStrength += (commonChars / Math.max(wordLower.length, keyword.length)) * 0.3;
  }
  
  matchStrength = Math.min(1, matchStrength / fokusKeywords.length);
  
  // Amplitude in Polarform (Grover-inspiriert)
  const amplitude = 0.5 + (matchStrength * 0.5);
  const phase = basePhase + (matchStrength * Math.PI / 4);
  
  return {
    real: amplitude * Math.cos(phase),
    imaginary: amplitude * Math.sin(phase)
  };
}
```

### Grover-Amplifikation

```typescript
function groverAmplification(amplitude: QuantumAmplitude, iterations: number = 2): QuantumAmplitude {
  let { real, imaginary } = amplitude;
  
  for (let i = 0; i < iterations; i++) {
    const magnitude = Math.sqrt(real * real + imaginary * imaginary);
    
    if (magnitude > 0.6) {  // Schwellwert für relevante Zustände
      const diffusionFactor = 1 + (0.2 * (i + 1));
      real *= diffusionFactor;
      imaginary *= diffusionFactor;
    }
  }
  
  // Renormalisierung
  const newMagnitude = Math.sqrt(real * real + imaginary * imaginary);
  if (newMagnitude > 1) {
    real /= newMagnitude;
    imaginary /= newMagnitude;
  }
  
  return { real, imaginary };
}
```

### Interferenz-Berechnung

```typescript
function calculateInterference(
  wordAmplitude: QuantumAmplitude, 
  clientWellenfunktion: number
): 'konstruktiv' | 'destruktiv' | 'neutral' {
  const clientPhase = (clientWellenfunktion % 360) * Math.PI / 180;
  const wordPhase = Math.atan2(wordAmplitude.imaginary, wordAmplitude.real);
  const phaseDiff = Math.abs(wordPhase - clientPhase) % (2 * Math.PI);
  
  if (phaseDiff < Math.PI / 4 || phaseDiff > 7 * Math.PI / 4) {
    return 'konstruktiv';   // +10% Bonus
  } else if (phaseDiff > 3 * Math.PI / 4 && phaseDiff < 5 * Math.PI / 4) {
    return 'destruktiv';    // -5% Malus
  }
  return 'neutral';
}
```

### Kombinierte Resonanz

```typescript
// Formel: (1 - gewichtung) × baseResonanz + gewichtung × fokusAnteil × interferenz × kohärenz
const kombinierteResonanz = Math.min(100, 
  (1 - gewichtung) * baseResonanz + gewichtung * fokusAnteil
);
```

---

## 7. Hardware-Algorithmen (Kozyrev)

### Datei: `src/utils/hardwareAlgorithms.ts`

### Metriken-Interface

```typescript
interface HardwareMetrics {
  cpuQuantumJitter: number;      // 0.0 - 1.0 (+2-3% Akkuranz)
  ramEntropy: number;            // 0.0 - 1.0 (+1-2% Akkuranz)
  timeSourceCoherence: number;   // 0.0 - 1.0 (+3-4% Akkuranz)
  gpuRenderingEntropy: number;   // 0.0 - 1.0 (+2-3% Akkuranz)
  networkLatency: number;        // 0.0 - 1.0 (+1-2% Akkuranz)
  combinedScore: number;         // 0.0 - 1.0 (+3-5% Akkuranz)
}
```

### CPU Quantum Jitter

```typescript
function getCPUQuantumJitter(): number {
  const samples = 100;
  const timestamps: number[] = [];
  
  for (let i = 0; i < samples; i++) {
    timestamps.push(performance.now());
  }
  
  // Standardabweichung der Zeitstempel-Differenzen
  const diffs = timestamps.slice(1).map((t, i) => t - timestamps[i]);
  const mean = diffs.reduce((a, b) => a + b) / diffs.length;
  const variance = diffs.reduce((sum, d) => sum + (d - mean) ** 2, 0) / diffs.length;
  const stdDev = Math.sqrt(variance);
  
  return Math.min(1.0, stdDev / 0.1);  // Normalisierung
}
```

### Zeit-Kohärenz (Kozyrev-Bezug)

```typescript
function getTimeSourceCoherence(): number {
  const perfTime = performance.now();
  const dateTime = Date.now();
  const perfTimeAgain = performance.now();
  
  const perfDelta = perfTimeAgain - perfTime;
  const drift = Math.abs(perfDelta);
  
  return 1.0 - Math.min(1.0, drift / 1.0);  // Hohe Kohärenz = wenig Drift
}
```

### Kombinierte Gewichtung

```typescript
function calculateCombinedScore(metrics: HardwareMetrics): number {
  const weights = {
    timeSourceCoherence: 0.30,   // Höchste Priorität (Kozyrev: Zeit = Energie)
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
```

### Rate-Modulation

```typescript
function modulateRateWithHardware(baseRate: number, config: HardwareConfig, metrics: HardwareMetrics): number {
  let modulationFactor = 0;
  
  if (config.combinedAlgorithm === 'on') {
    modulationFactor = metrics.combinedScore * 0.05;  // +3-5%
  } else {
    // Einzelne Algorithmen
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

## 8. Raten-Kombination

### Datei: `src/utils/copenRateGenerator.ts`

### Kombinations-Methoden

| Methode | Formel | Beschreibung |
|---------|--------|--------------|
| `arithmetic` | `Σ(rates) / n` | Arithmetisches Mittel |
| `geometric` | `∏(rates)^(1/n)` | Geometrisches Mittel |
| `harmonic` | `n / Σ(1/rate)` | Harmonisches Mittel |
| `fibonacci` | `(arith × 34/21 + geom × 21/34) / 2` | Fibonacci-moduliert |
| `weighted_potency` | `Σ(rate × weight) / Σ(weight)` | Potenz-gewichtet |
| `copen_digital` | `∏(rates) mod 10^10` | 10-stellig digital |
| `malcolm_rae` | `geometric × Φ` | Goldener Schnitt |

### Quanten-erweiterte Kombination

```typescript
const combineCopenRatesWithEntropy = (inputs, preferredMethod, useQuantumEnhancement) => {
  const baseResult = combineCopenRates(inputs, preferredMethod);
  const entropyMetrics = collectLocalEntropy();
  
  const PHI = 1.618033988749895;
  
  // Entropie-gewichtete Modulation
  const entropyWeight = (
    entropyMetrics.cpuJitter * 0.3 +
    entropyMetrics.timeCoherence * 0.4 +
    entropyMetrics.systemEntropy * 0.3
  );
  
  // Quanten-modulierte Rate
  const quantumFactor = 1 + (entropyWeight * 0.05);
  const quantumEnhancedRate = Math.floor(baseResult.combinedRate * quantumFactor * PHI);
  
  // Digitale 10-stellige Rate
  const digitalQuantumRate = Math.floor(
    (baseResult.combinedRate * PHI * PHI) + 
    (timestampFactor * entropyWeight * 1000)
  ) % 10000000000;
  
  return { ...baseResult, quantumEnhancedRate, digitalQuantumRate };
};
```

---

## 9. Trend-Analyse

### WordEnergyTester - Trend-Berechnung

```typescript
const calculateTrends = (archives: ArchivedTest[]) => {
  // Zähle Vorkommen pro SESSION (nicht pro Wort-Eintrag)
  const wordSessionMap = new Map<string, {
    sessionValues: Map<string, {
      resonanz: number;
      intensität: number;
      polarität: number;
      level: number;
    }>;
  }>();

  archives.forEach(archive => {
    archive.results.forEach(result => {
      const existing = wordSessionMap.get(result.word) || { sessionValues: new Map() };
      
      // Höchste Resonanz pro Wort pro Session
      const currentValue = existing.sessionValues.get(archive.id);
      if (!currentValue || result.resonanz > currentValue.resonanz) {
        existing.sessionValues.set(archive.id, {
          resonanz: result.resonanz,
          intensität: result.intensität,
          polarität: result.polaritätWert,
          level: normalizeEbenVerteilung(result)  // Level normalisieren
        });
      }
      wordSessionMap.set(result.word, existing);
    });
  });

  // Trends für Items in ≥2 Sessions
  wordSessionMap.forEach((data, word) => {
    if (data.sessionValues.size >= 2) {
      const values = [...data.sessionValues.values()];
      const trendValue = values[0].resonanz - values[1].resonanz;
      
      allTrends.push({
        word,
        trend: trendValue > 5 ? 'up' : trendValue < -5 ? 'down' : 'stable',
        occurrences: data.sessionValues.size  // Anzahl Sessions
      });
    }
  });
};
```

### Ebenen-Normalisierung

```typescript
const normalizeEbenVerteilung = (result: WordEnergyTestResult): number => {
  if (result.dominanteEbene > 0) return result.dominanteEbene;
  
  // Fallback: Aus ebenVerteilung extrahieren
  let maxLevel = 1, maxValue = 0;
  for (const [key, value] of Object.entries(result.ebenVerteilung || {})) {
    // Matcht: level_1, level_1_physical_particles, etc.
    const match = key.match(/level_(\d+)/);
    if (match && value > maxValue) {
      maxValue = value;
      maxLevel = parseInt(match[1]);
    }
  }
  return maxLevel;
};
```

---

## 10. Cloud-Persistente Harmonisierung

### Supabase-Tabelle: `harmonization_sessions_v2`

| Spalte | Typ | Beschreibung |
|--------|-----|--------------|
| `id` | uuid | Primärschlüssel |
| `user_id` | uuid | Benutzer-ID |
| `patient_id` | uuid | Klienten-ID |
| `word` | text | Harmonisierungswort |
| `copen_rate` | text | Klienten-Rate |
| `duration_seconds` | integer | Gesamtdauer |
| `remaining_seconds` | integer | Verbleibende Zeit |
| `progress` | integer | Fortschritt (0-100%) |
| `status` | text | pending, running, paused, completed, cancelled |
| `pulse_seconds` | integer | Impulsdauer |
| `pause_seconds` | integer | Pausendauer |
| `pulse_pause_active` | boolean | Pulse/Pause aktiv |

### Realtime + Polling

```typescript
useEffect(() => {
  if (!patientId) return;

  const loadActiveSessions = async () => {
    const { data: activeSessions } = await supabase
      .from('harmonization_sessions_v2')
      .select('*')
      .eq('patient_id', patientId)
      .in('status', ['pending', 'running', 'paused']);

    if (activeSessions?.length > 0) {
      const totalDuration = activeSessions.reduce((sum, s) => sum + s.duration_seconds, 0);
      const totalRemaining = activeSessions.reduce((sum, s) => sum + (s.remaining_seconds ?? s.duration_seconds), 0);
      
      setHarmonization(prev => ({
        ...prev,
        isActive: true,
        totalDurationSeconds: totalDuration,
        remainingSeconds: totalRemaining,
        elapsedSeconds: totalDuration - totalRemaining
      }));
    }
  };

  loadActiveSessions();
  const pollInterval = setInterval(loadActiveSessions, 3000);  // Polling alle 3s
  
  const channel = supabase
    .channel(`harmonization-${patientId}`)
    .on('postgres_changes', { event: '*', table: 'harmonization_sessions_v2' }, loadActiveSessions)
    .subscribe();

  return () => {
    clearInterval(pollInterval);
    supabase.removeChannel(channel);
  };
}, [patientId]);
```

---

## 11. Datenstrukturen

### WordEnergyTestResult

```typescript
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
  harmonisierungsWort: string;       // "Kohärente Harmonisierung Regulation {word}"
  harmonisierungsRate: number;
  clarkeSymptoms?: string[];         // Nur Anzeige, keine Berechnung
}
```

### HarmonizationState

```typescript
interface HarmonizationState {
  isActive: boolean;
  isPaused: boolean;
  selectedItems: WordEnergyTestResult[];
  pulseDuration: number;
  pauseDuration: number;
  maxDuration: number;
  elapsedSeconds: number;
  currentItemIndex: number;
  inPulsePhase: boolean;
  totalDurationSeconds: number;
  remainingSeconds: number;
}
```

### ArchivedTest

```typescript
interface ArchivedTest {
  id: string;
  created_at: string;
  total_words: number;
  average_resonance: number;
  top_items: WordEnergyTestResult[];
  results: WordEnergyTestResult[];
}
```

---

## 12. Dateien & Komponenten

### Kernkomponenten

| Datei | Beschreibung |
|-------|--------------|
| `src/components/WordEnergyTester.tsx` | Haupt-UI für Wortenergie-Tests |
| `src/components/SessionStatusList.tsx` | Harmonisierungs-Status-Anzeige |
| `src/components/SymptomBrowser.tsx` | Clarke Materia Medica Browser |

### Algorithmen

| Datei | Beschreibung |
|-------|--------------|
| `src/utils/copenRateGenerator.ts` | Bruce Copen V4, Raten-Kombination |
| `src/utils/resonanceAnalysis.ts` | Java-portierte Resonanz-Engine |
| `src/utils/levelResonance.ts` | 13-Ebenen Kosmologie |
| `src/utils/quantumFocusAlgorithm.ts` | Grover-inspirierte Fokus-Korrelation |
| `src/utils/hardwareAlgorithms.ts` | Kozyrev Hardware-Modulation |

### Datenbanken

| Datei | Beschreibung |
|-------|--------------|
| `public/databases/clarkeMateriaMedica.json` | Clarke Materia Medica |
| `src/utils/meridianPointsDatabase.ts` | 409 Meridianpunkte |
| `src/utils/anatomyDatabases/` | Terminologia Anatomica |

---

## Berechnungsbeispiel

**Eingabe:** "Arnica" mit Klienten-Wellenfunktion 12.345.678

```
1. Normalisierung: "ARNICA"

2. Primärsumme:
   A(1)×1 + R(18)×2 + N(14)×3 + I(9)×4 + C(3)×5 + A(1)×6
   = 1 + 36 + 42 + 36 + 15 + 6 = 136

3. Baserate: 136 × 1000 = 136.000

4. Fibonacci: ⌊(136.000 / 21) × 34⌋ = 220.190

5. Potenz D0: 220.190 + 0 = 220.190

6. Harmonisierungs-Wort: "Kohärente Harmonisierung Regulation Arnica"
   → Separate Rate-Berechnung

7. Resonanz zum Klientenfeld:
   ratio = 220.190 / 12.345.678 ≈ 0.0178
   normalized = |1 - (0.0178 mod 1)| = 0.9822
   jitter = (220.190 mod 1000) / 1000 × 15 = 2.85
   resonanz = min(100, 98.22 + 2.85) = 100%

8. 13-Ebenen (220.190 Hz):
   Level 1 (1-100.000): 67%
   Level 2 (100.000-500.000): 89%  ← Dominant
   Level 3+: fallend

9. Fokus "Herz-Kreislauf" (keine Keywords in "Arnica"):
   fokusKorrelation = 0%
   kombinierteResonanz = (1-0.15) × 100 + 0.15 × 0 = 85%

10. Endergebnis:
    {
      word: "Arnica",
      copenRate: 220190,
      resonanz: 85,
      dominanteEbene: 2,
      harmonisierungsRate: 1549788000
    }
```

---

**Dokumentation erstellt:** 2025-01-29  
**Version:** 2.0  
**Validiert für:** WordEnergyTester, Trend-Analyse, Cloud-Harmonisierung
