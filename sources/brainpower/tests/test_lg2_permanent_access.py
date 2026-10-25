"""Linux-only tests for the separate durable SSH access utility."""

import sys

# The production module uses POSIX ownership and dirfd APIs. Skip before import
# so Windows test discovery never imports a platform-specific module.
if not sys.platform.startswith("linux"):
    import unittest

    raise unittest.SkipTest("requires Linux POSIX filesystem semantics")

import base64
import json
import os
import struct
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from tools.server import lg2_permanent_access as access


def _ssh_key(seed: int) -> str:
    raw_key = bytes([seed]) * 32
    wire = struct.pack(">I", len(b"ssh-ed25519")) + b"ssh-ed25519"
    wire += struct.pack(">I", len(raw_key)) + raw_key
    return "ssh-ed25519 " + base64.b64encode(wire).decode("ascii")


def _payload():
    return {
        "admin": {"public_key": _ssh_key(1)},
        "ops": {"public_key": _ssh_key(2)},
        "website": {"public_key": _ssh_key(3)},
    }


class FakeHost:
    def __init__(self, fs_root: Path):
        self.fs_root = fs_root
        self.root = True
        self.ubuntu = True
        self.host_name = "vm2565"
        self.users = {
            "root": SimpleNamespace(uid=0, gid=0, home="/root"),
            "aurelia-ops": SimpleNamespace(uid=1000, gid=1000, home="/home/aurelia-ops"),
        }
        self.groups_by_name = {"root": 0, "aurelia-ops": 1000}
        self.groups_by_user = {"root": (0,), "aurelia-ops": (1000,)}
        self.commands = []

    def is_linux(self):
        return True

    def is_root(self):
        return self.root

    def is_ubuntu(self):
        return self.ubuntu

    def hostname(self):
        return self.host_name

    def which(self, name):
        return "/usr/sbin/" + name

    def user(self, name):
        return self.users.get(name)

    def group(self, name):
        gid = self.groups_by_name.get(name)
        return None if gid is None else SimpleNamespace(name=name, gid=gid)

    def groups(self, name, primary_gid):
        return self.groups_by_user.get(name, (primary_gid,))

    def password_locked(self, name):
        return name == "rauch-web-test" and name in self.users

    def run(self, argv):
        self.commands.append(tuple(argv))
        if argv[0] == "useradd":
            self.users["rauch-web-test"] = SimpleNamespace(
                uid=1001, gid=1001, home="/home/rauch-web-test"
            )
            self.groups_by_name["rauch-web-test"] = 1001
            self.groups_by_user["rauch-web-test"] = (1001,)
            home = self.fs_root / "home" / "rauch-web-test"
            home.mkdir(mode=0o700, parents=True)
            os.chown(home, 1001, 1001)
            return
        raise AssertionError(f"unexpected command: {argv!r}")


@unittest.skipUnless(os.geteuid() == 0, "dirfd ownership checks require a root Linux test process")
class PermanentAccessTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "root" / ".ssh").mkdir(mode=0o700, parents=True)
        (self.root / "home" / "aurelia-ops" / ".ssh").mkdir(
            mode=0o700, parents=True
        )
        (self.root / "home" / "aurelia-ops").chmod(0o755)
        os.chown(self.root / "home" / "aurelia-ops", 1000, 1000)
        os.chown(self.root / "home" / "aurelia-ops" / ".ssh", 1000, 1000)
        self.host = FakeHost(self.root)
        self.manager = access.AccessManager(fs_root=self.root, host=self.host)
        self.workdir = "/root/aurelia-durable-access-20261016T000000Z"
        self.payload_path = self.root / "payload.json"
        self.payload_arg = "/payload.json"
        self.payload_path.write_text(json.dumps(_payload()), encoding="utf-8")

        self.root_before = (
            b"# root annotation\nrestrict,expiry-time=\"20261016T210835Z\" ssh-ed25519 "
            + access.OLD_ROOT_BLOB.encode("ascii")
            + b" bootstrap-root\n"
            + _ssh_key(4).encode("ascii")
            + b" unrelated-root\n"
        )
        self.ops_before = (
            _ssh_key(5).encode("ascii")
            + b" unrelated-ops\nrestrict ssh-ed25519 "
            + access.OLD_OPS_BLOB.encode("ascii")
            + b" bootstrap-ops"
        )
        (self.root / "root" / ".ssh" / "authorized_keys").write_bytes(self.root_before)
        (self.root / "home" / "aurelia-ops" / ".ssh" / "authorized_keys").write_bytes(
            self.ops_before
        )
        os.chown(self.root / "home" / "aurelia-ops" / ".ssh" / "authorized_keys", 1000, 1000)

    def tearDown(self):
        self.temp.cleanup()

    def test_stage_appends_restricted_keys_without_changing_existing_bytes(self):
        self.manager.stage(self.workdir, self.payload_arg)

        root_after = (self.root / "root" / ".ssh" / "authorized_keys").read_bytes()
        ops_after = (
            self.root / "home" / "aurelia-ops" / ".ssh" / "authorized_keys"
        ).read_bytes()
        website_after = (
            self.root / "home" / "rauch-web-test" / ".ssh" / "authorized_keys"
        ).read_bytes()
        self.assertTrue(root_after.startswith(self.root_before))
        self.assertTrue(ops_after.startswith(self.ops_before))
        self.assertTrue(root_after[len(self.root_before) :].startswith(b"restrict ssh-ed25519 "))
        self.assertIn(b"\nrestrict ssh-ed25519 ", ops_after[len(self.ops_before) :])
        self.assertEqual(website_after.count(b"restrict ssh-ed25519 "), 1)
        self.assertIn("-p", self.host.commands[0])
        self.assertIn("!", self.host.commands[0])

    def test_retirement_removes_only_old_blobs_and_keeps_new_and_unrelated_keys(self):
        self.manager.stage(self.workdir, self.payload_arg)
        self.manager.retire(self.workdir, verified=True)

        root_after = (self.root / "root" / ".ssh" / "authorized_keys").read_bytes()
        ops_after = (
            self.root / "home" / "aurelia-ops" / ".ssh" / "authorized_keys"
        ).read_bytes()
        self.assertIn(b"# root annotation\n", root_after)
        self.assertIn(b"unrelated-root", root_after)
        self.assertIn(b"unrelated-ops", ops_after)
        self.assertNotIn(b"bootstrap-root", root_after)
        self.assertNotIn(b"bootstrap-ops", ops_after)
        self.assertIn(_payload()["admin"]["public_key"].split()[1].encode(), root_after)
        self.assertIn(_payload()["ops"]["public_key"].split()[1].encode(), ops_after)
        self.assertNotIn(access.OLD_ROOT_BLOB.encode(), root_after)
        self.assertNotIn(access.OLD_OPS_BLOB.encode(), ops_after)
        self.assertEqual(self.manager.status(self.workdir)["phase"], "complete")

    def test_quoted_expiry_option_is_parsed_as_one_authorized_key_option(self):
        old_record = next(record for record in access._key_records(self.root_before)
                          if record[0] == access.OLD_ROOT_BLOB)
        self.assertEqual(old_record[1], ["restrict,expiry-time=20261016T210835Z"])

    def test_guards_and_duplicate_keys_fail_before_mutation(self):
        self.host.root = False
        with self.assertRaises(access.PermanentAccessError):
            self.manager.stage(self.workdir, self.payload_arg)
        self.assertFalse((self.root / "root" / "aurelia-durable-access-20261016T000000Z").exists())

        self.host.root = True
        self.host.host_name = "wrong-host"
        with self.assertRaises(access.PermanentAccessError):
            self.manager.stage(self.workdir, self.payload_arg)
        self.assertFalse((self.root / "root" / "aurelia-durable-access-20261016T000000Z").exists())
        self.host.host_name = "vm2565"
        data = _payload()
        data["ops"]["public_key"] = data["admin"]["public_key"]
        self.payload_path.write_text(json.dumps(data), encoding="utf-8")
        with self.assertRaises(access.PermanentAccessError):
            self.manager.stage(self.workdir, self.payload_arg)
        self.assertFalse((self.root / "root" / "aurelia-durable-access-20261016T000000Z").exists())

    def test_collision_and_drift_are_refused_without_retiring_old_keys(self):
        collision = _payload()["admin"]["public_key"].encode()
        (self.root / "root" / ".ssh" / "authorized_keys").write_bytes(
            self.root_before + b"\n" + collision + b" preexisting\n"
        )
        with self.assertRaises(access.PermanentAccessError):
            self.manager.stage(self.workdir, self.payload_arg)
        self.assertIn(access.OLD_ROOT_BLOB.encode(), (self.root / "root" / ".ssh" / "authorized_keys").read_bytes())

        (self.root / "root" / ".ssh" / "authorized_keys").write_bytes(self.root_before)
        self.manager.stage(self.workdir, self.payload_arg)
        root_keys = self.root / "root" / ".ssh" / "authorized_keys"
        root_keys.write_bytes(root_keys.read_bytes() + b"unrelated concurrent key\n")
        with self.assertRaises(access.PermanentAccessError):
            self.manager.retire(self.workdir, verified=True)
        self.assertIn(access.OLD_ROOT_BLOB.encode(), root_keys.read_bytes())
        self.assertIn(access.OLD_OPS_BLOB.encode(), (self.root / "home" / "aurelia-ops" / ".ssh" / "authorized_keys").read_bytes())

    def test_key_wire_validation_rejects_non_ed25519_and_bad_lengths(self):
        self.assertEqual(set(access.validate_payload(_payload())), {"admin", "ops", "website"})
        malformed = {
            "admin": {"public_key": "ssh-ed25519 !!!!"},
            "ops": {"public_key": _ssh_key(2)},
            "website": {"public_key": _ssh_key(3)},
        }
        with self.assertRaises(access.PermanentAccessError):
            access.validate_payload(malformed)

        bad_type = struct.pack(">I", len(b"ssh-rsa")) + b"ssh-rsa" + struct.pack(">I", 32) + bytes(32)
        bad_length = struct.pack(">I", 11) + b"ssh-ed25519" + struct.pack(">I", 31) + bytes(31)
        for wire in (bad_type, bad_length):
            candidate = _payload()
            candidate["admin"]["public_key"] = "ssh-ed25519 " + base64.b64encode(wire).decode()
            with self.subTest(wire=wire[:16]), self.assertRaises(access.PermanentAccessError):
                access.validate_payload(candidate)


if __name__ == "__main__":
    unittest.main()
