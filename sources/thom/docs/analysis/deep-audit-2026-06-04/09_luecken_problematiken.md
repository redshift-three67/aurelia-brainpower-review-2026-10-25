# 09 Lücken und Problematiken in RadiThoms

Stand: 2026-06-04
Repository: `/opt/radithoms`
Analysebezug: `radiquant/morpho-field-nexus`, Commit `64b9a38`

## Zweck

Dieses Dokument listet die wesentlichen Lücken und Problematiken aus der Tiefenanalyse in priorisierter Form. Es dient als Risiko- und Backlog-Grundlage.

## Kritikalitätsskala

- Kritisch: blockiert Echtdaten, Produktivbetrieb oder reale Therapie-/Hardware-Nutzung.
- Hoch: muss vor Pilot-/Deployment-Reife behoben werden.
- Mittel: relevant für Wartbarkeit, UX, Performance oder Skalierung.
- Niedrig: Verbesserung, Dokumentations-/Qualitätsdetail.

## Kritische Lücken

## 1. Edge Functions ohne JWT-Verifikation

### Befund

`supabase/config.toml` setzt:

```toml
[functions.realtime-sync]
verify_jwt = false

[functions.hardware-metrics]
verify_jwt = false

[functions.meridian-diagnosis]
verify_jwt = false
```

### Risiko

- anonyme Aufrufe möglich.
- KI-Gateway kann missbraucht werden.
- Realtime-/Session-/Frequenzdaten können unkontrolliert fließen.

### Kritikalität

Kritisch.

### Empfehlung

- `verify_jwt = true` für `realtime-sync` und `meridian-diagnosis`.
- `hardware-metrics` nur geschützt oder klar als öffentliche Simulation mit Rate Limit.

## 2. Wildcard CORS

### Befund

Edge Functions setzen:

```ts
'Access-Control-Allow-Origin': '*'
```

### Risiko

- beliebige Webseiten können Browser-Requests gegen die Functions auslösen.
- bei deaktiviertem JWT besonders gefährlich.

### Kritikalität

Kritisch.

### Empfehlung

- erlaubte Origins explizit konfigurieren.
- Origin beim WebSocket Upgrade prüfen.

## 3. Realtime-Broadcast ohne Mandanten-/Session-Isolation

### Befund

`realtime-sync` nutzt eine globale Connection Map und broadcastet Events an alle anderen Clients.

### Risiko

- Cross-User-Datenabfluss.
- Frequenz-/Session-/Hardwareevents können an falsche Clients gehen.
- nicht DSGVO-/Patientendaten-tauglich.

### Kritikalität

Kritisch.

### Empfehlung

- Rooms pro User/Session.
- Join nur nach DB-Autorisierung.
- Event ACLs.
- Zod Event-Schemas.

## 4. RLS mit `user_id IS NULL`

### Befund

Spätere Migrationen erlauben teilweise:

```sql
user_id = auth.uid() OR user_id IS NULL
```

### Risiko

- Legacy-/Null-owner-Daten können von allen authentifizierten Nutzern gesehen werden.
- Patientendatenisolation ist nicht garantiert.

### Kritikalität

Kritisch.

### Empfehlung

- Null-owner-Daten migrieren oder sperren.
- Policy-Ausnahme entfernen.
- RLS-Zwei-User-Tests.

## 5. Client-Fotos öffentlich lesbar

### Befund

Storage-Policy für `client-photos` enthält public read.

### Risiko

- Personenfotos sind hochsensible personenbezogene Daten.
- öffentlicher Zugriff ist für Patientenkontext nicht akzeptabel.

### Kritikalität

Kritisch.

### Empfehlung

- Bucket privat machen.
- signed URLs mit kurzer TTL.
- Pfadbindung an User/Client.

## 6. Versionierte `.env`

### Befund

`.env` ist in Git getrackt.

### Risiko

- Konfiguration exponiert.
- in Kombination mit offenen Edge Functions/RLS erhöhtes Risiko.

### Kritikalität

Hoch bis kritisch, abhängig von Exposure.

### Empfehlung

- `.env` aus Git entfernen.
- `.env.example` einführen.
- Keys bei Bedarf rotieren.

## Hohe Lücken

## 7. `npm ci` ist gebrochen

### Befund

`npm ci` schlägt fehl, weil `package.json` und `package-lock.json` nicht synchron sind.

### Risiko

- CI/CD nicht reproduzierbar.
- Deployments können lokal anders laufen als in CI.

### Kritikalität

Hoch.

### Empfehlung

- Lockfile synchronisieren.
- Paketmanager festlegen.
- CI mit `npm ci` erzwingen.

## 8. Lint-Gate rot

### Befund

`npm run lint` meldet:

- 95 Probleme.
- 71 Errors.
- 24 Warnings.

### Risiko

- technische Schulden.
- potenzielle Hook-/Realtime-/State-Bugs.
- schwächeres Vertrauen in Refactoring.

### Kritikalität

Hoch.

### Empfehlung

- Fehlerklassen phasenweise beheben.
- `any` in Domain-/Realtime-/Edge-Flows durch Typen ersetzen.
- Hook Warnings ernsthaft prüfen.

## 9. Produktive Dependency Vulnerabilities

### Befund

`npm audit --omit=dev` meldet:

- 11 Vulnerabilities.
- 7 high.
- 4 moderate.

### Risiko

- XSS/Open Redirect über React Router-Familie.
- PostCSS XSS Advisory.
- lodash Prototype Pollution / Code Injection Advisory.
- glob/minimatch/picomatch ReDoS/Injection-Klassen.

### Kritikalität

Hoch.

### Empfehlung

- kontrollierte Updates.
- Audit Gate high/critical.

## 10. KI-Diagnose ohne Consent-/PII-Gate

### Befund

`meridian-diagnosis` sendet ClientVector/Imbalances an externen Lovable AI Gateway.

### Risiko

- Gesundheitsdaten verlassen das System ohne sichtbare Einwilligungs-/Minimierungslogik.
- medizinisch/rechtlich problematisch.

### Kritikalität

Hoch.

### Empfehlung

- Consent vor KI-Aufruf.
- PII-Minimierung.
- medizinischer Disclaimer.
- Provider-/DSGVO-Prüfung.

## 11. Reale Hardware-Safety fehlt

### Befund

WebAudio/WebSerial/Spooky2-Flows sind vorhanden, aber ohne zentrale Safety-Schicht.

### Risiko

- reale Frequenzausgabe ohne ausreichende Freigabe.
- Fehlbedienung.
- nicht auditierbare Gerätekommandos.

### Kritikalität

Hoch.

### Empfehlung

- Not-Aus.
- Treatment Orchestrator.
- Device Adapter Layer.
- Dry-run und MockAdapter.
- Audit Trail.

## Mittlere Lücken

## 12. Hardware-/GPU-/Servermetriken sind simuliert

### Befund

`SystemMonitorService` und `hardware-metrics` generieren synthetische Werte.

### Risiko

- falscher Eindruck realer Hardware-/Realtime-Fähigkeit.
- Entscheidungen auf Basis simulierter Werte.

### Kritikalität

Mittel bis hoch, falls als real dargestellt.

### Empfehlung

- Simulation klar kennzeichnen.
- echten Metrics-Agent nur geschützt einführen.

## 13. Bundle sehr groß

### Befund

Produktivbuild erzeugt Hauptbundle ca. 3 MB minified / 845 kB gzip.

### Risiko

- langsamer initialer Load.
- schlechte UX auf schwächeren Geräten.

### Kritikalität

Mittel.

### Empfehlung

- Route-level Lazy Loading.
- 3D/Recharts getrennt laden.
- Bundle Analyzer.

## 14. CSS-Syntaxfehler

### Befund

Build warnt bei:

```css
.dark @keyframes chreode-pulse
```

### Risiko

- Dark-Mode-Animation fehlerhaft.
- CSS-Minifier ignoriert oder bricht Teile.

### Kritikalität

Mittel.

### Empfehlung

- eigenes `@keyframes chreode-pulse-dark` definieren.
- CSS-Variablen statt Selektor-verschachteltem Keyframe.

## 15. README ist Lovable-Template

### Befund

README beschreibt noch generisch Lovable und enthält Platzhalter.

### Risiko

- Projektstatus unklar.
- Onboarding schwer.
- Dokumentationsdrift.

### Kritikalität

Mittel.

### Empfehlung

- echte RadiThoms README erstellen:
  - Zweck.
  - Stack.
  - Setup.
  - Env.
  - Scripts.
  - Sicherheitsstatus.
  - Demo-vs-Real-Hinweis.

## 16. Direkte Supabase-Zugriffe verteilt in Hooks/Komponenten

### Befund

Viele Hooks greifen direkt auf Supabase Tabellen zu.

### Risiko

- Error-/Security-/Audit-Patterns sind verteilt.
- schwerer zu testen.

### Kritikalität

Mittel.

### Empfehlung

- Repository-/Service-Schicht pro Domain.
- Hooks nutzen Repositories.

## 17. Fachkern nicht ausreichend getestet

### Befund

Thom-/Feldengine-/Meridian-/Frequenzberechnungen sind nicht sichtbar mit Unit Tests abgesichert.

### Risiko

- fachliche Regressionen unentdeckt.
- medizinisch/therapeutische Interpretationen schwer prüfbar.

### Kritikalität

Mittel bis hoch.

### Empfehlung

- pure Domain-Module.
- Golden Tests.
- Property-based Tests.
- Evidenz-/Claim-Dokumentation.

## 18. WebSerial Response Matching zu grob

### Befund

Spooky2-Service ordnet Antworten offenbar dem ersten wartenden Callback zu.

### Risiko

- parallele Kommandos können falsch zugeordnet werden.
- Gerätefehler schwer nachvollziehbar.

### Kritikalität

Mittel bis hoch bei realer Hardware.

### Empfehlung

- Command Queue.
- Sequenznummern.
- Timeout pro Command.
- Geräte-State-Machine.

## 19. Authentifizierter E2E-Flow nicht verifiziert

### Befund

Ohne Testaccount wurde nur unauthentifizierter Browser-Smoke-Test durchgeführt.

### Risiko

- Analyseflow kann nach Login Fehler enthalten.
- Supabase-/Realtime-/Storage-Flows nicht end-to-end geprüft.

### Kritikalität

Mittel.

### Empfehlung

- Testuser/Testprojekt.
- Playwright-Smoke für Login, Client-Erstellung, Analyse-Demo, Export.

## 20. Medizinische Disclaimer und Claim-Grenzen fehlen

### Befund

Therapeutische und energetische Begriffe werden genutzt, aber klare rechtliche/medizinische Grenzen sind nicht ausreichend sichtbar.

### Risiko

- Nutzer können System als klinisch validierte Diagnose verstehen.
- Haftungs-/Compliance-Risiko.

### Kritikalität

Hoch bei realer Nutzung, mittel im Demo-Kontext.

### Empfehlung

- Disclaimer.
- Claim-Klassifizierung.
- Review durch Fach-/Rechtsberatung.

## Zusammenfassende Risiko-Matrix

| Bereich | Risiko | Kritikalität |
|---|---|---|
| Edge Auth | öffentlich/anonym | Kritisch |
| Realtime | globaler Broadcast | Kritisch |
| RLS | Null-owner Bypass | Kritisch |
| Storage | öffentliche Client-Fotos | Kritisch |
| Secrets | `.env` getrackt | Hoch/Kritisch |
| CI | `npm ci` rot | Hoch |
| Lint | 71 Errors | Hoch |
| Dependencies | 7 High Findings | Hoch |
| KI | kein Consent/PII-Gate | Hoch |
| Hardware | keine Safety-Schicht | Hoch |
| Performance | großes Bundle | Mittel |
| CSS | ungültiger Keyframe | Mittel |
| Doku | README drift | Mittel |
| Tests | keine Auth/HW E2E | Mittel |

## Nicht mit Echtdaten nutzen, bis mindestens behoben

Vor echten Klienten-/Patientendaten müssen mindestens folgende Punkte erledigt sein:

1. Edge JWT/CORS.
2. Realtime Rooms.
3. RLS ohne Null-owner-Bypass.
4. private Client-Fotos.
5. `.env` entfernt und Secrets geprüft.
6. KI-Consent und PII-Minimierung.
7. Demo-/Real-Modus.
8. Not-Aus und Hardware-Safety.
9. `npm ci`, build, typecheck, lint/audit Baseline.
10. DSGVO-/Legal-Review.
