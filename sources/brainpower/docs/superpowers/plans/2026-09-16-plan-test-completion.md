# Eigenständiger Testabschluss und Vorgängerketten

Freigegebene Fortsetzung von Paket 2. Expliziter Workerauftrag führt den bestehenden begrenzten Unittest-Adapter auf einer versiegelten, unveränderten Dateikopie aus. Kein Modellaufruf, keine Produktdateiänderung, keine automatische Folgeausführung. Nur konfigurierte isolierte Piloten; Gruppen und historische Produkte bleiben ausgeschlossen.

- [x] Tests zuerst: echter erfolgreicher/fehlgeschlagener Testlauf, Quellen-/Adapterdrift, neuester Versuch, Auswahlbindung, Vorgängerrücknahme und transitive Entwertung.
- [x] Plan-Testmodul: validierte Auswahl plus alle akzeptierten Vorgänger; eingefrorene Auswahl-/Vorgänger-IDs, frischer Quellenabgleich vor/nach Lauf; unveränderlicher step_completions-Beleg nur bei belegtem Erfolg.
- [x] Kettenprüfung: Testbeleg nur bei passendem aktuellen Job, letzter Versuch, Adapter-/Dateistand und Vorgängerbelegen anerkennen; Testbelege können wie andere Belege zurückgenommen werden. Fehlende Konfiguration sperrt Anerkennung.
- [x] Geschützte API und einzelner Worker, UI-Teststart im Kettenbericht und lesbare Ergebnisdarstellung. Keine frei eingegebenen Kommandos oder Interpreter.
- [x] Regressionen, HTTP, Browser/Syntax, Gesamtsuite, Dokumentation und kontrollierter Dienstneustart.

Grenzen: feste stdlib-unittest-Tests, ausschließlich explizite Scope-Dateien, Audit-Guard keine OS-Sandbox. Testinhalt ist nicht automatisch fachlich ausreichend. Änderungsschritte mit Scope-Übergang erhalten hierdurch keine allgemeine Kettenfreigabe.

Abschlussnachweis: 437 Tests, 435 bestanden, zwei ausgelassen (203,167 s). Echter temporärer HTTP-/Workerablauf und Chrome mit simulierten API-Daten erfolgreich; Syntax/Kompilierung/JSON/Diff geprüft. Lokaler Governor kontrolliert neu gestartet: keine aktiven Jobs, automatische Reviews aus, Supervisor gpt-6-astra erhalten, neuer Teststart ausgeliefert.
