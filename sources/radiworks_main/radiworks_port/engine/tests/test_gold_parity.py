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
from fastapi.testclient import TestClient

from radiworks.core.analysis import Rate, analyse_rate_list
from radiworks.core.javahashmap import java_hashmap_string_order
from radiworks.core.javaprng import JavaRandom
from radiworks.entropy import EntropyProvider
from radiworks.main import create_app

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


def _production_run() -> dict:
    rates = [Rate(name=f"{PREFIX}{i:04d}") for i in range(RATE_COUNT)]
    return analyse_rate_list(
        rates,
        EntropyProvider(seed=MASTER_SEED, mode="seeded"),
        max_hits=100,
    ).to_dict()


def test_gold_file_exists(gold: dict):
    assert gold["masterSeed"] == MASTER_SEED
    assert gold["rateCount"] == RATE_COUNT
    assert len(gold["rateObjects"]) == 105


def test_production_entropy_and_order_match_gold_adapter():
    assert _production_run() == _python_run()


def test_rest_analysis_path_matches_gold_fixture(gold: dict, tmp_path: Path):
    data = tmp_path / "data"
    data.mkdir()
    (data / "GOLD.txt").write_text(
        "\n".join(f"{PREFIX}{index:04d}" for index in range(RATE_COUNT)),
        encoding="utf-8",
    )
    app = create_app(base_dir=tmp_path, data_dir=data)

    with TestClient(app) as client:
        response = client.post(
            "/analysis",
            json={"database": "GOLD", "seed": MASTER_SEED, "max_hits": 100},
        )

    assert response.status_code == 200
    result = response.json()["result"]
    assert result["numberOfTrials"] == gold["numberOfTrials"]
    assert result["rateObjects"] == gold["rateObjects"]


@pytest.mark.parametrize(
    ("seed", "max_hits", "fixture_name"),
    [
        (42, 100, "gold_rest_analysis_300_seed_42.json"),
        (20260829, 100, "gold_rest_analysis_300_seed_20260829.json"),
        (42, 1000, "gold_rest_analysis_300_seed_42_max_hits_1000.json"),
    ],
)
def test_rest_seeded_result_matches_original_java_oracle(
    seed: int,
    max_hits: int,
    fixture_name: str,
    tmp_path: Path,
):
    expected = json.loads((GOLD_FILE.parent / fixture_name).read_text(encoding="utf-8"))
    assert expected["oracleVersion"] == "original-java-analysis-v2"
    assert expected["javaVersion"].startswith("24.0.1")
    assert expected["mode"] == "seeded"
    assert expected["maxHits"] == max_hits
    assert expected["includesGeneralVitality"] is True
    data = tmp_path / "data"
    data.mkdir()
    (data / "GOLD.txt").write_text(
        "\n".join(f"{PREFIX}{index:04d}" for index in range(RATE_COUNT)),
        encoding="utf-8",
    )
    app = create_app(base_dir=tmp_path, data_dir=data)

    with TestClient(app) as client:
        response = client.post(
            "/analysis",
            json={
                "database": "GOLD",
                "seed": seed,
                "mode": "seeded",
                "max_hits": max_hits,
            },
        )

    assert response.status_code == 200
    assert response.json()["result"] == {
        "generalVitality": expected["generalVitality"],
        "numberOfTrials": expected["numberOfTrials"],
        "rateObjects": expected["rateObjects"],
    }


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
