# Aurelia P0 – WSL-Referenzbasis, 10.10.2026

## Ergebnis und Grenze

Die vom Betreiber neu eingerichtete WSL2/Ubuntu-24.04-Basis startet wieder. Eine frische, getrennte Distribution `Aurelia-Referenz-24.04` wurde auf F: eingerichtet; Docker und Compose sind dort installiert. Kleine Speicher-/Netz-/HTTP-Proben im bereits gestarteten Zustand sind teilweise bestanden. **P0 insgesamt bleibt offen; kein Supabase- oder Anwendungsstart, kein P1/P2-Abschluss.**

Beim erneuten Anlauf liefen äußere WSL-Aufrufe ins Timeout. Die Voraussetzungen für den kontrollierten Dienst-/Distributionsneustart wurden nicht erreicht; dieser wurde weder durchgeführt noch als bestanden oder gescheitert bewertet. Ein Docker-Hänger ist damit nicht bewiesen. Während eines früheren Starts waren Linux-I/O-Wartezustände und ein systemd-Starttimeout sichtbar. Ihre genaue Ursache und die Tragfähigkeit des vollständigen Stacks sind offen.

## Phasenstand

| Schritt | Nachgewiesen | Offen / Konsequenz |
|---|---|---|
| P0-R1 Betreiber-Reparatur | WSL2 2.5.9.0, Kernel 6.6.87.2; Ubuntu 24.04.5 startet; Defaultdistribution bleibt Ubuntu-24.04 | Kein Windows-Warmstartnachweis |
| P0-R2 Getrennte Grundlage | Frisches offizielles Ubuntu-Image mit signierter Prüfsummenliste; eigene Distribution und Linux-VHD auf F: | F: muss für diese Referenz verbunden sein; Dateitrennung ist keine vollständige Ressourcen-/Sicherheitsisolation |
| P0-R3 Container-Warmtest | Docker 29.9.0, Compose 5.6.0, Unixsocket; 64 MiB Testinhalt innerhalb 128-MiB-Limit, Swaplimit 0, kein OOM | Keine Aussage über PostgreSQL/Supabase-Volumen oder Gesamtspeicherlast |
| P0-R4 Netzwerkpfad | Interner Testdienst erreichbar im Container und vom Linuxhost; temporärer Host-Loopback-Relay von Windows erreichbar | Docker-Portveröffentlichung im ausschließlich internen Netz nicht wirksam; dauerhaften Zugang und vollständige Egress-Sperren separat bauen/testen |
| P0-R5 Wiederanlauf | Anlauf-Timeouts erhalten; zeitbegrenzte Hilfsprozesse beendet | Reproduzierbarer Kaltstart und I/O-Ursache offen; keine weiteren großen Stacks starten |
| P0-R6 Bestandsschutz | Acht bestehende Windows-HTTP-Endpunkte 200; Quellen-/PID-/Listenervergleich im Abschlussreceipt | HTTP 200 ist keine vollständige Funktionsabnahme |
| P0-D1 Backendvertrag | Aktive Auth/REST/Storage/Realtime/Functions-Caller und feste externe Zielbindungen begrenzt erfasst | Functions-/Cron-/Worker-Definitionen und technische Lokalbindung vor P1 vervollständigen |
| P1/P2 | Keine Anwendung oder Altklientendaten gestartet/importiert | Erst nach Runtime-, Zielbindungs-, Geheimnis-, Versions- und Ressourcenprüfung |
| P3–P8 | Bestehender Reasoning-/Matrix-/Entscheidungs-/Integrationsplan unverändert | Unabhängige P3-Aufnahme kann weiterlaufen; zentrale DB-Entscheidung und S4.8 bleiben separate Gates |

## Aufbau, Versionen und Sicherung

- Geschützter neuer Root: `F:\Aurelia-Lokaltest`, Unterordner `downloads` und `WSL`; ACL auf Betreiber und SYSTEM begrenzt. Bestehende Archive unter `F:\Hauptprojekt` nicht verändert.
- Image: `ubuntu-24.04.5-wsl-amd64.wsl`, 388975696 Bytes; SHA256 `bb415d824822c4b878125729af451a5d18fb13d1cf5cbed9a7393ad64ac6039e`. Signatur der Prüfsummenliste mit vorhandenen Ubuntu-Schlüsselringen rein lesend geprüft, gpgv Exit 0; Signer `843938DF228D22F7B3742BC0D94AA3F0EFE21092`.
- Pakete aus dem offiziellen Docker-Ubuntu-Repository, Schlüssel-Fingerprint `9DC858229FC7DD38854AE2D88D81803C0EBFCD88`:
  `docker-ce/docker-ce-cli=5:29.9.0-1~ubuntu.24.04~noble`, `containerd.io=2.4.1-2~ubuntu.24.04~noble`, `docker-buildx-plugin=0.38.0-1~ubuntu.24.04~noble`, `docker-compose-plugin=5.6.0-1~ubuntu.24.04~noble`.
- Docker-/containerd-Daten liegen innerhalb des Linux-Dateisystems auf F:, nicht als NTFS-Bindmount. Eigenes Daemon-JSON: data-root `/var/lib/docker`, Standard-IP `127.0.0.1`, json-file-Logs max-size 10m/max-file 3. Unixsocket verwendet; kein Docker-TCP-Zugang eingerichtet.
- Kein Docker Desktop, keine globale `.wslconfig`, kein Windows-Firewall-/Portproxy-/Dienst-/Pagefile-Umbau; keine eigene Änderung der ursprünglichen Ubuntu-Konfiguration. Kein globales `wsl --shutdown`. WSL-Ressourcen bleiben gemeinsam; die neue Distribution ist keine harte Sicherheitsgrenze.
- Linux-Paketplan und exakte Versionen unter `/root/aurelia-provision`; Installationsscript und aktuelle Prüfskripte im privaten Nachweispunkt. Dies ist ein Grundlagen-/Dokumentensicherungspunkt, kein vollständiger VHD-, Projekt-, Server- oder Schlüsselrestore.

Installationsreceipt meldet Exit 0. Eine nachfolgende Windows-Ausgabe schlug wegen cp1252/Unicode fehl; die Installation wurde deshalb nicht doppelt ausgeführt. Ein erster Readiness-Aufruf lief ins Timeout, spätere warme Client-/Daemon-/Compose-Abfragen bestanden. Diese unterschiedlichen Ergebnisse bleiben getrennt erhalten.

Offizielle Grundlagen: [Ubuntu-WSL-Installation](https://documentation.ubuntu.com/wsl/latest/guides/install-ubuntu-wsl2/), [Ubuntu-24.04-Artefakte](https://releases.ubuntu.com/24.04/), [WSL-Import in eigenes Verzeichnis](https://learn.microsoft.com/en-us/windows/wsl/use-custom-distro), [Docker für Ubuntu](https://docs.docker.com/engine/install/ubuntu/).

## Container- und Zugriffsbefund

BusyBox 1.37.0 wurde für Infrastrukturproben bezogen und dann ausschließlich über Digest `sha256:bdf57e528e45e4433820e045b29b4597825a1c9e38353532d90a01445013f82e` verwendet. Kein Produktcode oder Klientendatensatz lief in den Containern.

Die Speicherprobe hatte memory.max 134217728, memory.swap.max 0, pids.max 64, 67108864 Testbytes und OOM/OOM-kill 0. Ein eigenes internes Docker-Netz hatte keine externe Standardroute; Zugriff auf die reservierte Probeadresse 198.18.0.1 war nicht routbar. Das beweist nicht, dass DNS, Host-Proxys, Browser oder zukünftige Anwendungen keine Cloud erreichen könnten.

Der erste Windows-HTTP-Test schlug fehl. Schichtweise Nachprüfung ergab:

| Pfad | Befund |
|---|---|
| Container → eigener httpd:8080 | Eindeutiger Testinhalt korrekt |
| Linuxhost → Container-IP:8080 | Derselbe Inhalt korrekt |
| Angeforderter Docker-Hostport | HostConfig enthält 127.0.0.1:61220; tatsächliche NetworkSettings.Ports enthält `8080/tcp:null` |
| Linuxhost → 127.0.0.1:61220 | Verbindung verweigert |
| Windows → 127.0.0.1:61220 | Erst Timeout, in Folgeprobe Verbindung verweigert |
| Windows → temporärer Linuxhost-Relay:61221 → interner Container | HTTP 200 und exakt derselbe Inhalt; Relay endet nach zwölf Sekunden mit Exit 0 |

Damit ist ein lokaler Relaypfad grundsätzlich belegt; weder Docker-Portveröffentlichung noch eine dauerhafte Lösung sind abgenommen. Kein externes Zweitnetz, öffentliches Binding oder globaler Windows-Portproxy wurde als Umgehung eingerichtet. Alle eigenen Testcontainer/-netze wurden über genaue IDs entfernt; keine verbleibenden Testlistener auf 61220/61221. [Docker-Portgrenzen](https://docs.docker.com/engine/network/port-publishing/) sind bei der endgültigen Konfiguration zu beachten.

Ein eigener versteckter WSL-Client hielt die Probe für maximal 600 Sekunden offen; eine spätere Anlaufprobe war auf 180 Sekunden Linux-Keepalive angelegt, dessen tatsächlicher Linuxstart nicht belegt ist. Beide Windows-Clientprozesse sind im Abschlussinventar beendet; beide Distributionen stehen auf Stopped. Systemd-Dienste allein halten WSL laut [Microsoft](https://learn.microsoft.com/en-us/windows/wsl/systemd) nicht dauerhaft aktiv. Keine Windows-Autostartfähigkeit daraus ableiten.

## Ressourcen und Datenträgeralternativen

Vorbereitung: Windows rund 15,26 GiB RAM; Linux meldete rund 7,38 GiB sichtbaren RAM. Diese Werte sind nicht addierbar. Abschlussnahe Windows-Leseprobe: rund 3,74 GiB freie physische und 3,46 GiB freie virtuelle Kapazität; C: rund 23,12 GiB frei. F: meldet NTFS/Healthy und rund 378,06 GiB frei. Linux-`df`-Maximalgröße ist keine freie Hostkapazität.

F: ist über USB angeschlossen. Startdiagnosen zeigten I/O-Wartezustände; das beweist weder einen Datenträgerdefekt noch USB als alleinige Ursache. Vor vollständigem Supabase: Speicher-/I/O-/Kaltstartbudget des repräsentativen ersten Stacks unter bestehenden Windows-Instanzen messen. [Supabase nennt für vollständiges Selfhosting](https://supabase.com/docs/guides/self-hosting/docker) mindestens 4 GB RAM/40 GB Speicher, empfohlen 8 GB/80 GB; diese Hostwerte sind kein Nachweis unserer verfügbaren Reserve.

Betreiber bietet zusätzlich 64-GB-SD/USB3 und 120-GB-SanDisk-SSD an. SSD kann derzeit nur am selben Adapter wie F: angeschlossen werden; daher kein gleichzeitiger SSDvergleich oder Umzug erfolgt. SSD ist eine aussichtsreiche Reserve, ihre nutzbare Kapazität/Leistung unbekannt. SD kann separat auf Eignung geprüft werden; USB3 garantiert keine geeignete Datenbank-I/O-Leistung. Kein Formatieren/Überschreiben freigegeben oder erfolgt. F: vorerst verbunden lassen; kontrollierter Wechsel erst nach Zielklärung, Sicherung und bestätigtem Stillstand/Schlüsselbedarf aller betroffenen Pfade.

## Aktive Backendanforderungen – begrenzte Quellaufnahme

Gebunden bleiben Explorer `c69d5aa224018b0484efd90ae456a10aecc78a77` und Thom `18e6c12c238985da698f9a46743d893b30d61ba7`; je 20 manifestgebundene SQL-Migrationsdateien. Dies ist kein neuer Cloud-Schemaabgleich.

| Anwendung / Weg | Tatsächlicher Bedarf / Lokalgrenze |
|---|---|
| Explorer Auth, PatientManagerCloud, Copen-v2, SessionRecoveryDashboard | Auth und Postgres-REST; aktive Realtime-Kanäle zusätzlich, Polling allein ersetzt sie nicht |
| Explorer BohmClientFieldCalculator | Privater Storage `client-signatures`: Upload, signierte URLs, Entfernen |
| Explorer CopenGeneratorPage/HarmonizationManager/DatabaseManager | Aufrufe von `harmonization-worker`; vollständigen Function-/Worker-/Cron-Vertrag gesondert erheben |
| Explorer OCR | Tesseract-Worker-/Sprachassets lokal bündeln und Browser-Netzverkehr prüfen; keine Offlinefähigkeit behauptet |
| Explorer WorkerStatusMonitor/hardwareAlgorithms | Externer Google-HEAD-Latenztest im erreichbaren Weg; lokal kontrolliert adaptieren oder sichtbar begrenzen, keine beliebige Formel ersetzen |
| Explorer optional Ollama | Browser-localhost11434 ist nicht automatisch WSL-/Container-localhost |
| Thom RealtimeSyncService/RealtimeSyncWidget/Analyse | Festes externes WebSocketziel; reine VITE-URL-Änderung reicht nicht |
| Thom RealtimeHarmonizationService | https→wss-Umsetzung berücksichtigt lokales http→ws nicht; technischen Lokalvertrag prüfen |
| Thom ModelUpload/AnatomyResonanceViewer | Direkter Projekt-Storage-/Resumable-Pfad mit externer Fallbackkennung; weder unverändert starten noch Cloud-Token weiterreichen |
| Thom useMeridianDiagnosis | Erreichbarer Function-Aufruf; hardware-metrics, meridian-diagnosis und realtime-sync müssen passend lokal geprüft werden |

Function-/Trigger-Rohdefinitionen, Secrets und Datensätze gingen nicht an Helfer. Kein Backendstub als funktionaler Ersatz. PostgreSQL-17.6-Kompatibilität bleibt mit den erlaubten Cloud-Metadaten gesondert zu prüfen; keine zentrale DB-Technik entschieden.

## Fortsetzung und Rücknahme

1. P0: Anlauf-/I/O-Ursache und tragfähigen Datenträgerpfad gezielt klären; erst danach vollständiges Stackbudget und dauerhaften lokalen Zugang prüfen. Keine weiteren ungezielten WSL-Reparatur-/Globalparameterexperimente.
2. P0: Funktionen/Trigger/Cron/Worker, Realtime, Storage, Auth und feste externe Browser-/Serverziele mit lokalen Secrets/URLs/Assets vollständig binden. Egress samt Negativtests; zuerst nur Explorer-Stack, danach Thom.
3. P3 kann unabhängig fortgeführt werden: Radi144-Restgrenzen, RadiMorphic-Quell-/Owner-/Lease-Abdeckung und RadiFarben-Accessreferenzen. Algorithmen unverändert; P4 gemeinsame Matrix vor P5-Betreiberentscheidung.
4. Rücknahme zunächst nur eigene Testcontainer/-netze beenden und eigene Distribution geordnet stillsetzen. Nie automatisch `wsl --unregister`, VHD löschen, F: abziehen oder globale WSL-Konfiguration ändern. Die Rootfs-Ausgangsdatei, Prüfsummen, genaue Paketversionen und eigene Konfigurationen sind Wiederaufbaugrundlagen; kompletter VHD-/Apprestore ungetestet.

Privater Nachweispunkt: `runtime/aurelia-three-modules-20261009/reference-plan/p0-wsl-reentry-20261010-131856Z`. Vorherkopien, Installations-/Timeout-/Container-/Relay-/Livebelege und Nachherdokumente; `VERIFY.json`/`MANIFEST.json` sind maßgeblich für den abschließenden Hash-/Bestandsvergleich. Alte Wiederaufnahme vollständig erhalten. Keine neue F:-Gesamtsicherung, kein RadiWorks-Rollout, keine normative Modul_Templates- oder Governors-Routingänderung.

Helfer tatsächlich: Luna6/max für begrenzte aktive Backend-Calleraufnahme; Astra6/medium für Infrastruktur-/Netz-/Abschlussgrenzen. Ursprünglich abweichende Luna-Migrationszählung vor Übernahme berichtigt: Explorer20/Thom20. Chatleitung gemäß gewählter Route; kein Laufzeitmodell aus gespeicherten Defaults behauptet.
