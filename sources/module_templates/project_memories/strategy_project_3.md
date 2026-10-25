# Strategieplan 3 — Modul_Templates: statische Architektur- und Vertragsprüfung

## Prüfgrenze und Evidenzstatus

Diese Prüfung ist ausschließlich lesend und auf das Repository `Modul_Templates` begrenzt. Es enthält ausschließlich Koordinations-, Standard- und Übergabedokumentation; es enthält keine ausführbaren Python-, JavaScript-, TypeScript- oder Build-Dateien. Externe Modul- und Plattformpfade werden nur als dokumentierte Abhängigkeitsgrenzen behandelt. Es wurden keine Anwendungen importiert, Tests, Builds, Server, Migrationen oder Browserprüfungen ausgeführt.

Die Bezeichnung „loss-free“ wird hier als Nachvollziehbarkeitsziel umgesetzt, nicht als unbeweisbare Absolutheitsbehauptung: dokumentierte, statisch belegte, externe, unbestätigte und zukünftige Aussagen bleiben getrennt. Eine Aussage über RadiWorks-Laufzeitverhalten ist keine erneute Laufzeitvalidierung, solange die externe Engine nicht im genehmigten Scope gelesen und ausgeführt wurde.

```json
{
  "metadata_type": "review_snapshot",
  "review_mode": "strict_static_repository_only",
  "repository_root": "C:/Users/Hubert111/Documents/Modul_Templates",
  "branch": "main",
  "head": "041ae65ee5ff2a7aa4a0cc0a1bd82666e4e3ac04",
  "tracked_file_count": 14,
  "tracked_source_manifest_sha256_before_report": "e49a9d73c54e8db73e24b408e1a49f83113cded15f798f279e28920474506804",
  "pre_existing_modified_paths": [
    "MODULE_REGISTRY.md",
    "UEBERGABE_AURELIA.md",
    "modules/radiworks/FESTLEGUNGEN.md",
    "modules/radiworks/PORT_PLAN.md",
    "standards/API_CONTRACT.md",
    "standards/REIFEGRADE.md"
  ],
  "only_allowed_write": "project_memories/strategy_project_3.md",
  "not_executed": ["imports", "tests", "build", "server", "migration", "browser", "external source inspection"],
  "state_vocabulary": ["verified-static", "documented", "external-authority", "unverified-runtime", "future-only", "absent-in-reviewed-scope"]
}
```

## Management-Zusammenfassung

Das Repository ist die normative Integrations- und Koordinationsschicht für RadiX-Module, nicht deren Implementierung. Es zentralisiert die Modulblaupause, REST-/WebSocket-Konventionen, UI-Vorgaben, Reifegrade, ein Modulportfolio und RadiWorks-bezogene Portierungs- bzw. Übergabeevidenz. Die beabsichtigte Verantwortungsaufteilung ist sinnvoll: Modulrepos besitzen Fachlogik und Laufzeitdaten; Aurelia besitzt spätere Plattformautorität; dieses Repository besitzt Contract-Governance.

Die zentrale Optimierungsaufgabe ist eine präzise Vertragsschließung vor weiterer Integration. Drei Befunde haben Vorrang: eine einheitliche ABI-Identität, vollständige versionierte Manifest-/Request-/Response-Schemas und ein routeübergreifender Tenant-/Autorisierungsvertrag. Diese Punkte sind Voraussetzungen, nicht nachgelagerte Dokumentationskosmetik.

Die vorhandenen RadiWorks-Aussagen sind an mehreren Stellen bewusst vorsichtiger geworden: Sie begrenzen Java-Parität auf definierte Fixtures und erklären S4/S5 nicht als zertifiziert. Das ist architektonisch korrekt. Es muss jedoch künftig durch immutable, ausführbare Evidenzkarten ergänzt werden, bevor ein Reifegrad als Integrationstatsache dient.

## Architecture map — English technical view

```text
Aurelia platform (external authority)
  ├─ identity / RBAC / tenant context / quotas
  ├─ kernel registry and administrator approval
  ├─ timerd: authoritative time and lane lifecycle
  ├─ emitterd: lease, arming, acknowledgement, physical actuation
  └─ CopyGuard platform stage

Modul_Templates (reviewed governance repository)
  ├─ portfolio registry
  ├─ engine + webapp blueprint
  ├─ ABI, REST, WebSocket and draft conventions
  ├─ UI embedding and accessibility conventions
  ├─ maturity gates
  └─ RadiWorks-specific plan and evidence references

Individual module repository (external authority)
  ├─ engine/ domain implementation
  ├─ webapp/ standalone and iframe client
  ├─ manifest, tests and runtime API
  └─ runtime home, catalogs, journals and deployment secrets
```

```json
{
  "metadata_type": "architecture_dependency_map",
  "nodes": [
    {"id":"coordination_repo","path":".","kind":"documentation_governance","state":"verified-static"},
    {"id":"registry","path":"MODULE_REGISTRY.md","kind":"portfolio_inventory","state":"verified-static"},
    {"id":"module_standard","path":"standards/MODUL_STANDARD.md","kind":"normative_blueprint","state":"verified-static"},
    {"id":"api_contract","path":"standards/API_CONTRACT.md","kind":"normative_contract","state":"verified-static"},
    {"id":"maturity_model","path":"standards/REIFEGRADE.md","kind":"readiness_model","state":"verified-static"},
    {"id":"ui_standard","path":"standards/UI_DESIGN_STANDARD.md","kind":"embedding_contract","state":"verified-static"},
    {"id":"radiworks_docs","path":"modules/radiworks","kind":"module_evidence","state":"verified-static"},
    {"id":"radiworks_runtime","path":"C:/Users/Hubert111/Documents/Radiworks/radiworks_port","kind":"external_runtime","state":"external-authority"},
    {"id":"aurelia_platform","path":"C:/Users/Hubert111/Documents/ChatGPT/Aurelia","kind":"external_platform","state":"external-authority"}
  ],
  "edges": [
    {"from":"module_standard","to":"api_contract","relation":"requires implementation of","state":"documented"},
    {"from":"maturity_model","to":"api_contract","relation":"uses as readiness evidence","state":"documented"},
    {"from":"ui_standard","to":"module_standard","relation":"specializes webapp layer","state":"documented"},
    {"from":"radiworks_docs","to":"api_contract","relation":"declares RadiWorks profile","state":"documented"},
    {"from":"radiworks_runtime","to":"aurelia_platform","relation":"future registry and iframe integration","state":"future-only"},
    {"from":"aurelia_platform","to":"radiworks_runtime","relation":"supplies identity, time, hardware and approval authority","state":"future-only"}
  ],
  "exportable_dependencies": [
    "Kernel ABI v1 manifest",
    "POST /analysis REST operation",
    "WebSocket /ws v:1 envelope",
    "AnalysisDraft state machine",
    "Computation Passport",
    "EntropyProvider abstraction",
    "VirtualEmitter event choreography",
    "window.__MODULE_CONFIG__",
    "data-module-theme and data-accent"
  ]
}
```

## Kerninvarianten / Core invariants

| ID | Invariant in English | Deutscher Steuerungswert | State | Statische Evidenz |
|---|---|---|---|---|
| INV-01 | Domain logic remains in module repositories; this repository owns coordination and standardization. | Keine Fachlogik in Templates verschieben. | verified-static | `README.md:3-8` |
| INV-02 | A module consists of `engine/` and `webapp/`; the webapp contains no domain logic. | Einzige fachliche Wahrheit bleibt Engine-seitig. | documented | `standards/MODUL_STANDARD.md:7-19` |
| INV-03 | The API base must be configurable and never hard-coded. | Portable Solo- und Embed-Ausführung erhalten. | documented | `standards/API_CONTRACT.md:7`; `standards/MODUL_STANDARD.md:43-44` |
| INV-04 | Default reproducibility is `seeded`; `stochastic` is explicit and provenance-bearing. | Keine stille Netz- oder Entropiepfadänderung. | documented | `standards/API_CONTRACT.md:33-39`; `modules/radiworks/FESTLEGUNGEN.md:8-17` |
| INV-05 | The browser is not the authoritative clock; live state is server-driven through `/ws`. | Kein clientseitiges Timing als Fachautorität. | documented | `standards/API_CONTRACT.md:113`; `GEMEINSAME_PUNKTE_AURELIA.md:62-64` |
| INV-06 | Hardware actuation is platform-daemon authority; module manifests remain non-activatable. | Keine direkte Hardwaresteuerung aus Modulen. | documented | `standards/API_CONTRACT.md:115-119`; `GEMEINSAME_PUNKTE_AURELIA.md:58-70` |
| INV-07 | AnalysisDraft lifecycle is `draft → client_review → ready → promoted|discarded`; promotion is the stated route to harmonization. | CopyGuard und bewusste Freigabe nicht umgehen. | documented | `standards/API_CONTRACT.md:41-53` |
| INV-08 | Visible copy must remain CopyGuard-safe and must not make diagnostic, therapeutic or cure claims. | Produkt- und Compliance-Grenze wahren. | documented | `MODULE_REGISTRY.md:35-40`; `standards/MODUL_STANDARD.md:42` |
| INV-09 | Tenant isolation is required by platform policy; nullable prototype fields do not establish authorization or scoped query enforcement. | S4 nicht aus Feldexistenz ableiten. | documented / unverified-runtime | `MODULE_REGISTRY.md:37`; `standards/API_CONTRACT.md:154-157` |
| INV-10 | `radiquant4` is prohibited as a source/reference tree. | Tabu-Grenze bleibt explizit und unverändert. | documented | `MODULE_REGISTRY.md:18`; `standards/MODUL_STANDARD.md:32` |

## API contracts — English technical map

No endpoint was called. The following is an exact normalization of the documented contract; fields not specified by the source remain unspecified.

```json
{
  "metadata_type": "api_contract_inventory",
  "authority_path": "standards/API_CONTRACT.md",
  "state": "documented_not_runtime_verified",
  "transport": {"apiBase":"configurable","hardcoded_api_base_prohibited":true},
  "routes": [
    {"method":"GET","path":"/ping","response_fields":["result","module","version"]},
    {"method":"GET","path":"/manifest","response":"Kernel ABI v1 object"},
    {"method":"GET","path":"/entropy/status","response_fields":["defaultMode","factoryDefault","modes","activeSource","chain","note"]},
    {"method":"POST","path":"/entropy/acquire"},
    {"method":"GET","path":"/databases"},
    {"method":"POST","path":"/analysis","request_ref":"AnalysisRequest","response_fields":["passport","result","draft"]},
    {"method":"GET","path":"/analysis/current"},
    {"method":"POST","path":"/gv","response_fields":["gv","source"]},
    {"method":"POST","path":"/search-anomaly","request_fields":["width","height"]},
    {"method":"GET","path":"/drafts","query_fields":["status?"]},
    {"method":"GET","path":"/drafts/{id}","response":"metadata without payload"},
    {"method":"POST","path":"/drafts/{id}/transition","request_fields":["status"]},
    {"method":"POST","path":"/drafts/{id}/promote","failure_statuses":[409]},
    {"method":"POST","path":"/drafts/{id}/discard"},
    {"method":"POST","path":"/analysis/gv-round"},
    {"method":"POST","path":"/analysis/gv-round/reset"},
    {"method":"GET","path":"/analysis/gv-round"},
    {"method":"POST","path":"/essential-questions"},
    {"method":"POST","path":"/stickpad/position","request_fields":["x","y"]},
    {"method":"POST","path":"/stickpad/analyze","request_fields":["database"]},
    {"method":"POST","path":"/stickpad/gv"},
    {"method":"DELETE","path":"/stickpad"},
    {"method":"GET","path":"/settings"},
    {"method":"PUT","path":"/settings","request_fields":["booleans?","integers?","strings?"],"failure_statuses":[422]},
    {"method":"POST","path":"/images/analyze"},
    {"method":"POST","path":"/images/broadcast","request_fields":["md5","seconds?","multiplier?"]},
    {"method":"GET","path":"/cases"},
    {"method":"POST","path":"/cases"},
    {"method":"GET","path":"/cases/{name}"},
    {"method":"GET","path":"/cases/current"},
    {"method":"POST","path":"/broadcast"},
    {"method":"POST","path":"/broadcast/mix"},
    {"method":"GET","path":"/broadcast/queue"},
    {"method":"DELETE","path":"/broadcast/current"},
    {"method":"DELETE","path":"/broadcast/all"},
    {"method":"POST","path":"/script/execute"},
    {"method":"GET","path":"/scripts"},
    {"method":"GET","path":"/scripts/{name}"}
  ],
  "websocket": {
    "path":"/ws",
    "envelope":{"v":"integer","id":"integer","boot":"string","type":"string","payload":"object","ts":"milliseconds"},
    "connect_event":"server.hello",
    "control_event_id":0,
    "domain_event_id":"positive integer",
    "reconnect_inputs":["last_event_id","last_boot"],
    "gap_event":"server.replay_gap"
  },
  "error_envelope":{"error":{"code":"string","message":"string"}}
}
```

## Schema and data boundaries — English technical map

```json
{
  "metadata_type":"schema_inventory",
  "state":"documented_not_runtime_verified",
  "schemas":[
    {
      "id":"AnalysisRequest",
      "authority_path":"standards/API_CONTRACT.md:28",
      "fields":[
        {"name":"database","type":"string","required":true},
        {"name":"seed","type":"integer","required":false},
        {"name":"mode","type":"enum","values":["seeded","stochastic"],"required":false},
        {"name":"max_hits","type":"integer","documented_values":[100,1000],"required":false},
        {"name":"tenant_id","type":"string","required":false,"state":"nullable prototype field"},
        {"name":"client_id","type":"string","required":false,"state":"nullable prototype field"}
      ],
      "response_required_fields":["passport","result","draft"]
    },
    {
      "id":"AnalysisDraft",
      "authority_path":"standards/API_CONTRACT.md:45-53",
      "fields":["id","tenant_id","client_id","practitioner_id","source_kernel","source_run_id","payload","copyguard_digest","client_editable_fields","status","timestamps"],
      "lifecycle":["draft","client_review","ready","promoted","discarded"],
      "read_boundary":"GET /drafts/{id} returns metadata without payload"
    },
    {
      "id":"ComputationPassport",
      "authority_paths":["standards/API_CONTRACT.md:37-39","UEBERGABE_AURELIA.md:54-57"],
      "documented_fields":["run_id","kernel_hash","input_hash","seed","entropy_mode","dauer_ms","sources","signatur"],
      "later_documented_fields":["replayable","seed_scheme"],
      "schema_completeness":"incomplete in reviewed repository"
    },
    {
      "id":"KernelManifest",
      "authority_path":"standards/API_CONTRACT.md:121-147",
      "documented_fields":["id","version","hash","class","repro","budget","abi_surface","abi_version","operations","entry","entry_status","isHardwareActivatable"],
      "integration_operation":"POST /analysis",
      "legacy_metadata":"entry"
    },
    {
      "id":"ModuleConfig",
      "authority_path":"standards/UI_DESIGN_STANDARD.md:51-59",
      "transport":"window.__MODULE_CONFIG__",
      "fields":["apiBase","wsUrl","theme","locale"],
      "fallbacks":["?api=","?theme="],
      "embedding":"isolated iframe/preview host; no parent script access"
    }
  ],
  "data_boundaries":[
    {"data":"rate catalog","authority":"RADIOWORKS_DATA_DIR or RADIOWORKS_HOME/data","state":"RadiWorks-specific documented rule"},
    {"data":"cases, drafts, configuration, entropy journals","authority":"RADIOWORKS_HOME","state":"RadiWorks-specific documented rule"},
    {"data":"stochastic raw seeds","authority":"encrypted private runtime journal","state":"documented implementation claim; external to review scope"},
    {"data":"sensitive screenshots","authority":"local only; not shared repo/cloud","state":"documented privacy boundary"}
  ]
}
```

## Befundmatrix und Maßnahmen

| ID | Schwere | Befund | Statische Evidenz | Strategische Maßnahme |
|---|---|---|---|---|
| F-01 | hoch | Die globale Modul-ID-Konvention verlangt `radiworks.engine.v1`; das aktuelle RadiWorks-Profil verwendet `radiworks.engine`. Ohne kanonische Regel entstehen Registry-, Approval- und Consumer-Mehrdeutigkeiten. | `standards/MODUL_STANDARD.md:68-70`; `standards/API_CONTRACT.md:128-142`; `MODULE_REGISTRY.md:12` | G1: ABI-Identität entscheiden; ID, Versionsort, Alias-Policy und Migration maschinenlesbar fixieren. |
| F-02 | hoch | Die Registry-Invarianten nennen `input_schema`, `output_schema` und `copy`, das aktuelle Manifestprofil liefert diese Felder nicht und verweist auf ein externes Live-Manifest. Der lokale Mindestvertrag ist daher unvollständig. | `MODULE_REGISTRY.md:35`; `standards/API_CONTRACT.md:128-147` | G2: Versionierte JSON-Schemas und Required/Optional-Matrix veröffentlichen oder ABI-Revision explizit ändern. |
| F-03 | hoch | Fail-closed-Scoping wird für jede Query/Buffer gefordert, aber Tenant-/Client-Felder sind nur teilweise und nullable beschrieben; `job_id`, WS-Autorisierung und routeweise Filterpflicht fehlen. | `MODULE_REGISTRY.md:37`; `standards/API_CONTRACT.md:28, 51-53, 154-157`; `GEMEINSAME_PUNKTE_AURELIA.md:14` | G3: Tenant/Auth-Contract pro HTTP-, WS- und Persistenzpfad mit Kontextquelle, Fehlern und Fail-closed-Regel. |
| F-04 | mittel | Der Satz, alle Mutationen seien über `/cases/current` plus `/analysis/current` introspektierbar, deckt Draft-, Broadcast-, Settings- und StickPad-State nicht nachvollziehbar ab. | `standards/API_CONTRACT.md:149-153` gegenüber `:41-113` | G4: State-Observability-Matrix mit Owner, Readback, Redaction und Konsistenzmodell. |
| F-05 | mittel | `/images/broadcast` exportiert `md5`, während der Funktionsabgleich SHA-256 als bewusste Passport-Familien-Anpassung bezeichnet. | `standards/API_CONTRACT.md:89-90`; `modules/radiworks/FUNKTIONSABGLEICH_BILDER.md:80-82` | G5: Witness-Hash-Contract mit Algorithmus, Feldname, Encoding, Migration und no-store-Regel. |
| F-06 | mittel | `GET /settings` darf Defaults beim ersten Abruf belegen. Damit trägt ein GET eine dokumentierte Schreibsemantik. | `standards/API_CONTRACT.md:82-83` | G6: Reine Lesesemantik oder explizite idempotente Initialisierung mit Audit- und Speicherregel. |
| F-07 | mittel | Draft-Metadaten werden ohne Payload gelesen; der geschützte Review-/Payload-Projektionspfad für Promote ist nicht spezifiziert. | `standards/API_CONTRACT.md:45-49` | G7: Authentisierte Payload-Ansicht, Redaktion, Editierfelder und CopyGuard-Zeitpunkt definieren. |
| F-08 | mittel | S2/S3 beruhen auf lokalen Nachweisformulierungen ohne immutable Revision, Befehl, Ergebnis, Hash und Prüferurteil. Der Text vermeidet korrekt S4-Zertifizierung, bleibt aber schwach reproduzierbar. | `standards/REIFEGRADE.md:13-29, 34-43`; `UEBERGABE_AURELIA.md:13-14` | G8: Evidence Card je Modul und nur hashgebundene Reifegradfreigabe. |
| F-09 | niedrig | `aurelia-entropyd` ist ausdrücklich nur Diskussionsentwurf; Lease-Response, Auth, Fehler, Retention und Betrieb sind nicht formalisiert. | `D-VORLAGE_ENTROPYD.md:1-5, 12-23, 58-75` | G9: Betreiberentscheidung/ADR vor jeder Standard- oder Implementierungsübernahme. |
| F-10 | niedrig | Externe Aurelia- und RadiWorks-Referenzen sind in diesem Repo nicht an immutable Revisionen gebunden und können still driften. | `MODULE_REGISTRY.md:3-4`; `standards/MODUL_STANDARD.md:3-4`; `standards/API_CONTRACT.md:123-126` | G10: External-authority inventory mit Repo, Commit, Pfad, Zugriffsklasse und Verifikationsdatum. |

```json
{
  "metadata_type":"finding_inventory",
  "findings":[
    {"id":"F-01","severity":"high","state":"verified-static","topic":"ABI identifier inconsistency","evidence_paths":["standards/MODUL_STANDARD.md:68-70","standards/API_CONTRACT.md:128-142","MODULE_REGISTRY.md:12"],"gate":"G1"},
    {"id":"F-02","severity":"high","state":"verified-static","topic":"Manifest schema closure missing","evidence_paths":["MODULE_REGISTRY.md:35","standards/API_CONTRACT.md:128-147"],"gate":"G2"},
    {"id":"F-03","severity":"high","state":"verified-static","topic":"Tenant and authorization scope incomplete","evidence_paths":["MODULE_REGISTRY.md:37","standards/API_CONTRACT.md:28","standards/API_CONTRACT.md:51-53","standards/API_CONTRACT.md:154-157","GEMEINSAME_PUNKTE_AURELIA.md:14"],"gate":"G3"},
    {"id":"F-04","severity":"medium","state":"verified-static","topic":"State introspection overclaim","evidence_paths":["standards/API_CONTRACT.md:149-153","standards/API_CONTRACT.md:41-113"],"gate":"G4"},
    {"id":"F-05","severity":"medium","state":"verified-static","topic":"Witness hash contract mismatch","evidence_paths":["standards/API_CONTRACT.md:89-90","modules/radiworks/FUNKTIONSABGLEICH_BILDER.md:80-82"],"gate":"G5"},
    {"id":"F-06","severity":"medium","state":"verified-static","topic":"GET settings has initialization side effect","evidence_paths":["standards/API_CONTRACT.md:82-83"],"gate":"G6"},
    {"id":"F-07","severity":"medium","state":"verified-static","topic":"Draft payload review boundary unspecified","evidence_paths":["standards/API_CONTRACT.md:45-49"],"gate":"G7"},
    {"id":"F-08","severity":"medium","state":"verified-static","topic":"Maturity evidence not reproducibly bound","evidence_paths":["standards/REIFEGRADE.md:13-29","standards/REIFEGRADE.md:34-43","UEBERGABE_AURELIA.md:13-14"],"gate":"G8"},
    {"id":"F-09","severity":"low","state":"verified-static","topic":"Entropy service proposal incomplete","evidence_paths":["D-VORLAGE_ENTROPYD.md:1-5","D-VORLAGE_ENTROPYD.md:12-23","D-VORLAGE_ENTROPYD.md:58-75"],"gate":"G9"},
    {"id":"F-10","severity":"low","state":"verified-static","topic":"External authority references unpinned","evidence_paths":["MODULE_REGISTRY.md:3-4","standards/MODUL_STANDARD.md:3-4","standards/API_CONTRACT.md:123-126"],"gate":"G10"}
  ]
}
```

## Priorisierte Gate-Folge

1. G1, G2 und G3 zuerst abschließen. Sie sind gemeinsame Vorbedingungen für jede Registry-, Schema- und Mandantenintegration.
2. G5 und G6 danach getrennt behandeln. Beide sind klar begrenzte Export- und Zustandsverträge und dürfen keine Algorithmusänderung enthalten.
3. G4 und G7 als Kontrollflächen-Gate schließen, mit getrennten Akzeptanzkriterien für Observability und Datenschutz.
4. G8 vor jeder S4-Behauptung durchführen. Bis dahin bleiben S2/S3 dokumentierte lokale Nachweise statt Integrationszertifikate.
5. G9 nur nach ausdrücklicher Betreiberentscheidung eröffnen. Der Entropiedienst ist ein Vorschlag, keine aktuelle Plattformabhängigkeit.
6. G10 fortlaufend als Governance-Inventar führen.

```json
{
  "metadata_type":"gate_dependency_dag",
  "gates":[
    {"id":"G1","name":"ABI identity decision","depends_on":[],"closes_findings":["F-01"],"mode":"specification_only"},
    {"id":"G2","name":"Manifest schema closure","depends_on":["G1"],"closes_findings":["F-02"],"mode":"specification_and_schema_review"},
    {"id":"G3","name":"Tenant and authorization contract","depends_on":["G1"],"closes_findings":["F-03"],"mode":"specification_and_threat_model"},
    {"id":"G4","name":"State observability matrix","depends_on":["G2","G3"],"closes_findings":["F-04"],"mode":"contract_review"},
    {"id":"G5","name":"Witness hash contract","depends_on":["G2"],"closes_findings":["F-05"],"mode":"contract_review"},
    {"id":"G6","name":"Settings authority","depends_on":["G3"],"closes_findings":["F-06"],"mode":"contract_review"},
    {"id":"G7","name":"Draft review boundary","depends_on":["G3","G4"],"closes_findings":["F-07"],"mode":"privacy_and_contract_review"},
    {"id":"G8","name":"Evidence-backed maturity","depends_on":["G1","G2","G3","G4","G5","G6","G7"],"closes_findings":["F-08"],"mode":"immutable_evidence_gate"},
    {"id":"G9","name":"Entropy service decision","depends_on":[],"closes_findings":["F-09"],"mode":"operator_decision_only"},
    {"id":"G10","name":"External authority pinning","depends_on":[],"closes_findings":["F-10"],"mode":"governance_inventory"}
  ],
  "parallel_groups":[["G1","G9","G10"],["G2","G3"],["G5","G6"],["G4"],["G7"],["G8"]]
}
```

## No-go-Grenzen und Freigabepunkt

- Dieser Plan autorisiert keine Code-, Daten-, Konfigurations-, Runtime-, Registry- oder Commitänderung.
- Kein S4/S5-Nachweis darf aus den statischen S2/S3-Formulierungen abgeleitet werden.
- Sensible Screenshots, Roh-Seeds, Journale und Schlüssel wurden nicht gesucht, gelesen oder kopiert.
- Der verbotene `radiquant4`-Baum wurde nicht geöffnet oder referenziert.
- Der früheste zulässige nächste Schritt ist nur die explizit genehmigte Spezifikationsentscheidung G1. Danach ist eine neue, hashgebundene Vertragsprüfung erforderlich.

```json
{
  "metadata_type":"no_go_boundaries",
  "approval_required_before_execution":true,
  "first_permissible_gate":"G1",
  "prohibited_without_explicit_approval":["source changes","configuration changes","runtime execution","test execution","external repository content inspection","commit creation","registry registration","hardware activation","sensitive data access"],
  "review_limits":["No executable source files are present in the reviewed repository.","API and implementation statements are documentation-derived.","External paths are architectural boundaries, not inspected source authorities."]
}
```

Keine Umsetzung ist freigegeben. Dieses Dokument bleibt eine passive, statische Architektur- und Planungsgrundlage bis zur Nutzerfreigabe.
