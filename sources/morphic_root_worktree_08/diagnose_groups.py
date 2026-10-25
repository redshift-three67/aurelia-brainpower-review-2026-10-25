#!/usr/bin/env python3
"""Diagnose-Skript: prüft, ob alle Gruppen mindestens einen Kandidaten erzeugen.

Nutzung:
    python diagnose_groups.py [--k-total 512]

Ohne Argumente wird jede Gruppe mit k=4 getestet. Falls --k-total angegeben ist,
werden wie bei generate_fullbody_candidates die Items verteilt.
"""

import sys
from typing import List
from services.subgroup_service import SubgroupService
from core.subgroups import procedural_groups as pg

DEFAULT_K = 4


def diagnose_per_group(k: int = DEFAULT_K) -> None:
    """Testet jede Gruppe einzeln mit k Kandidaten."""
    missing: List[str] = []
    for group in sorted(pg._GROUP_LABELS.keys()):
        try:
            items = pg.generate_candidates_for_group(group, seed="diag", k=k)
            if not items:
                missing.append(group)
        except Exception as exc:
            missing.append(f"{group} (ERROR: {exc})")
    total = len(pg._GROUP_LABELS)
    ok = total - len(missing)
    print(f"Gesamtgruppen: {total}")
    print(f"✓ Gruppen MIT Kandidaten: {ok}")
    print(f"✗ Gruppen OHNE Kandidaten: {len(missing)}")
    if missing:
        print("-" * 70)
        for g in missing:
            print(f"  - {g}")


def diagnose_fullbody(k_total: int):
    """Verteilt k_total auf alle Gruppen (wie Multiplex-Scan) und prüft."""
    groups = sorted(pg._GROUP_LABELS.keys())
    svc = SubgroupService()
    items = svc.generate_fullbody_candidates(groups, seed="diag", k_total=k_total)
    with_candidates = {}
    for it in items:
        g = it.get("group")
        if g:
            with_candidates[g] = with_candidates.get(g, 0) + 1
    missing = [g for g in groups if g not in with_candidates]
    print(f"k_total = {k_total}")
    print(f"Gesamtgruppen: {len(groups)}")
    print(f"✓ Gruppen MIT Kandidaten: {len(with_candidates)}")
    print(f"✗ Gruppen OHNE Kandidaten: {len(missing)}")
    if missing:
        print("-" * 70)
        for g in missing:
            print(f"  - {g}")


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "--k-total":
        try:
            k_total_val = int(sys.argv[2])
        except ValueError:
            print("--k-total muss eine Ganzzahl sein")
            sys.exit(1)
        diagnose_fullbody(k_total_val)
    else:
        diagnose_per_group()
