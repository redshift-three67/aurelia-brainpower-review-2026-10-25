from __future__ import annotations

import json

from core.compliance.runtime_manifest import RuntimeManifestService


def test_erasure_manifest_reports_structured_workbench_identity_matches_read_only(tmp_path) -> None:
    runtime = tmp_path / "runtime"
    workbench = tmp_path / "workbench"
    service = RuntimeManifestService(runtime)
    client = {
        "first_name": "Klara",
        "last_name": "Beispiel",
        "birth_date": "01012000",
        "birth_place": "Augsburg",
    }
    client_id = service.get_or_create_client(client)["client_id"]
    workbench.mkdir()
    draft_path = workbench / "draft.json"
    original = {
        "draft": {
            "last_name": "Beispiel",
            "first_name": "Klara",
            "birth_date": "01012000",
            "birth_place": "Augsburg",
        }
    }
    draft_path.write_text(json.dumps(original), encoding="utf-8")
    (workbench / "templates.json").write_text("{not valid json", encoding="utf-8")
    (workbench / "run_traces.json").write_text(
        json.dumps({"run_traces": [{"review": {"client_id": client_id}}]}),
        encoding="utf-8",
    )

    manifest = service.erasure_manifest(client_id, workbench_root=workbench)

    stores = {item["store"]: item for item in manifest["workbench_runtime"]}
    assert stores["draft"]["state"] == "identity_match"
    assert stores["draft"]["matched_identity_fields"] == [
        "birth_date",
        "birth_place",
        "first_name",
        "last_name",
    ]
    assert stores["templates"]["state"] == "invalid_json"
    assert stores["run_traces"]["state"] == "identity_match"
    assert stores["run_traces"]["matched_identity_fields"] == ["client_id"]
    assert draft_path.read_text(encoding="utf-8") == json.dumps(original)
