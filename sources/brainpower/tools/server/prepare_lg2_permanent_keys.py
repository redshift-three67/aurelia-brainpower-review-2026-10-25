"""Prepare local operator-only SSH identities; never export private key bytes."""
import csv
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys

HOST_KEY = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIPWTo2e7dSPoE2ePEKoNhNY6jOKyB69Rlh7OoRgZY8qk"
HOST_FP = "SHA256:fKHw1GvT9mJDTG4Y9sXfgziO9Ok8s0EryS4G7E1WkEQ"
ROLES = {"admin": ("root", "aurelia-lg2-admin"), "ops": ("aurelia-ops", "aurelia-lg2-project"), "website": ("rauch-web-test", "rauch-lg2-test")}


def run(args):
    process = subprocess.run(args, capture_output=True, text=True)
    if process.returncode:
        raise RuntimeError(process.stderr.strip() or process.stdout.strip())
    return process.stdout.strip()


def main():
    stamp, output = sys.argv[1:3]
    verify_existing = sys.argv[3:] == ["--verify-existing"]
    if sys.argv[3:] and not verify_existing:
        raise ValueError("Unknown option")
    if len(stamp) != 16 or not stamp.endswith("Z") or not stamp.replace("T", "").replace("Z", "").isdigit():
        raise ValueError("Invalid UTC stamp")
    sid = next(csv.reader(io.StringIO(run(["whoami", "/user", "/fo", "csv", "/nh"]))))[1]
    bundle = Path.home() / ".ssh" / ("aurelia-lg2-permanent-" + stamp)
    if not verify_existing:
        bundle.mkdir(exist_ok=False)
    run(["icacls", str(bundle), "/inheritance:r", "/grant:r", f"*{sid}:(OI)(CI)F", "*S-1-5-18:(OI)(CI)F"])
    result = {"bundle": str(bundle), "operator_sid": sid, "roles": {}}
    for role, (user, alias) in ROLES.items():
        folder = bundle / role
        if not verify_existing:
            folder.mkdir()
        key = folder / "id_ed25519"
        if not verify_existing:
            run(["ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-f", str(key), "-C", f"lg2-{role}-{stamp}"])
        # Windows ssh-keygen adds explicit grants: replace with exactly two SIDs.
        for protected in (key, key.with_suffix(".pub")):
            run(["icacls", str(protected), "/inheritance:r", "/grant:r", f"*{sid}:F", "*S-1-5-18:F"])
            run(["icacls", str(protected), "/remove:g", "*S-1-5-32-544", "*S-1-1-0"])
        public = key.with_suffix(".pub").read_text(encoding="ascii").strip()
        derived = run(["ssh-keygen", "-y", "-f", str(key)])
        if public.split()[:2] != derived.split()[:2]:
            raise ValueError("Private/public pair mismatch")
        known = folder / "known_hosts"
        known.write_text(f"193.142.40.36,vm2565.ipp-vps.net {HOST_KEY}\n", encoding="ascii")
        if HOST_FP not in run(["ssh-keygen", "-lf", str(known)]):
            raise ValueError("Host fingerprint mismatch")
        config = folder / "ssh_config"
        config.write_text(f'''Host {alias}
    HostName 193.142.40.36
    User {user}
    Port 22
    AddressFamily inet
    IdentityFile "{key.as_posix()}"
    UserKnownHostsFile "{known.as_posix()}"
    GlobalKnownHostsFile none
    IdentitiesOnly yes
    IdentityAgent none
    PreferredAuthentications publickey
    PasswordAuthentication no
    KbdInteractiveAuthentication no
    BatchMode yes
    StrictHostKeyChecking yes
    HostKeyAlgorithms ssh-ed25519
    RequestTTY no
    ForwardAgent no
    ClearAllForwardings yes
    ControlMaster no
    ControlPath none
    ControlPersist no
    ConnectTimeout 15
    ServerAliveInterval 15
''', encoding="ascii")
        effective = run(["ssh", "-G", "-F", str(config), alias])
        expected = [f"user {user}", "hostname 193.142.40.36", "addressfamily inet", "passwordauthentication no", "kbdinteractiveauthentication no", "stricthostkeychecking true", "identitiesonly yes", "batchmode yes"]
        if any(item not in effective.splitlines() for item in expected):
            raise ValueError("SSH effective configuration mismatch")
        result["roles"][role] = {"user": user, "alias": alias, "profile": str(config), "public_key": public, "fingerprint": run(["ssh-keygen", "-lf", str(key.with_suffix(".pub"))]), "config_sha256": hashlib.sha256(config.read_bytes()).hexdigest()}
    script = "$ErrorActionPreference='Stop'; $p='" + str(bundle).replace("'", "''") + "'; $allowed=@('" + sid + "','S-1-5-18'); $items=@(Get-Item -LiteralPath $p)+@(Get-ChildItem -LiteralPath $p -Recurse -Force); foreach($item in $items){ $acl=Get-Acl -LiteralPath $item.FullName; foreach($rule in $acl.Access){$s=$rule.IdentityReference.Translate([System.Security.Principal.SecurityIdentifier]).Value; if($s -notin $allowed -or $rule.AccessControlType -ne 'Allow'){throw 'Unexpected ACL principal or deny rule'}} }; 'ACL_VERIFIED'"
    if run(["pwsh", "-NoProfile", "-NonInteractive", "-Command", script]) != "ACL_VERIFIED":
        raise ValueError("ACL verification failed")
    result["acl_verified"] = True
    Path(output).write_text(json.dumps(result, indent=2, ensure_ascii=True) + "\n", encoding="ascii")
    print(json.dumps({"bundle": str(bundle), "acl_verified": True, "roles": {k: {"user": v["user"], "fingerprint": v["fingerprint"]} for k, v in result["roles"].items()}}, ensure_ascii=True))


if __name__ == "__main__":
    main()
