# Governor Workbench implementation plan

Approved 2026-09-11 by the operator, including optional GPT-6 Astra medium, extensible planned modules, low-resource Windows monitoring and separate human/developer/LLM installation documentation.

## Architecture and responsibilities

Python 3.11+ standard library service, sqlite durable journal, vanilla browser UI; no Node runtime or Docker required in production. The service monitors known sources every 15 seconds, Git every 60 seconds, and performs paid model work only on explicit request (with a bounded opt-in change-review mode). One job worker. All process arguments are fixed or validated arrays. Bind 127.0.0.1 only. Browser session + CSRF/Origin/Host checks. Product gate restrictions remain separate from Workbench installation approval.

- Root: `governor_workbench/config.py`, `evidence.py`, `store.py`, `jobs.py`, `server.py`, `__main__.py`, tests and launch/installation scripts.
- LLM adapter worker: `governor_workbench/llm.py`, `hermes.py`, `tests/test_llm.py`, `tests/test_hermes.py`, `tools/evaluate_models.py`, model integration/evaluation documentation. Stdlib only; no changes to Hermes/CC Switch configuration.
- Frontend worker: `governor_workbench/static/index.html`, `app.js`, `style.css`; German responsive application, served by the root service.

## Sequence

1. Establish config/API contract, evidence and memory-write tests; verify missing implementation fails.
2. Implement observer, strict project paths, hashes, staged vs committed memory facts, snapshot/goals drift, extensible planned projects and gate DAG; no invented GO.
3. Implement durable jobs/events/settings with atomic duplicate prevention, recovery, one worker, read-only model reviews and isolated test execution; tests cover cancellation, stale evidence and errors.
4. Implement local HTTP/SSE API with session, strict host/origin and CSRF; filesystem access only through validated memory IDs. Editor backup, conflict detection, atomic replace and audit. Browser does not supply shell commands.
5. Wire frontend to API contract. Exercise real five-project state and browser interactions on desktop/mobile.
6. Test Terra/Sol/Astra with identical bounded governance cases, real endpoint identity and structured outputs. Document pass/fail and limitations; no benchmark implies global optimality.
7. Add portable Windows config, start/stop/autostart launchers, doctor/export commands, installation guide, developer guide and machine-readable LLM contract. Test package installed into isolated venv.
8. Independent code/spec and design review, fix findings, run relevant tests, start real monitor and verify persistence/idle resource use. Enable current-user autostart within authorized monitoring scope if environment supports it; report any concrete approval block.

## API contract (v1)

All GET requests same-origin. `GET /api/state` sets an HttpOnly SameSite=Strict session cookie, returns `csrf_token` and state. All POST require `X-CSRF-Token` plus exact Origin. JSON errors: `{error: string}`, normal HTTP codes.

State shape:
```
{version,csrf_token,observed_at,monitor:{enabled,interval_seconds,git_interval_seconds,last_error},
 runtime:{router:{reachable,url,error},hermes:{available,path},models:{orchestrator,supervisor,reasoning,options}},
 projects:[{id,name,path,kind,gate,status,next_step,depends_on,observed_at,head,branch,git_status,
 evidence_hash,warnings:[],memories:[{name,sha256,size,committed,staged}],sources:[]}],
 jobs:[{id,action,project_id,status,created_at,started_at,ended_at,error,result}],
 events:[{id,time,level,source,message,job_id}],settings:{supervisor,auto_review,monitor_enabled},
 planned_projects:[]}
```
`GET /api/events` SSE emits `event: state` with complete state JSON on revision changes, heartbeat otherwise. UI also reconnects/polls after disconnect; no overlapping state requests.
`GET /api/memory?project=ID&name=FILE.md` -> `{project,name,content,sha256}`.
`POST /api/memory` `{project,name,content,expected_sha256}` -> `{sha256,backup}` or 409; exact existing .md filename only.
`POST /api/actions` `{action,project_id?,supervisor?}` -> `{job}` HTTP 202. Actions: `refresh`, `hybrid_review`, `model_check`, `radiworks_tests`, `hermes_check`. Model check evaluates bounded synthetic governance questions, no source transmission. Hybrid review sends the explicitly selected project/all-project source context to configured models.
`POST /api/jobs/cancel` `{id}` -> `{ok:true}`.
`POST /api/settings` `{supervisor?,auto_review?,monitor_enabled?}` validated option set. Supervisor Sol or Astra; auto-review defaults false.
`POST /api/projects` `{name,description,depends_on:[ID]}` creates planned item with no filesystem path, implementation remains blocked. Reject unknown dependencies and duplicate names.
`POST /api/shutdown` `{}` stops service after response.

LLM module interface agreed with worker: see their messages if detailed return types change. Root owns integration and tests. No automatic product-code editing in this release; queued governed implementation requires a future dedicated allowlisted capability and separately approved scope.
