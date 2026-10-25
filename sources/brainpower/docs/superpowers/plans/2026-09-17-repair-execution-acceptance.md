# Durchgängige Abnahme der ausdrücklichen Pilot-Reparatur

Genehmigte Fortsetzung von Paket 3. Bestehende Ausführungswege gemeinsam prüfen, bevor neue Ausführungsrechte oder Automatik ergänzt werden. Ziel: echter fehlgeschlagener lokaler Test → gebundene Diagnose → modellgeprüfter Reparaturplan (Modelle simuliert) → separate HTTP-Auswahl → Änderungsvorschlag → isolierter Test/Review → separate Übernahme → Abschluss/Quellenübergang → Folgetest/Review → Rollback.

- [x] Vorhandene HTTP-Pilotpipeline um echte Reparaturherkunft erweitern; Auswahl vor Änderung zwingend prüfen, unveränderte Testdatei und korrigierte Quelldatei nachweisen.
- [x] Im Auftragsbericht Reparaturherkunft und notwendige separate Auswahl sichtbar machen.
- [x] Durchgängigen Ablauf, JS/Browser und Gesamtsuite prüfen; Nachweisgrenzen und nächsten offenen Teil dokumentieren.

Temporärer Pilot mit `calc.py` und unverändertem Regressionstest. Keine echten Produkt-/Serveränderungen, keine Modellanfragen. Dieser Nachweis deckt manuell einzeln freigegebene Reparatur ab, keine automatische Folgeausführung und keine Modellqualitätsabnahme.

Abnahme: 482 Tests / 480 bestanden / zwei ausgelassen (423,172 s). Browsernavigation, JS-/Python-Syntax und JSON-Vertrag geprüft. Testtransport-Verbindungsabbau und begrenzte Wartefristen korrigiert; Produktionslimits unverändert. Details und Nachweisgrenzen im aktuellen Wiederaufnahmestand.
