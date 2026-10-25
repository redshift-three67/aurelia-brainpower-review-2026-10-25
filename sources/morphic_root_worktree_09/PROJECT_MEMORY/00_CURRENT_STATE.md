# MORPHIC ENGINE V1 - AKTUELLER ZUSTAND (Worktree: operator-workbench-phase1, Branch: report-ux-polish)

**Letztes Update:** 2026-08-06
**Session:** Gate 5 Task 8 - Zwischencheckpoint vor finaler Vollsuite, Reviews und SHA-Freeze.
**Status:**
- Gate 4 Primary Workflow / Report UX: **ACCEPTED**.
- Exakte Report-Session-Autoritaet ist vom Top-N-Orchestrator bis Katalog/Preview ownergebunden und
  nutzt produktiv die kanonische ID `S_TOP{N}_SESSION`.
- Katalog oberhalb der vollbreiten Preview; Desktop horizontal/lokal scrollbar, Mobil vertikal;
  Roving Focus klemmt an Endpunkten, persistiert den Fokusanker und aktiviert keine Preview.
- Spec-Review `APPROVE`, `P0=P1=P2=P3=0`; Quality/Security `APPROVE`, `P0=P1=P2=P3=0`.
- Immutable Evidence: `docs/status/2026-07-31-gate4-primary-workflow-report-ux-acceptance.md`
  (`092c5a17e3ee279ad41a5ae528800e7487d13cb78fe9af892c3e2cf5293df4c9`).
- Gate 5 Tasks 1-7: implementiert und final taskweise APPROVE-reviewed. Task 6 schliesst Monitor-
  Quellenwahrheit, Invalid-No-Gauge, gemeinsame Hardwarestatus-Normalisierung und WCAG-Kontrast ein.
- Whole-Gate Auth-Haertung: Generation-Snapshot bis Response-Body/WS-Send, atomare Sessionausgabe,
  Mutation-Kompensation und gelockte Key-Beobachtung implementiert; Fokus `368 passed`, Spec-Fix-
  und Security-Re-Review APPROVE.
- Whole-Gate Quality-Haertung: Session-Same-Origin, revisionsgebundene CAS-Kompensation, ambige
  Timeout-Fences und strikte/beschraenkte Probe-Truth implementiert. Integriert `595 passed`,
  Backend `429`, Profil `116`, Timeout Node `54` plus Browser `2`; Whole-Gate Quality APPROVE
  `P0=P1=P2=0`.
- Gate 5 ist **NICHT ACCEPTED**: volle Python-Suite und volle Browsermatrix nach dem Markerfix,
  globale Doppelreviews, Manifest, Freeze und Acceptance-Status fehlen noch.
**Letzte Gate-5-Verifikation:** Fokus `408 passed in 39.86s`; fokussierter Browser `1 passed in
7.8s`; Erklaer-/Task-5/6/UI-Matrix `126 passed in 10.35s`. Erste Vollsuite vor Markerfix:
`1 failed, 3221 passed, 17 skipped, 9 warnings in 481.46s`; einziger Fehler danach gezielt behoben.
**Betrieb:** Kein Webserver aktiv. Worktree-Branch ist `report-ux-polish`.
**Wiederherstellung:** `PROJECT_MEMORY/2026-08-06-gate5-session-checkpoint.md`; Prompt fuer neue
Session: `PROJECT_MEMORY/2026-08-06-gate5-new-session-prompt.md`; WIP-Driftmanifest:
`PROJECT_MEMORY/2026-08-06-gate5-wip-source.sha256` (kein Acceptance-Freeze).
**Naechster Schritt:** volle Python-Suite auf den finalen Quality-Bytes, danach volle Browsermatrix,
globale Gate-5-Doppelreviews
und SHA-Freeze. Kein
Gate 6 oder Hardware-/Remote-WebSocket-/Quantum-/Cloud-Gate vor Gate-5-Acceptance.

## KILO-STABILITAETSPROTOKOLL (VERBINDLICH AB 2026-07-31)

- Integrierte `grep`-/`glob`-Toolaufrufe duerfen in diesem grossen kumulativen Worktree nicht mehr in
  `multi_tool_use.parallel` laufen. Ein Grep-Completion-Haenger blockierte am 2026-07-31 von
  11:10 bis zum manuellen Abbruch um 18:07, obwohl `rg` selbst in Sekunden fertig war.
- Inhaltssuchen bis zu einem Upstream-Fix nur mit gezieltem `rg` ueber das Shell-Tool und hartem
  Timeout (typisch 30-120 Sekunden). Dateiinhalte weiterhin mit `Read`, Aenderungen mit
  `apply_patch`; keine breiten ungebremsten Such- oder Diff-Ausgaben.
- Beleg: OpenCode-Issue `anomalyco/opencode#22139` beschreibt denselben intermittierenden Fehler:
  Grep/Edit ist fertig, aber das Tool-Completion-Signal kehrt nicht zurueck. Dokumentierter
  Grep-Workaround: `rg` ueber Bash/Shell.
- Kilo CLI `7.4.17` ist aktuell; `kilo config check` ist sauber. Auto-Pruning funktioniert laut Log.
  Bei langen Meilensteinen trotzdem `/compact` verwenden und den Kilo-Prozess kontrolliert neu
  starten, wenn er laenger als 12 Stunden lebt oder deutlich ueber 2 GiB Private Memory waechst.
- Nie zwei alte Kilo-Hauptprozesse parallel behalten. Vor langen Python-/Browsermatrizen RAM,
  Testprozesse und Ports pruefen; Tests seriell ausfuehren.
- Der zweite Haenger war kein Projekt-, Test- oder RAM-Fehler: keine neuen Windows-Events 2004,
  rund 5,7 GiB RAM und 6,0 GiB virtueller Speicher waren frei. Der erste historische Haenger hatte
  dagegen nachweislich zusaetzlichen virtuellen Speichermangel durch zwei Kilo-Prozesse.
- Kilo-Sitzungen dieses Projekts/der Worktrees sind ueber `/sessions` beziehungsweise `Ctrl+X`, dann
  `L` wieder oeffenbar; `/timeline` springt zu Nachrichten, `/copy-session` exportiert den Verlauf.
  Vor Pausen, langen Matrizen und Reviewdispatches diesen Golden Record mit Branch, HEAD, Dirty-Scope,
  letztem Ergebnis und exakt naechstem Schritt aktualisieren. Die lokale Session-Historie ist nur
  Komfortschicht: nicht persistierte Crash-Eingaben oder Sitzungen anderer Projektfamilien koennen fehlen.

## GATE 4 ACCEPTANCE (FREIGEGEBEN 2026-08-06)

- Nutzerfreigegebene Spezifikation:
  `docs/superpowers/specs/2026-07-31-gate4-primary-workflow-report-ux-design.md`.
- Vollstaendiger TDD-Implementierungsplan:
  `docs/superpowers/plans/2026-07-31-gate4-primary-workflow-report-ux.md`.
- Ausfuehrungsmodus war subagent-gesteuert und seriell; Implementierung, Spec-Review und
  Qualitaetsreview wurden getrennt ausgefuehrt.
- Verbindliche UI-Entscheidungen: Radi144 nur als visuelle/sequentielle Referenz; beide
  Systemmodell-Links aus der primaeren Workbench entfernen; Katalog oberhalb der vollbreiten
  Preview; Kontext je Reportkarte; Desktop horizontal, Mobil vertikal; Roving Tabindex mit
  Links/Rechts beziehungsweise Hoch/Runter sowie Home/End.
- Auto-Preview nur fuer eine explizit aus strukturierten Exportrecords gebundene aktive
  Report-Session. Keine Heuristik. Innerhalb der exakten Session: HTML vor TXT/JSON, PDF zuletzt;
  manuelle Auswahl bleibt autoritativ.
- Acceptance-Status:
  `docs/status/2026-07-31-gate4-primary-workflow-report-ux-acceptance.md`.
- Source-Manifest: 33 Dateien, SHA-256
  `ba17d57f5d05c2f3247cf680e813ceafa77fe1d4a98c38598a224a2f5dfeeef6`.
- Freeze-Record SHA-256:
  `9224a6ce868503f742b3379596d2f708b2cd568745f2b1fc2d57aac9bd1d4508`.
- Gate 4 bleibt uncommitted. Kein Staging, Commit, Push oder Reset ohne separate Nutzeranweisung.
**Du befindest dich bereits am richtigen Arbeitsort** (`.worktrees/operator-workbench-phase1`,
Branch `report-ux-polish`). Verifiziere mit `git branch --show-current`.

## GATE 5 IMPLEMENTIERUNGSSTAND (TASK 8 OFFEN, 2026-08-06)

- Nutzerfreigegebene Spezifikation:
  `docs/superpowers/specs/2026-08-06-gate5-emf-authority-source-truth-design.md`.
- Selbstgepruefter TDD-Implementierungsplan:
  `docs/superpowers/plans/2026-08-06-gate5-emf-authority-source-truth.md`.
- Verbindliche Aktivierungspolitik: default-off bei erstmaliger Initialisierung, danach dauerhaft
  aktiv bis zur bewussten manuellen Deaktivierung; Reload/Prozessneustart setzt nicht still zurueck.
- Moderne `/api/emf/*`- und Legacy-`/api/v1/emf/*`-Routen muessen auf dieselbe durable Autoritaet,
  dieselbe Messung und dieselbe API-Key-/Session-/Lease-Sicherheit delegieren.
- Legacy-WebSocket-Connect darf niemals aktivieren. Disable rotiert die Generation und verhindert
  jeden spaeteren HTTP-/WebSocket-Publish unter dem alten Lease.
- Sichtbare Bezeichnung: `System-/Entropie-basierter EMF-Proxy-Index`. Werte bleiben bei Software-
  Fallback sichtbar, aber jeder Teilwert zeigt `rng`, `cpu_timing`, `system_load` oder
  `sensor_entropy` sowie `ok`, `partial`, `fallback` oder `unknown`.
- Nichtziele: physische Sensorintegration, Linux-Root-Server, Remote-WSS, Hardwaremodulation,
  Harmonisierung, Quantum/Grover und Cloud-Integration.
- Tasks 1-5 und 7 sind implementiert und final taskweise APPROVE-reviewed.
- Task 6 ist final Spec- und Quality/Accessibility-approved. Der Monitor zeigt alle vier Quellen,
  versteckt Invalid-Gauges, normalisiert Hardwarestatus konsistent und stellt nach gueltigem Frame
  den Verbindungsstatus wieder her. Badgekontraste: 5.404:1 und 8.285:1.
- Manuelle reale Desktop-/375px-Acceptance ist PASS; Server, Screenshots, Skript und Temp-Runtime
  wurden danach entfernt.
- Die volle Python-Suite muss nach dem Markerfix wiederholt werden. Die volle Browsermatrix, globale
  Gate-5-Reviews und das Gate-5-Manifest/Freeze/Acceptance fehlen noch.
- Detaillierter Wiederanlaufstatus:
  `PROJECT_MEMORY/2026-08-06-gate5-session-checkpoint.md`.
- Kein Staging/Commit/Push ohne separate Nutzeranweisung.

---

## F5-MAKROBLOCKMODELL (verbindlich)

Makrobloecke dienen ausschliesslich der ergonomischen Orchestrierung. Teilnummern, RED-Vertraege,
Sicherheitsgrenzen, Verifikationslaeufe, Hashfreeze, unabhaengige Reviews, Stop-Gates und externe
ShadowCopies bleiben separat rueckverfolgbar und einzeln stoppfaehig.

- **F5-A:** F5.5 Source-Policy/lokale Importgrenzen; F5.4 atomare Registry-/Audit-/Rollbackpfade;
  F5.1 vollstaendiger Batch-Hash, Replay-Schutz und quarantinisiertes `analysis_only`-Staging.
- **F5-B:** F5.2 typenspezifische Source-Normalizer; F5.3 kontrollierte Draft-Uebernahme.
- **F5-C:** F5.6 verbleibende Pipeline-Haertung und F5-Gesamtgate.

Verbindliche Reihenfolge je Makroblock: read-only Discovery; Authority-/Scope-Entscheidung;
hashverifizierte externe Pre-State-ShadowCopy; getrennte RED-Mikrogates; kleinste GREEN-Implementierung;
adversariale Haertung; Fokus/Admin/breit/Top-5; Hashfreeze; zwei driftfreie technische Reviews;
Gate-/Memory-Dokumentation; dokumentationsgebundener Doppelreview; externe Post-State-ShadowCopy mit
vollstaendiger Rueckverifikation. Jeder Patch nach Reviewdispatch invalidiert den Snapshot.

Die historischen Reviewbatches `deleg_9444028c` und `deleg_0ab4aeb0` sind nicht gatewirksam; alle
Befunde sind geschlossen. Der maßgebliche Freeze v3 besitzt zwei unabhängige driftfreie technische
APPROVE mit null P0–P3. Der Gate-Record
`docs/status/2026-07-15-feedback-f-F5-A-source-pipeline-hardening-gate.md` definiert CONDITIONAL GO:
wirksam erst nach zwei dokumentgebundenen APPROVE und anschließender vollständig rückverifizierter
externer Post-State-ShadowCopy. Bis dahin bleibt F5-B gesperrt.
Aktueller F5-A-Nachweis: Fokus `114 passed, 1 skipped`;
Admin `437 passed, 6 skipped`; breit `921 passed, 8 skipped` plus exakt 14 bekannte Baselinefehler;
Top-5 `1 passed in 98.70s`; Ruff, `py_compile` und `git diff --check` PASS. Das Consistency-Ledger
verwendet Schema v3 und `data-record-consistency`; `data-promote` ist nur deprecateter Alias. Keine Catalog-Promotion, kein Publish,
keine Aktivierung, kein Netzwerk und kein lokales Source-Daten-I/O.

---

## ⚠️ WICHTIG

1. **Nicht nach `C:\morphic_v1` (Root, `master`-Branch) wechseln, um dort zu arbeiten.** Dort liegen
   nur Referenz-Dokumente und ein eigener, unbezogener uncommitteter Stand von `app.js`/`index.html`
   aus einer fruehen Session — nicht anfassen.
2. **UI/UX-Konsolidierungsplan (abgeschlossen, nur noch als Referenz):**
   `docs/superpowers/plans/2026-07-07-operator-workbench-radi144-uiux-consolidation.md`
   (auf `master` committet; `git show master:<pfad>` falls hier nicht sichtbar)
3. **Nutzer-Feedback-Liste (Quelle fuer aktuelle Arbeit):** `C:\Users\Hubert111\Desktop\forderung.txt`
   (lokale Datei auf dem Host, nicht im Repo). Enthaelt Punkte a) bis f), vom Nutzer selbst grob
   priorisiert in einer Tabelle (Aufwand/Risiko). Vorgehen bisher: pro Punkt erst rein analytisch
   (Grep/Read, kein Code), dann Tabelle mit Entscheidungsfragen an den Nutzer, dann TDD-Umsetzung
   nach Freigabe.
4. **Aktueller HEAD:** `2d38d3b`. Der Working Tree ist gezielt fuer Gate-4-Remediation und
   Acceptance-Dokumentation modified sowie historisch umfangreich untracked. Er enthaelt
   mehrere bereits abgeschlossene Feedback-Gates. Nicht pauschal bereinigen, stagen, resetten oder
   committen; immer nur den aktuellen Scope gezielt pruefen.

---

## FORTSCHRITT: RADI144-UI/UX-KONSOLIDIERUNGSPLAN — ✅ VOLLSTAENDIG (9/9)

Alle 9 Tasks abgeschlossen und committet (`3a957a3` WIP → `bbda9ae` (Task 5, .jpg-Validierung) →
`18b2c4f` (Task 2, main_symptom-Regressionstests) → `ea3a457` (Task 7, Harmonisierung Phase 11 +
Impuls/Pause/Solfeggio-Backend) → `fbfd75c` (Task 8, Berichtskatalog) → `d8c75d4` (Task 9,
Radi144-Paritaet-Politur)). Kein weiterer Handlungsbedarf, ausser der Nutzer meldet neue Luecken.

---

## FORTSCHRITT: NUTZER-FEEDBACK-LISTE (forderung.txt, Punkte a–f)

Vom Nutzer selbst grob priorisierte Tabelle: a) einheitliches Design aller Berichte (Workflow-Look,
niedrig/mittel), b) Scores auf max. 5 Nachkommastellen (sehr niedrig/klein), c) PDF-Berichte ohne
Layout — nur Rohtext (niedrig, aber technisch groesster Einzelpunkt), d) Export-Pfad-Isolation pro
Klient (hoch/gross, mehrstufig, betrifft kuenftige Radiquant4-Multi-Tenancy mit 6 Modulen),
e) Klientendatenerfassung nach Radi144-Vektoren (hoch/mittel-gross, Vorsicht bei Kernengine-Feldern),
f) Admin-Verwaltung von Profilen/Remedies/Multiplexen + Online-Repositories (mittel/gross).
Vereinbartes Vorgehen: der Reihe nach b) → c) → d) → e) → f), a) noch nicht terminiert.

| Punkt | Titel | Status | Commit | Naechster Schritt |
|---|---|---|---|---|
| b | Scores max. 5 Nachkommastellen | ✅ fertig | `abe8739` | — |
| c | PDF-Berichte ohne Layout (Rohtext-Bug) | ✅ fertig | `d4701e7` | — |
| d | Export-Pfad-Isolation pro Klient (Single + Multi-Tenancy) | ✅ fertig (alle 5 Phasen) | `713b66a` | — |
| e | Klientendatenerfassung nach Radi144-Vektoren | ✅ fertig | — | E4/E5 einschliesslich E5.10F GO; Geo bleibt separater NO-GO-Zweig |
| f | Admin-Verwaltung Profile/Remedies/Multiplexe + Online-Repos | technisch abgeschlossen, produktive Runtime-Autoritaet default-off | — | F1-F8/Option A+B technisch GO; formales aktuelles Gate 14 bleibt vor Produktivaktivierung offen |
| a | Einheitliches Design aller Berichte (Workflow-Look) | technisch umgesetzt | `29481ab` | Keine Produktivfreigabe allein aus diesem historischen Feedback-Gate ableiten |

### Befund/Umsetzung Punkt d) — Export-Pfad-Isolation (tenant_id-basiert, Variante 1: strikt, nur aktueller Tenant)

Entscheidung (nach radiquant4-Live-Verifikation via `git show HEAD:...` auf `C:\morphic_v1\radiquant4-live-ref`,
oeffentliches Repo zwischenzeitlich vom Nutzer freigeschaltet/wieder deaktiviert): Isolationsschluessel heisst
`tenant_id` (nicht `workspace_id`), additiv mit `resolve_operator_context().workspace_id` als Default-Fallback
und `MORPHIC_TENANT_ID`-Env-Override. Begruendung: radiquant4s eigenes `_resolve_tenant_scope()`
(`session_orchestrator.py:341`) und `UnifiedTenantMiddleware` (`middleware.py:32-133`) nutzen exakt dieses
Muster (request-scoped `tenant_id`, Fail-Closed bei fehlendem Tenant) — `morphic_v1` spiegelt das jetzt als
Vorlage fuer die 6 kuenftigen Module.

**Phase 1 (fertig):** `core/compliance/operator_context.py` — `OperatorContext.tenant_id` (Pflichtfeld,
Default = `workspace_id`, Override via `MORPHIC_TENANT_ID`). Tests: `tests/test_operator_context.py`.

**Phase 2 (fertig):** `apps/cli/commands/helpers/utility_helpers.py::_resolve_export_paths()` und
`tools/reporting_common.py::client_report_dir()` haben optionalen `tenant_id`-Parameter — Root-Ordner
bekommt `__<tenant_id>`-Suffix, **nur** wenn gesetzt (additiv, kein Effekt bei leerem String). Tests:
`tests/test_topn_export_paths.py`, `tests/test_reporting_common.py`.

**Phase 3 (fertig):** Alle 5 CLI-Consumer (`field.py`, `interpretation_generator.py`, `trend_analyzer.py`,
`remedy_reporter.py`, `synergy_consolidator.py`) reichen `tenant_id` durch — **aber nur wenn der interne
Default-Root verwendet wird**, nicht bei explizit vom Nutzer gesetztem `--export`/`--output-root`/
`--archive-root` (Frage 6, User-Antwort: "aktuelles Verhalten" bleibt fuer explizite Pfade unangetastet).
Wichtige Falle dabei: in `field.py` heisst die Variable bewusst `export_tenant_id` (nicht `tenant_id`),
weil sie nur beim `export is None`-Zweig (interner Default `Benutzer_Archive`) gesetzt wird — bei
explizitem `--export` bleibt sie leer.

**Phase 4 (fertig):** `apps/web/main.py` — `DEFAULT_REPORT_ROOTS`-Konstante ersetzt durch Funktion
`default_report_roots(tenant_id)` (5 Pfade mit `__<tenant_id>`-Suffix). `app.state.report_catalog`
(einmalig bei App-Start gebaut) ersetzt durch `app.state.report_catalog_factory` (Callable, loest
`resolve_operator_context().tenant_id` **pro Aufruf** neu auf — echte leseseitige Isolation, wie vom
Nutzer gefordert). Ein explizit an `create_app(report_roots=...)` uebergebener Wert (nur in Tests) bleibt
unangetastet, keine Tenant-Suffixierung. Tests: `tests/test_web_shell.py::test_web_shell_report_roots_isolate_by_tenant_id`
(neu) + `test_web_shell_lists_opens_and_previews_reports` angepasst (`report_catalog` → `report_catalog_factory()`).

**Phase 5 (fertig):** Test-Exportordner auf `C:\` geloescht (`C:\Benutzer_Archive_Start`,
`C:\Benutzer_Deutung_Start`, `C:\Benutzer_Synergy_Start`, `C:\Benutzer_Remedies_Start`,
`C:\Benutzer_Trends_Start` — `C:\Benutzer_Archive` existierte nicht). User-Freigabe erhalten,
alles reine Testdaten (Test_Klient-Fixtures), Loeschung statt Migration wie vereinbart.
`pyproject.toml:44` (`norecursedirs`) und `config.yaml:1` (`archive_root`) noch nicht angepasst —
beide referenzieren weiterhin die alten, jetzt geloeschten Pfadnamen; niedrige Prioritaet, da
Tests durchgehend `tmp_path` nutzen und `config.yaml` aktuell von keinem produktiven Web-/CLI-Pfad
gelesen wird (nur `monitoring/health.py`/`core/db/health.py` referenzieren die Schluessel
`archive_root` etc. als Health-Check-Konfig-Erwartung). Bei Bedarf spaeter nachziehen.

**Verifikation Phase 1–4:** `pytest tests -q` → 282 passed, 2 skipped (2026-07-10), committet in
`713b66a` ("feat: tenant_id-basierte Export-Pfad-Isolation (feedback point d, Phasen 1-4)").
Betroffene Dateien: `core/compliance/operator_context.py`, `apps/cli/commands/helpers/utility_helpers.py`,
`tools/reporting_common.py`, `apps/cli/commands/field.py`, `tools/interpretation_generator.py`,
`tools/trend_analyzer.py`, `tools/remedy_reporter.py`, `tools/synergy_consolidator.py`, `apps/web/main.py`,
sowie neue/geaenderte Tests (`tests/test_operator_context.py`, `tests/test_entitlement_stub.py`,
`tests/test_topn_export_paths.py`, `tests/test_reporting_common.py` (neu), `tests/test_web_shell.py`).

### Befund Punkt c) (fuer Kontext bei kuenftigen PDF-Themen, z.B. Punkt a)

Drei PDF-Erzeuger existierten parallel: `core/pdf_handler.py` (nur manueller `pdf-export`-CLI-Befehl,
unbenutzt im reguraeren Workflow), `tools/pdf_exporter.py::html_to_pdf()/write_layout_pdf()`
(ReportLab-basiert, HTML-strukturiert, bereits produktiv in `tools/reporting_common.py`), und
`tools/simple_pdf.py::write_text_pdf()` (reiner Rohtext-Fallback, manuell gebaute PDF-Objekte).
Der reguläre Scan-Workflow (`field.py` field-test/multiplex-scan, `interpretation_generator.py`
Deutung) rief bislang direkt `write_text_pdf()` auf statt `html_to_pdf()` — obwohl bereits
vollstaendig formatiertes HTML vorlag. Fix: alle drei Stellen nutzen jetzt `html_to_pdf()`.
Falls Punkt a) (einheitliches Design) angegangen wird: `tools/pdf_exporter.py` ist die zentrale
Stelle fuer PDF-Layout, `_render_basic_html`/`render_legacy_html` (in `apps/cli/commands/helpers/`
bzw. `tools/reporting_common.py`) fuer HTML-Layout.

---

## VERIFIKATION

```powershell
$env:PYTHONUTF8="1"
$env:PYTHONIOENCODING="utf-8"
$env:OPENBLAS_NUM_THREADS="1"
& C:\morphic_v1\.venv\Scripts\python.exe -m pytest tests -q --tb=short
# Letzter voller Lauf (2026-08-06): 3108 passed, 17 skipped, 9 bekannte Warnungen

npm --prefix tests\browser test
# Letzte volle Browsermatrix (2026-08-06): 49 passed in vier isolierten Shards

node --check apps/web/static/app.js
node --check apps/web/static/workbench-api.js
node --check apps/web/static/workbench-render.js
node --check apps/web/static/workbench-state.js
```

**Wichtig (Git-Bash-Syntax, nicht PowerShell):** In diesem CLI-Kontext laeuft Git Bash (POSIX sh).
`$env:VAR="x"` (PowerShell) funktioniert NICHT — stattdessen `VAR=x command` oder `export VAR=x`.
Pfade mit Backslash in Anfuehrungszeichen setzen oder auf `/c/...`-Form umstellen.

Radi144-Referenz zum visuellen Abgleich (nur noch fuer Punkt a/e relevant): `http://localhost:8090/user_workflow.html`

---

## KRITISCHE PFADE (relativ zu diesem Worktree)

```
apps/web/static/index.html          11-Phasen-Wizard-HTML
apps/web/static/app.css             Design-Tokens + Styles
apps/web/static/app.js              Business-Logik, onStepEnter-Hook, formScanPayload()
apps/web/static/workbench-render.js Rendering (renderReviewCards, renderFocusHistoryChips, renderChoiceCards)
apps/web/static/workbench-state.js  Zustand + loadFocusHistory/saveFocusToHistory
apps/web/static/workbench-api.js    Alle fetch()-Aufrufe
apps/web/contracts.py               Phase1ScanRequest (main_symptom, .jpg/.jpeg-Validierung)
apps/web/hardware_truth.py          build_hardware_truth_snapshot() - components ist Dict!
apps/web/display_scores.py          DISPLAY_SCORE_DECIMALS=3, normalize_display_payload() (Web-Layer)
apps/web/harmonization.py           WorkerHarmonizationService (Adapter zu services/harmonization_worker.py)
services/harmonization_worker.py    start_harmonization_job() mit pulse/pause/solfeggio Parametern
apps/cli/commands/scan.py:422-484   Reale Profilvorlage/Entropie-Semantik (Quelle der Hint-Texte)
apps/cli/commands/field.py          field-test/multiplex-scan Export (JSON/HTML/TXT/PDF), _resolve_export_paths
apps/cli/workflow/substep_manifest.py  12-Substep-Mapping (Quelle der Timeline in Phase 7)
tools/pdf_exporter.py               html_to_pdf()/write_layout_pdf() — zentraler ReportLab-Layout-PDF-Renderer
tools/simple_pdf.py                 write_text_pdf() — reiner Rohtext-Fallback, NICHT im regulaeren Workflow verwenden
tools/interpretation_generator.py   Deutung-Report-Generator (HTML + PDF via html_to_pdf)
tools/reporting_common.py           register_report_artifact(), client_report_dir() — Export-Pfad-Basis (relevant fuer Punkt d)
```

---

## 🔧 CONTRACT-FALLSTRICKE (bereits einmal zum Bug gefuehrt — nicht wiederholen)

- `apps/web/hardware_truth.py`: `components` im Response ist ein **Dict** (keyed by Komponenten-Id),
  **kein Array**. Frontend-Konsumenten muessen `Object.values()` verwenden.
- `main_symptom` (in `apps/web/contracts.py`) ist **nicht rein dokumentarisch** — `apps/web/launcher.py:58-68`
  kombiniert es mit `focus` und beeinflusst dadurch die Analyse.
- Profilvorlage/Entropie-Modus-Semantik ist real in `apps/cli/commands/scan.py:422-484` definiert.
- **Score-Rundung:** Aktuelle Web-Anzeige verwendet 3 Nachkommastellen. Interne
  Berechnungswerte, die in nachgelagerte Logik einfliessen (z.B. `harmonization_helpers.py:337`
  `round(normalized, 4)` → Level-Berechnung; `core/realtime/emf_profile.py`; `apps/web/analyze.py`
  `composite_emf_index`; `core/hardware/snapshots.py`), wurden **bewusst nicht angefasst**, da unklar
  ob sie in Schwellwert-/Gate-Logik einfliessen. Bei Bedarf einzeln pruefen, nicht pauschal aendern.
- **PDF-Erzeugung (Punkt c):** Immer `tools/pdf_exporter.py::html_to_pdf()` verwenden, niemals
  `tools/simple_pdf.py::write_text_pdf()` direkt im regulaeren Report-Workflow (nur als interner
  Fallback in `write_layout_pdf()`, falls ReportLab zur Laufzeit fehlt).

---

**Vollstaendiger Kontext UI/UX-Plan:** `docs/superpowers/plans/2026-07-07-operator-workbench-radi144-uiux-consolidation.md`
**Vollstaendiger Kontext Feedback-Liste:** `C:\Users\Hubert111\Desktop\forderung.txt` (lokal, nicht im Repo)

---

## KLARUNGEN F/G/G2/G3 (2026-08-04)

### f) Externe Registry-Quellen / Admin-Verwaltung

- `core/admin_catalog` ist vollstaendig implementiert, aber der Runtime-Adapter bleibt **read-only Shadow**.
- Produktive Profile kommen weiterhin aus `core/profile_sync/__init__.py::MASTER_PROFILES`.
- Aktivierungsschalter: `MORPHIC_ADMIN_CATALOG_ENABLED` (`1/on/true` = an, `0/false/off` = aus); in `Run-WebUI.ps1` default `0`.
- API-Endpunkte unter `/api/admin/catalog` (geschuetzt durch `apps/web/admin_security.py::require_admin_request`).
- Externe Registries: Source-Adapter in `core/admin_catalog/source_adapters/` (NCBI Taxonomy, Live-Acceptance).
- Draft/Revision/Activate/Rollback ist implementiert; nutzt SQLite-Persistenz ueber `core/admin_catalog/store.py`.

### g) Profile/Multiplexe/Remedies erweitern

- **Profile (Produktion):** In `core/profile_sync/__init__.py` `_register()`-Eintrag zu `MASTER_PROFILES` hinzufuegen; Attribute: name, display_name, groups, category, level, aliases, enabled.
- **Remedies/Multiplexe:** Ueber Admin-Catalog-API:
  1. `create_draft()`
  2. `create_remedy()` / `create_multiplex()` (oder update)
  3. `validate_draft()`
  4. `publish_draft()`
  5. `activate_revision()`
- Persistenz: `core/admin_catalog/store.py` (SQLite).
- Validierung: `core/admin_catalog/validation.py`.

### g2) Echtzeithardware, deterministisch vs. stochastisch

- **Deterministischer Modus:** `core/realtime/seed_generator.py::generate_deterministic_seed()` — SHA256 aus workspace_id + Patientendaten, reproduzierbar.
- **Stochastischer Modus:** `generate_seed_with_entropy(use_hardware=True)` — mischt OS-CSPRNG (`os.urandom()`) ein.
- Hardware-Status wird ueber `apps/web/hardware_truth.py` und `core/hardware/drivers.py`/`sensors.py` ermittelt; die meisten Komponenten melden aktuell `software_fallback`.
- Quartz-Echtzeitsteuerung ist `not_implemented`.
- Default im Workbench: deterministisch mit optionalem Hardware-Entropy.

### g3) Standalone vs. Cloud-Plattform

- Kein expliziter Standalone/Cloud-Modus im Code.
- **Verbindliches Zielbild:** RadiMorphic und Radi144 muessen standalone funktionsfaehig bleiben,
  werden produktiv aber als integrierbare Module der spaeteren hybriden Radiquant-/Lovable-Cloud-
  Plattform vorbereitet.
- **Standalone-first:** Lokale Datei-Persistenz, kein Cloud-Call im Kern.
- **Multitenant-Vorbereitung:** `core/compliance/operator_context.py` (`operator_id`, `workspace_id`, `tenant_id`) und Tenant-Suffixe fuer Report-Roots sind implementiert.
- **Cloud-Interoperabilitaet:** `core/compliance/platform_export.py` baut Radiquant4-kompatible `StandardAnalysisBlock`-Outputs.
- **Aktueller Default:** reiner Standalone-Betrieb.
- **Referenzgrenze:** `redshift-three67/radi144` und `redshift-three67/radiquant-cloud-build`
  ausschliesslich read-only analysieren. Radi144 darf UI/UX, Stepper und Sequenzfluss praegen, aber
  nicht ungeprueft RadiMorphic-Algorithmen, Kernengine oder Fachfunktionalitaet ersetzen.
