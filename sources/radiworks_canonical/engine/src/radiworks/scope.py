"""Feste lokale Single-Operator-Scope-Grenze für RadiWorks."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from enum import StrEnum
from typing import Mapping
from urllib.parse import urlsplit


_SCOPE_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}\Z")


_LOCAL_HOSTS = frozenset({"localhost", "127.0.0.1", "::1"})
# Starlette TestClient uses this in-process Host; browser Origins never may.
_TEST_HOST = "testserver"


def _local_authority(value: str, *, origin: bool) -> bool:
    if not value or value != value.strip():
        return False
    try:
        parsed = urlsplit(value if origin else f"http://{value}")
        host = parsed.hostname
        port = parsed.port
        if port is not None and port < 1:
            return False
    except ValueError:
        return False
    if (
        (origin and parsed.scheme not in {"http", "https"})
        or parsed.username is not None
        or parsed.password is not None
        or parsed.path
        or parsed.query
        or parsed.fragment
    ):
        return False
    allowed = _LOCAL_HOSTS if origin else _LOCAL_HOSTS | {_TEST_HOST}
    return host in allowed


class ScopeMode(StrEnum):
    LOCAL = "local"
    ENFORCED = "enforced"


class ScopeError(ValueError):
    pass


@dataclass(frozen=True)
class ScopeContext:
    tenant_id: str
    client_id: str
    job_id: str

    def __post_init__(self) -> None:
        for label, value in (
            ("tenant_id", self.tenant_id),
            ("client_id", self.client_id),
            ("job_id", self.job_id),
        ):
            if not isinstance(value, str) or not _SCOPE_ID.fullmatch(value):
                raise ScopeError(f"{label} ist ungueltig")

    def to_dict(self) -> dict[str, str]:
        return {
            "tenant_id": self.tenant_id,
            "client_id": self.client_id,
            "job_id": self.job_id,
        }


@dataclass(frozen=True)
class ScopeResolver:
    mode: ScopeMode
    local_scope: ScopeContext

    @classmethod
    def from_environment(cls) -> "ScopeResolver":
        configured_mode = os.environ.get("RADIOWORKS_SCOPE_MODE", ScopeMode.LOCAL)
        try:
            mode = ScopeMode(configured_mode)
        except ValueError as exc:
            raise ScopeError("RADIOWORKS_SCOPE_MODE muss local oder enforced sein") from exc
        if mode is not ScopeMode.LOCAL:
            raise ScopeError("RADIOWORKS_SCOPE_MODE unterstützt derzeit nur local")
        return cls(
            mode=mode,
            local_scope=ScopeContext(
                tenant_id=os.environ.get("RADIOWORKS_LOCAL_TENANT_ID", "local"),
                client_id=os.environ.get("RADIOWORKS_LOCAL_CLIENT_ID", "preview"),
                job_id=os.environ.get("RADIOWORKS_LOCAL_JOB_ID", "default"),
            ),
        )

    def resolve(self, headers: Mapping[str, str]) -> ScopeContext:
        normalized = {key.lower(): value for key, value in headers.items()}
        scope_headers = (
            "x-aurelia-tenant-id",
            "x-aurelia-client-id",
            "x-aurelia-job-id",
        )
        if any(header in normalized for header in scope_headers):
            raise ScopeError("Aurelia-Scope-Header sind im lokalen Betrieb nicht zulässig")
        host = normalized.get("host")
        if host is not None and not _local_authority(host, origin=False):
            raise ScopeError("Host ist im lokalen Betrieb nicht zulässig")
        browser_origin = normalized.get("origin")
        if browser_origin is not None and not _local_authority(browser_origin, origin=True):
            raise ScopeError("Origin ist im lokalen Betrieb nicht zulässig")
        return self.local_scope
