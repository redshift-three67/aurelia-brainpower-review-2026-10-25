from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

from core.admin_catalog.contracts import CatalogContext
from core.admin_catalog.paths import (
    CATALOG_DATABASE_FILENAME,
    admin_catalog_root,
    catalog_database_path,
    context_namespace,
)
from core.compliance.runtime_manifest import runtime_root


def _context(**overrides: str) -> CatalogContext:
    values = {
        "operator_id": "operator-a",
        "workspace_id": "workspace-a",
        "tenant_id": "tenant-a",
        "scope": "workspace",
    }
    values.update(overrides)
    return CatalogContext(**values)


def test_root_uses_explicit_environment_override(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    configured = tmp_path / "catalog-root"
    monkeypatch.setenv("MORPHIC_ADMIN_CATALOG_DIR", str(configured))
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "ignored-local-app-data"))

    assert admin_catalog_root() == configured.resolve()
    assert configured.exists() is False


def test_root_defaults_to_dedicated_local_app_data_directory(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    local_app_data = tmp_path / "LocalAppData"
    monkeypatch.delenv("MORPHIC_ADMIN_CATALOG_DIR", raising=False)
    monkeypatch.setenv("LOCALAPPDATA", str(local_app_data))

    assert admin_catalog_root() == (local_app_data / "MorphicEngine" / "admin_catalog").resolve()


def test_root_fails_closed_without_override_or_local_app_data(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("MORPHIC_ADMIN_CATALOG_DIR", raising=False)
    monkeypatch.delenv("LOCALAPPDATA", raising=False)

    with pytest.raises(RuntimeError, match="LOCALAPPDATA"):
        admin_catalog_root()


def test_admin_catalog_default_never_uses_runtime_root(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    runtime = tmp_path / "runtime"
    local_app_data = tmp_path / "LocalAppData"
    monkeypatch.setenv("MORPHIC_RUNTIME_DIR", str(runtime))
    monkeypatch.delenv("MORPHIC_ADMIN_CATALOG_DIR", raising=False)
    monkeypatch.setenv("LOCALAPPDATA", str(local_app_data))

    assert runtime_root() == runtime
    assert admin_catalog_root() != runtime_root()
    assert admin_catalog_root() == (local_app_data / "MorphicEngine" / "admin_catalog").resolve()


@pytest.mark.parametrize(
    "configured",
    ["relative/catalog", "../escape", "safe/../escape"],
)
def test_root_rejects_relative_or_traversing_configuration(
    monkeypatch: pytest.MonkeyPatch, configured: str
) -> None:
    monkeypatch.setenv("MORPHIC_ADMIN_CATALOG_DIR", configured)

    with pytest.raises(ValueError, match="absolute|traversal"):
        admin_catalog_root()


def test_context_namespace_is_canonical_stable_and_component_bound() -> None:
    first = _context(
        operator_id="operator-a.b",
        workspace_id="workspace-c",
        tenant_id="tenant-d",
    )
    delimiter_collision_attempt = _context(
        operator_id="operator-a",
        workspace_id="workspace-b.c",
        tenant_id="tenant-d",
    )

    assert context_namespace(first) == context_namespace(first)
    assert context_namespace(first) != context_namespace(delimiter_collision_attempt)
    assert context_namespace(first).startswith("ctx-v1-")
    assert len(context_namespace(first)) == len("ctx-v1-") + 64
    assert set(context_namespace(first)) <= set("abcdefghijklmnopqrstuvwxyz0123456789-")


def test_context_namespace_binds_every_context_dimension() -> None:
    baseline = _context()

    namespaces = {
        context_namespace(baseline),
        context_namespace(_context(operator_id="operator-b")),
        context_namespace(_context(workspace_id="workspace-b")),
        context_namespace(_context(tenant_id="tenant-b")),
        context_namespace(_context(scope="tenant")),
    }

    assert len(namespaces) == 5


def test_database_path_is_context_isolated_and_does_not_create_directories(tmp_path: Path) -> None:
    root = tmp_path / "catalog-root"

    first = catalog_database_path(_context(), root=root)
    second = catalog_database_path(_context(tenant_id="tenant-b"), root=root)

    assert first == root.resolve() / context_namespace(_context()) / CATALOG_DATABASE_FILENAME
    assert second == root.resolve() / context_namespace(_context(tenant_id="tenant-b")) / CATALOG_DATABASE_FILENAME
    assert first != second
    assert root.exists() is False


def test_system_scope_is_not_writable_by_default(tmp_path: Path) -> None:
    context = _context(scope="system")

    with pytest.raises(PermissionError, match="system"):
        catalog_database_path(context, root=tmp_path / "catalog-root")

    readonly_path = catalog_database_path(
        context,
        root=tmp_path / "catalog-root",
        writable=False,
    )
    assert readonly_path.name == CATALOG_DATABASE_FILENAME


def test_root_inside_project_is_rejected(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    configured = project_root / "data" / "admin-catalog"

    with pytest.raises(ValueError, match="project"):
        catalog_database_path(
            _context(),
            root=configured,
            project_root=project_root,
            blocked_roots=(),
        )


def test_root_overlapping_project_is_rejected(tmp_path: Path) -> None:
    broad_root = tmp_path
    project_root = tmp_path / "project"

    with pytest.raises(ValueError, match="project"):
        catalog_database_path(
            _context(),
            root=broad_root,
            project_root=project_root,
            blocked_roots=(),
        )


def test_root_inside_or_overlapping_export_archive_root_is_rejected(tmp_path: Path) -> None:
    archive_root = tmp_path / "Benutzer_Archive_Start"

    with pytest.raises(ValueError, match="export|archive"):
        catalog_database_path(
            _context(),
            root=archive_root / "catalog",
            project_root=tmp_path / "project",
            blocked_roots=(archive_root,),
        )
    with pytest.raises(ValueError, match="export|archive"):
        catalog_database_path(
            _context(),
            root=tmp_path,
            project_root=tmp_path.parent / "different-project-root",
            blocked_roots=(archive_root,),
        )


@pytest.mark.skipif(os.name != "nt", reason="Windows default archive roots are platform-specific")
def test_windows_default_export_archive_roots_are_blocked() -> None:
    with pytest.raises(ValueError, match="export|archive"):
        catalog_database_path(
            _context(),
            root=Path(r"C:\Benutzer_Archive_Start") / "admin_catalog",
        )


@pytest.mark.skipif(os.name != "nt", reason="Windows tenant archive roots are platform-specific")
@pytest.mark.parametrize(
    "root_name",
    [
        "Benutzer_Archive_Start",
        "Benutzer_Deutung_Start",
        "Benutzer_Remedies_Start",
        "Benutzer_Synergy_Start",
        "Benutzer_Trends_Start",
        "benutzer_archive_start",
        "BENUTZER_SYNERGY_START",
    ],
)
def test_windows_tenant_export_archive_roots_are_blocked(root_name: str) -> None:
    with pytest.raises(ValueError, match="export|archive"):
        catalog_database_path(
            _context(),
            root=Path(f"C:/{root_name}__tenant-123/admin_catalog"),
        )


@pytest.mark.parametrize("position", ["equal", "inside", "above"])
def test_parallel_export_root_is_blocked_by_default(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    position: str,
) -> None:
    parallel_root = tmp_path / "parallel-export"
    catalog_root = {
        "equal": parallel_root,
        "inside": parallel_root / "admin-catalog",
        "above": tmp_path,
    }[position]
    monkeypatch.setenv("MORPHIC_PARALLEL_EXPORT_ROOT", str(parallel_root))

    with pytest.raises(ValueError, match="export|archive"):
        catalog_database_path(
            _context(),
            root=catalog_root,
            project_root=tmp_path.parent / "separate-project",
        )


@pytest.mark.parametrize("position", ["equal", "inside", "above"])
def test_explicit_blocked_roots_cannot_disable_parallel_export_root(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    position: str,
) -> None:
    parallel_root = tmp_path / "parallel-export"
    catalog_root = {
        "equal": parallel_root,
        "inside": parallel_root / "admin-catalog",
        "above": tmp_path,
    }[position]
    monkeypatch.setenv("MORPHIC_PARALLEL_EXPORT_ROOT", str(parallel_root))

    with pytest.raises(ValueError, match="export|archive"):
        catalog_database_path(
            _context(),
            root=catalog_root,
            project_root=tmp_path.parent / "separate-project",
            blocked_roots=(),
        )


@pytest.mark.parametrize("configured", ["relative/export", "../escape", "safe/../escape"])
def test_invalid_parallel_export_root_configuration_fails_closed(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    configured: str,
) -> None:
    monkeypatch.setenv("MORPHIC_PARALLEL_EXPORT_ROOT", configured)

    with pytest.raises(ValueError, match="export|archive|absolute|traversal"):
        catalog_database_path(
            _context(),
            root=tmp_path / "catalog-root",
            project_root=tmp_path.parent / "separate-project",
        )


@pytest.mark.parametrize("configured", ["relative/export", "../escape", "safe/../escape"])
def test_invalid_parallel_export_root_fails_closed_with_explicit_blocked_roots(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    configured: str,
) -> None:
    monkeypatch.setenv("MORPHIC_PARALLEL_EXPORT_ROOT", configured)

    with pytest.raises(ValueError, match="export|archive|absolute|traversal"):
        catalog_database_path(
            _context(),
            root=tmp_path / "catalog-root",
            project_root=tmp_path.parent / "separate-project",
            blocked_roots=(tmp_path.parent / "additional-blocked-root",),
        )


def test_symlink_escape_from_context_namespace_is_rejected(tmp_path: Path) -> None:
    root = tmp_path / "catalog-root"
    outside = tmp_path / "outside"
    root.mkdir()
    outside.mkdir()
    link = root / context_namespace(_context())
    try:
        link.symlink_to(outside, target_is_directory=True)
    except OSError as exc:
        pytest.skip(f"directory symlinks unavailable: {exc}")

    with pytest.raises(ValueError, match="reparse|symlink|escape"):
        catalog_database_path(
            _context(),
            root=root,
            project_root=tmp_path / "project",
            blocked_roots=(),
        )


@pytest.mark.skipif(os.name != "nt", reason="Windows junction contract")
def test_windows_junction_escape_from_context_namespace_is_rejected(tmp_path: Path) -> None:
    root = tmp_path / "catalog-root"
    outside = tmp_path / "outside"
    root.mkdir()
    outside.mkdir()
    junction = root / context_namespace(_context())
    created = subprocess.run(
        ["cmd.exe", "/c", "mklink", "/J", str(junction), str(outside)],
        capture_output=True,
        check=False,
    )
    if created.returncode != 0:
        pytest.skip("Windows junction creation unavailable")
    try:
        with pytest.raises(ValueError, match="reparse|symlink|escape"):
            catalog_database_path(
                _context(),
                root=root,
                project_root=tmp_path / "project",
                blocked_roots=(),
            )
    finally:
        junction.rmdir()


@pytest.mark.skipif(os.name != "nt", reason="Windows dangling junction contract")
def test_windows_dangling_junction_is_rejected(tmp_path: Path) -> None:
    missing_target = tmp_path / "missing-target"
    junction = tmp_path / "catalog-root-junction"
    created = subprocess.run(
        ["cmd.exe", "/c", "mklink", "/J", str(junction), str(missing_target)],
        capture_output=True,
        check=False,
    )
    if created.returncode != 0:
        pytest.skip("Windows dangling junction creation unavailable")
    try:
        assert missing_target.exists() is False
        with pytest.raises(ValueError, match="reparse|symlink|escape"):
            catalog_database_path(
                _context(),
                root=junction,
                project_root=tmp_path / "project",
                blocked_roots=(),
            )
    finally:
        junction.rmdir()
