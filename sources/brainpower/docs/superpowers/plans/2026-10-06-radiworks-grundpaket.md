# RadiWorks Grundpaket M1–M6

Freigegeben am 2026-10-06 durch den Betreiber. Ziel: Original und bestätigtes EXP1 erhalten; getrennte Verfahren/Zufallsmodi, unveränderliche Auftragsbezüge und nachvollziehbare persönliche Analysen ergänzen. Keine Aurelia-Integrationsfreigabe.

Architektur: isolierter Kandidat `runtime/rw-basepackage-20261006` aus dem geprüften C23-Release; getestete Entropie-Backoff-Änderung als dokumentierter Delta. Liveports 8103–8109 und 8110 bleiben während Entwicklung unverändert. Isolierte Prüfung ab 8111. Python/FastAPI, bestehendes Vanilla-JS; bestehende CPU-Heuristik unverändert versioniert.

## M1 Ausgangspunkt
- [x] C23 und Backoff-Manifest vollständig verifizieren, separate Entwicklungskopie erstellen.
- [x] Produkt, Startkonfiguration, Katalog und gespeicherte Daten unter F: mit Zeitstempel sichern; SQLite über Backup-API. Schlüssel bleiben extern. Laufende Broadcastzustände im RAM sind ausdrücklich kein Bestandteil eines atomaren Wiederanlaufs.
- [x] Baseline mit vorhandenen Engine-Tests und gesonderten CPU-Tests prüfen. Alte Fälle/Sitzungen/EXP1 bleiben unverändert.

## M2 Fall- und Auftragsbezug
- [x] RED: Falltitel aus Vorname/Nachname/Geburtsdatum/aktivem Ort/Fokus; Teilfelder, Pfadzeichen, lange Texte, alte Fälle, Umbenennung ohne neue Datei/ID.
- [x] GREEN: `core/personal_context.py`, `core/cases.py`, `api/routes.py`, `webapp/js/views/cases.js` und Fallformular: explizites Titelverfahren, Vorschau, stabile Speicherung, keine stille Altfallumbenennung.
- [x] BC1 RED: Promote, Direkt, Auto und Bild binden gültigen unveränderlichen Kontext/Quelle; Wechsel/Neustart/Legacy und Konkurrenz geprüft.
- [x] BC1 GREEN: `core/broadcast.py`, `core/draft.py`, `core/automode.py`, `api/routes.py`, `main.py`; historische/aktive Einträge unverändert, keine neue numerische Broadcastformel.
- [x] Unabhängige Astra-Prüfung der Identitäts-/Auftragsgrenzen, danach Fehlerbehebung und Regression.

## M3 Auftragsspezifische Entropie
- [x] RED: eigene RNG je Auftrag, Seed-Replay, stochastischer Wiederanlauf mit Journal, parallele Fälle ohne gemeinsame Ziehfolgen; Quellen/Fallback klar.
- [x] GREEN: `entropy.py`, `entropy_journal.py`, Auftragskontext/Broadcastcontroller; getestete 60s Fehlerpause übernehmen, Original reproduzierbare Ergebnisse erhalten.
- [x] Verifikation: Original + beide Zufallsmodi, Abbruch und Neustart; keine behauptete Hardware-Entropie für OS-Fallback.

## M4 Persönliche Heuristik
- [x] RED: vollständige Ratenliste/Pages mit begrenztem Budget, Abbruch/Parallelbetrieb/Journal-Replay; vorhandene EXP1-Vergleiche unverändert.
- [x] GREEN: getrennte versionierte persönliche Auftragssteuerung aus vorhandener Radi144-CPU-Heuristik. Keine neuen Gewichte, keine semantische KI-Suche.
- [x] Reproduzierbar/stochastisch je Auftrag; Matrixscores getrennt von Original EW/GV. Bewusste Ratenwahl für Broadcast mit gleichem Kontext, keine beliebige persönliche Resonanzformel.

## M5 Bedienung und Abnahme
- [x] Zwei Auswahlen: Verfahren Original/persönlich und Zufallsmodus reproduzierbar/stochastisch. Änderungen wirken nur für neue Aufträge; Sitzungen erklären Modus/Quelle/Kontext.
- [x] Engine-, CPU-, JavaScript- und synthetische Browserprüfungen aller vier Kombinationen, Grenzfälle/Isolation/Neustart/Historie.
- [ ] Nutzerabnahme des nachgewiesenen Kandidaten. Keine Freigabe durch Modellantwort.

## M6 Synchronisierung und Abschluss
- [ ] Nach bewiesenem Kandidaten: kanonische RadiWorks-Quelle und Modul_Templates-Verträge synchronisieren; geprüfte Versionierung/Portable5 und zeitgestempelte Sicherung.
- [ ] Dauerinstanzen nur am erlaubten Übernahmezeitpunkt aktualisieren; Fälle erhalten, aktive Jobs nicht umdeuten. Optionales danach separat entscheiden.
- [ ] Erst danach Datenbankstruktur besprechen. S4.8 bleibt geschlossen.

## Nachweise
Testlogs und Quellprüfsummen im Kandidaten/evidence. Statusmeldungen nennen tatsächliche Modelle, prüfbare Teilpaketfortschritte und Grenzen. Prozente beziehen sich auf diese Prüfpakete, nicht auf Wirksamkeit oder die Gesamtplattform. Kein neuer echter Hermes-Modellauftrag ist durch diese Umsetzung impliziert.

Aktueller Nachweis: docs/verification/RADIWORKS_GRUNDPAKET_KANDIDAT_2026-10-06.md. Technische M5-Prüfung abgeschlossen; Nutzerabnahme und M6 offen.
