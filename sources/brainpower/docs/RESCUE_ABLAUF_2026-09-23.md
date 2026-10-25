> **Standkorrektur23.09.2026:** Aktueller konsolidierter Stand in [Serverabnahme](SERVER_ABNAHME_AKTUELL_2026-09-23.md). Backup und Aufbewahrungsautomatik inzwischen aktiv und manuell abgenommen. Ältere Angaben „Timer/Löschung aus“ sind historisch. Rescue, zweite Datenkopie und externe Ausfallüberwachung ausdrücklich zurückgestellt; weitere G0-Punkte bleiben separat offen.

# Rescue-Abnahme – Vorbereitung

**Betreiberentscheidung23.09.2026:** Rescue-Erprobung aktuell zurückgestellt und für den jetzigen Serverabschluss optional. Betreiber beschafft die Anleitung und meldet sich an passender Stelle. Keine weitere Nachfrage oder Durchführung bis dahin. Diese ausdrückliche Scope-Änderung geht älteren Rescue-Gate-Formulierungen vor; sie ist kein technischer Recovery-/RTO-Nachweis und keine pauschale Aufhebung anderer Restpunkte.

Stand23.09.2026: Betreiber bestätigt „Rescue-System verfügbar“. Noch kein technischer Rescue-Zugang, Boot oder Restore verifiziert. Start-/Zugangs-/Rückkehranleitung beim Betreiber angefragt. Reasoning: Medium.

## Geplanter gebündelter Ablauf

1. **Start und Rückkehr klären:** Provideranleitung für Aktivierung, Startart (einmalig/dauerhaft), KVM/SSH-Zugang und Rückkehr zu NVMe prüfen. Zugangsdaten nur über vorgesehenen sicheren Weg, niemals Chat. SSH-Identität im Rescue kann abweichen; getrennt verifizieren, vorhandene Hostprüfung nicht deaktivieren.
2. **Vorbereitung vor Unterbrechung:** frischen erfolgreichen Backup-/Restorestand und Healthzustand prüfen; externe LUKS-/Backup-Schlüsselverfügbarkeit und Wiederaufbauanleitung außerhalb des Servers bestätigen. Vorhandene gültige Nachweise wiederverwenden. Konkretes Wartungsfenster, erwartete Unterbrechung und Rückkehrschritte dokumentieren. Laufende Backupjobs ausschließen, Timerzustand vorübergehender Änderungen festhalten.
3. **Rescue-Abnahme:** nach geklärtem Providerverfahren starten. Zunächst Hardware-/Datenträger-/Netzwerkzustand und vorhandene Mounts lesen. Keine Neuinstallation, Formatierung, RAID-Reparatur oder Header-Rücksicherung. Kein automatisches schreibendes Einbinden der Originaldaten voraussetzen; Providerverhalten zuerst klären.
4. **Unabhängiger Backupzugang:** SMB-Erreichbarkeit, nötige Werkzeuge und Zugriff mit extern bereitgestelltem Repositoryschlüssel prüfen. Zugang nicht ausschließlich aus der installierten Serverplatte beziehen. Eine Restoreprobe nur in eindeutig getrennten temporären Speicher oder ein geeignetes unabhängiges Ziel schreiben; Zielkapazität und Pfad vorher prüfen. Vorhandene NVMe-Originale sind kein Restoreziel.
5. **Rückkehr und Abnahme:** Rescue deaktivieren bzw. Einmalboot beenden, regulär von NVMe starten, Health/RAID/Netzwerk/SSH und Backup-/Watchdog-Timer prüfen. Unterbrechungszeit messen, temporäre Zugangsdaten/Dateien nach vereinbartem Verfahren entfernen. Keine dauerhaft gelockerten Zugriffsregeln.

## Grenzen und weitere Abhängigkeiten

Erfolgreicher Rescue-Boot plus Archivzugriff ist ein unabhängiger Zugangs-/Rückkehrnachweis, noch kein vollständiger Maschinenwiederaufbau innerhalb12h. Für den Vollrestore muss ein geeignetes getrenntes Ziel feststehen. Bestehende Sicherungen enthalten definierte Daten-/Konfigurationsarchive, kein automatisch bootfähiges vollständiges Systemabbild.

Ground-Zero-Vorgabe gemäß `G0_BACKUP_RECOVERY_ABGLEICH_2026-09-20.md`: zwei verifizierte externe Kopien vor Löschungen. Aktuelle Nachweise dafür noch abgleichen; automatische Aufbewahrungsbereinigung bleibt aus. Providerangaben zu BMC-Trennung, ECC und Stromausfall-/USV-Verhalten bleiben separat offen. Verfügbarkeit eines Rescue-Systems erfüllt diese Punkte nicht automatisch.
