"""Stick-Pad — 1:1-Port (domain/StickPad.java, FUNKTIONSANALYSE §6).

Original-Mechanik: Zeiger-/Tasten-Positionen (x, y) sammeln; die Analyse
bildet Positionen deterministisch auf Raten ab:
    Rate  = rates[ java.util.Random(x).nextInt(len) ]
    Wert += java.util.Random(y).nextInt(10) + 1
Die Ziehung nutzt die bitexakte JavaRandom-Emulation — gleiche Positionen,
gleiches Ergebnis (reproduzierbar).
"""

from __future__ import annotations

from .analysis import AnalysisResult, Rate, RateObject, check_general_vitality
from ..entropy import EntropyProvider
from .javaprng import JavaRandom


class StickPad:
    def __init__(self) -> None:
        self.positions: list[tuple[int, int]] = []

    def add_position(self, x: int, y: int) -> int:
        self.positions.append((int(x), int(y)))
        return len(self.positions)

    def clear(self) -> int:
        count = len(self.positions)
        self.positions.clear()
        return count

    # -- Analyse (StickPad.analyze) ---------------------------------------

    def analyze(self, rates: list[Rate]) -> AnalysisResult:
        values: dict[str, int] = {}
        url_by_name = {r.name: r.url for r in rates if r.url}
        for x, y in self.positions:
            rate_index = JavaRandom(int(x)).next_int(len(rates))
            rate = rates[rate_index]
            energetic_value = JavaRandom(int(y)).next_int(10) + 1
            values[rate.name] = values.get(rate.name, 0) + energetic_value
        self.positions.clear()
        result = AnalysisResult()
        for name, value in values.items():
            parts = name.split("\t")
            if len(parts) > 1:
                result.rate_objects.append(
                    RateObject(energetic_value=value, name_or_rate=parts[0], url=parts[1])
                )
            else:
                result.rate_objects.append(
                    RateObject(energetic_value=value, name_or_rate=name, url=url_by_name.get(name))
                )
        return result.sort()

    # -- GV (StickPad.checkGeneralVitality, Positionen werden verbraucht) --

    def check_general_vitality(self) -> int | None:
        if not self.positions:
            return None
        draws = sorted((JavaRandom(x).next_int(1000) + 1 for x, _ in self.positions), reverse=True)
        gv = draws[0]
        if gv > 950 and self.positions:
            _, y = self.positions.pop(0)
            roll = JavaRandom(y).next_int(100)
            while roll >= 50 and self.positions:
                gv += roll
                _, y = self.positions.pop(0)
                roll = JavaRandom(y).next_int(100)
        return gv
