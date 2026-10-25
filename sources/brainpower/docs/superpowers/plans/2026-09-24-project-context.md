# Projektkontext und getrennte Eingaben

Grundlage: bestätigter Hermes-Abschlussplan, Block 3. Reasoning Medium. Skill Planumsetzung, Test-first und abschließender Review. Bestehender Arbeitsstand bleibt erhalten; das übergeordnete Home-Repository ist kein Ziel für pauschale Git-Operationen.

Ziel: Projekt-/Gruppenwechsel mit laufenden Aufträgen bleibt quellengebunden; ungespeicherte Aufnahmefelder überleben den Wechsel innerhalb des geöffneten Tabs, ohne zwischen Einzel- und Gruppenkontexten zu vermischen. Keine neue Persistenz oder automatische Zustimmung.

Ansatz: kleine tablokale Zuordnung nach Umfangsart, Umfangs-ID und Mitglieds-ID. Nur Textentwürfe und deren ursprüngliche Quellenbindung merken. Vault-Versanderlaubnis, Schrittauswahl und ausführbare Kandidaten werden nicht restauriert. Bei veränderter Quellenbindung bleibt ein zuvor vom Dienst geladener Entwurf gesperrt und ausdrücklich als veraltet markiert. Eigene unbestätigte Texte erhalten einen Hinweis zur erneuten Prüfung und benötigen weiterhin die ausdrückliche Bestätigung gegen den aktuellen Quellenstand. Bestehende Request-/Objektidentitäten für verspätete Antworten prüfen. Kein Backendvertrag, Modellrouting oder Executor geändert.

- [x] Regressionsprüfung `tests/test_scope_ui.cjs`: A→B→A, gleiche Mitglieds-ID in Einzel-/Gruppe, neue Quellenbindung, verspätete Aufnahme/Planantwort, unverändertes Ziel eines bereits eingereihten Reviews. Zunächst Erhaltstest rot belegen.
- [x] `governor_workbench/static/app.js`: getrennte Aufnahmeentwürfe, klare Kontext-/Speichergrenzen, kein Wiederherstellen von Freigaben. Bestehendes Layout erhalten.
- [x] Bestehende Registry-/Scope-/Memoryprüfungen und JS-Prüfungen ausführen. Echte Browserstrecke auf isoliertem synthetischem Testdienst; keine echten Projekttexte an Modelle.
- [x] Unabhängiger begrenzter Review, Befunde beheben, Bericht/Wiederaufnahme aktualisieren. Live-Governor weiterhin geöffnet, kein Auftrag automatisch gestartet.

Der bereits bestandene vollständige Pilot-/Folgetest-/Rollbacknachweis wird wiederverwendet, solange sein Backend unverändert bleibt. Allgemeine Gruppenmatrix-Ausführung, neue Projektanlage und Fremd-PC-Setup bleiben eigenständige spätere Pakete. Kleine Schrittführung folgt auf diesem geprüften Kontextzustand.

Abgeschlossen: Nachweise und verbleibende Grenzen in `docs/verification/PROJECT_CONTEXT_2026-09-24.md`. Keine Gesamtproduktfreigabe.
