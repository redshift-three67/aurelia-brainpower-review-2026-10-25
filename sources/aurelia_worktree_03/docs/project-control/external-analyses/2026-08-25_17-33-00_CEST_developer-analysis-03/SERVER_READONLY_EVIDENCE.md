# Sanitierte Read-only-Serverevidenz

**Erhebung:** 2026-08-25, nach Eingang der V3
**Zielidentität:** `root3091.ipp-srv.net`, Debian Linux, Kernel
`6.1.0-51-amd64`
**Zugang:** vorhandener OpenSSH-Schlüssel des Kontos `klaus999`,
`BatchMode=yes`, strikte Host-Key-Prüfung
**Mutation:** keine

## Schutzgrenzen der Erhebung

- keine Konfigurationsänderung;
- kein Neustart und kein Dienststart/-stopp;
- keine Paketinstallation;
- keine Firewalländerung;
- kein Docker-Prune und keine Volumenänderung;
- keine Ausgabe von Passwortwerten, privaten Schlüsseln oder Quell-IP-Adressen;
- Cron wurde nur über Zählungen und Pfad-/Topologieaussagen geprüft;
- externe Erreichbarkeit wurde nur für die von V3 ausdrücklich genannten
  TCP-Ports durch Verbindungsaufbau geprüft, ohne Anmeldung.

## E-01 — SSH und Privilegien

| Beobachtung | Read-only-Nachweis | Urteil |
|---|---|---|
| Root-SSH | effektive SSHD-Konfiguration: `permitrootlogin yes` | bestätigt |
| Passwortauthentifizierung | effektiv `passwordauthentication yes` und `authenticationmethods any` | bestätigt |
| Root-Passwort | Kontostatus `P` | gesetzt/nutzbar |
| Root-Schlüssel | drei aktive Datensätze in `/root/.ssh/authorized_keys` | bestätigt, Inhalte nicht gelesen |
| Root-Passwortanmeldungen | acht erfolgreiche `sshd`-Ereignisse seit 2026-08-01: sechs am 19.08., zwei am 21.08. | bestätigt; am 2026-08-25 vom Betreiber als eigene, autorisierte Servereinrichtung bestätigt |
| `klaus999` | `(ALL) NOPASSWD: ALL` vorhanden | bestätigt |
| Docker-Gruppe | `klaus999` ist Mitglied | zusätzlich root-äquivalent |
| Fail2ban | 23.305 Fehlversuche, 4.623 Bans zum Prüfzeitpunkt | bestätigt; kein Kompromittierungsbeweis |

Die Root-Anmeldungen wurden prozessgefiltert aus dem Systemjournal gezählt.
Eine vorherige `auth.log`-Zählung wurde verworfen, weil der Suchbefehl selbst
über `sudo` im Log auftauchte und einen Selbstbeobachtungseffekt erzeugte.

**Betreiberabgleich vom 2026-08-25:** Der Betreiber bestätigte im
Projektthread, dass sämtliche acht Root-Passwortanmeldungen von ihm selbst bei
der Einrichtung des Servers durchgeführt wurden. Sie werden daher nicht als
Incident-Indikator klassifiziert. Die unsichere Root-SSH-Konfiguration bleibt
als eigenständiger Härtungsbefund bestehen.

## E-02 — Systemd und Container

`systemctl --failed` meldete zehn, nicht neun, fehlgeschlagene Units:

- `iptables-restore.service`;
- `radiquant4-api.service`;
- `radiquant4-backup.service`;
- sechs `radiquant4-engine-*.service`;
- `radiquant4-runtime-guardian.service`.

Parallel waren 15 von 19 Docker-Containern aktiv. API, sechs Engines,
PostgreSQL, Redis-Instanzen und Worker liefen überwiegend gesund in Docker;
`radiquant4-strapi` befand sich in einer Neustartschleife. Die Namens- und
Portüberdeckung stützt den Verdacht einer Doppelorchestrierung, ersetzt aber
noch keine Unit-/Compose-Eigentümermatrix.

## E-03 — Netzwerk und Firewall

- Laufzeit-Firewall: IPv4-Policy `INPUT DROP`; UFW-, Docker-, Libvirt- und
  Fail2ban-Ketten aktiv.
- `iptables-restore.service`: aktiviert, aber seit 2026-08-01 fehlgeschlagen.
- Lokal an alle Interfaces gebunden waren unter anderem 25, 80, 443, 8000,
  8080, 8443, 9090, 3001, 3389 und 6556.
- Von einem externen Prüfpunkt erreichbar waren 80, 443, 8000 und 3389.
- Von demselben Prüfpunkt nicht erreichbar waren 25, 8443, 8080, 9090, 3001
  und 6556.

Damit ist V3 für Alt-API 8000 und xRDP 3389 bestätigt. Die pauschale
Bezeichnung aller lokal gebundenen Ports als öffentlich ist widerlegt. Ein
einzelner externer Prüfpunkt beweist umgekehrt keine globale Unerreichbarkeit.

## E-04 — Backup und Speicher

- `/opt/radiquant4/backups` liegt auf `/dev/md3`, also derselben
  Fehlerdomäne wie das Root-Dateisystem.
- Der Benutzer-Cron enthält vier Backup-/Redis-bezogene Zeilen und genau eine
  `PGPASSWORD`-Zuweisung; der Wert wurde nicht ausgelesen.
- Sichtbare Cron-Dateien enthalten mehrere lokale Legacy-Backups.
- Der Timer `radiquant4-backup.timer` existiert; die zugehörige Service-Unit
  ist fehlgeschlagen.
- Im Benutzer-Cron war kein Verweis auf die geprüften Offsite-Werkzeuge oder
  Remoteprotokolle sichtbar.

Aus dem Server allein kann nicht ausgeschlossen werden, dass ein Provider-
Snapshot oder ein extern initiierter Pull existiert. Solange der Betreiber
keinen externen Zielnachweis und keinen Restore-Test vorlegt, ist WV01
operativ als unerfüllt zu behandeln.

Dateisystemstand: `/dev/md3`, 1,8 TiB, 1,1 TiB belegt, 667 GiB frei, 62 %.

Docker meldete:

| Typ | Gesamt | Aktiv | Größe | Rückgewinnbar |
|---|---:|---:|---:|---:|
| Images | 235 | 17 | 200,2 GB | 185,1 GB |
| Container | 19 | 15 | 1,962 MB | 5,75 kB |
| Volumes | 57 | 11 | 15,02 GB | 5,511 GB |
| Build-Cache | 615 | 0 | 3,302 GB | 3,302 GB |

`reclaimable` bedeutet nicht, dass eine sofortige Löschung betrieblich sicher
ist. Ohne Abhängigkeitsinventar, Backup und Rollback wurde nichts bereinigt.

## E-05 — GPU, CPU, RAID und Swap

- NVML scheitert mit Driver-/Library-Version-Mismatch.
- geladenes NVIDIA-Kernelmodul: 535.261.03;
- installierte Userland-Bibliothek/Treiber: 535.309.01;
- DKMS 535.309.01 ist für Kernel 6.1.0-51 und 6.1.0-52 installiert;
- `nvidia-cuda-toolkit` ist nicht installiert;
- 6.1.0-52 ist installiert, laufend ist 6.1.0-51.

Ein kontrollierter Neustart dürfte den geladenen Modulstand angleichen, ist
aber ohne Boot-, Rollback-, Dienst- und Out-of-Band-Plan keine freigegebene
Maßnahme.

`md0`, `md1` und `md3` zeigten `[UU]`. `md2` war `clean`, aber
`resyncing (PENDING)` und nicht als Swap aktiv. Aktiv war stattdessen ein
32-GiB-Swapfile unter `/opt`. Deshalb ist „Hardware vollständig gesund“ ohne
SMART-, Temperatur-, Speicher- und Restore-Evidenz zu stark.

`lscpu` meldete für den Ryzen 5 9600X einen Maximalwert von 8424,6094 MHz.
Der Hersteller spezifiziert maximal 5,4 GHz; der Messwert ist daher als
Telemetrie-/Firmwareanomalie zu behandeln, nicht als bestätigte
Hardwareeigenschaft.
