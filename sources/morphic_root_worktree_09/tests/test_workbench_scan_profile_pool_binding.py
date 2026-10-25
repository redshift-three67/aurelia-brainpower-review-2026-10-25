from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

import apps.web.main as web_main
from apps.web.contracts import Phase1ScanRequest
from apps.web.main import create_app
from apps.web.workbench import (
    ScanProfilePoolAuthority,
    current_scan_profile_pool_authority,
    current_scan_profile_pool_fingerprint,
)
from core.profile_sync import SCAN_PROFILE_POOL_FINGERPRINT_ENV
from tests.test_web_shell import request


def _request_payload(
    fingerprint: str,
    *,
    profile_level: int = 3,
    top_n: int = 5,
) -> dict[str, object]:
    return {
        "last_name": "Gate",
        "first_name": "Drei",
        "birth_date": "09041966",
        "birth_place": "Augsburg",
        "focus": "synthetischer Fokus",
        "profile_level": profile_level,
        "top_n": top_n,
        "scan_profile_pool_fingerprint": fingerprint,
        "consent_local": True,
        "consent_safety": True,
    }


class FakeScanJobs:
    def __init__(self) -> None:
        self.started: list[list[str]] = []
        self.environments: list[dict[str, str] | None] = []

    def start(
        self,
        command: list[str],
        owner_id: str | None = None,
        env_overrides: dict[str, str] | None = None,
        job_id: str | None = None,
    ) -> dict[str, Any]:
        self.started.append(list(command))
        self.environments.append(
            None if env_overrides is None else dict(env_overrides)
        )
        return {
            "executes": True,
            "job_id": job_id or "scan-gate3",
            "status": "running",
            "command": command,
            "progress_percent": 0.0,
            "current_phase": "Phase 1",
            "current_substep": "Screening aller Haupt-Profile",
            "completed_substeps": [],
            "owner_id": owner_id,
        }


@pytest.mark.parametrize("fingerprint", ["", "A" * 64, "a" * 63, "g" * 64])
def test_scan_request_rejects_invalid_pool_fingerprint(fingerprint: str) -> None:
    with pytest.raises(ValidationError):
        Phase1ScanRequest.model_validate(_request_payload(fingerprint))


def test_scan_request_requires_pool_fingerprint() -> None:
    payload = _request_payload("a" * 64)
    payload.pop("scan_profile_pool_fingerprint")

    with pytest.raises(ValidationError):
        Phase1ScanRequest.model_validate(payload)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        pytest.param("profile_level", "3", id="profile-level-string"),
        pytest.param("profile_level", 3.0, id="profile-level-float"),
        pytest.param("profile_level", True, id="profile-level-bool"),
        pytest.param("top_n", "5", id="top-n-string"),
        pytest.param("top_n", 5.0, id="top-n-float"),
        pytest.param("top_n", True, id="top-n-bool"),
        pytest.param("consent_local", "true", id="consent-local-string"),
        pytest.param("consent_local", 1, id="consent-local-int"),
        pytest.param("consent_local", 1.0, id="consent-local-float"),
        pytest.param("consent_safety", "true", id="consent-safety-string"),
        pytest.param("consent_safety", 1, id="consent-safety-int"),
        pytest.param("consent_safety", 1.0, id="consent-safety-float"),
        pytest.param("adaptive_limits", "false", id="adaptive-string"),
        pytest.param("adaptive_limits", 0, id="adaptive-int"),
        pytest.param("adaptive_limits", 0.0, id="adaptive-float"),
        pytest.param("planetary_vector_enabled", "false", id="planetary-string"),
        pytest.param("planetary_vector_enabled", 0, id="planetary-int"),
        pytest.param("planetary_vector_enabled", 0.0, id="planetary-float"),
    ],
)
@pytest.mark.parametrize("path", ["/api/scan/preview", "/api/scan/jobs"])
def test_scan_endpoints_reject_phase1_scalar_coercion_without_side_effects(
    tmp_path: Path,
    field: str,
    value: object,
    path: str,
) -> None:
    jobs = FakeScanJobs()
    app = create_app(runtime_dir=tmp_path / "runtime", scan_jobs=jobs)
    payload = _request_payload(current_scan_profile_pool_fingerprint(3))
    payload[field] = value

    response = request(app, "POST", path, json_body=payload)

    assert response.status_code == 422
    assert jobs.started == []
    assert list(app.state.start_operations.root.glob("*.json")) == []


@pytest.mark.parametrize("path", ["/api/scan/preview", "/api/scan/jobs"])
@pytest.mark.parametrize("fingerprint", [None, "", "A" * 64, "a" * 63, "g" * 64])
def test_scan_endpoints_reject_missing_or_invalid_pool_fingerprint(
    tmp_path: Path,
    path: str,
    fingerprint: str | None,
) -> None:
    jobs = FakeScanJobs()
    app = create_app(runtime_dir=tmp_path / "runtime", scan_jobs=jobs)
    payload = _request_payload(fingerprint or "")
    if fingerprint is None:
        payload.pop("scan_profile_pool_fingerprint")

    response = request(app, "POST", path, json_body=payload)

    assert response.status_code == 422
    assert jobs.started == []
    assert list(app.state.start_operations.root.glob("*.json")) == []


def test_stale_pool_fingerprint_rejects_preview_before_launcher(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    jobs = FakeScanJobs()
    app = create_app(runtime_dir=tmp_path / "runtime", scan_jobs=jobs)
    monkeypatch.setattr(
        web_main,
        "current_scan_profile_pool_authority",
        lambda _level: ScanProfilePoolAuthority(
            profiles=(("profile", "Profil"),),
            count=1,
            fingerprint="b" * 64,
        ),
        raising=False,
    )

    def forbidden_launcher(*_args: object, **_kwargs: object) -> object:
        pytest.fail("stale preview reached the launcher")

    monkeypatch.setattr(web_main, "build_phase1_scan_launcher", forbidden_launcher)

    response = request(
        app,
        "POST",
        "/api/scan/preview",
        json_body=_request_payload("a" * 64),
    )

    assert response.status_code == 409
    assert response.json() == {
        "detail": "Scanprofil-Pool hat sich geändert. Bitte neu laden und erneut prüfen."
    }
    assert response.headers["x-morphic-scan-profile-pool"] == "stale"
    assert jobs.started == []
    assert list(app.state.start_operations.root.glob("*.json")) == []


def test_stale_pool_fingerprint_rejects_start_before_side_effects(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    jobs = FakeScanJobs()
    app = create_app(runtime_dir=tmp_path / "runtime", scan_jobs=jobs)
    monkeypatch.setattr(
        web_main,
        "current_scan_profile_pool_authority",
        lambda _level: ScanProfilePoolAuthority(
            profiles=(("profile", "Profil"),),
            count=1,
            fingerprint="b" * 64,
        ),
        raising=False,
    )

    def forbidden_side_effect(*_args: object, **_kwargs: object) -> object:
        pytest.fail("stale start reached group activation or launcher")

    monkeypatch.setattr(web_main, "prepare_group_scan_activation", forbidden_side_effect)
    monkeypatch.setattr(web_main, "build_phase1_scan_launcher", forbidden_side_effect)

    response = request(
        app,
        "POST",
        "/api/scan/jobs",
        json_body=_request_payload("a" * 64),
    )

    assert response.status_code == 409
    assert response.json() == {
        "detail": "Scanprofil-Pool hat sich geändert. Bitte neu laden und erneut prüfen."
    }
    assert response.headers["x-morphic-scan-profile-pool"] == "stale"
    assert jobs.started == []
    assert list(app.state.start_operations.root.glob("*.json")) == []


@pytest.mark.parametrize("path", ["/api/scan/preview", "/api/scan/jobs"])
@pytest.mark.parametrize(
    ("error_type", "sensitive_detail"),
    [
        (OSError, r"C:\private\profile-pool\Geheimes-Profil.json"),
        (RuntimeError, "Loaderdetail fuer Profil Geheime-Therapie"),
    ],
)
def test_pool_provider_failure_is_redacted_before_scan_side_effects(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
    path: str,
    error_type: type[Exception],
    sensitive_detail: str,
) -> None:
    jobs = FakeScanJobs()
    app = create_app(runtime_dir=tmp_path / "runtime", scan_jobs=jobs)

    def failing_provider(_level: int) -> ScanProfilePoolAuthority:
        raise error_type(sensitive_detail)

    def forbidden_side_effect(*_args: object, **_kwargs: object) -> object:
        pytest.fail("pool provider failure reached group activation or launcher")

    monkeypatch.setattr(
        web_main,
        "current_scan_profile_pool_authority",
        failing_provider,
        raising=False,
    )
    monkeypatch.setattr(web_main, "prepare_group_scan_activation", forbidden_side_effect)
    monkeypatch.setattr(web_main, "build_phase1_scan_launcher", forbidden_side_effect)

    with caplog.at_level(logging.ERROR, logger="apps.web.main"):
        response = request(
            app,
            "POST",
            path,
            json_body=_request_payload("a" * 64),
        )

    assert response.status_code == 503
    assert response.json() == {
        "detail": (
            "Scanprofil-Pool konnte nicht bestätigt werden. "
            "Bitte neu laden und erneut prüfen."
        )
    }
    assert sensitive_detail not in response.text
    assert sensitive_detail not in caplog.text
    assert error_type.__name__ in caplog.text
    assert "Traceback" not in caplog.text
    assert jobs.started == []
    assert list(app.state.start_operations.root.glob("*.json")) == []


def test_current_pool_fingerprint_allows_preview_and_one_start_without_leakage(
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    fingerprint = current_scan_profile_pool_fingerprint(3)
    jobs = FakeScanJobs()
    app = create_app(runtime_dir=tmp_path / "runtime", scan_jobs=jobs)
    payload = _request_payload(fingerprint)

    with caplog.at_level(logging.DEBUG):
        preview = request(app, "POST", "/api/scan/preview", json_body=payload)
        started = request(app, "POST", "/api/scan/jobs", json_body=payload)

    assert preview.status_code == 200
    assert started.status_code == 200
    assert len(jobs.started) == 1
    assert jobs.environments == [
        {
            SCAN_PROFILE_POOL_FINGERPRINT_ENV: fingerprint,
            "MORPHIC_EMF_AUTHORITY_PATH": str(
                app.state.emf_telemetry_authority.path
            ),
        }
    ]
    assert fingerprint not in preview.text
    assert fingerprint not in started.text
    assert SCAN_PROFILE_POOL_FINGERPRINT_ENV not in preview.text
    assert SCAN_PROFILE_POOL_FINGERPRINT_ENV not in started.text
    assert fingerprint not in jobs.started[0]
    assert fingerprint not in caplog.text
    assert SCAN_PROFILE_POOL_FINGERPRINT_ENV not in caplog.text
    assert all(
        fingerprint not in path.read_text(encoding="utf-8")
        and SCAN_PROFILE_POOL_FINGERPRINT_ENV
        not in path.read_text(encoding="utf-8")
        for path in app.state.start_operations.root.glob("*.json")
    )
    trace = app.state.workbench_store.get_run_trace(started.json()["job_id"])
    assert fingerprint not in str(trace)
    assert SCAN_PROFILE_POOL_FINGERPRINT_ENV not in str(trace)


@pytest.mark.parametrize("path", ["/api/scan/preview", "/api/scan/jobs"])
@pytest.mark.parametrize("top_n", [7, 9])
def test_level_one_top_n_above_confirmed_pool_is_422_before_side_effects(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    path: str,
    top_n: int,
) -> None:
    authority = current_scan_profile_pool_authority(1)
    assert authority.count == 5
    jobs = FakeScanJobs()
    app = create_app(runtime_dir=tmp_path / "runtime", scan_jobs=jobs)

    def forbidden_side_effect(*_args: object, **_kwargs: object) -> object:
        pytest.fail("invalid Top-N reached launcher or group activation")

    monkeypatch.setattr(web_main, "prepare_group_scan_activation", forbidden_side_effect)
    monkeypatch.setattr(web_main, "build_phase1_scan_launcher", forbidden_side_effect)

    response = request(
        app,
        "POST",
        path,
        json_body=_request_payload(
            authority.fingerprint,
            profile_level=1,
            top_n=top_n,
        ),
    )

    assert response.status_code == 422
    assert response.json() == {
        "detail": "Top-N überschreitet den bestätigten Scanprofil-Pool."
    }
    assert "x-morphic-scan-profile-pool" not in response.headers
    assert jobs.started == []
    assert list(app.state.start_operations.root.glob("*.json")) == []


@pytest.mark.parametrize("path", ["/api/scan/preview", "/api/scan/jobs"])
def test_stale_fingerprint_precedes_invalid_top_n(
    tmp_path: Path,
    path: str,
) -> None:
    authority = current_scan_profile_pool_authority(1)
    jobs = FakeScanJobs()
    app = create_app(runtime_dir=tmp_path / "runtime", scan_jobs=jobs)

    response = request(
        app,
        "POST",
        path,
        json_body=_request_payload(
            "f" * 64,
            profile_level=1,
            top_n=9,
        ),
    )

    assert authority.fingerprint != "f" * 64
    assert response.status_code == 409
    assert response.json() == {
        "detail": "Scanprofil-Pool hat sich geändert. Bitte neu laden und erneut prüfen."
    }
    assert response.headers["x-morphic-scan-profile-pool"] == "stale"
    assert jobs.started == []
    assert list(app.state.start_operations.root.glob("*.json")) == []


def test_group_activation_environment_merges_without_overwriting_confirmed_fingerprint(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    authority = current_scan_profile_pool_authority(3)
    jobs = FakeScanJobs()
    runtime_dir = tmp_path / "runtime"
    app = create_app(runtime_dir=runtime_dir, scan_jobs=jobs)
    activation = {
        "MORPHIC_GROUP_ACTIVATION_RUNTIME": "1",
        "MORPHIC_GROUP_ACTIVATION_HANDLE": "gah-private",
        SCAN_PROFILE_POOL_FINGERPRINT_ENV: "0" * 64,
    }
    monkeypatch.setattr(
        web_main,
        "prepare_group_scan_activation",
        lambda *_args, **_kwargs: dict(activation),
    )

    response = request(
        app,
        "POST",
        "/api/scan/jobs",
        json_body=_request_payload(authority.fingerprint),
    )

    assert response.status_code == 200
    assert jobs.environments == [{
        "MORPHIC_GROUP_ACTIVATION_RUNTIME": "1",
        "MORPHIC_GROUP_ACTIVATION_HANDLE": "gah-private",
        "MORPHIC_RUNTIME_DIR": str(runtime_dir),
        SCAN_PROFILE_POOL_FINGERPRINT_ENV: authority.fingerprint,
        "MORPHIC_EMF_AUTHORITY_PATH": str(
            app.state.emf_telemetry_authority.path
        ),
    }]
    assert authority.fingerprint not in response.text
    assert authority.fingerprint not in str(jobs.started)
