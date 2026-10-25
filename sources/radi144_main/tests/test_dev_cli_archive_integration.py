from types import SimpleNamespace

from dev_cli import mirror_session_archive
from app.services.client_registry_service import ClientRegistryService
from app.services.report_manifest_service import ReportManifestService
from app.services.session_archive_service import SessionArchiveService


def test_mirror_session_archive_registers_client_session_and_artifacts(tmp_path):
    args = SimpleNamespace(
        firstname="Max",
        surname="Mustermann",
        dob="01011990",
        place="Berlin",
        planet="Mars",
        mode="precision",
        matrix_size=12,
        weight="Sanft",
        palette="Client Coherent (Auto)",
        hrv_sim=False,
        quantum_active=False,
        use_planetary=True,
        emf_compensate=True,
        amplifier="",
        symmetry="none",
        harmonize=True,
        template_name="Testlauf",
    )

    all_results = [
        {
            "focus": "Harmonisierung",
            "resonance_score": 0.98,
            "hardware": "CPU (CUDA)",
            "rates_string": "1234",
        },
        {
            "focus": "Vitalitaet",
            "resonance_score": 0.95,
            "hardware": "CPU (CUDA)",
            "rates_string": "5678",
        },
    ]

    exported_paths = [
        tmp_path / "Max_Mustermann_001.pdf",
        tmp_path / "Max_Mustermann_001.xlsx",
        tmp_path / "Max_Mustermann_001_KOMPLETT.pdf",
    ]
    for path in exported_paths:
        path.write_text("artifact", encoding="utf-8")

    summary = mirror_session_archive(
        args=args,
        client_data={"first_name": "Max", "last_names": ["Mustermann"]},
        full_name="Max Mustermann",
        focus_list=["Harmonisierung", "Vitalitaet"],
        all_results=all_results,
        out_dir=str(tmp_path),
        exported_paths=[str(path) for path in exported_paths],
        harmonization_status="requested",
        archive_root=tmp_path / "runtime",
    )

    assert summary["client_id"].startswith("cli-")
    assert summary["session_id"].startswith("sess-")
    assert len(summary["artifact_ids"]) == 3

    client_service = ClientRegistryService(tmp_path / "runtime" / "clients.json")
    session_service = SessionArchiveService(tmp_path / "runtime" / "sessions.json")
    report_service = ReportManifestService(tmp_path / "runtime" / "artifacts.json")

    session = session_service.get_session(summary["session_id"])
    assert session is not None
    assert session.client_ref.client_id == summary["client_id"]
    assert session.focus == "Harmonisierung"
    assert session.focus_sequence == ["Harmonisierung", "Vitalitaet"]
    assert session.harmonization_status == "requested"
    assert len(session.artifact_ids) == 3

    artifacts = report_service.list_for_session(summary["session_id"])
    assert len(artifacts) == 3
    assert sorted(item.artifact_type for item in artifacts) == ["combined_pdf", "pdf", "xlsx"]

    client = client_service.get_or_create(
        {
            "first_name": "Max",
            "last_names": ["Mustermann"],
            "birth_date": "1990-01-01",
            "birth_place": "Berlin",
            "planet": "Mars",
        }
    )
    assert client.client_id == summary["client_id"]
