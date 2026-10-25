# Feedback f – F2.2 sichere Admin-Catalog-Pfadpolicy

- **Stand:** 2026-07-13
- **Gate:** F2.2
- **Status:** GO
- **Gesamtfeature Feedback f:** NO-GO

## 1. Scope

F2.2 ergänzt ausschließlich eine offline und seiteneffektfrei arbeitende Pfadpolicy:

- Root aus `MORPHIC_ADMIN_CATALOG_DIR` oder `%LOCALAPPDATA%/MorphicEngine/admin_catalog`;
- kein Rückgriff auf den worktreebasierten `runtime_root()`-Default;
- kanonischer, an Operator, Workspace, Tenant und Scope gebundener Namespace;
- fail-closed Traversal-, Projektroot-, Export-/Archivroot- und Reparse-Schutz;
- systemweiter Scope standardmäßig nicht schreibbar;
- reine Point-in-time-Pfadplanung ohne Verzeichnis-, Datei- oder SQLite-Erzeugung.

Nicht enthalten sind Runtime-, Web-, CLI-, Engine- oder Netzwerkverdrahtung, Backup/Recovery (F2.3), HMAC/Audit-Verankerung (F2.4), Schema-Migration oder produktive Catalog-Aktivierung.

## 2. Sicherheitsverträge

| Vertrag | Umsetzung |
|---|---|
| Externer Default | `%LOCALAPPDATA%/MorphicEngine/admin_catalog`; fehlendes `LOCALAPPDATA` scheitert ohne Override geschlossen. |
| Expliziter Root | `MORPHIC_ADMIN_CATALOG_DIR` hat Vorrang; relative und traversierende Werte werden abgewiesen. |
| Kein Runtime-Default | `runtime_root()` wird weder importiert noch konsultiert. |
| Kontextnamespace | Kanonisches JSON aller vier Kontextdimensionen, SHA-256, Versionpräfix `ctx-v1-`. |
| System-Scope | `writable=True` wird für `scope="system"` standardmäßig abgewiesen; read-only Planung bleibt möglich. |
| Projekttrennung | Catalogroot innerhalb oder oberhalb des Projektroots wird abgewiesen. |
| Archivtrennung | Bekannte `Benutzer_*`-Roots einschließlich case-insensitiver `__<tenant>`-Varianten werden abgewiesen. |
| Parallel-Export | `MORPHIC_PARALLEL_EXPORT_ROOT` ist unverrückbare Standardsperre; equal/inside/above werden abgewiesen. |
| Zusatzroots | `blocked_roots` ergänzt Standardsperren ausschließlich additiv und kann sie nicht deaktivieren. |
| Reparse/Symlink | Bestehende Komponenten werden lexikalisch per `lstat()` auf Symlink-/Windows-Reparse-Attribute geprüft; echte Junction und dangling Junction sind testabgesichert. |
| TOCTOU-Grenze | Der Docstring bezeichnet die Rückgabe ausdrücklich als Point-in-time-Planung; spätere Integration muss unmittelbar vor Create/Open erneut validieren. |
| Seiteneffekte | Kein `mkdir`, kein Datei-/DB-Open, keine produktive Importverdrahtung. |

## 3. TDD- und Review-Evidenz

### Initiales RED

```text
ModuleNotFoundError: No module named 'core.admin_catalog.paths'
```

### Reviewfix-REDs

```text
11 failed, 16 passed, 1 skipped
1 failed, 29 passed, 1 skipped
6 failed, 30 passed, 1 skipped
```

Damit wurden real reproduziert:

- tenantgebundene bekannte Export-/Archivroots und `MORPHIC_PARALLEL_EXPORT_ROOT`;
- dangling Windows-Junction als konfigurierter Catalogroot;
- Abschaltung der Default-/Environment-Sperren über `blocked_roots=()`.

### Finales GREEN

```text
Pfadfokus:          36 passed, 1 skipped
Admin-Catalog:      118 passed, 1 skipped (-W error)
py_compile:         PASS
Top-5-Smoke:        1 passed in 154.06s
```

Der einzige Skip ist der privilegabhängige Windows-Symlink-Test. Echte Windows-Junction und echte dangling Junction wurden erstellt, geprüft und kontrolliert entfernt.

## 4. Breite Regression

```text
Gesamtsuite ohne Top-5: 598 passed, 3 skipped, 14 failed
Baseline ohne alle Admin-Catalog-Dateien: 480 passed, 2 skipped, 14 failed
Differenz: 118 neue grüne Admin-Catalog-Tests
```

Die 14 Fehler sind baseline-identisch:

- 13 bekannte prozessweite HTTP-429-/Rate-Limiter-Ausreißer;
- 1 inzwischen zeitabhängig abgelaufene feste Consent-Fixture (`NOW + 1 day` liegt am Ausführungstag in der Vergangenheit).

Keine Fehlerklasse stammt aus F2.2.

## 5. Unabhängiger Current-Snapshot-Review

Maßgeblicher hashgebundener Re-Review:

```text
Delegation: deleg_f377ca25
Verdikt: APPROVE
Konfidenz: HOCH
Offene P0–P3: keine
Adversariale Override-Matrix: 21/21 fail-closed
```

Verifizierte Snapshot-Hashes:

```text
core/admin_catalog/paths.py
  e5eaf86c7df2c41d8c6e8e4dfd3354d74eb2c51360ce97062d8a9f159932d6b1
tests/test_admin_catalog_paths.py
  388096c672ff5677674fef67530881e6c98c29455ba31afff89b0c054be542ac
```

Historische `REQUEST CHANGES` wurden als Findingquellen genutzt, aber nicht als Verdikt für den finalen Snapshot ausgegeben.

## 6. Nichtmutation

```text
data/remedies.db
c67d4e899dab9547a2171ec0d5604d9628721b6757a87d33ef8d34f0c0dadfa0
```

- Ports 8000 und 8090 blieben belegt und unberührt.
- Keine Runtime-, Web-, CLI-, Engine-, Legacy- oder Netzwerkverdrahtung.
- Kein Commit, Push, Staging, Reset oder Clean.
- Keine bestehenden Archive oder produktiven Catalogdaten verändert.

## 7. Gateentscheidung

**GO.** F2.2 erfüllt die freigegebenen Pfadpolicy- und Sandbox-Verträge im finalen hashgebundenen Snapshot ohne offene P0–P3.

F2 steht damit bei 50 %. Feedback f bleibt als Gesamtfeature NO-GO. Als nächster zulässiger Block folgt ausschließlich F2.3 – hashverifizierter Backup-/Recovery-Vertrag mit SQLite-Backup-API und ausschließlich synthetischen `tmp_path`-Stores.
