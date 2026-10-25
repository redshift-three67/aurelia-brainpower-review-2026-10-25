"""Harmless systemd retry checks; no network or application configuration writes."""
import contextlib
import io
import json
import sys

import lg2_ipv4_operator as operator


REMOTE = r"""
import json,os,pathlib,subprocess,sys,time,uuid
d=json.load(sys.stdin)
assert os.geteuid()==0
root=pathlib.Path('/root/aurelia-ipv4-validation-20261016T070215Z/retry-probes')
assert not root.is_symlink()
root.mkdir(mode=0o700,exist_ok=True)
script=root/'probe.py'
script.write_text('''import pathlib,sys,time
p=pathlib.Path(sys.argv[1]); mode=sys.argv[2]
n=int(p.read_text())+1 if p.exists() else 1
p.write_text(str(n))
if mode == "always-fail": sys.exit(42)
if n == 1:
 if mode == "timeout-first": time.sleep(5)
 sys.exit(42)
(p.parent/(p.name+".done")).write_text("ok")
''')
script.chmod(0o600)
results=[]
def call(argv,allowed=(0,),timeout=20):
 r=subprocess.run(argv,capture_output=True,text=True,timeout=timeout)
 assert r.returncode in allowed,(argv,r.returncode,r.stdout,r.stderr)
 return r
for mode in d['modes']:
 assert mode in ('fail-first','timeout-first','always-fail')
 token=uuid.uuid4().hex
 unit='aurelia-ipv4-retry-probe-'+token+'.service'
 state=root/token
 props=[p for p in d['properties'] if not p.startswith(('TimeoutStartSec=','TimeoutStopSec=','RestartSec=','StartLimitIntervalSec='))]
 props+=['TimeoutStartSec=2s','TimeoutStopSec=1s','RestartSec=1s','StartLimitIntervalSec=30s']
 props+=['PrivateNetwork=yes','RestrictAddressFamilies=AF_UNIX','NoNewPrivileges=yes','ProtectSystem=strict','ReadWritePaths='+str(root),'ProtectHome=no','MemoryMax=64M','CPUQuota=25%','TasksMax=16']
 argv=['systemd-run','--no-block','--unit='+unit]+['--property='+p for p in props]+['/usr/bin/python3',str(script),str(state),mode]
 try:
  call(argv)
  readback=call(['systemctl','show',unit,'-p','Type','-p','Restart','-p','RestartUSec','-p','StartLimitIntervalUSec','-p','StartLimitBurst','-p','TimeoutStartUSec','-p','KillMode']).stdout
  deadline=time.monotonic()+16
  while time.monotonic()<deadline:
   r=call(['systemctl','show',unit,'-p','ActiveState','-p','SubState','-p','Result','-p','NRestarts'],allowed=(0,1))
   status=dict(line.split('=',1) for line in r.stdout.splitlines() if '=' in line)
   if (state.parent/(state.name+'.done')).exists() or status.get('Result')=='start-limit-hit': break
   if mode=='always-fail' and status.get('ActiveState')=='failed' and int(status.get('NRestarts','0'))>=3: break
   if 'Restart=on-failure' not in readback and status.get('ActiveState')=='failed': break
   time.sleep(.2)
  attempts=int(state.read_text()) if state.exists() else 0
  done=(state.parent/(state.name+'.done')).exists()
  journal=call(['journalctl','--no-pager','-u',unit,'-n','12','-o','cat']).stdout
  # systemd 255 may retain Result=exit-code when the subsequent start job hits the unit limit.
  limited=status.get('Result')=='start-limit-hit' or 'Start request repeated too quickly' in journal
  expected=(attempts==3 and status.get('ActiveState')=='failed' and limited and not done) if mode=='always-fail' else (attempts==2 and done)
  results.append({'mode':mode,'attempts':attempts,'done':done,'expected_behavior':expected,'readback':readback,'status':status,'journal':journal})
 finally:
  call(['systemctl','stop',unit],allowed=(0,1,5))
  call(['systemctl','reset-failed',unit],allowed=(0,1))
print(json.dumps({'all_expected':all(r['expected_behavior'] for r in results),'results':results}))
"""


if __name__ == '__main__':
    label = sys.argv[1]
    properties = getattr(operator, 'ROLLBACK_SERVICE_PROPERTIES', (
        'Type=oneshot', 'TimeoutStartSec=300s', 'TimeoutStopSec=10s',
        'KillMode=control-group', 'Environment=LC_ALL=C'))
    with contextlib.redirect_stdout(io.StringIO()):
        result = operator.remote(REMOTE, {
            'properties': list(properties),
            'modes': ['fail-first'] if label.endswith('RED') else ['fail-first', 'timeout-first', 'always-fail'],
        }, label)
    print(json.dumps(result, ensure_ascii=True))
