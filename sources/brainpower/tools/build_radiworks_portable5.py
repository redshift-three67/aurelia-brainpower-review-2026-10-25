from __future__ import annotations

import argparse
import hashlib
import importlib.metadata as metadata
import json
import os
import shutil
import stat
import sys
import tomllib
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
LABEL = "RadiWorks-Portable5-0.4.0-rc1"
PRODUCT_REL = Path("runtime/rw-r6-release-20261008")
EXPECTED_PRODUCT_MANIFEST_SHA256 = "445ece8f8c826e1391fead34c9a4c9b271e3b13b6d59a7654f66f11ab77b6275"
EXPECTED_PRODUCT_FILE_COUNT = 200
WRAPPER_REL = Path("tools/radiworks_release_service.py")
WRAPPER_PIN_REL = PRODUCT_REL / "service.py"
CATALOG_REL = Path("runtime/radiworks-catalog-releases/e33ea136d8ea448fada7524757385ee4")
CPU_REL = Path("runtime/rw-exp1c-20261005")
CLARKE_SOURCE = Path(r"C:\Users\Hubert111\Documents\Radiworks\materiaMedica\Clarke")
BASE_VENV = Path(r"C:\Users\Hubert111\Documents\Radiworks\radiworks_port\engine\.venv")
CPYTHON_ROOT = Path(r"C:\Python313")
OUTPUT = ROOT / "builds" / "new-version" / LABEL
BASE_DIRECT = ("fastapi", "uvicorn", "websockets", "httpx", "cryptography")
EXPECTED_BASE = {
    "annotated-doc": "0.0.5", "annotated-types": "0.8.0", "anyio": "4.14.2",
    "certifi": "2026.7.22", "cffi": "2.1.1", "click": "8.5.0",
    "cryptography": "50.0.1", "fastapi": "0.141.1", "h11": "0.16.0",
    "httpcore": "1.0.9", "httpx": "0.28.1", "idna": "3.19",
    "pydantic": "2.13.5", "pydantic-core": "2.46.5", "pycparser": "3.0",
    "starlette": "1.6.0",
    "typing-extensions": "4.16.0", "typing-inspection": "0.4.4",
    "uvicorn": "0.52.4", "websockets": "17.1",
}
EXCLUDED_STDLIB = {"site-packages", "test", "idlelib", "ensurepip", "tkinter", "turtledemo", "__pycache__"}


class BuildError(RuntimeError):
    pass


@dataclass(frozen=True)
class ManifestCheck:
    digest: str
    file_count: int


def _is_reparse(path: Path) -> bool:
    if path.is_symlink() or (hasattr(path, "is_junction") and path.is_junction()):
        return True
    try:
        return bool(path.lstat().st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT)
    except (AttributeError, FileNotFoundError, OSError):
        return False


def _safe_rel_path(raw: object) -> str:
    if not isinstance(raw, str) or not raw or "\x00" in raw or "\\" in raw:
        raise BuildError(f"Invalid relative path: {raw!r}")
    posix, windows = PurePosixPath(raw), PureWindowsPath(raw)
    if posix.is_absolute() or windows.is_absolute() or windows.drive or any(p in ("", ".", "..") for p in posix.parts):
        raise BuildError(f"Unsafe relative path: {raw!r}")
    return posix.as_posix()


def resolve_bundle_path(root: Path | str, rel: str) -> Path:
    root_path = Path(root).resolve()
    safe = _safe_rel_path(rel)
    current = root_path
    for part in PurePosixPath(safe).parts:
        current = current / part
        if current.exists() and _is_reparse(current):
            raise BuildError(f"Linked path refused: {current}")
    result = current.resolve()
    if result != root_path and root_path not in result.parents:
        raise BuildError(f"Path escapes root: {rel!r}")
    return result


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_product_manifest(source_root: Path | str) -> ManifestCheck:
    source = Path(source_root).resolve()
    manifest_path = source / "PRODUCT_MANIFEST.json"
    if not manifest_path.is_file() or _is_reparse(manifest_path):
        raise BuildError("Pinned product manifest missing or linked")
    raw = manifest_path.read_bytes()
    try:
        manifest = json.loads(raw.decode("utf-8-sig"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise BuildError("Invalid product manifest JSON") from exc
    files = manifest.get("files") if isinstance(manifest, dict) else None
    if not isinstance(files, list) or not files or len(files) > 10000:
        raise BuildError("Invalid product manifest file list")
    seen: set[str] = set()
    for item in files:
        if not isinstance(item, dict):
            raise BuildError("Invalid product manifest entry")
        rel = _safe_rel_path(item.get("path"))
        if rel.casefold() in seen:
            raise BuildError(f"Duplicate product path: {rel}")
        seen.add(rel.casefold())
        target = resolve_bundle_path(source, rel)
        if not target.is_file() or _sha256(target) != str(item.get("sha256", "")).lower():
            raise BuildError(f"Pinned product file mismatch: {rel}")
        if "bytes" in item and item["bytes"] != target.stat().st_size:
            raise BuildError(f"Pinned product size mismatch: {rel}")
    return ManifestCheck(hashlib.sha256(raw).hexdigest(), len(files))


def verify_pinned_product(source_root: Path | str) -> ManifestCheck:
    checked = verify_product_manifest(source_root)
    if checked.digest != EXPECTED_PRODUCT_MANIFEST_SHA256 or checked.file_count != EXPECTED_PRODUCT_FILE_COUNT:
        raise BuildError("R6 pinned product manifest identity mismatch")
    return checked


def _verify_release_manifest(path: Path, files_root: Path, schema: str) -> tuple[bytes, dict, list[dict]]:
    root = files_root.resolve()
    if not path.is_file() or _is_reparse(path):
        raise BuildError(f"Release manifest missing or linked: {path}")
    raw = path.read_bytes()
    try:
        data = json.loads(raw.decode("utf-8-sig"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise BuildError(f"Invalid release manifest: {path}") from exc
    files = data.get("files") if isinstance(data, dict) else None
    if data.get("schema") != schema or not isinstance(files, list) or not files:
        raise BuildError(f"Unexpected release manifest: {path}")
    seen: set[str] = set()
    for item in files:
        rel = _safe_rel_path(item.get("path") if isinstance(item, dict) else None)
        if rel.casefold() in seen:
            raise BuildError(f"Duplicate release path: {rel}")
        seen.add(rel.casefold())
        file_path = resolve_bundle_path(root, rel)
        if not file_path.is_file() or _sha256(file_path) != str(item.get("sha256", "")).lower():
            raise BuildError(f"Release file mismatch: {rel}")
        if "bytes" in item and item["bytes"] != file_path.stat().st_size:
            raise BuildError(f"Release file size mismatch: {rel}")
    return raw, data, files


def _copy_file(source: Path, target: Path) -> None:
    if not source.is_file() or _is_reparse(source):
        raise BuildError(f"Refusing missing or linked file: {source}")
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)


def _copy_tree(source: Path, target: Path, skip_pycache: bool = True) -> int:
    source = source.resolve()
    if not source.is_dir() or _is_reparse(source):
        raise BuildError(f"Refusing missing or linked source directory: {source}")
    count = 0
    for base, dirs, files in os.walk(source, followlinks=False):
        current = Path(base)
        dirs[:] = sorted(name for name in dirs if not (skip_pycache and name == "__pycache__"))
        for name in dirs:
            if _is_reparse(current / name):
                raise BuildError(f"Linked source directory: {current / name}")
        for name in sorted(files):
            src = current / name
            if _is_reparse(src):
                raise BuildError(f"Linked source file: {src}")
            if skip_pycache and (src.suffix.lower() == ".pyc" or "__pycache__" in src.parts):
                continue
            _copy_file(src, target / src.relative_to(source))
            count += 1
    return count


def _copy_manifest_files(source: Path, target: Path, files: list[dict]) -> None:
    for item in files:
        rel = _safe_rel_path(item["path"])
        _copy_file(resolve_bundle_path(source, rel), resolve_bundle_path(target, rel))


def _canonical(name: str) -> str:
    from packaging.utils import canonicalize_name
    return canonicalize_name(name)


def _distributions(site: Path) -> dict[str, metadata.Distribution]:
    found = {}
    for dist in metadata.distributions(path=[str(site)]):
        name = dist.metadata.get("Name")
        if name:
            key = _canonical(name)
            if key in found:
                raise BuildError(f"Duplicate distribution: {key}")
            found[key] = dist
    return found


def _closure(site: Path, direct: Iterable[str]) -> tuple[dict[str, metadata.Distribution], dict[str, str]]:
    try:
        from packaging.markers import default_environment
        from packaging.requirements import Requirement
    except ImportError as exc:
        raise BuildError("Existing venv must include packaging") from exc
    all_dists = _distributions(site)
    needed: set[str] = set()
    queue = [_canonical(name) for name in direct]
    while queue:
        key = queue.pop(0)
        if key in needed:
            continue
        dist = all_dists.get(key)
        if dist is None:
            raise BuildError(f"Required distribution missing: {key}")
        needed.add(key)
        for raw in dist.requires or ():
            requirement = Requirement(raw)
            if requirement.marker is None or requirement.marker.evaluate({**default_environment(), "extra": ""}):
                queue.append(_canonical(requirement.name))
    versions = {key: all_dists[key].version for key in sorted(needed)}
    if versions != EXPECTED_BASE:
        raise BuildError(f"Base dependency versions changed: {versions!r}")
    return {key: all_dists[key] for key in sorted(needed)}, versions


def _copy_distribution_files(dists: dict[str, metadata.Distribution], site_root: Path, target: Path, allow_scripts: bool) -> dict[str, object]:
    site = site_root.resolve()
    copied: dict[str, str] = {}
    records: dict[str, object] = {}
    excluded = []
    cpu_generated = {
        "../../bin/torchfrtrace.exe", "../../bin/torchrun.exe",
        "../../bin/isympy.exe", "../../share/man/man1/isympy.1",
    }
    for name, dist in sorted(dists.items()):
        file_records = []
        files = list(dist.files or ())
        if not files:
            raise BuildError(f"Distribution has no file records: {name}")
        for record in files:
            record_text = PurePosixPath(str(record)).as_posix()
            # direct_url.json may contain a local path to a private wheel/cache source.
            if PurePosixPath(record_text).name.casefold() == "direct_url.json":
                excluded.append({"distribution": name, "record": record_text, "reason": "local-source-metadata"})
                continue
            if "__pycache__" in record.parts or str(record).lower().endswith(".pyc"):
                continue
            source = Path(dist.locate_file(record)).resolve()
            if allow_scripts and source.is_relative_to(site.parents[1] / "Scripts") and source.suffix.lower() == ".exe":
                excluded.append({"distribution": name, "record": record_text, "reason": "generated-console-launcher"})
                continue
            if not allow_scripts and record_text in cpu_generated:
                excluded.append({"distribution": name, "record": record_text, "reason": "generated-entrypoint-or-man-page"})
                continue
            if not source.exists():
                raise BuildError(f"Dependency file missing: {name}/{record}")
            try:
                rel = source.relative_to(site)
            except ValueError:
                raise BuildError(f"Dependency escapes package root: {name}: {record_text}")
            if _is_reparse(source):
                raise BuildError(f"Linked dependency refused: {source}")
            rel_text = rel.as_posix()
            digest = _sha256(source)
            key = rel_text.casefold()
            if key in copied and copied[key] != digest:
                raise BuildError(f"Conflicting package file: {rel_text}")
            if key not in copied:
                _copy_file(source, resolve_bundle_path(target, rel_text))
                copied[key] = digest
            file_records.append({"path": rel_text, "sha256": digest, "bytes": source.stat().st_size})
        records[name] = file_records
    records["__excluded_nonruntime_records__"] = excluded
    return records

def _verify_cpu(cpu_root: Path) -> tuple[dict[str, str], dict]:
    path = cpu_root / "DEPENDENCY_MANIFEST.json"
    wheelhouse, deps = cpu_root / "wheelhouse", cpu_root / "deps"
    if not path.is_file() or not wheelhouse.is_dir() or not deps.is_dir():
        raise BuildError("C1 CPU runtime is incomplete")
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
        wheels = data["wheels"]
        if data.get("platform") != "win_amd64 cp313" or len(wheels) != 11:
            raise BuildError("Unexpected C1 CPU dependency manifest")
        expected = {}
        for wheel in wheels:
            filename = wheel["file"]
            if Path(filename).name != filename or not filename.endswith(".whl"):
                raise BuildError(f"Unsafe wheel filename: {filename!r}")
            key = _canonical(wheel["name"])
            file_path = wheelhouse / filename
            if key in expected or not file_path.is_file():
                raise BuildError(f"Missing or duplicate CPU wheel: {filename}")
            if file_path.stat().st_size != wheel["bytes"] or _sha256(file_path) != wheel["sha256"]:
                raise BuildError(f"CPU wheel provenance mismatch: {filename}")
            expected[key] = wheel["version"]
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise BuildError("Invalid C1 CPU manifest") from exc
    actual_dists = _distributions(deps)
    actual = {name: actual_dists[name].version for name in sorted(actual_dists)}
    if actual != expected:
        raise BuildError(f"Installed CPU closure differs from wheel manifest: {actual!r}")
    return expected, data


def embedded_pth() -> str:
    return ".\nDLLs\nLib\nLib/site-packages\n../app/engine/src\n../cpu/deps\nimport site\n"


def _copy_runtime(source: Path, target: Path) -> None:
    if sys.platform != "win32":
        raise BuildError("Builder must run on Windows")
    for name in ("python.exe", "pythonw.exe", "python3.dll", "python313.dll", "LICENSE.txt"):
        if not (source / name).is_file():
            raise BuildError(f"CPython runtime file missing: {source / name}")
        _copy_file(source / name, target / name)
    for path in source.glob("vcruntime140*.dll"):
        _copy_file(path, target / path.name)
    for path in sorted((source / "DLLs").iterdir()):
        if path.is_file():
            _copy_file(path, target / "DLLs" / path.name)
        elif path.is_dir():
            _copy_tree(path, target / "DLLs" / path.name)
        else:
            raise BuildError(f"Invalid CPython DLL entry: {path}")
    for path in sorted((source / "Lib").iterdir()):
        if path.name.casefold() in EXCLUDED_STDLIB:
            continue
        if path.is_file():
            _copy_file(path, target / "Lib" / path.name)
        elif path.is_dir():
            _copy_tree(path, target / "Lib" / path.name)
        else:
            raise BuildError(f"Invalid CPython stdlib entry: {path}")
    (target / "Lib" / "site-packages").mkdir(parents=True, exist_ok=True)
    (target / "python313._pth").write_text(embedded_pth(), encoding="ascii", newline="\n")


def _install_bytecode_guard(python_root: Path) -> None:
    import importlib.util
    import py_compile
    guard = python_root / "Lib" / "sitecustomize.py"
    if guard.exists():
        raise BuildError("Unexpected existing sitecustomize")
    guard.write_text("import sys\nsys.dont_write_bytecode = True\n", encoding="ascii", newline="\n")
    # Hash-based cache survives ZIP timestamps and relocation; children inherit via site.
    startup_sources = [guard] + sorted((python_root / "Lib" / "encodings").glob("*.py"))
    # Codec modules are imported before sitecustomize can disable later cache writes.
    for source in startup_sources:
        cache = Path(importlib.util.cache_from_source(str(source)))
        py_compile.compile(str(source), cfile=str(cache),
                           dfile="RadiWorks/python/" + source.relative_to(python_root).as_posix(),
                           doraise=True, invalidation_mode=py_compile.PycInvalidationMode.CHECKED_HASH)


def _hash_tree(root: Path, excluded: set[str] | None = None) -> list[dict]:
    excluded = excluded or set()
    records = []
    for path in sorted(root.rglob("*"), key=lambda value: value.relative_to(root).as_posix().casefold()):
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        if rel in excluded:
            continue
        if _is_reparse(path):
            raise BuildError(f"Linked package file: {path}")
        records.append({"path": rel, "bytes": path.stat().st_size, "sha256": _sha256(path)})
    return records


def _write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8", newline="\n")


def _verify_embedded(python: Path, cpu_deps: Path) -> None:
    import subprocess
    base = (
        "import sys,site; assert sys.version_info[:3]==(3,13,7); "
        "assert site.ENABLE_USER_SITE is False; "
        "assert sys.dont_write_bytecode is True and sys.flags.isolated; assert any(p.replace(chr(92),'/').lower().endswith('app/engine/src') for p in sys.path); "
        "assert any(p.replace(chr(92),'/').lower().endswith('cpu/deps') for p in sys.path); "
        "import fastapi,uvicorn,websockets,httpx,cryptography; "
        "import radiworks.core.comparison_worker; print('BASE_WORKER_IMPORTS_OK')"
    )
    result = subprocess.run([str(python), "-I", "-c", base], capture_output=True, text=True, timeout=60)
    if result.returncode or "BASE_WORKER_IMPORTS_OK" not in result.stdout:
        raise BuildError(f"Embedded base/worker import failed: {result.stderr[-1600:]}")
    cpu = (
        "import sys; import numpy,torch; assert not torch.cuda.is_available(); "
        "print('CPU_IMPORTS_OK',numpy.__version__,torch.__version__)"
    )
    result = subprocess.run([str(python), "-I", "-c", cpu], capture_output=True, text=True, timeout=180)
    if result.returncode or "CPU_IMPORTS_OK" not in result.stdout:
        raise BuildError(f"Embedded CPU import failed: {result.stderr[-1600:]}")


def _docs(bundle: Path, product: ManifestCheck, catalog: dict, catalog_files: list[dict], clarke_files: list[dict], base_versions: dict, cpu_versions: dict) -> None:
    _write_json(bundle / "VERSION.json", {
        "bundleLabel": LABEL, "bundleKind": "private-portable-test-candidate",
        "builtAtUtc": datetime.now(timezone.utc).isoformat(),
        "engineVersion": "0.2.0", "productCandidate": PRODUCT_REL.as_posix(),
        "productManifestDigest": product.digest, "productManifestFileCount": product.file_count,
        "python": "CPython 3.13.7 x64 embedded", "defaultInstances": 5,
        "defaultBasePort": 8103, "optionalCpuMode": True,
    })
    _write_json(bundle / "BASIS_DEPENDENCIES.json", {
        "schema": "radiworks.portable5-dependencies.v1",
        "baseRuntimeSource": "Pinned RadiWorks CPython 3.13.7 production dependency closure", "basePython": "3.13.7 x64",
        "baseDirectRequirements": list(BASE_DIRECT),
        "baseDistributions": [{"name": k, "version": v} for k, v in sorted(base_versions.items())],
        "cpuSource": CPU_REL.as_posix(), "cpuWheelIndex": cpu_versions["index"],
        "cpuPlatform": cpu_versions["platform"],
        "cpuDistributions": [{"name": k, "version": v} for k, v in sorted(cpu_versions["packages"].items())],
        "cpuWheelhouseIncluded": False,
        "cpythonSource": "Installed official CPython 3.13.7 x64 runtime",
        "python313Pth": embedded_pth().splitlines(),
    })
    _write_json(bundle / "DATA_RELEASES.json", {
        "catalogReleaseId": catalog["releaseId"],
        "catalogManifestSha256": catalog["manifestSha256"],
        "catalogFileCount": len(catalog_files),
        "clarkeSource": "Operator-provided RadiWorks materiaMedica/Clarke",
        "clarkeFileCount": len(clarke_files),
        "clarkeTotalBytes": sum(item["bytes"] for item in clarke_files),
        "clarkeManifest": clarke_files,
    })
    (bundle / "KURZSTART.md").write_text("""# RadiWorks Portable5 – Kurzstart

Privater Offline-Testkandidat für Windows 10 x64 mit eingebettetem CPython 3.13.7. Kein Installer und kein öffentlicher Produktrelease. Die Engine-Version bleibt 0.2.0; 0.4.0-rc1 bezeichnet nur dieses Testpaket.

## Start und Bedienung

1. Den vollständigen Ordner auf ein lokales NTFS-Laufwerk entpacken. Der Pfad darf Leerzeichen enthalten. Verschieben ist vor dem ersten Start möglich. Nach dem ersten Start nicht umbenennen oder verschieben: die laufzeitgebundenen absoluten Pfade benötigen einen gesonderten kontrollierten Datenumzug. Nicht aus dem ZIP starten.
2. Start-5.cmd per Explorer oder aus einer normalen eigenständigen PowerShell starten. Für Prozesse, die ein Ende einer Codex-Sitzung überleben sollen, nicht aus einem Codex-Terminal starten. Es wird keine geplante Aufgabe installiert.
3. Im Browser http://127.0.0.1:8103 bis http://127.0.0.1:8107 öffnen.
4. Status.cmd zeigt den Laufzustand. Stop-5.cmd fordert geordneten Stopp an. Start-01.cmd bis Start-05.cmd starten einzelne Instanzen.
5. Der Manager nimmt --count 1 bis 5 (Standard 5) und --base-port an. Beispiel für fünf Prüfports: python\\python.exe tools\\radiworks_portable_manager.py start --base-port 8120. Status/Stop müssen denselben Portblock erhalten.
6. Ein Fünferstart wird nur begonnen, wenn alle vorgesehenen Loopback-Ports frei sind. Es werden keine fremden Prozesse beendet. Bei Fehlern rollt der Manager ausschließlich selbst gestartete Instanzen geordnet zurück.

## Daten und Schlüssel

Katalog und Clarke-Materia-Medica werden von der Anwendung nur gelesen und sind über das Paketmanifest versionsgebunden. Ein Windows-Schreibschutz wird nicht behauptet. Jede Instanz erhält ein eigenes Home und einen eigenen Tenant/Client/Job-Scope unter state\\instances. Fernet-Schlüssel werden beim ersten Zielstart erzeugt und mit Windows-ACL im benutzerspezifischen %LOCALAPPDATA%\\RadiWorks\\Portable5-0.3.0-rc1\\keys gespeichert. Dieser historische Ordnername bleibt für die Schlüsselkontinuität bei einem Upgrade auf demselben PC bestehen. Sichere den Key-Ordner verschlüsselt und getrennt vom Paket; ohne passenden Schlüssel sind verschlüsselte Journale nicht wiederherstellbar. Das neue Paket kopiert keine bisherigen Homes, Fälle, Journale oder Schlüssel und führt keine automatische Datenmigration aus.

## Betriebsgrenzen

- Nur synthetische Testfälle verwenden. Keine realen Fälle, persönlichen Daten, vorhandenen Homes oder Schlüssel kopieren.
- Vor einem geplanten Stopp oder Update persönliche und Watchlist-Aufträge fertigstellen. Ein ausdrücklicher Stopp kann noch laufende Aufträge unterbrechen; sie werden nach einem Neustart nicht automatisch wiederholt.
- Bis zu fünf Instanzen sind ein Start-/Isolationsumfang, keine Leistungszusage. CPU, RAM und Datenträger begrenzen die Last; keine Zusage zu fünf parallelen 80k-Läufen.
- Der CPU-Pfad enthält die vorhandene Windows-CPU-Abhängigkeitsclosure einschließlich PyTorch CPU. Kein CUDA/GPU und kein S4.8-Modus.
- Clarke stammt aus dem lokal bereitgestellten materiaMedica\\Clarke-Ordner. Eine zuordenbare Lizenz der Daten wurde nicht verifiziert; vor öffentlicher Weitergabe ist Lizenzklärung erforderlich. Es wird kein pauschaler MIT-/LGPL-Grant für die Daten behauptet.
- Produkt- und Katalogdateien wurden anhand ihrer Quellmanifeste geprüft. Die Abnahme auf einem anderen Windows-PC ist separat durchzuführen: Start, synthetische Analyse, CPU-Vergleich, Stop und Neustart.
- Das Paket enthält Python und seine Anwendungs-/CPU-Bibliotheken; keine Python- oder Codex-Installation erforderlich. Windows 10/11 x64 benötigt zusätzlich die Microsoft Visual C++ v14 x64-Laufzeit (MSVCP140.dll/MSVCP140_ATOMIC_WAIT.dll). Der Start prüft diese Voraussetzung. Falls sie fehlt, die offizielle Laufzeit installieren: https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist?view=msvc-170 (x64-Download https://aka.ms/vc14/vc_redist.x64.exe). Es erfolgt keine automatische Installation oder Übernahme von System-DLLs. Danach ist der Betrieb offline über Loopback möglich. Ein unverändert frischer Windows-PC wurde noch nicht geprüft.
""", encoding="utf-8", newline="\n")
    (bundle / "KURZSTART.txt").write_bytes((bundle / "KURZSTART.md").read_bytes())
    (bundle / "PROVENANCE.md").write_text(f"""# Provenienz und Lizenzhinweise

Privater Portable5 0.4.0-rc1 Testkandidat auf dem gepinnten R6-Release, kein öffentlicher Produktrelease.

- Produktcode: gepinnter RadiWorks-Kandidat mit Manifest-SHA-256 {product.digest}; {product.file_count} Dateien aus {PRODUCT_REL.as_posix()}. Der freigegebene Wrapper wurde bytegleich zu service.py kopiert.
- Rate-Katalog: Release {catalog["releaseId"]}, Manifest-SHA-256 {catalog["manifestSha256"]}, {len(catalog_files)} Dateien aus {CATALOG_REL.as_posix()}.
- Clarke-Materia-Medica: Quelle bereitgestellter RadiWorks materiaMedica/Clarke-Bestand, {len(clarke_files)} Dateien und {sum(v["bytes"] for v in clarke_files)} Bytes. Die Quellablage enthielt keine eindeutig zuordenbare Lizenz/Provenienzdatei. Die Datenlizenz bleibt ungeklärt; es wird kein MIT- oder LGPL-Grant für diese Daten behauptet. Datei-Hashes stehen in DATA_RELEASES.json.
- Originalablage-Lizenzhinweise: licenses/UPSTREAM_LICENSE_LGPL3.txt und UPSTREAM_NOTICE.txt wurden unverändert übernommen; keine pauschale Lizenzzusage für sämtliche Daten.
- Code-/Laufzeitlizenzen: CPython-Lizenztext und Distributionsmetadaten/Lizenzdateien liegen in python/ und python/Lib/site-packages.
- CPU-Erweiterung: 11 installierte Distributionen aus runtime/rw-exp1c-20261005/deps; das C1-Manifest und die SHA-256-geprüften Wheels wurden als Buildprovenienz ausgewertet. Wheels werden nicht doppelt ins Paket kopiert.
- Keine bestehenden Homes, Fälle, Benutzer-Schlüssel, Secrets oder privaten lokalen Release-Artefakte wurden einbezogen.

Öffentliche Nutzung oder Weitergabe der Clarke-Daten setzt separate Lizenzklärung voraus.
""", encoding="utf-8", newline="\n")


def _launcher(bundle: Path, command: str, name: str) -> None:
    content = '@echo off\r\nsetlocal\r\n"%~dp0python\\python.exe" "%~dp0tools\\radiworks_portable_manager.py" ' + command + '\r\nset "RW_EXIT=%ERRORLEVEL%"\r\n'
    content += 'pause\r\n' if command in ("status", "stop") else 'if not "%RW_EXIT%"=="0" pause\r\n'
    content += 'exit /b %RW_EXIT%\r\n'
    (bundle / name).write_text(content, encoding="ascii", newline="")


def _make_zip(bundle: Path, zip_path: Path) -> None:
    if zip_path.exists():
        raise BuildError(f"Refusing to overwrite ZIP: {zip_path}")
    with zipfile.ZipFile(zip_path, "x", compression=zipfile.ZIP_DEFLATED, compresslevel=1, allowZip64=True) as archive:
        for path in sorted(bundle.rglob("*"), key=lambda value: value.relative_to(bundle).as_posix().casefold()):
            if path.is_file():
                info = zipfile.ZipInfo((Path(bundle.name) / path.relative_to(bundle)).as_posix(), (1980, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = (stat.S_IFREG | 0o644) << 16
                info.compress_level = 1
                with path.open("rb") as source, archive.open(info, "w", force_zip64=True) as target:
                    shutil.copyfileobj(source, target, length=1024 * 1024)


def build_bundle(make_zip: bool = False) -> Path:
    if os.name != "nt" or sys.platform != "win32":
        raise BuildError("Portable5 builder must run on Windows")
    staging = OUTPUT.with_name("." + OUTPUT.name + ".building")
    if OUTPUT.exists() or staging.exists():
        raise BuildError(f"Output/staging already exists; refusing overwrite: {OUTPUT}")
    product_root = ROOT / PRODUCT_REL
    product_check = verify_pinned_product(product_root)
    wrapper = ROOT / WRAPPER_REL
    pinned_wrapper = ROOT / WRAPPER_PIN_REL
    if not wrapper.is_file() or not pinned_wrapper.is_file() or _sha256(wrapper) != _sha256(pinned_wrapper):
        raise BuildError("Release wrapper is not the pinned final copy")
    catalog_root = ROOT / CATALOG_REL
    catalog_raw, catalog, catalog_files = _verify_release_manifest(catalog_root / "manifest.json", catalog_root / "data", "radiworks.catalog-release.v1")
    catalog["manifestSha256"] = hashlib.sha256(catalog_raw).hexdigest()
    cpu_root = ROOT / CPU_REL
    cpu_packages, cpu_manifest = _verify_cpu(cpu_root)
    if not CLARKE_SOURCE.is_dir() or _is_reparse(CLARKE_SOURCE):
        raise BuildError(f"Authorized Clarke source unavailable: {CLARKE_SOURCE}")
    venv_site = BASE_VENV / "Lib" / "site-packages"
    if not venv_site.is_dir():
        raise BuildError(f"Base venv package directory missing: {venv_site}")
    project = tomllib.loads((product_root / "engine" / "pyproject.toml").read_text(encoding="utf-8"))
    from packaging.requirements import Requirement
    direct = [Requirement(value).name for value in project["project"]["dependencies"]]
    if set(map(_canonical, direct)) != set(map(_canonical, BASE_DIRECT)):
        raise BuildError(f"Unexpected project dependencies: {direct!r}")
    base_dists, base_versions = _closure(venv_site, direct)

    staging.mkdir(parents=True)
    try:
        (staging / "tools").mkdir()
        manifest_data = json.loads((product_root / "PRODUCT_MANIFEST.json").read_text(encoding="utf-8-sig"))
        _copy_manifest_files(product_root, staging / "app", manifest_data["files"])
        _copy_file(product_root / "PRODUCT_MANIFEST.json", staging / "app" / "PRODUCT_MANIFEST.json")
        _copy_file(wrapper, staging / "app" / "service.py")
        _copy_file(catalog_root / "manifest.json", staging / "data" / "catalog-releases" / catalog_root.name / "manifest.json")
        _copy_manifest_files(catalog_root / "data", staging / "data" / "catalog-releases" / catalog_root.name / "data", catalog_files)
        clarke_dest = staging / "data" / "materia" / "Clarke"
        _copy_tree(CLARKE_SOURCE, clarke_dest)
        clarke_files = _hash_tree(clarke_dest)
        pyroot = staging / "python"
        _copy_runtime(CPYTHON_ROOT, pyroot)
        base_file_records = _copy_distribution_files(base_dists, venv_site, pyroot / "Lib" / "site-packages", True)
        cpu_file_records = _copy_distribution_files(_distributions(cpu_root / "deps"), cpu_root / "deps", staging / "cpu" / "deps", False)
        if set(cpu_file_records) - {"__excluded_nonruntime_records__"} != set(cpu_packages):
            raise BuildError("Copied CPU dependencies differ from their manifest")
        manager_source = ROOT / "tools" / "radiworks_portable_manager.py"
        if not manager_source.is_file():
            raise BuildError("Portable manager implementation is missing")
        _copy_file(manager_source, staging / "tools" / manager_source.name)
        for source_name, target_name in (("LICENSE.txt", "UPSTREAM_LICENSE_LGPL3.txt"), ("NOTICE.txt", "UPSTREAM_NOTICE.txt")):
            _copy_file(CLARKE_SOURCE.parents[1] / source_name, staging / "licenses" / target_name)
        _docs(staging, product_check, catalog, catalog_files, clarke_files, base_versions, {**cpu_manifest, "packages": cpu_packages})
        _write_json(staging / "BUILD_DEPENDENCY_FILES.json", {"base": base_file_records, "cpu": cpu_file_records})
        _launcher(staging, "start", "Start-5.cmd")
        _launcher(staging, "start --instance 01 --count 1", "Start-01.cmd")
        _launcher(staging, "start --instance 02 --count 1", "Start-02.cmd")
        _launcher(staging, "start --instance 03 --count 1", "Start-03.cmd")
        _launcher(staging, "start --instance 04 --count 1", "Start-04.cmd")
        _launcher(staging, "start --instance 05 --count 1", "Start-05.cmd")
        _launcher(staging, "status", "Status.cmd")
        _launcher(staging, "stop", "Stop-5.cmd")
        _install_bytecode_guard(pyroot)
        before_imports = _hash_tree(staging)
        _verify_embedded(pyroot / "python.exe", staging / "cpu" / "deps")
        if _hash_tree(staging) != before_imports:
            raise BuildError("Embedded import mutated package payload")
        _write_json(staging / "FILE_MANIFEST.json", {"schema": "radiworks.portable5-file-manifest.v1", "files": _hash_tree(staging, {"FILE_MANIFEST.json"})})
        staging.rename(OUTPUT)
        if make_zip:
            _make_zip(OUTPUT, OUTPUT.with_name(OUTPUT.name + ".zip"))
    except BaseException:
        raise
    return OUTPUT


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the offline RadiWorks Portable5 private test package")
    parser.add_argument("--zip", action="store_true", help="also make a compressed ZIP")
    args = parser.parse_args()
    try:
        path = build_bundle(args.zip)
        check = verify_pinned_product(path / "app")
    except (BuildError, OSError) as exc:
        print(f"Portable5 build failed: {exc}", file=sys.stderr)
        return 2
    print(f"Portable5 bundle created: {path}")
    print(f"Product manifest SHA-256: {check.digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
