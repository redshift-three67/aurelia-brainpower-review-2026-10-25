# Feedback f – F4.1 Legacy-Remedy-Import read-only

- **Stand:** 2026-07-14 17:03 CEST
- **Teilgate:** F4.1
- **Teilgate-Status:** GO
- **Gesamtgate F4:** offen; F4.2–F4.4 ausstehend
- **Feedback f als Gesamtfeature:** NO-GO bis F8
- **Branch:** `operator-workbench-phase1`
- **HEAD:** `619a1f5485a151816e32732929a6a823839ccb57`

## 1. Freigegebener Umfang

F4.1 inventarisiert die bestehende Legacy-Remedy-Authority deterministisch und ohne Runtimewirkung:

- 4.079 Remedies;
- 1.273 Pathogene;
- 4.373 Remedy-Pathogen-Relationen;
- insgesamt 9.725 valide Catalogprojektionen;
- stabile, typisierte Catalog-IDs aus Legacy-Integer-IDs;
- vollständige Linkziele und Prioritäten;
- vorhandene Raw-Source-Werte bleiben erhalten, verleihen aber kein Vertrauen;
- sämtliche Einträge bleiben `legacy_unprovenanced`.

Es gibt keinen Package-Reexport und keinen produktiven Runtime-, Engine-, Web-, CLI-, Scan-, Publish-, Activate- oder Netzwerk-Consumer.

## 2. Read-only- und Integritätsgrenze

Der finale Vertrag ist stärker als ein erneutes pfadbasiertes SQLite-`mode=ro`-Öffnen:

1. Die Source-Datei wird einmal über einen gehaltenen Dateihandle gelesen.
2. Pfad-/Handle-Identität, Größe, `mtime_ns`, Bytelänge und SHA-256 werden gebunden.
3. Vor und nach der Aufnahme werden `-wal`, `-shm` und `-journal` fail-closed abgewiesen.
4. Exakt diese unveränderlichen Bytes werden direkt an `sqlite3.Connection.deserialize()` übergeben; es gibt keine temporäre Datenbankdatei und keinen zweiten Pfad-Open.
5. Die private `:memory:`-Verbindung setzt vor und nach `deserialize()`:
   - `query_only=ON`;
   - `temp_store=MEMORY`;
   - `trusted_schema=OFF`.
6. Danach folgen explizites `BEGIN` und vollständiger `integrity_check`.
7. Die drei importierten Tabellen sind vollständig über `table_xinfo` an Reihenfolge, Name, Typ, `NOT NULL`, Default, PK und Hidden-/Generated-Marker gebunden.
8. Fehlende, zusätzliche, anders typisierte oder versteckte Spalten, Orphans, doppelte IDs und Sourceänderungen schlagen fail-closed fehl.

Der instrumentierte Regressionstest bindet den SHA-256 der tatsächlich an `deserialize()` übergebenen Bytes exakt an den Source-/Export-Hash. Damit besteht kein Hash→Pfad→SQLite-TOCTOU.

## 3. Daten- und Projektionsvertrag

- Raw-Felder aller Remedies und Pathogene werden feldgenau erhalten.
- Relation-ID, Remedy-ID, Pathogen-ID und Priorität werden vollständig erhalten.
- Namen dienen nicht als Identität; vorhandene Casefold-Kollisionen beeinflussen stabile IDs nicht.
- Jede Remedy-, Pathogen- und Relationsprojektion wird als vollständiges exaktes `data`-Mapping geprüft.
- `validate_entries()` akzeptiert alle 9.725 Projektionen ohne Cross-Reference-Fehler.
- Kanonisches JSON ist deterministisch und als Known Answer gebunden.

Known-Answer Export-SHA-256:

`21141427843b112560c333681e4512e24110b5d9701a192d840a192a9304e6a4`

## 4. TDD- und Reviewverlauf

Der erste F4.1-Stand war funktional grün, erhielt aber `REQUEST CHANGES` wegen nicht gebundener WAL-/Sidecar-Semantik, Pfad-TOCTOU, fehlender Relation-ID-Eindeutigkeit und Testlücken.

Der zweite Stand band eine private immutable Snapshotdatei, erhielt jedoch erneut `REQUEST CHANGES`, weil zwischen Snapshot-Hash und pfadbasiertem SQLite-Open ein A→B→A-Fenster verblieb und die Tabellenschemata nicht vollständig gebunden waren.

Der finale Stand entfernt den Snapshotpfad vollständig, deserialisiert exakt die hashgebundenen Bytes in Memory, bindet `table_xinfo` vollständig und vergleicht alle Projektionsmappings exakt.

Finale hashgebundene Reviews `deleg_82f9e495`:

| Review | Verdikt | Konfidenz | Offene P0–P3 |
|---|---|---:|---:|
| SQLite/Security | APPROVE | 0,97 | 0 |
| Daten/Contracts | APPROVE | 0,98 | 0 |

Die Reviewer änderten keine Dateien und bestätigten die Hashes zu Beginn und Ende.

## 5. Finale Hashbindung

| Artefakt | SHA-256 |
|---|---|
| `core/admin_catalog/legacy_remedy_adapter.py` | `0828434114e5870efcea36f144b6c93542863525ead1e40f362777215334057f` |
| `tests/test_admin_catalog_legacy_remedies.py` | `03de5f924d22d6198e13176864f969c333ffcb68615c940f8d25c0e557b2cb1e` |
| `data/remedies.db` | `c67d4e899dab9547a2171ec0d5604d9628721b6757a87d33ef8d34f0c0dadfa0` |
| `core/admin_catalog/contracts.py` | `5e5af414f4188d60df2b9bc730528add87165695b913affb539fe28c3bd6c7c4` |
| `core/admin_catalog/validation.py` | `bd4ba94581e2101259b4cb69488f55102e8b0b047c7626b3e1f161428445b443` |

## 6. Verifikation

| Prüfung | Ergebnis |
|---|---:|
| F4.1-Fokus mit `-W error` | 14 passed, 1 skipped |
| Admin F0–F4.1 mit `-W error` | 256 passed, 3 skipped |
| Breite Regression ohne Top-5 | 736 passed, 5 skipped; exakt 14 bekannte Baselinefehler |
| Top-5-Smoke | 1 passed |
| `py_compile` | PASS |
| `git diff --check` | PASS |
| Remedy-DB | hashidentisch |
| Port 8090 | unangetastet |
| Port 8000 | frei |

Der Skip betrifft ausschließlich fehlende Windows-Berechtigung zum Erzeugen synthetischer Symlinks; reguläre, fehlende, Verzeichnis-, Sonderzeichen- und Pfad-Swap-Verträge sind grün.

## 7. Gateentscheidung

**F4.1 = GO.**

**F4 bleibt offen.** Als nächster zulässiger Block folgt ausschließlich F4.2: die drei Legacy-Multiplexmodelle getrennt und read-only inventarisieren. Remedy-/Multiplex-Draft-CRUD (F4.3), Launcherentscheidung (F4.4), Publish, Activate, Runtimewirkung und Netzwerk bleiben NO-GO.

## 8. Post-State-ShadowCopy

Zirkelfreie externe Sicherung:

`E:\mprphic_v1_Backups\morphic_v1_shadowcopy_20260714_170549_feedback_f_F4_1_GO_post`

- Hauptmanifest: 38/38 Dateien hashverifiziert;
- Hauptmanifest: `SHA256SUMS.txt`;
- Hauptmanifest-SHA-256:
  `26f32e3bf416ee99a2e0def36674005aa67db0d7a09eeae1de0b4ec0ebfbe292`;
- Inhalt: Admin-Catalog-Code und -Tests, unveränderte Remedy-DB, Plan-/Status-/Golden-Record-Dokumente sowie beide finalen Reviewberichte;
- der finale Gate-Record wird separat nach diesem Eintrag kopiert und über `FINAL_DOC_SHA256SUMS.txt` verifiziert, damit keine Manifest-Zirkularität entsteht.
