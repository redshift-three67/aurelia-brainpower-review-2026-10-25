"""
Debug-Script: Zeigt alle Zeilen im PDF, die die fehlenden Namen enthalten könnten.
"""

import sys
from pathlib import Path

try:
    import PyPDF2
except ImportError:
    print("❌ PyPDF2 fehlt.")
    sys.exit(1)

def debug_missing_names(pdf_path):
    print(f"\n🔍 SUCHE NACH FEHLENDEN NAMEN IN: {pdf_path}")
    print("=" * 70)
    
    # Die 5 Vermissten
    search_terms = [
        "BURBUR",
        "PINELLA", 
        "NUTRA",
        "BBS",
        "BRL",
        "BRT",
        "SERRA",
        "PEPTASE",
        "SERRAPEPTASE"
    ]
    
    with open(pdf_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        
        for page_num, page in enumerate(reader.pages):
            text = page.extract_text()
            lines = text.split('\n')
            
            for line in lines:
                line = line.strip()
                if not line: continue
                
                upper_line = line.upper()
                
                # Prüfe, ob einer der Suchbegriffe vorkommt
                for term in search_terms:
                    if term in upper_line:
                        # Zeige die Zeile, wenn sie kurz ist (Überschrift)
                        if len(line) < 80:
                            print(f"Seite {page_num+1:3d} | {line}")
                        break

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python debug_pdf_names.py <pdf_path>")
        sys.exit(1)
        
    debug_missing_names(sys.argv[1])
