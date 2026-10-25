# P3: Validierung persistierter Morphic-Auftragsdaten

Freigegebene serverunabhängige Referenzfortsetzung. Dieser Block ergänzt die bisherigen Rohobjekt-/Recoveryproben durch den tatsächlichen Parser, ohne Auftragsdateien oder echte Worker zu öffnen.

## Umfang und Schutzgrenzen

- Referenz `C:/morphic_v1/.worktrees/operator-workbench-phase1`, HEAD `151e2bb0a69d49677a0b1e40e0bffd0f172d34c4`. Keine führende Produktquelle gewählt.
- Zwei benannte Quellen: `services/harmonization_worker.py` und `apps/web/authority_ids.py`. Vollständige Bytebindung vor/nach. Keine Modulinitialisierer, JOBS_DIR-Anlage, psutil-/Hardware-/Webimporte oder echte Prozess-/Netz-/Dateiaktionen aus den Funktionsproben.
- Originalparser und seine tatsächlich benötigten reinen Helper/Autoritäts-ID-Regeln verwenden. Das Dataclass-Feldmodell darf kontrolliert aus Original-AST übernommen werden; genaue Klassen-/Decorator-/Annotationsextraktion vor Ausführung prüfen. Kein permissiver Autoritäts-Dummy und keine ersetzte Parserlogik.
- Nur synthetische Eingaben. Dateilesen/-speichern, Locks, HTTP, reale Persistenz, Workerstart und Restore bleiben außerhalb des Nachweises. Ein bestandener Negativfall belegt die konkrete Ablehnung, keine allgemeine Sicherheitsabnahme.
- Neue Werkzeuge/Belege ausschließlich `checkpoints/Aurelia-P3-Morphic-Record-20261014/`; Produktquellen, normative Templates, Liveinstanzen und Governors unverändert.

## Schritte

- [x] Quellen/Git frisch gebunden: 19 relevante Dateien unverändert, HEAD und getrackter Zustand gleich. Vorigen 41-Dateien-Prüfpunkt samt Siegel rückgeprüft; neuer Vorherpunkt `checkpoints/Aurelia-P3-Morphic-Record-Status-20261014-164313Z`. Statischer Aufrufvertrag und 27 Feld-/sechs Methoden-Metadaten aufgenommen.
- [x] Luna/max: statischer Parser-/Feld-/Helpervertrag und Werkzeug vorbereitet; zwölf synthetische Tooltests grün. Keine Originaldefinitionen vor Review ausgeführt. Historische Nachweislücke: keine v1-Bytekopie oder dauerhaft gespeicherte rote Entwicklungsläufe; nur v1-Hashes/Root-Grünprotokoll und Reviewbefunde erhalten. Kein vollständiger TDD-Nachweis behauptet. Tatsächlich ausgeführte v2-Bytes vor Ausführung gesichert.
- [x] 24 benannte Fallgruppen einschließlich v2, Legacy, Schema/Felder/IDs, Zahlen, Hardware-JSON, Zeit/Status/Phase/Fortschritt und Autorität. Explizite Unterassertions zählen nicht als weitere Gruppen.
- [x] Leitung: zwölf Werkzeugtests vor/nach Korrektur; Astra SPEC→QUALITY vor Ausführung. Drei blockierende Erwartungsfehler und zwei Qualitätsbefunde korrigiert, v2 neu gehasht und geprüft. Originalcode unverändert.
- [x] Zwei frische Läufe je24 Gruppen, vollständige Ergebnisse gleich. 19 Quellen, zwei Werkzeuge, HEAD und getrackter Zustand unverändert. Negative `-O`-Probe vor Quellenlesen abgelehnt.
- [x] Unabhängiger Ergebnisreview ohne Restblocker im begrenzten Scope; Befunde/Grenzen im Prüfbericht für P4. Keine DB-Technik, neue Formel oder Produktreparatur ausgewählt.
- [x] Benannter Vorher-/Nachherumfang rückgeprüft, historischer Wiederaufnahme-Bytesuffix erhalten. FINAL-MANIFEST.json und FINAL-VERIFICATION.json binden den abgeschlossenen lokalen Prüfpunkt; keine Gesamtphase-/Serverabnahme.

Prüfbericht: `docs/verification/AURELIA_P3_MORPHIC_RECORD_VALIDIERUNG_2026-10-14.md`. Werkzeug-/Ergebnisumfang: `checkpoints/Aurelia-P3-Morphic-Record-20261014`; neuer Statusprüfpunkt: `checkpoints/Aurelia-P3-Morphic-Record-Status-20261014-164313Z`. Abschluss ausschließlich durch tatsächlichen erfolgreichen Manifest-Rücklesebeleg, kein F:-Gesamtbackup.

Gesamt-P3, RF-E1, Linux-/Backendpfade und verbindliche Morphic-Quelle bleiben offen. P4 vollständige siebenmodulige Matrix vor P5 Datenstrukturentscheidung; normative Abstimmung und Integration P6–P8/S4.8 unverändert.

Modellarbeit: Luna/max begrenzte Vorbereitung, Astra/medium unabhängiger Review; Leitung führt tatsächliche Proben aus. Orientierung 45–90 Minuten ohne Qualitätsbegrenzung. Desktop-Leitmodell oder App-Routing werden nicht aus gespeicherten Defaults abgeleitet oder geändert.
