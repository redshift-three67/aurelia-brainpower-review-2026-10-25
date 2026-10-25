"""CP2A own-process Linux loader proof; :memory: only, no product imports.

Importing this module performs no native collection. Passing checks is evidence,
not permission for native CI, compatibility acceptance or product integration.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import platform
import re
import stat

PREFIX = "/opt/radiworks-sqlite/lib"
SCHEMA = "radiworks.cp2a-sqlite-probe.v1"
FEATURES = "update_limit delete_limit json_unicode max_int foreign_keys fts3 fts4 fts5 rtree math session_symbol preupdate_symbol".split()
# Exact 2026-10-18 preview PRAGMA evidence; COMPILER is provenance, not semantics.
BASELINE_OPTIONS = """ATOMIC_INTRINSICS=1 COMPILER=gcc-12.2.0 DEFAULT_AUTOVACUUM
DEFAULT_CACHE_SIZE=-2000 DEFAULT_FILE_FORMAT=4 DEFAULT_JOURNAL_SIZE_LIMIT=-1
DEFAULT_MMAP_SIZE=0 DEFAULT_PAGE_SIZE=4096 DEFAULT_PCACHE_INITSZ=20
DEFAULT_RECURSIVE_TRIGGERS DEFAULT_SECTOR_SIZE=4096 DEFAULT_SYNCHRONOUS=2
DEFAULT_WAL_AUTOCHECKPOINT=1000 DEFAULT_WAL_SYNCHRONOUS=2 DEFAULT_WORKER_THREADS=0
ENABLE_COLUMN_METADATA ENABLE_DBSTAT_VTAB ENABLE_FTS3 ENABLE_FTS3_PARENTHESIS
ENABLE_FTS3_TOKENIZER ENABLE_FTS4 ENABLE_FTS5 ENABLE_LOAD_EXTENSION
ENABLE_MATH_FUNCTIONS ENABLE_PREUPDATE_HOOK ENABLE_RTREE ENABLE_SESSION
ENABLE_STMTVTAB ENABLE_UNLOCK_NOTIFY ENABLE_UPDATE_DELETE_LIMIT HAVE_ISNAN
LIKE_DOESNT_MATCH_BLOBS MALLOC_SOFT_LIMIT=1024 MAX_ATTACHED=10 MAX_COLUMN=2000
MAX_COMPOUND_SELECT=500 MAX_DEFAULT_PAGE_SIZE=32768 MAX_EXPR_DEPTH=1000
MAX_FUNCTION_ARG=127 MAX_LENGTH=1000000000 MAX_LIKE_PATTERN_LENGTH=50000
MAX_MMAP_SIZE=0x7fff0000 MAX_PAGE_COUNT=1073741823 MAX_PAGE_SIZE=65536
MAX_SCHEMA_RETRY=25 MAX_SQL_LENGTH=1000000000 MAX_TRIGGER_DEPTH=1000
MAX_VARIABLE_NUMBER=250000 MAX_VDBE_OP=250000000 MAX_WORKER_THREADS=8
MUTEX_PTHREADS OMIT_LOOKASIDE SECURE_DELETE SOUNDEX SYSTEM_MALLOC TEMP_STORE=1
THREADSAFE=1 USE_URI""".split()


def _options(values):
    if not isinstance(values, list) or not 1 <= len(values) <= 256:
        raise ValueError("invalid compile options")
    result = {}
    for value in values:
        if not isinstance(value, str) or not re.fullmatch(r"[A-Z][A-Z0-9_]*(?:=[A-Za-z0-9_.+\-]+)?", value):
            raise ValueError("invalid compile options")
        key = value.split("=", 1)[0]
        if key in result:
            raise ValueError("duplicate compile options")
        result[key] = value
    if "COMPILER" not in result:
        raise ValueError("missing compiler compile options")
    return result


def _delta(before, after):
    a, b = {k: v for k, v in before.items() if k != "COMPILER"}, {k: v for k, v in after.items() if k != "COMPILER"}
    return {"missing": sorted(a[k] for k in a.keys() - b.keys()),
            "added": sorted(b[k] for k in b.keys() - a.keys()),
            "changed": {k: {"baseline": a[k], "candidate": b[k]} for k in sorted(a.keys() & b.keys()) if a[k] != b[k]}}


def _posix(value):
    if not isinstance(value, str) or "\\" in value or any(ord(c) < 33 for c in value):
        raise ValueError("invalid path")
    p = PurePosixPath(value)
    if not p.is_absolute() or str(p) != value or ".." in p.parts:
        raise ValueError("noncanonical path")
    return p


def _sha(value):
    return isinstance(value, str) and re.fullmatch("[0-9a-f]{64}", value) is not None


def _common_errors(report):
    errors = []
    if report["schema"] != SCHEMA:
        errors.append("report schema mismatch")
    if report["python_version"] != "3.12.15":
        errors.append("Python version mismatch")
    extension = report["extension"]
    _posix(extension["path"])
    if not _sha(extension.get("sha256")):
        errors.append("extension hash missing or invalid")
    if any(report["features"].get(name) is not True for name in FEATURES):
        errors.append("features failed or missing")
    libs = report["mapped_libraries"]
    if not isinstance(libs, list) or len(libs) != 1:
        raise ValueError("exactly one mapped SQLite library required")
    library = libs[0]
    for key in ("path", "resolved_path"):
        if not re.fullmatch(r"libsqlite3\.so(?:\.[0-9]+)*", _posix(library[key]).name):
            errors.append("invalid SQLite library path")
    if library.get("deleted") is not False or " (deleted)" in library["path"]:
        errors.append("deleted or unproven mapping")
    if not _sha(library.get("sha256")):
        errors.append("library hash missing or invalid")
    return errors


def _baseline_errors(report):
    errors = _common_errors(report)
    if report["sqlite_version"] != "3.40.1":
        errors.append("baseline SQLite version mismatch")
    for key in ("path", "resolved_path"):
        p = _posix(report["mapped_libraries"][0][key])
        if not any(p.is_relative_to(root) for root in ("/usr/lib", "/lib")):
            errors.append("baseline must map system library")
    if any(_delta(_options(BASELINE_OPTIONS), _options(report["compile_options"])).values()):
        errors.append("baseline compile options differ from source evidence")
    return errors


def validate_report(report, baseline, expected_source_id, expected_library_hash, prefix=PREFIX):
    """Pure, fail-closed comparison; never access files, load SQLite or approve use."""
    result = {"ok": False, "errors": [], "option_delta": {}, "compiler": {}, "review_required": False, "compatibility_approved": False}
    errors = result["errors"]
    try:
        errors.extend("baseline: " + e for e in _baseline_errors(baseline))
        errors.extend(_common_errors(report))
        if report["sqlite_version"] != "3.54.1":
            errors.append("SQLite version mismatch")
        if not isinstance(expected_source_id, str) or not expected_source_id or report["source_id"] != expected_source_id:
            errors.append("SQLite source identity mismatch")
        root = _posix(prefix)
        library = report["mapped_libraries"][0]
        if any(not _posix(library[k]).is_relative_to(root) for k in ("path", "resolved_path")):
            errors.append("mapped library escapes private prefix")
        if not _sha(expected_library_hash) or library["sha256"] != expected_library_hash:
            errors.append("actual library hash mismatch")
        if report["python_version"] != baseline["python_version"]:
            errors.append("Python drift from baseline")
        if report["extension"] != baseline["extension"]:
            errors.append("Python extension drift from baseline")
        before, after = _options(baseline["compile_options"]), _options(report["compile_options"])
        result["option_delta"] = _delta(before, after)
        result["compiler"] = {"baseline": before["COMPILER"], "candidate": after["COMPILER"]}
        if any(result["option_delta"].values()):
            result["review_required"] = True
            errors.append("functional compile options delta: review required")
    except (KeyError, TypeError, ValueError, AttributeError) as exc:
        errors.append("invalid report: " + str(exc))
    result["ok"] = not errors
    return result


def parse_maps(text):
    """Collapse segments, retaining distinct path/device/inode and deleted state."""
    found = {}
    for line in text.splitlines():
        parts = line.split(None, 5)
        if len(parts) < 6 or "libsqlite3" not in parts[5]:
            continue
        path = parts[5]
        deleted = path.endswith(" (deleted)")
        if deleted:
            path = path[:-10]
        _posix(path)
        major, minor = (int(v, 16) for v in parts[3].split(":"))
        item = {"path": path, "deleted": deleted, "device": [major, minor], "inode": int(parts[4])}
        found[(path, major, minor, item["inode"], deleted)] = item
    return sorted(found.values(), key=lambda item: (item["path"], item["inode"]))


def _read_regular(path, max_bytes, prefix=None):
    path = Path(path)
    if not path.is_absolute() or ".." in path.parts or any(ord(c) < 32 for c in str(path)):
        raise ValueError("invalid file path")
    resolved = path.resolve(strict=True)
    if prefix is not None:
        root = Path(prefix)
        if root.resolve(strict=True) != root or not path.is_relative_to(root) or not resolved.is_relative_to(root):
            raise ValueError("file escapes private prefix")
    if not stat.S_ISREG(resolved.stat().st_mode):
        raise ValueError("nonregular file")
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0) | getattr(os, "O_BINARY", 0)
    with os.fdopen(os.open(resolved, flags), "rb") as handle:
        before = os.fstat(handle.fileno())
        if not stat.S_ISREG(before.st_mode) or before.st_size > max_bytes:
            raise ValueError("nonregular or oversized file")
        content = handle.read(max_bytes + 1)
        after = os.fstat(handle.fileno())
    identity = lambda s: (s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns, s.st_ctime_ns)
    if len(content) > max_bytes or identity(before) != identity(after) or identity(after) != identity(resolved.stat()):
        raise ValueError("file changed during bounded read")
    return resolved, after, content


def hash_file(path, prefix=None, max_bytes=128 * 1024 * 1024):
    resolved, info, content = _read_regular(path, max_bytes, prefix)
    return {"path": str(path), "resolved_path": str(resolved), "sha256": hashlib.sha256(content).hexdigest(),
            "st_dev": info.st_dev, "st_ino": info.st_ino}


def _maps():
    with open("/proc/self/maps", "r", encoding="utf-8") as handle:
        text = handle.read(4 * 1024 * 1024 + 1)
    if len(text) > 4 * 1024 * 1024:
        raise ValueError("oversized process maps")
    return parse_maps(text)


def _features(connection, sqlite, library):
    import ctypes
    features, failures = {}, {}
    def check(name, action):
        try:
            features[name] = action() is True
        except (sqlite.Error, ValueError, OSError, AttributeError) as exc:
            features[name], failures[name] = False, str(exc)[:300]
    def limited_update():
        connection.execute("CREATE TABLE limits_test (id INTEGER PRIMARY KEY, value INTEGER)")
        connection.executemany("INSERT INTO limits_test VALUES (?, 0)", [(1,), (2,), (3,)])
        connection.execute("UPDATE limits_test SET value=7 ORDER BY id LIMIT 1")
        return connection.execute("SELECT group_concat(value, ',') FROM (SELECT value FROM limits_test ORDER BY id)").fetchone() == ("7,0,0",)
    def limited_delete():
        connection.execute("DELETE FROM limits_test ORDER BY id DESC LIMIT 1")
        return connection.execute("SELECT group_concat(id, ',') FROM (SELECT id FROM limits_test ORDER BY id)").fetchone() == ("1,2",)
    def foreign_key():
        connection.commit()
        connection.execute("PRAGMA foreign_keys=ON")
        if connection.execute("PRAGMA foreign_keys").fetchone() != (1,):
            return False
        connection.execute("CREATE TABLE parent (id INTEGER PRIMARY KEY)")
        connection.execute("CREATE TABLE child (parent_id INTEGER REFERENCES parent(id))")
        try:
            connection.execute("INSERT INTO child VALUES (123)")
        except sqlite.IntegrityError:
            connection.rollback()
            return True
        return False
    def fts(module):
        connection.execute("CREATE VIRTUAL TABLE " + module + "_test USING " + module + "(body)")
        connection.execute("INSERT INTO " + module + "_test VALUES (?)", ("unicode café",))
        return connection.execute("SELECT count(*) FROM " + module + "_test WHERE body MATCH 'unicode'").fetchone() == (1,)
    def rtree():
        connection.execute("CREATE VIRTUAL TABLE rtree_test USING rtree(id, x1, x2)")
        connection.execute("INSERT INTO rtree_test VALUES (1, 2, 3)")
        return connection.execute("SELECT id FROM rtree_test WHERE x1 <= 2 AND x2 >= 3").fetchone() == (1,)
    check("update_limit", limited_update)
    check("delete_limit", limited_delete)
    check("json_unicode", lambda: connection.execute("SELECT json_extract(?, '$.value')", ('{"value":"Grüße 世界 🌍"}',)).fetchone() == ("Grüße 世界 🌍",))
    check("max_int", lambda: connection.execute("SELECT ?, typeof(?)", (2**63 - 1, 2**63 - 1)).fetchone() == (2**63 - 1, "integer"))
    check("foreign_keys", foreign_key)
    for module in ("fts3", "fts4", "fts5"):
        check(module, lambda module=module: fts(module))
    check("rtree", rtree)
    check("math", lambda: connection.execute("SELECT sqrt(81), sin(0), pow(2, 10)").fetchone() == (9.0, 0.0, 1024.0))
    try:
        loaded = ctypes.CDLL(library, mode=os.RTLD_NOLOAD | os.RTLD_LOCAL)
    except (OSError, AttributeError) as exc:
        for name in ("session_symbol", "preupdate_symbol"):
            features[name], failures[name] = False, str(exc)[:300]
    else:
        for name, symbol in (("session_symbol", "sqlite3session_create"), ("preupdate_symbol", "sqlite3_preupdate_hook")):
            check(name, lambda symbol=symbol: getattr(loaded, symbol) is not None)
    return features, failures


def collect_report(prefix=None):
    """Only called by CLI; Linux own-process maps and in-memory SQL, no DB files."""
    if platform.system() != "Linux":
        raise ValueError("native collection requires explicitly authorized Linux CI")
    import sqlite3
    import _sqlite3
    maps = _maps()
    if len(maps) != 1 or maps[0]["deleted"]:
        raise ValueError("exactly one nondeleted mapped SQLite library required")
    mapping = maps[0]
    library = hash_file(mapping["path"], prefix=prefix)
    if library["st_ino"] != mapping["inode"] or library["st_dev"] != os.makedev(*mapping["device"]):
        raise ValueError("mapped SQLite library/file identity mismatch")
    connection = sqlite3.connect(":memory:")
    try:
        version, source_id = connection.execute("SELECT sqlite_version(), sqlite_source_id()").fetchone()
        options = sorted(row[0] for row in connection.execute("PRAGMA compile_options"))
        features, failures = _features(connection, sqlite3, library["resolved_path"])
    finally:
        connection.close()
    if _maps() != maps or hash_file(mapping["path"], prefix=prefix) != library:
        raise ValueError("mapped SQLite identity changed during feature proof")
    extension = hash_file(_sqlite3.__file__)
    return {"schema": SCHEMA, "python_version": platform.python_version(), "sqlite_version": version,
            "source_id": source_id, "compile_options": options, "features": features, "feature_errors": failures,
            "extension": {"path": extension["resolved_path"], "sha256": extension["sha256"]},
            "mapped_libraries": [{**mapping, **library}], "persistent_db_opened": False, "product_imported": False}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline")
    parser.add_argument("--expected-library-hash")
    parser.add_argument("--expected-source-id")
    parser.add_argument("--output", required=True)
    args = parser.parse_args(argv)
    if (args.baseline and not (args.expected_library_hash and args.expected_source_id)) or (not args.baseline and (args.expected_library_hash or args.expected_source_id)):
        parser.error("candidate requires baseline, expected-library-hash and expected-source-id together")
    report = {}
    try:
        report = collect_report(PREFIX if args.baseline else None)
        if args.baseline:
            baseline = json.loads(_read_regular(Path(args.baseline).absolute(), 1024 * 1024)[2])
            validation = validate_report(report, baseline, args.expected_source_id, args.expected_library_hash)
        else:
            errors = _baseline_errors(report)
            validation = {"ok": not errors, "errors": errors, "compatibility_approved": False}
    except (OSError, ValueError, TypeError, KeyError, AttributeError) as exc:
        validation = {"ok": False, "errors": ["collection/validation failed: " + str(exc)], "compatibility_approved": False}
    report["validation"] = validation
    output = Path(args.output).absolute()
    if output.parent.resolve(strict=True) != output.parent or ".." in output.parts:
        raise ValueError("noncanonical or symlinked output path")
    with output.open("x", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    return 0 if validation["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
