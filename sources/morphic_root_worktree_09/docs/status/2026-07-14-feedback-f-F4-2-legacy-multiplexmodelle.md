# Feedback f – F4.2 Legacy-Multiplexmodelle read-only

- **Stand:** 2026-07-14 18:41 CEST
- **Teilgate:** F4.2
- **Teilgate-Status:** GO
- **Gesamtgate F4:** offen; F4.3–F4.4 ausstehend
- **Feedback f als Gesamtfeature:** NO-GO bis F8
- **Branch:** `operator-workbench-phase1`
- **HEAD:** `619a1f5485a151816e32732929a6a823839ccb57`

## 1. Freigegebener Umfang

F4.2 inventarisiert die getrennten Legacy-Multiplex-Authorities deterministisch und ohne produktive Wirkung:

- 55 Runtime-Multiplexgruppen aus der prozeduralen Runtime-Authority;
- 40 explizite Remedy-Gruppen aus dem separaten Remedy-Gruppenregister;
- 4.373 bereits durch F4.1 vollständig gebundene Remedy-Pathogen-Relationen als eigener, nicht scanverbrauchter Modelltyp;
- optionale Custom-Gruppen und Custom-Multiplexe aus `config/groups_config.json` einschließlich `type`, Beschreibungen, Zeitfeldern, Gruppenreferenzen, Fokusfeldern und `k_total`;
- 16 BAT-Fallbackschlüssel mit 48 Remedy-Paaren sowie separatem Default-Fallback und Matcherhash;
- deterministische Konfliktberichte für Authority-, Namens-, Casefold-, Gruppen-/Multiplex-, Referenz- und Beschreibungskollisionen.

Die Produktionskonfiguration `config/groups_config.json` ist nicht vorhanden und wird durch den Adapter nicht erzeugt. Es gibt keinen Package-Reexport und keinen produktiven Runtime-, Engine-, Web-, CLI-, Scan-, Publish-, Activate- oder Netzwerk-Consumer.

## 2. Authority- und Wirkungsgrenzen

Die Authorities bleiben sichtbar getrennt:

1. prozedurale Runtime-Multiplexe: `active_runtime`;
2. explizite Remedy-Gruppen: separate Registryklassifikation;
3. Remedy-Pathogen-Relationen: `not_consumed_by_scan`;
4. Custom-Multiplexe: `no_runtime_effect`;
5. BAT-Hardcode-Fallbacks: `fallback_only`, `authoritative=False`.

Eine Namens-, ID- oder Casefold-Übereinstimmung vereinigt diese Authorities nicht und erhöht weder Vertrauen noch Scanwirksamkeit. Sämtliche Einträge bleiben `legacy_unprovenanced`.

## 3. Read-only-, Pfad- und Snapshotgrenze

- Custom- und BAT-Dateien werden über atomare No-Follow-Handles geöffnet:
  - Windows: `CreateFileW` mit `FILE_FLAG_OPEN_REPARSE_POINT`, ohne Write-/Delete-Sharing;
  - POSIX: `O_NOFOLLOW` und Regular-File-Prüfung.
- Zwei vollständige Reads, `fstat` vor/nach, Größen-/Zeitvergleich und ein zweites No-Follow-Open binden Bytes, Hash und Pfadidentität.
- Verschwindet die optionale Config nach erfolgreichem ersten Open, schlägt der Export fail-closed fehl; nur Abwesenheit beim ersten Open ergibt `configured=False`.
- Jede gebundene Textquelle ist auf 1 MiB begrenzt; `MemoryError` und `RecursionError` werden stabil und pfadfrei redigiert.
- Der Adapter konstruiert keinen `GroupManager`, schreibt keine Datei und verändert keine Authority.
- `data/remedies.db` bleibt durch den bereits freigegebenen F4.1-Bytes→In-Memory-Vertrag gebunden und unverändert.

## 4. BAT-Vertrag

Die BAT-Authority ist vor UTF-8-Decoding und AST-Auswertung exakt an folgenden SHA-256 gebunden:

`6b6b9f2536bd838dfe26455460082fae3b1f513e077f7b015623b545e558b6a5`

Jede Byteänderung – einschließlich Aliasbildung, Decorators, importiertem `exec`, indirekter Mutation oder Kontrollflussänderung – wird dadurch vor der Interpretation abgewiesen. Der Matcher ist zusätzlich an folgenden SHA-256 gebunden:

`a41964d281421cb9f39416220691b0cfed288dd83c5c4ad01ca3bfd28f602c25`

Die Defaultprojektion akzeptiert ausschließlich eine literale Remedy-Paarliste mit exakt `[:max_remedies]`. Der BAT-Code wird niemals importiert oder ausgeführt.

## 5. Daten- und Konfliktvertrag

- Alle 55 Runtime-Multiplexe behalten jedes statische oder dynamische Label und dessen Labelquelle.
- Alle 40 expliziten Remedy-Gruppen bleiben separat und feldgenau erkennbar.
- Das Relationsmodell bindet alle 4.373 stabilen Relations-IDs und den vollständigen F4.1-Exporthash; F4.1 bindet bereits sämtliche Relationfelder, Ziele und Prioritäten.
- Custom-`type` und alle weiteren Customfelder werden vollständig erhalten.
- Doppelte JSON-Schlüssel, unbekannte Felder, falsche Shapes/Typen und falsche Versionen schlagen fail-closed fehl.
- Runtime- und Custom-Casefold-Konflikte können gleichzeitig gemeldet werden.
- `group_descriptions` erkennt unbekannte, case-abweichende, casefold-kollidierende und mehrdeutige Referenzen.
- Konflikte werden sortiert berichtet; es gibt kein stilles Last-write-wins.

Kanonischer Known-Answer Export-SHA-256:

`ff714fe6f83c2f277248319dcfee7af2351c73d75c467298bb2fb1e869c46bb6`

## 6. TDD- und Reviewverlauf

Mehrere hashgebundene Reviewzyklen blieben zunächst `REQUEST CHANGES` und führten insbesondere zu:

- atomarem No-Follow-Descriptorbinding statt Pfad-Precheck;
- vollständiger Customfeld- und Konflikterhaltung;
- fail-closed Behandlung doppelter JSON-/BAT-Deklarationen;
- exakter BAT-Authority- und Matcherhashbindung statt unvollständiger allgemeiner Python-Datenflussanalyse;
- fail-closed Reopen-Removal sowie Größen- und Ressourcenlimits.

Finale hashgebundene Reviews `deleg_0c21a5c3`:

| Review | Verdikt | Konfidenz | Offene P0–P3 |
|---|---|---:|---:|
| Security/Nullmutation | APPROVE | hoch | 0 |
| Daten/Contracts | APPROVE | hoch | 0 |

Die Reviewer änderten keine Dateien und bestätigten alle Scope-Hashes zu Beginn und Ende.

## 7. Finale Hashbindung

| Artefakt | SHA-256 |
|---|---|
| `core/admin_catalog/legacy_multiplex_adapter.py` | `314b41c04e2ae3544c834ca9ea5a6faca48fe99cb9c84cc11f434d2aae8b08ba` |
| `tests/test_admin_catalog_legacy_multiplexes.py` | `87f09b41fe34662eb4b11a0dbf4e3e14e7152b911479bcb078f593a9a54db7af` |
| `core/admin_catalog/legacy_remedy_adapter.py` | `0828434114e5870efcea36f144b6c93542863525ead1e40f362777215334057f` |
| `tests/test_admin_catalog_legacy_remedies.py` | `8fa092bc74a077f170294b23b35fcefb69136447b6f39a6f949c145e6c3845e9` |
| `data/remedies.db` | `c67d4e899dab9547a2171ec0d5604d9628721b6757a87d33ef8d34f0c0dadfa0` |
| `core/subgroups/procedural_groups.py` | `1c362690f4569fab5ec6bf816be18c5462711a6350a58a22cded162721da1f8c` |
| `core/remedy_group_registry.py` | `7b75fcd52a68405c9c2b6cbbba903282d27db62a8b86f22717ad7740fcf4b9bc` |
| `core/bat_report_aggregator.py` | `6b6b9f2536bd838dfe26455460082fae3b1f513e077f7b015623b545e558b6a5` |

## 8. Verifikation

| Prüfung | Ergebnis |
|---|---:|
| F4.2-Fokus mit `-W error` | 30 passed, 2 skipped |
| Admin F0–F4.2 mit `-W error` | 286 passed, 5 skipped |
| Breite Regression ohne Top-5 | 766 passed, 7 skipped; exakt 14 bekannte Baselinefehler |
| Top-5-Smoke | 1 passed |
| `py_compile` | PASS |
| `git diff --check` | PASS |
| Remedy-DB und Authorities | hashidentisch |
| `config/groups_config.json` | weiterhin nicht vorhanden |
| Port 8090 | PID 20404, unangetastet |
| Port 8000 | frei |

Die zwei Fokusskips betreffen ausschließlich fehlende Windows-Berechtigung zum Erzeugen synthetischer Custom-/BAT-Symlinks. Der reale Windows-No-Follow-Pfad sowie adversarialer Pfadwechsel und Reopen-Removal sind grün.

## 9. Gateentscheidung

**F4.2 = GO.**

**F4 bleibt offen.** Als nächster zulässiger Block folgt ausschließlich F4.3: Remedy-/Multiplex-Draft-CRUD und Cross-References. F4.4, Publish, Activate, produktive Runtimewirkung und Netzwerk bleiben NO-GO.

## 10. Post-State-ShadowCopy

Zirkelfreie externe Sicherung:

`E:\mprphic_v1_Backups\morphic_v1_shadowcopy_20260714_184121_feedback_f_F4_2_GO_post`

- Hauptmanifest: 45/45 Dateien hashverifiziert;
- Hauptmanifest: `SHA256SUMS.txt`;
- Hauptmanifest-SHA-256:
  `99a6760759155c9a2b05e1e147f1b9b25ed7c7c171c76881e90c3b609ad7adbf`;
- Inhalt: vollständiger Admin-Catalog-Code und Admin-Testscope, unveränderte Remedy-DB, getrennte Legacy-Authorities, Plan-/Status-/Golden-Record-Dokumente sowie sämtliche vier F4.2-Reviewzyklen;
- der finale Gate-Record ist absichtlich nicht Teil des zirkelfreien Hauptmanifests und wird nach diesem Eintrag separat über `FINAL_DOC_SHA256SUMS.txt` synchronisiert und verifiziert.
