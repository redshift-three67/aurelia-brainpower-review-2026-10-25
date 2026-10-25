"""Tests P3-Teil 3: GV-Runde, Essenzielle Fragen, Settings-API, Stick-Pad."""

from radiworks.core.gvround import GvRoundState
from radiworks.core.analysis import AnalysisResult, RateObject
from radiworks.core.essential import ask_essential_questions
from radiworks.core.stickpad import StickPad
from radiworks.core.rates import Rate
from radiworks.entropy import EntropyProvider
import pytest


def _result(n: int = 5) -> AnalysisResult:
    return AnalysisResult(rate_objects=[RateObject(energetic_value=100 - i, name_or_rate=f"R{i}") for i in range(n)])


def test_gvround_first_draw_sets_case_gv():
    state = GvRoundState(result=_result())
    snap = state.step(EntropyProvider(seed=11))
    assert snap["counter"] == 1
    assert snap["generalVitality"] == snap["gv"]
    assert snap["rateIndex"] is None
    # Raten noch unberührt nach dem ersten (Fall-)Zug
    assert all(r.gv == 0 for r in state.result.rate_objects)


def test_gvround_assigns_rates_and_recurring():
    state = GvRoundState(result=_result(3))
    state.step(EntropyProvider(seed=1))
    seed_pool = iter(range(100, 200))
    for _ in range(3):
        state.step(EntropyProvider(seed=next(seed_pool)))
    assert state.counter == 4
    assert state.total_runs == 4
    gv_values = [r.gv for r in state.result.rate_objects]
    assert all(v > 0 for v in gv_values)
    # recurringGeneralVitality = Häufigkeit des eigenen GV-Werts (mindestens 1)
    assert all(r.recurring_general_vitality >= 1 for r in state.result.rate_objects)


def test_gvround_clean_resets_after_21():
    state = GvRoundState(result=_result(3))
    state.counter = 22  # erzwungen Rundenende beim nächsten Zug
    for r in state.result.rate_objects:
        r.gv = 555
    state.step(EntropyProvider(seed=3))
    assert state.counter == 1
    assert all(r.gv == 0 for r in state.result.rate_objects)


def test_gvround_deterministic():
    def run():
        state = GvRoundState(result=_result(4))
        for seed in (7, 8, 9):
            state.step(EntropyProvider(seed=seed))
        return state.result.to_dict(), state.general_vitality

    assert run() == run()


def test_essential_questions_structure_and_copyguard():
    report = ask_essential_questions(EntropyProvider(seed=42))
    assert report.startswith("== ESSENZIELLE FRAGEN ==")
    assert "Angemessenheit?" in report
    assert "Darf ich mit dieser Person arbeiten?" in report
    verdict, _ = __import__("radiworks").copyguard.check_text(report)
    assert verdict == "allow"


def test_stickpad_deterministic_mapping():
    """Exakte Java-Random-Abbildung: Rate = Random(x), Wert = Random(y)+1."""
    from radiworks.core.javaprng import JavaRandom

    rates = [Rate(name=f"RATE{i}") for i in range(50)]
    pad = StickPad()
    pad.add_position(640, 400)
    pad.add_position(120, 80)
    result = pad.analyze(rates)

    expected: dict[str, int] = {}
    for x, y in [(640, 400), (120, 80)]:
        rate = rates[JavaRandom(x).next_int(50)]
        expected[rate.name] = expected.get(rate.name, 0) + JavaRandom(y).next_int(10) + 1
    got = {r.name_or_rate: r.energetic_value for r in result.rate_objects}
    assert got == expected
    assert pad.positions == []  # Analyse verbraucht die Positionen


def test_stickpad_gv_consumes_positions_on_bonus():
    pad = StickPad()
    for i in range(40):
        pad.add_position(10_000 + i * 37, 500 + i * 11)
    gv = pad.check_general_vitality()
    assert gv is not None and gv > 0
    assert pad.positions == []


def test_stickpad_original_mode_records_capture_time_and_matches_java_seeds(tmp_path):
    from radiworks.core.javaprng import JavaRandom

    state_file = tmp_path / "stickpad.json"
    captured_ms = 1_700_000_000_123
    pad = StickPad(storage_path=state_file, clock_ms=lambda: captured_ms)
    assert pad.add_position(640, 400, mode="original") == 1
    assert pad.status()["positions"][0] == {
        "x": 640, "y": 400, "seedX": 640 + captured_ms,
        "seedY": 400 + captured_ms, "capturedAtMs": captured_ms,
        "mode": "original",
    }
    with pytest.raises(ValueError, match="Modus"):
        pad.add_position(120, 80, mode="reproducible")
    assert len(pad.positions) == 1

    restored = StickPad(storage_path=state_file, clock_ms=lambda: captured_ms + 1000)
    rates = [Rate(name=f"RATE{i}") for i in range(50)]
    result = restored.analyze(rates)
    # Unabhaengiges Java-24-Orakel: Random(1700000000763).nextInt(50)=49,
    # Random(1700000000523).nextInt(10)+1=7.
    assert JavaRandom(640 + captured_ms).next_int(50) == 49
    assert JavaRandom(400 + captured_ms).next_int(10) + 1 == 7
    expected_rate = rates[49]
    expected_value = 7
    assert [(r.name_or_rate, r.energetic_value) for r in result.rate_objects] == [
        (expected_rate.name, expected_value)
    ]
    assert restored.status()["positions"] == []
    assert restored.status()["lastReceipt"]["positions"][0]["capturedAtMs"] == captured_ms
    assert StickPad(storage_path=state_file).status()["lastReceipt"] == restored.status()["lastReceipt"]


def test_stickpad_matches_original_29_jar_for_three_fixed_positions():
    # Original-JAR: StickPadPosition.x/y wurden nach Konstruktion auf feste Seeds gesetzt.
    rates = [Rate(name=f"Synthetic {name}") for name in (
        "Alpha", "Beta", "Gamma", "Delta", "Epsilon",
    )]
    pad = StickPad(clock_ms=lambda: 1_700_000_000_123)
    for x, y in ((640, 400), (140, 80), (1300, 990)):
        pad.add_position(x, y, mode="original")
    result = pad.analyze(rates)
    assert [(rate.name_or_rate, rate.energetic_value) for rate in result.rate_objects] == [
        ("Synthetic Beta", 10), ("Synthetic Epsilon", 7), ("Synthetic Delta", 4),
    ]
    assert pad.positions == []


def test_stickpad_gv_matches_original_29_jar_first_ui_measurement():
    pad = StickPad(clock_ms=lambda: 1_700_000_000_123)
    for x, y in ((640, 400), (140, 80), (1300, 990)):
        pad.add_position(x, y, mode="original")
    assert pad.check_general_vitality() == 602
    assert pad.positions == []


def test_stickpad_reproducible_default_remains_stable_after_restart(tmp_path):
    state_file = tmp_path / "stickpad.json"
    pad = StickPad(storage_path=state_file, clock_ms=lambda: 1)
    pad.add_position(640, 400)
    assert pad.status()["positions"][0]["seedX"] == 640
    assert pad.status()["positions"][0]["capturedAtMs"] is None
    restored = StickPad(storage_path=state_file, clock_ms=lambda: 999)
    assert restored.status()["mode"] == "reproducible"
    assert restored.status()["positions"][0]["seedX"] == 640


def test_stickpad_failed_persistence_keeps_pending_positions(tmp_path, monkeypatch):
    import radiworks.core.stickpad as stickpad_module

    state_file = tmp_path / "stickpad.json"
    pad = StickPad(storage_path=state_file)
    pad.add_position(10, 20, mode="original")
    before = pad.status()

    def fail_write(*_args, **_kwargs):
        raise OSError("synthetic disk failure")

    monkeypatch.setattr(stickpad_module, "atomic_json_replace", fail_write)
    with pytest.raises(OSError, match="synthetic disk failure"):
        pad.clear()
    assert pad.status() == before
    assert StickPad(storage_path=state_file).status() == before


def test_stickpad_rejects_corrupt_saved_position(tmp_path):
    state_file = tmp_path / "stickpad.json"
    state_file.write_text('{"version":1,"positions":[{}],"receipts":[]}', encoding="utf-8")
    with pytest.raises(ValueError, match="ungueltig"):
        StickPad(storage_path=state_file)


def test_stickpad_all_catalog_receipt_survives_restart(tmp_path):
    state_file = tmp_path / "stickpad.json"
    pad = StickPad(storage_path=state_file)
    pad.add_position(10, 20)
    _, receipt = pad.analyze_with_capture([Rate(name="Synthetic Alpha")], selector="")
    assert receipt["catalog"]["selector"] == ""
    restored = StickPad(storage_path=state_file)
    assert restored.status()["lastReceipt"] == receipt


def test_stickpad_rejects_malformed_catalog_binding(tmp_path):
    state_file = tmp_path / "stickpad.json"
    pad = StickPad(storage_path=state_file)
    pad.add_position(10, 20)
    pad.analyze([Rate(name="Synthetic Alpha")])
    import json

    stored = json.loads(state_file.read_text(encoding="utf-8"))
    stored["receipts"][0]["catalog"] = {"selector": "Synthetic", "digest": "not-a-hash"}
    state_file.write_text(json.dumps(stored), encoding="utf-8")
    with pytest.raises(ValueError, match="ungueltig"):
        StickPad(storage_path=state_file)
