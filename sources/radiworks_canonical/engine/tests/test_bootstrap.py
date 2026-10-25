"""Tests fuer den opt-in Preview-Katalog-Bootstrap."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from radiworks.bootstrap import SyntheticCatalogBootstrapError, bootstrap_synthetic_catalog
from radiworks.main import create_app


def test_bootstrap_creates_synthetic_catalog_for_clean_runtime_home(tmp_path: Path):
    catalog = bootstrap_synthetic_catalog(tmp_path)

    assert catalog == tmp_path / "data" / "radionics" / "HOMEOPATHY_Synthetic.txt"
    assert catalog.read_text(encoding="utf-8").splitlines() == [
        "Synthetic-Aurum",
        "Synthetic-Borealis",
        "Synthetic-Cirrus",
        "Synthetic-Deneb",
        "Synthetic-Equinox",
    ]

    with TestClient(create_app(base_dir=tmp_path)) as client:
        assert client.get("/databases").json() == {"databases": ["HOMEOPATHY_Synthetic"]}
        response = client.post(
            "/analysis",
            json={"database": "HOMEOPATHY_Synthetic", "seed": 42},
        )
    assert response.status_code == 200
    assert response.json()["result"]["rateObjects"]


def test_bootstrap_rejects_external_operator_catalog(tmp_path: Path):
    external = tmp_path / "operator-catalog"
    external.mkdir()
    sentinel = external / "operator.txt"
    sentinel.write_text("do not change\n", encoding="utf-8")

    with pytest.raises(SyntheticCatalogBootstrapError, match="RADIOWORKS_DATA_DIR"):
        bootstrap_synthetic_catalog(tmp_path / "home", external_data_dir=external)

    assert sentinel.read_text(encoding="utf-8") == "do not change\n"
    assert not (tmp_path / "home" / "data").exists()


@pytest.mark.parametrize("existing_name", ["existing.txt", "existing.rscript"])
def test_bootstrap_never_overwrites_an_existing_catalog(tmp_path: Path, existing_name: str):
    target = tmp_path / "data" / "radionics" / existing_name
    target.parent.mkdir(parents=True)
    target.write_text("operator content\n", encoding="utf-8")

    with pytest.raises(SyntheticCatalogBootstrapError, match="ueberschreibt keine Daten"):
        bootstrap_synthetic_catalog(tmp_path)

    assert target.read_text(encoding="utf-8") == "operator content\n"


def test_repeated_bootstrap_leaves_the_first_catalog_unchanged(tmp_path: Path):
    catalog = bootstrap_synthetic_catalog(tmp_path)
    original = catalog.read_bytes()

    with pytest.raises(SyntheticCatalogBootstrapError, match="ueberschreibt keine Daten"):
        bootstrap_synthetic_catalog(tmp_path)

    assert catalog.read_bytes() == original


def test_run_cli_bootstraps_only_the_runtime_home(tmp_path: Path, monkeypatch):
    run_path = Path(__file__).parents[1] / "run.py"
    spec = importlib.util.spec_from_file_location("radiworks_run", run_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    started = {}

    monkeypatch.setenv("RADIOWORKS_HOME", str(tmp_path))
    monkeypatch.delenv("RADIOWORKS_DATA_DIR", raising=False)
    monkeypatch.setattr(sys, "argv", ["run.py", "--bootstrap-synthetic-catalog", "--port", "9999"])
    monkeypatch.setattr(module.uvicorn, "run", lambda app, **kwargs: started.update(kwargs))

    module.main()

    assert (tmp_path / "data" / "radionics" / "HOMEOPATHY_Synthetic.txt").is_file()
    assert started == {"host": "127.0.0.1", "port": 9999}
