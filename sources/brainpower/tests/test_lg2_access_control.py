import hashlib
import importlib.util
import contextlib
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import time
import unittest
from unittest import mock


if os.name != "posix":
    raise unittest.SkipTest("LG2 access controller requires Linux; run these mocks on the isolated Linux test host")

MODULE_PATH = Path(__file__).resolve().parents[1] / "tools" / "server" / "lg2_access_control.py"
SPEC = importlib.util.spec_from_file_location("lg2_access_control", MODULE_PATH)
lg2 = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = lg2
SPEC.loader.exec_module(lg2)


class FakeRunner:
    def __init__(self):
        self.calls = []
        self.timer_active = False
        self.timer_created = False
        self.timer_deadline = 0
        self.on_call = None
        self.after_call = None
        self.fs = None
        self.user_exists = False
        self.group_collision = False
        self.ufw_active = False
        self.v6_rule = False

    def __call__(self, argv, **kwargs):
        argv = [str(part) for part in argv]
        argv[0] = argv[0].rsplit("/", 1)[-1]
        self.calls.append(argv)
        if self.on_call:
            self.on_call(argv)
        result = self._execute(argv)
        if self.after_call:
            self.after_call(argv)
        return result

    def _execute(self, argv):
        good = lg2.CommandResult(0, "", "")
        if argv[0] == "sshd":
            if "-T" in argv:
                values = dict(lg2.SSH_SETTINGS)
                values["permitrootlogin"] = "without-password"
                return lg2.CommandResult(0, "".join(k + " " + v + "\n" for k, v in values.items()), "")
            return good
        if argv[0] == "systemd-run":
            self.timer_active = self.timer_created = True
            self.timer_deadline = time.monotonic() + 900
            unit = next(v.split("=", 1)[1] for v in argv if v.startswith("--unit="))
            stderr = "" if "--quiet" in argv else f"Running timer as unit: {unit}.timer\nWill run service as unit: {unit}.service\n"
            return lg2.CommandResult(0, "", stderr)
        if argv[:2] == ["systemctl", "show"]:
            unit = argv[2]
            prop = next((v.split("=", 1)[1] for v in argv if v.startswith("--property=")), "")
            if prop == "LoadState": value = "loaded" if self.timer_created else "not-found"
            elif prop == "ActiveState": value = "active" if unit.endswith(".timer") and self.timer_active else "inactive"
            elif prop == "SubState": value = "waiting" if unit.endswith(".timer") and self.timer_active else "dead"
            elif prop == "LastTriggerUSec": value = ""
            elif prop == "NextElapseUSecMonotonic":
                seconds = self.timer_deadline
                value = f"{int(seconds // 3600)}h {int(seconds % 3600 // 60)}min {seconds % 60:.6f}s"
            else: raise AssertionError("Unmodelled systemctl property: " + repr(argv))
            return lg2.CommandResult(0, value + "\n", "")
        if argv[:2] == ["systemctl", "stop"]:
            self.timer_active = False
            return good
        if argv[:2] == ["systemctl", "is-active"]:
            return lg2.CommandResult(0, "active\n", "")
        if argv[:2] == ["systemctl", "reload"]:
            return good
        if argv[:2] == ["getent", "passwd"]:
            return lg2.CommandResult(0, "aurelia-ops:x:1001:1001::/home/aurelia-ops:/bin/bash\n", "") if self.user_exists else lg2.CommandResult(2, "", "")
        if argv[:2] == ["getent", "group"]:
            return lg2.CommandResult(0, "aurelia-ops:x:1001:\n", "") if self.user_exists or self.group_collision else lg2.CommandResult(2, "", "")
        if argv[0] == "useradd":
            self.user_exists = True
            (self.fs / "home/aurelia-ops").mkdir(parents=True)
            return good
        if argv[0] == "usermod": return good
        if argv[:2] == ["passwd", "-S"]:
            return lg2.CommandResult(0, "aurelia-ops L 10/15/2026 0 99999 7 -1\n", "")
        if argv[0] == "id":
            if "-u" in argv: value = "1001"
            elif "-g" in argv: value = "1001"
            else: value = "aurelia-ops"
            return lg2.CommandResult(0, value + "\n", "")
        if argv[0] == "ufw":
            if "status" in argv:
                if "verbose" in argv:
                    value = "Status: active\nDefault: deny (incoming), allow (outgoing), deny (routed)\n"
                elif "numbered" in argv:
                    value = "Status: active\n[ 1] 22/tcp ALLOW IN Anywhere\n"
                    if self.v6_rule: value += "[ 2] 22/tcp (v6) ALLOW IN Anywhere (v6)\n"
                else: value = "Status: active\n" if self.ufw_active else "Status: inactive\n"
                return lg2.CommandResult(0, value, "")
            if "default" in argv:
                path = self.fs / "etc/default/ufw"
            elif "allow" in argv:
                path = self.fs / "etc/ufw/user.rules"
            elif "enable" in argv or "disable" in argv:
                self.ufw_active = "enable" in argv
                path = self.fs / "etc/ufw/ufw.conf"
                path.write_text("ENABLED=yes\n" if self.ufw_active else "ENABLED=no\n")
                return good
            else: raise AssertionError("Unmodelled ufw command: " + repr(argv))
            with path.open("a") as stream: stream.write("# " + " ".join(argv) + "\n")
            return good
        raise AssertionError("Unmodelled system command: " + repr(argv))


class AccessControlTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.fs = Path(self.temp.name)
        self.runner = FakeRunner()
        self._write("etc/ssh/sshd_config", "Include /etc/ssh/sshd_config.d/*.conf\nPermitRootLogin yes\n", 0o640)
        self._write("etc/ssh/sshd_config.d/50-cloud-init.conf", "PasswordAuthentication yes\n", 0o644)
        self._write("etc/ssh/ssh_host_ed25519_key", "PRIVATE HOST KEY MUST NOT BE COPIED\n", 0o600)
        self._write("etc/shadow", "USER SECRET MUST NOT BE COPIED\n", 0o600)
        self._write("etc/default/ufw", "IPV6=yes\n", 0o644)
        self._write("etc/ufw/ufw.conf", "ENABLED=no\n", 0o640)
        self._write("etc/ufw/user.rules", "*filter\nCOMMIT\n", 0o640)
        self._write("etc/ufw/user6.rules", "*filter\nCOMMIT\n", 0o640)
        self._write("root/.placeholder", "", 0o600)
        self.workdir = "/root/aurelia-access-20261015T010203Z"

    def tearDown(self):
        self.temp.cleanup()

    def _write(self, relative, content, mode):
        path = self.fs / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        path.chmod(mode)
        return path

    def controller(self, *, hostname="vm2565", uid=0, workdir=None):
        self.runner.fs = self.fs
        def owner(path):
            relative = Path(path).relative_to(self.fs).as_posix()
            return 1001 if relative == "home/aurelia-ops" or relative.startswith("home/aurelia-ops/") else 0
        return lg2.AccessController(
            workdir or self.workdir,
            system_root=self.fs,
            hostname=hostname,
            effective_uid=uid,
            runner=self.runner,
            executable_finder=lambda name: f"/usr/sbin/{name}",
            owner_uid=owner,
            chown=lambda *_args: None,
            environ={"SSH_CONNECTION": "82.135.84.93 12345 193.142.40.36 22"},
        )

    KEY = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIJXnrSo7SoAMbCM0KaTZqRSA5AZ9idXwWSB3xIlTyDl1 test-key"

    def ready(self, controller):
        controller.prepare()
        controller.create_user(self.KEY)
        controller.record_user_login(1001)
        return controller

    def state(self):
        return json.loads((self.fs / self.workdir.lstrip("/") / "state.json").read_text())

    def test_valid_ed25519_key_is_preserved(self):
        self.assertEqual(lg2.validate_public_key(self.KEY), self.KEY)

    def test_timer_recovery_uses_exact_same_controller_source(self):
        self.controller().prepare()
        helper = self.fs / self.workdir.lstrip("/") / "rollback.py"
        self.assertEqual(helper.read_bytes(), MODULE_PATH.read_bytes())
        compile(helper.read_bytes(), str(helper), "exec")
        schedule = next(c for c in self.runner.calls if c[0] == "systemd-run")
        self.assertEqual(schedule[-1], "rollback")

    def test_user_creation_and_login_attestation_are_unprivileged(self):
        controller = self.ready(self.controller())
        state = self.state()
        self.assertEqual(state["phase"], "user_created")
        self.assertEqual(state["user"]["uid"], 1001)
        self.assertEqual(state["user"]["privileged_groups"], [])
        auth = self.fs / "home/aurelia-ops/.ssh/authorized_keys"
        self.assertEqual(auth.stat().st_mode & 0o777, 0o600)
        self.assertIn('restrict,expiry-time="20261016210835Z"', auth.read_text())
        self.assertFalse(any("sudo" in c or "docker" in c for c in self.runner.calls))

    def test_group_collision_prevents_useradd(self):
        controller = self.controller()
        controller.prepare()
        self.runner.group_collision = True
        self.runner.calls.clear()
        with self.assertRaises(lg2.ControllerError): controller.create_user(self.KEY)
        self.assertFalse(any(c[0] == "useradd" for c in self.runner.calls))

    def test_missing_timer_blocks_apply_before_mutation(self):
        controller = self.ready(self.controller())
        self.runner.timer_active = False
        self.runner.calls.clear()
        with self.assertRaises(lg2.ControllerError): controller.apply()
        self.assertFalse((self.fs / lg2.SSH_SNIPPET.lstrip("/")).exists())
        self.assertFalse(any(c[0] == "ufw" and "status" not in c for c in self.runner.calls))

    def test_expiring_timer_blocks_apply_before_mutation(self):
        controller = self.ready(self.controller())
        self.runner.timer_deadline = time.monotonic() + 2
        self.runner.calls.clear()
        with self.assertRaises(lg2.ControllerError): controller.apply()
        self.assertFalse((self.fs / lg2.SSH_SNIPPET.lstrip("/")).exists())
        self.assertFalse(any(c[0] == "ufw" and "status" not in c for c in self.runner.calls))

    def test_successful_apply_uses_only_ipv4_ssh_and_commit_precedes_timer_stop(self):
        controller = self.ready(self.controller())
        result = controller.apply()
        self.assertEqual(result["phase"], "applied")
        rules = [c for c in self.runner.calls if c[0] == "ufw" and "allow" in c and "default" not in c]
        self.assertEqual(len(rules), 1)
        self.assertIn("0.0.0.0/0", rules[0])
        self.assertNotIn(["ufw", "allow", "22/tcp"], self.runner.calls)
        def before_stop(argv):
            if argv[:2] == ["systemctl", "stop"]:
                self.assertEqual(self.state()["phase"], "committed")
        self.runner.on_call = before_stop
        self.assertEqual(controller.commit(parent_verified=True)["phase"], "committed")
        self.assertFalse(self.runner.timer_active)
        self.assertTrue(controller.rollback()["noop"])
        self.assertTrue(self.runner.ufw_active)

    def test_ipv6_allow_rule_is_rejected_and_changes_reverted(self):
        controller = self.ready(self.controller())
        self.runner.v6_rule = True
        with self.assertRaises(lg2.ControllerError): controller.apply()
        self.assertFalse(self.runner.ufw_active)
        self.assertFalse((self.fs / lg2.SSH_SNIPPET.lstrip("/")).exists())

    def test_successful_rollback_restores_original_bytes_and_removes_only_own_snippet(self):
        controller = self.ready(self.controller())
        baseline = {n:(self.fs/n).read_bytes() for n in ["etc/default/ufw","etc/ufw/ufw.conf","etc/ufw/user.rules","etc/ssh/sshd_config.d/50-cloud-init.conf"]}
        controller.apply()
        self.assertEqual(controller.rollback()["phase"], "rolled_back")
        for n,b in baseline.items(): self.assertEqual((self.fs/n).read_bytes(), b)
        self.assertFalse(self.runner.ufw_active)
        self.assertFalse((self.fs / lg2.SSH_SNIPPET.lstrip("/")).exists())
        self.assertTrue(self.runner.user_exists)

    def test_rollback_still_restores_ufw_when_ssh_reload_fails(self):
        controller = self.ready(self.controller())
        controller.apply()
        def fail_ssh(argv):
            if argv[:2] == ["systemctl", "reload"]: raise lg2.ControllerError("injected SSH reload failure")
        self.runner.on_call = fail_ssh
        with self.assertRaises(lg2.ControllerError): controller.rollback()
        self.assertFalse(self.runner.ufw_active)
        self.assertEqual(self.state()["phase"], "rollback_incomplete")

    def test_commit_requires_parent_attestation(self):
        controller = self.ready(self.controller())
        controller.apply()
        with self.assertRaises(lg2.ControllerError): controller.commit()
        self.assertTrue(self.runner.timer_active)
        self.assertEqual(self.state()["phase"], "applied")

    def test_process_crash_after_ufw_mutation_can_be_recovered(self):
        class SimulatedKill(BaseException): pass
        controller = self.ready(self.controller())
        baseline = (self.fs / "etc/ufw/user.rules").read_bytes()
        def kill(argv):
            if argv[0] == "ufw" and "allow" in argv and "default" not in argv:
                raise SimulatedKill()
        self.runner.after_call = kill
        with self.assertRaises(SimulatedKill): controller.apply()
        self.runner.after_call = None
        self.assertEqual(controller.rollback()["phase"], "rolled_back")
        self.assertEqual((self.fs / "etc/ufw/user.rules").read_bytes(), baseline)
        self.assertFalse((self.fs / lg2.SSH_SNIPPET.lstrip("/")).exists())

    def test_own_interrupted_atomic_state_tempfile_does_not_block_recovery(self):
        controller = self.ready(self.controller())
        controller.apply()
        leftover = self.fs / self.workdir.lstrip("/") / "state.json.tmp-1234-5678"
        leftover.write_bytes(b"partial uncommitted state")
        leftover.chmod(0o600)
        self.assertEqual(controller.rollback()["phase"], "rolled_back")
        self.assertFalse(self.runner.ufw_active)

    def test_unknown_workdir_file_blocks_operation(self):
        controller = self.controller()
        controller.prepare()
        (self.fs / self.workdir.lstrip("/") / "unexpected.conf").write_bytes(b"foreign")
        with self.assertRaises(lg2.ControllerError): controller.rollback()

    def test_crash_after_ssh_snippet_write_is_recoverable(self):
        class SimulatedKill(BaseException): pass
        controller = self.ready(self.controller())
        original = controller._write_ssh_snippet
        def crash():
            original()
            raise SimulatedKill()
        controller._write_ssh_snippet = crash
        with self.assertRaises(SimulatedKill): controller.apply()
        self.assertTrue((self.fs / lg2.SSH_SNIPPET.lstrip("/")).exists())
        self.assertEqual(controller.rollback()["phase"], "rolled_back")
        self.assertFalse((self.fs / lg2.SSH_SNIPPET.lstrip("/")).exists())

    def test_mutation_has_durable_intent_before_ufw_command(self):
        controller = self.ready(self.controller())
        seen = []
        def inspect(argv):
            if argv[0] == "ufw" and "status" not in argv:
                intent = self.state().get("active_intent")
                self.assertIsInstance(intent, dict)
                self.assertTrue(intent.get("paths"))
                seen.append(argv)
        self.runner.on_call = inspect
        controller.apply()
        self.assertGreaterEqual(len(seen), 4)

    def test_systemd_real_timer_duration_format_is_parsed_as_absolute_uptime(self):
        self.assertAlmostEqual(lg2.AccessController._timer_deadline_monotonic_seconds("1h 25min 36.842275s"), 5136.842275, places=6)
        self.assertEqual(lg2.AccessController._timer_deadline_monotonic_seconds("unknown"), 0)

    def test_ufw_runtime_is_disabled_even_when_one_file_has_foreign_drift(self):
        controller = self.ready(self.controller())
        controller.apply()
        conflict = self.fs / "etc/ufw/user.rules"
        foreign = b"foreign administrator change\n"
        conflict.write_bytes(foreign)
        with self.assertRaises(lg2.ControllerError): controller.rollback()
        self.assertFalse(self.runner.ufw_active)
        self.assertEqual(conflict.read_bytes(), foreign)
        self.assertEqual(self.state()["phase"], "rollback_incomplete")

    def test_failed_atomic_restore_publish_preserves_full_previous_bytes_and_can_retry(self):
        controller = self.ready(self.controller())
        controller.apply()
        state = self.state()
        change = next(v for v in state["changes"] if v["path"] == "/etc/ufw/user.rules")
        target = self.fs / "etc/ufw/user.rules"
        after = target.read_bytes()
        replace = lg2.os.replace
        def fail_publish(src, dst):
            if Path(dst) == target: raise OSError("injected publish failure")
            return replace(src, dst)
        with mock.patch.object(lg2.os, "replace", side_effect=fail_publish):
            with self.assertRaises((OSError, lg2.ControllerError)):
                controller._restore_file(change, state)
        self.assertEqual(target.read_bytes(), after)
        self.assertEqual(controller.rollback()["phase"], "rolled_back")
        self.assertEqual(target.read_bytes(), b"*filter\nCOMMIT\n")

    def test_commit_refuses_post_apply_drift_and_keeps_timer_armed(self):
        controller = self.ready(self.controller())
        controller.apply()
        target = self.fs / lg2.SSH_SNIPPET.lstrip("/")
        target.write_text(target.read_text() + "# foreign edit\n")
        with self.assertRaises(lg2.ControllerError): controller.commit(parent_verified=True)
        self.assertTrue(self.runner.timer_active)
        self.assertEqual(self.state()["phase"], "applied")

    def test_foreign_ssh_edit_between_apply_steps_is_preserved(self):
        controller = self.ready(self.controller())
        target = self.fs / lg2.SSH_SNIPPET.lstrip("/")
        foreign = b"# foreign administrator edit between mutations\n"
        edited = []
        def edit_during_ufw(argv):
            if argv[0] == "ufw" and "default" in argv and not edited:
                target.write_bytes(foreign)
                edited.append(True)
        self.runner.after_call = edit_during_ufw
        with self.assertRaises(lg2.ControllerError): controller.apply()
        self.assertTrue(edited)
        self.assertEqual(target.read_bytes(), foreign)
        self.assertFalse(self.runner.ufw_active)
        self.assertEqual(self.state()["phase"], "rollback_incomplete")

    def test_crash_after_restore_replace_can_retry_from_persisted_state(self):
        class SimulatedKill(BaseException): pass
        controller = self.ready(self.controller())
        controller.apply()
        target = self.fs / "etc/ufw/user.rules"
        replace = lg2.os.replace
        def kill_after_publish(src, dst):
            result = replace(src, dst)
            if Path(dst) == target: raise SimulatedKill()
            return result
        with mock.patch.object(lg2.os, "replace", side_effect=kill_after_publish):
            with self.assertRaises(SimulatedKill): controller.rollback()
        self.assertEqual(target.read_bytes(), b"*filter\nCOMMIT\n")
        self.assertEqual(self.controller().rollback()["phase"], "rolled_back")
        self.assertFalse(self.runner.ufw_active)

    def test_final_runtime_probe_failure_remains_retryable(self):
        controller = self.ready(self.controller())
        controller.apply()
        with mock.patch.object(controller, "_service_state", side_effect=lg2.ControllerError("injected final probe failure")):
            with self.assertRaises(lg2.ControllerError): controller.rollback()
        self.assertEqual(self.state()["phase"], "rollback_incomplete")
        self.assertEqual(controller.rollback()["phase"], "rolled_back")

    def test_final_inactive_ssh_state_makes_rollback_incomplete(self):
        controller = self.ready(self.controller())
        controller.apply()
        with mock.patch.object(controller, "_service_state", return_value="inactive"):
            with self.assertRaises(lg2.ControllerError): controller.rollback()
        self.assertEqual(self.state()["phase"], "rollback_incomplete")
        self.assertEqual(controller.rollback()["phase"], "rolled_back")

    def test_final_contradictory_ufw_state_makes_rollback_incomplete(self):
        controller = self.ready(self.controller())
        controller.apply()
        with mock.patch.object(controller, "_ufw_active", side_effect=[False, True]):
            with self.assertRaises(lg2.ControllerError): controller.rollback()
        self.assertEqual(self.state()["phase"], "rollback_incomplete")
        self.assertEqual(controller.rollback()["phase"], "rolled_back")

    def test_exact_copied_controller_cli_rollback_in_isolated_filesystem(self):
        controller = self.ready(self.controller())
        controller.apply()
        helper = self.fs / self.workdir.lstrip("/") / "rollback.py"
        spec = importlib.util.spec_from_file_location("lg2_copied_rollback_test", helper)
        copied = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = copied
        try:
            with mock.patch.object(sys, "dont_write_bytecode", True):
                spec.loader.exec_module(copied)
            real_class = copied.AccessController
            with mock.patch.object(lg2, "AccessController", real_class):
                isolated = self.controller()
            self.assertIsInstance(isolated, real_class)
            output = io.StringIO()
            with mock.patch.object(copied, "AccessController", return_value=isolated), mock.patch.object(lg2, "CommandResult", copied.CommandResult), contextlib.redirect_stdout(output):
                code = copied.main(["--workdir", self.workdir, "rollback"])
            self.assertEqual(code, 0, output.getvalue())
            self.assertEqual(json.loads(output.getvalue())["phase"], "rolled_back")
            self.assertFalse(self.runner.ufw_active)
        finally:
            sys.modules.pop(spec.name, None)

    def test_prepare_fails_closed_on_wrong_host_or_nonroot_before_commands(self):
        with self.assertRaises(lg2.ControllerError):
            self.controller(hostname="another-vm").prepare()
        with self.assertRaises(lg2.ControllerError):
            self.controller(uid=1000).prepare()
        self.assertEqual(self.runner.calls, [])

    def test_workdir_must_be_a_new_direct_child_of_root_with_utc_stamp(self):
        for bad in (
            "relative/aurelia-access-20261015T010203Z",
            "/tmp/aurelia-access-20261015T010203Z",
            "/root/aurelia-access-today",
            "/root/../tmp/aurelia-access-20261015T010203Z",
        ):
            with self.subTest(workdir=bad), self.assertRaises(lg2.ControllerError):
                self.controller(workdir=bad).prepare()
        self.assertEqual(self.runner.calls, [])

    def test_prepare_rejects_symlinked_ssh_config_before_creating_backup(self):
        source = self.fs / "etc/ssh/sshd_config.d/50-cloud-init.conf"
        real = self.fs / "etc/ssh/real.conf"
        source.unlink()
        try:
            source.symlink_to(real)
        except (OSError, NotImplementedError):
            self.skipTest("symlink creation is unavailable in this environment")
        with self.assertRaises(lg2.ControllerError):
            self.controller().prepare()
        self.assertFalse((self.fs / self.workdir.lstrip("/")).exists())

    def test_prepare_snapshots_only_allowed_config_files_with_exact_hash_and_mode(self):
        controller = self.controller()
        result = controller.prepare()
        manifest_path = self.fs / self.workdir.lstrip("/") / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        paths = {item["path"] for item in manifest["files"]}
        self.assertEqual(
            paths,
            {
                "/etc/ssh/sshd_config",
                "/etc/ssh/sshd_config.d/50-cloud-init.conf",
                "/etc/default/ufw",
                "/etc/ufw/ufw.conf",
                "/etc/ufw/user.rules",
                "/etc/ufw/user6.rules",
            },
        )
        self.assertNotIn("/etc/ssh/ssh_host_ed25519_key", paths)
        self.assertNotIn("/etc/shadow", paths)
        main = next(item for item in manifest["files"] if item["path"] == "/etc/ssh/sshd_config")
        source = self.fs / "etc/ssh/sshd_config"
        self.assertEqual(main["sha256"], hashlib.sha256(source.read_bytes()).hexdigest())
        self.assertEqual(main["mode"], 0o640)
        self.assertEqual(result["phase"], "prepared")

    def test_prepare_timer_is_scheduled_after_validation_and_before_any_config_mutation(self):
        def inspect_timer(argv):
            if argv[0] == "systemd-run":
                self.assertFalse((self.fs / "etc/ssh/sshd_config.d/00-aurelia-access.conf").exists())
                self.assertEqual((self.fs / "etc/ufw/user.rules").read_text(), "*filter\nCOMMIT\n")

        self.runner.on_call = inspect_timer
        self.controller().prepare()
        self.assertTrue(any(call[0] == "sshd" and "-t" in call for call in self.runner.calls))
        self.assertTrue(self.runner.timer_active)

    def test_open_ssh_public_key_parser_rejects_authorized_key_options_and_newlines(self):
        valid_blob = "AAAAC3NzaC1lZDI1NTE5AAAAIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
        with self.assertRaises(lg2.ControllerError):
            lg2.validate_public_key(f'restrict ssh-ed25519 {valid_blob}')
        with self.assertRaises(lg2.ControllerError):
            lg2.validate_public_key(f"ssh-ed25519 {valid_blob}\ncommand=bad")

    def test_apply_refuses_snapshot_drift_before_running_mutating_commands(self):
        controller = self.controller()
        self.ready(controller)
        self.runner.calls.clear()
        target = self.fs / "etc/ssh/sshd_config.d/50-cloud-init.conf"
        target.write_text("PasswordAuthentication no\n", encoding="utf-8")
        with self.assertRaises(lg2.ControllerError):
            controller.apply()
        self.assertFalse(any(call[:2] == ["ufw", "allow"] for call in self.runner.calls))
        self.assertFalse((self.fs / "etc/ssh/sshd_config.d/00-aurelia-access.conf").exists())

    def test_rollback_of_committed_state_is_noop_under_the_shared_lock(self):
        controller = self.controller()
        controller.prepare()
        state_path = self.fs / self.workdir.lstrip("/") / "state.json"
        state = json.loads(state_path.read_text(encoding="utf-8"))
        state["phase"] = "committed"
        state_path.write_text(json.dumps(state), encoding="utf-8")
        before = list(self.runner.calls)
        result = controller.rollback()
        self.assertTrue(result["noop"])
        self.assertEqual(self.runner.calls, before)


if __name__ == "__main__":
    unittest.main()
