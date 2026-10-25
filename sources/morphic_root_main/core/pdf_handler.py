"""
PDF Handler für Morphic Engine V1

Features:
- PDF-Export: Professionelle Scan-Reports als PDF
- PDF-Import: Extraktion von Daten aus externen Reports
- Analyse: Pattern-Erkennung für neue Gruppen/Remedies
"""

import json
import re
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass

# PDF-Libraries (optional)
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm, cm
    from reportlab.lib.colors import HexColor, black, white
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        Image, PageBreak, HRFlowable
    )
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

try:
    import fitz  # PyMuPDF für Import
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False


# Farben für PDF
COLORS = {
    'primary': '#00d4ff',
    'secondary': '#1a1a2e',
    'success': '#00C853',
    'warning': '#FFD600',
    'danger': '#D50000',
    'text': '#333333',
    'light': '#f5f5f5',
}


@dataclass
class PDFConfig:
    """Konfiguration für PDF-Export"""
    title: str = "Morphic Engine V1 - Scan Report"
    author: str = "Morphic Engine"
    include_logo: bool = True
    include_3d_link: bool = True
    include_recommendations: bool = True
    include_confidence: bool = True
    page_size: tuple = A4 if REPORTLAB_AVAILABLE else (595, 842)


def generate_pdf_report(
    scan_result: Dict,
    output_path: str,
    config: Optional[PDFConfig] = None
) -> str:
    """
    Generiert professionellen PDF-Report aus Scan-Ergebnis.
    
    Args:
        scan_result: Scan-Ergebnis Dictionary
        output_path: Ausgabe-Pfad für PDF
        config: Optionale PDF-Konfiguration
    
    Returns:
        Pfad zur generierten PDF-Datei
    """
    if not REPORTLAB_AVAILABLE:
        raise ImportError("reportlab nicht installiert. Run: pip install reportlab")
    
    config = config or PDFConfig()
    
    # Daten extrahieren
    client_name = scan_result.get('client_name', 'Unbekannt')
    profile = scan_result.get('profile', 'unknown')
    focus = scan_result.get('focus', '')
    items = scan_result.get('top_items', [])[:20]
    h_level = scan_result.get('h_level', 0)
    entropy_source = scan_result.get('entropy_source', 'unknown')
    confidence = scan_result.get('confidence', {})
    timestamp = scan_result.get('timestamp', datetime.now().isoformat())
    
    # PDF erstellen
    doc = SimpleDocTemplate(
        output_path,
        pagesize=config.page_size,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )
    
    # Styles
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name='Title_Custom',
        parent=styles['Title'],
        fontSize=24,
        textColor=HexColor(COLORS['primary']),
        spaceAfter=20
    ))
    styles.add(ParagraphStyle(
        name='Heading_Custom',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=HexColor(COLORS['secondary']),
        spaceBefore=15,
        spaceAfter=10
    ))
    styles.add(ParagraphStyle(
        name='Body_Custom',
        parent=styles['Normal'],
        fontSize=10,
        textColor=HexColor(COLORS['text'])
    ))
    
    # Inhalt aufbauen
    story = []
    
    # Header
    story.append(Paragraph("🔬 Morphic Engine V1", styles['Title_Custom']))
    story.append(Paragraph("Resonanz-Analyse Report", styles['Heading_Custom']))
    story.append(Spacer(1, 10))
    
    # Meta-Info Tabelle
    meta_data = [
        ['Klient:', client_name],
        ['Profil:', profile],
        ['Fokus:', focus or '(keiner)'],
        ['Datum:', datetime.fromisoformat(timestamp).strftime('%d.%m.%Y %H:%M') if timestamp else '-'],
        ['H-Level:', f"{h_level:.4f} ({entropy_source})"],
    ]
    
    meta_table = Table(meta_data, colWidths=[4*cm, 10*cm])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), HexColor(COLORS['light'])),
        ('TEXTCOLOR', (0, 0), (-1, -1), HexColor(COLORS['text'])),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#cccccc')),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 20))
    
    # Konfidenz-Box
    if config.include_confidence and confidence:
        grade = confidence.get('grade', '?')
        overall = confidence.get('overall', 0)
        description = confidence.get('description', '')
        
        grade_color = {
            'A': COLORS['success'],
            'B': '#64DD17',
            'C': COLORS['warning'],
            'D': '#FF6D00',
            'F': COLORS['danger']
        }.get(grade, '#888888')
        
        story.append(Paragraph("📊 Konfidenz-Bewertung", styles['Heading_Custom']))
        conf_data = [
            [f"Grade: {grade}", f"{overall:.0%}", description]
        ]
        conf_table = Table(conf_data, colWidths=[3*cm, 3*cm, 8*cm])
        conf_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, 0), HexColor(grade_color)),
            ('TEXTCOLOR', (0, 0), (0, 0), white),
            ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('PADDING', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOX', (0, 0), (-1, -1), 1, HexColor('#cccccc')),
        ]))
        story.append(conf_table)
        story.append(Spacer(1, 20))
    
    # Top Befunde
    story.append(Paragraph("🔍 Top Befunde", styles['Heading_Custom']))
    
    if items:
        items_data = [['#', 'Befund', 'Gruppe', 'Score']]
        for i, item in enumerate(items, 1):
            score = item.get('score', 0)
            score_pct = f"{score*100:.1f}%" if score <= 1 else f"{score:.2f}"
            items_data.append([
                str(i),
                item.get('label', '?')[:40],
                item.get('group', '')[:20],
                score_pct
            ])
        
        items_table = Table(items_data, colWidths=[1*cm, 7*cm, 4*cm, 2*cm])
        items_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor(COLORS['secondary'])),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('PADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#cccccc')),
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),
            ('ALIGN', (3, 0), (3, -1), 'RIGHT'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, HexColor(COLORS['light'])]),
        ]))
        story.append(items_table)
    else:
        story.append(Paragraph("Keine Befunde vorhanden.", styles['Body_Custom']))
    
    story.append(Spacer(1, 20))
    
    # Footer
    story.append(HRFlowable(width="100%", thickness=1, color=HexColor('#cccccc')))
    story.append(Spacer(1, 10))
    story.append(Paragraph(
        f"Generiert am {datetime.now().strftime('%d.%m.%Y %H:%M')} | Morphic Engine V1",
        ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=HexColor('#888888'), alignment=TA_CENTER)
    ))
    
    # PDF schreiben
    doc.build(story)
    
    return output_path


def extract_from_pdf(pdf_path: str) -> Dict:
    """
    Extrahiert Daten aus einem PDF-Report.
    
    Args:
        pdf_path: Pfad zur PDF-Datei
    
    Returns:
        Dictionary mit extrahierten Daten
    """
    if not PYMUPDF_AVAILABLE:
        raise ImportError("PyMuPDF nicht installiert. Run: pip install PyMuPDF")
    
    doc = fitz.open(pdf_path)
    full_text = ""
    
    for page in doc:
        full_text += page.get_text()
    
    doc.close()
    
    # Pattern-Extraktion
    extracted = {
        'source_file': pdf_path,
        'extracted_at': datetime.now().isoformat(),
        'raw_text_length': len(full_text),
        'items': [],
        'metadata': {}
    }
    
    # Klient extrahieren
    client_match = re.search(r'Klient[:\s]+([^\n]+)', full_text, re.IGNORECASE)
    if client_match:
        extracted['metadata']['client'] = client_match.group(1).strip()
    
    # Profil extrahieren
    profile_match = re.search(r'Profil[:\s]+([^\n]+)', full_text, re.IGNORECASE)
    if profile_match:
        extracted['metadata']['profile'] = profile_match.group(1).strip()
    
    # Items extrahieren (Pattern: Label mit Score)
    item_patterns = [
        r'(\d+)\.\s+([^:]+):\s*score[=\s]*([0-9.]+)',  # "1. Item: score=0.5"
        r'([A-Za-zäöüÄÖÜß\s\-]+)\s*–\s*([A-Za-zäöüÄÖÜß\s\-]+).*?([0-9.]+)%',  # "Gruppe – Item ... 50%"
    ]
    
    for pattern in item_patterns:
        matches = re.findall(pattern, full_text, re.IGNORECASE)
        for match in matches:
            if len(match) >= 3:
                try:
                    score = float(match[-1])
                    if score > 1:
                        score = score / 100  # Prozent zu Dezimal
                    extracted['items'].append({
                        'label': match[1].strip() if len(match) > 2 else match[0].strip(),
                        'score': score,
                        'raw_match': str(match)
                    })
                except ValueError:
                    continue
    
    # Duplikate entfernen
    seen = set()
    unique_items = []
    for item in extracted['items']:
        key = item['label'].lower()
        if key not in seen:
            seen.add(key)
            unique_items.append(item)
    extracted['items'] = unique_items
    
    return extracted


def analyze_extracted_data(extracted: Dict) -> Dict:
    """
    Analysiert extrahierte PDF-Daten für neue Gruppen/Remedies.
    
    Args:
        extracted: Extrahierte Daten aus extract_from_pdf
    
    Returns:
        Analyse-Ergebnis mit Vorschlägen
    """
    items = extracted.get('items', [])
    
    # Kategorisierung nach Keywords
    categories = {
        'pathogen': [],
        'toxin': [],
        'organ': [],
        'supplement': [],
        'remedy': [],
        'unknown': []
    }
    
    pathogen_keywords = ['bakter', 'virus', 'parasit', 'pilz', 'candida', 'borrel']
    toxin_keywords = ['schwermetal', 'quecksilber', 'blei', 'cadmium', 'aluminium', 'pestizid']
    organ_keywords = ['leber', 'niere', 'herz', 'lunge', 'darm', 'magen', 'gehirn']
    supplement_keywords = ['vitamin', 'mineral', 'zink', 'magnesium', 'eisen', 'selen']
    remedy_keywords = ['homöopath', 'bach', 'spagyri', 'nosode', 'potenz']
    
    for item in items:
        label_lower = item['label'].lower()
        categorized = False
        
        for kw in pathogen_keywords:
            if kw in label_lower:
                categories['pathogen'].append(item)
                categorized = True
                break
        
        if not categorized:
            for kw in toxin_keywords:
                if kw in label_lower:
                    categories['toxin'].append(item)
                    categorized = True
                    break
        
        if not categorized:
            for kw in organ_keywords:
                if kw in label_lower:
                    categories['organ'].append(item)
                    categorized = True
                    break
        
        if not categorized:
            for kw in supplement_keywords:
                if kw in label_lower:
                    categories['supplement'].append(item)
                    categorized = True
                    break
        
        if not categorized:
            for kw in remedy_keywords:
                if kw in label_lower:
                    categories['remedy'].append(item)
                    categorized = True
                    break
        
        if not categorized:
            categories['unknown'].append(item)
    
    # Vorschläge generieren
    suggestions = []
    
    if len(categories['pathogen']) >= 3:
        suggestions.append({
            'type': 'new_group',
            'name': 'imported_pathogen_multiplex',
            'items': [i['label'] for i in categories['pathogen']],
            'reason': f"{len(categories['pathogen'])} Pathogen-Items gefunden"
        })
    
    if len(categories['remedy']) >= 3:
        suggestions.append({
            'type': 'new_remedy_group',
            'name': 'imported_remedies_multiplex',
            'items': [i['label'] for i in categories['remedy']],
            'reason': f"{len(categories['remedy'])} Remedy-Items gefunden"
        })
    
    return {
        'total_items': len(items),
        'categories': {k: len(v) for k, v in categories.items()},
        'category_details': categories,
        'suggestions': suggestions,
        'quality_score': min(1.0, len(items) / 20)  # Qualität basierend auf Item-Anzahl
    }


def get_pdf_capabilities() -> Dict:
    """Gibt verfügbare PDF-Funktionen zurück."""
    return {
        'export_available': REPORTLAB_AVAILABLE,
        'import_available': PYMUPDF_AVAILABLE,
        'install_commands': {
            'export': 'pip install reportlab',
            'import': 'pip install PyMuPDF'
        }
    }
