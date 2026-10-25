"""Atomare JSON-Schreibvorgaenge und private Recovery-Marker."""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
import threading
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

RECOVERY_SCHEMA = "radiworks.recovery.v1"


class RecoveryError(RuntimeError):
    """Eine unvollstaendige Persistenzoperation kann nicht sicher fortgesetzt werden."""


def _canonical_json(document: Any) -> bytes:
    return json.dumps(
        document,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def document_digest(document: dict[str, Any] | None) -> str | None:
    if document is None:
        return None
    return hashlib.sha256(_canonical_json(document)).hexdigest()


def _fsync_directory(directory: Path) -> None:
    """Best effort: Windows erlaubt kein fsync auf Verzeichnissen."""
    try:
        descriptor = os.open(directory, os.O_RDONLY)
    except OSError:
        return
    try:
        os.fsync(descriptor)
    except OSError:
        pass
    finally:
        os.close(descriptor)


def atomic_json_replace(path: Path, document: dict[str, Any]) -> None:
    """Schreibt ein JSON-Dokument durch fsync + atomaren Ersatz."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        suffix=".tmp",
        dir=path.parent,
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as handle:
            json.dump(document, handle, ensure_ascii=False, indent=2)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        _fsync_directory(path.parent)
    finally:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass


@dataclass(frozen=True)
class RecoveryTarget:
    store: str
    key: str
    before: dict[str, Any] | None
    after: dict[str, Any]


class RecoveryCoordinator:
    """Repariert Case-/Draft-Operationen ohne untrusted Pfadangaben zu verwenden."""

    def __init__(
        self,
        root: Path,
        *,
        stores: dict[str, Path],
        failure_hook: Callable[[str, int], None] | None = None,
    ) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self._stores = {name: Path(path).resolve() for name, path in stores.items()}
        self._failure_hook = failure_hook
        self._lock = threading.RLock()

    def apply(self, kind: str, targets: list[RecoveryTarget]) -> str:
        """Persistiert einen vollstaendigen Mehrdatei-Endzustand oder dessen Repair-Marker."""
        if not targets:
            raise ValueError("Recovery-Operation braucht mindestens ein Ziel")
        marker = self._new_marker(kind, targets)
        marker_path = self.root / f"{marker['operationId']}.json"
        with self._lock:
            if any(self.root.glob("*.json")):
                raise RecoveryError("Ausstehende Recovery braucht einen kontrollierten Neustart")
            try:
                atomic_json_replace(marker_path, marker)
                self._checkpoint("prepared", 0)
                marker["state"] = "applying"
                atomic_json_replace(marker_path, marker)
                self._apply_marker(marker, marker_path)
            except RecoveryError:
                raise
            except Exception as exc:
                raise RecoveryError("Persistenzoperation braucht einen kontrollierten Neustart") from exc
        return marker["operationId"]

    def ensure_no_pending(self) -> None:
        """Verhindert neue Stick-Pad-Schreibvorgaenge bis zum kontrollierten Recovery-Start."""
        with self._lock:
            if any(self.root.glob("*.json")):
                raise RecoveryError("Ausstehende Recovery braucht einen kontrollierten Neustart")

    def recover(self) -> None:
        """Vervollstaendigt markierte Operationen vor dem Start der Anwendung."""
        with self._lock:
            for marker_path in sorted(self.root.glob("*.json")):
                try:
                    marker = json.loads(marker_path.read_text(encoding="utf-8"))
                    self._validate_marker(marker)
                    if marker["state"] == "failed":
                        raise RecoveryError("Recovery-Marker ist als fehlgeschlagen markiert")
                    if marker["state"] not in {"prepared", "applying", "completed"}:
                        raise RecoveryError("Recovery-Marker hat einen ungueltigen Zustand")
                    self._apply_marker(marker, marker_path)
                except RecoveryError:
                    raise
                except (OSError, ValueError, json.JSONDecodeError) as exc:
                    raise RecoveryError(
                        f"Recovery-Marker kann nicht sicher verarbeitet werden: {marker_path.name}"
                    ) from exc

    def _new_marker(self, kind: str, targets: list[RecoveryTarget]) -> dict[str, Any]:
        if not isinstance(kind, str) or not kind:
            raise ValueError("Recovery-Operation braucht einen Typ")
        marker_targets = []
        for target in targets:
            self._target_path(target.store, target.key)
            if not isinstance(target.after, dict):
                raise ValueError("Recovery-Ziel braucht ein JSON-Objekt")
            marker_targets.append(
                {
                    "store": target.store,
                    "key": target.key,
                    "beforeSha256": document_digest(target.before),
                    "afterSha256": document_digest(target.after),
                    "document": target.after,
                }
            )
        return {
            "schema": RECOVERY_SCHEMA,
            "operationId": uuid.uuid4().hex,
            "kind": kind,
            "state": "prepared",
            "createdAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "targets": marker_targets,
        }

    def _apply_marker(self, marker: dict[str, Any], marker_path: Path) -> None:
        self._validate_marker(marker)
        for index, target in enumerate(marker["targets"]):
            path = self._target_path(target["store"], target["key"])
            actual = self._read_document(path)
            actual_digest = document_digest(actual)
            if actual_digest == target["afterSha256"]:
                continue
            if actual_digest != target["beforeSha256"]:
                self._mark_failed(marker, marker_path, "digest-conflict")
                raise RecoveryError(
                    f"Recovery-Operation kann nicht sicher fortgesetzt werden: {marker['operationId']}"
                )
            atomic_json_replace(path, target["document"])
            self._checkpoint("target-replaced", index)

        for target in marker["targets"]:
            path = self._target_path(target["store"], target["key"])
            if document_digest(self._read_document(path)) != target["afterSha256"]:
                self._mark_failed(marker, marker_path, "verification-failed")
                raise RecoveryError(
                    f"Recovery-Operation kann nicht verifiziert werden: {marker['operationId']}"
                )
        marker["state"] = "completed"
        atomic_json_replace(marker_path, marker)
        self._checkpoint("completed", len(marker["targets"]))
        marker_path.unlink()
        _fsync_directory(marker_path.parent)

    def _mark_failed(self, marker: dict[str, Any], marker_path: Path, code: str) -> None:
        marker["state"] = "failed"
        marker["failure"] = {"code": code}
        atomic_json_replace(marker_path, marker)

    def _validate_marker(self, marker: dict[str, Any]) -> None:
        if not isinstance(marker, dict) or marker.get("schema") != RECOVERY_SCHEMA:
            raise RecoveryError("Recovery-Marker hat ein unbekanntes Schema")
        if not isinstance(marker.get("operationId"), str) or not marker["operationId"]:
            raise RecoveryError("Recovery-Marker hat keine Operation-ID")
        targets = marker.get("targets")
        if not isinstance(targets, list) or not targets:
            raise RecoveryError("Recovery-Marker hat keine Ziele")
        for target in targets:
            if not isinstance(target, dict):
                raise RecoveryError("Recovery-Marker enthaelt ein ungueltiges Ziel")
            self._target_path(target.get("store"), target.get("key"))
            if not isinstance(target.get("document"), dict):
                raise RecoveryError("Recovery-Marker enthaelt kein JSON-Ziel")
            if document_digest(target["document"]) != target.get("afterSha256"):
                raise RecoveryError("Recovery-Marker hat einen ungueltigen Nachher-Hash")
            if target.get("beforeSha256") is not None and not isinstance(
                target["beforeSha256"], str
            ):
                raise RecoveryError("Recovery-Marker hat einen ungueltigen Vorher-Hash")

    def _target_path(self, store: Any, key: Any) -> Path:
        if not isinstance(store, str) or store not in self._stores:
            raise RecoveryError("Recovery-Marker referenziert einen unbekannten Store")
        if not isinstance(key, str) or not key.endswith(".json") or Path(key).name != key:
            raise RecoveryError("Recovery-Marker referenziert ein ungueltiges Ziel")
        root = self._stores[store]
        path = (root / key).resolve()
        try:
            path.relative_to(root)
        except ValueError as exc:
            raise RecoveryError("Recovery-Marker liegt ausserhalb des Runtime-Home") from exc
        return path

    @staticmethod
    def _read_document(path: Path) -> dict[str, Any] | None:
        if not path.exists():
            return None
        try:
            document = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise RecoveryError("Persistiertes JSON ist nicht lesbar") from exc
        if not isinstance(document, dict):
            raise RecoveryError("Persistiertes JSON ist kein Objekt")
        return document

    def _checkpoint(self, phase: str, index: int) -> None:
        if self._failure_hook is not None:
            self._failure_hook(phase, index)
