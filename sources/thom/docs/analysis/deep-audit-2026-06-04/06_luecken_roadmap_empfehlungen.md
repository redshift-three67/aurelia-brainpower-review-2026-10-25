# 06 Lücken, Problematiken, Echtzeitbewertung, innovative Empfehlungen

## Wichtigste Lücken nach Priorität

## P0 – Sicherheits-/Datenschutzblocker

### 1. Öffentliche Edge Functions mit sensiblen Flows

Befund:

- `verify_jwt = false` für `realtime-sync`, `hardware-metrics`, `meridian-diagnosis`.
- `Access-Control-Allow-Origin: *`.

Auswirkung:

- Externe Clients können Funktionen ohne Auth aufrufen.
- Realtime-Broadcast und KI-Diagnose sind missbrauchsgefährdet.

Empfehlung:

- Für `realtime-sync` und `meridian-diagnosis`: `verify_jwt = true`.
- Origin Whitelist.
- Token/User serverseitig auswerten.
- Rate-Limits und Schema-Validierung.

### 2. Realtime ohne Raum-/Mandantenbindung

Befund:

- Alle WebSocket-Clients teilen eine globale Connection Map.
- Events werden an alle anderen Clients gesendet.

Auswirkung:

- Potenzieller Cross-Client-Datenabfluss.
- Session-/Klientendaten können an falsche Empfänger gehen.

Empfehlung:

- Rooms nach `user_id`, `session_id`, `client_id`.
- Join nur nach DB-Prüfung: Session gehört zu User.
- Keine Broadcasts ohne Room.
- Event ACL pro Eventtyp.

### 3. RLS `user_id IS NULL` Bypass

Befund:

- Authentifizierte Nutzer können Datensätze mit `user_id IS NULL` sehen/teilweise nutzen.

Auswirkung:

- Legacy- oder falsch angelegte Patientendaten können mandantenübergreifend sichtbar sein.

Empfehlung:

- Legacy-Daten migrieren.
- Null-owner-Daten sperren.
- Policies ohne `OR user_id IS NULL`.
- RLS-Testmatrix mit zwei Usern.

### 4. Client-Fotos öffentlich lesbar

Befund:

- Storage Policy zeigt public read für `client-photos`.

Auswirkung:

- Personenfotos im Patientenkontext sind hochsensibel.

Empfehlung:

- Private Bucket.
- Signed URLs, kurze TTL.
- Pfadbindung an `auth.uid()` und `client_id`.

### 5. `.env` im Repository

Befund:

- `.env` ist versioniert.

Empfehlung:

- `.env` aus Git entfernen.
- `.env.example` einführen.
- Supabase publishable key rotieren, wenn extern zugänglich.
- Secret scanning.

## P1 – Stabilitäts-/CI-Blocker

### 1. Lockfile drift

Befund:

- `npm ci` schlägt fehl.
- `tus-js-client` und transitive Dependencies fehlen im Lockfile.

Empfehlung:

- In kontrolliertem Commit `npm install` ausführen.
- Nur einen Paketmanager festlegen: npm oder bun, nicht beides parallel ohne Policy.
- CI zwingend `npm ci`.

### 2. ESLint rot

Befund:

- 95 Probleme, 71 Errors.

Empfehlung:

- Fehlerklassen in Phasen beheben:
  1. `no-case-declarations`, `no-empty`, `no-async-promise-executor`.
  2. `any` durch Domain-Typen ersetzen.
  3. Hook Dependencies prüfen.
  4. UI-shadcn Warnings ggf. konfigurieren oder akzeptierte Baseline.

### 3. Dependency Vulnerabilities

Befund:

- 7 high, 4 moderate produktive Vulnerabilities.

Empfehlung:

- React Router aktualisieren.
- PostCSS aktualisieren.
- Transitive glob/lodash/ws/yaml/minimatch/picomatch über Lockfile/Overrides aktualisieren.
- Audit Gate für high/critical.

### 4. CSS-Syntaxfehler

Befund:

- `.dark @keyframes chreode-pulse` ist ungültig.

Empfehlung:

- Separates `@keyframes chreode-pulse-dark`.
- Theme-spezifische Werte über CSS-Variablen.

## P2 – Architektur-/Skalierungsprobleme

### 1. Zu viele direkte Supabase-Zugriffe im UI

Befund:

- Viele Hooks/Komponenten rufen `.from(...)` direkt auf.

Auswirkung:

- Security-/Error-/Auditlogik verteilt.
- Tests schwieriger.

Empfehlung:

- Repository-/DAO-Schicht pro Domain:
  - `clientsRepository`
  - `sessionsRepository`
  - `resonanceRepository`
  - `hardwareRepository`
- Hooks nutzen Repositories, nicht direkte Tabellen.

### 2. Fachkern nicht ausreichend isoliert/testbar

Befund:

- Feldengine/TCM/Resonanzberechnungen sind vorhanden, aber ohne sichtbare Tests.

Empfehlung:

- `src/domain/feldengine/` als pure TypeScript Module.
- Golden Tests mit bekannten Vektoren.
- Property-based Tests für Frequenz-/Vektorgrenzen.
- Mathematische Dokumentation neben Testcases.

### 3. Realtime/Eventmodell nicht versioniert

Befund:

- Events sind ad hoc JSON.

Empfehlung:

- Eventschema mit Version:

```ts
type EventEnvelope = {
  version: 1;
  eventId: string;
  type: string;
  roomId: string;
  userId: string;
  sessionId?: string;
  timestamp: string;
  payload: unknown;
}
```

- Zod-Validierung client- und serverseitig.
- Sequenznummern/Acks für kritische Frequenz-/Hardwareevents.

### 4. Bundle zu groß

Befund:

- Hauptbundle ca. 3 MB minified / 845 kB gzip.

Empfehlung:

- Route-level code splitting.
- Three.js/3D lazy load.
- Recharts lazy load.
- Supabase nur dort laden, wo Auth/Data nötig.

## Echtzeitfunktionalität – realistische Einschätzung

## Was real vorhanden ist

- Browser-WebSocket Client.
- Supabase Edge Function WebSocket Upgrade.
- Ping/Pong-Latenzmessung.
- Broadcast von Vector/Frequency/Hardware/Session Events.
- WebAudio/AudioWorklet für lokale Audio-Frequenzgenerierung.
- WebSerial-Service für Spooky2-artige Geräte.
- Hardware-Metrik-WebSocket mit 500ms Updateintervall.

## Was noch nicht real belastbar ist

- Keine echte GPU-beschleunigte Frequenzberechnung im Code nachweisbar.
- Hardware-Metriken sind simuliert.
- Keine echte Serverhardware-Abfrage.
- Keine Multi-Client-Sicherheitsisolation.
- Keine garantierte Latenz/SLO.
- Keine Jitter-/Dropout-/Reconnect-Tests.
- Keine Hardware-in-the-loop Tests.
- Keine Frequenzoutput-Safety-Zertifizierung.

## Realtime-Reifegrad

| Ebene | Bewertung |
|---|---|
| Demo-Realtime UI | gut begonnen |
| Lokale Audio-Realtime | technisch plausibel |
| Server-Realtime | Demo-fähig, nicht sicher |
| Multi-User Realtime | nicht produktionsreif |
| Hardware-Realtime | Prototypisch |
| Medizinisch belastbare Realtime | nicht erreicht |

## Zielarchitektur für sichere Realtime

1. Authenticated WebSocket Gateway
   - JWT required.
   - Origin check.
   - Room join only after DB authorization.

2. Typed Event Bus
   - Zod schemas.
   - Event versions.
   - Size limits.
   - Rate limits.

3. Session-Isolated Realtime
   - Room pro treatment session.
   - Nur behandelnder User/zugelassene Geräte.
   - Server validates `session_id` ownership.

4. Hardware Control Plane
   - Reale Geräte nicht direkt durch beliebige UI-Events steuern.
   - Command queue.
   - Safety interlock.
   - Not-Aus.
   - Dry-run/simulation.

5. Monitoring
   - p50/p95/p99 latency.
   - reconnect count.
   - dropped events.
   - audio underruns.
   - device errors.

## Innovative Empfehlungen

## 1. Safety-first Treatment Orchestrator

Ein zentraler Orchestrator steuert jede Behandlung als explizite State Machine:

```text
DRAFT → REVIEWED → CONSENT_CONFIRMED → DEVICE_READY → RUNNING → PAUSED/STOPPED → COMPLETED → ARCHIVED
```

Eigenschaften:

- Keine Frequenzausgabe außerhalb `RUNNING`.
- Jede Transition validiert.
- Not-Aus von überall.
- Session Audit Trail.

## 2. Dualer Modus: Simulation vs. reale Behandlung

RadiThoms sollte global zwischen Modi unterscheiden:

1. Demo/Simulation
   - synthetische Hardwaredaten.
   - keine echten Patientendaten.
   - keine echte Hardwareausgabe.

2. Clinical/Real Mode
   - Auth required.
   - Consent required.
   - echte Geräteprofile.
   - strikte Auditierung.
   - Safety Gates.

UI muss den Modus dauerhaft sichtbar zeigen.

## 3. Privacy-Preserving AI Diagnosis

Vor KI-Gateway-Aufruf:

- Keine Namen/Geburtsdaten senden.
- Vektoren normalisieren und pseudonymisieren.
- Prompt-Kontext minimieren.
- Nutzer-/Klienten-Einwilligung prüfen.
- KI-Ausgabe mit Disclaimer und Review-Step versehen.

Optional:

- Lokales LLM für sensible Voranalyse.
- Externer KI-Aufruf nur für nicht-identifizierende Zusammenfassung.

## 4. Fachliche Validierungsbibliothek

Eine testbare `radi-thoms-domain` Bibliothek:

- Vektormodell.
- Bifurkationsdetektion.
- Meridian-Mapping.
- Frequenzvorschläge.
- Contraindications/Safety Rules.

Jede Regel mit:

- Quelle/Evidenzgrad.
- Testcases.
- Grenzen/Disclaimer.

## 5. Realtime Digital Twin

Vor realem Hardwarestart läuft jede Sequenz in einem digitalen Zwilling:

- erwartete Frequenzkurve.
- Amplitudenverlauf.
- Dauer.
- Gerätekompatibilität.
- Maximalwerte.
- Not-Aus-Test.

Erst nach erfolgreichem Simulation Check darf echte Hardware aktiviert werden.

## 6. Device Adapter Layer

Statt Spooky2 direkt aus UI/Hook zu nutzen:

```text
UI → Treatment Orchestrator → Device Adapter Interface → Spooky2Adapter/WebAudioAdapter/MockAdapter
```

Vorteile:

- Tests mit MockAdapter.
- Einheitliche Safety Checks.
- Austauschbare Geräte.
- Auditierbare Commands.

## 7. Evidence & Claim Management

Da das Projekt therapeutische Begriffe nutzt, sollte jeder Claim klassifiziert werden:

- Mathematisches Modell.
- Traditionelle TCM-Annahme.
- Experimentelle Hypothese.
- Klinisch validierte Aussage.
- Nicht validierte/konzeptuelle Aussage.

UI und Reports sollten diese Einstufung sichtbar machen.

## 8. Datenräume und Rollen

Einführen von Rollen:

- Practitioner/Admin.
- Assistant/Reader.
- Client/Patient optional.
- Device Agent.

Datenräume:

- Private Practitioner Workspace.
- Client-specific workspace.
- Public reference data.
- Simulation sandbox.

## 9. Report-Pipeline mit Redaction

Session Reports sollten vor Export:

- PII klassifizieren.
- Redaction Preview anbieten.
- Exportzweck wählen: intern, Klient, Arzt, anonymisiert.
- Metadaten/Prompt/KI-Anteile markieren.

## 10. Hardware Evidence Recorder

Für reale Sessions:

- Tatsächlich gesendete Kommandos.
- Geräteantworten.
- Start/Stop-Zeitpunkte.
- Fehler/Timeouts.
- Operator-Bestätigungen.
- Nicht die vollständigen sensiblen Patientendaten in Logs.

## Empfohlene Umsetzungs-Roadmap

### Phase 0: Freeze & Hygiene

- Keine neuen Features.
- `.env` entfernen, `.env.example`.
- Lockfile synchronisieren.
- README ersetzen.
- CI mit `npm ci`, build, tsc, lint, audit.

### Phase 1: Security Hotfix

- Edge JWT aktivieren.
- CORS einschränken.
- RLS `user_id IS NULL` entfernen.
- Client photos privat.
- Realtime Rooms.

### Phase 2: Quality Baseline

- ESLint Fehler beheben.
- CSS Keyframes fixen.
- Dependency Vulnerabilities beheben.
- Route-level code splitting.

### Phase 3: Domain Tests

- Feldengine Unit Tests.
- Meridian/Frequenz Mapping Tests.
- RLS Tests mit zwei Usern.
- Edge Function schema tests.

### Phase 4: Safe Realtime & Hardware

- Treatment Orchestrator.
- Device Adapter Layer.
- Mock Device + Hardware Simulator.
- Not-Aus.
- Latenz-/Jitter-/Reconnect-Tests.

### Phase 5: DSGVO/Legal/Medical Review

- Datenschutzkonzept.
- Consent Flows.
- KI-Auftrags-/Providerprüfung.
- Medizinische Disclaimer.
- Rollen-/Berechtigungskonzept.

### Phase 6: Controlled Pilot

- Nur Testdaten oder rechtlich freigegebene Pilotdaten.
- Monitoring.
- Audit Logs.
- Rollback-/Incident-Prozess.

## Konkrete nächste technische Tickets

1. `package-lock.json` synchronisieren und `npm ci` grün machen.
2. `react-router-dom`, `postcss` und transitive Vulnerabilities aktualisieren.
3. `.env` aus Git entfernen, `.env.example` schreiben.
4. `supabase/config.toml`: `verify_jwt=true` für `realtime-sync` und `meridian-diagnosis`.
5. Edge Functions: Origin/JWT/User prüfen.
6. `realtime-sync`: Rooms und Zod Event Validation.
7. RLS Migration: `OR user_id IS NULL` entfernen.
8. Storage Policies: `client-photos` private.
9. `src/index.css`: `.dark @keyframes` korrigieren.
10. ESLint: `no-case-declarations`, leere Catch-Blöcke, `any`-Hotspots.
11. `README.md` durch echte RadiThoms-Dokumentation ersetzen.
12. `SystemMonitorService`/Hardware-Metrics UI als Simulation kennzeichnen.
13. Globaler Not-Aus und Demo/Real-Modus.
14. Authentifizierter Browser-E2E-Test für `/analyse`.
15. RLS Regression Tests.

## Schlussbewertung

RadiThoms hat ein starkes Fundament als Forschungs-/Prototypplattform: moderne UI, Supabase-Integration, Fachmodule, Realtime-Ansätze, Audio-/Hardwareintegration und umfangreiche Dokumentation. Die größte Gefahr liegt nicht im fehlenden Featureumfang, sondern in der Diskrepanz zwischen ambitionierter therapeutischer Echtzeit-/Hardware-Vision und aktueller Sicherheits-/Validierungsreife.

Wenn zuerst Sicherheit, Datenisolation, CI-Qualität, reale Messbarkeit und medizinisch-rechtliche Leitplanken nachgezogen werden, kann daraus ein deutlich belastbareres Modul entstehen. Ohne diese Härtung sollte das System nur mit Demo-/Testdaten und ohne echte Therapie-/Patientenentscheidungen verwendet werden.
