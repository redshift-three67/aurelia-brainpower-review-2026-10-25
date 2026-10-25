"""Broadcast-Manager — Port der Broadcast-Mechanik (FUNKTIONSANALYSE §5).

Umfang des Engine-Kernels: Queue, Laufzeit, Resonanz-Events, Binaural-Parameter,
Stop-Kontrolle. Die visuelle Fibonacci-Aesthetik (13/21/33/54/89/144/.../987)
ist Darstellung und gehoert in die Webapp (P3); der Engine-Kernel liefert die
identischen Resonanz- und Progress-Ereignisse.

Aurelia-Angleichung:
- Server ist die Uhr (Hard Rule 4): Ticks im Manager-Thread, nie setInterval im Browser.
- Progress-Events alle 200 ms (docs/15-live.md: Analyse-Progress 200 ms).
- Broadcast ist rein ereignisbasiert (isHardwareActivatable: false) — die
  GPIO-LED-Mapping-Tabelle des Originals bleibt als Datenstruktur erhalten
  (BROADCAST_LED_GROUPS), damit ein spaeterer aurelia-emitterd-Anschluss
  (Hard Rule 11: Lease -> Arming -> ACK) dieselbe Semantik nutzen kann.
"""

from __future__ import annotations

import copy
import json
import threading
import time
import uuid
import logging
from collections import deque
from dataclasses import dataclass, field
from typing import Any, Callable

from ..entropy import EntropyProvider
from .emitter import DEFAULT_DELAY_MS, DEFAULT_REPEAT, emitter_sequence
from .observation_binding import ObservationBinding
from .broadcast_policy import ExecutionPolicy
from .analysis import check_general_vitality
from ..scope import ScopeContext
from .personal_context import ContextReference
from .broadcast_target import BroadcastTarget, BroadcastTargetError

# Original: max. 8 aktive Elemente, im single-Modus 1 (GuiElements, Zeile 215-224)
MAX_ACTIVE = 8

# BroadCastService-LED-Gruppen (FUNKTIONSANALYSE §5.3) — Referenzdaten; die
# Verarbeitung liegt im VirtualEmitter (core/emitter.py).
BROADCAST_LED_GROUPS: dict[str, list[int]] = {
    "ultraviolet": [1, 2, 3, 5, 8],
    "reds": [2, 5],
    "greens": [3, 7],
    "blues": [4, 8],
    "whites": [0, 9],
    "infrared": [1, 6],
}

# BroadcastElement-Zeile 207: Resonanz ab naechster Wert von 6765 + multiplier
# (Fibonacci 6765); Wahrscheinlichkeit exakt 1/(6765+multiplier) je Draw.
RESONANCE_BASE = 6765

# BroadcastElement-Zeile 292-294: Binaural-Parameter bei Resonanz
BINAURAL_BASE_FREQ = 50
BINAURAL_MAX_OFFSET = 500
BINAURAL_BEAT_MAX = 50
BINAURAL_VOLUME_STEPS = 10

# Original: paintOneLayer liefert ~60 Draws/s (Frame-Loop); Tick 50 ms => 3 Draws.
DRAWS_PER_TICK = 3
TICK_SECONDS = 0.05
PROGRESS_EVENT_EVERY_S = 0.2

MIN_BROADCAST_SECONDS = 1
MAX_BROADCAST_SECONDS = 24 * 3600
MIN_MULTIPLIER = 1
MAX_MULTIPLIER = 1000
MIN_DELAY_MS = 1
MAX_DELAY_MS = 10_000
MIN_REPEAT = 1
MAX_REPEAT = 1000


class BroadcastError(ValueError):
    """Ein Broadcast-Element verletzt den Queue-Vertrag."""


@dataclass
class BroadcastElement:
    signature: str
    seconds: int
    multiplier: int = 1
    clear: bool = False
    delay_ms: int = DEFAULT_DELAY_MS
    repeat: int = DEFAULT_REPEAT
    broadcast_id: str = field(default_factory=lambda: uuid.uuid4().hex)
    start: float | None = None
    resonance_count: int = 0
    observation_binding: ObservationBinding | None = None
    context_reference: ContextReference | None = None
    target: BroadcastTarget | None = None
    entropy_provider: EntropyProvider | None = None
    execution_policy: ExecutionPolicy | None = None
    _presentation_snapshot: str | None = field(default=None, repr=False)

    def __setattr__(self, name: str, value: Any) -> None:
        if name == "execution_policy" and name in self.__dict__:
            raise AttributeError("execution_policy is pinned at construction")
        if name == "_presentation_snapshot" and self.__dict__.get(name) is not None:
            raise AttributeError("presentation snapshot is immutable after acceptance")
        if name == "entropy_provider" and name in self.__dict__:
            raise AttributeError("entropy_provider is pinned at construction")
        if name == "target":
            if name in self.__dict__:
                raise AttributeError("target is pinned at construction")
            if value is not None and not isinstance(value, BroadcastTarget):
                raise TypeError("target must be a BroadcastTarget")
        if name == "context_reference":
            if name in self.__dict__:
                raise AttributeError("context_reference is pinned at construction")
            if value is not None and not isinstance(value, ContextReference):
                raise TypeError("context_reference must be a ContextReference")
        if name == "observation_binding":
            if name in self.__dict__:
                raise AttributeError("observation_binding is pinned at construction")
            if value is not None and not isinstance(value, ObservationBinding):
                raise TypeError("observation_binding must be an ObservationBinding")
        object.__setattr__(self, name, value)

    def __delattr__(self, name: str) -> None:
        if name in ("observation_binding", "context_reference", "target", "entropy_provider", "execution_policy", "_presentation_snapshot"):
            raise AttributeError(f"{name} is pinned at construction")
        object.__delattr__(self, name)

    def bind_presentation(self, value: dict) -> None:
        if self._presentation_snapshot is not None or type(value) is not dict:
            raise BroadcastError("Präsentationsbeleg ist ungültig oder bereits eingefroren.")
        self._presentation_snapshot = json.dumps(
            copy.deepcopy(value), ensure_ascii=False, sort_keys=True, separators=(",", ":"),
        )

    @property
    def elapsed(self) -> float:
        if self.start is None:
            return 0.0
        return time.monotonic() - self.start

    @property
    def progress(self) -> float:
        if self.start is None:
            return 0.0
        if self.seconds <= 0:
            return 1.0
        return min(1.0, self.elapsed / self.seconds)

    def payload(self) -> dict[str, Any]:
        result = {
            "broadcastId": self.broadcast_id,
            "signature": self.signature,
            "seconds": self.seconds,
            "multiplier": self.multiplier,
            "clear": self.clear,
            "delayMs": self.delay_ms,
            "repeat": self.repeat,
        }
        if self.entropy_provider is not None:
            provider = self.entropy_provider
            result["entropy"] = {
                "mode": provider.mode,
                "source": provider.status().active_source,
                "drawCount": provider.draw_count,
                "seed": provider.effective_seed,
            }
        if self.execution_policy is not None:
            result["executionPolicy"] = self.execution_policy.payload()
        if self.target is not None:
            result["targetReference"] = self.target.summary()
        if self._presentation_snapshot is not None:
            result["presentation"] = json.loads(self._presentation_snapshot)
        if self.context_reference is not None:
            result["contextReference"] = self.context_reference.payload()
        if self.observation_binding is not None:
            result["observationBinding"] = self.observation_binding.payload()
        return result


def _validate_integer(name: str, value: int, minimum: int, maximum: int) -> None:
    if not isinstance(value, int) or isinstance(value, bool) or not minimum <= value <= maximum:
        raise BroadcastError(f"{name} muss zwischen {minimum} und {maximum} liegen")


def validate_broadcast_input(
    signature: str,
    seconds: int,
    multiplier: int,
    delay_ms: int,
    repeat: int,
) -> None:
    if not isinstance(signature, str) or not signature.strip():
        raise BroadcastError("signature darf nicht leer sein")
    _validate_integer("seconds", seconds, MIN_BROADCAST_SECONDS, MAX_BROADCAST_SECONDS)
    _validate_integer("multiplier", multiplier, MIN_MULTIPLIER, MAX_MULTIPLIER)
    _validate_integer("delay_ms", delay_ms, MIN_DELAY_MS, MAX_DELAY_MS)
    _validate_integer("repeat", repeat, MIN_REPEAT, MAX_REPEAT)


class BroadcastManager:
    """FIFO-Queue plus Laufzeit-Thread; Events an Abonnenten (WebSocket)."""

    def __init__(
        self,
        entropy: EntropyProvider,
        emit: Callable[[str, dict], None],
        on_tick: Callable[[], None] | None = None,
        keep_alive: Callable[[], bool] | None = None,
        on_accept: Callable[[list[dict]], None] | None = None,
        on_abort: Callable[[dict], None] | None = None,
        entropy_factory: Callable[[BroadcastTarget], EntropyProvider] | None = None,
        on_entropy: Callable[[dict], None] | None = None,
        policy_factory: Callable[..., ExecutionPolicy] | None = None,
        capacity: Callable[[], int] | None = None,
        on_adjustment: Callable[[dict], None] | None = None,
    ) -> None:
        self._policy_factory = policy_factory
        self._capacity = capacity
        self._on_adjustment = on_adjustment
        self._entropy = entropy
        self._on_accept = on_accept
        self._on_abort = on_abort
        self._entropy_factory = entropy_factory
        self._on_entropy = on_entropy
        self._bound_providers: list[EntropyProvider] = []
        self._emit = emit
        self._on_tick = on_tick
        self._keep_alive = keep_alive
        self._queue: deque[BroadcastElement] = deque()
        self._active: list[BroadcastElement] = []
        self._lock = threading.RLock()
        self._running = False
        self._shutdown = False
        self._resonance_totals: dict[str, int] = {}
        self._thread: threading.Thread | None = None

    def active_count(self) -> int:
        with self._lock:
            return len(self._active)

    def ensure_running(self) -> None:
        """Startet den Laufzeit-Thread (auch ohne Queue — z. B. Auto-Modus)."""
        self._start_thread()

    # -- Steuerung ---------------------------------------------------------

    def enqueue(
        self,
        signature: str,
        seconds: int,
        multiplier: int = 1,
        *,
        clear: bool = False,
        delay_ms: int = DEFAULT_DELAY_MS,
        repeat: int = DEFAULT_REPEAT,
        target: BroadcastTarget | None = None,
        execution_policy: ExecutionPolicy | None = None,
    ) -> dict[str, Any]:
        validate_broadcast_input(signature, seconds, multiplier, delay_ms, repeat)
        policy = execution_policy or (self._policy_factory(target, seconds, allow_delta=True) if self._policy_factory else None)
        if policy is not None:
            policy = ExecutionPolicy.from_payload(policy.payload())
            seconds = policy.seconds
        element = BroadcastElement(
            signature=signature,
            seconds=seconds,
            multiplier=multiplier,
            clear=clear,
            delay_ms=delay_ms,
            repeat=repeat,
            target=target,
            entropy_provider=self._provider_for_target(target),
            execution_policy=policy,
        )
        steps = [
            step.to_dict()
            for step in emitter_sequence(
                signature,
                clear=clear,
                delay_ms=delay_ms,
                repeat=repeat,
            )
        ]
        with self._lock:
            if self._shutdown:
                raise RuntimeError("Broadcast-Manager ist bereits beendet")
            try:
                self._persist_acceptance([element])
                self._checkpoint_entropy(element)
                self._queue.append(element)
                self._start_thread()
                # VirtualEmitter: die komplette LED-Choreografie als Event
                # ausliefern, aber erst nach erfolgreichem Threadstart.
                self._emit(
                    "emitter.sequence",
                    {**element.payload(), "steps": steps},
                )
            except Exception:
                if element in self._queue:
                    self._queue.remove(element)
                self._record_abort([element])
                raise
            queued = len(self._queue)
            return {**element.payload(), "queued": queued}

    def enqueue_batch(
        self,
        entries: list[dict[str, Any]],
        *,
        on_accepted: Callable[[list[str]], None],
    ) -> list[dict[str, Any]]:
        """Uebernimmt einen Promote-Batch und persistiert den Abschluss vor Sichtbarkeit."""
        if not entries:
            raise BroadcastError("Broadcast-Batch darf nicht leer sein")
        prepared: list[tuple[BroadcastElement, list[dict[str, Any]]]] = []
        for entry in entries:
            signature = entry["signature"]
            seconds = entry["seconds"]
            multiplier = entry.get("multiplier", 1)
            validate_broadcast_input(
                signature, seconds, multiplier, DEFAULT_DELAY_MS, DEFAULT_REPEAT
            )
            try:
                binding = (
                    ObservationBinding.from_payload(entry["observationBinding"])
                    if "observationBinding" in entry else None
                )
            except (TypeError, ValueError) as exc:
                raise BroadcastError("Ungueltige GV-Beobachtungsbindung") from exc
            try:
                context = ContextReference.from_payload(entry["contextReference"]) if "contextReference" in entry else None
            except (TypeError, ValueError) as exc:
                raise BroadcastError("Ungueltige Kontextreferenz") from exc
            try:
                target = BroadcastTarget.from_payload(entry["target"]) if "target" in entry else None
                if target is not None and context is not None:
                    source = target.payload()["source"]
                    snapshot = target.payload()["contextSnapshot"]
                    reference = context.payload()
                    if snapshot is None or any(reference[k] != snapshot[k] for k in ("schemaVersion", "snapshotId", "caseId", "contextVersion", "scope", "digest")) or any(reference[k] != source.get(k) for k in ("sessionId", "draftId")):
                        raise BroadcastTargetError("Kontextreferenz und Auftragsziel stimmen nicht überein.")
            except (TypeError, ValueError) as exc:
                raise BroadcastError("Ungültiges oder widersprüchliches Broadcastziel") from exc
            policy = self._policy_factory(target, seconds, allow_delta=False) if self._policy_factory else None
            element = BroadcastElement(
                signature,
                seconds,
                multiplier,
                observation_binding=binding,
                context_reference=context,
                target=target,
                entropy_provider=self._provider_for_target(target),
                execution_policy=policy,
            )
            steps = [step.to_dict() for step in emitter_sequence(signature)]
            prepared.append((element, steps))
        with self._lock:
            if self._shutdown:
                raise BroadcastError("Broadcast-Manager ist bereits beendet")
            try:
                self._persist_acceptance([element for element, _ in prepared])
                for element, _ in prepared:
                    self._checkpoint_entropy(element)
                for element, _ in prepared:
                    self._queue.append(element)
                self._start_thread()
                on_accepted([element.broadcast_id for element, _ in prepared])
            except Exception:
                for element, _ in prepared:
                    if element in self._queue:
                        self._queue.remove(element)
                self._record_abort([element for element, _ in prepared])
                raise
            for element, steps in prepared:
                try:
                    self._emit("emitter.sequence", {**element.payload(), "steps": steps})
                except Exception:
                    logging.getLogger(__name__).exception("Promote-Event konnte nicht zugestellt werden")
            return [element.payload() for element, _ in prepared]

    def _provider_for_target(self, target: BroadcastTarget | None) -> EntropyProvider | None:
        if target is None:
            return None
        mode = target.payload()["entropyMode"]
        if self._entropy_factory is None:
            if mode == "stochastic":
                raise BroadcastError("Stochastic-Broadcast benötigt einen eigenen Journal-Provider.")
            provider = self._entropy
        else:
            provider = self._entropy_factory(target)
        if getattr(provider, "mode", None) != mode:
            raise BroadcastError("Provider-Modus stimmt nicht mit dem Broadcastziel überein.")
        if mode == "stochastic":
            if not getattr(provider, "has_journal", False):
                raise BroadcastError("Stochastic-Broadcast benötigt ein eigenes Journal.")
            if self._on_entropy is None:
                raise BroadcastError("Stochastic-Broadcast benötigt dauerhafte Entropiecheckpoint-Speicherung.")
        if self._entropy_factory is not None:
            if any(provider is existing for existing in self._bound_providers):
                raise BroadcastError("Jeder gebundene Broadcast benötigt einen eigenen Provider.")
            self._bound_providers.append(provider)
        return provider

    def _checkpoint_entropy(self, element: BroadcastElement) -> None:
        provider = element.entropy_provider
        if provider is None or element.target is None or self._on_entropy is None:
            return
        provider.commit_journal()
        self._on_entropy({
            "broadcastId": element.broadcast_id,
            "checkpoint": provider.checkpoint(),
        })

    def _persist_acceptance(self, elements: list[BroadcastElement]) -> None:
        if self._on_accept is None:
            return  # Compatibility for standalone legacy kernel users.
        if any(element.target is None for element in elements):
            raise BroadcastError("Neue Broadcasts benötigen einen festen Zielbeleg.")
        entries = [{
            "broadcastId": element.broadcast_id, "signature": element.signature,
            "seconds": element.seconds, "multiplier": element.multiplier,
            "clear": element.clear, "delayMs": element.delay_ms, "repeat": element.repeat,
            "target": element.target.payload(),
            **({"executionPolicy": element.execution_policy.payload()} if element.execution_policy else {}),
        } for element in elements]
        try:
            accepted = self._on_accept(entries)
        except BroadcastTargetError as exc:
            raise BroadcastError(str(exc)) from exc
        if accepted is None:
            return
        expected = {element.broadcast_id for element in elements}
        if type(accepted) is not dict or set(accepted) != expected:
            raise BroadcastError("Annahmebeleg hat keine vollständigen Präsentationsbelege geliefert.")
        for element in elements:
            element.bind_presentation(accepted[element.broadcast_id])

    def _record_abort(self, elements: list[BroadcastElement]) -> None:
        if self._on_abort is None:
            return
        for element in elements:
            try:
                self._on_abort({"broadcastId": element.broadcast_id, "failed": True})
            except Exception:
                logging.getLogger(__name__).exception("Abgelehnter Broadcast braucht persistente Wiederanlaufklärung")

    def stop_current(self) -> None:
        """Stoppt das erste aktive Element vor Rückkehr synchron."""
        self._stop_current_element()

    def stop_all(self) -> None:
        """Leert aktive und wartende Elemente vor Rückkehr synchron."""
        self._stop_all_elements()

    def queue_state(self) -> dict[str, Any]:
        with self._lock:
            return {
                "queued": [element.payload() for element in self._queue],
                "active": [
                    {
                        **element.payload(),
                        "progress": round(element.progress, 4),
                        "resonanceCount": element.resonance_count,
                    }
                    for element in self._active
                ],
                "resonanceTotals": dict(self._resonance_totals),
            }

    def commit_observation_if_active(self, broadcast_id: str, binding: dict, commit: Callable[[], None]) -> bool:
        """Short commit boundary: a concurrent stop/end cannot publish a late sample."""
        with self._lock:
            if self._shutdown:
                return False
            element = next((e for e in self._active if e.broadcast_id == broadcast_id), None)
            if element is None or element.progress >= 1.0 or element.observation_binding is None:
                return False
            if element.observation_binding.payload() != binding:
                return False
            commit()
            return True

    def shutdown(self, timeout: float | None = 2.0) -> None:
        """Beendet Queue und Laufzeit-Thread; Fehler dürfen den Join nicht überspringen."""
        with self._lock:
            self._shutdown = True
            self._running = False
            elements = [*self._active, *self._queue]
            self._active.clear()
            self._queue.clear()
            thread = self._thread

        failure = None
        for element in elements:
            try:
                self._emit(
                    "broadcast.progress",
                    {**element.payload(), "stopped": True},
                )
            except Exception as exc:
                if failure is None:
                    failure = exc

        join_failure = None
        if thread is not None:
            if thread is threading.current_thread():
                join_failure = RuntimeError("Broadcast-Laufzeitthread kann sich nicht selbst beenden")
            else:
                thread.join(None if timeout is None else max(0.0, timeout))
                if thread.is_alive():
                    join_failure = RuntimeError("Broadcast-Laufzeitthread ist noch aktiv")

        if join_failure is not None:
            if failure is not None:
                raise join_failure from failure
            raise join_failure
        if failure is not None:
            raise RuntimeError("Broadcast-Shutdown konnte nicht alle Stopereignisse senden") from failure

    # -- Laufzeit ------------------------------------------------------------

    def _start_thread(self) -> None:
        with self._lock:
            if self._shutdown:
                raise RuntimeError("Broadcast-Manager ist bereits beendet")
            if self._running:
                return
            self._running = True
            thread = threading.Thread(
                target=self._loop,
                daemon=True,
                name="broadcast-queue",
            )
            self._thread = thread
            try:
                thread.start()
            except Exception:
                self._running = False
                self._thread = None
                raise

    def _loop(self) -> None:  # pragma: no cover - Zeit-Thread, in Tests manuell getaktet
        last_progress = 0.0
        tick_count = 0
        try:
            while True:
                with self._lock:
                    if not self._running:
                        return

                now = time.monotonic()
                self._promote_from_queue()

                with self._lock:
                    active = list(self._active)
                progress_due = now - last_progress >= PROGRESS_EVENT_EVERY_S
                for element in active:
                    with self._lock:
                        if not self._running or element not in self._active:
                            continue
                    try:
                        for _ in range(DRAWS_PER_TICK):
                            self._resonance_draw(element)
                        if progress_due:
                            self._emit_progress_if_active(element)
                        if element.progress >= 1.0:
                            self._finish(element)
                    except Exception as exc:  # noqa: BLE001 - ein Element darf die Queue nicht vergiften
                        self._fail(element, exc)

                if progress_due:
                    last_progress = now
                tick_count += 1
                if tick_count % 20 == 0 and self._on_tick is not None:
                    # 1-Sekunden-Takt für den Auto-Modus-Regelkreis
                    try:
                        self._on_tick()
                    except Exception:  # noqa: BLE001 - Regelfehler dürfen Broadcasts nicht killen
                        pass
                time.sleep(TICK_SECONDS)
                keep = self._keep_alive is not None and self._keep_alive()
                with self._lock:
                    if not self._running:
                        return
                    if not self._active and not self._queue and not keep:
                        self._running = False
                        return
        finally:
            with self._lock:
                if self._thread is threading.current_thread():
                    self._running = False

    def _promote_from_queue(self) -> None:
        with self._lock:
            if self._shutdown:
                return
            capacity = self._capacity() if self._capacity else MAX_ACTIVE
            if type(capacity) is not int or not 1 <= capacity <= MAX_ACTIVE:
                raise BroadcastError("Ungültige Queue-Grenze")
            while self._queue and len(self._active) < capacity:
                element = self._queue.popleft()
                element.start = time.monotonic()
                self._active.append(element)
                self._emit(
                    "broadcast.progress",
                    {**element.payload(), "progress": 0.0, "started": True},
                )

    def _stop_current_element(self) -> None:
        with self._lock:
            if not self._active:
                return
            element = self._active.pop(0)
            self._emit(
                "broadcast.progress",
                {**element.payload(), "stopped": True},
            )

    def _stop_all_elements(self) -> None:
        with self._lock:
            elements = [*self._active, *self._queue]
            self._active.clear()
            self._queue.clear()
            for element in elements:
                self._emit(
                    "broadcast.progress",
                    {**element.payload(), "stopped": True},
                )

    def _emit_progress_if_active(self, element: BroadcastElement) -> None:
        with self._lock:
            if self._shutdown or element not in self._active:
                return
        self._checkpoint_entropy(element)
        with self._lock:
            if self._shutdown or element not in self._active:
                return
            self._emit(
                "broadcast.progress",
                {
                    **element.payload(),
                    "progress": round(element.progress, 4),
                },
            )

    def _fail(self, element: BroadcastElement, error: Exception) -> None:
        with self._lock:
            if self._shutdown or element not in self._active:
                return
            self._active.remove(element)
            self._record_abort([element])
            self._emit(
                "broadcast.progress",
                {
                    **element.payload(),
                    "failed": True,
                    "error": type(error).__name__,
                },
            )

    def _finish(self, element: BroadcastElement) -> None:
        # Finish/Stop share this lock: no late child can survive stop_all.
        with self._lock:
            if self._shutdown or element not in self._active:
                return
            decision = None
            child = None
            policy = element.execution_policy
            if policy is not None and policy.dynamic_enabled:
                provider = element.entropy_provider or self._entropy
                gv = check_general_vitality(provider)
                seconds = policy.followup_seconds(gv)
                decision = {"parentBroadcastId": element.broadcast_id,
                            "parentJobId": element.target.payload()["jobId"],
                            "rootJobId": policy.payload()["rootJobId"],
                            "depth": policy.payload()["depth"],
                            "referenceGv": policy.payload()["referenceGv"],
                            "measuredGv": gv, "seconds": seconds,
                            "reason": "followup" if seconds is not None else "comparison-complete",
                            "childJobId": None}
                if seconds is not None:
                    previous = element.target.payload()
                    child = BroadcastTarget.capture(scope=ScopeContext(**previous["scope"]),
                        source=previous["source"],snapshot=previous["contextSnapshot"],
                        legacy=previous["binding"]=="legacy-unbound",procedure=previous["procedure"],
                        entropy_mode=previous["entropyMode"])
                    decision["childJobId"] = child.payload()["jobId"]
            self._checkpoint_entropy(element)
            if decision is not None:
                if self._on_adjustment is not None:
                    self._on_adjustment(decision)
                self._emit("broadcast.adjustment", decision)
            self._active.remove(element)
            self._emit("broadcast.progress", {**element.payload(), "progress": 1.0,
                       "resonanceCount": element.resonance_count, "finished": True})
            if child is not None:
                try:
                    self.enqueue(element.signature, decision["seconds"], element.multiplier,
                        clear=element.clear,delay_ms=element.delay_ms,repeat=element.repeat,
                        target=child,execution_policy=policy.child(decision["parentJobId"],decision["seconds"]))
                except Exception:
                    decision = {**decision,"reason":"followup-not-accepted"}
                    if self._on_adjustment is not None:self._on_adjustment(decision)
                    self._emit("broadcast.adjustment",decision)
                    logging.getLogger(__name__).exception("Begrenzter Folgeauftrag konnte nicht angenommen werden")

    # -- Resonanz (BroadcastElement.paintOneLayer, Zeile 207-226) ------------

    def _resonance_draw(self, element: BroadcastElement) -> None:
        with self._lock:
            if self._shutdown or element not in self._active:
                return
        provider = element.entropy_provider or self._entropy
        bound = RESONANCE_BASE + element.multiplier
        if provider.get_integer(0, bound - 1) != bound - 1:
            return
        binaural = self._binaural_params(provider)
        self._checkpoint_entropy(element)
        with self._lock:
            if self._shutdown or element not in self._active:
                return
            element.resonance_count += 1
            self._resonance_totals[element.signature] = (
                self._resonance_totals.get(element.signature, 0) + 1
            )
            self._emit(
                "broadcast.resonance",
                {
                    **element.payload(),
                    "resonanceCount": element.resonance_count,
                    "binaural": binaural,
                    "source": "simulated",
                },
            )

    def _binaural_params(self, entropy: EntropyProvider | None = None) -> dict[str, float]:
        """BroadcastElement.playBinauralSound, Zeile 292-294 — exakte Formeln."""
        provider = entropy or self._entropy
        left_freq = BINAURAL_BASE_FREQ + provider.get_integer(0, BINAURAL_MAX_OFFSET - 1)
        right_freq = left_freq + provider.get_integer(0, BINAURAL_BEAT_MAX - 1)
        volume = 0.1 + provider.get_integer(0, BINAURAL_VOLUME_STEPS - 1) * 0.1
        return {"left_freq": left_freq, "right_freq": right_freq, "volume": round(volume, 1)}

