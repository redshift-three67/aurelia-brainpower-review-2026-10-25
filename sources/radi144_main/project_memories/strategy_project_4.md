# Radi144 — Strategischer Optimierungsplan 4

## 1. Prüfungsmodus, Aussagegrenze und Entscheidungsstatus

Diese Bewertung ist eine strikt passive, statische Architekturprüfung. Es wurden keine Produktmodule importiert, keine Tests, Server, CLI-, PowerShell- oder Deployment-Skripte ausgeführt, keine Ports geprüft und keine Runtime-, Referenz-, PII- oder Secret-Dateien geöffnet. Die alleinige Mutation dieser Prüfung ist dieses ausdrücklich angeforderte Dokument. Aussagen über Laufzeitverhalten sind daher als `static-inference` bzw. `unverified-runtime` gekennzeichnet.

Der aktuelle Quellstand ist kein freigegebener Releasezustand. Die bisherige Übergabe dokumentiert zudem ausdrücklich, dass `approved` nicht `active` bedeutet und dass reale Integration, Release, Pilot und Produktivbetrieb gesperrt bleiben (`docs/Radi144_Projektuebergabe_2026-07-24/README.md:3-4, 43-51`). Diese Aussage wird nicht durch ältere Dokumentation überschrieben.

```json
{
  "metadata_type": "review_snapshot",
  "review_mode": "static_read_only",
  "repository_root": "C:/Users/Hubert111/Documents/Radi144",
  "branch": "main",
  "head": "b8ac33a1360f1cb56f06e602fcd37cbda2a9c641",
  "initial_tracked_source_manifest_sha256": "aadc537cde0f5a2952a80a952b53b259d31afbaa82c1dcf21cd5d33579f73b2f",
  "tracked_file_count": 216,
  "tracked_python_file_count": 57,
  "tracked_test_python_file_count": 24,
  "initial_worktree_status": [
    " A AGENTS.md",
    "?? project_memories/proposed_strategy.md"
  ],
  "requested_output_path": "project_memories/strategy_project_4.md",
  "source_execution": "not_performed",
  "tests": "not_performed",
  "server_or_port_probe": "not_performed",
  "confidential_roots_excluded_without_content_inspection": [
    "data/runtime",
    "Analysen",
    "deploy/server.env",
    "RestorePoints",
    "restore_points",
    ".venv",
    "build_env"
  ]
}
```

## 2. Zusammenfassung für Entwicklung und Freigabe

Radi144 ist ein lokal orientierter Python/FastAPI-Prototyp mit einer tatsächlich vorhandenen Matrix-Engine, einer Vanilla-JavaScript-Bedienoberfläche, dateibasierter Sitzungsverwaltung, PDF-Erzeugung und einem bewusst noch nicht verdrahteten SQLite-Bus-Consumer. Die Architektur enthält brauchbare additive Grenzen — Runtime-Abhängigkeitsprofile, loopback-sichere Standardbindung, kanonische Nicht-Medizin-Marker, PII-Safe-Projection, manifest-vor-Ausführung bei Löschung und ein kuratiertes Bus-Vokabular. Diese Grenzen sind jedoch keine Freigabe für Mehrbenutzer-, Netzwerk-, Echtzeit-, klinische oder Produktivnutzung.

Die Priorität ist nicht eine funktionale Erweiterung. Zuerst müssen Exposition, Ressourcenbudget, Zustandsisolation, Persistenz-Transaktionen und fachliche Claim-Grenzen durch nachweisbare, kleine Gates geschlossen werden. Bis dahin dürfen keine externe Busverdrahtung, keine reale Hardware-/Sensorintegration, keine D-Wave-Anbindung, kein öffentliches Deployment und keine fachlich wirksame Änderung an Scoring oder Signatur erfolgen.

| Befundklasse | Statischer Status | Entwicklerische Konsequenz |
|---|---|---|
| Zugriffs- und Ausführungsgrenze | hoch | Default-off API-Key schützt nur, wenn ein nicht-Placeholder gesetzt ist; HTTP-Middleware deckt WebSockets nicht ab. Öffentliche oder Multiuser-Exposition bleibt gesperrt. |
| Pfad- und Exportgrenze | hoch | Mehrere API-Pfade können absolute Dateien lesen, absolute Pfade offenlegen oder PDF-Dateien schreiben. Vor jeder externen Bindung zwingend auf capability-bound Pfade umstellen. |
| Compute- und Zustandsgrenze | hoch | Ein globaler Engine-Singleton, mutable EMF/Amplifier-Zustände und ungebundene Matrixgröße verhindern sichere Parallelität und belastbare Mandantentrennung. |
| PII, Aufbewahrung und Löschung | hoch | JSON-Stores halten Roh-PII; die Löschkaskade ist nicht transaktional und Audit-Append-only ist nur eine Service-Konvention. |
| Fachliche/physikalische Aussagegrenze | hoch | Nicht-medizinische Marker existieren, während Oberfläche, Kommentare und Konstanten wirkungsnahe Begriffe führen; D-Wave und SDR sind future-only bzw. placeholder. |
| Dokumentations-/Deploymentdrift | mittel | Historische Docs und Setup-Ausgaben sind kein Laufzeitbeweis und enthalten mindestens einen Portwiderspruch. |

## 3. Technical architecture map (English)

### 3.1 Implemented control plane

`main.py` is the HTTP application entrypoint. It enforces `API_PROFILE` before router imports, creates one FastAPI application, installs CORS, supplies static workflow files, conditionally applies an HTTP API-key middleware, and mounts two routers under `/api/v1`.

`app/api/resonance.py` creates a process-global `ResonanceMatrixEngine` at import time. This module is the sole implemented HTTP adapter to engine analysis, database reference scanning, PDF production, EMF state, WebSockets, and amplifier management. `app/api/clients.py` is a separate adapter for safety projection, erasure manifest/execute, and audit readback.

`dev_cli.py` is an independent CLI entrypoint that imports `CLI_PROFILE`; `generate_matrix.ps1` is a separate Windows-oriented interactive orchestration surface. The static browser workflow calls HTTP endpoints only; its harmonizer runs client-side timers/audio/visual rendering and is not traced to a backend harmonization worker.

```json
{
  "metadata_type": "implemented_dependency_graph",
  "nodes": [
    {"id": "main", "path": "main.py", "state": "implemented", "role": "FastAPI application entrypoint"},
    {"id": "api_resonance", "path": "app/api/resonance.py", "state": "implemented", "role": "HTTP/WebSocket resonance adapter"},
    {"id": "api_clients", "path": "app/api/clients.py", "state": "implemented", "role": "PII-safe client and erasure adapter"},
    {"id": "engine", "path": "app/algorithms/resonance_engine.py", "state": "implemented", "role": "matrix search and response construction"},
    {"id": "signature", "path": "app/algorithms/client_signature.py", "state": "implemented", "role": "client/group/image/geo signature generation"},
    {"id": "emf", "path": "app/algorithms/emf_compensator.py", "state": "implemented_with_future_hardware_boundary", "role": "software-derived environment profile and optional continuous monitor"},
    {"id": "amplifier", "path": "app/algorithms/amplifier.py", "state": "implemented", "role": "amplifier registry, match and palette modulation"},
    {"id": "stores", "path": "app/services/json_store.py", "state": "implemented", "role": "atomic-replace JSON persistence primitive"},
    {"id": "bus", "path": "app/interchange_bus", "state": "implemented_but_unwired", "role": "SQLite consumer-side bus contract"},
    {"id": "ui", "path": "user_workflow.js", "state": "implemented", "role": "same-origin browser workflow"},
    {"id": "cli", "path": "dev_cli.py", "state": "implemented", "role": "CLI report and archive workflow"},
    {"id": "powershell", "path": "generate_matrix.ps1", "state": "implemented_legacy_adapter", "role": "PowerShell workflow and runtime metadata adapter"}
  ],
  "edges": [
    {"from": "main", "to": "api_resonance", "kind": "router_mount", "evidence": "main.py:14,111"},
    {"from": "main", "to": "api_clients", "kind": "router_mount", "evidence": "main.py:15,113"},
    {"from": "api_resonance", "to": "engine", "kind": "process_global_instance", "evidence": "app/api/resonance.py:16,27-33"},
    {"from": "engine", "to": "signature", "kind": "algorithm_dependency", "evidence": "app/algorithms/resonance_engine.py:13,107"},
    {"from": "engine", "to": "emf", "kind": "optional_runtime_state", "evidence": "app/algorithms/resonance_engine.py:14,122-124,166-191"},
    {"from": "engine", "to": "amplifier", "kind": "algorithm_dependency", "evidence": "app/algorithms/resonance_engine.py:15,127-129"},
    {"from": "api_resonance", "to": "stores", "kind": "archive_and_artifact_metadata", "evidence": "app/api/resonance.py:52-62,83-125,138-150"},
    {"from": "api_clients", "to": "stores", "kind": "safe_projection_and_erasure", "evidence": "app/api/clients.py:27-51,62-118"},
    {"from": "ui", "to": "api_resonance", "kind": "same_origin_fetch", "evidence": "user_workflow.js:2,228,271,323,700,740,1042,1543"},
    {"from": "cli", "to": "stores", "kind": "session_archive_mirror", "evidence": "dev_cli.py:13-15,239"}
  ]
}
```

### 3.2 Core invariants and boundaries (English)

| ID | Invariant / boundary | State | Evidence |
|---|---|---|---|
| INV-01 | A launcher must fail before meaningful runtime import if its declared dependency profile is incomplete. | implemented | `app/bootstrap.py:19-35,62-80`; `main.py:10-15`; `app/algorithms/resonance_engine.py:1-3`; `dev_cli.py:8-9` |
| INV-02 | Direct `main.py` defaults to loopback `127.0.0.1:8090`; configured CORS defaults to the two loopback origins. | implemented | `main.py:42-57,124-142` |
| INV-03 | The API key gate is disabled unless `API_KEY` is nonempty and differs from `<set-local-api-key>`; it only applies to HTTP requests. | implemented; not an authentication guarantee for WebSockets | `main.py:78-107` |
| INV-04 | Every `ResonanceAnalysisResponse` built by the HTTP adapter carries a newly constructed safety block; PDF generation appends the same disclaimer string. | implemented | `app/api/resonance.py:255-276,847-858`; `app/services/safety_service.py:24-44` |
| INV-05 | Raw identity data is intentionally retained internally because signature generation depends on it; `/clients` removes four specified raw fields only. | implemented; privacy boundary is partial | `app/services/safety_service.py:8-11,49-77`; `app/models/client_registry.py:9-18` |
| INV-06 | Client registry identity is a deterministic lowercase/string normalization key and is emitted as `cli-` plus SHA-1 prefix. | implemented | `app/models/client_registry.py:26-56`; `app/services/client_registry_service.py:21-46` |
| INV-07 | Session/artifact references form `client_id -> session_id -> artifact_id/path`; the erasure flow follows this relation. | implemented | `app/models/session_archive.py:8-27`; `app/models/report_manifest.py:6-17`; `app/services/erasure_service.py:74-101,178-243` |
| INV-08 | The bus consumer accepts only allowed topic/schema pairs, self-certifying envelope IDs, and `real_output_enabled=false`, `medical_claims=0`. | implemented within consumer path; not application-wired | `app/interchange_bus/topics.py:12-45`; `app/interchange_bus/envelope.py:54-180`; `app/services/bus_consumer_service.py:23-119` |
| INV-09 | The MVP bus role is consumer-only; no `publish` operation is implemented in `BusConsumerStore`. | implemented/documented | `app/interchange_bus/consumer_store.py:8-10`; `app/services/bus_consumer_service.py:122-145` |
| INV-10 | `precision` mode snapshots and restores Torch RNG state after normal completion; `quantum` mode remains stochastic. | implemented but exception-path restoration is unverified by structure | `app/algorithms/resonance_engine.py:282-303,481-484` |

## 4. API contracts and schema map (English)

The following is the static contract surface mounted at `/api/v1`. `ResonanceAnalysisRequest` is shared by analysis and DB ranking/scanning routes. Untyped `dict` payloads intentionally have no Pydantic field contract in the source.

```json
{
  "metadata_type": "api_contracts",
  "base_path": "/api/v1",
  "http_routes": [
    {"method": "POST", "path": "/analyze-matrix", "request": "ResonanceAnalysisRequest", "response": "ResonanceAnalysisResponse", "state": "implemented", "evidence": "app/api/resonance.py:413-466"},
    {"method": "POST", "path": "/analyze-sequence", "request": "ResonanceAnalysisRequest", "response": "ResonanceSequenceResponse", "state": "implemented", "evidence": "app/api/resonance.py:469-496"},
    {"method": "POST", "path": "/analyze-group", "request": "ResonanceAnalysisRequest", "response": "ResonanceAnalysisResponse", "state": "implemented", "evidence": "app/api/resonance.py:499-514"},
    {"method": "POST", "path": "/analyze-geo", "request": "ResonanceAnalysisRequest", "response": "ResonanceAnalysisResponse", "state": "implemented", "evidence": "app/api/resonance.py:517-532"},
    {"method": "GET", "path": "/db/list", "request": null, "response": "untyped object", "state": "implemented", "evidence": "app/api/resonance.py:535-551"},
    {"method": "POST", "path": "/db/rank", "request": "ResonanceAnalysisRequest", "response": "untyped object", "state": "implemented", "evidence": "app/api/resonance.py:554-639"},
    {"method": "POST", "path": "/db/scan", "request": "ResonanceAnalysisRequest", "response": "untyped object", "state": "implemented", "evidence": "app/api/resonance.py:642-693"},
    {"method": "POST", "path": "/export/pdf", "request": "dict[str, Any]", "response": "application/pdf", "state": "implemented", "evidence": "app/api/resonance.py:696-884"},
    {"method": "POST", "path": "/emf/enable", "request": "query continuous: bool", "response": "untyped object", "state": "implemented", "evidence": "app/api/resonance.py:891-895"},
    {"method": "POST", "path": "/emf/disable", "request": null, "response": "untyped object", "state": "implemented", "evidence": "app/api/resonance.py:898-902"},
    {"method": "GET", "path": "/emf/status", "request": null, "response": "untyped object despite EMFStatusResponse definition", "state": "implemented", "evidence": "app/api/resonance.py:905-911; app/schemas/resonance.py:87-98"},
    {"method": "GET", "path": "/emf/profile", "request": null, "response": "untyped object", "state": "implemented", "evidence": "app/api/resonance.py:914-926"},
    {"method": "GET", "path": "/emf/monitor", "request": null, "response": "text/html", "state": "implemented", "evidence": "app/api/resonance.py:929-1069"},
    {"method": "GET", "path": "/amplifier/list", "request": null, "response": "untyped object", "state": "implemented", "evidence": "app/api/resonance.py:1228-1231"},
    {"method": "POST", "path": "/amplifier/set/{amplifier_name}", "request": "path parameter", "response": "untyped object", "state": "implemented", "evidence": "app/api/resonance.py:1233-1239"},
    {"method": "POST", "path": "/amplifier/clear", "request": null, "response": "untyped object", "state": "implemented", "evidence": "app/api/resonance.py:1241-1245"},
    {"method": "POST", "path": "/amplifier/match", "request": "dict", "response": "untyped object", "state": "implemented", "evidence": "app/api/resonance.py:1247-1262"},
    {"method": "POST", "path": "/amplifier/add", "request": "dict", "response": "untyped object", "state": "implemented", "evidence": "app/api/resonance.py:1264-1280"},
    {"method": "GET", "path": "/clients/safety/posture", "request": null, "response": "safety block", "state": "implemented", "evidence": "app/api/clients.py:55-58"},
    {"method": "GET", "path": "/clients", "request": null, "response": "PII-stripped list", "state": "implemented", "evidence": "app/api/clients.py:62-71"},
    {"method": "GET", "path": "/clients/{client_id}/erasure-manifest", "request": "path parameter", "response": "untyped object", "state": "implemented_with_audit_write", "evidence": "app/api/clients.py:82-91"},
    {"method": "DELETE", "path": "/clients/{client_id}?gate_token=...", "request": "path and query parameter", "response": "untyped object", "state": "implemented_destructive", "evidence": "app/api/clients.py:94-111"},
    {"method": "GET", "path": "/clients/{client_id}/audit", "request": "path parameter", "response": "AuditLogEntry[]", "state": "implemented", "evidence": "app/api/clients.py:114-118"}
  ],
  "websocket_routes": [
    {"path": "/emf/ws", "direction": "server-to-client periodic profile", "state": "implemented", "evidence": "app/api/resonance.py:1072-1119"},
    {"path": "/emf/client-sensor", "direction": "client sensor input and recommendation response", "state": "implemented", "evidence": "app/api/resonance.py:1121-1221"}
  ],
  "static_ui_routes": ["/", "/user_workflow.html", "/user_workflow.css", "/user_workflow.js"]
}
```

```json
{
  "metadata_type": "schema_definitions",
  "schemas": [
    {
      "name": "ResonanceAnalysisRequest",
      "path": "app/schemas/resonance.py:8-30",
      "required_fields": ["focus"],
      "optional_or_defaulted_fields": ["client_id", "client_data", "matrix_size", "iterations", "use_quantum", "use_cuda", "focus_weight", "calculation_mode", "hrv_sim", "emf_compensate", "use_planetary", "palette", "amplifier", "group_members", "geo_coords", "image_path", "image_base64", "db_path", "symmetry"],
      "contract_notes": ["iterations, use_quantum, and use_cuda are declared but are not forwarded by analyze_matrix_resonance to calculate_resonance", "matrix_size has no schema enum/range constraint"]
    },
    {
      "name": "ResonanceAnalysisResponse",
      "path": "app/schemas/resonance.py:55-77",
      "fields": ["analysis_id", "timestamp", "client_name", "focus", "resonance_score", "matrix_12x12", "matrix_data", "matrix_size", "matrix_colors", "resonant_patterns", "processing_time_ms", "hardware_acceleration", "emf_compensation", "amplifier", "amplifier_recommendations", "symmetry", "client_frequency_hz", "top_10", "safety"]
    },
    {
      "name": "ClientBase",
      "path": "app/schemas/klienten.py:6-18",
      "required_fields": ["first_name", "last_names", "birth_date", "birth_place"],
      "sensitive_fields": ["first_name", "last_names", "birth_date", "birth_place", "email", "phone", "address", "main_symptom", "notes", "geolocation"]
    },
    {
      "name": "Runtime JSON stores",
      "paths": ["app/models/client_registry.py:9-23", "app/models/session_archive.py:8-27", "app/models/report_manifest.py:6-17", "app/models/audit_log.py:14-28"],
      "store_files": ["data/runtime/clients.json", "data/runtime/sessions.json", "data/runtime/artifacts.json", "data/runtime/audit_log.json"]
    },
    {
      "name": "BusEnvelope",
      "path": "app/interchange_bus/envelope.py:83-130",
      "fields": ["schema_version", "message_id", "topic", "producer", "schema_ref", "subject_ref", "content_hash", "payload", "safety", "acl", "created_at_utc"],
      "safety_required_on_consume": {"real_output_enabled": false, "medical_claims": 0}
    }
  ]
}
```

## 5. Engine, data, and exportable dependency boundaries (English)

### 5.1 Algorithmic pipeline

The implemented matrix path is: request normalization -> optional precomputed group/image/geo signature -> `ClientSignatureGenerator` -> deterministic embeddings for signature/focus -> optional bio vector -> optional EMF vector modification -> random candidate matrix generation -> random projection -> cosine similarity -> Top-10 -> optional symmetry -> color grid -> HTTP response/archive. The matrix search is numerical pattern generation; the code itself does not provide a scientific or clinical validation layer.

`precision` supplies a stable seed for Torch based on first name, birth date and focus, but the calculation still depends on environment-dependent hardware/runtime behavior and some supplied modes contain time or random inputs. `quantum_active` only enables a D-Wave preparation branch; the actual solver method returns its input after placeholder comments (`app/algorithms/resonance_engine.py:1120-1155`). The commented `dwave-ocean-sdk` dependency is therefore future-only (`requirements.txt:15-16`).

The EMF component measures software proxies (timing jitter, OS RNG statistics, system load, and optional GPU numerical/timing observations) rather than a directly implemented SDR measurement. `pyrtlsdr` is commented optional and `_sdr_available` initializes false (`requirements.txt:18-19`; `app/algorithms/emf_compensator.py:107-109`). Claims of physical sensing must remain outside the implemented-status boundary.

### 5.2 Storage and export authority

| Authority | Location | Read/write behavior | State |
|---|---|---|---|
| Curated reference text databases | `db_import/**/*.txt` | listed and read by API DB operations | implemented source/reference input |
| Bio mapping | `bio_knowledge.json` | read by engine constructor | implemented source/reference input |
| Amplifier registry | `data/amplifiers.json` | consumed/mutated through generator, exact persistence behavior requires its module inspection | implemented dependency; runtime mutation boundary |
| Client registry | `data/runtime/clients.json` | raw PII and deterministic client ID | ignored runtime authority |
| Session archive | `data/runtime/sessions.json` | session/config/result summary/artifact IDs | ignored runtime authority |
| Artifact manifest | `data/runtime/artifacts.json` | arbitrary artifact paths registered by PDF flow | ignored runtime authority |
| Audit log | `data/runtime/audit_log.json` | service-level append attempt | ignored runtime authority |
| Browser storage | browser `localStorage` via UI session/history helpers | local browser persistence | implemented client-side state; unverified browser runtime |
| Generated PDF/CSV/JSON | browser download or requested server `output_path` | potentially contains PII and focus content | export boundary |
| Bus SQLite DB | externally chosen absolute path | store bootstrap, registry, poll, ack, audit | implemented but unwired / future integration |

```json
{
  "metadata_type": "exportable_dependencies",
  "python_packages_required_by_profiles": {
    "core": ["numpy", "torch", "psutil"],
    "api": ["fastapi", "uvicorn", "numpy", "torch", "pydantic", "psutil", "websockets"],
    "cli": ["numpy", "torch", "reportlab", "openpyxl", "psutil"]
  },
  "declared_packages": ["fastapi==0.104.1", "uvicorn[standard]==0.24.0", "httpx<0.28", "torch>=2.0.0", "numpy>=1.24.0", "pydantic>=2.0.0", "psutil>=5.9.0", "reportlab>=4.0.0", "openpyxl>=3.1.0", "websockets>=12.0"],
  "optional_or_future_dependencies": [
    {"name": "dwave-ocean-sdk", "state": "commented_future_only", "evidence": "requirements.txt:15-16"},
    {"name": "pyrtlsdr", "state": "commented_future_only", "evidence": "requirements.txt:18-19"},
    {"name": "Pillow/PIL", "state": "soft_optional_not_declared", "evidence": "app/algorithms/client_signature.py:198-231"},
    {"name": "shared ME2 SQLite BusDB", "state": "external_contract_unwired", "evidence": "app/interchange_bus/envelope.py:1-10; app/interchange_bus/consumer_store.py:1-10"},
    {"name": "NVIDIA CUDA / systemd / Debian", "state": "deployment_assumption", "evidence": "deploy/setup_server.sh:15-89; deploy/resonance-engine.service:1-32"}
  ],
  "outbound_network_dependencies": [
    {"name": "D-Wave", "state": "not_implemented_call_path", "evidence": "app/algorithms/resonance_engine.py:1120-1155"},
    {"name": "WebSocket clients", "state": "inbound_only_server endpoints", "evidence": "app/api/resonance.py:1072-1221"}
  ],
  "explicitly_absent_by_static_search_or_design": [
    "No Radi144 bus publish operation in BusConsumerStore",
    "No configured external API client in requirements or main router wiring",
    "No implemented RTL-SDR adapter",
    "No backend harmonization worker reached by user_workflow.js"
  ]
}
```

## 6. Befundregister und strategische Optimierungsgates

Die Schweregrade bedeuten: `hoch` = Blocker für Exposition, reale Daten oder Freigabe; `mittel` = vor einer stabilen operativen Erweiterung schließen; `niedrig` = gezielt nach den Schutzgates behandeln. Jeder Befund bleibt an den geprüften Dateistand gebunden.

| ID | Schwere | Statischer Befund (English) | Deutsche Maßnahme | Evidenz |
|---|---|---|---|---|
| F-01 | hoch | `API_KEY` protection is default-off, and HTTP middleware does not govern WebSocket handshakes. Both WebSocket handlers accept a connection without an authorization/tenant check and can mutate global EMF state. | Vor jeder nicht-loopback Bindung ein einheitliches Authentifizierungs- und Autorisierungskonzept für HTTP, WebSocket und Löschung festlegen; fehlende Autorität muss fail-closed sein. | `main.py:78-107`; `app/api/resonance.py:1072-1221` |
| F-02 | hoch | `image_path` and `db_path` accept absolute paths; `_resolve_existing_path` returns any existing regular file. `/db/list` and ranking responses disclose absolute paths. `/export/pdf` resolves and writes caller-controlled absolute output paths. | Alle Dateioperationen auf serverseitig erzeugte, zweckgebundene IDs und erlaubte Wurzeln umstellen; absolute Pfade weder akzeptieren noch zurückgeben. Read/Write/Erase getrennt testen. | `app/api/resonance.py:128-135,212-228,535-551,624-627,643-693,864-874` |
| F-03 | hoch | A process-global engine contains mutable amplifier and EMF state. Request-level amplifier state is saved/restored, but concurrent requests and global EMF enable/disable/client-sensor writes have no isolation or lock boundary. | Vor Parallel- oder Mehrbenutzerbetrieb eine explizite Session-/Request-Engine-Grenze und Nebenläufigkeitsstrategie einführen; globalen fachlichen Zustand nicht als Mandantenautorität verwenden. | `app/api/resonance.py:27-33,185-200,891-902,1121-1221`; `app/algorithms/resonance_engine.py:122-129` |
| F-04 | hoch | Matrix size is described but not bounded in the request schema. Computational routes execute synchronous Torch work in async handlers and have no request budget, queue, timeout, admission policy, or per-actor rate limit. The engine memory guard is partial and documented historical evidence records OOM/native failure for real engine checks. | Zuerst ein deterministisches kleines Ressourcenprofil mit hard input bounds, Budget, Cancel-/Timeout-Semantik und Lasttestvertrag definieren; erst danach externe Bindung oder Vollsuite. | `app/schemas/resonance.py:12-13`; `app/api/resonance.py:413-466,554-639,642-693`; `app/algorithms/resonance_engine.py:999-1111`; `docs/Radi144_Projektuebergabe_2026-07-24/README.md:90-102` |
| F-05 | hoch | Runtime JSON stores use load-modify-save plus atomic replace but no cross-process locking, transaction spanning stores, durable fsync protocol, version migration, or integrity anchor. Erasure performs independent destructive steps, so a failure can leave partial state. | Persistenz- und Löschgrenze zuerst als atomaren, wiederaufnehmbaren Transaktionsvertrag modellieren; Crash-, Parallel- und Teilfehler-RED-Tests vor Migration schreiben. | `app/services/json_store.py:19-36`; `app/services/erasure_service.py:178-243` |
| F-06 | hoch | Raw PII/health-adjacent fields are accepted and retained in local JSON; safe projection is endpoint-specific and does not protect analysis responses, PDFs, browser downloads, error strings, runtime files, or browser storage. | Datenminimierung, Retention, Verschlüsselungs-/Berechtigungsgrenze und Exportklassifikation als eigenen Privacy-Gate schließen; reale Daten bis dahin gesperrt lassen. | `app/schemas/klienten.py:6-18`; `app/models/client_registry.py:9-18`; `app/services/safety_service.py:49-77`; `user_workflow.js:1207-1251,1254-1304` |
| F-07 | hoch | The erasure gate defaults to the public constant `R144_ERASURE_ACKNOWLEDGED`; manifest and audit endpoints expose client-linked metadata. The audit service treats write failure as non-fatal and an append-only claim is not DB-/cryptographically enforced. | Erasure-Autorisierung aus einem echten, rotierbaren Operator-Kontext ableiten; Audit als fehlertolerante Beobachtung nicht als forensische Autorität deklarieren, bis eine attestierbare Autorität existiert. | `app/services/erasure_service.py:30-35,103-146`; `app/services/audit_service.py:51-69`; `app/api/clients.py:82-118` |
| F-08 | hoch | The UI injects focus, client name, and some result-derived values using `innerHTML`; those fields derive from local input and API response. This is a static reflected/stored DOM-XSS boundary unless every value is constrained/encoded before use. | UI-Rendering auf text nodes bzw. kontextgerechte Encodierung umstellen und mit bösartigen Namen/Fokuswerten browsernah absichern. Keine kosmetische Sanitizer-Annahme ohne RED-Test. | `user_workflow.js:1006-1054,1101-1150,1207-1238,1654-1671` |
| F-09 | hoch | The non-medical safety block is additive, while source/UI vocabulary and EMF constants still contain diagnosis/therapy/healing-adjacent semantics. The repository has no scientific validation layer; D-Wave is a mock and SDR is unimplemented. | Produktzweck, UI-Texte, PDF-Text, Datenquellen und Integrationsverträge gegen eine verbindliche Claim-Taxonomie prüfen; keine Wirksamkeits- oder Hardwareaussage aus Codekommentaren ableiten. | `app/services/safety_service.py:21-44`; `app/algorithms/emf_compensator.py:1-13,52-63`; `app/algorithms/resonance_engine.py:1120-1155`; `user_workflow.js:62-75` |
| F-10 | mittel | Request fields `iterations`, `use_quantum`, and `use_cuda` are declared but not consumed by `analyze_matrix_resonance -> calculate_resonance`; `quantum_active` is distinct from request `use_quantum`. This is an API contract drift/latent-control boundary. | Öffentliche Felder in aktiviert, latent oder entfernt klassifizieren; jede aktiv behauptete Option bis zur konkreten Laufzeitwirkung und Antworttrace nachweisen. | `app/schemas/resonance.py:12-22`; `app/api/resonance.py:441-452`; `app/algorithms/resonance_engine.py:40,109-116,243-255` |
| F-11 | mittel | Precision RNG restoration occurs only after successful result construction; exception paths after manual seeding can skip restoration. Group signature generation also mutates supplied member dictionaries by adding `birth_place`. | Determinismus als vollständigen Erfolgs- und Fehlerpfadvertrag testen; Eingaben an der Algorithmusgrenze kopieren oder als unveränderlich behandeln. | `app/algorithms/resonance_engine.py:282-303,481-484`; `app/algorithms/client_signature.py:131-159` |
| F-12 | mittel | The bus consumer constructor creates directories, SQLite schema/WAL state, registry rows and audit entries. It is explicitly unwired, but it is not a read-only adapter and has no application activation authority. | Bus nur in einem späteren, separat genehmigten Integrationsgate aktivieren; DB-Pfad, Rechte, Producer-Vertrauen, ACL-Auswertung, Replay, Retention und Recovery vorher verbindlich testen. | `app/interchange_bus/consumer_store.py:91-119,122-140`; `app/services/bus_consumer_service.py:122-145` |
| F-13 | mittel | The envelope’s self-hash detects accidental/inconsistent payload changes but is not an independent signature or external tamper anchor; `content_hash` is computed yet consumer verification only checks `message_id`. | Integritätsversprechen auf „self-consistency“ begrenzen, bis Schlüsselverwaltung und externe/signierte Attestierung entschieden und getestet sind. | `app/interchange_bus/envelope.py:54-60,91,123-130,165-180`; `app/services/bus_consumer_service.py:84-100` |
| F-14 | mittel | The PDF route manually validates only a portion of its untyped payload and returns detailed exception strings from analysis failure. Error and export schemas are therefore not stable privacy-safe contracts. | PDF- und Fehlervertrag mit Pydantic-Modellen, zulässigen Feldern, redigierten Fehlern und einer klaren Server-vs-Browser-Exportentscheidung festlegen. | `app/api/resonance.py:462-466,696-884` |
| F-15 | mittel | Deployment metadata differs from current defaults: setup output advertises port 8000, while the app defaults to 8090; service write paths do not directly model arbitrary caller-selected PDF destinations. | Deployment erst nach Konfigurations-SSOT, least-privilege Pfadautorität und reproduzierbarem Installations-/Smoke-Vertrag korrigieren. | `main.py:124-142`; `deploy/setup_server.sh:96-100`; `deploy/resonance-engine.service:11-22` |
| F-16 | niedrig | `EMFStatusResponse` exists but `/emf/status` has no response model; several amplifier/export routes use raw dictionaries. | Nach den Schutzgates die OpenAPI-Verträge vervollständigen und kompatibilitätsgebunden testen. | `app/schemas/resonance.py:87-98`; `app/api/resonance.py:905-911,1247-1280` |
| F-17 | niedrig | Pillow is optionally imported for image color analysis but not declared in requirements; behavior degrades silently to hash/name components. | Optionalität explizit machen: dependency profile, capability response und Testfall für mit/ohne Pillow. | `app/algorithms/client_signature.py:195-231`; `requirements.txt:1-19` |

```json
{
  "metadata_type": "findings",
  "findings": [
    {"id": "F-01", "severity": "high", "state": "implemented_risk", "evidence_paths": ["main.py", "app/api/resonance.py"], "gate": "G1"},
    {"id": "F-02", "severity": "high", "state": "implemented_risk", "evidence_paths": ["app/api/resonance.py"], "gate": "G2"},
    {"id": "F-03", "severity": "high", "state": "static_inference", "evidence_paths": ["app/api/resonance.py", "app/algorithms/resonance_engine.py"], "gate": "G3"},
    {"id": "F-04", "severity": "high", "state": "static_inference_with_historical_documentary_evidence", "evidence_paths": ["app/schemas/resonance.py", "app/api/resonance.py", "app/algorithms/resonance_engine.py", "docs/Radi144_Projektuebergabe_2026-07-24/README.md"], "gate": "G4"},
    {"id": "F-05", "severity": "high", "state": "implemented_risk", "evidence_paths": ["app/services/json_store.py", "app/services/erasure_service.py"], "gate": "G5"},
    {"id": "F-06", "severity": "high", "state": "implemented_risk", "evidence_paths": ["app/schemas/klienten.py", "app/services/safety_service.py", "user_workflow.js"], "gate": "G6"},
    {"id": "F-07", "severity": "high", "state": "implemented_risk", "evidence_paths": ["app/services/erasure_service.py", "app/services/audit_service.py", "app/api/clients.py"], "gate": "G5"},
    {"id": "F-08", "severity": "high", "state": "static_inference", "evidence_paths": ["user_workflow.js"], "gate": "G2"},
    {"id": "F-09", "severity": "high", "state": "implemented_and_future_only_mixed", "evidence_paths": ["app/services/safety_service.py", "app/algorithms/emf_compensator.py", "app/algorithms/resonance_engine.py", "user_workflow.js"], "gate": "G0"},
    {"id": "F-10", "severity": "medium", "state": "implemented_contract_drift", "evidence_paths": ["app/schemas/resonance.py", "app/api/resonance.py", "app/algorithms/resonance_engine.py"], "gate": "G7"},
    {"id": "F-11", "severity": "medium", "state": "static_inference", "evidence_paths": ["app/algorithms/resonance_engine.py", "app/algorithms/client_signature.py"], "gate": "G4"},
    {"id": "F-12", "severity": "medium", "state": "implemented_but_unwired", "evidence_paths": ["app/interchange_bus/consumer_store.py", "app/services/bus_consumer_service.py"], "gate": "G8"},
    {"id": "F-13", "severity": "medium", "state": "implemented_contract_limit", "evidence_paths": ["app/interchange_bus/envelope.py", "app/services/bus_consumer_service.py"], "gate": "G8"},
    {"id": "F-14", "severity": "medium", "state": "implemented_contract_drift", "evidence_paths": ["app/api/resonance.py"], "gate": "G7"},
    {"id": "F-15", "severity": "medium", "state": "documented_vs_implemented_drift", "evidence_paths": ["main.py", "deploy/setup_server.sh", "deploy/resonance-engine.service"], "gate": "G9"},
    {"id": "F-16", "severity": "low", "state": "implemented_contract_gap", "evidence_paths": ["app/schemas/resonance.py", "app/api/resonance.py"], "gate": "G7"},
    {"id": "F-17", "severity": "low", "state": "optional_dependency_gap", "evidence_paths": ["app/algorithms/client_signature.py", "requirements.txt"], "gate": "G9"}
  ]
}
```

## 7. Priorisierter Umsetzungsplan

### G0 — Zweck-, Claim- und Freigabe-Sperre

Ziel: Die aktuelle lokale, nicht-medizinische und nicht-produktive Grenze maschinen- und testbar festschreiben, ohne Algorithmik zu verändern.

1. Eine einzige normative Claim-/Produktzweckquelle gegen UI, PDF, API, Bus und Deploy-Dokumente abgleichen.
2. `implemented`, `future-only`, `documented` und `unverified-runtime` für EMF, SDR, D-Wave, Harmonizer und Bus explizit separieren.
3. Stop-Kriterium: Jede reale Daten-, Hardware-, Cloud-, Bus-, Pilot- oder Produktionsaktivierung bleibt bis zu schriftlicher Gatefreigabe verboten.

Akzeptanz: Keine Komponente wird aufgrund eines Kommentars, eines UI-Labels oder eines optionalen Imports als aktiv bezeichnet.

### G1 — Einheitliche Zugriffsautorität

Ziel: Eine Default-deny Autorität für HTTP, WebSocket, destruktive Operationen und sensible Lesepfade schaffen.

1. Den Einsatzmodus explizit wählen: ausschließlich loopback single operator oder authentifiziertes Mehrbenutzersystem. Nicht beide implizit bedienen.
2. Authentisierung, Rollen, Tenant-/Subject-Bindung, Origin/Host/CORS/CSRF-Regeln sowie Secret-Rotation als konkreten Vertrag definieren.
3. HTTP- und WebSocket-Handshake gegen denselben Autoritätskontext prüfen; fehlende, beschädigte oder abgelaufene Autorität muss ablehnen.
4. RED-Tests für ungültige Header, WebSocket ohne Autorität, abgelaufene Credentials, Cross-Origin und Löschversuch hinzufügen.

Akzeptanz: F-01 ist durch nachweisbare, gleichartige Negativtests in allen Transporten geschlossen.

### G2 — Capability-bound Dateien und browserseitige Ausgabesicherheit

Ziel: Kein externer Request darf einen Hostpfad lesen, schreiben, löschen oder offenlegen können; DOM-Ausgabe darf keinen untrusted HTML-Kontext verwenden.

1. Pfadstrings durch serverseitig erzeugte, kurzlebige Ressourcen-IDs ersetzen; jede ID an Zweck, Besitzer, erlaubte Wurzel, Lebensdauer und Inhaltstyp binden.
2. DB-Katalog nur mit relativen, nicht sensitiven Identifikatoren ausgeben.
3. PDF ausschließlich als kontrollierter Download oder als serverseitig erzeugtes Artefakt in einer fest gebundenen Exportwurzel behandeln — nicht beides ungebunden vermischen.
4. Alle UI-Ausgaben für Name, Fokus, Fehler, EMF und Antworten auf textContent/DOM-Knoten oder kontextbewiesene Kodierung umstellen.
5. RED-Tests: absolute Pfade, Traversal, Symlink/Race-Szenarien, fremde Artefakt-ID, HTML-/Script-Payloads in allen sichtbaren Feldern.

Akzeptanz: F-02 und F-08 schließen mit browsernaher Payload-Evidenz, nicht nur String-Suchen.

### G3 — Engine-Instanz-, Nebenläufigkeits- und Sessiongrenze

Ziel: Fachlicher Zustand wird pro Request/Session autoritativ und nicht über globale Variablen geteilt.

1. Alle mutablen Felder (`emf_compensator`, `emf_active`, Amplifier, HRV-Status, RNG-bezogene Zustände) samt Lesern/Schreibern inventarisieren.
2. Eine Ein-Engine-pro-Request oder eine strikt serialisierte Single-Operator-Strategie entscheiden; Default- und Wiederanlaufverhalten dokumentieren.
3. Client-Sensor-Eingaben typisieren, begrenzen, Eigentümer binden und außerhalb globaler Enginefelder speichern.
4. Parallel-, Abbruch- und Restore-Tests schreiben, die Zustandstrennung beweisen.

Akzeptanz: F-03 schließt ohne implizite globale Cross-Request-Wirkung.

### G4 — Ressourcen- und Determinismusbaseline

Ziel: Der Enginekern bleibt charakterisiert, begrenzt und im Fehlerfall zustandskorrekt.

1. Zuerst eine hashgebundene Golden-Baseline mit kleinen deterministischen Eingaben und expliziten Ressourcenlimits erzeugen.
2. Matrixgröße, Kandidatenzahl, Uploadgröße, DB-Scanmenge, Fokuszahl und Requestdauer als harte Verträge festlegen.
3. Jede RNG-Manipulation über `try/finally` bzw. einen äquivalenten vollständigen Restaurationsvertrag führen; mutable Eingaben kopieren.
4. OOM, native Abbruch, Cancel, CPU/GPU-Fallback und Fehlerpfad isoliert auf einer nichtautoritativen Arbeitskopie testen.

Akzeptanz: F-04 und F-11 schließen erst bei reproduzierbarer Erfolg-/Fehlerpfad-Evidenz; historische OOM-Dokumentation wird nicht als behoben umgedeutet.

### G5 — Transaktionale Runtime-Daten, Löschung und Auditgrenze

Ziel: Client, Session, Artefakt, Datei und Audit besitzen eine konsistente, recovery-fähige Lebenszyklusautorität.

1. Vor einer Speicherung die Datenklassifikation, Retention, Export- und Backupgrenze festlegen.
2. Eine transaktionale/kompensierbare Kaskade mit Crash-Recovery, eindeutigen Zuständen und einer unveränderlichen Löschquittung entwerfen.
3. Den Standard-Löschtoken entfernen; Operatorautorisierung und Auditfehlerpolitik ausdrücklich machen.
4. „Append-only“ nur behaupten, wenn Speicher- und Integritätsmodell das erzwingen; andernfalls korrekt als Best-effort Journal bezeichnen.
5. RED-Tests für jeden Teilfehler zwischen Registry, Session, Manifest, Datei, Verzeichnis und Audit ausführen.

Akzeptanz: F-05, F-06 und F-07 schließen mit vollständigem Nachweis aller Teilfehler- und Wiederanlaufpfade.

### G6 — Privacy-by-design und Exportkontrolle

Ziel: Roh-PII, sensible Fokusdaten und Analyseergebnisse werden entlang ihrer gesamten Lebensdauer minimiert und kontrolliert.

1. Datenfelder je Eingang, Arbeitsspeicher, Runtime-Store, API-Antwort, UI, Download, PDF, Log und Backup klassifizieren.
2. Nur tatsächlich benötigte Felder in Signatur/Archiv vorhalten; Pseudonymisierung nicht mit Anonymisierung verwechseln.
3. Exportfreigabe, Löschbarkeit und lokale Browserpersistenz sichtbar und konsistent machen.
4. Reale Klientendaten erst nach einer unabhängigen Privacy-/Regulatory-Freigabe zulassen.

Akzeptanz: Kein Safe-View-Endpunkt wird als Gesamtschutz ausgegeben, solange andere Datenpfade Rohdaten führen.

### G7 — API- und Fehlervertragskonsolidierung

Ziel: Öffentliche Felder, Responses, Fehler und aktivierte Optionen sind vollständig typisiert und wahrheitsgemäß.

1. `iterations`, `use_quantum`, `use_cuda`, `EMFStatusResponse` und sämtliche raw-dict-Routen klassifizieren: implementieren, als latent ausweisen oder entfernen.
2. PDF-, Amplifier-, DB- und Fehlerpayloads als Pydantic-Modelle mit Größen-/Typ-/Enumgrenzen modellieren.
3. Keine internen Exceptiondetails an Clients ausgeben; korrelierbare, redigierte Fehler plus sichere Serverdiagnostik definieren.
4. OpenAPI- und Frontend-Vertrag mit Negativfällen und Rückwärtskompatibilität testen.

Akzeptanz: F-10, F-14 und F-16 schließen ohne „sichtbares Feld ohne Runtime-Wirkung“.

### G8 — Bus nur als separates, offline-first Integrationsgate

Ziel: Die vorhandene Consumer-Vorbereitung bleibt getrennt von der Radi144-Engine und erhält erst nach Sicherheits-/Betriebsgates eine Aktivierungsentscheidung.

1. Absoluten Bus-DB-Pfad, Dateibesitzer, Prozesse, ACL-Auswertung, Producer-Identität, Replay, Cursor, Quarantäne, Retention und Backup als expliziten Vertrag definieren.
2. Schema-Bootstrap als schreibende Aktivierung behandeln und auf nichtautoritative Testdaten begrenzen.
3. `message_id`-Self-Consistency, `content_hash`, Authentizität und externe Attestierung klar getrennt bewerten.
4. Keine direkte Bus-zu-Engine-Kopplung ohne isolierten Preview-/Adapter-/Rollback-Gate.

Akzeptanz: F-12 und F-13 schließen nicht durch Dokumentation, sondern durch getrennte Ownership-, Tamper-, Replay- und Recovery-Evidenz.

### G9 — Reproduzierbarer Betrieb und optionale Fähigkeiten

Ziel: Deployment, Abhängigkeiten und Capability-Anzeige stimmen mit dem implementierten Verhalten überein.

1. Einen Konfigurations-SSOT für Port, Host, Worker, Exportwurzel, CORS, API-Key und Runtimepfade festlegen.
2. `setup_server.sh`, systemd-Unit, README und UI gegen diese Autorität abgleichen; keine mutierende Setupausführung in der Entwurfsphase.
3. Pillow, CUDA, D-Wave und SDR als explizite Capabilities statt stiller Fallbacks modellieren.
4. Reproduzierbaren Build/Install/Smoke nur auf einer separaten Arbeitskopie durchführen.

Akzeptanz: F-15 und F-17 schließen mit dokumentierter und tatsächlich ausführbarer, aber nicht produktiver Umgebungsevidenz.

```json
{
  "metadata_type": "gate_dependency_dag",
  "gates": [
    {"id": "G0", "name": "Claim and release boundary", "depends_on": [], "closes": ["F-09"], "may_run_in_parallel_with": ["G1", "G2", "G4"]},
    {"id": "G1", "name": "Unified access authority", "depends_on": ["G0"], "closes": ["F-01"], "may_run_in_parallel_with": ["G2", "G4"]},
    {"id": "G2", "name": "Capability-bound files and DOM output", "depends_on": ["G0"], "closes": ["F-02", "F-08"], "may_run_in_parallel_with": ["G1", "G4"]},
    {"id": "G3", "name": "Engine state isolation", "depends_on": ["G1", "G2", "G4"], "closes": ["F-03"], "may_run_in_parallel_with": ["G5"]},
    {"id": "G4", "name": "Resource and determinism baseline", "depends_on": ["G0"], "closes": ["F-04", "F-11"], "may_run_in_parallel_with": ["G1", "G2"]},
    {"id": "G5", "name": "Transactional lifecycle and erasure", "depends_on": ["G1", "G2"], "closes": ["F-05", "F-07"], "may_run_in_parallel_with": ["G3"]},
    {"id": "G6", "name": "Privacy and export control", "depends_on": ["G1", "G2", "G5"], "closes": ["F-06"], "may_run_in_parallel_with": ["G7"]},
    {"id": "G7", "name": "API contract consolidation", "depends_on": ["G1", "G2", "G4"], "closes": ["F-10", "F-14", "F-16"], "may_run_in_parallel_with": ["G6"]},
    {"id": "G8", "name": "Offline-first bus integration", "depends_on": ["G0", "G1", "G5", "G6", "G7"], "closes": ["F-12", "F-13"], "may_run_in_parallel_with": ["G9"]},
    {"id": "G9", "name": "Reproducible operation and capabilities", "depends_on": ["G4", "G7"], "closes": ["F-15", "F-17"], "may_run_in_parallel_with": ["G8"]}
  ]
}
```

## 8. No-go boundaries and approval checkpoint

Die folgenden Grenzen sind nicht als Optimierungsvorschlag, sondern als fortgeltende Sperre zu behandeln:

- Keine Änderung an Score, Signaturgewichtung, Kandidatensuche, Matrixauswahl, Farbsemantik oder fachlicher Enginewirkung vor G4-Golden-Baseline und separater Genehmigung.
- Keine externe Bindung, Mehrbenutzerbetrieb, WebSocket-Exposition, reale Klientendaten, Pilot, Produktion oder Cloudintegration vor G0, G1, G2, G5 und G6.
- Keine direkte Bus-zu-Engine-Kopplung, kein ME2-/Radiquant-/Lovable-Gateway und keine reale BusDB-Aktivierung vor G8.
- Keine D-Wave-, SDR- oder Hardwarewirkung als implementiert oder validiert behandeln, solange die Abhängigkeits-, Adapter-, Authentizitäts- und Messgrenzen nicht separat geschlossen sind.
- Keine Lösch- oder Audit-Compliance behaupten, solange Teilausfall, Backup, Recovery, Autorität und Unveränderlichkeit nicht nachgewiesen sind.

```json
{
  "metadata_type": "no_go_boundaries",
  "status": "NO_GO_PENDING_APPROVAL",
  "blocked_operations": [
    "production_deployment",
    "external_network_exposure",
    "multi_user_activation",
    "real_client_data_processing",
    "clinical_or_effectiveness_claim",
    "direct_bus_to_engine_wiring",
    "real_hardware_or_sdr_claim",
    "d_wave_activation",
    "score_or_signature_semantic_change"
  ],
  "earliest_permissible_next_gate": "G0",
  "approval_required_before": ["source_code_change", "configuration_change", "test_execution_that_mutates_project_runtime_state", "server_start", "commit", "deployment"]
}
```

## 9. Review limits and evidence discipline (English)

- This report preserves observed distinctions rather than claiming an unverifiable absolute “loss-free” property. States used here are `implemented`, `implemented_but_unwired`, `implemented_with_future_hardware_boundary`, `documented`, `future-only`, `static-inference`, `unverified-runtime`, and `absent-by-design/search-scope`.
- Static source review cannot prove successful imports, package compatibility, GPU availability, port availability, browser behavior, concurrency behavior, PDF bytes, schema migrations, external path permissions, data contents, or the historical test results beyond their documentary status.
- Existing handoff/audit documents were treated as dated documentary evidence, not as replacement for current source evidence. The live snapshot differs from the July handoff branch/HEAD; this report binds its source claims to the snapshot in Section 1.
- Ignored and potentially sensitive roots were not opened. Their existence and `.gitignore` classification are boundaries, not evidence of their contents.
- The bus code was classified from static constructors and module wiring. No BusConsumerStore instance was constructed, because doing so would create directories, SQLite schema/WAL state, registry rows, and audit state.

## 10. Freigabeentscheidung

Status: `NO_GO_PENDING_APPROVAL`.

Dieses Dokument ist ein Plan- und Architekturartefakt, keine Implementierungsfreigabe. Der nächste zulässige Schritt ist ausschließlich die explizite Nutzerfreigabe für G0 oder für einen enger definierten, hashgebundenen Read-only-Vertiefungsgate. Bis dahin stoppen.
