# Temporärer Installer-Zugang 2026-09-14

Ergänzt PAUSE_INSTALLER_SSH_2026-09-14.md: Betreiber hat Pause aufgehoben und ursprünglichen Public-Key-Import bestätigt. Live-SSH bestätigt: Server akzeptiert id_ed25519, lokale Signatur scheitert an verschlüsseltem privaten Schlüssel; Windows ssh-agent gestoppt. Keine erfolgreiche Remote-Anmeldung, keine Serverreparatur bislang.

Betreiber wünscht ausdrücklich einen neuen temporären Schlüssel. Separat erstellt, ohne Passphrase; private Datei per Windows-ACL auf aktuellen Benutzer beschränkt. Bestehende Schlüssel unverändert.

- Temporärer privater Schlüssel (NICHT in Backups/Repos kopieren): C:/Users/Hubert111/AppData/Local/Temp/brainpower-installer-ssh-i90fhn1c/id_ed25519
- Öffentlicher Schlüssel: gleichnamige .pub-Datei.
- Kommentar: brainpower-temporary-installer
- Ziel: installer@185.242.115.210, Port 22.
- Verifizierter Hostkey bleibt SHA256:ilK3AmEvgw+uvQ1EYRrAFp0jFl3hkb8hsTts8CFUYcw; separate known_hosts-Datei C:/Users/Hubert111/AppData/Local/Temp/brainpower-installer.known_hosts.
- Neuer Public-Key-Import noch NICHT bestätigt. Nach Bestätigung mit BatchMode und StrictHostKeyChecking=yes anmelden; sudo -n und Zielmount prüfen, dann lesende Paket-/Bootdiagnose.
- Schlüssel nur für Installer-Reparatur, nicht automatisch ins installierte Zielsystem übernehmen. Nach Abschluss eigenen authorized_keys-Eintrag gezielt entfernen und temporären privaten Schlüssel löschen; bestehende Einträge nicht entfernen.
- Reparaturfähigkeit zuerst prüfen; kein Neustart/Upgrade/Neuinstallation allein aus Zugangserlaubnis ableiten. Automatische Modellreviews bleiben aus.
