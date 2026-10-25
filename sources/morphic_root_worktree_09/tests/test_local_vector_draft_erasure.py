from datetime import UTC, datetime
from pathlib import Path

from apps.web.client_context_contracts import LocalVectorDraftEnvelope
from core.compliance.local_vector_draft_store import LocalVectorDraftStore


def _draft() -> LocalVectorDraftEnvelope:
    return LocalVectorDraftEnvelope(
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


def test_erasure_dry_run_reports_expired_local_vector_draft_without_mutation(tmp_path: Path) -> None:
    store = LocalVectorDraftStore(tmp_path / "local-vector-drafts")
    stored_at = datetime(2026, 1, 1, tzinfo=UTC)
    store.save("draft-001", _draft(), stored_at=stored_at)

    plan = store.erasure_dry_run(now=datetime(2026, 1, 15, tzinfo=UTC))

    assert plan == [
        {
            "draft_id": "draft-001",
            "reason": "retention_expired",
            "stored_at": "2026-01-01T00:00:00Z",
            "expires_at": "2026-01-15T00:00:00Z",
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
    ]
    assert store.load("draft-001") == _draft()


def test_erasure_dry_run_uses_strictest_vector_retention_and_ignores_fresh_drafts(
    tmp_path: Path,
) -> None:
    store = LocalVectorDraftStore(tmp_path / "local-vector-drafts")
    store.save("draft-001", _draft(), stored_at=datetime(2026, 1, 1, tzinfo=UTC))

    assert store.erasure_dry_run(now=datetime(2026, 1, 14, 23, 59, 59, tzinfo=UTC)) == []
