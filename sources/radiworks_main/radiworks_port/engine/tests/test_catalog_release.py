from pathlib import Path

import pytest

from radiworks.core.catalog_release import CatalogSnapshotError, publish_catalog_release
from radiworks.core.rates import RateRepository


def _source(tmp_path: Path) -> Path:
    source = tmp_path / "source"
    source.mkdir()
    (source / "HOMEOPATHY_A.txt").write_text("Alpha old\n", encoding="utf-8")
    (source / "HOMEOPATHY_B.txt").write_text("Beta old\n", encoding="utf-8")
    return source


def test_published_release_is_pinned_while_new_version_is_published(tmp_path: Path):
    source = _source(tmp_path)
    releases = tmp_path / "releases"
    first_dir = publish_catalog_release(source, releases)
    first = RateRepository(first_dir / "data")
    first.refresh()
    assert {rate.name for rate in first.find_all_fresh_by_source_name("HOMEOPATHY")} == {
        "Alpha old", "Beta old"
    }

    (source / "HOMEOPATHY_A.txt").write_text("Alpha new\n", encoding="utf-8")
    (source / "HOMEOPATHY_B.txt").write_text("Beta new\n", encoding="utf-8")
    second_dir = publish_catalog_release(source, releases)
    second = RateRepository(second_dir / "data")
    second.refresh()

    assert first.release_id != second.release_id
    assert {rate.name for rate in first.find_all_fresh_by_source_name("HOMEOPATHY")} == {
        "Alpha old", "Beta old"
    }
    assert {rate.name for rate in second.find_all_fresh_by_source_name("HOMEOPATHY")} == {
        "Alpha new", "Beta new"
    }


def test_published_release_rejects_mutation_and_extra_file(tmp_path: Path):
    source = _source(tmp_path)
    release_dir = publish_catalog_release(source, tmp_path / "releases")
    repo = RateRepository(release_dir / "data")
    repo.refresh()
    (release_dir / "data" / "HOMEOPATHY_B.txt").write_text("Tampered\n", encoding="utf-8")
    with pytest.raises(CatalogSnapshotError):
        repo.find_all_by_source_name("HOMEOPATHY")
    with pytest.raises(CatalogSnapshotError):
        repo.find_all_fresh_by_source_name("HOMEOPATHY")

    (release_dir / "data" / "HOMEOPATHY_B.txt").write_text("Beta old\n", encoding="utf-8")
    (release_dir / "data" / "HOMEOPATHY_C.txt").write_text("Extra\n", encoding="utf-8")
    with pytest.raises(CatalogSnapshotError):
        repo.find_all_fresh_by_source_name("HOMEOPATHY")


def test_release_without_manifest_fails_closed(tmp_path: Path):
    release_data = tmp_path / "releases" / "1234567890abcdef1234567890abcdef" / "data"
    release_data.mkdir(parents=True)
    (release_data / "HOMEOPATHY_A.txt").write_text("Unverified\n", encoding="utf-8")
    with pytest.raises(CatalogSnapshotError):
        RateRepository(release_data)


def test_release_root_name_is_not_a_safety_requirement(tmp_path: Path):
    source = _source(tmp_path)
    release_dir = publish_catalog_release(source, tmp_path / "catalog_versions")
    repo = RateRepository(release_dir / "data")
    repo.refresh()
    assert repo.release_id == release_dir.name
    assert {rate.name for rate in repo.find_all_by_source_name("HOMEOPATHY")} == {
        "Alpha old", "Beta old"
    }


def test_api_returns_conflict_when_published_catalog_is_modified(tmp_path: Path):
    from fastapi.testclient import TestClient
    from radiworks.main import create_app

    release_dir = publish_catalog_release(_source(tmp_path), tmp_path / "catalog_versions")
    app = create_app(
        base_dir=tmp_path / "runtime",
        data_dir=release_dir / "data",
        materia_dir=tmp_path / "empty",
    )
    with TestClient(app) as client:
        (release_dir / "data" / "HOMEOPATHY_B.txt").write_text("Tampered\n", encoding="utf-8")
        response = client.post("/analysis", json={"database": "HOMEOPATHY", "seed": 42})
        assert response.status_code == 409
        assert "Katalog" in response.text


def test_named_script_cannot_read_modified_published_bytes(tmp_path: Path):
    from fastapi.testclient import TestClient
    from radiworks.main import create_app

    source = _source(tmp_path)
    (source / "probe.rscript").write_text("PRINT old\n", encoding="utf-8")
    release_dir = publish_catalog_release(source, tmp_path / "catalog_versions")
    app = create_app(
        base_dir=tmp_path / "runtime",
        data_dir=release_dir / "data",
        materia_dir=tmp_path / "empty",
    )
    with TestClient(app) as client:
        (release_dir / "data" / "probe.rscript").write_text("PRINT changed\n", encoding="utf-8")
        response = client.get("/scripts/probe")
        assert response.status_code == 409
        assert "Katalog" in response.text


def test_stickpad_receipt_binds_published_release_id(tmp_path: Path):
    from fastapi.testclient import TestClient
    from radiworks.main import create_app

    release_dir = publish_catalog_release(_source(tmp_path), tmp_path / "releases")
    app = create_app(
        base_dir=tmp_path / "runtime",
        data_dir=release_dir / "data",
        materia_dir=tmp_path / "empty",
    )
    with TestClient(app) as client:
        assert client.post("/stickpad/position", json={"x": 640, "y": 400}).status_code == 200
        response = client.post("/stickpad/analyze", json={"database": "HOMEOPATHY"})
        assert response.status_code == 200
        catalog = response.json()["stickPadCapture"]["catalog"]
        assert catalog["releaseId"] == release_dir.name
        assert client.get("/stickpad").json()["catalogCheck"]["state"] == "current"


def test_analysis_passport_binds_catalog_release_without_changing_legacy_scheme(tmp_path: Path):
    from fastapi.testclient import TestClient

    from radiworks.main import create_app

    source = _source(tmp_path)
    first_dir = publish_catalog_release(source, tmp_path / "versions")
    second_dir = publish_catalog_release(source, tmp_path / "versions")
    hashes = []
    for index, release_dir in enumerate((first_dir, second_dir)):
        app = create_app(
            base_dir=tmp_path / f"runtime-{index}",
            data_dir=release_dir / "data",
            materia_dir=tmp_path / "empty",
        )
        with TestClient(app) as client:
            response = client.post("/analysis", json={"database": "HOMEOPATHY", "seed": 42})
            assert response.status_code == 200
            passport = response.json()["passport"]
            assert passport["input_hash_scheme"] == "analysis-request-catalog-v1"
            manifest = client.get("/manifest").json()
            passport_schema = manifest["operations"][0]["output_schema"]["properties"]["passport"]
            scheme_schema = passport_schema["properties"]["input_hash_scheme"]
            assert set(scheme_schema["enum"]) == {
                "analysis-request-v2", "analysis-request-catalog-v1",
            }
            assert passport["input_hash_scheme"] in scheme_schema["enum"]
            hashes.append(passport["input_hash"])
    assert hashes[0] != hashes[1]

    legacy_app = create_app(
        base_dir=tmp_path / "runtime-legacy",
        data_dir=source,
        materia_dir=tmp_path / "empty",
    )
    with TestClient(legacy_app) as client:
        response = client.post("/analysis", json={"database": "HOMEOPATHY", "seed": 42})
        assert response.status_code == 200
        assert response.json()["passport"]["input_hash_scheme"] == "analysis-request-v2"


def test_release_data_symlink_cannot_downgrade_to_legacy_mode(tmp_path: Path):
    import os

    source = _source(tmp_path)
    release_dir = publish_catalog_release(source, tmp_path / "versions")
    data = release_dir / "data"
    data.rename(release_dir / "saved-data")
    try:
        os.symlink(source, data, target_is_directory=True)
    except OSError as exc:
        pytest.skip(f"directory symlinks unavailable: {exc}")
    with pytest.raises(CatalogSnapshotError):
        RateRepository(data)


def test_release_path_redirect_is_rejected_before_resolution(tmp_path: Path, monkeypatch):
    import radiworks.core.catalog_release as catalog_module

    source = _source(tmp_path)
    release_dir = publish_catalog_release(source, tmp_path / "versions")
    data = release_dir / "data"
    original_redirected = catalog_module._redirected
    original_resolve = Path.resolve
    monkeypatch.setattr(
        catalog_module,
        "_redirected",
        lambda path: path == data or original_redirected(path),
    )
    monkeypatch.setattr(
        Path,
        "resolve",
        lambda path, *args, **kwargs: source if path == data else original_resolve(path, *args, **kwargs),
    )
    with pytest.raises(CatalogSnapshotError):
        RateRepository(data)


def test_alias_to_release_cannot_silently_use_legacy_mode(tmp_path: Path, monkeypatch):
    release_dir = publish_catalog_release(_source(tmp_path), tmp_path / "versions")
    alias = tmp_path / "current"
    original_resolve = Path.resolve
    monkeypatch.setattr(
        Path,
        "resolve",
        lambda path, *args, **kwargs: release_dir / "data"
        if path == alias else original_resolve(path, *args, **kwargs),
    )
    with pytest.raises(CatalogSnapshotError):
        RateRepository(alias)
