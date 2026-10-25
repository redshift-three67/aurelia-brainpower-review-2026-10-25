from __future__ import annotations

from typing import Dict, List

from core.subgroups import procedural_groups, procedural_circulation


class SubgroupService:
    """Fassade für prozedurale Subgruppen- und Fullbody-Kandidatengeneratoren."""

    def __init__(self, catalog_provider: object | None = None) -> None:
        self._catalog_provider = catalog_provider

    def list_groups(self) -> List[str]:
        if self._catalog_provider is not None:
            return list(self._catalog_provider.list_groups())  # type: ignore[attr-defined]
        return procedural_groups.list_groups()

    def generate_group_candidates(self, group: str, seed: str, k: int = 32) -> List[Dict]:
        if self._catalog_provider is not None:
            return list(
                self._catalog_provider.generate_group_candidates(  # type: ignore[attr-defined]
                    group,
                    seed,
                    k=k,
                )
            )
        return procedural_groups.generate_candidates_for_group(group, seed, k=k)

    def generate_fullbody_candidates(
        self,
        groups: List[str],
        seed: str,
        k_total: int = 64,
    ) -> List[Dict]:
        if self._catalog_provider is not None:
            return list(
                self._catalog_provider.generate_fullbody_candidates(  # type: ignore[attr-defined]
                    groups,
                    seed,
                    k_total=k_total,
                )
            )
        return procedural_groups.generate_fullbody_candidates(groups, seed, k_total=k_total)

    def generate_circulation_candidates(self, seed: str, k: int = 32) -> List[Dict]:
        return procedural_circulation.generate_circulation_candidates(seed, k=k)
