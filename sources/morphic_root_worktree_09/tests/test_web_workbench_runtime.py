from __future__ import annotations

import hashlib
import json
import multiprocessing
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from pathlib import Path

import pytest

from apps.web.main import create_app
from apps.web.scan_jobs import ScanJobOwnershipError
from apps.web.workbench import current_scan_profile_pool_fingerprint
from apps.web.workbench_runtime import WorkbenchRuntimeStore
from core.compliance.artifact_repository import parallel_export_plan_from_environment
from core.compliance.runtime_manifest import RuntimeManifestService
from tests.test_web_shell import request
from tests.test_web_authority_ids import INVALID_AUTHORITY_IDS


def _finalize_trace_in_process(root: str, queue) -> None:
    store = WorkbenchRuntimeStore(root)
    try:
        store.finalize_run_trace_once("run-cross-process", {"status": "completed"})
        queue.put("finalized")
    except ValueError:
        queue.put("conflict")


def _save_templates_in_process(root: str, prefix: str, start_event, queue) -> None:
    store = WorkbenchRuntimeStore(root)
    start_event.wait(timeout=5)
    for index in range(10):
        store.save_template(name=f"{prefix}-{index}", draft={"focus": prefix})
    queue.put(prefix)


def _delete_template_in_process(root: str, template_id: str, start_event, queue) -> None:
    store = WorkbenchRuntimeStore(root)
    start_event.wait(timeout=5)
    queue.put(("delete", store.delete_template(template_id)))


def _save_one_template_in_process(root: str, start_event, queue) -> None:
    store = WorkbenchRuntimeStore(root)
    start_event.wait(timeout=5)
    created = store.save_template(name="concurrent-save", draft={"focus": "new"})
    queue.put(("save", created["template_id"]))


def _save_large_drafts_in_process(root: str, marker: str, start_event, queue) -> None:
    store = WorkbenchRuntimeStore(root)
    start_event.wait(timeout=5)
    for index in range(20):
        store.save_draft(
            {
                "marker": marker,
                "sequence": index,
                "payload": marker * 50000,
            }
        )
    queue.put(marker)


def _observe_draft_json_in_process(
    path: str, observer_ready_event, stop_event, queue
) -> None:
    observed = 0
    invalid = 0
    target = Path(path)
    observer_ready_event.set()
    while not stop_event.is_set():
        try:
            payload = json.loads(target.read_text(encoding="utf-8"))
            marker = payload["draft"]["marker"]
            if marker not in {"A", "B"} or payload["draft"]["payload"] != marker * 50000:
                invalid += 1
            observed += 1
        except (FileNotFoundError, PermissionError):
            pass
        except (KeyError, json.JSONDecodeError):
            invalid += 1
        time.sleep(0.001)
    queue.put((observed, invalid))


def _draft_payload(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "last_name": "Deisenhofer",
        "first_name": "Klaus",
        "birth_date": "09041966",
        "birth_place": "Augsburg",
        "focus": "Bronchien",
        "profile_level": 3,
        "top_n": 7,
        "profile_template": "personal-focused",
        "entropy_mode": "hybrid",
        "adaptive_limits": True,
    }
    payload.update(overrides)
    payload.setdefault(
        "scan_profile_pool_fingerprint",
        current_scan_profile_pool_fingerprint(payload["profile_level"]),
    )
    return payload


def _scan_request_payload(**overrides: object) -> dict[str, object]:
    payload = {
        **_draft_payload(image_path="C:/images/client-reference.jpg"),
        "consent_local": True,
        "consent_safety": True,
    }
    payload.update(overrides)
    return payload


class _FakeScanJobs:
    def __init__(self) -> None:
        self.started: list[list[str]] = []
        self.owner_id: str | None = None

    def start(
        self,
        command: list[str],
        owner_id: str | None = None,
        env_overrides: dict[str, str] | None = None,
        job_id: str | None = None,
    ) -> dict[str, object]:
        self.started.append(command)
        self.owner_id = owner_id
        return {
            "executes": True,
            "job_id": job_id,
            "status": "running",
            "command": command,
            "progress_percent": 12.5,
            "current_phase": "Phase 1",
            "current_substep": "Screening aller Haupt-Profile",
            "completed_substeps": [],
        }

    def get(self, job_id: str) -> dict[str, object]:
        return {"job_id": job_id, "owner_id": self.owner_id, "status": "running"}

    def get_owned(
        self,
        job_id: str,
        *,
        expected_owner_id: str,
    ) -> dict[str, object]:
        snapshot = self.get(job_id)
        if snapshot.get("owner_id") != expected_owner_id:
            raise ScanJobOwnershipError("scan job owner identity mismatch")
        return snapshot


class _FailingTraceStore:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, object]]] = []

    def ensure_run_trace(self, run_id: str, payload: dict[str, object]) -> None:
        self.calls.append((run_id, payload))
        raise OSError("disk full")


def test_workbench_runtime_store_roundtrips_draft_template_and_run_trace(
    tmp_path: Path,
) -> None:
    root = tmp_path / "workbench"
    store = WorkbenchRuntimeStore(root)
    draft = store.save_draft(_draft_payload())
    template = store.save_template(name="Respiratory baseline", draft=_draft_payload())
    trace = store.ensure_run_trace(
        "scan-123",
        {
            "status": "running",
            "focus": "Bronchien",
            "command": ["python", "-m", "apps.cli.main"],
        },
    )

    reloaded = WorkbenchRuntimeStore(root)

    assert reloaded.load_draft() == draft
    assert reloaded.list_templates() == [template]
    assert reloaded.get_run_trace("scan-123") == trace


def test_workbench_runtime_store_excludes_local_ai_from_saved_draft(
    tmp_path: Path,
) -> None:
    store = WorkbenchRuntimeStore(tmp_path / "workbench")
    source = {"focus": "Schlaf", "local_ai_enabled": True}

    saved = store.save_draft(source)

    assert saved["draft"] == {"focus": "Schlaf"}
    assert store.load_draft()["draft"] == {"focus": "Schlaf"}
    assert source == {"focus": "Schlaf", "local_ai_enabled": True}


def test_workbench_runtime_store_excludes_local_ai_from_saved_template(
    tmp_path: Path,
) -> None:
    store = WorkbenchRuntimeStore(tmp_path / "workbench")
    source = {"profile_level": 3, "local_ai_enabled": True}

    saved = store.save_template(name="Default off", draft=source)

    assert saved["draft"] == {"profile_level": 3}
    assert store.list_templates()[0]["draft"] == {"profile_level": 3}
    assert source == {"profile_level": 3, "local_ai_enabled": True}


def test_workbench_runtime_store_isolates_all_state_by_hashed_tenant(
    tmp_path: Path,
) -> None:
    base_root = tmp_path / "workbench"
    tenant_a = "Kunden/Mandant Alpha"
    tenant_b = "Kunden/Mandant Beta"
    store_a = WorkbenchRuntimeStore(base_root, tenant_id=tenant_a)
    store_b = WorkbenchRuntimeStore(base_root, tenant_id=tenant_b)

    draft_a = store_a.save_draft({"marker": "tenant-a"})
    template_a = store_a.save_template(
        name="Tenant A",
        draft={"marker": "tenant-a"},
    )
    trace_a = store_a.ensure_run_trace(
        "scan-shared",
        {"status": "running", "marker": "tenant-a"},
    )

    expected_a = "tenant-v1-" + hashlib.sha256(tenant_a.encode("utf-8")).hexdigest()
    expected_b = "tenant-v1-" + hashlib.sha256(tenant_b.encode("utf-8")).hexdigest()
    assert store_a.root == base_root / expected_a
    assert store_b.root == base_root / expected_b
    assert tenant_a not in store_a.root.name
    assert tenant_b not in store_b.root.name
    assert store_b.load_draft() == {"draft": {}, "updated_at": None}
    assert store_b.list_templates() == []
    with pytest.raises(KeyError):
        store_b.get_run_trace("scan-shared")

    draft_b = store_b.save_draft({"marker": "tenant-b"})
    template_b = store_b.save_template(
        name="Tenant B",
        draft={"marker": "tenant-b"},
    )
    trace_b = store_b.ensure_run_trace(
        "scan-shared",
        {"status": "running", "marker": "tenant-b"},
    )

    assert store_a.load_draft() == draft_a
    assert store_a.list_templates() == [template_a]
    assert store_a.get_run_trace("scan-shared") == trace_a
    assert store_b.load_draft() == draft_b
    assert store_b.list_templates() == [template_b]
    assert store_b.get_run_trace("scan-shared") == trace_b


def test_workbench_runtime_store_without_tenant_preserves_explicit_root(
    tmp_path: Path,
) -> None:
    explicit_root = tmp_path / "explicit-workbench"
    store = WorkbenchRuntimeStore(explicit_root)

    store.save_draft({"marker": "direct"})
    store.save_template(name="Direct", draft={"marker": "direct"})
    store.ensure_run_trace("scan-direct", {"status": "running"})

    assert store.root == explicit_root
    assert (explicit_root / "draft.json").is_file()
    assert (explicit_root / "templates.json").is_file()
    assert (explicit_root / "run_traces.json").is_file()


@pytest.mark.parametrize("tenant_id", ["", "   "])
def test_workbench_runtime_store_rejects_supplied_blank_tenant(
    tmp_path: Path,
    tenant_id: str,
) -> None:
    with pytest.raises(ValueError):
        WorkbenchRuntimeStore(tmp_path / "workbench", tenant_id=tenant_id)


@pytest.mark.parametrize("invalid_id", INVALID_AUTHORITY_IDS)
def test_run_trace_ids_are_rejected_before_store_lock(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    invalid_id: str,
) -> None:
    store = WorkbenchRuntimeStore(tmp_path / "workbench")
    lock_calls: list[str] = []

    @contextmanager
    def unexpected_lock(store_name: str):
        lock_calls.append(store_name)
        yield

    monkeypatch.setattr(store, "_process_lock", unexpected_lock)

    with pytest.raises(ValueError):
        store.ensure_run_trace(invalid_id, {"status": "running"})
    with pytest.raises(ValueError):
        store.get_run_trace(invalid_id)
    with pytest.raises(ValueError):
        store.finalize_run_trace_once(invalid_id, {"status": "completed"})
    assert lock_calls == []
    assert not (tmp_path / "workbench").exists()


@pytest.mark.parametrize("method", ["register", "finalize"])
def test_run_trace_payload_id_is_rejected_before_store_lock(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    method: str,
) -> None:
    store = WorkbenchRuntimeStore(tmp_path / "workbench")
    lock_calls: list[str] = []

    @contextmanager
    def unexpected_lock(store_name: str):
        lock_calls.append(store_name)
        yield

    monkeypatch.setattr(store, "_process_lock", unexpected_lock)
    payload = {"run_id": "../outside", "status": "completed"}

    with pytest.raises(ValueError):
        if method == "register":
            store.ensure_run_trace("scan-valid", payload)
        else:
            store.finalize_run_trace_once("scan-valid", payload)
    assert lock_calls == []
    assert not (tmp_path / "workbench").exists()


@pytest.mark.parametrize("invalid_id", INVALID_AUTHORITY_IDS)
@pytest.mark.parametrize("operation", ["get", "register", "finalize"])
def test_persisted_run_trace_ids_fail_closed_without_mutating_store_bytes(
    tmp_path: Path,
    invalid_id: str,
    operation: str,
) -> None:
    root = tmp_path / "workbench"
    root.mkdir()
    path = root / "run_traces.json"
    original = json.dumps(
        {"run_traces": [{"run_id": invalid_id, "status": "running"}]},
        ensure_ascii=False,
    ).encode("utf-8")
    path.write_bytes(original)
    store = WorkbenchRuntimeStore(root)

    with pytest.raises(RuntimeError, match="invalid authority"):
        if operation == "get":
            store.get_run_trace("scan-valid")
        elif operation == "register":
            store.ensure_run_trace("scan-valid", {"status": "running"})
        else:
            store.finalize_run_trace_once(
                "scan-valid", {"status": "completed"}
            )

    assert path.read_bytes() == original


def test_persisted_run_trace_sanitization_collision_fails_without_rewrite(
    tmp_path: Path,
) -> None:
    root = tmp_path / "workbench"
    root.mkdir()
    path = root / "run_traces.json"
    original = json.dumps(
        {
            "run_traces": [
                {"run_id": "name/child", "status": "running"},
                {"run_id": "name\\child", "status": "running"},
            ]
        }
    ).encode("utf-8")
    path.write_bytes(original)
    store = WorkbenchRuntimeStore(root)

    with pytest.raises(RuntimeError, match="invalid authority"):
        store.ensure_run_trace("scan-valid", {"status": "running"})

    assert path.read_bytes() == original
    assert not (root / "name_child.json").exists()


@pytest.mark.parametrize("operation", ["get", "register", "finalize"])
def test_persisted_run_trace_corruption_rejects_before_lock_side_effect(
    tmp_path: Path,
    operation: str,
) -> None:
    root = tmp_path / "workbench"
    root.mkdir()
    path = root / "run_traces.json"
    original = json.dumps(
        {"run_traces": [{"run_id": "name/child", "status": "running"}]}
    ).encode("utf-8")
    path.write_bytes(original)
    store = WorkbenchRuntimeStore(root)

    with pytest.raises(RuntimeError, match="invalid authority"):
        if operation == "get":
            store.get_run_trace("scan-valid")
        elif operation == "register":
            store.ensure_run_trace("scan-valid", {"status": "running"})
        else:
            store.finalize_run_trace_once(
                "scan-valid",
                {"status": "completed"},
            )

    assert path.read_bytes() == original
    assert {entry.name for entry in root.iterdir()} == {"run_traces.json"}


@pytest.mark.parametrize(
    "payload",
    [
        pytest.param([], id="array-root"),
        pytest.param({}, id="missing-run-traces"),
        pytest.param({"runs": []}, id="wrong-root-key"),
        pytest.param({"run_traces": {}}, id="non-list-run-traces"),
        pytest.param(
            {"run_traces": [], "schema_version": 1},
            id="unknown-root-field",
        ),
    ],
)
def test_structurally_corrupt_run_trace_root_rejects_before_lock_or_overwrite(
    tmp_path: Path,
    payload: object,
) -> None:
    root = tmp_path / "workbench"
    root.mkdir()
    path = root / "run_traces.json"
    original = json.dumps(payload).encode("utf-8")
    path.write_bytes(original)
    store = WorkbenchRuntimeStore(root)

    with pytest.raises(RuntimeError, match="schema"):
        store.ensure_run_trace("scan-valid", {"status": "running"})

    assert path.read_bytes() == original
    assert {entry.name for entry in root.iterdir()} == {"run_traces.json"}


def test_workbench_runtime_store_save_and_load_draft(tmp_path: Path) -> None:
    store = WorkbenchRuntimeStore(tmp_path / "workbench")

    saved = store.save_draft(_draft_payload(notes="morgens staerker"))

    assert saved["draft"]["notes"] == "morgens staerker"
    assert store.load_draft() == saved


def test_workbench_runtime_store_save_list_and_delete_template(tmp_path: Path) -> None:
    store = WorkbenchRuntimeStore(tmp_path / "workbench")

    created = store.save_template(
        name="Respiratory baseline",
        draft=_draft_payload(focus="Lunge"),
    )

    assert created["template_id"].startswith("tpl-")
    assert created["name"] == "Respiratory baseline"
    assert store.list_templates() == [created]

    deleted = store.delete_template(created["template_id"])

    assert deleted is True
    assert store.list_templates() == []


def test_workbench_runtime_store_serializes_template_writes(
    tmp_path: Path,
    monkeypatch,
) -> None:
    store = WorkbenchRuntimeStore(tmp_path / "workbench")
    original_save_store = store._save_store
    first_save_waiting = threading.Event()
    allow_first_save = threading.Event()
    save_calls = 0
    save_calls_lock = threading.Lock()

    def blocked_save(store_name: str, payload: dict[str, object]) -> None:
        nonlocal save_calls
        if store_name != "templates":
            original_save_store(store_name, payload)
            return
        with save_calls_lock:
            save_calls += 1
            call_index = save_calls
        if call_index == 1:
            first_save_waiting.set()
            allow_first_save.wait(timeout=2)
        original_save_store(store_name, payload)

    monkeypatch.setattr(store, "_save_store", blocked_save)
    first_thread = threading.Thread(
        target=store.save_template,
        kwargs={"name": "Template A", "draft": _draft_payload(focus="A")},
    )
    second_thread = threading.Thread(
        target=store.save_template,
        kwargs={"name": "Template B", "draft": _draft_payload(focus="B")},
    )

    first_thread.start()
    assert first_save_waiting.wait(timeout=1)
    second_thread.start()
    second_thread.join(timeout=0.2)
    allow_first_save.set()
    first_thread.join(timeout=1)
    second_thread.join(timeout=1)

    assert not first_thread.is_alive()
    assert not second_thread.is_alive()
    assert {entry["name"] for entry in store.list_templates()} == {
        "Template A",
        "Template B",
    }


def test_workbench_runtime_store_serializes_template_writes_across_processes(
    tmp_path: Path,
) -> None:
    context = multiprocessing.get_context("spawn")
    root = str(tmp_path / "workbench")
    start_event = context.Event()
    queue = context.Queue()
    processes = [
        context.Process(
            target=_save_templates_in_process,
            args=(root, prefix, start_event, queue),
        )
        for prefix in ("Process-A", "Process-B")
    ]
    for process in processes:
        process.start()
    start_event.set()
    for process in processes:
        process.join(timeout=10)

    assert all(process.exitcode == 0 for process in processes)
    assert {queue.get(timeout=1) for _ in processes} == {"Process-A", "Process-B"}
    templates = WorkbenchRuntimeStore(root).list_templates()
    assert len(templates) == 20
    assert {entry["name"] for entry in templates} == {
        f"{prefix}-{index}"
        for prefix in ("Process-A", "Process-B")
        for index in range(10)
    }


def test_workbench_runtime_store_ensure_preserves_existing_trace_bytes(
    tmp_path: Path,
) -> None:
    store = WorkbenchRuntimeStore(tmp_path / "workbench")

    first = store.ensure_run_trace(
        "scan-123",
        {
            "status": "running",
            "command": ["python", "-m", "apps.cli.main"],
        },
    )
    trace_path = store._path_for("run_traces")
    first_bytes = trace_path.read_bytes()
    repeated = store.ensure_run_trace(
        "scan-123",
        {
            "status": "completed",
            "result_count": 3,
        },
    )

    assert first["run_id"] == "scan-123"
    assert repeated == first
    assert repeated["status"] == "running"
    assert "result_count" not in repeated
    assert trace_path.read_bytes() == first_bytes
    assert store.get_run_trace("scan-123") == first


def test_workbench_runtime_store_concurrent_ensure_keeps_one_first_writer(
    tmp_path: Path,
) -> None:
    store = WorkbenchRuntimeStore(tmp_path / "workbench")
    barrier = threading.Barrier(2)

    def ensure(marker: str) -> dict[str, object]:
        barrier.wait(timeout=2)
        return store.ensure_run_trace(
            "run-shared",
            {"status": "running", "first_writer": marker},
        )

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(ensure, marker) for marker in ("A", "B")]
        results = [future.result(timeout=5) for future in futures]

    assert results[0] == results[1]
    assert results[0]["first_writer"] in {"A", "B"}
    traces = store._load_store("run_traces")["run_traces"]
    assert traces == [results[0]]


def test_workbench_api_persists_draft_and_templates(tmp_path: Path) -> None:
    app = create_app(runtime_dir=tmp_path)

    empty_draft = request(app, "GET", "/api/workbench/draft")

    assert empty_draft.status_code == 200
    assert empty_draft.json() == {"draft": {}, "updated_at": None}

    saved_draft = request(
        app,
        "PUT",
        "/api/workbench/draft",
        json_body={
            "draft": _draft_payload(notes="abends staerker"),
            "updated_at": None,
            "persist_sensitive_data": True,
        },
    )

    assert saved_draft.status_code == 200
    assert saved_draft.json()["draft"]["notes"] == "abends staerker"

    listed_draft = request(app, "GET", "/api/workbench/draft")

    assert listed_draft.status_code == 200
    assert listed_draft.json() == saved_draft.json()

    roundtripped_draft = request(
        app,
        "PUT",
        "/api/workbench/draft",
        json_body=listed_draft.json(),
    )

    assert roundtripped_draft.status_code == 422
    approved_roundtrip = request(
        app,
        "PUT",
        "/api/workbench/draft",
        json_body={**listed_draft.json(), "persist_sensitive_data": True},
    )
    assert approved_roundtrip.status_code == 200
    assert approved_roundtrip.json()["draft"] == listed_draft.json()["draft"]
    assert "draft" not in approved_roundtrip.json()["draft"]

    rejected_sensitive_template = request(
        app,
        "POST",
        "/api/workbench/templates",
        json_body={"name": "Unsafe", "draft": _draft_payload(focus="Lunge")},
    )

    assert rejected_sensitive_template.status_code == 422
    assert "explizite" in rejected_sensitive_template.json()["detail"]

    invalid_draft = request(
        app,
        "PUT",
        "/api/workbench/draft",
        json_body=_draft_payload(notes="wrong-shape"),
    )

    assert invalid_draft.status_code == 422

    created_template = request(
        app,
        "POST",
        "/api/workbench/templates",
        json_body={
            "name": "Respiratory baseline",
            "draft": _draft_payload(focus="Lunge"),
            "persist_sensitive_data": True,
        },
    )

    assert created_template.status_code == 200
    template = created_template.json()
    assert template["template_id"].startswith("tpl-")
    assert template["name"] == "Respiratory baseline"

    listed_templates = request(app, "GET", "/api/workbench/templates")

    assert listed_templates.status_code == 200
    assert listed_templates.json()["templates"] == [template]

    deleted_template = request(
        app,
        "DELETE",
        f"/api/workbench/templates/{template['template_id']}",
    )

    assert deleted_template.status_code == 200
    assert deleted_template.json() == {
        "deleted": True,
        "template_id": template["template_id"],
    }
    assert request(app, "GET", "/api/workbench/templates").json() == {"templates": []}


def test_scan_job_start_seeds_run_trace_and_workbench_endpoint_reads_it(
    tmp_path: Path,
) -> None:
    jobs = _FakeScanJobs()
    app = create_app(runtime_dir=tmp_path, scan_jobs=jobs)

    response = request(
        app,
        "POST",
        "/api/scan/jobs",
        json_body=_scan_request_payload(workbench_mode="expert"),
    )

    assert response.status_code == 200
    payload = response.json()
    job_id = payload["job_id"]
    trace = app.state.workbench_store.get_run_trace(job_id)

    assert job_id.startswith("scan-op-")
    assert trace["run_id"] == job_id
    assert trace["job_id"] == job_id
    assert trace["status"] == "running"
    assert trace["workbench_mode"] == "expert"
    assert trace["profile_template"] == "personal-focused"
    assert trace["entropy_mode"] == "hybrid"
    assert trace["launcher"]["script_path"] == "Run-MultiplexScan.ps1"
    assert "launcher" not in payload
    assert trace["image_enabled"] is True
    assert "command" not in trace
    assert "notes" not in trace
    assert "focus" not in trace
    assert "image_path" not in trace

    trace_response = request(app, "GET", f"/api/workbench/run-trace/{job_id}")

    assert trace_response.status_code == 200
    assert trace_response.json() == trace


@pytest.mark.parametrize("owner_id", ["operator-b", None, "", "   "])
def test_workbench_run_trace_rejects_untrusted_scan_owner(
    tmp_path: Path,
    monkeypatch,
    owner_id: str | None,
) -> None:
    class ForeignJobs:
        def get(self, job_id: str) -> dict[str, object]:
            return {"job_id": job_id, "owner_id": owner_id, "status": "completed"}

        def get_owned(
            self,
            job_id: str,
            *,
            expected_owner_id: str,
        ) -> dict[str, object]:
            snapshot = self.get(job_id)
            if snapshot.get("owner_id") != expected_owner_id:
                raise ScanJobOwnershipError("scan job owner identity mismatch")
            return snapshot

    monkeypatch.setenv("MORPHIC_OPERATOR_ID", "operator-a")
    app = create_app(runtime_dir=tmp_path, scan_jobs=ForeignJobs())
    app.state.workbench_store.ensure_run_trace(
        "foreign-run", {"job_id": "foreign-run", "status": "completed"}
    )

    response = request(app, "GET", "/api/workbench/run-trace/foreign-run")

    assert response.status_code == 403


def test_scan_job_start_keeps_running_when_run_trace_persistence_fails(
    tmp_path: Path,
) -> None:
    jobs = _FakeScanJobs()
    app = create_app(runtime_dir=tmp_path, scan_jobs=jobs)
    failing_store = _FailingTraceStore()
    app.state.workbench_store = failing_store

    response = request(
        app,
        "POST",
        "/api/scan/jobs",
        json_body=_scan_request_payload(workbench_mode="expert"),
    )

    assert response.status_code == 200
    job_id = response.json()["job_id"]
    assert job_id.startswith("scan-op-")
    assert len(jobs.started) == 1
    assert len(failing_store.calls) == 1
    run_id, trace_seed = failing_store.calls[0]
    assert run_id == job_id
    assert trace_seed["job_id"] == job_id
    assert trace_seed["review"]["client_id"].startswith("cli-")
    assert "client" not in trace_seed["review"]
    assert "focus" not in trace_seed["review"]
    assert "Deisenhofer" not in str(trace_seed)


def test_scan_job_start_adds_opt_in_parallel_export_plan_without_writing(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setenv("MORPHIC_PARALLEL_EXPORT_ROOT", str(tmp_path / "parallel"))
    jobs = _FakeScanJobs()
    app = create_app(runtime_dir=tmp_path, scan_jobs=jobs)

    response = request(app, "POST", "/api/scan/jobs", json_body=_scan_request_payload())

    assert response.status_code == 200
    payload = response.json()
    trace = app.state.workbench_store.get_run_trace(payload["job_id"])
    client_id = trace["review"]["client_id"]
    plan = Path(
        parallel_export_plan_from_environment(
            tenant_id=app.state.operator_context.tenant_id,
            client_id=client_id,
            session_id=payload["job_id"],
        )
    )
    assert plan.name == "planned_result.json"
    assert "Deisenhofer" not in str(plan)
    assert not plan.exists()
    command = jobs.started[0]
    assert command[command.index("--export") + 1] == str(app.state.report_roots[0])
    assert "parallel_export_plan" not in payload
    assert "parallel_export_client_id" not in payload
    assert "command" not in payload
    manifest = RuntimeManifestService(tmp_path).erasure_manifest(
        client_id
    )
    assert manifest["artifacts"][0]["path"] == str(plan)
    assert manifest["artifacts"][0]["artifact_type"] == "parallel_export_plan"


def test_run_trace_terminal_finalization_is_atomic_across_processes(tmp_path: Path) -> None:
    store = WorkbenchRuntimeStore(tmp_path)
    store.ensure_run_trace("run-cross-process", {"status": "running"})
    context = multiprocessing.get_context("spawn")
    queue = context.Queue()
    processes = [
        context.Process(target=_finalize_trace_in_process, args=(str(tmp_path), queue))
        for _ in range(2)
    ]
    for process in processes:
        process.start()
    for process in processes:
        process.join(timeout=20)
        assert process.exitcode == 0

    assert sorted(queue.get(timeout=5) for _ in processes) == ["conflict", "finalized"]


def test_corrupt_runtime_store_fails_closed_without_overwriting_bytes(tmp_path: Path) -> None:
    path = tmp_path / "templates.json"
    corrupt = b'{"templates": ['
    path.write_bytes(corrupt)
    store = WorkbenchRuntimeStore(tmp_path)

    with pytest.raises(RuntimeError, match="templates"):
        store.save_template(name="must-not-overwrite", draft={"focus": "blocked"})

    assert path.read_bytes() == corrupt


def test_template_create_and_delete_different_ids_are_cross_process_commutative(
    tmp_path: Path,
) -> None:
    store = WorkbenchRuntimeStore(tmp_path)
    old = store.save_template(name="delete-me", draft={"focus": "old"})
    context = multiprocessing.get_context("spawn")
    start_event = context.Event()
    queue = context.Queue()
    processes = [
        context.Process(
            target=_delete_template_in_process,
            args=(str(tmp_path), old["template_id"], start_event, queue),
        ),
        context.Process(
            target=_save_one_template_in_process,
            args=(str(tmp_path), start_event, queue),
        ),
    ]
    for process in processes:
        process.start()
    start_event.set()
    for process in processes:
        process.join(timeout=20)
        assert process.exitcode == 0

    results = [queue.get(timeout=5) for _ in processes]
    created_id = next(value for action, value in results if action == "save")
    assert next(value for action, value in results if action == "delete") is True
    remaining = store.list_templates()
    assert {entry["template_id"] for entry in remaining} == {created_id}


def test_independent_draft_writers_never_expose_partial_json(tmp_path: Path) -> None:
    context = multiprocessing.get_context("spawn")
    start_event = context.Event()
    observer_ready_event = context.Event()
    stop_event = context.Event()
    queue = context.Queue()
    draft_path = tmp_path / "draft.json"
    observer = context.Process(
        target=_observe_draft_json_in_process,
        args=(str(draft_path), observer_ready_event, stop_event, queue),
    )
    writers = [
        context.Process(
            target=_save_large_drafts_in_process,
            args=(str(tmp_path), marker, start_event, queue),
        )
        for marker in ("A", "B")
    ]
    observer.start()
    for writer in writers:
        writer.start()
    assert observer_ready_event.wait(timeout=5), "observer process did not become ready"
    start_event.set()
    for writer in writers:
        writer.join(timeout=30)
        assert writer.exitcode == 0
    assert {queue.get(timeout=5), queue.get(timeout=5)} == {"A", "B"}
    stop_event.set()
    observer.join(timeout=10)
    assert observer.exitcode == 0
    observed, invalid = queue.get(timeout=5)

    assert observed > 0
    assert invalid == 0
    final = json.loads(draft_path.read_text(encoding="utf-8"))
    marker = final["draft"]["marker"]
    assert marker in {"A", "B"}
    assert final["draft"]["payload"] == marker * 50000
