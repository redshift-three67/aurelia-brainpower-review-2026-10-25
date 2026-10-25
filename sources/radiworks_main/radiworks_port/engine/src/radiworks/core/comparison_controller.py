"""Single owned CPU child; durable transitions precede process cancellation."""
import hashlib
import json
import logging
import os
from pathlib import Path
import queue
import subprocess
import sys
import threading
from .owned_cpu import reap_owned_process


class ComparisonControllerError(ValueError):
    def __init__(self, code):
        self.code = code
        super().__init__(code)


def implementation_hash():
    root = Path(__file__).parent
    names = ('comparison_basis.py','comparison_store.py','comparison_worker.py','comparison_controller.py',
        'owned_cpu.py','experimental_matrix.py','experimental_context.py','personal_context.py')
    digest = hashlib.sha256()
    for name in names:
        digest.update(name.encode('ascii')); digest.update((root / name).read_bytes())
    return digest.hexdigest()


class ComparisonController:
    def __init__(self, root, scope, *, deps_dir=None, worker_timeout=120):
        self.root = Path(root); self.scope = scope
        self.deps_dir = Path(deps_dir).resolve() if deps_dir else None
        self.worker_timeout = worker_timeout
        self.store = None; self._unavailable_reason = None
        self._stop = threading.Event(); self._queue = queue.Queue()
        self._lock = threading.RLock(); self._process = None; self._active_id = None; self._cpu_budget = threading.Lock()
        self._thread = threading.Thread(target=self._run, name='experimental-comparison', daemon=True)

    def capability(self):
        configured = bool(not self._unavailable_reason and self.deps_dir and not self.deps_dir.is_symlink() and not self.deps_dir.is_junction()
            and (self.deps_dir / 'torch' / '__init__.py').is_file() and (self.deps_dir / 'numpy' / '__init__.py').is_file())
        return {'configured': configured, 'formulaVersion': 'radi144-matrix-cpu-v1', 'candidateCount': 80000,
            'maxRates': 21, 'backend': 'cpu', 'defaultMode': 'original', 'automaticReplay': False, 'unavailableReason': self._unavailable_reason or (None if configured else 'cpu_unavailable')}

    def start(self):
        from .comparison_store import ComparisonStore, ComparisonStoreError
        try:
            self.store = ComparisonStore(self.root / 'comparisons.sqlite3', self.scope)
            self.store.interrupt_pending()
        except ComparisonStoreError as exc:
            self.store = None; self._unavailable_reason = exc.code
            return
        self._thread.start()

    def _ready(self):
        if self.store is None or self._stop.is_set() or not self._thread.is_alive(): raise ComparisonControllerError('shutdown')
        if not self.capability()['configured']: raise ComparisonControllerError('cpu_unavailable')

    def request(self, payload, request_id):
        with self._lock:
            self._ready()
            if payload.get('implementationHash') != implementation_hash(): raise ComparisonControllerError('implementation_changed')
            record = self.store.create(request_id, payload)
            if record['status'] == 'queued': self._queue.put(record['id'])
            return record

    def retry(self, job_id, request_id):
        with self._lock:
            self._ready()
            if self.store.get(job_id)['input']['implementationHash'] != implementation_hash(): raise ComparisonControllerError('implementation_changed')
            record = self.store.retry(job_id, request_id)
            if record['status'] == 'queued': self._queue.put(record['id'])
            return record

    def cancel(self, job_id):
        with self._lock:
            record = self.store.cancel(job_id)
            if self._active_id == job_id and self._process is not None and self._process.poll() is None:
                self._process.terminate()
            return record

    def shutdown(self, timeout=None):
        failure = None
        with self._lock:
            self._stop.set()
            try:
                if self.store is not None: self.store.interrupt_pending()
            except Exception as exc:
                failure = exc
            finally:
                try:
                    if self._process is not None and self._process.poll() is None:self._process.terminate()
                except Exception as exc:
                    if failure is None:failure=exc
                finally:self._queue.put(None)
        if self._thread.is_alive(): self._thread.join(timeout=timeout)
        if self._thread.is_alive(): raise ComparisonControllerError('shutdown')
        if failure is not None: raise ComparisonControllerError('shutdown') from failure

    def _spawn(self):
        environment = os.environ.copy()
        # Only this candidate and the explicit CPU bundle may supply subprocess imports.
        environment['PYTHONPATH'] = os.pathsep.join((str(Path(__file__).parents[2]), str(self.deps_dir)))
        environment['OMP_NUM_THREADS'] = '1'; environment['MKL_NUM_THREADS'] = '1'
        environment['PYTHONNOUSERSITE'] = '1'
        return subprocess.Popen([sys.executable, '-m', 'radiworks.core.comparison_worker'],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8',
            env=environment, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))

    def _fail(self, identifier, code):
        from .comparison_store import ComparisonStoreError
        try:
            if self.store.get(identifier)['status'] == 'running': self.store.fail(identifier, code)
        except ComparisonStoreError:
            if self.store.get(identifier)['status'] == 'running': raise

    def _run(self):
        try:
            self._dispatch()
        except Exception as exc:
            # A failed dispatcher must not admit work into an unattended queue.
            self._unavailable_reason = getattr(exc, 'code', 'worker_failed')
            self._stop.set()
            logging.getLogger(__name__).error('Experimental comparison dispatcher unavailable: %s', self._unavailable_reason)

    def _dispatch(self):
        from .comparison_store import ComparisonStoreError
        while not self._stop.is_set():
            identifier = self._queue.get()
            if identifier is None: break
            with self._cpu_budget:
                process = None
                try:
                    with self._lock:
                        if self._stop.is_set(): break
                        if self.store.get(identifier)['status'] != 'queued': continue
                        record = self.store.claim(identifier)
                        if record['input']['implementationHash'] != implementation_hash():
                            self._fail(identifier, 'implementation_changed'); continue
                        try: process = self._spawn()
                        except OSError:
                            self._fail(identifier, 'worker_start_failed'); continue
                        self._process = process; self._active_id = identifier
                    envelope = {'input': record['input'], 'implementationHash': record['input']['implementationHash']}
                    try:
                        output, _ = process.communicate(json.dumps(envelope, ensure_ascii=False, allow_nan=False), timeout=self.worker_timeout)
                    except subprocess.TimeoutExpired:
                        process.kill(); process.communicate()
                        self._fail(identifier, 'worker_timeout'); continue
                    if self.store.get(identifier)['status'] != 'running': continue
                    if process.returncode != 0:
                        self._fail(identifier, 'worker_failed'); continue
                    if len(output.encode('utf-8')) > 256 * 1024:
                        self._fail(identifier, 'worker_protocol'); continue
                    try:
                        reply = json.loads(output)
                        if type(reply) is not dict: raise ValueError()
                        if set(reply) == {'error'} and reply['error'] in {'cpu_unavailable','implementation_changed','worker_failed','worker_protocol'}:
                            self._fail(identifier, reply['error'])
                        elif set(reply) == {'result'}:
                            self.store.finish(identifier, reply['result'])
                        else: raise ValueError()
                    except (ValueError, TypeError, ComparisonStoreError):
                        self._fail(identifier, 'worker_protocol')
                except (ComparisonStoreError, OSError, ValueError):
                    self._fail(identifier, 'worker_failed')
                finally:
                    try:reap_owned_process(process)
                    finally:
                        with self._lock:
                            if self._active_id == identifier:self._active_id = None;self._process = None
