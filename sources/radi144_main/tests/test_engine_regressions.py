import torch
import pytest

from app.algorithms.resonance_engine import ResonanceMatrixEngine


class _StopAfterRandint(RuntimeError):
    pass


def _client_data(birth_date: str = "2000-01-01"):
    return {
        "first_name": "Regression",
        "last_names": ["Suite"],
        "birth_date": birth_date,
        "birth_place": "Berlin",
    }


def test_default_palette_fallback_returns_color_grid():
    engine = ResonanceMatrixEngine(use_cuda=False)
    result = engine.calculate_resonance(
        _client_data(),
        "Test Fokus",
        calculation_mode="precision",
        palette=None,
    )

    colors = result["matrix_colors"]
    assert len(colors) == 12
    assert all(len(row) == 12 for row in colors)
    assert all(cell.startswith("#") for row in colors for cell in row)


def test_precision_seed_uses_birth_date():
    engine = ResonanceMatrixEngine(use_cuda=False)

    result_a = engine.calculate_resonance(
        _client_data("2000-01-01"),
        "Identischer Fokus",
        calculation_mode="precision",
    )
    result_b = engine.calculate_resonance(
        _client_data("2001-01-01"),
        "Identischer Fokus",
        calculation_mode="precision",
    )

    assert result_a["matrix_data"] != result_b["matrix_data"]


def test_precision_cpu_guard_reduces_candidates_when_available_ram_is_low(monkeypatch):
    engine = ResonanceMatrixEngine(use_cuda=False)
    engine.candidate_count = 150000

    recorded = {}

    class _VirtualMemory:
        available = 64 * 1024 * 1024

    def fake_randint(low, high, size, device=None):
        recorded["candidate_count"] = size[0]
        raise _StopAfterRandint()

    monkeypatch.setattr("psutil.virtual_memory", lambda: _VirtualMemory())
    monkeypatch.setattr(torch, "randint", fake_randint)

    with pytest.raises(_StopAfterRandint):
        engine._find_optimal_matrix_cuda(
            torch.zeros(256),
            torch.zeros(256),
            size=12,
        )

    assert recorded["candidate_count"] < 150000


def test_precision_cpu_guard_keeps_major_tensor_estimate_within_budget(monkeypatch):
    engine = ResonanceMatrixEngine(use_cuda=False)
    engine.candidate_count = 150000

    class _VirtualMemory:
        available = 5 * 1024 * 1024 * 1024

    monkeypatch.setattr("psutil.virtual_memory", lambda: _VirtualMemory())

    limited = engine._limit_candidates_for_available_memory(150000, size=12, embed_dim=256)

    budget_bytes = min(int(_VirtualMemory.available * 0.25), 160 * 1024 * 1024)
    candidate_matrix_bytes = limited * 12 * 12 * 4
    projection_bytes = limited * 256 * 4
    similarity_bytes = limited * 4
    estimated_major_tensors = candidate_matrix_bytes + projection_bytes + similarity_bytes

    assert limited < 150000
    assert estimated_major_tensors <= budget_bytes


def test_precision_restores_torch_rng_state():
    engine = ResonanceMatrixEngine(use_cuda=False)

    torch.manual_seed(123456)
    rng_state_before = torch.get_rng_state()

    _ = engine.calculate_resonance(
        _client_data(),
        "RNG Zustand",
        calculation_mode="precision",
    )

    rng_state_after = torch.get_rng_state()
    assert torch.equal(rng_state_before, rng_state_after)


def test_chakra_focus_populates_bio_info():
    engine = ResonanceMatrixEngine(use_cuda=False)
    result = engine.calculate_resonance(
        _client_data(),
        "Muladhara Wurzelchakra Ausgleich",
        calculation_mode="precision",
    )

    assert result["bio_info"] is not None
    assert result["bio_info"]["type"] == "chakra"


def test_chakra_spectrum_palette_has_all_digits():
    engine = ResonanceMatrixEngine(use_cuda=False)
    palette = engine.generate_chakra_spectrum_palette("Chakra Ausgleich", client_frequency=432.0)

    assert set(palette.keys()) == set(range(10))
    assert all(isinstance(color, str) and color.startswith("#") and len(color) == 7 for color in palette.values())


def test_twilight_balance_palette_has_all_digits():
    engine = ResonanceMatrixEngine(use_cuda=False)
    palette = engine.generate_twilight_balance_palette("Abendruhe", client_frequency=440.0)

    assert set(palette.keys()) == set(range(10))
    assert all(isinstance(color, str) and color.startswith("#") and len(color) == 7 for color in palette.values())
