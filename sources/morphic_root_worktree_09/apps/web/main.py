from __future__ import annotations

from contextlib import asynccontextmanager, contextmanager
from functools import lru_cache
import hashlib
import hmac
import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable, Sequence
from urllib.parse import quote

from fastapi import Depends, FastAPI, Header, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import (
    FileResponse,
    HTMLResponse,
    JSONResponse,
    RedirectResponse,
    StreamingResponse,
)
from fastapi.staticfiles import StaticFiles

from apps.web.admin_security import (
    create_admin_security_from_env,
    router as admin_security_router,
)
from apps.web.admin_catalog import (
    admin_catalog_context_from_operator,
    default_admin_catalog_service_factory,
    router as admin_catalog_router,
)
from apps.web.amplifiers import router as amplifier_router
from apps.web.analyze import router as analyze_router
from apps.web.authority_ids import AuthorityIdError, validate_authority_id
from apps.web.contracts import (
    HarmonizationRequest,
    Phase1ScanJobResponse,
    Phase1ScanStartResponse,
    Phase1ScanPreviewResponse,
    Phase1ScanRequest,
    ScanStartOperationReconcileResponse,
)
from apps.web.display_scores import adaptive_result_limit
from apps.web.emf import legacy_router as legacy_emf_router, router as emf_router
from apps.web.emf_authority import build_emf_telemetry_authority
from apps.web.hardware_truth import (
    build_hardware_truth_snapshot,
    measure_realtime_calibration,
)
from apps.web.group_drafts import build_group_draft_store, router as group_drafts_router
from apps.web.group_consents import (
    build_client_identity_store,
    router as group_consents_router,
)
from apps.web.group_analysis_policy import (
    GroupAnalysisPolicyService,
    router as group_analysis_policy_router,
)
from apps.web.group_analysis_runtime import prepare_group_scan_activation
from apps.web.harmonization import (
    HarmonizationOwnershipError,
    HarmonizationReplayAuthorityError,
    HarmonizationReplayIdentityError,
    HarmonizationReplayOwnershipError,
    HarmonizationJobStore,
    WorkerHarmonizationService,
    normalize_harmonization_mode,
    resolve_harmonization_intention,
)
from apps.web.launcher import build_phase1_scan_launcher
from apps.web.profiles import router as profiles_router
from apps.web.reports import ReportCatalog
from apps.web.scan_diagnostics import safe_scan_diagnostics
from core.compliance.artifact_repository import parallel_export_plan_from_environment
from core.compliance.group_activation_handle_store import GroupActivationHandleStore
from core.compliance.operator_context import (
    OwnershipError,
    assert_owner,
    operator_owner_scope,
    resolve_operator_context,
)
from apps.web.scan_jobs import (
    LocalScanJobService,
    ProcessAuthorityAmbiguousError,
    ScanJobOwnershipError,
    ScanJobReplayAuthorityError,
    ScanJobReplayIdentityError,
    ScanJobReplayOwnershipError,
    ScanJobStore,
)
from apps.web.scan_live import router as scan_live_router
from apps.web.start_operations import (
    StartOperationConflictError,
    StartOperationError,
    StartOperationOwnershipError,
    StartOperationStore,
)
from apps.web.security import (
    POLL_RATE_LIMIT_MAX_REQUESTS,
    READ_RATE_LIMIT_MAX_REQUESTS,
    REPORT_RATE_LIMIT_MAX_REQUESTS,
    MeasurementPublishPermitMiddleware,
    SESSION_COOKIE_NAME,
    SessionAuthority,
    get_api_key,
    rate_limit_middleware,
    revalidate_protected_response,
    verify_api_key,
)
from apps.web.synergy import router as synergy_router
from apps.web.workbench import (
    ScanProfilePoolAuthority,
    current_scan_profile_pool_authority,
    router as workbench_router,
)
from apps.web.workbench_runtime import WorkbenchRuntimeStore
from core.compliance.runtime_manifest import RuntimeManifestService, runtime_root, stable_client_id
from core.db.health import collect_runtime_health
from core.hardware.drivers import HardwareDriverRegistry
from core.profile_sync import SCAN_PROFILE_POOL_FINGERPRINT_ENV
from core.source_registry import SourceRegistry, SourceRegistryError

STATIC_DIR = Path(__file__).with_name("static")
ROOT_DIR = Path(__file__).resolve().parents[2]
LOGGER = logging.getLogger(__name__)


def _attachment_content_disposition(file_name: str) -> str:
    fallback = "".join(
        character
        if character.isascii() and (character.isalnum() or character in " ._-")
        else "_"
        for character in file_name
    ).strip(" .")
    fallback = fallback or "report"
    encoded = quote(file_name, safe="")
    return (
        f'attachment; filename="{fallback}"; '
        f"filename*=UTF-8''{encoded}"
    )


class _ReportStreamingResponse(StreamingResponse):
    def __init__(self, content: Any, *, report_handle: Any, **kwargs: Any) -> None:
        self._report_handle = report_handle
        super().__init__(content, **kwargs)

    async def __call__(self, scope: Any, receive: Any, send: Any) -> None:
        try:
            await super().__call__(scope, receive, send)
        finally:
            self._report_handle.close()

WORKFLOW_STEPPING_HTML = STATIC_DIR / "workflow-stepping.html"
_DEFAULT_REPORT_ROOT_NAMES = [
    "Benutzer_Archive_Start",
    "Benutzer_Synergy_Start",
    "Benutzer_Remedies_Start",
    "Benutzer_Trends_Start",
    "Benutzer_Deutung_Start",
]


def _route_authority_id(value: str) -> str:
    try:
        return validate_authority_id(value)
    except AuthorityIdError as exc:
        raise HTTPException(status_code=422, detail="invalid authority id") from exc


def default_report_roots(tenant_id: str = "") -> list[Path]:
    """Leseseitige Tenant-Isolation (Punkt d, Variante 1: nur aktueller Tenant).

    Ohne `tenant_id` identisch zum bisherigen Verhalten (kein Suffix).
    """

    suffix = f"__{tenant_id}" if tenant_id else ""
    return [Path(f"C:/{name}{suffix}") for name in _DEFAULT_REPORT_ROOT_NAMES]


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
    except Exception:
        return {
            "providers": [],
            "note": "Driver layer status unavailable.",
            "error": "driver layer status unavailable",
        }


def _scan_notes(request: Phase1ScanRequest, effective_result_limit: int) -> list[str]:
    image_status = request.image_path or "kein Referenzbild"
    adaptive_status = "aktiv" if request.adaptive_limits else "aus"
    if request.adaptive_limits:
        adaptive_effect = (
            "Phase-2-Detail-Cap aktiv; ownergebundene Top-Profilliste "
            f"höchstens {effective_result_limit} bei Top-{request.top_n}"
        )
    else:
        adaptive_effect = (
            "voller angeforderter Detailumfang; ownergebundene Top-Profilliste "
            f"bis Top-{request.top_n}"
        )
    return [
        (
            "Web-Profil: "
            f"Template `{request.profile_template}`, Entropie `{request.entropy_mode}`, "
            f"Bild `{image_status}`."
        ),
        (
            f"Adaptive Limits: {adaptive_status}; {adaptive_effect}."
        ),
        (
            "Template, Entropie-Modus und Bildoption werden im Preview transparent gezeigt, "
            "und an den produktiven CLI-Pfad uebergeben."
        ),
    ]


def _assert_current_scan_profile_pool(
    scan_request: Phase1ScanRequest,
) -> ScanProfilePoolAuthority:
    try:
        current = current_scan_profile_pool_authority(scan_request.profile_level)
    except Exception as exc:
        LOGGER.error(
            "Scan profile pool confirmation failed (%s)",
            type(exc).__name__,
        )
        raise HTTPException(
            status_code=503,
            detail=(
                "Scanprofil-Pool konnte nicht bestätigt werden. "
                "Bitte neu laden und erneut prüfen."
            ),
        ) from exc
    if not hmac.compare_digest(
        scan_request.scan_profile_pool_fingerprint,
        current.fingerprint,
    ):
        raise HTTPException(
            status_code=409,
            detail=(
                "Scanprofil-Pool hat sich geändert. "
                "Bitte neu laden und erneut prüfen."
            ),
            headers={"X-Morphic-Scan-Profile-Pool": "stale"},
        )
    if scan_request.top_n > current.count:
        raise HTTPException(
            status_code=422,
            detail="Top-N überschreitet den bestätigten Scanprofil-Pool.",
        )
    return current


def _phase1_scan_payload(
    request: Phase1ScanRequest, *, executes: bool, export_root: str | Path | None = None
) -> dict[str, Any]:
    launcher_kwargs: dict[str, Any] = {"executes": executes}
    if export_root is not None:
        launcher_kwargs["export_path"] = str(Path(export_root).resolve())
    payload = build_phase1_scan_launcher(request, **launcher_kwargs)
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


def _scan_run_trace_terminal_fields(snapshot: dict[str, Any]) -> dict[str, Any]:
    return {
        key: snapshot.get(key)
        for key in (
            "status",
            "returncode",
            "progress_percent",
            "current_phase",
            "current_substep",
            "current_stage_id",
            "completed_stage_ids",
            "updated_at",
        )
        if key in snapshot
    }


def _workbench_run_trace_seed(
    launch: dict[str, Any], *, workbench_mode: str, request: Phase1ScanRequest | None = None
) -> dict[str, Any]:
    review_block: dict[str, Any] = {}
    if request is not None:
        review_block = {
            "client_id": stable_client_id(
                {
                "last_name": request.last_name,
                "first_name": request.first_name,
                "birth_date": request.birth_date,
                "birth_place": request.birth_place,
                }
            ),
            "profile": {
                "profile_template": request.profile_template,
                "entropy_mode": request.entropy_mode,
                "adaptive_limits": request.adaptive_limits,
            },
        }
    seed = {
        "job_id": launch["job_id"],
        "status": launch["status"],
        "executes": launch["executes"],
        "launcher": dict(launch["launcher"]),
        "profile_level": launch["profile_level"],
        "top_n": launch["top_n"],
        "workbench_mode": workbench_mode,
        "profile_template": launch["profile_template"],
        "entropy_mode": launch["entropy_mode"],
        "image_enabled": launch["image_enabled"],
        "adaptive_limits_requested": launch["adaptive_limits_requested"],
        "effective_result_limit": launch["effective_result_limit"],
        "progress_percent": launch["progress_percent"],
        "current_phase": launch["current_phase"],
        "current_substep": launch["current_substep"],
        "completed_substeps": list(launch["completed_substeps"]),
        "review": review_block,
    }
    if launch["status"] in {"completed", "failed"}:
        seed.update(_scan_run_trace_terminal_fields(launch))
    return seed


def _status_counts(sources: list[Any]) -> dict[str, int]:
    counts = {"active": 0, "disabled": 0, "quarantined": 0, "deprecated": 0}
    for source in sources:
        counts[source.status] = counts.get(source.status, 0) + 1
    return counts


def _source_workbench_safe_view(source: Any) -> dict[str, Any]:
    return {
        "active": bool(source.active),
        "description": str(source.description),
        "enabled": bool(source.enabled),
        "id": str(source.id),
        "label": str(source.label),
        "scopes": list(source.scopes),
        "status": str(source.status),
        "warnings": list(source.warnings),
    }


def _scan_job_safe_view(job: dict[str, Any]) -> dict[str, Any]:
    allowed = {
        "job_id", "status", "returncode", "progress_percent", "current_phase",
        "current_substep", "completed_substeps", "completed_stage_ids",
        "current_stage_id", "updated_at",
    }
    safe = {key: job.get(key) for key in allowed if key in job}
    safe["diagnostics"] = safe_scan_diagnostics(job)
    return safe


def _harmonization_safe_view(result: dict[str, Any]) -> dict[str, Any]:
    hidden = {"tenant_id", "operator_id"}
    safe = {key: value for key, value in result.items() if key not in hidden}
    hardware_config = safe.get("hardware_config")
    if isinstance(hardware_config, dict):
        safe["hardware_config"] = {
            key: value
            for key, value in hardware_config.items()
            if not str(key).startswith("_")
        }
    lease = safe.get("lease")
    if isinstance(lease, dict):
        safe["lease"] = {"heartbeat_at": lease.get("heartbeat_at")}
    if safe.get("error_message"):
        safe["error_message"] = "harmonization worker failed"
    return safe


def build_hardware_status_payload(
    report: dict[str, Any] | None = None,
    *,
    driver_layer: dict[str, Any] | None = None,
) -> dict[str, Any]:
    from core.hardware.system_info import get_full_system_report

    report = report if report is not None else get_full_system_report()
    sensors = report.get("sensors", {}) or {}
    gpu = report.get("gpu", {}) or {}
    devices = sensors.get("devices", []) or []
    # "system_truerng" ist keine externe Hardware, sondern CPU-Jitter-basiert
    # (siehe core/hardware/sensors.py TrueRandomSensor) - nicht als externe
    # Sensor-Hardware ausweisen, um die UI-Kommunikation nicht zu verfaelschen.
    external_devices = [d for d in devices if d.get("type") != "system_truerng"]
    has_external_sensors = len(external_devices) > 0
    driver_layer = driver_layer if driver_layer is not None else driver_layer_status()
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


def create_app(
    runtime_dir: str | Path | None = None,
    scan_jobs: ScanJobStore | None = None,
    harmonization_jobs: HarmonizationJobStore | None = None,
    report_roots: Sequence[str | Path] | None = None,
    admin_catalog_service_factory: Callable[[Any], Any] | None = None,
    admin_catalog_context_factory: Callable[[Any], Any] | None = None,
) -> FastAPI:
    @asynccontextmanager
    async def lifespan(application: FastAPI):
        primary_error: BaseException | None = None
        try:
            if application.state.recover_harmonization_on_startup:
                application.state.harmonization_jobs.recover_interrupted_jobs()
            yield
        except BaseException as exc:
            primary_error = exc
        cleanup_error: BaseException | None = None
        if application.state.close_scan_jobs_on_shutdown:
            try:
                application.state.scan_jobs.close()
            except BaseException as exc:
                cleanup_error = exc
        if primary_error is not None and cleanup_error is not None:
            raise BaseExceptionGroup(
                "application lifespan and scan job cleanup failed",
                [primary_error, cleanup_error],
            ) from None
        if primary_error is not None:
            raise primary_error.with_traceback(primary_error.__traceback__)
        if cleanup_error is not None:
            raise cleanup_error.with_traceback(cleanup_error.__traceback__)

    app = FastAPI(title="Morphic Engine V1 Web Shell", lifespan=lifespan)
    runtime_path = Path(runtime_dir) if runtime_dir is not None else None
    app.state.runtime_dir = runtime_path
    job_root = (
        runtime_path / "web_jobs"
        if runtime_path is not None
        else Path.cwd() / "codex_tmp" / "web-jobs"
    )
    workbench_root = (
        runtime_path / "workbench"
        if runtime_path is not None
        else Path.cwd() / "codex_tmp" / "workbench"
    )
    app.state.scan_jobs = (
        LocalScanJobService(job_root) if scan_jobs is None else scan_jobs
    )
    app.state.close_scan_jobs_on_shutdown = scan_jobs is None
    app.state.harmonization_jobs = harmonization_jobs or WorkerHarmonizationService()
    app.state.recover_harmonization_on_startup = harmonization_jobs is None
    app.state.session_authority = SessionAuthority()
    authority_root = runtime_path if runtime_path is not None else Path.cwd() / "codex_tmp"
    app.state.emf_telemetry_authority = build_emf_telemetry_authority(runtime_path)

    operator_context = resolve_operator_context(runtime_path)
    app.state.operator_context = operator_context
    app.state.workbench_store = WorkbenchRuntimeStore(
        workbench_root,
        tenant_id=operator_context.tenant_id,
    )
    app.state.start_operations = StartOperationStore(
        authority_root / "start-operations"
    )
    app.state.group_draft_store = build_group_draft_store(runtime_path, operator_context)
    app.state.client_identity_store = build_client_identity_store(runtime_path)
    app.state.group_analysis_policy = GroupAnalysisPolicyService()
    activation_runtime_root = runtime_path if runtime_path is not None else runtime_root()
    app.state.group_activation_handles = GroupActivationHandleStore(
        activation_runtime_root / "group-activation-handles"
    )
    app.state.invalidate_group_analysis_context = (
        app.state.group_activation_handles.invalidate_context
    )
    _explicit_report_roots = (
        [Path(root) for root in report_roots] if report_roots is not None else None
    )

    app.state.report_roots = _explicit_report_roots or default_report_roots(
        operator_context.tenant_id
    )
    app.state.report_catalog = ReportCatalog(
        app.state.report_roots,
        cache_ttl_seconds=0.5,
    )

    def _report_catalog_for_current_tenant() -> ReportCatalog:
        """Return the app-scoped catalog bound to this operator tenant."""

        return app.state.report_catalog

    app.state.report_catalog_factory = _report_catalog_for_current_tenant
    app.state.driver_layer_status_builder = driver_layer_status

    def _build_hardware_status_payload(
        report: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return build_hardware_status_payload(
            report,
            driver_layer=app.state.driver_layer_status_builder(),
        )

    app.state.build_hardware_status_payload = _build_hardware_status_payload
    app.state.build_hardware_truth_snapshot = build_hardware_truth_snapshot
    app.state.measure_realtime_calibration = measure_realtime_calibration
    app.state.admin_security = create_admin_security_from_env()
    app.state.admin_catalog_context_factory = (
        admin_catalog_context_factory or admin_catalog_context_from_operator
    )
    app.state.admin_catalog_service_factory = (
        admin_catalog_service_factory or default_admin_catalog_service_factory
    )

    app.middleware("http")(revalidate_protected_response)

    # Separate Budgets verhindern, dass Reads, Polling und Mutationen einander
    # aushungern; Reporttraversals erhalten die engste eigene Grenze.
    @app.middleware("http")
    async def _rate_limit(request: Request, call_next):
        if request.headers.get("upgrade", "").lower() == "websocket":
            return await call_next(request)
        if request.method == "GET":
            path = request.url.path
            if path.startswith("/api/reports"):
                return await rate_limit_middleware(
                    request,
                    call_next,
                    bucket="report-read",
                    max_requests=REPORT_RATE_LIMIT_MAX_REQUESTS,
                )
            if path.startswith(("/api/scan/jobs/", "/api/harmonization/jobs/")):
                return await rate_limit_middleware(
                    request,
                    call_next,
                    bucket="job-poll",
                    max_requests=POLL_RATE_LIMIT_MAX_REQUESTS,
                )
            return await rate_limit_middleware(
                request,
                call_next,
                bucket="read",
                max_requests=READ_RATE_LIMIT_MAX_REQUESTS,
            )
        return await rate_limit_middleware(request, call_next)

    # Lokaler Einoperator: dieselbe Origin wird ohne CORS bedient; externe
    # Browser-Origins erhalten bewusst keinen Freigabeheader.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[],
        allow_credentials=False,
        allow_methods=["GET", "POST", "PUT", "OPTIONS"],
        allow_headers=["Content-Type", "X-API-Key"],
    )

    @app.middleware("http")
    async def add_local_security_headers(request: Request, call_next):
        if request.headers.get("upgrade", "").lower() == "websocket":
            return await call_next(request)
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self'; style-src 'self'; "
            "img-src 'self' data:; frame-src 'self'; object-src 'none'; "
            "base-uri 'self'; frame-ancestors 'self'"
        )
        return response

    # No-Cache fuer UI-Routen - ueberspringt WebSocket-Upgrades
    @app.middleware("http")
    async def add_no_cache_headers(request, call_next):
        if request.headers.get("upgrade", "").lower() == "websocket":
            return await call_next(request)
        response = await call_next(request)
        path = request.url.path
        if (
            path.startswith("/ui")
            or path.startswith("/workflow-stepping")
            or path in {"/static/admin.html", "/static/admin-catalog.js"}
        ):
            response.headers["Cache-Control"] = (
                "no-store, no-cache, must-revalidate, max-age=0"
            )
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
        return response

    app.add_middleware(MeasurementPublishPermitMiddleware)

    # Statische Frontend-Dateien
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    @app.get("/ui", include_in_schema=False)
    @app.get("/ui/{path:path}", include_in_schema=False)
    def redirect_deprecated_ui(path: str = "") -> RedirectResponse:
        del path
        return RedirectResponse(url="/", status_code=307)

    # Migrierte Router aus web_app.py
    app.include_router(emf_router)
    app.include_router(legacy_emf_router)
    app.include_router(amplifier_router)
    app.include_router(profiles_router)
    app.include_router(analyze_router)
    app.include_router(synergy_router)
    app.include_router(scan_live_router)
    app.include_router(workbench_router)
    app.include_router(admin_security_router)
    app.include_router(admin_catalog_router)
    app.include_router(group_drafts_router)
    app.include_router(group_consents_router)
    app.include_router(group_analysis_policy_router)

    @app.get("/")
    def index() -> FileResponse:
        return FileResponse(STATIC_DIR / "index.html")

    @app.get("/workflow-stepping")
    def workflow_stepping() -> HTMLResponse:
        """Serviert die separate Pipeline-/Dokumentationsoberflaeche, nicht den primaeren Operator-Flow."""
        if WORKFLOW_STEPPING_HTML.exists():
            content = WORKFLOW_STEPPING_HTML.read_text(encoding="utf-8")
            return HTMLResponse(content, status_code=200)
        return HTMLResponse(
            "<h1>workflow_stepping.html nicht gefunden</h1>", status_code=404
        )

    @app.get("/api/status")
    def api_status(
        _api_key: str | None = Depends(verify_api_key),
    ) -> dict[str, Any]:
        return {"status": "ok", "version": "1.0.0", "server": "Morphic Engine V1"}

    @app.post("/api/auth/session")
    def create_browser_session(
        credentials: dict[str, str],
        request: Request,
        response: Response,
    ) -> dict[str, str]:
        token = app.state.session_authority.issue_for_api_key(
            credentials.get("api_key")
        )
        if token is None:
            raise HTTPException(status_code=401, detail="Invalid or missing API key")
        response.set_cookie(
            SESSION_COOKIE_NAME,
            token,
            httponly=True,
            samesite="strict",
            secure=request.url.scheme == "https",
            path="/",
        )
        return {"status": "authenticated"}

    @app.get("/api/auth/status")
    def browser_session_status(request: Request) -> dict[str, bool]:
        current_key, _generation = app.state.session_authority.observe_current_generation()
        required = current_key is not None
        token = request.cookies.get(SESSION_COOKIE_NAME)
        return {
            "required": required,
            "authenticated": not required or app.state.session_authority.contains(token),
        }

    @app.delete("/api/auth/session")
    def delete_browser_session(
        request: Request,
        response: Response,
    ) -> dict[str, str]:
        app.state.session_authority.revoke(request.cookies.get(SESSION_COOKIE_NAME))
        response.delete_cookie(
            SESSION_COOKIE_NAME,
            path="/",
            httponly=True,
            samesite="strict",
        )
        return {"status": "logged_out"}

    @app.get("/api/health")
    def health(_api_key: str | None = Depends(verify_api_key)) -> dict[str, Any]:
        return collect_runtime_health()

    @app.get("/api/hardware/status")
    def hardware_status(
        _api_key: str | None = Depends(verify_api_key),
    ) -> dict[str, Any]:
        """Transparente Uebersicht, welche Hardware-/Echtzeitkomponenten
        aktuell tatsaechlich aktiv genutzt werden (vs. Software-Fallback)."""
        try:
            return app.state.build_hardware_status_payload()
        except Exception:  # pragma: no cover - defensive
            return {"error": "hardware status unavailable"}

    @app.get("/api/sources")
    def sources(_api_key: str | None = Depends(verify_api_key)) -> dict[str, Any]:
        try:
            registry = SourceRegistry.load_default()
            source_list = registry.list_sources()
        except (SourceRegistryError, OSError, ValueError) as exc:
            raise HTTPException(
                status_code=503,
                detail="Lokaler Quellenkatalog nicht verfügbar.",
            ) from exc
        return {
            "count": len(source_list),
            "status_counts": _status_counts(source_list),
            "sources": [_source_workbench_safe_view(source) for source in source_list],
        }

    @app.get("/api/privacy/clients")
    def privacy_clients(
        _api_key: str | None = Depends(verify_api_key),
    ) -> dict[str, Any]:
        service = RuntimeManifestService(app.state.runtime_dir)
        clients = service.list_clients_safe()
        return {"count": len(clients), "clients": clients}

    @app.get("/api/reports")
    def reports(
        _api_key: str | None = Depends(verify_api_key),
    ) -> dict[str, Any]:
        return app.state.report_catalog_factory().list(include_all_formats=True)

    @app.get("/api/reports/{report_id}/preview")
    def report_preview(
        report_id: str,
        _api_key: str | None = Depends(verify_api_key),
    ) -> dict[str, Any]:
        try:
            return app.state.report_catalog_factory().preview(report_id)
        except (KeyError, OSError) as exc:
            raise HTTPException(status_code=404, detail="report not found") from exc

    @app.get("/api/reports/{report_id}/file")
    def report_file(
        report_id: str,
        _api_key: str | None = Depends(verify_api_key),
    ) -> StreamingResponse:
        handle = None
        try:
            handle, entry = app.state.report_catalog_factory().open_download(report_id)
        except (KeyError, OSError) as exc:
            raise HTTPException(status_code=404, detail="report not found") from exc
        iterator = handle.iter_chunks()
        try:
            return _ReportStreamingResponse(
                iterator,
                report_handle=handle,
                media_type=str(entry["media_type"]),
                headers={
                    "Content-Length": str(entry["size"]),
                    "Content-Disposition": _attachment_content_disposition(
                        str(entry["file_name"])
                    ),
                },
            )
        except BaseException:
            iterator.close()
            handle.close()
            raise

    def _start_operation_owner(kind: str) -> str:
        context = app.state.operator_context
        return operator_owner_scope(context)

    def _fail_start_before_creation(
        claim: Any,
        status_code: int,
        detail: str,
        cause: BaseException | None = None,
    ) -> None:
        claim.fail_before_creation()
        error = HTTPException(
            status_code=status_code,
            detail=detail,
            headers={"X-Morphic-Start-Operation": "safe-to-replace"},
        )
        if cause is not None:
            raise error from cause
        raise error

    @contextmanager
    def _start_operation(kind: str, idempotency_key: str, request_model: Any):
        request_sha256 = hashlib.sha256(
            request_model.model_dump_json().encode("utf-8")
        ).hexdigest()
        try:
            StartOperationStore.validate_key(idempotency_key)
        except StartOperationError as exc:
            raise HTTPException(
                status_code=422,
                detail=str(exc),
                headers={"X-Morphic-Start-Operation": "safe-to-replace"},
            ) from exc
        try:
            with app.state.start_operations.operation(
                kind=kind,
                key=idempotency_key,
                owner_id=_start_operation_owner(kind),
                request_sha256=request_sha256,
            ) as claim:
                yield claim
        except HTTPException:
            raise
        except StartOperationConflictError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        except StartOperationError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    @app.post("/api/harmonization/jobs")
    def harmonization_start(
        request: HarmonizationRequest,
        idempotency_key: str = Header(alias="Idempotency-Key"),
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
            "_emf_authority_path": str(app.state.emf_telemetry_authority.path),
        }
        duration_minutes = request.duration_factor * 21
        with _start_operation("harmonization", idempotency_key, request) as claim:
            if claim.state == "failed":
                raise HTTPException(
                    status_code=409,
                    detail="harmonization start operation failed before job creation",
                    headers={"X-Morphic-Start-Operation": "safe-to-replace"},
                )
            if not claim.is_new:
                get_for_replay = getattr(
                    app.state.harmonization_jobs,
                    "get_for_replay",
                    None,
                )
                if not callable(get_for_replay):
                    raise HTTPException(
                        status_code=503,
                        detail="atomic harmonization replay authority unavailable",
                    )
                try:
                    existing = get_for_replay(
                        claim.job_id,
                        mode=intention,
                        target_frequency=request.target_frequency,
                        duration_minutes=duration_minutes,
                        intention=intention,
                        hardware_config=hardware_config,
                        pulse_seconds=request.pulse_seconds,
                        pause_seconds=request.pause_seconds,
                        duration_factor=request.duration_factor,
                        solfeggio_base=request.target_frequency,
                        report_id=request.report_id,
                        workbench_mode=request.workbench_mode,
                        tenant_id=app.state.operator_context.tenant_id,
                        operator_id=app.state.operator_context.operator_id,
                    )
                except KeyError:
                    existing = None
                except HarmonizationReplayOwnershipError as exc:
                    raise HTTPException(
                        status_code=403,
                        detail="resource access forbidden",
                    ) from exc
                except (
                    HarmonizationReplayIdentityError,
                    HarmonizationReplayAuthorityError,
                ) as exc:
                    raise HTTPException(
                        status_code=409,
                        detail="harmonization replay authority mismatch",
                    ) from exc
                if existing is not None:
                    _assert_harmonization_owner(existing)
                    if claim.state == "pending":
                        claim.complete(claim.job_id)
                    return _harmonization_safe_view(existing)
                if claim.state == "completed":
                    raise HTTPException(
                        status_code=409,
                        detail="completed harmonization operation lost job authority",
                    )

            try:
                app.state.report_catalog_factory().validate(request.report_id)
            except (KeyError, OSError) as exc:
                _fail_start_before_creation(
                    claim,
                    404,
                    "report not found",
                    exc,
                )
            try:
                result = app.state.harmonization_jobs.start(
                    mode=intention,
                    target_frequency=request.target_frequency,
                    duration_minutes=duration_minutes,
                    intention=intention,
                    hardware_config=hardware_config,
                    pulse_seconds=request.pulse_seconds,
                    pause_seconds=request.pause_seconds,
                    duration_factor=request.duration_factor,
                    solfeggio_base=request.target_frequency,
                    report_id=request.report_id,
                    workbench_mode=request.workbench_mode,
                    tenant_id=app.state.operator_context.tenant_id,
                    operator_id=app.state.operator_context.operator_id,
                    job_id=claim.job_id,
                )
            except RuntimeError as exc:
                if "active harmonization job" not in str(exc):
                    raise
                _fail_start_before_creation(
                    claim,
                    409,
                    "active harmonization job already exists",
                    exc,
                )
            claim.complete(str(result["job_id"]))
            return _harmonization_safe_view(result)

    def _assert_harmonization_owner(result: dict[str, Any]) -> None:
        context = app.state.operator_context
        if (
            result.get("tenant_id") != context.tenant_id
            or result.get("operator_id") != context.operator_id
        ):
            raise HTTPException(status_code=403, detail="resource access forbidden")

    @app.get("/api/harmonization/jobs/{job_id}")
    def harmonization_status(
        job_id: str,
        _api_key: str | None = Depends(verify_api_key),
    ) -> dict[str, Any]:
        job_id = _route_authority_id(job_id)
        try:
            result = app.state.harmonization_jobs.get_owned(
                job_id,
                tenant_id=app.state.operator_context.tenant_id,
                operator_id=app.state.operator_context.operator_id,
            )
        except KeyError as exc:
            raise HTTPException(
                status_code=404, detail="harmonization job not found"
            ) from exc
        except HarmonizationOwnershipError as exc:
            raise HTTPException(
                status_code=403,
                detail="resource access forbidden",
            ) from exc
        return _harmonization_safe_view(result)

    @app.post("/api/harmonization/jobs/{job_id}/stop")
    def harmonization_stop(
        job_id: str,
        _api_key: str | None = Depends(verify_api_key),
    ) -> dict[str, Any]:
        job_id = _route_authority_id(job_id)
        try:
            result = app.state.harmonization_jobs.stop_owned(
                job_id,
                tenant_id=app.state.operator_context.tenant_id,
                operator_id=app.state.operator_context.operator_id,
            )
        except KeyError as exc:
            raise HTTPException(
                status_code=404, detail="harmonization job not found"
            ) from exc
        except HarmonizationOwnershipError as exc:
            raise HTTPException(
                status_code=403,
                detail="resource access forbidden",
            ) from exc
        return _harmonization_safe_view(result)

    @app.post("/api/scan/preview", response_model=Phase1ScanPreviewResponse)
    def scan_preview(
        request: Phase1ScanRequest,
        _api_key: str | None = Depends(verify_api_key),
    ) -> Phase1ScanPreviewResponse:
        _assert_current_scan_profile_pool(request)
        return Phase1ScanPreviewResponse.model_validate(
            _phase1_scan_payload(
                request, executes=False, export_root=app.state.report_roots[0]
            )
        )

    @app.post("/api/scan/jobs", response_model=Phase1ScanStartResponse)
    def scan_job_start(
        request: Phase1ScanRequest,
        idempotency_key: str = Header(alias="Idempotency-Key"),
        _api_key: str | None = Depends(verify_api_key),
    ) -> Phase1ScanStartResponse:
        confirmed_pool = _assert_current_scan_profile_pool(request)
        operator_ctx = app.state.operator_context
        owner_scope = operator_owner_scope(operator_ctx)
        with _start_operation("scan", idempotency_key, request) as claim:
            if claim.state == "failed":
                raise HTTPException(
                    status_code=409,
                    detail="scan start operation failed before job creation",
                    headers={"X-Morphic-Start-Operation": "safe-to-replace"},
                )
            if not claim.is_new:
                replay_launch = _phase1_scan_payload(
                    request,
                    executes=True,
                    export_root=app.state.report_roots[0],
                )
                expected_command = replay_launch["command"]
                get_for_replay = getattr(
                    app.state.scan_jobs,
                    "get_for_replay",
                    None,
                )
                if not callable(get_for_replay):
                    raise HTTPException(
                        status_code=503,
                        detail="atomic scan replay authority unavailable",
                    )
                try:
                    existing = get_for_replay(
                        claim.job_id,
                        expected_command=expected_command,
                        expected_owner_id=owner_scope,
                    )
                except KeyError:
                    existing = None
                except ScanJobReplayOwnershipError as exc:
                    raise HTTPException(
                        status_code=403,
                        detail="resource access forbidden",
                    ) from exc
                except ScanJobReplayIdentityError as exc:
                    raise HTTPException(
                        status_code=409,
                        detail="scan replay identity mismatch",
                    ) from exc
                except ScanJobReplayAuthorityError as exc:
                    raise HTTPException(
                        status_code=409,
                        detail="scan replay authority mismatch",
                    ) from exc
                if existing is not None:
                    if claim.state == "pending":
                        claim.complete(claim.job_id)
                    replay_launch.update(
                        {
                            "executes": bool(existing.get("executes", True)),
                            "job_id": claim.job_id,
                            "completed_substeps": list(
                                existing.get("completed_substeps", [])
                            ),
                        }
                    )
                    replay_launch.update(_scan_run_trace_terminal_fields(existing))
                    replay_launch["status"] = str(existing["status"])
                    try:
                        app.state.workbench_store.ensure_run_trace(
                            claim.job_id,
                            _workbench_run_trace_seed(
                                replay_launch,
                                workbench_mode=request.workbench_mode,
                                request=request,
                            ),
                        )
                    except Exception:
                        LOGGER.warning(
                            "Failed to ensure replayed workbench run trace for %s",
                            claim.job_id,
                            exc_info=True,
                        )
                    return Phase1ScanStartResponse.model_validate(replay_launch)
                if claim.state == "completed":
                    raise HTTPException(
                        status_code=409,
                        detail="completed scan operation lost job authority",
                    )

            try:
                activation_environment = prepare_group_scan_activation(
                    request,
                    policy=app.state.group_analysis_policy,
                    draft_store=app.state.group_draft_store,
                    identity_store=app.state.client_identity_store,
                    handle_store=app.state.group_activation_handles,
                    context=operator_ctx,
                    now=datetime.now(UTC),
                )
            except OwnershipError as exc:
                _fail_start_before_creation(
                    claim,
                    403,
                    "resource access forbidden",
                    exc,
                )
            except FileNotFoundError as exc:
                _fail_start_before_creation(
                    claim,
                    404,
                    "group draft not found",
                    exc,
                )
            except LookupError as exc:
                _fail_start_before_creation(
                    claim,
                    422,
                    "group activation is unavailable",
                    exc,
                )
            except ValueError as exc:
                _fail_start_before_creation(claim, 422, str(exc), exc)
            launch = _phase1_scan_payload(
                request, executes=True, export_root=app.state.report_roots[0]
            )
            command = launch["command"]
            emf_environment = {
                "MORPHIC_EMF_AUTHORITY_PATH": str(app.state.emf_telemetry_authority.path),
            }
            if activation_environment is None:
                activation_environment = {
                    SCAN_PROFILE_POOL_FINGERPRINT_ENV: confirmed_pool.fingerprint,
                    **emf_environment,
                }
            else:
                activation_environment = {
                    **activation_environment,
                    "MORPHIC_RUNTIME_DIR": str(activation_runtime_root),
                    SCAN_PROFILE_POOL_FINGERPRINT_ENV: confirmed_pool.fingerprint,
                    **emf_environment,
                }
            payload = app.state.scan_jobs.start(
                command,
                owner_id=owner_scope,
                env_overrides=activation_environment,
                job_id=claim.job_id,
            )
            claim.complete(str(payload["job_id"]))
            launch["executes"] = bool(payload.get("executes", True))
            launch["job_id"] = str(payload["job_id"])
            launch["status"] = str(payload["status"])
            launch["progress_percent"] = payload.get("progress_percent")
            launch["current_phase"] = payload.get("current_phase")
            launch["current_substep"] = payload.get("current_substep")
            launch["completed_substeps"] = list(payload.get("completed_substeps", []))
            if launch["status"] in {"completed", "failed"}:
                launch.update(_scan_run_trace_terminal_fields(payload))
            client = {
                "last_name": request.last_name,
                "first_name": request.first_name,
                "birth_date": request.birth_date,
                "birth_place": request.birth_place,
            }
            client_id = stable_client_id(client)
            parallel_plan = parallel_export_plan_from_environment(
                tenant_id=operator_ctx.tenant_id,
                client_id=client_id,
                session_id=launch["job_id"],
            )
            if parallel_plan is not None:
                launch["parallel_export_plan"] = str(parallel_plan)
                launch["parallel_export_client_id"] = client_id
                RuntimeManifestService(app.state.runtime_dir).register_artifact(
                    client,
                    artifact_type="parallel_export_plan",
                    path=parallel_plan,
                    session_id=launch["job_id"],
                    config={
                        "mode": "plan_only",
                        "tenant_id": operator_ctx.tenant_id,
                    },
                )
            try:
                app.state.workbench_store.ensure_run_trace(
                    launch["job_id"],
                    _workbench_run_trace_seed(
                        launch,
                        workbench_mode=request.workbench_mode,
                        request=request,
                    ),
                )
            except Exception:
                LOGGER.warning(
                    "Failed to persist initial workbench run trace for %s",
                    launch["job_id"],
                    exc_info=True,
                )
            return Phase1ScanStartResponse.model_validate(launch)

    @app.post(
        "/api/scan/start-operation/reconcile",
        response_model=ScanStartOperationReconcileResponse,
        response_model_exclude_none=True,
        response_model_exclude_defaults=True,
    )
    def reconcile_scan_start_operation(
        response: Response,
        idempotency_key: str = Header(alias="Idempotency-Key"),
        _api_key: str | None = Depends(verify_api_key),
    ) -> dict[str, Any]:
        owner_scope = operator_owner_scope(app.state.operator_context)
        try:
            with app.state.start_operations.inspect(
                kind="scan",
                key=idempotency_key,
                owner_id=owner_scope,
            ) as claim:
                if claim is None:
                    return {"disposition": "retry-same-key"}
                if claim.state == "failed":
                    response.headers["X-Morphic-Start-Operation"] = "safe-to-replace"
                    return {"disposition": "safe-to-replace"}

                observe_owned = getattr(app.state.scan_jobs, "observe_owned", None)
                if not callable(observe_owned):
                    raise HTTPException(
                        status_code=503,
                        detail="scan job authority unavailable",
                    )
                try:
                    job = observe_owned(
                        claim.job_id,
                        expected_owner_id=owner_scope,
                    )
                except KeyError:
                    if claim.state == "completed":
                        raise HTTPException(
                            status_code=409,
                            detail="completed scan operation lost job authority",
                        )
                    claim.fail_before_creation()
                    response.headers["X-Morphic-Start-Operation"] = "safe-to-replace"
                    return {"disposition": "safe-to-replace"}
                except ScanJobOwnershipError as exc:
                    raise HTTPException(
                        status_code=403,
                        detail="resource access forbidden",
                    ) from exc
                except ProcessAuthorityAmbiguousError as exc:
                    raise HTTPException(
                        status_code=503,
                        detail="scan job authority unavailable",
                    ) from exc

                if claim.state == "pending":
                    claim.complete(claim.job_id)
                safe_job = _scan_job_safe_view(job)
                safe_job.pop("updated_at", None)
                return {"disposition": "job", **safe_job}
        except HTTPException:
            raise
        except OSError as exc:
            raise HTTPException(
                status_code=503,
                detail="scan start operation authority unavailable",
            ) from exc
        except StartOperationOwnershipError as exc:
            raise HTTPException(
                status_code=403,
                detail="resource access forbidden",
            ) from exc
        except StartOperationConflictError as exc:
            raise HTTPException(
                status_code=409,
                detail="scan start operation authority mismatch",
            ) from exc
        except StartOperationError as exc:
            raise HTTPException(status_code=422, detail="invalid idempotency key") from exc

    def get_owned_scan_job(job_id: str) -> dict[str, object]:
        return app.state.scan_jobs.get_owned(
            job_id,
            expected_owner_id=operator_owner_scope(app.state.operator_context),
        )

    @app.get("/api/scan/jobs/{job_id}")
    def scan_job_status(
        job_id: str, _api_key: None = Depends(verify_api_key)
    ) -> dict[str, object]:
        job_id = _route_authority_id(job_id)
        try:
            job = get_owned_scan_job(job_id)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="scan job not found") from exc
        except ScanJobOwnershipError as exc:
            raise HTTPException(status_code=403, detail="resource access forbidden") from exc
        return _scan_job_safe_view(job)

    @app.post("/api/scan/jobs/{job_id}/stop")
    def stop_scan_job(
        job_id: str, _api_key: None = Depends(verify_api_key)
    ) -> dict[str, object]:
        job_id = _route_authority_id(job_id)
        try:
            job = app.state.scan_jobs.stop_owned(
                job_id,
                expected_owner_id=operator_owner_scope(app.state.operator_context),
            )
            return _scan_job_safe_view(job)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="scan job not found") from exc
        except ScanJobOwnershipError as exc:
            raise HTTPException(status_code=403, detail="resource access forbidden") from exc

    @app.post("/api/scan/jobs/{job_id}/sync-trace")
    def scan_job_sync_trace(
        job_id: str,
        _api_key: str | None = Depends(verify_api_key),
    ) -> dict[str, Any]:
        job_id = _route_authority_id(job_id)
        try:
            status = get_owned_scan_job(job_id)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="scan job not found") from exc
        except ScanJobOwnershipError as exc:
            raise HTTPException(status_code=403, detail="resource access forbidden") from exc
        if status.get("status") not in {"completed", "failed"}:
            raise HTTPException(status_code=409, detail="scan job is not terminal")
        trace_update = _scan_run_trace_terminal_fields(status)
        try:
            app.state.workbench_store.ensure_run_trace(
                job_id,
                {"job_id": job_id, "status": "running"},
            )
            app.state.workbench_store.finalize_run_trace_once(job_id, trace_update)
        except ValueError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        except Exception as exc:
            LOGGER.warning(
                "Failed to update workbench run trace for %s", job_id, exc_info=True
            )
            raise HTTPException(status_code=500, detail="run trace synchronization failed") from exc
        return trace_update

    @app.get("/api/scan/jobs/{job_id}/results")
    def scan_job_results(
        job_id: str, _api_key: None = Depends(verify_api_key)
    ) -> dict[str, Any]:
        """Top-Profile und Resonanzen aus den Scan-JSON-Dateien extrahieren."""
        import json

        job_id = _route_authority_id(job_id)
        try:
            job = get_owned_scan_job(job_id)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="scan job not found") from exc
        except ScanJobOwnershipError as exc:
            raise HTTPException(status_code=403, detail="resource access forbidden") from exc

        persisted_command = job.get("command")
        command = (
            persisted_command
            if isinstance(persisted_command, list)
            and all(isinstance(token, str) for token in persisted_command)
            else []
        )

        def _arg_after(flag: str) -> str:
            try:
                idx = command.index(flag)
            except ValueError:
                return ""
            return command[idx + 1] if idx + 1 < len(command) else ""

        export_path = _arg_after("--export")
        result_top_n = 10
        result_adaptive_limits = False
        top_n_positions = [
            index for index, token in enumerate(command) if token == "--top-n"
        ]
        adaptive_count = command.count("--adaptive-limits")
        fixed_count = command.count("--fixed-limits")
        has_attached_limit_value = any(
            token.startswith("--adaptive-limits=")
            or token.startswith("--fixed-limits=")
            for token in command
        )
        limit_flag_positions = [
            index
            for index, token in enumerate(command)
            if token in {"--adaptive-limits", "--fixed-limits"}
        ]
        limit_flags_are_standalone = all(
            index + 1 == len(command) or command[index + 1].startswith("--")
            for index in limit_flag_positions
        )
        limits_are_unambiguous = (
            len(top_n_positions) == 1
            and adaptive_count <= 1
            and fixed_count <= 1
            and not (adaptive_count and fixed_count)
            and limit_flags_are_standalone
            and not has_attached_limit_value
        )
        if limits_are_unambiguous:
            top_n_index = top_n_positions[0]
            top_n_value = (
                command[top_n_index + 1] if top_n_index + 1 < len(command) else ""
            )
            if top_n_value in {"3", "5", "7", "9"}:
                result_top_n = int(top_n_value)
                result_adaptive_limits = adaptive_count == 1
        result_limit = adaptive_result_limit(result_top_n, result_adaptive_limits)

        top_profiles: list[dict[str, Any]] = []
        all_resonances: list[dict[str, Any]] = []
        export_paths: dict[str, str] = {}
        export_root = Path(export_path).resolve() if export_path else None
        artifact_paths = [Path(str(value)) for value in job.get("artifact_paths", [])]
        report_folders = {
            "Resonanz": "archive",
            "Synergy": "synergy",
            "Remedies": "remedies",
            "Trends": "trends",
        }
        for artifact in artifact_paths:
            try:
                resolved = artifact.resolve(strict=True)
                if export_root is None or not resolved.is_relative_to(export_root):
                    continue
            except (OSError, RuntimeError):
                continue
            for folder, report_type in report_folders.items():
                if folder in resolved.parts:
                    export_paths[report_type] = str(resolved)
                    break
            if not resolved.name.endswith("_multiplex_scan.json"):
                continue
            try:
                data = json.loads(resolved.read_text(encoding="utf-8", errors="replace"))
                profile_name = data.get("profile", resolved.parent.name)
                top_items = (data.get("sub_results") or {}).get("top", [])
                top_score = max(
                    (float(item.get("score", 0)) for item in top_items), default=0.0
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
            except (json.JSONDecodeError, OSError, TypeError, ValueError):
                continue

        raw_report_session_id = job.get("report_session_id")
        report_session_id = (
            raw_report_session_id
            if type(raw_report_session_id) is str and raw_report_session_id
            else None
        )

        # Sortiere nach Score
        top_profiles.sort(key=lambda p: p["score"], reverse=True)
        all_resonances.sort(key=lambda r: r["score"], reverse=True)


        return {
            "job_id": job_id,
            "status": job.get("status"),
            "top_profiles": top_profiles[:result_limit],
            "top_resonances": all_resonances[:20],
            "export_paths": export_paths,
            "report_session_id": report_session_id,
        }

    @app.api_route(
        "/api/scan/jobs/{unmatched_path:path}",
        methods=["GET", "POST"],
    )
    def reject_unmatched_scan_job_path(
        unmatched_path: str,
        _api_key: None = Depends(verify_api_key),
    ) -> None:
        _route_authority_id(unmatched_path)
        raise HTTPException(status_code=404, detail="scan job route not found")

    @app.api_route(
        "/api/harmonization/jobs/{unmatched_path:path}",
        methods=["GET", "POST"],
    )
    def reject_unmatched_harmonization_job_path(
        unmatched_path: str,
        _api_key: None = Depends(verify_api_key),
    ) -> None:
        _route_authority_id(unmatched_path)
        raise HTTPException(status_code=404, detail="harmonization job route not found")

    @app.get("/api/workbench/run-trace/{unmatched_path:path}")
    def reject_unmatched_run_trace_path(
        unmatched_path: str,
        _api_key: None = Depends(verify_api_key),
    ) -> None:
        _route_authority_id(unmatched_path)
        raise HTTPException(status_code=404, detail="run trace route not found")

    return app


app = create_app()
