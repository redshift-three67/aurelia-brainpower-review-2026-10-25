from __future__ import annotations

import asyncio
import ctypes
import importlib
import io
import os
import stat
import subprocess
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from types import SimpleNamespace
from typing import Any
from unittest.mock import ANY

import pytest
from starlette.requests import ClientDisconnect

from apps.web.main import create_app


def _report_handles():
    return importlib.import_module("apps.web.report_handles")


def _fake_stat(mode: int, *, size: int = 7, mtime: float = 1_700_000_000.0):
    return SimpleNamespace(
        st_mode=mode,
        st_size=size,
        st_mtime=mtime,
        st_mtime_ns=int(mtime * 1_000_000_000),
        st_dev=41,
        st_ino=43,
    )


class _CountingStream(io.BytesIO):
    def __init__(self, content: bytes = b"payload", *, descriptor: int = 99) -> None:
        super().__init__(content)
        self.descriptor = descriptor
        self.close_calls = 0

    def fileno(self) -> int:
        return self.descriptor

    def close(self) -> None:
        self.close_calls += 1
        super().close()


class _FakeKernelFunction:
    def __init__(self, callback) -> None:
        self.callback = callback
        self.argtypes = None
        self.restype = None

    def __call__(self, *args):
        return self.callback(*args)


@pytest.mark.parametrize(
    "components",
    [
        (),
        ("",),
        (".", "report.txt"),
        ("..", "report.txt"),
        ("nested/report.txt",),
        (r"nested\report.txt",),
        ("report\x00.txt",),
        ("line\nfeed.txt",),
    ],
)
def test_relative_report_components_are_strictly_validated(
    components: tuple[str, ...],
) -> None:
    report_handles = _report_handles()

    with pytest.raises((TypeError, ValueError)):
        report_handles.validate_relative_components(components)


def test_posix_opener_walks_directory_fds_and_transfers_only_the_final_fd(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    report_handles = _report_handles()
    monkeypatch.setattr(report_handles, "_IS_WINDOWS", False)
    monkeypatch.setattr(report_handles.os, "O_DIRECTORY", 0x100000, raising=False)
    monkeypatch.setattr(report_handles.os, "O_NOFOLLOW", 0x200000, raising=False)
    opens: list[tuple[object, int, int | None]] = []
    closes: list[int] = []
    descriptors = iter((10, 11, 12, 13))
    stream = _CountingStream(descriptor=13)

    def fake_open(path, flags, mode=0o777, *, dir_fd=None):
        opens.append((path, flags, dir_fd))
        return next(descriptors)

    def fake_fstat(descriptor: int):
        if descriptor == 13:
            return _fake_stat(stat.S_IFREG | 0o600)
        result = _fake_stat(stat.S_IFDIR | 0o700)
        result.st_dev = 41
        result.st_ino = descriptor
        return result

    monkeypatch.setattr(report_handles.os, "open", fake_open)
    monkeypatch.setattr(report_handles.os, "fstat", fake_fstat)
    monkeypatch.setattr(report_handles.os, "close", closes.append)
    monkeypatch.setattr(report_handles.os, "fdopen", lambda fd, mode: stream)
    expected = report_handles.RootIdentity("/private/reports", 41, 10)

    opened = report_handles._open_posix_report(
        Path("/private/reports"),
        ("client", "session", "report.txt"),
        expected_root_identity=expected,
    )

    nofollow = report_handles.os.O_NOFOLLOW
    directory = report_handles.os.O_DIRECTORY
    assert opens == [
        (Path("/private/reports"), ANY, None),
        ("client", ANY, 10),
        ("session", ANY, 11),
        ("report.txt", ANY, 12),
    ]
    assert all(flags & nofollow for _, flags, _ in opens)
    assert all(flags & directory for _, flags, _ in opens[:3])
    assert not opens[-1][1] & directory
    assert closes == [12, 11, 10]
    assert opened.read() == b"payload"
    opened.close()
    opened.close()
    assert stream.close_calls == 1


def test_posix_final_open_failure_closes_every_intermediate_fd_once(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    report_handles = _report_handles()
    monkeypatch.setattr(report_handles, "_IS_WINDOWS", False)
    monkeypatch.setattr(report_handles.os, "O_DIRECTORY", 0x100000, raising=False)
    monkeypatch.setattr(report_handles.os, "O_NOFOLLOW", 0x200000, raising=False)
    closes: list[int] = []
    descriptors = iter((20, 21, 22))

    def fake_open(path, flags, mode=0o777, *, dir_fd=None):
        if path == "report.txt":
            raise OSError("final open failed")
        return next(descriptors)

    def fake_fstat(descriptor: int):
        result = _fake_stat(stat.S_IFDIR | 0o700)
        result.st_dev = 41
        result.st_ino = 20 if descriptor == 20 else descriptor
        return result

    monkeypatch.setattr(report_handles.os, "open", fake_open)
    monkeypatch.setattr(report_handles.os, "fstat", fake_fstat)
    monkeypatch.setattr(report_handles.os, "close", closes.append)
    expected = report_handles.RootIdentity("/private/reports", 41, 20)

    with pytest.raises(OSError, match="final open failed"):
        report_handles._open_posix_report(
            Path("/private/reports"),
            ("client", "session", "report.txt"),
            expected_root_identity=expected,
        )

    assert closes == [22, 21, 20]


def test_posix_non_regular_final_fd_is_rejected_and_closed_once(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    report_handles = _report_handles()
    monkeypatch.setattr(report_handles, "_IS_WINDOWS", False)
    monkeypatch.setattr(report_handles.os, "O_DIRECTORY", 0x100000, raising=False)
    monkeypatch.setattr(report_handles.os, "O_NOFOLLOW", 0x200000, raising=False)
    descriptors = iter((30, 31))
    closes: list[int] = []

    def fake_open(path, flags, mode=0o777, *, dir_fd=None):
        return next(descriptors)

    def fake_fstat(descriptor: int):
        mode = stat.S_IFDIR if descriptor == 30 else stat.S_IFIFO
        result = _fake_stat(mode | 0o600)
        result.st_ino = 30 if descriptor == 30 else descriptor
        return result

    monkeypatch.setattr(report_handles.os, "open", fake_open)
    monkeypatch.setattr(report_handles.os, "fstat", fake_fstat)
    monkeypatch.setattr(report_handles.os, "close", closes.append)
    expected = report_handles.RootIdentity("/private/reports", 41, 30)

    with pytest.raises(OSError, match="regular file"):
        report_handles._open_posix_report(
            Path("/private/reports"),
            ("pipe.txt",),
            expected_root_identity=expected,
        )

    assert closes == [31, 30]


def test_windows_identity_uses_complete_file_id_info(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    report_handles = _report_handles()
    volume_serial = 0x1122334455667788
    shared_low = bytes.fromhex("0011223344556677")
    file_ids = {
        101: shared_low + bytes.fromhex("8899aabbccddeeff"),
        102: shared_low + bytes.fromhex("0123456789abcdef"),
    }

    class FakeKernel32:
        def __init__(self) -> None:
            self.file_id_calls: list[tuple[int, int, int]] = []
            self.legacy_identity_calls: list[int] = []
            self.CreateFileW = _FakeKernelFunction(lambda *args: 101)
            self.GetFileInformationByHandleEx = _FakeKernelFunction(
                self.get_information_ex
            )
            self.GetFileInformationByHandle = _FakeKernelFunction(
                self.get_legacy_information
            )
            self.GetFinalPathNameByHandleW = _FakeKernelFunction(
                lambda *args: 0
            )
            self.GetFileType = _FakeKernelFunction(lambda handle: 1)
            self.CloseHandle = _FakeKernelFunction(lambda handle: True)

        def get_information_ex(
            self,
            handle,
            information_class,
            information,
            size,
        ) -> bool:
            self.file_id_calls.append(
                (int(handle), int(information_class), int(size))
            )
            payload = volume_serial.to_bytes(8, "little") + file_ids[int(handle)]
            ctypes.memmove(information, payload, len(payload))
            return True

        def get_legacy_information(self, handle, information) -> bool:
            self.legacy_identity_calls.append(int(handle))
            return True

    kernel32 = FakeKernel32()
    monkeypatch.setattr(
        ctypes,
        "WinDLL",
        lambda *args, **kwargs: kernel32,
        raising=False,
    )
    api = report_handles._WindowsApi()

    first = api.identity(101)
    second = api.identity(102)

    assert kernel32.file_id_calls == [(101, 18, 24), (102, 18, 24)]
    assert kernel32.legacy_identity_calls == []
    assert first == (volume_serial, file_ids[101])
    assert second == (volume_serial, file_ids[102])
    assert first != second


class _FakeWindowsApi:
    FILE_ATTRIBUTE_DIRECTORY = 0x10
    FILE_ATTRIBUTE_REPARSE_POINT = 0x400
    FILE_TYPE_DISK = 1

    def __init__(self) -> None:
        self.next_handle = iter((101, 102, 103, 104))
        self.open_calls: list[tuple[Path, bool]] = []
        self.close_calls: list[int] = []
        self.attributes_by_handle = {101: 0x10, 102: 0x10, 103: 0x10, 104: 0}
        self.final_paths = {
            101: r"\\?\C:\private\reports",
            104: r"\\?\C:\private\reports\client\session\report.txt",
        }
        self.detach_calls: list[int] = []
        self.detach_error: OSError | None = None

    def open_path(self, path: Path, *, directory: bool) -> int:
        self.open_calls.append((path, directory))
        return next(self.next_handle)

    def attributes(self, handle: int) -> int:
        return self.attributes_by_handle[handle]

    def identity(self, handle: int) -> tuple[int, int]:
        return (71, 101 if handle == 101 else handle)

    def final_path(self, handle: int) -> str:
        return self.final_paths[handle]

    def file_type(self, handle: int) -> int:
        return self.FILE_TYPE_DISK

    def detach_to_fd(self, handle: int) -> int:
        self.detach_calls.append(handle)
        if self.detach_error is not None:
            raise self.detach_error
        return 99

    def close(self, handle: int) -> None:
        self.close_calls.append(handle)


def test_windows_opener_holds_components_and_transfers_final_handle_once(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    report_handles = _report_handles()
    api = _FakeWindowsApi()
    stream = _CountingStream(descriptor=99)
    monkeypatch.setattr(
        report_handles.os,
        "fstat",
        lambda fd: _fake_stat(stat.S_IFREG | 0o600),
    )
    monkeypatch.setattr(report_handles.os, "fdopen", lambda fd, mode: stream)
    expected = report_handles.RootIdentity(
        r"\\?\C:\private\reports",
        71,
        101,
    )

    opened = report_handles._open_windows_report(
        Path(r"C:\private\reports"),
        ("client", "session", "report.txt"),
        expected_root_identity=expected,
        api=api,
    )

    assert api.open_calls == [
        (Path(r"C:\private\reports"), True),
        (Path(r"C:\private\reports") / "client", True),
        (Path(r"C:\private\reports") / "client" / "session", True),
        (
            Path(r"C:\private\reports") / "client" / "session" / "report.txt",
            False,
        ),
    ]
    assert api.detach_calls == [104]
    assert api.close_calls == [103, 102, 101]
    opened.close()
    opened.close()
    assert stream.close_calls == 1
    assert 104 not in api.close_calls


@pytest.mark.parametrize(
    ("reparse_handle", "expected_closes"),
    [
        pytest.param(102, [102, 101], id="intermediate"),
        pytest.param(104, [104, 103, 102, 101], id="final"),
    ],
)
def test_windows_reparse_component_fails_closed_and_closes_once(
    monkeypatch: pytest.MonkeyPatch,
    reparse_handle: int,
    expected_closes: list[int],
) -> None:
    report_handles = _report_handles()
    api = _FakeWindowsApi()
    api.attributes_by_handle[reparse_handle] |= 0x400
    expected = report_handles.RootIdentity(
        r"\\?\C:\private\reports",
        71,
        101,
    )

    with pytest.raises(OSError, match="reparse"):
        report_handles._open_windows_report(
            Path(r"C:\private\reports"),
            ("client", "session", "report.txt"),
            expected_root_identity=expected,
            api=api,
        )

    assert api.close_calls == expected_closes
    assert api.detach_calls == []


def test_windows_containment_failure_closes_final_and_intermediate_handles_once(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    report_handles = _report_handles()
    api = _FakeWindowsApi()
    api.final_paths[104] = r"\\?\C:\escaped\report.txt"
    expected = report_handles.RootIdentity(
        r"\\?\C:\private\reports",
        71,
        101,
    )

    with pytest.raises(OSError, match="outside"):
        report_handles._open_windows_report(
            Path(r"C:\private\reports"),
            ("client", "session", "report.txt"),
            expected_root_identity=expected,
            api=api,
        )

    assert api.close_calls == [104, 103, 102, 101]
    assert api.detach_calls == []


def test_windows_failed_handle_transfer_closes_final_handle_once(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    report_handles = _report_handles()
    api = _FakeWindowsApi()
    api.detach_error = OSError("transfer failed")
    expected = report_handles.RootIdentity(
        r"\\?\C:\private\reports",
        71,
        101,
    )

    with pytest.raises(OSError, match="transfer failed"):
        report_handles._open_windows_report(
            Path(r"C:\private\reports"),
            ("client", "session", "report.txt"),
            expected_root_identity=expected,
            api=api,
        )

    assert api.detach_calls == [104]
    assert api.close_calls == [104, 103, 102, 101]


def test_windows_fdopen_failure_closes_transferred_fd_not_native_handle(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    report_handles = _report_handles()
    api = _FakeWindowsApi()
    descriptor_closes: list[int] = []
    monkeypatch.setattr(
        report_handles.os,
        "fstat",
        lambda fd: _fake_stat(stat.S_IFREG | 0o600),
    )
    monkeypatch.setattr(
        report_handles.os,
        "fdopen",
        lambda fd, mode: (_ for _ in ()).throw(OSError("fdopen failed")),
    )
    monkeypatch.setattr(report_handles.os, "close", descriptor_closes.append)
    expected = report_handles.RootIdentity(
        r"\\?\C:\private\reports",
        71,
        101,
    )

    with pytest.raises(OSError, match="fdopen failed"):
        report_handles._open_windows_report(
            Path(r"C:\private\reports"),
            ("client", "session", "report.txt"),
            expected_root_identity=expected,
            api=api,
        )

    assert descriptor_closes == [99]
    assert 104 not in api.close_calls
    assert api.close_calls == [103, 102, 101]


def test_download_iterator_closes_handle_on_cancellation_and_read_error() -> None:
    report_handles = _report_handles()
    metadata = _fake_stat(stat.S_IFREG | 0o600)
    stream = _CountingStream(b"abcdef")
    handle = report_handles.ReportHandle(stream, metadata)
    iterator = handle.iter_chunks(2)

    assert next(iterator) == b"ab"
    iterator.close()
    assert stream.close_calls == 1

    class FailingStream(_CountingStream):
        def read(self, size: int = -1) -> bytes:
            raise OSError("injected read error")

    failing_stream = FailingStream()
    failing_handle = report_handles.ReportHandle(failing_stream, metadata)
    with pytest.raises(OSError, match="read error"):
        list(failing_handle.iter_chunks(2))
    assert failing_stream.close_calls == 1


class _BarrierReadStream(_CountingStream):
    def __init__(self, content: bytes) -> None:
        super().__init__(content)
        self.first_read_started = threading.Event()
        self.release_first_read = threading.Event()
        self._blocked = False

    def read(self, size: int = -1) -> bytes:
        if not self._blocked:
            self._blocked = True
            self.first_read_started.set()
            if not self.release_first_read.wait(timeout=5):
                raise TimeoutError("test did not release first report read")
        return super().read(size)

    def append_after_fstat(self, content: bytes) -> None:
        position = self.tell()
        self.seek(0, io.SEEK_END)
        self.write(content)
        self.seek(position)

    def truncate_after_fstat(self, size: int) -> None:
        position = self.tell()
        self.truncate(size)
        self.seek(min(position, size))


def test_download_stream_ignores_bytes_appended_after_fstat() -> None:
    report_handles = _report_handles()
    initial = b"cataloged-bytes"
    stream = _BarrierReadStream(initial)
    handle = report_handles.ReportHandle(
        stream,
        _fake_stat(stat.S_IFREG | 0o600, size=len(initial)),
    )

    with ThreadPoolExecutor(max_workers=1) as pool:
        result = pool.submit(lambda: b"".join(handle.iter_chunks(64)))
        assert stream.first_read_started.wait(timeout=5)
        stream.append_after_fstat(b"-appended-after-fstat")
        stream.release_first_read.set()
        streamed = result.result(timeout=5)

    assert streamed == initial
    assert stream.close_calls == 1


def test_download_stream_rejects_early_eof_after_fstat() -> None:
    report_handles = _report_handles()
    initial = b"declared-content"
    stream = _BarrierReadStream(initial)
    handle = report_handles.ReportHandle(
        stream,
        _fake_stat(stat.S_IFREG | 0o600, size=len(initial)),
    )

    with ThreadPoolExecutor(max_workers=1) as pool:
        result = pool.submit(lambda: b"".join(handle.iter_chunks(64)))
        assert stream.first_read_started.wait(timeout=5)
        stream.truncate_after_fstat(4)
        stream.release_first_read.set()
        with pytest.raises(RuntimeError, match="ended before declared length"):
            result.result(timeout=5)

    assert stream.close_calls == 1


def test_download_stream_emits_exact_fstat_size() -> None:
    report_handles = _report_handles()
    content = b"exact-content-length"
    stream = _CountingStream(content)
    handle = report_handles.ReportHandle(
        stream,
        _fake_stat(stat.S_IFREG | 0o600, size=len(content)),
    )

    assert b"".join(handle.iter_chunks(3)) == content
    assert stream.close_calls == 1


def _route_download_response(
    tmp_path: Path,
    stream: _CountingStream,
):
    report_handles = _report_handles()
    handle = report_handles.ReportHandle(
        stream,
        _fake_stat(stat.S_IFREG | 0o600, size=len(stream.getvalue())),
    )

    class Catalog:
        def open_download(self, report_id: str):
            assert report_id == "report-asgi-lifecycle"
            return handle, {
                "media_type": "text/plain; charset=utf-8",
                "size": len(stream.getvalue()),
                "file_name": "report.txt",
            }

    app = create_app(
        runtime_dir=tmp_path / "runtime",
        report_roots=[tmp_path / "reports"],
    )
    app.state.report_catalog_factory = lambda: Catalog()
    route = next(
        route
        for route in app.routes
        if getattr(route, "path", None) == "/api/reports/{report_id}/file"
    )
    response = route.endpoint("report-asgi-lifecycle")
    return response, handle


def _download_scope() -> dict[str, Any]:
    return {
        "type": "http",
        "asgi": {"version": "3.0", "spec_version": "2.4"},
        "http_version": "1.1",
        "method": "GET",
        "scheme": "http",
        "path": "/api/reports/report-asgi-lifecycle/file",
        "raw_path": b"/api/reports/report-asgi-lifecycle/file",
        "query_string": b"",
        "headers": [],
        "client": ("testclient", 50000),
        "server": ("testserver", 80),
    }


async def _unused_receive() -> dict[str, str]:
    await asyncio.Future()
    raise AssertionError("unreachable")


def test_report_response_keeps_handle_lazy_and_closes_once_after_completion(
    tmp_path: Path,
) -> None:
    stream = _CountingStream(b"complete-body")
    response, _handle = _route_download_response(tmp_path, stream)
    messages: list[dict[str, Any]] = []

    async def send(message: dict[str, Any]) -> None:
        messages.append(message)

    assert stream.close_calls == 0
    asyncio.run(response(_download_scope(), _unused_receive, send))

    assert b"".join(
        message.get("body", b"")
        for message in messages
        if message["type"] == "http.response.body"
    ) == b"complete-body"
    assert stream.close_calls == 1


def test_report_response_closes_once_when_cancelled_before_first_body_chunk(
    tmp_path: Path,
) -> None:
    class BlockingFirstReadStream(_CountingStream):
        def __init__(self) -> None:
            super().__init__(b"first-body")
            self.read_started = threading.Event()
            self.release_read = threading.Event()

        def read(self, size: int = -1) -> bytes:
            self.read_started.set()
            if not self.release_read.wait(timeout=5):
                raise TimeoutError("test did not release first read")
            return super().read(size)

    stream = BlockingFirstReadStream()
    response, _handle = _route_download_response(tmp_path, stream)
    messages: list[dict[str, Any]] = []

    async def cancel_during_first_read() -> None:
        async def send(message: dict[str, Any]) -> None:
            messages.append(message)

        task = asyncio.create_task(
            response(_download_scope(), _unused_receive, send)
        )
        assert await asyncio.to_thread(stream.read_started.wait, 5)
        assert not any(
            message["type"] == "http.response.body" for message in messages
        )
        task.cancel()
        stream.release_read.set()
        with pytest.raises(asyncio.CancelledError):
            await task
        assert stream.close_calls == 1

    assert stream.close_calls == 0
    asyncio.run(cancel_during_first_read())
    assert stream.close_calls == 1


def test_report_response_closes_once_when_cancelled_after_first_body_chunk(
    tmp_path: Path,
) -> None:
    stream = _CountingStream(b"first-body")
    response, _handle = _route_download_response(tmp_path, stream)

    async def cancel_during_first_send() -> None:
        first_body = asyncio.Event()
        hold_send = asyncio.Event()

        async def send(message: dict[str, Any]) -> None:
            if message["type"] == "http.response.body" and message.get(
                "more_body"
            ):
                first_body.set()
                await hold_send.wait()

        task = asyncio.create_task(response(_download_scope(), _unused_receive, send))
        await asyncio.wait_for(first_body.wait(), timeout=5)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
        assert stream.close_calls == 1

    assert stream.close_calls == 0
    asyncio.run(cancel_during_first_send())
    assert stream.close_calls == 1


def test_report_response_closes_once_on_asgi_send_error(tmp_path: Path) -> None:
    stream = _CountingStream(b"send-error-body")
    response, _handle = _route_download_response(tmp_path, stream)

    async def fail_body_send(message: dict[str, Any]) -> None:
        if message["type"] == "http.response.body":
            raise RuntimeError("injected ASGI send error")

    async def run_send_error() -> None:
        with pytest.raises(RuntimeError, match="ASGI send error"):
            await response(_download_scope(), _unused_receive, fail_body_send)
        assert stream.close_calls == 1

    asyncio.run(run_send_error())
    assert stream.close_calls == 1


def test_report_response_closes_once_on_asgi_read_error(tmp_path: Path) -> None:
    class FailingReadStream(_CountingStream):
        def read(self, size: int = -1) -> bytes:
            raise OSError("injected ASGI read error")

    stream = FailingReadStream()
    response, _handle = _route_download_response(tmp_path, stream)

    async def send(_message: dict[str, Any]) -> None:
        return None

    async def run_read_error() -> None:
        with pytest.raises(ClientDisconnect):
            await response(_download_scope(), _unused_receive, send)
        assert stream.close_calls == 1

    asyncio.run(run_read_error())
    assert stream.close_calls == 1


def _bound_root(report_handles, root: Path):
    return report_handles.inspect_report_root(root)


def test_replaced_root_is_rejected_against_cataloged_identity(tmp_path: Path) -> None:
    report_handles = _report_handles()
    root = tmp_path / "reports"
    report = root / "client" / "report.txt"
    report.parent.mkdir(parents=True)
    report.write_text("original", encoding="utf-8")
    identity = _bound_root(report_handles, root)
    moved = tmp_path / "reports-old"
    root.replace(moved)
    replacement = root / "client" / "report.txt"
    replacement.parent.mkdir(parents=True)
    replacement.write_text("replacement", encoding="utf-8")

    with pytest.raises(OSError, match="identity"):
        report_handles.open_report_handle(
            root,
            ("client", "report.txt"),
            expected_root_identity=identity,
        )


def test_file_swap_after_safe_open_reads_only_the_opened_handle(tmp_path: Path) -> None:
    report_handles = _report_handles()
    root = tmp_path / "reports"
    report = root / "client" / "report.txt"
    report.parent.mkdir(parents=True)
    report.write_text("opened-once", encoding="utf-8")
    identity = _bound_root(report_handles, root)

    with report_handles.open_report_handle(
        root,
        ("client", "report.txt"),
        expected_root_identity=identity,
    ) as opened:
        replacement = report.with_name("replacement.txt")
        replacement.write_text("replacement", encoding="utf-8")
        try:
            os.replace(replacement, report)
        except PermissionError:
            assert os.name == "nt"
        else:
            assert opened.read() == b"opened-once"


def test_root_swap_after_safe_open_uses_handle_or_blocks_swap(tmp_path: Path) -> None:
    report_handles = _report_handles()
    root = tmp_path / "reports"
    report = root / "client" / "report.txt"
    report.parent.mkdir(parents=True)
    report.write_text("opened-root", encoding="utf-8")
    identity = _bound_root(report_handles, root)

    with report_handles.open_report_handle(
        root,
        ("client", "report.txt"),
        expected_root_identity=identity,
    ) as opened:
        moved = tmp_path / "reports-moved"
        try:
            root.replace(moved)
        except PermissionError:
            assert os.name == "nt"
        else:
            replacement = root / "client" / "report.txt"
            replacement.parent.mkdir(parents=True)
            replacement.write_text("replacement-root", encoding="utf-8")
            assert opened.read() == b"opened-root"


@pytest.mark.parametrize("link_final", [False, True], ids=["intermediate", "final"])
def test_symlinked_report_components_fail_closed(
    tmp_path: Path,
    link_final: bool,
) -> None:
    report_handles = _report_handles()
    root = tmp_path / "reports"
    root.mkdir()
    target_dir = tmp_path / "target"
    target_dir.mkdir()
    (target_dir / "report.txt").write_text("outside", encoding="utf-8")
    identity = _bound_root(report_handles, root)
    try:
        if link_final:
            client = root / "client"
            client.mkdir()
            os.symlink(target_dir / "report.txt", client / "report.txt")
        else:
            os.symlink(target_dir, root / "client", target_is_directory=True)
    except (NotImplementedError, OSError) as exc:
        pytest.skip(f"symlink creation unavailable: {exc}")

    with pytest.raises(OSError):
        report_handles.open_report_handle(
            root,
            ("client", "report.txt"),
            expected_root_identity=identity,
        )


def test_directory_in_final_position_is_rejected_as_non_regular(tmp_path: Path) -> None:
    report_handles = _report_handles()
    root = tmp_path / "reports"
    final_directory = root / "client" / "report.txt"
    final_directory.mkdir(parents=True)
    identity = _bound_root(report_handles, root)

    with pytest.raises(OSError):
        report_handles.open_report_handle(
            root,
            ("client", "report.txt"),
            expected_root_identity=identity,
        )


@pytest.mark.skipif(os.name != "nt", reason="Windows junction contract")
def test_windows_junction_component_fails_closed(tmp_path: Path) -> None:
    report_handles = _report_handles()
    root = tmp_path / "reports"
    root.mkdir()
    target = tmp_path / "junction-target"
    target.mkdir()
    (target / "report.txt").write_text("outside", encoding="utf-8")
    junction = root / "client"
    result = subprocess.run(
        ["cmd.exe", "/c", "mklink", "/J", str(junction), str(target)],
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        pytest.skip(f"junction creation unavailable: {result.stderr or result.stdout}")
    identity = _bound_root(report_handles, root)

    with pytest.raises(OSError, match="reparse"):
        report_handles.open_report_handle(
            root,
            ("client", "report.txt"),
            expected_root_identity=identity,
        )
