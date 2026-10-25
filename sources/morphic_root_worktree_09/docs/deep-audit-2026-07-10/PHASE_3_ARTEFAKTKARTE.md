# Phase 3 – Daten- und Artefaktkarte (Read-only)

**Erstellt:** 2026-07-10
**Methode:** Quellcode-/Pfadanalyse; keine Klientenexporte, Runtime-Inhalte oder Secrets gelesen.

## 1. Datenfluss auf hoher Ebene

```text
Workbench-Formular / Browser-LocalStorage
  → FastAPI Contracts / Scanstart
  → Web-Joblogs + Workbench-Drafts/Traces + Runtime-Manifest
  → CLI-Ausführung
  → Exportwurzel / Resonanz-, Synergy-, Remedies-, Trends-, Deutungsartefakte
  → ReportCatalog / Inline-Vorschau
```

## 2. Artefaktinventar

| Speicherort / Muster | Erzeuger / Codebeleg | Mögliche Datenklassen | Aktuelle Schutz-/Löschlage | Phase-3-Folge |
|---|---|---|---|---|
| `codex_tmp/web-jobs/<scan-id>.stdout.log`, `.stderr.log` | `apps/web/scan_jobs.py:218-240`; Root aus `apps/web/main.py:253-257` | CLI-Argumente, Fokus, potenziell Klienten-/Fehlerdaten | pro Prozess lokal, keine Retention/Erasure-Verknüpfung belegt | in Artefaktindex, tenant-/clientbezogene Löschkaskade |
| `codex_tmp/workbench/draft.json` | `apps/web/workbench_runtime.py:11-66`; Root `apps/web/main.py:258-265` | Formularentwurf, potenziell Klienten-/Fokusdaten | atomisches Schreiben, aber globaler lokaler Store; keine Retention | Datenklassifikation, explizites Löschen/TTL |
| `codex_tmp/workbench/templates.json` | `apps/web/workbench_runtime.py:69-99` | benannte Entwürfe, potenziell personenbezogene Werte | lokale JSON-Datei; Template-Delete vorhanden, keine globale Erasure-Kopplung | Template-Index und clientbezogene Löschung |
| `codex_tmp/workbench/run_traces.json` | `apps/web/workbench_runtime.py:101-143`; Trace-Seeding `apps/web/main.py:148-180,505-513` | Run-ID, Operator-/Tenantkontext, Profil, derzeit auch Review-Klientendaten | lokaler JSON-Store; keine Retention; Trace enthält hohe Sensitivität | PII-Minimierung, Erasure-Index, Zugriffskontrolle |
| `data/runtime/{sessions,artifacts,audit_log}.json` oder `MORPHIC_RUNTIME_DIR` | `core/compliance/runtime_manifest.py:14-27,55-105` | Clientpseudonym, Sitzungen, Artefaktpfade, Auditaktionen | atomische JSON-Speicherung; vorhandene Erasure-/Retention-APIs müssen gegen alle Pfade validiert werden | Vollständigkeits-Dry-run statt blindem Löschen |
| `data/runtime/...` Client-/Manifestreferenzen | `core/compliance/operator_context.py:57,97`; `runtime_manifest.py:198-347` | Operator-/Tenant-/Client-Referenzen und Pfade | teilweise pseudonymisiert; Pfadreferenzen können externe Artefakte erfassen | Artefaktkarte vor Löschaktion vervollständigen |
| Harmonization-Jobzustand / Events | `apps/web/harmonization.py`, `core/realtime/event_log.py:15-50` | Jobparameter, Status, Ereignisse | genauer Defaultpfad/Retention noch separat zu belegen | eigener Job-/Event-Pfad im Erasure-Dry-run |
| Browser `localStorage` Fokus-Historie | `apps/web/static/workbench-state.js:23-46` | bis zu acht Fokuswerte, personenbezogen/gesundheitsnah möglich | stiller Browser-Speicher; kein UI-Opt-in oder Löschknopf belegt | Opt-in, Erklärung, Löschen im UI |
| Tenant-suffixierte Standard-Reportroots | `apps/web/main.py:63-80,270-285` | Berichte und Exporte | Leseseitige Tenant-Suffixierung; allein kein Mehrbenutzer-AuthZ | in Variante A nur lokaler Kontext; Variante B serverseitige Principal-Grenze |
| `C:/Benutzer_Archive_Start__<tenant>` und weitere Reportroots | `apps/web/main.py:63-80`; Scan-Exportauflösung ab `main.py:565-689` | Resonanz-/Synergy-/Remedies-/Trends-/Deutungsberichte, Dateimetadaten | Klarname nicht als Rootname, aber Artefaktinhalt und Unterpfade potenziell sensibel | Artefaktindex, verschleierter Clientslug, Backup-/Erasure-Verifikation |
| CLI-Exportroot / Konfiguration | `config.yaml:1-4`, Launcher-/CLI-Pfade | Exportdateien inkl. HTML/JSON/TXT/PDF | globale Roots, bisher kein zentraler Lifecycle | Repositoryadapter statt globaler Pfaderzwingung |

## 3. Code-Echte Schutzstärken

- `WorkbenchRuntimeStore` und `RuntimeManifestService` schreiben JSON atomisch über temporäre Datei plus Replace.
- Standard-Reportroots erhalten bei gesetztem Tenant-ID-Kontext einen Suffix.
- Reportkatalog arbeitet leseseitig über die aktuelle Tenant-Auflösung.
- Browser- und Server-Workbenchaustausch sind im lokalen Phase-2A-Modus auf Loopback begrenzt.

## 4. Offene Datenschutz-/Lifecycle-Gates

1. Keine nachgewiesene vollständige, clientübergreifende Erasure-Transaktion über Joblogs, Workbench-Drafts/Templates/Traces, Runtime-Manifeste, Harmonizationevents und sämtliche Exporttypen.
2. Browser-Fokus-Historie ist nicht explizit opt-in und besitzt keinen sichtbaren Löschpfad.
3. Run-Traces enthalten im aktuellen Seed Klientendaten; für Diagnostik und Erasure muss Feldminimierung entschieden werden.
4. Backup-/Restore- und Windows-ACL-/Verschlüsselungsnachweis fehlen.
5. `config.yaml` enthält globale Exportroots; neue Pfade benötigen einen serverseitigen Kontextadapter, nicht Browserwerte.

## 5. Nächster Implementierungsschritt

Zuerst einen **nur lesenden Erasure-Dry-run-Planer** für die vorhandenen Runtime-Manifestdaten bauen. Er darf keine Dateien löschen, sondern muss je Client die gefundenen Manifest-/Artefakt-Referenzen, fehlende Pfade und nicht abgedeckte Speicherklassen als Completion-Report ausgeben. Erst nach dessen Testnachweis kann ein bewusster Löschmodus diskutiert werden.
