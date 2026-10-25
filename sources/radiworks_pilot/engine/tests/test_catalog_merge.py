"""Legacy catalog intake must preserve a pinned base and expose collisions."""

from pathlib import Path

import pytest

from radiworks.core.catalog_merge import merge_catalog
from radiworks.core.catalog_release import CatalogSnapshotError


def test_merge_keeps_base_and_namespaces_distinct_legacy_files(tmp_path: Path):
    base = tmp_path / "base"
    old = tmp_path / "old"
    target = tmp_path / "target"
    base.mkdir()
    (base / "Datalists.txt").write_text("Current\n", encoding="utf-8")
    (base / "Known.txt").write_text("Same\n", encoding="utf-8")
    (old / "HOMEOPATHY").mkdir(parents=True)
    (old / "Known.txt").write_text("Same\n", encoding="utf-8")
    (old / "Datalists.txt").write_text("Older\n", encoding="utf-8")
    (old / "Zeeden_V1.txt").write_text("Root\n", encoding="utf-8")
    (old / "HOMEOPATHY" / "Zeeden_V1.txt").write_text("Nested\n", encoding="utf-8")
    (old / "HOMEOPATHY" / "Extra.txt").write_bytes("Gr\xfcne\n".encode("latin-1"))

    report = merge_catalog(base, old, target)

    assert (target / "Datalists.txt").read_text(encoding="utf-8") == "Current\n"
    assert (target / "Known.txt").read_text(encoding="utf-8") == "Same\n"
    assert (target / "Zeeden_V1.txt").read_text(encoding="utf-8") == "Root\n"
    assert (target / "HOMEOPATHY" / "HOMEOPATHY_Zeeden_V1.txt").read_text(encoding="utf-8") == "Nested\n"
    assert (target / "HOMEOPATHY" / "Extra.txt").read_text(encoding="utf-8") == "Grüne\n"
    assert report["added"] == 3
    assert report["same"] == 1
    assert report["conflicts"] == 1
    assert report["transcoded"] == 1
    assert (old / "HOMEOPATHY" / "Extra.txt").read_bytes() == "Gr\xfcne\n".encode("latin-1")


def test_merge_rejects_target_resolving_inside_a_source(tmp_path: Path):
    base = tmp_path / "base"
    old = tmp_path / "old"
    base.mkdir()
    old.mkdir()
    (base / "Known.txt").write_text("Keep\n", encoding="utf-8")
    alias = tmp_path / "alias"
    try:
        alias.symlink_to(base, target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("Directory symlinks unavailable on this Windows host")
    with pytest.raises(CatalogSnapshotError):
        merge_catalog(base, old, alias / "new")
    assert not (base / "new").exists()
