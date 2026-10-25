# 01 – Belegter Ist-Stand und Planungsreview

Stand: 07.09.2026, Europe/Berlin. Vorschlag zur Besprechung; keine Ausführungsfreigabe.

## 1. Umfang und Urteil

**Urteil: Änderungen an der operativen Planung erforderlich; Grundarchitektur beibehalten.** Hohe Sicherheit besteht für die hier konkret belegten Dokument-/Git-Widersprüche. Die Laufzeitstabilität der Gesamtanwendung ist nicht beurteilt.

Untersucht wurden der K1-Masterplan, die Projektsteuerung, die Übergabe vom 30.08., ausgewählte Implementierungsdateien und die lokale Git-Historie. Dies ist kein vollständiges Security-Audit aller Komponenten. Keine externen Rohquellen, Secrets, produktiven Daten oder Server wurden geprüft. Es erfolgten keine Builds, Datenbankmigrationen, Testläufe mit Dateifixtures oder Browserabnahmen. Zwei lesende Vertragsprüfungen wurden am 07.09.2026 erneut ausgeführt.

## 2. Ausgangsbasis

| Objekt | Tatsächlich beobachtet | Bedeutung |
|---|---|---|
| ROOT-Branch | `codex/aurelia-vorbereitung`, Commit `8706186` | Älterer Planungsstand; nicht die aktuelle K1-Implementierung |
| K1-Branch | `codex/aurelia-konsolidierung` | Arbeitsbasis der Empfehlungen |
| K1-HEAD | `1185a68ed984b525686764f995513355701929e3` | Portal-Commit vom 31.08.2026 |
| Vorheriger Kanon-Commit | `c00fd83` vom 31.08.2026 | Task-5-Ergebnis bereits committed |
| Task-4-Commit | `1257283` vom 29.08.2026 | Kanonvertrag vorhanden |
| Uncommittierte Änderung | `package.json`: `test` auf `node scripts/test-runner.mjs` umgestellt | Bestandteil des aktuellen Arbeitsstands |
| Unversionierte Dateien | `scripts/test-runner.mjs`, `scripts/test-runner.test.mjs` | Task 7 begonnen; Abschluss nicht nachgewiesen |
| Server-Gatestatus | `G0-SRV-0`, Backup/Restore-Nachweis ausstehend | Dokumentierter Stand; kein frischer Hostnachweis |
| Node | `v22.22.0` | Runtime der lesenden Vertragsprüfungen |

Ein Commit belegt vorhandene Änderungen, nicht automatisch deren Freigabe oder vollständige Abnahme. Aus späteren Commits darf insbesondere kein rückwirkender Berechtigungsverstoß gegen frühere Freigabegrenzen abgeleitet werden: Der zugehörige gesamte Freigabeverlauf wurde nicht geprüft.

## 3. Verifikation

Ausführungsort: K1. Beide Befehle wurden in separaten Prozessen ausgeführt.

| Befehl | Ergebnis am 07.09.2026 | Beweist | Beweist nicht |
|---|---|---|---|
| `node --experimental-strip-types scripts/canon-contract.mjs` | Exit 0, keine Fehlerausgabe | Aktuelle Dateien erfüllen den implementierten Kanonvertrag | Vollständigkeit jedes Produkt-/Sicherheitsvertrags |
| `node scripts/check-project-control-k1.mjs` | Exit 0, keine Fehlerausgabe | Implementierte K1-Steuerungsregeln erfüllt | Vollständig aktuelles Task-Ledger |
| `git status --short` in K1 | Drei oben benannte Einträge | Uncommittierter Stand vorhanden | Autorisierung oder Testqualität |
| Lokale Git-Historie | `c00fd83`, danach `1185a68` | Tasks 5/6 als Änderungen vorhanden | Aktueller Remotezustand |

Historische Meldungen wie „31/31 PASS“ oder „53 Tests grün“ bleiben historische Evidenz und werden nicht als Ergebnis dieses Reviews ausgegeben. Remote-Tracking-Refs wurden nicht durch Fetch aktualisiert.

## 4. Bestätigte Planungsbefunde

### R01 – Operative Statusquellen widersprechen dem Codefortschritt

**Priorität: hoch.** `docs/project-control/K1-STATUS.md:59` nennt für Task 5 „noch kein Commit“; Zeilen 81 und 221–223 erklären Task 6 als nicht begonnen. Dem stehen `c00fd83` und `1185a68` gegenüber. Die ROOT-Übergabe nennt noch Task 5 als nächsten Schritt. Der aktuelle Dirty-Diff weist bereits auf Task 7.

**Folge:** Wiederaufnahme kann abgeschlossene Arbeiten erneut beginnen oder vorhandene Task-7-Dateien überschreiben. Der grüne Steuerungscheck verhindert das derzeit nicht.

**Korrektur:** Aktuellen Fortschritt separat von historischen Snapshots führen; Phase, Implementierung, Verifikation und Berechtigung nicht in einem Status vermischen. Zuordnung zu Paket E0/E1.

### R02 – Task 10 hat widersprüchliche Dependency-Injection-Namen

**Priorität: hoch.** ALT:906/913 verwendet `spawn` und `fetch`; ALT:936/937 deklariert `spawnImpl` und `fetchImpl`.

**Folge:** Tests können Fakes an wirkungslosen Optionsnamen übergeben. Je nach Implementierung wird dann der reale Standardpfad statt des vorgesehenen Testpfads verwendet. Dies ist ein bestätigter Vertragswiderspruch, kein nachgewiesener Laufzeitfehler einer bereits fertigen Task-10-Implementierung.

**Korrektur:** Durchgängig `spawnImpl`/`fetchImpl`; Integrationstest, der unerwartete reale Prozess-/Netzwerkzugriffe ausschließt. Zuordnung E5.

### R03 – Abschlussklassifikation bildet Fehler und fehlende Prüfungen nicht ab

**Priorität: mittel.** ALT:1253 erlaubt nur `green`, `external_blocker`, `publication_blocked`.

**Folge:** Tatsächliches Scheitern, nicht ausgeführte Prüfungen und veraltete Evidenz sind nicht ausdrücklich modelliert. Dadurch werden Wiederaufnahme und Teilabnahme mehrdeutig.

**Korrektur:** Testergebnis, Aktualität und Freigabegates als getrennte Felder führen. Ein externer Blocker darf keinen fehlgeschlagenen lokalen Test ersetzen. Zuordnung E1/E8.

### R04 – Falscher Verweis auf Browserabnahme

**Priorität: mittel.** ALT:680 verweist auf Task 13; die Browserabnahme ist in Task 14 ab Zeile 1177 beschrieben. Task 13 ist Lintbereinigung.

**Korrektur:** Verweis auf Task 14 beziehungsweise E8 berichtigen; Portal-Implementierungsabschluss nicht als Browserabnahme ausgeben. Zuordnung E1/E6/E8.

## 5. Präventive Vertragslücken und Abnahmegrenzen

### R05 – Eigener Prozess muss als Prüfziel identifizierbar sein

**Priorität: hoch für die Umsetzung von Task 10.** ALT:943 verlangt den Start eines Kindprozesses, Polling von `/__app-env` an Port 8080 und Aufräumen im `finally`. Der Vertrag fordert keine eindeutige Zuordnung der Antwort zum gestarteten Prozess und keinen expliziten Fremdserver-/Portkonflikttest.

**Risiko:** Eine Antwort eines bereits laufenden Servers kann als Readiness des neuen Prozesses fehlinterpretiert werden. „Elternprozess beendet“ beweist zudem nicht, dass ein Vite-Nachkomme auf Windows beendet wurde.

**Korrektur:** Negativfälle verbindlich machen: Port belegt, falsche Instanz, früher Exit, Timeout, Abbruch, verbleibender Nachkomme. Fail-closed bei nicht nachweisbarer Zuordnung. E5 definiert den Vertrag; Implementierung erst nach dessen Freigabe.

### R06 – Lokale K1-Abnahme ist keine Produktionsabnahme

`package.json` führt `build:dev` mit `--mode development` aus. Die bestehende Auth-Prüfung vergleicht die Dev-Antwort mit der aufgelösten Build-Konfiguration; sie liest laut eigenem Kommentar kein gebautes Bundle. Das ist als begrenzter Konfigurationscheck sinnvoll, aber kein Nachweis wirksamer Authentisierung oder Mandantentrennung.

**Empfehlung:** Begrenzung beibehalten und sichtbar benennen. Produktionsmodus und fachliche Zugriffstests als separate Folgeabnahmen planen. Kein `npm run build` als spontane Gegenprobe: Dieses Script verkettet den Build mit `db:migrate`.

## 6. Was erhalten bleiben soll

- Freigegebene Produktgrenzen, synthetische Daten und Pause bis dokumentiert bestandenem `G0-SRV-12`.
- Keine neuen Moduladapter, keine CUDA-/USB-Aktivierung, kein Video/WebRTC.
- Selektive Übernahme statt Zusammenführen historischer Implementierungszweige.
- Trennung von lokalem Engineering, Publikation, Plattformassets und Serverabnahme.
- Risikobasierte Spur A/B, gezielte Wiederholungsprüfungen und primäre Verifikation externer Findings.
- Backup/Restore vor destruktiver Installation; Gerätetabelle und Installation separat freigeben.

## 7. Korrektur der früheren Gesprächsauskunft

Die erste Statusübersicht betrachtete überwiegend ROOT und war bezüglich K1 unvollständig. Maßgeblich für diese Übergabe sind der hier belegte K1-Stand und die SHA-256-Werte im Quellenmanifest. Auch diese Aufnahme ist ein Zeitpunkt, keine dauerhaft aktuelle Zustandsbehauptung.
