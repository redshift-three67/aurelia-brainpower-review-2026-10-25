"""Steering and recorded Linux checks for the fixed LG2 preview change."""
import base64
import hashlib
import json
from pathlib import Path
import sys
import subprocess
import time
import socket
import urllib.request
import re
from datetime import datetime, timezone

import lg2_testbase_operator as host

VALIDATION = '/root/aurelia-preview-validation-20261016T120000Z'
WORKDIR = '/root/aurelia-preview-20261016T123500Z'
TIMER = 'aurelia-preview-rollback-20261016T123500Z'

def tests(label):
    paths = ['tools/server/lg2_ipv4_control.py','tools/server/lg2_preview_control.py','tests/test_lg2_preview_control.py']
    for path in ['tools/server/lg2_preview_candidates.py','tests/test_lg2_preview_candidates.py']:
        if Path(path).is_file(): paths.append(path)
    files = [{'name':n,'data':base64.b64encode(Path(n).read_bytes()).decode(),'sha256':hashlib.sha256(Path(n).read_bytes()).hexdigest()} for n in paths]
    return host.run(label, r'''
import pathlib,json,sys,base64,hashlib,subprocess,os
assert os.geteuid()==0
d=json.load(sys.stdin);base=pathlib.Path(d['root']);base.mkdir(mode=0o700,exist_ok=True)
assert not base.is_symlink() and base.stat().st_uid==0 and base.stat().st_mode&0o777==0o700
for item in d['files']:
 path=base/item['name'];path.parent.mkdir(mode=0o700,parents=True,exist_ok=True)
 raw=base64.b64decode(item['data']);assert hashlib.sha256(raw).hexdigest()==item['sha256']
 assert not path.is_symlink();path.write_bytes(raw);path.chmod(0o600)
p=subprocess.run(['python3','-m','unittest','discover','-s','tests','-p','test_lg2_preview*.py','-v'],cwd=base,capture_output=True,text=True,timeout=90)
print(json.dumps({'rc':p.returncode,'stdout':p.stdout,'stderr':p.stderr,'files':[{'name':i['name'],'sha256':i['sha256']} for i in d['files']]}))
''', {'root':VALIDATION,'files':files})

CONTROL = r'''
import json,sys,subprocess,pathlib,hashlib,os
assert os.geteuid()==0
d=json.load(sys.stdin);action=d['action'];work=d['work'];validation=d['validation']
tool=validation+'/tools/server/lg2_preview_control.py' if action=='prepare' else work+'/lg2_preview_control.py'
for item in d['files']:
 path=pathlib.Path(validation)/item['name']
 assert hashlib.sha256(path.read_bytes()).hexdigest()==item['sha256'],item['name']+' differs'
args=['python3',tool,action,work]
p=subprocess.run(args,input=json.dumps(d.get('proof')),capture_output=True,text=True,timeout=150)
print(json.dumps({'rc':p.returncode,'stdout':p.stdout,'stderr':p.stderr}))
'''

def control(action,label,proof=None):
    names=['tools/server/lg2_ipv4_control.py','tools/server/lg2_preview_control.py','tools/server/lg2_preview_candidates.py']
    files=[{'name':n,'sha256':hashlib.sha256(Path(n).read_bytes()).hexdigest()} for n in names]
    return host.run(label,CONTROL,{'action':action,'work':WORKDIR,'validation':VALIDATION,'files':files,'proof':proof})

UNITS = r'''
import subprocess,sys,json,os
assert os.geteuid()==0
d=json.load(sys.stdin);mode=d['mode'];work=d['work'];timer=d['timer'];tool=work+'/lg2_preview_control.py'
def call(args,timeout=45):
 p=subprocess.run(args,capture_output=True,text=True,timeout=timeout)
 assert p.returncode==0,(args,p.returncode,p.stdout,p.stderr)
 return p.stdout
common=['--property=TimeoutStopSec=10s','--property=KillMode=control-group','--property=Environment=LC_ALL=C']
if mode=='probe':
 out=call(['systemd-run','--unit='+timer+'-probe','--collect','--wait','--pipe','--property=Type=oneshot','--property=TimeoutStartSec=120s']+common+['/usr/bin/python3',tool,'rollback-check',work],150)
 r={'probe':out}
elif mode=='arm':
 out=call(['systemd-run','--unit='+timer,'--on-active=15m','--timer-property=AccuracySec=1s','--property=Type=oneshot','--property=TimeoutStartSec=300s','--property=Restart=on-failure','--property=RestartSec=5s','--property=StartLimitIntervalSec=3600s','--property=StartLimitBurst=3']+common+['/usr/bin/python3',tool,'rollback',work])
 timerstate=call(['systemctl','show',timer+'.timer','-p','ActiveState','-p','NextElapseUSecMonotonic'])
 service=call(['systemctl','show',timer+'.service','-p','ExecStart','-p','Restart','-p','RestartUSec','-p','TimeoutStartUSec','-p','TimeoutStopUSec','-p','StartLimitBurst','-p','StartLimitIntervalUSec','-p','KillMode'])
 assert 'ActiveState=active' in timerstate and 'Restart=on-failure' in service and 'StartLimitBurst=3' in service and 'TimeoutStartUSec=5min' in service
 r={'arm':out,'timer':timerstate,'service':service}
elif mode=='apply':
 out=call(['systemd-run','--unit='+timer+'-apply','--collect','--wait','--pipe','--property=Type=exec','--property=RuntimeMaxSec=120s']+common+['/usr/bin/python3',tool,'apply',work],150)
 r={'apply':out}
else:raise ValueError(mode)
print(json.dumps(r))
'''

def unit(mode,label):return host.run(label,UNITS,{'mode':mode,'work':WORKDIR,'timer':TIMER})

ACCESS = r'''
import os,pwd,json,socket,urllib.request,subprocess,pathlib
p=pwd.getpwuid(os.geteuid());assert p.pw_name in ['aurelia-ops','rauch-web-test']
own=18112 if p.pw_uid==1000 else 18113;other=18113 if own==18112 else 18112
otheruser='rauch-web-test' if p.pw_uid==1000 else 'aurelia-ops';otheruid=1001 if p.pw_uid==1000 else 1000
def tcp(port):
 s=socket.socket();s.settimeout(2);rc=s.connect_ex(('127.0.0.1',port));s.close();return rc
with urllib.request.urlopen(f'http://127.0.0.1:{own}/',timeout=3) as response: health=json.load(response)
assert health['project']==p.pw_name
foreign=tcp(other);assert foreign!=0,'foreign project HTTP access unexpectedly allowed'
denied={}
for path in [f'/home/{otheruser}/testbase/socket/backend.sock',f'/run/user/{otheruid}/docker.sock']:
 s=socket.socket(socket.AF_UNIX);s.settimeout(2)
 try:s.connect(path)
 except PermissionError:denied[path]='permission denied'
 else:raise AssertionError('foreign socket unexpectedly accessible: '+path)
 finally:s.close()
base=['docker','-H',f'unix:///run/user/{p.pw_uid}/docker.sock']
probe='''+repr(r'''import socket,json,pathlib,os
os.environ['RES_OPTIONS']='attempts:1 timeout:1'
results={}
for host,port in [('1.1.1.1',443),('193.142.40.36',22),('127.0.0.1',18112),('127.0.0.1',18113)]:
 s=socket.socket();s.settimeout(1);rc=s.connect_ex((host,port));s.close();assert rc!=0,(host,port);results[host+':'+str(port)]=rc
try:socket.getaddrinfo('example.com',443)
except socket.gaierror:results['external_dns_denied']=True
else:raise AssertionError('external DNS unexpectedly available')
limits={n:pathlib.Path('/sys/fs/cgroup',n).read_text().strip() for n in ['memory.max','cpu.max','pids.max']}
assert limits['memory.max']=='134217728' and limits['pids.max']=='64' and limits['cpu.max']=='25000 100000',limits
results['actual_cgroup_limits']=limits
print(json.dumps(results))
''')+r'''
q=subprocess.run(base+['exec','lg2-readiness-unix','python','-c',probe],capture_output=True,text=True,timeout=20);assert q.returncode==0,(q.stdout,q.stderr)
print(json.dumps({'user':p.pw_name,'uid':p.pw_uid,'own_http':health,'foreign_tcp_rc':foreign,'foreign_sockets':denied,'container':json.loads(q.stdout),'ssh_process_cgroup':pathlib.Path('/proc/self/cgroup').read_text()}))
'''

def access_checks(label):
    return {role:host.run_role(role,label+'-'+role.upper(),ACCESS) for role in ['ops','website']}

def logins(label):
    return {role:host.run_role(role,label+'-'+role.upper(),host.access.acceptance_code(role)) for role in ['admin','ops','website']}

RUNTIME = r'''
import subprocess,json,os,pathlib,re
assert os.geteuid()==0
def call(args):
 p=subprocess.run(args,capture_output=True,text=True,timeout=30);assert p.returncode==0,(args,p.returncode,p.stderr);return p.stdout
r={'rules':call(['iptables-save']),'rules6':call(['ip6tables-save']),'preview_counters':subprocess.run(['iptables','-nvL','AURELIA_PREVIEW'],capture_output=True,text=True).stdout,'listeners':call(['ss','-lntp']),'users':{}}
r['preview_processes']={}
for port,uid in [(18112,1000),(18113,1001)]:
 lines=[line for line in r['listeners'].splitlines() if '127.0.0.1:'+str(port)+' ' in line];assert len(lines)==1
 pids=re.findall(r'pid=(\d+)',lines[0]);assert pids
 for pid in pids:
  status=pathlib.Path('/proc',pid,'status').read_text();actual_uid=re.search(r'^Uid:\s+(\d+)',status,re.M)[1]
  cg=pathlib.Path('/proc',pid,'cgroup').read_text();assert int(actual_uid)==uid and f'/user-{uid}.slice/' in cg
  r['preview_processes'][pid]={'uid':uid,'cgroup':cg}
client=os.environ['SSH_CONNECTION'].split()[0]
for uid,user in [(1000,'aurelia-ops'),(1001,'rauch-web-test')]:
 effective=call(['/usr/sbin/sshd','-T','-C',f'user={user},host=client,addr={client},laddr=193.142.40.36,lport=22'])
 r['users'][user]={'ssh':{line.split(' ',1)[0]:line.split(' ',1)[1] for line in effective.splitlines() if line.split(' ',1)[0] in ['allowtcpforwarding','allowstreamlocalforwarding','permitopen','permitlisten','passwordauthentication','kbdinteractiveauthentication','allowagentforwarding','x11forwarding']},'slice':call(['systemctl','show',f'user-{uid}.slice','-p','MemoryMax','-p','MemoryHigh','-p','CPUQuotaPerSecUSec','-p','TasksMax'])}
assert not call(['ip','-6','address','show']).strip()
r['failed']=call(['systemctl','--failed','--no-legend'])
print(json.dumps(r))
'''

def runtime(label):return host.run(label,RUNTIME)

def tunnel_checks(label):
    clients=json.loads((host.access.CHECKPOINT/'PUBLIC-CLIENTS.json').read_text())['roles']
    def probe(role,local,target,expected=None,reverse=False):
        c=clients[role]
        assert hashlib.sha256(Path(c['profile']).read_bytes()).hexdigest()==c['config_sha256']
        with socket.socket() as check:
            check.bind(('127.0.0.1',local))
        args=['ssh','-4','-F',c['profile'],'-o','ControlMaster=no','-o','ControlPath=none','-o','ControlPersist=no','-o','ClearAllForwardings=no','-o','ExitOnForwardFailure=yes','-o','ConnectTimeout=8','-N','-R' if reverse else '-L',f'127.0.0.1:{local}:{target}',c['alias']]
        p=subprocess.Popen(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        body=None;request_error=None
        try:
            if reverse:
                stdout,stderr=p.communicate(timeout=15)
                assert p.returncode==255 and 'remote port forwarding failed' in stderr,(p.returncode,stderr)
                return {'role':role,'reverse_denied':True,'stderr':stderr}
            for attempt in range(40):
                if p.poll() is not None:raise AssertionError('SSH tunnel exited before local listener')
                try:
                    with socket.create_connection(('127.0.0.1',local),timeout=.2):pass
                    break
                except OSError:
                    if attempt==39:raise
                    time.sleep(.2)
            try:
                with urllib.request.urlopen(f'http://127.0.0.1:{local}/',timeout=4) as response:body=json.load(response)
            except (OSError,ValueError) as exc:request_error=type(exc).__name__
            if expected:assert body and body['project']==expected,(body,request_error)
            else:assert body is None and request_error,(body,request_error)
        finally:
            if p.poll() is None:p.terminate()
            stdout,stderr=p.communicate(timeout=8)
        if not expected:assert 'administratively prohibited' in stderr or 'open failed' in stderr,stderr
        return {'role':role,'target':target,'http':body,'denied':not bool(expected),'request_error':request_error,'stderr':stderr}
    results=[probe('ops',19112,'127.0.0.1:18112','aurelia-ops'),probe('website',19113,'127.0.0.1:18113','rauch-web-test'),
             probe('ops',19114,'127.0.0.1:18113'),probe('website',19115,'127.0.0.1:18112'),
             probe('ops',19116,'127.0.0.1:18112',reverse=True),probe('website',19117,'127.0.0.1:18113',reverse=True),
             probe('ops',19118,'/home/aurelia-ops/testbase/socket/backend.sock'),
             probe('admin',19119,'127.0.0.1:18112'),probe('ops',19120,'example.com:443')]
    for port in [18112,18113]:
        s=socket.socket();s.settimeout(2);rc=s.connect_ex(('193.142.40.36',port));s.close();assert rc!=0
        results.append({'external_port':port,'tcp_rc':rc,'denied':True})
    path=host.operator.CHECKPOINT/(label+'.json');path.write_text(json.dumps(results,indent=2,ensure_ascii=True)+'\n',encoding='ascii')
    print(json.dumps(results,ensure_ascii=True))
    return results

def acceptance(label):
    checkpoint=host.operator.CHECKPOINT
    read=lambda name:json.loads((checkpoint/(name+'.json')).read_text())
    before=read('PREVIEW-RUNTIME-BEFORE');after=read('PREVIEW-RUNTIME-AFTER')
    def canonical(raw,strip_owned=False):
        lines=[]
        for line in raw.splitlines():
            if not line or line.startswith('#'):continue
            if strip_owned and 'AURELIA_PREVIEW' in line:continue
            lines.append(re.sub(r'\[\d+:\d+\]','[COUNTERS]',line))
        return lines
    assert canonical(before['rules'])==canonical(after['rules'],True),'unrelated IPv4 firewall drift'
    ipv6_expected=['-A ufw6-user-limit -j REJECT --reject-with icmp6-port-unreachable','-A ufw6-user-limit-accept -j ACCEPT']
    six_before=canonical(before['rules6']);six_after=canonical(after['rules6'])
    regeneration=[]
    if six_before!=six_after:
        source=read('PREVIEW-IPV6-SOURCE-EXACT')['source_limit_lines']
        diag=read('PREVIEW-IPV6-RELOAD-DIAG')
        assert '-A ufw6-user-limit -j REJECT' in source and '-A ufw6-user-limit-accept -j ACCEPT' in source
        assert diag['chain_references']==[] and diag['ipv6_addresses']=='' and diag['ipv6_routes']==''
        assert all(line not in six_before and line in six_after for line in ipv6_expected)
        assert six_before==[line for line in six_after if line not in ipv6_expected],'unexplained IPv6 firewall drift'
        regeneration=ipv6_expected
    owned=[line for line in after['rules'].splitlines() if 'AURELIA_PREVIEW' in line]
    assert len(owned)==6,owned
    output=[line for line in after['rules'].splitlines() if line.startswith('-A ufw-before-output ')]
    assert 'AURELIA_PREVIEW' in output[0] and '-o lo -j ACCEPT' in output[1]
    counters=[line for line in after['preview_counters'].splitlines() if re.match(r'\s*\d+\s+\d+\s+',line)]
    assert len(counters)==4 and all(int(counters[i].split()[0])>0 for i in [1,2,3]),counters
    for user in ['aurelia-ops','rauch-web-test']:
        s=after['users'][user]['ssh']
        assert s['allowtcpforwarding']=='local' and s['allowstreamlocalforwarding']=='no' and s['permitlisten']=='none' and s['permitopen']=='127.0.0.1:18112 127.0.0.1:18113'
    for role,user in [('ops','aurelia-ops'),('website','rauch-web-test')]:
        a=read('PREVIEW-ACCESS-POST-APPLY-'+role.upper())
        assert a['own_http']['project']==user and a['foreign_tcp_rc']!=0 and len(a['foreign_sockets'])==2 and a['container']['external_dns_denied'] is True
    for role in ['admin','ops','website']:assert read('PREVIEW-POST-APPLY-LOGIN-'+role.upper())['hostname']=='vm2565'
    tunnels=read('PREVIEW-TUNNEL-ACCEPTANCE')
    assert len(tunnels)==11 and tunnels[0]['http']['project']=='aurelia-ops' and tunnels[1]['http']['project']=='rauch-web-test'
    assert all(tunnels[i]['denied'] is True for i in [2,3,6,7,8,9,10]) and all(tunnels[i]['reverse_denied'] is True for i in [4,5])
    state=json.loads(read('PREVIEW-APPLY')['apply']);assert state['workdir']==WORKDIR and state['phase']=='applied'
    proof={'workdir':WORKDIR,'applied_at':state['applied_at'],'checked_at':datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),
           'after_sha256':{n:i['sha256'] for n,i in state['files'].items()},
           'checks':dict.fromkeys(['admin_login','ops_login','website_login','own_http','cross_denied','reverse_denied','socket_denied','ufw_reload'],True)}
    target=checkpoint/(label+'.json');target.write_text(json.dumps(proof,indent=2)+'\n')
    print(json.dumps({'proof_path':str(target),'checks':proof['checks'],'unrelated_ipv4_firewall_unchanged':True,'ipv6_standard_chain_regeneration':regeneration,'owned_rules':owned,'counter_lines':counters}))
    return proof

SNAPSHOT = r'''
import pathlib,json,subprocess,hashlib,os,datetime,stat
assert os.geteuid()==0
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
root=pathlib.Path('/root/aurelia-testbasis-checkpoint-'+stamp);root.mkdir(mode=0o700)
prior=json.loads(pathlib.Path('/root/aurelia-preview-20261016T123500Z/preview.json').read_text());assert prior['phase']=='committed'
paths=set(prior['protected'])|set(prior['after'])
paths.update(['/etc/apt/keyrings/docker.asc','/etc/apt/sources.list.d/docker.sources'])
for uid,user in [(1000,'aurelia-ops'),(1001,'rauch-web-test')]:
 paths.update([f'/etc/systemd/system/user-{uid}.slice.d/50-aurelia-testbudget.conf',f'/etc/systemd/system/user@{uid}.service.d/50-aurelia-delegate.conf'])
 for rel in ['.config/docker/daemon.json','.config/systemd/user/docker.service','.config/systemd/user/lg2-preview.service','testbase/nginx.conf','testbase/readiness-unix.py','testbase/image.json']:
  paths.add('/home/'+user+'/'+rel)
files={}
for name in sorted(paths):
 p=pathlib.Path(name)
 if not p.exists():continue
 st=p.lstat();assert stat.S_ISREG(st.st_mode) and st.st_nlink==1,name
 raw=p.read_bytes();target=root/(hashlib.sha256(name.encode()).hexdigest()+'.bin');target.write_bytes(raw);target.chmod(0o600)
 digest=hashlib.sha256(raw).hexdigest();assert hashlib.sha256(target.read_bytes()).hexdigest()==digest
 files[name]={'sha256':digest,'uid':st.st_uid,'gid':st.st_gid,'mode':stat.S_IMODE(st.st_mode),'bytes':len(raw),'backup':target.name}
states={}
for unit in ['docker.service','docker.socket','containerd.service','nginx.service']:
 assert os.readlink('/etc/systemd/system/'+unit)=='/dev/null'
 states[unit]='masked'
for unit in ['ssh.service','ssh.socket','fail2ban.service','chrony.service','user@1000.service','user@1001.service']:
 p=subprocess.run(['systemctl','is-active',unit],capture_output=True,text=True);assert p.returncode==0 and p.stdout.strip()=='active';states[unit]='active'
failed=subprocess.check_output(['systemctl','--failed','--no-legend'],text=True);assert not failed.strip(),failed
timer=subprocess.run(['systemctl','is-active','--quiet','aurelia-preview-rollback-20261016T123500Z.timer']);assert timer.returncode in [3,4]
manifest={'created_utc':stamp,'files':files,'units':states,'preview_phase':prior['phase'],'rollback_timer_inactive':True,'scope':'configuration and public authorized keys only; no private keys, full image, reboot or off-host restore proof'}
path=root/'manifest.json';path.write_text(json.dumps(manifest,indent=2));path.chmod(0o600)
print(json.dumps({'root':str(root),'manifest_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'file_count':len(files),'units':states,'timer_inactive':True,'files':files}))
'''

if __name__ == '__main__':
    action,label=sys.argv[1:3]
    if action=='tests':tests(label)
    elif action in ('prepare','status','rollback','rollback-check'):control(action,label)
    elif action in ('probe','arm','apply'):unit(action,label)
    elif action=='commit':control(action,label,json.loads(Path(sys.argv[3]).read_text()))
    elif action=='access':access_checks(label)
    elif action=='tunnels':tunnel_checks(label)
    elif action=='runtime':runtime(label)
    elif action=='logins':logins(label)
    elif action=='acceptance':acceptance(label)
    elif action=='snapshot':host.run(label,SNAPSHOT)
    else:raise ValueError(action)
