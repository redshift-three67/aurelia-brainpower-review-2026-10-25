from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DOC = ROOT / "docs" / "QUELLEN_REGISTRY_BEWERTUNG_20260628.md"
STABILIZATION_MATRIX = ROOT / "docs" / "STABILIZATION_TEST_MATRIX.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_source_documentation_states_actual_registry_boundaries() -> None:
    source_doc = _read(SOURCE_DOC)
    matrix = _read(STABILIZATION_MATRIX)

    assert "keine Host-Allowlist" in source_doc
    assert "HTTPS-Allowlist" not in source_doc
    assert "HTTPS-Allowlist" not in matrix

    assert "JSON-Read-Modify-Write" in source_doc
    assert "nicht technisch append-only" in source_doc
    assert "technisch append-only" not in matrix

    assert "Ledger-only" in source_doc
    assert "keine fachliche Datenpromotion" in source_doc
    assert "keine fachliche Datenpromotion" in matrix

    active_boundary = (
        "Metadatenstatus `active` ist keine Adapterfreigabe, kein Fetch, "
        "kein Publish und keine Runtime-Aktivierung"
    )
    assert active_boundary in source_doc
    assert active_boundary in matrix


def test_source_documentation_examples_keep_staging_approval_registry_and_rollback_boundaries() -> None:
    source_doc = _read(SOURCE_DOC)

    assert "sources stage" in source_doc
    assert "--approval-id" in source_doc
    assert "--registry C:\\Pfad\\source_repositories.v1.json" in source_doc
    assert "sources import-plan" in source_doc
    assert "sources rollback" in source_doc
    assert "kein Catalog-Publish" in source_doc
