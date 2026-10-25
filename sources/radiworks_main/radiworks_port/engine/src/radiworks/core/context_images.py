
"""Bounded normalized PNG storage; no original filenames or embedded metadata."""
from __future__ import annotations
import hashlib, json, os, re, struct, tempfile, zlib
from pathlib import Path
from ..scope import ScopeContext

MAX_IMAGE_BYTES = 5_000_000
MAX_UPLOAD_BODY = 6_666_800
PNG_SIGNATURE = b'\x89PNG\r\n\x1a\n'
class ContextImageError(ValueError):
    pass

def validate_png(data: bytes) -> dict:
    if not 0 < len(data) <= MAX_IMAGE_BYTES or not data.startswith(PNG_SIGNATURE):
        raise ContextImageError("Bitte ein gültiges, aufbereitetes PNG-Fokusbild wählen.")
    pos, kinds, compressed, width, height, channels = 8, [], [], 0, 0, 0
    while pos < len(data):
        if pos+12 > len(data):
            raise ContextImageError("Das Fokusbild ist unvollständig.")
        length = int.from_bytes(data[pos:pos+4], 'big')
        end = pos+12+length
        if end > len(data):
            raise ContextImageError("Das Fokusbild ist unvollständig.")
        kind = data[pos+4:pos+8]
        value = data[pos+8:pos+8+length]
        crc = int.from_bytes(data[pos+8+length:end], 'big')
        if zlib.crc32(kind+value)&0xffffffff != crc:
            raise ContextImageError("Die Prüfsumme des Fokusbilds ist ungültig.")
        if kind == b'IHDR' and not kinds and length==13:
            width,height,depth,color,compression,filtering,interlace=struct.unpack('>IIBBBBB',value)
            if not (1<=width<=1024 and 1<=height<=1024 and depth==8 and color in (2,6)
                    and compression==0 and filtering==0 and interlace==0):
                raise ContextImageError("Das Fokusbild benötigt ein begrenztes RGB/RGBA-PNG.")
            channels=3 if color==2 else 4
        elif kind == b'IDAT' and kinds and kinds[-1] in (b'IHDR',b'IDAT'):
            compressed.append(value)
        elif kind == b'IEND' and compressed and length==0 and end==len(data):
            kinds.append(kind); pos=end; break
        else:
            raise ContextImageError("Animationen und eingebettete Bildmetadaten sind nicht zulässig.")
        kinds.append(kind); pos=end
    if not kinds or kinds[-1]!=b'IEND':
        raise ContextImageError("Das Fokusbild ist unvollständig.")
    expected=height*(1+width*channels)
    try:
        decoder=zlib.decompressobj()
        raster=decoder.decompress(b''.join(compressed),expected+1)
    except zlib.error as exc:
        raise ContextImageError("Die Bilddaten des Fokusbilds sind ungültig.") from exc
    if (len(raster)!=expected or not decoder.eof or decoder.unconsumed_tail or decoder.unused_data
            or any(raster[offset]>4 for offset in range(0,expected,1+width*channels))):
        raise ContextImageError("Die Bilddaten überschreiten die zulässige Rasterstruktur.")
    return {'sha256':hashlib.sha256(data).hexdigest(),'mediaType':'image/png','byteLength':len(data)}

class ContextImageStore:
    def __init__(self, cases_dir: Path, scope: ScopeContext, *, namespace: str = "context-images"):
        if namespace not in ("context-images", "presentation-images"):
            raise ContextImageError("Ungültiger Bildspeicherbereich.")
        self.base=Path(cases_dir).resolve()
        self.namespace=namespace
        self.scope_hash=hashlib.sha256(json.dumps(scope.to_dict(),sort_keys=True,separators=(',',':')).encode()).hexdigest()

    def _directory(self, create: bool) -> Path:
        directory=self.base/self.namespace/self.scope_hash
        for p in (self.base/self.namespace,directory):
            if p.is_symlink() or (hasattr(p,'is_junction') and p.is_junction()):
                raise ContextImageError("Die lokale Bildablage ist nicht sicher erreichbar.")
        if not directory.resolve().is_relative_to(self.base):
            raise ContextImageError("Die lokale Bildablage ist nicht sicher erreichbar.")
        if create:
            directory.mkdir(parents=True,exist_ok=True)
        return directory

    def _path(self, sha: str, create=False) -> Path:
        if not isinstance(sha,str) or not re.fullmatch('[0-9a-f]{64}',sha):
            raise ContextImageError("Ungültiger Fokusbild-Verweis.")
        path=self._directory(create)/(sha+'.png')
        if path.is_symlink() or not path.resolve().is_relative_to(self.base):
            raise ContextImageError("Die lokale Bildablage ist nicht sicher erreichbar.")
        return path

    def put(self, data: bytes) -> dict:
        metadata=validate_png(data)
        path=self._path(metadata['sha256'],True)
        if path.exists():
            if self.get(metadata['sha256'])!=data:
                raise ContextImageError("Die gespeicherte Bildreferenz ist widersprüchlich.")
            return metadata
        temporary=None
        try:
            with tempfile.NamedTemporaryFile(dir=path.parent,prefix='.focus-',suffix='.tmp',delete=False) as out:
                temporary=Path(out.name)
                out.write(data); out.flush(); os.fsync(out.fileno())
            os.replace(temporary,path)
            temporary=None
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)
        return metadata

    def get(self, sha: str) -> bytes:
        path=self._path(sha)
        with path.open('rb') as source:
            data=source.read(MAX_IMAGE_BYTES+1)
        if validate_png(data)['sha256']!=sha:
            raise ContextImageError("Die gespeicherte Bildreferenz ist widersprüchlich.")
        return data


