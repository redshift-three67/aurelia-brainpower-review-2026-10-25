# R2-0 – sicherer Wiederaufnahmepunkt, 17.10.2026

Status: zusätzliche synthetische SQLite-Tests freigegeben, aber **Kapazitäts- und Crashpakete noch nicht gestartet**. Keine Produktänderung, Schutzaktivierung, Vorschau-/Budgetänderung oder neuer Cloud-Security-Scan.

## Verifizierter letzter Lauf

- Eigene Arbeitskopie: `runtime/rw-storage-r2-20261017`, Branch `codex/rw-storage-r2-20261017`, Produktbasis HEAD `d1eb34260179a499e2b0362bf609ce96957b78aa`.
- `AURELIA_RW_STORAGE_R2_0_2026-10-17_controls_c4205fb93421.json`: vollständiger Linux-Kontrolllauf, Exit 0, 29 Kontrollen (19 Runner / 10 Protokoll), Container entfernt, Quellen und Vorschau unverändert. Kein Kapazitäts-/Crashnachweis.
- Vorheriger gezielter RED-Lauf `controls_ceddfd7961f4`: 29 Tests, elf erwartete Assertionfehler, keine Import-/Umgebungsfehler. Container entfernt, Vorschau unverändert.
- Frühere RED-/GREEN-Belege bleiben erhalten; nichts umetikettieren oder löschen.

## Nächster Schritt – zuerst Testtreiber abschließen

Der unabhängige Review erkannte einen Widerspruch der ursprünglichen Probetabelle zur exakten ComparisonStore-Schemaprüfung. Der Plan ist auf ein natives UPDATE der synthetischen input_json-Zeile angepasst: echte Hauptdatenbank, gleiche aktive Connection, bestätigtes Seitenlimit, keine selbst erzeugte SQLite-Ausnahme und kein Commit/Rollback im Produktadapter. Produktcode bleibt unverändert.

Root korrigierte die drei Review-Befunde: erforderliches package-Schlüsselwort am Abschlussvalidator, negative Erfolgsfelder bei Abschlussfehlern, sofortige Crash-Belegsicherung sowie verpflichtende SQLite-Snapshots vor/nach Abbruch und im READY. Die 29 Kontrollen wurden danach grün ausgeführt. Der Reviewer konnte diese Korrekturen wegen lokaler Tool-Timeouts nicht abschließend erneut lesen.

Zwei noch offene Testtreiberpunkte aus dem letzten Review:

1. ACTIVE_CASE_EVIDENCE und LAST_CHILD_CAPTURE vor **jedem** neuen Fall zurücksetzen, damit Fixture-Aufbaufehler keine Belege des vorherigen Erfolgsfalls übernehmen.
2. Bei fehlgeschlagener Fallvalidierung failed_case.consistency_ok ausdrücklich False ausweisen; erfolgreichen Readback und vollständige Fallvalidierung unterscheiden.

Nach Wiederherstellung verlässlicher Toolsteuerung: diese Punkte gezielt absichern/korrigieren, Kontrollen Linux grün, unabhängigen Review abschließen. Erst danach capacity (sechs Fälle) und crash (vier Fälle) nacheinander unter den unveränderten Grenzen. Keine Kriterien lockern und keine alten R1-Ergebnisse als neuen Nachweis verwenden.

## Grund des Halts

Nach dem gespeicherten GREEN scheiterten wiederholt lokale exec-Prozessstarts am `connecting runner pipe-in`-Timeout; auch der alternative Node-Dateizugriff lief in einen Timeout. Das ist ein Ausführungs-/Beobachtungshindernis, kein belegter Fehler der laufenden Serveranwendung. Keine Kapazitäts-/Crashausführung ohne abgeschlossenen Review. Dieser Text ist eine dokumentierte Übergabe, **kein hashverifizierter Vollcheckpoint, Runtimebackup oder Gitcommit**; abschließende Dateiverifikation bei Wiederaufnahme nachholen.

## Ergänzende Betreiberwünsche

- Auslastungsbeleg: `AURELIA_PILOT_AUSLASTUNG_2026-10-17.json`, fünf Sekunden am 17.10.2026, 18:42:36 UTC. Aurelia etwa 1,04 / 10 GiB, 0,09 % seines CPU-Budgets; Website etwa 1,18 / 4 GiB, 4,56 % ihres CPU-Budgets. Host 0,45 % CPU, etwa 22 GiB verfügbar; kein OOM im beobachteten Zustand. Momentaufnahme, keine Lastabnahme. Limits nicht verändert.
- Jeder weitere kostenpflichtige Cloud-Security-Scan benötigt vorab einen Hinweis zu Zweck, Kostenschätzung und Bezug zum verlässlich einsehbaren aktuellen Guthaben; erst nach Betreiberfreigabe ausführen. Kein neuer Scan für R2-0 vorgesehen; Guthaben nicht neu geprüft.
- Die zurückgezogenen Website-Repositoryhinweise gehören nicht zu Aurelia und werden hier nicht verwendet.
