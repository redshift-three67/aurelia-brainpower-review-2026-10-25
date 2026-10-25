from pydantic import ValidationError

from apps.web.client_context_contracts import (
    GeoContextDraft,
    GroupContextDraft,
    LocalVectorDraftEnvelope,
)
from apps.web.contracts import Phase1ScanRequest


def test_group_draft_is_local_opt_in_and_exposes_only_a_pseudonymous_summary() -> None:
    draft = GroupContextDraft(
        group_label="Testgruppe Morgenkreis",
        members=[
            {"client_id": "cli-alpha", "consent_recorded": True},
            {"client_id": "cli-beta", "consent_recorded": True},
        ],
        persistence_consent=True,
        retention_days=30,
    )

    assert draft.safe_summary() == {
        "schema_version": 1,
        "vector": "group",
        "persistence": "local_opt_in",
        "retention_days": 30,
        "member_count": 2,
        "analysis_enabled": False,
    }


def test_group_draft_rejects_member_without_explicit_consent() -> None:
    try:
        GroupContextDraft(
            group_label="Testgruppe",
            members=[{"client_id": "cli-alpha", "consent_recorded": False}],
            persistence_consent=True,
            retention_days=30,
        )
    except ValidationError as exc:
        assert "consent_recorded" in str(exc)
    else:
        raise AssertionError("expected ValidationError")


def test_geo_draft_is_manual_local_opt_in_and_redacts_coordinates_from_summary() -> None:
    draft = GeoContextDraft(
        latitude=47.3769,
        longitude=8.5417,
        radius_meters=500,
        coordinate_precision="coarse",
        source="manual",
        persistence_consent=True,
        retention_days=14,
    )

    assert draft.safe_summary() == {
        "schema_version": 1,
        "vector": "geo",
        "persistence": "local_opt_in",
        "source": "manual",
        "coordinate_precision": "coarse",
        "retention_days": 14,
        "analysis_enabled": False,
    }


def test_geo_draft_rejects_browser_source_unknown_fields_and_invalid_retention() -> None:
    for payload in (
        {
            "latitude": 47.0,
            "longitude": 8.0,
            "radius_meters": 10,
            "coordinate_precision": "coarse",
            "source": "browser",
            "persistence_consent": True,
            "retention_days": 30,
        },
        {
            "latitude": 47.0,
            "longitude": 8.0,
            "radius_meters": 10,
            "coordinate_precision": "coarse",
            "source": "manual",
            "persistence_consent": True,
            "retention_days": 30,
            "unexpected": "must not be accepted",
        },
        {
            "latitude": 47.0,
            "longitude": 8.0,
            "radius_meters": 10,
            "coordinate_precision": "coarse",
            "source": "manual",
            "persistence_consent": True,
            "retention_days": 0,
        },
    ):
        try:
            GeoContextDraft(**payload)
        except ValidationError:
            pass
        else:
            raise AssertionError("expected ValidationError")


def test_local_vector_envelope_is_not_a_phase1_scan_input_and_summary_has_no_cleartext() -> None:
    envelope = LocalVectorDraftEnvelope(
        group={
            "group_label": "Testgruppe Morgenkreis",
            "members": [{"client_id": "cli-alpha", "consent_recorded": True}],
            "persistence_consent": True,
            "retention_days": 30,
        },
        geo={
            "latitude": 47.3769,
            "longitude": 8.5417,
            "radius_meters": 500,
            "coordinate_precision": "coarse",
            "source": "manual",
            "persistence_consent": True,
            "retention_days": 14,
        },
    )

    assert envelope.safe_summary() == {
        "schema_version": 1,
        "vectors": [
            {
                "schema_version": 1,
                "vector": "group",
                "persistence": "local_opt_in",
                "retention_days": 30,
                "member_count": 1,
                "analysis_enabled": False,
            },
            {
                "schema_version": 1,
                "vector": "geo",
                "persistence": "local_opt_in",
                "source": "manual",
                "coordinate_precision": "coarse",
                "retention_days": 14,
                "analysis_enabled": False,
            },
        ],
    }
    assert {"group", "geo", "group_members", "latitude", "longitude", "radius"}.isdisjoint(
        Phase1ScanRequest.model_fields
    )
    assert "Morgenkreis" not in str(envelope.safe_summary())
    assert "47.3769" not in str(envelope.safe_summary())
