from __future__ import annotations

import importlib.util
from dataclasses import dataclass
from typing import Iterable, Sequence


class RuntimeDependencyError(RuntimeError):
    """Fehlende Pflicht-Abhängigkeiten verhindern den Start von Radi144."""


@dataclass(frozen=True)
class DependencyProfile:
    name: str
    required_modules: tuple[str, ...]
    install_hint: str


CORE_PROFILE = DependencyProfile(
    name="Radi144 Core Engine",
    required_modules=("numpy", "torch", "psutil"),
    install_hint="python -m pip install -r requirements.txt",
)

API_PROFILE = DependencyProfile(
    name="Radi144 API",
    required_modules=("fastapi", "uvicorn", "numpy", "torch", "pydantic", "psutil", "websockets"),
    install_hint="python -m pip install -r requirements.txt",
)

CLI_PROFILE = DependencyProfile(
    name="Radi144 CLI",
    required_modules=("numpy", "torch", "reportlab", "openpyxl", "psutil"),
    install_hint="python -m pip install -r requirements.txt",
)


def _missing_modules(required_modules: Iterable[str]) -> list[str]:
    missing: list[str] = []
    for module_name in required_modules:
        if importlib.util.find_spec(module_name) is None:
            missing.append(module_name)
    return missing


def _build_error_message(*, context: str, missing: Sequence[str], install_hint: str | None) -> str:
    lines = [
        f"{context}: Fehlende Python-Abhängigkeiten erkannt.",
        "Radi144 ist im Option-A-Modus konfiguriert und startet nur mit vollständig installiertem Runtime-Stack.",
        "",
        "Fehlend:",
    ]
    lines.extend(f"- {name}" for name in missing)
    if install_hint:
        lines.extend([
            "",
            f"Installation: {install_hint}",
        ])
    return "\n".join(lines)


def enforce_runtime_dependencies(
    required_modules: Iterable[str],
    *,
    context: str,
    install_hint: str | None = None,
) -> None:
    missing = _missing_modules(required_modules)
    if missing:
        raise RuntimeDependencyError(
            _build_error_message(context=context, missing=missing, install_hint=install_hint)
        )


def enforce_profile(profile: DependencyProfile) -> None:
    enforce_runtime_dependencies(
        required_modules=profile.required_modules,
        context=profile.name,
        install_hint=profile.install_hint,
    )
