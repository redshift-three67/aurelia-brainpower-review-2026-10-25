# Aurelia / Modul-Templates – vorgeschaltete Voraussetzungen

Aktueller Folgeabgleich nach abgeschlossenem synthetischem T3: [Voraussetzungen vom 20.09.](VORAUSSETZUNGEN_NACH_T3_2026-09-20.md). Nachfolgender Stand vom18.09. ist historisch; insbesondere spätere Konfigurations-/Schlüssel-/Recoverybelege nicht daraus als fehlend ableiten.

Lesender Abgleich am 18.09.2026. Betreiberentscheidung: zuerst diese Voraussetzungen klären; noch kein erstes Modul zur Übertragung bestimmt.

Aktualisierung nach SMB-Test: Anmeldung, SMB 3.1.1 mit Verschlüsselung und tatsächlicher synthetischer NAS-Backup-/Restoretest erfolgreich (siehe `verification/SMB_RESTORE_2026-09-18.md`). Die folgenden alten Angaben zu fehlendem Login/Mount sind historische Befunde. Gezielte Konfigurationssicherung jetzt vorbereitet, noch nicht mit echten Konfigurationen ausgeführt. Keine vollständige produktive Backupplattform vorziehen; projektspezifische Sicherung erst passend zur ersten Integration. G0-SRV-0 bleibt ohne Abgleich seiner vollständigen Kriterien und ausdrückliche Gateentscheidung unbestätigt.

| Bereich | Beobachteter Quellenstand | Erforderlicher Abschluss |
|---|---|---|
| Aurelia Ground Zero | `Aurelia/docs/STATUS.md` und `docs/project-control/ground-zero/GATE-STATUS.md` vom 25.08.2026 stehen noch auf „server_changes_started: false“ und ausstehendem Backup/Restore. Brainpower-Infrastrukturnachweise vom 15.09. beschreiben dagegen bereits Ubuntu-/Desktop-/VPN-Arbeiten. | Historische Planung und tatsächlichen Serverstand getrennt halten; aktuelle lesende Inventur und Backup-/Restore-Nachweise vor einer neuen Gatebewertung. Keine erneute Installation aus dem alten Plan ableiten. |
| Backup/Restore | G0-SRV-0 verlangt einen echten externen Sicherungs- und Wiederherstellungsnachweis. SMB-Benutzer inzwischen k213487 bestätigt; die bisherigen Mountversuche waren nicht erfolgreich belegt. | Tatsächliche Anmeldung, verschlüsselten Mount, getrennten synthetischen Backup-/Restorebereich und Hashvergleich nachweisen; danach erst Schutzrichtlinie/Timer. |
| Vertragsautorität | `Modul_Templates/README.md`: Aurelia ist Referenz, Integration erst ab S4. `standards/API_CONTRACT.md`, `standards/REIFEGRADE.md` und `UEBERGABE_AURELIA.md` sind Koordinations-/Übergabequellen. | Gegen aktuelle Aurelia-ABI-/Admin-/Mandanten-/CopyGuard-Verträge abgleichen und Abweichungen ausdrücklich entscheiden; Übergabeangebot ist keine Registryfreigabe. |
| RadiWorks | `REIFEGRADE.md` dokumentiert S0–S3 lokal, S4 nicht zertifiziert, S5 offen. Übergabe nennt nullable Mandantenfelder ohne Nachweis von Authentifizierung oder tenant-scoped Queries. | Für spätere Modulwahl: wiederholbarer Linux-Smoke, Manifest/Contract, Mandantentrennung, sichtbare Texte/CopyGuard, WebSocket und Betriebsdokumentation. Vorher keine Integrationsreife behaupten. |
| Modulreihenfolge | `MODULE_REGISTRY.md` nennt historisch „Morphic zuerst“; lokale Modulpfade/Reifegrade enthalten teils ältere Angaben. | Priorität und aktuelle Quellen mit Aurelia abgleichen, bevor ein Erstmodul und seine konkreten Adapter freigegeben werden. Keine automatische Wahl von RadiWorks allein wegen seines höheren lokalen Reifegrads. |

## Nächster konkreter Ablauf

1. Hermes-Abnahme für das begrenzte direkte Pilotprofil abschließen.
2. Aktuellen Ubuntu-/VPN-/RAID-/Dienst-/SMB-Zustand lesend erheben; Beobachtungszeit und Grenzen speichern.
3. Fehlende Provideranmeldung gegebenenfalls verdeckt vervollständigen, synthetisches Backup tatsächlich wiederherstellen und vergleichen. Kein produktiver Restore.
4. Mit diesen Belegen den Aurelia-Gatestatus und die Vertragsautorität zur konkreten Betreiberentscheidung vorlegen.
5. Erst danach Erstmodul/Adapter und isolierten Server-Integrationsplan konkretisieren. Produktfreigabe bleibt getrennt.

Dieser Abgleich verändert keine externen Produktdateien, Freigaben oder Registrierungen. Quellen wurden gezielt gelesen; kein vollständiger Audit der Produktrepositories.

## Ergänzender aktueller Servercheck

18.09.2026 10:45 UTC, lesend über WireGuard mit bestehendem temporären Schlüssel und geprüftem Hostschlüssel: Ubuntu 24.04.5 LTS, Kernel 6.8.0-139-generic, beide RAID1 [UU], null failed Units. Firewall und wg-admin aktiv. Restic und mount.cifs vorhanden, kein CIFS-Mount, aurelia-backup-files.timer disabled. Health-Unit letzter Result=success/ExecMainStatus=0; kein umfassender Sicherheits- oder Hardwaretest. sudo -n verlangt Passwort. Keine Serveränderung; Root-Zugang für weitere SMB-/Restoreprüfung noch erforderlich. Dies widerlegt den aktuellen Geltungsanspruch der alten „keine Serveränderungen“-Dokumentation, ersetzt aber nicht deren fehlende Gatebelege.
