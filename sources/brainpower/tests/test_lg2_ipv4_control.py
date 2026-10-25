"""Linux-only mock regressions for the bounded LG2 IPv4 transaction."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import fcntl
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch

if not sys.platform.startswith("linux"):
    raise unittest.SkipTest("requires Linux filesystem and flock semantics")

from tools.server import lg2_ipv4_control as control


STAMP = "20261016T070215Z"
WORKDIR = f"/root/aurelia-ipv4-{STAMP}"
TIMER = f"aurelia-ipv4-rollback-{STAMP}.timer"
NETPLAN = "/etc/netplan/50-cloud-init.yaml"
CHRONY = "/etc/default/chrony"
NEW_PATHS = {
    "/etc/cloud/cloud.cfg.d/99-disable-network-config.cfg",
    "/etc/sysctl.d/99-aurelia-ipv4.conf",
    "/etc/ssh/sshd_config.d/01-aurelia-ipv4.conf",
    "/etc/systemd/system/ssh.socket.d/99-aurelia-ipv4.conf",
}
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
DESIRED_TAIL = {
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


class SimulatedPowerLoss(SystemExit):
    pass


class MockLinuxRunner:
    """Predictable subprocess double for identity, timer, probes and service actions."""

    def __init__(self):
        self.commands: list[tuple[str, ...]] = []
        self.timer_active = True
        self.netplan_generate_ok = True
        self.network_ipv4 = False
        self.netplan_apply_count = 0
        self.services = {"ssh.service", "ssh.socket", "chrony.service", "fail2ban.service", "ufw.service"}
        self.sysctls = {
            "net.ipv6.conf.all.disable_ipv6": "0",
            "net.ipv6.conf.default.disable_ipv6": "0",
            "net.ipv6.conf.lo.disable_ipv6": "0",
            "net.ipv6.conf.eth0.disable_ipv6": "0",
        }
        self.unhealthy: set[str] = set()
        self.fail_once_fragments: list[str] = []
        self.block_fragment: str | None = None
        self.block_entered = threading.Event()
        self.block_release = threading.Event()

    def __call__(self, argv, *, input=None, cwd=None, timeout=None, **kwargs):
        args = tuple(str(x) for x in argv)
        self.commands.append(args)
        joined = " ".join(args)
        if self.block_fragment and self.block_fragment in joined:
            self.block_entered.set()
            self.block_release.wait(3)
        for fragment in tuple(self.fail_once_fragments):
            if fragment in joined:
                self.fail_once_fragments.remove(fragment)
                return subprocess.CompletedProcess(args, 1, "", "injected command failure")
        if "netplan" in args and "generate" in args:
            rc = 0 if self.netplan_generate_ok else 1
            return subprocess.CompletedProcess(args, rc, "", "invalid candidate" if rc else "")
        if "netplan" in args and "apply" in args:
            try:
                netplan = self.root / "etc/netplan/50-cloud-init.yaml"
                desired = "dhcp6: false" in netplan.read_text(encoding="utf-8")
            except (AttributeError, OSError):
                desired = False
            self.network_ipv4 = desired
            return subprocess.CompletedProcess(args, 0, "", "")
        if args[-1:] == ("vm2565",) and "hostname" in args[0]:
            return subprocess.CompletedProcess(args, 0, "vm2565\n", "")
        if "lsb_release" in args:
            return subprocess.CompletedProcess(args, 0, "24.04\n", "")
        if "is-active" in args:
            unit = args[-1]
            active = self.timer_active if unit.endswith(".timer") else unit in self.services
            return subprocess.CompletedProcess(args, 0 if active else 3, "active\n" if active else "inactive\n", "")
        if "is-enabled" in args:
            return subprocess.CompletedProcess(args, 0, "enabled\n", "")
        if "stop" in args and args[-1].endswith(".timer"):
            self.timer_active = False
        if "sysctl" in args and "-w" in args:
            for arg in args:
                if "=1" in arg and arg.split("=", 1)[0] in self.sysctls:
                    self.sysctls[arg.split("=", 1)[0]] = "1"
                if "=0" in arg and arg.split("=", 1)[0] in self.sysctls:
                    self.sysctls[arg.split("=", 1)[0]] = "0"
        if "sysctl" in args and "-p" in args:
            for key in self.sysctls:
                self.sysctls[key] = "1"
        if "sysctl" in args and "-n" in args:
            key = args[-1]
            value = self.sysctls.get(key, "1")
            if "sysctl:" in self.unhealthy or "sysctl:" + key in self.unhealthy:
                value = "0"
            return subprocess.CompletedProcess(args, 0, value + "\n", "")
        if "hostname" in args[0]:
            return subprocess.CompletedProcess(args, 0, "vm2565\n", "")
        if "ip" in args and "-j" in args and "address" in args:
            if "address" in self.unhealthy:
                out = "[]"
            elif self.network_ipv4 or "-4" in args:
                out = '[{"ifname":"eth0","addr_info":[{"family":"inet","local":"193.142.40.36","prefixlen":24}]}]'
            else:
                out = ('[{"ifname":"eth0","addr_info":[{"family":"inet","local":"193.142.40.36","prefixlen":24},'
                       '{"family":"inet6","local":"2001:db8::36","prefixlen":64}]}]')
            return subprocess.CompletedProcess(args, 0, out, "")
        if "ip" in args and "-j" in args and "route" in args:
            if "-6" in args:
                routes = [] if self.network_ipv4 and "ipv6" not in self.unhealthy else [
                    {"dst": "default", "gateway": "fe80::1", "dev": "eth0", "table": 254}
                ]
            else:
                routes = [{"dst": "default", "gateway": "193.142.40.1", "dev": "eth0", "table": 254}]
            out = json.dumps(routes)
            return subprocess.CompletedProcess(args, 0, out, "")
        if "ip" in args and "-4" in args and "route" in args:
            out = "" if "route" in self.unhealthy else "default via 193.142.40.1 dev eth0\n"
            return subprocess.CompletedProcess(args, 0, out, "")
        if "ip" in args and "-6" in args:
            out = "::1 dev lo\n" if "ipv6" in self.unhealthy else ""
            return subprocess.CompletedProcess(args, 0, out, "")
        if "ss" in args and "-6" in args:
            out = "udp UNCONN 0 0 [::]:53 [::]:*\n" if "listener" in self.unhealthy else ""
            return subprocess.CompletedProcess(args, 0, out, "")
        if "sshd" in args and "-T" in args:
            out = "addressfamily any\nlistenaddress [::]:22\n" if "sshd" in self.unhealthy else (
                "addressfamily inet\nlistenaddress 0.0.0.0:22\n"
            )
            return subprocess.CompletedProcess(args, 0, out, "")
        if "Listen" in joined and "systemctl" in args:
            return subprocess.CompletedProcess(args, 0, "0.0.0.0:22 (Stream)\n", "")
        if "ss" in args:
            out = "LISTEN 0 4096 0.0.0.0:22 0.0.0.0:* users:((\"systemd\",pid=1,fd=42))\n"
            if "socket" in self.unhealthy:
                out += "LISTEN 0 4096 [::]:22 [::]:* users:((\"systemd\",pid=1,fd=43))\n"
            return subprocess.CompletedProcess(args, 0, out, "")
        if "show" in args and "KillMode" in joined:
            mode = "control-group" if "killmode" in self.unhealthy else "process"
            out = mode + "\n" if "--value" in args else "KillMode=" + mode + "\n"
            return subprocess.CompletedProcess(args, 0, out, "")
        if "ufw" in args:
            return subprocess.CompletedProcess(args, 0, "Status: active\n", "")
        if "getent" in args:
            out = "" if "dns" in self.unhealthy else "194.45.196.14 STREAM archive.ubuntu.com\n"
            return subprocess.CompletedProcess(args, 0 if out else 2, out, "")
        if "pgrep" in args and "chronyd" in args:
            out = "" if "chrony" in self.unhealthy else "123 /usr/sbin/chronyd -F 1 -4\n"
            return subprocess.CompletedProcess(args, 0 if out else 1, out, "")
        return subprocess.CompletedProcess(args, 0, "", "")


class IPv4ControllerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.runner = MockLinuxRunner()
        self.runner.root = self.root
        self._write(NETPLAN, b"network:\n  version: 2\n  ethernets:\n    eth0:\n      dhcp4: true\n      dhcp6: true\n")
        self._write(CHRONY, b'DAEMON_OPTS="-F 1"\n')
        for path in PROTECTED_PATHS:
            self._write(path, b"ssh-ed25519 MOCK_PUBLIC_KEY\n" if path.endswith("authorized_keys") else b"FIXTURE\n")
        self._write("/etc/ufw/ufw.conf", b"IPV6=yes\nENABLED=yes\n")
        self.workdir_path = self.root / WORKDIR.lstrip("/")
        self.controller = control.IPv4Controller(WORKDIR, self.runner, root=self.root)

    def tearDown(self):
        self.temp.cleanup()

    def _path(self, target):
        return self.root / target.lstrip("/")

    def _write(self, target, data, mode=0o644):
        path = self._path(target)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        path.chmod(mode)
        if hasattr(os, "chown") and os.geteuid() == 0:
            os.chown(path, 0, 0)
            os.chown(path.parent, 0, 0)
        return path

    def _fingerprint(self, target):
        path = self._path(target)
        if not path.exists():
            return {"exists": False, "sha256": None, "mode": None, "uid": None, "gid": None, "size": None}
        st = path.stat()
        raw = path.read_bytes()
        return {"exists": True, "sha256": hashlib.sha256(raw).hexdigest(), "mode": st.st_mode & 0o777,
                "uid": st.st_uid, "gid": st.st_gid, "size": len(raw)}

    def _payload(self):
        before = {path: self._fingerprint(path) for path in control.TARGET_PATHS}
        chrony = self._path(CHRONY).read_text(encoding="utf-8")
        self.assertEqual(chrony.count('DAEMON_OPTS="-F 1"'), 1)
        desired = {NETPLAN: NETPLAN_DESIRED, **DESIRED_TAIL,
                   CHRONY: chrony.replace('DAEMON_OPTS="-F 1"', 'DAEMON_OPTS="-F 1 -4"')}
        self.assertEqual(set(before), set(desired))
        return {"schema_version": 1, "hostname": "vm2565", "os_release": "24.04",
                "expected_before": before, "desired": desired, "rollback_timer": TIMER}

    def _prepare(self):
        return self.controller.prepare(self._payload())

    def _report_unknown_for_inactive_timer(self):
        runner = self.runner

        def run(argv, **kwargs):
            result = runner(argv, **kwargs)
            args = tuple(str(x) for x in argv)
            if (args[:3] == ("systemctl", "is-active", "--quiet")
                    and args[-1:] == (TIMER,) and not runner.timer_active):
                return subprocess.CompletedProcess(args, 4, "", "Unit not found")
            return result

        self.controller.runner = run

    def _proof(self, **overrides):
        status = self.controller.status()
        proof = {"schema_version": 1, "workdir": WORKDIR,
                 "desired_manifest_sha256": status["desired_manifest_sha256"],
                 "issued_at": datetime.now(timezone.utc).isoformat(),
                 "roles": {"admin": True, "ops": True, "website": True}}
        proof.update(overrides)
        return proof

    def _assert_original_targets(self, originals):
        for target, (exists, raw, mode) in originals.items():
            path = self._path(target)
            self.assertEqual(path.exists(), exists, target)
            if exists:
                self.assertEqual(path.read_bytes(), raw, target)
                self.assertEqual(path.stat().st_mode & 0o777, mode, target)

    def _originals(self):
        return {target: (self._path(target).exists(), self._path(target).read_bytes() if self._path(target).exists() else None,
                         self._path(target).stat().st_mode & 0o777 if self._path(target).exists() else None)
                for target in control.TARGET_PATHS}

    def test_payload_must_match_the_six_fixed_targets_and_host_identity(self):
        payload = self._payload()
        payload["desired"]["/etc/ssh/sshd_config"] = "PermitRootLogin yes\n"
        with self.assertRaises(control.IPv4ControlError):
            self.controller.prepare(payload)
        self.assertFalse(self.workdir_path.exists())
        payload = self._payload()
        payload["hostname"] = "other-host"
        with self.assertRaises(control.IPv4ControlError):
            self.controller.prepare(payload)
        self.assertFalse(self.workdir_path.exists())

    def test_candidate_netplan_failure_leaves_all_etc_targets_untouched(self):
        originals = self._originals()
        self.runner.netplan_generate_ok = False
        with self.assertRaises(control.IPv4ControlError):
            self.controller.prepare(self._payload())
        self._assert_original_targets(originals)
        self.assertTrue(any("netplan" in cmd and "generate" in cmd for cmd in self.runner.commands))

    def test_symlink_target_is_rejected_without_following_it(self):
        outside = self._write("/outside", b"keep me")
        link = self._path(next(iter(NEW_PATHS)))
        link.parent.mkdir(parents=True, exist_ok=True)
        link.symlink_to(outside)
        with self.assertRaises(control.IPv4ControlError):
            self.controller.prepare(self._payload())
        self.assertEqual(outside.read_bytes(), b"keep me")

    def test_prepare_captures_originals_and_apply_requires_active_rollback_timer(self):
        originals = self._originals()
        self._prepare()
        self.runner.timer_active = False
        with self.assertRaises(control.IPv4ControlError):
            self.controller.apply()
        self._assert_original_targets(originals)
        self.assertEqual(self.controller.status()["phase"], "prepared")
        journal = json.loads((self.workdir_path / "journal.json").read_text())
        self.assertEqual(set(journal["network_before"]["routes"]), {"ipv4", "ipv6"})
        self.assertTrue(any("-4" in command and "table" in command and "all" in command for command in self.runner.commands))
        self.assertTrue(any("-6" in command and "table" in command and "all" in command for command in self.runner.commands))

    def test_apply_writes_only_six_files_preserves_metadata_and_checks_services(self):
        self._prepare()
        self.controller.apply()
        self.assertEqual(set(control.TARGET_PATHS), set(self.controller.status()["target_paths"]))
        self.assertEqual(self._path(NETPLAN).read_text(), NETPLAN_DESIRED)
        self.assertEqual(self._path(CHRONY).read_text(), 'DAEMON_OPTS="-F 1 -4"\n')
        for target in NEW_PATHS:
            expected = 0o644 if target.endswith("ssh.socket.d/99-aurelia-ipv4.conf") else 0o600
            self.assertEqual(self._path(target).stat().st_mode & 0o777, expected, target)
        self.assertEqual(self._path(NETPLAN).stat().st_mode & 0o777, 0o644)
        self.assertEqual(self._path(CHRONY).stat().st_mode & 0o777, 0o644)
        self.assertEqual(self._path("/etc/ufw/ufw.conf").read_bytes(), b"IPV6=yes\nENABLED=yes\n")
        status = self.controller.status()
        self.assertEqual(status["phase"], "applied")
        self.assertTrue(status["checks"]["runtime"]["healthy"])

    def test_apply_refuses_foreign_before_state_drift(self):
        self._prepare()
        netplan = self._path(NETPLAN)
        netplan.write_text("foreign edit\n")
        with self.assertRaises(control.IPv4ControlError):
            self.controller.apply()
        self.assertEqual(netplan.read_text(), "foreign edit\n")

    def test_hard_crash_after_target_replace_can_be_checked_and_rolled_back(self):
        originals = self._originals()
        self._prepare()
        target = self._path(NETPLAN)
        replace = os.replace

        def crash_after_first_target(source, destination):
            replace(source, destination)
            if Path(destination) == target:
                raise SimulatedPowerLoss()

        with patch.object(control.os, "replace", side_effect=crash_after_first_target):
            with self.assertRaises(SimulatedPowerLoss):
                self.controller.apply()
        recovered = control.IPv4Controller(WORKDIR, self.runner, root=self.root)
        check = recovered.rollback_check()
        self.assertTrue(check["ok"])
        recovered.rollback()
        self._assert_original_targets(originals)
        self.assertEqual(recovered.status()["phase"], "rolled_back")

    def test_rollback_conflict_and_corrupt_backup_never_clobber_foreign_bytes(self):
        self._prepare()
        self.controller.apply()
        foreign = self._path(next(iter(NEW_PATHS)))
        foreign.write_text("operator edit after apply\n")
        for attempt in range(2):
            with self.subTest(attempt=attempt):
                with self.assertRaises(control.IPv4ControlError):
                    self.controller.rollback()
                self.assertEqual(foreign.read_text(), "operator edit after apply\n")
        self.assertEqual(self.controller.status()["phase"], "rollback_conflict")

    def test_rollback_retry_finishes_after_hard_crash_mid_restore(self):
        originals = self._originals()
        self._prepare()
        self.controller.apply()
        first_restored = []
        restore_target = self.controller._restore_target

        def crash_after_first_restore(journal, target):
            restore_target(journal, target)
            first_restored.append(target)
            if len(first_restored) == 1:
                raise SimulatedPowerLoss()

        with patch.object(self.controller, "_restore_target", side_effect=crash_after_first_restore):
            with self.assertRaises(SimulatedPowerLoss):
                self.controller.rollback()

        self.assertEqual(first_restored, [control.TARGET_PATHS[-1]])
        self.assertEqual(self.controller.status()["phase"], "rolling_back")
        self.assertEqual(self._path(control.TARGET_PATHS[-1]).read_bytes(), originals[control.TARGET_PATHS[-1]][1])

        recovered = control.IPv4Controller(WORKDIR, self.runner, root=self.root)
        check = recovered.rollback_check()
        self.assertTrue(check["ok"], check["reasons"])
        recovered.rollback()
        self._assert_original_targets(originals)
        self.assertEqual(recovered.status()["phase"], "rolled_back")

    def test_corrupt_backup_blocks_rollback_check(self):
        self._prepare()
        backup = next((self.workdir_path / "backups").glob("*.bin"))
        backup.write_bytes(b"corrupt")
        check = self.controller.rollback_check()
        self.assertFalse(check["ok"])
        self.assertIn("backup", " ".join(check["reasons"]))

    def test_runtime_failure_blocks_commit_and_missing_or_stale_role_proof(self):
        self._prepare()
        self.controller.apply()
        proof = self._proof()
        preapply = {**proof, "issued_at": (datetime.now(timezone.utc) - timedelta(seconds=2)).isoformat()}
        with self.assertRaises(control.IPv4ControlError):
            self.controller.commit(preapply)
        for bad in (
            {**proof, "roles": {"admin": True, "ops": True}},
            {**proof, "roles": {"admin": True, "ops": True, "website": False}},
            {**proof, "issued_at": (datetime.now(timezone.utc) - timedelta(seconds=121)).isoformat()},
            {**proof, "workdir": "/root/aurelia-ipv4-20261016T070216Z"},
            {**proof, "desired_manifest_sha256": "0" * 64},
        ):
            with self.subTest(proof=bad), self.assertRaises(control.IPv4ControlError):
                self.controller.commit(bad)
        self.runner.unhealthy.add("sysctl:")
        with self.assertRaises(control.IPv4ControlError):
            self.controller.commit(proof)
        self.assertEqual(self.controller.status()["phase"], "applied")

    def test_individual_sysctl_probe_failures_cannot_be_overwritten_by_eth0_success(self):
        self._prepare()
        self.controller.apply()
        self.runner.unhealthy.add("sysctl:net.ipv6.conf.lo.disable_ipv6")
        runtime = self.controller.status()["checks"]["runtime"]
        self.assertFalse(runtime["checks"]["sysctl_net_ipv6_conf_lo_disable_ipv6"])
        self.assertTrue(runtime["checks"]["sysctl_net_ipv6_conf_eth0_disable_ipv6"])
        self.assertFalse(runtime["healthy"])
        with self.assertRaises(control.IPv4ControlError):
            self.controller.commit(self._proof())

    def test_rollback_requires_the_saved_original_runtime_state(self):
        self._prepare()
        self.controller.apply()
        self.runner.unhealthy.add("address")
        with self.assertRaises(control.IPv4ControlError):
            self.controller.rollback()
        self.assertEqual(self.controller.status()["phase"], "rollback_incomplete")

    def test_commit_is_durable_before_timer_stop_and_retry_finishes_timer_stop(self):
        self._prepare()
        self.controller.apply()
        self.runner.fail_once_fragments.append("stop " + TIMER)
        with self.assertRaises(control.IPv4ControlError):
            self.controller.commit(self._proof())
        self.assertEqual(self.controller.status()["phase"], "committed")
        self.assertTrue(self.runner.timer_active)
        result = self.controller.commit(self._proof())
        self.assertEqual(result["phase"], "committed")
        self.assertFalse(self.runner.timer_active)

    def test_commit_stays_committed_when_stopped_transient_timer_becomes_unknown(self):
        self._prepare()
        self.controller.apply()
        self._report_unknown_for_inactive_timer()

        result = self.controller.commit(self._proof())
        self.assertEqual(result["phase"], "committed")
        self.assertFalse(result["checks"]["timer_active"])
        self.assertFalse(self.runner.timer_active)

        retried = self.controller.commit(self._proof())
        self.assertEqual(retried["phase"], "committed")
        self.assertFalse(retried["checks"]["timer_active"])
        self.assertFalse(self.runner.timer_active)

    def test_apply_refuses_a_missing_timer_reported_as_unknown(self):
        originals = self._originals()
        self._prepare()
        self._report_unknown_for_inactive_timer()
        self.runner.timer_active = False

        with self.assertRaises(control.IPv4ControlError) as raised:
            self.controller.apply()

        self.assertEqual(raised.exception.code, "rollback_timer_inactive")
        self._assert_original_targets(originals)
        self.assertEqual(self.controller.status()["phase"], "prepared")

    def test_rollback_attempts_later_restore_steps_and_records_incomplete(self):
        self._prepare()
        self.controller.apply()
        self.runner.fail_once_fragments.append("netplan apply")
        with self.assertRaises(control.IPv4ControlError):
            self.controller.rollback()
        self.assertEqual(self.controller.status()["phase"], "rollback_incomplete")
        joined = [" ".join(cmd) for cmd in self.runner.commands]
        failed_at = max(i for i, command in enumerate(joined) if "netplan apply" in command)
        self.assertTrue(any("daemon-reload" in command for command in joined[failed_at + 1:]))
        self.assertTrue(any("chrony" in command for command in joined[failed_at + 1:]))

    def test_timer_rollback_waits_for_an_active_controller_lock(self):
        self._prepare()
        self.controller.apply()
        other = control.IPv4Controller(WORKDIR, self.runner, root=self.root)
        started = threading.Event()
        lock_waiting = threading.Event()
        finished = threading.Event()
        outcome = []
        real_sleep = control.time.sleep

        def note_lock_wait(seconds):
            lock_waiting.set()
            real_sleep(seconds)

        def rollback_in_thread():
            started.set()
            try:
                outcome.append(other.rollback())
            except BaseException as exc:
                outcome.append(exc)
            finally:
                finished.set()

        with patch.object(control.time, "sleep", side_effect=note_lock_wait):
            with self.controller._lock(fcntl.LOCK_EX):
                thread = threading.Thread(target=rollback_in_thread)
                thread.start()
                self.assertTrue(started.wait(1))
                self.assertTrue(lock_waiting.wait(1))
                self.assertFalse(finished.is_set())
        thread.join(5)
        self.assertFalse(thread.is_alive())
        self.assertEqual(len(outcome), 1)
        self.assertIsInstance(outcome[0], dict)
        self.assertEqual(outcome[0]["phase"], "rolled_back")

    def test_timer_rollback_retries_after_a_real_short_lock_timeout(self):
        originals = self._originals()
        self._prepare()
        self.controller.apply()
        other = control.IPv4Controller(WORKDIR, self.runner, root=self.root)

        with patch.object(control, "ROLLBACK_LOCK_WAIT_SECONDS", 0.02):
            with self.controller._lock(fcntl.LOCK_EX):
                with self.assertRaises(control.IPv4ControlError) as raised:
                    other.rollback()
                self.assertEqual(raised.exception.code, "transaction_busy")

        self.assertEqual(self.controller.status()["phase"], "applied")
        result = other.rollback()
        self.assertEqual(result["phase"], "rolled_back")
        self._assert_original_targets(originals)

    def test_rollback_does_not_rebind_ssh_when_killmode_is_unsafe(self):
        self._prepare()
        self.controller.apply()
        self.runner.unhealthy.add("killmode")
        before = len(self.runner.commands)
        with self.assertRaises(control.IPv4ControlError):
            self.controller.rollback()
        rollback_commands = self.runner.commands[before:]
        self.assertNotIn(("systemctl", "stop", "ssh.service"), rollback_commands)
        self.assertNotIn(("systemctl", "restart", "ssh.socket"), rollback_commands)
        self.assertNotIn(("systemctl", "start", "ssh.service"), rollback_commands)
        self.assertIn(("systemctl", "restart", "chrony.service"), rollback_commands)
        self.assertEqual(self.controller.status()["phase"], "rollback_incomplete")

    def test_status_does_not_expose_captured_public_key_bytes(self):
        self._prepare()
        serialized = json.dumps(self.controller.status())
        self.assertNotIn("MOCK_PUBLIC_KEY", serialized)


if __name__ == "__main__":
    unittest.main()
