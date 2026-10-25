from __future__ import annotations

import asyncio
import json
import os
import re
import time
import uuid
from contextlib import asynccontextmanager, contextmanager
from dataclasses import dataclass
from pathlib import Path

from apps.web.durable_io import durable_mkdir_parents, durable_write_bytes


@contextmanager
def _authority_lock(path: Path):
    lock_path = path.with_suffix(path.suffix + ".lock")
    durable_mkdir_parents(lock_path.parent, mode=0o700)
    descriptor = os.open(lock_path, os.O_RDWR | os.O_CREAT, 0o600)
    with os.fdopen(descriptor, "r+b") as handle:
        if os.name == "nt":
            import msvcrt  # type: ignore[import-not-found]

            handle.seek(0, os.SEEK_END)
            if handle.tell() == 0:
                handle.write(b"0")
                handle.flush()
            handle.seek(0)
            while True:
                try:
                    msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
                    break
                except OSError:
                    time.sleep(0.01)
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


@dataclass(frozen=True, slots=True)
class _EmfAuthorityRevision:
    generation: int
    activation_id: str
    enabled: bool


class EmfTelemetryAuthority:
    """Durable generation authority for all productive EMF measurement paths."""

    def __init__(self, path: Path) -> None:
        self.path = Path(path)
        self.generation_path = self.path.with_suffix(self.path.suffix + ".generation")

    def is_enabled(self) -> bool:
        return self.begin_measurement() is not None

    def initialize_disabled_if_missing(self) -> None:
        with _authority_lock(self.path):
            if self.path.exists() or self.generation_path.exists():
                return
            generation_record = {
                "activation_id": uuid.uuid4().hex,
                "generation": 1,
            }
            durable_write_bytes(
                self.generation_path,
                json.dumps(
                    generation_record, sort_keys=True, separators=(",", ":")
                ).encode("utf-8"),
            )
            durable_write_bytes(
                self.path,
                json.dumps(
                    {"enabled": False, **generation_record},
                    sort_keys=True,
                    separators=(",", ":"),
                ).encode("utf-8"),
            )

    @staticmethod
    def _valid_record(payload: object) -> tuple[int, str] | None:
        if not isinstance(payload, dict):
            return None
        generation = payload.get("generation")
        activation_id = payload.get("activation_id")
        if (
            not isinstance(generation, int)
            or isinstance(generation, bool)
            or generation < 1
            or not isinstance(activation_id, str)
            or re.fullmatch(r"[0-9a-f]{32}", activation_id) is None
        ):
            return None
        return generation, activation_id

    def _current_lease_locked(self) -> str | None:
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
            generation_payload = json.loads(
                self.generation_path.read_text(encoding="utf-8")
            )
        except (OSError, ValueError, TypeError):
            return None
        main_record = self._valid_record(payload)
        generation_record = self._valid_record(generation_payload)
        if (
            not isinstance(payload, dict)
            or set(payload) != {"enabled", "generation", "activation_id"}
            or not isinstance(generation_payload, dict)
            or set(generation_payload) != {"generation", "activation_id"}
            or payload.get("enabled") is not True
            or main_record is None
            or main_record != generation_record
        ):
            return None
        generation, activation_id = main_record
        return f"{generation}:{activation_id}"

    def begin_measurement(self) -> str | None:
        with _authority_lock(self.path):
            return self._current_lease_locked()

    def measurement_is_current(self, lease: str | None) -> bool:
        return lease is not None and self.begin_measurement() == lease

    @contextmanager
    def publish_permit(self, lease: str | None):
        """Hold the final lease validation through a single payload emission."""
        with _authority_lock(self.path):
            yield lease is not None and self._current_lease_locked() == lease

    @asynccontextmanager
    async def async_publish_permit(self, lease: str | None):
        """Acquire the cross-process permit without blocking the event loop."""
        permit = self.publish_permit(lease)
        enter_task = asyncio.create_task(asyncio.to_thread(permit.__enter__))
        try:
            permitted = await asyncio.shield(enter_task)
        except asyncio.CancelledError:
            try:
                await enter_task
            except Exception:
                pass
            else:
                await asyncio.to_thread(permit.__exit__, None, None, None)
            raise
        try:
            yield permitted
        finally:
            exit_task = asyncio.create_task(
                asyncio.to_thread(permit.__exit__, None, None, None)
            )
            try:
                await asyncio.shield(exit_task)
            except asyncio.CancelledError:
                await exit_task
                raise

    def _write_revision_locked(
        self,
        *,
        generation: int,
        enabled: bool,
    ) -> _EmfAuthorityRevision:
        activation_id = uuid.uuid4().hex
        generation_record = {
            "activation_id": activation_id,
            "generation": generation,
        }
        durable_write_bytes(
            self.generation_path,
            json.dumps(
                generation_record, sort_keys=True, separators=(",", ":")
            ).encode("utf-8"),
        )
        durable_write_bytes(
            self.path,
            json.dumps(
                {"enabled": bool(enabled), **generation_record},
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8"),
        )
        return _EmfAuthorityRevision(generation, activation_id, bool(enabled))

    def set_enabled(self, enabled: bool) -> _EmfAuthorityRevision:
        with _authority_lock(self.path):
            generations: list[int] = []
            invalid_authority = False
            for authority_path in (self.path, self.generation_path):
                try:
                    candidate = json.loads(authority_path.read_text(encoding="utf-8"))
                except FileNotFoundError:
                    continue
                except (OSError, ValueError, TypeError):
                    invalid_authority = True
                    continue
                record = self._valid_record(candidate)
                if record is None:
                    # Legacy main files contain a generation but no activation id.
                    generation = candidate.get("generation") if isinstance(candidate, dict) else None
                    if authority_path == self.path and isinstance(generation, int) and generation >= 1:
                        generations.append(generation)
                        continue
                    invalid_authority = True
                    continue
                generations.append(record[0])
            if invalid_authority and not generations:
                raise RuntimeError("EMF generation authority is unreadable")
            generation = max(generations, default=0) + 1
            return self._write_revision_locked(
                generation=generation,
                enabled=enabled,
            )

    def compensate_to_disabled_if_current(
        self,
        revision: _EmfAuthorityRevision,
    ) -> bool:
        if not isinstance(revision, _EmfAuthorityRevision) or not revision.enabled:
            return False
        with _authority_lock(self.path):
            try:
                payload = json.loads(self.path.read_text(encoding="utf-8"))
                generation_payload = json.loads(
                    self.generation_path.read_text(encoding="utf-8")
                )
            except (OSError, ValueError, TypeError):
                return False
            if (
                not isinstance(payload, dict)
                or set(payload) != {"enabled", "generation", "activation_id"}
                or not isinstance(generation_payload, dict)
                or set(generation_payload) != {"generation", "activation_id"}
            ):
                return False
            main_record = self._valid_record(payload)
            generation_record = self._valid_record(generation_payload)
            expected_record = (revision.generation, revision.activation_id)
            if (
                payload.get("enabled") is not True
                or main_record != generation_record
                or main_record != expected_record
            ):
                return False
            self._write_revision_locked(
                generation=revision.generation + 1,
                enabled=False,
            )
            return True


def build_emf_telemetry_authority(
    runtime_dir: str | Path | None = None,
) -> EmfTelemetryAuthority:
    root = Path(runtime_dir) if runtime_dir is not None else Path.cwd() / "codex_tmp"
    authority = EmfTelemetryAuthority(root / "emf-telemetry-authority.json")
    authority.initialize_disabled_if_missing()
    return authority
