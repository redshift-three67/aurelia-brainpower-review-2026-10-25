# Gebundener technischer Übernahmeabschluss

Fortsetzung von Paket 2 im bereits freigegebenen Ablauf. Ein beliebiger geänderter Scope darf keine alten Planfreigaben erneuern. Daher explizite Bestätigung des angezeigten Nachher-Stands nur für die isolierte, bereits übernommene Änderung; keine allgemeine fachliche Abnahme oder Freigabe abhängiger Schritte.

- [x] Tests: unveränderlicher Beleg, konkreter letzter Nachprüfungsauftrag, erwarteter Scope, erneute Dateiprüfung, Auswahl-/Testdrift, Rücknahme, neue Prüfung und Persistenz.
- [x] Neues Modul `technical_completion.py`: append-only Belege; Abschluss über erfolgreichen letzten `pilot_verify`-Auftrag plus frische Nachprüfung, identische Bindung und verpflichtende Betreiberbegründung. Status bei erneuter Nachprüfung dynamisch als aktuell oder veraltet ausweisen.
- [x] Geschützter Workerauftrag `/api/pilot/complete`: exakt verified_job_id, observed_scope_hash, note. Kein Modellaufruf, keine Produktdateischreiboperation. Abbruch vor Belegspeicherung respektieren.
- [x] UI: konkrete Nachher-Hashanzeige, Pflichtbegründung, ausdrücklicher Abschlussknopf, historischer Abschlussbeleg und erneute Prüfung. Keine direkte allgemeine change/test-Abnahme über Plan-API.
- [x] Relevante Tests, Browser/Syntax, Gesamtsuite und Dokumentation. Bestehende Quelle-/Auswahlfreigaben nicht ersetzen; eigenständige Testschritte und Kettenanerkennung bleiben gesonderte Adapterarbeit.
