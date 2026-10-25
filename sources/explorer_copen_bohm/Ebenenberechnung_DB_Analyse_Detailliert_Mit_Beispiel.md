# Ebenenberechnung in der DB-Analyse - Hochdetaillierte Dokumentation mit Beispiel

## Inhaltsverzeichnis
1. [Übersicht](#übersicht)
2. [Die 13 Ebenen im Detail](#die-13-ebenen-im-detail)
3. [Algorithmus Schritt-für-Schritt](#algorithmus-schritt-für-schritt)
4. [Konkretes Berechnungsbeispiel: "Allergie"](#konkretes-berechnungsbeispiel-allergie)
5. [Mathematische Formeln](#mathematische-formeln)
6. [Code-Implementierung](#code-implementierung)

---

## Übersicht

Die Ebenenberechnung ordnet jeden analysierten Begriff aus der Datenbank einer oder mehreren der 13 kosmologischen Ebenen zu. Diese Zuordnung basiert auf zwei Faktoren:

1. **Frequenzbasierte Resonanz**: Die berechnete Copen-Rate wird mit den Frequenzbereichen der Ebenen verglichen
2. **Keyword-basierte Resonanz**: Das Wort selbst wird mit den Schlüsselwörtern der Ebenen abgeglichen

Das Ergebnis ist ein **Resonanzprofil** mit Prozentwerten (0-100%) für alle 13 Ebenen.

---

## Die 13 Ebenen im Detail

Das System basiert auf einem spirituell-kosmologischen Modell von der physischen bis zur göttlichen Ebene:

### Ebene 1: Physical Realm - Particles
**Deutsche Bezeichnung**: Physische Ebene - Partikel  
**Frequenzbereich**: 1 - 100.000  
**Beschreibung**: Materielle Ebene: Atome, Partikel, Elemente  
**Keywords**: `atom`, `partikel`, `molekül`, `element`, `materie`, `particles`, `atoms`, `matter`, `dna`, `struktur`

### Ebene 2: Physical Realm - Structure
**Deutsche Bezeichnung**: Physische Ebene - Struktur  
**Frequenzbereich**: 100.000 - 500.000  
**Beschreibung**: Physische Struktur: Gewebe, Organe, Körper  
**Keywords**: `körper`, `organ`, `gewebe`, `struktur`, `fascia`, `electromagnetism`, `body`, `tissue`, `structure`

### Ebene 3: Etheric Realm - Prana
**Deutsche Bezeichnung**: Ätherische Ebene - Prana  
**Frequenzbereich**: 500.000 - 1.000.000  
**Beschreibung**: Lebenskraft-Ebene: Qi, Prana, Atmung  
**Keywords**: `prana`, `qi`, `lebenskraft`, `atmung`, `heartbeat`, `breathing`, `life-force`, `energie`

### Ebene 4: Etheric Realm - Meridians
**Deutsche Bezeichnung**: Ätherische Ebene - Meridiane  
**Frequenzbereich**: 1.000.000 - 2.000.000  
**Beschreibung**: Energiekanäle: Meridiane, Chakren (physisch)  
**Keywords**: `meridian`, `chakra`, `energiekanal`, `nadis`, `akupunktur`, `meridians`, `energy channels`

### Ebene 5: Astral Realm - Emotions
**Deutsche Bezeichnung**: Astrale Ebene - Emotionen  
**Frequenzbereich**: 2.000.000 - 3.500.000  
**Beschreibung**: Emotionale Ebene: Gefühle, emotionale Komplexe  
**Keywords**: `emotion`, `gefühl`, `empfindung`, `emotions`, `feelings`, `plasmic archetypes`, `emotional complexes`

### Ebene 6: Astral Realm - Thought-Forms
**Deutsche Bezeichnung**: Astrale Ebene - Gedankenformen  
**Frequenzbereich**: 3.500.000 - 5.000.000  
**Beschreibung**: Gedankenformen: Magnetische Felder, Schwingungsmuster  
**Keywords**: `gedanke`, `thought`, `magnetisch`, `schwingung`, `thought-forms`, `magnetic fields`, `pattern`

### Ebene 7: Mental Realm - Time
**Deutsche Bezeichnung**: Mentale Ebene - Zeit  
**Frequenzbereich**: 5.000.000 - 7.000.000  
**Beschreibung**: Zeitliche Konstrukte: Raum, Form, Farbe  
**Keywords**: `zeit`, `time`, `raum`, `space`, `form`, `shape`, `farbe`, `colour`, `psychons`

### Ebene 8: Mental Realm - Mental Constructs
**Deutsche Bezeichnung**: Mentale Ebene - Mentale Konstrukte  
**Frequenzbereich**: 7.000.000 - 9.000.000  
**Beschreibung**: Mentale Konstrukte: Poetische Felder, Konzepte  
**Keywords**: `konzept`, `idee`, `mental`, `konstrukt`, `mental constructs`, `poetic fields`, `concept`

### Ebene 9: Causal Plane - Blueprints
**Deutsche Bezeichnung**: Kausale Ebene - Blaupausen  
**Frequenzbereich**: 9.000.000 - 11.000.000  
**Beschreibung**: Akasha-Chronik: Destiny Scripts, Blaupausen  
**Keywords**: `akasha`, `blueprint`, `blaupause`, `destiny`, `script`, `akashic`, `blueprints`, `destiny scripts`

### Ebene 10: Causal Plane - Alchemy
**Deutsche Bezeichnung**: Kausale Ebene - Alchemie  
**Frequenzbereich**: 11.000.000 - 13.000.000  
**Beschreibung**: Intention: Alchemische Transformation  
**Keywords**: `intention`, `alchemie`, `alchemy`, `transformation`, `transmutation`, `wandlung`

### Ebene 11: Atmic Plane - Identity
**Deutsche Bezeichnung**: Atmische Ebene - Identität  
**Frequenzbereich**: 13.000.000 - 16.000.000  
**Beschreibung**: Reine Essenz: Unfragmentierte Identität  
**Keywords**: `identität`, `essenz`, `identity`, `essence`, `pure essence`, `unfragmented`, `incarnation`

### Ebene 12: Atmic Plane - Love & Unity
**Deutsche Bezeichnung**: Atmische Ebene - Liebe & Einheit  
**Frequenzbereich**: 16.000.000 - 20.000.000  
**Beschreibung**: Einheit: Liebe, Archetypal Thinking  
**Keywords**: `liebe`, `einheit`, `love`, `unity`, `archetypal thinking`, `transcending ego`

### Ebene 13: Creator - Divinity
**Deutsche Bezeichnung**: Schöpfer - Göttlichkeit  
**Frequenzbereich**: 20.000.000 - ∞  
**Beschreibung**: Göttliche Ebene: Ewigkeit, Wille zum Leben  
**Keywords**: `creator`, `schöpfer`, `göttlich`, `divinity`, `eternity`, `ewigkeit`, `will to life`, `prayers`

---

## Algorithmus Schritt-für-Schritt

### Schritt 1: Eingabedaten
- **Wort**: Der zu analysierende Begriff (z.B. "Allergie")
- **Copen-Rate**: Die berechnete numerische Rate (z.B. 85.432.187)

### Schritt 2: Normalisierung
```typescript
const normalizedWord = word.toLowerCase(); // "allergie"
```

### Schritt 3: Iteration über alle 13 Ebenen

Für jede Ebene wird eine **Gesamt-Resonanz** berechnet, die sich aus zwei Komponenten zusammensetzt:

#### 3.1 Frequenzbasierte Resonanz (baseResonance)

Es gibt **vier verschiedene Fälle**, je nachdem, wo die Copen-Rate im Verhältnis zum Frequenzbereich der Ebene liegt:

**Fall A: Ebene 13 (Göttliche Ebene mit max = ∞)**
```typescript
if (max === Infinity) {
  if (copenRate >= min) {
    baseResonance = 100; // Volle Resonanz
  } else {
    const ratio = copenRate / min;
    baseResonance = Math.max(0, ratio * 50);
  }
}
```

**Fall B: Rate liegt IM Frequenzbereich (min ≤ copenRate ≤ max)**
```typescript
if (copenRate >= min && copenRate <= max) {
  const midpoint = (min + max) / 2;           // Mittelpunkt des Bereichs
  const distance = Math.abs(copenRate - midpoint); // Abstand zum Mittelpunkt
  const range = (max - min) / 2;              // Halbe Bereichsbreite
  baseResonance = Math.max(0, 100 - (distance / range) * 50);
}
```
- **Maximum**: 100% wenn Rate genau auf dem Mittelpunkt liegt
- **Minimum**: 50% an den Bereichsgrenzen
- **Verlauf**: Linear fallend vom Mittelpunkt zu den Grenzen

**Fall C: Rate liegt UNTER dem Bereich (copenRate < min)**
```typescript
if (copenRate < min) {
  const ratio = copenRate / min;
  baseResonance = Math.max(0, ratio * 40);
}
```
- **Maximum**: 40% wenn Rate nahe am Minimum
- **Minimum**: 0% wenn Rate sehr weit unter dem Bereich

**Fall D: Rate liegt ÜBER dem Bereich (copenRate > max)**
```typescript
if (copenRate > max) {
  const overshoot = (copenRate - max) / max;
  baseResonance = Math.max(0, 30 - overshoot * 30);
}
```
- **Maximum**: 30% wenn Rate knapp über dem Maximum
- **Minimum**: 0% wenn Rate sehr weit über dem Bereich

#### 3.2 Keyword-basierte Resonanz (keywordBonus)

```typescript
let keywordBonus = 0;
level.keywords.forEach(keyword => {
  if (normalizedWord.includes(keyword.toLowerCase())) {
    keywordBonus += 25; // +25% pro Treffer
  }
});
```

**Wichtig**: Mehrfache Treffer sind möglich! Wenn ein Wort mehrere Keywords einer Ebene enthält, addieren sich die Boni.

#### 3.3 Kombination und Normalisierung

```typescript
const totalResonance = Math.min(100, baseResonance + keywordBonus);
resonance[`level_${level.id}`] = parseFloat(totalResonance.toFixed(2));
```

- Die Gesamtresonanz ist die **Summe** aus Frequenz- und Keyword-Resonanz
- Maximum ist **100%** (hard cap)
- Ergebnis wird auf **2 Dezimalstellen** gerundet

### Schritt 4: Identifikation der höchsten Resonanz

```typescript
function findHighestResonanceLevel(resonanceValues: Record<string, number>) {
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

---

## Konkretes Berechnungsbeispiel: "Allergie"

### Eingangsdaten
- **Wort**: `"Allergie"`
- **Copen-Rate**: `85.432.187` (beispielhaft berechnet)
- **Normalisiert**: `"allergie"`

---

### Berechnung für jede Ebene

#### **Ebene 1: Physical Particles** (1 - 100.000)

**Frequenzbasierte Resonanz:**
- Rate: 85.432.187
- Bereich: 1 - 100.000
- Fall: **D** (Rate liegt ÜBER dem Bereich)

```
overshoot = (85.432.187 - 100.000) / 100.000
overshoot = 85.332.187 / 100.000
overshoot = 853,32

baseResonance = max(0, 30 - 853,32 * 30)
baseResonance = max(0, 30 - 25.599,6)
baseResonance = 0
```

**Keyword-basierte Resonanz:**
- Keywords: atom, partikel, molekül, element, materie, particles, atoms, matter, dna, struktur
- "allergie" enthält KEINE dieser Keywords
- keywordBonus = 0

**Gesamt-Resonanz:**
```
totalResonance = min(100, 0 + 0) = 0.00%
```

---

#### **Ebene 2: Physical Structure** (100.000 - 500.000)

**Frequenzbasierte Resonanz:**
- Rate: 85.432.187
- Bereich: 100.000 - 500.000
- Fall: **D** (Rate liegt ÜBER dem Bereich)

```
overshoot = (85.432.187 - 500.000) / 500.000
overshoot = 84.932.187 / 500.000
overshoot = 169,86

baseResonance = max(0, 30 - 169,86 * 30)
baseResonance = max(0, 30 - 5.095,8)
baseResonance = 0
```

**Keyword-basierte Resonanz:**
- Keywords: körper, organ, gewebe, struktur, fascia, electromagnetism, body, tissue, structure
- "allergie" enthält KEINE dieser Keywords
- keywordBonus = 0

**Gesamt-Resonanz:**
```
totalResonance = 0.00%
```

---

#### **Ebene 3: Etheric Prana** (500.000 - 1.000.000)

**Frequenzbasierte Resonanz:**
- Rate: 85.432.187
- Bereich: 500.000 - 1.000.000
- Fall: **D** (Rate liegt ÜBER dem Bereich)

```
overshoot = (85.432.187 - 1.000.000) / 1.000.000
overshoot = 84.432.187 / 1.000.000
overshoot = 84,43

baseResonance = max(0, 30 - 84,43 * 30)
baseResonance = max(0, 30 - 2.532,9)
baseResonance = 0
```

**Keyword-basierte Resonanz:**
- Keywords: prana, qi, lebenskraft, atmung, heartbeat, breathing, life-force, energie
- "allergie" enthält das Keyword: **"energie"** (in "all**ergie**")
- keywordBonus = 25

**Gesamt-Resonanz:**
```
totalResonance = min(100, 0 + 25) = 25.00%
```

---

#### **Ebene 4: Etheric Meridians** (1.000.000 - 2.000.000)

**Frequenzbasierte Resonanz:**
- Rate: 85.432.187
- Bereich: 1.000.000 - 2.000.000
- Fall: **D** (Rate liegt ÜBER dem Bereich)

```
overshoot = (85.432.187 - 2.000.000) / 2.000.000
overshoot = 83.432.187 / 2.000.000
overshoot = 41,72

baseResonance = max(0, 30 - 41,72 * 30)
baseResonance = max(0, 30 - 1.251,6)
baseResonance = 0
```

**Keyword-basierte Resonanz:**
- Keywords: meridian, chakra, energiekanal, nadis, akupunktur, meridians, energy channels
- "allergie" enthält KEINE dieser Keywords
- keywordBonus = 0

**Gesamt-Resonanz:**
```
totalResonance = 0.00%
```

---

#### **Ebene 5: Astral Emotions** (2.000.000 - 3.500.000)

**Frequenzbasierte Resonanz:**
- Rate: 85.432.187
- Bereich: 2.000.000 - 3.500.000
- Fall: **D** (Rate liegt ÜBER dem Bereich)

```
overshoot = (85.432.187 - 3.500.000) / 3.500.000
overshoot = 81.932.187 / 3.500.000
overshoot = 23,41

baseResonance = max(0, 30 - 23,41 * 30)
baseResonance = max(0, 30 - 702,3)
baseResonance = 0
```

**Keyword-basierte Resonanz:**
- Keywords: emotion, gefühl, empfindung, emotions, feelings, plasmic archetypes, emotional complexes
- "allergie" enthält KEINE dieser Keywords
- keywordBonus = 0

**Gesamt-Resonanz:**
```
totalResonance = 0.00%
```

---

#### **Ebene 6: Astral Thought-Forms** (3.500.000 - 5.000.000)

**Frequenzbasierte Resonanz:**
- Rate: 85.432.187
- Bereich: 3.500.000 - 5.000.000
- Fall: **D** (Rate liegt ÜBER dem Bereich)

```
overshoot = (85.432.187 - 5.000.000) / 5.000.000
overshoot = 80.432.187 / 5.000.000
overshoot = 16,09

baseResonance = max(0, 30 - 16,09 * 30)
baseResonance = max(0, 30 - 482,7)
baseResonance = 0
```

**Keyword-basierte Resonanz:**
- Keywords: gedanke, thought, magnetisch, schwingung, thought-forms, magnetic fields, pattern
- "allergie" enthält KEINE dieser Keywords
- keywordBonus = 0

**Gesamt-Resonanz:**
```
totalResonance = 0.00%
```

---

#### **Ebene 7: Mental Time** (5.000.000 - 7.000.000)

**Frequenzbasierte Resonanz:**
- Rate: 85.432.187
- Bereich: 5.000.000 - 7.000.000
- Fall: **D** (Rate liegt ÜBER dem Bereich)

```
overshoot = (85.432.187 - 7.000.000) / 7.000.000
overshoot = 78.432.187 / 7.000.000
overshoot = 11,20

baseResonance = max(0, 30 - 11,20 * 30)
baseResonance = max(0, 30 - 336)
baseResonance = 0
```

**Keyword-basierte Resonanz:**
- Keywords: zeit, time, raum, space, form, shape, farbe, colour, psychons
- "allergie" enthält KEINE dieser Keywords
- keywordBonus = 0

**Gesamt-Resonanz:**
```
totalResonance = 0.00%
```

---

#### **Ebene 8: Mental Constructs** (7.000.000 - 9.000.000)

**Frequenzbasierte Resonanz:**
- Rate: 85.432.187
- Bereich: 7.000.000 - 9.000.000
- Fall: **D** (Rate liegt ÜBER dem Bereich)

```
overshoot = (85.432.187 - 9.000.000) / 9.000.000
overshoot = 76.432.187 / 9.000.000
overshoot = 8,49

baseResonance = max(0, 30 - 8,49 * 30)
baseResonance = max(0, 30 - 254,7)
baseResonance = 0
```

**Keyword-basierte Resonanz:**
- Keywords: konzept, idee, mental, konstrukt, mental constructs, poetic fields, concept
- "allergie" enthält KEINE dieser Keywords
- keywordBonus = 0

**Gesamt-Resonanz:**
```
totalResonance = 0.00%
```

---

#### **Ebene 9: Causal Blueprints** (9.000.000 - 11.000.000)

**Frequenzbasierte Resonanz:**
- Rate: 85.432.187
- Bereich: 9.000.000 - 11.000.000
- Fall: **D** (Rate liegt ÜBER dem Bereich)

```
overshoot = (85.432.187 - 11.000.000) / 11.000.000
overshoot = 74.432.187 / 11.000.000
overshoot = 6,77

baseResonance = max(0, 30 - 6,77 * 30)
baseResonance = max(0, 30 - 203,1)
baseResonance = 0
```

**Keyword-basierte Resonanz:**
- Keywords: akasha, blueprint, blaupause, destiny, script, akashic, blueprints, destiny scripts
- "allergie" enthält KEINE dieser Keywords
- keywordBonus = 0

**Gesamt-Resonanz:**
```
totalResonance = 0.00%
```

---

#### **Ebene 10: Causal Alchemy** (11.000.000 - 13.000.000)

**Frequenzbasierte Resonanz:**
- Rate: 85.432.187
- Bereich: 11.000.000 - 13.000.000
- Fall: **D** (Rate liegt ÜBER dem Bereich)

```
overshoot = (85.432.187 - 13.000.000) / 13.000.000
overshoot = 72.432.187 / 13.000.000
overshoot = 5,57

baseResonance = max(0, 30 - 5,57 * 30)
baseResonance = max(0, 30 - 167,1)
baseResonance = 0
```

**Keyword-basierte Resonanz:**
- Keywords: intention, alchemie, alchemy, transformation, transmutation, wandlung
- "allergie" enthält KEINE dieser Keywords
- keywordBonus = 0

**Gesamt-Resonanz:**
```
totalResonance = 0.00%
```

---

#### **Ebene 11: Atmic Identity** (13.000.000 - 16.000.000)

**Frequenzbasierte Resonanz:**
- Rate: 85.432.187
- Bereich: 13.000.000 - 16.000.000
- Fall: **D** (Rate liegt ÜBER dem Bereich)

```
overshoot = (85.432.187 - 16.000.000) / 16.000.000
overshoot = 69.432.187 / 16.000.000
overshoot = 4,34

baseResonance = max(0, 30 - 4,34 * 30)
baseResonance = max(0, 30 - 130,2)
baseResonance = 0
```

**Keyword-basierte Resonanz:**
- Keywords: identität, essenz, identity, essence, pure essence, unfragmented, incarnation
- "allergie" enthält KEINE dieser Keywords
- keywordBonus = 0

**Gesamt-Resonanz:**
```
totalResonance = 0.00%
```

---

#### **Ebene 12: Atmic Love & Unity** (16.000.000 - 20.000.000)

**Frequenzbasierte Resonanz:**
- Rate: 85.432.187
- Bereich: 16.000.000 - 20.000.000
- Fall: **D** (Rate liegt ÜBER dem Bereich)

```
overshoot = (85.432.187 - 20.000.000) / 20.000.000
overshoot = 65.432.187 / 20.000.000
overshoot = 3,27

baseResonance = max(0, 30 - 3,27 * 30)
baseResonance = max(0, 30 - 98,1)
baseResonance = 0
```

**Keyword-basierte Resonanz:**
- Keywords: liebe, einheit, love, unity, archetypal thinking, transcending ego
- "allergie" enthält KEINE dieser Keywords
- keywordBonus = 0

**Gesamt-Resonanz:**
```
totalResonance = 0.00%
```

---

#### **Ebene 13: Creator - Divinity** (20.000.000 - ∞)

**Frequenzbasierte Resonanz:**
- Rate: 85.432.187
- Bereich: 20.000.000 - ∞
- Fall: **A** (Göttliche Ebene)

```
copenRate = 85.432.187
min = 20.000.000

Da copenRate >= min:
baseResonance = 100
```

**Keyword-basierte Resonanz:**
- Keywords: creator, schöpfer, göttlich, divinity, eternity, ewigkeit, will to life, prayers
- "allergie" enthält KEINE dieser Keywords
- keywordBonus = 0

**Gesamt-Resonanz:**
```
totalResonance = min(100, 100 + 0) = 100.00%
```

---

### Ergebnis-Zusammenfassung für "Allergie" (Rate: 85.432.187)

| Ebene | Name | Resonanz | Frequenz | Keyword |
|-------|------|----------|----------|---------|
| 1 | Physical Particles | 0.00% | 0% | 0% |
| 2 | Physical Structure | 0.00% | 0% | 0% |
| 3 | Etheric Prana | **25.00%** | 0% | **25%** |
| 4 | Etheric Meridians | 0.00% | 0% | 0% |
| 5 | Astral Emotions | 0.00% | 0% | 0% |
| 6 | Astral Thought-Forms | 0.00% | 0% | 0% |
| 7 | Mental Time | 0.00% | 0% | 0% |
| 8 | Mental Constructs | 0.00% | 0% | 0% |
| 9 | Causal Blueprints | 0.00% | 0% | 0% |
| 10 | Causal Alchemy | 0.00% | 0% | 0% |
| 11 | Atmic Identity | 0.00% | 0% | 0% |
| 12 | Atmic Love & Unity | 0.00% | 0% | 0% |
| 13 | **Creator - Divinity** | **100.00%** | **100%** | **0%** |

**Höchste Resonanz:**
- **Ebene 13** (Creator - Divinity)
- **Wert**: 100.00%
- **Grund**: Die Copen-Rate von 85.432.187 liegt über der Mindestfrequenz von 20.000.000 für die göttliche Ebene

**Sekundäre Resonanz:**
- **Ebene 3** (Etheric Prana)
- **Wert**: 25.00%
- **Grund**: Das Wort "allergie" enthält das Keyword "energie"

---

## Mathematische Formeln

### Frequenzbasierte Resonanz

**Fall A: Göttliche Ebene (max = ∞)**
```
R_freq = { 100                      wenn rate ≥ min
         { max(0, (rate/min) × 50)  wenn rate < min
```

**Fall B: Rate im Bereich (min ≤ rate ≤ max)**
```
midpoint = (min + max) / 2
distance = |rate - midpoint|
range = (max - min) / 2

R_freq = max(0, 100 - (distance/range) × 50)

Wertebereich: 50% ≤ R_freq ≤ 100%
```

**Fall C: Rate unter dem Bereich (rate < min)**
```
ratio = rate / min
R_freq = max(0, ratio × 40)

Wertebereich: 0% ≤ R_freq ≤ 40%
```

**Fall D: Rate über dem Bereich (rate > max)**
```
overshoot = (rate - max) / max
R_freq = max(0, 30 - overshoot × 30)

Wertebereich: 0% ≤ R_freq ≤ 30%
```

### Keyword-basierte Resonanz

```
R_keyword = Σ (25% pro Keyword-Treffer)

Beispiele:
- 0 Treffer: R_keyword = 0%
- 1 Treffer: R_keyword = 25%
- 2 Treffer: R_keyword = 50%
- 3 Treffer: R_keyword = 75%
- 4+ Treffer: R_keyword = 100% (Cap)
```

### Gesamt-Resonanz

```
R_total = min(100, R_freq + R_keyword)

Maximum ist immer 100%
```

---

## Code-Implementierung

### Vollständiger Algorithmus (TypeScript)

```typescript
/**
 * Berechnet Resonanzwerte für alle 13 Ebenen
 * @param copenRate - Die berechnete Copen-Rate (numerisch)
 * @param word - Das zu analysierende Wort
 * @returns Record mit Resonanzwerten für alle 13 Ebenen
 */
export function calculateLevelResonance(
  copenRate: number,
  word: string
): Record<string, number> {
  const resonance: Record<string, number> = {};
  const normalizedWord = word.toLowerCase();

  LEVELS.forEach(level => {
    let baseResonance = 0;

    // 1. FREQUENZBASIERTE RESONANZ
    const { min, max } = level.frequencyRange;
    
    if (max === Infinity) {
      // Fall A: Göttliche Ebene
      if (copenRate >= min) {
        baseResonance = 100;
      } else {
        const ratio = copenRate / min;
        baseResonance = Math.max(0, ratio * 50);
      }
    } else if (copenRate >= min && copenRate <= max) {
      // Fall B: Rate im Bereich
      const midpoint = (min + max) / 2;
      const distance = Math.abs(copenRate - midpoint);
      const range = (max - min) / 2;
      baseResonance = Math.max(0, 100 - (distance / range) * 50);
    } else if (copenRate < min) {
      // Fall C: Rate unter dem Bereich
      const ratio = copenRate / min;
      baseResonance = Math.max(0, ratio * 40);
    } else {
      // Fall D: Rate über dem Bereich
      if (max > 0) {
        const overshoot = (copenRate - max) / max;
        baseResonance = Math.max(0, 30 - overshoot * 30);
      }
    }

    // 2. KEYWORD-BASIERTE RESONANZ
    let keywordBonus = 0;
    level.keywords.forEach(keyword => {
      if (normalizedWord.includes(keyword.toLowerCase())) {
        keywordBonus += 25;
      }
    });

    // 3. KOMBINATION UND NORMALISIERUNG
    const totalResonance = Math.min(100, baseResonance + keywordBonus);
    
    resonance[`level_${level.id}`] = parseFloat(totalResonance.toFixed(2));
  });

  return resonance;
}

/**
 * Findet die Ebene mit der höchsten Resonanz
 */
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

### Integration in DB-Analyse

```typescript
// In DatabaseManager.tsx oder analyzeWordEnergy()

import { 
  calculateLevelResonance, 
  findHighestResonanceLevel 
} from '@/utils/levelResonance';
import { calculateCopenRate } from '@/utils/copenRateGenerator';

// 1. Copen-Rate berechnen
const copenRate = calculateCopenRate(
  word, 
  potencyLevel, 
  potencyType, 
  personalRate
);

// 2. Ebenen-Resonanz berechnen
const resonanceValues = calculateLevelResonance(copenRate, word);

// 3. Höchste Resonanz ermitteln
const highestResonance = findHighestResonanceLevel(resonanceValues);

// 4. In Datenbank speichern
const analysisData = {
  word: word,
  copen_rate: formatCopenRate(copenRate),
  tested_potency: `${potencyType}${potencyLevel}`,
  
  // Alle 13 Ebenen
  level_1_physical_particles: resonanceValues.level_1,
  level_2_physical_structure: resonanceValues.level_2,
  level_3_etheric_prana: resonanceValues.level_3,
  level_4_etheric_meridians: resonanceValues.level_4,
  level_5_astral_emotions: resonanceValues.level_5,
  level_6_astral_thoughts: resonanceValues.level_6,
  level_7_mental_time: resonanceValues.level_7,
  level_8_mental_constructs: resonanceValues.level_8,
  level_9_causal_blueprints: resonanceValues.level_9,
  level_10_causal_alchemy: resonanceValues.level_10,
  level_11_atmic_identity: resonanceValues.level_11,
  level_12_atmic_love: resonanceValues.level_12,
  level_13_creator: resonanceValues.level_13,
  
  // Höchste Resonanz
  highest_resonance_level: highestResonance.level,
  highest_resonance_value: highestResonance.value
};

await supabase
  .from('analysis_archives_v2')
  .insert(analysisData);
```

---

## Weiteres Beispiel: "Liebe" (Rate: 15.234.567)

### Schnellübersicht

| Ebene | Resonanz | Begründung |
|-------|----------|------------|
| 1-11 | 0-40% | Rate liegt über oder deutlich über Bereich |
| **12** | **75.00%** | **Keyword "liebe" (+25%) + Frequenz nahe Bereich (50%)** |
| **13** | **76.17%** | **Rate unter min, aber nahe (15.234.567/20.000.000 × 50)** |

**Höchste Resonanz**: Ebene 13 (Creator) mit 76.17%

---

## Weitere Beispiele nach Rate

### Niedrige Rate: "DNA" (Rate: 45.678)

**Ergebnis**: Ebene 1 (Physical Particles) - 100.00%
- Grund: Rate liegt perfekt im Bereich 1-100.000
- Keyword-Treffer: "dna" (+25%)

### Mittlere Rate: "Emotion" (Rate: 2.856.432)

**Ergebnis**: Ebene 5 (Astral Emotions) - 100.00%
- Grund: Rate liegt nahe Mittelpunkt des Bereichs 2.000.000-3.500.000
- Keyword-Treffer: "emotion" (+25%)

### Hohe Rate: "Transformation" (Rate: 12.543.876)

**Ergebnis**: Ebene 10 (Causal Alchemy) - 100.00%
- Grund: Rate liegt im Bereich 11.000.000-13.000.000
- Keyword-Treffer: "transformation" (+25%)

---

## Zusammenfassung

Die Ebenenberechnung ist ein **zweistufiger Algorithmus**:

1. **Frequenzbasierte Zuordnung**: Die numerische Copen-Rate wird mit den Frequenzbereichen verglichen
2. **Semantische Verstärkung**: Keyword-Treffer im Wort selbst können die Resonanz um bis zu 100% erhöhen (4 Treffer à 25%)

Das Ergebnis ist ein **multidimensionales Resonanzprofil**, das zeigt, auf welchen kosmologischen Ebenen das analysierte Konzept primär wirkt.

**Typische Muster:**
- Niedrige Raten (< 100.000): Physische Ebenen dominant
- Mittlere Raten (1-10 Mio): Ätherische/Astrale Ebenen
- Hohe Raten (> 20 Mio): Göttliche Ebene mit 100% Resonanz
- Keyword-Treffer: +25% Resonanz-Boost unabhängig von der Frequenz

Die gespeicherten Werte in der Datenbank ermöglichen später eine **multidimensionale Filterung** und **statistische Auswertung** über alle Analyse-Einträge hinweg.
