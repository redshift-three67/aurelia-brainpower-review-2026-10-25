"""FastAPI-App fuer Morphic Engine V1 Web-UI.

DEPRECATED: Diese Datei ist veraltet. Bitte verwende apps/web/main.py
stattdessen, die alle Endpunkte dieser App enthaelt plus zusaetzliche
Endpoints (health, sources, privacy, report-catalog).

Die Funktionen wurden migriert nach:
  - apps/web/emf.py (EMF-Endpoints + WebSocket)
  - apps/web/amplifiers.py (Amplifier-List + Match)
  - apps/web/profiles.py (Profile-List)
  - apps/web/analyze.py (12-Step Workflow)
   - apps/web/main.py (Status, workflow-stepping, CORS, No-Cache, moderne Workbench)

Enthaelt:
   - API-Endpunkte unter /api/v1/
"""

from __future__ import annotations

import os
import re
import subprocess
import threading
import uuid
from datetime import datetime
from html import escape as html_escape
from pathlib import Path
from typing import Any, Dict
from urllib.parse import urlencode

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse

from apps.web.emf import legacy_router as legacy_emf_router, router as emf_router
from apps.web.emf_authority import build_emf_telemetry_authority
from apps.web.security import (
    MeasurementPublishPermitMiddleware,
    SessionAuthority,
    revalidate_protected_response,
    verify_api_key,
)

ROOT = Path(__file__).resolve().parent
APP_STATIC_DIR = ROOT / "apps" / "web" / "static"
SHARED_MONITOR_ASSETS = frozenset({"emf-monitor.css", "emf-monitor.js"})
LEGACY_REPORT_ROOTS = (
    Path(r"C:\Benutzer_Archive_Start"),
    Path(r"C:\Benutzer_Synergy_Start"),
    Path(r"C:\Benutzer_Remedies_Start"),
    Path(r"C:\Benutzer_Deutung_Start"),
    Path(r"C:\Benutzer_Trends_Start"),
)
_LEGACY_REPORT_ROOT_KEYS = ("archive", "synergy", "remedies", "deutung", "trends")

app = FastAPI(
    title="Morphic Engine V1 - Web-UI",
    version="1.0.0",
    description="Interaktive Workflow-UI nach Radi144-Blueprint",
)
app.state.session_authority = SessionAuthority()
legacy_runtime_dir = os.getenv("MORPHIC_RUNTIME_DIR")
app.state.emf_telemetry_authority = build_emf_telemetry_authority(
    Path(legacy_runtime_dir) if legacy_runtime_dir else None
)

# CORS (loopback-safe)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.middleware("http")(revalidate_protected_response)


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


app.add_middleware(MeasurementPublishPermitMiddleware)


@app.get("/static/{asset:path}", include_in_schema=False)
async def shared_monitor_asset(asset: str) -> FileResponse:
    if asset not in SHARED_MONITOR_ASSETS:
        raise HTTPException(status_code=404)
    return FileResponse(APP_STATIC_DIR / asset)

app.include_router(emf_router)
app.include_router(legacy_emf_router)


# ---------------------------------------------------------------------------
# Hilfsfunktionen
# ---------------------------------------------------------------------------


def _safe_float(val: Any, default: float = 0.0) -> float:
    try:
        return float(val)
    except (TypeError, ValueError):
        return default


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


def _legacy_report_root_pairs() -> tuple[tuple[str, Path], ...]:
    return tuple(
        (key, Path(root))
        for key, root in zip(_LEGACY_REPORT_ROOT_KEYS, LEGACY_REPORT_ROOTS)
    )


def _legacy_report_token(path: Path) -> str | None:
    for key, root in _legacy_report_root_pairs():
        try:
            resolved_root = root.resolve(strict=False)
            if path.is_relative_to(resolved_root):
                return f"{key}/{path.relative_to(resolved_root).as_posix()}"
        except (OSError, RuntimeError, ValueError):
            continue
    return None


def _resolve_legacy_report_path(path: str) -> Path | None:
    try:
        root_pairs = _legacy_report_root_pairs()
        allowed_roots = tuple(root.resolve(strict=False) for _, root in root_pairs)
        requested = Path(path)
        if requested.is_absolute():
            candidate = requested
        else:
            normalized = path.replace("\\", "/")
            root_key, separator, relative_name = normalized.partition("/")
            roots_by_key = dict(root_pairs)
            if not separator or not relative_name or root_key not in roots_by_key:
                return None
            relative_path = Path(relative_name)
            if relative_path.is_absolute():
                return None
            candidate = roots_by_key[root_key] / relative_path
        full = candidate.resolve(strict=False)
    except (OSError, RuntimeError, ValueError):
        return None
    if not full.exists() or not any(
        full.is_relative_to(root) for root in allowed_roots
    ):
        return None
    return full


def _safe_legacy_job_view(job: dict[str, Any]) -> dict[str, Any]:
    fields = (
        "job_id",
        "status",
        "progress",
        "current_step",
        "step_label",
        "created_at",
        "updated_at",
    )
    return {field: job.get(field) for field in fields if field in job}


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


def _deprecated_ui_response() -> HTMLResponse:
    return HTMLResponse(
        "<h1>Deprecated UI</h1>"
        "<p>Use apps.web.main:app for the modern Workbench.</p>",
        status_code=410,
    )


@app.get("/")
async def root() -> HTMLResponse:
    return _deprecated_ui_response()


@app.get("/ui", include_in_schema=False)
@app.get("/ui/{path:path}", include_in_schema=False)
async def deprecated_ui(path: str = "") -> HTMLResponse:
    del path
    return _deprecated_ui_response()


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
async def amplifier_match(
    payload: dict,
    _api_key: str | None = Depends(verify_api_key),
):
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
# Analyse-Jobs (PS1-/CLI-konformer Flow)
# ---------------------------------------------------------------------------


@app.post("/api/v1/jobs/start")
async def start_job(
    payload: dict,
    _api_key: str | None = Depends(verify_api_key),
):
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
async def get_job(
    job_id: str,
    _api_key: str | None = Depends(verify_api_key),
):
    with JOB_LOCK:
        job = JOBS.get(job_id)
        if not job:
            return JSONResponse({"error": "Job nicht gefunden"}, status_code=404)
        return _safe_legacy_job_view(job)


@app.get("/api/v1/jobs")
async def list_jobs(
    _api_key: str | None = Depends(verify_api_key),
):
    with JOB_LOCK:
        jobs = [_safe_legacy_job_view(job) for job in JOBS.values()]
    return {
        "count": len(jobs),
        "jobs": jobs,
    }


# ---------------------------------------------------------------------------
# Analyse (Legacy sync workflow endpoint)
# ---------------------------------------------------------------------------


@app.post("/api/v1/analyze")
async def analyze(
    payload: dict,
    _api_key: str | None = Depends(verify_api_key),
):
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
async def harmonize_start(
    payload: dict,
    _api_key: str | None = Depends(verify_api_key),
):
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
async def harmonize_jobs(
    _api_key: str | None = Depends(verify_api_key),
):
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
async def list_reports(
    client_name: str,
    _api_key: str | None = Depends(verify_api_key),
):
    """Listet Berichte fuer einen Klienten."""
    result = {}
    for key, base_path in _legacy_report_root_pairs():
        base = Path(base_path)
        if not os.path.exists(base):
            result[key] = []
            continue
        try:
            resolved_base = base.resolve(strict=True)
        except (OSError, RuntimeError, ValueError):
            result[key] = []
            continue
        found = []
        for d in os.listdir(base):
            if client_name.lower() in d.lower():
                client_dir = base / d
                try:
                    resolved_client_dir = client_dir.resolve(strict=True)
                except (OSError, RuntimeError, ValueError):
                    continue
                if not resolved_client_dir.is_relative_to(
                    resolved_base
                ) or not resolved_client_dir.is_dir():
                    continue
                for root, dirs, files in os.walk(resolved_client_dir):
                    root_path = Path(root)
                    try:
                        resolved_root = root_path.resolve(strict=True)
                    except (OSError, RuntimeError, ValueError):
                        dirs.clear()
                        continue
                    if not resolved_root.is_relative_to(resolved_base):
                        dirs.clear()
                        continue
                    safe_dirs = []
                    for directory in dirs:
                        try:
                            resolved_directory = (root_path / directory).resolve(
                                strict=True
                            )
                        except (OSError, RuntimeError, ValueError):
                            continue
                        if resolved_directory.is_relative_to(resolved_base):
                            safe_dirs.append(directory)
                    dirs[:] = safe_dirs
                    for f in files:
                        if not f.endswith((".html", ".json", ".pdf", ".txt")):
                            continue
                        try:
                            report_path = (root_path / f).resolve(strict=True)
                        except (OSError, RuntimeError, ValueError):
                            continue
                        if not report_path.is_relative_to(
                            resolved_base
                        ) or not report_path.is_file():
                            continue
                        try:
                            size = report_path.stat().st_size
                        except OSError:
                            continue
                        found.append(
                            {
                                "path": (
                                    f"{key}/"
                                    f"{report_path.relative_to(resolved_base).as_posix()}"
                                ),
                                "name": f,
                                "size": size,
                            }
                        )
        found.sort(key=lambda item: item["path"], reverse=True)
        result[key] = found
    return result


@app.get("/api/v1/report-preview")
async def report_preview(
    path: str,
    _api_key: str | None = Depends(verify_api_key),
):
    """Liefert HTML/TXT/JSON Berichtsinhalte fuer die Web-Vorschau."""
    try:
        full = _resolve_legacy_report_path(path)
        if full is None:
            return HTMLResponse(
                "<h3>Bericht nicht gefunden oder nicht erlaubt.</h3>", status_code=404
            )

        suffix = full.suffix.lower()
        if suffix == ".html":
            return HTMLResponse(
                "<html><body><pre>"
                + html_escape(full.read_text(encoding="utf-8", errors="replace"))
                + "</pre></body></html>",
                status_code=200,
            )
        if suffix == ".pdf":
            token = _legacy_report_token(full)
            if token is None:
                return HTMLResponse(
                    "<h3>Bericht nicht gefunden oder nicht erlaubt.</h3>",
                    status_code=404,
                )
            raw_url = "/api/v1/report-raw?" + urlencode({"path": token})
            escaped_raw_url = html_escape(raw_url, quote=True)
            return HTMLResponse(
                "<html><body style='margin:0;background:#f7f3ee;'>"
                f'<object data="{escaped_raw_url}" type="application/pdf" width="100%" height="100%" style="min-height:95vh;"></object>'
                f'<div style="padding:16px;font-family:Segoe UI,sans-serif;"><a href="{escaped_raw_url}" target="_blank">PDF direkt oeffnen</a></div>'
                "</body></html>",
                status_code=200,
            )
        if suffix in {".txt", ".json"}:
            text = full.read_text(encoding="utf-8", errors="replace")
            return HTMLResponse(
                "<html><body style='font-family:Consolas,monospace;padding:16px;white-space:pre-wrap;'><pre>"
                + html_escape(text)
                + "</pre>"
                + "</body></html>",
                status_code=200,
            )
        return HTMLResponse(
            "<h3>Vorschau fuer dieses Dateiformat nicht verfuegbar.</h3>",
            status_code=200,
        )
    except Exception:
        return HTMLResponse("<h3>Vorschau derzeit nicht verfuegbar.</h3>", status_code=500)


@app.get("/api/v1/report-raw")
async def report_raw(
    path: str,
    _api_key: str | None = Depends(verify_api_key),
):
    try:
        full = _resolve_legacy_report_path(path)
        if full is None:
            return JSONResponse({"error": "Datei nicht erlaubt"}, status_code=404)
        return FileResponse(str(full))
    except Exception:
        return JSONResponse(
            {"error": "Datei derzeit nicht verfuegbar"},
            status_code=500,
        )
