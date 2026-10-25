"""Analyze-Endpoint fuer die Morphic Engine Web-App.

Migriert von web_app.py - bereitstellen des synchronen 12-Step
Workflow-Endpoints unter /api/analyze.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from apps.web.security import verify_api_key

router = APIRouter(prefix="/api", tags=["analyze"])


@router.post("/analyze")
async def analyze(
    payload: dict,
    _api_key: str | None = Depends(verify_api_key),
) -> dict:
    """Startet den 12-Step Workflow-Scan synchron.

    Payload: {name, first_name, birth_date, birth_place, focus, intention,
              profile_level, top_n, image_path, harmonize, harm_duration}
    """
    try:
        from apps.cli.workflow.orchestrator import run_workflow

        name = str(payload.get("name", "")).strip()
        first_name = str(payload.get("first_name", "")).strip()
        birth_date = str(payload.get("birth_date", "")).strip()
        birth_place = str(payload.get("birth_place", "")).strip()

        if not name or not first_name:
            return JSONResponse(
                {"error": "Name und Vorname erforderlich"}, status_code=400
            )

        state = run_workflow(
            name=name,
            first_name=first_name,
            birth_date=birth_date,
            birth_place=birth_place,
            focus=str(payload.get("focus", "")).strip(),
            intention=str(payload.get("intention", "harmonization")).strip(),
            profile_level=int(payload.get("profile_level", 3)),
            top_n=int(payload.get("top_n", 5)),
            image_path=str(payload.get("image_path", "")).strip(),
            harmonize=bool(payload.get("harmonize", False)),
            harmonize_duration=int(payload.get("harm_duration", 1)),
            verbose=False,
        )

        return {
            "status": "completed",
            "steps_completed": state.step_completed,
            "errors": state.errors,
            "client_frequency": round(state.client_frequency, 2),
            "emf_index": round(state.composite_emf_index, 4),
            "candidate_count": state.candidate_count,
            "matrix_results_count": len(state.matrix_results),
            "quantum_synergies_count": len(state.quantum_synergies),
            "amplifier_recommendations": state.amplifier_recommendations[:3],
            "palette": state.palette,
            "export_paths": state.export_paths,
        }
    except Exception as exc:
        import traceback

        return JSONResponse(
            {"error": str(exc), "traceback": traceback.format_exc()},
            status_code=500,
        )
