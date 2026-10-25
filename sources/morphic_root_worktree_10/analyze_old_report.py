#!/usr/bin/env python3

import re
from pathlib import Path

# Analysiere die alte Berichtsstruktur
old_report = Path("../history/Deisenhofer_Klaus_09041966_Augsburg/20251111_174159.html")

if old_report.exists():
    content = old_report.read_text(encoding='utf-8')
    
    print("=== ALTE BERICHTSSTRUKTUR ANALYSE ===")
    
    # Extrahiere Hauptsektionen
    sections = re.split(r'<h[12]>', content)
    print(f"Anzahl Hauptsektionen: {len(sections)}")
    
    # Finde alle H2 und H3 Überschriften
    h2_matches = re.findall(r'<h2>([^<]+)</h2>', content)
    h3_matches = re.findall(r'<h3>([^<]+)</h3>', content)
    
    print("\nH2 Überschriften:")
    for i, h2 in enumerate(h2_matches):
        print(f"  {i+1}. {h2}")
    
    print("\nH3 Überschriften:")
    for i, h3 in enumerate(h3_matches):
        print(f"  {i+1}. {h3}")
    
    # Analysiere Tabellen
    table_matches = re.findall(r'<table[^>]*>(.*?)</table>', content, re.DOTALL)
    print(f"\nAnzahl Tabellen: {len(table_matches)}")
    
    # Analysiere Tabellenheader
    for i, table in enumerate(table_matches):
        headers = re.findall(r'<th>([^<]+)</th>', table)
        if headers:
            print(f"  Tabelle {i+1} Header: {', '.join(headers)}")
    
    # Analysiere <pre> Blöcke (Deutung)
    pre_matches = re.findall(r'<pre>(.*?)</pre>', content, re.DOTALL)
    print(f"\nAnzahl <pre> Blöcke: {len(pre_matches)}")
    if pre_matches:
        print("Deutung Inhalt (erste 200 Zeichen):")
        print(pre_matches[0][:200] + "...")

else:
    print("Alte Berichtsdatei nicht gefunden!")
