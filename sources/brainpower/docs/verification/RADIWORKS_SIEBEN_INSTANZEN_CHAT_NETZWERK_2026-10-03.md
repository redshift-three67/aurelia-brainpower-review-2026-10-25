# RadiWorks: sieben Instanzen, Chatroute und Verbindungsdiagnose

Stand: 03.10.2026, lokale Windows-Vorbereitung. Keine Aurelia-Integrationsfreigabe.

## Codex-Verbindung

Die Codex-Protokolle melden zwischen 21:35 und 21:48 wiederholte Verbindungsfehler beim Senden von Modellanfragen. Der konfigurierte Provider führt über CC Switch auf `127.0.0.1:3000/v1`. Das CC-Switch-Protokoll dokumentiert einen Neustart um 21:49 nach einem vorherigen abnormalen Ende und die Wiederherstellung der Proxy-Einbindung. Danach werden wieder Anfragen für `gpt-6.1-sol` weitergeleitet. Der Windows-Ethernetstatus meldet Internetzugang, Port 3000 ist erreichbar und die aktuelle Chatbearbeitung funktioniert. Die zeitliche Übereinstimmung belegt den lokalen Proxy als konkrete Fehlerstelle; ein LAN-Ausfall ist damit nicht nachgewiesen. Netzwerk-/Providerkonfiguration wurde nicht zurückgesetzt.

Die aktuellen Codex-Protokolle bestätigen `gpt-6.1-sol` mit Reasoning `high`. Das separate Profil wurde nach Sicherung und TOML-Prüfung entsprechend angepasst. Luna 6/max bleibt begrenzter Worker, Astra 6/medium unabhängiger Prüfer für folgenschwere Entscheidungen oder ungelöste wesentliche Widersprüche. Hermes-Anwendungsrouten und die globale CC-Switch-Providerkonfiguration wurden nicht geändert. Eine Einsparquote für die neue Kombination ist nicht gemessen.

## Dauerinstanzen

`RadiWorks-Local-8103` bis `RadiWorks-Local-8109` sind registriert und laufen. Alle sieben `/ping`-Proben lieferten `pong`. Die Listener-PIDs blieben bei der Einrichtung unverändert: 64344, 22064, 69908, 24552, 69960, 50748, 23764 in aufsteigender Portreihenfolge. Bestehende Fälle, Auto-Modus und Broadcasts wurden nicht beendet.

Jede Instanz besitzt ihren eigenen Laufzeitordner und Fall-Scope. Sie teilen den geprüften Modulquellbaum und einen fest gepinnten Ratenkatalog. 8103 verwendet den vorhandenen externen Recovery-Schlüssel auf E:; 8104–8109 bleiben im getrennten Seed-Modus ohne diesen Schlüssel. Entwicklung erfolgt außerhalb 8103–8109, ab 8110.

Die Aufgaben starten bei Anmeldung des Betreibers, mit `Interactive/Limited`, `IgnoreNew` und ohne Laufzeitgrenze. Damit ist Wiederanlauf nach Windows-Neustart **bei anschließender Anmeldung eingerichtet**, jedoch heute nicht praktisch getestet. Vor Anmeldung ist kein Dienstbetrieb zugesagt. Der bisherige Nachweis für Codex-unabhängigen Engine-Start auf 8103–8105 steht im [früheren Aufgabenbericht](RADIWORKS_TASKS_F_VERGLEICH_2026-10-03.md).

Bei der Diagnose waren die Hosts von 8108/8109 beendet (`0xC000013A`), ihre Engines aber weiterhin erreichbar. Nur diese Aufgabenhosts wurden wieder gestartet. Die zusätzliche Aufgabe `RadiWorks-Local-Watchdog` prüft einmal pro Minute die sieben **bekannten Aktionen** und startet nur Aufgaben im Zustand `Ready`. Deaktivierte Aufgaben bleiben deaktiviert, fremde Aktionen werden verweigert. Der synthetische Test bestätigt diese Grenzen; die registrierte Wiederholung ist `PT1M` ohne Enddauer, der erste reale Kontrolllauf endete mit Ergebnis 0.

Für geplante Wartung zuerst die betreffende Instanzaufgabe deaktivieren und den Aufgabenhost kontrolliert stoppen. Ein alleiniger Engine-Stop löst sonst den Wiederanlauf aus. Der Watchdog beendet keine Engine, bewertet keine Fallinhalte und startet keinen Broadcast. Ein Prozessneustart stellt eine bisher nur im Speicher gehaltene Broadcast-Queue nicht automatisch wieder her.

## Peggotty und GV-RE

Die aktuelle Quelle ist für `core/script.py` und `api/routes.py` bytegleich mit dem zuvor isoliert geprüften Peggotty-Fix. Doppelte Labels wurden auf den laufenden Ports 8103 und 8106 mit HTTP 422 abgewiesen. Der ältere Bericht mit „noch nicht übernommen“ ist für diesen Punkt überholt. Die fünf gezielten Peggotty-Regressionstests bestanden: gültige Skripte, unbekannter Befehl, Laden eines Skripts sowie doppelte und verschiedene Labels. Der erste Testaufbau scheiterte am Sandbox-Zugriff auf den Testordner; die Wiederholung mit lokalen Rechten und neuem isolierten Ordner bestand. Eine bestehende Starlette/httpx-Deprecation-Warnung bleibt.

**GV-RE** zählt im gesamten Analyseergebnis die Raten mit exakt demselben, von null verschiedenen Raten-GV. Angezeigt wird die Zahl erst bei mindestens zwei Treffern. Sie ist weder ein Wiederholungsmesswert noch ein zeitlicher Trend. Der Original-Java-Code und `core/gvround.py` stimmen hierin überein. Die Erklärung ist jetzt in `webapp/index.html` ergänzt und wird von 8103 ausgeliefert; dafür war kein Engine-Neustart nötig.

## Nächste Umsetzung und Grenzen

1. Periodische GV-Beobachtungen zuerst isoliert entwickeln. Jede Beobachtung benötigt eindeutigen Fall-, Sitzungs- und Auftragsbezug, eigene Zeitangabe und eine getrennte Zufallsziehung. Die vorhandenen 21er-Runden und ihre Werte dürfen nicht überschrieben oder durch zusätzliche Entropieziehungen beeinflusst werden.
2. Erst danach eine optionale 21-Minuten-Abfrage und persistierte tabellarische Verlaufshistorie ergänzen. Fünf Klassen beschreiben numerische Veränderungen; Schwellen und Vergleichsbasis müssen sichtbar sein. Entropiebasierte GV-Werte belegen keine tatsächliche gesundheitliche Blockade, Verbesserung oder Harmonisierung.
3. Bestehende Broadcasts tragen derzeit keinen vollständigen Fall-/Sitzungsbezug. Diese Zuordnung darf beim Fallwechsel nicht geraten werden. Luna 6/max bestätigte dies unabhängig an `BroadcastRequest`, `BroadcastElement`, direktem UI-Broadcast und Auto-Modus. Kleinster Pilot: ausschließlich freigegebene Drafts mit vorhandener `sessionId`; Fall, Draft, Sitzung und Ratenindex validiert bis in jedes Queue-Element weitergeben. Ungebundene oder veraltete Aufträge bleiben von Beobachtungen ausgeschlossen. Fake-Clock-Tests prüfen Intervall, Stop und Ende; Reload- und Scope-Tests sichern Historie und unveränderte Originalwerte. Für diese Architekturprüfung wurde Astra nicht benötigt.
4. Reale USB-Kamera, Entropie-Langlauf und Stochastic-Recovery beim aktiven Testfall folgen mit verfügbarer Kamera. Mehrere Aufträge pro Fall in Aurelia, Host-/Mandantenrechte und Integrationsentscheidung bleiben gesonderte Gates.

| Teilpaket | Stand | Grenze |
| --- | ---: | --- |
| Verbindungsdiagnose und Chatmodell-Nachweis | 100 % | aktuelle Verbindung; kein dauerhafter Verfügbarkeitsbeweis |
| Sieben Instanzen und Kontrollaufgabe | 100 % eingerichtet | Windows-Neustart/Anmeldung noch praktisch testen |
| Peggotty-Duplikatkorrektur | 100 % lokal | HTTP 422 live; fünf Regressionstests bestanden |
| GV-RE-Erklärung | 100 % technisch lokal | Ansicht nach bewusstem Neuladen |
| Neue periodische GV-Historie | Planung | noch nicht aktiviert |
| Kamera und Stochastic-Langlauf | offen | reale Kamera fehlt heute |
| S4.8 Aurelia-Integration | 0 % | keine Freigabe |

Die drei RadiWorks-Modulreferenzen `PORT_PLAN.md`, `FESTLEGUNGEN.md` und `QUELLENANALYSE.md` wurden nach Sicherung ihrer Vorher-Dateien mit den geprüften Betriebsgrenzen aktualisiert. Gemeinsame ABI und Hostvertrag wurden nicht geändert.

Prozentangaben beziehen sich auf die genannten begrenzten Arbeitspakete, nicht auf Testabdeckung oder Gesamtreife. Tatsächlicher Modelleinsatz: GPT-6.1 Sol/high als Chatlead, Luna 6/max für die begrenzte unabhängige GV-Vertragsprüfung; kein Astra-Auftrag in diesem Block.

## Nachfolgender isolierter Pilot, 03.10.2026

Der erste Schritt der Fall-/Sitzungsbindung ist danach ausschließlich im Kandidaten geprüft worden: 360 Engine-Tests bestanden, zwei Windows-Symlink-Skips, 22 Browser-PASS-Abschnitte. [Aktueller Pilotnachweis und offene Historie](RADIWORKS_GV_BINDUNG_2026-10-03.md). Dieser Folgeblock nutzte Luna/max und Astra/medium; die oben beschriebene Architekturprüfung hatte Astra noch nicht genutzt. Die Dauerinstanzen und der echte Quellbaum wurden nicht geändert. Die periodische GV-Historie bleibt offen.
