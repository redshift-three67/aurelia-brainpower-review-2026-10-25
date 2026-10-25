from __future__ import annotations

from pathlib import Path
from typing import List, Dict, Any

import numpy as np

_THIS_FILE = Path(__file__).resolve()
RADIALGO_ROOT = _THIS_FILE.parents[2]
ME_ROOT = _THIS_FILE.parents[1]

import sys
for p in (RADIALGO_ROOT, ME_ROOT):
    s = str(p)
    if s not in sys.path:
        sys.path.insert(0, s)

from core.nls import nls_db as new_nls
from services.nls_service import NlsService


def _dummy_items() -> List[Dict[str, Any]]:
    return [
        {
            "label": "item_low_rel",
            "rates": [10.0, 20.0],
            "entropy_mean": 0.3,
            "entropy_std": 0.1,
            "weight": 1.0,
            "reliability": 0.0,
        },
        {
            "label": "item_mid_rel",
            "rates": [15.0, 25.0],
            "entropy_mean": 0.3,
            "entropy_std": 0.1,
            "weight": 1.0,
            "reliability": 0.5,
        },
        {
            "label": "item_high_rel",
            "rates": [20.0, 30.0],
            "entropy_mean": 0.3,
            "entropy_std": 0.1,
            "weight": 1.0,
            "reliability": 1.0,
        },
    ]


def _resonance_fn(a: np.ndarray, b: np.ndarray) -> float:
    a = np.asarray(a, dtype=float).ravel()
    b = np.asarray(b, dtype=float).ravel()
    n = min(a.size, b.size)
    if n == 0:
        return 0.0
    a = a[:n]
    b = b[:n]
    return float(np.dot(a, b) / (1.0 + np.linalg.norm(a) * np.linalg.norm(b)))


def _dummy_items_personal() -> List[Dict[str, Any]]:
    base_fields = {
        "rates": [10.0, 20.0],
        "entropy_mean": 0.3,
        "entropy_std": 0.1,
        "weight": 1.0,
        "reliability": 1.0,
    }

    return [
        {
            **base_fields,
            "label": "item_emotion",
            "personal_vector": [1.0, 0.0, 0.0, 0.0],
        },
        {
            **base_fields,
            "label": "item_physisch",
            "personal_vector": [0.0, 1.0, 0.0, 0.0],
        },
        {
            **base_fields,
            "label": "item_mental",
            "personal_vector": [0.0, 0.0, 1.0, 0.0],
        },
        {
            **base_fields,
            "label": "item_astral",
            "personal_vector": [0.0, 0.0, 0.0, 1.0],
        },
    ]


def test_v2_matches_v1_when_no_reliability() -> None:
    items: List[Dict[str, Any]] = [
        {
            "label": "item_no_rel",
            "rates": [10.0, 20.0],
            "entropy_mean": 0.3,
            "entropy_std": 0.1,
            "weight": 1.0,
            # keine reliability gesetzt
        }
    ]

    client_rates = np.linspace(0.0, 50.0, num=8, dtype=float)
    client_entropy = 0.35

    scores_v1 = new_nls.compute_nls_scores(items, client_rates, client_entropy, _resonance_fn)
    scores_v2 = new_nls.compute_nls_scores_v2(items, client_rates, client_entropy, _resonance_fn)

    assert len(scores_v1) == len(scores_v2) == 1
    s1 = scores_v1[0]
    s2 = scores_v2[0]

    assert s1["label"] == s2["label"]
    assert np.isclose(s1["score"], s2["score"], rtol=1e-12, atol=1e-12)
    assert np.isclose(s1["resonance"], s2["resonance"], rtol=1e-12, atol=1e-12)
    assert np.isclose(s1["entropy_alignment"], s2["entropy_alignment"], rtol=1e-12, atol=1e-12)
    assert np.isclose(s1["z_entropy"], s2["z_entropy"], rtol=1e-12, atol=1e-12)


def test_v2_reliability_scales_scores_and_ranking() -> None:
    items = _dummy_items()
    client_rates = np.linspace(0.0, 50.0, num=8, dtype=float)
    client_entropy = 0.35

    scores = new_nls.compute_nls_scores_v2(items, client_rates, client_entropy, _resonance_fn)

    # Scores sollten nach reliability-Faktor sortiert sein, da Basis-Score ähnlich
    labels_by_score = [s["label"] for s in scores]
    assert labels_by_score[0] == "item_high_rel"
    assert labels_by_score[-1] == "item_low_rel"

    # Zusätzlich prüfen, dass reliability-Feld korrekt zurückgegeben wird
    rels = {s["label"]: s["reliability"] for s in scores}
    assert np.isclose(rels["item_low_rel"], 0.0)
    assert np.isclose(rels["item_mid_rel"], 0.5)
    assert np.isclose(rels["item_high_rel"], 1.0)


def test_v2_personal_vector_missing_does_not_change_scores() -> None:
    items = _dummy_items()
    client_rates = np.linspace(0.0, 50.0, num=8, dtype=float)
    client_entropy = 0.35

    base_scores = new_nls.compute_nls_scores_v2(items, client_rates, client_entropy, _resonance_fn)
    personal_vec = np.array([0.9, 0.1, 0.0, 0.0], dtype=float)
    personal_scores = new_nls.compute_nls_scores_v2(
        items,
        client_rates,
        client_entropy,
        _resonance_fn,
        client_personal_vector=personal_vec,
    )

    assert len(base_scores) == len(personal_scores)
    for s_base, s_pers in zip(base_scores, personal_scores):
        assert s_base["label"] == s_pers["label"]
        assert np.isclose(s_base["score"], s_pers["score"], rtol=1e-12, atol=1e-12)


def test_v2_personal_vector_influences_ranking() -> None:
    items = _dummy_items_personal()
    client_rates = np.linspace(0.0, 50.0, num=8, dtype=float)
    client_entropy = 0.35

    personal_vec = np.array([1.0, 0.0, 0.0, 0.0], dtype=float)
    scores = new_nls.compute_nls_scores_v2(
        items,
        client_rates,
        client_entropy,
        _resonance_fn,
        client_personal_vector=personal_vec,
    )

    labels_by_score = [s["label"] for s in scores]
    assert labels_by_score[0] == "item_emotion"
    assert labels_by_score[-1] in {"item_physisch", "item_mental", "item_astral"}


def test_nls_service_compute_scores_v2_delegates() -> None:
    items = _dummy_items()
    svc = NlsService(items)

    client_rates = np.linspace(0.0, 50.0, num=8, dtype=float)
    client_entropy = 0.35

    scores_core = new_nls.compute_nls_scores_v2(items, client_rates, client_entropy, _resonance_fn)
    scores_svc = svc.compute_scores_v2(client_rates, client_entropy, _resonance_fn)

    assert len(scores_core) == len(scores_svc)
    for sc, ss in zip(scores_core, scores_svc):
        assert sc["label"] == ss["label"]
        assert np.isclose(sc["score"], ss["score"], rtol=1e-12, atol=1e-12)
        assert np.isclose(sc["resonance"], ss["resonance"], rtol=1e-12, atol=1e-12)
        assert np.isclose(sc["entropy_alignment"], ss["entropy_alignment"], rtol=1e-12, atol=1e-12)
        assert np.isclose(sc["z_entropy"], ss["z_entropy"], rtol=1e-12, atol=1e-12)
        assert np.isclose(sc["reliability"], ss["reliability"], rtol=1e-12, atol=1e-12)


def test_nls_service_compute_scores_v2_with_personal_vector_delegates() -> None:
    items = _dummy_items_personal()
    svc = NlsService(items)

    client_rates = np.linspace(0.0, 50.0, num=8, dtype=float)
    client_entropy = 0.35
    personal_vec = np.array([0.0, 1.0, 0.0, 0.0], dtype=float)

    scores_core = new_nls.compute_nls_scores_v2(
        items,
        client_rates,
        client_entropy,
        _resonance_fn,
        client_personal_vector=personal_vec,
    )
    scores_svc = svc.compute_scores_v2(
        client_rates,
        client_entropy,
        _resonance_fn,
        client_personal_vector=personal_vec,
    )

    assert len(scores_core) == len(scores_svc)
    for sc, ss in zip(scores_core, scores_svc):
        assert sc["label"] == ss["label"]
        assert np.isclose(sc["score"], ss["score"], rtol=1e-12, atol=1e-12)
        assert np.isclose(sc["resonance"], ss["resonance"], rtol=1e-12, atol=1e-12)
        assert np.isclose(sc["entropy_alignment"], ss["entropy_alignment"], rtol=1e-12, atol=1e-12)
        assert np.isclose(sc["z_entropy"], ss["z_entropy"], rtol=1e-12, atol=1e-12)
        assert np.isclose(sc["reliability"], ss["reliability"], rtol=1e-12, atol=1e-12)
