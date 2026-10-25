#!/usr/bin/env python3
"""
Gruppen- und Multiplex-Verwaltung für Morphic Engine V1.
Ermöglicht das Erstellen, Bearbeiten und Verwalten von Gruppen und Multiplexen.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set
from datetime import datetime

# Pfad zum Hauptverzeichnis hinzufügen
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from core.subgroups.procedural_groups import list_groups, _GROUP_LABELS, _DYNAMIC_GROUPS
    GROUPS_AVAILABLE = True
except ImportError:
    GROUPS_AVAILABLE = False
    def list_groups():
        return []

class GroupManager:
    """Verwaltet Gruppen und Multiplexe für das Morphic Engine System."""
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or Path(__file__).parent.parent / "config" / "groups_config.json"
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self.config = self._load_config()
    
    def _load_config(self) -> Dict:
        """Lädt die Gruppen-Konfiguration."""
        if self.config_path.exists():
            try:
                return json.loads(self.config_path.read_text(encoding='utf-8'))
            except Exception as e:
                print(f"Fehler beim Laden der Konfiguration: {e}")
        
        # Standard-Konfiguration
        return {
            "custom_groups": {},
            "custom_multiplexes": {},
            "group_descriptions": {},
            "last_modified": datetime.now().isoformat(),
            "version": "1.0"
        }
    
    def _save_config(self):
        """Speichert die Gruppen-Konfiguration."""
        self.config["last_modified"] = datetime.now().isoformat()
        try:
            self.config_path.write_text(json.dumps(self.config, indent=2, ensure_ascii=False), encoding='utf-8')
            print(f"Konfiguration gespeichert: {self.config_path}")
        except Exception as e:
            print(f"Fehler beim Speichern: {e}")
    
    def list_available_groups(self) -> List[str]:
        """Listet alle verfügbaren Gruppen auf."""
        if GROUPS_AVAILABLE:
            return list_groups()
        return []
    
    def list_custom_groups(self) -> List[str]:
        """Listet alle benutzerdefinierten Gruppen auf."""
        return list(self.config.get("custom_groups", {}).keys())
    
    def list_custom_multiplexes(self) -> List[str]:
        """Listet alle benutzerdefinierten Multiplexe auf."""
        return list(self.config.get("custom_multiplexes", {}).keys())
    
    def create_custom_group(self, name: str, labels: List[str], description: str = "") -> bool:
        """
        Erstellt eine neue benutzerdefinierte Gruppe.
        
        Args:
            name: Name der Gruppe
            labels: Liste der Labels in der Gruppe
            description: Beschreibung der Gruppe
            
        Returns:
            True wenn erfolgreich erstellt
        """
        if not name or not labels:
            print("Name und Labels sind erforderlich!")
            return False
        
        if name in self.list_available_groups():
            print(f"Gruppe '{name}' existiert bereits als System-Gruppe!")
            return False
        
        self.config["custom_groups"][name] = {
            "labels": labels,
            "description": description,
            "created": datetime.now().isoformat(),
            "type": "custom"
        }
        
        if description:
            self.config["group_descriptions"][name] = description
        
        self._save_config()
        print(f"Benutzerdefinierte Gruppe '{name}' erstellt mit {len(labels)} Labels.")
        return True
    
    def create_custom_multiplex(self, name: str, groups: List[str], description: str = "", 
                              k_total: int = 512, focus_areas: List[str] = None) -> bool:
        """
        Erstellt einen neuen benutzerdefinierten Multiplex.
        
        Args:
            name: Name des Multiplex
            groups: Liste der Gruppen im Multiplex
            description: Beschreibung des Multiplex
            k_total: Anzahl Kandidaten
            focus_areas: Fokus-Bereiche
            
        Returns:
            True wenn erfolgreich erstellt
        """
        if not name or not groups:
            print("Name und Gruppen sind erforderlich!")
            return False
        
        # Prüfe ob alle Gruppen existieren
        available_groups = self.list_available_groups() + self.list_custom_groups()
        missing_groups = [g for g in groups if g not in available_groups]
        if missing_groups:
            print(f"Unbekannte Gruppen: {missing_groups}")
            return False
        
        self.config["custom_multiplexes"][name] = {
            "groups": groups,
            "description": description,
            "k_total": k_total,
            "focus_areas": focus_areas or [],
            "created": datetime.now().isoformat(),
            "type": "custom"
        }
        
        self._save_config()
        print(f"Benutzerdefinierter Multiplex '{name}' erstellt mit {len(groups)} Gruppen.")
        return True
    
    def get_group_info(self, name: str) -> Optional[Dict]:
        """Gibt Informationen über eine Gruppe zurück."""
        # System-Gruppen
        if GROUPS_AVAILABLE and name in _GROUP_LABELS:
            return {
                "name": name,
                "type": "system",
                "labels": _GROUP_LABELS[name],
                "count": len(_GROUP_LABELS[name]),
                "description": self.config.get("group_descriptions", {}).get(name, "")
            }
        
        # Dynamische Gruppen
        if GROUPS_AVAILABLE and name in _DYNAMIC_GROUPS:
            return {
                "name": name,
                "type": "dynamic",
                "labels": [],
                "count": "dynamisch",
                "description": self.config.get("group_descriptions", {}).get(name, "")
            }
        
        # Benutzerdefinierte Gruppen
        custom_groups = self.config.get("custom_groups", {})
        if name in custom_groups:
            group_data = custom_groups[name]
            return {
                "name": name,
                "type": "custom",
                "labels": group_data.get("labels", []),
                "count": len(group_data.get("labels", [])),
                "description": group_data.get("description", ""),
                "created": group_data.get("created", "")
            }
        
        return None
    
    def get_multiplex_info(self, name: str) -> Optional[Dict]:
        """Gibt Informationen über einen Multiplex zurück."""
        custom_multiplexes = self.config.get("custom_multiplexes", {})
        if name in custom_multiplexes:
            multiplex_data = custom_multiplexes[name]
            return {
                "name": name,
                "type": "custom",
                "groups": multiplex_data.get("groups", []),
                "group_count": len(multiplex_data.get("groups", [])),
                "description": multiplex_data.get("description", ""),
                "k_total": multiplex_data.get("k_total", 512),
                "focus_areas": multiplex_data.get("focus_areas", []),
                "created": multiplex_data.get("created", "")
            }
        return None
    
    def delete_custom_group(self, name: str) -> bool:
        """Löscht eine benutzerdefinierte Gruppe."""
        custom_groups = self.config.get("custom_groups", {})
        if name not in custom_groups:
            print(f"Benutzerdefinierte Gruppe '{name}' nicht gefunden!")
            return False
        
        del custom_groups[name]
        if name in self.config.get("group_descriptions", {}):
            del self.config["group_descriptions"][name]
        
        self._save_config()
        print(f"Benutzerdefinierte Gruppe '{name}' gelöscht.")
        return True
    
    def delete_custom_multiplex(self, name: str) -> bool:
        """Löscht einen benutzerdefinierten Multiplex."""
        custom_multiplexes = self.config.get("custom_multiplexes", {})
        if name not in custom_multiplexes:
            print(f"Benutzerdefinierter Multiplex '{name}' nicht gefunden!")
            return False
        
        del custom_multiplexes[name]
        self._save_config()
        print(f"Benutzerdefinierter Multiplex '{name}' gelöscht.")
        return True
    
    def export_config(self, export_path: Path) -> bool:
        """Exportiert die Konfiguration in eine Datei."""
        try:
            export_path.write_text(json.dumps(self.config, indent=2, ensure_ascii=False), encoding='utf-8')
            print(f"Konfiguration exportiert nach: {export_path}")
            return True
        except Exception as e:
            print(f"Export fehlgeschlagen: {e}")
            return False
    
    def import_config(self, import_path: Path, merge: bool = True) -> bool:
        """Importiert eine Konfiguration aus einer Datei."""
        if not import_path.exists():
            print(f"Import-Datei nicht gefunden: {import_path}")
            return False
        
        try:
            imported_config = json.loads(import_path.read_text(encoding='utf-8'))
            
            if merge:
                # Merge mit bestehender Konfiguration
                self.config["custom_groups"].update(imported_config.get("custom_groups", {}))
                self.config["custom_multiplexes"].update(imported_config.get("custom_multiplexes", {}))
                self.config["group_descriptions"].update(imported_config.get("group_descriptions", {}))
            else:
                # Komplette Ersetzung
                self.config = imported_config
            
            self._save_config()
            print(f"Konfiguration importiert von: {import_path}")
            return True
        except Exception as e:
            print(f"Import fehlgeschlagen: {e}")
            return False
    
    def print_summary(self):
        """Gibt eine Zusammenfassung aller Gruppen und Multiplexe aus."""
        print("=== GRUPPEN- UND MULTIPLEX-VERWALTUNG ===")
        print(f"Konfigurationsdatei: {self.config_path}")
        print(f"Letzte Änderung: {self.config.get('last_modified', 'unbekannt')}")
        print()
        
        # System-Gruppen
        system_groups = self.list_available_groups()
        print(f"System-Gruppen: {len(system_groups)}")
        for group in sorted(system_groups)[:10]:  # Erste 10 anzeigen
            info = self.get_group_info(group)
            if info:
                count = info.get("count", "?")
                print(f"  - {group}: {count} Labels ({info.get('type', 'unknown')})")
        if len(system_groups) > 10:
            print(f"  ... und {len(system_groups) - 10} weitere")
        print()
        
        # Benutzerdefinierte Gruppen
        custom_groups = self.list_custom_groups()
        print(f"Benutzerdefinierte Gruppen: {len(custom_groups)}")
        for group in custom_groups:
            info = self.get_group_info(group)
            if info:
                print(f"  - {group}: {info.get('count', '?')} Labels - {info.get('description', 'Keine Beschreibung')}")
        print()
        
        # Benutzerdefinierte Multiplexe
        custom_multiplexes = self.list_custom_multiplexes()
        print(f"Benutzerdefinierte Multiplexe: {len(custom_multiplexes)}")
        for multiplex in custom_multiplexes:
            info = self.get_multiplex_info(multiplex)
            if info:
                print(f"  - {multiplex}: {info.get('group_count', '?')} Gruppen - {info.get('description', 'Keine Beschreibung')}")

def main():
    """Hauptfunktion für die Kommandozeilen-Verwaltung."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Gruppen- und Multiplex-Verwaltung")
    parser.add_argument("action", choices=["list", "info", "create-group", "create-multiplex", "delete", "export", "import", "summary"])
    parser.add_argument("--name", help="Name der Gruppe/des Multiplex")
    parser.add_argument("--labels", nargs="+", help="Labels für neue Gruppe")
    parser.add_argument("--groups", nargs="+", help="Gruppen für neuen Multiplex")
    parser.add_argument("--description", help="Beschreibung")
    parser.add_argument("--file", help="Datei für Export/Import")
    parser.add_argument("--k-total", type=int, default=512, help="Anzahl Kandidaten für Multiplex")
    
    args = parser.parse_args()
    
    manager = GroupManager()
    
    if args.action == "summary":
        manager.print_summary()
    
    elif args.action == "list":
        print("System-Gruppen:")
        for group in sorted(manager.list_available_groups()):
            print(f"  - {group}")
        print("\nBenutzerdefinierte Gruppen:")
        for group in manager.list_custom_groups():
            print(f"  - {group}")
        print("\nBenutzerdefinierte Multiplexe:")
        for multiplex in manager.list_custom_multiplexes():
            print(f"  - {multiplex}")
    
    elif args.action == "info":
        if not args.name:
            print("--name ist erforderlich für info")
            return
        
        # Versuche Gruppe
        info = manager.get_group_info(args.name)
        if info:
            print(f"Gruppe: {info['name']}")
            print(f"Typ: {info['type']}")
            print(f"Anzahl Labels: {info['count']}")
            print(f"Beschreibung: {info.get('description', 'Keine')}")
            if info.get('labels'):
                print(f"Labels: {', '.join(info['labels'][:10])}")
                if len(info['labels']) > 10:
                    print(f"... und {len(info['labels']) - 10} weitere")
            return
        
        # Versuche Multiplex
        info = manager.get_multiplex_info(args.name)
        if info:
            print(f"Multiplex: {info['name']}")
            print(f"Typ: {info['type']}")
            print(f"Anzahl Gruppen: {info['group_count']}")
            print(f"K-Total: {info['k_total']}")
            print(f"Beschreibung: {info.get('description', 'Keine')}")
            print(f"Gruppen: {', '.join(info['groups'])}")
            if info.get('focus_areas'):
                print(f"Fokus-Bereiche: {', '.join(info['focus_areas'])}")
            return
        
        print(f"'{args.name}' nicht gefunden!")
    
    elif args.action == "create-group":
        if not args.name or not args.labels:
            print("--name und --labels sind erforderlich")
            return
        manager.create_custom_group(args.name, args.labels, args.description or "")
    
    elif args.action == "create-multiplex":
        if not args.name or not args.groups:
            print("--name und --groups sind erforderlich")
            return
        manager.create_custom_multiplex(args.name, args.groups, args.description or "", args.k_total)
    
    elif args.action == "delete":
        if not args.name:
            print("--name ist erforderlich")
            return
        if not manager.delete_custom_group(args.name):
            manager.delete_custom_multiplex(args.name)
    
    elif args.action == "export":
        if not args.file:
            print("--file ist erforderlich")
            return
        manager.export_config(Path(args.file))
    
    elif args.action == "import":
        if not args.file:
            print("--file ist erforderlich")
            return
        manager.import_config(Path(args.file))

if __name__ == "__main__":
    main()
