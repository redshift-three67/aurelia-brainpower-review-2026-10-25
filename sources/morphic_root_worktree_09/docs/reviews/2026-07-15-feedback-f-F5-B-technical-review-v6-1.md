# Review 1 – F5-B Technical Freeze v6

## Verdict

**REQUEST CHANGES**

**Confidence:** HIGH
**Reviewart:** unabhängiges adversariales Security-/Correctness-Review, strikt statisch und read-only
**Befundzählung:** **P0=0, P1=3, P2=0, P3=0**

Freeze und Scope waren während des Reviews stabil. Das Verdict beruht daher nicht auf Scope-Drift, sondern auf drei substantiellen P1-Sicherheits-/Korrektheitsbefunden.

---

## 1. Snapshot- und Hashbindung

| Nachweis | Start | Ende | Ergebnis |
|---|---|---|---|
| Branch | `operator-workbench-phase1` | `operator-workbench-phase1` | stabil |
| HEAD | `619a1f5485a151816e32732929a6a823839ccb57` | identisch | stabil |
| Freeze SHA-256 | `cf3c2a880b9903bbbf65393efe7117a2248a4e23abec3c6fa365bd5cfc218db6` | identisch | entspricht Erwartung |
| Manifestzeilen | exakt 41, eindeutig | exakt 41, eindeutig | korrekt |
| Scope-Dateien | 41/41 = Manifest | 41/41 = Manifest | kein Drift |
| `config/source_repositories.json` | `6c93c5a1aab9b022bf22e3a8c8097b07bde2738efec3678645ffadf849e4a0b3` | identisch | stabil |
| `data/remedies.db` | `c67d4e899dab9547a2171ec0d5604d9628721b6757a87d33ef8d34f0c0dadfa0` | identisch | stabil |
| `config/source_repositories.json.stage-key` | fehlt | fehlt | korrekt |
| Tracked-Status-Fingerprint | `77cf319c0c498a58148b79bccf68343e9b5f7dc0deb859069274a6754d55321c` | identisch | stabil, 37 Zeilen |

**Driftentscheidung:** Kein Scope-, Freeze-, Authority-, Branch- oder HEAD-Drift.
`INVALIDATED BY SCOPE DRIFT` ist daher nicht anzuwenden.

---

## 2. Findings

| ID | Priorität | Befund | Evidenz |
|---|---:|---|---|
| F5B-V6-R1-01 | P1 | Live-Registry-Revalidation besitzt eine ausnutzbare Read-/Identity-TOCTOU-Lücke; ein während des Reads eingeschobener stale Registry-Snapshot kann als Live-Authority akzeptiert werden. | `core/source_registry.py:188-240`, `core/source_registry.py:968-984`, `core/admin_catalog/store.py:1879-1894` |
| F5B-V6-R1-02 | P1 | Der Stage-HMAC-Key wird nach einer punktuellen Pfadprüfung ohne über den Read gebundene Dateiidentität geladen. Ein Key-Swap zwischen Prüfung und `read_bytes()` kann einen fremd signierten Stage-Index autorisieren. | `core/source_data_promotion.py:1049-1056`, `core/source_data_promotion.py:1240-1243`, `core/source_data_promotion.py:1354-1392` |
| F5B-V6-R1-03 | P1 | Eine `pending`-Reservation bindet nur Catalog-Pfad und Draft-ID, nicht den vollständigen Catalog-Kontext. Nach einem pre-commit-Fehler kann derselbe Draft-Name in einem anderen Operator-/Workspace-/Tenant-Kontext die Reservation übernehmen. | `core/admin_catalog/store.py:125-137`, `core/admin_catalog/store.py:1233-1238`, `core/source_data_promotion.py:1075-1087`, `core/source_data_promotion.py:1263-1284` |

---

## 3. Detailbefunde

### F5B-V6-R1-01 – Registry-Read ist nicht identitätsgebunden

**Priorität:** P1
**Confidence:** HIGH

`SourceRegistry.load()` führt folgende Reihenfolge aus:

1. `path.exists()`;
2. `_strict_json_load(registry_path)` liest die Registry über `Path.read_text()`;
3. erst danach konstruiert `SourceRegistry(...)` die Registry und ruft über den Konstruktor `_canonical_registry_path()` auf.

Evidenz:

- `core/source_registry.py:188-193`: Read vor der Konstruktor-/Canonicalization-Grenze;
- `core/source_registry.py:232-240`: Konstruktion und Baseline-Hash erst nach dem Read;
- `core/source_registry.py:968-984`: `_strict_json_load()` verwendet einen ungebundenen pfadbasierten Read;
- `core/admin_catalog/store.py:1879-1894`: Source-Publish hält zwar den Registry-Lock, lädt die Live-Registry aber über genau diese nicht identitätsgebundene Route.

`_canonical_registry_path()` lehnt statische Symlinks, Reparse-Points und Hardlinks ab, bindet jedoch nicht die Dateiidentität der tatsächlich gelesenen Bytes. Ein adversarialer Ablauf ist deshalb möglich:

1. Publish sperrt die Registry-Sidecar-Lockdatei.
2. Ein nicht kooperierender Dateisystemakteur ersetzt die produktive, inzwischen widerrufene Registry unmittelbar vor oder während `_strict_json_load()` durch eine stale aktive Kopie.
3. Die stale Bytes werden gelesen.
4. Vor dem späteren `_canonical_registry_path()` wird wieder eine reguläre Single-Link-Datei am Authority-Pfad eingesetzt.
5. Der Konstruktor akzeptiert die gelesenen stale Bytes; Receipt-Revalidation kann die Revocation umgehen.

Der Sidecar-Lock verhindert nur kooperierende Writer. Er beweist nicht, dass die gelesenen Bytes derselben Dateiidentität entstammen, die vor und nach dem Read geprüft wurde.

Das widerspricht insbesondere:

- Freeze `:48-49`: independently configured Registry und Live-Revalidation;
- Freeze `:52`: Registry-Dateiidentitätswechsel werde an der Authority-Read-Grenze geprüft;
- Freeze `:62`: stale Registry könne produktive Revocation nicht umgehen.

**Erforderliche Korrektur:**

- Registry über einen identitätsgebundenen Read laden:
  - `lstat/fstat` bzw. OS-Handle vor dem Read;
  - Read über denselben Handle;
  - Identität, Linkzahl, Größe sowie relevante Zeit-/Change-Metadaten nach dem Read erneut prüfen;
  - Parsing ausschließlich aus den über diesen Handle gelesenen Bytes.
- Die Prüfung muss innerhalb des bereits gehaltenen Registry-Locks erfolgen.
- RED-Test mit realem `os.replace` exakt während des Registry-Reads; Ergebnis muss nullmutierend und fail-closed sein.

---

### F5B-V6-R1-02 – Stage-Key-Read besitzt dieselbe TOCTOU-Klasse

**Priorität:** P1
**Confidence:** HIGH

`_stage_hmac_key()`:

1. kanonisiert den Keypfad;
2. erzeugt ihn optional;
3. kanonisiert den Pfad erneut;
4. lädt den Schlüssel anschließend separat über `key_path.read_bytes()`.

Evidenz:

- `core/source_data_promotion.py:1357-1364`: Pfad-/Rootprüfung;
- `core/source_data_promotion.py:1365-1384`: exklusive Initialisierung;
- `core/source_data_promotion.py:1385-1389`: punktuelle Canonicalization, danach separater pfadbasierter Read;
- `core/source_data_promotion.py:1049-1056` und `:1240-1243`: genau dieser Key autorisiert Stage-Index-Reads und Transitionen.

Zwischen `_canonical_registry_path(key_path)` und `key_path.read_bytes()` ist ein Dateiwechsel nicht erkennbar. Anders als `_load_stage_authority_json()` besitzt der Key-Read keinen Vorher-/Nachher-Identitätsvergleich.

Ein Angreifer kann daher einen bereits mit seinem Schlüssel signierten Index bereitstellen und den Key im schmalen Fenster nach der Canonicalization austauschen. Die anschließende HMAC-Prüfung validiert dann Angreifer-Key gegen Angreifer-Index. Statische Hardlinktests und die reale Parallel-Key-Initialisierung decken diesen Read-Swap nicht ab.

Das widerspricht Freeze `:52`, wonach auch der Key gegen Dateiidentitätswechsel **an der Authority-Read-Grenze** geschützt sei.

**Erforderliche Korrektur:**

- Key über einen einmal geöffneten, no-follow/single-link-geprüften Handle lesen.
- Vorher-/Nachher-Identität auf demselben Handle prüfen.
- Auf Windows nach Möglichkeit delete-sharing ausschließen oder eine gleichwertige handlegebundene Schutzgrenze verwenden.
- RED-Test: Swap unmittelbar nach erfolgreicher Keypfadprüfung und vor dem Byte-Read; sowohl Stage-Import als auch Indextransition müssen nullmutierend scheitern.

---

### F5B-V6-R1-03 – Pending-Reservation ist nicht kontextvollständig

**Priorität:** P1
**Confidence:** HIGH

Catalog-Draft-IDs sind nicht global, sondern Teil eines zusammengesetzten Schlüssels aus:

- `operator_id`,
- `workspace_id`,
- `tenant_id`,
- `scope`,
- `draft_id`.

Evidenz: `core/admin_catalog/store.py:125-137`.

Der Stage-Index bindet eine Pending-Reservation dagegen nur an:

- `consumer_catalog_path`;
- `consumer_draft_id`.

Evidenz:

- `core/source_data_promotion.py:1075-1087`;
- `core/source_data_promotion.py:1263-1269`.

Bei einem Commitfehler bleibt die Reservation absichtlich `pending`. Ein zweiter Aufruf mit:

- derselben Catalog-Datei,
- derselben textuellen Draft-ID,
- aber einem anderen Operator-/Workspace-/Tenant-/Scope-Kontext

passiert daher die Pending-Kontextprüfung. Wenn im zweiten Kontext noch kein Receipt gespeichert ist, ersetzt `_replace_pending_registered_stage()` den alten Receipt-Hash durch den neu erzeugten Receipt-Hash:

- `core/source_data_promotion.py:1270-1284`.

Der Receipt selbst bindet zwar den vollständigen neuen Kontext (`core/admin_catalog/store.py:1233-1238`), aber diese Prüfung erfolgt erst nach der unvollständigen Reservation-Autorisierung. Sie verhindert nicht, dass eine Reservation aus Kontext A von Kontext B übernommen wird.

Damit ist die Recovery zwar gegen andere Catalog-Pfade und andere Draft-Namen geschützt, nicht aber gegen eine Kollision desselben Draft-Namens über die im Schema ausdrücklich erlaubten Kontextpartitionen. Das kann einen freigegebenen Stage-Batch nach einem transienten Commitfehler in den falschen Tenant-/Workspace-Kontext verschieben.

**Erforderliche Korrektur:**

- Stage-Index-Schema um den vollständigen Consumer-Kontext erweitern oder eine kanonische `consumer_context_sha256` binden.
- Pending-Reconciliation nur erlauben, wenn Catalog-Pfad, Draft-ID und vollständiger Kontext identisch sind.
- RED-Tests für:
  - gleicher Catalog + gleiche Draft-ID + anderer Operator;
  - anderer Workspace;
  - anderer Tenant;
  - anderer Scope;
  - zusätzlich die bereits geforderten Cross-Draft- und Cross-DB-Pending-Fälle.

---

## 4. Prüfung der zwölf Freeze-Punkte

| # | Prüfpunkt | Ergebnis |
|---:|---|---|
| 1 | Caller-selected/stale Registry nach Revocation | **Nicht geschlossen.** Caller-selected anderer Pfad wird korrekt abgewiesen (`store.py:1193-1200`); stale Read-Swap der konfigurierten Live-Authority bleibt durch F5B-V6-R1-01 möglich. |
| 2 | Generic-Draft-Laundering exakt/mutiert/case-variant | Die finalen Store-Boundaries prüfen receiptgebundene Source-IDs kontextweit und normalisiert (`store.py:809-860`, `:1941-1949`, `:2106-2111`). Exakte, mutierte und Case-Varianten sind statisch geschlossen. |
| 3 | Pending/Committed Recovery in beiden Commitfenstern | Commitfehler und post-commit/pre-index-finalize werden in `store.py:1247-1339` reconciliert. Innerhalb identischen Consumer-Kontexts plausibel korrekt; kontextübergreifende Übernahme bleibt offen. |
| 4 | Cross-DB/Cross-Draft Pending-Replay | Andere DB-Pfade und andere Draft-IDs werden in `source_data_promotion.py:1081-1087` bzw. `:1263-1269` abgewiesen. Gleicher Draft-Name in anderem Catalog-Kontext bleibt offen. |
| 5 | Reale Parallel-Key-Injektion | Test verwendet zwei Threads, Barrier am Key-`os.link` und fordert exakt zwei Linkversuche (`tests/test_f5b_review_findings.py:1162-1205`). Initialisierungsrace ist real; Key-Read-Swap ist davon unabhängig offen. |
| 6 | Realer Index-Swap | Reale `os.replace`-Injektion im Readfenster vorhanden (`tests/test_f5b_review_findings.py:1220-1260`); `_load_stage_authority_json()` bindet Identität vor/nach Read (`source_data_promotion.py:958-980`). |
| 7 | Stage/Index/Registry/Key Link-/TOCTOU | Stage und Index besitzen Single-Link- und Read-Identity-Prüfung. Registry und Key erfüllen die behauptete Read-Identity-Grenze nicht: Findings 01 und 02. |
| 8 | Source-Publish Live-Revalidation/Lockdauer | Registry-Lock wird vor Revalidation erworben und erst nach Catalog-Commit geschlossen (`store.py:1870-1904`, `:2040-2054`). Lockdauer korrekt; Registry-Read darunter nicht identitätsgebunden. |
| 9 | Schemaattestierung unterstützter Writes | `_begin_attested_write()` führt `BEGIN IMMEDIATE` und Fingerprintprüfung auf derselben Connection aus (`store.py:378-386`). Draft-, Import-, Update-, Delete-, Validate-, Publish-, Revision-, Activate-/Deactivate-Routen benutzen diese Boundary. Schema v7/Fingerprint stimmen mit `backup.py:14-23` überein. |
| 10 | Direct Revision / Generic Publish | Beide finalen Pfade führen vollständige Snapshotvalidierung und Source-Identity-Policy innerhalb der attestierten Write-Transaktion aus (`store.py:1904-2048`, `:2071-2127`). |
| 11 | Scope-Vollständigkeit | Exakt 41 Dateien; alle 14 `core/admin_catalog/*.py`, CLI, Registry/Promotion, relevante Tests, `tests/test_admin_profile_management.py` sowie Freeze v4/v5 vorhanden und hashgebunden. |
| 12 | Plan-/Freeze-/Baseline-/Trust-Claims | Plan kennzeichnet v4/v5 als superseded und v6 als nächsten Reviewblock (`plan:313-315`); Schema v7 und Stage-Index v3 stimmen. v4/v5 sind eindeutig `SUPERSEDED / REQUEST CHANGES / NO-GO`. Baselinezahlen sind intern konsistent, wurden gemäß Reviewverbot nicht neu ausgeführt. Trust-Ausschluss für beliebigen direkten SQLite-/Dateizugriff ist dokumentiert, hebt die ausdrücklich behaupteten Authority-Read-/TOCTOU-Verträge aber nicht auf. |

---

## 5. Unterstützte Persistenzpfade

Statisch verfolgt wurden:

- Catalog-Initialisierung;
- Draft create/update/delete;
- spezialisierte Profile-/Remedy-/Multiplex-Tombstonepfade;
- Draft-Validation-Marker;
- Stage→Draft+Receipt-Import;
- generischer Draft-Publish;
- dedizierter Source-Publish;
- Direct Revision;
- Activate/Deactivate/Rollback mit Auditereignis;
- Registry save/import/rollback;
- Stage-Artefakt-, Stage-Index- und Stage-Key-Publikation;
- Consistency-Ledger;
- Catalog Backup/Restore.

Es wurde keine schreibbare Store-Connection als öffentliche Storemethode gefunden. Source-Publish ist außerhalb der Tests nur über den expliziten Wrapper definiert; automatisches Runtime-, Web-, Engine-, Scan- oder Netzwerk-Wiring wurde nicht gefunden.

---

## 6. Severity-Zählung

| Severity | Anzahl |
|---|---:|
| P0 | 0 |
| P1 | 3 |
| P2 | 0 |
| P3 | 0 |

Da bereits ein P0–P3-Befund gemäß Freeze-Regel zwingend `REQUEST CHANGES` auslöst, ist ein Approval unzulässig.

---

## 7. Endgültiges Verdict

# **REQUEST CHANGES**

Freeze v6 ist driftfrei und reproduzierbar gebunden, erfüllt aber wegen der drei P1-Befunde nicht die Freigabeschwelle `P0=P1=P2=P3=0`.

Empfohlene nächste Schritte:

1. Registry-Read handle- und identitätsgebunden machen.
2. Stage-Key-Read handle- und identitätsgebunden machen.
3. Pending-Consumer-Identität um den vollständigen Catalog-Kontext erweitern.
4. Für alle drei Root-Causes gezielte RED→GREEN-Mikrogates ergänzen.
5. Vollständige Verifikationsmatrix erneut ausführen und anschließend einen neuen Freeze v7 erzeugen.

## Ausführungsnachweis

- Keine Tests ausgeführt.
- Kein Server gestartet.
- Kein Netzwerkzugriff.
- Keine Dateien erstellt, verändert oder gelöscht.
- Keine Temp-/Probe-Dateien erzeugt.
- Keine produktive Authority außer per rein lesendem SHA-256-Zugriff geöffnet.
