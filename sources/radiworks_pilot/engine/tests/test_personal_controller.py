"""Owned personal CPU process stream protocol; artificial jobs only."""
import hashlib
import os
import subprocess
import sys
import threading
import time
from pathlib import Path

import pytest

from test_personal_analysis import basis, freeze, SCOPE
from radiworks.core.personal_controller import PersonalController, personal_implementation_hash
from radiworks.core.personal_worker import execute


def data(tmp_path, count=24):
    value = freeze(*basis(tmp_path, count))
    value["implementationHash"] = personal_implementation_hash()
    from radiworks.persistence import document_digest
    value["inputDigest"] = document_digest({k: v for k, v in value.items() if k != "inputDigest"})
    return value


def wait_status(controller, identifier, statuses, timeout=10):
    end = time.monotonic() + timeout
    while time.monotonic() < end:
        result = controller.store.get(identifier)
        if result["status"] in statuses:
            return result
        time.sleep(0.01)
    pytest.fail("personal controller did not settle")


def wait_path(path):
    end = time.monotonic() + 5
    while time.monotonic() < end:
        if path.exists():
            return
        time.sleep(0.01)
    pytest.fail("stream child did not reach its synchronization point")



def wait_prefix(controller, identifier, count):
    end = time.monotonic() + 5
    while time.monotonic() < end:
        record = controller.store.get(identifier)
        if record["status"] == "running" and len(record["rows"]) >= count:
            return record
        time.sleep(0.01)
    pytest.fail("personal controller did not publish the validated prefix")
def stream_script(*, marker=None, release=None, duplicate=False, exit_code=0):
    lines = [
        "import json,pathlib,sys,time",
        "payload=json.loads(sys.stdin.buffer.read())['input']",
        "def send(frame):",
        " sys.stdout.buffer.write((json.dumps(frame,separators=(',',':'))+'\\n').encode('utf-8'))",
        " sys.stdout.buffer.flush()",
        "def rows(start,stop):",
        " return [{'inputIndex':i,'rate':payload['rates'][i],'score':i/100.0,'intensity':1.0,'matrix':[[i%10]*12 for _ in range(12)]} for i in range(start,stop)]",
    ]
    if duplicate:
        lines.extend(["send({'rows':rows(0,21)})", "send({'rows':rows(0,21)})"])
    else:
        lines.extend(
            [
                "for start in range(0,len(payload['rates']),21):",
                " send({'rows':rows(start,min(start+21,len(payload['rates'])))} )",
            ]
        )
    if marker is not None:
        lines.extend(
            [
                "pathlib.Path(sys.argv[1]).write_text('ready',encoding='utf-8')",
                "while not pathlib.Path(sys.argv[2]).exists(): time.sleep(0.01)",
            ]
        )
    lines.extend([ "send({'done':len(payload['rates'])})", f"sys.exit({exit_code})" ])
    return "\n".join(lines), ([str(marker), str(release)] if marker is not None else [])


def attach_child(monkeypatch, controller, script, args):
    created = []

    def spawn():
        process = subprocess.Popen(
            [sys.executable, "-c", script, *args],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=0,
        )
        created.append(process)
        return process

    monkeypatch.setattr(controller, "_spawn", spawn)
    return created


def test_two_blocks_share_one_owned_process_and_complete_once(tmp_path, monkeypatch):
    payload = data(tmp_path)
    marker = tmp_path / "final-frame-sent"
    release = tmp_path / "allow-done"
    script, args = stream_script(marker=marker, release=release)
    controller = PersonalController(tmp_path / "runtime", SCOPE, deps_dir=tmp_path)
    monkeypatch.setattr(controller, "capability", lambda: {"configured": True})
    processes = attach_child(monkeypatch, controller, script, args)
    controller.start()
    try:
        job = controller.request(payload, "3" * 32)
        wait_path(marker)
        prefix = wait_prefix(controller, job["id"], 21)
        assert prefix["status"] == "running"
        assert len(prefix["rows"]) == 21
        assert [row["inputIndex"] for row in prefix["rows"]] == list(range(21))
        release.touch()
        completed = wait_status(controller, job["id"], {"completed", "failed"})
        assert completed["status"] == "completed"
        assert len(processes) == 1 and len(completed["rows"]) == 24
        assert completed["rows"][0]["inputIndex"] == 23
    finally:
        release.touch()
        controller.shutdown()


def test_cancel_after_prefix_preserves_only_incremental_rows(tmp_path, monkeypatch):
    payload = data(tmp_path)
    marker = tmp_path / "final-frame-sent"
    release = tmp_path / "allow-done"
    script, args = stream_script(marker=marker, release=release)
    controller = PersonalController(tmp_path / "runtime", SCOPE, deps_dir=tmp_path)
    monkeypatch.setattr(controller, "capability", lambda: {"configured": True})
    attach_child(monkeypatch, controller, script, args)
    controller.start()
    try:
        job = controller.request(payload, "4" * 32)
        wait_path(marker)
        assert len(wait_prefix(controller, job["id"], 21)["rows"]) == 21
        cancelled = controller.cancel(job["id"])
        assert cancelled["status"] == "cancelled"
        end = time.monotonic() + 5
        while controller._process is not None and time.monotonic() < end:
            time.sleep(0.01)
        assert controller._process is None
        record = controller.store.get(job["id"])
        assert record["status"] == "cancelled"
        assert len(record["rows"]) == 21
    finally:
        release.touch()
        controller.shutdown()


def test_final_rows_are_not_committed_when_child_exits_nonzero(tmp_path, monkeypatch):
    payload = data(tmp_path, 2)
    script, args = stream_script(exit_code=7)
    controller = PersonalController(tmp_path / "runtime", SCOPE, deps_dir=tmp_path)
    monkeypatch.setattr(controller, "capability", lambda: {"configured": True})
    attach_child(monkeypatch, controller, script, args)
    controller.start()
    try:
        job = controller.request(payload, "5" * 32)
        failed = wait_status(controller, job["id"], {"completed", "failed"})
        assert failed["status"] == "failed"
        assert failed["error"] == "worker_failed"
        assert failed["rows"] == []
    finally:
        controller.shutdown()


def test_duplicate_rate_frame_fails_after_persisted_prefix(tmp_path, monkeypatch):
    payload = data(tmp_path, 24)
    script, args = stream_script(duplicate=True)
    controller = PersonalController(tmp_path / "runtime", SCOPE, deps_dir=tmp_path)
    monkeypatch.setattr(controller, "capability", lambda: {"configured": True})
    attach_child(monkeypatch, controller, script, args)
    controller.start()
    try:
        job = controller.request(payload, "6" * 32)
        failed = wait_status(controller, job["id"], {"completed", "failed"})
        assert failed["status"] == "failed"
        assert failed["error"] == "worker_protocol"
        assert len(failed["rows"]) == 21
    finally:
        controller.shutdown()


def test_implementation_drift_after_computation_blocks_final_commit(tmp_path, monkeypatch):
    from radiworks.core import personal_controller as controller_module

    payload = data(tmp_path, 22)
    marker = tmp_path / "final-frame-sent"
    release = tmp_path / "allow-done"
    script, args = stream_script(marker=marker, release=release)
    controller = PersonalController(tmp_path / "runtime", SCOPE, deps_dir=tmp_path)
    monkeypatch.setattr(controller, "capability", lambda: {"configured": True})
    attach_child(monkeypatch, controller, script, args)
    controller.start()
    try:
        job = controller.request(payload, "7" * 32)
        wait_path(marker)
        wait_prefix(controller, job["id"], 21)
        monkeypatch.setattr(controller_module, "personal_implementation_hash", lambda: "f" * 64)
        release.touch()
        failed = wait_status(controller, job["id"], {"completed", "failed"})
        assert failed["status"] == "failed"
        assert failed["error"] == "implementation_changed"
        assert len(failed["rows"]) == 21
    finally:
        release.touch()
        controller.shutdown()


def test_worker_rejects_wrong_implementation_and_protocol_before_cpu(tmp_path):
    payload = data(tmp_path, 2)
    digest = payload["implementationHash"]
    assert execute({"input": payload, "indices": [0, 1], "implementationHash": "0" * 64}, digest) == {
        "error": "implementation_changed"
    }
    assert execute(
        {"input": payload, "indices": [], "implementationHash": digest, "extra": "x"}, digest
    ) == {"error": "worker_protocol"}


def test_real_owned_cpu_worker_matches_exp1_and_no_keys_in_child(tmp_path, monkeypatch):
    bundle = os.environ.get("RADIOWORKS_EXP1_TEST_DEPS")
    if not bundle:
        pytest.skip("pinned CPU bundle required")
    from radiworks.core.experimental_matrix import rank_experimental_rates

    payload = data(tmp_path, 2)
    controller = PersonalController(tmp_path / "runtime", SCOPE, deps_dir=Path(bundle))
    controller.start()
    try:
        job = controller.request(payload, "8" * 32)
        end = time.monotonic() + 60
        while time.monotonic() < end:
            record = controller.store.get(job["id"])
            if record["status"] in {"completed", "failed"}:
                break
            time.sleep(0.05)
        assert record["status"] == "completed", record.get("error")
        exp = rank_experimental_rates(payload["contextSnapshot"], payload["catalog"], payload["rates"])
        assert {r["rate"]: r["score"] for r in record["rows"]} == {
            r["rate"]: r["score"] for r in exp["results"]
        }
    finally:
        controller.shutdown()


def test_oversized_serialized_catalog_is_rejected_before_admission(tmp_path, monkeypatch):
    import hashlib
    from radiworks.core.personal_jobs import PersonalJobError
    from radiworks.core.personal_analysis import freeze_personal_input
    from radiworks.entropy import EntropyProvider

    snap, _, _ = basis(tmp_path, 1)
    rates = ['"' * 2048] * 2047
    content = "\n".join(rates)
    catalog = {
        "name": "Large.txt",
        "sha256": hashlib.sha256(content.encode()).hexdigest(),
        "content": content,
    }
    payload = freeze_personal_input(
        SCOPE,
        snap,
        catalog,
        rates,
        mode="seeded",
        job_seed=0,
        entropy=EntropyProvider(seed=0),
        implementation_hash=personal_implementation_hash(),
    )
    ctrl = PersonalController(tmp_path / "runtime", SCOPE, deps_dir=tmp_path)
    monkeypatch.setattr(ctrl, "capability", lambda: {"configured": True})
    ctrl.start()
    try:
        with pytest.raises(PersonalJobError, match="input_too_large"):
            ctrl.request(payload, "9" * 32)
        assert ctrl.store.list() == []
    finally:
        ctrl.shutdown()





def test_repeated_final_rows_frame_is_rejected(tmp_path, monkeypatch):
    payload = data(tmp_path, 2)
    script = (
        "import json,sys\n"
        "payload=json.loads(sys.stdin.buffer.read())['input']\n"
        "def send(frame): sys.stdout.buffer.write((json.dumps(frame)+'\\n').encode()); sys.stdout.buffer.flush()\n"
        "def rows(): return [{'inputIndex':i,'rate':payload['rates'][i],'score':0.5,'intensity':1.0,'matrix':[[0]*12 for _ in range(12)]} for i in range(len(payload['rates']))]\n"
        "send({'rows':rows()})\n"
        "send({'rows':rows()})\n"
        "send({'done':len(payload['rates'])})"
    )
    controller = PersonalController(tmp_path / "runtime", SCOPE, deps_dir=tmp_path)
    monkeypatch.setattr(controller, "capability", lambda: {"configured": True})
    attach_child(monkeypatch, controller, script, [])
    controller.start()
    try:
        job = controller.request(payload, "a" * 32)
        failed = wait_status(controller, job["id"], {"completed", "failed"})
        assert failed["status"] == "failed"
        assert failed["error"] == "worker_protocol"
        assert failed["rows"] == []
    finally:
        controller.shutdown()


def test_unhashable_worker_error_value_is_protocol_failure(tmp_path, monkeypatch):
    payload = data(tmp_path, 2)
    script = (
        "import sys; sys.stdin.buffer.read(); "
        "sys.stdout.buffer.write(b'{\"error\":[]}\\n'); sys.stdout.buffer.flush()"
    )
    controller = PersonalController(tmp_path / "runtime", SCOPE, deps_dir=tmp_path)
    monkeypatch.setattr(controller, "capability", lambda: {"configured": True})
    attach_child(monkeypatch, controller, script, [])
    controller.start()
    try:
        job = controller.request(payload, "b" * 32)
        failed = wait_status(controller, job["id"], {"completed", "failed"})
        assert failed["status"] == "failed"
        assert failed["error"] == "worker_protocol"
        assert failed["rows"] == []
    finally:
        controller.shutdown()


def test_store_rejection_fails_job_instead_of_leaving_it_running(tmp_path, monkeypatch):
    from radiworks.core.personal_jobs import PersonalJobError

    payload = data(tmp_path, 24)
    script, args = stream_script()
    controller = PersonalController(tmp_path / "runtime", SCOPE, deps_dir=tmp_path)
    monkeypatch.setattr(controller, "capability", lambda: {"configured": True})
    attach_child(monkeypatch, controller, script, args)
    controller.start()
    monkeypatch.setattr(
        controller.store,
        "append_block",
        lambda *args: (_ for _ in ()).throw(PersonalJobError("ledger_write_failed")),
    )
    try:
        job = controller.request(payload, "c" * 32)
        failed = wait_status(controller, job["id"], {"completed", "failed"})
        assert failed["status"] == "failed"
        assert failed["error"] == "worker_failed"
        assert failed["rows"] == []
    finally:
        controller.shutdown()


def test_cancelled_queued_payload_is_removed_before_dispatch(tmp_path, monkeypatch):
    payload = data(tmp_path, 2)
    controller = PersonalController(tmp_path / "runtime", SCOPE, deps_dir=tmp_path)
    monkeypatch.setattr(controller, "capability", lambda: {"configured": True})
    spawned = attach_child(monkeypatch, controller, "", [])
    controller._cpu_budget.acquire()
    controller.start()
    try:
        job = controller.request(payload, "d" * 32)
        cancelled = controller.cancel(job["id"])
        assert cancelled["status"] == "cancelled"
        assert job["id"] not in controller._payloads
        controller._cpu_budget.release()
        wait_status(controller, job["id"], {"cancelled"})
        end = time.monotonic() + 5
        while not controller._queue.empty() and time.monotonic() < end:
            time.sleep(0.01)
        assert job["id"] not in controller._payloads
        assert spawned == []
    finally:
        if controller._cpu_budget.locked():
            controller._cpu_budget.release()
        controller.shutdown()


def test_unconfirmed_cleanup_holds_cpu_lease_and_shutdown_fails(tmp_path, monkeypatch):
    from radiworks.core.personal_stream import PersonalStreamError, PersonalWorkerStream
    from radiworks.core.personal_jobs import PersonalJobError

    payload = data(tmp_path, 2)
    script, args = stream_script()
    controller = PersonalController(tmp_path / "runtime", SCOPE, deps_dir=tmp_path)
    monkeypatch.setattr(controller, "capability", lambda: {"configured": True})
    processes = attach_child(monkeypatch, controller, script, args)
    original_cleanup = PersonalWorkerStream.cleanup

    def unconfirmed_cleanup(stream, timeout=3.0):
        original_cleanup(stream, timeout)
        stream._cleanup_confirmed = False
        raise PersonalStreamError("worker_cleanup")

    monkeypatch.setattr(PersonalWorkerStream, "cleanup", unconfirmed_cleanup)
    controller.start()
    try:
        job = controller.request(payload, "e" * 32)
        failed = wait_status(controller, job["id"], {"completed", "failed"})
        controller._thread.join(5)
        assert not controller._thread.is_alive()
        assert failed["status"] == "failed"
        assert processes and processes[0].poll() is not None
        assert controller._stream is not None
        assert not controller._stream.cleanup_confirmed
        assert controller._cpu_budget.acquire(blocking=False) is False
        with pytest.raises(PersonalJobError, match="shutdown"):
            controller.request(payload, "f" * 32)
        assert len(processes) == 1
        with pytest.raises(PersonalJobError, match="shutdown"):
            controller.shutdown()
    finally:
        # The child was really terminated and all reader threads joined before the test
        # deliberately revoked the cleanup confirmation.
        if controller._cpu_budget.acquire(blocking=False):
            controller._cpu_budget.release()






def test_sequential_jobs_use_distinct_children(tmp_path, monkeypatch):
    controller = PersonalController(tmp_path / "runtime", SCOPE, deps_dir=tmp_path)
    monkeypatch.setattr(controller, "capability", lambda: {"configured": True})
    script, args = stream_script()
    processes = attach_child(monkeypatch, controller, script, args)
    controller.start()
    try:
        first = controller.request(data(tmp_path, 2), "1" * 32)
        first_done = wait_status(controller, first["id"], {"completed", "failed"})
        assert first_done["status"] == "completed"
        assert controller._payloads == {}
        second = controller.request(data(tmp_path, 3), "2" * 32)
        second_done = wait_status(controller, second["id"], {"completed", "failed"})
        assert second_done["status"] == "completed"
        assert len(processes) == 2
        assert processes[0].pid != processes[1].pid
    finally:
        controller.shutdown()


def test_unknown_process_without_stream_makes_shutdown_fail_closed(tmp_path, monkeypatch):
    from radiworks.core.personal_jobs import PersonalJobError

    class UnknownProcess:
        stdin = None
        stdout = None
        stderr = None

        def poll(self):
            return None

        def kill(self):
            raise OSError("synthetic unconfirmed process")

        def terminate(self):
            return None

        def wait(self, timeout=None):
            raise subprocess.TimeoutExpired("synthetic", timeout)

    controller = PersonalController(tmp_path / "runtime", SCOPE, deps_dir=tmp_path)
    monkeypatch.setattr(controller, "capability", lambda: {"configured": True})
    process = UnknownProcess()
    monkeypatch.setattr(controller, "_spawn", lambda: process)
    controller.start()
    try:
        job = controller.request(data(tmp_path, 2), "3" * 32)
        failed = wait_status(controller, job["id"], {"completed", "failed"})
        controller._thread.join(5)
        assert not controller._thread.is_alive()
        assert failed["status"] == "failed"
        assert controller._process is process
        assert controller._stream is None
        assert controller._cpu_budget.acquire(blocking=False) is False
        with pytest.raises(PersonalJobError, match="shutdown"):
            controller.shutdown()
    finally:
        if controller._cpu_budget.acquire(blocking=False):
            controller._cpu_budget.release()




@pytest.mark.parametrize("failed_method", ["get", "claim"])
def test_preclaim_store_failure_stops_dispatch_and_discards_payload(tmp_path, monkeypatch, failed_method):
    from radiworks.core.personal_jobs import PersonalJobError

    controller = PersonalController(tmp_path / "runtime", SCOPE, deps_dir=tmp_path)
    monkeypatch.setattr(controller, "capability", lambda: {"configured": True})
    spawned = attach_child(monkeypatch, controller, "", [])
    original_get = controller.store.get if controller.store is not None else None
    controller._cpu_budget.acquire()
    controller.start()
    try:
        job = controller.request(data(tmp_path, 2), "4" * 32)
        store = controller.store
        original_get = store.get
        if failed_method == "get":
            monkeypatch.setattr(store, "get", lambda *args: (_ for _ in ()).throw(PersonalJobError("store_unavailable")))
        else:
            monkeypatch.setattr(store, "claim", lambda *args: (_ for _ in ()).throw(RuntimeError("commit failed")))
        controller._cpu_budget.release()
        controller._thread.join(5)
        assert not controller._thread.is_alive()
        assert controller._stop.is_set()
        assert controller._unavailable_reason == "store_unavailable"
        assert controller._payloads == {}
        assert spawned == []
        monkeypatch.setattr(store, "get", original_get)
        assert original_get(job["id"])["status"] == "queued"
    finally:
        if controller._cpu_budget.locked():
            controller._cpu_budget.release()
        controller.shutdown()

@pytest.mark.parametrize("count", [2, 24])
def test_final_block_store_rejection_fails_job_without_committing_rows(tmp_path, monkeypatch, count):
    from radiworks.core.personal_jobs import PersonalJobError

    controller = PersonalController(tmp_path / "runtime", SCOPE, deps_dir=tmp_path)
    monkeypatch.setattr(controller, "capability", lambda: {"configured": True})
    script, args = stream_script()
    attach_child(monkeypatch, controller, script, args)
    controller.start()
    monkeypatch.setattr(
        controller.store,
        "append_block",
        lambda *args: (_ for _ in ()).throw(PersonalJobError("ledger_write_failed")),
    )
    try:
        job = controller.request(data(tmp_path, count), "5" * 32)
        failed = wait_status(controller, job["id"], {"completed", "failed"})
        assert failed["status"] == "failed"
        assert failed["error"] == "worker_failed"
        assert failed["rows"] == []
    finally:
        controller.shutdown()


@pytest.mark.parametrize("failure_method", ["get", "fail"])
def test_fail_stream_store_error_stops_without_claiming_persisted_failure(tmp_path, monkeypatch, failure_method):
    from radiworks.core.personal_jobs import PersonalJobError

    controller = PersonalController(tmp_path / "runtime", SCOPE, deps_dir=tmp_path)
    original_capability = controller.capability
    monkeypatch.setattr(
        controller,
        "capability",
        lambda: {"configured": True, "unavailableReason": controller._unavailable_reason},
    )
    script = (
        "import sys; sys.stdin.buffer.read(); "
        "sys.stdout.buffer.write(b'{\\\"error\\\":\\\"worker_failed\\\"}\\n'); "
        "sys.stdout.buffer.flush()"
    )
    processes = attach_child(monkeypatch, controller, script, [])
    controller.start()
    store = controller.store
    original_get = store.get
    if failure_method == "get":
        calls = {"count": 0}

        def fail_during_failure_finalization(identifier):
            calls["count"] += 1
            if calls["count"] >= 2:
                raise PersonalJobError("store_unavailable")
            return original_get(identifier)

        monkeypatch.setattr(store, "get", fail_during_failure_finalization)
    else:
        monkeypatch.setattr(
            store,
            "fail",
            lambda *args: (_ for _ in ()).throw(PersonalJobError("store_unavailable")),
        )
    try:
        job = controller.request(data(tmp_path, 2), "6" * 32)
        controller._thread.join(5)
        assert not controller._thread.is_alive()
        assert controller._stop.is_set()
        assert controller.capability()["unavailableReason"] == "store_unavailable"
        assert controller._payloads == {}
        assert len(processes) == (0 if failure_method == "get" else 1)
        monkeypatch.setattr(store, "get", original_get)
        assert original_get(job["id"])["status"] == "running"
    finally:
        monkeypatch.setattr(controller, "capability", original_capability)
        controller.shutdown()

def test_second_append_failure_keeps_validated_prefix_and_fails_job(tmp_path, monkeypatch):
    from radiworks.core.personal_jobs import PersonalJobError

    controller = PersonalController(tmp_path / "runtime", SCOPE, deps_dir=tmp_path)
    monkeypatch.setattr(controller, "capability", lambda: {"configured": True})
    script, args = stream_script()
    attach_child(monkeypatch, controller, script, args)
    controller.start()
    store = controller.store
    append_block = store.append_block
    calls = {"count": 0}

    def append_then_fail(identifier, generation, rows):
        calls["count"] += 1
        if calls["count"] == 2:
            raise PersonalJobError("ledger_write_failed")
        return append_block(identifier, generation, rows)

    monkeypatch.setattr(store, "append_block", append_then_fail)
    try:
        job = controller.request(data(tmp_path, 24), "7" * 32)
        failed = wait_status(controller, job["id"], {"completed", "failed"})
        assert calls["count"] == 2
        assert failed["status"] == "failed"
        assert failed["error"] == "worker_failed"
        assert [row["inputIndex"] for row in failed["rows"]] == list(range(21))
    finally:
        controller.shutdown()