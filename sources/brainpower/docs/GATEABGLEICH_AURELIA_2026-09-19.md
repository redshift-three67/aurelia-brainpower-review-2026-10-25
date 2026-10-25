# Aurelia Ground-Zero: Nachweisabgleich 19.09.2026

Aktualisierung nach Root-Prüfung: `verification/ROOT_BASELINE_2026-09-19.md` ergänzt die folgende erste Bestandsaufnahme. LUKS2, SSH-Härtung in geprüften Kontexten, aktive Firewall und funktionierender Root-NVML-Zugriff jetzt belegt. Secure Boot bleibt disabled; DMI ECC None; zwei Ubuntu-EFI-Einträge sind kein Dual-NVMe-Boottest. Keine Gatefreigabe.

Lesender Abgleich gegen Aurelia `docs/superpowers/specs/2026-08-25-aurelia-ground-zero-server-design.md` §§9–12 und `docs/superpowers/plans/2026-08-25-aurelia-ground-zero-preflight.md`. Keine externe Gateänderung. Historische Neuinstallationsschritte werden nicht erneut ausgeführt. Dokumentierte Anforderungen sind nicht automatisch aktuelle Implementierungsaufträge.

| Gate | Vorhandener Nachweis | Fehlender Abschluss / Einordnung |
|---|---|---|
| 0 Backup/Restore | Synthetischer NAS-Restore und echtes Konfigurationsarchiv mit Hashvergleich; Schlüssel E:/F: verifiziert | Historisches Gate verlangt zwei vollständige externe Sicherungssätze, Git-Restore und DB-Restore oder begründete Nichtübernahme. Zwei Schlüsselkopien sind keine zwei vollständigen Sicherungssätze. Historische Altbestandsnachweise nicht durch heutige Konfigurationssicherung ersetzt. |
| 1 IPMI/KVM/Virtual Media | Wiederholt erfolgreiche KVM-Eingaben und Login durch Betreiber | Unabhängiger Recoveryboot/Virtual Media und BMC-Netztrennung nicht vollständig belegt; kein Neustart dafür ausgelöst. |
| 2 Hardware/Firmware/UEFI | RAID [UU], frühere Hardwareinventur; aktueller Secure-Boot-Status abgefragt | Secure Boot disabled, Setup Mode. ECC-/Firmware-/USV-Abschluss fehlt. Keine automatische Firmware-/Secure-Boot-Änderung. |
| 3 Installation | Ubuntu 24.04.5 vorhanden; aktuelle lsblk zeigt RAID1 → crypto_LUKS → LVM, Systemdatenpfade und Swap darunter | Historische ISO-/Neuinstallationsprovenienz und abweichende LV-Größen gesondert einordnen. lsblk allein beweist nicht LUKS-Version oder vollständige Recoveryfähigkeit. Keine Neuinstallation. |
| 4 Boot/Recovery | Reboot mit entsperrtem System und grafischem Login bestätigt | Separater LUKS-Recoverykey-/Headernachweis und Boot über beide NVMe/EFI-Pfade offen; keine Ausfallprobe durchgeführt. |
| 5 Identitäten/SSH/VPN/Firewall | VPN/Firewall aktiv; getrenntes aurelia-dev ohne Zusatzgruppen; frühere SSH-Härtung dokumentiert | Aktuelle Konfigurationsdatei erlaubt Port 22 ohne Quell-IP-Beschränkung (explizit früher vom Betreiber gewünscht). Abweichung vom alten VPN-only-Ziel dokumentieren/entscheiden; aktuelle privilegierte Regel-/sshd-/sudo-Prüfung fehlt. Datei ist nicht Beweis des gesamten aktiven nft-Regelwerks. |
| 6 Desktop/Codex | GDM aktiv, graphical.target, korrekte Startlinks, Benutzerbestätigung | Vollständiger Rechte-/Datenzugriffstest unter tatsächlicher Entwicklungsidentität nicht hier erneut ausgeführt. Root-KVM für Administration ist keine Freigabe für Codex als root. |
| 7 NVIDIA | Historische Treibervorbereitung; aktuelles nvidia-smi als klaus999 verweigert | Insufficient Permissions ist kein Treiberdefektbeleg. Autorisierte GPU-Identität muss NVML/Version/Desktopbelegung prüfen. Kein nvcc im SSH-PATH ist kein vollständiger Toolkit-Ausschluss. |
| 8 Security/Logging/Updates | AppArmor, auditd, chrony aktuell aktiv; NTP synchron; keine failed Units; Health Result=success | Statusmeldungen ersetzen keine vollständige Regel-/Update-/Alert-/Soak-Abnahme. |
| 9 PostgreSQL16 | Cluster 16/main vorhanden und down; ältere Tests zeigen Loopback/Checksums | Absichtlich gestoppt. Vor späterer Nutzung frische isolierte Abnahme; kein Start allein für diesen Bericht. |
| 10 Offsite-Betrieb | Einmalige NAS-Sicherung und Rücklesetest bestanden | Automatische Sicherung deaktiviert; RPO/RTO, Aufbewahrung, Monitoring und kompletter Off-Server-Restore offen. Gemäß Betreiber passend zur ersten echten Integration ergänzen. |
| 11 Selektiver Projekt-Restore | Bisher keine Produktübertragung aus diesem Arbeitspaket | Erstmodul, Hashbindung, Altsecret-/Altservice-Ausschluss und konkreter Adapter offen. |
| 12 Gesamtbaseline | Einzelbelege verfügbar | Keine Gesamtfreigabe: vorangehende Nachweislücken, Recovery-/Soaktests und Vertragsentscheidung offen. |

## Konkrete Sicherungslücke geschlossen

Die feste Pfadauswahl des Backups vom 18.09. enthält nicht `/etc/aurelia-firewall.nft`, obwohl die gesicherte Firewall-Unit genau diese Datei lädt. Datei am 19.09. lesend als `aurelia-firewall-20260919.nft` nach E:/F: in Aurelia-Recovery kopiert und verglichen. SHA256: `4576e89f8522673b823623f39135ab2372ce6b38541c3fe99ceff268bc9c98f8`. Serverdatei root:root 0644. Kein Secret, keine Firewalländerung. Diese Ergänzung und das Grafikstart-Tar gehören zum Restic-Basissatz; kein vollständiges Systemabbild behaupten. Das alte Skript nicht ohne korrigierte Pfadauswahl als vollständige neue Konfigurationssicherung wiederverwenden.

## Nächste Schritte

1. Aktuelle nichtdestruktive Baseline-Abnahme von historischer Vorinstallationsabnahme ausdrücklich trennen; alte fehlende Belege nicht rückdatieren.
2. Privilegierte lesende Prüfung bündeln: aktive Firewall/SSH/sudo-Regeln, zulässiger GPU-Zugriff, Verschlüsselungs-/Recoverymetadaten ohne Schlüsselmaterial, Paket-/Bootprovenienz soweit verfügbar. Keine neuen Dienste aktivieren oder Schutzkonfiguration automatisch ändern.
3. Separate Entscheidungen vorbereiten: SSH weiterhin IP-unabhängig mit Schlüssel versus VPN-only; Secure-Boot-/Recovery-Wartungsplan; REST-Integrationsprofil unter unveränderten Schema-/Hash-/CopyGuard-Pflichten.
4. Erst nach relevanten Infrastruktur- und Vertragsfreigaben konkrete Modul-/Adapterauswahl und isolierten Linux-Smoke planen. Keine pauschale Freigabe der fünf Produkte.
