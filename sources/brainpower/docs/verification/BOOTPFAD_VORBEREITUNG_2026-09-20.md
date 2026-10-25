# Einmaliger sekundärer EFI-Boot – vorbereitet

Betreiber genehmigt20.09.2026 erforderlichen Neustart. Root-SSH weiterhin nicht ohne Passwort; Durchführung durch kurzen Root-KVM-Aufruf, dabei Bediener für LUKS-Entsperrung anwesend. Noch kein Neustart ausgeführt und keine Bootvariable geändert.

## Frisch geprüfte Ausgangslage, 17:30:51 UTC

- Boot-ID: 2d811cdf-f770-4fa0-bb3c-f6ec54666fed; gestartet18.09.2026 14:57:57 Serverzeit.
- BootCurrent0000 Ubuntu, EFI-UUID e9372cc5-356a-44d5-b72a-c75a441e4bb5 auf /dev/nvme1n1p1, Loader EFI/ubuntu/shimx64.efi.
- Boot0004 Ubuntu-secondary, EFI-UUID20b45555-f9c3-4df1-ae39-e4e02a8fae2d auf /dev/nvme0n1p1, gleicher Loaderpfad.
- BootOrder0000,0004,0002,0003,0001. Kein BootNext vorhanden.
- RAID md0/md1 jeweilsdegraded0; SSH/WireGuard/GDM/Firewallactive. Healthtimeractive. Kein /run/reboot-required vorhanden. Neustart dient gezielt dem fehlenden zweiten EFI-Bootnachweis, nicht einer allgemeinen Reparatur.
- Historischer EFI-Dateivergleich: acht Dateien paarweise identisch, dokumentiert in EFI_RECOVERY_2026-09-19.md. Externe LUKS-Header-/Schlüsselkopien zuvor bestätigt; kein vollständiger Recoverytest daraus.

## Konkrete Durchführung

Im geöffneten Root-KVM-Terminal, nur wenn der Bediener die LUKS-Entsperrung jetzt begleiten kann:

```bash
efibootmgr -n 0004 && systemctl reboot
```

`-n` setzt BootNext ausschließlich für einen Start; BootOrder bleibt unverändert. Referenz: https://manpages.ubuntu.com/manpages/noble/man8/efibootmgr.8.html . Kein RAID-Mitglied wird entfernt/deaktiviert, keine Partition beschrieben, Secure Boot bleibt unverändert. Bei einem Fehler der ersten Anweisung erfolgt durch && kein Neustart. Bei späterem Rebootfehler den gesetzten BootNext-Zustand prüfen, nicht blind wiederholen.

Bediener entsperrt LUKS in der KVM und meldet, wenn der Login wieder sichtbar ist. Falls der sekundäre Boot scheitert, sichtbare KVM-Meldung auswerten; vorhandenen primären Ubuntu-Eintrag gezielt verwenden, keine Schleife und keine automatische Neuinstallation.

## Nachprüfung nach Rückkehr

Neue Boot-ID und BootCurrent0004 müssen belegt sein. Ein erreichbarer Server allein reicht nicht: automatischer Firmwarefallback zu0000 gilt nicht als bestandener Sekundärtest. Außerdem BootOrder unverändert, BootNext verbraucht, RAIDbeideUU/degraded0, alle erwarteten verschlüsselten Mounts, SSH/VPN/GDM/Firewall/Health und NVIDIA-Basis prüfen. Beobachtete Abweichungen einzeln auswerten. Keine weiteren Reboots ohne konkreten Bedarf.

Grenze: erfolgreicher Start über beide EFI-Einträge bei vorhandenen beiden Laufwerken ist kein physischer Einzellaufwerks-Ausfalltest, kein unabhängiger Virtual-Media-Recoveryboot und kein Restore der LUKS-Header.

## Installationsprovenienz – neuer Befund

`/var/log/installer/media-info` enthält Ubuntu-Server22.04.2LTS JammyJellyfish Releaseamd64(20230217.1). Heutiger Systemstand24.04.5 ist getrennt belegt. Die Datei liefert keinen Nachweis einer frischen24.04-ISO-Installation; genauer Upgrade-/Installationsverlauf bleibt zu rekonstruieren. Fehlende Dateien an den geprüften Pfaden lsb-release/subiquity-server-debug.log beweisen keine globale Abwesenheit anderer Installationsbelege. Keine Neuinstallation aus dieser Lücke ableiten.
