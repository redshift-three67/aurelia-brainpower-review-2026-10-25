"""Synthetic, deterministic tests for the approved EXP1-B scalar input preparation."""
import copy
import hashlib

import pytest

from radiworks.core.experimental_context import (
    ExperimentalContextError,
    FORMULA_VERSION,
    SOURCE_SHA256,
    prepare_experimental_context,
)
from radiworks.core.personal_context import ContextSnapshot, prepare_identity


DATE = "1980-02-29"
SOURCE_HASH = "3146960a23041cca959befd85882888fc3f896fe3b9a4eb83916b85aec859894"


def make_snapshot(*, focus="Pflanzen", **personal_fields):
    case = {
        "caseId": "a" * 32,
        "name": "Synthetic",
        "description": "Synthetic fixture",
        "focus": focus,
        "personalContext": personal_fields,
    }
    prepare_identity(case)
    return ContextSnapshot.capture(case, None)


def reference_name_frequency(first_name, last_names):
    """Test oracle copied from Radi144 client_signature.py (pinned SHA above)."""
    full_name = f"{first_name} {' '.join(last_names)}"
    text = full_name.lower()
    numerology = sum(ord(char) for char in text if char.isalpha())
    vowels = {"a": 440, "e": 330, "i": 550, "o": 220, "u": 165}
    phonetic = sum(
        vowels[char] if char in vowels else ord(char) * 2.0 if char.isalpha() else 0.0
        for char in text
    )
    return ((numerology + phonetic) / 2.0) % 1000.0


def reference_birth_frequency(birth_date, birth_place=None):
    """Pinned JDN, place MD5 and 0.6/0.3 coefficients; birth time is omitted."""
    year, month, day = (int(part) for part in birth_date.split("-"))
    a = (14 - month) // 12
    y = year + 4800 - a
    m = month + 12 * a - 3
    jdn = day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045
    base = float(jdn) % 1000.0
    place_mod = 0.0
    if birth_place:
        place_hash = hashlib.md5(birth_place.lower().strip().encode()).hexdigest()
        place_mod = int(place_hash[:4], 16) / 65.535
    return (base * 0.6 + place_mod * 0.3) % 1000.0


def test_name_and_birth_components_match_pinned_reference_formulas():
    snapshot = make_snapshot(
        firstName="Zoë",
        lastName="Müller",
        birthDate=DATE,
        place="Berlin",
        placeKind="birth",
    )

    prepared = prepare_experimental_context(snapshot)
    expected_name = reference_name_frequency("Zoë", ["Müller"])
    expected_birth = reference_birth_frequency(DATE, "Berlin")

    assert prepared["signature"]["components"] == {
        "name": pytest.approx(expected_name),
        "birth": pytest.approx(expected_birth),
    }
    assert prepared["signature"]["weights"] == {"name": 0.15, "birth": 0.20}
    assert prepared["signature"]["frequency"] == pytest.approx(
        (expected_name * 0.15 + expected_birth * 0.20) / 0.35
    )
    assert prepared["placeUse"] == "birth-scalar"


def test_name_only_and_date_only_normalize_over_available_weights():
    name_snapshot = make_snapshot(lastName="Müller")
    name_result = prepare_experimental_context(name_snapshot)
    expected_name = reference_name_frequency("", ["Müller"])
    assert name_result["signature"]["components"] == {"name": pytest.approx(expected_name)}
    assert name_result["signature"]["weights"] == {"name": 0.15}
    assert name_result["signature"]["frequency"] == pytest.approx(expected_name)

    date_snapshot = make_snapshot(birthDate=DATE)
    date_result = prepare_experimental_context(date_snapshot)
    expected_birth = reference_birth_frequency(DATE)
    assert date_result["signature"]["components"] == {"birth": pytest.approx(expected_birth)}
    assert date_result["signature"]["weights"] == {"birth": 0.20}
    assert date_result["signature"]["frequency"] == pytest.approx(expected_birth)
    assert date_result["parameters"]["birthTimeMultiplier"] == 0.0


def test_only_explicit_birth_place_changes_birth_scalar():
    birth_without_place = prepare_experimental_context(
        make_snapshot(birthDate=DATE, placeKind="birth", place=None)
    )
    birth_with_place = prepare_experimental_context(
        make_snapshot(birthDate=DATE, placeKind="birth", place="Berlin")
    )
    residence_place = prepare_experimental_context(
        make_snapshot(birthDate=DATE, placeKind="residence", place="Berlin")
    )
    legacy_untyped_place = prepare_experimental_context(
        make_snapshot(birthDate=DATE, place="Berlin")
    )

    expected = reference_birth_frequency(DATE)
    assert birth_without_place["signature"]["components"]["birth"] == pytest.approx(expected)
    assert birth_with_place["signature"]["components"]["birth"] == pytest.approx(
        reference_birth_frequency(DATE, "Berlin")
    )
    assert birth_with_place["signature"]["components"]["birth"] != pytest.approx(expected)
    assert residence_place["signature"]["components"]["birth"] == pytest.approx(expected)
    assert legacy_untyped_place["signature"]["components"]["birth"] == pytest.approx(expected)
    assert birth_with_place["placeUse"] == "birth-scalar"
    assert residence_place["placeUse"] == "context-only"
    assert legacy_untyped_place["placeUse"] == "context-only"


def test_image_and_focus_remain_context_only():
    plain = prepare_experimental_context(make_snapshot(firstName="Lina"))
    enriched = prepare_experimental_context(
        make_snapshot(
            firstName="Lina",
            focus="Mineralien",
            image={
                "sha256": "b" * 64,
                "mediaType": "image/png",
                "byteLength": 12,
            },
        )
    )

    assert enriched["signature"] == plain["signature"]
    assert enriched["imageUse"] == "context-only"
    assert enriched["focusUse"] == "requires-catalog-match"
    assert enriched["contextDigest"] != plain["contextDigest"]


def test_output_is_deterministic_and_binds_snapshot_source_and_parameters():
    snapshot = make_snapshot(firstName="Ada", birthDate=DATE)
    payload = snapshot.payload()

    first = prepare_experimental_context(snapshot)
    second = prepare_experimental_context(ContextSnapshot.from_payload(copy.deepcopy(payload)))

    assert first == second
    assert first["formulaVersion"] == FORMULA_VERSION
    assert first["sourceHashes"] == {
        "Radi144/app/algorithms/client_signature.py": SOURCE_HASH
    }
    assert first["contextDigest"] == payload["digest"]
    assert first["contextVersion"] == payload["contextVersion"]
    assert first["caseId"] == payload["caseId"]
    assert first["imageUse"] == "not-provided"
    assert first["parameters"]["nameWeight"] == 0.15
    assert first["parameters"]["birthWeight"] == 0.20
    assert first["parameters"]["birthBaseMultiplier"] == 0.6
    assert first["parameters"]["birthPlaceMultiplier"] == 0.3
    assert first["parameters"]["birthPlaceDivisor"] == 65.535
    assert first["parameters"]["organClockEnabled"] is False
    assert first["parameters"]["planetaryEnabled"] is False
    assert first["parameters"]["emfEnabled"] is False
    assert first["parameters"]["hrvEnabled"] is False
    assert first["parameters"]["imageSignatureEnabled"] is False
    assert first["parameters"]["focusVectorizationEnabled"] is False
    assert "timestamp" not in first


def test_invalid_or_tampered_snapshot_is_a_controlled_error():
    snapshot = make_snapshot(firstName="Ada")
    bad_payload = snapshot.payload()
    bad_payload["context"]["personal"]["firstName"] = "Changed without digest update"

    with pytest.raises(ExperimentalContextError):
        prepare_experimental_context(bad_payload)

    with pytest.raises(ExperimentalContextError):
        prepare_experimental_context({"not": "a snapshot"})


def test_context_only_fields_cannot_replace_name_or_birth_scalar():
    snapshot = make_snapshot(
        place="Berlin",
        image={
            "sha256": "c" * 64,
            "mediaType": "image/jpeg",
            "byteLength": 8,
        },
    )

    with pytest.raises(ExperimentalContextError):
        prepare_experimental_context(snapshot)



def test_birthplace_without_birthdate_is_not_reported_as_scalar():
    result=prepare_experimental_context(make_snapshot(firstName='Synthetic',place='Berlin',placeKind='birth'))
    assert set(result['signature']['components'])=={'name'}
    assert result['placeUse']=='context-only'


def test_preparation_of_saved_snapshot_never_reads_current_date(monkeypatch):
    import radiworks.core.personal_context as context_module
    from datetime import date
    payload=make_snapshot(firstName='Synthetic',birthDate=DATE).payload()
    expected=prepare_experimental_context(payload)
    class NoClockDate(date):
        @classmethod
        def today(cls):
            raise AssertionError('snapshot revalidation must not read clock')
    monkeypatch.setattr(context_module,'date',NoClockDate)
    assert prepare_experimental_context(payload)==expected


def test_new_input_future_guard_remains_strict(monkeypatch):
    import radiworks.core.personal_context as context_module
    from datetime import date
    class EarlierDate(date):
        @classmethod
        def today(cls): return cls(1970,1,1)
    monkeypatch.setattr(context_module,'date',EarlierDate)
    with pytest.raises(context_module.ContextError):
        context_module.normalize_personal({'birthDate':DATE})


@pytest.mark.parametrize('birth_date,accepted',[('1980-02-29',True),('1980-03-01',False)])
def test_snapshot_utc_calendar_tolerance_is_bounded(birth_date,accepted):
    from radiworks.persistence import document_digest
    from radiworks.core.personal_context import ContextError
    payload=make_snapshot(birthDate=birth_date).payload()
    payload['capturedAt']='1980-02-28T23:30:00+00:00'
    payload['digest']=document_digest({k:v for k,v in payload.items() if k!='digest'})
    if accepted: assert ContextSnapshot.from_payload(payload).payload()==payload
    else:
        with pytest.raises(ContextError): ContextSnapshot.from_payload(payload)


def test_snapshot_extreme_timezone_is_controlled_error():
    from radiworks.persistence import document_digest
    from radiworks.core.personal_context import ContextError
    payload=make_snapshot(firstName='Synthetic').payload()
    payload['capturedAt']='0001-01-01T00:00:00+14:00'
    payload['digest']=document_digest({k:v for k,v in payload.items() if k!='digest'})
    with pytest.raises(ContextError): ContextSnapshot.from_payload(payload)
