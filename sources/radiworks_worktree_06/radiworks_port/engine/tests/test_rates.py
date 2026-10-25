"""Tests: Raten-Repository (DataService-Port, FUNKTIONSANALYSE §7.2)."""

from radiworks.core.rates import RateRepository


def _make_tree(tmp_path):
    data = tmp_path / "data" / "radionics"
    (data / "HOMEOPATHY").mkdir(parents=True)
    (data / "BIOLOGICAL").mkdir(parents=True)
    (data / "HOMEOPATHY" / "HOMEOPATHY_Clarke.txt").write_text(
        "Abrotanum\thttp://mm/abrotanum.htm\nAbsinthium\t\n\nAEsculus\n", encoding="utf-8"
    )
    (data / "HOMEOPATHY" / "HOMEOPATHY_Boericke.txt").write_text("Aconitum\n", encoding="utf-8")
    (data / "BIOLOGICAL" / "BIOLOGICAL_Flower.txt").write_text("Rose\n", encoding="utf-8")
    (data / "FUNCTION_ignore.txt").write_text("soll ignoriert werden\n", encoding="utf-8")
    (data / "skript.rscript").write_text("PRINT test\n", encoding="utf-8")
    return data


def test_refresh_finds_databases_and_scripts(tmp_path):
    repo = RateRepository(_make_tree(tmp_path))
    repo.refresh()
    names = repo.database_names()
    assert "HOMEOPATHY_Clarke" in names
    assert "HOMEOPATHY_Boericke" in names
    assert "BIOLOGICAL_Flower" in names
    assert not any(name.startswith("FUNCTION_") for name in names)
    assert "skript" in repo.script_names()


def test_prefix_matching_loads_all_matching_databases(tmp_path):
    repo = RateRepository(_make_tree(tmp_path))
    repo.refresh()
    rates = repo.find_all_by_source_name("HOMEOPATHY")
    names = {r.name for r in rates}
    assert {"Abrotanum", "Absinthium", "AEsculus", "Aconitum"} <= names


def test_exact_txt_lookup(tmp_path):
    repo = RateRepository(_make_tree(tmp_path))
    repo.refresh()
    rates = repo.find_all_by_source_name("HOMEOPATHY_Boericke.txt")
    assert [r.name for r in rates] == ["Aconitum"]


def test_url_splitting_by_tab(tmp_path):
    repo = RateRepository(_make_tree(tmp_path))
    repo.refresh()
    rates = repo.find_all_by_source_name("HOMEOPATHY_Clarke.txt")
    abrotanum = next(r for r in rates if r.name == "Abrotanum")
    assert abrotanum.url == "http://mm/abrotanum.htm"
    aesculus = next(r for r in rates if r.name == "AEsculus")
    assert aesculus.url is None


def test_missing_database_returns_empty(tmp_path):
    repo = RateRepository(tmp_path / "leer")
    repo.refresh()
    assert repo.find_all_by_source_name("NIX") == []
