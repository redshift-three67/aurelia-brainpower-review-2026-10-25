"""Local orchestration for the explicitly approved LG2 key transition."""
import base64
import hashlib
import json
from pathlib import Path
import shlex
import subprocess
import sys

STAMP = "20261016T061825Z"
CHECKPOINT = Path("checkpoints") / ("Aurelia-LG2-Dauerzugaenge-" + STAMP)
REMOTE = "/root/aurelia-permanent-validation-" + STAMP
WORKDIR = "/root/aurelia-durable-access-" + STAMP
BOOTSTRAP = str(Path.home() / ".ssh/aurelia-lg2-bootstrap-20261015T210828Z/ssh_config")


def ssh(role, code, data=None, label=None):
    if role == "bootstrap":
        profile, alias = BOOTSTRAP, "aurelia-lg2-bootstrap"
    else:
        client = json.loads((CHECKPOINT / "PUBLIC-CLIENTS.json").read_text())["roles"][role]
        profile, alias = client["profile"], client["alias"]
        if hashlib.sha256(Path(profile).read_bytes()).hexdigest() != client["config_sha256"]:
            raise ValueError("SSH profile differs from verified manifest")
    command = "python3 -c " + shlex.quote(code)
    args = ["ssh", "-4", "-F", profile, "-o", "ControlMaster=no", "-o", "ControlPath=none", "-o", "ControlPersist=no", alias, command]
    process = subprocess.run(args, input=json.dumps(data) if data is not None else None, capture_output=True, text=True, timeout=240)
    result = {"role": role, "exit_code": process.returncode, "stdout": process.stdout, "stderr": process.stderr}
    if label:
        (CHECKPOINT / (label + ".json")).write_text(json.dumps(result, indent=2, ensure_ascii=True) + "\n", encoding="ascii")
    print(json.dumps(result, ensure_ascii=True))
    if process.returncode:
        raise SystemExit(process.returncode)
    return process.stdout


def acceptance_code(role):
    expected_user, expected_uid = {"admin": ("root", 0), "ops": ("aurelia-ops", 1000), "website": ("rauch-web-test", None)}[role]
    uid_check = f"p.pw_uid=={expected_uid}" if expected_uid is not None else "p.pw_uid>1000"
    return f'''import os,pwd,socket,json,pathlib,subprocess
p=pwd.getpwuid(os.geteuid())
assert p.pw_name=={expected_user!r}
assert {uid_check}
r={{"hostname":socket.gethostname(),"user":p.pw_name,"uid":p.pw_uid,"gid":p.pw_gid,"groups":os.getgroups(),"home_mode":oct(pathlib.Path(p.pw_dir).stat().st_mode&0o777),"ssh_connection":os.environ.get("SSH_CONNECTION")}}
assert r["hostname"]=="vm2565" and ":" not in r["ssh_connection"]
if p.pw_uid!=0:
 assert set(r["groups"])=={{p.pw_gid}}
 assert r["home_mode"]=="0o700"
 assert not os.access("/root/.ssh/authorized_keys",os.R_OK)
 other="/home/rauch-web-test" if p.pw_name=="aurelia-ops" else "/home/aurelia-ops"
 assert not os.access(other,os.R_OK|os.X_OK)
 r["other_project_home_denied"]=True
else:
 r["sudo_checks"]={{}}
 for user in ("aurelia-ops","rauch-web-test"):
  check=subprocess.run(["sudo","-n","-l","-U",user],capture_output=True,text=True,env={{**os.environ,"LC_ALL":"C"}})
  assert check.returncode==0 and check.stdout.strip()==f"User {{user}} is not allowed to run sudo on vm2565." and not check.stderr.strip()
  r["sudo_checks"][user]={{"exit_code":check.returncode,"denied":True}}
print(json.dumps(r))'''


def accept_roles(label):
    for role in ("admin", "ops", "website"):
        ssh(role, acceptance_code(role), label="LOGIN-" + role.upper() + "-" + label)


def main():
    action = sys.argv[1]
    if action == "preflight":
        code = '''import os,pwd,grp,socket,json,pathlib,hashlib,subprocess
assert os.geteuid()==0 and socket.gethostname()=="vm2565"
r={"hostname":socket.gethostname(),"utc":subprocess.check_output(["date","-u","+%FT%TZ"],text=True).strip(),"accounts":{}}
for user in ("root","aurelia-ops"):
 p=pwd.getpwnam(user); files={}
 for path in (pathlib.Path(p.pw_dir),pathlib.Path(p.pw_dir)/".ssh",pathlib.Path(p.pw_dir)/".ssh/authorized_keys"):
  st=path.lstat(); assert not path.is_symlink(); files[str(path)]={"uid":st.st_uid,"gid":st.st_gid,"mode":oct(st.st_mode&0o777),"sha256":hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None}
 r["accounts"][user]={"uid":p.pw_uid,"gid":p.pw_gid,"groups":os.getgrouplist(user,p.pw_gid),"files":files}
assert r["accounts"]["aurelia-ops"]["groups"]==[1000]
assert all(p.pw_name!="rauch-web-test" for p in pwd.getpwall())
assert all(g.gr_name!="rauch-web-test" for g in grp.getgrall())
assert not pathlib.Path("/home/rauch-web-test").exists()
r["website_absent"]=True
r["sshd_syntax"]=subprocess.run(["/usr/sbin/sshd","-t"],capture_output=True,text=True).returncode
assert r["sshd_syntax"]==0
print(json.dumps(r))'''
        ssh("bootstrap", code, label="PREFLIGHT")
    elif action == "tests":
        files = []
        for name in ("tools/server/lg2_permanent_access.py", "tests/test_lg2_permanent_access.py", "tools/server/lg2_permanent_operator.py", "tests/test_lg2_permanent_operator.py"):
            raw = Path(name).read_bytes()
            files.append({"path": name, "data": base64.b64encode(raw).decode(), "sha256": hashlib.sha256(raw).hexdigest()})
        code = '''import os,json,sys,pathlib,base64,hashlib,subprocess
assert os.geteuid()==0
data=json.load(sys.stdin); root=pathlib.Path(data["root"]); root.mkdir(mode=0o700,exist_ok=True)
for item in data["files"]:
 path=root/item["path"]; path.parent.mkdir(mode=0o700,parents=True,exist_ok=True); raw=base64.b64decode(item["data"]); assert hashlib.sha256(raw).hexdigest()==item["sha256"]; path.write_bytes(raw); path.chmod(0o600)
p=subprocess.run(["python3","-m","unittest","discover","-s","tests","-p","test_lg2_permanent*.py","-v"],cwd=root,capture_output=True,text=True)
print(json.dumps({"files":[{"path":i["path"],"sha256":i["sha256"]} for i in data["files"]],"returncode":p.returncode,"stdout":p.stdout,"stderr":p.stderr})); sys.exit(p.returncode)'''
        ssh("bootstrap", code, {"root": REMOTE, "files": files}, label="LINUX-TESTS")
    elif action in ("stage", "retire", "status"):
        if action == "retire":
            accept_roles("PRE-RETIRE")
        clients = json.loads((CHECKPOINT / "PUBLIC-CLIENTS.json").read_text())["roles"]
        payload = {role: {"public_key": item["public_key"]} for role, item in clients.items()}
        code = '''import os,json,sys,pathlib,subprocess,hashlib
assert os.geteuid()==0
d=json.load(sys.stdin); tool=pathlib.Path(d["tool"]); assert hashlib.sha256(tool.read_bytes()).hexdigest()==d["sha256"]
args=["python3",str(tool),"--workdir",d["workdir"],d["action"]]
if d["action"]=="stage":
 p=tool.parent/"public-payload.json"; p.write_text(json.dumps(d["payload"])); p.chmod(0o600); args.extend(["--payload-file",str(p)])
if d["action"]=="retire": args.append("--verified")
p=subprocess.run(args,capture_output=True,text=True); print(p.stdout,end=""); print(p.stderr,end="",file=sys.stderr); sys.exit(p.returncode)'''
        sha = hashlib.sha256(Path("tools/server/lg2_permanent_access.py").read_bytes()).hexdigest()
        ssh("bootstrap" if action == "stage" else "admin", code, {"tool": REMOTE + "/tools/server/lg2_permanent_access.py", "sha256": sha, "workdir": WORKDIR, "action": action, "payload": payload}, label=action.upper())
    elif action == "accept":
        accept_roles(sys.argv[2] if len(sys.argv) > 2 else "INITIAL")
    else:
        raise ValueError("Unknown action")


if __name__ == "__main__":
    main()
