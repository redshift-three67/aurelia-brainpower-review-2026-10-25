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
    (data / "HOMEOPATHY" / "HOMEOPATHY_Zeeden.txt").write_text("Zincum\n", encoding="utf-8")
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


def test_prefix_matching_uses_original_java_hashmap_database_order(tmp_path):
    repo = RateRepository(_make_tree(tmp_path))
    repo.refresh()

    rates = repo.find_all_by_source_name("HOMEOPATHY")

    # DataService.getAllDatabaseNames() iterates HashMap.keySet(), not a sort.
    assert [rate.name for rate in rates] == [
        "Aconitum",
        "Zincum",
        "Abrotanum",
        "Absinthium",
        "AEsculus",
    ]


def test_refresh_preserves_filesystem_enumeration_for_hashmap_collisions(tmp_path, monkeypatch):
    data = tmp_path / "data"
    data.mkdir()
    first = data / "HOMEOPATHY_Test_3.txt"
    second = data / "HOMEOPATHY_Test_12.txt"
    first.write_text("Three\n", encoding="utf-8")
    second.write_text("Twelve\n", encoding="utf-8")
    original_iterdir = type(data).iterdir

    def ordered_iterdir(path):
        if path == data:
            return iter((first, second))
        return original_iterdir(path)

    monkeypatch.setattr(type(data), "iterdir", ordered_iterdir)
    repo = RateRepository(data)
    repo.refresh()

    # Both names share the initial Java HashMap bucket; keySet keeps insertion order.
    assert [rate.name for rate in repo.find_all_by_source_name("HOMEOPATHY")] == [
        "Three",
        "Twelve",
    ]


def test_refresh_uses_original_depth_first_file_enumeration(tmp_path, monkeypatch):
    data = tmp_path / "data"
    nested = data / "HOMEOPATHY"
    nested.mkdir(parents=True)
    root_file = data / "Zeeden_V1.txt"
    nested_file = nested / "Zeeden_V1.txt"
    root_file.write_text("Root\n", encoding="utf-8")
    nested_file.write_text("Nested\n", encoding="utf-8")
    original_iterdir = type(data).iterdir

    def depth_first_iterdir(path):
        if path == data:
            return iter((nested, root_file))
        if path == nested:
            return iter((nested_file,))
        return original_iterdir(path)

    monkeypatch.setattr(type(data), "iterdir", depth_first_iterdir)
    repo = RateRepository(data)
    repo.refresh()

    # DataService recurses into HOMEOPATHY before continuing the root listing.
    assert [rate.name for rate in repo.find_all_by_source_name("Zeeden_V1.txt")] == ["Root"]


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
    assert abrotanum.analysis_key == "Abrotanum\thttp://mm/abrotanum.htm"
    aesculus = next(r for r in rates if r.name == "AEsculus")
    assert aesculus.url is None
    assert aesculus.analysis_key == "AEsculus"


def test_missing_database_returns_empty(tmp_path):
    repo = RateRepository(tmp_path / "leer")
    repo.refresh()
    assert repo.find_all_by_source_name("NIX") == []
