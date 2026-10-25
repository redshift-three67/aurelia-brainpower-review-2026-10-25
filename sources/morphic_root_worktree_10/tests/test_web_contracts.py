from pydantic import ValidationError

from apps.web.contracts import Phase1ScanRequest


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
        "image_path": "/tmp/client.png",
        "adaptive_limits": True,
        "consent_local": True,
        "consent_safety": True,
    }
    payload.update(overrides)
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
    assert request.image_path == "/tmp/client.png"
    assert request.adaptive_limits is True


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
