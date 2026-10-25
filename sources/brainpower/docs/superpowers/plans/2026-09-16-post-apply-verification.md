# Nachprüfung nach Pilotübernahme

Ziel: ausdrücklich angeforderter, lesender Nachweis nach tatsächlicher Übernahme als Grundlage technischer Abschlussadapter. Stdlib-Python, bestehender einzelner Worker und geschützte API; keine neuen Modellaufrufe.

Entscheidung innerhalb des freigegebenen Pakets 2: Ein späterer Dateiabgleich benötigt einen eigenen datierten Bericht. Wiederverwendung der Vorher-Prüfung würde beabsichtigte Dateiänderungen ablehnen; automatische Bestätigung des neuen Scope wäre dagegen unbelegt. Deshalb getrennte Prüfungen für Transaktion, bisherigen Test, Auswahl und Dateien; aktuellen Scope separat berichten, keine Abschluss-/Folgefreigabe erteilen.

- [x] Regressionstests für echte temporäre Übernahme, nachträgliche Dateiänderung, Rücknahme, neue Testversuche, Auswahländerung, Manifestdrift und Abbruch.
- [x] `pilot_verification.py`: begrenzter lesender Nachprüfungsbericht; IDs/Hashes aus Journal statt Browser, Manifest-/Root-/Dateiprüfung, alle versiegelten Dateien einschließlich unveränderter Dateien. Aktueller Scope ist eine Beobachtung, keine automatische Übernahme neuer Planquellen. Dateivergleich ersetzt keinen Funktionstest im Ziel.
- [x] `jobs.py`, `server.py`: striktes POST `/api/pilot/verify` nur mit transaction_id, über vorhandenen Worker. Ergebnis dauerhaft im Jobjournal; Diagnoseausführung und positiver Nachweis getrennt.
- [x] `static/app.js`: explizite Nachprüfung am abgeschlossenen Transaktionsbeleg, datierter Bericht und klare Grenzen. Alte Berichte bleiben historische Beobachtungen; keine Freigabe durch Anzeige.
- [x] Gezielte Tests, relevante Gesamtsuite und Browser-/Syntaxprüfung. Dokumentation mit belegtem Stand und verbleibenden change/test-Abschlussgrenzen aktualisieren.

Nicht enthalten: allgemeiner test-Schritt-Adapter, fachliche Anerkennung eines Scope-Übergangs nach Änderung, automatische Schrittfolge, Produktfreigabe, Server-/SMB-Zugriff. Diese bleiben nächste Teile von Paket 2 beziehungsweise nachgelagerten Paketen.
