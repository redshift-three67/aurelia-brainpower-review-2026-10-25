"""
3D-Viewer Integration für Morphic Engine V1

Ermöglicht 3D-Visualisierung von Scan-Ergebnissen:
- Export für Z-Anatomy (WebGL)
- Koordinaten-Mapping auf 3D-Körpermodell
- Farbcodierung nach Score/Priorität
- HTML-basierter interaktiver Viewer
"""

import json
import math
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass


@dataclass
class Point3D:
    """3D-Koordinate mit Metadaten"""
    x: float
    y: float
    z: float
    label: str
    score: float
    group: str
    color: str
    radius: float


# Basis-Koordinaten für Körperregionen (normalisiert 0-100)
BODY_REGION_COORDS: Dict[str, Tuple[float, float, float]] = {
    # Kopf
    "kopf": (50, 95, 50),
    "gehirn": (50, 95, 50),
    "stirn": (50, 98, 60),
    "schläfe": (40, 95, 55),
    "hinterkopf": (50, 92, 40),
    
    # Gesicht
    "auge": (45, 93, 60),
    "nase": (50, 90, 65),
    "mund": (50, 87, 62),
    "ohr": (35, 92, 50),
    "kiefer": (50, 85, 55),
    "zahn": (50, 86, 58),
    
    # Hals
    "hals": (50, 80, 50),
    "kehlkopf": (50, 80, 55),
    "schilddrüse": (50, 78, 55),
    
    # Thorax
    "lunge": (45, 68, 50),
    "herz": (55, 70, 55),
    "brust": (50, 70, 55),
    "bronchien": (50, 72, 50),
    "thymus": (50, 75, 55),
    
    # Abdomen
    "magen": (55, 58, 55),
    "leber": (60, 60, 50),
    "galle": (62, 58, 48),
    "pankreas": (48, 56, 45),
    "milz": (38, 58, 45),
    "darm": (50, 45, 50),
    "dickdarm": (50, 48, 50),
    "dünndarm": (50, 42, 50),
    "niere": (45, 52, 35),
    "nebenniere": (45, 55, 38),
    "blase": (50, 30, 55),
    
    # Wirbelsäule
    "hws": (50, 80, 40),
    "bws": (50, 65, 40),
    "lws": (50, 50, 40),
    "sakrum": (50, 35, 40),
    "steißbein": (50, 30, 40),
    
    # Extremitäten
    "schulter": (35, 75, 50),
    "oberarm": (25, 65, 50),
    "ellenbogen": (20, 55, 50),
    "unterarm": (18, 45, 50),
    "hand": (15, 35, 50),
    "hüfte": (42, 38, 50),
    "oberschenkel": (42, 28, 50),
    "knie": (42, 18, 50),
    "unterschenkel": (42, 10, 50),
    "fuß": (42, 2, 50),
    
    # Chakren
    "wurzel": (50, 28, 50),
    "sakral": (50, 35, 55),
    "solar": (50, 50, 55),
    "herz_chakra": (50, 68, 55),
    "hals_chakra": (50, 80, 55),
    "stirn_chakra": (50, 95, 60),
    "krone": (50, 100, 50),
    
    # Meridiane (vereinfacht)
    "meridian_lunge": (30, 60, 50),
    "meridian_dickdarm": (30, 50, 50),
    "meridian_magen": (55, 55, 55),
    "meridian_milz": (38, 55, 55),
    "meridian_herz": (55, 68, 55),
    "meridian_dünndarm": (28, 55, 50),
    "meridian_blase": (50, 50, 35),
    "meridian_niere": (45, 50, 40),
    "meridian_perikard": (52, 65, 55),
    "meridian_dreifach": (35, 65, 50),
    "meridian_gallenblase": (40, 60, 45),
    "meridian_leber": (58, 58, 50),
}


def score_to_color(score: float) -> str:
    """
    Konvertiert Score zu Farbe (Grün→Gelb→Rot).
    
    Args:
        score: Score-Wert (0.0 - 1.0)
    
    Returns:
        Hex-Farbcode
    """
    # Normalisiere auf 0-1
    s = min(1.0, max(0.0, score))
    
    if s < 0.3:
        # Grün (niedriger Score = gut)
        return "#00FF00"
    elif s < 0.5:
        # Grün zu Gelb
        r = int(255 * (s - 0.3) / 0.2)
        return f"#{r:02X}FF00"
    elif s < 0.7:
        # Gelb zu Orange
        g = int(255 - 128 * (s - 0.5) / 0.2)
        return f"#FF{g:02X}00"
    else:
        # Orange zu Rot
        g = int(127 - 127 * (s - 0.7) / 0.3)
        return f"#FF{g:02X}00"


def map_item_to_3d(item: Dict) -> Optional[Point3D]:
    """
    Mappt Scan-Item auf 3D-Koordinaten.
    
    Args:
        item: Scan-Item mit label, score, group
    
    Returns:
        Point3D oder None wenn kein Mapping möglich
    """
    label = item.get('label', '').lower()
    score = item.get('score', 0.0)
    group = item.get('group', '')
    
    # Finde passende Region
    coords = None
    matched_region = None
    
    # Exakte Übereinstimmung
    for region, coord in BODY_REGION_COORDS.items():
        if region in label:
            coords = coord
            matched_region = region
            break
    
    # Fallback: Gruppen-basiert
    if not coords:
        group_lower = group.lower()
        for region, coord in BODY_REGION_COORDS.items():
            if region in group_lower:
                coords = coord
                matched_region = region
                break
    
    if not coords:
        return None
    
    # Leichte Variation für gleiche Region
    import random
    variation = random.uniform(-2, 2)
    
    return Point3D(
        x=coords[0] + variation,
        y=coords[1] + variation,
        z=coords[2] + variation,
        label=item.get('label', ''),
        score=score,
        group=group,
        color=score_to_color(score),
        radius=0.5 + score * 1.5  # Größer bei höherem Score
    )


def export_to_viewer_json(items: List[Dict], output_path: str) -> Dict:
    """
    Exportiert Items als JSON für 3D-Viewer.
    
    Args:
        items: Liste von Scan-Items
        output_path: Ausgabe-Pfad für JSON
    
    Returns:
        Export-Statistik
    """
    points = []
    unmapped = []
    
    for item in items:
        point = map_item_to_3d(item)
        if point:
            points.append({
                "x": point.x,
                "y": point.y,
                "z": point.z,
                "label": point.label,
                "score": point.score,
                "group": point.group,
                "color": point.color,
                "radius": point.radius
            })
        else:
            unmapped.append(item.get('label', ''))
    
    export_data = {
        "version": "1.0",
        "point_count": len(points),
        "points": points,
        "unmapped_items": unmapped[:20]
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)
    
    return {
        "exported": len(points),
        "unmapped": len(unmapped),
        "output": output_path
    }


def generate_html_viewer(items: List[Dict], output_path: str) -> str:
    """
    Generiert eigenständigen HTML-3D-Viewer.
    
    Args:
        items: Liste von Scan-Items
        output_path: Ausgabe-Pfad für HTML
    
    Returns:
        Pfad zur generierten HTML-Datei
    """
    points = []
    for item in items:
        point = map_item_to_3d(item)
        if point:
            points.append({
                "x": point.x,
                "y": point.y,
                "z": point.z,
                "label": point.label,
                "score": round(point.score, 3),
                "color": point.color,
                "radius": point.radius
            })
    
    points_json = json.dumps(points, ensure_ascii=False)

    html_content = f'''<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <title>Morphic Engine - Offline Viewer</title>
    <style>
        html, body {{ margin: 0; width: 100%; height: 100%; overflow: hidden; font-family: Arial, sans-serif; background: #05070b; color: #eee; }}
        canvas {{ display: block; width: 100vw; height: 100vh; }}
        #info {{ position: absolute; top: 10px; left: 10px; background: rgba(0,0,0,0.72); padding: 15px; border-radius: 8px; }}
        #legend {{ position: absolute; bottom: 10px; left: 10px; background: rgba(0,0,0,0.72); padding: 15px; border-radius: 8px; }}
        .legend-item {{ display: flex; align-items: center; margin: 5px 0; }}
        .legend-color {{ width: 20px; height: 20px; border-radius: 50%; margin-right: 10px; }}
        #tooltip {{ position: absolute; background: rgba(0,0,0,0.9); padding: 10px; border-radius: 5px; display: none; pointer-events: none; }}
    </style>
</head>
<body>
    <canvas id="viewer"></canvas>
    <div id="info">
        <h3>Morphic Engine Offline Viewer</h3>
        <p>Punkte: <span id="point-count">{len(points)}</span></p>
        <p>Offlinefaehige Canvas-Ansicht</p>
    </div>
    <div id="legend">
        <div class="legend-item"><div class="legend-color" style="background:#00FF00"></div>Niedrig (0-30%)</div>
        <div class="legend-item"><div class="legend-color" style="background:#FFFF00"></div>Mittel (30-50%)</div>
        <div class="legend-item"><div class="legend-color" style="background:#FFA500"></div>Erhöht (50-70%)</div>
        <div class="legend-item"><div class="legend-color" style="background:#FF0000"></div>Hoch (70-100%)</div>
    </div>
    <div id="tooltip"></div>
    
    <script>
        const points = {points_json};
        const canvas = document.getElementById('viewer');
        const ctx = canvas.getContext('2d');
        const tooltip = document.getElementById('tooltip');
        let angle = 0;
        let mouse = {{ x: -9999, y: -9999 }};
        let projected = [];

        function resize() {{
            const ratio = window.devicePixelRatio || 1;
            canvas.width = Math.floor(window.innerWidth * ratio);
            canvas.height = Math.floor(window.innerHeight * ratio);
            ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
        }}

        function project(p) {{
            const nx = (Number(p.x) - 50) / 50;
            const ny = (Number(p.y) - 50) / 50;
            const nz = (Number(p.z) - 50) / 50;
            const cos = Math.cos(angle);
            const sin = Math.sin(angle);
            const x = nx * cos - nz * sin;
            const z = nx * sin + nz * cos;
            const depth = 2.8 + z;
            const scale = Math.min(window.innerWidth, window.innerHeight) * 0.34;
            return {{
                data: p,
                x: window.innerWidth / 2 + (x / depth) * scale,
                y: window.innerHeight / 2 - (ny / depth) * scale,
                z,
                radius: Math.max(4, Number(p.radius || 5) * 3),
            }};
        }}

        function drawReference() {{
            const cx = window.innerWidth / 2;
            const cy = window.innerHeight / 2;
            ctx.strokeStyle = 'rgba(140,220,210,0.16)';
            ctx.beginPath();
            ctx.ellipse(cx, cy - 100, 42, 54, 0, 0, Math.PI * 2);
            ctx.moveTo(cx, cy - 46);
            ctx.lineTo(cx, cy + 150);
            ctx.moveTo(cx - 90, cy - 10);
            ctx.lineTo(cx + 90, cy - 10);
            ctx.moveTo(cx - 52, cy + 150);
            ctx.lineTo(cx - 30, cy + 238);
            ctx.moveTo(cx + 52, cy + 150);
            ctx.lineTo(cx + 30, cy + 238);
            ctx.stroke();
        }}

        function updateTooltip() {{
            const hit = [...projected].reverse().find(item => {{
                const dx = item.x - mouse.x;
                const dy = item.y - mouse.y;
                return Math.sqrt(dx * dx + dy * dy) <= item.radius + 5;
            }});
            if (hit) {{
                const p = hit.data;
                tooltip.innerHTML = `<strong>${{p.label}}</strong><br>Score: ${{Number(p.score || 0).toFixed(3)}}`;
                tooltip.style.left = mouse.x + 15 + 'px';
                tooltip.style.top = mouse.y + 15 + 'px';
                tooltip.style.display = 'block';
            }} else {{
                tooltip.style.display = 'none';
            }}
        }}

        function draw() {{
            ctx.clearRect(0, 0, window.innerWidth, window.innerHeight);
            const gradient = ctx.createRadialGradient(window.innerWidth / 2, window.innerHeight / 2, 80, window.innerWidth / 2, window.innerHeight / 2, Math.max(window.innerWidth, window.innerHeight));
            gradient.addColorStop(0, '#102033');
            gradient.addColorStop(1, '#05070b');
            ctx.fillStyle = gradient;
            ctx.fillRect(0, 0, window.innerWidth, window.innerHeight);
            drawReference();
            projected = points.map(project).sort((a, b) => a.z - b.z);
            for (const item of projected) {{
                ctx.globalAlpha = 0.28;
                ctx.fillStyle = item.data.color || '#57d9ff';
                ctx.beginPath();
                ctx.arc(item.x, item.y, item.radius * 2.2, 0, Math.PI * 2);
                ctx.fill();
                ctx.globalAlpha = 0.92;
                ctx.beginPath();
                ctx.arc(item.x, item.y, item.radius, 0, Math.PI * 2);
                ctx.fill();
            }}
            ctx.globalAlpha = 1;
            updateTooltip();
            angle += 0.004;
            requestAnimationFrame(draw);
        }}

        window.addEventListener('mousemove', event => {{
            mouse = {{ x: event.clientX, y: event.clientY }};
            tooltip.style.left = event.clientX + 15 + 'px';
            tooltip.style.top = event.clientY + 15 + 'px';
        }});
        window.addEventListener('resize', () => {{
            resize();
        }});

        resize();
        draw();
    </script>
</body>
</html>'''
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return output_path


def get_body_regions() -> List[str]:
    """Gibt alle verfügbaren Körperregionen zurück."""
    return list(BODY_REGION_COORDS.keys())
