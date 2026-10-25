# RadiWorks GV-2 — getrennter Betriebsnachweis vom 04.10.2026

Abgeschlossenes begrenztes Pilotpaket: echter erster 1260-Sekunden-Zyklus, Journal-Replay und kontrollierter Neustart bestanden. Keine Übernahme in die sieben Dauerinstanzen oder Aurelia-Freigabe. Grundlage: [isolierter GV-2/UI-Abschluss](RADIWORKS_GV2_ABSCHLUSS_2026-10-04.md).

## Aufbau und Grenzen

- Eigene manuell gestartete Windows-Aufgabe `RadiWorks-GV2-Pilot-8110`, `Interactive/Limited`, ohne Trigger, ohne Watchdog oder automatische Wiederaufnahme. Verifiziertes Task-XML fest gepinnt. Kein neuer Autostart für den Pilot; vorhandene Daueraufgaben unverändert.
- Kandidat `runtime/rw-gv2-20261004`, 103 Produkt-/Test-/UI-Dateien per SHA-256 geprüft. Manifestdigest im Pilotstart festgeschrieben. Eigene UI-Kopie: 22 Dateien identisch, index.html ausschließlich mit sichtbarem synthetischem Hinweis und Pilottitel ergänzt.
- Eigener lokaler Scope, Home, rein künstlicher Katalog und zwei künstliche Fälle. Eigener Fernet-Key; Datei und Verzeichnis haben eine geschützte benutzereigene ACL. Kein Zugriff auf echte E:/F:-Keys oder Falldaten.
- Produktions-App/Beobachtungsworker, echte monotone Uhr und OS-Entropie. Keine Testendpunkte, FakeClock, vorgegebenen GV-Zahlen oder geteilten Kamera-/random.org-Streams. Vier gebundene Promotions-Broadcasts ausdrücklich eingeschaltet; erster Termin gegen20:16 Uhr. Hardwareausgabe bleibt deaktiviert.
- `pilot_service.py` läuft über pythonw in der getrennten Aufgabe. Startprüfung verweigert Quellen-/Taskdrift, fremden Listener oder veraltete PID. `Stop-Pilot.ps1` fordert Uvicorn-Shutdown an, wartet Listenerende/Taskende und Exit0 ab; kein erzwungenes Beenden.

Diese Guards schützen vor versehentlicher Drift/Verwechslung; sie sind keine Signatur- oder Sicherheitsgrenze gegen einen Angreifer mit demselben Benutzerkonto und Schreibzugriff auf die Launcher.

## Historischer Zwischenstand vor dem Intervallabschluss

- Verkürztes Manifest: zunächst1 erwarteter roter Test, danach2 grüne Tests inklusive aktuellem Quellenstand.
- Wiederholter Start: bestehender eigener PID erhalten, kein Doppelstart.
- Browser4PASS: Hinweis/Titel, WebSocket/Dunkel, vier gebundene Aktivierungen,375px ohne Seitenüberlauf, keine JS-Seitenfehler. Headless Chrome; kein Benutzerabnahmetest.
- Astra-Nachprüfung der Startschutzkorrekturen: kein konkreter verbleibender Blocker im begrenzten Umfang. Zu diesem Zwischenzeitpunkt waren Timer, Shutdown/Restart und Live-Nachvergleich noch offen; die Abschlussbelege stehen unten.

## Ausgeführtes Vorgehen nach erstem Termin

1. Vier OS-journalisierte Basiseinträge, eindeutige Fall-/Sitzungsbindung und unveränderte Analyse-/Falldateien nachweisen. Neue Fälligkeit prüfen.
2. Nur den Pilot sauber beenden. Port/Task/Exitcode prüfen; Historien- und Schlüsselbestand bewahren.
3. Mit derselben Quelle/Home/Key neu starten: Historie unverändert, Intervalle aus und Queue leer. Kein unerlaubtes Wiederansetzen eines alten Broadcasts.
4. Danach Pilot für die Bedienprobe erreichbar lassen; Dauerinstanzen8103–8109 bleiben beim bisherigen Stand. Kontrollierte Übernahme in echte Instanzen, kanonische Quell-/Modul_Templates-/F:-Synchronisation und S4.8 sind andere Schritte.

## Betrieb / Rückkehr

Start und Stop ausschließlich über die festen Skripte unter `runtime/rw-gv2-pilot-8110-20261004/`. Nicht die sieben Daueraufgaben oder deren Watchdog verwenden. Rückkehr zum bisherigen Bedienstand: nur den Pilot stoppen, weiter8103–8109 nutzen. Der ursprüngliche Modulquellbaum wird nicht ersetzt.

Codex-Schließen und Windows-Neustart werden in diesem Block nicht tatsächlich ausgeführt. Der Schedulerstart belegt die getrennte Startzuständigkeit, keinen umfassenden Warmstart- oder Netzwerkausfallnachweis. Die Pilotaufgabe hat absichtlich keinen Anmeldetrigger. Die erste Beobachtung ist eine Basis ohne Trend; zwei echte aufeinanderfolgende Intervalle sind ein zusätzlicher Nachweis, kein Ergebnis dieses ersten Zyklus.

Modelle: gewählte Leitung Sol6.1/high; Root setzte Start/Stop und sämtliche Pilot-/Launcher-Gegenproben um. Luna6/max lieferte den begrenzten Start-/Pfadabgleich, keine Implementierung der Launcher-Gegenproben. Astra6/medium prüfte Betriebsgrenzen und Abschlussnachweise unabhängig. Keine gemessene Kosteneinsparung.


## Verifizierter Abschlussstand

- Erste vier Beobachtungen tatsächlich nach 1260.94–1261.04 Sekunden; 223 Statusproben bis zum Übergang0→4. Eigene OS-Journale, zwei getrennte künstliche Fälle/Sitzungen. Zwei ursprüngliche Falldateien blieben bytegleich. Vier Baselines, noch keine zweiten Echtzeit-Trendwerte.
- Alle vier verschlüsselten Journale mit dem privaten Pilotschlüssel authentifiziert; Digest/Cursor/OS-Quelle geprüft und beide GV-Werte exakt reproduziert. Nach Neustart erneut erfolgreich geprüft. Schlüssel/Rohseeds nicht exportiert.
- Sauberer Uvicorn-App-Shutdown, Port geschlossen, AufgabeReady/Exit0; neuer PID23288 statt54552. Vier Historienzeilen, zwei Sitzungsbindungen und zehn Persistenzdateien unverändert. Intervalle aus, Queue leer; keine automatische Wiederholung alter Aufträge. Die neue App meldet den eigenen Recovery-Key als verfügbar.
- Browser nach Neustart4PASS: vier Basiszeilen, beide Filter mit exakt passendem Sitzungspräfix,375px ohne Seitenüberlauf, Fokus über Polling erhalten, keine JS-Seitenfehler. Desktop-/Mobilbilder geprüft. Vorheriger Pilotbrowser ebenfalls4PASS.
- Zehn lesende Launcher-Guards: gültige Aufgabe/Listener akzeptiert; sechs simulierte Task-XML-Änderungen, fremdes Kommando, veraltete Prozesszeit und Nicht-Loopback abgelehnt. Keine echte Taskmanipulation. Vier Python-Voraussetzungstests bestanden. Die erste Testharness-Logbereinigung und eine eigenständige Journal-Importreihenfolge wurden korrigiert; Diagnosebelege erhalten, Engine nicht verändert.
- Abschließend134/134 Original- und103/103 Kandidatenhashes identisch. Alle sieben Dauerinstanzen gleicher PID/`pong`, Taskaktionen unverändert. Keine F:-Synchronisation oder kanonische Quellen-/Templateübernahme.
- Astra-Abschlussnachprüfung: kein neuer blockierender Befund im geprüften Umfang. Kein unabhängiger zweiter Vollsuite-Lauf durch den Prüfer. Die Engine ist unverändert; ihre zuvor geprüften431PASS/3Windows-Skips gelten zum gepinnten Kandidaten, sie wurden für diesen reinen Pilotstart nicht nochmals ausgeführt.

Belege: `runtime/rw-gv2-pilot-8110-20261004/REAL_21M_RESULT.json`, `JOURNAL_REPLAY_RESULT.json`, `STOP_RESULT.json`, `RESTART_RESULT.json`, `BROWSER_RESTART_RESULT.json`, `LAUNCHER_GUARD_RESULT.json`, `SOURCE_SAFETY_FINAL.json`, `LIVE_FINAL.json` und `service.log`.

| Paket | Stand |
|---|---|
| GV-2/UI-2 isolierte Umsetzung |100 % des begrenzten Pakets|
| GV-2 Pilot: echter erster21-Minuten-Zyklus, Journal-Replay, sauberer Restart |100 % des beschriebenen Nachweises|
| Zweiter Echtzeit-Trendzyklus/Dauerlauf und Bedienabnahme |offen|
| Übernahme auf8103–8109 / Quellen-/F:-Abgleich |0 % dieses Kandidaten|
| VF-2 persönliche Felder/Auftragssnapshot |0 % Umsetzung, genehmigter nächster Block|
| VF-3 heuristische Suche / EXP-1 Radi144-Modus |geplant,0 % Umsetzung|
| Aurelia/Modul_Templates Delta |Entwurf fertig; kanonische Übernahme0 %|
| S4.8 Integration |0 % Freigabe|

Pilot erreichbar auf http://127.0.0.1:8110/; sichtbarer synthetischer Hinweis. Unter Broadcast→Sitzungshistorie lassen sich beide künstlichen Sitzungen ansehen. Eigene manuelle Aufgabe, kein Pilot-Anmeldetrigger; 8103–8109 behalten ihren unabhängigen Dauerstart. Browseröffnung im Codex-Panel wurde nur als queued quittiert, nicht als sichtbar geöffnet bestätigt.

Nächster Entwicklungsschritt: VF-2 persönliche Felder und unveränderlicher Auftragskontext gemäß bestätigtem Plan; ursprüngliche Analysewerte/Algorithmen erhalten. Liveübernahme und Template-/F:-Sync bleiben gesonderte kontrollierte Schritte.

Begrenzter lokaler Checkpoint: `checkpoints/RadiWorks-GV2-Pilot-20261004-203257`. Enthält geprüfte Kandidaten-/Pilotdateien und Belege; reale und synthetische Laufzeithomes sowie Schlüssel nicht enthalten. Kein vollständiges F:-Projektbackup.
