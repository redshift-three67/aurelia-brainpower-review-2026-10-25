# radiquant4 / radimorphic — Kontrakt-Referenz für morphic_v1

Stand: `2026-07-05` (Serverzustand `root@185.242.115.210:/opt/radiquant4`, read-only via WinSCP geprüft)
Zweck: Präzise, codebasierte Referenz dessen, was `radiquant4` von einem andockfähigen `radimorphic`-Baustein technisch erwartet — als Zielbild für die Fertigstellung von `morphic_v1`.

> Wichtig: Diese Datei beschreibt ausschließlich, was auf dem `radiquant4`-Server **gelesen** wurde. Es wurden keine Änderungen an `radiquant4` vorgenommen. Lokale Kopien der zitierten Dateien liegen (read-only, kuratiert, ohne Secrets) unter `C:\Users\Hubert111\Documents\radiquant4-reference\`.

## 1. Plattform-Gesamtbild (aus `SYSTEM_STATE.md`, v10.5, Stand 2026-06-07)

- Monorepo: `apps/api` (FastAPI 3.11), `apps/web-astro` (Astro 6.1 + React 19 + Tailwind 3.4), `apps/worker` (Celery/Redis), `apps/radi-core` (gemeinsame Python-Module).
- Laufzeit: Postgres (SSOT-DB, pgvector), Redis (Cache/JTI-Blacklist/Event-Bus), Celery-Worker, Ollama (lokale LLM-Inferenz), Prometheus/Grafana/Loki, GPU-Pool-Manager, Nginx-Reverse-Proxy mit TLS.
- Qualität: `3443` Backend-Tests grün, `tsc --noEmit` 0 Fehler, Codegen-Drift-Check grün, 5/5 typisierte TS-Contracts, Playwright-E2E grün, SBOM (CycloneDX 1.5), Chaos-/Stresstests.
- Live unter `app.radiquant.de`, produktiv betrieben.

## 2. Die 6-Modul-Pipeline (SSOT: `contracts/workflow-manifest.v1.json`)

```
canonical_module_order: radi144 → radiworks → radimorphic → radiblohm → radithoms → radicopen
```

| Modul | Phase | GPU | Resume-Level | UI-Label | API-Endpoint |
| --- | --- | --- | --- | --- | --- |
| radi144 | diagnose | ja | module | "Resonanz-Fokus" | `/analyze/radi144` |
| radiworks | diagnose | ja | substep | "Quanten-Scan" | `/analyze/radiworks` |
| **radimorphic** | analyse | ja | module | "Vakuum-Sync" | `/analyze/radimorphic` |
| radiblohm | analyse | nein | substep | "Projektion" | `/analyze/radiblohm` |
| radithoms | harmonize | nein | module | "Chreoden-Vektor" | `/analyze/radithoms` |
| radicopen | harmonize | nein | subsubstep | "Manifestation" | `/analyze/radicopen` |

Drei Phasen mit fester Chromotherapie/Solfeggio-Zuordnung (`diagnose`=396 Hz, `analyse`=528 Hz, `harmonize`=963 Hz, zusätzlich `reflexion`=852 Hz nur UI-seitig) inkl. CSS-Variablen pro Phase (`--phase-accent`, `--phase-bg-glow-from/-to`, `--phase-ring`).

Drei vordefinierte Workflow-Presets: `workflow_a` (Light: nur diagnose), `workflow_b` (Group Analysis: radimorphic+radiblohm), `workflow_c` (Full: alle 6 Module).

**Jedes Modul besitzt `standaloneRunSupported: true`** (`apps/web-astro/src/lib/module-registry.ts`) — Standalone-Betrieb einzelner Module ist ein explizites, offizielles Architekturprinzip der Plattform, nicht nur eine Nebenanforderung.

## 3. RadiMorphic Backend-Service (`apps/api/app/services/radimorphic/radimorphic_service.py`, ~2170 Zeilen)

### 3.1 Rolle laut Docstring

> "Lokale Gold-Orchestrierung für Multiplex-Scans, NLS-Suche, Frequenz-Analyse und HAL-basierte Harmonisierung."

### 3.2 Das kanonische 12-Substep-Contract (`_RADI_MORPHIC_GOLD_SUBSTEPS`)

| # | Substep | Phase | Zweck |
| --- | --- | --- | --- |
| 1 | `profile_resolution` | multiplex | Profile/Scan-Modus/Level auflösen |
| 2 | `candidate_generation` | multiplex | Profile/Gruppen in Multiplex-Raum überführen |
| 3 | `entropy_sampling` | multiplex | Deterministische + hybride Entropie ziehen |
| 4 | `client_signature` | multiplex | Klientensignatur/Persona/Personalvektor kodieren |
| 5 | `multiplex_scoring` | multiplex | Hadamard-Multiplex + NLS-Scoring |
| 6 | `client_modifiers` | multiplex | Stress/Schlaf/EMF/Konstitution modulieren Scores |
| 7 | `quantum_modulation` | analysis | Entropy-/Quantum-Faktoren verfeinern Treffer |
| 8 | `intention_weighting` | analysis | Fokus/Intention/planetare Gewichtung |
| 9 | `synergy_analysis` | analysis | Synergy-Kombinationen + Remedy-Synergien |
| 10 | `db_analysis` | analysis | DB-Top-Resonanzen, Analyse-Summary |
| 11 | `morphic_field` | analysis | Geometrie/Kohärenz/Achsen des morphischen Felds |
| 12 | `export` | export | Ergebnisblock, History, Export-Metadaten persistieren |

Jeder Substep wird über `_emit_gold_substep_completed(...)` an den `realtime_event_bus` gemeldet (`emit_substep_completed`, `emit_hardware_emission_started/completed/failed`) — echtzeitfähiger Event-Stream statt Text-Parsing.

### 3.3 Kern-Klassen und Methoden (Auszug, Beleg: Zeilennummern im Originalfile)

- `RateEncoder` (Z.256-275): `name_to_rate`, `date_to_rate`, `place_to_rate` — radionische Ratenkodierung aus Klientendaten.
- `MorphicFieldResonator` (Z.280-322): `calculate_m_field`, `resonance_score`, `holographic_entropy`.
- `RadiMorphicService` (Z.323ff.): u. a. `run_from_job_payload`, `run_analysis`, `run_multiplex_scan` (Z.426-828, Kernstück), `search_nls`, `get_system_status`, `analyze_frequencies`, `build_standard_analysis_block`, `start_harmonization`, `run_multiplex_scan_chunked` (überladen, gechunkt/streambar), `_hadamard_matrix`, `_multiplex_scores`, `_find_remedy_matches`, `_load_all_remedy_databases`, `_load_nls_databases_parallel`, `get_cached_result`/`cache_result`, `_persist_results`.
- Domänenkonstanten: `_MORPHIC_GEOMETRY_FACTORS` (tetrahedron/cube/merkaba/torus/flower_of_life/sri_yantra, goldene-Schnitt-nahe Faktoren), `_MORPHIC_INTENTION_FACTORS` (healing/manifestation/protection/…), `_PLANET_FACTORS` — dieselbe radionische/esoterische Domänenlogik wie in `morphic_v1` (Bruce-Copen-Resonanz, Phi/Schumann), nur mit anderer Faktorentabelle.

### 3.4 Technische Bausteine, die `RadiMorphicService` konsumiert

- **Async SQLAlchemy** (`AsyncSession`) gegen Postgres-Modelle `Patient`, `AnalysisSession`/`SessionStatus`.
- **Verteiltes Locking**: `get_session_lock` + `RedisLockManager`/`RedisLockTimeoutError` (verhindert parallele Scans auf derselben Session).
- **Multi-Tenant-Kontext**: `correlation_id_var`, `tenant_id_ctx_var`, `trace_id_ctx_var` (contextvars, request-scoped, für Logging/Tracing/Isolation).
- **Audit**: `AuditService` aus `app.services.audit.audit_service`.
- **Hardware-Entropie**: `generate_radionic_seeds` aus `app.services.hardware.seed_generator` (siehe Abschnitt 6).
- **NLS**: `get_nls_service` aus `nls_database_service.py`.
- **Fehler-Hierarchie**: `RadiMorphicHardwareUnavailableError`, `RadiMorphicInternalError`, `RadiMorphicInvalidInputError`, `RadiMorphicSessionNotFoundError` (eigener, modulweiter Exception-Namespace statt generischer Exceptions).

## 4. REST-Contract (aus `radimorphic-client.ts` + `app/schemas/radimorphic.py`)

| Endpoint | Methode | Zweck |
| --- | --- | --- |
| `/api/v1/radimorphic/analysis/{session_id}` | POST | startet asynchronen Multiplex-Scan, liefert sofort `job_id` (`RadiMorphicJobResponse`) |
| `/api/v1/radimorphic/nls/search` | POST | NLS-Datenbanksuche |
| `/api/v1/radimorphic/nls/databases` | GET | listet verfügbare NLS-Datenbanken |
| `/api/v1/radimorphic/frequency-analysis` | POST | Frequenzanalyse |
| `/api/v1/radimorphic/harmonize/{session_id}` | POST | startet asynchrone Harmonisierung |
| `/api/v1/radimorphic/results/{session_id}` | GET | liefert Ergebnisse einer Session |
| `/api/v1/radimorphic/system/status` | GET | Systemstatus (u. a. Hardware-/Quantum-Verfügbarkeit) |

Schema-Familie in `app/schemas/radimorphic.py` (26 Klassen, `_FlexibleModel`-Basis): u. a. `RadiMorphicAnalysisRequest`, `RadiMorphicJobResponse`, `RadiMorphicAnalysisResult`, `RadiMorphicResultsResponse`, `RadiMorphicSubstepContract`/`-Definition`, `RadiMorphicNlsScore`, `RadiMorphicSynergyComponent`, `RadiMorphicQuantumSynergyEntry`, `RadiMorphicRemedySynergyEntry`, `RadiMorphicDbTopResonance`, `RadiMorphicDatabaseAnalysis`, `RadiMorphicMorphicAxis`/`-FieldBlock`, `RadiMorphicHarmonizationRequest`/`-Result`/`-Response`, `RadiMorphicStatusResponse`.

Alle Typen werden per **OpenAPI-Codegen** (`schema.gen.ts`) erzeugt und im Frontend typsicher via `openapi-fetch` konsumiert (`ApiSchema<K>`-Pattern) — kein Handschreiben von Fetch-Aufrufen.

## 5. Cross-Modul-Kontrakt: `StandardAnalysisBlock` (`app/schemas/standard_analysis_block.py`)

Einheitliches Ergebnis-Schema für **alle sechs Module**, Basis für Reporting, LLM-Synthese, Monitoring, Trend-/Synergie-Analysen:

```python
class StandardAnalysisBlock(BaseModel):
    id, module: ModuleType, version
    tenant_id, session_id, patient_id, user_id
    timestamp, analysis_started_at, analysis_completed_at
    status: AnalysisStatus  # pending/running/completed/failed/partial
    summary, summary_source  # "algorithm" | "llm" | "manual"
    metrics: MetricsBlock    # general_vitality, entropy, synergy_score, confidence, trend_*, custom{}
    raw_data_refs: list[RawDataReference]  # storage_type db/s3/filesystem/redis + reference_id
    synergy_context: SynergyContext | None  # related_modules, related_patient_ids, synergy_score, coherence_factor
    module_payload: dict[str, Any]  # modulspezifisch, flexibel
    tags, notes
```

Modulspezifische Subklasse: `RadiMorphicAnalysisBlock(StandardAnalysisBlock)` mit `profile_name`, `profile_id`, `resonances`, `top_resonances`, `recurring_patterns`.

`to_llm_context()` liefert eine kompakte, PII-arme Projektion für LLM-Prompts.

**Konsequenz für morphic_v1:** Jede zukünftige Kopplung an `radiquant4` läuft über dieses Schema — nicht über morphic_v1s heutige Dateisystem-/JSON-Exportform.

## 6. Erwartete Ergebnis-Rohform für Reporting (`radimorphic_reporting_adapter.py`)

Der Reporting-Adapter erwartet `analysis_sessions.results["radimorphic"]` in exakt dieser Form:

```python
{
  "inputs": {"profiles": [...], "focus": "...", "intention": "..."},
  "outputs": {
    "quality_score": float,
    "morphic_field": float,
    "holographic_entropy": float,
    "remedy_matches": [(name: str, score: float), ...],
  },
  "meta": {"timestamp": iso8601, "source_system": "R4_RADIMORPHIC"},
}
```

Daraus werden automatisch erzeugt: ein `InterpretationReport`, `TrendPoint`-Serien (`radimorphic_quality_score`, `radimorphic_morphic_field`, `radimorphic_holographic_entropy`) und `RemedyRecommendation`-Einträge (Rang = Listenposition).

**Bemerkenswert:** `remedy_matches` als `(name, score)`-Tupelliste entspricht nahezu 1:1 der Ausgabeform, die `morphic_v1` heute schon in seiner eigenen Remedy-/Top-N-Logik erzeugt (`tools/remedy_reporter.py`, `core/quantum_synergy/synergy_core.py`).

## 7. Orchestrierung & Dispatch (`app/services/orchestrator/session_orchestrator.py`, ~1400 Zeilen)

- `execute_full_workflow(...)`: kompletter Pipeline-Lauf über mehrere/alle Module.
- `execute_single_module(...)` / `execute_module_for_existing_session(...)`: **Standalone-Einzelmodul-Ausführung** — der technische Mechanismus hinter `standaloneRunSupported`.
- `_assert_module_entitlement(...)`: Abo-/Tier-Gate vor Modulausführung (siehe Abschnitt 8).
- `_resolve_tenant_scope(...)`: Tenant-Isolation pro Aufruf.
- `_resolve_approved_clipboard_inputs` / `_targets_from_clipboard_inputs`: kuratierter Cross-Modul-Datenaustausch ("Clipboard"-Konzept) statt impliziter globaler Zustände.
- `_merge_synergy_buffers` / `compute_synergy_score`: Cross-Modul-Synergieberechnung.
- `_harmonize_module` → `_harmonize_radimorphic(...)`: modulspezifische Harmonisierungs-Dispatch-Funktion, analog für alle 6 Module.

## 8. Multitenancy & Abo-Gating (Backend: `tenant.py`, `subscription.py`; Frontend: `entitlements.ts`)

### Tenant (B2B, nicht nur Benutzerkonto)

```python
class TenantBase:
    slug, name, subdomain, max_users=10, max_patients=1000
```
Ein Tenant = eine Organisation/Praxis mit eigener Subdomain, eigenen Nutzern und Patienten.

### Subscription/Plan

`PlanTier` (`free`/`starter`/`professional`/`enterprise`), Stripe-Checkout/-Portal/-Webhooks, Quoten (`max_patients`, `max_sessions_per_month`, `max_storage_mb`, `max_api_requests_per_day`, `max_users`), `features: dict` inkl. `available_modules`.

### Modul-Freischaltung pro Tier (`entitlements.ts`)

| Tier | Freigeschaltete Module |
| --- | --- |
| free | radi144, radiworks |
| starter | radi144, radiworks, **radimorphic**, radiblohm |
| professional / enterprise | alle 6 Module |

`radimorphic` ist also nicht im kostenlosen Einstiegstarif enthalten, sondern ab `starter` freigeschaltet. Backend-seitig ist `subscription_gate_service.py` nur noch eine Kompatibilitäts-Fassade vor `module_access_service.EntitlementService` (echte Gate-Logik).

## 9. Echtzeit-/Entropie-Kaskade (`app/services/hardware/seed_generator.py`)

Kanonisches Muster für nachvollziehbare, tenant-gebundene Zufalls-/Seed-Erzeugung:

```
TRNG-Kaskade: QRNG (Kozyrev/AMD 3D V-Cache/GPU) → WebCam-Hotbits → Infinite-Noise-USB-TRNG → ESP32 → os.urandom (Fallback)
```

- **Deterministischer Seed:** `sha256(f"{tenant_id}:{first_name}:{last_name}:{birth_date}:{birth_time}:{birth_place}:{geo_location}")[:8]` als int — reproduzierbar, tenant-gebunden, ohne Klartext-PII im Seed selbst.
- **Hardware-Seed (optional, "Quantum-Modus"):** aus TRNG-Kaskade, plus 30 Audit-Samples für statistische Nachvollziehbarkeit.
- Rückwärtskompatibler Wrapper `generate_radionic_seeds(...)` liefert `(deterministic_seed, hardware_seed, entropy_samples)`.

**Das ist der konkrete "Echtzeit + Nachvollziehbarkeit"-Goldstandard**, an dem sich `providers/hardware/entropy_sources.py` und `core/realtime/emf_profile.py` in `morphic_v1` messen lassen sollten (siehe Lückenanalyse).

## 10. Quantum-Architektur (`SYSTEM_STATE.md`, Abschnitt 2.4)

| Komponente | Rolle |
| --- | --- |
| PennyLane 0.44.1 | VQC-Resonanz-Boost in RadiMorphic (`lightning.gpu`-Backend) |
| Qiskit 2.2.3 + Aer | QRNG in RadiThoms, Grover-Kandidaten-Boost |
| NumPy-Fallback | immer verfügbar |
| Graceful Degradation | Kaskade **Qiskit → PennyLane → NumPy**, automatischer Fallback, alle 3 Backends aktiv gepflegt |

Vergleich zu `morphic_v1`: `core/quantum_synergy/grover_search.py` hat exakt dieselbe Fallback-Idee (Qiskit → klassisch), aber nur zwei Stufen statt drei, und `qiskit` ist in `morphic_v1`s `.venv` nicht installiert (siehe `PHASE_8_QUANTUM_FRAMEWORK_TIEFENANALYSE.md`).

## 11. Frontend-Stack & Design-Referenz (`apps/web-astro`)

- **Stack:** Astro 6.1 (SSR) + React 19 (Islands) + TailwindCSS 3.4 + shadcn/ui + TypeScript + `openapi-fetch` + Playwright/Vitest.
- **Design-Tokens:** `src/styles/design-tokens.css` (oklch-basiert, semantische Tokens `--background/--foreground/--primary/...`, Phasen-Tokens `--phase-diagnose/-analyse/-harmonize/-reflexion`, Modul-Primärfarben `--radi144-primary` … `--radicopen-primary`, Typografie `Fraunces` (Display-Serif) + `Inter` (Sans), Radius-Skala `--radius` … `--radius-3xl`, Glow-/Shadow-Tokens, Motion-Tokens).
- **Tailwind-Bindung:** `tailwind.config.mjs` mappt alle Tokens 1:1 in Utility-Klassen (`colors.radimorphic`, `boxShadow.glow.morphic`, `animation.breathe/floating/aurora-drift`, Z-Index-Skala inkl. `skip-link`).
- **Referenzkomponenten:** `WorkflowWizardIsland.tsx` (Haupt-Wizard, ~56 KB), `ModulePageIsland.tsx` (generische Modul-Seite pro Pipeline-Modul), `DesignSystemShowcase.tsx` + `pages/design-system.astro` (lebende Design-System-Doku), `HardwareReadinessIsland.tsx`, `HarmonizationJobMonitor.tsx`, `SynergyMatrix.tsx`, `QuantumResonanceVisualizer.tsx`, `Navigation/{Sidebar,MobileHeader,Breadcrumbs}.astro`.
- **Modul-Registry:** `module-registry.ts` — pro Modul `slug/title/backendRoute/uiFolder/primaryComponent/standaloneRunSupported`. `radimorphic` → `primaryComponent: "MultiplexWorkflow"`.

## 11a. Substep-Vokabular-Mapping (morphic_v1 -> radiquant4)

Umgesetzt in `apps/cli/workflow/substep_manifest.py` (`SUBSTEP_MANIFEST`, getestet in `tests/test_substep_manifest.py`). Kurzfassung:

| morphic_v1 Step | radiquant4-Substep-Aequivalent |
| --- | --- |
| `step01_init` | `entropy_sampling` |
| `step02_input` | `profile_resolution` (naeherungsweise) |
| `step03_signature` | `client_signature` |
| `step04_focus` | `intention_weighting` |
| `step05_emf` | `client_modifiers` |
| `step06_amplifier` | kein Aequivalent (morphic_v1-spezifisch) |
| `step07_palette` | kein Aequivalent (radiquant4 hat Chromotherapie nur auf Phasen-, nicht Substep-Ebene) |
| `step08_matrix` | `multiplex_scoring` |
| `step09_quantum` | `quantum_modulation` |
| `step10_post` | `db_analysis` |
| `step11_export` | `export` |
| `step12_harmonize` | kein Aequivalent (radiquant4 fuehrt Harmonisierung als eigenen Job-Flow ausserhalb der 12 Substeps) |

Radiquant4-Substeps ohne morphic_v1-Quellschritt: `candidate_generation`, `synergy_analysis`, `morphic_field`.

## 12. Lokale Referenzkopie (kuratiert, keine Secrets)

```
C:\Users\Hubert111\Documents\radiquant4-reference\
├── SYSTEM_STATE.md, UMSETZUNGSPLAN.md
├── contracts\workflow-manifest.v1.json
├── apps\api\app\schemas\{radimorphic,standard_analysis_block,subscription,tenant,session,patient,client,engine_output,job_queue,harmonization_job,preflight}.py
├── apps\api\app\services\radimorphic\{radimorphic_service,accel_service,exceptions,nls_database_service,__init__}.py
├── apps\api\app\services\{radimorphic_reporting_adapter,subscription_gate_service,hardware_seed_generator}.py
├── apps\api\app\services\orchestrator\session_orchestrator.py
├── apps\web-astro\{tailwind.config.mjs,astro.config.mjs,package.json}
├── apps\web-astro\src\styles\{design-tokens.css,global.css}
├── apps\web-astro\src\layouts\{BaseLayout.astro,AuthLayout.astro}
├── apps\web-astro\src\components\{DesignSystemShowcase.tsx,ModulePageIsland.tsx,WorkflowWizardIsland.tsx}
├── apps\web-astro\src\components\ui\{QuantumResonanceVisualizer.tsx,Loading.tsx}
├── apps\web-astro\src\components\{Theme\ThemeManager.astro,Navigation\{Sidebar,MobileHeader,Breadcrumbs}.astro}
├── apps\web-astro\src\lib\{entitlements.ts,route-access.ts,module-registry.ts,module-registry-client.ts}
├── apps\web-astro\src\lib\engines\{radimorphic-client.ts,workflow-client.ts}
├── apps\web-astro\src\lib\workflow\manifest.ts
└── components\ui\{button.tsx,input.tsx}
```

Nicht heruntergeladen (bewusst ausgeschlossen): `.env*`, `keys/`, `cert(s)/`, `vault-config.hcl`, `users_backup*.csv`, `backups/`, `.backup/`, `node_modules/`, `.git/`, `logs/`, Admin-Reset-Skripte, Monitoring-Rohdaten.
