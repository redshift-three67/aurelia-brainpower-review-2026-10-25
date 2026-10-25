"""FastAPI-App fuer Morphic Engine V1 Web-UI.

DEPRECATED: Diese Datei ist veraltet. Bitte verwende apps/web/main.py
stattdessen, die alle Endpunkte dieser App enthaelt plus zusaetzliche
Endpoints (health, sources, privacy, report-catalog).

Die Funktionen wurden migriert nach:
  - apps/web/emf.py (EMF-Endpoints + WebSocket)
  - apps/web/amplifiers.py (Amplifier-List + Match)
  - apps/web/profiles.py (Profile-List)
  - apps/web/analyze.py (12-Step Workflow)
  - apps/web/main.py (Status, workflow-stepping, CORS, No-Cache, web_ui)

Enthaelt:
  - Statische Dateien (HTML/CSS/JS) unter /ui/
  - API-Endpunkte unter /api/v1/
  - WebSocket /api/v1/emf/ws
"""

from __future__ import annotations

import asyncio
import json
import os
import re
import subprocess
import threading
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

ROOT = Path(__file__).resolve().parent
UI_DIR = ROOT / "web_ui"

app = FastAPI(
    title="Morphic Engine V1 - Web-UI",
    version="1.0.0",
    description="Interaktive Workflow-UI nach Radi144-Blueprint",
)

# CORS (loopback-safe)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_no_cache_headers(request, call_next):
    response = await call_next(request)
    if request.url.path.startswith("/ui") or request.url.path.startswith(
        "/workflow-stepping"
    ):
        response.headers["Cache-Control"] = (
            "no-store, no-cache, must-revalidate, max-age=0"
        )
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response


# Statische Frontend-Dateien
if UI_DIR.exists():
    app.mount("/ui", StaticFiles(directory=str(UI_DIR), html=True), name="ui")


# ---------------------------------------------------------------------------
# Hilfsfunktionen
# ---------------------------------------------------------------------------


def _safe_float(val: Any, default: float = 0.0) -> float:
    try:
        return float(val)
    except (TypeError, ValueError):
        return default


def _measure_emf() -> dict:
    """Misst EMF-Werte (vereinfachte Version von step05_emf)."""
    try:
        import os

        data = os.urandom(2048)
        import numpy as np

        arr = np.frombuffer(data, dtype=np.uint8).astype(float)
        mean = arr.mean()
        diff = np.diff(arr)
        autocorr = float(np.corrcoef(arr[:-1], arr[1:])[0, 1]) if len(arr) > 1 else 0.0
        shannon = -np.sum((arr / 256.0) * np.log2(arr / 256.0 + 1e-12))
        entropy_score = float(
            max(
                0.0,
                min(1.0, 0.4 * (shannon / 8.0) + 0.3 * (1 - abs(autocorr)) + 0.3 * 0.5),
            )
        )

        timings = []
        for _ in range(20):
            t0 = time.perf_counter_ns()
            s = sum(i * i for i in range(50))
            t1 = time.perf_counter_ns()
            timings.append((t1 - t0) / 1e6)
        jitter = float(np.std(timings))

        try:
            import psutil

            sys_load = (
                psutil.cpu_percent(interval=0.05) + psutil.virtual_memory().percent
            ) / 200.0
        except Exception:
            sys_load = 0.3

        emf_index = float(
            max(
                0.0,
                min(
                    1.0,
                    0.30 * (1.0 - entropy_score)
                    + 0.25 * min(1.0, jitter)
                    + 0.20 * sys_load
                    + 0.10 * abs(autocorr)
                    + 0.15 * 0.0,
                ),
            )
        )

        rec = "niedrig"
        if emf_index > 0.6:
            rec = "hoch"
        elif emf_index > 0.3:
            rec = "mittel"

        counters = [528.0]
        if emf_index > 0.3:
            counters.append(741.0)
        if emf_index > 0.6:
            counters.append(963.0)
            counters.append(174.0)

        return {
            "timestamp": datetime.now().isoformat(),
            "emf_index": round(emf_index, 4),
            "entropy_score": round(entropy_score, 4),
            "timing_jitter_ms": round(jitter, 4),
            "system_load": round(sys_load, 4),
            "recommendation": rec,
            "counter_frequencies": counters,
        }
    except Exception as exc:
        return {"error": str(exc), "emf_index": 0.0}


JOBS: Dict[str, Dict[str, Any]] = {}
JOB_LOCK = threading.Lock()


def _client_folder_name(
    name: str, first_name: str, birth_date: str, birth_place: str
) -> str:
    return f"{name}_{first_name}_{birth_date}_{birth_place}".strip("_")


def _latest_session_dir(client_folder: str) -> str:
    base = Path(r"C:\Benutzer_Archive_Start") / client_folder
    if not base.exists():
        return ""
    dirs = [p for p in base.iterdir() if p.is_dir()]
    if not dirs:
        return ""
    latest = max(dirs, key=lambda p: p.stat().st_mtime)
    return str(latest)


def _job_update(job_id: str, **fields: Any) -> None:
    with JOB_LOCK:
        job = JOBS.get(job_id)
        if not job:
            return
        job.update(fields)
        job["updated_at"] = datetime.now().isoformat()


def _job_log(job_id: str, line: str) -> None:
    with JOB_LOCK:
        job = JOBS.get(job_id)
        if not job:
            return
        logs = job.setdefault("logs", [])
        logs.append(line)
        if len(logs) > 200:
            del logs[:-200]


def _job_phase(job_id: str, step: int, label: str) -> None:
    with JOB_LOCK:
        job = JOBS.get(job_id)
        if not job:
            return
        history = job.setdefault("phase_history", [])
        if not history or history[-1].get("label") != label:
            history.append(
                {
                    "step": step,
                    "label": label,
                    "timestamp": datetime.now().isoformat(),
                }
            )


def _parse_progress(job_id: str, line: str, top_n: int) -> None:
    txt = line.strip()
    if not txt:
        return
    current_step = 1
    step_label = "Initialisierung"
    progress = 2

    if "PHASE 1: Screening" in txt:
        current_step, step_label, progress = 3, "Screening aller Haupt-Profile", 15
    elif "TOP-" in txt and "RELEVANTE PROFILE" in txt:
        current_step, step_label, progress = 4, "Top-Profile Auswahl", 30
    elif "PHASE 2: Vollstaendige Analyse" in txt:
        current_step, step_label, progress = 5, "Vollstaendige Profilanalysen", 40
    elif "Vollstaendige Analyse:" in txt:
        current_step, step_label = 5, txt
        progress = 45
    elif "Profil " in txt and "abgeschlossen" in txt:
        done = len(
            re.findall(
                r"Profil .* abgeschlossen",
                "\n".join(JOBS.get(job_id, {}).get("logs", [])),
            )
        )
        progress = min(70, 45 + done * max(1, int(25 / max(1, top_n))))
        current_step, step_label = 5, "Profilanalyse abgeschlossen"
    elif "Quantum-Synergy Report erstellt" in txt or "Quantum-Synergy Report" in txt:
        current_step, step_label, progress = 7, "Synergy-Gesamtbericht", 78
    elif (
        "Remedy-Kombinationen Report erstellt" in txt
        or "Remedy-Kombinationen Report" in txt
    ):
        current_step, step_label, progress = 8, "Remedy-Bericht", 84
    elif "Deutungsbericht erstellt" in txt or "Deutungsbericht" in txt:
        current_step, step_label, progress = 9, "Deutungsbericht", 90
    elif "Trendbericht erstellt" in txt or "Trendbericht" in txt:
        current_step, step_label, progress = 10, "Trendanalyse", 95
    elif "Die HTML-Berichte wurden unter" in txt or "Export:" in txt:
        current_step, step_label, progress = 11, "Archivierung", 98

    _job_update(
        job_id, current_step=current_step, step_label=step_label, progress=progress
    )
    _job_phase(job_id, current_step, step_label)


def _run_cli_top_scan_job(job_id: str, payload: dict) -> None:
    name = str(payload.get("name", "")).strip()
    first_name = str(payload.get("first_name", "")).strip()
    birth_date = str(payload.get("birth_date", "")).strip()
    birth_place = str(payload.get("birth_place", "")).strip()
    focus = str(payload.get("focus", "")).strip()
    top_n = int(payload.get("top_n", 5))
    profile_level = int(payload.get("profile_level", 3))
    harmonize = bool(payload.get("harmonize", False))
    harm_duration = int(payload.get("harm_duration", 5))

    python_exe = str(ROOT / ".venv" / "Scripts" / "python.exe")
    if not Path(python_exe).exists():
        python_exe = "python"

    cmd = [
        python_exe,
        "-u",
        "-m",
        "apps.cli.main",
        "scan",
        "top3-scan",
        name,
        first_name,
        "--birth-date",
        birth_date,
        "--birth-place",
        birth_place,
        "--top-n",
        str(top_n),
        "--level",
        str(profile_level),
    ]
    if focus:
        cmd.extend(["--focus", focus])

    _job_update(
        job_id,
        status="running",
        progress=5,
        current_step=2,
        step_label="CLI-Workflow startet",
        command=cmd,
    )
    _job_log(job_id, "Starte produktiven Top-N Multiplex-Scan...")

    proc = subprocess.Popen(
        cmd,
        cwd=str(ROOT),
        env={**os.environ, "PYTHONUNBUFFERED": "1", "PYTHONIOENCODING": "utf-8"},
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        bufsize=1,
    )
    try:
        assert proc.stdout is not None
        for raw_line in proc.stdout:
            line = raw_line.rstrip()
            _job_log(job_id, line)
            _parse_progress(job_id, line, top_n)

        exit_code = proc.wait()
        client_folder = _client_folder_name(name, first_name, birth_date, birth_place)
        latest_session = _latest_session_dir(client_folder)

        result: Dict[str, Any] = {
            "exit_code": exit_code,
            "client_folder": client_folder,
            "latest_session": latest_session,
            "focus": focus,
            "top_n": top_n,
            "profile_level": profile_level,
        }

        if exit_code == 0 and harmonize:
            try:
                from services.harmonization_worker import start_harmonization_job

                _job_update(
                    job_id, current_step=12, step_label="Harmonisierung", progress=97
                )
                hjob = start_harmonization_job(
                    target_frequency=432.0,
                    duration_minutes=harm_duration,
                    intention="harmonization",
                    hardware_config={
                        "use_cpu": True,
                        "use_ram": True,
                        "use_gpu": False,
                        "use_websocket": False,
                    },
                )
                result["harmonization_job_id"] = getattr(hjob, "job_id", "")
                _job_log(
                    job_id,
                    f"Harmonisierung gestartet: {result['harmonization_job_id']}",
                )
            except Exception as exc:
                _job_log(job_id, f"Harmonisierung konnte nicht gestartet werden: {exc}")

        if exit_code == 0:
            _job_update(
                job_id,
                status="completed",
                progress=100,
                current_step=12,
                step_label="Abgeschlossen",
                result=result,
            )
        else:
            _job_update(
                job_id,
                status="failed",
                progress=100,
                current_step=12,
                step_label="Fehlgeschlagen",
                error=f"CLI exit code {exit_code}",
                result=result,
            )
    except Exception as exc:
        _job_log(job_id, f"Fehler: {exc}")
        _job_update(
            job_id,
            status="failed",
            progress=100,
            current_step=12,
            step_label="Fehlgeschlagen",
            error=str(exc),
        )
    finally:
        if proc.poll() is None:
            proc.kill()


# ---------------------------------------------------------------------------
# Root + Frontend
# ---------------------------------------------------------------------------


@app.get("/")
async def root():
    """Weiterleitung zum Frontend."""
    return HTMLResponse(
        '<meta http-equiv="refresh" content="0; url=/ui/">',
        status_code=200,
    )


@app.get("/workflow-stepping")
async def workflow_stepping():
    """Serviert die 12-Step Dokumentationsseite direkt ueber den Web-Server."""
    path = ROOT / "apps" / "cli" / "workflow" / "workflow_stepping.html"
    if not path.exists():
        return HTMLResponse(
            "<h1>workflow_stepping.html nicht gefunden</h1>", status_code=404
        )
    return HTMLResponse(path.read_text(encoding="utf-8"), status_code=200)


@app.get("/api/v1/status")
async def api_status():
    return {"status": "ok", "version": "1.0.0", "server": "Morphic Engine V1"}


# ---------------------------------------------------------------------------
# Profile
# ---------------------------------------------------------------------------


@app.get("/api/v1/profiles")
async def list_profiles(level: int = 0):
    """Listet Profile, optional gefiltert nach Level."""
    try:
        from core.profile_sync import (
            get_all_profiles,
            get_profiles_by_level,
            get_level_stats,
        )

        if level > 0:
            profiles = get_profiles_by_level(level)
        else:
            profiles = get_all_profiles()
        stats = get_level_stats()
        return {
            "count": len(profiles),
            "level": level,
            "stats": stats,
            "items": [
                {
                    "name": p.name,
                    "display_name": p.display_name,
                    "level": getattr(p, "level", 3),
                    "enabled": p.enabled,
                }
                for p in profiles
            ],
        }
    except Exception as exc:
        return JSONResponse({"error": str(exc)}, status_code=500)


# ---------------------------------------------------------------------------
# Amplifier
# ---------------------------------------------------------------------------


@app.get("/api/v1/amplifier/list")
async def amplifier_list():
    """Listet alle 12 Amplifier."""
    try:
        from apps.cli.workflow.step06_amplifier import _AMPLIFIERS

        return {"count": len(_AMPLIFIERS), "amplifiers": _AMPLIFIERS}
    except Exception as exc:
        return JSONResponse({"error": str(exc)}, status_code=500)


@app.post("/api/v1/amplifier/match")
async def amplifier_match(payload: dict):
    """Cosinus-Match fuer Client-Daten."""
    try:
        from apps.cli.workflow.step06_amplifier import _AMPLIFIERS, _amp_vector
        import numpy as np

        client_freq = _safe_float(payload.get("client_frequency"), 432.0)
        focus = str(payload.get("focus", ""))
        top_n = int(payload.get("top_n", 3))

        cvec = np.zeros(12)
        cvec[0] = (client_freq - 20) / 1980
        cvec[1] = (client_freq * 1.5 - 20) / 1980
        cvec[6] = client_freq / 1000
        import hashlib

        focus_hash = (
            int(hashlib.md5(focus.encode()).hexdigest()[:6], 16) if focus else 0
        )
        cvec[8] = (focus_hash % 360) / 360

        cnorm = np.linalg.norm(cvec) or 1.0
        scored = []
        for amp in _AMPLIFIERS:
            avec = _amp_vector(amp)
            anorm = np.linalg.norm(avec) or 1.0
            cos_sim = float(np.dot(cvec, avec) / (cnorm * anorm))
            total = 0.55 * cos_sim + 0.20 * 0.5 + 0.25 * 0.3
            scored.append(
                {**amp, "score": round(total, 4), "cosine": round(cos_sim, 4)}
            )
        scored.sort(key=lambda x: x["score"], reverse=True)
        return {"recommendations": scored[:top_n], "client_frequency": client_freq}
    except Exception as exc:
        return JSONResponse({"error": str(exc)}, status_code=500)


# ---------------------------------------------------------------------------
# EMF
# ---------------------------------------------------------------------------

_emf_active = False


@app.post("/api/v1/emf/enable")
async def emf_enable(continuous: bool = False):
    global _emf_active
    _emf_active = True
    return {"status": "active", "continuous": continuous}


@app.post("/api/v1/emf/disable")
async def emf_disable():
    global _emf_active
    _emf_active = False
    return {"status": "inactive"}


@app.get("/api/v1/emf/status")
async def emf_status():
    return {"active": _emf_active}


@app.get("/api/v1/emf/profile")
async def emf_profile():
    return _measure_emf()


@app.get("/api/v1/emf/monitor")
async def emf_monitor():
    """Inline EMF-Dashboard HTML (wie Radi144)."""
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
const wsUrl=(location.protocol==='https:'?'wss://':'ws://')+location.host+'/api/v1/emf/ws';
let ws;
function connect(){ws=new WebSocket(wsUrl);ws.onmessage=e=>{const d=JSON.parse(e.data);update(d)};ws.onclose=()=>{setTimeout(connect,3000)};ws.onerror=()=>{ws.close()}}
function update(d){document.getElementById('emf').textContent=d.emf_index.toFixed(3);document.getElementById('emfBar').style.width=(d.emf_index*100)+'%';document.getElementById('ent').textContent=d.entropy_score.toFixed(3);document.getElementById('jit').textContent=d.timing_jitter_ms.toFixed(2);document.getElementById('load').textContent=d.system_load.toFixed(3);document.getElementById('rec').textContent=d.recommendation;document.getElementById('freq').innerHTML=(d.counter_frequencies||[]).map(f=>f.toFixed(1)+' Hz').join(', ')}
connect();
</script></body></html>""")


# ---------------------------------------------------------------------------
# WebSocket: EMF Live-Stream (5s Push)
# ---------------------------------------------------------------------------


@app.websocket("/api/v1/emf/ws")
async def emf_websocket(websocket: WebSocket):
    await websocket.accept()
    global _emf_active
    _emf_active = True
    try:
        while True:
            payload = _measure_emf()
            await websocket.send_json({"type": "emf_update", **payload})
            await asyncio.sleep(5)
    except WebSocketDisconnect:
        pass
    except Exception:
        pass
    finally:
        _emf_active = False


# ---------------------------------------------------------------------------
# Analyse-Jobs (PS1-/CLI-konformer Flow)
# ---------------------------------------------------------------------------


@app.post("/api/v1/jobs/start")
async def start_job(payload: dict):
    name = str(payload.get("name", "")).strip()
    first_name = str(payload.get("first_name", "")).strip()
    birth_date = str(payload.get("birth_date", "")).strip()
    birth_place = str(payload.get("birth_place", "")).strip()
    if not name or not first_name or not birth_date or not birth_place:
        return JSONResponse(
            {"error": "Name, Vorname, Geburtsdatum und Geburtsort sind erforderlich"},
            status_code=400,
        )

    job_id = uuid.uuid4().hex[:12]
    with JOB_LOCK:
        JOBS[job_id] = {
            "job_id": job_id,
            "status": "queued",
            "progress": 0,
            "current_step": 1,
            "step_label": "Wartet auf Start",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "payload": payload,
            "logs": [],
        }

    thread = threading.Thread(
        target=_run_cli_top_scan_job, args=(job_id, payload), daemon=True
    )
    thread.start()
    return {"job_id": job_id, "status": "queued"}


@app.get("/api/v1/jobs/{job_id}")
async def get_job(job_id: str):
    job = JOBS.get(job_id)
    if not job:
        return JSONResponse({"error": "Job nicht gefunden"}, status_code=404)
    return job


@app.get("/api/v1/jobs")
async def list_jobs():
    return {
        "count": len(JOBS),
        "jobs": [
            {
                "job_id": j["job_id"],
                "status": j.get("status"),
                "progress": j.get("progress"),
                "current_step": j.get("current_step"),
                "step_label": j.get("step_label"),
                "updated_at": j.get("updated_at"),
            }
            for j in JOBS.values()
        ],
    }


# ---------------------------------------------------------------------------
# Analyse (Legacy sync workflow endpoint)
# ---------------------------------------------------------------------------


@app.post("/api/v1/analyze")
async def analyze(payload: dict):
    """Startet den 12-Step Workflow-Scan.

    Payload: {name, first_name, birth_date, birth_place, focus, intention,
              profile_level, top_n, image_path, harmonize, harm_duration}
    """
    try:
        from apps.cli.workflow.orchestrator import run_workflow

        name = str(payload.get("name", "")).strip()
        first_name = str(payload.get("first_name", "")).strip()
        birth_date = str(payload.get("birth_date", "")).strip()
        birth_place = str(payload.get("birth_place", "")).strip()

        if not name or not first_name:
            return JSONResponse(
                {"error": "Name und Vorname erforderlich"}, status_code=400
            )

        state = run_workflow(
            name=name,
            first_name=first_name,
            birth_date=birth_date,
            birth_place=birth_place,
            focus=str(payload.get("focus", "")).strip(),
            intention=str(payload.get("intention", "harmonization")).strip(),
            profile_level=int(payload.get("profile_level", 3)),
            top_n=int(payload.get("top_n", 5)),
            image_path=str(payload.get("image_path", "")).strip(),
            harmonize=bool(payload.get("harmonize", False)),
            harmonize_duration=int(payload.get("harm_duration", 1)),
            verbose=False,
        )

        return {
            "status": "completed",
            "steps_completed": state.step_completed,
            "errors": state.errors,
            "client_frequency": round(state.client_frequency, 2),
            "emf_index": round(state.composite_emf_index, 4),
            "candidate_count": state.candidate_count,
            "matrix_results_count": len(state.matrix_results),
            "quantum_synergies_count": len(state.quantum_synergies),
            "amplifier_recommendations": state.amplifier_recommendations[:3],
            "palette": state.palette,
            "export_paths": state.export_paths,
        }
    except Exception as exc:
        import traceback

        return JSONResponse(
            {"error": str(exc), "traceback": traceback.format_exc()}, status_code=500
        )


# ---------------------------------------------------------------------------
# Harmonisierung
# ---------------------------------------------------------------------------


@app.post("/api/v1/harmonize/start")
async def harmonize_start(payload: dict):
    """Startet eine Harmonisierung."""
    try:
        from services.harmonization_worker import start_harmonization_job

        freq = _safe_float(payload.get("frequency", 432.0))
        duration = int(payload.get("duration", 5))
        intention = str(payload.get("intention", "harmonization"))

        job = start_harmonization_job(
            target_frequency=freq,
            duration_minutes=duration,
            intention=intention,
            hardware_config={
                "use_cpu": True,
                "use_ram": True,
                "use_gpu": False,
                "use_websocket": False,
            },
        )
        return {
            "status": "started",
            "job_id": getattr(job, "job_id", "unknown"),
            "frequency": freq,
            "duration": duration,
        }
    except Exception as exc:
        return JSONResponse({"error": str(exc)}, status_code=500)


@app.get("/api/v1/harmonize/jobs")
async def harmonize_jobs():
    """Listet aktive Harmonisierungs-Jobs."""
    try:
        from services.harmonization_worker import list_all_jobs

        jobs = list_all_jobs()
        return {
            "count": len(jobs),
            "jobs": [
                {
                    "job_id": getattr(j, "job_id", ""),
                    "status": getattr(j, "status", ""),
                    "progress": getattr(j, "progress_percent", 0),
                }
                for j in jobs
            ],
        }
    except Exception as exc:
        return JSONResponse({"error": str(exc)}, status_code=500)


# ---------------------------------------------------------------------------
# Reports
# ---------------------------------------------------------------------------


@app.get("/api/v1/reports/{client_name}")
async def list_reports(client_name: str):
    """Listet Berichte fuer einen Klienten."""
    import os

    paths = {
        "archive": r"C:\Benutzer_Archive_Start",
        "synergy": r"C:\Benutzer_Synergy_Start",
        "remedies": r"C:\Benutzer_Remedies_Start",
        "deutung": r"C:\Benutzer_Deutung_Start",
        "trends": r"C:\Benutzer_Trends_Start",
    }
    result = {}
    for key, base in paths.items():
        if not os.path.exists(base):
            result[key] = []
            continue
        found = []
        for d in os.listdir(base):
            if client_name.lower() in d.lower():
                client_dir = os.path.join(base, d)
                if os.path.isdir(client_dir):
                    for root, dirs, files in os.walk(client_dir):
                        for f in files:
                            if f.endswith((".html", ".json", ".pdf", ".txt")):
                                found.append(
                                    {
                                        "path": os.path.join(root, f).replace(base, ""),
                                        "full_path": os.path.join(root, f),
                                        "name": f,
                                        "size": os.path.getsize(os.path.join(root, f)),
                                    }
                                )
        found.sort(key=lambda item: item["path"], reverse=True)
        result[key] = found
    return result


@app.get("/api/v1/report-preview")
async def report_preview(path: str):
    """Liefert HTML/TXT/JSON Berichtsinhalte fuer die Web-Vorschau."""
    try:
        full = Path(path)
        allowed_roots = [
            Path(r"C:\Benutzer_Archive_Start"),
            Path(r"C:\Benutzer_Synergy_Start"),
            Path(r"C:\Benutzer_Remedies_Start"),
            Path(r"C:\Benutzer_Deutung_Start"),
            Path(r"C:\Benutzer_Trends_Start"),
        ]
        if not full.exists() or not any(
            str(full).startswith(str(root)) for root in allowed_roots
        ):
            return HTMLResponse(
                "<h3>Bericht nicht gefunden oder nicht erlaubt.</h3>", status_code=404
            )

        suffix = full.suffix.lower()
        if suffix == ".html":
            return HTMLResponse(
                full.read_text(encoding="utf-8", errors="replace"), status_code=200
            )
        if suffix == ".pdf":
            raw_url = "/api/v1/report-raw?path=" + str(full)
            return HTMLResponse(
                "<html><body style='margin:0;background:#f7f3ee;'>"
                f"<object data='{raw_url}' type='application/pdf' width='100%' height='100%' style='min-height:95vh;'></object>"
                f"<div style='padding:16px;font-family:Segoe UI,sans-serif;'><a href='{raw_url}' target='_blank'>PDF direkt oeffnen</a></div>"
                "</body></html>",
                status_code=200,
            )
        if suffix in {".txt", ".json"}:
            text = full.read_text(encoding="utf-8", errors="replace")
            return HTMLResponse(
                "<html><body style='font-family:Consolas,monospace;padding:16px;white-space:pre-wrap;'>"
                + text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                + "</body></html>",
                status_code=200,
            )
        return HTMLResponse(
            "<h3>Vorschau fuer dieses Dateiformat nicht verfuegbar.</h3>",
            status_code=200,
        )
    except Exception as exc:
        return HTMLResponse(f"<h3>Vorschau-Fehler: {exc}</h3>", status_code=500)


@app.get("/api/v1/report-raw")
async def report_raw(path: str):
    try:
        full = Path(path)
        allowed_roots = [
            Path(r"C:\Benutzer_Archive_Start"),
            Path(r"C:\Benutzer_Synergy_Start"),
            Path(r"C:\Benutzer_Remedies_Start"),
            Path(r"C:\Benutzer_Deutung_Start"),
            Path(r"C:\Benutzer_Trends_Start"),
        ]
        if not full.exists() or not any(
            str(full).startswith(str(root)) for root in allowed_roots
        ):
            return JSONResponse({"error": "Datei nicht erlaubt"}, status_code=404)
        return FileResponse(str(full))
    except Exception as exc:
        return JSONResponse({"error": str(exc)}, status_code=500)
