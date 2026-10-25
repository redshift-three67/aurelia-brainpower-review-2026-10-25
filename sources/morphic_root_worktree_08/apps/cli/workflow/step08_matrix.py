"""Step 08: Matrix-Suche - Delegiert an NlsService (Kernengine)."""

from __future__ import annotations

from .state import WorkflowState


def step_08_matrix(state: WorkflowState, verbose: bool = True) -> WorkflowState:
    if verbose:
        print("  [8/12] Matrix-Suche (NLS v2)...")

    try:
        from services.nls_service import NlsService
        from services.subgroup_service import SubgroupService
        from core.profile_sync import get_profiles_up_to_level

        subgroup_svc = SubgroupService()
        profiles = get_profiles_up_to_level(max(1, min(4, state.profile_level)))
        groups: list[str] = []
        for profile in profiles:
            for group in getattr(profile, "groups", []):
                if group not in groups:
                    groups.append(group)

        seed = f"{state.first_name}|{state.name}|{state.birth_date}|{state.birth_place}|{state.focus}"
        items = subgroup_svc.generate_fullbody_candidates(
            groups=groups, seed=seed, k_total=4096
        )
        state.candidate_count = len(items)

        nls = NlsService(items)
        scores = nls.compute_scores_v2(
            client_rates=state.client_rates,
            client_entropy=0.3,
            resonance_fn=lambda a, b: float(
                __import__(
                    "core.resonance.resonator", fromlist=["MorphicFieldResonator"]
                )
                .MorphicFieldResonator({}, h_level=state.h_level)
                .resonance_score(a, b)
            ),
        )

        state.matrix_results = scores[:384]
        if verbose:
            print(f"        Kandidaten: {state.candidate_count}")
            print(f"        Top-Scores: {len(state.matrix_results)}")
            if scores:
                top = scores[0]
                print(
                    f"        #1: {top.get('label', '?')} (score={top.get('score', 0):.4f})"
                )
    except Exception as exc:
        state.add_error(8, str(exc))
        if verbose:
            print(f"        [WARN] Matrix-Suche: {exc}")

    state.mark_step(8)
    return state
