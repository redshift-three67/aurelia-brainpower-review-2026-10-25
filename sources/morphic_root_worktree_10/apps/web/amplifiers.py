"""Amplifier-Endpoints fuer die Morphic Engine Web-App.

Migriert von web_app.py - bereitstellen der Amplifier-List- und
Cosinus-Match-Endpoints unter /api/amplifier/*.
"""
from __future__ import annotations

import hashlib
from typing import Any

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from apps.web.security import verify_api_key

router = APIRouter(prefix="/api/amplifier", tags=["amplifier"])


def _safe_float(val: Any, default: float = 0.0) -> float:
    try:
        return float(val)
    except (TypeError, ValueError):
        return default


@router.get("/list")
async def amplifier_list() -> dict:
    """Listet alle 12 Amplifier."""
    try:
        from apps.cli.workflow.step06_amplifier import _AMPLIFIERS

        return {"count": len(_AMPLIFIERS), "amplifiers": _AMPLIFIERS}
    except Exception as exc:
        return JSONResponse({"error": str(exc)}, status_code=500)


@router.post("/match")
async def amplifier_match(
    payload: dict,
    _api_key: str | None = Depends(verify_api_key),
) -> dict:
    """Cosinus-Match fuer Client-Daten."""
    try:
        import numpy as np

        from apps.cli.workflow.step06_amplifier import _AMPLIFIERS, _amp_vector

        client_freq = _safe_float(payload.get("client_frequency"), 432.0)
        focus = str(payload.get("focus", ""))
        top_n = int(payload.get("top_n", 3))

        cvec = np.zeros(12)
        cvec[0] = (client_freq - 20) / 1980
        cvec[1] = (client_freq * 1.5 - 20) / 1980
        cvec[6] = client_freq / 1000

        focus_hash = (
            int(hashlib.md5(focus.encode()).hexdigest()[:6], 16) if focus else 0
        )
        cvec[8] = (focus_hash % 360) / 360

        cnorm = np.linalg.norm(cvec) or 1.0
        scored = []
        for amp in _AMPLIFIERS:
            avec = _amp_vector(amp)
            anorm = np.linalg.norm(avec) or 1.0
            cos_sim = float(np.dot(cvec, avec) / (cnorm * anorm))
            total = 0.55 * cos_sim + 0.20 * 0.5 + 0.25 * 0.3
            scored.append(
                {**amp, "score": round(total, 4), "cosine": round(cos_sim, 4)}
            )
        scored.sort(key=lambda x: x["score"], reverse=True)
        return {"recommendations": scored[:top_n], "client_frequency": client_freq}
    except Exception as exc:
        return JSONResponse({"error": str(exc)}, status_code=500)
