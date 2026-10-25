# Kontextbezogene Schrittführung

Bestätigter Block 3b, Reasoning Medium. Kleine additive Anzeige im bestehenden Projektregister; keine neue Ausführung und keine Änderung von Freigaben. Planumsetzung mit Test-first und Abschlussprüfung.

Die Anzeige leitet aus vorhandenem Umfang, Aktualität, Aufnahmevoraussetzungen und bewusst geladenen Kandidaten vier Phasen ab: Umfang, Aufnahme, Planung, bewusste Freigabe. Sie nennt den Kontext, die nächste Bedienhandlung und ihren Sperrgrund. Höchstens ein bereits aktiviertes Bedienelement erhält eine zusätzliche Akzentumrandung. Text vermittelt dieselbe Information ohne Farbe. Keine zusätzlichen Bestätigungsdialoge, automatischen Klicks oder Fokuswechsel.

- [x] Reine Entscheidungsmatrix in `tests/test_workflow_guide.cjs` zunächst rot: kein Umfang, laufender Abruf, veraltete Quellen, fehlende Aufnahme, leere Planliste, ungültiger Kandidat, bewusste Prüfung. Renderingprüfung: deaktivierte Elemente werden nicht hervorgehoben oder aktiviert.
- [x] `governor_workbench/static/app.js`, `index.html`, `style.css`: additive Anzeige und aktualisierte Hinweise über vorhandene Control-Updates.
- [x] Neue/vorhandene JavaScript-Prüfungen, Syntax und isolierter Browser mit synthetischen Daten; unabhängiger Review. Backend bleibt unverändert, vorhandene Python-/Pilotnachweise wiederverwenden.
- [x] Bericht, Abschlussplan und Wiederaufnahme aktualisieren; Live-Oberfläche ohne Verlust eingegebener Texte aktualisieren. Danach gemeinsame Funktionsabnahme, keine vorweggenommene Gesamtfreigabe.

Abschluss und Grenzen: `docs/verification/WORKFLOW_GUIDE_2026-09-24.md`.
