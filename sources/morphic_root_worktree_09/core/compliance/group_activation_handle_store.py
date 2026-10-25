"""Short-lived, one-time DPAPI transport for authorized group-analysis candidates.

The handle store is a server-side transport primitive only. Productive scan,
CLI, job, report, trace, and manifest paths do not import it.
"""
from __future__ import annotations

import hashlib
import json
import re
from datetime import UTC, datetime, timedelta
from pathlib import Path
from threading import RLock
from typing import Mapping
from uuid import uuid4

import numpy as np

from apps.web.durable_io import durable_mkdir_parents
from core.compliance.operator_context import OperatorContext, OwnershipError
from core.compliance.windows_protection import protect_for_current_user, unprotect_for_current_user
from core.profiles.group_vector import GroupAnalysisOptIn


GROUP_ACTIVATION_HANDLE_VERSION = "group-activation-handle-v1"
_HANDLE = re.compile(r"^gah-[0-9a-f]{32}$")
_SUFFIX = ".dpapi"
_AUDIT = "activation-audit.jsonl"
_GENERATION = re.compile(r"^[0-9a-f]{32}$")


class GroupActivationHandleStore:
    """Transport an authorized in-memory candidate through a one-time handle."""

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root).resolve()
        self._lock = RLock()

    @staticmethod
    def _handle(value: str) -> str:
        cleaned = str(value or "").strip()
        if not _HANDLE.fullmatch(cleaned):
            raise ValueError("activation_handle must be canonical")
        return cleaned

    @staticmethod
    def _timestamp(value: datetime) -> str:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("activation handle timestamp must be timezone-aware")
        return value.astimezone(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    @classmethod
    def _parse_timestamp(cls, value: object) -> datetime:
        try:
            parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        except (TypeError, ValueError) as exc:
            raise ValueError("activation handle payload is invalid") from exc
        if parsed.tzinfo is None or parsed.utcoffset() is None:
            raise ValueError("activation handle payload is invalid")
        return parsed.astimezone(UTC)

    def _path_for(self, activation_handle: str) -> Path:
        return self.root / f"{self._handle(activation_handle)}{_SUFFIX}"

    @staticmethod
    def _context_key(context: OperatorContext) -> str:
        values = (context.operator_id, context.workspace_id, context.tenant_id)
        if not all(values):
            raise ValueError("activation handle context must be complete")
        canonical = json.dumps(values, ensure_ascii=False, separators=(",", ":"))
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:32]

    def _generation_path(self, context: OperatorContext) -> Path:
        return self.root / f".generation-{self._context_key(context)}{_SUFFIX}"

    def _write_generation(self, context: OperatorContext, generation: str) -> None:
        if not _GENERATION.fullmatch(generation):
            raise ValueError("activation generation is invalid")
        durable_mkdir_parents(self.root, mode=0o700)
        target = self._generation_path(context)
        temporary = target.with_suffix(f"{_SUFFIX}.tmp.{uuid4().hex[:8]}")
        protected = protect_for_current_user(
            generation.encode("ascii"),
            description="morphic-group-activation-generation",
        )
        try:
            temporary.write_bytes(protected)
            temporary.replace(target)
        finally:
            if temporary.exists():
                temporary.unlink()

    def _current_generation(self, context: OperatorContext) -> str:
        with self._lock:
            target = self._generation_path(context)
            if target.is_file():
                try:
                    generation = unprotect_for_current_user(target.read_bytes()).decode("ascii")
                except Exception as exc:
                    raise ValueError("activation generation is invalid") from exc
                if not _GENERATION.fullmatch(generation):
                    raise ValueError("activation generation is invalid")
                return generation
            generation = uuid4().hex
            self._write_generation(context, generation)
            return generation

    def authorization_generation(self, context: OperatorContext) -> str:
        """Capture the context generation before authorization I/O begins."""

        return self._current_generation(context)

    @staticmethod
    def _validate_context_payload(payload: dict[str, object], context: OperatorContext) -> None:
        expected = (context.operator_id, context.workspace_id, context.tenant_id)
        actual = (
            str(payload.get("operator_id", "")),
            str(payload.get("workspace_id", "")),
            str(payload.get("tenant_id", "")),
        )
        if not all(expected) or actual != expected:
            raise OwnershipError("activation handle belongs to another operator/workspace/tenant")

    @staticmethod
    def _validated_opt_in(opt_in: GroupAnalysisOptIn) -> tuple[np.ndarray, float]:
        if opt_in.enabled is not True:
            raise ValueError("activation handle requires an enabled group opt-in")
        if opt_in.consent_verified is not True:
            raise ValueError("activation handle requires verified consent")
        if opt_in.centroid_rates is None:
            raise ValueError("activation handle requires centroid rates")
        try:
            centroid = np.asarray(opt_in.centroid_rates, dtype=float)
            strength = float(opt_in.strength)
        except (TypeError, ValueError) as exc:
            raise ValueError("activation handle candidate must be numeric") from exc
        if centroid.ndim != 1 or centroid.size == 0 or not np.isfinite(centroid).all():
            raise ValueError("activation handle centroid must be finite and one-dimensional")
        if not np.isfinite(strength) or not 0.0 <= strength <= 1.0:
            raise ValueError("activation handle strength must be finite and within [0,1]")
        return centroid, strength

    def _audit(self, event: str, *, occurred_at: datetime, outcome: str) -> None:
        durable_mkdir_parents(self.root, mode=0o700)
        record = {
            "event": event,
            "policy_version": GROUP_ACTIVATION_HANDLE_VERSION,
            "outcome": outcome,
            "occurred_at": self._timestamp(occurred_at),
        }
        with (self.root / _AUDIT).open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(record, separators=(",", ":"), sort_keys=True) + "\n")

    def _read(self, activation_handle: str) -> dict[str, object]:
        target = self._path_for(activation_handle)
        if not target.is_file():
            raise LookupError("activation handle not found")
        try:
            plaintext = unprotect_for_current_user(target.read_bytes())
            payload = json.loads(plaintext.decode("utf-8"))
        except Exception as exc:
            raise ValueError("activation handle payload is invalid") from exc
        if not isinstance(payload, dict) or payload.get("policy_version") != GROUP_ACTIVATION_HANDLE_VERSION:
            raise ValueError("activation handle payload is invalid")
        return payload

    def issue(
        self,
        opt_in: GroupAnalysisOptIn,
        *,
        context: OperatorContext,
        now: datetime,
        ttl_seconds: int = 60,
    ) -> dict[str, object]:
        if isinstance(ttl_seconds, bool) or not isinstance(ttl_seconds, int) or not 1 <= ttl_seconds <= 300:
            raise ValueError("activation handle ttl_seconds must be an integer within [1,300]")
        issued_at = self._parse_timestamp(self._timestamp(now))
        centroid, strength = self._validated_opt_in(opt_in)
        if not all((context.operator_id, context.workspace_id, context.tenant_id)):
            raise ValueError("activation handle context must be complete")
        generation = self._current_generation(context)
        candidate_generation = str(opt_in.activation_generation or "").strip()
        if not candidate_generation:
            raise LookupError("activation authorization generation is required")
        if candidate_generation != generation:
            raise LookupError("activation authorization was invalidated")
        activation_handle = f"gah-{uuid4().hex}"
        expires_at = issued_at + timedelta(seconds=ttl_seconds)
        payload = {
            "policy_version": GROUP_ACTIVATION_HANDLE_VERSION,
            "operator_id": context.operator_id,
            "workspace_id": context.workspace_id,
            "tenant_id": context.tenant_id,
            "issued_at": self._timestamp(issued_at),
            "expires_at": self._timestamp(expires_at),
            "activation_generation": generation,
            "opt_in": {
                "enabled": True,
                "centroid_rates": centroid.tolist(),
                "strength": strength,
                "consent_verified": True,
            },
        }
        protected = protect_for_current_user(
            json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8"),
            description="morphic-group-activation-handle",
        )
        durable_mkdir_parents(self.root, mode=0o700)
        target = self._path_for(activation_handle)
        temporary = target.with_suffix(f"{_SUFFIX}.tmp.{uuid4().hex[:8]}")
        try:
            temporary.write_bytes(protected)
            temporary.replace(target)
        finally:
            if temporary.exists():
                temporary.unlink()
        self._audit("issued", occurred_at=issued_at, outcome="ready")
        return {
            "activation_handle": activation_handle,
            "policy_version": GROUP_ACTIVATION_HANDLE_VERSION,
            "status": "ready",
            "expires_at": self._timestamp(expires_at),
            "one_time": True,
        }

    def consume(
        self,
        activation_handle: str,
        *,
        context: OperatorContext,
        now: datetime,
    ) -> GroupAnalysisOptIn:
        identifier = self._handle(activation_handle)
        current = self._parse_timestamp(self._timestamp(now))
        with self._lock:
            payload = self._read(identifier)
            self._validate_context_payload(payload, context)
            generation = str(payload.get("activation_generation", ""))
            if generation != self._current_generation(context):
                self._path_for(identifier).unlink()
                self._audit("invalidated", occurred_at=current, outcome="deleted")
                raise LookupError("activation authorization was invalidated")
            expires_at = self._parse_timestamp(payload.get("expires_at"))
            target = self._path_for(identifier)
            if current >= expires_at:
                target.unlink()
                self._audit("expired", occurred_at=current, outcome="deleted")
                raise TimeoutError("activation handle expired")
            opt_in = payload.get("opt_in")
            if not isinstance(opt_in, dict):
                raise ValueError("activation handle payload is invalid")
            try:
                candidate = GroupAnalysisOptIn(
                    enabled=opt_in.get("enabled") is True,
                    centroid_rates=np.asarray(opt_in.get("centroid_rates"), dtype=float),
                    strength=float(opt_in.get("strength")),
                    consent_verified=opt_in.get("consent_verified") is True,
                    activation_generation=generation,
                )
                self._validated_opt_in(candidate)
            except (TypeError, ValueError) as exc:
                raise ValueError("activation handle payload is invalid") from exc
            target.unlink()
            self._audit("consumed", occurred_at=current, outcome="success")
            return candidate

    def invalidate_context(
        self,
        context: OperatorContext,
        *,
        now: datetime | None = None,
    ) -> dict[str, int]:
        """Revoke current handles and prevent stale in-memory fan-out."""

        occurred_at = now or datetime.now(UTC)
        invalidated: list[Path] = []
        with self._lock:
            self._write_generation(context, uuid4().hex)
            targets = (
                sorted(self.root.glob(f"gah-*{_SUFFIX}"))
                if self.root.is_dir()
                else []
            )
            for target in targets:
                try:
                    payload = self._read(target.name.removesuffix(_SUFFIX))
                    self._validate_context_payload(payload, context)
                except OwnershipError:
                    continue
                except ValueError:
                    continue
                invalidated.append(target)
            for target in invalidated:
                target.unlink()
            self._audit(
                "invalidated",
                occurred_at=occurred_at,
                outcome=f"deleted:{len(invalidated)}",
            )
        return {"invalidated_count": len(invalidated)}

    def worker_payload(self, activation_handle: str) -> dict[str, str]:
        """Return the only payload shape allowed across the worker boundary."""

        return {"activation_handle": self._handle(activation_handle)}

    def consume_worker_payload(
        self,
        payload: Mapping[str, object],
        *,
        context: OperatorContext,
        now: datetime,
    ) -> GroupAnalysisOptIn:
        """Strictly consume a handle-only worker payload."""

        if not isinstance(payload, Mapping) or set(payload) != {"activation_handle"}:
            raise ValueError("worker payload may contain only activation_handle")
        activation_handle = payload.get("activation_handle")
        if not isinstance(activation_handle, str):
            raise ValueError("worker payload may contain only activation_handle")
        return self.consume(activation_handle, context=context, now=now)

    def erase(
        self,
        activation_handle: str,
        *,
        confirmation_handle: str,
        context: OperatorContext,
    ) -> bool:
        identifier = self._handle(activation_handle)
        if self._handle(confirmation_handle) != identifier:
            raise ValueError("confirmation_handle must exactly match activation_handle")
        with self._lock:
            target = self._path_for(identifier)
            if not target.is_file():
                return False
            payload = self._read(identifier)
            self._validate_context_payload(payload, context)
            target.unlink()
            self._audit("erased", occurred_at=datetime.now(UTC), outcome="success")
            return True

    def purge_expired(self, *, now: datetime, dry_run: bool = True) -> dict[str, int]:
        current = self._parse_timestamp(self._timestamp(now))
        expired: list[Path] = []
        with self._lock:
            for target in sorted(self.root.glob(f"gah-*{_SUFFIX}")) if self.root.is_dir() else []:
                payload = self._read(target.name.removesuffix(_SUFFIX))
                if current >= self._parse_timestamp(payload.get("expires_at")):
                    expired.append(target)
            if not dry_run:
                for target in expired:
                    target.unlink()
                if expired:
                    self._audit("purged", occurred_at=current, outcome=f"deleted:{len(expired)}")
        return {
            "expired_count": len(expired),
            "deleted_count": 0 if dry_run else len(expired),
        }

    def audit_events(self) -> list[dict[str, object]]:
        path = self.root / _AUDIT
        if not path.is_file():
            return []
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]
