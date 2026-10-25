from apps.cli.commands.helpers import _render_basic_html, _render_multiplex_txt
from tools.reporting_common import render_legacy_html


def test_shared_legacy_html_contains_wellbeing_disclaimer() -> None:
    html = render_legacy_html(
        title="Deutung - Klaus Mustermann",
        subtitle="Morphic Engine Deutungsbericht",
        body_html='<div class="section"><h2>Zusammenfassung</h2><p>Test</p></div>',
        focus="Bronchien",
    )

    assert "Wellbeing Compliance" in html
    assert "keine medizinische Diagnose" in html
    assert "keine Behandlung oder Heilung" in html


def test_multiplex_html_contains_wellbeing_disclaimer() -> None:
    html = _render_basic_html(
        {
            "command": "multiplex_scan",
            "focus": "Bronchien",
            "client": {
                "first_name": "Klaus",
                "name": "Mustermann",
                "birth_date": "09041966",
                "birth_place": "Augsburg",
            },
            "analysis": {"rates": [1, 2, 3], "morphic_field": 0.5},
            "sub_results": {
                "top": [{"label": "Bronchien", "score": 8.0, "group": "Atmung"}]
            },
        }
    )

    assert "Wellbeing Compliance" in html
    assert "keine medizinische Diagnose" in html
    assert "keine Behandlung oder Heilung" in html


def test_multiplex_txt_contains_wellbeing_disclaimer() -> None:
    text = _render_multiplex_txt(
        {
            "profile": "atmung_lunge_detailliert",
            "focus": "Bronchien",
            "client": {"first_name": "Klaus", "name": "Mustermann"},
            "sub_results": {
                "top": [{"label": "Bronchien", "score": 8.0, "group": "Atmung"}]
            },
        }
    )

    assert "Wellbeing Compliance" in text
    assert "keine medizinische Diagnose" in text
    assert "keine Behandlung oder Heilung" in text
