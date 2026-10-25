import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

try:
    from core.subgroups.procedural_groups import _DYNAMIC_GROUPS, _GROUP_LABELS, list_groups

    GROUPS_AVAILABLE = True
except ImportError:
    GROUPS_AVAILABLE = False
    _DYNAMIC_GROUPS = {}
    _GROUP_LABELS = {}

    def list_groups() -> List[str]:
        return []


class GroupManager:
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or Path("config") / "groups_config.json"
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self.config = self._load_config()

    def _load_config(self) -> Dict:
        if self.config_path.exists():
            try:
                return json.loads(self.config_path.read_text(encoding="utf-8"))
            except Exception:
                pass
        return {
            "custom_groups": {},
            "custom_multiplexes": {},
            "group_descriptions": {},
            "last_modified": datetime.now().isoformat(),
            "version": "1.0",
        }

    def _save_config(self) -> None:
        self.config["last_modified"] = datetime.now().isoformat()
        self.config_path.write_text(
            json.dumps(self.config, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def list_available_groups(self) -> List[str]:
        return list_groups() if GROUPS_AVAILABLE else []

    def list_custom_groups(self) -> List[str]:
        return list(self.config.get("custom_groups", {}).keys())

    def list_custom_multiplexes(self) -> List[str]:
        return list(self.config.get("custom_multiplexes", {}).keys())

    def create_custom_group(self, name: str, labels: List[str], description: str = "") -> bool:
        if not name or not labels:
            return False
        if name in self.list_available_groups():
            return False

        self.config.setdefault("custom_groups", {})[name] = {
            "labels": labels,
            "description": description,
            "created": datetime.now().isoformat(),
            "type": "custom",
        }
        if description:
            self.config.setdefault("group_descriptions", {})[name] = description
        self._save_config()
        return True

    def create_custom_multiplex(
        self,
        name: str,
        groups: List[str],
        description: str = "",
        k_total: int = 512,
        focus_areas: Optional[List[str]] = None,
    ) -> bool:
        if not name or not groups:
            return False
        available_groups = self.list_available_groups() + self.list_custom_groups()
        if [group for group in groups if group not in available_groups]:
            return False

        self.config.setdefault("custom_multiplexes", {})[name] = {
            "groups": groups,
            "description": description,
            "k_total": k_total,
            "focus_areas": focus_areas or [],
            "created": datetime.now().isoformat(),
            "type": "custom",
        }
        self._save_config()
        return True

    def get_group_info(self, name: str) -> Optional[Dict]:
        if GROUPS_AVAILABLE and name in _GROUP_LABELS:
            labels = _GROUP_LABELS[name]
            return {
                "name": name,
                "type": "system",
                "labels": labels,
                "count": len(labels),
                "description": self.config.get("group_descriptions", {}).get(name, ""),
            }
        if GROUPS_AVAILABLE and name in _DYNAMIC_GROUPS:
            return {
                "name": name,
                "type": "dynamic",
                "labels": [],
                "count": "dynamisch",
                "description": self.config.get("group_descriptions", {}).get(name, ""),
            }
        group = self.config.get("custom_groups", {}).get(name)
        if group:
            labels = group.get("labels", [])
            return {
                "name": name,
                "type": "custom",
                "labels": labels,
                "count": len(labels),
                "description": group.get("description", ""),
                "created": group.get("created", ""),
            }
        return None

    def get_multiplex_info(self, name: str) -> Optional[Dict]:
        multiplex = self.config.get("custom_multiplexes", {}).get(name)
        if not multiplex:
            return None
        groups = multiplex.get("groups", [])
        return {
            "name": name,
            "type": "custom",
            "groups": groups,
            "group_count": len(groups),
            "description": multiplex.get("description", ""),
            "k_total": multiplex.get("k_total", 512),
            "focus_areas": multiplex.get("focus_areas", []),
            "created": multiplex.get("created", ""),
        }

    def delete_custom_group(self, name: str) -> bool:
        custom_groups = self.config.get("custom_groups", {})
        if name not in custom_groups:
            return False
        del custom_groups[name]
        self.config.get("group_descriptions", {}).pop(name, None)
        self._save_config()
        return True

    def delete_custom_multiplex(self, name: str) -> bool:
        custom_multiplexes = self.config.get("custom_multiplexes", {})
        if name not in custom_multiplexes:
            return False
        del custom_multiplexes[name]
        self._save_config()
        return True

    def export_config(self, export_path: Path) -> bool:
        export_path.write_text(
            json.dumps(self.config, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        return True

    def import_config(self, import_path: Path, merge: bool = True) -> bool:
        if not import_path.exists():
            return False
        imported_config = json.loads(import_path.read_text(encoding="utf-8"))
        if merge:
            self.config.setdefault("custom_groups", {}).update(imported_config.get("custom_groups", {}))
            self.config.setdefault("custom_multiplexes", {}).update(
                imported_config.get("custom_multiplexes", {})
            )
            self.config.setdefault("group_descriptions", {}).update(
                imported_config.get("group_descriptions", {})
            )
        else:
            self.config = imported_config
        self._save_config()
        return True

    def print_summary(self) -> None:
        print("=== GRUPPEN- UND MULTIPLEX-VERWALTUNG ===")
        print(f"Konfigurationsdatei: {self.config_path}")
        print(f"System-Gruppen: {len(self.list_available_groups())}")
        print(f"Benutzerdefinierte Gruppen: {len(self.list_custom_groups())}")
        print(f"Benutzerdefinierte Multiplexe: {len(self.list_custom_multiplexes())}")
