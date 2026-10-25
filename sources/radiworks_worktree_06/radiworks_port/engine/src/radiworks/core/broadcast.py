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


@dataclass
class BroadcastElement:
    signature: str
    seconds: int
    multiplier: int = 1
    clear: bool = False
    delay_ms: int = DEFAULT_DELAY_MS
    repeat: int = DEFAULT_REPEAT
    start: float = field(default_factory=lambda: time.monotonic())
    resonance_count: int = 0

    @property
    def elapsed(self) -> float:
        return time.monotonic() - self.start

    @property
    def progress(self) -> float:
        if self.seconds <= 0:
            return 1.0
        return min(1.0, self.elapsed / self.seconds)


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
        self._stop_current = threading.Event()
        self._stop_all = threading.Event()
        self._running = False
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
        element = BroadcastElement(
            signature=signature,
            seconds=seconds,
            multiplier=multiplier,
            clear=clear,
            delay_ms=delay_ms,
            repeat=repeat,
        )
        with self._lock:
            self._queue.append(element)
            queued = len(self._queue)
        # VirtualEmitter: die komplette LED-Choreografie als Event ausliefern
        # (Original: BroadCastService.broadcastNow, hier ereignisbasiert).
        self._emit(
            "emitter.sequence",
            {
                "signature": signature,
                "clear": clear,
                "delayMs": delay_ms,
                "repeat": repeat,
                "steps": [s.to_dict() for s in emitter_sequence(signature, clear=clear, delay_ms=delay_ms, repeat=repeat)],
            },
        )
        self._start_thread()
        return {
            "signature": signature,
            "seconds": seconds,
            "multiplier": multiplier,
            "clear": clear,
            "delayMs": delay_ms,
            "repeat": repeat,
            "queued": queued,
        }

    def stop_current(self) -> None:
        self._stop_current.set()

    def stop_all(self) -> None:
        self._stop_all.set()

    def queue_state(self) -> dict[str, Any]:
        with self._lock:
            return {
                "queued": [
                    {"signature": e.signature, "seconds": e.seconds, "multiplier": e.multiplier}
                    for e in self._queue
                ],
                "active": [
                    {
                        "signature": e.signature,
                        "seconds": e.seconds,
                        "multiplier": e.multiplier,
                        "progress": round(e.progress, 4),
                        "resonanceCount": e.resonance_count,
                    }
                    for e in self._active
                ],
                "resonanceTotals": dict(self._resonance_totals),
            }

    # -- Laufzeit ------------------------------------------------------------

    def _start_thread(self) -> None:
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True, name="broadcast-queue")
        self._thread.start()

    def _loop(self) -> None:  # pragma: no cover - Zeit-Thread, in Tests manuell getaktet
        last_progress = 0.0
        tick_count = 0
        while self._running:
            now = time.monotonic()
            self._stop_current.clear()
            self._promote_from_queue()

            if self._stop_all.is_set():
                self._stop_all_elements()
                self._stop_all.clear()

            for element in list(self._active):
                for _ in range(DRAWS_PER_TICK):
                    self._resonance_draw(element)
                if now - last_progress >= PROGRESS_EVENT_EVERY_S:
                    self._emit(
                        "broadcast.progress",
                        {"signature": element.signature, "progress": round(element.progress, 4)},
                    )
                if element.progress >= 1.0:
                    self._finish(element)

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
            if not self._active and not self._queue and not keep:
                self._running = False

    def _promote_from_queue(self) -> None:
        with self._lock:
            limit = MAX_ACTIVE
            while self._active and len(self._active) >= limit:
                return
            while self._queue and len(self._active) < limit:
                element = self._queue.popleft()
                self._active.append(element)
                self._emit(
                    "broadcast.progress",
                    {"signature": element.signature, "progress": 0.0, "started": True},
                )

    def _stop_all_elements(self) -> None:
        with self._lock:
            for element in self._active:
                self._emit("broadcast.progress", {"signature": element.signature, "stopped": True})
            self._active.clear()

    def _finish(self, element: BroadcastElement) -> None:
        with self._lock:
            if element in self._active:
                self._active.remove(element)
        self._emit(
            "broadcast.progress",
            {
                "signature": element.signature,
                "progress": 1.0,
                "resonanceCount": element.resonance_count,
                "finished": True,
            },
        )

    # -- Resonanz (BroadcastElement.paintOneLayer, Zeile 207-226) ------------

    def _resonance_draw(self, element: BroadcastElement) -> None:
        bound = RESONANCE_BASE + element.multiplier
        if self._entropy.get_integer(0, bound - 1) != bound - 1:
            return
        element.resonance_count += 1
        self._resonance_totals[element.signature] = (
            self._resonance_totals.get(element.signature, 0) + 1
        )
        self._emit(
            "broadcast.resonance",
            {
                "signature": element.signature,
                "resonanceCount": element.resonance_count,
                "binaural": self._binaural_params(),
                "source": "simulated",
            },
        )

    def _binaural_params(self) -> dict[str, float]:
        """BroadcastElement.playBinauralSound, Zeile 292-294 — exakte Formeln."""
        left_freq = BINAURAL_BASE_FREQ + self._entropy.get_integer(0, BINAURAL_MAX_OFFSET - 1)
        right_freq = left_freq + self._entropy.get_integer(0, BINAURAL_BEAT_MAX - 1)
        volume = 0.1 + self._entropy.get_integer(0, BINAURAL_VOLUME_STEPS - 1) * 0.1
        return {"left_freq": left_freq, "right_freq": right_freq, "volume": round(volume, 1)}
