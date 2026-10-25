#!/usr/bin/env python3
"""
Batch-Beschreibungsgenerator für Morphic Engine
Verwendet Ollama (llama3.2:3b) für AI-generierte Beschreibungen
Speichert in SQLite-Datenbank
"""

import json
import time
import sys
from pathlib import Path
from typing import List, Dict, Optional

# Füge Parent-Verzeichnis zum Path hinzu
sys.path.insert(0, str(Path(__file__).parent.parent))

import requests
from services.description_service import (
    init_database,
    save_descriptions_batch,
    get_items_without_description,
    register_items,
    get_sync_status,
    get_group_stats,
    update_sync_timestamp,
    get_db_path,
)

# Konfiguration
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.2:3b"
DESCRIPTIONS_DIR = Path(__file__).parent.parent / "data" / "descriptions"


def generate_description(item_label: str, context: str = "Bioresonanz") -> Optional[str]:
    """
    Generiert eine Beschreibung für ein Item mit Ollama.
    
    Args:
        item_label: Name des Items (z.B. "Oscillococcinum C200")
        context: Kontext für die Beschreibung
    
    Returns:
        Generierte Beschreibung oder None bei Fehler
    """
    prompt = f"""Formuliere eine sehr kurze, neutrale Beschreibung (1-2 Sätze) für "{item_label}" im Kontext von {context}, Radionik und energetischer Betrachtung.

Beschreibe nur, welche energetischen, emotionalen oder symbolischen Aspekte typischerweise mit diesem Eintrag in Verbindung gebracht werden.

Mache KEINE medizinischen Aussagen, KEINE Heilversprechen und KEINE Therapie- oder Wirksamkeitsaussagen. Vermeide Wörter wie heilen, Heilung, Behandlung, Therapie, Medikament, Arznei, wirksam, lindern, vorbeugen und stelle keine Diagnosen.

Formuliere mit Wendungen wie „kann als energetische Unterstützung bei ... gesehen werden“ oder „wird im Rahmen der Bioresonanz als Hinweis auf ... interpretiert“.

Antworte nur mit der Beschreibung, ohne Einleitung und ohne Aufzählungszeichen."""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 150,
                }
            },
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get("response", "").strip()
        else:
            print(f"  ❌ Ollama Error: {response.status_code}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("  ❌ Ollama nicht erreichbar. Bitte starten mit: ollama serve")
        return None
    except Exception as e:
        print(f"  ❌ Fehler: {e}")
        return None


def batch_generate(
    items: List[str],
    group_name: str,
    context: str = "Bioresonanz",
    delay_seconds: float = 0.5
) -> Dict[str, str]:
    """
    Generiert Beschreibungen für eine Liste von Items.
    
    Args:
        items: Liste der Item-Labels
        group_name: Name der Gruppe (für Dateiname)
        context: Kontext für Beschreibungen
        delay_seconds: Pause zwischen Anfragen
    
    Returns:
        Dictionary mit Item -> Beschreibung
    """
    descriptions = {}
    total = len(items)
    
    print(f"\n{'='*60}")
    print(f"Batch-Beschreibungen: {group_name}")
    print(f"{'='*60}")
    print(f"Items: {total}")
    print(f"Modell: {MODEL}")
    print(f"{'='*60}\n")
    
    for i, item in enumerate(items, 1):
        print(f"[{i}/{total}] {item[:50]}...")
        
        desc = generate_description(item, context)
        if desc:
            descriptions[item] = desc
            print(f"  ✅ {desc[:60]}...")
        else:
            print(f"  ⚠️ Keine Beschreibung generiert")
        
        if i < total:
            time.sleep(delay_seconds)
    
    # In SQLite-DB speichern
    if descriptions:
        saved = save_descriptions_batch(descriptions, group_name=group_name, model_used=MODEL)
        update_sync_timestamp()
    else:
        saved = 0
    
    # Zusätzlich als JSON-Backup
    DESCRIPTIONS_DIR.mkdir(parents=True, exist_ok=True)
    output_file = DESCRIPTIONS_DIR / f"{group_name}_descriptions.json"
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(descriptions, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*60}")
    print(f"✅ {len(descriptions)}/{total} Beschreibungen generiert")
    print(f"💾 SQLite-DB: {get_db_path()}")
    print(f"📁 JSON-Backup: {output_file}")
    print(f"{'='*60}\n")
    
    return descriptions


def test_connection() -> bool:
    """Testet die Verbindung zu Ollama."""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            model_names = [m.get("name", "") for m in models]
            if any(MODEL in name for name in model_names):
                print(f"✅ Ollama verbunden, {MODEL} verfügbar")
                return True
            else:
                print(f"⚠️ Ollama verbunden, aber {MODEL} nicht gefunden")
                print(f"   Verfügbar: {', '.join(model_names)}")
                return False
        return False
    except:
        print("❌ Ollama nicht erreichbar")
        return False


def run_test():
    """Führt einen Test mit 5 Beispiel-Items durch."""
    test_items = [
        "Oscillococcinum C200",
        "Arnica montana D12",
        "Vitamin D3",
        "Borreliose",
        "Herzchakra"
    ]
    
    print("\n" + "="*60)
    print("TEST-MODUS: 5 Beispiel-Items")
    print("="*60)
    
    if not test_connection():
        return None
    
    return batch_generate(test_items, "test", context="Bioresonanz/Naturheilkunde")


def scan_all_groups() -> Dict[str, List[str]]:
    """
    Scannt alle verfügbaren Gruppen und deren Items.
    
    Returns:
        Dictionary {group_name: [item_labels]}
    """
    from core.subgroups.procedural_groups import generate_candidates_for_group, list_groups
    
    groups = {}
    available = list_groups()
    
    print(f"\n📊 Scanne {len(available)} Gruppen...")
    
    for group_name in available:
        try:
            items = generate_candidates_for_group(group_name, "scan_seed", k=100)
            if items:
                labels = [it.get("label", "") for it in items if it.get("label")]
                if labels:
                    groups[group_name] = labels
        except Exception:
            pass
    
    return groups


def sync_groups_to_db():
    """
    Synchronisiert alle Gruppen zur DB (registriert Items ohne Beschreibung).
    """
    init_database()
    groups = scan_all_groups()
    
    total_items = 0
    new_items = 0
    
    for group_name, labels in groups.items():
        count = register_items(labels, group_name)
        total_items += len(labels)
        new_items += count
    
    update_sync_timestamp()
    
    print(f"\n{'='*60}")
    print(f"✅ Sync abgeschlossen")
    print(f"   Gruppen: {len(groups)}")
    print(f"   Items gesamt: {total_items}")
    print(f"   Neue Items: {new_items}")
    print(f"{'='*60}\n")
    
    return groups


def show_status():
    """Zeigt den aktuellen Status der Beschreibungs-DB."""
    init_database()
    status = get_sync_status()
    
    print(f"\n{'='*60}")
    print(f"BESCHREIBUNGS-DATENBANK STATUS")
    print(f"{'='*60}")
    print(f"📁 Datenbank: {get_db_path()}")
    print(f"")
    print(f"📊 Statistik:")
    print(f"   Items gesamt:      {status['items_total']:,}")
    print(f"   Mit Beschreibung:  {status['items_with_desc']:,}")
    print(f"   Ohne Beschreibung: {status['items_missing_desc']:,}")
    print(f"   Abdeckung:         {status['coverage_percent']:.1f}%")
    print(f"   Gruppen:           {status['groups_total']}")
    print(f"   Letzter Sync:      {status['last_sync'] or 'Nie'}")
    print(f"{'='*60}\n")
    
    # Gruppen-Details
    group_stats = get_group_stats()
    if group_stats:
        print(f"Gruppen ohne vollständige Beschreibungen:")
        for gs in group_stats[:15]:
            if gs["missing"] > 0:
                print(f"   {gs['group'][:40]}: {gs['with_desc']}/{gs['total']} ({gs['coverage']:.0f}%)")
        if len(group_stats) > 15:
            print(f"   ... und {len(group_stats) - 15} weitere Gruppen")


def generate_for_group(group_name: str, limit: int = 0):
    """
    Generiert Beschreibungen für eine bestimmte Gruppe.
    
    Args:
        group_name: Name der Gruppe
        limit: Max. Anzahl Items (0 = alle)
    """
    from core.subgroups.procedural_groups import generate_candidates_for_group
    
    if not test_connection():
        return
    
    items = generate_candidates_for_group(group_name, "desc_seed", k=limit if limit > 0 else 200)
    if not items:
        print(f"❌ Keine Items für Gruppe '{group_name}' gefunden")
        return
    
    labels = [it.get("label", "") for it in items if it.get("label")]
    
    # Registriere Items zuerst
    register_items(labels, group_name)
    
    # Finde Items ohne Beschreibung
    missing = get_items_without_description(group_name)
    
    if not missing:
        print(f"✅ Alle Items in '{group_name}' haben bereits Beschreibungen")
        return
    
    print(f"📝 {len(missing)} Items ohne Beschreibung in '{group_name}'")
    
    if limit > 0:
        missing = missing[:limit]
    
    batch_generate(missing, group_name, context="Bioresonanz/Naturheilkunde")


def list_categories() -> Dict[str, List[str]]:
    """
    Gruppiert alle Gruppen nach Kategorie (Präfix).
    
    Returns:
        Dictionary {kategorie: [gruppen_namen]}
    """
    from core.subgroups.procedural_groups import list_groups
    
    categories = {}
    
    for group in list_groups():
        # Extrahiere Kategorie aus Gruppenname
        parts = group.split("_")
        if len(parts) >= 1:
            # Bestimme Kategorie
            if group.startswith("bat_"):
                cat = "bat_akut"
            elif group.startswith("bakterien"):
                cat = "bakterien"
            elif group.startswith("viren"):
                cat = "viren"
            elif group.startswith("pilze"):
                cat = "pilze"
            elif group.startswith("parasiten"):
                cat = "parasiten"
            elif group.startswith("homoeopathie"):
                cat = "homoeopathie"
            elif group.startswith("spagyrik"):
                cat = "spagyrik"
            elif group.startswith("bachblueten"):
                cat = "bachblueten"
            elif group.startswith("organe"):
                cat = "organe"
            elif group.startswith("chakra"):
                cat = "chakra"
            elif group.startswith("meridian"):
                cat = "meridiane"
            elif group.startswith("wirbel"):
                cat = "wirbelsaeule"
            elif group.startswith("schmerz"):
                cat = "schmerz"
            elif group.startswith("orthomolekular") or group.startswith("vitamin") or group.startswith("mineral"):
                cat = "orthomolekular"
            else:
                cat = "sonstige"
            
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(group)
    
    return categories


def show_categories():
    """Zeigt alle Kategorien und deren Gruppenanzahl."""
    categories = list_categories()
    
    print(f"\n{'='*60}")
    print(f"VERFÜGBARE KATEGORIEN")
    print(f"{'='*60}")
    
    total_groups = 0
    for cat, groups in sorted(categories.items()):
        print(f"  {cat}: {len(groups)} Gruppen")
        total_groups += len(groups)
    
    print(f"{'='*60}")
    print(f"  GESAMT: {total_groups} Gruppen")
    print(f"{'='*60}\n")


def generate_for_category(category: str):
    """
    Generiert Beschreibungen für alle Gruppen einer Kategorie.
    
    Args:
        category: Name der Kategorie (z.B. "bat_akut", "bakterien")
    """
    from core.subgroups.procedural_groups import generate_candidates_for_group
    
    categories = list_categories()
    
    if category not in categories:
        print(f"❌ Kategorie '{category}' nicht gefunden")
        print(f"   Verfügbar: {', '.join(sorted(categories.keys()))}")
        return
    
    if not test_connection():
        return
    
    groups = categories[category]
    print(f"\n{'='*60}")
    print(f"KATEGORIE: {category.upper()}")
    print(f"Gruppen: {len(groups)}")
    print(f"{'='*60}\n")
    
    total_generated = 0
    
    for gi, group_name in enumerate(groups, 1):
        print(f"\n[{gi}/{len(groups)}] Gruppe: {group_name}")
        print("-" * 40)
        
        try:
            items = generate_candidates_for_group(group_name, "desc_seed", k=200)
            if not items:
                print(f"  ⚠️ Keine Items")
                continue
            
            labels = [it.get("label", "") for it in items if it.get("label")]
            
            # Registriere Items
            register_items(labels, group_name)
            
            # Finde Items ohne Beschreibung
            missing = get_items_without_description(group_name)
            
            if not missing:
                print(f"  ✅ Alle {len(labels)} Items haben bereits Beschreibungen")
                continue
            
            print(f"  📝 {len(missing)} von {len(labels)} Items ohne Beschreibung")
            
            # Generiere Beschreibungen
            descriptions = {}
            for i, item in enumerate(missing, 1):
                print(f"    [{i}/{len(missing)}] {item[:40]}...", end=" ")
                desc = generate_description(item, "Bioresonanz/Naturheilkunde")
                if desc:
                    descriptions[item] = desc
                    print(f"✅")
                else:
                    print(f"⚠️")
                time.sleep(0.3)  # Kurze Pause
            
            # Speichern
            if descriptions:
                save_descriptions_batch(descriptions, group_name=group_name, model_used=MODEL)
                total_generated += len(descriptions)
                print(f"  💾 {len(descriptions)} Beschreibungen gespeichert")
        
        except Exception as e:
            print(f"  ❌ Fehler: {e}")
    
    update_sync_timestamp()
    
    print(f"\n{'='*60}")
    print(f"✅ KATEGORIE '{category}' ABGESCHLOSSEN")
    print(f"   Generierte Beschreibungen: {total_generated}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Verwendung:")
        print("  python batch_descriptions.py --test         # Test mit 5 Items")
        print("  python batch_descriptions.py --status       # Zeigt DB-Status")
        print("  python batch_descriptions.py --sync         # Synchronisiert alle Gruppen")
        print("  python batch_descriptions.py --categories   # Zeigt alle Kategorien")
        print("  python batch_descriptions.py --category NAME  # Generiert für Kategorie")
        print("  python batch_descriptions.py --group NAME   # Generiert für eine Gruppe")
        print("")
        print("Kategorien: bat_akut, bakterien, viren, pilze, parasiten,")
        print("            homoeopathie, spagyrik, bachblueten, organe,")
        print("            chakra, meridiane, wirbelsaeule, schmerz, orthomolekular")
        sys.exit(0)
    
    cmd = sys.argv[1]
    
    if cmd == "--test":
        run_test()
    elif cmd == "--status":
        show_status()
    elif cmd == "--sync":
        sync_groups_to_db()
    elif cmd == "--categories":
        show_categories()
    elif cmd == "--category" and len(sys.argv) >= 3:
        category = sys.argv[2]
        generate_for_category(category)
    elif cmd == "--group" and len(sys.argv) >= 3:
        group_name = sys.argv[2]
        limit = 0
        if "--limit" in sys.argv:
            idx = sys.argv.index("--limit")
            if idx + 1 < len(sys.argv):
                limit = int(sys.argv[idx + 1])
        generate_for_group(group_name, limit)
    else:
        print(f"Unbekannter Befehl: {cmd}")
