# RadiWorks — Strategischer Optimierungsplan 2

## Verbindlicher Plattformvertrag

**Zielbetriebssystem: Ubuntu Server 24.04.4 LTS.** Dieser Parameter ist für alle
folgenden Architektur-, Laufzeit-, Deployment- und Verifikationsentscheidungen
verbindlich; abweichende Hostsysteme sind ausschließlich Entwicklungsumgebungen.

## Prüfmodus, Aussagegrenzen und Freigabestatus

Diese Bewertung ist eine **strikte statische, read-only Architekturprüfung** des aktuellen Arbeitsbaums. Es wurden weder Python-Module importiert noch Tests, Server, Migrationen, Browser, Netzwerk- oder Build-Schritte ausgeführt. Deshalb sind Aussagen über Startfähigkeit, Testgrünheit, Nebenwirkungen unter Last, Browser-Kompatibilität, Java-Parität und Recovery-Verhalten **unverified-runtime**, nicht bestanden oder fehlgeschlagen.

Die angeforderte Datei ist die einzige erzeugte Arbeitsbaumdatei. „Loss-free“ wird nicht als unbeweisbare Absolute behauptet: beobachtete Implementierung, dokumentierte Absicht, statische Schlussfolgerung, nicht geprüfte Laufzeit, ausgeschlossene Wurzeln und durch Suche nicht belegte Komponenten bleiben getrennt erhalten.

**Freigabestatus: NO-GO für Implementierung.** Zuerst ist die Entscheidung über die priorisierten Gates erforderlich. Der früheste zulässige Umsetzungsschritt ist **G0: Snapshot- und Vertragsfrierung**; kein Commit, keine Bereinigung, keine Datenmigration und keine Produktfunktionsänderung sind durch dieses Dokument autorisiert.

```json
{
  "metadata_type": "review_snapshot",
  "review_mode": "strict-static-read-only",
  "repository_root": "C:/Users/Hubert111/Documents/Radiworks",
  "application_boundary": "radiworks_port",
  "branch": "main",
  "head": "067b1142ec02f4db3b590b1d9e4c8cbc7c578284",
  "source_manifest_sha256": "8784ca6ea870dcabc481e3263679f64da00eb0e360bf56b42a09e42383451602",
  "initial_status_all_count": 60,
  "tracked_subtree_diff": {"files_changed": 39, "insertions": 4600, "deletions": 920},
  "reviewed_roots": [
    "radiworks_port/engine/src/radiworks",
    "radiworks_port/engine/tests",
    "radiworks_port/engine/pyproject.toml",
    "radiworks_port/engine/README.md",
    "radiworks_port/webapp",
    "radiworks_port/README.md",
    "radiworks_port/ROADMAP.md",
    ".gitignore"
  ],
  "excluded_roots": [
    {"path": ".git", "reason": "version-control internals"},
    {"path": "_archive", "reason": "ignored archives; not opened to avoid operational/confidential content"},
    {"path": "radiworks_port/engine/.venv", "reason": "ignored dependency environment"},
    {"path": "radiworks_port/engine/radiworks_home", "reason": "runtime/operator data; inventory only, no payload inspection"},
    {"path": "decompiled", "reason": "reference/decompiled Java context, not current port implementation"}
  ],
  "non_executed": ["tests", "imports", "FastAPI startup", "WebSocket handshake", "browser UI", "network", "migration", "Java Gold harness"],
  "report_path": "project_memories/strategy_project_2.md"
}
```

## Management Summary (Deutsch)

RadiWorks ist ein lokaler Python/FastAPI-Prototyp mit einer Vanilla-JavaScript-Webapp. Der funktionsfähige Kern ist klar erkennbar: Ratenkatalog → Entropieprovider → Analyse → Passport → Draft → optional fallgebundene Session → kontrollierte Broadcast-Queue → WebSocket-Events. Die Architektur enthält bereits belastbare Schutzabsichten: seeded als Standard, getrenntes Runtime-Home, atomare JSON-Ersetzung, Recovery-Marker, Draft-Statusmaschine, CopyGuard und explizit nicht hardware-aktivierbare Broadcasts.

Der aktuelle Arbeitsbaum ist jedoch eine große, nicht eingefrorene Integrationsfläche. In `radiworks_port` liegen 39 geänderte getrackte Dateien sowie relevante ungetrackte Produktions- und Testdateien. Parallel existieren implementierte lokale globale Zustände und vorbereitete, aber nicht in `create_app()` verdrahtete Scope-/Workspace-Abstraktionen. Das ist der wichtigste Architekturpunkt: Eine sichtbare Mandanten-/Job-Isolationssemantik ist im Code vorhanden, aber nach statischer Tracing-Evidenz nicht Authority des produktiven API-Pfads.

Die nächsten Optimierungen sollen nicht als Refactor-Batch erfolgen. Zuerst werden Verträge, Autoritäten, Runtime-Fakten und UI/API-Basisadressen eingefroren. Anschließend kann die Isolation mit einem einzigen Authority-Pfad geschlossen werden. Persistenz- und Entropie-Integrität bleiben dabei additive, rückwärtskompatible Gates.

## System Map (English)

### Runtime topology

```text
Browser document (webapp/index.html)
  -> ES module bootstrap (webapp/js/boot.js)
     -> API client + websocket reconnect (webapp/js/api.js)
     -> view modules and EventTarget event bus
  -> REST / WebSocket
FastAPI factory (engine/src/radiworks/main.py:create_app)
  -> AppState (routes.py)
     -> RateRepository / MateriaMedica (read catalog)
     -> EntropyProvider (seeded | stochastic)
     -> Analysis, GV, StickPad, Script, Images
     -> CaseStore + DraftStore + RecoveryCoordinator (runtime JSON authority)
     -> BroadcastManager + AutoModeController (in-memory worker authority)
  -> static webapp mount only when webapp_dir is explicitly supplied
Runtime roots:
  writable: RADIOWORKS_HOME or ~/.radiworks
  read catalog: RADIOWORKS_DATA_DIR or <runtime_home>/data
```

### Implemented boundary classification

| Boundary | State | Authority / evidence | Notes |
|---|---|---|---|
| HTTP application factory | implemented | `engine/src/radiworks/main.py:88-234` | Explicit injectable directories and CORS origins. |
| REST API | implemented | `engine/src/radiworks/api/routes.py:475-1414` | Router is the observable API authority. |
| WebSocket v1 event stream | implemented | `routes.py:67-315`, `1425-1572` | In-memory history; reconnect and replay-gap protocol. |
| Analysis algorithm | implemented | `core/analysis.py:154-221` | Java-order emulation is used by default; parity claim remains bounded. |
| Entropy abstraction | implemented | `entropy.py:123-254` | Seeded and stochastic source chain. |
| Case/Draft persistence | implemented | `core/cases.py`, `core/draft.py`, `persistence.py` | JSON files, atomic replacement and recovery markers. |
| Scope isolation integration | static-inference: disconnected | `scope.py:24-78`, `workflow.py:24-59`; absent from `main.py:88-234` imports/construction | Prepared abstraction is not the active API authority. |
| Hardware emission | absent-by-design | `core/broadcast.py:8-14`, `manifest.py` contract documentation | Broadcast emits simulation/event payloads; physical activation is future integration. |
| Full external Aurelia contract corpus | excluded/absent-in-tree | documented references in README/comments | `Modul_Templates` and cited `docs/*` are not present under this repository root. |

```json
{
  "metadata_type": "dependency_graph",
  "nodes": [
    {"id":"web.document","path":"radiworks_port/webapp/index.html","state":"implemented"},
    {"id":"web.bootstrap","path":"radiworks_port/webapp/js/boot.js","state":"implemented"},
    {"id":"web.api","path":"radiworks_port/webapp/js/api.js","state":"implemented"},
    {"id":"api.factory","path":"radiworks_port/engine/src/radiworks/main.py","symbol":"create_app","state":"implemented"},
    {"id":"api.router","path":"radiworks_port/engine/src/radiworks/api/routes.py","symbol":"build_router","state":"implemented"},
    {"id":"analysis","path":"radiworks_port/engine/src/radiworks/core/analysis.py","symbol":"analyse_rate_list","state":"implemented"},
    {"id":"entropy","path":"radiworks_port/engine/src/radiworks/entropy.py","symbol":"EntropyProvider","state":"implemented"},
    {"id":"drafts","path":"radiworks_port/engine/src/radiworks/core/draft.py","symbol":"DraftStore","state":"implemented"},
    {"id":"cases","path":"radiworks_port/engine/src/radiworks/core/cases.py","symbol":"CaseStore","state":"implemented"},
    {"id":"recovery","path":"radiworks_port/engine/src/radiworks/persistence.py","symbol":"RecoveryCoordinator","state":"implemented"},
    {"id":"broadcast","path":"radiworks_port/engine/src/radiworks/core/broadcast.py","symbol":"BroadcastManager","state":"implemented"},
    {"id":"automode","path":"radiworks_port/engine/src/radiworks/core/automode.py","symbol":"AutoModeController","state":"implemented"},
    {"id":"scope","path":"radiworks_port/engine/src/radiworks/scope.py","symbol":"ScopeResolver","state":"implemented-not-wired"},
    {"id":"workspace","path":"radiworks_port/engine/src/radiworks/workflow.py","symbol":"WorkflowRegistry","state":"implemented-not-wired"}
  ],
  "edges": [
    ["web.document","web.bootstrap"], ["web.bootstrap","web.api"], ["web.api","api.router"],
    ["api.factory","api.router"], ["api.router","analysis"], ["api.router","entropy"],
    ["api.router","drafts"], ["api.router","cases"], ["api.router","recovery"],
    ["api.router","broadcast"], ["api.factory","automode"], ["automode","analysis"],
    ["automode","broadcast"], ["analysis","entropy"], ["drafts","recovery"], ["cases","recovery"]
  ],
  "exportable_dependencies": [
    "FastAPI >=0.115", "uvicorn >=0.32", "websockets >=13", "httpx >=0.27", "cryptography >=43", "pytest >=8.0 (dev)",
    "Browser APIs: fetch, WebSocket, Web Crypto, MediaDevices, Canvas, Clipboard, AudioContext"
  ]
}
```

## Core Invariants and Authority Boundaries (English)

### Invariants that must survive optimization

| ID | Invariant | Evidence | State |
|---|---|---|---|
| INV-01 | `seeded` is the reproducible default; only `seeded` and `stochastic` are accepted. | `entropy.py:20,123-147`; `routes.py:129-161,449-469` | implemented |
| INV-02 | A seeded analysis is bounded by `max_hits in {100,1000}` and result is sorted then limited to 105 entries. | `analysis.py:17-21,154-221`; `routes.py:351-364` | implemented |
| INV-03 | Analysis result wire keys are camelCase and reconstructable from persisted JSON. | `analysis.py:51-62,73-111` | implemented |
| INV-04 | Draft lifecycle is a directed state machine; promotion rechecks CopyGuard. | `draft.py:29-39,273-288` | implemented |
| INV-05 | Draft promotion is the normal path to multi-rate broadcast; direct broadcast remains an explicit operator command. | `draft.py:290-328`; `routes.py:1265-1284,1302-1316` | implemented, intentional dual path |
| INV-06 | Case sessions use immutable baseline plus mutable projection/history and revision increment. | `cases.py:163-185,230-263,265-283` | implemented |
| INV-07 | Cross-file case/draft writes use a private before/after SHA-256 recovery marker and fail closed on digest conflict. | `persistence.py:84-193` | implemented, runtime unverified |
| INV-08 | Runtime data defaults outside checkout; rate data is logically separate from writable home. | `main.py:48-57,98-115`; `engine/README.md:23-40` | implemented |
| INV-09 | Broadcast is simulated/event-only; server worker owns ticks and queue time. | `broadcast.py:8-14,130-314`; `main.py:133-150` | implemented |
| INV-10 | Every historical WebSocket business event has positive monotonic ID; control frames use ID 0; replay window is bounded. | `routes.py:67-87,190-315,1445-1572` | implemented |
| INV-11 | Auto mode only acts with no waiting queue; active broadcasts contribute quadratic cooldown; stale generation work is rejected. | `automode.py:44-87,191-338` | implemented, runtime unverified |
| INV-12 | Scope IDs are syntactically constrained and a scoped workspace path is partitioned by tenant/client/job. | `scope.py:12-78`; `workflow.py:34-59` | implemented-not-wired |

### Data authority and persistence boundary

```json
{
  "metadata_type": "schemas_and_authorities",
  "runtime_roots": {
    "runtime_home": ["RADIOWORKS_HOME", "~/.radiworks"],
    "rate_data": ["RADIOWORKS_DATA_DIR", "<runtime_home>/data"],
    "writable_collections": ["cases", "drafts", "config", "recovery", "entropy_journals"]
  },
  "schemas": [
    {
      "name":"AnalysisResult",
      "path":"radiworks_port/engine/src/radiworks/core/analysis.py",
      "fields":{"generalVitality":"int|null","numberOfTrials":"int|null","rateObjects":"RateObject[]"}
    },
    {
      "name":"RateObject",
      "path":"radiworks_port/engine/src/radiworks/core/analysis.py",
      "fields":{"energeticValue":"int","nameOrRate":"string","url":"string|null","gv":"int","recurring":"int","recurringGeneralVitality":"int","level":"int","potency":"string|null","resonateCounter":"int"}
    },
    {
      "name":"ComputationPassport.v2",
      "path":"radiworks_port/engine/src/radiworks/passport.py",
      "fields":{"run_id":"UUID","kernel_hash":"sha256 string","input_hash":"sha256 string","seed":"int|null","entropy_mode":"seeded|stochastic","replayable":"boolean","copyguard_digest":"sha256|null","signatur_status":"unsigned"}
    },
    {
      "name":"CaseSession",
      "path":"radiworks_port/engine/src/radiworks/core/cases.py",
      "fields":{"sessionId":"hex UUID","parentSessionId":"string|null","revision":"int","analysisBaseline":"AnalysisResult","analysisResult":"AnalysisResult","passport":"summary","draftId":"UUID|null","gvHistory":"event[]","gvState":"object","entropyCheckpoint":"object|null"}
    },
    {
      "name":"AnalysisDraft",
      "path":"radiworks_port/engine/src/radiworks/core/draft.py",
      "fields":{"id":"UUID","status":"draft|client_review|ready|promoted|discarded","payload":"AnalysisResult","focus":"object","copyguard_verdict":"allow|block","sessionId":"string|null","sessionRevision":"int","ttl_hint":"ISO-8601"}
    },
    {
      "name":"WebSocketEnvelope.v1",
      "path":"radiworks_port/engine/src/radiworks/api/routes.py",
      "fields":{"v":"1","id":"0 for control or positive int","boot":"string","type":"string","payload":"object","ts":"milliseconds"}
    },
    {
      "name":"ScopeContext",
      "path":"radiworks_port/engine/src/radiworks/scope.py",
      "fields":{"tenant_id":"validated string","client_id":"validated string","job_id":"validated string"},
      "state":"implemented-not-wired"
    }
  ],
  "write_authorities": [
    {"path":"core/cases.py","writes":["case JSON","dashboardInformations.json"]},
    {"path":"core/draft.py","writes":["draft JSON"]},
    {"path":"config.py","writes":["Settings.json"]},
    {"path":"persistence.py","writes":["temporary JSON","recovery marker","target JSON"]},
    {"path":"entropy_journal.py","writes":["encrypted entropy journal"]}
  ]
}
```

## API Contracts and Exportable Interfaces (English)

### Public HTTP and WebSocket surface

| Group | Contract | Primary implementation |
|---|---|---|
| Health/identity | `GET /ping`, `GET /manifest` | `routes.py:480-490` |
| Entropy | `GET /entropy/status`, `POST /entropy/acquire`, `GET /entropy/feed` | `routes.py:492-533` |
| Analysis | `POST /analysis`, `GET /analysis`, `GET /analysis/current`, GV-round routes, `POST /gv`, `POST /search-anomaly` | `routes.py:537-848,1081-1105` |
| Settings | `GET/PUT /settings` | `routes.py:876-906` |
| Catalog/scripts | `GET /databases`, `GET /rates`, `GET/POST /scripts*`, `GET /materiaMedicaSearch` | `routes.py:954-986,1109-1117,1390-1395` |
| Case/session | `/cases*`, `/case`, `/analysis/sessions*` | `routes.py:910-921,1121-1248` |
| Draft | `/drafts*`, transition/promote/discard | `routes.py:1252-1298` |
| Broadcast/auto | `/broadcast*`, `/auto-mode*` | `routes.py:1302-1373,1023-1047` |
| Interactive utilities | `/stickpad*`, `/images*`, `/essential-questions`, `/training*`, `/materia/clarke-compare` | `routes.py:852-856,925-950,990-1019,1051-1078,1377-1388` |
| Event stream | `GET websocket /ws?last_event_id=&last_boot=` | `routes.py:1401-1572` |

```json
{
  "metadata_type": "api_contracts",
  "base_path": "/",
  "analysis": {
    "method":"POST","path":"/analysis",
    "request":{"database":"string","seed":"int|null","mode":"seeded|stochastic|null","max_hits":"100|1000","tenant_id":"string|null","client_id":"string|null"},
    "response":{"passport":"ComputationPassport.v2","result":"AnalysisResult","draft":"AnalysisDraft without payload"},
    "side_effects":["creates Draft", "may append CaseSession", "may create entropy journal", "publishes analysis.progress and analysis.update"]
  },
  "broadcast": {
    "method":"POST","path":"/broadcast",
    "request":{"signature":"non-empty string","seconds":"1..86400","multiplier":"1..1000","clear":"bool","delay_ms":"1..10000","repeat":"1..1000"},
    "response":"BroadcastElement payload with broadcastId",
    "side_effects":["in-memory queue", "worker thread", "emitter.sequence event"]
  },
  "websocket": {
    "path":"/ws",
    "query":{"last_event_id":"int|null","last_boot":"string|null"},
    "envelope":{"v":1,"id":"0|positive integer","boot":"string","type":"string","payload":"object","ts":"milliseconds"},
    "control_events":["server.hello","server.replay_gap","pong"],
    "business_event_examples":["analysis.progress","analysis.update","broadcast.progress","broadcast.resonance","emitter.sequence","auto.mode","auto.broadcast","auto.error","gv.update","clipboard.updated"],
    "retention":"256 in-memory business events per process"
  },
  "frontend_api_bypass_candidates": [
    {"path":"radiworks_port/webapp/js/views/peggotty.js","line":23,"call":"fetch(`/scripts/${encodeURIComponent(name)}`)","risk":"ignores configured apiBase"},
    {"path":"radiworks_port/webapp/js/views/statusbar.js","line":99,"call":"fetch('/entropy/feed')","risk":"ignores configured apiBase"}
  ]
}
```

## Architecture Findings and Strategic Actions (Deutsch)

| ID | Schwere | Befund | Evidenz | Strategische Maßnahme |
|---|---|---|---|---|
| F-01 | hoch | ScopeResolver und WorkflowRegistry modellieren Mandanten-/Klienten-/Job-Isolation, sind aber im produktiven AppFactory/API-Pfad nicht verdrahtet. Der aktive `AppState` hält globale Case-, Draft-, GV-, StickPad-, Training- und Auto-Zustände. | `scope.py:24-78`, `workflow.py:24-59`, gegen `main.py:88-150`, `routes.py:110-188` | G1: Eine explizite Scope-Authority festlegen und jeden Read/Write-/in-memory-Pfad daran binden; erst danach Mehrinstanzbetrieb behaupten. |
| F-02 | hoch | Zwei Frontend-Aufrufe umgehen den konfigurierbaren API-Client. Beim eingebetteten Modul oder abweichenden `apiBase` können Skriptladen und Entropieanzeige gegen einen falschen Origin laufen. | `webapp/js/views/peggotty.js:23`; `webapp/js/views/statusbar.js:99`; Client-Vertrag `webapp/js/api.js:45-187` | G2: Alle HTTP-Aufrufe ausschließlich über einen konfigurationsgebundenen Client führen; kontraktbasierten Browser-/Node-Probe hinzufügen. |
| F-03 | hoch | Das Root-README und Kommentare referenzieren externe `Modul_Templates`/`docs` als normative Verträge, die im geprüften Repo nicht vorliegen. Die tatsächliche Routenquelle ist `routes.py`. | `radiworks_port/README.md:3-15`; `engine/README.md:20-22,43-54`; `ROADMAP.md:69-71` | G0: Vertragssnapshot mit vorhandenen Artefakten oder versionierter externer Referenz-ID erstellen; keine Architekturentscheidung allein aus fehlenden Dokumentlinks ableiten. |
| F-04 | mittel | Die Settings-Leseoperation erzeugt beim Erstzugriff Persistenzdateien/Defaults. Damit ist ein nominelles GET nicht beobachtungsrein und der Settings-Store ist keine reine Query-Schnittstelle. | `config.py:56-90`; `routes.py:876-883` | G3: Query- und Initialisierungssemantik explizit trennen oder dokumentieren; danach idempotente GET- und Recovery-Tests. |
| F-05 | mittel | `ScopeContext` enthält Header-Modell und validierte IDs, während `AnalysisRequest` eigene optionale tenant/client-Felder akzeptiert. Diese zwei Identitätsquellen sind nicht zusammengeführt. | `scope.py:68-78`; `routes.py:351-358,537-571` | G1: Einen kanonischen, authentifizierten Scope-Eingang definieren; Request-Payload darf ihn nicht überschreiben. |
| F-06 | mittel | `promote_draft()` setzt den Draftstatus vor dem Enqueue mehrerer Broadcasts. Ein späterer Queue-Fehler kann damit einen bereits als promoted persistierten Draft und nur teilweise eingereihte Broadcasts hinterlassen. | `draft.py:292-328`; `routes.py:1265-1284` | G4: Promotion als kompensierbares/atomar modelliertes Workflow-Gate behandeln; vorher RED-Fault-Injection für Enqueue-Fehler und Wiederanlauf definieren. |
| F-07 | mittel | Der Bild-Client berechnet SHA-256, übergibt ihn aber in das Feld `md5`; der Server prüft weder Name/Format noch Algorithmus. Das erzeugt eine semantisch falsche exportierte Schnittstelle. | `webapp/js/views/images.js:1-9,55`; `routes.py:395-399,937-950` | G5: Versionierten `contentHash` + `algorithm` Vertrag ergänzen, Legacy-Feld nur kompatibel migrieren und keine Bildbytes übertragen. |
| F-08 | mittel | Clarke-Dialog baut servergelieferte Werte mittels `innerHTML` zusammen. Der aktuelle Ursprung ist lokal, aber Katalogdaten sind eine externe/Betreiber-Eingabegrenze. | `webapp/js/views/analyze.js:341-360` | G6: DOM-Knoten und `textContent` verwenden; Tests mit HTML-Sonderzeichen und potenziell bösartigen Katalogstrings. |
| F-09 | mittel | Globale in-memory AppState-Komponenten (`gv_round`, `training_signature`, `stick_pad`, Broadcast, Auto, Event-History) definieren eine Prozess- und nicht Fall-/Scope-isolierte Authority. | `routes.py:110-188`; `main.py:120-150` | G1/G7: Ownership und Reset-/Restart-Semantik pro Scope oder explizit single-operator lokal spezifizieren. |
| F-10 | mittel | Die Webapp behauptet bzw. verlinkt einzelne Qualitäts-/Produktgrenzen (WCAG, externe Dokumente, Parität), die ohne Browser-, Accessibility- oder Gold-Harness-Ausführung in dieser Prüfung nicht bestätigt sind. | `index.html:96-115,486-491`; `engine/README.md:56-103` | G8: Behauptungen gegen reale Evidenzmatrix binden; unbekannte Messungen als unbekannt anzeigen. |
| F-11 | niedrig | `WebcamFeedSource` verwendet eine Liste und `pop(0)`, wodurch große Feed-Last pro Entnahme linear wird; die Obergrenze beträgt vier Millionen Werte. | `entropy.py:101-120,171-179` | G9: Nach Profiling auf `deque` oder Ringpuffer wechseln; nur nach Performance-Baseline und Verhaltensäquivalenz. |
| F-12 | niedrig | Die Projektwurzel enthält eine große Referenz-/Bytecode-Baumstruktur; die aktive Anwendung ist nur `radiworks_port`. Eine pauschale LOC-/Abhängigkeitsbewertung der Wurzel wäre irreführend. | Top-level inventory; `radiworks_port/README.md:5-9` | G0: Build-, SBOM- und Audit-Grenze auf `radiworks_port/engine` und `radiworks_port/webapp` festschreiben; Referenzbaum separat deklarieren. |

```json
{
  "metadata_type": "findings",
  "items": [
    {"id":"F-01","severity":"high","state":"static-inference","title":"Scoped workflow abstractions are not wired into active AppState","paths":["radiworks_port/engine/src/radiworks/scope.py","radiworks_port/engine/src/radiworks/workflow.py","radiworks_port/engine/src/radiworks/main.py","radiworks_port/engine/src/radiworks/api/routes.py"],"gate":"G1"},
    {"id":"F-02","severity":"high","state":"implemented","title":"Two frontend requests bypass configured apiBase","paths":["radiworks_port/webapp/js/views/peggotty.js","radiworks_port/webapp/js/views/statusbar.js","radiworks_port/webapp/js/api.js"],"gate":"G2"},
    {"id":"F-03","severity":"high","state":"documented-missing-in-tree","title":"Normative external documentation references are unavailable in review scope","paths":["radiworks_port/README.md","radiworks_port/engine/README.md","radiworks_port/ROADMAP.md"],"gate":"G0"},
    {"id":"F-04","severity":"medium","state":"implemented","title":"GET settings has initialization writes","paths":["radiworks_port/engine/src/radiworks/config.py","radiworks_port/engine/src/radiworks/api/routes.py"],"gate":"G3"},
    {"id":"F-05","severity":"medium","state":"static-inference","title":"Payload tenancy and header scope models are separate authorities","paths":["radiworks_port/engine/src/radiworks/scope.py","radiworks_port/engine/src/radiworks/api/routes.py"],"gate":"G1"},
    {"id":"F-06","severity":"medium","state":"static-inference","title":"Draft promotion and multi-enqueue lack one combined recovery boundary","paths":["radiworks_port/engine/src/radiworks/core/draft.py","radiworks_port/engine/src/radiworks/api/routes.py"],"gate":"G4"},
    {"id":"F-07","severity":"medium","state":"implemented","title":"SHA-256 image hash is named md5 at API boundary","paths":["radiworks_port/webapp/js/views/images.js","radiworks_port/engine/src/radiworks/api/routes.py"],"gate":"G5"},
    {"id":"F-08","severity":"medium","state":"implemented","title":"Clarke dialog interpolates server values via innerHTML","paths":["radiworks_port/webapp/js/views/analyze.js"],"gate":"G6"},
    {"id":"F-09","severity":"medium","state":"implemented","title":"Interactive state is process-global","paths":["radiworks_port/engine/src/radiworks/api/routes.py","radiworks_port/engine/src/radiworks/main.py"],"gate":"G1"},
    {"id":"F-10","severity":"medium","state":"unverified-runtime","title":"UI and documentation claims require external evidence","paths":["radiworks_port/webapp/index.html","radiworks_port/engine/README.md"],"gate":"G8"},
    {"id":"F-11","severity":"low","state":"static-inference","title":"Large entropy feed uses list pop(0)","paths":["radiworks_port/engine/src/radiworks/entropy.py"],"gate":"G9"},
    {"id":"F-12","severity":"low","state":"implemented","title":"Repository boundary includes reference artifacts beyond active port","paths":["radiworks_port/README.md"],"gate":"G0"}
  ]
}
```

## Optimierungs-Roadmap (Deutsch)

### G0 — Vertrags- und Snapshotfrierung (Voraussetzung für alle Gates)

- Die aktive Grenze `radiworks_port/engine` + `radiworks_port/webapp` festlegen und Referenz-/Archiv-/Runtime-Wurzeln explizit ausschließen.
- Den vollständigen REST-, WebSocket-, Persistenz- und Frontend-API-Vertrag aus dem aktuellen Code erzeugen und mit eindeutiger Version/Hash binden.
- Die fehlenden externen `Modul_Templates`-/`docs`-Verträge entweder einbringen oder als bewusst externe, versionierte Abhängigkeit deklarieren.
- Für jede aktuelle Produktbehauptung (Java-Parität, Accessibility, Browser, Hardware-Nichtaktivierung) eine Evidenzspalte `implemented`, `tested`, `documented`, `unverified` führen.
- **Abnahmekriterium:** unveränderter Kernquell-Hash, vollständige Contract-Inventur, keine stillschweigende Bereinigung der schmutzigen Arbeitskopie.

### G1 — Kanonische Scope- und Zustandsautorität

- Einen einzigen Scope-Resolver als Eingangsautorität bestimmen; `tenant_id`, `client_id`, `job_id` dürfen nicht zugleich Header-, Request- und Dateifeldautorität sein.
- `WorkflowRegistry` nur dann produktiv verdrahten, wenn alle Case-, Draft-, Journal-, Recovery-, GV-, StickPad-, Training-, Broadcast- und WebSocket-Lesewege eine klare Scope-/Owner-Semantik erhalten.
- Falls das Produkt bewusst single-operator lokal bleibt, diesen Modus explizit begrenzen statt vorbereitete Multitenancy als aktiv darzustellen.
- **Abnahmekriterium:** Negativtests beweisen, dass kein Scope A Daten, laufende Zustände oder Event-Historie von Scope B lesen/ändern kann; lokale Kompatibilität bleibt erhalten.

### G2 — Frontend-Transportvertrag schließen

- Direkte `fetch()`-Aufrufe in Peggotty und Statusleiste in den `createClient(apiBase)`-Pfad überführen.
- Einen kleinen contract-first Browser-/Node-Test einführen: abweichendes `apiBase` und `wsUrl`, HTTP-Fehlerumschlag, Reconnect, Restart und Replay-Gap.
- **Abnahmekriterium:** keine produktiven View-Dateien besitzen direkte relative API-Aufrufe außerhalb eines bewusst dokumentierten Ausnahmeadapters.

### G3/G4 — Schreibsemantik und Workflow-Atomizität

- Settings-Initialisierung von GET-Semantik trennen oder die Schreibwirkung als ABI-Vertrag verifizieren.
- Für Draft-Promote plus Mehrfach-Enqueue eine Recovery-/Kompensationsgrenze entwerfen. Dabei den bestehenden Case/Draft-Recovery-Ansatz erweitern, nicht ersetzen.
- **Abnahmekriterium:** Fault-Injection für jeden Schritt erzeugt entweder den vollständigen Endzustand oder einen klaren fail-closed Recovery-Zustand; keine halbpromoteten Drafts ohne Betreiberentscheidung.

### G5/G6 — Export- und Eingabegrenzen härten

- Bildhash in `contentHash` und `algorithm` versionieren; Legacy `md5` nur als klar gekennzeichnete Kompatibilität behandeln.
- Alle katalog- oder servergesteuerten Texte über DOM-APIs rendern; HTML-Interpretation an dieser Grenze entfernen.
- **Abnahmekriterium:** Hashalgorithmus und Format werden serverseitig validiert; Sonderzeichen-/Injection-Fixtures bleiben Text.

### G7/G8/G9 — Betriebs- und Qualitätsnachweise

- G7: definierte Shutdown-, Restart-, Ownership- und Event-Reset-Semantik für globale Workerzustände.
- G8: isolierte reale Checks für Start, REST, WebSocket, Browser, WCAG und Gold-Harness; keine Vermischung mit Implementierung.
- G9: Entropiepuffer erst nach Profiling optimieren; Draw-Reihenfolge, FIFO und Journal-Semantik müssen äquivalent bleiben.

```json
{
  "metadata_type": "gate_dependency_dag",
  "gates": [
    {"id":"G0","name":"Contract and snapshot freeze","depends_on":[],"findings":["F-03","F-12"],"change_class":"documentation/evidence only"},
    {"id":"G1","name":"Canonical scope and state authority","depends_on":["G0"],"findings":["F-01","F-05","F-09"],"change_class":"high-risk architectural"},
    {"id":"G2","name":"Frontend transport contract","depends_on":["G0"],"findings":["F-02"],"change_class":"bounded compatibility"},
    {"id":"G3","name":"Settings query/write semantics","depends_on":["G0"],"findings":["F-04"],"change_class":"bounded persistence contract"},
    {"id":"G4","name":"Promotion-to-queue atomicity","depends_on":["G0","G3"],"findings":["F-06"],"change_class":"high-risk persistence workflow"},
    {"id":"G5","name":"Image hash API versioning","depends_on":["G0","G2"],"findings":["F-07"],"change_class":"versioned API compatibility"},
    {"id":"G6","name":"Catalog output rendering boundary","depends_on":["G0","G2"],"findings":["F-08"],"change_class":"frontend safety"},
    {"id":"G7","name":"Runtime ownership semantics","depends_on":["G1"],"findings":["F-09"],"change_class":"concurrency/lifecycle"},
    {"id":"G8","name":"Runtime evidence matrix","depends_on":["G0"],"findings":["F-10"],"change_class":"verification only"},
    {"id":"G9","name":"Entropy buffer performance","depends_on":["G8"],"findings":["F-11"],"change_class":"performance-preserving refactor"}
  ],
  "parallelizable_after_G0": [["G2","G3","G8"], ["G5","G6"]],
  "not_parallelizable": [["G1","G7"], ["G3","G4"], ["G8","G9"]]
}
```

## No-Go Boundaries (Deutsch)

- Keine Behauptung vollständiger Java-/Python-Bitidentität: statisch belegt ist nur die begrenzte, dokumentierte seeded-Paritätsabsicht; reale Gold-Harness-Ausführung war ausgeschlossen.
- Keine Behauptung von Mandantentrennung im laufenden API-Pfad, bevor G1 abgeschlossen ist.
- Keine Verlagerung von Betreiber-/Fall-/Journal-/Katalogdaten in den Git-Arbeitsbaum oder in Audit-Artefakte.
- Keine Hardware-Emission aus dem Broadcast-Manager; der vorhandene Vertrag ist event-only und `isHardwareActivatable: false`.
- Kein Big-Bang-Refactor der Analyse-, JavaRandom-, JavaHashMap- oder Entropiepfade. Neue Konfigurationen benötigen defaults, die den heutigen seeded Pfad erhalten.
- Kein Commit, Push, History-Rewrite, Löschen ungetrackter Runtime- oder Archivdaten und keine automatische Umsetzung aus diesem Plan.

```json
{
  "metadata_type": "no_go_boundaries",
  "items": [
    {"id":"NG-01","boundary":"No runtime claim from static review","applies_to":["test status","startup","browser","Java parity","recovery"]},
    {"id":"NG-02","boundary":"No multi-tenant claim before canonical scope wiring","applies_to":["ScopeResolver","WorkflowRegistry","AppState"]},
    {"id":"NG-03","boundary":"No sensitive runtime data copied into repository evidence","applies_to":["radiworks_home","entropy_journals","cases","drafts","archives"]},
    {"id":"NG-04","boundary":"No physical hardware activation","applies_to":["BroadcastManager","emitter integration"]},
    {"id":"NG-05","boundary":"No core entropy or analysis replacement without equivalence gate","applies_to":["EntropyProvider","JavaRandom","java_hashmap_string_order","analyse_rate_list"]},
    {"id":"NG-06","boundary":"No source changes, commits, or cleanup authorized","applies_to":["entire repository"]}
  ]
}
```

## Approval Checkpoint (Deutsch)

Bitte zuerst nur entscheiden, ob **G0** als nächster, rein dokumentierender Freeze-Gate freigegeben wird. Nach einer Freigabe wird keine Implementierung impliziert: Der nächste Schritt wäre ein separat hashgebundener, minimaler G0-Nachweis mit anschließender erneuter Prüfung der uncommitteten Arbeitsfläche.

## Review Completeness Ledger (English)

- Reviewed statically: application entrypoint, route registry, request models, WebSocket protocol, analysis/entropy/broadcast/auto-mode/case/draft/persistence/scope/workspace core, frontend bootstrap/client/views, project docs/manifests, test file inventory.
- Not read as content: operator data, archives, virtual environment, decompiled/reference trees, screenshots/binary images.
- Not executed: all runtime checks listed in the opening snapshot.
- Static conclusions are source-bound to the snapshot hash recorded above; concurrent modifications after that snapshot invalidate any claim that this is a current runtime verdict.
