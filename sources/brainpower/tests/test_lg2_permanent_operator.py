"""No-network regressions for the mandatory fresh-login retirement gate."""
import json
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
import contextlib
import io
from unittest.mock import patch
import sys

if not sys.platform.startswith("linux"):
    raise unittest.SkipTest("requires Linux account semantics")

from tools.server import lg2_permanent_operator as operator


class OperatorGateTests(unittest.TestCase):
    def test_failed_fresh_login_prevents_retire_command(self):
        with patch.object(operator.sys, "argv", ["operator", "retire"]), patch.object(operator, "accept_roles", side_effect=RuntimeError("login refused")) as verify, patch.object(operator, "ssh") as ssh:
            with self.assertRaisesRegex(RuntimeError, "login refused"):
                operator.main()
            verify.assert_called_once_with("PRE-RETIRE")
            ssh.assert_not_called()

    def test_all_three_roles_required_in_order(self):
        with patch.object(operator, "ssh") as ssh:
            operator.accept_roles("CHECK")
            self.assertEqual([call.args[0] for call in ssh.call_args_list], ["admin", "ops", "website"])

    def test_root_login_cannot_satisfy_project_role(self):
        for role in ("ops", "website"):
            with self.subTest(role=role), patch("pwd.getpwuid", return_value=SimpleNamespace(pw_name="root", pw_uid=0)):
                with self.assertRaises(AssertionError):
                    exec(operator.acceptance_code(role), {})

    def test_changed_profile_refused_before_ssh(self):
        with tempfile.TemporaryDirectory() as folder:
            checkpoint = Path(folder)
            profile = checkpoint / "ssh_config"
            profile.write_text("tampered profile")
            (checkpoint / "PUBLIC-CLIENTS.json").write_text(json.dumps({"roles": {"ops": {"profile": str(profile), "alias": "test", "config_sha256": "0" * 64}}}))
            with patch.object(operator, "CHECKPOINT", checkpoint), patch.object(operator.subprocess, "run") as run:
                with self.assertRaisesRegex(ValueError, "differs"):
                    operator.ssh("ops", "pass")
                run.assert_not_called()

    def test_root_sudo_query_requires_exact_explicit_denial(self):
        with tempfile.TemporaryDirectory() as folder:
            account = SimpleNamespace(pw_name="root", pw_uid=0, pw_gid=0, pw_dir=folder)
            def denied(argv, **kwargs):
                return SimpleNamespace(returncode=0, stdout=f"User {argv[-1]} is not allowed to run sudo on vm2565.\n", stderr="")
            with patch("pwd.getpwuid", return_value=account), patch("socket.gethostname", return_value="vm2565"), patch.dict("os.environ", {"SSH_CONNECTION": "192.0.2.1 1000 193.142.40.36 22"}), patch("subprocess.run", side_effect=denied), contextlib.redirect_stdout(io.StringIO()):
                exec(operator.acceptance_code("admin"), {})
            allowed = SimpleNamespace(returncode=0, stdout="User aurelia-ops may run the following commands: (ALL) ALL\n", stderr="")
            with patch("pwd.getpwuid", return_value=account), patch("socket.gethostname", return_value="vm2565"), patch.dict("os.environ", {"SSH_CONNECTION": "192.0.2.1 1000 193.142.40.36 22"}), patch("subprocess.run", return_value=allowed):
                with self.assertRaises(AssertionError):
                    exec(operator.acceptance_code("admin"), {})
