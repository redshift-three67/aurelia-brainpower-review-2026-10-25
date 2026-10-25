"""Private, verschluesselte Rohseed-Journale fuer stochastic Session-Recovery."""

from __future__ import annotations

import hashlib
import json
import os
import threading
import uuid
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

from cryptography.fernet import Fernet, InvalidToken


class JournalConfigurationError(ValueError):
    pass


class EntropyJournalWriteError(RuntimeError):
    pass


class EntropyJournalScopeError(RuntimeError):
    pass


class EntropyJournal:
    def __init__(self, path: Path, fernet: Fernet) -> None:
        self.path = path
        self._fernet = fernet
        self._cursor: int | None = None
        self._write_lock = threading.RLock()
        self._scope_owner: int | None = None
        self._writer = None
        self._failed_writer = None
        self._fault: BaseException | None = None
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def _raise_if_faulted(self) -> None:
        if self._fault is not None:
            raise EntropyJournalWriteError(
                "Entropiejournal ist nach einem Schreibfehler unbrauchbar"
            ) from self._fault

    def _mark_fault(self, exc: BaseException) -> None:
        if self._fault is None:
            self._fault = exc

    def _close_handle(self, handle) -> None:
        try:
            handle.close()
        except BaseException as first:
            self._mark_fault(first)
            try:
                still_open = not handle.closed
            except BaseException:
                still_open = True
            if still_open:
                try:
                    handle.close()
                except BaseException as cleanup:
                    self._failed_writer = handle
                    first.add_note(
                        f"bounded close cleanup also failed: {cleanup}"
                    )
            raise

    def _close_writer(self) -> None:
        handle = self._writer
        self._writer = None
        if handle is None:
            return
        self._close_handle(handle)

    @property
    def journal_id(self) -> str:
        return self.path.stem

    @property
    def cursor(self) -> int:
        self._raise_if_faulted()
        if self._cursor is None:
            self._cursor = (
                sum(1 for line in self.path.read_bytes().splitlines() if line)
                if self.path.exists()
                else 0
            )
        return self._cursor

    @contextmanager
    def write_scope(self) -> Iterator[None]:
        if not self._write_lock.acquire(blocking=False):
            raise EntropyJournalScopeError("Entropiejournal-Scope ist bereits aktiv")
        owner = threading.get_ident()
        owns_scope = False
        try:
            self._raise_if_faulted()
            if self._scope_owner is not None:
                raise EntropyJournalScopeError("verschachtelter Entropiejournal-Scope")
            self._scope_owner = owner
            owns_scope = True
            try:
                yield
            except BaseException as primary:
                try:
                    self._close_writer()
                except BaseException as cleanup:
                    primary.add_note(
                        f"Entropiejournal-Scope konnte den Writer nicht schließen: {cleanup}"
                    )
                raise
            else:
                self._close_writer()
        finally:
            if owns_scope:
                self._scope_owner = None
            self._write_lock.release()

    def append(self, seed: int, source: str, segment: int) -> int:
        with self._write_lock:
            self._raise_if_faulted()
            record = json.dumps(
                {"seed": seed, "source": source, "segment": segment},
                separators=(",", ":"),
            ).encode("utf-8")
            token = self._fernet.encrypt(record)
            payload = token + b"\n"
            cursor_before = self.cursor
            owner = threading.get_ident()

            if self._scope_owner == owner:
                try:
                    if self._writer is None:
                        self._writer = self.path.open("ab")
                    written = self._writer.write(payload)
                    if written != len(payload):
                        raise OSError("short write while appending Entropiejournal")
                    self._writer.flush()
                except BaseException as exc:
                    self._mark_fault(exc)
                    raise
                self._cursor = cursor_before + 1
                return self._cursor

            handle = None
            write_error: BaseException | None = None
            try:
                handle = self.path.open("ab")
                written = handle.write(payload)
                if written != len(payload):
                    raise OSError("short write while appending Entropiejournal")
                handle.flush()
                self._cursor = cursor_before + 1
            except BaseException as exc:
                self._mark_fault(exc)
                write_error = exc

            if handle is not None:
                try:
                    self._close_handle(handle)
                except BaseException as cleanup:
                    self._mark_fault(cleanup)
                    if write_error is None:
                        write_error = cleanup
                    else:
                        write_error.add_note(
                            f"Entropiejournal konnte den Append-Writer nicht schließen: {cleanup}"
                        )
            if write_error is not None:
                raise write_error
            return self._cursor

    def commit(self) -> None:
        with self._write_lock:
            self._raise_if_faulted()
            if self._scope_owner is not None:
                raise EntropyJournalScopeError("Journal-Commit innerhalb eines Write-Scope")
            if not self.path.exists():
                return
            handle = None
            commit_error: BaseException | None = None
            try:
                handle = self.path.open("r+b")
                handle.flush()
                os.fsync(handle.fileno())
            except BaseException as exc:
                self._mark_fault(exc)
                commit_error = exc
            if handle is not None:
                try:
                    self._close_handle(handle)
                except BaseException as cleanup:
                    self._mark_fault(cleanup)
                    if commit_error is None:
                        commit_error = cleanup
                    else:
                        commit_error.add_note(
                            f"Entropiejournal konnte den Commit-Handle nicht schließen: {cleanup}"
                        )
            if commit_error is not None:
                raise commit_error

    def records(self) -> list[dict[str, Any]]:
        self._raise_if_faulted()
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
        self._raise_if_faulted()
        return hashlib.sha256(self.path.read_bytes() if self.path.exists() else b"").hexdigest()

    def prefix_digest(self, cursor: int) -> str:
        self._raise_if_faulted()
        if cursor < 0:
            raise JournalConfigurationError("Entropiejournal-Cursor darf nicht negativ sein")
        tokens = self.path.read_bytes().splitlines() if self.path.exists() else []
        if any(not token for token in tokens) or len(tokens) < cursor:
            raise JournalConfigurationError("Entropiejournal ist kuerzer als der Checkpoint")
        return hashlib.sha256(b"\n".join(tokens[:cursor]) + (b"\n" if cursor else b"")).hexdigest()

    def matches_prefix_digest(self, cursor: int, expected_digest: str) -> bool:
        self._raise_if_faulted()
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
