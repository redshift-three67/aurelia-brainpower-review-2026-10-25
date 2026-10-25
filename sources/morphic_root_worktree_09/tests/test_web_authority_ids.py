from __future__ import annotations

import importlib
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from apps.web.start_operations import (
    StartOperationConflictError,
    StartOperationStore,
)


INVALID_AUTHORITY_IDS = (
    "",
    " ",
    "..",
    "name/child",
    "name\\child",
    "C:\\absolute",
    "/absolute",
    "\\\\server\\share",
    "name:ads",
    "name\0suffix",
    "n\N{LATIN SMALL LETTER A WITH DIAERESIS}me",
    "a" * 129,
)


def _authority_ids():
    try:
        return importlib.import_module("apps.web.authority_ids")
    except ModuleNotFoundError:
        pytest.fail("apps.web.authority_ids is missing")


@pytest.mark.parametrize("invalid_id", INVALID_AUTHORITY_IDS)
def test_shared_authority_id_validator_rejects_without_sanitizing(
    invalid_id: str,
) -> None:
    module = _authority_ids()
    validator = getattr(module, "validate_authority_id", None)
    assert callable(validator)

    with pytest.raises(ValueError):
        validator(invalid_id)


@pytest.mark.parametrize(
    "valid_id",
    ["a", "A0", "job-1", "job_1", "z" * 128],
)
def test_shared_authority_id_validator_preserves_valid_ids(valid_id: str) -> None:
    module = _authority_ids()
    validator = getattr(module, "validate_authority_id", None)
    assert callable(validator)

    assert validator(valid_id) == valid_id


@pytest.mark.parametrize("valid_id", ["scan-a", "harm-auth-a"])
def test_scan_creation_validator_requires_shipped_prefix(valid_id: str) -> None:
    module = _authority_ids()
    validator = getattr(module, "validate_scan_job_id_for_creation", None)
    assert callable(validator)

    assert validator(valid_id) == valid_id
    with pytest.raises(ValueError):
        validator("job-valid-but-wrong-prefix")


def test_harmonization_creation_validator_requires_shipped_prefix() -> None:
    module = _authority_ids()
    validator = getattr(
        module,
        "validate_harmonization_job_id_for_creation",
        None,
    )
    assert callable(validator)

    assert validator("harm_valid") == "harm_valid"
    with pytest.raises(ValueError):
        validator("harm-valid-but-wrong-prefix")


@pytest.mark.parametrize(
    ("length", "creation_valid"),
    [
        pytest.param(118, True, id="largest-valid-derived-authority-128"),
        pytest.param(119, False, id="first-invalid-derived-authority-129"),
        pytest.param(128, False, id="shared-limit-still-invalid-for-creation"),
    ],
)
def test_harmonization_creation_limit_reserves_authority_prefix(
    length: int,
    creation_valid: bool,
) -> None:
    module = _authority_ids()
    job_id = "harm_" + "a" * (length - len("harm_"))
    assert len(job_id) == length

    assert module.validate_authority_id(job_id) == job_id
    if creation_valid:
        assert module.validate_harmonization_job_id_for_creation(job_id) == job_id
        authority_job_id = f"harm-auth-{job_id}"
        assert len(authority_job_id) == 128
        assert module.validate_scan_job_id_for_creation(authority_job_id) == authority_job_id
    else:
        with pytest.raises(ValueError):
            module.validate_harmonization_job_id_for_creation(job_id)


@pytest.mark.parametrize("operation", ["start", "replay", "get", "stop"])
def test_harmonization_service_validates_ids_before_worker_import(
    tmp_path: Path,
    operation: str,
) -> None:
    jobs_root = tmp_path / "worker-jobs"
    script = r'''
import os
from pathlib import Path
import sys

from apps.web.harmonization import WorkerHarmonizationService

service = WorkerHarmonizationService()
invalid_id = "../outside"
try:
    if sys.argv[1] == "start":
        service.start(
            mode="harmonization",
            target_frequency=432.0,
            duration_minutes=21,
            intention="harmonization",
            hardware_config={},
            job_id=invalid_id,
        )
    elif sys.argv[1] == "replay":
        service.get_for_replay(
            invalid_id,
            mode="harmonization",
            target_frequency=432.0,
            duration_minutes=21,
            intention="harmonization",
            hardware_config={},
            pulse_seconds=3.0,
            pause_seconds=2.0,
            duration_factor=1,
            solfeggio_base=432.0,
            report_id="",
            workbench_mode="standard",
            tenant_id="tenant-a",
            operator_id="operator-a",
        )
    elif sys.argv[1] == "get":
        service.get(invalid_id)
    else:
        service.stop(invalid_id)
except ValueError:
    pass
else:
    raise SystemExit("invalid ID was accepted")

if Path(os.environ["MORPHIC_HARMONIZATION_JOBS_DIR"]).exists():
    raise SystemExit("worker import created the jobs directory")
'''
    result = subprocess.run(
        [sys.executable, "-c", script, operation],
        cwd=Path(__file__).resolve().parents[1],
        env={
            **os.environ,
            "MORPHIC_HARMONIZATION_JOBS_DIR": str(jobs_root),
        },
        capture_output=True,
        text=True,
        timeout=30,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert not jobs_root.exists()


@pytest.mark.parametrize(
    ("kind", "invalid_job_id"),
    [
        ("scan", "../scan-outside"),
        ("scan", "harm_wrong-kind"),
        ("harmonization", "..\\harm-outside"),
        ("harmonization", "scan-wrong-kind"),
    ],
)
def test_start_operation_read_rejects_persisted_job_id_by_kind(
    tmp_path,
    kind: str,
    invalid_job_id: str,
) -> None:
    store = StartOperationStore(tmp_path / "operations")
    key = f"{kind}-authority-12345678"
    request_hash = "a" * 64
    owner_id = "tenant:operator"
    assert store.begin(
        kind=kind,
        key=key,
        owner_id=owner_id,
        request_sha256=request_hash,
    ) is None
    record_path = next(store.root.glob("*.json"))
    record = json.loads(record_path.read_text(encoding="utf-8"))
    record["job_id"] = invalid_job_id
    record_path.write_text(json.dumps(record), encoding="utf-8")

    with pytest.raises(StartOperationConflictError, match="job id"):
        store.begin(
            kind=kind,
            key=key,
            owner_id=owner_id,
            request_sha256=request_hash,
        )
