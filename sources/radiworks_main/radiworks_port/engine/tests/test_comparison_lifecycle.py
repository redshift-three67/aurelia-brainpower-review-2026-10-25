import threading,time
from pathlib import Path
from fastapi.testclient import TestClient
import pytest
from radiworks.main import create_app
from radiworks.api.routes import STATE
from radiworks.runtime_lease import runtime_home_lease
from radiworks.core.comparison_controller import ComparisonController


def test_lease_not_released_while_owned_comparison_thread_delays(tmp_path,monkeypatch):
    stopping=threading.Event();release=threading.Event();exit_done=threading.Event()
    def slow_run(self):
        self._stop.wait();stopping.set();release.wait(timeout=10)
    monkeypatch.setattr(ComparisonController,'_run',slow_run)
    app=create_app(base_dir=tmp_path);client=TestClient(app);client.__enter__();state=STATE.state
    errors=[]
    def close():
        try:client.__exit__(None,None,None)
        except BaseException as exc:errors.append(exc)
        finally:exit_done.set()
    thread=threading.Thread(target=close);thread.start()
    try:
        assert stopping.wait(timeout=5)
        assert not exit_done.is_set()
        with pytest.raises(RuntimeError):
            with runtime_home_lease(tmp_path):pass
    finally:release.set();thread.join(timeout=10)
    assert not errors and exit_done.is_set()
    assert not state.comparisons._thread.is_alive() and not state.broadcast._running
    with runtime_home_lease(tmp_path):pass


def test_optional_corrupt_comparison_store_keeps_original_available(tmp_path):
    folder=tmp_path/'comparisons';folder.mkdir();(folder/'comparisons.sqlite3').write_bytes(b'SYNTHETIC corrupt')
    with TestClient(create_app(base_dir=tmp_path)) as client:
        assert client.get('/ping').status_code==200
        reply=client.get('/comparisons/capability')
        assert reply.status_code==200 and reply.json()['configured'] is False
        assert reply.json()['unavailableReason']=='corrupt_store'
        assert client.get('/settings').status_code==200
