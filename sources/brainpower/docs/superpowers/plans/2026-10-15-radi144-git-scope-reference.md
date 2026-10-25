# P3 – prozessgebundene Git-Prüfung und Kontextreferenz

Betreiberfreigabe: „Ja, gehe gerne weiter,,,“. Der konkrete Vorschlag aus dem vorherigen Halt ist genehmigt: nur den Prüfprozess für den exakten Radi144-Pfad konfigurieren, gezielt testen und unabhängig prüfen, dann zwei neue Referenzläufe. Originalalgorithmen und Liveinstanzen bleiben unverändert. Kein globaler Git-Eintrag, keine Wildcard und kein Ändern alter Nachweise.

Neuer Punkt: `checkpoints/Aurelia-P3-Radi144-Context-GitScope-20261015-072137Z`. Vorpunkt mit117 Manifestdateien/116 Archiveinträgen nachgerechnet;26 Anfangsdateien gesichert. Neue Gate-Datei geschlossen. Alte Laufkennung1 bleibt unangetastet; gleiche Labelnamen im neuen Punkt bezeichnen neue Versuche.

## Begrenzter Entwurf

Die bestehende `source_state()`-Prüfung erhält eine zentrale `git_read_prefix()`-Grenze. Sie prüft zuerst die gewöhnlichen Pfadkomponenten und den fest erlaubten absoluten Radi144-Pfad. Jeder Git-Leseprozess setzt nur über Argumente seine `safe.directory`-Liste leer und danach auf diesen einen Pfad. `core.fsmonitor=false` verhindert für diese Leseabfragen einen extern konfigurierten Dateiwächter. Keine `git config`-Schreibbefehle, keine Übernahme fremder Git-Konfigurationsvariablen, keine pauschale Repositoryfreigabe. Hashes, HEAD, Raw-XY, Hostpfad, Clean-env, frische Laufverzeichnisse, Fehler- und Nachprüfungen bleiben erhalten.

`context_probe.py` und dessen13 synthetische Tests werden bytegleich übernommen. Originalumfang bleibt exakt acht AST-Definitionen, zwölf Gruppen; native Typ-Double und In-Memory-Grenzen statt echter Pydantic-/HTTP-/Store-/Engineausführung. Keine numerische Reparatur.

## Reihenfolge und Besitz

1. [x] Vorpunkt rücklesen, neue Freigabe, Quellen, vier Werkzeugfassungen und drei Statusdokumente sichern. Root besitzt Controller, Pläne, Ausführung und Abschluss.
2. [x] Luna/max besitzt ausschließlich neuen `test_ROOT_controller.py` und eigene neue Rot-/Grünbelege: Prozessargumente/kein Persistieren, fremder Pfad und Reparse-Abwehr, nur erlaubte Leseabfragen. Keine Originalaufrufe; zuerst Rot gegen unveränderten neuen Controller. Kein paralleler zweiter Schreiber.
3. [x] Root implementiert minimale Controlleränderung, prüft Rotursache und aktuelle gesamte synthetische Suite; vier Dateien einfrieren. Astra/medium prüft SPEC→QUALITY der tatsächlichen Hashes.
4. [x] Erst danach Gate öffnen: neuer context-run-1, nur bei Erfolg context-run-2. Bei unerwartetem Fehler keine Wiederholung; Gate auch bei Abbruch schließen.
5. [x] Vollständige Ergebnisse ausschließlich ohne Label vergleichen; exakte Quellen-/AST-/Werkzeug-/HEAD-/Raw-XY-Bindung und aktuelle Fehlerausgaben auswerten. Unabhängiger Ergebnisreview, bekannte Originalbefunde unverändert führen.
6. [x] Bericht, Hauptplan und Wiederaufnahme konsolidieren; lokaler Vorher-/Nachherpunkt mit Manifest, ZIP-Einzelhashes und Rücklesen. Gesamt-P3, P4-Siebenermatrix einschließlich Aurelia/Modul_Templates vor P5 und P6–P8/S4.8 bleiben getrennt.

Werkzeugtests: vorhandenes Radi144-Python mit `-I -S -B -m unittest discover -s . -p test_*.py -v`, bereinigte Umgebung, keine Originalmodule/-körper. Rot-/Grünfassungen jeweils als Bytes mit Kommando, Exit und Ausgaben erhalten. Alte Prüfpunktdateien werden nicht verändert.

## Tatsächlicher Abschluss

23 aktuelle Werkzeugtests ohne Skips bestanden. Zwei neue Läufe je12 Gruppen/42 Erwartungen; vollständiger Berichtvergleich ausschließlich ohne Label gleich, kanonischer Hash8929b240cad50ea6d445bf74f57f8024457d3301f10d5fdc771aea1cfb1bb536. Astra/medium eingefrorener Vorreview und unabhängiger Ergebnisreview ohne materiellen Blocker. Quellen/AST/Werkzeuge/HEAD/benannter Raw-XY vor/nach gleich, Gate Originalbytes geschlossen. Alter Punkt unverändert. Bericht `docs/verification/AURELIA_P3_RADI144_KONTEXT_GITSCOPE_2026-10-15.md`; tatsächlicher Sicherungsschluss nur durch FINAL-READBACK. Kein Gesamt-P3 oder Produktfix. Ein LF-only-Wrapper-Vorhalt vor Teststart wurde nach Readback der ursprünglichen CRLF-Bytes korrigiert; kein Referenzretry.
