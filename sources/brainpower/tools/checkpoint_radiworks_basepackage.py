"""Verified RadiWorks M1 snapshot; no live mutations or key material."""
from pathlib import Path
from datetime import datetime
import hashlib, json, os, shutil, sqlite3, time, stat
ROOT=Path(__file__).resolve().parents[1]
LIVE=ROOT/'runtime/rw-c23-fixed-release-20261005'
BACKOFF=ROOT/'runtime/rw-entropy-backoff-20261005'
CANDIDATE=ROOT/'runtime/rw-basepackage-20261006'
STAMP=datetime.now().astimezone().strftime('%Y%m%d-%H%M%S')
DEST=Path('F:/Hauptprojekt/Aurelia')/('RadiWorks-Grundpaket-M1-'+STAMP)

def digest(data): return hashlib.sha256(data).hexdigest()
def checked(path,root):
    path=path.absolute()
    if not path.resolve().is_relative_to(root.resolve()): raise RuntimeError('Source escaped declared root')
    for item in [path,*path.parents]:
        if item==root.parent: break
        if item.is_symlink() or bool(getattr(item.lstat(), 'st_file_attributes', 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT): raise RuntimeError('Link/junction source rejected')
    return path

def manifest(root):
    raw=(root/'PRODUCT_MANIFEST.json').read_bytes();m=json.loads(raw)
    for row in m['files']:
        f=checked(root/row['path'],root);b=f.read_bytes()
        if digest(b)!=row['sha256'] or len(b)!=row['bytes']:raise RuntimeError('Product integrity failed: '+row['path'])
    return m,digest(raw)

live,ld=manifest(LIVE);back,bd=manifest(BACKOFF)
changes=[r['path'] for r in back['files'] if r['sha256']!=next(x['sha256'] for x in live['files'] if x['path']==r['path'])]
if changes!=['engine/src/radiworks/entropy.py']:raise RuntimeError('Unexpected backoff delta')
if CANDIDATE.exists() or DEST.exists():raise RuntimeError('Fresh directories required')
if not DEST.resolve().is_relative_to(Path('F:/Hauptprojekt/Aurelia').resolve()):raise RuntimeError('Destination outside named archive root')
if shutil.disk_usage(DEST.parent).free<200_000_000:raise RuntimeError('Insufficient archive space')
DEST.mkdir();CANDIDATE.mkdir()
entries=[];sqlite_receipts=[];captured=[]
def save(data,relative,source,kind):
    target=DEST/relative
    if not target.resolve().is_relative_to(DEST.resolve()):raise RuntimeError('Destination escape')
    target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
    entries.append({'path':relative,'sha256':digest(data),'bytes':len(data),'source':str(source),'kind':kind})
def snapshot(f,root,relative,kind='file'):
    checked(f,root)
    for attempt in range(5):
        start=f.stat();b=f.read_bytes();end=f.stat()
        if (start.st_size,start.st_mtime_ns)==(end.st_size,end.st_mtime_ns) and len(b)==end.st_size:
            if f.suffix=='.json':json.loads(b)
            save(b,relative,f,kind);return
        time.sleep(.05)
    raise RuntimeError('Live document remained changing; snapshot not asserted')
for label,src,m in [('c23-product',LIVE,live),('backoff-product',BACKOFF,back)]:
    for row in m['files']:snapshot(src/row['path'],src,label+'/'+row['path'])
    snapshot(src/'PRODUCT_MANIFEST.json',src,label+'/PRODUCT_MANIFEST.json')
for row in back['files']:
    f=CANDIDATE/row['path'];f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes((BACKOFF/row['path']).read_bytes())
(CANDIDATE/'PRODUCT_MANIFEST.json').write_bytes((BACKOFF/'PRODUCT_MANIFEST.json').read_bytes())
(CANDIDATE/'BASE_PRODUCT_MANIFEST.json').write_bytes((LIVE/'PRODUCT_MANIFEST.json').read_bytes())
for f in (BACKOFF/'engine/tests').rglob('*'):
    if f.is_file() and f.suffix=='.py':
        checked(f,BACKOFF);target=CANDIDATE/f.relative_to(BACKOFF);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(f.read_bytes())
        snapshot(f,BACKOFF,'backoff-tests/'+str(f.relative_to(BACKOFF)).replace('\\','/'))
for port in range(8103,8110):
    f=ROOT/'runtime/rw-c23-rollout-20261005'/f'instance-{port}.json'
    c=json.loads(f.read_bytes())
    if c['port']!=port or Path(c['sourceDir']).resolve()!=LIVE.resolve() or c['manifestDigest']!=ld:raise RuntimeError('Unexpected live binding')
    snapshot(f,ROOT,f'instance-configs/instance-{port}.json')
    home=Path(c['home']);checked(home,ROOT)
    captured.append({'port':port,'startedAt':datetime.now().astimezone().isoformat()})
    for doc in home.rglob('*'):
        if not doc.is_file() or '.release-service-owner' in doc.parts:continue
        rel=doc.relative_to(home).as_posix()
        if doc.suffix in ('.json','.journal') and doc.name not in ('instance.json','service.identity.json'):
            snapshot(doc,home,f'private-homes/{port}/{rel}','per-document-live-snapshot')
        elif doc.suffix=='.sqlite3':
            checked(doc,home);target=DEST/f'private-homes/{port}/{rel}';target.parent.mkdir(parents=True,exist_ok=True)
            with sqlite3.connect(doc.resolve().as_uri()+'?mode=ro',uri=True) as original, sqlite3.connect(target) as copy:
                original.backup(copy);result=copy.execute('PRAGMA integrity_check').fetchone()[0]
            if result!='ok':raise RuntimeError('SQLite snapshot integrity failed')
            entries.append({'path':target.relative_to(DEST).as_posix(),'sha256':digest(target.read_bytes()),'bytes':target.stat().st_size,'source':str(doc),'kind':'sqlite-consistent-backup'})
            sqlite_receipts.append({'port':port,'integrity':'ok'})
    captured[-1]['finishedAt']=datetime.now().astimezone().isoformat()
first=json.loads((ROOT/'runtime/rw-c23-rollout-20261005/instance-8103.json').read_bytes())
for label in ('data','materia'):
    base=Path(first[label]);checked(base,base)
    for f in base.rglob('*'):
        if f.is_file():snapshot(f,base,f'catalogs/{label}/'+f.relative_to(base).as_posix())
for rel in ('tools/radiworks_release_service.py','tools/radiworks_scheduled_launcher.pyw','tools/radiworks_scheduled_host.ps1','tools/radiworks_scheduled_watchdog.ps1','tools/install_radiworks_scheduled_tasks.ps1','tools/checkpoint_radiworks_basepackage.py','docs/superpowers/plans/2026-10-06-radiworks-grundpaket.md','docs/verification/RADIWORKS_MODI_KLIENTENBEZUG_ORIGINALEINSTELLUNGEN_2026-10-06.md'):
    snapshot(ROOT/rel,ROOT,'workspace/'+rel)
receipt={'schema':1,'createdAt':datetime.now().astimezone().isoformat(),'c23Manifest':ld,'backoffManifest':bd,'candidate':str(CANDIDATE),'delta':changes,'files':entries,'sqlite':sqlite_receipts,'homeCaptureWindows':captured,'limitations':['Per-document snapshots, not an atomic cross-home/case/draft transaction.','In-memory active broadcasts, runtime leases/logs and secret key bytes excluded.','Encrypted entropy journals require the retained external recovery key.','No Aurelia integration release or live replacement.']}
(DEST/'MANIFEST.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
for row in entries:
    b=(DEST/row['path']).read_bytes()
    if digest(b)!=row['sha256'] or len(b)!=row['bytes']:raise RuntimeError('Archive read-back failed')
manifest(CANDIDATE);manifest(LIVE)
restore="""# RadiWorks M1 Wiederherstellung

Die Manifest-Prüfsummen aller Dateien vor einer Wiederherstellung erneut vergleichen. C23 war der Live-Stand; backoff-product ist ausschließlich die Entwicklungsbasis mit Entropie-Fehlerpause. Alte Laufzeitdateien nicht in laufende Instanzen kopieren. Für Wiederherstellung erst den genau zugehörigen Host kontrolliert stoppen, Eigentümer/Scope prüfen und aktive Jobs gesondert behandeln; anschließend private-homes/PORT, passende Startkonfiguration, Kataloge und Quellversion zusammen zuordnen. Die festen absoluten Pfade der Konfiguration auf einem anderen PC neu prüfen.

SQLite wurde konsistent über die Backup-API erfasst. JSON/Journale sind einzeln geprüfte Dateistände zu den Zeitfenstern im Manifest. Fall-/Draft-Dateien können dennoch unterschiedliche Transaktionszeitpunkte repräsentieren und benötigen den vorhandenen Recovery-Abgleich; diese Sicherung behauptet keine atomare globale Laufzeitkonsistenz. Aktive Broadcasts im RAM sind nicht vollständig wiederherstellbar. Schlüsselmaterial wurde nicht kopiert; verschlüsselte Journale benötigen den vorhandenen externen Fernet-Schlüssel. Keine bestehenden Sicherungen überschreiben.
"""
(DEST/'RESTORE.md').write_text(restore,encoding='utf-8')
(DEST/'VERIFY.json').write_text(json.dumps({'readback':True,'files':len(entries),'sqlite':sqlite_receipts,'liveProductUnchanged':True},indent=2),encoding='utf-8')
(CANDIDATE/'evidence').mkdir(exist_ok=True)
(CANDIDATE/'evidence/M1_CHECKPOINT.json').write_text(json.dumps({'archive':str(DEST),'verifiedFiles':len(entries),'c23Manifest':ld,'backoffManifest':bd,'delta':changes,'sqliteCount':len(sqlite_receipts)},indent=2),encoding='utf-8')
print(json.dumps({'archive':str(DEST),'verifiedFiles':len(entries),'sqlite':len(sqlite_receipts),'candidate':str(CANDIDATE),'delta':changes}))
