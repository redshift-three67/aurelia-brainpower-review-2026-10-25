"""
Pathogen-Remedy Linking Tool

Erstellt automatische Verknüpfungen zwischen Pathogenen und Remedies
basierend auf Keyword-Matching (Multiplex B).
"""

import sys
from pathlib import Path

# Füge Parent-Verzeichnis zum Path hinzu
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.remedy_service import (
    get_remedy_connection,
    link_remedy_to_pathogen,
    get_remedy_stats
)


def find_matching_remedies_for_pathogen(pathogen_id, pathogen_keywords, conn):
    """
    Findet passende Remedies für ein Pathogen basierend auf Keywords.
    
    Args:
        pathogen_id: ID des Pathogens
        pathogen_keywords: Keywords des Pathogens
        conn: DB-Verbindung
    
    Returns:
        Liste von (remedy_id, match_score) Tupeln
    """
    cursor = conn.cursor()
    
    matches = {}
    
    for keyword in pathogen_keywords:
        # Finde Remedies mit passendem Keyword
        cursor.execute("""
            SELECT DISTINCT r.id, r.name, rk.keyword
            FROM remedies r
            JOIN remedy_keywords rk ON r.id = rk.remedy_id
            WHERE rk.keyword LIKE ?
        """, (f"%{keyword}%",))
        
        for row in cursor.fetchall():
            remedy_id = row[0]
            
            if remedy_id not in matches:
                matches[remedy_id] = 0
            
            matches[remedy_id] += 1  # Score = Anzahl übereinstimmender Keywords
    
    # Sortiere nach Score
    sorted_matches = sorted(matches.items(), key=lambda x: -x[1])
    
    return sorted_matches[:10]  # Top 10


def link_all_pathogens_to_remedies(dry_run=False):
    """
    Verknüpft alle Pathogene mit passenden Remedies.
    
    Args:
        dry_run: Wenn True, nur analysieren ohne Verknüpfung
    """
    print("=" * 70)
    print("PATHOGEN-REMEDY LINKING (MULTIPLEX B)")
    print("=" * 70)
    print()
    
    if dry_run:
        print("🔍 DRY-RUN-MODUS (keine Verknüpfungen)")
        print()
    
    with get_remedy_connection() as conn:
        cursor = conn.cursor()
        
        # Hole alle Pathogene
        cursor.execute("""
            SELECT p.id, p.name, p.pathogen_type
            FROM pathogens p
            ORDER BY p.pathogen_type, p.name
        """)
        
        pathogens = cursor.fetchall()
        
        print(f"Gefunden: {len(pathogens)} Pathogene")
        print()
        
        total_links = 0
        pathogens_with_links = 0
        pathogens_without_links = 0
        
        for pathogen_id, pathogen_name, pathogen_type in pathogens:
            # Hole Keywords des Pathogens
            cursor.execute("""
                SELECT keyword
                FROM pathogen_keywords
                WHERE pathogen_id = ?
            """, (pathogen_id,))
            
            keywords = [row[0] for row in cursor.fetchall()]
            
            if not keywords:
                pathogens_without_links += 1
                continue
            
            # Finde passende Remedies
            matches = find_matching_remedies_for_pathogen(pathogen_id, keywords, conn)
            
            if not matches:
                pathogens_without_links += 1
                continue
            
            pathogens_with_links += 1
            
            # Verknüpfe Top-Matches
            for remedy_id, score in matches[:5]:  # Top 5
                if not dry_run:
                    link_remedy_to_pathogen(
                        pathogen_id=pathogen_id,
                        remedy_id=remedy_id,
                        priority=score
                    )
                
                total_links += 1
        
        if not dry_run:
            conn.commit()
    
    print()
    print("=" * 70)
    print("LINKING ABGESCHLOSSEN")
    print("=" * 70)
    print(f"Pathogene mit Links: {pathogens_with_links}")
    print(f"Pathogene ohne Links: {pathogens_without_links}")
    print(f"Gesamt Links erstellt: {total_links}")
    print()
    
    if not dry_run:
        # Statistiken
        stats = get_remedy_stats()
        print(f"Multiplex-Links in DB: {stats.get('multiplex_links', 0)}")
    
    print("=" * 70)


def show_example_links(limit=5):
    """
    Zeigt Beispiel-Verknüpfungen an.
    
    Args:
        limit: Anzahl Beispiele
    """
    print()
    print("=" * 70)
    print("BEISPIEL-VERKNÜPFUNGEN")
    print("=" * 70)
    print()
    
    with get_remedy_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT p.name, r.name, rpm.priority
            FROM remedy_pathogen_map rpm
            JOIN pathogens p ON rpm.pathogen_id = p.id
            JOIN remedies r ON rpm.remedy_id = r.id
            ORDER BY rpm.priority DESC
            LIMIT ?
        """, (limit,))
        
        for i, (pathogen_name, remedy_name, priority) in enumerate(cursor.fetchall(), 1):
            print(f"{i}. {pathogen_name}")
            print(f"   → {remedy_name}")
            print(f"   Score: {priority}")
            print()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Verknüpft Pathogene mit Remedies')
    parser.add_argument('--dry-run', action='store_true', help='Nur analysieren, nicht verknüpfen')
    parser.add_argument('--examples', action='store_true', help='Zeige Beispiel-Verknüpfungen')
    
    args = parser.parse_args()
    
    if args.examples:
        show_example_links(limit=10)
    else:
        link_all_pathogens_to_remedies(dry_run=args.dry_run)
        
        if not args.dry_run:
            show_example_links(limit=5)
