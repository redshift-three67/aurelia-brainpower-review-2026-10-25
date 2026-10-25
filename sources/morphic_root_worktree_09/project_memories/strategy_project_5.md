# Strategischer Optimierungsplan — Morphic Engine V1

## Prüfmodus, Bindung und Aussagegrenzen

Diese Analyse ist eine **streng statische, passive Architekturprüfung** des Worktrees `C:/morphic_v1/.worktrees/operator-workbench-phase1`. Es wurden weder Projektmodule importiert noch Tests, Server, Browser, Migrationen, Hardwarezugriffe oder Netzwerkaufrufe ausgeführt. Es wurden keine Quellen, Konfigurationen, Laufzeitdaten oder Git-Objekte verändert. Die alleinige zulässige Schreiboperation ist dieses verlangte Plan-Dokument.

Die Aussage „loss-free“ kann nicht als absoluter Beweis erbracht werden. Stattdessen bewahrt dieses Dokument beobachtete Nuancen durch explizite Zustände: `implemented`, `documented`, `static-inference`, `unverified-runtime`, `excluded`, `absent-by-search` und `future-only`. Dynamische Pfade, optionale Pakete, umgebungsabhängige Werte und untracked Artefakte bleiben bewusst als nicht statisch verifiziert gekennzeichnet.

```json
{
  "artifact_type": "static_bilingual_strategic_optimization_plan",
  "review_mode": "strict-static-read-only",
  "repository_root": "C:/morphic_v1/.worktrees/operator-workbench-phase1",
  "branch": "report-ux-polish",
  "head": "151e2bb0a69d49677a0b1e40e0bffd0f172d34c4",
  "source_manifest_sha256_before": "8faba19159c3a8a6ba5c5196cf7d0e9096abe846ffc764ae131d71c4a0a7f58b",
  "git_status_all_sha256_before": "6ffb1f3e39d0832e7e5d703afb8ea07c5461f78d0506c2d2d05d861164279e69",
  "git_status_all_count_before": 6062,
  "scope": {
    "included": ["apps/", "core/", "services/", "tools/", "cli/", "providers/", "monitoring/", "data/", "tests/", "pyproject.toml", "requirements.txt", "config.yaml", "Run-WebUI.ps1", "README.md"],
    "excluded_without_content_inspection": [".git/", ".venv/", "Benutzer_Archive*/", "data/harmonization_jobs/", "tests/browser/node_modules/", "tests/browser/test-results/", "untracked historical reviews and archives"],
    "excluded_reason": "Potential runtime, client, credential, browser-cache, archive, or pre-existing untracked evidence; not source authority for this static review.",
    "not_executed": ["pytest", "node", "uvicorn", "FastAPI import", "SQLite access", "browser automation", "hardware discovery", "network requests"]
  },
  "states": ["implemented", "documented", "static-inference", "unverified-runtime", "excluded", "absent-by-search", "future-only"]
}
```

## Management Summary (Deutsch)

Das Repository ist ein lokaler Single-Operator-Prototyp mit drei produktiven Oberflächen: Typer-CLI, FastAPI-Operator-Workbench und datei-/SQLite-basierte lokale Persistenz. Die aktuelle Architektur enthält ungewöhnlich viele explizite Sicherheits- und Konsistenzmechanismen: Loopback-Startgrenzen, optionale API-Key-/Cookie-Authentisierung, Eigentümer-Scope, idempotente Startautoritäten, jobgebundene Prozessidentität, tenant-spezifische Workbench-Daten, report-root-Validierung sowie unveränderliche Catalog-Revisionen.

Die Stabilitätsgrenze liegt nicht primär in fehlenden Bausteinen, sondern in **mehreren parallel gewachsenen Autoritäten und Betriebsmodellen**: historische `web_app.py`-Routen neben `apps/web/main.py`, einfache globale Konfiguration neben tenantgebundenen Laufzeitpfaden, produktive `MASTER_PROFILES` neben einem bewusst nicht scanwirksamen Admin Catalog sowie dokumentierte optionale Integrationen ohne statisch belegte produktive Aktivierung. Diese Differenzierung darf bei einer Optimierung nicht geglättet werden.

Priorität hat daher nicht ein Umbau der Resonanz-/Scoring-Engine. Zuerst ist eine autoritätsgebundene, rückwärtskompatible Konsolidierung der Produktionspfade erforderlich: eine verbindliche Entry-point-Matrix, klar markierte Legacy-Grenzen, ein belastbarer Dependency-Lock- und Deployment-Vertrag, ein maschinenlesbares API-/Schema-Register und isolierte Tests für jede Sicherheitsinvariante. Änderungen an Kernformeln, Profile-Pools, Exportformaten oder medizinisch interpretierbaren Texten bleiben bis zu einer eigenen Freigabe tabu.

## Architecture Map (English)

### Layer model

```text
Operator / local browser / CLI shell
  ├─ PowerShell controlled launcher: Run-WebUI.ps1
  ├─ CLI adapter: apps/cli/main.py (Typer)
  ├─ Web composition root: apps/web/main.py:create_app()
  └─ Legacy parallel server: web_server.py → web_app.py
       ↓
Boundary layer
  ├─ Pydantic contracts, router handlers, security middleware
  ├─ command construction, API safe views, HTML/report sanitization
  └─ WebSocket and process/job lifecycle adapters
       ↓
Application services
  ├─ scan jobs / process supervision
  ├─ harmonization worker adapter
  ├─ workbench draft/template/run-trace store
  ├─ report catalog and runtime manifest
  └─ admin catalog service / source registry
       ↓
Domain and compliance
  ├─ profile authority: core/profile_sync::MASTER_PROFILES
  ├─ operator/tenant ownership context
  ├─ source registry and source-data promotion
  ├─ realtime EMF profile and hardware abstractions
  └─ platform export adapter
       ↓
Authorities and artifacts
  ├─ JSON runtime files, locked/atomic writes, report directories
  ├─ local subprocess state and process identity
  ├─ SQLite catalog / description / remedy stores
  └─ JSON, HTML, TXT, PDF, StandardAnalysisBlock exports
```

```json
{
  "architecture_layers": [
    {"id":"entrypoints","state":"implemented","paths":["Run-WebUI.ps1","apps/cli/main.py","apps/web/main.py","web_server.py","web_app.py"],"responsibility":"Local startup, CLI command registration, web composition, and legacy server compatibility."},
    {"id":"web_boundary","state":"implemented","paths":["apps/web/contracts.py","apps/web/security.py","apps/web/workbench.py","apps/web/emf.py","apps/web/scan_live.py"],"responsibility":"HTTP/WebSocket validation, authentication generation, UI-facing safe payloads, and route binding."},
    {"id":"process_and_job_services","state":"implemented","paths":["apps/web/scan_jobs.py","apps/web/start_operations.py","apps/web/harmonization.py","services/harmonization_worker.py"],"responsibility":"Durable job lifecycle, ownership, idempotency, polling, process supervision, and worker control."},
    {"id":"domain_authorities","state":"implemented","paths":["core/profile_sync/__init__.py","core/compliance/operator_context.py","core/source_registry.py","core/realtime/emf_profile.py"],"responsibility":"Profile selection, identity scope, source authority, and derived realtime telemetry."},
    {"id":"persistence_and_export","state":"implemented","paths":["apps/web/workbench_runtime.py","core/compliance/runtime_manifest.py","tools/reporting_common.py","apps/web/reports.py","core/admin_catalog/store.py"],"responsibility":"Local JSON/SQLite persistence, report registration/cataloging, tenant-separated runtime data, and catalog revision storage."},
    {"id":"external_platform_adapter","state":"implemented_additive","paths":["core/compliance/platform_export.py","apps/cli/workflow/step11_export.py"],"responsibility":"Best-effort StandardAnalysisBlock export for radiquant4-compatible consumption; it does not replace local exports."}
  ]
}
```

### Core invariants

| ID | Invariant (English technical definition) | State | Evidence |
|---|---|---|---|
| INV-01 | The controlled Windows web launcher binds to `127.0.0.1`, preflights the selected port, and does not terminate an existing listener. | implemented | `Run-WebUI.ps1:35-44`, `Run-WebUI.ps1:88-90`, `README.md:5-12` |
| INV-02 | API authentication is optional only when `MORPHIC_API_KEY` is absent; otherwise API key or generation-bound browser cookie is required. | implemented | `apps/web/security.py:46-49`, `apps/web/security.py:361-383` |
| INV-03 | Unsafe cookie-authenticated methods require exact same-origin matching. | implemented | `apps/web/security.py:196-236`, `apps/web/security.py:375-382` |
| INV-04 | Protected response emission revalidates the captured authentication generation and can compensate protected mutations. | implemented | `apps/web/security.py:239-317`, `apps/web/security.py:428-463` |
| INV-05 | Owner scope is a SHA-256 digest over the exact ordered `[tenant_id, operator_id]` tuple; protected resources use strict owner checks where implemented. | implemented | `core/compliance/operator_context.py:42-52`, `core/compliance/operator_context.py:140-143` |
| INV-06 | Scan starts are bound to a current profile-pool SHA-256 fingerprint and reject stale or oversized Top-N requests. | implemented | `apps/web/contracts.py:16-44`, `apps/web/main.py:233-267` |
| INV-07 | Scan/harmonization starts require an idempotency key and replay through an owned authority rather than silently creating a second job. | implemented | `apps/web/main.py:841-868`, `apps/web/main.py:869-983`, `apps/web/main.py:1051-1139` |
| INV-08 | The Workbench runtime store namespaces data by SHA-256(tenant ID), uses process locks, and writes through durable I/O. | implemented | `apps/web/workbench_runtime.py:51-97`, `apps/web/workbench_runtime.py:132-148` |
| INV-09 | Sensitive draft fields cannot be persisted without explicit request consent; `local_ai_enabled` is intentionally non-persisted. | implemented | `apps/web/workbench.py:37-40`, `apps/web/workbench.py:164-181`, `apps/web/workbench_runtime.py:17-34` |
| INV-10 | Browser report previews restrict file types, bound preview size, sanitize HTML, and produce report IDs from root identity plus relative components. | implemented | `apps/web/reports.py:27-56`, `apps/web/reports.py:69-192`, `apps/web/reports.py:195-216` |
| INV-11 | `core/profile_sync::MASTER_PROFILES` remains the scan-effective profile authority; active source-registry entries are metadata-only for scan selection. | implemented | `core/profile_sync/__init__.py:151-186`, `apps/web/workbench.py:97-130` |
| INV-12 | The Admin Catalog has explicit context-scoped SQLite revisions, immutable validation/import records, finalized revision constraints, and activation pointers; it is not proven scan-effective by this static review. | implemented / integration-limited | `core/admin_catalog/store.py:1-5`, `core/admin_catalog/store.py:127-398`, `apps/web/workbench.py:119-128` |
| INV-13 | EMF output is labelled as a derived system/entropy proxy, not a physical field measurement; enablement is durable until manually disabled. | implemented | `apps/web/emf.py:26-42`, `apps/web/emf.py:129-191`, `apps/web/main.py:417-453` |
| INV-14 | The Radiquant-compatible standard block is additive, preserves unknown quantities as `null`, and does not replace ordinary exports. | implemented | `core/compliance/platform_export.py:1-15`, `core/compliance/platform_export.py:29-104`, `apps/cli/workflow/step11_export.py:124-144` |

## Boundary and Dependency Map (English)

```json
{
  "dependency_edges": [
    {"from":"Run-WebUI.ps1","to":"apps.web.main:app","kind":"controlled_uvicorn_start","state":"implemented","evidence":"Run-WebUI.ps1:23-42,183"},
    {"from":"apps/cli/main.py","to":"apps/cli/commands/*","kind":"Typer_command_registration","state":"implemented","evidence":"apps/cli/main.py:39-50"},
    {"from":"apps/web/main.py","to":"apps/web/{emf,workbench,scan_live,admin_catalog,group_drafts,group_consents}.py","kind":"router_composition","state":"implemented","evidence":"apps/web/main.py:658-671"},
    {"from":"apps/web/main.py","to":"apps/web/scan_jobs.py","kind":"LocalScanJobService","state":"implemented","evidence":"apps/web/main.py:492-505,1195-1201"},
    {"from":"apps/web/main.py","to":"apps/web/harmonization.py","kind":"WorkerHarmonizationService","state":"implemented","evidence":"apps/web/main.py:506-507,957-972"},
    {"from":"apps/web/main.py","to":"core/compliance/operator_context.py","kind":"current_operator_tenant_context","state":"implemented","evidence":"apps/web/main.py:512-517"},
    {"from":"apps/web/workbench.py","to":"core/profile_sync/__init__.py","kind":"scan_profile_pool_authority","state":"implemented","evidence":"apps/web/workbench.py:25-32,66-83"},
    {"from":"apps/web/workbench.py","to":"core/source_registry.py","kind":"source_metadata_read","state":"implemented_non_scan_effective","evidence":"apps/web/workbench.py:97-130,210-222"},
    {"from":"tools/reporting_common.py","to":"core/compliance/runtime_manifest.py","kind":"best_effort_artifact_registration","state":"implemented","evidence":"tools/reporting_common.py:590-620"},
    {"from":"apps/web/main.py","to":"apps/web/reports.py","kind":"tenant_bound_report_catalog","state":"implemented","evidence":"apps/web/main.py:531-548,777-819"},
    {"from":"apps/cli/workflow/step11_export.py","to":"core/compliance/platform_export.py","kind":"optional_additive_standard_block","state":"implemented_additive","evidence":"apps/cli/workflow/step11_export.py:124-144"},
    {"from":"core/admin_catalog/store.py","to":"scan_runtime","kind":"direct_productive_consumer","state":"absent-by-static-mapping","evidence":"core/admin_catalog/store.py:1-5; apps/web/workbench.py:119-128"},
    {"from":"web_server.py","to":"web_app.py","kind":"legacy_server_path","state":"implemented_parallel_legacy","evidence":"web_server.py:40; web_app.py:56-882"}
  ],
  "exportable_dependencies": [
    {"name":"StandardAnalysisBlock","producer":"core/compliance/platform_export.py","consumer_contract":"radiquant4-compatible reporting adapter","state":"implemented_additive","fields":["inputs","outputs","meta"]},
    {"name":"report_artifact_catalog","producer":"tools/reporting_common.py and core/compliance/runtime_manifest.py","consumer":"apps/web/reports.py via report roots/catalog","state":"implemented_with_dual_discovery_paths"},
    {"name":"scan_job_safe_view","producer":"apps/web/main.py","consumer":"apps/web/static/workbench-api.js and app.js","state":"implemented","fields":["job_id","status","returncode","progress_percent","current_phase","current_substep","completed_substeps","completed_stage_ids","current_stage_id","updated_at","diagnostics"]},
    {"name":"hardware_truth_snapshot","producer":"apps/web/hardware_truth.py","consumer":"apps/web/static/workbench-render.js","state":"implemented","critical_shape":"components is a dictionary keyed by component id"},
    {"name":"admin_catalog_revision","producer":"core/admin_catalog/store.py","consumer":"apps/web/admin_catalog.py","state":"implemented_but_runtime_activation_not_statically_proven"}
  ]
}
```

## API Contracts (English)

| Route family | Contract / boundary | State | Evidence |
|---|---|---|---|
| `/api/auth/session`, `/api/auth/status` | Issues/revokes an HTTP-only, strict-SameSite session cookie only after API-key verification; session authority is process-local and generation-bound. | implemented | `apps/web/main.py:693-736`, `apps/web/security.py:57-112` |
| `/api/scan/preview`, `/api/scan/jobs` | Accepts `Phase1ScanRequest`; validates consents, dates, profile template, entropy mode, JPEG suffix, profile-pool fingerprint, and idempotency key for start. | implemented | `apps/web/contracts.py:16-144`, `apps/web/main.py:1039-1251` |
| `/api/scan/jobs/{id}`, `/stop`, `/results`, `/sync-trace` | Requires validated authority ID and owner-scoped job access; only safe fields are returned. Result extraction is restricted to paths under the job export root. | implemented | `apps/web/main.py:1333-1535` |
| `/api/harmonization/jobs` | Requires `HarmonizationRequest` and idempotency key; binds work to current tenant/operator and selected report ID. | implemented | `apps/web/contracts.py:147-171`, `apps/web/main.py:869-1037` |
| `/api/reports/*` | Lists, previews, and streams catalogued report files; download response closes its handle in `finally`. | implemented | `apps/web/main.py:777-819`, `apps/web/reports.py:227-260` |
| `/api/workbench/*` | Provides registry, current internal profile pool plus source metadata, hardware snapshot, consent-gated drafts/templates, and owned run traces. | implemented | `apps/web/workbench.py:184-347` |
| `/api/emf/*`, `/api/v1/emf/*` | Modern and legacy aliases share enable/disable/status/profile/monitor/WebSocket semantics with generation revalidation. Output is derived telemetry only. | implemented | `apps/web/emf.py:26-126`, `apps/web/emf.py:194-260` |
| `/api/admin/catalog/*` | Draft/validate/diff/publish/activate/rollback management interface protected by admin security; runtime scan activation remains explicitly unavailable in the visible scan catalog. | implemented / limited integration | `apps/web/admin_catalog.py:38-465`, `apps/web/workbench.py:119-128` |

```json
{
  "api_contracts": [
    {"route":"POST /api/scan/preview","request_model":"Phase1ScanRequest","response_model":"Phase1ScanPreviewResponse","auth":"verify_api_key","side_effect":"none_expected","state":"implemented","paths":["apps/web/contracts.py","apps/web/main.py"]},
    {"route":"POST /api/scan/jobs","request_model":"Phase1ScanRequest + Idempotency-Key","response_model":"Phase1ScanStartResponse","auth":"verify_api_key + owner_scope","side_effect":"subprocess job and runtime records","state":"implemented","paths":["apps/web/main.py","apps/web/scan_jobs.py","apps/web/start_operations.py"]},
    {"route":"POST /api/harmonization/jobs","request_model":"HarmonizationRequest + Idempotency-Key","response_model":"safe harmonization view","auth":"verify_api_key + tenant/operator ownership","side_effect":"worker job","state":"implemented","paths":["apps/web/contracts.py","apps/web/main.py","apps/web/harmonization.py"]},
    {"route":"GET /api/reports/{report_id}/preview","request_model":"path report_id","response_model":"catalog preview","auth":"verify_api_key","side_effect":"none_expected","state":"implemented","paths":["apps/web/main.py","apps/web/reports.py","apps/web/report_handles.py"]},
    {"route":"PUT /api/workbench/draft","request_model":"WorkbenchDraftEnvelope","response_model":"WorkbenchDraftEnvelope","auth":"verify_api_key","side_effect":"tenant-scoped durable JSON","state":"implemented","paths":["apps/web/contracts.py","apps/web/workbench.py","apps/web/workbench_runtime.py"]},
    {"route":"GET|POST /api/emf/* and /api/v1/emf/*","request_model":"route-specific","response_model":"status or derived proxy payload","auth":"verify_api_key + auth generation","side_effect":"enable/disable state and bounded measurement lease","state":"implemented","paths":["apps/web/emf.py","apps/web/security.py","apps/web/emf_authority.py"]}
  ]
}
```

## Persisted Schemas and Artifact Contracts (English)

### Runtime JSON and report contracts

- `WorkbenchRuntimeStore` persists `draft.json`, `templates.json`, and `run_traces.json` under `workbench/tenant-v1-<sha256(tenant_id)>/`. The run-trace store demands exactly `{ "run_traces": [...] }`; each `run_id` must satisfy the authority-ID validator. (`apps/web/workbench_runtime.py:17-21`, `99-135`, `183-248`)
- Report registration derives a supplied session ID or a deterministic session fallback from the resolved parent directory; registration failure is intentionally swallowed and returns `None`. This preserves report-generation availability but makes catalog completeness a non-guaranteed best-effort property. (`tools/reporting_common.py:590-620`)
- The report catalog accepts `.html`, `.htm`, `.json`, `.txt`, `.pdf`; preview is byte/character bounded and HTML is allow-list sanitized. (`apps/web/reports.py:27-124`, `127-192`)
- Workflow Step 11 writes JSON/HTML/TXT and attempts a `standard_block.json` additively; it currently materializes `morphic_field=0.0`, `holographic_entropy=0.3`, and `entropy_calibrated=0.3 * 0.247` inside the legacy workflow export, while the platform adapter deliberately exports those unavailable fields as `null`. Both facts must remain distinct. (`apps/cli/workflow/step11_export.py:34-91`, `124-144`; `core/compliance/platform_export.py:97-103`)

### Admin Catalog SQLite schema

The following is a normalized, non-exhaustive machine map of visible schema authorities. It does not assert that an existing database has been migrated or that every migration path executed; that is runtime-unverified.

```json
{
  "schemas": [
    {"authority":"apps/web/workbench_runtime.py","storage":"durable JSON","namespace":"tenant-v1-SHA256(tenant_id)","records":["draft","templates","run_traces"],"constraints":["run_traces payload has exactly run_traces key","validated authority run_id","process lock plus thread lock"],"state":"implemented"},
    {"authority":"core/admin_catalog/store.py","storage":"SQLite","schema_version":8,"context_key":["operator_id","workspace_id","tenant_id","scope"],"tables":["catalog_drafts","catalog_draft_validation_attestations","catalog_draft_source_imports","catalog_draft_profile_tombstones","catalog_draft_managed_tombstones","catalog_revisions","catalog_revision_entries","catalog_activations","catalog_audit_events"],"constraints":["immutable validation attestation update/delete triggers","immutable source-import receipt update/delete triggers","global batch identity replay unique index","finalized revision immutability","revision-entry insert block after finalization","activation version > 0"],"state":"implemented"},
    {"authority":"core/compliance/platform_export.py","storage":"JSON export","schema":"StandardAnalysisBlock","fields":{"inputs":["profiles","focus","intention"],"outputs":["quality_score","morphic_field","holographic_entropy","remedy_matches"],"meta":["timestamp","source_system"]},"state":"implemented_additive"},
    {"authority":"apps/web/reports.py","storage":"filesystem catalog","accepted_extensions":[".html",".htm",".json",".txt",".pdf"],"identity":"SHA256(canonical_root, root device/inode, relative components)","state":"implemented"}
  ]
}
```

## Dependency, Deployment, and Operational Truth (English)

### Declared package dependencies

`pyproject.toml` is the packaging authority observed by this review: Python `>=3.10`; runtime dependencies `numpy`, `pydantic`, `typer[all]`, `fastapi`, `uvicorn[standard]`, `requests`, `websockets`, `psutil`, `reportlab`; optional extras `qiskit`, `cupy-cuda12x`, `pytest`, `pytest-asyncio`. (`pyproject.toml:1-35`)

`requirements.txt` declares overlapping but non-identical dependencies, additionally listing `pyserial`, `scipy`, and `matplotlib`, while describing Qiskit/CUDA as commented optional installation. (`requirements.txt:1-35`) This is a concrete dual-manifest drift risk, not proof that either environment is currently broken.

### Deployment boundaries

- `Run-WebUI.ps1` is the controlled loopback path and constructs ephemeral admin bootstrap values; its isolated acceptance mode explicitly disables Admin Catalog and group analysis and creates disposable runtime roots. (`Run-WebUI.ps1:35-72`, `88-183`)
- `README.md` declares external multiuser/LAN/SaaS use out of scope and explicitly warns that direct Uvicorn bypasses the controlled `web_server.py` protection path. (`README.md:3-40`)
- `apps/web/main.py` can be imported as `app = create_app()` and defaults absent runtime paths to `Path.cwd()/codex_tmp/...`, whereas the controlled launcher supplies its own environment-bound path. This is an operational boundary worth making explicit. (`apps/web/main.py:456-524`, `1570`)
- `config.yaml` still names unsuffixed `C:\Benutzer_*_Start` roots. The web default roots tenant-suffix those roots and the CLI helper suffixes only when a tenant value is passed. (`config.yaml:1-4`, `apps/web/main.py:172-179`, `tools/reporting_common.py:547-572`)

## Strategic Optimization Plan (Deutsch)

### Nicht verhandelbare Schutzplanken

1. **Keine Kernalgorithmus-Substitution.** `MASTER_PROFILES`, Scoring, Entropie, Resonanz, Synergie, medizinisch interpretierbare Sprache und bestehende Exportinhalte dürfen nicht durch diesen Plan ersetzt werden.
2. **Keine Produktivaktivierung des Admin Catalog ohne separaten Wirksamkeitsnachweis.** Der sichtbare Katalog meldet externe Quellen ausdrücklich als `registry_only` und `scan_effect=false`; eine UI-Aktivierung wäre keine fachliche Scan-Integration.
3. **Keine Aufweichung der lokalen Sicherheitsgrenze.** Optionaler API-Key ist kein Mehrbenutzer-System. LAN, TLS, zentraler Principal, echte Tenant-Autorisierung und Secret-Lifecycle bleiben eigenständige Architekturentscheidungen.
4. **Keine pauschale Bereinigung untracked Daten.** Die initiale Statuspopulation umfasst 6.062 Einträge, darunter Archive, Browserartefakte und historische Reviews. Ihre Klassifizierung/Retention ist ein separater Datenschutz- und Betriebsentscheid.
5. **Keine Gleichsetzung von „statisch vorhanden“ mit „zur Laufzeit wirksam“.** Jede künftige Umsetzung benötigt einen isolierten RED/GREEN-Nachweis auf dem tatsächlichen Entry-point.

```json
{
  "no_go_boundaries": [
    {"id":"NG-01","rule":"Do not replace profile scoring, entropy, resonance, synergy, or existing report semantics during architecture consolidation.","affected_paths":["core/profile_sync/","apps/cli/commands/field.py","apps/cli/commands/scan.py","services/harmonization_worker.py"]},
    {"id":"NG-02","rule":"Do not represent admin-catalog activation or source-registry status as scan-effective until a full registry-to-scan consumption contract is proven.","affected_paths":["core/admin_catalog/","apps/web/admin_catalog.py","apps/web/workbench.py","core/profile_sync/__init__.py"]},
    {"id":"NG-03","rule":"Do not expose non-loopback service, enable CORS, or claim multi-tenant security without an approved network/auth architecture gate.","affected_paths":["Run-WebUI.ps1","web_server.py","apps/web/security.py","apps/web/main.py"]},
    {"id":"NG-04","rule":"Do not delete or copy excluded runtime/archive data as part of source optimization.","affected_paths":["Benutzer_Archive*/","data/harmonization_jobs/","tests/browser/node_modules/","tests/browser/test-results/"]}
  ]
}
```

### Befundmatrix

| ID | Schwere | Befund | Empfohlene Maßnahme | Abhängigkeit / Stop-Gate |
|---|---|---|---|---|
| F-01 | hoch | Zwei Web-Server-/Routenoberflächen existieren parallel: der aktuelle Kompositionspfad `apps/web/main.py` und die Legacy-Oberfläche `web_app.py`. | Eine verbindliche Entry-point-Matrix als Dokument und Testvertrag erstellen; jede Route als `current`, `legacy-compatible` oder `retired-candidate` kennzeichnen. Erst danach einen freigegebenen, schrittweisen Deaktivierungsplan formulieren. | Kein Entfernen von `web_app.py` ohne Traffic-/Launcher-/Testnachweis. |
| F-02 | hoch | Paketautorität ist auf `pyproject.toml` und `requirements.txt` verteilt; die Mengen differieren. | Einen Dependency-Authority-Gate durchführen: installierte Zielumgebung, beide Manifeste und optionalen GPU/Quantum-Pfad vergleichen; erst danach einen lockbaren, reproduzierbaren Installationsvertrag beschließen. | Kein Versions-Upgrade oder Neu-Pinning ohne Plattformmatrix und vollständige Regression. |
| F-03 | hoch | Der Admin Catalog ist technisch stark abgesichert, aber die Scanprofil-API deklariert externe Quellen ausdrücklich als nicht scanwirksam. | Eine getrennte „catalog-to-scan-effectiveness“-Entscheidung vorbereiten: Datenmodell, Validation, erlaubte Entry-Typen, Revision-Pointer, Rollback und `MASTER_PROFILES`-Kompatibilität. Bis dahin UI wording beibehalten. | Erst Preview-only; kein Publish/Activate/Scan-Effekt im selben Gate. |
| F-04 | mittel | Mehrere Exportautoritäten koexistieren: direkte Dateiexporte, Runtime Manifest, Report Catalog und StandardAnalysisBlock. `register_report_artifact` ist best effort und verschluckt Fehler. | Ein exportierbares Artifact-Contract-Register erstellen: Producer, Pfad, Session-ID-Quelle, Pflicht-/Optionalstatus, Registrierungsfehler, Consumer. Anschließend nur additive Observability für unregistrierte Artefakte. | Keine Änderung des erfolgreichen Report-Exports zugunsten von Katalogvollständigkeit. |
| F-05 | mittel | Tenant-Isolation ist asymmetrisch: Web-Workbench speichert tenant-hashed, Web report roots sind beim App-Aufbau an aktuellen Kontext gebunden, CLI export suffixing ist parameterabhängig, `config.yaml` bleibt unsuffixed. | Einen Pfadauktoritätsvertrag definieren: jeder produktive Read/Write-Pfad muss `tenant_id`-Quelle, Fallback, Override-Policy und Rückwärtskompatibilität ausweisen. Mit statischen Path-Matrix-Tests beginnen. | Keine automatische Migration vorhandener Klientenexporte. |
| F-06 | mittel | `resolve_operator_context()` erzeugt bei fehlender Datei Workspace-ID und schreibt Laufzeitstatus; damit ist die Funktion nicht für „read-only by default“-Verwendungen neutral. | Read-/create-Semantik explizit trennen oder alle Callers mit einem klaren Runtime-Initialisierungsvertrag versehen. Die Änderung benötigt Crash-/Permission-/Concurrency-Tests. | Kein Umbau der Ownership-IDs ohne Migrations-/Kompatibilitätsplan. |
| F-07 | mittel | Controlled launcher und direkter `create_app()`-Import haben unterschiedliche Runtime-Root-Defaults. | Einen einzigen dokumentierten Runtime-Root-Resolver plus explizite Entwicklungs-/Test-Injektion spezifizieren; bestehende isolierte Acceptance-Modes erhalten. | Kein Verhalten ändern, bevor alle Job-, Workbench-, EMF- und Reportstore-Callers abgebildet sind. |
| F-08 | mittel | Fortschrittsermittlung im ScanJob-Service interpretiert textuelle Prozessausgabe anhand von Markerlisten. | Ein versioniertes, strukturiertes Child-Process-Event-Protokoll zusätzlich zu bestehenden Textmarkern planen; zunächst dual schreiben und Telemetrie vergleichen. | Textparser erst entfernen, wenn reale dual-path Äquivalenz belegt ist. |
| F-09 | niedrig | Monolithische Dateien bündeln mehrere Verantwortlichkeiten: `apps/web/main.py`, `apps/web/scan_jobs.py`, `apps/web/static/app.js`, `apps/cli/commands/field.py`. | Nur nach den Autoritätsgates gezielt entlang bereits vorhandener Grenzen extrahieren: route module, orchestration service, telemetry parser, UI controller. Je Extraktion einen Import-/Contract-Regressionstest. | Kein großflächiges Reformatting oder „clean architecture“-Rewrite. |
| F-10 | niedrig | Die Plattform-Export-Adapterhaltung ist korrekt additiv, aber einzelne Legacy-Workflowfelder verwenden Platzhalterwerte, während der Standardadapter `null` nutzt. | Die semantische Herkunft je Exportfeld im Contract-Register markieren: measured, derived, placeholder, unavailable. Konsumenten dürfen `null` nicht zu `0` normalisieren. | Keine Zahlensubstitution ohne fachliche Zustimmung. |

```json
{
  "findings": [
    {"id":"F-01","severity":"high","state":"implemented_parallel_paths","statement":"Current FastAPI composition and legacy web server/application surfaces coexist.","evidence":["apps/web/main.py:456-1570","web_server.py:40","web_app.py:56-882"],"action_de":"Entry-point-Matrix und Migrationsgrenze erstellen; keine Entfernung ohne Nachweis."},
    {"id":"F-02","severity":"high","state":"documented_manifest_drift","statement":"Packaging metadata and requirements file declare non-identical dependency sets.","evidence":["pyproject.toml:13-28","requirements.txt:1-35"],"action_de":"Dependency-Authority-Gate und reproduzierbaren Installationsvertrag planen."},
    {"id":"F-03","severity":"high","state":"implemented_but_non_scan_effective","statement":"Admin catalog is persisted and route-exposed, while external scan profiles are explicitly registry-only and scan_effect=false.","evidence":["core/admin_catalog/store.py:1-398","apps/web/workbench.py:97-130"],"action_de":"Preview-only Catalog-to-Scan Gate vor jeder Aktivierung."},
    {"id":"F-04","severity":"medium","state":"implemented_dual_authorities","statement":"Artifact production, best-effort runtime registration, and report discovery are separate mechanisms.","evidence":["tools/reporting_common.py:590-646","core/compliance/runtime_manifest.py","apps/web/reports.py:227-260"],"action_de":"Artifact-Contract-Register mit Failure Semantics anlegen."},
    {"id":"F-05","severity":"medium","state":"implemented_asymmetric","statement":"Tenant propagation differs among web runtime data, web report roots, CLI export helpers, and static config defaults.","evidence":["apps/web/workbench_runtime.py:51-67","apps/web/main.py:172-179","tools/reporting_common.py:547-572","config.yaml:1-4"],"action_de":"Path-Authority-Matrix als Voraussetzung für konsolidierte Tenant-Isolation."},
    {"id":"F-06","severity":"medium","state":"implemented_side_effect_boundary","statement":"Resolving operator context can create a workspace identity file and parent directories.","evidence":["core/compliance/operator_context.py:55-76","core/compliance/operator_context.py:101-119"],"action_de":"Read/create-Lebenszyklus explizit trennen oder zentralisieren."},
    {"id":"F-07","severity":"medium","state":"implemented_configuration_split","statement":"Runtime roots are launcher-injected in one path and cwd/codex_tmp-derived in direct app construction.","evidence":["Run-WebUI.ps1:49-72","apps/web/main.py:489-524"],"action_de":"Zentralen Runtime-Root-Vertrag spezifizieren."},
    {"id":"F-08","severity":"medium","state":"implemented_text_protocol","statement":"Scan progress derives from child-process textual markers.","evidence":["apps/web/scan_jobs.py:58-96","apps/web/scan_jobs.py:118-243"],"action_de":"Versioniertes strukturiertes Ereignisprotokoll additiv einführen."},
    {"id":"F-09","severity":"low","state":"maintainability_risk","statement":"Several high-change files combine orchestration and presentation responsibilities.","evidence":["apps/web/main.py:456-1570","apps/web/scan_jobs.py:1-3123","apps/web/static/app.js:1-3917","apps/cli/commands/field.py:1-4540"],"action_de":"Nur nach Autoritätsgates klein und testgebunden extrahieren."},
    {"id":"F-10","severity":"low","state":"semantic_divergence_preserved","statement":"Legacy workflow export contains fixed values where the additive platform adapter exports unavailable values as null.","evidence":["apps/cli/workflow/step11_export.py:34-91","core/compliance/platform_export.py:97-103"],"action_de":"Feldherkunft explizit markieren; keine implizite Null-oder-Nullpunkt-Normalisierung."}
  ]
}
```

### Umsetzungsreihenfolge und Freigabegates

| Gate | Ziel | Konkrete, kleinste zulässige Lieferung | Nachweis vor GO |
|---|---|---|---|
| G0 — Authority Freeze | Ausgangswahrheit stabilisieren | Hash-gebundene Entry-point-, Runtime-root-, Tenant-path- und Export-Authority-Matrix; keine Codeänderung. | Vollständige statische Zuordnung, Schutzgrenzen, Nutzergenehmigung. |
| G1 — Dependency Authority | Installierbarkeit deterministisch machen | Beschlussdokument für `pyproject.toml` als Authority oder bewusst synchronisierte Doppelmanifest-Policy; Zielplattformen einschließlich optionaler GPU/Quantum-Pfade. | Isolierte Installationsproben und volle Regression erst nach Freigabe. |
| G2 — Entry-point Consolidation | Parallelserver kontrollierbar machen | Aktuelle/Legacy-Routenliste, Launcherbeziehung, Verbrauchernachweis und Deprecation-Spezifikation. | Kein produktiver Launcher referenziert einen zu entfernenden Pfad; API-Contract-Diff genehmigt. |
| G3 — Artifact Contract | Exporte nachvollziehbar machen | Maschinenlesbares Register für JSON/HTML/TXT/PDF/StandardBlock, Manifest und Katalog; Fehlertypen und Session-Authority. | Bestehende Exportbytes/Dateinamen bleiben im Äquivalenztest unverändert. |
| G4 — Tenant Path Authority | Isolation präzisieren | Read/write path matrix mit tenant source, override, legacy fallback und Migration-Entscheidung. | Dual-tenant, expliziter Exportpfad, fehlende Context-Datei und Report-read Tests. |
| G5 — Catalog Effectiveness Preview | Katalogwahrheit absichern | Ausschließlich import-preview und read-only Scan-effect simulation; keine Aktivierung. | Nachweis, dass source metadata, catalog revision und `MASTER_PROFILES` nicht verwechselt werden. |
| G6 — Structured Job Events | Prozessausgabe robust ergänzen | Versioniertes JSON-event dual zum Textmarker, nur Telemetrie/Status. | Realer dual-path Äquivalenznachweis für Erfolg, Fehler, Abbruch, partiellen Export. |
| G7 — Bounded Extraction | Wartbarkeit erhöhen | Eine extrahierte Verantwortung pro Gate mit unveränderten externen Contracts. | Focus tests, vollständige Python-Suite, Node syntax checks, unabhängige Reviewfreigaben. |

```json
{
  "gate_dependency_dag": {
    "nodes": [
      {"id":"G0","name":"Authority Freeze","kind":"read_only","depends_on":[]},
      {"id":"G1","name":"Dependency Authority","kind":"decision_and_implementation","depends_on":["G0"]},
      {"id":"G2","name":"Entry-point Consolidation","kind":"specification_then_implementation","depends_on":["G0","G1"]},
      {"id":"G3","name":"Artifact Contract","kind":"additive_contract","depends_on":["G0"]},
      {"id":"G4","name":"Tenant Path Authority","kind":"additive_contract","depends_on":["G0","G3"]},
      {"id":"G5","name":"Catalog Effectiveness Preview","kind":"preview_only","depends_on":["G0","G3","G4"]},
      {"id":"G6","name":"Structured Job Events","kind":"additive_dual_path","depends_on":["G0","G2"]},
      {"id":"G7","name":"Bounded Extraction","kind":"refactor","depends_on":["G1","G2","G3","G4","G6"]}
    ],
    "parallelizable_after_g0": [["G1","G3"], ["G2","G4"]],
    "forbidden_combinations": ["G5 must not combine import-preview, catalog activation, and scan-effective runtime mutation.","G7 must not combine broad refactoring with dependency upgrades or security boundary redesign."]
  }
}
```

## Frontend and Operator-Flow Assessment (English)

The frontend has a deliberately split responsibility model: `workbench-state.js` owns browser state and consent-gated local focus history; `workbench-api.js` centralizes fetch, timeout, error, reset, and idempotency handling; `workbench-render.js` creates DOM output and format normalization; `app.js` composes UI behavior, polling, start operation persistence, gating, and workflow events. (`apps/web/static/workbench-state.js:1-93`, `apps/web/static/workbench-api.js:1-382`, `apps/web/static/workbench-render.js:1-145`, `apps/web/static/app.js:1-300`)

Important preserved facts:

- `components` in hardware truth is a dictionary, not an array; rendering correctly converts it with `Object.values()`. (`apps/web/static/workbench-render.js:162-172`)
- Scan preview/start controls are blocked until the exact current profile-pool fingerprint and Top-N capacity are confirmed. (`apps/web/static/app.js:229-299`)
- Browser-side start-operation IDs are persisted in `localStorage` to reconcile ambiguous start timeouts. (`apps/web/static/app.js:86-147`; `apps/web/static/workbench-api.js:307-326`)
- UI EMF language consistently marks output as a derived proxy, and renderer suppresses invalid pseudo-gauges rather than displaying zero. (`apps/web/static/workbench-render.js:11-25`, `200-289`; `apps/web/emf.py:129-191`)
- JavaScript behavior was **not executed** in this review; syntax, DOM interaction, timeout behavior, accessibility and browser compatibility remain runtime-unverified.

## Test and Verification Topology (English)

The tracked tree contains 225 files under `tests/`; `pyproject.toml` declares `tests` as the pytest root and excludes archive/runtime-heavy directories. (`pyproject.toml:37-47`) High-volume test modules target web scan jobs, web shell, Gate 4 catalog interactions, browser process tree supervision, Gate 5 EMF source truth, and source data promotion. This indicates contract-heavy regression coverage, but it is not a coverage percentage and no tests were executed.

```json
{
  "verification_topology": {
    "state":"static-inference",
    "test_root":"tests",
    "tracked_test_file_count":225,
    "notable_test_targets":[
      "tests/test_web_scan_jobs.py",
      "tests/test_web_shell.py",
      "tests/test_gate4_report_catalog_js.py",
      "tests/browser/workbench.spec.js",
      "tests/test_browser_process_tree_supervisor.py",
      "tests/test_gate5_emf_source_truth_js.py",
      "tests/test_source_data_promotion.py"
    ],
    "recommended_post_approval_commands":[
      "PYTHONUTF8=1 OPENBLAS_NUM_THREADS=1 C:/morphic_v1/.venv/Scripts/python.exe -m pytest tests -q --tb=short",
      "node --check apps/web/static/app.js",
      "node --check apps/web/static/workbench-api.js",
      "node --check apps/web/static/workbench-render.js",
      "node --check apps/web/static/workbench-state.js"
    ],
    "limitations":["No test command was executed.","No runtime package resolution was tested.","No browser acceptance or hardware probe was run."]
  }
}
```

## Approval Checkpoint (Deutsch)

**NO-GO für Code-, Konfigurations-, Daten-, Dependency-, Deployment- und Commit-Änderungen.** Der früheste zulässige nächste Schritt nach Genehmigung ist ausschließlich **G0 — Authority Freeze** als weiterer read-only, hash-gebundener Nachweis. Erst eine explizite Nutzerfreigabe darf ein separates, klein gehaltenes Umsetzungs-Gate mit RED-Test, GREEN-Änderung, kompletter Regression und unabhängiger Review eröffnen.

Dieses Dokument stellt keine Behauptung über Laufzeitfunktion, Produktionsreife, klinische Wirksamkeit, reale Hardwaremessung oder externe Plattformkompatibilität dar. Es ist ein strategischer Architektur- und Vertragsplan auf Basis statisch gelesener Quellen.
