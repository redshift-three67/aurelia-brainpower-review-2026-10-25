# Genehmigte Pilot-Prüffolge — Umsetzungsplan

> Umsetzung inline mit `superpowers:executing-plans`, keine automatische Delegation. Grundlage: [S1-Entwurf](../specs/2026-09-17-approved-pilot-sequence-design.md).

**Ziel:** Einen vorhandenen isolierten Vorschlag nach ausdrücklicher gebundener Zustimmung einmal testen/nachprüfen und anschließend vor der Übernahme halten.

**Architektur:** Erst schreibfreie Vorschau; anschließend eine persistente Sequenzreservierung über gewöhnlichen `stage_test`-/`pilot_assess`-Jobs am bestehenden einzelnen Worker. Aktive und terminale Sequenzzustände bleiben von Jobstatus und Produktgates getrennt.

**Technik:** Python-Standardbibliothek, SQLite, vorhandener HTTP-Dienst, Vanilla JS. Medium und ausgewähltes Modellrouting unverändert.

## S1a — Vorschau ohne Ausführung (abgenommen)

Dateien: neu `governor_workbench/sequences.py`, `tests/test_sequences.py`; ändern `governor_workbench/server.py`, `tests/test_server.py`; Betriebsvertrag/Entwickleranleitung erst mit dem tatsächlich implementierten API ergänzen.

- [x] Tests für `preview(app, stage_job_id)` gegen temporären erlaubten Pilot mit bestehendem versiegeltem Vorschlag anlegen. Erwartet: `eligible`, `profile_id`, `binding`, `binding_hash`, `stop_before=['pilot_prepare','pilot_apply']`, `model_transmission_required=true`, `execution_authorized=false`.
- [x] Negativfälle einzeln nachweisen: unbekannter/falscher/nicht abgeschlossener Auftrag, fehlende Stage, Gruppen/historische Produkte, neue Auswahl, Dateidrift in Original/Stage, widerrufene Egress-/Pilotregel und fehlender Testadapter.
- [x] Bestehende Prüfungen `PlanBook.execution_permission`, `require_staging_pilot` und `WorkspaceStager` wiederverwenden. Keine Test-, Modell-, Vorschlags- oder Sequenzanlage. Bei fehlenden Voraussetzungen `eligible=false` und begrenzter verständlicher Grund; keine geheimen oder ungefilterten Fehlerdaten.
- [x] Fingerprint aus dem S1-Bindungsvertrag erzeugen. Gleicher Stand ergibt denselben Hash; Änderung jeder bindungsrelevanten Komponente ändert Hash oder sperrt die Vorschau. Flüchtige Beobachtungszeit nicht in den Hash aufnehmen.
- [x] Route `POST /api/sequences/preview` unter bestehenden Host/Origin/Session/CSRF-Regeln ergänzen. Zusätzliche Felder, insbesondere `command`, `steps` und `supervisor`, abweisen.
- [x] Regression prüft Job-/Sequenz-/Entscheidungsbestand und Originaldateien vor/nach Vorschau auf Gleichheit; RouterClient-Aufrufe müssen null sein. Unabhängige lokale Cachebeobachtung nicht mit Freigabespeicherung verwechseln.

Gezielt ausführen (erst nach Anlage der Testdatei):

```powershell
$taskPython=(Get-Content runtime-python.json -Raw | ConvertFrom-Json).python
& $taskPython -m unittest tests.test_sequences tests.test_server
```

Erwartung vor Implementierung: neue Verhaltenstests schlagen wegen fehlender API/Funktion fehl; nach Umsetzung bestehen sie. Nur S1a-Abnahme, noch keine ausführbare Folge melden.

Abnahme 17.09.2026: 497 Tests, 495 bestanden/zwei ausgelassen; HTTP-/Browser-/Syntax-/Vertragsprüfung erfolgreich. Details im Wiederaufnahmestand. Start und Sequenzreservierung bleiben unimplementiert.

## S1b — Journal und exklusive Reservierung

Dateien: neu `governor_workbench/sequence_store.py`, `tests/test_sequence_store.py`; geändert `governor_workbench/store.py`, `governor_workbench/operator_questions.py`, `governor_workbench/sequences.py`, `tests/test_store.py`. Vorhandene JobRunner-/Auto-Review-Wege nutzen die gemeinsame Store-Sperre; keine Worker-Anbindung in S1b.

- [x] Zustandsübergänge und atomare Start-/Kind-/Abbruchtransaktionen aus S1 testen, bevor der Worker angebunden wird. Keine Zwischenphase darf fremde Jobstarts zulassen.
- [x] Sequenzschema separat und additiv anlegen; eindeutige Vorschlagsreferenz sowie eindeutige `(sequence_id, ordinal)`-Kindreferenzen erzwingen. Freigabebindung unveränderlich, Übergangsereignisse append-only.
- [x] Start erstellt Reservierung und ersten normalen Job gemeinsam. Private Kindanlage validiert Profil, nächste Position, reservierte Sequenz und erwarteten Vorgänger; keine beliebigen Kindaktionen zulassen.
- [x] Alle vorhandenen Einreihungswege einschließlich Rückfrageantwort/automatischem Review auf die gemeinsame Reservierung prüfen. Laufender Parent als normaler Job ist ausgeschlossen.
- [x] Konkurrenztests mit zwei Verbindungen, gleichzeitiger Abbruch-/Übergangsentscheidung und wiederholtem Start. Nach Crash zwischen Commit und Queue-Aufnahme darf beim Neustart kein Kind wiederholt werden.
- [x] Wiederanlauf markiert aktive Folge und Kinder unterbrochen; keine automatische Wiederaufnahme. Terminale Nachweise und Reservierungsfreigabe konsistent erhalten.

## S1c — Adapterfolge, UI und Gesamtprüfung

Dateien: geändert `governor_workbench/sequences.py`, `governor_workbench/sequence_store.py`, `governor_workbench/jobs.py`, `governor_workbench/server.py`, `governor_workbench/static/app.js`, `governor_workbench/static/style.css`, `tests/test_server.py`; neu `tests/test_sequence_controller.py`. Browserprüfungen liegen als temporäre Playwright-Skripte vor.

- [x] Schutztests für `/api/sequences/start` und `/api/sequences/cancel`, jeweils exakt den S1-Feldern entsprechend. Vorschauhash serverseitig vor Anlage rekonstruieren.
- [x] Gewöhnlichen `stage_test` ohne duplizierten Test-/Reviewcode starten. Vor jedem externen Modellaufruf Versand-/Routing-/Quellenbindung prüfen; am Schrittende wiederum auf Drift prüfen.
- [x] Nur bei echtem, aktuellem, vollständig verifiziertem Testerfolg einmal `pilot_assess` einreihen. Dort `evidence_usable` explizit auswerten; sonst gesperrt statt erfolgreich anzeigen.
- [x] UI: Vorschau, konkrete Folge/Modellversand/Haltepunkt, Pflichtbegründung, ausdrücklicher Start, Abbruch, Kindbelege und historische Endzustände. Kein automatischer Start durch Laden, Auswahl, Reparaturplanung oder Neuladen.
- [x] Echte temporäre HTTP-/Workerstrecke mit Mock-Modellen prüfen: genau zwei Kinder, unveränderte Zielbytes und keine Übernahme-/Planabschlusszeilen; bestehenden manuellen Übernahmeweg danach weiter funktionsfähig halten.
- [x] Alle S1-Haltebedingungen und Neustartgrenzen testen. Browsernavigation/CSRF, Syntax, JSON-Vertrag und Python-Gesamtsuite ausführen. Hermes-Nullwerkzeugprobe erneut prüfen, falls Integration/API-Payload geändert wird. Keine Live-Modellbewertung ohne separaten Auftrag.
- [x] Erst nach erfolgreichen Nachweisen Featurestatus, Wiederaufnahme und Betriebsvertrag aktualisieren. Allgemeine Planfolgen, weitere Adapter, Gesamtabnahme/Windows-Erstsetup bleiben offen.

Abnahme 17.09.2026: 536 Tests in 543,560 Sekunden; 534 bestanden, zwei ausgelassen. HTTP-/Workerstrecke, Browser, Syntax/Vertrag und Hermes-Nullwerkzeugprobe erfolgreich. Modelle in Ausführungstests simuliert; keine echten Produktaufträge. Zusätzlich gespeicherte Verifikation nach Drift entwertet und begrenztes Verwerfen abgewiesener HTTP-Anfragekörper getestet.

## Planung geprüft

- [x] Genehmigte Freigabegrenzen übernommen; erste Folge auf zwei bestehende Prüfaktionen beschränkt.
- [x] Konflikt mit nur einem aktiven Job erkannt und eigene Reservierung vorgesehen.
- [x] Aktuelle Job-/Nachweisidentitäten bleiben für bestehende Übernahmeprüfungen erhalten.
- [x] Keine Vermischung von gestagtem Test, eigenständigem Testschrittabschluss und Produktfreigabe.
- [x] Abbruch, Replay, Konkurrenz, Drift, Versand und historischer Zustand in Abnahme aufgenommen.
- [x] S1a abgenommen; S1b-Speicherung abgenommen: 518 Tests, 516 bestanden/zwei ausgelassen, Browser-/Syntax-/Vertragsprüfung erfolgreich. S1c abgenommen (536 Tests; 534 bestanden/zwei ausgelassen). Nur ein ausdrücklicher gebundener Start gestattet die feste Pilotfolge; Vorschau und Speicherhash allein gewähren keine Ausführung.
