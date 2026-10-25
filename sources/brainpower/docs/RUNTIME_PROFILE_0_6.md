# Lokales Laufzeitprofil – begrenzter erster Adapter

Dieses App-Profil prüft Prozessbesitz, Startbereitschaft, Portkonflikte und Stop. Es startet ausschließlich den mitgelieferten `runtime_probe.py` unter Windows. Keine Produktdateien werden gelesen oder ausgeliefert, keine Modellaufrufe gestartet und keine frei formulierbaren Befehle entgegengenommen. Weitere Projektadapter bleiben offen.

## Bedienung und Lebensdauer

Unter der lokalen Browserprüfung erscheint „Lokaler Laufzeittest“ mit Start/Stop und Laufhistorie. Standardport ist 8794, konfigurierbar über `runtime_probe_port` (1024–65535, weder Routerport3000 noch Governorport). Es darf nur ein eigener Prüfdienst gleichzeitig laufen. Maximale Laufzeit ist eine Stunde. Dienstende beendet den Prüfdienst. Nach Neustart gibt es keinen automatischen Wiederanlauf und keine Übernahme alter Prozessnummern; ein neuer Start erzeugt eine neue Instanz.

Das Profil bindet seine Konfiguration und Implementierungsdateien an einen Hash. Die Startanforderung muss diesen aktuellen Hash enthalten. Eine Portbelegungsprüfung geht dem Start voraus; der Listener bindet ausschließlich 127.0.0.1 und nutzt exklusiven Portbesitz. Die Bereitschaft wird durch eine lokale HTTP-Antwort mit zur gestarteten Instanz passender Kennung überprüft, nicht durch einen offenen Port allein. Ein konkurrierender Dienst wird weder beendet noch als eigener übernommen. Profile sind aktuell fest in der App vorgegeben, keine Benutzer- oder Modellkommandos.

## API und Nachweise

- POST `/api/runtime/start`: ausschließlich `profile_id` und `profile_hash`.
- POST `/api/runtime/stop`: ausschließlich `instance_id`.
- Beide Wege verwenden die bestehende geschützte Session/Origin/CSRF-Prüfung und einzelne Jobwarteschlange; keine zweite Ausführungswarteschlange.
- `/api/state` enthält `runtime_profiles` mit Profilen und bis zu30 aktuellen/historischen Instanzen.
- `runtime_instances` hält den letzten Zustand, `runtime_events` die angehängten Zustandsbelege. Zustände: starting, running, stopped, failed, interrupted.
- Alte aktive Belege werden beim Governor-Start interrupted. Das ist ein Unterbrechungsnachweis, kein erneuter Prozessstart oder Test-Erfolgsnachweis.

Ein Bereitschaftsnachweis ist keine dauerhafte Anwendungs-Gesundheitsgarantie. Der Beobachter überwacht Prozessende und maximale Laufzeit, nicht laufend den HTTP-Zustand. Portprüfung und anschließender Bind sind nicht atomar; ein Rennen wird durch exklusiven Listener und Instanzprüfung abgefangen. Betrieb unter einem potenziell böswilligen Prozess desselben Benutzers ist keine zugesicherte Sicherheitsgrenze.

Windows-Prozessbesitz erfolgt über das bereits getestete Kernel-Jobobjekt. POSIX und allgemeine Produktdienste werden durch dieses Profil nicht freigegeben. Die nächsten Schritte sind weitere explizite Adapterprofile, quellengebundene Fortschrittsnachweise und genehmigte Schrittfolgen.

## Verifikation

Aktueller Nachweis einschließlich Nachprüfung: vollständige Suite 379 Tests in 150,311 Sekunden, 377 bestanden und zwei ausgelassen. Chrome: Start, explizite Bereitschaftsprüfung, Stop und gespeicherter Prüfbeleg nach Neuladen erfolgreich, keine JavaScript-Fehler. Python-Kompilierung, JavaScript-Syntax und JSON-Vertrag geprüft. Governor neu gestartet; keine aktive Laufzeitinstanz zurückgelassen, automatische Reviews weiterhin aus. Kein Modelllauf und keine Server-/Produktänderung.

Ergänzung: „Bereitschaft prüfen“ führt über den einzelnen Auftragsworker eine explizite erneute Prüfung der eigenen aktiven Instanz aus. POST /api/runtime/check nimmt ausschließlich instance_id an; keine Ziel-URL oder Kommandos. Antwortkennung, Prozess und aktueller Profilhash müssen passen. Das Ergebnis wird mit Zeitpunkt im Instanz- und Ereignisjournal gespeichert; ein negatives Ergebnis ersetzt den letzten positiven Prüfbeleg, ohne einen Neustart auszulösen. Historische Belege sind keine kontinuierliche Überwachung und gelten nicht als Produktfreigabe. Nach Stop/Neustart können alte Instanzen nicht geprüft werden.

374 Tests in der vollständigen Suite: 372 bestanden, zwei ausgelassen (149,867 Sekunden). Chrome-Prüfung über die sichtbaren Schaltflächen: Start, Bereitschaft, Stop und Historie nach Reload erfolgreich; keine JavaScript-Fehler. Echte Neustartprüfung: Laufzeitinstanz 0c53115228eb4aef9cd8cd5459b2cda8 beim Governor-Ende gestoppt, nach Neustart als gestoppt erhalten; keine aktive Instanz, exklusives erneutes Binden des Ports erfolgreich. Automatische Reviews aus, Reasoning Medium. Keine Modellaufrufe für diesen Ausbau.
