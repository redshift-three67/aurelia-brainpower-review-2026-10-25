# LG2 – getrennte Testbasis abgenommen

Stand 16.10.2026, 12:42 Uhr Europe/Berlin. Ziel: Ubuntu-Testhost 193.142.40.36 / vm2565. Die Infrastruktur ist für die nächsten isolierten Projekt-Liveprüfungen vorbereitet. Noch keine Website oder RadiWorks-Produktversion auf diesen Host übertragen.

| Bereich | Tatsächlich geprüft |
|---|---|
| Zugang | Drei neue IPv4-Logins root/aurelia-ops/rauch-web-test; Projektnutzer ohne sudo/Docker-Gruppe, getrennte Homes |
| Container | Zwei eigene rootlose Docker-29.9.1-Daemons, systemd/cgroup v2; rootful Docker/Socket/Containerd maskiert |
| Gesamtlimits | Aurelia 5 CPU, MemoryHigh 8 GiB, Max 10 GiB, SwapMax 1 GiB, 1024 Tasks; Website 1 CPU, High 1 GiB, Max 2 GiB, SwapMax 256 MiB, 512 Tasks |
| Laufzeit | Synthetische Appcontainer intern, ohne veröffentlichte Ports; UID65532, read-only, alle Capabilities entfernt, no-new-privileges, 128 MiB/0,25 CPU/64 PIDs tatsächlich in cgroup-Dateien bestätigt |
| Vorschau | Je Benutzer eigener nginx, festes Unix-Socket-Ziel, nur 127.0.0.1:18112 bzw. :18113; nginx-Prozess-UID und Zugehörigkeit zum jeweiligen Gesamtbudget bestätigt |
| SSH-Tunnel | Eigenes HTTP für beide Projekte erfolgreich; fremdes Projekt, Reverse-Tunnel, beliebiges Ziel, Root-Key-Forward und Unix-Socket-Forward abgewiesen. Temporäre Prüftunnel wieder geschlossen |
| Trennung | Eigene HTTP-Ziele erreichbar; fremde HTTP-/Appsocket-/Docker-Socket-Zugriffe verweigert. Eigene persistente UFW-OUTPUT-Kette vor Loopback-/Established-Freigaben; positive und negative Zähler belegt |
| App-Netz | Externe IPv4-Verbindung, Host-SSH, fremde/Host-Loopbackports und externe DNS-Auflösung im synthetischen Appcontainer verweigert; IPv6 deaktiviert |
| Wiederanlauf | Beide Container neu gestartet, HTTP danach erfolgreich und gespeicherter Startzähler jeweils genau um eins erhöht |
| Abschluss | Änderung committed, unabhängiger Rückfalltimer inaktiv; SSH/Socket/Fail2ban/Chrony gesund, keine failed Units |

Docker veröffentlicht bei dieser ausschließlich internen Netzkonfiguration den angeforderten Port nicht. Deshalb bleibt das Appnetz intern; ein unprivilegierter Host-nginx vermittelt ausschließlich zu einem festen Unix-Socket. WebSocket-Upgrade-Header und ausgeschaltete Proxy-Pufferung sind konfiguriert, ihre spätere Produktfunktion ist hier noch nicht abgenommen. Nur das dedizierte Socketverzeichnis ist als Bind-Mount vorgesehen, niemals Home oder Docker-Socket. Socketverzeichnis 0777/Socket0666 liegen hinter dem jeweiligen nicht durchquerbaren Home0700; fremder Zugriff wurde negativ getestet.

Die Host-/Benutzerumgebung bleibt für Paketinstallation und Builds netzwerkfähig. Die nachgewiesene Egress-Sperre gilt für die geprüften Appcontainer. Gemeinsamer Kernel und dasselbe Windows-Betreiberkonto sind keine vollständige Mandanten-/VM-Isolation. Keine Zusicherung von AppArmor-Schutz für diese rootlosen Container aus dem aktivierten Host-AppArmor ableiten.

## Absicherung und Befunde

24 Linux-Regressionen erfolgreich, darunter Teilabbruch, Konflikterhalt, Wiederherstellung konfliktfreier rootverwalteter Ziele trotz fremder Projekt-Key-Änderung, echte geerbte Identitätsprüfung und transaktionsgebundener Commitnachweis. Luna/max lieferte die begrenzten Kandidatenfunktionen, Astra/medium prüfte den sicherheitsrelevanten Controller unabhängig; Befunde vor Apply korrigiert. Echte SSH-/iptables-Syntaxprüfung und systemd-Aufruf des kopierten Controllers erfolgreich. Keine reale destruktive Wiederherstellung oder Neustartabnahme daraus ableiten.

Genau vier Konfigurationsdateien geändert: SSH-Zugangssnippet, UFW-before.rules und die beiden öffentlichen authorized_keys. Andere geschützte Datei-Hashes unverändert, vorhandene IPv4-Laufzeitregeln nach Herausnahme der sechs eigenen Preview-Zeilen exakt gleich. UFW-Reload lud zusätzlich zwei bereits auf Disk vorhandene IPv6-Standardregeln (REJECT in ufw6-user-limit, ACCEPT in ufw6-user-limit-accept); keine Kettenverweise darauf und keine IPv6-Adressen/Routen. Diese begrenzte Regenerierung wurde separat ausgewiesen, nicht als bytegleiche IPv6-Laufzeit behauptet.

Rootgeschützter Konfigsicherungspunkt: `/root/aurelia-testbasis-checkpoint-20261016T104207Z`, 43 reguläre Konfig-/öffentliche Schlüsseldateien kopiert und hashgeprüft. Manifest SHA256 `a02c8d73713d34be36aba6359c240a91e9f949bb1ff5f1138bc4a883fbf72146`. Keine privaten Schlüssel, kein Vollbackup/off-host Restore oder Reboot-/Langzeitnachweis. Der vorher bestehende Kernel-Neustartbedarf und vier simulierte reguläre OS-Paketupdates wurden durch diese Einrichtung nicht erledigt; vor späterer Betriebsabnahme gesondert einplanen, kein Releaseupgrade.

Nachweise unter `checkpoints/Aurelia-LG2-IPv4-20261016T070215Z`: `PREVIEW-PROTOCOL-GREEN3.json`, `PREVIEW-PREPARE3.json`, `PREVIEW-COPIED-CONTROLLER-PROBE.json`, `PREVIEW-ROLLBACK-ARM.json`, `PREVIEW-APPLY.json`, `PREVIEW-POST-APPLY-LOGIN-*.json`, `PREVIEW-ACCESS-POST-APPLY-*.json`, `PREVIEW-TUNNEL-ACCEPTANCE.json`, `PREVIEW-RUNTIME-BEFORE.json`, `PREVIEW-RUNTIME-AFTER.json`, `PREVIEW-IPV6-*.json`, `PREVIEW-BOUND-PROOF.json`, `PREVIEW-COMMIT.json`, `PREVIEW-ACCESS-AFTER-COMMIT-*.json`, `TESTBASIS-CONFIG-CHECKPOINT.json`.

## Nachtrag – Website-Speicherbudget

Am 16.10.2026 auf ausdrücklichen Betreiberwunsch Website-Gesamtbudget von Max 2 GiB/High 1 GiB auf Max 4 GiB/High 2 GiB erhöht. Die obige Abnahmetabelle beschreibt den ursprünglichen Stand um 12:42 Uhr. Persistente Konfiguration und aktive Kernel-cgroup stimmen mit dem neuen Budget überein; 1 CPU, 256 MiB Swap und 512 Tasks bleiben gleich. Aurelia-Konfigurationshash und Ressourcenlimits unverändert, keine Dienste neu gestartet. Vorherige Website-Konfiguration rootgeschützt gesichert. Kein Reboot-/Lastnachweis daraus ableiten. Nachweis: `checkpoints/LG2-Website-4GiB-20261016T153824Z/RESULT.json`; aktuelle Übergabe `LG2_WEB_TESTZUGANG.md`.

## Fortsetzung

Website-Projekt bekommt den eigenen Zugang über `LG2_WEB_TESTZUGANG.md`; keine Nachricht dorthin gesendet, keine bestehende Website/DNS/Hosting geändert. Hier weiter mit RadiWorks C2a: Herkunft/Rechte und unabhängiges privates Quellziel, bereinigte Provenienz/Allowlist, danach Linux-Abhängigkeiten und kleinster Original-Pilot. Keine alte Profil-Git-Historie, Betreiberfälle/Medien/Kataloge/Schlüssel übertragen. Cloud-/Quellen-/P3/P4/P5-/Modul_Templates-Gates bleiben bestehen. Keine offene Reasoning-Umschaltung.
