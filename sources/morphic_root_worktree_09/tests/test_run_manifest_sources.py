from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path

import pytest

from core.compliance.run_manifest_sources import collect_source_hashes, resolve_git_commit


def test_collect_source_hashes_is_sorted_and_changes_with_synthetic_content(tmp_path: Path) -> None:
    profile = tmp_path / "profile.json"
    data = tmp_path / "groups.json"
    profile.write_text('{"profile": "synthetic"}\n', encoding="utf-8")
    data.write_text('{"groups": []}\n', encoding="utf-8")

    first = collect_source_hashes(
        profile_sources={"profile_catalog": profile},
        data_sources={"group_catalog": data},
    )
    data.write_text('{"groups": ["changed"]}\n', encoding="utf-8")
    second = collect_source_hashes(
        profile_sources={"profile_catalog": profile},
        data_sources={"group_catalog": data},
    )

    assert list(first["profile_hashes"]) == ["profile_catalog"]
    assert list(first["data_hashes"]) == ["group_catalog"]
    assert first["profile_hashes"]["profile_catalog"] == hashlib.sha256(profile.read_bytes()).hexdigest()
    assert first["data_hashes"]["group_catalog"] != second["data_hashes"]["group_catalog"]


def test_collect_source_hashes_rejects_missing_sources(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="source file"):
        collect_source_hashes(profile_sources={"missing": tmp_path / "missing.json"})


def test_resolve_git_commit_reads_a_real_temporary_repository(tmp_path: Path) -> None:
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    (tmp_path / "manifest.txt").write_text("synthetic\n", encoding="utf-8")
    subprocess.run(["git", "add", "manifest.txt"], cwd=tmp_path, check=True)
    subprocess.run(
        ["git", "-c", "user.name=Synthetic", "-c", "user.email=synthetic@example.invalid", "commit", "-qm", "synthetic"],
        cwd=tmp_path,
        check=True,
    )

    commit = resolve_git_commit(tmp_path)

    assert len(commit) == 40
    assert int(commit, 16) >= 0
