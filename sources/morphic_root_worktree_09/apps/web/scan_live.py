"""WebSocket Live-Updates fuer Scan-Job-Fortschritt.

Bietet einen WebSocket-Endpoint unter /api/scan/jobs/{job_id}/ws
der serverseitig den Job-Status pollt und Updates an verbundene
Clients pusht (alle 2 Sekunden bis Job abgeschlossen).
"""
from __future__ import annotations

import asyncio
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from apps.web.security import get_api_key, websocket_authenticated
from apps.web.authority_ids import AuthorityIdError, validate_authority_id
from apps.web.scan_diagnostics import safe_scan_diagnostics
from apps.web.scan_jobs import ScanJobOwnershipError
from core.compliance.operator_context import operator_owner_scope

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
    try:
        job_id = validate_authority_id(job_id)
    except AuthorityIdError:
        await websocket.close(code=4404)
        return

    scope = getattr(websocket, "scope", {}) or {}
    app = scope.get("app")
    state = getattr(app, "state", None) if app is not None else None
    scan_jobs = getattr(state, "scan_jobs", None) if state is not None else None
    if scan_jobs is None:
        await websocket.close(code=1011)
        return

    authentication_required = get_api_key() is not None
    if not websocket_authenticated(websocket, state, authentication_required):
        await websocket.close(code=4401)
        return

    try:
        initial_snapshot = scan_jobs.get_owned(
            job_id,
            expected_owner_id=operator_owner_scope(state.operator_context),
        )
    except KeyError:
        await websocket.close(code=4404)
        return
    except ScanJobOwnershipError:
        await websocket.close(code=4403)
        return

    await websocket.accept()

    previous_diagnostics: list[str] = []
    elapsed = 0.0

    try:
        while elapsed < MAX_CONNECTION_SECONDS:
            if not websocket_authenticated(websocket, state, authentication_required):
                await websocket.close(code=4401)
                return
            try:
                snapshot = scan_jobs.get_owned(
                    job_id,
                    expected_owner_id=operator_owner_scope(state.operator_context),
                )
            except KeyError:
                current_auth_required = get_api_key() is not None
                if not websocket_authenticated(websocket, state, current_auth_required):
                    await websocket.close(code=4401)
                    return
                await websocket.send_json(
                    {"error": "job not found"}
                )
                await websocket.close()
                return
            except ScanJobOwnershipError:
                await websocket.close(code=4403)
                return

            # Logs (nur neue Zeilen)
            diagnostics = safe_scan_diagnostics(snapshot)
            overlap = 0
            maximum_overlap = min(len(previous_diagnostics), len(diagnostics))
            for size in range(maximum_overlap, 0, -1):
                if previous_diagnostics[-size:] == diagnostics[:size]:
                    overlap = size
                    break
            new_logs = diagnostics[overlap:]
            previous_diagnostics = diagnostics

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
            current_auth_required = get_api_key() is not None
            if not websocket_authenticated(websocket, state, current_auth_required):
                await websocket.close(code=4401)
                return
            try:
                latest_snapshot = scan_jobs.get_owned(
                    job_id,
                    expected_owner_id=operator_owner_scope(state.operator_context),
                )
                current_auth_required = get_api_key() is not None
                if not websocket_authenticated(websocket, state, current_auth_required):
                    await websocket.close(code=4401)
                    return
            except KeyError:
                await websocket.close(code=4404)
                return
            except ScanJobOwnershipError:
                await websocket.close(code=4403)
                return
            await websocket.send_json(update)

            status = snapshot.get("status", "")
            if status in ("completed", "failed", "cancelled", "stopped"):
                await websocket.close()
                return

            await asyncio.sleep(POLL_INTERVAL_SECONDS)
            elapsed += POLL_INTERVAL_SECONDS

        # Timeout
        current_auth_required = get_api_key() is not None
        if not websocket_authenticated(websocket, state, current_auth_required):
            await websocket.close(code=4401)
            return
        try:
            latest_snapshot = scan_jobs.get_owned(
                job_id,
                expected_owner_id=operator_owner_scope(state.operator_context),
            )
            current_auth_required = get_api_key() is not None
            if not websocket_authenticated(websocket, state, current_auth_required):
                await websocket.close(code=4401)
                return
        except (KeyError, ScanJobOwnershipError):
            await websocket.close(code=4403)
            return
        await websocket.send_json(
            {"error": "connection timeout"}
        )
        await websocket.close()

    except WebSocketDisconnect:
        pass
    except Exception:
        try:
            await websocket.close()
        except Exception:
            pass


@router.websocket("/api/scan/jobs/{invalid_job_id:path}/ws")
async def reject_invalid_scan_job_live(
    websocket: WebSocket,
    invalid_job_id: str,
) -> None:
    await websocket.close(code=4404)
