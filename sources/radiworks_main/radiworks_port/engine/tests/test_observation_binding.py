"""Strict identity bindings for rates promoted from a pinned analysis session."""

from __future__ import annotations

import copy
import importlib
import inspect
from dataclasses import FrozenInstanceError

import pytest

from radiworks.scope import ScopeContext


SCOPE = ScopeContext(tenant_id="tenant-a", client_id="client-a", job_id="job-a")
CASE_REF = "a" * 64
SESSION_ID = "b" * 32
DRAFT_ID = "12345678-1234-4234-8234-123456789abc"
ANALYSIS_DIGEST = "c" * 64


def _api():
    try:
        return importlib.import_module("radiworks.core.observation_binding")
    except ModuleNotFoundError as error:
        if error.name == "radiworks.core.observation_binding":
            pytest.fail("observation_binding helper has not been implemented", pytrace=False)
        raise


def _rate(name: str, gv: int, energetic_value: int) -> dict:
    return {
        "nameOrRate": name,
        "gv": gv,
        "energeticValue": energetic_value,
        "potency": None,
    }


def _documents() -> tuple[dict, dict, ScopeContext, str]:
    analysis = {
        "generalVitality": 4,
        "rateObjects": [
            _rate("Duplicate", 3, 90),
            _rate("Duplicate", 7, 10),
            _rate("Third", 9, 20),
        ],
    }
    draft = {
        "id": DRAFT_ID,
        "scope": SCOPE.to_dict(),
        "sessionId": SESSION_ID,
        "sessionRevision": 2,
        "payload": copy.deepcopy(analysis),
    }
    case = {
        "name": "Private Case Name",
        "scope": SCOPE.to_dict(),
        "sessionList": [
            {
                "sessionId": SESSION_ID,
                "draftId": DRAFT_ID,
                "revision": 2,
                "analysisResult": copy.deepcopy(analysis),
            }
        ],
    }
    return draft, case, SCOPE, CASE_REF


def _binding(**changes):
    values = {
        "scope": SCOPE,
        "case_ref": CASE_REF,
        "session_id": SESSION_ID,
        "draft_id": DRAFT_ID,
        "session_revision": 2,
        "rate_index": 3,
        "analysis_digest": ANALYSIS_DIGEST,
    }
    values.update(changes)
    return _api().ObservationBinding(**values)


def _bind(draft, case, *, scope, case_ref, source_case_ref):
    binder = _api().bind_promoted_rates
    if "source_case_ref" not in inspect.signature(binder).parameters:
        pytest.fail("bind_promoted_rates has no independent source_case_ref", pytrace=False)
    return binder(
        draft,
        case,
        scope=scope,
        case_ref=case_ref,
        source_case_ref=source_case_ref,
    )


def test_payload_round_trip_has_exact_camel_case_contract_and_detached_scope():
    binding = _binding()

    payload = binding.payload()

    assert set(payload) == {
        "schemaVersion", "scope", "caseRef", "sessionId", "draftId",
        "sessionRevision", "rateIndex", "analysisDigest",
    }
    assert payload == {
        "schemaVersion": 1,
        "scope": SCOPE.to_dict(),
        "caseRef": CASE_REF,
        "sessionId": SESSION_ID,
        "draftId": DRAFT_ID,
        "sessionRevision": 2,
        "rateIndex": 3,
        "analysisDigest": ANALYSIS_DIGEST,
    }
    restored = _api().ObservationBinding.from_payload(payload)
    assert restored == binding

    payload["scope"]["tenant_id"] = "changed"
    assert binding.scope == SCOPE
    assert restored.scope == SCOPE


def test_observation_binding_is_frozen():
    binding = _binding()

    with pytest.raises(FrozenInstanceError):
        binding.rate_index = 8


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("case_ref", "not-64-hex"),
        ("case_ref", "A" * 64),
        ("session_id", "not-32-hex"),
        ("session_id", "B" * 32),
        ("draft_id", "12345678-1234-4234-8234-123456789ABC"),
        ("draft_id", "not-a-uuid"),
        ("session_revision", -1),
        ("session_revision", True),
        ("session_revision", 1.5),
        ("rate_index", -1),
        ("rate_index", False),
        ("rate_index", 1.0),
        ("analysis_digest", "not-64-hex"),
        ("analysis_digest", "D" * 64),
    ],
)
def test_constructor_rejects_noncanonical_or_wrongly_typed_identity_fields(field, value):
    with pytest.raises((TypeError, ValueError)):
        _binding(**{field: value})


@pytest.mark.parametrize(
    "mutate",
    [
        lambda payload: payload.update(extra="unknown"),
        lambda payload: payload.pop("rateIndex"),
        lambda payload: payload.update(schemaVersion=True),
        lambda payload: payload.update(schemaVersion=2),
        lambda payload: payload.update(sessionRevision=True),
        lambda payload: payload.update(rateIndex="3"),
        lambda payload: payload["scope"].update(extra="unknown"),
        lambda payload: payload["scope"].pop("job_id"),
    ],
)
def test_from_payload_rejects_unknown_missing_or_wrongly_typed_fields(mutate):
    payload = _binding().payload()
    mutate(payload)

    with pytest.raises((TypeError, ValueError)):
        _api().ObservationBinding.from_payload(payload)


def test_bind_promoted_rates_uses_every_original_rate_index_and_pinned_digest():
    from radiworks.persistence import document_digest

    draft, case, scope, case_ref = _documents()
    before_draft = copy.deepcopy(draft)
    before_case = copy.deepcopy(case)

    bindings = _bind(
        draft, case, scope=scope, case_ref=case_ref, source_case_ref=CASE_REF
    )

    assert list(bindings) == [0, 1, 2]
    assert [binding.rate_index for binding in bindings.values()] == [0, 1, 2]
    assert {binding.analysis_digest for binding in bindings.values()} == {
        document_digest(case["sessionList"][0]["analysisResult"])
    }
    assert all(binding.scope == scope for binding in bindings.values())
    assert all(binding.case_ref == case_ref for binding in bindings.values())
    assert all(binding.session_id == SESSION_ID for binding in bindings.values())
    assert all(binding.draft_id == DRAFT_ID for binding in bindings.values())
    assert all(binding.session_revision == 2 for binding in bindings.values())
    assert "Private Case Name" not in repr([binding.payload() for binding in bindings.values()])
    assert draft == before_draft
    assert case == before_case


def test_bind_promoted_rates_does_not_infer_session_from_current_selection():
    draft, case, scope, case_ref = _documents()
    draft.pop("sessionId")
    case["selectedSessionId"] = SESSION_ID

    assert _bind(
        draft, case, scope=scope, case_ref=case_ref, source_case_ref=CASE_REF
    ) == {}


def test_bind_promoted_rates_requires_explicit_source_case_reference():
    draft, case, scope, case_ref = _documents()
    case["sourceCaseRef"] = CASE_REF

    assert _bind(
        draft, case, scope=scope, case_ref=case_ref, source_case_ref=None
    ) == {}


def test_bind_promoted_rates_rejects_source_reference_for_another_case():
    draft, case, scope, case_ref = _documents()

    assert _bind(
        draft, case, scope=scope, case_ref=case_ref, source_case_ref="d" * 64
    ) == {}


def test_bind_promoted_rates_rejects_malformed_source_case_reference():
    draft, case, scope, case_ref = _documents()

    assert _bind(
        draft, case, scope=scope, case_ref=case_ref, source_case_ref="not-a-reference"
    ) == {}


def test_bind_promoted_rates_rejects_copied_session_in_another_case():
    draft, case_b, scope, source_case_ref = _documents()
    case_b["name"] = "Different Current Case"
    current_case_ref = "e" * 64

    assert _bind(
        draft,
        case_b,
        scope=scope,
        case_ref=current_case_ref,
        source_case_ref=source_case_ref,
    ) == {}


@pytest.mark.parametrize(
    "invalidate",
    [
        lambda draft, case: (draft, None),
        lambda draft, case: (None, case),
        lambda draft, case: ({**draft, "sessionId": None}, case),
        lambda draft, case: ({**draft, "sessionId": "bad"}, case),
        lambda draft, case: ({**draft, "id": "bad"}, case),
        lambda draft, case: ({**draft, "sessionRevision": True}, case),
        lambda draft, case: ({**draft, "sessionRevision": 3}, case),
        lambda draft, case: ({**draft, "payload": {"different": True}}, case),
        lambda draft, case: (draft, {**case, "scope": {**SCOPE.to_dict(), "job_id": "other"}}),
        lambda draft, case: ({**draft, "scope": {**SCOPE.to_dict(), "job_id": "other"}}, case),
        lambda draft, case: (draft, {**case, "sessionList": []}),
        lambda draft, case: (
            draft,
            {**case, "sessionList": case["sessionList"] + copy.deepcopy(case["sessionList"])},
        ),
        lambda draft, case: (
            draft,
            {**case, "sessionList": [{**case["sessionList"][0], "draftId": "other"}]},
        ),
        lambda draft, case: (
            draft,
            {**case, "sessionList": [{**case["sessionList"][0], "revision": 1}]},
        ),
        lambda draft, case: (draft, {**case, "sessionList": "malformed"}),
        lambda draft, case: ({**draft, "sessionId": "d" * 32}, case),
    ],
)
def test_bind_promoted_rates_fails_closed_for_unbound_or_stale_session(invalidate):
    draft, case, scope, case_ref = _documents()
    draft, case = invalidate(draft, case)

    assert _bind(
        draft, case, scope=scope, case_ref=case_ref, source_case_ref=CASE_REF
    ) == {}


@pytest.mark.parametrize(
    "rates",
    [
        "not-a-list",
        ["not-a-rate"],
        [{"nameOrRate": "missing energy"}],
        [{"nameOrRate": 4, "energeticValue": 2}],
        [{"nameOrRate": "bad gv", "energeticValue": 2, "gv": True}],
        [_rate("valid", 3, 4), {"nameOrRate": "malformed"}],
    ],
)
def test_bind_promoted_rates_fails_closed_for_malformed_rate_arrays(rates):
    draft, case, scope, case_ref = _documents()
    draft["payload"]["rateObjects"] = rates
    case["sessionList"][0]["analysisResult"] = copy.deepcopy(draft["payload"])

    assert _bind(
        draft, case, scope=scope, case_ref=case_ref, source_case_ref=CASE_REF
    ) == {}


def test_bind_promoted_rates_fails_closed_for_invalid_server_case_reference():
    draft, case, scope, _ = _documents()

    assert _bind(
        draft,
        case,
        scope=scope,
        case_ref="private case name",
        source_case_ref=CASE_REF,
    ) == {}
