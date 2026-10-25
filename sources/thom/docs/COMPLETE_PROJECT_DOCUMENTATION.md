# Feldengine — Vollständige Projektdokumentation

**Version:** v17.0 (Stand: 2026-03-11)  
**Zielgruppe:** Entwickler zur vollständigen Reproduktion  
**Stack:** React 18 + Vite + TypeScript + Tailwind CSS + Supabase (Lovable Cloud)

---

## Inhaltsverzeichnis

1. [Projektübersicht](#1-projektübersicht)
2. [Architektur & Routing](#2-architektur--routing)
3. [Design-System](#3-design-system)
4. [Authentifizierung & Sicherheit](#4-authentifizierung--sicherheit)
5. [Datenbank-Schema (Supabase)](#5-datenbank-schema-supabase)
6. [Kern-Algorithmen: Feldengine](#6-kern-algorithmen-feldengine)
7. [Klienten-Management](#7-klienten-management)
8. [3D-Anatomie-Visualisierung](#8-3d-anatomie-visualisierung)
9. [NLS-Landmark-System](#9-nls-landmark-system)
10. [Meridian-Diagnose & TCM](#10-meridian-diagnose--tcm)
11. [Frequenz-Ausgabe & Audio-Engine](#11-frequenz-ausgabe--audio-engine)
12. [Hardware-Integration](#12-hardware-integration)
13. [Session-Management](#13-session-management)
14. [Gruppen-Analyse](#14-gruppen-analyse)
15. [Mittel-Datenbank](#15-mittel-datenbank)
16. [Wort-Energien](#16-wort-energien)
17. [Edge Functions](#17-edge-functions)
18. [Storage Buckets](#18-storage-buckets)
19. [Abhängigkeiten](#19-abhängigkeiten)
20. [Dateistruktur-Übersicht](#20-dateistruktur-übersicht)

---

## 1. Projektübersicht

Die **Feldengine** ist ein webbasiertes Diagnose- und Harmonisierungssystem, das auf **René Thoms Katastrophentheorie** und **morphogenetischen Feldern** basiert. Es kombiniert:

- **Biometrische Vektor-Analyse** (Numerologie, Geo-Resonanz, Temporal-Phase)
- **TCM-Meridian-Diagnose** mit 409 WHO-Akupunkturpunkten
- **3D-Anatomie-Visualisierung** mit GLB-Modellen und Surface-Projection
- **NLS-Organscan** mit 162 Messpunkten + 268 anatomischen Landmarks
- **Frequenz-Therapie** (Audio via WebAudio API + Hardware via WebSerial)
- **Echtzeit-Bifurkationserkennung** nach Scheffer et al. (2009)
- **Hardware-Integration** für Spooky2 Frequenzgeneratoren

### Kern-URLs
- **Landing Page:** `/` — Konzeptuelle Einführung, Cusp-Visualisierung
- **Analyse:** `/analyse` — Geschützter Hauptarbeitsbereich
- **Klient-Dashboard:** `/klient/:id` — Einzelklient-Ansicht
- **Login:** `/login` — Email/Passwort-Authentifizierung
- **Export:** `/export` — Datenexport
- **Z-Anatomy Workflow:** `/workflow` — Anatomie-Workflow
- **Pilot-Import:** `/import` — Landmark-Datenimport

---

## 2. Architektur & Routing

### App.tsx — Routing-Struktur
```tsx
// Geschützte Routen via ProtectedRoute-Wrapper
<Route path="/analyse" element={<ProtectedRoute><Analyse /></ProtectedRoute>} />
<Route path="/export" element={<ProtectedRoute><Export /></ProtectedRoute>} />
<Route path="/klient/:id" element={<ProtectedRoute><KlientDashboard /></ProtectedRoute>} />
```

### Seitenarchitektur
- **Index.tsx:** Hero, ConceptSection, CuspVisualization, CuspSurface3D, FrequencyTherapySection, SystemStatusDashboard, ThomResources
- **Analyse.tsx:** ClientVectorInterface → ClientVectorTrajectory3D → AnatomyResonanceViewer → MeridianDiagnosisPanel → FrequencyOutputModule → Spooky2Panel → RemedyDatabasePanel → TCMTrendAnalytics → SessionReportGenerator

### Datenfluß auf der Analyse-Seite
```
ClientVectorInterface
  ↓ onVectorCreated(VectorAnalysis)
  ↓ onClientSelected(clientId)
BifurcationWarningWidget ← currentVectorAnalysis
ClientVectorTrajectory3D ← currentVectorAnalysis
AnatomyResonanceViewer ← currentVectorAnalysis, scanConfig
  ↓ onFrequencySelect(frequency)
  ↓ onNLSDysregulationData(data)
MeridianDiagnosisPanel ← vectorAnalysis, clientId, nlsDysregulationData
  ↓ onTreatmentComplete(TreatmentResult)
FrequencyOutputModule (standalone)
Spooky2Panel ← selectedFrequency
RemedyDatabasePanel ← onSelectFrequency
```

---

## 3. Design-System

### Fonts
- **Display:** Playfair Display (serif)
- **Body:** Inter (sans-serif)

### Farbschema (HSL in CSS Custom Properties)

#### Light Theme (Healing)
| Token | HSL | Zweck |
|---|---|---|
| `--background` | `40 20% 97%` | Warmes Off-White |
| `--foreground` | `210 25% 15%` | Dunkles Blaugrau |
| `--primary` | `174 62% 38%` | Healing Teal |
| `--primary-glow` | `174 72% 48%` | Teal Glow |
| `--secondary` | `42 70% 55%` | Warmes Sage Gold |
| `--accent` | `260 35% 68%` | Soft Lavender |
| `--muted` | `150 10% 92%` | Soft Sage |
| `--destructive` | `0 65% 55%` | Rot |

#### Dark Theme
| Token | HSL |
|---|---|
| `--background` | `200 20% 8%` |
| `--primary` | `174 62% 45%` |
| `--secondary` | `42 75% 52%` |
| `--accent` | `260 45% 62%` |

#### Custom Feldengine-Tokens
| Token | Zweck |
|---|---|
| `--field-deep/surface/elevated` | Hintergrund-Hierarchie |
| `--chreode / --chreode-glow` | Chreode-Pfadvisualisierung |
| `--attractor / --attractor-glow` | Attraktor-Markierung |
| `--bifurkation` | Bifurkations-Warnung |
| `--katastrophe` | Katastrophen-Schwelle |

#### Tailwind Custom Extensions
- Colors: `field.deep/surface/elevated`, `chreode.DEFAULT/glow`, `attractor.DEFAULT/glow`, `bifurkation`, `katastrophe`
- Animations: `float`, `pulse-glow`, `fade-in-up`
- Background Images: `gradient-field`, `gradient-chreode`, `gradient-attractor`, `gradient-hero`, `gradient-card`
- Box Shadows: `glow-primary`, `glow-secondary`, `card`, `elevated`

---

## 4. Authentifizierung & Sicherheit

### Auth-Flow
- **useAuth Hook** (`src/hooks/useAuth.ts`): Zentraler Auth-State via `supabase.auth`
- **ProtectedRoute** (`src/components/ProtectedRoute.tsx`): Leitet nicht-authentifizierte User auf `/login`
- **Login Page** (`src/pages/Login.tsx`): Email/Passwort mit Registrierung, Zod-Validierung

### Row Level Security (RLS)
**Alle Tabellen** haben RLS aktiviert. Muster:
- **Klientenbezogene Daten** (clients, client_vectors, treatment_sessions, harmonization_protocols, harmonization_jobs, resonance_results): Zugriff nur über `clients.user_id = auth.uid()`
- **Gruppen** (client_groups, client_group_members): Zugriff über `user_id = auth.uid()` bzw. `group_id ∈ (SELECT id FROM client_groups WHERE user_id = auth.uid())`
- **Referenzdaten** (organ_schemas, organ_landmarks, organ_scan_points, anatomy_models, anatomy_resonance_points, word_energies, remedies): Öffentlich lesbar, Schreibzugriff nur für authentifizierte Benutzer

---

## 5. Datenbank-Schema (Supabase)

### Tabellen-Übersicht

#### `clients`
| Spalte | Typ | Beschreibung |
|---|---|---|
| id | uuid PK | Auto-generiert |
| first_name | text NOT NULL | Vorname |
| last_name | text NOT NULL | Nachname |
| birth_date | date NOT NULL | Geburtsdatum |
| birth_place | text NOT NULL | Geburtsort |
| photo_url | text | URL zum Foto (Supabase Storage) |
| field_signature | text | Deterministischer Hash (z.B. `FS-02AFF235`) |
| notes | text | Notizen |
| user_id | uuid | Therapeuten-ID (auth.uid()) |
| created_at / updated_at | timestamptz | Zeitstempel |

#### `client_vectors`
| Spalte | Typ | Beschreibung |
|---|---|---|
| id | uuid PK | |
| client_id | uuid FK→clients | |
| dimension_physical | float8 | [-1, 1] |
| dimension_emotional | float8 | [-1, 1] |
| dimension_mental | float8 | [-1, 1] |
| dimension_energy | float8 | [-1, 1] |
| dimension_stress | float8 | [-1, 1] |
| attractor_distance | float8 | Stabilität 0-1 |
| phase | text | 'approach' / 'transition' / 'stable' |
| primary_concern | text | Hauptbeschwerde |
| session_id | text NOT NULL | Session-Identifikator |
| input_method | text | 'manual' / 'sensor' / 'hybrid' |
| hrv_value / gsr_value | float8 | Biosensor-Werte |
| sensor_data | jsonb | Zusätzliche Sensordaten |

#### `treatment_sessions`
| Spalte | Typ | Beschreibung |
|---|---|---|
| id | uuid PK | |
| client_id | uuid FK→clients | |
| session_number | int (default 1) | Fortlaufende Nummer |
| session_date | timestamptz | |
| status | text ('active'/'completed'/'cancelled') | |
| vector_snapshot | jsonb | Vektor bei Sitzungsbeginn |
| diagnosis_snapshot | jsonb | Diagnose-Ergebnis |
| treatment_summary | jsonb | Behandlungszusammenfassung |
| duration_seconds | int | Sitzungsdauer |
| notes | text | |

#### `chreode_trajectories`
| Spalte | Typ | Beschreibung |
|---|---|---|
| id | uuid PK | |
| client_id | uuid FK→clients | |
| session_id | uuid FK→treatment_sessions | |
| dimensions | float8[] NOT NULL | 5D-Vektor |
| phase | text | |
| stability / bifurcation_risk / chreode_alignment / attractor_distance | numeric | Thom-Metriken |
| entropy_modulation | numeric[] | Hardware-Entropie-Werte |

#### `harmonization_protocols`
| Spalte | Typ | Beschreibung |
|---|---|---|
| id | uuid PK | |
| client_id | uuid FK→clients | |
| vector_id | uuid FK→client_vectors | |
| frequency | float8 NOT NULL | Zielfrequenz Hz |
| amplitude | float8 (0.5) | 0-1 |
| waveform | text ('sine') | sine/square/triangle/sawtooth |
| output_type | text ('audio') | audio/electromagnetic/dual |
| modulation_enabled | bool | |
| modulation_type / modulation_frequency / modulation_depth | | AM/FM/PWM |
| status | text ('pending') | pending/active/completed |
| effectiveness_rating | int | 1-5 |

#### `harmonization_jobs`
| Spalte | Typ | Beschreibung |
|---|---|---|
| id | uuid PK | |
| client_id | uuid FK→clients | |
| job_type | text ('harmonization') | |
| status | text ('pending') | pending/running/completed/failed |
| target_frequencies | float8[] | Zielfrequenzen |
| target_anatomy_points | text[] | Anatomie-Punkt-IDs |
| target_word_energies | text[] | Wort-Energie-IDs |
| progress | float8 (0) | 0-100 |
| result_data | jsonb | Ergebnisse mit Punkt-Details |

#### `organ_schemas`
| Spalte | Typ | Beschreibung |
|---|---|---|
| id | uuid PK | |
| organ_code | text NOT NULL | z.B. 'HEART', 'BRAIN' |
| organ_name | text NOT NULL | |
| source_dataset | text ('BodyParts3D') | |
| source_concept_id | text | FMA-ID (z.B. FMA_7088) |
| coordinate_system | text ('RAS') | Right-Anterior-Superior |
| regions | jsonb | Array von {region_code, name} |
| point_classes | text[] (['A','S','V']) | |
| sampling_config | jsonb | FPS-Parameter |
| validation_config | jsonb | Validierungsregeln |
| mesh_file | text | Pfad zum 3D-Mesh |
| version | text ('v1.0') | |

#### `organ_landmarks`
| Spalte | Typ | Beschreibung |
|---|---|---|
| id | uuid PK | |
| organ_schema_id | uuid FK→organ_schemas | |
| point_id | text NOT NULL | z.B. 'HEART_A_001' |
| label | text NOT NULL | z.B. 'Apex cordis' |
| point_class | text ('A') | A=Anatomisch, S=Scan, V=Validierung |
| region_code | text NOT NULL | |
| structure_concept_id | text | FMA-ID |
| x/y/z_position | float8 NOT NULL | RAS-Koordinaten (mm) |
| surface_normal_x/y/z | float8 | Oberflächennormale |
| scan_frequency | float8 | Hz |
| harmonic_frequencies | float8[] | Obertöne |
| placement_method | text ('manual') | manual/mirrored/generated_fps |
| confidence | float8 (1.0) | 0-1 |
| mirror_pair | text | ID des Spiegelpunkts |

#### `organ_scan_points`
162 NLS-Messpunkte über 15 Organsysteme.

| Spalte | Typ | Beschreibung |
|---|---|---|
| id | uuid PK | |
| organ_system | text | z.B. 'brain', 'heart', 'adrenal' |
| organ_name_de | text | Deutscher Name |
| organ_name_latin | text | Lateinischer Name |
| point_index | int | |
| point_name | text | z.B. 'Frontallappen' |
| scan_frequency | float8 | Hz |
| harmonic_frequencies | float8[] | |
| x/y/z_position | float8 | Normalisierte Koordinaten |
| tissue_type | text | cortex/nucleus/endocrine/... |
| body_region | text | head/thorax/abdomen/... |
| layer_depth | text ('surface') | surface/deep |
| dysregulation_threshold | float8 (1.5) | |

#### `anatomy_models`
13 3D-Modell-Einträge (Ganzkörper + Organ-Modelle).

| Spalte | Typ | Beschreibung |
|---|---|---|
| id | uuid PK | |
| name | text NOT NULL | |
| source | text ('custom') | custom/z-anatomy/bodyparts3d |
| category | text ('full_body') | full_body/organ |
| file_path | text NOT NULL | Lokaler oder Cloud-Pfad |
| storage_type | text ('local') | local/cloud |
| gender | text ('neutral') | male/female/neutral |
| supports_meridian_mapping | bool | |
| supports_organ_layers | bool | |
| visible_layers | text[] | Verfügbare Visualisierungs-Layer |
| applicable_organ_systems | text[] | Bei Organ-Modellen: relevante Systeme |
| is_default | bool | |
| sort_order | int | |

#### `anatomy_resonance_points`
10 Hauptorgan-Resonanzpunkte.

| Spalte | Typ |
|---|---|
| id | uuid PK |
| name / name_latin | text |
| body_region | text |
| x/y/z_position | float8 |
| primary_frequency | float8 |
| harmonic_frequencies | float8[] |
| organ_associations | text[] |
| meridian_associations | text[] |
| emotional_associations | text[] |

#### `remedies`
100 Mittel (38 Bachblüten, 12 Schüßler-Salze, 50 homöopathische Mittel).

| Spalte | Typ |
|---|---|
| id | uuid PK |
| name / name_latin | text |
| category | text | bach_flower/schuessler_salt/homeopathy |
| potency | text |
| frequency | numeric |
| element | text | TCM-Element |
| emotional_pattern | text |
| meridian_associations | text[] |
| organ_associations | text[] |
| contraindications | text |
| source | text |

#### `word_energies`
| Spalte | Typ |
|---|---|
| id | uuid PK |
| word | text |
| frequency | float8 |
| amplitude | float8 (0.5) |
| category | text | positive/negative |
| chakra | text |
| organ_system | text |
| meridian | text |
| emotional_quality | text |
| language | text ('de') |

#### `word_energy_collections`
| Spalte | Typ |
|---|---|
| id | uuid PK |
| user_id | uuid |
| name | text |
| words | text[] |
| description | text |

#### `client_groups` / `client_group_members`
Gruppen-Management für kollektive Analyse.

#### `resonance_results`
Scan-Ergebnisse pro Sitzung mit Dysregulations-Scores.

### Trigger
```sql
-- Automatisches updated_at
CREATE FUNCTION update_updated_at_column() RETURNS trigger
  LANGUAGE plpgsql SECURITY DEFINER SET search_path TO 'public'
AS $$ BEGIN NEW.updated_at = now(); RETURN NEW; END; $$;
```

---

## 6. Kern-Algorithmen: Feldengine

### 6.1 ThomVectorEngine (`src/services/feldengine/ThomVectorEngine.ts`)

**Eingabe:** BiometricClientData + StateDimensions + HardwareEntropy  
**Ausgabe:** VectorAnalysis (ClientVector + FieldSignature + AttractorState + RecommendedFrequencies)

#### Feld-Signatur-Berechnung
1. **Numerologie** (Pythagoras-System):
   - `LETTER_VALUES`: a=1..z=8, ä=5, ö=6, ü=3, ß=1
   - `nameValue`, `vowelValue`, `consonantValue` durch Quersummenreduktion (Ausnahme: Meisterzahlen 11, 22, 33)
   - `lifePathNumber` aus Geburtsdatum-Quersumme

2. **Geo-Resonanz**:
   - Ortsnamen-Hash via Bit-Shifting (`(hash << 5) - hash + charCode`)
   - Harmonische Frequenzen: `7.83 * (1 + hash_variant / 1000)` (Schumann-Basis)

3. **Temporal-Phase**:
   - `dayPhase = (day - 1) / 30`
   - `monthPhase = (month - 1) / 11`
   - `yearCycle = ((year - 1) % 9) / 8` (9-Jahres-Zyklus)
   - `seasonalResonance = sin(2π * monthPhase)`

4. **Vektor-Kombination** (5D):
   ```
   D1: norm(nameValue, 33)          // Name-Essenz
   D2: norm(lifePathNumber, 33)     // Lebensweg
   D3: norm(placeHash % 1000, 1000) // Ort-Resonanz
   D4: seasonalResonance            // Temporal-Phase
   D5: norm(harmonics[0], 30)       // Primär-Harmonik
   ```

5. **Signatur-Hash**: `FS-${hex(hash).padStart(8, '0')}`

#### Klienten-Vektor-Berechnung
```
stateVector[i] = (dimension[i] - 50) / 50    // Normalisierung auf [-1, 1]
combined[i] = 0.3 * fieldSignature[i] + 0.7 * stateVector[i]
combined = applyHardwareEntropyModulation(combined, entropy)  // ±10%
```

#### Attraktor-Zustand
```
distance = √(Σ d[i]²)
stability = max(0, 1 - distance/2)
bifurcationRisk = |stress| * (1 - max(0, energy))
phase: distance > 1.2 → 'approach', > 0.5 → 'transition', else → 'stable'
chreodeAlignment = stability * (0.5 + 0.5 * lifePathNumber/33)
```

#### Hardware-Entropie-Modulation
```
MAX_MODULATION = 0.10 (±10%)
phase = (dimIndex * φ) % 1  // φ = Goldener Schnitt 1.618...
modulation = sin(entropy * 2π + phase * π) * MAX_MODULATION
result = clamp(d + modulation * combinedEntropy, -1, 1)
```

### 6.2 BifurcationDetector (`src/services/feldengine/BifurcationDetector.ts`)

Implementiert drei Frühwarnsignale nach **Scheffer et al. (Nature, 2009)**:

#### 1. Varianz-Analyse
```
σ²(d) = (1/N) Σ(x_i,d - μ_d)²
```
Steigende Varianz → System nähert sich Bifurkation.

#### 2. Lag-1 Autokorrelation
```
AC(d) = Σ((x_t - μ)(x_{t+1} - μ)) / Σ(x_t - μ)²
```
Steigende AC → kritische Verlangsamung (System braucht länger zur Rückkehr zum Attraktor).

#### 3. Flickering-Detektion
Zählt Vorzeichenwechsel der Ableitung über alle Dimensionen. Normalisiert auf `(window-2) * numDims`.

#### Risiko-Berechnung
```
risk = 0.4 * normalizedVariance + 0.4 * normalizedAC + 0.2 * normalizedFlicker
```

#### Bifurkationstypen und Empfehlungen
| Bedingung | Typ | Aktion |
|---|---|---|
| Hohe Varianz + AC + Flickering | `cusp_bifurcation` | `pause_and_reassess` |
| Hohe Varianz + AC, kein Flickering | `fold_bifurcation` | `stabilize_with_10hz_alpha` |
| Flickering > 0.6 | `flickering` | `apply_schumann_grounding` |
| AC > 70% Schwelle | `critical_slowing_down` | `reduce_frequency_intensity` |

#### Konfiguration (Defaults)
```ts
windowSize: 32,
varianceThreshold: 0.5,
autocorrelationThreshold: 0.8,
flickeringThreshold: 3,
samplingIntervalMs: 250,
dimensionWeights: [0.2, 0.2, 0.15, 0.25, 0.2]  // Physical, Emotional, Mental, Energy, Stress
```

---

## 7. Klienten-Management

### useClientDatabase Hook (`src/hooks/useClientDatabase.ts`)
CRUD-Operationen:
- `createClient(biometricData, notes)` → Berechnet FieldSignature, speichert in `clients`
- `loadClients()` → Alle Klienten des authentifizierten Users
- `getClient(id)` → Einzelner Klient
- `updateClient(id, updates)` → Partial Update
- `deleteClient(id)` → Kaskadiert via FK
- `saveClientVector(clientId, dimensions, biometricData, options)` → Neuer Vektor + ThomVectorEngine-Berechnung
- `loadClientVectors(clientId)` → Vektor-Historie
- `uploadClientPhoto(clientId, file)` → Upload in `client-photos` Bucket

### ClientVectorInterface (`src/components/ClientVectorInterface.tsx`, ~945 Zeilen)
- Klienten-Ersterfassung: Vorname, Nachname, Geburtsdatum, Geburtsort, Foto
- 5D-Schieberegler: Physical, Emotional, Mental, Energy, Stress (0-100)
- Hardware-Entropie-Toggle (moduliert Vektor um ±10%)
- Klienten-Liste in der Seitenleiste
- Inline-Bearbeitung und Löschung
- Word Energy Manager Integration
- Gruppen-Management Integration

---

## 8. 3D-Anatomie-Visualisierung

### AnatomyResonanceViewer (`src/components/AnatomyResonanceViewer.tsx`, ~2313 Zeilen)
Verwendet `@react-three/fiber` + `@react-three/drei`.

#### Modell-Verwaltung
- **ModelSelector**: Auswahl zwischen lokalen und Cloud-gespeicherten GLB-Modellen
- **ModelUpload**: Upload neuer Modelle in den `3d-models` Bucket
- **GLBModelLoader**: Lädt GLB-Dateien mit automatischer Normalisierung

#### Visualisierungs-Layer (Toggle-basiert)
| Layer | Beschreibung |
|---|---|
| Meridiane | 409 WHO-Akupunkturpunkte, per Raycasting auf Mesh-Oberfläche projiziert |
| Chakren | 7 Hauptchakren mit Glow-Effekt |
| Resonanzpunkte | 10 Organ-Resonanzpunkte aus DB |
| NLS-Scan | 162 Organ-Scan-Punkte + 268 Landmarks |

#### Surface Projection (`src/utils/surfaceProjection.ts`)
- Multi-Directional Raycasting (8 Richtungen)
- Projiziert TCM-Punkte auf die nächste Mesh-Oberfläche
- Offset von 5mm für visuelle Klarheit

#### Organ-Modell-Logik
Bei Modellen der Kategorie `organ` (z.B. Herz, Gehirn) werden nur relevante Layer angezeigt (typischerweise nur NLS-Scan), um Redundanzen zu vermeiden.

---

## 9. NLS-Landmark-System

### Datenstruktur
8 Organsysteme mit insgesamt 268 Landmarks:

| Organ | Code | A-Punkte | S-Punkte | Gesamt |
|---|---|---|---|---|
| Herz | HEART | 9 | 36 | 45 |
| Gehirn | BRAIN | 8 | 44 | 52 |
| Leber | LIVER | 6 | 18 | 24 |
| Niere | KIDNEY_PAIR | 6 | 18 | 24 |
| Lunge | LUNG_PAIR | 6 | 22 | 28 |
| Wirbelsäule | SPINE_PELVIS | 8 | 23 | 31 |
| Ganzkörper | WHOLEBODY | 10 | 25 | 35 |
| TCM-Oberfläche | TCM_SURFACE | 4 | 25 | 29 |

### Punkt-Klassen
- **A (Anatomisch):** Manuell platzierte Referenzpunkte mit `confidence: 1.0`
- **S (Scan):** Automatisch generierte Scan-Punkte via Geodesic Farthest Point Sampling mit `confidence: 0.8`
- **V (Validierung):** Für Qualitätskontrolle (noch nicht verwendet)

### Pilotdaten
Lokale TypeScript-Dateien unter `src/data/anatomy-pilots/`:
- `heart.ts`, `brain.ts`, `liver.ts`, `kidney.ts`, `lung.ts`, `spine.ts`, `wholebody.ts`, `tcm.ts`
- Jede Datei exportiert ein `SCHEMA` und ein `LANDMARKS`-Array

### Hooks
- `useOrganLandmarks` (`src/hooks/useOrganLandmarks.ts`): Lädt aus DB, Fallback auf Pilotdaten
- `useOrganScanPoints` (`src/hooks/useOrganScanPoints.ts`): 162 NLS-Messpunkte

---

## 10. Meridian-Diagnose & TCM

### Akupunktur-Datenbank
409 Punkte total:
- 361 WHO-Standard (12 Hauptmeridiane + Du Mai + Ren Mai)
- 48 Extra-Punkte
- Modulare Dateien: `src/utils/meridianPoints/{spleen,heart,smallIntestine,bladder,kidney,pericardium,tripleWarmer,gallbladder,liver}.ts`
- Hauptdatenbank: `src/utils/meridianPointsDatabase.ts`

### Punkt-Struktur
```ts
{
  id: string,          // z.B. 'LU1'
  meridian: string,    // z.B. 'LU'
  nameChinese: string,
  nameEnglish: string,
  nameGerman: string,
  frequency: number,   // Paul-Schmidt + Baklayan
  element: string,     // TCM-Element
  indications: string[],
  type: string,        // 'he_sea', 'yuan_source', etc.
}
```

### Frequenz-Berechnung
Synthese aus:
- **Paul-Schmidt-Bioresonanz**: Element-Basisfrequenz + Geweberesistenz
- **Baklayan Harmonikale Theorie**: Ganzzahlige Obertöne
- **Zirkadiane Rhythmen**: Organ-Uhr-Zuordnung

### Meridian-Diagnose-Hook (`src/hooks/useMeridianDiagnosis.ts`, ~521 Zeilen)
- Analysiert den 5D-Vektor gegen die 6 TCM-Elemente
- Identifiziert Ungleichgewichte: `excess`, `deficiency`, `stagnation`
- Berechnet Imbalance-Scores pro Meridian
- Integriert die 8 Außergewöhnlichen Gefäße (Qi Jing Ba Mai)

### MeridianDiagnosisPanel (`src/components/MeridianDiagnosisPanel.tsx`, ~1373 Zeilen)
- Diagnose-Anzeige mit Element-Zuordnung
- Behandlungssequenz mit individueller Zeiteinstellung (Sekunden/Minuten)
- Bis zu 9 Punkte pro dysreguliertem Meridian
- Automatische Nachtestung nach Pause
- Trend- und Archivierungsfunktion
- NLS-Dysregulations-Integration

---

## 11. Frequenz-Ausgabe & Audio-Engine

### FrequencyOutputModule (`src/components/FrequencyOutputModule.tsx`, ~866 Zeilen)

#### Therapie-Modi
1. **Bipolar-Resonanz**: Gegenphasige Wellenformen
2. **Harmonikale Modulation**: Mehrstufige Obertöne mit AM/FM/PWM

#### Wellenformen
`sine`, `square`, `triangle`, `sawtooth`, `bipolar_sine`, `harmonic_complex`

#### Audio-Engine (WebAudio API)
- `AudioContext` + `OscillatorNode` + `GainNode`
- AudioWorklet für komplexe Wellenformen
- Echtzeit-Spektrum-Visualisierung (`SpectrumVisualizer`)
- Integrierte WHO-409-Punkt-Suche

#### Modulationsoptionen
| Parameter | Beschreibung |
|---|---|
| Modulation Type | AM / FM / PWM |
| Modulation Frequency | 0.1 - 100 Hz |
| Modulation Depth | 0 - 100% |

---

## 12. Hardware-Integration

### 12.1 HardwareDiscoveryService (`src/services/hardware/HardwareDiscoveryService.ts`, ~493 Zeilen)
- **WebUSB**: USB-DAC-Erkennung für Audio-Output
- **WebSerial**: Frequenzgenerator-Erkennung (Spooky2)
- Automatisches Scanning und Event-System

### 12.2 Spooky2Service (`src/services/hardware/Spooky2Service.ts`, ~365 Zeilen)
- Unterstützte Modelle: **Spooky2 XM** (5 MHz max) und **Generator X Pro** (40 MHz max, 2 Kanäle)
- USB-Serial-Chips: CH340 (0x1A86:0x7523), FT232R (0x0403:0x6001), FT231X (0x0403:0x6015), CP2102 (0x10C4:0xEA60)
- Baud: 115200, 8N1
- Befehle: `set_frequency`, `set_amplitude`, `set_waveform`, `start`, `stop`, `status`

### 12.3 SystemMonitorService (`src/services/hardware/SystemMonitorService.ts`)
- Server-seitige Metriken: CPU, GPU, RAM, Latenz
- Echtzeit-Entropie-Berechnung für Vektor-Modulation

### 12.4 HardwareMethodSelector (`src/components/HardwareMethodSelector.tsx`)
Zentrale Steuerung aller Ausgabemethoden:
- Audio (WebAudio)
- EM-Feld (WebSerial)
- Server-GPU
- Bipolar-Resonanz
- Harmonikale Modulation

---

## 13. Session-Management

### useSessionManagement (`src/hooks/useSessionManagement.ts`, ~177 Zeilen)
- `startSession(clientId, vectorAnalysis)` → Erstellt neue Sitzung mit Vektor-Snapshot
- `completeSession(sessionId, notes, diagnosisSnapshot, duration)` → Archiviert Sitzung
- `loadSessions(clientId)` → Sitzungshistorie
- Auto-Start bei Vektorerstellung
- Timer-Integration auf der Analyse-Seite

### useChreodeTracking (`src/hooks/useChreodeTracking.ts`)
- Zeichnet Trajektorienpunkte in `chreode_trajectories` auf
- Verknüpft Client-ID, Session-ID und VectorAnalysis

---

## 14. Gruppen-Analyse

### useClientGroups (`src/hooks/useClientGroups.ts`, ~297 Zeilen)
- CRUD für Gruppen und Mitgliedschaften
- `getGroupVectorSummary(groupId)`: Aggregiert Gruppenvektoren
  - Lädt neuesten Vektor pro Gruppenmitglied
  - Berechnet Durchschnitt der 5 Dimensionen
  - Liefert Phasenverteilung

### GroupManagementPanel (`src/components/GroupManagementPanel.tsx`)
- Gruppenanlage mit Farbwahl
- Klienten-Zuordnung
- Radar-Chart mit Gruppendurchschnitt

---

## 15. Mittel-Datenbank

### useRemedyDatabase (`src/hooks/useRemedyDatabase.ts`)
100 vorinstallierte Mittel:

| Kategorie | Anzahl | Beispiele |
|---|---|---|
| bach_flower | 38 | Agrimony, Aspen, Beech, Centaury... |
| schuessler_salt | 12 | Nr. 1 Calcium fluoratum bis Nr. 12 |
| homeopathy | 50 | Aconitum, Arnica, Belladonna... |

Jedes Mittel hat:
- Frequenz (Hz)
- TCM-Element-Zuordnung
- Meridian-Assoziationen (z.B. `['LU', 'LI']`)
- Emotionales Muster
- Organassoziationen

---

## 16. Wort-Energien

### Vorinstallierte Wort-Energien (10 Stück)
| Wort | Frequenz | Kategorie | Chakra | Organ |
|---|---|---|---|---|
| Angst | 20 Hz | negative | root | adrenal |
| Stress | 25 Hz | negative | solar_plexus | nervous_system |
| Trauer | 15 Hz | negative | heart | lungs |
| Wut | 35 Hz | negative | solar_plexus | liver |
| Freude | 396 Hz | positive | sacral | sacral |
| Frieden | 639 Hz | positive | heart | thymus |
| Gesundheit | 852 Hz | positive | third_eye | pineal |
| Harmonie | 741 Hz | positive | throat | thyroid |
| Kraft | 174 Hz | positive | root | adrenal |
| Liebe | 528 Hz | positive | heart | heart |

### WordEnergyDBManager (`src/components/WordEnergyDBManager.tsx`)
- Verwaltet Wort-Energie-Sammlungen pro Therapeut
- Integration in Harmonisierungs-Jobs

---

## 17. Edge Functions

### `/realtime-sync` (verify_jwt: false)
Server-seitige Metriken-Synchronisation.

### `/hardware-metrics` (verify_jwt: false)
Hardware-Performance-Daten.

### `/meridian-diagnosis` (verify_jwt: false)
Server-seitige Diagnose-Berechnung.

---

## 18. Storage Buckets

| Bucket | Public | Zweck |
|---|---|---|
| `client-photos` | Ja | Klienten-Fotos für biometrische Analyse |
| `3d-models` | Ja | GLB-Anatomie-Modelle |

---

## 19. Abhängigkeiten

### Kern
- `react` ^18.3.1, `react-dom` ^18.3.1
- `vite` (Build Tool)
- `typescript`
- `tailwindcss` + `tailwindcss-animate`

### 3D
- `three` ^0.170.0
- `@react-three/fiber` ^8.18.0
- `@react-three/drei` ^9.122.0

### State & Data
- `@tanstack/react-query` ^5.83.0
- `@supabase/supabase-js` ^2.89.0
- `react-router-dom` ^6.30.1

### UI
- `@radix-ui/*` (Accordion, Dialog, Select, Tabs, Toast, etc.)
- `lucide-react` ^0.462.0
- `recharts` ^2.15.4
- `framer-motion` ^12.23.26
- `sonner` ^1.7.4
- `class-variance-authority`, `clsx`, `tailwind-merge`
- `cmdk` ^1.1.1

### Utility
- `zod` ^3.25.76
- `react-hook-form` ^7.61.1 + `@hookform/resolvers`
- `date-fns` ^3.6.0
- `react-helmet-async` ^2.0.5
- `tus-js-client` ^4.3.1

---

## 20. Dateistruktur-Übersicht

```
src/
├── App.tsx                           # Routing
├── main.tsx                          # Entry Point
├── index.css                         # Design Tokens (365 Zeilen)
├── components/
│   ├── AcupuncturePointSearch.tsx     # WHO-409 Suche
│   ├── AnatomyResonanceViewer.tsx     # 3D-Viewer (2313 Zeilen)
│   ├── BifurcationWarningWidget.tsx   # Echtzeit-Warnung
│   ├── ChreodeCard.tsx               # Chreode-Visualisierung
│   ├── ClientVectorInterface.tsx      # Haupteingabe (945 Zeilen)
│   ├── ClientVectorTrajectory3D.tsx   # 3D-Trajektorie
│   ├── CuspSurface3D.tsx             # Cusp-Oberfläche
│   ├── CuspVisualization.tsx         # 2D-Cusp
│   ├── FrequencyOutputModule.tsx     # Audio-Engine (866 Zeilen)
│   ├── GroupManagementPanel.tsx       # Gruppenanalyse
│   ├── HardwareMethodSelector.tsx    # Methoden-Auswahl
│   ├── MeridianDiagnosisPanel.tsx    # TCM-Diagnose (1373 Zeilen)
│   ├── NLSAutoScanOverlay.tsx        # Scan-Fortschritt
│   ├── NLSScanConfigPanel.tsx        # Scan-Konfiguration
│   ├── RemedyDatabasePanel.tsx       # Mittel-DB
│   ├── SessionManagementPanel.tsx    # Sitzungsverwaltung
│   ├── SessionReportGenerator.tsx    # Berichterstellung
│   ├── Spooky2Panel.tsx              # Hardware-Steuerung
│   ├── SpectrumVisualizer.tsx        # Audio-Spektrum
│   ├── SystemStatusDashboard.tsx     # System-Status
│   ├── TCMTrendAnalytics.tsx         # Trend-Charts
│   ├── WordEnergyDBManager.tsx       # Wort-Energien
│   ├── anatomy/                      # Anatomie-Subkomponenten
│   │   ├── ChakraVisualization.tsx
│   │   ├── DetailedHumanModel.tsx
│   │   ├── DysregulationLegend.tsx
│   │   ├── GLBModelLoader.tsx
│   │   ├── InteractiveMeridianPoints.tsx
│   │   ├── ModelSelector.tsx
│   │   ├── ModelUpload.tsx
│   │   ├── OrganLandmarkLayer.tsx
│   │   └── OrganScanLayer.tsx
│   └── ui/                           # shadcn/ui Komponenten
├── data/anatomy-pilots/              # 8 Organ-Pilotdaten
├── hooks/
│   ├── useAuth.ts                    # Authentifizierung
│   ├── useClientDatabase.ts          # Klienten-CRUD
│   ├── useClientGroups.ts            # Gruppen-CRUD
│   ├── useChreodeTracking.ts         # Trajektorien
│   ├── useHardwareDiscovery.ts       # WebUSB/Serial
│   ├── useMeridianDiagnosis.ts       # TCM-Analyse
│   ├── useNLSAutoScan.ts             # Auto-Scan
│   ├── useOrganLandmarks.ts          # 268 Landmarks
│   ├── useOrganScanPoints.ts         # 162 Scan-Punkte
│   ├── useRealtimeHarmonization.ts   # Echtzeit-Sync
│   ├── useRemedyDatabase.ts          # 100 Mittel
│   ├── useResonanceDatabase.ts       # Resonanzpunkte
│   ├── useSessionManagement.ts       # Sitzungen
│   ├── useSpooky2.ts                 # Spooky2-Hook
│   ├── useSystemMonitor.ts           # System-Metriken
│   └── useTreatmentSequence.ts       # Behandlungssequenz
├── pages/
│   ├── Index.tsx                     # Landing Page
│   ├── Analyse.tsx                   # Hauptarbeitsbereich
│   ├── KlientDashboard.tsx           # Einzelklient
│   ├── Login.tsx                     # Auth
│   ├── Export.tsx                    # Datenexport
│   ├── ZAnatomyWorkflow.tsx          # Workflow
│   └── PilotDataImport.tsx           # Import
├── services/
│   ├── feldengine/
│   │   ├── ThomVectorEngine.ts       # Kern-Algorithmus
│   │   ├── BifurcationDetector.ts    # Frühwarnung
│   │   └── index.ts
│   ├── hardware/
│   │   ├── HardwareDiscoveryService.ts
│   │   ├── Spooky2Service.ts
│   │   ├── SystemMonitorService.ts
│   │   └── deviceProfiles.ts
│   ├── harmonization/
│   │   └── HarmonizationJobService.ts
│   └── realtime/
│       ├── RealtimeHarmonizationService.ts
│       └── RealtimeSyncService.ts
├── types/
│   ├── hardware.ts                   # ~208 Zeilen Typ-Definitionen
│   └── webapis.d.ts                  # WebUSB/WebSerial Typen
├── utils/
│   ├── meridianPointsDatabase.ts     # Haupt-Akupunktur-DB
│   ├── meridianPoints/               # 9 Meridian-Module
│   └── surfaceProjection.ts          # 3D Raycasting
└── integrations/supabase/
    ├── client.ts                     # Auto-generiert
    └── types.ts                      # Auto-generiert
```

---

*Erstellt am 2026-03-11 | Feldengine v17.0 | 17 Entwicklungsphasen abgeschlossen*
