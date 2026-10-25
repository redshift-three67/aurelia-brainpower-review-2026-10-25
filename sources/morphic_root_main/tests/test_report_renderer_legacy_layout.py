from apps.cli.commands.helpers import _render_basic_html, _render_multiplex_txt


def test_multiplex_report_uses_legacy_inspired_layout_sections() -> None:
    html = _render_basic_html(
        {
            "command": "multiplex_scan",
            "hardware_profile": "windows",
            "hardware_source": "network",
            "h_level": 0.42,
            "focus": "Lunge",
            "client": {
                "first_name": "Klaus",
                "name": "Mustermann",
                "birth_date": "09041966",
                "birth_place": "Augsburg",
            },
            "analysis": {
                "morphic_field": 0.75,
                "holographic_entropy": 1.25,
                "entropy_calibrated": 0.31,
                "rates": [5, 4, 7, 83],
                "heim_signature": [1.1, 2.2],
            },
            "morphic_field": {
                "field_strength": 7.5,
                "coherence": 0.64,
                "resonance_frequency": 432.0,
            },
            "influence_factors": {
                "organ_clock": {"organ": "Lunge", "time_window": "03-05"},
                "image": {"present": False},
            },
            "sub_results": {
                "groups": ["atmung_lunge_detailliert", "heel_remedies_multiplex"],
                "top": [
                    {
                        "label": "Bronchien",
                        "group": "atmung_lunge_detailliert",
                        "score": 8.2,
                        "priority": "hoch",
                        "potency": "C30",
                        "level": "Physische Ebene",
                        "rates": [12.5, 14.0],
                        "description": "Atemwegsbezug",
                    },
                    {
                        "label": "Mucosa compositum",
                        "group": "heel_remedies_multiplex",
                        "score": 5.1,
                        "priority": "mittel",
                        "potency": "D12",
                        "level": "Regulation",
                        "rates": [22.0, 23.5],
                    },
                ],
            },
            "quantum_synergy": [
                {
                    "items": [{"label": "Bronchien"}, {"label": "Mucosa compositum"}],
                    "score": 8.4,
                    "category": "primary",
                    "components": {"resonance": 0.8, "harmony": 0.7, "relevance": 0.9},
                }
            ],
            "remedy_synergies": [
                {"item1": "Mucosa compositum", "item2": "Bronchien", "synergy_score": 7.1}
            ],
        }
    )

    assert "<title>Resonanzanalyse" in html
    assert "class='container'" in html
    assert "header-info" in html
    assert "Morphische Feld-Analyse" in html
    assert "Einflussfaktoren" in html
    assert "Fokus / Symptom" in html
    assert "Resonanzwerte" in html
    assert "Fullbody-Subgruppen" in html
    assert "Intensität (global/gruppe)" in html
    assert "0.62 / 1.00" in html
    assert "Score = Absolute Resonanzstärke" in html
    assert "Priorität:</strong> Level 1-10" in html
    assert "Atmung Lunge Detailliert" in html
    assert "data-group='atmung_lunge_detailliert'" in html
    assert ">atmung_lunge_detailliert<" not in html
    assert "atmung_lunge_detailliert:" not in html
    assert "Atmung Lunge Detailliert: sanft ausgleichen" in html
    assert "Quantum-Synergy Analyse" in html
    assert "Remedy-Synergien" in html
    assert "badge prio-high" in html


def test_multiplex_txt_uses_readable_group_labels() -> None:
    text = _render_multiplex_txt(
        {
            "command": "multiplex_scan",
            "client": {
                "first_name": "Klaus",
                "name": "Mustermann",
            },
            "sub_results": {
                "top": [
                    {
                        "label": "Bronchien",
                        "group": "atmung_lunge_detailliert",
                        "score": 8.2,
                    }
                ]
            },
        }
    )

    assert "Atmung Lunge Detailliert" in text
    assert "atmung_lunge_detailliert" not in text
