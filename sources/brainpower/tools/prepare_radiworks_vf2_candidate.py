"""Create verified VF2 working copy without live homes/keys."""
from pathlib import Path
import hashlib, json, shutil
from datetime import datetime, timezone
ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'runtime/rw-gv2-20261004'
TARGET = ROOT / 'runtime/rw-vf2-20261004'
if TARGET.exists():
    raise SystemExit('VF2 target exists; refusing replacement')
manifest = json.loads((SOURCE / 'PRODUCT_MANIFEST.json').read_text(encoding='utf-8'))
for entry in manifest['files']:
    path = (SOURCE / entry['path']).resolve()
    if not path.is_relative_to(SOURCE.resolve()):
        raise SystemExit('Manifest path escaped source')
    if hashlib.sha256(path.read_bytes()).hexdigest() != entry['sha256']:
        raise SystemExit('Source drift: ' + entry['path'])
TARGET.mkdir()
for entry in manifest['files']:
    dest = TARGET / entry['path']
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(SOURCE / entry['path'], dest)
for name in ('PRODUCT_MANIFEST.json', 'REFERENCE_SOURCES.json'):
    shutil.copyfile(SOURCE / name, TARGET / ('PARENT_' + name))
(TARGET / 'BASELINE.json').write_text(json.dumps({
    'createdAt': datetime.now(timezone.utc).isoformat(),
    'source': str(SOURCE), 'files': manifest['files'],
    'liveHomesCopied': False, 'keysCopied': False, 'liveProcessesChanged': False,
}, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'candidate': str(TARGET), 'verifiedCopiedFiles': len(manifest['files'])}))

