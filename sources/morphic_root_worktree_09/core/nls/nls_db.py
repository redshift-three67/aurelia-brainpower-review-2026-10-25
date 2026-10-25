from __future__ import annotations

import json
from pathlib import Path
from typing import Callable, Dict, List, Any

import numpy as np


def load_nls_db(path: str) -> List[Dict[str, Any]]:
    db_path = Path(path)
    if not db_path.exists():
        fallback = Path(__file__).resolve().parents[2] / "data" / "nls" / db_path.name
        if fallback.exists():
            db_path = fallback
    with open(db_path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    items = data.get("items", []) if isinstance(data, dict) else data
    normed = []
    for it in items:
        label = it.get("label")
        rates = it.get("rates", [])
        entropy_mean = float(it.get("entropy_mean", 0.3))
        entropy_std = float(it.get("entropy_std", 0.1))
        weight = float(it.get("weight", 1.0))
        normed.append({
            "label": label,
            "rates": list(map(float, rates)),
            "entropy_mean": entropy_mean,
            "entropy_std": entropy_std,
            "weight": weight,
        })
    return normed


def compute_nls_scores(
    items: List[Dict[str, Any]],
    client_rates: np.ndarray,
    client_entropy: float,
    resonance_fn: Callable[[np.ndarray, np.ndarray], float],
) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []
    for it in items:
        rates = np.array(it["rates"], dtype=float)
        s_res = float(resonance_fn(client_rates, rates))
        mean_ent = float(it.get("entropy_mean", 0.3))
        std = max(1e-6, float(it.get("entropy_std", 0.1)))
        z = (client_entropy - mean_ent) / std
        s_ent = float(np.exp(-0.5 * z * z))  # 1.0 bei perfektem Match, ->0 bei starker Abweichung
        w = float(it["weight"]) if "weight" in it else 1.0
        score = w * (0.6 * s_res + 0.4 * s_ent)
        results.append({
            "label": it["label"],
            "score": score,
            "resonance": s_res,
            "entropy_alignment": s_ent,
            "z_entropy": z,
        })
    results.sort(key=lambda x: x["score"], reverse=True)
    return results


def _personal_alignment(client_vec: np.ndarray, item_vec: np.ndarray) -> float:
    client = np.asarray(client_vec, dtype=float).ravel()
    item = np.asarray(item_vec, dtype=float).ravel()
    n = min(client.size, item.size)
    if n == 0:
        return 1.0
    client = client[:n]
    item = item[:n]
    n_client = float(np.linalg.norm(client))
    n_item = float(np.linalg.norm(item))
    if n_client == 0.0 or n_item == 0.0:
        return 1.0
    cos_sim = float(np.dot(client, item) / (n_client * n_item))
    # Kosinus-Ähnlichkeit [-1,1] nach [0,1] abbilden und klemmen
    sim01 = (cos_sim + 1.0) / 2.0
    return float(max(0.0, min(1.0, sim01)))


def compute_nls_scores_v2(
    items: List[Dict[str, Any]],
    client_rates: np.ndarray,
    client_entropy: float,
    resonance_fn: Callable[[np.ndarray, np.ndarray], float],
    client_personal_vector: np.ndarray | None = None,
) -> List[Dict[str, Any]]:
    """Erweiterte NLS-Bewertung mit Reliability-Faktor.

    - Basisscore wie in v1: 0.6 * s_res + 0.4 * s_ent
    - zusätzlicher Faktor "reliability" in [0,1], der den Score skaliert.

    Ist reliability nicht gesetzt, verhält sich v2 praktisch wie v1.
    """

    results: List[Dict[str, Any]] = []
    for it in items:
        rates = np.array(it["rates"], dtype=float)
        s_res = float(resonance_fn(client_rates, rates))
        mean_ent = float(it.get("entropy_mean", 0.3))
        std = max(1e-6, float(it.get("entropy_std", 0.1)))
        z = (client_entropy - mean_ent) / std
        s_ent = float(np.exp(-0.5 * z * z))
        w = float(it.get("weight", 1.0))

        base = 0.6 * s_res + 0.4 * s_ent

        rel_raw = float(it.get("reliability", 1.0))
        rel = max(0.0, min(1.0, rel_raw))
        rel_factor = 0.5 + 0.5 * rel

        score = w * base * rel_factor

        personal_align = 1.0
        if client_personal_vector is not None and "personal_vector" in it:
            try:
                personal_align = _personal_alignment(client_personal_vector, np.asarray(it["personal_vector"], dtype=float))
            except Exception:
                personal_align = 1.0

        score *= 0.5 + 0.5 * personal_align

        results.append(
            {
                "label": it["label"],
                "score": score,
                "resonance": s_res,
                "entropy_alignment": s_ent,
                "z_entropy": z,
                "reliability": rel,
                "personal_alignment": personal_align,
            }
        )

    results.sort(key=lambda x: x["score"], reverse=True)
    return results
