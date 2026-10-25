> **Standkorrektur23.09.2026:** Aktueller konsolidierter Stand in [Serverabnahme](SERVER_ABNAHME_AKTUELL_2026-09-23.md). Backup und Aufbewahrungsautomatik inzwischen aktiv und manuell abgenommen. Ältere Angaben „Timer/Löschung aus“ sind historisch. Rescue, zweite Datenkopie und externe Ausfallüberwachung ausdrücklich zurückgestellt; weitere G0-Punkte bleiben separat offen.

# G0 – aktueller Abgleich und konkrete Restpunkte

21.09. 20:54 UTC: Logischer PostgreSQL-Restore auf separater Kopie erfolgreich: 1 Nichttemplate-Datenbank, 15 Rollen und Globals geprüft, Runtimeisolation bestätigt, beide Testcluster beendet. Original unverändert und weiterhin gestoppt. [Nachweis](verification/POSTGRES_LOGICAL_RESTORE_2026-09-21.md). Dieser DB-Restore-Restpunkt ist abgeschlossen; ältere Aussagen zum fehlenden logischen Restore sind überholt. Unabhängiger Server-Recoveryweg, Providerfragen, vollständige Backup-Betriebsregeln und abschließende G0-Konsolidierung bleiben offen.

21.09.: physische PostgreSQL16-Sicherung auf SMB mit vollständiger Repositoryprüfung, getrenntem Archiv-/Clusterrestore, Inhalts-/Metadatenvergleich und Offline-Prüfsummenprüfung bestätigt. Quelle unverändert/Originaldienst weiterdown. [Nachweis](verification/POSTGRES_SMB_RESTORE_2026-09-21.md). Logischer DB-Restore/Betriebsprüfung und vollständige Recovery bleiben offen; ältere pauschale Aussagen fehlender DB-Sicherung sind für diesen physischen Teil überholt.

21.09.09:37UTC: PostgreSQL-Offline-Prüfsummenprüfung bestanden:948Dateien/2820Blöcke,0Fehler. Cluster bleibtgestoppt. [Nachweis](verification/POSTGRES_OFFLINE_2026-09-21.md). DB-Sicherung/Restore und logische Bestandsprüfung bleiben getrennte offene Schritte.

Aktualisierung21.09.00:39CEST: aktuelle SMB-Konfigurationssicherung samt vollständiger Repositoryprüfung und getrenntem Archivrestore bestätigt (38Pfade). Bericht lokal/serverhashgleich, eigene Mount-Rücknahme unabhängig bestätigt; keinefailedUnits, Backuptimerweiterdisabled. [Ergebnis](verification/SMB_CONFIG_REFRESH_2026-09-21.md). Kein vollständiger Server-/DB-/Produktrestore; Gesamt-G0 bleibt offen.

Neuer Backup-Teilnachweis: Hermes-Snapshot19.09. vollständig gegen3147Manifestdateien geprüft und isoliert wiederhergestellt; SQLiteintegrityok, keine Anwendung gestartet. Kein Server-/PostgreSQL-/vollständiger Git-Restore. Umfang und nächste Abhängigkeiten: [Backup/Recovery-Abgleich](G0_BACKUP_RECOVERY_ABGLEICH_2026-09-20.md). Betreiber klärt Rescue-/VirtualMedia-Verfügbarkeit; [Provider-Anfrageentwurf](G0_PROVIDER_ANFRAGE_2026-09-20.md) vorbereitet, nicht gesendet.

Aktualisierung18:08:53UTC: Root-Sammelbericht ausgewertet und gehasht gesichert. dpkg-Audit und APT-Abhängigkeitssimulation ohne Fehler/Warnungen; PostgreSQL16 sauber heruntergefahren, Seitenprüfsummen Version1 aktiviert. Kein vollständiger DB-/Restore-/Upgrade-Abschlussnachweis. Backup-Timer aurelia-backup-files.timer weiterhin disabled. Einzelheiten und Grenzen im Bericht [Betrieb/Provenienz](verification/G0_BETRIEB_PROVENIENZ_2026-09-20.md).

Aktualisierung 17:54 UTC: Drei fehlerfreie Health-Läufe seit dem Neustart; tatsächliche WireGuard-Unit wg-quick@wg-admin aktiv. Upgrade-Transaktionen vom 15.09. mit aktuell bestätigten Zielversionen der Basispakete gefunden. Teilnachweise und Grenzen: [Betrieb/Provenienz](verification/G0_BETRIEB_PROVENIENZ_2026-09-20.md). Vollständiger Upgrade-Abschluss, Restore und Langzeitabnahme bleiben offen.

Aktualisierung17:26:42UTC: Health-Korrektur durch Betreiber installiert, installierter SHA256 entspricht018cc0a45acb0ac7c9f54040e3d869874f0656426d0d536dd96479479d5fb219. Vollständiger Bericht healthy=true/errors[]/failed_units[], RAID md0clean/md1active jeweilsdegraded0, NVMepassed ohnecritical_warning/media_errors, NTPsynchron. UnitResultsuccess/Exit0, keine failedUnits; SSH/WireGuard/GDM/Firewall active. Lokaler Beleg artifacts/health-fixed20-report.json maschinell validiert, SHA2561d8574284e4ed5ded28d2add1c93e013a354ca4cd0434ba2c081ee6cd3e77778. Originalbackup-Pfad vom Installer bestätigt, geschütztes Backup in dieser SSH-Prüfung nicht nochmals gelesen. Kein write-pending im aktuellen erfolgreichen Lauf; Übergangs-/Negativverhalten durch sieben lokale Tests belegt, kein künstlicher RAID-Zustandswechsel ausgelöst. Monitoringkorrektur abgeschlossen, kein Soak-/Gesamt-G0-Nachweis.

20.09.2026. G0-Gesamtfreigabe bleibt offen. T3-Prüfungen sind abgeschlossen, aber kein Ersatz für die vollständigen Kriterien aus Aurelia Ground-Zero-Design §§9–12. Keine Neuinstallation, Firmwareänderung oder Bootprobe aus diesem Dokument.

## Frischer lesender Servercheck

17:20:01 UTC: md0/md1 beide RAID1 [2/2][UU]; SSH/WireGuard/GDM/Firewall/AppArmor/auditd/chrony active; NTP synchron. Kein CIFS-Mount, Backuptimer disabled, PostgreSQL16/main down wie vorgesehen. Diese Beobachtung ist keine erneute Firewall-/SSH-Konfigurationsabnahme.

Health-Unit zunächst failed/Exit1. Journal: 17:08:48 und17:14:59 UTC md1 degraded0/state write-pending, Fehler RAID unhealthy; anschließend17:20:24 UTC beide Arrays clean/degraded0, Health healthy=true/Exit0. NVMe-SMART in diesen Berichten passed, keine Medienfehler/critical_warning. Die Einzelmessung von write-pending wird vom bestehenden Skript sofort negativ bewertet. Weder Hardwaredefekt noch Harmlosigkeit eines anhaltenden write-pending sind dadurch belegt.

## Reihenfolge

| Priorität | Bereich | Nachweis / Restarbeit |
|---|---|---|
| Erledigt | Zuverlässige Health-Bewertung | Begrenzte Nachmessung installiert und erfolgreicher Healthlauf geprüft; Details oben. Kein Fehlerzustand wird pauschal erlaubt. |
| Teilnachweis erledigt | NVIDIA nach Neustart | Root-NVML per KVM-Screenshot erfolgreich: RTX4000SFFAda, Treiber580.173.02 passend zum geladenen Kernelmodul, 0MiB/display_activeDisabled. Kein CUDA-/GPU-Lastnachweis. Siehe verification/BOOTPFAD_ERGEBNIS_2026-09-20.md. |
| Danach, nichtunterbrechend | Iststand statt historischer Neuinstallation | Vorhandene Ubuntu-/LUKS-/RAID-/Benutzer-/Treibernachweise konsolidieren; Installationsprovenienz und Abweichungen ausdrücklich offenlassen, keine Rückdatierung. |
| Eigene Betriebsentscheidung | SSH/IPMI | IP-unabhängiges Schlüssel-SSH ist bereits ausdrücklich genehmigt, nicht erneut erfragen oder eigenmächtig ändern. Abweichung zum historischen VPN-only-Text kanonisch einordnen. BMC-Netztrennung/Providerzugriff noch belegen. |
| Bootpfade belegt; weitere Recovery offen | Boot/Recovery | Primärer Boot0000 und genehmigter sekundärer Boot0004 mit neuerBoot-ID bestätigt; BOOTPFAD_ERGEBNIS_2026-09-20.md. Beide NVMe vorhanden, kein physischer Ausfalltest. Unabhängiger Recoveryboot und tatsächliche Recoveryprüfung fehlen. Kein Entfernen von RAID-Mitgliedern. |
| Provider-/Hardwarebeleg | Secure Boot, ECC, USV | Secure Boot disabled, aktives ECC nicht belegt; USV-/Shutdownnachweis offen. Secure Boot erst mit vorbereitetem Recoverypfad; Non-ECC braucht explizite Behandlung vor realen sensiblen Daten. |
| Vor Gesamt-G0 gemäß geltendem Plan | Vollständiger Restore, Soak, Treiber-/DB-Abnahme | Konfigurations-/synthetischer Restore ist kein vollständiger Repository-/DB-/Serverrestore. Relevanten Sicherungsumfang, zwei externe Sicherungssätze und DB-Nichtanwendbarkeit gegebenenfalls ausdrücklich begründen. Soak sowie Treiber-/DB-Kriterien separat zuordnen. |
| Zur konkreten Integration | Produktbackup/CA/Module | Datenkonsistenz, RPO/RTO, Retention/Alarmierung, reale Dienstidentitäten und modulbezogene Limits festlegen. Historische G0-Anforderungen dürfen nicht allein durch Zurückstellung als erfüllt gelten. |

Die geltende Aurelia-Verfassung verlangt G0-Abnahme vor AUDIT-02 und Produktarbeit. Nur eine ausdrücklich beschlossene, dokumentierte Revision könnte den Umfang ändern; kein implizites Überspringen offener Gates. Vertragskandidaten bleiben lokale Vorschläge.

## Historisch: Health-Korrektur vorbereitet (inzwischen installiert, siehe oben)

Linux beschreibt write-pending als Zustand mit wartenden Schreibvorgängen: https://kernel.org/doc/html/v6.7/admin-guide/md.html . Deshalb nicht in die Liste gesunder Endzustände aufnehmen. Neuer Beobachter liest höchstens1s/12Versuche erneut und verlangt am Ende degraded0 plus clean/active/active-idle. Degradierung, andere unbekannte/schlechte Zustände, Lesefehler und anhaltender Übergang bleiben Fehler. Erfolgreiche Nachmessungen behalten alle Samples im Bericht. Keine Schreiboperation auf RAID/sysfs.

Sieben gezielte lokale Tests bestanden; zuerst fehlender Beobachter nachgewiesen, dann Implementierung geprüft. Gehashte Serverquelle lokal gesichert, exakt zwei Bewertungszeilen durch Funktionsaufruf ersetzt, Beobachter eingebettet. Alle übrigen Healthprüfungen unverändert. Payload und Installer syntaxgeprüft; keine produktive Installation bisher.

- Original SHA256 bce4c46fbacb8d4240d939cd89554ba8183fa6e66b52e7cadba680934b0e08ac.
- Neue Healthdatei SHA256 018cc0a45acb0ac7c9f54040e3d869874f0656426d0d536dd96479479d5fb219.
- Installer SHA256 40a7b29dac038d45f19df3ad46a94ce34c98e886d3f8feec5b3aa6c86bbe233e.
- Beide Uploads auf Server geprüft; Zielpfade vorher abwesend.

Nächste Root-KVM-Aktion: `python3 /home/klaus999/bphealth20`. Installer prüft Original-/Payloadhash, sichert Original exklusiv unter /var/backups/aurelia-health-before-fix20.py, ersetzt atomar unter Beibehaltung von Eigentümer/Modus und startet einmal die bestehende Health-Prüfung. Kein reboot/RAID-/Firewall-Eingriff. Wiederholung/Drift sperrt. Anschließend tatsächlichen Bericht und Hash prüfen; Installationsmeldung allein ist keine Gesamt-G0-Freigabe. SSH sudo-n verlangt Passwort, daher kurzer Root-KVM-Schritt nötig.
