import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _sample_scan(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "client": {
                    "name": "Mustermann",
                    "first_name": "Klaus",
                    "birth_date": "09041966",
                    "birth_place": "Augsburg",
                },
                "sub_results": {
                    "top": [
                        {
                            "label": "Schwermetall-LeberschÃ¤den",
                            "group": "atmung_lunge_detailliert",
                            "score": 6.2,
                        }
                    ]
                },
                "quantum_synergy": [
                    {
                        "items": [{"label": "Bronchien"}, {"label": "Mucosa compositum"}],
                        "score": 8.4,
                        "category": "primary",
                    }
                ],
                "remedy_synergies": [
                    {"item1": "Mucosa compositum", "item2": "Bronchien", "synergy_score": 7.1}
                ],
            }
        ),
        encoding="utf-8",
    )


def _sample_scan_with_profile(path: Path, profile: str, first_item: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "client": {
                    "name": "Mustermann",
                    "first_name": "Klaus",
                    "birth_date": "09041966",
                    "birth_place": "Augsburg",
                },
                "profile": profile,
                "quantum_synergy": [
                    {
                        "items": [
                            {"label": first_item, "group": "atmung_lunge_detailliert"},
                            {"label": "Mucosa compositum", "group": "heel_komplexmittel"},
                        ],
                        "score": 8.4,
                        "category": "primary",
                        "scan_overlap": 2,
                        "components": {
                            "individual_scores": 6.5,
                            "resonance": 7.8,
                            "harmony": 9.2,
                            "relevance": 6.1,
                        },
                    }
                ],
                "remedy_synergies": [
                    {"item1": "Mucosa compositum", "item2": first_item, "synergy_score": 7.1}
                ],
            }
        ),
        encoding="utf-8",
    )


def _run_tool(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=30,
    )


def test_interpretation_report_uses_legacy_archive_shape(tmp_path: Path) -> None:
    archive_root = tmp_path / "archive"
    _sample_scan(
        archive_root
        / "Resonanz"
        / "Mustermann_Klaus_09041966_Augsburg"
        / "20251222_210515_TOP9_SESSION"
        / "01_atmung_lunge_detailliert"
        / "20251222_210515_01_atmung_lunge_detailliert_top9_multiplex_scan.json"
    )

    result = _run_tool(
        [
            "tools.interpretation_generator",
            "Mustermann",
            "Klaus",
            "--birth-date",
            "09041966",
            "--birth-place",
            "Augsburg",
            "--scans",
            "9",
            "--focus",
            "Bronchien",
            "--archive-root",
            str(archive_root),
            "--output-root",
            str(tmp_path),
        ]
    )

    assert result.returncode == 0, result.stdout + result.stderr
    html_files = list((tmp_path / "Deutung" / "Mustermann_Klaus_09041966_Augsburg").glob("*_top9/deutung_*.html"))
    assert len(html_files) == 1
    html = html_files[0].read_text(encoding="utf-8")
    assert "Deutung - Klaus Mustermann" in html
    assert 'class="container"' in html
    # Der Header-Block kann zusaetzliche Utility-Klassen tragen (z.B. "report-block"
    # fuer das gemeinsame Card-Styling), daher nur auf den "header"-Klassennamen pruefen.
    assert 'class="header' in html
    assert "Bronchien" in html
    assert "Schwermetall-Leberschäden" in html
    assert "Schwermetall-LeberschÃ¤den" not in html
    assert "Schluesselbefunde" in html
    assert "Erkannte Muster" in html
    assert "Empfehlungen" in html
    assert "KI-gestuetzte Tiefenanalyse" in html
    assert "Mucosa compositum" in html

    pdf_files = list((tmp_path / "Deutung" / "Mustermann_Klaus_09041966_Augsburg").glob("*_top9/deutung_*.pdf"))
    assert len(pdf_files) == 1
    assert pdf_files[0].read_bytes().startswith(b"%PDF-")


def test_synergy_and_remedy_reports_use_legacy_archive_shape(tmp_path: Path) -> None:
    archive_root = tmp_path / "archive"
    scan_path = (
        archive_root
        / "Resonanz"
        / "Mustermann_Klaus_09041966_Augsburg"
        / "20251222_210515_TOP9_SESSION"
        / "01_atmung_lunge_detailliert"
        / "20251222_210515_01_atmung_lunge_detailliert_top9_multiplex_scan.json"
    )
    _sample_scan(scan_path)
    report_root = tmp_path / "reports"

    synergy = _run_tool(
        [
            "tools.synergy_consolidator",
            "Mustermann",
            "Klaus",
            "--birth-date",
            "09041966",
            "--birth-place",
            "Augsburg",
            "--archive-root",
            str(archive_root),
            "--output-root",
            str(report_root),
        ]
    )
    assert synergy.returncode == 0, synergy.stdout + synergy.stderr
    synergy_files = list((report_root / "Synergy" / "Mustermann_Klaus_09041966_Augsburg").glob("*_synergy_report/synergy_gesamt.html"))
    assert len(synergy_files) == 1
    assert "Synergy-Gesamtanalyse" in synergy_files[0].read_text(encoding="utf-8")
    synergy_json = list((report_root / "Synergy" / "Mustermann_Klaus_09041966_Augsburg").glob("*_synergy_report/synergy_gesamt.json"))
    assert len(synergy_json) == 1
    synergy_payload = json.loads(synergy_json[0].read_text(encoding="utf-8"))
    assert synergy_payload["schema"] == "morphic_synergy_report"
    assert synergy_payload["schema_version"] == 1
    synergy_pdfs = list((report_root / "Synergy" / "Mustermann_Klaus_09041966_Augsburg").glob("*_synergy_report/synergy_gesamt.pdf"))
    assert len(synergy_pdfs) == 1
    assert synergy_pdfs[0].read_bytes().startswith(b"%PDF-")

    remedy = _run_tool(
        [
            "tools.remedy_reporter",
            "Mustermann",
            "Klaus",
            "--birth-date",
            "09041966",
            "--birth-place",
            "Augsburg",
            "--archive-root",
            str(archive_root),
            "--output-root",
            str(report_root),
            "--top-n",
            "9",
        ]
    )
    assert remedy.returncode == 0, remedy.stdout + remedy.stderr
    remedy_files = list((report_root / "Remedies" / "Mustermann_Klaus_09041966_Augsburg").glob("*_top9_remedies.html"))
    assert len(remedy_files) == 1
    remedy_html = remedy_files[0].read_text(encoding="utf-8")
    assert "Remedy Report - Klaus Mustermann" in remedy_html
    assert "Synergetische Remedy-Kombinationen (Therapeutische Synergie-Analyse)" in remedy_html
    assert "<th>Remedy</th>" in remedy_html
    assert "<th>Raten</th>" in remedy_html
    assert "<th>Synergien</th>" in remedy_html
    assert "<th>Synergie-Score</th>" in remedy_html
    assert "Mucosa compositum" in remedy_html
    assert "Bronchien" in remedy_html
    assert "atmung_lunge_detailliert" in remedy_html
    remedy_json = list((report_root / "Remedies" / "Mustermann_Klaus_09041966_Augsburg").glob("*_top9_remedies.json"))
    assert len(remedy_json) == 1
    remedy_payload = json.loads(remedy_json[0].read_text(encoding="utf-8"))
    assert remedy_payload["schema"] == "morphic_remedy_report"
    assert remedy_payload["schema_version"] == 1
    remedy_pdfs = list((report_root / "Remedies" / "Mustermann_Klaus_09041966_Augsburg").glob("*_top9_remedies.pdf"))
    assert len(remedy_pdfs) == 1
    assert remedy_pdfs[0].read_bytes().startswith(b"%PDF-")
    profile_json = list((report_root / "Remedies" / "Mustermann_Klaus_09041966_Augsburg").glob("*_remedy.json"))
    assert len(profile_json) == 1
    profile_payload = json.loads(profile_json[0].read_text(encoding="utf-8"))
    assert profile_payload["schema"] == "morphic_remedy_profile_report"
    assert profile_payload["schema_version"] == 1
    profile_pdfs = list((report_root / "Remedies" / "Mustermann_Klaus_09041966_Augsburg").glob("*_remedy.pdf"))
    assert len(profile_pdfs) == 1
    assert profile_pdfs[0].read_bytes().startswith(b"%PDF-")


def test_synergy_report_renders_legacy_quantum_detail_sections(tmp_path: Path) -> None:
    archive_root = tmp_path / "archive"
    _sample_scan_with_profile(
        archive_root
        / "Resonanz"
        / "Mustermann_Klaus_09041966_Augsburg"
        / "20251222_210515_TOP9_SESSION"
        / "01_atmung_lunge_detailliert"
        / "20251222_210515_01_atmung_lunge_detailliert_top9_multiplex_scan.json",
        "atmung_lunge_detailliert",
        "Bronchien",
    )
    _sample_scan_with_profile(
        archive_root
        / "Resonanz"
        / "Mustermann_Klaus_09041966_Augsburg"
        / "20251222_210515_TOP9_SESSION"
        / "02_mikrozirkulation"
        / "20251222_210515_02_mikrozirkulation_top9_multiplex_scan.json",
        "mikrozirkulation",
        "Kapillaren",
    )

    result = _run_tool(
        [
            "tools.synergy_consolidator",
            "Mustermann",
            "Klaus",
            "--birth-date",
            "09041966",
            "--birth-place",
            "Augsburg",
            "--archive-root",
            str(archive_root),
            "--output-root",
            str(tmp_path / "reports"),
        ]
    )

    assert result.returncode == 0, result.stdout + result.stderr
    html_files = list(
        (tmp_path / "reports" / "Synergy" / "Mustermann_Klaus_09041966_Augsburg").glob(
            "*_synergy_report/synergy_gesamt.html"
        )
    )
    assert len(html_files) == 1
    html = html_files[0].read_text(encoding="utf-8")
    assert "Analysierte Profile" in html
    assert "Cross-Profile Synergien" in html
    assert "Quantum-Synergy Analyse" in html
    assert "Profil: atmung_lunge_detailliert" in html
    assert "Profil: mikrozirkulation" in html
    assert "Top Quantum-Synergien" in html
    assert "Bronchien" in html
    assert "Kapillaren" in html
    assert "Mucosa compositum" in html
    assert "Resonanz-Verstärkung" in html


def test_trend_report_writes_pdf_for_real_history(tmp_path: Path) -> None:
    archive_root = tmp_path / "archive"
    first_scan = (
        archive_root
        / "Resonanz"
        / "Mustermann_Klaus_09041966_Augsburg"
        / "20251222_210515_TOP9_SESSION"
        / "01_atmung_lunge_detailliert"
        / "20251222_210515_01_atmung_lunge_detailliert_top9_multiplex_scan.json"
    )
    second_scan = (
        archive_root
        / "Resonanz"
        / "Mustermann_Klaus_09041966_Augsburg"
        / "20251223_210515_TOP9_SESSION"
        / "01_atmung_lunge_detailliert"
        / "20251223_210515_01_atmung_lunge_detailliert_top9_multiplex_scan.json"
    )
    _sample_scan(first_scan)
    _sample_scan(second_scan)

    result = _run_tool(
        [
            "tools.trend_analyzer",
            "Mustermann",
            "Klaus",
            "--birth-date",
            "09041966",
            "--birth-place",
            "Augsburg",
            "--archive-root",
            str(archive_root),
            "--output-root",
            str(tmp_path / "reports"),
        ]
    )

    assert result.returncode == 0, result.stdout + result.stderr
    trend_dir = tmp_path / "reports" / "Trends" / "Mustermann_Klaus_09041966_Augsburg"
    trend_pdfs = list(trend_dir.glob("trendanalyse_*.pdf"))
    assert len(trend_pdfs) == 1
    assert trend_pdfs[0].read_bytes().startswith(b"%PDF-")


def test_trend_report_writes_legacy_notice_when_history_is_insufficient(tmp_path: Path) -> None:
    result = _run_tool(
        [
            "tools.trend_analyzer",
            "Mustermann",
            "Klaus",
            "--birth-date",
            "09041966",
            "--birth-place",
            "Augsburg",
            "--archive-root",
            str(tmp_path / "empty_archive"),
            "--output-root",
            str(tmp_path / "reports"),
        ]
    )

    assert result.returncode == 0, result.stdout + result.stderr
    notice = tmp_path / "reports" / "Trends" / "Mustermann_Klaus_09041966_Augsburg" / "Hinweis.txt"
    assert notice.exists()
    assert "Noch keine Trends" in notice.read_text(encoding="utf-8")
