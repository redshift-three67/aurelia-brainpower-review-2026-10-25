# Erster Bootversuch 14.09.2026

## Betreiberbestätigung nach Neustart

Der Betreiber meldet: „wir sind drin und auch eingeloggt unter dem Benutzer klaus999“. Erfolgreicher Start und Benutzeranmeldung sind damit als Betreiberbeobachtung bestätigt; die frühere Aussage „noch nicht bestätigt“ unten ist historisch. Technische Nachprüfung des gestarteten Systems (Kernel/Version, RAID, Mounts, cloud-init, Netzwerk, Dienste) und SSH-Zugang mit neuem Ziel-Hostkey stehen noch aus. Keine vollständige Produktabnahme und kein 24.04-Upgrade daraus ableiten.

Betreiber hat kontrollierten ersten Boot nach erfolgreicher gezielter Paketvervollständigung ausdrücklich mit „Ja“ freigegeben. Verifizierte Installer-SSH-Verbindung genutzt; Zielmount und dpkg-Audit erneut geprüft, keine dpkg-Locks belegt. Boot0000 passt per PARTUUID e9372cc5-356a-44d5-b72a-c75a441e4bb5 zur primären ESP nvme1n1p1 mit Ubuntu-shim.

`/target/usr/bin/efibootmgr -n 0000` ausgeführt und BootNext: 0000 zurückgelesen. Dauerhafte BootOrder bleibt 0002,0000,0004,0003,0001 (PXE zuerst). Anschließend sync und systemctl reboot in Live-Installer-Rootshell ausgelöst. Boot-Erfolg und tatsächliche Passphrase-Entsperrung noch NICHT bestätigt. Betreiber wurde gebeten, KVM zu beobachten und LUKS-Passphrase selbst einzugeben.

Nächster Schritt: KVM-Bild auswerten, ersten Zielsystemstart und cloud-init-Benutzer klaus999 sowie RAID/Mounts/Netz prüfen. Temporärer Installer-Schlüssel wurde nicht ins Zielsystem übernommen. Ziel-SSH-Hostkey nach Systemwechsel erneut unabhängig verifizieren. Bei erneutem PXE-/Installationsbild keinen Installerlauf starten. Keine permanente Bootumstellung und kein Ubuntu-24.04-Upgrade erfolgt. Reparaturnachweis siehe REPARATUR_ERFOLGT_2026-09-14.md.
