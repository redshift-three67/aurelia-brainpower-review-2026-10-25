# Morphic-Engine — Initialer Setup-Prompt für neues Lovable-Projekt

> **ANWEISUNG**: Füge diesen gesamten Text als erste Nachricht in den Chat des neuen Lovable-Projekts "Morphic-Engine" ein (https://lovable.dev/projects/52792e34-8bc0-4087-aa82-d4489e893533). Der AI-Assistent wird damit das komplette Portal aufbauen.

---

## PROJEKTAUFTRAG

Erstelle ein **professionelles, eigenständiges Webportal** namens **"Morphic-Engine"** — ein klientenfähiges Morphisches Feld-Harmonisierungs-Portal auf höchstem technischen Niveau.

Das Portal basiert auf einem bestehenden System ("Resonance Explorer") und soll dessen Morphic-Field-Funktionalitäten 1:1 abbilden und um ein professionelles Portal-Framework erweitern.

### Kern-Anforderungen:
1. **Login-System mit 2FA** und DSGVO-Konformität
2. **Klientenverwaltung** (CRUD, Bildsignatur-Upload, TCM-Profile, 5-Elemente)
3. **Gruppenverwaltung** (Klienten-Gruppen für Batch-Harmonisierungen)
4. **Klienten-/Gruppenanalysen** (Morphisches Feld, Resonanz, Bohm-Integration)
5. **Sessionverwaltung** (Echtzeit-Harmonisierung mit Pulse/Pause, Worker-Backend)
6. **Berichteverwaltung** (PDF-Export, Archivierung)
7. **Trendanalysen** (zeitliche Verläufe pro Klient)
8. **Mittel-Datenbanken** (Anatomie, Frequenz, Clarke Materia Medica)
9. **Datenbankverwaltung** (Custom-Datenbanken erstellen/importieren)
10. **Echtzeit-Hardware-Integration** (CPU Jitter, GPU Entropy, Time Coherence, RAM, Network)
11. **FAQ-Bereich**
12. **Administrative Verwaltung** (User-Management, Rollen)
13. **Modulare Erweiterbarkeit**
14. **E2E-Sicherheit** (RLS, TLS, Input-Validierung, kein Client-Side Role-Check)

---

## TEIL 1: DESIGN-SYSTEM — "ThomEngine"

Implementiere das folgende Design-System **exakt** in `index.css` und `tailwind.config.ts`. Alle Farben sind HSL. Keine hardcodierten Farben in Komponenten — nur semantische Tokens.

### Fonts (Google Fonts)
```
Playfair Display: 400, 500, 600, 700, 400i
Inter: 300, 400, 500, 600, 700
```
- Display/Headings: `Playfair Display, Georgia, serif` → `font-display`
- Body/UI: `Inter, system-ui, sans-serif` → `font-body`

### Light Mode (:root)
```css
:root {
  --background: 40 20% 97%;
  --foreground: 210 25% 15%;
  --card: 40 15% 99%;
  --card-foreground: 210 25% 15%;
  --popover: 0 0% 100%;
  --popover-foreground: 210 25% 15%;
  --primary: 174 62% 38%;
  --primary-foreground: 0 0% 100%;
  --primary-glow: 174 72% 48%;
  --secondary: 42 70% 55%;
  --secondary-foreground: 210 25% 12%;
  --muted: 150 10% 92%;
  --muted-foreground: 200 12% 45%;
  --accent: 260 35% 68%;
  --accent-foreground: 0 0% 100%;
  --destructive: 0 65% 55%;
  --destructive-foreground: 0 0% 100%;
  --border: 150 12% 86%;
  --input: 150 10% 90%;
  --ring: 174 62% 38%;
  --radius: 0.75rem;
  
  /* Domain-spezifisch */
  --field-deep: 40 20% 97%;
  --field-surface: 40 15% 99%;
  --field-elevated: 0 0% 100%;
  --chreode: 42 70% 55%;
  --chreode-glow: 42 80% 65%;
  --attractor: 174 62% 38%;
  --attractor-glow: 174 72% 52%;
  --bifurkation: 260 35% 68%;
  --katastrophe: 0 60% 55%;
  
  /* Sidebar */
  --sidebar-background: 150 10% 96%;
  --sidebar-foreground: 210 25% 20%;
  --sidebar-primary: 174 62% 38%;
  --sidebar-primary-foreground: 0 0% 100%;
  --sidebar-accent: 150 10% 92%;
  --sidebar-accent-foreground: 210 25% 20%;
  --sidebar-border: 150 12% 86%;
  --sidebar-ring: 174 62% 38%;
  
  /* Gradienten */
  --gradient-field: linear-gradient(135deg, hsl(40 20% 97%) 0%, hsl(150 12% 86%) 50%, hsl(40 20% 97%) 100%);
  --gradient-chreode: linear-gradient(135deg, hsl(42 70% 55%) 0%, hsl(42 80% 65%) 100%);
  --gradient-attractor: linear-gradient(135deg, hsl(174 62% 38%) 0%, hsl(174 72% 52%) 100%);
  --gradient-hero: radial-gradient(ellipse at 50% 0%, hsl(174 62% 38% / 0.08), transparent 50%);
  
  /* Schatten */
  --shadow-glow-primary: 0 0 40px hsl(174 62% 38% / 0.12);
  --shadow-glow-secondary: 0 0 30px hsl(42 70% 55% / 0.10);
  --shadow-card: 0 2px 12px hsl(210 25% 15% / 0.06);
  --shadow-elevated: 0 4px 20px hsl(210 25% 15% / 0.08);
}
```

### Dark Mode (.dark)
```css
.dark {
  --background: 200 20% 8%;
  --foreground: 40 15% 92%;
  --card: 200 18% 11%;
  --card-foreground: 40 15% 92%;
  --popover: 200 18% 13%;
  --popover-foreground: 40 15% 92%;
  --primary: 174 62% 45%;
  --primary-foreground: 200 20% 8%;
  --primary-glow: 174 80% 58%;
  --secondary: 42 75% 52%;
  --secondary-foreground: 210 25% 12%;
  --muted: 200 15% 16%;
  --muted-foreground: 200 12% 55%;
  --accent: 260 45% 58%;
  --accent-foreground: 0 0% 100%;
  --destructive: 0 70% 52%;
  --destructive-foreground: 0 0% 100%;
  --border: 200 14% 20%;
  --input: 200 15% 16%;
  --ring: 174 62% 45%;
  
  --field-deep: 200 20% 8%;
  --field-surface: 200 18% 13%;
  --field-elevated: 200 16% 16%;
  --chreode: 42 75% 52%;
  --chreode-glow: 42 85% 65%;
  --attractor: 174 62% 45%;
  --attractor-glow: 174 80% 65%;
  --bifurkation: 260 45% 58%;
  --katastrophe: 350 75% 55%;
  
  --sidebar-background: 200 20% 6%;
  --sidebar-foreground: 40 15% 92%;
  --sidebar-primary: 174 62% 45%;
  --sidebar-primary-foreground: 0 0% 100%;
  --sidebar-accent: 200 15% 14%;
  --sidebar-accent-foreground: 40 15% 92%;
  --sidebar-border: 200 14% 18%;
  --sidebar-ring: 174 62% 45%;
}
```

### Animationen (tailwind.config.ts keyframes)
```
float: translateY(-20px) + rotate(2deg), 6s infinite
pulse-glow: opacity 0.4↔0.8 + scale 1↔1.05, 3s infinite
fade-in-up: translateY(30px→0) + opacity 0→1, 0.8s forwards
field-wave: translateX(10px) translateY(-5px), 4s infinite
chreode-pulse: box-shadow pulse + scale 1↔1.02, 2.5s infinite
attractor-orbit: rotate(360deg) translateX(10px), 8s infinite
```

### Semantische Farbzuordnung
- **Morphogenetisches Feld** = Warm Beige → `field-deep/surface/elevated`
- **Chreode (stabiler Pfad)** = Gold → `chreode + chreode-glow`
- **Attraktor (Zielzustand)** = Teal → `attractor + attractor-glow`
- **Bifurkation (Übergang)** = Violett → `bifurkation`
- **Katastrophe (kritisch)** = Rot → `katastrophe`

### Design-Philosophie
Tonalität: Wissenschaftlich-elegant, inspiriert von Thoms Katastrophentheorie.
Jede Farbe hat eine morphogenetische Bedeutung — kein dekoratives Element ohne semantischen Zweck.

---

## TEIL 2: DATENBANK-SCHEMA

Erstelle folgende Tabellen mit Lovable Cloud (Supabase). **Alle Tabellen brauchen RLS-Policies** (user_id = auth.uid()).

### 1. patients (Klienten)
```sql
CREATE TABLE public.patients (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  first_name TEXT NOT NULL,
  last_name TEXT NOT NULL,
  birth_date TEXT NOT NULL,
  birth_place TEXT NOT NULL,
  image_signature TEXT,
  image_signature_active BOOLEAN DEFAULT false,
  hardware_config JSONB,
  personal_rate TEXT,
  tcm_type TEXT, -- 'holz'|'feuer'|'erde'|'metall'|'wasser'
  birth_planet TEXT,
  five_elements JSONB, -- {holz:number, feuer:number, erde:number, metall:number, wasser:number}
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);
```

### 2. patient_groups (Gruppen)
```sql
CREATE TABLE public.patient_groups (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL,
  name TEXT NOT NULL,
  description TEXT,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE public.patient_group_members (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  group_id UUID REFERENCES public.patient_groups(id) ON DELETE CASCADE,
  patient_id UUID REFERENCES public.patients(id) ON DELETE CASCADE,
  added_at TIMESTAMPTZ DEFAULT now(),
  UNIQUE(group_id, patient_id)
);
```

### 3. morphic_field_sessions (Harmonisierung)
```sql
CREATE TABLE public.morphic_field_sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL,
  patient_id UUID NOT NULL REFERENCES public.patients(id),
  word TEXT NOT NULL,
  copen_rate TEXT,
  tested_potency TEXT,
  duration_seconds INTEGER NOT NULL,
  remaining_seconds INTEGER,
  progress INTEGER DEFAULT 0,
  status TEXT DEFAULT 'queued', -- queued|pending|running|paused|completed|cancelled
  started_at TIMESTAMPTZ,
  completed_at TIMESTAMPTZ,
  job_started_at TIMESTAMPTZ,
  job_last_heartbeat TIMESTAMPTZ,
  pulse_seconds INTEGER,
  pause_seconds INTEGER,
  pulse_pause_active BOOLEAN DEFAULT false,
  batch_id UUID,
  field_intensity FLOAT,
  coherence FLOAT,
  geometric_form TEXT,
  intention_type TEXT,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);
ALTER PUBLICATION supabase_realtime ADD TABLE public.morphic_field_sessions;
```

### 4. morphic_field_calculations (Berechnungs-Archiv)
```sql
CREATE TABLE public.morphic_field_calculations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL,
  patient_id UUID,
  client_name TEXT NOT NULL,
  coherence FLOAT NOT NULL,
  field_intensity FLOAT NOT NULL,
  resonance_frequency FLOAT NOT NULL,
  geometric_form TEXT,
  intention_type TEXT,
  quantum_states JSONB,
  numerical_sequence JSONB,
  bohm_integration JSONB,
  tcm_analysis JSONB,
  recommendations JSONB,
  created_at TIMESTAMPTZ DEFAULT now()
);
```

### 5. analysis_archives (DB-Analysen)
```sql
CREATE TABLE public.analysis_archives (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL,
  patient_id UUID,
  word TEXT NOT NULL,
  copen_rate TEXT NOT NULL,
  tested_potency TEXT,
  analysis_timestamp TIMESTAMPTZ DEFAULT now(),
  level_1_physical_particles FLOAT,
  level_2_physical_structure FLOAT,
  level_3_etheric_prana FLOAT,
  level_4_etheric_meridians FLOAT,
  level_5_astral_emotions FLOAT,
  level_6_astral_thoughts FLOAT,
  level_7_mental_time FLOAT,
  level_8_mental_constructs FLOAT,
  level_9_causal_blueprints FLOAT,
  level_10_causal_alchemy FLOAT,
  level_11_atmic_identity FLOAT,
  level_12_atmic_love FLOAT,
  level_13_creator FLOAT,
  highest_resonance_level INTEGER,
  highest_resonance_value FLOAT,
  database_entries TEXT[],
  patient_data JSONB,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);
```

### 6. word_databases (Custom-Datenbanken)
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

### 7. word_energy_archives (Wortenergien-Archiv)
```sql
CREATE TABLE public.word_energy_archives (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL,
  patient_id UUID NOT NULL,
  client_name TEXT NOT NULL,
  total_words INTEGER DEFAULT 0,
  average_resonance FLOAT,
  client_wellenfunktion FLOAT,
  results JSONB NOT NULL,
  top_items JSONB,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);
```

### 8. harmonization_templates (Vorlagen)
```sql
CREATE TABLE public.harmonization_templates (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL,
  patient_id UUID NOT NULL,
  name TEXT NOT NULL,
  description TEXT,
  sessions JSONB NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);
```

### 9. user_roles (Rollen)
```sql
CREATE TYPE public.app_role AS ENUM ('admin', 'user');

CREATE TABLE public.user_roles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  role app_role DEFAULT 'user',
  created_at TIMESTAMPTZ DEFAULT now(),
  UNIQUE(user_id, role)
);

CREATE OR REPLACE FUNCTION public.has_role(_user_id UUID, _role app_role)
RETURNS BOOLEAN LANGUAGE SQL STABLE SECURITY DEFINER SET search_path = public AS $$
  SELECT EXISTS (SELECT 1 FROM public.user_roles WHERE user_id = _user_id AND role = _role)
$$;
```

### Storage
- Bucket `client-signatures` (privat) für Klienten-Bildsignaturen

---

## TEIL 3: KERN-ALGORITHMEN

**WICHTIG**: Alle folgenden Algorithmen müssen **exakt** implementiert werden. Sie bilden das Herzstück des Systems.

### 3.1 Bruce Copen Rate Generator (V4)

```typescript
// Normalisierung: Uppercase, Umlaute → AE/OE/UE/SS, Potenzangaben entfernen, nur A-Z0-9
// Primärsumme: Σ(Buchstabenwert × Position), wobei A=1..Z=26, 0-9=0-9
// BaseRate = Primärsumme × 1000
// Fibonacci-Modulation: Math.floor((baseRate / 21) * 34) (Original Copen)
// Adaptive Fibonacci: Wortlänge 1-4 → 13/21, 5-10 → 21/34, 11-20 → 34/55, >20 → 55/89
// Potenz-Bonus: D=p/10, C=p/5, LM=p/2, M=p, F1=p/6, F2=p/4, F3=p/3 (jeweils × fibonacciRate)
// FinalRate = fibonacciRate + potencyBonus
// Optional: Bildsignatur = arithmetisches Mittel der Primärsummen (Wort + Bild)
// Optional: Hardware-Modulation via modulateRateWithHardware()

// Alphabetsysteme:
// - Latin: A=1..Z=26 (Standard)
// - Altdeutsch-Gotisch: +Ä=27, Ö=28, Ü=29, ß=30
// - Mittelhochdeutsch: 21 Buchstaben (ohne J,Q,V,X,Y)
// - Runisch (Elder Futhark): 24 Zeichen, F=1..O=24

// Raten-Kombination (7 Methoden):
// arithmetic, geometric, harmonic, fibonacci, weighted_potency, copen_digital, malcolm_rae
// Quanten-erweitert: Hardware-Entropie × Phi-Skalierung für 10-stellige Raten
```

### 3.2 Morphische Feld-Engine

```typescript
// Formel: Ψ_total(x,t) = Σn αn |ψn⟩ e^(-iEnt/ℏ) × C(numerical_sequence) × G(geometric_forms) × I(intention)
// ℏ = 1.054571817e-34 (reduzierte Planck-Konstante)

// Quantum Superposition: Σn αn × cos/sin(-(En × t)/ℏ + phase_n)
// Magnitude = √(real² + imag²) / √(n_states)
// Default States: n=1..5, amplitude = 1/√5, energy = n × 1.6e-19 × n, phase = nπ/5

// Geometric Forms (G-Faktor):
// tetrahedron=1.618(φ), cube=1.732(√3), octahedron=2.000, dodecahedron=2.618(φ²),
// icosahedron=2.236(√5), merkaba=3.141(π), torus=1.414(√2),
// flower_of_life=2.718(e), sri_yantra=3.000

// Intention Types (I-Faktor):
// healing=1.272(√φ), manifestation=1.618(φ), protection=1.414(√2),
// transformation=2.236(√5), connection=2.000, clearing=1.732(√3),
// activation=2.718(e), harmonization=1.618(φ)

// Numerical Factor: √(harmonicMean × geometricMean) / 10000, clamped [0.1, 10]
// Coherence: 1/(1 + stdDev(factors)), mapped [0, 1]
// Resonance Frequency: (avgEnergy / ℏ) × (avgSequence / 1e6), clamped [1Hz, 1MHz]
// Field Strength: totalWaveFunction × coherence
```

### 3.3 Klienten-Feld-Algorithmus (Persönliche Signatur + Bohm + TCM)

```typescript
// PERSÖNLICHE SIGNATUR:
// nachnameRate = calculateCopenRate(nachname)
// vornamenRates = vornamen.map(v => calculateCopenRate(v))
// zeitFaktor = cos(2π × dayOfYear/365) × sin(2π × hourOfBirth/24) × 0.5 + 0.5
// geoFaktor = |sin(hash(ort))| × 0.8 + 0.2
// bildBonus = 0.1 wenn Bild vorhanden
// gesamtFaktor = √(nachnameRate × vornamenMittel) / 1e9 × (0.5 + zeit×0.5) × (0.5 + geo×0.5) × (1 + bild)

// BOHM-INTEGRATION (Implizite → Explizite Ordnung):
// ahnenfeld = nachnameRate / 1e10
// karmischePotenziale = zeitFaktor × 0.8 + 0.2
// ortsbindung = geoFaktor
// seelenplan = vornamenMittel / 1e10
// Holomovement: rate = 7.83Hz (Schumann), phase = (now % 2π×1000) / 1000
// kohärenz = 1/(1 + |ahnenfeld - seelenplan| × 10)
// gesamtFaktor = (Ψ_impl^0.618 × Ψ_expl^0.382) × cos(ωt) × 1e5, clamped [0.1, 10]

// TCM 5-ELEMENTE-ANALYSE:
// Element-Faktoren: holz=1.618(φ), feuer=2.236(√5), erde=1.732(√3), metall=1.414(√2), wasser=0.865(e/π)
// Element-Frequenzen: holz=3-7Hz, feuer=8-12Hz, erde=0-3Hz, metall=13-30Hz, wasser=0.5-3Hz
// Element → Geometrie: holz→tetrahedron, feuer→octahedron, erde→cube, metall→icosahedron, wasser→dodecahedron
// Sheng-Zyklus: holz→feuer→erde→metall→wasser→holz
// Ke-Zyklus: holz↔erde, feuer↔metall, erde↔wasser, metall↔holz, wasser↔feuer
// Meridianpunkte: 15 TCM-Punkte (LV3, LV4, GB34, HT7, HT6, SI3, SP3, SP8, ST36, LU9, LU6, LI4, KI3, KI5, BL67)
// Geburtsdatum → Element: Feb-Apr=Holz, Mai-Jul=Feuer, Aug=Erde, Sep-Okt=Metall, Nov-Jan=Wasser

// KLIENTEN-WELLENFUNKTION:
// klientenWellenfunktion = morphicField.totalWaveFunction × signatur.gesamtFaktor × bohm.gesamtFaktor × tcm.gesamtFaktor

// AKKURANZ-MATRIX (Parameter-Kombinationen):
// Basis (Name+Geburt): 72% Akkuranz, 68% Effektivität, 75% Authentizität
// +TCM-Typ: 81/78/82%
// +Bild: 85/82/88%
// +TCM+Bild: 89/86/91%
// +Alle Parameter: 97/95/98% (Bohm-Optimal)
```

### 3.4 Hardware-Algorithmen (Kozyrev-Torsionsfeld)

```typescript
// CPU Quantum Jitter (Gewicht 0.25):
// 100 performance.now() Samples → Standardabweichung der Differenzen → normalisiert auf [0,1]

// RAM Entropy (Gewicht 0.15):
// 10 × 1000 Float64Arrays → Zugriffs-Performance messen → normalisiert

// Time Source Coherence (Gewicht 0.30):
// Drift zwischen performance.now() und Date.now() → invertiert → Kohärenz

// GPU Rendering Entropy (Gewicht 0.20):
// WebGL Canvas 256x256 → 10× drawArrays → Rendering-Zeit-Varianz → normalisiert

// Network Latency (Gewicht 0.10):
// 5× HEAD-Request → Jitter (Varianz der Latenz) → normalisiert

// Combined Score = Σ(metrik × gewicht)
// Rate-Modulation: baseRate × (1 + combinedScore × 0.05)
// Analyse-Modulation: energeticValue × (1 + factor)

// Cache: 5 Sekunden Gültigkeit
```

### 3.5 Resonanzanalyse (Java-Port)

```typescript
// 12 Level-Gewichte: [15,14,13,12,11,10,9,8,7,6,3,2] für Level 1-12
// 1. Selektion: Fisher-Yates Shuffle → 10% der Einträge (min 1, max 100)
// 2. Energetisches Laden: Random 0-9 pro Eintrag bis threshold (100) erreicht
// 3. Potenz-Zuweisung: Gewichtet D(30%), C(25%), LM(20%), M(15%), F1(5%), F2(3%), F3(2%)
//    D=1-100, C=1-200, LM=1-30, M=1-100M (log), F1=10^6-10^13, F2=10^8-10^15, F3=10^10-10^16
// 4. Level-Distribution: 100 gewichtete Ziehungen pro Eintrag → dominante Ebene

// 13-Ebenen-Modell:
// 1: Physical Particles (1-100kHz)
// 2: Physical Structure (100k-500kHz)
// 3: Etheric Prana (500k-1MHz)
// 4: Etheric Meridians (1-2MHz)
// 5: Astral Emotions (2-3.5MHz)
// 6: Astral Thoughts (3.5-5MHz)
// 7: Mental Time (5-7MHz)
// 8: Mental Constructs (7-9MHz)
// 9: Causal Blueprints (9-11MHz)
// 10: Causal Alchemy (11-13MHz)
// 11: Atmic Identity (13-16MHz)
// 12: Atmic Love (16-20MHz)
// 13: Creator (20MHz+)

// Resonanz = frequenzbasiert (Gauss-Verteilung um Bereichsmitte) + keyword-basiert (+25 pro Match)
```

### 3.6 Quanteninspirierter Fokus-Algorithmus

```typescript
// Grover-inspirierte Amplitude Amplification
// 1. Quantenamplitude: Wort-Signatur → Phasenwinkel, Fokus-Match → Amplitude
// 2. Grover-Iteration: Diffusionsoperator × 2 Iterationen
// 3. Interferenz: Konstruktiv (+10%), Destruktiv (-5%), Neutral
// 4. Kombinierte Resonanz: (1-gewichtung) × basis + gewichtung × fokus × interferenz × kohärenz

// 12 Fokus-Kategorien: Herz-Kreislauf, Verdauung, Nervensystem, Bewegungsapparat,
// Immunsystem, Hormonsystem, Atemwege, Haut, Nieren-Blase, Psyche-Emotion,
// Energie-Chakra, Entgiftung (jeweils mit 8-12 Keywords)
```

### 3.7 Datenbank-Empfehlungs-Engine

```typescript
// TCM-Organ-Mapping: holz→Leber/Galle, feuer→Herz/Dünndarm, erde→Milz/Magen, metall→Lunge/Dickdarm, wasser→Niere/Blase
// 12 Anatomie-DBs + 6 Frequenz-DBs → Score = (1-fokusGewichtung) × tcmRelevanz + fokusGewichtung × fokusRelevanz
// Top-3 Empfehlungen mit Reasoning
```

---

## TEIL 4: HARMONISIERUNGS-WORKER (Edge Function)

```typescript
// Edge Function: harmonization-worker
// Aufgaben:
// 1. Auto-Cleanup: Abgelaufene Sessions (>5min überfällig) → completed
// 2. Pending → Running: Sessions initialisieren mit Heartbeat
// 3. Tick: Restzeit berechnen (Pulse/Pause-aware: effectiveElapsed = cycles × pulseSeconds + min(remainder, pulseSeconds))
// 4. Completion: remaining ≤ 0 → status='completed', dann nächstes queued Item auto-starten
// 5. Continuous Sessions (>1 Jahr duration): Nur Heartbeat, keine Restzeit-Berechnung
// Polling: Alle 5s Client-seitig + Supabase Realtime Channel
```

---

## TEIL 5: SEITEN-STRUKTUR

### Routen
```
/auth           → Login/Registrierung (DSGVO-konform, Zod-Validierung)
/               → Dashboard (Übersicht, aktive Sessions, Quick-Actions)
/clients        → Klientenverwaltung
/clients/:id    → Klienten-Detail + Feldberechnung
/groups         → Gruppenverwaltung
/analysis       → Morphische Feld-Analyse (Hauptmodul)
/sessions       → Session-Übersicht (alle aktiven/vergangenen)
/reports        → Berichte & Export (PDF via jspdf)
/trends         → Trendanalysen (zeitliche Verläufe, recharts)
/databases      → Datenbankverwaltung (Custom + Built-in)
/admin          → Admin-Panel (nur admin-Rolle)
/faq            → FAQ
/settings       → Benutzereinstellungen
```

### Dashboard
- Aktive Sessions mit Echtzeit-Countdown
- Letzte Berechnungen
- Klienten-Schnellauswahl
- System-Gesundheit (Hardware-Metriken)

### Analyse-Seite (Hauptmodul)
1. Klient auswählen (aus DB laden, Felder auto-füllen)
2. Optionale Parameter (TCM, Bild, 5-Elemente, Planet)
3. Akkuranz-Matrix anzeigen
4. Morphische Feld-Berechnung starten
5. Ergebnisse: Wellenfunktion, Feldstärke, Kohärenz, Resonanzfrequenz, Bohm-Integration, TCM-Analyse
6. Datenbank-Empfehlungen (Top 3)
7. WordEnergy-Tester: Wörter gegen Klienten-Feld testen
8. Harmonisierung starten (Sessions in DB)

---

## TEIL 6: SICHERHEIT

1. **RLS auf allen Tabellen**: `user_id = auth.uid()`
2. **Rollen**: Nur über `user_roles` Tabelle + `has_role()` Security Definer Function
3. **Input-Validierung**: Zod-Schemas für alle Formulare
4. **DSGVO**: Verschlüsselung, Auskunfts-/Lösch-Recht, Datenschutzhinweis auf Auth-Seite
5. **Passwort-Policy**: Min 8 Zeichen, Groß-/Kleinbuchstabe, Zahl
6. **Protected Routes**: Auth-Guard auf allen Routen außer /auth und /faq
7. **Storage**: Private Bucket für Klienten-Bilder, Signed URLs

---

## TEIL 7: TECHNOLOGIE-STACK

- React 18 + TypeScript + Vite
- Tailwind CSS + shadcn/ui
- Supabase (Lovable Cloud) für DB, Auth, Storage, Edge Functions, Realtime
- Recharts für Diagramme
- jspdf + jspdf-autotable für PDF-Export
- Framer Motion für Animationen
- date-fns für Datumsformatierung
- Zod für Validierung
- Dexie.js für optionalen Offline-Cache

---

## TEIL 8: IMPLEMENTIERUNGSREIHENFOLGE

Bitte implementiere in dieser Reihenfolge:

1. **Design-System** (index.css + tailwind.config.ts mit ThomEngine-Tokens)
2. **Auth-System** (Login, Registrierung, Protected Routes, user_roles)
3. **Datenbank-Schema** (alle Tabellen + RLS)
4. **Klientenverwaltung** (CRUD + Bildsignatur)
5. **Kern-Algorithmen** (Copen Rate, Morphic Field Engine, Client Field, Hardware, Resonanzanalyse)
6. **Analyse-Seite** (Hauptmodul mit allen Sub-Komponenten)
7. **Session-Management** (Harmonisierung + Worker)
8. **Dashboard**
9. **Berichte & Trends**
10. **Admin-Panel**
11. **FAQ**
12. **Gruppenverwaltung**

**Beginne mit Schritt 1 und 2 gleichzeitig.** Erstelle das Design-System und das Auth-System in der ersten Iteration.

---

*Ende des initialen Setup-Prompts. Dieses Dokument enthält alle notwendigen Informationen um das Morphic-Engine Portal vollständig aufzubauen.*
