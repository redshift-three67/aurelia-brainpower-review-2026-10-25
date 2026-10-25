# RadiWorks: unabhängige Windows-Aufgaben und lesender F:-Vergleich

Stand: 03.10.2026, lokaler Windows-Prototyp. Keine Aurelia-Integrationsfreigabe.

**Späterer Stand am selben Tag:** Dauerinstanzen auf 8103–8109 erweitert und zusätzliche Kontrollaufgabe eingerichtet. [Nachweis, Chatverbindung und aktueller Restplan](RADIWORKS_SIEBEN_INSTANZEN_CHAT_NETZWERK_2026-10-03.md). Der folgende Dreier- und F:-Vergleich bleibt ein zeitlich begrenzter früherer Befund.

## Drei Aufgaben

Die Aufgaben `RadiWorks-Local-8103`, `RadiWorks-Local-8104` und
`RadiWorks-Local-8105` wurden unter dem interaktiven Konto des Betreibers
registriert und sofort gestartet. Jede hat einen Anmeldetrigger, genau eine
Aktion auf `tools/radiworks_scheduled_host.ps1` mit festem Port, die
Mehrfachstartregel `IgnoreNew` und keine zeitliche Ausführungsgrenze.
Der Installer `tools/install_radiworks_scheduled_tasks.ps1` überschreibt
eine bestehende Aufgabe mit abweichender Aktion nicht. Ein zweiter Aufruf
war idempotent.

Der Host wartet bei belegtem Port. Er beendet und ersetzt den vorhandenen
Prozess nicht. Bei freiem Port startet er RadiWorks mit demselben Quell-,
Katalog- und Runtime-Pfad wie der bisherige Launcher. Für 8103 liest er
den bereits vorhandenen externen Fernet-Schlüssel von E: vor dem Start;
8104 und 8105 bleiben ohne diesen Schlüssel im eigenen `seeded`-Scope.
Die Aufgaben verwenden nur `127.0.0.1` und getrennte Laufzeitordner.
Ein fremder oder nicht antwortender Listener wird nicht übernommen.

Nach der Registrierung: alle drei Aufgaben meldeten `Running` und
`LastTaskResult=267009` (laufender Task). Ihre eigenen Host-Protokolle
meldeten `radiworks_ready`; alle drei `/ping`-Aufrufe lieferten `pong`,
und auf allen Ports waren virtuelle Broadcast-Aufträge weiterhin aktiv.
Die drei Host-PowerShell-Prozesse hatten `svchost` als Elternprozess,
nicht Codex. Das belegt den unabhängigen Start der **Warteprozesse**,
nicht schon einen getesteten Wechsel der drei Engine-Prozesse.
Bei der Einrichtung liefen die Aufgaben zunächst nur als Warteschicht neben
den bestehenden Prozessen. **Nachtrag vom 03.10.2026:** Nach dem Schließen
von Codex wurden die Ports zwischen 09:06:56 und 09:06:58 frei. Alle drei
Aufgaben starteten um 09:07:05 ihre RadiWorks-Engine selbst. Bei der
Wiederaufnahme waren die drei Aufgaben `Running`, alle Ports antworteten
mit `pong`, und die Engine-Prozesse 42296, 29084 und 18692 hatten jeweils
den passenden Aufgaben-PowerShell-Prozess als Elternprozess. Die Falllisten
meldeten 3/1/1 Fälle; auf 8103 war Stochastic-Recovery verfügbar, auf
8104/8105 erwartungsgemäß nicht. Damit ist der unabhängige Start nach
Codex-Schließen praktisch belegt. Der Prozesswechsel überträgt keine
laufende In-Memory-Broadcast-Queue; deren damaliger Einzelstatus wurde
nicht protokolliert. Eine Abmeldung, ein Windows-Neustart und ein Ausfall
des Schlüssellaufwerks E: wurden nicht simuliert. `Interactive` setzt eine
angemeldete Benutzersitzung voraus.

Protokolle: `runtime/radiworks-preview-8103/scheduled-host.log` bzw.
`runtime/radiworks-local-8104/scheduled-host.log` und
`runtime/radiworks-local-8105/scheduled-host.log`. Die Aufgaben vor einer
gewollten Abschaltung kontrolliert beenden; ein normaler Engine-Stop allein
würde sonst den automatischen Wiederanlauf auslösen. Laufende Aufträge
vor einem Wechsel gesondert prüfen.

## F:-Vergleich

Verglichen wurde ausschließlich der produktive Modulquellbaum
`C:\Users\Hubert111\Documents\Radiworks\radiworks_port` gegen
`F:\Hauptprojekt\Aurelia\20260930-1\sources\RadiWorks\radiworks_port`.
SHA-256 wurde für jede berücksichtigte Datei neu berechnet. Generierte
Umgebungen, Caches, `radiworks_home` und Logdateien waren aus diesem
**Quellvergleich** ausgeschlossen; er ist kein Daten- oder
Wiederherstellungstest.

| Nachweis | Ergebnis |
| --- | ---: |
| Aktuelle Modulquelldateien | 135 |
| Modulquelldateien in F:-Archiv | 126 |
| Bytegleich | 102 |
| Gleicher Pfad, andere Bytes | 24 |
| Nur aktuell vorhanden | 9 |
| Nur im Archiv vorhanden | 0 |

Die 24 Änderungen betreffen u. a. Analyse-, Fall-, Stick-Pad-,
Broadcast-, Entropie- und Browserdateien. Die neun neuen Dateien enthalten
u. a. Katalogsuche/-Zusammenführung, Fokus- und GV-Darstellung sowie
zugehörige Tests. Der RadiWorks-Branch ist weiterhin
`backup/radiworks_final_polish` bei HEAD
`866f52146ad212157bfb20c9852714cb307a3b12`; der heutige
Arbeitsstand ist damit **nicht** durch die gleiche Commit-ID als
archiviert nachgewiesen.

Das F:-Archiv `20260930-1` wurde damals mit 274.403 Dateien und
8.544.704.231 Bytes als verifiziert protokolliert. Heute stimmten die
SHA-256-Werte seiner Dateien `MANIFEST.jsonl`, `SOURCE_STATE.json`,
`OMISSIONS.json` und `PROJECT_STATUS.md` erneut mit `VERIFY.json`
überein. Es wurden heute **nicht** sämtliche 274.403 archivierten Dateien
erneut gelesen.

Die derzeitigen Laufzeitordner `radiworks-preview-8103`,
`radiworks-local-8104` und `radiworks-local-8105` fehlen im
F:-Governor-Archiv `20260930-2`; dieses stammt ebenfalls vom 30.09.
Somit belegt F: weder den aktuellen Quellstand noch die heutigen drei
Fall-/Broadcast-Laufzeitstände. Auf F: wurde nichts verändert.

## Folgerung

Für eine aktuelle unabhängige Wiederherstellung muss nach einem
kontrollierten, konsistenten Sicherungszeitpunkt ein neuer Quell- **und**
Runtime-Sicherungspunkt erstellt und verifiziert werden. Ein bloßes
Überschreiben des F:-Archivs oder eine Kopie während aktiver
Broadcast-/Fallzugriffe wäre kein nachgewiesener Wiederherstellungspunkt.
