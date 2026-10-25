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

import hmac
import os
import secrets
import threading
import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Callable, Optional
from urllib.parse import urlsplit

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import APIKeyHeader

API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)
SESSION_COOKIE_NAME = "morphic_session"
_UNOBSERVED_KEY = object()
_REQUEST_AUTH_SNAPSHOT_ATTRIBUTE = "_morphic_authentication_generation"
_REQUEST_AUTH_COMPENSATION_ATTRIBUTE = "_morphic_authentication_compensation"
_REQUEST_MEASUREMENT_PUBLISH_PERMIT_ATTRIBUTE = "_morphic_measurement_publish_permit"
_UNSAFE_HTTP_METHODS = frozenset({"POST", "PUT", "PATCH", "DELETE"})

# Rate-Limit: IP -> [(timestamp, ...)]
_rate_limit_store: dict[str, list[float]] = defaultdict(list)
RATE_LIMIT_WINDOW_SECONDS = 60
RATE_LIMIT_MAX_REQUESTS = 60
READ_RATE_LIMIT_MAX_REQUESTS = 300
REPORT_RATE_LIMIT_MAX_REQUESTS = 30
POLL_RATE_LIMIT_MAX_REQUESTS = 600


def get_api_key() -> Optional[str]:
    """Liest den API-Key aus der Environment-Variable."""
    return os.getenv("MORPHIC_API_KEY", "").strip() or None


@dataclass(frozen=True, slots=True)
class _AuthenticationGenerationSnapshot:
    expected_key: str | None = field(repr=False)
    generation: int


class SessionAuthority:
    """Process-local browser sessions bound to a monotone observed auth generation."""

    def __init__(self) -> None:
        self._tokens: dict[str, int] = {}
        self._lock = threading.RLock()
        self._observed_key: object | str | None = _UNOBSERVED_KEY
        self._generation = 0

    def _observe_current_generation_locked(self) -> tuple[str | None, int]:
        current_key = get_api_key()
        if self._observed_key is _UNOBSERVED_KEY:
            self._observed_key = current_key
        elif self._observed_key != current_key:
            self._tokens.clear()
            self._generation += 1
            self._observed_key = current_key
        return current_key, self._generation

    def observe_current_generation(self) -> tuple[str | None, int]:
        with self._lock:
            return self._observe_current_generation_locked()

    def issue(self) -> str:
        with self._lock:
            expected, generation = self._observe_current_generation_locked()
            if expected is None:
                raise RuntimeError("browser session requires configured authentication")
            token = secrets.token_urlsafe(32)
            self._tokens[token] = generation
        return token

    def issue_for_api_key(self, candidate: str | None) -> str | None:
        with self._lock:
            expected, generation = self._observe_current_generation_locked()
            if not _credential_matches_expected(candidate, expected):
                return None
            token = secrets.token_urlsafe(32)
            self._tokens[token] = generation
            return token

    def contains(self, token: str | None) -> bool:
        if not token:
            return False
        with self._lock:
            expected, generation = self._observe_current_generation_locked()
            if expected is None:
                return False
            return self._tokens.get(token) == generation

    def revoke(self, token: str | None) -> None:
        if not token:
            return
        with self._lock:
            self._tokens.pop(token, None)


def api_key_matches(candidate: str | None) -> bool:
    expected = get_api_key()
    return bool(expected and candidate and hmac.compare_digest(candidate, expected))


def _authentication_generation(state: object) -> _AuthenticationGenerationSnapshot:
    authority = getattr(state, "session_authority", None)
    if authority is not None:
        expected, generation = authority.observe_current_generation()
    else:
        expected, generation = get_api_key(), 0
    return _AuthenticationGenerationSnapshot(expected, generation)


def _credential_matches_expected(candidate: str | None, expected: str | None) -> bool:
    return bool(
        expected
        and candidate
        and hmac.compare_digest(candidate, expected)
    )


def _session_matches_generation(
    state: object,
    session_token: str | None,
) -> bool:
    authority = getattr(state, "session_authority", None)
    return authority is not None and authority.contains(session_token)


def _request_authenticated_for_snapshot(
    request: Request,
    snapshot: _AuthenticationGenerationSnapshot,
) -> bool:
    if snapshot.expected_key is None:
        return True
    headers = getattr(request, "headers", {})
    cookies = getattr(request, "cookies", {})
    return _credential_matches_expected(
        headers.get("x-api-key"), snapshot.expected_key
    ) or _session_matches_generation(
        request.app.state,
        cookies.get(SESSION_COOKIE_NAME),
    )


def _websocket_authenticated_for_snapshot(
    websocket: Any,
    state: object,
    snapshot: _AuthenticationGenerationSnapshot,
) -> bool:
    if snapshot.expected_key is None:
        return True
    return _credential_matches_expected(
        websocket.headers.get("x-api-key"), snapshot.expected_key
    ) or _session_matches_generation(
        state,
        websocket.cookies.get(SESSION_COOKIE_NAME),
    )


def _unauthorized() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing API key",
        headers={"WWW-Authenticate": "ApiKey"},
    )


def _cross_origin_denied() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Cross-origin request denied",
    )


def _effective_port(scheme: str, port: int | None) -> int | None:
    if port is not None:
        return port
    return {"http": 80, "https": 443}.get(scheme)


def _session_origin_matches_request_target(request: Request) -> bool:
    origins = request.headers.getlist("origin")
    if len(origins) != 1:
        return False
    origin = origins[0]
    if not origin or origin != origin.strip():
        return False
    if any(ord(character) < 0x20 or ord(character) == 0x7F for character in origin):
        return False
    try:
        origin.encode("ascii")
        parsed = urlsplit(origin)
        origin_port = parsed.port
        target_port = request.url.port
    except (UnicodeError, ValueError):
        return False
    scheme = parsed.scheme.lower()
    target_scheme = request.url.scheme.lower()
    if scheme not in {"http", "https"} or target_scheme not in {"http", "https"}:
        return False
    if (
        not parsed.netloc
        or parsed.hostname is None
        or parsed.username is not None
        or parsed.password is not None
        or parsed.path
        or parsed.query
        or parsed.fragment
        or parsed.netloc.endswith(":")
        or "%" in parsed.netloc
        or any(character.isspace() for character in parsed.netloc)
    ):
        return False
    target_host = request.url.hostname
    return (
        target_host is not None
        and scheme == target_scheme
        and parsed.hostname == target_host
        and _effective_port(scheme, origin_port)
        == _effective_port(target_scheme, target_port)
    )


def capture_authenticated_request_generation(
    request: Request,
) -> _AuthenticationGenerationSnapshot:
    """Capture one stable authenticated generation before productive work."""
    state = request.app.state
    snapshot = _authentication_generation(state)
    if not _request_authenticated_for_snapshot(request, snapshot):
        raise _unauthorized()
    if _authentication_generation(state) != snapshot:
        raise _unauthorized()
    setattr(request.state, _REQUEST_AUTH_SNAPSHOT_ATTRIBUTE, snapshot)
    return snapshot


def register_request_authentication_compensation(
    request: Request,
    compensation: Callable[[], None],
) -> None:
    setattr(request.state, _REQUEST_AUTH_COMPENSATION_ATTRIBUTE, compensation)


def register_measurement_publish_permit(
    request: Request,
    authority: Any,
    lease: str,
) -> None:
    """Bind one measurement response to its authority lease until body emission."""
    setattr(
        request.state,
        _REQUEST_MEASUREMENT_PUBLISH_PERMIT_ATTRIBUTE,
        (authority, lease),
    )


def _clear_measurement_publish_permit(request: Request) -> None:
    setattr(request.state, _REQUEST_MEASUREMENT_PUBLISH_PERMIT_ATTRIBUTE, None)


def _compensate_request_authentication_failure(request: Request) -> None:
    compensation = getattr(
        request.state,
        _REQUEST_AUTH_COMPENSATION_ATTRIBUTE,
        None,
    )
    if compensation is None:
        return
    setattr(request.state, _REQUEST_AUTH_COMPENSATION_ATTRIBUTE, None)
    compensation()


def _raise_request_authentication_failure(request: Request) -> None:
    _compensate_request_authentication_failure(request)
    raise _unauthorized()


def revalidate_authenticated_request_generation(
    request: Request,
    snapshot: _AuthenticationGenerationSnapshot,
) -> None:
    """Fail closed unless the request still owns its captured generation."""
    state = request.app.state
    if _authentication_generation(state) != snapshot:
        _raise_request_authentication_failure(request)
    if not _request_authenticated_for_snapshot(request, snapshot):
        _raise_request_authentication_failure(request)
    if _authentication_generation(state) != snapshot:
        _raise_request_authentication_failure(request)


def revalidate_captured_request_generation(request: Request) -> bool:
    snapshot = getattr(
        request.state,
        _REQUEST_AUTH_SNAPSHOT_ATTRIBUTE,
        None,
    )
    if snapshot is None:
        return False
    revalidate_authenticated_request_generation(request, snapshot)
    return True


def capture_authenticated_websocket_generation(
    websocket: Any,
    state: object,
    authenticate: Callable[[Any, object, bool], bool] | None = None,
) -> _AuthenticationGenerationSnapshot | None:
    """Capture one stable authenticated generation before WebSocket accept."""
    snapshot = _authentication_generation(state)
    if authenticate is None:
        authenticated = _websocket_authenticated_for_snapshot(
            websocket, state, snapshot
        )
    else:
        authenticated = authenticate(
            websocket, state, snapshot.expected_key is not None
        )
    if not authenticated or _authentication_generation(state) != snapshot:
        return None
    return snapshot


def websocket_generation_is_current(
    websocket: Any,
    state: object,
    snapshot: _AuthenticationGenerationSnapshot,
) -> bool:
    """Revalidate a live WebSocket against its original auth generation."""
    if _authentication_generation(state) != snapshot:
        return False
    if not _websocket_authenticated_for_snapshot(websocket, state, snapshot):
        return False
    return _authentication_generation(state) == snapshot


def websocket_authenticated(websocket: Any, state: object, required: bool) -> bool:
    """Revalidate API-key or browser-session authority for a live WebSocket."""
    snapshot = _authentication_generation(state)
    if snapshot.expected_key is None:
        return not required
    return _websocket_authenticated_for_snapshot(websocket, state, snapshot)


async def verify_api_key(
    request: Request,
    api_key: str = Depends(API_KEY_HEADER),
) -> Optional[str]:
    """Dependency: Verifiziert den API-Key falls einer konfiguriert ist.

    Wenn kein MORPHIC_API_KEY in der Environment gesetzt ist, wird
    die Authentifizierung uebersprungen (lokaler Modus).
    """
    snapshot = _authentication_generation(request.app.state)
    if snapshot.expected_key is None:
        return None  # Kein Auth-Modus (lokal)
    if _credential_matches_expected(api_key, snapshot.expected_key):
        return api_key
    session_token = request.cookies.get(SESSION_COOKIE_NAME)
    if _session_matches_generation(request.app.state, session_token):
        if (
            request.method.upper() in _UNSAFE_HTTP_METHODS
            and not _session_origin_matches_request_target(request)
        ):
            raise _cross_origin_denied()
        return "browser-session"
    raise _unauthorized()


async def _revalidate_response_authentication(request: Request) -> None:
    if revalidate_captured_request_generation(request):
        return
    await verify_api_key(request, request.headers.get("x-api-key", ""))


class MeasurementPublishPermitMiddleware:
    """Hold a measurement lease through the outer ASGI payload send."""

    def __init__(self, app: Any) -> None:
        self.app = app

    async def __call__(self, scope: Any, receive: Any, send: Any) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        request = Request(scope)

        async def guarded_send(message: dict[str, Any]) -> None:
            publish_permit = scope.get("state", {}).get(
                _REQUEST_MEASUREMENT_PUBLISH_PERMIT_ATTRIBUTE,
            )
            if (
                message["type"] == "http.response.body"
                and message.get("body")
                and publish_permit is not None
            ):
                authority, lease = publish_permit
                async with authority.async_publish_permit(lease) as permitted:
                    if not permitted:
                        return
                    try:
                        await _revalidate_response_authentication(request)
                    except HTTPException:
                        return
                    await send(message)
                return
            await send(message)

        await self.app(scope, receive, guarded_send)


async def revalidate_protected_response(request: Request, call_next: Any) -> Any:
    """Revalidate captured auth generations through final response emission."""
    response = await call_next(request)
    if (
        request.method == "OPTIONS"
        and request.headers.get("origin", "").strip()
        and request.headers.get("access-control-request-method", "").strip()
    ):
        return response
    path = request.url.path
    if not path.startswith("/api/") or path.startswith("/api/auth/"):
        return response
    try:
        await _revalidate_response_authentication(request)
    except HTTPException as exc:
        from fastapi.responses import JSONResponse

        _clear_measurement_publish_permit(request)
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )

    original_body = response.body_iterator

    async def guarded_body():
        async for chunk in original_body:
            try:
                await _revalidate_response_authentication(request)
            except HTTPException:
                _clear_measurement_publish_permit(request)
                return
            yield chunk

    response.body_iterator = guarded_body()
    return response


async def rate_limit_middleware(
    request: Request,
    call_next: Any,
    *,
    bucket: str = "mutation",
    max_requests: int = RATE_LIMIT_MAX_REQUESTS,
) -> Any:
    """Simple in-memory Rate-Limiter pro Client-IP und Traffic-Klasse."""
    client_ip = request.client.host if request.client else "unknown"
    now = time.time()
    store_key = f"{bucket}:{client_ip}"

    # Alte Eintraege entfernen
    entries = _rate_limit_store[store_key]
    cutoff = now - RATE_LIMIT_WINDOW_SECONDS
    _rate_limit_store[store_key] = [t for t in entries if t > cutoff]

    if len(_rate_limit_store[store_key]) >= max_requests:
        from fastapi.responses import JSONResponse

        return JSONResponse(
            status_code=429,
            content={
                "error": "Rate limit exceeded",
                "detail": f"Max {max_requests} requests per "
                f"{RATE_LIMIT_WINDOW_SECONDS}s",
            },
            headers={
                "Retry-After": str(RATE_LIMIT_WINDOW_SECONDS),
            },
        )

    _rate_limit_store[store_key].append(now)
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
