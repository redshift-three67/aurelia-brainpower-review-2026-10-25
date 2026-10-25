"""Explicit Python unittest adapter for sealed staging artifacts; no apply-back."""
import json
import hashlib
import os
from pathlib import Path
import sys
import tempfile
import threading

from .jobs import JobCancelled, run_process
from .execution_workspace import _components, _read
from .evidence import fingerprint


def adapter_identity():
    """Disk implementation evidence, not attestation of the host or loaded code."""
    names=('staged_tests.py','restricted_test_runner.py','jobs.py','process_tree.py',
           'process_gate.py','execution_workspace.py')
    value=dict(id='python_stdlib_unittest_audit', schema_version=1,
               python_version=sys.version, implementation=sys.implementation.name,
               platform=sys.platform, timeout_seconds=60,
               files={name:hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
                      for name in names})
    return dict(value,hash=fingerprint(value))


def require_current_adapter(result):
    """Historical completion is insufficient after an adapter update."""
    current=adapter_identity()
    if (result.get('adapter_verified') is not True
            or any(not isinstance(result.get(key),dict)
                   or fingerprint(result[key]) != fingerprint(current)
                   for key in ('adapter_before','adapter_after'))):
        raise ValueError('Adapter-Nachweis fehlt oder ist veraltet. Staging-Test erneut ausführen.')


def run_staged_tests(stager, stage_id, manifest_hash, cancel, on_line):
    cancel = cancel if cancel is not None else threading.Event()
    on_line = on_line or (lambda line: None)
    if cancel.is_set():
        raise JobCancelled('Staging-Test vor Ausführung abgebrochen.')
    stager.verify_source(stage_id, manifest_hash)
    adapter_before = adapter_identity()
    staged = stager.base/stage_id/'files'
    if not (staged/'tests').is_dir():
        raise ValueError('Der Python-Testadapter benötigt einen explizit gestagten tests-Ordner.')
    scratch_parent = stager.base.parent/'execution-test-scratch'
    _components(scratch_parent)
    scratch_parent.mkdir(parents=True, exist_ok=True)
    _components(scratch_parent)
    completion_data = None
    with tempfile.TemporaryDirectory(prefix='run-', dir=scratch_parent) as control:
        scratch = str(Path(control)/'scratch')
        Path(scratch).mkdir()
        completion_path = Path(control)/'completion.json'
        env = {key: os.environ[key] for key in ('SystemRoot', 'SYSTEMROOT', 'WINDIR', 'SystemDrive') if key in os.environ}
        env.update(TEMP=scratch, TMP=scratch, TMPDIR=scratch, USERPROFILE=scratch, HOME=scratch,
                   APPDATA=scratch, LOCALAPPDATA=scratch)
        argv = [sys.executable, '-I', '-S', '-B', str(Path(__file__).with_name('restricted_test_runner.py')), str(staged), scratch, str(completion_path)]
        try:
            exit_code, output = run_process(argv, str(staged), env, cancel, on_line, timeout=60)
        finally:
            # A failed or cancelled process does not bypass post-run source checks.
            stager.verify_source(stage_id, manifest_hash)
        try:
            completion_data = _read(Path(control), 'completion.json', 4096)
        except ValueError:
            pass
    if cancel.is_set():
        raise JobCancelled('Staging-Test abgebrochen.')
    adapter_after = adapter_identity()
    adapter_verified = adapter_before == adapter_after
    valid = False
    summary = dict(count=0, errors=1, failures=0, skipped=0, success=False)
    if completion_data:
        try:
            parsed = json.loads(completion_data)
            fields = {'count', 'errors', 'failures', 'skipped', 'success'}
            if (isinstance(parsed, dict) and set(parsed) == fields and type(parsed['success']) is bool
                    and all(type(parsed[key]) is int and 0 <= parsed[key] <= 1000000 for key in fields-{'success'})
                    and parsed['skipped'] <= parsed['count']):
                summary = parsed
                valid = True
        except (ValueError, TypeError):
            pass
    success = bool(adapter_verified and valid and exit_code == 0 and summary['success'] and summary['count'] > summary['skipped'] >= 0
                   and summary['errors'] == 0 and summary['failures'] == 0)
    return dict(summary, success=success, exit_code=exit_code, sources_verified=True, output=output,
                adapter_before=adapter_before, adapter_after=adapter_after, adapter_verified=adapter_verified,
                stage_id=stage_id, manifest_hash=manifest_hash, adapter='python_stdlib_unittest_audit', completion_verified=valid,
                execution_permission_granted=False, apply_back_enabled=False,
                limitations=['Python audit guard, not an OS sandbox for hostile Python or native code.',
                             'Completion is a runner-owned record outside test scratch; stdout is never completion proof.',
                             'Same-process Python introspection or native-code attacks are not isolated by this adapter.',
                             'Only explicitly staged Python stdlib unittest tests are supported.'])
