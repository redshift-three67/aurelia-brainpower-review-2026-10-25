"""API_CONTRACT v1 — Endpunkte des RadiWorks-Kernels.

Vertrag: Modul_Templates/standards/API_CONTRACT.md
Original-Routen (Aliase): FUNKTIONSANALYSE §8 — ping, rates, analysis, gv,
case, broadcast, materiaMedicaSearch.
WebSocket: Fachkanal mit Umschlag {v:1, id, boot, type, payload, ts}
(docs/15-live.md). Positive IDs kennzeichnen replayfähige Fachereignisse;
Kontrollereignisse verwenden ID 0. Reconnect erfolgt an letzter Event-ID und
Boot-Kennung.
"""

from __future__ import annotations

import asyncio
import base64
import binascii
import copy
import hashlib
import json
import logging
import threading
import time
import uuid
from collections import deque
from dataclasses import dataclass, field
from functools import wraps
from pathlib import Path
from typing import Any, Literal

from fastapi import APIRouter, Header, HTTPException, Request, Response, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictInt, StrictStr, field_validator

from .. import copyguard
from .. import manifest as manifest_module
from ..config import SettingsStore
from ..core.comparison_basis import capture_catalog, make_source, source_reference, ComparisonBasisError
from ..core.analysis import (
    ALLOWED_MAX_HITS,
    AnalysisResult,
    Rate,
    analyse_rate_list,
    check_general_vitality,
    check_percentage,
    search_anomaly,
    select_training_rate,
)
from ..core.automode import AutoModeController
from ..core.broadcast import (
    MAX_BROADCAST_SECONDS,
    MAX_DELAY_MS,
    MAX_MULTIPLIER,
    MAX_REPEAT,
    MIN_BROADCAST_SECONDS,
    MIN_DELAY_MS,
    MIN_MULTIPLIER,
    MIN_REPEAT,
    BroadcastError,
    BroadcastManager,
)
from ..core.cases import CaseNameError, CaseStore, SessionError
from ..core.context_images import ContextImageStore, ContextImageError, MAX_UPLOAD_BODY
from ..core.presentation_profile import (
    AUDIO_PROFILE_IDS,
    PULSE_PROFILE_IDS,
    PresentationProfileError,
    PresentationProfileStore,
)
from ..core.catalog_suggestions import RULE_VERSION, query_terms, rank_catalog
from ..core.catalog_suggestion_sources import catalog_snapshot, CatalogSearchBoundsError, CatalogSearchDrift
from ..core.personal_context import ContextError, ContextSnapshot, normalize_personal
from ..core.broadcast_policy import ExecutionPolicy, PolicyError, VERSION as OPTIONS_VERSION
from ..core.broadcast_target import BroadcastTarget, BroadcastTargetStore, BroadcastTargetError
from ..core.draft import DraftError, DraftStore
from ..core.essential import ask_essential_questions
from ..core.gvround import GvRoundState, MAX_ROUND_STEPS
from ..core.images import analyze_layers
from ..core.materia import MateriaMedica
from ..core.rates import CatalogSnapshotError, RateRepository, catalog_binding
from ..core.script import DuplicateScriptLabelError, execute_script
from ..core.observation_binding import bind_promoted_rates
from ..core.gv_observations import GvObservationController
from ..core.watchlist import WatchlistController, WatchlistError
from ..core.statistics import case_statistics
from ..core.stickpad import StickPad
from ..entropy import ENTROPY_MODES, EntropyProvider, RandomOrgSource, WebcamFeedSource
from ..entropy_journal import EntropyJournal, EntropyJournalStore, JournalConfigurationError
from ..passport import Passport, now_ms
from ..persistence import RecoveryCoordinator, RecoveryError, RecoveryTarget, document_digest
from ..scope import ScopeContext, ScopeResolver

WS_EVENT_HISTORY = 256
WS_CLIENT_QUEUE = WS_EVENT_HISTORY
WS_HANDSHAKE_QUEUE = WS_EVENT_HISTORY
WS_SEND_TIMEOUT_S = 5.0
WS_HANDSHAKE_TIMEOUT_S = 10.0
WS_SHUTDOWN_TIMEOUT_S = 1.0
# Boot-Kennung: WebSocket-Clients erkennen einen Engine-Neustart daran und
# verwerfen Geister-Panels (in-memory Queue stirbt mit dem Prozess).
BOOT_ID = uuid.uuid4().hex[:12]


def control_envelope(event_type: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    """Nicht historisierter WS-Kontrollumschlag; ID 0 ist kein Replay-Cursor."""
    return {
        "v": 1,
        "id": 0,
        "boot": BOOT_ID,
        "type": event_type,
        "payload": payload or {},
        "ts": int(time.time() * 1000),
    }


@dataclass
class _PendingHandshake:
    events: deque[dict] = field(
        default_factory=lambda: deque(maxlen=WS_HANDSHAKE_QUEUE)
    )
    overflowed: bool = False


class _HandshakeOverflow(RuntimeError):
    pass


class _HandshakeDeadline(RuntimeError):
    pass


class EntropyConfigurationError(ValueError):
    """Die persistierte Entropie-Konfiguration verletzt den Vertragsbereich."""


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
    random_org: RandomOrgSource
    journal_dir: Path
    recovery: RecoveryCoordinator
    scope: ScopeContext
    scope_resolver: ScopeResolver
    gv_round: GvRoundState | None = None
    training_signature: str | None = None
    live_provider: EntropyProvider | None = None
    observations: GvObservationController | None = None
    watchlist: WatchlistController | None = None
    auto: AutoModeController | None = None
    auto_jobs: Any = None
    personal: Any = None
    comparisons: Any = None
    broadcast_targets: BroadcastTargetStore | None = None
    presentation_profiles: PresentationProfileStore | None = None
    loop: asyncio.AbstractEventLoop | None = None

    def broadcast_capacity(self, saved=None) -> int:
        if saved is None: saved = self.settings_store.load("Settings").to_dict()
        active = saved["strings"].get("broadcast.optionsVersion") == OPTIONS_VERSION
        return 1 if active and saved["booleans"].get("broadcast.single.rates.only") is True else 8

    def broadcast_policy(self, target, seconds, *, allow_delta=True, saved=None):
        reference = None
        if target is not None:
            proof = target.payload()
            snapshot = proof.get("contextSnapshot")
            source = proof["source"]
            if proof["procedure"] == "original-aetherone-v1" and proof["binding"] == "bound":
                if source.get("draftId"):
                    draft = self.draft_store.get(source["draftId"])
                    if draft and draft.get("contextSnapshot") == snapshot:
                        reference = draft.get("payload", {}).get("generalVitality")
                elif source.get("sessionId") and snapshot:
                    owner = self.case_store.find_identity(snapshot["caseId"])
                    if owner:
                        matches = [row for row in owner[1].get("sessionList", []) if row.get("sessionId") == source["sessionId"] and row.get("contextSnapshot") == snapshot]
                        if len(matches) == 1:
                            reference = matches[0].get("analysisResult", {}).get("generalVitality")
        return ExecutionPolicy.capture(saved if saved is not None else self.settings_store.load("Settings").to_dict(), target, seconds, reference, allow_delta=allow_delta)

    def resolve_entropy_mode(self, requested_mode: str | None) -> str:
        if requested_mode is not None:
            if requested_mode not in ENTROPY_MODES:
                raise EntropyConfigurationError(
                    f"mode muss einer von {ENTROPY_MODES} sein"
                )
            return requested_mode
        mode = self.settings_store.load("Settings").strings.get(
            "entropy.defaultMode", "seeded"
        )
        if mode not in ENTROPY_MODES:
            raise EntropyConfigurationError(
                f"entropy.defaultMode muss einer von {ENTROPY_MODES} sein"
            )
        return mode

    def new_provider(
        self,
        seed: int | None,
        mode: str | None,
        *,
        journal: EntropyJournal | None = None,
        source_segment: int = 0,
    ) -> EntropyProvider:
        """Zentrale Provider-Fabrik mit geteiltem Hotbits- und random.org-Cache."""
        return EntropyProvider(
            seed=seed,
            mode=self.resolve_entropy_mode(mode),
            feed=self.entropy_feed,
            random_org=self.random_org,
            journal=journal,
            source_segment=source_segment,
        )

    def create_entropy_journal(self) -> EntropyJournal:
        return EntropyJournalStore(self.journal_dir).create()

    def open_entropy_journal(self, journal_id: str) -> EntropyJournal:
        return EntropyJournalStore(self.journal_dir).open(journal_id)

    def live(self) -> EntropyProvider:
        """Persistenter Laufzeit-Strom fuer Ad-hoc-Zuege und Auto-Modus."""
        mode = self.resolve_entropy_mode(None)
        if self.live_provider is None or self.live_provider.mode != mode:
            seed = int(time.time()) if mode == "seeded" else None
            self.live_provider = EntropyProvider(
                seed=seed,
                mode=mode,
                feed=self.entropy_feed,
                random_org=self.random_org,
            )
        return self.live_provider
    event_history: deque[dict] = field(default_factory=deque)
    _ws_clients: set[WebSocket] = field(default_factory=set)
    _ws_pending: dict[WebSocket, _PendingHandshake] = field(default_factory=dict)
    _event_seq: int = 0
    _event_lock: Any = field(default_factory=threading.RLock, repr=False)
    _promotion_lock: Any = field(default_factory=threading.RLock, repr=False)
    _ws_queues: dict[WebSocket, asyncio.Queue[dict]] = field(default_factory=dict)
    _ws_senders: dict[WebSocket, asyncio.Task] = field(default_factory=dict)
    _ws_tasks: set[asyncio.Task] = field(default_factory=set)

    def publish(self, event_type: str, payload: dict[str, Any]) -> None:
        """Event-Umschlag v:1 mit monotoner ID (Reconnect-Faehigkeit).

        Thread-sicher: aufrufbar aus dem Broadcast-Worker-Thread; Clients im
        Handshake puffern neue Events, etablierte Clients werden als Snapshot
        auf die Event-Loop verdrahtet.
        """
        if event_type == "broadcast.progress":
            try:
                if self.broadcast_targets is not None:
                    self.broadcast_targets.terminal(payload)
            except (OSError, BroadcastTargetError):
                logging.getLogger(__name__).exception("Broadcast-Zielabschluss konnte nicht persistiert werden")
            try:
                self.draft_store.record_broadcast_terminal(payload)
            except OSError:
                logging.getLogger(__name__).exception("Broadcast-Abschluss konnte nicht persistiert werden")
        public_payload = copyguard.public_view(payload)
        with self._event_lock:
            self._event_seq += 1
            envelope = {
                "v": 1,
                "id": self._event_seq,
                "boot": BOOT_ID,
                "type": event_type,
                "payload": public_payload,
                "ts": int(time.time() * 1000),
            }
            self.event_history.append(envelope)
            if len(self.event_history) > WS_EVENT_HISTORY:
                self.event_history.popleft()
            for pending in self._ws_pending.values():
                if pending.overflowed:
                    continue
                if len(pending.events) >= WS_HANDSHAKE_QUEUE:
                    pending.overflowed = True
                    continue
                pending.events.append(envelope)
            clients = tuple(self._ws_clients)
            if self.loop is not None and clients:
                try:
                    self.loop.call_soon_threadsafe(
                        self._schedule_send,
                        envelope,
                        clients,
                    )
                except RuntimeError:
                    pass

    def _schedule_send(
        self,
        envelope: dict,
        clients: tuple[WebSocket, ...],
    ) -> None:
        for client in clients:
            with self._event_lock:
                if client not in self._ws_clients:
                    continue
            queue = self._ws_queues.get(client)
            if queue is None:
                queue = asyncio.Queue(maxsize=WS_CLIENT_QUEUE)
                self._ws_queues[client] = queue
                sender = asyncio.create_task(self._send_client_queue(client, queue))
                self._ws_senders[client] = sender
                self._ws_tasks.add(sender)
                sender.add_done_callback(self._ws_tasks.discard)
            try:
                queue.put_nowait(envelope)
            except asyncio.QueueFull:
                self._remove_ws_client(client)
                closer = asyncio.create_task(self._close_ws_client(client, code=1013))
                self._ws_tasks.add(closer)
                closer.add_done_callback(self._ws_tasks.discard)

    async def _send_client_queue(
        self,
        client: WebSocket,
        queue: asyncio.Queue[dict],
    ) -> None:
        try:
            while True:
                envelope = await queue.get()
                await asyncio.wait_for(
                    client.send_json(envelope),
                    timeout=WS_SEND_TIMEOUT_S,
                )
        except asyncio.CancelledError:
            raise
        except Exception:
            await self._close_ws_client(client, code=1011)
        finally:
            self._remove_ws_client(client, cancel_sender=False)

    async def _close_ws_client(self, client: WebSocket, *, code: int) -> None:
        try:
            await asyncio.wait_for(client.close(code=code), timeout=1.0)
        except Exception:
            pass

    def _remove_ws_client(
        self,
        client: WebSocket,
        *,
        cancel_sender: bool = True,
    ) -> None:
        with self._event_lock:
            self._ws_clients.discard(client)
            self._ws_pending.pop(client, None)
        self._ws_queues.pop(client, None)
        sender = self._ws_senders.pop(client, None)
        if cancel_sender and sender is not None and not sender.done():
            sender.cancel()

    async def shutdown_websockets(self) -> None:
        """Schließt Handshakes, Live-Clients und alle WS-Tasks begrenzt."""
        with self._event_lock:
            clients = tuple(set(self._ws_clients) | set(self._ws_pending))
            senders = tuple(self._ws_senders.values())
            tasks = tuple(self._ws_tasks)
        for client in clients:
            self._remove_ws_client(client)
        for sender in senders:
            if not sender.done():
                sender.cancel()
        closers = tuple(
            asyncio.create_task(self._close_ws_client(client, code=1001))
            for client in clients
        )
        pending = set(tasks) | set(closers)
        if pending:
            _, unfinished = await asyncio.wait(
                pending,
                timeout=WS_SHUTDOWN_TIMEOUT_S,
            )
            for task in unfinished:
                task.cancel()
        self._ws_tasks.clear()


def broadcast_emit(state: AppState):
    def emit(event_type: str, payload: dict[str, Any]) -> None:
        state.publish(event_type, payload)

    return emit


class AppStateHolder:
    """Kompatibilitätszeiger auf die zuletzt aktivierte App-Instanz."""

    def __init__(self) -> None:
        self.state: AppState | None = None
        self._active: list[AppState] = []
        self._lock = threading.RLock()

    def activate(self, state: AppState) -> None:
        with self._lock:
            self._active = [item for item in self._active if item is not state]
            self._active.append(state)
            self.state = state

    def deactivate(self, state: AppState) -> None:
        with self._lock:
            self._active = [item for item in self._active if item is not state]
            self.state = self._active[-1] if self._active else None


STATE = AppStateHolder()


# -- Request-/Response-Modelle ----------------------------------------------


class DatabaseSuggestionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    topics: str = Field(default="", max_length=240, strict=True)
    use_focus: StrictBool = True
    expected_case_ref: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    expected_context_version: int | None = Field(default=None, ge=1, strict=True)
    limit: int = Field(default=8, ge=1, le=8, strict=True)

class DatabaseSuggestionConfirmRequest(DatabaseSuggestionRequest):
    catalogSnapshotDigest: str = Field(pattern=r"^[0-9a-f]{64}$")
    selector: str = Field(min_length=5, max_length=512, strict=True)

class AnalysisRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    database: str
    seed: int | None = None
    mode: str | None = None  # None => Settings-Schluessel entropy.defaultMode
    max_hits: int = 100

    @field_validator("max_hits")
    @classmethod
    def validate_max_hits(cls, value: int) -> int:
        if value not in ALLOWED_MAX_HITS:
            raise ValueError("max_hits muss 100 oder 1000 sein")
        return value


class StickPadFollowupRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_session_id: str
    seed: int | None = None
    mode: str | None = None
    max_hits: int = 100

    @field_validator("max_hits")
    @classmethod
    def validate_max_hits(cls, value: int) -> int:
        if value not in ALLOWED_MAX_HITS:
            raise ValueError("max_hits muss 100 oder 1000 sein")
        return value


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


class BroadcastCaseGuard(BaseModel):
    expected_case_ref: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    expected_context_version: int | None = Field(default=None, strict=True, ge=1)


class PresentationProfileUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    expected_case_ref: str = Field(pattern=r"^[0-9a-f]{64}$")
    expected_context_version: StrictInt = Field(ge=1)
    expected_profile_version: StrictInt = Field(ge=0)
    audio_profile: Literal[
        "original", "off", "fixed-432", "fixed-528",
        "fixed-42962", "solfeggio-9", "pink",
        "pink-pulse-v1", "pink-phi-v1", "pink-fibonacci-v1",
    ]
    stage_seconds: StrictInt = Field(ge=1, le=600)
    repeat: StrictBool
    images: list[StrictStr] = Field(max_length=5)
    modulation_depth_percent: StrictInt | None = Field(default=None, ge=0, le=100)


class BroadcastRequest(BroadcastCaseGuard):
    expected_preview_digest: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    source_personal_job_id: str | None = Field(default=None, pattern=r"^[0-9a-f]{32}$")
    source_personal_input_index: StrictInt | None = Field(default=None, ge=0, lt=4096)
    mode: Literal["seeded", "stochastic"] | None = None
    source_draft_id: str | None = Field(default=None, pattern=r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
    source_session_id: str | None = Field(default=None, pattern=r"^[0-9a-f]{32}$")
    signature: str
    seconds: int = Field(default=60, ge=MIN_BROADCAST_SECONDS, le=MAX_BROADCAST_SECONDS)
    multiplier: int = Field(default=1, ge=MIN_MULTIPLIER, le=MAX_MULTIPLIER)
    clear: bool = False
    delay_ms: int = Field(default=25, ge=MIN_DELAY_MS, le=MAX_DELAY_MS)
    repeat: int = Field(default=1, ge=MIN_REPEAT, le=MAX_REPEAT)


class WatchlistRequest(BroadcastCaseGuard):
    source_session_id: str = Field(pattern=r"^[0-9a-f]{32}$")
    indices: list[StrictInt] = Field(min_length=1, max_length=100)
    mode: Literal["seeded", "stochastic"]
    seed: StrictInt | None = Field(default=None, ge=0)
    expected_preview_digest: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    request_id: str | None = Field(default=None, pattern=r"^[0-9a-f]{32}$")


class ImageBroadcastRequest(BroadcastCaseGuard):
    mode: Literal["seeded", "stochastic"] | None = None
    md5: str
    seconds: int = Field(default=60, ge=MIN_BROADCAST_SECONDS, le=MAX_BROADCAST_SECONDS)
    multiplier: int = Field(default=1, ge=MIN_MULTIPLIER, le=MAX_MULTIPLIER)

    @field_validator("md5")
    @classmethod
    def validate_image_hash(cls, value: str) -> str:
        if len(value) not in (32, 64) or any(c not in "0123456789abcdefABCDEF" for c in value):
            raise ValueError("Bild-Hash muss 32 oder 64 Hex-Zeichen enthalten")
        return value


class BroadcastMixRequest(BaseModel):
    draft_id: str
    max_rates: int = Field(default=8, ge=1, le=105)
    seconds_per_rate: int = Field(default=60, ge=MIN_BROADCAST_SECONDS, le=MAX_BROADCAST_SECONDS)
    multiplier: int = Field(default=1, ge=MIN_MULTIPLIER, le=MAX_MULTIPLIER)


class DraftPromotionRequest(BaseModel):
    max_rates: int = Field(default=8, ge=1, le=105)
    seconds_per_rate: int = Field(default=60, ge=MIN_BROADCAST_SECONDS, le=MAX_BROADCAST_SECONDS)
    multiplier: int = Field(default=1, ge=MIN_MULTIPLIER, le=MAX_MULTIPLIER)


class GvRoundRequest(BaseModel):
    seed: int | None = None
    mode: str | None = None
    expected_draft_id: str | None = None
    expected_counter: int | None = Field(default=None, ge=0)


class GvPageStartRequest(BaseModel):
    page: int = Field(ge=2)
    expected_draft_id: str
    expected_session_id: str


class EssentialRequest(BaseModel):
    seed: int | None = None
    mode: str | None = None


class StickPositionRequest(BaseModel):
    x: int = Field(ge=0, le=100_000)
    y: int = Field(ge=0, le=100_000)
    mode: Literal["reproducible", "original"] = "reproducible"


class StickAnalyzeRequest(BaseModel):
    database: str


class TrainingStartRequest(BaseModel):
    database: str
    seed: int | None = None
    mode: str | None = None


class AutoModeRequest(BroadcastCaseGuard):
    seed: int | None = None
    mode: str | None = None
    database: str
    multiplier: int = Field(default=1, ge=1, le=1000)


class BroadcastFocusRequest(BaseModel):
    case: str | None = None
    intention: str | None = None


class CurrentCaseMetadataRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str | None = None
    description: str | None = None
    intention: str | None = None
    focus: str | None = Field(default=None, max_length=240)
    personalContext: dict[str, Any] | None = None
    personalContextChanges: dict[str, Any] | None = None
    expected_context_version: int | None = Field(default=None, strict=True, ge=1)
    expected_case_ref: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    titleMode: Literal["manual", "context"] | None = None

    @field_validator("personalContext", "personalContextChanges")
    @classmethod
    def validate_personal_context(cls, value):
        normalize_personal(value)
        return value

def _resolve_mode(state: "AppState", request_mode: str | None) -> str:
    """Request-Override oder validierter persistierter Entropie-Modus."""
    try:
        return state.resolve_entropy_mode(request_mode)
    except EntropyConfigurationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


def _live_entropy(state: "AppState") -> EntropyProvider:
    try:
        return state.live()
    except EntropyConfigurationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


def _stochastic_recovery_available(state: "AppState") -> bool:
    try:
        EntropyJournalStore(state.journal_dir)
    except JournalConfigurationError:
        return False
    return True


# -- Router -------------------------------------------------------------------


class ObservationRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    enabled: StrictBool


def build_router(app_state: AppState) -> APIRouter:
    router = APIRouter()

    def selected_rates(name: str) -> list[Rate]:
        try:
            return app_state.rate_repository.find_all_by_source_name(name)
        except CatalogSnapshotError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc

    def selected_script(name: str) -> str | None:
        try:
            return app_state.rate_repository.read_script(name)
        except CatalogSnapshotError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc

    def serialized_case_mutation(handler):
        """Serialisiert Sitzungswechsel und GV mit Stick-Pad-Schreibvorgaengen."""
        @wraps(handler)
        def locked(*args, **kwargs):
            with app_state.stick_pad.transaction_lock():
                try:
                    app_state.recovery.ensure_no_pending()
                except RecoveryError as exc:
                    raise HTTPException(status_code=409, detail=str(exc)) from exc
                return handler(*args, **kwargs)
        return locked

    def capture_broadcast_target(request: BroadcastCaseGuard, source: dict, *, mode: str = "seeded") -> BroadcastTarget:
        """Caller holds the case mutation lock; client supplies no snapshot or target."""
        current = app_state.case_store.current
        reference = app_state.case_store.reference_for_case(current) if current else None
        version = current.get("contextVersion") if current else None
        if (("expected_case_ref" in request.model_fields_set and request.expected_case_ref != reference)
                or ("expected_context_version" in request.model_fields_set and request.expected_context_version != version)):
            raise HTTPException(409, "Fallauswahl oder Kontext wurde geändert. Bitte Fall erneut laden.")
        snapshot = None
        legacy = False
        session_id = getattr(request, "source_session_id", None)
        draft_id = getattr(request, "source_draft_id", None)
        personal_id = getattr(request, "source_personal_job_id", None)
        personal_index = getattr(request, "source_personal_input_index", None)
        if personal_id is None and personal_index is not None:
            raise HTTPException(409,"Persönlicher Ergebnisindex benötigt einen persönlichen Auftrag.")
        requested_mode = getattr(request, "mode", None)
        if requested_mode is not None:mode=requested_mode
        procedure="original-aetherone-v1"
        try:
            if personal_id is not None:
                if draft_id is not None or session_id is not None:
                    raise HTTPException(409,"Persönlicher und Original-Ursprung dürfen nicht vermischt werden.")
                if app_state.personal is None or app_state.personal.store is None:
                    raise HTTPException(503,"Persönlicher Auftragsbeleg ist nicht verfügbar.")
                try:job=app_state.personal.store.get(personal_id)
                except ValueError as exc:raise HTTPException(409,"Persönlicher Analyseauftrag ist nicht sicher belegbar.") from exc
                snapshot=job["input"]["contextSnapshot"]
                if job["status"]!="completed" or current is None or current.get("caseId")!=snapshot["caseId"]:
                    raise HTTPException(409,"Vollständig abgeschlossener persönlicher Auftrag des aktiven Falls fehlt.")
                selected = [row for row in job["rows"] if row["inputIndex"] == personal_index]
                if len(selected) != 1 or selected[0]["rate"] != request.signature:
                    raise HTTPException(409,"Die gewählte Rate gehört nicht zum persönlichen Analyseergebnis.")
                if requested_mode is not None and requested_mode!=job["input"]["mode"]:
                    raise HTTPException(409,"Der persönliche Broadcast übernimmt den Zufallsmodus seiner Analyse.")
                mode=job["input"]["mode"];procedure=job["input"]["procedure"]
                source={**source,"personalJobId":personal_id,"personalInputIndex":personal_index}
            elif draft_id is not None:
                draft = app_state.draft_store.get(draft_id)
                if draft is None or draft.get("status") == "discarded":
                    raise HTTPException(409, "Die Analyseherkunft ist nicht mehr sicher verfügbar.")
                if session_id is not None and draft.get("sessionId") != session_id:
                    raise HTTPException(409, "Sitzung und Draft gehören nicht zur selben Analyse.")
                if requested_mode is None:mode=draft.get("source_entropy_mode","seeded")
                snapshot = draft.get("contextSnapshot")
                legacy = snapshot is None and bool(draft.get("sessionId") or (draft.get("focus") or {}).get("case"))
                source = {**source, "draftId": draft_id}
                if draft.get("sessionId") is not None:
                    source["sessionId"] = draft["sessionId"]
            elif session_id is not None:
                sessions = [item for item in (current or {}).get("sessionList", []) if item.get("sessionId") == session_id]
                if len(sessions) != 1:
                    raise HTTPException(409, "Die ausgewählte Analysesitzung gehört nicht zum aktiven Fall.")
                session = sessions[0]
                if requested_mode is None:mode=(session.get("passport") or {}).get("entropy_mode","seeded")
                snapshot = session.get("contextSnapshot")
                legacy = snapshot is None
                source = {**source, "sessionId": session_id}
                if session.get("draftId") is not None:
                    source["draftId"] = session["draftId"]
            elif current is not None:
                if not current.get("caseId") or not current.get("contextVersion"):
                    current = app_state.case_store.save(copy.deepcopy(current), allow_inherited_context=True)
                snapshot = ContextSnapshot.capture(current, app_state.scope).payload()
            return BroadcastTarget.capture(scope=app_state.scope, source=source, snapshot=snapshot, legacy=legacy, entropy_mode=mode, procedure=procedure)
        except (ContextError, CaseNameError, BroadcastTargetError, ValueError, TypeError) as exc:
            raise HTTPException(409, "Der feste Broadcast-Bezug ist nicht sicher belegbar.") from exc
        except OSError as exc:
            raise HTTPException(503, "Der Analysebeleg ist derzeit nicht lesbar.") from exc

    # 0. Infrastruktur

    def image_store() -> ContextImageStore:
        return ContextImageStore(app_state.case_store.cases_dir, app_state.scope)

    @router.post("/context-images")
    async def upload_context_image(request: Request) -> dict:
        chunks, size = [], 0
        async for part in request.stream():
            size += len(part)
            if size > MAX_UPLOAD_BODY:
                raise HTTPException(status_code=413, detail="Das Fokusbild ist zu groß.")
            chunks.append(part)
        try:
            body = json.loads(b"".join(chunks))
            if type(body) is not dict or set(body) != {"pngBase64"} or type(body["pngBase64"]) is not str:
                raise ContextImageError("Ungültiger Fokusbild-Auftrag.")
            data = base64.b64decode(body["pngBase64"], validate=True)
            return {"image": image_store().put(data)}
        except (ValueError, UnicodeError, binascii.Error, ContextImageError) as exc:
            raise HTTPException(status_code=422, detail="Fokusbild konnte nicht geprüft werden. Bitte neu auswählen.") from exc
        except OSError as exc:
            raise HTTPException(status_code=503, detail="Lokale Fokusbild-Ablage derzeit nicht verfügbar.") from exc

    @router.get("/context-images/{sha}")
    def read_context_image(sha: str) -> Response:
        try:
            data = image_store().get(sha)
        except (OSError, ContextImageError) as exc:
            raise HTTPException(status_code=404, detail="Fokusbild in dieser lokalen Instanz nicht verfügbar.") from exc
        return Response(data, media_type="image/png", headers={
            "Cache-Control":"no-store", "X-Content-Type-Options":"nosniff",
            "Content-Security-Policy":"default-src 'none'; sandbox",
        })

    def presentation_store() -> PresentationProfileStore:
        if app_state.presentation_profiles is None:
            raise HTTPException(status_code=503, detail="Präsentationsprofile sind derzeit nicht verfügbar.")
        return app_state.presentation_profiles

    def bound_presentation_case(reference: str, version: int) -> dict:
        current = app_state.case_store.current
        if (
            not current
            or not current.get("caseId")
            or app_state.case_store.reference_for_case(current) != reference
            or current.get("contextVersion") != version
        ):
            raise HTTPException(status_code=409, detail="Fall oder Kontext wurde geändert. Bitte Fall erneut laden.")
        return current

    def presentation_error(exc: PresentationProfileError) -> HTTPException:
        status = 409 if exc.code in ("profile_conflict", "profile_corrupt", "image_unavailable", "store_unavailable") else 422
        return HTTPException(status_code=status, detail=str(exc))

    @router.get("/presentation-profile")
    @serialized_case_mutation
    def get_presentation_profile(case_ref: str, context_version: int) -> dict:
        case = bound_presentation_case(case_ref, context_version)
        try:
            return {"profile": presentation_store().get(case["caseId"])}
        except PresentationProfileError as exc:
            raise presentation_error(exc) from exc
        except OSError as exc:
            raise HTTPException(status_code=503, detail="Präsentationsprofil konnte nicht sicher geladen werden.") from exc

    @router.put("/presentation-profile")
    @serialized_case_mutation
    def update_presentation_profile(request: PresentationProfileUpdateRequest) -> dict:
        case = bound_presentation_case(request.expected_case_ref, request.expected_context_version)
        has_modulation_depth = "modulation_depth_percent" in request.model_fields_set
        if request.audio_profile in PULSE_PROFILE_IDS:
            if not has_modulation_depth or type(request.modulation_depth_percent) is not int:
                raise HTTPException(status_code=422, detail="Pulsprofile brauchen eine ganzzahlige Modulationstiefe.")
        elif has_modulation_depth:
            raise HTTPException(status_code=422, detail="Dieses Audio-Profil unterstützt keine Modulationstiefe.")
        try:
            profile = presentation_store().update(
                case_id=case["caseId"],
                expected_version=request.expected_profile_version,
                audio_profile=request.audio_profile,
                stage_seconds=request.stage_seconds,
                repeat=request.repeat,
                images=request.images,
                modulation_depth_percent=request.modulation_depth_percent,
            )
            return {"profile": profile}
        except PresentationProfileError as exc:
            raise presentation_error(exc) from exc
        except OSError as exc:
            raise HTTPException(status_code=503, detail="Präsentationsprofil konnte nicht dauerhaft gespeichert werden.") from exc

    @router.post("/presentation-images")
    async def upload_presentation_image(request: Request) -> dict:
        chunks, size = [], 0
        async for part in request.stream():
            size += len(part)
            if size > MAX_UPLOAD_BODY:
                raise HTTPException(status_code=413, detail="Das Präsentationsbild ist zu groß.")
            chunks.append(part)
        try:
            body = json.loads(b"".join(chunks))
            if type(body) is not dict or set(body) != {"pngBase64"} or type(body["pngBase64"]) is not str:
                raise ContextImageError("Ungültiger Präsentationsbild-Auftrag.")
            data = base64.b64decode(body["pngBase64"], validate=True)
            return {"image": presentation_store().put_image(data)}
        except (ValueError, UnicodeError, binascii.Error, ContextImageError) as exc:
            raise HTTPException(status_code=422, detail="Präsentationsbild konnte nicht geprüft werden. Bitte neu auswählen.") from exc
        except OSError as exc:
            raise HTTPException(status_code=503, detail="Lokale Präsentationsbild-Ablage derzeit nicht verfügbar.") from exc

    @router.get("/presentation-images/{sha}")
    def read_presentation_image(sha: str) -> Response:
        try:
            data = presentation_store().get_image(sha)
        except (OSError, ContextImageError) as exc:
            raise HTTPException(status_code=404, detail="Präsentationsbild in dieser lokalen Instanz nicht verfügbar.") from exc
        return Response(data, media_type="image/png", headers={
            "Cache-Control":"no-store", "X-Content-Type-Options":"nosniff",
            "Content-Security-Policy":"default-src 'none'; sandbox",
        })

    @router.get("/ping")
    def ping() -> dict:
        return {
            "result": "pong",
            "module": manifest_module.KERNEL_ID,
            "version": manifest_module.KERNEL_VERSION,
            "supportsStickPadFollowup": True,
        }

    @router.get('/gv-observations')
    def observations_status() -> dict:
        return app_state.observations.snapshot()

    @router.get('/gv-observations/history')
    def observations_history(session_id: str | None = None, case_ref: str | None = None) -> dict:
        import re
        if ((session_id is not None and not re.fullmatch(r'[0-9a-f]{32}', session_id))
                or (case_ref is not None and not re.fullmatch(r'[0-9a-f]{64}', case_ref))):
            raise HTTPException(status_code=422, detail='Ungueltiger Historienfilter')
        try:
            return app_state.observations.history(session_id=session_id, case_ref=case_ref)
        except (ValueError, OSError) as exc:
            raise HTTPException(status_code=409, detail='Beobachtungshistorie kann nicht sicher gelesen werden') from exc

    @router.post('/gv-observations/{broadcast_id}')
    def observations_enable(broadcast_id: str, request: ObservationRequest) -> dict:
        try:
            return app_state.observations.set_enabled(broadcast_id, request.enabled)
        except JournalConfigurationError as exc:
            raise HTTPException(status_code=503, detail='GV-Beobachtung braucht den gesicherten Journalschluessel') from exc
        except (ValueError, OSError) as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc

    @router.get("/manifest")
    def get_manifest() -> dict:
        return manifest_module.manifest()

    @router.get("/entropy/status")
    def entropy_status() -> dict:
        state = app_state
        settings_default = _resolve_mode(state, None)
        provider = state.new_provider(None, settings_default)
        status = provider.status()
        return {
            "defaultMode": settings_default,
            "factoryDefault": "seeded",
            "modes": list(ENTROPY_MODES),
            "activeSource": status.active_source,
            "chain": status.chain,
            "stochasticRecovery": {
                "activeCase": bool(state.case_store.current),
                "requiredForActiveCase": bool(state.case_store.current),
                "available": _stochastic_recovery_available(state),
            },
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
        state = app_state
        values = (body or {}).get("integerList") or []
        accepted = state.entropy_feed.feed(values)
        return {
            "acquired": accepted,
            "feedSize": len(state.entropy_feed),
            "note": "Werte werden als Entropie-Seeds genutzt; keine Bildspeicherung.",
        }

    @router.get("/entropy/feed")
    def entropy_feed_state() -> dict:
        state = app_state
        return {"feedSize": len(state.entropy_feed)}

    # 2. Analyse

    @router.post("/analysis")
    @serialized_case_mutation
    def run_analysis(request: AnalysisRequest, x_client_seed: int | None = Header(default=None)) -> dict:
        state = app_state
        rates = selected_rates(request.database)
        if not rates:
            raise HTTPException(status_code=404, detail=f"Keine Raten fuer '{request.database}'")
        comparison_catalog = None
        if state.case_store.current:
            try:
                comparison_catalog = capture_catalog(state.rate_repository, request.database, rates)
            except (ComparisonBasisError, ValueError, OSError):
                # Unsupported prefix/legacy sources keep the Original path fully usable.
                comparison_catalog = None
        seed = request.seed if request.seed is not None else x_client_seed
        mode = _resolve_mode(state, request.mode)
        journal: EntropyJournal | None = None
        if mode == "stochastic" and state.case_store.current:
            try:
                journal = state.create_entropy_journal()
            except JournalConfigurationError as exc:
                raise HTTPException(
                    status_code=503,
                    detail=(
                        "Fallgebundene stochastic-Recovery ist nicht verfügbar. "
                        "Bitte seeded verwenden oder die Betreiberkonfiguration prüfen."
                    ),
                ) from exc
        entropy = state.new_provider(seed, mode, journal=journal)
        input_payload = {
            "database": request.database,
            "seed": entropy.effective_seed,
            "mode": mode,
            "max_hits": request.max_hits,
        }
        if state.rate_repository.release_id is not None:
            input_payload["catalog"] = catalog_binding(
                request.database, rates, release_id=state.rate_repository.release_id,
            )
        passport = Passport.create(
            kernel=manifest_module.KERNEL_ID,
            kernel_version=manifest_module.KERNEL_VERSION,
            kernel_hash=manifest_module.kernel_hash(),
            input_payload=input_payload,
            entropy=entropy,
            tenant_id=state.scope.tenant_id,
            client_id=state.scope.client_id,
        )
        if state.rate_repository.release_id is not None:
            passport.input_hash_scheme = "analysis-request-catalog-v1"
        started = now_ms()
        state.publish(
            "analysis.progress",
            {"database": request.database, "stage": "started", "runId": passport.run_id},
        )
        with entropy.journal_write_scope():
            result = analyse_rate_list(rates, entropy, max_hits=request.max_hits)
            result.general_vitality = check_general_vitality(entropy)
        result_dict = result.to_dict()
        passport.copyguard_digest = copyguard.digest(
            copyguard.visible_rate_texts(result_dict)
        )
        passport.finish(
            dauer_ms=now_ms() - started,
            sources={"gv": "derived", "energeticValue": "derived", "potency": "derived"},
        )
        entropy.commit_journal()
        # Vektor/Fokus (Frage g): aktiver Fall + Absicht wandern ins Artefakt
        focus: dict[str, Any] = {}
        current_case = state.case_store.current
        if current_case and current_case.get("name"):
            sessions = current_case.get("sessionList") or []
            focus = {
                "case": current_case.get("name"),
                "intention": (sessions[-1].get("intention") if sessions else None),
                "case_focus": current_case.get("focus"),
            }
        draft = state.draft_store.create_from_analysis(
            analysis_dict=result_dict,
            passport=passport.to_dict(),
            database=request.database,
            tenant_id=state.scope.tenant_id,
            client_id=state.scope.client_id,
            focus=focus or None,
            copyguard_digest=passport.copyguard_digest,
            persist=False,
        )
        planned = state.case_store.plan_attach_analysis(
            result_dict,
            passport.to_dict(),
            draft_id=draft["id"],
            entropy_checkpoint=entropy.checkpoint(),
        )
        session = None
        if planned is None:
            state.draft_store.write_planned(draft)
        else:
            case, session = planned
            draft = state.draft_store.plan_link_context_document(draft, session)
            draft = state.draft_store.plan_link_session_document(
                draft,
                session["sessionId"],
                session.get("revision", 0),
            )
            comparison_target = []
            if comparison_catalog is not None:
                try:
                    source = make_source(session, comparison_catalog, state.scope)
                    session["comparisonBasis"] = source_reference(source)
                    comparison_target = [RecoveryTarget("comparisonSource", session["sessionId"] + ".json", None, source)]
                except (ComparisonBasisError, ValueError, KeyError):
                    session["comparisonEligibility"] = "source_not_supported"
            else:
                session["comparisonEligibility"] = "exact_catalog_required"
            try:
                state.recovery.apply(
                    "analysis-session-link",
                    [
                        RecoveryTarget(
                            "draft",
                            state.draft_store.target_key(draft),
                            None,
                            draft,
                        ),
                        RecoveryTarget(
                            "case",
                            state.case_store.current_target_key(case),
                            current_case,
                            case,
                        ),
                    ] + comparison_target,
                )
            except RecoveryError as exc:
                raise HTTPException(
                    status_code=409,
                    detail="Persistenzoperation konnte nicht abgeschlossen werden",
                ) from exc
            state.case_store.apply_planned_case(case)
        state.gv_round = GvRoundState(
            result=result,
            entropy=entropy,
            session_id=session.get("sessionId") if session else None,
            session_index=(len(state.case_store.current.get("sessionList", [])) - 1) if session else None,
            draft_id=draft["id"],
            revision=session.get("revision", 0) if session else 0,
        )
        state.publish(
            "analysis.update",
            {"runId": passport.run_id, "draftId": draft["id"], "result": result_dict},
        )
        return {"passport": passport.to_dict(), "result": result_dict, "draft": _draft_view(draft)}

    @router.get("/analysis/current")
    def current_analysis() -> dict:
        state = app_state
        drafts = state.draft_store.list()
        if not drafts:
            return {"passport": None, "result": None}
        latest = drafts[-1]
        return {"result": latest["payload"], "draft": _draft_view(latest)}

    @router.post("/analysis/stickpad-followup")
    @serialized_case_mutation
    def stickpad_followup(request: StickPadFollowupRequest) -> dict:
        """Neue Analyse nur aus den gespeicherten Treffern einer Stick-Pad-Sitzung."""
        state = app_state
        current_case = state.case_store.current
        if not current_case:
            raise HTTPException(status_code=409, detail="Zuerst einen Fall mit Stick-Pad-Sitzung laden")
        source = next((session for session in current_case.get("sessionList", [])
                       if session.get("sessionId") == request.source_session_id), None)
        if (
            not source
            or (source.get("passport") or {}).get("input_hash_scheme") != "stickpad-position-catalog-v1"
            or (source.get("stickPadCapture") or {}).get("runId") != (source.get("passport") or {}).get("run_id")
        ):
            raise HTTPException(status_code=409, detail="Keine passende Stick-Pad-Quellsitzung im aktiven Fall")
        source_baseline = source.get("analysisBaseline") or {}
        raw_hits = source_baseline.get("rateObjects") or []
        if not 0 < len(raw_hits) <= 5000 or any(
            not isinstance(hit, dict)
            or not isinstance(hit.get("nameOrRate"), str)
            or not hit["nameOrRate"].strip()
            or (hit.get("url") is not None and not isinstance(hit["url"], str))
            for hit in raw_hits
        ):
            raise HTTPException(status_code=409, detail="Stick-Pad-Trefferliste ist nicht verwendbar")
        if copyguard.digest(copyguard.visible_rate_texts(source_baseline)) != source["passport"].get("copyguard_digest"):
            raise HTTPException(status_code=409, detail="Stick-Pad-Quellsitzung hat sich verändert")
        # Die ersten EW sind Provenienz, keine Gewichte der neuen Analyse.
        rates = [Rate(name=hit["nameOrRate"], url=hit.get("url")) for hit in raw_hits]
        mode = _resolve_mode(state, request.mode)
        journal: EntropyJournal | None = None
        if mode == "stochastic":
            try:
                journal = state.create_entropy_journal()
            except JournalConfigurationError as exc:
                raise HTTPException(
                    status_code=503,
                    detail="Fallgebundene stochastic-Recovery ist nicht verfügbar. Bitte seeded verwenden oder die Betreiberkonfiguration prüfen.",
                ) from exc
        entropy = state.new_provider(request.seed, mode, journal=journal)
        input_payload = {
            "scheme": "stickpad-followup-v1",
            "sourceSessionId": request.source_session_id,
            "sourceRunId": source["passport"]["run_id"],
            "sourceReceiptId": source["stickPadCapture"]["id"],
            "sourceHits": raw_hits,
            "seed": entropy.effective_seed,
            "mode": mode,
            "maxHits": request.max_hits,
        }
        passport = Passport.create(
            kernel=manifest_module.KERNEL_ID,
            kernel_version=manifest_module.KERNEL_VERSION,
            kernel_hash=manifest_module.kernel_hash(),
            input_payload=input_payload,
            entropy=entropy,
            modus="stickpad-folgeanalyse",
            tenant_id=state.scope.tenant_id,
            client_id=state.scope.client_id,
        )
        passport.input_hash_scheme = "stickpad-followup-v1"
        started = now_ms()
        result = analyse_rate_list(rates, entropy, max_hits=request.max_hits)
        result.general_vitality = check_general_vitality(entropy)
        result_dict = result.to_dict()
        passport.copyguard_digest = copyguard.digest(copyguard.visible_rate_texts(result_dict))
        passport.finish(
            dauer_ms=now_ms() - started,
            sources={"analysis": "stickpad-result-rates", "gv": "derived", "energeticValue": "derived", "potency": "derived"},
        )
        entropy.commit_journal()
        sessions = current_case.get("sessionList") or []
        focus = {
            "case": current_case.get("name"),
            "intention": sessions[-1].get("intention") if sessions else None,
            "case_focus": current_case.get("focus"),
        }
        draft = state.draft_store.create_from_analysis(
            analysis_dict=result_dict,
            passport=passport.to_dict(),
            database="Stick-Pad-Treffer",
            tenant_id=state.scope.tenant_id,
            client_id=state.scope.client_id,
            focus=focus,
            copyguard_digest=passport.copyguard_digest,
            persist=False,
        )
        planned = state.case_store.plan_attach_analysis(
            result_dict, passport.to_dict(), draft_id=draft["id"],
            entropy_checkpoint=entropy.checkpoint(),
        )
        assert planned is not None
        case, session = planned
        draft = state.draft_store.plan_link_context_document(draft, session)
        session["parentSessionId"] = request.source_session_id
        draft = state.draft_store.plan_link_session_document(draft, session["sessionId"], session["revision"])
        try:
            state.recovery.apply("stickpad-followup-link", [
                RecoveryTarget("draft", state.draft_store.target_key(draft), None, draft),
                RecoveryTarget("case", state.case_store.current_target_key(case), current_case, case),
            ])
        except RecoveryError as exc:
            raise HTTPException(status_code=409, detail="Folgeanalyse konnte nicht vollständig gespeichert werden") from exc
        state.case_store.apply_planned_case(case)
        state.gv_round = GvRoundState(
            result=result,
            entropy=entropy,
            session_id=session["sessionId"],
            session_index=len(case["sessionList"]) - 1,
            draft_id=draft["id"],
            revision=session["revision"],
        )
        state.publish("analysis.update", {"runId": passport.run_id, "draftId": draft["id"], "result": result_dict})
        return {
            "passport": passport.to_dict(), "result": result_dict,
            "draft": _draft_view(draft), "sourceSessionId": request.source_session_id,
            "sessionId": session["sessionId"], "sessionIndex": len(case["sessionList"]) - 1,
        }

    # ---- GV-Runde (FUNKTIONSABGLEICH ①, Aether_4: "GV (runs = n)") ----

    def persist_gv_round(
        round_state: GvRoundState,
        snapshot: dict,
        kind: str,
        extra_targets: list[RecoveryTarget] | None = None,
    ) -> dict:
        state = app_state
        extra_targets = extra_targets or []
        planned_case: dict[str, Any] | None = None
        if round_state.session_id is None and round_state.session_index is not None:
            try:
                planned_case, legacy_session = state.case_store.plan_assign_legacy_session_id(
                    round_state.session_index
                )
            except SessionError as exc:
                raise HTTPException(status_code=409, detail=str(exc)) from exc
            round_state.session_id = legacy_session["sessionId"]
            round_state.revision = legacy_session.get("revision", 0)
        if round_state.session_id is None:
            if extra_targets:
                try:
                    state.recovery.apply("stickpad-gv", extra_targets)
                except RecoveryError as exc:
                    raise HTTPException(
                        status_code=409, detail="Persistenzoperation konnte nicht abgeschlossen werden",
                    ) from exc
            return snapshot
        if round_state.entropy is None:
            raise HTTPException(status_code=409, detail="GV-Entropiestrom fehlt")
        round_state.entropy.commit_journal()
        try:
            case, session = state.case_store.plan_persist_gv_event(
                round_state.session_id,
                round_state.revision,
                snapshot,
                round_state.entropy.checkpoint(),
                kind,
                case=planned_case,
            )
            draft = None
            targets = [
                RecoveryTarget(
                    "case",
                    state.case_store.current_target_key(case),
                    state.case_store.current,
                    case,
                )
            ]
            if round_state.draft_id:
                previous_draft = state.draft_store.get(round_state.draft_id)
                draft = state.draft_store.plan_project_session(
                    round_state.draft_id,
                    snapshot["result"],
                    round_state.session_id,
                    session["revision"],
                )
                if draft["id"] != round_state.draft_id:
                    case = state.case_store.plan_set_session_draft(
                        case,
                        round_state.session_id,
                        draft["id"],
                    )
                    targets[0] = RecoveryTarget(
                        "case",
                        state.case_store.current_target_key(case),
                        state.case_store.current,
                        case,
                    )
                targets.append(
                    RecoveryTarget(
                        "draft",
                        state.draft_store.target_key(draft),
                        previous_draft if draft["id"] == round_state.draft_id else None,
                        draft,
                    )
                )
            targets.extend(extra_targets)
            state.recovery.apply("gv-projection", targets)
            state.case_store.apply_planned_case(case)
            round_state.revision = session["revision"]
            if draft is not None and draft["id"] != round_state.draft_id:
                round_state.draft_id = draft["id"]
            return {
                **snapshot,
                "draftId": round_state.draft_id,
                "sessionId": round_state.session_id,
                "revision": round_state.revision,
            }
        except (SessionError, DraftError, RecoveryError) as exc:
            raise HTTPException(
                status_code=409,
                detail="Persistenzoperation konnte nicht abgeschlossen werden",
            ) from exc

    def fork_gv_round(
        round_state: GvRoundState, *, page_start: int = 0, page_length: int = 21,
    ) -> GvRoundState:
        state = app_state
        if round_state.session_id is None:
            round_state.clean()
            return round_state
        try:
            case, child = state.case_store.plan_fork_session_for_new_round(
                round_state.session_id,
                page_start=page_start,
                page_length=page_length,
                entropy_checkpoint=round_state.entropy.checkpoint() if round_state.entropy else None,
            )
            draft_id = round_state.draft_id
            targets = [
                RecoveryTarget(
                    "case",
                    state.case_store.current_target_key(case),
                    state.case_store.current,
                    case,
                )
            ]
            if draft_id:
                draft = state.draft_store.plan_successor_for_session(
                    draft_id,
                    child["analysisResult"],
                    child["sessionId"],
                    child["revision"],
                )
                case = state.case_store.plan_set_session_draft(
                    case,
                    child["sessionId"],
                    draft["id"],
                )
                targets[0] = RecoveryTarget(
                    "case",
                    state.case_store.current_target_key(case),
                    state.case_store.current,
                    case,
                )
                targets.append(
                    RecoveryTarget(
                        "draft",
                        state.draft_store.target_key(draft),
                        None,
                        draft,
                    )
                )
                draft_id = draft["id"]
            state.recovery.apply("gv-fork-link", targets)
            state.case_store.apply_planned_case(case)
            return GvRoundState(
                result=AnalysisResult.from_dict(child["analysisResult"]),
                entropy=round_state.entropy,
                general_vitality=round_state.general_vitality,
                session_id=child["sessionId"],
                session_index=len(case.get("sessionList", [])) - 1,
                draft_id=draft_id,
                revision=child["revision"],
                page_start=page_start,
                page_length=page_length,
            )
        except (SessionError, DraftError, RecoveryError) as exc:
            raise HTTPException(
                status_code=409,
                detail="Persistenzoperation konnte nicht abgeschlossen werden",
            ) from exc

    @router.post("/analysis/gv-page/start")
    @serialized_case_mutation
    def start_gv_page(request: GvPageStartRequest) -> dict:
        round_state = app_state.gv_round
        if round_state is None or round_state.session_id is None:
            raise HTTPException(status_code=409, detail="Keine gespeicherte Analyse fuer die Seitenpruefung")
        if (round_state.draft_id != request.expected_draft_id
                or round_state.session_id != request.expected_session_id):
            raise HTTPException(status_code=409, detail="Analyse oder Sitzung hat sich geaendert")
        page_start = (request.page - 1) * MAX_ROUND_STEPS
        count = len(round_state.result.rate_objects)
        if page_start >= count:
            raise HTTPException(status_code=422, detail="Ergebnisseite existiert nicht")
        page_length = min(MAX_ROUND_STEPS, count - page_start)
        child = fork_gv_round(round_state, page_start=page_start, page_length=page_length)
        app_state.gv_round = child
        return {**child.snapshot(), "sessionId": child.session_id,
                "sessionIndex": child.session_index, "revision": child.revision}

    @router.post("/analysis/gv-round")
    @serialized_case_mutation
    def gv_round(request: GvRoundRequest) -> dict:
        state = app_state
        if state.gv_round is None:
            raise HTTPException(status_code=409, detail="Keine Analyse im Speicher — erst /analysis ausführen.")
        if request.expected_draft_id is not None or request.expected_counter is not None:
            if (request.expected_draft_id != state.gv_round.draft_id
                    or request.expected_counter != state.gv_round.counter):
                raise HTTPException(status_code=409, detail="GV-Runde gehört nicht mehr zur erwarteten Analyse oder zum erwarteten Schritt")
        if request.seed is not None or request.mode is not None:
            state.gv_round.entropy = state.new_provider(
                request.seed, _resolve_mode(state, request.mode)
            )
        if state.gv_round.at_round_boundary:
            if state.gv_round.page_start != 0:
                raise HTTPException(status_code=409, detail="Seitenpruefung abgeschlossen; neue Seite ausdruecklich starten")
            state.gv_round = fork_gv_round(state.gv_round)
            boundary = persist_gv_round(
                state.gv_round,
                state.gv_round.snapshot(),
                "round-boundary",
            )
            return {**boundary, "roundBoundary": True}
        snapshot = state.gv_round.step()
        return {**persist_gv_round(state.gv_round, snapshot, "step"), "roundBoundary": False}

    @router.post("/analysis/gv-round/reset")
    @serialized_case_mutation
    def gv_round_reset() -> dict:
        state = app_state
        if state.gv_round is None:
            raise HTTPException(status_code=409, detail="Keine Analyse im Speicher.")
        state.gv_round.clean()
        snapshot = state.gv_round.snapshot()
        persisted = persist_gv_round(state.gv_round, snapshot, "reset")
        return {"state": state.gv_round.state_dict(), "result": state.gv_round.result.to_dict(), **persisted}

    @router.get("/analysis/gv-round")
    def gv_round_state() -> dict:
        state = app_state
        if state.gv_round is None:
            return {"active": False}
        return {
            "active": True,
            "draftId": state.gv_round.draft_id,
            "sessionId": state.gv_round.session_id,
            "supportsBoundSuccessor": True,
            **state.gv_round.state_dict(),
        }

    # ---- Essenzielle Fragen (FUNKTIONSABGLEICH ②) ----

    @router.post("/essential-questions")
    def essential_questions(request: EssentialRequest) -> dict:
        state = app_state
        entropy = state.new_provider(request.seed, _resolve_mode(state, request.mode))
        return {"report": ask_essential_questions(entropy)}

    # ---- Settings (FUNKTIONSABGLEICH ③, Aether_3) ----

    # Kanonische Schalter des Originals (Aether_3-Aufnahme) + Kernel-Festlegungen;
    # Selbst-Default wie im Original: erster Zugriff persistiert den Default.
    CANONICAL_BOOLEANS: dict[str, bool] = {
        "broadcast.localCompletionNotice": False,
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
        state = app_state
        settings = state.settings_store.load("Settings")
        return settings.to_dict(
            default_booleans=CANONICAL_BOOLEANS,
            default_strings={"entropy.defaultMode": "seeded"},
            default_integers={"broadcast.adjustment.maxFollowups": 1, "broadcast.adjustment.minSeconds": 10},
        )

    @router.put("/settings")
    @serialized_case_mutation
    def put_settings(body: dict) -> dict:
        state = app_state
        settings = state.settings_store.load("Settings")
        try:
            settings.update(body)
        except ValueError as exc:
            raise HTTPException(422, str(exc)) from exc
        except OSError as exc:
            raise HTTPException(503, "Einstellungen konnten nicht dauerhaft gespeichert werden.") from exc
        return settings.to_dict()

    # ---- Fall-Statistik (FUNKTIONSABGLEICH ⑥, StatisticsGenerator) ----

    @router.get("/cases/{name}/statistics")
    def case_statistics_endpoint(name: str) -> dict:
        state = app_state
        try:
            case = state.case_store.load(
                name,
                record_recent=False,
                activate=False,
            )
        except CaseNameError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        if case is None:
            raise HTTPException(status_code=404, detail=f"Case '{name}' nicht gefunden")
        top = case_statistics(dict(case))
        return {"case": name, "sessions": len(case.get("sessionList", [])), "topList": top}

    # ---- Bildschichten (FUNKTIONSABGLEICH ⑦, Aether_5) ----

    @router.post("/images/analyze")
    def images_analyze(body: dict) -> dict:
        """`{"count": n}` — GV je Schicht (Original: 256 Züge, Runden bis
        max >= 162). Bilder selbst bleiben im Browser; nur die Anzahl wird
        analysiert — MD5/Zeugen pflegt der Client (Passport-`input_hash`)."""
        state = app_state
        count = int(body.get("count", 0))
        if count < 1 or count > 50:
            raise HTTPException(status_code=422, detail="count muss 1..50 sein")
        entropy = state.new_provider(body.get("seed"), _resolve_mode(state, body.get("mode")))
        return analyze_layers(count, entropy)

    @router.post("/images/broadcast")
    @serialized_case_mutation
    def images_broadcast(request: ImageBroadcastRequest) -> dict:
        state = app_state
        md5 = request.md5.strip()
        if not md5:
            raise HTTPException(status_code=422, detail="md5 fehlt")
        try:
            return state.broadcast.enqueue(
                f"IMAGE:{md5}",
                request.seconds,
                request.multiplier,
                target=capture_broadcast_target(request, {"kind": "image", "imageHash": md5.lower()}),
            )
        except BroadcastError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        except OSError as exc:
            raise HTTPException(503, "Broadcast-Auftrag konnte nicht dauerhaft angenommen werden.") from exc

    # ---- RadionicScript / PEGGOTTY (FUNKTIONSABGLEICH ⑨) ----

    @router.post("/script/execute")
    def script_execute(body: dict) -> dict:
        state = app_state
        lines: list[str]
        if body.get("name"):
            content = selected_script(str(body["name"]))
            if content is None:
                raise HTTPException(status_code=404, detail=f"Skript '{body['name']}' nicht gefunden")
            lines = content.splitlines()
        elif body.get("script"):
            lines = str(body["script"]).splitlines()
        else:
            raise HTTPException(status_code=422, detail="script (Text) oder name erforderlich")
        entropy = state.new_provider(body.get("seed"), _resolve_mode(state, body.get("mode")))
        try:
            result = execute_script(
                lines,
                find_rates=selected_rates,
                entropy=entropy,
            )
        except DuplicateScriptLabelError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        return result.to_dict()

    @router.get("/scripts")
    def list_scripts() -> dict:
        state = app_state
        return {"scripts": state.rate_repository.script_names()}

    @router.get("/scripts/{name}")
    def read_script(name: str) -> dict:
        content = selected_script(name)
        if content is None:
            raise HTTPException(status_code=404, detail=f"Skript '{name}' nicht gefunden")
        return {"name": name, "content": content}

    # ---- Trainings-Modus (Aether_4: TRAINING[START]/[UNCOVER]) ----

    @router.post("/training/start")
    def training_start(request: TrainingStartRequest) -> dict:
        """Event-Handler.trainingSelectSignatureFromCurrentDatabase: verdeckte
        Signatur aus der gewählten Datenbank ziehen."""
        state = app_state
        rates = selected_rates(request.database)
        if not rates:
            raise HTTPException(status_code=404, detail=f"Keine Raten fuer '{request.database}'")
        entropy = state.new_provider(request.seed, _resolve_mode(state, request.mode))
        state.training_signature = select_training_rate(rates, entropy)
        return {"active": True, "covered": True}

    @router.post("/training/uncover")
    def training_uncover() -> dict:
        """TRAINING[UNCOVER]: lüftet die Signatur (Original: print + UI)."""
        state = app_state
        if state.training_signature is None:
            raise HTTPException(status_code=409, detail="Kein Training aktiv — erst TRAINING[START].")
        return {"active": True, "covered": False, "signature": state.training_signature}

    @router.get("/training")
    def training_state() -> dict:
        state = app_state
        return {"active": state.training_signature is not None}

    @router.delete("/training")
    def training_stop() -> dict:
        state = app_state
        state.training_signature = None
        return {"active": False}

    # ---- Auto-Modus (Aether_4: AUTO MODE ON/OFF = Harmonisierungsregler) ----

    @router.post("/auto-mode/on")
    @serialized_case_mutation
    def auto_mode_on(request: AutoModeRequest) -> dict:
        """Original handleAutoMode: bei leerer Queue und GV <= 300 analysiert
        der Regelkreis selbstständig und sendet eine Rate 10-1000 s
        (Hotbits-Wurf, UI-Multiplikator). Server ist die Uhr."""
        state = app_state
        rates = selected_rates(request.database)
        if not rates:
            raise HTTPException(status_code=404, detail=f"Keine Raten fuer '{request.database}'")
        assert state.auto is not None
        mode = _resolve_mode(state, request.mode)
        target = capture_broadcast_target(request, {"kind": "auto", "generationId": uuid.uuid4().hex}, mode=mode)
        try:
            journal = state.create_entropy_journal() if mode == "stochastic" else None
            provider = state.new_provider(request.seed if request.seed is not None else int(time.time()), mode, journal=journal)
            snapshot = state.auto.start(request.database, request.multiplier, target_template=target, entropy_provider=provider, rates_snapshot=rates)
            try:
                state.broadcast.ensure_running()
            except Exception:
                state.auto.stop()
                raise
            return snapshot  # Preserve the established Auto REST response; provenance is stored separately.
        except (JournalConfigurationError, OSError) as exc:
            raise HTTPException(503, "Auto-Auftrag braucht eine dauerhaft gesicherte Zufallsquelle und Annahme.") from exc

    @router.post("/auto-mode/off")
    def auto_mode_off() -> dict:
        state = app_state
        assert state.auto is not None
        return state.auto.stop()

    @router.get("/auto-mode")
    def auto_mode_state() -> dict:
        state = app_state
        assert state.auto is not None
        return state.auto.snapshot()

    # ---- Stick-Pad (FUNKTIONSABGLEICH ④, Aether_6) ----

    @router.get("/stickpad")
    def stickpad_status() -> dict:
        state = app_state
        status = state.stick_pad.status()
        receipt = status["lastReceipt"]
        if receipt is None:
            status["catalogCheck"] = {"state": "none"}
        elif receipt["kind"] != "analysis":
            status["catalogCheck"] = {"state": "not_applicable"}
        elif "catalog" not in receipt:
            status["catalogCheck"] = {"state": "unverified_legacy"}
        else:
            binding = receipt["catalog"]
            try:
                rates = state.rate_repository.find_all_fresh_by_source_name(binding["selector"])
            except CatalogSnapshotError:
                status["catalogCheck"] = {"state": "unavailable"}
                return status
            if not rates:
                status["catalogCheck"] = {"state": "unavailable"}
            else:
                current = catalog_binding(binding["selector"], rates, release_id=state.rate_repository.release_id)
                status["catalogCheck"] = {
                    "state": "current" if current["digest"] == binding["digest"] and current.get("releaseId") == binding.get("releaseId") else "changed",
                    "currentDigest": current["digest"],
                    "currentRateCount": current["rateCount"],
                }
        return status

    @router.post("/stickpad/position")
    def stickpad_position(request: StickPositionRequest) -> dict:
        state = app_state
        with state.stick_pad.transaction_lock():
            try:
                state.recovery.ensure_no_pending()
                capture = state.stick_pad.record_position(request.x, request.y, mode=request.mode)
            except (ValueError, RecoveryError) as exc:
                raise HTTPException(status_code=409, detail=str(exc)) from exc
        return capture

    @router.post("/stickpad/analyze")
    def stickpad_analyze(request: StickAnalyzeRequest) -> dict:
        state = app_state
        with state.stick_pad.transaction_lock():
            try:
                state.recovery.ensure_no_pending()
                rates = state.rate_repository.find_all_fresh_by_source_name(request.database)
            except (CatalogSnapshotError, RecoveryError) as exc:
                raise HTTPException(status_code=409, detail=str(exc)) from exc
            if not rates:
                raise HTTPException(status_code=404, detail=f"Keine Raten fuer '{request.database}'")
            try:
                if not state.stick_pad.positions:
                    raise ValueError("Keine Stick-Pad-Positionen gesammelt.")
                binding = catalog_binding(request.database, rates, release_id=state.rate_repository.release_id)
                input_payload = {
                    "algorithm": "stickpad-position-catalog-v1",
                    "positions": state.stick_pad.status()["positions"],
                    "catalog": binding,
                }
                encoded = json.dumps(
                    input_payload, ensure_ascii=False, sort_keys=True,
                    separators=(",", ":"),
                ).encode("utf-8")
                seed = int.from_bytes(hashlib.sha256(encoded).digest()[:8], "big")
                entropy = state.new_provider(seed, "seeded")
                passport = Passport.create(
                    kernel=manifest_module.KERNEL_ID,
                    kernel_version=manifest_module.KERNEL_VERSION,
                    kernel_hash=manifest_module.kernel_hash(),
                    input_payload=input_payload,
                    entropy=entropy,
                    modus="stickpad-analyse",
                    tenant_id=state.scope.tenant_id,
                    client_id=state.scope.client_id,
                )
                passport.input_hash_scheme = "stickpad-position-catalog-v1"
                passport.seed_scheme = "stickpad-gv-continuation-v1"
                # Der historische Gesamtkatalog ist nicht archiviert; Replay wird nicht behauptet.
                passport.replayable = False
                started = now_ms()
                result, receipt, before, after = state.stick_pad.plan_analysis_with_capture(
                    rates, selector=request.database, run_id=passport.run_id,
                    release_id=state.rate_repository.release_id,
                )
                result_dict = result.to_dict()
                passport.copyguard_digest = copyguard.digest(
                    copyguard.visible_rate_texts(result_dict)
                )
                passport.finish(
                    dauer_ms=now_ms() - started,
                    sources={
                        "analysis": "stickpad-positions",
                        "energeticValue": "stickpad-positions",
                        "gv": "not_measured",
                        "continuationEntropy": "seeded-from-stickpad-input",
                    },
                )
                current_case = state.case_store.current
                focus: dict[str, Any] = {}
                if current_case and current_case.get("name"):
                    sessions = current_case.get("sessionList") or []
                    focus = {
                        "case": current_case["name"],
                        "intention": sessions[-1].get("intention") if sessions else None,
                        "case_focus": current_case.get("focus"),
                    }
                draft = state.draft_store.create_from_analysis(
                    analysis_dict=result_dict,
                    passport=passport.to_dict(),
                    database=request.database,
                    tenant_id=state.scope.tenant_id,
                    client_id=state.scope.client_id,
                    focus=focus or None,
                    copyguard_digest=passport.copyguard_digest,
                    persist=False,
                )
                planned = state.case_store.plan_attach_analysis(
                    result_dict, passport.to_dict(), draft_id=draft["id"],
                    entropy_checkpoint=entropy.checkpoint(),
                )
                targets = [RecoveryTarget(
                    "draft", state.draft_store.target_key(draft), None, draft,
                )]
                session = None
                if planned is not None:
                    case, session = planned
                    session["stickPadReceiptId"] = receipt["id"]
                    session["stickPadCapture"] = receipt
                    draft = state.draft_store.plan_link_context_document(draft, session)
                    draft = state.draft_store.plan_link_session_document(
                        draft, session["sessionId"], session["revision"],
                    )
                    targets[0] = RecoveryTarget(
                        "draft", state.draft_store.target_key(draft), None, draft,
                    )
                    targets.append(RecoveryTarget(
                        "case", state.case_store.current_target_key(case),
                        current_case, case,
                    ))
                targets.append(RecoveryTarget("stickpad", "state.json", before, after))
                state.recovery.apply("stickpad-analysis-link", targets)
                state.stick_pad.apply_persisted_document(after)
                if planned is not None:
                    state.case_store.apply_planned_case(case)
                state.gv_round = GvRoundState(
                    result=result,
                    entropy=entropy,
                    session_id=session["sessionId"] if session else None,
                    session_index=(len(case["sessionList"]) - 1) if session else None,
                    draft_id=draft["id"],
                    revision=session["revision"] if session else 0,
                ) if session else None
            except ValueError as exc:
                raise HTTPException(status_code=409, detail=str(exc)) from exc
            except RecoveryError as exc:
                try:
                    state.recovery.ensure_no_pending()
                except RecoveryError:
                    # Ein angefangener Mehrdatei-Schreibvorgang verlangt Neustart.
                    state.gv_round = None
                raise HTTPException(
                    status_code=409,
                    detail="Stick-Pad-Analyse konnte nicht vollständig gespeichert werden",
                ) from exc
        state.publish(
            "analysis.update",
            {"runId": passport.run_id, "draftId": draft["id"], "result": result_dict},
        )
        return {
            **result_dict, "result": result_dict, "passport": passport.to_dict(),
            "draft": _draft_view(draft), "stickPadCapture": receipt,
            "sessionLinked": session is not None,
            "sessionId": session["sessionId"] if session else None,
            "sessionIndex": (len(case["sessionList"]) - 1) if session else None,
        }

    @router.post("/stickpad/gv")
    def stickpad_gv() -> dict:
        state = app_state
        with state.stick_pad.transaction_lock():
            try:
                state.recovery.ensure_no_pending()
            except RecoveryError as exc:
                raise HTTPException(status_code=409, detail=str(exc)) from exc
            if not state.stick_pad.positions:
                return {"gv": None, "positions": 0, "stickPadCapture": None, "coupled": False}
            round_state = state.gv_round
            if round_state is None:
                if state.case_store.current:
                    raise HTTPException(status_code=409, detail="Aktiver Fall braucht eine geladene Analyse")
                gv, receipt = state.stick_pad.check_general_vitality_with_capture()
                return {"gv": gv, "positions": 0, "stickPadCapture": receipt, "coupled": False}
            if state.case_store.current and round_state.session_id is None:
                raise HTTPException(status_code=409, detail="Analyse ist nicht mit dem aktiven Fall verbunden")
            if round_state.at_round_boundary:
                state.gv_round = fork_gv_round(round_state)
                boundary = persist_gv_round(state.gv_round, state.gv_round.snapshot(), "round-boundary")
                return {
                    **boundary, "roundBoundary": True, "coupled": True,
                    "positions": len(state.stick_pad.positions), "stickPadCapture": None,
                }
            planned = state.stick_pad.plan_general_vitality_with_capture()
            assert planned is not None
            gv, receipt, before, after = planned
            candidate = round_state.clone()
            snapshot = candidate.record_measured_gv(gv)
            snapshot["stickPadReceiptId"] = receipt["id"]
            persisted = persist_gv_round(
                candidate, snapshot, "stickpad-step",
                [RecoveryTarget("stickpad", "state.json", before, after)],
            )
            state.stick_pad.apply_persisted_document(after)
            state.gv_round = candidate
            return {
                **persisted, "roundBoundary": False, "coupled": True,
                "positions": 0, "stickPadCapture": receipt,
            }

    @router.delete("/stickpad")
    def stickpad_clear() -> dict:
        state = app_state
        with state.stick_pad.transaction_lock():
            try:
                state.recovery.ensure_no_pending()
            except RecoveryError as exc:
                raise HTTPException(status_code=409, detail=str(exc)) from exc
            cleared = state.stick_pad.clear()
        return {"cleared": cleared}

    # Original-Alias
    @router.get("/analysis")
    def analysis_alias() -> dict:
        return current_analysis()

    @router.post("/gv")
    def general_vitality(request: GvRequest) -> dict:
        state = app_state
        # Ohne seed: Laufzeit-Strom (jeder Aufruf anders); mit seed: fest.
        entropy = (
            state.new_provider(request.seed, _resolve_mode(state, request.mode))
            if request.seed is not None or request.mode is not None
            else _live_entropy(state)
        )
        return {"gv": check_general_vitality(entropy), "source": "derived"}

    @router.post("/search-anomaly")
    def anomaly(request: AnomalyRequest) -> dict:
        state = app_state
        entropy = (
            state.new_provider(request.seed, _resolve_mode(state, request.mode))
            if request.seed is not None or request.mode is not None
            else _live_entropy(state)
        )
        matrix = search_anomaly(request.width, request.height, entropy)
        return {"width": request.width, "height": request.height, "values": matrix}

    # 1. Entropie-Alias lt. Contract

    @router.get("/databases")
    def databases() -> dict:
        state = app_state
        return {"databases": state.rate_repository.database_names()}

    @router.get("/catalogs")
    def catalogs() -> dict:
        state = app_state
        return {
            "catalogs": state.rate_repository.catalog_entries(),
            "releaseId": state.rate_repository.release_id,
        }

    async def parse_suggestion_request(request, model):
        parts, size = [], 0
        async for chunk in request.stream():
            size += len(chunk)
            if size > 4096:
                raise HTTPException(status_code=413, detail="Suchauftrag überschreitet die lokale Grenze.")
            parts.append(chunk)
        try:
            body = json.loads(b"".join(parts))
            if type(body) is not dict:
                raise ValueError("shape")
            return model.model_validate(body)
        except (ValueError, UnicodeError) as exc:
            raise HTTPException(status_code=422, detail="Ungültiger Suchauftrag. Bitte Eingaben und Anzahl der Begriffe prüfen.") from exc

    def suggestion_context():
        with app_state.stick_pad.transaction_lock():
            current = app_state.case_store.current or {}
            return (
                app_state.case_store.reference_for_case(current) if current.get("name") else None,
                current.get("contextVersion"),
                current.get("focus") if isinstance(current.get("focus"), str) else "",
            )

    def compute_suggestions(body):
        context = suggestion_context()
        reference, version, focus = context
        if (body.expected_case_ref != reference or body.expected_context_version != version):
            raise HTTPException(status_code=409, detail="Fallkontext ist nicht mehr aktuell. Bitte Fall neu laden.")
        try:
            terms = query_terms(focus if body.use_focus else "", body.topics)
            documents, digest = catalog_snapshot(app_state.rate_repository)
            ranked = rank_catalog(documents, terms, body.limit)
            catalogs_by_name = {
                entry["name"]: entry for entry in app_state.rate_repository.catalog_entries()
            }
            suggestions = []
            for suggestion in ranked["suggestions"]:
                entry = catalogs_by_name.get(suggestion["name"])
                if entry is None:
                    raise HTTPException(status_code=409, detail="Katalog seit dem Vorschlag verändert.")
                suggestions.append({
                    **suggestion,
                    "catalogId": entry["id"],
                    "exactId": entry["exactId"],
                    "selector": entry["exactId"],
                })
            ranked = {**ranked, "suggestions": suggestions}
        except CatalogSearchBoundsError as exc:
            raise HTTPException(status_code=413, detail="Katalog überschreitet die Grenze der Inhaltsuche; Namenssuche bleibt verfügbar.") from exc
        except CatalogSearchDrift as exc:
            raise HTTPException(status_code=409, detail="Katalog ist verändert oder nicht sicher lesbar. Bitte Datenbankindex prüfen und Vorschläge neu anfordern.") from exc
        except OSError as exc:
            raise HTTPException(status_code=503, detail="Katalog derzeit nicht vollständig erreichbar; Namenssuche bleibt verfügbar.") from exc
        except ValueError as exc:
            raise HTTPException(status_code=422, detail="Suchbegriffe nicht nutzbar. Bitte bis zwölf passende Wörter verwenden.") from exc
        if suggestion_context() != context:
            raise HTTPException(status_code=409, detail="Fallkontext während der Suche verändert. Bitte Vorschläge neu anfordern.")
        return {"ruleVersion": RULE_VERSION, "queryTerms": terms, "catalogSnapshotDigest": digest,
                "caseRef": reference, "contextVersion": version,
                "catalogWarnings": {"utf8ReplacementFiles": sum(bool(v.get("encodingReplacement")) for v in documents)}, **ranked}

    @router.post("/database-suggestions")
    async def database_suggestions(request: Request) -> dict:
        body = await parse_suggestion_request(request, DatabaseSuggestionRequest)
        return await asyncio.to_thread(compute_suggestions, body)

    @router.post("/database-suggestions/confirm")
    async def confirm_database_suggestion(request: Request) -> dict:
        body = await parse_suggestion_request(request, DatabaseSuggestionConfirmRequest)
        result = await asyncio.to_thread(compute_suggestions, body)
        if result["catalogSnapshotDigest"] != body.catalogSnapshotDigest:
            raise HTTPException(status_code=409, detail="Katalog seit dem Vorschlag verändert. Bitte Vorschläge neu anfordern.")
        exact_id = app_state.rate_repository.exact_id_for_selector(body.selector)
        selected = next(
            (v for v in result["suggestions"] if v["exactId"] == exact_id), None
        )
        if selected is None:
            raise HTTPException(status_code=409, detail="Auswahl passt nicht zum aktuellen Vorschlag.")
        # Read-only confirmation is a point-in-time check, never an analysis lease.
        return {
            "selector": selected["exactId"],
            "exactId": selected["exactId"],
            "catalogId": selected["catalogId"],
            "name": selected["name"],
            "catalogSnapshotDigest": result["catalogSnapshotDigest"],
            "ruleVersion": RULE_VERSION,
        }

    # Original-Alias
    @router.get("/rates")
    def rates_alias() -> dict:
        return databases()

    # 3. Session / Case

    @router.get("/cases")
    def cases() -> dict:
        state = app_state
        raw_entries = state.case_store.list_entries()
        legacy = [
            copyguard.PUBLIC_REDACTION if copyguard.check_text(entry["name"])[0] == "block"
            else entry["legacy_name"] for entry in raw_entries
        ]
        entries = [{"name": entry["name"], "ref": entry["ref"]} for entry in raw_entries]
        return {"cases": legacy, "entries": entries}

    @router.post("/cases")
    @serialized_case_mutation
    def save_case(case: dict, response: Response) -> dict:
        state = app_state
        if copyguard.contains_public_redaction(case):
            raise HTTPException(
                status_code=409,
                detail="Geschwärzte Falldaten dürfen nicht vollständig gespeichert werden.",
            )
        mode = case.get("titleMode", "manual")
        if mode not in ("manual", "context"):
            raise HTTPException(status_code=422, detail="Titelmodus muss manual oder context sein.")

        if set(case) <= {"name", "description"} and isinstance(case.get("name"), str):
            try:
                existing = state.case_store.load(case["name"], record_recent=False, activate=False)
            except CaseNameError as exc:
                code = 409 if "nicht eindeutig" in str(exc) else 422
                raise HTTPException(status_code=code, detail=str(exc)) from exc
            if existing is not None:
                if existing.get("titleMode", "manual") != "manual" or existing.get("name") != case["name"]:
                    raise HTTPException(status_code=409, detail="Nur ein gleichnamiger manueller Legacy-Fall erlaubt diese Metadatenänderung.")
                description = case.get("description")
                if description is not None and not isinstance(description, str):
                    raise HTTPException(status_code=422, detail="Beschreibung muss Text sein.")
                if isinstance(description, str) and copyguard.check_text(description)[0] == "block":
                    raise HTTPException(status_code=409, detail="CopyGuard sperrt die Beschreibung.")
                document = copy.deepcopy(existing)
                if "description" in case:
                    document["description"] = description
                try:
                    saved = state.case_store.save(document, allow_rename=True, origin_reference=state.case_store.reference_for_case(existing))
                    response.headers["X-RadiWorks-Case-Ref"] = state.case_store.reference_for_case(saved)
                    return saved
                except SessionError as exc:
                    raise HTTPException(status_code=409, detail=str(exc)) from exc
                except CaseNameError as exc:
                    raise HTTPException(status_code=422, detail=str(exc)) from exc

        if any(field in case for field in ("caseId", "contextVersion", "personalContextOriginal")):
            clone_allowed = False
            incoming_name = case.get("name")
            incoming_id = case.get("caseId")
            owner = state.case_store.find_identity(incoming_id) if isinstance(incoming_id, str) else None
            if (
                mode == "manual"
                and owner is not None
                and owner[1].get("titleMode", "manual") == "manual"
                and isinstance(incoming_name, str)
                and incoming_name != owner[1].get("name")
            ):
                destination = state.case_store._direct_case_path(incoming_name)
                expected = copy.deepcopy(owner[1])
                expected["name"] = incoming_name
                clone_allowed = (
                    destination is not None
                    and not destination.exists()
                    and case == expected
                )
            if not clone_allowed:
                raise HTTPException(status_code=422, detail="Fallidentität und vollständige Falländerungen sind nur über gebundene Metadaten zulässig.")
        elif mode == "manual" and case.get("name"):
            try:
                existing = state.case_store.load(case["name"], record_recent=False, activate=False)
            except CaseNameError as exc:
                code = 409 if "nicht eindeutig" in str(exc) else 422
                raise HTTPException(status_code=code, detail=str(exc)) from exc
            if existing is not None:
                personal=case.get("personalContext")
                if isinstance(personal,dict) and "placeKind" in personal and "place" not in personal and personal["placeKind"]!=(existing.get("personalContext") or {}).get("placeKind"):
                    raise HTTPException(status_code=422, detail="Bei einem Ortstypwechsel muss der Ort ausdrücklich neu angegeben werden.")
                raise HTTPException(status_code=409, detail="Ein bestehender Fall kann hier nicht vollständig überschrieben werden.")

        if "personalContext" in case:
            try:
                normalize_personal(case["personalContext"])
            except ContextError as exc:
                raise HTTPException(status_code=422, detail=str(exc)) from exc
            if copyguard.contains_public_redaction(case["personalContext"]):
                raise HTTPException(status_code=409, detail="Geschwärzter Kontext darf nicht gespeichert werden.")
            if copyguard.check_strings([v for v in (case["personalContext"] or {}).values() if isinstance(v, str)])[0] == "block":
                raise HTTPException(status_code=409, detail="CopyGuard sperrt den persönlichen Kontext.")
        focus = case.get("focus")
        if focus is not None:
            if not isinstance(focus, str) or len(focus) > 240:
                raise HTTPException(status_code=422, detail="Fokus muss Text mit höchstens 240 Zeichen sein.")
            if copyguard.check_text(focus)[0] == "block":
                raise HTTPException(status_code=409, detail="CopyGuard sperrt den Fokus.")
            case["focus"] = focus.strip() or None
        try:
            saved = state.case_store.save(case)
            response.headers["X-RadiWorks-Case-Ref"] = state.case_store.reference_for_case(saved)
            return saved
        except SessionError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        except CaseNameError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
    @router.post("/cases/current/metadata")
    @serialized_case_mutation
    def save_current_case_metadata(body: CurrentCaseMetadataRequest, response: Response) -> dict:
        current = app_state.case_store.current
        if current is None:
            raise HTTPException(status_code=409, detail="Kein aktiver Fall vorhanden.")
        current_ref = app_state.case_store.reference_for_case(current)
        current_mode = current.get("titleMode", "manual")
        if body.expected_case_ref is not None and body.expected_case_ref != current_ref:
            raise HTTPException(status_code=409, detail="Aktiver Fall hat sich geändert. Bitte Fall neu laden.")
        if body.expected_context_version is not None and body.expected_context_version != current.get("contextVersion"):
            raise HTTPException(status_code=409, detail="Fallkontext wurde geändert. Bitte Fall neu laden.")
        if current_mode == "context" or body.titleMode is not None:
            if body.expected_case_ref is None or (current.get("contextVersion") and body.expected_context_version is None):
                raise HTTPException(status_code=409, detail="Fallbindung und Kontextversion fehlen. Bitte Fall neu laden.")

        document = copy.deepcopy(current)
        if {"personalContext", "personalContextChanges"} <= body.model_fields_set:
            raise HTTPException(status_code=422, detail="Persönlichen Kontext entweder ändern oder vollständig ersetzen.")
        if "personalContextChanges" in body.model_fields_set:
            if body.expected_case_ref is None or (current.get("contextVersion") and body.expected_context_version is None):
                raise HTTPException(status_code=409, detail="Fallbindung und Kontextversion fehlen. Bitte Fall neu laden.")
            changes = body.personalContextChanges or {}
            old_kind = (current.get("personalContext") or {}).get("placeKind")
            if ("placeKind" in changes and changes["placeKind"] != old_kind
                    and "place" not in changes):
                raise HTTPException(status_code=409, detail="Beim Wechsel des Ortstyps den Ort ausdrücklich neu angeben oder leeren.")
            if copyguard.contains_public_redaction(changes) or copyguard.check_strings([v for v in changes.values() if isinstance(v, str)])[0] == "block":
                raise HTTPException(status_code=409, detail="CopyGuard sperrt den persönlichen Kontext.")
            raw = copy.deepcopy(current.get("personalContextOriginal") or current.get("personalContext") or {})
            raw.update(changes)
            document["personalContext"] = raw
            document.pop("personalContextOriginal", None)
        if "personalContext" in body.model_fields_set:
            raw = body.personalContext or {}
            if copyguard.contains_public_redaction(raw) or copyguard.check_strings([v for v in raw.values() if isinstance(v, str)])[0] == "block":
                raise HTTPException(status_code=409, detail="CopyGuard sperrt den persönlichen Kontext.")
            document["personalContext"] = raw
            document.pop("personalContextOriginal", None)

        if "titleMode" in body.model_fields_set:
            document["titleMode"] = body.titleMode
        effective_mode = body.titleMode or current_mode
        for field in ("name", "description", "intention", "focus"):
            if field not in body.model_fields_set:
                continue
            value = getattr(body, field)
            if value == copyguard.PUBLIC_REDACTION:
                continue
            if isinstance(value, str) and copyguard.check_text(value)[0] == "block":
                raise HTTPException(status_code=409, detail="CopyGuard sperrt die Metadaten.")
            if field == "name":
                if effective_mode == "context":
                    continue
                if not isinstance(value, str) or not value.strip():
                    raise HTTPException(status_code=422, detail="Fallname darf nicht leer sein.")
                document["name"] = value.strip()
            elif field == "description":
                document["description"] = value
            elif field == "focus":
                document["focus"] = value.strip() or None if isinstance(value, str) else None
            else:
                sessions = document.get("sessionList") or []
                if not sessions:
                    raise HTTPException(status_code=409, detail="Keine Sitzung für eine Absicht vorhanden.")
                sessions[-1]["intention"] = value
        try:
            saved = app_state.case_store.save(document, allow_rename=True, origin_reference=current_ref)
            response.headers["X-RadiWorks-Case-Ref"] = app_state.case_store.reference_for_case(saved)
            return saved
        except SessionError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        except CaseNameError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
    @router.get("/cases/current")
    def current_case(response: Response) -> dict:
        state = app_state
        with state.stick_pad.transaction_lock():
            current = state.case_store.current
            if current is None:
                return {}
            response.headers["X-RadiWorks-Case-Ref"] = state.case_store.reference_for_case(current)
            return copy.deepcopy(current)

    @router.get("/cases/current/ref")
    def current_case_reference() -> dict:
        current = app_state.case_store.current
        if current is None:
            raise HTTPException(status_code=409, detail="Kein aktiver Fall vorhanden.")
        return {"ref": app_state.case_store.reference_for_case(current)}

    @router.get("/cases/recent")
    def recent_cases() -> dict:
        """Original „LAST CASES“ (dashboardInformations.json, max. 11)."""
        state = app_state
        raw_entries = state.case_store.list_entries(recent=True)
        legacy = [
            copyguard.PUBLIC_REDACTION if copyguard.check_text(entry["name"])[0] == "block"
            else entry["legacy_name"] for entry in raw_entries
        ]
        entries = [{"name": entry["name"], "ref": entry["ref"]} for entry in raw_entries]
        return {"recent": legacy, "entries": entries}

    @router.post("/cases/ref/{reference}/activate")
    @serialized_case_mutation
    def activate_case_reference(reference: str, response: Response) -> dict:
        case = app_state.case_store.load_reference(reference)
        if case is None:
            raise HTTPException(status_code=404, detail="Fallverweis nicht gefunden")
        response.headers["X-RadiWorks-Case-Ref"] = app_state.case_store.reference_for_case(case)
        return case

    @router.get("/cases/ref/{reference}/statistics")
    def case_statistics_reference(reference: str) -> dict:
        case = app_state.case_store.load_reference(reference, record_recent=False, activate=False)
        if case is None:
            raise HTTPException(status_code=404, detail="Fallverweis nicht gefunden")
        return {"case": case["name"], "sessions": len(case.get("sessionList", [])),
                "topList": case_statistics(dict(case))}
    @router.post("/cases/{name}/activate")
    @serialized_case_mutation
    def activate_case(name: str, response: Response) -> dict:
        """Setzt den aktiven lokalen Fall über eine explizite Mutation."""
        state = app_state
        try:
            case = state.case_store.load(name)
        except CaseNameError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        if case is None:
            raise HTTPException(status_code=404, detail=f"Case '{name}' nicht gefunden")
        response.headers["X-RadiWorks-Case-Ref"] = state.case_store.reference_for_case(case)
        return case

    # ---- Session-Navigation (Original: ←/→ + analysisPointer) ----

    @router.get("/analysis/sessions")
    def analysis_sessions() -> dict:
        state = app_state
        case = state.case_store.current
        if not case:
            return {"sessions": []}
        sessions = []
        for index, session in enumerate(case.get("sessionList", [])):
            result = session.get("analysisResult")
            sessions.append(
                {
                    "index": index,
                    "sessionId": session.get("sessionId"),
                    "revision": session.get("revision", 0),
                    "created": session.get("created"),
                    "intention": session.get("intention"),
                    "hasResult": bool(result),
                    "generalVitality": (result or {}).get("generalVitality"),
                    "rates": len((result or {}).get("rateObjects", [])),
                }
            )
        return {"sessions": sessions}

    @router.post("/analysis/sessions/{index}/view")
    @serialized_case_mutation
    def view_session(index: int) -> dict:
        """Historische Session laden, ohne Legacy-Artefakte beim Lesen zu mutieren."""
        state = app_state
        try:
            session = state.case_store.session_at(index)
        except SessionError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        stored = session.get("analysisResult")
        if not stored:
            raise HTTPException(status_code=409, detail="Session hat kein Analyseergebnis.")
        checkpoint = session.get("entropyCheckpoint") or {}
        passport = session.get("passport") or {}
        mode = checkpoint.get("mode") or passport.get("entropy_mode") or "seeded"
        seed = checkpoint.get("effectiveSeed", passport.get("seed"))
        try:
            journal = None
            source_segment = int(checkpoint.get("sourceSegment", 0))
            if mode == "stochastic" and checkpoint.get("journalId"):
                journal = state.open_entropy_journal(checkpoint["journalId"])
                prefix_digest = checkpoint.get("journalPrefixDigest")
                if prefix_digest:
                    if "journalCursor" not in checkpoint or not journal.matches_prefix_digest(
                        int(checkpoint["journalCursor"]),
                        prefix_digest,
                    ):
                        raise JournalConfigurationError(
                            "Entropiejournal stimmt nicht mit dem Session-Checkpoint ueberein"
                        )
                elif checkpoint.get("journalDigest") and checkpoint["journalDigest"] != journal.digest():
                    raise JournalConfigurationError("Entropiejournal stimmt nicht mit der Session ueberein")
                source_segment += 1
            provider = state.new_provider(
                seed,
                mode,
                journal=journal,
                source_segment=source_segment,
            )
            if mode == "seeded":
                provider.restore_seeded_cursor(int(checkpoint.get("drawCount", 0)))
        except (EntropyConfigurationError, JournalConfigurationError, ValueError) as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        gv_state = session.get("gvState") or {}
        state.gv_round = GvRoundState(
            result=AnalysisResult.from_dict(stored),
            entropy=provider,
            general_vitality=gv_state.get("generalVitality", stored.get("generalVitality") or 0),
            counter=gv_state.get("counter", 0),
            total_runs=gv_state.get("totalRuns", 0),
            history=session.get("gvHistory", []),
            session_id=session.get("sessionId"),
            session_index=index,
            draft_id=session.get("draftId"),
            revision=session.get("revision", 0),
            page_start=gv_state.get("pageStart", 0),
            page_length=gv_state.get("pageLength", MAX_ROUND_STEPS),
        )
        return {
            "pointer": index,
            "sessionId": session.get("sessionId"),
            "draftId": session.get("draftId"),
            "sourceKind": "stickpad" if passport.get("input_hash_scheme") == "stickpad-position-catalog-v1" else "analysis",
            "result": stored,
            "state": state.gv_round.state_dict(),
        }

    @router.get("/cases/{name}")
    def load_case(name: str) -> dict:
        state = app_state
        try:
            case = state.case_store.load(
                name,
                record_recent=False,
                activate=False,
            )
        except CaseNameError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
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

    def submit_promotion(draft_id: str, request: DraftPromotionRequest, *, legacy: bool = False) -> dict:
        state = app_state
        with state.stick_pad.transaction_lock(), state._promotion_lock:
            bindings = {}
            try:
                state.recovery.ensure_no_pending()
                draft = state.draft_store.get(draft_id)
                current = state.case_store.current
                if draft is not None and current is not None:
                    current_owner = state.case_store.find_identity(current["caseId"]) if current.get("caseId") else None
                    stored = current_owner[1] if current_owner is not None else state.case_store.load(current["name"], record_recent=False, activate=False)
                    focus = draft.get("focus")
                    source_name = focus.get("case") if isinstance(focus, dict) else None
                    source_case_ref = (
                        state.case_store.reference_for_name(source_name)
                        if isinstance(source_name, str) else None
                    )
                    bindings = bind_promoted_rates(
                        draft, stored, scope=state.scope,
                        case_ref=state.case_store.reference_for_case(current),
                        source_case_ref=source_case_ref,
                    )
            except (RecoveryError, CaseNameError, OSError, ValueError, TypeError, KeyError, AttributeError):
                logging.getLogger(__name__).warning("GV-Beobachtungsbindung nicht verfuegbar; regulaerer Promote bleibt erhalten")
            try:
                promotion_id, entries = state.draft_store.begin_promotion(
                    draft_id,
                    max_rates=request.max_rates,
                    seconds_per_rate=request.seconds_per_rate,
                    multiplier=request.multiplier,
                    observation_bindings=bindings,
                )
            except DraftError as exc:
                raise HTTPException(status_code=409, detail=str(exc)) from exc
            except BroadcastError as exc:
                raise HTTPException(status_code=422, detail=str(exc)) from exc
            try:
                queued = state.broadcast.enqueue_batch(
                    entries,
                    on_accepted=lambda ids: state.draft_store.finish_promotion(
                        draft_id, promotion_id, ids
                    ),
                )
            except Exception as exc:
                try:
                    state.draft_store.fail_promotion(draft_id, promotion_id)
                except (DraftError, OSError):
                    # Ein pending-Marker bleibt fuer den kontrollierten Neustart sichtbar.
                    pass
                status = 422 if isinstance(exc, BroadcastError) else 503
                raise HTTPException(status_code=status, detail="Promote-Batch wurde nicht uebernommen") from exc
            result = {
                "draftId": draft_id,
                "status": "promoted",
                "promotionId": promotion_id,
                "broadcastEntries": queued,
            }
            if legacy:
                result["mode"] = "legacy-mix"
            state.publish(
                "clipboard.updated",
                {"draftId": draft_id, "status": "promoted", "queued": len(queued)},
            )
            return result

    @router.get("/drafts")
    def drafts(status: str | None = None) -> dict:
        state = app_state
        return {"drafts": [_draft_view(d) for d in state.draft_store.list(status)]}

    @router.get("/drafts/{draft_id}")
    def draft_by_id(draft_id: str) -> dict:
        state = app_state
        draft = state.draft_store.get(draft_id)
        if draft is None:
            raise HTTPException(status_code=404, detail="Draft nicht gefunden")
        return _draft_view(draft)

    @router.post("/drafts/{draft_id}/promote")
    def promote_draft(draft_id: str, body: DraftPromotionRequest | None = None) -> dict:
        return submit_promotion(draft_id, body or DraftPromotionRequest())

    @router.post("/drafts/{draft_id}/transition")
    def transition_draft(draft_id: str, body: dict) -> dict:
        state = app_state
        requested = body.get("status", "")
        if requested not in {"client_review", "ready", "discarded"}:
            raise HTTPException(status_code=409, detail="Status nur ueber den vorgesehenen Endpunkt aendern")
        try:
            with state._promotion_lock:
                draft = state.draft_store.transition(draft_id, requested)
        except DraftError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        state.publish("clipboard.updated", {"draftId": draft_id, "status": draft["status"]})
        return _draft_view(draft)

    @router.post("/drafts/{draft_id}/discard")
    def discard_draft(draft_id: str) -> dict:
        return transition_draft(draft_id, {"status": "discarded"})

    # 4. Broadcast

    def broadcast_preview(request):
        verdict, _ = copyguard.check_text(request.signature)
        if verdict == "block":
            raise HTTPException(409, "CopyGuard blockt Broadcast (fail-closed)")
        target = capture_broadcast_target(request, {"kind": "direct"})
        saved = app_state.settings_store.load("Settings").to_dict()
        capacity = app_state.broadcast_capacity(saved)
        policy = app_state.broadcast_policy(target, request.seconds, saved=saved)
        proof = target.payload()
        snapshot = proof.get("contextSnapshot")
        # Per-request random receipt IDs are omitted; semantic context remains bound.
        context = {k: v for k, v in (snapshot or {}).items() if k not in ("digest", "snapshotId", "capturedAt")}
        options = {k: v for k, v in policy.payload().items() if k not in ("digest", "rootJobId", "parentJobId")}
        digest = document_digest({"request": request.model_dump(exclude={"expected_preview_digest"}),
            "source": proof["source"], "scope": proof["scope"], "context": context,
            "procedure": proof["procedure"], "mode": proof["entropyMode"],
            "policy": options, "capacity": capacity})
        return target, policy, digest, capacity

    @router.post("/broadcast/preview")
    @serialized_case_mutation
    def preview_broadcast(request: BroadcastRequest) -> dict:
        try:
            target, policy, digest, capacity = broadcast_preview(request)
            return {"previewDigest": digest, "executionPolicy": policy.payload(),
                "maxActive": capacity, "binding": target.payload()["binding"]}
        except PolicyError as exc:
            raise HTTPException(422, str(exc)) from exc
        except OSError as exc:
            raise HTTPException(503, "Broadcast-Vorschau ist derzeit nicht sicher verfügbar.") from exc

    @router.post("/broadcast")
    @serialized_case_mutation
    def broadcast(request: BroadcastRequest) -> dict:
        """Explicit operator command, with optional stale-preview protection."""
        try:
            target, policy, digest, capacity = broadcast_preview(request)
            if request.expected_preview_digest is not None and request.expected_preview_digest != digest:
                raise HTTPException(409, "Fall oder Einstellungen wurden seit der Vorschau geändert. Bitte Vorschau erneut prüfen.")
            return app_state.broadcast.enqueue(request.signature, request.seconds, request.multiplier,
                clear=request.clear, delay_ms=request.delay_ms, repeat=request.repeat,
                target=target, execution_policy=policy)
        except (BroadcastError, PolicyError) as exc:
            raise HTTPException(422, str(exc)) from exc
        except OSError as exc:
            raise HTTPException(503, "Broadcast-Auftrag konnte nicht dauerhaft angenommen werden.") from exc

    def watchlist_basis(request):
        target = capture_broadcast_target(request, {"kind": "direct"})
        proof = target.payload(); snapshot = proof.get("contextSnapshot")
        current = app_state.case_store.current
        if not current or proof["binding"] != "bound" or snapshot["caseId"] != current.get("caseId"):
            raise HTTPException(409, "Bitte eine gespeicherte Original-Analysesitzung des aktiven Falls wählen.")
        matches = [row for row in current.get("sessionList", []) if row.get("sessionId") == request.source_session_id]
        if len(matches) != 1: raise HTTPException(409, "Originalsitzung ist nicht eindeutig verfügbar.")
        session = matches[0]; result = session.get("analysisResult", {}); rows = result.get("rateObjects", [])
        if len(set(request.indices)) != len(request.indices) or any(not 0 <= i < len(rows) for i in request.indices):
            raise HTTPException(422, "Bitte 1 bis 100 verschiedene verfügbare Raten wählen.")
        names = [rows[i]["nameOrRate"] for i in request.indices]
        if any(copyguard.check_text(name)[0] == "block" for name in names): raise HTTPException(409, "CopyGuard hält mindestens eine gewählte Rate zurück.")
        basis = {"caseId": snapshot["caseId"], "sessionId": request.source_session_id,
            "contextSnapshot": snapshot, "sessionDigest": document_digest(session),
            "indices": request.indices, "rates": names, "referenceGv": result.get("generalVitality"),
            "mode": request.mode, "seed": request.seed if request.mode == "seeded" else None}
        try: app_state.watchlist._validate_basis(basis)
        except WatchlistError as exc: raise HTTPException(409, str(exc)) from exc
        return basis, document_digest(basis)

    @router.post("/watchlist/preview")
    @serialized_case_mutation
    def watchlist_preview(request: WatchlistRequest) -> dict:
        basis, digest = watchlist_basis(request)
        if request.mode == "stochastic":
            try: EntropyJournalStore(app_state.journal_dir)
            except JournalConfigurationError as exc: raise HTTPException(503, "Stochastik benötigt den gesicherten Journalschlüssel.") from exc
        return {"previewDigest": digest, "count": len(basis["rates"]), "mode": basis["mode"], "seed": basis["seed"], "referenceGv": basis["referenceGv"]}

    @router.post("/watchlist")
    @serialized_case_mutation
    def watchlist_start(request: WatchlistRequest) -> dict:
        basis, digest = watchlist_basis(request)
        if request.expected_preview_digest != digest or request.request_id is None:
            raise HTTPException(409, "Watchlist-Vorschau fehlt oder Sitzung wurde geändert. Bitte erneut prüfen.")
        try:
            provider = app_state.new_provider(basis["seed"], basis["mode"], journal=app_state.create_entropy_journal() if basis["mode"] == "stochastic" else None)
            return app_state.watchlist.submit(basis, provider, request.request_id)
        except JournalConfigurationError as exc: raise HTTPException(503, "Stochastik benötigt den gesicherten Journalschlüssel.") from exc
        except (WatchlistError, OSError) as exc: raise HTTPException(409, "Watchlist-Auftrag konnte nicht sicher angenommen werden.") from exc

    def watchlist_owner(job):
        try: record = app_state.watchlist.get(job)
        except WatchlistError as exc: raise HTTPException(409, str(exc)) from exc
        if record["input"]["caseId"] != (app_state.case_store.current or {}).get("caseId"):
            raise HTTPException(409, "Watchlist gehört zu einem anderen Fall. Bitte diesen Fall bewusst laden.")
        return record

    @router.get("/watchlist")
    @serialized_case_mutation
    def watchlist_history() -> dict:
        current = app_state.case_store.current or {}
        try: return {"jobs": app_state.watchlist.history(current.get("caseId"))}
        except (WatchlistError, OSError) as exc: raise HTTPException(409, "Watchlist-Historie ist nicht sicher lesbar.") from exc

    @router.get("/watchlist/{job}")
    @serialized_case_mutation
    def watchlist_status(job: str) -> dict: return watchlist_owner(job)

    @router.post("/watchlist/{job}/cancel")
    @serialized_case_mutation
    def watchlist_cancel(job: str, request: BroadcastCaseGuard) -> dict:
        current = app_state.case_store.current
        ref = app_state.case_store.reference_for_case(current) if current else None
        if request.expected_case_ref != ref or request.expected_context_version != (current or {}).get("contextVersion"):
            raise HTTPException(409, "Fallauswahl geändert. Bitte erneut laden.")
        watchlist_owner(job)
        try: return app_state.watchlist.cancel(job)
        except (WatchlistError, OSError) as exc: raise HTTPException(409, "Watchlist-Abbruch konnte nicht gespeichert werden.") from exc

    @router.get("/broadcast/adjustments")
    def broadcast_adjustments() -> dict:
        try:
            return {"decisions": app_state.broadcast_targets.adjustments()}
        except (BroadcastTargetError, OSError) as exc:
            raise HTTPException(409, "Anpassungshistorie ist nicht sicher lesbar.") from exc

    @router.post("/broadcast/mix")
    def broadcast_mix(request: BroadcastMixRequest) -> dict:
        """Original 'BROADCAST MIX' — Festlegung 2 (2026-08-29).

        Settings broadcast.legacyMixMode=true: ein Klick — Draft wird in einer
        Kette (draft -> ready -> promoted) mit CopyGuard-Pruefung uebernommen.
        false (Default, Aurelia D18): 409 — Draft muss sichtbar geprueft und
        ueber /drafts/{id}/promote freigegeben werden.
        """
        state = app_state
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
        except DraftError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        return submit_promotion(
            request.draft_id,
            DraftPromotionRequest(
                max_rates=request.max_rates,
                seconds_per_rate=request.seconds_per_rate,
                multiplier=request.multiplier,
            ),
            legacy=True,
        )

    @router.get("/broadcast/queue")
    def broadcast_queue() -> dict:
        state = app_state
        return state.broadcast.queue_state()

    @router.delete("/broadcast/current")
    def stop_current() -> dict:
        state = app_state
        state.broadcast.stop_current()
        return {"stopped": "current"}

    @router.delete("/broadcast/all")
    def stop_all() -> dict:
        state = app_state
        state.broadcast.stop_all()
        return {"stopped": "all"}

    # 9. Materia Medica

    @router.post("/materia/clarke-compare")
    def clarke_compare(body: dict) -> dict:
        """CLARKE-Button des Originals (Aether_4): Symptom-Vergleich der
        aktuellen Analyse mit der Ziel-Remedy (AnalysisService.analyzeClarke,
        Berechnungsteil; Report rendert die Webapp)."""
        state = app_state
        rate = str(body.get("rate", "")).strip()
        if not rate:
            raise HTTPException(status_code=422, detail="rate fehlt")
        result = state.gv_round.result if state.gv_round else None
        names = [r.name_or_rate for r in result.rate_objects] if result else []
        return state.materia_medica.compare_clarke(rate, names)

    @router.get("/materiaMedicaSearch")
    def materia_search(field: str | None = None, query: str = "") -> dict:
        state = app_state
        if len(query) < 3:
            return {"searchResults": []}
        return {"searchResults": state.materia_medica.search(query, field)}

    # WebSocket-Fachkanal — als Router-Route registriert, damit er mit allen
    # REST-Routen aus einer Quelle (include_router) eingebunden wird.
    # HINWEIS Betrieb: uvicorn benoetigt eine WebSocket-Bibliothek
    # (`pip install websockets`), sonst antwortet der Handshake mit 404.
    @router.websocket("/ws")
    async def ws_channel(
        websocket: WebSocket,
        last_event_id: int | None = None,
        last_boot: str | None = None,
    ) -> None:
        try:
            app_state.scope_resolver.resolve(websocket.headers)
        except ValueError:
            await websocket.close(code=1008)
            return
        await websocket_endpoint(
            websocket,
            last_event_id,
            last_boot,
            state=app_state,
        )

    return router


def _draft_view(draft: dict) -> dict:
    """Draft ohne volles Payload (Payload nur unter /drafts/{id})."""
    return {**{k: v for k, v in draft.items() if k != "payload"}, "contextSnapshot": draft.get("contextSnapshot")}


# -- WebSocket -----------------------------------------------------------------


async def _send_handshake_envelope(
    websocket: WebSocket,
    envelope: dict,
    deadline: float,
) -> None:
    loop = asyncio.get_running_loop()
    remaining = deadline - loop.time()
    if remaining <= 0:
        raise _HandshakeDeadline
    try:
        await asyncio.wait_for(
            websocket.send_json(envelope),
            timeout=min(WS_SEND_TIMEOUT_S, remaining),
        )
    except TimeoutError as exc:
        if loop.time() >= deadline:
            raise _HandshakeDeadline from exc
        raise


async def websocket_endpoint(
    websocket: WebSocket,
    last_event_id: int | None = None,
    last_boot: str | None = None,
    *,
    state: AppState,
) -> None:
    with state._event_lock:
        connection_start_seq = state._event_seq
    handshake_deadline = (
        asyncio.get_running_loop().time() + WS_HANDSHAKE_TIMEOUT_S
    )
    try:
        try:
            await asyncio.wait_for(
                websocket.accept(),
                timeout=WS_HANDSHAKE_TIMEOUT_S,
            )
        except TimeoutError as exc:
            raise _HandshakeDeadline from exc

        boot_changed = last_boot is not None and last_boot != BOOT_ID
        first_connection = last_event_id is None and last_boot is None

        with state._event_lock:
            replay_upper = state._event_seq
            oldest_available = (
                state.event_history[0]["id"] if state.event_history else None
            )
            gap_reason: str | None = None

            if first_connection:
                replay_after = connection_start_seq
            elif boot_changed:
                replay_after = 0
                if oldest_available is not None and oldest_available > 1:
                    gap_reason = "boot-history-truncated"
                    replay_after = oldest_available - 1
            else:
                requested = last_event_id if last_event_id is not None else 0
                if requested > replay_upper:
                    gap_reason = "cursor-ahead"
                    replay_after = (
                        oldest_available - 1
                        if oldest_available is not None
                        else replay_upper
                    )
                elif (
                    oldest_available is not None
                    and requested < oldest_available - 1
                ):
                    gap_reason = "history-truncated"
                    replay_after = oldest_available - 1
                else:
                    replay_after = requested

            replay = [
                envelope
                for envelope in state.event_history
                if replay_after < envelope["id"] <= replay_upper
            ]
            state._ws_pending[websocket] = _PendingHandshake()

        await _send_handshake_envelope(
            websocket,
            control_envelope(
                "server.hello",
                {"cursor": replay_after, "latestEventId": replay_upper},
            ),
            handshake_deadline,
        )
        if gap_reason is not None:
            await _send_handshake_envelope(
                websocket,
                control_envelope(
                    "server.replay_gap",
                    {
                        "reason": gap_reason,
                        "requestedLastEventId": last_event_id,
                        "oldestAvailableEventId": oldest_available,
                        "latestEventId": replay_upper,
                    },
                ),
                handshake_deadline,
            )
        for envelope in replay:
            await _send_handshake_envelope(
                websocket,
                envelope,
                handshake_deadline,
            )

        # Während Hello/Replay publizierte Events landen geordnet im Pending-
        # Puffer. Erst ein atomarer leer->live-Wechsel macht den Client sichtbar.
        pending_sent = 0
        while True:
            with state._event_lock:
                pending = state._ws_pending[websocket]
                if pending.overflowed:
                    raise _HandshakeOverflow
                if not pending.events:
                    state._ws_pending.pop(websocket, None)
                    state._ws_clients.add(websocket)
                    break
                batch = list(pending.events)
                pending.events.clear()
            if pending_sent + len(batch) > WS_HANDSHAKE_QUEUE:
                raise _HandshakeOverflow
            pending_sent += len(batch)
            for envelope in batch:
                await _send_handshake_envelope(
                    websocket,
                    envelope,
                    handshake_deadline,
                )

        while True:
            message = await websocket.receive_text()
            if message == "ping":
                state._schedule_send(control_envelope("pong"), (websocket,))
    except (_HandshakeOverflow, _HandshakeDeadline):
        await state._close_ws_client(websocket, code=1013)
    except WebSocketDisconnect:
        pass
    except Exception:
        await state._close_ws_client(websocket, code=1011)
    finally:
        state._remove_ws_client(websocket)

