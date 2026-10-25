"""Private, verschluesselte Rohseed-Journale fuer stochastic Session-Recovery."""

from __future__ import annotations

import hashlib
import json
import os
import uuid
from pathlib import Path
from typing import Any

from cryptography.fernet import Fernet, InvalidToken


class JournalConfigurationError(ValueError):
    pass


class EntropyJournal:
    def __init__(self, path: Path, fernet: Fernet) -> None:
        self.path = path
        self._fernet = fernet
        self._cursor: int | None = None
        self.path.parent.mkdir(parents=True, exist_ok=True)

    @property
    def journal_id(self) -> str:
        return self.path.stem

    @property
    def cursor(self) -> int:
        if self._cursor is None:
            self._cursor = (
                sum(1 for line in self.path.read_bytes().splitlines() if line)
                if self.path.exists()
                else 0
            )
        return self._cursor

    def append(self, seed: int, source: str, segment: int) -> int:
        record = json.dumps(
            {"seed": seed, "source": source, "segment": segment},
            separators=(",", ":"),
        ).encode("utf-8")
        token = self._fernet.encrypt(record)
        cursor_before = self.cursor
        with self.path.open("ab") as handle:
            handle.write(token + b"\n")
        self._cursor = cursor_before + 1
        return self._cursor

    def commit(self) -> None:
        if not self.path.exists():
            return
        with self.path.open("r+b") as handle:
            handle.flush()
            os.fsync(handle.fileno())

    def records(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        records: list[dict[str, Any]] = []
        for token in self.path.read_bytes().splitlines():
            if not token:
                continue
            try:
                record = json.loads(self._fernet.decrypt(token).decode("utf-8"))
            except (InvalidToken, UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise JournalConfigurationError("Entropiejournal ist nicht lesbar") from exc
            records.append(record)
        return records

    def digest(self) -> str:
        return hashlib.sha256(self.path.read_bytes() if self.path.exists() else b"").hexdigest()

    def prefix_digest(self, cursor: int) -> str:
        if cursor < 0:
            raise JournalConfigurationError("Entropiejournal-Cursor darf nicht negativ sein")
        tokens = self.path.read_bytes().splitlines() if self.path.exists() else []
        if any(not token for token in tokens) or len(tokens) < cursor:
            raise JournalConfigurationError("Entropiejournal ist kuerzer als der Checkpoint")
        return hashlib.sha256(b"\n".join(tokens[:cursor]) + (b"\n" if cursor else b"")).hexdigest()

    def matches_prefix_digest(self, cursor: int, expected_digest: str) -> bool:
        return self.prefix_digest(cursor) == expected_digest


class EntropyJournalStore:
    """Runtime-only Journalstore. Der Schluessel lebt ausschliesslich im Deployment."""

    def __init__(self, root: Path, key: str | bytes | None = None) -> None:
        self.root = Path(root)
        configured = key if key is not None else os.environ.get("RADIOWORKS_JOURNAL_KEY")
        if configured is None:
            raise JournalConfigurationError("RADIOWORKS_JOURNAL_KEY fehlt fuer stochastic Recovery")
        try:
            self._fernet = Fernet(configured.encode("ascii") if isinstance(configured, str) else configured)
        except (ValueError, TypeError) as exc:
            raise JournalConfigurationError("RADIOWORKS_JOURNAL_KEY ist kein gueltiger Fernet-Schluessel") from exc

    def create(self) -> EntropyJournal:
        return EntropyJournal(self.root / f"{uuid.uuid4().hex}.journal", self._fernet)

    def open(self, journal_id: str) -> EntropyJournal:
        if not journal_id or "/" in journal_id or "\\" in journal_id or "." in journal_id:
            raise JournalConfigurationError("ungueltige Entropiejournal-ID")
        path = self.root / f"{journal_id}.journal"
        if not path.exists():
            raise JournalConfigurationError("Entropiejournal fehlt")
        return EntropyJournal(path, self._fernet)
