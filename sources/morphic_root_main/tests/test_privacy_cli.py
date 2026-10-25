import json
import os
import subprocess
import sys
from pathlib import Path

from core.compliance.runtime_manifest import DEFAULT_ERASURE_GATE_TOKEN, RuntimeManifestService


ROOT = Path(__file__).resolve().parents[1]


def _run_privacy(args: list[str], runtime: Path) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"
    return subprocess.run(
        [sys.executable, "-m", "apps.cli.main", "privacy", *args, "--runtime", str(runtime)],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=30,
    )


def test_privacy_cli_lists_safe_clients_and_executes_gated_erasure(tmp_path: Path) -> None:
    runtime = tmp_path / "runtime"
    service = RuntimeManifestService(runtime)
    report = tmp_path / "reports" / "bericht.html"
    report.parent.mkdir()
    report.write_text("report", encoding="utf-8")
    artifact = service.register_artifact(
        {
            "first_name": "Klaus",
            "last_name": "Mustermann",
            "birth_date": "09041966",
            "birth_place": "Augsburg",
        },
        artifact_type="html",
        path=report,
        label="Deutung",
        session_id="sess-test",
    )
    client_id = artifact["client_id"]

    clients = _run_privacy(["clients", "--json"], runtime)
    assert clients.returncode == 0, clients.stdout + clients.stderr
    clients_payload = json.loads(clients.stdout)
    assert clients_payload == service.list_clients_safe()
    assert "Klaus" not in clients.stdout
    assert "Mustermann" not in clients.stdout

    manifest = _run_privacy(["erasure-manifest", client_id], runtime)
    assert manifest.returncode == 0, manifest.stdout + manifest.stderr
    manifest_payload = json.loads(manifest.stdout)
    assert manifest_payload["client_id"] == client_id
    assert manifest_payload["artifacts"][0]["path"] == str(report)
    assert report.exists()

    denied = _run_privacy(["erase", client_id, "--gate-token", "WRONG"], runtime)
    assert denied.returncode == 1
    assert report.exists()

    erased = _run_privacy(["erase", client_id, "--gate-token", DEFAULT_ERASURE_GATE_TOKEN], runtime)
    assert erased.returncode == 0, erased.stdout + erased.stderr
    erased_payload = json.loads(erased.stdout)
    assert erased_payload["outcome"] == "ok"
    assert not report.exists()

    audit = _run_privacy(["audit", client_id, "--json"], runtime)
    assert audit.returncode == 0, audit.stdout + audit.stderr
    audit_payload = json.loads(audit.stdout)
    assert any(entry["action"] == "erasure_execute" for entry in audit_payload)
