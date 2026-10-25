"""App-Fabrik des RadiWorks-Kernels.

Verwendung:
    uvicorn "radiworks.main:create_app" --factory --port 8090
oder mit eigenem Heimatverzeichnis:
    uvicorn "radiworks.main:create_app" --factory --port 8090 \\
        --factory-create-kwargs '{"base_dir": "C:/pfad/zum/home"}'
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import threading
import time
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from . import copyguard
from . import manifest as manifest_module
from .api.routes import STATE, AppState, build_router
from .api.comparisons import build_comparison_router
from .core.auto_jobs import AutoJobStore
from .core.personal_controller import PersonalController
from .core.watchlist import WatchlistController
from .api.personal import build_personal_router
from .core.comparison_controller import ComparisonController
from .core.analysis import analyse_rate_list
from .config import SettingsStore
from .core.broadcast import BroadcastManager
from .core.broadcast_target import BroadcastTargetStore
from .core.presentation_profile import PresentationProfileStore
from .core.gv_observations import GvObservationController, journaled_os_draw
from .entropy_journal import EntropyJournalStore
from .core.cases import CaseStore
from .core.draft import DraftStore
from .core.automode import AutoModeController
from .core.materia import MateriaMedica
from .core.rates import RateRepository
from .core.stickpad import StickPad
from .entropy import EntropyProvider, RandomOrgSource, WebcamFeedSource
from .persistence import RecoveryCoordinator
from .runtime_lease import runtime_home_lease
from .scope import ScopeError, ScopeResolver

DEFAULT_ORIGINS = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:8081",
    "http://127.0.0.1",
    "http://127.0.0.1:8080",
    "http://127.0.0.1:8081",
]


def default_runtime_home() -> Path:
    """Laufzeitdaten gehoeren nie in den ausgecheckten Projektbaum."""
    configured = os.environ.get("RADIOWORKS_HOME")
    return Path(configured).expanduser() if configured else Path.home() / ".radiworks"


def default_rate_data_dir(runtime_home: Path) -> Path:
    """Read-only Rate-Katalog; explizit vom schreibbaren Runtime-Home getrennt."""
    configured = os.environ.get("RADIOWORKS_DATA_DIR")
    return Path(configured).expanduser() if configured else runtime_home / "data"


def _error_code(status_code: int) -> str:
    return {
        400: "bad_request",
        404: "not_found",
        405: "method_not_allowed",
        409: "conflict",
        422: "validation_error",
        503: "stochastic_recovery_unavailable",
    }.get(status_code, "http_error" if status_code < 500 else "internal_error")


def _error_response(
    status_code: int,
    message: str,
    *,
    headers: dict[str, str] | None = None,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"error": {
            "code": _error_code(status_code),
            "message": copyguard.public_view(message),
        }},
        headers=headers,
    )


def _http_exception_message(detail: object) -> str:
    return detail if isinstance(detail, str) else "Anfrage konnte nicht verarbeitet werden."


def create_app(
    base_dir: Path | str | None = None,
    *,
    data_dir: Path | str | None = None,
    cases_dir: Path | str | None = None,
    drafts_dir: Path | str | None = None,
    materia_dir: Path | str | None = None,
    webapp_dir: Path | str | None = None,
    cors_origins: list[str] | None = None,
) -> FastAPI:
    base = Path(base_dir).expanduser() if base_dir else default_runtime_home()
    data = Path(data_dir).expanduser() if data_dir else default_rate_data_dir(base)
    cases = Path(cases_dir) if cases_dir else base / "cases"
    drafts = Path(drafts_dir) if drafts_dir else base / "drafts"
    materia = Path(materia_dir) if materia_dir else base / "materiaMedica" / "Clarke"
    webapp = Path(webapp_dir) if webapp_dir else None
    scope_resolver = ScopeResolver.from_environment()
    scope = scope_resolver.resolve({})

    rate_repository = RateRepository(data)
    rate_repository.refresh()
    case_store = CaseStore(cases, scope=scope)
    draft_store = DraftStore(drafts, scope=scope)
    recovery = RecoveryCoordinator(
        base / "recovery",
        stores={"case": cases, "draft": drafts, "stickpad": base / "stickpad", "comparisonSource": base / "comparison_sources"},
    )
    materia_medica = MateriaMedica(materia)
    materia_medica.load()
    settings = SettingsStore(base / "config")

    # Zyklus bewusst in zwei Schritten: der emit-Rueckruf greift erst zur
    # Laufzeit auf state.publish zu; der Manager wird sofort vollstaendig
    # initialisiert (EntropyProvider seeded, Hard Rule 7).
    state = AppState(
        rate_repository=rate_repository,
        case_store=case_store,
        draft_store=draft_store,
        materia_medica=materia_medica,
        broadcast=None,  # type: ignore[arg-type]
        settings_store=settings,
        stick_pad=StickPad(base / "stickpad" / "state.json"),
        entropy_feed=WebcamFeedSource(),
        random_org=RandomOrgSource(),
        journal_dir=base / "entropy_journals",
        recovery=recovery,
        scope=scope,
        scope_resolver=scope_resolver,
        presentation_profiles=PresentationProfileStore(cases, scope),
    )
    state.personal = PersonalController(base / "personal_jobs", scope, deps_dir=os.environ.get("RADIOWORKS_EXP1_CPU_DEPS"))
    state.comparisons = ComparisonController(base / "comparisons", scope, deps_dir=os.environ.get("RADIOWORKS_EXP1_CPU_DEPS"))
    shared_cpu_budget = threading.Lock()
    state.personal._cpu_budget = shared_cpu_budget
    state.comparisons._cpu_budget = shared_cpu_budget
    state.broadcast = BroadcastManager(
        entropy=EntropyProvider(seed=0, mode="seeded"),
        emit=lambda event_type, payload: state.publish(event_type, payload),
        on_accept=lambda entries: state.broadcast_targets.accept(entries),
        on_abort=lambda payload: state.broadcast_targets.terminal(payload),
        entropy_factory=lambda target: state.new_provider(
            0 if target.payload()["entropyMode"] == "seeded" else None,
            target.payload()["entropyMode"],
            journal=state.create_entropy_journal() if target.payload()["entropyMode"] == "stochastic" else None,
        ),
        on_entropy=lambda payload: state.broadcast_targets.record_entropy(payload),
        policy_factory=state.broadcast_policy,
        capacity=state.broadcast_capacity,
        on_adjustment=lambda payload: state.broadcast_targets.record_adjustment(payload),
    )
    observation_journals = base / 'observation_entropy_journals'
    state.observations = GvObservationController(
        base / 'gv_observations', scope, state.broadcast,
        draw=lambda: journaled_os_draw(observation_journals),
        ready=lambda: EntropyJournalStore(observation_journals),
    )
    # Auto-Modus-Regelkreis (Original handleAutoMode): serverseitige Uhr,
    # schaltet bei GV <= 300 selbstständig Harmonisierungs-Broadcasts.
    state.auto = AutoModeController(
        enqueue=lambda signature, seconds, multiplier: state.broadcast.enqueue(
            signature, seconds, multiplier
        ),
        enqueue_target=lambda signature, seconds, multiplier, target: state.broadcast.enqueue(
            signature, seconds, multiplier, target=target
        ),
        emit=lambda event_type, payload: state.publish(event_type, payload),
        find_rates=rate_repository.find_all_by_source_name,
        analyse=analyse_rate_list,
        live_entropy=lambda: state.live(),
        queue_state=state.broadcast.queue_state,
        on_generation_start=lambda *args: state.auto_jobs.accept(*args),
        on_generation_entropy=lambda *args: state.auto_jobs.checkpoint(*args),
        on_generation_end=lambda *args: state.auto_jobs.end(*args),
    )
    state.broadcast._on_tick = state.auto.tick
    state.broadcast._keep_alive = lambda: state.auto.state.enabled

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        with runtime_home_lease(base):
            state.recovery.recover()
            state.watchlist = WatchlistController(base / "watchlists", scope)
            state.broadcast_targets = BroadcastTargetStore(
                base / "broadcast_jobs",
                scope,
                presentation_resolver=state.presentation_profiles.freeze_for_target,
            )
            state.auto_jobs = AutoJobStore(base / "auto_jobs", scope)
            state.stick_pad = StickPad(base / "stickpad" / "state.json")
            state.draft_store.reconcile_promotions()
            STATE.activate(state)
            state.loop = asyncio.get_running_loop()
            state.rate_repository.refresh()
            state.materia_medica.load()
            # Original-Quelle: data/radionics/HOMEOPATHY/clarkeMateriaMedica.json
            merged_index = Path(data) / "radionics" / "HOMEOPATHY" / "clarkeMateriaMedica.json"
            if merged_index.exists():
                loaded = state.materia_medica.load_merged_clinical_index(merged_index)
                if loaded:
                    print(f"RadiWorks Engine — Original-Clinical-Index: {loaded} Symptome")
            state.personal.start()
            state.comparisons.start()
            state.observations.start()
            try:
                yield
            finally:
                cleanup_errors = []

                def cleanup(name, action):
                    try:
                        action()
                    except Exception as exc:
                        cleanup_errors.append((name, exc))
                        logging.getLogger(__name__).error(
                            "Engine shutdown step failed: %s (%s)",
                            name,
                            type(exc).__name__,
                        )

                cleanup("watchlist", state.watchlist.shutdown)
                cleanup("observation-stop", state.observations.request_stop)
                cleanup("personal", state.personal.shutdown)
                cleanup("comparisons", state.comparisons.shutdown)
                if state.auto is not None:
                    cleanup("auto", lambda: state.auto.shutdown(timeout=None))
                cleanup("broadcast", lambda: state.broadcast.shutdown(timeout=None))
                cleanup("observations", lambda: state.observations.shutdown(timeout=None))
                try:
                    await state.shutdown_websockets()
                except Exception as exc:
                    cleanup_errors.append(("websockets", exc))
                    logging.getLogger(__name__).error(
                        "Engine shutdown step failed: %s (%s)",
                        "websockets",
                        type(exc).__name__,
                    )

                state.loop = None
                STATE.deactivate(state)
                if cleanup_errors:
                    names = ", ".join(name for name, _ in cleanup_errors)
                    raise RuntimeError(f"Engine cleanup failed: {names}") from cleanup_errors[0][1]

    app = FastAPI(
        title="RadiWorks Engine",
        version=manifest_module.KERNEL_VERSION,
        description=(
            "AetherOnePi-Kernlogik als Kernel-ABI-v1-konformer Dienst "
            "(Aurelia-Modul 'Werkbank'). Wellbeing-Dokumentation, kein Medizinprodukt."
        ),
        lifespan=lifespan,
    )

    @app.middleware("http")
    async def trace_case_mutations(request: Request, call_next):
        # Diagnose nur für feste Pfade; weder Falldaten noch URL-Parameter protokollieren.
        path = request.url.path
        if request.method != "POST" or path not in {"/cases", "/cases/current/metadata", "/analysis"}:
            return await call_next(request)
        logger = logging.getLogger("uvicorn.error")
        started = time.monotonic()
        logger.info("RadiWorks mutation received: %s", path)
        try:
            response = await call_next(request)
        except Exception:
            logger.exception("RadiWorks mutation failed: %s", path)
            raise
        logger.info("RadiWorks mutation completed: %s status=%s duration_ms=%d",
                    path, response.status_code, int((time.monotonic() - started) * 1000))
        return response

    @app.middleware("http")
    async def enforce_local_scope(request: Request, call_next):
        try:
            scope_resolver.resolve(request.headers)
        except ScopeError as exc:
            return _error_response(400, str(exc))
        return await call_next(request)

    @app.middleware("http")
    async def project_public_json(request: Request, call_next):
        response = await call_next(request)
        if not response.headers.get("content-type", "").startswith("application/json"):
            return response
        chunks = [chunk async for chunk in response.body_iterator]
        body = b"".join(chunks)
        try:
            source = json.loads(body)
        except (ValueError, UnicodeDecodeError):
            return _error_response(500, "Öffentliche Antwort konnte nicht geprüft werden.")
        projected = copyguard.public_view(source)
        outgoing: Response = (
            Response(content=body, status_code=response.status_code, media_type="application/json")
            if projected == source else
            JSONResponse(projected, status_code=response.status_code)
        )
        outgoing.raw_headers = [
            (key, value) for key, value in response.raw_headers
            if key.lower() not in {b"content-type", b"content-length"}
        ] + outgoing.raw_headers
        outgoing.background = response.background
        return outgoing

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        _request: Request,
        exc: StarletteHTTPException,
    ) -> JSONResponse:
        return _error_response(
            exc.status_code,
            _http_exception_message(exc.detail),
            headers=exc.headers,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        _request: Request,
        _exc: RequestValidationError,
    ) -> JSONResponse:
        return _error_response(422, "Anfrage ist ungültig.")

    @app.exception_handler(Exception)
    async def unexpected_exception_handler(
        _request: Request,
        _exc: Exception,
    ) -> JSONResponse:
        return _error_response(500, "Interner Serverfehler.")

    app.include_router(build_router(state))
    app.include_router(build_personal_router(state))
    app.include_router(build_comparison_router(state))

    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins if cors_origins is not None else DEFAULT_ORIGINS,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-RadiWorks-Case-Ref"],
    )

    if webapp and Path(webapp).exists():
        # No-Cache für die Webapp: veraltete JS-Bundles im Browser waren schon
        # Ursache von „Funktion kommt nicht an“-Meldungen. Für den Prototyp
        # gilt: immer frisch liefern (Aurelia setzt später Immutable-Caching
        # für gehashte Artefakte, docs/15-live.md).
        class NoCacheStaticFiles(StaticFiles):
            def file_response(self, *args, **kwargs):  # type: ignore[override]
                response = super().file_response(*args, **kwargs)
                response.headers["Cache-Control"] = "no-cache, max-age=0"
                return response

        app.mount("/", NoCacheStaticFiles(directory=str(webapp), html=True), name="webapp")

    app.state.radiworks_state = state
    app.state.settings_store = settings
    return app


# Dev-Standard: `uvicorn radiworks.main:app --port 8090`
app = create_app()

