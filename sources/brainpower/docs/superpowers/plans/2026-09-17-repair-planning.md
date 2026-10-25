# Begrenzte Reparaturplanung

Genehmigte Fortsetzung: ausdrücklicher, begründeter Modell-Planungsauftrag aus aktueller Fehlerdiagnose. Bestehendes Terra-/Supervisor-Routing, Medium, keine Tools/Produktausführung. Diagnose, Intake, Egress, Quelle, Auswahl, Vorgänger und Dateien vor Versand und vor Kandidatenspeicherung prüfen. Maximal zwei journalisierte Reparaturplanversuche je ursprünglichem Kandidaten/Testschritt, alle Zustände zählen. Ein neuer Kandidat ersetzt keine Auswahl-/Produktfreigabe.

- [x] Tests: fehlende/veraltete Diagnose, Quelle, Scope-Ausweitung, Versuchsgrenze, Planvalidierung und neuer Kandidat ohne Freigabe.
- [x] repair_planning.py: gebundener Kontext und strikte Ergebnisgrenzen. jobs.py: bestehenden scope_plan-Worker benutzen, keine alternative Modellstrecke.
- [x] Geschützte API und UI mit ausdrücklicher Versandinformation und Pflichtbegründung.
- [x] Mock-HTTP/Modelle, Browser, Null-Tool-Nachweis, Gesamtsuite und Dokumentation.

Im Reparaturplan dürfen nur Dateien des fehlgeschlagenen Tests erscheinen. Erweiterungen verlangen separate Neuplanung. Ein Plan enthält mindestens Änderung und anschließenden abhängigen Test; keine automatische Folgeausführung. Rückfragen und blockierte Reviews erzeugen keinen Kandidaten. Originaldateien und bestehende Journalbelege werden nicht verändert.

Verifiziert: sieben gezielte Prüfungen einschließlich echter HTTP-/Workerstrecke mit simulierten Modellantworten bestanden. Ungültige Scope-Erweiterung gesperrt; gültiger Kandidat ohne Auswahl-/Ausführungsfreigabe gespeichert. Gesamtsuite Python 3.12: 480 Tests in 289,597 Sekunden, 478 bestanden und zwei ausgelassen. Browser mit simulierten API-Antworten: Pflichtbegründung/Versandhinweis, exakte Anfragebindung und ausgeblendete Reparaturaktion bei gesperrter Diagnose; keine JavaScript-Fehler. Lokale Hermes-Initialisierungsprobe bestätigt tool_count=0, ohne Modellanfrage. Python-Kompilierung, JavaScript-Syntax und JSON-Vertrag geprüft. Keine echten Projektinhalte für diese Verifikation an Modelle gesendet.

