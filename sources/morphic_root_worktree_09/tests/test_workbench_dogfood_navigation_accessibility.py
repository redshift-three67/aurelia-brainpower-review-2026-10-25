from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP_JS = ROOT / "apps/web/static/app.js"
RENDER_JS = ROOT / "apps/web/static/workbench-render.js"
INDEX_HTML = ROOT / "apps/web/static/index.html"


def test_forward_navigation_uses_explicit_phase_readiness_gate() -> None:
    app = APP_JS.read_text(encoding="utf-8")
    render = RENDER_JS.read_text(encoding="utf-8")
    assert "function phaseReadiness(" in app
    assert "window.MorphicWorkbenchCanEnterStep = phaseReadiness" in app
    navigate = app.split("function navigate(direction)", 1)[1].split("/* ── Choice", 1)[0]
    assert "enterStep(next, direction > 0)" in navigate
    assert "phaseReadiness(index)" in navigate
    assert "showInlineState" in navigate
    stepper = render.split("renderStepper(steps)", 1)[1].split("showStep(index)", 1)[0]
    assert "MorphicWorkbenchCanEnterStep" in stepper
    assert "window.MorphicWorkbenchState.registry" not in stepper


def test_review_includes_all_scan_affecting_choices_and_consents() -> None:
    render = RENDER_JS.read_text(encoding="utf-8")
    block = render.split("renderReviewCards(formData", 1)[1].split("/* ── Results", 1)[0]
    for token in (
        "main_symptom",
        "workbenchMode",
        "planetary_vector_enabled",
        "planet_type",
        "group_draft_id",
        "consent_local",
        "consent_safety",
    ):
        assert token in block


def test_new_case_reset_clears_sensitive_form_and_all_active_references() -> None:
    app = APP_JS.read_text(encoding="utf-8")
    assert "function resetWorkbenchForNewCase()" in app
    block = app.split("function resetWorkbenchForNewCase()", 1)[1].split("/* ── Choice", 1)[0]
    for token in (
        "form.reset()",
        "activeJobId = null",
        "RESET_COMPLETED",
        "activeHarmonizationJobId = null",
        "scanResults = null",
        "runTrace = null",
        "clearTimeout(jobPollTimer)",
        "clearTimeout(harmonizationPollTimer)",
        "resetSubstepTimeline",
    ):
        assert token in block
    handler = app.split('const newCase = $("#new-case-button")', 1)[1].split("// Keyboard", 1)[0]
    assert "resetWorkbenchForNewCase" in handler


def test_stepper_and_choice_cards_expose_keyboard_and_selection_semantics() -> None:
    render = RENDER_JS.read_text(encoding="utf-8")
    stepper = render.split("renderStepper(steps)", 1)[1].split("/* ── Hardware", 1)[0]
    for token in (
        'setAttribute("aria-controls"',
        'setAttribute("tabindex"',
        ".focus()",
        "scrollIntoView",
    ):
        assert token in stepper
    choices = render.split("renderChoiceCards(containerId", 1)[1].split("/* ── Reale", 1)[0]
    assert 'setAttribute("role", "radiogroup")' in choices
    assert 'setAttribute("aria-checked"' in choices
    assert 'aria-pressed' not in choices


def test_progress_indicators_have_progressbar_semantics() -> None:
    html = INDEX_HTML.read_text(encoding="utf-8")
    assert 'id="wizard-progress-fill" role="progressbar"' in html
    assert 'id="job-progress-fill" role="progressbar"' in html


def test_read_only_gets_use_buckets_separate_from_mutation_rate_limit() -> None:
    main = (ROOT / "apps/web/main.py").read_text(encoding="utf-8")
    block = main.split('if request.method == "GET":', 1)[1].split("# Lokaler", 1)[0]
    assert 'bucket="read"' in block
    assert 'bucket="report-read"' in block
    assert 'bucket="job-poll"' in block
    assert "return await rate_limit_middleware(request, call_next)" in block


def test_mobile_phase_two_groups_optional_controls_in_disclosure() -> None:
    html = INDEX_HTML.read_text(encoding="utf-8")
    assert '<details class="optional-group-workflow">' in html
    assert '<summary>Optionale Gruppenfunktionen verwalten</summary>' in html
