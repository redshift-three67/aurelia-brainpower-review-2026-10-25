"""Authenticated tombstone for the retired legacy analyze endpoint."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from apps.web.security import verify_api_key

router = APIRouter(prefix="/api", tags=["analyze"])


@router.post("/analyze")
async def analyze(
    payload: dict,
    _api_key: str | None = Depends(verify_api_key),
) -> JSONResponse:
    del payload
    return JSONResponse(
        status_code=410,
        content={
            "detail": "legacy analyze endpoint retired; use /api/scan/jobs"
        },
    )
