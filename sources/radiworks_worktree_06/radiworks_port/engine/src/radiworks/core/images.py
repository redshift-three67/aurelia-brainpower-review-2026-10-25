"""Bildschichten-Analyse — Port (imagelayers/ImageLayersAnalysis.analyze,
FUNKTIONSANALYSE §10).

Original-Verhalten: je Schicht GV aus 256 Zügen (Zug zählt, wenn
getInteger(0,1000) >= 500; Bonus bei Würfel-6 getInteger(1,6)==6); Runden
werden wiederholt, bis max >= 162. Danach Normalisierung 256 / (max - min).

Die Bilder selbst verlässt der Browser nie als Binärdaten-Anhang: die
Webapp sendet MD5 + Pixelmaße; die Analyse ist rein entropiebasiert
(wie im Original, das ebenfalls nur GV-Werte je Schicht zieht).
"""

from __future__ import annotations

from ..entropy import EntropyProvider

# ImageLayersAnalysis: RESIZE_HEIGHT etc. sind Darstellung; fachlich zählen
# 256 Züge je Schicht und die Abbruchschwelle max >= 162.
DRAWS_PER_LAYER = 256
ROUND_STOP_MAX = 162


def analyze_layers(count: int, entropy: EntropyProvider) -> dict:
    """Port des analyze()-Kerns für `count` Schichten."""
    if count <= 0:
        return {"layers": [], "min": 0, "max": 0, "relativeGVratio": 0.0}
    gvs: list[int] = []
    max_gv = 0
    rounds = 0
    while max_gv < ROUND_STOP_MAX:
        rounds += 1
        gvs = []
        for _ in range(count):
            gv = 0
            for _ in range(DRAWS_PER_LAYER):
                if entropy.get_integer(0, 1000) >= 500:
                    gv += 1
                    if entropy.get_integer(1, 6) == 6:
                        gv += 1
            gvs.append(gv)
            max_gv = max(max_gv, gv)
    min_gv = min(gvs)
    ratio = 256.0 / (max_gv - min_gv) if max_gv != min_gv else 0.0
    return {
        "layers": [{"index": i, "gv": gv} for i, gv in enumerate(gvs)],
        "min": min_gv,
        "max": max_gv,
        "rounds": rounds,
        "relativeGVratio": round(ratio, 4),
    }
