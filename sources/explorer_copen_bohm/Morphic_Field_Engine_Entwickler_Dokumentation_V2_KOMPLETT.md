# Morphische Feld-Engine - Vollständige Entwickler-Dokumentation V2

**Erstellt:** 2026-01-03  
**Version:** 2.0 (Vollständig aktualisiert)  
**Projekt:** Resonance Research Explorer  
**Route:** `/morphic-field`

---

## Inhaltsverzeichnis

1. [Systemübersicht](#1-systemübersicht)
2. [Theoretische Grundlagen](#2-theoretische-grundlagen)
3. [Dateistruktur](#3-dateistruktur)
4. [Detaillierte Komponentendokumentation](#4-detaillierte-komponentendokumentation)
5. [Algorithmen & Berechnungen](#5-algorithmen--berechnungen)
6. [Datenbank-Schema](#6-datenbank-schema)
7. [Typdefinitionen](#7-typdefinitionen)
8. [Schritt-für-Schritt Implementierungsanleitung](#8-schritt-für-schritt-implementierungsanleitung)
9. [Abhängigkeiten](#9-abhängigkeiten)
10. [Test & Validierung](#10-test--validierung)

---

## 1. Systemübersicht

### 1.1 Kernfunktionalität

Die Morphische Feld-Engine ist ein quantenbasiertes Berechnungssystem für morphogenetische Felder, das folgende Hauptfunktionen bietet:

- **Standard-Feldberechnung**: Berechnung basierend auf Wort/Phrase, Geometrie und Intention
- **Klienten-Feldalgorithmus**: Personalisierte Berechnung mit TCM, Bohm-Integration und Patientendaten
- **Hardware-Modulation**: Kozyrev-basierte Torsionsfeld-Verstärkung
- **Integration mit WordEnergyTester**: Vollständige Wortenergie-Analyse für Klienten

### 1.2 Kernformel

```
Ψ_total(x,t) = Σn αn |ψn⟩ e^(-iEnt/ℏ) × C(numerical_sequence) × G(geometric_forms) × I(intention)
```

**Komponenten:**
- `Σn αn |ψn⟩ e^(-iEnt/ℏ)` - Quantenmechanische Superposition
- `C(numerical_sequence)` - Numerischer Faktor (Copen-Raten)
- `G(geometric_forms)` - Geometrischer Faktor (Heilige Geometrie)
- `I(intention)` - Intentions-Faktor

### 1.3 Architektur-Diagramm

```
┌─────────────────────────────────────────────────────────────────┐
│                    MorphicFieldPage.tsx                         │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Theorie-Sektion (Akkordeon)                             │   │
│  │  - Quantenmechanik, Geometrie, Intention, Hardware       │   │
│  └──────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Tabs                                                     │   │
│  │  ├── Standard-Berechnung → MorphicFieldCalculator.tsx    │   │
│  │  └── Klienten-Feldalgorithmus → ClientFieldCalculator.tsx│   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Utils Layer                               │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────────┐ │
│  │morphicFieldEngine│  │clientFieldAlgo. │  │hardwareAlgorithms│ │
│  │        .ts       │  │       .ts       │  │       .ts        │ │
│  └────────┬────────┘  └────────┬────────┘  └────────┬─────────┘ │
│           │                    │                     │          │
│           └────────────────────┼─────────────────────┘          │
│                                ▼                                 │
│                    ┌─────────────────────┐                      │
│                    │ copenRateGenerator  │                      │
│                    │        .ts          │                      │
│                    └─────────┬───────────┘                      │
│                              ▼                                   │
│                    ┌─────────────────────┐                      │
│                    │  alphabetSystems    │                      │
│                    │        .ts          │                      │
│                    └────────────────────┘                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Supabase Backend                            │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────────┐ │
│  │   patients_v2   │  │morphic_field_   │  │morphic_field_    │ │
│  │                 │  │  calculations   │  │   sessions       │ │
│  └─────────────────┘  └─────────────────┘  └──────────────────┘ │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │              Storage: client-signatures                      ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Theoretische Grundlagen

### 2.1 Quantenmechanische Komponente

**Superposition:**
```
Σn αn |ψn⟩ e^(-iEnt/ℏ)
```

- `αn` - Amplituden-Koeffizient für Zustand n
- `|ψn⟩` - Quantenzustand mit Energie En
- `e^(-iEnt/ℏ)` - Zeitliche Evolution (Phasenrotation)
- `ℏ` - Reduzierte Planck-Konstante (1.054571817 × 10⁻³⁴ J·s)

### 2.2 Geometrische Faktoren

| Form | Faktor | Bedeutung |
|------|--------|-----------|
| Tetraeder | 1.618 (φ) | Feuer-Element |
| Würfel | 1.732 (√3) | Erde-Element, Stabilität |
| Oktaeder | 2.000 | Luft-Element, Balance |
| Dodekaeder | 2.618 (φ²) | Äther, universelle Harmonie |
| Ikosaeder | 2.236 (√5) | Wasser-Element, Fluss |
| Merkaba | 3.141 (π) | Lichtkörper-Rotation |
| Torus | 1.414 (√2) | Selbsterhaltung |
| Blume des Lebens | 2.718 (e) | Natürliches Wachstum |
| Sri Yantra | 3.000 | Trinitäts-Verstärkung |

### 2.3 Intentions-Faktoren

| Intention | Faktor | Beschreibung |
|-----------|--------|--------------|
| Heilung | 1.272 (√φ) | Natürliche Wiederherstellung |
| Manifestation | 1.618 (φ) | Goldene Schöpfung |
| Schutz | 1.414 (√2) | Stabiler Schild |
| Transformation | 2.236 (√5) | Dynamische Veränderung |
| Verbindung | 2.000 | Perfekte Einheit |
| Klärung | 1.732 (√3) | Reinigung |
| Aktivierung | 2.718 (e) | Natürliches Erwachen |
| Harmonisierung | 1.618 (φ) | Perfekte Balance |

### 2.4 TCM 5-Elemente System

**Element-Faktoren:**
```typescript
const ELEMENT_FAKTOREN: Record<TCMElement, number> = {
  holz: 1.618,    // φ - Goldener Schnitt
  feuer: 2.236,   // √5
  erde: 1.732,    // √3
  metall: 1.414,  // √2
  wasser: 0.865   // e/π
};
```

**Element-Frequenzbereiche (Hz):**
| Element | Min | Max |
|---------|-----|-----|
| Holz | 3 | 7 |
| Feuer | 8 | 12 |
| Erde | 0 | 3 |
| Metall | 13 | 30 |
| Wasser | 0.5 | 3 |

**Element-Geometrie-Zuordnung:**
| Element | Geometrie |
|---------|-----------|
| Holz | Tetraeder |
| Feuer | Oktaeder |
| Erde | Würfel |
| Metall | Ikosaeder |
| Wasser | Dodekaeder |

**Sheng-Zyklus (Nährender Kreislauf):**
```
Holz → Feuer → Erde → Metall → Wasser → Holz
```

**Ke-Zyklus (Kontrollierender Kreislauf):**
```
Holz → Erde
Feuer → Metall
Erde → Wasser
Metall → Holz
Wasser → Feuer
```

### 2.5 Bohm'sche Ordnung

**David Bohms Holographisches Universum:**

- **Implizite Ordnung**: Ahnenfeld, karmische Potenziale, Ortsbindung, Seelenplan
- **Holomovement**: Dynamische Bewegung zwischen impliziter und expliziter Ordnung (Rate: 7.83 Hz Schumann-Resonanz)
- **Explizite Ordnung**: Symptome, Resonanzpunkte, Harmonisierungsbedarf

**Gesamt-Faktor Berechnung:**
```
Ψ_bohm = (Ψ_impl^0.618 × Ψ_expl^0.382) × cos(ωt)
```

### 2.6 Hardware-Modulation (Kozyrev-Torsionsfelder)

| Metrik | Akkuranz-Bonus | Beschreibung |
|--------|---------------|--------------|
| CPU Quantum Jitter | +2-3% | Mikro-Variationen in CPU-Timing |
| RAM Entropy | +1-2% | Speicher-Fragmentierung |
| Time Source Coherence | +3-4% | Zeit-Drift-Messung |
| GPU Rendering Entropy | +2-3% | Grafische Entropie |
| Network Latency | +1-2% | Netzwerk-Jitter |
| Combined Algorithm | +3-5% | Gewichtete Kombination |

**Gewichtung im Combined Algorithm:**
```typescript
const weights = {
  timeSourceCoherence: 0.30,  // Höchste Priorität
  cpuQuantumJitter: 0.25,
  gpuRenderingEntropy: 0.20,
  ramEntropy: 0.15,
  networkLatency: 0.10
};
```

---

## 3. Dateistruktur

```
src/
├── pages/
│   └── MorphicFieldPage.tsx          # Hauptseite (253 Zeilen)
│
├── components/
│   ├── MorphicFieldCalculator.tsx    # Standard-Kalkulator (299 Zeilen)
│   ├── ClientFieldCalculator.tsx     # Klienten-Kalkulator (997 Zeilen)
│   └── WordEnergyTester.tsx          # Wortenergie-Analyse (importiert)
│
├── utils/
│   ├── morphicFieldEngine.ts         # Kern-Engine (355 Zeilen)
│   ├── clientFieldAlgorithms.ts      # Klienten-Algorithmen (468 Zeilen)
│   ├── copenRateGenerator.ts         # Copen-Raten (723+ Zeilen)
│   ├── hardwareAlgorithms.ts         # Hardware-Modulation (412 Zeilen)
│   └── alphabetSystems.ts            # Alphabet-Systeme (72 Zeilen)
│
└── integrations/supabase/
    └── client.ts                      # Supabase-Client (auto-generiert)
```

---

## 4. Detaillierte Komponentendokumentation

### 4.1 MorphicFieldPage.tsx

**Pfad:** `src/pages/MorphicFieldPage.tsx`  
**Zeilen:** 253

**State:**
```typescript
const [showTheory, setShowTheory] = useState(false);
```

**Struktur:**
1. **Header**
   - Home-Button (Link zu `/`)
   - Titel: "Morphisches Feld-Engine"
   - Theorie-Toggle-Button

2. **Theorie-Sektion** (Collapsible)
   - Formel-Anzeige
   - Akkordeon mit 6 Sektionen:
     - Quantenmechanische Komponente
     - Numerischer Faktor
     - Geometrischer Faktor
     - Intentions-Faktor
     - Hardware-Modulation
     - Integration mit bestehenden Systemen

3. **Calculator-Tabs**
   - Tab 1: "Standard-Berechnung" → `<MorphicFieldCalculator />`
   - Tab 2: "Klienten-Feldalgorithmus" → `<ClientFieldCalculator />`

4. **Footer**

**Verwendete UI-Komponenten:**
- `Card`, `CardContent`, `CardDescription`, `CardHeader`, `CardTitle`
- `Accordion`, `AccordionContent`, `AccordionItem`, `AccordionTrigger`
- `Tabs`, `TabsContent`, `TabsList`, `TabsTrigger`
- `Button`
- Icons: `Home`, `BookOpen`, `User`, `Sparkles`

---

### 4.2 MorphicFieldCalculator.tsx

**Pfad:** `src/components/MorphicFieldCalculator.tsx`  
**Zeilen:** 299

**State:**
```typescript
const [inputWord, setInputWord] = useState('');
const [geometricForm, setGeometricForm] = useState<GeometricForm>('flower_of_life');
const [intention, setIntention] = useState<IntentionType>('harmonization');
const [useHardware, setUseHardware] = useState(true);
const [isCalculating, setIsCalculating] = useState(false);
const [result, setResult] = useState<MorphicFieldResult | null>(null);
```

**Berechnungslogik:**
```typescript
const handleCalculate = async () => {
  if (!inputWord.trim()) return;

  setIsCalculating(true);
  try {
    const numericalSequence = generateSequenceFromWord(inputWord);
    const quantumStates = generateDefaultQuantumStates(5);

    const fieldResult = await calculateMorphicField({
      quantumStates,
      numericalSequence,
      geometricForm,
      intention,
      useHardwareModulation: useHardware
    });

    setResult(fieldResult);
  } catch (error) {
    console.error('Fehler bei morphischer Feldberechnung:', error);
  } finally {
    setIsCalculating(false);
  }
};
```

**Hilfsfunktionen:**
```typescript
const formatScientific = (num: number) => {
  if (num === 0) return '0';
  const exp = Math.floor(Math.log10(Math.abs(num)));
  const mantissa = (num / Math.pow(10, exp)).toFixed(3);
  return `${mantissa} × 10^${exp}`;
};

const formatNumber = (num: number) => {
  if (num < 0.01) return formatScientific(num);
  return num.toFixed(4);
};
```

**Eingabefelder:**
1. Wort/Phrase Input
2. Geometrische Form Select (9 Optionen)
3. Intention Select (8 Optionen)
4. Hardware-Modulation Switch

**Ergebnis-Anzeige:**
- Gesamt-Wellenfunktion Ψ
- Feldstärke
- Kohärenz (Progress-Bar)
- 4 Faktor-Cards: Quanten, Numerisch, Geometrisch, Intention
- Hardware-Faktor (optional)
- Resonanzfrequenz (Hz)
- Zeitstempel

---

### 4.3 ClientFieldCalculator.tsx

**Pfad:** `src/components/ClientFieldCalculator.tsx`  
**Zeilen:** 997

**Konstanten:**
```typescript
const PLANET_LABELS: Record<Planet, string> = {
  sonne: '☀️ Sonne',
  mond: '🌙 Mond',
  merkur: '☿️ Merkur',
  venus: '♀️ Venus',
  mars: '♂️ Mars',
  jupiter: '♃ Jupiter',
  saturn: '♄ Saturn',
  uranus: '⛢ Uranus',
  neptun: '♆ Neptun',
  pluto: '♇ Pluto'
};

const ELEMENT_COLORS: Record<TCMElement, string> = {
  holz: 'bg-green-500',
  feuer: 'bg-red-500',
  erde: 'bg-yellow-600',
  metall: 'bg-gray-400',
  wasser: 'bg-blue-500'
};

const ELEMENT_LABELS: Record<TCMElement, string> = {
  holz: '🌳 Holz',
  feuer: '🔥 Feuer',
  erde: '🌍 Erde',
  metall: '⚙️ Metall',
  wasser: '💧 Wasser'
};
```

**Akkuranz-Matrix:**
```typescript
interface ParameterKombination {
  pflichtFelder: string[];
  optionaleFelder: string[];
  akkuranz: number;
  effektivität: number;
  authentizität: number;
  beschreibung: string;
}

const PARAMETER_KOMBINATIONEN: ParameterKombination[] = [
  {
    pflichtFelder: ['Name', 'Vornamen', 'Geburtsdatum', 'Geburtsort'],
    optionaleFelder: [],
    akkuranz: 72, effektivität: 68, authentizität: 75,
    beschreibung: 'Basis-Konfiguration'
  },
  // ... bis Maximum:
  {
    pflichtFelder: ['Name', 'Vornamen', 'Geburtsdatum', 'Geburtsort'],
    optionaleFelder: ['TCM-Typ', 'Bild-Signatur', 'Geburtsplanet', '5-Elemente-Profil'],
    akkuranz: 97, effektivität: 95, authentizität: 98,
    beschreibung: 'Maximum: Bohm-Optimal'
  }
];
```

**State:**
```typescript
// Basis-Felder
const [nachname, setNachname] = useState('');
const [vornamen, setVornamen] = useState('');
const [geburtsdatum, setGeburtsdatum] = useState('');
const [geburtsort, setGeburtsort] = useState('');

// Optionale Felder
const [tcmTyp, setTcmTyp] = useState<TCMElement | ''>('');
const [geburtsplanet, setGeburtsplanet] = useState<Planet | ''>('');
const [fünfElemente, setFünfElemente] = useState<FünfElementeProfile>({
  holz: 20, feuer: 20, erde: 20, metall: 20, wasser: 20
});
const [showFünfElemente, setShowFünfElemente] = useState(false);

// Bild-Signatur
const [bildSignatur, setBildSignatur] = useState<string>('');
const [bildPreview, setBildPreview] = useState<string>('');
const [isUploading, setIsUploading] = useState(false);

// Patienten-Verknüpfung
const [patients, setPatients] = useState<PatientV2[]>([]);
const [selectedPatientId, setSelectedPatientId] = useState<string>('');
const [isLoadingPatients, setIsLoadingPatients] = useState(false);
const [isSavingToPatient, setIsSavingToPatient] = useState(false);

// UI State
const [showMatrix, setShowMatrix] = useState(false);
const [isCalculating, setIsCalculating] = useState(false);
const [result, setResult] = useState<KlientenFeldErgebnis | null>(null);
```

**Haupt-Funktionen:**

1. **loadPatients()** - Lädt Patienten aus `patients_v2`
2. **handlePatientSelect(patientId)** - Füllt Formular aus Patientenprofil
3. **saveImageToPatient()** - Speichert Bild-Signatur zum Patienten
4. **handleImageUpload(event)** - Upload zu Supabase Storage
5. **handleRemoveImage()** - Entfernt Bild-Signatur
6. **getCurrentConfig()** - Ermittelt aktuelle Akkuranz-Konfiguration
7. **handleCalculate()** - Hauptberechnung via `berechneKlientenFeld()`

**Bild-Upload Workflow:**
```typescript
const handleImageUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
  const file = event.target.files?.[0];
  if (!file) return;

  // Validierung: Typ und Größe (max 5MB)
  if (!file.type.startsWith('image/')) { /* Error */ }
  if (file.size > 5 * 1024 * 1024) { /* Error */ }

  // Upload zu Supabase Storage
  const { data: { user } } = await supabase.auth.getUser();
  const fileName = `${user.id}/${Date.now()}-${randomId}.${fileExt}`;
  
  await supabase.storage
    .from('client-signatures')
    .upload(fileName, file, { cacheControl: '3600', upsert: false });

  // Signierte URL für Vorschau
  const { data: urlData } = await supabase.storage
    .from('client-signatures')
    .createSignedUrl(data.path, 3600);
};
```

**Ergebnis-Integration mit WordEnergyTester:**
```typescript
{result && (
  <WordEnergyTester 
    clientResult={result} 
    clientName={`${vornamen} ${nachname}`.trim()}
    patientId={selectedPatientId || undefined}
    sourceModule="morphic_field"
  />
)}
```

---

## 5. Algorithmen & Berechnungen

### 5.1 morphicFieldEngine.ts

**Pfad:** `src/utils/morphicFieldEngine.ts`  
**Zeilen:** 355

**Konstante:**
```typescript
const HBAR = 1.054571817e-34; // Reduzierte Planck-Konstante
```

**Interfaces:**
```typescript
export interface QuantumState {
  n: number;              // Energy level
  amplitude: number;      // αn
  energy: number;         // En (Joules)
  phase?: number;         // Optional phase offset
}

export interface MorphicFieldConfig {
  quantumStates: QuantumState[];
  numericalSequence: number[];
  geometricForm: GeometricForm;
  intention: IntentionType;
  time?: number;
  useHardwareModulation?: boolean;
}

export interface MorphicFieldResult {
  totalWaveFunction: number;
  quantumComponent: number;
  numericalFactor: number;
  geometricFactor: number;
  intentionFactor: number;
  hardwareFactor?: number;
  coherence: number;
  resonanceFrequency: number;
  fieldStrength: number;
  timestamp: number;
}
```

**Kernfunktionen:**

#### calculateGeometricFactor(form)
```typescript
function calculateGeometricFactor(form: GeometricForm): number {
  const factors: Record<GeometricForm, number> = {
    'tetrahedron': 1.618,    // φ
    'cube': 1.732,           // √3
    'octahedron': 2.000,
    'dodecahedron': 2.618,   // φ²
    'icosahedron': 2.236,    // √5
    'merkaba': 3.141,        // π
    'torus': 1.414,          // √2
    'flower_of_life': 2.718, // e
    'sri_yantra': 3.000
  };
  return factors[form];
}
```

#### calculateIntentionFactor(intention)
```typescript
function calculateIntentionFactor(intention: IntentionType): number {
  const factors: Record<IntentionType, number> = {
    'healing': 1.272,        // √φ
    'manifestation': 1.618,  // φ
    'protection': 1.414,     // √2
    'transformation': 2.236, // √5
    'connection': 2.000,
    'clearing': 1.732,       // √3
    'activation': 2.718,     // e
    'harmonization': 1.618   // φ
  };
  return factors[intention];
}
```

#### calculateNumericalFactor(sequence)
```typescript
function calculateNumericalFactor(sequence: number[]): number {
  if (sequence.length === 0) return 1.0;
  
  // Harmonisches Mittel
  const harmonicSum = sequence.reduce((sum, val) => sum + (1 / (val || 1)), 0);
  const harmonicMean = sequence.length / harmonicSum;
  
  // Geometrisches Mittel
  const product = sequence.reduce((prod, val) => prod * Math.abs(val || 1), 1);
  const geometricMean = Math.pow(product, 1 / sequence.length);
  
  // Normalisierung
  const factor = Math.sqrt(harmonicMean * geometricMean) / 10000;
  return Math.max(0.1, Math.min(10, factor));
}
```

#### calculateQuantumSuperposition(states, time)
```typescript
function calculateQuantumSuperposition(states: QuantumState[], time: number): number {
  if (states.length === 0) return 1.0;
  
  let realPart = 0;
  let imagPart = 0;
  
  for (const state of states) {
    // Phase: e^(-iEnt/ℏ)
    const phase = -(state.energy * time) / HBAR + (state.phase || 0);
    
    // Euler: e^(iθ) = cos(θ) + i*sin(θ)
    realPart += state.amplitude * Math.cos(phase);
    imagPart += state.amplitude * Math.sin(phase);
  }
  
  // Magnitude: |Ψ|
  const magnitude = Math.sqrt(realPart * realPart + imagPart * imagPart);
  return magnitude / Math.sqrt(states.length);
}
```

#### calculateCoherence(...)
```typescript
function calculateCoherence(q, n, g, i): number {
  const factors = [q, n, g, i];
  const mean = factors.reduce((a, b) => a + b, 0) / factors.length;
  const variance = factors.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / factors.length;
  const stdDev = Math.sqrt(variance);
  
  // Niedrigere StdDev = höhere Kohärenz
  return Math.max(0, Math.min(1, 1 / (1 + stdDev)));
}
```

#### calculateResonanceFrequency(...)
```typescript
function calculateResonanceFrequency(quantumStates, numericalSequence): number {
  let baseFreq = 0;
  if (quantumStates.length > 0) {
    const avgEnergy = quantumStates.reduce((sum, s) => sum + s.energy, 0) / quantumStates.length;
    baseFreq = avgEnergy / HBAR;
  }
  
  let seqModulation = 1;
  if (numericalSequence.length > 0) {
    const avgSeq = numericalSequence.reduce((a, b) => a + b, 0) / numericalSequence.length;
    seqModulation = avgSeq / 1000000;
  }
  
  const frequency = Math.abs(baseFreq * seqModulation);
  return Math.max(1, Math.min(1e6, frequency));
}
```

#### calculateMorphicField(config) - HAUPTFUNKTION
```typescript
export async function calculateMorphicField(config: MorphicFieldConfig): Promise<MorphicFieldResult> {
  const time = config.time || Date.now();
  
  // Phase 1: Quantum Superposition
  const quantumComponent = calculateQuantumSuperposition(config.quantumStates, time);
  
  // Phase 2: Numerical Factor
  const numericalFactor = calculateNumericalFactor(config.numericalSequence);
  
  // Phase 3: Geometric Factor
  const geometricFactor = calculateGeometricFactor(config.geometricForm);
  
  // Phase 4: Intention Factor
  const intentionFactor = calculateIntentionFactor(config.intention);
  
  // Phase 5: Hardware Modulation (optional)
  let hardwareFactor = 1.0;
  if (config.useHardwareModulation) {
    const metrics = await collectHardwareMetrics();
    hardwareFactor = 1 + (metrics.combinedScore / 100);
  }
  
  // Total Wave Function
  const totalWaveFunction = 
    quantumComponent * numericalFactor * geometricFactor * intentionFactor * hardwareFactor;
  
  // Field Properties
  const coherence = calculateCoherence(quantumComponent, numericalFactor, geometricFactor, intentionFactor);
  const resonanceFrequency = calculateResonanceFrequency(config.quantumStates, config.numericalSequence);
  const fieldStrength = totalWaveFunction * coherence;
  
  return {
    totalWaveFunction, quantumComponent, numericalFactor, geometricFactor, intentionFactor,
    hardwareFactor: config.useHardwareModulation ? hardwareFactor : undefined,
    coherence, resonanceFrequency, fieldStrength, timestamp: time
  };
}
```

#### Hilfsfunktionen:
```typescript
export function generateDefaultQuantumStates(count: number = 5): QuantumState[] {
  const states: QuantumState[] = [];
  for (let n = 1; n <= count; n++) {
    states.push({
      n,
      amplitude: 1 / Math.sqrt(count),
      energy: n * 1.6e-19 * n,
      phase: (n * Math.PI) / count
    });
  }
  return states;
}

export function generateSequenceFromWord(word: string): number[] {
  const words = word.split(/\s+/).filter(w => w.length > 0);
  return words.map(w => calculateCopenRate(w, 1, 'D', 'latin').rate);
}

export async function testMorphicResonance(config1, config2): Promise<number> {
  const result1 = await calculateMorphicField(config1);
  const result2 = await calculateMorphicField(config2);
  
  const freqRatio = Math.min(r1.resonanceFrequency / r2.resonanceFrequency, r2/r1);
  const strengthRatio = Math.min(r1.fieldStrength / r2.fieldStrength, r2/r1);
  const coherenceAvg = (r1.coherence + r2.coherence) / 2;
  
  return Math.max(0, Math.min(1, freqRatio * 0.4 + strengthRatio * 0.4 + coherenceAvg * 0.2));
}
```

---

### 5.2 clientFieldAlgorithms.ts

**Pfad:** `src/utils/clientFieldAlgorithms.ts`  
**Zeilen:** 468

**Typen:**
```typescript
export type TCMElement = 'holz' | 'feuer' | 'erde' | 'metall' | 'wasser';
export type Planet = 'sonne' | 'mond' | 'merkur' | 'venus' | 'mars' | 'jupiter' | 'saturn' | 'uranus' | 'neptun' | 'pluto';

export interface FünfElementeProfile {
  holz: number;   // 0-100
  feuer: number;
  erde: number;
  metall: number;
  wasser: number;
}

export interface KlientenDaten {
  nachname: string;
  vornamen: string[];
  geburtsdatum: Date;
  geburtsort: string;
  bildSignatur?: string;
  tcmTyp?: TCMElement;
  geburtsplanet?: Planet;
  fünfElemente?: FünfElementeProfile;
}

export interface BohmIntegration {
  impliziteOrdnung: {
    ahnenfeld: number;
    karmischePotenziale: number;
    ortsbindung: number;
    seelenplan: number;
  };
  holomovement: {
    rate: number;     // 7.83 Hz (Schumann)
    phase: number;
    kohärenz: number;
  };
  expliziteOrdnung: {
    symptome: string[];
    resonanzpunkte: number[];
    harmonisierungsbedarf: number;
  };
  gesamtFaktor: number;
}

export interface TCMAnalyse {
  dominantesElement: TCMElement;
  elementVerteilung: FünfElementeProfile;
  shengFaktor: number;
  keFaktor: number;
  meridianEmpfehlungen: MeridianPunkt[];
  frequenzbereich: { min: number; max: number };
  gesamtFaktor: number;
}

export interface MeridianPunkt {
  name: string;
  kürzel: string;  // LV, HT, SP, etc.
  nummer: number;
  element: TCMElement;
  typ: 'xi-cleft' | 'shu' | 'source' | 'luo';
}

export interface PersönlicheSignatur {
  nachnameRate: number;
  vornamenRates: number[];
  vornamenMittel: number;
  zeitFaktor: number;
  geoFaktor: number;
  bildBonus: number;
  copenSequenz: number[];
  gesamtFaktor: number;
}

export interface KlientenFeldErgebnis extends MorphicFieldResult {
  persönlicheSignatur: PersönlicheSignatur;
  bohmIntegration: BohmIntegration;
  tcmAnalyse: TCMAnalyse;
  klientenWellenfunktion: number;
  empfehlungen: {
    geometrie: GeometricForm;
    intention: IntentionType;
    meridianPunkte: MeridianPunkt[];
    frequenzen: number[];
  };
}
```

**Meridian-Punkte Datenbank:**
```typescript
const MERIDIAN_PUNKTE: MeridianPunkt[] = [
  // Holz
  { name: 'Taichong', kürzel: 'LV', nummer: 3, element: 'holz', typ: 'source' },
  { name: 'Zhongfeng', kürzel: 'LV', nummer: 4, element: 'holz', typ: 'xi-cleft' },
  { name: 'Yanglingquan', kürzel: 'GB', nummer: 34, element: 'holz', typ: 'shu' },
  // Feuer
  { name: 'Shenmen', kürzel: 'HT', nummer: 7, element: 'feuer', typ: 'source' },
  { name: 'Yinxi', kürzel: 'HT', nummer: 6, element: 'feuer', typ: 'xi-cleft' },
  { name: 'Houxi', kürzel: 'SI', nummer: 3, element: 'feuer', typ: 'source' },
  // Erde
  { name: 'Taibai', kürzel: 'SP', nummer: 3, element: 'erde', typ: 'source' },
  { name: 'Diji', kürzel: 'SP', nummer: 8, element: 'erde', typ: 'xi-cleft' },
  { name: 'Zusanli', kürzel: 'ST', nummer: 36, element: 'erde', typ: 'shu' },
  // Metall
  { name: 'Taiyuan', kürzel: 'LU', nummer: 9, element: 'metall', typ: 'source' },
  { name: 'Kongzui', kürzel: 'LU', nummer: 6, element: 'metall', typ: 'xi-cleft' },
  { name: 'Hegu', kürzel: 'LI', nummer: 4, element: 'metall', typ: 'source' },
  // Wasser
  { name: 'Taixi', kürzel: 'KI', nummer: 3, element: 'wasser', typ: 'source' },
  { name: 'Shuiquan', kürzel: 'KI', nummer: 5, element: 'wasser', typ: 'xi-cleft' },
  { name: 'Zhiyin', kürzel: 'BL', nummer: 67, element: 'wasser', typ: 'source' }
];
```

**Planet-Faktoren:**
```typescript
const PLANET_FAKTOREN: Record<Planet, number> = {
  sonne: 1.0,
  mond: 0.272,
  merkur: 0.055,
  venus: 0.815,
  mars: 0.532,
  jupiter: 11.209,
  saturn: 9.449,
  uranus: 4.007,
  neptun: 3.883,
  pluto: 0.178
};
```

**Kernfunktionen:**

#### berechnePersönlicheSignatur(klient)
```typescript
export function berechnePersönlicheSignatur(klient: KlientenDaten): PersönlicheSignatur {
  const nachnameRate = calculateCopenRate(klient.nachname, 1, 'D', 'latin').rate;
  
  const vornamenRates = klient.vornamen.map(v => 
    calculateCopenRate(v, 1, 'D', 'latin').rate
  );
  const vornamenMittel = vornamenRates.reduce((a, b) => a + b, 0) / vornamenRates.length;
  
  const dayOfYear = getDayOfYear(klient.geburtsdatum);
  const hourOfBirth = klient.geburtsdatum.getHours() || 12;
  const zeitFaktor = Math.cos(2 * Math.PI * dayOfYear / 365) * 
                     Math.sin(2 * Math.PI * hourOfBirth / 24) * 0.5 + 0.5;
  
  const geoFaktor = berechneGeoFaktor(klient.geburtsort);
  const bildBonus = klient.bildSignatur ? 0.1 : 0;
  const copenSequenz = [nachnameRate, ...vornamenRates];
  
  const gesamtFaktor = Math.sqrt(nachnameRate * vornamenMittel) / 1e9 * 
                       (0.5 + zeitFaktor * 0.5) * 
                       (0.5 + geoFaktor * 0.5) * 
                       (1 + bildBonus);
  
  return {
    nachnameRate, vornamenRates, vornamenMittel,
    zeitFaktor, geoFaktor, bildBonus, copenSequenz, gesamtFaktor
  };
}
```

#### berechneBohmIntegration(signatur, klient)
```typescript
export function berechneBohmIntegration(signatur, klient): BohmIntegration {
  // Implizite Ordnung
  const ahnenfeld = signatur.nachnameRate / 1e10;
  const karmischePotenziale = signatur.zeitFaktor * 0.8 + 0.2;
  const ortsbindung = signatur.geoFaktor;
  const seelenplan = signatur.vornamenMittel / 1e10;
  
  // Holomovement
  const rate = 7.83; // Schumann-Resonanz
  const phase = (Date.now() % (2 * Math.PI * 1000)) / 1000;
  const kohärenz = 1 / (1 + Math.abs(ahnenfeld - seelenplan) * 10);
  
  // Explizite Ordnung
  const resonanzpunkte = signatur.copenSequenz.map(r => r % 1000);
  const harmonisierungsbedarf = 1 - kohärenz;
  
  // Gesamt-Faktor: (Ψ_impl^0.618 × Ψ_expl^0.382) × cos(ωt)
  const psi_impl = ahnenfeld * karmischePotenziale * ortsbindung;
  const psi_expl = seelenplan * signatur.zeitFaktor;
  const gesamtFaktor = Math.pow(psi_impl, 0.618) * Math.pow(psi_expl, 0.382) * 
                       Math.cos(rate * phase) * 1e5;
  
  return {
    impliziteOrdnung: { ahnenfeld, karmischePotenziale, ortsbindung, seelenplan },
    holomovement: { rate, phase, kohärenz },
    expliziteOrdnung: { symptome: [], resonanzpunkte, harmonisierungsbedarf },
    gesamtFaktor: Math.max(0.1, Math.min(10, gesamtFaktor))
  };
}
```

#### berechneTCMAnalyse(klient)
```typescript
export function berechneTCMAnalyse(klient: KlientenDaten): TCMAnalyse {
  let elementVerteilung: FünfElementeProfile;
  
  if (klient.fünfElemente) {
    elementVerteilung = klient.fünfElemente;
  } else if (klient.tcmTyp) {
    elementVerteilung = erstelleElementProfilAusTyp(klient.tcmTyp);
  } else {
    elementVerteilung = berechneElementeAusGeburt(klient.geburtsdatum);
  }
  
  // Dominantes Element
  const dominantesElement = (Object.entries(elementVerteilung) as [TCMElement, number][])
    .sort((a, b) => b[1] - a[1])[0][0];
  
  // Sheng-Faktor
  const shengIndex = (SHENG_ZYKLUS.indexOf(dominantesElement) - 1 + 5) % 5;
  const nährendesElement = SHENG_ZYKLUS[shengIndex];
  const shengFaktor = ELEMENT_FAKTOREN[nährendesElement] * 1.272;
  
  // Ke-Faktor
  const kontrollierendesElement = Object.entries(KE_ZYKLUS)
    .find(([_, v]) => v === dominantesElement)?.[0] as TCMElement || 'holz';
  const keFaktor = ELEMENT_FAKTOREN[kontrollierendesElement] / 
                   ELEMENT_FAKTOREN[dominantesElement] * 0.786;
  
  // Meridian-Empfehlungen
  const meridianEmpfehlungen = MERIDIAN_PUNKTE.filter(m => 
    m.element === dominantesElement || m.element === nährendesElement
  );
  
  // Gesamt-Faktor
  const gesamtFaktor = ELEMENT_FAKTOREN[dominantesElement] * 
                       (1 + shengFaktor / 5 - keFaktor / 5);
  
  return {
    dominantesElement, elementVerteilung, shengFaktor, keFaktor,
    meridianEmpfehlungen, frequenzbereich: ELEMENT_FREQUENZEN[dominantesElement],
    gesamtFaktor
  };
}
```

#### berechneKlientenFeld(klient, intention?, geometrie?) - HAUPTFUNKTION
```typescript
export async function berechneKlientenFeld(
  klient: KlientenDaten,
  intention: IntentionType = 'harmonization',
  geometrie?: GeometricForm
): Promise<KlientenFeldErgebnis> {
  // 1. Persönliche Signatur
  const persönlicheSignatur = berechnePersönlicheSignatur(klient);
  
  // 2. Bohm-Integration
  const bohmIntegration = berechneBohmIntegration(persönlicheSignatur, klient);
  
  // 3. TCM-Analyse
  const tcmAnalyse = berechneTCMAnalyse(klient);
  
  // 4. Geometrie
  const verwendeteGeometrie = geometrie || ELEMENT_GEOMETRIE[tcmAnalyse.dominantesElement];
  
  // 5. Morphisches Feld
  const feldErgebnis = await calculateMorphicField({
    quantumStates: generateDefaultQuantumStates(5),
    numericalSequence: persönlicheSignatur.copenSequenz,
    geometricForm: verwendeteGeometrie,
    intention,
    useHardwareModulation: true
  });
  
  // 6. Klienten-Wellenfunktion
  const klientenWellenfunktion = feldErgebnis.totalWaveFunction * 
                                  persönlicheSignatur.gesamtFaktor * 
                                  bohmIntegration.gesamtFaktor * 
                                  tcmAnalyse.gesamtFaktor;
  
  // 7. Empfehlungen
  const empfehlungen = generiereEmpfehlungen(tcmAnalyse, bohmIntegration);
  
  return {
    ...feldErgebnis,
    persönlicheSignatur, bohmIntegration, tcmAnalyse,
    klientenWellenfunktion, empfehlungen
  };
}
```

---

### 5.3 copenRateGenerator.ts

**Pfad:** `src/utils/copenRateGenerator.ts`  
**Zeilen:** 723+

**Bruce Copen V4 Algorithmus:**
```typescript
export const calculateCopenRate = (
  word: string,
  potency: number,
  potencyType: 'D' | 'C' | 'LM' | 'M' | 'F1' | 'F2' | 'F3',
  alphabetType: AlphabetType = 'latin',
  imageSignature?: string,
  useImageSignature: boolean = false,
  useAdaptiveFibonacci: boolean = false
): CopenRateResult => {
  
  // 1) Normalisierung
  const normalize = (w: string) =>
    w.toUpperCase()
      .replace(/Ä/g, 'AE').replace(/Ö/g, 'OE').replace(/Ü/g, 'UE').replace(/ß/g, 'SS')
      .replace(/\s*[DCLMF]+\d+/g, '')  // Potenzangaben entfernen
      .replace(/[^A-Z0-9]/g, '')        // Nur Buchstaben + Zahlen
      .trim();

  // Zeichenwert
  const getCharValue = (ch: string): number => {
    if (ch >= 'A' && ch <= 'Z') return ch.charCodeAt(0) - 64;
    if (ch >= '0' && ch <= '9') return parseInt(ch, 10);
    return 0;
  };

  // 2) Primärsumme (positionsgewichtet)
  const computePrimarySum = (text: string) => {
    let sum = 0, pos = 1;
    for (const ch of text) {
      sum += getCharValue(ch) * pos;
      pos++;
    }
    return sum;
  };

  const cleanWord = normalize(word);
  let primarySum = computePrimarySum(cleanWord);

  // Bildsignatur-Integration (optional)
  if (useImageSignature && imageSignature) {
    const imgPrimary = computePrimarySum(normalize(imageSignature));
    primarySum = Math.floor((primarySum + imgPrimary) / 2);
  }

  // 3) Baserate
  const baseRate = primarySum * 1000;
  
  // 4) Fibonacci-Modulation
  let fibonacciRate: number;
  if (useAdaptiveFibonacci) {
    const pair = getAdaptiveFibonacciPair(cleanWord.length);
    fibonacciRate = Math.floor((baseRate / pair.div) * pair.mult);
  } else {
    fibonacciRate = Math.floor((baseRate / 21) * 34); // Original Copen
  }

  // 5) Potenz-Bonus
  let potencyBonus = 0;
  const p = Math.max(0, potency);
  if (p > 0) {
    switch (potencyType) {
      case 'D':  potencyBonus = Math.floor(fibonacciRate * (p / 10)); break;
      case 'C':  potencyBonus = Math.floor(fibonacciRate * (p / 5)); break;
      case 'LM': potencyBonus = Math.floor(fibonacciRate * (p / 2)); break;
      case 'M':  potencyBonus = Math.floor(fibonacciRate * p); break;
      case 'F1': potencyBonus = Math.floor(fibonacciRate * (p / 6)); break;
      case 'F2': potencyBonus = Math.floor(fibonacciRate * (p / 4)); break;
      case 'F3': potencyBonus = Math.floor(fibonacciRate * (p / 3)); break;
    }
  }

  return {
    word, potency, potencyType, alphabetType,
    rate: fibonacciRate + potencyBonus,
    calculation: { letterSum: primarySum, baseRate, fibonacciRate },
    isAdaptive: useAdaptiveFibonacci
  };
};
```

**Adaptive Fibonacci-Paare:**
```typescript
export const getAdaptiveFibonacciPair = (wordLength: number): { div: number; mult: number } => {
  if (wordLength <= 0) return { div: 21, mult: 34 };
  if (wordLength >= 1 && wordLength <= 4) return { div: 13, mult: 21 };   // Kurze Wörter
  if (wordLength >= 5 && wordLength <= 10) return { div: 21, mult: 34 }; // Standard
  if (wordLength >= 11 && wordLength <= 20) return { div: 34, mult: 55 };// Lange Wörter
  return { div: 55, mult: 89 }; // Sehr lange Wörter
};
```

---

### 5.4 hardwareAlgorithms.ts

**Pfad:** `src/utils/hardwareAlgorithms.ts`  
**Zeilen:** 412

**Interface:**
```typescript
export interface HardwareMetrics {
  cpuQuantumJitter: number;      // 0.0 - 1.0
  ramEntropy: number;            // 0.0 - 1.0
  timeSourceCoherence: number;   // 0.0 - 1.0
  gpuRenderingEntropy: number;   // 0.0 - 1.0
  networkLatency: number;        // 0.0 - 1.0
  combinedScore: number;         // 0.0 - 1.0
}

export interface HardwareConfig {
  cpuQuantumJitter: 'auto' | 'on' | 'off';
  ramEntropy: 'auto' | 'on' | 'off';
  timeSourceCoherence: 'auto' | 'on' | 'off';
  gpuRenderingEntropy: 'auto' | 'on' | 'off';
  networkLatency: 'auto' | 'on' | 'off';
  combinedAlgorithm: 'auto' | 'on' | 'off';
}
```

**Metriken-Sammlung:**
```typescript
export async function collectHardwareMetrics(): Promise<HardwareMetrics> {
  // Cache-Prüfung (5 Sekunden)
  if (metricsCache && Date.now() - metricsCache.timestamp < 5000) {
    return metricsCache.metrics;
  }
  
  const [gpuEntropy, networkJitter] = await Promise.all([
    getGPURenderingEntropy(),
    getNetworkLatency()
  ]);
  
  const metrics: HardwareMetrics = {
    cpuQuantumJitter: getCPUQuantumJitter(),
    ramEntropy: getRAMEntropy(),
    timeSourceCoherence: getTimeSourceCoherence(),
    gpuRenderingEntropy: gpuEntropy,
    networkLatency: networkJitter,
    combinedScore: 0
  };
  
  metrics.combinedScore = calculateCombinedScore(metrics);
  metricsCache = { metrics, timestamp: Date.now() };
  
  return metrics;
}
```

---

### 5.5 alphabetSystems.ts

**Pfad:** `src/utils/alphabetSystems.ts`  
**Zeilen:** 72

```typescript
export type AlphabetType = 'latin' | 'altdeutsch-gotisch' | 'altdeutsch-mittelhochdeutsch' | 'runisch';

export interface AlphabetSystem {
  name: string;
  description: string;
  letterValues: Record<string, number>;
}

export const alphabetSystems: Record<AlphabetType, AlphabetSystem> = {
  'latin': {
    name: 'Lateinisches Alphabet',
    description: 'Standard A=1, B=2, C=3... (Original Copen)',
    letterValues: { 'A': 1, 'B': 2, ..., 'Z': 26 }
  },
  'altdeutsch-gotisch': {
    name: 'Altdeutsch (Gotische Schrift)',
    description: 'Fraktur mit Umlauten',
    letterValues: { ..., 'Ä': 27, 'Ö': 28, 'Ü': 29, 'ß': 30 }
  },
  'altdeutsch-mittelhochdeutsch': {
    name: 'Altdeutsch (Mittelhochdeutsch)',
    description: 'Historisches 21-Buchstaben-Alphabet',
    letterValues: { ... }
  },
  'runisch': {
    name: 'Runenschrift (Elder Futhark)',
    description: 'Germanische Runen mit 24 Zeichen',
    letterValues: { 'F': 1, 'U': 2, 'TH': 3, ... }
  }
};

export const calculateLetterSum = (word: string, alphabetType: AlphabetType = 'latin'): number => {
  const system = alphabetSystems[alphabetType];
  
  // Zahlen im Text extrahieren und addieren
  const numberMatches = word.match(/\d+/g);
  let numberSum = numberMatches ? numberMatches.reduce((sum, n) => sum + parseInt(n), 0) : 0;
  
  const cleanWord = word.toUpperCase().replace(/[^A-ZÜÄÖ]/g, '');
  let sum = 0;
  for (const char of cleanWord) {
    if (system.letterValues[char]) sum += system.letterValues[char];
  }
  
  return sum + numberSum;
};
```

---

## 6. Datenbank-Schema

### 6.1 patients_v2

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
  personal_rate TEXT,
  hardware_config JSONB,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- RLS Policies
ALTER TABLE public.patients_v2 ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own patients v2" 
  ON public.patients_v2 FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert their own patients v2" 
  ON public.patients_v2 FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update their own patients v2" 
  ON public.patients_v2 FOR UPDATE USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can delete their own patients v2" 
  ON public.patients_v2 FOR DELETE USING (auth.uid() = user_id);
CREATE POLICY "Admins can view all patients v2" 
  ON public.patients_v2 FOR SELECT USING (has_role(auth.uid(), 'admin'::app_role));
```

### 6.2 morphic_field_calculations

```sql
CREATE TABLE public.morphic_field_calculations (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID NOT NULL,
  patient_id UUID,
  client_name TEXT NOT NULL,
  field_intensity NUMERIC NOT NULL,
  coherence NUMERIC NOT NULL,
  resonance_frequency NUMERIC NOT NULL,
  numerical_sequence JSONB,
  quantum_states JSONB,
  tcm_analysis JSONB,
  bohm_integration JSONB,
  recommendations JSONB,
  intention_type TEXT,
  geometric_form TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- RLS Policies
ALTER TABLE public.morphic_field_calculations ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own morphic field calculations" 
  ON public.morphic_field_calculations FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert their own morphic field calculations" 
  ON public.morphic_field_calculations FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can delete their own morphic field calculations" 
  ON public.morphic_field_calculations FOR DELETE USING (auth.uid() = user_id);
CREATE POLICY "Admins can view all morphic field calculations" 
  ON public.morphic_field_calculations FOR SELECT USING (has_role(auth.uid(), 'admin'::app_role));
```

### 6.3 morphic_field_sessions

```sql
CREATE TABLE public.morphic_field_sessions (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID NOT NULL,
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
  batch_id UUID,
  geometric_form TEXT,
  intention_type TEXT,
  field_intensity NUMERIC,
  coherence NUMERIC,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- RLS Policies
ALTER TABLE public.morphic_field_sessions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own morphic field sessions" 
  ON public.morphic_field_sessions FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert their own morphic field sessions" 
  ON public.morphic_field_sessions FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update their own morphic field sessions" 
  ON public.morphic_field_sessions FOR UPDATE USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can delete their own morphic field sessions" 
  ON public.morphic_field_sessions FOR DELETE USING (auth.uid() = user_id);
CREATE POLICY "Admins can view all morphic field sessions" 
  ON public.morphic_field_sessions FOR SELECT USING (has_role(auth.uid(), 'admin'::app_role));
```

### 6.4 Storage Bucket

```sql
-- Private Bucket für Klienten-Signaturen
INSERT INTO storage.buckets (id, name, public) 
VALUES ('client-signatures', 'client-signatures', false);

-- RLS Policies
CREATE POLICY "Users can upload their own signatures"
  ON storage.objects FOR INSERT
  WITH CHECK (bucket_id = 'client-signatures' AND auth.uid()::text = (storage.foldername(name))[1]);

CREATE POLICY "Users can view their own signatures"
  ON storage.objects FOR SELECT
  USING (bucket_id = 'client-signatures' AND auth.uid()::text = (storage.foldername(name))[1]);

CREATE POLICY "Users can delete their own signatures"
  ON storage.objects FOR DELETE
  USING (bucket_id = 'client-signatures' AND auth.uid()::text = (storage.foldername(name))[1]);
```

---

## 7. Typdefinitionen

### 7.1 Vollständige TypeScript-Typen

```typescript
// ============= Geometrische Formen =============
export type GeometricForm = 
  | 'tetrahedron' | 'cube' | 'octahedron' | 'dodecahedron' | 'icosahedron'
  | 'merkaba' | 'torus' | 'flower_of_life' | 'sri_yantra';

// ============= Intentionen =============
export type IntentionType =
  | 'healing' | 'manifestation' | 'protection' | 'transformation'
  | 'connection' | 'clearing' | 'activation' | 'harmonization';

// ============= TCM =============
export type TCMElement = 'holz' | 'feuer' | 'erde' | 'metall' | 'wasser';

// ============= Planeten =============
export type Planet = 
  | 'sonne' | 'mond' | 'merkur' | 'venus' | 'mars' 
  | 'jupiter' | 'saturn' | 'uranus' | 'neptun' | 'pluto';

// ============= Alphabete =============
export type AlphabetType = 
  | 'latin' | 'altdeutsch-gotisch' | 'altdeutsch-mittelhochdeutsch' | 'runisch';

// ============= Potenzen =============
export type PotencyType = 'D' | 'C' | 'LM' | 'M' | 'F1' | 'F2' | 'F3';

// ============= Session Status =============
export type SessionStatus = 'pending' | 'running' | 'paused' | 'completed' | 'cancelled';
```

---

## 8. Schritt-für-Schritt Implementierungsanleitung

### Phase 1: Projekt-Setup (30 Min)

1. **Neues Projekt erstellen**
   - Lovable: "Erstelle neues Projekt"
   - Name: z.B. "morphic-field-standalone"

2. **Lovable Cloud aktivieren**
   - Backend-Funktionalität einrichten

3. **Abhängigkeiten installieren** (siehe Abschnitt 9)

### Phase 2: Utility-Dateien (2 Std)

**Reihenfolge ist wichtig wegen Abhängigkeiten!**

1. **alphabetSystems.ts** erstellen
   - Keine Abhängigkeiten
   - 72 Zeilen

2. **hardwareAlgorithms.ts** erstellen
   - Keine Abhängigkeiten
   - 412 Zeilen

3. **copenRateGenerator.ts** erstellen
   - Import: `alphabetSystems.ts`, `hardwareAlgorithms.ts`
   - 723+ Zeilen

4. **morphicFieldEngine.ts** erstellen
   - Import: `hardwareAlgorithms.ts`, `copenRateGenerator.ts`
   - 355 Zeilen

5. **clientFieldAlgorithms.ts** erstellen
   - Import: `copenRateGenerator.ts`, `morphicFieldEngine.ts`
   - 468 Zeilen

### Phase 3: Datenbank-Migration (30 Min)

Führe SQL-Migrationen aus für:
1. `patients_v2` Tabelle
2. `morphic_field_calculations` Tabelle
3. `morphic_field_sessions` Tabelle
4. `client-signatures` Storage Bucket

### Phase 4: Komponenten (2 Std)

1. **MorphicFieldCalculator.tsx** erstellen
   - 299 Zeilen
   - Import: `morphicFieldEngine.ts`

2. **ClientFieldCalculator.tsx** erstellen
   - 997 Zeilen
   - Import: `clientFieldAlgorithms.ts`, `WordEnergyTester`

### Phase 5: Page erstellen (30 Min)

1. **MorphicFieldPage.tsx** erstellen
   - 253 Zeilen
   - Import: beide Calculator-Komponenten

2. **Route hinzufügen** in `App.tsx`:
```typescript
<Route path="/morphic-field" element={<ProtectedRoute><MorphicFieldPage /></ProtectedRoute>} />
```

### Phase 6: Test & Validierung (1 Std)

1. Navigiere zu `/morphic-field`
2. Teste Standard-Berechnung
3. Teste Klienten-Feldalgorithmus
4. Teste Bild-Upload
5. Teste Patient-Verknüpfung

---

## 9. Abhängigkeiten

### package.json Auszug

```json
{
  "dependencies": {
    "@radix-ui/react-accordion": "^1.2.0",
    "@radix-ui/react-avatar": "^1.1.0",
    "@radix-ui/react-checkbox": "^1.1.1",
    "@radix-ui/react-dialog": "^1.1.2",
    "@radix-ui/react-dropdown-menu": "^2.1.1",
    "@radix-ui/react-label": "^2.1.0",
    "@radix-ui/react-popover": "^1.1.1",
    "@radix-ui/react-progress": "^1.1.0",
    "@radix-ui/react-select": "^2.1.1",
    "@radix-ui/react-separator": "^1.1.0",
    "@radix-ui/react-slider": "^1.2.0",
    "@radix-ui/react-slot": "^1.1.0",
    "@radix-ui/react-switch": "^1.1.0",
    "@radix-ui/react-tabs": "^1.1.0",
    "@radix-ui/react-toast": "^1.2.1",
    "@radix-ui/react-tooltip": "^1.1.4",
    "@supabase/supabase-js": "^2.75.1",
    "@tanstack/react-query": "^5.56.2",
    "class-variance-authority": "^0.7.1",
    "clsx": "^2.1.1",
    "date-fns": "^3.6.0",
    "lucide-react": "^0.462.0",
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "react-router-dom": "^6.26.2",
    "sonner": "^1.5.0",
    "tailwind-merge": "^2.5.2",
    "tailwindcss-animate": "^1.0.7"
  }
}
```

---

## 10. Test & Validierung

### Unit-Tests

```typescript
// morphicFieldEngine.test.ts
describe('MorphicFieldEngine', () => {
  test('calculateGeometricFactor returns correct phi for tetrahedron', () => {
    expect(calculateGeometricFactor('tetrahedron')).toBeCloseTo(1.618, 3);
  });
  
  test('generateDefaultQuantumStates creates correct number of states', () => {
    const states = generateDefaultQuantumStates(5);
    expect(states.length).toBe(5);
    expect(states[0].amplitude).toBeCloseTo(1/Math.sqrt(5), 4);
  });
  
  test('calculateMorphicField returns valid result', async () => {
    const result = await calculateMorphicField({
      quantumStates: generateDefaultQuantumStates(3),
      numericalSequence: [12345, 67890],
      geometricForm: 'flower_of_life',
      intention: 'healing',
      useHardwareModulation: false
    });
    
    expect(result.totalWaveFunction).toBeGreaterThan(0);
    expect(result.coherence).toBeGreaterThanOrEqual(0);
    expect(result.coherence).toBeLessThanOrEqual(1);
  });
});
```

### Integration-Tests

```typescript
// clientFieldCalculator.test.ts
describe('ClientFieldCalculator', () => {
  test('berechneKlientenFeld produces valid output', async () => {
    const klient: KlientenDaten = {
      nachname: 'Müller',
      vornamen: ['Hans', 'Peter'],
      geburtsdatum: new Date('1985-06-15'),
      geburtsort: 'München',
      tcmTyp: 'holz'
    };
    
    const result = await berechneKlientenFeld(klient);
    
    expect(result.persönlicheSignatur.nachnameRate).toBeGreaterThan(0);
    expect(result.tcmAnalyse.dominantesElement).toBe('holz');
    expect(result.klientenWellenfunktion).toBeGreaterThan(0);
  });
});
```

### Manuelle Validierung

| Test-Szenario | Erwartetes Ergebnis |
|---------------|---------------------|
| Wort "Heilung" eingeben | Rate wird berechnet, alle Faktoren angezeigt |
| Geometrie wechseln | Geometrischer Faktor ändert sich |
| Hardware-Modulation aktivieren | Hardware-Faktor wird angezeigt |
| Patient aus DB laden | Formular wird automatisch gefüllt |
| Bild hochladen | Vorschau erscheint, Akkuranz steigt |
| TCM-Typ wählen | Element-Balken zeigt dominantes Element |
| 5-Elemente-Profil anpassen | Slider-Werte beeinflussen Analyse |
| Feld berechnen | Vollständiges Ergebnis mit Empfehlungen |

---

## Changelog

| Version | Datum | Änderungen |
|---------|-------|------------|
| 2.0 | 2026-01-03 | Vollständige Überarbeitung mit allen Code-Details |
| 1.0 | 2026-01-02 | Initiale Dokumentation |

---

*Diese Dokumentation ermöglicht die 1:1 Rekonstruktion der gesamten Morphischen Feld-Engine.*
