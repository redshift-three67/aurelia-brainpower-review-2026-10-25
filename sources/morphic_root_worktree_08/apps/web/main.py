from __future__ import annotations

from pathlib import Path
from typing import Any, Sequence

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, ConfigDict

from apps.web.contracts import (
    Phase1ScanJobResponse,
    Phase1ScanPreviewResponse,
    Phase1ScanRequest,
)
from apps.web.display_scores import adaptive_result_limit
from apps.web.harmonization import (
    HarmonizationJobStore,
    WorkerHarmonizationService,
    normalize_harmonization_mode,
    resolve_harmonization_intention,
)
from apps.web.launcher import build_phase1_scan_launcher
from apps.web.reports import ReportCatalog
from apps.web.scan_jobs import LocalScanJobService, ScanJobStore
from core.compliance.runtime_manifest import RuntimeManifestService
from core.db.health import collect_runtime_health
from core.source_registry import SourceRegistry


STATIC_DIR = Path(__file__).with_name("static")
DEFAULT_REPORT_ROOTS = [
    Path("C:/Benutzer_Archive_Start"),
    Path("C:/Benutzer_Synergy_Start"),
    Path("C:/Benutzer_Remedies_Start"),
    Path("C:/Benutzer_Trends_Start"),
    Path("C:/Benutzer_Deutung_Start"),
]


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
            "aber aktuell nicht als produktive CLI-Flags uebergeben."
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
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    @app.get("/")
    def index() -> FileResponse:
        return FileResponse(STATIC_DIR / "index.html")

    @app.get("/api/health")
    def health() -> dict[str, Any]:
        return collect_runtime_health()

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

    @app.post("/api/harmonization/jobs")
    def harmonization_start(request: HarmonizationRequest) -> dict[str, Any]:
        intention = normalize_harmonization_mode(request.intention)
        hardware_config = {
            "use_cpu": request.use_cpu,
            "use_gpu": request.use_gpu,
            "use_ram": request.use_ram,
            "use_websocket": request.use_websocket,
            "use_quartz": False,
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
    def harmonization_stop(job_id: str) -> dict[str, Any]:
        try:
            return app.state.harmonization_jobs.stop(job_id)
        except KeyError as exc:
            raise HTTPException(
                status_code=404, detail="harmonization job not found"
            ) from exc

    @app.post("/api/scan/preview", response_model=Phase1ScanPreviewResponse)
    def scan_preview(request: Phase1ScanRequest) -> Phase1ScanPreviewResponse:
        return Phase1ScanPreviewResponse.model_validate(
            _phase1_scan_payload(request, executes=False)
        )

    @app.post("/api/scan/jobs", response_model=Phase1ScanJobResponse)
    def scan_job_start(request: Phase1ScanRequest) -> Phase1ScanJobResponse:
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

    return app


app = create_app()
