"""Bounded binary protocol tests for the personal CPU job stream."""
import subprocess
import sys
import threading
import time

import pytest

from radiworks.core.personal_stream import (
    MAX_OUTPUT_FRAME_BYTES,
    PersonalStreamError,
    PersonalWorkerStream,
)


def child(code):
    return subprocess.Popen(
        [sys.executable, "-c", code],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        bufsize=0,
    )


def stream(code, payload=b"{}\n"):
    owned = PersonalWorkerStream(child(code), payload)
    owned.start()
    return owned


def deadline(seconds=10):
    return time.monotonic() + seconds


@pytest.mark.parametrize(
    "wire",
    [
        b"\xff\n",
        b"{broken}\n",
        b"{\"rows\":[],\"rows\":[]}\n",
        b"{\"rows\":[]} trailing\n",
        b"{\"rows\":[]}",
    ],
)
def test_stdout_reader_rejects_invalid_bounded_frames(wire):
    code = f"import sys; sys.stdin.buffer.read(); sys.stdout.buffer.write({wire!r}); sys.stdout.buffer.flush()"
    owned = stream(code)
    try:
        with pytest.raises(PersonalStreamError) as error:
            owned.next_frame(deadline())
        assert error.value.code == "worker_protocol"
    finally:
        owned.cleanup()


def test_stdout_reader_rejects_oversized_frame():
    code = (
        "import sys; sys.stdin.buffer.read(); "
        "sys.stdout.buffer.write(b'{\"x\":\"' + b'x' * "
        f"{MAX_OUTPUT_FRAME_BYTES} + b'\"}}\\n'); sys.stdout.buffer.flush()"
    )
    owned = stream(code)
    try:
        with pytest.raises(PersonalStreamError) as error:
            owned.next_frame(deadline())
        assert error.value.code == "worker_protocol"
    finally:
        owned.cleanup()


def test_eof_before_completion_is_reported_without_a_frame():
    owned = stream("import sys; sys.stdin.buffer.read()")
    try:
        assert owned.next_frame(deadline()) is None
    finally:
        owned.cleanup()


def test_completion_requires_eof_and_rejects_a_trailing_frame():
    code = (
        "import sys; sys.stdin.buffer.read(); "
        "sys.stdout.buffer.write(b'{\"rows\":[]}\\n{\"done\":1}\\n{\"rows\":[]}\\n'); "
        "sys.stdout.buffer.flush()"
    )
    owned = stream(code)
    try:
        assert owned.next_frame(deadline()) == {"rows": []}
        assert owned.next_frame(deadline()) == {"done": 1}
        with pytest.raises(PersonalStreamError) as error:
            owned.finish(deadline())
        assert error.value.code == "worker_protocol"
    finally:
        owned.cleanup()


def test_nonzero_exit_after_done_is_a_worker_failure():
    code = (
        "import sys; sys.stdin.buffer.read(); "
        "sys.stdout.buffer.write(b'{\"done\":1}\\n'); sys.stdout.buffer.flush(); sys.exit(7)"
    )
    owned = stream(code)
    try:
        assert owned.next_frame(deadline()) == {"done": 1}
        with pytest.raises(PersonalStreamError) as error:
            owned.finish(deadline())
        assert error.value.code == "worker_failed"
    finally:
        owned.cleanup()


def test_blocked_input_write_is_bounded_by_the_first_frame_deadline():
    code = "import time; time.sleep(30)"
    owned = stream(code, b"x" * (4 * 1024 * 1024) + b"\n")
    try:
        with pytest.raises(PersonalStreamError) as error:
            owned.next_frame(deadline(0.15))
        assert error.value.code == "worker_timeout"
    finally:
        owned.cleanup()
    assert owned.process.poll() is not None
    assert owned.threads_stopped


def test_cancel_stops_owned_child_and_joins_all_stream_threads():
    code = "import sys,time; sys.stdin.buffer.read(); time.sleep(30)"
    owned = stream(code)
    cancelled = threading.Event()
    try:
        cancelled.set()
        with pytest.raises(PersonalStreamError) as error:
            owned.next_frame(deadline(), cancelled)
        assert error.value.code == "cancelled"
    finally:
        owned.cleanup()
    assert owned.process.poll() is not None
    assert owned.threads_stopped



def _fake_rows(payload, indices):
    return [
        {
            "inputIndex": index,
            "rate": payload["rates"][index],
            "score": 0.5,
            "intensity": 1.0,
            "matrix": [[0] * 12 for _ in range(12)],
        }
        for index in indices
    ]


def test_worker_stream_emits_ordered_blocks_then_exact_completion(monkeypatch):
    from radiworks.core import personal_worker

    monkeypatch.setattr(personal_worker, "rank_personal_block", _fake_rows)
    digest = "a" * 64
    payload = {"implementationHash": digest, "rates": [f"Rate {i}" for i in range(23)]}
    frames = list(personal_worker.stream_frames(
        {"input": payload, "implementationHash": digest},
        digest,
        lambda: digest,
    ))
    assert [frame["rows"][0]["inputIndex"] for frame in frames[:-1]] == [0, 21]
    assert [len(frame["rows"]) for frame in frames[:-1]] == [21, 2]
    assert frames[-1] == {"done": 23}


def test_worker_stream_stops_after_implementation_hash_drift(monkeypatch):
    from radiworks.core import personal_worker

    monkeypatch.setattr(personal_worker, "rank_personal_block", _fake_rows)
    digest = "a" * 64
    checks = iter([digest, "b" * 64])
    payload = {"implementationHash": digest, "rates": [f"Rate {i}" for i in range(23)]}
    frames = list(personal_worker.stream_frames(
        {"input": payload, "implementationHash": digest},
        digest,
        lambda: next(checks),
    ))
    assert len(frames) == 2
    assert len(frames[0]["rows"]) == 21
    assert frames[1] == {"error": "implementation_changed"}




def test_stderr_flood_is_drained_with_bounded_retention():
    from radiworks.core.personal_stream import MAX_RETAINED_STDERR_BYTES

    code = (
        "import sys; sys.stdin.buffer.read(); "
        "sys.stderr.buffer.write(b'x' * 1048576); sys.stderr.buffer.flush(); "
        "sys.stdout.buffer.write(b'{\"done\":1}\\n'); sys.stdout.buffer.flush()"
    )
    owned = stream(code)
    try:
        assert owned.next_frame(deadline()) == {"done": 1}
        assert owned.finish(deadline()) == 0
    finally:
        owned.cleanup()
    assert len(owned._stderr) == MAX_RETAINED_STDERR_BYTES
    assert owned.threads_stopped

