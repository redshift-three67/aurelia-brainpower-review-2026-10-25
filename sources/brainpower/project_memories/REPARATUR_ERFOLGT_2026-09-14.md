# Gezielte Paketvervollständigung erfolgreich — 14.09.2026

Betreiberfreigabe: „Ja, gerne ... Go!“ für Schritt 1 und 2 des Reparaturvorschlags: gezielte Paketvervollständigung und Nachprüfung. Kein Neustart und kein Versionsupgrade freigegeben oder ausgeführt.

## Durchgeführte Änderungen

- Temporärer SSH-Zugang als installer funktioniert; Shell über F2 in Installer-UI. Verifizierter Hostkey unverändert.
- Alte conffiles von ubuntu-advantage-tools mit dpkg-MD5-Werten verglichen: alle Paketoriginale, keine Betreiberanpassungen. Neue Paket-conffiles extrahiert und vorhandene Unterschiede geprüft: normale Herstelleränderungen an APT-Hooks, Client-Defaults, MOTD und Release-Upgrade-Hook.
- Backup im Zielsystem: /root/brainpower-repair-20260914-Ox7x6H (in Live-Umgebung unter /target/root/...). Enthält ursprünglichen dpkg-Status, alte Konfigurationen, ursprüngliche resolv.conf-Verknüpfung, extrahiertes Paket und repair.sh/repair.log. Kein vollständiges Datenträgerbackup und keine automatische Paketrollback-Zusage.
- Erster Paketdownload scheiterte an fehlender DNS-Auflösung im chroot: resolv.conf zeigte auf noch nicht vorhandenes /run/systemd/resolve/stub-resolv.conf im Ziel. Für Download/Reparatur durch Live-Resolverkopie ersetzt, danach ursprünglichen Symlink exakt wiederhergestellt.
- Nur ubuntu-advantage-tools aktualisiert und ubuntu-pro-client sowie ubuntu-pro-client-l10n neu installiert: jeweils 37.2ubuntu~22.04.1. Über APT vom bestehenden signierten Jammy-Paketbestand bezogen; keine Quellenänderung und kein apt update.
- Scoped Installation der drei festen Versionen mit --no-download und --force-confnew, nachdem alle vorhandenen betroffenen Konfigurationen als unangepasste Paketoriginale geprüft und gesichert waren. Keine globale dpkg-Einstellung verändert.
- /dev,/proc,/sys nur für chroot-Reparatur eingebunden; rekursive Mounts auf slave gesetzt. Temporäres policy-rc.d exit 101 verhindert Dienststarts. Alle eigenen Hilfsmounts und policy-rc.d danach entfernt. /run des Live-Systems wurde nicht ins Ziel gebunden.
- repair.sh und Paketlauf erfolgreich, REPAIR_EXIT=0. Vorhandene Partitionierung, LUKS-Passphrase, RAID-Layout, Bootreihenfolge und SSH-Authentisierung im Ziel nicht verändert.

## Nachprüfungen

| Prüfung | Ergebnis |
|---|---|
| dpkg --audit | Keine Befunde, Exit 0 |
| apt-get -s check | Exit 0, keine gemeldeten Abhängigkeitsfehler |
| Erneute Simulation derselben drei Pakete | 0 Änderungen; alle drei in Version 37.2ubuntu~22.04.1 installiert |
| Neue conffiles | Alle neun entsprechen dem neuen Herstellerpaket |
| RAID md0/md1 | Beide [2/2] [UU] |
| fstab | Alle referenzierten Geräte im Live-System vorhanden |
| GRUB-Syntax | grub-script-check Exit 0 |
| Kernel/Initramfs | 5.15.0-191-generic weiterhin vorhanden |
| Resolver | Ursprünglicher Symlink ../run/systemd/resolve/stub-resolv.conf wiederhergestellt |
| Hilfsmounts/policy-rc.d | Eigene Mounts entfernt, policy-Datei entfernt |
| Weitere Paketupdates | 100 zurückgestellt im Sinne nicht ausgeführt; keine vollständige Systemaktualisierung |

Nicht als neue Hauptfehler behandeln: dpkg konnte altes nichtleeres /etc/ubuntu-advantage-Verzeichnis nicht entfernen (neues Paket benutzt es); needrestart-Microcode-Warnung im Live-chroot blieb. Kein Beleg, dass vollständiger späterer Hardware-/Bootcheck entfallen darf.

## Offene Schritte / Grenzen

Die konkrete Paketsperre wurde behoben, aber Installer-Anzeige/Backend wurde nicht künstlich auf Erfolg gesetzt und unattended-upgrades nicht erneut global gestartet. Echte Bootfähigkeit, Passphrase-Eingabe, erste cloud-init-Ausführung mit klaus999, Netzwerk und SSH unter installiertem Ubuntu sind noch zu testen. Deshalb keine vollständige Installations-/Produktabnahme.

BootOrder unverändert: 0002 (PXE),0000 (Ubuntu),0004 (Ubuntu zweite ESP),0003 (weiteres PXE),0001 (EFI Shell). Vor Neustart gemeinsam mit Betreiber Bootweg festlegen und KVM plus LUKS-Passphrase bereithalten. NICHT „Restart installer“ oder „Continue to try installation again“ auswählen. Einen kontrollierten Bootversuch getrennt abstimmen.

Nach erfolgreichem Boot: vollständige 22.04-Aktualisierung, anschließend regulärer Wechsel nach Ubuntu 24.04 nach entsprechender Freigabe. Fünf Produktgates, Testpflicht und automatische Governor-Reviews unverändert. Temporären Installer-Schlüssel/Passwortzugang nach Abschluss gezielt beseitigen, keine privaten Schlüssel archivieren.

## Lokaler Nachweis

artifacts/server-repair-2026-09-14.log ist die per SSH gelesene Original-repair.log. Enthält Ablauf und Exit 0, keine privaten Schlüssel oder Passwörter. Historische Vorbefunde: REPARATURBEFUND_2026-09-14.md; SSH_TEMP_ZUGANG_2026-09-14.md. Die vorherigen Pausenbeschreibungen sind bezüglich Zugang und Paketstand überholt.
