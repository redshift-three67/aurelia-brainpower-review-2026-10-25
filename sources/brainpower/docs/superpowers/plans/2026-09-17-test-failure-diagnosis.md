# Gebundene Fehlerdiagnose vor Reparaturaufträgen

Genehmigte Fortsetzung von Paket 3. Ein expliziter lokaler Workerauftrag prüft einen fehlgeschlagenen eigenständigen Test: neuester Versuch, aktuelle Auswahl/Quelle/Vorgänger, Adapter und Original-/Staging-Dateien. Er erstellt einen datierten Bericht mit Diagnoseklasse, konkreten nächsten Schritten, Testbudget und begrenztem ausdrücklich markiertem Logauszug samt Hash/Quellauftrag. Keine Behauptung einer automatisch erkannten Fehlerursache.

Warum dieser Schritt: ungeprüfte historische Fehler dürfen keine Reparatur auslösen. Ein bloßer Wiederholungsbutton erfüllt die Quellenbindung nicht; eine sofortige Modellreparatur würde eine neue Freigabe-/Kontextübertragung benötigen. Die lesende Diagnose nutzt vorhandene Nachweise und wird Grundlage späterer ausdrücklicher Reparaturplanung.

- [x] Regressionstests: aktueller Fehler, Drift, Adapter/Selektion/Vorgänger, neuer Versuch, fehlende Runnerbelege, Erfolg, Budget, Logkürzung und Abbruch.
- [x] Neues test_failure.py, strikte API und einzelner Worker; keine Produktänderung oder Modellanfrage.
- [x] Fehlerbericht in Aufträgen mit erneutem Prüfen; alte Berichte klar historische Beobachtung.
- [x] HTTP, Browser, Syntax, gezielte und vollständige Tests; Fortschritt dokumentieren.

Verifiziert: 22 gezielte Tests einschließlich echter HTTP-Diagnose bestanden. Gesamtsuite unter Python 3.12: 474 Tests in 305,417 Sekunden, 472 bestanden und zwei ausgelassen. Chrome mit simulierten API-Daten prüft Fehlerschaltfläche, exakte Auftragsbindung, Bericht, erneute gesperrte Prüfung nach Drift, Neuladen und reine Textdarstellung von Loginhalt; keine JavaScript-Fehler. Python-Kompilierung, JS-Syntax und JSON-Vertrag geprüft. Governor läuft, automatische Modellreviews aus, Supervisor Astra, keine aktiven Aufträge.

