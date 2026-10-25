# Ebenen- und Potenzberechnung: Entwickler-Dokumentation

**Version:** 2025-11-17  
**Zielgruppe:** Entwickler  
**Zweck:** Exakte, detaillierte Schritt-für-Schritt-Erklärung der Algorithmen

---

## Inhaltsverzeichnis

1. [Ebenenberechnung (levelResonance.ts)](#1-ebenenberechnung-levelresonancets)
   - 1.1 [Das 13-Ebenen-Modell](#11-das-13-ebenen-modell)
   - 1.2 [Algorithmus: calculateLevelResonance()](#12-algorithmus-calculatelevelresonance)
   - 1.3 [Frequenzbasierte Resonanz](#13-frequenzbasierte-resonanz)
   - 1.4 [Keyword-basierte Resonanz](#14-keyword-basierte-resonanz)
   - 1.5 [Kombination und Normalisierung](#15-kombination-und-normalisierung)
   - 1.6 [Höchste Resonanzebene ermitteln](#16-höchste-resonanzebene-ermitteln)
2. [Potenzberechnung (resonanceAnalysis.ts)](#2-potenzberechnung-resonanceanalysists)
   - 2.1 [Level-Gewichte (1-12)](#21-level-gewichte-1-12)
   - 2.2 [Gewichtete Zufallsauswahl](#22-gewichtete-zufallsauswahl)
   - 2.3 [Potenztyp-Auswahl](#23-potenztyp-auswahl)
   - 2.4 [Potenzwert-Generierung](#24-potenzwert-generierung)
   - 2.5 [Level-Distribution (100 Ziehungen)](#25-level-distribution-100-ziehungen)
   - 2.6 [Dominante Ebene ermitteln](#26-dominante-ebene-ermitteln)
3. [Integration in DB-Analyse](#3-integration-in-db-analyse)
4. [Mathematische Referenz](#4-mathematische-referenz)

---

## 1. Ebenenberechnung (levelResonance.ts)

Die Ebenenberechnung ordnet jede berechnete Copen-Rate einer oder mehreren der 13 kosmologischen Ebenen zu und berechnet Resonanzwerte (0-100%) für jede Ebene.

### 1.1 Das 13-Ebenen-Modell

Das System basiert auf einem spirituellen Kosmologie-Modell mit 13 Ebenen:

| ID | Name (EN) | Name (DE) | Beschreibung | Frequenzbereich (Hz) | Keywords (Beispiele) |
|----|-----------|-----------|--------------|----------------------|----------------------|
| 1 | Physical Realm - Particles | Physische Ebene - Partikel | Materielle Ebene: Atome, Partikel, Elemente | 1 - 100.000 | atom, partikel, molekül, element, materie, dna |
| 2 | Physical Realm - Structure | Physische Ebene - Struktur | Physische Struktur: Gewebe, Organe, Körper | 100.000 - 500.000 | körper, organ, gewebe, struktur, fascia |
| 3 | Etheric Realm - Prana | Ätherische Ebene - Prana | Lebenskraft-Ebene: Qi, Prana, Atmung | 500.000 - 1.000.000 | prana, qi, lebenskraft, atmung, breathing |
| 4 | Etheric Realm - Meridians | Ätherische Ebene - Meridiane | Energiekanäle: Meridiane, Chakren (physisch) | 1.000.000 - 2.000.000 | meridian, chakra, energiekanal, nadis, akupunktur |
| 5 | Astral Realm - Emotions | Astrale Ebene - Emotionen | Emotionale Ebene: Gefühle, emotionale Komplexe | 2.000.000 - 3.500.000 | emotion, gefühl, empfindung, feelings |
| 6 | Astral Realm - Thought-Forms | Astrale Ebene - Gedankenformen | Gedankenformen: Magnetische Felder, Schwingungsmuster | 3.500.000 - 5.000.000 | gedanke, thought, magnetisch, schwingung, pattern |
| 7 | Mental Realm - Time | Mentale Ebene - Zeit | Zeitliche Konstrukte: Raum, Form, Farbe | 5.000.000 - 7.000.000 | zeit, time, raum, space, form, farbe, psychons |
| 8 | Mental Realm - Mental Constructs | Mentale Ebene - Mentale Konstrukte | Mentale Konstrukte: Poetische Felder, Konzepte | 7.000.000 - 9.000.000 | konzept, idee, mental, konstrukt, poetic fields |
| 9 | Causal Plane - Blueprints | Kausale Ebene - Blaupausen | Akasha-Chronik: Destiny Scripts, Blaupausen | 9.000.000 - 11.000.000 | akasha, blueprint, blaupause, destiny, script |
| 10 | Causal Plane - Alchemy | Kausale Ebene - Alchemie | Intention: Alchemische Transformation | 11.000.000 - 13.000.000 | intention, alchemie, alchemy, transformation |
| 11 | Atmic Plane - Identity | Atmische Ebene - Identität | Reine Essenz: Unfragmentierte Identität | 13.000.000 - 16.000.000 | identität, essenz, identity, pure essence, incarnation |
| 12 | Atmic Plane - Love & Unity | Atmische Ebene - Liebe & Einheit | Einheit: Liebe, Archetypal Thinking | 16.000.000 - 20.000.000 | liebe, einheit, love, unity, archetypal thinking |
| 13 | Creator - Divinity | Schöpfer - Göttlichkeit | Göttliche Ebene: Ewigkeit, Wille zum Leben | 20.000.000 - ∞ | creator, schöpfer, göttlich, divinity, eternity, prayers |

**Dateistruktur:**
```typescript
export interface Level {
  id: number;
  name: string;
  germanName: string;
  description: string;
  keywords: string[];
  frequencyRange: { min: number; max: number };
}

export const LEVELS: Level[] = [
  // ... 13 Ebenen wie oben
];
```

---

### 1.2 Algorithmus: calculateLevelResonance()

**Funktion:**
```typescript
export function calculateLevelResonance(
  copenRate: number,
  word: string
): Record<string, number>
```

**Parameter:**
- `copenRate`: Die berechnete Copen-Rate (z.B. 85432187)
- `word`: Das Eingabewort (z.B. "Allergie")

**Rückgabe:**
- Ein Objekt mit 13 Resonanzwerten: `{ level_1: 45.67, level_2: 78.23, ..., level_13: 12.34 }`

**Prozess-Übersicht:**
1. Normalisiere Wort zu Kleinbuchstaben
2. Für jede der 13 Ebenen:
   - Berechne frequenzbasierte Resonanz
   - Berechne keyword-basierte Resonanz
   - Kombiniere beide Resonanzen
   - Normalisiere auf 0-100%

---

### 1.3 Frequenzbasierte Resonanz

Die frequenzbasierte Resonanz bestimmt, wie gut die Copen-Rate in den Frequenzbereich einer Ebene passt.

**Schritt-für-Schritt:**

#### Fall 1: Göttliche Ebene (Level 13, max = Infinity)

```typescript
if (max === Infinity) {
  if (copenRate >= min) {
    baseResonance = 100;
  } else {
    const ratio = copenRate / min;
    baseResonance = Math.max(0, ratio * 50);
  }
}
```

**Beispiel:**
- Level 13: min = 20.000.000, max = ∞
- Copen-Rate = 85.432.187

```
copenRate (85.432.187) >= min (20.000.000) ✓
→ baseResonance = 100
```

**Erklärung:** Wenn die Rate über dem Minimum liegt, erreicht sie volle Resonanz (100%). Sonst proportionale Teilresonanz.

---

#### Fall 2: Rate liegt im Bereich (min ≤ copenRate ≤ max)

```typescript
if (copenRate >= min && copenRate <= max) {
  const midpoint = (min + max) / 2;
  const distance = Math.abs(copenRate - midpoint);
  const range = (max - min) / 2;
  baseResonance = Math.max(0, 100 - (distance / range) * 50);
}
```

**Beispiel:**
- Level 5: min = 2.000.000, max = 3.500.000
- Copen-Rate = 2.750.000

```
midpoint = (2.000.000 + 3.500.000) / 2 = 2.750.000
distance = |2.750.000 - 2.750.000| = 0
range = (3.500.000 - 2.000.000) / 2 = 750.000

baseResonance = 100 - (0 / 750.000) * 50
              = 100 - 0
              = 100
```

**Erklärung:** 
- Je näher die Rate am Mittelpunkt des Bereichs liegt, desto höher die Resonanz
- Am Mittelpunkt: 100% Resonanz
- An den Grenzen (min/max): 50% Resonanz
- Außerhalb: < 50% Resonanz

**Weiteres Beispiel (Rate am Rand):**
- Level 5: min = 2.000.000, max = 3.500.000
- Copen-Rate = 2.000.000 (am Minimum)

```
midpoint = 2.750.000
distance = |2.000.000 - 2.750.000| = 750.000
range = 750.000

baseResonance = 100 - (750.000 / 750.000) * 50
              = 100 - 50
              = 50
```

---

#### Fall 3: Rate liegt unter dem Bereich (copenRate < min)

```typescript
if (copenRate < min) {
  const ratio = copenRate / min;
  baseResonance = Math.max(0, ratio * 40);
}
```

**Beispiel:**
- Level 7: min = 5.000.000, max = 7.000.000
- Copen-Rate = 2.500.000

```
ratio = 2.500.000 / 5.000.000 = 0.5

baseResonance = 0.5 * 40
              = 20
```

**Erklärung:** Je näher die Rate am Minimum liegt, desto höher die Teilresonanz (max 40%).

---

#### Fall 4: Rate liegt über dem Bereich (copenRate > max)

```typescript
if (copenRate > max) {
  const overshoot = (copenRate - max) / max;
  baseResonance = Math.max(0, 30 - overshoot * 30);
}
```

**Beispiel:**
- Level 4: min = 1.000.000, max = 2.000.000
- Copen-Rate = 3.000.000

```
overshoot = (3.000.000 - 2.000.000) / 2.000.000
          = 1.000.000 / 2.000.000
          = 0.5

baseResonance = 30 - (0.5 * 30)
              = 30 - 15
              = 15
```

**Erklärung:** Je weiter die Rate über dem Maximum liegt, desto geringer die Resonanz (max 30%, dann abnehmend).

---

### 1.4 Keyword-basierte Resonanz

Zusätzlich zur Frequenz wird geprüft, ob das Eingabewort Keywords der Ebene enthält.

**Algorithmus:**
```typescript
let keywordBonus = 0;
level.keywords.forEach(keyword => {
  if (normalizedWord.includes(keyword.toLowerCase())) {
    keywordBonus += 25;
  }
});
```

**Beispiel:**
- Word: "Allergie"
- Level 1 Keywords: ["atom", "partikel", "molekül", "element", "materie", "particles", "atoms", "matter", "dna", "struktur"]

```
normalizedWord = "allergie"

Prüfung:
- "allergie".includes("atom") → false
- "allergie".includes("partikel") → false
- ... (alle Keywords)
- Keine Treffer

keywordBonus = 0
```

**Beispiel mit Treffer:**
- Word: "Emotionale Blockade"
- Level 5 Keywords: ["emotion", "gefühl", "empfindung", "emotions", "feelings", "plasmic archetypes", "emotional complexes"]

```
normalizedWord = "emotionale blockade"

Prüfung:
- "emotionale blockade".includes("emotion") → true → +25
- "emotionale blockade".includes("gefühl") → false
- "emotionale blockade".includes("empfindung") → false
- ...

keywordBonus = 25
```

**Mehrfachtreffer:**
- Word: "Liebe und Einheit"
- Level 12 Keywords: ["liebe", "einheit", "love", "unity", "archetypal thinking", "transcending ego"]

```
normalizedWord = "liebe und einheit"

Prüfung:
- "liebe und einheit".includes("liebe") → true → +25
- "liebe und einheit".includes("einheit") → true → +25
- ...

keywordBonus = 50
```

---

### 1.5 Kombination und Normalisierung

Die finale Resonanz kombiniert Frequenz- und Keyword-basierte Resonanz:

```typescript
const totalResonance = Math.min(100, baseResonance + keywordBonus);
resonance[`level_${level.id}`] = parseFloat(totalResonance.toFixed(2));
```

**Beispiel:**
- Level 5: baseResonance = 75 (aus Frequenzberechnung)
- keywordBonus = 25 (ein Keyword-Treffer)

```
totalResonance = Math.min(100, 75 + 25)
               = Math.min(100, 100)
               = 100

resonance['level_5'] = 100.00
```

**Erklärung:**
- Die Gesamtresonanz wird auf maximal 100% begrenzt
- Keyword-Treffer können die Resonanz deutlich verstärken
- Auf 2 Dezimalstellen gerundet für Präzision

**Komplettes Beispiel:**

| Level | Base Resonanz (Frequenz) | Keyword Bonus | Total Resonanz |
|-------|--------------------------|---------------|----------------|
| 1     | 12.34                    | 0             | 12.34          |
| 2     | 45.67                    | 0             | 45.67          |
| 3     | 67.89                    | 0             | 67.89          |
| 4     | 78.23                    | 0             | 78.23          |
| 5     | 89.45                    | 25            | **100.00** (gekippt) |
| 6     | 56.78                    | 0             | 56.78          |
| ...   | ...                      | ...           | ...            |
| 13    | 100.00                   | 0             | 100.00         |

---

### 1.6 Höchste Resonanzebene ermitteln

Nach Berechnung aller 13 Resonanzwerte wird die Ebene mit der höchsten Resonanz ermittelt:

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

**Beispiel:**
```typescript
const resonance = {
  level_1: 12.34,
  level_2: 45.67,
  level_3: 67.89,
  level_4: 78.23,
  level_5: 100.00, // ← Höchste
  level_6: 56.78,
  ...
  level_13: 95.00
};

findHighestResonanceLevel(resonance);
// → { level: 5, value: 100.00 }
```

**Erklärung:**
- Iteriert über alle Resonanzwerte
- Merkt sich Ebene und Wert mit höchstem Wert
- Gibt ID der Ebene (1-13) und Resonanzwert zurück

---

## 2. Potenzberechnung (resonanceAnalysis.ts)

Die Potenzberechnung ermittelt für jede Rate in der DB-Analyse:
- Eine **Potenz** (1-12) basierend auf gewichteter Zufallsauswahl
- Einen **Potenztyp** (D, C, LM, M, F1, F2, F3) basierend auf gewichteter Zufallsauswahl
- Einen **Potenzwert** (z.B. D6, C30, LM15) basierend auf dem Potenztyp
- Eine **Level-Distribution** über 100 Ziehungen
- Die **dominante Ebene** (Ebene mit den meisten Treffern)

---

### 2.1 Level-Gewichte (1-12)

**ACHTUNG:** Die Potenzberechnung verwendet **12 Ebenen** (nicht 13), da die göttliche Ebene (Level 13) aus der Potenzberechnung ausgeschlossen ist.

```typescript
const LEVEL_WEIGHTS = [
  { level: 1, weight: 15 }, // Physical Particles
  { level: 2, weight: 14 }, // Physical Structure
  { level: 3, weight: 13 }, // Etheric Prana
  { level: 4, weight: 12 }, // Etheric Meridians
  { level: 5, weight: 11 }, // Astral Emotions
  { level: 6, weight: 10 }, // Astral Thoughts
  { level: 7, weight: 9 },  // Mental Time
  { level: 8, weight: 8 },  // Mental Constructs
  { level: 9, weight: 7 },  // Causal Blueprints
  { level: 10, weight: 6 }, // Causal Alchemy
  { level: 11, weight: 3 }, // Atmic Identity
  { level: 12, weight: 2 }, // Atmic Love
];

const TOTAL_WEIGHT = 15+14+13+12+11+10+9+8+7+6+3+2 = 110
```

**Wahrscheinlichkeitsverteilung:**

| Level | Gewicht | Wahrscheinlichkeit | Beschreibung |
|-------|---------|-------------------|--------------|
| 1     | 15      | 13.64%            | Physical Particles |
| 2     | 14      | 12.73%            | Physical Structure |
| 3     | 13      | 11.82%            | Etheric Prana |
| 4     | 12      | 10.91%            | Etheric Meridians |
| 5     | 11      | 10.00%            | Astral Emotions |
| 6     | 10      | 9.09%             | Astral Thoughts |
| 7     | 9       | 8.18%             | Mental Time |
| 8     | 8       | 7.27%             | Mental Constructs |
| 9     | 7       | 6.36%             | Causal Blueprints |
| 10    | 6       | 5.45%             | Causal Alchemy |
| 11    | 3       | 2.73%             | Atmic Identity |
| 12    | 2       | 1.82%             | Atmic Love |

**Interpretation:**
- Niedrigere Ebenen (1-6) sind **häufiger** (60% kombiniert)
- Mittlere Ebenen (7-10) sind **moderat häufig** (27% kombiniert)
- Höhere Ebenen (11-12) sind **selten** (4.5% kombiniert)

---

### 2.2 Gewichtete Zufallsauswahl

**Algorithmus:**
```typescript
function weightedPickLevel(): number {
  const r = Math.random() * TOTAL_WEIGHT; // 0 bis 110
  let cumulative = 0;
  
  for (const { level, weight } of LEVEL_WEIGHTS) {
    cumulative += weight;
    if (r < cumulative) {
      return level;
    }
  }
  
  return 1; // Fallback
}
```

**Visualisierung:**

```
Zufallszahl r = Math.random() * 110

Kumulativer Bereich:
0 ─────────── 15 ────── 29 ───── 42 ──── 54 ─── 65 ── 75 ─ 84 ─ 92 ─ 99 ─ 105 ─ 108 ─ 110
    Level 1     Level 2   Level 3  Level 4  L5   L6   L7  L8  L9  L10  L11  L12
   (15 breit)  (14)      (13)     (12)    (11) (10) (9) (8) (7) (6)  (3)  (2)
```

**Beispiel-Ziehungen:**

1. `r = 7.5` → fällt in `[0, 15)` → **Level 1**
2. `r = 20.0` → fällt in `[15, 29)` → **Level 2**
3. `r = 50.0` → fällt in `[42, 54)` → **Level 4**
4. `r = 107.0` → fällt in `[105, 108)` → **Level 11**
5. `r = 109.5` → fällt in `[108, 110)` → **Level 12**

**Schritt-für-Schritt für r = 50.0:**

```
r = 50.0
cumulative = 0

Iteration 1: level=1, weight=15
  cumulative = 0 + 15 = 15
  r (50.0) < cumulative (15)? Nein

Iteration 2: level=2, weight=14
  cumulative = 15 + 14 = 29
  r (50.0) < cumulative (29)? Nein

Iteration 3: level=3, weight=13
  cumulative = 29 + 13 = 42
  r (50.0) < cumulative (42)? Nein

Iteration 4: level=4, weight=12
  cumulative = 42 + 12 = 54
  r (50.0) < cumulative (54)? Ja! ← TREFFER
  → return 4
```

---

### 2.3 Potenztyp-Auswahl

Neben der Ebene (1-12) wird auch ein Potenztyp gewählt:

**Potenztyp-Gewichte:**
```typescript
const POTENCY_TYPE_WEIGHTS = [
  { type: 'D', weight: 30 },  // Dezimal-Potenz (D1-D100)
  { type: 'C', weight: 25 },  // Centesimal-Potenz (C1-C200)
  { type: 'LM', weight: 20 }, // LM-Potenz (LM1-LM30)
  { type: 'M', weight: 15 },  // M-Potenz (M1-M∞, logarithmisch)
  { type: 'F1', weight: 5 },  // Fluxion 1
  { type: 'F2', weight: 3 },  // Fluxion 2
  { type: 'F3', weight: 2 },  // Fluxion 3
];

const TOTAL_POTENCY_WEIGHT = 30+25+20+15+5+3+2 = 100
```

**Wahrscheinlichkeitsverteilung:**

| Typ | Gewicht | Wahrscheinlichkeit | Beschreibung |
|-----|---------|-------------------|--------------|
| D   | 30      | 30.0%             | Dezimal-Potenz (häufigste) |
| C   | 25      | 25.0%             | Centesimal-Potenz |
| LM  | 20      | 20.0%             | LM-Potenz |
| M   | 15      | 15.0%             | M-Potenz |
| F1  | 5       | 5.0%              | Fluxion 1 (selten) |
| F2  | 3       | 3.0%              | Fluxion 2 (sehr selten) |
| F3  | 2       | 2.0%              | Fluxion 3 (extrem selten) |

**Algorithmus (analog zu Level-Auswahl):**
```typescript
function weightedPickPotencyType(): 'D' | 'C' | 'LM' | 'M' | 'F1' | 'F2' | 'F3' {
  const r = Math.random() * 100;
  let cumulative = 0;
  
  for (const { type, weight } of POTENCY_TYPE_WEIGHTS) {
    cumulative += weight;
    if (r < cumulative) {
      return type;
    }
  }
  
  return 'D'; // Fallback
}
```

---

### 2.4 Potenzwert-Generierung

Je nach Potenztyp wird ein spezifischer Wert generiert:

#### Typ D (Dezimal-Potenz)

**Bereich:** D1 - D100  
**Verteilung:** Gleichverteilt mit Gewichtung auf niedrige Werte

```typescript
if (potencyType === 'D') {
  // 70% Chance für D1-D30 (häufigste homöopathische Potenzen)
  if (Math.random() < 0.7) {
    potencyValue = Math.floor(Math.random() * 30) + 1;
  } else {
    // 30% Chance für D31-D100
    potencyValue = Math.floor(Math.random() * 70) + 31;
  }
  potencyString = `D${potencyValue}`;
}
```

**Beispiele:**
- `r1 = 0.3` → 0.3 < 0.7 → niedrige Potenz → `r2 = 0.5` → `D15` ✓
- `r1 = 0.8` → 0.8 ≥ 0.7 → hohe Potenz → `r2 = 0.4` → `D58` ✓

**Wahrscheinlichkeitsverteilung:**
- D1-D30: 70% Chance (je ~2.33% pro Potenz)
- D31-D100: 30% Chance (je ~0.43% pro Potenz)

---

#### Typ C (Centesimal-Potenz)

**Bereich:** C1 - C200  
**Verteilung:** Gleichverteilt mit Gewichtung auf mittlere Werte

```typescript
if (potencyType === 'C') {
  // 60% Chance für C1-C50
  if (Math.random() < 0.6) {
    potencyValue = Math.floor(Math.random() * 50) + 1;
  } else {
    // 40% Chance für C51-C200
    potencyValue = Math.floor(Math.random() * 150) + 51;
  }
  potencyString = `C${potencyValue}`;
}
```

**Beispiele:**
- `r1 = 0.4` → 0.4 < 0.6 → niedrige Potenz → `r2 = 0.7` → `C35` ✓
- `r1 = 0.9` → 0.9 ≥ 0.6 → hohe Potenz → `r2 = 0.5` → `C125` ✓

---

#### Typ LM (Quinquagintamillesimal-Potenz)

**Bereich:** LM1 - LM30  
**Verteilung:** Gleichverteilt

```typescript
if (potencyType === 'LM') {
  potencyValue = Math.floor(Math.random() * 30) + 1;
  potencyString = `LM${potencyValue}`;
}
```

**Beispiele:**
- `r = 0.1` → `LM3` ✓
- `r = 0.9` → `LM27` ✓

---

#### Typ M (M-Potenz)

**Bereich:** M1 - M∞ (theoretisch unbegrenzt)  
**Verteilung:** Logarithmisch (höhere M-Werte werden seltener)

```typescript
if (potencyType === 'M') {
  // Logarithmische Verteilung für sehr hohe Potenzen
  const logValue = Math.random() * 10; // 0-10
  potencyValue = Math.floor(Math.pow(10, logValue)); // 10^0 bis 10^10
  potencyString = `M${potencyValue}`;
}
```

**Mathematik:**
```
logValue = Math.random() * 10  // 0 bis 10
potencyValue = floor(10^logValue)

Beispiele:
- logValue = 0.0 → 10^0.0 = 1 → M1
- logValue = 2.0 → 10^2.0 = 100 → M100
- logValue = 5.0 → 10^5.0 = 100.000 → M100000
- logValue = 9.0 → 10^9.0 = 1.000.000.000 → M1000000000
```

**Wahrscheinlichkeitsverteilung:**
- M1-M10: ~10% (niedrige M-Potenzen)
- M11-M100: ~10% (mittlere M-Potenzen)
- M101-M1000: ~10% (hohe M-Potenzen)
- M1001-M10000: ~10% (sehr hohe M-Potenzen)
- ... (exponentiell ansteigend)

---

#### Typ F1, F2, F3 (Fluxionen)

**Bereich:** F1(1-50), F2(1-100), F3(1-200)  
**Verteilung:** Gleichverteilt innerhalb des jeweiligen Bereichs

```typescript
if (potencyType === 'F1') {
  potencyValue = Math.floor(Math.random() * 50) + 1;
  potencyString = `F1-${potencyValue}`;
}

if (potencyType === 'F2') {
  potencyValue = Math.floor(Math.random() * 100) + 1;
  potencyString = `F2-${potencyValue}`;
}

if (potencyType === 'F3') {
  potencyValue = Math.floor(Math.random() * 200) + 1;
  potencyString = `F3-${potencyValue}`;
}
```

**Beispiele:**
- F1: `F1-12`, `F1-38`, `F1-50`
- F2: `F2-5`, `F2-67`, `F2-99`
- F3: `F3-1`, `F3-123`, `F3-200`

---

### 2.5 Level-Distribution (100 Ziehungen)

Für jede Rate werden **100 gewichtete Zufallsziehungen** durchgeführt, um eine Level-Distribution zu erstellen:

```typescript
// Führe 100 gewichtete Ziehungen durch
const levelDistribution: Record<number, number> = {};
for (let i = 1; i <= 12; i++) {
  levelDistribution[i] = 0;
}

for (let i = 0; i < 100; i++) {
  const pickedLevel = weightedPickLevel();
  levelDistribution[pickedLevel]++;
}
```

**Beispiel-Ablauf:**

| Ziehung | Zufallszahl (r) | Gewähltes Level | Level-Zähler |
|---------|-----------------|-----------------|--------------|
| 1       | 8.5             | 1               | L1: 1 |
| 2       | 22.3            | 2               | L2: 1 |
| 3       | 7.2             | 1               | L1: 2 |
| 4       | 48.9            | 4               | L4: 1 |
| 5       | 106.7           | 11              | L11: 1 |
| ...     | ...             | ...             | ... |
| 100     | 15.1            | 2               | (finale Zähler) |

**Beispiel-Ergebnis nach 100 Ziehungen:**

```typescript
levelDistribution = {
  1: 15,  // 15% der Ziehungen
  2: 13,  // 13%
  3: 12,  // 12%
  4: 11,  // 11%
  5: 10,  // 10%
  6: 9,   // 9%
  7: 8,   // 8%
  8: 7,   // 7%
  9: 6,   // 6%
  10: 5,  // 5%
  11: 3,  // 3%
  12: 1   // 1%
}
```

**Interpretation:**
- Die Verteilung spiegelt die Gewichtung wider (LEVEL_WEIGHTS)
- Niedrigere Ebenen haben mehr Treffer
- Höhere Ebenen haben weniger Treffer

---

### 2.6 Dominante Ebene ermitteln

Die dominante Ebene ist die Ebene mit den **meisten Treffern** in der Level-Distribution:

```typescript
let dominantLevel = 1;
let maxCount = 0;

for (const [level, count] of Object.entries(levelDistribution)) {
  if (count > maxCount) {
    dominantLevel = parseInt(level);
    maxCount = count;
  }
}
```

**Beispiel (aus obiger Distribution):**

```typescript
levelDistribution = {
  1: 15,  // ← Höchste Anzahl
  2: 13,
  3: 12,
  ...
}

Iteration:
- Level 1: count=15 > maxCount=0 → dominantLevel=1, maxCount=15
- Level 2: count=13 < maxCount=15 → keine Änderung
- Level 3: count=12 < maxCount=15 → keine Änderung
- ...

Result: dominantLevel = 1
```

**Komplettes Beispiel-Objekt:**

```typescript
{
  rateName: "Allergie",
  copenRate: 85432187,
  energeticValue: 147.23,
  potency: 5,                    // ← Gewählte Ebene (aus weightedPickLevel)
  potencyType: 'D',              // ← Gewählter Typ (aus weightedPickPotencyType)
  potencyValue: 15,              // ← Generierter Wert (für D-Typ)
  potencyString: 'D15',          // ← Finale Potenzangabe
  levelDistribution: {           // ← 100 Ziehungen
    1: 15, 2: 13, 3: 12, 4: 11,
    5: 10, 6: 9, 7: 8, 8: 7,
    9: 6, 10: 5, 11: 3, 12: 1
  },
  dominantLevel: 1               // ← Ebene mit meisten Treffern
}
```

---

## 3. Integration in DB-Analyse

Die beiden Algorithmen werden in der DB-Analyse wie folgt kombiniert:

### 3.1 Ablauf

1. **Wort-Eingabe:** Benutzer gibt Wort ein (z.B. "Allergie")

2. **Copen-Rate berechnen:**
   ```typescript
   import { calculateCopenRate } from './copenRateGenerator';
   const result = calculateCopenRate(word, 'latin', false, 0);
   // → copenRate = 85432187
   ```

3. **Ebenenresonanz berechnen:**
   ```typescript
   import { calculateLevelResonance, findHighestResonanceLevel } from './levelResonance';
   const resonance = calculateLevelResonance(result.finalRate, word);
   const highest = findHighestResonanceLevel(resonance);
   // → resonance = { level_1: 12.34, level_2: 45.67, ..., level_13: 100.00 }
   // → highest = { level: 13, value: 100.00 }
   ```

4. **Potenz und Level-Distribution berechnen:**
   ```typescript
   import { assignPotencyAndLevels } from './resonanceAnalysis';
   const potencyData = assignPotencyAndLevels(word);
   // → {
   //     potency: 5,
   //     potencyType: 'D',
   //     potencyValue: 15,
   //     potencyString: 'D15',
   //     levelDistribution: { 1: 15, 2: 13, ..., 12: 1 },
   //     dominantLevel: 1
   //   }
   ```

5. **Ergebnis speichern:**
   ```typescript
   const archiveEntry = {
     word: word,
     copen_rate: result.finalRate.toString(),
     tested_potency: potencyData.potencyString, // "D15"
     level_1_physical_particles: resonance.level_1,
     level_2_physical_structure: resonance.level_2,
     // ... alle 13 Ebenen
     level_13_creator: resonance.level_13,
     highest_resonance_level: highest.level, // 13
     highest_resonance_value: highest.value, // 100.00
     // ... weitere Daten
   };
   
   // Speichern in Supabase
   await supabase.from('analysis_archives_v2').insert(archiveEntry);
   ```

---

### 3.2 Datenfluss-Diagramm

```
┌─────────────┐
│ Wort-Input  │
│ "Allergie"  │
└──────┬──────┘
       │
       ├─────────────────────────────────────┐
       ↓                                     ↓
┌──────────────────┐                ┌──────────────────┐
│ calculateCopenRate│                │ Database Lookup  │
│ (copenRateGen.)  │                │ (word_databases) │
└────────┬─────────┘                └────────┬─────────┘
         │                                   │
         │ copenRate: 85432187               │ entries: [...]
         │                                   │
         ├───────────────┬───────────────────┤
         ↓               ↓                   ↓
  ┌──────────────┐ ┌─────────────┐  ┌──────────────┐
  │ Level Resonanz│ │  Potency &  │  │  Parallel    │
  │ (13 Ebenen)  │ │Level Distrib│  │Harmonizations│
  │levelResonance│ │resonanceAnal│  │              │
  └──────┬───────┘ └──────┬──────┘  └──────┬───────┘
         │                │                 │
         │ resonance:     │ potency: D15   │ sessions: []
         │ {level_1: ..., │ dominantLevel:1│
         │  ...,          │                 │
         │  level_13:100} │                 │
         │                │                 │
         └────────┬───────┴─────────────────┘
                  ↓
         ┌────────────────┐
         │  Supabase DB   │
         │analysis_       │
         │archives_v2     │
         └────────────────┘
```

---

## 4. Mathematische Referenz

### 4.1 Resonanzberechnung (Frequenz-basiert)

**Fall 1: Innerhalb des Bereichs**

```
midpoint = (min + max) / 2
distance = |copenRate - midpoint|
range = (max - min) / 2

baseResonance = max(0, 100 - (distance/range) * 50)
```

**Eigenschaften:**
- Am Mittelpunkt: distance = 0 → baseResonance = 100
- An den Grenzen: distance = range → baseResonance = 50
- Lineare Abnahme von 100% (Mittelpunkt) zu 50% (Grenzen)

**Fall 2: Unterhalb des Bereichs**

```
ratio = copenRate / min
baseResonance = max(0, ratio * 40)
```

**Eigenschaften:**
- Lineare Zunahme von 0% (copenRate = 0) zu 40% (copenRate = min)
- Maximum bei 40% Resonanz

**Fall 3: Oberhalb des Bereichs**

```
overshoot = (copenRate - max) / max
baseResonance = max(0, 30 - overshoot * 30)
```

**Eigenschaften:**
- Am Maximum: overshoot = 0 → baseResonance = 30
- Bei copenRate = 2*max: overshoot = 1 → baseResonance = 0
- Lineare Abnahme von 30% zu 0%

---

### 4.2 Gewichtete Zufallsauswahl

**Kumulativer Wahrscheinlichkeitsansatz:**

```
r ~ U(0, TOTAL_WEIGHT)

Für i = 1 bis N:
  c_i = Σ(weight_j) für j=1 bis i
  
  Wenn r < c_i:
    return level_i
```

**Eigenschaften:**
- Jedes Level hat Wahrscheinlichkeit `weight_i / TOTAL_WEIGHT`
- Kumulativer Ansatz ermöglicht effiziente O(N) Auswahl
- Gewichtung kann dynamisch angepasst werden

---

### 4.3 Logarithmische M-Potenz-Verteilung

```
logValue ~ U(0, 10)
potencyValue = floor(10^logValue)
```

**Verteilungseigenschaften:**
- Gleichverteilung im Logarithmusraum
- Exponentielle Verteilung im linearen Raum
- Ermöglicht sehr hohe Potenzen (bis 10^10) bei gleichmäßiger Zufallsauswahl

**Beispiel-Dichte:**

| logValue-Bereich | Potenzwert-Bereich | Wahrscheinlichkeit |
|------------------|--------------------|--------------------|
| 0.0 - 1.0        | 1 - 10             | 10%                |
| 1.0 - 2.0        | 10 - 100           | 10%                |
| 2.0 - 3.0        | 100 - 1.000        | 10%                |
| 3.0 - 4.0        | 1.000 - 10.000     | 10%                |
| ...              | ...                | ...                |
| 9.0 - 10.0       | 10^9 - 10^10       | 10%                |

---

## Zusammenfassung

1. **Ebenenberechnung:**
   - 13 Ebenen (Physical → Etheric → Astral → Mental → Causal → Atmic → Creator)
   - Frequenzbasierte Resonanz (0-100%) basierend auf Copen-Rate
   - Keyword-basierte Resonanz (+25% pro Treffer)
   - Kombination beider Resonanzen (max 100%)

2. **Potenzberechnung:**
   - 12 Ebenen (ohne Creator) mit gewichteter Auswahl
   - 7 Potenztypen (D, C, LM, M, F1, F2, F3) mit unterschiedlichen Wahrscheinlichkeiten
   - Typspezifische Wertgenerierung (D1-D100, C1-C200, LM1-LM30, M1-M∞, F1-F3)
   - 100 Ziehungen für Level-Distribution
   - Dominante Ebene = Ebene mit meisten Treffern

3. **Integration:**
   - Beide Algorithmen arbeiten unabhängig
   - Ebenenresonanz nutzt Copen-Rate + Wort-Keywords
   - Potenzberechnung nutzt gewichtete Zufallsauswahl
   - Ergebnisse werden in `analysis_archives_v2` gespeichert

---

**Ende der Dokumentation**
