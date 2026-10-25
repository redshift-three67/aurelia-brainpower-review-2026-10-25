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

import threading
import time
import uuid
import logging
from collections import deque
from dataclasses import dataclass, field
from typing import Any, Callable

from ..entropy import EntropyProvider
from .emitter import DEFAULT_DELAY_MS, DEFAULT_REPEAT, emitter_sequence

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
        return {
            "broadcastId": self.broadcast_id,
            "signature": self.signature,
            "seconds": self.seconds,
            "multiplier": self.multiplier,
            "clear": self.clear,
            "delayMs": self.delay_ms,
            "repeat": self.repeat,
        }


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
    ) -> None:
        self._entropy = entropy
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
    ) -> dict[str, Any]:
        validate_broadcast_input(signature, seconds, multiplier, delay_ms, repeat)
        element = BroadcastElement(
            signature=signature,
            seconds=seconds,
            multiplier=multiplier,
            clear=clear,
            delay_ms=delay_ms,
            repeat=repeat,
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
            self._queue.append(element)
            try:
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
            element = BroadcastElement(signature, seconds, multiplier)
            steps = [step.to_dict() for step in emitter_sequence(signature)]
            prepared.append((element, steps))
        with self._lock:
            if self._shutdown:
                raise BroadcastError("Broadcast-Manager ist bereits beendet")
            for element, _ in prepared:
                self._queue.append(element)
            try:
                self._start_thread()
                on_accepted([element.broadcast_id for element, _ in prepared])
            except Exception:
                for element, _ in prepared:
                    if element in self._queue:
                        self._queue.remove(element)
                raise
            for element, steps in prepared:
                try:
                    self._emit("emitter.sequence", {**element.payload(), "steps": steps})
                except Exception:
                    logging.getLogger(__name__).exception("Promote-Event konnte nicht zugestellt werden")
            return [element.payload() for element, _ in prepared]

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

    def shutdown(self, timeout: float = 2.0) -> None:
        """Beendet Queue, aktive Elemente und den Laufzeit-Thread begrenzt."""
        with self._lock:
            self._shutdown = True
            self._running = False
            elements = [*self._active, *self._queue]
            self._active.clear()
            self._queue.clear()
            thread = self._thread
            for element in elements:
                self._emit(
                    "broadcast.progress",
                    {**element.payload(), "stopped": True},
                )
        if thread is not None and thread is not threading.current_thread():
            thread.join(max(0.0, timeout))

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
                for element in active:
                    with self._lock:
                        if not self._running or element not in self._active:
                            continue
                    try:
                        for _ in range(DRAWS_PER_TICK):
                            self._resonance_draw(element)
                        if now - last_progress >= PROGRESS_EVENT_EVERY_S:
                            self._emit_progress_if_active(element)
                        if element.progress >= 1.0:
                            self._finish(element)
                    except Exception as exc:  # noqa: BLE001 - ein Element darf die Queue nicht vergiften
                        self._fail(element, exc)

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
            while self._queue and len(self._active) < MAX_ACTIVE:
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
            self._emit(
                "broadcast.progress",
                {
                    **element.payload(),
                    "failed": True,
                    "error": type(error).__name__,
                },
            )

    def _finish(self, element: BroadcastElement) -> None:
        with self._lock:
            if self._shutdown or element not in self._active:
                return
            self._active.remove(element)
            self._emit(
                "broadcast.progress",
                {
                    **element.payload(),
                    "progress": 1.0,
                    "resonanceCount": element.resonance_count,
                    "finished": True,
                },
            )

    # -- Resonanz (BroadcastElement.paintOneLayer, Zeile 207-226) ------------

    def _resonance_draw(self, element: BroadcastElement) -> None:
        with self._lock:
            if self._shutdown or element not in self._active:
                return
        bound = RESONANCE_BASE + element.multiplier
        if self._entropy.get_integer(0, bound - 1) != bound - 1:
            return
        binaural = self._binaural_params()
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

    def _binaural_params(self) -> dict[str, float]:
        """BroadcastElement.playBinauralSound, Zeile 292-294 — exakte Formeln."""
        left_freq = BINAURAL_BASE_FREQ + self._entropy.get_integer(0, BINAURAL_MAX_OFFSET - 1)
        right_freq = left_freq + self._entropy.get_integer(0, BINAURAL_BEAT_MAX - 1)
        volume = 0.1 + self._entropy.get_integer(0, BINAURAL_VOLUME_STEPS - 1) * 0.1
        return {"left_freq": left_freq, "right_freq": right_freq, "volume": round(volume, 1)}
