"""Bounded file/Git observations and conflict-aware existing memory editing."""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import threading
import time


def now(): return datetime.now(timezone.utc).isoformat(timespec='seconds')
def digest(data): return hashlib.sha256(data).hexdigest()
def fingerprint(value): return digest(json.dumps(value,sort_keys=True,ensure_ascii=False).encode('utf-8'))


class MemoryConflict(ValueError): pass


class Observer:
    def __init__(self, config, stop_event=None):
        self.config = config
        self.stop_event = stop_event
        self.git_cache = {}
        self.commit_cache = {}
        self.lock = threading.RLock()

    def project(self, key):
        for p in self.config['projects']:
            if p['id'] == key: return p
        raise ValueError('Unbekanntes Projekt.')

    def memory_path(self, key, name):
        if not isinstance(name,str) or not re.fullmatch(r'[^/\\:\x00-\x1f]{1,160}\.md',name) or name.startswith('.'):
            raise ValueError('Nur bestehende Markdown-Gedächtnisdateien sind erlaubt.')
        root = Path(self.project(key)['path']).resolve()
        folder = root/'project_memories'
        if folder.is_symlink() or not folder.resolve().is_relative_to(root):
            raise ValueError('Gedächtnisordner verlässt das Projekt.')
        target = folder/name
        if target.is_symlink() or target.resolve().parent != folder.resolve():
            raise ValueError('Dateiverweis außerhalb des Gedächtnisses.')
        if not target.is_file() or target.stat().st_size > 524288:
            raise ValueError('Datei fehlt oder überschreitet 512 KiB.')
        return target

    def read_memory(self, key, name):
        with self.lock:
            raw = self.memory_path(key,name).read_bytes()
            return dict(project=key,name=name,content=raw.decode('utf-8-sig'),sha256=digest(raw))

    def save_memory(self, key, name, content, expected_sha256):
        if not isinstance(content,str) or len(content.encode('utf-8')) > 524288:
            raise ValueError('Gedächtnistext überschreitet 512 KiB.')
        with self.lock:
            target = self.memory_path(key,name)
            raw = target.read_bytes()
            if digest(raw) != expected_sha256: raise MemoryConflict('Extern geändert. Neu laden und Unterschiede prüfen; nichts überschrieben.')
            directory = Path(self.config['data_dir'])/'backups'/key
            directory.mkdir(parents=True,exist_ok=True)
            backup = directory/(str(time.time_ns())+'-'+name)
            backup.write_bytes(raw)
            fd, pending = tempfile.mkstemp(prefix='.governor-',suffix='.tmp',dir=target.parent)
            try:
                with os.fdopen(fd,'wb') as f:
                    f.write(content.encode('utf-8')); f.flush(); os.fsync(f.fileno())
                # A second check closes the normal edit-during-save window.
                if target.read_bytes() != raw: raise MemoryConflict('Während des Speicherns extern geändert; nichts überschrieben.')
                os.replace(pending,target)
            finally:
                if Path(pending).exists(): Path(pending).unlink()
            written = target.read_bytes()
            if written != content.encode('utf-8'): raise OSError('Rückleseprüfung fehlgeschlagen.')
            return dict(sha256=digest(written),backup=str(backup))

    def git(self, root, args):
        if self.stop_event is not None and self.stop_event.is_set():
            return 1, '', 'Beobachtung wird beendet; kein weiterer Git-Aufruf.'
        try:
            # Evidence is bound to original objects; mutable replace refs cannot alter cached commits.
            p=subprocess.run(['git','--no-replace-objects','--no-optional-locks','-C',str(root),*args],capture_output=True,
                             timeout=15,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
            return p.returncode,p.stdout.decode('utf-8',errors='replace'),p.stderr.decode('utf-8',errors='replace')[:500]
        except (OSError,subprocess.TimeoutExpired): return 1,'','Git nicht verfügbar oder Zeitlimit überschritten.'

    def git_state(self, root, force):
        cached = self.git_cache.get(str(root))
        if cached and not force and time.monotonic()-cached[0] < self.config['git_interval']:
            return cached[1]
        top_rc,top,_=self.git(root,['rev-parse','--show-toplevel'])
        if top_rc or Path(top.strip()).resolve()!=root.resolve():
            result=dict(head='',branch='',git_status='',git_observed_at=now(),committed=set(),staged=set(),
                committed_hashes={},staged_hashes={},incomplete=True,
                error='Projektordner ist kein eigener Git-Arbeitsbaum; übergeordnetes Repository wird nicht einbezogen.',
                tracked_diff_hash=fingerprint({'git_root_unverified':True}))
            self.git_cache[str(root)]=(time.monotonic(),result)
            return result
        from .git_status import parse_status
        status_rc,raw_status,error=self.git(root,['status','--porcelain=v2','--branch','--no-renames','--untracked-files=no','-z'])
        metadata=dict(head='',branch='',status='',names=[],staged=set(),conflict=False)
        if not status_rc:
            try:metadata=parse_status(raw_status)
            except ValueError as exc:status_rc=1;error=str(exc)
        head,branch,status=metadata['head'],metadata['branch'],metadata['status']
        names=metadata['names'];staged=metadata['staged']
        # Read the immutable commit reported by status, not a possibly newer HEAD.
        commit_key=(str(root.resolve()),head)
        saved_commit=self.commit_cache.get(commit_key) if not status_rc and head else None
        committed_rc,committed,tree_error=(1,'','Git-HEAD fehlt.')
        if saved_commit is not None:
            committed_rc,committed,tree_error=0,saved_commit['names'],''
        elif not status_rc and head:
            committed_rc,committed,tree_error=self.git(root,['ls-tree','-r','--name-only','-z',head,'--','project_memories'])
        committed_names=[name for name in committed.split('\0') if name]
        # Hash changed tracked file bytes, not just status letters; do not enumerate enormous untracked trees.
        changed=[]; remaining=64*1024*1024
        bad_tree=bool('\ufffd' in committed or (committed and not committed.endswith('\0')))
        incomplete=bool(status_rc or committed_rc or metadata['conflict'] or bad_tree)
        if len(names)>1000: incomplete=True
        for name in names[:1000]:
            if not name: continue
            path = root/name
            try:
                if path.resolve().is_relative_to(root.resolve()) and path.is_file() and path.stat().st_size <= remaining:
                    size=path.stat().st_size; remaining-=size
                    hasher=hashlib.sha256()
                    with path.open('rb') as f:
                        while chunk:=f.read(1024*1024): hasher.update(chunk)
                    changed.append((name,hasher.hexdigest()))
                elif not path.exists(): changed.append((name,'deleted'))
                else: changed.append((name,'unhashed')); incomplete=True
            except OSError: changed.append((name,'unreadable')); incomplete=True
        committed_hashes=dict(saved_commit['hashes']) if saved_commit is not None else {}
        staged_hashes={};commit_ok=not committed_rc and not bad_tree
        if saved_commit is None:
            for name in committed_names[:100]:
                if name.endswith('.md'):
                    code,content,_=self.git(root,['show',head+':'+name])
                    if not code: committed_hashes[name]=digest(content.encode('utf-8'))
                    else: incomplete=True;commit_ok=False
            # Only immutable, fully read commit data is cached; index/worktree never are.
            if commit_ok and head and len(committed_names)<=100:
                if len(self.commit_cache)>=16:self.commit_cache.pop(next(iter(self.commit_cache)))
                self.commit_cache[commit_key]=dict(names=committed,hashes=dict(committed_hashes))
        for name in sorted(staged)[:100]:
            if name.endswith('.md'):
                code,content,_=self.git(root,['show',':'+name])
                if not code: staged_hashes[name]=digest(content.encode('utf-8'))
                else: incomplete=True
        if incomplete: changed.append(('incomplete-observation',True))
        result = dict(head=head,branch=branch,git_status=status[:16000],git_observed_at=now(),
                      committed=set(committed_names),staged=staged,
                      committed_hashes=committed_hashes,staged_hashes=staged_hashes,incomplete=incomplete,
                      error=error if status_rc else tree_error if committed_rc else '',tracked_diff_hash=fingerprint(changed))
        self.git_cache[str(root)] = (time.monotonic(),result)
        return result

    def sources(self):
        result=[]
        gov=self.config.get('governor_dir'); snap=self.config.get('snapshot_dir')
        paths=([Path(gov)/n for n in ['governor_manifest.json','goals.json','RADIWORKS_AURELIA_STEP_01.md',
                'RADI144_STATUS_CHECK_2026-09-11.md','MORPHIC_V1_OPTION_B_SCAN_2026-09-11.md']] if gov else [])
        if snap: paths.append(Path(snap)/'session_state_freeze.json')
        for path in paths:
            try:
                if path.stat().st_size>524288: raise ValueError('Quelle zu groß.')
                raw=path.read_bytes()
                result.append(dict(name=path.name,path=str(path),sha256=digest(raw),content=raw.decode('utf-8-sig')))
            except (OSError,ValueError,UnicodeError):
                result.append(dict(name=path.name,path=str(path),sha256=None,content='',error='Quelle nicht lesbar.'))
        return result

    def scan(self, force_git=False):
        with self.lock:
            sources=self.sources()
            results=[]
            for config in self.config['projects']:
                p=dict(config); p.update(observed_at=now(),warnings=[],memories=[],sources=sources,
                                        evidence_complete=True,status_basis='Konfigurierter Betreiberplan; keine automatisch erteilte Freigabe.')
                p['status']='Dokumentiert: '+p['status']
                p['next_step']='Planungsbasis: '+p['next_step']
                root=Path(p['path'])
                if not root.is_dir():
                    p.update(status='Nicht erreichbar',head='',branch='',git_status='',evidence_complete=False)
                    p['warnings'].append('Projektpfad fehlt oder ist nicht erreichbar.')
                else:
                    git=self.git_state(root,force_git)
                    p['evidence_complete']=not git['incomplete']
                    p.update({k:git[k] for k in ('head','branch','git_status','tracked_diff_hash','git_observed_at')})
                    if git['error']: p['warnings'].append('Git: '+git['error'])
                    if git['incomplete']: p['warnings'].append('Hashbudget überschritten oder Quelle nicht hashbar; Aktualität nicht vollständig beweisbar.')
                    folder=root/'project_memories'
                    if not folder.is_dir(): p['warnings'].append('Kein project_memories-Ordner vorhanden.')
                    else:
                        files=sorted(folder.glob('*.md'))
                        if len(files)>100:
                            p['evidence_complete']=False; p['warnings'].append('Mehr als 100 Gedächtnisdateien; Erfassung begrenzt.')
                        for path in files[:100]:
                            try:
                                data=self.read_memory(p['id'],path.name)
                                rel='project_memories/'+path.name
                                item=dict(name=path.name,sha256=data['sha256'],size=path.stat().st_size,
                                          committed=git['committed_hashes'].get(rel)==data['sha256'],
                                          tracked_in_head=rel in git['committed'],staged=git['staged_hashes'].get(rel)==data['sha256'],
                                          has_staged_changes=rel in git['staged'])
                                p['memories'].append(item)
                                if not item['committed']:
                                    p['warnings'].append(path.name+(': vorgemerkt; aktuelle Bytes nicht im HEAD.' if item['staged'] else ': aktuelle Bytes nicht im HEAD nachgewiesen.'))
                            except (OSError,ValueError,UnicodeError) as e:
                                p['warnings'].append(path.name+': '+str(e)); p['evidence_complete']=False
                    p['warnings'].append('Git erfasst getrackte Änderungen und Gedächtnisdateien; übrige ungetrackte Dateien nicht vollständig geprüft.')
                if any(s.get('error') for s in sources):
                    p['warnings'].append('Governance-Quellen teilweise nicht verfügbar.'); p['evidence_complete']=False
                statuses={}
                normalize=lambda value: re.sub(r'[^a-z0-9]','',value.lower())
                for source in sources:
                    try:
                        if source['name']=='goals.json':
                            for goal in json.loads(source['content']).get('projects',[]):
                                if normalize(goal.get('name',''))==normalize(p['name']): statuses['goals.json']=goal.get('status')
                        elif source['name']=='session_state_freeze.json':
                            for name,status in json.loads(source['content']).get('projects',{}).items():
                                if normalize(name)==normalize(p['name']): statuses['Snapshot']=status
                    except (ValueError,TypeError,AttributeError): p['warnings'].append(source['name']+': Inhalt nicht interpretierbar.')
                p['documented_statuses']=statuses
                if len(set(str(v) for v in statuses.values()))>1:
                    p['warnings'].append('Statusquellen weichen ab: '+'; '.join(k+' = '+str(v) for k,v in statuses.items())+'. Keine automatische Freigabe.')
                p['evidence_hash']=fingerprint({k:p.get(k) for k in ('id','name','path','gate','status','next_step','depends_on','head','git_status','tracked_diff_hash','memories','sources','warnings','evidence_complete')})
                results.append(p)
            return dict(observed_at=now(),projects=results,evidence_hash=fingerprint([p['evidence_hash'] for p in results]),
                        evidence_complete=all(p['evidence_complete'] for p in results))

    def context(self, observation, project_id=None):
        selected=[p for p in observation['projects'] if not project_id or p['id']==project_id]
        if not selected: raise ValueError('Projekt nicht gefunden.')
        result={'observed_at':observation['observed_at'],'evidence_hash':observation['evidence_hash'],
                'scope':'read_only_advisory','approval_granted':False,'projects':[], 'evidence_complete':observation.get('evidence_complete',False),
                'limits':['No product implementation or gate approval is authorized by this review.',
                          'Memory excerpts are partial; absence is not proof. Untracked source trees not fully scanned.']}
        for p in selected:
            row={k:p.get(k) for k in ('id','name','gate','status','next_step','depends_on','head','git_status','evidence_hash','warnings')}
            row['memories']=[]
            for m in p['memories']:
                value=self.read_memory(p['id'],m['name'])
                if value['sha256'] != m['sha256']: raise MemoryConflict('Quelle während der Kontextbildung geändert.')
                lines=value['content'].splitlines()
                excerpt='\n'.join(lines[:35])+'\n[... middle omitted ...]\n'+'\n'.join(lines[-35:]) if len(lines)>75 else value['content']
                row['memories'].append({**m,'excerpt':excerpt[:9000],'truncated':len(lines)>75 or len(excerpt)>9000})
            result['projects'].append(row)
        result['governance_sources']=[{k:s.get(k) for k in ('name','sha256','content','error')} for s in selected[0]['sources']]
        return result
