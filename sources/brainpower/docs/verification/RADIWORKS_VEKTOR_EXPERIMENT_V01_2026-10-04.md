# RadiWorks Kontext, Suche und Experimentalmodus — 04.10.2026

Status: Betreiber hat diese Richtung genehmigt; VF-2/VF-3/EXP-1 sind noch nicht implementiert. GV-2 und seine isolierte Prüfung haben Vorrang. Bestehender Originalmodus bleibt erhalten. Quellenhashes: runtime/rw-gv2-20261004/REFERENCE_SOURCES.json; Radi144-Prüfung auf HEAD b8ac33a mit sauberem gezielt geprüftem Quellstand.

## Empfehlung

1. **Katalogsuche (VF-3)**: Fokus und bewusst gewählte Themen liefern erklärbare Vorschläge auf Basis tatsächlicher Katalognamen/Inhalte. Begründung und Suchbegriffe anzeigen; Nutzer bestätigt Datenbank. Persönliche Identität allein ist kein geeigneter Suchbegriff. Eine Katalogauswahl ändert keine laufende Sitzung. Keine Behauptung semantischer KI bei Hash-/Wortfrequenzverfahren.
2. **Persönlicher Kontext (VF-2)**: Vorname, Nachname, Geburtsdatum, Ort, Fokus, optionales Bild getrennt erfassen; stabile zufällige Fall-ID, Scope separat. Fehlende Daten bleiben fehlend. Aus alten freien Fallnamen keine Identität erraten. Datum und Text klar normalisieren; Originaleingaben aufbewahren. Bild lokal, Format/Größe/Decoder begrenzen; Hash ist keine Anonymisierung.
3. **Auftragssnapshot**: Bei neuem Analyseauftrag Kontextversion einschließlich Fokus und optionalem Bildhash einfrieren, serverseitig fall-/session-/jobgebunden. Für Promotion unverändert referenzieren. Falländerung wirkt nur auf neue Aufträge; keine heimliche Neuberechnung oder Austausch laufender Broadcasts. Native Originalsignatur und experimentelles Ergebnis getrennt speichern.
4. **EXP-1**: ausdrücklich wählbarer Radi144-Vektor-Experimentalmodus mit formula_version, Parametern, Quellenhash und festem Zeitbezug. Zwei getrennte Sitzungen vergleichen, gleicher Kataloghash und Ausgangsentropiestand. Kein automatischer Moduswechsel, keine Migration bestehender Fälle. Rückwechsel zum Original ohne Datenverlust. Standard bleibt Original.

## Radi144-Befunde und Übernahmegrenzen

- app/api/resonance.py: persönliche Signatur wird für einen Datenbankvergleich einmal erzeugt und wiederverwendet; Fokus fließt gewichtet in den Zielvektor ein.
- app/algorithms/resonance_engine.py: Fokus-Embedding basiert auf MD5/PRNG und Textelementen. Dies ist eine Rechenheuristik, kein semantisches Sprachmodell und kein physischer Messwert.
- app/algorithms/client_signature.py: Name, Datum, Bild, optionale Komponenten und organ_clock wirken auf die Signatur. Der implizite aktuelle Zeitpunkt wird nicht ungeprüft übernommen: standardmäßig aus; bei Nutzung expliziter unveränderlicher Zeitpunkt in eigener Formelversion.
- Bildkomponenten sind Datei-Hash, RGB/HSV und Pixelentropie; keine Bilddiagnose. Die bisherige alternative Bild-/Textauswahl ist kein Nachweis, dass sämtliche persönlichen Komponenten gleichzeitig verarbeitet werden.
- Radi144s verkürzte SHA-1-Registerkennung ohne Tenantbezug ist keine geeignete Aurelia-Fall-ID. SHA-1/MD5 höchstens gekapselte Formelnkompatibilität, niemals Datenschutz-/Sicherheitsnachweis.
- Archivierte Zusammenfassung ist kein vollständiger rekonstruierbarer Vektor. Experimental-Snapshot muss deshalb Komponenten, Normalisierung, Parameter, Version und Zeitpunkt nachvollziehbar erfassen.
- Vorhandene Dummy-Engine-Tests beweisen keine fachliche Qualität des Rankings. Gezielte deterministische Vergleichs-, Grenz-, Isolation- und Regressionstests bleiben Pflicht.

## Reihenfolge / Abnahme

GV-2 → VF-2 → VF-3 → EXP-1 → eigenständige Betreiberprobe. Für EXP-1 vor Umsetzung genaue Formel/Parameter pinnen und ursprünglichen Ergebnisweg als Regression erfassen. Wissenschaftliche Wirksamkeit wird daraus nicht abgeleitet. Aurelia-Hostvertrag, Mehrmandantenautorität, Wiederherstellung und Integrationsfreigabe bleiben eigene Gates. Keine CUDA-/Kozyrev-/Hardwareabhängigkeit wird mit diesem Beschluss eingeführt.


## Plattformweite Betreibergrenze — 04.10.2026

Bestehende stabile Algorithmen und Heuristiken bleiben die Grundlage für RadiWorks und sämtliche aktuellen/künftigen Aurelia-Module. Keine semantische KI-Suche, neuen Embeddings oder anderen Analyseverfahren ohne ausdrückliche vorherige Besprechung. VF-3 nutzt erklärbare Katalog-/Wort-/Themenheuristik; EXP-1 bleibt der ausdrücklich genehmigte, getrennte Radi144-Heuristikmodus. Nicht automatisch auf andere Module ausweiten. Änderungen ergänzen bestätigte Funktionen; keine verdeckte Ersetzung.
