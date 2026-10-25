# 07 Notwendige Phasen für RadiThoms

Stand: 2026-06-04
Repository: `/opt/radithoms`
Analysebezug: `radiquant/morpho-field-nexus`, Commit `64b9a38`

## Ziel dieses Dokuments

Dieses Dokument verdichtet die Tiefenanalyse in eine phase-gated Umsetzungslogik. Die Phasen sind bewusst sicherheits- und stabilitätsorientiert, weil RadiThoms Klienten-/Gesundheits-/Therapie-/Hardware-/KI-Flows berührt.

Grundsatz:

- Erst stabilisieren und absichern.
- Dann fachliche Flows testen.
- Danach reale Hardware/KI/Realtime kontrolliert aktivieren.
- Keine Echtdaten in unsicheren oder unklaren Flows.

## Phase 0 – Freeze, Sicherheitskopie, Baseline

### Ziel

Einen stabilen, reproduzierbaren Ausgangspunkt schaffen, bevor Codeänderungen erfolgen.

### Schritte

1. Lokale Sicherheitskopie des aktuellen Repository-Zustands erstellen.
2. Git-Status dokumentieren.
3. aktuellen Commit dokumentieren.
4. vorhandene Analyseberichte sichern.
5. keine Feature-Arbeit parallel beginnen.
6. README/Statusdokumente gegen reale Tool-Ausgaben abgleichen.

### Akzeptanzkriterien

- Sicherheitskopie existiert außerhalb des Projektordners.
- `git status` ist bekannt und dokumentiert.
- Commit/Branch/Remote sind dokumentiert.
- Bericht `docs/analysis/deep-audit-2026-06-04/` bleibt erhalten.

## Phase 1 – Paket-/Build-/CI-Baseline reparieren

### Ziel

Das Projekt muss reproduzierbar installierbar, baubar und prüfbar werden.

### Befunde aus Audit

- `npm ci` schlägt fehl.
- `package.json` und `package-lock.json` sind nicht synchron.
- `npm run build` ist grün.
- `npx tsc --noEmit` ist grün.
- `npm run lint` ist rot.
- `npm audit --omit=dev` ist rot.

### Schritte

1. Paketmanager-Strategie festlegen: npm als primärer Standard, sofern nicht anders entschieden.
2. `package-lock.json` kontrolliert synchronisieren.
3. `npm ci` grün machen.
4. `npm run build` erneut ausführen.
5. `npx tsc --noEmit` erneut ausführen.
6. Lint-Fehler in Hotspot-Klassen beheben:
   - `no-case-declarations`
   - `no-empty`
   - `no-explicit-any`
   - React Hook Dependency Warnings prüfen.
7. Dependency-Audit aktualisieren und High-Severity-Probleme beheben.
8. CI-Gate definieren:
   - install
   - typecheck
   - build
   - lint
   - audit high/critical fail.

### Akzeptanzkriterien

- `npm ci` exit 0.
- `npm run build` exit 0.
- `npx tsc --noEmit` exit 0.
- `npm run lint` exit 0 oder bewusst dokumentierte Baseline ohne kritische Fehler.
- keine High/Critical produktiven npm Audit Findings.

## Phase 2 – Secret-/Env-/Repo-Hygiene

### Ziel

Keine Live-Konfiguration und keine unnötigen Zugriffsinformationen im Repository.

### Befunde aus Audit

- `.env` ist versioniert.
- Supabase Publishable Key/URL/Project ID liegen im Repo.

### Schritte

1. `.env` aus Git entfernen.
2. `.env.example` mit Platzhaltern erstellen.
3. `.gitignore` prüfen/ergänzen.
4. Supabase Publishable/Anon Key rotieren, falls Repo breiter exponiert war.
5. Secret Scanning aktivieren.
6. Keine Service Role Keys im Frontend oder Repo.

### Akzeptanzkriterien

- `.env` ist nicht mehr getrackt.
- `.env.example` dokumentiert benötigte Variablen ohne echte Werte.
- Secret Scan ohne kritische Treffer.

## Phase 3 – Supabase Auth, RLS und Storage härten

### Ziel

Klienten-/Patientendaten dürfen nur dem jeweils berechtigten Nutzer zugänglich sein.

### Befunde aus Audit

- Historische Public Policies wurden teilweise ersetzt.
- Weiterhin problematisch: `user_id = auth.uid() OR user_id IS NULL`.
- Client-Fotos sind öffentlich lesbar.

### Schritte

1. Legacy-Daten mit `user_id IS NULL` identifizieren.
2. Daten einem Owner zuweisen oder in Quarantäne verschieben.
3. RLS-Policies ohne `OR user_id IS NULL` schreiben.
4. RLS-Testmatrix mit mindestens zwei Usern erstellen.
5. `client-photos` Bucket privat machen.
6. signed URLs mit kurzer TTL nutzen.
7. Storage-Pfade an `auth.uid()` und `client_id` binden.
8. öffentliche Referenzdaten klar von Patientendaten trennen.

### Akzeptanzkriterien

- Nutzer A kann keine Daten von Nutzer B lesen/schreiben.
- Null-owner-Daten sind nicht allgemein sichtbar.
- Client-Fotos sind nicht public read.
- RLS-Regressionstests existieren.

## Phase 4 – Edge Functions und CORS absichern

### Ziel

Sensible Edge Functions dürfen nicht öffentlich und anonym aufrufbar sein.

### Befunde aus Audit

- `verify_jwt = false` für:
  - `realtime-sync`
  - `hardware-metrics`
  - `meridian-diagnosis`
- CORS wildcard `*`.

### Schritte

1. `verify_jwt = true` für `realtime-sync` und `meridian-diagnosis`.
2. bei `hardware-metrics` entscheiden: public simulation oder protected real metrics.
3. erlaubte Origins explizit konfigurieren.
4. JWT/User serverseitig prüfen.
5. Eingaben mit Zod/Schema validieren.
6. Rate-Limit pro User/IP/Session einführen.
7. keine sensitiven Payloads loggen.
8. KI-Gateway nur nach Consent und PII-Minimierung aufrufen.

### Akzeptanzkriterien

- anonyme Requests auf sensible Functions werden abgelehnt.
- fremde Origins werden abgelehnt.
- Rate-Limits greifen.
- KI-Diagnose ist nur für authentifizierte, berechtigte Nutzer möglich.

## Phase 5 – Realtime-Räume und Event-Sicherheit

### Ziel

Realtime darf nicht global broadcasten, sondern muss session-/nutzergebunden sein.

### Befunde aus Audit

- `realtime-sync` nutzt globale Connection Map.
- Events werden an alle anderen verbundenen Clients broadcastet.
- keine Räume, keine Mandantenbindung, keine Event-Schemas.

### Schritte

1. Event Envelope definieren:
   - `eventId`
   - `version`
   - `type`
   - `userId`
   - `sessionId`
   - `roomId`
   - `timestamp`
   - `payload`
2. Rooms pro User/Session einführen.
3. Join nur nach DB-Autorisierung.
4. Eventtypen mit Zod validieren.
5. Sequenznummern/Acks für kritische Events.
6. p50/p95/p99 Latenz messen.
7. dropped/replayed/reconnected Events erfassen.

### Akzeptanzkriterien

- kein Cross-User-Broadcast möglich.
- falsche Session-ID wird abgelehnt.
- Eventschemas verhindern beliebige Payloads.
- Latenzmetriken sind sichtbar und testbar.

## Phase 6 – Hardware-/Frequenz-Safety

### Ziel

Reale Audio-/Spooky2-/WebSerial-/WebUSB-Ausgabe nur kontrolliert, auditierbar und sicher starten.

### Befunde aus Audit

- WebAudio und WebSerial sind technisch vorhanden.
- Safety-/Consent-/Not-Aus-/Audit-Schichten fehlen.
- System-/Hardwaremetriken sind simuliert.

### Schritte

1. globalen Demo-/Real-Modus einführen.
2. reale Ausgabe standardmäßig deaktivieren.
3. Not-Aus zentral implementieren.
4. Treatment Orchestrator als State Machine:
   - DRAFT
   - REVIEWED
   - CONSENT_CONFIRMED
   - DEVICE_READY
   - RUNNING
   - PAUSED/STOPPED
   - COMPLETED
   - ARCHIVED
5. Device Adapter Layer einführen:
   - MockAdapter
   - WebAudioAdapter
   - Spooky2Adapter
6. Frequenz-/Amplitude-/Dauergrenzen je Gerät validieren.
7. Hardware Simulator und Dry-Run Modus.
8. tatsächliche Commands auditieren.

### Akzeptanzkriterien

- keine reale Ausgabe ohne Consent und Safety Check.
- Not-Aus stoppt alle aktiven Outputs.
- jede reale Ausgabe ist auditierbar.
- Mock-/Dry-Run Tests laufen ohne physische Geräte.

## Phase 7 – KI-/Diagnose-/DSGVO-Gates

### Ziel

KI- und Diagnosefunktionen dürfen keine unkontrollierten Patientendaten an externe Dienste senden.

### Befunde aus Audit

- `meridian-diagnosis` sendet Vektor-/Imbalance-Daten an Lovable AI Gateway.
- Consent, PII-Minimierung und rechtlicher Hinweis fehlen.

### Schritte

1. KI-Consent vor jedem externen Aufruf.
2. PII aus Prompt entfernen.
3. Prompt- und Antwort-Schema validieren.
4. medizinischen Disclaimer ergänzen.
5. KI-Ausgaben als Assistenz, nicht Diagnose, kennzeichnen.
6. Provider-/AV-/Retentionprüfung durchführen.
7. Testmodus mit synthetischen Daten beibehalten.

### Akzeptanzkriterien

- kein KI-Aufruf ohne Consent.
- keine Namen/Geburtsdaten/Fotos im KI-Prompt.
- Nutzer sieht klare Grenzen der KI-Ausgabe.

## Phase 8 – Fachkern-Tests und wissenschaftliche Transparenz

### Ziel

Feldengine-, Meridian-, Frequenz- und Bifurkationslogik nachvollziehbar und testbar machen.

### Schritte

1. Domain-Kern isolieren.
2. Unit Tests für Vektoren/Bifurkationen/Frequenzmapping.
3. Golden Testcases mit bekannten Eingaben.
4. Claim-Klassifizierung:
   - mathematisches Modell
   - traditionelle Annahme
   - Hypothese
   - validierte klinische Aussage
   - nicht validierter Konzeptanteil
5. Reports mit Evidenz-/Grenzenhinweisen versehen.

### Akzeptanzkriterien

- Domain-Funktionen sind ohne UI testbar.
- zentrale Berechnungen haben Tests.
- UI/Reports unterscheiden Modell/Hypothese/medizinische Evidenz.

## Phase 9 – Kontrollierter Pilot

### Ziel

Erst nach technischer, rechtlicher und fachlicher Härtung kontrolliert testen.

### Schritte

1. nur Testdaten oder rechtlich freigegebene Pilotdaten.
2. definierte Nutzerrollen.
3. Monitoring und Incident-Prozess.
4. Export-/Lösch-/Auskunftsfähigkeit testen.
5. Hardware nur mit freigegebenem Safety-Protokoll.

### Akzeptanzkriterien

- Datenschutzfreigabe liegt vor.
- technische Gates sind grün.
- Pilotumfang ist begrenzt und rückholbar.
