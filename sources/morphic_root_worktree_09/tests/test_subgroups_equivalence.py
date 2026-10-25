from __future__ import annotations

from pathlib import Path
from typing import List, Dict

import numpy as np

_THIS_FILE = Path(__file__).resolve()
RADIALGO_ROOT = _THIS_FILE.parents[2]
ME_ROOT = _THIS_FILE.parents[1]

import sys
for p in (RADIALGO_ROOT, ME_ROOT):
    s = str(p)
    if s not in sys.path:
        sys.path.insert(0, s)

import procedural_groups as old_pg  # type: ignore
import procedural_circulation as old_pc  # type: ignore
from core.subgroups import procedural_groups as new_pg
from core.subgroups import procedural_circulation as new_pc
from services.subgroup_service import SubgroupService


def _compare_candidate_lists(a: List[Dict], b: List[Dict]) -> None:
    assert len(a) == len(b)
    for ia, ib in zip(a, b):
        assert ia["label"] == ib["label"]
        np.testing.assert_allclose(
            np.asarray(ia["rates"], dtype=float),
            np.asarray(ib["rates"], dtype=float),
            rtol=1e-10,
            atol=1e-10,
        )


def test_list_groups_equivalence() -> None:
    old_groups = sorted(old_pg.list_groups())
    new_groups = sorted(new_pg.list_groups())
    assert old_groups == new_groups


def test_generate_candidates_for_groups_equivalence() -> None:
    seed = "test-seed-123"
    groups = ["chakren", "meridiane", "tcm_full", "ps_freq", "schwermetalle_tox"]
    for g in groups:
        old_items = old_pg.generate_candidates_for_group(g, seed, k=32)
        new_items = new_pg.generate_candidates_for_group(g, seed, k=32)
        _compare_candidate_lists(old_items, new_items)


def test_generate_fullbody_candidates_equivalence() -> None:
    seed = "fullbody-seed"
    groups = ["chakren", "meridiane", "bakterien", "viren"]
    k_total = 64
    old_items = old_pg.generate_fullbody_candidates(groups, seed, k_total=k_total)
    new_items = new_pg.generate_fullbody_candidates(groups, seed, k_total=k_total)
    _compare_candidate_lists(old_items, new_items)


def test_circulation_candidates_equivalence() -> None:
    seed = "circulation-seed"
    k = 24
    old_items = old_pc.generate_circulation_candidates(seed, k=k)
    new_items = new_pc.generate_circulation_candidates(seed, k=k)
    _compare_candidate_lists(old_items, new_items)


def test_subgroup_service_delegates_correctly() -> None:
    seed = "service-seed"
    svc = SubgroupService()
    groups = svc.list_groups()
    assert groups  # nicht leer

    g = "chakren"
    k = 16
    items_old = old_pg.generate_candidates_for_group(g, seed, k=k)
    items_new = svc.generate_group_candidates(g, seed, k=k)
    _compare_candidate_lists(items_old, items_new)

    fb_old = old_pg.generate_fullbody_candidates([g], seed, k_total=k)
    fb_new = svc.generate_fullbody_candidates([g], seed, k_total=k)
    _compare_candidate_lists(fb_old, fb_new)

    circ_old = old_pc.generate_circulation_candidates(seed, k=k)
    circ_new = svc.generate_circulation_candidates(seed, k=k)
    _compare_candidate_lists(circ_old, circ_new)
