# AURELIA – Empfohlene K1-Fortsetzungsplanung

> Für ausführende LLMs: Nach ausdrücklicher Übernahme dieses Vorschlags paketweise arbeiten. Falls im Ausführungssystem vorhanden, `superpowers:executing-plans` verwenden; die projektbezogene Zwei-Spuren-Qualitätsstrategie hat bei Reviewumfang Vorrang. Checkboxen bezeichnen zukünftige Schritte, keine bereits erteilte Freigabe.

**Ziel:** Den vorhandenen K1-Stand ohne Wiederholung erledigter Arbeiten zu einer nachvollziehbaren lokalen Abnahme führen und externe Freigaben sauber getrennt halten.

**Architektur:** Bestehenden Kanon, Scanner, Portal und Toolchain erhalten. Operativen Fortschritt, Prüfergebnis, Evidenzaktualität und Berechtigungen getrennt führen. Die korrigierten Verträge ergänzen ALT nur nach dokumentierter Übernahme.

**Technik:** Vorhandenes Node-22-/TypeScript-/React-/TanStack-/Vite-Projekt, Node Test Runner, Git und bestehende Browserprüfungen. Keine neue Plattform oder Bibliothek erforderlich.

**Status:** `proposed_for_discussion`; keine Implementation in diesem Dokumentationsauftrag. Dateien und Befehle beziehen sich auf K1 gemäß README. Dieses Dokument spezifiziert Arbeitspakete und Abnahmeverträge; es behauptet keine bereits ausführbare, vollständig implementierte Patchserie. Für kritische Vertragsänderungen wird vor Code der begrenzte Paketvertrag finalisiert.

## 0. Ausführungsgrenzen

- Vorhandene uncommittierte Änderungen erhalten. Kein Reset, Checkout zum Verwerfen, Clean oder stilles Überschreiben.
- Keine Publikation, kein Push/PR, keine Historienänderung, keine Serveraktion und keine Produktionsmigration aus diesem Plan ableiten.
- Bestehende Freigaben paketbezogen prüfen. Dokumentationsfreigabe dieses Gesprächs gilt nur für den neuen Ordner.
- Tests können temporäre Dateien schreiben; Dev-Server können synthetische Schemaoperationen ausführen. Das ist kein strikt lesender Betrieb. Vor Ausführung muss genau dieser lokale synthetische Scope bereits autorisiert sein.
- `npm run build` bleibt ausgeschlossen: Das aktuelle Script ruft anschließend `db:migrate` auf. `build:dev` umgeht diese npm-Verkettung, beweist aber allein keine insgesamt nebenwirkungsfreie Ausführung.
- Keine Produktions-Credentials in Prüfprozesse übernehmen; Werte niemals ausgeben. Vor Start den effektiven Backendpfad prüfen, nicht nur den Scriptnamen.
- Historische Quellen und Publikationsgrenzen bleiben erhalten. Keine Credentialrotation oder Entfernung historischer Objekte nebenbei.
- Aktuelle Runtime/Abhängigkeiten dokumentieren; hier geprüfte Node-Version ist `v22.22.0`. Ein später abweichendes System erfordert eine passende Neubewertung der davon abhängigen Evidenz.

## 1. Reihenfolge und Zuständigkeiten

```text
E0 Bestandsaufnahme
  -> E1 Status- und Vertragskorrektur
  -> E2 vorhandenen Runner abschließen
  -> E3 Testverträge
  -> E4 Vite-Portabilität
  -> E5 kontrollierte Auth-Konfigurationsprüfung
  -> E6 Browser-Smoke und Routenprüfung
  -> E7 Assetgate und Lint abschließen
  -> E8 lokale Gesamtabnahme
```

Die reine Asset-/Abhängigkeitsinventur gehört bereits zu E0. Externe Bereitstellung darf parallel geklärt werden; keine konkurrierenden Änderungen an `package.json`. Servervorbereitung ist ein separates Programm und kein impliziter Nebeneffekt dieser Kette.

| Rolle | Verantwortung |
|---|---|
| Primärer Entwickler / Agent | Scope, Umsetzung, frische Nachweise, Konsolidierung |
| Betreiber | Entscheidungen zu Paketübernahme, Publikation und Server-/Destruktionsgrenzen |
| Spec-Reviewer bei Spur B | Freigegebenen Vertrag gegen relevanten Diff und Evidenz prüfen |
| Quality-/Securityreviewer bei Spur B | Erst nach Spec-PASS Fehlerfälle, Sicherheit und Wartbarkeit gegenprüfen |
| Plattformanbieter | Autoritative verwaltete Assets bereitstellen, soweit erforderlich |

## 2. Einheitliches Status- und Evidenzmodell

**Empfehlung für E1:** `docs/project-control/K1-CURRENT.json` als neue operative Quelle. Historisches `K1-STATUS.md` bleibt als Nachweis erhalten und verweist auf den aktuellen Stand. Der vorhandene Produktkanon `src/lib/concept/canon.ts` bleibt eine andere Quelle mit anderer Zuständigkeit.

Das folgende Beispiel enthält bewusst keinen erfundenen Testerfolg:

```json
{
  "schema_version": 1,
  "workstream": "K1",
  "task_id": "T07",
  "branch": "codex/aurelia-konsolidierung",
  "observed_head": "1185a68ed984b525686764f995513355701929e3",
  "dirty_paths": [
    "package.json",
    "scripts/test-runner.mjs",
    "scripts/test-runner.test.mjs"
  ],
  "implementation": "in_progress",
  "verification": {
    "result": "not_run",
    "freshness": "unknown",
    "evidence_ref": null
  },
  "server_gate_ref": "docs/project-control/ground-zero/GATE-STATUS.md",
  "authorization": {
    "implementation_ref": null,
    "commit_ref": null,
    "publication_ref": null
  }
}
```

| Dimension | Zulässige Werte / Regel |
|---|---|
| `implementation` | `planned`, `in_progress`, `implemented` |
| `verification.result` | `not_run`, `passed`, `failed`, `indeterminate`, `not_applicable` |
| `verification.freshness` | `current`, `stale`, `unknown` |
| Freigabegate | Separat `not_requested`, `blocked`, `approved`; mit Entscheidungsreferenz, keine Ableitung aus Testerfolg |
| `not_applicable` | Nur mit konkreter Begründung; nicht für fehlende Tools oder fehlende Evidenz |
| `passed` | Nur mit passendem Prüfbeleg für den untersuchten Snapshot |
| `current` | Quellstand und relevante Konfiguration stimmen mit dem Prüfbeleg überein |
| `null` bei Freigabereferenz | Keine Freigabe aus diesem Datensatz ableitbar; kein Beweis, dass nie eine externe Freigabe existierte |

Eine Gate-Referenz darf den Serverstatus nicht eigenständig überschreiben. Ungültige oder fehlende Felder führen zu `indeterminate` beziehungsweise Validatorfehler, niemals zu implizitem PASS.

Je Prüflauf mindestens erfassen: Zeitpunkt mit UTC-Offset, relative Arbeitsbasis, Git-HEAD, Hashmanifest relevanter Dirty-Dateien, Befehl, Exitcode, Testanzahl sofern vom Runner geliefert, Konfigurationsfingerabdruck ohne Geheimnisse, Ergebnis und Blockergrund. Keine selbstreferenziellen Commit-/Dateihashes verlangen. Konfiguration mit Secrets niemals als Klartext oder durch einzeln erratbare Secret-Hashes protokollieren.

## E0 – Wiederaufnahmebasis sichern

**ALT-Bezug:** Einstieg, Tasks 1–7 und frühe Task-12-Inventur. **Risiko:** lesende Inventur; keine Codeänderung.

**Lesen:** `AGENTS.project.md`, `docs/project-control/K1-STATUS.md`, `docs/project-control/QUALITY-ROUTING.md`, ALT, `package.json`, beide Runner-Dateien, `docs/project-control/ground-zero/GATE-STATUS.md`.

- [ ] Branch, HEAD und Dirty-Dateien frisch erfassen:

```powershell
git branch --show-current
git rev-parse HEAD
git status --short
git diff -- package.json
```

- [ ] Vorfahr prüfen:

```powershell
git merge-base --is-ancestor 8706186af01e10e4253e25abb31bf3577110dae4 HEAD
if ($LASTEXITCODE -ne 0) { throw 'K1_BASE_MISMATCH' }
```

- [ ] Bei Abweichung zum Review-Snapshot den neuen Diff bewerten. Nicht auf `1185a68` zurücksetzen.
- [ ] Tasks 5/6 über Commitinhalt zuordnen; Task 7 als vorhandene Arbeit erfassen. Freigaben getrennt prüfen.
- [ ] Benötigte Plattformassets anhand ALT Task 12 lesend inventarisieren; fehlende Lieferquelle als Abhängigkeit vermerken.

**Abnahme:** Ein aktueller Fortsetzungspunkt mit vollständigem Dirty-Inventar. Fehlende Abhängigkeiten sind sichtbar. Kein Code und keine Serverdaten verändert.

## E1 – Operative Statusführung und Planverträge korrigieren

**ALT-Bezug:** Tasks 1/4/5/6/14; R01–R04. **Risiko:** Statusdarstellung zunächst Spur A; Validator-/Gatevertrag nach bestehender Regel Spur B.

**Vorgeschlagene Dateien:** neu `docs/project-control/K1-CURRENT.json`; anpassen `docs/project-control/README.md`, `docs/project-control/K1-STATUS.md`, `scripts/check-project-control-k1.mjs`, `scripts/check-project-control-k1.test.mjs`. ALT nur nach Übernahmefreigabe mit eindeutig datierter Ergänzung ändern.

- [ ] Statusschema aus Abschnitt 2 paketbezogen freigeben; historische und aktuelle Felder eindeutig abgrenzen.
- [ ] Aktuellen Task-Stand eintragen, ohne historische Snapshots umzuschreiben.
- [ ] R02 schriftlich korrigieren: Task 10 verwendet nur `spawnImpl`/`fetchImpl`. R04 auf Task 14/E8 verweisen.
- [ ] Für den Validator Negativtests festlegen: `passed` ohne Evidenz; fehlende Pflichtfelder; unbekannter Ergebniswert; Gatefreigabe aus bloßem Testerfolg; unerkannte Dirty-Datei bei einer behaupteten Gesamtabnahme. Alle müssen fehlschlagen.
- [ ] HTML zunächst deutlich mit Erstellungszeit und geprüftem Commit kennzeichnen. Änderung der alten HTML-Datei nur in einem später dafür freigegebenen Scope; diese Dokumentationsfreigabe reicht dafür nicht.
- [ ] Prüfen:

```powershell
node --test scripts/check-project-control-k1.test.mjs
node scripts/check-project-control-k1.mjs
```

**Erwartung:** Tests und reale Kontrolle Exit 0; dargestellter aktueller Zustand entspricht E0. Ein funktionierender Checker darf auch einen noch nicht abgenommenen Task 7 korrekt darstellen.

**Abnahme:** Entwickler und LLM gelangen aus README zum selben Fortsetzungspunkt. Historische Fakten, aktuelle Beobachtung und Freigabe sind getrennt.

## E2 – Vorhandenen Test-Runner abschließen

**ALT-Bezug:** Task 7. **Dateien:** `scripts/test-runner.mjs`, `scripts/test-runner.test.mjs`, `package.json`. **Risiko:** Mindestens Vertragsprüfung; bei fail-closed-Gateänderung Spur B.

- [ ] Bestehende Implementierung gegen ALT lesen; keine Neuanlage über vorhandene Dateien.
- [ ] Pflichtgruppen bestätigen: MJS-Tests unter `scripts`, die beiden benannten TypeScript-Tests. Zukünftige zusätzliche TS-Dateien nicht stillschweigend als abgedeckt ausgeben.
- [ ] Fehlerfälle prüfen: fehlende Pflichtdatei, leere Gruppe, I/O-Fehler, Prozessstartfehler, Signalabbruch, Symlink-/Junction-Grenzen. Keine Shellausführung.
- [ ] Ein absichtlich fehlschlagender synthetischer Test muss bis zum Runner-Exit durchschlagen; beide Gruppen müssen nachweislich ausgeführt werden.
- [ ] Ausführen, sofern lokale Fixture-Schreibrechte im Paket erteilt sind:

```powershell
node --test scripts/test-runner.test.mjs
npm test
```

**Erwartung:** Runner-Vertragstests Exit 0. Die Gesamtsuite darf in diesem Zwischenpaket durch bekannte Legacy-Verträge rot sein; die Fehler werden E3 zugeordnet. Das ist kein grünes Gesamtergebnis. Testanzahlen frisch erfassen, nicht aus alten Protokollen übernehmen.

**Abnahme:** Discovery und Fehlerweitergabe funktionieren; keine Pflichtgruppe unbemerkt leer; uncommittierte Änderungen vollständig erklärt. Commit nur bei entsprechender Paketfreigabe.

## E3 – Testverträge auf Auth-on und synthetische Fixtures ausrichten

**ALT-Bezug:** Task 8. **Dateien:** `scripts/with-app-env.test.mjs`, `scripts/check-auth-invariant.test.mjs`, `scripts/migration-plan.test.mjs`, `scripts/grok-pwa-plugin.test.mjs`; neuer Helfer `scripts/test-support/symlink-capability.mjs`. **Risiko:** Spur B für Auth-/Migrationsvertrag.

- [ ] Erwartung festhalten: fehlender App-Override schaltet Auth nicht aus; Root-Migrationsdiscovery enthält Auth und Tenants. Discoverytest führt keine Migration aus.
- [ ] PWA-Fixtures von realen Plattformassets trennen. Ein grüner Fixturetest macht das reale Assetgate nicht grün.
- [ ] Nur dokumentierte Windows-Capability-Fehler wie `EPERM`/`EACCES` als Skip zulassen; fehlerhafte Pfade oder andere Fehler bleiben FAIL.
- [ ] Gegenbeispiele zuerst nachweisen und minimal korrigieren, ohne Produktanforderungen abzuschwächen.
- [ ] Prüfen:

```powershell
node --test scripts/with-app-env.test.mjs scripts/check-auth-invariant.test.mjs scripts/migration-plan.test.mjs scripts/grok-pwa-plugin.test.mjs
npm test
```

**Abnahme:** Fokussierte Tests und komplette Suite grün, zulässige Capability-Skips einzeln begründet. Ein Skip ist kein Plattformnachweis für die übersprungene Eigenschaft.

## E4 – Vite-Aufruf und sichere lokale Prüfumgebung

**ALT-Bezug:** Task 9. **Dateien:** `scripts/with-app-env.mjs`, `scripts/with-app-env.test.mjs`; keine spontane Änderung an `vite.config.ts` oder Buildskripten. **Risiko:** Toolchain; Environment-/Migrationsgrenze kritisch behandeln.

- [ ] Vorhandenen `resolveInvocation`-Vertrag aus ALT umsetzen: installierten JS-CLI-Pfad über Paketmetadaten auflösen, `process.execPath` verwenden, `shell: false`.
- [ ] Argumente mit Leerzeichen und Fehler bei fehlender CLI testen; Env-Priorität und Signalweitergabe erhalten.
- [ ] Vor realem Start die erlaubte Prozessumgebung und den synthetischen Backendpfad bestimmen. Kein dump aller Umgebungsvariablen.
- [ ] Prüfen:

```powershell
node --test scripts/with-app-env.test.mjs
npm run build:dev
```

**Abnahme:** Passende Tests und Entwicklungsmodus-Build Exit 0. Windows-Nachweis und Linux-Nachweis getrennt erfassen; nicht verfügbares Zielsystem bedeutet ausstehender Nachweis, kein fiktives PASS.

## E5 – Auth-Konfigurationsprüfung an eigene Instanz binden

**ALT-Bezug:** Task 10; R02/R05/R06. **Risiko:** Spur B; korrigierten Vertrag vor Implementierung freigeben.

**Dateien:** neu `scripts/check-auth-with-dev-server.mjs`, `scripts/check-auth-with-dev-server.test.mjs`; anpassen `package.json`. Eine eventuelle Erweiterung von `scripts/app-env-plugin.mjs` und dessen Tests benötigt ausdrücklich den unten beschriebenen begrenzten Scope.

**Einheitliche Optionsnamen:**

```typescript
type CheckOptions = {
  spawnImpl?: typeof import('node:child_process').spawn;
  fetchImpl?: typeof fetch;
  timeoutMs?: number;
  port?: number;
};
```

Keine alternative `spawn`-/`fetch`-Option. Unbekannte Optionsnamen sollen im Testvertrag sichtbar abgelehnt werden, statt stillschweigend reale Standardabhängigkeiten zu verwenden.

- [ ] Negativtests festschreiben: bereits belegter Port, sofortiger Child-Exit, fremde Readiness-Antwort, Timeout, Spawnfehler, manueller Abbruch, fehlgeschlagene Bereinigung.
- [ ] Eindeutige Instanzzuordnung festlegen. **Empfohlene Designoption:** kurzlebiger zufälliger Prüf-Identifier nur im Environment des gestarteten lokalen Dev-Prozesses; Rückgabe ausschließlich über den Dev-Prüfendpunkt. Der Wert ist kein Auth-Secret, keine Berechtigung und kein dauerhafter Projektidentifier. Kein Produktionsendpunkt und keine protokollierten Credentials. Diese Option ist eine neue Vertragsentscheidung, nicht vorhandene Implementierung.
- [ ] Vorzeitigen Prozess-Exit gegen Polling auswerten; Antwort ohne passende Instanzidentität darf keinen Erfolg auslösen. Portprüfung allein reicht wegen Start-Rennen nicht.
- [ ] Nach jedem Ausgang den eigenen Prozessbaum beenden und Beendigung abwarten. Fremde Prozesse niemals beenden. Plattformmethode vor Implementierung bestimmen und Windows/Linux getrennt testen.
- [ ] Env-Konfigurationsvergleich mit bestehender `compareAuthInvariant`-API durchführen. Das Ergebnis ausdrücklich als Konfigurationsvergleich benennen.
- [ ] Prüfen:

```powershell
node --test scripts/check-auth-with-dev-server.test.mjs
npm run check:auth
```

**Abnahme:** Exit 0 nur bei passender eigener Instanz, Auth-on-Konfiguration und erfolgreichem Cleanup. Jeder Fehlerfall liefert Nichtnull. Kein laufender fremder Server kann einen scheinbaren Erfolg erzeugen. Keine Behauptung einer bereits geprüften Mandantenisolation.

## E6 – Browser-Smoke und Portalprüfung

**ALT-Bezug:** Tasks 6/11, Vorbereitung Task 14. **Dateien:** `scripts/browser-smoke.mjs`, `scripts/browser-smoke-verdict.mjs`, `scripts/browser-smoke-verdict.test.mjs`; Screenshots im vorgesehenen lokalen Nachweisverzeichnis. **Risiko:** Pfadvertrag / Browser-Nebenwirkungen explizit beachten.

- [ ] Ausgabe- und Baselinepfade an den tatsächlichen Worktree binden; Traversal-/Symlink-/fremde Zielpfade negativ prüfen. Keine starre Linux-Workspaceannahme unter Windows.
- [ ] Browserprüfungen nur mit zugelassenem Browserwerkzeug durchführen. Eine Browser-Sicherheitsablehnung nicht durch CDP oder alternative Oberflächen umgehen.
- [ ] Pflichtmatrix abnehmen: `/`, `/roadmap`, `/offen`, `/entscheidungen`, `/hardware`, `/live`, `/sicherheit`; jeweils Desktop und etwa 390×844. Den Statusbanner zusätzlich in der zentralen Schale prüfen.
- [ ] Sichtbare Inhalte, horizontales Überlaufen, Tastaturbedienbarkeit wesentlicher Navigation, Konsolen-/Modulfehler und korrekte Kanonaussagen prüfen. Nicht behaupten, dieser Umfang sei ein vollständiges WCAG-Audit.
- [ ] Auth-Zustände separat beschreiben: anonyme Konzeptseite, Loginansicht und später authentifizierte synthetische Praxis. Aktuell nicht freigegebene Session-/Tenant-Mutationen bleiben ausstehend.

**Prüfbefehl für den vorhandenen Smoke nach Reparatur und autorisiertem Serverstart:**

```powershell
node --test scripts/browser-smoke-verdict.test.mjs
node scripts/browser-smoke.mjs http://127.0.0.1:8080/ screenshots/k1-dev.png
```

Die zusätzlichen Routen mit dem unterstützten Browserwerkzeug prüfen; der obige Homepage-Aufruf ersetzt die Routenmatrix nicht.

**Abnahme:** Frische Screenshots und nachvollziehbare Routenbefunde. Ein Assetfehler bleibt sichtbar als Fehler mit Ursache; er wird nicht aus dem Smoke entfernt, um Grün zu erzwingen.

## E7 – Reale Plattformassets und Lint

**ALT-Bezug:** Tasks 12/13. **Dateien:** neu `scripts/platform-assets.mjs`, `scripts/platform-assets.test.mjs`; anpassen `package.json`. Lintscope zunächst `src/lib/app-data/client.server.ts`, `src/lib/auth/use-current-user.ts`, `src/routes/daten.tsx`, `src/routes/gestaltung.tsx`; neue Befunde vor Erweiterung einordnen.

- [ ] Assetvertrag gemäß ALT Task 12 implementieren; ausschließlich autoritative Dateien prüfen. Keine Generierung oder erzwungene Git-Aufnahme verwalteter Dateien.
- [ ] Reale Verfügbarkeit messen statt den historischen Blocker als unveränderlichen Zustand einzutragen.
- [ ] Lintbaseline frisch erheben; nur verhaltensneutrale Bereinigungen in diesem Paket. Authlogik nicht beiläufig verändern.
- [ ] Prüfen:

```powershell
node --test scripts/platform-assets.test.mjs
npm run check:platform-assets
npm run lint
npm run typecheck
```

**Abnahme:** Asset-Unit-Tests Exit 0; reales Assetgate tatsächlicher Erfolg oder präzises `platform_assets_unavailable` (ALT: Exit 2). Lint 0 Fehler/0 Warnungen und Typecheck Exit 0. Falls reale Assets die Browserabnahme blockieren, bleibt diese Abnahme unvollständig; nur unabhängige lokale Teilnachweise sind abschließbar.

## E8 – Lokale Gesamtabnahme und Übergabe

**ALT-Bezug:** Task 14. **Dateien:** `docs/project-control/K1-VERIFICATION.md` erst hier erstellen; aktuelle Statusquelle fortschreiben. Review-/Rohprotokolle gemäß geltender Evidenzgrenze lokal und sanitisiert halten.

- [ ] Snapshot eindeutig fixieren: HEAD plus Hashes relevanter uncommittierter Dateien; für einen späteren Abschlusscommit die Freigabe prüfen. Nicht stillschweigend committieren.
- [ ] Lokale Gates frisch ausführen und jeweils Exitcode erfassen:

```powershell
npm run check:k1-control
npm run check:canon
npm test
npm run typecheck
npm run lint
npm run check:auth
npm run build:dev
```

- [ ] Fehlgeschlagene Befehle einzeln dokumentieren; der Exitcode des letzten PowerShell-Befehls darf frühere Fehler nicht verdecken.
- [ ] E6-Routenmatrix gegen Dev und gebautes Ergebnis vergleichen. Vor Built-Smoke den passenden frischen Build verwenden; nur selbst gestartete alte Preview beenden.

```powershell
npm run preview -- --host 127.0.0.1 --port 8081 --strictPort
```

Dieser Befehl läuft in einem eigenen freigegebenen Prozess; danach separat:

```powershell
node scripts/browser-smoke.mjs http://127.0.0.1:8081/ screenshots/k1-built.png --baseline screenshots/k1-dev.json
```

- [ ] Asset- und Publikationsgate getrennt beurteilen. Für den Scanner nur die bestehende wertfreie Ausgabe und explizit bestimmte lokale Basis verwenden; keine spontane Remoteaktualisierung oder Publikation.
- [ ] Gemäß ALT Gesamt-Spec-Review, danach unabhängiges Quality-/Securityreview; Reviewpaket auf relevanten Diff und frische Evidenz begrenzen. Befunde primär verifizieren.
- [ ] Status nur für vollständig geprüften Scope als verifiziert markieren. Offene externe Blocker, unerledigte Browserrouten und veraltete Nachweise ausdrücklich nennen.

**Abnahme:** Reproduzierbare lokale K1-Evidenz. Kein Schluss auf Produktionsreife, Publikationsfreigabe oder Serverabnahme. Eine auf fehlenden Plattformassets beruhende unvollständige Browserprüfung erlaubt keine pauschale Gesamtfreigabe.

## 3. Separat vorzubereitende Folgepakete

| Paket | Eintrittsbedingung | Ergebnis |
|---|---|---|
| Produktionsmodus-Build | Separat freigegebene synthetische Umgebung und Buildpfad ohne Produktionsmigration | Gebautes Produktionsmodus-Artefakt unter passenden Flags geprüft; keine Behauptung durch `build:dev` |
| Server G0-SRV | Bestehender Preflight, Backup-/Restore- und Recovery-Nachweise; Installation gesondert freigegeben | Dokumentierte Gates 0–12; Produktpause endet erst bei `G0-SRV-12` |
| Phase-1-Sicherheitsabnahme | Serverbaseline abgenommen; synthetische Auth-/Tenant-Tests freigegeben | Zwei Mandanten, Rollen, Sessionablauf, fremde Objekt-IDs und serverseitige Verweigerung geprüft |
| Produktphasen 2–10 | Abnahme jeweils vorheriger Phase | Jeweils phasengerechter Detailvertrag statt spekulativer vollständiger Implementierungsplanung heute |

## 4. Besprechungsentscheidungen

- [ ] Zuordnung E0–E8 als korrigierte Fortsetzung von ALT übernehmen oder Abweichungen dokumentieren.
- [ ] Neues operatives Statusformat einschließlich HTML-Aktualitätsanzeige bestätigen.
- [ ] Instanzzuordnung und Cleanup-Vertrag von E5 bestätigen.
- [ ] Externe Assetabhängigkeit und spätere Produktionsabnahme mit Verantwortlichem versehen.
- [ ] Erst danach konkretes Ausführungspaket und dessen Mutationsgrenze benennen.

Unbestätigte Checkboxen sind keine implizite Zustimmung. Bestehende Produktentscheidungen werden hier nicht neu zur Disposition gestellt.
