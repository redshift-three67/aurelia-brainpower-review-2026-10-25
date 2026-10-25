"""Analyse-Kern — 1:1-Port der AetherOnePi-Algorithmen.

Referenz: Radiworks/docs/FUNKTIONSANALYSE.md §4 (AnalysisService.java,
bytecode-verifiziert). Jede Funktion nennt die Java-Zeile ihrer Logik.

Bewusste, dokumentierte Abweichung: Java HashMap hat keine stabile
Iterationsreihenfolge; hier gilt Einfuegereihenfolge (Python dict). Die
algorithmische Verteilung bleibt identisch, die Auswertung ist sogar
deterministischer als im Original.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from ..entropy import EntropyProvider

# AnalysisService.MAX_RATELIST_SIZE
MAX_RATELIST_SIZE = 5000
# AnalysisResult.sort().shorten(105)
RESULT_LIMIT = 105

POTENCY_TYPES = ("D", "C", "LM", "Q", "FLUX")
POTENCY_STRENGTH_D = (0, 1, 3, 4, 6, 12, 30, 200)
POTENCY_STRENGTH_C_FLUX = (0, 1, 3, 6, 12, 30, 200, 1000, 10000, 50000, 100000, 1000000)


@dataclass
class Rate:
    """Java de.isuret.polos.AetherOnePi.domain.Rate (nur die genutzten Felder)."""

    name: str
    url: str | None = None
    source_name: str | None = None


@dataclass
class RateObject:
    """Java domain.RateObject — Feldfolge exakt (FUNKTIONSANALYSE §7.1)."""

    energetic_value: int = 0
    name_or_rate: str = ""
    url: str | None = None
    gv: int = 0
    recurring: int = 0
    recurring_general_vitality: int = 0
    level: int = 0
    potency: str | None = None
    resonate_counter: int = 0

    def to_dict(self) -> dict:
        return {
            "energeticValue": self.energetic_value,
            "nameOrRate": self.name_or_rate,
            "url": self.url,
            "gv": self.gv,
            "recurring": self.recurring,
            "recurringGeneralVitality": self.recurring_general_vitality,
            "level": self.level,
            "potency": self.potency,
            "resonateCounter": self.resonate_counter,
        }


@dataclass
class AnalysisResult:
    """Java domain.AnalysisResult."""

    rate_objects: list[RateObject] = field(default_factory=list)
    general_vitality: int | None = None
    number_of_trials: int | None = None

    @classmethod
    def from_dict(cls, data: dict) -> "AnalysisResult":
        """Rekonstruktion aus dem JSON-Contract (Sessions in Cases)."""
        key_map = {
            "energeticValue": "energetic_value",
            "nameOrRate": "name_or_rate",
            "url": "url",
            "gv": "gv",
            "recurring": "recurring",
            "recurringGeneralVitality": "recurring_general_vitality",
            "level": "level",
            "potency": "potency",
            "resonateCounter": "resonate_counter",
        }
        rate_objects = [
            RateObject(**{key_map[k]: v for k, v in raw.items() if k in key_map})
            for raw in data.get("rateObjects", [])
        ]
        return cls(
            rate_objects=rate_objects,
            general_vitality=data.get("generalVitality"),
            number_of_trials=data.get("numberOfTrials"),
        )

    def sort(self) -> "AnalysisResult":
        # AnalysisResult.sort(): energeticValue desc, Gleichstand nameOrRate asc
        self.rate_objects.sort(key=lambda r: (-r.energetic_value, r.name_or_rate))
        return self

    def shorten(self, max_size: int) -> "AnalysisResult":
        del self.rate_objects[max_size:]
        return self

    def to_dict(self) -> dict:
        return {
            "generalVitality": self.general_vitality,
            "numberOfTrials": self.number_of_trials,
            "rateObjects": [r.to_dict() for r in self.rate_objects],
        }


def clean_rate_name(name: str | None) -> str:
    """Event-Handler.cleanRateName + RateUtils.cleanRateName."""
    if not name:
        return "---"
    name = name.replace("æ", "ae").replace("Æ", "Ae").replace("Œ", "Oe")
    return name[:100] if len(name) > 100 else name


def _insert_rate(
    result: AnalysisResult,
    rates_values: dict[str, int],
    rate: str,
    url_by_name: dict[str, str] | None = None,
) -> None:
    """RateUtils.insertRate — Name-Format 'NAME\\tURL' (TAB-Trenner).

    Alternativ (Port-Format): die URL steckt im Rate-Objekt (rates.py trennt
    Name/URL beim Parsen) und wird hier über die Nachschlagetabelle vereint.
    """
    parts = rate.split("\t")
    if len(parts) > 1:
        url: str | None = parts[1]
        name = parts[0]
    else:
        url = (url_by_name or {}).get(rate)
        name = rate
    result.rate_objects.append(
        RateObject(energetic_value=rates_values[rate], name_or_rate=name, url=url)
    )


def _shuffle_rate_list(rate_list: list[Rate], entropy: EntropyProvider) -> list[Rate]:
    """AnalysisService.shuffleRateList: Hotbit-Entfernen-Mischen."""
    shuffled: list[Rate] = []
    while rate_list:
        idx = entropy.get_integer(0, len(rate_list) - 1)
        shuffled.append(rate_list.pop(idx))
    return shuffled


def analyse_rate_list(
    rates: list[Rate],
    entropy: EntropyProvider,
    *,
    max_hits: int = 100,
    key_order: "Callable[[list[str]], list[str]] | None" = None,
) -> AnalysisResult:
    """AnalysisService.analyseRateList (FUNKTIONSANALYSE §4, Zeile 49-131).

    max_hits entspricht Settings "analysis.very.high.max.hit": 100 (Default)
    oder 1000.

    key_order (optional): ersetzt die Einfuegereihenfolge der selektierten
    Raten durch eine externe Ordnungsfunktion — fuer den bitidentischen
    Goldwert-Abgleich wird java_hashmap_string_order uebergeben (das Java-
    Original iteriert die HashMap<String,Integer> in Hash-Reihenfolge).
    """
    if max_hits not in (100, 1000):
        raise ValueError("max_hits muss 100 oder 1000 sein (Original-Settings)")

    result = AnalysisResult()
    rate_list: list[Rate] = list(rates)
    url_by_name = {r.name: r.url for r in rate_list if r.url}
    rate_list = _shuffle_rate_list(rate_list, entropy)

    # Selektionsphase: n = size/10, geklemmt auf [120, 5000]
    rates_values: dict[str, int] = {}
    max_n = len(rate_list) // 10
    if max_n > MAX_RATELIST_SIZE:
        max_n = MAX_RATELIST_SIZE
    if max_n < 120:
        max_n = 120

    count = 0
    while rate_list:
        idx = entropy.get_integer(0, len(rate_list) - 1)
        rate = rate_list.pop(idx)
        rates_values[rate.name] = 0  # Duplikat-Name: Wert wird wie im Original auf 0 gesetzt
        count += 1
        if count >= max_n:
            break

    # Anreicherungsphase: +getInteger(10) je Rate, Abbruch bei biggestLevel >= max_hits.
    # Iterationsreihenfolge wie im Java-Original (HashMap) via key_order nachstellbar.
    iteration_order = list(key_order(list(rates_values))) if key_order else list(rates_values)
    biggest_level = 0
    analysis_finished = False
    trials = 0
    while not analysis_finished:
        for rate_name in iteration_order:
            trials += 1
            rates_values[rate_name] += entropy.get_integer(0, 9)
            if rates_values[rate_name] > biggest_level:
                biggest_level = rates_values[rate_name]
            if biggest_level >= max_hits:
                analysis_finished = True
                break

    result.number_of_trials = trials

    for rate_name in iteration_order:
        _insert_rate(result, rates_values, rate_name, url_by_name)

    result.sort().shorten(RESULT_LIMIT)

    for rate_object in result.rate_objects:
        rate_object.potency = analyze_potency(entropy)
        rate_object.level = analyze_level(entropy)

    return result


def analyze_level(entropy: EntropyProvider) -> int:
    """Level 1-12: 12 Faecher, 100 Zuege getInteger(1,12), gate getBoolean(); argmax."""
    levels = {level: 0 for level in range(1, 13)}
    for _ in range(100):
        level = entropy.get_integer(1, 12)
        if entropy.get_boolean():
            levels[level] += 1
    max_value = 0
    chosen = 0
    for level in range(1, 13):
        if levels[level] > max_value:
            max_value = levels[level]
            chosen = level
    return chosen


def analyze_potency(entropy: EntropyProvider) -> str:
    """AnalysisService.analyzePotency (FUNKTIONSANALYSE §4.2)."""
    potencies: list[tuple[str, int]] = []
    for _ in range(100):
        potency_type = POTENCY_TYPES[entropy.get_integer(0, len(POTENCY_TYPES) - 1)]
        if potency_type == "D":
            strength = POTENCY_STRENGTH_D[entropy.get_integer(0, len(POTENCY_STRENGTH_D) - 1)]
        elif potency_type in ("C", "FLUX"):
            strength = POTENCY_STRENGTH_C_FLUX[
                entropy.get_integer(0, len(POTENCY_STRENGTH_C_FLUX) - 1)
            ]
        else:  # LM / Q
            strength = entropy.get_integer(1, 30)
        potencies.append((potency_type, strength))

    potency_choice = [0] * 100
    while True:
        pos = entropy.get_integer(0, 99)
        potency_choice[pos] += 1
        if potency_choice[pos] > 77:
            potency_type, strength = potencies[pos]
            return f"{potency_type} {strength}"


def select_training_rate(rates: list[Rate], entropy: EntropyProvider) -> str:
    """AnalysisService.selectTrainingRate (Zeile 166-170): verdeckte Signatur."""
    return rates[entropy.get_integer(0, len(rates) - 1)].name


def check_general_vitality(entropy: EntropyProvider) -> int:
    """AnalysisService.checkGeneralVitality (FUNKTIONSANALYSE §4.1)."""
    draws = sorted((entropy.get_integer(0, 999) for _ in range(3)), reverse=True)
    gv = draws[0]
    if gv > 950:
        roll = entropy.get_integer(0, 99)
        while roll >= 50:
            gv += roll
            roll = entropy.get_integer(0, 99)
    return gv


def check_percentage(entropy: EntropyProvider) -> int:
    """AetherOneUI.checkPercentage: max aus 3 x getInteger(100)."""
    return max(entropy.get_integer(0, 99) for _ in range(3))


def check_general_vitality_for_analysis(
    result: AnalysisResult, entropy: EntropyProvider
) -> AnalysisResult:
    """AnalysisService.checkGeneralVitalityForAnalysis: GV je Rate."""
    result.general_vitality = check_general_vitality(entropy)
    for rate_object in result.rate_objects:
        rate_object.gv = check_general_vitality(entropy)
    return result


def search_anomaly(width: int, height: int, entropy: EntropyProvider) -> list[int]:
    """AnalysisService.searchAnomaly: width x height GV-Matrix."""
    return [check_general_vitality(entropy) for _ in range(width * height)]
