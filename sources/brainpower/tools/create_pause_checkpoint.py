"""One-off local pause checkpoint; does not change Governor state."""
import hashlib
import json
import sqlite3
import urllib.request
import zipfile
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'checkpoints/2026-09-12_PAUSE_ABCD'

def digest(data):
    return hashlib.sha256(data).hexdigest()

def state():
    with urllib.request.urlopen('http://127.0.0.1:8787/api/state', timeout=15) as response:
        result = json.load(response)
    result.pop('csrf_token', None)
    assert result['settings']['auto_review'] is False, 'Pause required'
    assert not any(j.get('status') in ('queued', 'running') for j in result['jobs']), 'Active jobs'
    return result

def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')

before = state()
DEST.mkdir(parents=True, exist_ok=False)
origins = {}

def copy_file(source, relative, expected=None):
    assert source.is_file() and not source.is_symlink(), source
    data = source.read_bytes()
    if expected:
        assert digest(data) == expected, f'Source changed: {source}'
    target = DEST / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    origins[relative.as_posix()] = str(source)

def copy_tree(source, relative):
    if not source.exists():
        return
    for item in source.iterdir():
        if item.is_symlink() or (hasattr(item, 'is_junction') and item.is_junction()):
            continue
        if item.name in ('__pycache__', '.git', 'node_modules') or item.suffix == '.pyc':
            continue
        if item.is_dir():
            copy_tree(item, relative / item.name)
        elif item.is_file():
            copy_file(item, relative / item.name)

for name in ('governor_workbench', 'tests', 'scripts', 'tools', 'docs', 'project_memories'):
    copy_tree(ROOT / name, Path('workbench') / name)
for name in ('README.md', 'AGENTS.md', 'pyproject.toml', 'config.example.json', 'config.local.json', 'runtime-python.json', '.gitignore', 'Install-Governor.cmd', 'Start-Governor.cmd', 'Stop-Governor.cmd', 'WIEDERAUFNAHME.md'):
    if (ROOT / name).exists():
        copy_file(ROOT / name, Path('workbench') / name)
copy_tree(ROOT / 'runtime/runs', Path('workbench/runtime/runs'))
for item in (ROOT / 'runtime/live').glob('**/*.png'):
    if item.name == 'screenshot.png' or item.name.startswith('capture'):
        copy_file(item, Path('workbench') / item.relative_to(ROOT))
for pattern in ('unit-tests*.txt', 'real-comparison-final*.json', 'live-api-capture.json', 'idle-v02.json', 'ui-v02*.png'):
    for item in (ROOT / 'artifacts').glob(pattern):
        copy_file(item, Path('workbench/artifacts') / item.name)

db_target = DEST / 'workbench/runtime/journal.db'
db_target.parent.mkdir(parents=True, exist_ok=True)
with sqlite3.connect((ROOT / 'runtime/journal.db').as_uri() + '?mode=ro', uri=True) as source:
    with sqlite3.connect(db_target) as target:
        source.backup(target)
        assert target.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
        assert target.execute("SELECT COUNT(*) FROM jobs WHERE status IN ('queued','running')").fetchone()[0] == 0

seen = set()
for project in before['projects']:
    for memory in project.get('memories', []):
        source = Path(project['path']) / 'project_memories' / memory['name']
        copy_file(source, Path('external-evidence') / project['id'] / 'project_memories' / memory['name'], memory['sha256'])
    for item in project.get('sources', []):
        if item['path'] in seen:
            continue
        seen.add(item['path'])
        copy_file(Path(item['path']), Path('external-evidence/sources') / f'{len(seen):02d}_{Path(item["path"]).name}', item['sha256'])

after = state()
for key in ('evidence_hash', 'decision_hash', 'settings'):
    assert before[key] == after[key], f'State changed: {key}'
assert [(j['id'], j['status']) for j in before['jobs']] == [(j['id'], j['status']) for j in after['jobs']]
write_json(DEST / 'state.json', after)
(DEST / 'RESTORE.md').write_text('''# Wiederaufnahme und gezielte Wiederherstellung

Zur normalen Fortsetzung `workbench/WIEDERAUFNAHME.md` lesen. Nichts zurückkopieren, solange die aktuellen Arbeitsdateien vorhanden sind. Abweichungen zuerst prüfen.

Bei tatsächlichem Datenverlust: Governor mit Stop-Governor.cmd beenden; den noch vorhandenen Arbeitsstand gesondert bewahren. Erst dann den Inhalt von workbench/ in ein frisches Arbeitsverzeichnis übernehmen. Konfiguration, Projektpfade, Python-Laufzeit und externe Installationen prüfen. journal.db ist eine konsistente SQLite-Online-Sicherung; alte WAL-/SHM-Dateien gehören nicht dazu. Bei geändertem Installationspfad die Windows-Anmeldeaufgabe anhand der Einrichtungsdokumentation neu einrichten. Automatische Reviews bleiben ausgeschaltet, bis die Wiederaufnahme besprochen wurde.

manifest.json enthält SHA-256 und Länge jeder gesicherten Datei. Die ZIP-Prüfsumme steht neben dem Archiv. state.json enthält den beobachteten Zustand ohne CSRF-Token. external-evidence/ enthält ausgewählte Quellen zum Abgleich, keine vollständig wiederherstellbaren Produktrepositories. Diese Quellen niemals ungeprüft in Projekte zurückkopieren.

Dies ist eine lokale Workbench-Sicherung mit Projektinformationen und lokaler Konfiguration, kein öffentliches Installationspaket. Nicht enthalten: vollständige fünf Produktrepositories, Git-Historien/WIP-Backups, Linux-Server, Hermes-/CC-Switch-Installation, Anmeldedaten, Browserprofile und virtuelle Python-Umgebungen. Die ursprünglichen externen Installationen und Zugangsdaten werden weiter benötigt.
''', encoding='utf-8')
files = {}
for item in sorted(DEST.rglob('*')):
    if item.is_file():
        data = item.read_bytes()
        relative = item.relative_to(DEST).as_posix()
        files[relative] = {'sha256': digest(data), 'bytes': len(data), 'original': origins.get(relative)}
write_json(DEST / 'manifest.json', {'created_at': datetime.now().astimezone().isoformat(), 'scope': 'Local workbench, consistent journal, runs, selected source evidence; not full product backups', 'evidence_hash': after['evidence_hash'], 'decision_hash': after['decision_hash'], 'files': files})
archive = DEST.with_suffix('.zip')
assert not archive.exists()
with zipfile.ZipFile(archive, 'x', zipfile.ZIP_DEFLATED) as output:
    for item in sorted(DEST.rglob('*')):
        if item.is_file():
            output.write(item, item.relative_to(DEST).as_posix())
with zipfile.ZipFile(archive) as check:
    assert check.testzip() is None
    for relative, entry in files.items():
        assert digest(check.read(relative)) == entry['sha256']
        assert digest((DEST / relative).read_bytes()) == entry['sha256']
archive_hash = digest(archive.read_bytes())
archive.with_suffix('.zip.sha256').write_text(f'{archive_hash}  {archive.name}\n', encoding='ascii')
state()
print(json.dumps({'checkpoint': str(DEST), 'archive': str(archive), 'files_verified': len(files), 'zip_sha256': archive_hash, 'sqlite_integrity': 'ok', 'auto_review': False}, indent=2))
