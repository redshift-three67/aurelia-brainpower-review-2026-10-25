"""Windows-only Phase-3 DPAPI/ACL feasibility boundary.

This module is deliberately not wired into runtime stores or export writers.  It
proves that the local Windows account can protect synthetic bytes with DPAPI and
apply a private ACL only below the operating system's temporary directory.
"""
from __future__ import annotations

import ctypes
import os
import subprocess
import tempfile
from ctypes import wintypes
from pathlib import Path


CRYPTPROTECT_UI_FORBIDDEN = 0x1


class _DataBlob(ctypes.Structure):
    _fields_ = [("cbData", wintypes.DWORD), ("pbData", ctypes.c_void_p)]


def _require_windows() -> None:
    if os.name != "nt":
        raise OSError("Windows DPAPI/ACL protection is only available on Windows")


def _input_blob(payload: bytes) -> tuple[_DataBlob, ctypes.Array[ctypes.c_char]]:
    buffer = ctypes.create_string_buffer(payload, max(1, len(payload)))
    return (
        _DataBlob(
            len(payload),
            ctypes.cast(buffer, ctypes.c_void_p),
        ),
        buffer,
    )


def _read_and_free(blob: _DataBlob) -> bytes:
    try:
        return ctypes.string_at(blob.pbData, blob.cbData) if blob.cbData else b""
    finally:
        if blob.pbData:
            local_free = ctypes.windll.kernel32.LocalFree
            local_free.argtypes = [ctypes.c_void_p]
            local_free.restype = ctypes.c_void_p
            local_free(ctypes.c_void_p(blob.pbData))


def protect_for_current_user(payload: bytes, *, description: str = "") -> bytes:
    """Protect bytes with the current Windows user's DPAPI context."""
    _require_windows()
    input_blob, _buffer = _input_blob(bytes(payload))
    output_blob = _DataBlob()
    protect = ctypes.windll.crypt32.CryptProtectData
    protect.argtypes = [
        ctypes.POINTER(_DataBlob),
        wintypes.LPCWSTR,
        ctypes.POINTER(_DataBlob),
        ctypes.c_void_p,
        ctypes.c_void_p,
        wintypes.DWORD,
        ctypes.POINTER(_DataBlob),
    ]
    protect.restype = wintypes.BOOL
    if not protect(
        ctypes.byref(input_blob),
        description or None,
        None,
        None,
        None,
        CRYPTPROTECT_UI_FORBIDDEN,
        ctypes.byref(output_blob),
    ):
        raise ctypes.WinError(ctypes.get_last_error())
    return _read_and_free(output_blob)


def unprotect_for_current_user(protected: bytes) -> bytes:
    """Recover bytes protected by :func:`protect_for_current_user`."""
    _require_windows()
    input_blob, _buffer = _input_blob(bytes(protected))
    output_blob = _DataBlob()
    description = wintypes.LPWSTR()
    unprotect = ctypes.windll.crypt32.CryptUnprotectData
    unprotect.argtypes = [
        ctypes.POINTER(_DataBlob),
        ctypes.POINTER(wintypes.LPWSTR),
        ctypes.POINTER(_DataBlob),
        ctypes.c_void_p,
        ctypes.c_void_p,
        wintypes.DWORD,
        ctypes.POINTER(_DataBlob),
    ]
    unprotect.restype = wintypes.BOOL
    if not unprotect(
        ctypes.byref(input_blob),
        ctypes.byref(description),
        None,
        None,
        None,
        CRYPTPROTECT_UI_FORBIDDEN,
        ctypes.byref(output_blob),
    ):
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        return _read_and_free(output_blob)
    finally:
        if description:
            local_free = ctypes.windll.kernel32.LocalFree
            local_free.argtypes = [ctypes.c_void_p]
            local_free.restype = ctypes.c_void_p
            local_free(ctypes.cast(description, ctypes.c_void_p))


def current_windows_username() -> str:
    """Return the current local Windows account name without shell invocation."""
    _require_windows()
    size = wintypes.DWORD(257)
    buffer = ctypes.create_unicode_buffer(size.value)
    if not ctypes.windll.advapi32.GetUserNameW(buffer, ctypes.byref(size)):
        raise ctypes.WinError(ctypes.get_last_error())
    return buffer.value


def restrict_directory_to_current_user(directory: str | Path) -> str:
    """Restrict a *temporary* directory to the current user and return its ACL.

    This feasibility helper refuses paths outside the OS temporary directory so it
    cannot be used to mutate a project, export, backup, or runtime directory.
    """
    _require_windows()
    target = Path(directory).resolve()
    temporary_root = Path(tempfile.gettempdir()).resolve()
    try:
        target.relative_to(temporary_root)
    except ValueError as exc:
        raise ValueError("ACL feasibility helper accepts only temporary directories") from exc
    if not target.is_dir():
        raise ValueError("ACL feasibility helper requires an existing directory")

    username = current_windows_username()
    command = [
        "icacls",
        str(target),
        "/inheritance:r",
        "/grant:r",
        f"{username}:(OI)(CI)F",
    ]
    applied = subprocess.run(command, capture_output=True, text=True, check=False)
    if applied.returncode != 0:
        raise RuntimeError("Failed to apply temporary Windows ACL")
    inspected = subprocess.run(
        ["icacls", str(target)], capture_output=True, text=True, check=False
    )
    if inspected.returncode != 0:
        raise RuntimeError("Failed to inspect temporary Windows ACL")
    return inspected.stdout
