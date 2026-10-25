"""
PDF-Analyse-Tool für Morphic Engine

Analysiert PDF-Dateien und extrahiert Struktur und Inhalte.
Verwendet PyPDF2 für PDF-Extraktion.
"""

import sys
from pathlib import Path

# Füge Parent-Verzeichnis zum Path hinzu
sys.path.insert(0, str(Path(__file__).parent.parent))


def analyze_pdf_structure(pdf_path: Path) -> dict:
    """
    Analysiert die Struktur eines PDFs.
    
    Args:
        pdf_path: Pfad zur PDF-Datei
        
    Returns:
        Dictionary mit Struktur-Informationen
    """
    try:
        import PyPDF2
    except ImportError:
        print("❌ PyPDF2 nicht installiert. Bitte installieren mit: pip install PyPDF2")
        return {}
    
    result = {
        "file": str(pdf_path),
        "size_mb": pdf_path.stat().st_size / (1024 * 1024),
        "pages": 0,
        "metadata": {},
        "first_page_text": "",
        "toc_entries": [],
        "sample_pages": []
    }
    
    try:
        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            
            # Basis-Informationen
            result["pages"] = len(reader.pages)
            
            # Metadata
            if reader.metadata:
                result["metadata"] = {
                    "title": reader.metadata.get('/Title', 'N/A'),
                    "author": reader.metadata.get('/Author', 'N/A'),
                    "subject": reader.metadata.get('/Subject', 'N/A'),
                    "creator": reader.metadata.get('/Creator', 'N/A'),
                }
            
            # Erste Seite
            if len(reader.pages) > 0:
                first_page = reader.pages[0]
                result["first_page_text"] = first_page.extract_text()[:500]
            
            # Sample-Seiten (erste 3 und letzte)
            sample_indices = [0, 1, 2, len(reader.pages) - 1] if len(reader.pages) > 3 else list(range(len(reader.pages)))
            
            for idx in sample_indices:
                if 0 <= idx < len(reader.pages):
                    page = reader.pages[idx]
                    text = page.extract_text()
                    result["sample_pages"].append({
                        "page": idx + 1,
                        "text_preview": text[:300] if text else "(Kein Text extrahierbar)"
                    })
    
    except Exception as e:
        result["error"] = str(e)
    
    return result


def print_analysis(analysis: dict):
    """Gibt die Analyse formatiert aus."""
    print("\n" + "=" * 70)
    print("PDF-ANALYSE")
    print("=" * 70)
    print(f"\n📄 Datei: {analysis.get('file', 'N/A')}")
    print(f"📊 Größe: {analysis.get('size_mb', 0):.2f} MB")
    print(f"📑 Seiten: {analysis.get('pages', 0)}")
    
    if analysis.get('error'):
        print(f"\n❌ Fehler: {analysis['error']}")
        return
    
    # Metadata
    metadata = analysis.get('metadata', {})
    if metadata:
        print("\n📋 METADATA:")
        print(f"  Titel:   {metadata.get('title', 'N/A')}")
        print(f"  Autor:   {metadata.get('author', 'N/A')}")
        print(f"  Thema:   {metadata.get('subject', 'N/A')}")
        print(f"  Creator: {metadata.get('creator', 'N/A')}")
    
    # Erste Seite
    first_page = analysis.get('first_page_text', '')
    if first_page:
        print("\n📝 ERSTE SEITE (Vorschau):")
        print("-" * 70)
        print(first_page[:400])
        if len(first_page) > 400:
            print("...")
    
    # Sample-Seiten
    samples = analysis.get('sample_pages', [])
    if samples:
        print("\n📖 SAMPLE-SEITEN:")
        for sample in samples:
            print(f"\n  Seite {sample['page']}:")
            print("  " + "-" * 66)
            preview = sample['text_preview'].replace('\n', '\n  ')
            print(f"  {preview}")
            if len(sample['text_preview']) >= 300:
                print("  ...")
    
    print("\n" + "=" * 70)


def main():
    """Hauptfunktion."""
    if len(sys.argv) < 2:
        print("Verwendung:")
        print("  python analyze_pdf.py <pdf-datei>")
        print("\nBeispiel:")
        print("  python analyze_pdf.py imports/Antihomotoxikologie.pdf")
        sys.exit(1)
    
    pdf_path = Path(sys.argv[1])
    
    if not pdf_path.exists():
        print(f"❌ Datei nicht gefunden: {pdf_path}")
        sys.exit(1)
    
    if not pdf_path.suffix.lower() == '.pdf':
        print(f"❌ Keine PDF-Datei: {pdf_path}")
        sys.exit(1)
    
    print(f"\n🔍 Analysiere PDF: {pdf_path.name}")
    
    analysis = analyze_pdf_structure(pdf_path)
    print_analysis(analysis)


if __name__ == "__main__":
    main()
