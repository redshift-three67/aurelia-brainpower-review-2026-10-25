import json
from pathlib import Path

from app.services.client_registry_service import ClientRegistryService
from app.services.session_archive_service import (
    SessionArchiveService,
    export_powershell_templates_from_runtime_dir,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_runtime_session_archive_exports_legacy_compatible_powershell_templates(tmp_path):
    runtime_dir = tmp_path / "runtime"
    client_service = ClientRegistryService(runtime_dir / "clients.json")
    session_service = SessionArchiveService(runtime_dir / "sessions.json")

    client = client_service.get_or_create(
        {
            "first_name": "Max",
            "last_names": ["Mustermann"],
            "birth_date": "1990-01-01",
            "birth_place": "Berlin",
            "planet": "Mars",
        }
    )
    session_service.create_session(
        client_ref={"client_id": client.client_id, "client_name": "Max Mustermann"},
        focus="Harmonisierung",
        focus_sequence=["Harmonisierung", "Vitalitaet"],
        config={
            "mode": "precision",
            "matrix_size": 24,
            "weight": "Sanft",
            "palette": "Client Coherent (Auto)",
            "hrv_sim": True,
            "quantum_active": False,
            "use_planetary": True,
            "emf_compensate": True,
            "amplifier": "schungit",
            "symmetry": "horizontal",
            "template_name": "Archivlauf",
        },
        result_summary={"resonance_score": 0.98},
    )

    out_file = export_powershell_templates_from_runtime_dir(runtime_dir)
    payload = json.loads(out_file.read_text(encoding="utf-8"))

    assert payload["_meta"]["source"] == "data/runtime/sessions.json"
    assert payload["_meta"]["version"] == "1.0"
    assert payload["templates"][0] == {
        "timestamp": payload["templates"][0]["timestamp"],
        "template_name": "Archivlauf",
        "client_name": "Max Mustermann",
        "surname": "Mustermann",
        "firstname": "Max",
        "dob": "01011990",
        "place": "Berlin",
        "planet": "Mars",
        "focus": "Harmonisierung;Vitalitaet",
        "weight": "Sanft",
        "palette": "Client Coherent (Auto)",
        "mode": "precision",
        "hrv_sim": True,
        "quantum_active": False,
        "use_planetary": True,
        "emf_compensate": True,
        "amplifier": "schungit",
        "symmetry": "horizontal",
        "matrix_size": 24,
    }


def test_generate_matrix_prefers_runtime_metadata_adapter_with_legacy_fallback():
    script = (PROJECT_ROOT / "generate_matrix.ps1").read_text(encoding="utf-8")

    assert "data\\runtime" in script
    assert "export_powershell_templates_from_runtime_dir" in script
    assert "powershell_templates.json" in script
    assert "Fallback: legacy session_templates.json" in script


def test_generate_matrix_resolves_python_from_project_venv_before_global_python():
    script = (PROJECT_ROOT / "generate_matrix.ps1").read_text(encoding="utf-8")

    assert "function Resolve-Radi144PythonCommand" in script
    assert "$PythonCommand = Resolve-Radi144PythonCommand" in script
    assert "$PythonCommandExpression" in script
    assert script.index(".venv\\Scripts\\python.exe") < script.index(".venv\\bin\\python")
    assert script.index(".venv\\bin\\python") < script.index('"python"')
    assert script.index('"python"') < script.index('"py"')
    assert "& $PythonCommand --version" in script
    assert "& $PythonCommand -c \"import torch\"" in script
    assert "& $PythonCommand -c \"import reportlab\"" in script
    assert "& $PythonCommand -c \"from app.services.session_archive_service" in script
    assert '$Command = "$PythonCommandExpression `"$ScriptPath`" "' in script


def test_powershell_runtime_scratch_files_stay_ignored():
    import subprocess

    for path in ["temp_group.json", "_temp_db_list.txt", "data/runtime/powershell_templates.json"]:
        result = subprocess.run(
            ["git", "check-ignore", "-q", path],
            cwd=PROJECT_ROOT,
            check=False,
        )
        assert result.returncode == 0, f"{path} is local PowerShell/runtime scratch state"
