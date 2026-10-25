# Feedback f: F5-B/v10 Gate M1 v7 Known-Answer Closure

Stand: 2026-07-16
Worktree: `C:\morphic_v1\.worktrees\operator-workbench-phase1`
Branch: `operator-workbench-phase1`
HEAD: `619a1f5485a151816e32732929a6a823839ccb57`
Gate M1: **TECHNISCH GESCHLOSSEN**
F5-B gesamt: **NO-GO**

## 1. Entscheidung

Gate M1 aus `docs/developer-current-state-2026-07-16/02_AKTUELLE_PLANUNG_UND_PAUSEPUNKT.md:53-60` ist geschlossen.

Erreicht wurden:

- Rekonstruktion des letzten ausfuehrbaren v7-Schemas aus Freeze-v8-Evidenz;
- exakte Bindung des historischen v7-Schemafingerprints;
- synthetische, aber intern konsistente Known-Answer-v7-Datenbank;
- Draft, Source Receipt, Revision, Activation und Audit Event in der Fixture;
- kontrollierte, byteunveraenderte Ablehnung der v7-DB durch den aktuellen v8-Store;
- kontrollierte, byteunveraenderte Ablehnung einer unbekannten Schemaform;
- kontrollierte, byteunveraenderte Ablehnung einer explizit nicht historischen Preview-v8-Form.

M1 implementiert keine Migration. F5-B bleibt `NO-GO`.

## 2. Historische Authority

Der letzte repositoryseitig identifizierte, ausfuehrbare v7-Scope ist Technical Freeze v8 vom 15.07.2026. Er war nicht freigegeben, ist aber die letzte belastbare v7-Schemaquelle.

Der exakte v7-Fingerprint lautet:

```text
e8bcf21ff2317c82e8fd142abf46b6ca9ac1169c7738767c2553ede06e6e0d21
```

Belege:

- direkte Fingerprintberechnung im hashgebundenen Sessionexport;
- Freeze v5, v6 und v7;
- Freeze-v8-Store- und Backup-Identitaeten;
- Freeze-v9-Nachweis der Schemaaenderung von v7 auf v8.

Die vollstaendige Evidenzkette ist in `docs/developer-current-state-2026-07-16/02_AKTUELLE_PLANUNG_UND_PAUSEPUNKT.md` und den Freeze-/Sessionunterlagen dokumentiert.

## 3. Fixture-Vertrag

Die neue testseitige Fixture liegt unter:

```text
tests/admin_catalog_v7_fixture.py
```

Sie importiert weder `CatalogStore` noch die aktuelle Produktionsschema-Konstante. Die v7-DDL ist unabhaengig eingebettet und entspricht der aktuellen `_SCHEMA` ohne ausschliesslich die spaeteren v8-Validation-Attestation-Objekte.

Die Fixture erzeugt deterministisch:

- einen Context;
- einen gueltigen Group Entry mit kanonischem Payload;
- einen Draft mit kanonischem Snapshot und Hash;
- einen Source Receipt mit kanonischem Receipt-Hash;
- eine finalisierte Revision mit aus den persistierten Bestandteilen berechnetem Bundlehash;
- eine Revision Entry mit kanonischem Entry-Hash;
- eine Activation;
- ein hashverkettetes Audit Event.

Der Verifier prueft:

- den exakten v7-Schemafingerprint;
- `PRAGMA foreign_key_check`;
- kanonische Draft-, Entry-, Revision-, Receipt- und Audit-Hashes;
- Revision-Source-Draft-Felder;
- Activation-Identitaet und Version.

Damit ist die Known-Answer-DB nicht nur strukturell, sondern auch intern konsistent.

## 4. Preview-v8-Grenze

Die exakte DDL und der vollstaendige Fingerprint der fruehen Freeze-v9-v8-Form sind im Repository nicht erhalten. Diese Form wird deshalb nicht frei erfunden oder als historische Authority ausgegeben.

Die Fixture erzeugt nur eine klar als synthetisch und nicht autoritativ markierte Preview-v8-Attestationform. Sie prueft die erforderliche Fail-Closed-Eigenschaft: Der aktuelle Store akzeptiert keine nur teilweise bekannte oder nicht exakt gebundene Schemaform.

Der aktuelle HMAC-v8-Fingerprint bleibt die alleinige v8-Authority:

```text
3dde32b404989c89c392a272c086d09b8b9ac2cb7e2f61372b6d5f41fa5385c5
```

## 5. TDD- und Verifikationsnachweise

### RED

1. Die neue M1-Testdatei importierte absichtlich die noch fehlende v7-Fixture:

```text
ModuleNotFoundError: No module named 'tests.admin_catalog_v7_fixture'
```

2. Die nachfolgende Preview-/Unknown-Erweiterung schlug bis zur Bereitstellung der zwei Fixturemutatoren mit einem gezielten ImportError fehl.

3. Der Revision-Bundle-Driftvertrag entfernte testseitig die drei `source_draft_*`-Felder und umging nur fuer diesen Verifier-Test die Schemafingerprintpruefung. Vor der Verifierergaenzung wurde kein AssertionError ausgeloest.

### GREEN

```text
tests/test_admin_catalog_v7_migration_contract.py
5 passed in 0.61s

M1 + Admin Store + Backup + Service + Profile + Remedy
138 passed, 1 skipped in 14.99s
```

Der Skip ist ein bestehender hostabhaengiger Symlink-/Junction-Fall.

Zusaetzlich:

- `py_compile`: PASS;
- `ruff check`: PASS;
- `git diff --check`: PASS, abgesehen von bekannten LF->CRLF-Hinweisen in vorbestehenden WIP-Dateien.

## 6. Reviews

Spezifikationsreview:

```text
COMPLIANT
No P0-P3 findings.
```

Codequalitaetsreview:

- zuerst P1 fuer Platzhalterhashes und P2 fuer ungeschuetzte Fingerprint-Cleanup-Grenze;
- danach P2 fuer unvollstaendige Revision-Bundle-Verifikation;
- finale Runde: `APPROVED`, keine Befunde im M1-Zweifilescope.

## 7. Beruehrte Dateien

- `tests/admin_catalog_v7_fixture.py`
- `tests/test_admin_catalog_v7_migration_contract.py`

Produktive Store-, Backup-, Registry-, Stage- oder Runtime-Dateien wurden in M1 nicht veraendert. Es wurden keine produktiven Datenbanken, Backups, Keys oder Authorities erzeugt oder mutiert.

## 8. Naechster verbindlicher Block

Gate M2 aus `docs/developer-current-state-2026-07-16/02_AKTUELLE_PLANUNG_UND_PAUSEPUNKT.md:61-69`:

1. dedizierte v7->v8-Migration-API;
2. `BEGIN IMMEDIATE`, v7-Vorbedingung und Schema-Attestation auf derselben Connection;
3. Attestationtabelle und Trigger anlegen;
4. alte Draftvalidierungsmarker invalidieren;
5. externe Neuvalidierung verlangen;
6. Foreign-Key-, Integrity- und exakten aktuellen v8-Fingerprint vor Commit pruefen;
7. Fault-Injection vor/nach DDL und vor Commit;
8. vollstaendiges v7 oder vollstaendiges v8, nie Mischschema;
9. idempotenter Start auf vollstaendigem aktuellen v8; unbekannte Zustaende bleiben fail-closed.

M3, B1, P1 und C1 bleiben nachgelagert.
