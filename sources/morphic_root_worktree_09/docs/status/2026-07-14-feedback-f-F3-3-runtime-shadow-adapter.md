# Feedback f – F3.3 Read-only Runtime-Adapter und F3-Gate

- **Stand:** 2026-07-14 12:08 CEST
- **Teilgate:** F3.3
- **Teilgate-Status:** GO
- **Gate:** F3 – Profilverwaltung ohne stille Runtimewirkung
- **Gate-Status:** GO
- **F3-Fortschritt:** 100 %
- **Konservativer Feedback-f-Fortschritt:** 44,4 %
- **Feedback f als Gesamtfeature:** NO-GO bis F8
- **Nächster zulässiger Block:** F4.1 – Legacy-Remedy-Import read-only

## Freigegebener Umfang

F3.3 ergänzt ausschließlich einen isolierten read-only Schattenadapter:

- ohne explizites `shadow_mode=True` wird der Catalog nicht gelesen;
- der Default und jede produktiv ausgewählte Profilliste bleiben Legacy;
- Legacyprofile werden als vollständig entkoppelte `ProfileDefinition`-Kopien geliefert;
- im Schattenmodus werden Aktivierungspointer und Revisionspayload atomar aus einem SQLite-Read-Snapshot gelesen;
- Entry-JSON, eingebetteter Kontext, DB-Identität, Entry-Hash und vollständiger Revisionsbundle-Hash werden geprüft;
- Cross-References werden vor dem Mapping validiert;
- deaktivierte Profile und Tombstones werden nicht als aktive Catalogprofile abgebildet;
- Diffs verwenden den normalisierten Catalog-ID-Vertrag und sind deterministisch sowie feldspezifisch;
- fehlende, defekte oder nicht sicher vergleichbare Snapshots fallen ausschließlich im Schattenmodus sichtbar und mit redigierten stabilen Fehlercodes auf Legacy zurück;
- es existiert kein Package-Reexport und kein produktiver Engine-, Web-, CLI- oder Scan-Consumer.

Damit sind F3.1, F3.2 und F3.3 abgeschlossen. F3 hat weiterhin keine stille Runtimewirkung und schaltet keine Catalogprofile produktiv frei.

## Integritätsgrenze

`CatalogStore.current_revision_snapshot()` liest Pointer und Payload innerhalb eines expliziten SQLite-`BEGIN`. Die gemeinsame Store-Verifikation bindet:

1. finalisierten Revisionsstatus,
2. bytegenau kanonisches Entry-JSON,
3. eingebetteten `CatalogContext`,
4. DB-Entry-Typ und DB-Entry-ID,
5. gespeicherten Entry-Hash,
6. vollständigen Revisionsbundle-Hash einschließlich Draft-Provenienz.

Manipulierte oder kontextfremde Payloads werden fail-closed abgewiesen.

## TDD- und Verifikationsevidenz

| Prüfung | Ergebnis |
|---|---:|
| finale F3.3-/Integritäts-Fokustests | 17 passed |
| finale Admin-Gesamtmatrix F0–F3 | 242 passed, 2 skipped |
| breite Regression ohne Top-5 | 722 passed, 4 skipped, 14 bekannte Baselinefehler |
| Top-5-Workflow-Smoke | 1 passed |
| `py_compile` | PASS |
| `git diff --check` | PASS |
| `data/remedies.db` | SHA-256 unverändert |
| Port 8090 | unangetastet |
| Port 8000 | frei |

Die breite Regression hat gegenüber dem Stand vor F3.3 ausschließlich die neuen Tests hinzugewonnen. Die 14 Fehler sind dieselben vorbekannten Baselinefehler: ein abgelaufener statischer Consent-Zeitpunkt und globale Web-Test-Rate-Limit-Leaks mit HTTP 429. Sie sind nicht durch F3 verursacht.

## Freigegebener Hashsnapshot

```text
core/admin_catalog/store.py
340975c006c50caec462576bc7896a2d8d253dda10522e6ca018792c84c7ae47

core/admin_catalog/runtime_adapter.py
e0b6f24f68d2572e4736d2b8096cbee7fde3e8f49103de924b9d02ffbe9fd499

tests/test_admin_catalog_store.py
1ef5631873b5a2f85e7fd9245868ba325bfd84c1c054c73600c4b475a5eeb1c2

tests/test_admin_catalog_runtime_adapter.py
853c5e4d5aab7edd6671b491d3c67ddb2fecb4aa3f1c285eb5a0a5f9c3fbd79a

core/admin_catalog/service.py
fb7cdbb3dcf8a7ffa8e524c8097e6f0411c3e1057786a2dafe26a7e26ff2027a

data/remedies.db
c67d4e899dab9547a2171ec0d5604d9628721b6757a87d33ef8d34f0c0dadfa0
```

## Unabhängige Reviews

| Review | Ergebnis |
|---|---|
| `deleg_f49f61e3` | REQUEST CHANGES: zwei P1 und drei P2 |
| `deleg_2d8faf3e` | technischer Timeout ohne Verdikt; keine Freigabewirkung |
| `deleg_e7b55495` Store | REQUEST CHANGES: ein P1 |
| `deleg_e7b55495` Adapter | REQUEST CHANGES: ein P1 und zwei P2 |
| `deleg_aa5de206` Store | **APPROVE**, hohe Konfidenz, keine neuen P0–P3 |
| `deleg_aa5de206` Adapter | **APPROVE**, Konfidenz 0,98, keine offenen P0–P3 |

Die finalen beiden APPROVE sind an die oben aufgeführten Hashes gebunden. Die Reviews waren strikt read-only und änderten keine Dateien.

## Ausdrücklich nicht freigegeben

- produktive Catalog-Runtimeumschaltung,
- Änderung von `MASTER_PROFILES`, Scan-, Engine-, Web- oder CLI-Consumerpfaden,
- Online-Fetch oder Repository-Synchronisierung,
- Remedy-/Multiplex-Migration außerhalb von F4,
- Auto-Publish oder Auto-Activate,
- Änderungen an `data/remedies.db`,
- F5–F8.

## Gateentscheidung

**F3.3: GO. F3: GO.**

Feedback f bleibt als Gesamtfeature NO-GO. Der nächste zulässige Arbeitsblock ist F4.1: bestehende Legacy-Remedy-/Pathogen-/Linkdaten ausschließlich read-only und deterministisch inventarisieren; keine Catalogaktivierung, keine Datenbankmutation und keine Runtimewirkung.

## Post-State-ShadowCopy

```text
E:\mprphic_v1_Backups\morphic_v1_shadowcopy_20260714_121237_feedback_f_F3_GO_post
```

Hauptmanifest:

```text
FILES=29 VERIFIED=29
SOURCE_MANIFEST_SHA256=23b7cdee841c0d1aa0b8c87856a61caf49e0b3298bc8c6ce29ca2013b4dcb487
```

Das Hauptmanifest bindet den vollständigen `core/admin_catalog`-Pythonbestand, die Admin-Testmatrix, Haupt-/Kurzplan, Gesamtfortschritt, F3.1-/F3.2-Gate-Records, Golden Record, Projektmanifeste und eine lokale Evidenz der beiden finalen APPROVE. Der vorliegende finale F3.3-/F3-Gate-Record wird wegen der Selbstreferenzfreiheit separat im selben Ordner durch `FINAL_DOCUMENTATION.sha256` gebunden. Beide Manifeste wurden nach dem Kopieren vollständig gegen die externen Dateien verifiziert.
