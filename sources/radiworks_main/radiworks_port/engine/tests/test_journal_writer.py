import hashlib
import threading
from pathlib import Path

import pytest
from cryptography.fernet import Fernet

from radiworks.entropy import EntropyProvider, RandomOrgSource, WebcamFeedSource
from radiworks import entropy_journal as journal_module
from radiworks.entropy_journal import EntropyJournal


class Probe:
    def __init__(self, wrapped):
        self.wrapped = wrapped
        self.flush_calls = 0

    def __getattr__(self, name):
        return getattr(self.wrapped, name)

    def flush(self):
        self.flush_calls += 1
        self.wrapped.flush()


def test_scope_reuses_lazy_writer_and_flushes_each_visible_record(monkeypatch, tmp_path):
    journal = EntropyJournal(tmp_path / "synthetic.journal", Fernet(Fernet.generate_key()))
    original_open = Path.open
    handles = []

    def tracked_open(self, mode="r", *args, **kwargs):
        handle = original_open(self, mode, *args, **kwargs)
        if self == journal.path and mode == "ab":
            handle = Probe(handle)
            handles.append(handle)
        return handle

    monkeypatch.setattr(Path, "open", tracked_open)
    with journal.write_scope():
        assert handles == []
        assert journal.append(11, "webcam", 0) == 1
        assert journal.path.read_bytes().count(b"\n") == 1
        assert not handles[0].closed
        assert journal.append(22, "os", 1) == 2
        assert journal.path.read_bytes().count(b"\n") == 2
        assert len(handles) == 1
        assert handles[0].flush_calls == 2
    assert handles[0].closed


def test_scope_closes_writer_when_body_raises(tmp_path):
    journal = EntropyJournal(tmp_path / "synthetic.journal", Fernet(Fernet.generate_key()))

    with pytest.raises(ValueError, match="algorithm failed"):
        with journal.write_scope():
            journal.append(11, "webcam", 0)
            raise ValueError("algorithm failed")

    assert journal.append(22, "os", 1) == 2
    moved = tmp_path / "renamed.journal"
    journal.path.rename(moved)
    moved.unlink()


def test_provider_write_scope_is_a_noop_without_journal():
    provider = EntropyProvider(
        seed=7,
        mode="seeded",
        random_org=RandomOrgSource(http_get=None),
    )
    with provider.journal_write_scope():
        assert provider.get_integer(0, 10) in range(11)

class CloseFailsBeforeClose:
    def __init__(self, wrapped):
        self.wrapped = wrapped
        self.close_calls = 0

    def __getattr__(self, name):
        return getattr(self.wrapped, name)

    def close(self):
        self.close_calls += 1
        if self.close_calls == 1:
            raise OSError("synthetic first close failure")
        self.wrapped.close()


def test_failed_close_gets_one_bounded_cleanup_attempt(monkeypatch, tmp_path):
    journal = EntropyJournal(tmp_path / "synthetic.journal", Fernet(Fernet.generate_key()))
    original_open = Path.open
    handles = []

    def tracked_open(self, mode="r", *args, **kwargs):
        handle = original_open(self, mode, *args, **kwargs)
        if self == journal.path and mode == "ab":
            handle = CloseFailsBeforeClose(handle)
            handles.append(handle)
        return handle

    monkeypatch.setattr(Path, "open", tracked_open)
    with pytest.raises(OSError, match="first close failure"):
        with journal.write_scope():
            journal.append(11, "webcam", 0)

    assert handles[0].close_calls == 2
    assert handles[0].closed
    with pytest.raises(RuntimeError):
        journal.append(22, "webcam", 0)
    moved = tmp_path / "closed.journal"
    journal.path.rename(moved)
    moved.unlink()


def test_unscoped_append_close_fault_gets_one_bounded_cleanup_attempt(monkeypatch, tmp_path):
    journal = EntropyJournal(tmp_path / "synthetic.journal", Fernet(Fernet.generate_key()))
    original_open = Path.open
    handles = []

    def tracked_open(self, mode="r", *args, **kwargs):
        handle = original_open(self, mode, *args, **kwargs)
        if self == journal.path and mode == "ab":
            handle = CloseFailsBeforeClose(handle)
            handles.append(handle)
        return handle

    monkeypatch.setattr(Path, "open", tracked_open)
    with pytest.raises(OSError, match="first close failure"):
        journal.append(11, "webcam", 0)

    assert handles[0].close_calls == 2
    assert handles[0].closed
    moved = tmp_path / "append-closed.journal"
    journal.path.rename(moved)
    moved.unlink()


def test_commit_close_fault_gets_one_bounded_cleanup_attempt(monkeypatch, tmp_path):
    journal = EntropyJournal(tmp_path / "synthetic.journal", Fernet(Fernet.generate_key()))
    with journal.write_scope():
        journal.append(11, "webcam", 0)

    original_open = Path.open
    handles = []

    def tracked_open(self, mode="r", *args, **kwargs):
        handle = original_open(self, mode, *args, **kwargs)
        if self == journal.path and mode == "r+b":
            handle = CloseFailsBeforeClose(handle)
            handles.append(handle)
        return handle

    monkeypatch.setattr(Path, "open", tracked_open)
    with pytest.raises(OSError, match="first close failure"):
        journal.commit()

    assert handles[0].close_calls == 2
    assert handles[0].closed
    with pytest.raises(RuntimeError):
        journal.append(22, "webcam", 0)
    moved = tmp_path / "commit-closed.journal"
    journal.path.rename(moved)
    moved.unlink()


class FaultProbe:
    def __init__(self, wrapped, *, short_write=False, flush_error=None):
        self.wrapped = wrapped
        self.short_write = short_write
        self.flush_error = flush_error

    def __getattr__(self, name):
        return getattr(self.wrapped, name)

    def write(self, data):
        if self.short_write:
            self.wrapped.write(data[:-1])
            return len(data) - 1
        return self.wrapped.write(data)

    def flush(self):
        if self.flush_error is not None:
            raise self.flush_error
        self.wrapped.flush()


class FailsCloseTwice:
    def __init__(self, wrapped):
        self.wrapped = wrapped
        self.close_calls = 0

    def __getattr__(self, name):
        return getattr(self.wrapped, name)

    def close(self):
        self.close_calls += 1
        raise OSError(f"synthetic close attempt {self.close_calls}")


def test_scope_keeps_format_order_cursor_digests_and_reopens_after_commit(tmp_path, monkeypatch):
    journal, fernet = new_journal(tmp_path)
    fsync_calls = []
    monkeypatch.setattr(journal_module.os, "fsync", lambda fd: fsync_calls.append(fd))

    with journal.write_scope():
        journal.append(101, "webcam", 0)
        journal.append(202, "os", 1)
        assert fsync_calls == []

    content = journal.path.read_bytes()
    tokens = content.splitlines()
    assert len(tokens) == 2
    assert journal.records() == [
        {"seed": 101, "source": "webcam", "segment": 0},
        {"seed": 202, "source": "os", "segment": 1},
    ]
    assert journal.cursor == 2
    assert journal.digest() == hashlib.sha256(content).hexdigest()
    assert journal.prefix_digest(1) == hashlib.sha256(tokens[0] + b"\n").hexdigest()
    assert journal.prefix_digest(2) == journal.digest()

    journal.commit()
    assert len(fsync_calls) == 1
    reopened = EntropyJournal(journal.path, fernet)
    assert reopened.cursor == 2
    assert reopened.records() == journal.records()
    assert reopened.append(303, "webcam", 2) == 3


@pytest.mark.parametrize(
    ("probe_kwargs", "message"),
    [
        ({"short_write": True}, "short write"),
        ({"flush_error": OSError("synthetic flush failure")}, "flush failure"),
    ],
)
def test_write_fault_does_not_advance_cursor_and_blocks_success(
    monkeypatch, tmp_path, probe_kwargs, message
):
    journal, _ = new_journal(tmp_path)
    assert journal.cursor == 0
    original_open = Path.open
    handles = []

    def tracked_open(self, mode="r", *args, **kwargs):
        handle = original_open(self, mode, *args, **kwargs)
        if self == journal.path and mode == "ab":
            handle = FaultProbe(handle, **probe_kwargs)
            handles.append(handle)
        return handle

    monkeypatch.setattr(Path, "open", tracked_open)
    with pytest.raises(OSError, match=message):
        with journal.write_scope():
            journal.append(11, "webcam", 0)

    assert journal._cursor == 0
    assert len(handles) == 1 and handles[0].closed
    with pytest.raises(RuntimeError):
        journal.append(22, "webcam", 0)
    with pytest.raises(RuntimeError):
        journal.commit()
    with pytest.raises(RuntimeError):
        journal.cursor
    with pytest.raises(RuntimeError):
        synthetic_provider(journal).checkpoint()


def test_fsync_fault_is_not_retried_and_blocks_checkpoint(monkeypatch, tmp_path):
    journal, _ = new_journal(tmp_path)
    with journal.write_scope():
        journal.append(11, "webcam", 0)
    fsync_calls = []

    def fail_fsync(fd):
        fsync_calls.append(fd)
        raise OSError("synthetic fsync failure")

    monkeypatch.setattr(journal_module.os, "fsync", fail_fsync)
    with pytest.raises(OSError, match="fsync failure"):
        journal.commit()
    assert journal._cursor == 1
    assert len(fsync_calls) == 1
    with pytest.raises(RuntimeError):
        journal.commit()
    with pytest.raises(RuntimeError):
        synthetic_provider(journal).checkpoint()


def test_nested_and_concurrent_scopes_are_rejected(tmp_path):
    journal, _ = new_journal(tmp_path)
    with journal.write_scope():
        with pytest.raises(RuntimeError, match="(?i)scope"):
            with journal.write_scope():
                pass

    entered = threading.Event()
    release = threading.Event()
    errors = []

    def hold_scope():
        try:
            with journal.write_scope():
                entered.set()
                if not release.wait(3):
                    raise TimeoutError("scope test was not released")
                journal.append(11, "webcam", 0)
        except BaseException as exc:
            errors.append(exc)

    thread = threading.Thread(target=hold_scope)
    thread.start()
    assert entered.wait(3)
    try:
        with pytest.raises(RuntimeError, match="(?i)scope"):
            with journal.write_scope():
                pass
    finally:
        release.set()
        thread.join(3)
    assert not thread.is_alive()
    assert errors == []
    assert journal.records() == [{"seed": 11, "source": "webcam", "segment": 0}]


def test_persistent_close_failure_retains_handle_and_first_fault(tmp_path):
    journal, _ = new_journal(tmp_path)
    original_open = Path.open
    handles = []

    def tracked_open(self, mode="r", *args, **kwargs):
        handle = original_open(self, mode, *args, **kwargs)
        if self == journal.path and mode == "ab":
            handle = FailsCloseTwice(handle)
            handles.append(handle)
        return handle

    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(Path, "open", tracked_open)
        with pytest.raises(OSError, match="close attempt 1"):
            with journal.write_scope():
                journal.append(11, "webcam", 0)

    assert handles[0].close_calls == 2
    assert journal._failed_writer is handles[0]
    assert str(journal._fault) == "synthetic close attempt 1"
    with pytest.raises(RuntimeError):
        journal.append(22, "webcam", 0)
    with pytest.raises(RuntimeError):
        journal.commit()
    handles[0].wrapped.close()


def test_body_error_and_original_cause_survive_persistent_close_failure(tmp_path):
    journal, _ = new_journal(tmp_path)
    original_open = Path.open
    handles = []

    def tracked_open(self, mode="r", *args, **kwargs):
        handle = original_open(self, mode, *args, **kwargs)
        if self == journal.path and mode == "ab":
            handle = FailsCloseTwice(handle)
            handles.append(handle)
        return handle

    original_cause = LookupError("original analysis cause")
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(Path, "open", tracked_open)
        with pytest.raises(ValueError, match="algorithm failure") as caught:
            with journal.write_scope():
                journal.append(11, "webcam", 0)
                raise ValueError("algorithm failure") from original_cause

    assert caught.value.__cause__ is original_cause
    assert any("close attempt 1" in note for note in caught.value.__notes__)
    assert journal._failed_writer is handles[0]
    with pytest.raises(RuntimeError):
        synthetic_provider(journal).checkpoint()
    handles[0].wrapped.close()


def test_provider_scope_forwards_writer_and_no_journal_is_noop(monkeypatch, tmp_path):
    journal, _ = new_journal(tmp_path)
    feed = WebcamFeedSource()
    feed.feed([321, 654])
    provider = EntropyProvider(
        mode="stochastic",
        feed=feed,
        random_org=RandomOrgSource(http_get=None),
        journal=journal,
    )
    original_open = Path.open
    handles = []

    def tracked_open(self, mode="r", *args, **kwargs):
        handle = original_open(self, mode, *args, **kwargs)
        if self == journal.path and mode == "ab":
            handles.append(handle)
        return handle

    monkeypatch.setattr(Path, "open", tracked_open)
    with provider.journal_write_scope():
        provider.get_boolean()
        provider.get_boolean()
        assert len(handles) == 1
    assert handles[0].closed
    assert journal.records() == [
        {"seed": 321, "source": "webcam", "segment": 0},
        {"seed": 654, "source": "webcam", "segment": 0},
    ]

    seeded = EntropyProvider(seed=7, mode="seeded", random_org=RandomOrgSource(http_get=None))
    with seeded.journal_write_scope():
        assert seeded.get_integer(0, 10) in range(11)


def new_journal(tmp_path):
    fernet = Fernet(Fernet.generate_key())
    return EntropyJournal(tmp_path / "synthetic.journal", fernet), fernet


def synthetic_provider(journal=None):
    feed = WebcamFeedSource()
    feed.feed([321, 654, 987])
    return EntropyProvider(
        mode="stochastic",
        feed=feed,
        random_org=RandomOrgSource(http_get=None),
        journal=journal,
    )

