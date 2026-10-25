# RadiWorks: drei lokale Instanzen für getrennte Fälle

Stand: 02.10.2026. Dieser Nachweis gilt nur für den lokalen Windows-Prototyp; er ist keine Freigabe des Aurelia-Mandantenhosts oder für mehrere unabhängige Aufträge innerhalb eines Prozesses.

## Ergebnis

Die bestehende Instanz auf `127.0.0.1:8103` blieb unangetastet. Zusätzlich laufen `127.0.0.1:8104` und `127.0.0.1:8105` als eigene RadiWorks-Prozesse. Jede Instanz hat einen eigenen Port, ein eigenes `RADIOWORKS_HOME`, eine eigene Engine-Sperre, Fallablage, Draftablage und virtuelle Broadcast-Queue. Alle verwenden dieselben aktuellen RadiWorks-Quellbytes und denselben angehefteten, lesend genutzten Katalog-Release. Der HTTP-Manifesthash war auf allen drei Ports `sha256:fa169781a07b21c4dd569fad1ae6225611095f8bdb3aae41f22a0d986b2309eb`.

| Port | Laufzeitverzeichnis | Zustand bei Abschluss | Besonderheit |
| --- | --- | --- | --- |
| 8103 | bestehende Laufzeit | erreichbar; drei vorhandene Fälle, leere Queue, Auto AUS | externer Fernet-Recovery-Schlüssel weiterhin verfügbar; nicht neu gestartet |
| 8104 | `runtime/radiworks-local-8104` | erreichbar; leerer eigener Fallbestand, leere Queue, Auto AUS | neue lokale Instanz, Standard `seeded` |
| 8105 | `runtime/radiworks-local-8105` | erreichbar; leerer eigener Fallbestand, leere Queue, Auto AUS | dritte lokale Instanz, Standard `seeded` |

Die neuen Instanzen laufen mit festem lokalem Scope und ohne `RADIOWORKS_JOURNAL_KEY`. Deshalb ist dort eine fallgebundene Stochastic-Analyse nicht verfügbar; die 8103-Konfiguration und ihr externer Schlüssel werden nicht geteilt. Die Bindung an `127.0.0.1` und die bestehenden lokalen Schutzregeln der RadiWorks-App bleiben maßgeblich.

## Bedienung

Der Launcher `tools/radiworks_local_instances.ps1` verwaltet ausschließlich 8104 und 8105. Er startet die Prozesse mit verborgenem Fenster und getrennten Verzeichnissen. Ein zweiter Start desselben nachgewiesenen Prozesses ist idempotent. Ein fremder oder nicht nachweisbar zugehöriger Listener wird nicht übernommen. `Stop` verweigert bei aktivem Auto-Modus oder laufenden/angestellten virtuellen Broadcasts den Abbruch. Der Marker verknüpft Port, Prozess-ID, Prozessstartzeit und Runtime, um eine wiederverwendete PID nicht als eigene Instanz zu behandeln.

```powershell
& 'C:\Users\Hubert111\Documents\Brainpower\tools\radiworks_local_instances.ps1' -Action Status -Port 8104
& 'C:\Users\Hubert111\Documents\Brainpower\tools\radiworks_local_instances.ps1' -Action Status -Port 8105
& 'C:\Users\Hubert111\Documents\Brainpower\tools\radiworks_local_instances.ps1' -Action Start -Port 8104
& 'C:\Users\Hubert111\Documents\Brainpower\tools\radiworks_local_instances.ps1' -Action Start -Port 8105
```

Die Browseradressen sind `http://127.0.0.1:8103/`, `http://127.0.0.1:8104/` und `http://127.0.0.1:8105/`. Ein anderer Browser-Tab auf **demselben** Port teilt dessen aktuellen Fall und Laufzeitzustand. Für einen anderen Fall daher einen anderen Port verwenden. Es wurde kein Autostart nach Windows-Neustart eingerichtet; danach die beiden `Start`-Befehle ausführen. Ein Schließen von Codex bei laufenden Hintergrundprozessen wurde in dieser Sitzung nicht als eigener Neustart-/Abmeldetest geprüft.

## Prüfung und Testdaten

Vor dem Start waren 8104 und 8105 frei. Ein älterer, anders benannter synthetischer 8104-Vorschaubereich wurde nicht verändert. Der PowerShell-Parser akzeptierte den Launcher; ungültiger Port 8090 wurde abgewiesen. Start, wiederholter Start, Status und kontrollierter Stop von 8104 sowie Start/Status von 8105 wurden tatsächlich ausgeführt. Nach einem Stop gab 8104 den Port frei, während 8105 und 8103 erreichbar blieben. Danach wurde 8104 wieder sauber gestartet.

Ein zeitgleicher synthetischer Test legte auf 8104 und 8105 je einen erfundenen Fall mit unterschiedlichem Fokus an, analysierte dieselbe Datenbank, führte auf 8104 einen GV-Schritt und einen kurzen virtuellen Broadcast aus und prüfte, dass Fall, Fokus, Sitzung, GV und Queue von 8105 unverändert blieben. Der Test meldete `PASS: two concurrent synthetic cases, distinct focus/sessions, GV and virtual queue isolated`. Testskript und SHA-256-Dateiliste liegen unter `runtime/radiworks-multiinstance-20261002`. Die beiden Test-Runtimes wurden nach dem Stop hashgeprüft nach `checkpoints/radiworks-multiinstance-smoke-20261002/{8104,8105}` verschoben. Anschließend wurden 8104 und 8105 mit **leeren** nutzerseitigen Laufzeitverzeichnissen neu gestartet. Keine Testfälle wurden auf 8103 angelegt.

Die beiden geöffneten Browserseiten zeigten jeweils „kein Fall geladen“, `Live`, leere Queue und `seeded`. Auf allen drei Ports antworteten `/ping` und `/manifest`; auf den neuen Ports meldete `/cases` jeweils null Fälle. Ein tatsächliches Schließen von Codex, Windows-Neustart oder Wiederherstellen eines realen Falls auf 8104/8105 wurde nicht geprüft. Der lokale Mehrprozessnachweis ersetzt weder Backup noch die spätere mandanten- und auftragsgebundene Aurelia-Integration.

## Planstand

| Abschnitt | Stand | Nächster Nachweis |
| --- | ---: | --- |
| Drei lokale Instanzen, getrennte Fälle | 100 % des heutigen Einrichtungs- und synthetischen Isolationstests | Betreiberprobe mit erfundenen Fällen auf 8104/8105 |
| Dauerbetrieb nach Codex-Schließen/Windows-Neustart | teilweise | getrennte Betriebsprobe; nach Neustart manuell starten |
| Physische Webcam-Hotbits | offen | bewegte USB-Kamera, serverbestätigter Feed und Quellenprüfung |
| Mehrere Aufträge desselben Falls innerhalb Aurelia | Vertragsentwurf | Hostautorisierung, Auftragsscope, Rechte, Quoten, WebSocket- und Recovery-Tests |
| Aurelia-Integration S4.8 | 0 % | Host-/ABI-/Betreiber-Gates |

Die Prozentangabe bezieht sich auf den begrenzten lokalen Arbeitsschritt, nicht auf allgemeine Testabdeckung oder Integrationsfreigabe.
