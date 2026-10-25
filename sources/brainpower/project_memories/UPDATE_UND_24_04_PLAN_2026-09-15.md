# Serverupdate und integrierte Vorbereitung, 15.09.2026

## Neuester Stand: Noble-Normalboot erfolgreich

Am 15.09.2026 gegen 09:41 UTC nach Betreiber-Entsperrung über SSH live geprüft: Ubuntu 24.04.5 LTS, uname 6.8.0-139-generic, RAID md0/md1 beide [2/2][UU], geplante Mounts vorhanden, Swap 32 GiB aktiv. Systemzustand running, keine fehlgeschlagenen Units, SSH active, dpkg --audit leer, cloud-init done, NTP synchronisiert, Python 3.12.3. Cloud-init-Warnung betrifft die fehlenden Leserechte des unprivilegierten Abfragebenutzers auf geschützte Konfiguration. Upgrade und Normalboot sind damit verifiziert. Sekundärer Bootpfad/Ausfalltest, Offsite-Restore und die Infrastruktur-/Matrixfolge bleiben offen. Die folgenden Upgrade-Zwischenstände sind historisch.

## Ausgeführt und geprüft

Temporärer SSH-Zugang als klaus999 funktioniert nach Eintrag des bereits freigegebenen öffentlichen Schlüssels in die zuvor leere authorized_keys. Fingerprint fihsk9V7iSVIKM1aURAgghkj/vIvjM4IPm2AEzlU7KM; Rechte .ssh 700 und authorized_keys 600. Passwort-SSH-Ursache bleibt ungeklärt. Root-Konsole vom Betreiber über sudo -i in Chrome-KVM geöffnet; keine NOPASSWD-Regel eingerichtet.

Verwaiste file:///cdrom-Quelle deaktiviert, Original unter /root/brainpower-preupdate-FC9TvaT4 gesichert. apt-get update und Simulation erfolgreich.

Betreiber hat Updates und zuvor vorgeschlagene Bootreihenfolge-Korrektur freigegeben. 98 Pakete aktualisiert, 6 neu installiert, keine entfernt. Nun Ubuntu 22.04.5. dpkg --audit ohne Befund, apt-get check und grub-script-check erfolgreich; UPDATE_OK im /home/klaus999/bpupdate.log. Keine fehlgeschlagenen Units, RAID md0/md1 jeweils [UU]. BootOrder jetzt 0000,0004,0002,0003,0001 (Ubuntu primär, Ubuntu sekundär, PXE, PXE, Shell). Noch kein Neustart und kein Releaseupgrade ausgeführt.

Sicherung ausgewählter Konfiguration und Paketliste: /root/brainpower-update-VL8ipHOv. Kein Vollbackup oder Snapshot. Update behielt vorhandene Konfigurationen bei Rückfragen; NEEDRESTART_MODE=l. /run/reboot-required lieferte keinen Inhalt; Wiederanlauf nach Updates dennoch nicht geprüft.

Sechs Pakete bleiben zurück: libgssapi-krb5-2, libk5crypto3, libkrb5-3, libkrb5support0, libnetplan0, netplan.io. Keine manuellen Holds. apt-cache policy zeigt bei Kerberos und Netplan Kandidaten phased 10%; vor Releaseupgrade gesondert behandeln, nicht als Paketdefekt ausgeben.

## Quellengebundener Integrationsplan (vorbereitet, nicht umgesetzt)

NEUESTER STAND: Upgrade installiert, Neustart in Noble ausgelöst. /etc/os-release 24.04.5; 6.8.0-139 initramfs mit cryptroot/crypttab, cryptsetup, lvm, mdadm geprüft. Paketcheck, sshd -t, GRUB-Syntax und Netplan bestanden. Netplan-Warnung durch chmod 600 behoben. fwupd-refresh nach Neustart des fwupd-Dienstes erneut erfolgreich, keine Firmware installiert. Upgrade hatte Boot0004 entfernt; zweite ESP nach Sicherung unter /root/brainpower-efi-* von /boot/efi/EFI synchronisiert, diff identisch; Boot0004 Ubuntu-secondary neu erstellt. Bootreihenfolge im Neustartskript wieder 0000,0004,0002,0003,0001. bpnoblereboot führt Prüfungen und systemctl reboot aus. Nachstartprüfung und LUKS-Eingabe noch offen.

Vorupgrade-Archiv: /root/brainpower-prerelease-pdmKjwjb/config-boot-dpkg.tgz, SHA256 8cb305b6e08a18ce3c1e579f47f3fc5ebfefa281be9f7165ade48f42ab8db657. Archiv enthält vertrauliche Systemkonfiguration, verbleibt rootgeschützt auf Server; nicht in Repository kopieren. Keine vollständige Rücksicherung getestet. Protokolle /home/klaus999/bpphase.log, bpverify.log, bpbootfix.log, bpnoblereboot.log. Einige APT-Quellen/neu angelegte EFI-Variable sind wegen root-umask 077 für klaus999 nicht lesbar; root-Prüfungen verwenden, nicht falsche fehlende Quellen daraus ableiten. Historische laufende Upgrade-Angaben unten sind überholt.

AKTUELL: Releaseupgrade am 15.09.2026 gestartet, Paketumstellung läuft; keinesfalls parallel apt/dpkg starten oder rebooten. Sechs Restupdates vorher erfolgreich (PHASE_OK), danach null ausstehende Pakete. Root-KVM führt /home/klaus999/bprelease aus: Sicherung von /etc, /boot, dpkg-Datenbank unter /root/brainpower-prerelease-*/config-boot-dpkg.tgz mit SHA256, dann do-release-upgrade -f DistUpgradeViewText. Sicherung bleibt auf Server, ist kein Vollbackup/Offsite-Restore.

Mirror-Rückfrage nach Nachweis bestätigt: Noble-Basisliste signiert (Release-Datum 2024), noble-updates/security vom 15.09.2026 und backports vom 14.09.2026, jeweils gpgv Good signature Ubuntu Archive 2018. Automatische Freigabeprüfung hatte zunächst mangelnde Frischebelege beanstandet; nach zusätzlichen Prüfungen Bestätigung zugelassen. Umfang 537 Updates, 185 neue Pakete, 48 alte Bibliotheks-/Hilfspakete entfernt, ca. 1164 MB Download. Details vor Bestätigung gelesen. Erste Konsole-Zeichensatzfrage mit Guess optimal character set bestätigt. Upgradeabschluss noch offen.

Neustart-Nachprüfung: Betreiber hat LUKS entsperrt. SSH-Schlüsselzugang funktioniert nach Boot, Kernel 5.15.0-191, RAID md0/md1 [UU], alle vorgesehenen Mounts vorhanden, keine fehlgeschlagenen Units, dpkg --audit ohne Befund. BootCurrent 0000 und Ubuntu zuerst bleiben erhalten. Das ist ein erfolgreicher Normalboot, kein Test des sekundären Laufwerks oder Ausfalls.

do-release-upgrade -c bietet konkret 24.04.5 LTS an. Simulation mit APT::Get::Always-Include-Phased-Updates=true: 6 Updates, 2 neue Pakete, keine Löschungen, keine verbleibenden Updates. Noch nicht ausgeführt. Root-KVM-Sitzung nach Neustart beendet; erneute lokale Anmeldung/sudo durch Betreiber erforderlich. Kein Passwort oder breiter passwortloser sudo-Zugang angefordert. Releaseupgrade noch nicht gestartet.

Fortsetzung: Betreiber hat die Umsetzung des vorgeschlagenen weiteren Ablaufs freigegeben. Kontrollierter Neustart am 15.09.2026 gegen 08:58 UTC über verifizierte Root-KVM mit systemctl reboot ausgelöst. Vorher keine aktiven apt/dpkg-Arbeiten sichtbar (nur wartender unattended-upgrade-shutdown-Helfer), RAID vollständig und Ubuntu-Bootreihenfolge bestätigt. Bootabschluss und mögliche manuelle LUKS-Entsperrung noch abzuwarten. Kein 24.04-Upgrade bislang gestartet.

Quellen: artifacts/QUELLEN_GATE_TESTPLAN_2026-09-13.md; project_memories/SERVER_KLARSTELLUNG_2026-09-13.md; Aurelia/docs/superpowers/specs/2026-08-25-aurelia-ground-zero-server-design.md; docs/RESTARBEITEN_0_5.md.

1. Aktuellen 22.04-Zustand und Konfigurationssicherungen dokumentieren; kontrollierter Neustart mit KVM/LUKS, beide EFI-/Recoverypfade gesondert testen. Vor Releaseupgrade verbleibende Updates prüfen.
2. Unterstützten 22.04 -> 24.04-Upgradeweg separat freigeben und durchführen. Abweichung vom ursprünglich geforderten offiziellen 24.04-ISO-Neuaufbau ausdrücklich dokumentieren. Ein Upgrade beweist keine geprüfte ISO-Provenienz. Aktuelles Pointrelease und Treiberversionen bei Ausführung überprüfen.
3. Gemeinsame Infrastruktur auf 24.04: getrennte Administration/Entwicklung/Dienstidentitäten und Dateirechte; vorhandenen klaus999-Admin zur vorgesehenen Rollenstruktur zuordnen. Management-VPN/nftables und anschließend SSH-Härtung ohne Aussperren. Logging/AppArmor/Audit/Zeit, RAID/NVMe-/Dienstüberwachung und begrenzte Sicherheitsupdates ohne automatische Reboots.
4. Externen 1-TB-G2-Backupspeicher anbinden, verschlüsselte Sicherung und isolierten Restore mit Nachweisen einrichten. Zugang und tatsächliche Funktion noch offen.
5. Produktübergreifende Testbasis: isolierte Python-Umgebungen (RadiWorks >=3.12), separate Buildpfade/Ressourcenbudgets; PostgreSQL 16 intern mit getrennten Rollen/Checksums und synthetischen Testdaten. Aurelia Build und Migration trennen; Devserver nicht ungeprüft öffentlich binden. Projektstände und Testergebnisse an Hashes binden.
6. Spätere freigegebene Stufen: minimales GNOME/Entwicklungswerkzeuge ohne Produktivdatenzugriff; paketverwaltete NVIDIA-Basis mit Reboottest. Kein CUDA-Toolkit, Hardwareaktivierung oder produktive Klientendaten. Datenbankerweiterungen erst nach Versions-/Migrationsprüfung.

Keine automatischen Matrix-/Gatebestätigungen, keine Projektdateien in den fünf externen Repositories geändert und keine Produktdienste installiert. Automatische Modellreviews bleiben unverändert aus. ABI-/Schemaentscheidungen und Produktabnahmen bleiben eigene Arbeitspakete.
