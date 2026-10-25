"""Tests: Analyse-Kern gegen die Java-Referenzlogik (FUNKTIONSANALYSE §4)."""

from radiworks.core.analysis import (
    AnalysisResult,
    Rate,
    RateObject,
    analyse_rate_list,
    analyze_potency,
    check_general_vitality,
    check_percentage,
    clean_rate_name,
    search_anomaly,
)
from radiworks.entropy import EntropyProvider


def _rates(n: int, with_url: bool = False) -> list[Rate]:
    rates = []
    for i in range(n):
        name = f"RATE {i:04d}"
        rates.append(Rate(name=f"{name}\thttp://x/{i}.htm" if with_url else name))
    return rates


def test_analysis_is_deterministic_with_seed():
    a = analyse_rate_list(_rates(300), EntropyProvider(seed=123), max_hits=100)
    b = analyse_rate_list(_rates(300), EntropyProvider(seed=123), max_hits=100)
    assert a.to_dict() == b.to_dict()


def test_analysis_shape_and_limits():
    result = analyse_rate_list(_rates(2000, with_url=True), EntropyProvider(seed=7))
    assert result.rate_objects, "Es muss ein Ergebnis geben"
    assert len(result.rate_objects) <= 105  # shorten(105)
    assert result.number_of_trials and result.number_of_trials > 0
    top = result.rate_objects[0]
    # sort(): energeticValue absteichend
    values = [r.energetic_value for r in result.rate_objects]
    assert values == sorted(values, reverse=True)
    # URL-Splitting nach TAB (RateUtils.insertRate)
    if top.url:
        assert top.url.startswith("http://x/")
    # Potenz und Level sind gesetzt
    assert top.potency is not None
    assert 1 <= top.level <= 12


def test_analysis_max_hits_1000_allows_higher_values():
    lo = analyse_rate_list(_rates(1500), EntropyProvider(seed=11), max_hits=100)
    hi = analyse_rate_list(_rates(1500), EntropyProvider(seed=11), max_hits=1000)
    max_lo = max(r.energetic_value for r in lo.rate_objects)
    max_hi = max(r.energetic_value for r in hi.rate_objects)
    # Der abbrechende Wert liegt bis zu +8 ueber der Schwelle (+getInteger(0,9));
    # identisch zur Java-Referenz (Abbruchpruefung nach der Erhoehung).
    assert max_lo <= 108
    assert max_hi <= 1008
    assert max_hi > max_lo


def test_general_vitality_bounds():
    for seed in range(10):
        gv = check_general_vitality(EntropyProvider(seed=seed))
        # Basis 0-999; Bonus-Spirale ab 950 kann darueber hinausgehen, gedeckelt im Test auf Plausibilitaet
        assert 0 <= gv < 1500


def test_check_percentage_bounds():
    for seed in range(10):
        p = check_percentage(EntropyProvider(seed=seed))
        assert 0 <= p <= 99


def test_potency_format_and_types():
    valid_types = ("D", "C", "LM", "Q", "FLUX")
    for seed in range(20):
        potency = analyze_potency(EntropyProvider(seed=seed))
        kind, _, strength = potency.partition(" ")
        assert kind in valid_types, potency
        assert strength.lstrip("-").isdigit(), potency


def test_search_anomaly_matrix_size():
    matrix = search_anomaly(3, 4, EntropyProvider(seed=3))
    assert len(matrix) == 12


def test_clean_rate_name():
    assert clean_rate_name("Æthusa") == "Aethusa"
    assert clean_rate_name(None) == "---"
    assert len(clean_rate_name("x" * 250)) == 100


def test_sort_and_shorten():
    result = AnalysisResult(
        rate_objects=[
            RateObject(energetic_value=5, name_or_rate="b"),
            RateObject(energetic_value=5, name_or_rate="a"),
            RateObject(energetic_value=9, name_or_rate="c"),
        ]
    )
    result.sort().shorten(2)
    assert [r.name_or_rate for r in result.rate_objects] == ["c", "a"]
