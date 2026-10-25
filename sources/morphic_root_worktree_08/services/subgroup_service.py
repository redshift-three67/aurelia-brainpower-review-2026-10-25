from __future__ import annotations

from typing import List, Dict

from core.subgroups import procedural_groups, procedural_circulation


class SubgroupService:
    """Fassade für prozedurale Subgruppen- und Fullbody-Kandidatengeneratoren."""

    def list_groups(self) -> List[str]:
        return procedural_groups.list_groups()

    def generate_group_candidates(self, group: str, seed: str, k: int = 32) -> List[Dict]:
        return procedural_groups.generate_candidates_for_group(group, seed, k=k)

    def generate_fullbody_candidates(
        self,
        groups: List[str],
        seed: str,
        k_total: int = 64,
    ) -> List[Dict]:
        return procedural_groups.generate_fullbody_candidates(groups, seed, k_total=k_total)

    def generate_circulation_candidates(self, seed: str, k: int = 32) -> List[Dict]:
        return procedural_circulation.generate_circulation_candidates(seed, k=k)
