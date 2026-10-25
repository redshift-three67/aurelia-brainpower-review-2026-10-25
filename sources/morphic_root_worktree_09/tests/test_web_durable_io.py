from __future__ import annotations

import ctypes
import json
import os
import stat
import subprocess
import sys
import threading
from ctypes import wintypes
from pathlib import Path
from types import SimpleNamespace

import pytest

from apps.web import durable_io
from apps.web import scan_jobs as scan_jobs_module
from apps.web import workbench_runtime as workbench_runtime_module
from apps.web.scan_jobs import LocalScanJobService
from apps.web.workbench_runtime import WorkbenchRuntimeStore
from core.profile_sync import (
    SCAN_PROCESS_GATE_NONCE_ENV,
    SCAN_PROCESS_GATE_PROOF_ENV,
    SCAN_PROFILE_POOL_FINGERPRINT_ENV,
    build_scan_process_gate_proof,
)
from services import harmonization_worker as worker
from services import scan_process_gate
from services.harmonization_worker import HarmonizationJob


class _FakeWindowsError(OSError):
    def __init__(self, winerror: int) -> None:
        super().__init__(f"fake Windows error {winerror}")
        self.winerror = winerror


class _FakeKernelFunction:
    def __init__(self, callback) -> None:
        self.callback = callback
        self.argtypes = None
        self.restype = None

    def __call__(self, *args):
        return self.callback(*args)


class _FakeDirectoryKernel32:
    def __init__(
        self,
        *,
        create_handle: int = 101,
        create_error: int = 6,
        flush_error: int | None = None,
        information_error: int | None = None,
        close_error: int | None = None,
        attributes: int = 0x10,
    ) -> None:
        self.create_handle = create_handle
        self.create_error = create_error
        self.flush_error = flush_error
        self.information_error = information_error
        self.close_error = close_error
        self.attributes = attributes
        self.last_error = 0
        self.create_calls: list[tuple[object, ...]] = []
        self.flush_calls: list[int] = []
        self.close_calls: list[int] = []
        self.information_calls: list[int] = []
        self.CreateFileW = _FakeKernelFunction(self._create_file)
        self.GetFileInformationByHandleEx = _FakeKernelFunction(self._get_information)
        self.FlushFileBuffers = _FakeKernelFunction(self._flush)
        self.CloseHandle = _FakeKernelFunction(self._close)

    def _create_file(self, *args):
        self.create_calls.append(args)
        invalid = wintypes.HANDLE(-1).value
        if self.create_handle == invalid:
            self.last_error = self.create_error
        return self.create_handle

    def _get_information(self, handle, information_class, information, size):
        self.information_calls.append(int(handle))
        if self.information_error is not None:
            self.last_error = self.information_error
            return False
        fields = ctypes.cast(information, ctypes.POINTER(ctypes.c_uint32))
        fields[0] = self.attributes
        fields[1] = 0
        return True

    def _flush(self, handle):
        self.flush_calls.append(int(handle))
        if self.flush_error is None:
            return True
        self.last_error = self.flush_error
        return False

    def _close(self, handle):
        self.close_calls.append(int(handle))
        if self.close_error is not None:
            self.last_error = self.close_error
            return False
        return True


def _install_fake_directory_kernel(
    monkeypatch: pytest.MonkeyPatch,
    **options,
) -> _FakeDirectoryKernel32:
    kernel = _FakeDirectoryKernel32(**options)
    monkeypatch.setattr(ctypes, "WinDLL", lambda *args, **kwargs: kernel)
    monkeypatch.setattr(ctypes, "get_last_error", lambda: kernel.last_error)
    monkeypatch.setattr(ctypes, "WinError", lambda error: _FakeWindowsError(error))
    return kernel


def _install_posix_directory_io(
    monkeypatch: pytest.MonkeyPatch,
    trace: list[tuple[str, Path]],
    *,
    failure: tuple[str, Path] | None = None,
) -> None:
    original_mkdir = os.mkdir
    original_open = os.open
    original_fsync = os.fsync
    original_close = os.close
    descriptors: dict[int, Path] = {}
    next_descriptor = iter(range(10_000, 20_000))
    current_component: Path | None = None

    monkeypatch.setattr(durable_io, "_IS_WINDOWS", False, raising=False)

    def mkdir(path, mode=0o777, *, dir_fd=None):
        nonlocal current_component
        candidate = Path(path)
        trace.append(("mkdir", candidate))
        if failure == ("mkdir", candidate):
            raise OSError("injected mkdir failure")
        result = original_mkdir(path, mode, dir_fd=dir_fd)
        current_component = candidate
        return result

    def open_directory(path, flags, mode=0o777, *, dir_fd=None):
        candidate = Path(path)
        if not candidate.is_dir():
            return original_open(path, flags, mode, dir_fd=dir_fd)
        role = "parent" if current_component is not None and candidate == current_component.parent else "child"
        operation = f"open_{role}"
        trace.append((operation, current_component or candidate))
        if current_component is not None and failure == (operation, current_component):
            raise OSError(f"injected {operation} failure")
        descriptor = next(next_descriptor)
        descriptors[descriptor] = candidate
        return descriptor

    def fsync(descriptor: int) -> None:
        candidate = descriptors.get(descriptor)
        if candidate is None:
            original_fsync(descriptor)
            return
        role = "parent" if current_component is not None and candidate == current_component.parent else "child"
        operation = f"fsync_{role}"
        trace.append((operation, current_component or candidate))
        if current_component is not None and failure == (operation, current_component):
            raise OSError(f"injected {operation} failure")

    def close(descriptor: int) -> None:
        candidate = descriptors.pop(descriptor, None)
        if candidate is None:
            original_close(descriptor)
            return
        role = "parent" if current_component is not None and candidate == current_component.parent else "child"
        trace.append((f"close_{role}", current_component or candidate))

    monkeypatch.setattr(durable_io.os, "mkdir", mkdir)
    monkeypatch.setattr(durable_io.os, "open", open_directory)
    monkeypatch.setattr(durable_io.os, "fsync", fsync)
    monkeypatch.setattr(durable_io.os, "close", close)


def test_durable_mkdir_parents_persists_each_posix_component_in_order(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    target = tmp_path / "first" / "second" / "third"
    trace: list[tuple[str, Path]] = []
    _install_posix_directory_io(monkeypatch, trace)

    durable_io.durable_mkdir_parents(target)

    components = [tmp_path / "first", tmp_path / "first" / "second", target]
    assert trace == [
        item
        for component in components
        for item in (
            ("mkdir", component),
            ("open_parent", component),
            ("fsync_parent", component),
            ("close_parent", component),
            ("open_child", component),
            ("fsync_child", component),
            ("close_child", component),
        )
    ]


@pytest.mark.parametrize(
    "operation",
    ("mkdir", "open_parent", "fsync_parent", "open_child", "fsync_child"),
)
@pytest.mark.parametrize("failure_index", range(3))
def test_posix_parent_fault_stops_before_deeper_component_and_publication(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    operation: str,
    failure_index: int,
) -> None:
    components = [
        tmp_path / "first",
        tmp_path / "first" / "second",
        tmp_path / "first" / "second" / "third",
    ]
    destination = components[-1] / "authority.json"
    trace: list[tuple[str, Path]] = []
    _install_posix_directory_io(
        monkeypatch,
        trace,
        failure=(operation, components[failure_index]),
    )

    with pytest.raises(OSError, match="injected"):
        durable_io.durable_write_bytes(destination, b"authority\n")

    assert not destination.exists()
    assert list(tmp_path.rglob("authority.json.tmp.*")) == []
    assert all(not path.exists() for path in components[failure_index + 1 :])


def test_posix_retry_redurabilizes_existing_component_before_publication(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    parent = tmp_path / "authority-parent"
    destination = parent / "state.json"
    trace: list[tuple[str, Path]] = []
    fail_child_once = True

    def fsync_directory(path: Path) -> None:
        nonlocal fail_child_once
        candidate = Path(path)
        trace.append(("fsync", candidate))
        if candidate == parent and fail_child_once:
            fail_child_once = False
            raise OSError("injected child fsync failure")

    def publish(source: Path, target: Path) -> None:
        trace.append(("publish", Path(target)))
        os.replace(source, target)

    monkeypatch.setattr(durable_io, "_IS_WINDOWS", False)
    monkeypatch.setattr(durable_io, "_fsync_directory", fsync_directory)
    monkeypatch.setattr(durable_io, "_publish_durable", publish)

    with pytest.raises(OSError, match="child fsync failure"):
        durable_io.durable_write_bytes(destination, b"first\n")

    assert parent.is_dir()
    assert not destination.exists()
    assert trace == [("fsync", tmp_path), ("fsync", parent)]

    durable_io.durable_write_bytes(destination, b"second\n")

    assert trace == [
        ("fsync", tmp_path),
        ("fsync", parent),
        ("fsync", tmp_path),
        ("fsync", parent),
        ("publish", destination),
    ]
    assert destination.read_bytes() == b"second\n"


@pytest.mark.parametrize("failure_index", (0, 1))
def test_posix_three_level_retry_redurabilizes_ancestor_before_next_mkdir(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    failure_index: int,
) -> None:
    components = [
        tmp_path / "first",
        tmp_path / "first" / "second",
        tmp_path / "first" / "second" / "third",
    ]
    destination = components[-1] / "authority.json"
    trace: list[tuple[str, Path]] = []
    original_mkdir = durable_io.os.mkdir
    current_component: Path | None = None
    failed = False

    def mkdir(path, mode=0o777, *, dir_fd=None):
        nonlocal current_component
        current_component = Path(path)
        trace.append(("mkdir", current_component))
        return original_mkdir(path, mode, dir_fd=dir_fd)

    def fsync_directory(path: Path) -> None:
        nonlocal failed
        candidate = Path(path)
        trace.append(("fsync", candidate))
        if (
            not failed
            and current_component == components[failure_index]
            and candidate == components[failure_index].parent
        ):
            failed = True
            raise OSError("injected ancestor parent fsync failure")

    def publish(source: Path, target: Path) -> None:
        trace.append(("publish", Path(target)))
        os.replace(source, target)

    monkeypatch.setattr(durable_io, "_IS_WINDOWS", False)
    monkeypatch.setattr(durable_io.os, "mkdir", mkdir)
    monkeypatch.setattr(durable_io, "_fsync_directory", fsync_directory)
    monkeypatch.setattr(durable_io, "_publish_durable", publish)

    with pytest.raises(OSError, match="ancestor parent fsync failure"):
        durable_io.durable_write_bytes(destination, b"first\n")

    assert components[failure_index].is_dir()
    assert all(not path.exists() for path in components[failure_index + 1 :])
    assert not destination.exists()

    durable_io.durable_write_bytes(destination, b"second\n")

    expected: list[tuple[str, Path]] = []
    for index in range(failure_index + 1):
        component = components[index]
        expected.extend((("mkdir", component), ("fsync", component.parent)))
        if index < failure_index:
            expected.append(("fsync", component))
    ancestor = components[failure_index]
    expected.extend((("fsync", ancestor.parent), ("fsync", ancestor)))
    for component in components[failure_index + 1 :]:
        expected.extend(
            (
                ("mkdir", component),
                ("fsync", component.parent),
                ("fsync", component),
            )
        )
    expected.append(("publish", destination))
    assert trace == expected


def test_durable_mkdir_parents_revalidates_and_flushes_a_concurrent_creator(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    target = tmp_path / "shared"
    trace: list[tuple[str, Path]] = []
    _install_posix_directory_io(monkeypatch, trace)
    installed_mkdir = durable_io.os.mkdir
    original_require = durable_io._require_directory_component
    raced = False

    def concurrent_mkdir(path, mode=0o777, *, dir_fd=None):
        nonlocal raced
        candidate = Path(path)
        if candidate == target and not raced:
            raced = True
            installed_mkdir(path, mode, dir_fd=dir_fd)
            trace.append(("concurrent_winner", candidate))
            raise FileExistsError("competing creator won")
        return installed_mkdir(path, mode, dir_fd=dir_fd)

    def observed_require(path: Path) -> None:
        original_require(path)
        if raced and Path(path) == target:
            trace.append(("revalidated", target))

    monkeypatch.setattr(durable_io.os, "mkdir", concurrent_mkdir)
    monkeypatch.setattr(durable_io, "_require_directory_component", observed_require)

    durable_io.durable_mkdir_parents(target)

    assert target.is_dir()
    assert trace == [
        ("mkdir", target),
        ("concurrent_winner", target),
        ("revalidated", target),
        ("open_parent", target),
        ("fsync_parent", target),
        ("close_parent", target),
        ("open_child", target),
        ("fsync_child", target),
        ("close_child", target),
    ]


def test_durable_mkdir_parents_rejects_existing_file_component(tmp_path: Path) -> None:
    file_component = tmp_path / "not-a-directory"
    file_component.write_text("authority", encoding="utf-8")

    with pytest.raises((NotADirectoryError, OSError), match="directory|component"):
        durable_io.durable_mkdir_parents(file_component / "child")


def test_durable_mkdir_parents_rejects_symlink_component(tmp_path: Path) -> None:
    real = tmp_path / "real"
    real.mkdir()
    link = tmp_path / "linked"
    try:
        link.symlink_to(real, target_is_directory=True)
    except OSError as exc:
        pytest.skip(f"directory symlink unavailable: {exc}")

    with pytest.raises(OSError, match="link|reparse"):
        durable_io.durable_mkdir_parents(link / "child")


def test_durable_mkdir_parents_rejects_windows_reparse_component(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    component = tmp_path / "reparse"
    component.mkdir()
    original_lstat = durable_io.os.lstat

    def reparse_lstat(path):
        attributes = original_lstat(path)
        if Path(path) != component:
            return attributes
        return SimpleNamespace(
            st_mode=stat.S_IFDIR,
            st_file_attributes=getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400),
        )

    monkeypatch.setattr(durable_io, "_IS_WINDOWS", True, raising=False)
    monkeypatch.setattr(durable_io.os, "lstat", reparse_lstat)

    with pytest.raises(OSError, match="link|reparse"):
        durable_io.durable_mkdir_parents(component)


def _install_windows_directory_io(
    monkeypatch: pytest.MonkeyPatch,
    trace: list[tuple[str, Path]],
    *,
    failure: tuple[str, Path] | None = None,
) -> None:
    original_mkdir = os.mkdir
    current_component: Path | None = None

    monkeypatch.setattr(durable_io, "_IS_WINDOWS", True, raising=False)
    monkeypatch.setattr(
        durable_io,
        "_probe_windows_directory_flush",
        lambda path: trace.append(("probe", Path(path))) or True,
        raising=False,
    )

    def mkdir(path, mode=0o777, *, dir_fd=None):
        nonlocal current_component
        candidate = Path(path)
        trace.append(("mkdir", candidate))
        if failure == ("mkdir", candidate):
            raise OSError("injected mkdir failure")
        result = original_mkdir(path, mode, dir_fd=dir_fd)
        current_component = candidate
        return result

    def open_directory(path: Path):
        candidate = Path(path)
        role = "parent" if current_component is not None and candidate == current_component.parent else "child"
        operation = f"open_{role}"
        trace.append((operation, current_component or candidate))
        if current_component is not None and failure == (operation, current_component):
            raise OSError(f"injected {operation} failure")
        return candidate

    def flush_directory(handle: Path) -> None:
        role = "parent" if current_component is not None and handle == current_component.parent else "child"
        operation = f"flush_{role}"
        trace.append((operation, current_component or handle))
        if current_component is not None and failure == (operation, current_component):
            raise OSError(f"injected {operation} failure")

    def close_handle(handle: Path) -> None:
        role = "parent" if current_component is not None and handle == current_component.parent else "child"
        operation = f"close_{role}"
        trace.append((operation, current_component or handle))
        if current_component is not None and failure == (operation, current_component):
            raise OSError(f"injected {operation} failure")

    monkeypatch.setattr(durable_io.os, "mkdir", mkdir)
    monkeypatch.setattr(durable_io, "_open_windows_directory", open_directory, raising=False)
    monkeypatch.setattr(durable_io, "_windows_handle_is_reparse", lambda handle: False, raising=False)
    monkeypatch.setattr(durable_io, "_flush_windows_directory", flush_directory, raising=False)
    monkeypatch.setattr(durable_io, "_close_windows_handle", close_handle, raising=False)


def test_windows_directory_open_uses_reparse_safe_flags_and_closes_handle(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    kernel = _install_fake_directory_kernel(monkeypatch)

    handle = durable_io._open_windows_directory(tmp_path)
    durable_io._close_windows_handle(handle)

    assert len(kernel.create_calls) == 1
    flags = int(kernel.create_calls[0][5])
    assert flags & 0x02000000
    assert flags & 0x00200000
    assert kernel.close_calls == [101]


def test_windows_probe_classifies_unsupported_flush_and_closes_once(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    kernel = _install_fake_directory_kernel(monkeypatch, flush_error=50)

    assert durable_io._probe_windows_directory_flush(tmp_path) is False

    assert kernel.flush_calls == [101]
    assert kernel.close_calls == [101]


def test_windows_probe_propagates_unexpected_flush_error_and_closes_once(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    kernel = _install_fake_directory_kernel(monkeypatch, flush_error=123)

    with pytest.raises(_FakeWindowsError) as captured:
        durable_io._probe_windows_directory_flush(tmp_path)

    assert captured.value.winerror == 123
    assert kernel.close_calls == [101]


def test_windows_probe_preserves_primary_flush_error_when_close_also_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    kernel = _install_fake_directory_kernel(
        monkeypatch,
        flush_error=123,
        close_error=6,
    )

    with pytest.raises(_FakeWindowsError) as captured:
        durable_io._probe_windows_directory_flush(tmp_path)

    assert captured.value.winerror == 123
    assert kernel.close_calls == [101]


def test_windows_probe_rejects_handle_reparse_and_closes_without_flush(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    kernel = _install_fake_directory_kernel(
        monkeypatch,
        attributes=0x10 | 0x400,
    )

    with pytest.raises(OSError, match="reparse"):
        durable_io._probe_windows_directory_flush(tmp_path)

    assert kernel.information_calls == [101]
    assert kernel.flush_calls == []
    assert kernel.close_calls == [101]


def test_windows_probe_preserves_reparse_error_when_close_also_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    kernel = _install_fake_directory_kernel(
        monkeypatch,
        attributes=0x10 | 0x400,
        close_error=6,
    )

    with pytest.raises(OSError, match="reparse"):
        durable_io._probe_windows_directory_flush(tmp_path)

    assert kernel.close_calls == [101]


def test_windows_probe_preserves_information_error_when_close_also_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    kernel = _install_fake_directory_kernel(
        monkeypatch,
        information_error=111,
        close_error=6,
    )

    with pytest.raises(_FakeWindowsError) as captured:
        durable_io._probe_windows_directory_flush(tmp_path)

    assert captured.value.winerror == 111
    assert kernel.close_calls == [101]


def test_windows_probe_invalid_handle_is_an_open_error_without_close(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    invalid = wintypes.HANDLE(-1).value
    kernel = _install_fake_directory_kernel(
        monkeypatch,
        create_handle=invalid,
        create_error=6,
    )

    with pytest.raises(_FakeWindowsError) as captured:
        durable_io._probe_windows_directory_flush(tmp_path)

    assert captured.value.winerror == 6
    assert kernel.close_calls == []


def test_windows_parent_creation_probes_before_first_mutation_and_flushes_each_component(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    target = tmp_path / "first" / "second" / "third"
    trace: list[tuple[str, Path]] = []
    _install_windows_directory_io(monkeypatch, trace)

    durable_io.durable_mkdir_parents(target)

    assert trace[0] == ("probe", tmp_path)
    for component in (tmp_path / "first", tmp_path / "first" / "second", target):
        assert trace.index(("mkdir", component)) < trace.index(("open_parent", component))
        assert trace.index(("open_parent", component)) < trace.index(("open_child", component))
        assert trace.index(("open_child", component)) < trace.index(("flush_parent", component))
        assert trace.index(("flush_parent", component)) < trace.index(("flush_child", component))
        assert trace.index(("flush_child", component)) < trace.index(("close_child", component))
        assert trace.index(("close_child", component)) < trace.index(("close_parent", component))


@pytest.mark.parametrize(
    "operation",
    (
        "mkdir",
        "open_parent",
        "open_child",
        "flush_parent",
        "flush_child",
        "close_parent",
        "close_child",
    ),
)
@pytest.mark.parametrize("failure_index", range(3))
def test_windows_parent_fault_stops_before_deeper_component_and_publication(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    operation: str,
    failure_index: int,
) -> None:
    components = [
        tmp_path / "first",
        tmp_path / "first" / "second",
        tmp_path / "first" / "second" / "third",
    ]
    destination = components[-1] / "authority.json"
    trace: list[tuple[str, Path]] = []
    _install_windows_directory_io(
        monkeypatch,
        trace,
        failure=(operation, components[failure_index]),
    )

    with pytest.raises(OSError, match="injected"):
        durable_io.durable_write_bytes(destination, b"authority\n")

    assert not destination.exists()
    assert list(tmp_path.rglob("authority.json.tmp.*")) == []
    assert all(not path.exists() for path in components[failure_index + 1 :])


def test_windows_retry_redurabilizes_existing_component_before_publication(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    parent = tmp_path / "authority-parent"
    destination = parent / "state.json"
    trace: list[tuple[str, Path]] = []
    fail_flush_once = True

    def probe(path: Path) -> bool:
        trace.append(("probe", Path(path)))
        return True

    def flush_component(parent_path: Path, child_path: Path) -> None:
        nonlocal fail_flush_once
        trace.append(("flush", Path(child_path)))
        if fail_flush_once:
            fail_flush_once = False
            raise OSError("injected child flush failure")

    def publish(source: Path, target: Path) -> None:
        trace.append(("publish", Path(target)))
        os.replace(source, target)

    monkeypatch.setattr(durable_io, "_IS_WINDOWS", True)
    monkeypatch.setattr(durable_io, "_probe_windows_directory_flush", probe)
    monkeypatch.setattr(durable_io, "_flush_windows_component", flush_component)
    monkeypatch.setattr(durable_io, "_publish_durable", publish)

    with pytest.raises(OSError, match="child flush failure"):
        durable_io.durable_write_bytes(destination, b"first\n")

    assert parent.is_dir()
    assert not destination.exists()
    assert trace == [("probe", tmp_path), ("flush", parent)]

    durable_io.durable_write_bytes(destination, b"second\n")

    assert trace == [
        ("probe", tmp_path),
        ("flush", parent),
        ("probe", tmp_path),
        ("flush", parent),
        ("publish", destination),
    ]
    assert destination.read_bytes() == b"second\n"


@pytest.mark.parametrize("failure_index", (0, 1))
def test_windows_three_level_retry_redurabilizes_ancestor_before_next_mkdir(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    failure_index: int,
) -> None:
    components = [
        tmp_path / "first",
        tmp_path / "first" / "second",
        tmp_path / "first" / "second" / "third",
    ]
    destination = components[-1] / "authority.json"
    trace: list[tuple[str, Path]] = []
    original_mkdir = durable_io.os.mkdir
    failed = False

    def probe(path: Path) -> bool:
        trace.append(("probe", Path(path)))
        return True

    def mkdir(path, mode=0o777, *, dir_fd=None):
        candidate = Path(path)
        trace.append(("mkdir", candidate))
        return original_mkdir(path, mode, dir_fd=dir_fd)

    def flush_component(parent_path: Path, child_path: Path) -> None:
        nonlocal failed
        child = Path(child_path)
        trace.append(("flush", child))
        if child == components[failure_index] and not failed:
            failed = True
            raise OSError("injected ancestor parent flush failure")

    def publish(source: Path, target: Path) -> None:
        trace.append(("publish", Path(target)))
        os.replace(source, target)

    monkeypatch.setattr(durable_io, "_IS_WINDOWS", True)
    monkeypatch.setattr(durable_io, "_probe_windows_directory_flush", probe)
    monkeypatch.setattr(durable_io.os, "mkdir", mkdir)
    monkeypatch.setattr(durable_io, "_flush_windows_component", flush_component)
    monkeypatch.setattr(durable_io, "_publish_durable", publish)

    with pytest.raises(OSError, match="ancestor parent flush failure"):
        durable_io.durable_write_bytes(destination, b"first\n")

    assert components[failure_index].is_dir()
    assert all(not path.exists() for path in components[failure_index + 1 :])
    assert not destination.exists()

    durable_io.durable_write_bytes(destination, b"second\n")

    expected: list[tuple[str, Path]] = [("probe", tmp_path)]
    for index in range(failure_index + 1):
        component = components[index]
        expected.extend((("mkdir", component), ("flush", component)))
    ancestor = components[failure_index]
    expected.extend((("probe", ancestor.parent), ("flush", ancestor)))
    for component in components[failure_index + 1 :]:
        expected.extend((("mkdir", component), ("flush", component)))
    expected.append(("publish", destination))
    assert trace == expected


def test_windows_unproven_ancestor_rejects_unsupported_retry_before_next_mkdir(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    first = tmp_path / "first"
    second = first / "second"
    destination = second / "authority.json"
    support = iter((True, False))
    trace: list[tuple[str, Path]] = []
    original_mkdir = durable_io.os.mkdir

    def probe(path: Path) -> bool:
        trace.append(("probe", Path(path)))
        return next(support)

    def mkdir(path, mode=0o777, *, dir_fd=None):
        candidate = Path(path)
        trace.append(("mkdir", candidate))
        return original_mkdir(path, mode, dir_fd=dir_fd)

    def flush_component(parent_path: Path, child_path: Path) -> None:
        trace.append(("flush", Path(child_path)))
        raise OSError("injected first flush failure")

    monkeypatch.setattr(durable_io, "_IS_WINDOWS", True)
    monkeypatch.setattr(durable_io, "_probe_windows_directory_flush", probe)
    monkeypatch.setattr(durable_io.os, "mkdir", mkdir)
    monkeypatch.setattr(durable_io, "_flush_windows_component", flush_component)

    with pytest.raises(OSError, match="first flush failure"):
        durable_io.durable_write_bytes(destination, b"first\n")

    with pytest.raises(
        OSError,
        match="durable directory creation unavailable; pre-provision parent",
    ):
        durable_io.durable_write_bytes(destination, b"second\n")

    assert trace == [
        ("probe", tmp_path),
        ("mkdir", first),
        ("flush", first),
        ("probe", tmp_path),
    ]
    assert not second.exists()
    assert not destination.exists()


def test_windows_component_is_unproven_before_visible_mkdir_and_concurrent_retry(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    component = tmp_path / "first"
    destination = component / "authority.json"
    support = iter((True, False))
    trace: list[tuple[str, Path]] = []
    publications: list[Path] = []
    concurrent_errors: list[str] = []
    marked_before_mkdir: list[bool] = []
    original_mkdir = durable_io.os.mkdir

    def probe(path: Path) -> bool:
        trace.append(("probe", Path(path)))
        return next(support)

    def mkdir(path, mode=0o777, *, dir_fd=None):
        candidate = Path(path)
        marked_before_mkdir.append(
            candidate in durable_io._UNPROVEN_WINDOWS_DIRECTORIES
        )
        original_mkdir(path, mode, dir_fd=dir_fd)
        trace.append(("visible", candidate))
        try:
            durable_io.durable_write_bytes(destination, b"concurrent\n")
        except OSError as exc:
            concurrent_errors.append(str(exc))
            trace.append(("concurrent_blocked", candidate))
        else:
            trace.append(("concurrent_published", candidate))

    def flush_component(parent_path: Path, child_path: Path) -> None:
        trace.append(("flush", Path(child_path)))
        raise OSError("injected outer flush failure")

    def publish(source: Path, target: Path) -> None:
        publications.append(Path(target))
        os.replace(source, target)

    monkeypatch.setattr(durable_io, "_IS_WINDOWS", True)
    monkeypatch.setattr(durable_io, "_probe_windows_directory_flush", probe)
    monkeypatch.setattr(durable_io.os, "mkdir", mkdir)
    monkeypatch.setattr(durable_io, "_flush_windows_component", flush_component)
    monkeypatch.setattr(durable_io, "_publish_durable", publish)

    with pytest.raises(OSError, match="outer flush failure"):
        durable_io.durable_mkdir_parents(component)

    assert marked_before_mkdir == [True]
    assert concurrent_errors == [
        "durable directory creation unavailable; pre-provision parent"
    ]
    assert publications == []
    assert not destination.exists()
    assert trace == [
        ("probe", tmp_path),
        ("visible", component),
        ("probe", tmp_path),
        ("concurrent_blocked", component),
        ("flush", component),
    ]


def test_windows_transition_lock_prevents_creator_cleanup_from_exposing_unproven_path(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    component = tmp_path / "shared"
    destination = component / "authority.json"
    alone = tmp_path / "alone-failure"
    condition = threading.Condition()
    states: set[str] = set()
    errors: dict[str, BaseException] = {}
    publications: list[tuple[Path, bool]] = []
    release_t1 = threading.Event()
    release_t2_flush = threading.Event()
    t2_flush_completed = threading.Event()
    original_mkdir = durable_io.os.mkdir
    original_validate = durable_io._validate_existing_directory_chain

    def mark(state: str) -> None:
        with condition:
            states.add(state)
            condition.notify_all()

    def wait_for(*required: str) -> None:
        with condition:
            assert condition.wait_for(
                lambda: all(state in states for state in required),
                timeout=5,
            )

    class ObservedRLock:
        def __init__(self) -> None:
            self._lock = threading.RLock()

        def __enter__(self):
            name = threading.current_thread().name
            mark(f"{name}:lock-attempt")
            self._lock.acquire()
            mark(f"{name}:lock-entered")
            return self

        def __exit__(self, exc_type, exc, traceback) -> None:
            self._lock.release()

    def validate(path: Path) -> None:
        original_validate(path)
        if threading.current_thread().name == "T1" and "T1:paused" not in states:
            mark("T1:paused")
            assert release_t1.wait(5)

    def probe(path: Path) -> bool:
        return threading.current_thread().name != "T3"

    def mkdir(path, mode=0o777, *, dir_fd=None):
        candidate = Path(path)
        name = threading.current_thread().name
        if name == "T1" or candidate == alone:
            raise OSError("injected creator mkdir failure")
        result = original_mkdir(path, mode, dir_fd=dir_fd)
        if name == "T2":
            mark("T2:visible")
        return result

    def flush_component(parent_path: Path, child_path: Path) -> None:
        if threading.current_thread().name == "T2":
            mark("T2:at-flush")
            assert release_t2_flush.wait(5)
            t2_flush_completed.set()

    def publish(source: Path, target: Path) -> None:
        publications.append((Path(target), t2_flush_completed.is_set()))
        os.replace(source, target)

    def creator(name: str, action) -> None:
        try:
            action()
        except BaseException as exc:
            errors[name] = exc
        finally:
            mark(f"{name}:done")

    monkeypatch.setattr(durable_io, "_IS_WINDOWS", True)
    monkeypatch.setattr(
        durable_io,
        "_DIRECTORY_TRANSITION_LOCK",
        ObservedRLock(),
        raising=False,
    )
    monkeypatch.setattr(durable_io, "_validate_existing_directory_chain", validate)
    monkeypatch.setattr(durable_io, "_probe_windows_directory_flush", probe)
    monkeypatch.setattr(durable_io.os, "mkdir", mkdir)
    monkeypatch.setattr(durable_io, "_flush_windows_component", flush_component)
    monkeypatch.setattr(durable_io, "_publish_durable", publish)

    t1 = threading.Thread(
        name="T1",
        target=creator,
        args=("T1", lambda: durable_io.durable_mkdir_parents(component)),
    )
    t2 = threading.Thread(
        name="T2",
        target=creator,
        args=("T2", lambda: durable_io.durable_mkdir_parents(component)),
    )
    t1.start()
    wait_for("T1:paused")
    t2.start()
    with condition:
        assert condition.wait_for(
            lambda: "T2:lock-attempt" in states or "T2:at-flush" in states,
            timeout=5,
        )
    release_t1.set()
    wait_for("T1:done", "T2:at-flush")

    t3 = threading.Thread(
        name="T3",
        target=creator,
        args=("T3", lambda: durable_io.durable_write_bytes(destination, b"safe\n")),
    )
    t3.start()
    with condition:
        assert condition.wait_for(
            lambda: "T3:lock-attempt" in states or "T3:done" in states,
            timeout=5,
        )
    publications_before_flush = list(publications)
    release_t2_flush.set()
    t1.join(5)
    t2.join(5)
    t3.join(5)

    assert not t1.is_alive() and not t2.is_alive() and not t3.is_alive()
    assert isinstance(errors.get("T1"), OSError)
    assert "T2" not in errors and "T3" not in errors
    assert publications_before_flush == []
    assert publications == [(destination, True)]
    assert destination.read_bytes() == b"safe\n"
    assert component not in durable_io._UNPROVEN_WINDOWS_DIRECTORIES

    with pytest.raises(OSError, match="creator mkdir failure"):
        durable_io.durable_mkdir_parents(alone)
    assert alone not in durable_io._UNPROVEN_WINDOWS_DIRECTORIES


def test_windows_failed_creation_cannot_use_unsupported_preprovision_fallback(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    parent = tmp_path / "authority-parent"
    destination = parent / "state.json"
    support = iter((True, False))
    publications: list[Path] = []

    monkeypatch.setattr(durable_io, "_IS_WINDOWS", True)
    monkeypatch.setattr(
        durable_io,
        "_probe_windows_directory_flush",
        lambda path: next(support),
    )
    monkeypatch.setattr(
        durable_io,
        "_flush_windows_component",
        lambda parent_path, child_path: (_ for _ in ()).throw(
            OSError("injected component flush failure")
        ),
    )
    monkeypatch.setattr(
        durable_io,
        "_publish_durable",
        lambda source, target: publications.append(Path(target)),
    )

    with pytest.raises(OSError, match="component flush failure"):
        durable_io.durable_write_bytes(destination, b"first\n")

    with pytest.raises(
        OSError,
        match="durable directory creation unavailable; pre-provision parent",
    ):
        durable_io.durable_write_bytes(destination, b"second\n")

    assert publications == []
    assert not destination.exists()


def test_windows_unsupported_directory_flush_fails_before_first_mkdir(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    target = tmp_path / "missing" / "parent"
    mkdir_calls: list[Path] = []
    original_mkdir = durable_io.os.mkdir
    monkeypatch.setattr(durable_io, "_IS_WINDOWS", True, raising=False)
    kernel = _install_fake_directory_kernel(monkeypatch, flush_error=50)

    def observed_mkdir(path, mode=0o777, *, dir_fd=None):
        mkdir_calls.append(Path(path))
        return original_mkdir(path, mode, dir_fd=dir_fd)

    monkeypatch.setattr(durable_io.os, "mkdir", observed_mkdir)

    with pytest.raises(
        OSError,
        match="durable directory creation unavailable; pre-provision parent",
    ):
        durable_io.durable_mkdir_parents(target)

    assert mkdir_calls == []
    assert not target.parent.exists()
    assert kernel.flush_calls == [101]
    assert kernel.close_calls == [101]


class _FinishedGateChild:
    pid = 4242

    @staticmethod
    def poll() -> int:
        return 0


def test_scan_process_gate_generates_private_fingerprint_proof_after_release(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fingerprint = "b" * 64
    nonce = "a" * 64
    inherited_nonce = "inherited-nonce"
    inherited_proof = "inherited-proof"
    release_path = tmp_path / "release"
    release_path.write_text("release", encoding="ascii")
    started_path = tmp_path / "started"
    events: list[str] = []
    captured: dict[str, object] = {}

    def token_hex(size: int) -> str:
        events.append("nonce")
        assert size == 32
        return nonce

    def build_proof(exact_nonce: object, exact_fingerprint: object) -> str:
        events.append("builder")
        return build_scan_process_gate_proof(exact_nonce, exact_fingerprint)

    def popen(command, *, shell, env):
        events.append("popen")
        captured.update(command=command, shell=shell, env=env)
        return _FinishedGateChild()

    monkeypatch.setenv(SCAN_PROFILE_POOL_FINGERPRINT_ENV, fingerprint)
    monkeypatch.setenv(SCAN_PROCESS_GATE_NONCE_ENV, inherited_nonce)
    monkeypatch.setenv(SCAN_PROCESS_GATE_PROOF_ENV, inherited_proof)
    monkeypatch.setattr(
        scan_process_gate,
        "secrets",
        SimpleNamespace(token_hex=token_hex),
        raising=False,
    )
    monkeypatch.setattr(
        scan_process_gate,
        "build_scan_process_gate_proof",
        build_proof,
        raising=False,
    )
    monkeypatch.setattr(scan_process_gate, "_create_windows_job", lambda: object())
    monkeypatch.setattr(scan_process_gate.subprocess, "Popen", popen)
    monkeypatch.setattr(scan_process_gate, "_windows_job_active_processes", lambda handle: 1)
    monkeypatch.setattr(scan_process_gate.psutil, "Process", lambda: object())

    result = scan_process_gate.supervise(
        release_path,
        started_path,
        1.0,
        "tree-token",
        ["productive-command"],
    )

    child_environment = captured["env"]
    assert isinstance(child_environment, dict)
    assert result == 0
    assert events == ["nonce", "builder", "popen"]
    assert captured["command"] == ["productive-command"]
    assert captured["shell"] is False
    assert child_environment is not os.environ
    assert child_environment[SCAN_PROFILE_POOL_FINGERPRINT_ENV] == fingerprint
    assert child_environment[SCAN_PROCESS_GATE_NONCE_ENV] == nonce
    assert child_environment[SCAN_PROCESS_GATE_PROOF_ENV] == build_scan_process_gate_proof(
        nonce, fingerprint
    )
    assert child_environment["MORPHIC_SCAN_GROUP_TOKEN"] == "tree-token"
    assert os.environ[SCAN_PROCESS_GATE_NONCE_ENV] == inherited_nonce
    assert os.environ[SCAN_PROCESS_GATE_PROOF_ENV] == inherited_proof
    assert started_path.read_text(encoding="ascii") == "4242"


def test_scan_process_gate_does_not_generate_proof_or_spawn_before_release(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls = {"nonce": 0, "builder": 0, "popen": 0}

    def unexpected(name: str):
        def fail(*args, **kwargs):
            calls[name] += 1
            raise AssertionError(f"{name} called before release")

        return fail

    monkeypatch.setattr(
        scan_process_gate,
        "secrets",
        SimpleNamespace(token_hex=unexpected("nonce")),
        raising=False,
    )
    monkeypatch.setattr(
        scan_process_gate,
        "build_scan_process_gate_proof",
        unexpected("builder"),
        raising=False,
    )
    monkeypatch.setattr(scan_process_gate.subprocess, "Popen", unexpected("popen"))

    result = scan_process_gate.supervise(
        tmp_path / "missing-release",
        tmp_path / "started",
        0.0,
        "tree-token",
        ["productive-command"],
    )

    assert result == 75
    assert calls == {"nonce": 0, "builder": 0, "popen": 0}


@pytest.mark.parametrize("failure_source", ["token_hex", "builder"])
def test_scan_process_gate_proof_generation_failure_prevents_popen(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    failure_source: str,
) -> None:
    release_path = tmp_path / "release"
    release_path.write_text("release", encoding="ascii")
    popen_calls = 0

    def token_hex(size: int) -> str:
        assert size == 32
        if failure_source == "token_hex":
            raise RuntimeError("proof generation failed")
        return "a" * 64

    def build_proof(nonce: object, fingerprint: object) -> str:
        if failure_source == "builder":
            raise RuntimeError("proof generation failed")
        return build_scan_process_gate_proof(nonce, fingerprint)

    def popen(*args, **kwargs):
        nonlocal popen_calls
        popen_calls += 1
        return _FinishedGateChild()

    monkeypatch.setattr(
        scan_process_gate,
        "secrets",
        SimpleNamespace(token_hex=token_hex),
        raising=False,
    )
    monkeypatch.setattr(
        scan_process_gate,
        "build_scan_process_gate_proof",
        build_proof,
        raising=False,
    )
    monkeypatch.setattr(scan_process_gate, "_create_windows_job", lambda: object())
    monkeypatch.setattr(scan_process_gate.subprocess, "Popen", popen)
    monkeypatch.setattr(scan_process_gate, "_windows_job_active_processes", lambda handle: 1)
    monkeypatch.setattr(scan_process_gate.psutil, "Process", lambda: object())

    with pytest.raises(RuntimeError, match="proof generation failed"):
        scan_process_gate.supervise(
            release_path,
            tmp_path / "started",
            1.0,
            "tree-token",
            ["productive-command"],
        )

    assert popen_calls == 0


def test_scan_process_gate_direct_entrypoint_resolves_repository_imports(
    tmp_path: Path,
) -> None:
    environment = os.environ.copy()
    environment.pop("PYTHONPATH", None)

    completed = subprocess.run(
        [sys.executable, str(Path(scan_process_gate.__file__).resolve()), "--help"],
        cwd=tmp_path,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    assert "ModuleNotFoundError" not in completed.stderr


def test_scan_process_gate_direct_entrypoint_rejects_pythonpath_shadow(
    tmp_path: Path,
) -> None:
    shadow_root = tmp_path / "shadow"
    shadow_package = shadow_root / "apps" / "web"
    shadow_package.mkdir(parents=True)
    (shadow_root / "apps" / "__init__.py").write_text("", encoding="ascii")
    (shadow_package / "__init__.py").write_text("", encoding="ascii")
    shadow_marker = tmp_path / "shadow-imported"
    (shadow_package / "durable_io.py").write_text(
        "from pathlib import Path\n"
        f"Path({str(shadow_marker)!r}).write_text('shadow', encoding='ascii')\n"
        "def durable_mkdir_parents(*args, **kwargs):\n"
        "    raise AssertionError('shadow durability boundary used')\n",
        encoding="ascii",
    )
    working_directory = tmp_path / "cwd"
    working_directory.mkdir()
    script_path = Path(scan_process_gate.__file__).resolve()
    repository_root = script_path.parents[1]
    environment = os.environ.copy()
    environment["PYTHONPATH"] = os.pathsep.join(
        (str(shadow_root), str(repository_root))
    )

    completed = subprocess.run(
        [sys.executable, str(script_path), "--help"],
        cwd=working_directory,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    assert not shadow_marker.exists()
    assert "usage: scan_process_gate.py" in completed.stdout


def test_process_gate_started_parent_failure_prevents_every_process_side_effect(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    release_path = tmp_path / "release"
    release_path.write_text("release", encoding="ascii")
    started_path = tmp_path / "missing" / "markers" / "started"
    events: list[str] = []

    def fail_parent(path: Path, *, mode: int = 0o777) -> None:
        events.append("parent")
        assert Path(path) == started_path.parent
        raise OSError("started parent unavailable")

    def create_job():
        events.append("job")
        return object()

    def popen(*args, **kwargs):
        events.append("popen")
        return _FinishedGateChild()

    monkeypatch.setattr(scan_process_gate, "durable_mkdir_parents", fail_parent)
    monkeypatch.setattr(scan_process_gate, "_create_windows_job", create_job)
    monkeypatch.setattr(scan_process_gate.subprocess, "Popen", popen)

    with pytest.raises(OSError, match="started parent unavailable"):
        scan_process_gate.supervise(
            release_path,
            started_path,
            1.0,
            "private-token",
            ["productive-command"],
        )

    assert events == ["parent"]
    assert not started_path.exists()
    assert not started_path.parent.exists()


def test_process_gate_checks_started_parent_before_popen_and_marker_publication(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    release_path = tmp_path / "release"
    release_path.write_text("release", encoding="ascii")
    started_path = tmp_path / "nested" / "markers" / "started"
    events: list[str] = []
    original_write_text = Path.write_text

    def parent(path: Path, *, mode: int = 0o777) -> None:
        events.append("parent")
        Path(path).mkdir(parents=True, exist_ok=True)

    def create_job():
        events.append("job")
        return object()

    def popen(*args, **kwargs):
        events.append("popen")
        return _FinishedGateChild()

    def write_text(path: Path, data: str, *args, **kwargs):
        if Path(path) == started_path:
            events.append("marker")
        return original_write_text(path, data, *args, **kwargs)

    monkeypatch.setattr(scan_process_gate, "durable_mkdir_parents", parent)
    monkeypatch.setattr(scan_process_gate, "_create_windows_job", create_job)
    monkeypatch.setattr(scan_process_gate.subprocess, "Popen", popen)
    monkeypatch.setattr(scan_process_gate, "_windows_job_active_processes", lambda handle: 1)
    monkeypatch.setattr(scan_process_gate.psutil, "Process", lambda: object())
    monkeypatch.setattr(Path, "write_text", write_text)

    result = scan_process_gate.supervise(
        release_path,
        started_path,
        1.0,
        "private-token",
        ["productive-command"],
    )

    assert result == 0
    assert events == ["parent", "job", "popen", "marker"]
    assert started_path.read_text(encoding="ascii") == "4242"


def test_process_gate_started_marker_failure_converges_spawned_tree(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    release_path = tmp_path / "release"
    release_path.write_text("release", encoding="ascii")
    started_path = tmp_path / "started"
    events: list[str] = []

    class Descendant:
        pid = 4243
        info = {"pid": 4243, "status": "running"}
        alive = True

        @staticmethod
        def environ() -> dict[str, str]:
            return {"MORPHIC_SCAN_GROUP_TOKEN": "private-token"}

        def terminate(self) -> None:
            events.append("descendant-terminate")
            self.alive = False

        def wait(self, timeout: float) -> int:
            events.append(f"descendant-wait-{timeout:g}")
            return 1

    descendant = Descendant()

    class RootAuthority:
        def children(self, *, recursive: bool) -> list[Descendant]:
            assert recursive is True
            events.append("enumerate")
            return [descendant]

    class ProductiveChild:
        pid = 4242
        returncode: int | None = None

        def poll(self) -> int | None:
            return self.returncode

        def terminate(self) -> None:
            events.append("child-terminate")
            self.returncode = 1

        def kill(self) -> None:
            self.returncode = 1

        def wait(self, timeout: float) -> int:
            events.append(f"child-wait-{timeout:g}")
            return 1

    child = ProductiveChild()
    original_write_text = Path.write_text

    def write_text(path: Path, data: str, *args, **kwargs):
        if Path(path) == started_path:
            raise OSError("started marker unavailable")
        return original_write_text(path, data, *args, **kwargs)

    monkeypatch.setattr(scan_process_gate, "_create_windows_job", lambda: object())
    monkeypatch.setattr(scan_process_gate.subprocess, "Popen", lambda *a, **k: child)
    monkeypatch.setattr(
        scan_process_gate.psutil,
        "Process",
        lambda pid=None: RootAuthority(),
    )
    monkeypatch.setattr(
        scan_process_gate.psutil,
        "process_iter",
        lambda attrs: [descendant] if descendant.alive else [],
    )
    monkeypatch.setattr(Path, "write_text", write_text)

    with pytest.raises(OSError, match="started marker unavailable"):
        scan_process_gate.supervise(
            release_path,
            started_path,
            1.0,
            "private-token",
            ["productive-command"],
        )

    assert events == [
        "enumerate",
        "child-terminate",
        "descendant-terminate",
    ]
    assert not started_path.exists()


def test_process_gate_failure_converges_reparented_token_descendant(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    release_path = tmp_path / "release"
    release_path.write_text("release", encoding="ascii")
    started_path = tmp_path / "started"
    events: list[str] = []

    class OrphanedDescendant:
        info = {"pid": 5252, "status": "running"}
        pid = 5252
        alive = True

        @staticmethod
        def environ() -> dict[str, str]:
            return {"MORPHIC_SCAN_GROUP_TOKEN": "private-token"}

        def terminate(self) -> None:
            events.append("orphan-terminate")
            self.alive = False

        @staticmethod
        def wait(timeout: float) -> int:
            events.append(f"orphan-wait-{timeout:g}")
            return 1

    orphan = OrphanedDescendant()

    class ExitedChild:
        pid = 4242

        @staticmethod
        def poll() -> int:
            return 1

        @staticmethod
        def terminate() -> None:
            raise ProcessLookupError()

        @staticmethod
        def wait(timeout: float) -> int:
            raise ProcessLookupError()

        @staticmethod
        def kill() -> None:
            raise ProcessLookupError()

    original_write_text = Path.write_text

    def write_text(path: Path, data: str, *args, **kwargs):
        if Path(path) == started_path:
            raise OSError("started marker unavailable")
        return original_write_text(path, data, *args, **kwargs)

    monkeypatch.setattr(scan_process_gate, "_create_windows_job", lambda: object())
    monkeypatch.setattr(
        scan_process_gate.subprocess,
        "Popen",
        lambda *args, **kwargs: ExitedChild(),
    )
    monkeypatch.setattr(
        scan_process_gate.psutil,
        "Process",
        lambda pid=None: (_ for _ in ()).throw(
            scan_process_gate.psutil.NoSuchProcess(4242)
        ),
    )
    monkeypatch.setattr(
        scan_process_gate.psutil,
        "process_iter",
        lambda attrs: [orphan] if orphan.alive else [],
    )
    monkeypatch.setattr(Path, "write_text", write_text)

    with pytest.raises(OSError, match="started marker unavailable"):
        scan_process_gate.supervise(
            release_path,
            started_path,
            1.0,
            "private-token",
            ["productive-command"],
        )

    assert events == ["orphan-terminate"]


def test_process_gate_cleanup_rescans_for_children_spawned_during_term(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    events: list[str] = []
    late_visible = {"value": False}

    class TokenProcess:
        def __init__(self, pid: int, label: str) -> None:
            self.pid = pid
            self.info = {"pid": pid, "status": "running"}
            self.label = label
            self.alive = True

        @staticmethod
        def environ() -> dict[str, str]:
            return {"MORPHIC_SCAN_GROUP_TOKEN": "private-token"}

        def terminate(self) -> None:
            events.append(f"{self.label}-terminate")
            self.alive = False
            if self.label == "first":
                late_visible["value"] = True

        def wait(self, timeout: float) -> int:
            events.append(f"{self.label}-wait")
            return 1

    first = TokenProcess(5101, "first")
    late = TokenProcess(5102, "late")

    class RootAuthority:
        @staticmethod
        def children(*, recursive: bool) -> list[TokenProcess]:
            assert recursive is True
            return []

    class ProductiveChild:
        pid = 5100
        returncode: int | None = None

        @classmethod
        def poll(cls) -> int | None:
            return cls.returncode

        @classmethod
        def terminate(cls) -> None:
            events.append("root-terminate")
            cls.returncode = 1

        @staticmethod
        def wait(timeout: float) -> int:
            events.append("root-wait")
            return 1

        @classmethod
        def kill(cls) -> None:
            cls.returncode = 1

    scans = {"count": 0}

    def process_iter(attrs: list[str]) -> list[TokenProcess]:
        assert attrs == ["pid", "status"]
        scans["count"] += 1
        return [
            process
            for process in (first, late)
            if process.alive
            and (process is first or late_visible["value"])
        ]

    monkeypatch.setattr(scan_process_gate.psutil, "Process", lambda pid: RootAuthority())
    monkeypatch.setattr(scan_process_gate.psutil, "process_iter", process_iter)

    failures = scan_process_gate._converge_spawned_tree(
        ProductiveChild(),  # type: ignore[arg-type]
        "private-token",
    )

    assert failures == []
    assert next(event for event in events if event.endswith("terminate")) == (
        "root-terminate"
    )
    assert "first-terminate" in events
    assert "late-terminate" in events
    assert scans["count"] >= 2


def test_process_gate_cleanup_has_one_deadline_and_reports_final_survivor(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    waits: list[float] = []

    class Survivor:
        pid = 6101
        info = {"pid": 6101, "status": "running"}

        @staticmethod
        def environ() -> dict[str, str]:
            return {"MORPHIC_SCAN_GROUP_TOKEN": "private-token"}

        @staticmethod
        def terminate() -> None:
            pass

        @staticmethod
        def kill() -> None:
            pass

        @staticmethod
        def wait(timeout: float) -> int:
            waits.append(timeout)
            raise scan_process_gate.psutil.TimeoutExpired(timeout)

    class RootAuthority:
        @staticmethod
        def children(*, recursive: bool) -> list[Survivor]:
            return []

    class ExitedChild:
        pid = 6100

        @staticmethod
        def poll() -> int:
            return 1

        @staticmethod
        def terminate() -> None:
            raise ProcessLookupError()

        @staticmethod
        def wait(timeout: float) -> int:
            raise ProcessLookupError()

        @staticmethod
        def kill() -> None:
            raise ProcessLookupError()

    scans = {"count": 0}

    def process_iter(attrs: list[str]) -> list[Survivor]:
        scans["count"] += 1
        return [Survivor()]

    monkeypatch.setattr(
        scan_process_gate,
        "_SPAWNED_TREE_CLEANUP_TIMEOUT",
        0.1,
        raising=False,
    )
    monkeypatch.setattr(scan_process_gate.psutil, "Process", lambda pid: RootAuthority())
    monkeypatch.setattr(scan_process_gate.psutil, "process_iter", process_iter)

    failures = scan_process_gate._converge_spawned_tree(
        ExitedChild(),  # type: ignore[arg-type]
        "private-token",
    )

    assert sum(waits) <= 0.1
    assert scans["count"] >= 2
    assert any("authorized processes survived cleanup: 6101" in str(exc) for exc in failures)


def test_process_gate_cleanup_failure_preserves_original_post_popen_error(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    release_path = tmp_path / "release"
    release_path.write_text("release", encoding="ascii")
    started_path = tmp_path / "started"
    primary_error = OSError("started marker unavailable")
    cleanup_error = RuntimeError("authorized processes survived cleanup: 8101")
    original_write_text = Path.write_text

    def write_text(path: Path, data: str, *args, **kwargs):
        if Path(path) == started_path:
            raise primary_error
        return original_write_text(path, data, *args, **kwargs)

    monkeypatch.setattr(scan_process_gate, "_create_windows_job", lambda: object())
    monkeypatch.setattr(
        scan_process_gate.subprocess,
        "Popen",
        lambda *args, **kwargs: _FinishedGateChild(),
    )
    monkeypatch.setattr(
        scan_process_gate,
        "_converge_spawned_tree",
        lambda child, token: [cleanup_error],
    )
    monkeypatch.setattr(Path, "write_text", write_text)

    with pytest.raises(BaseExceptionGroup) as raised:
        scan_process_gate.supervise(
            release_path,
            started_path,
            1.0,
            "private-token",
            ["productive-command"],
        )

    assert raised.value.exceptions == (primary_error, cleanup_error)


def test_windows_preprovisioned_non_reparse_tree_remains_usable_without_flush_support(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    target = tmp_path / "existing" / "parent"
    target.mkdir(parents=True)
    probes: list[Path] = []
    monkeypatch.setattr(durable_io, "_IS_WINDOWS", True, raising=False)
    monkeypatch.setattr(
        durable_io,
        "_probe_windows_directory_flush",
        lambda path: probes.append(Path(path)) or False,
        raising=False,
    )
    monkeypatch.setattr(
        durable_io,
        "_flush_windows_component",
        lambda parent, child: (_ for _ in ()).throw(
            AssertionError("unsupported preprovisioned tree must not flush")
        ),
    )

    durable_io.durable_mkdir_parents(target)

    assert probes == [target.parent]


def test_durable_write_calls_parent_helper_before_temporary_open(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    target = tmp_path / "nested" / "state.json"
    calls: list[tuple[str, Path]] = []
    original_open = durable_io.os.open

    def parent(path: Path, *, mode: int = 0o777) -> None:
        calls.append(("parent", Path(path)))
        Path(path).mkdir(parents=True, exist_ok=True)

    def observed_open(path, flags, mode=0o777, *, dir_fd=None):
        calls.append(("open", Path(path)))
        return original_open(path, flags, mode, dir_fd=dir_fd)

    monkeypatch.setattr(durable_io, "durable_mkdir_parents", parent, raising=False)
    monkeypatch.setattr(durable_io.os, "open", observed_open)

    durable_io.durable_write_bytes(target, b"state\n")

    assert calls[0] == ("parent", target.parent)
    assert calls[1][0] == "open"


def test_lock_and_process_gate_callers_use_shared_parent_helper(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[str, Path]] = []

    def observed(label: str):
        def create(path: Path, *, mode: int = 0o777) -> None:
            calls.append((label, Path(path)))
            Path(path).mkdir(parents=True, exist_ok=True)

        return create

    monkeypatch.setattr(
        scan_jobs_module,
        "durable_mkdir_parents",
        observed("scan"),
        raising=False,
    )
    scan_service = LocalScanJobService(tmp_path / "scan" / "jobs", cwd=tmp_path)
    with scan_service._process_lock("scan-test"):
        pass
    with scan_service._start_process_lock("scan-test"):
        pass

    monkeypatch.setattr(
        workbench_runtime_module,
        "durable_mkdir_parents",
        observed("workbench"),
        raising=False,
    )
    WorkbenchRuntimeStore(tmp_path / "workbench" / "runtime").save_draft({"focus": "safe"})

    monkeypatch.setattr(
        worker,
        "durable_mkdir_parents",
        observed("harmonization"),
        raising=False,
    )
    with worker._path_lock(tmp_path / "harmonization" / "jobs" / ".registry.lock"):
        pass

    monkeypatch.setattr(
        scan_process_gate,
        "durable_mkdir_parents",
        observed("process-gate"),
        raising=False,
    )
    release_path = tmp_path / "process-gate" / "release"
    release_path.parent.mkdir(parents=True, exist_ok=True)
    release_path.write_text("release", encoding="ascii")
    started_path = tmp_path / "process-gate" / "started" / "marker"
    monkeypatch.setattr(scan_process_gate, "_create_windows_job", lambda: object())
    monkeypatch.setattr(
        scan_process_gate.subprocess,
        "Popen",
        lambda *args, **kwargs: _FinishedGateChild(),
    )
    monkeypatch.setattr(scan_process_gate, "_windows_job_active_processes", lambda handle: 1)
    monkeypatch.setattr(scan_process_gate.psutil, "Process", lambda: object())
    assert scan_process_gate.supervise(
        release_path,
        started_path,
        1.0,
        "private-token",
        ["productive-command"],
    ) == 0
    result_path = tmp_path / "process-gate" / "result" / "exit-code"
    scan_process_gate._publish_result(result_path, 0)

    labels = [label for label, _ in calls]
    assert labels.count("scan") >= 3
    assert "workbench" in labels
    assert "harmonization" in labels
    assert [path for label, path in calls if label == "process-gate"] == [
        started_path.parent,
        result_path.parent,
    ]


def test_durable_write_publishes_complete_bytes_and_removes_private_temp(tmp_path: Path) -> None:
    target = tmp_path / "state.json"

    durable_io.durable_write_bytes(target, b'{"state":"complete"}\n')

    assert target.read_bytes() == b'{"state":"complete"}\n'
    assert list(tmp_path.glob("state.json.tmp.*")) == []


def test_durable_write_failure_preserves_previous_authority_bytes(tmp_path: Path, monkeypatch) -> None:
    target = tmp_path / "state.json"
    target.write_bytes(b'{"state":"previous"}\n')

    def fail_publish(source: Path, destination: Path) -> None:
        raise OSError("injected publish failure")

    monkeypatch.setattr(durable_io, "_publish_durable", fail_publish)

    with pytest.raises(OSError, match="injected publish failure"):
        durable_io.durable_write_bytes(target, b'{"state":"new"}\n')

    assert target.read_bytes() == b'{"state":"previous"}\n'
    assert list(tmp_path.glob("state.json.tmp.*")) == []


def test_durable_write_enforces_owner_only_parent_and_file_modes(
    tmp_path: Path,
    monkeypatch,
) -> None:
    target = tmp_path / "private" / "state.json"
    chmod_calls: list[tuple[Path, int]] = []
    original_chmod = durable_io.os.chmod
    original_publish = durable_io._publish_durable
    temporary_modes: list[int] = []

    def observed(path, mode) -> None:
        chmod_calls.append((Path(path), mode))
        original_chmod(path, mode)

    monkeypatch.setattr(durable_io.os, "chmod", observed)

    def observed_publish(source: Path, destination: Path) -> None:
        temporary_modes.append(source.stat().st_mode & 0o777)
        original_publish(source, destination)

    monkeypatch.setattr(durable_io, "_publish_durable", observed_publish)

    durable_io.durable_write_bytes(target, b"private\n")

    assert (target.parent, 0o700) in chmod_calls
    assert any(
        path.name.startswith("state.json.tmp.") and mode == 0o600
        for path, mode in chmod_calls
    )
    assert (target, 0o600) in chmod_calls
    if durable_io.os.name != "nt":
        assert temporary_modes == [0o600]
        assert target.stat().st_mode & 0o777 == 0o600


def test_workbench_store_uses_shared_durable_publication(tmp_path: Path, monkeypatch) -> None:
    calls: list[Path] = []
    original = durable_io.durable_write_bytes

    def observed(path: Path, data: bytes) -> None:
        calls.append(path)
        original(path, data)

    monkeypatch.setattr("apps.web.workbench_runtime.durable_write_bytes", observed)
    WorkbenchRuntimeStore(tmp_path).save_draft({"focus": "durable"})

    assert calls == [tmp_path / "draft.json"]


def test_scan_registry_uses_shared_durable_publication(tmp_path: Path, monkeypatch) -> None:
    calls: list[Path] = []
    original = durable_io.durable_write_bytes

    def observed(path: Path, data: bytes) -> None:
        calls.append(path)
        original(path, data)

    monkeypatch.setattr("apps.web.scan_jobs.durable_write_bytes", observed)
    service = LocalScanJobService(tmp_path / "jobs", cwd=tmp_path)
    snapshot = service.start(["python", "-c", "import time; time.sleep(30)"])
    try:
        state_path = tmp_path / "jobs" / f"{snapshot['job_id']}.state.json"
        assert state_path in calls
        assert json.loads(state_path.read_text(encoding="utf-8"))["job_id"] == snapshot["job_id"]
    finally:
        service.stop(str(snapshot["job_id"]))


def test_harmonization_job_and_stop_marker_use_durable_boundary(tmp_path: Path, monkeypatch) -> None:
    jobs = tmp_path / "jobs"
    monkeypatch.setattr(worker, "JOBS_DIR", jobs)
    monkeypatch.setattr(worker, "EVENTS_DIR", jobs / "events")
    calls: list[Path] = []

    def durable(path: Path, data: bytes) -> None:
        calls.append(Path(path))
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_bytes(data)

    monkeypatch.setattr(worker, "durable_write_bytes", durable)
    job = HarmonizationJob(
        job_id="harm_durable",
        target_frequency=432.0,
        duration_minutes=1,
        intention="harmonization",
        hardware_config={"use_cpu": False},
    )

    job.save()
    worker._atomic_write_text(worker._stop_marker_path(job.job_id), "stopped")

    assert [path.name for path in calls] == ["harm_durable.json", "harm_durable.stop"]


def test_harmonization_publication_failure_preserves_prior_authority(
    tmp_path: Path,
    monkeypatch,
) -> None:
    jobs = tmp_path / "jobs"
    jobs.mkdir()
    monkeypatch.setattr(worker, "JOBS_DIR", jobs)
    monkeypatch.setattr(worker, "EVENTS_DIR", jobs / "events")
    canonical = jobs / "harm_failure.json"
    original = b'{"status":"pending"}\n'
    canonical.write_bytes(original)
    monkeypatch.setattr(
        worker,
        "durable_write_bytes",
        lambda path, data: (_ for _ in ()).throw(OSError("publication failed")),
    )
    job = HarmonizationJob(
        job_id="harm_failure",
        target_frequency=432.0,
        duration_minutes=1,
        intention="harmonization",
        hardware_config={"use_cpu": False},
        status="running",
    )

    with pytest.raises(OSError, match="publication failed"):
        job.save()

    assert canonical.read_bytes() == original
    assert list(jobs.glob("*.tmp")) == []
