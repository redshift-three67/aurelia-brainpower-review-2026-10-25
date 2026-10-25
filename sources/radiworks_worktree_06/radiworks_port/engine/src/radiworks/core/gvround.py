"""GV-Runde — Port der General-Vitality-Runde (AetherOneEventHandler,
checkGeneralVitality / setRateGeneralVitality / cleanAnalysisForNewGvCheck,
FUNKTIONSANALYSE §4.3).

Ablauf im Original (Enter-Taste im Tab ANALYZE):
- 1. Zug: GV des Falles; jeder weitere Zug: GV der nächsten Rate
  (Index = gvCounter - 1); dabei recurringGeneralVitality = Häufigkeit
  des jeweiligen GV-Werts über alle Raten.
- Nach 21 Zügen (oder > Ratenzahl): Analyse-GVs zurücksetzen, neue Runde.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .analysis import AnalysisResult, RateObject, check_general_vitality
from ..entropy import EntropyProvider

# Original: gvCounter > 21 beendet die Runde (Event-Handler Zeile 891)
MAX_ROUND_STEPS = 21


@dataclass
class GvRoundState:
    result: AnalysisResult
    general_vitality: int = 0
    counter: int = 0
    total_runs: int = 0
    history: list[dict] = field(default_factory=list)
    entropy: EntropyProvider | None = None  # eigener, fortlaufender Strom der Analyse

    # -- ein GV-Zug -------------------------------------------------------

    def step(self, entropy: EntropyProvider | None = None) -> dict:
        """Ein GV-Zug. Ohne expliziten Provider wird der Analyse-Strom
        fortgesetzt (Original: weitere Züge aus demselben Hotbits-Cache) —
        so ist jeder Zug anders, bei Seed aber replizierbar."""
        provider = entropy or self.entropy
        if provider is None:  # pragma: no cover - wird immer gesetzt
            raise RuntimeError("GvRoundState ohne EntropyProvider")
        if self.counter > MAX_ROUND_STEPS or self.counter > len(self.result.rate_objects):
            self.clean()
        gv = check_general_vitality(provider)
        self.total_runs += 1
        rate_index: int | None = None
        if self.counter == 0:
            self.general_vitality = gv
        else:
            rate_index = self.counter - 1
            self._set_rate_gv(gv)
        self.counter += 1
        self.history.append({"gv": gv, "index": rate_index})
        return self.snapshot(gv, rate_index)

    def _set_rate_gv(self, gv: int) -> None:
        """Event-Handler.setRateGeneralVitality (Zeile 933-963)."""
        index = self.counter - 1
        if index >= len(self.result.rate_objects):
            return
        self.result.rate_objects[index].gv = gv
        # Häufigkeit je GV-Wert über alle befüllten Raten
        occurrences: dict[int, int] = {}
        for rate in self.result.rate_objects:
            if rate.gv == 0:
                continue
            occurrences[rate.gv] = occurrences.get(rate.gv, 0) + 1
        for rate in self.result.rate_objects:
            rate.recurring_general_vitality = (
                occurrences.get(rate.gv, 0) if rate.gv != 0 else 0
            )

    def clean(self) -> None:
        """Event-Handler.cleanAnalysisForNewGvCheck (Zeile 924-931)."""
        self.counter = 0
        for rate in self.result.rate_objects:
            rate.gv = 0
            rate.recurring_general_vitality = 0

    # -- Snapshots ---------------------------------------------------------

    def snapshot(self, last_gv: int | None = None, rate_index: int | None = None) -> dict:
        return {
            "gv": last_gv,
            "generalVitality": self.general_vitality,
            "counter": self.counter,
            "totalRuns": self.total_runs,
            "rateIndex": rate_index,
            "result": self.result.to_dict(),
        }

    def state_dict(self) -> dict:
        return {
            "generalVitality": self.general_vitality,
            "counter": self.counter,
            "totalRuns": self.total_runs,
            "rounds": len(self.history),
        }
