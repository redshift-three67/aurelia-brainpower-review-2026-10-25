import pytest
from pydantic import ValidationError

from apps.web.contracts import (
    HarmonizationRequest,
    Phase1ScanRequest,
    WorkbenchTemplateRequest,
)
from apps.web.workbench import current_scan_profile_pool_fingerprint


def valid_payload(**overrides):
    payload = {
        "last_name": "Deisenhofer",
        "first_name": "Klaus",
        "birth_date": "09041966",
        "birth_place": "Augsburg",
        "focus": "Bronchien",
        "profile_level": 3,
        "top_n": 7,
        "profile_template": "phase1-default",
        "entropy_mode": "hybrid",
        "image_path": "/tmp/client.jpg",
        "adaptive_limits": True,
        "consent_local": True,
        "consent_safety": True,
    }
    payload.update(overrides)
    payload.setdefault(
        "scan_profile_pool_fingerprint",
        current_scan_profile_pool_fingerprint(payload["profile_level"]),
    )
    return payload


def test_phase1_scan_request_accepts_supported_phase1_fields() -> None:
    request = Phase1ScanRequest(**valid_payload())

    assert request.last_name == "Deisenhofer"
    assert request.first_name == "Klaus"
    assert request.birth_date == "09041966"
    assert request.birth_place == "Augsburg"
    assert request.focus == "Bronchien"
    assert request.profile_level == 3
    assert request.top_n == 7
    assert request.profile_template == "phase1-default"
    assert request.entropy_mode == "hybrid"
    assert request.image_path == "/tmp/client.jpg"
    assert request.adaptive_limits is True


def test_phase1_scan_request_defaults_local_ai_enabled_to_false() -> None:
    request = Phase1ScanRequest(**valid_payload())

    assert request.local_ai_enabled is False


def test_phase1_scan_request_accepts_explicit_local_ai_enabled_true() -> None:
    request = Phase1ScanRequest(**valid_payload(local_ai_enabled=True))

    assert request.local_ai_enabled is True


@pytest.mark.parametrize("value", [1, 0, "true", "false", None])
def test_phase1_scan_request_rejects_non_boolean_local_ai_enabled(value: object) -> None:
    with pytest.raises(ValidationError):
        Phase1ScanRequest(**valid_payload(local_ai_enabled=value))


def test_phase1_scan_request_accepts_expert_workbench_mode() -> None:
    request = Phase1ScanRequest(**valid_payload(workbench_mode="expert"))

    assert request.workbench_mode == "expert"


def test_phase1_scan_request_accepts_jpeg_extension() -> None:
    request = Phase1ScanRequest(**valid_payload(image_path="/tmp/client.jpeg"))

    assert request.image_path == "/tmp/client.jpeg"


def test_phase1_scan_request_accepts_none_image_path() -> None:
    request = Phase1ScanRequest(**valid_payload(image_path=None))

    assert request.image_path is None


def test_phase1_scan_request_rejects_non_jpg_image_path() -> None:
    try:
        Phase1ScanRequest(**valid_payload(image_path="/tmp/client.png"))
    except ValidationError as exc:
        assert "image_path must be a .jpg/.jpeg file" in str(exc)
    else:
        raise AssertionError("expected ValidationError")


def test_phase1_scan_request_trims_optional_context_fields() -> None:
    request = Phase1ScanRequest(
        **valid_payload(main_symptom="  Atemdruck  ", notes="  morgens staerker  ")
    )

    assert request.main_symptom == "Atemdruck"
    assert request.notes == "morgens staerker"


def test_phase1_scan_request_rejects_unsupported_topn() -> None:
    try:
        Phase1ScanRequest(**valid_payload(top_n=4))
    except ValidationError as exc:
        assert "top_n must be one of 3, 5, 7 or 9" in str(exc)
    else:
        raise AssertionError("expected ValidationError")


def test_phase1_scan_request_rejects_invalid_profile_level() -> None:
    try:
        Phase1ScanRequest(**valid_payload(profile_level=5))
    except ValidationError as exc:
        assert "profile_level must be one of 1, 2, 3 or 4" in str(exc)
    else:
        raise AssertionError("expected ValidationError")


def test_phase1_scan_request_rejects_unsupported_entropy_mode() -> None:
    try:
        Phase1ScanRequest(**valid_payload(entropy_mode="future"))
    except ValidationError as exc:
        assert "entropy_mode must be one of legacy, enhanced or hybrid" in str(exc)
    else:
        raise AssertionError("expected ValidationError")


def test_phase1_scan_request_rejects_unknown_workbench_mode() -> None:
    try:
        Phase1ScanRequest(**valid_payload(workbench_mode="future"))
    except ValidationError as exc:
        assert "workbench_mode must be one of standard or expert" in str(exc)
    else:
        raise AssertionError("expected ValidationError")


def test_phase1_scan_request_rejects_blank_required_text_fields() -> None:
    try:
        Phase1ScanRequest(**valid_payload(last_name=" "))
    except ValidationError as exc:
        assert "last_name must not be blank" in str(exc)
    else:
        raise AssertionError("expected ValidationError")


def test_phase1_scan_request_rejects_invalid_birth_date_format() -> None:
    try:
        Phase1ScanRequest(**valid_payload(birth_date="09/04/1966"))
    except ValidationError as exc:
        assert "birth_date must use DDMMYYYY format" in str(exc)
    else:
        raise AssertionError("expected ValidationError")


def test_phase1_scan_request_rejects_impossible_calendar_birth_date() -> None:
    for value in ("31022024", "00000000"):
        try:
            Phase1ScanRequest(**valid_payload(birth_date=value))
        except ValidationError as exc:
            assert "birth_date must be a valid calendar date" in str(exc)
        else:
            raise AssertionError(f"expected ValidationError for {value}")


def test_phase1_scan_request_accepts_valid_leap_day() -> None:
    request = Phase1ScanRequest(**valid_payload(birth_date="29022024"))

    assert request.birth_date == "29022024"


def test_phase1_scan_request_requires_consent_flags() -> None:
    try:
        Phase1ScanRequest(**valid_payload(consent_local=False))
    except ValidationError as exc:
        assert "consent_local must be accepted" in str(exc)
    else:
        raise AssertionError("expected ValidationError")


def test_phase1_scan_request_requires_consent_fields_present() -> None:
    try:
        payload = valid_payload()
        payload.pop("consent_local")
        Phase1ScanRequest(**payload)
    except ValidationError as exc:
        assert "consent_local" in str(exc)
    else:
        raise AssertionError("expected ValidationError")


def test_harmonization_request_accepts_report_binding_and_workbench_mode() -> None:
    request = HarmonizationRequest(
        target_frequency=432.0,
        report_id="rep-123",
        workbench_mode="expert",
    )

    assert request.report_id == "rep-123"
    assert request.workbench_mode == "expert"


def test_harmonization_request_accepts_pulse_pause_duration_solfeggio() -> None:
    request = HarmonizationRequest(
        report_id="rep-test",
        target_frequency=432.0,
        pulse_seconds=4,
        pause_seconds=1,
        duration_factor=7,
    )

    assert request.pulse_seconds == 4
    assert request.pause_seconds == 1
    assert request.duration_factor == 7



def test_harmonization_request_pulse_pause_defaults_are_backwards_compatible() -> None:
    request = HarmonizationRequest(report_id="rep-test", target_frequency=432.0)

    assert request.pulse_seconds == 3.0
    assert request.pause_seconds == 2.0
    assert request.duration_factor == 1


def test_harmonization_request_rejects_unbounded_duration_factor() -> None:
    try:
        HarmonizationRequest(
            report_id="rep-test",
            target_frequency=432.0,
            duration_factor=22,
        )
    except ValidationError as exc:
        assert "duration_factor" in str(exc)
    else:
        raise AssertionError("expected ValidationError")



def test_harmonization_request_rejects_truly_unknown_extra_fields() -> None:
    try:
        HarmonizationRequest(completely_unknown_field="should_fail")
    except ValidationError as exc:
        assert "completely_unknown_field" in str(exc).lower() or "extra" in str(exc).lower()
    else:
        raise AssertionError("expected ValidationError")


def test_workbench_template_request_requires_non_empty_name() -> None:
    try:
        WorkbenchTemplateRequest(name=" ")
    except ValidationError as exc:
        assert "name must not be blank" in str(exc)
    else:
        raise AssertionError("expected ValidationError")
