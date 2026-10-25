# 08 Empfehlungen für RadiThoms

Stand: 2026-06-04
Repository: `/opt/radithoms`
Analysebezug: `radiquant/morpho-field-nexus`, Commit `64b9a38`

## Leitprinzipien

RadiThoms sollte nicht primär als weiteres Feature-Projekt behandelt werden, sondern als sicherheitskritische Plattform mit sensiblen Daten, Realtime-Kommunikation, KI-Auswertung und potenzieller Hardware-/Frequenzausgabe.

Empfohlene Leitprinzipien:

1. Safety first.
2. Datenschutz by design.
3. Demo und reale Behandlung strikt trennen.
4. Realtime nur authentifiziert und session-isoliert.
5. Jede Hardwareausgabe auditierbar machen.
6. KI-Ausgaben als Assistenz kennzeichnen, nicht als medizinische Diagnose.
7. Erst CI/Build/Lint/Security stabilisieren, dann neue Features.

## Top-10 Empfehlungen

## 1. Demo-/Real-Modus als globale Systementscheidung

### Empfehlung

RadiThoms sollte global sichtbar zwischen zwei Modi unterscheiden:

- Demo/Simulation
- Real/Clinical Mode

### Warum

Aktuell gibt es simulierte Hardware-/GPU-/Serverdaten, während UI und Dokumentation teils produktionsnahe Echtzeit-/Hardwarefunktionalität suggerieren. Das kann fachlich und rechtlich problematisch werden.

### Umsetzung

- globaler App-State `runtimeMode`.
- Demo-Modus als Default.
- Real-Modus nur nach Admin-/Legal-/Safety-Freigabe.
- UI-Badge dauerhaft sichtbar.
- echte Hardware-/KI-/Patientendaten-Flows im Demo-Modus blockieren.

## 2. Treatment Orchestrator als State Machine

### Empfehlung

Jede Behandlung/Harmonisierung sollte durch einen zentralen Orchestrator laufen.

### Vorgeschlagene Zustände

```text
DRAFT → REVIEWED → CONSENT_CONFIRMED → DEVICE_READY → RUNNING → PAUSED/STOPPED → COMPLETED → ARCHIVED
```

### Vorteile

- keine unkontrollierte Frequenzausgabe.
- klare Safety-Gates.
- auditierbarer Ablauf.
- UI, Realtime und Hardware folgen demselben Zustandsmodell.

## 3. Realtime sicher neu schneiden

### Empfehlung

Den bisherigen globalen WebSocket-Broadcast durch authentifizierte Rooms ersetzen.

### Zielmodell

- User-Room für private Events.
- Session-Room für Behandlungssitzung.
- Device-Room für autorisierte Hardware-Agenten.
- kein Broadcast ohne Raum.
- Join nur nach DB-Autorisierung.

### Technische Mindestbausteine

- JWT Pflicht.
- Origin Check.
- Zod Event Schemas.
- Event-Versionierung.
- Rate-Limits.
- p95/p99 Latenzmessung.

## 4. Device Adapter Layer einführen

### Empfehlung

Hardware nicht direkt aus UI-/Hook-Logik steuern, sondern über Adapter.

### Zielstruktur

```text
UI
  → Treatment Orchestrator
    → Device Safety Layer
      → Device Adapter Interface
        → WebAudioAdapter
        → Spooky2Adapter
        → MockAdapter
        → FutureDeviceAdapter
```

### Vorteile

- Mock-Tests ohne Geräte.
- Dry-run möglich.
- einheitlicher Not-Aus.
- zentrale Frequenz-/Amplitude-/Dauergrenzen.
- bessere Auditierbarkeit.

## 5. Datenschutz- und Consent-Gates vor KI

### Empfehlung

Die KI-/Meridian-Diagnose darf nicht anonym/offen und nicht ohne explizite Einwilligung laufen.

### Umsetzung

- `verify_jwt = true`.
- Consent-Dialog vor externem KI-Aufruf.
- PII-Minimierung:
  - keine Namen.
  - keine Geburtsdaten.
  - keine Fotos.
  - keine freien Notizen ungeprüft.
- Prompt-/Response-Logging deaktivieren oder pseudonymisieren.
- KI-Ergebnis immer als Assistenz kennzeichnen.

## 6. Domain-Kern fachlich testbar machen

### Empfehlung

Feldengine-, Thom-, Meridian-, Frequenz- und Resonanzberechnungen sollten als pure TypeScript-Domainbibliothek extrahiert werden.

### Warum

Diese Logik ist der fachliche Kern des Projekts. Ohne Tests bleibt unklar, ob Änderungen unbemerkt therapeutisch relevante Berechnungen verändern.

### Umsetzung

- `src/domain/feldengine/`
- `src/domain/meridians/`
- `src/domain/frequency/`
- Unit Tests.
- Golden Tests.
- Property-based Grenzwerttests.
- fachliche Quellen/Evidenzgrad neben Regeln dokumentieren.

## 7. RLS und Storage als eigene Test-Suite behandeln

### Empfehlung

RLS darf nicht nur per SQL-Review geprüft werden, sondern braucht echte Zwei-User-Tests.

### Testszenario

1. User A legt Client A an.
2. User B legt Client B an.
3. User A versucht Client B zu lesen.
4. User B versucht Client A zu ändern.
5. Null-owner-Daten werden geprüft.
6. Foto-Storage wird geprüft.

### Akzeptanz

- Cross-User-Zugriff immer abgelehnt.
- Fotos nicht öffentlich abrufbar.
- Null-owner-Daten nicht allgemein sichtbar.

## 8. Build-/Dependency-/Lint-Gates automatisieren

### Empfehlung

Vor jeder fachlichen Weiterentwicklung muss die technische Baseline grün werden.

### CI-Gates

```bash
npm ci
npx tsc --noEmit
npm run build
npm run lint
npm audit --omit=dev --audit-level=high
```

### Warum

Aktuell sind `npm ci`, `npm run lint` und `npm audit` rot. Das reduziert Vertrauen in Deployments und erschwert Lovable/GitHub-Synchronisation.

## 9. Performance durch Lazy Loading verbessern

### Empfehlung

Große Module wie 3D/Anatomie/Recharts/Analyse sollten nicht im Hauptbundle landen.

### Umsetzung

- `React.lazy` für Routen:
  - `/analyse`
  - `/workflow`
  - `/import`
  - `/export`
  - `/klient/:id`
- separate Vendor Chunks:
  - three/drei/fiber
  - recharts
  - supabase
  - radix/ui
- GLB-Modelle progressiv laden.

## 10. Medizinische Claims klassifizieren

### Empfehlung

Alle fachlichen Aussagen sollten nach Evidenz-/Aussagetyp markiert werden.

### Kategorien

- mathematisches Modell.
- traditionelle TCM-Annahme.
- experimentelle Hypothese.
- konzeptuelle energetische Interpretation.
- klinisch validierte Aussage.
- nicht validierte Aussage.

### Nutzen

- reduziert rechtliches Risiko.
- macht Grenzen transparent.
- stärkt Seriosität des Systems.

## Konkrete technische Startempfehlungen

### Sofort umsetzbar

1. `package-lock.json` synchronisieren.
2. `.env` aus Git entfernen.
3. `.env.example` erstellen.
4. CSS-Fehler `.dark @keyframes` beheben.
5. `react-router-dom`/`postcss`/transitive Vulnerabilities aktualisieren.
6. `verify_jwt = true` für sensible Functions.
7. CORS Whitelist einführen.
8. `user_id IS NULL` RLS-Bypass entfernen.
9. Client-Fotos privat machen.
10. README durch echte RadiThoms-Dokumentation ersetzen.

### Danach

1. Realtime Rooms.
2. Event Schemas.
3. RLS-Test-Suite.
4. Domain-Tests.
5. Device Adapter Layer.
6. Treatment Orchestrator.
7. Demo-/Real-Modus.
8. KI-Consent-Flow.

## Empfehlung zur Arbeitsweise

Für dieses Repository empfehle ich ein vorsichtiges, phasenbasiertes Vorgehen:

1. Vor jeder Phase lokale Sicherheitskopie erstellen.
2. Pro Phase nur wenige, klar überprüfbare Änderungen.
3. Nach jeder Phase lokal testen.
4. Erst nach lokaler Verifikation committen.
5. GitHub/Lovable-Push erst nach ausdrücklicher Freigabe.
6. Keine echten Patientendaten für Tests verwenden.
7. Security-/DSGVO-Themen nicht nebenbei mit Featurearbeit vermischen.

## Empfehlung zur Port-Nutzung bei lokaler Entwicklung

Für Vite ist der Default-Port `5173`.

Empfohlener Standard für RadiThoms:

1. Vor Start Port prüfen:

```bash
ss -ltnp | grep ':5173 ' || true
```

2. Wenn frei:

```bash
npm run dev -- --host 127.0.0.1 --port 5173 --strictPort
```

3. Wenn belegt, bewusst Alternativport wählen, z.B. `5174`, und vorher prüfen:

```bash
ss -ltnp | grep ':5174 ' || true
npm run dev -- --host 127.0.0.1 --port 5174 --strictPort
```

4. Port in der Antwort ausdrücklich nennen.

Wichtig:

- `--strictPort` ist sinnvoll, weil Vite sonst automatisch auf einen anderen Port ausweichen kann.
- Bei dieser Analyse war Port `8080` durch nginx belegt; deshalb war `8080` ungeeignet.
