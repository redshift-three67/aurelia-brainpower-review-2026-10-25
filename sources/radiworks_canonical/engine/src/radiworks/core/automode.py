"""Auto-Modus — 1:1-Port des Harmonisierungsreglers
(GuiElements.handleAutoMode, Zeile 369-418, bytecode-verifiziert).

Original-Verhalten (im draw()-Loop dauerhaft geprüft):
1. Nur bei aktivem Auto-Modus UND leerer wartender Broadcast-Queue.
2. Aktive Broadcasts sind erlaubt; Cooldown: aktive² × 111 ms (Calendar-
   Feld 14 = MILLISECOND).
3. Fall-GV ziehen; Serie (max. 180) + Durchschnitt (letzte 10) führen.
4. GV > 300  → nichts zu tun.
5. GV <= 300 → Analyse der gewählten Datenbank (eigener Thread); die ERSTE
   Rate außerhalb der übersprungenen Originalgrenzen wird gesendet:
   gv > 1400 ODER gv > FallGV + 700. SEKUNDEN = getInteger(10, 1000),
   Multiplikator aus der UI.

Der Port läuft serverseitig im Broadcast-Takt (Hard Rule 4: Server ist die
Uhr) — der Browser startet nur und zeigt an.
"""

from __future__ import annotations

import threading
import time
from collections import deque
from dataclasses import dataclass, field
from typing import Any, Callable

from .. import copyguard
from ..entropy import EntropyProvider
from .analysis import Rate, check_general_vitality

# Original-Schwellen (Zeile 381-417)
GV_THRESHOLD = 300
GV_SERIES_MAX = 180
GV_AVERAGE_MAX = 10
RATE_GV_CEILING = 1400
AUTO_SECONDS_MIN = 10
AUTO_SECONDS_MAX = 1000
COOLDOWN_MS_PER_ACTIVE = 111


class _StaleAutoGeneration(RuntimeError):
    """Interner Abbruch eines deaktivierten oder ersetzten Analyse-Workers."""


class _GenerationEntropy:
    """Serialisiert Entropiezüge mit Auto-Start/Stop und prüft die Generation."""

    def __init__(
        self,
        controller: AutoModeController,
        generation: int,
        provider: EntropyProvider,
    ) -> None:
        self._controller = controller
        self._generation = generation
        self._provider = provider

    def _checked(self, draw: Callable[[], Any]) -> Any:
        with self._controller._entropy_lock:
            with self._controller._lock:
                if (
                    self._controller._shutdown
                    or self._generation != self._controller._generation
                    or not self._controller.state.enabled
                ):
                    raise _StaleAutoGeneration
            value = draw()
        with self._controller._lock:
            if (
                self._controller._shutdown
                or self._generation != self._controller._generation
                or not self._controller.state.enabled
            ):
                raise _StaleAutoGeneration
        return value

    def get_boolean(self) -> bool:
        return bool(self._checked(self._provider.get_boolean))

    def get_integer(self, min_inclusive: int, max_inclusive: int) -> int:
        return int(
            self._checked(
                lambda: self._provider.get_integer(min_inclusive, max_inclusive)
            )
        )

    def get_integer_bound(self, bound: int) -> int:
        return int(self._checked(lambda: self._provider.get_integer_bound(bound)))


@dataclass
class AutoModeState:
    enabled: bool = False
    database: str = ""
    multiplier: int = 1
    case_gv: int = 0
    runs: int = 0
    series: deque[int] = field(default_factory=lambda: deque(maxlen=GV_SERIES_MAX))
    average: deque[int] = field(default_factory=lambda: deque(maxlen=GV_AVERAGE_MAX))
    _next_analysis_at: float | None = None
    _analysing: bool = False

    def snapshot(self) -> dict[str, Any]:
        avg = round(sum(self.average) / len(self.average)) if self.average else None
        return {
            "enabled": self.enabled,
            "database": self.database,
            "multiplier": self.multiplier,
            "caseGv": self.case_gv,
            "runs": self.runs,
            "seriesLength": len(self.series),
            "average": avg,
        }


def is_auto_broadcast_candidate(gv_of_rate: int, case_gv: int) -> bool:
    """Negation der ``continue``-Bedingung im Original-Bytecode."""
    return gv_of_rate > RATE_GV_CEILING or gv_of_rate > case_gv + 700


class AutoModeController:
    """Regelkreis im Server-Takt; broadcastet selbstständig bei GV <= 300."""

    def __init__(
        self,
        *,
        enqueue: Callable[[str, int, int], dict[str, Any] | None],
        emit: Callable[[str, dict], None],
        find_rates: Callable[[str], list[Rate]],
        analyse: Callable[[list[Rate], EntropyProvider], Any],
        live_entropy: Callable[[], EntropyProvider],
        queue_state: Callable[[], dict[str, Any]],
    ) -> None:
        self.state = AutoModeState()
        self._enqueue = enqueue
        self._emit = emit
        self._find_rates = find_rates
        self._analyse = analyse
        self._live_entropy = live_entropy
        self._queue_state = queue_state
        self._lock = threading.RLock()
        self._entropy_lock = threading.Lock()
        self._generation = 0
        self._worker: threading.Thread | None = None
        self._ticking = False
        self._shutdown = False

    # -- Steuerung ----------------------------------------------------------

    def start(self, database: str, multiplier: int = 1) -> dict[str, Any]:
        with self._lock:
            if self._shutdown:
                raise RuntimeError("Auto-Modus ist bereits beendet")
            self._generation += 1
            self.state.enabled = True
            self.state.database = database
            self.state.multiplier = multiplier
            self.state.case_gv = 0
            self.state.runs = 0
            self.state.series.clear()
            self.state.average.clear()
            snapshot = self.state.snapshot()
            self._emit("auto.mode", snapshot)
            return snapshot

    def stop(self) -> dict[str, Any]:
        with self._lock:
            self._generation += 1
            self.state.enabled = False
            self.state.series.clear()
            snapshot = self.state.snapshot()
            self._emit("auto.mode", snapshot)
            return snapshot

    def shutdown(self, timeout: float = 2.0) -> None:
        """Invalidiert den Regler und wartet begrenzt auf den Analyse-Worker."""
        with self._lock:
            self._generation += 1
            self._shutdown = True
            self.state.enabled = False
            self.state.series.clear()
            worker = self._worker
        if worker is not None and worker is not threading.current_thread():
            worker.join(max(0.0, timeout))

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            return self.state.snapshot()

    # -- Takt (aus dem Broadcast-Manager alle ~1 s gerufen) ------------------

    def tick(self) -> None:
        worker_args: tuple[int, str, int] | None = None
        with self._lock:
            if self._shutdown or not self.state.enabled or self._ticking:
                return

            queue = self._queue_state()
            if queue["queued"]:
                return

            now = time.monotonic()
            if (
                self.state._next_analysis_at is not None
                and now < self.state._next_analysis_at
            ):
                return

            active_count = len(queue["active"])
            cooldown_s = (
                active_count * active_count * COOLDOWN_MS_PER_ACTIVE
            ) / 1000.0
            self.state._next_analysis_at = now + cooldown_s
            generation = self._generation
            self._ticking = True

        try:
            with self._entropy_lock:
                entropy = self._live_entropy()
                case_gv = check_general_vitality(entropy)
        finally:
            with self._lock:
                self._ticking = False

        with self._lock:
            if (
                self._shutdown
                or generation != self._generation
                or not self.state.enabled
            ):
                return

            # Schritt 3: Fall-GV ziehen (Original: setGeneralVitality)
            self.state.case_gv = case_gv
            self.state.runs += 1
            self.state.series.append(self.state.case_gv)
            self.state.average.append(self.state.case_gv)
            self._emit(
                "gv.update",
                {
                    "gv": self.state.case_gv,
                    "runs": self.state.runs,
                    "average": self.state.snapshot()["average"],
                    "source": "auto",
                },
            )

            # Schritt 4: GV > 300 -> Regelkreis zufrieden
            if self.state.case_gv > GV_THRESHOLD:
                return

            # Schritt 5: GV <= 300 -> Analyse + Auto-Broadcast (eigener Thread)
            if self.state._analysing:
                return
            self.state._analysing = True
            worker_args = (
                self._generation,
                self.state.database,
                self.state.multiplier,
            )

        assert worker_args is not None
        thread = threading.Thread(
            target=self._analyse_worker,
            args=worker_args,
            daemon=True,
            name="automode-analyse",
        )
        with self._lock:
            generation = worker_args[0]
            if (
                self._shutdown
                or generation != self._generation
                or not self.state.enabled
            ):
                self.state._analysing = False
                return
            self._worker = thread
            try:
                thread.start()
            except Exception:
                self._worker = None
                self.state._analysing = False
                raise

    def _analyse_worker(
        self,
        generation: int,
        database: str,
        multiplier: int,
    ) -> None:  # pragma: no cover - Zeit-Thread; Verhalten separat getestet
        try:
            rates = self._find_rates(database)
            if not rates:
                return
            entropy = _GenerationEntropy(self, generation, self._live_entropy())
            result = self._analyse(rates, entropy)  # type: ignore[arg-type]
            for rate_object in result.rate_objects:
                gv_of_rate = check_general_vitality(entropy)  # type: ignore[arg-type]
                with self._lock:
                    if generation != self._generation or not self.state.enabled:
                        return
                    case_gv = self.state.case_gv
                    if not is_auto_broadcast_candidate(gv_of_rate, case_gv):
                        continue
                if copyguard.check_text(rate_object.name_or_rate)[0] == "block":
                    with self._lock:
                        if generation != self._generation or not self.state.enabled:
                            return
                        self._generation += 1
                        self.state.enabled = False
                        self._emit(
                            "auto.error",
                            {"phase": "copyguard", "message": "CopyGuard blockt Auto-Broadcast"},
                        )
                        self._emit("auto.mode", self.state.snapshot())
                    return
                seconds = entropy.get_integer(AUTO_SECONDS_MIN, AUTO_SECONDS_MAX)
                with self._lock:
                    if generation != self._generation or not self.state.enabled:
                        return
                    queued = self._enqueue(
                        rate_object.name_or_rate,
                        seconds,
                        multiplier,
                    )
                    payload = {
                        "rate": rate_object.name_or_rate,
                        "seconds": seconds,
                        "multiplier": multiplier,
                        "gvOfRate": gv_of_rate,
                        "caseGv": case_gv,
                    }
                    if queued is not None and queued.get("broadcastId"):
                        payload["broadcastId"] = queued["broadcastId"]
                    self._emit("auto.broadcast", payload)
                break
        except _StaleAutoGeneration:
            pass
        except Exception as exc:  # noqa: BLE001 - Worker darf den Regler nicht blockieren
            with self._lock:
                if generation == self._generation and self.state.enabled:
                    self._emit(
                        "auto.error",
                        {"phase": "analysis", "message": str(exc)},
                    )
        finally:
            with self._lock:
                if self._worker is threading.current_thread():
                    self._worker = None
                self.state._analysing = False
