"""Fixed four-file preview transaction with independent, conflict-aware rollback."""
import argparse
import base64
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import re
import socket
import stat
import subprocess
import sys
import uuid

from lg2_ipv4_control import IPv4Controller, TARGET_PATHS, PROTECTED_PATHS, _utc_now, _parse_utc
from lg2_preview_candidates import (ssh_security_config_candidate,
    project_authorized_key_candidate, ufw_before_rules_candidate)

TARGETS = ('/etc/ssh/sshd_config.d/00-aurelia-access.conf','/etc/ufw/before.rules','/home/aurelia-ops/.ssh/authorized_keys','/home/rauch-web-test/.ssh/authorized_keys')
PROOFS = {'admin_login','ops_login','website_login','own_http','cross_denied','reverse_denied','socket_denied','ufw_reload'}

class PreviewError(RuntimeError):
    pass


class PreviewController(IPv4Controller):
    def __init__(self, workdir, runner=None, *, root='/'):
        if not re.fullmatch(r'/root/aurelia-preview-\d{8}T\d{6}Z', str(workdir)):
            raise PreviewError('invalid fixed workdir')
        super().__init__(str(workdir).replace('aurelia-preview-', 'aurelia-ipv4-'), runner, root=root)
        self.workdir = str(workdir)
        self._work = self._physical(self.workdir)
        self.timer_unit = f'aurelia-preview-rollback-{self.stamp}.timer'

    def _run(self, args, *, allowed=(0,), input=None, timeout=30):
        p = self.runner(args, capture_output=True, text=True, timeout=timeout,
                        input=input, env={**os.environ, 'LC_ALL':'C'})
        if p.returncode not in allowed:
            raise PreviewError(f'command failed: {args}: {p.returncode}: {p.stderr}')
        return p

    @contextmanager
    def _parentfd(self, name):
        # Directory descriptors prevent a project-owned .ssh rename from redirecting root writes.
        fd = os.open(self.root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        try:
            for part in Path(name).parts[1:-1]:
                newer = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
                os.close(fd); fd = newer
                st = os.fstat(fd)
                if st.st_mode & 0o022 or (self.root == Path('/') and st.st_uid not in (0,1000,1001)):
                    raise PreviewError('unsafe parent permissions')
            yield fd
        except OSError as exc:
            raise PreviewError('unsafe target path') from exc
        finally:
            os.close(fd)

    def _current(self, name):
        with self._parentfd(name) as parent:
            fd = os.open(Path(name).name, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=parent)
            try:
                st = os.fstat(fd)
                if not stat.S_ISREG(st.st_mode) or st.st_nlink != 1 or st.st_size > 65536:
                    raise PreviewError('unsafe target file')
                expected_uid = 1000 if name==TARGETS[2] else 1001 if name==TARGETS[3] else 0
                if self.root == Path('/') and (st.st_uid != expected_uid or st.st_gid != expected_uid or st.st_mode & 0o022):
                    raise PreviewError('unexpected target owner/mode')
                with os.fdopen(os.dup(fd),'rb') as stream: raw=stream.read(65537)
                again=os.fstat(fd)
                if len(raw)>65536 or (st.st_mtime_ns,st.st_ctime_ns,st.st_size)!=(again.st_mtime_ns,again.st_ctime_ns,again.st_size):
                    raise PreviewError('target changed while reading')
                return {'sha256':hashlib.sha256(raw).hexdigest(),'mode':stat.S_IMODE(st.st_mode),
                        'uid':st.st_uid,'gid':st.st_gid,'data':base64.b64encode(raw).decode()}
            finally: os.close(fd)

    def _replace(self, name, raw, metadata):
        with self._parentfd(name) as parent:
            temporary='.'+Path(name).name+'.preview-'+uuid.uuid4().hex
            fd=os.open(temporary,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600,dir_fd=parent)
            try:
                os.fchown(fd,metadata['uid'],metadata['gid']);os.fchmod(fd,metadata['mode'])
                with os.fdopen(os.dup(fd),'wb') as stream:stream.write(raw);stream.flush();os.fsync(stream.fileno())
            finally:os.close(fd)
            try:
                os.replace(temporary,Path(name).name,src_dir_fd=parent,dst_dir_fd=parent);os.fsync(parent)
            finally:
                try:os.unlink(temporary,dir_fd=parent)
                except FileNotFoundError:pass

    def _protected(self):
        return {n:self._fingerprint(n,managed=False) for n in sorted(set(TARGET_PATHS+PROTECTED_PATHS)-set(TARGETS))}

    def _copy_tools(self):
        result={}
        for name in ['lg2_preview_control.py','lg2_preview_candidates.py','lg2_ipv4_control.py']:
            raw=(Path(__file__).parent/name).read_bytes(); path=self._work/name
            if path.exists() and path.read_bytes()!=raw: raise PreviewError('tool drift')
            self._atomic_path(path,raw,0o600,0,0,managed=False)
            result[name]=hashlib.sha256(raw).hexdigest()
        return result

    def _save(self,journal):
        self._atomic_path(self._work/'preview.json',(json.dumps(journal,sort_keys=True)+'\n').encode(),0o600,0,0,managed=False)

    def _load(self):
        path=self._work/'preview.json'
        st=path.lstat()
        if not stat.S_ISREG(st.st_mode) or st.st_uid!=0 or st.st_mode&0o077 or st.st_size>1048576:raise PreviewError('unsafe journal')
        j=json.loads(path.read_text())
        if j['workdir']!=self.workdir or set(j['before'])!=set(TARGETS) or set(j['after'])!=set(TARGETS):raise PreviewError('journal binding')
        for group in ['before','after']:
            for item in j[group].values():
                if hashlib.sha256(base64.b64decode(item['data'],validate=True)).hexdigest()!=item['sha256']:raise PreviewError('backup hash')
        for name,digest in j['tools'].items():
            if name not in ['lg2_preview_control.py','lg2_preview_candidates.py','lg2_ipv4_control.py'] or hashlib.sha256((self._work/name).read_bytes()).hexdigest()!=digest:raise PreviewError('tool integrity')
        return j

    def _guard(self,j,which):
        if self._protected()!=j['protected']:raise PreviewError('protected drift')
        for n in TARGETS:
            if self._current(n)!=j[which][n]:raise PreviewError('target drift: '+n)

    def _validate(self,j):
        ssh=self._work/'ssh-candidate.conf';ufw=self._work/'ufw-candidate.rules'
        for path,name in [(ssh,TARGETS[0]),(ufw,TARGETS[1])]:
            self._atomic_path(path,base64.b64decode(j['after'][name]['data']),0o600,0,0,managed=False)
        self._run(['/usr/sbin/sshd','-t','-f',str(ssh)])
        self._run(['iptables-restore','--test','--noflush'],input=ufw.read_text())

    def _reload(self, preview):
        self._run(['/usr/sbin/sshd','-t'])
        if preview:
            actual=self._run(['/usr/sbin/sshd','-T']).stdout.splitlines()
            for expected in ['allowtcpforwarding local','allowstreamlocalforwarding no','permitlisten none','permitopen 127.0.0.1:18112 127.0.0.1:18113','passwordauthentication no','kbdinteractiveauthentication no']:
                if expected not in actual:raise PreviewError('effective SSH mismatch: '+expected)
        self._run(['ufw','reload'])
        self._run(['systemctl','reload','ssh.service'])

    def _timer(self):
        return self._run(['systemctl','is-active','--quiet',self.timer_unit],allowed=(0,3,4)).returncode==0

    def prepare(self):
        self._require_root();self._check_identity();self._ensure_workdir()
        with self._locked():
            if (self._work/'preview.json').exists():raise PreviewError('transaction already exists')
            before={n:self._current(n) for n in TARGETS}
            raw=[base64.b64decode(before[n]['data']) for n in TARGETS]
            desired=[ssh_security_config_candidate(raw[0]),ufw_before_rules_candidate(raw[1]),project_authorized_key_candidate(raw[2],18112),project_authorized_key_candidate(raw[3],18113)]
            after={n:{**before[n],'sha256':hashlib.sha256(b).hexdigest(),'data':base64.b64encode(b).decode()} for n,b in zip(TARGETS,desired)}
            j={'workdir':self.workdir,'phase':'prepared','prepared_at':_utc_now(),'before':before,'after':after,'protected':self._protected(),'tools':self._copy_tools()}
            self._validate(j);self._guard(j,'before');self._save(j)
            return self._summary(j)

    def apply(self):
        self._require_root();self._check_identity()
        with self._locked():
            j=self._load()
            if j['phase']!='prepared' or not self._timer():raise PreviewError('prepared state and active rollback timer required')
            self._guard(j,'before');self._validate(j);j['phase']='applying';self._save(j)
            for n in TARGETS:
                if self._current(n)!=j['before'][n]:raise PreviewError('target drift before write')
                self._replace(n,base64.b64decode(j['after'][n]['data']),j['after'][n])
            self._reload(True);self._guard(j,'after');j['phase']='applied';j['applied_at']=_utc_now();self._save(j)
            return self._summary(j)

    def rollback(self):
        self._require_root()
        with self._locked(wait_seconds=90):
            j=self._load()
            if j['phase'] in ['committed','rolled_back']:return self._summary(j)
            if self._protected()!=j['protected']:raise PreviewError('protected drift during rollback')
            conflicts=[]
            for n in TARGETS:
                try:current=self._current(n)
                except (PreviewError,OSError):conflicts.append(n);continue
                if current not in [j['before'][n],j['after'][n]]:conflicts.append(n);continue
                if current!=j['before'][n]:self._replace(n,base64.b64decode(j['before'][n]['data']),j['before'][n])
            # A foreign project-key edit cannot prevent recovery of root-owned network policy.
            if TARGETS[1] not in conflicts:self._run(['ufw','reload'])
            if TARGETS[0] not in conflicts:
                self._run(['/usr/sbin/sshd','-t']);self._run(['systemctl','reload','ssh.service'])
            if conflicts:
                j['phase']='rollback_conflict';j['conflicts']=conflicts;self._save(j)
                raise PreviewError('foreign edits preserved; other targets restored: '+', '.join(conflicts))
            self._guard(j,'before');j['phase']='rolled_back';j['rolled_back_at']=_utc_now();self._save(j)
            return self._summary(j)

    def commit(self,proof):
        self._require_root()
        if not isinstance(proof,dict) or set(proof)!={'workdir','applied_at','checked_at','after_sha256','checks'}:raise PreviewError('bound acceptance proof required')
        checks=proof['checks']
        if not isinstance(checks,dict) or set(checks)!=PROOFS or any(v is not True for v in checks.values()):raise PreviewError('complete explicit acceptance proof required')
        with self._locked():
            j=self._load()
            if j['phase'] not in ['applied','committed']:raise PreviewError('not applied')
            if proof['workdir']!=self.workdir or proof['applied_at']!=j['applied_at'] or proof['after_sha256']!={n:i['sha256'] for n,i in j['after'].items()}:raise PreviewError('acceptance binding mismatch')
            if not _parse_utc(j['applied_at'])<=_parse_utc(proof['checked_at'])<=_parse_utc(_utc_now()):raise PreviewError('acceptance time mismatch')
            self._guard(j,'after');self._reload(True)
            j['phase']='committed';j['proof']=proof;j.setdefault('committed_at',_utc_now());self._save(j)
            self._run(['systemctl','stop',self.timer_unit],allowed=(0,5))
            if self._timer():raise PreviewError('timer still active')
            j['timer_stopped_at']=_utc_now();self._save(j)
            return self._summary(j)

    def _summary(self,j):
        return {'workdir':self.workdir,'phase':j['phase'],'timer_active':self._timer(),
                'files':{n:{k:v for k,v in item.items() if k!='data'} for n,item in j['after'].items()},
                'prepared_at':j['prepared_at'],'applied_at':j.get('applied_at'),'committed_at':j.get('committed_at')}

    def status(self):
        self._require_root()
        with self._locked():return self._summary(self._load())

    def rollback_check(self):
        self._require_root()
        with self._locked():
            j=self._load();self._guard(j,'before');self._validate(j)
            return self._summary(j)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['prepare','apply','rollback','rollback-check','commit','status']);parser.add_argument('workdir')
    args=parser.parse_args();c=PreviewController(args.workdir)
    result=c.commit(json.load(sys.stdin)) if args.action=='commit' else getattr(c,args.action.replace('-','_'))()
    print(json.dumps(result))

if __name__=='__main__':main()
