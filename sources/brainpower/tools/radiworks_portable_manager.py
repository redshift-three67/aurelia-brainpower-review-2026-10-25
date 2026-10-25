from __future__ import annotations

import argparse
import ctypes
import base64
import threading
from contextlib import contextmanager
import json
import os
import shutil
import socket
import stat
import subprocess
import sys
import time
from pathlib import Path, PurePosixPath, PureWindowsPath


CREATE_NO_WINDOW = 0x08000000
CATALOG_RELEASE_ID = "e33ea136d8ea448fada7524757385ee4"
SUPPORTED_BUNDLE_LABELS = frozenset(("RadiWorks-Portable5-0.3.0-rc1", "RadiWorks-Portable5-0.4.0-rc1"))

class ManagerError(RuntimeError):
    pass


def _is_reparse(path: Path) -> bool:
    try:
        info = path.lstat()
    except FileNotFoundError:
        return False
    return stat.S_ISLNK(info.st_mode) or bool(getattr(info, "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT)


def _abs(path: Path | str) -> Path:
    result = Path(path).expanduser().resolve()
    if result.exists() and _is_reparse(result):
        raise ManagerError(f"Verknüpfter Pfad wird abgelehnt: {result}")
    return result


_HELD_BUNDLES: set[str] = set()
_HELD_BUNDLES_MUTEX = threading.Lock()


@contextmanager
def _bundle_lock(bundle_root: Path | str):
    root = _abs(bundle_root)
    state_dir = root / "state"
    state_dir.mkdir(parents=True, exist_ok=True)
    if _is_reparse(state_dir):
        raise ManagerError("Manager-Statuspfad ist ein Link")
    lock_path = state_dir / ".portable5.manager.lock"
    if lock_path.exists() and _is_reparse(lock_path):
        raise ManagerError("Manager-Lockdatei ist ein Link")
    key = os.path.normcase(os.path.normpath(str(root)))
    with _HELD_BUNDLES_MUTEX:
        if key in _HELD_BUNDLES:
            raise ManagerError("Eine andere Manageraktion bearbeitet dieses Bundle bereits")
        _HELD_BUNDLES.add(key)
    handle = None
    locked = False
    try:
        handle = lock_path.open("a+b")
        if handle.seek(0, os.SEEK_END) == 0:
            handle.write(bytes([0]))
            handle.flush()
        handle.seek(0)
        if os.name == "nt":
            import msvcrt
            msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        locked = True
        yield root
    except (OSError, ImportError) as exc:
        if locked:
            raise
        raise ManagerError("Eine andere Managerinstanz hält das Bundle-Lock") from exc
    finally:
        if handle is not None:
            if locked:
                try:
                    handle.seek(0)
                    if os.name == "nt":
                        import msvcrt
                        msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
                    else:
                        import fcntl
                        fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
                except OSError:
                    pass
            handle.close()
        with _HELD_BUNDLES_MUTEX:
            _HELD_BUNDLES.discard(key)

def _same_path(left: object, right: object) -> bool:
    if not isinstance(left, str) or not isinstance(right, str):
        return False
    import ntpath
    return ntpath.normcase(ntpath.normpath(left)) == ntpath.normcase(ntpath.normpath(right))


def build_instance_configs(
    bundle_root: Path | str,
    key_root: Path | str,
    manifest_digest: str,
    cpu_deps: Path | str | None = None,
    base_port: int = 8103,
    count: int = 5,
    first_instance: int = 1,
) -> list[dict]:
    root, keys = _abs(bundle_root), _abs(key_root)
    if not isinstance(manifest_digest, str) or len(manifest_digest) != 64 or any(c not in "0123456789abcdef" for c in manifest_digest):
        raise ManagerError("Ungültiger Manifest-Hash")
    if type(base_port) is not int or base_port < 1024 or base_port > 65535:
        raise ManagerError("Basis-Port muss zwischen 1024 und 65535 liegen")
    if type(count) is not int or not 1 <= count <= 5:
        raise ManagerError("Die Instanzanzahl muss zwischen 1 und 5 liegen")
    if type(first_instance) is not int or not 1 <= first_instance <= 5 or first_instance + count - 1 > 5:
        raise ManagerError("Instanznummern müssen zwischen 1 und 5 liegen")
    if base_port + first_instance + count - 2 > 65535:
        raise ManagerError("Portbereich überschreitet 65535")
    cpu = _abs(cpu_deps) if cpu_deps is not None else (root / "cpu" / "deps").resolve()
    if root == keys or root in keys.parents:
        raise ManagerError("Fernet-Schlüssel müssen außerhalb des Pakets liegen")
    configs = []
    for number in range(first_instance, first_instance + count):
        home = root / "state" / "instances" / f"{number:02d}"
        configs.append({
            "schema": 1,
            "sourceDir": str(root / "app"),
            "manifestDigest": manifest_digest,
            "home": str(home),
            "data": str(root / "data" / "catalog-releases" / CATALOG_RELEASE_ID / "data"),
            "materia": str(root / "data" / "materia" / "Clarke"),
            "port": base_port + number - 1,
            "tenant": f"portable5-{number:02d}",
            "client": f"instance-{number:02d}",
            "job": f"localtest-{number:02d}",
            "keyFile": str(keys / f"instance-{number:02d}.fernet"),
            "cpuDeps": str(cpu),
        })
    return configs


def _command_args(command_line: object) -> list[str] | None:
    if isinstance(command_line, list) and all(isinstance(value, str) for value in command_line):
        return command_line
    if not isinstance(command_line, str) or not command_line:
        return None
    if os.name == "nt":
        argc = ctypes.c_int()
        shell32, kernel32 = ctypes.windll.shell32, ctypes.windll.kernel32
        shell32.CommandLineToArgvW.restype = ctypes.POINTER(ctypes.c_wchar_p)
        shell32.CommandLineToArgvW.argtypes = [ctypes.c_wchar_p, ctypes.POINTER(ctypes.c_int)]
        kernel32.LocalFree.argtypes = [ctypes.c_void_p]
        pointer = shell32.CommandLineToArgvW(command_line, ctypes.byref(argc))
        if not pointer:
            return None
        try:
            return [pointer[index] for index in range(argc.value)]
        finally:
            kernel32.LocalFree(pointer)
    import shlex
    try:
        return shlex.split(command_line)
    except ValueError:
        return None


def is_owned_service(state: object, process: object, listener_pid: object, expected: dict) -> bool:
    if not isinstance(state, dict) or not isinstance(process, dict) or not isinstance(expected, dict):
        return False
    try:
        pid = int(state["pid"])
        created = float(process["createdEpoch"])
        started = float(state["startedEpoch"])
    except (KeyError, TypeError, ValueError):
        return False
    if pid <= 0 or pid != int(process.get("pid", -1)) or pid != listener_pid:
        return False
    if started < created or started - created > 120:
        return False
    for key in ("home", "sourceDir", "manifestDigest", "port"):
        if state.get(key) != expected.get(key):
            return False
    if not _same_path(process.get("imagePath"), expected.get("pythonw")):
        return False
    argv = _command_args(process.get("commandLine"))
    if argv is None or len(argv) != 4:
        return False
    return (
        _same_path(argv[0], expected.get("pythonw"))
        and _same_path(argv[1], expected.get("serviceScript"))
        and argv[2] == "--config"
        and _same_path(argv[3], expected.get("configPath"))
    )


def _sha256(path: Path) -> str:
    import hashlib
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _safe_rel(raw: object) -> str:
    if not isinstance(raw, str) or not raw or "\x00" in raw or "\\" in raw:
        raise ManagerError(f"Ungültiger Paketpfad: {raw!r}")
    posix, windows = PurePosixPath(raw), PureWindowsPath(raw)
    if posix.is_absolute() or windows.is_absolute() or windows.drive or any(part in ("", ".", "..") or part.endswith((".", " ")) or ":" in part for part in raw.split("/")):
        raise ManagerError(f"Unsicherer Paketpfad: {raw!r}")
    return posix.as_posix()


def _inside(root: Path, rel: str) -> Path:
    safe = _safe_rel(rel)
    current = root
    for part in PurePosixPath(safe).parts:
        current = current / part
        if current.exists() and _is_reparse(current):
            raise ManagerError(f"Verknüpfter Paketpfad: {current}")
    result = current.resolve()
    if result != root and root not in result.parents:
        raise ManagerError(f"Paketpfad verlässt die Wurzel: {rel}")
    return result


def _payload_files(root: Path) -> dict[str, tuple[int, str]]:
    result = {}
    def walk_error(error):
        raise ManagerError(f"Paketverzeichnis kann nicht gelesen werden: {error.filename}") from error
    for parent, directories, files in os.walk(root, topdown=True, followlinks=False, onerror=walk_error):
        parent = Path(parent)
        for name in list(directories):
            path = parent / name
            rel = _safe_rel(path.relative_to(root).as_posix())
            if _is_reparse(path):
                raise ManagerError(f"Verknüpftes Paketverzeichnis: {rel}")
            if parent == root and name.casefold() == "state":
                directories.remove(name)
        for name in files:
            path = parent / name
            rel = _safe_rel(path.relative_to(root).as_posix())
            info = path.lstat()
            if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT:
                raise ManagerError(f"Verknüpfter Paketinhalt: {rel}")
            if not stat.S_ISREG(info.st_mode):
                raise ManagerError(f"Nicht regulärer Paketinhalt: {rel}")
            if rel == "FILE_MANIFEST.json":
                continue
            key = rel.casefold()
            if key in result:
                raise ManagerError(f"Doppelter Paketinhalt: {rel}")
            result[key] = (info.st_size, _sha256(path))
    return result


def _verify_product(root: Path, version: dict) -> tuple[str, int]:
    source = root / "app"
    manifest_path = source / "PRODUCT_MANIFEST.json"
    if not manifest_path.is_file():
        raise ManagerError("Produktmanifest fehlt")
    raw = manifest_path.read_bytes()
    import hashlib
    digest = hashlib.sha256(raw).hexdigest()
    if digest != version.get("productManifestDigest"):
        raise ManagerError("Produktmanifest-Hash passt nicht zu VERSION.json")
    try:
        data = json.loads(raw.decode("utf-8-sig"))
        entries = data["files"]
    except (UnicodeDecodeError, json.JSONDecodeError, KeyError, TypeError) as exc:
        raise ManagerError("Produktmanifest ist ungültig") from exc
    if not isinstance(entries, list) or not entries or len(entries) > 10000:
        raise ManagerError("Produktmanifest-Dateiliste ungültig")
    seen = set()
    for item in entries:
        if not isinstance(item, dict):
            raise ManagerError("Ungültiger Produktmanifest-Eintrag")
        rel = _safe_rel(item.get("path"))
        if rel.casefold() in seen:
            raise ManagerError(f"Doppelter Manifestpfad: {rel}")
        seen.add(rel.casefold())
        path = _inside(source, rel)
        if not path.is_file() or _sha256(path) != str(item.get("sha256", "")).lower():
            raise ManagerError(f"Produktdatei fehlt oder wurde verändert: {rel}")
        if "bytes" in item and path.stat().st_size != item["bytes"]:
            raise ManagerError(f"Produktdateigröße abweichend: {rel}")
    return digest, len(entries)


def verify_bundle(bundle_root: Path | str | None = None) -> dict:
    root = _abs(bundle_root or Path(__file__).resolve().parents[1])
    try:
        version = json.loads((root / "VERSION.json").read_text(encoding="utf-8"))
        manifest = json.loads((root / "FILE_MANIFEST.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ManagerError("Bundle-Version oder Dateimanifest fehlt/ist ungültig") from exc
    if not isinstance(version, dict) or not isinstance(manifest, dict):
        raise ManagerError("Bundle-Version und Manifest müssen Objekte sein")
    if version.get("bundleLabel") not in SUPPORTED_BUNDLE_LABELS:
        raise ManagerError("Unerwartetes Bundle-Label")
    if manifest.get("schema") != "radiworks.portable5-file-manifest.v1" or not isinstance(manifest.get("files"), list):
        raise ManagerError("Ungültiges Bundle-Dateimanifest")
    expected = {}
    for item in manifest["files"]:
        rel = _safe_rel(item.get("path") if isinstance(item, dict) else None)
        if rel.casefold() in expected:
            raise ManagerError(f"Doppelter Bundlepfad: {rel}")
        size, digest = item.get("bytes"), item.get("sha256")
        if type(size) is not int or size < 0 or not isinstance(digest, str) or len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            raise ManagerError(f"Ungültige Größe oder SHA-256 im Bundlemanifest: {rel}")
        expected[rel.casefold()] = (size, digest)
    actual = _payload_files(root)
    if expected != actual:
        missing = sorted(set(expected) - set(actual))[:5]
        extra = sorted(set(actual) - set(expected))[:5]
        raise ManagerError(f"Bundle-Dateiliste weicht ab (fehlend={missing}, zusätzlich={extra})")
    digest, count = _verify_product(root, version)
    for rel in ("python/python.exe", "python/pythonw.exe", "python/python313._pth", "app/service.py",
                f"data/catalog-releases/{CATALOG_RELEASE_ID}/data", "data/materia/Clarke", "cpu/deps"):
        if not (root / rel).exists():
            raise ManagerError(f"Bundle-Baustein fehlt: {rel}")
    return {"root": root, "version": version, "manifestDigest": digest, "productFileCount": count, "payloadFileCount": len(expected)}


def _key_root() -> Path:
    local = os.environ.get("LOCALAPPDATA") or str(Path.home() / "AppData" / "Local")
    # Keep the historical namespace so same-machine upgrades can retain their recovery keys.
    return Path(local) / "RadiWorks" / "Portable5-0.3.0-rc1" / "keys"


def _check_vc_runtime() -> None:
    if os.name != "nt":
        return
    system = Path(os.environ.get("SYSTEMROOT", r"C:\Windows")) / "System32"
    required = ("MSVCP140.dll", "MSVCP140_ATOMIC_WAIT.dll")
    for name in required:
        path = system / name
        try:
            if not path.is_file():
                raise OSError("missing DLL")
            ctypes.WinDLL(str(path))
        except OSError as exc:
            raise ManagerError(
                f"Microsoft Visual C++ v14 x64 Runtime fehlt oder ist defekt ({name}). "
                "Installiere es manuell vor dem Start: "
                "https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist?view=msvc-170 "
                "(x64: https://aka.ms/vc14/vc_redist.x64.exe)."
            ) from exc

def _validate_acl_report(report: object, owner_sid: str, directory: bool) -> bool:
    if not isinstance(report, dict) or report.get("ownerSid") != owner_sid or report.get("protected") is not True:
        return False
    rules = report.get("rules")
    if not isinstance(rules, list) or len(rules) != 3:
        return False
    expected = {owner_sid, "S-1-5-18", "S-1-5-32-544"}
    seen = set()
    expected_inheritance = {"ContainerInherit", "ObjectInherit"} if directory else set()
    for rule in rules:
        if not isinstance(rule, dict):
            return False
        sid = rule.get("sid")
        inheritance = {item.strip() for item in str(rule.get("inheritance", "")).split(",") if item.strip() and item.strip() != "None"}
        if (
            sid not in expected or sid in seen
            or rule.get("type") != "Allow"
            or rule.get("rights") != "FullControl"
            or rule.get("propagation") != "None"
            or rule.get("inherited") is not False
            or inheritance != expected_inheritance
        ):
            return False
        seen.add(sid)
    return seen == expected


def _run_hidden(args: list[str], **kwargs):
    flags = int(kwargs.pop("creationflags", 0))
    if os.name == "nt":
        flags |= CREATE_NO_WINDOW
    kwargs["creationflags"] = flags
    return subprocess.run(args, **kwargs)


def _acl_command(path: Path, directory: bool) -> None:
    if os.name != "nt":
        raise ManagerError("Die Fernet-Key-ACL kann nur unter Windows eingerichtet werden")
    target = str(path.resolve()).replace("'", "''")
    is_dir = "$true" if directory else "$false"
    script = f"""
$ErrorActionPreference = 'Stop'
$target = '{target}'
$isDirectory = {is_dir}
$owner = [Security.Principal.WindowsIdentity]::GetCurrent().User
$acl = if ($isDirectory) {{ New-Object System.Security.AccessControl.DirectorySecurity }} else {{ New-Object System.Security.AccessControl.FileSecurity }}
$acl.SetAccessRuleProtection($true, $false)
$acl.SetOwner($owner)
$inheritance = [System.Security.AccessControl.InheritanceFlags]::None
if ($isDirectory) {{ $inheritance = [System.Security.AccessControl.InheritanceFlags]::ContainerInherit -bor [System.Security.AccessControl.InheritanceFlags]::ObjectInherit }}
foreach ($sidText in @($owner.Value, 'S-1-5-18', 'S-1-5-32-544')) {{
    $sid = New-Object System.Security.Principal.SecurityIdentifier($sidText)
    $rule = [System.Security.AccessControl.FileSystemAccessRule]::new($sid, [System.Security.AccessControl.FileSystemRights]::FullControl, $inheritance, [System.Security.AccessControl.PropagationFlags]::None, [System.Security.AccessControl.AccessControlType]::Allow)
    [void]$acl.AddAccessRule($rule)
}}
if ($isDirectory) {{ [System.IO.Directory]::SetAccessControl($target, $acl); $check = [System.IO.Directory]::GetAccessControl($target) }}
else {{ [System.IO.File]::SetAccessControl($target, $acl); $check = [System.IO.File]::GetAccessControl($target) }}
$rules = @($check.GetAccessRules($true, $true, [System.Security.Principal.SecurityIdentifier]) | ForEach-Object {{
    [pscustomobject]@{{sid=$_.IdentityReference.Value;type=$_.AccessControlType.ToString();rights=$_.FileSystemRights.ToString();inheritance=$_.InheritanceFlags.ToString();propagation=$_.PropagationFlags.ToString();inherited=[bool]$_.IsInherited}}
}})
[pscustomobject]@{{ownerSid=$check.GetOwner([System.Security.Principal.SecurityIdentifier]).Value;currentSid=$owner.Value;protected=[bool]$check.AreAccessRulesProtected;rules=$rules}} | ConvertTo-Json -Depth 5 -Compress
"""
    report = _powershell_json(script)
    if not isinstance(report, dict) or not _validate_acl_report(report, str(report.get("currentSid", "")), directory):
        raise ManagerError("Key-DACL-Readback ist nicht die exakte Owner/SYSTEM/Administrators-Allowlist")


def _ensure_key(path: Path, key_root: Path) -> None:
    key_root.mkdir(parents=True, exist_ok=True)
    if _is_reparse(key_root):
        raise ManagerError("Key-Verzeichnis ist ein Link")
    _acl_command(key_root, True)
    if path.exists():
        if _is_reparse(path):
            raise ManagerError(f"Key-Datei ist ein Link: {path.name}")
        value = path.read_bytes().strip()
        if len(value) != 44:
            raise ManagerError(f"Vorhandene Key-Datei ist ungültig: {path.name}")
        try:
            from cryptography.fernet import Fernet
            Fernet(value)
        except Exception as exc:
            raise ManagerError(f"Vorhandene Key-Datei ist ungültig: {path.name}") from exc
        _acl_command(path, False)
        return
    from cryptography.fernet import Fernet
    value = Fernet.generate_key()
    with path.open("xb") as target:
        target.write(value)
    try:
        _acl_command(path, False)
    except ManagerError:
        path.unlink(missing_ok=True)
        raise


def _ports_free(ports: list[int]) -> None:
    occupied = []
    for port in ports:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            if os.name == "nt":
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
            sock.bind(("127.0.0.1", port))
        except OSError:
            occupied.append(port)
        finally:
            sock.close()
    if occupied:
        raise ManagerError(f"Ports sind nicht frei; es wurde nichts gestartet: {occupied}")


def _powershell() -> str:
    return shutil.which("powershell.exe") or shutil.which("powershell") or "powershell.exe"


def _powershell_json(command: str) -> object | None:
    command = "[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false); " + command
    encoded = base64.b64encode(command.encode("utf-16le")).decode("ascii")
    result = _run_hidden([_powershell(), "-NoProfile", "-NonInteractive", "-EncodedCommand", encoded],
                         capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=20)
    if result.returncode:
        raise ManagerError("Windows-Prozess-/Portidentität konnte nicht sicher gelesen werden")
    raw = result.stdout.strip()
    if not raw:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ManagerError("Ungültige Antwort der Windows-Prozessabfrage") from exc

def _process_info(pid: int) -> dict | None:
    if type(pid) is not int or pid <= 0:
        return None
    script = (
        f"$p=Get-CimInstance Win32_Process -Filter 'ProcessId = {pid}'; "
        "if($null -ne $p){$ft=([datetime]$p.CreationDate).ToUniversalTime().ToFileTimeUtc(); "
        "[pscustomobject]@{pid=[int]$p.ProcessId;createdFileTime=[string]$ft;"
        "createdEpoch=([double]$ft/10000000.0-11644473600.0);"
        "imagePath=[string]$p.ExecutablePath;commandLine=[string]$p.CommandLine}|ConvertTo-Json -Compress}"
    )
    result = _powershell_json(script)
    return result if isinstance(result, dict) else None


def _listener_pids(port: int) -> list[int]:
    script = (
        "$ErrorActionPreference='Stop'; "
        "try {$items=@(Get-NetTCPConnection -State Listen -ErrorAction Stop)} "
        "catch {if ($_.FullyQualifiedErrorId -eq 'CmdletizationQuery_NotFound,Get-NetTCPConnection' "
        "-and $_.CategoryInfo.Category -eq [System.Management.Automation.ErrorCategory]::ObjectNotFound) "
        "{$items=@()} else {throw}}; "
        f"$owners=@($items | Where-Object {{$_.LocalPort -eq {int(port)}}} "
        "| Select-Object -ExpandProperty OwningProcess -Unique); "
        "ConvertTo-Json -InputObject $owners -Compress"
    )
    result = _powershell_json(script)
    if not isinstance(result, list) or any(type(pid) is not int or pid <= 0 for pid in result):
        raise ManagerError(f"Listener auf Port {port} konnte nicht sicher bestimmt werden")
    return result


def _expected(config: dict, root: Path) -> dict:
    return {
        "home": config["home"], "sourceDir": config["sourceDir"],
        "manifestDigest": config["manifestDigest"], "port": config["port"],
        "pythonw": str(root / "python" / "pythonw.exe"),
        "serviceScript": str(root / "app" / "service.py"),
        "configPath": str(Path(config["home"]) / "service-config.json"),
    }


def _load_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    if _is_reparse(path):
        raise ManagerError(f"Verknüpfte Statusdatei abgelehnt: {path.name}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ManagerError(f"Statusdatei unlesbar: {path.name}") from exc
    return value if isinstance(value, dict) else None


def _state_path(config: dict) -> Path:
    return Path(config["home"]) / "service-state.json"


def _owner_path(config: dict) -> Path:
    return Path(config["home"]) / "manager-owner.json"


def _same_state(state: dict, config: dict) -> bool:
    return (
        state.get("home") == config["home"]
        and state.get("sourceDir") == config["sourceDir"]
        and state.get("manifestDigest") == config["manifestDigest"]
        and state.get("port") == config["port"]
    )


def _owner_matches(owner: dict | None, process: dict, state: dict, config: dict) -> bool:
    return bool(
        isinstance(owner, dict)
        and owner.get("pid") == state.get("pid") == process.get("pid")
        and owner.get("createdFileTime") == process.get("createdFileTime")
        and owner.get("home") == config["home"]
        and owner.get("sourceDir") == config["sourceDir"]
        and owner.get("manifestDigest") == config["manifestDigest"]
        and owner.get("port") == config["port"]
    )


def _owner_matches_stopped(owner: dict | None, state: dict, config: dict) -> bool:
    return bool(
        isinstance(owner, dict)
        and owner.get("pid") == state.get("pid")
        and owner.get("home") == config["home"]
        and owner.get("sourceDir") == config["sourceDir"]
        and owner.get("manifestDigest") == config["manifestDigest"]
        and owner.get("port") == config["port"]
        and isinstance(owner.get("createdFileTime"), str)
    )


def _write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    if temporary.exists() and _is_reparse(temporary):
        raise ManagerError(f"Verknüpfte temporäre Datei abgelehnt: {temporary.name}")
    temporary.write_text(json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    temporary.replace(path)


def _write_owner(config: dict, process: dict) -> None:
    _write_json(_owner_path(config), {
        "pid": process["pid"], "createdFileTime": process["createdFileTime"],
        "createdEpoch": process["createdEpoch"], "home": config["home"],
        "sourceDir": config["sourceDir"], "manifestDigest": config["manifestDigest"],
        "port": config["port"],
    })


def _owned(config: dict, root: Path, require_listener: bool = True) -> tuple[dict, dict, dict] | None:
    state = _load_json(_state_path(config))
    if not state or not _same_state(state, config):
        return None
    try:
        pid = int(state["pid"])
    except (KeyError, ValueError, TypeError):
        return None
    process = _process_info(pid)
    if process is None:
        return None
    listeners = _listener_pids(config["port"])
    listener = listeners[0] if len(listeners) == 1 else None
    if not require_listener and listener is None:
        listener = pid
    expected = _expected(config, root)
    if not is_owned_service(state, process, listener, expected):
        return None
    owner = _load_json(_owner_path(config))
    if not _owner_matches(owner, process, state, config):
        return None
    return state, process, owner


def _write_stop_flag(config: dict) -> None:
    home = Path(config["home"])
    home.mkdir(parents=True, exist_ok=True)
    flag = home / "service.stop"
    if flag.exists():
        if _is_reparse(flag):
            raise ManagerError("Stop-Datei ist ein Link")
        return
    with flag.open("x", encoding="ascii") as stream:
        stream.write("manager-requested\n")


def _wait_for_stop(config: dict, root: Path, timeout: float) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        state = _load_json(_state_path(config))
        if not state or not _same_state(state, config):
            raise ManagerError("Service-Identität änderte sich während des Stopps")
        try:
            pid = int(state["pid"])
        except (KeyError, TypeError, ValueError) as exc:
            raise ManagerError("Service-PID ist ungültig") from exc
        process = _process_info(pid)
        listeners = _listener_pids(config["port"])
        if process is None and not listeners:
            final_state = _load_json(_state_path(config))
            if final_state and final_state.get("exitClean") is True and final_state.get("stoppedEpoch") and _same_state(final_state, config):
                return
            raise ManagerError("Service endete ohne bestätigten clean shutdown")
        if _owned(config, root, require_listener=bool(listeners)) is None:
            raise ManagerError("Service-Identität änderte sich; Stop wurde beendet")
        time.sleep(0.25)
    raise ManagerError(f"Geordneter Stopp überschritt {timeout:g}s; Stop-Flag bleibt erhalten")


def _stop_one(config: dict, root: Path, timeout: float) -> str:
    state = _load_json(_state_path(config))
    flag = Path(config["home"]) / "service.stop"
    if not state:
        if flag.exists():
            raise ManagerError("Stop-Flag ohne verifizierbare Service-Identität bleibt unangetastet")
        return "nicht gestartet"
    if not _same_state(state, config):
        raise ManagerError("Service-Identität gehört nicht zu dieser Instanz-/Portkonfiguration")
    pid = state.get("pid")
    process = _process_info(pid) if type(pid) is int else None
    if process is None:
        if state.get("exitClean") is True and state.get("stoppedEpoch") and not _listener_pids(config["port"]):
            return "bereits sauber beendet"
        if _listener_pids(config["port"]):
            raise ManagerError("Port belegt, Prozessidentität fehlt; fremder Prozess bleibt unangetastet")
        return "Prozess beendet, Shutdown nicht sauber bestätigt"
    if _owned(config, root) is None:
        raise ManagerError("Eigentum nicht sicher belegt; fremder oder veränderter Prozess bleibt unangetastet")
    _write_stop_flag(config)
    _wait_for_stop(config, root, timeout)
    return "geordnet beendet"


def _preflight_slot(config: dict, root: Path) -> None:
    home = Path(config["home"])
    if home.exists() and _is_reparse(home):
        raise ManagerError(f"Instanz-Home ist Link: {home}")
    state = _load_json(_state_path(config))
    flag = home / "service.stop"
    if flag.exists():
        if _is_reparse(flag):
            raise ManagerError(f"Stop-Datei ist Link: {home.name}")
        if not state or not _same_state(state, config):
            raise ManagerError("Persistentes Stop-Flag ohne passende Service-Identität")
        pid = state.get("pid")
        process = _process_info(pid) if type(pid) is int else None
        if process is not None:
            if _owned(config, root) is not None:
                raise ManagerError(f"Instanz läuft bereits auf Port {config['port']}")
            raise ManagerError("Stop-Flag gehört zu einem nicht verifizierbaren aktiven Prozess")
        owner = _load_json(_owner_path(config))
        if state.get("exitClean") is not True or not state.get("stoppedEpoch") or not _owner_matches_stopped(owner, state, config):
            raise ManagerError("Stop-Flag bleibt ohne bestätigten geordneten Vorstopp bestehen")
        flag.unlink()
    elif state:
        pid = state.get("pid")
        process = _process_info(pid) if type(pid) is int else None
        if process is not None:
            if _owned(config, root) is not None:
                raise ManagerError(f"Instanz läuft bereits auf Port {config['port']}")
            raise ManagerError("Instanz-PID existiert, Eigentum ist nicht belegt")
        if _listener_pids(config["port"]):
            raise ManagerError(f"Port {config['port']} gehört nicht zu einem nachweisbaren Service")


def _write_config(config: dict) -> None:
    home = Path(config["home"])
    home.mkdir(parents=True, exist_ok=True)
    (home / "tmp").mkdir(parents=True, exist_ok=True)
    if _is_reparse(home):
        raise ManagerError(f"Instanz-Home ist Link: {home}")
    _write_json(home / "service-config.json", config)


def _spawn(config: dict, root: Path) -> subprocess.Popen:
    pythonw = root / "python" / "pythonw.exe"
    service = root / "app" / "service.py"
    cfg_path = Path(config["home"]) / "service-config.json"
    if not pythonw.is_file() or not service.is_file():
        raise ManagerError("Embedded Python oder Release-Wrapper fehlt")
    temp = Path(config["home"]) / "tmp"
    temp.mkdir(parents=True, exist_ok=True)
    windir = os.environ.get("SYSTEMROOT", r"C:\Windows")
    env = {
        "SYSTEMROOT": windir, "WINDIR": windir,
        "PATH": str(root / "python") + os.pathsep + windir + r"\System32",
        "TEMP": str(temp), "TMP": str(temp), "PYTHONNOUSERSITE": "1",
    }
    for name in ("LOCALAPPDATA", "USERPROFILE", "HOMEDRIVE", "HOMEPATH"):
        if name in os.environ:
            env[name] = os.environ[name]
    flags = getattr(subprocess, "DETACHED_PROCESS", 0x00000008) | getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0x00000200)
    return subprocess.Popen(
        [str(pythonw), str(service), "--config", str(cfg_path)],
        cwd=str(root), env=env, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL, close_fds=True, creationflags=flags,
    )


def _matches_spawned(process: dict | None, pid: int, launched_epoch: float, expected: dict) -> bool:
    if not isinstance(process, dict) or process.get("pid") != pid:
        return False
    try:
        created = float(process["createdEpoch"])
    except (KeyError, TypeError, ValueError):
        return False
    argv = _command_args(process.get("commandLine"))
    return bool(
        launched_epoch - 2 <= created <= time.time() + 2
        and _same_path(process.get("imagePath"), expected.get("pythonw"))
        and argv is not None and len(argv) == 4
        and _same_path(argv[0], expected.get("pythonw"))
        and _same_path(argv[1], expected.get("serviceScript"))
        and argv[2] == "--config"
        and _same_path(argv[3], expected.get("configPath"))
    )


def _wait_for_start(config: dict, root: Path, child: subprocess.Popen, launched_epoch: float, timeout: float) -> dict:
    deadline = time.monotonic() + timeout
    expected = _expected(config, root)
    while time.monotonic() < deadline:
        if child.poll() is not None:
            raise ManagerError(f"{Path(config['home']).name} wurde beim Start beendet; Details im Release-Service-Log")
        state = _load_json(_state_path(config))
        if state and _same_state(state, config):
            process = _process_info(child.pid)
            listeners = _listener_pids(config["port"])
            listener = listeners[0] if len(listeners) == 1 else None
            if is_owned_service(state, process, listener, expected):
                if process is None or float(process["createdEpoch"]) < launched_epoch - 2:
                    raise ManagerError("Prozessstartzeit stimmt nicht mit dem gestarteten Child überein")
                _write_owner(config, process)
                return state
        time.sleep(0.25)
    raise ManagerError(f"{Path(config['home']).name} nicht innerhalb {timeout:g}s betriebsbereit")


def _rollback_spawned(children: list[tuple[dict, subprocess.Popen, float]], root: Path, timeout: float) -> list[str]:
    problems = []
    for config, child, launched_epoch in reversed(children):
        label = Path(config["home"]).name
        try:
            if child.poll() is not None:
                continue
            state = _load_json(_state_path(config))
            if state and _owned(config, root) is not None:
                _write_stop_flag(config)
                _wait_for_stop(config, root, timeout)
                continue
            process = _process_info(child.pid)
            if _matches_spawned(process, child.pid, launched_epoch, _expected(config, root)):
                _write_stop_flag(config)
                child.wait(timeout=timeout)
                if _process_info(child.pid) is not None or _listener_pids(config["port"]):
                    problems.append(f"{label}: blieb nach Rollback aktiv")
            else:
                problems.append(f"{label}: nicht sicher als eigener Prozess erkennbar")
        except Exception as exc:
            problems.append(f"{label}: rollback verification failed ({type(exc).__name__})")
    return problems

def _start_instances_locked(root: Path, base_port: int = 8103, count: int = 5, first_instance: int = 1, timeout: float = 90.0) -> list[dict]:
    _check_vc_runtime()
    verified = verify_bundle(root)
    root = verified["root"]
    key_root = _key_root().resolve()
    configs = build_instance_configs(root, key_root, verified["manifestDigest"], root / "cpu" / "deps",
                                     base_port=base_port, count=count, first_instance=first_instance)
    for rel in (f"data/catalog-releases/{CATALOG_RELEASE_ID}/data", "data/materia/Clarke", "cpu/deps"):
        if not (root / rel).is_dir():
            raise ManagerError(f"Paketpfad fehlt: {rel}")
    _ports_free([item["port"] for item in configs])
    for config in configs:
        _preflight_slot(config, root)
    children: list[tuple[dict, subprocess.Popen, float]] = []
    states = []
    try:
        for config in configs:
            _ensure_key(Path(config["keyFile"]), key_root)
            _write_config(config)
            launched = time.time()
            child = _spawn(config, root)
            children.append((config, child, launched))
            states.append(_wait_for_start(config, root, child, launched, timeout))
        return states
    except (ManagerError, OSError, subprocess.SubprocessError) as exc:
        failures = _rollback_spawned(children, root, min(timeout, 30.0))
        suffix = f"; Rollback-Probleme: {failures}" if failures else "; selbst gestartete Instanzen wurden geordnet zurückgerollt"
        raise ManagerError(f"Start abgebrochen: {exc}{suffix}") from exc


def _status_instances_locked(root: Path, base_port: int = 8103, count: int = 5, first_instance: int = 1) -> list[str]:
    verified = verify_bundle(root)
    root = verified["root"]
    configs = build_instance_configs(root, _key_root(), verified["manifestDigest"], root / "cpu" / "deps",
                                     base_port=base_port, count=count, first_instance=first_instance)
    results = []
    for config in configs:
        label = Path(config["home"]).name
        state = _load_json(_state_path(config))
        if not state:
            results.append(f"{label} Port {config['port']}: nicht gestartet")
        elif not _same_state(state, config):
            results.append(f"{label} Port {config['port']}: Identität weicht ab; keine Aktion")
        else:
            pid = state.get("pid")
            process = _process_info(pid) if type(pid) is int else None
            if process is None:
                status = "sauber beendet" if state.get("exitClean") is True else "Prozess beendet, Shutdownstatus unbestätigt"
                results.append(f"{label} Port {config['port']}: {status}")
            elif _owned(config, root) is not None:
                results.append(f"{label} Port {config['port']}: läuft (PID {pid}), eigene Identität bestätigt")
            else:
                results.append(f"{label} Port {config['port']}: Prozess läuft, Eigentum/Listener nicht bestätigt")
    return results


def _stop_instances_locked(root: Path, base_port: int = 8103, count: int = 5, first_instance: int = 1, timeout: float = 45.0) -> list[str]:
    verified = verify_bundle(root)
    root = verified["root"]
    configs = build_instance_configs(root, _key_root(), verified["manifestDigest"], root / "cpu" / "deps",
                                     base_port=base_port, count=count, first_instance=first_instance)
    results, errors = [], []
    for config in configs:
        try:
            results.append(f"{Path(config['home']).name} Port {config['port']}: {_stop_one(config, root, timeout)}")
        except ManagerError as exc:
            errors.append(f"{Path(config['home']).name} Port {config['port']}: {exc}")
    if errors:
        raise ManagerError("; ".join(errors))
    return results


def start_instances(root: Path, base_port: int = 8103, count: int = 5, first_instance: int = 1, timeout: float = 90.0) -> list[dict]:
    with _bundle_lock(root) as locked_root:
        return _start_instances_locked(locked_root, base_port, count, first_instance, timeout)


def status_instances(root: Path, base_port: int = 8103, count: int = 5, first_instance: int = 1) -> list[str]:
    with _bundle_lock(root) as locked_root:
        return _status_instances_locked(locked_root, base_port, count, first_instance)


def stop_instances(root: Path, base_port: int = 8103, count: int = 5, first_instance: int = 1, timeout: float = 45.0) -> list[str]:
    with _bundle_lock(root) as locked_root:
        return _stop_instances_locked(locked_root, base_port, count, first_instance, timeout)

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="RadiWorks Portable5 Manager")
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("start", "status", "stop"):
        sub = commands.add_parser(name)
        sub.add_argument("--base-port", type=int, default=8103)
        sub.add_argument("--count", type=int, default=None)
        sub.add_argument("--instance", type=int, choices=range(1, 6), default=None)
        if name in ("start", "stop"):
            sub.add_argument("--timeout", type=float, default=90.0 if name == "start" else 45.0)
    commands.add_parser("verify")
    args = parser.parse_args(argv)
    root = Path(__file__).resolve().parents[1]
    try:
        if args.command == "verify":
            result = verify_bundle(root)
            print(f"Paketprüfung OK: {result['payloadFileCount']} Dateien; Produktmanifest {result['manifestDigest']}")
            return 0
        first = args.instance or 1
        count = args.count if args.count is not None else (1 if args.instance else 5)
        if type(count) is not int or not 1 <= count <= 5 or first + count - 1 > 5:
            raise ManagerError("--count muss 1..5 sein und in Instanz 1..5 passen")
        if args.command == "start":
            states = start_instances(root, args.base_port, count, first, args.timeout)
            for state in states:
                print(f"Instanz {Path(state['home']).name} gestartet: http://127.0.0.1:{state['port']}")
        elif args.command == "status":
            for line in status_instances(root, args.base_port, count, first):
                print(line)
        else:
            for line in stop_instances(root, args.base_port, count, first, args.timeout):
                print(line)
        return 0
    except (ManagerError, OSError, subprocess.SubprocessError) as exc:
        print(f"Portable5: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
