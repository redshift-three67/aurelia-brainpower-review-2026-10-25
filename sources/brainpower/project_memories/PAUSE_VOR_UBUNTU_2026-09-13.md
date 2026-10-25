# Pause vor Ubuntu-Initialisierung – 13.09.2026

Arbeitsverzeichnis: C:/Users/Hubert111/Documents/Brainpower.
Checkpoint: checkpoints/2026-09-13_PAUSE_VOR_UBUNTU.

## Neueste Betreiberanweisung

Der Betreiber sichert vor der Initialisierung noch etwas und kehrt nach einer Pause zurück. Die Sicherung ist angekündigt, nicht als abgeschlossen bestätigt. Während dieser Pause keine Serverinitialisierung, Neustarts, Partitionierung, Installation oder Modell-/Entwicklungsaufträge starten. Bei Rückkehr zuerst Abschluss seiner Sicherung und aktuellen Serverstand berücksichtigen. Nicht aus der früheren Aussage „keine Altprojekte zu sichern“ ableiten, dass seine jetzt angekündigte Sicherung übersprungen werden darf.

## Gesicherter fachlicher Stand

- Server läuft laut Betreiber noch unter Debian; Ubuntu und Aurelia sind dort nicht eingerichtet. Lokale Projekte bleiben unverändert. Grundsätzlich gewünschter Neuaufbau ersetzt keine konkrete Datenträger-/Layoutfreigabe.
- Bestätigter Server 185.242.115.210, Nutzer klaus999, RDP/SSH; Provider-IPMI/KVM vorhanden. Keine eigene Serververbindung oder Serveraktion in dieser Runde.
- Backupspeicher 1 TB G2 zugehörig und laut Betreiber einsatzfähig. Keine Backupjobs/Restore-Ergebnisse technisch nachgewiesen. Künftiges Ubuntu erhält Backup und Monitoring; isolierter Restore erfolgt nach Einrichtung. Aktuelle private Sicherungsabsicht siehe oben.
- BMC-Bilder: vier DDR5-Module mit je 32768 MB, NoECC; Ryzen 5 9600X mit 6 Kernen/12 Threads; zwei grün angezeigte Netzteile. Keine vollständige Live-Hardwareabnahme.
- df-h-Bild: /dev/md3 als / ca. 1.8 T, 1.1 T belegt; /dev/md1 als /boot ca. 990 M; /dev/md0 als /boot/efi ca. 255 M. Physische NVMe, RAID-Mitglieder, genaue Kapazitäten/IDs fehlen. Keine Gerätezuordnung aus md-Nummern ableiten.

## Vorliegender Plan und neue Empfehlung

Quelle: C:/Users/Hubert111/Documents/ChatGPT/Aurelia/docs/superpowers/specs/2026-08-25-aurelia-ground-zero-server-design.md, Abschnitte 3 und 5.

Plan: Ubuntu Server 24.04.4 AMD64, offizielles geprüftes Abbild, UEFI. Zunächst ohne GUI; minimales GNOME später. Zwei physische 2-TB-NVMe: getrennte EFI-Partitionen, eigenes RAID1 für /boot, zweites System-RAID1, darauf LUKS2, darin LVM vg_aurelia.

Größenwiderspruch im alten Plan: 1640 GiB LV-Zuteilung lässt bei nominell 2 TB gespiegelt höchstens 11.95 Prozent vor Boot/Metadaten frei; gefordert sind mindestens 15 Prozent.

Noch NICHT final angenommener Korrekturvorschlag:

| Bereich | Vorgeschlagen |
|---|---|
| EFI je NVMe | ca. 1 GiB; eigenständige ESP, kein RAID; Installer kann ESP automatisch erzeugen |
| /boot-Mitglied je NVMe | 2 GiB; gemeinsames RAID1, ext4 /boot |
| System-Mitglied je NVMe | Rest; gemeinsames RAID1, LUKS2, vg_aurelia |
| lv_root | 120 GiB, ext4 / |
| lv_home | 80 GiB, ext4 /home |
| lv_log | 64 GiB, ext4 /var/log |
| lv_postgres | 384 GiB, ext4 /var/lib/postgresql |
| lv_aurelia | 704 GiB, ext4 /srv/aurelia; früher 768 GiB |
| lv_build | 128 GiB, ext4 /srv/build; früher 192 GiB und Mountpoint offen |
| lv_swap | 32 GiB innerhalb Verschlüsselung |
| VG-Reserve | verbleibend, rechnerisch ca. 340 GiB; tatsächliche Kapazität prüfen, mindestens 15 Prozent |

Zuteilung 1512 GiB. Die vorgeschlagene Aufteilung ist nicht auf dem Server ausgeführt, nicht in einem Installer getestet und noch nicht der verbindliche externe Projektplan.

## Exakter Wiedereinstieg

1. Der Betreiber meldet sich nach seiner Sicherung. Aktuellen Serverzustand erfragen/beachten, keine stillschweigende Neustartaktion.
2. Noch ausstehende lesende Debian-Ausgaben entgegennehmen:

```bash
lsblk -e 7 -o NAME,PATH,SIZE,TYPE,FSTYPE,MOUNTPOINTS,MODEL
cat /proc/mdstat
ls -l /dev/disk/by-id/ | grep nvme
```

3. Reale NVMe-IDs, Kapazitäten und RAID-Zustand abgleichen. Netzwerkparameter aus Provider-Panel festhalten, nicht raten. Zugangsdaten/Schlüssel nicht im Chat anfordern.
4. Exaktes Installationsmedium und UEFI-Boot klären: Provider-Auswahl „Ubuntu 24.04 Noble LTS manuell“ belegt nicht die im Plan genannte Unterversion. Der zuletzt aufgerufene offizielle /24.04.4/-Webindex lieferte einen 24.04.5-Titel; keine unbestätigte ISO-URL/Prüfsumme als geprüft ausgeben, keine stille Versionsänderung. Originalabbild/Prüfsumme oder begründete Versionsentscheidung separat prüfen.
5. Manueller Subiquity-Weg in Anleitung: Custom storage layout; beide Datenträger als Bootgeräte; getrennte ESP; /boot-RAID1; System-RAID1; verschlüsselte LVM-Gruppe aus dem System-RAID; LVs und freie VG-Reserve. Tatsächliche Installer-Version/Optionen prüfen. Keine Standardpartitionierung oder unverschlüsselte Ersatzlösung still wählen.
6. Speicherübersicht vor endgültiger Schreibbestätigung konkret prüfen und freigeben lassen. Provider-Speichern startet laut Panel bereits neu. Kein Klick ohne den konkreten Kontext.
7. Später: LUKS2-/Bootprüfung über beide NVMe, Recovery-Passphrase separat sichern. Initiale manuelle Entsperrung über Fernkonsole berücksichtigen; unbeaufsichtigter Reboot noch nicht zugesichert. Backupsystem/Monitoring und Restore des neuen Basiszustands; Module erst nach eigenen Gates integrieren.

## Governor und lokale Projektarbeit

Der letzte geprüfte Governorstand war 0.5.0, Sol, Beobachtung an und automatische Modellreviews aus. Tatsächlicher Zustand wird im Checkpoint state.json erfasst. Fünf Aufnahmen bleiben unbestätigt, keine Gruppenstrategie automatisch übernommen. Quellen-/Gate-/Testvorbereitung: artifacts/QUELLEN_GATE_TESTPLAN_2026-09-13.md. Keine neuen Produkttests ausgeführt. Erst nach passenden Voraussetzungen neue aktuelle Tests; Ubuntu ist spätere Produktabnahmeumgebung.

## Wortlaut zur Fortsetzung

> Wir setzen am Pausenstand PAUSE_VOR_UBUNTU_2026-09-13 fort. Lies project_memories/PAUSE_VOR_UBUNTU_2026-09-13.md und SERVER_KLARSTELLUNG_2026-09-13.md. Ich hatte vor der Initialisierung noch eine Sicherung angekündigt; beachte deren tatsächlichen Abschluss. Prüfe als Nächstes meine lsblk-/mdstat-/by-id-Ausgaben, die konkreten Zielgeräte und die vorgeschlagene korrigierte Partitionierung. Kläre das genaue Ubuntu-Installationsmedium und begleite den manuellen Installer bis zur geprüften Speicherübersicht. Keine automatische Initialisierung oder Schreibbestätigung, keine ungeprüfte Wiederherstellung von Checkpointdateien und keine automatische Aktivierung der Modellreviews. Lokale Projekte, Produktgates und meine endgültige Auswahl bleiben maßgeblich.

## Umfang der Sicherung

Lokaler Workbench-Checkpoint mit Programm, Konfiguration, Dokumenten, konsistenter Journal-DB und ausgewählten Artefakten. Kein Backup des Debian-Servers, der fünf vollständigen Produktrepositories, von Hermes/CC Switch oder Zugangsdaten. Alte Checkpoints bleiben erhalten. Normale Fortsetzung benötigt kein Zurückkopieren. Bei tatsächlicher Wiederherstellung zuerst Dienst stoppen und vorhandenen Stand bewahren; Programm/DB zusammen wiederherstellen, keine alten WAL-/SHM-Dateien beimischen und externe Pfade prüfen.

Referenzen zur Anleitung:
- https://faq.ip-projects.de/de-de/10-server/70-ip-projects-server-panel-quick-start
- https://faq.ip-projects.de/de-de/13-dedicated-server/21-eigene-iso-installieren
- https://canonical-subiquity.readthedocs-hosted.com/en/latest/howto/configure-storage.html
- https://github.com/canonical/subiquity/blob/24.04.1/subiquity/ui/views/filesystem/lvm.py
