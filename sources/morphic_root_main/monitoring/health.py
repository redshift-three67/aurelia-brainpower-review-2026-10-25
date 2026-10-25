import sys
from pathlib import Path
import yaml

def _load_config() -> dict:
    """Liest die zentrale config.yaml im Projekt‑Root.
    Erwartet Schlüssel: archive_root, synergy_root, export_root, log_dir.
    """
    # The config.yaml resides in Morphic_Engine_V1, which is one level up from this file.
    config_path = Path(__file__).resolve().parents[1] / "config.yaml"
    if not config_path.is_file():
        sys.stderr.write(f"⚠ Config‑Datei nicht gefunden: {config_path}\n")
        raise SystemExit(1)
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}

def check_paths() -> None:
    """Prüft, ob alle in der config.yaml definierten Verzeichnisse existieren.
    Bei Fehlenden Verzeichnissen wird ein klarer Fehler ausgegeben und das Programm beendet.
    """
    cfg = _load_config()
    required_keys = ["archive_root", "synergy_root", "export_root", "log_dir"]
    missing = []
    for key in required_keys:
        path_str = cfg.get(key, "")
        if not path_str:
            missing.append(f"{key}=<nicht definiert>")
            continue
        p = Path(path_str)
        if not p.is_dir():
            missing.append(str(p))
    if missing:
        sys.stderr.write("⚠ Fehlende erforderliche Verzeichnisse: " + ", ".join(missing) + "\n")
        raise SystemExit(1)
    # optional: ensure log_dir exists (wird vom Logger erstellt, aber hier sicherheitshalber)
    log_dir = Path(cfg.get("log_dir", "logs"))
    log_dir.mkdir(parents=True, exist_ok=True)
