"""
Z-Anatomy Bridge für Morphic Engine V1

Integration mit Z-Anatomy (Open-Source 3D-Anatomie-Viewer):
https://www.z-anatomy.com/

Features:
- Export zu Z-Anatomy-kompatiblen Formaten
- Mapping von Scan-Items auf anatomische Strukturen
- Generierung von Overlay-Layern für Scan-Ergebnisse
- Standalone HTML-Viewer mit eingebettetem Z-Anatomy
"""

import json
import os
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

# Z-Anatomy verwendet spezifische anatomische Terminologie (FMA - Foundational Model of Anatomy)
# Mapping von deutschen Labels auf FMA-IDs

FMA_MAPPING: Dict[str, Dict[str, any]] = {
    # Kopf/Gehirn
    "gehirn": {"fma_id": "FMA50801", "z_name": "Brain", "layer": "nervous"},
    "großhirn": {"fma_id": "FMA61817", "z_name": "Cerebrum", "layer": "nervous"},
    "kleinhirn": {"fma_id": "FMA67944", "z_name": "Cerebellum", "layer": "nervous"},
    "hirnstamm": {"fma_id": "FMA79876", "z_name": "Brainstem", "layer": "nervous"},
    "hypophyse": {"fma_id": "FMA13889", "z_name": "Pituitary gland", "layer": "endocrine"},
    "hypothalamus": {"fma_id": "FMA62008", "z_name": "Hypothalamus", "layer": "nervous"},
    "thalamus": {"fma_id": "FMA62007", "z_name": "Thalamus", "layer": "nervous"},
    "amygdala": {"fma_id": "FMA61841", "z_name": "Amygdala", "layer": "nervous"},
    "hippocampus": {"fma_id": "FMA275020", "z_name": "Hippocampus", "layer": "nervous"},
    
    # Sinnesorgane
    "auge": {"fma_id": "FMA54448", "z_name": "Eye", "layer": "sensory"},
    "ohr": {"fma_id": "FMA52780", "z_name": "Ear", "layer": "sensory"},
    "nase": {"fma_id": "FMA46472", "z_name": "Nose", "layer": "respiratory"},
    
    # Herz-Kreislauf
    "herz": {"fma_id": "FMA7088", "z_name": "Heart", "layer": "cardiovascular"},
    "aorta": {"fma_id": "FMA3734", "z_name": "Aorta", "layer": "cardiovascular"},
    "vena_cava": {"fma_id": "FMA4720", "z_name": "Vena cava", "layer": "cardiovascular"},
    
    # Respiratorisch
    "lunge": {"fma_id": "FMA7195", "z_name": "Lung", "layer": "respiratory"},
    "bronchien": {"fma_id": "FMA7409", "z_name": "Bronchus", "layer": "respiratory"},
    "trachea": {"fma_id": "FMA7394", "z_name": "Trachea", "layer": "respiratory"},
    "zwerchfell": {"fma_id": "FMA13295", "z_name": "Diaphragm", "layer": "muscular"},
    
    # Verdauung
    "magen": {"fma_id": "FMA7148", "z_name": "Stomach", "layer": "digestive"},
    "leber": {"fma_id": "FMA7197", "z_name": "Liver", "layer": "digestive"},
    "gallenblase": {"fma_id": "FMA7202", "z_name": "Gallbladder", "layer": "digestive"},
    "pankreas": {"fma_id": "FMA7198", "z_name": "Pancreas", "layer": "digestive"},
    "milz": {"fma_id": "FMA7196", "z_name": "Spleen", "layer": "lymphatic"},
    "dünndarm": {"fma_id": "FMA7200", "z_name": "Small intestine", "layer": "digestive"},
    "dickdarm": {"fma_id": "FMA7201", "z_name": "Large intestine", "layer": "digestive"},
    "blinddarm": {"fma_id": "FMA14541", "z_name": "Appendix", "layer": "digestive"},
    
    # Urogenital
    "niere": {"fma_id": "FMA7203", "z_name": "Kidney", "layer": "urinary"},
    "nebenniere": {"fma_id": "FMA9604", "z_name": "Adrenal gland", "layer": "endocrine"},
    "blase": {"fma_id": "FMA15900", "z_name": "Urinary bladder", "layer": "urinary"},
    "prostata": {"fma_id": "FMA9600", "z_name": "Prostate", "layer": "reproductive"},
    "uterus": {"fma_id": "FMA17558", "z_name": "Uterus", "layer": "reproductive"},
    "ovar": {"fma_id": "FMA7209", "z_name": "Ovary", "layer": "reproductive"},
    
    # Endokrin
    "schilddrüse": {"fma_id": "FMA9603", "z_name": "Thyroid gland", "layer": "endocrine"},
    "thymus": {"fma_id": "FMA9607", "z_name": "Thymus", "layer": "lymphatic"},
    "epiphyse": {"fma_id": "FMA62033", "z_name": "Pineal gland", "layer": "endocrine"},
    
    # Muskuloskelettal
    "wirbelsäule": {"fma_id": "FMA13478", "z_name": "Vertebral column", "layer": "skeletal"},
    "hws": {"fma_id": "FMA72063", "z_name": "Cervical vertebrae", "layer": "skeletal"},
    "bws": {"fma_id": "FMA72064", "z_name": "Thoracic vertebrae", "layer": "skeletal"},
    "lws": {"fma_id": "FMA72065", "z_name": "Lumbar vertebrae", "layer": "skeletal"},
    "sakrum": {"fma_id": "FMA16202", "z_name": "Sacrum", "layer": "skeletal"},
    "becken": {"fma_id": "FMA9578", "z_name": "Pelvis", "layer": "skeletal"},
    "schulter": {"fma_id": "FMA25202", "z_name": "Shoulder", "layer": "skeletal"},
    "ellenbogen": {"fma_id": "FMA24890", "z_name": "Elbow", "layer": "skeletal"},
    "handgelenk": {"fma_id": "FMA24920", "z_name": "Wrist", "layer": "skeletal"},
    "hüfte": {"fma_id": "FMA35178", "z_name": "Hip", "layer": "skeletal"},
    "knie": {"fma_id": "FMA24974", "z_name": "Knee", "layer": "skeletal"},
    "sprunggelenk": {"fma_id": "FMA9665", "z_name": "Ankle", "layer": "skeletal"},
    
    # Zähne/Kiefer
    "kiefer": {"fma_id": "FMA52748", "z_name": "Jaw", "layer": "skeletal"},
    "oberkiefer": {"fma_id": "FMA9711", "z_name": "Maxilla", "layer": "skeletal"},
    "unterkiefer": {"fma_id": "FMA52748", "z_name": "Mandible", "layer": "skeletal"},
    "kiefergelenk": {"fma_id": "FMA54832", "z_name": "TMJ", "layer": "skeletal"},
}

# Layer-Farben für Z-Anatomy
LAYER_COLORS: Dict[str, str] = {
    "nervous": "#FFD700",      # Gold
    "cardiovascular": "#FF4444",  # Rot
    "respiratory": "#87CEEB",  # Hellblau
    "digestive": "#98FB98",    # Hellgrün
    "urinary": "#DDA0DD",      # Pflaume
    "endocrine": "#FF69B4",    # Pink
    "lymphatic": "#90EE90",    # Grün
    "muscular": "#CD853F",     # Peru
    "skeletal": "#F5F5DC",     # Beige
    "reproductive": "#FFB6C1", # Hellpink
    "sensory": "#9370DB",      # Mittel-Lila
}


@dataclass
class ZAnatomyMarker:
    """Marker für Z-Anatomy Overlay"""
    fma_id: str
    z_name: str
    layer: str
    score: float
    color: str
    label: str
    group: str


def map_item_to_fma(item: Dict) -> Optional[ZAnatomyMarker]:
    """
    Mappt Scan-Item auf FMA-Anatomie-ID.
    
    Args:
        item: Scan-Item mit label, score, group
    
    Returns:
        ZAnatomyMarker oder None
    """
    label = item.get('label', '').lower()
    score = item.get('score', 0.0)
    group = item.get('group', '')
    
    # Suche nach Übereinstimmung
    for key, mapping in FMA_MAPPING.items():
        if key in label:
            # Score-basierte Farbintensität
            base_color = LAYER_COLORS.get(mapping['layer'], '#FFFFFF')
            intensity_color = _adjust_color_intensity(base_color, score)
            
            return ZAnatomyMarker(
                fma_id=mapping['fma_id'],
                z_name=mapping['z_name'],
                layer=mapping['layer'],
                score=score,
                color=intensity_color,
                label=item.get('label', ''),
                group=group
            )
    
    return None


def _adjust_color_intensity(hex_color: str, intensity: float) -> str:
    """Passt Farbintensität basierend auf Score an."""
    # Parse Hex
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    
    # Intensität anpassen (höherer Score = sattere Farbe)
    factor = 0.3 + (intensity * 0.7)
    r = int(r * factor)
    g = int(g * factor)
    b = int(b * factor)
    
    return f"#{r:02X}{g:02X}{b:02X}"


def export_z_anatomy_overlay(items: List[Dict], output_path: str) -> Dict:
    """
    Exportiert Scan-Items als Z-Anatomy Overlay-JSON.
    
    Args:
        items: Liste von Scan-Items
        output_path: Ausgabe-Pfad
    
    Returns:
        Export-Statistik
    """
    markers = []
    unmapped = []
    
    for item in items:
        marker = map_item_to_fma(item)
        if marker:
            markers.append({
                "fma_id": marker.fma_id,
                "z_name": marker.z_name,
                "layer": marker.layer,
                "score": marker.score,
                "color": marker.color,
                "label": marker.label,
                "group": marker.group,
                "opacity": min(1.0, 0.3 + marker.score * 0.7)
            })
        else:
            unmapped.append(item.get('label', ''))
    
    # Gruppiere nach Layer
    layers = {}
    for m in markers:
        layer = m['layer']
        if layer not in layers:
            layers[layer] = {
                "name": layer,
                "color": LAYER_COLORS.get(layer, '#FFFFFF'),
                "structures": []
            }
        layers[layer]["structures"].append(m)
    
    export_data = {
        "version": "1.0",
        "format": "z-anatomy-overlay",
        "total_markers": len(markers),
        "layers": list(layers.values()),
        "unmapped": unmapped[:20]
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)
    
    return {
        "exported": len(markers),
        "layers": len(layers),
        "unmapped": len(unmapped)
    }


def generate_z_anatomy_html(items: List[Dict], output_path: str) -> str:
    """
    Generiert HTML mit eingebettetem Z-Anatomy Viewer.
    
    Args:
        items: Liste von Scan-Items
        output_path: Ausgabe-Pfad
    
    Returns:
        Pfad zur HTML-Datei
    """
    markers = []
    for item in items:
        marker = map_item_to_fma(item)
        if marker:
            markers.append({
                "fma_id": marker.fma_id,
                "z_name": marker.z_name,
                "label": marker.label,
                "score": round(marker.score, 3),
                "color": marker.color,
                "layer": marker.layer
            })
    
    markers_json = json.dumps(markers, ensure_ascii=False)
    layers_json = json.dumps(LAYER_COLORS, ensure_ascii=False)
    
    html_content = f'''<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Morphic Engine - Z-Anatomy Viewer</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #eee;
            min-height: 100vh;
        }}
        .container {{ display: flex; height: 100vh; }}
        
        /* Sidebar */
        .sidebar {{
            width: 350px;
            background: rgba(0,0,0,0.3);
            padding: 20px;
            overflow-y: auto;
            border-right: 1px solid #333;
        }}
        .sidebar h2 {{ 
            color: #00d4ff; 
            margin-bottom: 20px;
            font-size: 1.4em;
        }}
        
        /* Layer Controls */
        .layer-control {{
            display: flex;
            align-items: center;
            padding: 8px 12px;
            margin: 5px 0;
            background: rgba(255,255,255,0.05);
            border-radius: 5px;
            cursor: pointer;
            transition: background 0.2s;
        }}
        .layer-control:hover {{ background: rgba(255,255,255,0.1); }}
        .layer-color {{
            width: 20px;
            height: 20px;
            border-radius: 50%;
            margin-right: 10px;
        }}
        .layer-checkbox {{
            margin-left: auto;
            width: 18px;
            height: 18px;
        }}
        
        /* Findings List */
        .findings {{ margin-top: 30px; }}
        .finding-item {{
            padding: 12px;
            margin: 8px 0;
            background: rgba(255,255,255,0.05);
            border-radius: 8px;
            border-left: 4px solid;
            cursor: pointer;
            transition: transform 0.2s;
        }}
        .finding-item:hover {{ transform: translateX(5px); }}
        .finding-label {{ font-weight: bold; }}
        .finding-score {{ 
            font-size: 0.85em; 
            color: #aaa;
            margin-top: 4px;
        }}
        .finding-anatomy {{
            font-size: 0.8em;
            color: #00d4ff;
            margin-top: 2px;
        }}
        
        /* Main Viewer */
        .viewer {{
            flex: 1;
            display: flex;
            flex-direction: column;
        }}
        .viewer-header {{
            padding: 15px 20px;
            background: rgba(0,0,0,0.2);
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}
        .viewer-header h1 {{
            font-size: 1.2em;
            color: #00d4ff;
        }}
        
        /* 3D Frame (Placeholder für Z-Anatomy) */
        .anatomy-frame {{
            flex: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            background: #0a0a1a;
            position: relative;
        }}
        .anatomy-placeholder {{
            text-align: center;
            padding: 40px;
            background: rgba(0,100,200,0.1);
            border-radius: 15px;
            border: 2px dashed #00d4ff;
        }}
        .anatomy-placeholder h3 {{
            color: #00d4ff;
            margin-bottom: 15px;
        }}
        .anatomy-placeholder p {{
            color: #888;
            margin: 10px 0;
        }}
        .anatomy-placeholder a {{
            color: #00d4ff;
            text-decoration: none;
        }}
        
        /* Stats Bar */
        .stats-bar {{
            padding: 10px 20px;
            background: rgba(0,0,0,0.3);
            display: flex;
            gap: 30px;
            font-size: 0.9em;
        }}
        .stat {{ color: #888; }}
        .stat strong {{ color: #00d4ff; }}
        
        /* Score Bar */
        .score-bar {{
            height: 4px;
            background: #333;
            border-radius: 2px;
            margin-top: 8px;
            overflow: hidden;
        }}
        .score-fill {{
            height: 100%;
            border-radius: 2px;
            transition: width 0.3s;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="sidebar">
            <h2>🔬 Morphic Scan Overlay</h2>
            
            <div class="layers">
                <h3 style="color:#888; font-size:0.9em; margin-bottom:10px;">LAYER KONTROLLE</h3>
                <div id="layer-controls"></div>
            </div>
            
            <div class="findings">
                <h3 style="color:#888; font-size:0.9em; margin-bottom:10px;">BEFUNDE ({len(markers)})</h3>
                <div id="findings-list"></div>
            </div>
        </div>
        
        <div class="viewer">
            <div class="viewer-header">
                <h1>Z-Anatomy Integration</h1>
                <span style="color:#888">Morphic Engine V1</span>
            </div>
            
            <div class="anatomy-frame">
                <div class="anatomy-placeholder">
                    <h3>🦴 Z-Anatomy Viewer</h3>
                    <p>Für vollständige 3D-Anatomie-Ansicht:</p>
                    <p><a href="https://www.z-anatomy.com/app" target="_blank">→ Z-Anatomy Web App öffnen</a></p>
                    <p style="margin-top:20px; font-size:0.85em;">
                        Laden Sie die Overlay-Daten in Z-Anatomy<br>
                        oder nutzen Sie den eingebauten Simple-Viewer
                    </p>
                    <button onclick="showSimpleViewer()" style="
                        margin-top:20px;
                        padding:10px 25px;
                        background:#00d4ff;
                        border:none;
                        border-radius:5px;
                        color:#000;
                        font-weight:bold;
                        cursor:pointer;
                    ">Simple 3D Viewer starten</button>
                </div>
            </div>
            
            <div class="stats-bar">
                <div class="stat">Befunde: <strong>{len(markers)}</strong></div>
                <div class="stat">Layer: <strong id="active-layers">0</strong></div>
                <div class="stat">Gemappt: <strong>{len(markers)}</strong> / {len(items)}</div>
            </div>
        </div>
    </div>
    
    <script>
        const markers = {markers_json};
        const layerColors = {layers_json};
        
        // Layer Controls erstellen
        function createLayerControls() {{
            const container = document.getElementById('layer-controls');
            const layers = [...new Set(markers.map(m => m.layer))];
            
            layers.forEach(layer => {{
                const count = markers.filter(m => m.layer === layer).length;
                const div = document.createElement('div');
                div.className = 'layer-control';
                div.innerHTML = `
                    <div class="layer-color" style="background:${{layerColors[layer] || '#fff'}}"></div>
                    <span>${{layer}} (${{count}})</span>
                    <input type="checkbox" class="layer-checkbox" checked data-layer="${{layer}}">
                `;
                container.appendChild(div);
            }});
            
            document.getElementById('active-layers').textContent = layers.length;
        }}
        
        // Findings Liste erstellen
        function createFindingsList() {{
            const container = document.getElementById('findings-list');
            
            markers.sort((a, b) => b.score - a.score).forEach(m => {{
                const div = document.createElement('div');
                div.className = 'finding-item';
                div.style.borderColor = m.color;
                div.innerHTML = `
                    <div class="finding-label">${{m.label}}</div>
                    <div class="finding-anatomy">🏷️ ${{m.z_name}} (${{m.fma_id}})</div>
                    <div class="finding-score">Score: ${{(m.score * 100).toFixed(1)}}%</div>
                    <div class="score-bar">
                        <div class="score-fill" style="width:${{m.score * 100}}%; background:${{m.color}}"></div>
                    </div>
                `;
                div.onclick = () => highlightStructure(m.fma_id);
                container.appendChild(div);
            }});
        }}
        
        function highlightStructure(fmaId) {{
            console.log('Highlight:', fmaId);
            // Z-Anatomy API call würde hier erfolgen
        }}
        
        function showSimpleViewer() {{
            // Wechsel zu eingebautem 3D-Viewer
            window.location.href = window.location.href.replace('_zanatomy.html', '_3d.html');
        }}
        
        // Init
        createLayerControls();
        createFindingsList();
    </script>
</body>
</html>'''
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return output_path


def get_supported_structures() -> List[str]:
    """Gibt alle unterstützten anatomischen Strukturen zurück."""
    return list(FMA_MAPPING.keys())


def get_fma_info(structure: str) -> Optional[Dict]:
    """Gibt FMA-Informationen für eine Struktur zurück."""
    return FMA_MAPPING.get(structure.lower())
