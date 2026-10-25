# S2a — Schreibfreie Vorschau genehmigter Testketten

> Umsetzung inline mit executing-plans und test-driven-development; keine Delegation. Betreiber hat den S2-Entwurf und S2a ausdrücklich bestätigt.

**Ziel:** Zwei bis fünf ausgewählte Testschritte eines unabhängigen Piloten mit deterministischer Reihenfolge, aktuellen externen Vorgängern und gebundener bedingter Bereitschaft vorschauen.

**Architektur:** Separates `test_chains.py` verwendet bestehenden Dependency-Report, Pilot-Testeligibilität und begrenzte sichere Dateileser. Geschützter POST-Endpunkt, keine Aufträge oder Freigaben. S1 bleibt unverändert.

**Technik:** Python-Standardbibliothek und bestehender HTTP-Dienst.

- [x] Neue Tests: stabile kanonische Bindung, schreibfreier DB-/Dateistand, bedingte interne Vorgänger, abgewiesene externe Lücken/Review-/Änderungsschritte, Auswahl-/Datei-/Budget-/Adapterdrift.
- [x] Zweifache frische Beobachtung vergleicht Bindung einschließlich expliziter Dateibytes, Wurzel, Auswahl, effektivem Quellenstand/Übergang, externen Beleg-IDs und Versuchslage. Keine erfundenen Belege oder Modellaufrufe.
- [x] `POST /api/test-chains/preview` akzeptiert ausschließlich candidate_id/step_ids; bestehende Host/Origin/Sitzung/CSRF-Regeln beibehalten. HTTP-Schutz und keine Schreibwirkung nachweisen.
- [x] Relevante Tests und Syntax/Vertrag prüfen. Keine vollständige neue Ausführungsengine behaupten. S2b/S2c und UI-Start bleiben offen.
- [x] Dokumentation und Wiederaufnahme mit tatsächlichen Ergebnissen aktualisieren; lokalen Dienst nur ohne aktive Aufträge neu starten und Browser-Schutzprüfung durchführen.

Abnahme 17.09.2026: 54 relevante Tests in 20,893 Sekunden bestanden. Python-/JS-Syntax und JSON-Vertrag gültig. Lokaler Dienst ohne aktive Aufträge neu gestartet; Browserprüfung für CSRF, strikte Felder, unbekannte Vorschau, fehlenden S2-Start, unveränderte Auftragsliste und Neuladen ohne JS-Fehler bestanden. Kein neuer Gesamtsuitenlauf, keine realen Modelle oder Produktänderungen. Read-only-Regression für leeres Planjournal zuerst fehlgeschlagen (PlanBook-Konstruktor legte Tabellen an), danach lesende Fassade ohne Schemainitialisierung verifiziert.

