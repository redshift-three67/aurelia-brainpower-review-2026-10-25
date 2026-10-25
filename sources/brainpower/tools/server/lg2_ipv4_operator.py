"""Windows control only; Linux validation and bounded server configuration."""
import base64
import hashlib
import json
from pathlib import Path
import sys

from lg2_permanent_operator import acceptance_code, ssh

STAMP = "20261016T070215Z"
CHECKPOINT = Path("checkpoints") / ("Aurelia-LG2-IPv4-" + STAMP)
VALIDATION = "/root/aurelia-ipv4-validation-" + STAMP
WORKDIR = "/root/aurelia-ipv4-" + STAMP
TOOL = VALIDATION + "/tools/server/lg2_ipv4_control.py"
TIMER = "aurelia-ipv4-rollback-" + STAMP + ".timer"
ROLLBACK_SERVICE_PROPERTIES = (
    "Type=oneshot", "TimeoutStartSec=300s", "TimeoutStopSec=10s",
    "KillMode=control-group", "Environment=LC_ALL=C", "Restart=on-failure",
    "RestartSec=5s", "StartLimitIntervalSec=3600s", "StartLimitBurst=3",
)


def remote(code, data=None, label=None):
    raw = ssh("admin", code, data)
    if label:
        (CHECKPOINT / (label + ".json")).write_text(raw, encoding="utf-8")
    return json.loads(raw)


def payload():
    before = json.loads((CHECKPOINT / "PREFLIGHT-EXACT.json").read_text())["files"]
    expected = {}
    for name, item in before.items():
        expected[name] = {"exists": item is not None,
                          **{k: item[k] if item else None for k in ("sha256", "mode", "uid", "gid")},
                          "size": len(item["text"].encode()) if item else None}
    chrony = before["/etc/default/chrony"]["text"]
    assert chrony.count('DAEMON_OPTS="-F 1"') == 1
    desired = {
        "/etc/netplan/50-cloud-init.yaml": '''network:
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
''',
        "/etc/cloud/cloud.cfg.d/99-disable-network-config.cfg": "network: {config: disabled}\n",
        "/etc/sysctl.d/99-aurelia-ipv4.conf": (
            "net.ipv6.conf.all.disable_ipv6 = 1\n"
            "net.ipv6.conf.default.disable_ipv6 = 1\n"
            "net.ipv6.conf.lo.disable_ipv6 = 1\n"),
        "/etc/ssh/sshd_config.d/01-aurelia-ipv4.conf": "AddressFamily inet\nListenAddress 0.0.0.0\n",
        "/etc/systemd/system/ssh.socket.d/99-aurelia-ipv4.conf": (
            "[Socket]\nListenStream=\nListenStream=0.0.0.0:22\n"),
        "/etc/default/chrony": chrony.replace('DAEMON_OPTS="-F 1"', 'DAEMON_OPTS="-F 1 -4"'),
    }
    assert set(expected) == set(desired)
    return {"schema_version": 1, "hostname": "vm2565", "os_release": "24.04",
            "expected_before": expected, "desired": desired, "rollback_timer": TIMER}


def tests(label):
    names = ("tools/server/lg2_ipv4_control.py", "tests/test_lg2_ipv4_control.py")
    files = []
    for name in names:
        raw = Path(name).read_bytes()
        files.append({"path": name, "data": base64.b64encode(raw).decode(),
                      "sha256": hashlib.sha256(raw).hexdigest()})
    result = remote('''import os,pathlib,json,sys,base64,hashlib,subprocess,socket
assert os.geteuid()==0 and socket.gethostname()=="vm2565"
d=json.load(sys.stdin); root=pathlib.Path(d["root"])
assert str(root)=="/root/aurelia-ipv4-validation-20261016T070215Z" and not root.is_symlink()
root.mkdir(mode=0o700,exist_ok=True)
assert root.stat().st_uid==0 and root.stat().st_mode&0o777==0o700
for item in d["files"]:
 assert item["path"] in ("tools/server/lg2_ipv4_control.py","tests/test_lg2_ipv4_control.py")
 p=root/item["path"]; p.parent.mkdir(mode=0o700,parents=True,exist_ok=True)
 assert not p.is_symlink()
 raw=base64.b64decode(item["data"],validate=True); assert hashlib.sha256(raw).hexdigest()==item["sha256"]
 p.write_bytes(raw); p.chmod(0o600)
p=subprocess.run(["python3","-m","unittest","discover","-s","tests","-p","test_lg2_ipv4_control.py","-v"],cwd=root,capture_output=True,text=True,timeout=90)
print(json.dumps({"returncode":p.returncode,"stdout":p.stdout,"stderr":p.stderr,"files":[{"path":i["path"],"sha256":i["sha256"]} for i in d["files"]]}))''',
                    {"root": VALIDATION, "files": files}, label)
    return result


def controller(action, label):
    raw = Path("tools/server/lg2_ipv4_control.py").read_bytes()
    return remote('''import json,sys,pathlib,hashlib,subprocess
d=json.load(sys.stdin); p=pathlib.Path(d["tool"])
assert hashlib.sha256(p.read_bytes()).hexdigest()==d["sha256"]
args=["python3",str(p),"--workdir",d["workdir"],d["action"]]
if d["action"]=="prepare":
 payload=p.parents[2]/"payload.json"; payload.write_text(json.dumps(d["payload"])); payload.chmod(0o600)
 args.extend(["--payload-file",str(payload)])
r=subprocess.run(args,capture_output=True,text=True,timeout=180)
print(json.dumps({"exit_code":r.returncode,"stdout":r.stdout,"stderr":r.stderr}))''',
                  {"tool": TOOL, "sha256": hashlib.sha256(raw).hexdigest(),
                   "workdir": WORKDIR, "action": action,
                   "payload": payload() if action == "prepare" else None}, label)


def protected_status(label):
    baseline = json.loads((CHECKPOINT / "PRIOR-CHECKPOINT-MANIFEST.json").read_text())["manifest"]["files"]
    return remote('''import os,json,sys,pathlib,hashlib,stat,subprocess,re
d=json.load(sys.stdin);result={"files":[],"ufw_runtime":{}}
assert len(d)==19
for item in d:
 p=pathlib.Path(item["path"]);s=p.lstat();assert stat.S_ISREG(s.st_mode) and not p.is_symlink()
 actual={"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"uid":s.st_uid,"gid":s.st_gid,"mode":stat.S_IMODE(s.st_mode)}
 ok=actual=={"sha256":item["sha256"],"uid":item["original_uid"],"gid":item["original_gid"],"mode":item["original_mode"]}
 result["files"].append({"path":str(p),"matches_prior":ok,"actual":actual})
 assert ok, str(p)+" differs from accepted protected baseline"
for c in (["ufw","status","numbered"],["iptables-save","-t","filter"],["ip6tables-save","-t","filter"]):
 p=subprocess.run(c,capture_output=True,text=True,timeout=20);assert p.returncode==0,p.stderr
 out=p.stdout
 if c[0]!="ufw":
  out='\\n'.join(re.sub(r'\\[\\d+:\\d+\\]','[COUNTERS]',line) for line in out.splitlines() if 'ufw-' in line or re.match(r':(?:INPUT|OUTPUT|FORWARD) ',line))
 else:assert out.startswith("Status: active"),out
 result["ufw_runtime"][' '.join(c)]={"sha256":hashlib.sha256(out.encode()).hexdigest(),"text":out}
result["all_19_unchanged"]=True
print(json.dumps(result))''', baseline, label)


def unit_action(action, label):
    raw = Path("tools/server/lg2_ipv4_control.py").read_bytes()
    return remote('''import json,sys,pathlib,hashlib,subprocess
d=json.load(sys.stdin);tool=pathlib.Path(d["workdir"])/"controller.py"
assert hashlib.sha256(tool.read_bytes()).hexdigest()==d["sha256"]
base=["/usr/bin/python3",str(tool),"--workdir",d["workdir"]]
def call(args,timeout=60):
 p=subprocess.run(args,capture_output=True,text=True,timeout=timeout)
 assert p.returncode==0,(p.returncode,p.stdout,p.stderr)
 return p.stdout
state=json.loads(call(base+["status"]))
assert state["phase"]=="prepared"
check=json.loads(call(base+["rollback-check"]))
assert check["ok"] and not check["noop"]
stamp=d["stamp"];result={"action":d["action"]}
if d["action"]=="rollback-probe":
 args=["systemd-run","--unit=aurelia-ipv4-probe-"+stamp,"--wait","--pipe","--collect","--property=Type=oneshot","--property=TimeoutStartSec=60s"]+base+["rollback-check"]
 result["probe"]=json.loads(call(args))
elif d["action"]=="arm":
 args=["systemd-run","--unit=aurelia-ipv4-rollback-"+stamp,"--on-active=15m","--timer-property=AccuracySec=1s"]+["--property="+p for p in d["rollback_properties"]]+base+["rollback"]
 result["start"]=call(args)
 result["timer_state"]=call(["systemctl","is-active",d["timer"]]).strip()
 assert result["timer_state"]=="active"
 result["timer_readback"]=call(["systemctl","show",d["timer"],"-p","ActiveState","-p","NextElapseUSecMonotonic","-p","Triggers"])
 result["service_readback"]=call(["systemctl","show",d["timer"].removesuffix(".timer")+".service","-p","ExecStart","-p","Type","-p","TimeoutStartUSec","-p","TimeoutStopUSec","-p","KillMode","-p","Restart","-p","RestartUSec","-p","StartLimitIntervalUSec","-p","StartLimitBurst"])
 assert str(tool) in result["service_readback"] and "TimeoutStartUSec=5min" in result["service_readback"]
 assert "Type=oneshot" in result["service_readback"] and "KillMode=control-group" in result["service_readback"]
 assert "Restart=on-failure" in result["service_readback"] and "RestartUSec=5s" in result["service_readback"]
 assert "StartLimitIntervalUSec=1h" in result["service_readback"] and "StartLimitBurst=3" in result["service_readback"]
else:
 assert d["action"]=="apply-unit" and state["checks"]["timer_active"]
 args=["systemd-run","--unit=aurelia-ipv4-apply-"+stamp,"--property=Type=exec","--property=RuntimeMaxSec=300s","--property=TimeoutStopSec=10s","--property=KillMode=control-group","--property=Environment=LC_ALL=C"]+base+["apply"]
 result["start"]=call(args)
 result["service_readback"]=call(["systemctl","show","aurelia-ipv4-apply-"+stamp+".service","-p","ExecStart","-p","Type","-p","RuntimeMaxUSec","-p","TimeoutStopUSec","-p","KillMode"])
 assert str(tool) in result["service_readback"] and "RuntimeMaxUSec=5min" in result["service_readback"]
 assert "Type=exec" in result["service_readback"] and "KillMode=control-group" in result["service_readback"]
print(json.dumps(result))''',
                  {"action": action, "workdir": WORKDIR, "stamp": STAMP,
                   "timer": TIMER, "sha256": hashlib.sha256(raw).hexdigest(),
                   "rollback_properties": list(ROLLBACK_SERVICE_PROPERTIES)}, label)


def accept_commit(label):
    import contextlib
    import io
    from concurrent.futures import ThreadPoolExecutor

    def login(role):
        code = "from datetime import datetime,timezone\n" + acceptance_code(role).replace(
            "print(json.dumps(r))", 'r["verified_at"]=datetime.now(timezone.utc).isoformat();print(json.dumps(r))')
        # Capture transport printing together below; every result remains in its own evidence file.
        raw = ssh(role, code)
        result = json.loads(raw)
        (CHECKPOINT / ("LOGIN-" + role.upper() + "-" + label + ".json")).write_text(raw, encoding="utf-8")
        return role, result

    with contextlib.redirect_stdout(io.StringIO()) as transport_log:
        try:
            with ThreadPoolExecutor(max_workers=3) as pool:
                logins = dict(pool.map(login, ("admin", "ops", "website")))
        except BaseException:
            print(transport_log.getvalue(), file=sys.stderr)
            raise
    result = controller("status", "PRE-COMMIT-STATUS")
    assert result["exit_code"] == 0
    state = json.loads(result["stdout"])
    assert state["phase"] == "applied" and state["checks"]["runtime"]["healthy"]
    from datetime import datetime
    assert all(datetime.fromisoformat(r["verified_at"]) >= datetime.fromisoformat(state["applied_at"].replace("Z", "+00:00")) for r in logins.values())
    proof = {"schema_version": 1, "workdir": WORKDIR,
             "desired_manifest_sha256": state["desired_manifest_sha256"],
             "issued_at": max(r["verified_at"] for r in logins.values()),
             "roles": {role: True for role in logins}}
    (CHECKPOINT / "FRESH-LOGIN-PROOF.json").write_text(json.dumps(proof, indent=2) + "\n")
    raw = Path("tools/server/lg2_ipv4_control.py").read_bytes()
    return remote('''import json,sys,pathlib,hashlib,subprocess
d=json.load(sys.stdin);root=pathlib.Path(d["workdir"]);tool=root/"controller.py"
assert hashlib.sha256(tool.read_bytes()).hexdigest()==d["sha256"]
p=root/"fresh-login-proof.json";assert not p.exists();p.write_text(json.dumps(d["proof"]));p.chmod(0o600)
r=subprocess.run(["python3",str(tool),"--workdir",str(root),"commit","--proof-file",str(p)],capture_output=True,text=True,timeout=150)
print(json.dumps({"exit_code":r.returncode,"stdout":r.stdout,"stderr":r.stderr}))''',
                  {"workdir": WORKDIR, "sha256": hashlib.sha256(raw).hexdigest(), "proof": proof}, label)


if __name__ == "__main__":
    action, label = sys.argv[1:3]
    if action == "tests":
        result = tests(label)
        sys.exit(result["returncode"])
    if action == "payload":
        result = payload()
        (CHECKPOINT / (label + ".json")).write_text(json.dumps(result, indent=2) + "\n")
    elif action in ("prepare", "status", "rollback-check"):
        result = controller(action, label)
        sys.exit(result["exit_code"])
    elif action == "protected-status":
        protected_status(label)
    elif action in ("rollback-probe", "arm", "apply-unit"):
        unit_action(action, label)
    elif action == "accept-commit":
        result = accept_commit(label)
        sys.exit(result["exit_code"])
    else:
        raise ValueError("Unsupported operator action")
