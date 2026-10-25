from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDEX_HTML = ROOT / "apps" / "web" / "static" / "index.html"
APP_JS = ROOT / "apps" / "web" / "static" / "app.js"


def test_client_context_identifies_the_existing_client_vector_without_new_inputs() -> None:
    source = INDEX_HTML.read_text(encoding="utf-8")

    assert 'id="client-vector-context"' in source
    assert 'data-vector="client"' in source
    assert "Standard-Signatur aus Name, Geburtsdatum und Geburtsort" in source
    assert "Diese Uebersicht aendert keine Analyseparameter" in source


def test_client_context_displays_all_radi144_vector_boundaries_without_activating_new_ones() -> None:
    html = INDEX_HTML.read_text(encoding="utf-8")

    assert 'data-vector="client" data-vector-state="active"' in html
    assert 'data-vector="group" data-vector-state="local-draft"' in html
    assert 'id="group-vector-draft"' in html
    assert 'data-vector="geo" data-vector-state="not-activated" aria-disabled="true"' in html
    assert 'data-vector="image" data-vector-state="optional"' in html
    assert "Standard-Signatur" in html
    assert "Lokaler Entwurf" in html
    assert "Referenzbild in Phase 4" in html


def test_client_context_does_not_expose_unapproved_vector_or_pii_fields() -> None:
    html = INDEX_HTML.read_text(encoding="utf-8")
    payload = APP_JS.read_text(encoding="utf-8")

    for field_name in (
        "group_members",
        "latitude",
        "longitude",
        "radius",
        "gender",
        "weight",
        "height",
        "stress_level",
        "sleep_hours",
        "emf_exposure",
    ):
        assert f'name="{field_name}"' not in html
        assert f'{field_name}:' not in payload

    assert 'name="image_path"' in html
    assert "image_path:" in payload
    assert 'name="main_symptom"' in html
    assert "main_symptom:" in payload
