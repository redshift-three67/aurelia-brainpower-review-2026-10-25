"""Bounded binary transport for one owned personal CPU job stream."""
from __future__ import annotations

import json
import queue
import subprocess
import threading
import time


MAX_INPUT_BYTES = 12 * 1024 * 1024
MAX_OUTPUT_FRAME_BYTES = 256 * 1024
MAX_BUFFERED_FRAMES = 2
MAX_RETAINED_STDERR_BYTES = 64 * 1024
_POLL_SECONDS = 0.05


class PersonalStreamError(RuntimeError):
    def __init__(self, code):
        super().__init__(code)
        self.code = code


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def _reject_constant(value):
    raise ValueError("non-finite JSON number")


def parse_json_frame(raw):
    if type(raw) is not bytes or not raw or len(raw) > MAX_OUTPUT_FRAME_BYTES or not raw.endswith(b"\n"):
        raise PersonalStreamError("worker_protocol")
    try:
        value = json.loads(
            raw[:-1].decode("utf-8", "strict"),
            object_pairs_hook=_unique_object,
            parse_constant=_reject_constant,
        )
    except (UnicodeDecodeError, ValueError, TypeError, json.JSONDecodeError) as exc:
        raise PersonalStreamError("worker_protocol") from exc
    if type(value) is not dict:
        raise PersonalStreamError("worker_protocol")
    return value


def encode_input(envelope):
    try:
        raw = json.dumps(envelope, ensure_ascii=False, allow_nan=False, separators=(",", ":")).encode("utf-8") + b"\n"
    except (TypeError, ValueError, UnicodeEncodeError) as exc:
        raise PersonalStreamError("worker_protocol") from exc
    if len(raw) > MAX_INPUT_BYTES:
        raise PersonalStreamError("input_too_large")
    return raw


def decode_input(raw):
    if type(raw) is not bytes or not raw or len(raw) > MAX_INPUT_BYTES or not raw.endswith(b"\n") or raw.count(b"\n") != 1:
        raise PersonalStreamError("worker_protocol")
    try:
        value = json.loads(
            raw[:-1].decode("utf-8", "strict"),
            object_pairs_hook=_unique_object,
            parse_constant=_reject_constant,
        )
    except (UnicodeDecodeError, ValueError, TypeError, json.JSONDecodeError) as exc:
        raise PersonalStreamError("worker_protocol") from exc
    if type(value) is not dict:
        raise PersonalStreamError("worker_protocol")
    return value


def encode_frame(frame):
    try:
        raw = json.dumps(frame, ensure_ascii=False, allow_nan=False, separators=(",", ":")).encode("utf-8") + b"\n"
    except (TypeError, ValueError, UnicodeEncodeError) as exc:
        raise PersonalStreamError("worker_protocol") from exc
    if len(raw) > MAX_OUTPUT_FRAME_BYTES:
        raise PersonalStreamError("worker_protocol")
    return raw


class PersonalWorkerStream:
    """Owns binary stdin/stdout/stderr pipes and their single reader threads."""

    def __init__(self, process, input_bytes):
        if type(input_bytes) is not bytes or not input_bytes or len(input_bytes) > MAX_INPUT_BYTES or not input_bytes.endswith(b"\n"):
            raise PersonalStreamError("worker_protocol")
        if process.stdin is None or process.stdout is None or process.stderr is None:
            raise PersonalStreamError("worker_start_failed")
        self.process = process
        self.input_bytes = input_bytes
        self._events = queue.Queue(maxsize=MAX_BUFFERED_FRAMES)
        self._stop = threading.Event()
        self._writer_done = threading.Event()
        self._writer_error = None
        self._stderr_lock = threading.Lock()
        self._stderr = bytearray()
        self._threads = []
        self._started = False
        self._finished = False
        self._cleanup_confirmed = False

    @property
    def threads_stopped(self):
        return all(not thread.is_alive() for thread in self._threads)

    @property
    def cleanup_confirmed(self):
        return self._cleanup_confirmed

    def start(self):
        if self._started:
            raise PersonalStreamError("worker_protocol")
        self._started = True
        self._threads = [
            threading.Thread(target=self._read_stdout, name="personal-stream-stdout", daemon=True),
            threading.Thread(target=self._drain_stderr, name="personal-stream-stderr", daemon=True),
            threading.Thread(target=self._write_stdin, name="personal-stream-stdin", daemon=True),
        ]
        try:
            for thread in self._threads:
                thread.start()
        except Exception as exc:
            self._stop.set()
            raise PersonalStreamError("worker_start_failed") from exc
        return self

    def _post(self, kind, value=None):
        event = (kind, value)
        while not self._stop.is_set():
            try:
                self._events.put(event, timeout=_POLL_SECONDS)
                return True
            except queue.Full:
                continue
        return False

    def _read_stdout(self):
        try:
            while not self._stop.is_set():
                raw = self.process.stdout.readline(MAX_OUTPUT_FRAME_BYTES + 1)
                if not raw:
                    self._post("eof")
                    return
                if len(raw) > MAX_OUTPUT_FRAME_BYTES:
                    raise PersonalStreamError("worker_protocol")
                self._post("frame", parse_json_frame(raw))
        except PersonalStreamError as exc:
            self._post("error", exc.code)
        except (OSError, ValueError):
            self._post("error", "worker_failed")
        except Exception:
            self._post("error", "worker_failed")

    def _drain_stderr(self):
        try:
            while True:
                chunk = self.process.stderr.read(4096)
                if not chunk:
                    return
                with self._stderr_lock:
                    available = MAX_RETAINED_STDERR_BYTES - len(self._stderr)
                    if available > 0:
                        self._stderr.extend(chunk[:available])
        except Exception:
            return

    def _write_stdin(self):
        try:
            view = memoryview(self.input_bytes)
            while view:
                written = self.process.stdin.write(view)
                if not written:
                    raise BrokenPipeError("worker input closed")
                view = view[written:]
            self.process.stdin.close()
        except Exception as exc:
            self._writer_error = exc
        finally:
            self._writer_done.set()

    def _check_writer(self, until):
        while not self._writer_done.is_set():
            remaining = until - time.monotonic()
            if remaining <= 0:
                raise PersonalStreamError("worker_timeout")
            self._writer_done.wait(min(_POLL_SECONDS, remaining))
        if self._writer_error is not None:
            raise PersonalStreamError("worker_failed") from self._writer_error

    def next_frame(self, until, cancelled=None):
        if not self._started:
            raise PersonalStreamError("worker_protocol")
        while True:
            if cancelled is not None and cancelled.is_set():
                raise PersonalStreamError("cancelled")
            if self._writer_done.is_set() and self._writer_error is not None:
                raise PersonalStreamError("worker_failed") from self._writer_error
            remaining = until - time.monotonic()
            if remaining <= 0:
                raise PersonalStreamError("worker_timeout")
            try:
                kind, value = self._events.get(timeout=min(_POLL_SECONDS, remaining))
            except queue.Empty:
                continue
            if kind == "error":
                raise PersonalStreamError(value)
            self._check_writer(until)
            if kind == "eof":
                return None
            if kind != "frame":
                raise PersonalStreamError("worker_protocol")
            return value

    def finish(self, until, cancelled=None):
        if self._finished:
            raise PersonalStreamError("worker_protocol")
        extra = self.next_frame(until, cancelled)
        if extra is not None:
            raise PersonalStreamError("worker_protocol")
        remaining = until - time.monotonic()
        if remaining <= 0:
            raise PersonalStreamError("worker_timeout")
        try:
            exit_code = self.process.wait(timeout=remaining)
        except subprocess.TimeoutExpired as exc:
            raise PersonalStreamError("worker_timeout") from exc
        except Exception as exc:
            raise PersonalStreamError("worker_failed") from exc
        if exit_code != 0:
            raise PersonalStreamError("worker_failed")
        self._join_threads(until)
        self._finished = True
        return exit_code

    def _join_threads(self, until):
        for thread in self._threads:
            remaining = until - time.monotonic()
            if remaining <= 0:
                raise PersonalStreamError("worker_timeout")
            thread.join(remaining)
            if thread.is_alive():
                raise PersonalStreamError("worker_timeout")

    def cleanup(self, timeout=3.0):
        if self._cleanup_confirmed:
            return
        until = time.monotonic() + max(0.1, timeout)
        self._stop.set()
        failure = None
        try:
            active = self.process.poll() is None
        except Exception as exc:
            active = True
            failure = exc
        if active:
            try:
                self.process.terminate()
            except Exception as exc:
                failure = failure or exc
            try:
                self.process.wait(timeout=min(0.25, max(0.01, until - time.monotonic())))
            except subprocess.TimeoutExpired:
                try:
                    self.process.kill()
                except Exception as exc:
                    failure = failure or exc
                try:
                    self.process.wait(timeout=max(0.01, until - time.monotonic()))
                except Exception as exc:
                    failure = failure or exc
            except Exception as exc:
                failure = failure or exc
        try:
            if self.process.poll() is None:
                raise PersonalStreamError("worker_cleanup")
        except PersonalStreamError:
            raise
        except Exception as exc:
            raise PersonalStreamError("worker_cleanup") from exc
        for pipe in (self.process.stdin, self.process.stdout, self.process.stderr):
            try:
                if pipe is not None and not pipe.closed:
                    pipe.close()
            except Exception as exc:
                failure = failure or exc
        for thread in self._threads:
            remaining = until - time.monotonic()
            if remaining > 0:
                thread.join(remaining)
        if not self.threads_stopped:
            raise PersonalStreamError("worker_cleanup")
        if failure is not None:
            raise PersonalStreamError("worker_cleanup") from failure
        self._cleanup_confirmed = True

