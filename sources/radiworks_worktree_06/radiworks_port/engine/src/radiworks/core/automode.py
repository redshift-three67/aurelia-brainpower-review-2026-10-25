"""Auto-Modus — 1:1-Port des Harmonisierungsreglers
(GuiElements.handleAutoMode, Zeile 369-418, bytecode-verifiziert).

Original-Verhalten (im draw()-Loop dauerhaft geprüft):
1. Nur bei aktivem Auto-Modus UND leerer Broadcast-Queue.
2. Cooldown: nächster Zyklus frühestens nach aktive² × 111 ms (Calendar-
   Feld 14 = MILLISECOND).
3. Fall-GV ziehen; Serie (max. 180) + Durchschnitt (letzte 10) führen.
4. GV > 300  → nichts zu tun.
5. GV <= 300 → Analyse der gewählten Datenbank (eigener Thread); die ERSTE
   Rate mit gv <= 1400 UND gv <= FallGV + 700 wird gesendet:
   SEKUNDEN = getInteger(10, 1000), Multiplikator aus der UI.

Der Port läuft serverseitig im Broadcast-Takt (Hard Rule 4: Server ist die
Uhr) — der Browser startet nur und zeigt an.
"""

from __future__ import annotations

import threading
import time
from collections import deque
from dataclasses import dataclass, field
from typing import Any, Callable

from ..entropy import EntropyProvider
from .analysis import Rate, analyse_rate_list, check_general_vitality

# Original-Schwellen (Zeile 381-417)
GV_THRESHOLD = 300
GV_SERIES_MAX = 180
GV_AVERAGE_MAX = 10
RATE_GV_CEILING = 1400
AUTO_SECONDS_MIN = 10
AUTO_SECONDS_MAX = 1000
COOLDOWN_MS_PER_ACTIVE = 111


@dataclass
class AutoModeState:
    enabled: bool = False
    database: str = ""
    multiplier: int = 1
    case_gv: int = 0
    runs: int = 0
    series: deque[int] = field(default_factory=lambda: deque(maxlen=GV_SERIES_MAX))
    average: deque[int] = field(default_factory=lambda: deque(maxlen=GV_AVERAGE_MAX))
    _last_analysis: float | None = None
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


class AutoModeController:
    """Regelkreis im Server-Takt; broadcastet selbstständig bei GV <= 300."""

    def __init__(
        self,
        *,
        enqueue: Callable[[str, int, int], None],
        emit: Callable[[str, dict], None],
        find_rates: Callable[[str], list[Rate]],
        analyse: Callable[[list[Rate], EntropyProvider], Any],
        live_entropy: Callable[[], EntropyProvider],
    ) -> None:
        self.state = AutoModeState()
        self._enqueue = enqueue
        self._emit = emit
        self._find_rates = find_rates
        self._analyse = analyse
        self._live_entropy = live_entropy
        self._lock = threading.RLock()

    # -- Steuerung ----------------------------------------------------------

    def start(self, database: str, multiplier: int = 1) -> dict:
        with self._lock:
            self.state.enabled = True
            self.state.database = database
            self.state.multiplier = multiplier
        self._emit("auto.mode", self.state.snapshot())
        return self.state.snapshot()

    def stop(self) -> dict:
        with self._lock:
            self.state.enabled = False
        self._emit("auto.mode", self.state.snapshot())
        return self.state.snapshot()

    # -- Takt (aus dem Broadcast-Manager alle ~1 s gerufen) ------------------

    def tick(self) -> None:
        with self._lock:
            if not self.state.enabled:
                return
            if self.state._analysing:
                return
        now = time.monotonic()
        if self.state._last_analysis is not None:
            active_count = self._active_count()
            cooldown_s = (active_count * active_count * COOLDOWN_MS_PER_ACTIVE) / 1000.0
            if now < self.state._last_analysis + cooldown_s:
                return
        # Schritt 3: Fall-GV ziehen (Original: setGeneralVitality)
        entropy = self._live_entropy()
        self.state.case_gv = check_general_vitality(entropy)
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
            active_count = self._active_count()
            self.state._last_analysis = time.monotonic() + (
                active_count * active_count * COOLDOWN_MS_PER_ACTIVE
            ) / 1000.0
            return
        # Schritt 5: GV <= 300 -> Analyse + Auto-Broadcast (eigener Thread)
        with self._lock:
            if self.state._analysing:
                return
            self.state._analysing = True
        self.state._last_analysis = time.monotonic()

        def analyse_worker() -> None:  # pragma: no cover - Zeit-Thread
            try:
                rates = self._find_rates(self.state.database)
                if not rates:
                    return
                entropy = self._live_entropy()
                result = self._analyse(rates, entropy)
                for rate_object in result.rate_objects:
                    gv_of_rate = check_general_vitality(entropy)
                    if gv_of_rate <= RATE_GV_CEILING and gv_of_rate <= self.state.case_gv + 700:
                        seconds = entropy.get_integer(AUTO_SECONDS_MIN, AUTO_SECONDS_MAX)
                        self._enqueue(rate_object.name_or_rate, seconds, self.state.multiplier)
                        self._emit(
                            "auto.broadcast",
                            {
                                "rate": rate_object.name_or_rate,
                                "seconds": seconds,
                                "multiplier": self.state.multiplier,
                                "gvOfRate": gv_of_rate,
                                "caseGv": self.state.case_gv,
                            },
                        )
                        break
            finally:
                with self._lock:
                    self.state._analysing = False

        threading.Thread(target=analyse_worker, daemon=True, name="automode-analyse").start()

    def _active_count(self) -> int:
        return 0  # wird vom Manager via Callback gesetzt (queue_state)

    def set_active_count_probe(self, probe: Callable[[], int]) -> None:
        self._active_count = probe  # type: ignore[assignment]
