"""Bridging-Tools fuer NLS-3D-Exports.

Dieses Modul gehoert NICHT zum Engine-Kern, sondern dient als
Hilfs-Skript, um *_3d_scan.json-Exporte auszuwerten und fuer
Frontends (Web, Blender, Z-Anatomy) aufzubereiten.

Konventionen fuer point_id <-> 3D-Objektnamen
===========================================

Die IDs in den *_3d_scan.json-Dateien koennen 1:1 als Objektnamen
oder Empties in einem 3D-Modell (z.B. Blender) verwendet werden.

Aktuelle Punkte:

- SPINE_CERVICAL   -> Halswirbelsaeule (C0-C7), zentraler HWS-Punkt
- SPINE_THORACIC   -> Brustwirbelsaeule (Th1-Th12), zentraler BWS-Punkt
- SPINE_LUMBAR     -> Lendenwirbelsaeule (L1-L5), zentraler LWS-Punkt
- SPINE_SACRAL     -> Kreuzbein/Sakrum-Bereich

- MERIDIAN_LU      -> Lungenmeridian (LU)
- MERIDIAN_HE      -> Herzmeridian (HE)
- MERIDIAN_KI      -> Nierenmeridian (KI)
- MERIDIAN_BL      -> Blasenmeridian (BL)

- CHAKRA_ROOT      -> Wurzelchakra
- CHAKRA_SOLAR     -> Solarplexus-Chakra
- CHAKRA_HEART     -> Herzchakra
- CHAKRA_THROAT    -> Halschakra
- CHAKRA_THIRD_EYE -> Stirnchakra / Drittes Auge
- CHAKRA_CROWN     -> Kronenchakra

Ein 3D-Client kann diese IDs direkt zum Binden von Empties, Bones
oder Vertex-Gruppen verwenden. Die in nls3d_points.py hinterlegten
coords sind symbolische Defaults; ein echtes 3D-Modell kann
praezisere Koordinaten liefern.

Nutzung dieses Skripts
======================

Dieses Skript ist als einfaches Hilfstool gedacht:

- Liest eine *_3d_scan.json-Datei.
- Sortiert Punkte nach Normalisierung oder Score-Summe.
- Gibt Top-N Punkte auf der Konsole aus.
- Optional: schreibt eine CSV-Datei fuer externe Visualisierung.

Beispiel (Windows CMD):

    python -m tools.nls3d_bridge pfad\zu\DEIN_3D_SCAN.json --top-n 10 \
        --csv-output pfad\zu\DEIN_3D_SCAN_top10.csv

Das Skript ist bewusst robust gehalten: Fehler im Input fuehren zu
klaren Meldungen und Exit-Code 1, aber nicht zu unkontrollierten
Tracebacks.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any, Dict, List


def _load_3d_scan(path: Path) -> Dict[str, Any]:
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"Datei nicht gefunden oder kein regulaere Datei: {path}")
    try:
        text = path.read_text(encoding="utf-8")
    except Exception as exc:  # pragma: no cover - defensive
        raise RuntimeError(f"Datei konnte nicht gelesen werden: {exc}") from exc
    try:
        data = json.loads(text)
    except Exception as exc:  # pragma: no cover - defensive
        raise RuntimeError(f"JSON konnte nicht geparst werden: {exc}") from exc
    schema = str(data.get("schema", "") or "").strip()
    if schema != "nls3d_points_v1":
        raise RuntimeError(
            f"Unerwartetes Schema '{schema}' (erwartet 'nls3d_points_v1')."
        )
    if "points" not in data or not isinstance(data["points"], list):
        raise RuntimeError("Keine 'points'-Liste im 3D-Scan-Export gefunden.")
    return data


def _sort_points(points: List[Dict[str, Any]], key: str) -> List[Dict[str, Any]]:
    def _get_num(d: Dict[str, Any], k: str) -> float:
        try:
            return float(d.get(k, 0.0) or 0.0)
        except Exception:  # pragma: no cover - defensiv
            return 0.0

    return sorted(points, key=lambda d: _get_num(d, key), reverse=True)


def _print_top_points(points: List[Dict[str, Any]], top_n: int, sort_key: str) -> None:
    if top_n <= 0:
        return

    pts_sorted = _sort_points(points, sort_key)
    pts_top = pts_sorted[:top_n]

    print(f"Top {len(pts_top)} Punkte (Sortierung nach '{sort_key}'):")
    print("id,label,layer,normalized,score_sum,score_max,count")
    for p in pts_top:
        pid = str(p.get("id", ""))
        label = str(p.get("label", ""))
        layer = str(p.get("layer", ""))
        try:
            norm = float(p.get("normalized", 0.0) or 0.0)
        except Exception:  # pragma: no cover - defensiv
            norm = 0.0
        try:
            score_sum = float(p.get("score_sum", 0.0) or 0.0)
        except Exception:  # pragma: no cover - defensiv
            score_sum = 0.0
        try:
            score_max = float(p.get("score_max", 0.0) or 0.0)
        except Exception:  # pragma: no cover - defensiv
            score_max = 0.0
        try:
            count = int(p.get("count", 0) or 0)
        except Exception:  # pragma: no cover - defensiv
            count = 0
        print(
            f"{pid},{label},{layer},{norm:.4f},{score_sum:.4f},{score_max:.4f},{count}"
        )


def _write_csv(points: List[Dict[str, Any]], csv_path: Path) -> None:
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "id",
        "label",
        "layer",
        "coords_x",
        "coords_y",
        "coords_z",
        "score_sum",
        "score_max",
        "normalized",
        "count",
    ]
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for p in points:
            coords = p.get("coords") or [0.0, 0.0, 0.0]
            if not isinstance(coords, list) or len(coords) < 3:
                coords = [0.0, 0.0, 0.0]
            try:
                cx = float(coords[0])
            except Exception:  # pragma: no cover - defensiv
                cx = 0.0
            try:
                cy = float(coords[1])
            except Exception:  # pragma: no cover - defensiv
                cy = 0.0
            try:
                cz = float(coords[2])
            except Exception:  # pragma: no cover - defensiv
                cz = 0.0
            try:
                score_sum = float(p.get("score_sum", 0.0) or 0.0)
            except Exception:  # pragma: no cover - defensiv
                score_sum = 0.0
            try:
                score_max = float(p.get("score_max", 0.0) or 0.0)
            except Exception:  # pragma: no cover - defensiv
                score_max = 0.0
            try:
                normalized = float(p.get("normalized", 0.0) or 0.0)
            except Exception:  # pragma: no cover - defensiv
                normalized = 0.0
            try:
                count = int(p.get("count", 0) or 0)
            except Exception:  # pragma: no cover - defensiv
                count = 0
            writer.writerow(
                {
                    "id": p.get("id", ""),
                    "label": p.get("label", ""),
                    "layer": p.get("layer", ""),
                    "coords_x": cx,
                    "coords_y": cy,
                    "coords_z": cz,
                    "score_sum": score_sum,
                    "score_max": score_max,
                    "normalized": normalized,
                    "count": count,
                }
            )


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Hilfstool zur Auswertung von *_3d_scan.json-Exports der Morphic Engine V1."
        )
    )
    parser.add_argument(
        "input",
        type=str,
        help="Pfad zu einer *_3d_scan.json-Datei (Schema nls3d_points_v1)",
    )
    parser.add_argument(
        "--top-n",
        type=int,
        default=10,
        help="Anzahl der Top-Punkte fuer die Konsolenausgabe (Standard: 10)",
    )
    parser.add_argument(
        "--sort-key",
        type=str,
        default="normalized",
        choices=["normalized", "score_sum", "score_max"],
        help="Sortierschluessel fuer die Top-Liste (Standard: normalized)",
    )
    parser.add_argument(
        "--csv-output",
        type=str,
        default="",
        help=(
            "Optionaler Pfad fuer eine CSV-Ausgabe aller Punkte. "
            "Wenn leer, wird keine CSV erzeugt."
        ),
    )

    args = parser.parse_args(argv)

    input_path = Path(args.input)
    try:
        data = _load_3d_scan(input_path)
    except Exception as exc:
        print(f"Fehler beim Laden des 3D-Scans: {exc}", file=sys.stderr)
        return 1

    points = data.get("points") or []
    if not isinstance(points, list) or not points:
        print("Keine Punkte im 3D-Scan vorhanden.", file=sys.stderr)
        return 1

    _print_top_points(points, args.top_n, args.sort_key)

    if args.csv_output:
        csv_path = Path(args.csv_output)
        try:
            _write_csv(points, csv_path)
        except Exception as exc:  # pragma: no cover - defensiv
            print(f"CSV-Ausgabe fehlgeschlagen: {exc}", file=sys.stderr)
            return 1
        else:
            print(f"CSV-Datei geschrieben: {csv_path}")

    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
