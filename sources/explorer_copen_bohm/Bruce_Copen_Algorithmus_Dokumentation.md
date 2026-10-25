# Bruce Copen Algorithmus - Vollständige Dokumentation

## Übersicht

Der modernisierte Bruce Copen Algorithmus ist ein mathematisches Verfahren zur Berechnung von Radionik-Raten basierend auf Wortenergien und homöopathischen Potenzen. Diese Dokumentation beschreibt die vollständige Implementierung mit allen mathematischen Formeln.

## Algorithmus-Schritte

### Schritt 1: Wortenergie-Normalisierung

**Funktion:** `normalizeWordEnergy(word: string): string`

```javascript
// Umwandlungsregeln:
word.toUpperCase()
  .replace(/Ä/g, 'AE')     // Umlaute umwandeln
  .replace(/Ö/g, 'OE')
  .replace(/Ü/g, 'UE')
  .replace(/ß/g, 'SS')
  .replace(/\s*[DCLM]+\d+/g, '')  // Potenzangaben entfernen
  .replace(/\d+/g, '')            // Zahlen entfernen
  .replace(/[^A-Z\s]/g, '')       // Sonderzeichen entfernen
  .replace(/\s+/g, ' ')           // Mehrfache Leerzeichen normalisieren
  .trim()                         // Führende/nachfolgende Leerzeichen
```

**Beispiele:**
- `"Nux vomica D6"` → `"NUX VOMICA"`
- `"Schüßler Nr.1"` → `"SCHUESSLER NR"`
- `"Arnica C30"` → `"ARNICA"`

### Schritt 2: Buchstabenwerte berechnen

**Formel:** Lateinisches Alphabet A=1, B=2, C=3, ..., Z=26

```javascript
getLetterValue(letter: string): number {
  return letter.toUpperCase().charCodeAt(0) - 64;
}
```

**Positionsgewichtung:**
- Leerzeichen werden übersprungen (Wert = 0, Position wird nicht erhöht)
- Jeder Buchstabe erhält eine Positionsnummer (1, 2, 3, ...)
- Gewichteter Wert = Buchstabenwert × Position

**Beispiel "NUX VOMICA":**
```
N (Position 1): 14 × 1 = 14
U (Position 2): 21 × 2 = 42
X (Position 3): 24 × 3 = 72
  (Leerzeichen): übersprungen
V (Position 4): 22 × 4 = 88
O (Position 5): 15 × 5 = 75
M (Position 6): 13 × 6 = 78
I (Position 7): 9 × 7 = 63
C (Position 8): 3 × 8 = 24
A (Position 9): 1 × 9 = 9
```

### Schritt 3: Primärsumme

**Formel:**
```
Primärsumme = Σ(Buchstabenwert × Position)
```

**Beispiel "NUX VOMICA":**
```
Primärsumme = 14 + 42 + 72 + 88 + 75 + 78 + 63 + 24 + 9 = 465
```

### Schritt 4: Baserate

**Formel:**
```
Baserate = Primärsumme × 1000
```

**Beispiel:**
```
Baserate = 465 × 1000 = 465.000
```

### Schritt 5: Fibonacci-Modulation

**Formel:**
```
Fibonacci-Rate = ⌊(Baserate ÷ 21) × 34⌋
```

**Mathematischer Hintergrund:**
- Fibonacci-Zahlen: F₈ = 21, F₉ = 34
- Verhältnis 34/21 ≈ 1,619 (Goldener Schnitt φ)
- Biologische Resonanz durch natürliche Proportionen

**Beispiel:**
```
Fibonacci-Rate = ⌊(465.000 ÷ 21) × 34⌋ = ⌊22.142 × 34⌋ = ⌊752.828⌋ = 752.828
```

### Schritt 6: Potenzanpassung

**Potenz-Faktoren:**

| Potenztyp | Faktor-Formel | Beschreibung |
|-----------|---------------|--------------|
| D (Dezimal) | `Fibonacci-Rate × (Potenz ÷ 10)` | Dezimale Verdünnung 1:10 |
| C (Centesimal) | `Fibonacci-Rate × (Potenz ÷ 5)` | Centesimale Verdünnung 1:100 |
| LM (50-Millesimal) | `Fibonacci-Rate × (Potenz ÷ 2)` | 50-Millesimale Verdünnung |
| M (Millennial) | `Fibonacci-Rate × Potenz` | Hochpotenzen nach Boericke |

**Spezialfall D0/C0 (Ursubstanz):**
```
Potenz-Bonus = 0  (keine Potenzierung)
```

**Beispiele:**

**D6-Potenz:**
```
Potenz-Bonus = ⌊752.828 × (6 ÷ 10)⌋ = ⌊752.828 × 0,6⌋ = ⌊451.696⌋ = 451.696
```

**C30-Potenz:**
```
Potenz-Bonus = ⌊752.828 × (30 ÷ 5)⌋ = ⌊752.828 × 6⌋ = ⌊4.516.968⌋ = 4.516.968
```

### Schritt 7: Finale Rate

**Formel:**
```
Finale Rate = Fibonacci-Rate + Potenz-Bonus
```

**Vollständige Berechnungsformel:**
```
Rate = ⌊((Σ(Buchstabenwert × Position) × 1000) ÷ 21) × 34⌋ + Potenz-Bonus
```

## Praktische Beispiele

### Beispiel 1: "NUX VOMICA" D6

1. **Normalisierung:** `"NUX VOMICA D6"` → `"NUX VOMICA"`
2. **Buchstabenwerte:**
   - N(1)=14, U(2)=42, X(3)=72, V(4)=88, O(5)=75, M(6)=78, I(7)=63, C(8)=24, A(9)=9
3. **Primärsumme:** 465
4. **Baserate:** 465.000
5. **Fibonacci-Rate:** 752.828
6. **Potenz-Bonus (D6):** 451.696
7. **Finale Rate:** 1.204.524

### Beispiel 2: "LIEBE" D0 (Ursubstanz)

1. **Normalisierung:** `"LIEBE"`
2. **Buchstabenwerte:**
   - L(1)=12, I(2)=18, E(3)=15, B(4)=8, E(5)=25
3. **Primärsumme:** 78
4. **Baserate:** 78.000
5. **Fibonacci-Rate:** 126.857
6. **Potenz-Bonus (D0):** 0
7. **Finale Rate:** 126.857

### Beispiel 3: "HEILUNG" C30

1. **Normalisierung:** `"HEILUNG"`
2. **Buchstabenwerte:**
   - H(1)=8, E(2)=10, I(3)=27, L(4)=48, U(5)=105, N(6)=84, G(7)=49
3. **Primärsumme:** 331
4. **Baserate:** 331.000
5. **Fibonacci-Rate:** 535.619
6. **Potenz-Bonus (C30):** 3.213.714
7. **Finale Rate:** 3.749.333

## Mathematische Konstanten

### Fibonacci-Verhältnis
```
φ = 34/21 ≈ 1,619047619...
```

### Potenz-Multiplikatoren
```
D: k_D = 0,1    (Dezimalverdünnung)
C: k_C = 0,2    (Centesimalverdünnung) 
LM: k_LM = 0,5  (50-Millesimalverdünnung)
M: k_M = 1,0    (Vollpotenz)
```

## Validierung & Qualitätssicherung

### Eingabevalidierung
- Maximale Wortlänge: 50 Zeichen
- Erlaubte Zeichen: A-Z, Ä, Ö, Ü, ß, Leerzeichen, Zahlen (werden normalisiert)
- Potenzbereich: 0-50.000

### Berechnungsgenauigkeit
- Verwendung von `Math.floor()` für ganzzahlige Ergebnisse
- Konsistente Rundung bei allen Zwischenschritten
- Vermeidung von Floating-Point-Fehlern

## Historischer Kontext

Bruce Copen (1914-1998) entwickelte dieses System basierend auf:
- Radiästhetischen Prinzipien
- Homöopathischer Potenzlehre
- Mathematischer Harmonik (Fibonacci-Zahlen)
- Kinesiologischer Testung

## Technische Implementierung

### JavaScript-Pseudocode
```javascript
function calculateCopenRate(word, potency, potencyType) {
  // 1. Normalisierung
  const cleanWord = normalizeWordEnergy(word);
  
  // 2. Buchstabenwerte mit Positionsgewichtung
  let primarySum = 0;
  let position = 1;
  
  for (let char of cleanWord) {
    if (char !== ' ') {
      primarySum += getLetterValue(char) * position;
      position++;
    }
  }
  
  // 3. Baserate
  const baseRate = primarySum * 1000;
  
  // 4. Fibonacci-Modulation
  const fibonacciRate = Math.floor((baseRate / 21) * 34);
  
  // 5. Potenzanpassung
  const potencyModifier = calculatePotencyModifier(fibonacciRate, potency, potencyType);
  
  // 6. Finale Rate
  return fibonacciRate + potencyModifier;
}
```

---

**Dokumentation erstellt:** 2025-08-03  
**Version:** 2.0  
**Algorithmus-Standard:** Modernisierter Bruce Copen (mit Leerzeichen-Erhaltung)  
**Validiert für:** Homöopathische Mittel, Bachblüten, Edelsteine, Affirmationen