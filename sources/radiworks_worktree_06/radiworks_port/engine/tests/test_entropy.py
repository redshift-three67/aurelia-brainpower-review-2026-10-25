"""Tests: EntropyProvider — Seed-Determinismus und Fallback-Kette."""

from radiworks.entropy import EntropyProvider


def test_seeded_mode_is_deterministic():
    a = EntropyProvider(seed=42, mode="seeded")
    b = EntropyProvider(seed=42, mode="seeded")
    seq_a = [a.get_integer(0, 999) for _ in range(50)]
    seq_b = [b.get_integer(0, 999) for _ in range(50)]
    assert seq_a == seq_b


def test_different_seeds_diverge():
    a = EntropyProvider(seed=1, mode="seeded")
    b = EntropyProvider(seed=2, mode="seeded")
    seq_a = [a.get_integer(0, 999) for _ in range(20)]
    seq_b = [b.get_integer(0, 999) for _ in range(20)]
    assert seq_a != seq_b


def test_seeded_mode_never_touches_network():
    """Seed-Modus darf random.org nicht kontaktieren (Hard Rule 7, ABI)."""
    provider = EntropyProvider(seed=7, mode="seeded")
    assert provider.status().active_source == "seeded"
    assert "random.org" not in provider.status().chain


def test_get_integer_bounds_inclusive():
    provider = EntropyProvider(seed=5)
    draws = {provider.get_integer(1, 6) for _ in range(500)}
    assert draws <= set(range(1, 7))
    assert draws  # überhaupt gezogen


def test_get_boolean_exists():
    provider = EntropyProvider(seed=9)
    values = {provider.get_boolean() for _ in range(100)}
    assert values <= {True, False}


def test_stochastic_mode_falls_back_to_os():
    """Ohne Netz antwortet random.org nicht -> OS-CSPRNG (fail-forward, kein Crash)."""
    provider = EntropyProvider(seed=None, mode="stochastic")
    provider._random_org._http_get = None  # Netz bewusst entfernt
    value = provider.get_integer(0, 10)
    assert 0 <= value <= 10


def test_invalid_mode_rejected():
    try:
        EntropyProvider(seed=1, mode="quantum")  # type: ignore[arg-type]
    except ValueError:
        return
    raise AssertionError("unbekannter Modus muss abgelehnt werden")
