import importlib

import pytest


MODULE_NAME = "app.bootstrap"


def _load_module():
    return importlib.import_module(MODULE_NAME)


def test_enforce_runtime_dependencies_raises_clear_error_for_missing_packages(monkeypatch):
    bootstrap = _load_module()

    def fake_find_spec(name):
        if name in {"torch", "numpy"}:
            return None
        return object()

    monkeypatch.setattr(bootstrap.importlib.util, "find_spec", fake_find_spec)

    with pytest.raises(bootstrap.RuntimeDependencyError) as exc:
        bootstrap.enforce_runtime_dependencies(
            required_modules=["torch", "numpy", "fastapi"],
            context="Radi144 CLI",
            install_hint="python -m pip install -r requirements.txt",
        )

    message = str(exc.value)
    assert "Radi144 CLI" in message
    assert "Fehlende Python-Abhängigkeiten" in message
    assert "torch" in message
    assert "numpy" in message
    assert "fastapi" not in message
    assert "python -m pip install -r requirements.txt" in message


def test_enforce_runtime_dependencies_passes_when_all_modules_exist(monkeypatch):
    bootstrap = _load_module()

    monkeypatch.setattr(bootstrap.importlib.util, "find_spec", lambda name: object())

    bootstrap.enforce_runtime_dependencies(
        required_modules=["torch", "numpy", "fastapi"],
        context="Radi144 API",
    )
