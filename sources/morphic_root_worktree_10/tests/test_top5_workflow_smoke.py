from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from core.compliance.runtime_manifest import RuntimeManifestService


ROOT = Path(__file__).resolve().parents[1]


def test_top5_scan_writes_multiplex_exports(tmp_path: Path) -> None:
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"
    runtime = tmp_path / "runtime"
    env["MORPHIC_RUNTIME_DIR"] = str(runtime)

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "apps.cli.main",
            "scan",
            "top3-scan",
            "Test",
            "Klient",
            "--birth-date",
            "01011990",
            "--birth-place",
            "Berlin",
            "--export",
            str(tmp_path),
            "--hardware-profile",
            "windows",
            "--k-total",
            "16",
            "--top-k",
            "2",
            "--top-n",
            "3",
            "--no-synergy",
            "--focus",
            "Bronchien",
        ],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=180,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert f"Die HTML-Berichte wurden unter {tmp_path.resolve()} gespeichert." in result.stdout
    assert "Benutzer_Archive_Start Ordner" not in result.stdout
    exports = list(tmp_path.rglob("*_multiplex_scan.json"))
    assert len(exports) >= 3
    assert any("TOP3_SESSION" in str(path) for path in exports)

    html_exports = [path.with_suffix(".html") for path in exports]
    assert all(path.exists() for path in html_exports)
    assert "Resonanzanalyse" in html_exports[0].read_text(encoding="utf-8")

    pdf_exports = [path.with_suffix(".pdf") for path in exports]
    assert all(path.exists() for path in pdf_exports)
    assert all(path.read_bytes().startswith(b"%PDF-") for path in pdf_exports)

    artifacts = RuntimeManifestService(runtime).load_store("artifacts")["artifacts"]
    artifact_types = {entry["artifact_type"] for entry in artifacts}
    assert "multiplex_scan_pdf" in artifact_types
    assert {"synergy_pdf", "remedy_pdf", "remedy_profile_pdf"} <= artifact_types
    pdf_artifacts = [entry for entry in artifacts if entry["artifact_type"] == "multiplex_scan_pdf"]
    assert len(pdf_artifacts) >= len(pdf_exports)
    assert all(Path(entry["path"]).exists() for entry in pdf_artifacts)

    for export_path in exports:
        payload = json.loads(export_path.read_text(encoding="utf-8"))
        assert payload["schema"] == "morphic_multiplex_scan"
        assert payload["schema_version"] == 1
        top = (payload.get("sub_results") or {}).get("top") or []
        raw_groups = {
            str(item.get("group", "")).strip()
            for item in top
            if isinstance(item, dict) and str(item.get("group", "")).strip()
        }
        txt = export_path.with_suffix(".txt").read_text(encoding="utf-8")
        used_groups_section = txt.split("Verwendete Gruppen:", 1)[-1].split("Top-Resonanzen", 1)[0]
        for raw_group in raw_groups:
            assert raw_group not in used_groups_section
            assert f"\n{raw_group.upper()}:" not in txt
            assert f"\n{raw_group}:" not in txt

    assert list((tmp_path / "Synergy" / "Test_Klient_01011990_Berlin").glob("*_synergy_report/synergy_gesamt.html"))
    synergy_pdfs = list((tmp_path / "Synergy" / "Test_Klient_01011990_Berlin").glob("*_synergy_report/synergy_gesamt.pdf"))
    assert synergy_pdfs
    assert all(path.read_bytes().startswith(b"%PDF-") for path in synergy_pdfs)

    assert list((tmp_path / "Remedies" / "Test_Klient_01011990_Berlin").glob("*_top3_remedies.html"))
    remedy_pdfs = list((tmp_path / "Remedies" / "Test_Klient_01011990_Berlin").glob("*_top3_remedies.pdf"))
    profile_remedy_pdfs = list((tmp_path / "Remedies" / "Test_Klient_01011990_Berlin").glob("*_remedy.pdf"))
    assert remedy_pdfs
    assert profile_remedy_pdfs
    assert all(path.read_bytes().startswith(b"%PDF-") for path in remedy_pdfs + profile_remedy_pdfs)

    deutung_files = list((tmp_path / "Deutung" / "Test_Klient_01011990_Berlin").glob("*_top3/deutung_*.html"))
    assert len(deutung_files) == 1
    deutung_html = deutung_files[0].read_text(encoding="utf-8")
    assert "Deutung - Klient Test" in deutung_html
    assert "Keine priorisierten Resonanzwerte im Quellmaterial gefunden." not in deutung_html
    assert "<td colspan=\"3\">" not in deutung_html

    trend_notice = tmp_path / "Trends" / "Test_Klient_01011990_Berlin" / "Hinweis.txt"
    assert trend_notice.exists()
    assert "Noch keine Trends" in trend_notice.read_text(encoding="utf-8")
