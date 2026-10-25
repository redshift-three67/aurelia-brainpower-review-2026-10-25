#!/usr/bin/env python3
"""
Synergy Consolidator für Morphic Engine V1

Konsolidiert Synergy-Daten aus mehreren Scan-Berichten (z.B. Top-5 Analyse)
und erstellt einen Gesamt-Synergy-Bericht.

Funktionen:
- Sammelt synergetische Remedy-Kombinationen aus allen Profil-Scans
- Sammelt Quantum-Synergy Trigger aus allen Profil-Scans
- Identifiziert Cross-Profile Synergien (Items in mehreren Profilen)
- Erstellt konsolidierten HTML/JSON-Bericht

Verwendung:
    python -m tools.synergy_consolidator "Nachname" "Vorname" --birth-date DDMMYYYY --birth-place "Ort"
    
Erstellt: 01.12.2025
"""

import json
import argparse
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from collections import defaultdict
import numpy as np

# Füge Projektverzeichnis zum Path hinzu für Imports
SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from tools.label_converter import convert_legacy_label

# Produktions-Pfade
ARCHIVE_DIR = Path(r"C:\Benutzer_Archive_Start")
SYNERGY_DIR = Path(r"C:\Benutzer_Synergy_Start")


def find_client_folder(last_name: str, first_name: str, base_dir: Path) -> Optional[Path]:
    """Findet den Klienten-Ordner.
    
    Einfache Logik: Suche nach Name_Vorname_* Pattern.
    SESSION-Erkennung erfolgt in den Unterordnern.
    """
    pattern = f"{last_name}_{first_name}_*"
    folders = list(base_dir.glob(pattern))
    
    if not folders:
        return None
    
    # Neuester Ordner (nach Modifikationszeit)
    return sorted(folders, key=lambda f: f.stat().st_mtime)[-1]


def find_recent_scans(client_folder: Path, hours: int = 24) -> List[Path]:
    """
    Findet alle Scan-JSON-Dateien der letzten X Stunden.
    
    PRIORITÄT 1: Sucht nach neuesten Top-5 SESSION-Ordnern (alle Scans daraus)
    PRIORITÄT 2: Einzelne Scans der letzten X Stunden
    
    Berücksichtigt die neue Unterordner-Struktur.
    """
    if not client_folder.exists():
        return []
    
    cutoff = datetime.now().timestamp() - (hours * 3600)
    scan_files = []
    
    # PRIORITÄT 1: Suche nach Top-5 SESSION-Ordnern (erkennbar an _top5 im Namen)
    session_folders = []
    for item in client_folder.iterdir():
        if item.is_dir() and ("_top5" in item.name.lower() or "_session" in item.name.lower()):
            # Prüfe ob Session-Ordner innerhalb des Zeitfensters erstellt wurde
            if item.stat().st_mtime >= cutoff:
                session_folders.append(item)
    
    # Wenn Top-5 Session-Ordner gefunden, nimm ALLE Scans daraus
    if session_folders:
        # Neuester Session-Ordner zuerst
        session_folders.sort(key=lambda f: f.stat().st_mtime, reverse=True)
        latest_session = session_folders[0]
        print(f"📦 Top-5 Session gefunden: {latest_session.name}")
        
        # Sammle alle Scans aus diesem Session-Ordner
        for json_file in latest_session.rglob("*_multiplex_scan.json"):
            scan_files.append(json_file)
        
        if scan_files:
            print(f"   → {len(scan_files)} Scans im Session-Ordner")
            return scan_files
    
    # PRIORITÄT 2: Fallback - Suche einzelne Scans nach Zeitfenster
    for json_file in client_folder.rglob("*_multiplex_scan.json"):
        if json_file.stat().st_mtime >= cutoff:
            scan_files.append(json_file)
    
    # Sortiere nach Änderungszeit (neueste zuerst)
    scan_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
    return scan_files


def load_scan_data(json_path: Path) -> Optional[Dict]:
    """Lädt Scan-Daten aus JSON-Datei."""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"  ⚠ Fehler beim Laden von {json_path.name}: {e}")
        return None


def extract_remedy_synergies(scan_data: Dict) -> List[Dict]:
    """Extrahiert oder berechnet synergetische Remedy-Kombinationen aus Scan-Daten."""
    # Erst prüfen ob bereits berechnet
    synergies = scan_data.get("remedy_synergies", [])
    if synergies:
        return synergies if isinstance(synergies, list) else []
    
    # WICHTIG: Die Raten sind in sub_results.top, NICHT in nls_scores!
    # nls_scores hat keine rates, sub_results.top hat rates und copen_rate
    sub_results = scan_data.get("sub_results", {})
    if isinstance(sub_results, dict):
        top_items = sub_results.get("top", [])
        if top_items and len(top_items) >= 2:
            # Prüfe ob rates vorhanden
            if top_items[0].get("rates"):
                return _calculate_remedy_synergies_simple(top_items[:100], max_results=10)
    
    # Fallback: Versuche nls_scores (falls rates vorhanden)
    nls_scores = scan_data.get("nls_scores", [])
    if nls_scores and len(nls_scores) >= 2:
        # Prüfe ob rates vorhanden
        if nls_scores[0].get("rates"):
            return _calculate_remedy_synergies_simple(nls_scores, max_results=10)
    
    return []


def _calculate_remedy_synergies_simple(items: List[Dict], max_results: int = 10) -> List[Dict]:
    """Einfache Berechnung von Remedy-Synergien basierend auf Rate-Overlap."""
    if not items or len(items) < 2:
        return []
    
    # Map von Label auf Item
    label_to_item = {}
    for it in items:
        lbl = str(it.get("label", "") or "").strip()
        if lbl:
            label_to_item[lbl] = it
    
    if len(label_to_item) < 2:
        return []
    
    # Sammle Synergien
    main_synergies = {}
    labels = list(label_to_item.keys())
    
    for i in range(len(labels)):
        for j in range(i + 1, len(labels)):
            lbl1, lbl2 = labels[i], labels[j]
            item1, item2 = label_to_item[lbl1], label_to_item[lbl2]
            
            rates1 = item1.get("rates", [])
            rates2 = item2.get("rates", [])
            if not rates1 or not rates2:
                continue
            
            try:
                r1 = np.array([float(x) for x in rates1[:2]])
                r2 = np.array([float(x) for x in rates2[:2]])
                if r1.shape[0] == 0 or r2.shape[0] == 0:
                    continue
                
                distance = np.linalg.norm(r1 - r2)
                synergy_score = max(0.0, 10.0 - distance / 10.0)
                
                if synergy_score <= 5.0:
                    continue
                
                main_synergies.setdefault(lbl1, {})[lbl2] = synergy_score
                main_synergies.setdefault(lbl2, {})[lbl1] = synergy_score
            except Exception:
                continue
    
    if not main_synergies:
        return []
    
    # Baue Ergebnisstruktur
    results = []
    for main_label, partners in main_synergies.items():
        item = label_to_item.get(main_label, {})
        main_score = float(item.get("score", 0.0) or 0.0)
        rates_raw = item.get("rates", []) or []
        rates_clean = [float(x) for x in rates_raw[:2]] if rates_raw else []
        copen_rate = item.get("copen_rate")
        
        partner_list = [
            {"partner_label": pl, "synergy_score": float(ps)}
            for pl, ps in partners.items()
        ]
        partner_list.sort(key=lambda e: e["synergy_score"], reverse=True)
        
        if not partner_list:
            continue
        
        result_item = {
            "label": main_label,
            "score": main_score,
            "rates": rates_clean,
            "synergies": partner_list,
            "_max_partner_synergy": partner_list[0]["synergy_score"],
        }
        if copen_rate is not None:
            result_item["copen_rate"] = copen_rate
        results.append(result_item)
    
    results.sort(key=lambda x: x.get("_max_partner_synergy", 0.0), reverse=True)
    trimmed = results[:max_results]
    for r in trimmed:
        r.pop("_max_partner_synergy", None)
    return trimmed


def extract_quantum_synergies(scan_data: Dict) -> List[Dict]:
    """Extrahiert Quantum-Synergy Kombinationen aus Scan-Daten."""
    if scan_data is None:
        return []
    return scan_data.get("quantum_synergy", [])


def extract_top_items(scan_data: Dict, limit: int = 20) -> List[Dict]:
    """Extrahiert Top-Items aus Scan-Daten."""
    items = scan_data.get("nls_scores", [])
    if not items:
        items = scan_data.get("top_items", [])
    return items[:limit]


def consolidate_synergies(scan_files: List[Path], base_dir: Path = None):
    """
    Konsolidiert Synergy-Daten aus mehreren Scan-Dateien.
    
    Args:
        scan_files: Liste von JSON-Scan-Dateien
        base_dir: Basis-Verzeichnis für Output (wenn gesetzt: generiert HTML und gibt bool zurück)
    
    Returns:
        Wenn base_dir gegeben: True/False
        Sonst: Dict mit konsolidierten Daten
    """
    try:
        result = {
            "profiles_analyzed": [],
            "remedy_synergies": defaultdict(lambda: {"count": 0, "scores": [], "profiles": []}),
            "quantum_synergies": [],
            "cross_profile_items": defaultdict(lambda: {"count": 0, "scores": [], "profiles": []}),
            "total_scans": 0,
            "focus": "",
            "client_info": {}  # NEU: Client-Metadaten
        }
        
        for json_path in scan_files:
            scan_data = load_scan_data(json_path)
            if not scan_data:
                continue
            
            result["total_scans"] += 1
            
            # Client-Info (einmal erfassen) - NEU!
            if not result["client_info"]:
                result["client_info"] = {
                    "name": scan_data.get("name", ""),
                    "first_name": scan_data.get("first_name", ""),
                    "birth_date": scan_data.get("birth_date", ""),
                    "birth_place": scan_data.get("birth_place", "")
                }
            
            # Profil-Name extrahieren
            profile = scan_data.get("profile", "unknown")
            result["profiles_analyzed"].append(profile)
            
            # Fokus übernehmen (vom ersten Scan)
            if not result["focus"] and scan_data.get("focus"):
                result["focus"] = scan_data.get("focus")
            
            # Remedy-Synergien sammeln
            for syn in extract_remedy_synergies(scan_data):
                label = syn.get("label", "")
                if label:
                    entry = result["remedy_synergies"][label]
                    entry["count"] += 1
                    entry["scores"].append(syn.get("score", 0))
                    entry["profiles"].append(profile)
                    entry["rates"] = syn.get("rates", [])
                    entry["copen_rate"] = syn.get("copen_rate")
                    entry["synergies"] = syn.get("synergies", [])
            
            # Quantum-Synergien sammeln
            try:
                quantum_synergies = extract_quantum_synergies(scan_data)
                if quantum_synergies:
                    for qs in quantum_synergies:
                        qs["source_profile"] = profile
                        result["quantum_synergies"].append(qs)
            except Exception as e:
                print(f"   ⚠️ Fehler bei Quantum-Synergien für {profile}: {e}")
            
            # Top-Items für Cross-Profile Analyse
            for item in extract_top_items(scan_data):
                label = item.get("label", "")
                if label:
                    entry = result["cross_profile_items"][label]
                    entry["count"] += 1
                    entry["scores"].append(item.get("score", 0))
                    entry["profiles"].append(profile)
                    entry["group"] = item.get("group", "")
        
        # Konvertiere defaultdicts zu normalen dicts
        result["remedy_synergies"] = dict(result["remedy_synergies"])
        result["cross_profile_items"] = dict(result["cross_profile_items"])
        
        # MODUS 1: MIT base_dir → Generiere HTML und gebe bool zurück
        if base_dir is not None:
            # Bestimme Output-Pfad
            if result["client_info"].get("name"):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                client_folder_name = f"{result['client_info']['name']}_{result['client_info']['first_name']}_" + \
                                    result['client_info'].get('birth_date', '').replace('.', '')[:8] + "_" + \
                                    result['client_info'].get('birth_place', '').replace(' ', '')
                synergy_client_dir = SYNERGY_DIR / client_folder_name
                synergy_client_dir.mkdir(parents=True, exist_ok=True)
                output_path = synergy_client_dir / f"{timestamp}_synergy_report"
            else:
                output_path = Path.cwd() / "synergy_report"
            
            # Generiere HTML-Report
            generate_html_report(
                consolidated=result,
                client_name=result["client_info"].get("name", ""),
                client_first_name=result["client_info"].get("first_name", ""),
                output_path=output_path
            )
            
            print(f"✓ Synergy-Report gespeichert: {output_path}")
            return True
        
        # MODUS 2: OHNE base_dir → Gebe Dictionary zurück (für CLI-Tool)
        else:
            return result
    
    except Exception as e:
        print(f"❌ Fehler beim Konsolidieren der Synergien: {e}")
        import traceback
        traceback.print_exc()
        
        # Im Fehlerfall: bool wenn base_dir gesetzt, sonst None
        if base_dir is not None:
            return False
        else:
            return None


def generate_html_report(
    consolidated: Dict[str, Any],
    client_name: str,
    client_first_name: str,
    output_path: Path
) -> Path:
    """Generiert HTML-Bericht aus konsolidierten Daten."""
    
    timestamp = datetime.now().strftime("%d.%m.%Y %H:%M")
    profiles = consolidated["profiles_analyzed"]
    focus = consolidated["focus"]
    client_info = consolidated.get("client_info", {})
    
    # Sortiere Remedy-Synergien nach Häufigkeit
    remedy_syn = sorted(
        consolidated["remedy_synergies"].items(),
        key=lambda x: (x[1]["count"], sum(x[1]["scores"]) / max(len(x[1]["scores"]), 1)),
        reverse=True
    )
    
    # Sortiere Cross-Profile Items nach Häufigkeit
    cross_items = sorted(
        [(k, v) for k, v in consolidated["cross_profile_items"].items() if v["count"] >= 2],
        key=lambda x: (x[1]["count"], sum(x[1]["scores"]) / max(len(x[1]["scores"]), 1)),
        reverse=True
    )[:20]
    
    # Sortiere Quantum-Synergien nach Score
    quantum_syn = sorted(
        consolidated["quantum_synergies"],
        key=lambda x: x.get("score", 0),
        reverse=True
    )[:10]
    
    html = f"""<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Synergy-Gesamtanalyse - {client_first_name} {client_name}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Inter', 'Segoe UI', Roboto, Arial, sans-serif;
            background: linear-gradient(135deg, #E8F1F8 0%, #D8E8F0 50%, #C5DAE8 100%);
            min-height: 100vh;
            color: #2C3E50;
            padding: 30px 20px;
            font-size: 11pt;
            line-height: 1.6;
        }}
        .container {{
            max-width: 1100px;
            margin: 0 auto;
            background: rgba(255,255,255,0.75);
            backdrop-filter: blur(20px);
            border-radius: 24px;
            box-shadow: 0 8px 32px rgba(107,165,208,0.15), 0 2px 8px rgba(0,0,0,0.05);
            border: 1px solid rgba(255,255,255,0.8);
            overflow: hidden;
        }}
        .header {{
            background: rgba(255,255,255,0.75);
            backdrop-filter: blur(20px);
            padding: 30px;
            text-align: center;
            box-shadow: 0 8px 32px rgba(107,165,208,0.15);
            border-bottom: 1px solid rgba(107,165,208,0.2);
        }}
        .header h1 {{
            margin: 0 0 12px;
            font-size: 22pt;
            font-weight: 600;
            color: #2C3E50;
            letter-spacing: -0.5px;
        }}
        .header .subtitle {{
            font-size: 11pt;
            color: #5D6D7E;
        }}
        .meta {{
            display: flex;
            justify-content: center;
            gap: 30px;
            margin-top: 15px;
            font-size: 14px;
        }}
        .meta span {{
            background: linear-gradient(135deg, rgba(107,165,208,0.15), rgba(167,199,231,0.20));
            padding: 8px 18px;
            border-radius: 24px;
            color: #3D5A73;
            font-weight: 500;
            border: 1px solid rgba(107,165,208,0.25);
        }}
        .content {{
            padding: 30px;
        }}
        .section {{
            margin-bottom: 30px;
        }}
        .section h2 {{
            color: #3D5A73;
            font-size: 16pt;
            font-weight: 600;
            margin: 0 0 18px;
            padding: 12px 20px;
            background: linear-gradient(135deg, rgba(107,165,208,0.08), rgba(167,199,231,0.12));
            border-radius: 12px;
            border-left: 4px solid #6BA5D0;
        }}
        .section h3 {{
            color: #4a5568;
            font-size: 16px;
            margin: 20px 0 10px;
        }}
        .card {{
            background: rgba(255,255,255,0.6);
            border: 1px solid rgba(107,165,208,0.15);
            border-radius: 12px;
            padding: 18px;
            margin-bottom: 15px;
            transition: all 0.2s ease;
        }}
        .card:hover {{
            transform: translateX(4px);
            box-shadow: 0 4px 16px rgba(107,165,208,0.12);
        }}
        .card.highlight {{
            border-left: 4px solid #6BA5D0;
        }}
        .card.quantum {{
            border-left: 4px solid #ffc107;
        }}
        .card-title {{
            font-weight: 600;
            color: #2d3748;
            margin-bottom: 8px;
        }}
        .card-meta {{
            font-size: 13px;
            color: #718096;
        }}
        .badge {{
            display: inline-block;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 500;
            margin-right: 5px;
        }}
        .badge-primary {{ background: linear-gradient(135deg, #6BA5D0, #7FB5DB); color: white; box-shadow: 0 2px 8px rgba(107,165,208,0.3); }}
        .badge-success {{ background: linear-gradient(135deg, #77DD77, #98D8C8); color: white; box-shadow: 0 2px 8px rgba(119,221,119,0.3); }}
        .badge-warning {{ background: linear-gradient(135deg, #FFB347, #FFCC80); color: white; box-shadow: 0 2px 8px rgba(255,179,71,0.3); }}
        .badge-info {{ background: linear-gradient(135deg, #6BA5D0, #A7C7E7); color: white; box-shadow: 0 2px 8px rgba(107,165,208,0.3); }}
        .score {{
            font-size: 18px;
            font-weight: 600;
            color: #6BA5D0;
        }}
        .profiles-list {{
            display: flex;
            flex-wrap: wrap;
            gap: 5px;
            margin-top: 8px;
        }}
        .profile-tag {{
            background: linear-gradient(135deg, rgba(107,165,208,0.12), rgba(167,199,231,0.18));
            padding: 6px 12px;
            border-radius: 16px;
            font-size: 11px;
            color: #3D5A73;
            font-weight: 500;
            border: 1px solid rgba(107,165,208,0.2);
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
        }}
        th, td {{
            padding: 10px 12px;
            text-align: left;
            border-bottom: 1px solid #e2e8f0;
        }}
        th {{
            background: #f7fafc;
            font-weight: 600;
            color: #4a5568;
        }}
        tr:hover {{
            background: #f7fafc;
        }}
        .footer {{
            background: #f7fafc;
            padding: 20px 30px;
            text-align: center;
            font-size: 12px;
            color: #718096;
            border-top: 1px solid #e2e8f0;
        }}
        @media print {{
            body {{ background: white; padding: 0; }}
            .container {{ box-shadow: none; }}
            .header {{ background: #667eea !important; -webkit-print-color-adjust: exact; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>⚛️ Synergy-Gesamtanalyse</h1>
            <div class="subtitle">{client_first_name} {client_name}</div>
            <div class="meta">
                <span>📊 {len(profiles)} Profile analysiert</span>
                <span>🎯 Fokus: {focus or 'Allgemein'}</span>
                <span>📅 {timestamp}</span>
            </div>
            <div class="meta" style="margin-top:10px;">
                <span>🎂 {client_info.get('birth_date', '–')}</span>
                <span>📍 {client_info.get('birth_place', '–')}</span>
            </div>
        </div>
        
        <div class="content">
            <!-- Analysierte Profile -->
            <div class="section">
                <h2>📋 Analysierte Profile</h2>
                <div class="profiles-list">
"""
    
    for profile in profiles:
        html += f'                    <span class="profile-tag">{profile}</span>\n'
    
    html += """                </div>
            </div>
            
            <!-- Cross-Profile Synergien -->
            <div class="section">
                <h2>🔗 Cross-Profile Synergien</h2>
                <p style="color:#718096;font-size:14px;">Items, die in mehreren Profilen hohe Resonanz zeigen:</p>
"""
    
    if cross_items:
        html += """                <table>
                    <thead>
                        <tr>
                            <th>Item</th>
                            <th>Gruppe</th>
                            <th>Profile</th>
                            <th>Ø Score</th>
                        </tr>
                    </thead>
                    <tbody>
"""
        for label, data in cross_items[:15]:
            avg_score = sum(data["scores"]) / len(data["scores"]) if data["scores"] else 0
            profiles_str = ", ".join(set(data["profiles"]))
            html += f"""                        <tr>
                            <td><strong>{label}</strong></td>
                            <td>{data.get('group', '-')}</td>
                            <td><span class="badge badge-info">{data['count']}x</span> {profiles_str}</td>
                            <td class="score">{avg_score:.2f}</td>
                        </tr>
"""
        html += """                    </tbody>
                </table>
"""
    else:
        html += '                <p style="color:#a0aec0;">Keine Cross-Profile Synergien gefunden.</p>\n'
    
    html += """            </div>
            
            <!-- HINWEIS: Remedy-Kombinationen wurden in separaten Remedy-Report verschoben -->
"""
    
    # Gruppiere Quantum-Synergien nach Profil
    quantum_by_profile = {}
    for qs in consolidated["quantum_synergies"]:
        profile = qs.get("source_profile", "unknown")
        if profile not in quantum_by_profile:
            quantum_by_profile[profile] = []
        quantum_by_profile[profile].append(qs)
    
    # Sortiere jede Profil-Liste nach Score
    for profile in quantum_by_profile:
        quantum_by_profile[profile] = sorted(
            quantum_by_profile[profile],
            key=lambda x: x.get("score", 0),
            reverse=True
        )
    
    html += """
            
            <!-- Quantum-Synergy Trigger PRO PROFIL -->
            <div class="section">
                <h2>⚛️ Quantum-Synergy Analyse</h2>
                <p style="color:#718096;font-size:14px;margin-bottom:20px;">Grover-basierte Multi-Item Kombinationen pro Profil:</p>
"""
    
    if quantum_by_profile:
        # Zeige Quantum-Synergien PRO PROFIL
        for profile_idx, (profile, synergies) in enumerate(sorted(quantum_by_profile.items()), 1):
            html += f"""
                <div style="background:#f8f9fa;padding:20px;border-radius:12px;margin-bottom:20px;border-left:4px solid #667eea;">
                    <h3 style="color:#667eea;margin-bottom:15px;">📊 Profil: {profile}</h3>
                    <p style="color:#718096;font-size:13px;margin-bottom:15px;">Quantum-Synergien aus diesem Profil ({len(synergies)} gefunden):</p>
"""
            
            for i, qs in enumerate(synergies[:5], 1):  # Top 5 pro Profil
                score = qs.get("score", 0)
                items = qs.get("items", [])
                components = qs.get("components", {})
                
                # Score-Bewertung
                if score >= 8.0:
                    level = "Sehr Hoch"
                    badge_class = "badge-success"
                elif score >= 7.0:
                    level = "Hoch"
                    badge_class = "badge-success"
                elif score >= 6.0:
                    level = "Mittel"
                    badge_class = "badge-warning"
                else:
                    level = "Niedrig"
                    badge_class = "badge-info"
                
                html += f"""
                    <div class="card quantum" style="margin-bottom:15px;">
                        <div class="card-title">#{i} – Synergy-Score: <span class="score">{score:.2f}/10.0</span> <span class="badge {badge_class}">{level}</span></div>
                        <div style="margin-top:12px;">
                            <strong>Kombination ({len(items)} Items):</strong>
                            <ul style="margin:8px 0;padding-left:20px;">
"""
                for item in items:
                    item_label = convert_legacy_label(item.get("label", ""), item.get("copen_rate"))
                    item_group = item.get("group", "")
                    html += f'                                <li>{item_label} <span style="color:#a0aec0;">({item_group})</span></li>\n'
                
                html += """                            </ul>
                        </div>
"""
                
                # Komponenten-Details wenn vorhanden
                if components:
                    html += """
                        <div style="margin-top:10px;padding:10px;background:#f8fafc;border-radius:6px;font-size:12px;">
                            <strong>Komponenten:</strong><br>
"""
                    if "individual_scores" in components:
                        html += f'                            • Einzelwirkungen: {components["individual_scores"]:.2f}/10.0<br>\n'
                    if "resonance" in components:
                        html += f'                            • Resonanz-Verstärkung: {components["resonance"]:.2f}/10.0<br>\n'
                    if "harmony" in components:
                        html += f'                            • Frequenz-Harmonien: {components["harmony"]:.2f}/10.0<br>\n'
                    if "relevance" in components:
                        html += f'                            • Fokus-Relevanz: {components["relevance"]:.2f}/10.0<br>\n'
                    html += """                        </div>
"""
                
                html += """                    </div>
"""
            
            html += """                </div>
"""
    else:
        html += """
                <div style="background:#fff3cd;border:1px solid #ffc107;padding:20px;margin:20px 0;border-radius:8px;">
                    <p style="margin:0;color:#856404;"><strong>ℹ️ Hinweis:</strong> Keine Quantum-Synergien gefunden.</p>
                    <p style="margin:10px 0 0 0;color:#856404;">Mögliche Gründe: Keine ausreichenden Resonanz-Überlappungen oder zu hoher Threshold.</p>
                </div>
"""
    
    # OPTIONAL: Kombinierte Top Quantum-Synergien über alle Profile
    if quantum_by_profile:
        all_quantum = sorted(
            consolidated["quantum_synergies"],
            key=lambda x: x.get("score", 0),
            reverse=True
        )[:5]  # Top 5 über alle Profile
        
        if len(quantum_by_profile) > 1 and all_quantum:  # Nur bei Multi-Profil-Scans
            html += """
            
            <!-- KOMBINIERTE TOP QUANTUM-SYNERGIEN -->
            <div class="section">
                <h2>🌟 Top Quantum-Synergien (Profile-übergreifend)</h2>
                <p style="color:#718096;font-size:14px;margin-bottom:20px;">Die besten 5 Quantum-Kombinationen aus allen analysierten Profilen:</p>
"""
            
            for i, qs in enumerate(all_quantum, 1):
                score = qs.get("score", 0)
                items = qs.get("items", [])
                source = qs.get("source_profile", "")
                components = qs.get("components", {})
                
                # Score-Bewertung
                if score >= 8.0:
                    level = "⭐ Sehr Hoch"
                    badge_class = "badge-success"
                    box_color = "#667eea"
                elif score >= 7.0:
                    level = "Hoch"
                    badge_class = "badge-success"
                    box_color = "#48bb78"
                else:
                    level = "Mittel"
                    badge_class = "badge-warning"
                    box_color = "#ed8936"
                
                html += f"""
                <div style="background:linear-gradient(135deg, rgba(102,126,234,0.08), rgba(167,199,231,0.12));padding:20px;border-radius:12px;margin-bottom:15px;border-left:4px solid {box_color};">
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
                        <div style="font-size:16px;font-weight:600;color:#2d3748;">#{i} – Score: {score:.2f}/10.0</div>
                        <div><span class="badge {badge_class}">{level}</span> <span style="font-size:13px;color:#718096;">Quelle: {source}</span></div>
                    </div>
                    <div style="margin-top:12px;">
                        <strong>Kombination ({len(items)} Items):</strong>
                        <ul style="margin:8px 0;padding-left:20px;">
"""
                
                for item in items:
                    item_label = convert_legacy_label(item.get("label", ""), item.get("copen_rate"))
                    item_group = item.get("group", "")
                    html += f'                            <li><strong>{item_label}</strong> <span style="color:#a0aec0;">({item_group})</span></li>\n'
                
                html += """                        </ul>
                    </div>
"""
                
                # Komponenten
                if components:
                    html += """
                    <div style="margin-top:12px;padding:12px;background:rgba(255,255,255,0.6);border-radius:6px;font-size:13px;">
                        <strong>🔬 Komponenten-Analyse:</strong><br>
"""
                    if "individual_scores" in components:
                        html += f'                        • Einzelwirkungen: <strong>{components["individual_scores"]:.2f}/10.0</strong><br>\n'
                    if "resonance" in components:
                        html += f'                        • Resonanz-Verstärkung: <strong>{components["resonance"]:.2f}/10.0</strong><br>\n'
                    if "harmony" in components:
                        html += f'                        • Frequenz-Harmonien: <strong>{components["harmony"]:.2f}/10.0</strong><br>\n'
                    if "relevance" in components:
                        html += f'                        • Fokus-Relevanz: <strong>{components["relevance"]:.2f}/10.0</strong><br>\n'
                    html += """                    </div>
"""
                
                html += """                </div>
"""
            
            html += """            </div>
"""
    
    html += f"""        </div>
        
        <div class="footer">
            <p>Morphic Engine V1 – Synergy-Gesamtanalyse</p>
            <p>Generiert am {timestamp}</p>
            <p style="margin-top:10px;font-size:11px;color:#a0aec0;">
                Diese Analyse dient ausschließlich zu Informationszwecken und ersetzt keine medizinische Beratung.
            </p>
        </div>
    </div>
</body>
</html>
"""
    
    # Speichern
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    return output_path


def generate_json_export(
    consolidated: Dict[str, Any],
    client_name: str,
    client_first_name: str,
    output_path: Path
) -> Path:
    """Speichert konsolidierte Daten als JSON."""
    
    export_data = {
        "client": {
            "name": client_name,
            "first_name": client_first_name,
        },
        "generated_at": datetime.now().isoformat(),
        "profiles_analyzed": consolidated["profiles_analyzed"],
        "total_scans": consolidated["total_scans"],
        "focus": consolidated["focus"],
        "remedy_synergies": consolidated["remedy_synergies"],
        "quantum_synergies": consolidated["quantum_synergies"],
        "cross_profile_items": consolidated["cross_profile_items"],
    }
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, ensure_ascii=False, indent=2)
    
    return output_path


def consolidate_client_synergies(
    last_name: str,
    first_name: str,
    birth_date: str = "",
    birth_place: str = "",
    hours: int = 24
) -> Optional[Dict[str, Path]]:
    """
    Hauptfunktion: Konsolidiert Synergien für einen Klienten.
    
    Args:
        last_name: Nachname
        first_name: Vorname
        birth_date: Geburtsdatum (optional, für Ordnersuche)
        birth_place: Geburtsort (optional, für Ordnersuche)
        hours: Zeitraum in Stunden für Scan-Suche
    
    Returns:
        Dict mit Pfaden zu generierten Dateien oder None bei Fehler
    """
    print("=" * 70)
    print("SYNERGY-KONSOLIDIERUNG")
    print("=" * 70)
    print(f"Klient: {first_name} {last_name}")
    print(f"Zeitraum: Letzte {hours} Stunden")
    print("-" * 70)
    
    # Finde Klienten-Ordner
    client_folder = find_client_folder(last_name, first_name, ARCHIVE_DIR)
    if not client_folder:
        print(f"❌ Kein Ordner gefunden für {first_name} {last_name}")
        return None
    
    print(f"📁 Klienten-Ordner: {client_folder}")
    
    # Finde Scan-Dateien
    scan_files = find_recent_scans(client_folder, hours)
    if not scan_files:
        print(f"❌ Keine Scans in den letzten {hours} Stunden gefunden")
        return None
    
    print(f"📊 {len(scan_files)} Scan-Dateien gefunden")
    for sf in scan_files[:5]:
        print(f"   - {sf.name}")
    if len(scan_files) > 5:
        print(f"   ... und {len(scan_files) - 5} weitere")
    
    # Konsolidiere Daten
    print("-" * 70)
    print("🔄 Konsolidiere Synergy-Daten...")
    consolidated = consolidate_synergies(scan_files)
    
    print(f"   ✓ {len(consolidated['profiles_analyzed'])} Profile")
    print(f"   ✓ {len(consolidated['remedy_synergies'])} Remedy-Synergien")
    print(f"   ✓ {len(consolidated['quantum_synergies'])} Quantum-Synergien")
    print(f"   ✓ {len([k for k,v in consolidated['cross_profile_items'].items() if v['count'] >= 2])} Cross-Profile Items")
    
    # Erstelle Ausgabe-Ordner
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Finde Klienten-Ordner-Name für Synergy-Verzeichnis
    client_folder_name = client_folder.name
    synergy_client_dir = SYNERGY_DIR / client_folder_name / f"{timestamp}_synergy_report"
    synergy_client_dir.mkdir(parents=True, exist_ok=True)
    
    # Generiere Berichte
    print("-" * 70)
    print("📝 Generiere Berichte...")
    
    html_path = synergy_client_dir / "synergy_gesamt.html"
    json_path = synergy_client_dir / "synergy_gesamt.json"
    
    generate_html_report(consolidated, last_name, first_name, html_path)
    print(f"   ✓ HTML: {html_path}")
    
    generate_json_export(consolidated, last_name, first_name, json_path)
    print(f"   ✓ JSON: {json_path}")
    
    print("=" * 70)
    print("✅ SYNERGY-KONSOLIDIERUNG ABGESCHLOSSEN")
    print("=" * 70)
    print(f"Berichte gespeichert in: {synergy_client_dir}")
    
    return {
        "html": html_path,
        "json": json_path,
        "folder": synergy_client_dir,
    }


def create_single_scan_synergy_report(last_name: str, first_name: str) -> Optional[Dict]:
    """
    Erstellt Synergy-Bericht für einen einzelnen Scan.
    
    Sucht nach neuestem SINGLE-Scan und extrahiert die Synergy-Daten.
    """
    print("=" * 70)
    print("SINGLE-SCAN SYNERGY-BERICHT")
    print("=" * 70)
    print(f"Klient: {first_name} {last_name}")
    print("-" * 70)
    
    # Finde Klienten-Ordner
    client_folder = find_client_folder(last_name, first_name, ARCHIVE_DIR)
    if not client_folder:
        print(f"❌ Kein Ordner gefunden für {first_name} {last_name}")
        return None
    
    print(f"📁 Klienten-Ordner: {client_folder}")
    
    # Suche nach neuestem SINGLE-Ordner
    single_folders = []
    for item in client_folder.iterdir():
        if item.is_dir() and "_SINGLE" in item.name:
            single_folders.append(item)
    
    if not single_folders:
        print("❌ Kein SINGLE-Scan Ordner gefunden")
        return None
    
    # Neuester SINGLE-Ordner
    single_folders.sort(key=lambda f: f.stat().st_mtime, reverse=True)
    latest_single = single_folders[0]
    print(f"📦 Single-Scan: {latest_single.name}")
    
    # Suche Scan-JSON
    scan_json = list(latest_single.glob("*_multiplex_scan.json"))
    if not scan_json:
        print("❌ Keine Scan-JSON gefunden")
        return None
    
    scan_file = scan_json[0]
    print(f"📊 Scan-Datei: {scan_file.name}")
    
    # Lade Scan-Daten
    scan_data = load_scan_data(scan_file)
    if not scan_data:
        return None
    
    # Extrahiere Synergy-Daten
    remedy_synergies = scan_data.get("remedy_synergies", []) or []
    quantum_synergies = scan_data.get("quantum_synergy", []) or []  # Beachte: "quantum_synergy" ohne 'ies'
    profile = scan_data.get("profile", "unknown")
    focus = scan_data.get("focus", "")
    
    print(f"   ✓ Profil: {profile}")
    if focus:
        print(f"   ✓ Fokus: {focus}")
    print(f"   ✓ {len(remedy_synergies)} Remedy-Synergien")
    print(f"   ✓ {len(quantum_synergies)} Quantum-Synergien")
    
    # Erstelle Ausgabe-Ordner
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    client_folder_name = client_folder.name
    synergy_client_dir = SYNERGY_DIR / client_folder_name
    synergy_client_dir.mkdir(parents=True, exist_ok=True)
    
    # Generiere vereinfachten HTML-Bericht
    html_path = synergy_client_dir / f"{timestamp}_single_synergy.html"
    
    # HTML-Content (modernes Layout wie im Multiplex-Scan)
    html_lines = []
    html_lines.append("<!DOCTYPE html><html><head><meta charset='utf-8'>")
    html_lines.append("<title>Single-Scan Synergy Report</title>")
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
        .rates {
            font-family: 'Fira Code', 'Consolas', monospace;
            font-size: 10pt;
            color: #6BA5D0;
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
    html_lines.append(f"<h1>🔮 Single-Scan Quantum Synergy Report</h1>")
    
    # Meta-Info
    html_lines.append("<div class='meta'>")
    html_lines.append(f"<p><strong>Klient:</strong> {first_name} {last_name}</p>")
    html_lines.append(f"<p><strong>Profil:</strong> {profile}</p>")
    if focus:
        html_lines.append(f"<p><strong>Fokus:</strong> {focus}</p>")
    html_lines.append(f"<p><strong>Datum:</strong> {datetime.now().strftime('%d.%m.%Y %H:%M')}</p>")
    html_lines.append(f"<p><strong>Quantum-Synergien gefunden:</strong> {len(quantum_synergies)}</p>")
    html_lines.append("</div>")
    
    # Quantum Synergies - Original-Layout wie im Multiplex
    # HINWEIS: Remedy-Kombinationen gehören in den separaten Remedy-Report!
    if quantum_synergies:
        html_lines.append("<h2 style='color:#667eea;'>⚛️ Quantum-Synergy Analyse</h2>")
        html_lines.append(
            "<p style='background:#f8f9fa;padding:14px;border-left:4px solid #667eea;margin-top:8px;'>" 
            "Diese Analyse basiert auf dem Quantum-inspirierten Grover-Ansatz. Es werden nur die stärksten Kombinationen "
            "aus dem aktuellen Scan berücksichtigt. Fokus: " + (focus if focus else "–") + "</p>"
        )
        
        for idx, combo in enumerate(quantum_synergies[:10], 1):
            combo_score = float(combo.get("score", 0.0) or 0.0)
            combo_items = combo.get("items", []) or []
            components = combo.get("components", {}) or {}
            frequencies = combo.get("frequencies", []) or []
            category = combo.get("category", "unknown")  # NEU: primary oder secondary
            scan_overlap = combo.get("scan_overlap", 0)  # NEU: Anzahl Items aus Scan
            
            # Color based on score
            if combo_score >= 8.5:
                color = "#28a745"
                priority = "Sehr hoch"
            elif combo_score >= 7.5:
                color = "#17a2b8"
                priority = "Hoch"
            else:
                color = "#ffc107"
                priority = "Mittel"
            
            # Kategorie-Badge
            if category == "primary":
                category_badge = f"<span style='background:#4CAF50;color:white;padding:3px 8px;border-radius:10px;font-size:10px;margin-left:8px;'>✓ {scan_overlap} aus Scan</span>"
            else:
                category_badge = "<span style='background:#9E9E9E;color:white;padding:3px 8px;border-radius:10px;font-size:10px;margin-left:8px;'>⊕ Fokus-Synergie</span>"
            
            html_lines.append(
                f"<div style='background:#fff;border:1px solid #e2e8f0;border-left:4px solid {color};"
                "padding:16px;margin:16px 0;border-radius:4px;'>"
            )
            html_lines.append(
                f"<h3 style='margin-top:0;color:{color};'>#{idx} – Synergy-Score {combo_score:.2f}/10.0 "
                f"<span style='font-size:12px;color:#555;'>({priority})</span>{category_badge}</h3>"
            )
            
            # Dedupliziere gleiche Substanzen, fasse Gruppen zusammen
            dedup = {}
            for item in combo_items:
                try:
                    lbl = str(item.get("label", "") or "").strip()
                except Exception:
                    continue
                if not lbl:
                    continue
                grp_raw = str(item.get("group", "") or "")
                entry = dedup.get(lbl)
                if entry is None:
                    entry = {"groups": [], "groups_set": set()}
                    dedup[lbl] = entry
                gset = entry["groups_set"]
                glst = entry["groups"]
                if grp_raw and grp_raw not in gset:
                    gset.add(grp_raw)
                    glst.append(grp_raw)
            
            html_lines.append("<p><strong>Kombination (Substanzen, gruppenübergreifend):</strong></p><ul>")
            for item in combo_items:
                try:
                    lbl = str(item.get("label", "") or "").strip()
                except Exception:
                    continue
                if not lbl:
                    continue
                    
                in_scan = item.get("in_scan", False)  # NEU: Prüfe ob aus Scan
                scan_marker = "<span style='color:#4CAF50;font-weight:600;'>✓</span> " if in_scan else ""
                
                grp_raw = str(item.get("group", "") or "")
                if grp_raw:
                    groups_fmt = grp_raw.replace("_", " ").title()
                else:
                    groups_fmt = "Gruppe unbekannt"
                    
                html_lines.append(
                    f"<li>{scan_marker}{lbl} <span style='color:#777;font-size:11px;'>[{groups_fmt}]</span></li>"
                )
            html_lines.append("</ul>")
            
            # Komponenten-Tabelle
            ind_score = float(components.get("individual_scores", 0.0) or 0.0)
            res_score = float(components.get("resonance", 0.0) or 0.0)
            har_score = float(components.get("harmony", 0.0) or 0.0)
            rel_score = float(components.get("relevance", 0.0) or 0.0)
            
            html_lines.append(
                "<table style='width:100%;border-collapse:collapse;margin:10px 0;font-size:12px;'>"
                "<tr><th style='text-align:left;background:#f1f5f9;'>Komponente</th><th style='background:#f1f5f9;'>Score</th>"
                "<th style='text-align:left;background:#f1f5f9;'>Bedeutung</th></tr>"
            )
            html_lines.append(
                f"<tr><td>Einzelwirkungen</td><td>{ind_score:.2f}/10.0</td>"
                "<td style='font-size:11px;'>Durchschnitt der beteiligten Items</td></tr>"
            )
            html_lines.append(
                f"<tr><td>Resonanz-Verstärkung</td><td>{res_score:.2f}/10.0</td>"
                "<td style='font-size:11px;'>Bruce-Copen Resonanzüberlagerung</td></tr>"
            )
            html_lines.append(
                f"<tr><td>Frequenz-Harmonien</td><td>{har_score:.2f}/10.0</td>"
                "<td style='font-size:11px;'>Phi/Oktaven/Schumann-Bezug</td></tr>"
            )
            html_lines.append(
                f"<tr><td>Fokus-Relevanz</td><td>{rel_score:.2f}/10.0</td>"
                f"<td style='font-size:11px;'>Semantische Nähe zum Fokus '{focus or '-'}'</td></tr>"
            )
            html_lines.append("</table>")
            
            # Frequenzen pro Substanz
            if frequencies:
                freq_map = {}
                for item, freq in zip(combo_items, frequencies):
                    try:
                        lbl = str(item.get("label", "") or "").strip()
                        fval = float(freq)
                    except Exception:
                        continue
                    if not lbl:
                        continue
                    freq_map.setdefault(lbl, []).append(fval)
                
                html_lines.append("<p><strong>Frequenzen (pro Substanz):</strong></p>")
                html_lines.append(
                    "<table style='width:100%;border-collapse:collapse;font-size:11px;'>"
                    "<tr><th style='text-align:left;background:#f9fafb;'>Substanz</th>"
                    "<th style='background:#f9fafb;'>Frequenz (Hz)</th></tr>"
                )
                
                for lbl, vals in freq_map.items():
                    if not vals:
                        freq_str = "-"
                    elif len(vals) == 1:
                        freq_str = f"{vals[0]:.2f}"
                    else:
                        f_min = min(vals)
                        f_max = max(vals)
                        f_avg = sum(vals) / len(vals)
                        freq_str = f"{f_min:.2f}–{f_max:.2f} (Ø {f_avg:.2f})"
                    html_lines.append(f"<tr><td>{lbl}</td><td>{freq_str}</td></tr>")
                
                html_lines.append("</table>")
            
            # Interpretation
            if res_score >= 8.5:
                base_interpret = "Sehr starke Resonanzüberlagerung – simultane Behandlung empfohlen."
            elif res_score >= 7.0:
                base_interpret = "Gute Synergien – Kombination priorisieren."
            else:
                base_interpret = "Moderate Synergien – nach klinischer Relevanz auswählen."
            
            html_lines.append(f"<p style='font-size:11px;color:#555;font-style:italic;'><strong>Interpretation:</strong> {base_interpret}</p>")
            html_lines.append("</div>")
    else:
        # Keine Quantum-Synergien gefunden
        html_lines.append("<div style='background:#fff3cd;border:1px solid #ffc107;padding:20px;margin:20px 0;border-radius:8px;'>")
        html_lines.append("<p style='margin:0;color:#856404;'><strong>ℹ️ Hinweis:</strong> Keine Quantum-Synergien gefunden. Mögliche Gründe:</p>")
        html_lines.append("<ul style='color:#856404;margin:10px 0;'>")
        html_lines.append("<li>Keine ausreichenden Resonanz-Überlappungen im Scan-Ergebnis vorhanden</li>")
        html_lines.append("<li>Das gewählte Profil hatte zu wenige hochresonante Items</li>")
        html_lines.append("<li>Die gefundenen Items zeigten keine signifikanten Frequenz-Harmonien</li>")
        html_lines.append("</ul>")
        html_lines.append("<p style='margin:0;color:#856404;'><strong>Empfehlung:</strong> Prüfen Sie den separaten <strong>Remedy-Report</strong> für 2er-Kombinationen mit detaillierten Raten-Analysen.</p>")
        html_lines.append("</div>")
    
    # Footer
    html_lines.append("<div class='footer'>")
    html_lines.append(f"<p>Generiert am {datetime.now().strftime('%d.%m.%Y %H:%M:%S')} | Morphic Engine Synergy Consolidator</p>")
    html_lines.append("</div>")
    
    html_lines.append("</div></body></html>")
    
    # Schreibe HTML
    with open(html_path, "w", encoding="utf-8") as f:
        f.write("\n".join(html_lines))
    
    print(f"\n✅ Single-Synergy Bericht gespeichert: {html_path}")
    
    return {
        "html": html_path,
        "profile": profile,
        "remedy_count": len(remedy_synergies),
        "quantum_count": len(quantum_synergies),
    }


def main():
    """CLI-Einstiegspunkt."""
    parser = argparse.ArgumentParser(
        description="Konsolidiert Synergy-Daten aus mehreren Scan-Berichten"
    )
    parser.add_argument("last_name", help="Nachname des Klienten")
    parser.add_argument("first_name", help="Vorname des Klienten")
    parser.add_argument("--birth-date", "-d", default="", help="Geburtsdatum")
    parser.add_argument("--birth-place", "-p", default="", help="Geburtsort")
    parser.add_argument("--hours", type=int, default=24, help="Zeitraum in Stunden (Standard: 24)")
    parser.add_argument("--single", action="store_true", help="Erstelle Bericht für Single-Scan")
    
    args = parser.parse_args()
    
    # Single-Scan Modus
    if args.single:
        result = create_single_scan_synergy_report(
            last_name=args.last_name,
            first_name=args.first_name
        )
    else:
        # Multi-Scan Konsolidierung
        result = consolidate_client_synergies(
            last_name=args.last_name,
            first_name=args.first_name,
            birth_date=args.birth_date,
            birth_place=args.birth_place,
            hours=args.hours
        )
    
    if result:
        print(f"\n📂 Öffne Bericht: {result['html']}")
    else:
        print("\n❌ Konsolidierung fehlgeschlagen")
        exit(1)


if __name__ == "__main__":
    main()
