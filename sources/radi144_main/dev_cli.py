import sys
import os
import argparse
import random
import time
import math
import struct

from app.bootstrap import CLI_PROFILE, enforce_profile

enforce_profile(CLI_PROFILE)

import numpy as np
from datetime import datetime

import json
from pathlib import Path

from app.services.client_registry_service import ClientRegistryService
from app.services.report_manifest_service import ReportManifestService
from app.services.session_archive_service import SessionArchiveService
# Optional CLI Autocomplete
try:
    import argcomplete
    HAS_ARGCOMPLETE = True
except ImportError:
    HAS_ARGCOMPLETE = False

# Force output to be unbuffered and UTF-8
if sys.stdout.encoding.lower() != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Pfad setup
sys.path.append(os.getcwd())

# Paletten laden
PALETTES = {}
try:
    # Use utf-8-sig to handle BOM if present
    with open(os.path.join(os.getcwd(), 'palettes.json'), 'r', encoding='utf-8-sig') as f:
        PALETTES = json.load(f)
except Exception as e:
    print(f"Warnung: Konnte palettes.json nicht laden ({e}). Nutze Standards.", flush=True)

# Preset Profile laden
PRESETS = {}
try:
    with open(os.path.join(os.getcwd(), 'preset_profiles.json'), 'r', encoding='utf-8-sig') as f:
        PRESETS = json.load(f)
except Exception as e:
    print(f"Info: Konnte preset_profiles.json nicht laden ({e}).", flush=True)

# Ensure Standard Palette exists in PALETTES
if "Radionik (Standard)" not in PALETTES:
    PALETTES["Radionik (Standard)"] = {
        "0": "#FFFFFF", "1": "#FF0000", "2": "#FF7F00", "3": "#FFFF00", 
        "4": "#00FF00", "5": "#00FFFF", "6": "#0000FF", "7": "#8B00FF", 
        "8": "#FF00FF", "9": "#FFD700"
    }

# Globale Flags f\u00fcr Verf\u00fcgbarkeit
HAS_EXPORT_LIBS = False
HAS_TORCH = False

# Imports f\u00fcr Export pr\u00fcefen
try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    import openpyxl
    from openpyxl.styles import PatternFill, Font, Alignment
    
    # ReportLab Font Registration for Umlaute
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    try:
        # Versuch 1: CWD
        font_path = 'arial.ttf'
        if not os.path.exists(font_path):
            # Versuch 2: Windows Fonts
            font_path = r'C:\Windows\Fonts\arial.ttf'
            
        if os.path.exists(font_path):
            pdfmetrics.registerFont(TTFont('Arial', font_path))
            FONT_NAME = 'Arial'
        else:
            # Fallback
            FONT_NAME = 'Helvetica'
    except:
        FONT_NAME = 'Helvetica'

    HAS_EXPORT_LIBS = True
except ImportError as e:
    print(f"WARNUNG: Export-Module fehlen ({e}). Keine PDF/Excel Ausgabe m\u00f6glich.", flush=True)
    print("Bitte f\u00fchren Sie die 'install_dependencies.bat' im Projektverzeichnis aus,", flush=True)
    print("oder nutzen Sie: pip install reportlab openpyxl", flush=True)
    FONT_NAME = 'Helvetica'

def get_contrast_color(hex_color):
    """Ermittelt die passende Textfarbe (Schwarz/Weiss) basierend auf Helligkeit."""
    hex_color = hex_color.lstrip('#')
    if len(hex_color) != 6:
        return "#000000"
    
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    
    # Helligkeit nach ITU-R BT.709
    luminance = (0.2126 * r + 0.7152 * g + 0.0722 * b)
    
    # Grenzwert 128 (oder 0.5 bei 0-1) ist Standard, aber oft ist 140 besser lesbar
    return "#000000" if luminance > 128 else "#FFFFFF"

def ensure_output_dir(client_name, timestamp_str):
    """Erstellt einen ordnerbasierten Archiv-Pfad."""
    base_dir = os.path.join(os.getcwd(), "Analysen")
    # Ordnername: YYYY-MM-DD_HH-MM_Name
    folder_name = f"{timestamp_str}_{client_name.replace(' ', '_')}"
    full_path = os.path.join(base_dir, folder_name)
    
    if not os.path.exists(full_path):
        os.makedirs(full_path)
    return full_path

def get_palette(name):
    """Holt die Palette oder den Standard."""
    # Special Case for Dynamic Palette (handled by Engine, but we need a placeholder here if called directly)
    if name == "Client Coherent (Auto)":
        return None 

    # Standard Radionik Palette als Fallback
    default = {
        "0": "#FFFFFF", "1": "#FF0000", "2": "#FF7F00", "3": "#FFFF00", 
        "4": "#00FF00", "5": "#00FFFF", "6": "#0000FF", "7": "#8B00FF", 
        "8": "#FF00FF", "9": "#FFD700"
    }
    
    raw_palette = PALETTES.get(name, default)
    # Ensure keys are ints for processing
    return {int(k): v for k, v in raw_palette.items()}

def save_session_template(args, client_data, full_name, focus_str):
    """Speichert die aktuelle Konfiguration als Template fuer spaeteres Wiederladen."""
    template_path = os.path.join(os.getcwd(), "data", "session_templates.json")
    
    try:
        templates_data = {"_meta": {"version": "1.5.0", "max_templates": 21}, "templates": []}
        if os.path.exists(template_path):
            with open(template_path, "r", encoding="utf-8") as f:
                templates_data = json.load(f)
        
        template = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "template_name": getattr(args, "template_name", ""),
            "client_name": full_name,
            "surname": getattr(args, "surname", ""),
            "firstname": getattr(args, "firstname", ""),
            "dob": getattr(args, "dob", ""),
            "place": getattr(args, "place", ""),
            "planet": getattr(args, "planet", ""),
            "focus": focus_str,
            "weight": getattr(args, "weight", "Sanft"),
            "palette": getattr(args, "palette", "Client Coherent (Auto)"),
            "mode": getattr(args, "mode", "quantum"),
            "hrv_sim": getattr(args, "hrv_sim", False),
            "quantum_active": getattr(args, "quantum_active", False),
            "use_planetary": getattr(args, "use_planetary", False),
            "emf_compensate": getattr(args, "emf_compensate", False),
            "amplifier": getattr(args, "amplifier", ""),
            "symmetry": getattr(args, "symmetry", "none"),
            "matrix_size": getattr(args, "matrix_size", 12),
        }
        
        templates = templates_data.get("templates", [])
        templates.insert(0, template)
        
        max_t = templates_data.get("_meta", {}).get("max_templates", 21)
        templates = templates[:max_t]
        templates_data["templates"] = templates
        
        os.makedirs(os.path.dirname(template_path), exist_ok=True)
        with open(template_path, "w", encoding="utf-8") as f:
            json.dump(templates_data, f, indent=2, ensure_ascii=False)
        
    except Exception as e:
        print(f"Template-Speicherung fehlgeschlagen: {e}", flush=True)

def get_config_summary(args, result):
    """Erstellt eine kompakte Konfigurations-Zusammenfassung fuer Berichte."""
    msize = getattr(args, "matrix_size", 12)
    config = {
        "Matrix-Groesse": f"{msize}x{msize} ({msize*msize} Zellen)",
        "Berechnungs-Modus": "Precision (Deterministisch)" if getattr(args, "mode", "quantum") == "precision" else "Quantum (Stochastisch)",
        "Fokus-Gewichtung": getattr(args, "weight", "Sanft"),
        "Farbpalette": getattr(args, "palette", "Client Coherent (Auto)"),
        "HRV-Simulation": "Aktiv" if getattr(args, "hrv_sim", False) else "Inaktiv",
        "Quantum-Modul": "Aktiv" if getattr(args, "quantum_active", False) else "Inaktiv",
        "Planetarisch": "Aktiv" if getattr(args, "use_planetary", False) else "Inaktiv",
        "EMF-Kompensation": "Aktiv" if getattr(args, "emf_compensate", False) else "Inaktiv",
    }
    
    amp = result.get("amplifier")
    if amp and amp.get("active"):
        config["Verstaerker"] = f"{amp['name']} ({amp.get('element', '')}, Faktor {amp.get('amplification_factor', 0.5)})"
    else:
        config["Verstaerker"] = getattr(args, "amplifier", "") or "Keiner"
    
    sym = result.get("symmetry", "none")
    sym_labels = {"none": "Original", "horizontal": "Spiegel (Links-Rechts)", "quadrant": "Mandala (4-Quadranten)"}
    config["Symmetrie"] = sym_labels.get(sym, sym)
    
    return config

def _default_archive_root(base_dir=None):
    root = Path(base_dir) if base_dir else Path(os.getcwd()) / "data" / "runtime"
    root.mkdir(parents=True, exist_ok=True)
    return root

def _infer_artifact_type(path_str):
    artifact_path = Path(path_str)
    upper_name = artifact_path.name.upper()
    suffix = artifact_path.suffix.lower()
    if suffix == ".pdf" and "KOMPLETT" in upper_name:
        return "combined_pdf"
    if suffix == ".pdf":
        return "pdf"
    if suffix == ".xlsx":
        return "xlsx"
    if suffix == ".txt":
        return "log"
    if suffix == ".wav":
        return "audio"
    return suffix.lstrip(".") or "artifact"

def mirror_session_archive(args, client_data, full_name, focus_list, all_results, out_dir, exported_paths, harmonization_status="not_requested", archive_root=None):
    archive_dir = _default_archive_root(archive_root)
    client_service = ClientRegistryService(archive_dir / "clients.json")
    session_service = SessionArchiveService(archive_dir / "sessions.json")
    report_service = ReportManifestService(archive_dir / "artifacts.json")

    birth_date = client_data.get("birth_date") or ""
    if not birth_date:
        raw_dob = str(getattr(args, "dob", "") or "").strip()
        try:
            if "-" in raw_dob:
                birth_date = raw_dob
            elif len(raw_dob) == 6:
                birth_date = datetime.strptime(raw_dob, "%d%m%y").strftime("%Y-%m-%d")
            elif len(raw_dob) == 8:
                birth_date = datetime.strptime(raw_dob, "%d%m%Y").strftime("%Y-%m-%d")
        except ValueError:
            birth_date = ""

    client_entry = client_service.get_or_create(
        {
            "first_name": client_data.get("first_name") or getattr(args, "firstname", "") or full_name,
            "last_names": client_data.get("last_names") or ([getattr(args, "surname", "")] if getattr(args, "surname", "") else []),
            "birth_date": birth_date,
            "birth_place": client_data.get("birth_place") or getattr(args, "place", "Unknown"),
            "planet": client_data.get("planet") or getattr(args, "planet", "") or None,
        }
    )

    primary_result = all_results[0] if all_results else {}
    session_entry = session_service.create_session(
        client_ref={"client_id": client_entry.client_id, "client_name": full_name},
        focus=focus_list[0] if focus_list else "",
        focus_sequence=focus_list,
        config={
            "mode": getattr(args, "mode", "quantum"),
            "matrix_size": getattr(args, "matrix_size", 12),
            "weight": getattr(args, "weight", "Sanft"),
            "palette": getattr(args, "palette", "Client Coherent (Auto)"),
            "hrv_sim": getattr(args, "hrv_sim", False),
            "quantum_active": getattr(args, "quantum_active", False),
            "use_planetary": getattr(args, "use_planetary", False),
            "emf_compensate": getattr(args, "emf_compensate", False),
            "amplifier": getattr(args, "amplifier", ""),
            "symmetry": getattr(args, "symmetry", "none"),
            "harmonize": getattr(args, "harmonize", False),
            "template_name": getattr(args, "template_name", ""),
            "output_dir": str(out_dir),
        },
        result_summary={
            "result_count": len(all_results),
            "resonance_score": primary_result.get("resonance_score"),
            "hardware": primary_result.get("hardware"),
            "rates_string": primary_result.get("rates_string"),
        },
        harmonization_status=harmonization_status,
    )

    artifact_ids = []
    for path_str in exported_paths:
        if not path_str:
            continue
        artifact = report_service.register_artifact(
            session_id=session_entry.session_id,
            artifact_type=_infer_artifact_type(path_str),
            path=str(path_str),
            label=Path(path_str).name,
        )
        session_service.attach_artifact(session_entry.session_id, artifact.artifact_id)
        artifact_ids.append(artifact.artifact_id)

    return {
        "client_id": client_entry.client_id,
        "session_id": session_entry.session_id,
        "artifact_ids": artifact_ids,
        "archive_root": str(archive_dir),
    }

def export_to_excel(data, filepath, palette_map, palette_name, config_summary=None):
    if not HAS_EXPORT_LIBS:
        return
        
    wb = openpyxl.Workbook()
    
    # --- Sheet 1: Main Matrix ---
    ws = wb.active
    ws.title = "Haupt-Resonanz"
    
    # Header
    msize = data.get('matrix_size', 12)
    ws['A1'] = f"{msize}x{msize} RESONANCE MATRIX REPORT"
    ws['A1'].font = Font(bold=True, size=14)
    
    ws['A3'] = "Klient:"
    ws['B3'] = data['client_name']
    ws['A4'] = "Geboren:"
    ws['B4'] = f"{data.get('birth_date', '')} in {data.get('birth_place', 'Unknown')}"
    if data.get('planet'):
        ws['B4'] = f"{ws['B4'].value} (Planet: {data['planet']})"
    ws['A5'] = "Fokus:"
    ws['B5'] = f"{data['focus']} ({data.get('focus_weight', 'Normal')})"
    ws['A6'] = "Score:"
    ws['B6'] = f"{data['resonance_score']:.4f}"
    if "intensity" in data:
        ws['A6'] = f"Score / Int:"
        ws['B6'] = f"{data['resonance_score']:.4f} / {data['intensity']:.4f}"
        
    ws['A7'] = "Hardware:"
    ws['B7'] = data['hardware']
    ws['A8'] = "Palette:"
    ws['B8'] = palette_name
    
    # Konfigurationsdaten
    config_row = 10
    if config_summary:
        ws.cell(row=config_row, column=1, value="KONFIGURATION:").font = Font(bold=True, size=10)
        config_row += 1
        for key, val in config_summary.items():
            ws.cell(row=config_row, column=1, value=key)
            ws.cell(row=config_row, column=2, value=str(val))
            config_row += 1
        config_row += 1
    
    # Matrix
    start_row = config_row + 1
    matrix = data.get('matrix_data', data.get('matrix_12x12'))
    
    # Palette laden (wird nun übergeben)
    color_map = palette_map
    
    # Spaltenbreite und Zeilenhöhe adaptiv für Matrix-Größe
    col_w = 5.5 if msize <= 12 else 3.5 if msize <= 24 else 2.5
    row_h = 22 if msize <= 12 else 14 if msize <= 24 else 10
    font_sz = 11 if msize <= 12 else 8 if msize <= 24 else 6
    
    for j in range(msize):
        col_letter = chr(ord('A') + j) if j < 26 else chr(ord('A') + j // 26 - 1) + chr(ord('A') + j % 26)
        ws.column_dimensions[col_letter].width = col_w
    
    for i, row in enumerate(matrix):
        ws.row_dimensions[start_row + i].height = row_h
        for j, val in enumerate(row):
            cell = ws.cell(row=start_row + i, column=1 + j)
            cell.value = val
            cell.alignment = Alignment(horizontal='center', vertical='center')
            
            hex_color = color_map.get(val, "#FFFFFF")
            fill_hex = hex_color.replace("#", "")
            cell.fill = PatternFill(start_color=fill_hex, end_color=fill_hex, fill_type="solid")
            
            # Textfarbe Kontrast
            text_hex = get_contrast_color(hex_color).replace("#", "")
            cell.font = Font(color=text_hex, size=font_sz)

    # --- Sheet 2: Top 3 ---
    if "top_10" in data:
        ws2 = wb.create_sheet("Top 3 Varianten")
        ws2.column_dimensions['A'].width = 10
        ws2.column_dimensions['B'].width = 15
        ws2.column_dimensions['C'].width = 15
        ws2.column_dimensions['D'].width = 50
        
        ws2.append(["Rang", "Score", "Intensit\u00e4t", "Matrix-String (Flattened)"])
        
        for idx, item in enumerate(data["top_10"][:3]):
            flat_str = "".join([str(val) for row in item['matrix_12x12'] for val in row])
            ws2.append([
                idx + 1, 
                f"{item['score']:.6f}", 
                f"{item['intensity']:.6f}", 
                flat_str
            ])
                
    wb.save(filepath)
    print(f"Excel Export gespeichert: {filepath}", flush=True)

def export_to_pdf(data, filepath, palette_map, palette_name, title_prefix="", config_summary=None):
    if not HAS_EXPORT_LIBS:
        return

    doc = SimpleDocTemplate(filepath, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()
    
    # Update default font to support Umlaute
    if FONT_NAME != 'Helvetica':
        styles['Normal'].fontName = FONT_NAME
        styles['Title'].fontName = FONT_NAME
        styles['Heading2'].fontName = FONT_NAME
    
    color_map = palette_map
    msize = data.get('matrix_size', 12)
    
    # Title
    title_text = f"{title_prefix}{msize}x{msize} Resonance Matrix Report" if title_prefix else f"{msize}x{msize} Resonance Matrix Report"
    elements.append(Paragraph(title_text, styles['Title']))
    elements.append(Spacer(1, 12))
    
    # Bio-Info Section
    if data.get('bio_info'):
        bio = data['bio_info']
        b_type = bio['type'].upper()
        b_data = bio['data']
        elements.append(Paragraph(f"<b>Bio-Resonanz Fokus: {b_data['name']}</b>", styles['Heading2']))
        elements.append(Paragraph(f"Element: {b_data.get('element', '-')} | Frequenz: {b_data.get('frequency_hz', '-')} Hz | Mantra: {b_data.get('mantra', '-')}", styles['Normal']))
        elements.append(Paragraph(f"Psychologisch: {b_data.get('psychological', '-')}", styles['Normal']))
        elements.append(Spacer(1, 12))
    
    # Info Block
    info_text = [
        f"<b>Klient:</b> {data['client_name']}",
        f"<b>Geboren:</b> {data.get('birth_date', '')} in {data.get('birth_place', 'Unknown')}",
    ]
    if data.get('planet'):
        info_text.append(f"<b>Planet:</b> {data['planet']}")
        
    info_text.extend([
        f"<b>Fokus:</b> {data['focus']} (<i>{data.get('focus_weight', 'Normal')}</i>)",
        f"<b>Datum:</b> {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"<b>Resonanz Score:</b> {data['resonance_score']:.4f}",
    ])
    
    if "intensity" in data:
        info_text.append(f"<b>Intensit\u00e4t:</b> {data['intensity']:.4f}")
        
    info_text.extend([
        f"<b>System:</b> {data['hardware']}",
        f"<b>Palette:</b> {palette_name}"
    ])
    
    for line in info_text:
        elements.append(Paragraph(line, styles['Normal']))
    elements.append(Spacer(1, 12))
    
    # Konfigurationsdaten-Sektion
    if config_summary:
        elements.append(Paragraph("<b>Konfiguration:</b>", styles['Heading2']))
        for key, val in config_summary.items():
            elements.append(Paragraph(f"<b>{key}:</b> {val}", styles['Normal']))
        elements.append(Spacer(1, 12))
    
    # Seitenumbruch vor Matrix bei groesseren Matrizen (damit sie komplett auf eine Seite passt)
    if msize > 12:
        from reportlab.platypus import PageBreak
        elements.append(PageBreak())
    
    # Matrix Data Preparation
    matrix_data = data.get('matrix_data', data.get('matrix_12x12'))
    # Convert ints to strings
    table_data = [[str(cell) for cell in row] for row in matrix_data]
    
    # Spaltenbreiten berechnen: Matrix muss auf A4-Seitenbreite passen
    # A4 nutzbar: ca. 480pt (595pt - 2x ~57pt Rand)
    page_usable_width = 480
    col_width = page_usable_width / msize
    row_height = col_width  # Quadratische Zellen
    
    t = Table(table_data, colWidths=[col_width] * msize, rowHeights=[row_height] * msize)
    
    # Font/Padding adaptiv
    if msize <= 12:
        font_sz, pad = 10, 4
    elif msize <= 24:
        font_sz, pad = 6, 1
    else:
        font_sz, pad = 5, 0
    
    # Base Style
    table_style_cmds = [
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5 if msize > 12 else 1, colors.black),
        ('FONTSIZE', (0,0), (-1,-1), font_sz),
        ('LEADING', (0,0), (-1,-1), font_sz + 2),
        ('TOPPADDING', (0,0), (-1,-1), pad),
        ('BOTTOMPADDING', (0,0), (-1,-1), pad),
        ('LEFTPADDING', (0,0), (-1,-1), pad),
        ('RIGHTPADDING', (0,0), (-1,-1), pad),
        ('FONTNAME', (0,0), (-1,-1), FONT_NAME), 
    ]
    
    # Color Highlighting & Contrast Text
    for r, row in enumerate(matrix_data):
        for c, val in enumerate(row):
            # Val is already int in matrix_data
            hex_color = color_map.get(val, "#FFFFFF")
            text_color = get_contrast_color(hex_color)
            
            table_style_cmds.append(('BACKGROUND', (c,r), (c,r), colors.HexColor(hex_color)))
            table_style_cmds.append(('TEXTCOLOR', (c,r), (c,r), colors.HexColor(text_color)))

    t.setStyle(TableStyle(table_style_cmds))

    elements.append(t)
    elements.append(Spacer(1, 20))
    
    # Top 3 Section (Only if not a sub-report)
    if "top_10" in data and not title_prefix:
        elements.append(Paragraph("<b>Top 3 Resonanz-Varianten</b>", styles['Heading2']))
        elements.append(Spacer(1, 10))
        
        top3_data = [["Rang", "Score", "Intensit\u00e4t", "Signatur (Auszug)"]]
        for idx, item in enumerate(data["top_10"][:3]):
            flat_str = "".join([str(val) for row in item['matrix_12x12'] for val in row])
            short_sig = flat_str[:20] + "..."
            top3_data.append([
                str(idx + 1),
                f"{item['score']:.4f}",
                f"{item['intensity']:.4f}",
                short_sig
            ])
            
        t3 = Table(top3_data, colWidths=[40, 80, 80, 200])
        t3.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('FONTNAME', (0,0), (-1,-1), FONT_NAME),
        ]))
        elements.append(t3)
        elements.append(Spacer(1, 20))

    # Footer
    elements.append(Paragraph(f"Rates String: {data['rates_string']}", styles['Normal']))
    
    doc.build(elements)
    print(f"PDF Export gespeichert: {filepath}", flush=True)

def export_combined_pdf(all_results, filepath, palette_maps, palette_name, config_summary=None):
    """Exportiert ALLE Fokus-Matrizen in ein einziges PDF. 2 Seiten pro Fokus."""
    if not HAS_EXPORT_LIBS:
        return
    
    from reportlab.platypus import PageBreak
    
    doc = SimpleDocTemplate(filepath, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()
    
    if FONT_NAME != 'Helvetica':
        styles['Normal'].fontName = FONT_NAME
        styles['Title'].fontName = FONT_NAME
        styles['Heading2'].fontName = FONT_NAME
    
    for focus_idx, data in enumerate(all_results):
        msize = data.get('matrix_size', 12)
        color_map = palette_maps.get(focus_idx, palette_maps.get(0, {}))
        
        # ===== SEITE 1: Konfiguration + Rates String =====
        # Fokus-Titel
        elements.append(Paragraph(
            f"Fokus {focus_idx+1}/{len(all_results)}: {data.get('focus', 'Unbekannt')}",
            styles['Title']
        ))
        elements.append(Spacer(1, 8))
        
        # Bio-Info
        if data.get('bio_info'):
            bio = data['bio_info']
            b_data = bio['data']
            elements.append(Paragraph(f"<b>Bio-Resonanz: {b_data['name']}</b>", styles['Heading2']))
            elements.append(Paragraph(
                f"Element: {b_data.get('element', '-')} | Frequenz: {b_data.get('frequency_hz', '-')} Hz | Mantra: {b_data.get('mantra', '-')}",
                styles['Normal']
            ))
            elements.append(Spacer(1, 6))
        
        # Info Block
        info_lines = [
            f"<b>Klient:</b> {data.get('client_name', '')}",
            f"<b>Fokus:</b> {data.get('focus', '')} (<i>{data.get('focus_weight', 'Normal')}</i>)",
            f"<b>Resonanz Score:</b> {data.get('resonance_score', 0):.4f}",
            f"<b>Intensitaet:</b> {data.get('intensity', 0):.4f}",
            f"<b>System:</b> {data.get('hardware', '')}",
            f"<b>Palette:</b> {palette_name}",
            f"<b>Datum:</b> {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        ]
        if data.get('planet'):
            info_lines.insert(1, f"<b>Planet:</b> {data['planet']}")
        
        for line in info_lines:
            elements.append(Paragraph(line, styles['Normal']))
        elements.append(Spacer(1, 8))
        
        # Konfiguration
        if config_summary:
            elements.append(Paragraph("<b>Konfiguration:</b>", styles['Heading2']))
            for key, val in config_summary.items():
                elements.append(Paragraph(f"<b>{key}:</b> {val}", styles['Normal']))
            elements.append(Spacer(1, 10))
        
        # Rates String (unterhalb der Konfiguration, oberhalb der Matrix)
        rates_str = data.get('rates_string', '')
        elements.append(Spacer(1, 10))
        elements.append(Paragraph(f"<b>{msize}x{msize} Rates String:</b>", styles['Heading2']))
        # Rates in Zeilen umbrechen fuer Lesbarkeit
        chunk_size = msize
        rates_lines = [rates_str[i:i+chunk_size] for i in range(0, len(rates_str), chunk_size)]
        for rl in rates_lines:
            elements.append(Paragraph(f"<font size='8' face='Courier'>{rl}</font>", styles['Normal']))
        
        # ===== SEITE 2: Matrix-Grafik =====
        elements.append(PageBreak())
        
        elements.append(Paragraph(
            f"{msize}x{msize} Matrix: {data.get('focus', '')}",
            styles['Title']
        ))
        elements.append(Spacer(1, 6))
        
        # Matrix-Tabelle
        matrix_data = data.get('matrix_data', data.get('matrix_12x12'))
        table_data = [[str(cell) for cell in row] for row in matrix_data]
        
        # Skalierung: Matrix soll moeglichst gross auf die Seite passen
        # A4 nutzbar: ca. 480pt breit, ca. 680pt hoch (nach Titel-Bereich)
        page_usable_width = 480
        page_usable_height = 650
        col_width = min(page_usable_width / msize, page_usable_height / msize)
        row_height = col_width  # Quadratische Zellen
        
        t = Table(table_data, colWidths=[col_width] * msize, rowHeights=[row_height] * msize)
        
        # Font/Padding adaptiv
        if msize <= 12:
            font_sz, pad = 10, 4
        elif msize <= 24:
            font_sz, pad = 6, 1
        else:
            font_sz, pad = 5, 0
        
        table_style_cmds = [
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('GRID', (0,0), (-1,-1), 0.5 if msize > 12 else 1, colors.black),
            ('FONTSIZE', (0,0), (-1,-1), font_sz),
            ('LEADING', (0,0), (-1,-1), font_sz + 2),
            ('TOPPADDING', (0,0), (-1,-1), pad),
            ('BOTTOMPADDING', (0,0), (-1,-1), pad),
            ('LEFTPADDING', (0,0), (-1,-1), pad),
            ('RIGHTPADDING', (0,0), (-1,-1), pad),
            ('FONTNAME', (0,0), (-1,-1), FONT_NAME),
        ]
        
        # Farben pro Zelle
        for r, row in enumerate(matrix_data):
            for c, val in enumerate(row):
                hex_color = color_map.get(int(val), "#FFFFFF")
                text_color = get_contrast_color(hex_color)
                table_style_cmds.append(('BACKGROUND', (c,r), (c,r), colors.HexColor(hex_color)))
                table_style_cmds.append(('TEXTCOLOR', (c,r), (c,r), colors.HexColor(text_color)))
        
        t.setStyle(TableStyle(table_style_cmds))
        elements.append(t)
        
        # Seitenumbruch nach jeder Matrix (ausser letzte)
        if focus_idx < len(all_results) - 1:
            elements.append(PageBreak())
    
    try:
        doc.build(elements)
        print(f"Kombiniertes PDF ({len(all_results)} Fokusse, {len(all_results)*2} Seiten) gespeichert: {filepath}", flush=True)
    except Exception as e:
        print(f"Kombiniertes PDF Fehler: {e}", flush=True)

def mock_resonance_calculation(client_data, focus, size=12):
    """Fallback Berechnung - Nur nutzen wenn PyTorch fehlt"""
    print("Info: Nutze AMD Ryzen 9 8945HS Optimierung (Simulation)...", flush=True)
    time.sleep(0.5)
    
    seed_str = f"{client_data.get('first_name')}{focus}{client_data.get('birth_date')}"
    random.seed(seed_str)
    
    # Helper to gen matrix
    def gen_matrix():
        return [[random.randint(0, 9) for _ in range(size)] for _ in range(size)]
    
    matrix = gen_matrix()
    score = 0.92 + (random.random() * 0.07)
    intensity = 2.5 + (random.random() * 1.5)
    sim_freq = 150.0 + (random.random() * 300.0)
    
    # Generate Mock Top 10
    top_10 = []
    for i in range(10):
        # Slightly lower score for each
        sub_score = score - (i * 0.005) - (random.random() * 0.002)
        sub_intensity = 2.0 + (random.random() * 2.0)
        top_10.append({
            "score": sub_score,
            "intensity": sub_intensity,
            "matrix_12x12": gen_matrix()
        })
    
    return {
        "matrix_12x12": matrix,
        "resonance_score": score,
        "intensity": intensity,
        "top_10": top_10,
        "hardware": "AMD Ryzen 9 8945HS w/ Radeon 780M Graphics (Sim)",
        "client_name": f"{client_data.get('first_name')} {client_data.get('last_names', [''])[0]}",
        "client_signature": {
            "frequency": sim_freq,
            "components": {}
        }
    }

def _run_bus_command(args):
    """R-10..R-14: Interchange-Bus Consumer CLI (Radi144). Konservativ, opt-in,
    default-off. KEIN publish (Radi144 ist Consumer im MVP), KEIN Netzwerk.
    Gibt 0 zurueck, druckt strukturierte JSON-Ausgabe auf stdout."""
    from app.services.bus_consumer_service import consume_bus_messages
    from app.interchange_bus import BusConsumerStore, topic_values

    bus_db = getattr(args, "bus_db", "") or ""
    if not bus_db:
        print("Fehler: --bus-db (absoluter Pfad zur BusDB) erforderlich fuer Bus-Befehle.", flush=True)
        return 1
    if not os.path.isabs(bus_db):
        print(f"Fehler: --bus-db muss ein absoluter Pfad sein (got {bus_db!r}).", flush=True)
        return 1

    topic = getattr(args, "bus_topic", "scan_result")
    if topic not in topic_values():
        print(f"Fehler: --bus-topic {topic!r} ungueltig. Erlaubt: {', '.join(topic_values())}", flush=True)
        return 1

    store = BusConsumerStore(bus_db)

    if getattr(args, "bus_status", False):
        print(json.dumps(store.status(), indent=2, ensure_ascii=False), flush=True)
        return 0

    if getattr(args, "bus_register", False):
        result = store.register_module(
            module_id=getattr(args, "bus_subscriber", "radi144"),
            module_kind="consumer",
            capabilities={"topics": list(topic_values()), "publish": False},
        )
        print(json.dumps({"registered": result}, indent=2, ensure_ascii=False), flush=True)
        return 0

    if getattr(args, "bus_ack", ""):
        try:
            result = store.ack(getattr(args, "bus_subscriber", "radi144"), args.bus_ack)
        except ValueError as e:
            print(json.dumps({"error": str(e)}, indent=2, ensure_ascii=False), flush=True)
            return 2
        print(json.dumps({"acked": result}, indent=2, ensure_ascii=False), flush=True)
        return 0

    if getattr(args, "bus_consume", False):
        result = consume_bus_messages(
            getattr(args, "bus_subscriber", "radi144"),
            topic,
            bus_db,
            limit=getattr(args, "bus_limit", 100),
            auto_ack=getattr(args, "bus_auto_ack", False),
        )
        print(json.dumps(result, indent=2, ensure_ascii=False), flush=True)
        return 0

    print("Kein Bus-Befehl erkannt (--bus-consume/--bus-register/--bus-status/--bus-ack).", flush=True)
    return 1


def main():
    print("Starte Resonance Matrix Engine...", flush=True)
    
    # Initialize variables to avoid UnboundLocalError
    client_data = {}
    
    parser = argparse.ArgumentParser()
    # Old args for compat (optional)
    parser.add_argument("--name", help="Full name (deprecated)")
    
    # New args
    parser.add_argument("--surname", default="")
    parser.add_argument("--firstname", default="")
    parser.add_argument("--dob", default="01011990", help="DDMMYYYY or DDMMYY")
    parser.add_argument("--place", default="Unknown", help="Birthplace")
    parser.add_argument("--planet", default="", help="Birth Planet (optional)")
    parser.add_argument("--focus", default="Heilung")
    parser.add_argument("--focus-file", default="", help="Pfad zu einer UTF-8 Datei mit Fokus-Themen (robuste Alternative zu --focus)")
    parser.add_argument("--weight", default="Sanft", help="Deaktiviert, Sanft, Normal, Stark")
    parser.add_argument("--palette", default="Client Coherent (Auto)", help="Farbpalette aus palettes.json")
    parser.add_argument("--preset", choices=list(PRESETS.keys()), help="Preset-ID aus preset_profiles.json")
    parser.add_argument("--mode", default="quantum", choices=["quantum", "precision"], help="Berechnungs-Modus: quantum (stochastisch) oder precision (deterministisch)")
    parser.add_argument("--hrv-sim", action="store_true", help="Simuliert HRV-basiertes Bio-Feedback fuer die Analyse")
    parser.add_argument("--quantum-active", action="store_true", help="Aktiviert das Quantum-Modul (Software-Toggle)")
    parser.add_argument("--use-planetary", action="store_true", help="Aktiviert den optionalen planetarischen Einfluss in der Signatur")
    parser.add_argument("--emf-compensate", action="store_true", help="Aktiviert EMF-Umfeld-Kompensation (Stoerfrequenz-Filterung)")
    parser.add_argument("--amplifier", default="", help="Resonanz-Verstaerker (z.B. 'Rosenquarz', 'Orgonit-Pyramide (Schungit-Kern)')")
    parser.add_argument("--symmetry", default="none", choices=["none", "horizontal", "quadrant"], help="Symmetrie-Modus: none (Original), horizontal (Spiegel), quadrant (Mandala)")
    parser.add_argument("--matrix-size", type=int, default=12, choices=[12, 24, 36], help="Matrix-Groesse: 12 (Standard), 24 (Erweitert), 36 (Server/RTX)")
    parser.add_argument("--template-name", default="", help="Benutzerdefinierter Name fuer das Session-Template")
    
    # Gruppen-, Geo-, Bild- und DB-Erweiterungen
    parser.add_argument("--group", help="Pfad zu einer JSON-Datei mit Gruppenmitgliedern")
    parser.add_argument("--coords", help="Google Maps Koordinaten (Format: 'Lat,Lon')")
    parser.add_argument("--image-path", default="", help="Pfad zu einem Bild fuer Bild-Resonanz Analyse")
    parser.add_argument("--db-path", help="Pfad zu einer .txt Datenbank fuer Vorab-Vektorisierung")
    
    parser.add_argument("--db-scan", action="store_true", help="Scant eine Datenbank (.txt) gegen die Signatur und gibt die Top-N Resonanzen zurueck")
    parser.add_argument("--db-top-n", type=int, default=21, help="Anzahl der Top-Resonanzen beim DB-Scan (1, 5, 9 oder 21)")
    parser.add_argument("--db-rank-file", default="", help="Pfad zu einer Datei mit DB-Pfaden (ein Pfad pro Zeile) fuer Top-5 DB-Ranking")
    
    # Harmonization Args
    parser.add_argument("--harmonize", action="store_true", help="Start Harmonization Mode after analysis")
    parser.add_argument("--pulse", type=float, default=21.0, help="Pulse duration in seconds")
    parser.add_argument("--pause", type=float, default=14.0, help="Pause duration in seconds")
    parser.add_argument("--duration", type=float, default=1.0, help="Duration factor (multiples of 21 min)")
    parser.add_argument("--audio", action="store_true", help="Enable Harmonical Frequency Audio")
    parser.add_argument("--solfeggio", choices=["528", "429.62", "432"], default="528", help="Solfeggio/Base frequency modulation")

    # Interchange-Bus Consumer (R-10..R-14) — konservative Vorbereitung, keine
    # fixe Verdrahtung. Opt-in; default-off. Finale Verdrahtung auf Debian-Server.
    parser.add_argument("--bus-db", default="", help="Pfad zur geteilten BusDB (SQLite) — absolut. Aktiviert Bus-Consumer-Modus wenn mit --bus-consume/--bus-status/--bus-register gesetzt.")
    parser.add_argument("--bus-topic", default="scan_result", help="Bus-Topic (scan_result|post_scan_report|trend_snapshot|catalog_snapshot)")
    parser.add_argument("--bus-subscriber", default="radi144", help="Subscriber-Modul-ID fuer Bus-Cursor/ACK")
    parser.add_argument("--bus-limit", type=int, default=100, help="Max. Nachrichten pro Poll")
    parser.add_argument("--bus-consume", action="store_true", help="Konsumiere Bus-Nachrichten zu --bus-topic (verify+safety-check, at-least-once)")
    parser.add_argument("--bus-auto-ack", action="store_true", help="Auto-ACK der letzten verifizierten Nachricht (Cursor vorruecken)")
    parser.add_argument("--bus-register", action="store_true", help="Registriere --bus-subscriber in der Bus-Modul-Registry")
    parser.add_argument("--bus-ack", default="", help="ACK eine bestimmte message_id (Cursor dorthin setzen)")
    parser.add_argument("--bus-status", action="store_true", help="Bus-Store-Status (Counts, Schema, DB-Pfad)")

    if HAS_ARGCOMPLETE:
        argcomplete.autocomplete(parser)
    args = parser.parse_args()

    # --- Interchange-Bus Consumer Dispatch (vor Hauptflow, kein Analysis-Setup noetig) ---
    if any(getattr(args, k, False) for k in ("bus_consume", "bus_register", "bus_status", "bus_ack")):
        return _run_bus_command(args)

    # Focus aus Datei laden (robuste Uebergabe fuer lange/komplexe Fokus-Strings)
    if getattr(args, 'focus_file', '') and os.path.exists(args.focus_file):
        try:
            with open(args.focus_file, 'r', encoding='utf-8') as ff:
                file_focus = ff.read().strip()
            if file_focus:
                args.focus = file_focus
                print(f"Fokus aus Datei geladen ({len(file_focus)} Zeichen)", flush=True)
        except Exception as e:
            print(f"Warnung: Fokus-Datei konnte nicht gelesen werden: {e}", flush=True)
    
    # Preset Overrides
    if getattr(args, "preset", None):
        preset_cfg = PRESETS.get(args.preset, {})
        args.focus = preset_cfg.get("focus", args.focus)
        args.weight = preset_cfg.get("weight", args.weight)
        args.palette = preset_cfg.get("palette", args.palette)

    # Date conversion DDMMYYYY -> YYYY-MM-DD
    try:
        # Check if already YYYY-MM-DD (legacy support)
        if "-" in args.dob:
             dob_iso = args.dob
        elif len(args.dob) == 6:
             # DDMMYY
             dt = datetime.strptime(args.dob, "%d%m%y")
             # Century fix: If year is in future, assume previous century (e.g. 60 -> 1960)
             if dt.year > datetime.now().year:
                 dt = dt.replace(year=dt.year - 100)
             dob_iso = dt.strftime("%Y-%m-%d")
        else:
             # DDMMYYYY
             dob_iso = datetime.strptime(args.dob, "%d%m%Y").strftime("%Y-%m-%d")
    except ValueError:
        print(f"Warnung: Ung\u00fcltiges Datumsformat '{args.dob}'. Nutze 1990-01-01.", flush=True)
        dob_iso = "1990-01-01"

    # Construct client_data
    if args.name:
         # Fallback if old arg used
         parts = args.name.split(" ")
         fname = parts[0]
         lname = parts[1:] if len(parts) > 1 else ["Unknown"]
    else:
         fname = args.firstname if args.firstname else "Analyse"
         lname = [args.surname] if args.surname else [""]

    client_data = {
        "first_name": fname,
        "last_names": lname,
        "birth_date": dob_iso,
        "birth_place": args.place,
        "planet": args.planet
    }

    # --- Signatur-Generierung (Adaptiv) ---
    from app.algorithms.client_signature import ClientSignatureGenerator
    from app.algorithms.resonance_engine import ResonanceMatrixEngine
    sig_gen = ClientSignatureGenerator()
    
    if args.image_path and os.path.exists(args.image_path):
        # --- Bild-Resonanz Flow ---
        client_sig = sig_gen.generate_image_signature(args.image_path)
        image_label = client_sig.get("image_label", os.path.splitext(os.path.basename(args.image_path))[0])
        full_name = image_label
        fname = image_label
        lname = [""]
        print(f"Bild-Resonanz aktiv: {image_label} ({client_sig['frequency']:.2f} Hz)", flush=True)
    elif args.group and os.path.exists(args.group):
        try:
            with open(args.group, 'r', encoding='utf-8-sig') as f:
                members = json.load(f)
            client_sig = sig_gen.generate_group_signature(members)
            full_name = f"Gruppe ({len(members)} Personen)"
            print(f"Gruppen-Analyse aktiv: {full_name}", flush=True)
        except Exception as e:
            print(f"Fehler beim Laden der Gruppe: {e}", flush=True)
            sys.exit(1)
    else:
        client_sig = sig_gen.generate_signature(client_data, use_planetary=args.use_planetary)

    # Geo-Integration
    if args.coords:
        try:
            coords_parts = args.coords.split(',')
            lat = float(coords_parts[0])
            lon = float(coords_parts[1])
            radius = float(coords_parts[2]) if len(coords_parts) > 2 else 0.0
            
            geo_freq = sig_gen.calculate_geo_frequency(lat, lon, radius_m=radius)
            client_sig["frequency"] = (client_sig["frequency"] + geo_freq) / 2.0
            radius_str = f" (Radius: {radius}m)" if radius > 0 else ""
            print(f"Geo-Resonanz integriert: {lat:.4f},{lon:.4f}{radius_str} ({geo_freq:.2f} Hz)", flush=True)
        except Exception as e:
            print(f"Warnung: Ungueltige Koordinaten oder Radius '{args.coords}': {e}", flush=True)

    # DB-Vektorisierung
    if args.db_path:
        db_freq = sig_gen.vectorise_database_selection(args.db_path, args.focus)
        if db_freq > 0:
            client_sig["frequency"] = (client_sig["frequency"] + db_freq) / 2.0
            print(f"Datenbank-Resonanz integriert aus {os.path.basename(args.db_path)} ({db_freq:.2f} Hz)", flush=True)

    # Engine initialisieren
    from app.algorithms.resonance_engine import ResonanceMatrixEngine
    engine = ResonanceMatrixEngine(use_cuda=True, quantum_active=args.quantum_active)
    
    # --- Datenbank-Ranking Modus (Hybrid: Dateinamen-Vorfilter + Inhalts-Scan) ---
    if args.db_rank_file and os.path.exists(args.db_rank_file):
        # Lese DB-Pfade aus Datei (ein Pfad pro Zeile)
        db_paths = []
        for enc in ['utf-8-sig', 'utf-8', 'latin-1']:
            try:
                with open(args.db_rank_file, 'r', encoding=enc) as f:
                    db_paths = [line.strip() for line in f if line.strip()]
                break
            except UnicodeDecodeError:
                continue
        db_paths = [p for p in db_paths if os.path.exists(p)]
        print(f"DB-Ranking Hybrid: {len(db_paths)} Datenbanken gefunden", flush=True)
        
        # === PHASE 1: Dateinamen-Resonanz (schnell, alle DBs) ===
        print(f"  Phase 1: Dateinamen-Vorfilter...", flush=True)
        name_scores = []
        for db_p in db_paths:
            db_name = os.path.splitext(os.path.basename(db_p))[0]
            # Dateiname als Fokus gegen Klienten-Vektor berechnen
            try:
                res = engine.calculate_resonance(
                    client_data, db_name, matrix_size=12,
                    focus_weight=args.weight,
                    precomputed_signature=client_sig,
                    calculation_mode="precision",
                    emf_compensate=args.emf_compensate
                )
                name_scores.append({"path": db_p, "name": db_name, "score": res["resonance_score"]})
            except Exception:
                name_scores.append({"path": db_p, "name": db_name, "score": 0.0})
        
        # Top-30 nach Dateinamen-Relevanz
        name_scores.sort(key=lambda x: x["score"], reverse=True)
        top30_candidates = name_scores[:30]
        print(f"  Phase 1 abgeschlossen: Top-30 von {len(name_scores)} vorausgewaehlt", flush=True)
        
        # === PHASE 2: Inhalts-Scan (nur Top-30 Kandidaten) ===
        print(f"  Phase 2: Inhalts-Scan der Top-30...", flush=True)
        db_scores = []
        for ci, cand in enumerate(top30_candidates):
            db_p = cand["path"]
            try:
                entries = []
                for enc in ['utf-8', 'latin-1', 'cp1252']:
                    try:
                        with open(db_p, 'r', encoding=enc) as f:
                            entries = [line.strip() for line in f if line.strip()]
                        break
                    except UnicodeDecodeError:
                        continue
                if not entries:
                    continue
                
                # Berechne Resonanz fuer bis zu 50 Eintraege pro DB
                entry_scores = []
                for entry in entries[:50]:
                    res = engine.calculate_resonance(
                        client_data, entry, matrix_size=12,
                        focus_weight=args.weight,
                        precomputed_signature=client_sig,
                        calculation_mode="precision",
                        emf_compensate=args.emf_compensate
                    )
                    entry_scores.append(res["resonance_score"])
                
                entry_scores.sort(reverse=True)
                avg_top5 = sum(entry_scores[:5]) / min(5, len(entry_scores))
                db_scores.append({
                    "path": db_p,
                    "name": os.path.basename(db_p),
                    "avg_score": avg_top5,
                    "name_score": cand["score"],
                    "entries": len(entries)
                })
                if (ci + 1) % 10 == 0:
                    print(f"    {ci+1}/30 gescannt...", flush=True)
            except Exception as e:
                print(f"  Warnung: {os.path.basename(db_p)}: {e}", flush=True)
        
        # Sortiere nach Inhalts-Score und gib Top-5 aus
        db_scores.sort(key=lambda x: x["avg_score"], reverse=True)
        top5_dbs = db_scores[:5]
        
        print(f"\nDB-RANKING ({len(db_paths)} geprueft, {len(db_scores)} tiefenanalysiert):", flush=True)
        rank_lines = []
        for i, db in enumerate(top5_dbs):
            line = f"{db['avg_score']:.4f} | {db['name']} ({db['entries']} Eintraege)"
            print(f" [{i+1}] {line}", flush=True)
            rank_lines.append(line)
        
        print(f"###DBRANK###{chr(10).join(rank_lines)}###ENDDBRANK###", flush=True)
        sys.exit(0)
    
    # --- Datenbank-Scan Modus (Top-N) ---
    if args.db_scan and args.db_path:
        print(f"Starte Datenbank-Scan: {os.path.basename(args.db_path)}...", flush=True)
        print(f"Engine gestartet (CUDA aktiv, Quantum: {'EIN' if args.quantum_active else 'AUS'})", flush=True)
        if not os.path.exists(args.db_path):
            print(f"Fehler: Datenbank {args.db_path} nicht gefunden.", flush=True)
            sys.exit(1)
            
        entries = []
        # Robustes Encoding-Handling fuer Datenbank-Dateien
        for enc in ['utf-8', 'latin-1', 'cp1252']:
            try:
                with open(args.db_path, 'r', encoding=enc) as f:
                    entries = [line.strip() for line in f if line.strip()]
                break
            except UnicodeDecodeError:
                continue
            
        if not entries:
            print("Fehler: Datenbank konnte nicht gelesen werden oder ist leer.", flush=True)
            sys.exit(1)
            
        print(f"Analysiere {len(entries)} Eintraege gegen Vektor...", flush=True)
        
        # Berechne Resonanz fuer jeden Eintrag
        scan_results = []
        for entry in entries:
            res = engine.calculate_resonance(
                client_data,
                entry,
                matrix_size=12,
                focus_weight=args.weight,
                precomputed_signature=client_sig,
                calculation_mode="precision", # Nutze Precision fuer stabilen Scan
                emf_compensate=args.emf_compensate
            )
            scan_results.append({
                "entry": entry,
                "score": res["resonance_score"]
            })
            
        # Sortiere nach Score (absteigend) und nimm Top-N
        top_n_count = min(args.db_top_n, len(scan_results))
        top_results = sorted(scan_results, key=lambda x: x["score"], reverse=True)[:top_n_count]
        
        print(f"\nTOP-{top_n_count} RESONANZEN GEFUNDEN:", flush=True)
        focus_output = []
        for i, item in enumerate(top_results):
            print(f" [{i+1:2}] {item['score']:.4f} | {item['entry']}", flush=True)
            focus_output.append(item['entry'])
            
        # Gib die Liste als Semicolon-separierten String aus, damit PS sie lesen kann
        print(f"###TOP21###{';'.join(focus_output)}###ENDTOP21###", flush=True)
        sys.exit(0)

    # --- Standard Analyse Flow ---
    print(f"High-Performance Engine gestartet (CUDA aktiv, Quantum: {'EIN' if args.quantum_active else 'AUS'})", flush=True)

    full_name = f"{fname} {' '.join(lname)}".strip()
    print(f"\nAnalyse fuer: {full_name}", flush=True)
    print(f"Geboren:     {dob_iso} in {args.place}", flush=True)
    if args.planet:
        print(f"Planet:      {args.planet}", flush=True)
    print(f"Fokus:       {args.focus} (Gewichtung: {args.weight})", flush=True)
    print(f"Palette:     {args.palette}", flush=True)
    # Organ-Uhr Check
    now = datetime.now()
    hour = now.hour
    active_meridian = "Unbekannt"
    try:
        knowledge_path = os.path.join(os.getcwd(), 'bio_knowledge.json')
        if os.path.exists(knowledge_path):
            with open(knowledge_path, 'r', encoding='utf-8') as f:
                bio_k = json.load(f)
                for m_id, m_data in bio_k.get('meridians', {}).items():
                    start_h = int(m_data['peak_time'].split(':')[0])
                    end_h = int(m_data['peak_time'].split('-')[1].split(':')[0])
                    # Handle midnight wrap
                    if start_h > end_h:
                        if hour >= start_h or hour < end_h:
                            active_meridian = m_data['name']
                            break
                    elif start_h <= hour < end_h:
                        active_meridian = m_data['name']
                        break
    except: pass
    print(f"Zeitpunkt:   {now.strftime('%H:%M')} (Aktiver Meridian: {active_meridian})", flush=True)
    print("----------------------------------------", flush=True)

    # Palette holen
    engine_palette_arg = None
    if args.palette == "Focus+EMF Coherent":
        # NEU: Fokus+EMF+Bio kohaerente Palette - wird zur Engine durchgereicht
        engine_palette_arg = "focus_emf_coherent"
        print("Palette: Focus+EMF Coherent (wird dynamisch aus Fokus + EMF berechnet)", flush=True)
    elif args.palette == "Client Coherent (Auto)":
        # Client + Fokus kohaerente Palette (pro Fokus dynamisch)
        engine_palette_arg = "client_focus_coherent"
        print(f"Palette: Client+Fokus Coherent (dynamisch pro Fokus-Thema)", flush=True)
    elif args.palette == "Focus Coherent":
        # Rein fokus-basierte Palette (ohne Client-Frequenz)
        engine_palette_arg = "focus_only_coherent"
        print("Palette: Fokus Coherent (rein fokus-basierte Farben)", flush=True)
    elif args.palette == "Natur Heilsam":
        # Natur-heilsame Palette: Fokus → Natur-Familie (Wald/Erde/Himmel/Moos/Nebel/Morgenrot)
        engine_palette_arg = "nature_healing"
        print("Palette: Natur Heilsam (Wald/Erde/Himmel/Moos/Nebel/Morgenrot)", flush=True)
    elif args.palette == "Unified Coherent":
        # Optimale 5-Schicht-Palette: Client + ALLE Fokusse + Bio + EMF
        # Wird EINMAL berechnet und fuer alle Fokus-Berechnungen verwendet
        engine_palette_arg = "unified_coherent_pending"
        print("Palette: Unified Coherent (5-Schicht: Client+Alle Fokusse+Bio+EMF)", flush=True)
    else:
        engine_palette_arg = get_palette(args.palette)

    # --- Amplifier Aktivierung ---
    if args.amplifier:
        amp_result = engine.set_amplifier(args.amplifier)
        if amp_result:
            print(f"Verstaerker: {amp_result['name']} ({amp_result.get('element', '')} / {amp_result.get('chakra', '')})", flush=True)
            print(f"  Basis:     {amp_result['base_frequency_hz']} Hz | Faktor: {amp_result.get('amplification_factor', 0.5)}", flush=True)
        else:
            print(f"Verstaerker '{args.amplifier}' nicht gefunden. Verfuegbare:", flush=True)
            for a in engine.list_amplifiers():
                print(f"  - {a['name']} ({a['category']}, {a['element']})", flush=True)

    # Focus Sequence Parsing
    focus_list = [f.strip() for f in args.focus.split(';') if f.strip()]
    all_results = []
    
    if len(focus_list) > 1:
        print(f"Erkannte Sequenz mit {len(focus_list)} Fokus-Energien.", flush=True)

    # Unified Coherent: Berechne Palette EINMAL mit ALLEN Fokussen VOR dem Loop
    if engine_palette_arg == "unified_coherent_pending":
        try:
            engine_palette_arg = engine.generate_unified_coherent_palette(
                client_data=client_data,
                focus_list=focus_list,
                use_planetary=args.use_planetary
            )
            print(f"Unified Palette berechnet ({len(focus_list)} Fokusse, 10 Farben)", flush=True)
        except Exception as e:
            print(f"Warnung: Unified Palette Fehler ({e}), nutze Fallback", flush=True)
            engine_palette_arg = get_palette("Radionik (Standard)")

    all_palette_maps = {}
    
    for idx, current_focus in enumerate(focus_list):
        if len(focus_list) > 1:
            print(f"\n--- Berechnung {idx+1}/{len(focus_list)}: '{current_focus}' ---", flush=True)
            
        if idx == 0:
            print("Berechne Matrix (CUDA Optimized)...", flush=True)
        try:
            result = engine.calculate_resonance(
                client_data,
                current_focus,
                matrix_size=args.matrix_size,
                focus_weight=args.weight,
                palette=engine_palette_arg,
                calculation_mode=args.mode,
                hrv_sim=args.hrv_sim,
                precomputed_signature=client_sig,
                emf_compensate=args.emf_compensate,
                symmetry=args.symmetry
            )
            # Kennzeichnung des Hardware-Modus
            hw = result.get("hardware", "")
            if "CUDA" not in hw:
                result["hardware"] = f"{hw} (CUDA)"
        except Exception as e:
            print(f"FATAL: Engine-Berechnung fehlgeschlagen: {e}", flush=True)
            sys.exit(1)
        
        # Daten aufbereiten
        matrix = result["matrix_12x12"]
        flat_string = "".join([str(val) for row in matrix for val in row])
        result["rates_string"] = flat_string
        if "client_name" not in result:
            result["client_name"] = full_name
        result["focus"] = current_focus
        result["birth_place"] = args.place
        result["planet"] = args.planet
        result["focus_weight"] = args.weight
        
        all_results.append(result)
        
        # Console Output (Full for single, Short for sequence)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        client_sig = result.get("client_signature", {})
        client_freq = client_sig.get("frequency", 0.0)
        
        if len(focus_list) == 1:
            print(f"\nERGEBNIS ({timestamp})", flush=True)
            print(f"Score:        {result['resonance_score']:.4f}", flush=True)
            if result.get('hrv_score'):
                print(f"HRV Score:    {result['hrv_score']:.2f} (Kohaerenz-Modulation)", flush=True)
            emf_data = result.get('emf_compensation')
            if emf_data and emf_data.get('active'):
                emf_idx = emf_data.get('emf_index', 0)
                ent_sc = emf_data.get('entropy_score', 0)
                rec = emf_data.get('timing_recommendation', {})
                rec_label = rec.get('recommendation', '?') if rec else '?'
                print(f"EMF Index:    {emf_idx:.3f} | Entropy: {ent_sc:.3f} | Umfeld: {rec_label}", flush=True)
                counters = emf_data.get('counter_frequencies', [])
                if counters:
                    cf_str = ", ".join([f"{c['frequency_hz']}Hz" for c in counters])
                    print(f"Counter-Freq: {cf_str}", flush=True)
            # Amplifier-Empfehlung
            amp_recs = result.get('amplifier_recommendations', [])
            active_amp = result.get('amplifier')
            if active_amp and active_amp.get('active'):
                print(f"Verstaerker:  {active_amp['name']} (Faktor: {active_amp['amplification_factor']}, {active_amp['element']})", flush=True)
            elif amp_recs:
                print(f"Empf. Verst.: {amp_recs[0]['name']} ({amp_recs[0]['score']*100:.1f}%)", flush=True)
                for r in amp_recs[0].get('reasons', [])[:2]:
                    print(f"  -> {r}", flush=True)
            print(f"Client Vector:{client_freq:.2f} Hz", flush=True)
            print(f"Hardware:     {result['hardware']}", flush=True)
            sym_mode = result.get('symmetry', 'none')
            if sym_mode != 'none':
                sym_labels = {"horizontal": "Spiegel (Links-Rechts)", "quadrant": "Mandala (4-Quadranten)"}
                print(f"Symmetrie:    {sym_labels.get(sym_mode, sym_mode)}", flush=True)
            msize = result.get('matrix_size', args.matrix_size)
            print(f"Matrix:       {msize}x{msize} ({msize*msize} Zellen)", flush=True)
            print(f"\n{msize}x{msize} MATRIX:", flush=True)
            for row in matrix:
                print("  " + " ".join(str(x) for x in row), flush=True)
            print(f"\n{msize*msize} RATES STRING:", flush=True)
            print(flat_string, flush=True)
            print("\n========================================", flush=True)
        else:
            print(f"  -> Score: {result['resonance_score']:.4f} | Freq: {client_freq:.2f} Hz | Rates: {flat_string[:20]}...", flush=True)

        # Export logic per item
        timestamp_file = datetime.now().strftime('%Y%m%d_%H%M%S')
        out_dir = ensure_output_dir(full_name, timestamp_file)
        
        # Unique file base for sequence items
        if len(focus_list) > 1:
            safe_focus = "".join([c for c in current_focus if c.isalnum()])[:15]
            file_base = f"{full_name.replace(' ', '_')}_{timestamp_file}_{idx+1}_{safe_focus}"
        else:
            file_base = f"{full_name.replace(' ', '_')}_{timestamp_file}"
        
        final_palette_map = result.get("used_palette")
        if not final_palette_map:
            if isinstance(engine_palette_arg, dict):
                final_palette_map = engine_palette_arg
            else:
                final_palette_map = get_palette("Radionik (Standard)")
        
        final_palette_map = {int(k): v for k, v in final_palette_map.items()}
        all_palette_maps[idx] = final_palette_map
        
        # Logs
        log_path = os.path.join(out_dir, "analysis_log.txt")
        try:
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(f"\n[{timestamp}] {full_name} | {current_focus}\n")
                f.write(f"Score: {result['resonance_score']:.4f} | HW: {result['hardware']}\n")
                f.write(f"Palette: {args.palette}\n")
                f.write(f"String: {flat_string}\n")
        except Exception as e:
            print(f"Log Fehler: {e}", flush=True)

    # Konfigurationsdaten fuer Berichte
    config_summary = get_config_summary(args, result)
    exported_paths = [os.path.join(out_dir, "analysis_log.txt")]
    
    # Einzel-Exports (letzter Fokus als Einzelbericht)
    try:
        single_pdf_path = os.path.join(out_dir, f"{file_base}.pdf")
        single_xlsx_path = os.path.join(out_dir, f"{file_base}.xlsx")
        export_to_pdf(result, single_pdf_path, palette_map=final_palette_map, palette_name=args.palette, config_summary=config_summary)
        export_to_excel(result, single_xlsx_path, palette_map=final_palette_map, palette_name=args.palette, config_summary=config_summary)
        exported_paths.extend([single_pdf_path, single_xlsx_path])
    except Exception as e:
        print(f"Export Fehler: {e}", flush=True)
    
    # Kombiniertes PDF: Alle Matrizen in einem PDF (2 Seiten pro Fokus)
    try:
        combined_base = f"{full_name.replace(' ', '_')}_{timestamp_file}_KOMPLETT"
        combined_pdf_path = os.path.join(out_dir, f"{combined_base}.pdf")
        export_combined_pdf(
            all_results,
            combined_pdf_path,
            palette_maps=all_palette_maps,
            palette_name=args.palette,
            config_summary=config_summary
        )
        exported_paths.append(combined_pdf_path)
    except Exception as e:
        print(f"Kombiniertes PDF Fehler: {e}", flush=True)
    
    # Template-Historie speichern
    save_session_template(args, client_data, full_name, args.focus)

    try:
        archive_summary = mirror_session_archive(
            args=args,
            client_data=client_data,
            full_name=full_name,
            focus_list=focus_list,
            all_results=all_results,
            out_dir=out_dir,
            exported_paths=exported_paths,
            harmonization_status="requested" if args.harmonize else "not_requested",
        )
        print(f"Session-Archiv gespiegelt: {archive_summary['session_id']} | Client: {archive_summary['client_id']}", flush=True)
    except Exception as e:
        print(f"Archiv-Spiegelung fehlgeschlagen: {e}", flush=True)

    # Decide what to pass to harmonization
    if len(all_results) == 1:
        result_to_pass = all_results[0]
        out_dir_final = ensure_output_dir(full_name, datetime.now().strftime('%Y%m%d_%H%M%S')) # Fallback
    else:
        result_to_pass = all_results
        # Use the last out_dir which is the session folder
        out_dir_final = out_dir

    # --- Harmonisierung (Optional) ---
    if args.harmonize:
        # Prepare Transmission Data
        transmission_items = []
        
        # Check if we have a sequence or single result
        if isinstance(result_to_pass, list):
            # Sequence Mode (Reduced to top 3 per focus)
            print(f"\nStarte Sequenz-Harmonisierung ({len(result_to_pass)} Fokus-Themen x 3 Varianten)...", flush=True)
            for res in result_to_pass:
                # Add Top 3 variants for EACH focus in the sequence
                for idx, item in enumerate(res.get("top_10", [])[:3]):
                    transmission_items.append({
                        "matrix": item.get("matrix_data", item.get("matrix_12x12")),
                        "label": f"{res['focus']} (Var {idx+1})",
                        "client_freq": res.get("client_signature", {}).get("frequency", 432.0),
                        "bio_info": res.get("bio_info"),
                        "emf_data": res.get("emf_compensation"),
                        "amplifier": res.get("amplifier"),
                        "palette": res.get("used_palette")
                    })
        elif "top_10" in result_to_pass:
            # Standard Mode (Top 3 of single focus)
            print("\nStarte Standard-Harmonisierung (Top 3 Varianten)...", flush=True)
            for idx, item in enumerate(result_to_pass["top_10"][:3]):
                transmission_items.append({
                    "matrix": item.get("matrix_data", item.get("matrix_12x12")),
                    "label": f"{result_to_pass['focus']} (Var {idx+1})",
                    "client_freq": result_to_pass.get("client_signature", {}).get("frequency", 432.0),
                    "bio_info": result_to_pass.get("bio_info"),
                    "emf_data": result_to_pass.get("emf_compensation"),
                    "amplifier": result_to_pass.get("amplifier"),
                    "palette": result_to_pass.get("used_palette")
                })
        
        if transmission_items:
            print("Dr\u00fccken Sie ESC zum Beenden...", flush=True)
            try:
                import tkinter as tk
                import threading
                import winsound
                import tempfile
                
                class HarmonizerWindow:
                    def __init__(self, items, palette_map, pulse_sec, pause_sec, duration_factor, client_name, use_audio=False, solfeggio_freq=528.0, output_dir=None, template_name=""):
                        self.items = items # List of dicts {matrix, label, client_freq}
                        self.palette = palette_map
                        self.template_name = template_name
                        self.pulse_ms = int(pulse_sec * 1000)
                        self.pause_ms = int(pause_sec * 1000)
                        self.total_duration_sec = duration_factor * 21 * 60
                        self.start_time = time.time()
                        self.client_name = client_name
                        self.use_audio = use_audio
                        self.output_dir = output_dir
                        
                        self.current_idx = 0
                        self.is_blank = False
                        self.running = True
                        # Session Audio Export Accumulator
                        self.session_audio_parts = []
                        self.export_done = False
                        
                        # Calculate Coherent Background + Label Colors from Palette
                        bg_hex = "#0a0a14"
                        self.label_primary = "#FFFFFF"
                        self.label_secondary = "#00FF00"
                        self.label_muted = "#AAAAAA"
                        self.label_bright = "#CCCCCC"
                        if palette_map:
                            try:
                                r_total, g_total, b_total = 0, 0, 0
                                count = 0
                                brightest_lum = 0
                                brightest_hex = "#FFFFFF"
                                second_hex = "#CCCCCC"
                                sorted_by_lum = []
                                for hex_val in palette_map.values():
                                    h = hex_val.lstrip('#')
                                    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
                                    r_total += r; g_total += g; b_total += b
                                    count += 1
                                    lum = 0.299 * r + 0.587 * g + 0.114 * b
                                    sorted_by_lum.append((lum, r, g, b, hex_val))
                                sorted_by_lum.sort(key=lambda x: x[0], reverse=True)
                                if count > 0:
                                    # Background: 20% des Palette-Durchschnitts (sichtbar, aber dunkel)
                                    r_bg = min(255, int((r_total / count) * 0.20))
                                    g_bg = min(255, int((g_total / count) * 0.20))
                                    b_bg = min(255, int((b_total / count) * 0.20))
                                    bg_hex = f"#{r_bg:02x}{g_bg:02x}{b_bg:02x}"
                                    # Primary Label: Hellste Palette-Farbe (aufgehellt auf 85% min)
                                    lr, lg, lb = sorted_by_lum[0][1], sorted_by_lum[0][2], sorted_by_lum[0][3]
                                    boost = max(1.0, 210.0 / max(max(lr, lg, lb), 1))
                                    lr = min(255, int(lr * boost)); lg = min(255, int(lg * boost)); lb = min(255, int(lb * boost))
                                    self.label_primary = f"#{lr:02x}{lg:02x}{lb:02x}"
                                    # Secondary Label: Zweithellste Palette-Farbe (aufgehellt)
                                    if len(sorted_by_lum) > 1:
                                        sr, sg, sb = sorted_by_lum[1][1], sorted_by_lum[1][2], sorted_by_lum[1][3]
                                        boost2 = max(1.0, 180.0 / max(max(sr, sg, sb), 1))
                                        sr = min(255, int(sr * boost2)); sg = min(255, int(sg * boost2)); sb = min(255, int(sb * boost2))
                                        self.label_secondary = f"#{sr:02x}{sg:02x}{sb:02x}"
                                    # Muted Label: Palette-Mittelwert bei 50% Helligkeit
                                    mr = min(255, int((r_total / count) * 0.50))
                                    mg = min(255, int((g_total / count) * 0.50))
                                    mb = min(255, int((b_total / count) * 0.50))
                                    self.label_muted = f"#{mr:02x}{mg:02x}{mb:02x}"
                                    # Bright Label: Palette-Mittelwert bei 70% Helligkeit (fuer HW + Template)
                                    br = min(255, int((r_total / count) * 0.70))
                                    bg_ = min(255, int((g_total / count) * 0.70))
                                    bb = min(255, int((b_total / count) * 0.70))
                                    self.label_bright = f"#{br:02x}{bg_:02x}{bb:02x}"
                            except:
                                bg_hex = "#0a0a14"
                        self.bg_color = bg_hex
                        self.text_color = self.label_primary

                        # Fenster-Groesse adaptiv fuer Matrix-Groesse
                        sample_msize = len(items[0]["matrix"]) if items and items[0].get("matrix") else 12
                        if sample_msize <= 12:
                            win_w, win_h, canvas_sz = 500, 520, 375
                        elif sample_msize <= 24:
                            win_w, win_h, canvas_sz = 1030, 1020, 830
                        else:
                            win_w, win_h, canvas_sz = 1200, 1180, 980
                        self.canvas_size = canvas_sz
                        
                        self.root = tk.Tk()
                        self.root.title(f"Harmonisierung - {client_name}")
                        self.root.geometry(f"{win_w}x{win_h}")
                        self.root.configure(bg=self.bg_color)
                        
                        self.root.bind("<Escape>", lambda e: self.close())
                        
                        # Template-Label (unterste Zeile, IMMER sichtbar)
                        tpl_display = f"Template: {self.template_name}" if self.template_name else "Template: (ohne Bezeichnung)"
                        self.template_label = tk.Label(
                            self.root,
                            text=tpl_display,
                            font=("Arial", 8, "italic"),
                            fg=self.label_bright,
                            bg=self.bg_color
                        )
                        self.template_label.pack(side="bottom", pady=(0, 10))
                        
                        self.info_label = tk.Label(
                            self.root, 
                            text="Initialisiere...", 
                            font=("Arial", 10, "bold"), 
                            fg=self.label_primary, 
                            bg=self.bg_color
                        )
                        self.info_label.pack(side="bottom", pady=(10, 2))
                        
                        # Add Bio-Info Label
                        bio_text = ""
                        if items[0].get('bio_info'):
                            bio = items[0]['bio_info']['data']
                            bio_text = f"Resonanz: {bio['name']} ({bio.get('frequency_hz')} Hz)"
                        
                        self.bio_label = tk.Label(
                            self.root,
                            text=bio_text,
                            font=("Arial", 9, "italic"),
                            fg=self.label_secondary,
                            bg=self.bg_color
                        )
                        self.bio_label.pack(side="bottom", pady=5)
                        
                        # Add Hardware Status Label
                        self.hw_label = tk.Label(
                            self.root,
                            text="Echtzeit-Hardware: STANDBY (Visual/Audio Transmission)",
                            font=("Arial", 8),
                            fg=self.label_bright,
                            bg=self.bg_color
                        )
                        self.hw_label.pack(side="bottom", pady=5)
                        
                        self.canvas = tk.Canvas(
                            self.root, 
                            width=self.canvas_size, 
                            height=self.canvas_size, 
                            bg=self.bg_color, 
                            highlightthickness=0
                        )
                        self.canvas.pack(expand=False, pady=(10, 0))
                        
                        # Audio State
                        self.current_wav = None
                        self.temp_path = None
                        self.last_freq = 0
                        
                        # Start cycle
                        self.solfeggio_freq = solfeggio_freq
                        self.update_content()
                        self.root.after(self.pulse_ms, self.cycle_step)

                    def close(self):
                        self.running = False
                        self.stop_audio()
                        self.export_session_audio()
                        self.root.destroy()
                        if self.temp_path and os.path.exists(self.temp_path):
                            try:
                                os.remove(self.temp_path)
                            except:
                                pass

                    def export_session_audio(self):
                        """Exports the accumulated session audio as a single high-quality lossless WAV file."""
                        if not self.use_audio or not self.session_audio_parts or not self.output_dir or self.export_done:
                            return
                        
                        try:
                            print(f"\nGeneriere Session-Audio-Export...", flush=True)
                            combined_data = b"".join(self.session_audio_parts)
                            n_samples = len(combined_data) // 2
                            sample_rate = 44100
                            
                            header = b'RIFF' + struct.pack('<I', 36 + n_samples * 2) + b'WAVE' + b'fmt ' + struct.pack('<I', 16) + \
                                     struct.pack('<H', 1) + struct.pack('<H', 1) + struct.pack('<I', sample_rate) + \
                                     struct.pack('<I', sample_rate * 2) + struct.pack('<H', 2) + struct.pack('<H', 16) + \
                                     b'data' + struct.pack('<I', n_samples * 2)
                            
                            out_file = os.path.join(self.output_dir, f"session_audio_lossless.wav")
                            with open(out_file, "wb") as f:
                                f.write(header + combined_data)
                            print(f"[OK] Verlustfreier Audio-Export gespeichert: {out_file}", flush=True)
                            self.export_done = True
                        except Exception as e:
                            print(f"Export Fehler (Audio): {e}", flush=True)

                    def stop_audio(self):
                        if self.use_audio:
                            try:
                                winsound.PlaySound(None, winsound.SND_PURGE)
                            except Exception:
                                pass

                    def play_audio(self):
                        if self.use_audio and self.temp_path:
                            try:
                                winsound.PlaySound(None, winsound.SND_PURGE)
                                winsound.PlaySound(self.temp_path, winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_NODEFAULT)
                            except Exception as e:
                                print(f"Audio Fehler (ignoriert): {e}", flush=True)

                    def generate_sine_wave(self, frequency, duration=30.0, sample_rate=44100, amplitude=0.12, solfeggio_freq=528.0, emf_counters=None, amplifier_freqs=None):
                        # High-Performance Long-Duration Ambient Engine mit EMF + Amplifier
                        frequency = max(30.0, min(frequency, 4000.0))
                        n_samples = int(sample_rate * duration)
                        t = np.linspace(0, duration, n_samples, endpoint=False)
                        
                        f1 = frequency
                        f2 = frequency * 1.5 # Fifth
                        f3 = float(solfeggio_freq)
                        f4 = frequency / 2.0 # Octave
                        
                        # Generate Layered Resonance
                        w1 = amplitude * np.sin(2 * np.pi * f1 * t)
                        w2 = (amplitude * 0.1) * np.sin(2 * np.pi * f2 * t)
                        w3 = (amplitude * 0.05) * np.sin(2 * np.pi * f3 * t)
                        w4 = (amplitude * 0.15) * np.sin(2 * np.pi * f4 * t)
                        
                        mixed = (w1 + w2 + w3 + w4) / 1.2
                        
                        # EMF Counter-Frequency Layers (subtile Kompensations-Toene)
                        if emf_counters:
                            for cf in emf_counters[:3]:
                                cf_hz = cf.get("frequency_hz", 0)
                                cf_amp = cf.get("amplitude", 0.3) * amplitude * 0.03
                                if 20 < cf_hz < 4000:
                                    mixed += cf_amp * np.sin(2 * np.pi * cf_hz * t)
                        
                        # Amplifier-Frequency Layers (Verstaerker-Resonanz)
                        if amplifier_freqs:
                            for af in amplifier_freqs[:4]:
                                af_hz = af.get("frequency_hz", 0)
                                af_amp = af.get("amplitude", 0.5) * amplitude * 0.08
                                if 20 < af_hz < 4000:
                                    mixed += af_amp * np.sin(2 * np.pi * af_hz * t)
                        
                        # Apply a long fade-in (500ms) and fade-out (500ms) for stability
                        fade_len = int(sample_rate * 0.5)
                        if n_samples > 2 * fade_len:
                            mixed[:fade_len] *= np.linspace(0, 1, fade_len)
                            mixed[-fade_len:] *= np.linspace(1, 0, fade_len)
                        
                        # Final conversion to 16-bit PCM
                        audio_data = (mixed * 32767).astype(np.int16)
                        
                        # WAV Header
                        header = b'RIFF' + struct.pack('<I', 36 + n_samples * 2) + b'WAVE' + b'fmt ' + struct.pack('<I', 16) + \
                                 struct.pack('<H', 1) + struct.pack('<H', 1) + struct.pack('<I', sample_rate) + \
                                 struct.pack('<I', sample_rate * 2) + struct.pack('<H', 2) + struct.pack('<H', 16) + \
                                 b'data' + struct.pack('<I', n_samples * 2)
                        
                        return header + audio_data.tobytes()

                    def draw_matrix(self, matrix, item_palette=None):
                        self.canvas.delete("all")
                        grid_size = len(matrix) if matrix else 12
                        cell_size = self.canvas_size / grid_size
                        font_size = max(6, int(cell_size * 0.45))
                        
                        # Fokus-spezifische Palette verwenden falls vorhanden
                        pal = item_palette if item_palette else self.palette
                        
                        for r, row in enumerate(matrix):
                            for c, val in enumerate(row):
                                try:
                                    val_int = int(val)
                                except:
                                    val_int = 0
                                    
                                x1 = c * cell_size
                                y1 = r * cell_size
                                x2 = x1 + cell_size
                                y2 = y1 + cell_size
                                
                                hex_color = pal.get(val_int, "#FFFFFF")
                                self.canvas.create_rectangle(x1, y1, x2, y2, fill=hex_color, outline=hex_color)
                                
                                text_color = get_contrast_color(hex_color)
                                center_x = x1 + (cell_size / 2)
                                center_y = y1 + (cell_size / 2)
                                self.canvas.create_text(center_x, center_y, text=str(val), fill=text_color, font=("Arial", font_size, "bold"))
                                
                    def update_content(self):
                        if not self.running: return

                        item = self.items[self.current_idx]
                        
                        # 1. Update Audio if Freq changed (mit EMF + Amplifier Frequencies)
                        freq = item["client_freq"]
                        emf_cfs = None
                        emf_d = item.get("emf_data")
                        if emf_d and emf_d.get("active"):
                            emf_cfs = emf_d.get("counter_frequencies")
                        # Amplifier-Frequenzen sammeln
                        amp_freqs = None
                        amp_d = item.get("amplifier")
                        if amp_d and amp_d.get("active"):
                            amp_freqs = amp_d.get("audio_frequencies")
                        if self.use_audio and (freq != self.last_freq or self.current_wav is None):
                            self.current_wav = self.generate_sine_wave(freq, solfeggio_freq=self.solfeggio_freq, emf_counters=emf_cfs, amplifier_freqs=amp_freqs)
                            self.last_freq = freq
                            
                            try:
                                if self.temp_path and os.path.exists(self.temp_path):
                                    try:
                                        os.remove(self.temp_path)
                                    except:
                                        pass
                                
                                fd, self.temp_path = tempfile.mkstemp(suffix=".wav")
                                os.close(fd)
                                with open(self.temp_path, "wb") as f:
                                    f.write(self.current_wav)
                            except Exception as e:
                                print(f"Temp Audio Error: {e}", flush=True)
                        
                        # 2. Draw Visuals (mit fokus-spezifischer Palette falls vorhanden)
                        item_pal = None
                        if item.get("palette"):
                            try:
                                item_pal = {int(k): v for k, v in item["palette"].items()}
                            except:
                                pass
                        self.draw_matrix(item["matrix"], item_palette=item_pal)
                        self.play_audio()
                        
                        # 3. Add to Session Audio Accumulator (Pulse only)
                        if self.use_audio and self.current_wav:
                            # Extract PCM data without header (header is 44 bytes)
                            pulse_samples = int(44100 * (self.pulse_ms / 1000.0))
                            pcm_data = self.current_wav[44 : 44 + (pulse_samples * 2)]
                            self.session_audio_parts.append(pcm_data)
                        
                        # 4. Update Label (mit Restlaufzeit)
                        elapsed = time.time() - self.start_time
                        remaining = max(0, self.total_duration_sec - elapsed)
                        r_mins = int(remaining // 60)
                        r_secs = int(remaining % 60)
                        self.info_label.config(text=f"{self.client_name} | {item['label']} | IMPULS | Rest: {r_mins:02d}:{r_secs:02d}")

                    def cycle_step(self):
                        if not self.running: return
                        
                        elapsed = time.time() - self.start_time
                        remaining = self.total_duration_sec - elapsed
                        if remaining <= 0:
                            self.close()
                            return
                        
                        mins = int(remaining // 60)
                        secs = int(remaining % 60)
                        
                        if self.is_blank:
                            self.is_blank = False
                            self.current_idx = (self.current_idx + 1) % len(self.items)
                            self.update_content()
                            self.root.after(self.pulse_ms, self.cycle_step)
                        else:
                            self.is_blank = True
                            self.canvas.delete("all")
                            self.stop_audio()
                            
                            # Add Silence to session audio accumulator during pause
                            if self.use_audio:
                                pause_samples = int(44100 * (self.pause_ms / 1000.0))
                                silence = b'\x00' * (pause_samples * 2)
                                self.session_audio_parts.append(silence)
                            
                            self.info_label.config(text=f"{self.client_name} | PAUSE | Rest: {mins:02d}:{secs:02d}")
                            self.root.after(self.pause_ms, self.cycle_step)
                            
                    def start(self):
                        self.root.mainloop()

                # Create Harmonizer Instance
                app = HarmonizerWindow(
                    items=transmission_items,
                    palette_map=final_palette_map,
                    pulse_sec=args.pulse,
                    pause_sec=args.pause,
                    duration_factor=args.duration,
                    client_name=result_to_pass[0]['client_name'] if isinstance(result_to_pass, list) else result_to_pass['client_name'],
                    use_audio=args.audio,
                    solfeggio_freq=args.solfeggio,
                    output_dir=out_dir_final,
                    template_name=getattr(args, 'template_name', '')
                )
                app.start()
            
            except Exception as e:
                print(f"Fehler bei Harmonisierung: {e}", flush=True)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nAbbruch: Vorgang vom Benutzer beendet.", flush=True)
        sys.exit(0)
        sys.exit(0)
