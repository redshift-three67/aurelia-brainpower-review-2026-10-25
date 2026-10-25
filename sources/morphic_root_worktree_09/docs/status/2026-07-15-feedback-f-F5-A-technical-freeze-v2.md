# Feedback f – F5-A technischer Freeze v2 für Abschlussreviews

> **SUPERSEDED / REQUEST CHANGES:** Reviewbatch `deleg_0ab4aeb0` war driftfrei, aber nicht
> einstimmig: ein APPROVE und ein P1 REQUEST CHANGES. Der P1 betraf das verbleibende
> Hardlink-TOCTOU-Fenster zwischen Temp-Write/`fsync` und `os.replace`. Freeze v2 ist nur
> historische Evidenz; maßgeblich wird ausschließlich Freeze v3 nach RED→GREEN und neuer Matrix.

**Stand:** 2026-07-15
**Arbeitsverzeichnis:** `C:\morphic_v1\.worktrees\operator-workbench-phase1`
**Branch:** `operator-workbench-phase1`
**HEAD:** `619a1f5485a151816e32732929a6a823839ccb57`
**Gate:** F5-A (F5.5/F5.4/F5.1)
**Status:** technisch erneut verifiziert; formales GO ausdrücklich noch nicht erteilt

## Historische Reviewabgrenzung

Der erste Freeze `docs/status/2026-07-15-feedback-f-F5-A-technical-freeze.md` und der
Reviewbatch `deleg_9444028c` sind nur historische REQUEST-CHANGES-Evidenz. Der Batch meldete zwei
P1 und drei P2. Alle fünf Befunde wurden danach per RED→GREEN geschlossen:

1. Ledger-Hardlink-Aliase werden über die kanonische Authorityprüfung vor sowie innerhalb des Locks
   und unmittelbar vor dem Replace abgewiesen.
2. Bestehende Source-Policy-/Typfelder sind bei Manifestreplacement immutable; neue Source-IDs
   starten ausschließlich deaktiviert mit typgebundener Lizenz, `experimental_unverified` und
   `reference_only`; dieselbe Policy wird am finalen Import erneut geprüft.
3. Immutable Stagingdateinamen verwenden die zeitunabhängige `batch_identity_sha256`; `staged_at`
   bleibt im vollständigen Artefakthash gebunden.
4. Die Ist-Analyse ist als Vor-F5-A-Baseline markiert und nennt die aktuellen Schließungsnachweise.
5. Die Testmatrix nennt das aktuelle v3-Consistency-Ledger.

Nur ein neuer, auf diesen Freeze v2 gebundener Doppelreview kann gatewirksam werden.

## Technische Matrix

```text
Fokus: 112 passed, 1 skipped in 1.69s
Admin: 435 passed, 6 skipped in 18.73s
Breit: 919 passed, 8 skipped, exakt 14 bekannte Baselinefehler in 161.22s
Top-5: 1 passed in 106.73s
Ruff: PASS
py_compile: PASS
git diff --check: PASS; nur bekannte LF->CRLF-Hinweise ausserhalb des F5-A-Scopes
```

Die 14 breiten Fehler sind ausschließlich der datumsabhängige Consent-Test und 13 bekannte
HTTP-429-/Rate-Limit-Tests. Keine neue Regression wurde beobachtet.

## Aktueller technischer Vertrag

- primärer CLI-Befehl: `sources data-record-consistency`;
- Ledger-Schema: `morphic_source_data_consistency_ledger`, Version 3;
- Ledgerliste `entries`, Zeitfeld `recorded_at`;
- `sources data-promote` bleibt nur sichtbar deprecateter No-Publish-Alias;
- alte Promotion-Ledger v1/v2 werden fail-closed abgewiesen;
- stabile Duplicate-Staging-Identität ist unabhängig von `staged_at`;
- Registry- und Ledgerauthorities weisen Hardlink-Aliase fail-closed ab;
- bestehende `source_type`/`license`/`trust_level`/`import_policy` sind bei Manifestreplacement
  server-owned und immutable;
- neue Sources sind ausschließlich deaktiviertes Least-Privilege-Onboarding;
- finaler Import revalidiert die Policy auch gegen intern konsistent neu gehashte Stage-Artefakte;
- F5.3 plant getrennt `data-import-draft`; keine stille Aliasumdeutung;
- im Worktree existieren keine Ledgerartefakte; keine produktive Migration wurde ausgeführt.

## Sicherheits- und Wirkungsgrenzen

- kein Catalog-Draft, Publish oder Activate;
- keine Engine-/Scan-/Runtimewirkung;
- kein Netzwerkzugriff;
- kein lokales Source-Daten-I/O über einen produktiven Consumer;
- Point-in-time-`local_path`-Prüfung; künftiger Consumer muss Handleprüfung und privaten Snapshot
  am Read-Boundary wiederholen;
- Replay nur im intakten aktuellen Ledger, kein externer Tamper-Anker;
- produktive Legacy-v1-Registry bleibt read-only;
- Authorities blieben hashidentisch;
- F5-B bleibt bis zum vollständigen formalen F5-A-GO gesperrt.

## System-/Scope-Nachweis

```text
Git-Statusfingerprint vor Freeze v2:
50c8bc8a972923a43c07254daa2818d3640e7be7fba7d71865aa440b71115b7c

Port 8000: frei
Port 8090: bestehender Listener 127.0.0.1, PID 20404, unangetastet
F5-A-Ledgerdateien im Projekt: 0
Registry-Locksidecars unter config/: 0
```

## SHA-256 des technischen Scopes

```text
153bfd23cb0bd57b61b0ddc5f4d5bd666c9643538c54ddaf4ee666241e5c0277  core/admin_catalog/source_policy.py
37b19ff68bd2ba1de91d806e6dedf76fbea1f1bfeed7c37b92befddcff212e40  core/source_registry.py
3a5dcb77b8e85b73ba912093f27b634dd976aa6d229bb0248f4cf2a7c85f13e0  core/source_data_promotion.py
602b972b80203b3ccbfa9127e3afd0f90ebfe36e4ec4c31abfdea5c5dcc666aa  apps/cli/commands/sources.py
885e0280b21ec040da089060e638a9b7de4c6f3f24b32052e8a95a158f2e0736  tests/test_admin_source_policy.py
16c05e0972266a06115f01f0b847a61e070780eeee78c2333da438fbbf442bf2  tests/test_source_registry_atomicity.py
7cc243b7e9e528b7b970b384c24820303726b481f2b4864c309d9b4ede17b062  tests/test_source_registry.py
944821737a99fa0507a9f05fbd9d04f27d69e2681cc5035bd0bb9c9c3d9267b8  tests/test_source_data_promotion.py
9ade1f0e04472a7d5359e948b5ffcc50fd79b9e93ff57df47fd74711e0c1ad14  tests/test_source_registry_cli.py
3c007c40f1e137024a60a760604cfb12209ec93bcb08b208625db5ba5c5418bd  PROJECT_MEMORY/00_CURRENT_STATE.md
215aade857d2c392202a331e468d9a06d7f2ced6e9f5649b2df247dfdc410965  .hermes/plans/2026-07-13-feedback-f-admin-catalog-repositories.md
b8f859f6d5febc7c59b5421338157dff134e63519f5f008a39941646baab21e2  docs/status/2026-07-13-feedback-f-umsetzungsplan-kurz.md
bcfd08640cbe9808b64212d893f8e7b9916aef30cbd262494536613640ebfb60  docs/status/2026-07-12-gesamtstruktur-fortschritt.md
866e1b5a0bbf0a37f5fff39c8381437621b0159fd66778b4121ac0f003d0ef35  docs/status/2026-07-13-feedback-f-admin-repositories-ist-analyse.md
fc7e5a804104235467c2e35a0c2edc5597234b3cb439ddba8169359dceb02dc9  docs/status/2026-07-15-feedback-f-F5-A-technical-freeze.md
e64d292eb74abe962ce87ff4b83e4195bfd7684c68079c1192b0125ed8f59f70  docs/QUELLEN_REGISTRY_BEWERTUNG_20260628.md
8f75576caae49ca7750540dc9f4f0e7a18e5a7544d30ad0ddb0d9218c1f35645  docs/STABILIZATION_TEST_MATRIX.md
35da3185e47bf1a3e09cfe6024678f7c0058dce382370bbb8db95f7403ca0286  docs/SESSION_HANDOFF_20260628.md
ac808ab421d65a31fab2ffe0921692adf464ed1bab75f243e91864209a5fff57  docs/WORKTREE_INVENTORY_20260629.md
6c93c5a1aab9b022bf22e3a8c8097b07bde2738efec3678645ffadf849e4a0b3  config/source_repositories.json
c67d4e899dab9547a2171ec0d5604d9628721b6757a87d33ef8d34f0c0dadfa0  data/remedies.db
```

Dieser Record bindet die oben gelisteten 21 Dateien. Reviewer müssen zusätzlich diesen Freeze-v2-
Record selbst zu Beginn und Ende hashen. Jede Abweichung oder jedes Finding P0–P3 invalidiert den
Review; einzig ein driftfreies Doppel-APPROVE ohne P0–P3 darf den Dokumentationsblock entsperren.
