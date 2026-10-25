# Technical Production GO - Freeze v6 Live Acceptance

Stand: 2026-07-25

Arbeitsort: `C:\morphic_v1\.worktrees\operator-workbench-phase1`

Branch: `operator-workbench-phase1`

HEAD/Baseline: `3271ff9366ab3fecb2a158913a0cc19ed6a06726`

Status: `TECHNICAL PRODUCTION GO / GATE 0 ACCEPTED`

## 1. Accepted Freeze

Der technische Produktions-GO basiert auf Freeze v6, nicht auf den immutable rejected Freezes v4/v5.

| Evidence | SHA-256 |
|---|---|
| `docs/reviews/2026-07-22-technical-production-go-freeze-v6.sha256` | `5bdf57840f2db647ff98bafb2c88571143ef733c38ced540d3a3b9a7f24608dd` |
| `docs/reviews/2026-07-22-technical-production-go-freeze-v6.md` | `3607c4fa553beefd2ec68065173b132bd02340e9a6da51e47e6a6628c43b90e2` |
| `docs/reviews/2026-07-22-technical-production-go-review-v6-1.md` | `2bb249c354166f9408fbc9627507291c84eca571d258111dea6a7518d0404e14` |
| `docs/reviews/2026-07-22-technical-production-go-review-v6-2.md` | `297a54c8e92d6215b41bcdfda7ff50f707bfc651e9328c0e188f91d331b16dff` |

Both independent v6 reviews contain:

```text
APPROVE
start drift: 0
end drift: 0
P0: 0
P1: 0
P2: 0
P3: 0
```

Immediate pre-start gate at `2026-07-25T22:29:09.5200081+02:00` recomputed the accepted manifest/record/review hashes, verified 117 manifest entries, and found zero syntax, path, ordering, duplicate, missing-file, reparse, or entry-hash issues.

## 2. Live Server

Reviewed command started from the accepted worktree:

```text
C:\morphic_v1\.venv\Scripts\python.exe -m uvicorn apps.web.main:app --host 127.0.0.1 --port 8765
```

Live runtime root:

`C:\Users\HUBERT~1\AppData\Local\Temp\opencode\morphic-live-gate-v6-20260725\runtime`

Live logs:

- `C:\Users\HUBERT~1\AppData\Local\Temp\opencode\morphic-live-gate-v6-20260725\logs\uvicorn-8765.stdout.log`
- `C:\Users\HUBERT~1\AppData\Local\Temp\opencode\morphic-live-gate-v6-20260725\logs\uvicorn-8765.stderr.log`

Observed live process at `2026-07-25T23:38:19.7732101+02:00`:

| Field | Value |
|---|---|
| Port | `127.0.0.1:8765` |
| Port-owner PID | `29000` |
| Parent PID | `28760` |
| Port-owner executable | `C:\Users\Hubert111\AppData\Local\Programs\Python\Python312\python.exe` |
| Parent executable | `C:\morphic_v1\.venv\Scripts\python.exe` |
| Command line | `"C:\Users\Hubert111\AppData\Local\Programs\Python\Python312\python.exe" -m uvicorn apps.web.main:app --host 127.0.0.1 --port 8765` |
| Parent command line | `"C:\morphic_v1\.venv\Scripts\python.exe" -m uvicorn apps.web.main:app --host 127.0.0.1 --port 8765` |

The venv launcher/parent returned PID `28760`; the actual listening Uvicorn child is PID `29000`. Live monitoring and rollback must use the port owner PID, then verify port ownership again.

Rollback command, if this GO must be reverted:

```powershell
$serverPid = 29000
$parentPid = 28760
Stop-Process -Id $serverPid -ErrorAction Stop
Start-Sleep -Seconds 2
Stop-Process -Id $parentPid -ErrorAction SilentlyContinue
if (Get-NetTCPConnection -LocalAddress 127.0.0.1 -LocalPort 8765 -State Listen -ErrorAction SilentlyContinue) { throw 'port 8765 still has a listener' }
```

## 3. Port Observations

Pre-start and live checks did not stop or restart the existing `8090` process.

| Port | Observation |
|---|---|
| `8090` | Existing listener remained PID `7976` (`python.exe main.py`) |
| `8765` | Free before start; now owned by PID `29000` |
| `8766` | Free |

## 4. Live Acceptance Evidence

| Gate | Result |
|---|---|
| `/api/health` | HTTP `200`, response length `2390` |
| `/` | HTTP `200`, contains `Morphic Engine V1` and `Operator Workbench` |
| `/api/workbench/scan-profile-catalog?profile_level=4` | HTTP `200`; `profile_level=4`; `internal.count=208`; `internal.profiles=208`; `external.count=0`; `total_scan_profiles=208` |
| Scan start | `POST /api/scan/jobs` with synthetic Gate-0 payload and `Idempotency-Key: scan-live-gate-v6-20260725-2229` returned job `scan-op-e6026a8f40e2c3238f48de25`, status `running` |
| Scan replay | Same payload and same idempotency key returned the same job `scan-op-e6026a8f40e2c3238f48de25`, status `running` |
| Scan stop | `POST /api/scan/jobs/scan-op-e6026a8f40e2c3238f48de25/stop` returned `stopped`; terminal stopped state confirmed |
| Browser smoke | Passed against `http://127.0.0.1:8765`; `Health: OK`; profile count `502`; Review reached; scan scope rendered `55 interne + 0 externe Profile = 55 Screening-Profile`; no console, page, request, or HTTP errors |

Browser evidence root:

`C:\Users\HUBERT~1\AppData\Local\Temp\opencode\morphic-live-gate-v6-20260725\browser`

| Browser evidence | SHA-256 |
|---|---|
| `live-smoke.js` | `93e5c30e38fdcd16afe0e2161ff5329f09ea7ca557dbee08ee4b175f3baa2351` |
| `live-smoke-evidence.json` | `095b2bc16365c04dec835fd7159b5fdaa0d1a7551332e330fd0538342059d060` |
| `live-smoke-review.png` | `4b1959ca0ba7bf9aba6759be41a1c906455cde1d97ce3aa0dce4689373df7e86` |

## 5. Hanger Analysis During Live Gate

The apparent hang was not a server hang. Evidence showed `/api/health` was HTTP `200`, Uvicorn was listening, and logs had no traceback. The blocking perception came from two orchestration issues:

- progress had not been advanced after server start;
- `Start-Process` returned the venv launcher PID `28760`, while the actual port owner was child PID `29000`.

Two initial browser-smoke attempts failed because of smoke-script assertions, not product failures:

- first attempt checked `#health-pill` immediately after `workbenchReady`, before the asynchronous health UI finished loading;
- second attempt hardcoded `208` for the Review UI profile pool, but the UI Review used default Level 3 and correctly rendered `55` profiles while the separate Level-4 API gate returned `208`.

The final smoke used state-based waiting and positive profile-pool rendering checks.

## 6. Deferred Scope

This status grants technical production GO for the Gate-0 recovery/live acceptance boundary only. Gates 1-16 remain separate deferred scope and require their own plans, tests, reviews, and acceptance evidence. No Git commit, staging, reset, cleanup, or broad worktree mutation is implied by this record.

Next action: discuss Gate 1 scope and ordering; do not continue Gate-0 remediation unless a new live drift or production issue is observed.
