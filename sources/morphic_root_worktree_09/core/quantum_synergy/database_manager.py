"""
Quantum-Synergy Database Manager
Dynamisches Laden und Caching aller Items aus procedural_groups
"""

from typing import List, Dict, Optional, Tuple
import hashlib
import math
from pathlib import Path
import json

# Import Bruce Copen Rate-Berechnung
from ..subgroups.procedural_groups import (
    _GROUP_LABELS,
    _u01,
    _rate_from_freq,
    _musical_rate,
    _phi_rate,
    SCHUMANN_F0,
    PHI
)


class ItemDatabase:
    """Verwaltet alle Items für Quantum-Synergy"""
    
    def __init__(self):
        self.items: List[Dict] = []
        self.cache_file = Path(__file__).parent / "cache" / "items_cache.json"
        self.last_group_count = 0
        self._ensure_cache_dir()
    
    def _ensure_cache_dir(self):
        """Erstellt Cache-Verzeichnis"""
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
    
    def load_all_items(self, force_reload: bool = False) -> List[Dict]:
        """
        Lädt alle Items aus procedural_groups
        
        Args:
            force_reload: Erzwingt Neu-Laden (ignoriert Cache)
        
        Returns:
            Liste aller Items mit Metadaten
        """
        current_group_count = len(_GROUP_LABELS)
        
        # Prüfe ob Update nötig
        if not force_reload and current_group_count == self.last_group_count and self.items:
            print(f"✓ Item-Datenbank bereits aktuell ({len(self.items)} Items)")
            return self.items
        
        print(f"⟳ Lade Items aus {current_group_count} Gruppen...")
        
        self.items = []
        for group_name, group_data in _GROUP_LABELS.items():
            # Extrahiere Items aus Gruppe
            if isinstance(group_data, list):
                items_list = group_data
            elif isinstance(group_data, dict):
                items_list = group_data.get("items", [])
            else:
                continue
            
            # Verarbeite jedes Item
            for item in items_list:
                if isinstance(item, dict):
                    label = item.get("label", "")
                    rates = item.get("rates", [])
                elif isinstance(item, str):
                    label = item
                    rates = []
                else:
                    continue
                
                if not label:
                    continue
                
                # Berechne Rate wenn nicht vorhanden (Bruce Copen)
                if not rates:
                    rates = self._calculate_bruce_copen_rate(label)
                
                # Erstelle Item-Dict
                item_dict = {
                    'label': label,
                    'group': group_name,
                    'rates': rates,
                    'hash': self._hash_label(label),
                    'frequency': self._rate_to_frequency(rates[0] if rates else 0.0),
                }
                
                self.items.append(item_dict)
        
        self.last_group_count = current_group_count
        print(f"✓ {len(self.items)} Items geladen aus {current_group_count} Gruppen")
        
        # Cache speichern
        self._save_cache()
        
        return self.items
    
    def _calculate_bruce_copen_rate(self, label: str) -> List[float]:
        """
        Berechnet Rate nach Bruce Copen Algorithmus
        Base 10 System mit Wortenergie-Analyse
        """
        # Hash-basierte Rate (deterministisch)
        u = _u01(label)
        
        # Kombiniere verschiedene Methoden
        musical_idx = int(u * 12)  # 0-11 (Oktave)
        phi_idx = int(u * 10)      # 0-9 (Phi-Reihe)
        
        rate1 = _musical_rate(musical_idx)
        rate2 = _phi_rate(phi_idx)
        
        # Gewichtete Kombination
        final_rate = (rate1 * 0.618 + rate2 * 0.382) % 100.0
        
        return [final_rate, final_rate]  # [rate1, rate2]
    
    def _hash_label(self, label: str) -> str:
        """Erstellt Hash für Label"""
        return hashlib.md5(label.encode('utf-8')).hexdigest()[:8]
    
    def _rate_to_frequency(self, rate: float) -> float:
        """Konvertiert Rate zurück zu Frequenz"""
        # Inverse von _rate_from_freq
        return SCHUMANN_F0 * (10 ** (rate / 100.0))
    
    def get_items_by_group(self, group_name: str) -> List[Dict]:
        """Gibt alle Items einer Gruppe zurück"""
        return [item for item in self.items if item['group'] == group_name]
    
    def get_item_by_label(self, label: str) -> Optional[Dict]:
        """Findet Item nach Label"""
        for item in self.items:
            if item['label'] == label:
                return item
        return None
    
    def search_items(self, query: str, max_results: int = 50) -> List[Dict]:
        """Sucht Items nach Query"""
        query_lower = query.lower()
        results = []
        
        for item in self.items:
            if query_lower in item['label'].lower():
                results.append(item)
                if len(results) >= max_results:
                    break
        
        return results
    
    def _save_cache(self):
        """Speichert Items in Cache"""
        try:
            cache_data = {
                'group_count': self.last_group_count,
                'item_count': len(self.items),
                'items': self.items
            }
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠ Cache konnte nicht gespeichert werden: {e}")
    
    def _load_cache(self) -> bool:
        """Lädt Items aus Cache"""
        try:
            if not self.cache_file.exists():
                return False
            
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            self.last_group_count = cache_data.get('group_count', 0)
            self.items = cache_data.get('items', [])
            
            return True
        except Exception as e:
            print(f"⚠ Cache konnte nicht geladen werden: {e}")
            return False
    
    def get_statistics(self) -> Dict:
        """Gibt Statistiken zurück"""
        groups = set(item['group'] for item in self.items)
        
        return {
            'total_items': len(self.items),
            'total_groups': len(groups),
            'groups': sorted(groups),
            'avg_items_per_group': len(self.items) / len(groups) if groups else 0
        }


# Singleton-Instanz
_db_instance: Optional[ItemDatabase] = None


def get_item_database(force_reload: bool = False) -> ItemDatabase:
    """
    Gibt Singleton-Instanz der Item-Datenbank zurück
    
    Args:
        force_reload: Erzwingt Neu-Laden der Daten
    
    Returns:
        ItemDatabase-Instanz
    """
    global _db_instance
    
    if _db_instance is None:
        _db_instance = ItemDatabase()
        _db_instance.load_all_items(force_reload=force_reload)
    elif force_reload:
        _db_instance.load_all_items(force_reload=True)
    
    return _db_instance
