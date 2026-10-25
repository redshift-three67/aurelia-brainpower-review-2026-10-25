"""WebSocket Live-Updates fuer Scan-Job-Fortschritt.

Bietet einen WebSocket-Endpoint unter /api/scan/jobs/{job_id}/ws
der serverseitig den Job-Status pollt und Updates an verbundene
Clients pusht (alle 2 Sekunden bis Job abgeschlossen).
"""
from __future__ import annotations

import asyncio
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from apps.web.scan_jobs import LocalScanJobService

router = APIRouter(tags=["scan-live"])

POLL_INTERVAL_SECONDS = 2.0
MAX_CONNECTION_SECONDS = 600  # 10 Min Timeout


@router.websocket("/api/scan/jobs/{job_id}/ws")
async def scan_job_live(websocket: WebSocket, job_id: str) -> None:
    """WebSocket-Stream fuer Scan-Job-Fortschritt.

    Sendet alle 2 Sekunden ein JSON-Update mit:
    - job_id, status, progress_percent, current_phase, current_substep
    - completed_substeps, logs (neue Zeilen seit letztem Update)

    Bei Status 'completed' oder 'failed' wird ein finales Update
    gesendet und die Verbindung geschlossen.
    """
    await websocket.accept()

    # ScanJobService aus App-State holen - robust ueber scope
    scan_jobs = None
    scope = getattr(websocket, "scope", {}) or {}
    # Starlette/FastAPI speichert app in scope["app"]
    app = scope.get("app")
    if app is not None:
        state = getattr(app, "state", None)
        if state is not None:
            scan_jobs = getattr(state, "scan_jobs", None)

    if scan_jobs is None:
        # Letzter Fallback: eigene Instanz mit default Pfad
        from pathlib import Path
        from apps.web.scan_jobs import LocalScanJobService
        job_root = Path.cwd() / "codex_tmp" / "web-jobs"
        scan_jobs = LocalScanJobService(job_root)

    last_log_count = 0
    elapsed = 0.0

    try:
        while elapsed < MAX_CONNECTION_SECONDS:
            try:
                snapshot = scan_jobs.get(job_id)
            except KeyError:
                await websocket.send_json(
                    {"error": "job not found", "job_id": job_id}
                )
                await websocket.close()
                return

            # Logs (nur neue Zeilen)
            logs = snapshot.get("logs", [])
            current_log_count = len(logs)
            new_logs = logs[last_log_count:] if current_log_count > last_log_count else []
            last_log_count = current_log_count

            update: dict[str, Any] = {
                "job_id": job_id,
                "status": snapshot.get("status"),
                "progress_percent": snapshot.get("progress_percent"),
                "current_phase": snapshot.get("current_phase"),
                "current_substep": snapshot.get("current_substep"),
                "completed_substeps": snapshot.get("completed_substeps", []),
                "new_logs": new_logs,
                "timestamp": snapshot.get("updated_at"),
            }
            await websocket.send_json(update)

            status = snapshot.get("status", "")
            if status in ("completed", "failed", "cancelled"):
                await websocket.close()
                return

            await asyncio.sleep(POLL_INTERVAL_SECONDS)
            elapsed += POLL_INTERVAL_SECONDS

        # Timeout
        await websocket.send_json(
            {"error": "connection timeout", "job_id": job_id}
        )
        await websocket.close()

    except WebSocketDisconnect:
        pass
    except Exception:
        try:
            await websocket.close()
        except Exception:
            pass
