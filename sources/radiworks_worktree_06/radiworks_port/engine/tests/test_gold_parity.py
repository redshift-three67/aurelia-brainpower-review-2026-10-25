"""Goldwert-Parität: Python-Port gegen ORIGINAL-Bytecode (AetherOnePi 2.2.0).

Der Goldwert in tests/gold/gold_analysis_300.json wurde vom unveränderten
Java-Bytecode erzeugt (tools/gold/GoldHarness.java auf de/isuret-Klassen mit
openjdk-24): AnalysisService.analyseRateList, deterministische Zwei-Stufen-
Entropie (Master-Seed 20260829, Hotbit = Seed eines java.util.Random).

Dieser Test repliziert dieselbe Ziehungssequenz bitexakt (JavaRandom-Emulation)
und dieselbe HashMap-Iterationsreihenfolge (javahashmap-Emulation) und fordert
Feld-feld-Gleichheit mit dem Python-Port.
"""

import json
from pathlib import Path

import pytest

from radiworks.core.analysis import Rate, analyse_rate_list
from radiworks.core.javahashmap import java_hashmap_string_order
from radiworks.core.javaprng import JavaRandom

GOLD_FILE = Path(__file__).parent / "gold" / "gold_analysis_300.json"
MASTER_SEED = 20260829
RATE_COUNT = 300
PREFIX = "R"


class GoldEntropy:
    """Zwei-Stufen-Entropie wie GoldHarness: master.nextInt() als Seed."""

    def __init__(self, master_seed: int) -> None:
        self.master = JavaRandom(master_seed)

    def _seed(self) -> int:
        return self.master.next_int32()

    def get_boolean(self) -> bool:
        return JavaRandom(self._seed()).next_boolean()

    def get_integer(self, min_inclusive: int, max_inclusive: int) -> int:
        bound = max_inclusive - min_inclusive + 1
        return min_inclusive + JavaRandom(self._seed()).next_int(bound)

    def get_integer_bound(self, bound: int) -> int:
        return JavaRandom(self._seed()).next_int(bound)


@pytest.fixture(scope="module")
def gold() -> dict:
    return json.loads(GOLD_FILE.read_text(encoding="utf-8"))


def _python_run() -> dict:
    rates = [Rate(name=f"{PREFIX}{i:04d}") for i in range(RATE_COUNT)]
    result = analyse_rate_list(
        rates,
        GoldEntropy(MASTER_SEED),
        max_hits=100,
        key_order=java_hashmap_string_order,
    )
    return result.to_dict()


def test_gold_file_exists(gold: dict):
    assert gold["masterSeed"] == MASTER_SEED
    assert gold["rateCount"] == RATE_COUNT
    assert len(gold["rateObjects"]) == 105


def test_gold_parity_trials(gold: dict):
    python = _python_run()
    assert python["numberOfTrials"] == gold["numberOfTrials"]


def test_gold_parity_rate_objects(gold: dict):
    """Feld-feld-Gleichheit inkl. Reihenfolge (Sortierung + Stabilität)."""
    python = _python_run()
    assert len(python["rateObjects"]) == len(gold["rateObjects"])
    for index, (py, ja) in enumerate(zip(python["rateObjects"], gold["rateObjects"])):
        assert py["nameOrRate"] == ja["nameOrRate"], f"Position {index}"
        assert py["energeticValue"] == ja["energeticValue"], f"{py['nameOrRate']}"
        assert py["url"] == ja["url"]
        assert py["gv"] == ja["gv"]
        assert py["recurring"] == ja["recurring"]
        assert py["recurringGeneralVitality"] == ja["recurringGeneralVitality"]
        assert py["level"] == ja["level"], f"{py['nameOrRate']}"
        assert py["potency"] == ja["potency"], f"{py['nameOrRate']}"
        assert py["resonateCounter"] == ja["resonateCounter"]


def test_gold_parity_general_vitality_untouched(gold: dict):
    """analyseRateList setzt generalVitality nicht (beide Seiten null)."""
    python = _python_run()
    assert python["generalVitality"] is None and gold["generalVitality"] is None
