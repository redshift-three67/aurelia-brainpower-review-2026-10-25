# Wiederherstellungspunkt – 2026-03-08 v2

**Erstellt:** 2026-03-08T09:25:00Z  
**Anlass:** Nach Abschluss Phase 11–16 (Bugs, Healing-Theme, Spooky2, Klienten-Dashboard, AudioWorklet)  
**Status:** Alle 16 Kernphasen abgeschlossen, System stabil, AudioWorklet + Spektrum-Visualisierung verifiziert

---

## Datenbankschema (IST-Zustand)

### Tabellen
| Tabelle | Spalten (Schlüssel) | RLS | Status |
|---------|-------------------|-----|--------|
| `clients` | id, first_name, last_name, birth_date, birth_place, photo_url, field_signature, notes, user_id | ✅ user_id = auth.uid() | OK |
| `client_vectors` | id, client_id, dimension_*, phase, session_id, input_method, sensor_data | ✅ via client_id→clients.user_id | OK |
| `treatment_sessions` | id, client_id, session_number, session_date, status, notes, vector_snapshot, diagnosis_snapshot, treatment_summary, duration_seconds | ✅ via client_id | OK |
| `harmonization_protocols` | id, client_id, vector_id, frequency, amplitude, waveform, output_type, modulation_*, status | ✅ via client_id | OK |
| `harmonization_jobs` | id, client_id, vector_id, protocol_id, status, progress, job_type, target_frequencies | ✅ via client_id | OK |
| `chreode_trajectories` | id, client_id, session_id, dimensions, stability, bifurcation_risk, chreode_alignment, phase | ✅ INSERT/SELECT authenticated | OK |
| `resonance_results` | id, session_id, client_id, scan_point_id, scan_frequency, intensity, dysregulation_score, organ_name | ✅ via client_id | OK |
| `word_energies` | id, word, frequency, category, meridian, chakra, organ_system | SELECT only (Referenz) | OK |
| `word_energy_collections` | id, user_id, name, words, description | ✅ user_id = auth.uid() | OK |
| `anatomy_resonance_points` | id, name, body_region, x/y/z_position, primary_frequency | SELECT only (Referenz) | OK |
| `organ_scan_points` | id, point_index, scan_frequency, organ_system, organ_name_de, body_region, layer_depth | SELECT only (Referenz) | OK |
| `anatomy_models` | id, name, category, file_path, storage_type, supports_* flags | ✅ Full CRUD authenticated | OK |
| `remedies` | id, name, name_latin, category, frequency, meridian_associations, organ_associations | ✅ SELECT + INSERT | **100 Datensätze** |

### Storage Buckets
- `client-photos` (public: yes)
- `3d-models` (public: yes)

### Edge Functions
- `realtime-sync` (verify_jwt: false)
- `hardware-metrics` (verify_jwt: false)
- `meridian-diagnosis` (verify_jwt: false)

### Secrets
- LOVABLE_API_KEY, SUPABASE_URL, SUPABASE_ANON_KEY, SUPABASE_SERVICE_ROLE_KEY, SUPABASE_DB_URL, SUPABASE_PUBLISHABLE_KEY

---

## Anwendungsarchitektur (IST-Zustand)

### Seiten
| Datei | Beschreibung | Zeilen |
|-------|-------------|--------|
| `src/pages/Index.tsx` | Landing Page mit Hero, Konzepten, 3D-Cusp, CTA | 72 |
| `src/pages/Analyse.tsx` | Hauptarbeitsseite: Vektor, Meridian-Diagnose, Frequenz-Output, NLS, Sessions | 257 |
| `src/pages/KlientDashboard.tsx` | Klienten-Dashboard mit Timeline, Trends, Remedies, Berichte | 372 |
| `src/pages/Login.tsx` | Login-only (kein Signup), Zod-Validierung | 178 |
| `src/pages/Export.tsx` | WHO-Datenbank Download (JSON/CSV) | – |
| `src/pages/NotFound.tsx` | 404-Seite | – |

### Routing (App.tsx)
- `/` → Index (public)
- `/analyse` → ProtectedRoute → Analyse
- `/export` → ProtectedRoute → Export
- `/klient/:id` → ProtectedRoute → KlientDashboard
- `/exports` → Redirect → `/export`
- `/login` → Login
- `*` → NotFound

### Hooks (Geschäftslogik)
| Datei | Beschreibung |
|-------|-------------|
| `useClientDatabase.ts` | CRUD clients + vectors, Photo-Upload |
| `useMeridianDiagnosis.ts` | Meridian-Diagnose via Edge Function |
| `useTreatmentSequence.ts` | Behandlungssequenz mit AM-Modulation, 1-42x Zyklen |
| `useTreatmentArchive.ts` | Behandlungs-Archiv |
| `useSessionManagement.ts` | Session-CRUD, Start/Complete |
| `useChreodeTracking.ts` | Chreode-Trajektorien aufzeichnen |
| `useResonanceDatabase.ts` | Anatomie-Resonanzpunkte Abfrage |
| `useResonanceResults.ts` | NLS-Scan-Ergebnisse speichern |
| `useOrganScanPoints.ts` | Organ-Scan-Punkte laden |
| `useNLSAutoScan.ts` | Automatischer NLS-Scan |
| `useAnatomyModels.ts` | 3D-Modell-Verwaltung mit Verfügbarkeits-Check |
| `useRemedyDatabase.ts` | Remedy-Datenbank Abfrage |
| `useRealtimeHarmonization.ts` | Realtime Harmonisierungs-Session |
| `useRealtimeSync.ts` | Realtime-Synchronisation |
| `useHardwareDiscovery.ts` | Hardware-Erkennung (WebUSB/WebSerial) |
| `useSpooky2.ts` | Spooky2 WebSerial Integration |
| `useSystemMonitor.ts` | System-Monitoring |
| `useServerHardwareMetrics.ts` | Server-Hardware-Metriken |
| `useAuth.ts` | Authentifizierung |

### Kern-Komponenten
| Datei | Zeilen | Beschreibung |
|-------|--------|-------------|
| `ClientVectorInterface.tsx` | – | Klienten-Eingabe + Vektor-Berechnung |
| `ClientVectorTrajectory3D.tsx` | – | 3D-Vektor-Visualisierung |
| `AnatomyResonanceViewer.tsx` | ~2123 | 3D-Anatomie mit Meridianen, Chakren, NLS-Scan, Organ-Layer |
| `MeridianDiagnosisPanel.tsx` | ~1355 | Meridian-Diagnose, Behandlungssequenz, Nachtestung, Archiv |
| `FrequencyOutputModule.tsx` | 866 | Audio/EM-Frequenzausgabe, AudioWorklet, FFT-Spektrum |
| `SpectrumVisualizer.tsx` | 177 | Echtzeit-FFT Canvas mit Spektrum + Wellenform |
| `WordEnergyDBManager.tsx` | 417 | Wort-Energie-Sammlungen (ohne Vektor-Pflicht) |
| `SessionManagementPanel.tsx` | 138 | Aktive Sitzung, Session-Historie |
| `SessionReportGenerator.tsx` | 269 | PDF/HTML-Bericht-Export |
| `TCMTrendAnalytics.tsx` | 270 | Wu-Xing Element-Trend-Visualisierung |
| `RemedyDatabasePanel.tsx` | – | Remedy-Datenbank UI mit Filter |
| `BifurcationWarningWidget.tsx` | – | Bifurkations-Warnung in Echtzeit |
| `RealtimeStatusWidget.tsx` | – | Realtime-Verbindungsstatus |
| `NLSScanConfigPanel.tsx` | – | NLS-Scan Konfiguration (oben rechts im Anatomie-Header) |
| `NLSAutoScanOverlay.tsx` | – | Auto-Scan Fortschritts-Overlay |
| `Spooky2Panel.tsx` | – | Spooky2 Hardware-Integration |
| `HardwareMethodSelector.tsx` | – | Hardware-Methoden Auswahl |
| `SystemStatusDashboard.tsx` | – | System-Status Dashboard |
| `ThemeToggle.tsx` | – | Light/Dark Mode Toggle (Healing-Theme) |

### Services
| Datei | Beschreibung |
|-------|-------------|
| `feldengine/ThomVectorEngine.ts` | Kern-Mathematik: Thom-Vektor, Feldsignatur, Attraktoren |
| `feldengine/BifurcationDetector.ts` | Echtzeit-Bifurkationserkennung |
| `hardware/HardwareDiscoveryService.ts` | Hardware Discovery (WebUSB/WebSerial) |
| `hardware/Spooky2Service.ts` | Spooky2 XM/Generator X Pro WebSerial-Protokoll |
| `hardware/SystemMonitorService.ts` | System-Monitoring |
| `hardware/deviceProfiles.ts` | Geräteprofile |
| `harmonization/HarmonizationJobService.ts` | Job-Queue für Harmonisierungs-Aufträge |
| `realtime/RealtimeHarmonizationService.ts` | AudioWorklet-Engine, GPU-Berechnung, WebSocket |
| `realtime/RealtimeSyncService.ts` | Realtime-Synchronisation via WebSocket |

### Design-System
| Datei | Beschreibung |
|-------|-------------|
| `src/index.css` | HSL-Tokens, Light + Dark Theme, Healing-Farbpalette |
| `tailwind.config.ts` | Semantic Colors, Custom Fonts, Gradients, Shadows |

---

## Abgeschlossene Phasen (1–16)

### Phase 1–10: Kernfunktionalität
- Thom-Vektor-Engine, Feldsignaturen, Attraktoren
- 5-dimensionaler Klienten-Vektor
- TCM-Meridian-Diagnose (12 Meridiane)
- NLS-Organscan (162 Messpunkte)
- 3D-Anatomie-Viewer mit GLB-Modellen
- Behandlungssequenz (1-42 Zyklen, AM-Modulation)
- Chreode-Tracking, Bifurkationserkennung
- Word-Energy-Datenbank
- Remedy-Datenbank (100 Einträge)
- Session-Management mit Report-Generator

### Phase 11: Bugfixes
- ✅ WordEnergy CRUD ohne Vektor-Pflicht
- ✅ Frequenz-Anzeige "—" Bug behoben
- ✅ diagnosis_snapshot zuverlässig gespeichert
- ✅ NLS-Scan-Config oben rechts positioniert

### Phase 12: Healing-Theme
- ✅ Helles Theme: Off-White/Teal/Sage Farbpalette
- ✅ Light/Dark Mode Toggle
- ✅ Therapeuten-optimierte UI

### Phase 13: Adaptive Harmonisierung
- ✅ Re-Analyse nach Zyklus-Ende
- ✅ Automatische Frequenzlisten-Anpassung

### Phase 14: Spooky2 Hardware-Integration
- ✅ WebSerial-Protokoll (XM Generator + Generator X Pro)
- ✅ Frequenz-Upload, Wellenform-Steuerung
- ✅ Spooky2Panel Komponente

### Phase 15: Klienten-Dashboard
- ✅ Route `/klient/:id`
- ✅ Session-Timeline, Trends, Remedies
- ✅ KlientDashboard.tsx (372 Zeilen)

### Phase 16: AudioWorklet + FFT
- ✅ Custom AudioWorkletProcessor (48kHz, sub-1ms Latenz)
- ✅ AnalyserNode mit FFT-Size 2048
- ✅ SpectrumVisualizer (Canvas: Spektrum-Balken + Oszilloskop)
- ✅ AudioWorklet-Badge und Live-Status-Anzeige
- ✅ Automatischer Fallback auf Standard-Oszillatoren
- ✅ Browser-Test bestätigt: AudioWorklet aktiv, 6ms Latenz

---

## Nächste Phasen (geplant)

### Phase 17: Anatomy-Modell & NLS-Punktsystem
- BodyParts3D als anatomische Masterdatenquelle (FMA-IDs)
- Definierte Organ-Schemas (Heart, Brain als Piloten)
- Punkt-Klassen: A (Anatomisch), S (Scan), V (Validierung)
- Geodätisches Farthest Point Sampling
- 3D Slicer Markups JSON als Punkt-Master
- GLB-Export mit eingebetteten Landmarken

### Phase 18: GPU/CPU-Optimierung
- LOD (Level of Detail) für 3D-Modelle
- Instanced Rendering für Meridianpunkte
- Frame-Rate-Begrenzung bei Inaktivität

---

## Bekannte offene Punkte

1. **3D-Modelle**: Derzeit nur Basis-GLB; hochdetaillierte Z-Anatomy/BodyParts3D-Modelle noch nicht integriert
2. **TCM-Meridiane in 3D**: Frei exportierbare GLB-Datensätze mit verifizierten Koordinaten nicht verfügbar; muss manuell modelliert werden
3. **NLS-Punktkoordinaten**: Aktuell auf organ_scan_points-Tabelle basiert; benötigt echte anatomische Landmark-Koordinaten

---

## Hinweis zur Wiederherstellung

Falls eine Wiederherstellung nötig ist, nutzen Sie die Lovable-History-Funktion:
> Klicken Sie auf den Revert-Button unter der Chat-Nachricht vom 2026-03-08 (v2), um den exakten Zustand wiederherzustellen.
