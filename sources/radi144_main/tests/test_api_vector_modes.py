from pathlib import Path

import pytest
from fastapi.testclient import TestClient

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
            "top_10": [
                {
                    "score": float(score),
                    "intensity": 1.0,
                    "matrix_12x12": matrix,
                    "matrix_data": matrix,
                }
            ],
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


@pytest.mark.parametrize(
    "endpoint,payload",
    [
        (
            "/api/v1/analyze-matrix",
            {"focus": "Client Fokus", "client_data": _client_data_payload()},
        ),
        (
            "/api/v1/analyze-group",
            {
                "focus": "Group Fokus",
                "group_members": [
                    {
                        "first_name": "Anna",
                        "last_names": ["Muster"],
                        "birth_date": "1990-01-01",
                        "birth_place": "Wien",
                    }
                ],
            },
        ),
        (
            "/api/v1/analyze-geo",
            {
                "focus": "Geo Fokus",
                "geo_coords": "48.137154,11.576124,250",
            },
        ),
        (
            "/api/v1/analyze-matrix",
            {
                "focus": "Image Fokus",
                "image_base64": "data:image/png;base64,AAAA",
            },
        ),
    ],
)
def test_vector_mode_endpoints(api_client, endpoint, payload):
    response = api_client.post(endpoint, json=payload)
    assert response.status_code == 200

    body = response.json()
    assert body["matrix_size"] == 12
    assert isinstance(body["matrix_data"], list)
    assert len(body["matrix_data"]) == 12
    assert "client_frequency_hz" in body


def test_db_endpoints(api_client, monkeypatch, tmp_path):
    db_root = tmp_path / "db_import"
    db_root.mkdir(parents=True, exist_ok=True)
    db_a = db_root / "a.txt"
    db_b = db_root / "b.txt"
    db_a.write_text("Herz\nLunge\nStress\n", encoding="utf-8")
    db_b.write_text("Schlaf\nRegeneration\nBalance\n", encoding="utf-8")

    monkeypatch.setattr(resonance_api, "DB_IMPORT_DIR", db_root)

    list_res = api_client.get("/api/v1/db/list")
    assert list_res.status_code == 200
    list_body = list_res.json()
    assert list_body["count"] == 2

    rank_payload = {
        "focus": "Regulation",
        "client_data": _client_data_payload(),
        "focus_weight": "Normal",
        "emf_compensate": False,
    }
    rank_res = api_client.post("/api/v1/db/rank?limit=3", json=rank_payload)
    assert rank_res.status_code == 200
    rank_body = rank_res.json()
    assert rank_body["count"] >= 1
    assert len(rank_body["items"]) >= 1

    scan_payload = {
        "focus": "Regulation",
        "client_data": _client_data_payload(),
        "focus_weight": "Normal",
        "emf_compensate": False,
        "db_path": str(db_a),
    }
    scan_res = api_client.post("/api/v1/db/scan?top_n=2", json=scan_payload)
    assert scan_res.status_code == 200
    scan_body = scan_res.json()
    assert scan_body["count"] == 2
    assert len(scan_body["items"]) == 2
    assert ";" in scan_body["focus_string"]
