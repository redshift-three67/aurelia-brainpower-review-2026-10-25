# Wiederherstellungspunkt – 2026-03-08

**Erstellt:** 2026-03-08T14:00:00Z  
**Anlass:** Vor Implementierung Phase 11–16 (Konsolidierter Projektplan v2)  
**Status:** Alle 10 Kernphasen abgeschlossen, 100 Remedies in DB, System stabil

---

## Datenbankschema (IST-Zustand)

### Tabellen
| Tabelle | Spalten (Schlüssel) | RLS | Status |
|---------|-------------------|-----|--------|
| `clients` | id, first_name, last_name, birth_date, birth_place, photo_url, field_signature, notes, **user_id** | ✅ Korrekt (user_id = auth.uid()) | OK |
| `client_vectors` | id, client_id, dimension_*, phase, session_id, input_method, sensor_data | ✅ RLS via client_id→clients.user_id | OK |
| `treatment_sessions` | id, client_id, session_number, session_date, status, notes, vector_snapshot, diagnosis_snapshot, treatment_summary, duration_seconds | ✅ RLS via client_id | OK |
| `harmonization_protocols` | id, client_id, vector_id, frequency, amplitude, waveform, output_type, modulation_*, status | ✅ RLS via client_id | OK |
| `harmonization_jobs` | id, client_id, vector_id, protocol_id, status, progress, job_type, target_frequencies | ✅ RLS via client_id | OK |
| `chreode_trajectories` | id, client_id, session_id, dimensions, stability, bifurcation_risk, chreode_alignment, phase | ✅ INSERT/SELECT for authenticated | OK |
| `resonance_results` | id, session_id, client_id, scan_point_id, scan_frequency, intensity, dysregulation_score, organ_name | ✅ RLS via client_id | OK |
| `word_energies` | id, word, frequency, category, meridian, chakra, organ_system | SELECT only (Referenzdaten) | OK |
| `word_energy_collections` | id, user_id, name, words, description | ✅ RLS via user_id = auth.uid() | OK |
| `anatomy_resonance_points` | id, name, body_region, x/y/z_position, primary_frequency | SELECT only (Referenzdaten) | OK |
| `organ_scan_points` | id, point_index, scan_frequency, organ_system, organ_name_de, body_region, layer_depth | SELECT only (Referenzdaten) | OK |
| `anatomy_models` | id, name, category, file_path, storage_type, supports_* flags | ✅ Full CRUD for authenticated | OK |
| `remedies` | id, name, name_latin, category, frequency, meridian_associations, organ_associations, element, emotional_pattern | ✅ SELECT + INSERT | **100 Datensätze** |

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
| `src/pages/Analyse.tsx` | Hauptarbeitsseite: Vektor, Meridian-Diagnose, Frequenz-Output, NLS, Sessions | 246 |
| `src/pages/Login.tsx` | Login-only (kein Signup), Zod-Validierung | 178 |
| `src/pages/Export.tsx` | WHO-Datenbank Download (JSON/CSV) | – |
| `src/pages/NotFound.tsx` | 404-Seite | – |

### Routing (App.tsx)
- `/` → Index (public)
- `/analyse` → ProtectedRoute → Analyse
- `/export` → ProtectedRoute → Export
- `/exports` → Redirect → `/export`
- `/login` → Login
- `*` → NotFound

### Hooks (Geschäftslogik)
| Datei | Zeilen | Beschreibung |
|-------|--------|-------------|
| `useClientDatabase.ts` | 304 | CRUD clients + vectors, Photo-Upload |
| `useMeridianDiagnosis.ts` | – | Meridian-Diagnose via Edge Function |
| `useTreatmentSequence.ts` | 728 | Behandlungssequenz mit AM-Modulation, 1-42x Zyklen |
| `useTreatmentArchive.ts` | – | Behandlungs-Archiv |
| `useSessionManagement.ts` | 177 | Session-CRUD, Start/Complete |
| `useChreodeTracking.ts` | – | Chreode-Trajektorien aufzeichnen |
| `useResonanceDatabase.ts` | – | Anatomie-Resonanzpunkte Abfrage |
| `useResonanceResults.ts` | – | NLS-Scan-Ergebnisse speichern |
| `useOrganScanPoints.ts` | – | Organ-Scan-Punkte laden |
| `useNLSAutoScan.ts` | – | Automatischer NLS-Scan |
| `useAnatomyModels.ts` | – | 3D-Modell-Verwaltung |
| `useRemedyDatabase.ts` | – | Remedy-Datenbank Abfrage |
| `useRealtimeHarmonization.ts` | – | Realtime Harmonisierungs-Session |
| `useRealtimeSync.ts` | – | Realtime-Synchronisation |
| `useHardwareDiscovery.ts` | – | Hardware-Erkennung (WebUSB/WebSerial) |
| `useSystemMonitor.ts` | – | System-Monitoring |
| `useServerHardwareMetrics.ts` | – | Server-Hardware-Metriken |
| `useAuth.ts` | – | Authentifizierung |

### Kern-Komponenten
| Datei | Zeilen | Beschreibung |
|-------|--------|-------------|
| `ClientVectorInterface.tsx` | – | Klienten-Eingabe + Vektor-Berechnung |
| `ClientVectorTrajectory3D.tsx` | – | 3D-Vektor-Visualisierung |
| `AnatomyResonanceViewer.tsx` | 2123 | 3D-Anatomie mit Meridianen, Chakren, NLS-Scan, Organ-Layer |
| `MeridianDiagnosisPanel.tsx` | 1355 | Meridian-Diagnose, Behandlungssequenz, Nachtestung, Archiv |
| `FrequencyOutputModule.tsx` | 725 | Audio/EM-Frequenzausgabe mit Bipolar/Harmonik-Modi |
| `WordEnergyDBManager.tsx` | 417 | Wort-Energie-Sammlungen + Resonanz-Analyse |
| `SessionManagementPanel.tsx` | 138 | Aktive Sitzung, Session-Historie |
| `SessionReportGenerator.tsx` | 269 | PDF/HTML-Bericht-Export |
| `TCMTrendAnalytics.tsx` | 270 | Wu-Xing Element-Trend-Visualisierung |
| `RemedyDatabasePanel.tsx` | – | Remedy-Datenbank UI mit Filter |
| `BifurcationWarningWidget.tsx` | – | Bifurkations-Warnung in Echtzeit |
| `RealtimeStatusWidget.tsx` | – | Realtime-Verbindungsstatus |
| `NLSScanConfigPanel.tsx` | – | NLS-Scan Konfiguration |
| `NLSAutoScanOverlay.tsx` | – | Auto-Scan Fortschritts-Overlay |
| `HardwareMethodSelector.tsx` | – | Hardware-Methoden Auswahl |
| `SystemStatusDashboard.tsx` | – | System-Status Dashboard |

### Services
| Datei | Beschreibung |
|-------|-------------|
| `feldengine/ThomVectorEngine.ts` | Kern-Mathematik: Thom-Vektor, Feldsignatur, Attraktoren |
| `feldengine/BifurcationDetector.ts` | Echtzeit-Bifurkationserkennung |
| `hardware/*` | Hardware Discovery, System Monitor, Device Profiles |
| `harmonization/*` | Harmonization Job Service |
| `realtime/*` | Realtime Harmonization + Sync Services |

### Design-System
| Datei | Beschreibung |
|-------|-------------|
| `src/index.css` | 254 Zeilen: Dark Theme, HSL-Tokens, Animations, Custom Utilities |
| `tailwind.config.ts` | 131 Zeilen: Semantic Colors, Custom Fonts, Gradients, Shadows |

---

## Bekannte Issues (vor Phase 11)

1. **WordEnergy-Bug**: `analyzeResonance()` zeigt "Bitte erst einen Klienten-Vektor erstellen" auch wenn nur CRUD gewünscht (kein Vektor nötig für Sammlung-Verwaltung)
2. **Frequenz-Strich**: In `TreatmentInProgress` wird manchmal `— Hz` statt Frequenzwert angezeigt (Type-Conversion bei NLS-Punkten)
3. **diagnosis_snapshot**: Wird bei `completeSession()` nicht immer mitgespeichert → Trend-Analyse hat Datenlücken
4. **NLS-Scan-Config Position**: Ist aktuell im Side-Panel statt oben rechts unterhalb des Analysefeldes
5. **Dark Theme**: Aktuelles Design ist sehr dunkel; Nutzer wünscht helleres, freundlicheres Healing-Theme

---

## Geplante Änderungen (Phase 11–16)

### Phase 11: Kritische Bugs fixen
- WordEnergy CRUD ohne Vektor-Pflicht
- Frequenz-Anzeige Strich-Bug beheben
- diagnosis_snapshot zuverlässig speichern
- NLS-Scan-Config Position korrigieren

### Phase 12: Healing-Theme
- Helles, freundliches Design mit Teal/Sage/Warm-White
- Light/Dark Mode Toggle
- Therapeuten-optimierte Farbpalette

### Phase 13: Adaptive Harmonisierung
- Re-Analyse nach Zyklus-Ende
- Verbleibende Dysregulationen fließen in nächsten Zyklus ein
- Automatische Anpassung der Frequenzliste

### Phase 14: Spooky2 Hardware-Integration
- WebSerial-Protokoll für Spooky2 XM Generator
- WebSerial-Protokoll für Spooky2 Generator X Pro
- Frequenz-Upload, Wellenform-Steuerung

### Phase 15: Klienten-Dashboard
- Dedizierte Unterseite `/klient/:id`
- Session-Timeline, Trends, Remedies, Berichte
- Umfassendes Klienten-Management

### Phase 16: Audio-Qualitätsoptimierung
- AudioWorklet für sub-1ms Latenz
- AnalyserNode für Echtzeit-FFT
- Spektrum-Visualisierung

---

## Hinweis zur Wiederherstellung

Falls eine Wiederherstellung nötig ist, nutzen Sie die Lovable-History-Funktion:
> Klicken Sie auf den Revert-Button unter der Chat-Nachricht vom 2026-03-08, um den exakten Zustand wiederherzustellen.
