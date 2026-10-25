# Testserverzugang für das Codex-Projekt rauch-heilpraktiker.de

Der getrennte dauerhafte Zugang zum gemeinsamen Ubuntu-Testserver ist eingerichtet und am 16.10.2026 mit einer neuen IPv4-Verbindung geprüft.

- Host: `193.142.40.36` (`vm2565.ipp-vps.net`).
- Benutzer: `rauch-web-test`, UID/GID 1001, Home `/home/rauch-web-test`.
- Eigenes lokales SSH-Profil: `C:\Users\Hubert111\.ssh\aurelia-lg2-permanent-20261016T061825Z\website\ssh_config`.
- Alias: `rauch-lg2-test`.
- Kein sudo und keine Docker-Gruppe. Aurelia-Dateien sind nicht freigegeben.
- Eigenes Schlüsselpaar ohne Ablaufdatum, einzeln widerrufbar. Private Datei weder in Git noch in Cloud-Jobs/Container übertragen.

Verbindungsprobe auf diesem Windows-Steuerrechner:

```powershell
ssh -4 -F "C:\Users\Hubert111\.ssh\aurelia-lg2-permanent-20261016T061825Z\website\ssh_config" rauch-lg2-test "id -un"
```

Erwartet: `rauch-web-test`. Das Profil enthält den bestätigten Hostschlüssel und erzwingt die eigene Identität. Nicht auf Passwortlogin oder eine andere Identität ausweichen, wenn die Probe fehlschlägt.

Dieser Zugang betrifft ausschließlich die parallele Testumgebung. Kein Zugang zur bestehenden Website, keine DNS-/Hostingänderung oder Berechtigung für Aurelia- oder Serververwaltung. Die getrennte Testbasis ist am 16.10.2026 abgenommen: eigener rootloser Docker-Daemon `unix:///run/user/1001/docker.sock`, Gesamtbudget 1 CPU/4 GiB RAM/512 Tasks und Vorschau ausschließlich auf 127.0.0.1:18113. Andere Projektports und -Sockets bleiben gesperrt. Gemeinsamer Kernel ist keine vollständige VM-/Mandantenisolation.

Auf Betreiberwunsch am 16.10.2026 ohne Dienstneustart erhöht: `MemoryMax=4G` (feste RAM-Obergrenze), `MemoryHigh=2G` (weiche Rückgewinnungs-/Drosselgrenze), `MemorySwapMax=256M` unverändert. Persistente systemd-Konfiguration und aktive cgroup-Grenzen wurden übereinstimmend geprüft. Dies ist das gemeinsame Budget aller Prozesse dieses Projektbenutzers, keine RAM-Reservierung und keine automatische Erhöhung individueller Containerlimits. Aurelia behält sein eigenes unverändertes Budget. Sicherung und Nachweis: `checkpoints/LG2-Website-4GiB-20261016T153824Z/RESULT.json`; serverseitiger Rückfallstand unter `/root/aurelia-checkpoints/website-budget-20261016T153826Z`.

Eigener Vorschautunnel auf diesem Windows-Rechner (Konsole geöffnet lassen, zum Beenden Strg+C):

```powershell
ssh -4 -F "C:\Users\Hubert111\.ssh\aurelia-lg2-permanent-20261016T061825Z\website\ssh_config" -o ClearAllForwardings=no -o ExitOnForwardFailure=yes -N -L 127.0.0.1:18113:127.0.0.1:18113 rauch-lg2-test
```

Danach `http://127.0.0.1:18113/` öffnen. Derzeit erscheint nur der synthetische Bereitschaftsnachweis (`project: rauch-web-test`), noch keine Website. Vor Livekorrekturen eigene Quellenfreigabe, bereinigten Projektumfang und reversible Testversion festhalten. Ausschließlich die eigene Fixture `lg2-readiness-unix` ablösen; andere Projektcontainer nicht anfassen.

Die eigene Benutzer-unit `lg2-preview.service` betreibt nginx mit `/home/rauch-web-test/testbase/nginx.conf`, festem Upstream `/home/rauch-web-test/testbase/socket/backend.sock` und eigenem Laufzeitverzeichnis. Appcontainer bleiben ohne veröffentlichte Ports im internen Docker-Netz und erhalten nur dieses dedizierte Socketverzeichnis; niemals Home, SSH-Verzeichnis oder Docker-Socket einbinden. Ein passender Unix-Socket-Backendserver ist nötig (z.B. statischer nginx oder Uvicorn --uds). Der jetzige Nachweis ist kein Test einer konkreten Website, WebSocket-Anwendung oder Produktionsmigration. [Technische Abnahme](LG2_TESTBASIS_ABNAHME_2026-10-16.md).

## Verwendung im anderen Codex-Projekt

Das Öffnen oder Aktivieren eines Projekts übergibt keinen SSH-Zugang automatisch. Auf diesem Windows-Steuerrechner kann der Website-Task die obige eigene Konfiguration nutzen, sobald er diese Anleitung ausdrücklich erhalten hat. Einmal dort mitteilen:

> Lies C:\Users\Hubert111\Documents\Brainpower\docs\LG2_WEB_TESTZUGANG.md und prüfe den dort beschriebenen eigenen Testserverzugang. Verwende ausschließlich rauch-web-test; keine Admin- oder Aurelia-Zugänge.

Für spätere Sitzungen kann das Website-Projekt diese Anleitungsreferenz in seiner eigenen AGENTS.md festhalten. Hier wurde keine Datei im Website-Projekt geändert und keine Nachricht an den anderen Task gesendet. Auf einem anderen Rechner oder in einer Cloud-Umgebung ist dieser lokale private Schlüssel nicht automatisch vorhanden; dafür einen eigenen begrenzten Zugang vorbereiten und separat prüfen, keine private Schlüsseldatei in Projekt-/Cloud-Inhalte kopieren.
