from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "apps" / "web" / "static" / "index.html"
APP_JS = ROOT / "apps" / "web" / "static" / "app.js"


def test_wizard_navigation_block_feedback_is_visible_at_navigation_controls() -> None:
    html = INDEX.read_text(encoding="utf-8")
    source = APP_JS.read_text(encoding="utf-8")

    controls = html.split('<div class="wizard-controls">', 1)[1].split("</div>", 1)[0]
    assert 'id="wizard-navigation-state"' in controls
    assert 'role="status"' in controls
    assert 'aria-live="polite"' in controls

    enter_step = source.split("function enterStep(index, enforceGate = true)", 1)[1].split(
        "async function resetWorkbenchForNewCase", 1
    )[0]
    assert 'showWizardNavigationState(blocked, "bad")' in enter_step
    assert 'showWizardNavigationState("", "neutral")' in enter_step
    assert 'showInlineState(blocked, "bad")' not in enter_step


def test_optional_client_context_fields_are_not_wizard_requirements() -> None:
    html = INDEX.read_text(encoding="utf-8")
    source = APP_JS.read_text(encoding="utf-8")

    for name in ("birth_time", "email", "notes"):
        control = html.split(f'name="{name}"', 1)[0].rsplit("<", 1)[1]
        assert "required" not in control

    readiness = source.split("function phaseReadiness(index)", 1)[1].split(
        "window.MorphicWorkbenchCanEnterStep", 1
    )[0]
    assert '"birth_time"' not in readiness
    assert '"email"' not in readiness
    assert '"notes"' not in readiness
