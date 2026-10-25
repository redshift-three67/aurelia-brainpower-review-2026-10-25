"""Quantum-Synergy Endpoints fuer die Morphic Engine Web-App.

Bietet API-Endpoints fuer die Quantum-Synergy-Optimierung:
  - POST /api/synergy/optimize - Finde optimale Remedy-Kombinationen
  - GET  /api/synergy/status   - Quantum-Verfuegbarkeit pruefen
  - GET  /api/synergy/stats    - Datenbank-Statistiken
"""
from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from apps.web.security import verify_api_key

router = APIRouter(prefix="/api/synergy", tags=["synergy"])


class SynergyOptimizeRequest(BaseModel):
    focus: str = Field(..., min_length=1, max_length=500, description="Fokus-Thema")
    top_n: int = Field(default=5, ge=1, le=50)
    combination_size: int = Field(default=3, ge=2, le=5)
    threshold: float = Field(default=7.0, ge=0.0, le=10.0)
    use_quantum: bool = Field(default=True, description="Quantum-Suche (auto-detect)")


@router.get("/status")
async def synergy_status(_api_key: str | None = Depends(verify_api_key)) -> dict:
    """Prueft Quantum-Verfuegbarkeit."""
    try:
        from core.quantum_synergy.grover_search import QISKIT_AVAILABLE

        return {
            "qiskit_available": QISKIT_AVAILABLE,
            "mode": "quantum" if QISKIT_AVAILABLE else "classical",
        }
    except ImportError:
        return {"qiskit_available": False, "mode": "unavailable"}


@router.get("/stats")
async def synergy_stats(_api_key: str | None = Depends(verify_api_key)) -> dict:
    """Gibt Datenbank-Statistiken zurueck."""
    try:
        from core.quantum_synergy.hybrid_engine import QuantumSynergyEngine

        engine = QuantumSynergyEngine(use_quantum=False)
        stats = engine.get_statistics()
        return {"stats": stats}
    except Exception:
        return {"error": "synergy statistics unavailable"}


@router.post("/optimize")
async def synergy_optimize(
    request: SynergyOptimizeRequest,
    _api_key: str | None = Depends(verify_api_key),
) -> dict:
    """Findet optimale synergetische Remedy-Kombinationen fuer einen Fokus."""
    try:
        from core.quantum_synergy.hybrid_engine import QuantumSynergyEngine
        from core.quantum_synergy.grover_search import QISKIT_AVAILABLE

        engine = QuantumSynergyEngine(use_quantum=request.use_quantum)
        results = engine.find_synergistic_triggers(
            focus=request.focus,
            combination_size=request.combination_size,
            top_n=request.top_n,
            threshold=request.threshold,
        )

        combinations = []
        for items, score, details in results:
            combinations.append(
                {
                    "items": [
                        {"label": i.get("label", ""), "group": i.get("group", "")}
                        for i in items
                    ],
                    "score": round(score, 4),
                    "category": "primary" if score >= 7.0 else "secondary",
                    "components": details if isinstance(details, dict) else {},
                }
            )

        return {
            "status": "completed",
            "focus": request.focus,
            "quantum_used": request.use_quantum and QISKIT_AVAILABLE,
            "combination_count": len(combinations),
            "combinations": combinations,
        }
    except Exception:
        return {"error": "synergy optimization failed"}
