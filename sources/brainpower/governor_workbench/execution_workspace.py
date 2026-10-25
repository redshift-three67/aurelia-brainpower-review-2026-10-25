"""Sealed, inspectable patch proposals in fresh directories; never an executor.

The caller must persist manifest_hash independently in its trusted journal. Path
checks are defense in depth, not an OS sandbox against hostile concurrent changes.
Original project files are read only; no apply-back or test execution exists here.
"""
import difflib
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import uuid

from .plans import _path

MAX_FILE_BYTES = 256 * 1024
MAX_TOTAL_BYTES = 1024 * 1024
MAX_MANIFEST_BYTES = 8 * 1024 * 1024


def _sha(data):
    return hashlib.sha256(data).hexdigest()


def _reparse(info):
    return stat.S_ISLNK(info.st_mode) or bool(
        getattr(info, 'st_file_attributes', 0) & getattr(stat, 'FILE_ATTRIBUTE_REPARSE_POINT', 0x400))


def _components(path):
    cursor = Path(path.anchor)
    for component in path.parts[1:]:
        cursor /= component
        try:
            info = cursor.lstat()
        except FileNotFoundError:
            continue
        if _reparse(info):
            raise ValueError('Pfad enthält eine symbolische Verknüpfung oder Junction.')


def _root(value):
    try:
        root = Path(value)
        if not root.is_absolute():
            raise ValueError('Projektwurzel muss absolut und kanonisch sein.')
        _components(root)
        if not root.is_dir() or os.path.normcase(str(root.resolve(strict=True))) != os.path.normcase(str(root)):
            raise ValueError('Projektwurzel fehlt oder hat ihre kanonische Identität geändert.')
        info = root.stat()
        return root, dict(device=info.st_dev, inode=info.st_ino)
    except (OSError, TypeError, RuntimeError) as exc:
        raise ValueError('Projektwurzel kann nicht sicher geprüft werden.') from exc


def _read(root, relative, limit=MAX_FILE_BYTES):
    _path(relative)
    target = root / relative
    try:
        _components(target)
        try:
            before = target.lstat()
        except FileNotFoundError:
            return None
        if not stat.S_ISREG(before.st_mode) or before.st_nlink > 1:
            raise ValueError('Nur reguläre Dateien ohne Hardlinks sind zulässig.')
        with target.open('rb') as stream:
            data = stream.read(limit + 1)
        after = target.lstat()
        _components(target)
        if (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) != (
                after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns):
            raise ValueError('Datei hat sich während des Lesens geändert.')
        if len(data) > limit:
            raise ValueError('Datei überschreitet das zulässige Bytebudget.')
        data.decode('utf-8')
        return data
    except (OSError, UnicodeError, RuntimeError) as exc:
        raise ValueError('Datei fehlt, ist umgeleitet oder enthält keinen lesbaren UTF-8-Text.') from exc


def _diff(path, before, after):
    # Diff text is for inspection; exact hashes remain authoritative.
    lines = difflib.unified_diff((before or b'').decode('utf-8').splitlines(keepends=True),
        after.decode('utf-8').splitlines(keepends=True),
        fromfile='a/'+path if before is not None else '/dev/null', tofile='b/'+path)
    return ''.join(line if line.endswith('\n') else line+'\n\\ No newline at end of file\n' for line in lines)


class WorkspaceStager:
    def __init__(self, data_dir):
        self.base = (Path(data_dir).resolve() / 'execution-staging')

    def _storage(self):
        _components(self.base)
        if self.base.resolve() != self.base:
            raise ValueError('Staging-Verzeichnis wurde umgeleitet.')

    def stage(self, project_root, allowed_paths, patches, expected_hashes):
        root, identity = _root(project_root)
        self._storage()
        if self.base == root or self.base.is_relative_to(root) or root.is_relative_to(self.base):
            raise ValueError('Staging und Originalprojekt müssen getrennte Verzeichnisse sein.')
        if not isinstance(allowed_paths, list) or not 1 <= len(allowed_paths) <= 20:
            raise ValueError('Genau begrenzter Umfang mit 1 bis 20 Dateien erforderlich.')
        allowed = [_path(path) for path in allowed_paths]
        if len({os.path.normcase(path) for path in allowed}) != len(allowed):
            raise ValueError('Doppelte oder aliasierte Umfangspfade.')
        if not isinstance(expected_hashes, dict) or set(expected_hashes) != set(allowed):
            raise ValueError('Expliziter erwarteter Hash für jede Umfangsdatei erforderlich.')
        if not isinstance(patches, list) or not 1 <= len(patches) <= 20:
            raise ValueError('Ein Vorschlag benötigt 1 bis 20 Dateiänderungen.')
        replacements = {}
        for patch in patches:
            if not isinstance(patch, dict) or set(patch) != {'path', 'content'}:
                raise ValueError('Dateiänderungen dürfen nur path und content enthalten.')
            path = _path(patch['path'])
            if path not in allowed or path in replacements or not isinstance(patch['content'], str):
                raise ValueError('Doppelter oder nicht erlaubter Änderungspfad oder ungültiger Inhalt.')
            try:
                data = patch['content'].encode('utf-8')
            except UnicodeError as exc:
                raise ValueError('Änderungsinhalt ist kein gültiger UTF-8-Text.') from exc
            if len(data) > MAX_FILE_BYTES:
                raise ValueError('Dateiänderung überschreitet 256 KiB.')
            replacements[path] = data
        if sum(map(len, replacements.values())) > MAX_TOTAL_BYTES:
            raise ValueError('Dateiänderungen überschreiten zusammen 1 MiB.')
        originals = {}
        for path in allowed:
            expected = expected_hashes[path]
            if expected is not None and (not isinstance(expected, str) or not re.fullmatch('[a-f0-9]{64}', expected)):
                raise ValueError('Erwarteter Hash muss SHA-256 sein; None bedeutet explizit nicht vorhanden.')
            data = _read(root, path)
            if (None if data is None else _sha(data)) != expected:
                raise ValueError('Originalquelle weicht vom erwarteten Hash ab.')
            if data is None and path not in replacements:
                raise ValueError('Fehlende Umfangsdatei benötigt einen expliziten Erstellungsvorschlag.')
            originals[path] = data
        if sum(len(data or b'') for data in originals.values()) > MAX_TOTAL_BYTES:
            raise ValueError('Originalquellen überschreiten zusammen 1 MiB.')
        final = {path: replacements.get(path, originals[path]) for path in allowed}
        if sum(map(len, final.values())) > MAX_TOTAL_BYTES:
            raise ValueError('Staging-Dateien überschreiten zusammen 1 MiB.')
        stage_id = uuid.uuid4().hex
        location = self.base / stage_id
        self.base.mkdir(parents=True, exist_ok=True)
        self._storage()
        location.mkdir()  # Fresh UUID, exclusive directory; never reuse prior work.
        files_root = location/'files'
        files_root.mkdir()
        records = []
        for path in allowed:
            target = files_root/path
            target.parent.mkdir(parents=True, exist_ok=True)
            _components(target)
            with target.open('xb') as stream:
                stream.write(final[path])
                stream.flush()
                os.fsync(stream.fileno())
            records.append(dict(path=path, original_sha256=expected_hashes[path],
                                staged_sha256=_sha(final[path]), staged_bytes=len(final[path]),
                                diff=_diff(path, originals[path], final[path])))
        # Check every original again before publishing a sealed, reviewable stage.
        if _root(root)[1] != identity:
            raise ValueError('Originalwurzel hat sich während des Stagings geändert.')
        for path in allowed:
            current = _read(root, path)
            if (None if current is None else _sha(current)) != expected_hashes[path]:
                raise ValueError('Originalquelle hat sich während des Stagings geändert.')
        manifest = dict(version=1, id=stage_id, original_root=str(root), root_identity=identity,
                        files=records, execution_enabled=False, apply_back_enabled=False)
        encoded = json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2).encode('utf-8')
        if len(encoded) > MAX_MANIFEST_BYTES:
            raise ValueError('Staging-Manifest überschreitet das Bytebudget.')
        manifest_path = location/'manifest.json'
        with manifest_path.open('xb') as stream:
            stream.write(encoded)
            stream.flush()
            os.fsync(stream.fileno())
        seal = _sha(encoded)
        self.verify_source(stage_id, seal)
        return dict(id=stage_id, path=str(location), manifest_path=str(manifest_path),
                    manifest_hash=seal, manifest=manifest)

    def verify_source(self, stage_id, expected_manifest_hash):
        return self._verify(stage_id, expected_manifest_hash, applied=False)

    def verify_applied(self, stage_id, expected_manifest_hash):
        """Observe target bytes against the sealed stage; does not run tests."""
        return self._verify(stage_id, expected_manifest_hash, applied=True)

    def _verify(self, stage_id, expected_manifest_hash, *, applied):
        if not isinstance(stage_id, str) or not re.fullmatch('[a-f0-9]{32}', stage_id):
            raise ValueError('Ungültige Staging-ID.')
        if not isinstance(expected_manifest_hash, str) or not re.fullmatch('[a-f0-9]{64}', expected_manifest_hash):
            raise ValueError('Unabhängig gespeicherter Manifest-Hash erforderlich.')
        self._storage()
        location = self.base/stage_id
        encoded = _read(location, 'manifest.json', MAX_MANIFEST_BYTES)
        if encoded is None or _sha(encoded) != expected_manifest_hash:
            raise ValueError('Staging-Manifest fehlt oder wurde verändert.')
        try:
            manifest = json.loads(encoded)
            if manifest['id'] != stage_id or manifest['execution_enabled'] is not False or manifest['apply_back_enabled'] is not False:
                raise ValueError('Ungültiges Staging-Manifest.')
            root, identity = _root(manifest['original_root'])
            if identity != manifest['root_identity']:
                raise ValueError('Originalwurzel hat ihre Identität geändert.')
            expected_inventory = {'manifest.json'}
            expected_directories = {'files'}
            for record in manifest['files']:
                path = _path(record['path'])
                staged = _read(location/'files', path)
                if staged is None or _sha(staged) != record['staged_sha256']:
                    raise ValueError('Staging-Datei fehlt oder wurde verändert.')
                current = _read(root, path)
                expected = record['staged_sha256'] if applied else record['original_sha256']
                if (None if current is None else _sha(current)) != expected:
                    raise ValueError('Zieldatei stimmt nicht mit der Übernahme überein.' if applied
                                     else 'Originalquelle wurde seit dem Staging verändert.')
                expected_inventory.add('files/'+path)
                expected_directories.update(parent.as_posix() for parent in Path('files/'+path).parents if parent != Path('.'))
            observed = set()
            for directory, directories, files in os.walk(location, followlinks=False):
                for name in directories + files:
                    _components(Path(directory)/name)
                for name in directories:
                    if (Path(directory)/name).relative_to(location).as_posix() not in expected_directories:
                        raise ValueError('Unerwartetes zusätzliches Staging-Verzeichnis.')
                for name in files:
                    observed.add((Path(directory)/name).relative_to(location).as_posix())
                    if len(observed) > 21:
                        raise ValueError('Unerwartete zusätzliche Staging-Dateien.')
            if observed != expected_inventory:
                raise ValueError('Staging-Dateiumfang wurde verändert.')
        except (KeyError, TypeError, OSError, json.JSONDecodeError) as exc:
            raise ValueError('Staging-Manifest oder Quellen sind ungültig.') from exc
        return dict(id=stage_id, verified=True, manifest_hash=expected_manifest_hash,
                    execution_enabled=False, apply_back_enabled=False)
