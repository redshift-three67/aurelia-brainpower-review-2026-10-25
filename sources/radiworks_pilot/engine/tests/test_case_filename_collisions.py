"""Fall-Dateinamen dürfen weder andere Namen noch andere Scopes überschreiben."""

import pytest

from radiworks.core.cases import CaseNameError, CaseStore
from radiworks.scope import ScopeContext


def test_distinct_display_names_with_same_filename_do_not_overwrite(tmp_path):
    store = CaseStore(tmp_path)
    store.save({"name": "QA A B", "description": "erster Fall"})

    with pytest.raises(CaseNameError, match="kollidiert"):
        store.save({"name": "QA AB", "description": "zweiter Fall"})

    assert store.load("QA A B")["description"] == "erster Fall"
    assert store.current["name"] == "QA A B"


def test_same_name_can_update_its_existing_case(tmp_path):
    store = CaseStore(tmp_path)
    store.save({"name": "QA A B", "description": "vorher"})
    store.save({"name": "QA A B", "description": "nachher"})

    assert store.load("QA A B")["description"] == "nachher"


def test_existing_other_scope_is_not_overwritten(tmp_path):
    first = CaseStore(tmp_path, scope=ScopeContext("tenant-a", "client", "job"))
    second = CaseStore(tmp_path, scope=ScopeContext("tenant-b", "client", "job"))
    first.save({"name": "Gemeinsamer Name", "description": "tenant-a"})

    with pytest.raises(CaseNameError, match="kollidiert"):
        second.save({"name": "Gemeinsamer Name", "description": "tenant-b"})

    assert first.load("Gemeinsamer Name")["description"] == "tenant-a"
