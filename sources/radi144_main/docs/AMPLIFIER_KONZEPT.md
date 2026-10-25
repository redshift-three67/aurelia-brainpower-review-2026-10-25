# Amplifier-System – Vollständiges Konzept & Architektur

**Version:** 1.5.0  
**Stand:** 09. Februar 2026  
**Modul:** Resonanz-Verstärker (Amplifier)  
**Status:** Implementiert & Validiert

---

## 1. Konzept-Übersicht

### 1.1 Was ist ein Amplifier?

Ein **Amplifier** (Resonanz-Verstärker) ist ein physisches Objekt – Heilstein, Orgonit-Pyramide, Kristall, Metallelement oder Symbol – das als **zusätzlicher Frequenz-Vektor** in die Harmonisierung eingebracht wird. Er verstärkt die Effektivität der Klienten-spezifischen Resonanzbehandlung durch:

1. **Frequenz-Verstärkung** – Eigene Resonanzfrequenzen des Materials als Audio-Layer
2. **Farbmodulation** – Mineralogische Farbsignatur moduliert die Visualisierungs-Palette
3. **Element-Synergie** – 5-Elemente-Zyklus-basierte Klienten-Zuordnung
4. **Chakra-Korrelation** – Amplifier-Chakra ↔ Klienten-Bio-Vektor
5. **Umfeld-Sensorik** – Bild-basierte Umfeldanalyse (Server-Phase)

### 1.2 Datenfluss (Amplifier im Gesamtsystem)

```
┌──────────────────────────────────────────────────────────────────┐
│                    KLIENTEN-EINGABE                              │
│  Name, Geburtsdatum, Ort, Fokus, Planet                         │
└──────────┬───────────────────────────────────────────────────────┘
           │
           ▼
┌──────────────────────────┐     ┌──────────────────────────────┐
│ ClientSignatureGenerator │     │   AmplifierVectorGenerator   │
│                          │     │                              │
│ → 6 Komponenten:         │     │ → 12D Vektor:                │
│   Name-Freq              │     │   Frequenz [0-3]             │
│   Geburtsdaten           │     │   Element [4]                │
│   Bild-Hash              │     │   Chakra [5]                 │
│   Organuhr               │     │   Verstärkungsfaktor [6]     │
│   Planetarisch           │     │   Solfeggio [7]              │
│   EMF-Korrektur          │     │   Farb-Signatur [8-9]        │
│                          │     │   Kristallsystem [10]        │
│ → Client-Frequenz (Hz)   │     │   Bild-Hash [11]             │
└──────────┬───────────────┘     └──────────┬───────────────────┘
           │                                │
           ▼                                ▼
┌──────────────────────────────────────────────────────────────────┐
│              COSINUS-ÄHNLICHKEIT (Matching)                      │
│                                                                  │
│  Client 12D ←→ Amplifier 12D → Score (0-1)                      │
│  + Element-Synergie-Bonus (5-Elemente-Zyklus)                    │
│  + Property-Match-Bonus (Fokus ↔ Amplifier-Eigenschaften)        │
│                                                                  │
│  Gewichtung: 55% Cosinus + 20% Element + 25% Property           │
│                                                                  │
│  → Top-3 Empfehlung mit Begründungen                            │
└──────────┬───────────────────────────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────────────────────────┐
│                    HARMONISIERUNG                                │
│                                                                  │
│  ┌──────────┐  ┌──────────────┐  ┌──────────────────────────┐   │
│  │ VISUELL  │  │    AUDIO     │  │    AMPLIFIER-MODULATION  │   │
│  │          │  │              │  │                          │   │
│  │ 12x12    │  │ Client-Freq  │  │ + Amplifier-Harmonische  │   │
│  │ Matrix   │  │ + Quinte     │  │   als Audio-Layer        │   │
│  │ mit      │  │ + Solfeggio  │  │ + Palette-Hue-Shift      │   │
│  │ Amplif.  │  │ + Sub-Oktave │  │   Richtung Amplifier     │   │
│  │ modulie- │  │ + EMF-Komp.  │  │ + Verstärkungsfaktor     │   │
│  │ rter     │  │ + Amplifier  │  │   moduliert Amplitude    │   │
│  │ Palette  │  │   Frequenzen │  │                          │   │
│  └──────────┘  └──────────────┘  └──────────────────────────┘   │
└──────────────────────────────────────────────────────────────────┘
```

---

## 2. Amplifier-Vektor (12 Dimensionen)

Jeder Amplifier wird in einen **12-dimensionalen Vektor** transformiert:

| Index | Dimension | Berechnung | Wertebereich |
|-------|-----------|------------|-------------|
| 0-3 | Frequenz-Komponenten | `(harmonic_hz - 20) / 1980` | 0.0 – 1.0 |
| 4 | Element-Affinität | `element_weight / max_weight` | 0.0 – 1.0 |
| 5 | Chakra-Resonanz | `1 - |base_freq - chakra_freq| / 500` | 0.0 – 1.0 |
| 6 | Verstärkungsfaktor | Direkt aus Registry | 0.0 – 1.0 |
| 7 | Solfeggio-Affinität | `(solfeggio - 174) / 789` | 0.0 – 1.0 |
| 8 | Farb-Hue | HSV H-Wert aus `color_hex` | 0.0 – 1.0 |
| 9 | Farb-Sättigung | HSV S-Wert aus `color_hex` | 0.0 – 1.0 |
| 10 | Kristallsystem | Kategorisch kodiert | 0.0 – 1.0 |
| 11 | Bild-Signatur | SHA-256 Hash normalisiert | 0.0 – 1.0 |

---

## 3. Matching-Algorithmus

### 3.1 Klienten-Projektion in Amplifier-Space

Der Klienten-Vektor wird in denselben 12D-Raum projiziert:

| Index | Klienten-Quelle |
|-------|-----------------|
| 0-3 | Client-Frequenz + Quinte + Oktave + Sub-Oktave |
| 4 | Name-Frequenz-Modulo |
| 5 | Bio-Info Frequenz (Meridian/Chakra) |
| 6 | Signatur-Stärke |
| 7 | Nächste Solfeggio-Frequenz |
| 8-9 | Fokus-Hash (Hue + Sättigung) |
| 10 | Tageszeit-Korrelation |
| 11 | EMF-Korrektur-Komponente |

### 3.2 Score-Berechnung

```
Total Score = 0.55 × Cosinus(Client, Amplifier)
            + 0.20 × Element-Synergie
            + 0.25 × Property-Match
```

**Element-Synergie** basiert auf dem 5-Elemente-Nährungs-Zyklus:
- **1.0** → Nährungs-Richtung (Holz→Feuer→Erde→Metall→Wasser→Holz)
- **0.8** → Gleiches Element
- **0.7** → Umgekehrte Nahrung
- **0.4** → Neutral/Kontrolle

**Property-Match** korreliert Fokus-Begriffe mit Amplifier-Eigenschaften über ein semantisches Keyword-Mapping (z.B. "Heilung" → ["heilung", "reinigung", "liebe", "harmonie"]).

---

## 4. Audio-Integration

Die Amplifier-Frequenzen werden als **zusätzliche Sinuswellen-Layer** in die Audio-Engine eingespeist:

```python
# Amplifier-Frequency Layers (Verstärker-Resonanz)
for af in amplifier_freqs[:4]:
    af_hz = af["frequency_hz"]          # z.B. 350 Hz (Rosenquarz Basis)
    af_amp = af["amplitude"] * 0.08     # 8% der Hauptamplitude
    mixed += af_amp * sin(2π × af_hz × t)
```

Die **Amplituden-Kaskade** nimmt mit jeder Harmonischen ab:
- Basis: `amplification_factor × 1.0`
- H1: `amplification_factor × 0.8`
- H2: `amplification_factor × 0.64`
- H3: `amplification_factor × 0.512`

---

## 5. Farbpaletten-Modulation

Die Palette wird **subtil** in Richtung der Amplifier-Farbe verschoben:

```python
new_hue = palette_hue + (amplifier_hue - palette_hue) × 0.15
new_sat = palette_sat + (amplifier_sat - palette_sat) × 0.075
new_val = palette_val + (amplifier_val - palette_val) × 0.045
```

**Stärke:** 15% Hue-Shift, 7.5% Sättigung, 4.5% Helligkeit → Dezent, aber wahrnehmbar.

---

## 6. Umfeld-Sensor (Server-Phase)

### 6.1 Bild-basierte Analyse

```
Referenzbild (registriert)  ←→  Aktuelles Bild (Kamera)
         │                              │
    byte_mean                      byte_mean
    byte_std                       byte_std
    byte_entropy                   byte_entropy
         │                              │
         └──────────────────────────────┘
                      │
         Delta-Analyse (Gewichtet):
         40% Helligkeits-Delta
         30% Variations-Delta
         30% Entropie-Delta
                      │
         Environment Change Score (0-1)
```

### 6.2 Interpretation

| Score | Bedeutung |
|-------|-----------|
| < 0.1 | Umfeld stabil |
| 0.1 – 0.3 | Leichte Variation (Lichtänderung) |
| 0.3 – 0.6 | Moderate Änderung (Lichtquelle/Tageszeit) |
| > 0.6 | Starke Änderung (Standortwechsel) |

---

## 7. Registrierte Amplifier (v1.5.0)

| ID | Name | Kategorie | Basis-Hz | Solfeggio | Element | Chakra | Faktor |
|----|------|-----------|----------|-----------|---------|--------|--------|
| rosenquarz | Rosenquarz | Heilstein | 350 | 639 | Wasser | Herz | 0.75 |
| amethyst | Amethyst | Heilstein | 480 | 852 | Feuer | 3. Auge | 0.85 |
| bergkristall | Bergkristall | Kristall | 528 | 528 | Metall | Krone | 1.00 |
| schwarzer_turmalin | Schwarzer Turmalin | Heilstein | 174 | 174 | Erde | Wurzel | 0.90 |
| schungit | Schungit | Heilstein | 196 | 396 | Erde | Wurzel | 0.95 |
| citrin | Citrin | Heilstein | 320 | 417 | Feuer | Solar | 0.70 |
| lapislazuli | Lapislazuli | Heilstein | 448 | 741 | Wasser | Kehlkopf | 0.80 |
| orgonit_pyramide_schungit | Orgonit-Pyramide (Schungit) | Orgonit | 7.83 | 528 | Erde | Alle | 1.00 |
| orgonit_pyramide_bergkristall | Orgonit-Pyramide (Bergkristall) | Orgonit | 7.83 | 528 | Metall | Alle | 0.95 |
| kupferspirale | Kupferspirale (Tensor-Ring) | Metall | 144 | 285 | Metall | Sakral | 0.65 |
| blume_des_lebens | Blume des Lebens | Symbol | 432 | 963 | Holz | Alle | 0.80 |
| selenit | Selenit | Kristall | 560 | 963 | Wasser | Krone | 0.85 |

---

## 8. API Endpoints

| Method | Endpoint | Beschreibung |
|--------|----------|-------------|
| GET | `/api/v1/amplifier/list` | Alle verfügbaren Amplifier |
| POST | `/api/v1/amplifier/set/{name}` | Aktiven Amplifier setzen |
| POST | `/api/v1/amplifier/clear` | Amplifier deaktivieren |
| POST | `/api/v1/amplifier/match` | Klienten-Matching (Top-N) |
| POST | `/api/v1/amplifier/add` | Neuen Amplifier registrieren |

---

## 9. CLI & PowerShell Integration

### CLI
```bash
python dev_cli.py --surname Mustermann --firstname Max --dob 1990-01-15 \
    --focus "Heilung" --amplifier "rosenquarz" --harmonize --audio
```

### PowerShell
Im interaktiven UI erscheint nach der EMF-Auswahl:
```
Resonanz-Verstärker (Amplifier):
 [0] Keiner
 [1] Rosenquarz (Liebe/Herz)
 [2] Amethyst (Intuition/Klarheit)
 ...
 [9] Selenit (Reinigung)
 Auswahl (0-9) [0]:
```
