# Aufbewahrungsbetrieb – installiert und manuell abgenommen

23.09.2026, Reasoning Medium. Bestehender Backupbetrieb unverändert. Reale Installation und produktives Prune mit Restore-Prüfung erfolgreich. Zeitplanaktivierung am23.09.21:10:09UTC ebenfalls bestätigt; erster geplanter Lauf noch nicht beobachtet. Die folgenden Vorbereitungsabschnitte dokumentieren den vorherigen Stand.

## Dateien und Prüfung

- `artifacts/server-retention-runtime23.py` → `/home/klaus999/bpmaintret23.py`, SHA256 `92225a1c9f8bd82327a1f9a8c6a6046f7da693024b465fed6e7d58a64b493ba4`.
- `artifacts/server-retention-install23.py` → `/home/klaus999/bpinstallret23.py`, SHA256 `2a1b95307ab374f1c0160059030d1da0741470831623ef1b92de48ab84ec0d8a`.
- Wiederverwendet: unveränderter `bpret23.py`, SHA256 `0bf12a0f1f05f593264ccc7921cb8b711473dbbdab1115767ec5320e1263c119`. Weitere Root-Helfer über feste Hashes gebunden.
- Tests zuerst: sechs fehlende Ablauf-/Monitorfunktionen als fehlende Implementierung nachgewiesen, danach grün. Installer separat zunächst rot. Letzter gezielter Lauf: `python -m unittest tests.test_retention_runtime23 tests.test_retention23 -q`: **18 Tests bestanden**. Bestehende neun Backup-Runtime-Tests zusätzlich während der Implementierung bestanden.
- Nachgewiesen: Vorschau-/Snapshotdrift blockiert Löschung bzw. Prune; jüngster Stand und fremdes Profil bleiben erhalten; Fehler vor Prüfung verursacht keine Löschung; Restorefehler propagiert; fehlgeschlagenes Unmount löscht keinen Arbeitsbereich; veraltete/fehlende/fehlgeschlagene Wartung wird erkannt; unveränderte Fehlermeldung innerhalb einer Stunde nicht erneut versandt. SMTP in Tests ersetzt, keine Testmail.
- Linux `python3 /home/klaus999/bpinstallret23.py --check`: Exit0, `hashes_syntax_units_calendars_verified_no_installation`.
- Linux `python3 /home/klaus999/bpmaintret23.py --self-test`: Exit0, ausschließlich eigenes temporäres lokales Restic-Repository. `synthetic=true, production_access=false, mail_sent=false, repository_check=true, prune_verified=true, retained_snapshot_restore_verified=true`. Ein künstlicher Zwischenstand entfernt, drei Snapshots erhalten, darunter fremdes Profil. Temporärdaten entfernt.

## Verhalten und Grenzen

Daily 01:00 UTC (aktuell03:00CEST), zwischen den vierstündlichen Backups; Watchdog stündlich zur Minute30 und bei Dienstfehler. Gemeinsame operations.lock verhindert gleichzeitige Backup-/Retention-Arbeit. Sperrkonflikt führt zu Fehlerbericht und Alarm, nicht zum ungesperrten Lauf. Arbeitsbereiche beginnen mit runtime-retention-, damit auch der unveränderte Backup-Runner liegengebliebene Bereiche erkennt und stoppt.

Nur frischer verifizierter Backupstand unter acht Stunden. Feste SMB-Freigabe, verschlüsselter CIFS-Mount, Repository-ID und Operations-Cold-Profil. Vollständiger Check vor Änderung, frisch berechnete/erneut abgeglichene 7/4/6-Kandidaten, explizite IDs statt ungeprüfter Policy-Löschung. Prune mit maximal128MiB Repack und10Prozent toleriertem ungenutztem Datenanteil. Das begrenzt den Repack-Aufwand, nicht die insgesamt freigegebene Datenmenge; teilweise ungenutzter Platz kann bleiben.

Nach Prune vollständiger Check, exakte verbleibende Snapshotmetadaten, Restore des geschützten Snapshots mit --verify. Restore nur in eigenem lokalen Bereich, höchstens1GiB Nutzdaten und ausreichender freier Platz, keine Archive über Live-Dateien entpacken. Dienst maximal20Minuten, Abbruchbereinigung90Sekunden. Nicht abgehängter Mount bleibt erhalten und blockiert weitere Backups bis zur Prüfung. Keine automatische erzwungene Entsperrung.

Separater Wartungsalarm über vorhandenes SMTP; Erfolg älter als36h oder fehlgeschlagener/fehlender Bericht löst Alarm aus. Bei unverändertem Fehler höchstens ein Versandversuch je Stunde, Zustandswechsel können sofort melden. Server-/Netzausfall braucht weiterhin externe Überwachung. Kein Nachweis langfristiger RPO12h oder vollständiger RTO12h.

## Nächster Bedienpunkt

Root-KVM: `python3 /home/klaus999/bpinstallret23.py`.

Dieser Aufruf installiert zusätzliche Root-Helfer/Units und führt **einmal echte Aufbewahrung nach7/4/6 plus begrenztes Prune** mit Restore-Nachprüfung aus. Neue Timer bleiben aus. Bestehende Backup-/Watchdogtimer werden nicht geändert. Bei Fehler nicht wiederholen, Bericht `/var/tmp/aurelia-maintenance-install23-result.json` auswerten; Laufdetails zusätzlich `/var/tmp/aurelia-maintenance23-result.json`. Erst nach erfolgreicher realer Abnahme die beiden neuen Timer aktivieren und Zustand belegen. Keine aktuelle reale Abnahme behaupten.

## Reale Abnahme bestätigt

Betreiber meldete Root-Aufruf fertig; Bericht per SSH gelesen und lokal als `artifacts/maintenance-install23-report.json` gesichert. SHA256 `a0ac31cee736fc644e4928fa1dd60dd1196b377dde2ca69ce4062c58be8287c7`. Status `maintenance_installed_manual_run_verified_timers_disabled`, ok=true. Lauf etwa12Sekunden. Kein weiterer Snapshot entfernt (remove=[]), alle drei vorhandenen Stände erhalten. Prune, vollständiger Repositorycheck und Restore des geschützten8591d898 erfolgreich. Mount abgehängt, Staging entfernt, Originalmount unverändert. Watch healthy. Beide Services Result=success/inactive; neue Timer disabled/inactive. Bestehende Backup-/Watchdogtimer enabled/active. Keine freigegebene Bytezahl aus diesem Bericht ableitbar.

Nächster Root-Aufruf: `systemctl enable --now aurelia-retention23.timer aurelia-retention-watch23.timer`. Aktiviert tatsächliche wiederkehrende 7/4/6-Aufbewahrung mit Prune sowie eigenen Watchdog. Anschließend Zustände/Termine lesen; Aktivierung noch nicht belegt. Installer nicht wiederholen.

## Aktivierung nachgewiesen

23.09.2026 21:10:09UTC per SSH: beide Retentiontimer loaded/active/enabled. Nächster Lauf24.09.03:00CEST, nächster Retention-Watch23.09.23:30CEST. Beide bestehenden Backuptimer ebenfalls active/enabled. Letzte Retention-/Watchdienste Result=success. Nachweis `artifacts/retention-activation23.json`. Nach Tippfehlern aktivierte der Betreiber erfolgreich über `systemctl enable --now /etc/systemd/system/aurelia-ret*.timer` die beiden zuvor geprüften Dateien. Keine Wiederholung nötig. Aktivierung ist kein Nachweis des ersten späteren planmäßigen Retentionlaufs.
