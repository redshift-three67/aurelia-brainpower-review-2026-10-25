"""Regression contract for persisted active-case selection."""

from pathlib import Path


PAGE = Path(__file__).resolve().parents[2] / "webapp" / "js" / "views" / "cases.js"


def test_active_case_is_saved_only_after_activation_and_restored_after_case_list_refresh():
    source = PAGE.read_text(encoding="utf-8")

    activation = "const loaded = entry.ref ? await api.activateCaseRef(entry.ref) : await api.activateCase(entry.name);"
    persisted = 'localStorage.setItem("radiworks_active_case", `ref:${loaded.ref}`);'
    startup = 'const savedCase = localStorage.getItem("radiworks_active_case");'
    assert activation in source
    assert persisted in source
    assert source.index(activation) < source.index(persisted)
    assert "if (entry.ref && loaded.ref !== entry.ref)" in source
    assert startup in source
    assert source.index("refreshCases().then((loaded) => {") < source.index(startup)
    assert source.index("if (!loaded) return;") < source.index(startup)
