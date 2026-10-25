# Bruce Copen Raten-Generator - Vollständige Dokumentation

**Version:** 3.0  
**Stand:** 2025-01-29  
**Algorithmus-Standard:** Modernisierter Bruce Copen mit 13+1 Ebenen-Resonanz

---

## 1. ÜBERSICHT & ARCHITEKTUR

### 1.1 Systemkomponenten

Der Bruce Copen Raten-Generator besteht aus folgenden Hauptkomponenten:

```
Bruce Copen Raten-Generator
├── Core-Algorithmen
│   ├── copenRateGenerator.ts        → Hauptberechnungslogik
│   ├── alphabetSystems.ts            → Buchstabenwert-Systeme
│   ├── resonanceAnalysis.ts          → 13-Ebenen Resonanzanalyse
│   ├── levelResonance.ts             → Level-spezifische Resonanzberechnung
│   └── potencyText.ts                → Potenz-zu-Text Konvertierung
│
├── UI-Komponenten
│   ├── CopenRateGenerator.tsx        → Standalone-Generator
│   ├── forms/
│   │   ├── SingleCalculationForm.tsx → Einzelberechnung
│   │   ├── BatchImportForm.tsx       → CSV-Batch-Import
│   │   └── FileImportForm.tsx        → PDF/Bild-OCR-Import
│   └── tables/
│       └── ResultsTable.tsx          → Ergebnisanzeige
│
├── Page-Integration
│   └── CopenGeneratorPage.tsx        → Cloud-Integration mit Harmonisierung
│
└── Dokumentation
    └── Bruce_Copen_Algorithmus_Dokumentation.md
```

### 1.2 Datenfluss

```
┌─────────────────────┐
│   Wortenergie       │
│   + Potenz          │
│   + Potenztyp       │
│   + Alphabet        │
└──────────┬──────────┘
           ↓
┌──────────────────────────────────────────┐
│  calculateCopenRate()                    │
│  --------------------------------        │
│  1. Normalisierung                       │
│  2. Buchstabenwerte & Position           │
│  3. Primärsumme                          │
│  4. Baserate (× 1000)                    │
│  5. Fibonacci-Modulation (34/21)         │
│  6. Potenz-Bonus                         │
│  7. Finale Rate                          │
└──────────┬───────────────────────────────┘
           ↓
┌──────────────────────────────────────────┐
│  analyzeRates()                          │
│  --------------------------------        │
│  1. Selektion (10%)                      │
│  2. Energetisches Laden                  │
│  3. Level-Verteilung (1-12)              │
│  4. Dominante Ebene                      │
│  5. Potenzreihen-Zuweisung              │
└──────────┬───────────────────────────────┘
           ↓
┌──────────────────────────────────────────┐
│  calculateLevelResonance()               │
│  --------------------------------        │
│  1. Frequenzbasierte Resonanz            │
│  2. Keyword-basierte Resonanz            │
│  3. 13+1 Ebenen-Bewertung                │
└──────────┬───────────────────────────────┘
           ↓
┌──────────────────────────────────────────┐
│  CopenRateResult                         │
│  {                                       │
│    word, potency, potencyType,           │
│    rate, alphabetType, calculation       │
│  }                                       │
└──────────────────────────────────────────┘
```

---

## 2. KERN-ALGORITHMUS (copenRateGenerator.ts)

### 2.1 CopenRateResult Interface

```typescript
export interface CopenRateResult {
  word: string;                    // Eingabe-Wortenergie
  potency: number;                 // Potenzwert (0-50000)
  potencyType: 'D' | 'C' | 'LM' | 'M' | 'F1' | 'F2' | 'F3';
  rate: number;                    // Berechnete Copen-Rate
  alphabetType: AlphabetType;      // Verwendetes Alphabet
  calculation: {
    letterSum: number;             // Primärsumme
    baseRate: number;              // Baserate (× 1000)
    fibonacciRate: number;         // Nach Fibonacci-Modulation
  };
}
```

### 2.2 Schritt-für-Schritt Algorithmus

#### Schritt 1: Normalisierung

```typescript
const normalize = (w: string) =>
  w.toUpperCase()
   .replace(/Ä/g, 'AE')           // Umlaute standardisieren
   .replace(/Ö/g, 'OE')
   .replace(/Ü/g, 'UE')
   .replace(/ß/g, 'SS')
   .replace(/\s*[DCLM]+\d+/g, '') // Potenzangaben entfernen
   .replace(/\d+/g, '')            // Zahlen entfernen
   .replace(/[^A-Z\s]/g, '')       // Sonderzeichen entfernen
   .replace(/\s+/g, ' ')           // Mehrfache Leerzeichen
   .trim();
```

**Beispiele:**
- `"Nux vomica D6"` → `"NUX VOMICA"`
- `"Schüßler Nr.1"` → `"SCHUESSLER NR"`
- `"Ärgerlich C30"` → `"AERGERLICH"`

#### Schritt 2: Buchstabenwerte mit Positionsgewichtung

```typescript
const getLetterValue = (ch: string) => ch.charCodeAt(0) - 64; // A=1..Z=26

const computePrimarySum = (text: string) => {
  let sum = 0;
  let pos = 1;
  for (const ch of text) {
    if (ch === ' ') continue;  // Leerzeichen überspringen
    sum += getLetterValue(ch) * pos;
    pos++;
  }
  return sum;
};
```

**Beispiel "NUX VOMICA":**
```
N (Position 1): 14 × 1 = 14
U (Position 2): 21 × 2 = 42
X (Position 3): 24 × 3 = 72
  (Leerzeichen überspringen)
V (Position 4): 22 × 4 = 88
O (Position 5): 15 × 5 = 75
M (Position 6): 13 × 6 = 78
I (Position 7):  9 × 7 = 63
C (Position 8):  3 × 8 = 24
A (Position 9):  1 × 9 = 9

Primärsumme = 465
```

#### Schritt 3: Bildsignatur-Integration (Optional)

```typescript
if (useImageSignature && imageSignature && imageSignature.trim().length > 0) {
  const cleanSig = normalize(imageSignature);
  const imgPrimary = computePrimarySum(cleanSig);
  const original = primarySum;
  primarySum = Math.floor((primarySum + imgPrimary) / 2);
  // Arithmetisches Mittel aus Wort-Primärsumme und Bildsignatur-Primärsumme
}
```

#### Schritt 4: Baserate

```typescript
const baseRate = primarySum * 1000;
```

**Beispiel:**
```
Baserate = 465 × 1000 = 465.000
```

#### Schritt 5: Fibonacci-Modulation

```typescript
const fibonacciRate = Math.floor((baseRate / 21) * 34);
```

**Mathematischer Hintergrund:**
- Fibonacci-Zahlen: F₈ = 21, F₉ = 34
- Verhältnis 34/21 ≈ 1,619 (Goldener Schnitt φ)
- Biologische Resonanz durch natürliche Proportionen

**Beispiel:**
```
Fibonacci-Rate = ⌊(465.000 ÷ 21) × 34⌋ = ⌊752.857⌋ = 752.857
```

#### Schritt 6: Potenz-Bonus

```typescript
let potencyBonus = 0;
const p = Math.max(0, potency);

if (p > 0) {
  switch (potencyType) {
    case 'D':   potencyBonus = Math.floor(fibonacciRate * (p / 10)); break;
    case 'C':   potencyBonus = Math.floor(fibonacciRate * (p / 5));  break;
    case 'LM':  potencyBonus = Math.floor(fibonacciRate * (p / 2));  break;
    case 'M':   potencyBonus = Math.floor(fibonacciRate * p);        break;
    case 'F1':  potencyBonus = Math.floor(fibonacciRate * (p / 6));  break;
    case 'F2':  potencyBonus = Math.floor(fibonacciRate * (p / 4));  break;
    case 'F3':  potencyBonus = Math.floor(fibonacciRate * (p / 3));  break;
  }
}
```

**Potenz-Faktoren-Tabelle:**

| Potenztyp | Faktor | Verdünnungsreihe | Beispiel |
|-----------|--------|------------------|----------|
| **D** (Dezimal) | p / 10 | 1:10 | D6 → 0,6× |
| **C** (Centesimal) | p / 5 | 1:100 | C30 → 6× |
| **LM** (50-Millesimal) | p / 2 | 1:50.000 | LM12 → 6× |
| **M** (Millennial) | p | 1MM-100MM | M1000 → 1000× |
| **F1** (Fibonacci Stufe 1) | p / 6 | 1MM-10C-MMMM | F1 6000000 → 1.000.000× |
| **F2** (Fibonacci Stufe 2) | p / 4 | 100MM-1CC-MMMM | F2 500000000 → 125.000.000× |
| **F3** (Fibonacci Stufe 3) | p / 3 | 10C-MM-10MMMMMM | F3 30000000000 → 10.000.000.000× |

**Spezialfall D0/C0 (Ursubstanz/Urtinktur):**
```typescript
if (potency === 0) {
  potencyBonus = 0; // Keine Potenzierung
}
```

#### Schritt 7: Finale Rate

```typescript
const finalRate = fibonacciRate + potencyBonus;
```

### 2.3 Vollständige Berechnungsformel

```
Rate = ⌊((Σ(Buchstabenwert × Position) × 1000) ÷ 21) × 34⌋ + Potenz-Bonus

wobei:
  Primärsumme = Σ(Buchstabenwert × Position)
  Baserate = Primärsumme × 1000
  Fibonacci-Rate = ⌊(Baserate ÷ 21) × 34⌋
  Potenz-Bonus = Fibonacci-Rate × Potenz-Faktor
```

### 2.4 Praktische Rechenbeispiele

#### Beispiel 1: "NUX VOMICA" D6

```
1. Normalisierung:     "NUX VOMICA D6" → "NUX VOMICA"
2. Primärsumme:        465
3. Baserate:           465.000
4. Fibonacci-Rate:     752.857
5. Potenz-Bonus (D6):  752.857 × 0,6 = 451.714
6. Finale Rate:        752.857 + 451.714 = 1.204.571
```

#### Beispiel 2: "ARNICA" C30

```
1. Normalisierung:     "ARNICA"
2. Buchstabenwerte:    A(1)×1, R(18)×2, N(14)×3, I(9)×4, C(3)×5, A(1)×6
                       = 1 + 36 + 42 + 36 + 15 + 6 = 136
3. Baserate:           136.000
4. Fibonacci-Rate:     220.190
5. Potenz-Bonus (C30): 220.190 × 6 = 1.321.140
6. Finale Rate:        220.190 + 1.321.140 = 1.541.330
```

#### Beispiel 3: "HEILUNG" D0 (Ursubstanz)

```
1. Normalisierung:     "HEILUNG"
2. Primärsumme:        H(8)×1 + E(5)×2 + I(9)×3 + L(12)×4 + U(21)×5 + N(14)×6 + G(7)×7
                       = 8 + 10 + 27 + 48 + 105 + 84 + 49 = 331
3. Baserate:           331.000
4. Fibonacci-Rate:     535.619
5. Potenz-Bonus (D0):  0 (Ursubstanz)
6. Finale Rate:        535.619
```

---

## 3. ALPHABET-SYSTEME (alphabetSystems.ts)

### 3.1 AlphabetType Definition

```typescript
export type AlphabetType = 
  | 'latin'                      // Standard A=1..Z=26
  | 'altdeutsch-gotisch'         // Fraktur mit Ä,Ö,Ü,ß
  | 'altdeutsch-mittelhochdeutsch' // Historisch ohne J,Q,V,X,Y
  | 'runisch';                   // Elder Futhark (24 Zeichen)
```

### 3.2 Alphabet-Systeme im Detail

#### 3.2.1 Lateinisches Alphabet (Standard)

```typescript
'latin': {
  name: 'Lateinisches Alphabet',
  description: 'Standard A=1, B=2, C=3... (Original Copen)',
  letterValues: {
    'A': 1,  'B': 2,  'C': 3,  'D': 4,  'E': 5,  'F': 6,  
    'G': 7,  'H': 8,  'I': 9,  'J': 10, 'K': 11, 'L': 12,
    'M': 13, 'N': 14, 'O': 15, 'P': 16, 'Q': 17, 'R': 18,
    'S': 19, 'T': 20, 'U': 21, 'V': 22, 'W': 23, 'X': 24,
    'Y': 25, 'Z': 26
  }
}
```

#### 3.2.2 Altdeutsch (Gotische Schrift)

```typescript
'altdeutsch-gotisch': {
  name: 'Altdeutsch (Gotische Schrift)',
  description: 'Fraktur-Alphabet mit 26 Buchstaben',
  letterValues: {
    // A-Z wie Standard (1-26)
    'Ä': 27, 'Ö': 28, 'Ü': 29, 'ß': 30
  }
}
```

#### 3.2.3 Altdeutsch (Mittelhochdeutsch)

```typescript
'altdeutsch-mittelhochdeutsch': {
  name: 'Altdeutsch (Mittelhochdeutsch)',
  description: 'Historisches Alphabet ohne J,Q,V,X,Y (21 Buchstaben)',
  letterValues: {
    'A': 1,  'B': 2,  'C': 3,  'D': 4,  'E': 5,  'F': 6,
    'G': 7,  'H': 8,  'I': 9,  'K': 10, 'L': 11, 'M': 12,
    'N': 13, 'O': 14, 'P': 15, 'R': 16, 'S': 17, 'T': 18,
    'U': 19, 'W': 20, 'Z': 21, 'Ä': 22, 'Ö': 23, 'Ü': 24
  }
}
```

#### 3.2.4 Runenschrift (Elder Futhark)

```typescript
'runisch': {
  name: 'Runenschrift (Elder Futhark)',
  description: 'Germanische Runen mit 24 Zeichen',
  letterValues: {
    'F': 1,  'U': 2,  'TH': 3, 'A': 4,   'R': 5,  'K': 6,
    'G': 7,  'W': 8,  'H': 9,  'N': 10,  'I': 11, 'J': 12,
    'EI': 13, 'P': 14, 'Z': 15, 'S': 16, 'T': 17, 'B': 18,
    'E': 19, 'M': 20, 'L': 21, 'NG': 22, 'D': 23, 'O': 24
  }
}
```

### 3.3 Erweiterte Buchstabensumme mit Zahlenextraktion

```typescript
export const calculateLetterSum = (word: string, alphabetType: AlphabetType = 'latin'): number => {
  const system = alphabetSystems[alphabetType];
  
  // 1. Extrahiere Zahlenwerte aus dem Text (z.B. "Lade 800 Hertz")
  const numberMatches = word.match(/\d+/g);
  let numberSum = 0;
  if (numberMatches) {
    numberSum = numberMatches.reduce((sum, num) => sum + parseInt(num), 0);
  }
  
  // 2. Bereinige Wort
  const cleanWord = word.toUpperCase().replace(/[^A-ZÜÄÖ]/g, '');
  
  // 3. Berechne Buchstabensumme
  let sum = 0;
  for (const char of cleanWord) {
    const value = system.letterValues[char];
    if (value) sum += value;
  }
  
  // 4. Kombiniere Buchstabensumme mit Zahlenwerten
  return sum + numberSum;
}
```

**Beispiel:**
```
"Lade 800 Hertz" → Buchstabensumme + 800
```

---

## 4. RESONANZANALYSE (resonanceAnalysis.ts)

### 4.1 AnalysisConfig Interface

```typescript
export interface AnalysisConfig {
  selectionFraction: number;    // Standard 0.1 (10%)
  minSelection: number;          // Mindestanzahl Selektion
  maxSelection: number;          // Maximalanzahl Selektion
  chargingThreshold: number;     // Standard 100
  maxEntries?: number;           // Optional: Max. Ergebnisse
}
```

### 4.2 RateObject Interface

```typescript
export interface RateObject {
  rateName: string;                          // Original-Wortenergie
  copenRate: number;                         // Berechnete Rate
  energeticValue: number;                    // Energiewert (0-100+)
  potency: number;                           // Ermittelte Potenz (1-12)
  potencyType: 'D' | 'C' | 'LM' | 'M' | 'F1' | 'F2' | 'F3';
  levelDistribution: Record<number, number>; // Verteilung über 100 Ziehungen
  dominantLevel: number;                     // Ebene mit meisten Treffern (1-12)
}
```

### 4.3 Level-Gewichtung (1-12 Ebenen)

```typescript
const LEVEL_WEIGHTS = [
  { level: 1,  weight: 15 },  // Physical Particles
  { level: 2,  weight: 14 },  // Physical Structure
  { level: 3,  weight: 13 },  // Etheric Prana
  { level: 4,  weight: 12 },  // Etheric Meridians
  { level: 5,  weight: 11 },  // Astral Emotions
  { level: 6,  weight: 10 },  // Astral Thoughts
  { level: 7,  weight: 9  },  // Mental Time
  { level: 8,  weight: 8  },  // Mental Constructs
  { level: 9,  weight: 7  },  // Causal Blueprints
  { level: 10, weight: 6  },  // Causal Alchemy
  { level: 11, weight: 3  },  // Atmic Identity
  { level: 12, weight: 2  }   // Atmic Love
];

const TOTAL_WEIGHT = 120;
```

### 4.4 Analyse-Prozess

#### 4.4.1 Fisher-Yates Shuffle mit Quantum-Seed

```typescript
function fisherYatesShuffle<T>(array: T[], quantumSeed?: number): T[] {
  const shuffled = [...array];
  
  const getRandom = () => {
    if (quantumSeed !== undefined) {
      return (Math.random() + quantumSeed) / 2; // Hardware-Entropie
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

#### 4.4.2 Gewichtete Ebenenauswahl

```typescript
function weightedPickLevel(): number {
  const r = Math.random() * TOTAL_WEIGHT;
  let cumulative = 0;
  
  for (const { level, weight } of LEVEL_WEIGHTS) {
    cumulative += weight;
    if (r < cumulative) return level;
  }
  
  return 1; // Fallback
}
```

#### 4.4.3 Raten-Selektion (10%)

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

#### 4.4.4 Energetisches Laden

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
    
    if (trials > 10000) break; // Sicherheit
  }
  
  return { energies, trials };
}
```

#### 4.4.5 Potenzreihen-Zuweisung

```typescript
function assignPotencyAndLevels(rateName: string): {
  potency: number;
  potencyType: 'D' | 'C' | 'LM' | 'M' | 'F1' | 'F2' | 'F3';
  levelDistribution: Record<number, number>;
  dominantLevel: number;
} {
  // 1. Gewichtete Potenzreihen-Auswahl
  const potencyTypes = ['D', 'C', 'LM', 'M', 'F1', 'F2', 'F3'];
  const potencyTypeWeights = [30, 25, 20, 15, 5, 3, 2];
  
  // 2. Realistische Potenzwerte gemäß Spezifikation
  let actualPotency: number;
  
  switch (selectedPotencyType) {
    case 'D':   actualPotency = Math.floor(Math.random() * 100) + 1; break;
    case 'C':   actualPotency = Math.floor(Math.random() * 200) + 1; break;
    case 'LM':  actualPotency = Math.floor(Math.random() * 30) + 1;  break;
    case 'M':   
      const mExponent = Math.random() * 8; // 10^0 bis 10^8
      actualPotency = Math.floor(Math.pow(10, mExponent));
      actualPotency = Math.min(actualPotency, 100000000);
      break;
    case 'F1':  
      const f1Exponent = 6 + Math.random() * 7; // 10^6 bis 10^13
      actualPotency = Math.floor(Math.pow(10, f1Exponent));
      break;
    case 'F2':  
      const f2Exponent = 8 + Math.random() * 7; // 10^8 bis 10^15
      actualPotency = Math.floor(Math.pow(10, f2Exponent));
      break;
    case 'F3':  
      const f3Exponent = 10 + Math.random() * 6; // 10^10 bis 10^16
      actualPotency = Math.floor(Math.pow(10, f3Exponent));
      break;
  }
  
  // 3. Level-Verteilung: 100 Ziehungen (1-12)
  const levelDistribution: Record<number, number> = {};
  for (let i = 1; i <= 12; i++) {
    levelDistribution[i] = 0;
  }
  
  for (let i = 0; i < 100; i++) {
    const level = weightedPickLevel();
    levelDistribution[level]++;
  }
  
  // 4. Dominante Ebene = Maximum
  let dominantLevel = 1;
  let maxCount = 0;
  
  for (let level = 1; level <= 12; level++) {
    if (levelDistribution[level] > maxCount) {
      maxCount = levelDistribution[level];
      dominantLevel = level;
    }
  }
  
  return { potency: actualPotency, potencyType, levelDistribution, dominantLevel };
}
```

### 4.5 Haupt-Analyse-Funktion

```typescript
export function analyzeRates(
  rates: Array<{ name: string; copenRate: number }>,
  config: AnalysisConfig
): AnalysisResult {
  // 1. Selektion (10%)
  const selected = selectRates(rates, config);
  
  // 2. Energetisches Laden
  const { energies, trials } = chargeRates(selected, config.chargingThreshold);
  
  // 3. RateObjects erstellen mit Potenz, Potenztyp und Level
  const rateObjects: RateObject[] = selected.map(rate => {
    const { potency, potencyType, levelDistribution, dominantLevel } = 
      assignPotencyAndLevels(rate.name);
    
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
  
  // 4. Sortieren nach energeticValue (absteigend)
  rateObjects.sort((a, b) => b.energeticValue - a.energeticValue);
  
  // 5. Optional auf maxEntries kürzen
  const finalRates = config.maxEntries 
    ? rateObjects.slice(0, config.maxEntries)
    : rateObjects;
  
  return { rateObjects: finalRates, numberOfTrials: trials };
}
```

### 4.6 Standard-Konfiguration

```typescript
export const DEFAULT_ANALYSIS_CONFIG: AnalysisConfig = {
  selectionFraction: 0.1,    // 10%
  minSelection: 1,
  maxSelection: 100,
  chargingThreshold: 100,
  maxEntries: 35,
};
```

---

## 5. 13+1 EBENEN-RESONANZ (levelResonance.ts)

### 5.1 Level Interface

```typescript
export interface Level {
  id: number;                         // 1-13
  name: string;                       // Englischer Name
  germanName: string;                 // Deutscher Name
  description: string;                // Beschreibung
  keywords: string[];                 // Suchbegriffe
  frequencyRange: { min: number; max: number }; // Frequenzbereich
}
```

### 5.2 13+1 Ebenen-Modell

```typescript
export const LEVELS: Level[] = [
  {
    id: 1,
    name: "Physical Realm - Particles",
    germanName: "Physische Ebene - Partikel",
    description: "Materielle Ebene: Atome, Partikel, Elemente",
    keywords: ["atom", "partikel", "molekül", "element", "materie", "particles", "atoms", "matter", "dna", "struktur"],
    frequencyRange: { min: 1, max: 100000 }
  },
  {
    id: 2,
    name: "Physical Realm - Structure",
    germanName: "Physische Ebene - Struktur",
    description: "Physische Struktur: Gewebe, Organe, Körper",
    keywords: ["körper", "organ", "gewebe", "struktur", "fascia", "electromagnetism", "body", "tissue", "structure"],
    frequencyRange: { min: 100000, max: 500000 }
  },
  {
    id: 3,
    name: "Etheric Realm - Prana",
    germanName: "Ätherische Ebene - Prana",
    description: "Lebenskraft-Ebene: Qi, Prana, Atmung",
    keywords: ["prana", "qi", "lebenskraft", "atmung", "heartbeat", "breathing", "life-force", "energie"],
    frequencyRange: { min: 500000, max: 1000000 }
  },
  {
    id: 4,
    name: "Etheric Realm - Meridians",
    germanName: "Ätherische Ebene - Meridiane",
    description: "Energiekanäle: Meridiane, Chakren (physisch)",
    keywords: ["meridian", "chakra", "energiekanal", "nadis", "akupunktur", "meridians", "energy channels"],
    frequencyRange: { min: 1000000, max: 2000000 }
  },
  {
    id: 5,
    name: "Astral Realm - Emotions",
    germanName: "Astrale Ebene - Emotionen",
    description: "Emotionale Ebene: Gefühle, emotionale Komplexe",
    keywords: ["emotion", "gefühl", "empfindung", "emotions", "feelings", "plasmic archetypes", "emotional complexes"],
    frequencyRange: { min: 2000000, max: 3500000 }
  },
  {
    id: 6,
    name: "Astral Realm - Thought-Forms",
    germanName: "Astrale Ebene - Gedankenformen",
    description: "Gedankenformen: Magnetische Felder, Schwingungsmuster",
    keywords: ["gedanke", "thought", "magnetisch", "schwingung", "thought-forms", "magnetic fields", "pattern"],
    frequencyRange: { min: 3500000, max: 5000000 }
  },
  {
    id: 7,
    name: "Mental Realm - Time",
    germanName: "Mentale Ebene - Zeit",
    description: "Zeitliche Konstrukte: Raum, Form, Farbe",
    keywords: ["zeit", "time", "raum", "space", "form", "shape", "farbe", "colour", "psychons"],
    frequencyRange: { min: 5000000, max: 7000000 }
  },
  {
    id: 8,
    name: "Mental Realm - Mental Constructs",
    germanName: "Mentale Ebene - Mentale Konstrukte",
    description: "Mentale Konstrukte: Poetische Felder, Konzepte",
    keywords: ["konzept", "idee", "mental", "konstrukt", "mental constructs", "poetic fields", "concept"],
    frequencyRange: { min: 7000000, max: 9000000 }
  },
  {
    id: 9,
    name: "Causal Plane - Blueprints",
    germanName: "Kausale Ebene - Blaupausen",
    description: "Akasha-Chronik: Destiny Scripts, Blaupausen",
    keywords: ["akasha", "blueprint", "blaupause", "destiny", "script", "akashic", "blueprints", "destiny scripts"],
    frequencyRange: { min: 9000000, max: 11000000 }
  },
  {
    id: 10,
    name: "Causal Plane - Alchemy",
    germanName: "Kausale Ebene - Alchemie",
    description: "Intention: Alchemische Transformation",
    keywords: ["intention", "alchemie", "alchemy", "transformation", "transmutation", "wandlung"],
    frequencyRange: { min: 11000000, max: 13000000 }
  },
  {
    id: 11,
    name: "Atmic Plane - Identity",
    germanName: "Atmische Ebene - Identität",
    description: "Reine Essenz: Unfragmentierte Identität",
    keywords: ["identität", "essenz", "identity", "essence", "pure essence", "unfragmented", "incarnation"],
    frequencyRange: { min: 13000000, max: 16000000 }
  },
  {
    id: 12,
    name: "Atmic Plane - Love & Unity",
    germanName: "Atmische Ebene - Liebe & Einheit",
    description: "Einheit: Liebe, Archetypal Thinking",
    keywords: ["liebe", "einheit", "love", "unity", "archetypal thinking", "transcending ego"],
    frequencyRange: { min: 16000000, max: 20000000 }
  },
  {
    id: 13,
    name: "Creator - Divinity",
    germanName: "Schöpfer - Göttlichkeit",
    description: "Göttliche Ebene: Ewigkeit, Wille zum Leben",
    keywords: ["creator", "schöpfer", "göttlich", "divinity", "eternity", "ewigkeit", "will to life", "prayers"],
    frequencyRange: { min: 20000000, max: Infinity }
  }
];
```

### 5.3 Resonanzberechnung

```typescript
export function calculateLevelResonance(
  copenRate: number,
  word: string
): Record<string, number> {
  const resonance: Record<string, number> = {};
  const normalizedWord = word.toLowerCase();

  LEVELS.forEach(level => {
    let baseResonance = 0;

    // 1. Frequenzbasierte Resonanz
    const { min, max } = level.frequencyRange;
    
    if (max === Infinity) {
      // Göttliche Ebene (13)
      if (copenRate >= min) {
        baseResonance = 100;
      } else {
        baseResonance = Math.max(0, (copenRate / min) * 50);
      }
    } else if (copenRate >= min && copenRate <= max) {
      // Rate liegt im Bereich - hohe Resonanz
      const midpoint = (min + max) / 2;
      const distance = Math.abs(copenRate - midpoint);
      const range = (max - min) / 2;
      baseResonance = Math.max(0, 100 - (distance / range) * 50);
    } else if (copenRate < min) {
      // Rate liegt unter dem Bereich
      baseResonance = Math.max(0, (copenRate / min) * 40);
    } else {
      // Rate liegt über dem Bereich
      if (max > 0) {
        const overshoot = (copenRate - max) / max;
        baseResonance = Math.max(0, 30 - overshoot * 30);
      }
    }

    // 2. Keyword-basierte Resonanz
    let keywordBonus = 0;
    level.keywords.forEach(keyword => {
      if (normalizedWord.includes(keyword.toLowerCase())) {
        keywordBonus += 25;
      }
    });

    // 3. Kombiniere beide Resonanzen
    const totalResonance = Math.min(100, baseResonance + keywordBonus);
    
    resonance[`level_${level.id}`] = parseFloat(totalResonance.toFixed(2));
  });

  return resonance;
}
```

### 5.4 Höchste Resonanzebene ermitteln

```typescript
export function findHighestResonanceLevel(
  resonanceValues: Record<string, number>
): { level: number; value: number } {
  let highestLevel = 1;
  let highestValue = 0;

  Object.entries(resonanceValues).forEach(([key, value]) => {
    if (value > highestValue) {
      const levelMatch = key.match(/level_(\d+)/);
      if (levelMatch) {
        highestLevel = parseInt(levelMatch[1]);
        highestValue = value;
      }
    }
  });

  return { level: highestLevel, value: highestValue };
}
```

### 5.5 Ebenen-Hilfsfunktionen

```typescript
export function getLevelDisplayName(levelId: number, language: 'de' | 'en' = 'de'): string {
  const level = LEVELS.find(l => l.id === levelId);
  if (!level) return `Ebene ${levelId}`;
  return language === 'de' ? level.germanName : level.name;
}

export function getLevelDescription(levelId: number): string {
  const level = LEVELS.find(l => l.id === levelId);
  return level?.description || '';
}
```

---

## 6. POTENZ-TEXT-KONVERTIERUNG (potencyText.ts)

### 6.1 Zahlen zu deutschen Wörtern

```typescript
export const numberToGermanWords = (num: number): string => {
  const ones = ['', 'ein', 'zwei', 'drei', 'vier', 'fünf', 'sechs', 'sieben', 'acht', 'neun'];
  const teens = ['zehn', 'elf', 'zwölf', 'dreizehn', 'vierzehn', 'fünfzehn', 'sechzehn', 'siebzehn', 'achtzehn', 'neunzehn'];
  const tens = ['', 'zehn', 'zwanzig', 'dreißig', 'vierzig', 'fünfzig', 'sechzig', 'siebzig', 'achtzig', 'neunzig'];
  const hundreds = ['', 'einhundert', 'zweihundert', 'dreihundert', 'vierhundert', 'fünfhundert', 'sechshundert', 'siebenhundert', 'achthundert', 'neunhundert'];

  if (num === 0) return 'null';
  if (num < 10) return ones[num];
  if (num >= 10 && num < 20) return teens[num - 10];
  if (num >= 20 && num < 100) {
    const ten = Math.floor(num / 10);
    const one = num % 10;
    if (one === 0) return tens[ten];
    return `${ones[one]}und${tens[ten]}`;
  }
  if (num >= 100 && num < 1000) {
    const hundred = Math.floor(num / 100);
    const rest = num % 100;
    if (rest === 0) return hundreds[hundred];
    return `${hundreds[hundred]}${numberToGermanWords(rest)}`;
  }
  if (num >= 1000 && num < 10000) {
    const thousand = Math.floor(num / 1000);
    const rest = num % 1000;
    const thousandWord = thousand === 1 ? 'eintausend' : `${ones[thousand]}tausend`;
    if (rest === 0) return thousandWord;
    return `${thousandWord}${numberToGermanWords(rest)}`;
  }
  
  return num.toString(); // Für sehr große Zahlen
};
```

### 6.2 Potenz-Konvertierung

```typescript
export const convertPotencyNumbersToWords = (text: string): string => {
  const potencyPattern = /\b([DCLM]+)(\d+)\b/gi;
  
  return text.replace(potencyPattern, (match, potencyType, numStr) => {
    const num = parseInt(numStr, 10);
    let wordNum = numberToGermanWords(num);
    
    // Für Zahlen >= 100: Ersten Buchstaben groß schreiben
    if (num >= 100 && wordNum.length > 0) {
      wordNum = wordNum.charAt(0).toUpperCase() + wordNum.slice(1);
    }
    
    return `${potencyType.toUpperCase()}${wordNum}`;
  });
};
```

### 6.3 Beispiele

```
"Arnica D6"        → "Arnica Dsechs"
"Belladonna C30"   → "Belladonna Cdreißig"
"Nux vomica D100"  → "Nux vomica DEinhundert"
"Sulphur C200"     → "Sulphur CZweihundert"
"Pulsatilla LM18"  → "Pulsatilla LMachtzehn"
```

---

## 7. UI-KOMPONENTEN

### 7.1 CopenRateGenerator.tsx (Standalone)

**Komponente:** `src/components/CopenRateGenerator.tsx`

**Features:**
- Einzelberechnung mit SingleCalculationForm
- Batch-Import mit CSV
- Datei-Import (PDF/Bild mit OCR)
- Ergebnistabelle mit Export/Löschen

**State:**
```typescript
const [singleWord, setSingleWord] = useState('');
const [singlePotency, setSinglePotency] = useState(6);
const [singlePotencyType, setSinglePotencyType] = useState<'D' | 'C' | 'LM' | 'M'>('D');
const [singleAlphabetType, setSingleAlphabetType] = useState<AlphabetType>('latin');
const [results, setResults] = useState<CopenRateResult[]>([]);
const [csvInput, setCsvInput] = useState('');
```

**Hauptfunktionen:**
- `handleSingleCalculation()` → Einzelne Rate berechnen
- `handleBatchCalculation()` → Batch aus CSV
- `handleFileUpload()` → CSV-Datei einlesen
- `handleFileImportData()` → OCR-extrahierte Daten
- `handleExport()` → CSV-Export
- `clearResults()` → Ergebnisse löschen

### 7.2 SingleCalculationForm.tsx

**Komponente:** `src/components/forms/SingleCalculationForm.tsx`

**Props:**
```typescript
interface SingleCalculationFormProps {
  word: string;
  potency: number;
  potencyType: 'D' | 'C' | 'LM' | 'M';
  alphabetType: AlphabetType;
  onWordChange: (word: string) => void;
  onPotencyChange: (potency: number) => void;
  onPotencyTypeChange: (type: 'D' | 'C' | 'LM' | 'M') => void;
  onAlphabetTypeChange: (type: AlphabetType) => void;
  onCalculate: () => void;
  calculatedRate?: number;
  highestLevel?: { level: number; value: number };
}
```

**Features:**
- Input für Wortenergie
- Potenz-Eingabe (0-50000)
- Potenztyp-Auswahl (D, C, LM, M)
- Alphabet-Auswahl (Latin, Altdeutsch, Runisch)
- Anzeige berechneter Rate + höchste Resonanzebene

### 7.3 BatchImportForm.tsx

**Komponente:** `src/components/forms/BatchImportForm.tsx`

**Features:**
- CSV-Datei-Upload
- Textarea für manuelle CSV-Eingabe
- Batch-Berechnung starten

**CSV-Format:**
```
Wort,Potenz,Typ,Alphabet
Arnica,6,D,latin
Belladonna,12,D,latin
Nux vomica,30,C,latin
```

### 7.4 FileImportForm.tsx

**Komponente:** `src/components/forms/FileImportForm.tsx`

**Features:**
- PDF-Import mit direkter Texterkennung + OCR
- Bild-Import mit OCR (Tesseract.js)
- Unterstützte Formate: PDF, JPG, PNG, GIF, WEBP
- Fortschrittsanzeige
- Dateigrößen-Limit: PDF max. 10MB, Bilder max. 5MB

**OCR-Optimierungen:**
- Deutsch/Englisch Erkennung
- Optimiert für mentale Raten
- Tabellen-Erkennung
- Whitelist für spezifische Zeichen

### 7.5 ResultsTable.tsx

**Komponente:** `src/components/tables/ResultsTable.tsx`

**Features:**
- Tabellarische Anzeige aller berechneten Raten
- Spalten: Wortenergie, Potenz, Typ, Alphabet, Copen-Rate, Details
- Export-Button (CSV)
- Löschen-Button
- Detailansicht mit Berechnungsschritten

---

## 8. CLOUD-INTEGRATION (CopenGeneratorPage.tsx)

### 8.1 CloudPatient Interface

```typescript
interface CloudPatient {
  id: string;
  user_id: string;
  first_name: string;
  last_name: string;
  birth_date: string;
  birth_place: string;
  created_at: string;
  updated_at: string;
  image_signature?: string | null;
  image_signature_active?: boolean;
}
```

### 8.2 Harmonisierungs-Optionen

```typescript
// State
const [harmonizationDuration, setHarmonizationDuration] = useState(5);
const [harmonizationUnit, setHarmonizationUnit] = useState<'seconds' | 'minutes' | 'hours' | 'days'>('minutes');
const [continuousMode, setContinuousMode] = useState(false);
const [pulsePauseActive, setPulsePauseActive] = useState(false);
const [pulseSeconds, setPulseSeconds] = useState(3);
const [pauseSeconds, setPauseSeconds] = useState(7);
```

### 8.3 Harmonisierung starten

```typescript
const startHarmonization = async () => {
  // Validierung
  if (!user || !selectedPatient || currentCalculatedRate === undefined) return;

  // Dauer berechnen
  const durationSeconds = continuousMode 
    ? 999999999 
    : getDurationInSeconds(harmonizationDuration, harmonizationUnit);

  // Session-Daten
  const sessionData = {
    user_id: user.id,
    patient_id: selectedPatient.id,
    word: singleWord,                           // WICHTIG: Original-Wortenergie
    copen_rate: currentCalculatedRate.toString(),
    tested_potency: `${singlePotencyType}${singlePotency}`,
    duration_seconds: durationSeconds,
    remaining_seconds: durationSeconds,
    status: 'pending' as const,
    pulse_seconds: pulsePauseActive ? pulseSeconds : null,
    pause_seconds: pulsePauseActive ? pauseSeconds : null,
    pulse_pause_active: pulsePauseActive,
  };

  // In Supabase speichern
  await supabase.from('harmonization_sessions_v2').insert([sessionData]);

  // Worker triggern
  await supabase.functions.invoke('harmonization-worker');
};
```

### 8.4 Bildsignatur-Integration

```typescript
const handleSingleCalculation = () => {
  // Bildsignatur nutzen, wenn Klient ausgewählt und aktiv
  const useImgSig = selectedPatient?.image_signature_active ?? false;
  const imgSig = selectedPatient?.image_signature ?? undefined;
  
  const result = calculateCopenRate(
    singleWord, 
    singlePotency, 
    singlePotencyType, 
    singleAlphabetType,
    imgSig,      // Bildsignatur-String
    useImgSig    // Flag: Bildsignatur nutzen
  );
  
  // ... Resonanzanalyse ...
};
```

### 8.5 Integrierte Komponenten

```typescript
<PatientManagerCloud
  selectedPatient={selectedPatient}
  onSelectPatient={setSelectedPatient}
/>

<HarmonizationArchiveCloud
  patientId={selectedPatient?.id}
/>

<AnalysisArchiveCloud />
```

---

## 9. DATENSTRUKTUREN

### 9.1 Supabase Tabellen

#### 9.1.1 harmonization_sessions_v2

```sql
CREATE TABLE harmonization_sessions_v2 (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL,
  patient_id UUID NOT NULL,
  word TEXT NOT NULL,                -- Original-Wortenergie
  copen_rate TEXT,
  tested_potency TEXT,
  duration_seconds INTEGER NOT NULL,
  remaining_seconds INTEGER,
  progress INTEGER DEFAULT 0,
  status TEXT NOT NULL DEFAULT 'pending',
  started_at TIMESTAMP WITH TIME ZONE,
  completed_at TIMESTAMP WITH TIME ZONE,
  job_started_at TIMESTAMP WITH TIME ZONE,
  job_last_heartbeat TIMESTAMP WITH TIME ZONE,
  pulse_seconds INTEGER,
  pause_seconds INTEGER,
  pulse_pause_active BOOLEAN DEFAULT false,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);
```

#### 9.1.2 analysis_archives_v2

```sql
CREATE TABLE analysis_archives_v2 (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL,
  patient_id UUID,
  word TEXT NOT NULL,
  copen_rate TEXT NOT NULL,
  tested_potency TEXT,
  analysis_timestamp TIMESTAMP WITH TIME ZONE DEFAULT now(),
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
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);
```

#### 9.1.3 patients_v2

```sql
CREATE TABLE patients_v2 (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL,
  first_name TEXT NOT NULL,
  last_name TEXT NOT NULL,
  birth_date TEXT NOT NULL,
  birth_place TEXT NOT NULL,
  image_signature TEXT,
  image_signature_active BOOLEAN DEFAULT true,
  personal_rate TEXT,
  hardware_config JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);
```

### 9.2 Export-Format (CSV)

```csv
Wortenergie,Potenz,Typ,Alphabet,Copen-Rate
Arnica,6,D,latin,183648
Belladonna,12,D,latin,436752
Nux vomica,30,C,latin,7227426
```

---

## 10. MATHEMATISCHE VALIDIERUNG

### 10.1 Validierungsregeln

```typescript
export const validateWordEnergy = (word: string): ValidationResult => {
  if (!word.trim()) {
    return { valid: false, error: 'Wortenergie darf nicht leer sein' };
  }

  if (word.length > 50) {
    return { valid: false, error: 'Wortenergie darf maximal 50 Zeichen enthalten' };
  }

  return { valid: true };
};
```

### 10.2 Fibonacci-Cache

```typescript
const fibonacciCache: { [key: number]: number } = {};

const getFibonacciMultiplier = (n: number): number => {
  if (n <= 0) return 1;
  if (n === 1) return 1;
  if (fibonacciCache[n]) return fibonacciCache[n];

  let a = 1, b = 1;
  for (let i = 2; i <= n; i++) {
    const temp = a + b;
    a = b;
    b = temp;
  }

  fibonacciCache[n] = b;
  return b;
};
```

### 10.3 Mathematische Konstanten

```typescript
// Fibonacci-Verhältnis
const PHI = 34 / 21; // ≈ 1,619047619 (Goldener Schnitt)

// Potenz-Multiplikatoren
const POTENCY_FACTORS = {
  D:  0.1,   // Dezimalverdünnung
  C:  0.2,   // Centesimalverdünnung
  LM: 0.5,   // 50-Millesimalverdünnung
  M:  1.0,   // Vollpotenz
  F1: 1/6,   // Fibonacci Stufe 1
  F2: 1/4,   // Fibonacci Stufe 2
  F3: 1/3    // Fibonacci Stufe 3
};
```

---

## 11. WIEDERHERSTELLUNGS-CHECKLISTE

### 11.1 Core-Dateien

- [x] `src/utils/copenRateGenerator.ts` → Hauptalgorithmus
- [x] `src/utils/alphabetSystems.ts` → Alphabet-Systeme
- [x] `src/utils/resonanceAnalysis.ts` → 13-Ebenen-Analyse
- [x] `src/utils/levelResonance.ts` → Level-Resonanzberechnung
- [x] `src/utils/potencyText.ts` → Potenz-Textkonvertierung

### 11.2 UI-Komponenten

- [x] `src/components/CopenRateGenerator.tsx` → Standalone-Generator
- [x] `src/components/forms/SingleCalculationForm.tsx`
- [x] `src/components/forms/BatchImportForm.tsx`
- [x] `src/components/forms/FileImportForm.tsx`
- [x] `src/components/tables/ResultsTable.tsx`

### 11.3 Pages

- [x] `src/pages/CopenGeneratorPage.tsx` → Cloud-Integration

### 11.4 Supabase

- [x] Tabelle `harmonization_sessions_v2`
- [x] Tabelle `analysis_archives_v2`
- [x] Tabelle `patients_v2`
- [x] RLS-Policies für alle Tabellen

### 11.5 Dokumentation

- [x] `Bruce_Copen_Algorithmus_Dokumentation.md`
- [x] `Bruce_Copen_Ratengenerator_Komplett.md` (dieses Dokument)

---

## 12. WICHTIGE IMPLEMENTIERUNGSDETAILS

### 12.1 Wortenergie vs. Rate in Harmonisierung

**KRITISCH:** Bei der Harmonisierung wird die **Original-Wortenergie** übergeben, NICHT die Rate!

```typescript
// ✅ RICHTIG (CopenGeneratorPage.tsx)
const sessionData = {
  word: singleWord,  // Original-Wortenergie (z.B. "Arnica")
  copen_rate: currentCalculatedRate.toString(),  // Rate als String
  // ...
};

// ❌ FALSCH
const sessionData = {
  word: currentCalculatedRate.toString(),  // NICHT die Rate!
  // ...
};
```

### 12.2 Bildsignatur-Pfad

```typescript
// Bruce Copen Pfad (arithmetisches Mittel)
if (useImageSignature && imageSignature) {
  primarySum = Math.floor((primarySum + imgPrimary) / 2);
}

// NICHT: Hardware-Algorithmus-Pfad (würde andere Berechnung verwenden)
```

### 12.3 Potenz-Konvertierung im DB-Import

```typescript
// In DatabaseManager.tsx
import { convertPotencyNumbersToWords } from '@/utils/potencyText';

// Nur auf erste Spalte (Wortenergie) anwenden
const firstColumn = convertPotencyNumbersToWords(cols[0]);
```

### 12.4 DB-Analyse Syntax für Harmonisierung

```typescript
// ✅ RICHTIG (DatabaseManager.tsx)
word: `Harmonisierung mit ${r.rate.toLocaleString('de-DE')}`

// ❌ FALSCH (alte Syntax)
word: `Optimale Harmonisierung von "${r.rateName}"...`
```

---

## 13. ENTWICKLUNGS-HINWEISE

### 13.1 Neue Features hinzufügen

1. Core-Algorithmus erweitern → `copenRateGenerator.ts`
2. UI-Komponente erstellen/anpassen
3. Integration in `CopenGeneratorPage.tsx`
4. Supabase-Schema anpassen (falls nötig)
5. Dokumentation aktualisieren

### 13.2 Testing-Strategien

```typescript
// Test-Beispiele für Validierung
const testCases = [
  { input: "NUX VOMICA D6", expected: 1204571 },
  { input: "ARNICA C30", expected: 1541330 },
  { input: "HEILUNG D0", expected: 535619 },
];
```

### 13.3 Performance-Optimierungen

- Fibonacci-Cache für wiederholte Berechnungen
- Batch-Verarbeitung für große Datensätze
- Lazy-Loading für Komponenten
- Memoization für Resonanzberechnungen

---

## 14. ÄNDERUNGSHISTORIE

| Datum | Version | Änderung |
|-------|---------|----------|
| 2025-01-29 | 3.0 | Vollständige Dokumentation erstellt |
| 2025-01-29 | 2.9 | Potenz-Textkonvertierung hinzugefügt |
| 2025-01-28 | 2.8 | DB-Analyse Syntax angepasst |
| 2025-01-27 | 2.7 | Bildsignatur-Integration optimiert |
| 2025-01-26 | 2.6 | 13+1 Ebenen-Resonanz implementiert |

---

**Ende der Dokumentation**

*Für Fragen oder Erweiterungen bitte diese Dokumentation aktualisieren und versionieren.*
