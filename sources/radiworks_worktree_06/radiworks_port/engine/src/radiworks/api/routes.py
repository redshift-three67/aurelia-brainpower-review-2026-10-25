"""API_CONTRACT v1 — Endpunkte des RadiWorks-Kernels.

Vertrag: Modul_Templates/standards/API_CONTRACT.md
Original-Routen (Aliase): FUNKTIONSANALYSE §8 — ping, rates, analysis, gv,
case, broadcast, materiaMedicaSearch.
WebSocket: Fachkanal mit Umschlag {v:1, id, type, payload, ts} (docs/15-live.md),
Reconnect an letzter Event-ID.
"""

from __future__ import annotations

import asyncio
import time
import uuid
from collections import deque
from dataclasses import dataclass, field
from typing import Any

from fastapi import APIRouter, Header, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field

from .. import manifest as manifest_module
from ..config import SettingsStore
from ..core.analysis import (
    AnalysisResult,
    Rate,
    analyse_rate_list,
    check_general_vitality,
    check_percentage,
    search_anomaly,
    select_training_rate,
)
from ..core.automode import AutoModeController
from ..core.broadcast import BroadcastManager
from ..core.cases import CaseStore
from ..core.draft import DraftError, DraftStore
from ..core.essential import ask_essential_questions
from ..core.gvround import GvRoundState
from ..core.images import analyze_layers
from ..core.materia import MateriaMedica
from ..core.rates import RateRepository
from ..core.script import execute_script
from ..core.statistics import case_statistics
from ..core.stickpad import StickPad
from ..entropy import ENTROPY_MODES, EntropyProvider, WebcamFeedSource
from ..passport import Passport, now_ms

WS_EVENT_HISTORY = 256
# Boot-Kennung: WebSocket-Clients erkennen einen Engine-Neustart daran und
# verwerfen Geister-Panels (in-memory Queue stirbt mit dem Prozess).
BOOT_ID = uuid.uuid4().hex[:12]


@dataclass
class AppState:
    rate_repository: RateRepository
    case_store: CaseStore
    draft_store: DraftStore
    materia_medica: MateriaMedica
    broadcast: BroadcastManager | None
    settings_store: SettingsStore
    stick_pad: StickPad
    entropy_feed: WebcamFeedSource
    gv_round: GvRoundState | None = None
    training_signature: str | None = None
    live_provider: EntropyProvider | None = None
    auto: AutoModeController | None = None
    loop: asyncio.AbstractEventLoop | None = None

    def new_provider(self, seed: int | None, mode: str | None) -> EntropyProvider:
        """Zentrale Provider-Fabrik: geteilter Webcam-Feed über alle Requests."""
        return EntropyProvider(
            seed=seed,
            mode=mode if mode in ENTROPY_MODES else "seeded",
            feed=self.entropy_feed,
        )

    def live(self) -> EntropyProvider:
        """Persistenter Laufzeit-Provider für Ad-hoc-Züge (/gv, Anomalie,
        Fragen): zieht WEITER (kein Neustart je Request). Im Seed-Modus mit
        bootfestem Strom, im stochastischen Modus über die Fallback-Kette."""
        mode = self.settings_store.load("Settings").get_string("entropy.defaultMode", "seeded")
        if self.live_provider is None or self.live_provider.mode != mode:
            seed = int(time.time()) if mode == "seeded" else None
            self.live_provider = EntropyProvider(seed=seed, mode=mode, feed=self.entropy_feed)
        return self.live_provider
    event_history: deque[dict] = field(default_factory=deque)
    _ws_clients: set[WebSocket] = field(default_factory=set)
    _event_seq: int = 0

    def publish(self, event_type: str, payload: dict[str, Any]) -> None:
        """Event-Umschlag v:1 mit monotoner ID (Reconnect-Faehigkeit).

        Thread-sicher: aufrufbar aus dem Broadcast-Worker-Thread; der Versand
        an die WebSocket-Clients wird auf die Event-Loop verdrahtet.
        """
        self._event_seq += 1
        envelope = {
            "v": 1,
            "id": self._event_seq,
            "boot": BOOT_ID,
            "type": event_type,
            "payload": payload,
            "ts": int(time.time() * 1000),
        }
        self.event_history.append(envelope)
        if len(self.event_history) > WS_EVENT_HISTORY:
            self.event_history.popleft()
        if self.loop is not None and self._ws_clients:
            try:
                self.loop.call_soon_threadsafe(self._schedule_send, envelope)
            except RuntimeError:
                pass

    def _schedule_send(self, envelope: dict) -> None:
        task = asyncio.create_task(self._send_to_clients(envelope))
        _BACKGROUND_TASKS.add(task)
        task.add_done_callback(_BACKGROUND_TASKS.discard)

    async def _send_to_clients(self, envelope: dict) -> None:
        dead: list[WebSocket] = []
        for client in list(self._ws_clients):
            try:
                await client.send_json(envelope)
            except Exception:
                dead.append(client)
        for client in dead:
            self._ws_clients.discard(client)


_BACKGROUND_TASKS: set[asyncio.Task] = set()


def broadcast_emit(state: AppState):
    def emit(event_type: str, payload: dict[str, Any]) -> None:
        state.publish(event_type, payload)

    return emit


class AppStateHolder:
    """Spaet gebundener Zustand (create_app uebergibt die Instanz)."""

    def __init__(self) -> None:
        self.state: AppState | None = None


STATE = AppStateHolder()


# -- Request-/Response-Modelle ----------------------------------------------


class AnalysisRequest(BaseModel):
    database: str
    seed: int | None = None
    mode: str | None = None  # None => Settings-Schluessel entropy.defaultMode
    max_hits: int = Field(default=100, ge=100, le=1000)
    tenant_id: str | None = None
    client_id: str | None = None


class GvRequest(BaseModel):
    seed: int | None = None
    mode: str | None = None


class AnomalyRequest(BaseModel):
    width: int = Field(ge=1, le=200)
    height: int = Field(ge=1, le=200)
    seed: int | None = None
    mode: str | None = None


class CaseEnvelope(BaseModel):
    name: str | None = None
    description: str | None = None
    tenant_id: str | None = None
    client_id: str | None = None


class BroadcastRequest(BaseModel):
    signature: str
    seconds: int = Field(default=60, ge=1, le=24 * 3600)
    multiplier: int = Field(default=1, ge=1, le=1000)
    clear: bool = False
    delay_ms: int = Field(default=25, ge=1, le=10_000)
    repeat: int = Field(default=1, ge=1, le=1000)


class BroadcastMixRequest(BaseModel):
    draft_id: str
    max_rates: int = Field(default=8, ge=1, le=105)
    seconds_per_rate: int = Field(default=60, ge=1, le=24 * 3600)
    multiplier: int = Field(default=1, ge=1, le=1000)


class GvRoundRequest(BaseModel):
    seed: int | None = None
    mode: str | None = None


class EssentialRequest(BaseModel):
    seed: int | None = None
    mode: str | None = None


class StickPositionRequest(BaseModel):
    x: int = Field(ge=0, le=100_000)
    y: int = Field(ge=0, le=100_000)


class StickAnalyzeRequest(BaseModel):
    database: str


class TrainingStartRequest(BaseModel):
    database: str
    seed: int | None = None
    mode: str | None = None


class AutoModeRequest(BaseModel):
    database: str
    multiplier: int = Field(default=1, ge=1, le=1000)


class BroadcastFocusRequest(BaseModel):
    case: str | None = None
    intention: str | None = None


def _resolve_mode(state: "AppState", request_mode: str | None) -> str:
    """Festlegung 1: Mode None => Settings-Schluessel entropy.defaultMode.

    Factory-Default 'seeded' (Aurelia Hard Rule 7); der Praktiker kann in
    config/Settings.json 'stochastic' als Arbeitsmodus setzen.
    """
    if request_mode is None:
        return state.settings_store.load("Settings").get_string("entropy.defaultMode", "seeded")
    if request_mode not in ENTROPY_MODES:
        raise HTTPException(
            status_code=422,
            detail=f"mode muss einer von {ENTROPY_MODES} sein",
        )
    return request_mode


# -- Router -------------------------------------------------------------------


def build_router() -> APIRouter:
    router = APIRouter()

    # 0. Infrastruktur

    @router.get("/ping")
    def ping() -> dict:
        return {
            "result": "pong",
            "module": manifest_module.KERNEL_ID,
            "version": manifest_module.KERNEL_VERSION,
        }

    @router.get("/manifest")
    def get_manifest() -> dict:
        return manifest_module.manifest()

    @router.get("/entropy/status")
    def entropy_status() -> dict:
        state = STATE.state
        assert state is not None
        provider = EntropyProvider()
        status = provider.status()
        settings_default = state.settings_store.load("Settings").get_string(
            "entropy.defaultMode", "seeded"
        )
        return {
            "defaultMode": settings_default,
            "factoryDefault": "seeded",
            "modes": list(ENTROPY_MODES),
            "activeSource": status.active_source,
            "chain": status.chain,
            "note": (
                "Factory-Default seeded (Aurelia Hard Rule 7). Der Arbeitsmodus ist per "
                "Settings-Schluessel entropy.defaultMode umstellbar; jeder Lauf "
                "protokolliert seinen Modus im Computation Passport."
            ),
        }

    @router.post("/entropy/acquire")
    def entropy_acquire(body: dict | None = None) -> dict:
        """Aether_8 „GET HOTBITS": Webcam-Pakete im Original-Format
        {"integerList": [...]} einspeisen. Es werden NUR abgeleitete
        Ganzzahlen übernommen (>= 100, wie im Original), niemals Bildframes."""
        state = STATE.state
        assert state is not None
        values = (body or {}).get("integerList") or []
        accepted = state.entropy_feed.feed(values)
        return {
            "acquired": accepted,
            "feedSize": len(state.entropy_feed),
            "note": "Werte werden als Entropie-Seeds genutzt; keine Bildspeicherung.",
        }

    @router.get("/entropy/feed")
    def entropy_feed_state() -> dict:
        state = STATE.state
        assert state is not None
        return {"feedSize": len(state.entropy_feed)}

    # 2. Analyse

    @router.post("/analysis")
    def run_analysis(request: AnalysisRequest, x_client_seed: int | None = Header(default=None)) -> dict:
        state = STATE.state
        assert state is not None
        rates = state.rate_repository.find_all_by_source_name(request.database)
        if not rates:
            raise HTTPException(status_code=404, detail=f"Keine Raten fuer '{request.database}'")
        seed = request.seed if request.seed is not None else x_client_seed
        entropy = state.new_provider(seed, _resolve_mode(state, request.mode))
        passport = Passport.create(
            kernel=manifest_module.KERNEL_ID,
            kernel_version=manifest_module.KERNEL_VERSION,
            kernel_hash=manifest_module.kernel_hash(),
            input_payload={"database": request.database, "seed": seed, "max_hits": request.max_hits},
            entropy=entropy,
            tenant_id=request.tenant_id,
            client_id=request.client_id,
        )
        started = now_ms()
        state.publish(
            "analysis.progress",
            {"database": request.database, "stage": "started", "runId": passport.run_id},
        )
        result = analyse_rate_list(rates, entropy, max_hits=request.max_hits)
        result.general_vitality = check_general_vitality(entropy)
        # Die GV-Runde setzt den Entropiestrom DER ANALYSE fort (Original:
        # weitere Züge aus demselben Hotbits-Cache) — kein Neustart je Request.
        state.gv_round = GvRoundState(result=result, entropy=entropy)
        passport.finish(
            dauer_ms=now_ms() - started,
            sources={"gv": "derived", "energeticValue": "derived", "potency": "derived"},
        )
        result_dict = result.to_dict()
        # Vektor/Fokus (Frage g): aktiver Fall + Absicht wandern ins Artefakt
        focus: dict[str, Any] = {}
        current_case = state.case_store.current
        if current_case and current_case.get("name"):
            sessions = current_case.get("sessionList") or []
            focus = {
                "case": current_case.get("name"),
                "intention": (sessions[-1].get("intention") if sessions else None),
            }
        draft = state.draft_store.create_from_analysis(
            analysis_dict=result_dict,
            passport=passport.to_dict(),
            database=request.database,
            tenant_id=request.tenant_id,
            client_id=request.client_id,
            focus=focus or None,
        )
        state.case_store.attach_analysis(result_dict, passport.to_dict())
        state.publish(
            "analysis.update",
            {"runId": passport.run_id, "draftId": draft["id"], "result": result_dict},
        )
        return {"passport": passport.to_dict(), "result": result_dict, "draft": _draft_view(draft)}

    @router.get("/analysis/current")
    def current_analysis() -> dict:
        state = STATE.state
        assert state is not None
        drafts = state.draft_store.list()
        if not drafts:
            return {"passport": None, "result": None}
        latest = drafts[-1]
        return {"result": latest["payload"], "draft": _draft_view(latest)}

    # ---- GV-Runde (FUNKTIONSABGLEICH ①, Aether_4: "GV (runs = n)") ----

    @router.post("/analysis/gv-round")
    def gv_round(request: GvRoundRequest) -> dict:
        state = STATE.state
        assert state is not None
        if state.gv_round is None:
            raise HTTPException(status_code=409, detail="Keine Analyse im Speicher — erst /analysis ausführen.")
        # Ohne seed/mode: Analyse-Strom fortsetzen (jeder Zug anders, mit
        # Seed replizierbar). Mit seed/mode: bewusster Neustart des Stroms.
        if request.seed is not None or request.mode is not None:
            state.gv_round.entropy = state.new_provider(request.seed, _resolve_mode(state, request.mode))
        return state.gv_round.step()

    @router.post("/analysis/gv-round/reset")
    def gv_round_reset() -> dict:
        state = STATE.state
        assert state is not None
        if state.gv_round is None:
            raise HTTPException(status_code=409, detail="Keine Analyse im Speicher.")
        state.gv_round.clean()
        return {"state": state.gv_round.state_dict(), "result": state.gv_round.result.to_dict()}

    @router.get("/analysis/gv-round")
    def gv_round_state() -> dict:
        state = STATE.state
        assert state is not None
        if state.gv_round is None:
            return {"active": False}
        return {"active": True, **state.gv_round.state_dict()}

    # ---- Essenzielle Fragen (FUNKTIONSABGLEICH ②) ----

    @router.post("/essential-questions")
    def essential_questions(request: EssentialRequest) -> dict:
        state = STATE.state
        assert state is not None
        entropy = state.new_provider(request.seed, _resolve_mode(state, request.mode))
        return {"report": ask_essential_questions(entropy)}

    # ---- Settings (FUNKTIONSABGLEICH ③, Aether_3) ----

    # Kanonische Schalter des Originals (Aether_3-Aufnahme) + Kernel-Festlegungen;
    # Selbst-Default wie im Original: erster Zugriff persistiert den Default.
    CANONICAL_BOOLEANS: dict[str, bool] = {
        "analysis.very.high.max.hit": False,
        "broadcast.delta.time": False,
        "broadcast.embedded": True,
        "broadcast.single.rates.only": False,
        "dynamic.adjustments": False,
        "notification.after.broadcast": True,
        "play.binaural.sound": False,
        "power.switch": False,
        "use.overlay": False,
        "watchlist.activate": False,
        "broadcast.legacyMixMode": False,
    }

    @router.get("/settings")
    def get_settings() -> dict:
        state = STATE.state
        assert state is not None
        settings = state.settings_store.load("Settings")
        for key, default in CANONICAL_BOOLEANS.items():
            settings.get_boolean(key, default)
        settings.get_string("entropy.defaultMode", "seeded")
        return settings.to_dict()

    @router.put("/settings")
    def put_settings(body: dict) -> dict:
        state = STATE.state
        assert state is not None
        settings = state.settings_store.load("Settings")
        for key, value in (body.get("booleans") or {}).items():
            if not isinstance(value, bool):
                raise HTTPException(status_code=422, detail=f"booleans.{key} muss bool sein")
            settings.set_boolean(key, value)
        for key, value in (body.get("integers") or {}).items():
            if not isinstance(value, int) or isinstance(value, bool):
                raise HTTPException(status_code=422, detail=f"integers.{key} muss int sein")
            settings.set_integer(key, value)
        for key, value in (body.get("strings") or {}).items():
            if not isinstance(value, str):
                raise HTTPException(status_code=422, detail=f"strings.{key} muss str sein")
            settings.set_string(key, value)
        return settings.to_dict()

    # ---- Fall-Statistik (FUNKTIONSABGLEICH ⑥, StatisticsGenerator) ----

    @router.get("/cases/{name}/statistics")
    def case_statistics_endpoint(name: str) -> dict:
        state = STATE.state
        assert state is not None
        case = state.case_store.load(name)
        if case is None:
            raise HTTPException(status_code=404, detail=f"Case '{name}' nicht gefunden")
        top = case_statistics(case)
        state.case_store.save(case)  # Original: start() mutiert das Case (topTenList)
        return {"case": name, "sessions": len(case.get("sessionList", [])), "topList": top}

    # ---- Bildschichten (FUNKTIONSABGLEICH ⑦, Aether_5) ----

    @router.post("/images/analyze")
    def images_analyze(body: dict) -> dict:
        """`{"count": n}` — GV je Schicht (Original: 256 Züge, Runden bis
        max >= 162). Bilder selbst bleiben im Browser; nur die Anzahl wird
        analysiert — MD5/Zeugen pflegt der Client (Passport-`input_hash`)."""
        state = STATE.state
        assert state is not None
        count = int(body.get("count", 0))
        if count < 1 or count > 50:
            raise HTTPException(status_code=422, detail="count muss 1..50 sein")
        entropy = state.new_provider(body.get("seed"), _resolve_mode(state, body.get("mode")))
        return analyze_layers(count, entropy)

    @router.post("/images/broadcast")
    def images_broadcast(body: dict) -> dict:
        state = STATE.state
        assert state is not None
        md5 = str(body.get("md5", "")).strip()
        if not md5:
            raise HTTPException(status_code=422, detail="md5 fehlt")
        queued = state.broadcast.enqueue(f"IMAGE:{md5}", int(body.get("seconds", 60)), int(body.get("multiplier", 1)))
        state.publish("broadcast.progress", {"signature": queued["signature"], "progress": 0.0, "started": True})
        return queued

    # ---- RadionicScript / PEGGOTTY (FUNKTIONSABGLEICH ⑨) ----

    @router.post("/script/execute")
    def script_execute(body: dict) -> dict:
        state = STATE.state
        assert state is not None
        lines: list[str]
        if body.get("name"):
            path = state.rate_repository._scripts.get(str(body["name"]) + ".rscript")
            if path is None:
                raise HTTPException(status_code=404, detail=f"Skript '{body['name']}' nicht gefunden")
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        elif body.get("script"):
            lines = str(body["script"]).splitlines()
        else:
            raise HTTPException(status_code=422, detail="script (Text) oder name erforderlich")
        entropy = state.new_provider(body.get("seed"), _resolve_mode(state, body.get("mode")))
        result = execute_script(
            lines,
            find_rates=state.rate_repository.find_all_by_source_name,
            entropy=entropy,
        )
        return result.to_dict()

    @router.get("/scripts")
    def list_scripts() -> dict:
        state = STATE.state
        assert state is not None
        return {"scripts": state.rate_repository.script_names()}

    @router.get("/scripts/{name}")
    def read_script(name: str) -> dict:
        state = STATE.state
        assert state is not None
        path = state.rate_repository._scripts.get(name if name.endswith(".rscript") else name + ".rscript")
        if path is None:
            raise HTTPException(status_code=404, detail=f"Skript '{name}' nicht gefunden")
        return {"name": name, "content": path.read_text(encoding="utf-8", errors="replace")}

    # ---- Trainings-Modus (Aether_4: TRAINING[START]/[UNCOVER]) ----

    @router.post("/training/start")
    def training_start(request: TrainingStartRequest) -> dict:
        """Event-Handler.trainingSelectSignatureFromCurrentDatabase: verdeckte
        Signatur aus der gewählten Datenbank ziehen."""
        state = STATE.state
        assert state is not None
        rates = state.rate_repository.find_all_by_source_name(request.database)
        if not rates:
            raise HTTPException(status_code=404, detail=f"Keine Raten fuer '{request.database}'")
        entropy = state.new_provider(request.seed, _resolve_mode(state, request.mode))
        state.training_signature = select_training_rate(rates, entropy)
        return {"active": True, "covered": True}

    @router.post("/training/uncover")
    def training_uncover() -> dict:
        """TRAINING[UNCOVER]: lüftet die Signatur (Original: print + UI)."""
        state = STATE.state
        assert state is not None
        if state.training_signature is None:
            raise HTTPException(status_code=409, detail="Kein Training aktiv — erst TRAINING[START].")
        return {"active": True, "covered": False, "signature": state.training_signature}

    @router.get("/training")
    def training_state() -> dict:
        state = STATE.state
        assert state is not None
        return {"active": state.training_signature is not None}

    @router.delete("/training")
    def training_stop() -> dict:
        state = STATE.state
        assert state is not None
        state.training_signature = None
        return {"active": False}

    # ---- Auto-Modus (Aether_4: AUTO MODE ON/OFF = Harmonisierungsregler) ----

    @router.post("/auto-mode/on")
    def auto_mode_on(request: AutoModeRequest) -> dict:
        """Original handleAutoMode: bei leerer Queue und GV <= 300 analysiert
        der Regelkreis selbstständig und sendet eine Rate 10-1000 s
        (Hotbits-Wurf, UI-Multiplikator). Server ist die Uhr."""
        state = STATE.state
        assert state is not None
        rates = state.rate_repository.find_all_by_source_name(request.database)
        if not rates:
            raise HTTPException(status_code=404, detail=f"Keine Raten fuer '{request.database}'")
        assert state.auto is not None
        state.broadcast.ensure_running()
        snapshot = state.auto.start(request.database, request.multiplier)
        return snapshot

    @router.post("/auto-mode/off")
    def auto_mode_off() -> dict:
        state = STATE.state
        assert state is not None
        assert state.auto is not None
        return state.auto.stop()

    @router.get("/auto-mode")
    def auto_mode_state() -> dict:
        state = STATE.state
        assert state is not None
        assert state.auto is not None
        return state.auto.state.snapshot()

    # ---- Stick-Pad (FUNKTIONSABGLEICH ④, Aether_6) ----

    @router.post("/stickpad/position")
    def stickpad_position(request: StickPositionRequest) -> dict:
        state = STATE.state
        assert state is not None
        count = state.stick_pad.add_position(request.x, request.y)
        return {"positions": count}

    @router.post("/stickpad/analyze")
    def stickpad_analyze(request: StickAnalyzeRequest) -> dict:
        state = STATE.state
        assert state is not None
        rates = state.rate_repository.find_all_by_source_name(request.database)
        if not rates:
            raise HTTPException(status_code=404, detail=f"Keine Raten fuer '{request.database}'")
        if not state.stick_pad.positions:
            raise HTTPException(status_code=409, detail="Keine Stick-Pad-Positionen gesammelt.")
        result = state.stick_pad.analyze(rates)
        return result.to_dict()

    @router.post("/stickpad/gv")
    def stickpad_gv() -> dict:
        state = STATE.state
        assert state is not None
        gv = state.stick_pad.check_general_vitality()
        return {"gv": gv, "positions": len(state.stick_pad.positions)}

    @router.delete("/stickpad")
    def stickpad_clear() -> dict:
        state = STATE.state
        assert state is not None
        cleared = state.stick_pad.clear()
        return {"cleared": cleared}

    # Original-Alias
    @router.get("/analysis")
    def analysis_alias() -> dict:
        return current_analysis()

    @router.post("/gv")
    def general_vitality(request: GvRequest) -> dict:
        state = STATE.state
        assert state is not None
        # Ohne seed: Laufzeit-Strom (jeder Aufruf anders); mit seed: fest.
        entropy = (
            state.new_provider(request.seed, _resolve_mode(state, request.mode))
            if request.seed is not None or request.mode is not None
            else state.live()
        )
        return {"gv": check_general_vitality(entropy), "source": "derived"}

    @router.post("/search-anomaly")
    def anomaly(request: AnomalyRequest) -> dict:
        state = STATE.state
        assert state is not None
        entropy = (
            state.new_provider(request.seed, _resolve_mode(state, request.mode))
            if request.seed is not None or request.mode is not None
            else state.live()
        )
        matrix = search_anomaly(request.width, request.height, entropy)
        return {"width": request.width, "height": request.height, "values": matrix}

    # 1. Entropie-Alias lt. Contract

    @router.get("/databases")
    def databases() -> dict:
        state = STATE.state
        assert state is not None
        return {"databases": state.rate_repository.database_names()}

    # Original-Alias
    @router.get("/rates")
    def rates_alias() -> dict:
        return databases()

    # 3. Session / Case

    @router.get("/cases")
    def cases() -> dict:
        state = STATE.state
        assert state is not None
        return {"cases": state.case_store.list_names()}

    @router.post("/cases")
    def save_case(case: dict) -> dict:
        state = STATE.state
        assert state is not None
        return state.case_store.save(case)

    @router.get("/cases/current")
    def current_case() -> dict:
        state = STATE.state
        assert state is not None
        return state.case_store.current or {}

    @router.get("/cases/recent")
    def recent_cases() -> dict:
        """Original „LAST CASES“ (dashboardInformations.json, max. 11)."""
        state = STATE.state
        assert state is not None
        return {"recent": state.case_store.recent_list()}

    # ---- Session-Navigation (Original: ←/→ + analysisPointer) ----

    @router.get("/analysis/sessions")
    def analysis_sessions() -> dict:
        state = STATE.state
        assert state is not None
        case = state.case_store.current
        if not case:
            return {"sessions": []}
        sessions = []
        for index, session in enumerate(case.get("sessionList", [])):
            result = session.get("analysisResult")
            sessions.append(
                {
                    "index": index,
                    "created": session.get("created"),
                    "intention": session.get("intention"),
                    "hasResult": bool(result),
                    "generalVitality": (result or {}).get("generalVitality"),
                    "rates": len((result or {}).get("rateObjects", [])),
                }
            )
        return {"sessions": sessions}

    @router.post("/analysis/sessions/{index}/view")
    def view_session(index: int) -> dict:
        """Historische Session als aktuelle Ansicht laden; die GV-Runde
        setzt den Strom mit dem SESSION-Seed fort (Passport-Angabe)."""
        state = STATE.state
        assert state is not None
        case = state.case_store.current
        if not case:
            raise HTTPException(status_code=409, detail="Kein Fall geladen.")
        sessions = case.get("sessionList", [])
        if index < 0 or index >= len(sessions):
            raise HTTPException(status_code=404, detail="Session existiert nicht.")
        stored = sessions[index].get("analysisResult")
        if not stored:
            raise HTTPException(status_code=409, detail="Session hat kein Analyseergebnis.")
        session_seed = (sessions[index].get("passport") or {}).get("seed")
        provider = state.new_provider(session_seed, None)
        state.gv_round = GvRoundState(result=AnalysisResult.from_dict(stored), entropy=provider)
        state.gv_round.general_vitality = stored.get("generalVitality") or 0
        return {"pointer": index, "result": stored, "state": state.gv_round.state_dict()}

    @router.get("/cases/{name}")
    def load_case(name: str) -> dict:
        state = STATE.state
        assert state is not None
        case = state.case_store.load(name)
        if case is None:
            raise HTTPException(status_code=404, detail=f"Case '{name}' nicht gefunden")
        return case

    # Original-Alias: GET /case?name=...
    @router.get("/case")
    def case_alias(name: str | None = None) -> dict:
        if name is None:
            return cases()
        return load_case(name)

    # 4. Draft (Zwischenablage, D18)

    @router.get("/drafts")
    def drafts(status: str | None = None) -> dict:
        state = STATE.state
        assert state is not None
        return {"drafts": [_draft_view(d) for d in state.draft_store.list(status)]}

    @router.get("/drafts/{draft_id}")
    def draft_by_id(draft_id: str) -> dict:
        state = STATE.state
        assert state is not None
        draft = state.draft_store.get(draft_id)
        if draft is None:
            raise HTTPException(status_code=404, detail="Draft nicht gefunden")
        return _draft_view(draft)

    @router.post("/drafts/{draft_id}/promote")
    def promote_draft(draft_id: str, body: dict | None = None) -> dict:
        state = STATE.state
        assert state is not None
        body = body or {}
        try:
            entries = state.draft_store.promote_to_broadcast_queue(
                draft_id,
                max_rates=int(body.get("max_rates", 8)),
                seconds_per_rate=int(body.get("seconds_per_rate", 60)),
                multiplier=int(body.get("multiplier", 1)),
            )
        except DraftError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        for entry in entries:
            state.broadcast.enqueue(**entry)
        state.publish("clipboard.updated", {"draftId": draft_id, "status": "promoted", "queued": len(entries)})
        return {"draftId": draft_id, "status": "promoted", "broadcastEntries": entries}

    @router.post("/drafts/{draft_id}/transition")
    def transition_draft(draft_id: str, body: dict) -> dict:
        state = STATE.state
        assert state is not None
        try:
            draft = state.draft_store.transition(draft_id, body.get("status", ""))
        except DraftError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        state.publish("clipboard.updated", {"draftId": draft_id, "status": draft["status"]})
        return _draft_view(draft)

    @router.post("/drafts/{draft_id}/discard")
    def discard_draft(draft_id: str) -> dict:
        return transition_draft(draft_id, {"status": "discarded"})

    # 4. Broadcast

    @router.post("/broadcast")
    def broadcast(request: BroadcastRequest) -> dict:
        """Direkter Operator-Broadcast (bewusster Befehl, kein stiller Copy)."""
        state = STATE.state
        assert state is not None
        queued = state.broadcast.enqueue(
            request.signature,
            request.seconds,
            request.multiplier,
            clear=request.clear,
            delay_ms=request.delay_ms,
            repeat=request.repeat,
        )
        state.publish("broadcast.progress", {"signature": request.signature, "progress": 0.0, "started": True})
        return queued

    @router.post("/broadcast/mix")
    def broadcast_mix(request: BroadcastMixRequest) -> dict:
        """Original 'BROADCAST MIX' — Festlegung 2 (2026-08-29).

        Settings broadcast.legacyMixMode=true: ein Klick — Draft wird in einer
        Kette (draft -> ready -> promoted) mit CopyGuard-Pruefung uebernommen.
        false (Default, Aurelia D18): 409 — Draft muss sichtbar geprueft und
        ueber /drafts/{id}/promote freigegeben werden.
        """
        state = STATE.state
        assert state is not None
        legacy = state.settings_store.load("Settings").get_boolean("broadcast.legacyMixMode", False)
        if not legacy:
            raise HTTPException(
                status_code=409,
                detail=(
                    "broadcast.legacyMixMode ist aus (Aurelia D18): Draft zuerst prüfen "
                    "und dann über /drafts/{id}/promote freigeben."
                ),
            )
        try:
            state.draft_store.transition(request.draft_id, "ready")
            entries = state.draft_store.promote_to_broadcast_queue(
                request.draft_id,
                max_rates=request.max_rates,
                seconds_per_rate=request.seconds_per_rate,
                multiplier=request.multiplier,
            )
        except DraftError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        for entry in entries:
            state.broadcast.enqueue(**entry)
        state.publish(
            "clipboard.updated",
            {"draftId": request.draft_id, "status": "promoted", "mode": "legacy-mix", "queued": len(entries)},
        )
        return {"draftId": request.draft_id, "status": "promoted", "mode": "legacy-mix", "broadcastEntries": entries}

    @router.get("/broadcast/queue")
    def broadcast_queue() -> dict:
        state = STATE.state
        assert state is not None
        return state.broadcast.queue_state()

    @router.delete("/broadcast/current")
    def stop_current() -> dict:
        state = STATE.state
        assert state is not None
        state.broadcast.stop_current()
        return {"stopped": "current"}

    @router.delete("/broadcast/all")
    def stop_all() -> dict:
        state = STATE.state
        assert state is not None
        state.broadcast.stop_all()
        return {"stopped": "all"}

    # 9. Materia Medica

    @router.post("/materia/clarke-compare")
    def clarke_compare(body: dict) -> dict:
        """CLARKE-Button des Originals (Aether_4): Symptom-Vergleich der
        aktuellen Analyse mit der Ziel-Remedy (AnalysisService.analyzeClarke,
        Berechnungsteil; Report rendert die Webapp)."""
        state = STATE.state
        assert state is not None
        rate = str(body.get("rate", "")).strip()
        if not rate:
            raise HTTPException(status_code=422, detail="rate fehlt")
        result = state.gv_round.result if state.gv_round else None
        names = [r.name_or_rate for r in result.rate_objects] if result else []
        return state.materia_medica.compare_clarke(rate, names)

    @router.get("/materiaMedicaSearch")
    def materia_search(field: str | None = None, query: str = "") -> dict:
        state = STATE.state
        assert state is not None
        if len(query) < 3:
            return {"searchResults": []}
        return {"searchResults": state.materia_medica.search(query, field)}

    # WebSocket-Fachkanal — als Router-Route registriert, damit er mit allen
    # REST-Routen aus einer Quelle (include_router) eingebunden wird.
    # HINWEIS Betrieb: uvicorn benoetigt eine WebSocket-Bibliothek
    # (`pip install websockets`), sonst antwortet der Handshake mit 404.
    @router.websocket("/ws")
    async def ws_channel(websocket: WebSocket, last_event_id: int | None = None) -> None:
        await websocket_endpoint(websocket, last_event_id)

    return router


def _draft_view(draft: dict) -> dict:
    """Draft ohne volles Payload (Payload nur unter /drafts/{id})."""
    return {k: v for k, v in draft.items() if k != "payload"}


# -- WebSocket -----------------------------------------------------------------


async def websocket_endpoint(websocket: WebSocket, last_event_id: int | None = None) -> None:
    state = STATE.state
    assert state is not None
    await websocket.accept()
    state._ws_clients.add(websocket)
    try:
        if last_event_id is not None:
            for envelope in list(state.event_history):
                if envelope["id"] > last_event_id:
                    await websocket.send_json(envelope)
        while True:
            message = await websocket.receive_text()
            if message == "ping":
                await websocket.send_json({"v": 1, "type": "pong", "payload": {}, "ts": 0})
    except WebSocketDisconnect:
        pass
    finally:
        state._ws_clients.discard(websocket)
