# Kontrollierter Quellenübergang für isolierte Änderungsketten

Genehmigte Fortsetzung von Paket 2. Ein expliziter, begründeter Operatorauftrag bindet den aktuellen Nachher-Scope und die bestehende Auswahl an einen unveränderlichen technischen Übernahmebeleg. Keine neue Ausführungsberechtigung, keine automatische Aufnahmeerneuerung oder Modellprüfung. Nur bereits erlaubter isolierter Änderungsschritt ohne Vorgänger; nachfolgende Test-/Reviewschritte können neue Belege erhalten.

- [x] Tests: bestätigter Übergang, Folgeabnahme, Drift, Rücknahme, neue Auswahl/Revision, fehlende Aufnahme, alte Belege, fehlende Konfiguration, doppelte/abweichende Bestätigung.
- [x] Neues change_chain-Modul: atomarer Übergangs- und Schrittbeleg, frische technische Prüfung bei Anerkennung; exakte Adapter-/Auswahl-/Quellenbindung.
- [x] PlanBook erkennt den ausdrücklich bestätigten effektiven Scope nur für Kettendiagnose und fachliche Abnahmen; execution_permission bleibt nach Übergang gesperrt. Testadapter erhält den ausdrücklich gebundenen effektiven Kandidaten.
- [x] Geschützter Workerauftrag und UI am aktuellen technischen Nachprüfungsbeleg; Pflichtbegründung und sichtbarer Nachher-Hash.
- [x] Gezielte Tests, HTTP/Syntax/Browser, Gesamtsuite und Dokumentation.

Der Operator muss die Aufnahme für den tatsächlichen aktuellen Stand bereits bestätigt haben. Bestehende Freigabe darf nicht durch gefälschten alten Scope erneuert werden. Vorherige Belege werden nicht umgeschrieben; Scopewechsel entwertet alle nicht neu belegten Schritte. Allgemeine abhängige Änderungsausführung und Gruppen-/Produktintegration bleiben ausgeschlossen.

Verifiziert: Gesamtsuite 452 Tests in 257,176 Sekunden, 450 bestanden und zwei ausgelassen (Python 3.11). Echter temporärer HTTP-/Workerablauf Übernahme → Quellenübergang → eigenständiger Test → Review → Rollback bestanden. Chrome-Browserprüfung mit simulierten API-Daten bestätigt Pflichtbegründung, exakte Anfragebindung, Beleganzeige, ausgeblendete Doppelbestätigung und Neuladen; keine JavaScript-Fehler. Python-Kompilierung, JavaScript-Syntax und JSON-Vertrag geprüft. Governor unter konfiguriertem Python 3.12 wieder aktiv; automatische Reviews aus, Supervisor Astra, keine aktiven Aufträge. Keine echten Produktfreigaben oder Modellaufrufe.

