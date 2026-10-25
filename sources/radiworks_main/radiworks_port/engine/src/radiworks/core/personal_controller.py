"""One owned personal CPU child per job; cancelled generations cannot publish."""
from __future__ import annotations

import hashlib
import logging
import os
from pathlib import Path
import queue
import subprocess
import sys
import threading
import time

from .personal_jobs import PersonalJobStore, PersonalJobError, ACTIVE
from .personal_analysis import MAX_PERSONAL_RATES, PROCEDURE
from .personal_stream import PersonalStreamError, PersonalWorkerStream, encode_input


def personal_implementation_hash():
    root = Path(__file__).parent
    digest = hashlib.sha256()
    for name in (
        "owned_cpu.py",
        "personal_analysis.py",
        "personal_jobs.py",
        "personal_controller.py",
        "personal_worker.py",
        "personal_stream.py",
        "experimental_matrix.py",
        "experimental_context.py",
        "personal_context.py",
    ):
        digest.update(name.encode("ascii"))
        digest.update((root / name).read_bytes())
    return digest.hexdigest()


class PersonalController:
    def __init__(self, root, scope, *, deps_dir=None, worker_timeout=120):
        self.root = Path(root)
        self.scope = scope
        self.deps_dir = Path(deps_dir).resolve() if deps_dir else None
        self.worker_timeout = worker_timeout
        self.store = None
        self._unavailable_reason = None
        self._stop = threading.Event()
        self._queue = queue.Queue()
        self._lock = threading.RLock()
        self._process = None
        self._stream = None
        self._active_id = None
        self._active_cancel_event = None
        self._payloads = {}
        self._cpu_budget = threading.Lock()
        self._thread = threading.Thread(target=self._run, name="personal-analysis", daemon=True)

    def capability(self):
        configured = bool(
            not self._unavailable_reason
            and self.deps_dir
            and not self.deps_dir.is_symlink()
            and not self.deps_dir.is_junction()
            and (self.deps_dir / "torch/__init__.py").is_file()
            and (self.deps_dir / "numpy/__init__.py").is_file()
        )
        return {
            "configured": configured,
            "procedure": PROCEDURE,
            "candidateCount": 80000,
            "maxRates": MAX_PERSONAL_RATES,
            "blockSize": 21,
            "backend": "cpu",
            "automaticReplay": False,
            "unavailableReason": self._unavailable_reason or (None if configured else "cpu_unavailable"),
        }

    def start(self):
        try:
            self.store = PersonalJobStore(self.root / "personal.sqlite3", self.scope)
            self.store.interrupt_pending()
        except PersonalJobError as exc:
            self.store = None
            self._unavailable_reason = exc.code
            return
        self._thread.start()

    def request(self, data, request_id):
        with self._lock:
            if self.store is None or self._stop.is_set() or not self._thread.is_alive():
                raise PersonalJobError("shutdown")
            if not self.capability()["configured"]:
                raise PersonalJobError("cpu_unavailable")
            if data.get("implementationHash") != personal_implementation_hash():
                raise PersonalJobError("implementation_changed")
            try:
                input_bytes = encode_input({"input": data, "implementationHash": data.get("implementationHash")})
            except PersonalStreamError as exc:
                raise PersonalJobError(exc.code) from exc
            record = self.store.create(request_id, data)
            if record["status"] == "queued":
                self._payloads[record["id"]] = input_bytes
                self._queue.put(record["id"])
            return record

    def cancel(self, identifier):
        with self._lock:
            record = self.store.cancel(identifier)
            if self._active_id == identifier:
                if self._active_cancel_event is not None:
                    self._active_cancel_event.set()
                if self._process is not None and self._process.poll() is None:
                    try:
                        self._process.terminate()
                    except OSError:
                        pass
            else:
                # The dispatcher cannot claim this queued payload while this lock is held.
                self._payloads.pop(identifier, None)
            return record

    def shutdown(self, timeout=None):
        failure = None
        with self._lock:
            self._stop.set()
            try:
                if self.store is not None:
                    self.store.interrupt_pending()
            except Exception as exc:
                failure = exc
            finally:
                # Claimed inputs were removed from this map while holding the same lock.
                self._payloads.clear()
                try:
                    if self._active_cancel_event is not None:
                        self._active_cancel_event.set()
                    if self._process is not None and self._process.poll() is None:
                        self._process.terminate()
                except Exception as exc:
                    if failure is None:
                        failure = exc
                finally:
                    self._queue.put(None)
        if self._thread.is_alive():
            self._thread.join(timeout)
        if self._thread.is_alive():
            raise PersonalJobError("shutdown")
        if self._stream is not None and not self._stream.cleanup_confirmed:
            raise PersonalJobError("shutdown")
        if self._process is not None:
            raise PersonalJobError("shutdown")
        if failure:
            raise PersonalJobError("shutdown") from failure

    def _spawn(self):
        # CPU children receive frozen input only; service/model keys are not inherited.
        names = {
            "systemroot",
            "windir",
            "path",
            "temp",
            "tmp",
            "localappdata",
            "appdata",
            "userprofile",
            "number_of_processors",
            "processor_architecture",
        }
        environment = {key: value for key, value in os.environ.items() if key.lower() in names}
        environment.update(
            PYTHONPATH=os.pathsep.join((str(Path(__file__).parents[2]), str(self.deps_dir))),
            OMP_NUM_THREADS="1",
            MKL_NUM_THREADS="1",
            PYTHONNOUSERSITE="1",
            PYTHONIOENCODING="utf-8",
        )
        return subprocess.Popen(
            [sys.executable, "-m", "radiworks.core.personal_worker", "--job-stream"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=0,
            env=environment,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )

    def _fail(self, identifier, code):
        if self.store.get(identifier)["status"] in ACTIVE:
            self.store.fail(identifier, code)

    def _run(self):
        try:
            self._dispatch()
        except Exception as exc:
            self._unavailable_reason = getattr(exc, "code", "worker_failed")
            self._stop.set()
            logging.getLogger(__name__).error(
                "Personal analysis unavailable: %s", self._unavailable_reason
            )

    def _record_is_current(self, identifier, generation):
        current = self.store.get(identifier)
        return current if current["status"] == "running" and current["generation"] == generation else None

    def _note_store_unavailable(self):
        self._unavailable_reason = "store_unavailable"
        self._stop.set()
        logging.getLogger(__name__).error("Personal analysis state unavailable: store_unavailable")

    def _discard_unclaimed_payloads(self):
        # Store lookup/claim failed before any child owned this queued input.
        self._note_store_unavailable()
        with self._lock:
            self._payloads.clear()

    def _fail_stream(self, identifier, generation, code):
        try:
            current = self._record_is_current(identifier, generation)
            if current is not None:
                self._fail(identifier, code)
        except Exception:
            self._note_store_unavailable()

    def _append_block(self, identifier, generation, rows):
        try:
            self.store.append_block(identifier, generation, rows)
            return True
        except PersonalJobError as exc:
            if exc.code != "stale_job":
                self._fail_stream(
                    identifier,
                    generation,
                    "worker_protocol" if exc.code == "worker_protocol" else "worker_failed",
                )
            return False
        except Exception:
            self._fail_stream(identifier, generation, "worker_failed")
            if self._unavailable_reason != "store_unavailable":
                self._note_store_unavailable()
            return False

    def _check_frame_rows(self, rows, start, total):
        end = min(start + 21, total)
        if type(rows) is not list or len(rows) != end - start:
            return False
        if any(type(row) is not dict or type(row.get("inputIndex")) is not int for row in rows):
            return False
        return [row["inputIndex"] for row in rows] == list(range(start, end))

    def _dispatch(self):
        while not self._stop.is_set():
            identifier = self._queue.get()
            if identifier is None:
                break
            self._cpu_budget.acquire()
            release_budget = True
            record = None
            process = None
            stream = None
            cancel_event = None
            try:
                with self._lock:
                    if self._stop.is_set():
                        self._payloads.pop(identifier, None)
                        continue
                    queued = self.store.get(identifier)
                    if queued["status"] != "queued":
                        self._payloads.pop(identifier, None)
                        continue
                    record = self.store.claim(identifier)
                    input_bytes = self._payloads.pop(identifier, None)
                    cancel_event = threading.Event()
                    self._active_id = identifier
                    self._active_cancel_event = cancel_event
                generation = record["generation"]
                expected_hash = record["input"]["implementationHash"]
                if input_bytes is None:
                    self._fail_stream(identifier, generation, "worker_protocol")
                    continue
                if self._record_is_current(identifier, generation) is None:
                    continue
                if expected_hash != personal_implementation_hash():
                    self._fail_stream(identifier, generation, "implementation_changed")
                    continue
                total = len(record["input"]["rates"])
                if type(total) is not int or total < 1:
                    self._fail_stream(identifier, generation, "worker_protocol")
                    continue
                # The first block deadline includes process startup and input delivery.
                deadline = time.monotonic() + self.worker_timeout
                try:
                    process = self._spawn()
                except OSError:
                    self._fail_stream(identifier, generation, "worker_start_failed")
                    continue
                with self._lock:
                    self._process = process
                stream = PersonalWorkerStream(process, input_bytes)
                with self._lock:
                    self._stream = stream
                stream.start()
                expected_start = len(record["rows"])
                if expected_start != 0:
                    self._fail_stream(identifier, generation, "worker_protocol")
                    continue
                final_rows = None
                final_start = None
                while not self._stop.is_set():
                    current = self._record_is_current(identifier, generation)
                    if current is None:
                        break
                    if current["input"]["implementationHash"] != personal_implementation_hash():
                        self._fail_stream(identifier, generation, "implementation_changed")
                        break
                    frame = stream.next_frame(deadline, cancel_event)
                    if frame is None:
                        self._fail_stream(identifier, generation, "worker_protocol")
                        break
                    next_deadline = time.monotonic() + self.worker_timeout
                    current = self._record_is_current(identifier, generation)
                    if current is None:
                        break
                    if current["input"]["implementationHash"] != personal_implementation_hash():
                        self._fail_stream(identifier, generation, "implementation_changed")
                        break
                    if set(frame) == {"error"}:
                        code = frame["error"]
                        allowed = {
                            "cpu_unavailable",
                            "implementation_changed",
                            "worker_failed",
                            "worker_protocol",
                        }
                        if type(code) is not str or code not in allowed:
                            code = "worker_protocol"
                        self._fail_stream(identifier, generation, code)
                        break
                    if set(frame) == {"rows"}:
                        if final_rows is not None:
                            self._fail_stream(identifier, generation, "worker_protocol")
                            break
                        rows = frame["rows"]
                        if not self._check_frame_rows(rows, expected_start, total):
                            self._fail_stream(identifier, generation, "worker_protocol")
                            break
                        end = expected_start + len(rows)
                        if end == total:
                            final_rows = rows
                            final_start = expected_start
                        else:
                            # Prefix progress is durable after a fresh hash/generation check.
                            current = self._record_is_current(identifier, generation)
                            if current is None:
                                break
                            if current["input"]["implementationHash"] != personal_implementation_hash():
                                self._fail_stream(identifier, generation, "implementation_changed")
                                break
                            if not self._append_block(identifier, generation, rows):
                                break
                            expected_start = end
                        deadline = next_deadline
                        continue
                    if set(frame) == {"done"}:
                        count = frame["done"]
                        if (
                            type(count) is not int
                            or count != total
                            or final_rows is None
                            or final_start != expected_start
                            or expected_start + len(final_rows) != total
                        ):
                            self._fail_stream(identifier, generation, "worker_protocol")
                            break
                        stream.finish(deadline, cancel_event)
                        stream.cleanup()
                        current = self._record_is_current(identifier, generation)
                        if current is None:
                            break
                        if current["input"]["implementationHash"] != personal_implementation_hash():
                            self._fail_stream(identifier, generation, "implementation_changed")
                            break
                        self._append_block(identifier, generation, final_rows)
                        break
                    self._fail_stream(identifier, generation, "worker_protocol")
                    break
            except PersonalStreamError as exc:
                if exc.code != "cancelled":
                    code = exc.code if exc.code in {
                        "cpu_unavailable",
                        "implementation_changed",
                        "worker_start_failed",
                        "worker_timeout",
                        "worker_failed",
                        "worker_protocol",
                    } else "worker_failed"
                    if record is not None:
                        self._fail_stream(identifier, record["generation"], code)
            except PersonalJobError as exc:
                code = exc.code if exc.code == "worker_protocol" else "worker_failed"
                if record is not None:
                    self._fail_stream(identifier, record["generation"], code)
                else:
                    self._discard_unclaimed_payloads()
            except Exception:
                if record is not None:
                    self._fail_stream(identifier, record["generation"], "worker_failed")
                else:
                    self._discard_unclaimed_payloads()
            finally:
                cleanup_confirmed = process is None
                if stream is not None:
                    try:
                        stream.cleanup()
                        cleanup_confirmed = stream.cleanup_confirmed
                    except PersonalStreamError:
                        cleanup_confirmed = False
                elif process is not None:
                    try:
                        if process.poll() is None:
                            process.kill()
                        process.wait(timeout=3)
                        for pipe in (process.stdin, process.stdout, process.stderr):
                            if pipe is not None:
                                pipe.close()
                        cleanup_confirmed = process.poll() is not None
                    except Exception:
                        cleanup_confirmed = False
                if cleanup_confirmed:
                    with self._lock:
                        if self._active_id == identifier:
                            self._active_id = None
                            self._process = None
                            self._stream = None
                            self._active_cancel_event = None
                else:
                    release_budget = False
                    self._unavailable_reason = "worker_cleanup"
                    self._stop.set()
                    if record is not None:
                        self._fail_stream(identifier, record["generation"], "worker_failed")
                if release_budget:
                    self._cpu_budget.release()



