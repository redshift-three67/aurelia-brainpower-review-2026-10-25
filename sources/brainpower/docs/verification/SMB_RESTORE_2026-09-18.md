# Synthetischer SMB-Backup-/Restoretest bestanden

Am 18.09.2026 durch den Betreiber in Root-KVM ausgeführt; Ergebnis anschließend per SSH gelesen und mit Screenshot abgeglichen.

- Bericht: `/var/tmp/aurelia-restore-result-60974435bacc44529915b9c87ee76069.json`
- Status: `synthetic_restore_verified`
- NAS-Repository: `//fra1-nas-backup1.ip-projects.de/213487/hermes-restore-test-60974435bacc44529915b9c87ee76069`
- Snapshot: `f3ad485d1fe6f279e2edcd991267bec86ffe6b30585bcabce50aa6abe8a492a6`
- Vier synthetische Dateien, 1048624 Bytes: Backup, vollständige Repositoryprüfung und Restore erfolgreich. Unabhängiger Datei-/Hash-/Modusvergleich erfolgreich.
- Test-Schreibmount entfernt laut Bericht und frischem CIFS-Mountinventar; einzig verbleibender CIFS-Mount `/mnt/aurelia-g2` mit korrekter Quelle und `ro,nosuid,nodev,noexec,relatime`.
- `aurelia-backup-files.timer` weiterhin `disabled`. Der kombinierte SSH-Lesebefehl endete deshalb mit Status 1 (`systemctl is-enabled`), nicht wegen eines fehlgeschlagenen Restoretests.
- Private Logs, Originale, Restore und Testschlüssel verbleiben unter `/var/lib/aurelia-backup-tests/60974435bacc44529915b9c87ee76069`; NAS-Testrepository erhalten. Keine Geheimnisse lokal kopiert.

Grenzen: kein produktives Serverbackup, kein PostgreSQL-/Vollserver-Restore, keine automatisierte Sicherung, kein Nachweis externer Schlüsselwiederherstellung bei Serververlust. Produktgates bleiben bestehen. Nächster Arbeitsschritt ist die Festlegung des produktiven Sicherungsumfangs, der konsistenten Datenbanksicherung, Aufbewahrung und separaten Schlüsselsicherung vor Aktivierung und kontrollierter Serverintegration.
