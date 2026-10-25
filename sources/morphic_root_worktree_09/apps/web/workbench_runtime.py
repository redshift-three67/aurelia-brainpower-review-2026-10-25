from __future__ import annotations

import hashlib
import json
import os
import threading
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from apps.web.durable_io import durable_mkdir_parents, durable_write_bytes
from apps.web.authority_ids import AuthorityIdError, validate_authority_id


STORE_DEFAULTS: dict[str, dict[str, Any]] = {
    "draft": {"draft": {}, "updated_at": None},
    "templates": {"templates": []},
    "run_traces": {"run_traces": []},
}
_NON_PERSISTED_DRAFT_KEYS = frozenset({"local_ai_enabled"})


def _copy_json(value: dict[str, Any]) -> dict[str, Any]:
    return json.loads(json.dumps(value))


def _persistent_draft(draft: dict[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in draft.items()
        if key not in _NON_PERSISTED_DRAFT_KEYS
    }


def _now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def _validate_payload_run_id(
    lookup: str,
    payload: dict[str, Any],
) -> None:
    if "run_id" not in payload:
        return
    if validate_authority_id(payload["run_id"]) != lookup:
        raise AuthorityIdError("run trace identity mismatch")


class WorkbenchRuntimeStore:
    def __init__(self, root: str | Path, tenant_id: str | None = None) -> None:
        base_root = Path(root)
        if tenant_id is None:
            self.root = base_root
        else:
            if not isinstance(tenant_id, str) or not tenant_id.strip():
                raise ValueError("tenant_id must be nonblank when supplied")
            tenant_hash = hashlib.sha256(tenant_id.encode("utf-8")).hexdigest()
            self.root = base_root / f"tenant-v1-{tenant_hash}"
        self._lock = threading.RLock()

    def _path_for(self, store_name: str) -> Path:
        if store_name not in STORE_DEFAULTS:
            raise KeyError(f"Unknown workbench runtime store: {store_name}")
        return self.root / f"{store_name}.json"

    @contextmanager
    def _process_lock(self, store_name: str):
        """Serialize one store across app processes, not just threads."""
        durable_mkdir_parents(self.root, mode=0o700)
        lock_path = self.root / f".{store_name}.lock"
        try:
            descriptor = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(descriptor, b"0")
            os.fsync(descriptor)
            os.close(descriptor)
        except FileExistsError:
            pass
        with lock_path.open("r+b") as handle:
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

    def _load_store(self, store_name: str) -> dict[str, Any]:
        path = self._path_for(store_name)
        if not path.exists():
            return _copy_json(STORE_DEFAULTS[store_name])
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise RuntimeError(
                f"Workbench runtime store '{store_name}' contains invalid JSON"
            ) from exc
        if store_name == "run_traces":
            if (
                not isinstance(payload, dict)
                or set(payload) != {"run_traces"}
                or not isinstance(payload["run_traces"], list)
            ):
                raise RuntimeError(
                    "Workbench run trace store schema is invalid"
                )
            store = {"run_traces": list(payload["run_traces"])}
            for entry in store.get("run_traces", []):
                try:
                    validate_authority_id(entry.get("run_id") if isinstance(entry, dict) else None)
                except AuthorityIdError as exc:
                    raise RuntimeError(
                        "Workbench run trace store contains invalid authority"
                    ) from exc
            return store
        store = _copy_json(STORE_DEFAULTS[store_name])
        if isinstance(payload, dict):
            store.update(payload)
        return store

    def _save_store(self, store_name: str, payload: dict[str, Any]) -> None:
        path = self._path_for(store_name)
        serialized = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
        durable_write_bytes(path, serialized.encode("utf-8"))

    def _preflight_run_traces(self) -> None:
        self._load_store("run_traces")

    def load_draft(self) -> dict[str, Any]:
        with self._lock, self._process_lock("draft"):
            return self._load_store("draft")

    def save_draft(self, draft: dict[str, Any]) -> dict[str, Any]:
        with self._lock, self._process_lock("draft"):
            payload = {"draft": _persistent_draft(draft), "updated_at": _now()}
            self._save_store("draft", payload)
            return payload

    def list_templates(self) -> list[dict[str, Any]]:
        with self._lock, self._process_lock("templates"):
            return list(self._load_store("templates").get("templates", []))

    def save_template(self, *, name: str, draft: dict[str, Any]) -> dict[str, Any]:
        """Create a new template identity; concurrent deletes affect only their ID."""
        with self._lock, self._process_lock("templates"):
            stamp = _now()
            entry = {
                "template_id": f"tpl-{uuid4().hex[:12]}",
                "name": name.strip(),
                "draft": _persistent_draft(draft),
                "created_at": stamp,
                "updated_at": stamp,
            }
            store = self._load_store("templates")
            store.setdefault("templates", []).insert(0, entry)
            self._save_store("templates", store)
            return entry

    def delete_template(self, template_id: str) -> bool:
        with self._lock, self._process_lock("templates"):
            store = self._load_store("templates")
            templates = list(store.get("templates", []))
            filtered = [
                entry for entry in templates if entry.get("template_id") != template_id
            ]
            if len(filtered) == len(templates):
                return False
            store["templates"] = filtered
            self._save_store("templates", store)
            return True

    def ensure_run_trace(
        self, run_id: str, seed: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        lookup = validate_authority_id(run_id)
        initial = seed or {}
        _validate_payload_run_id(lookup, initial)
        self._preflight_run_traces()
        with self._lock, self._process_lock("run_traces"):
            store = self._load_store("run_traces")
            traces = list(store.get("run_traces", []))
            for entry in traces:
                if entry.get("run_id") == lookup:
                    return entry

            stamp = _now()
            entry = {
                "run_id": lookup,
                "created_at": stamp,
                "updated_at": stamp,
                **initial,
            }
            traces.insert(0, entry)
            store["run_traces"] = traces
            self._save_store("run_traces", store)
            return entry

    def get_run_trace(self, run_id: str) -> dict[str, Any]:
        lookup = validate_authority_id(run_id)
        self._preflight_run_traces()
        with self._lock, self._process_lock("run_traces"):
            for entry in self._load_store("run_traces").get("run_traces", []):
                if entry.get("run_id") == lookup:
                    return entry
            raise KeyError(lookup)

    def finalize_run_trace_once(
        self, run_id: str, payload: dict[str, Any]
    ) -> dict[str, Any]:
        """Atomically transition one trace to a terminal state exactly once."""
        terminal_states = {"completed", "failed"}
        if payload.get("status") not in terminal_states:
            raise ValueError("run trace update is not terminal")
        lookup = validate_authority_id(run_id)
        _validate_payload_run_id(lookup, payload)
        self._preflight_run_traces()
        with self._lock, self._process_lock("run_traces"):
            store = self._load_store("run_traces")
            traces = list(store.get("run_traces", []))
            stamp = _now()
            for index, entry in enumerate(traces):
                if entry.get("run_id") != lookup:
                    continue
                if entry.get("status") in terminal_states:
                    raise ValueError("run trace already finalized")
                finalized = {
                    **entry,
                    **payload,
                    "run_id": lookup,
                    "created_at": entry.get("created_at", stamp),
                    "updated_at": stamp,
                }
                traces[index] = finalized
                store["run_traces"] = traces
                self._save_store("run_traces", store)
                return finalized
            raise KeyError(lookup)
