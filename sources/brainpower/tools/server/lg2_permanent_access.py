#!/usr/bin/env python3
"""Narrow, fail-closed SSH key staging and retirement for the LG2 host."""

from __future__ import annotations

import argparse
import base64
import binascii
import grp
import hashlib
import json
import os
import pwd
import re
import shlex
import shutil
import socket
import stat
import struct
import subprocess
import sys
import time
from contextlib import ExitStack
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any


OLD_ROOT_BLOB = "AAAAC3NzaC1lZDI1NTE5AAAAIFpqzmx8uducq+BLEmbG0cFRby5wcLRLFphdIfsC6WOS"
OLD_OPS_BLOB = "AAAAC3NzaC1lZDI1NTE5AAAAIJXnrSo7SoAMbCM0KaTZqRSA5AZ9idXwWSB3xIlTyDl1"
ROLES = {
    "admin": ("root", "/root", 0),
    "ops": ("aurelia-ops", "/home/aurelia-ops", 1000),
    "website": ("rauch-web-test", "/home/rauch-web-test", None),
}
MAX_KEY_FILE = 1024 * 1024
MAX_STATE_FILE = 256 * 1024
KEY_TYPE = b"ssh-ed25519"
EXPECTED_HOSTNAME = "vm2565"


class PermanentAccessError(RuntimeError):
    """An explicit guard failed; no broader recovery is attempted."""


def _read_wire_string(raw: bytes, offset: int) -> tuple[bytes, int]:
    if len(raw) < offset + 4:
        raise PermanentAccessError("truncated SSH public key")
    length = struct.unpack(">I", raw[offset : offset + 4])[0]
    start = offset + 4
    end = start + length
    if length > 1024 or end > len(raw):
        raise PermanentAccessError("invalid SSH public key field length")
    return raw[start:end], end


def decode_ssh_blob(blob: str) -> bytes:
    """Decode and validate a canonical 32-byte OpenSSH ed25519 wire blob."""
    if not isinstance(blob, str) or not blob or len(blob) > 4096:
        raise PermanentAccessError("invalid ed25519 public-key blob")
    try:
        raw = base64.b64decode(blob.encode("ascii"), validate=True)
    except (UnicodeEncodeError, binascii.Error, ValueError) as exc:
        raise PermanentAccessError("invalid ed25519 public-key base64") from exc
    key_type, offset = _read_wire_string(raw, 0)
    key_data, offset = _read_wire_string(raw, offset)
    if key_type != KEY_TYPE or len(key_data) != 32 or offset != len(raw):
        raise PermanentAccessError("public key must be a 32-byte ssh-ed25519 key")
    return raw


def _fingerprint(blob: str) -> str:
    digest = hashlib.sha256(decode_ssh_blob(blob)).digest()
    return "SHA256:" + base64.b64encode(digest).decode("ascii").rstrip("=")


def _public_key(value: Any) -> str:
    if not isinstance(value, str) or len(value) > 4096 or any(c in value for c in "\r\n\0"):
        raise PermanentAccessError("public_key must be one OpenSSH key line")
    fields = value.split()
    if len(fields) not in (2, 3) or fields[0] != "ssh-ed25519":
        raise PermanentAccessError("public_key must contain only an ssh-ed25519 key and optional comment")
    blob = fields[1]
    decode_ssh_blob(blob)
    return blob


def validate_payload(payload: Any) -> dict[str, dict[str, str]]:
    """Validate exactly the three public-key roles and return safe key records."""
    if not isinstance(payload, dict) or set(payload) != set(ROLES):
        raise PermanentAccessError("payload must contain exactly admin, ops, and website")
    records: dict[str, dict[str, str]] = {}
    for role in ROLES:
        item = payload[role]
        if not isinstance(item, dict) or set(item) != {"public_key"}:
            raise PermanentAccessError(f"{role} must contain exactly public_key")
        blob = _public_key(item["public_key"])
        records[role] = {
            "blob": blob,
            "fingerprint": _fingerprint(blob),
            "line": f"restrict ssh-ed25519 {blob}",
        }
    blobs = [records[role]["blob"] for role in ROLES]
    if len(set(blobs)) != len(blobs):
        raise PermanentAccessError("new role keys must be distinct")
    if set(blobs) & {OLD_ROOT_BLOB, OLD_OPS_BLOB}:
        raise PermanentAccessError("new keys must differ from both bootstrap keys")
    if OLD_ROOT_BLOB == OLD_OPS_BLOB:
        raise PermanentAccessError("configured bootstrap keys are not distinct")
    decode_ssh_blob(OLD_ROOT_BLOB)
    decode_ssh_blob(OLD_OPS_BLOB)
    return records


def _key_records(content: bytes) -> list[tuple[str, list[str], bytes]]:
    records: list[tuple[str, list[str], bytes]] = []
    for line in content.splitlines(keepends=True):
        body = line.rstrip(b"\r\n")
        try:
            tokens = shlex.split(body.decode("utf-8", "surrogateescape"), comments=False)
        except ValueError as exc:
            if b"ssh-ed25519" in body:
                raise PermanentAccessError("malformed ed25519 authorized_keys line") from exc
            continue
        for index, token in enumerate(tokens[:-1]):
            if token != "ssh-ed25519":
                continue
            blob = tokens[index + 1]
            decode_ssh_blob(blob)
            records.append((blob, tokens[:index], line))
            break
    return records


def _count_blob(content: bytes, blob: str) -> int:
    return sum(1 for found, _options, _line in _key_records(content) if found == blob)


def _append_line(content: bytes, line: str) -> bytes:
    separator = b"" if not content or content.endswith(b"\n") else b"\n"
    return content + separator + line.encode("ascii") + b"\n"


def _remove_blob(content: bytes, blob: str) -> tuple[bytes, int]:
    kept: list[bytes] = []
    removed = 0
    for line in content.splitlines(keepends=True):
        matches = [key_blob for key_blob, _options, _record_line in _key_records(line)]
        if blob in matches:
            if matches.count(blob) != 1 or len(matches) != 1:
                raise PermanentAccessError("bootstrap key appears ambiguously on one line")
            removed += 1
        else:
            kept.append(line)
    return b"".join(kept), removed


def _sha256(content: bytes | None) -> str | None:
    return hashlib.sha256(content).hexdigest() if content is not None else None


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


class SystemHost:
    """Small system boundary; commands are fixed argv arrays and never use a shell."""

    def is_linux(self) -> bool:
        return sys.platform.startswith("linux")

    def is_root(self) -> bool:
        return hasattr(os, "geteuid") and os.geteuid() == 0

    def is_ubuntu(self) -> bool:
        try:
            values = {}
            with open("/etc/os-release", "r", encoding="utf-8") as stream:
                for line in stream:
                    key, sep, value = line.partition("=")
                    if sep:
                        values[key] = value.strip().strip('"')
            return values.get("ID") == "ubuntu"
        except OSError:
            return False

    def hostname(self) -> str:
        return socket.gethostname()

    def which(self, name: str) -> str | None:
        return shutil.which(name)

    def user(self, name: str):
        try:
            entry = pwd.getpwnam(name)
        except KeyError:
            return None
        return type("Account", (), {"uid": entry.pw_uid, "gid": entry.pw_gid, "home": entry.pw_dir})()

    def group(self, name: str):
        try:
            entry = grp.getgrnam(name)
        except KeyError:
            return None
        return type("Group", (), {"name": entry.gr_name, "gid": entry.gr_gid})()

    def groups(self, name: str, primary_gid: int) -> tuple[int, ...]:
        return tuple(sorted(set(os.getgrouplist(name, primary_gid))))

    def run(self, argv: list[str]) -> None:
        result = subprocess.run(argv, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, text=True, check=False)
        if result.returncode:
            raise PermanentAccessError(f"{Path(argv[0]).name} failed with exit status {result.returncode}")

    def password_locked(self, name: str) -> bool:
        result = subprocess.run(["passwd", "-S", name], stdin=subprocess.DEVNULL,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                text=True, check=False)
        if result.returncode:
            return False
        fields = result.stdout.split()
        return len(fields) >= 2 and fields[0] == name and fields[1] in {"L", "LK"}


class AccessManager:
    """Use dirfd/no-follow operations for a fixed set of SSH account paths."""

    def __init__(self, *, fs_root: str | os.PathLike[str] = "/", host=None):
        self.fs_root = Path(fs_root).resolve()
        self.host = host or SystemHost()

    def _mapped(self, logical_path: str | PurePosixPath) -> Path:
        logical = PurePosixPath(logical_path)
        if not logical.is_absolute() or ".." in logical.parts:
            raise PermanentAccessError("paths must be absolute and cannot traverse parents")
        if self.fs_root == Path("/"):
            return Path(str(logical))
        return self.fs_root.joinpath(*logical.parts[1:])

    def _open_abs_dir(self, logical_path: str | PurePosixPath) -> int:
        physical = self._mapped(logical_path)
        anchor = Path("/") if self.fs_root == Path("/") else self.fs_root
        flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_CLOEXEC", 0)
        nofollow = getattr(os, "O_NOFOLLOW", 0)
        fd = os.open(str(anchor), flags | nofollow)
        try:
            relative = physical.relative_to(anchor)
            for component in relative.parts:
                child = os.open(component, flags | nofollow, dir_fd=fd)
                os.close(fd)
                fd = child
            return fd
        except Exception:
            os.close(fd)
            raise

    @staticmethod
    def _read_at(dir_fd: int, name: str, *, max_bytes: int = MAX_KEY_FILE,
                 expected_uid: int | None = None, expected_gid: int | None = None):
        flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
        try:
            fd = os.open(name, flags, dir_fd=dir_fd)
        except FileNotFoundError:
            return None, None
        try:
            info = os.fstat(fd)
            if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
                raise PermanentAccessError(f"{name} must be a regular single-link file")
            if expected_uid is not None and (info.st_uid != expected_uid or info.st_gid != expected_gid):
                raise PermanentAccessError(f"{name} has unexpected ownership")
            if info.st_size > max_bytes:
                raise PermanentAccessError(f"{name} exceeds the permitted size")
            parts = []
            total = 0
            while True:
                chunk = os.read(fd, min(65536, max_bytes + 1 - total))
                if not chunk:
                    break
                parts.append(chunk)
                total += len(chunk)
                if total > max_bytes:
                    raise PermanentAccessError(f"{name} exceeds the permitted size")
            return b"".join(parts), info
        finally:
            os.close(fd)

    @staticmethod
    def _write_all(fd: int, data: bytes) -> None:
        view = memoryview(data)
        while view:
            count = os.write(fd, view)
            view = view[count:]

    def _write_new_at(self, dir_fd: int, name: str, data: bytes, *, uid: int, gid: int,
                      mode: int = 0o600) -> None:
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
        fd = os.open(name, flags, mode, dir_fd=dir_fd)
        try:
            os.fchown(fd, uid, gid)
            os.fchmod(fd, mode)
            self._write_all(fd, data)
            os.fsync(fd)
        except Exception:
            os.close(fd)
            try:
                os.unlink(name, dir_fd=dir_fd)
            except OSError:
                pass
            raise
        os.close(fd)

    def _atomic_write_at(self, dir_fd: int, name: str, data: bytes, *, expected_hash: str | None,
                         uid: int, gid: int, mode: int = 0o600) -> str:
        current, _info = self._read_at(dir_fd, name, expected_uid=uid, expected_gid=gid)
        if _sha256(current) != expected_hash:
            raise PermanentAccessError(f"{name} changed since its bound snapshot")
        temp_name = f".{name}.tmp.{os.getpid()}.{os.urandom(6).hex()}"
        self._write_new_at(dir_fd, temp_name, data, uid=uid, gid=gid, mode=mode)
        try:
            current_again, _info = self._read_at(dir_fd, name, expected_uid=uid, expected_gid=gid)
            if _sha256(current_again) != expected_hash:
                raise PermanentAccessError(f"{name} drifted before atomic replacement")
            os.replace(temp_name, name, src_dir_fd=dir_fd, dst_dir_fd=dir_fd)
            os.fsync(dir_fd)
        except Exception:
            try:
                os.unlink(temp_name, dir_fd=dir_fd)
            except OSError:
                pass
            raise
        actual, info = self._read_at(dir_fd, name, expected_uid=uid, expected_gid=gid)
        if actual != data or info is None or stat.S_IMODE(info.st_mode) != mode:
            raise PermanentAccessError(f"{name} failed post-write verification")
        return _sha256(actual) or ""

    def _open_ssh_dir(self, home_fd: int, *, uid: int, gid: int, create: bool) -> int | None:
        flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
        try:
            fd = os.open(".ssh", flags, dir_fd=home_fd)
        except FileNotFoundError:
            if not create:
                return None
            os.mkdir(".ssh", 0o700, dir_fd=home_fd)
            fd = os.open(".ssh", flags, dir_fd=home_fd)
            os.fchown(fd, uid, gid)
            os.fchmod(fd, 0o700)
            os.fsync(home_fd)
        info = os.fstat(fd)
        if not stat.S_ISDIR(info.st_mode) or info.st_uid != uid or info.st_gid != gid:
            os.close(fd)
            raise PermanentAccessError(".ssh directory has unexpected type or ownership")
        if create:
            os.fchmod(fd, 0o700)
        return fd

    def _account_file_snapshot(self, home_fd: int, *, uid: int, gid: int):
        ssh_fd = self._open_ssh_dir(home_fd, uid=uid, gid=gid, create=False)
        if ssh_fd is None:
            return None, None
        try:
            content, info = self._read_at(ssh_fd, "authorized_keys", expected_uid=uid, expected_gid=gid)
            metadata = None if info is None else {
                "mode": stat.S_IMODE(info.st_mode), "uid": info.st_uid, "gid": info.st_gid,
                "size": info.st_size,
            }
            return content, metadata
        finally:
            os.close(ssh_fd)

    @staticmethod
    def _workdir_name(workdir: str) -> str:
        if not isinstance(workdir, str) or not re.fullmatch(r"/root/aurelia-durable-access-[A-Za-z0-9TZ._-]{1,64}", workdir):
            raise PermanentAccessError("workdir must be a new direct child of /root/aurelia-durable-access-<UTCstamp>")
        return PurePosixPath(workdir).name

    def _open_workdir(self, workdir: str) -> tuple[int, int]:
        name = self._workdir_name(workdir)
        root_fd = self._open_abs_dir("/root")
        try:
            flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
            fd = os.open(name, flags, dir_fd=root_fd)
            info = os.fstat(fd)
            if not stat.S_ISDIR(info.st_mode) or info.st_uid != 0 or stat.S_IMODE(info.st_mode) != 0o700:
                os.close(fd)
                raise PermanentAccessError("workdir must be a root-owned mode-0700 directory")
            return root_fd, fd
        except Exception:
            os.close(root_fd)
            raise

    def _create_workdir(self, workdir: str) -> tuple[int, int]:
        name = self._workdir_name(workdir)
        root_fd = self._open_abs_dir("/root")
        try:
            os.mkdir(name, 0o700, dir_fd=root_fd)
            fd = os.open(name, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) |
                         getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0), dir_fd=root_fd)
            os.fchown(fd, 0, 0)
            os.fchmod(fd, 0o700)
            os.fsync(root_fd)
            os.mkdir("backups", 0o700, dir_fd=fd)
            backup_fd = os.open("backups", os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) |
                                getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0), dir_fd=fd)
            try:
                os.fchown(backup_fd, 0, 0)
                os.fchmod(backup_fd, 0o700)
                os.fsync(fd)
            finally:
                os.close(backup_fd)
            return root_fd, fd
        except Exception:
            os.close(root_fd)
            raise

    def _write_state(self, work_fd: int, state: dict[str, Any]) -> None:
        data = (json.dumps(state, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
        if len(data) > MAX_STATE_FILE:
            raise PermanentAccessError("state journal exceeds the permitted size")
        temp_name = f".state.tmp.{os.getpid()}.{os.urandom(6).hex()}"
        self._write_new_at(work_fd, temp_name, data, uid=0, gid=0, mode=0o600)
        try:
            os.replace(temp_name, "state.json", src_dir_fd=work_fd, dst_dir_fd=work_fd)
            os.fsync(work_fd)
        except Exception:
            try:
                os.unlink(temp_name, dir_fd=work_fd)
            except OSError:
                pass
            raise

    def _read_state(self, work_fd: int) -> dict[str, Any]:
        data, info = self._read_at(work_fd, "state.json", max_bytes=MAX_STATE_FILE, expected_uid=0, expected_gid=0)
        if data is None or info is None or stat.S_IMODE(info.st_mode) != 0o600:
            raise PermanentAccessError("root-only state journal is missing or has unsafe metadata")
        try:
            state = json.loads(data.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise PermanentAccessError("state journal is malformed") from exc
        if not isinstance(state, dict) or state.get("schema") != 1:
            raise PermanentAccessError("unsupported state journal")
        return state

    def _backup(self, work_fd: int, name: str, content: bytes | None) -> str | None:
        if content is None:
            return None
        backup_fd = os.open("backups", os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) |
                            getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0), dir_fd=work_fd)
        try:
            self._write_new_at(backup_fd, name, content, uid=0, gid=0, mode=0o600)
            os.fsync(backup_fd)
            return f"backups/{name}"
        finally:
            os.close(backup_fd)

    def _read_payload(self, payload_file: str) -> Any:
        logical = PurePosixPath(payload_file)
        if not logical.is_absolute():
            raise PermanentAccessError("payload-file must be an absolute path")
        parent = logical.parent
        parent_fd = self._open_abs_dir(parent)
        try:
            data, info = self._read_at(parent_fd, logical.name, max_bytes=16 * 1024)
        finally:
            os.close(parent_fd)
        if data is None or info is None:
            raise PermanentAccessError("payload file is missing")
        if data.startswith(b"-----BEGIN"):
            raise PermanentAccessError("private-key material is not accepted")
        try:
            return json.loads(data.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise PermanentAccessError("payload file must be UTF-8 JSON") from exc

    def _guard(self, *, stage: bool) -> dict[str, Any]:
        if (not self.host.is_linux() or not self.host.is_root() or not self.host.is_ubuntu() or
                self.host.hostname() != EXPECTED_HOSTNAME):
            raise PermanentAccessError("requires root on the expected Ubuntu host vm2565")
        for tool in ("useradd", "passwd"):
            if not self.host.which(tool):
                raise PermanentAccessError(f"required system tool is unavailable: {tool}")
        root = self.host.user("root")
        root_group = self.host.group("root")
        ops = self.host.user("aurelia-ops")
        ops_group = self.host.group("aurelia-ops")
        if not root or root.uid != 0 or root.gid != 0 or root.home != "/root" or not root_group or root_group.gid != 0:
            raise PermanentAccessError("root account or group does not match the fixed host contract")
        if not ops or ops.uid != 1000 or ops.gid != 1000 or ops.home != "/home/aurelia-ops" or not ops_group or ops_group.gid != 1000:
            raise PermanentAccessError("aurelia-ops account or group does not match uid/gid 1000")
        if set(self.host.groups("aurelia-ops", 1000)) != {1000}:
            raise PermanentAccessError("aurelia-ops has unexpected supplementary groups")
        if stage:
            if self.host.user("rauch-web-test") or self.host.group("rauch-web-test"):
                raise PermanentAccessError("website account or group already exists")
            if self._logical_path_exists("/home/rauch-web-test"):
                raise PermanentAccessError("website home path already exists")
        else:
            site = self.host.user("rauch-web-test")
            site_group = self.host.group("rauch-web-test")
            if not site or not site_group or site.uid <= 1000 or site.gid != site_group.gid or site.home != "/home/rauch-web-test":
                raise PermanentAccessError("website account or private group does not match the staged contract")
            if set(self.host.groups("rauch-web-test", site.gid)) != {site.gid}:
                raise PermanentAccessError("website account has unexpected supplementary groups")
            if not self.host.password_locked("rauch-web-test"):
                raise PermanentAccessError("website account password is not locked")
        return {"admin": root, "ops": ops, **({} if stage else {"website": self.host.user("rauch-web-test")})}

    def _logical_path_exists(self, logical_path: str) -> bool:
        path = PurePosixPath(logical_path)
        parent_fd = self._open_abs_dir(path.parent)
        try:
            try:
                os.stat(path.name, dir_fd=parent_fd, follow_symlinks=False)
                return True
            except FileNotFoundError:
                return False
        finally:
            os.close(parent_fd)

    def _home_fd(self, account, expected_home: str, expected_uid: int, expected_gid: int) -> int:
        if account.home != expected_home:
            raise PermanentAccessError(f"account home does not match {expected_home}")
        fd = self._open_abs_dir(expected_home)
        info = os.fstat(fd)
        if not stat.S_ISDIR(info.st_mode) or info.st_uid != expected_uid or info.st_gid != expected_gid:
            os.close(fd)
            raise PermanentAccessError(f"home directory ownership does not match {expected_home}")
        return fd

    def _ensure_account_ssh(self, home_fd: int, uid: int, gid: int) -> int:
        fd = self._open_ssh_dir(home_fd, uid=uid, gid=gid, create=True)
        if fd is None:
            raise PermanentAccessError("could not create .ssh directory")
        return fd

    def stage(self, workdir: str, payload_file: str) -> dict[str, Any]:
        keys = validate_payload(self._read_payload(payload_file))
        accounts = self._guard(stage=True)
        self._workdir_name(workdir)
        with ExitStack() as stack:
            root_home = self._home_fd(accounts["admin"], "/root", 0, 0)
            ops_home = self._home_fd(accounts["ops"], "/home/aurelia-ops", 1000, 1000)
            stack.callback(os.close, root_home)
            stack.callback(os.close, ops_home)
            root_before, root_meta = self._account_file_snapshot(root_home, uid=0, gid=0)
            ops_before, ops_meta = self._account_file_snapshot(ops_home, uid=1000, gid=1000)
            if root_before is None or ops_before is None:
                raise PermanentAccessError("both bootstrap authorized_keys files must already exist")
            if _count_blob(root_before, OLD_ROOT_BLOB) != 1 or _count_blob(root_before, OLD_OPS_BLOB) != 0:
                raise PermanentAccessError("root bootstrap key inventory differs from the expected baseline")
            if _count_blob(ops_before, OLD_OPS_BLOB) != 1 or _count_blob(ops_before, OLD_ROOT_BLOB) != 0:
                raise PermanentAccessError("ops bootstrap key inventory differs from the expected baseline")
            for blob in (keys[role]["blob"] for role in ROLES):
                if _count_blob(root_before, blob) or _count_blob(ops_before, blob):
                    raise PermanentAccessError("new key already exists in a root or ops authorized_keys file")

            work_root_fd, work_fd = self._create_workdir(workdir)
            stack.callback(os.close, work_root_fd)
            stack.callback(os.close, work_fd)
            backup_root = self._backup(work_fd, "root.authorized_keys", root_before)
            backup_ops = self._backup(work_fd, "ops.authorized_keys", ops_before)
            root_after = _append_line(root_before, keys["admin"]["line"])
            ops_after = _append_line(ops_before, keys["ops"]["line"])
            website_after = (keys["website"]["line"] + "\n").encode("ascii")
            state: dict[str, Any] = {
                "schema": 1,
                "phase": "staging",
                "workdir": workdir,
                "created_at": _now(),
                "users": {
                    role: {"name": name, "home": home, "expected_uid": uid}
                    for role, (name, home, uid) in ROLES.items()
                },
                "keys": keys,
                "old_keys": {
                    "admin": {"blob": OLD_ROOT_BLOB, "fingerprint": _fingerprint(OLD_ROOT_BLOB)},
                    "ops": {"blob": OLD_OPS_BLOB, "fingerprint": _fingerprint(OLD_OPS_BLOB)},
                },
                "homes": {"ops_before_mode": stat.S_IMODE(os.fstat(ops_home).st_mode)},
                "files": {
                    "admin": {"path": "/root/.ssh/authorized_keys", "before_hash": _sha256(root_before),
                              "before_exists": True, "before_metadata": root_meta, "backup": backup_root,
                              "after_hash": _sha256(root_after)},
                    "ops": {"path": "/home/aurelia-ops/.ssh/authorized_keys", "before_hash": _sha256(ops_before),
                            "before_exists": True, "before_metadata": ops_meta, "backup": backup_ops,
                            "after_hash": _sha256(ops_after)},
                    "website": {"path": "/home/rauch-web-test/.ssh/authorized_keys", "before_hash": None,
                                "before_exists": False, "before_metadata": None, "backup": None,
                                "after_hash": _sha256(website_after)},
                },
            }
            self._write_state(work_fd, state)
            try:
                os.fchmod(ops_home, 0o700)
                self.host.run(["useradd", "-m", "-U", "-s", "/bin/bash", "-d",
                               "/home/rauch-web-test", "-p", "!", "rauch-web-test"])
                site = self.host.user("rauch-web-test")
                site_group = self.host.group("rauch-web-test")
                if (not site or not site_group or site.uid <= 1000 or site.gid != site_group.gid or
                        site.home != "/home/rauch-web-test" or
                        set(self.host.groups("rauch-web-test", site.gid)) != {site.gid} or
                        not self.host.password_locked("rauch-web-test")):
                    raise PermanentAccessError("created website account failed its locked unprivileged profile check")
                state["users"]["website"].update({"uid": site.uid, "gid": site.gid, "groups": [site.gid],
                                                   "password_locked": True})
                site_home = self._home_fd(site, "/home/rauch-web-test", site.uid, site.gid)
                stack.callback(os.close, site_home)
                os.fchmod(site_home, 0o700)

                root_ssh = self._ensure_account_ssh(root_home, 0, 0)
                ops_ssh = self._ensure_account_ssh(ops_home, 1000, 1000)
                site_ssh = self._ensure_account_ssh(site_home, site.uid, site.gid)
                stack.callback(os.close, root_ssh)
                stack.callback(os.close, ops_ssh)
                stack.callback(os.close, site_ssh)
                site_existing, _meta = self._read_at(site_ssh, "authorized_keys", expected_uid=site.uid, expected_gid=site.gid)
                if site_existing is not None:
                    raise PermanentAccessError("new website account already has authorized_keys content")

                root_hash = self._atomic_write_at(root_ssh, "authorized_keys", root_after,
                                                  expected_hash=state["files"]["admin"]["before_hash"], uid=0, gid=0)
                state["files"]["admin"]["written_hash"] = root_hash
                self._write_state(work_fd, state)
                ops_hash = self._atomic_write_at(ops_ssh, "authorized_keys", ops_after,
                                                 expected_hash=state["files"]["ops"]["before_hash"], uid=1000, gid=1000)
                state["files"]["ops"]["written_hash"] = ops_hash
                self._write_state(work_fd, state)
                site_hash = self._atomic_write_at(site_ssh, "authorized_keys", website_after,
                                                  expected_hash=None, uid=site.uid, gid=site.gid)
                state["files"]["website"]["written_hash"] = site_hash
                for role in ROLES:
                    if state["files"][role]["written_hash"] != state["files"][role]["after_hash"]:
                        raise PermanentAccessError(f"{role} authorized_keys did not match the staged hash")
                state["phase"] = "staged"
                state["staged_at"] = _now()
                self._write_state(work_fd, state)
                return self._public_status(state)
            except Exception as exc:
                state["phase"] = "stage_partial"
                state["stage_error"] = type(exc).__name__
                try:
                    self._write_state(work_fd, state)
                except Exception:
                    pass
                if isinstance(exc, PermanentAccessError):
                    raise
                raise PermanentAccessError("stage incomplete; old root and ops keys have not been retired") from exc

    def _public_status(self, state: dict[str, Any]) -> dict[str, Any]:
        return {
            "phase": state.get("phase"),
            "created_at": state.get("created_at"),
            "staged_at": state.get("staged_at"),
            "completed_at": state.get("completed_at"),
            "roles": {
                role: {"account": state.get("users", {}).get(role, {}).get("name"),
                       "fingerprint": state.get("keys", {}).get(role, {}).get("fingerprint")}
                for role in ROLES
            },
        }

    def _read_current_role(self, role: str, state: dict[str, Any]):
        account = self.host.user(ROLES[role][0])
        if not account:
            return None, None, None
        uid = account.uid
        gid = account.gid
        home_fd = self._home_fd(account, ROLES[role][1], uid, gid)
        try:
            ssh_fd = self._open_ssh_dir(home_fd, uid=uid, gid=gid, create=False)
            if ssh_fd is None:
                return account, None, None
            try:
                content, info = self._read_at(ssh_fd, "authorized_keys", expected_uid=uid, expected_gid=gid)
                return account, content, info
            finally:
                os.close(ssh_fd)
        finally:
            os.close(home_fd)

    def _status_report(self, state: dict[str, Any]) -> dict[str, Any]:
        role_reports = {}
        for role in ROLES:
            account, content, info = self._read_current_role(role, state)
            found = _key_records(content or b"")
            role_reports[role] = {
                "account": ROLES[role][0],
                "uid": account.uid if account else None,
                "groups": sorted(set(self.host.groups(ROLES[role][0], account.gid))) if account else [],
                "key_count": len(found),
                "options": [options for _blob, options, _line in found],
                "fingerprints": sorted({_fingerprint(blob) for blob, _options, _line in found}),
                "sha256": _sha256(content),
                "mode": stat.S_IMODE(info.st_mode) if info else None,
            }
        result = self._public_status(state)
        result["roles"] = role_reports
        return result

    def status(self, workdir: str) -> dict[str, Any]:
        if (not self.host.is_linux() or not self.host.is_root() or not self.host.is_ubuntu() or
                self.host.hostname() != EXPECTED_HOSTNAME):
            raise PermanentAccessError("requires root on the expected Ubuntu host vm2565")
        root_fd, work_fd = self._open_workdir(workdir)
        try:
            state = self._read_state(work_fd)
            if state.get("workdir") != workdir:
                raise PermanentAccessError("workdir does not match its state journal")
            return self._status_report(state)
        finally:
            os.close(work_fd)
            os.close(root_fd)

    def retire(self, workdir: str, *, verified: bool = False) -> dict[str, Any]:
        if verified is not True:
            raise PermanentAccessError("retirement requires the explicit --verified attestation")
        accounts = self._guard(stage=False)
        root_fd, work_fd = self._open_workdir(workdir)
        try:
            state = self._read_state(work_fd)
            if state.get("workdir") != workdir:
                raise PermanentAccessError("workdir does not match its state journal")
            if state.get("phase") not in {"staged", "retiring"}:
                raise PermanentAccessError("only a fully staged journal can retire bootstrap keys")
            files = state.get("files")
            keys = state.get("keys")
            if not isinstance(files, dict) or not isinstance(keys, dict):
                raise PermanentAccessError("state journal lacks the required file/key bindings")

            # Verify every file before changing either bootstrap authorization.
            snapshots: dict[str, bytes] = {}
            for role in ROLES:
                account = accounts[role]
                home_fd = self._home_fd(account, ROLES[role][1], account.uid, account.gid)
                try:
                    ssh_fd = self._open_ssh_dir(home_fd, uid=account.uid, gid=account.gid, create=False)
                    if ssh_fd is None:
                        raise PermanentAccessError(f"{role} .ssh directory is missing")
                    try:
                        content, info = self._read_at(ssh_fd, "authorized_keys", expected_uid=account.uid, expected_gid=account.gid)
                    finally:
                        os.close(ssh_fd)
                finally:
                    os.close(home_fd)
                if content is None or info is None:
                    raise PermanentAccessError(f"{role} authorized_keys is missing")
                expected = files.get(role, {}).get("after_hash")
                if state["phase"] == "staged":
                    if _sha256(content) != expected:
                        raise PermanentAccessError(f"{role} authorized_keys drifted after staging")
                else:
                    retired_hash = files.get(role, {}).get("retire_hash")
                    if _sha256(content) not in {expected, retired_hash}:
                        raise PermanentAccessError(f"{role} authorized_keys drifted during retirement")
                new_blob = keys.get(role, {}).get("blob")
                if not isinstance(new_blob, str) or _count_blob(content, new_blob) != 1:
                    raise PermanentAccessError(f"{role} permanent key is missing or duplicated")
                snapshots[role] = content

            if state["phase"] == "staged":
                root_after, root_removed = _remove_blob(snapshots["admin"], OLD_ROOT_BLOB)
                ops_after, ops_removed = _remove_blob(snapshots["ops"], OLD_OPS_BLOB)
                if root_removed != 1 or ops_removed != 1:
                    raise PermanentAccessError("each bootstrap key must occur exactly once before retirement")
                state["files"]["admin"]["retire_hash"] = _sha256(root_after)
                state["files"]["ops"]["retire_hash"] = _sha256(ops_after)
                state["files"]["website"]["retire_hash"] = files["website"]["after_hash"]
                state["phase"] = "retiring"
                state["retirement_started_at"] = _now()
                self._write_state(work_fd, state)

            for role, old_blob in (("admin", OLD_ROOT_BLOB), ("ops", OLD_OPS_BLOB)):
                current = snapshots[role]
                file_record = state["files"][role]
                if _sha256(current) == file_record["retire_hash"]:
                    if _count_blob(current, old_blob) != 0:
                        raise PermanentAccessError(f"{role} retirement hash does not match its key inventory")
                    continue
                updated, removed = _remove_blob(current, old_blob)
                if removed != 1:
                    raise PermanentAccessError(f"{role} bootstrap key is no longer present exactly once")
                account = accounts[role]
                home_fd = self._home_fd(account, ROLES[role][1], account.uid, account.gid)
                try:
                    ssh_fd = self._open_ssh_dir(home_fd, uid=account.uid, gid=account.gid, create=False)
                    if ssh_fd is None:
                        raise PermanentAccessError(f"{role} .ssh directory disappeared")
                    try:
                        actual_hash = self._atomic_write_at(ssh_fd, "authorized_keys", updated,
                                                           expected_hash=file_record["after_hash"],
                                                           uid=account.uid, gid=account.gid)
                    finally:
                        os.close(ssh_fd)
                finally:
                    os.close(home_fd)
                if actual_hash != file_record["retire_hash"]:
                    raise PermanentAccessError(f"{role} retired bytes do not match the journal")

            for role, old_blob in (("admin", OLD_ROOT_BLOB), ("ops", OLD_OPS_BLOB)):
                account, content, _info = self._read_current_role(role, state)
                if not account or content is None or _sha256(content) != state["files"][role]["retire_hash"]:
                    raise PermanentAccessError(f"{role} retirement did not reach its recorded hash")
                if _count_blob(content, old_blob) != 0 or _count_blob(content, state["keys"][role]["blob"]) != 1:
                    raise PermanentAccessError(f"{role} key inventory failed post-retirement verification")
            website, website_content, _info = self._read_current_role("website", state)
            if not website or website_content is None or _sha256(website_content) != state["files"]["website"]["after_hash"]:
                raise PermanentAccessError("website key changed during retirement")
            state["phase"] = "complete"
            state["completed_at"] = _now()
            self._write_state(work_fd, state)
            return self._status_report(state)
        finally:
            os.close(work_fd)
            os.close(root_fd)


def _cli() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workdir", required=True)
    sub = parser.add_subparsers(dest="action", required=True)
    stage_parser = sub.add_parser("stage")
    stage_parser.add_argument("--payload-file", required=True)
    retire_parser = sub.add_parser("retire")
    retire_parser.add_argument("--verified", action="store_true")
    sub.add_parser("status")
    args = parser.parse_args()
    manager = AccessManager()
    try:
        if args.action == "stage":
            result = manager.stage(args.workdir, args.payload_file)
        elif args.action == "retire":
            result = manager.retire(args.workdir, verified=args.verified)
        else:
            result = manager.status(args.workdir)
        print(json.dumps(result, sort_keys=True, indent=2))
        return 0
    except (PermanentAccessError, OSError, ValueError) as exc:
        print(f"lg2_permanent_access: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(_cli())
