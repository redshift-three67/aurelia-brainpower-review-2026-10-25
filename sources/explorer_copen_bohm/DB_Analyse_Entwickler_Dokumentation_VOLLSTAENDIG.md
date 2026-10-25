# Datenbank-Analyse & Datenbank-Manager
## Vollständige Entwickler-Dokumentation für Wiederherstellung

**Version:** 2.5.0  
**Stand:** Dezember 2025  
**Autor:** Bruce Copen System Development Team

---

## 1. Übersicht

Der **DatabaseManager** (`src/components/DatabaseManager.tsx`) ist das zentrale Modul für:
- Import und Verwaltung von Wortenergie-Datenbanken
- Resonanzanalyse nach Java-Algorithmus
- Level-Resonanz-Berechnung (13 kosmologische Ebenen)
- LLM-basierte Interpretation
- Harmonisierungs-Übergabe an Cloud-Worker

---

## 2. Dateistruktur

```
src/
├── components/
│   └── DatabaseManager.tsx          # Haupt-UI-Komponente (1593 Zeilen)
│
└── utils/
    ├── resonanceAnalysis.ts         # Java-portierter Analyse-Algorithmus
    ├── levelResonance.ts            # 13-Ebenen-Kosmologie
    ├── copenRateGenerator.ts        # Bruce Copen V4 Rate-Berechnung
    ├── analysisInterpreter.ts       # LLM/Regel-basierte Interpretation
    ├── hardwareAlgorithms.ts        # Kozyrev Hardware-Modulation
    ├── alphabetSystems.ts           # Alphabet-Systeme (Latin, Runisch, etc.)
    └── potencyText.ts               # Potenz-Zahlen zu Wörtern
```

---

## 3. Kern-Interfaces

### 3.1 CloudPatient
```typescript
interface CloudPatient {
  id: string;
  first_name: string;
  last_name: string;
  birth_date: string;
  birth_place: string;
  image_signature?: string | null;
  image_signature_active?: boolean;
}
```

### 3.2 ResonanceResult
```typescript
interface ResonanceResult {
  word: string;                      // Wortenergie
  potency: number;                   // Potenzwert (1-100, 1-200, etc.)
  potencyType: 'D' | 'C' | 'LM' | 'M' | 'F1' | 'F2' | 'F3';
  rate: number;                      // Berechnete Copen-Rate
  resonanceScore: number;            // Resonanz-Score (0-100%)
  clientResonance: number;           // Klienten-Rate
  levelResonance?: Record<string, number>;  // 13 Ebenen-Werte
  highestLevel?: number;             // Dominante Ebene (1-12)
  highestLevelValue?: number;        // Prozent der dominanten Ebene
}
```

### 3.3 RateObject (Resonanzanalyse)
```typescript
interface RateObject {
  rateName: string;
  copenRate: number;
  energeticValue: number;            // Energetischer Ladungswert
  potency: number;                   // Automatisch ermittelt
  potencyType: 'D' | 'C' | 'LM' | 'M' | 'F1' | 'F2' | 'F3';
  levelDistribution: Record<number, number>;  // 100 Ziehungen
  dominantLevel: number;             // Ebene mit meisten Treffern
}
```

### 3.4 AnalysisConfig
```typescript
interface AnalysisConfig {
  selectionFraction: number;  // Standard: 0.1 (10%)
  minSelection: number;       // Minimum Auswahl
  maxSelection: number;       // Maximum Auswahl
  chargingThreshold: number;  // Energetische Schwelle (Standard: 100)
  maxEntries?: number;        // Max. Ergebnisse (Standard: 35)
}
```

---

## 4. Algorithmen im Detail

### 4.1 Bruce Copen Rate-Berechnung V4 (`copenRateGenerator.ts`)

#### Schritt 1: Normalisierung
```typescript
const normalize = (w: string) =>
  w
    .toUpperCase()
    .replace(/Ä/g, 'AE')
    .replace(/Ö/g, 'OE')
    .replace(/Ü/g, 'UE')
    .replace(/ß/g, 'SS')
    .replace(/\s*[DCLMF]+\d+/g, '')  // Potenzangaben entfernen
    .replace(/[^A-Z0-9]/g, '')        // Nur Buchstaben und Zahlen
    .trim();
```

#### Schritt 2: Zeichenwert-Berechnung
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

#### Schritt 3: Positions-gewichtete Primärsumme
```typescript
const computePrimarySum = (text: string) => {
  let sum = 0;
  let pos = 1;
  for (const ch of text) {
    const value = getCharValue(ch);
    sum += value * pos;  // Position multipliziert mit Wert
    pos++;
  }
  return sum;
};
```

#### Schritt 4: Bildsignatur-Integration (optional)
```typescript
if (useImageSignature && imageSignature) {
  const cleanSig = normalize(imageSignature);
  const imgPrimary = computePrimarySum(cleanSig);
  primarySum = Math.floor((primarySum + imgPrimary) / 2);
}
```

#### Schritt 5: Baserate & Fibonacci-Modulation
```typescript
const baseRate = primarySum * 1000;

// Feste Modulation (Original Copen)
fibonacciRate = Math.floor((baseRate / 21) * 34);

// ODER: Adaptive Modulation
const fibonacciPair = getAdaptiveFibonacciPair(wordLength);
fibonacciRate = Math.floor((baseRate / fibonacciPair.div) * fibonacciPair.mult);
```

**Adaptive Fibonacci-Paare:**
| Wortlänge | Fibonacci-Paar | Verhältnis |
|-----------|----------------|------------|
| 1-4       | 13/21          | ≈ 1.615    |
| 5-10      | 21/34          | ≈ 1.619    |
| 11-20     | 34/55          | ≈ 1.618    |
| >20       | 55/89          | ≈ 1.618    |

#### Schritt 6: Potenz-Bonus
```typescript
switch (potencyType) {
  case 'D':  potencyBonus = Math.floor(fibonacciRate * (potency / 10));  break;
  case 'C':  potencyBonus = Math.floor(fibonacciRate * (potency / 5));   break;
  case 'LM': potencyBonus = Math.floor(fibonacciRate * (potency / 2));   break;
  case 'M':  potencyBonus = Math.floor(fibonacciRate * potency);         break;
  case 'F1': potencyBonus = Math.floor(fibonacciRate * (potency / 6));   break;
  case 'F2': potencyBonus = Math.floor(fibonacciRate * (potency / 4));   break;
  case 'F3': potencyBonus = Math.floor(fibonacciRate * (potency / 3));   break;
}

const finalRate = fibonacciRate + potencyBonus;
```

---

### 4.2 Klienten-Rate-Berechnung

```typescript
const calculateClientRate = (patient: CloudPatient, useImageSig: boolean = true): number => {
  let clientData = `${patient.first_name} ${patient.last_name} ${patient.birth_date} ${patient.birth_place}`;
  
  if (useImageSig && patient.image_signature_active && patient.image_signature) {
    clientData += ` ${patient.image_signature}`;
  }
  
  // Normalisierung
  const normalizedData = clientData
    .toUpperCase()
    .replace(/Ä/g, 'AE').replace(/Ö/g, 'OE').replace(/Ü/g, 'UE').replace(/ß/g, 'SS')
    .replace(/[^A-Z0-9]/g, '');
  
  // Positions-gewichtete Summe
  let sum = 0;
  let position = 1;
  for (const char of normalizedData) {
    let value = 0;
    if (char >= 'A' && char <= 'Z') value = char.charCodeAt(0) - 64;
    else if (char >= '0' && char <= '9') value = parseInt(char, 10);
    sum += value * position;
    position++;
  }
  
  const clientBaseRate = sum * 1000;
  return Math.floor((clientBaseRate / 21) * 34);  // Fibonacci-Modulation
};
```

---

### 4.3 Resonanzanalyse-Engine (`resonanceAnalysis.ts`)

#### Level-Gewichte (1-12)
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
```

#### Fisher-Yates Shuffle (Selektion)
```typescript
function fisherYatesShuffle<T>(array: T[], quantumSeed?: number): T[] {
  const shuffled = [...array];
  
  const getRandom = () => {
    if (quantumSeed !== undefined) {
      return (Math.random() + quantumSeed) / 2;  // Hardware-Entropie
    }
    return Math.random();
  };
  
  for (let i = shuffled.length - 1; i > 0; i--) {
    const j = Math.floor(getRandom() * (i + 1));
    [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
  }
  return shuffled;
}
```

#### Gewichtete Level-Auswahl
```typescript
function weightedPickLevel(): number {
  const r = Math.random() * TOTAL_WEIGHT;
  let cumulative = 0;
  
  for (const { level, weight } of LEVEL_WEIGHTS) {
    cumulative += weight;
    if (r < cumulative) return level;
  }
  return 1;
}
```

#### Selektion
```typescript
function selectRates(
  rates: Array<{ name: string; copenRate: number }>,
  config: AnalysisConfig,
  quantumSeed?: number
): Array<{ name: string; copenRate: number }> {
  const targetCount = Math.ceil(rates.length * config.selectionFraction);
  const actualCount = Math.max(
    config.minSelection,
    Math.min(config.maxSelection, targetCount)
  );
  
  const shuffled = fisherYatesShuffle(rates, quantumSeed);
  return shuffled.slice(0, actualCount);
}
```

#### Energetisches Laden
```typescript
function chargeRates(
  selectedRates: Array<{ name: string; copenRate: number }>,
  threshold: number
): { energies: Record<string, number>; trials: number } {
  const energies: Record<string, number> = {};
  selectedRates.forEach(rate => { energies[rate.name] = 0; });
  
  let trials = 0;
  let maxEnergy = 0;
  
  while (maxEnergy < threshold) {
    selectedRates.forEach(rate => {
      const boost = Math.floor(Math.random() * 10);  // 0-9
      energies[rate.name] += boost;
      maxEnergy = Math.max(maxEnergy, energies[rate.name]);
    });
    trials++;
    if (trials > 10000) break;  // Sicherheit
  }
  
  return { energies, trials };
}
```

#### Potenz- und Level-Zuweisung
```typescript
function assignPotencyAndLevels(rateName: string): {
  potency: number;
  potencyType: 'D' | 'C' | 'LM' | 'M' | 'F1' | 'F2' | 'F3';
  levelDistribution: Record<number, number>;
  dominantLevel: number;
} {
  // 1. Gewichtete Ebene
  const levelValue = weightedPickLevel();
  
  // 2. Potenzreihe (gewichtete Auswahl)
  const potencyTypes = ['D', 'C', 'LM', 'M', 'F1', 'F2', 'F3'];
  const potencyTypeWeights = [30, 25, 20, 15, 5, 3, 2];
  // ... gewichtete Auswahl ...
  
  // 3. Potenzwerte nach Typ
  switch (selectedPotencyType) {
    case 'D':  actualPotency = Math.floor(Math.random() * 100) + 1;  break;  // 1-100
    case 'C':  actualPotency = Math.floor(Math.random() * 200) + 1;  break;  // 1-200
    case 'LM': actualPotency = Math.floor(Math.random() * 30) + 1;   break;  // 1-30
    case 'M':  /* Logarithmisch 1 - 100.000.000 */                   break;
    case 'F1': /* Logarithmisch 10^6 - 10^13 */                      break;
    case 'F2': /* Logarithmisch 10^8 - 10^15 */                      break;
    case 'F3': /* Logarithmisch 10^10 - 10^16 */                     break;
  }
  
  // 4. Level-Verteilung: 100 Ziehungen
  const levelDistribution: Record<number, number> = {};
  for (let i = 1; i <= 12; i++) levelDistribution[i] = 0;
  for (let i = 0; i < 100; i++) {
    const level = weightedPickLevel();
    levelDistribution[level]++;
  }
  
  // 5. Dominante Ebene = Maximum
  let dominantLevel = levelValue;
  let maxCount = levelDistribution[levelValue];
  for (let level = 1; level <= 12; level++) {
    if (levelDistribution[level] > maxCount) {
      maxCount = levelDistribution[level];
      dominantLevel = level;
    }
  }
  
  return { potency: actualPotency, potencyType: selectedPotencyType, levelDistribution, dominantLevel };
}
```

#### Haupt-Analyse-Funktion
```typescript
export function analyzeRates(
  rates: Array<{ name: string; copenRate: number }>,
  config: AnalysisConfig
): AnalysisResult {
  // 1. Selektion
  const selected = selectRates(rates, config);
  
  // 2. Energetisches Laden
  const { energies, trials } = chargeRates(selected, config.chargingThreshold);
  
  // 3. RateObjects erstellen
  const rateObjects: RateObject[] = selected.map(rate => {
    const { potency, potencyType, levelDistribution, dominantLevel } = assignPotencyAndLevels(rate.name);
    return {
      rateName: rate.name,
      copenRate: rate.copenRate,
      energeticValue: energies[rate.name],
      potency, potencyType, levelDistribution, dominantLevel,
    };
  });
  
  // 4. Sortieren nach energeticValue
  rateObjects.sort((a, b) => b.energeticValue - a.energeticValue);
  
  // 5. Optional kürzen
  const finalRates = config.maxEntries ? rateObjects.slice(0, config.maxEntries) : rateObjects;
  
  return { rateObjects: finalRates, numberOfTrials: trials };
}
```

**Standard-Konfiguration für DB-Analyse:**
```typescript
const analysisConfig = {
  selectionFraction: 1,        // ALLE Einträge
  minSelection: 1,
  maxSelection: 10000,
  chargingThreshold: 100,
  maxEntries: 200,             // Max 200 Ergebnisse
};
```

---

### 4.4 13-Ebenen-Kosmologie (`levelResonance.ts`)

```typescript
export const LEVELS: Level[] = [
  { id: 1, name: "Physical Realm - Particles", germanName: "Physische Ebene - Partikel",
    keywords: ["atom", "partikel", "molekül", "dna"], frequencyRange: { min: 1, max: 100000 } },
  { id: 2, name: "Physical Realm - Structure", germanName: "Physische Ebene - Struktur",
    keywords: ["körper", "organ", "gewebe"], frequencyRange: { min: 100000, max: 500000 } },
  { id: 3, name: "Etheric Realm - Prana", germanName: "Ätherische Ebene - Prana",
    keywords: ["prana", "qi", "lebenskraft"], frequencyRange: { min: 500000, max: 1000000 } },
  { id: 4, name: "Etheric Realm - Meridians", germanName: "Ätherische Ebene - Meridiane",
    keywords: ["meridian", "chakra", "nadis"], frequencyRange: { min: 1000000, max: 2000000 } },
  { id: 5, name: "Astral Realm - Emotions", germanName: "Astrale Ebene - Emotionen",
    keywords: ["emotion", "gefühl"], frequencyRange: { min: 2000000, max: 3500000 } },
  { id: 6, name: "Astral Realm - Thought-Forms", germanName: "Astrale Ebene - Gedankenformen",
    keywords: ["gedanke", "thought"], frequencyRange: { min: 3500000, max: 5000000 } },
  { id: 7, name: "Mental Realm - Time", germanName: "Mentale Ebene - Zeit",
    keywords: ["zeit", "time", "raum"], frequencyRange: { min: 5000000, max: 7000000 } },
  { id: 8, name: "Mental Realm - Mental Constructs", germanName: "Mentale Ebene - Mentale Konstrukte",
    keywords: ["konzept", "idee"], frequencyRange: { min: 7000000, max: 9000000 } },
  { id: 9, name: "Causal Plane - Blueprints", germanName: "Kausale Ebene - Blaupausen",
    keywords: ["akasha", "blueprint"], frequencyRange: { min: 9000000, max: 11000000 } },
  { id: 10, name: "Causal Plane - Alchemy", germanName: "Kausale Ebene - Alchemie",
    keywords: ["intention", "alchemie"], frequencyRange: { min: 11000000, max: 13000000 } },
  { id: 11, name: "Atmic Plane - Identity", germanName: "Atmische Ebene - Identität",
    keywords: ["identität", "essenz"], frequencyRange: { min: 13000000, max: 16000000 } },
  { id: 12, name: "Atmic Plane - Love & Unity", germanName: "Atmische Ebene - Liebe & Einheit",
    keywords: ["liebe", "einheit"], frequencyRange: { min: 16000000, max: 20000000 } },
  { id: 13, name: "Creator - Divinity", germanName: "Schöpfer - Göttlichkeit",
    keywords: ["creator", "schöpfer", "göttlich"], frequencyRange: { min: 20000000, max: Infinity } }
];
```

#### Level-Resonanz-Berechnung
```typescript
export function calculateLevelResonance(copenRate: number, word: string): Record<string, number> {
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

    // 2. Keyword-Bonus (+25% pro Match)
    let keywordBonus = 0;
    level.keywords.forEach(keyword => {
      if (normalizedWord.includes(keyword.toLowerCase())) {
        keywordBonus += 25;
      }
    });

    resonance[`level_${level.id}`] = parseFloat(Math.min(100, baseResonance + keywordBonus).toFixed(2));
  });

  return resonance;
}
```

---

### 4.5 Hardware-Algorithmen (`hardwareAlgorithms.ts`)

#### Metriken
```typescript
interface HardwareMetrics {
  cpuQuantumJitter: number;      // CPU-Timing-Varianz
  ramEntropy: number;            // Speicher-Fragmentierung
  timeSourceCoherence: number;   // Zeit-Kohärenz (Kozyrev)
  gpuRenderingEntropy: number;   // GPU-Rendering-Varianz
  networkLatency: number;        // Netzwerk-Jitter
  combinedScore: number;         // Gewichtete Kombination
}
```

#### Gewichtung (nach Kozyrev-Theorie)
```typescript
const weights = {
  timeSourceCoherence: 0.30,    // Höchste Priorität
  cpuQuantumJitter: 0.25,
  gpuRenderingEntropy: 0.20,
  ramEntropy: 0.15,
  networkLatency: 0.10
};
```

#### CPU Quantum Jitter
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
  return Math.min(1.0, Math.sqrt(variance) / 0.1);
}
```

---

### 4.6 LLM-Interpretation (`analysisInterpreter.ts`)

```typescript
export async function interpretAnalysisResults(
  results: Array<{word: string; resonanceScore: number; highestLevel: number; testedPotency: string}>,
  patientName?: string
): Promise<AnalysisInterpretation> {
  try {
    // Ollama LLM Anfrage
    const response = await fetch('http://localhost:11434/api/generate', {
      method: 'POST',
      body: JSON.stringify({ model: 'llama2', prompt: context, stream: false })
    });
    // Parse Response...
  } catch (error) {
    // Fallback: Regel-basierte Interpretation
    return {
      summary: `${results.length} Einträge analysiert`,
      insights: [`Höchste Resonanz: "${results[0].word}"`],
      recommendations: ['Konzentriere dich auf Top-5 Resonanzen']
    };
  }
}
```

---

## 5. Datenbank-Import & Parsing

### parseImportData()
```typescript
const parseImportData = (data: string): string[] => {
  const lines = data.trim().split('\n');
  const entries: string[] = [];

  // CSV-Erkennung
  const looksLikeCsvRecord = (line: string) => {
    const parts = line.split(',').map(p => p.trim());
    if (parts.length < 3) return false;
    const potencyNum = parseInt(parts[1], 10);
    const type = (parts[2] || '').toUpperCase();
    return !isNaN(potencyNum) && ['D', 'C', 'LM', 'M'].includes(type);
  };

  const anyCsv = lines.some(l => looksLikeCsvRecord(l));

  for (const raw of lines) {
    const line = raw.trim();
    if (line.length === 0) continue;

    if (anyCsv) {
      // CSV-Modus: Potenz-Zahlen konvertieren
      const parts = line.split(',').map(p => p.trim());
      parts[0] = convertPotencyNumbersToWords(parts[0]);
      entries.push(parts.join(','));
    } else {
      // TXT-Modus: Zeile = Datensatz
      entries.push(convertPotencyNumbersToWords(line));
    }
  }

  return [...new Set(entries)];  // Deduplizieren
};
```

### Potenz-Konvertierung
```typescript
// D6 → Dsechs, C100 → CEinhundert
export const convertPotencyNumbersToWords = (text: string): string => {
  const potencyPattern = /\b([DCLM]+)(\d+)\b/gi;
  return text.replace(potencyPattern, (match, type, numStr) => {
    const num = parseInt(numStr, 10);
    let wordNum = numberToGermanWords(num);
    if (num >= 100) wordNum = wordNum.charAt(0).toUpperCase() + wordNum.slice(1);
    return `${type.toUpperCase()}${wordNum}`;
  });
};
```

---

## 6. Analyse-Workflow (handleAnalyzeDatabase)

```typescript
const handleAnalyzeDatabase = () => {
  // 1. Validierung
  if (!selectedPatient || !importData.trim()) return;

  setIsAnalyzing(true);
  let words = parseImportData(importData);
  
  // 2. Optional: Fokus-Wort priorisieren
  if (focusWord.trim()) {
    words = [focusWord.trim(), ...words.filter(w => w.toLowerCase() !== focusWord.toLowerCase())];
  }
  
  // 3. Klienten-Rate berechnen
  const clientRate = calculateClientRate(selectedPatient);
  
  // 4. Rates-Array erstellen
  const ratesInput = words.map(word => {
    const parts = word.split(',').map(p => p.trim());
    const hasExistingRate = parts.length >= 2 && !isNaN(Number(parts[1]));
    
    if (hasExistingRate) {
      return { name: parts[0], copenRate: Number(parts[1]), hasExistingRate: true };
    } else {
      const result = calculateCopenRate(word, 30, 'D', 'latin', imgSig, useImgSig);
      return { name: word, copenRate: result.rate, hasExistingRate: false };
    }
  });

  // 5. Java-Algorithmus ausführen
  const analysisResult = analyzeRates(ratesInput, analysisConfig);
  
  // 6. ResonanceResults erstellen
  const results: ResonanceResult[] = analysisResult.rateObjects.map(rateObj => {
    const calculatedRate = hasExistingRate 
      ? { rate: rateObj.copenRate } 
      : calculateCopenRate(rateObj.rateName, rateObj.potency, rateObj.potencyType, ...);
    
    const levelResonance = calculateLevelResonance(calculatedRate.rate, rateObj.rateName);
    const { level, value } = findHighestResonanceLevel(levelResonance);
    
    return {
      word: rateObj.rateName,
      potency: rateObj.potency,
      potencyType: rateObj.potencyType,
      rate: calculatedRate.rate,
      resonanceScore: Math.min(100, Math.round((rateObj.energeticValue / 100) * 100)),
      clientResonance: clientRate,
      levelResonance,
      highestLevel: rateObj.dominantLevel,
      highestLevelValue: rateObj.levelDistribution[rateObj.dominantLevel],
    };
  });
  
  setResonanceResults(results);
  
  // 7. LLM-Interpretation (async, nicht-blockierend)
  interpretAnalysisResults(results.map(...)).then(setInterpretation);
};
```

---

## 7. Harmonisierungs-Übergabe

### Aus Analyseergebnissen
```typescript
const inserts = selectedResults.map(r => ({
  user_id: user.id,
  patient_id: selectedPatient.id,
  word: `Harmonisierung mit ${r.rate.toLocaleString('de-DE')}`,
  copen_rate: r.rate.toString(),
  tested_potency: null,
  duration_seconds: durationSeconds,
  remaining_seconds: durationSeconds,
  status: 'pending',
  pulse_seconds: pulseInSeconds,
  pause_seconds: pauseInSeconds,
  pulse_pause_active: pulsePauseActive,
}));

await supabase.from('harmonization_sessions_v2').insert(inserts);
await supabase.functions.invoke('harmonization-worker');
```

### Direkte Raten-Harmonisierung
```typescript
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
  // ... weitere Felder
}));
```

---

## 8. Export-Funktionen

### CSV/TXT
```typescript
const exportResults = (format: 'csv' | 'txt' | 'pdf') => {
  if (format === 'csv') {
    content = 'Wortenergie,Potenz,Typ,Copen-Rate,Resonanz-Score,Klienten-Rate\n';
    content += resonanceResults.map(r => 
      `${r.word},${r.potency},${r.potencyType},${r.rate},${r.resonanceScore},${r.clientResonance}`
    ).join('\n');
  }
  // ... Blob erstellen und Download
};
```

### PDF mit jsPDF
```typescript
if (format === 'pdf') {
  const doc = new jsPDF({ orientation: 'landscape' });
  doc.text(title, 14, 14);
  
  autoTable(doc, {
    head: [["Wortenergie", "Potenz", "Copen-Rate", "Resonanz", "Höchste Ebene"]],
    body: resonanceResults.map(r => [...]),
    // ... Styling
  });
  
  doc.save(`resonanz-analyse-${Date.now()}.pdf`);
}
```

---

## 9. Datenbank-Verwaltung

### Speichern
```typescript
const handleSaveDatabase = async () => {
  const entries = parseImportData(importData);
  await supabase.from('word_databases').insert({
    user_id: user.id,
    name: databaseName,
    entries: entries,
  });
};
```

### Laden
```typescript
const loadSavedDatabases = async () => {
  const { data } = await supabase
    .from('word_databases')
    .select('id,name,entries')
    .order('created_at', { ascending: false });
  setSavedDatabases(data || []);
};
```

---

## 10. UI-Komponenten

### Spalten-Resize
```typescript
const [columnSizes, setColumnSizes] = useState<ColumnSize>({
  word: 420, potency: 90, rate: 160, resonance: 120, level: 160, actions: 120
});

const startResize = (key: keyof ColumnSize, e: React.MouseEvent) => {
  setResizing({ key, startX: e.clientX, startWidth: columnSizes[key] });
};

// Mouse move handler
const dx = ev.clientX - resizing.startX;
const newWidth = Math.max(80, resizing.startWidth + dx);
setColumnSizes(prev => ({ ...prev, [resizing.key!]: newWidth }));
```

### Sortierung
```typescript
const sortedResults = React.useMemo(() => {
  if (!sortBy) return resonanceResults;
  
  return [...resonanceResults].sort((a, b) => {
    let compareValue = 0;
    switch (sortBy) {
      case 'resonance': compareValue = a.resonanceScore - b.resonanceScore; break;
      case 'level': compareValue = (a.highestLevel || 0) - (b.highestLevel || 0); break;
      case 'potency': compareValue = a.potency - b.potency; break;
    }
    return sortOrder === 'asc' ? compareValue : -compareValue;
  });
}, [resonanceResults, sortBy, sortOrder]);
```

---

## 11. Supabase-Tabellen

### word_databases
```sql
CREATE TABLE public.word_databases (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL,
  name TEXT NOT NULL,
  entries TEXT[] NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);
```

### analysis_archives_v2
```sql
CREATE TABLE public.analysis_archives_v2 (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL,
  patient_id UUID,
  word TEXT NOT NULL,
  copen_rate TEXT NOT NULL,
  tested_potency TEXT,
  level_1_physical_particles NUMERIC,
  level_2_physical_structure NUMERIC,
  -- ... level_3 bis level_13 ...
  highest_resonance_level INTEGER,
  highest_resonance_value NUMERIC,
  patient_data JSONB,
  database_entries TEXT[],
  analysis_timestamp TIMESTAMPTZ DEFAULT now(),
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);
```

### harmonization_sessions_v2
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
  status TEXT DEFAULT 'pending',
  pulse_seconds INTEGER,
  pause_seconds INTEGER,
  pulse_pause_active BOOLEAN DEFAULT false,
  started_at TIMESTAMPTZ,
  completed_at TIMESTAMPTZ,
  job_started_at TIMESTAMPTZ,
  job_last_heartbeat TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);
```

---

## 12. Wiederherstellungs-Checkliste

1. **Dateien erstellen:**
   - `src/utils/alphabetSystems.ts`
   - `src/utils/potencyText.ts`
   - `src/utils/copenRateGenerator.ts`
   - `src/utils/levelResonance.ts`
   - `src/utils/resonanceAnalysis.ts`
   - `src/utils/hardwareAlgorithms.ts`
   - `src/utils/analysisInterpreter.ts`
   - `src/components/DatabaseManager.tsx`

2. **Supabase-Tabellen migrieren:**
   - `word_databases`
   - `analysis_archives_v2`
   - `harmonization_sessions_v2`

3. **Dependencies sicherstellen:**
   - `jspdf`, `jspdf-autotable` für PDF-Export
   - Supabase Client konfiguriert

4. **Edge Function deployen:**
   - `harmonization-worker`

---

## 13. Berechnungsbeispiel

**Eingabe:** "ARNICA", Patient "Max Mustermann, 01.01.1990, Berlin"

1. **Klienten-Rate:**
   - Normalisiert: `MAXMUSTERMANN01011990BERLIN`
   - Primärsumme: Σ(Wert × Position)
   - BaseRate = Summe × 1000
   - Fibonacci: ⌊(BaseRate / 21) × 34⌋ = **z.B. 12.345.678**

2. **Wort-Rate "ARNICA":**
   - Normalisiert: `ARNICA`
   - A=1×1, R=18×2, N=14×3, I=9×4, C=3×5, A=1×6 = 1+36+42+36+15+6 = 136
   - BaseRate = 136 × 1000 = 136.000
   - Fibonacci = ⌊(136.000 / 21) × 34⌋ = 220.190
   - Mit Potenz D30: Bonus = ⌊220.190 × (30/10)⌋ = 660.570
   - **Final Rate = 880.760**

3. **Resonanzanalyse:**
   - Energetisches Laden bis Threshold 100
   - Potenz automatisch: z.B. D45
   - Level-Verteilung: 100 Ziehungen → Dominant Ebene 3

4. **Level-Resonanz:**
   - Rate 880.760 liegt im Bereich Physical (1-100.000) → 40% Basis
   - Keine Keyword-Matches → 40% gesamt

---

*Ende der Entwickler-Dokumentation*
