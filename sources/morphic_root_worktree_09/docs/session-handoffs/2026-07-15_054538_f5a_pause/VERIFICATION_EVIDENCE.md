# Verifikationsevidenz zum F5-A-Pause-Handoff

**Zeitpunkt der Zustandsaufnahme:** 2026-07-15 05:45 lokaler Hostzeit
**Arbeitsverzeichnis:** `C:\morphic_v1\.worktrees\operator-workbench-phase1`

## Repository

```text
Branch: operator-workbench-phase1
HEAD: 619a1f5485a151816e32732929a6a823839ccb57
Gesamter dirty/untracked Status: 321 Einträge
```

Es wurde kein Commit, Push, Staging, Reset oder Clean ausgeführt.

## Letzte ausgeführte Tests

```text
F5-A-Fokus:
103 passed, 1 skipped in 1.67s

Adminmatrix:
426 passed, 6 skipped in 18.10s

Breite Suite:
910 passed, 8 skipped, 14 failed in 146.31s
```

Die 14 Fehler entsprachen exakt der bekannten Baseline:

- `tests/test_group_member_consent_revocation.py::test_expired_group_consent_fails_closed_without_mutating_client`;
- 13 bestehende HTTP-429-/Rate-Limit-Fehler in Web-Shell-/Workbench-Tests.

## Statische Nachweise

```text
ruff check: PASS
py_compile: PASS
git diff --check: PASS
```

`git diff --check` gab ausschließlich bekannte LF→CRLF-Hinweise in fremden/außerhalb des F5-A-Scopes liegenden Dateien aus.

## Top-5

Letzter ausgeführter Lauf vor dem abschließenden bool-sicheren `record_count`-Patch:

```text
1 passed in 94.87s
```

Dieser Nachweis ist nicht der finale Post-Patch-Nachweis und muss nach den noch offenen P2-Patches erneut ausgeführt werden.

## Relevante aktuelle SHA-256

```text
153bfd23cb0bd57b61b0ddc5f4d5bd666c9643538c54ddaf4ee666241e5c0277  core/admin_catalog/source_policy.py
966da7ce452b6098ded161ed58893e86de9cf3e6b7704c1ae2ed2edccd5c3ca9  core/source_registry.py
f5c5df42a34de38b18a578c2dea243dc155bb7b344c94dd7ac8ff94447ea1f7e  core/source_data_promotion.py
b8bcf4ef95f1772dc44ecdd19a1058ad3a4890f81d3dfa65e590458294272000  apps/cli/commands/sources.py
885e0280b21ec040da089060e638a9b7de4c6f3f24b32052e8a95a158f2e0736  tests/test_admin_source_policy.py
57b31994ec6b47fa92cb42b0d915142edae8e52cf7f7b86d97fa40ad30b5b532  tests/test_source_registry_atomicity.py
ca036b9a33c9b721c6561024ce26b261787f28531dcf9ef1a9bebfce16636c22  tests/test_source_registry.py
5948a46a226f383d2eb0527f01df641079d52b42dc0ee32d7b345406e1584722  tests/test_source_data_promotion.py
90ef165b7ed80d5edaba8486964b0148906149165a429a19df92f766c9df3e4c  tests/test_source_registry_cli.py
a8aa9ed292c47979ba89373bb4a1f9c7379fe08e645fc2ca50422a05e443c8a1  PROJECT_MEMORY/00_CURRENT_STATE.md
265f7c1412fb46f2a6d46bb1e7629dfc3c72c8ceb1550a0c36d908650acd14f4  docs/QUELLEN_REGISTRY_BEWERTUNG_20260628.md
457d0a4c8755558fc4a546bc161b74bf3d4bc99cab4538faebe321f4e9c8b91e  docs/WORKTREE_INVENTORY_20260629.md
bcfd08640cbe9808b64212d893f8e7b9916aef30cbd262494536613640ebfb60  docs/status/2026-07-12-gesamtstruktur-fortschritt.md
23a2cbe4463da88724ba7912aeae661acc2b48e2d9a0d4f27c5f70af71fa4183  docs/status/2026-07-13-feedback-f-umsetzungsplan-kurz.md
9a1ade069158d7a889a6762ab55260a7606e3336d7a8a84ad638fa7fedf3261a  .hermes/plans/2026-07-13-feedback-f-admin-catalog-repositories.md
6c93c5a1aab9b022bf22e3a8c8097b07bde2738efec3678645ffadf849e4a0b3  config/source_repositories.json
c67d4e899dab9547a2171ec0d5604d9628721b6757a87d33ef8d34f0c0dadfa0  data/remedies.db
```

Diese Hashliste ist eine Pause-Evidenz, kein finaler F5-A-Freeze: Zwei P2-Patches und anschließende Neuverifikation stehen noch aus.

## Backup

```text
Pre-State:
E:\mprphic_v1_Backups\morphic_v1_shadowcopy_20260714_224422_feedback_f_F5_A_pre

Rückverifikation:
verified=12/12 bad=[]
```

Der konkrete SHA-256 des Pre-State-Manifests war im erhaltenen Toolauszug nicht vorhanden und wurde nicht erfunden.

## Reviewstatus

- alle älteren Security-/Data-PREreviews: wegen Drift oder Folgepatches invalidiert;
- jüngster Securityteil `deleg_11f0ea26`: durch Testdrift invalidiert;
- jüngster Data-/CLI-/Docs-Teil `deleg_11f0ea26`: driftfrei, `REQUEST CHANGES`, zwei P2;
- keine zwei gültigen finalen APPROVE-Reviews vorhanden.

## Sessionexport

Die aktive Session `20260715_054525_14f636` wurde über den kanonischen Hermes-Befehl mit eingebauter Secret-Redaktion exportiert:

```text
hermes sessions export <ziel> --format md \
  --session-id 20260715_054525_14f636 \
  --redact --lineage logical --yes
```

Ergebnis zum Exportzeitpunkt:

```text
Exported 1 session (167 messages)
```

Der Export befindet sich unter `session-export/` innerhalb dieses Handoffordners. Da die Session beim Export noch aktiv war, wird der Endzustand durch `SESSION_HANDOFF.md` und `NEXT_SESSION_PROMPT.md` ergänzt.
