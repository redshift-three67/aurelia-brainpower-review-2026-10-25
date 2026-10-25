"""CP1 source/wheel/result guards. Does not build, install or start products."""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import sys
import re
import shutil
import subprocess
import xml.etree.ElementTree as ET

COMMIT = "d1eb34260179a499e2b0362bf609ce96957b78aa"
SINGLETONS = {"pilot/Dockerfile", "pilot/dependencies.json", "pilot/requirements-linux-c3a.lock"}


def linked(path):
    return path.is_symlink() or getattr(path, "is_junction", lambda: False)()


def digest(path, maximum=100 * 1024 * 1024):
    if linked(path) or not path.is_file() or path.stat().st_size > maximum:
        raise ValueError("unexpected file kind or size")
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(65536), b""):
            h.update(block)
    return h.hexdigest()


def safe_name(value):
    if not isinstance(value, str) or "\\" in value:
        raise ValueError("unsafe path")
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in value.split("/")):
        raise ValueError("unsafe path")
    if not (value.startswith(("engine/", "webapp/")) or value in SINGLETONS):
        raise ValueError("path outside product scope")
    return value


def verify_source(root, lock, actual_commit):
    if actual_commit != COMMIT or lock.get("commit") != COMMIT or linked(root):
        raise ValueError("source identity mismatch")
    records = lock.get("files", [])
    if not 0 < len(records) <= 1000:
        raise ValueError("invalid source inventory")
    expected = set()
    for item in records:
        name = safe_name(item["path"])
        if name in expected or not re.fullmatch(r"[0-9a-f]{64}", item["sha256"]):
            raise ValueError("duplicate path or malformed hash")
        expected.add(name)
        path = root / name
        for parent in path.parents:
            if parent == root: break
            if linked(parent): raise ValueError("linked source parent")
        if digest(path, 16 * 1024 * 1024) != item["sha256"] or path.stat().st_size != item["bytes"]:
            raise ValueError("source bytes differ: " + name)
    if not SINGLETONS <= expected or not any(p.startswith("engine/") for p in expected) or not any(p.startswith("webapp/") for p in expected):
        raise ValueError("incomplete source control inventory")
    actual = set()
    for prefix in ("engine", "webapp"):
        base = root / prefix
        if linked(base) or not base.is_dir(): raise ValueError("missing product directory")
        for parent, dirs, files in os.walk(base, followlinks=False):
            for child in dirs + files:
                if linked(Path(parent) / child): raise ValueError("linked source entry")
            for name in files:
                actual.add((Path(parent) / name).relative_to(root).as_posix())
    if actual != {p for p in expected if p.startswith(("engine/", "webapp/"))}:
        raise ValueError("product file set differs")
    return len(records)


def verify_wheels(root, dependencies):
    if linked(root) or not root.is_dir() or not dependencies:
        raise ValueError("missing wheels")
    expected = set()
    for item in dependencies:
        name = item["file"]
        if not isinstance(name, str) or "/" in name or "\\" in name or not name.endswith(".whl") or name in expected:
            raise ValueError("invalid wheel name")
        expected.add(name)
        if digest(root / name) != item["sha256"]: raise ValueError("wheel hash differs")
    if {p.name for p in root.iterdir()} != expected: raise ValueError("wheel set differs")
    return len(expected)


def junit_counts(path):
    try:
        root = ET.fromstring(path.read_bytes())
        suites = [x for x in root.iter("testsuite") if not list(x.iterfind("testsuite"))]
        result = {key: sum(int(s.get(key, "0")) for s in suites) for key in ("tests", "failures", "errors", "skipped")}
    except (ET.ParseError, ValueError, OSError) as exc:
        raise ValueError("invalid JUnit") from exc
    if result["tests"] <= 0 or any(result[key] != 0 for key in ("failures", "errors", "skipped")):
        raise ValueError("tests absent, failed or skipped")
    return result


def cloud_audit():
    """Bounded metadata only; no environment dump/credentials, Docker calls or installs."""
    usage = shutil.disk_usage(Path.cwd())
    return {"os": sys.platform, "architecture": os.uname().machine if hasattr(os, "uname") else "unverified",
            "python": ".".join(map(str, sys.version_info[:3])), "cpu_count": os.cpu_count(),
            "workspace_free_bytes": usage.free,
            "commands_present": {name: shutil.which(name) is not None for name in ("git", "docker", "node", "google-chrome", "chromium")},
            "docker_daemon_usable": "unverified", "browser_usable": "unverified",
            "product_started": False, "environment_variables_dumped": False}


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    source = sub.add_parser("source")
    source.add_argument("root", type=Path)
    source.add_argument("lock", type=Path)
    wheels = sub.add_parser("wheels")
    wheels.add_argument("root", type=Path)
    wheels.add_argument("dependencies", type=Path)
    junit = sub.add_parser("junit")
    junit.add_argument("report", type=Path)
    sub.add_parser("cloud-audit")
    args = parser.parse_args()
    if args.command == "source":
        commit = subprocess.run(["git", "-C", str(args.root), "rev-parse", "HEAD"], check=True, capture_output=True, text=True, timeout=15).stdout.strip()
        result = {"verified_source_files": verify_source(args.root, json.loads(args.lock.read_text(encoding="utf-8")), commit), "commit": commit}
    elif args.command == "wheels":
        result = {"verified_wheels": verify_wheels(args.root, json.loads(args.dependencies.read_text(encoding="utf-8")))}
    elif args.command == "junit": result = junit_counts(args.report)
    else: result = cloud_audit()
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
