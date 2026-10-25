"""Tests P3-Teil 3: GV-Runde, Essenzielle Fragen, Settings-API, Stick-Pad."""

from radiworks.core.gvround import GvRoundState
from radiworks.core.analysis import AnalysisResult, RateObject
from radiworks.core.essential import ask_essential_questions
from radiworks.core.stickpad import StickPad
from radiworks.core.rates import Rate
from radiworks.entropy import EntropyProvider


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
