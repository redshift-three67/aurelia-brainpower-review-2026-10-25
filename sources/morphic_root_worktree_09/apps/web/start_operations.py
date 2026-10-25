"""Durable idempotency authority for non-repeatable web start operations."""

from __future__ import annotations

import hashlib
import json
import os
import re
import threading
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Iterator, Literal, TypedDict

from apps.web.durable_io import durable_mkdir_parents, durable_write_bytes
from apps.web.authority_ids import (
    AuthorityIdError,
    validate_harmonization_job_id_for_creation,
    validate_scan_job_id_for_creation,
)


_OPERATION_KEY_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{7,127}$")
_OPERATION_KINDS = {"scan", "harmonization"}


def _validate_operation_job_id(kind: str, job_id: object) -> str:
    try:
        if kind == "scan":
            return validate_scan_job_id_for_creation(job_id)
        if kind == "harmonization":
            return validate_harmonization_job_id_for_creation(job_id)
    except AuthorityIdError as exc:
        raise StartOperationConflictError("start operation job id is invalid") from exc
    raise StartOperationConflictError("start operation kind is invalid")


class StartOperationError(ValueError):
    """Raised when a start-operation record or key is invalid."""


class StartOperationConflictError(StartOperationError):
    """Raised when existing durable authority cannot be safely replaced."""


class StartOperationOwnershipError(StartOperationConflictError):
    """Raised when a record at an owner-bound identity names another owner."""


class StartOperationRecord(TypedDict):
    schema_version: int
    kind: str
    owner_id: str
    key_sha256: str
    request_sha256: str
    state: Literal["pending", "completed", "failed"]
    job_id: str | None
    created_at: str
    updated_at: str


@dataclass
class StartOperationClaim:
    """A process-exclusive claim held for one complete start/replay decision."""

    _store: "StartOperationStore"
    _path: Path
    record: StartOperationRecord
    is_new: bool

    @property
    def state(self) -> str:
        return self.record["state"]

    @property
    def job_id(self) -> str:
        job_id = self.record.get("job_id")
        if not isinstance(job_id, str) or not job_id:
            raise StartOperationConflictError("start operation lacks job authority")
        return _validate_operation_job_id(self.record.get("kind", ""), job_id)

    def complete(self, job_id: str) -> None:
        supplied_job_id = _validate_operation_job_id(
            self.record.get("kind", ""), job_id
        )
        if supplied_job_id != self.job_id:
            raise StartOperationConflictError("start operation job identity mismatch")
        if self.state == "completed":
            return
        if self.state != "pending":
            raise StartOperationConflictError(
                f"{self.state} start operation cannot be completed"
            )
        self.record["state"] = "completed"
        self.record["updated_at"] = datetime.now(UTC).isoformat()
        durable_write_bytes(self._path, self._store._encode(self.record))

    def fail_before_creation(self) -> None:
        if self.state != "pending":
            raise StartOperationConflictError(
                f"{self.state} start operation cannot be failed"
            )
        self.record["state"] = "failed"
        self.record["job_id"] = None
        self.record["updated_at"] = datetime.now(UTC).isoformat()
        durable_write_bytes(self._path, self._store._encode(self.record))


class StartOperationStore:
    """Persist fail-closed operation claims before a job is created.

    A completed claim replays the existing job. A pending/failed claim never
    permits a second creation, including after a process restart.
    """

    def __init__(self, root: str | Path):
        self.root = Path(root).resolve()
        durable_mkdir_parents(self.root, mode=0o700)
        self._lock = threading.RLock()

    @staticmethod
    def validate_key(key: str) -> str:
        normalized = str(key or "").strip()
        if not _OPERATION_KEY_RE.fullmatch(normalized):
            raise StartOperationError("invalid idempotency key")
        return normalized

    @staticmethod
    def _identity(kind: str, key: str, owner_id: str) -> tuple[str, str, str]:
        if kind not in _OPERATION_KINDS:
            raise StartOperationError("invalid start operation kind")
        normalized_key = StartOperationStore.validate_key(key)
        normalized_owner = str(owner_id or "").strip()
        if not normalized_owner:
            raise StartOperationError("start operation owner is required")
        key_sha256 = hashlib.sha256(normalized_key.encode("utf-8")).hexdigest()
        identity = hashlib.sha256(
            f"{kind}\0{normalized_owner}\0{normalized_key}".encode("utf-8")
        ).hexdigest()
        return normalized_owner, key_sha256, identity

    def _path(self, kind: str, key: str, owner_id: str) -> tuple[Path, str, str]:
        normalized_owner, key_sha256, identity = self._identity(kind, key, owner_id)
        return self.root / f"{identity}.json", normalized_owner, key_sha256

    @contextmanager
    def _process_lock(self, path: Path) -> Iterator[None]:
        lock_path = self.root / f".{path.stem}.lock"
        durable_mkdir_parents(lock_path.parent, mode=0o700)
        with lock_path.open("a+b") as handle:
            if os.fstat(handle.fileno()).st_size == 0:
                handle.write(b"0")
                handle.flush()
                os.fsync(handle.fileno())
            handle.seek(0)
            if os.name == "nt":
                import msvcrt

                msvcrt.locking(handle.fileno(), msvcrt.LK_LOCK, 1)
            else:
                import fcntl

                fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
            try:
                yield
            finally:
                handle.seek(0)
                if os.name == "nt":
                    msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
                else:
                    fcntl.flock(handle.fileno(), fcntl.LOCK_UN)

    @staticmethod
    def _job_id(kind: str, path: Path) -> str:
        if kind == "scan":
            return f"scan-op-{path.stem[:24]}"
        return f"harm_{path.stem[:24]}"

    @staticmethod
    def _encode(record: StartOperationRecord) -> bytes:
        return (json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n").encode(
            "utf-8"
        )

    @staticmethod
    def _read(path: Path) -> StartOperationRecord:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise StartOperationConflictError(
                "start operation record is unreadable"
            ) from exc
        required = {
            "schema_version",
            "kind",
            "owner_id",
            "key_sha256",
            "request_sha256",
            "state",
            "job_id",
            "created_at",
            "updated_at",
        }
        if not isinstance(payload, dict) or set(payload) != required:
            raise StartOperationConflictError("start operation record fields are invalid")
        schema_version = payload["schema_version"]
        if (
            isinstance(schema_version, bool)
            or not isinstance(schema_version, int)
            or schema_version != 1
        ):
            raise StartOperationConflictError("start operation schema is unsupported")
        kind = payload["kind"]
        if not isinstance(kind, str) or kind not in _OPERATION_KINDS:
            raise StartOperationConflictError("start operation kind is invalid")
        state = payload["state"]
        if not isinstance(state, str) or state not in {"pending", "completed", "failed"}:
            raise StartOperationConflictError("start operation state is invalid")
        owner_id = payload["owner_id"]
        if not isinstance(owner_id, str) or not owner_id:
            raise StartOperationConflictError("start operation owner is invalid")
        for field in ("key_sha256", "request_sha256"):
            digest = payload[field]
            if not isinstance(digest, str) or re.fullmatch(r"[0-9a-f]{64}", digest) is None:
                raise StartOperationConflictError(
                    f"start operation {field} is invalid"
                )
        for field in ("created_at", "updated_at"):
            timestamp = payload[field]
            if not isinstance(timestamp, str) or not timestamp:
                raise StartOperationConflictError(
                    f"start operation {field} is invalid"
                )
        job_id = payload["job_id"]
        if state in {"pending", "completed"} and not (
            isinstance(job_id, str) and job_id
        ):
            raise StartOperationConflictError("start operation lacks job id")
        if state == "failed" and job_id is not None:
            raise StartOperationConflictError("failed start operation contains job id")
        if state in {"pending", "completed"}:
            _validate_operation_job_id(kind, job_id)
        return payload  # type: ignore[return-value]

    def _claim_locked(
        self,
        *,
        path: Path,
        kind: str,
        normalized_owner: str,
        key_sha256: str,
        request_sha256: str,
    ) -> tuple[StartOperationRecord, bool]:
        if path.exists():
            record = self._read(path)
            if (
                record["kind"] != kind
                or record["owner_id"] != normalized_owner
                or record["key_sha256"] != key_sha256
                or record["request_sha256"] != request_sha256
            ):
                raise StartOperationConflictError("start operation identity mismatch")
            return record, False
        now = datetime.now(UTC).isoformat()
        record: StartOperationRecord = {
            "schema_version": 1,
            "kind": kind,
            "owner_id": normalized_owner,
            "key_sha256": key_sha256,
            "request_sha256": request_sha256,
            "state": "pending",
            "job_id": self._job_id(kind, path),
            "created_at": now,
            "updated_at": now,
        }
        durable_write_bytes(path, self._encode(record))
        return record, True

    @contextmanager
    def operation(
        self,
        *,
        kind: str,
        key: str,
        owner_id: str,
        request_sha256: str,
    ) -> Iterator[StartOperationClaim]:
        path, normalized_owner, key_sha256 = self._path(kind, key, owner_id)
        normalized_request_sha256 = str(request_sha256 or "").strip().lower()
        if not re.fullmatch(r"[0-9a-f]{64}", normalized_request_sha256):
            raise StartOperationError("invalid start operation request hash")
        with self._lock, self._process_lock(path):
            record, is_new = self._claim_locked(
                path=path,
                kind=kind,
                normalized_owner=normalized_owner,
                key_sha256=key_sha256,
                request_sha256=normalized_request_sha256,
            )
            yield StartOperationClaim(self, path, record, is_new)

    @contextmanager
    def inspect(
        self,
        *,
        kind: str,
        key: str,
        owner_id: str,
    ) -> Iterator[StartOperationClaim | None]:
        """Inspect one owner-bound operation without creating durable authority."""
        path, normalized_owner, key_sha256 = self._path(kind, key, owner_id)
        with self._lock, self._process_lock(path):
            if not path.exists():
                yield None
                return
            record = self._read(path)
            if record["owner_id"] != normalized_owner:
                raise StartOperationOwnershipError("start operation owner mismatch")
            if record["kind"] != kind or record["key_sha256"] != key_sha256:
                raise StartOperationConflictError("start operation identity mismatch")
            yield StartOperationClaim(self, path, record, False)

    def begin(
        self,
        *,
        kind: str,
        key: str,
        owner_id: str,
        request_sha256: str,
    ) -> StartOperationRecord | None:
        with self.operation(
            kind=kind,
            key=key,
            owner_id=owner_id,
            request_sha256=request_sha256,
        ) as claim:
            return None if claim.is_new else dict(claim.record)  # type: ignore[return-value]

    def complete(self, *, kind: str, key: str, owner_id: str, job_id: str) -> None:
        path, _, _ = self._path(kind, key, owner_id)
        with self._lock, self._process_lock(path):
            record = self._read(path)
            claim = StartOperationClaim(self, path, record, False)
            claim.complete(job_id)

    def fail(self, *, kind: str, key: str, owner_id: str) -> None:
        path, _, _ = self._path(kind, key, owner_id)
        with self._lock, self._process_lock(path):
            record = self._read(path)
            claim = StartOperationClaim(self, path, record, False)
            claim.fail_before_creation()
