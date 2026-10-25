"""Verified source/config/catalog snapshot; does not copy active runtime data."""
from datetime import datetime
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ORIGINS = {
    'Brainpower': ROOT,
    'Radiworks': Path(r'C:\Users\Hubert111\Documents\Radiworks\radiworks_port'),
    'CodexProfile': Path(r'C:\Users\Hubert111\.codex'),
    'ModulTemplates': Path(r'C:\Users\Hubert111\Documents\Modul_Templates'),
}
baseline = ROOT / 'checkpoints/radiworks-route-seven-20261003-212308/MANIFEST.json'
entries = {(item['scope'], item['path']) for item in json.loads(baseline.read_text(encoding='utf-8-sig'))}
for path in (
    'tools/radiworks_scheduled_watchdog.ps1',
    'tools/create_radiworks_continuation_checkpoint.py',
    'docs/verification/RADIWORKS_SIEBEN_INSTANZEN_CHAT_NETZWERK_2026-10-03.md',
    'docs/verification/RADIWORKS_TASKS_F_VERGLEICH_2026-10-03.md',
    'docs/verification/RADIWORKS_EINSTELLUNGEN_AREA_PEGGOTTY_2026-10-02.md',
    'WIEDERAUFNAHME.md',
):
    entries.add(('Brainpower', path))
for name in ('chat_luna.toml', 'chat_astra.toml'):
    entries.add(('CodexProfile', 'agents/' + name))
for name in ('PORT_PLAN.md', 'FESTLEGUNGEN.md', 'QUELLENANALYSE.md'):
    entries.add(('ModulTemplates', 'modules/radiworks/' + name))
catalog = ROOT / 'runtime/radiworks-catalog-releases/e33ea136d8ea448fada7524757385ee4'
for source in catalog.rglob('*'):
    if source.is_file():
        entries.add(('Brainpower', str(source.relative_to(ROOT))))

stamp = datetime.now().astimezone()
destination = ROOT / 'checkpoints' / ('radiworks-continuation-' + stamp.strftime('%Y%m%d-%H%M%S'))
destination.mkdir(exist_ok=False)
manifest = []
for scope, relative in sorted(entries):
    origin = ORIGINS[scope].resolve()
    source = (origin / relative).resolve()
    if not source.is_relative_to(origin) or not source.is_file():
        raise ValueError(f'Invalid source: {scope}/{relative}')
    content = source.read_bytes()
    target = destination / scope / Path(relative)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(content)
    digest = hashlib.sha256(content).hexdigest()
    if hashlib.sha256(target.read_bytes()).hexdigest() != digest:
        raise ValueError(f'Copy mismatch: {scope}/{relative}')
    manifest.append({'scope': scope, 'path': str(Path(relative)), 'sha256': digest, 'bytes': len(content)})
for entry in manifest:
    source = ORIGINS[entry['scope']] / entry['path']
    if hashlib.sha256(source.read_bytes()).hexdigest() != entry['sha256']:
        raise ValueError(f'Source drift: {entry["scope"]}/{entry["path"]}')
(destination / 'MANIFEST.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
status = {
    'createdLocal': stamp.isoformat(), 'kind': 'source-config-catalog-only',
    'files': len(manifest), 'bytes': sum(item['bytes'] for item in manifest),
    'activeRuntimeConsistent': False, 'radiworksPorts': list(range(8103, 8110)),
    'chatLead': 'gpt-6.1-sol/high', 'worker': 'gpt-6-luna/max', 'reviewer': 'gpt-6-astra/medium',
    'excluded': ['active cases/drafts/journals', 'in-memory broadcasts', 'recovery key', 'credentials',
                 'installed Python environment', 'complete Governors/Aurelia product trees'],
    'next': 'isolated session-linked draft/broadcast observation pilot on 8110+',
}
(destination / 'STATUS.json').write_text(json.dumps(status, indent=2), encoding='utf-8')
(destination / 'RESTORE.md').write_text(
    '# Begrenzter Fortsetzungspunkt\n\n'
    'Dieser Punkt sichert RadiWorks-Quelle, den gepinnten Katalog, Chatrollen, ausgewählte '
    'Betriebsskripte, Modulreferenzen und den Restplan. Er ist keine vollständige Projekt- '
    'oder Laufzeitdatensicherung. Aktive Fall-/Draft-/Journaldateien und Broadcast-Queues '
    'sind nicht enthalten; der Recovery-Schlüssel bleibt separat auf E:.\n\n'
    'Bei normaler Fortsetzung nichts zurückkopieren. Bei Wiederherstellung zunächst '
    'MANIFEST.json vollständig prüfen, aktuelle Daten erhalten und betroffene Aufgaben '
    'kontrolliert deaktivieren. Dateien der benannten Bereiche nur gezielt zurückführen; '
    'abweichende spätere Arbeit nicht überschreiben. Profilübernahme schaltet kein aktives '
    'Chatmodell um. Die sieben Aufgaben anschließend mit dem enthaltenen Installer '
    'registrieren. Python-Umgebung separat bereitstellen. Anmeldung/Warmstart und '
    'fehlende Laufzeitdaten separat prüfen.\n', encoding='utf-8')
metadata = {}
for name in ('MANIFEST.json', 'STATUS.json', 'RESTORE.md'):
    metadata[name] = hashlib.sha256((destination / name).read_bytes()).hexdigest()
(destination / 'VERIFY.json').write_text(json.dumps({'allCopiedFilesVerified': True, 'metadata': metadata}, indent=2), encoding='utf-8')
print(json.dumps({'checkpoint': str(destination), **status}))
