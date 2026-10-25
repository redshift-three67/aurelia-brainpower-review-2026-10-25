# E5.10A – gehärteter lokaler Client-Identity-Store

**Stand:** 2026-07-12
**Branch:** `operator-workbench-phase1`
**Entscheidung:** **E5.10A technisch GO; E5.10 insgesamt weiterhin NO-GO**

## Ergebnis

E5.10A ersetzt die für Gruppenraten zulässige Identitätsquelle durch einen separaten, lokalen und mit Windows-DPAPI geschützten Store. Der bestehende Klartext-Store `clients.json` bleibt aus Rückwärtskompatibilitätsgründen unverändert, ist aber keine Resolverquelle mehr und wird nicht automatisch migriert.

| Vertrag | Ergebnis |
|---|---:|
| Identitätsklartext nur im entschlüsselten internen Record | ✅ |
| `<client_id>.dpapi` mit kanonischer pseudonymer ID | ✅ |
| keine Klartext-Indexdatei | ✅ |
| explizite Registrierung; keine Legacy-Migration | ✅ |
| Owner-/Workspace-/Tenant-Bindung fail-closed | ✅ |
| Consent standardmäßig deaktiviert | ✅ |
| redigierte Safe-Liste ohne Identität, Tenant oder Pfad | ✅ |
| beschädigte DPAPI-Daten fail-closed | ✅ |
| Pfad-/ID-Manipulation abgewiesen | ✅ |
| atomarer Schreibpfad mit Temp-Bereinigung bei Fehler | ✅ |
| per Record gespeicherte Retention | ✅ |
| Dry-Run und Purge verwaister Identity-Records | ✅ |
| Runtime-Erasure und -Retention können den Store explizit einbeziehen | ✅ |
| Gruppenresolver ohne `RuntimeManifestService`-Fallback | ✅ |
| produktive Scan-/CLI-/Job-/Reportverdrahtung | absichtlich nicht vorhanden |

## Zentrale Dateien

- `core/compliance/local_client_identity_store.py`
- `core/compliance/group_member_identity_source.py`
- `core/compliance/runtime_manifest.py`
- `tests/test_local_client_identity_store.py`
- `tests/test_group_member_identity_source.py`
- `tests/test_group_member_resolution_activation.py`
- `tests/test_group_member_consent_revocation.py`
- `tests/test_group_e510_release_gate.py`

## Sicherheitsgrenzen

1. `LocalClientIdentitySource` liest ausschließlich aus `LocalClientIdentityStore`.
2. `RuntimeManifestGroupMemberIdentitySource` wurde entfernt.
3. Ein nur in `clients.json` vorhandener Legacy-Client bleibt unauflösbar.
4. Weder Registrierung noch Consent sind über Webscan, CLI oder Worker erreichbar.
5. Der Store führt keine automatische Migration, kein Auto-Enrollment und keine implizite Einwilligung aus.
6. Windows-ACL-Härtung persistenter Runtime-Verzeichnisse bleibt ein separates Infrastruktur-Gate; E5.10A verwendet current-user-gebundene DPAPI-Verschlüsselung.

## Verifikation

| Prüfung | Ergebnis |
|---|---:|
| E5.10A-/Resolver-/Erasure-/Release-Fokus | `36 passed` |
| Rest-Suite ohne Top-5 | `432 passed, 2 skipped`; bekannter Rate-Limit-429-Ausreißer |
| Rate-Limit-Test isoliert | `1 passed` |
| Top-5-Smoke separat | `1 passed in 151.65s` |
| Python-Compile | bestanden |
| JavaScript-Syntax | bestanden |
| `git diff --check` | bestanden; nur bestehende LF→CRLF-Hinweise |

## Freigabegrenze

E5.10A ist technisch abgeschlossen. Dies ist **keine Freigabe produktiver Gruppenwirkung**.

Weiterhin offen:

1. E5.10B – reale, dedizierte Consent-Enrollment-/Widerruf-UI und API;
2. E5.10C – default-false Kill-Switch und explizite Gruppenstärke;
3. E5.10D – kurzlebiger serverseitiger Activation Handle ohne Rohidentitäten oder Raten in CLI-/Jobpayloads;
4. E5.10E/F – produktive lokale Integration, Rollback-, Datenschutz- und Browserabnahme.

**Finale Entscheidung:** `E5.10A GO`, `E5.10 weiterhin NO-GO`, `Geo weiterhin separat NO-GO`.
