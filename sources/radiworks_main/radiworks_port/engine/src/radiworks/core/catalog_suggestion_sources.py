"""Read-only bounded catalog evidence, separate from original analysis ordering."""
from __future__ import annotations
import hashlib,json,os,stat
from pathlib import Path
from .rates import RateRepository

MAX_FILES=2048
MAX_FILE_BYTES=2*1024*1024
MAX_TOTAL_BYTES=32*1024*1024
MAX_LINES=250_000
MAX_ENTRIES=4096
MAX_DEPTH=32

class CatalogSearchBoundsError(ValueError): pass
class CatalogSearchDrift(ValueError): pass

def _guard(path: Path, base: Path):
 info=path.lstat()
 if path.is_symlink() or getattr(info,'st_file_attributes',0)&0x400:
  raise CatalogSearchDrift('Katalog enthält einen umgeleiteten Pfad.')
 if not path.resolve().is_relative_to(base):
  raise CatalogSearchDrift('Katalogpfad liegt außerhalb des freigegebenen Verzeichnisses.')
 return info

def _inventory(repo: RateRepository):
 base=repo.data_dir.resolve(strict=True)
 _guard(repo.data_dir,base)
 if not repo.data_dir.is_dir():
  raise CatalogSearchDrift('Katalogverzeichnis ist nicht verfügbar.')
 entries=[];counter=0
 def walk(directory,depth):
  nonlocal counter
  if depth>MAX_DEPTH: raise CatalogSearchBoundsError('Katalogbaum überschreitet die Suchgrenze.')
  with os.scandir(directory) as scan:
   for item in scan:
    counter+=1
    if counter>MAX_ENTRIES: raise CatalogSearchBoundsError('Katalogbaum überschreitet die Suchgrenze.')
    path=Path(item.path);info=_guard(path,base)
    if stat.S_ISDIR(info.st_mode): walk(path,depth+1)
    elif stat.S_ISREG(info.st_mode): entries.append(path)
    else: raise CatalogSearchDrift('Katalog enthält keine reguläre Quelldatei.')
 walk(repo.data_dir,0)
 actual={p.relative_to(repo.data_dir).as_posix():p for p in entries}
 if repo.release:
  expected={v['path'] for v in repo.release.entries}
  if set(actual)!=expected: raise CatalogSearchDrift('Veröffentlichter Katalog ist verändert.')
 selected={}
 for path in entries:
  name=path.name
  if not name.endswith('.txt') or name.startswith('FUNCTION_'): continue
  if name in selected: raise CatalogSearchDrift('Datenbankname kommt mehrfach vor.')
  if len(selected)>=MAX_FILES: raise CatalogSearchBoundsError('Zu viele Datenbanken für die Inhaltsuche.')
  selected[name]=path
 indexed=repo._databases
 if set(selected)!=set(indexed) or any(selected[n].resolve()!=indexed[n].resolve() for n in selected):
  raise CatalogSearchDrift('Kataloginventar hat sich verändert; Datenbankindex erneut laden.')
 return {n:selected[n] for n in sorted(selected)}

def _read(path):
 if path.stat().st_size>MAX_FILE_BYTES: raise CatalogSearchBoundsError('Einzelne Datenbank überschreitet die Inhaltsuche.')
 with path.open('rb') as source:
  data=source.read(MAX_FILE_BYTES+1)
 if len(data)>MAX_FILE_BYTES: raise CatalogSearchBoundsError('Einzelne Datenbank überschreitet die Inhaltsuche.')
 return data

def catalog_snapshot(repo: RateRepository):
 """Double-read equality detects ordinary drift, not hostile filesystem ABA."""
 first=_inventory(repo);documents=[];evidence=[];total=0;lines=0
 # Pinned release integrity includes scripts/FUNCTION files, never partial evidence.
 sources={v['path']:repo.data_dir.joinpath(*v['path'].split('/')) for v in repo.release.entries} if repo.release else first
 selected_paths=set(first.values())
 release_entries={v['path']:v for v in repo.release.entries} if repo.release else {}
 for key,path in sources.items():
  name=path.name
  _guard(path,repo.data_dir.resolve(strict=True))
  data=_read(path);total+=len(data)
  if total>MAX_TOTAL_BYTES: raise CatalogSearchBoundsError('Katalog überschreitet die Inhaltsuche.')
  digest=hashlib.sha256(data).hexdigest()
  relative=path.relative_to(repo.data_dir).as_posix()
  if repo.release:
   entry=release_entries[relative]
   if digest!=entry['sha256'] or len(data)!=entry['bytes']:
    raise CatalogSearchDrift('Veröffentlichte Datenbank ist verändert.')
  if path in selected_paths:
   # Same decoding as the original RateRepository; retain byte hashes and disclose replacements.
   try:
    text=data.decode('utf-8');replaced=False
   except UnicodeError:
    text=data.decode('utf-8',errors='replace');replaced=True
   lines+=len(text.splitlines())
   if lines>MAX_LINES: raise CatalogSearchBoundsError('Zu viele Ratenzeilen für die Inhaltsuche.')
   document={'name':name[:-4],'text':text}
   if replaced: document['encodingReplacement']=True
   documents.append(document)
  evidence.append({'key':key,'name':name,'path':relative,'sha256':digest,'bytes':len(data)})
 second=_inventory(repo)
 if first!=second: raise CatalogSearchDrift('Kataloginventar wurde während der Suche verändert.')
 for entry in evidence:
  path=repo.data_dir.joinpath(*entry['path'].split('/')) if repo.release else second[entry['key']]
  _guard(path,repo.data_dir.resolve(strict=True))
  if hashlib.sha256(_read(path)).hexdigest()!=entry['sha256']:
   raise CatalogSearchDrift('Kataloginhalt wurde während der Suche verändert.')
 binding={'scheme':'catalog-search-files-v1','releaseId':repo.release_id,'files':evidence}
 digest=hashlib.sha256(json.dumps(binding,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
 return documents,digest
