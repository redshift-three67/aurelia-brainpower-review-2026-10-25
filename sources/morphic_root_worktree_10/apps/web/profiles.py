"""Profile-Endpoints fuer die Morphic Engine Web-App.

Migriert von web_app.py - bereitstellen der Profile-List-Endpoint
unter /api/profiles.
"""
from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/api/profiles", tags=["profiles"])


@router.get("")
async def list_profiles(level: int = 0) -> dict:
    """Listet Profile, optional gefiltert nach Level."""
    try:
        from core.profile_sync import (
            get_all_profiles,
            get_profiles_by_level,
            get_level_stats,
        )

        if level > 0:
            profiles = get_profiles_by_level(level)
        else:
            profiles = get_all_profiles()
        stats = get_level_stats()
        return {
            "count": len(profiles),
            "level": level,
            "stats": stats,
            "items": [
                {
                    "name": p.name,
                    "display_name": p.display_name,
                    "level": getattr(p, "level", 3),
                    "enabled": p.enabled,
                }
                for p in profiles
            ],
        }
    except Exception as exc:
        return JSONResponse({"error": str(exc)}, status_code=500)
