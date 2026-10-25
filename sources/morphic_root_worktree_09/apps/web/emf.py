"""EMF-Kompensation Endpoints fuer die Morphic Engine Web-App.

Migriert von web_app.py - bereitstellen der EMF-Mess-, Steuerungs- und
WebSocket-Endpoints unter /api/emf/*.
"""
from __future__ import annotations

import asyncio

from fastapi import APIRouter, Depends, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

from apps.web.emf_authority import EmfTelemetryAuthority
from apps.web.security import (
    capture_authenticated_request_generation,
    capture_authenticated_websocket_generation,
    register_measurement_publish_permit,
    register_request_authentication_compensation,
    revalidate_authenticated_request_generation,
    verify_api_key,
    websocket_authenticated,
    websocket_generation_is_current,
)
from core.realtime.emf_profile import EMFProfileService

router = APIRouter(prefix="/api/emf", tags=["emf"])
legacy_router = APIRouter(prefix="/api/v1/emf", tags=["emf-legacy"])
EMF_ACTIVATION_POLICY = "until_manually_disabled"
EMF_MEASUREMENT_LABEL = "System-/Entropie-basierter EMF-Proxy-Index"


def emf_status_payload(authority: EmfTelemetryAuthority) -> dict[str, object]:
    return {
        "active": authority.is_enabled(),
        "activation_policy": EMF_ACTIVATION_POLICY,
        "measurement_label": EMF_MEASUREMENT_LABEL,
    }


def measure_emf() -> dict:
    """Measure operational EMF telemetry through the shared V2 profile service."""
    return EMFProfileService().measure().to_dict()


@router.post("/enable")
@legacy_router.post("/enable")
async def emf_enable(
    request: Request,
    continuous: bool = False,
    _api_key: str | None = Depends(verify_api_key),
) -> dict[str, object]:
    del continuous
    authority = request.app.state.emf_telemetry_authority
    authentication_generation = capture_authenticated_request_generation(request)
    authority_revision = await asyncio.to_thread(authority.set_enabled, True)
    register_request_authentication_compensation(
        request,
        lambda: authority.compensate_to_disabled_if_current(authority_revision),
    )
    await asyncio.to_thread(
        revalidate_authenticated_request_generation,
        request,
        authentication_generation,
    )
    return await asyncio.to_thread(emf_status_payload, authority)


@router.post("/disable")
@legacy_router.post("/disable")
async def emf_disable(
    request: Request,
    _api_key: str | None = Depends(verify_api_key),
) -> dict[str, object]:
    authority = request.app.state.emf_telemetry_authority
    authentication_generation = capture_authenticated_request_generation(request)
    authority_revision = await asyncio.to_thread(authority.set_enabled, False)
    register_request_authentication_compensation(
        request,
        lambda: authority.compensate_to_disabled_if_current(authority_revision),
    )
    await asyncio.to_thread(
        revalidate_authenticated_request_generation,
        request,
        authentication_generation,
    )
    return await asyncio.to_thread(emf_status_payload, authority)


@router.get("/status")
@legacy_router.get("/status")
async def emf_status(
    request: Request,
    _api_key: str | None = Depends(verify_api_key),
) -> dict[str, object]:
    return await asyncio.to_thread(
        emf_status_payload,
        request.app.state.emf_telemetry_authority,
    )


@router.get("/profile")
@legacy_router.get("/profile")
async def emf_profile(
    request: Request,
    _api_key: str | None = Depends(verify_api_key),
) -> dict:
    authority = request.app.state.emf_telemetry_authority
    authentication_generation = capture_authenticated_request_generation(request)
    measurement_generation = await asyncio.to_thread(authority.begin_measurement)
    if measurement_generation is None:
        raise HTTPException(status_code=409, detail="EMF telemetry is disabled")
    payload = measure_emf()
    revalidate_authenticated_request_generation(
        request, authentication_generation
    )
    if not await asyncio.to_thread(
        authority.measurement_is_current,
        measurement_generation,
    ):
        raise HTTPException(status_code=409, detail="EMF telemetry is disabled")
    register_measurement_publish_permit(
        request,
        authority,
        measurement_generation,
    )
    return payload


@router.get("/monitor")
@legacy_router.get("/monitor")
async def emf_monitor(
    _api_key: str | None = Depends(verify_api_key),
) -> HTMLResponse:
    """CSP-kompatibles EMF-Dashboard mit statischen Same-Origin-Assets."""
    return HTMLResponse("""<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>EMF-Monitor</title>
  <link rel="icon" href="data:,">
  <link rel="stylesheet" href="/static/emf-monitor.css">
  <script src="/static/emf-monitor.js" defer></script>
</head>
<body>
  <h1>System-/Entropie-basierter EMF-Proxy-Index</h1>
  <p>Abgeleiteter System-/Entropie-Proxy; keine physische Feldmessung.</p>
  <p class="connection-state" id="connectionState" role="status">Verbindung wird aufgebaut …</p>
  <main class="grid">
    <section class="card">
      <div class="val" id="emf">--</div>
      <div class="label">System-/Entropie-basierter EMF-Proxy-Index</div>
      <progress class="emf-progress" id="emfBar" max="1" aria-label="System-/Entropie-basierter EMF-Proxy-Index" hidden></progress>
    </section>
    <section class="card monitor-source-card">
      <div class="val" id="ent">--</div>
      <div class="label">Entropie</div>
      <div class="monitor-source-meta">
        <code class="monitor-source-key">rng</code>
        <span class="monitor-source-status status-unknown" id="entStatus">unknown</span>
      </div>
    </section>
    <section class="card monitor-source-card">
      <div class="val" id="jit">--</div>
      <div class="label">Jitter (ms)</div>
      <div class="monitor-source-meta">
        <code class="monitor-source-key">cpu_timing</code>
        <span class="monitor-source-status status-unknown" id="jitStatus">unknown</span>
      </div>
    </section>
    <section class="card monitor-source-card">
      <div class="val" id="load">--</div>
      <div class="label">Systemlast</div>
      <div class="monitor-source-meta">
        <code class="monitor-source-key">system_load</code>
        <span class="monitor-source-status status-unknown" id="loadStatus">unknown</span>
      </div>
    </section>
    <section class="card monitor-source-card">
      <div class="val" id="sensor">--</div>
      <div class="label">Sensorentropie</div>
      <div class="monitor-source-meta">
        <code class="monitor-source-key">sensor_entropy</code>
        <span class="monitor-source-status status-unknown" id="sensorStatus">unknown</span>
      </div>
    </section>
    <section class="card wide"><div class="val" id="rec">--</div><div class="label">Empfehlung</div></section>
    <section class="card wide"><div class="label">Counter-Frequencies</div><div class="frequency-list" id="freq">--</div></section>
  </main>
</body>
</html>""")


@router.websocket("/ws")
@legacy_router.websocket("/ws")
async def emf_websocket(websocket: WebSocket) -> None:
    try:
        scope = getattr(websocket, "scope", {}) or {}
        app = scope.get("app")
        state = getattr(app, "state", None) if app is not None else None
        if state is None:
            await websocket.close(code=1011)
            return
        authentication_generation = capture_authenticated_websocket_generation(
            websocket,
            state,
            websocket_authenticated,
        )
        if authentication_generation is None:
            await websocket.close(code=4401)
            return
        authority = state.emf_telemetry_authority
        if not await asyncio.to_thread(authority.is_enabled):
            await websocket.close(code=4409)
            return
        await websocket.accept()
        while True:
            if not websocket_generation_is_current(
                websocket, state, authentication_generation
            ):
                await websocket.close(code=4401)
                return
            measurement_generation = await asyncio.to_thread(authority.begin_measurement)
            if measurement_generation is None:
                await websocket.close(code=4409)
                return
            payload = measure_emf()
            if not websocket_generation_is_current(
                websocket, state, authentication_generation
            ):
                await websocket.close(code=4401)
                return
            if not await asyncio.to_thread(
                authority.measurement_is_current,
                measurement_generation,
            ):
                await websocket.close(code=4409)
                return
            if not websocket_generation_is_current(
                websocket, state, authentication_generation
            ):
                await websocket.close(code=4401)
                return
            if not await asyncio.to_thread(
                authority.measurement_is_current,
                measurement_generation,
            ):
                await websocket.close(code=4409)
                return
            async with authority.async_publish_permit(
                measurement_generation
            ) as permitted:
                if not permitted:
                    await websocket.close(code=4409)
                    return
                if not websocket_generation_is_current(
                    websocket, state, authentication_generation
                ):
                    await websocket.close(code=4401)
                    return
                await websocket.send_json({"type": "emf_update", **payload})
            await asyncio.sleep(5)
    except WebSocketDisconnect:
        return
    except Exception:
        await _close_internal_error(websocket)


async def _close_internal_error(websocket: WebSocket) -> None:
    try:
        await websocket.close(code=1011)
    except Exception:
        return
