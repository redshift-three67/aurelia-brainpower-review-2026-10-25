#!/usr/bin/env python3
"""Narrow, fail-closed access hardening for the fresh vm2565 Ubuntu host."""

from __future__ import annotations

import argparse
import base64
import contextlib
import datetime as dt
import hashlib
import ipaddress
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import subprocess
import sys
import time
from dataclasses import dataclass

try:
    import fcntl
except ImportError:  # Test portability; production target is Linux.
    fcntl = None

try:
    import msvcrt
except ImportError:
    msvcrt = None


HOST_SHORT_NAME = "vm2565"
OPS_USER = "aurelia-ops"
OPS_HOME = "/home/aurelia-ops"
KEY_EXPIRY = "20261016210835Z"
SSH_SNIPPET = "/etc/ssh/sshd_config.d/00-aurelia-access.conf"
SSH_SETTINGS = {
    "permitrootlogin": "prohibit-password",
    "passwordauthentication": "no",
    "kbdinteractiveauthentication": "no",
    "pubkeyauthentication": "yes",
    "allowagentforwarding": "no",
    "x11forwarding": "no",
    "allowtcpforwarding": "local",
    "gatewayports": "no",
    "permittunnel": "no",
    "permituserenvironment": "no",
}
WORKDIR_RE = re.compile(r"^aurelia-access-(\d{8}T\d{6}Z)$")
MAX_CONFIG_BYTES = 4 * 1024 * 1024
MIN_APPLY_ROLLBACK_SECONDS = 120
UFW_MUTABLE_PATHS = (
    "/etc/default/ufw",
    "/etc/ufw/user.rules",
    "/etc/ufw/user6.rules",
    "/etc/ufw/ufw.conf",
)


class ControllerError(RuntimeError):
    """A sanitized, expected stop condition."""


@dataclass(frozen=True)
class CommandResult:
    returncode: int
    stdout: str = ""
    stderr: str = ""


def validate_public_key(value: str) -> str:
    """Validate one plain OpenSSH Ed25519 key; return its normalized line."""
    if not isinstance(value, str) or "\n" in value or "\r" in value or "\x00" in value:
        raise ControllerError("public key must be one line")
    value = value.strip()
    parts = value.split(None, 2)
    if len(parts) < 2 or parts[0] != "ssh-ed25519" or len(parts) > 3:
        raise ControllerError("expected one ssh-ed25519 public key")
    encoded = parts[1]
    try:
        blob = base64.b64decode(encoded, validate=True)
    except (ValueError, base64.binascii.Error) as exc:
        raise ControllerError("invalid Ed25519 public-key encoding") from exc
    if base64.b64encode(blob).decode("ascii") != encoded:
        raise ControllerError("noncanonical Ed25519 public-key encoding")
    if len(blob) < 4:
        raise ControllerError("invalid Ed25519 public-key blob")
    type_length = int.from_bytes(blob[:4], "big")
    offset = 4 + type_length
    if type_length != len(b"ssh-ed25519") or blob[4:offset] != b"ssh-ed25519" or offset + 4 > len(blob):
        raise ControllerError("invalid Ed25519 public-key blob")
    key_length = int.from_bytes(blob[offset:offset + 4], "big")
    key = blob[offset + 4:]
    if key_length != 32 or len(key) != 32:
        raise ControllerError("invalid Ed25519 public-key length")
    comment = parts[2] if len(parts) == 3 else ""
    if any(ord(char) < 32 or ord(char) == 127 for char in comment):
        raise ControllerError("invalid public-key comment")
    return "ssh-ed25519 " + encoded + (" " + comment if comment else "")


def _default_runner(argv, **kwargs):
    completed = subprocess.run(
        argv,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    return CommandResult(completed.returncode, completed.stdout or "", completed.stderr or "")


def _utc_now():
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _require_unexpired_key():
    expiry = dt.datetime.strptime(KEY_EXPIRY, "%Y%m%d%H%M%SZ").replace(tzinfo=dt.timezone.utc)
    if dt.datetime.now(dt.timezone.utc) >= expiry:
        raise ControllerError("aurelia-ops public-key expiry has passed")


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class AccessController:
    """One transaction rooted in /root/aurelia-access-<UTC stamp>."""

    def __init__(
        self,
        workdir: str,
        *,
        system_root: str | os.PathLike = "/",
        hostname: str | None = None,
        effective_uid: int | None = None,
        runner=_default_runner,
        executable_finder=shutil.which,
        owner_uid=None,
        chown=os.chown,
        environ=None,
    ):
        self.workdir_logical = workdir
        self.system_root = Path(system_root)
        self.hostname = hostname if hostname is not None else _system_hostname()
        self.effective_uid = effective_uid if effective_uid is not None else _effective_uid()
        self.runner = runner
        self.executable_finder = executable_finder
        self.owner_uid = owner_uid or (lambda path: Path(path).lstat().st_uid)
        self.chown = chown
        self.environ = dict(os.environ if environ is None else environ)
        self.work_path = None
        self._lock_local = None

    def _system_path(self, logical: str) -> Path:
        pure = PurePosixPath(logical)
        if not pure.is_absolute() or ".." in pure.parts:
            raise ControllerError("invalid managed path")
        return self.system_root.joinpath(*pure.parts[1:])

    def _guard(self):
        host = str(self.hostname).split(".", 1)[0].lower()
        if host != HOST_SHORT_NAME:
            raise ControllerError("host safety guard rejected this machine")
        if self.effective_uid != 0:
            raise ControllerError("effective UID must be 0")

    def _validate_workdir(self):
        if not isinstance(self.workdir_logical, str) or "\\" in self.workdir_logical:
            raise ControllerError("workdir must be an absolute POSIX path")
        pure = PurePosixPath(self.workdir_logical)
        match = WORKDIR_RE.fullmatch(pure.name)
        if not pure.is_absolute() or pure.parent != PurePosixPath("/root") or not match or ".." in pure.parts:
            raise ControllerError("workdir must be a new /root/aurelia-access-<UTCstamp> directory")
        try:
            dt.datetime.strptime(match.group(1), "%Y%m%dT%H%M%SZ")
        except ValueError as exc:
            raise ControllerError("workdir UTC stamp is invalid") from exc
        self.work_path = self._system_path(self.workdir_logical)

    def _check_directory(self, path: Path, *, mode: int | None = None, owner=0):
        try:
            info = path.lstat()
        except OSError as exc:
            raise ControllerError("required directory is absent") from exc
        if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode) or self.owner_uid(path) != owner:
            raise ControllerError("directory type or owner is unsafe")
        if mode is not None and stat.S_IMODE(info.st_mode) != mode:
            raise ControllerError("directory mode is unsafe")

    def _check_regular(self, path: Path, *, owner=0):
        try:
            info = path.lstat()
        except OSError as exc:
            raise ControllerError("required configuration file is absent") from exc
        if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode) or self.owner_uid(path) != owner:
            raise ControllerError("configuration file type or owner is unsafe")
        if info.st_size > MAX_CONFIG_BYTES:
            raise ControllerError("configuration file exceeds the bounded size")
        return info

    def _read_regular(self, path: Path, *, owner=0) -> tuple[bytes, os.stat_result]:
        self._check_regular(path, owner=owner)
        flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
        try:
            fd = os.open(path, flags)
        except OSError as exc:
            raise ControllerError("configuration file could not be opened safely") from exc
        try:
            info = os.fstat(fd)
            if not stat.S_ISREG(info.st_mode) or info.st_size > MAX_CONFIG_BYTES or self.owner_uid(path) != owner:
                raise ControllerError("configuration file changed during safe open")
            path_info = path.lstat()
            if stat.S_ISLNK(path_info.st_mode) or path_info.st_dev != info.st_dev or path_info.st_ino != info.st_ino:
                raise ControllerError("configuration path changed during safe open")
            chunks = []
            remaining = MAX_CONFIG_BYTES + 1
            while remaining:
                chunk = os.read(fd, min(65536, remaining))
                if not chunk:
                    break
                chunks.append(chunk)
                remaining -= len(chunk)
            data = b"".join(chunks)
            if len(data) > MAX_CONFIG_BYTES:
                raise ControllerError("configuration file exceeds the bounded size")
            return data, info
        finally:
            os.close(fd)

    def _bin(self, name: str) -> str:
        found = self.executable_finder(name)
        if not found:
            raise ControllerError("required system dependency is absent")
        return str(found)

    def _run(self, argv, *, allow_nonzero=False, strict_stderr=False):
        result = self.runner([str(part) for part in argv], capture_output=True, text=True, timeout=30, check=False)
        if isinstance(result, subprocess.CompletedProcess):
            result = CommandResult(result.returncode, result.stdout or "", result.stderr or "")
        if not isinstance(result, CommandResult):
            raise ControllerError("command runner returned an invalid result")
        if strict_stderr and result.stderr.strip():
            raise ControllerError("system command reported a warning or error")
        if result.returncode != 0 and not allow_nonzero:
            raise ControllerError("system command failed: " + Path(str(argv[0])).name)
        return result

    def _dependencies(self):
        for name in ("sshd", "ufw", "systemd-run", "systemctl", "useradd", "usermod", "getent", "id", "passwd"):
            self._bin(name)

    def _create_workdir(self):
        root = self._system_path("/root")
        self._check_directory(root)
        if self.work_path.exists() or self.work_path.is_symlink():
            raise ControllerError("workdir already exists; refusing unknown files")
        try:
            self.work_path.mkdir(mode=0o700)
            os.chmod(self.work_path, 0o700)
            self.chown(self.work_path, 0, 0)
        except OSError as exc:
            raise ControllerError("could not create the root-only workdir") from exc
        self._check_directory(self.work_path, mode=0o700)
        lock_path = self.work_path / "lock"
        self._create_file(lock_path, b"0", 0o600, exclusive=True)

    def _create_file(self, path: Path, data: bytes, mode: int, *, exclusive=True, owner=0, group=None):
        flags = os.O_WRONLY | os.O_CREAT | getattr(os, "O_NOFOLLOW", 0)
        flags |= os.O_EXCL if exclusive else os.O_TRUNC
        try:
            fd = os.open(path, flags, mode)
        except OSError as exc:
            raise ControllerError("refusing to overwrite or follow an unexpected file") from exc
        try:
            os.fchmod(fd, mode)
            try:
                os.fchown(fd, owner, owner if group is None else group)
            except (AttributeError, PermissionError):
                self.chown(path, owner, owner if group is None else group)
            view = memoryview(data)
            while view:
                written = os.write(fd, view)
                if written <= 0:
                    raise ControllerError("short write")
                view = view[written:]
            os.fsync(fd)
        except Exception:
            os.close(fd)
            if exclusive:
                with contextlib.suppress(OSError):
                    path.unlink()
            raise
        os.close(fd)
        try:
            self._fsync_directory(path.parent)
        except OSError as exc:
            if exclusive:
                with contextlib.suppress(OSError):
                    path.unlink()
            raise ControllerError("file directory entry could not be synced") from exc
        return path.lstat()

    @staticmethod
    def _fsync_directory(path: Path):
        fd = os.open(path, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
        try:
            os.fsync(fd)
        finally:
            os.close(fd)

    @contextlib.contextmanager
    def _locked(self):
        path = self.work_path / "lock"
        self._check_regular(path, owner=0)
        flags = os.O_RDWR | getattr(os, "O_NOFOLLOW", 0)
        fd = os.open(path, flags)
        try:
            info = os.fstat(fd)
            if not stat.S_ISREG(info.st_mode) or self.owner_uid(path) != 0:
                raise ControllerError("transaction lock is unsafe")
            if fcntl is not None:
                fcntl.flock(fd, fcntl.LOCK_EX)
            elif msvcrt is not None:
                os.lseek(fd, 0, os.SEEK_SET)
                msvcrt.locking(fd, msvcrt.LK_LOCK, 1)
            else:
                raise ControllerError("a process lock is unavailable")
            yield
        finally:
            if fcntl is not None:
                fcntl.flock(fd, fcntl.LOCK_UN)
            elif msvcrt is not None:
                os.lseek(fd, 0, os.SEEK_SET)
                with contextlib.suppress(OSError):
                    msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
            os.close(fd)

    def _check_existing_workdir(self):
        self._check_directory(self._system_path("/root"))
        self._check_directory(self.work_path, mode=0o700)
        expected = {"lock", "manifest.json", "state.json", "rollback.py", "backup"}
        try:
            names = {item.name for item in self.work_path.iterdir()}
        except OSError as exc:
            raise ControllerError("workdir cannot be inspected") from exc
        for name in names - expected:
            if not re.fullmatch(r"state\.json\.tmp-\d+-\d+", name):
                raise ControllerError("workdir contains unknown files")
            temp_info = self._check_regular(self.work_path / name, owner=0)
            if stat.S_IMODE(temp_info.st_mode) != 0o600:
                raise ControllerError("transaction temporary file mode is unsafe")
        self._check_regular(self.work_path / "lock", owner=0)

    def _read_json(self, name: str):
        path = self.work_path / name
        data, _ = self._read_regular(path, owner=0)
        try:
            value = json.loads(data.decode("utf-8"))
        except (UnicodeError, json.JSONDecodeError) as exc:
            raise ControllerError("transaction record is invalid") from exc
        if not isinstance(value, dict):
            raise ControllerError("transaction record is invalid")
        return value

    def _write_json(self, name: str, value: dict, *, create=False):
        data = (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
        path = self.work_path / name
        if create:
            self._create_file(path, data, 0o600, exclusive=True)
            return
        self._check_regular(path, owner=0)
        temp = self.work_path / (name + ".tmp-" + str(os.getpid()) + "-" + str(time.monotonic_ns()))
        self._create_file(temp, data, 0o600, exclusive=True)
        try:
            os.replace(temp, path)
            self._fsync_directory(path.parent)
        except OSError as exc:
            with contextlib.suppress(OSError):
                temp.unlink()
            raise ControllerError("transaction record could not be updated atomically") from exc

    def _ssh_files(self):
        sshd = self._system_path("/etc/ssh/sshd_config")
        sshd_dir = self._system_path("/etc/ssh/sshd_config.d")
        self._check_regular(sshd)
        self._check_directory(sshd_dir)
        result = [("ssh", "/etc/ssh/sshd_config", sshd)]
        try:
            children = sorted(sshd_dir.iterdir(), key=lambda item: item.name)
        except OSError as exc:
            raise ControllerError("SSH include directory cannot be inspected") from exc
        for path in children:
            if path.name.endswith(".conf"):
                self._check_regular(path)
                result.append(("ssh", "/etc/ssh/sshd_config.d/" + path.name, path))
            elif path.is_symlink():
                raise ControllerError("SSH include directory contains a symlink")
        return result

    def _ufw_files(self):
        default = self._system_path("/etc/default/ufw")
        base = self._system_path("/etc/ufw")
        self._check_regular(default)
        self._check_directory(base)
        found = [("ufw", "/etc/default/ufw", default)]
        for root, dirs, files in os.walk(base, topdown=True, followlinks=False):
            root_path = Path(root)
            for name in sorted(dirs):
                child = root_path / name
                info = child.lstat()
                if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode) or self.owner_uid(child) != 0:
                    raise ControllerError("UFW configuration tree contains an unsafe directory")
            for name in sorted(files):
                child = root_path / name
                self._check_regular(child)
                rel = child.relative_to(self._system_path("/etc")).as_posix()
                found.append(("ufw", "/etc/" + rel, child))
        return found

    def _inventory(self):
        entries = self._ssh_files() + self._ufw_files()
        seen = set()
        result = []
        for category, logical, path in entries:
            if logical in seen:
                raise ControllerError("duplicate managed configuration path")
            seen.add(logical)
            data, info = self._read_regular(path)
            result.append({
                "path": logical,
                "category": category,
                "sha256": _sha256(data),
                "mode": stat.S_IMODE(info.st_mode),
                "uid": self.owner_uid(path),
                "gid": info.st_gid,
                "dev": info.st_dev,
                "ino": info.st_ino,
                "size": len(data),
            })
        return result

    def _ufw_active(self) -> bool:
        result = self._run([self._bin("ufw"), "status"], strict_stderr=True)
        first = next((line.strip() for line in result.stdout.splitlines() if line.strip()), "")
        if first == "Status: active":
            return True
        if first == "Status: inactive":
            return False
        raise ControllerError("UFW status is not a recognized active/inactive state")

    def _ipv6_enabled(self):
        path = self._system_path("/etc/default/ufw")
        data, _ = self._read_regular(path)
        values = []
        for line in data.decode("utf-8", errors="strict").splitlines():
            stripped = line.strip()
            if stripped.startswith("IPV6") and "=" in stripped and not stripped.startswith("#"):
                key, value = stripped.split("=", 1)
                if key.strip() == "IPV6":
                    values.append(value.strip().strip("\"'"))
        if not values or values[-1].lower() != "yes":
            raise ControllerError("UFW IPv6 support must already be enabled")

    def _file_bytes(self, logical: str) -> bytes:
        path = self._backup_path(logical)
        data, info = self._read_regular(path, owner=0)
        if stat.S_IMODE(info.st_mode) != 0o600 or info.st_gid != 0:
            raise ControllerError("backup file permissions are unsafe")
        return data

    def _backup_path(self, logical: str):
        if not isinstance(logical, str) or not logical.startswith(("/etc/ssh/", "/etc/default/ufw", "/etc/ufw/")):
            raise ControllerError("backup path is outside the fixed configuration scope")
        root = self.work_path / "backup"
        parts = PurePosixPath(logical).parts[1:]
        if not parts:
            raise ControllerError("backup path is invalid")
        self._check_directory(root, mode=0o700)
        cursor = root
        for part in parts[:-1]:
            cursor = cursor / part
            self._check_directory(cursor, mode=0o700)
        return cursor / parts[-1]

    def _write_rollback_helper(self):
        """Copy this exact stdlib controller so the timer uses the same rollback code."""
        source = Path(__file__)
        try:
            info = source.lstat()
            if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode):
                raise ControllerError("controller source must be a regular file for rollback scheduling")
            script = source.read_bytes()
        except OSError as exc:
            raise ControllerError("controller source is unavailable for rollback scheduling") from exc
        self._create_file(self.work_path / "rollback.py", script, 0o700, exclusive=True)
        return _sha256(script)

    def _timer_unit(self, state=None):
        if state is None:
            state = self._read_json("state.json")
        unit = state.get("timer_unit")
        if not isinstance(unit, str) or not re.fullmatch(r"aurelia-access-\d{8}T\d{6}Z-rollback", unit):
            raise ControllerError("rollback timer identity is invalid")
        return unit

    def _timer_property(self, unit: str, prop: str):
        result = self._run([self._bin("systemctl"), "show", unit, "--property=" + prop, "--value"], allow_nonzero=True, strict_stderr=True)
        if result.returncode != 0:
            return None
        return result.stdout.strip()

    def _timer_info(self, state=None):
        unit = self._timer_unit(state)
        timer = unit + ".timer"
        return {
            "unit": timer,
            "active": self._timer_property(timer, "ActiveState"),
            "substate": self._timer_property(timer, "SubState"),
            "last_trigger": self._timer_property(timer, "LastTriggerUSec"),
            "next_monotonic_us": self._timer_property(timer, "NextElapseUSecMonotonic"),
            "service_active": self._timer_property(unit + ".service", "ActiveState"),
        }

    def _timer_is_pending(self, info):
        if info["active"] != "active" or info["substate"] != "waiting" or info["last_trigger"] not in ("0", "0.000000", ""):
            return False
        return self._timer_remaining_seconds(info["next_monotonic_us"]) > 0 and info["service_active"] in (None, "inactive", "failed")

    @staticmethod
    def _timer_deadline_monotonic_seconds(value):
        if not isinstance(value, str):
            return 0.0
        factors = {"ns": 1e-9, "us": 1e-6, "\u00b5s": 1e-6, "ms": 1e-3, "s": 1.0, "min": 60.0, "m": 60.0, "h": 3600.0, "d": 86400.0, "w": 604800.0}
        token = re.compile(r"(\d+(?:\.\d+)?)(ns|us|\u00b5s|ms|min|m|h|d|w|s)")
        rest = value.strip()
        if not rest:
            return 0.0
        seconds = 0.0
        while rest:
            rest = rest.lstrip()
            match = token.match(rest)
            if not match:
                return 0.0
            seconds += float(match.group(1)) * factors[match.group(2)]
            rest = rest[match.end():]
        return seconds

    @classmethod
    def _timer_remaining_seconds(cls, value):
        # systemd reports NextElapseUSecMonotonic as an absolute since-boot timespan.
        return cls._timer_deadline_monotonic_seconds(value) - time.monotonic()

    def _require_pending_timer(self, state, *, minimum_remaining_seconds=0):
        info = self._timer_info(state)
        remaining = self._timer_remaining_seconds(info["next_monotonic_us"])
        if not self._timer_is_pending(info):
            raise ControllerError("rollback timer is missing, expired, or already triggered")
        if remaining < minimum_remaining_seconds:
            raise ControllerError("rollback timer has insufficient time remaining")
        return info

    def _schedule_rollback(self, state):
        unit = self._timer_unit(state)
        timer = unit + ".timer"
        load_state = self._timer_property(timer, "LoadState")
        if load_state != "not-found":
            raise ControllerError("unique rollback timer name already exists")
        python = str(Path(sys.executable).resolve())
        helper = self.workdir_logical + "/rollback.py"
        result = self._run([
            self._bin("systemd-run"), "--quiet", "--on-active=15min", "--unit=" + unit,
            "--timer-property=AccuracySec=1s", python, helper, "--workdir", self.workdir_logical,
            "rollback",
        ])
        expected_message = "Running timer as unit: " + timer
        if result.stderr.strip() not in ("", expected_message):
            raise ControllerError("systemd-run reported an unexpected warning or error")
        info = self._timer_info(state)
        if info["active"] != "active" or info["substate"] != "waiting":
            raise ControllerError("rollback timer did not become active")
        self._require_pending_timer(state, minimum_remaining_seconds=MIN_APPLY_ROLLBACK_SECONDS)

    def prepare(self):
        self._guard()
        self._validate_workdir()
        self._dependencies()
        # Complete every read-only preflight before creating the transaction directory.
        self._run([self._bin("sshd"), "-t"], strict_stderr=True)
        self._ipv6_enabled()
        original_ufw_active = self._ufw_active()
        inventory = self._inventory()
        if self._system_path(SSH_SNIPPET).exists() or self._system_path(SSH_SNIPPET).is_symlink():
            raise ControllerError("unique SSH snippet path is already occupied")
        stamp = WORKDIR_RE.fullmatch(PurePosixPath(self.workdir_logical).name).group(1)
        timer_unit = "aurelia-access-" + stamp + "-rollback"
        if self._timer_property(timer_unit + ".timer", "LoadState") != "not-found":
            raise ControllerError("unique rollback timer name already exists")
        self._create_workdir()
        with self._locked():
            for entry in inventory:
                logical = entry["path"]
                data, source_info = self._read_regular(self._system_path(logical))
                if (
                    _sha256(data) != entry["sha256"]
                    or stat.S_IMODE(source_info.st_mode) != entry["mode"]
                    or source_info.st_gid != entry["gid"]
                    or self.owner_uid(self._system_path(logical)) != entry["uid"]
                ):
                    raise ControllerError("configuration changed while its backup was being made")
                components = logical.lstrip("/").split("/")
                cursor = self.work_path
                for component in ("backup", *components[:-1]):
                    cursor = cursor / component
                    try:
                        cursor.mkdir(mode=0o700)
                    except FileExistsError:
                        pass
                    self._check_directory(cursor, mode=0o700)
                    self.chown(cursor, 0, 0)
                    self._fsync_directory(cursor.parent)
                target = cursor / components[-1]
                self._create_file(target, data, 0o600, exclusive=True)
                entry["backup"] = "backup/" + logical.lstrip("/")
            latest = {item["path"]: item for item in self._inventory()}
            if set(latest) != {item["path"] for item in inventory}:
                raise ControllerError("configuration drifted during backup creation")
            if any(
                any(latest[entry["path"]].get(field) != entry.get(field) for field in ("sha256", "mode", "uid", "gid"))
                for entry in inventory
            ):
                raise ControllerError("configuration drifted during backup creation")
            if self._ufw_active() != original_ufw_active:
                raise ControllerError("UFW active state changed during backup creation")
            manifest = {"version": 1, "workdir": self.workdir_logical, "files": inventory}
            self._write_json("manifest.json", manifest, create=True)
            state = {
                "version": 1,
                "workdir": self.workdir_logical,
                "phase": "preparing",
                "created_at": _utc_now(),
                "original_ufw_active": original_ufw_active,
                "timer_unit": timer_unit,
                "changes": [],
                "rollback_progress": {},
                "user": {"name": OPS_USER, "home": OPS_HOME, "created": False},
            }
            self._write_json("state.json", state, create=True)
            state["rollback_helper_sha256"] = self._write_rollback_helper()
            self._write_json("state.json", state)
            self._schedule_rollback(state)
            state["phase"] = "prepared"
            state["prepared_at"] = _utc_now()
            self._write_json("state.json", state)
        return {"ok": True, "action": "prepare", "phase": "prepared", "workdir": self.workdir_logical, "rollback_timer": self._timer_info(state)}

    def _load_transaction(self):
        self._guard()
        self._validate_workdir()
        self._check_existing_workdir()
        manifest = self._read_json("manifest.json")
        state = self._read_json("state.json")
        if manifest.get("version") != 1 or manifest.get("workdir") != self.workdir_logical:
            raise ControllerError("backup manifest binding is invalid")
        if state.get("version") != 1 or state.get("workdir") != self.workdir_logical:
            raise ControllerError("transaction state binding is invalid")
        helper, helper_info = self._read_regular(self.work_path / "rollback.py", owner=0)
        if stat.S_IMODE(helper_info.st_mode) != 0o700 or _sha256(helper) != state.get("rollback_helper_sha256"):
            raise ControllerError("rollback helper does not match its recorded source hash")
        self._verify_backups(manifest)
        return manifest, state

    def _verify_backups(self, manifest):
        if not isinstance(manifest.get("files"), list):
            raise ControllerError("backup manifest file list is invalid")
        for entry in manifest["files"]:
            logical = entry.get("path")
            if not isinstance(logical, str) or not logical.startswith(("/etc/ssh/", "/etc/default/ufw", "/etc/ufw/")):
                raise ControllerError("backup manifest contains an out-of-scope path")
            data = self._file_bytes(logical)
            if _sha256(data) != entry.get("sha256") or len(data) != entry.get("size"):
                raise ControllerError("backup contents do not match the manifest")

    def _verify_snapshot_unchanged(self, manifest, state):
        current = self._inventory()
        baseline = {entry["path"]: entry for entry in manifest["files"]}
        current_map = {entry["path"]: entry for entry in current}
        if set(current_map) != set(baseline):
            raise ControllerError("configuration path set drifted after prepare")
        for logical, expected in baseline.items():
            now = current_map[logical]
            if any(now.get(field) != expected.get(field) for field in ("sha256", "mode", "uid", "gid")):
                raise ControllerError("configuration drifted after prepare")
        if self._ufw_active() != state.get("original_ufw_active"):
            raise ControllerError("UFW active state drifted after prepare")
        if self._system_path(SSH_SNIPPET).exists() or self._system_path(SSH_SNIPPET).is_symlink():
            raise ControllerError("unique SSH snippet path is already occupied")

    def _get_user(self):
        result = self._run([self._bin("getent"), "passwd", OPS_USER], allow_nonzero=True, strict_stderr=True)
        if result.returncode != 0:
            return None
        fields = result.stdout.strip().split(":")
        if len(fields) < 7 or fields[0] != OPS_USER:
            raise ControllerError("user database returned unexpected account data")
        try:
            uid, gid = int(fields[2]), int(fields[3])
        except ValueError as exc:
            raise ControllerError("user database returned an invalid UID/GID") from exc
        return {"uid": uid, "gid": gid, "home": fields[5], "shell": fields[6]}

    def _group_names(self):
        result = self._run([self._bin("id"), "-nG", OPS_USER], strict_stderr=True)
        groups = result.stdout.split()
        if groups != [OPS_USER]:
            raise ControllerError("aurelia-ops has unexpected supplementary groups")
        primary = self._run([self._bin("id"), "-gn", OPS_USER], strict_stderr=True).stdout.strip()
        if primary != OPS_USER:
            raise ControllerError("aurelia-ops primary group is unexpected")
        return groups

    def _verify_user_paths(self, user):
        if user["uid"] == 0 or user["home"] != OPS_HOME:
            raise ControllerError("aurelia-ops account identity is unsafe")
        home = self._system_path(OPS_HOME)
        self._check_directory(home, owner=user["uid"])
        ssh_dir = home / ".ssh"
        auth = ssh_dir / "authorized_keys"
        self._check_directory(ssh_dir, mode=0o700, owner=user["uid"])
        self._check_regular(auth, owner=user["uid"])
        if stat.S_IMODE(auth.lstat().st_mode) != 0o600:
            raise ControllerError("authorized_keys mode is not 0600")
        return auth

    def create_user(self, public_key: str):
        self._guard()
        self._validate_workdir()
        _require_unexpired_key()
        normalized_key = validate_public_key(public_key)
        self._check_existing_workdir()
        with self._locked():
            manifest, state = self._load_transaction()
            if state.get("phase") != "prepared":
                raise ControllerError("create-user is allowed only after prepare")
            if self._get_user() is not None:
                raise ControllerError("aurelia-ops already exists")
            group = self._run([self._bin("getent"), "group", OPS_USER], allow_nonzero=True, strict_stderr=True)
            if group.returncode == 0:
                raise ControllerError("aurelia-ops group already exists")
            if group.returncode != 2:
                raise ControllerError("group database lookup failed")
            home = self._system_path(OPS_HOME)
            if home.exists() or home.is_symlink():
                raise ControllerError("/home/aurelia-ops already exists")
            self._run([self._bin("useradd"), "-m", "-U", "-s", "/bin/bash", OPS_USER], strict_stderr=True)
            user = self._get_user()
            if user is None or user["shell"] != "/bin/bash":
                raise ControllerError("useradd did not create the expected account")
            self._group_names()
            self._run([self._bin("usermod"), "--lock", OPS_USER], strict_stderr=True)
            password = self._run([self._bin("passwd"), "-S", OPS_USER], strict_stderr=True)
            password_fields = password.stdout.split()
            if len(password_fields) < 2 or password_fields[0] != OPS_USER or password_fields[1] not in ("L", "LK"):
                raise ControllerError("aurelia-ops password is not locked")
            self._check_directory(home, owner=user["uid"])
            ssh_dir = home / ".ssh"
            if ssh_dir.exists() or ssh_dir.is_symlink():
                raise ControllerError("new account already contains an unexpected .ssh directory")
            try:
                ssh_dir.mkdir(mode=0o700)
                os.chmod(ssh_dir, 0o700)
                self.chown(ssh_dir, user["uid"], user["gid"])
                self._create_file(ssh_dir / "authorized_keys", (f'restrict,expiry-time="{KEY_EXPIRY}" ' + normalized_key + "\n").encode(), 0o600, exclusive=True, owner=user["uid"], group=user["gid"])
                self.chown(ssh_dir / "authorized_keys", user["uid"], user["gid"])
            except Exception:
                # The newly-created account remains locked and without elevated groups.
                raise
            auth = self._verify_user_paths(user)
            auth_data, _ = self._read_regular(auth, owner=user["uid"])
            state["phase"] = "user_created"
            state["user"] = {
                "name": OPS_USER,
                "uid": user["uid"],
                "gid": user["gid"],
                "home": OPS_HOME,
                "groups": [OPS_USER],
                "password_locked": True,
                "authorized_keys_mode": stat.S_IMODE(auth.lstat().st_mode),
                "authorized_keys_sha256": _sha256(auth_data),
                "key_expiry": KEY_EXPIRY,
                "created": True,
                "privileged_groups": [],
            }
            state["user_created_at"] = _utc_now()
            self._write_json("state.json", state)
        return {"ok": True, "action": "create-user", "phase": "user_created", "user": state["user"]}

    def record_user_login(self, parent_verified_uid: int):
        self._guard()
        self._validate_workdir()
        self._check_existing_workdir()
        with self._locked():
            manifest, state = self._load_transaction()
            if state.get("phase") != "user_created":
                raise ControllerError("user-login attestation requires the created account")
            user = self._get_user()
            self._group_names()
            if user is None or user["uid"] != int(parent_verified_uid) or user["uid"] == 0:
                raise ControllerError("parent-verified UID does not match aurelia-ops")
            self._verify_ops_key_policy(user, state)
            state["user_login_attestation"] = {
                "parent_verified_uid": user["uid"],
                "recorded_at": _utc_now(),
                "verified_by_controller": False,
            }
            self._write_json("state.json", state)
        return {"ok": True, "action": "record-user-login", "phase": state["phase"], "attestation_recorded": True}

    def _ssh_connection(self):
        raw = self.environ.get("SSH_CONNECTION", "")
        fields = raw.split()
        if len(fields) != 4:
            raise ControllerError("SSH_CONNECTION is required; source addresses are never hardcoded")
        try:
            client_ip = str(ipaddress.ip_address(fields[0]))
            server_ip = str(ipaddress.ip_address(fields[2]))
            client_port, server_port = int(fields[1]), int(fields[3])
        except ValueError as exc:
            raise ControllerError("SSH_CONNECTION is invalid") from exc
        if not (1 <= client_port <= 65535 and 1 <= server_port <= 65535):
            raise ControllerError("SSH_CONNECTION port is invalid")
        return {"client_ip": client_ip, "client_port": client_port, "server_ip": server_ip, "server_port": server_port}

    def _effective_ssh(self, context):
        sshd = self._bin("sshd")
        result_map = {}
        for user in ("root", OPS_USER):
            context_text = (
                f"user={user},addr={context['client_ip']},host={context['client_ip']},"
                f"laddr={context['server_ip']},lport={context['server_port']}"
            )
            result = self._run([sshd, "-T", "-C", context_text], strict_stderr=True)
            settings = {}
            for line in result.stdout.splitlines():
                fields = line.split(None, 1)
                if len(fields) == 2:
                    key, value = fields[0].lower(), fields[1].strip().lower()
                    if key == "permitrootlogin" and value == "without-password":
                        value = "prohibit-password"
                    settings[key] = value
            for name, expected in SSH_SETTINGS.items():
                if settings.get(name) != expected:
                    raise ControllerError("effective SSH setting failed validation")
            if user == "root" and settings.get("permitrootlogin") == "no":
                raise ControllerError("root public-key access would be disabled")
            result_map[user] = {name: settings[name] for name in SSH_SETTINGS}
        return result_map

    def _intent_allowlist(self, name):
        if name == "ssh_snippet":
            return {SSH_SNIPPET}
        if name in ("ufw_default_deny_incoming", "ufw_default_allow_outgoing", "ufw_allow_ssh_ipv4", "ufw_enable"):
            return set(UFW_MUTABLE_PATHS)
        raise ControllerError("unknown configuration mutation intent")

    def _begin_intent(self, manifest, state, name, paths):
        if state.get("active_intent"):
            raise ControllerError("a previous configuration mutation intent is still active")
        allowed = self._intent_allowlist(name)
        chosen = tuple(sorted(set(paths)))
        if not chosen or not set(chosen) <= allowed:
            raise ControllerError("mutation intent exceeds its fixed path allowlist")
        self._verify_tracked_snapshot(manifest, state)
        before = {logical: self._current_record(logical) for logical in chosen}
        state["active_intent"] = {"name": name, "paths": list(chosen), "before": before, "started_at": _utc_now()}
        self._write_json("state.json", state)

    def _verify_tracked_snapshot(self, manifest, state, *, intent_paths=()):
        expected = self._expected_records(manifest, state)
        expected_present = {path: record for path, record in expected.items() if record is not None}
        current = {item["path"]: item for item in self._inventory()}
        permitted = set(intent_paths)
        if (set(expected_present) - set(current) - permitted) or (set(current) - set(expected_present) - permitted):
            raise ControllerError("configuration path set drifted outside the active mutation intent")
        for logical in (set(expected_present) & set(current)) - permitted:
            if not self._matches(current[logical], expected_present[logical]):
                raise ControllerError("configuration drifted outside the active mutation intent")
        for logical, record in expected.items():
            if record is None and logical in current and logical not in permitted:
                raise ControllerError("unexpected managed configuration file appeared")
        return current

    def _capture_changes(self, manifest, state, *, include_paths=None, clear_intent=True):
        baseline = {entry["path"]: entry for entry in manifest["files"]}
        intent = state.get("active_intent")
        if include_paths is not None:
            intent_paths = set(include_paths)
        elif intent:
            intent_paths = set(intent.get("paths", []))
        else:
            intent_paths = set()
        if intent_paths:
            allowed_intent_paths = self._intent_allowlist(intent["name"]) if intent else intent_paths
            if not intent_paths <= allowed_intent_paths:
                raise ControllerError("change capture exceeds its fixed path allowlist")
        current_map = self._verify_tracked_snapshot(manifest, state, intent_paths=intent_paths)
        allowed_new = {SSH_SNIPPET, *UFW_MUTABLE_PATHS}
        unexpected = set(current_map) - set(baseline) - allowed_new
        if unexpected:
            raise ControllerError("an unexpected configuration file appeared during apply")
        previous = {item["path"]: item for item in state.get("changes", [])}
        eligible = set(previous)
        if include_paths is not None:
            eligible.update(include_paths)
        elif intent:
            eligible.update(intent.get("paths", []))
        all_paths = set(baseline) | set(current_map) | {SSH_SNIPPET}
        changes = {}
        for logical in sorted(all_paths):
            before = baseline.get(logical)
            after = current_map.get(logical)
            if _stable_file_record(before) == _stable_file_record(after):
                continue
            if logical not in eligible:
                raise ControllerError("configuration changed outside the active mutation intent")
            if logical == SSH_SNIPPET and before is not None:
                raise ControllerError("unique SSH snippet existed before this transaction")
            if logical.startswith("/etc/ssh/"):
                category = "ssh"
            elif logical == "/etc/default/ufw" or logical.startswith("/etc/ufw/"):
                category = "ufw"
            else:
                raise ControllerError("changed configuration path is outside the rollback scope")
            changes[logical] = {"path": logical, "category": category, "before": before, "after": after}
        state["changes"] = list(changes.values())
        if intent and clear_intent:
            state.pop("active_intent", None)
            state["intent_completed_at"] = _utc_now()
        self._write_json("state.json", state)

    def _recover_active_intent(self, manifest, state):
        intent = state.get("active_intent")
        if not intent:
            return []
        name, paths = intent.get("name"), intent.get("paths")
        allowed = self._intent_allowlist(name)
        if not isinstance(paths, list) or not paths or not set(paths) <= allowed:
            raise ControllerError("persisted mutation intent is invalid")
        intent_before = intent.get("before")
        if not isinstance(intent_before, dict) or set(intent_before) != set(paths):
            raise ControllerError("persisted mutation intent records are invalid")
        baseline = {entry["path"]: entry for entry in manifest["files"]}
        changes = {item["path"]: item for item in state.get("changes", [])}
        errors = []
        try:
            self._verify_tracked_snapshot(manifest, state, intent_paths=paths)
        except Exception as exc:
            errors.append(str(exc) if isinstance(exc, ControllerError) else "configuration drifted during interrupted mutation")
        for logical in paths:
            try:
                current = self._current_record(logical)
                if self._matches(current, intent_before.get(logical)):
                    continue
                before = baseline.get(logical)
                if self._matches(current, before):
                    changes.pop(logical, None)
                    continue
                category = "ssh" if logical.startswith("/etc/ssh/") else "ufw"
                changes[logical] = {"path": logical, "category": category, "before": before, "after": current}
            except Exception as exc:
                errors.append(str(exc) if isinstance(exc, ControllerError) else "intent recovery could not inspect a managed path")
        state["changes"] = list(changes.values())
        state["active_intent_recovery_errors"] = errors
        if not errors:
            state.pop("active_intent", None)
        state["intent_recovered_at"] = _utc_now()
        self._write_json("state.json", state)
        return errors

    def _write_ssh_snippet(self):
        content = "\n".join(
            [
                "# Managed by the bounded LG2 access controller.",
                "PermitRootLogin prohibit-password",
                "PasswordAuthentication no",
                "KbdInteractiveAuthentication no",
                "PubkeyAuthentication yes",
                "AllowAgentForwarding no",
                "X11Forwarding no",
                "AllowTcpForwarding local",
                "GatewayPorts no",
                "PermitTunnel no",
                "PermitUserEnvironment no",
                "",
            ]
        ).encode("ascii")
        path = self._system_path(SSH_SNIPPET)
        if path.exists() or path.is_symlink():
            raise ControllerError("unique SSH snippet path is already occupied")
        self._create_file(path, content, 0o644, exclusive=True)

    def _validate_user_before_apply(self, state):
        attestation = state.get("user_login_attestation")
        user = self._get_user()
        if not isinstance(attestation, dict) or user is None or user["uid"] != attestation.get("parent_verified_uid"):
            raise ControllerError("parent record-user-login attestation is required")
        self._group_names()
        self._verify_ops_key_policy(user, state)
        return user

    def _verify_ops_key_policy(self, user, state):
        _require_unexpired_key()
        auth = self._verify_user_paths(user)
        data, _ = self._read_regular(auth, owner=user["uid"])
        expected = f'restrict,expiry-time="{KEY_EXPIRY}" '
        if data.count(b"\n") != 1 or not data.endswith(b"\n"):
            raise ControllerError("aurelia-ops key file does not match the bounded policy")
        try:
            line = data[:-1].decode("utf-8")
        except UnicodeError as exc:
            raise ControllerError("aurelia-ops key file encoding is invalid") from exc
        if not line.startswith(expected) or _sha256(data) != state.get("user", {}).get("authorized_keys_sha256"):
            raise ControllerError("aurelia-ops authorized key drifted after creation")
        validate_public_key(line[len(expected):])
        return auth

    def _validate_ufw_after_apply(self):
        if not self._ufw_active():
            raise ControllerError("UFW did not become active")
        verbose = self._run([self._bin("ufw"), "status", "verbose"], strict_stderr=True).stdout.lower()
        if not re.search(r"default:\s*deny\s*\(incoming\).*allow\s*\(outgoing\)", verbose):
            raise ControllerError("UFW default policies did not validate")
        numbered = self._run([self._bin("ufw"), "status", "numbered"], strict_stderr=True).stdout.lower()
        ssh_allows = [line for line in numbered.splitlines() if "22/tcp" in line and "allow in" in line]
        v4 = any("(v6)" not in line and ("0.0.0.0/0" in line or re.search(r"\banywhere\b", line)) for line in ssh_allows)
        v6 = any("(v6)" in line for line in ssh_allows)
        if not v4 or v6:
            raise ControllerError("UFW must allow SSH on IPv4 only")

    def apply(self):
        self._guard()
        self._validate_workdir()
        self._check_existing_workdir()
        with self._locked():
            manifest, state = self._load_transaction()
            if state.get("phase") != "user_created":
                raise ControllerError("apply requires the created user and fresh parent login attestation")
            self._validate_user_before_apply(state)
            self._verify_snapshot_unchanged(manifest, state)
            self._require_pending_timer(state, minimum_remaining_seconds=MIN_APPLY_ROLLBACK_SECONDS)
            context = self._ssh_connection()
            state["phase"] = "applying"
            state["ssh_context"] = context
            state["apply_started_at"] = _utc_now()
            state["changes"] = []
            self._write_json("state.json", state)
            try:
                self._begin_intent(manifest, state, "ssh_snippet", (SSH_SNIPPET,))
                self._write_ssh_snippet()
                self._capture_changes(manifest, state)
                self._run([self._bin("sshd"), "-t"], strict_stderr=True)
                effective = self._effective_ssh(context)
                state["effective_ssh_before_reload"] = effective
                self._write_json("state.json", state)
                self._ipv6_enabled()
                for intent_name, args in (
                    ("ufw_default_deny_incoming", ("default", "deny", "incoming")),
                    ("ufw_default_allow_outgoing", ("default", "allow", "outgoing")),
                    ("ufw_allow_ssh_ipv4", ("allow", "in", "proto", "tcp", "from", "0.0.0.0/0", "to", "any", "port", "22")),
                    ("ufw_enable", ("--force", "enable")),
                ):
                    self._begin_intent(manifest, state, intent_name, UFW_MUTABLE_PATHS)
                    self._run([self._bin("ufw"), *args], strict_stderr=True)
                    self._capture_changes(manifest, state)
                self._validate_ufw_after_apply()
                self._run([self._bin("sshd"), "-t"], strict_stderr=True)
                self._run([self._bin("systemctl"), "reload", "ssh.service"], strict_stderr=True)
                active = self._run([self._bin("systemctl"), "is-active", "ssh.service"], strict_stderr=True)
                if active.stdout.strip() != "active":
                    raise ControllerError("SSH service did not remain active after reload")
                state["phase"] = "applied"
                state["applied_at"] = _utc_now()
                state["effective_ssh"] = self._effective_ssh(context)
                state["ufw_active"] = True
                self._capture_changes(manifest, state)
                return {"ok": True, "action": "apply", "phase": "applied", "effective_ssh": state["effective_ssh"], "rollback_timer": self._timer_info(state)}
            except Exception as exc:
                failure = exc if isinstance(exc, ControllerError) else ControllerError("apply failed before completion")
                try:
                    self._rollback_locked(manifest, state, reason="apply_failure")
                except Exception as rollback_exc:
                    raise ControllerError(f"{failure}; rollback also failed: {rollback_exc}; timer remains scheduled") from rollback_exc
                raise ControllerError(f"{failure}; immediate rollback attempted and timer remains scheduled") from exc

    def _current_record(self, logical):
        path = self._system_path(logical)
        if not path.exists() and not path.is_symlink():
            return None
        data, info = self._read_regular(path)
        category = "ssh" if logical.startswith("/etc/ssh/") else "ufw"
        return {
            "path": logical,
            "category": category,
            "sha256": _sha256(data),
            "mode": stat.S_IMODE(info.st_mode),
            "uid": self.owner_uid(path),
            "gid": info.st_gid,
            "dev": info.st_dev,
            "ino": info.st_ino,
            "size": len(data),
        }

    def _matches(self, actual, expected):
        return _stable_file_record(actual) == _stable_file_record(expected)

    def _restore_file(self, change, state):
        logical = change["path"]
        if not (logical.startswith("/etc/ssh/") or logical == "/etc/default/ufw" or logical.startswith("/etc/ufw/")):
            raise ControllerError("rollback path is outside the fixed configuration scope")
        path = self._system_path(logical)
        self._remove_stale_restore_temps(path)
        before, after = change.get("before"), change.get("after")
        current = self._current_record(logical)
        progress = state.setdefault("rollback_progress", {})
        if self._matches(current, before):
            progress[logical] = "restored"
            self._write_json("state.json", state)
            return
        if not self._matches(current, after):
            raise ControllerError("rollback conflict: managed file changed after apply")
        if before is None:
            current_info = path.lstat()
            if not stat.S_ISREG(current_info.st_mode) or stat.S_ISLNK(current_info.st_mode) or self.owner_uid(path) != 0:
                raise ControllerError("rollback refuses an unexpected created file")
            # Recheck identity and bytes immediately before removal.
            if not self._matches(self._current_record(logical), after):
                raise ControllerError("rollback created-file identity changed")
            path.unlink()
            self._fsync_directory(path.parent)
        else:
            data = self._file_bytes(logical)
            if _sha256(data) != before.get("sha256") or len(data) != before.get("size"):
                raise ControllerError("backup bytes failed the original hash check")
            parent = path.parent
            temp = parent / ("." + path.name + ".lg2-restore-" + str(os.getpid()) + "-" + str(time.monotonic_ns()))
            self._create_file(temp, data, before["mode"], exclusive=True, owner=before["uid"], group=before["gid"])
            try:
                temp_data, temp_info = self._read_regular(temp, owner=before["uid"])
                if (
                    _sha256(temp_data) != before["sha256"]
                    or stat.S_IMODE(temp_info.st_mode) != before["mode"]
                    or temp_info.st_gid != before["gid"]
                ):
                    raise ControllerError("atomic rollback temporary failed metadata/hash validation")
                latest = self._current_record(logical)
                if not self._matches(latest, after):
                    raise ControllerError("rollback target changed before atomic replacement")
                if latest is not None and (latest.get("dev") != after.get("dev") or latest.get("ino") != after.get("ino")):
                    raise ControllerError("rollback target inode changed")
                if latest is None:
                    # link() creates the restored path atomically and refuses an intervening file.
                    os.link(temp, path, follow_symlinks=False)
                    temp.unlink()
                else:
                    os.replace(temp, path)
                self._fsync_directory(parent)
            finally:
                with contextlib.suppress(FileNotFoundError):
                    temp.unlink()
        progress[logical] = "restored"
        self._write_json("state.json", state)

    def _remove_stale_restore_temps(self, path):
        prefix = "." + path.name + ".lg2-restore-"
        matcher = re.compile(re.escape(prefix) + r"\d+-\d+$")
        for candidate in path.parent.iterdir():
            if not matcher.fullmatch(candidate.name):
                continue
            info = candidate.lstat()
            if not stat.S_ISREG(info.st_mode) or stat.S_ISLNK(info.st_mode) or self.owner_uid(candidate) != 0:
                raise ControllerError("stale rollback temporary is unsafe")
            candidate.unlink()
            self._fsync_directory(path.parent)

    def _restore_group(self, category, manifest, state):
        changes = [item for item in state.get("changes", []) if item.get("category") == category]
        errors = []
        restored = 0
        for change in changes:
            try:
                self._restore_file(change, state)
                restored += 1
            except Exception as exc:
                errors.append(str(exc) if isinstance(exc, ControllerError) else "file restoration failed")
        if category == "ssh":
            try:
                self._run([self._bin("sshd"), "-t"], strict_stderr=True)
                if not errors:
                    self._run([self._bin("systemctl"), "reload", "ssh.service"], strict_stderr=True)
                active = self._run([self._bin("systemctl"), "is-active", "ssh.service"], strict_stderr=True)
                if active.stdout.strip() != "active":
                    raise ControllerError("SSH service runtime did not recover")
            except Exception as exc:
                errors.append(str(exc) if isinstance(exc, ControllerError) else "SSH runtime recovery failed")
        else:
            try:
                action = "enable" if state.get("original_ufw_active") else "disable"
                self._run([self._bin("ufw"), "--force", action], strict_stderr=True)
                if self._ufw_active() != bool(state.get("original_ufw_active")):
                    raise ControllerError("UFW runtime did not return to its original active state")
            except Exception as exc:
                errors.append(str(exc) if isinstance(exc, ControllerError) else "UFW runtime recovery failed")
        return {"ok": not errors, "paths": restored, "errors": errors}

    def _rollback_locked(self, manifest, state, *, reason="manual"):
        if state.get("phase") == "committed":
            return {"ok": True, "noop": True, "reason": "committed"}
        if state.get("phase") == "rolled_back":
            return {"ok": True, "noop": True, "reason": "already_rolled_back"}
        try:
            intent_errors = self._recover_active_intent(manifest, state)
        except Exception as exc:
            intent_errors = [str(exc) if isinstance(exc, ControllerError) else "persisted intent recovery failed"]
        state["phase"] = "rolling_back"
        state["rollback_reason"] = reason
        state["rollback_started_at"] = _utc_now()
        self._write_json("state.json", state)
        outcomes = {}
        errors = ["active intent recovery: " + error for error in intent_errors]
        for category in ("ssh", "ufw"):
            try:
                outcomes[category] = self._restore_group(category, manifest, state)
                if not outcomes[category]["ok"]:
                    errors.extend(category + ": " + error for error in outcomes[category]["errors"])
            except Exception as exc:
                message = str(exc) if isinstance(exc, ControllerError) else "unexpected restoration failure"
                outcomes[category] = {"ok": False, "error": message}
                errors.append(category + ": " + message)
        state["rollback_outcomes"] = outcomes
        runtime = {}
        runtime_errors = []
        try:
            ssh_status = self._service_state("ssh.service")
            runtime["ssh_service"] = ssh_status
            if ssh_status != "active":
                runtime_errors.append("SSH service is not active after rollback")
        except Exception as exc:
            runtime["ssh_service"] = "unknown"
            runtime_errors.append("SSH runtime status could not be read")
        try:
            ufw_active = self._ufw_active()
            runtime["ufw_active"] = ufw_active
            if ufw_active != bool(state.get("original_ufw_active")):
                runtime_errors.append("UFW active state differs from its original state after rollback")
        except Exception:
            runtime["ufw_active"] = "unknown"
            runtime_errors.append("UFW runtime status could not be read")
        state["rollback_runtime"] = runtime
        state["rollback_runtime_errors"] = runtime_errors
        errors.extend(runtime_errors)
        state["rollback_finished_at"] = _utc_now()
        state["phase"] = "rollback_incomplete" if errors else "rolled_back"
        self._write_json("state.json", state)
        if errors:
            raise ControllerError("; ".join(errors))
        return {"ok": True, "action": "rollback", "phase": "rolled_back", "outcomes": outcomes, "runtime": state["rollback_runtime"]}

    def _service_state(self, unit):
        result = self._run([self._bin("systemctl"), "is-active", unit], allow_nonzero=True, strict_stderr=True)
        return result.stdout.strip() if result.stdout.strip() else "unknown"

    def rollback(self):
        self._guard()
        self._validate_workdir()
        self._check_existing_workdir()
        with self._locked():
            manifest, state = self._load_transaction()
            result = self._rollback_locked(manifest, state)
        result.update({"ok": True, "action": "rollback", "account_retained": bool(state.get("user", {}).get("created")), "account_privilege": "none-added"})
        return result

    def _stop_timer(self, state):
        unit = self._timer_unit(state)
        timer = unit + ".timer"
        info = self._timer_info(state)
        if info["active"] == "active":
            self._run([self._bin("systemctl"), "stop", timer], strict_stderr=True)
        after = self._timer_info(state)
        if after["active"] == "active":
            raise ControllerError("rollback timer remains active after stop")
        if after["service_active"] in ("active", "activating", "reloading"):
            # The service must acquire this same lock and will see the committed marker.
            return {"timer": after, "service_may_be_waiting_on_lock": True}
        return {"timer": after, "service_may_be_waiting_on_lock": False}

    def commit(self, parent_verified: bool = False):
        self._guard()
        self._validate_workdir()
        self._check_existing_workdir()
        with self._locked():
            manifest, state = self._load_transaction()
            if state.get("phase") not in ("applied", "committed"):
                raise ControllerError("commit requires a verified applied state")
            if not parent_verified:
                raise ControllerError("explicit parent verification marker is required")
            if state.get("phase") == "applied":
                effective = self._verify_applied_configuration(manifest, state)
                info = self._require_pending_timer(state)
                # The marker precedes timer stop. A concurrently-started rollback waits for this lock.
                state["phase"] = "committed"
                state["effective_ssh_at_commit"] = effective
                state["ufw_validated_at_commit"] = True
                state["parent_commit_attestation"] = {"provided": True, "recorded_at": _utc_now(), "verified_by_controller": False}
                state["committed_at"] = _utc_now()
                self._write_json("state.json", state)
            timer_result = self._stop_timer(state)
            timer_result["timer"] = self._timer_info(state)
        return {"ok": True, "action": "commit", "phase": "committed", "rollback_timer": timer_result["timer"], "rollback_service_noop_guard": "committed marker is checked under shared lock"}

    def _verify_applied_configuration(self, manifest, state):
        expected = self._expected_records(manifest, state)
        current = {item["path"]: item for item in self._inventory()}
        if set(current) != set(expected):
            raise ControllerError("configuration path set drifted before commit")
        for logical, record in expected.items():
            if not self._matches(current.get(logical), record):
                raise ControllerError("configuration hash or metadata drifted before commit")
        self._run([self._bin("sshd"), "-t"], strict_stderr=True)
        effective = self._effective_ssh(state.get("ssh_context") or {})
        self._validate_ufw_after_apply()
        return effective

    def _expected_records(self, manifest, state):
        expected = {item["path"]: item for item in manifest["files"]}
        for change in state.get("changes", []):
            expected[change["path"]] = change.get("after")
        if state.get("phase") in ("applying", "applied", "committed", "rolling_back", "rollback_incomplete"):
            expected[SSH_SNIPPET] = next((item.get("after") for item in state.get("changes", []) if item.get("path") == SSH_SNIPPET), None)
        return expected

    def status(self):
        self._guard()
        self._validate_workdir()
        self._check_existing_workdir()
        with self._locked():
            manifest, state = self._load_transaction()
            files = []
            for logical, expected in sorted(self._expected_records(manifest, state).items()):
                try:
                    current = self._current_record(logical)
                    error = None
                except ControllerError as exc:
                    current, error = None, str(exc)
                files.append({
                    "path": logical,
                    "expected_sha256": expected.get("sha256") if expected else None,
                    "expected_mode": expected.get("mode") if expected else None,
                    "current_sha256": current.get("sha256") if current else None,
                    "current_mode": current.get("mode") if current else None,
                    "matches": self._matches(current, expected),
                    "error": error,
                })
            timer = self._timer_info(state)
            effective = None
            if state.get("ssh_context") and state.get("phase") in ("applied", "committed", "rolling_back", "rollback_incomplete"):
                try:
                    effective = self._effective_ssh(state["ssh_context"])
                except ControllerError:
                    effective = {"validation": "failed"}
            return {
                "ok": True,
                "action": "status",
                "phase": state.get("phase"),
                "workdir": self.workdir_logical,
                "files": files,
                "rollback_timer": timer,
                "effective_ssh": effective,
                "original_ufw_active": state.get("original_ufw_active"),
                "account": state.get("user"),
                "user_login_attestation": state.get("user_login_attestation"),
            }


def _stable_file_record(value):
    if value is None:
        return None
    return tuple(value.get(name) for name in ("path", "sha256", "mode", "uid", "gid", "size"))


def _effective_uid():
    getter = getattr(os, "geteuid", None)
    return getter() if getter else -1


def _system_hostname():
    import socket
    return socket.gethostname()


def _parser():
    parser = argparse.ArgumentParser(description="Bounded vm2565 SSH/UFW access controller")
    parser.add_argument("--workdir", required=True, help="/root/aurelia-access-<UTCstamp>")
    sub = parser.add_subparsers(dest="action", required=True)
    sub.add_parser("prepare")
    create = sub.add_parser("create-user")
    key = create.add_mutually_exclusive_group(required=True)
    key.add_argument("--public-key")
    key.add_argument("--public-key-file")
    login = sub.add_parser("record-user-login")
    login.add_argument("--parent-verified-uid", required=True, type=int)
    sub.add_parser("apply")
    commit = sub.add_parser("commit")
    commit.add_argument("--parent-verified", action="store_true", required=True)
    sub.add_parser("rollback")
    sub.add_parser("status")
    return parser


def main(argv=None):
    args = _parser().parse_args(argv)
    controller = AccessController(args.workdir)
    try:
        if args.action == "prepare":
            result = controller.prepare()
        elif args.action == "create-user":
            if args.public_key_file:
                path = Path(args.public_key_file)
                if path.is_symlink() or not path.is_file():
                    raise ControllerError("public-key file must be a regular file")
                key_data = path.read_text(encoding="utf-8")
            else:
                key_data = args.public_key
            result = controller.create_user(key_data)
        elif args.action == "record-user-login":
            result = controller.record_user_login(args.parent_verified_uid)
        elif args.action == "apply":
            result = controller.apply()
        elif args.action == "commit":
            result = controller.commit(parent_verified=args.parent_verified)
        elif args.action == "rollback":
            result = controller.rollback()
        else:
            result = controller.status()
        print(json.dumps(result, sort_keys=True, separators=(",", ":")))
        return 0
    except ControllerError as exc:
        print(json.dumps({"ok": False, "action": args.action, "error": str(exc)}, sort_keys=True, separators=(",", ":")))
        return 2
    except Exception as exc:
        print(json.dumps({"ok": False, "action": args.action, "error": "unexpected failure", "type": type(exc).__name__}, sort_keys=True, separators=(",", ":")))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
