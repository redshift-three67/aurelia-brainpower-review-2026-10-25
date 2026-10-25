import subprocess
import sys
import warnings

import pytest
from fastapi.testclient import TestClient
from pydantic.warnings import PydanticDeprecatedSince20

from main import app
from app.api import resonance as resonance_api


class _DummySignatureGenerator:
    def generate_signature(self, client_data, use_planetary=False, emf_compensator=None):
        return {"frequency": 440.0, "components": {"dummy": 1.0}}


class _DummyEngine:
    def __init__(self):
        self.emf_active = False
        self.emf_compensator = None
        self.signature_gen = _DummySignatureGenerator()
        self.active_amplifier_id = None
        self.active_amplifier_data = None

    def set_amplifier(self, amplifier_name):
        self.active_amplifier_id = amplifier_name
        self.active_amplifier_data = {
            "name": amplifier_name,
            "base_frequency_hz": 432.0,
            "amplification_factor": 0.5,
            "audio_frequencies": [],
        }
        return self.active_amplifier_data

    def clear_amplifier(self):
        self.active_amplifier_id = None
        self.active_amplifier_data = None

    def calculate_resonance(
        self,
        client_data,
        focus,
        matrix_size=12,
        focus_weight="Normal",
        calculation_mode="quantum",
        hrv_sim=False,
        palette=None,
        emf_compensate=False,
        symmetry="none",
        precomputed_signature=None,
    ):
        size = int(matrix_size or 12)
        matrix = [[(r + c) % 10 for c in range(size)] for r in range(size)]
        score = (sum(ord(ch) for ch in str(focus)) % 1000) / 1000.0
        first_name = client_data.get("first_name", "Standalone")
        last_names = client_data.get("last_names") or [""]
        last_name = last_names[0] if isinstance(last_names, list) else str(last_names)
        signature = precomputed_signature or {"frequency": 440.0, "components": {"dummy": 1.0}}
        return {
            "resonance_score": float(score),
            "intensity": 1.0,
            "matrix_12x12": matrix,
            "matrix_data": matrix,
            "matrix_size": size,
            "matrix_colors": [["#FFFFFF" for _ in range(size)] for _ in range(size)],
            "top_10": [{"score": float(score), "intensity": 1.0, "matrix_12x12": matrix, "matrix_data": matrix}],
            "processing_time_ms": 5.0,
            "hardware": "TEST",
            "client_name": f"{first_name} {last_name}".strip(),
            "client_signature": signature,
            "emf_compensation": None,
            "symmetry": symmetry,
        }


@pytest.fixture()
def api_client(monkeypatch):
    monkeypatch.setattr(resonance_api, "engine", _DummyEngine())
    monkeypatch.setattr(
        resonance_api,
        "_prepare_precomputed_signature",
        lambda request, client_data: {"frequency": 432.0, "components": {"vector": "ok"}},
    )
    return TestClient(app)


def _client_data_payload():
    return {
        "first_name": "Unit",
        "last_names": ["Test"],
        "birth_date": "2000-01-01",
        "birth_place": "Berlin",
    }


def test_schema_imports_raise_no_pydantic_v2_deprecations_in_fresh_process():
    script = """
import warnings
from pydantic.warnings import PydanticDeprecatedSince20
warnings.simplefilter('error', PydanticDeprecatedSince20)
import app.schemas.klienten
import app.schemas.resonance
"""
    command = [sys.executable, "-c", script]
    result = subprocess.run(command, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr or result.stdout


def test_analyze_matrix_request_path_raises_no_pydantic_v2_deprecations(api_client):
    with warnings.catch_warnings():
        warnings.simplefilter("error", PydanticDeprecatedSince20)
        response = api_client.post(
            "/api/v1/analyze-matrix",
            json={"focus": "Client Fokus", "client_data": _client_data_payload()},
        )
    assert response.status_code == 200
