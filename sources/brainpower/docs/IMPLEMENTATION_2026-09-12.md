# Umsetzung: nachvollziehbare Governor-Steuerung

Vom Betreiber am 12.09.2026 freigegebene Fortsetzung des sechs Punkte umfassenden Vorschlags. Umsetzung mit subagent-driven-development, getrennten Dateiverantwortungen und abschließender unabhängiger Prüfung.

## Architektur und Reihenfolge

1. Ein append-only Entscheidungsjournal speichert Betreiberentscheidungen mit Arbeitsschritt, Begründung, Zeit und Quellenbindung. Historische Dokumente werden als deklarierte Nachweise importiert, nicht als heutige Aufträge.
2. Eine reine Governance-Funktion berechnet Schritte, Voraussetzungen, Sperrgründe und Priorität. Ein lesender RadiWorks-Intake hängt nicht von Aurelias Infrastrukturabnahme ab. Implementierung bleibt an die konkreten Integrationsgates gebunden.
3. Modellkontext trennt Betreiberautorität, berechnete Schritte und historische Dokumente. Terra/Sol und Terra/Astra bleiben einzeln verfügbar; ein Vergleich verwendet denselben Terra-Plan für beide Supervisoren.
4. Die Oberfläche zeigt berechnete Matrix, lesbare Reviews und begründete Betreiberentscheidungen. Ein Modell oder erfolgreicher Test akzeptiert kein Produktgate automatisch.
5. Begrenzte lesende Governance-Aufträge erzeugen lokale, quellengebundene Berichte; vorhandene Testaufträge bleiben verfügbar. Fremde Produktdateien werden nicht autonom geändert.
6. Chrome-Live-Prüfung wird als separate, lokale Testaktion ergänzt bzw. vorbereitet: eigenes Profil, eigener Prozess, Loopback-Port, Nachweise im Auftrag. Kein beliebiger Shellbefehl aus der Oberfläche.

## Abnahme

- Tests für Staging/Commit, historische Pause, scoped authorization, Quellenänderung nach Abnahme, konkrete Abhängigkeiten, gleiche Vergleichseingaben und fehlgeschlagene Modellaufrufe.
- HTTP-Tests für Entscheidungsjournal und Ablehnung veralteter Abnahmen, Browserprüfung der neuen Bedienwege.
- Reale Modellprüfung mit den bereits freigegebenen Projektauszügen; keine Behauptung allgemeiner Modelloptimalität.
- Dokumentation und portables Paket aktualisieren; Ausgangssnapshot und Originalprodukte bewahren.

## Verantwortlichkeiten

governance.py: Regeln und Wissensübernahme. store.py/server.py: Persistenz und HTTP. jobs.py: begrenzte Ausführung. llm.py: hybrider Vergleich. static/: Bedienoberfläche. live_view.py: optionale Chrome-Prüfung.
