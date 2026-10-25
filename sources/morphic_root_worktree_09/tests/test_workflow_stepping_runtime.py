from pathlib import Path

from apps.web.main import create_app
from tests.test_web_shell import request


ROOT = Path(__file__).resolve().parents[1]
STATIC = ROOT / "apps/web/static"


def test_workflow_stepping_uses_csp_safe_self_hosted_assets() -> None:
    app = create_app()
    page = request(app, "GET", "/workflow-stepping")
    css = request(app, "GET", "/static/workflow-stepping.css")
    js = request(app, "GET", "/static/workflow-stepping.js")
    assert page.status_code == 200
    assert css.status_code == 200
    assert js.status_code == 200
    assert '/static/workflow-stepping.css' in page.text
    assert '/static/workflow-stepping.js' in page.text
    assert "fonts.googleapis.com" not in page.text
    assert " style=" not in page.text
    assert "onclick=" not in page.text
    assert page.text.count("<script") == 1
    assert '<script src="/static/workflow-stepping.js" defer></script>' in page.text


def test_workflow_stepping_content_is_honest_about_execution_paths() -> None:
    html = (STATIC / "workflow-stepping.html").read_text(encoding="utf-8")
    assert "field workflow-scan" in html
    assert "scan top3-scan" in html
    assert "Erklaermodell" in html
    assert "3, 5, 7 oder 9" in html
    assert "Level 1 bis 4" in html
    assert "separater Harmonisierungsjob" in html
    assert html.count('class="workflow-panel') == 12


def test_workflow_stepping_dom_css_and_keyboard_contract_align() -> None:
    html = (STATIC / "workflow-stepping.html").read_text(encoding="utf-8")
    css = (STATIC / "workflow-stepping.css").read_text(encoding="utf-8")
    js = (STATIC / "workflow-stepping.js").read_text(encoding="utf-8")
    assert 'id="workflow-nav"' in html
    assert ".workflow-step" in css
    assert 'className = "workflow-step"' in js
    assert 'className = "workflow-connector"' in js
    assert 'setAttribute("aria-controls"' in js
    assert "button.id = buttonId" in js
    assert 'setAttribute("aria-labelledby", buttonId)' in js
    assert 'setAttribute("aria-current"' in js
    assert 'case "Home"' in js
    assert 'case "End"' in js
    assert "scrollIntoView" in js
