from __future__ import annotations

import json

from core.compliance.runtime_manifest import RuntimeManifestService


def test_erasure_manifest_classifies_web_job_logs_via_pseudonymous_run_trace(tmp_path) -> None:
    service = RuntimeManifestService(tmp_path / "runtime")
    client_id = service.get_or_create_client(
        {
            "first_name": "Klara",
            "last_name": "Beispiel",
            "birth_date": "01012000",
            "birth_place": "Augsburg",
        }
    )["client_id"]
    workbench = tmp_path / "workbench"
    workbench.mkdir()
    (workbench / "run_traces.json").write_text(
        json.dumps(
            {
                "run_traces": [
                    {"run_id": "scan-attributable", "review": {"client_id": client_id}}
                ]
            }
        ),
        encoding="utf-8",
    )
    jobs = tmp_path / "web-jobs"
    jobs.mkdir()
    attributable = jobs / "scan-attributable.stdout.log"
    unattributable = jobs / "scan-unknown.stderr.log"
    attributable.write_text("log", encoding="utf-8")
    unattributable.write_text("log", encoding="utf-8")

    manifest = service.erasure_manifest(
        client_id, workbench_root=workbench, web_job_root=jobs
    )

    logs = {entry["path"]: entry["attribution"] for entry in manifest["web_job_logs"]}
    assert logs[str(attributable)] == "attributable_via_run_trace"
    assert logs[str(unattributable)] == "unattributable_global"
    assert attributable.exists()
    assert unattributable.exists()
