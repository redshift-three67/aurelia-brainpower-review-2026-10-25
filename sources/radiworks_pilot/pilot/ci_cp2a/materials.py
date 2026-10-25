"""Bounded official SQLite source download and extraction; never executes it."""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import stat
import urllib.request
import zipfile

SOURCE_URL = 'https://sqlite.org/2026/sqlite-src-3540100.zip'
SHA256 = '387e7f6cad4797b17848c07d453dc6606917bb356a6cfe5a3abafd38c240c71b'
SHA3 = '877c6f4996ce7adb368686bce21638de9e3d91534832ad3d9d119037d1bc22ad'
ROOT = 'sqlite-src-3540100'
SOURCE_ID = '555e07ef33f69a0957d24d8e555b702464a131d6f1607f4c3c1e4551e8e6ca76'


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError('source redirect is outside approved download')


def digest(path, algorithm='sha256'):
    h = hashlib.new(algorithm)
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(65536), b''):
            h.update(block)
    return h.hexdigest()


def regular(path, maximum):
    s = path.lstat()
    if not stat.S_ISREG(s.st_mode) or path.is_symlink() or getattr(path, 'is_junction', lambda: False)():
        raise ValueError('material is not a regular file')
    if s.st_size > maximum:
        raise ValueError('material size exceeds limit')


def extract_source(archive, target, expected_sha256=SHA256, expected_sha3=SHA3,
                   expected_root=ROOT, max_total=128 * 1024 * 1024):
    regular(archive, 16 * 1024 * 1024)
    if digest(archive) != expected_sha256 or digest(archive, 'sha3_256') != expected_sha3:
        raise ValueError('source hash differs')
    if target.exists() or target.is_symlink():
        raise FileExistsError('never reuse source destination')
    with zipfile.ZipFile(archive) as z:
        members = z.infolist()
        if len(members) > 3000 or sum(x.file_size for x in members) > max_total:
            raise ValueError('archive expansion exceeds limit')
        seen, files = set(), set()
        for item in members:
            if item.filename != item.orig_filename:
                raise ValueError('archive path was normalized by the platform')
            name = item.orig_filename.rstrip('/')
            parts = name.split('/')
            if (name in seen or '\\' in name or ':' in name or
                    not parts or parts[0] != expected_root or
                    any(x in ('', '.', '..') for x in parts) or PurePosixPath(name).is_absolute()):
                raise ValueError('unsafe or duplicate archive path')
            seen.add(name)
            kind = stat.S_IFMT(item.external_attr >> 16)
            if kind not in (0, stat.S_IFREG, stat.S_IFDIR) or (kind == stat.S_IFDIR) != item.is_dir() and kind != 0:
                raise ValueError('archive member is not a regular file/directory')
            if not item.is_dir():
                files.add(name)
        for name in seen:
            if any(parent.as_posix() in files for parent in PurePosixPath(name).parents):
                raise ValueError('archive parent is a file')
        target.mkdir(mode=0o700)
        for item in members:
            dst = target.joinpath(*item.filename.rstrip('/').split('/'))
            if item.is_dir():
                dst.mkdir(parents=True, exist_ok=True)
            else:
                dst.parent.mkdir(parents=True, exist_ok=True)
                with z.open(item) as source, dst.open('xb') as sink:
                    remaining = item.file_size
                    while block := source.read(min(65536, remaining + 1)):
                        remaining -= len(block)
                        if remaining < 0:
                            raise ValueError('archive member exceeded declared size')
                        sink.write(block)
                    if remaining:
                        raise ValueError('truncated archive member')
                os.chmod(dst, 0o555 if (item.external_attr >> 16) & 0o111 else 0o444)
        for parent, directories, _ in os.walk(target):
            os.chmod(parent, 0o755)
        return target / expected_root


def download(path):
    opener = urllib.request.build_opener(NoRedirect())
    with opener.open(SOURCE_URL, timeout=30) as response, path.open('xb') as sink:
        total = 0
        while block := response.read(65536):
            total += len(block)
            if total > 16 * 1024 * 1024:
                raise ValueError('download exceeds limit')
            sink.write(block)
    regular(path, 16 * 1024 * 1024)
    if digest(path) != SHA256 or digest(path, 'sha3_256') != SHA3:
        raise ValueError('download hash differs')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['download', 'extract'])
    parser.add_argument('archive', type=Path)
    parser.add_argument('--target', type=Path)
    args = parser.parse_args()
    if args.action == 'download':
        download(args.archive)
    else:
        if args.target is None:
            parser.error('--target required')
        root = extract_source(args.archive, args.target)
        if (root / 'VERSION').read_text().strip() != '3.54.1' or (root / 'manifest.uuid').read_text().strip() != SOURCE_ID:
            raise ValueError('SQLite version/source identity differs')
        print(json.dumps({'source_root': str(root), 'source_sha256': SHA256, 'source_sha3': SHA3}))


if __name__ == '__main__':
    main()
