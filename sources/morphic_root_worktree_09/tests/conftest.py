from __future__ import annotations

import pytest

from apps.web.security import _rate_limit_store
from services import harmonization_worker


@pytest.fixture(autouse=True)
def _reset_web_rate_limit_store() -> None:
    _rate_limit_store.clear()
    yield
    _rate_limit_store.clear()


@pytest.fixture(autouse=True)
def _isolate_harmonization_runtime(tmp_path, monkeypatch) -> None:
    jobs_dir = tmp_path / "harmonization_jobs"
    events_dir = jobs_dir / "events"
    monkeypatch.setenv("MORPHIC_HARMONIZATION_JOBS_DIR", str(jobs_dir))
    monkeypatch.setattr(harmonization_worker, "JOBS_DIR", jobs_dir)
    monkeypatch.setattr(harmonization_worker, "EVENTS_DIR", events_dir)
