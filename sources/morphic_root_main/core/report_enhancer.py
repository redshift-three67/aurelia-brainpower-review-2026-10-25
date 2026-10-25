"""
Report Enhancer für Morphic Engine V1

Erweitert Scan-Reports um:
- Konfidenz-Bewertung (A-F Grade)
- 3D-Export-Links
- Trend-Hinweise
- Profil-Empfehlungen
"""

import json
from typing import Dict, List, Optional
from pathlib import Path

from .confidence_intervals import get_overall_scan_confidence, CONFIDENCE_GRADES
from .profile_recommender import recommend_profiles, get_best_profile
from .viewer_3d import generate_html_viewer, export_to_viewer_json
from .trend_analysis import analyze_trends


def enhance_scan_result(
    result: Dict,
    h_level: float,
    entropy_source: str,
    sample_size: int,
    group_count: int,
    focus: str = ""
) -> Dict:
    """
    Erweitert Scan-Ergebnis um Konfidenz und Empfehlungen.
    
    Args:
        result: Original Scan-Ergebnis
        h_level: Hardware H-Level
        entropy_source: Verwendete Entropie-Quelle
        sample_size: Anzahl Samples
        group_count: Anzahl gescannter Gruppen
        focus: Optionaler Fokus
    
    Returns:
        Erweitertes Ergebnis mit confidence und recommendations
    """
    # Konfidenz berechnen
    confidence = get_overall_scan_confidence(
        h_level, entropy_source, sample_size, group_count
    )
    result['confidence'] = confidence
    
    # Profil-Empfehlungen wenn Fokus vorhanden
    if focus:
        recommendations = recommend_profiles(focus, top_k=3)
        result['profile_recommendations'] = recommendations
        result['best_profile'] = get_best_profile(focus)
    
    return result


def generate_enhanced_html(
    result: Dict,
    output_path: str,
    include_3d: bool = True
) -> str:
    """
    Generiert erweitertes HTML mit Konfidenz-Badge und optionalem 3D-Link.
    
    Args:
        result: Scan-Ergebnis (mit confidence)
        output_path: Ausgabe-Pfad
        include_3d: 3D-Viewer-Link einbinden
    
    Returns:
        Pfad zur HTML-Datei
    """
    confidence = result.get('confidence', {})
    grade = confidence.get('grade', '?')
    overall = confidence.get('overall', 0)
    description = confidence.get('description', 'Unbekannt')
    factors = confidence.get('factors', {})
    
    items = result.get('top_items', [])
    profile = result.get('profile', 'unknown')
    client = result.get('client_name', 'Unbekannt')
    focus = result.get('focus', '')
    
    # Grade Farben
    grade_colors = {
        'A': '#00C853', 'B': '#64DD17', 'C': '#FFD600',
        'D': '#FF6D00', 'F': '#D50000'
    }
    grade_color = grade_colors.get(grade, '#888888')
    
    # 3D-Viewer-Link
    viewer_3d_link = ""
    if include_3d and items:
        viewer_path = output_path.replace('.html', '_3d.html')
        generate_html_viewer(items, viewer_path)
        viewer_3d_link = f'''
        <div class="action-card" onclick="window.open('{Path(viewer_path).name}', '_blank')">
            <div class="action-icon">🌐</div>
            <div class="action-title">3D-Ansicht</div>
            <div class="action-desc">Interaktive Visualisierung</div>
        </div>
        '''
    
    # Empfehlungen
    recommendations_html = ""
    if 'profile_recommendations' in result:
        recs = result['profile_recommendations']
        if recs:
            rec_items = ''.join([
                f'<li><strong>{r["profile"]}</strong> (Score: {r["score"]:.0%}) - {r.get("match_reason", "")}</li>'
                for r in recs[:3]
            ])
            recommendations_html = f'''
            <div class="section">
                <h3>🎯 Profil-Empfehlungen für "{focus}"</h3>
                <ul>{rec_items}</ul>
            </div>
            '''
    
    # Items HTML
    items_html = ""
    for i, item in enumerate(items[:20], 1):
        score = item.get('score', 0)
        score_pct = score * 100
        score_color = '#00C853' if score < 0.3 else '#FFD600' if score < 0.6 else '#FF6D00' if score < 0.8 else '#D50000'
        items_html += f'''
        <div class="item-card">
            <div class="item-rank">#{i}</div>
            <div class="item-info">
                <div class="item-label">{item.get('label', '?')}</div>
                <div class="item-group">{item.get('group', '')}</div>
            </div>
            <div class="item-score">
                <div class="score-bar">
                    <div class="score-fill" style="width:{score_pct}%; background:{score_color}"></div>
                </div>
                <span>{score_pct:.1f}%</span>
            </div>
        </div>
        '''
    
    html_content = f'''<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Morphic Engine Report - {client}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #eee;
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{ max-width: 1000px; margin: 0 auto; }}
        
        /* Header */
        .header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 20px;
            background: rgba(0,0,0,0.3);
            border-radius: 12px;
            margin-bottom: 20px;
        }}
        .header h1 {{ color: #00d4ff; font-size: 1.5em; }}
        .confidence-badge {{
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 10px 20px;
            background: rgba(255,255,255,0.1);
            border-radius: 8px;
        }}
        .grade {{
            font-size: 2em;
            font-weight: bold;
            color: {grade_color};
        }}
        .grade-info {{
            text-align: right;
        }}
        .grade-percent {{ font-size: 1.2em; color: {grade_color}; }}
        .grade-desc {{ font-size: 0.85em; color: #888; }}
        
        /* Info Grid */
        .info-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }}
        .info-card {{
            background: rgba(255,255,255,0.05);
            padding: 15px;
            border-radius: 8px;
            border-left: 3px solid #00d4ff;
        }}
        .info-label {{ font-size: 0.8em; color: #888; margin-bottom: 5px; }}
        .info-value {{ font-size: 1.1em; color: #fff; }}
        
        /* Actions */
        .actions {{
            display: flex;
            gap: 15px;
            margin-bottom: 20px;
        }}
        .action-card {{
            flex: 1;
            background: rgba(0,100,200,0.2);
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            cursor: pointer;
            transition: transform 0.2s, background 0.2s;
        }}
        .action-card:hover {{ transform: scale(1.02); background: rgba(0,100,200,0.3); }}
        .action-icon {{ font-size: 2em; margin-bottom: 5px; }}
        .action-title {{ font-weight: bold; color: #00d4ff; }}
        .action-desc {{ font-size: 0.8em; color: #888; }}
        
        /* Section */
        .section {{
            background: rgba(0,0,0,0.2);
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 20px;
        }}
        .section h3 {{ color: #00d4ff; margin-bottom: 15px; }}
        .section ul {{ margin-left: 20px; }}
        .section li {{ margin: 8px 0; }}
        
        /* Items */
        .items {{ margin-top: 20px; }}
        .item-card {{
            display: flex;
            align-items: center;
            padding: 12px 15px;
            background: rgba(255,255,255,0.03);
            border-radius: 8px;
            margin-bottom: 8px;
            transition: background 0.2s;
        }}
        .item-card:hover {{ background: rgba(255,255,255,0.08); }}
        .item-rank {{
            font-size: 1.2em;
            font-weight: bold;
            color: #00d4ff;
            width: 50px;
        }}
        .item-info {{ flex: 1; }}
        .item-label {{ font-weight: 500; }}
        .item-group {{ font-size: 0.8em; color: #888; }}
        .item-score {{
            display: flex;
            align-items: center;
            gap: 10px;
            width: 150px;
        }}
        .score-bar {{
            flex: 1;
            height: 8px;
            background: rgba(255,255,255,0.1);
            border-radius: 4px;
            overflow: hidden;
        }}
        .score-fill {{
            height: 100%;
            border-radius: 4px;
            transition: width 0.3s;
        }}
        
        /* Factors */
        .factors {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
            margin-top: 15px;
        }}
        .factor {{
            display: flex;
            justify-content: space-between;
            padding: 8px 12px;
            background: rgba(255,255,255,0.05);
            border-radius: 5px;
        }}
        .factor-name {{ color: #888; }}
        .factor-value {{ color: #00d4ff; }}
        
        /* Footer */
        .footer {{
            text-align: center;
            padding: 20px;
            color: #555;
            font-size: 0.85em;
        }}
        
        /* ===== PRINT / PDF STYLESHEET ===== */
        @media print {{
            body {{ 
                background: #f8f9fa !important;
                color: #2c3e50 !important;
                padding: 10px !important;
            }}
            .container {{ max-width: 100% !important; }}
            .header {{
                background: #4a6278 !important;
                color: white !important;
                -webkit-print-color-adjust: exact !important;
                print-color-adjust: exact !important;
            }}
            .header h1 {{ color: white !important; }}
            .confidence-badge {{
                background: rgba(255,255,255,0.2) !important;
            }}
            .info-card {{
                background: #e8f4f8 !important;
                color: #2c3e50 !important;
                border-left-color: #5a7a9a !important;
            }}
            .info-label {{ color: #5d6d7e !important; }}
            .info-value {{ color: #2c3e50 !important; }}
            .actions {{ display: none !important; }}
            .section {{
                background: #ffffff !important;
                border: 1px solid #d1d5db !important;
                color: #2c3e50 !important;
            }}
            .section h3 {{ color: #4a6278 !important; }}
            .item-card {{
                background: #f8f9fa !important;
                color: #2c3e50 !important;
            }}
            .item-rank {{ color: #4a6278 !important; }}
            .item-label {{ color: #1a252f !important; }}
            .item-group {{ color: #5d6d7e !important; }}
            .score-bar {{ background: #d1d5db !important; }}
            .factor {{
                background: #e8f4f8 !important;
            }}
            .factor-name {{ color: #5d6d7e !important; }}
            .factor-value {{ color: #2c3e50 !important; }}
            .footer {{ color: #5d6d7e !important; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div>
                <h1>🔬 Morphic Engine Report</h1>
                <span style="color:#888">{profile}</span>
            </div>
            <div class="confidence-badge">
                <div class="grade">{grade}</div>
                <div class="grade-info">
                    <div class="grade-percent">{overall:.0%}</div>
                    <div class="grade-desc">{description}</div>
                </div>
            </div>
        </div>
        
        <div class="info-grid">
            <div class="info-card">
                <div class="info-label">Klient</div>
                <div class="info-value">{client}</div>
            </div>
            <div class="info-card">
                <div class="info-label">Fokus</div>
                <div class="info-value">{focus or '(keiner)'}</div>
            </div>
            <div class="info-card">
                <div class="info-label">Profil</div>
                <div class="info-value">{profile}</div>
            </div>
            <div class="info-card">
                <div class="info-label">Befunde</div>
                <div class="info-value">{len(items)}</div>
            </div>
        </div>
        
        <div class="actions">
            <div class="action-card" onclick="window.print()">
                <div class="action-icon">🖨️</div>
                <div class="action-title">Drucken</div>
                <div class="action-desc">Report ausdrucken</div>
            </div>
            {viewer_3d_link}
            <div class="action-card" onclick="downloadJSON()">
                <div class="action-icon">📥</div>
                <div class="action-title">Export</div>
                <div class="action-desc">JSON herunterladen</div>
            </div>
        </div>
        
        <div class="section">
            <h3>📊 Konfidenz-Faktoren</h3>
            <div class="factors">
                {''.join([f'<div class="factor"><span class="factor-name">{k}</span><span class="factor-value">{v}</span></div>' for k, v in factors.items()])}
            </div>
        </div>
        
        {recommendations_html}
        
        <div class="section">
            <h3>🔍 Top Befunde</h3>
            <div class="items">
                {items_html}
            </div>
        </div>
        
        <div class="footer">
            Morphic Engine V1 • Generiert am {__import__('datetime').datetime.now().strftime('%d.%m.%Y %H:%M')}
        </div>
    </div>
    
    <script>
        function downloadJSON() {{
            const data = {json.dumps(result, indent=2, ensure_ascii=False)};
            const blob = new Blob([JSON.stringify(data, null, 2)], {{type: 'application/json'}});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'scan_result.json';
            a.click();
        }}
    </script>
</body>
</html>'''
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return output_path


def add_confidence_to_json(json_path: str) -> Dict:
    """
    Fügt Konfidenz zu bestehender JSON-Datei hinzu.
    
    Args:
        json_path: Pfad zur JSON-Datei
    
    Returns:
        Aktualisierte Daten
    """
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Extrahiere Parameter
    h_level = data.get('h_level', 0.1)
    entropy_source = data.get('entropy_source', 'network')
    items = data.get('top_items', [])
    groups = data.get('groups_scanned', [])
    focus = data.get('focus', '')
    
    # Konfidenz berechnen
    confidence = get_overall_scan_confidence(
        h_level, entropy_source, len(items), len(groups)
    )
    data['confidence'] = confidence
    
    # Speichern
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    return data
