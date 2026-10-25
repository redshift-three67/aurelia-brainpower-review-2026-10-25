# Tatsächlicher Wiederaufnahmestand nach Governor 0.3

Stand: 12.09.2026, nach Umsetzung und Prüfung des begrenzten 0.3-Teilstands. Die ursprüngliche Pause ist als Historie in `project_memories/WIEDERAUFNAHME_2026-09-12.md` und `checkpoints/2026-09-12_PAUSE_ABCD/` erhalten. Deren Aussage „A–D noch nicht begonnen“ ist für den aktuellen Arbeitsstand überholt; der Checkpoint wird nicht zurückgespielt.

## Aktueller Betrieb

Governor 0.3.0 läuft auf `http://127.0.0.1:8787/`. Alle fünf alten IDs sind in `aurelia-integration` erhalten: Aurelia Elternprojekt, Modul_Templates Vertragsprojekt, RadiWorks/Radi144/Morphic Module. Lokale Beobachtung ist an, automatische Reviews sind aus, ausgewählter Supervisor ist Astra medium; Sol bleibt verfügbar. Die Grundsatzfreigabe A→B→C→D besteht fort. Sie ist keine pauschale Produktgate-Abnahme und kein Auftrag, die Automatik erneut einzuschalten.

Beim Umstieg stimmten der Legacy-Quellen-/Regelfingerprint `05f04d8e98e0c10c018cb33b6655f340b8e90c3282f9634a70b4be9d0b3141b1`, der Entscheidungsfingerprint `91869ea542f33251f68ee1313cf08f5ae393b3579519e946dcf1c24f9d0743a5` und das vollständige bestehende Governor-Matrixobjekt exakt überein. Nachweise: `artifacts/pre-v03-main/state.json` und `artifacts/post-v03-main-state.json`. Bei der nächsten Fortsetzung erneut gegen den dann aktuellen Stand prüfen.

Danach wurden alle fünf bereits vorhandenen Strategiegedächtnisse über den Registerendpunkt zugeordnet, jeweils `created=false`, ohne Änderung des Quellen- oder Entscheidungsfingerprints. Neuester Nachweis: `artifacts/existing-memory-mapping-v03.json`. Die Zuordnung ist erledigt; die fachliche Aufnahme bleibt separat offen. Die Gruppenkarten bieten Einzelaufnahme/Projekthybridreview mit ausdrücklicher Gruppenbegrenzung. Die frische portable 0.3-Kopie bestand auf demselben Windows-PC erneut 262 Tests bei zwei übersprungenen Fällen; `artifacts/portable-verification-v03.json` dokumentiert Paketintegrität und Grenzen. Ein zweiter physischer PC wurde nicht getestet.

Zusätzlicher lokaler Programm-/Journal-Checkpoint: `checkpoints/2026-09-12_GOVERNOR_0_3_FINAL`. Das Manifest beschreibt Grenzen; externe Produktrepositories und Runtime-Artefakte werden dadurch nicht vollständig gesichert. Der alte vollständiger angelegte Pausencheckpoint bleibt erhalten.

## Umgesetzter Umfang

- A: persistentes Register, Singles/Gruppen, dauerhafte Mitgliedschaft und Rollen, kontrollierte Strategiegedächtnisse, lokale rotierende Scope-Beobachtung sowie ausdrücklich zugeordnete Vault-Quellen. Neue Modellfreigaben starten aus; bekannte IDs allein erteilen keine Übermittlungserlaubnis.
- B: quellengebundene bestätigte Aufnahme, strukturierte Terra-Pläne mit unabhängigem Review, unveränderliche Kandidatenrevisionen und sichtbare Prioritäten/Abhängigkeiten. Auswahl bleibt `plan_selection_only`.
- C: ausdrücklich erlaubter unabhängiger Single-Pilot außerhalb der fünf Produkte; Modellpatch, Supervisorprüfung, versiegeltes Staging, realer eingeschränkter stdlib-unittest und Nachreview einschließlich vollständiger unveränderter Testquellen. Originaldateien werden nicht zurückgeschrieben.
- D: bisherige konfigurierte lokale Chrome/CDP-Ansichten bleiben verfügbar; kein neues allgemeines App-Adapter-System.

## Belege und Aussagegrenzen

Gesamtsuite: 264 Fälle, 262 erfolgreich, zwei Windows-Symlinktests wegen Berechtigung übersprungen; keine Fehlschläge. `artifacts/unit-tests-v03.txt` enthält den Abschluss. Der Browserablauf mit Registrierung, Gruppenbindung, Aufnahme, zwei synthetischen Revisionen, Auswahl und Vorgängersperre ist in `artifacts/browser-check-v03.json` als manuelle Aufzeichnung werkzeugbeobachteter Interaktionen dokumentiert. Der Screenshot existiert nur inline im Gespräch.

Der echte Pilot r3 verwendete Hermes 21.1/Terra mit Sol und mit Astra. Beide Kombinationen führten jeweils einen unittest aus und endeten nach vollständigem Quellenreview mit `verified=true`; keine Originaländerung, kein Apply-back. Die Zero-Tool-Prüfung war erfolgreich. Der Betreiberplan und das Projekt waren synthetische Fixtures, keine modellgenerierte Gesamtplanung und keine echten Produktinhalte. `artifacts/staging-pilot-live-2026-09-12-r3/report.json` ist der zusammengeführte Nachweis. Die früheren r1/r2-Blockaden bleiben historische Diagnoseevidenz; r2 führte zur Ergänzung vollständiger unveränderter Testtexte.

Der eingeschränkte Python-Runner ist keine OS-Sandbox gegen bösartigen Code im selben Prozess. Erfolg benötigt einen separaten Abschlussdatensatz außerhalb gewöhnlicher Test-Schreibrechte, tatsächlich nicht übersprungene Tests, unveränderte Quellen und einen sauberen Nachreview. Stdout, null Tests oder ausschließlich übersprungene Tests gelten nicht als Erfolg.

## Genau hier weiterarbeiten

Zuerst aktuelle Quellen, laufenden Dienst und jüngste Nachweise prüfen. Danach den bereits freigegebenen Ausbau fortsetzen: kontrolliertes Apply-back mit Konflikt-/Rollbacknachweisen, begrenzte Reparatur und Fortschrittsführung; anschließend vollständige projektspezifische D-Adapter. Vault-Spiegelung und sicherer Umzug/Pfadwechsel sind noch offen. Keine automatische Ausführung abhängiger Folgen oder Produktintegration aus einer bloßen Planauswahl ableiten. Die Grundsatzfreigabe nicht erneut als fehlend darstellen; konkrete Produktgates und geänderte Umfänge weiterhin individuell beachten.

Maßgebliche aktuelle Beschreibungen: `docs/GOVERNOR_0_3.md`, `docs/VERIFICATION_0_3.md`, `docs/LLM_OPERATING_CONTRACT.json` und der laufende Quellcode. Der ursprüngliche konsolidierte Ausbauplan bleibt `docs/KONSOLIDIERUNG_SINGLE_MATRIX_VAULT_2026-09-12.md`. A–D sind nicht vollständig abgeschlossen.
