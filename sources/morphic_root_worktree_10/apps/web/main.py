from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path
from typing import Any, Sequence

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, ConfigDict

from apps.web.amplifiers import router as amplifier_router
from apps.web.analyze import router as analyze_router
from apps.web.contracts import (
    Phase1ScanJobResponse,
    Phase1ScanPreviewResponse,
    Phase1ScanRequest,
)
from apps.web.display_scores import adaptive_result_limit
from apps.web.emf import router as emf_router
from apps.web.harmonization import (
    HarmonizationJobStore,
    WorkerHarmonizationService,
    normalize_harmonization_mode,
    resolve_harmonization_intention,
)
from apps.web.launcher import build_phase1_scan_launcher
from apps.web.profiles import router as profiles_router
from apps.web.reports import ReportCatalog
from apps.web.scan_jobs import LocalScanJobService, ScanJobStore
from apps.web.scan_live import router as scan_live_router
from apps.web.security import rate_limit_middleware, verify_api_key
from apps.web.synergy import router as synergy_router
from core.compliance.runtime_manifest import RuntimeManifestService
from core.db.health import collect_runtime_health
from core.hardware.drivers import HardwareDriverRegistry
from core.source_registry import SourceRegistry

STATIC_DIR = Path(__file__).with_name("static")
ROOT_DIR = Path(__file__).resolve().parents[2]
WEB_UI_DIR = ROOT_DIR / "web_ui"


def _parse_session_ts(value: str):
    """Parst einen Session-Zeitstempel-Praefix (YYYYMMDD_HHMMSS)."""
    from datetime import datetime

    try:
        return datetime.strptime(value, "%Y%m%d_%H%M%S")
    except ValueError:
        return None
WORKFLOW_STEPPING_HTML = ROOT_DIR / "apps" / "cli" / "workflow" / "workflow_stepping.html"
DEFAULT_REPORT_ROOTS = [
    Path("C:/Benutzer_Archive_Start"),
    Path("C:/Benutzer_Synergy_Start"),
    Path("C:/Benutzer_Remedies_Start"),
    Path("C:/Benutzer_Trends_Start"),
    Path("C:/Benutzer_Deutung_Start"),
]
ALLOWED_IMAGE_UPLOAD_SUFFIXES = {".png", ".jpg", ".jpeg"}
ALLOWED_IMAGE_UPLOAD_TYPES = {"image/png", "image/jpeg"}
MAX_IMAGE_UPLOAD_BYTES = 10 * 1024 * 1024
IMAGE_UPLOAD_MULTIPART_OVERHEAD_BYTES = 16 * 1024
MULTIPART_FILENAME_RE = re.compile(r'filename="([^"]*)"')
MULTIPART_CONTENT_TYPE_RE = re.compile(r"content-type:\s*([^\r\n;]+)", re.IGNORECASE)


def _upload_root(runtime_path: Path | None) -> Path:
    if runtime_path is not None:
        return runtime_path / "web_uploads"
    return Path.cwd() / "codex_tmp" / "web-uploads"


def _safe_upload_name(file_name: str) -> str:
    raw_name = Path(file_name or "image-reference").name
    cleaned = "".join(
        char if char.isalnum() or char in {".", "-", "_"} else "_"
        for char in raw_name
    ).strip("._")
    return cleaned or "image-reference"


def _multipart_boundary(content_type: str) -> bytes:
    marker = "boundary="
    if marker not in content_type:
        raise HTTPException(status_code=400, detail="multipart boundary missing")
    boundary = content_type.split(marker, 1)[1].strip().strip('"')
    if not boundary:
        raise HTTPException(status_code=400, detail="multipart boundary missing")
    return boundary.encode("utf-8")


def _parse_single_file_upload(body: bytes, content_type: str) -> tuple[str, str, bytes]:
    boundary = _multipart_boundary(content_type)
    delimiter = b"--" + boundary
    for raw_part in body.split(delimiter):
        if b"Content-Disposition" not in raw_part:
            continue
        headers, separator, data = raw_part.partition(b"\r\n\r\n")
        if not separator:
            continue
        header_text = headers.decode("utf-8", errors="replace")
        if 'name="file"' not in header_text:
            continue
        filename_match = MULTIPART_FILENAME_RE.search(header_text)
        content_type_match = MULTIPART_CONTENT_TYPE_RE.search(header_text)
        filename = filename_match.group(1) if filename_match else "image-reference"
        upload_type = (
            content_type_match.group(1).strip().lower()
            if content_type_match
            else "application/octet-stream"
        )
        if data.endswith(b"\r\n"):
            data = data[:-2]
        return filename, upload_type, data
    raise HTTPException(status_code=400, detail="image reference file missing")


def _content_length_too_large(content_length: str | None) -> bool:
    if content_length is None:
        return False
    try:
        declared_size = int(content_length)
    except ValueError:
        return False
    return declared_size > (
        MAX_IMAGE_UPLOAD_BYTES + IMAGE_UPLOAD_MULTIPART_OVERHEAD_BYTES
    )


def _write_unique_upload(target_root: Path, safe_name: str, data: bytes) -> Path:
    safe_path = Path(safe_name)
    target_stem = safe_path.stem
    target_suffix = safe_path.suffix
    counter = 0
    while True:
        target_name = (
            safe_name
            if counter == 0
            else f"{target_stem}-{counter}{target_suffix}"
        )
        target = target_root / target_name
        try:
            with target.open("xb") as handle:
                handle.write(data)
            return target
        except FileExistsError:
            counter += 1


@lru_cache(maxsize=1)
def driver_layer_status() -> dict[str, Any]:
    try:
        driver_registry = HardwareDriverRegistry.default()
        return {
            "providers": [
                status.to_dict() for status in driver_registry.list_statuses()
            ],
            "note": (
                "Driver layer is available; status does not open devices. "
                "Real HID/serial reads are opt-in and use short read windows, "
                "but native open behavior depends on the Windows driver."
            ),
        }
    except Exception as exc:
        return {
            "providers": [],
            "note": "Driver layer status unavailable.",
            "error": str(exc),
        }


def _scan_notes(request: Phase1ScanRequest, effective_result_limit: int) -> list[str]:
    image_status = request.image_path or "kein Referenzbild"
    adaptive_status = "aktiv" if request.adaptive_limits else "aus"
    return [
        (
            "Web-Profil: "
            f"Template `{request.profile_template}`, Entropie `{request.entropy_mode}`, "
            f"Bild `{image_status}`."
        ),
        (
            "Adaptive Limits: "
            f"{adaptive_status}; Vorschau-/Report-Cap {effective_result_limit} bei Top-{request.top_n}."
        ),
        (
            "Template, Entropie-Modus und Bildoption werden im Preview transparent gezeigt, "
            "und an den produktiven CLI-Pfad uebergeben."
        ),
    ]


def _phase1_scan_payload(
    request: Phase1ScanRequest, *, executes: bool
) -> dict[str, Any]:
    payload = build_phase1_scan_launcher(request, executes=executes)
    effective_result_limit = adaptive_result_limit(
        request.top_n, request.adaptive_limits
    )
    payload.update(
        {
            "profile_template": request.profile_template,
            "entropy_mode": request.entropy_mode,
            "image_path": request.image_path,
            "image_enabled": bool(request.image_path),
            "adaptive_limits_requested": request.adaptive_limits,
            "effective_result_limit": effective_result_limit,
            "notes": [
                *payload.get("notes", []),
                *_scan_notes(request, effective_result_limit),
            ],
        }
    )
    return payload


class HarmonizationRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    intention: str = Field(
        default="harmonization",
        min_length=1,
        alias="harmonization_mode",
        serialization_alias="intention",
    )
    target_frequency: float = Field(default=432.0, gt=0)
    duration_minutes: int = Field(default=5, ge=1)
    use_cpu: bool = True
    use_gpu: bool = False
    use_ram: bool = False
    use_websocket: bool = False
    use_driver_layer: bool = False


def _status_counts(sources: list[Any]) -> dict[str, int]:
    counts = {"active": 0, "disabled": 0, "quarantined": 0, "deprecated": 0}
    for source in sources:
        counts[source.status] = counts.get(source.status, 0) + 1
    return counts


def create_app(
    runtime_dir: str | Path | None = None,
    scan_jobs: ScanJobStore | None = None,
    harmonization_jobs: HarmonizationJobStore | None = None,
    report_roots: Sequence[str | Path] | None = None,
) -> FastAPI:
    app = FastAPI(title="Morphic Engine V1 Web Shell")
    runtime_path = Path(runtime_dir) if runtime_dir is not None else None
    app.state.runtime_dir = runtime_path
    job_root = (
        runtime_path / "web_jobs"
        if runtime_path is not None
        else Path.cwd() / "codex_tmp" / "web-jobs"
    )
    app.state.scan_jobs = scan_jobs or LocalScanJobService(job_root)
    app.state.harmonization_jobs = harmonization_jobs or WorkerHarmonizationService()
    default_report_roots: list[str | Path] = list(report_roots or DEFAULT_REPORT_ROOTS)
    app.state.report_roots = [Path(root) for root in default_report_roots]
    app.state.report_catalog = ReportCatalog(default_report_roots)

    # Rate-Limit Middleware (pro IP, 60 req/min) - ueberspringt WebSocket-Upgrades
    @app.middleware("http")
    async def _rate_limit(request: Request, call_next):
        if request.headers.get("upgrade", "").lower() == "websocket":
            return await call_next(request)
        return await rate_limit_middleware(request, call_next)

    # CORS (loopback-safe) - websocket origins werden separat gehandhabt
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # No-Cache fuer UI-Routen - ueberspringt WebSocket-Upgrades
    @app.middleware("http")
    async def add_no_cache_headers(request, call_next):
        if request.headers.get("upgrade", "").lower() == "websocket":
            return await call_next(request)
        response = await call_next(request)
        path = request.url.path
        if path.startswith("/ui") or path.startswith("/workflow-stepping"):
            response.headers["Cache-Control"] = (
                "no-store, no-cache, must-revalidate, max-age=0"
            )
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
        return response

    # Statische Frontend-Dateien
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
    if WEB_UI_DIR.exists():
        app.mount(
            "/ui", StaticFiles(directory=str(WEB_UI_DIR), html=True), name="ui"
        )

    # Migrierte Router aus web_app.py
    app.include_router(emf_router)
    app.include_router(amplifier_router)
    app.include_router(profiles_router)
    app.include_router(analyze_router)
    app.include_router(synergy_router)
    app.include_router(scan_live_router)

    @app.get("/")
    def index() -> FileResponse:
        return FileResponse(STATIC_DIR / "index.html")

    @app.get("/workflow-stepping")
    def workflow_stepping() -> HTMLResponse:
        """Serviert die 12-Step Dokumentationsseite."""
        if WORKFLOW_STEPPING_HTML.exists():
            return HTMLResponse(
                WORKFLOW_STEPPING_HTML.read_text(encoding="utf-8"), status_code=200
            )
        return HTMLResponse(
            "<h1>workflow_stepping.html nicht gefunden</h1>", status_code=404
        )

    @app.get("/api/status")
    def api_status() -> dict[str, Any]:
        return {"status": "ok", "version": "1.0.0", "server": "Morphic Engine V1"}

    @app.get("/api/health")
    def health() -> dict[str, Any]:
        return collect_runtime_health()

    @app.get("/api/hardware/status")
    def hardware_status() -> dict[str, Any]:
        """Transparente Uebersicht, welche Hardware-/Echtzeitkomponenten
        aktuell tatsaechlich aktiv genutzt werden (vs. Software-Fallback)."""
        from core.hardware.system_info import get_full_system_report

        try:
            report = get_full_system_report()
        except Exception as exc:  # pragma: no cover - defensive
            return {"error": str(exc)}

        sensors = report.get("sensors", {}) or {}
        gpu = report.get("gpu", {}) or {}
        devices = sensors.get("devices", []) or []
        # "system_truerng" ist keine externe Hardware, sondern CPU-Jitter-basiert
        # (siehe core/hardware/sensors.py TrueRandomSensor) - nicht als externe
        # Sensor-Hardware ausweisen, um die UI-Kommunikation nicht zu verfaelschen.
        external_devices = [d for d in devices if d.get("type") != "system_truerng"]
        has_external_sensors = len(external_devices) > 0
        driver_layer = driver_layer_status()

        return {
            "profile": report.get("profile"),
            "os": report.get("os"),
            "cpu": report.get("cpu"),
            "gpu": {
                **gpu,
                "note": (
                    "Echte GPU-Beschleunigung aktiv (CuPy)"
                    if gpu.get("has_gpu")
                    else "Software-Fallback (NumPy/CPU) - keine GPU erkannt"
                ),
            },
            "sensors": {
                "count": len(external_devices),
                "devices": external_devices,
                "note": (
                    f"{len(external_devices)} externe Sensor-Hardware erkannt"
                    if has_external_sensors
                    else "Keine externe Sensor-Hardware (USB/HID) erkannt - "
                    "EMF-/Entropie-Werte basieren auf CPU-Timing-Jitter, "
                    "OS-Zufallszahlen (os.urandom) und Systemlast (Software-Schaetzwert)"
                ),
            },
            "emf_measurement_source": (
                "hybrid (externer Sensor + CPU/OS-Entropie)"
                if has_external_sensors
                else "software (CPU-Jitter, os.urandom, psutil) - keine externe Sensorik"
            ),
            "driver_layer": driver_layer,
        }

    @app.get("/api/sources")
    def sources() -> dict[str, Any]:
        registry = SourceRegistry.load_default()
        source_list = registry.list_sources()
        return {
            "count": len(source_list),
            "status_counts": _status_counts(source_list),
            "sources": [source.to_mapping() for source in source_list],
        }

    @app.get("/api/privacy/clients")
    def privacy_clients() -> dict[str, Any]:
        service = RuntimeManifestService(app.state.runtime_dir)
        clients = service.list_clients_safe()
        return {"count": len(clients), "clients": clients}

    @app.get("/api/reports")
    def reports() -> dict[str, Any]:
        return app.state.report_catalog.list(client_view=True)

    @app.get("/api/reports/{report_id}/preview")
    def report_preview(report_id: str) -> dict[str, Any]:
        try:
            return app.state.report_catalog.preview(report_id)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="report not found") from exc

    @app.get("/api/reports/{report_id}/file")
    def report_file(report_id: str) -> FileResponse:
        try:
            path, entry = app.state.report_catalog.file_path(report_id)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="report not found") from exc
        response = FileResponse(
            path, media_type=str(entry["media_type"]), filename=path.name
        )
        if str(path.suffix).lower() in {".html", ".htm", ".json", ".txt"}:
            response.headers["Content-Disposition"] = (
                f'attachment; filename="{path.name}"'
            )
        return response

    @app.post("/api/uploads/image-reference")
    async def upload_image_reference(
        request: Request,
        _api_key: str | None = Depends(verify_api_key),
    ) -> dict[str, Any]:
        if _content_length_too_large(request.headers.get("content-length")):
            raise HTTPException(status_code=413, detail="image reference too large")

        body = await request.body()
        original_name, content_type, data = _parse_single_file_upload(
            body,
            request.headers.get("content-type", ""),
        )
        suffix = Path(original_name).suffix.lower()
        if suffix not in ALLOWED_IMAGE_UPLOAD_SUFFIXES:
            raise HTTPException(
                status_code=400,
                detail="unsupported image reference suffix",
            )
        if content_type not in ALLOWED_IMAGE_UPLOAD_TYPES:
            raise HTTPException(
                status_code=400,
                detail="unsupported image reference content type",
            )
        if not data:
            raise HTTPException(status_code=400, detail="empty image reference")
        if len(data) > MAX_IMAGE_UPLOAD_BYTES:
            raise HTTPException(status_code=413, detail="image reference too large")

        target_root = _upload_root(app.state.runtime_dir)
        target_root.mkdir(parents=True, exist_ok=True)
        safe_name = _safe_upload_name(original_name)
        target = _write_unique_upload(target_root, safe_name, data)
        return {
            "image_path": str(target),
            "file_name": target.name,
            "size": len(data),
            "content_type": content_type,
        }

    @app.post("/api/harmonization/jobs")
    def harmonization_start(
        request: HarmonizationRequest,
        _api_key: str | None = Depends(verify_api_key),
    ) -> dict[str, Any]:
        intention = normalize_harmonization_mode(request.intention)
        hardware_config = {
            "use_cpu": request.use_cpu,
            "use_gpu": request.use_gpu,
            "use_ram": request.use_ram,
            "use_websocket": request.use_websocket,
            "use_quartz": False,
            "use_driver_layer": request.use_driver_layer,
        }
        return app.state.harmonization_jobs.start(
            mode=intention,
            target_frequency=request.target_frequency,
            duration_minutes=request.duration_minutes,
            intention=intention,
            hardware_config=hardware_config,
        )

    @app.get("/api/harmonization/jobs/{job_id}")
    def harmonization_status(job_id: str) -> dict[str, Any]:
        try:
            return app.state.harmonization_jobs.get(job_id)
        except KeyError as exc:
            raise HTTPException(
                status_code=404, detail="harmonization job not found"
            ) from exc

    @app.post("/api/harmonization/jobs/{job_id}/stop")
    def harmonization_stop(
        job_id: str,
        _api_key: str | None = Depends(verify_api_key),
    ) -> dict[str, Any]:
        try:
            return app.state.harmonization_jobs.stop(job_id)
        except KeyError as exc:
            raise HTTPException(
                status_code=404, detail="harmonization job not found"
            ) from exc

    @app.post("/api/scan/preview", response_model=Phase1ScanPreviewResponse)
    def scan_preview(
        request: Phase1ScanRequest,
        _api_key: str | None = Depends(verify_api_key),
    ) -> Phase1ScanPreviewResponse:
        return Phase1ScanPreviewResponse.model_validate(
            _phase1_scan_payload(request, executes=False)
        )

    @app.post("/api/scan/jobs", response_model=Phase1ScanJobResponse)
    def scan_job_start(
        request: Phase1ScanRequest,
        _api_key: str | None = Depends(verify_api_key),
    ) -> Phase1ScanJobResponse:
        launch = _phase1_scan_payload(request, executes=True)
        command = launch["command"]
        payload = app.state.scan_jobs.start(command)
        launch["executes"] = bool(payload.get("executes", True))
        launch["job_id"] = str(payload["job_id"])
        launch["status"] = str(payload["status"])
        launch["progress_percent"] = payload.get("progress_percent")
        launch["current_phase"] = payload.get("current_phase")
        launch["current_substep"] = payload.get("current_substep")
        launch["completed_substeps"] = list(payload.get("completed_substeps", []))
        return Phase1ScanJobResponse.model_validate(launch)

    @app.get("/api/scan/jobs/{job_id}")
    def scan_job_status(job_id: str) -> dict[str, Any]:
        try:
            return app.state.scan_jobs.get(job_id)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="scan job not found") from exc

    @app.get("/api/scan/jobs/{job_id}/results")
    def scan_job_results(job_id: str) -> dict[str, Any]:
        """Top-Profile und Resonanzen aus den Scan-JSON-Dateien extrahieren."""
        import json
        from datetime import datetime

        from tools.reporting_common import client_slug

        try:
            job = app.state.scan_jobs.get(job_id)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="scan job not found") from exc

        command = job.get("command", [])

        def _arg_after(flag: str) -> str:
            try:
                idx = command.index(flag)
            except ValueError:
                return ""
            return command[idx + 1] if idx + 1 < len(command) else ""

        export_path = _arg_after("--export")

        # Klientenname steht als erste zwei Positionsargumente nach dem CLI-Entrypoint
        # (... "scan", "top3-scan", last_name, first_name, ...)
        last_name = first_name = ""
        try:
            entry_idx = command.index("top3-scan")
            last_name = command[entry_idx + 1]
            first_name = command[entry_idx + 2]
        except (ValueError, IndexError):
            pass
        birth_date = _arg_after("--birth-date")
        birth_place = _arg_after("--birth-place")

        top_profiles: list[dict[str, Any]] = []
        all_resonances: list[dict[str, Any]] = []

        if export_path and last_name:
            slug = client_slug(last_name, first_name, birth_date, birth_place)
            # Neue Hierarchie: export_root / Resonanz / client_slug / session
            client_dir = Path(export_path) / "Resonanz" / slug
            if client_dir.is_dir():
                session_dirs = [
                    d for d in client_dir.iterdir() if d.is_dir() and "SESSION" in d.name
                ]

                created_at = job.get("created_at")
                created_dt = None
                if isinstance(created_at, str):
                    try:
                        created_dt = datetime.fromisoformat(created_at)
                    except ValueError:
                        created_dt = None

                def _session_ts(d: Path) -> str:
                    return d.name.split("_TOP")[0]

                if created_dt is not None:
                    matching = [
                        d for d in session_dirs
                        if _parse_session_ts(_session_ts(d)) is not None
                        and _parse_session_ts(_session_ts(d)) >= created_dt.replace(tzinfo=None)
                    ]
                    session_dirs = matching or session_dirs

                # Neueste Session zuerst (Ordnername beginnt mit Zeitstempel)
                session_dirs.sort(key=lambda d: d.name, reverse=True)
                chosen = session_dirs[0] if session_dirs else None

                if chosen is not None:
                    for profile_dir in chosen.iterdir():
                        if not profile_dir.is_dir():
                            continue
                        for json_file in profile_dir.glob("*_multiplex_scan.json"):
                            try:
                                data = json.loads(
                                    json_file.read_text(encoding="utf-8", errors="replace")
                                )
                                profile_name = data.get("profile", profile_dir.name)
                                top_items = (data.get("sub_results") or {}).get("top", [])
                                top_score = max(
                                    (float(item.get("score", 0)) for item in top_items),
                                    default=0.0,
                                )
                                top_labels = [
                                    {
                                        "label": item.get("label", ""),
                                        "score": float(item.get("score", 0)),
                                        "group": item.get("group", ""),
                                    }
                                    for item in top_items[:5]
                                ]
                                top_profiles.append({
                                    "profile": profile_name,
                                    "score": top_score,
                                    "top_resonances": top_labels,
                                })
                                all_resonances.extend(top_labels)
                            except (json.JSONDecodeError, OSError):
                                continue

        # Sortiere nach Score
        top_profiles.sort(key=lambda p: p["score"], reverse=True)
        all_resonances.sort(key=lambda r: r["score"], reverse=True)

        # Export-Pfade fuer Step 10 ableiten
        export_paths: dict[str, str] = {}
        if export_path and last_name:
            slug = client_slug(last_name, first_name, birth_date, birth_place)
            export_root = Path(export_path)
            # Session-Verzeichnis ermitteln (neueste Session fuer diesen Klienten)
            session_name = ""
            resonanz_dir = export_root / "Resonanz" / slug
            if resonanz_dir.is_dir():
                sessions = sorted(
                    [d.name for d in resonanz_dir.iterdir()
                     if d.is_dir() and "SESSION" in d.name],
                    reverse=True,
                )
                if sessions:
                    session_name = sessions[0]
            for report_type, folder in (
                ("archive", "Resonanz"),
                ("synergy", "Synergy"),
                ("remedies", "Remedies"),
                ("trends", "Trends"),
            ):
                type_dir = export_root / folder / slug
                if session_name:
                    type_dir = type_dir / session_name
                export_paths[report_type] = str(type_dir)

        return {
            "job_id": job_id,
            "status": job.get("status"),
            "top_profiles": top_profiles[:10],
            "top_resonances": all_resonances[:20],
            "export_paths": export_paths,
        }

    return app


app = create_app()
