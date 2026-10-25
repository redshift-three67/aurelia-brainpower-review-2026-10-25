"""Bounded, journaled IPv4 configuration controller for the LG2 host.

The CLI has no arbitrary-root option. The constructor's ``root`` argument is
only for isolated Linux unit tests.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
import time
import uuid
from typing import Any, Callable


TARGET_PATHS = (
    "/etc/netplan/50-cloud-init.yaml",
    "/etc/cloud/cloud.cfg.d/99-disable-network-config.cfg",
    "/etc/sysctl.d/99-aurelia-ipv4.conf",
    "/etc/ssh/sshd_config.d/01-aurelia-ipv4.conf",
    "/etc/systemd/system/ssh.socket.d/99-aurelia-ipv4.conf",
    "/etc/default/chrony",
)
PROTECTED_PATHS = (
    "/etc/default/ufw",
    "/etc/ssh/sshd_config",
    "/etc/ssh/sshd_config.d/00-aurelia-access.conf",
    "/etc/ssh/sshd_config.d/50-cloud-init.conf",
    "/etc/ssh/sshd_config.d/permit_root.conf",
    "/etc/ufw/after.init",
    "/etc/ufw/after.rules",
    "/etc/ufw/after6.rules",
    "/etc/ufw/applications.d/openssh-server",
    "/etc/ufw/before.init",
    "/etc/ufw/before.rules",
    "/etc/ufw/before6.rules",
    "/etc/ufw/sysctl.conf",
    "/etc/ufw/ufw.conf",
    "/etc/ufw/user.rules",
    "/etc/ufw/user6.rules",
    "/root/.ssh/authorized_keys",
    "/home/aurelia-ops/.ssh/authorized_keys",
    "/home/rauch-web-test/.ssh/authorized_keys",
)
SYSCTL_KEYS = (
    "net.ipv6.conf.all.disable_ipv6",
    "net.ipv6.conf.default.disable_ipv6",
    "net.ipv6.conf.lo.disable_ipv6",
    "net.ipv6.conf.eth0.disable_ipv6",
)
SERVICE_UNITS = ("ssh.service", "ssh.socket", "chrony.service", "fail2ban.service")
NETPLAN_DESIRED = '''network:
  version: 2
  ethernets:
    eth0:
      match:
        macaddress: "bc:24:11:07:5e:1f"
      set-name: "eth0"
      dhcp4: false
      dhcp6: false
      accept-ra: false
      link-local: []
      addresses:
      - "193.142.40.36/24"
      nameservers:
        addresses:
        - 194.45.196.14
        - 185.194.237.210
        search:
        - ipp-vps.net
      routes:
      - to: "default"
        via: "193.142.40.1"
'''
FIXED_DESIRED = {
    "/etc/cloud/cloud.cfg.d/99-disable-network-config.cfg": "network: {config: disabled}\n",
    "/etc/sysctl.d/99-aurelia-ipv4.conf": (
        "net.ipv6.conf.all.disable_ipv6 = 1\n"
        "net.ipv6.conf.default.disable_ipv6 = 1\n"
        "net.ipv6.conf.lo.disable_ipv6 = 1\n"
    ),
    "/etc/ssh/sshd_config.d/01-aurelia-ipv4.conf": "AddressFamily inet\nListenAddress 0.0.0.0\n",
    "/etc/systemd/system/ssh.socket.d/99-aurelia-ipv4.conf": (
        "[Socket]\nListenStream=\nListenStream=0.0.0.0:22\n"
    ),
}
WORKDIR_RE = re.compile(r"^/root/aurelia-ipv4-(\d{8}T\d{6}Z)$")
COMMAND_TIMEOUT = 30
NETPLAN_TIMEOUT = 60
APPLY_RUNTIME_MAX_SECONDS = 300  # Parent's systemd service must use this bound.
ROLLBACK_LOCK_WAIT_SECONDS = 180


class IPv4ControlError(RuntimeError):
    """A bounded, expected controller refusal or operation failure."""

    def __init__(self, code: str, message: str | None = None):
        self.code = code
        super().__init__(message or code)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


def _parse_utc(value: str) -> datetime:
    if not isinstance(value, str):
        raise ValueError("timestamp")
    parsed = datetime.fromisoformat(value[:-1] + "+00:00" if value.endswith("Z") else value)
    if parsed.tzinfo is None:
        raise ValueError("timezone")
    return parsed.astimezone(timezone.utc)


def _canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _no_duplicate_pairs(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise ValueError("duplicate JSON key")
        obj[key] = value
    return obj


def _strict_json(raw: bytes) -> Any:
    return json.loads(raw.decode("utf-8"), object_pairs_hook=_no_duplicate_pairs)


class IPv4Controller:
    """A single-run, compare-and-swap IPv4 configuration transaction."""

    def __init__(
        self,
        workdir: str | Path,
        runner: Callable[..., subprocess.CompletedProcess[str]] | None = None,
        *,
        root: str | Path = "/",
    ) -> None:
        self.workdir = str(workdir)
        self.root = Path(root)
        self.runner = runner or subprocess.run
        match = WORKDIR_RE.fullmatch(self.workdir)
        if not match:
            raise IPv4ControlError("workdir_invalid")
        self.stamp = match.group(1)
        try:
            datetime.strptime(self.stamp, "%Y%m%dT%H%M%SZ")
        except ValueError:
            raise IPv4ControlError("workdir_invalid") from None
        self.timer_unit = f"aurelia-ipv4-rollback-{self.stamp}.timer"
        self._work = self._physical(self.workdir)

    def prepare(self, payload: dict[str, Any]) -> dict[str, Any]:
        self._require_root()
        self._validate_payload(payload)
        self._check_identity()
        self._ensure_workdir()
        with self._locked():
            if self._journal_path().exists():
                journal = self._load_journal()
                if journal.get("phase") == "prepared" and journal.get("desired_manifest_sha256") == self._manifest_hash(payload["desired"]):
                    return self._status_from_journal(journal)
                raise IPv4ControlError("transaction_exists")
            leftovers = [p for p in self._work.iterdir() if p.name != ".lock"]
            if leftovers:
                raise IPv4ControlError("untracked_workdir_content")

            before = {target: self._fingerprint(target, managed=True) for target in TARGET_PATHS}
            if before != payload["expected_before"]:
                raise IPv4ControlError("before_state_mismatch")
            self._validate_desired(payload["desired"], before)
            protected = self._capture_protected()
            sysctls = self._capture_sysctls()
            services = self._capture_services()
            if not all(services[unit]["active"] == "active" for unit in SERVICE_UNITS):
                raise IPv4ControlError("service_precondition")
            ufw = self._command(["ufw", "status"])
            if not re.search(r"(?im)^Status:\s*active\s*$", ufw):
                raise IPv4ControlError("ufw_precondition")
            network = self._capture_network()

            backup_dir = self._work / "backups"
            self._make_dir(backup_dir, 0o700)
            originals = {}
            backups = {}
            for target, fingerprint in before.items():
                raw = self._read_target(target) if fingerprint["exists"] else None
                backup_name = hashlib.sha256(target.encode("utf-8")).hexdigest() + ".bin"
                if raw is not None:
                    self._atomic_path(backup_dir / backup_name, raw, 0o600, 0, 0, managed=False)
                originals[target] = fingerprint
                backups[target] = backup_name if raw is not None else None

            desired_bytes = {p: payload["desired"][p].encode("utf-8") for p in TARGET_PATHS}
            expected_after = {}
            for target, raw in desired_bytes.items():
                old = before[target]
                mode = old["mode"] if old["exists"] else (0o644 if target.endswith("ssh.socket.d/99-aurelia-ipv4.conf") else 0o600)
                uid, gid = (old["uid"], old["gid"]) if old["exists"] else (0, 0)
                expected_after[target] = {"exists": True, "sha256": _sha(raw), "mode": mode,
                                          "uid": uid, "gid": gid, "size": len(raw)}

            self._validate_candidate(payload["desired"][TARGET_PATHS[0]])
            own_bytes = Path(__file__).read_bytes()
            own_hash = _sha(own_bytes)
            self_path = f"{self.workdir}/controller.py"
            self._atomic_path(self._physical(self_path), own_bytes, 0o600, 0, 0, managed=False)
            created_dirs = self._new_target_parent_dirs()
            manifest_hash = self._manifest_hash(payload["desired"])
            journal = {
                "schema_version": 1,
                "workdir": self.workdir,
                "phase": "prepared",
                "prepared_at": _utc_now(),
                "timer_unit": self.timer_unit,
                "desired_manifest_sha256": manifest_hash,
                "desired": payload["desired"],
                "originals": originals,
                "backups": backups,
                "expected_after": expected_after,
                "protected_files": protected,
                "sysctls_before": sysctls,
                "services_before": services,
                "network_before": network,
                "new_target_parent_dirs": created_dirs,
                "self_path": self_path,
                "self_sha256": own_hash,
                "last_error": None,
            }
            self._save_journal(journal)
            return self._status_from_journal(journal)

    def apply(self) -> dict[str, Any]:
        self._require_root()
        with self._locked():
            journal = self._load_journal()
            if journal["phase"] == "applied":
                return self._status_from_journal(journal)
            if journal["phase"] != "prepared":
                raise IPv4ControlError("phase_invalid")
            self._verify_self(journal)
            if not self._timer_active(journal):
                raise IPv4ControlError("rollback_timer_inactive")
            self._require_protected_unchanged(journal)
            self._require_files_match(journal, "before")
            journal["expected_after"] = self._expected_after_from_journal(journal)
            journal["phase"] = "applying"
            journal["apply_started_at"] = _utc_now()
            journal["last_error"] = None
            self._save_journal(journal)
            try:
                for target in TARGET_PATHS:
                    self._install_target(journal, target)
                    journal["last_written_path"] = target
                    self._save_journal(journal)
                self._command(["sshd", "-t"])
                self._command(["netplan", "apply"], timeout=NETPLAN_TIMEOUT)
                self._command(["sysctl", "-p", "/etc/sysctl.d/99-aurelia-ipv4.conf"])
                self._command(["sysctl", "-w", "net.ipv6.conf.eth0.disable_ipv6=1"])
                self._command(["systemctl", "daemon-reload"])
                self._require_killmode_process()
                self._command(["systemctl", "stop", "ssh.service"])
                self._command(["systemctl", "restart", "ssh.socket"])
                self._command(["systemctl", "start", "ssh.service"])
                self._command(["systemctl", "restart", "chrony.service"])
                runtime = self._runtime_checks(journal)
                if not runtime["healthy"]:
                    raise IPv4ControlError("runtime_validation_failed")
                self._require_protected_unchanged(journal)
                journal["phase"] = "applied"
                journal["applied_at"] = _utc_now()
                journal["runtime_checks_at_apply"] = runtime["checks"]
                self._save_journal(journal)
                return self._status_from_journal(journal)
            except BaseException as exc:
                if isinstance(exc, (KeyboardInterrupt, SystemExit)):
                    raise
                journal["phase"] = "apply_failed"
                journal["last_error"] = self._error_code(exc)
                self._save_journal(journal)
                if isinstance(exc, IPv4ControlError):
                    raise
                raise IPv4ControlError("apply_failed") from None

    def status(self) -> dict[str, Any]:
        with self._shared_locked():
            journal = self._load_journal()
            return self._status_from_journal(journal)

    def rollback_check(self) -> dict[str, Any]:
        with self._shared_locked():
            journal = self._load_journal()
            return self._rollback_check(journal)

    def rollback(self) -> dict[str, Any]:
        self._require_root()
        with self._locked(wait_seconds=ROLLBACK_LOCK_WAIT_SECONDS):
            journal = self._load_journal()
            if journal["phase"] in ("committed", "rolled_back"):
                return self._status_from_journal(journal)
            check = self._rollback_check(journal)
            if not check["ok"]:
                journal["phase"] = "rollback_conflict"
                journal["last_error"] = ",".join(check["reasons"])
                self._save_journal(journal)
                raise IPv4ControlError("rollback_precondition_failed")
            if journal["phase"] == "prepared":
                journal["phase"] = "rolling_back"
                journal["rollback_started_at"] = _utc_now()
                self._save_journal(journal)
                if not self._runtime_equals_before(journal):
                    journal["phase"] = "rollback_incomplete"
                    journal["last_error"] = "runtime_before_drift"
                    self._save_journal(journal)
                    raise IPv4ControlError("rollback_incomplete")
                self._finish_rollback(journal)
                return self._status_from_journal(journal)

            journal["phase"] = "rolling_back"
            journal["rollback_started_at"] = _utc_now()
            journal["last_error"] = None
            self._save_journal(journal)
            errors: list[str] = []

            for target in reversed(TARGET_PATHS):
                try:
                    self._restore_target(journal, target)
                except BaseException as exc:
                    if isinstance(exc, (KeyboardInterrupt, SystemExit)):
                        raise
                    errors.append(f"file:{target}")

            # Restore saved IPv6 sysctls before applying the original netplan.
            for key, value in journal["sysctls_before"].items():
                try:
                    self._command(["sysctl", "-w", f"{key}={value}"])
                except IPv4ControlError:
                    errors.append(f"sysctl:{key}")
            try:
                self._command(["netplan", "apply"], timeout=NETPLAN_TIMEOUT)
            except IPv4ControlError:
                errors.append("netplan_apply")
            try:
                self._command(["systemctl", "daemon-reload"])
            except IPv4ControlError:
                errors.append("systemd_reload")

            ssh_rebind_safe = True
            try:
                self._require_killmode_process()
            except IPv4ControlError:
                errors.append("ssh_killmode")
                ssh_rebind_safe = False
            service_actions = []
            if ssh_rebind_safe:
                service_actions.extend((
                    (["systemctl", "stop", "ssh.service"], "ssh_stop"),
                    (["systemctl", "restart", "ssh.socket"], "ssh_socket_restart"),
                    (["systemctl", "start", "ssh.service"], "ssh_start"),
                ))
            service_actions.append((["systemctl", "restart", "chrony.service"], "chrony_restart"))
            for argv, code in service_actions:
                try:
                    self._command(argv)
                except IPv4ControlError:
                    errors.append(code)

            errors.extend(self._verify_rollback_state(journal))
            if errors:
                journal["phase"] = "rollback_incomplete"
                journal["last_error"] = ",".join(sorted(set(errors)))
                self._save_journal(journal)
                raise IPv4ControlError("rollback_incomplete")
            self._finish_rollback(journal)
            return self._status_from_journal(journal)

    def commit(self, proof: dict[str, Any]) -> dict[str, Any]:
        self._require_root()
        with self._locked():
            journal = self._load_journal()
            if journal["phase"] == "committed":
                self._stop_timer(journal)
                return self._status_from_journal(journal)
            if journal["phase"] != "applied":
                raise IPv4ControlError("phase_invalid")
            self._validate_proof(proof, journal)
            self._verify_self(journal)
            if not self._timer_active(journal):
                raise IPv4ControlError("rollback_timer_inactive")
            self._require_files_match(journal, "after")
            self._require_protected_unchanged(journal)
            runtime = self._runtime_checks(journal)
            if not runtime["healthy"]:
                raise IPv4ControlError("runtime_validation_failed")
            journal["phase"] = "committed"
            journal["committed_at"] = _utc_now()
            journal["commit_proof_sha256"] = _sha(_canonical_bytes(proof))
            self._save_journal(journal)
            self._stop_timer(journal)
            return self._status_from_journal(journal)

    def _validate_proof(self, proof: dict[str, Any], journal: dict[str, Any]) -> None:
        if not isinstance(proof, dict) or set(proof) != {
            "schema_version", "workdir", "desired_manifest_sha256", "issued_at", "roles"
        }:
            raise IPv4ControlError("proof_schema")
        if proof["schema_version"] != 1 or proof["workdir"] != self.workdir:
            raise IPv4ControlError("proof_binding")
        if proof["desired_manifest_sha256"] != journal["desired_manifest_sha256"]:
            raise IPv4ControlError("proof_binding")
        if not isinstance(proof["roles"], dict) or set(proof["roles"]) != {"admin", "ops", "website"}:
            raise IPv4ControlError("proof_roles")
        if any(type(proof["roles"][role]) is not bool or proof["roles"][role] is not True for role in ("admin", "ops", "website")):
            raise IPv4ControlError("proof_roles")
        try:
            issued = _parse_utc(proof["issued_at"])
            applied = _parse_utc(journal["applied_at"])
        except (TypeError, ValueError):
            raise IPv4ControlError("proof_timestamp") from None
        now = datetime.now(timezone.utc)
        age = (now - issued).total_seconds()
        if age < 0 or age > 120 or issued < applied:
            raise IPv4ControlError("proof_stale")

    def _validate_payload(self, payload: dict[str, Any]) -> None:
        if not isinstance(payload, dict) or set(payload) != {
            "schema_version", "hostname", "os_release", "expected_before", "desired", "rollback_timer"
        }:
            raise IPv4ControlError("payload_schema")
        if payload["schema_version"] != 1 or payload["hostname"] != "vm2565" or payload["os_release"] != "24.04":
            raise IPv4ControlError("payload_identity")
        if payload["rollback_timer"] != self.timer_unit:
            raise IPv4ControlError("payload_timer")
        if not isinstance(payload["expected_before"], dict) or set(payload["expected_before"]) != set(TARGET_PATHS):
            raise IPv4ControlError("payload_scope")
        if not isinstance(payload["desired"], dict) or set(payload["desired"]) != set(TARGET_PATHS):
            raise IPv4ControlError("payload_scope")
        fields = {"exists", "sha256", "mode", "uid", "gid", "size"}
        for target, item in payload["expected_before"].items():
            if not isinstance(item, dict) or set(item) != fields or type(item["exists"]) is not bool:
                raise IPv4ControlError("fingerprint_schema")
            if item["exists"]:
                if not isinstance(item["sha256"], str) or not re.fullmatch(r"[0-9a-f]{64}", item["sha256"]):
                    raise IPv4ControlError("fingerprint_schema")
                for key in ("mode", "uid", "gid", "size"):
                    if type(item[key]) is not int or item[key] < 0:
                        raise IPv4ControlError("fingerprint_schema")
            elif any(item[key] is not None for key in ("sha256", "mode", "uid", "gid", "size")):
                raise IPv4ControlError("fingerprint_schema")
        for target, content in payload["desired"].items():
            if not isinstance(content, str) or "\x00" in content or len(content.encode("utf-8")) > 32768:
                raise IPv4ControlError("desired_content")

    def _validate_desired(self, desired: dict[str, str], before: dict[str, dict[str, Any]]) -> None:
        if desired[TARGET_PATHS[0]] != NETPLAN_DESIRED:
            raise IPv4ControlError("netplan_semantics")
        for path, expected in FIXED_DESIRED.items():
            if desired[path] != expected:
                raise IPv4ControlError("desired_semantics")
        chrony_path = "/etc/default/chrony"
        original = self._read_target(chrony_path).decode("utf-8", "strict")
        match = re.search(r'(?m)^DAEMON_OPTS="-F 1"$', original)
        if not match or len(re.findall(r'(?m)^DAEMON_OPTS=', original)) != 1:
            raise IPv4ControlError("chrony_before_semantics")
        expected = original[:match.start()] + 'DAEMON_OPTS="-F 1 -4"' + original[match.end():]
        if desired[chrony_path] != expected:
            raise IPv4ControlError("chrony_desired_semantics")
        if before[chrony_path]["exists"] is not True:
            raise IPv4ControlError("chrony_missing")

    def _check_identity(self) -> None:
        host = self._command(["hostname"]).strip()
        release = self._command(["lsb_release", "-rs"]).strip()
        if host != "vm2565" or release != "24.04":
            raise IPv4ControlError("host_identity_mismatch")

    def _require_root(self) -> None:
        if not hasattr(os, "geteuid") or os.geteuid() != 0:
            raise IPv4ControlError("root_required")

    def _manifest_hash(self, desired: dict[str, str]) -> str:
        return _sha(_canonical_bytes({path: desired[path] for path in sorted(TARGET_PATHS)}))

    def _physical(self, absolute: str) -> Path:
        if not isinstance(absolute, str) or not absolute.startswith("/") or ".." in Path(absolute).parts:
            raise IPv4ControlError("path_invalid")
        return self.root / absolute.lstrip("/")

    def _ensure_workdir(self) -> None:
        if self.root.is_symlink() or not self.root.is_dir():
            raise IPv4ControlError("root_path_invalid")
        if self.root.stat().st_uid != 0:
            raise IPv4ControlError("root_owner_invalid")
        path = self._work
        rel = path.relative_to(self.root)
        cursor = self.root
        for part in rel.parts:
            cursor = cursor / part
            try:
                st = cursor.lstat()
            except FileNotFoundError:
                cursor.mkdir(mode=0o700)
                os.chown(cursor, 0, 0)
                cursor.chmod(0o700)
                st = cursor.lstat()
            if stat.S_ISLNK(st.st_mode) or not stat.S_ISDIR(st.st_mode) or st.st_uid != 0 or (st.st_mode & 0o022):
                raise IPv4ControlError("workdir_path_unsafe")
        if self._work.stat().st_mode & 0o777 != 0o700:
            self._work.chmod(0o700)
            os.chown(self._work, 0, 0)

    @contextmanager
    def _locked(self, wait_seconds: float = 0):
        with self._lock(fcntl.LOCK_EX, wait_seconds=wait_seconds):
            yield

    @contextmanager
    def _shared_locked(self):
        with self._lock(fcntl.LOCK_SH):
            yield

    @contextmanager
    def _lock(self, operation, *, wait_seconds: float = 0):
        self._ensure_workdir()
        lock_path = self._work / ".lock"
        flags = os.O_CREAT | os.O_RDWR | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
        try:
            fd = os.open(lock_path, flags, 0o600)
            st = os.fstat(fd)
            if not stat.S_ISREG(st.st_mode) or st.st_uid != 0 or st.st_nlink != 1 or st.st_mode & 0o077:
                os.close(fd)
                raise IPv4ControlError("lock_unsafe")
            os.fchown(fd, 0, 0)
            os.fchmod(fd, 0o600)
            deadline = time.monotonic() + max(0, wait_seconds)
            while True:
                try:
                    fcntl.flock(fd, operation | fcntl.LOCK_NB)
                    break
                except BlockingIOError:
                    remaining = deadline - time.monotonic()
                    if remaining <= 0:
                        os.close(fd)
                        raise IPv4ControlError("transaction_busy") from None
                    time.sleep(min(0.1, remaining))
        except OSError:
            raise IPv4ControlError("lock_unavailable") from None
        try:
            yield
        finally:
            fcntl.flock(fd, fcntl.LOCK_UN)
            os.close(fd)

    def _journal_path(self) -> Path:
        return self._work / "journal.json"

    def _load_journal(self) -> dict[str, Any]:
        path = self._journal_path()
        try:
            st = path.lstat()
        except FileNotFoundError:
            raise IPv4ControlError("journal_missing") from None
        if stat.S_ISLNK(st.st_mode) or not stat.S_ISREG(st.st_mode) or st.st_uid != 0 or st.st_mode & 0o077 or st.st_size > 2 * 1024 * 1024:
            raise IPv4ControlError("journal_unsafe")
        try:
            data = _strict_json(path.read_bytes())
        except (OSError, UnicodeError, ValueError, json.JSONDecodeError):
            raise IPv4ControlError("journal_invalid") from None
        if not isinstance(data, dict) or data.get("schema_version") != 1 or data.get("workdir") != self.workdir:
            raise IPv4ControlError("journal_binding")
        if data.get("timer_unit") != self.timer_unit or data.get("desired_manifest_sha256") is None:
            raise IPv4ControlError("journal_binding")
        return data

    def _save_journal(self, journal: dict[str, Any]) -> None:
        self._atomic_path(self._journal_path(), _canonical_bytes(journal), 0o600, 0, 0, managed=False)

    def _atomic_path(self, path: Path, raw: bytes, mode: int, uid: int, gid: int, *, managed: bool) -> None:
        self._make_parent_dirs(path.parent, managed=managed)
        try:
            old = path.lstat()
        except FileNotFoundError:
            old = None
        if old is not None and (stat.S_ISLNK(old.st_mode) or not stat.S_ISREG(old.st_mode) or old.st_nlink != 1):
            raise IPv4ControlError("target_path_unsafe")
        temp = path.parent / ("." + path.name + ".tmp-" + uuid.uuid4().hex)
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
        fd = os.open(temp, flags, mode)
        try:
            os.fchown(fd, uid, gid)
            os.fchmod(fd, mode)
            with os.fdopen(fd, "wb", closefd=False) as handle:
                handle.write(raw)
                handle.flush()
                os.fsync(fd)
        finally:
            os.close(fd)
        current = None
        try:
            current = path.lstat()
        except FileNotFoundError:
            pass
        if current is not None and (stat.S_ISLNK(current.st_mode) or not stat.S_ISREG(current.st_mode) or current.st_nlink != 1):
            temp.unlink(missing_ok=True)
            raise IPv4ControlError("target_path_unsafe")
        os.replace(temp, path)
        self._fsync_dir(path.parent)

    def _make_dir(self, path: Path, mode: int) -> None:
        self._make_parent_dirs(path.parent, managed=False)
        try:
            path.mkdir(mode=mode)
        except FileExistsError:
            pass
        st = path.lstat()
        if stat.S_ISLNK(st.st_mode) or not stat.S_ISDIR(st.st_mode) or st.st_uid != 0 or st.st_mode & 0o022:
            raise IPv4ControlError("directory_unsafe")
        os.chown(path, 0, 0)
        os.chmod(path, mode)
        self._fsync_dir(path.parent)

    def _make_parent_dirs(self, path: Path, *, managed: bool) -> None:
        try:
            rel = path.relative_to(self.root)
        except ValueError:
            raise IPv4ControlError("path_outside_root") from None
        cursor = self.root
        for part in rel.parts:
            cursor = cursor / part
            try:
                st = cursor.lstat()
            except FileNotFoundError:
                cursor.mkdir(mode=0o755)
                os.chown(cursor, 0, 0)
                os.chmod(cursor, 0o755)
                st = cursor.lstat()
            if stat.S_ISLNK(st.st_mode) or not stat.S_ISDIR(st.st_mode):
                raise IPv4ControlError("parent_path_unsafe")
            if managed and (st.st_uid != 0 or st.st_mode & 0o022):
                raise IPv4ControlError("parent_path_unsafe")

    def _fsync_dir(self, path: Path) -> None:
        fd = os.open(path, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_CLOEXEC", 0))
        try:
            os.fsync(fd)
        finally:
            os.close(fd)

    def _fingerprint(self, absolute: str, *, managed: bool, missing_ok: bool = True) -> dict[str, Any]:
        path = self._physical(absolute)
        self._check_parent_chain(path.parent, managed=managed)
        try:
            st = path.lstat()
        except FileNotFoundError:
            if missing_ok:
                return {"exists": False, "sha256": None, "mode": None, "uid": None, "gid": None, "size": None}
            raise IPv4ControlError("required_file_missing") from None
        if stat.S_ISLNK(st.st_mode) or not stat.S_ISREG(st.st_mode) or st.st_nlink != 1:
            raise IPv4ControlError("file_path_unsafe")
        if managed and (st.st_uid != 0 or st.st_mode & 0o022):
            raise IPv4ControlError("file_owner_or_mode_unsafe")
        raw = path.read_bytes()
        if len(raw) > 1024 * 1024:
            raise IPv4ControlError("file_too_large")
        return {"exists": True, "sha256": _sha(raw), "mode": stat.S_IMODE(st.st_mode),
                "uid": st.st_uid, "gid": st.st_gid, "size": len(raw)}

    def _check_parent_chain(self, path: Path, *, managed: bool) -> None:
        try:
            rel = path.relative_to(self.root)
        except ValueError:
            raise IPv4ControlError("path_outside_root") from None
        cursor = self.root
        for part in rel.parts:
            cursor = cursor / part
            try:
                st = cursor.lstat()
            except FileNotFoundError:
                return
            if stat.S_ISLNK(st.st_mode) or not stat.S_ISDIR(st.st_mode):
                raise IPv4ControlError("parent_path_unsafe")
            if managed and (st.st_uid != 0 or st.st_mode & 0o022):
                raise IPv4ControlError("parent_path_unsafe")

    def _read_target(self, absolute: str) -> bytes:
        fp = self._fingerprint(absolute, managed=True, missing_ok=False)
        if not fp["exists"]:
            raise IPv4ControlError("required_file_missing")
        return self._physical(absolute).read_bytes()

    def _capture_protected(self) -> dict[str, dict[str, Any]]:
        protected = {}
        for path in PROTECTED_PATHS:
            protected[path] = self._fingerprint(path, managed=False, missing_ok=False)
        return protected

    def _protected_changed(self, journal: dict[str, Any]) -> list[str]:
        changed = []
        for path, expected in journal["protected_files"].items():
            try:
                actual = self._fingerprint(path, managed=False, missing_ok=False)
            except IPv4ControlError:
                changed.append(path)
                continue
            if actual != expected:
                changed.append(path)
        return changed

    def _require_protected_unchanged(self, journal: dict[str, Any]) -> None:
        if self._protected_changed(journal):
            raise IPv4ControlError("protected_file_drift")

    def _capture_sysctls(self) -> dict[str, str]:
        values = {}
        for key in SYSCTL_KEYS:
            value = self._command(["sysctl", "-n", key]).strip()
            if value not in ("0", "1", "2"):
                raise IPv4ControlError("sysctl_invalid")
            values[key] = value
        return values

    def _capture_services(self) -> dict[str, dict[str, str]]:
        states = {}
        for unit in SERVICE_UNITS:
            states[unit] = {
                "active": self._service_active(unit),
                "enabled": self._service_enabled(unit),
            }
        return states

    def _service_active(self, unit: str) -> str:
        cp = self._run(["systemctl", "is-active", "--quiet", unit], allowed=(0, 3))
        return "active" if cp.returncode == 0 else "inactive"

    def _service_enabled(self, unit: str) -> str:
        cp = self._run(["systemctl", "is-enabled", unit], allowed=(0, 1, 3))
        return cp.stdout.strip() or ("enabled" if cp.returncode == 0 else "disabled")

    def _capture_network(self) -> dict[str, Any]:
        addr_raw = self._command(["ip", "-j", "address", "show"])
        route_raw_by_family = {
            family: self._command(["ip", f"-{family}", "-j", "route", "show", "table", "all"])
            for family in ("4", "6")
        }
        try:
            addr = json.loads(addr_raw)
            routes_by_family = {family: json.loads(raw) for family, raw in route_raw_by_family.items()}
        except (TypeError, ValueError):
            raise IPv4ControlError("network_snapshot_invalid") from None
        if not isinstance(addr, list) or any(not isinstance(routes, list) for routes in routes_by_family.values()):
            raise IPv4ControlError("network_snapshot_invalid")
        interfaces = []
        for item in addr:
            if not isinstance(item, dict) or not isinstance(item.get("ifname"), str):
                raise IPv4ControlError("network_snapshot_invalid")
            addresses = []
            for info in item.get("addr_info", []):
                if not isinstance(info, dict):
                    raise IPv4ControlError("network_snapshot_invalid")
                addresses.append({key: info[key] for key in ("family", "local", "prefixlen", "scope", "label") if key in info})
            addresses.sort(key=lambda x: (str(x.get("family")), str(x.get("local")), int(x.get("prefixlen", 0))))
            interfaces.append({"ifname": item["ifname"], "addresses": addresses})
        interfaces.sort(key=lambda x: x["ifname"])
        route_keys = ("dst", "dev", "gateway", "metric", "table", "protocol", "scope", "prefsrc", "src", "type", "onlink", "via")
        compact_by_family = {}
        for family, routes in routes_by_family.items():
            compact_routes = []
            for route in routes:
                if not isinstance(route, dict):
                    raise IPv4ControlError("network_snapshot_invalid")
                compact_routes.append({key: route[key] for key in route_keys if key in route})
            compact_routes.sort(key=lambda x: _canonical_bytes(x))
            compact_by_family["ipv" + family] = compact_routes
        return {"interfaces": interfaces, "routes": compact_by_family}

    def _validate_candidate(self, netplan_text: str) -> None:
        target = self._work / "candidate-root/etc/netplan/50-cloud-init.yaml"
        self._atomic_path(target, netplan_text.encode("utf-8"), 0o600, 0, 0, managed=False)
        self._command(["netplan", "generate", "--root-dir", str(target.parents[2])], timeout=NETPLAN_TIMEOUT)

    def _run(self, argv: list[str], *, timeout: int = COMMAND_TIMEOUT, allowed: tuple[int, ...] = (0,)):
        try:
            result = self.runner(argv, capture_output=True, text=True, timeout=timeout, check=False)
        except subprocess.TimeoutExpired:
            raise IPv4ControlError("command_timeout") from None
        except OSError:
            raise IPv4ControlError("command_unavailable") from None
        if not hasattr(result, "returncode") or result.returncode not in allowed:
            raise IPv4ControlError("command_failed")
        if isinstance(result.stdout, bytes):
            result.stdout = result.stdout.decode("utf-8", "replace")
        if isinstance(result.stderr, bytes):
            result.stderr = result.stderr.decode("utf-8", "replace")
        return result

    def _command(self, argv: list[str], *, timeout: int = COMMAND_TIMEOUT) -> str:
        return self._run(argv, timeout=timeout).stdout

    def _timer_active(self, journal: dict[str, Any]) -> bool:
        # A stopped transient timer may be garbage-collected before this probe.
        cp = self._run(["systemctl", "is-active", "--quiet", journal["timer_unit"]], allowed=(0, 3, 4))
        return cp.returncode == 0

    def _stop_timer(self, journal: dict[str, Any]) -> None:
        try:
            self._command(["systemctl", "stop", journal["timer_unit"]])
        except IPv4ControlError:
            # The state check decides whether a failed stop is material.
            pass
        if self._timer_active(journal):
            raise IPv4ControlError("rollback_timer_stop_failed")
        journal["timer_stopped_at"] = _utc_now()
        journal["timer_stop_error"] = None
        self._save_journal(journal)

    def _expected_after_from_journal(self, journal: dict[str, Any]) -> dict[str, dict[str, Any]]:
        return journal["expected_after"]

    def _install_target(self, journal: dict[str, Any], target: str) -> None:
        desired = journal["desired"][target].encode("utf-8")
        before = journal["originals"][target]
        if self._fingerprint(target, managed=True) != before:
            raise IPv4ControlError("target_drift")
        mode = before["mode"] if before["exists"] else (0o644 if target.endswith("ssh.socket.d/99-aurelia-ipv4.conf") else 0o600)
        uid = before["uid"] if before["exists"] else 0
        gid = before["gid"] if before["exists"] else 0
        self._atomic_path(self._physical(target), desired, mode, uid, gid, managed=True)

    def _restore_target(self, journal: dict[str, Any], target: str) -> None:
        original = journal["originals"][target]
        path = self._physical(target)
        current = self._fingerprint(target, managed=True)
        if current not in (original, journal["expected_after"][target]):
            raise IPv4ControlError("target_conflict")
        if original["exists"]:
            backup_name = journal["backups"].get(target)
            if not backup_name:
                raise IPv4ControlError("backup_missing")
            backup = self._work / "backups" / backup_name
            raw = backup.read_bytes()
            if _sha(raw) != original["sha256"]:
                raise IPv4ControlError("backup_corrupt")
            self._atomic_path(path, raw, original["mode"], original["uid"], original["gid"], managed=True)
        elif current["exists"]:
            st = path.lstat()
            if stat.S_ISLNK(st.st_mode) or not stat.S_ISREG(st.st_mode) or st.st_uid != 0:
                raise IPv4ControlError("target_path_unsafe")
            path.unlink()
            self._fsync_dir(path.parent)

    def _require_files_match(self, journal: dict[str, Any], state: str) -> None:
        expected = journal["originals"] if state == "before" else journal["expected_after"]
        for target, fingerprint in expected.items():
            if self._fingerprint(target, managed=True) != fingerprint:
                raise IPv4ControlError("target_drift")

    def _verify_self(self, journal: dict[str, Any]) -> None:
        path = journal.get("self_path")
        if path != f"{self.workdir}/controller.py":
            raise IPv4ControlError("self_path_invalid")
        physical = self._physical(path)
        try:
            st = physical.lstat()
            if stat.S_ISLNK(st.st_mode) or not stat.S_ISREG(st.st_mode) or st.st_uid != 0 or st.st_mode & 0o077:
                raise IPv4ControlError("self_copy_unsafe")
            raw = physical.read_bytes()
        except OSError:
            raise IPv4ControlError("self_copy_missing") from None
        if _sha(raw) != journal.get("self_sha256"):
            raise IPv4ControlError("self_copy_changed")

    def _new_target_parent_dirs(self) -> list[str]:
        missing = set()
        for target in TARGET_PATHS:
            parent = self._physical(target).parent
            while parent != self.root and not parent.exists():
                missing.add("/" + str(parent.relative_to(self.root)).replace(os.sep, "/"))
                parent = parent.parent
        return sorted(missing, key=lambda p: p.count("/"), reverse=True)

    def _runtime_checks(self, journal: dict[str, Any]) -> dict[str, Any]:
        checks: dict[str, bool] = {}

        def probe(name, argv, predicate):
            try:
                out = self._command(argv)
                checks[name] = bool(predicate(out))
            except (IPv4ControlError, ValueError, TypeError):
                checks[name] = False

        probe("ipv4_address", ["ip", "-j", "-4", "address", "show"], self._has_expected_ipv4)
        probe("ipv4_default_route", ["ip", "-4", "route", "show", "default"],
              lambda out: bool(re.search(r"(?m)^default via 193\.142\.40\.1 dev eth0(?:\s|$)", out)))
        probe("ipv6_addresses_absent", ["ip", "-6", "address", "show"], lambda out: not out.strip())
        probe("ipv6_routes_absent", ["ip", "-6", "-j", "route", "show", "table", "all"],
              lambda out: json.loads(out) == [])
        probe("ipv6_listeners_absent", ["ss", "-6", "-H", "-lntup"], lambda out: not out.strip())
        for key in SYSCTL_KEYS:
            probe("sysctl_" + key.replace(".", "_"), ["sysctl", "-n", key], lambda out: out.strip() == "1")
        probe("sshd_ipv4", ["sshd", "-T"], self._sshd_ipv4)
        probe("chrony_process_ipv4", ["pgrep", "-a", "chronyd"],
              lambda out: bool(re.search(r"(?:^|\s)-4(?:\s|$)", out, re.MULTILINE)))
        probe("ssh_socket_ipv4_only", ["systemctl", "show", "ssh.socket", "--property=Listen", "--value"], self._socket_ipv4_only)
        probe("ssh_ipv4_listener", ["ss", "-4", "-H", "-lntp"], lambda out: bool(re.search(r"\s0\.0\.0\.0:22\s", out)))
        for unit in SERVICE_UNITS:
            try:
                checks["service_" + unit] = self._service_active(unit) == "active"
            except IPv4ControlError:
                checks["service_" + unit] = False
        probe("ufw_active", ["ufw", "status"], lambda out: bool(re.search(r"(?im)^Status:\s*active\s*$", out)))
        probe("dns_ipv4", ["getent", "ahostsv4", "archive.ubuntu.com"], lambda out: bool(out.strip()))
        try:
            checks["desired_files"] = all(
                self._fingerprint(path, managed=True) == journal["expected_after"][path] for path in TARGET_PATHS
            )
        except IPv4ControlError:
            checks["desired_files"] = False
        checks["protected_files_unchanged"] = not self._protected_changed(journal)
        return {"healthy": all(checks.values()), "checks": checks}

    @staticmethod
    def _has_expected_ipv4(out: str) -> bool:
        try:
            data = json.loads(out)
        except ValueError:
            return False
        return any(item.get("ifname") == "eth0" and any(
            addr.get("family") == "inet" and addr.get("local") == "193.142.40.36" and addr.get("prefixlen") == 24
            for addr in item.get("addr_info", [])
        ) for item in data if isinstance(item, dict))

    @staticmethod
    def _sshd_ipv4(out: str) -> bool:
        lines = [line.strip().lower() for line in out.splitlines() if line.strip()]
        families = [line for line in lines if line.startswith("addressfamily ")]
        listeners = [line for line in lines if line.startswith("listenaddress ")]
        return families == ["addressfamily inet"] and listeners == ["listenaddress 0.0.0.0:22"]

    @staticmethod
    def _socket_ipv4_only(out: str) -> bool:
        listeners = []
        for line in out.splitlines():
            value = line.strip().removeprefix("Listen=")
            if not value:
                continue
            listeners.append(value.replace(" (Stream)", ""))
        return listeners == ["0.0.0.0:22"]

    def _require_killmode_process(self) -> None:
        value = self._command(["systemctl", "show", "ssh.service", "--property=KillMode", "--value"]).strip()
        if value != "process":
            raise IPv4ControlError("ssh_killmode_unsafe")

    def _status_from_journal(self, journal: dict[str, Any]) -> dict[str, Any]:
        phase = journal["phase"]
        try:
            files_after = all(self._fingerprint(path, managed=True) == journal["expected_after"][path] for path in TARGET_PATHS)
        except IPv4ControlError:
            files_after = False
        protected_unchanged = not self._protected_changed(journal)
        try:
            timer_active = self._timer_active(journal)
        except IPv4ControlError:
            timer_active = False
        runtime = {"healthy": False, "checks": {}, "checked": False}
        if phase in ("applied", "committed", "apply_failed", "rollback_incomplete", "rollback_conflict"):
            runtime = {**self._runtime_checks(journal), "checked": True}
        return {
            "ok": True,
            "phase": phase,
            "workdir": self.workdir,
            "self_path": journal["self_path"],
            "self_sha256": journal["self_sha256"],
            "target_paths": list(TARGET_PATHS),
            "rollback_timer": journal["timer_unit"],
            "desired_manifest_sha256": journal["desired_manifest_sha256"],
            "prepared_at": journal["prepared_at"],
            "applied_at": journal.get("applied_at"),
            "committed_at": journal.get("committed_at"),
            "last_error": journal.get("last_error"),
            "protected_files": {path: item["sha256"] for path, item in journal["protected_files"].items()},
            "checks": {
                "files_match_desired": files_after,
                "protected_files_unchanged": protected_unchanged,
                "timer_active": timer_active,
                "runtime": runtime,
            },
        }

    def _rollback_check(self, journal: dict[str, Any]) -> dict[str, Any]:
        if journal["phase"] == "committed":
            return {"ok": True, "phase": "committed", "noop": True, "reasons": []}
        reasons = []
        try:
            self._verify_self(journal)
        except IPv4ControlError:
            reasons.append("self_copy")
        for target, original in journal["originals"].items():
            if original["exists"]:
                backup_name = journal.get("backups", {}).get(target)
                if not backup_name:
                    reasons.append("backup_missing:" + target)
                    continue
                backup = self._work / "backups" / backup_name
                try:
                    st = backup.lstat()
                    raw = backup.read_bytes()
                    if stat.S_ISLNK(st.st_mode) or not stat.S_ISREG(st.st_mode) or st.st_uid != 0 or st.st_mode & 0o077 or _sha(raw) != original["sha256"]:
                        reasons.append("backup_corrupt:" + target)
                except OSError:
                    reasons.append("backup_missing:" + target)
            try:
                current = self._fingerprint(target, managed=True)
            except IPv4ControlError:
                reasons.append("target_unsafe:" + target)
                continue
            if current not in (original, journal["expected_after"][target]):
                reasons.append("target_conflict:" + target)
        if self._protected_changed(journal):
            reasons.append("protected_files_changed")
        if journal["phase"] == "prepared" and not self._runtime_equals_before(journal):
            reasons.append("runtime_before_changed")
        return {"ok": not reasons, "phase": journal["phase"], "noop": False, "reasons": reasons}

    def _runtime_equals_before(self, journal: dict[str, Any]) -> bool:
        try:
            return (self._capture_sysctls() == journal["sysctls_before"]
                    and self._capture_network() == journal["network_before"]
                    and self._capture_services() == journal["services_before"])
        except IPv4ControlError:
            return False

    def _verify_rollback_state(self, journal: dict[str, Any]) -> list[str]:
        errors = []
        try:
            for target, original in journal["originals"].items():
                if self._fingerprint(target, managed=True) != original:
                    errors.append("files_after_restore")
                    break
        except IPv4ControlError:
            errors.append("files_after_restore")
        try:
            if self._capture_sysctls() != journal["sysctls_before"]:
                errors.append("sysctls_after_restore")
        except IPv4ControlError:
            errors.append("sysctls_after_restore")
        try:
            if self._capture_network() != journal["network_before"]:
                errors.append("network_after_restore")
        except IPv4ControlError:
            errors.append("network_after_restore")
        try:
            if self._capture_services() != journal["services_before"]:
                errors.append("services_after_restore")
        except IPv4ControlError:
            errors.append("services_after_restore")
        if self._protected_changed(journal):
            errors.append("protected_files_after_restore")
        try:
            v4 = self._command(["ss", "-4", "-H", "-lntp"])
            if not re.search(r"\s0\.0\.0\.0:22\s", v4):
                errors.append("ssh_ipv4_not_listening")
        except IPv4ControlError:
            errors.append("ssh_ipv4_probe")
        for unit in ("ssh.service", "ssh.socket", "chrony.service"):
            try:
                if self._service_active(unit) != "active":
                    errors.append("service_inactive:" + unit)
            except IPv4ControlError:
                errors.append("service_probe:" + unit)
        return errors

    def _finish_rollback(self, journal: dict[str, Any]) -> None:
        for text in journal.get("new_target_parent_dirs", []):
            try:
                path = self._physical(text)
                if path.exists() and not any(path.iterdir()):
                    path.rmdir()
                    self._fsync_dir(path.parent)
            except OSError:
                pass
        try:
            self._stop_timer(journal)
        except IPv4ControlError:
            journal["phase"] = "rollback_incomplete"
            journal["last_error"] = "rollback_timer_stop_failed"
            self._save_journal(journal)
            raise
        journal["phase"] = "rolled_back"
        journal["rolled_back_at"] = _utc_now()
        journal["last_error"] = None
        self._save_journal(journal)

    def _error_code(self, exc: BaseException) -> str:
        if isinstance(exc, IPv4ControlError):
            return exc.code
        if isinstance(exc, subprocess.TimeoutExpired):
            return "command_timeout"
        if isinstance(exc, OSError):
            return "filesystem_error"
        return "operation_error"


def _read_cli_json(path: str) -> dict[str, Any]:
    source = Path(path)
    try:
        st = source.lstat()
        if stat.S_ISLNK(st.st_mode) or not stat.S_ISREG(st.st_mode) or st.st_size > 256 * 1024:
            raise IPv4ControlError("input_file_invalid")
        value = _strict_json(source.read_bytes())
    except IPv4ControlError:
        raise
    except (OSError, ValueError, UnicodeError):
        raise IPv4ControlError("input_file_invalid") from None
    if not isinstance(value, dict):
        raise IPv4ControlError("input_schema_invalid")
    return value


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workdir", required=True)
    commands = parser.add_subparsers(dest="action", required=True)
    prepare = commands.add_parser("prepare")
    prepare.add_argument("--payload-file", required=True)
    commands.add_parser("apply")
    commands.add_parser("status")
    commands.add_parser("rollback-check")
    commands.add_parser("rollback")
    commit = commands.add_parser("commit")
    commit.add_argument("--proof-file", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        controller = IPv4Controller(args.workdir)
        if args.action == "prepare":
            result = controller.prepare(_read_cli_json(args.payload_file))
        elif args.action == "apply":
            result = controller.apply()
        elif args.action == "status":
            result = controller.status()
        elif args.action == "rollback-check":
            result = controller.rollback_check()
        elif args.action == "rollback":
            result = controller.rollback()
        else:
            result = controller.commit(_read_cli_json(args.proof_file))
        print(json.dumps(result, sort_keys=True))
        return 0
    except (IPv4ControlError, OSError, ValueError) as exc:
        code = exc.code if isinstance(exc, IPv4ControlError) else "operation_failed"
        print(json.dumps({"ok": False, "error": code}, sort_keys=True), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
