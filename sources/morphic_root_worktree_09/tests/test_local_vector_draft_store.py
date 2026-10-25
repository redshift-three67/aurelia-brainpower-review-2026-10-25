from pathlib import Path

import pytest

from apps.web.client_context_contracts import LocalVectorDraftEnvelope
from core.compliance.local_vector_draft_store import LocalVectorDraftStore


def test_local_vector_writer_uses_shared_durable_parent_helper(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from core.compliance import local_vector_draft_store as draft_store_module

    calls: list[Path] = []

    def parent(path: Path, *, mode: int = 0o777) -> None:
        calls.append(Path(path))
        Path(path).mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(
        draft_store_module,
        "durable_mkdir_parents",
        parent,
        raising=False,
    )
    store = LocalVectorDraftStore(tmp_path / "nested" / "drafts")

    store.save("draft-parent", _draft())

    assert calls == [store.root]


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


def test_local_vector_draft_store_roundtrips_dpapi_payload_without_cleartext_at_rest(
    tmp_path: Path,
) -> None:
    store = LocalVectorDraftStore(tmp_path / "local-vector-drafts")

    stored = store.save("draft-001", _draft())
    encrypted = (tmp_path / "local-vector-drafts" / "draft-001.dpapi").read_bytes()

    assert stored == {
        "draft_id": "draft-001",
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
    assert b"Morgenkreis" not in encrypted
    assert b"47.3769" not in encrypted
    assert store.load("draft-001") == _draft()


def test_local_vector_draft_store_lists_safe_metadata_and_requires_exact_delete_confirmation(
    tmp_path: Path,
) -> None:
    store = LocalVectorDraftStore(tmp_path / "local-vector-drafts")
    store.save("draft-001", _draft())

    assert store.list_safe() == [
        {
            "draft_id": "draft-001",
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
    with pytest.raises(ValueError, match="confirmation"):
        store.erase("draft-001", confirmation_id="draft-other")
    assert store.load("draft-001") == _draft()
    assert store.erase("draft-001", confirmation_id="draft-001") is True
    assert store.erase("draft-001", confirmation_id="draft-001") is False
    assert store.list_safe() == []


def test_local_vector_draft_store_refuses_non_temporary_root() -> None:
    with pytest.raises(ValueError, match="temporary"):
        LocalVectorDraftStore(Path.cwd() / "local-vector-drafts")
