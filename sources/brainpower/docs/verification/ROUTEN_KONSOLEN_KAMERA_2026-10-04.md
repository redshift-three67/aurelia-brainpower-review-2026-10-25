# Chat-/Hermes-Routen, Windows-Start und USB-Entropie — 04.10.2026

## Ergebnis und Grenzen

Die CC-Switch-Providerdefinition ist wieder vorhanden und TOML gültig. Der laufende Chatturn meldet tatsächlich GPT-6.1 Sol/high. Die nativen Rollen Luna 6/max und Astra 6/medium wurden in dieser Bearbeitung eingesetzt: Luna für den begrenzten konsolenfreien Starter, Astra für die unabhängige Bewertung einer Journaloptimierung. Das ist bedarfsabhängige Delegation, keine automatische Modelleskalation bei jedem Auftrag. Gespeicherte Defaults allein bestimmen keinen laufenden Chatturn.

Hermes/Governor: Zero-Tool-Probe bestanden. Ein echter, ausschließlich synthetischer Hybridreview je Weg bestand mit Terra 5.6/medium + Sol 5.6/medium beziehungsweise Sol 6/high + Luna 6/max + Astra 6/medium. Astra wurde im Anwendungstest ausdrücklich erzwungen, um diesen Transport ebenfalls zu prüfen. Route B der Anwendung nutzt den Router direkt; der alte Terra-Weg nutzt den isolierten Hermes-Adapter. Beide lieferten REVIEW_ONLY ohne Freigabe. Kein Governor-Job, echtes Projektgedächtnis, automatische Reviews oder Produktsettings wurden geändert. Die Hermes-Anwendung wurde nicht auf Sol 6.1 migriert. Fünf erfolgreiche Modellaufrufe sind ein begrenzter Funktionsnachweis, kein Qualitäts-/Kostenvergleich oder Beweis lückenlosen Gedächtnisses.

## Konsolenfenster und Dauerinstanzen

Der minütliche Watchdog startete vorher powershell.exe direkt. Das passt zum periodischen kurzen Fenster, ist ohne Desktopbeobachtung aber keine vollständige visuelle Ursachenzuordnung. Neu startet der vorhandene pythonw.exe einen streng begrenzten Launcher; dieser erzeugt PowerShell mit CREATE_NO_WINDOW. Zulässig sind ausschließlich Hosts 8103–8109 und der feste Watchdog.

Acht bekannte Aufgabenaktionen wurden nach XML-Sicherung umgestellt. Trigger, Principal und Settings wurden vor/nach bytegleich verglichen. Keine Aufgabe wurde von diesem Schritt gestoppt oder neu gestartet; alle sieben Engine-PIDs blieben gleich. Ein regulärer neuer Watchdog-Lauf endete mit Ergebniscode 0; sieben direkte HTTP-Proben ohne Proxy ergaben pong. Eine erste PowerShell-HTTP-Probe überschritt fünf Sekunden; sie wurde nicht als Instanzausfall gewertet. Die direkten Proben antworteten in 0,24–2,01 Sekunden. Während der kurzen Aktionsmigration protokollierte der alte laufende Watchdog erwartungsgemäß abweichende Aktionen; laufende Hosts waren dadurch unberührt. Keine Logs wurden gelöscht.

Nach Windows-Start 08:36:19 wurden alle sieben Hosts um 08:36:36 gestartet. Damit ist Start nach Anmeldung praktisch belegt. Kein Dienststart vor Anmeldung und kein garantierter Wiederanlauf virtueller Broadcasts nach Stromausfall. Visuelle Bestätigung, dass auf dem Desktop keine Fenster mehr aufblitzen, bleibt eine Betreiberbeobachtung.

## RadiWorks-Prüfung und Kamera

Der eingefrorene Kandidat runtime/rw-gv-binding-20261003 bestand die nachgeholte Browserregression mit 22/22 Abschnitten. Seine vorherige Engine-Suite: 362 Tests, zwei bekannte Windows-Symlink-Skips. Keine Übernahme des Kandidaten auf die Liveports. Alle 134 gepinnten Originaldateien wurden erneut geprüft: kein Drift.

Die reale USB2.0 FHD UVC WebCam wurde auf dem isolierten Port 8110 für 180,007 Sekunden geprüft. Browserstream 640×480/30 fps; die bestehende Extraktion arbeitet verkleinert. 51.232 abgeleitete Seeds gelangten an die Testengine. Kein Bildframe wurde gespeichert oder an den Server übertragen; Kamera anschließend gestoppt, eigener Browser geschlossen. In den ersten rund 100 Sekunden kamen zu wenige neue Kandidaten zusammen; danach stieg der Feed. Dies belegt Sammlung/Transport, nicht physikalische Zufallsqualität oder medizinische Wirkung.

Die anschließende fallgebundene Stochastic-Analyse überschritt zunächst die 60-Sekunden-Diagnosefrist. Ein zweiter isolierter Lauf nutzte die bereits gesammelten Seeds aus dem verschlüsselten Testjournal, ohne erneute Kameraaktivierung. Nach 80,522 Sekunden: 39 Raten, Stochastic-Passport, persistierte Sitzung. Neustart mit demselben ausschließlich synthetischen Fernet-Key und erneutes Laden bestätigten die unveränderte Sitzung. Alle 51.232 Kameraseeds wurden verwendet; weitere Seeds stammten vom OS-Fallback. External random.org war ausdrücklich nur im Test deaktiviert. Kein echter E:/F:-Schlüssel oder realer Fall wurde verwendet. Alle eigenen 8110-Testprozesse sind beendet.

Performance-Abgrenzung: 243.691 aufgezeichnete Seeds ergeben im unveränderten Analysealgorithmus ohne Journal/HTTP exakt dieselben Resultate in 0,139 Sekunden; Entschlüsselung davor separat 2,260 Sekunden. Der zusätzliche Seed-/Journal-/Persistenzpfad ist damit stark eingegrenzt. Öffnen/Schließen pro Record ist im Quelltext belegt, aber sein Zeitanteil gegenüber Verschlüsselung, Hashing und sonstiger Persistenz ist noch nicht isoliert gemessen. Keine Beschleunigung wurde bisher implementiert.

## Nächster begrenzter Block

1. Alten und neuen Writer mit gleichem synthetischem Seedstrom, gleicher Verschlüsselung und getrennten Append-/Commit-/Hashzeiten vergleichen.
2. Nur im isolierten Kandidaten einen eigenen wiederverwendbaren Writer mit unverändertem Recordformat prüfen: erfolgreicher Append bleibt sofort sichtbar; fsync bleibt an der vorhandenen Commit-Grenze. Explizites Cleanup/Windows-Handles, vollständige Writes, Fehlerzustände und Cursorgrenzen sind Pflicht. Keine Draw-, Seed-, Reihenfolge- oder Analyseänderung.
3. Fehler-/Crash-/Recoverytests und echte HTTP-Wiederanlaufprobe vor jeder Liveübernahme. GC allein reicht nicht für Cleanup. Astra bewertet diesen Ansatz als tragfähig, erteilt aber keine Aktivierungsfreigabe.
4. Danach GV-2: separate Beobachtungsentropie, bewusst aktiviertes 21-Minuten-Intervall, additive Historie und dauerhafte Fall-/Sitzungsidentität. Die positiven/negativen Zahlen beschreiben numerische Veränderungen, keinen belegten Gesundheits-/Harmonisierungszustand.
5. Verifizierten Stand mit Quellordner/Modul_Templates abgleichen; Aurelia-S4.8 und spätere Modulübergänge bleiben gesonderte Gates. Heute keine F:-Archivaktualisierung.

## Phasenstand dieses begrenzten Pakets

| Paket | Stand | Nachweis/Grenze |
|---|---:|---|
| Chatroute und beide Anwendungswege | 100 % geprüft | aktueller Turn, Rollen, fünf echte synthetische Aufrufe; kein Qualitätsbenchmark |
| Konsolenfreier Aufgabenstart | 100 % technisch umgesetzt | 6/6 Tests, PS-Parser, 8 Aktionen, natürlicher Watchdog 0, sieben PIDs unverändert; Sichtprobe optional |
| Kandidaten-Browserregression | 100 % | 22/22 bestanden; keine Liveübernahme |
| Reale USB-Sammlung | 100 % des Dreiminutenpakets | 51.232 Seeds; Entropiequalität unbewertet |
| Stochastic/Fall/Wiederanlauf | Funktionsprobe bestanden | 39 Raten; 81 s sind noch kein guter Bedienungsstand; random.org nicht geprüft |
| Journaloptimierung | 0 % umgesetzt | Diagnose und unabhängige Empfehlung vorhanden |
| GV-2, Intervall/Historie | 0 % umgesetzt | nächster Funktionsblock nach Performance-Gate |
| Aurelia-Integrationsfreigabe S4.8 | 0 % | unverändert keine Freigabe |

## Belege

- runtime/route-resume-check-20261004/{CHAT_VERIFY.json,RESULT.json,TASK_MIGRATION.json,TASK_VERIFY.json,PINGS.json,SOURCE_VERIFY.json} sowie acht *.before.xml / *.after.xml.
- runtime/rw-gv-binding-20261003/{progress-fix-browser-20261004.log,BROWSER_VERIFY_20261004.json,progress-fix-tests.xml}.
- runtime/rw-camera-20261004-02/{CAMERA.json,RESULT.json}: reale Sammlung, erster Timeout; ursprünglicher fehlgeschlagener UI-Start separat erhalten.
- runtime/rw-stochastic-diagnose-20261004/{RESULT.json,ANALYSIS.json,PERFORMANCE.json}: Stochastic, Wiederanlauf und exakter Seed-Replay. Testschlüssel/Journale enthalten nur künstliche Testdaten; niemals als reale Recovery-Konfiguration übernehmen.
- tools/radiworks_scheduled_launcher.pyw, tools/install_radiworks_scheduled_tasks.ps1, tools/radiworks_scheduled_watchdog.ps1, tests/test_radiworks_scheduled_launcher.py.

Modelle tatsächlich beteiligt: Sol 6.1/high als Chatlead; Luna 6/max als nativer Worker; Astra 6/medium als unabhängiger nativer Reviewer. Die fünf Anwendungsaufrufe sind davon getrennte Diagnoseaufrufe. Keine belastbare Tokenersparnis gemessen.
