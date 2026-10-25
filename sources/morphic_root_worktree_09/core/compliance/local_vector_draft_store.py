"""Temporary-only DPAPI persistence feasibility store for E4.2 vector drafts.

The store is deliberately not imported by web runtime, scan, report, job, trace,
or manifest paths. It accepts only an OS-temporary directory and stores the raw
draft exclusively as DPAPI-protected bytes for the current Windows user.
"""
from __future__ import annotations

import json
import re
import tempfile
from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import uuid4

from apps.web.client_context_contracts import LocalVectorDraftEnvelope
from apps.web.durable_io import durable_mkdir_parents
from core.compliance.windows_protection import (
    protect_for_current_user,
    restrict_directory_to_current_user,
    unprotect_for_current_user,
)


_DRAFT_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,127}$")
_SUFFIX = ".dpapi"


class LocalVectorDraftStore:
    """Persist explicitly consented local-vector drafts in a temporary DPAPI store."""

    def __init__(self, root: str | Path) -> None:
        candidate = Path(root).resolve()
        temporary_root = Path(tempfile.gettempdir()).resolve()
        try:
            candidate.relative_to(temporary_root)
        except ValueError as exc:
            raise ValueError("local vector draft root must be below the operating system temporary directory") from exc
        self.root = candidate

    @staticmethod
    def _draft_id(value: str) -> str:
        cleaned = str(value or "").strip()
        if not _DRAFT_ID.fullmatch(cleaned):
            raise ValueError("draft_id must be canonical")
        return cleaned

    @staticmethod
    def _timestamp(value: datetime) -> str:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("stored_at must be timezone-aware")
        return value.astimezone(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    @staticmethod
    def _parse_timestamp(value: object) -> datetime:
        try:
            parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValueError("local vector draft timestamp is invalid") from exc
        if parsed.tzinfo is None or parsed.utcoffset() is None:
            raise ValueError("local vector draft timestamp is invalid")
        return parsed.astimezone(UTC)

    def _path_for(self, draft_id: str) -> Path:
        return self.root / f"{self._draft_id(draft_id)}{_SUFFIX}"

    def _load_record(self, draft_id: str) -> tuple[datetime, LocalVectorDraftEnvelope]:
        protected = self._path_for(draft_id).read_bytes()
        plaintext = unprotect_for_current_user(protected)
        try:
            payload = json.loads(plaintext.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError("local vector draft payload is invalid") from exc
        if not isinstance(payload, dict) or not isinstance(payload.get("draft"), dict):
            raise ValueError("local vector draft payload is invalid")
        return self._parse_timestamp(payload.get("stored_at")), LocalVectorDraftEnvelope.model_validate(
            payload["draft"]
        )

    def save(
        self,
        draft_id: str,
        draft: LocalVectorDraftEnvelope,
        *,
        stored_at: datetime | None = None,
    ) -> dict[str, object]:
        identifier = self._draft_id(draft_id)
        durable_mkdir_parents(self.root, mode=0o700)
        restrict_directory_to_current_user(self.root)
        payload = {
            "stored_at": self._timestamp(stored_at or datetime.now(UTC)),
            "draft": draft.model_dump(mode="json"),
        }
        plaintext = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        protected = protect_for_current_user(plaintext, description="morphic-local-vector-draft")
        target = self._path_for(identifier)
        temporary = target.with_suffix(f"{_SUFFIX}.tmp.{uuid4().hex[:8]}")
        temporary.write_bytes(protected)
        temporary.replace(target)
        return {"draft_id": identifier, **draft.safe_summary()}

    def load(self, draft_id: str) -> LocalVectorDraftEnvelope:
        return self._load_record(draft_id)[1]

    def list_safe(self) -> list[dict[str, object]]:
        if not self.root.is_dir():
            return []
        result: list[dict[str, object]] = []
        for path in sorted(self.root.glob(f"*{_SUFFIX}")):
            draft_id = path.name.removesuffix(_SUFFIX)
            result.append({"draft_id": draft_id, **self.load(draft_id).safe_summary()})
        return result

    def erasure_dry_run(self, *, now: datetime) -> list[dict[str, object]]:
        current = self._parse_timestamp(self._timestamp(now))
        candidates: list[dict[str, object]] = []
        for path in sorted(self.root.glob(f"*{_SUFFIX}")) if self.root.is_dir() else []:
            draft_id = path.name.removesuffix(_SUFFIX)
            stored_at, draft = self._load_record(draft_id)
            summary = draft.safe_summary()
            retention_days = [
                int(vector["retention_days"])
                for vector in summary["vectors"]
                if isinstance(vector, dict) and "retention_days" in vector
            ]
            if not retention_days:
                continue
            expires_at = stored_at + timedelta(days=min(retention_days))
            if current >= expires_at:
                candidates.append(
                    {
                        "draft_id": draft_id,
                        "reason": "retention_expired",
                        "stored_at": self._timestamp(stored_at),
                        "expires_at": self._timestamp(expires_at),
                        **summary,
                    }
                )
        return candidates

    def erase(self, draft_id: str, *, confirmation_id: str) -> bool:
        identifier = self._draft_id(draft_id)
        if self._draft_id(confirmation_id) != identifier:
            raise ValueError("erase confirmation_id must exactly match draft_id")
        target = self._path_for(identifier)
        if not target.exists():
            return False
        target.unlink()
        return True
