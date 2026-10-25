# Wiederherstellungspunkt – 2026-03-04

**Erstellt:** 2026-03-04  
**Anlass:** Vor Implementierung der Sicherheits- und Funktionshärtung  
**Status:** Alle Dateien funktional, keine kritischen Fehler

---

## Datenbankschema (IST-Zustand)

### Tabellen
| Tabelle | Spalten (Schlüssel) | RLS | Kritische Lücke |
|---------|-------------------|-----|-----------------|
| `clients` | id, first_name, last_name, birth_date, birth_place, photo_url, field_signature, notes | `true` (offen) | **Kein user_id** – keine Datenisolierung |
| `client_vectors` | id, client_id (FK→clients), dimension_*, phase, session_id | `true` (offen) | Erbt Lücke von clients |
| `harmonization_protocols` | id, client_id (FK→clients), vector_id, frequency, amplitude, waveform | `true` (offen) | Erbt Lücke von clients |
| `harmonization_jobs` | id, client_id (FK→clients), vector_id, protocol_id, status, progress | `true` (offen) | Erbt Lücke von clients |
| `word_energies` | id, word, frequency, category, meridian, chakra | SELECT only | OK (Referenzdaten) |
| `anatomy_resonance_points` | id, name, body_region, x/y/z_position, primary_frequency | SELECT only | OK (Referenzdaten) |

### Storage Buckets
- `client-photos` (public: yes)

### Edge Functions
- `realtime-sync` (verify_jwt: false)
- `hardware-metrics` (verify_jwt: false)
- `meridian-diagnosis` (verify_jwt: false)

---

## Kritische Anwendungsdateien

### Seiten
| Datei | Beschreibung | Zeilen |
|-------|-------------|--------|
| `src/pages/Index.tsx` | Landing Page mit Hero, Konzepten, 3D-Cusp, CTA | 72 |
| `src/pages/Analyse.tsx` | Hauptarbeitsseite: Vektor, Meridian-Diagnose, Frequenz-Output | 144 |
| `src/pages/Login.tsx` | Login-only (kein Signup), Zod-Validierung | 178 |
| `src/pages/Export.tsx` | WHO-Datenbank Download (JSON/CSV) | – |
| `src/pages/NotFound.tsx` | 404-Seite | – |

### Routing
| Datei | Beschreibung |
|-------|-------------|
| `src/App.tsx` | BrowserRouter, Routen: /, /analyse, /export, /exports→/export, /login, * | 

### Hooks (Geschäftslogik)
| Datei | Beschreibung | Zeilen |
|-------|-------------|--------|
| `src/hooks/useClientDatabase.ts` | CRUD clients + vectors, Photo-Upload | 304 |
| `src/hooks/useMeridianDiagnosis.ts` | Meridian-Diagnose via Edge Function | – |
| `src/hooks/useRealtimeHarmonization.ts` | Realtime Harmonisierungs-Session | – |
| `src/hooks/useRealtimeSync.ts` | Realtime-Synchronisation | – |
| `src/hooks/useResonanceDatabase.ts` | Anatomie-Resonanzpunkte Abfrage | – |
| `src/hooks/useTreatmentArchive.ts` | Behandlungs-Archiv | – |
| `src/hooks/useTreatmentSequence.ts` | Automatische Behandlungssequenz | – |
| `src/hooks/useHardwareDiscovery.ts` | Hardware-Erkennung | – |
| `src/hooks/useSystemMonitor.ts` | System-Monitoring | – |
| `src/hooks/useServerHardwareMetrics.ts` | Server-Hardware-Metriken | – |

### Services
| Datei | Beschreibung |
|-------|-------------|
| `src/services/feldengine/ThomVectorEngine.ts` | Kern-Mathematik: Thom-Vektor, Feldsignatur, Attraktoren |
| `src/services/feldengine/index.ts` | Re-exports |
| `src/services/hardware/*` | Hardware Discovery, System Monitor, Device Profiles |
| `src/services/harmonization/*` | Harmonization Job Service |
| `src/services/realtime/*` | Realtime Harmonization + Sync Services |

### Datenbank (Frontend)
| Datei | Beschreibung |
|-------|-------------|
| `src/utils/meridianPoints/*.ts` | WHO-409 Akupunkturpunkt-Datenbank (9 Meridian-Dateien + index) |
| `src/utils/meridianPointsDatabase.ts` | Haupt-Datenbank mit Lung, LI, ST, DU, REN, Extra-Punkte |

### Komponenten (Schlüssel)
| Datei | Beschreibung |
|-------|-------------|
| `src/components/ClientVectorInterface.tsx` | Klienten-Eingabe + Vektor-Berechnung |
| `src/components/ClientVectorTrajectory3D.tsx` | 3D-Vektor-Visualisierung |
| `src/components/MeridianDiagnosisPanel.tsx` | Meridian-Diagnose UI |
| `src/components/FrequencyOutputModule.tsx` | Frequenz-Ausgabe (Audio/PEMF) |
| `src/components/AnatomyResonanceViewer.tsx` | Anatomie-Resonanz 3D-Viewer |
| `src/components/AcupuncturePointSearch.tsx` | Punktesuche |
| `src/components/TreatmentTrendAnalysis.tsx` | Behandlungstrend-Analyse |
| `src/components/RealtimeStatusWidget.tsx` | Realtime-Status |
| `src/components/SystemStatusDashboard.tsx` | System-Status Dashboard |

### Konfiguration
| Datei | Beschreibung |
|-------|-------------|
| `vite.config.ts` | Vite + WHO-Export-Plugin (esbuild) |
| `tailwind.config.ts` | Tailwind-Konfiguration |
| `src/index.css` | Design-Tokens, Farbsystem |
| `supabase/config.toml` | Edge Function Konfiguration |

---

## Geplante Änderungen (nach diesem Punkt)

1. **user_id auf `clients`** – Spalte hinzufügen, FK auf auth.users
2. **RLS-Policies** – Von `true` auf `auth.uid() = user_id` umstellen
3. **Route Guards** – /analyse, /export nur für authentifizierte Benutzer
4. **Hook-Updates** – user_id automatisch bei CRUD setzen

---

## Hinweis zur Wiederherstellung

Falls eine Wiederherstellung nötig ist, nutzen Sie die Lovable-History-Funktion:
> Klicken Sie auf den Revert-Button unter dieser Chat-Nachricht, um den exakten Zustand wiederherzustellen.
