"""EMF-Kompensation Endpoints fuer die Morphic Engine Web-App.

Migriert von web_app.py - bereitstellen der EMF-Mess-, Steuerungs- und
WebSocket-Endpoints unter /api/emf/*.
"""
from __future__ import annotations

import asyncio

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

from apps.web.security import verify_api_key
from core.realtime.emf_profile import EMFProfileService

router = APIRouter(prefix="/api/emf", tags=["emf"])

_emf_active = False


def measure_emf() -> dict:
    """Measure operational EMF telemetry through the shared V2 profile service."""
    return EMFProfileService().measure().to_dict()


@router.post("/enable")
async def emf_enable(
    continuous: bool = False,
    _api_key: str | None = Depends(verify_api_key),
) -> dict:
    global _emf_active
    _emf_active = True
    return {"status": "active", "continuous": continuous}


@router.post("/disable")
async def emf_disable(_api_key: str | None = Depends(verify_api_key)) -> dict:
    global _emf_active
    _emf_active = False
    return {"status": "inactive"}


@router.get("/status")
async def emf_status() -> dict:
    return {"active": _emf_active}


@router.get("/profile")
async def emf_profile() -> dict:
    return measure_emf()


@router.get("/monitor")
async def emf_monitor() -> HTMLResponse:
    """Inline EMF-Dashboard HTML."""
    return HTMLResponse("""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>EMF-Monitor</title>
<style>
body{font-family:Arial,sans-serif;background:#0d1117;color:#c9d1d9;margin:0;padding:20px}
h1{color:#58a6ff;font-size:18px}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:16px}
.card{background:#161b22;border:1px solid #30363d;border-radius:8px;padding:16px}
.val{font-size:24px;font-weight:bold;color:#7ee787}
.label{color:#8b949e;font-size:12px;margin-top:4px}
.bar{height:8px;background:#30363d;border-radius:4px;margin-top:8px;overflow:hidden}
.fill{height:100%;background:linear-gradient(90deg,#f85149,#d29922,#7ee787);transition:width 0.5s}
</style></head><body>
<h1>EMF Live-Monitor</h1>
<div class="grid">
<div class="card"><div class="val" id="emf">--</div><div class="label">EMF-Index</div><div class="bar"><div class="fill" id="emfBar" style="width:0%"></div></div></div>
<div class="card"><div class="val" id="ent">--</div><div class="label">Entropy Score</div></div>
<div class="card"><div class="val" id="jit">--</div><div class="label">Jitter (ms)</div></div>
<div class="card"><div class="val" id="load">--</div><div class="label">System Load</div></div>
<div class="card" style="grid-column:span 2"><div class="val" id="rec">--</div><div class="label">Empfehlung</div></div>
<div class="card" style="grid-column:span 2"><div class="label">Counter-Frequencies</div><div id="freq" style="margin-top:8px;font-size:14px;color:#58a6ff"></div></div>
</div>
<script>
const wsUrl=(location.protocol==='https:'?'wss://':'ws://')+location.host+'/api/emf/ws';
let ws;
function connect(){ws=new WebSocket(wsUrl);ws.onmessage=e=>{const d=JSON.parse(e.data);update(d)};ws.onclose=()=>{setTimeout(connect,3000)};ws.onerror=()=>{ws.close()}}
function update(d){document.getElementById('emf').textContent=d.emf_index.toFixed(3);document.getElementById('emfBar').style.width=(d.emf_index*100)+'%';document.getElementById('ent').textContent=d.entropy_score.toFixed(3);document.getElementById('jit').textContent=d.timing_jitter_ms.toFixed(2);document.getElementById('load').textContent=d.system_load.toFixed(3);document.getElementById('rec').textContent=d.recommendation;document.getElementById('freq').innerHTML=(d.counter_frequencies||[]).map(f=>f.toFixed(1)+' Hz').join(', ')}
connect();
</script></body></html>""")


@router.websocket("/ws")
async def emf_websocket(websocket: WebSocket) -> None:
    await websocket.accept()
    global _emf_active
    _emf_active = True
    try:
        while True:
            payload = measure_emf()
            await websocket.send_json({"type": "emf_update", **payload})
            await asyncio.sleep(5)
    except WebSocketDisconnect:
        pass
    except Exception:
        pass
    finally:
        _emf_active = False
