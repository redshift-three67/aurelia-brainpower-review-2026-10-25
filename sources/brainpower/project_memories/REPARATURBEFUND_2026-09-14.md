# Reparaturfähigkeitsprüfung Ubuntu 22.04 am 14.09.2026

Aktuelle Ergänzung zu PAUSE_INSTALLER_SSH_2026-09-14.md und SSH_TEMP_ZUGANG_2026-09-14.md. Betreiber meldete Public-Key-Import über Windows-SSH als erledigt. Temporärer Schlüssel funktioniert jetzt, Hostkey unverändert und strikt geprüft. Installer-Anmeldeshell ist /usr/bin/subiquity-shell; normale SSH-Remote-Kommandos öffnen Installer-UI statt Shell. SSH mit PTY und F2 (ESC O Q) öffnete die vorgesehene Root-Diagnoseshell. Keine Reparatur, Paketinstallation, Formatierung, Bootänderung oder Neustart ausgeführt. Lediglich Terminalbreite verändert und lesende Diagnose/APT-Simulationen durchgeführt.

## Live-Befunde

| Bereich | Ergebnis |
|---|---|
| Zielmount | /target ist vg_aurelia-lv_root; separate Mounts für home, log, postgres, aurelia, build, boot, efi vorhanden |
| Paketprüfung | chroot /target dpkg --audit ohne Befund, Exit 0; apt-get -s -o Debug::NoLocking=1 check ohne gemeldete Abhängigkeitsfehler; apt-mark showhold leer |
| Abbruch | unattended-upgrades: Konfigurationsrückfrage ubuntu-pro-client; ubuntu-advantage-tools deshalb zurückgehalten; andere ausgewählte Upgrades installiert |
| Ursachenbeleg | Installierte /target/usr/bin/unattended-upgrade, Zeilen um 2374: successful_run verlangt unter anderem not pkg_conffile_prompt. Rückfrage bewirkt negativen Gesamterfolg trotz All upgrades installed. |
| Zusätzliche Warnungen | Im dpkg-Log /dev/pts nicht verfügbar und needrestart-Microcode-Warnung im chroot; nicht als alleinige Hauptursache behaupten |
| RAID | md0 und md1 jeweils RAID1, [2/2] [UU], keine laufende Synchronisierung angezeigt |
| Verschlüsselung | md1 -> LUKS Version 2 -> dm_crypt-0 -> LVM vg_aurelia |
| LVM | Sieben LVs exakt 120/80/64/384/704/128/32 GiB; Reserve 347.82 GiB |
| Bootdateien | Kernel 5.15.0-191-generic, passendes initrd ca. 109 MB; GRUB-Einträge verweisen darauf |
| Initramfs | cryptroot/crypttab, mdadm.conf, cryptroot/lvm2-Skripte und cryptsetup enthalten; Entsperrbarkeit noch nicht getestet |
| EFI | Primary-ESP enthält EFI/ubuntu und Fallback-Bootdateien. Zwei ubuntu-NVRAM-Einträge passen per PARTUUID zu beiden ESPs. Dateien auf zweiter ESP und Einzeldisk-Boot nicht unabhängig getestet. |
| Bootreihenfolge | PXE 0002 zuerst; Ubuntu-Einträge 0000 und 0004 vorhanden. Vor Neustart Provider-PXE/HDD-Start abstimmen. |
| Benutzer | klaus999 noch nicht im Ziel-passwd, aber korrekt in cloud-init vorbereitet, sudo-Gruppe, /bin/bash, lock_passwd false. Erststart-Erstellung/Login noch offen. |
| cloud-init | /target/etc/cloud/cloud.cfg.d/99-installer.cfg: datasource None, userdata_raw enthält Benutzer; nur unkritische Felder ausgegeben, keine Passwort-Hashes. ssh_pwauth true. |
| Hostname | aureliaserver |
| Wichtige Pakete | openssh-server, cloud-init, cryptsetup-initramfs, mdadm, lvm2, grub-efi-amd64-signed installiert |

chroot efibootmgr meldete keine EFI-Variablen, weil /target/sys nicht gebunden ist. Ausführung /target/usr/bin/efibootmgr in der Live-Umgebung konnte vorhandene EFI-Variablen lesen. Das ist KEIN Beleg eines Firmwaredefekts.

## Simulierte Änderungen (nicht ausgeführt)

- Gezielt apt-get -s install ubuntu-advantage-tools: ein Upgrade (27.13.5~22.04.1 -> 37.2ubuntu~22.04.1), zwei neue Pakete ubuntu-pro-client und ubuntu-pro-client-l10n, null Entfernungen; 100 weitere Upgrades offen.
- Vollständiges simuliertes dist-upgrade auf Basis vorhandener Paketlisten: 101 Upgrades, 10 neue Pakete, null Entfernungen. Kein apt update erfolgt, daher Simulation keine Garantie aktueller Downloadverfügbarkeit.
- linux-generic installiert und Kandidat beide 5.15.0.191.169.

## Urteil und nächster Vorschlag

Vorhandene Installation wirkt gezielt vervollständigbar; keine Evidenz für notwendige Neupartitionierung. Keine Boot-/Produktabnahme erteilen. Empfehlung: zuerst betroffenes Konfigurationsdatei-Problem vergleichen und gezielte Paketvervollständigung unter korrekt vorbereiteter chroot-Umgebung; keine pauschale Überschreibung von Konfigurationsdateien. Danach Paket-/Bootprüfungen wiederholen. Bootversuch nur mit abgestimmter KVM-Erreichbarkeit und LUKS-Passphrase sowie korrigiertem/abgestimmtem Bootweg. Erststart-Benutzererstellung und SSH testen. Vollständige 22.04-Aktualisierung und reguläres Upgrade zu 24.04 sind nachfolgende gesonderte Schritte, noch nicht ausgeführt oder durch reine Diagnosefreigabe autorisiert.

Temporären SSH-Zugang nach Abschluss gezielt entfernen; nicht ohne Zustimmung in Zielsystem übernehmen. Alte Schlüssel unverändert lassen. Automatische Governor-Reviews/Gates unverändert.
