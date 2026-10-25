# E5.10E – streng lokale Gruppen-Produktivintegration

**Stand:** 2026-07-13
**Branch:** `operator-workbench-phase1`
**Entscheidung:** **E5.10E Backend-/Workerintegration technisch GO; E5.10 insgesamt weiterhin NO-GO**

## Ergebnis

E5.10E verbindet einen explizit ausgewählten, consent-verifizierten lokalen Gruppenentwurf mit dem produktiven lokalen Top-N-/Multiplex-Analysepfad. Rohidentitäten, Mitgliedslisten, Raten und Zentroide überschreiten keine Prozessgrenze. Die Aktivierung wird ausschließlich über DPAPI-geschützte One-Time-Handles und nicht persistierte Prozess-Environment-Overrides transportiert.

## Datenfluss

```text
Phase1ScanRequest.group_draft_id
  → serverseitig abgeleitete stabile subject_id
  → DPAPI-Gruppendraft
  → DPAPI-Identity-Store + aktueller Einzelconsent
  → Resolver + Autorisierung + explizite Policy-Stärke
  → Root-Handle
  → privates Job-Environment
  → Top-N konsumiert Root-Handle einmal
  → frischer Child-Handle pro Multiplex-Subprozess
  → Field-Worker konsumiert Child-Handle einmal
  → AnalysisService.encode_profile(group_opt_in=...)
```

## Sicherheitsverträge

| Vertrag | Ergebnis |
|---|---:|
| Kill-Switch default false | ✅ |
| fehlende/Null-Stärke ohne Wirkung und ohne Storezugriff | ✅ |
| Request enthält nur `group_draft_id`, keine Rohwerte | ✅ |
| Subject-ID wird serverseitig aus Scanidentität abgeleitet | ✅ |
| Draft-/Mitglieds-/Einzelconsent vor Prozessstart geprüft | ✅ |
| Owner-/Workspace-/Tenant-Bindung | ✅ |
| Root-Handle One-Time | ✅ |
| eigener Child-Handle je Screening-/Detailprozess | ✅ |
| Child-Handle One-Time | ✅ |
| Handle niemals CLI-Argument | ✅ |
| Handle/Storepfad niemals Job-Snapshot/Response/Run-Trace | ✅ |
| keine Gruppenwerte in Report/Trace/Manifest | ✅ |
| aktivierter ungültiger Handlepfad fail-closed | ✅ |
| Default-Web-/CLI-Scan kompatibel | ✅ |
| Geo weiterhin unverdrahtet | ✅ |

## Zentrale Dateien

Neu:

- `core/compliance/group_activation_runtime.py`
- `apps/web/group_analysis_runtime.py`
- `tests/test_group_activation_runtime.py`
- `tests/test_field_group_activation_runtime.py`
- `tests/test_topn_group_activation_fanout.py`
- `tests/test_scan_job_private_environment.py`
- `tests/test_web_group_productive_activation.py`
- `.hermes/plans/2026-07-13-e510e-local-productive-group-integration.md`

Geändert:

- `apps/web/contracts.py`
- `apps/web/main.py`
- `apps/web/scan_jobs.py`
- `apps/cli/commands/scan.py`
- `apps/cli/commands/field.py`
- `tests/test_group_e510_release_gate.py`
- `tests/test_group_vector.py`

## TDD-Nachweis

| Block | RED | GREEN |
|---|---:|---:|
| Runtime-Environment/One-Time-Consume | fehlendes Modul, 4 Fehler | `5 passed` |
| Field-Worker-In-Memory-Opt-in | fehlender Helper/Verdrahtung, 3 Fehler | grün im 11-/13-Test-Fokus |
| Top-N-Child-Handle-Fan-out | fehlende Helper/Verdrahtung, 3 Fehler | grün im 11-/13-Test-Fokus |
| privates ScanJob-Environment | unbekannter `env_overrides`-Parameter | `2 passed` |
| Web-Aktivierungsvorbereitung | fehlendes Modul/Feld, 4 Fehler | `5 passed` |
| reale Webroute→privates Job-Environment | Environment blieb `None` | grün |

## Verifikation

| Prüfung | Ergebnis |
|---|---:|
| E5.10E-/Web-/Release-Fokus | `59 passed` |
| erweiterter neuer Integrationsfokus | `13 passed` |
| Rest-Suite ohne Top-5 | `470 passed, 2 skipped`; 8 bekannte Rate-Limit-429-Ausreißer und zunächst 1 bewusst zu evolvierender alter Boundary-Test |
| alter Boundary-Test nach E5.10E-Evolution | `1 passed` |
| alle 8 Rate-Limit-Ausreißer separat/frisch | jeweils `1 passed` |
| Top-5-Smoke | `1 passed in 152.25s` |
| Python-Compile | bestanden |
| JavaScript-Syntax | bestanden |
| `git diff --check` | bestanden; nur bestehende LF→CRLF-Hinweise |

## Bewusst noch nicht freigegeben

- keine reale Browser-End-to-End-Abnahme der produktiven Gruppenwirkung;
- keine UI-Abnahme für explizite Draft-Auswahl und Aktivierungsstatus;
- keine finale Privacy-/Audit-Abnahme über einen real gestarteten aktivierten Top-N-Run;
- keine kombinierte Gruppe+Geo-Wirkung;
- keine Aussage, dass `OperatorContext` echte Authentifizierung sei.

## Nächste Freigabegrenze: E5.10F

E5.10F muss die explizite Browserverdrahtung, positive synthetische Wirkung, Kill-Switch-/Stärke-0-/Widerruf-/Ablauf-/Erasure-Rollbacks, Redaction der realen Job-/Reportartefakte und die vollständige Browser-/Gesamtfreigabe nachweisen.

**Finale Entscheidung:** `E5.10A–E technisch GO`, `E5.10 insgesamt weiterhin NO-GO`, `Geo separat NO-GO`.