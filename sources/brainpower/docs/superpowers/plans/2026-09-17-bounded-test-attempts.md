# Begrenzte Testversuche – Umsetzungspaket

Ziel: erster begrenzter Baustein von Paket 3. Bestehende ausdrückliche Testaufträge erhalten ein Limit, Doppelschutz und sichtbare Historie. Keine automatische Reparatur, Modellanfrage oder Ausführung von Folgeschritten.

Entscheidung: drei journalisierte Versuche je unveränderlicher Planrevision und Testschritt, unabhängig von erneuter Auswahl. Alle Zustände zählen, auch Abbruch/Unterbrechung. Ein neues Budget erfordert einen neuen Plan. Gegenüber unbegrenzten Wiederholungen ist der Aufwand damit begrenzt; gegenüber automatischen Wiederholungen bleibt jeder Start bewusst. Aktive Versuche verhindern einen zweiten Auftrag. Vor Ausführung prüft der Worker Budget und neuesten Auftrag erneut; Quellen-, Auswahl- und Vorgängerprüfung bleiben erhalten. Bestehende erfolgreiche historische Belege werden nicht allein wegen ausgeschöpftem Budget ungültig.

- [x] Tests zuerst: Limit, Abbruch zählt, Doppelschutz, Ausführungsprüfung, neuer Plan unabhängig, erneute Auswahl setzt nichts zurück.
- [x] plan_tests.py: lesende Budget-/Historienfunktion und Workerprüfung; jobs.py: atomare Admission unter bestehendem Runnerlock.
- [x] plans.py und app.js: verwendete/verbleibende Versuche, begrenzte Historie, eindeutiger Sperrgrund; API bleibt strikt.
- [x] Relevante Tests, HTTP, JavaScript und Browser; Gesamtsuite, Dokumentation und Wiederaufnahme.

Stdlib/Vanilla-JS, keine neuen Produktionsabhängigkeiten oder Datenbankmigration. Keine Produkt-, Server- oder SMB-Änderungen. Automatische Modellreviews aus; Medium bleibt Standard.

Verifikation: 37 gezielte Tests einschließlich echtem HTTP-Ablauf bestanden. Gesamtsuite unter konfiguriertem Python 3.12: 461 Tests in 280,078 Sekunden, 459 bestanden und zwei ausgelassen. Chrome mit simulierten API-Daten: Budget/History, exakte Testanfrage, gültiger dritter Erfolg und Sperre weiterer Starts geprüft, keine JavaScript-Fehler. Python-Kompilierung, JS-Syntax und JSON-Vertrag geprüft. Keine echten Produktabnahmen oder Modellaufrufe.

