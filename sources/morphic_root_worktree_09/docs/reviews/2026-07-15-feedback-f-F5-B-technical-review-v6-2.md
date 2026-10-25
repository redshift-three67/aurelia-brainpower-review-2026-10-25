# Review 2 – F5-B Technical Freeze v6

## Verdict

**REQUEST CHANGES**

**Confidence:** Hoch
**Reviewmodus:** vollständig unabhängig, adversarial, statisch und read-only
**Driftstatus:** driftfrei; das Verdict ist an exakt die geprüften Bytes gebunden.

## 1. Start- und Endnachweis

| Nachweis | Start | Ende | Ergebnis |
|---|---|---|---|
| Freeze SHA-256 | `cf3c2a880b9903bbbf65393efe7117a2248a4e23abec3c6fa365bd5cfc218db6` | identisch | PASS |
| Branch | `operator-workbench-phase1` | identisch | PASS |
| HEAD | `619a1f5485a151816e32732929a6a823839ccb57` | identisch | PASS |
| Manifestumfang | exakt 41 Dateien | exakt 41 Dateien | PASS |
| Scope gegen Manifest | 41/41 | 41/41 | PASS |
| Registry-Authority | `6c93c5a1aab9b022bf22e3a8c8097b07bde2738efec3678645ffadf849e4a0b3` | identisch | PASS |
| Remedy-DB | `c67d4e899dab9547a2171ec0d5604d9628721b6757a87d33ef8d34f0c0dadfa0` | identisch | PASS |
| Produktiver Stage-Key | nicht vorhanden | nicht vorhanden | PASS |

Es trat **kein Scope-Drift** auf. `INVALIDATED BY SCOPE DRIFT` ist daher nicht einschlägig.

## 2. Finding-Zählung

| Priorität | Anzahl |
|---|---:|
| P0 | 0 |
| P1 | 3 |
| P2 | 0 |
| P3 | 1 |

Nach der Freeze-Regel erzwingt bereits ein P3 `REQUEST CHANGES`.

---

## 3. Findings

### P1-1 – Live-Registry-Revalidation ist nicht an eine stabile Dateiidentität gebunden

**Evidenz:**

- `core/source_registry.py:188-192`
- `core/source_registry.py:232-240`
- `core/source_registry.py:968-984`
- `core/source_registry.py:1119-1153`
- `core/admin_catalog/store.py:1879-1894`
- `core/admin_catalog/store.py:2040-2054`
- Freeze-Claim: `docs/status/2026-07-15-feedback-f-F5-B-technical-freeze-v6.md:49,52`

`SourceRegistry.load()` liest zunächst unmittelbar über den caller-/pfadbasierten Namen:

```python
registry_path = Path(path)
payload = _strict_json_load(registry_path)
```

Erst nach dem vollständigen Parse wird über den Konstruktor `_canonical_registry_path()` ausgeführt. Der tatsächliche Registry-Read besitzt daher keine stabile Vorher-/Nachher-Bindung an beispielsweise:

```text
(dev, inode, size, mtime_ns, ctime_ns)
```

Der Registry-Lock ist advisory. Ein nicht kooperierender Writer kann deshalb:

1. die widerrufene produktive Registry kurzfristig durch die alte, zum Receipt passende Registry ersetzen;
2. genau diese stale Bytes durch `_strict_json_load()` lesen lassen;
3. vor der späteren Pfad-/Hardlink-Prüfung wieder die widerrufene Registry herstellen;
4. die Source-Publish-Revalidation mit dem bereits geparsten stale Objekt bestehen lassen.

Der Lock bleibt zwar bis nach dem Catalog-Commit gehalten, verhindert diesen Angriff aber nicht, weil die Sicherheitsentscheidung nicht an den unter Lock gelesenen Datei-Handle beziehungsweise eine stabile Dateiidentität gebunden ist. Damit bleibt ein Gegenbeispiel zum behaupteten Schutz gegen stale-copy/revocation und Registry-TOCTOU bestehen.

Die bestehenden Tests prüfen Hardlinks und normalen Registry-Drift, aber keinen tatsächlich ausgeführten Registry-Swap während `SourceRegistry.load()`:

- `tests/test_source_registry_atomicity.py:82-122`
- `tests/test_source_data_draft_import.py:202-230`
- Die wirksamen Swap-Tests betreffen nur Stage und Index: `tests/test_f5b_review_findings.py:664-718,1220-1260`.

**Erforderliche Korrektur:**

- Registry über einen no-follow geöffneten Handle lesen;
- vor und nach dem Read Identität und Linkzahl auf demselben Objekt prüfen;
- exakt die von diesem Handle gelesenen Bytes parsen;
- die Registry-Authority bis nach Catalog-Commit gesperrt und an diese Identität gebunden halten;
- adversarialen Test ergänzen, der den Registry-Swap tatsächlich ausführt und dessen Injektion explizit bestätigt.

Die gleiche Bindung sollte beim Key-Read ergänzt werden: `_stage_hmac_key()` prüft den Keypfad vor `read_bytes()`, bindet den Read aber ebenfalls nicht über eine stabile Vorher-/Nachher-Identität (`core/source_data_promotion.py:1354-1392`).

---

### P1-2 – Komponierbare Low-Level-Persistenzumgehung bleibt im Modul verfügbar

**Evidenz:**

- `core/admin_catalog/store.py:984-1063`
- `core/admin_catalog/store.py:1091-1109`
- `core/admin_catalog/store.py:378-386`
- `tests/test_admin_catalog_service.py:328-332`
- `tests/test_f5b_review_findings.py:1053-1070`
- Freeze-Trust-Claim: `docs/status/2026-07-15-feedback-f-F5-B-technical-freeze-v6.md:55-57`

Das Modul exponiert weiterhin zwei direkt komponierbare Primitives:

```python
_write_connection(db_path)
_insert_revision(connection, context, revision_id, entries, ...)
```

`_write_connection()` liefert eine schreibbare SQLite-Connection. `_insert_revision()` schreibt und finalisiert eine Revision, erzwingt aber selbst weder:

- `_begin_attested_write()`,
- `_require_no_source_identity_bypass()`,
- Receipt-/Registry-Revalidation,
- Profile-/Managed-Retention,
- noch die vollständige finale Publish-Policy.

Ein interner Caller kann beide Helfer importieren und direkt kombinieren. Dafür ist weder eigener `sqlite3.connect()`-Code noch beliebiger Dateizugriff erforderlich. Dass die Namen mit Unterstrichen beginnen, bildet keine Capability- oder Trust-Grenze. Die Tests demonstrieren sogar, dass `_write_connection` außerhalb des Store-Moduls importiert und verwendet wird.

Dies ist ein direkter Low-Level-Bypass der behaupteten finalen Persistenzboundary. Der Ausschluss „beliebiger direkter sqlite3-Zugriff durch vollständig feindlichen Code“ deckt diese konkrete Komposition nicht hinreichend ab: Der Bypass verwendet bereitgestellte Catalog-Implementierungsprimitives.

**Erforderliche Korrektur:**

- keine schreibbare Connection außerhalb einer authority-owning finalen Boundary bereitstellen;
- `_insert_revision()` entweder strukturell unerreichbar machen oder darin selbst Schemaattestierung und sämtliche finalen Policies erzwingen;
- adversarialer Regressionstest: `_write_connection + _insert_revision` tatsächlich komponieren und nachweisen, dass kein receiptloses Source-Laundering und kein Schema-/Retention-Bypass möglich ist.

---

### P1-3 – Provenance-Schutz klassifiziert Base-Revision-Einträge fälschlich als source-importierte Identitäten

**Evidenz:**

- `core/source_data_promotion.py:286-304`
- `core/source_data_promotion.py:306-352`
- `core/admin_catalog/store.py:835-859`
- `core/admin_catalog/store.py:1943-1949`
- `core/admin_catalog/store.py:2106-2111`
- `tests/test_f5b_review_findings.py:384-419`
- `tests/test_source_data_draft_import.py:300-373`

Bei einem Source-Import mit `base_revision_id` wird der Draft als vollständiger Snapshot aufgebaut:

```python
entries = (*base_entries, *(item.entry for item in normalization.normalized))
```

`_require_no_source_identity_bypass()` lädt später jedoch das komplette `payload_json` jedes receipt-gebundenen Drafts und schützt ausnahmslos die normalisierten IDs **aller** enthaltenen Einträge:

```python
protected_source_ids = {
    normalize_catalog_id(entry.entry_id)
    for row in source_payload_rows
    for entry in _entries_from_payload_json(...)
}
```

Dadurch werden auch bereits vor dem Source-Import existierende Base-Revision-Einträge zu angeblich source-importierten Identitäten. Nach einem solchen Import können Generic Publish und Direct Revision diese legitimen Base-IDs nicht mehr übernehmen, selbst wenn sie unverändert aus einer vorherigen manuellen Revision stammen.

Das schützt nicht nur „durch den Source-Import eingeführte Identitäten“, sondern vergiftet den gesamten übernommenen Basissnapshot dauerhaft für receiptlose Revisionen. Das ist ein erheblicher Verfügbarkeits- und Workflowfehler der Catalog-Persistenzpolitik.

Die vorhandenen Base-Tests prüfen Receipt-Hash-/Identitätsbindung und erfolgreichen Relation-Import, nicht einen anschließenden legitimen Generic Publish mit unveränderten Base-Einträgen.

**Erforderliche Korrektur:**

- Receipt beziehungsweise separate persistierte Provenance-Metadaten müssen die tatsächlich durch Normalisierung eingeführten typisierten Identitäten binden;
- `_require_no_source_identity_bypass()` darf nur diese eingeführte Menge schützen, nicht den vollständigen Basissnapshot;
- Vergleich weiterhin im normalisierten Typ-plus-ID-Domain und casefold-sicher durchführen;
- Regressionstest: Source-Import über bestehender Base-Revision, danach legitimer Generic Publish mit unveränderten Base-IDs und ohne die source-eingeführten IDs.

---

### P3-1 – Aktiver Plan ist gegenüber dem existierenden Review-Pending-Freeze statusveraltet

**Evidenz:**

- `.hermes/plans/2026-07-13-feedback-f-admin-catalog-repositories.md:315`
- `.hermes/plans/2026-07-13-feedback-f-admin-catalog-repositories.md:613-624`
- `docs/status/2026-07-15-feedback-f-F5-B-technical-freeze-v6.md:7`
- `docs/status/2026-07-15-feedback-f-F5-B-technical-freeze-v6.md:66`

Der aktive Plan behauptet in Zeile 315 weiterhin:

> „Freeze v6 wird vorbereitet.“

Der Freeze existiert jedoch bereits und ist ausdrücklich:

> `TECHNICAL FREEZE V6 / REVIEW PENDING / NO-GO`

Der spätere Planabschnitt beschreibt zwar korrekt die formale Prüfung, doch der Zwischenstand ist intern statusveraltet. Damit ist der Freeze-Claim einer vollständig synchronisierten Plan-/Freeze-Evidenz nicht ohne Einschränkung erfüllt.

**Erforderliche Korrektur:**

Den Zwischenstand auf „Freeze v6 erzeugt / Review pending / NO-GO“ aktualisieren und nach jeder Änderung einen neuen Freeze erstellen; Freeze v6 darf nicht nachträglich verändert werden.

---

## 4. Adversariale Prüfergebnisse ohne eigenes Finding

Statisch nachvollzogen und ohne weiteres separates P0–P3-Finding:

- `pending → committed` einschließlich DB-Commitfehler und post-commit/pre-index-finalize-Reconciliation;
- Cross-DB- und Cross-Draft-Reservierung;
- reale Zwei-Thread-`os.link`-Injektion im Parallel-Key-Test;
- ausgeführter `os.replace`-Index-Swap mit Injektionszähler;
- Stage-/Index-Single-Link- und Identitätsprüfung;
- Live-Registry-Lockdauer bis nach Catalog-Commit — jedoch mit dem unter P1-1 beschriebenen ungebundenen Read;
- casefold-sicherer Source-Identity-Abgleich;
- gemeinsame Policy in Direct Revision und receiptlosem Generic Publish — jedoch mit der unter P1-3 beschriebenen zu breiten Schutzmenge;
- `_begin_attested_write()` auf den unterstützten Store-Write-Routen;
- keine automatische Publish-/Activate-/Runtime-/Web-/Engine-/Scan-/Netzwerkverdrahtung;
- Freeze-v4/v5 korrekt als `SUPERSEDED / REQUEST CHANGES / NO-GO` erhalten.

## 5. Schlussfolgerung

Freeze v6 ist vollständig driftfrei, aber nicht approvable. Die Registry-Revalidation bleibt gegenüber einem tatsächlich getimten Authority-Swap verwundbar, die moduleigenen Low-Level-Primitives bilden weiterhin eine komponierbare Persistenzumgehung, und die Source-Identity-Policy sperrt fälschlich sämtliche Base-Revision-Identitäten. Zusätzlich ist der aktive Plan statusveraltet.

**Eindeutiges Verdict: `REQUEST CHANGES`**

## 6. Ausführungs- und Änderungsnachweis

- Keine Tests ausgeführt.
- Kein Server gestartet.
- Kein Netzwerk verwendet.
- Keine Probe-Datenbank und keine temporären Repositorydateien erzeugt.
- Keine Repositorydatei erstellt, verändert oder gelöscht.
- Ausschließlich statische Reads, Git-Metadatenabfragen und SHA-256-Berechnungen durchgeführt.
