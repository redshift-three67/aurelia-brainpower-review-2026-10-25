"""Security-Module fuer die Morphic Engine Web-App.

Bietet:
  - API-Key-Authentifizierung (optional, via MORPHIC_API_KEY env var)
  - Input-Validation Helpers
  - Rate-Limiting (simple in-memory)

Design-Entscheidungen:
  - API-Key ist OPTIONAL: Wenn MORPHIC_API_KEY nicht gesetzt ist,
    laeuft die App ohne Auth (fuer lokale Entwicklung).
  - Rate-Limit ist pro-IP, default 60 Requests/Minute.
  - Input-Validation nutzt Pydantic Models (in contracts.py definiert).
"""
from __future__ import annotations

import os
import time
from collections import defaultdict
from typing import Any, Callable, Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import APIKeyHeader

API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)

# Rate-Limit: IP -> [(timestamp, ...)]
_rate_limit_store: dict[str, list[float]] = defaultdict(list)
RATE_LIMIT_WINDOW_SECONDS = 60
RATE_LIMIT_MAX_REQUESTS = 60


def get_api_key() -> Optional[str]:
    """Liest den API-Key aus der Environment-Variable."""
    return os.getenv("MORPHIC_API_KEY", "").strip() or None


async def verify_api_key(api_key: str = Depends(API_KEY_HEADER)) -> Optional[str]:
    """Dependency: Verifiziert den API-Key falls einer konfiguriert ist.

    Wenn kein MORPHIC_API_KEY in der Environment gesetzt ist, wird
    die Authentifizierung uebersprungen (lokaler Modus).
    """
    expected = get_api_key()
    if expected is None:
        return None  # Kein Auth-Modus (lokal)
    if not api_key or api_key != expected:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    return api_key


async def rate_limit_middleware(request: Request, call_next: Any) -> Any:
    """Simple in-memory Rate-Limiter pro Client-IP."""
    client_ip = request.client.host if request.client else "unknown"
    now = time.time()

    # Alte Eintraege entfernen
    entries = _rate_limit_store[client_ip]
    cutoff = now - RATE_LIMIT_WINDOW_SECONDS
    _rate_limit_store[client_ip] = [t for t in entries if t > cutoff]

    if len(_rate_limit_store[client_ip]) >= RATE_LIMIT_MAX_REQUESTS:
        from fastapi.responses import JSONResponse

        return JSONResponse(
            status_code=429,
            content={
                "error": "Rate limit exceeded",
                "detail": f"Max {RATE_LIMIT_MAX_REQUESTS} requests per "
                f"{RATE_LIMIT_WINDOW_SECONDS}s",
            },
            headers={
                "Retry-After": str(RATE_LIMIT_WINDOW_SECONDS),
            },
        )

    _rate_limit_store[client_ip].append(now)
    response = await call_next(request)
    return response


# Input-Validation Helpers --------------------------------------------------

MAX_NAME_LENGTH = 100
MAX_FOCUS_LENGTH = 500
MAX_INTENTION_LENGTH = 200


def validate_client_name(value: str) -> str:
    """Validiert und bereinigt einen Klienten-Namen."""
    cleaned = value.strip()
    if not cleaned:
        raise ValueError("Name darf nicht leer sein")
    if len(cleaned) > MAX_NAME_LENGTH:
        raise ValueError(f"Name darf maximal {MAX_NAME_LENGTH} Zeichen lang sein")
    # Keine Control-Zeichen oder Path-Separators
    for char in ("..", "/", "\\", "\x00"):
        if char in cleaned:
            raise ValueError(f"Ungueltiges Zeichen im Namen: {repr(char)}")
    return cleaned


def validate_focus_text(value: str) -> str:
    """Validiert den Fokus-Freitext."""
    cleaned = value.strip()
    if len(cleaned) > MAX_FOCUS_LENGTH:
        raise ValueError(
            f"Fokus darf maximal {MAX_FOCUS_LENGTH} Zeichen lang sein"
        )
    return cleaned


def validate_intention(value: str) -> str:
    """Validiert die Intention."""
    cleaned = value.strip()
    if len(cleaned) > MAX_INTENTION_LENGTH:
        raise ValueError(
            f"Intention darf maximal {MAX_INTENTION_LENGTH} Zeichen lang sein"
        )
    return cleaned


def validate_birth_date(value: str) -> str:
    """Validiert das Geburtsdatum-Format (DDMMYYYY oder YYYY-MM-DD)."""
    cleaned = value.strip()
    if not cleaned:
        return ""
    # DDMMYYYY (8 Ziffern)
    if len(cleaned) == 8 and cleaned.isdigit():
        return cleaned
    # YYYY-MM-DD
    if len(cleaned) == 10 and cleaned.count("-") == 2:
        parts = cleaned.split("-")
        if all(p.isdigit() for p in parts):
            return cleaned
    raise ValueError(
        "Geburtsdatum muss DDMMYYYY oder YYYY-MM-DD Format haben"
    )
