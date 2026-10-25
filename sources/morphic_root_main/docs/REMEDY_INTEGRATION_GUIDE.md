# Remedy-Integration Guide

## Übersicht

Dieses Dokument beschreibt die Architektur der Remedy-Integration in Morphic Engine V1 und wie neue Remedy-Hersteller oder -Kategorien hinzugefügt werden können.

---

## 📊 Architektur

```
┌─────────────────────────────────────────────────────────────────┐
│                         PROFILE                                  │
│  (z.B. narben_entstoerung_gewebe_remedies)                      │
│                                                                  │
│  groups = [                                                      │
│      "haut_detailliert_fein",                                   │
│      "heel_remedies_multiplex",    ← NEU                        │
│      "nutramedix_remedies_multiplex", ← NEU                     │
│      ...                                                         │
│  ]                                                               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    remedy_service.py                             │
│                                                                  │
│  find_remedies_for_group("heel_remedies_multiplex")             │
│      → category_map["heel_remedies_multiplex"]                  │
│      → "homotoxikologie_heel"                                   │
│      → SELECT FROM remedies WHERE category = ?                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      remedies.db                                 │
│                                                                  │
│  remedies: id, name, potency, category, indication              │
│  remedy_keywords: remedy_id, keyword, priority                  │
│  remedy_descriptions: remedy_id, description                    │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔧 Komponenten

### 1. `apps/cli/main.py` - `_is_remedy_group()`

**Funktion:** Erkennt, ob eine Gruppe eine Remedy-Gruppe ist (für Synergien).

**Wichtige Einträge:**
```python
explicit = {
    # Standard-Gruppen
    "homoeopathie_klassisch",
    "tcm_rezepturen",
    "spagyrik",
    # Multiplex-Container
    "energie_remedies_multiplex",
    "entgiftung_remedies_multiplex",
    # Hersteller-spezifisch (NEU)
    "heel_remedies_multiplex",
    "nutramedix_remedies_multiplex",
    "schuessler_remedies_multiplex",
    "homotoxikologie_heel",
    "phytotherapie_nutramedix",
}

tokens = (
    "homoeopathie", "spagyrik", "remedy", "remedies",
    # Hersteller-Tokens (NEU)
    "heel", "nutramedix", "homotoxikologie", "phytotherapie",
    "schuessler", "schüssler",
)
```

### 2. `services/remedy_service.py` - `find_remedies_for_group()`

**Funktion:** Findet Remedies für eine Gruppe basierend auf Keywords oder Kategorie.

**Kategorie-Mapping:**
```python
category_map = {
    # Marker-Gruppen (für dedizierte Profile)
    '__remedy_category_heel_remedies__': 'homotoxikologie_heel',
    '__remedy_category_nutramedix_remedies__': 'phytotherapie_nutramedix',
    # Multiplex-Gruppen (für Standard-Profile)
    'heel_remedies_multiplex': 'homotoxikologie_heel',
    'nutramedix_remedies_multiplex': 'phytotherapie_nutramedix',
    'schuessler_remedies_multiplex': 'Kohärente Harmonisierung mit Schüssler-Salzen',
}
```

### 3. `core/remedy_auto_matcher.py`

**Funktion:** Automatische Zuordnung von Remedy-Gruppen zu Profilen.

**Kategorien:**
```python
CATEGORY_REMEDY_MAPPING = {
    "skin": ["haut_remedies_multiplex", "heel_remedies_multiplex", ...],
    "scar": ["heel_remedies_multiplex", "nutramedix_remedies_multiplex", ...],
    ...
}

PROFILE_CATEGORY_MAPPING = {
    "narben": ["scar", "skin", "detox"],
    "haut": ["skin", "immune", "detox"],
    ...
}
```

---

## ➕ Neuen Remedy-Hersteller hinzufügen

### Schritt 1: Datenbank-Import

```python
# tools/import_new_remedies.py
from services.remedy_service import add_remedy

add_remedy(
    name="Neues Mittel XY",
    potency="D6",
    category="neuer_hersteller",  # Kategorie-Name
    indication="Indikation...",
    keywords=["keyword1", "keyword2", ...]
)
```

### Schritt 2: `remedy_service.py` erweitern

```python
category_map = {
    ...
    'neuer_hersteller_remedies_multiplex': 'neuer_hersteller',
}
```

### Schritt 3: `_is_remedy_group()` erweitern

```python
explicit = {
    ...
    "neuer_hersteller_remedies_multiplex",
    "neuer_hersteller",
}

tokens = (
    ...
    "neuer_hersteller",
)
```

### Schritt 4: Profile aktualisieren (optional)

```python
elif prof == "relevantes_profil":
    groups = [
        ...
        "neuer_hersteller_remedies_multiplex",
    ]
```

---

## 📋 Aktuelle Remedy-Kategorien

| Kategorie | DB-Kategorie | Multiplex-Gruppe | Anzahl |
|-----------|--------------|------------------|--------|
| Heel | `homotoxikologie_heel` | `heel_remedies_multiplex` | ~266 |
| Nutramedix | `phytotherapie_nutramedix` | `nutramedix_remedies_multiplex` | ~48 |
| Schüssler | `Kohärente Harmonisierung mit Schüssler-Salzen` | `schuessler_remedies_multiplex` | ~27 |
| Homöopathie | `Kohärente Harmonisierung mit Homöopathischen Mitteln` | `homoeopathie_klassisch` | ~200+ |

---

## 🔍 Debugging

### Remedies für Gruppe prüfen:
```python
from services.remedy_service import find_remedies_for_group
remedies = find_remedies_for_group("heel_remedies_multiplex", max_results=10)
print(remedies)
```

### Keywords in DB prüfen:
```sql
SELECT DISTINCT keyword FROM remedy_keywords 
WHERE keyword LIKE '%narb%';
```

### Remedies mit Keyword finden:
```sql
SELECT r.name, r.category 
FROM remedies r 
JOIN remedy_keywords k ON r.id = k.remedy_id 
WHERE k.keyword = 'narben';
```

---

## ⚠️ Wichtige Regeln

1. **Namenskonvention:** Neue Multiplex-Gruppen MÜSSEN mit `_remedies_multiplex` enden
2. **Kategorie-Konsistenz:** DB-Kategorie muss exakt mit `category_map` übereinstimmen
3. **Token-Erkennung:** Hersteller-Namen als Token in `_is_remedy_group()` hinzufügen
4. **Backup:** VOR jeder Änderung Backup erstellen!

---

*Erstellt: 2024-11-29*
*Letzte Aktualisierung: 2024-11-29*
