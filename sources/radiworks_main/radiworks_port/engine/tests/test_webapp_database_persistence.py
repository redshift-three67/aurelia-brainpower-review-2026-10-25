"""Regression contract for the selected rate database in the analysis UI."""

from pathlib import Path


PAGE = (
    Path(__file__).resolve().parents[2]
    / "webapp"
    / "js"
    / "views"
    / "analyze.js"
)


def test_database_selection_is_restored_after_async_catalog_render_and_saved_on_change():
    source = PAGE.read_text(encoding="utf-8")

    assert 'const savedDb = localStorage.getItem("radiworks_selected_db");' in source
    assert 'localStorage.setItem("radiworks_selected_db", dbSelect.value);' in source
    restore = "const savedOption = savedDb && [...dbSelect.options].some("
    assert 'const restoredDb = selectorFor(savedDb || "");' in source
    assert '(option) => option.value === restoredDb' in source
    assert restore in source
    assert "if (savedOption) {\n      dbSelect.value = restoredDb;" in source
    assert source.index('renderDatabases(data.databases, savedDb || "");') < source.index(restore)
