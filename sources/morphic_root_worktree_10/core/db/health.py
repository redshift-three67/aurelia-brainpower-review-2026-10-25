from __future__ import annotations

import importlib.metadata
import importlib.util
import re
import sqlite3
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping


_TABLE_NAME_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


@dataclass(frozen=True)
class DatabaseSpec:
    key: str
    file_name: str
    min_table_rows: Mapping[str, int]
    required: bool = True
    allow_empty: bool = False


CORE_DATABASE_SPECS: tuple[DatabaseSpec, ...] = (
    DatabaseSpec(
        key="descriptions",
        file_name="descriptions.db",
        min_table_rows={"items": 1000, "descriptions": 1},
    ),
    DatabaseSpec(
        key="item_descriptions",
        file_name="item_descriptions.db",
        min_table_rows={"item_descriptions": 0},
        required=False,
    ),
    DatabaseSpec(
        key="remedies",
        file_name="remedies.db",
        min_table_rows={"remedies": 1000, "remedy_keywords": 1000},
    ),
    DatabaseSpec(
        key="resonance",
        file_name="resonance.db",
        min_table_rows={},
        required=False,
        allow_empty=True,
    ),
)


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _validate_table_name(table: str) -> None:
    if not _TABLE_NAME_RE.match(table):
        raise ValueError(f"Unsafe SQLite table name: {table!r}")


def table_count(db_path: Path, table: str) -> int:
    """Return row count for a trusted SQLite table name."""
    _validate_table_name(table)
    with sqlite3.connect(db_path) as conn:
        cursor = conn.execute(f'SELECT COUNT(*) FROM "{table}"')
        return int(cursor.fetchone()[0])


def _sqlite_table_names(db_path: Path) -> list[str]:
    with sqlite3.connect(db_path) as conn:
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name"
        )
        return [str(row[0]) for row in cursor.fetchall()]


def _check_database(data_dir: Path, spec: DatabaseSpec) -> dict[str, Any]:
    db_path = data_dir / spec.file_name
    warnings: list[str] = []
    errors: list[str] = []
    tables: dict[str, int] = {}

    status: dict[str, Any] = {
        "key": spec.key,
        "file": spec.file_name,
        "path": str(db_path),
        "required": spec.required,
        "exists": db_path.exists(),
        "size_bytes": db_path.stat().st_size if db_path.exists() else 0,
        "tables": tables,
        "warnings": warnings,
        "errors": errors,
        "ok": True,
    }

    if not db_path.exists():
        message = f"Missing database: {db_path}"
        (errors if spec.required else warnings).append(message)
        status["ok"] = not spec.required
        return status

    if status["size_bytes"] == 0:
        message = f"Empty database file: {db_path}"
        if spec.allow_empty:
            status["empty_allowed"] = True
            return status
        if not spec.required:
            warnings.append(message)
            return status
        errors.append(message)
        status["ok"] = False
        return status

    try:
        with sqlite3.connect(db_path) as conn:
            integrity = conn.execute("PRAGMA integrity_check").fetchone()
            if not integrity or str(integrity[0]).lower() != "ok":
                errors.append(f"SQLite integrity_check failed for {db_path}")

        available_tables = set(_sqlite_table_names(db_path))
        for table, minimum in spec.min_table_rows.items():
            if table not in available_tables:
                errors.append(f"Missing table {table!r} in {db_path}")
                continue
            count = table_count(db_path, table)
            tables[table] = count
            if count < minimum:
                errors.append(
                    f"{spec.file_name}:{table} has {count} rows, expected at least {minimum}"
                )
    except sqlite3.Error as exc:
        errors.append(f"SQLite error for {db_path}: {exc}")

    status["ok"] = not errors
    return status


def collect_core_database_health(data_dir: Path | None = None) -> dict[str, Any]:
    data_dir = Path(data_dir) if data_dir is not None else project_root() / "data"
    data_dir = data_dir.resolve()

    report: dict[str, Any] = {
        "data_dir": str(data_dir),
        "ok": True,
        "databases": {},
        "warnings": [],
        "errors": [],
    }

    for spec in CORE_DATABASE_SPECS:
        status = _check_database(data_dir, spec)
        report["databases"][spec.key] = status
        report["warnings"].extend(status["warnings"])
        report["errors"].extend(status["errors"])

    report["ok"] = not report["errors"]
    return report


def assert_core_databases_ready(data_dir: Path | None = None) -> None:
    report = collect_core_database_health(data_dir)
    if not report["ok"]:
        raise RuntimeError("; ".join(report["errors"]))


def _module_status(module_names: tuple[str, ...]) -> dict[str, dict[str, Any]]:
    modules: dict[str, dict[str, Any]] = {}
    for name in module_names:
        spec = importlib.util.find_spec(name)
        available = spec is not None
        version = None
        if available:
            try:
                version = importlib.metadata.version(name)
            except importlib.metadata.PackageNotFoundError:
                version = "unknown"
        modules[name] = {
            "available": available,
            "version": version,
            "origin": getattr(spec, "origin", None) if spec is not None else None,
        }
    return modules


def _load_config_paths(root: Path) -> dict[str, str]:
    config_path = root / "config.yaml"
    if not config_path.exists():
        return {}

    try:
        import yaml

        raw = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
        return {str(key): str(value) for key, value in raw.items()}
    except Exception:
        paths: dict[str, str] = {}
        for line in config_path.read_text(encoding="utf-8").splitlines():
            if ":" not in line or line.lstrip().startswith("#"):
                continue
            key, value = line.split(":", 1)
            paths[key.strip()] = value.strip().strip('"').strip("'")
        return paths


def collect_runtime_health(
    root: Path | None = None,
    *,
    strict: bool = False,
    modules: tuple[str, ...] = ("typer", "numpy"),
) -> dict[str, Any]:
    root = Path(root) if root is not None else project_root()
    root = root.resolve()

    module_report = _module_status(modules)
    missing_modules = [name for name, status in module_report.items() if not status["available"]]

    profile_report: dict[str, Any]
    profile_errors: list[str] = []
    try:
        from core.profile_sync import get_profile_stats

        profile_report = dict(get_profile_stats())
    except Exception as exc:
        profile_report = {}
        profile_errors.append(f"Profile registry error: {exc}")

    database_report = collect_core_database_health(root / "data")
    config_paths = _load_config_paths(root)

    errors: list[str] = []
    warnings: list[str] = []
    errors.extend(f"Missing Python module: {name}" for name in missing_modules)
    errors.extend(profile_errors)
    errors.extend(database_report["errors"])
    warnings.extend(database_report["warnings"])

    if strict:
        errors.extend(warnings)

    return {
        "ok": not errors,
        "project_root": str(root),
        "python": {
            "executable": sys.executable,
            "version": sys.version.split()[0],
        },
        "modules": module_report,
        "profiles": profile_report,
        "databases": database_report,
        "config_paths": config_paths,
        "warnings": warnings,
        "errors": errors,
        "strict": strict,
    }


def format_health_report(report: Mapping[str, Any]) -> str:
    lines = ["Morphic Engine Health"]
    python_info = report.get("python", {})
    lines.append(f"Python: {python_info.get('executable', '-')}")
    lines.append(f"Python-Version: {python_info.get('version', '-')}")

    lines.append("Modules:")
    for name, status in dict(report.get("modules", {})).items():
        marker = "OK" if status.get("available") else "FEHLER"
        version = status.get("version") or "-"
        lines.append(f"  [{marker}] {name} {version}")

    profiles = dict(report.get("profiles", {}))
    lines.append(f"Profiles: {profiles.get('total_profiles', 0)}")

    db_report = dict(report.get("databases", {}))
    lines.append("Databases:")
    for _key, db_status in dict(db_report.get("databases", {})).items():
        marker = "OK" if db_status.get("ok") else "FEHLER"
        file_name = db_status.get("file", "-")
        size = db_status.get("size_bytes", 0)
        table_bits = [
            f"{table}={count}"
            for table, count in dict(db_status.get("tables", {})).items()
        ]
        suffix = f" ({', '.join(table_bits)})" if table_bits else ""
        lines.append(f"  [{marker}] {file_name}: {size} bytes{suffix}")

    config_paths = dict(report.get("config_paths", {}))
    if config_paths:
        lines.append("Configured paths:")
        for key in ("archive_root", "synergy_root", "export_root", "log_dir"):
            if key in config_paths:
                lines.append(f"  {key}: {config_paths[key]}")

    warnings = list(report.get("warnings", []))
    if warnings:
        lines.append("Warnings:")
        lines.extend(f"  - {warning}" for warning in warnings)

    errors = list(report.get("errors", []))
    if errors:
        lines.append("Errors:")
        lines.extend(f"  - {error}" for error in errors)

    lines.append(f"Status: {'OK' if report.get('ok') else 'FEHLER'}")
    return "\n".join(lines)
