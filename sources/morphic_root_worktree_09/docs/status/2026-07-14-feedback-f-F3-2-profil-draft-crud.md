# Feedback f – F3.2 Profil-Draft-CRUD

- **Stand:** 2026-07-14
- **Gate:** F3.2
- **Status:** GO
- **F3-Fortschritt:** 66,7 %
- **F3-Gesamtstatus:** NO-GO bis F3.3
- **Gesamtfeature Feedback f:** NO-GO

## 1. Scope

F3.2 ergänzt vollständig offline und explizit injiziertes Profil-Draft-CRUD auf dem isolierten Admin-Catalog. Create, Update, Enable, Disable und Delete-as-Tombstone sind versions- und kontextgebunden; publizierte Profile werden nie hart gelöscht. Gruppenreferenzen und Aliase validieren fail-closed. Aktivierung bleibt eine reine Catalog-Metadatenoperation ohne Engine-, Web-, CLI- oder Runtimewirkung.

Nicht Bestandteil von F3.2 sind:

- Runtime- oder Engineumschaltung,
- Web- oder CLI-Integration,
- Online-Repositories oder Netzwerkzugriff,
- produktive Defaultpfade oder Defaultdatenbanken,
- Mutation der Legacy-Profilauthority,
- Beginn von F3.3.

## 2. Implementierte Verträge

- Profil-Create/Update/Enable/Disable/Delete-as-Tombstone mit strikt positiver Integer-CAS-Version.
- Fremde Operator-/Workspace-/Tenant-/Scope-Kontexte werden vor Storezugriff als stabile Domainfehler abgewiesen.
- Profiländerungen verändern ausschließlich den adressierten Draft.
- Tombstones entstehen nur über den dedizierten Löschpfad aus einem persistierten Liveprofil.
- Der Store konstruiert atomar exakt eine Live→Tombstone-Transition; ein generisches öffentliches Autorisierungsflag existiert nicht.
- Tombstone-Autorisierung ist an Kontext, Draft, Profil-ID und exakten Payload-Hash gebunden.
- Publizierte Profile müssen in allen späteren Revisionen erhalten bleiben; Auslassung wird fail-closed blockiert.
- Ein publizierter Tombstone ist draft- und revisionsübergreifend terminal und darf nicht wiederbelebt werden.
- Nur ein exakt hashidentischer terminaler `PROFILE`-Tombstone darf carry-forward geführt werden.
- Kanonische Tombstone-IDs und historische Aliase bleiben symmetrisch reserviert: ID→ID, Alias→ID, ID→Alias und Alias→Alias sind blockiert.
- Caller-kontrollierte Revisionseingaben werden einmalig als unveränderliches Tuple materialisiert und für Policy sowie Insert identisch wiederverwendet.
- Draft-Validierung und Publish bleiben über Version und Payload-Hash gekoppelt.
- Schema v2 enthält die Tombstone-Autorisierungstabelle; Backup-Schema-Version und Fingerprint wurden gemeinsam aktualisiert.
- Keine produktive Verdrahtung außerhalb der isolierten Admin-Catalog-Komponenten.

## 3. TDD- und Reviewverlauf

Initiale und reviewgetriebene RED-Verträge reproduzierten unter anderem:

- Cross-Draft-Auslassung eines publizierten Profils,
- forgebaren Tombstone-Bypass über ein öffentliches Store-Flag,
- Cross-Draft-Wiederbelebung publizierter Tombstones,
- inkonsistentes Fremdkontext-Fehlermapping,
- Low-Level-Revisionen mit Alias-/Canonical-ID-Diebstahl,
- zu breite Carry-forward-Ausnahme für fremde Entry-Typen,
- Übernahme der terminalen Canonical-ID als fremder Alias,
- mutable/stateful-Sequence-TOCTOU zwischen Policy und Insert.

Mehrere hashgebundene Reviews meldeten nacheinander engere Restbefunde. Jeder Befund wurde durch einen spezifischen RED-Vertrag bestätigt, minimal geschlossen, vollständig neu verifiziert und anschließend auf einem neuen Hashsnapshot erneut reviewed.

Finaler hashgebundener Re-Review:

- Delegation: `deleg_7ad76f8c`
- Ergebnis: **APPROVE**
- Konfidenz: **HOCH (0,97)**
- P0: 0
- P1: 0
- P2: 0
- P3: 0

Der Reviewer bestätigte insbesondere die einmalige Immutable-Snapshot-Materialisierung, vollständige symmetrische Tombstone-Namensreservation, exakten Carry-forward, Retention, Cross-Draft-Terminalität, Autorisierungsbindung, Kontextisolation, CAS/TOCTOU-Schutz, Schema-v2-/Backup-Konsistenz und Null-Runtimewirkung.

## 4. Verifikation

- F3.2-Fokus: `34 passed` mit `-W error`.
- Admin-/F3.1-Matrix: `225 passed, 2 skipped` mit `-W error`.
- `py_compile`: PASS.
- Breite Regression ohne Top-5: `705 passed, 4 skipped, 14 failed`.
- Baselinevergleich: exakt `671 + 34 = 705` grüne Tests; dieselben 14 bekannten Baselinefehler.
- Top-5-Smoke: `1 passed`.
- `git diff --check`: PASS; ausschließlich bestehende LF→CRLF-Hinweise in fremden Dateien.
- Temporärer Cross-Draft-Smoke: Live-Publish → Tombstone-Publish → identischer Carry-forward; stale Resurrection blockiert; Cleanup PASS.
- `data/remedies.db` blieb hashidentisch.
- Port 8090 blieb unangetastet; Port 8000 wurde nicht belegt.
- Kein Netzwerkzugriff, kein Commit, kein Push, kein Staging, kein Reset und kein Clean.

Die 14 bekannten breiten Fehler bestehen aus einem datumsgebundenen Consent-Fixture und 13 bereits bekannten gemeinsamen HTTP-429-/Rate-Limiter-Ausreißern. Sie sind gegenüber der dokumentierten Baseline unverändert und außerhalb des F3.2-Scopes.

## 5. Finaler Current-Snapshot

| Datei | SHA-256 |
|---|---|
| `core/admin_catalog/contracts.py` | `5e5af414f4188d60df2b9bc730528add87165695b913affb539fe28c3bd6c7c4` |
| `core/admin_catalog/validation.py` | `bd4ba94581e2101259b4cb69488f55102e8b0b047c7626b3e1f161428445b443` |
| `core/admin_catalog/store.py` | `ea924d38c3240c94098c498c11064b79c80ebc4d2f006d9b616158c4f7b810de` |
| `core/admin_catalog/service.py` | `fb7cdbb3dcf8a7ffa8e524c8097e6f0411c3e1057786a2dafe26a7e26ff2027a` |
| `core/admin_catalog/backup.py` | `a3953953f2f6708d86d6deb5c793d0ae7cf714796b021ea448b96ffa4f5db185` |
| `core/admin_catalog/__init__.py` | `063d8c657509092c58541b8c2c07b11975fb9ed9d2d15e1b91da4c2d93e3d0c3` |
| `tests/test_admin_profile_management.py` | `0000d132ef5662840f47ea4f2506c7d8ef89379a06a4ee2cb2698430fe83e782` |
| `tests/test_admin_catalog_store.py` | `f28e53a016e260f0cf4fbf85de98ab87c8a880983816f5d6811be1a6e060ce2a` |
| `data/remedies.db` | `c67d4e899dab9547a2171ec0d5604d9628721b6757a87d33ef8d34f0c0dadfa0` |

## 6. Post-State-ShadowCopy

```text
E:\mprphic_v1_Backups\morphic_v1_shadowcopy_20260714_103600_feedback_f_F3_2_GO_post
FILES=24 VERIFIED=24
SOURCE_MANIFEST_SHA256=8a8752c95416010f530995c9a78f20e1c992557f368464bb0840be9673f2d71b
FINAL_DOCUMENTATION_SHA256_CHECK=PASS
```

Das Hauptmanifest umfasst die neun Admin-Catalog-Module, neun zugehörigen Admin-/Profiltests, Hauptplan, Kurzplan, Gesamtfortschritt, Golden Record, den F3.1-Gate-Record und den finalen unabhängigen Review. Der nach Eintragung dieser realen Manifestdaten finalisierte F3.2-Gate-Record liegt im selben ShadowCopy-Ordner und ist separat durch `FINAL_DOCUMENTATION.sha256` gebunden und erfolgreich verifiziert. Dadurch entsteht keine selbstreferenzielle Manifestabhängigkeit.

## 7. Gateentscheidung

F3.2 ist **GO**.

F3 bleibt bis F3.3 **NO-GO**. Feedback f, produktiver Admin-Catalog, Online-Repositories und Runtimeumschaltung bleiben weiterhin **NO-GO**.

Nächster zulässiger Block: **F3.3 – Read-only Runtime-Adapter im Schattenmodus**. Default bleibt Legacy; Schattenvergleich darf Diffs sichtbar melden, aber keinen Scan verändern. Eine spätere produktive Catalog-Aktivierung oder Fallbackpolicy ist ausdrücklich nicht freigegeben.
