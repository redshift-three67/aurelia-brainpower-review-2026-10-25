"""App-Fabrik des RadiWorks-Kernels.

Verwendung:
    uvicorn "radiworks.main:create_app" --factory --port 8090
oder mit eigenem Heimatverzeichnis:
    uvicorn "radiworks.main:create_app" --factory --port 8090 \\
        --factory-create-kwargs '{"base_dir": "C:/pfad/zum/home"}'
"""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from . import manifest as manifest_module
from .api.routes import STATE, AppState, build_router
from .core.analysis import analyse_rate_list
from .config import SettingsStore
from .core.broadcast import BroadcastManager
from .core.cases import CaseStore
from .core.draft import DraftStore
from .core.automode import AutoModeController
from .core.materia import MateriaMedica
from .core.rates import RateRepository
from .core.stickpad import StickPad
from .entropy import EntropyProvider, WebcamFeedSource

DEFAULT_ORIGINS = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:8081",
    "http://127.0.0.1",
    "http://127.0.0.1:8080",
    "http://127.0.0.1:8081",
]


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
    base = Path(base_dir) if base_dir else Path("./radiworks_home")
    data = Path(data_dir) if data_dir else base / "data"
    cases = Path(cases_dir) if cases_dir else base / "cases"
    drafts = Path(drafts_dir) if drafts_dir else base / "drafts"
    materia = Path(materia_dir) if materia_dir else base / "materiaMedica" / "Clarke"
    webapp = Path(webapp_dir) if webapp_dir else None

    rate_repository = RateRepository(data)
    rate_repository.refresh()
    case_store = CaseStore(cases)
    draft_store = DraftStore(drafts)
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
        stick_pad=StickPad(),
        entropy_feed=WebcamFeedSource(),
    )
    state.broadcast = BroadcastManager(
        entropy=EntropyProvider(seed=0, mode="seeded"),
        emit=lambda event_type, payload: state.publish(event_type, payload),
    )
    # Auto-Modus-Regelkreis (Original handleAutoMode): serverseitige Uhr,
    # schaltet bei GV <= 300 selbstständig Harmonisierungs-Broadcasts.
    state.auto = AutoModeController(
        enqueue=lambda signature, seconds, multiplier: state.broadcast.enqueue(
            signature, seconds, multiplier
        ),
        emit=lambda event_type, payload: state.publish(event_type, payload),
        find_rates=rate_repository.find_all_by_source_name,
        analyse=analyse_rate_list,
        live_entropy=lambda: state.live(),
    )
    state.auto.set_active_count_probe(state.broadcast.active_count)
    state.broadcast._on_tick = state.auto.tick
    state.broadcast._keep_alive = lambda: state.auto.state.enabled
    STATE.state = state

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        state.loop = asyncio.get_running_loop()
        state.rate_repository.refresh()
        state.materia_medica.load()
        # Original-Quelle: data/radionics/HOMEOPATHY/clarkeMateriaMedica.json
        merged_index = Path(data) / "radionics" / "HOMEOPATHY" / "clarkeMateriaMedica.json"
        if merged_index.exists():
            loaded = state.materia_medica.load_merged_clinical_index(merged_index)
            if loaded:
                print(f"RadiWorks Engine — Original-Clinical-Index: {loaded} Symptome")
        yield
        state.loop = None

    app = FastAPI(
        title="RadiWorks Engine",
        version=manifest_module.KERNEL_VERSION,
        description=(
            "AetherOnePi-Kernlogik als Kernel-ABI-v1-konformer Dienst "
            "(Aurelia-Modul 'Werkbank'). Wellbeing-Dokumentation, kein Medizinprodukt."
        ),
        lifespan=lifespan,
    )

    app.include_router(build_router())

    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins if cors_origins is not None else DEFAULT_ORIGINS,
        allow_methods=["*"],
        allow_headers=["*"],
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

    app.state.settings_store = settings
    return app


# Dev-Standard: `uvicorn radiworks.main:app --port 8090`
app = create_app()
