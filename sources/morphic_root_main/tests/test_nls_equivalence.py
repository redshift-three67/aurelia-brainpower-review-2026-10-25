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

import nls_db as old_nls  # type: ignore
from core.nls import nls_db as new_nls
from services.nls_service import NlsService


def _assert_items_equal(items_old: List[Dict[str, Any]], items_new: List[Dict[str, Any]]) -> None:
    assert len(items_old) == len(items_new)
    for io, inew in zip(items_old, items_new):
        assert io["label"] == inew["label"]
        np.testing.assert_allclose(
            np.asarray(io["rates"], dtype=float),
            np.asarray(inew["rates"], dtype=float),
            rtol=1e-12,
            atol=1e-12,
        )
        assert np.isclose(io["entropy_mean"], inew["entropy_mean"], rtol=1e-12, atol=1e-12)
        assert np.isclose(io["entropy_std"], inew["entropy_std"], rtol=1e-12, atol=1e-12)
        assert np.isclose(io["weight"], inew["weight"], rtol=1e-12, atol=1e-12)


def test_load_nls_db_equivalence() -> None:
    path = RADIALGO_ROOT / "bakterien_nls.json"
    items_old = old_nls.load_nls_db(str(path))
    items_new = new_nls.load_nls_db(str(path))
    _assert_items_equal(items_old, items_new)


def test_compute_nls_scores_equivalence() -> None:
    path = RADIALGO_ROOT / "bakterien_nls.json"
    items_old = old_nls.load_nls_db(str(path))
    items_new = new_nls.load_nls_db(str(path))

    # deterministischer Dummy-Resonanz-Operator (unabhängig von Resonator)
    # robust gegenüber unterschiedlich langen Vektoren: arbeitet auf dem
    # überlappenden Abschnitt mit minimaler Länge.
    def resonance_fn(a: np.ndarray, b: np.ndarray) -> float:
        a = np.asarray(a, dtype=float).ravel()
        b = np.asarray(b, dtype=float).ravel()
        n = min(a.size, b.size)
        if n == 0:
            return 0.0
        a = a[:n]
        b = b[:n]
        return float(np.dot(a, b) / (1.0 + np.linalg.norm(a) * np.linalg.norm(b)))

    client_rates = np.linspace(0.0, 99.0, num=16, dtype=float)
    client_entropy = 0.42

    scores_old = old_nls.compute_nls_scores(items_old, client_rates, client_entropy, resonance_fn)
    scores_new = new_nls.compute_nls_scores(items_new, client_rates, client_entropy, resonance_fn)

    assert len(scores_old) == len(scores_new)
    for so, sn in zip(scores_old, scores_new):
        assert so["label"] == sn["label"]
        assert np.isclose(so["score"], sn["score"], rtol=1e-12, atol=1e-12)
        assert np.isclose(so["resonance"], sn["resonance"], rtol=1e-12, atol=1e-12)
        assert np.isclose(so["entropy_alignment"], sn["entropy_alignment"], rtol=1e-12, atol=1e-12)
        assert np.isclose(so["z_entropy"], sn["z_entropy"], rtol=1e-12, atol=1e-12)


def test_nls_service_matches_core() -> None:
    path = RADIALGO_ROOT / "bakterien_nls.json"
    items = new_nls.load_nls_db(str(path))
    service = NlsService(items)

    def resonance_fn(a: np.ndarray, b: np.ndarray) -> float:
        a = np.asarray(a, dtype=float).ravel()
        b = np.asarray(b, dtype=float).ravel()
        n = min(a.size, b.size)
        if n == 0:
            return 0.0
        a = a[:n]
        b = b[:n]
        return float(np.dot(a, b) / (1.0 + np.linalg.norm(a) * np.linalg.norm(b)))

    client_rates = np.linspace(0.0, 99.0, num=16, dtype=float)
    client_entropy = 0.42

    scores_core = new_nls.compute_nls_scores(items, client_rates, client_entropy, resonance_fn)
    scores_service = service.compute_scores(client_rates, client_entropy, resonance_fn)

    assert len(scores_core) == len(scores_service)
    for sc, ss in zip(scores_core, scores_service):
        assert sc["label"] == ss["label"]
        assert np.isclose(sc["score"], ss["score"], rtol=1e-12, atol=1e-12)
        assert np.isclose(sc["resonance"], ss["resonance"], rtol=1e-12, atol=1e-12)
        assert np.isclose(sc["entropy_alignment"], ss["entropy_alignment"], rtol=1e-12, atol=1e-12)
        assert np.isclose(sc["z_entropy"], ss["z_entropy"], rtol=1e-12, atol=1e-12)
