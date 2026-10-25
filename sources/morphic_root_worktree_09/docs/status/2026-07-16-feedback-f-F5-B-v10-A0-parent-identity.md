# Feedback f: F5-B/v10 Gate A0 Parent-Identity Closure

Stand: 2026-07-16
Worktree: `C:\morphic_v1\.worktrees\operator-workbench-phase1`
Branch: `operator-workbench-phase1`
HEAD: `619a1f5485a151816e32732929a6a823839ccb57`
Gate A0: **TECHNISCH GESCHLOSSEN**
F5-B gesamt: **NO-GO**
Freeze v10: **NOCH NICHT ERSTELLT**

## 1. Entscheidung

Gate A0 aus `docs/developer-current-state-2026-07-16/02_AKTUELLE_PLANUNG_UND_PAUSEPUNKT.md:43-51` ist technisch umgesetzt, fokussiert verifiziert und zweistufig reviewt.

Geschlossen sind Parent-Substitution und Parent-Identity-Transport fuer:

- Source Data Stage;
- Source Manifest Stage;
- Stage-Index-Registrierung;
- Stage-Index-Reservierung und `pending -> committed`;
- Consistency Ledger;
- Rollback Snapshot;
- Stage-Key bei fehlendem und vorhandenem Key.

Diese Entscheidung ist kein F5-B-GO. Schema-v7->v8-Migration, v7-Backupmigration, durable Backup-/Restore-Publikation, POSIX-Entscheidung, produktive Validation-Key-Komposition, Vollregression, Freeze v10 und Abschlussreviews bleiben offen.

## 2. Root Cause

Die Producer hatten einen Parentpfad validiert oder unter einem vertrauenswuerdigen Read-/Lockkontext verwendet, verloren diese Identitaet aber vor dem Commit. `_atomic_replace_json()` und `_atomic_publish_bytes()` banden anschliessend eigenstaendig den aktuell sichtbaren Parent.

Damit konnte ein anderer Namespace zwischen vertrauenswuerdigem Read und Commit als neue Authority akzeptiert werden, obwohl der generische Helper den neu ausgewaehlten Parent waehrend seines eigenen kurzen Commitfensters korrekt stabil hielt.

Die Registry-spezifische Implementierung war bereits staerker: `SourceRegistry.load()` band die Parent-Identitaet, und `SourceRegistry.save()` transportierte sie in den Directory Commit Guard. Gate A0 uebertraegt dieses Capability-Modell auf alle F5-B-Dateiauthorities.

## 3. Implementierte Sicherheitsvertraege

### 3.1 Commitprimitive

`_atomic_replace_json()`, `_atomic_publish_bytes()` und `_atomic_publish_json()` verlangen jetzt eine explizite `expected_parent_identity`.

Die Helper:

- erzeugen keinen Parent mehr nach der Identitaetsbindung;
- reichen die erwartete Identitaet an `_directory_commit_guard()` weiter;
- duerfen keinen aktuell sichtbaren Ersatzparent still als neue Authority auswaehlen;
- behalten bestehende Temp-Inode-, Flush- und Post-Publish-Attestierungslogik bei.

### 3.2 Stage und Stage-Index

Die Source Data Stage bindet die Stage-Parent-Identitaet nach expliziter Verzeichniserzeugung und vor der ersten Publication. Dieselbe Identitaet wird bis zur Stage-Index-Registrierung weitergereicht.

Ein Parentwechsel zwischen erfolgreicher Stage-Publikation und Indexregistrierung wird vor Indexmutation abgewiesen. Die Registrierung bindet ausserdem die Registry-Parent-Identitaet fuer den Stage-Key.

Die Draft-Import-Vorbereitung transportiert zwei getrennte Capabilities:

- `stage_parent_identity` fuer Stage und Stage-Index;
- `registry_parent_identity` fuer Registry und Stage-Key.

Beide Capabilities werden durch alle Admin-Store-Pfade fuer Reservierung, Pending-Reconciliation und Commit weitergereicht.

### 3.3 Stage-Key

Die Stage-Key-Erzeugung und der Stage-Key-Read werden gegen die Parent-Identitaet gebunden, die bereits beim vertrauenswuerdigen Registry-Read erfasst wurde.

Geschlossen sind damit:

- Parentwechsel vor Key-Publication;
- Parentwechsel nach dem Missing-Key-Check;
- Parentwechsel zu einem Namespace mit bereits vorhandenem fremdem 32-Byte-Key;
- Keyverwendung waehrend Stage-Index-Registrierung und Draft-Import-Transitions.

### 3.4 Ledger und Rollback Snapshot

Ledger und Rollback Snapshot reichen die vor dem Commit gebundene Parent-Identitaet an die gemeinsame Commitprimitive weiter. Registry-, Stage-Index- und Ledger-Lockreihenfolge wurde nicht geaendert.

### 3.5 Fail-Closed Retention statt unsicherem Cleanup

Ein erster Review fand, dass eine Identitaetspruefung direkt vor einem separaten pfadbasierten `unlink()` weiterhin ein TOCTOU-Fenster besitzt. Eine zwischenzeitlich eingefuehrte parentgebundene Loeschprimitive war gegen Parentwechsel sicher, band aber nicht die Child-Inode-Identitaet ausreichend fuer das festgelegte starke Angreifermodell.

Die finale minimale Entscheidung lautet deshalb:

- kein automatisches Loeschen eines unregistrierten immutable Stage-Artefakts;
- kein automatisches Loeschen eines uncommitteten immutable Rollback-Snapshots;
- kein automatisches `rmdir()` eines neu angelegten Rollback-Roots;
- Evidenz wird fail-closed behalten;
- ein identisches, valides und noch unregistriertes Stage-Artefakt kann durch erneutes Ausfuehren desselben Stagingbefehls kontrolliert registriert werden;
- ein bereits registriertes Artefakt bleibt Duplicate/Replay und wird nicht erneut registriert.

Damit existiert kein pfadbasierter destruktiver Cleanup gegen einen moeglicherweise ausgetauschten Childnamen.

## 4. TDD-Evidenz

### 4.1 Ausgangsbasis

Vor A0-Aenderungen:

```text
tests/test_source_registry_atomicity.py
tests/test_source_data_promotion.py
68 passed in 3.78s
```

### 4.2 Parent-Identity RED

Die Guardweitergabe wurde fuer eine kontrollierte Regression temporaer in beiden generischen Helpern deaktiviert. Exakt die sieben neuen Authority-Vertraege schlugen fehl:

```text
7 failed in 1.42s
```

Nach Wiederherstellung der Parent-Identity-Weitergabe:

```text
7 passed in 0.97s
```

### 4.3 Reviewgetriebene Cleanup-REDs

Die beiden pfadbasierten Cleanup-Races und der alte automatische Directory-Cleanup wurden reproduziert:

```text
3 failed in 0.91s
```

Eine zwischenzeitliche parentgebundene Loeschung erreichte:

```text
3 passed in 0.46s
```

Nach dem Codequalitaetsreview wurde diese Zwischenloesung bewusst durch evidenzerhaltende Retention ersetzt, weil Parentbindung allein keine Child-Inode-Bindung garantiert.

### 4.4 Weitere Review-REDs

Fuer Stage-Publication->Registration, Existing-Key, Missing-Key, ungebundene Registry und Retry-Semantik wurden weitere gezielte RED-Vertraege beobachtet:

```text
5 failed in 0.75s
3 failed in 0.66s
```

Nach den jeweiligen minimalen Fixes liefen die fokussierten Vertraege gruen.

### 4.5 Finale Nachbarmatrizen

```text
Source Registry/Atomicity/Promotion/Draft/CLI:
120 passed in 6.27s

F5-B Review Findings:
57 passed in 6.93s

Admin Store/Service/Backup/Profile/Remedy:
133 passed, 1 skipped in 13.41s
```

Der Skip ist ein bestehender hostabhaengiger Symlink-/Junction-Fall.

Statische Checks:

- `py_compile`: PASS;
- globales `ruff check`: PASS;
- `git diff --check`: PASS, abgesehen von bekannten LF->CRLF-Hinweisen.

## 5. Reviews

### 5.1 Spezifikationsreview

Erster Befund:

- Cleanup war zwischen Identitaetspruefung und Pfadmutation nicht atomar gebunden;
- mehrere Tests prueften den Zielpfad im displaced Namespace noch nicht explizit.

Nach Schliessung und finaler Retentionentscheidung:

```text
Gate A0 remains COMPLIANT.
No findings.
```

### 5.2 Codequalitaetsreview

Reviewrunden schlossen:

- Stage-Key-Existing-Branch;
- Stage-Publication->Registration-Gap;
- Child-Identity-Risiko bei Cleanup;
- fehlende `pending -> committed`-Abdeckung;
- falsche Replay-Klassifikation normaler Authorityfehler;
- fehlende Recovery fuer retained unregistered Stage-Artefakte;
- Registry-Identity-Pruefung nach statt vor Stage-Root-Erzeugung.

Finales Ergebnis:

```text
APPROVED
No Critical or Important findings.
```

Ein nicht blockierender Minor bleibt dokumentiert: Beim kontrollierten Retry eines retained Stage-Artefakts werden Fehler aus der privaten Registrierung derzeit als Duplicate/Replay klassifiziert. Das Verhalten bleibt fail-closed; eine spaetere praezisere interne Fehlerklasse ist moeglich, aber nicht A0-blockierend.

## 6. Beruehrte Dateien

Produktionsscope:

- `core/source_registry.py`
- `core/source_data_promotion.py`
- `core/admin_catalog/store.py`

Testscope:

- `tests/test_source_registry_atomicity.py`
- `tests/test_source_data_promotion.py`
- `tests/test_f5b_review_findings.py`

Es wurden keine produktive Registry, Remedy-DB, Stage-Key-Datei, Backups oder Runtimeauthorities mutiert.

## 7. Operative Nachweise nach A0

| Pruefung | Ergebnis |
|---|---|
| Registry SHA-256 | `6c93c5a1aab9b022bf22e3a8c8097b07bde2738efec3678645ffadf849e4a0b3` |
| Remedy-DB SHA-256 | `c67d4e899dab9547a2171ec0d5604d9628721b6757a87d33ef8d34f0c0dadfa0` |
| Produktiver Stage-Key | fehlt |
| `MORPHIC_ADMIN_STAGE_KEY` | nicht gesetzt |
| Port 8000 | frei |
| Radi144 | `127.0.0.1:8090`, PID 3304 |

## 8. Naechster verbindlicher Block

Der naechste zulaessige Implementierungsblock ist Gate M1 aus `docs/developer-current-state-2026-07-16/02_AKTUELLE_PLANUNG_UND_PAUSEPUNKT.md:53-60`:

1. historisches ausfuehrbares v7-Schema aus dem letzten validen v7-Scope rekonstruieren;
2. synthetische v7-Known-Answer-Datenbank mit Draft, Revision, Activation, Audit und Source-Receipt erzeugen;
3. exakten v7-Schemafingerprint binden;
4. RED: der heutige Store lehnt die v7-Datenbank kontrolliert und ohne Teilmigration ab;
5. RED: unbekannter Fingerprint und Preview-v8 bleiben fail-closed.

Erst nach M1 folgen:

- M2 atomare v7->v8-Migration;
- M3 v7-Backupmigration;
- B1 durable Backup-/Restore-Publikation;
- P1 POSIX-Entscheidung;
- C1 produktive Validation-Key-Komposition;
- v10-Regression, Freeze und Reviews.

## 9. Unveraenderliche Schranken

- F5-B bleibt `NO-GO`.
- Kein Freeze v10 vor Abschluss aller offenen v10-Bloecke.
- Keine produktive Registry- oder Remedy-DB-Mutation.
- Keinen produktiven Stage-Key erzeugen.
- Kein produktives Backup oder Post-State-ShadowCopy vor den vorgeschriebenen APPROVE-Gates.
- Radi144 auf Port 8090 nicht veraendern.
- Keine CI-, Packaging-, UI- oder Architekturmodernisierung in M1/M2 hineinziehen.
- Kein Commit, Staging oder Push ohne ausdrueckliche Benutzerfreigabe.
