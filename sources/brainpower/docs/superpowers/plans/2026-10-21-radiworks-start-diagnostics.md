# RadiWorks V5 – begrenzte Start-/Stopfehlerbelege

> Umsetzung nach vorhandener Betreiberfortsetzungsfreigabe: getrennte lokale Vorbereitung, Tests und unabhaengiger Review. Keine native Aktivierung oder neue Materialfreigabe.

**Ziel:** Den betroffenen Start-/Stoppschritt und einen festen, datenarmen Fehlergrund erkennen, ohne Startverhalten, Grenzwerte oder Produktalgorithmen zu aendern.
**Architektur:** Kopie des eingefrorenen V4-Kandidaten in `runtime/rw-material-v5-20261021`. Ein kleines Modul `start_diagnostics.py` laesst erfolgreiche Aufrufe unveraendert und fuegt Fehlern ausschliesslich erlaubte Kennungen hinzu. Lokale Kopie des gebundenen `remote_common.py`; dessen bestehende Pruefbedingungen bleiben gleich. `receipt_validation.safe_worker` und `linux_admission.Runtime.start` uebernehmen nur freigegebene Metadaten.
**Technik:** Python-Standardbibliothek; isolierte lokale Unittests mit synthetischen Daten. Keine SSH-Ausfuehrung, Installation, Hintergrundaufgabe oder kostenpflichtiger Scan.

## Befund und abgegrenzte Entscheidung

V4-Diagnose: paketpassender Startbeleg und Startfehler `RuntimeError`; Cleanup separat `RuntimeError`/Exit1. Aktuell Service nicht geladen, Slice inaktiv, eigene Cgroup abwesend. Exakte historische Fehlerstelle unbekannt. `remote_common.run` verwirft fuer Aussenbelege Kommandoexit und Grund; `limits` und `props` verwenden denselben Fehlertyp. Kein historischer Material-/Erhaltungsnachweis.

Ausgewaehlter Ansatz: additive feste Stufen und Gruende an den bestehenden Fehlergrenzen. Freie stderr-/Journaltexte wuerden mehr Daten offenlegen; ein weiterer unveraenderter Start koennte denselben unspezifischen Beleg erzeugen. Beide Alternativen sind hier nicht vorgesehen. Die neue Erfassung ist keine behauptete Behebung der unbekannten nativen Ursache.

## Vertrag

- Neue Identitaet: `/srv/aurelia-build-r2-1/fs/work/material-intake-20261021-v5`, `rwmaterialdiagv5.service`, `rwmaterialdiagv5.slice`. Alte Verzeichnisse/Units/Marker nicht anfassen.
- `failure_stage`: `start_entry`, `slice_create`, `slice_limits`, `slice_empty`, `argument_bound`, `service_start`, `fragment_slice_query`, `fragment_service_query`, `fragment_slice_path`, `fragment_service_path`, `fragment_size`, `cleanup_stop`.
- `failure_reason`: feste Codes fuer Kommandoexit, Ausgabegrenze, Unit-Abfrage, Kernel-Limitabweichung und bekannte Ausnahmegruppen; keine freien Texte.
- `command_exit_code`: nur echter Integer, nicht Boolean, -255..255, ungleich0, ausschliesslich bei Kommando-/Unit-Abfragefehler. Weder argv noch stdout/stderr, Token, URL oder Umgebungswerte ausgeben.
- Erfolgreiche Cleanup-Kommandoausgabe wird verworfen; im Fehlerbeleg bleibt nur exit_code0/resultnull statt freiem stdout. Urspruengliche Ausnahme unveraendert erneut ausloesen; primaerer Fehler und Cleanup getrennt erhalten. Fehler beim Belegschreiben weiterhin separat markieren. Kein Retry, kein tolerierter Fehler, keine neue Lifecycle-Aktion.
- Unveraendert: sieben gebundene Layer382717142B, alle Hash-/Framing-/TLS-/IPv4-/Speicher-/Erhaltungspruefungen, Limits/Zeiten und Stopsequenz.

## Schritte

- [x] **1. Basis sichern:** alle59 V4-Belege hashen; erforderliche Quell-/Testdateien und Preservation-Vorgabe bytegleich exklusiv kopieren. `COPIED_BASELINE.json` bindet Ursprung und Kopien.
- [x] **2. RED nachweisen:** `test_start_diagnostics.py` zuerst schreiben. Simulierter Slice-/Servicefehler muss fehlende `failure_stage`/`failure_reason`/Exitcode im alten Beleg aufdecken. Weitere Tests pruefen Cleanup-Trennung, keine Geheimtextausgabe, unveraenderte Primaerausnahme und Aufrufreihenfolge.
  Befehl: `python -I -S -B -m unittest discover -s runtime/rw-material-v5-20261021 -p test_start_diagnostics.py -v`. Erwartet: explizite Assertions wegen fehlender Metadaten, keine Import-/Fixturefehler. RED-Beleg exklusiv erhalten.
- [x] **3. Minimal implementieren:** `start_diagnostics.py` mit Allowlisten, `require`, `mark` und `metadata`; `remote_common.py` nur drei Fehlergrenzen in `run`, `props`, `limits` ergaenzen. In `linux_admission.py` Stufen vor bestehenden Aufrufen setzen und in `start()` primaere/sekundaere Fehler kennzeichnen. In `receipt_validation.py` ausschliesslich erlaubte Felder an Fehlerantwort anfuegen.
  Erfolgsantworten, akzeptierte Bedingungen und Reihenfolge unveraendert. Beispiel fuer eine Grenze: `diagnostics.require(r.returncode == 0, original_message, 'command_exit', r.returncode)`; `require` laesst Erfolg durch und versieht denselben RuntimeError bei Fehler mit erlaubten Attributen. `metadata` prueft Typ/Werte und gibt sonst keine Zusatzfelder aus.
- [x] **4. Vollstaendig verifizieren:** neue Fehlerszenarien und bestehende Kandidatensuite. Rueckgabecode0, keine Fehler/Skips, unveraenderte Quellen vor/nach Test; Rohbeleg und EOL-normalisierte Auswertung unterscheiden. Erzeugte Skripte reproduzierbar, maximal262144Bytes, Module und Einstiegspunkte gebunden. Transport bei Nichtnull-Exit: nur strikt geparste Fehlerantwort exit_code1 und erlaubte Fehlerfelder erhalten; accepted/launch_acknowledged/worker_completed/transport_succeeded bleibenfalse, remote_stateunknown. Widerspruechliche Erfolgsmeldungen/ungültiges JSON verwerfen, keine Rohtexte speichern. Eigener RED-/GREEN-Beleg in test_failure_transport.py. Kein Ausfuehren generierter Start-/Statusprogramme.
- [x] **5. Neue Identitaet/generiertes Paket:** `prepare_material.py` laedt lokales `remote_common.py` und `start_diagnostics.py` in korrekter Reihenfolge. Neuer Path/Unit/Package in Kopien und Transportpins. `review_tools/build_package.py` erzeugt lokal; Transport bleibt bis zu separatem Gate unbenutzt. Alle unveraenderten Modulbytes separat vergleichen.
- [x] **6. Unabhaengig pruefen und sichern:** Astra/medium prueft konkrete Diffs, Fehlerszenarien, Output-Allowlisten, Generator/Transportbindung und unveraenderte Gates. Materielle Befunde erst korrigieren. Ergebnis/Index und `docs/SERVER_AKTUELL.md` mit genauen Restgrenzen aktualisieren. Alle alten Evidenzbaeume erneut pruefen.
- [ ] **7. Gesondertes natives Folgegate:** Erst nach sauberer Vorbereitung konkrete Vorpruefung und ggf. neuer Materiallauf besprechen/freigeben. Dieser Plan erteilt weder einen neuen SSH-Aufruf noch Start-, Cleanup-, Import-, Container- oder Buildfreigabe.

## Abnahme und Grenzen

Die Vorbereitung ist nur bei passenden lokalen Tests, aktuellem unabhaengigen Review und unveraenderten alten Belegen abgeschlossen. Native Fehlerursache und Erfolg bleiben bis zu neuer geeigneter Evidenz unbekannt. Gemeinsamer Kernel/UID, nicht atomare Beobachtungen, bestehende Remote-Capture-/Timeoutgrenzen und rootless-AppArmor-Grenze bleiben ausgewiesen. Kein 25-Nutzer-Kapazitaetsnachweis und keine Aurelia-Integrationsfreigabe.

## Sicherungspunkt21.10.2026

Auf Betreiberwunsch nach lokalem V5-Abschluss pausiert.143Tests ohne Skips bestanden;35Quellbindungen und4externe Test-/Manifestbindungen vor/nach dem letzten Lauf gleich. Astra/medium-Review ohne materiellen Befund. Fehlerbeleg der unvollstaendigen stat-Testattrappe erhalten, nur Fixture korrigiert.176alte Evidenzeintraege unveraendert. Kandidat und Wiederaufnahme in `runtime/rw-material-v5-20261021/RESULT.json`/`INDEX_ALL.json` gebunden. Kein nativer Aufruf. Schritt7offen: zuerst lokale V5-Vorpruefungssteuerung mit eigenen Tests/Review vorbereiten; vier geerbte Wrappertests pruefen weiterhin den historischen V4-Wrapper. Danach nur mit passendem neuen Gate weiter.
