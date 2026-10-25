import pytest

from app.algorithms.resonance_engine import ResonanceMatrixEngine

def test_engine_smoke():
    """Basic one-shot resonance calculation should return a 12x12 matrix and score."""
    engine = ResonanceMatrixEngine(use_cuda=False)
    client_data = {
        "first_name": "Unit",
        "last_names": ["Test"],
        "birth_date": "2000-01-01",
        "birth_place": "Berlin"
    }
    result = engine.calculate_resonance(client_data, "Test Fokus")

    assert isinstance(result["matrix_12x12"], list)
    assert len(result["matrix_12x12"]) == 12
    assert all(len(row) == 12 for row in result["matrix_12x12"])
    assert 0.0 <= result["resonance_score"] <= 1.0
