from __future__ import annotations

from core.compliance.runtime_manifest import RuntimeManifestService


def test_erasure_manifest_lists_harmonization_job_and_event_files_as_unattributable(tmp_path) -> None:
    service = RuntimeManifestService(tmp_path / "runtime")
    client_id = service.get_or_create_client(
        {"first_name": "Klara", "last_name": "Beispiel", "birth_date": "01012000", "birth_place": "Augsburg"}
    )["client_id"]
    root = tmp_path / "harmonization_jobs"
    events = root / "events"
    events.mkdir(parents=True)
    job = root / "harm-test.json"
    event = events / "harm-test.jsonl"
    job.write_text("{}", encoding="utf-8")
    event.write_text("{}\n", encoding="utf-8")

    manifest = service.erasure_manifest(client_id, harmonization_root=root)

    files = {entry["path"]: entry["attribution"] for entry in manifest["harmonization_artifacts"]}
    assert files[str(job)] == "unattributable_global"
    assert files[str(event)] == "unattributable_global"
    assert job.exists()
    assert event.exists()
