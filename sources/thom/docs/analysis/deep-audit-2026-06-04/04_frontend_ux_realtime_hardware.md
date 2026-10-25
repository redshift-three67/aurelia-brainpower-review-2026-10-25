# 04 Frontend, UX, Realtime, Hardware

## Frontend-Stack

- Vite 5.
- React 18.
- TypeScript 5.8.
- React Router 6.
- shadcn/ui/Radix UI.
- Tailwind CSS.
- Framer Motion.
- React Three Fiber / drei / three.js.
- Supabase JS.
- Recharts.
- React Hook Form / Zod.

## Lokaler Browserbefund

Getestet mit lokalem Vite Dev Server auf `127.0.0.1:5174`.

### `/`

- Rendert erfolgreich.
- Titel: `Feldengine – Morphogenese & Katastrophentheorie | René Thom`.
- Sichtbar: Feldengine Landingpage, Konzeptsektionen, 3D/Simulationselemente.
- Browser-Konsole: keine JS-Fehler im initialen Test.

### `/analyse`

- Ohne Login redirectet die Route korrekt auf `/login`.
- Login-Seite rendert mit Tabs `Anmelden` / `Registrieren`.
- Browser-Konsole: keine JS-Fehler im initialen Test.

Einschränkung:

- Authentifizierter Analyseflow wurde nicht mit echten Zugangsdaten getestet.
- Hardware/WebSerial/WebUSB wurde nicht mit physischen Geräten getestet.

## UX-Struktur

### Öffentliche Experience

Die Landingpage ist stark konzeptuell und präsentiert:

- René Thom/Katastrophentheorie.
- Chreoden/Attraktoren/Bifurkationen.
- Morphogenetische Felder.
- Frequenztherapie.
- interaktive Kuspen-Simulationen.

Stärken:

- Visuell/fachlich kohärent.
- Gute Storyline für Konzeptvermittlung.
- 3D-/Animationselemente sind differenzierend.

Schwächen:

- Potenziell zu viel theoretische Tiefe vor konkretem Nutzen.
- Medizinisch/therapeutische Claims brauchen Disclaimer und Evidenz-/Grenzenabschnitt.
- README ist noch Lovable-Template und passt nicht zum tatsächlichen Projekt.

### Authentifizierte Experience

`/analyse` bündelt sehr viele Funktionsbereiche:

- Klientenvektor.
- 3D-Trajektorie.
- Anatomie-Viewer.
- Meridian-Diagnose.
- Frequenzausgabe.
- Spooky2-Ausgabe.
- Remedies.
- TCM Trends.
- Reports.
- Realtime Widget.

Stärken:

- Hoher fachlicher Integrationsgrad.
- Workflow von Analyse → Frequenz → Session → Trend ist erkennbar.

Risiken:

- Kognitive Überlastung.
- Fehlbedienung bei Frequenz-/Hardwareausgabe.
- Viele Module auf einer Seite können Performance und Fehlerisolierung belasten.
- Kein klarer Wizard mit Safety-/Consent-Steps.

Empfehlung:

Eine phase-gated Analyse-UX einführen:

1. Klient wählen / Consent prüfen.
2. Anamnese-/Vektorinput validieren.
3. Analyse berechnen.
4. Befund reviewen.
5. Frequenz-/Hardwareplan konfigurieren.
6. Safety-Check/Bestätigung.
7. Durchführung mit Live-Monitoring/Not-Aus.
8. Abschluss/Report/Archiv.

## Realtime-Funktionalitäten

### Implementierte Realtime-Flächen

1. Supabase Realtime Publication:
   - `clients`
   - `client_vectors`
   - `harmonization_protocols`

2. Edge WebSocket `realtime-sync`:
   - vector_update
   - frequency_sync
   - hardware_status
   - session_event
   - ping/pong latency

3. Edge WebSocket `hardware-metrics`:
   - simulierte Hardwaremetriken alle 500ms.

4. Client Services:
   - `RealtimeSyncService.ts`
   - `RealtimeHarmonizationService.ts`
   - `useRealtimeSync.ts`
   - `useRealtimeHarmonization.ts`
   - `useServerHardwareMetrics.ts`

### Latenzmodell

`RealtimeSyncService` misst Ping/Pong:

- Ping alle 2 Sekunden.
- One-way-Schätzung = Roundtrip / 2.
- Sampleliste letzte 50.
- Min/Max/Avg.

Bewertung:

- Gut für grobe UI-Latenz.
- Nicht ausreichend für therapeutische/Hardware-Synchronität.
- Kein Clock Sync, kein Jitter-Puffer, keine Sequenznummern, keine verlorenen Events, keine p95/p99-Auswertung.

### Realtime-Einschätzung

| Aspekt | Befund | Reife |
|---|---|---|
| WebSocket-Verbindung | vorhanden | Demo/Alpha |
| Auto-Reconnect | vorhanden, max 5 Versuche | Basis |
| Ping/Pong-Latenz | vorhanden | Basis |
| Rooms/Mandanten | fehlt | Kritisch |
| Eventschema | fehlt | Kritisch |
| Rate-Limit | fehlt | Kritisch |
| Offline/Replay | fehlt | Mittel |
| Echte Hardware-Synchronität | nicht nachgewiesen | Kritisch |
| Ende-zu-Ende-SLO | fehlt | Kritisch |

## Frequenzausgabe / WebAudio

`RealtimeHarmonizationService.ts`:

- Erzeugt `AudioContext` mit Sample Rate 48kHz und `latencyHint: 'interactive'`.
- Erstellt AudioWorklet dynamisch aus String.
- Unterstützt Waveforms:
  - sine
  - square
  - triangle
  - sawtooth
  - harmonic
  - bipolar im Typ, aber Worklet-Switch behandelt bipolar nicht explizit.
- Unterstützt Harmonics und FM-Modulation.
- Gain Fade-in/Fade-out.
- Fallback auf `OscillatorNode`, falls Worklet fehlschlägt.
- Sendet `frequency_sync` an WebSocket.

Stärken:

- AudioWorklet ist technisch passend für latenzarme Audioerzeugung.
- Fallback erhöht Browser-Kompatibilität.
- AnalyzerNode ermöglicht Visualisierung.

Probleme:

1. `bipolar` im Typ, aber nicht im Generator-Switch umgesetzt.
2. Keine zentrale Sicherheitsgrenze für Frequenz/Amplitude/Dauer.
3. Keine Benutzerwarnung für Audioausgabe/Kopfhörer/medizinische Risiken im Service erkennbar.
4. Mehrere leere Catch-Blöcke werden von ESLint bemängelt.
5. Dynamischer Worklet-Code als String ist wartungs-/testschwach.
6. Kein automatisierter Audio-Test.

Empfehlung:

- AudioWorklet in eigene Datei auslagern.
- Frequenz-/Amplitude-/Dauergrenzen als validierte Domain-Konfiguration.
- Safe Presets pro Output-Modus.
- Not-Aus global.
- Audiograph-Zustand testbar machen.
- Behandlungsausgabe nie automatisch starten, nur nach expliziter Nutzeraktion.

## Spooky2 / WebSerial

`Spooky2Service.ts`:

- Unterstützt Modelle `xm`, `gx_pro`.
- Erkennt CH340, FT232R, FT231X, CP2102 Filter.
- Öffnet Serial Port mit 115200 8N1.
- Sendet ASCII-Kommandos:
  - Frequenz setzen.
  - Amplitude setzen.
  - Waveform setzen.
  - Start/Stop.
  - Sequenz hochladen.
  - Status abfragen.

Stärken:

- Saubere Service-Kapselung.
- Frequenz/Amplitude werden auf Maximalwerte geklemmt.
- WebSerial passt für Chrome/Edge und lokale Geräte.

Risiken/Lücken:

1. Protokoll ist offenbar angenommen; keine Verifikation gegen reale Spooky2-Spezifikation im Code.
2. Response Matching löst den ersten wartenden Callback aus, nicht command-spezifisch. Bei parallelen Kommandos kann falsche Antwort zugeordnet werden.
3. Kein Queue-/Mutex für Serial-Kommandos.
4. Kein Not-Aus-Design über alle Komponenten.
5. Keine Persistenz der tatsächlich gesendeten Kommandos in Audit-Log.
6. Keine Gerätezustandsmaschine (`disconnected`, `opening`, `ready`, `running`, `stopping`, `error`).
7. Keine medizinisch/technische Safety-Freigabe pro Sequenz.
8. Keine Hardware-in-the-loop Tests.

Empfehlung:

- Serial Command Queue mit Sequenznummern/Timeouts.
- Geräteprofile versionieren und Herstellerprotokoll prüfen.
- Dry-run Modus.
- Hardware Simulator für Tests.
- Physischer Not-Aus Button in UI und Service.
- Jede reale Ausgabe mit Session-ID, Operator-ID, Frequenz, Amplitude, Dauer auditieren.

## WebUSB/WebSerial Discovery

`HardwareDiscoveryService.ts`:

- Prüft `navigator.usb` und `navigator.serial`.
- Lädt bereits autorisierte Devices/Ports.
- Registriert connect/disconnect Events.
- Bietet gezielte Requests für USB-DAC, Frequenzgenerator, Mikrocontroller und generische Geräte.

Stärken:

- Breite Hardware-Erkennung.
- Device Profiles ausgelagert.

Risiken:

- `requestAnyUSBDevice()` und `requestAnySerialPort()` mit `filters: []` erlauben zu breite Geräteauswahl.
- Keine Schutzlogik gegen falsches Gerät.
- Keine Permission-/Privacy-Hinweise.
- Hardwaredetails werden in Events/Realtime weitergegeben.

Empfehlung:

- Generische Any-Device-Funktionen nur im Dev-Modus.
- Produktiv ausschließlich erlaubte Vendor/Product Profile.
- Explizite Nutzerhinweise vor Gerätefreigabe.
- Gerätedaten minimieren.

## Hardware-Metriken / SystemMonitor

`SystemMonitorService.ts` enthält statische Development-/Production-Hardwareprofile:

- Development: ASUS Vivobook S 16, Ryzen 9 8945HS, Radeon 780M, 16 GB.
- Production: Ryzen 5 9600X, RTX 4000 SFF Ada, 128 GB.

Die laufenden Metriken werden simuliert:

- CPU usage/frequency/temperature.
- GPU usage/VRAM/temperature.
- Memory/latency/jitter.

Bewertung:

- Als Demo brauchbar.
- Für Diagnose, Realtime-Safety oder Hardwareleistungsbewertung nicht belastbar.
- UI muss Simulation deutlich kennzeichnen.

## 3D / Anatomie

Technologien:

- Three.js / React Three Fiber / drei.
- GLB Model Loader.
- Anatomy model upload/selector.
- Organ scan/landmark layers.
- Meridian point visualization.

Stärken:

- Starkes Alleinstellungsmerkmal.
- Z-Anatomy Workflow konzeptionell gut vorbereitet.

Risiken:

- GLB-Dateien können groß und performanceintensiv sein.
- Externe 3D-Modelle brauchen Lizenz- und Sicherheitsprüfung.
- 3D-Koordinaten/Frequenzzuordnungen müssen wissenschaftlich/fachlich validiert werden.
- Build-Bundle ist sehr groß: `index-D6qWOvty.js` ca. 3.019 kB, gzip 844 kB.

Empfehlung:

- Code Splitting für 3D-/Analyse-/Admin-Komponenten.
- Lazy Routes.
- GLB-Kompression/Draco/KTX2.
- Progressive Loading und Memory-Budget.
- Separater Import-Validator.

## CSS / Rendering-Probleme

Build-Warnung:

```text
Unexpected "@keyframes"
.dark @keyframes chreode-pulse
```

Quelle:

- `src/index.css`, Zeile 275: `.dark @keyframes chreode-pulse { ... }`

Bewertung:

- CSS-Syntax ist ungültig; `@keyframes` kann nicht innerhalb eines Selektors stehen.
- Build läuft trotzdem, aber Dark-Mode-spezifische Animation wird wahrscheinlich ignoriert/fehlerhaft minifiziert.

Empfehlung:

- Eigenen Keyframe-Namen für Dark Mode definieren, z.B. `@keyframes chreode-pulse-dark`, und Klasse/Variable steuern.

## Performance

Build-Warnung:

```text
Some chunks are larger than 500 kB after minification
```

Hauptbundle:

- JS: ca. 3.019 kB minified, 844 kB gzip.

Wahrscheinliche Ursachen:

- Three.js / drei / React Three Fiber.
- Recharts.
- Viele UI-Komponenten.
- Alle Analyse-/3D-/Hardwaremodule im Hauptbundle.

Empfehlung:

- Route-level `React.lazy`:
  - `/analyse`
  - `/workflow`
  - `/import`
  - `/export`
  - `/klient/:id`
- Vendor chunks für three/recharts/supabase/radix.
- 3D-Komponenten erst laden, wenn gebraucht.
- Bundle Analyzer in CI.

## Medizinische UX-/Safety-Lücken

Aktuell fehlen sichtbar/konzeptionell im Code:

- Deutliche medizinische Disclaimer.
- Einwilligungsdialog vor KI-Diagnose.
- Einwilligungsdialog vor Hardware-/Frequenzausgabe.
- Safety-Grenzen je Klient/Gerät/Protokoll.
- Not-Aus als globaler Zustand.
- Therapieprotokoll mit Operator-/Zeit-/Geräte-ID.
- Trennung von Demo/Simulation und echter Behandlung.

Empfehlung:

Vor jeder realen Nutzung:

1. Demo-Modus als Default.
2. Reale Ausgabe nur nach expliziter Aktivierung.
3. Safety Checklist vor Start.
4. Not-Aus immer sichtbar.
5. Keine medizinischen Heilsversprechen.
6. Rechts-/DSGVO-Review.
