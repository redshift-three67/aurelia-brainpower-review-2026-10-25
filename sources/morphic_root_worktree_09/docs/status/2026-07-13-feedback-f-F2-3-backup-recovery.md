# Feedback f – F2.3 Backup-/Recovery-Vertrag

- **Stand:** 2026-07-13
- **Gate:** F2.3
- **Status:** GO
- **Gesamtfeature Feedback f:** NO-GO

## 1. Scope

F2.3 ergänzt ausschließlich einen lokalen, offline arbeitenden Backup-/Recovery-Baustein für den isolierten Admin-Catalog:

- konsistentes SQLite-Backup über `sqlite3.Connection.backup()`;
- Manifest mit Manifest-/Catalog-Schemaversion, Dateigröße und SHA-256;
- Restore ausschließlich in einen noch nicht vorhandenen Zielstore;
- Integritäts-, Schema-, Sidecar- und Bundleprüfung;
- atomare Publikation ohne Überschreiben eines bestehenden oder konkurrierend entstehenden Ziels;
- sichere Handle- und Temp-Artefakt-Behandlung.

Nicht enthalten sind Runtime-, Web-, CLI-, Engine-, Legacy- oder Netzwerkverdrahtung, produktive Catalog-Aktivierung, HMAC-Verankerung (F2.4), Online-Synchronisation oder Schema-Migration.

## 2. Sicherheits- und Konsistenzverträge

| Vertrag | Umsetzung |
|---|---|
| Konsistenter Snapshot | Ausschließlich SQLite-Backup-API; committed WAL-Zustand wird übernommen. |
| Selbständiges Artefakt | Temporäre Snapshots werden auf `journal_mode=DELETE` normalisiert. |
| Manifestbindung | Exakte Größe und SHA-256; deklarierte Manifest- und Catalog-Schemaversion. |
| Ehrliches Catalog-Schema | SHA-256-Fingerprint aller nicht automatisch erzeugten `sqlite_master`-Tabellen, -Trigger, -Indizes und -Views; zusätzliche oder abweichende Objekte werden abgewiesen. |
| Interne SQLite-Objekte | Nur echte `sqlite_autoindex_*`-Einträge mit `sql IS NULL` sind ausgenommen; beispielsweise `sqlite_stat1` wird erkannt und abgewiesen. |
| Sidecars | `-wal`, `-shm` und `-journal` sowie jede weitere nicht manifestierte Bundle-Datei werden vor Restore abgewiesen. |
| Exaktes Bundle | Backupverzeichnis enthält ausschließlich `catalog.sqlite3` und `manifest.json`. |
| Restoreziel | Muss absolut, neu und unter einem bestehenden sicheren Elternverzeichnis liegen. |
| Nichtüberschreiben | Windows: `os.rename()` ohne Replace-Semantik; POSIX: Create-only-Hardlink-Publikation. Ein konkurrierendes Ziel bleibt erhalten. |
| Postpublish-Prüfung | Dateiidentität, Sidecarfreiheit, Manifestgröße/SHA-256 und Schema werden am publizierten Ziel erneut geprüft. |
| Sicherer Postpublish-Fehler | Nach Publikation wird bei Fehlern nichts am Ziel oder an Sidecars gelöscht; dadurch keine nicht atomar bindbare Cleanup-Race gegen fremde Dateien. |
| Handle-Lebensdauer | Source und Target werden über verschachtelte `finally`-Blöcke unabhängig geschlossen, auch bei Open-, Backup- oder Close-Fehlern. |
| Reparse-/Junction-Schutz | Symlinks, Windows-Reparse-Points und dangling Junctions werden fail-closed behandelt. |
| Offline-Grenze | Keine produktiven Aufrufer; ausschließlich synthetische Testdaten. |

## 3. TDD- und Review-Evidenz

### Initiales RED

```text
ModuleNotFoundError: No module named 'core.admin_catalog.backup'
```

### Reproduzierte Review-REDs

Test-first reproduziert und geschlossen wurden unter anderem:

- concurrent target konnte durch Existenzprüfung plus `os.replace()` überschrieben werden;
- Source-Connection blieb bei Fehlern während des zweiten Opens offen;
- gleichnamige wirkungslose Trigger täuschten Catalog-Schema 1 vor;
- ungehashter WAL-Zustand konnte nach initialer Prüfung einfließen;
- zusätzliche reguläre und interne SQLite-Objekte blieben unentdeckt;
- tatsächlich erzeugte Create-/Restore-Snapshots waren nicht in jedem Pfad erneut gebunden;
- sequenzielle `close()`-Aufrufe verhinderten bei Close-Fehlern das zweite Close;
- postpublish Cleanup konnte fremde Sidecars oder eine racing Ersatzdatei löschen.

### Finales GREEN

```text
Backup-/Restore-Fokus: 31 passed, 1 skipped (-W error)
Admin-Catalog-Matrix:  149 passed, 2 skipped (-W error)
py_compile:             PASS
CatalogStore-Roundtrip: PASS
Top-5-Smoke:            1 passed in 97.88s
```

Der Skip betrifft den privilegabhängigen Windows-Symlink-Vertrag. Windows-Junction-, dangling-Junction- und Publikationsverträge wurden real ausgeführt.

## 4. Breite Regression

```text
Gesamtsuite ohne Top-5: 629 passed, 4 skipped, 14 failed
Baseline ohne Admin-Catalog-Dateien: 480 passed, 2 skipped, 14 failed
Differenz: 149 neue grüne Admin-Catalog-Tests und 2 zusätzliche plattformabhängige Skips
```

Die 14 Fehler sind baseline-identisch:

- 13 bekannte prozessweite HTTP-429-/Rate-Limiter-Ausreißer;
- 1 zeitabhängig abgelaufene feste Consent-Fixture.

Keine Fehlerklasse stammt aus F2.3.

## 5. Unabhängiger Current-Snapshot-Review

Maßgeblicher hashgebundener finaler Re-Review:

```text
Delegation: deleg_43f1679f
Verdikt: APPROVE
Konfidenz: HOCH
Offene P0–P3: keine
```

Verifizierte Snapshot-Hashes:

```text
core/admin_catalog/backup.py
  fb6047461b8a9326a8976b18cd86cdfb7131a6584e7c8f5c3b6f1cc9f8c7690d
tests/test_admin_catalog_backup.py
  717610fa3229868a498f12d3d5e6823a21bc5ebccce64a1057019aab395ad01a
```

Historische `REQUEST CHANGES` wurden als Findingquellen genutzt, aber nicht als Verdikt für den finalen Snapshot ausgegeben.

## 6. Nichtmutation

```text
data/remedies.db
c67d4e899dab9547a2171ec0d5604d9628721b6757a87d33ef8d34f0c0dadfa0
```

- Ports 8000 und 8090 blieben belegt und wurden nicht verändert.
- Auf Port 8090 waren weiterhin die bereits beobachteten PIDs 18240 und 9056 sichtbar; keiner wurde durch F2.3 gestartet oder beendet.
- Keine Runtime-, Web-, CLI-, Engine-, Legacy- oder Netzwerkverdrahtung.
- Kein Commit, Push, Staging, Reset oder Clean.
- Keine bestehenden Archive oder produktiven Catalogdaten verändert.

## 7. Gateentscheidung

**GO.** F2.3 erfüllt den Backup-/Recovery-Vertrag im finalen hashgebundenen Snapshot ohne offene P0–P3.

F2 steht damit bei 75 %. Feedback f bleibt als Gesamtfeature NO-GO. Als nächster zulässiger Block folgt ausschließlich F2.4 – explizite Audit-Integritätsstufen und HMAC-SHA-256 mit synthetischen Schlüsseln und ohne produktive Key-Provider- oder Runtimeverdrahtung.
