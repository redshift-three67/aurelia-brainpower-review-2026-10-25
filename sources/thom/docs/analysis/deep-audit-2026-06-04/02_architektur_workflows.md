# 02 Architektur, Projektstruktur, Workflows, Steppings

## Architekturüberblick

RadiThoms besteht aus vier Schichten:

1. Browser-App
   - Vite + React + TypeScript.
   - shadcn/ui, Tailwind, Radix UI, Framer Motion.
   - React Router für Seitenrouting.
   - React Query ist global eingebunden, wird aber nicht flächendeckend als Datenzugriffsschicht genutzt.

2. Fachlogik im Frontend
   - Feldengine-/Thom-Vektorberechnung.
   - TCM-/Meridian-/Organ-/Resonanz-Algorithmen.
   - WebAudio-Frequenzgenerator.
   - WebSerial/WebUSB-Hardwareintegration.
   - Realtime-Clientservices.

3. Supabase Backend
   - Auth.
   - Postgres Tabellen + RLS.
   - Storage Buckets für Client-Fotos und 3D-Modelle.
   - Realtime Publication für ausgewählte Tabellen.
   - Edge Functions für WebSocket/REST/KI-Gateway.

4. Dokumentations- und Konzeptschicht
   - Umfangreiche Markdown-Dokumentation in `docs/`.
   - Konzepte zu René Thom, Feldengine, Realtime-Hardware, Z-Anatomy.

## Root-Struktur

| Pfad | Zweck |
|---|---|
| `src/` | React-App, Komponenten, Hooks, Services, Fachlogik. |
| `supabase/` | Supabase Config, Edge Functions, DB-Migrationen. |
| `docs/` | Architektur-/Projekt-/Konzeptdokumentation. |
| `public/` | Statische Assets, WHO-Meridianexporte, GLB-Modell. |
| `package.json` | npm Scripts und Dependencies. |
| `vite.config.ts` | Vite-Konfiguration plus WHO-Meridian-Exportgenerator. |
| `.env` | Aktuell versionierte Supabase-Konfiguration. |

## Frontend-Routen

Aus `src/App.tsx`:

| Route | Schutz | Zweck |
|---|---|---|
| `/` | öffentlich | Landingpage/Konzept/Feldengine-Präsentation. |
| `/analyse` | `ProtectedRoute` | Klienten-Feldanalyse, Meridian, Frequenz, Hardware, Sessions. |
| `/export` | `ProtectedRoute` | Exportbereich. |
| `/klient/:id` | `ProtectedRoute` | Klienten-Dashboard. |
| `/workflow` | öffentlich | Z-Anatomy Workflow. |
| `/import` | öffentlich | Pilotdaten-/Landmark-Import-Anleitung. |
| `/exports` | Redirect | Alias zu `/export`. |
| `/login` | öffentlich | Login/Registrierung. |
| `*` | öffentlich | NotFound. |

Bewertung:

- Dass `/analyse`, `/export`, `/klient/:id` geschützt sind, ist gut.
- `/workflow` und `/import` sind eher dokumentative Seiten; öffentlich ist vertretbar, solange keine echten Upload-/Datenänderungen stattfinden. Die Texte sprechen aber von Upload/Integration; falls daraus echte Funktionen werden, Auth erzwingen.

## Services

### `src/services/feldengine/`

- `ThomVectorEngine.ts`
- `BifurcationDetector.ts`
- `index.ts`

Funktionalität:

- Fachkern für Zustandsvektoren, Attraktoren, Chreoden/Bifurkationen.
- Wird in Analyse-/Trajectory-/Warning-Komponenten genutzt.

Einschätzung:

- Konzeptuell zentral.
- Sollte als eigener reiner Domain-Kern mit Tests separiert werden, weil diese Logik fachlich entscheidend ist.
- Aktuell gibt es keine sichtbaren Unit-Tests für die mathematischen/medizinisch interpretierten Berechnungen.

### `src/services/realtime/`

- `RealtimeSyncService.ts`
- `RealtimeHarmonizationService.ts`

Funktionalität:

- WebSocket-Verbindungen zu Supabase Edge Functions.
- Latenz-Ping alle 2 Sekunden.
- Broadcast/Senden von Vector/Frequency/Hardware/Session Events.
- WebAudio/AudioWorklet-Erzeugung von Frequenzen.

Einschätzung:

- Gute technische Grundstruktur für Realtime-UX.
- Sicherheits- und Isolationsmodell fehlt.
- Keine Backpressure-/Rate-Limit-/Schema-Validierung.
- Keine Messung echter Ende-zu-Ende-Latenz für therapeutisch relevante Events.

### `src/services/hardware/`

- `HardwareDiscoveryService.ts`
- `SystemMonitorService.ts`
- `Spooky2Service.ts`
- `deviceProfiles.ts`

Funktionalität:

- Browserseitige WebUSB/WebSerial Discovery.
- Spooky2-Kommandos über Serial-Port.
- Simulierte System-/Hardwaremetriken.

Einschätzung:

- WebSerial/WebUSB-Ansatz ist passend für Chrome/Edge lokale Hardware.
- Es fehlen Safety-Gates: Amplituden-/Frequenzprofile pro Gerät, Not-Aus, Session-Logging, Patientensicherheit, Firmware-Protokollvalidierung.
- `SystemMonitorService` ist ausdrücklich simulativ, obwohl UI/Docs teils produktiv wirkende Hardwaredaten suggerieren.

### `src/services/harmonization/`

- `HarmonizationJobService.ts`

Funktionalität:

- Supabase-Zugriff auf `harmonization_jobs`.
- Status-/Jobverwaltung für Harmonisierungsprozesse.

Einschätzung:

- Persistenzkonzept vorhanden.
- Realtime-/State-Machine-Abgleich mit Edge Function/WebSocket ist nicht vollständig robust modelliert.

## Hooks

Wichtige Hooks:

| Hook | Zweck |
|---|---|
| `useAuth` | Supabase Auth Session. |
| `useClientDatabase` | Clients, Fotos, Vektoren. |
| `useSessionManagement` | Treatment Sessions. |
| `useResonanceResults` | Resonanzresultate. |
| `useTreatmentArchive` | Harmonization Jobs. |
| `useClientGroups` | Klientengruppen. |
| `useRealtimeSync` | Realtime WebSocket Client. |
| `useRealtimeHarmonization` | Audio/Realtime-Harmonisierung. |
| `useHardwareDiscovery` | WebUSB/WebSerial Geräte. |
| `useSpooky2` | Spooky2 Device-Kommandos. |
| `useMeridianDiagnosis` | TCM-/AI-Empfehlungsfluss. |
| `useOrganScanPoints`, `useOrganLandmarks`, `useAnatomyModels` | Anatomie-/Scan-Daten. |

Bewertung:

- Domain-Hooks sind gut modularisiert.
- Viele Hooks verwenden direkte Supabase-Zugriffe statt zentraler Repository-/Service-Schicht. Dadurch sind Security-/Error-/Audit-Patterns verteilt.
- React Hook Dependency Warnings deuten auf mögliche stale closures und unzuverlässige Realtime-/Timer-Zustände.

## Komponentenlandschaft

Top-Level fachliche Komponenten:

- `ClientVectorInterface.tsx`
- `ClientVectorTrajectory3D.tsx`
- `AnatomyResonanceViewer.tsx`
- `MeridianDiagnosisPanel.tsx`
- `FrequencyOutputModule.tsx`
- `Spooky2Panel.tsx`
- `RealtimeStatusWidget.tsx`
- `BifurcationWarningWidget.tsx`
- `TreatmentTrendAnalysis.tsx`
- `TCMTrendAnalytics.tsx`
- `SessionReportGenerator.tsx`
- `SessionManagementPanel.tsx`
- `RemedyDatabasePanel.tsx`
- `GroupManagementPanel.tsx`
- `WordEnergyDBManager.tsx`

UI-System:

- umfangreiche shadcn/ui-Komponenten unter `src/components/ui/`.

3D/Anatomie:

- `CuspSurface3D.tsx`
- `FieldVisualization.tsx`
- `AnatomyResonanceViewer.tsx`
- `anatomy/GLBModelLoader.tsx`
- `anatomy/ModelUpload.tsx`
- `anatomy/ModelSelector.tsx`
- `anatomy/OrganScanLayer.tsx`
- `anatomy/OrganLandmarkLayer.tsx`
- `anatomy/InteractiveMeridianPoints.tsx`
- `anatomy/DetailedHumanModel.tsx`

## Datenmodell / Supabase Tabellen

Aus Migrationen erkannt:

| Tabelle | Zweck |
|---|---|
| `clients` | Klienten-Stammdaten inkl. Name, Geburtsdatum, Geburtsort, Foto-URL, field_signature, Notizen. |
| `client_vectors` | 5-dimensionale Zustandsvektoren, Sensor-/Anamnese-/Sessiondaten. |
| `harmonization_protocols` | Frequenz-/Amplitude-/Waveform-/Dauer-/Output-Protokolle. |
| `word_energies` | Wort-/Energie-/Resonanzdaten. |
| `anatomy_resonance_points` | Anatomische Resonanzpunkte. |
| `harmonization_jobs` | Harmonisierungsjobs. |
| `anatomy_models` | 3D-Modelle und Metadaten. |
| `organ_scan_points` | Organ-Scan-Punkte. |
| `treatment_sessions` | Behandlungssitzungen inkl. Snapshots. |
| `resonance_results` | Resonanzresultate. |
| `word_energy_collections` | Wortenergie-Sammlungen. |
| `remedies` | Remedies/Heilmittel-Frequenzen. |
| `chreode_trajectories` | Chreoden-Trajektorien. |
| `organ_schemas` | Organschemata. |
| `organ_landmarks` | Organ-Landmarks. |
| `client_groups` | Gruppen. |
| `client_group_members` | Gruppenzuordnungen. |

## Workflow: Benutzer/Auth

Stepping:

1. Nutzer öffnet `/login`.
2. Login/Registrierung über Supabase Auth.
3. `ProtectedRoute` prüft `supabase.auth.getSession()`.
4. Auth-State wird via `onAuthStateChange` beobachtet.
5. Bei fehlender Session Redirect zu `/login`.
6. Bei vorhandener Session Zugriff auf Analyse/Export/Klientenseiten.

Lücke:

- Frontend-Schutz ersetzt keine Backend-Autorisierung.
- Edge Functions ignorieren JWT laut Config.
- RLS muss alle Datenzugriffe absichern.

## Workflow: Klienten-Feldanalyse

Rekonstruierter Ablauf aus `Analyse.tsx`:

1. Analyse-Seite wird geladen (`/analyse`, geschützt).
2. `ClientVectorInterface` erlaubt Klientenauswahl / Vektorerstellung.
3. Bei Klientenauswahl lädt `useSessionManagement` bestehende Sessions.
4. Bei Vektorerstellung:
   - `currentVectorAnalysis` wird gesetzt.
   - Falls Klient gewählt und keine aktive Session: `startSession`.
   - Chreode-Punkt wird über `useChreodeTracking` aufgezeichnet.
5. `ClientVectorTrajectory3D` visualisiert Vektortrajektorie.
6. `AnatomyResonanceViewer` berechnet/visualisiert Anatomie-/Resonanzbezüge.
7. `MeridianDiagnosisPanel` verarbeitet NLS-/TCM-Daten und kann Frequenzen auswählen.
8. `FrequencyOutputModule` und `Spooky2Panel` geben Frequenz lokal/extern aus.
9. Bei Abschluss ruft `completeSession` Snapshots/Dauer auf.
10. Trend-/Berichts-/Remedy-/TCM-Komponenten zeigen Auswertung.

Substeppings mit Risiko:

- Vektor-/Diagnose-/Sessiondaten sind sensible Gesundheitsdaten.
- Frequenzausgabe kann reale Hardware triggern; es fehlen zentrale Safety-Bestätigungen.
- KI-Diagnosefluss muss rechtlich/medizinisch klar als Assistenz gekennzeichnet werden.

## Workflow: Realtime-Sync

Clientseitig `RealtimeSyncService.ts`:

1. WebSocket zu `wss://yoryyvfuscyfumeseour.supabase.co/functions/v1/realtime-sync`.
2. Server sendet `connected` mit `clientId`.
3. Client pingt alle 2 Sekunden.
4. Client kann senden:
   - `vector_update`
   - `frequency_sync`
   - `hardware_status`
   - `session_event`
5. Server broadcastet Events an andere Clients.
6. Client sammelt Latenzstatistik aus Pong.

Serverseitig `realtime-sync/index.ts`:

1. Upgrade auf WebSocket.
2. Anonyme Client-ID generieren.
3. Connection in globaler Map speichern.
4. Eingehende Events parsen.
5. Events ohne Auth-/Sessionprüfung an alle anderen Clients broadcasten.

Bewertung:

- Funktioniert als Demo-Eventbus.
- Nicht geeignet für Patientendaten oder Frequenz-/Hardware-Steuerung in Multi-User-Umgebung ohne Rooms/JWT/RLS-Backchannel.

## Workflow: Hardware-Metriken

`hardware-metrics/index.ts`:

1. REST `/metrics` liefert einmalige synthetische Metriken.
2. REST `/config` liefert statische Server-Konfiguration.
3. WebSocket sendet initial Config.
4. Alle 500ms werden generierte Metriken gestreamt.
5. Client kann `set_interval` zwischen 100ms und 5000ms senden.

Bewertung:

- Gute UI-Simulationsquelle.
- Keine echte Hardwaremessung.
- Public WebSocket kann unnötige Serverlast erzeugen; Rate-Limits fehlen.

## Workflow: Meridian-KI-Diagnose

`meridian-diagnosis/index.ts`:

1. JSON Body mit `clientVector` und `imbalances` wird angenommen.
2. Aus diesen Daten wird ein deutscher Prompt erstellt.
3. Funktion nutzt `LOVABLE_API_KEY` und ruft `https://ai.gateway.lovable.dev/v1/chat/completions` auf.
4. Modell: `google/gemini-2.5-flash`.
5. Antwort wird als `text/event-stream` zurückgegeben.

Bewertung:

- Fachlich nützlicher Assistenzfluss.
- Aktuell ohne JWT-Verifikation laut `config.toml` und wildcard CORS kritisch.
- Es fehlen Consent, Logging-Minimierung, Prompt-Injection-Abwehr, medizinischer Disclaimer und PII-Reduktion.

## Workflow: Z-Anatomy und Pilotdaten

`/workflow`:

- Anleitung zum Download/Export von Z-Anatomy/BodyParts3D/GLB-Modellen.
- Lokaler UI-Fortschritt über `useState`, keine Persistenz.

`/import`:

- Datenquellenliste und CSV/JSON-Formate.
- Import-Schritte sind aktuell dokumentativ, nicht vollautomatisch.

Bewertung:

- Gute konzeptionelle Brücke für Anatomieerweiterung.
- Wenn Upload/Import real wird, braucht es Auth, Validierung, Dateiscans, Lizenzprüfung, Größenlimits.

## Build-/Export-Spezialfall WHO-Meridianpunkte

`vite.config.ts` enthält ein eigenes Plugin `generateWhoMeridianExports()`:

- Bundlet `src/utils/meridianPoints/index.ts` via esbuild.
- Importiert das Bundle über data URL.
- Generiert `public/exports/who-meridian-points.json` und `.csv`.
- Build-Ausgabe bestätigte: 296 Punkte.

Bewertung:

- Praktisch für statische Exporte.
- Generierung während Dev/Build kann unerwartet Working-Tree-Dateien aktualisieren; im Test blieb `git status` sauber.
- Für CI sollte ein Drift-Check eingebaut werden.
