#!/usr/bin/env python3
"""
Remedy Reporter - Extrahiert und berichtet synergetische Remedy-Kombinationen

Erstellt separaten HTML-Bericht für Remedy-Empfehlungen aus Scan-Daten.
Speichert unter C:/Benutzer_Remedies_Start/<Klient>/

Verwendung:
    python -m tools.remedy_reporter "Nachname" "Vorname"
    python -m tools.remedy_reporter "Nachname" "Vorname" --single

Erstellt: 02.12.2025
"""

import json
import argparse
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Projektpfade
SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent

# Füge Projektverzeichnis zum Path hinzu für Imports
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from tools.label_converter import convert_legacy_label

# Produktions-Pfade
ARCHIVE_DIR = Path(r"C:\Benutzer_Archive_Start")
REMEDIES_DIR = Path(r"C:\Benutzer_Remedies_Start")


def find_client_folder(last_name: str, first_name: str) -> Optional[Path]:
    """Findet den Klienten-Ordner."""
    pattern = f"{last_name}_{first_name}_*"
    folders = list(ARCHIVE_DIR.glob(pattern))
    
    if not folders:
        return None
    
    # Neuester Ordner (nach Modifikationszeit)
    return sorted(folders, key=lambda f: f.stat().st_mtime)[-1]


def find_latest_scan(client_folder: Path, scan_type: str = "any") -> Optional[Path]:
    """
    Findet den neuesten Scan-Ordner.
    
    Args:
        client_folder: Klienten-Ordner
        scan_type: "SINGLE", "SESSION" oder "any"
    """
    scan_folders = []
    
    for item in client_folder.iterdir():
        if not item.is_dir():
            continue
        
        if scan_type == "SINGLE" and "_SINGLE" in item.name:
            scan_folders.append(item)
        elif scan_type == "SESSION" and "_SESSION" in item.name:
            scan_folders.append(item)
        elif scan_type == "any":
            if "_SINGLE" in item.name or "_SESSION" in item.name:
                scan_folders.append(item)
    
    if not scan_folders:
        return None
    
    # Neuester Ordner
    scan_folders.sort(key=lambda f: f.stat().st_mtime, reverse=True)
    return scan_folders[0]


def load_scan_data(json_path: Path) -> Optional[Dict]:
    """Lädt Scan-Daten aus JSON."""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠ Fehler beim Laden von {json_path.name}: {e}")
        return None


def generate_remedy_html(client_name: str, profile: str, focus: str, remedies: List[Dict], timestamp: str) -> str:
    """Generiert HTML-Bericht für Remedy-Kombinationen."""
    html_lines = []
    
    # Header
    html_lines.append("<!DOCTYPE html><html><head><meta charset='utf-8'>")
    html_lines.append(f"<title>Remedy Report - {client_name}</title>")
    
    # Modern Light Design CSS
    html_lines.append("<style>")
    html_lines.append("""
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%);
            color: #2C3E50;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.95);
            padding: 40px;
            border-radius: 16px;
            box-shadow: 0 8px 24px rgba(107, 165, 208, 0.2);
            backdrop-filter: blur(10px);
        }
        h1 {
            color: #3498DB;
            border-bottom: 3px solid #6BA5D0;
            padding-bottom: 12px;
            margin-bottom: 25px;
            font-size: 28pt;
        }
        h2 {
            color: #2980B9;
            margin-top: 35px;
            margin-bottom: 20px;
            font-size: 18pt;
        }
        .meta {
            background: linear-gradient(135deg, rgba(167,199,231,0.15), rgba(107,165,208,0.10));
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 30px;
            border: 1px solid rgba(107,165,208,0.2);
        }
        .meta p {
            margin: 8px 0;
            font-size: 11pt;
        }
        .remedy-item {
            background: linear-gradient(135deg, #FFFFFF, #F8F9FA);
            padding: 20px;
            margin: 15px 0;
            border-left: 5px solid #6BA5D0;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            transition: all 0.3s ease;
        }
        .remedy-item:hover {
            transform: translateX(5px);
            box-shadow: 0 4px 12px rgba(107,165,208,0.2);
        }
        .remedy-combo {
            font-size: 12pt;
            font-weight: 600;
            color: #2C3E50;
            margin-bottom: 10px;
        }
        .score {
            display: inline-block;
            padding: 6px 14px;
            background: linear-gradient(135deg, #FF6B9D, #FFA07A);
            color: white;
            border-radius: 20px;
            font-size: 10pt;
            font-weight: 600;
            box-shadow: 0 2px 8px rgba(255,107,157,0.3);
        }
        .rates {
            font-family: 'Fira Code', 'Consolas', monospace;
            font-size: 10pt;
            color: #6BA5D0;
            margin-top: 8px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            font-size: 11pt;
        }
        th {
            background: linear-gradient(135deg, #6BA5D0, #5B95C0);
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
        }
        td {
            padding: 12px;
            border-bottom: 1px solid #E0E0E0;
        }
        tr:hover {
            background: rgba(107,165,208,0.05);
        }
        .note {
            font-size: 10pt;
            color: #7f8c8d;
            font-style: italic;
            margin: 10px 0;
        }
        .badge {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 10pt;
            font-weight: 600;
            color: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.15);
        }
        .prio-high {
            background: linear-gradient(135deg, #2ECC71, #27AE60);
        }
        .prio-mid {
            background: linear-gradient(135deg, #F39C12, #E67E22);
        }
        .prio-low {
            background: linear-gradient(135deg, #95A5A6, #7F8C8D);
        }
        .footer {
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            color: #7f8c8d;
            font-size: 9pt;
            text-align: center;
        }
        @media print {
            body { background: #FFF !important; }
            .container { box-shadow: none !important; }
        }
    """)
    html_lines.append("</style></head><body><div class='container'>")
    
    # Title
    html_lines.append(f"<h1>💊 Synergetische Remedy-Kombinationen</h1>")
    
    # Meta-Info
    html_lines.append("<div class='meta'>")
    html_lines.append(f"<p><strong>Klient:</strong> {client_name}</p>")
    html_lines.append(f"<p><strong>Profil:</strong> {profile}</p>")
    if focus:
        html_lines.append(f"<p><strong>Fokus:</strong> {focus}</p>")
    html_lines.append(f"<p><strong>Datum:</strong> {datetime.now().strftime('%d.%m.%Y %H:%M')}</p>")
    html_lines.append(f"<p><strong>Anzahl Kombinationen:</strong> {len(remedies)}</p>")
    html_lines.append("</div>")
    
    # Remedy-Liste - Tabellen-Layout wie im Multiplex-Scan
    html_lines.append("<h2>⚡ Synergetische Remedy-Kombinationen (Rate-Overlap-Analyse)</h2>")
    html_lines.append("<p class='note'>Basierend auf Frequenz-Ähnlichkeit. Es werden nur Remedies aus den entsprechenden Remedy-Gruppen (Homöopathie/TCM-Rezepturen/Spagyrik/etc.) berücksichtigt.</p>")
    html_lines.append("<table>")
    html_lines.append("<tr><th>Remedy 1</th><th>Remedy 2</th><th>Synergy Score</th><th>Raten (Base 10)</th><th>Copen-Raten</th></tr>")
    
    for i, rem in enumerate(remedies[:20], 1):  # Top 20
        item1 = convert_legacy_label(rem.get("item1", ""), rem.get("rate1"))
        item2 = convert_legacy_label(rem.get("item2", ""), rem.get("rate2"))
        score = rem.get("synergy_score", 0)
        rate1 = rem.get("rate1", [0, 0])
        rate2 = rem.get("rate2", [0, 0])
        
        # Base-10 Raten formatieren
        if isinstance(rate1, (list, tuple)) and len(rate1) >= 2:
            rate1_str = f"[ {float(rate1[0]):.2f} - {float(rate1[1]):.2f} ]"
        else:
            rate1_str = "[]"
        
        if isinstance(rate2, (list, tuple)) and len(rate2) >= 2:
            rate2_str = f"[ {float(rate2[0]):.2f} - {float(rate2[1]):.2f} ]"
        else:
            rate2_str = "[]"
        
        # Copen-Raten berechnen (Durchschnitt des Bereichs)
        copen1 = ""
        copen2 = ""
        if isinstance(rate1, (list, tuple)) and len(rate1) >= 2:
            avg_rate1 = (float(rate1[0]) + float(rate1[1])) / 2
            copen1 = f"{avg_rate1:.0f}"
        
        if isinstance(rate2, (list, tuple)) and len(rate2) >= 2:
            avg_rate2 = (float(rate2[0]) + float(rate2[1])) / 2
            copen2 = f"{avg_rate2:.0f}"
        
        # Synergy Score Badge
        if score > 0.7:
            badge_class = "prio-high"
        elif score > 0.5:
            badge_class = "prio-mid"
        else:
            badge_class = "prio-low"
        
        html_lines.append("<tr>")
        html_lines.append(f"<td><strong>{item1}</strong></td>")
        html_lines.append(f"<td><strong>{item2}</strong></td>")
        html_lines.append(f"<td><span class='badge {badge_class}'>{score:.2f}</span></td>")
        html_lines.append(f"<td class='rates'>{rate1_str}<br>{rate2_str}</td>")
        html_lines.append(f"<td>{copen1}<br>{copen2}</td>")
        html_lines.append("</tr>")
    
    html_lines.append("</table>")
    html_lines.append("<p class='note' style='font-size:11px;'>Synergie-Score: 0.0-0.3 = schwach, 0.3-0.5 = mittel, 0.5-0.7 = gut, 0.7-1.0 = sehr stark.</p>")
    
    # Footer
    html_lines.append("<div class='footer'>")
    html_lines.append(f"<p>Generiert am {datetime.now().strftime('%d.%m.%Y %H:%M:%S')} | Morphic Engine Remedy Reporter</p>")
    html_lines.append("</div>")
    
    html_lines.append("</div></body></html>")
    
    return "\n".join(html_lines)


def create_remedy_report(last_name: str, first_name: str, scan_type: str = "any") -> Optional[Dict]:
    """
    Erstellt Remedy-Bericht aus Scan-Daten.
    
    Args:
        last_name: Nachname
        first_name: Vorname
        scan_type: "SINGLE", "SESSION" oder "any"
    """
    print("=" * 70)
    print("REMEDY REPORTER")
    print("=" * 70)
    print(f"Klient: {first_name} {last_name}")
    print(f"Scan-Typ: {scan_type}")
    print("-" * 70)
    
    # Finde Klienten-Ordner
    client_folder = find_client_folder(last_name, first_name)
    if not client_folder:
        print(f"❌ Kein Ordner gefunden für {first_name} {last_name}")
        return None
    
    print(f"📁 Klienten-Ordner: {client_folder}")
    
    # Finde neuesten Scan
    scan_folder = find_latest_scan(client_folder, scan_type)
    if not scan_folder:
        print(f"❌ Kein Scan-Ordner gefunden (Typ: {scan_type})")
        return None
    
    print(f"📦 Scan-Ordner: {scan_folder.name}")
    
    # Suche Scan-JSON
    scan_json = list(scan_folder.rglob("*_multiplex_scan.json"))
    if not scan_json:
        print("❌ Keine Scan-JSON gefunden")
        return None
    
    # Nehme neueste JSON (falls mehrere)
    scan_json.sort(key=lambda f: f.stat().st_mtime, reverse=True)
    scan_file = scan_json[0]
    print(f"📊 Scan-Datei: {scan_file.name}")
    
    # Lade Scan-Daten
    scan_data = load_scan_data(scan_file)
    if not scan_data:
        return None
    
    # Extrahiere Remedy-Synergien
    remedy_synergies = scan_data.get("remedy_synergies", [])
    profile = scan_data.get("profile", "unknown")
    
    print(f"   ✓ Profil: {profile}")
    print(f"   ✓ {len(remedy_synergies)} Remedy-Kombinationen gefunden")
    
    if not remedy_synergies:
        print("⚠ Keine Remedy-Synergien im Scan vorhanden")
        return None
    
    # Erstelle Ausgabe-Ordner
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    client_folder_name = client_folder.name
    remedies_client_dir = REMEDIES_DIR / client_folder_name
    remedies_client_dir.mkdir(parents=True, exist_ok=True)
    
    # Generiere HTML-Bericht
    client_name = f"{first_name} {last_name}"
    focus = scan_data.get("focus", "")
    html_content = generate_remedy_html(client_name, profile, focus, remedy_synergies, timestamp)
    
    # Speichere HTML
    scan_label = "single" if "_SINGLE" in scan_folder.name else "top5"
    html_path = remedies_client_dir / f"{timestamp}_{scan_label}_remedies.html"
    
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print(f"\n✅ Remedy-Bericht gespeichert: {html_path}")
    
    return {
        "html": html_path,
        "profile": profile,
        "remedies": remedy_synergies
    }


def consolidate_remedy_synergies(json_files: List[Path], output_dir: Path) -> bool:
    """
    Konsolidiert Remedy-Synergien aus mehreren Scans (Top-N) zu einem Bericht.
    
    Args:
        json_files: Liste von JSON-Scan-Dateien
        output_dir: Ausgabeverzeichnis
        
    Returns:
        True bei Erfolg, False bei Fehler
    """
    try:
        from collections import defaultdict
        
        # Sammle Remedy-Synergien pro Profil
        remedies_by_profile = defaultdict(list)
        all_remedies = []
        client_info = None
        focus = None
        
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Client-Info (einmal erfassen)
                if client_info is None:
                    client_info = {
                        "name": data.get("name", ""),
                        "first_name": data.get("first_name", ""),
                        "birth_date": data.get("birth_date", ""),
                        "birth_place": data.get("birth_place", "")
                    }
                    focus = data.get("focus", "")
                
                profile = data.get("profile", "unknown")
                remedy_synergies = data.get("remedy_synergies", [])
                
                if remedy_synergies:
                    remedies_by_profile[profile].extend(remedy_synergies)
                    all_remedies.extend(remedy_synergies)
            
            except Exception as e:
                print(f"⚠ Fehler beim Lesen von {json_file}: {e}")
                continue
        
        if not all_remedies:
            print("⚠ Keine Remedy-Synergien gefunden")
            return False
        
        # Erstelle HTML-Report im REMEDIES_DIR
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Bestimme Client-Ordner
        if client_info.get("name") and client_info.get("first_name"):
            client_folder_name = f"{client_info['name']}_{client_info['first_name']}_" + \
                                client_info.get('birth_date', '').replace('.', '')[:8] + "_" + \
                                client_info.get('birth_place', '').replace(' ', '')
            remedies_client_dir = REMEDIES_DIR / client_folder_name
            remedies_client_dir.mkdir(parents=True, exist_ok=True)
            report_path = remedies_client_dir / f"{timestamp}_remedy_kombinationen_top{len(json_files)}.html"
        else:
            # Fallback
            report_name = f"{timestamp}_remedy_kombinationen_top{len(json_files)}.html"
            report_path = output_dir / report_name if output_dir else Path.cwd() / report_name
        
        html = _generate_consolidated_remedy_html(
            remedies_by_profile=remedies_by_profile,
            all_remedies=all_remedies,
            client_info=client_info,
            focus=focus
        )
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"✓ Remedy-Report gespeichert: {report_path}")
        return True
    
    except Exception as e:
        print(f"❌ Fehler beim Konsolidieren der Remedy-Synergien: {e}")
        return False


def _generate_consolidated_remedy_html(
    remedies_by_profile: Dict[str, List[Dict]],
    all_remedies: List[Dict],
    client_info: Dict,
    focus: str
) -> str:
    """Generiert HTML für konsolidierten Remedy-Report."""
    html_lines = []
    
    # HTML Header
    html_lines.append("<!DOCTYPE html><html lang='de'><head>")
    html_lines.append("<meta charset='UTF-8'>")
    html_lines.append("<meta name='viewport' content='width=device-width, initial-scale=1.0'>")
    html_lines.append(f"<title>Remedy-Kombinationen Report - {client_info['first_name']} {client_info['name']}</title>")
    
    # CSS
    html_lines.append("<style>")
    html_lines.append("""
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%);
            color: #2C3E50;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.95);
            padding: 40px;
            border-radius: 16px;
            box-shadow: 0 8px 24px rgba(107, 165, 208, 0.2);
        }
        h1 { color: #3498DB; border-bottom: 3px solid #6BA5D0; padding-bottom: 12px; margin-bottom: 25px; }
        h2 { color: #2980B9; margin-top: 35px; margin-bottom: 20px; }
        .meta { background: linear-gradient(135deg, rgba(167,199,231,0.15), rgba(107,165,208,0.10)); padding: 20px; border-radius: 12px; margin-bottom: 30px; }
        .profile-section { border-left: 4px solid #6BA5D0; padding-left: 20px; margin: 30px 0; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        th { background: linear-gradient(135deg, #6BA5D0, #5B95C0); color: white; padding: 12px; text-align: left; }
        td { padding: 10px 12px; border-bottom: 1px solid #E0E0E0; }
        tr:hover { background: rgba(107,165,208,0.05); }
        .badge { display: inline-block; padding: 4px 10px; border-radius: 12px; font-size: 10pt; font-weight: 600; color: white; }
        .prio-high { background: linear-gradient(135deg, #2ECC71, #27AE60); }
        .prio-mid { background: linear-gradient(135deg, #F39C12, #E67E22); }
        .prio-low { background: linear-gradient(135deg, #95A5A6, #7F8C8D); }
    """)
    html_lines.append("</style></head><body><div class='container'>")
    
    # Title
    html_lines.append(f"<h1>💊 Konsolidierte Remedy-Kombinationen (Top-{len(remedies_by_profile)})</h1>")
    
    # Meta-Info
    html_lines.append("<div class='meta'>")
    html_lines.append(f"<p><strong>Klient:</strong> {client_info['first_name']} {client_info['name']}</p>")
    html_lines.append(f"<p><strong>Profile:</strong> {len(remedies_by_profile)}</p>")
    if focus:
        html_lines.append(f"<p><strong>Fokus:</strong> {focus}</p>")
    html_lines.append(f"<p><strong>Datum:</strong> {datetime.now().strftime('%d.%m.%Y %H:%M')}</p>")
    html_lines.append(f"<p><strong>Gesamt-Kombinationen:</strong> {len(all_remedies)}</p>")
    html_lines.append("</div>")
    
    # Remedy-Kombinationen pro Profil
    for profile, remedies in sorted(remedies_by_profile.items()):
        html_lines.append(f"<div class='profile-section'>")
        html_lines.append(f"<h2>⚡ Profil: {profile}</h2>")
        html_lines.append(f"<p><em>{len(remedies)} Remedy-Kombinationen</em></p>")
        html_lines.append("<table>")
        html_lines.append("<tr><th>Remedy 1</th><th>Remedy 2</th><th>Synergy Score</th><th>Raten (Base 10)</th></tr>")
        
        for rem in remedies[:10]:  # Top 10 pro Profil
            item1 = convert_legacy_label(rem.get("item1", ""), rem.get("rate1"))
            item2 = convert_legacy_label(rem.get("item2", ""), rem.get("rate2"))
            score = rem.get("synergy_score", 0)
            rate1 = rem.get("rate1", [0, 0])
            rate2 = rem.get("rate2", [0, 0])
            
            rate1_str = f"[ {float(rate1[0]):.2f} - {float(rate1[1]):.2f} ]" if isinstance(rate1, (list, tuple)) and len(rate1) >= 2 else "[]"
            rate2_str = f"[ {float(rate2[0]):.2f} - {float(rate2[1]):.2f} ]" if isinstance(rate2, (list, tuple)) and len(rate2) >= 2 else "[]"
            
            badge_class = "prio-high" if score > 0.7 else ("prio-mid" if score > 0.5 else "prio-low")
            
            html_lines.append(f"<tr>")
            html_lines.append(f"<td>{item1}</td>")
            html_lines.append(f"<td>{item2}</td>")
            html_lines.append(f"<td><span class='badge {badge_class}'>{score:.2f}</span></td>")
            html_lines.append(f"<td>{rate1_str} & {rate2_str}</td>")
            html_lines.append(f"</tr>")
        
        html_lines.append("</table>")
        html_lines.append("</div>")
    
    # Top 20 übergreifend
    html_lines.append("<h2>🏆 Top-20 Remedy-Kombinationen (Übergreifend)</h2>")
    all_remedies_sorted = sorted(all_remedies, key=lambda x: x.get("synergy_score", 0), reverse=True)
    
    html_lines.append("<table>")
    html_lines.append("<tr><th>Remedy 1</th><th>Remedy 2</th><th>Synergy Score</th><th>Raten (Base 10)</th></tr>")
    
    for rem in all_remedies_sorted[:20]:
        item1 = convert_legacy_label(rem.get("item1", ""), rem.get("rate1"))
        item2 = convert_legacy_label(rem.get("item2", ""), rem.get("rate2"))
        score = rem.get("synergy_score", 0)
        rate1 = rem.get("rate1", [0, 0])
        rate2 = rem.get("rate2", [0, 0])
        
        rate1_str = f"[ {float(rate1[0]):.2f} - {float(rate1[1]):.2f} ]" if isinstance(rate1, (list, tuple)) and len(rate1) >= 2 else "[]"
        rate2_str = f"[ {float(rate2[0]):.2f} - {float(rate2[1]):.2f} ]" if isinstance(rate2, (list, tuple)) and len(rate2) >= 2 else "[]"
        
        badge_class = "prio-high" if score > 0.7 else ("prio-mid" if score > 0.5 else "prio-low")
        
        html_lines.append(f"<tr>")
        html_lines.append(f"<td>{item1}</td>")
        html_lines.append(f"<td>{item2}</td>")
        html_lines.append(f"<td><span class='badge {badge_class}'>{score:.2f}</span></td>")
        html_lines.append(f"<td>{rate1_str} & {rate2_str}</td>")
        html_lines.append(f"</tr>")
    
    html_lines.append("</table>")
    
    # Footer
    html_lines.append("<div style='margin-top:40px;padding-top:20px;border-top:1px solid #ddd;color:#7f8c8d;font-size:9pt;text-align:center;'>")
    html_lines.append(f"Morphic Engine V1 | Konsolidierter Remedy-Report | {datetime.now().strftime('%d.%m.%Y %H:%M')}")
    html_lines.append("</div>")
    
    html_lines.append("</div></body></html>")
    
    return "\n".join(html_lines)


def main():
    """CLI-Einstiegspunkt."""
    parser = argparse.ArgumentParser(
        description="Erstellt Remedy-Bericht aus Scan-Daten"
    )
    parser.add_argument("last_name", help="Nachname des Klienten")
    parser.add_argument("first_name", help="Vorname des Klienten")
    parser.add_argument("--single", action="store_true", help="Nur Single-Scans")
    parser.add_argument("--session", action="store_true", help="Nur SESSION-Scans")
    
    args = parser.parse_args()
    
    # Bestimme Scan-Typ
    if args.single:
        scan_type = "SINGLE"
    elif args.session:
        scan_type = "SESSION"
    else:
        scan_type = "any"
    
    result = create_remedy_report(
        last_name=args.last_name,
        first_name=args.first_name,
        scan_type=scan_type
    )
    
    if result:
        print(f"\n📂 Bericht: {result['html']}")
    else:
        print("\n❌ Remedy-Report fehlgeschlagen")
        exit(1)


if __name__ == "__main__":
    main()
