#!/usr/bin/env python3
"""
Volltextsuche für Klienten-Analysen.

Durchsucht alle Klienten-Ordner (Archive, Deutung, Trends) nach Stichwörtern.

Verwendung:
    python tools/search_client_data.py "Stichwort"
    python tools/search_client_data.py "Stichwort" --client "Nachname"
    python tools/search_client_data.py "Stichwort" --type json
    python tools/search_client_data.py "Stichwort" --type html --limit 20
"""

import argparse
import json
import re
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

# Produktions-Pfade
ARCHIVE_DIR = Path(r"C:\Benutzer_Archive_Start")
TRENDS_DIR = Path(r"C:\Benutzer_Trends_Start")
DEUTUNG_DIR = Path(r"C:\Benutzer_Deutung_Start")

ALL_DIRS = [ARCHIVE_DIR, TRENDS_DIR, DEUTUNG_DIR]


@dataclass
class SearchResult:
    """Einzelnes Suchergebnis."""
    file_path: Path
    client_name: str
    file_type: str  # json, html, txt
    source_dir: str  # archive, trends, deutung
    match_context: str
    match_count: int
    timestamp: Optional[datetime] = None


def extract_timestamp_from_path(path: Path) -> Optional[datetime]:
    """Extrahiert Zeitstempel aus Datei- oder Ordnernamen."""
    # Suche nach YYYYMMDD_HHMMSS Pattern
    pattern = r'(\d{8}_\d{6})'
    match = re.search(pattern, str(path))
    if match:
        try:
            return datetime.strptime(match.group(1), '%Y%m%d_%H%M%S')
        except ValueError:
            pass
    return None


def search_in_json(file_path: Path, keyword: str, case_sensitive: bool = False) -> Tuple[int, str]:
    """Durchsucht eine JSON-Datei nach einem Stichwort."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if not case_sensitive:
            search_content = content.lower()
            search_keyword = keyword.lower()
        else:
            search_content = content
            search_keyword = keyword
        
        # Zähle Treffer
        count = search_content.count(search_keyword)
        
        if count == 0:
            return 0, ""
        
        # Finde Kontext um ersten Treffer
        idx = search_content.find(search_keyword)
        start = max(0, idx - 50)
        end = min(len(content), idx + len(keyword) + 50)
        context = content[start:end].replace('\n', ' ').strip()
        if start > 0:
            context = "..." + context
        if end < len(content):
            context = context + "..."
        
        return count, context
        
    except Exception as e:
        return 0, f"Fehler: {e}"


def search_in_html(file_path: Path, keyword: str, case_sensitive: bool = False) -> Tuple[int, str]:
    """Durchsucht eine HTML-Datei nach einem Stichwort (ohne HTML-Tags)."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Entferne HTML-Tags für bessere Suche
        text_content = re.sub(r'<[^>]+>', ' ', content)
        text_content = re.sub(r'\s+', ' ', text_content)
        
        if not case_sensitive:
            search_content = text_content.lower()
            search_keyword = keyword.lower()
        else:
            search_content = text_content
            search_keyword = keyword
        
        count = search_content.count(search_keyword)
        
        if count == 0:
            return 0, ""
        
        # Finde Kontext
        idx = search_content.find(search_keyword)
        start = max(0, idx - 50)
        end = min(len(text_content), idx + len(keyword) + 50)
        context = text_content[start:end].strip()
        if start > 0:
            context = "..." + context
        if end < len(text_content):
            context = context + "..."
        
        return count, context
        
    except Exception as e:
        return 0, f"Fehler: {e}"


def search_in_txt(file_path: Path, keyword: str, case_sensitive: bool = False) -> Tuple[int, str]:
    """Durchsucht eine TXT-Datei nach einem Stichwort."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if not case_sensitive:
            search_content = content.lower()
            search_keyword = keyword.lower()
        else:
            search_content = content
            search_keyword = keyword
        
        count = search_content.count(search_keyword)
        
        if count == 0:
            return 0, ""
        
        idx = search_content.find(search_keyword)
        start = max(0, idx - 50)
        end = min(len(content), idx + len(keyword) + 50)
        context = content[start:end].replace('\n', ' ').strip()
        if start > 0:
            context = "..." + context
        if end < len(content):
            context = context + "..."
        
        return count, context
        
    except Exception as e:
        return 0, f"Fehler: {e}"


def get_source_dir_name(file_path: Path) -> str:
    """Bestimmt den Quell-Ordner (archive, trends, deutung)."""
    path_str = str(file_path).lower()
    if 'archive' in path_str:
        return 'archive'
    elif 'trend' in path_str:
        return 'trends'
    elif 'deutung' in path_str:
        return 'deutung'
    return 'unknown'


def get_client_name_from_path(file_path: Path) -> str:
    """Extrahiert Klientennamen aus Pfad."""
    # Typischer Pfad: C:\Benutzer_Archive_Start\Nachname_Vorname_Datum_Ort\...
    parts = file_path.parts
    for part in parts:
        if '_' in part and not part.startswith('20'):  # Nicht Timestamp
            # Prüfe ob es wie ein Klientenname aussieht
            if re.match(r'^[A-Za-zäöüÄÖÜß-]+_[A-Za-zäöüÄÖÜß-]+_\d+_', part):
                return part
    return "Unbekannt"


def search_all_files(
    keyword: str,
    client_filter: Optional[str] = None,
    file_type_filter: Optional[str] = None,
    case_sensitive: bool = False,
    limit: int = 50
) -> List[SearchResult]:
    """
    Durchsucht alle Klienten-Dateien nach einem Stichwort.
    
    Args:
        keyword: Suchbegriff
        client_filter: Optional - nur Dateien dieses Klienten durchsuchen
        file_type_filter: Optional - nur bestimmte Dateitypen (json, html, txt)
        case_sensitive: Groß-/Kleinschreibung beachten
        limit: Maximale Anzahl Ergebnisse
    
    Returns:
        Liste von SearchResult Objekten
    """
    results: List[SearchResult] = []
    
    # Bestimme zu durchsuchende Dateitypen
    extensions = []
    if file_type_filter:
        extensions = [f".{file_type_filter.lower()}"]
    else:
        extensions = [".json", ".html", ".txt"]
    
    # Durchsuche alle Verzeichnisse
    for base_dir in ALL_DIRS:
        if not base_dir.exists():
            continue
        
        # Finde alle relevanten Dateien
        for ext in extensions:
            for file_path in base_dir.rglob(f"*{ext}"):
                # Client-Filter anwenden
                if client_filter:
                    if client_filter.lower() not in str(file_path).lower():
                        continue
                
                # Durchsuche Datei
                if ext == ".json":
                    count, context = search_in_json(file_path, keyword, case_sensitive)
                elif ext == ".html":
                    count, context = search_in_html(file_path, keyword, case_sensitive)
                else:
                    count, context = search_in_txt(file_path, keyword, case_sensitive)
                
                if count > 0:
                    results.append(SearchResult(
                        file_path=file_path,
                        client_name=get_client_name_from_path(file_path),
                        file_type=ext[1:],  # ohne Punkt
                        source_dir=get_source_dir_name(file_path),
                        match_context=context,
                        match_count=count,
                        timestamp=extract_timestamp_from_path(file_path)
                    ))
                
                if len(results) >= limit:
                    break
            
            if len(results) >= limit:
                break
        
        if len(results) >= limit:
            break
    
    # Sortiere nach Anzahl Treffer (absteigend)
    results.sort(key=lambda x: x.match_count, reverse=True)
    
    return results[:limit]


def print_results(results: List[SearchResult], keyword: str) -> None:
    """Gibt Suchergebnisse formatiert aus."""
    print("")
    print("=" * 80)
    print(f"🔍 SUCHERGEBNISSE FÜR: '{keyword}'")
    print("=" * 80)
    print(f"   Gefunden: {len(results)} Dateien")
    print("")
    
    if not results:
        print("   Keine Treffer gefunden.")
        return
    
    # Gruppiere nach Klient
    by_client: Dict[str, List[SearchResult]] = {}
    for r in results:
        if r.client_name not in by_client:
            by_client[r.client_name] = []
        by_client[r.client_name].append(r)
    
    for client_name, client_results in by_client.items():
        print(f"📁 {client_name}")
        print("-" * 60)
        
        for r in client_results:
            ts_str = r.timestamp.strftime('%d.%m.%Y %H:%M') if r.timestamp else "?"
            print(f"   [{r.source_dir}] {r.file_type.upper()} | {ts_str} | {r.match_count}x")
            print(f"   📄 {r.file_path.name}")
            if r.match_context:
                # Kürze Kontext auf 100 Zeichen
                ctx = r.match_context[:100] + "..." if len(r.match_context) > 100 else r.match_context
                print(f"   💬 {ctx}")
            print("")
        
        print("")


def main():
    parser = argparse.ArgumentParser(
        description="Volltextsuche in Klienten-Analysen",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Beispiele:
  python tools/search_client_data.py "Borreliose"
  python tools/search_client_data.py "Leber" --client "Deisenhofer"
  python tools/search_client_data.py "Entgiftung" --type html
  python tools/search_client_data.py "Trauma" --limit 10 --case-sensitive
        """
    )
    
    parser.add_argument("keyword", help="Suchbegriff")
    parser.add_argument("--client", "-c", help="Nur Dateien dieses Klienten durchsuchen")
    parser.add_argument("--type", "-t", choices=["json", "html", "txt"], help="Nur bestimmte Dateitypen")
    parser.add_argument("--limit", "-l", type=int, default=50, help="Maximale Anzahl Ergebnisse (Standard: 50)")
    parser.add_argument("--case-sensitive", "-s", action="store_true", help="Groß-/Kleinschreibung beachten")
    parser.add_argument("--json-output", "-j", action="store_true", help="Ausgabe als JSON")
    
    args = parser.parse_args()
    
    print(f"🔍 Suche nach: '{args.keyword}'")
    if args.client:
        print(f"   Filter: Klient enthält '{args.client}'")
    if args.type:
        print(f"   Filter: Nur {args.type.upper()} Dateien")
    
    results = search_all_files(
        keyword=args.keyword,
        client_filter=args.client,
        file_type_filter=args.type,
        case_sensitive=args.case_sensitive,
        limit=args.limit
    )
    
    if args.json_output:
        # JSON-Ausgabe
        output = []
        for r in results:
            output.append({
                "file_path": str(r.file_path),
                "client_name": r.client_name,
                "file_type": r.file_type,
                "source_dir": r.source_dir,
                "match_context": r.match_context,
                "match_count": r.match_count,
                "timestamp": r.timestamp.isoformat() if r.timestamp else None
            })
        print(json.dumps(output, indent=2, ensure_ascii=False))
    else:
        print_results(results, args.keyword)


if __name__ == "__main__":
    main()
