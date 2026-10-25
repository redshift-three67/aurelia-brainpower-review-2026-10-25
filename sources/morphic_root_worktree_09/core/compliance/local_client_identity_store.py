"""DPAPI-protected local client identities for E5.10A.

This store is additive and deliberately separate from the legacy runtime
``clients.json`` manifest. Records are created only by explicit registration;
there is no legacy import or productive scan integration.
"""
from __future__ import annotations

import json
import re
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any
from uuid import uuid4

from apps.web.durable_io import durable_mkdir_parents
from core.compliance.operator_context import OperatorContext, OwnershipError
from core.compliance.runtime_manifest import stable_client_id
from core.compliance.windows_protection import (
    protect_for_current_user,
    unprotect_for_current_user,
)


_CLIENT_ID = re.compile(r"^cli-[0-9a-f]{20}$")
_SUFFIX = ".dpapi"


def _clean(value: object) -> str:
    return str(value or "").strip()


def _timestamp(value: datetime) -> str:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("timestamp must be timezone-aware")
    return value.astimezone(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


class LocalClientIdentityStore:
    """Store identity plaintext only inside current-user DPAPI envelopes."""

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root).resolve()

    @staticmethod
    def _client_id(value: str) -> str:
        identifier = _clean(value)
        if not _CLIENT_ID.fullmatch(identifier):
            raise ValueError("client_id must be a canonical cli- identifier")
        return identifier

    def _path_for(self, client_id: str) -> Path:
        return self.root / f"{self._client_id(client_id)}{_SUFFIX}"

    def _write(self, client_id: str, record: dict[str, Any]) -> None:
        durable_mkdir_parents(self.root, mode=0o700)
        plaintext = json.dumps(record, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        protected = protect_for_current_user(
            plaintext,
            description="morphic-local-client-identity",
        )
        target = self._path_for(client_id)
        temporary = target.with_suffix(f"{_SUFFIX}.tmp.{uuid4().hex[:8]}")
        try:
            temporary.write_bytes(protected)
            temporary.replace(target)
        finally:
            if temporary.exists():
                temporary.unlink()

    def _read(self, client_id: str) -> dict[str, Any]:
        target = self._path_for(client_id)
        if not target.is_file():
            raise LookupError("client identity not found")
        try:
            payload = json.loads(unprotect_for_current_user(target.read_bytes()).decode("utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError("client identity payload is invalid") from exc
        if not isinstance(payload, dict):
            raise ValueError("client identity payload is invalid")
        return payload

    @staticmethod
    def _assert_binding(record: dict[str, Any], context: OperatorContext) -> None:
        owner_id = _clean(record.get("owner_id"))
        workspace_id = _clean(record.get("workspace_id"))
        tenant_id = _clean(record.get("tenant_id"))
        if not owner_id or not workspace_id or not tenant_id:
            raise ValueError("client identity lacks owner-/tenant binding")
        if workspace_id != context.workspace_id:
            raise OwnershipError("client identity belongs to another workspace")
        if tenant_id != context.tenant_id:
            raise OwnershipError("client identity belongs to another tenant")
        if owner_id not in (context.operator_id, context.workspace_id):
            raise OwnershipError("client identity belongs to another owner")

    @staticmethod
    def _safe_summary(record: dict[str, Any]) -> dict[str, object]:
        consent = record.get("group_analysis")
        consent_data = consent if isinstance(consent, dict) else {}
        return {
            "client_id": _clean(record.get("client_id")),
            "owner_bound": bool(
                _clean(record.get("owner_id"))
                and _clean(record.get("workspace_id"))
                and _clean(record.get("tenant_id"))
            ),
            "consent_enabled": bool(consent_data.get("enabled")),
            "consent_version": _clean(consent_data.get("consent_version")),
            "valid_until": _clean(consent_data.get("valid_until")),
        }

    def register(
        self,
        client: dict[str, Any],
        *,
        context: OperatorContext,
        retention_days: int = 365,
        registered_at: datetime | None = None,
    ) -> dict[str, object]:
        if not 1 <= retention_days <= 3650:
            raise ValueError("retention_days must be between 1 and 3650")
        client_id = stable_client_id(client)
        target = self._path_for(client_id)
        if target.exists():
            return self._safe_summary(self.resolve(client_id, context=context))
        stamp = _timestamp(registered_at or datetime.now(UTC))
        record = {
            "schema_version": 1,
            "client_id": client_id,
            "first_name": _clean(client.get("first_name")),
            "last_name": _clean(client.get("last_name") or client.get("name")),
            "birth_date": _clean(client.get("birth_date")),
            "birth_place": _clean(client.get("birth_place")),
            "owner_id": context.workspace_id,
            "workspace_id": context.workspace_id,
            "tenant_id": context.tenant_id,
            "created_at": stamp,
            "updated_at": stamp,
            "retention_days": retention_days,
            "group_analysis": {
                "enabled": False,
                "consent_version": "",
                "valid_until": "",
            },
        }
        self._write(client_id, record)
        return self._safe_summary(record)

    def resolve(self, client_id: str, *, context: OperatorContext) -> dict[str, Any]:
        identifier = self._client_id(client_id)
        record = self._read(identifier)
        self._assert_binding(record, context)
        if record.get("client_id") != identifier or stable_client_id(record) != identifier:
            raise ValueError("client identity does not match client_id")
        return json.loads(json.dumps(record))

    def record_group_analysis_consent(
        self,
        client_id: str,
        *,
        context: OperatorContext,
        enabled: bool,
        consent_version: str,
        valid_until: datetime,
    ) -> dict[str, object]:
        version = _clean(consent_version)
        if not version:
            raise ValueError("consent_version is required")
        expiry = _timestamp(valid_until)
        if enabled and valid_until.astimezone(UTC) <= datetime.now(UTC):
            raise ValueError("enabled consent valid_until must be in the future")
        record = self.resolve(client_id, context=context)
        record["group_analysis"] = {
            "enabled": bool(enabled),
            "consent_version": version,
            "valid_until": expiry,
        }
        record["updated_at"] = _timestamp(datetime.now(UTC))
        self._write(client_id, record)
        return self._safe_summary(record)

    def list_safe(self, *, context: OperatorContext) -> list[dict[str, object]]:
        if not self.root.is_dir():
            return []
        result: list[dict[str, object]] = []
        for path in sorted(self.root.glob(f"*{_SUFFIX}")):
            client_id = path.name.removesuffix(_SUFFIX)
            try:
                record = self.resolve(client_id, context=context)
            except OwnershipError:
                continue
            result.append(self._safe_summary(record))
        return result

    def erasure_dry_run(
        self,
        client_id: str,
        *,
        context: OperatorContext,
    ) -> dict[str, object]:
        identifier = self._client_id(client_id)
        present = self._path_for(identifier).is_file()
        if present:
            self.resolve(identifier, context=context)
        return {
            "client_id": identifier,
            "identity_entry_present": present,
            "dry_run": True,
        }

    def retention_dry_run(
        self,
        *,
        retention_days: int,
        now: datetime,
        context: OperatorContext,
    ) -> list[dict[str, str]]:
        if retention_days < 0:
            raise ValueError("retention_days must be non-negative")
        reference = datetime.fromisoformat(_timestamp(now).replace("Z", "+00:00"))
        candidates: list[dict[str, str]] = []
        for summary in self.list_safe(context=context):
            client_id = str(summary["client_id"])
            record = self.resolve(client_id, context=context)
            try:
                updated_at = datetime.fromisoformat(
                    _clean(record.get("updated_at")).replace("Z", "+00:00")
                )
            except ValueError as exc:
                raise ValueError("client identity timestamp is invalid") from exc
            if updated_at.tzinfo is None or updated_at.utcoffset() is None:
                raise ValueError("client identity timestamp is invalid")
            if updated_at.astimezone(UTC) < reference - timedelta(days=retention_days):
                candidates.append({"client_id": client_id, "reason": "retention_expired"})
        return candidates

    def find_expired(
        self,
        *,
        context: OperatorContext,
        now: datetime | None = None,
    ) -> list[str]:
        reference = datetime.fromisoformat(
            _timestamp(now or datetime.now(UTC)).replace("Z", "+00:00")
        )
        expired: list[str] = []
        for summary in self.list_safe(context=context):
            client_id = str(summary["client_id"])
            record = self.resolve(client_id, context=context)
            try:
                updated_at = datetime.fromisoformat(
                    _clean(record.get("updated_at")).replace("Z", "+00:00")
                )
                retention_days = int(record.get("retention_days"))
            except (TypeError, ValueError) as exc:
                raise ValueError("client identity retention metadata is invalid") from exc
            if updated_at.tzinfo is None or updated_at.utcoffset() is None:
                raise ValueError("client identity retention metadata is invalid")
            if not 1 <= retention_days <= 3650:
                raise ValueError("client identity retention metadata is invalid")
            if reference >= updated_at.astimezone(UTC) + timedelta(days=retention_days):
                expired.append(client_id)
        return expired

    def purge_expired(
        self,
        *,
        context: OperatorContext,
        now: datetime | None = None,
        dry_run: bool = False,
    ) -> list[str]:
        expired = self.find_expired(context=context, now=now)
        if dry_run:
            return expired
        purged: list[str] = []
        for client_id in expired:
            if self.erase(
                client_id,
                context=context,
                confirmation_id=client_id,
            ):
                purged.append(client_id)
        return purged

    def erase(
        self,
        client_id: str,
        *,
        context: OperatorContext,
        confirmation_id: str,
    ) -> bool:
        identifier = self._client_id(client_id)
        try:
            confirmed = self._client_id(confirmation_id)
        except ValueError as exc:
            raise ValueError("erase confirmation_id must exactly match client_id") from exc
        if confirmed != identifier:
            raise ValueError("erase confirmation_id must exactly match client_id")
        target = self._path_for(identifier)
        if not target.exists():
            return False
        self.resolve(identifier, context=context)
        target.unlink()
        return True
