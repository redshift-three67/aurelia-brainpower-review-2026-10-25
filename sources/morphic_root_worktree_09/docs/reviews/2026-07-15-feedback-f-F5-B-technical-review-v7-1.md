# Technisches Review 1 – F5-B Technical Freeze v7

## Verdict

**REQUEST CHANGES**

**Konfidenz:** HOCH
**Reviewart:** unabhängig, adversarial, statisch, read-only
**Gebundener Snapshot:** F5-B Technical Freeze v7
**Finding-Zählung:** `P0=0, P1=1, P2=0, P3=0`

Nach der für dieses Gate verbindlichen Regel verhindert das substantielle P1-Finding ein `APPROVE`.

---

## 1. Snapshot- und Drift-Nachweis

| Nachweis | Start | Unmittelbar vor Verdict | Ergebnis |
|---|---|---|---|
| Freeze-v7-SHA-256 | `d2bb3ffd7811e0991b076599952a14ce8ca37d5d1053fb9d8f342cf3bec2da38` | identisch | PASS |
| Manifestdateien | exakt 44, 44 eindeutige Pfade | exakt 44, 44 eindeutige Pfade | PASS |
| Scope-Hashes | `44/44` entsprechen dem Manifest | `44/44` entsprechen dem Manifest | PASS |
| `config/source_repositories.json` | `6c93c5a1aab9b022bf22e3a8c8097b07bde2738efec3678645ffadf849e4a0b3` | identisch | PASS |
| `data/remedies.db` | `c67d4e899dab9547a2171ec0d5604d9628721b6757a87d33ef8d34f0c0dadfa0` | identisch | PASS |
| Produktiver Stage-Key `config/source_repositories.json.stage-key` | fehlt | fehlt | PASS |
| `MORPHIC_ADMIN_STAGE_KEY` | nicht gesetzt | nicht gesetzt | PASS |
| Branch | `operator-workbench-phase1` | identisch | PASS |
| HEAD | `619a1f5485a151816e32732929a6a823839ccb57` | identisch | PASS |
| Working-Tree-Zeilen am Ende | – | `347` | entspricht Freeze-Präflight |
| End-Status-SHA-256 | – | `ab784aef702bc1f66aa8b72eb408110b3e8cafb4a0ad9d7ded9a0467e3143df0` | dokumentiert |

Es trat **keine Scope- oder Freeze-Drift** auf. Das Review ist daher nicht durch Scope Drift invalidiert.

---

## 2. Finding-Matrix

| Priorität | Finding | Primäre Belege |
|---|---|---|
| **P1** | Die Registry- und Stage-Key-Authority wird bereits während der Pfadauflösung auf einen fremden Swap-Target umgebunden. Die späteren Handle-/Metadatenprüfungen attestieren nur diesen fremden Zielpfad, nicht mehr den ursprünglich erwarteten Authority-Pfad. | `core/source_registry.py:1186-1220`, `core/source_registry.py:980-1016`, `core/source_registry.py:1019-1051`, `core/source_data_promotion.py:1392-1429`, `core/admin_catalog/store.py:1185-1192` |

---

## 3. Detailfinding

### P1 – Authority-Substitution im Canonicalization-Fenster bleibt möglich

#### Betroffene Stellen

- `core/source_registry.py:1186-1220`
- `core/source_registry.py:980-1016`
- `core/source_registry.py:1019-1051`
- `core/source_data_promotion.py:1392-1429`
- `core/admin_catalog/store.py:1185-1192`

#### Reale Ursache

`_canonical_registry_path()` prüft zunächst die Komponenten des erwarteten Pfads mittels `os.lstat()`:

```python
# core/source_registry.py:1186-1203
absolute = Path(os.path.abspath(path.expanduser()))
components = list(reversed(absolute.parents)) + [absolute]
for component in components:
    attributes = os.lstat(component)
    ...
    if component.is_symlink() or ...:
        raise SourceRegistryError(...)
```

Danach wird derselbe Name separat aufgelöst:

```python
# core/source_registry.py:1204-1209
resolved = absolute.resolve(strict=absolute.exists())
```

Es fehlt sowohl:

1. eine no-follow-/reparse-resistente Öffnung des **ursprünglich erwarteten** Pfads,
2. als auch eine Prüfung, dass `resolved` weiterhin dieselbe Authority bezeichnet wie `absolute`.

Ein advisory-lock-ignorierender lokaler Writer kann den Authority-Namen nach dem erfolgreichen `lstat()` und vor `resolve()` kurzzeitig durch einen Symlink beziehungsweise Windows-Reparse-Point ersetzen. `resolve()` folgt dann dem fremden Ziel. Die Funktion gibt anschließend den fremden Zielpfad als vermeintlich kanonische Authority zurück.

#### Warum die neuen Handle-Prüfungen das nicht schließen

`_strict_json_load()` ruft zuerst den fehlerhaften Canonicalizer auf:

```python
# core/source_registry.py:980-983
canonical = _canonical_registry_path(path)
initial = os.stat(canonical, follow_symlinks=False)
with canonical.open("rb") as handle:
```

Auch `_read_registry_authority_bytes()` tut dies:

```python
# core/source_registry.py:1019-1024
canonical = _canonical_registry_path(path)
initial = os.stat(canonical, follow_symlinks=False)
with canonical.open("rb") as handle:
```

Die nachfolgenden Vergleiche von Device, Inode, Größe, Linkzahl sowie Zeitmetadaten (`core/source_registry.py:997-1015` und `1032-1050`) prüfen nur noch den bereits aufgelösten fremden Zielpfad. Der ursprünglich angefragte Registry-/Key-Name wird nach dem Read nicht erneut identitätsgebunden geprüft.

Damit erkennen die neuen Checks einen Austausch **während des Reads des bereits gewählten Targets**, aber keinen Austausch **während der Auswahl dieses Targets**.

#### Stage-Key-Callgraph

Der produktive Pfad lautet:

1. `_stage_hmac_key()` berechnet den erwarteten Key-Namen.
2. Der Name wird durch `_canonical_registry_path()` in einen Pfad umgewandelt.
3. `_read_registry_authority_bytes()` kanonisiert diesen Pfad erneut und liest dessen Bytes.

Beleg:

```python
# core/source_data_promotion.py:1392-1425
key_path = _canonical_registry_path(
    registry_path.with_name(f"{registry_path.name}.stage-key")
)
...
key = _read_registry_authority_bytes(key_path)
```

Wenn die erste Canonicalization auf einen fremden Zielpfad umgebunden wird, liest die zweite Funktion bereits diesen fremden Pfad. Die spätere Prüfung kann den ursprünglichen erwarteten `*.stage-key`-Namen nicht mehr rekonstruieren.

Ein fremder 32-Byte-Key wird anschließend allein aufgrund seiner Länge akzeptiert:

```python
# core/source_data_promotion.py:1427-1429
if len(key) != 32:
    raise SourceDataPromotionError(...)
return key
```

Mit diesem Key kann ein Angreifer einen syntaktisch und kryptographisch gültigen Stage-Index für seine eigenen Artefakte erzeugen.

#### Registry-Authority-Callgraph

Der Store soll nur die unabhängig konfigurierte Default-Registry akzeptieren:

```python
# core/admin_catalog/store.py:1185-1192
configured_registry_path = _canonical_registry_path(
    Path(DEFAULT_SOURCE_REGISTRY_PATH)
)
provided_registry_path = _canonical_registry_path(Path(registry.path))
if provided_registry_path != configured_registry_path:
    raise CatalogStoreError(...)
```

Da beide Vergleiche lediglich Strings der potenziell umgebundenen `resolve()`-Ergebnisse vergleichen, ist dies keine unabhängige Handle- oder Dateiidentitätsprüfung. Werden beide Canonicalization-Aufrufe im jeweiligen Fenster auf dasselbe fremde Ziel umgebunden, sind die Ergebnisse gleich und die fremde Registry passiert die Authority-Prüfung.

Der Source-Draft-/Receipt-Pfad kann diese fremde Registry anschließend als Authority persistieren. Dadurch werden Registry-Revalidation, Receipt-Bindung und Stage-HMAC zwar intern konsistent, aber an die falsche Authority gebunden.

#### Sicherheitsauswirkung

Ein lokaler Writer mit Race-Zugriff auf die Authority-Verzeichnisse kann potenziell:

- eine fremde Registry als konfigurierte Registry erscheinen lassen,
- einen fremden Stage-HMAC-Key als produktiven Key einführen,
- einen selbst signierten Stage-Index akzeptabel machen,
- Source-Drafts und Receipts an die substituierte Authority binden,
- die beabsichtigte unabhängige Default-Registry-Vertrauensgrenze umgehen.

Das erfordert lokalen konkurrierenden Dateisystemzugriff und ist deshalb als **P1**, nicht als P0, eingestuft.

#### Erforderliche Korrektur

Die Authority muss anhand des ursprünglich erwarteten Pfadnamens geöffnet und gelesen werden, ohne vorher durch ein verfolgbares `Path.resolve()` das Trust-Objekt zu wechseln:

1. Öffnen über einen no-follow-/reparse-resistenten Handle.
   - POSIX: mindestens `O_NOFOLLOW`, reguläre Datei und Linkzahl prüfen.
   - Windows: geeignete `CreateFile`-Flags beziehungsweise reparse-resistente Handle-Öffnung und passende Share-Mode-Beschränkung.
2. `lstat` des exakten ursprünglichen Pfadnamens mit `fstat` des Handles vergleichen.
3. Registry/Key vollständig über genau diesen Handle lesen; Registry über dieselben Bytes parsen.
4. Vor und nach dem Read Handle-Identität und relevante Metadaten vergleichen.
5. Nach dem Schließen den **ursprünglichen Authority-Namen**, nicht nur einen zuvor aufgelösten Zielpfad, erneut prüfen.
6. Im Store die bereitgestellte Authority gegen die unabhängig konfigurierte Authority über ihre verifizierte Handle-/Dateiidentität binden, nicht durch Gleichheit zweier `resolve()`-Strings.
7. Einen adversarialen Regressionstest ergänzen, der den Swap ausdrücklich zwischen `lstat` und Pfadauflösung/Handle-Open injiziert und über einen Counter beweist, dass das Zielfenster erreicht wurde.

---

## 4. Ergebnisse der sechs adversarialen Prüfbereiche

| Prüfbereich | Ergebnis |
|---|---|
| 1. Registry- und Stage-Key-Reads | **Nicht geschlossen:** P1 im Canonicalization-/Authority-Selection-Fenster. Die Parse-/Read-Fenster selbst besitzen zusätzliche Identitätschecks, diese beginnen jedoch erst nach der potenziell falschen Target-Auswahl. |
| 2. Stage-Index v4, HMAC und Pending-Kontext | Kein weiteres substantiiertes Finding. `consumer_context_sha256` bindet Operator, Workspace, Tenant und Scope; Precheck, Reserve, Replace, Commit und Retry verwenden dieselbe Kontextdomäne. |
| 3. Persistenz-API und finale Transaktion | Kein weiteres substantiiertes Finding. `_revision_insert_plan()` ist rein; Publish und Direct Revision führen Policyprüfung und Writes nach `BEGIN IMMEDIATE` plus Schemaattestierung auf derselben Connection aus. Ein roher `_insert_revision`-Writer existiert nicht. |
| 4. Source-Provenance | Kein weiteres substantiiertes Finding. Schutzidentitäten werden als `(EntryType, normalized ID)` berechnet; explizite Base-Identitäten werden ausgenommen. Snapshotvalidierung verhindert gleichzeitig kollidierende Source-Neueinträge über dieselbe normalisierte ID. |
| 5. Siblingpfade, Rollback, Isolation, Immutable Revisionen, Replay und Nullmutation | Kein weiteres eigenständiges Finding. Stage-Recovery behält Pending/Committed-Zustände kontextgebunden; Source-Drafts sind nach Receipt-Bindung unveränderlich; Revisionen werden transaktional finalisiert und durch Schema-Trigger geschützt. |
| 6. Plan-/Freeze-Claims und Scope | Freeze-SHA, 44-Dateien-Manifest, Authorities, Branch und HEAD sind korrekt gebunden. Die behauptete Registry-/Key-Authority-Closure ist wegen des P1-Findings materiell nicht erfüllt. |

---

## 5. Read-only-Nachweis

Während dieses Reviews wurden:

- keine Tests ausgeführt,
- kein Python-Modul aus dem Repository importiert oder produktiv ausgeführt,
- kein Server gestartet,
- keine Ports oder produktiven Prozesse verändert,
- keine Netzwerkzugriffe ausgeführt,
- keine Datenbank geöffnet oder erzeugt,
- keine Repositorydatei erstellt, geändert oder gelöscht,
- keine produktive Authority und kein Stage-Key verändert oder erzeugt.

Verwendet wurden ausschließlich statische Dateiinspektion, Inhaltssuche, Git-Metadatenabfragen und SHA-256-Berechnungen.

**Repository-Dateien erstellt/geändert:** keine.

Hinweis zur Ausführungsumgebung: Ein übergroßes `read_file`-Toolresultat wurde vom Hermes-Runtime automatisch außerhalb des Repositorys in dessen internem Cache persistiert. Dies war keine Repositorymutation und wurde nicht als Reviewartefakt verwendet oder verändert.

---

## 6. Schlussfolgerung

Freeze v7 ist driftfrei und formal korrekt bytegebunden. Die beabsichtigte Security-Closure für Registry- und Stage-Key-TOCTOU ist jedoch unvollständig: Die Implementierung bindet den Read-Handle erst **nachdem** der erwartete Authority-Name in einem ungeprüften `lstat()`→`resolve()`-Fenster auf ein fremdes Ziel umgebunden werden kann.

## Endgültiges Verdict

**REQUEST CHANGES — `P0=0, P1=1, P2=0, P3=0`**

Freeze v7 darf nach der festgelegten Gate-Regel nicht freigegeben werden. Das Finding benötigt einen neuen adversarialen RED→GREEN-Mikrogate und anschließend einen neu bytegebundenen Technical Freeze.