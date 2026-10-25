# Feedback f – F3.1 Legacy-Profilnormalisierung

- **Stand:** 2026-07-14
- **Gate:** F3.1
- **Status:** GO
- **F3-Fortschritt:** 33,3 %
- **F3-Gesamtstatus:** NO-GO bis F3.2 und F3.3
- **Gesamtfeature Feedback f:** NO-GO

## 1. Scope

F3.1 normalisiert die bestehende zentrale Profil-Authority ausschließlich read-only und deterministisch. Der neue Adapter exportiert aktive kanonische Profile, Aliasbeziehungen und Gruppenreferenzen, ohne `MASTER_PROFILES` oder Gruppenquellen zu verändern.

Der duplizierte CLI-Fallback wird separat als nicht autoritative Driftquelle inventarisiert. Seine `_PROFILES_DATA` werden statisch per AST und `ast.literal_eval` gelesen; das CLI-Modul wird dabei nicht importiert oder ausgeführt.

Nicht Bestandteil von F3.1 sind:

- Profil-Draft-CRUD,
- Publish oder Activate,
- Runtime-/Engineumschaltung,
- Web- oder CLI-Integration,
- Netzwerkzugriff,
- Mutation der Legacy-Authority.

## 2. Implementierung

Neu:

- `core/admin_catalog/legacy_profile_adapter.py`
- `tests/test_admin_catalog_legacy_profiles.py`

Verträge:

- 502 aktive Profile vollständig und feldtreu exportiert,
- 5 Aliasbeziehungen erhalten,
- 449 referenzierte Gruppen vollständig aufgelöst,
- kanonisches JSON und SHA-256 wiederholbar byte-stabil,
- keine Mutation von `MASTER_PROFILES`, Registrydatei oder Gruppenquellen,
- CLI-Fallback getrennt und ausdrücklich nicht autoritativ,
- keine produktive Verdrahtung.

## 3. Live-Inventar

| Bestand | Wert |
|---|---:|
| Aktive kanonische Profile | 502 |
| `MASTER_PROFILES`-Schlüssel | 507 |
| Alias-Schlüssel | 5 |
| Referenzierte Gruppen | 449 |
| Verfügbare Gruppen | 450 |
| Unaufgelöste Gruppen | 0 |
| CLI-Fallbackprofile | 15 |
| CLI-Fallback-Gruppenreferenzen | 146 |
| Im Master fehlende Fallbackprofile | 2 |
| Exakt übereinstimmende Fallbackprofile | 1 |
| Driftende Fallbackprofile | 12 |

## 4. TDD- und Reviewverlauf

Initiales RED:

- `ModuleNotFoundError: core.admin_catalog.legacy_profile_adapter`

Erstes GREEN:

- 6 fokussierte Tests bestanden.

Erster hashgebundener Review:

- `REQUEST CHANGES`
- 0 P0, 0 P1, 2 P2, 1 P3
- Implementierung unabhängig als feldtreu bestätigt;
- gefordert wurden vollständiger 502-Profil-Feldvergleich, expliziter Nichtausführungsbeweis und Wiring-Regression.

Geschlossene Reviewpunkte:

- Vollvergleich aller 502 Profile über `name`, `display_name`, `groups`, `category`, `level`, `aliases`, `enabled`;
- temporäre Registry mit Top-Level-Sentinel und `raise` beweist AST-Lesen ohne Ausführung;
- `sys.modules`-Objektidentität bleibt unverändert;
- Architekturtest erlaubt ausschließlich den Testimport.

Finaler hashgebundener Re-Review:

- Delegation: `deleg_878af2f8`
- Ergebnis: **APPROVE**
- Konfidenz: **98 % / HOCH**
- P0: 0
- P1: 0
- P2: 0
- P3: 0

## 5. Verifikation

- Fokus: `9 passed`
- relevante lokale Admin-/Profilmatrix: `194 passed, 2 skipped`
- unabhängige erweiterte Reviewmatrix: `199 passed, 2 skipped`
- `py_compile`: PASS
- breite Regression: `671 passed, 4 skipped, 14 baseline-identische Fehler`
- Top-5-Smoke: erster Lauf mit transient fehlendem Deutungsartefakt; identischer Kontrolllauf `1 passed`
- `git diff --check`: PASS
- Ports 8000 und 8090 unangetastet
- kein Netzwerkzugriff

## 6. Finaler Current-Snapshot

| Datei | SHA-256 |
|---|---|
| `core/admin_catalog/legacy_profile_adapter.py` | `2e6e90d04d53e9fcb6e7231a38099b2d581c2030c63d00f49c24ba30c9e61e31` |
| `tests/test_admin_catalog_legacy_profiles.py` | `6f5c2630b4db1d3ac0eed6db503630b5a759e957a72985e3b84808c57bff8726` |
| `core/profile_sync/__init__.py` | `65b6a54975ed8e7e1e4ba723befe3b17e7e1e8455cd3e4d81bab0185a399224c` |
| `apps/cli/profiles/registry.py` | `52c3a151fca2c8173e69dd78b1edaada9a18ef2f5dfee71991b05eda927df24d` |
| `core/subgroups/procedural_groups.py` | `1c362690f4569fab5ec6bf816be18c5462711a6350a58a22cded162721da1f8c` |
| `data/remedies.db` | `c67d4e899dab9547a2171ec0d5604d9628721b6757a87d33ef8d34f0c0dadfa0` |

## 7. Gateentscheidung

F3.1 ist **GO**.

F3 bleibt bis F3.2 und F3.3 **NO-GO**. Es gibt insbesondere weiterhin keine produktive Runtimewirkung und keine Freigabe für Profil-Publish, Engineumschaltung oder Online-Repositories.

Nächster zulässiger Block: **F3.2 – Profil-Draft-CRUD** mit Gruppenreferenzvalidierung, Alias-Konflikten fail-closed, Tombstones statt Hard-Delete publizierter Einträge und weiterhin ohne Enginewirkung.
