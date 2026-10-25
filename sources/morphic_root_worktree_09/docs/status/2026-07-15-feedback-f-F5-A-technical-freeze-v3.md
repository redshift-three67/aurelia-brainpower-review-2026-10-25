# Feedback f – F5-A technischer Freeze v3 für Abschlussreviews

**Stand:** 2026-07-15
**Arbeitsverzeichnis:** `C:\morphic_v1\.worktrees\operator-workbench-phase1`
**Branch:** `operator-workbench-phase1`
**HEAD:** `619a1f5485a151816e32732929a6a823839ccb57`
**Gate:** F5-A (F5.5/F5.4/F5.1)
**Status:** technisch erneut verifiziert; formales GO ausdrücklich noch nicht erteilt

## Historische Reviewabgrenzung

Die Freeze-/Reviewbatches v1 (`deleg_9444028c`) und v2 (`deleg_0ab4aeb0`) sind nur historische
REQUEST-CHANGES-Evidenz und nicht gatewirksam. v1 meldete zwei P1 und drei P2. v2 war driftfrei,
aber nicht einstimmig: ein APPROVE und ein P1 REQUEST CHANGES.

Der zusätzliche v2-P1 ist per RED→GREEN geschlossen: `_atomic_replace_json()` schreibt und
`fsync`t zuerst die Tempdatei, ruft danach unter dem bereits gehaltenen Authoritylock den
authority-spezifischen Validator auf und führt erst dann `os.replace` aus. Zwei deterministische
Tests injizieren exakt nach Temp-`fsync` einen Hardlink und beweisen, dass Registry-/Ledgerauthority,
Aliasbytes und Temp-Cleanup unverändert bleiben.

Nur ein neuer, auf diesen Freeze v3 gebundener Doppelreview kann gatewirksam werden.

## Technische Matrix

```text
Betroffene Registry-/Ledgerdateien: 94 passed in 1.91s
Fokus: 114 passed, 1 skipped in 2.07s
Admin: 437 passed, 6 skipped in 21.25s
Breit: 921 passed, 8 skipped, exakt 14 bekannte Baselinefehler in 170.46s
Top-5: 1 passed in 98.70s
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
- Registry und Ledger revalidieren Hardlink-Aliase nach Temp-Write/`fsync` unmittelbar vor
  `os.replace`, jeweils unter gehaltenem Authoritylock;
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
Git-Statusfingerprint vor Freeze v3:
883879397ed254defabe1ba4836af8b563b43f3cc377420385d8ca094d099262

Port 8000: frei
Port 8090: bestehender Listener 127.0.0.1, PID 20404, unangetastet
F5-A-Ledgerdateien im Projekt: 0
Registry-Locksidecars unter config/: 0
```

## SHA-256 des technischen Scopes

```text
153bfd23cb0bd57b61b0ddc5f4d5bd666c9643538c54ddaf4ee666241e5c0277  core/admin_catalog/source_policy.py
5ab7116f64c16662e6b2c4eb1497dff690497fe11c66d84be5c653711e8f6793  core/source_registry.py
48126efea2846c8bac0521f6bda64f93bcc71f147002a8895f457ddd5f3a6d06  core/source_data_promotion.py
602b972b80203b3ccbfa9127e3afd0f90ebfe36e4ec4c31abfdea5c5dcc666aa  apps/cli/commands/sources.py
885e0280b21ec040da089060e638a9b7de4c6f3f24b32052e8a95a158f2e0736  tests/test_admin_source_policy.py
a4e4be6b05768bd2bd6c6143cf303f4b25f8baa8fd8e60a3b21868eabf4c507e  tests/test_source_registry_atomicity.py
7cc243b7e9e528b7b970b384c24820303726b481f2b4864c309d9b4ede17b062  tests/test_source_registry.py
de2a73aee053bf2301fb1cb5f6ef47100345009f20a11af1ab63984cfc1901b9  tests/test_source_data_promotion.py
9ade1f0e04472a7d5359e948b5ffcc50fd79b9e93ff57df47fd74711e0c1ad14  tests/test_source_registry_cli.py
40da7e1b43feb94a8fe4e8ecf6c3aa27e5783d2c78459befd0e0baabbe2f64cf  PROJECT_MEMORY/00_CURRENT_STATE.md
215aade857d2c392202a331e468d9a06d7f2ced6e9f5649b2df247dfdc410965  .hermes/plans/2026-07-13-feedback-f-admin-catalog-repositories.md
9c074ef70c5b8467b1c38c62941105e276961ed2a122b2ff8ca74b28bab2b2bd  docs/status/2026-07-13-feedback-f-umsetzungsplan-kurz.md
bcfd08640cbe9808b64212d893f8e7b9916aef30cbd262494536613640ebfb60  docs/status/2026-07-12-gesamtstruktur-fortschritt.md
866e1b5a0bbf0a37f5fff39c8381437621b0159fd66778b4121ac0f003d0ef35  docs/status/2026-07-13-feedback-f-admin-repositories-ist-analyse.md
fc7e5a804104235467c2e35a0c2edc5597234b3cb439ddba8169359dceb02dc9  docs/status/2026-07-15-feedback-f-F5-A-technical-freeze.md
3ffdf46a13b76d401c197b08a08fb519cbd4ec09f2890ec802b623ea1ea9c721  docs/status/2026-07-15-feedback-f-F5-A-technical-freeze-v2.md
e64d292eb74abe962ce87ff4b83e4195bfd7684c68079c1192b0125ed8f59f70  docs/QUELLEN_REGISTRY_BEWERTUNG_20260628.md
6cfd65bf2a62495ed9df665f36efe729ab428ac66f60d168dfab933a13b3902e  docs/STABILIZATION_TEST_MATRIX.md
35da3185e47bf1a3e09cfe6024678f7c0058dce382370bbb8db95f7403ca0286  docs/SESSION_HANDOFF_20260628.md
ac808ab421d65a31fab2ffe0921692adf464ed1bab75f243e91864209a5fff57  docs/WORKTREE_INVENTORY_20260629.md
6c93c5a1aab9b022bf22e3a8c8097b07bde2738efec3678645ffadf849e4a0b3  config/source_repositories.json
c67d4e899dab9547a2171ec0d5604d9628721b6757a87d33ef8d34f0c0dadfa0  data/remedies.db
```

Dieser Record bindet die oben gelisteten 22 Dateien. Reviewer müssen zusätzlich diesen Freeze-v3-
Record selbst zu Beginn und Ende hashen. Jede Abweichung oder jedes Finding P0–P3 invalidiert den
Review; einzig ein driftfreies Doppel-APPROVE ohne P0–P3 darf den Dokumentationsblock entsperren.
