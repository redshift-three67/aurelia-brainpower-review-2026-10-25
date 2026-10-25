# Ground-Zero-Gatestatus

Stand: 2026-08-25, Europe/Berlin

```yaml
active_program: G0-SRV-GROUND-ZERO
destructive_actions_allowed: false
current_gate: G0-SRV-0
current_gate_status: awaiting-backup-and-restore-evidence
server_changes_started: false
target_iso: ubuntu-24.04.4-live-server-amd64.iso
target_iso_sha256: e907d92eeec9df64163a7e454cbc8d7755e8ddc7ed42f99dbc80c40f1a138433
data_class: synthetic
audit_02: paused
```

## Voraussetzungen

| Voraussetzung | Betreiberangabe | Technische Abnahme |
|---|---|---|
| IPMI/BMC-Webzugang | bestätigt | ausstehend |
| Remote-KVM | bestätigt | ausstehend |
| Virtual Media | bestätigt | ausstehend |
| Anbieter-USV | bestätigt | Kapazitäts-/Shutdownnachweis ausstehend |
| separates Backupsystem | bestätigt | Backup-/Restore-Nachweis ausstehend |
| Anbieter-DDoS-Schutz | bestätigt | Leistungsumfang ausstehend; Hostfirewall bleibt Pflicht |

## Gateübersicht

| Gate | Status | Freigabewirkung |
|---|---|---|
| `G0-SRV-0` Backup/Restore | **wartet auf Nachweis** | erst danach darf der destruktive Installationsplan finalisiert werden |
| `G0-SRV-1` IPMI/KVM/Virtual Media | Betreiberzugang bestätigt, Funktionstest ausstehend | erlaubt Recovery-/Installationsbetrieb ohne Host-OS |
| `G0-SRV-2` Hardware/Firmware/UEFI | read-only Teilinventur vorhanden, Abschluss ausstehend | fixiert Geräte-IDs und Firmwarebasis |
| `G0-SRV-3` Installation | gesperrt | darf NVMe erst nach G0-SRV-0…2 verändern |
| `G0-SRV-4…12` | gesperrt | werden sequenziell nach Installation bearbeitet |

## Bereits belegte Tatsachen

- Ziel-ISO und offizieller SHA-256-Wert sind festgelegt.
- Zwei WD_BLACK SN850X mit jeweils 2 TB wurden read-only identifiziert.
- RAID1 war zum Zeitpunkt der V3-Inventur gesund.
- CPU, Board und RAM-Kapazität wurden bestätigt; aktiver ECC-Schutz ist noch
  nicht bewiesen.
- Secure Boot war deaktiviert und die Plattform im Setup Mode.
- Die acht Root-Passwortanmeldungen vom 19. und 21. August waren laut Betreiber
  eigene autorisierte Einrichtungszugriffe.
- Auf dem Server wurde im Rahmen dieser Ground-Zero-Vorbereitung nichts
  verändert.

## Stop-Regel

Ohne eine neue, ausdrückliche Eintragung `G0-SRV-0: bestanden` und die danach
separat freigegebene Geräte-/Partitionsmatrix bleiben Löschen, `wipefs`,
Partitionierung, `mdadm --create`, LUKS-Formatierung und Betriebssysteminstallation
verboten.
