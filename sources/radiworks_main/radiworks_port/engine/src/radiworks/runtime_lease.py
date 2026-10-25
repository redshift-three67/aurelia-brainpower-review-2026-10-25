"""Cross-process lease for one active engine per runtime home."""

from __future__ import annotations

import os
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator


@contextmanager
def runtime_home_lease(base_dir: Path) -> Iterator[None]:
    """Hold an OS lock for the complete app lifespan; keep the lock file in place."""
    home = Path(base_dir).expanduser().resolve()
    home.mkdir(parents=True, exist_ok=True)
    lock_path = home / ".engine.lock"
    with lock_path.open("a+b") as handle:
        handle.seek(0, os.SEEK_END)
        if handle.tell() == 0:
            handle.write(b"\0")
            handle.flush()
        handle.seek(0)
        if os.name == "nt":
            import msvcrt

            try:
                msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
            except OSError as exc:
                raise RuntimeError(
                    "Runtime-Home bereits von einer Engine verwendet oder Sperre nicht verfügbar"
                ) from exc
        else:
            import fcntl

            try:
                fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except OSError as exc:
                raise RuntimeError(
                    "Runtime-Home bereits von einer Engine verwendet oder Sperre nicht verfügbar"
                ) from exc
        try:
            yield
        finally:
            handle.seek(0)
            if os.name == "nt":
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
