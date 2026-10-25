from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_local_operator_documentation_matches_loopback_deployment_boundary() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    runbook = (ROOT / "docs" / "LOCAL_OPERATOR_RUNBOOK.md").read_text(encoding="utf-8")

    for document in (readme, runbook):
        assert "127.0.0.1" in document
        assert "nicht für externen Mehrbenutzer" in document or "Nicht freigegeben" in document
        assert "web_server.py" in document

    assert "beendet niemals fremde Prozesse" in runbook
