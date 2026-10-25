from __future__ import annotations

import ntpath
import os
import stat
from dataclasses import dataclass
from pathlib import Path
from typing import Any, BinaryIO, Iterator, Sequence


_IS_WINDOWS = os.name == "nt"


@dataclass(frozen=True)
class RootIdentity:
    canonical_path: str
    device: int
    inode: int | bytes


class ReportStreamLengthError(RuntimeError):
    pass


class ReportHandle:
    """Own one verified binary stream and its metadata until explicitly closed."""

    def __init__(self, stream: BinaryIO, stat_result: Any) -> None:
        self._stream = stream
        self.stat = stat_result
        self._closed = False

    def __enter__(self) -> ReportHandle:
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.close()

    def read(self, size: int = -1) -> bytes:
        return self._stream.read(size)

    def iter_chunks(self, chunk_size: int = 64 * 1024) -> Iterator[bytes]:
        try:
            if chunk_size <= 0:
                raise ValueError("chunk_size must be positive")
            remaining = int(self.stat.st_size)
            if remaining < 0:
                raise ReportStreamLengthError("report has a negative declared length")
            while remaining:
                chunk = self.read(min(chunk_size, remaining))
                if not chunk:
                    raise ReportStreamLengthError(
                        "report stream ended before declared length"
                    )
                chunk = chunk[:remaining]
                remaining -= len(chunk)
                yield chunk
        finally:
            self.close()

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        self._stream.close()


def validate_relative_components(components: Sequence[str]) -> tuple[str, ...]:
    validated = tuple(components)
    if not validated:
        raise ValueError("report path requires at least one component")
    for component in validated:
        if not isinstance(component, str):
            raise TypeError("report path components must be strings")
        if (
            not component
            or component in {".", ".."}
            or "/" in component
            or "\\" in component
            or any(ord(character) < 32 or ord(character) == 127 for character in component)
        ):
            raise ValueError("invalid report path component")
    return validated


def _require_directory(stat_result: Any) -> None:
    if not stat.S_ISDIR(stat_result.st_mode):
        raise NotADirectoryError("opened report component is not a directory")


def _require_regular(stat_result: Any) -> None:
    if not stat.S_ISREG(stat_result.st_mode):
        raise OSError("opened report component is not a regular file")


def _require_root_identity(actual: RootIdentity, expected: RootIdentity | None) -> None:
    if expected is None:
        return
    if (actual.device, actual.inode) != (expected.device, expected.inode):
        raise OSError("report root identity changed")


def _posix_directory_flags() -> int:
    nofollow = getattr(os, "O_NOFOLLOW", 0)
    directory = getattr(os, "O_DIRECTORY", 0)
    if not nofollow or not directory:
        raise OSError("safe root-relative report opening is unavailable")
    return os.O_RDONLY | nofollow | directory | getattr(os, "O_CLOEXEC", 0)


def _posix_file_flags() -> int:
    nofollow = getattr(os, "O_NOFOLLOW", 0)
    if not nofollow:
        raise OSError("safe root-relative report opening is unavailable")
    return (
        os.O_RDONLY
        | nofollow
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_BINARY", 0)
    )


def _note_cleanup_failure(primary: BaseException, cleanup: BaseException) -> None:
    try:
        primary.add_note(f"report handle cleanup failed: {cleanup}")
    except AttributeError:  # pragma: no cover - Python < 3.11 compatibility
        pass


def _open_posix_report(
    root: Path,
    components: Sequence[str],
    *,
    expected_root_identity: RootIdentity | None = None,
) -> ReportHandle:
    validated = validate_relative_components(components)
    directory_fds: list[int] = []
    final_fd: int | None = None
    stream: BinaryIO | None = None
    final_stat: Any = None
    failure: BaseException | None = None
    try:
        root_fd = os.open(root, _posix_directory_flags())
        directory_fds.append(root_fd)
        root_stat = os.fstat(root_fd)
        _require_directory(root_stat)
        _require_root_identity(
            RootIdentity(str(root), int(root_stat.st_dev), int(root_stat.st_ino)),
            expected_root_identity,
        )

        parent_fd = root_fd
        for component in validated[:-1]:
            child_fd = os.open(
                component,
                _posix_directory_flags(),
                dir_fd=parent_fd,
            )
            directory_fds.append(child_fd)
            _require_directory(os.fstat(child_fd))
            parent_fd = child_fd

        final_fd = os.open(
            validated[-1],
            _posix_file_flags(),
            dir_fd=parent_fd,
        )
        final_stat = os.fstat(final_fd)
        _require_regular(final_stat)
        stream = os.fdopen(final_fd, "rb")
        final_fd = None  # os.fdopen owns and closes the descriptor from here.
    except BaseException as exc:
        failure = exc

    if final_fd is not None:
        try:
            os.close(final_fd)
        except BaseException as exc:
            if failure is None:
                failure = exc
            else:
                _note_cleanup_failure(failure, exc)
    for descriptor in reversed(directory_fds):
        try:
            os.close(descriptor)
        except BaseException as exc:
            if failure is None:
                failure = exc
            else:
                _note_cleanup_failure(failure, exc)

    if failure is not None:
        if stream is not None:
            try:
                stream.close()
            except BaseException as exc:
                _note_cleanup_failure(failure, exc)
        raise failure
    if stream is None or final_stat is None:  # pragma: no cover - defensive
        raise OSError("safe report open did not produce a stream")
    return ReportHandle(stream, final_stat)


class _WindowsApi:
    FILE_ATTRIBUTE_DIRECTORY = 0x10
    FILE_ATTRIBUTE_REPARSE_POINT = 0x400
    FILE_TYPE_DISK = 1

    def __init__(self) -> None:
        import ctypes
        from ctypes import wintypes

        class FileAttributeTagInfo(ctypes.Structure):
            _fields_ = [
                ("FileAttributes", wintypes.DWORD),
                ("ReparseTag", wintypes.DWORD),
            ]

        class FileId128(ctypes.Structure):
            _fields_ = [
                ("Identifier", ctypes.c_ubyte * 16),
            ]

        class FileIdInfo(ctypes.Structure):
            _fields_ = [
                ("VolumeSerialNumber", ctypes.c_ulonglong),
                ("FileId", FileId128),
            ]

        self._ctypes = ctypes
        self._wintypes = wintypes
        self._attribute_info_type = FileAttributeTagInfo
        self._file_id_info_type = FileIdInfo
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        self._create_file = kernel32.CreateFileW
        self._create_file.argtypes = [
            wintypes.LPCWSTR,
            wintypes.DWORD,
            wintypes.DWORD,
            wintypes.LPVOID,
            wintypes.DWORD,
            wintypes.DWORD,
            wintypes.HANDLE,
        ]
        self._create_file.restype = wintypes.HANDLE
        self._get_attributes = kernel32.GetFileInformationByHandleEx
        self._get_attributes.argtypes = [
            wintypes.HANDLE,
            ctypes.c_int,
            wintypes.LPVOID,
            wintypes.DWORD,
        ]
        self._get_attributes.restype = wintypes.BOOL
        self._get_final_path = kernel32.GetFinalPathNameByHandleW
        self._get_final_path.argtypes = [
            wintypes.HANDLE,
            wintypes.LPWSTR,
            wintypes.DWORD,
            wintypes.DWORD,
        ]
        self._get_final_path.restype = wintypes.DWORD
        self._get_file_type = kernel32.GetFileType
        self._get_file_type.argtypes = [wintypes.HANDLE]
        self._get_file_type.restype = wintypes.DWORD
        self._close_handle = kernel32.CloseHandle
        self._close_handle.argtypes = [wintypes.HANDLE]
        self._close_handle.restype = wintypes.BOOL

    def open_path(self, path: Path, *, directory: bool) -> int:
        flags = 0x00200000  # FILE_FLAG_OPEN_REPARSE_POINT
        if directory:
            flags |= 0x02000000  # FILE_FLAG_BACKUP_SEMANTICS
        share = 0x00000001 | 0x00000002
        if not directory:
            share |= 0x00000004  # A replaced final file cannot redirect this handle.
        handle = self._create_file(
            str(path),
            0x80000000,  # GENERIC_READ
            share,
            None,
            3,  # OPEN_EXISTING
            flags,
            None,
        )
        invalid = self._wintypes.HANDLE(-1).value
        if handle in (None, invalid):
            raise self._ctypes.WinError(self._ctypes.get_last_error())
        return int(handle)

    def attributes(self, handle: int) -> int:
        information = self._attribute_info_type()
        if not self._get_attributes(
            handle,
            9,  # FileAttributeTagInfo
            self._ctypes.byref(information),
            self._ctypes.sizeof(information),
        ):
            raise self._ctypes.WinError(self._ctypes.get_last_error())
        return int(information.FileAttributes)

    def identity(self, handle: int) -> tuple[int, bytes]:
        information = self._file_id_info_type()
        if not self._get_attributes(
            handle,
            18,  # FileIdInfo
            self._ctypes.byref(information),
            self._ctypes.sizeof(information),
        ):
            raise self._ctypes.WinError(self._ctypes.get_last_error())
        return (
            int(information.VolumeSerialNumber),
            bytes(information.FileId.Identifier),
        )

    def final_path(self, handle: int) -> str:
        size = 512
        while True:
            buffer = self._ctypes.create_unicode_buffer(size)
            length = self._get_final_path(handle, buffer, size, 0)
            if not length:
                raise self._ctypes.WinError(self._ctypes.get_last_error())
            if length < size:
                return str(buffer.value)
            size = int(length) + 1

    def file_type(self, handle: int) -> int:
        return int(self._get_file_type(handle))

    def detach_to_fd(self, handle: int) -> int:
        import msvcrt

        return msvcrt.open_osfhandle(
            int(handle),
            os.O_RDONLY | getattr(os, "O_BINARY", 0),
        )

    def close(self, handle: int) -> None:
        if not self._close_handle(handle):
            raise self._ctypes.WinError(self._ctypes.get_last_error())


def _require_windows_directory(api: Any, handle: int) -> None:
    attributes = api.attributes(handle)
    if attributes & api.FILE_ATTRIBUTE_REPARSE_POINT:
        raise OSError("report directory component is a reparse point")
    if not attributes & api.FILE_ATTRIBUTE_DIRECTORY:
        raise NotADirectoryError("opened report component is not a directory")


def _require_windows_file(api: Any, handle: int) -> None:
    attributes = api.attributes(handle)
    if attributes & api.FILE_ATTRIBUTE_REPARSE_POINT:
        raise OSError("report file component is a reparse point")
    if attributes & api.FILE_ATTRIBUTE_DIRECTORY:
        raise OSError("opened report component is not a regular file")
    if api.file_type(handle) != api.FILE_TYPE_DISK:
        raise OSError("opened report component is not a regular disk file")


def _windows_path_is_below(path: str, root: str) -> bool:
    normalized_root = ntpath.normcase(ntpath.normpath(root)).rstrip("\\/")
    normalized_path = ntpath.normcase(ntpath.normpath(path))
    return normalized_path.startswith(normalized_root + "\\")


def _open_windows_report(
    root: Path,
    components: Sequence[str],
    *,
    expected_root_identity: RootIdentity | None = None,
    api: Any | None = None,
) -> ReportHandle:
    validated = validate_relative_components(components)
    api = api or _WindowsApi()
    directory_handles: list[int] = []
    final_handle: int | None = None
    descriptor: int | None = None
    stream: BinaryIO | None = None
    final_stat: Any = None
    failure: BaseException | None = None
    try:
        root_handle = api.open_path(root, directory=True)
        directory_handles.append(root_handle)
        _require_windows_directory(api, root_handle)
        root_device, root_inode = api.identity(root_handle)
        root_final_path = api.final_path(root_handle)
        _require_root_identity(
            RootIdentity(root_final_path, root_device, root_inode),
            expected_root_identity,
        )

        current_path = root
        for component in validated[:-1]:
            current_path = current_path / component
            directory_handle = api.open_path(current_path, directory=True)
            directory_handles.append(directory_handle)
            _require_windows_directory(api, directory_handle)

        final_path = current_path / validated[-1]
        final_handle = api.open_path(final_path, directory=False)
        _require_windows_file(api, final_handle)
        if not _windows_path_is_below(api.final_path(final_handle), root_final_path):
            raise OSError("opened report handle is outside the configured root")

        descriptor = api.detach_to_fd(final_handle)
        final_handle = None  # The CRT descriptor owns the native HANDLE after success.
        final_stat = os.fstat(descriptor)
        _require_regular(final_stat)
        stream = os.fdopen(descriptor, "rb")
        descriptor = None  # The binary stream owns the CRT descriptor from here.
    except BaseException as exc:
        failure = exc

    if descriptor is not None:
        try:
            os.close(descriptor)
        except BaseException as exc:
            if failure is None:
                failure = exc
            else:
                _note_cleanup_failure(failure, exc)
    if final_handle is not None:
        try:
            api.close(final_handle)
        except BaseException as exc:
            if failure is None:
                failure = exc
            else:
                _note_cleanup_failure(failure, exc)
    for handle in reversed(directory_handles):
        try:
            api.close(handle)
        except BaseException as exc:
            if failure is None:
                failure = exc
            else:
                _note_cleanup_failure(failure, exc)

    if failure is not None:
        if stream is not None:
            try:
                stream.close()
            except BaseException as exc:
                _note_cleanup_failure(failure, exc)
        raise failure
    if stream is None or final_stat is None:  # pragma: no cover - defensive
        raise OSError("safe report open did not produce a stream")
    return ReportHandle(stream, final_stat)


def _inspect_posix_root(root: Path) -> RootIdentity:
    descriptor = os.open(root, _posix_directory_flags())
    failure: BaseException | None = None
    identity: RootIdentity | None = None
    try:
        root_stat = os.fstat(descriptor)
        _require_directory(root_stat)
        canonical_path = os.path.normpath(os.path.abspath(os.fspath(root)))
        identity = RootIdentity(
            canonical_path,
            int(root_stat.st_dev),
            int(root_stat.st_ino),
        )
    except BaseException as exc:
        failure = exc
    try:
        os.close(descriptor)
    except BaseException as exc:
        if failure is None:
            failure = exc
        else:
            _note_cleanup_failure(failure, exc)
    if failure is not None:
        raise failure
    if identity is None:  # pragma: no cover - defensive
        raise OSError("report root identity unavailable")
    return identity


def _inspect_windows_root(root: Path) -> RootIdentity:
    api = _WindowsApi()
    handle = api.open_path(root, directory=True)
    failure: BaseException | None = None
    identity: RootIdentity | None = None
    try:
        _require_windows_directory(api, handle)
        device, inode = api.identity(handle)
        identity = RootIdentity(api.final_path(handle), device, inode)
    except BaseException as exc:
        failure = exc
    try:
        api.close(handle)
    except BaseException as exc:
        if failure is None:
            failure = exc
        else:
            _note_cleanup_failure(failure, exc)
    if failure is not None:
        raise failure
    if identity is None:  # pragma: no cover - defensive
        raise OSError("report root identity unavailable")
    return identity


def inspect_report_root(root: str | Path) -> RootIdentity:
    bound_root = Path(os.path.abspath(os.fspath(root)))
    if _IS_WINDOWS:
        return _inspect_windows_root(bound_root)
    return _inspect_posix_root(bound_root)


def open_report_handle(
    root: str | Path,
    components: Sequence[str],
    *,
    expected_root_identity: RootIdentity | None = None,
) -> ReportHandle:
    bound_root = Path(os.path.abspath(os.fspath(root)))
    validated = validate_relative_components(components)
    if _IS_WINDOWS:
        return _open_windows_report(
            bound_root,
            validated,
            expected_root_identity=expected_root_identity,
        )
    return _open_posix_report(
        bound_root,
        validated,
        expected_root_identity=expected_root_identity,
    )
