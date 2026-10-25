# Remedy-Gruppen Integration

## Übersicht

Dieses Dokument beschreibt, wie neue Remedy-Gruppen in das System integriert werden.

**Wichtig:** Seit der Zentralisierung müssen neue Remedy-Gruppen nur noch an **wenigen definierten Stellen** hinzugefügt werden.

---

## Checkliste für neue Remedy-Gruppen

### 1. Datenbank-Import (remedies.db)

```python
# Beispiel: Import-Script erstellen
# tools/import_neue_gruppe.py

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "remedies.db"
CATEGORY = "neue_gruppe_multiplex"

# Daten importieren mit:
# - name: Vollständiger Name
# - category: CATEGORY
# - indication: Beschreibung/Indikation
# - source: Quellenangabe
```

### 2. Gruppe in procedural_groups.py registrieren

```python
# core/subgroups/procedural_groups.py

# 1. Zu _DYNAMIC_GROUPS hinzufügen:
_DYNAMIC_GROUPS = [
    ...
    "neue_gruppe_multiplex",  # NEU
]

# 2. Zu db_category_map hinzufügen:
db_category_map = {
    ...
    "neue_gruppe_multiplex": "neue_gruppe_multiplex",  # NEU
}
```

### 3. Zentrale Registry aktualisieren (WICHTIGSTE STELLE!)

```python
# core/remedy_group_registry.py

# 1. Zu EXPLICIT_REMEDY_GROUPS hinzufügen:
EXPLICIT_REMEDY_GROUPS: Set[str] = {
    ...
    "neue_gruppe_multiplex",  # NEU
}

# 2. Zu GROUP_DISPLAY_INFO hinzufügen (für HTML-Berichte):
GROUP_DISPLAY_INFO: Dict[str, Tuple[str, str]] = {
    ...
    "neue_gruppe_multiplex": ("Anzeigename", "Beschreibung für Berichte"),
}

# 3. Optional: Token hinzufügen wenn Namenskonvention:
REMEDY_TOKENS: Tuple[str, ...] = (
    ...
    "neue_gruppe",  # Wenn zukünftige Gruppen mit "neue_gruppe_" beginnen
)
```

### 4. Optional: Profil erstellen

```python
# apps/cli/profiles/registry.py

_PROFILES_DATA: Dict[str, List[str]] = {
    ...
    "neue_gruppe_detailliert": [
        "neue_gruppe_multiplex",
        # Weitere verwandte Gruppen...
    ],
}
```

### 5. Optional: PowerShell-Auswahl hinzufügen

```powershell
# Run-MultiplexScan.ps1

$profiles = @(
    ...
    @{ Number = XX; Name = 'neue_gruppe_detailliert'; Display = 'neue_gruppe_detailliert (Beschreibung)'; }
)
```

### 6. Optional: Keywords generieren

```python
# tools/generate_neue_gruppe_keywords.py
# Ähnlich wie generate_oorep_keywords.py
```

---

## Was NICHT mehr nötig ist

Dank der zentralen Registry in `core/remedy_group_registry.py` müssen folgende Stellen **NICHT** mehr manuell angepasst werden:

- ❌ `_is_remedy_group()` in main.py
- ❌ `_is_remedy_group_name()` in main.py
- ❌ Explizite Listen in verschiedenen Funktionen

Diese Funktionen verwenden jetzt automatisch die zentrale Registry.

---

## Beispiel: OOREP-Integration

Die OOREP-Integration (2432 klassische homöopathische Einzelmittel) wurde wie folgt durchgeführt:

1. **Import-Script:** `tools/import_oorep_remedies.py`
2. **Keywords:** `tools/generate_oorep_keywords.py`
3. **procedural_groups.py:** 
   - `_DYNAMIC_GROUPS.append("oorep_homeopathy_multiplex")`
   - `db_category_map["oorep_homeopathy_multiplex"] = "oorep_homeopathy_multiplex"`
4. **remedy_group_registry.py:**
   - `EXPLICIT_REMEDY_GROUPS`: "oorep_homeopathy_multiplex"
   - `GROUP_DISPLAY_INFO`: Display-Info hinzugefügt
   - `REMEDY_TOKENS`: "oorep" hinzugefügt
5. **profiles/registry.py:** Profil "homeopathy_classical" erstellt
6. **Run-MultiplexScan.ps1:** Profil #55 hinzugefügt

---

## Verifikation

Nach der Integration testen:

```bash
# 1. Prüfe ob Gruppe geladen wird
python -c "from core.subgroups.procedural_groups import generate_candidates_for_group; items = generate_candidates_for_group('neue_gruppe_multiplex', 'test', 10); print(f'Geladen: {len(items)} Items')"

# 2. Prüfe ob als Remedy erkannt
python -c "from core.remedy_group_registry import is_remedy_group; print(is_remedy_group('neue_gruppe_multiplex'))"

# 3. Testlauf mit Profil
.\Run-MultiplexScan.ps1
# → Profil auswählen und HTML-Bericht prüfen
```

---

## Dateien-Übersicht

| Datei | Zweck |
|-------|-------|
| `core/remedy_group_registry.py` | **Zentrale Registry** - Hauptkonfiguration |
| `core/subgroups/procedural_groups.py` | Dynamische Gruppen-Registrierung |
| `apps/cli/profiles/registry.py` | Profil-Definitionen |
| `apps/cli/main.py` | CLI-Befehle (nutzt zentrale Registry) |
| `Run-MultiplexScan.ps1` | PowerShell-Auswahl |
| `data/remedies.db` | SQLite-Datenbank mit Remedy-Daten |

---

*Zuletzt aktualisiert: 29.11.2025*
