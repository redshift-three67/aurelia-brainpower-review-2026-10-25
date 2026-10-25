# EFI-Dateivergleich und Recovery-Nachweise

Betreiber führte bpefi19 in Root-KVM aus. Bericht `/var/tmp/aurelia-efi-compare-oefrm6u7/result.json` anschließend per SSH vollständig geprüft.

- Alle acht EFI-Dateien auf beiden Partitionen sind paarweise SHA256-identisch. Keine fehlenden, zusätzlichen oder abweichenden Dateien.
- shimx64.efi, grubx64.efi, grub.cfg und Fallback BOOTX64.EFI auf beiden vorhanden.
- Sekundäre ESP wurde ausschließlich lesend geprüft. Temporärer Mount entfernt laut Bericht und frischem findmnt-Inventar; nur /boot/efi auf /dev/nvme1n1p1 verbleibt.
- Keine Dateiänderung, keine Bootreihenfolgeänderung, kein Neustart.
- Vorherige Recovery-Inventur ordnete jeder ESP einen eigenen Ubuntu-Firmwareeintrag zu.
- LUKS2-Header zuvor auf E:/F: gesichert und hashgeprüft, externe Passphrase durch Betreiber bestätigt.

Grenze: Dateigleichheit und Firmwarezuordnung beweisen keine erfolgreiche Bootprobe über beide Pfade und keinen Betrieb bei physischem NVMe-Ausfall. Kein Header-Restore-/Entsperrtest aus diesen Prüfungen ableiten. Ein späterer Bootpfadtest braucht ein abgestimmtes Wartungsfenster und KVM/Entsperrbereitschaft; Laufwerke nicht dafür spontan aus RAID entfernen. Bloße Bootauswahl ist ebenfalls kein physischer Ausfalltest.

Die nichtunterbrechenden EFI-Prüfungen sind damit abgeschlossen. Weitere Wiederholungen ohne neue Änderungen sind nicht nötig. Produktgates und Secure-Boot-Abnahme bleiben getrennt.
