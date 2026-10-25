"""Explicit, recorded steps for the two-user LG2 test infrastructure."""
import contextlib
import io
import json
import sys

import lg2_ipv4_operator as operator
import lg2_permanent_operator as access


def run(label, code, data=None):
    with contextlib.redirect_stdout(io.StringIO()) as captured:
        try:
            result = operator.remote(code, data, label)
        except BaseException:
            print(captured.getvalue(), file=sys.stderr)
            raise
    print(json.dumps(result, ensure_ascii=True), flush=True)
    return result


REPOSITORY = r"""
import os,pathlib,subprocess,json,hashlib
assert os.geteuid()==0
def call(args,timeout=120):
 p=subprocess.run(args,capture_output=True,timeout=timeout)
 assert p.returncode==0,(args,p.returncode,p.stdout.decode(),p.stderr.decode())
 return p
key=call(['curl','-4','-fsSL','--proto','=https','--tlsv1.2','https://download.docker.com/linux/ubuntu/gpg'],30).stdout
q=subprocess.run(['gpg','--show-keys','--with-colons'],input=key,capture_output=True,timeout=20)
assert q.returncode==0
fingerprints=[l.split(':')[9] for l in q.stdout.decode().splitlines() if l.startswith('fpr:')]
assert fingerprints[0]=='9DC858229FC7DD38854AE2D88D81803C0EBFCD88'
kp=pathlib.Path('/etc/apt/keyrings/docker.asc');sp=pathlib.Path('/etc/apt/sources.list.d/docker.sources')
source=chr(10).join(['Types: deb','URIs: https://download.docker.com/linux/ubuntu','Suites: noble','Components: stable','Architectures: amd64','Signed-By: /etc/apt/keyrings/docker.asc',''])
for path,raw in ((kp,key),(sp,source.encode())):
 assert not path.is_symlink()
 if path.exists(): assert path.read_bytes()==raw,str(path)+' differs'
 else:
  path.parent.mkdir(mode=0o755,exist_ok=True);path.write_bytes(raw);path.chmod(0o644)
out=call(['apt-get','-o','Acquire::ForceIPv4=true','-o','APT::Update::Error-Mode=any','update'])
print(json.dumps({'fingerprints':fingerprints,'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'stdout':out.stdout.decode(),'stderr':out.stderr.decode()}))
"""

BOOTSTRAP = r"""
import os,pathlib,subprocess,json,pwd
assert os.geteuid()==0
def call(args):
 p=subprocess.run(args,capture_output=True,text=True,timeout=45)
 assert p.returncode==0,(args,p.returncode,p.stdout,p.stderr)
 return p.stdout.strip()
configs={}
for uid,user,cpu,high,maximum,swap,tasks in [(1000,'aurelia-ops',500,'8G','10G','1G',1024),(1001,'rauch-web-test',100,'2G','4G','256M',512)]:
 assert pwd.getpwnam(user).pw_uid==uid
 configs[f'/etc/systemd/system/user-{uid}.slice.d/50-aurelia-testbudget.conf']=f'[Slice]\nCPUQuota={cpu}%\nMemoryHigh={high}\nMemoryMax={maximum}\nMemorySwapMax={swap}\nTasksMax={tasks}\n'
 configs[f'/etc/systemd/system/user@{uid}.service.d/50-aurelia-delegate.conf']='[Service]\nDelegate=cpu cpuset io memory pids\n'
for name,text in configs.items():
 path=pathlib.Path(name);assert not path.is_symlink()
 if path.exists(): assert path.read_text()==text,name+' differs'
 else:
  path.parent.mkdir(mode=0o755,exist_ok=True);path.write_text(text);path.chmod(0o644)
call(['systemctl','daemon-reload'])
r={}
for uid,user in [(1000,'aurelia-ops'),(1001,'rauch-web-test')]:
 call(['loginctl','enable-linger',user]);call(['systemctl','start',f'user@{uid}.service'])
 r[user]={'slice':call(['systemctl','show',f'user-{uid}.slice','-p','CPUQuotaPerSecUSec','-p','MemoryHigh','-p','MemoryMax','-p','MemorySwapMax','-p','TasksMax']), 'delegate':call(['systemctl','show',f'user@{uid}.service','-p','DelegateControllers']), 'controllers':pathlib.Path(f'/sys/fs/cgroup/user.slice/user-{uid}.slice/user@{uid}.service/cgroup.controllers').read_text().strip()}
 assert all(x in r[user]['controllers'].split() for x in ['cpu','cpuset','io','memory','pids']),r[user]
for unit in ['docker.service','docker.socket','containerd.service']:
 q=subprocess.run(['systemctl','is-enabled',unit],capture_output=True,text=True,timeout=10)
 assert q.returncode==1 and q.stdout.strip()=='masked',(unit,q.returncode,q.stdout,q.stderr)
print(json.dumps(r))
"""

ROOTLESS = r"""
import os,pathlib,pwd,subprocess,json
p=pwd.getpwuid(os.geteuid());assert (p.pw_name,p.pw_uid) in [('aurelia-ops',1000),('rauch-web-test',1001)]
assert set(os.getgroups())=={p.pw_gid}
env=dict(os.environ,XDG_RUNTIME_DIR=f'/run/user/{p.pw_uid}',DBUS_SESSION_BUS_ADDRESS=f'unix:path=/run/user/{p.pw_uid}/bus')
def call(args,timeout=90):
 q=subprocess.run(args,capture_output=True,text=True,timeout=timeout,env=env)
 assert q.returncode==0,(args,q.returncode,q.stdout,q.stderr)
 return q.stdout.strip()
path=pathlib.Path(p.pw_dir)/'.config/docker/daemon.json'
text=json.dumps({'ipv6':False,'log-driver':'local','log-opts':{'max-size':'10m','max-file':'3'}},sort_keys=True)+'\n'
assert not path.is_symlink()
if path.exists():assert path.read_text()==text
else:
 path.parent.mkdir(mode=0o700,parents=True,exist_ok=True);path.write_text(text);path.chmod(0o600)
result=call(['/usr/bin/dockerd-rootless-setuptool.sh','install'])
endpoint=f'unix:///run/user/{p.pw_uid}/docker.sock'
info=json.loads(call(['docker','-H',endpoint,'info','--format','{{json .}}']))
assert info['CgroupVersion']=='2' and info['CgroupDriver']=='systemd',info
assert 'name=rootless' in info['SecurityOptions'] and info['DockerRootDir'].startswith(p.pw_dir+'/')
print(json.dumps({'user':p.pw_name,'uid':p.pw_uid,'setup':result,'endpoint':endpoint,'version':info['ServerVersion'],'cgroup_driver':info['CgroupDriver'],'cgroup_version':info['CgroupVersion'],'security_options':info['SecurityOptions'],'root_dir':info['DockerRootDir'],'compose':call(['docker','compose','version']),'buildx':call(['docker','buildx','version']),'service':call(['systemctl','--user','is-active','docker.service'])}))
"""

NGINX_PACKAGE = r"""
import os,pathlib,subprocess,json,re
assert os.geteuid()==0
env=dict(os.environ,LC_ALL='C',DEBIAN_FRONTEND='noninteractive',NEEDRESTART_MODE='l')
def call(args,allowed=(0,)):
 p=subprocess.run(args,capture_output=True,text=True,timeout=180,env=env)
 assert p.returncode in allowed,(args,p.returncode,p.stdout,p.stderr)
 return {'rc':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
state=call(['systemctl','is-active','--quiet','nginx.service'],(0,3,4));assert state['rc']!=0
version=re.search(r'Candidate:\s+(\S+)',call(['apt-cache','policy','nginx'])['stdout'])[1]
assert version!='(none)'
sim=call(['apt-get','-s','--no-install-recommends','install','nginx='+version]);assert '0 to remove' in sim['stdout']
call(['systemctl','mask','nginx.service'])
assert os.readlink('/etc/systemd/system/nginx.service')=='/dev/null'
installed=call(['apt-get','-y','--no-install-recommends','-o','Acquire::ForceIPv4=true','-o','Dpkg::Options::=--force-confold','install','nginx='+version])
assert call(['systemctl','is-enabled','nginx.service'],(1,))['stdout'].strip()=='masked'
r={'version':version,'simulation':sim,'installation':installed,'audit':call(['dpkg','--audit'])}
path=pathlib.Path('/root/aurelia-testbase-20261016/nginx-package.json');path.write_text(json.dumps(r,indent=2));path.chmod(0o600)
print(json.dumps(r))
"""

def run_role(role, label, code, data=None):
    with contextlib.redirect_stdout(io.StringIO()) as captured:
        try:
            raw = access.ssh(role, code, data)
        except BaseException:
            print(captured.getvalue(), file=sys.stderr)
            raise
    result = json.loads(raw)
    (operator.CHECKPOINT / (label + '.json')).write_text(json.dumps(result, indent=2, ensure_ascii=True) + '\n', encoding='ascii')
    print(json.dumps(result, ensure_ascii=True), flush=True)
    return result

READINESS = r"""
import os,pathlib,pwd,subprocess,json,sys,time,urllib.request
p=pwd.getpwuid(os.geteuid());assert (p.pw_name,p.pw_uid) in [('aurelia-ops',1000),('rauch-web-test',1001)]
port=18112 if p.pw_uid==1000 else 18113
endpoint=f'unix:///run/user/{p.pw_uid}/docker.sock'
def call(args,timeout=120):
 q=subprocess.run(['docker','-H',endpoint]+args,capture_output=True,text=True,timeout=timeout)
 assert q.returncode==0,(args,q.returncode,q.stdout,q.stderr)
 return q.stdout.strip()
env=dict(os.environ,XDG_RUNTIME_DIR=f'/run/user/{p.pw_uid}',DBUS_SESSION_BUS_ADDRESS=f'unix:path=/run/user/{p.pw_uid}/bus')
q=subprocess.run(['systemctl','--user','enable','docker.service'],capture_output=True,text=True,timeout=20,env=env);assert q.returncode==0,q.stderr
base=pathlib.Path(p.pw_dir)/'testbase';base.mkdir(mode=0o700,exist_ok=True)
script=base/'readiness-unix.py'
socketdir=base/'socket';socketdir.mkdir(mode=0o777,exist_ok=True);socketdir.chmod(0o777)
source='''import http.server,json,pathlib,os,socketserver,socket
path=pathlib.Path('/state/starts');count=int(path.read_text())+1 if path.exists() else 1
path.write_text(str(count))
class Handler(http.server.BaseHTTPRequestHandler):
 def do_GET(self):
  raw=json.dumps({'project':os.environ['PROJECT'],'status':'ready','starts':count}).encode()
  self.send_response(200);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(raw)));self.end_headers();self.wfile.write(raw)
 def log_message(self,*args):pass
class Server(socketserver.UnixStreamServer):pass
sock=pathlib.Path('/socket/backend.sock')
if sock.exists():
 assert sock.is_socket() and not sock.is_symlink();sock.unlink()
server=Server(str(sock),Handler);sock.chmod(0o666);server.serve_forever()
'''
assert not script.is_symlink()
if script.exists():assert script.read_text()==source
else:script.write_text(source);script.chmod(0o644)
imagefile=base/'image.json'
if imagefile.exists():image=json.loads(imagefile.read_text())['digest']
else:
 call(['pull','python:3.12-slim-bookworm'])
 images=json.loads(call(['image','inspect','python:3.12-slim-bookworm']))
 image=images[0]['RepoDigests'][0];assert image.startswith('python@sha256:')
 imagefile.write_text(json.dumps({'digest':image}));imagefile.chmod(0o600)
network='lg2-test-isolated';volume='lg2-readiness-state';name='lg2-readiness-unix'
nets=json.loads(call(['network','ls','--format','{{json .}}']).replace('\n',',').join(['[',']']))
if not any(n['Name']==network for n in nets):call(['network','create','--internal','--label','aurelia.testbase=20261016',network])
net=json.loads(call(['network','inspect',network]))[0]
assert net['Internal'] and not net['EnableIPv6'] and net['Labels'].get('aurelia.testbase')=='20261016'
vols=call(['volume','ls','-q']).splitlines()
if volume not in vols:
 call(['volume','create','--label','aurelia.testbase=20261016',volume])
 call(['run','--rm','--network','none','--user','0:0','--cap-drop','ALL','--cap-add','CHOWN','--security-opt','no-new-privileges','--pids-limit','32','--memory','64m','--cpus','0.25','--mount',f'type=volume,src={volume},dst=/state',image,'chown','65532:65532','/state'])
assert json.loads(call(['volume','inspect',volume]))[0]['Labels'].get('aurelia.testbase')=='20261016'
if 'lg2-readiness' in call(['ps','-a','--format','{{.Names}}']).splitlines():
 old=json.loads(call(['inspect','lg2-readiness']))[0];assert old['Config']['Labels'].get('aurelia.testbase')=='20261016'
 call(['stop','--timeout','5','lg2-readiness']);call(['rm','lg2-readiness'])
if name not in call(['ps','-a','--format','{{.Names}}']).splitlines():
 call(['run','-d','--name',name,'--label','aurelia.testbase=20261016','--restart','unless-stopped','--network',network,'--user','65532:65532','--cap-drop','ALL','--security-opt','no-new-privileges','--read-only','--pids-limit','64','--memory','128m','--memory-swap','128m','--cpus','0.25','--tmpfs','/tmp:rw,noexec,nosuid,size=16m','--sysctl','net.ipv6.conf.all.disable_ipv6=1','--sysctl','net.ipv6.conf.default.disable_ipv6=1','--mount',f'type=volume,src={volume},dst=/state','--mount',f'type=bind,src={socketdir},dst=/socket','--mount',f'type=bind,src={script},dst=/app/readiness.py,readonly','--env','PROJECT='+p.pw_name,image,'python','-u','/app/readiness.py'])
info=json.loads(call(['inspect',name]))[0]
assert info['Config']['Labels'].get('aurelia.testbase')=='20261016'
assert not info['HostConfig']['PortBindings']
assert info['HostConfig']['ReadonlyRootfs'] and info['HostConfig']['Memory']==134217728 and info['HostConfig']['PidsLimit']==64 and info['HostConfig']['NanoCpus']==250000000
nginx=base/'nginx.conf'
conf=f'''worker_processes 1;
pid /run/user/{p.pw_uid}/lg2-preview/nginx.pid;
error_log stderr warn;
events {{ worker_connections 128; }}
http {{
 access_log off;
 client_body_temp_path /run/user/{p.pw_uid}/lg2-preview/client_temp;
 proxy_temp_path /run/user/{p.pw_uid}/lg2-preview/proxy_temp;
 fastcgi_temp_path /run/user/{p.pw_uid}/lg2-preview/fastcgi_temp;
 uwsgi_temp_path /run/user/{p.pw_uid}/lg2-preview/uwsgi_temp;
 scgi_temp_path /run/user/{p.pw_uid}/lg2-preview/scgi_temp;
 map $http_upgrade $connection_upgrade {{ default upgrade; '' close; }}
 upstream backend {{ server unix:{socketdir}/backend.sock; }}
 server {{
  listen 127.0.0.1:{port};
  server_name 127.0.0.1 localhost;
  client_max_body_size 10m;
  location / {{
   proxy_pass http://backend;
   proxy_http_version 1.1;
   proxy_set_header Host $http_host;
   proxy_set_header Upgrade $http_upgrade;
   proxy_set_header Connection $connection_upgrade;
   proxy_read_timeout 300s;
   proxy_buffering off;
  }}
 }}
}}
'''
unit=pathlib.Path(p.pw_dir)/'.config/systemd/user/lg2-preview.service'
unittext=f'''[Unit]
Description=Private project preview via Unix socket
After=docker.service
Requires=docker.service
[Service]
ExecStartPre=/usr/sbin/nginx -t -c {nginx} -p {base}
ExecStart=/usr/sbin/nginx -c {nginx} -p {base} -g "daemon off;"
ExecReload=/usr/sbin/nginx -c {nginx} -p {base} -s reload
RuntimeDirectory=lg2-preview
RuntimeDirectoryMode=0700
Restart=on-failure
RestartSec=3
NoNewPrivileges=yes
UMask=0077
[Install]
WantedBy=default.target
'''
for path,raw in [(nginx,conf),(unit,unittext)]:
 assert not path.is_symlink()
 if path.exists():assert path.read_text()==raw
 else:path.write_text(raw);path.chmod(0o600)
for args in [['systemctl','--user','daemon-reload'],['systemctl','--user','enable','--now','lg2-preview.service']]:
 q=subprocess.run(args,capture_output=True,text=True,timeout=30,env=env);assert q.returncode==0,(q.stdout,q.stderr)
def health():
 for attempt in range(20):
  try:
   with urllib.request.urlopen(f'http://127.0.0.1:{port}/',timeout=2) as r:return json.load(r)
  except OSError:
   if attempt==19:raise
   time.sleep(.25)
before=health();assert before['project']==p.pw_name
call(['restart','--timeout','5',name]);after=health();assert after['starts']==before['starts']+1
probe='''import socket,json,pathlib
s=socket.socket();s.settimeout(2)
rc=s.connect_ex(('1.1.1.1',443));s.close()
assert rc!=0, 'runtime egress unexpectedly allowed'
assert pathlib.Path('/proc/sys/net/ipv6/conf/all/disable_ipv6').read_text().strip()=='1'
print(json.dumps({'external_ipv4_denied':True,'ipv6_disabled':True,'uid':__import__('os').geteuid(),'cgroup':pathlib.Path('/proc/self/cgroup').read_text()}))
'''
probe=json.loads(call(['exec',name,'python','-c',probe]))
print(json.dumps({'user':p.pw_name,'port':port,'image':image,'network_internal':True,'restart_before':before,'restart_after':after,'runtime':probe,'limits':{k:info['HostConfig'][k] for k in ['Memory','MemorySwap','NanoCpus','PidsLimit','ReadonlyRootfs','SecurityOpt','CapDrop','PortBindings']},'pid':info['State']['Pid']}))
"""

PACKAGES = r"""
import os,pathlib,subprocess,json,sys,re,hashlib
assert os.geteuid()==0
action=json.load(sys.stdin)['action']
root=pathlib.Path('/root/aurelia-testbase-20261016');root.mkdir(mode=0o700,exist_ok=True)
assert not root.is_symlink() and root.stat().st_uid==0 and root.stat().st_mode&0o777==0o700
env=dict(os.environ,LC_ALL='C',DEBIAN_FRONTEND='noninteractive',NEEDRESTART_MODE='l')
def call(args,timeout=180,allowed=(0,)):
 p=subprocess.run(args,capture_output=True,text=True,timeout=timeout,env=env)
 assert p.returncode in allowed,(args,p.returncode,p.stdout,p.stderr)
 return {'rc':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
names=['docker-ce','docker-ce-cli','docker-ce-rootless-extras','containerd.io','docker-buildx-plugin','docker-compose-plugin','uidmap','slirp4netns','python3-venv']
pinned=root/'packages.json'
if action=='simulate':
 versions={}
 for name in names:
  text=call(['apt-cache','policy',name])['stdout'];m=re.search(r'Candidate:\s+(\S+)',text)
  assert m and m[1]!='(none)',name
  versions[name]=m[1]
 args=[n+'='+v for n,v in versions.items()]
 sim=call(['apt-get','-s','--no-install-recommends','-o','Acquire::ForceIPv4=true','install']+args)
 assert '0 to remove' in sim['stdout']
 pinned.write_text(json.dumps(versions,sort_keys=True));pinned.chmod(0o600)
 r={'versions':versions,'simulation':sim}
elif action=='install':
 assert pinned.is_file() and not pinned.is_symlink()
 versions=json.loads(pinned.read_text());assert set(versions)==set(names)
 # Rootful service activation is blocked before package post-install scripts run.
 for unit in ['docker.service','docker.socket','containerd.service']:
  state=call(['systemctl','is-active','--quiet',unit],allowed=(0,3,4))
  assert state['rc']!=0,unit+' unexpectedly active'
 masks=call(['systemctl','mask','docker.service','docker.socket','containerd.service'])
 for unit in ['docker.service','docker.socket','containerd.service']:
  assert pathlib.Path('/etc/systemd/system',unit).is_symlink() and os.readlink('/etc/systemd/system/'+unit)=='/dev/null'
 args=[n+'='+v for n,v in versions.items()]
 result=call(['apt-get','-y','--no-install-recommends','-o','Acquire::ForceIPv4=true','-o','Dpkg::Options::=--force-confold','install']+args)
 actual=call(['dpkg-query','-W','-f=${Package} ${Version}\n']+names)
 r={'versions':versions,'masks':masks,'installation':result,'actual':actual,'audit':call(['dpkg','--audit'])}
else: raise ValueError(action)
(root/(action+'.json')).write_text(json.dumps(r,indent=2));(root/(action+'.json')).chmod(0o600)
print(json.dumps(r))
"""


if __name__ == '__main__':
    action, label = sys.argv[1:3]
    if action == 'repository':
        run(label, REPOSITORY)
    elif action in ('simulate', 'install'):
        run(label, PACKAGES, {'action': action})
    elif action == 'bootstrap':
        run(label, BOOTSTRAP)
    elif action == 'nginx-package':
        run(label, NGINX_PACKAGE)
    elif action in ('rootless-ops', 'rootless-website'):
        run_role(action.split('-', 1)[1], label, ROOTLESS)
    elif action in ('readiness-ops', 'readiness-website'):
        run_role(action.split('-', 1)[1], label, READINESS)
    else:
        raise ValueError(action)
