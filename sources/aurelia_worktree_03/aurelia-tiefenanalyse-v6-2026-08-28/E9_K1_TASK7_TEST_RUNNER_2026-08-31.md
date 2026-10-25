# E9 — K1 Task 7 plattformübergreifender Test-Runner

**Letzte Aktualisierung:** 2026-08-31, 20:00 CEST  
**Status:** `LOCAL_TASK7_PASS_UNCOMMITTED_TASK8_RED`  
**Task:** K1 Task 7 — fail-closed plattformübergreifender Test-Runner  
**Reasoning:** `High`  
**Basis:** Branch `codex/aurelia-konsolidierung`, HEAD `1185a68ed984b525686764f995513355701929e3`, Pflichtvorfahr `8706186af01e10e4253e25abb31bf3577110dae4`  
**Freigabegrenze:** lokale Task-7-Bearbeitung freigegeben; kein Task-7-Commit und kein Push

## 1. Read-only Preflight

| Prüfung | Ergebnis |
|---|---|
| `git status --short --branch` | sauber; Branch drei Commits vor Tracking-Ref |
| `git rev-parse HEAD` | exakt `1185a68ed984b525686764f995513355701929e3` |
| Divergenz | `0 3` |
| Pflichtvorfahr | vorhanden, Exit 0 |
| `git diff --check` | sauber, Exit 0 |
| `node --version` | `v22.22.0` |

E9 und alle vier Status-Live-Dateien sind über `/aurelia-tiefenanalyse*/` ignoriert.

## 2. Bestätigtes False-green

Das aktuelle `package.json` verwendet:

```json
"test": "node --test 'scripts/**/*.test.mjs' && node --experimental-strip-types --test src/lib/app-data/app-data.test.ts src/lib/auth/gate-identity.test.ts"
```

Unter Windows `cmd.exe` bleiben POSIX-Single-Quotes Teil des Globarguments. Dadurch kann Node die komplette MJS-Pflichtgruppe als `0 tests` auslassen und der nachfolgende TS-Prozess den Gesamtbefehl grün erscheinen lassen. Task 7 ersetzt diese shellabhängige Zweiprozesskette durch einen einzigen fail-closed Node-Prozess.

## 3. Exakte öffentliche API

`scripts/test-runner.mjs` exportiert ausschließlich:

```text
discoverRequiredTestGroups(root)
assertNoEmptyGroups(groups)
nodeTestCommand(files)
exitStatusFromChild(code, signal)
```

`projectRoot`, `isMainModule` und `exitStatusFromChild` werden aus `scripts/with-app-env.mjs` wiederverwendet; `exitStatusFromChild` wird re-exportiert.

## 4. Discovery-Vertrag

### MJS-Pflichtgruppe

- rekursiv, aber ausschließlich unter `<root>/scripts`;
- nur case-exakte reguläre Dateien `*.test.mjs`;
- keine Symlink-/Junction-Verfolgung;
- ein symlinked/junction `scripts`-Root ist ein Fehler;
- Repositorypfade mit `/`, deterministisch per Code-Unit sortiert;
- unerwartete I/O-Fehler werden nicht als leere Gruppe maskiert.

### TypeScript-Pflichtgruppe

Exakt und in dieser Reihenfolge:

```text
src/lib/app-data/app-data.test.ts
src/lib/auth/gate-identity.test.ts
```

Jede fehlende, nichtreguläre oder verlinkte Pflichtdatei ist vor Spawn ein Fehler. Weitere TS-Tests werden nicht automatisch aufgenommen.

Beide Gruppen müssen Arrays mit mindestens einem Eintrag sein. Fehlermeldungen nennen deterministisch `mjs ... empty` oder `typescript ... empty`.

## 5. Einprozess- und Lifecycle-Vertrag

`nodeTestCommand(files)` liefert ohne Eingabemutation:

```text
command: process.execPath
args: --experimental-strip-types --test <alle MJS> <beide TS>
```

Die CLI validiert vollständig vor Spawn und startet genau ein Kind mit:

```text
cwd: projectRoot()
shell: false
stdio: inherit
windowsHide: true
```

`SIGINT`, `SIGTERM` und `SIGHUP` werden an dieses Kind weitergegeben. Numerische Child-Exits bleiben exakt; Signale und `null/null` werden über `exitStatusFromChild` nie als Erfolg gemeldet. Discovery-/Gruppenfehler sind Exit 1 vor Spawn; synchrone oder asynchrone Spawnfehler Exit 127. Ausführung erfolgt nur hinter dem realpath-sicheren `isMainModule(import.meta.url)`-Guard.

## 6. Test-first Matrix

Der neue fokussierte Vertrag prüft:

1. rekursive, sortierte Happy-Path-Discovery;
2. Filter- und Root-Grenzen;
3. wiederholbare deterministische Ergebnisse;
4. übersprungene Nested-Symlinks/Junctions;
5. abgelehnten verlinkten `scripts`-Root;
6. beide TS-Pflichtdateien jeweils missing/nichtregulär/verlinkt;
7. beide leeren Gruppen unabhängig plus gültige Kontrolle;
8. unveränderte Einprozess-Commandkonstruktion;
9. Exit 0/7, `null/null` und `SIGTERM`;
10. Import ohne CLI-Nebeneffekt;
11. reale synthetische CLI mit einem MJS- und beiden TS-Tests in einem kombinierten Child-Prozess.

Windows-Symlinktests dürfen ausschließlich bei `EPERM`/`EACCES` capability-begründet skippen; alle anderen Fehler bleiben rot.

## 7. RED/GREEN und Suite-Exposition

1. Testdatei zuerst anlegen.
2. `node --test scripts/test-runner.test.mjs` muss ausschließlich wegen fehlendem Runner/API RED sein.
3. Runner minimal implementieren; fokussierter Vertrag vollständig GREEN.
4. Nur `package.json`-Testscript auf `node scripts/test-runner.mjs` umstellen.
5. `npm test` muss alle dynamisch entdeckten MJS-Dateien und exakt beide TS-Dateien in einem Prozess exponieren. Nach Anlage des Runner-Tests sind aktuell 12 MJS-Dateien zu erwarten; die Produktion hardcodiert diese Zahl nicht.
6. Exit 0 ist nur mit sichtbarer Vollentdeckung gültig. Exit ungleich 0 ist für Task 7 nur zulässig, wenn jeder Befund exakt einem unveränderten Task-8-Legacyvertrag zugeordnet ist. `0 tests`, Gruppenverlust, Runner-/TS-/unbekannte Fehler sind STOP.

## 8. Exakter Scope

Erlaubte tracked Dateien:

```text
package.json
scripts/test-runner.mjs
scripts/test-runner.test.mjs
```

Nichtziele:

- kein `package-lock.json`;
- keine Task-6- oder Task-8-Datei;
- keine tracked Dokumentation;
- kein Build, Dev-Server, Preview, Migration oder Serverzugriff;
- kein Staging, Commit oder Push.

## 9. Abschlussgates

- fokussierter Runnervertrag;
- ehrliches `npm test` mit Dateiinventar-/Fehlerklassifikation;
- Canon, K1-Control, Typecheck;
- fokussiertes ESLint und Prettier;
- Diff-Check;
- explizite Unverändertheitsnachweise für Lockfile, Task 6, `with-app-env` und Task-8-Tests;
- final exakt drei Task-7-Pfade im Git-Status.

Task 7 bleibt Spur A. Canon-/Security-Ausweitung, ein P0–P2-Befund, unklare Suiteklassifikation oder zusätzlicher tracked Scope führt zum Stopp und einer neuen Betreiberentscheidung einschließlich möglicher Extra-High-Hochstufung.

## 10. Test-first RED

Um 19:21 CEST wurde ausschließlich `scripts/test-runner.test.mjs` angelegt. Der Vertrag deckt Discovery, Filter-/Rootgrenzen, Symlinks/Junctions, beide TS-Pflichtdateien, leere Gruppen, Command-/Exitverhalten, Main-Guard und eine synthetische Einprozess-CLI ab.

```text
node --test scripts/test-runner.test.mjs
```

Ergebnis: **0/1 RED**, exakt `ERR_MODULE_NOT_FOUND` für das noch nicht vorhandene `scripts/test-runner.mjs`. Keine Fixture-, Permission- oder fremde Fehlerursache trat auf.

## 11. Minimaler Runner — fokussiert GREEN

`scripts/test-runner.mjs` implementiert die fixierte API, rekursive fail-closed Discovery, exakte TS-Allowlist und einen einzigen shell-freien Node-Spawn. Root-, Main-Guard- und Exitlogik werden aus `with-app-env.mjs` wiederverwendet.

Die synthetische CLI-Fixture wurde während der Testentwicklung so isoliert, dass ein geerbter `NODE_TEST_CONTEXT` vor dem absichtlich verschachtelten Testprozess entfernt wird; andernfalls behandelt Node den Child-Test als Teil des äußeren Testharness. Dies ändert keinen Produktionspfad und schwächt keine Assertion.

Fokussierter Endstand:

| Prüfung | Ergebnis |
|---|---|
| `node --test scripts/test-runner.test.mjs` vor Package-Wiring | **9 PASS / 1 capability-skip / 0 FAIL** |
| Package-Testscript | exakt `node scripts/test-runner.mjs` |
| fokussierter Lauf nach Package-Wiring | **9 PASS / 1 capability-skip / 0 FAIL** |
| fokussiertes ESLint | Exit 0 |

Der einzige Skip ist der ausdrücklich erlaubte Windows-Dateisymlink-`EPERM`; Directory-Junction-Grenzen wurden real ausgeführt und bestanden.

## 12. Ehrliche Vollsuite exponiert

`npm test` lief über den neuen Runner in genau einem Node-Testprozess und endete erwartungsgemäß mit Exit 1. Die Discovery wurde separat aus derselben Produktionsfunktion ausgegeben und enthält vollständig:

- **12 MJS-Dateien** unter `scripts/`, einschließlich `test-runner.test.mjs`;
- exakt **2 TypeScript-Pflichtdateien** aus der Allowlist.

Node-Gesamtergebnis:

```text
7 suites
308 tests
292 pass
15 fail
1 capability-skip
0 cancelled
0 todo
```

Alle 15 Fehler sind vollständig und ohne Rest Task 8 zugeordnet:

| unveränderte Task-8-Datei | Fehler | Klassifikation |
|---|---:|---|
| `scripts/check-auth-invariant.test.mjs` | 2 | alte Auth-off-Erwartung; Windows-Symlink-EPERM |
| `scripts/grok-pwa-plugin.test.mjs` | 9 | nicht fixture-isolierte PWA-/Site-/Asset-Annahmen, einschließlich fehlendem verwaltetem Asset |
| `scripts/migration-plan.test.mjs` | 1 | alte Erwartung ohne Root-Migrationen |
| `scripts/with-app-env.test.mjs` | 3 | alte Auth-off/App-Env-Erwartungen; Windows-Symlink-EPERM |

Keine Runner-, Discovery-, TypeScript-Gruppen-, Task-6- oder unbekannte Fehlerursache trat auf. `0 tests` ist ausgeschlossen. Die Task-8-Dateien wurden weder repariert noch verändert; ihr roter Zustand blockiert Task 7 nicht und bleibt separat für Task 8.

## 13. Finale Task-7-Gates — lokaler PASS

Um 20:00 CEST wurden die Abschlussprüfungen frisch beendet:

| Prüfung | Ergebnis |
|---|---|
| fokussierter Runnervertrag | **9 PASS / 1 EPERM capability-skip / 0 FAIL** |
| ehrliche Vollsuite | **12 MJS + 2 TS; 308 Tests; 292 PASS; 15 ausschließlich Task 8; 1 Skip** |
| `npm run check:canon` | Exit 0 |
| `npm run check:k1-control` | Exit 0 |
| `npm run typecheck` | Exit 0 |
| fokussiertes ESLint | Exit 0 |
| fokussiertes Prettier | PASS |
| `git diff --check` | Exit 0; nur bekannter LF/CRLF-Hinweis für `package.json` |
| `package-lock.json` | unverändert |
| Task-6-Dateien | unverändert |
| `with-app-env` + Task-8-Testdateien | unverändert |
| Index | sauber |
| Branch / HEAD | `codex/aurelia-konsolidierung` / `1185a68ed984b525686764f995513355701929e3` |
| Divergenz | `0 3` |

Exakter tracked Task-7-Stand:

```text
 M package.json
?? scripts/test-runner.mjs
?? scripts/test-runner.test.mjs
```

`package.json` besitzt ausschließlich die eine semantische Scriptänderung (1 Einfügung/1 Löschung). Keine weitere tracked Datei wurde verändert.

**K1 Task 7 ist lokal PASS und bleibt uncommittet.** Der rote `npm test`-Gesamtexit ist kein Task-7-Runnerfehler, sondern die nun erstmals vollständig sichtbare und exakt abgegrenzte Task-8-Altlast. Ein False-green durch `0 tests` ist geschlossen.

## 14. Exakter nächster Entscheidungsrand

Task 8 wurde nicht begonnen und ist nicht freigegeben. Ein Task-7-Commit benötigt eine separate Betreiberfreigabe für exakt die drei Task-7-Dateien; diese wäre keine Pushfreigabe. Bis zur nächsten Entscheidung: Task-7-PASS und den getrennten Task-8-RED-Status berichten und stoppen.
