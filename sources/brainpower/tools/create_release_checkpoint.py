"""Explicit local checkpoint of a quiet Workbench; never writes product sources."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sqlite3
import urllib.request


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--name',required=True)
    args=parser.parse_args()
    import re
    if not re.fullmatch(r'[A-Za-z0-9_-]{1,80}',args.name):
        parser.error('Use a simple checkpoint directory name.')
    root=Path(__file__).resolve().parents[1]
    from sys import path
    path.insert(0,str(root))
    from governor_workbench.config import load_config
    cfg=load_config(root/'config.local.json')
    def state():
        with urllib.request.urlopen('http://127.0.0.1:'+str(cfg['port'])+'/api/state',timeout=15) as response:
            data=json.load(response)
        data.pop('csrf_token',None)
        if any(j['status'] in ('queued','running') for j in data['jobs']):
            raise RuntimeError('Active job: checkpoint postponed.')
        if data['settings']['auto_review']:
            raise RuntimeError('Pause automatic reviews before a consistent checkpoint.')
        return data
    before=state()
    target=root/'checkpoints'/args.name
    target.mkdir(parents=True,exist_ok=False)
    files=[]
    for name in ('governor_workbench','tests','scripts','tools','docs','project_memories'):
        for source in (root/name).rglob('*'):
            if source.is_file() and not source.is_symlink() and '__pycache__' not in source.parts:
                files.append(source)
    for name in ('README.md','AGENTS.md','pyproject.toml','config.example.json','config.local.json','runtime-python.json',
                 'WIEDERAUFNAHME.md','Start-Governor.cmd','Stop-Governor.cmd','Install-Governor.cmd'):
        if (root/name).is_file(): files.append(root/name)
    for source in files:
        destination=target/'workbench'/source.relative_to(root)
        destination.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(source,destination)
    destination=target/'workbench/runtime/journal.db'
    destination.parent.mkdir(parents=True,exist_ok=True)
    with sqlite3.connect((Path(cfg['data_dir'])/'journal.db').as_uri()+'?mode=ro',uri=True) as db:
        with sqlite3.connect(destination) as backup:
            db.backup(backup)
            assert backup.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
    # sqlite connection context managers commit but do not close. Close before
    # hashing so transient WAL/SHM files cannot enter the checkpoint manifest.
    backup.close()
    db.close()
    after=state()
    for key in ('evidence_hash','decision_hash','settings'):
        if before[key]!=after[key]: raise RuntimeError('Source state changed during checkpoint; inspect incomplete checkpoint.')
    (target/'state.json').write_text(json.dumps(after,ensure_ascii=False,indent=2),encoding='utf-8')
    manifest={str(p.relative_to(target)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest()
              for p in target.rglob('*') if p.is_file()}
    (target/'MANIFEST.json').write_text(json.dumps({'version':after['version'],'files':manifest,
        'limitations':['No external product repositories or credentials copied.',
                       'Runtime artifact files are not copied; journal retains their original local paths.',
                       'Restore only as a matched program/journal checkpoint with service stopped.']},indent=2),encoding='utf-8')
    print(str(target))


if __name__=='__main__': main()
