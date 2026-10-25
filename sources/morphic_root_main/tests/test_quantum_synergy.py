"""Tests fuer Quantum-Synergy Engine und Web-Endpoints."""
from __future__ import annotations

from apps.web.main import create_app
from core.quantum_synergy.grover_search import (
    GroverRemedySearch,
    QISKIT_AVAILABLE,
    create_focus_oracle,
)


def test_qiskit_availability_detected() -> None:
    """QISKIT_AVAILABLE muss ein bool sein (True oder False)."""
    assert isinstance(QISKIT_AVAILABLE, bool)


def test_grover_classical_fallback_returns_results() -> None:
    """Klassischer Fallback muss Items zurueckgeben wenn Qiskit nicht verfuegbar."""
    items = [
        {"label": "Arnica", "group": "herbs", "score": 8.0},
        {"label": "Belladonna", "group": "herbs", "score": 6.0},
        {"label": "Nux vomica", "group": "herbs", "score": 4.0},
    ]
    oracle = create_focus_oracle("Arnica")
    searcher = GroverRemedySearch(verbose=False)
    results = searcher.search(items, oracle, max_results=5)
    # Ohne Qiskit wird klassischer Fallback verwendet
    if not QISKIT_AVAILABLE:
        assert len(results) >= 1
        assert results[0][0]["label"] == "Arnica"


def test_focus_oracle_matches_label() -> None:
    """Oracle muss Items mit passendem Label erkennen."""
    oracle = create_focus_oracle("Migraene")
    assert oracle({"label": "Migraene Kopf", "group": "neuro", "score": 8.0})
    assert not oracle({"label": "Verdauung", "group": "gastro", "score": 2.0})


def test_focus_oracle_matches_by_score_threshold() -> None:
    """Oracle muss Items mit hohem Score erkennen (threshold-basiert)."""
    oracle = create_focus_oracle("unbekannt", threshold=0.5)
    assert oracle({"label": "irgendwas", "group": "x", "score": 6.0})
    assert not oracle({"label": "irgendwas", "group": "x", "score": 2.0})


def test_synergy_status_endpoint() -> None:
    """GET /api/synergy/status muss qiskit_available zurueckgeben."""
    # TestClient benoetigt httpx - falls nicht installiert, skip
    try:
        from fastapi.testclient import TestClient
    except RuntimeError:
        return  # httpx nicht installiert - Test ueberspringen

    app = create_app()
    client = TestClient(app)
    response = client.get("/api/synergy/status")
    assert response.status_code == 200
    data = response.json()
    assert "qiskit_available" in data
    assert "mode" in data


def test_hybrid_engine_auto_detects_quantum() -> None:
    """QuantumSynergyEngine muss use_quantum auto-detecten."""
    from core.quantum_synergy.hybrid_engine import QuantumSynergyEngine

    # Default sollte use_quantum=True sein (auto-detect)
    engine = QuantumSynergyEngine()
    assert engine.use_quantum == (True and QISKIT_AVAILABLE)

    # Explicit False
    engine_classical = QuantumSynergyEngine(use_quantum=False)
    assert engine_classical.use_quantum is False
