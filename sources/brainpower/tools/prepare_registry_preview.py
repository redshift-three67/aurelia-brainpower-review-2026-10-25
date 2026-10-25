"""Prepare a local test instance from a consistent journal copy, never production writes."""
import json
import sqlite3
import subprocess
from pathlib import Path

root=Path(__file__).resolve().parents[1]
target=root/'artifacts/registry-preview'
target.mkdir(exist_ok=False)
runtime=target/'runtime'; runtime.mkdir()
with sqlite3.connect((root/'runtime/journal.db').as_uri()+'?mode=ro',uri=True) as source:
    with sqlite3.connect(runtime/'journal.db') as backup:
        source.backup(backup)
        assert backup.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
        assert backup.execute("SELECT COUNT(*) FROM jobs WHERE status IN ('queued','running')").fetchone()[0]==0
        for key in ('auto_review','monitor_enabled'):
            backup.execute('INSERT OR REPLACE INTO settings VALUES(?,?)',(key,'false'))
config=json.loads((root/'config.local.json').read_text(encoding='utf-8-sig'))
config.update(port=8788,data_dir=str(runtime))
(target/'config.json').write_text(json.dumps(config,ensure_ascii=False,indent=2),encoding='utf-8')
fixture=target/'demo-project'; (fixture/'project_memories').mkdir(parents=True)
(fixture/'project_memories/note.md').write_text('# Demo\nGoal: test local registry.\n',encoding='utf-8')
for args in (['init','-q'],['add','.'],['-c','user.name=Test','-c','user.email=test@example.invalid','commit','-qm','synthetic fixture']):
    subprocess.run(['git','-C',str(fixture),*args],check=True,capture_output=True)
print(json.dumps({'config':str(target/'config.json'),'fixture':str(fixture)}))
