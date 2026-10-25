"""
Generator für Item-Beschreibungen.

Generiert einmalig alle Beschreibungen für Items aus allen Gruppen
und speichert sie in SQLite-Datenbank für schnellen Zugriff.
"""

import sys
import time
from pathlib import Path
from typing import List, Tuple, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

# Füge Projekt-Root zum Path hinzu
sys.path.insert(0, str(Path(__file__).parent))

from core.db import get_descriptions_db
from core.llm import get_ollama_client, OllamaClient
from core.subgroups.procedural_groups import _GROUP_LABELS

# Thread-Lock für Datenbank-Zugriff
_db_lock = Lock()


def collect_all_items() -> List[Tuple[str, str, List[float]]]:
    """
    Sammelt alle Items aus allen Gruppen.
    
    Returns:
        Liste von (label, group_name, [rate_min, rate_max]) Tupeln
    """
    items = []
    
    for group_key, group_data in _GROUP_LABELS.items():
        # Gruppe kann Liste oder Dictionary sein
        if isinstance(group_data, list):
            group_items = group_data
        elif isinstance(group_data, dict):
            group_items = group_data.get("items", [])
        else:
            continue
        
        for item in group_items:
            if isinstance(item, dict):
                label = item.get("label", "")
                rates = item.get("rates", [])
            elif isinstance(item, str):
                label = item
                rates = []
            else:
                continue
            
            if label:
                items.append((label, group_key, rates))
    
    return items


def process_single_item(
    item_data: Tuple[str, str, List[float]],
    client: OllamaClient,
    db,
    quality_score: float = 0.8
) -> Tuple[bool, str]:
    """
    Verarbeitet ein einzelnes Item (für Threading).
    
    Args:
        item_data: (label, group, rates)
        client: Ollama Client
        db: Datenbank-Instanz
        quality_score: Qualitätsscore
    
    Returns:
        (success, message)
    """
    label, group, rates = item_data
    
    try:
        # Generiere Beschreibung
        description = client.generate_description(label, group, rates if rates else None)
        
        if description and description != "-":
            # Speichere in Datenbank (mit Lock)
            rate_min = rates[0] if rates and len(rates) > 0 else None
            rate_max = rates[1] if rates and len(rates) > 1 else None
            
            with _db_lock:
                success = db.add_description(
                    label=label,
                    group_name=group,
                    description=description,
                    rate_min=rate_min,
                    rate_max=rate_max,
                    source="ollama",
                    quality_score=quality_score
                )
            
            if success:
                return (True, f"✓ {description[:60]}...")
            else:
                return (False, "❌ Fehler beim Speichern")
        else:
            return (False, "⚠ Keine Beschreibung generiert")
    
    except Exception as e:
        return (False, f"❌ Fehler: {e}")


def generate_all_descriptions(
    batch_size: int = 10,
    skip_existing: bool = True,
    quality_threshold: float = 0.5,
    num_threads: int = 4,
    model: str = "phi3:latest"
):
    """
    Generiert Beschreibungen für alle Items.
    
    Args:
        batch_size: Anzahl Items pro Batch
        skip_existing: Überspringe Items mit existierenden Beschreibungen
        quality_threshold: Minimale Qualität für Überspringen
    """
    print("=" * 70)
    print("BESCHREIBUNGS-GENERATOR (PARALLEL)")
    print("=" * 70)
    
    # Initialisiere Datenbank
    db = get_descriptions_db()
    print(f"\n✓ Datenbank: {db.db_path}")
    
    # Initialisiere Ollama
    client = get_ollama_client(model=model)
    if not client or not client.available:
        print("\n❌ Ollama nicht verfügbar!")
        print("\nStarte Ollama:")
        print("  1. ollama serve")
        print(f"  2. ollama pull {model}")
        return
    
    print(f"✓ Ollama: {client.model}")
    print(f"✓ Threads: {num_threads} (parallele Verarbeitung)")
    
    # Sammle alle Items
    print("\nSammle Items aus allen Gruppen...")
    all_items = collect_all_items()
    print(f"✓ Gefunden: {len(all_items)} Items in {len(_GROUP_LABELS)} Gruppen")
    
    # Filtere bereits vorhandene
    if skip_existing:
        print("\nPrüfe existierende Beschreibungen...")
        items_to_generate = []
        for label, group, rates in all_items:
            info = db.get_full_info(label, group)
            if not info or info.get('quality_score', 0.0) < quality_threshold:
                items_to_generate.append((label, group, rates))
        
        print(f"✓ Zu generieren: {len(items_to_generate)} Items")
        print(f"  (Übersprungen: {len(all_items) - len(items_to_generate)} Items)")
    else:
        items_to_generate = all_items
    
    if not items_to_generate:
        print("\n✓ Alle Beschreibungen bereits vorhanden!")
        print_stats(db)
        return
    
    # Generiere Beschreibungen (PARALLEL)
    print("\n" + "=" * 70)
    print("STARTE PARALLELE GENERIERUNG")
    print("=" * 70)
    
    total = len(items_to_generate)
    success_count = 0
    error_count = 0
    start_time = time.time()
    completed = 0
    
    # Erstelle separate Clients für jeden Thread
    clients = [OllamaClient(model=model) for _ in range(num_threads)]
    
    # Parallele Verarbeitung mit ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        # Submitte alle Tasks
        future_to_item = {
            executor.submit(process_single_item, item, clients[i % num_threads], db): (i, item)
            for i, item in enumerate(items_to_generate)
        }
        
        # Verarbeite abgeschlossene Tasks
        for future in as_completed(future_to_item):
            idx, (label, group, rates) = future_to_item[future]
            completed += 1
            
            try:
                success, message = future.result()
                
                if success:
                    success_count += 1
                    print(f"[{completed}/{total}] {label}: {message}")
                else:
                    error_count += 1
                    print(f"[{completed}/{total}] {label}: {message}")
            
            except Exception as e:
                error_count += 1
                print(f"[{completed}/{total}] {label}: ❌ Exception: {e}")
            
            # Fortschritt
            if completed % batch_size == 0:
                elapsed = time.time() - start_time
                rate = completed / elapsed if elapsed > 0 else 0
                remaining = (total - completed) / rate if rate > 0 else 0
                print(f"\n  Fortschritt: {completed}/{total} ({completed/total*100:.1f}%)")
                print(f"  Geschwindigkeit: {rate:.1f} Items/s ({rate*num_threads:.1f} effektiv)")
                print(f"  Verbleibend: ~{remaining/60:.1f} Min\n")
    
    # Zusammenfassung
    elapsed = time.time() - start_time
    print("\n" + "=" * 70)
    print("GENERIERUNG ABGESCHLOSSEN")
    print("=" * 70)
    print(f"\n✓ Erfolgreich: {success_count}")
    print(f"❌ Fehler: {error_count}")
    print(f"⏱ Zeit: {elapsed/60:.1f} Min ({elapsed/total:.2f}s pro Item)")
    
    print_stats(db)


def print_stats(db):
    """Gibt Datenbank-Statistiken aus."""
    stats = db.get_stats()
    
    print("\n" + "=" * 70)
    print("DATENBANK-STATISTIKEN")
    print("=" * 70)
    print(f"\nGesamt: {stats.get('total', 0)} Beschreibungen")
    print(f"Durchschnittliche Qualität: {stats.get('avg_quality', 0.0):.2f}")
    
    print("\nNach Quelle:")
    for source, count in stats.get('by_source', {}).items():
        print(f"  - {source}: {count}")
    
    print("\nTop 10 Gruppen:")
    for group, count in stats.get('by_group', {}).items():
        print(f"  - {group}: {count}")


def export_descriptions():
    """Exportiert Beschreibungen als JSON."""
    db = get_descriptions_db()
    output_path = "data/descriptions_export.json"
    db.export_to_json(output_path)
    print(f"\n✓ Exportiert nach: {output_path}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Beschreibungs-Generator")
    parser.add_argument(
        "--mode",
        choices=["update", "regenerate", "export", "stats"],
        default="update",
        help="Modus: update (nur fehlende), regenerate (alle), export, stats"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=10,
        help="Batch-Größe für Fortschrittsanzeige"
    )
    parser.add_argument(
        "--threads",
        type=int,
        default=4,
        help="Anzahl paralleler Threads (Standard: 4)"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="phi3:latest",
        help="Ollama-Modell (phi3:latest, tinyllama, etc.)"
    )
    
    args = parser.parse_args()
    
    if args.mode == "update":
        generate_all_descriptions(
            skip_existing=True,
            quality_threshold=0.5,
            num_threads=args.threads,
            model=args.model,
            batch_size=args.batch_size
        )
    elif args.mode == "regenerate":
        print("\n⚠ WARNUNG: Alle existierenden Beschreibungen werden überschrieben!")
        response = input("Fortfahren? (ja/nein): ")
        if response.lower() in ['ja', 'j', 'yes', 'y']:
            generate_all_descriptions(
                skip_existing=False,
                num_threads=args.threads,
                model=args.model,
                batch_size=args.batch_size
            )
        else:
            print("Abgebrochen.")
    elif args.mode == "export":
        export_descriptions()
    elif args.mode == "stats":
        db = get_descriptions_db()
        print_stats(db)
