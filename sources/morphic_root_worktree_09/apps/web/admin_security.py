"""Fail-closed Admin-Security primitives for the local Web UI."""
from __future__ import annotations

import hashlib
import hmac
import os
import secrets
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Callable, Mapping

from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel, ConfigDict, Field

ADMIN_TOKEN_HEADER = "X-Morphic-Admin-Token"
ADMIN_BOOTSTRAP_NONCE_ENV = "MORPHIC_ADMIN_BOOTSTRAP_NONCE"
ADMIN_BOOTSTRAP_CREATED_AT_ENV = "MORPHIC_ADMIN_BOOTSTRAP_CREATED_AT_UTC"
ADMIN_EXPECTED_ORIGIN_ENV = "MORPHIC_ADMIN_EXPECTED_ORIGIN"
ADMIN_EXPECTED_HOST_ENV = "MORPHIC_ADMIN_EXPECTED_HOST"
DEFAULT_BOOTSTRAP_TTL_SECONDS = 30
DEFAULT_ADMIN_TOKEN_TTL_SECONDS = 900
DEFAULT_BOOTSTRAP_RATE_LIMIT = 12
BOOTSTRAP_RATE_LIMIT_WINDOW_SECONDS = 60
_MIN_SECRET_LENGTH = 43


class AdminSecurityError(RuntimeError):
    """Base error for invalid admin bootstrap or token checks."""


class AdminRateLimitError(AdminSecurityError):
    """Raised when the bootstrap exchange rate-limit is exceeded."""


@dataclass(frozen=True)
class AdminTokenIssue:
    token: str
    expires_at: datetime
    token_type: str = ADMIN_TOKEN_HEADER


@dataclass(frozen=True)
class _BootstrapNonceRecord:
    origin: str
    host: str
    expires_at: datetime
    server_instance_id: str


@dataclass(frozen=True)
class _AdminTokenRecord:
    origin: str
    host: str
    expires_at: datetime
    server_instance_id: str


@dataclass(frozen=True)
class AdminSecurityConfig:
    expected_origin: str
    expected_host: str
    bootstrap_ttl_seconds: int = DEFAULT_BOOTSTRAP_TTL_SECONDS
    token_ttl_seconds: int = DEFAULT_ADMIN_TOKEN_TTL_SECONDS
    bootstrap_rate_limit: int = DEFAULT_BOOTSTRAP_RATE_LIMIT
    server_instance_id: str = field(
        default_factory=lambda: secrets.token_urlsafe(24)
    )

    def __post_init__(self) -> None:
        if not self.expected_origin:
            raise ValueError("expected_origin must not be blank")
        if not self.expected_host:
            raise ValueError("expected_host must not be blank")
        if self.bootstrap_ttl_seconds <= 0:
            raise ValueError("bootstrap_ttl_seconds must be positive")
        if self.token_ttl_seconds <= 0:
            raise ValueError("token_ttl_seconds must be positive")
        if self.bootstrap_rate_limit <= 0:
            raise ValueError("bootstrap_rate_limit must be positive")


class AdminBootstrapExchangeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nonce: str = Field(min_length=_MIN_SECRET_LENGTH)


class AdminBootstrapExchangeResponse(BaseModel):
    token: str
    token_type: str = ADMIN_TOKEN_HEADER
    expires_at: datetime


class AdminSecurity:
    def __init__(
        self,
        config: AdminSecurityConfig,
        *,
        now: Callable[[], datetime] | None = None,
    ) -> None:
        self.config = config
        self._now = now or (lambda: datetime.now(UTC))
        self._bootstrap_nonces: dict[str, _BootstrapNonceRecord] = {}
        self._admin_tokens: dict[str, _AdminTokenRecord] = {}
        self._bootstrap_attempts: dict[str, list[datetime]] = {}

    @classmethod
    def create(
        cls,
        *,
        expected_origin: str,
        expected_host: str,
        bootstrap_ttl_seconds: int = DEFAULT_BOOTSTRAP_TTL_SECONDS,
        token_ttl_seconds: int = DEFAULT_ADMIN_TOKEN_TTL_SECONDS,
        bootstrap_rate_limit: int = DEFAULT_BOOTSTRAP_RATE_LIMIT,
        now: Callable[[], datetime] | None = None,
    ) -> "AdminSecurity":
        return cls(
            AdminSecurityConfig(
                expected_origin=expected_origin,
                expected_host=expected_host,
                bootstrap_ttl_seconds=bootstrap_ttl_seconds,
                token_ttl_seconds=token_ttl_seconds,
                bootstrap_rate_limit=bootstrap_rate_limit,
            ),
            now=now,
        )

    def create_bootstrap_nonce(
        self,
        *,
        origin: str | None = None,
        host: str | None = None,
        now: Callable[[], datetime] | None = None,
    ) -> str:
        nonce = secrets.token_urlsafe(48)
        self.register_bootstrap_nonce(
            nonce,
            origin=origin,
            host=host,
            created_at=(now or self._now)(),
        )
        return nonce

    def register_bootstrap_nonce(
        self,
        nonce: str,
        *,
        origin: str | None = None,
        host: str | None = None,
        created_at: datetime | None = None,
    ) -> None:
        cleaned = nonce.strip()
        if len(cleaned) < _MIN_SECRET_LENGTH:
            raise AdminSecurityError("bootstrap nonce is too short")
        issued_at = created_at or self._now()
        expires_at = issued_at + timedelta(seconds=self.config.bootstrap_ttl_seconds)
        if expires_at <= self._now():
            raise AdminSecurityError("bootstrap nonce is expired")
        self._bootstrap_nonces[self._digest(cleaned)] = _BootstrapNonceRecord(
            origin=origin or self.config.expected_origin,
            host=host or self.config.expected_host,
            expires_at=expires_at,
            server_instance_id=self.config.server_instance_id,
        )

    def exchange_bootstrap_nonce(
        self,
        nonce: str,
        *,
        origin: str,
        host: str,
        now: Callable[[], datetime] | None = None,
        client_id: str = "unknown",
    ) -> AdminTokenIssue:
        current = (now or self._now)()
        self._check_bootstrap_rate_limit(client_id, current)
        self._expire_bootstrap_nonces(current)
        nonce_digest = self._digest(nonce.strip())
        matched_digest = self._find_digest(self._bootstrap_nonces, nonce_digest)
        if matched_digest is None:
            raise AdminSecurityError("invalid bootstrap nonce")

        record = self._bootstrap_nonces.pop(matched_digest)
        if record.expires_at <= current:
            raise AdminSecurityError("bootstrap nonce expired")
        if record.server_instance_id != self.config.server_instance_id:
            raise AdminSecurityError("bootstrap nonce belongs to another server")
        if record.origin != origin or record.host != host:
            raise AdminSecurityError("bootstrap origin or host mismatch")
        return self._issue_admin_token(current)

    def verify_admin_token(
        self,
        token: str,
        *,
        origin: str,
        host: str,
        now: Callable[[], datetime] | None = None,
    ) -> bool:
        current = (now or self._now)()
        self._expire_admin_tokens(current)
        if origin != self.config.expected_origin or host != self.config.expected_host:
            return False
        if not token:
            return False
        token_digest = self._digest(token.strip())
        matched_digest = self._find_digest(self._admin_tokens, token_digest)
        if matched_digest is None:
            return False
        record = self._admin_tokens[matched_digest]
        return (
            record.expires_at > current
            and record.server_instance_id == self.config.server_instance_id
            and record.origin == origin
            and record.host == host
        )

    def revoke_admin_token(self, token: str) -> None:
        self._admin_tokens.pop(self._digest(token.strip()), None)

    def _issue_admin_token(self, current: datetime) -> AdminTokenIssue:
        token = secrets.token_urlsafe(48)
        expires_at = current + timedelta(seconds=self.config.token_ttl_seconds)
        self._admin_tokens[self._digest(token)] = _AdminTokenRecord(
            origin=self.config.expected_origin,
            host=self.config.expected_host,
            expires_at=expires_at,
            server_instance_id=self.config.server_instance_id,
        )
        return AdminTokenIssue(token=token, expires_at=expires_at)

    def _digest(self, value: str) -> str:
        return hmac.new(
            self.config.server_instance_id.encode("utf-8"),
            value.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

    def _find_digest(
        self, records: Mapping[str, object], candidate_digest: str
    ) -> str | None:
        for record_digest in records:
            if secrets.compare_digest(record_digest, candidate_digest):
                return record_digest
        return None

    def _expire_bootstrap_nonces(self, current: datetime) -> None:
        expired = [
            nonce_digest
            for nonce_digest, record in self._bootstrap_nonces.items()
            if record.expires_at <= current
        ]
        for nonce_digest in expired:
            self._bootstrap_nonces.pop(nonce_digest, None)

    def _expire_admin_tokens(self, current: datetime) -> None:
        expired = [
            token_digest
            for token_digest, record in self._admin_tokens.items()
            if record.expires_at <= current
        ]
        for token_digest in expired:
            self._admin_tokens.pop(token_digest, None)

    def _check_bootstrap_rate_limit(self, client_id: str, current: datetime) -> None:
        cutoff = current - timedelta(seconds=BOOTSTRAP_RATE_LIMIT_WINDOW_SECONDS)
        attempts = [
            attempt
            for attempt in self._bootstrap_attempts.get(client_id, [])
            if attempt > cutoff
        ]
        if len(attempts) >= self.config.bootstrap_rate_limit:
            self._bootstrap_attempts[client_id] = attempts
            raise AdminRateLimitError("admin bootstrap rate-limit exceeded")
        attempts.append(current)
        self._bootstrap_attempts[client_id] = attempts


router = APIRouter(prefix="/api/admin/bootstrap", tags=["admin-security"])


def _request_origin(request: Request) -> str:
    origin = request.headers.get("origin", "").strip()
    if origin:
        return origin
    host = request.headers.get("host", "").strip()
    if not host:
        return ""
    return f"{request.url.scheme}://{host}"


def require_admin_request(request: Request) -> AdminSecurity:
    security = getattr(request.app.state, "admin_security", None)
    if not isinstance(security, AdminSecurity):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="admin security not configured",
        )
    token = request.headers.get(ADMIN_TOKEN_HEADER, "")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"missing {ADMIN_TOKEN_HEADER}",
            headers={"WWW-Authenticate": "MorphicAdminToken"},
        )
    if not security.verify_admin_token(
        token,
        origin=_request_origin(request),
        host=request.headers.get("host", ""),
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="invalid admin token",
        )
    return security


def require_configured_admin_security(request: Request) -> AdminSecurity:
    security = getattr(request.app.state, "admin_security", None)
    if not isinstance(security, AdminSecurity):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="admin security not configured",
        )
    return security


@router.post("/exchange", response_model=AdminBootstrapExchangeResponse)
def exchange_bootstrap_nonce(
    payload: AdminBootstrapExchangeRequest,
    request: Request,
) -> AdminBootstrapExchangeResponse:
    security = require_configured_admin_security(request)
    client_id = request.client.host if request.client else "unknown"
    try:
        issue = security.exchange_bootstrap_nonce(
            payload.nonce,
            origin=_request_origin(request),
            host=request.headers.get("host", ""),
            client_id=client_id,
        )
    except AdminRateLimitError as exc:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="admin bootstrap rate-limit exceeded",
        ) from exc
    except AdminSecurityError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="invalid admin bootstrap nonce",
        ) from exc
    return AdminBootstrapExchangeResponse(
        token=issue.token,
        token_type=issue.token_type,
        expires_at=issue.expires_at,
    )


def create_admin_security_from_env(
    environ: Mapping[str, str] | None = None,
) -> AdminSecurity | None:
    env = os.environ if environ is None else environ
    origin = env.get(ADMIN_EXPECTED_ORIGIN_ENV, "").strip()
    host = env.get(ADMIN_EXPECTED_HOST_ENV, "").strip()
    nonce = env.get(ADMIN_BOOTSTRAP_NONCE_ENV, "").strip()
    if not origin and not host and not nonce:
        return None
    if not origin or not host or not nonce:
        return None

    security = AdminSecurity.create(expected_origin=origin, expected_host=host)
    try:
        security.register_bootstrap_nonce(
            nonce,
            created_at=_parse_created_at(env.get(ADMIN_BOOTSTRAP_CREATED_AT_ENV, "")),
        )
    except AdminSecurityError:
        return None
    if environ is None:
        os.environ.pop(ADMIN_BOOTSTRAP_NONCE_ENV, None)
    return security


def _parse_created_at(raw_value: str) -> datetime | None:
    cleaned = raw_value.strip()
    if not cleaned:
        return None
    try:
        return datetime.fromisoformat(cleaned.replace("Z", "+00:00")).astimezone(UTC)
    except ValueError:
        return None
