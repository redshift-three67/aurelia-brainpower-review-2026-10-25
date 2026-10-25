from __future__ import annotations

import os
import stat
import threading
import time
from pathlib import Path
from uuid import uuid4


_IS_WINDOWS = os.name == "nt"
_FILE_ATTRIBUTE_DIRECTORY = 0x10
_FILE_ATTRIBUTE_REPARSE_POINT = 0x400
_DIRECTORY_TRANSITION_LOCK = threading.RLock()
_UNPROVEN_POSIX_DIRECTORIES: set[Path] = set()
_UNPROVEN_WINDOWS_DIRECTORIES: set[Path] = set()


def _is_link_or_reparse(attributes: os.stat_result) -> bool:
    return stat.S_ISLNK(attributes.st_mode) or bool(
        (getattr(attributes, "st_file_attributes", 0) or 0)
        & _FILE_ATTRIBUTE_REPARSE_POINT
    )


def _require_directory_component(path: Path) -> None:
    attributes = os.lstat(path)
    if _is_link_or_reparse(attributes):
        raise OSError(f"directory component is a link or reparse point: {path}")
    if not stat.S_ISDIR(attributes.st_mode):
        raise NotADirectoryError(f"directory component is not a directory: {path}")


def _validate_existing_directory_chain(path: Path) -> None:
    for component in (*reversed(path.parents), path):
        _require_directory_component(component)


def _fsync_directory(path: Path) -> None:
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _open_windows_directory(path: Path):
    import ctypes
    from ctypes import wintypes

    create_file = ctypes.WinDLL("kernel32", use_last_error=True).CreateFileW
    create_file.argtypes = [
        wintypes.LPCWSTR,
        wintypes.DWORD,
        wintypes.DWORD,
        ctypes.c_void_p,
        wintypes.DWORD,
        wintypes.DWORD,
        wintypes.HANDLE,
    ]
    create_file.restype = wintypes.HANDLE
    handle = create_file(
        str(path.absolute()),
        0x80000000 | 0x40000000,  # GENERIC_READ | GENERIC_WRITE
        0x1 | 0x2 | 0x4,  # FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE
        None,
        3,  # OPEN_EXISTING
        0x02000000 | 0x00200000,  # BACKUP_SEMANTICS | OPEN_REPARSE_POINT
        None,
    )
    if handle == wintypes.HANDLE(-1).value:
        raise ctypes.WinError(ctypes.get_last_error())
    return handle


def _windows_handle_is_reparse(handle) -> bool:
    import ctypes
    from ctypes import wintypes

    class FileAttributeTagInfo(ctypes.Structure):
        _fields_ = [
            ("FileAttributes", wintypes.DWORD),
            ("ReparseTag", wintypes.DWORD),
        ]

    information = FileAttributeTagInfo()
    get_information = ctypes.WinDLL(
        "kernel32", use_last_error=True
    ).GetFileInformationByHandleEx
    get_information.argtypes = [
        wintypes.HANDLE,
        ctypes.c_int,
        ctypes.c_void_p,
        wintypes.DWORD,
    ]
    get_information.restype = wintypes.BOOL
    if not get_information(handle, 9, ctypes.byref(information), ctypes.sizeof(information)):
        raise ctypes.WinError(ctypes.get_last_error())
    if not information.FileAttributes & _FILE_ATTRIBUTE_DIRECTORY:
        raise NotADirectoryError("opened component is not a directory")
    return bool(information.FileAttributes & _FILE_ATTRIBUTE_REPARSE_POINT)


def _flush_windows_directory(handle) -> None:
    import ctypes
    from ctypes import wintypes

    flush = ctypes.WinDLL("kernel32", use_last_error=True).FlushFileBuffers
    flush.argtypes = [wintypes.HANDLE]
    flush.restype = wintypes.BOOL
    if not flush(handle):
        raise ctypes.WinError(ctypes.get_last_error())


def _close_windows_handle(handle) -> None:
    import ctypes
    from ctypes import wintypes

    close = ctypes.WinDLL("kernel32", use_last_error=True).CloseHandle
    close.argtypes = [wintypes.HANDLE]
    close.restype = wintypes.BOOL
    if not close(handle):
        raise ctypes.WinError(ctypes.get_last_error())


def _probe_windows_directory_flush(path: Path) -> bool:
    handle = _open_windows_directory(path)
    unsupported = False
    failure: BaseException | None = None
    try:
        if _windows_handle_is_reparse(handle):
            raise OSError(f"directory component is a link or reparse point: {path}")
        try:
            _flush_windows_directory(handle)
        except OSError as exc:
            if getattr(exc, "winerror", None) not in {1, 5, 6, 50, 87}:
                raise
            unsupported = True
    except BaseException as exc:
        failure = exc
    try:
        _close_windows_handle(handle)
    except BaseException as exc:
        if failure is None:
            failure = exc
    if failure is not None:
        raise failure
    return not unsupported


def _flush_windows_component(parent: Path, child: Path) -> None:
    handles: list[object] = []
    failure: BaseException | None = None
    try:
        parent_handle = _open_windows_directory(parent)
        handles.append(parent_handle)
        if _windows_handle_is_reparse(parent_handle):
            raise OSError(f"directory component is a link or reparse point: {parent}")
        child_handle = _open_windows_directory(child)
        handles.append(child_handle)
        if _windows_handle_is_reparse(child_handle):
            raise OSError(f"directory component is a link or reparse point: {child}")
        _flush_windows_directory(parent_handle)
        _flush_windows_directory(child_handle)
    except BaseException as exc:
        failure = exc
    for handle in reversed(handles):
        try:
            _close_windows_handle(handle)
        except BaseException as exc:
            if failure is None:
                failure = exc
    if failure is not None:
        raise failure


def durable_mkdir_parents(path: str | Path, *, mode: int = 0o777) -> None:
    """Make the complete directory path durable without following links."""
    with _DIRECTORY_TRANSITION_LOCK:
        _durable_mkdir_parents_locked(path, mode=mode)


def _durable_mkdir_parents_locked(path: str | Path, *, mode: int) -> None:
    target = Path(os.path.abspath(os.fspath(path)))
    unproven = (
        _UNPROVEN_WINDOWS_DIRECTORIES
        if _IS_WINDOWS
        else _UNPROVEN_POSIX_DIRECTORIES
    )
    missing: list[Path] = []
    ancestor = target
    while True:
        try:
            _require_directory_component(ancestor)
            break
        except FileNotFoundError:
            missing.append(ancestor)
            parent = ancestor.parent
            if parent == ancestor:
                raise OSError(f"directory path has no existing ancestor: {target}")
            ancestor = parent

    _validate_existing_directory_chain(ancestor)
    if not missing:
        if _IS_WINDOWS:
            if not _probe_windows_directory_flush(target.parent):
                if target in _UNPROVEN_WINDOWS_DIRECTORIES:
                    raise OSError(
                        "durable directory creation unavailable; pre-provision parent"
                    )
                return
            try:
                _flush_windows_component(target.parent, target)
            except BaseException:
                _UNPROVEN_WINDOWS_DIRECTORIES.add(target)
                raise
            _UNPROVEN_WINDOWS_DIRECTORIES.discard(target)
        else:
            try:
                _fsync_directory(target.parent)
                _fsync_directory(target)
            except BaseException:
                unproven.add(target)
                raise
            unproven.discard(target)
        return
    if ancestor in unproven:
        if _IS_WINDOWS:
            if not _probe_windows_directory_flush(ancestor.parent):
                raise OSError(
                    "durable directory creation unavailable; pre-provision parent"
                )
            _flush_windows_component(ancestor.parent, ancestor)
        else:
            _fsync_directory(ancestor.parent)
            _fsync_directory(ancestor)
        unproven.discard(ancestor)
    elif _IS_WINDOWS and not _probe_windows_directory_flush(ancestor):
        raise OSError("durable directory creation unavailable; pre-provision parent")

    for component in reversed(missing):
        _require_directory_component(component.parent)
        unproven.add(component)
        try:
            os.mkdir(component, mode)
        except FileExistsError:
            pass
        except BaseException:
            unproven.discard(component)
            raise
        _require_directory_component(component)
        if _IS_WINDOWS:
            _flush_windows_component(component.parent, component)
        else:
            _fsync_directory(component.parent)
            _fsync_directory(component)
        unproven.discard(component)


def _publish_windows(source: Path, destination: Path) -> None:
    import ctypes
    from ctypes import wintypes

    move_file = ctypes.WinDLL("kernel32", use_last_error=True).MoveFileExW
    move_file.argtypes = [wintypes.LPCWSTR, wintypes.LPCWSTR, wintypes.DWORD]
    move_file.restype = wintypes.BOOL
    replace_existing = 0x1
    write_through = 0x8
    deadline = time.monotonic() + 1.0
    while True:
        if move_file(
            str(source.resolve()),
            str(destination.resolve()),
            replace_existing | write_through,
        ):
            return
        error = ctypes.get_last_error()
        if error not in {5, 32, 33} or time.monotonic() >= deadline:
            raise ctypes.WinError(error)
        time.sleep(0.01)


def _fsync_parent(path: Path) -> None:
    flags = os.O_RDONLY
    if hasattr(os, "O_DIRECTORY"):
        flags |= os.O_DIRECTORY
    descriptor = os.open(path.parent, flags)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _publish_durable(source: Path, destination: Path) -> None:
    if os.name == "nt":
        _publish_windows(source, destination)
        return
    os.replace(source, destination)
    _fsync_parent(destination)


def durable_write_bytes(path: str | Path, data: bytes) -> None:
    """Publish complete bytes atomically with platform-appropriate durability."""
    destination = Path(path)
    durable_mkdir_parents(destination.parent, mode=0o700)
    os.chmod(destination.parent, 0o700)
    temporary = destination.with_suffix(
        destination.suffix + f".tmp.{uuid4().hex[:8]}"
    )
    try:
        descriptor = os.open(temporary, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        os.chmod(temporary, 0o600)
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        _publish_durable(temporary, destination)
        os.chmod(destination, 0o600)
    finally:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass
