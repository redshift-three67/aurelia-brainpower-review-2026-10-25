from app.models.session_archive import SessionArchiveEntry
from app.services.session_archive_service import SessionArchiveService


def test_session_archive_creates_manifest_from_analysis_context(tmp_path):
    service = SessionArchiveService(tmp_path / "sessions.json")

    entry = service.create_session(
        client_ref={"client_id": "cli-123", "client_name": "Max Mustermann"},
        focus="Harmonisierung",
        focus_sequence=["Harmonisierung", "Vitalitaet"],
        config={"mode": "precision", "matrix_size": 12, "emf_compensate": True},
        result_summary={"resonance_score": 0.9812, "hardware": "CPU"},
    )

    assert isinstance(entry, SessionArchiveEntry)
    assert entry.client_ref.client_id == "cli-123"
    assert entry.focus == "Harmonisierung"
    assert entry.focus_sequence == ["Harmonisierung", "Vitalitaet"]
    assert entry.config["matrix_size"] == 12
    assert entry.result_summary["hardware"] == "CPU"


def test_session_archive_can_attach_artifact_ids(tmp_path):
    service = SessionArchiveService(tmp_path / "sessions.json")
    entry = service.create_session(
        client_ref={"client_name": "Anna Muster"},
        focus="Schlaf",
        focus_sequence=["Schlaf"],
        config={"mode": "quantum", "matrix_size": 24},
        result_summary={"resonance_score": 0.88},
    )

    updated = service.attach_artifact(entry.session_id, "art-001")

    assert updated.artifact_ids == ["art-001"]
    persisted = service.get_session(entry.session_id)
    assert persisted is not None
    assert persisted.artifact_ids == ["art-001"]
