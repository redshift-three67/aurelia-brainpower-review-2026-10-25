"""Test-Konfiguration: App mit isoliertem Heimatverzeichnis + Beispieldaten."""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from radiworks.main import create_app
from radiworks.api.routes import STATE


@pytest.fixture()
def home(tmp_path: Path):
    """Isolierte Engine-Instanz mit kleinen Beispieldaten."""
    data = tmp_path / "data" / "radionics"
    data.mkdir(parents=True)
    (data / "HOMEOPATHY_Test.txt").write_text(
        "Abrotanum\thttp://mm/abrotanum.htm\n"
        "Absinthium\n"
        "AEsculus\n"
        "Aconitum\n"
        "Arnica\n",
        encoding="utf-8",
    )
    (data / "beispiel.rscript").write_text(
        "## Beispiel (PEGGOTTY)\nziel = ANALYZE HOMEOPATHY_Test\nPRINT ziel\nPRINT Ende.\n",
        encoding="utf-8",
    )
    materia = tmp_path / "materiaMedica" / "Clarke"
    materia.mkdir(parents=True)
    (materia / "Abrotanum.json").write_text(
        '{"remedyName": "Abrotanum", "remedyAlternativeNames": "Southernwood",'
        ' "categories": {"Clinical": ["Haarausfall", "Gelenkschmerz"]}}',
        encoding="utf-8",
    )
    (materia / "Absinthium.json").write_text(
        '{"remedyName": "Absinthium", "remedyAlternativeNames": "Wormwood",'
        ' "categories": {"Clinical": ["Epilepsie"]}}',
        encoding="utf-8",
    )
    webapp = tmp_path / "webapp"
    webapp.mkdir()
    (webapp / "index.html").write_text("<!doctype html><title>RadiWorks</title>", encoding="utf-8")

    app = create_app(
        base_dir=tmp_path,
        data_dir=data,
        cases_dir=tmp_path / "cases",
        drafts_dir=tmp_path / "drafts",
        materia_dir=materia,
        webapp_dir=webapp,
    )
    with TestClient(app) as client:
        assert STATE.state is not None
        yield client
    STATE.state = None
