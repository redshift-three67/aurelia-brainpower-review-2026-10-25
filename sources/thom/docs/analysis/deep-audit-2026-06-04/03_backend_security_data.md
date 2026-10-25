# 03 Backend, Security, Daten, Datenschutz

## Backend-Architektur

Das Backend besteht aus Supabase:

- Supabase Auth für Login/Registrierung.
- Supabase Postgres mit Migrationen unter `supabase/migrations/`.
- Row Level Security (RLS) in Migrationen.
- Supabase Storage Buckets für Fotos und 3D-Modelle.
- Supabase Realtime Publication für `clients`, `client_vectors`, `harmonization_protocols`.
- Edge Functions unter `supabase/functions/`:
  - `realtime-sync`
  - `hardware-metrics`
  - `meridian-diagnosis`

Es gibt kein separates FastAPI/Node-Backend im Repository.

## Supabase-Konfiguration

`supabase/config.toml`:

```toml
project_id = "yoryyvfuscyfumeseour"

[functions.realtime-sync]
verify_jwt = false

[functions.hardware-metrics]
verify_jwt = false

[functions.meridian-diagnosis]
verify_jwt = false
```

Bewertung:

- `verify_jwt = false` ist für reine Demo denkbar, für RadiThoms mit Klienten-/Gesundheitsdaten aber kritisch.
- Mindestens `meridian-diagnosis` und `realtime-sync` müssen JWT-verifiziert werden.
- Für `hardware-metrics` kann ein public read-only Modus denkbar sein, aber auch dort Rate-Limit und CORS einschränken.

## CORS

Alle Edge Functions setzen aktuell:

```ts
'Access-Control-Allow-Origin': '*'
```

Risiko:

- Beliebige Webseiten können Browser der Nutzer veranlassen, diese Funktionen aufzurufen.
- Bei `verify_jwt=false` braucht ein Angreifer nicht einmal eine gültige Session.
- Bei `meridian-diagnosis` kann das Kosten-/Missbrauchsrisiko für den Lovable AI Gateway Key erhöhen.
- Bei WebSocket-Funktionen kann Cross-Origin-Realtime-Abgriff/Broadcast-Missbrauch entstehen.

Empfehlung:

- In Produktion erlaubte Origins explizit konfigurieren:
  - lokale Dev-Origin separat.
  - Lovable-/Produktionsdomain separat.
- `Authorization`-Header prüfen.
- Bei WebSocket Upgrade Origin prüfen.

## Edge Function: `realtime-sync`

### Implementierte Funktionalität

- WebSocket Upgrade.
- Globale `connections = new Map<string, WebSocket>()`.
- Anonyme `clientId` pro Verbindung.
- Events:
  - `ping` → `pong`
  - `vector_update`
  - `frequency_sync`
  - `hardware_status`
  - `session_event`
- Broadcast an alle anderen offenen Sockets.

### Hauptprobleme

1. Keine Authentifizierung
   - Kein JWT, keine Supabase User-ID.

2. Keine Autorisierung
   - Keine Prüfung, ob der Client Zugriff auf `sessionId`, `clientId`, `vectorId` oder Geräte hat.

3. Keine Mandanten-/Raumtrennung
   - Alle Clients teilen denselben globalen Broadcast-Kanal.

4. Keine Schema-Validierung
   - `JSON.parse` plus `switch`, aber keine Zod/Valibot/Supabase-Typprüfung.

5. Keine Rate Limits
   - Ein Client kann viele Events senden.

6. Sensitive Logs
   - Es wird zwar nicht der gesamte Payload geloggt, aber IDs/Eventnamen können bei Patientendaten bereits relevant sein.

7. Keine Persistenz-/Replay-Kontrolle
   - Events gehen live verloren, es gibt keine geordnete Event-ID, ACK-Semantik ist minimal.

### Kritische Datenschutzbewertung

Für Vektor-, Frequenz-, Hardware- und Session-Events ist diese Funktion in aktueller Form nicht DSGVO-/Patientendaten-tauglich. Sie ist ein Demo-Eventbus, kein sicherer klinischer/therapeutischer Realtime-Kanal.

### Mindesthärtung

1. `verify_jwt = true`.
2. JWT aus Upgrade Request auswerten.
3. `user_id = auth.uid()` / Supabase Auth Context serverseitig ableiten.
4. Realtime Rooms einführen:
   - `room = user_id` für private Events.
   - `room = session_id`, aber nur wenn Session dem User gehört.
5. Alle Events per Zod validieren.
6. Eventgrößen begrenzen.
7. Rate-Limit pro User/IP/Session.
8. Keine Health-/Sessionpayloads an fremde Clients.
9. Audit-Logs nur pseudonymisiert.

## Edge Function: `hardware-metrics`

### Implementierte Funktionalität

- REST `/metrics` und `/config`.
- WebSocket Streaming alle 500ms.
- Simulierte CPU/GPU/RAM/Netzwerkdaten.
- `set_interval` durch Client steuerbar, geklemmt auf 100ms bis 5000ms.

### Probleme

1. Keine echten Servermetriken
   - Werte sind synthetisch.
   - UI/Docs können fälschlich reale RTX/Ryzen-Messung suggerieren.

2. Öffentliche Funktion
   - `verify_jwt=false`, wildcard CORS.

3. Kein Rate-Limit / Connection-Limit
   - Viele Clients können Streams starten.

4. Keine echte Hardwarebindung
   - Keine nvidia-smi/rocm-smi/OS-Metriken.
   - Keine GPU-Job-Metriken.

### Empfehlung

- Für Demo klar als Simulation labeln.
- Für Produktion echten Metrics-Agent separat betreiben:
  - Node/Deno/Go/Python Agent auf Hardwarehost.
  - nvidia-smi/DCGM, psutil, WebSocket/SSE mit Auth.
  - Signierte Metrikframes und Healthchecks.
- Public Endpoint nur grobe Statusdaten, keine internen Hardwaredetails.

## Edge Function: `meridian-diagnosis`

### Implementierte Funktionalität

- Nimmt `clientVector` und `imbalances` entgegen.
- Erzeugt deutschen TCM-/Energiemedizin-Prompt.
- Ruft Lovable AI Gateway mit `LOVABLE_API_KEY` auf.
- Streamt Antwort zurück.

### Kritische Risiken

1. Keine JWT-Verifikation laut Supabase Config.
2. Wildcard CORS.
3. Kein Consent-/Legal-Gate.
4. Keine PII-Reduktion oder Datenklassifizierung.
5. Kein Prompt-Injection-/Output-Safety-Filter.
6. Medizinische Empfehlungen ohne Disclaimer/Verantwortlichkeitsgrenzen.
7. Kein Rate-Limit/Kostenlimit außer Gateway-Fehlerbehandlung.
8. Keine Validierung der Eingabewerte; Wertebereiche können manipuliert werden.

### Datenschutzbewertung

Auch wenn der Body laut Interface primär Vektor-/Imbalance-Daten enthält, sind dies Gesundheits-/Therapiekontextdaten. Der Transfer an einen externen KI-Gateway braucht:

- Rechtsgrundlage/Einwilligung.
- AV-Vertrag/Providerprüfung.
- Datenminimierung.
- Transparenzhinweis.
- Lösch-/Retentionkonzept.
- Technische Zugriffskontrollen.

Bis das geklärt ist, sollte diese Funktion nur in Demo-/Testmodus mit nicht-realen Daten laufen.

## Datenmodell und Patientendaten

### `clients`

Enthält:

- Vorname, Nachname.
- Geburtsdatum.
- Geburtsort.
- Foto-URL.
- field_signature.
- Notizen.

Bewertung:

- Dies sind eindeutig personenbezogene und in Kombination mit Therapie-/Gesundheitsdaten besonders schützenswerte Daten.
- `field_signature` könnte biometrisch/energetisch interpretiert werden und sollte wie sensitives Pseudonym behandelt werden.

### `client_vectors`

Enthält:

- physisch/emotional/mental/energy/stress Dimensionen.
- primary_concern.
- notes.
- HRV/GSR/Sensorwerte.
- sensor_data JSONB.
- session_id/input_method.

Bewertung:

- Gesundheits-/Biometrie-/Anamnesedaten.
- Hohe Schutzklasse.

### `treatment_sessions`

Enthält Snapshots und Behandlungsergebnisse.

Bewertung:

- Gesundheitsdaten plus Behandlungsdokumentation.
- Muss mandantenisoliert, revisionssicher und export-/löschbar sein.

### `resonance_results`, `harmonization_protocols`, `harmonization_jobs`

Enthalten Ergebnis-/Therapie-/Frequenzdaten.

Bewertung:

- Therapiebezogene Gesundheitsdaten.

## RLS-Analyse

### Historische Public Policies

Initiale Migration `20251230230951...`:

```sql
CREATE POLICY "Allow all operations on clients" ON public.clients FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all operations on client_vectors" ON public.client_vectors FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all operations on harmonization_protocols" ON public.harmonization_protocols FOR ALL USING (true) WITH CHECK (true);
```

Spätere Migration `20260304172431...` droppt diese Policies und ersetzt sie durch Auth-Policies. Das ist positiv.

### Problematische Null-owner-Policies

Migration `20260306231210...` setzt u.a.:

```sql
USING (user_id = auth.uid() OR user_id IS NULL)
```

Für `clients`, abgeleitete `client_vectors`, `harmonization_protocols`, `harmonization_jobs`.

Risiko:

- Alle authentifizierten Nutzer können Legacy-Datensätze mit `user_id IS NULL` sehen oder teilweise bearbeiten.
- Wenn alte Patientendaten ohne `user_id` existieren, sind diese nicht mandantenisoliert.

Empfehlung:

1. Einmalige Migration, die Legacy-Daten sauber einem Owner zuweist oder sperrt.
2. `OR user_id IS NULL` entfernen.
3. Temporäre Admin-Migrationsfunktion statt dauerhafter Policy-Ausnahme.
4. Test-Suite für RLS mit mindestens zwei Nutzern.

### Public Read Tabellen

Mehrere Tabellen sind öffentlich lesbar, z.B.:

- `word_energies`
- `anatomy_resonance_points`
- `organ_scan_points`
- `organ_schemas`
- `organ_landmarks`
- `anatomy_models`
- Storage `3d-models` public read

Bewertung:

- Für reine Referenzdaten vertretbar.
- Muss strikt von patienten-/sessionspezifischen Daten getrennt bleiben.
- Bei user-generierten Modellen/Metadaten ist public read kritisch.

## Storage-Sicherheit

Erkannte Storage-Policies:

- `client-photos`: public read, authenticated upload/update/delete.
- `3d-models`: public read, authenticated upload.

Risiken:

1. Client-Fotos sind personenbezogene Daten; public read ist in realem Patientenkontext nicht akzeptabel.
2. Authenticated upload ohne Owner-/Path-Bindung kann Cross-User-Overwrite oder unerwünschte Inhalte ermöglichen.
3. Für GLB Uploads fehlen Content-Type-, Größe-, Malware-/Parser-Schutz und Lizenzprüfung.

Empfehlung:

- Client-Fotos privat, signed URLs mit kurzer TTL.
- Storage-Pfade nach User/Client partitionieren.
- RLS/Storage Policies an `auth.uid()` binden.
- Upload-Limits und MIME-/Magic-Byte-Prüfung.
- GLB-Dateien serverseitig prüfen oder isoliert rendern.

## Secrets / Environment

Befund:

- `.env` ist versioniert.
- Enthaltene Keys laut sicherer Namensprüfung:
  - `VITE_SUPABASE_PROJECT_ID`
  - `VITE_SUPABASE_PUBLISHABLE_KEY`
  - `VITE_SUPABASE_URL`

Bewertung:

- Publishable Supabase Key ist kein Service-Role-Secret, aber sollte dennoch nicht als Live-Konfig im Repo gepflegt werden.
- Das Risiko entsteht aus Kombination mit offenen Edge Functions/RLS/Storage.

Empfehlung:

1. `.env` aus Git entfernen.
2. `.env.example` mit Platzhaltern einführen.
3. Supabase anon/publishable Key rotieren, wenn Repo länger extern zugänglich war.
4. Service Role Keys niemals ins Frontend oder Repo.
5. CI Secret Scanning aktivieren.

## Frontend Auth / Session Storage

`src/integrations/supabase/client.ts`:

```ts
auth: {
  storage: localStorage,
  persistSession: true,
  autoRefreshToken: true,
}
```

Bewertung:

- Supabase SPA-Standard, aber localStorage ist XSS-anfällig.
- Bei Gesundheitsdaten sollte XSS-Härtung besonders streng sein.

Empfehlung:

- Strikte Content Security Policy.
- Keine unsicheren HTML-Injections.
- Dependency-Sicherheitsupdates.
- Session-Lifetime prüfen.
- Optional: serverseitige Session-/BFF-Architektur für produktive Patientendaten erwägen.

## XSS-/Injection-Oberflächen

Gefunden:

- `dangerouslySetInnerHTML` in `src/components/ui/chart.tsx`; vermutlich shadcn-Style-Injection aus kontrolliertem Theme-Objekt.
- Viele Benutzer-/Patientenfelder werden gerendert, aber React escaped standardmäßig.
- Externe KI-Antworten/Reports müssen geprüft werden: wenn Markdown/HTML später gerendert wird, XSS-Risiko.

Empfehlung:

- Keine KI-Ausgaben als HTML rendern ohne Sanitizer.
- DOMPurify nur falls zwingend HTML nötig.
- CSP einführen.
- Rich Text für medizinische Reports bewusst absichern.

## Dependency Security

`npm audit --omit=dev --json` meldete:

- 11 Vulnerabilities gesamt.
- 7 high.
- 4 moderate.

Wichtige direkte/indirekte Pakete:

- `react-router-dom` / `react-router` / `@remix-run/router`: Open Redirect/XSS-Klassen.
- `postcss`: XSS via CSS stringify.
- `lodash`: Prototype Pollution / Code Injection advisory.
- `glob`, `minimatch`, `picomatch`: ReDoS/Command-Injection/Glob-Probleme.
- `ws`: Uninitialized memory disclosure.
- `yaml`: Stack overflow via nested collections.

Empfehlung:

- `npm audit fix` prüfen, aber nicht blind in Produktion.
- React Router mindestens auf gefixte 6.x-Version oder aktuelle Major-Version heben.
- PostCSS aktualisieren.
- Lockfile konsolidieren.
- CI Audit Gate definieren: high/critical fail.

## DSGVO-/Patientendaten-Bewertung

RadiThoms verarbeitet dem Modell nach:

- Identitätsdaten.
- Geburtsdaten/-orte.
- Fotos.
- Gesundheits-/Therapie-/Sessiondaten.
- Sensor-/HRV-/GSR-Daten.
- KI-generierte Behandlungsempfehlungen.

Damit sind hohe Anforderungen relevant:

1. Rechtsgrundlage und Einwilligung.
2. Zweckbindung und Datenminimierung.
3. Transparenz/Datenschutzhinweise.
4. Zugriffskontrollen und Mandantentrennung.
5. Löschung/Export/Auskunft.
6. Auditierung ohne sensible Payloads.
7. Verschlüsselung at rest/in transit.
8. Providerprüfung für Supabase/Lovable/AI-Gateway.
9. Medizinische Verantwortung/Haftung/Disclaimer.
10. Keine Echtdaten in Demo, Logs, Screenshots, Testdaten.

## Sicherheits-Prioritäten

P0 – Sofort vor Echtdaten:

1. `verify_jwt=true` für sensible Edge Functions.
2. CORS einschränken.
3. Realtime Rooms + Auth + Rate-Limits.
4. `user_id IS NULL` RLS-Ausnahmen entfernen.
5. Client-Fotos private Storage.
6. `.env` aus Git entfernen und Keys rotieren.

P1 – Vor produktivem Pilot:

1. Dependency Updates.
2. Lint/CI grün.
3. RLS Tests mit zwei Usern.
4. KI-Diagnose Consent und PII-Minimierung.
5. Audit-/Logging-Policy.
6. Legal/DSGVO Review.

P2 – Für robuste Skalierung:

1. Backend-for-Frontend oder sichere Edge-Service-Schicht.
2. Event-Sourcing für Sessions.
3. Realtime-SLO-Monitoring.
4. Hardware Safety Controller.
