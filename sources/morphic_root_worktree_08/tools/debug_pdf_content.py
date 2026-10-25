"""
PDF Content Debugger
Liest spezifische Seitenbereiche, um Strukturen (Inhaltsverzeichnis, Index) zu finden.
"""

import sys
from pathlib import Path
import PyPDF2

def debug_pages(pdf_path, start_page, end_page):
    print(f"\n🔍 Untersuche Seiten {start_page}-{end_page} in {pdf_path.name}")
    print("=" * 70)
    
    try:
        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            
            for i in range(start_page, min(end_page + 1, len(reader.pages))):
                page = reader.pages[i]
                text = page.extract_text()
                
                print(f"\n📄 SEITE {i+1}")
                print("-" * 70)
                # Zeige nur die ersten 20 Zeilen jeder Seite (reicht meist für Struktur)
                lines = text.split('\n')
                for line in lines[:20]:
                    print(line)
                print("...")
                
    except Exception as e:
        print(f"❌ Fehler: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python debug_pdf_content.py <pdf_path> [start_page] [end_page]")
        sys.exit(1)
        
    path = Path(sys.argv[1])
    start = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    end = int(sys.argv[3]) if len(sys.argv) > 3 else 10
    
    debug_pages(path, start, end)
