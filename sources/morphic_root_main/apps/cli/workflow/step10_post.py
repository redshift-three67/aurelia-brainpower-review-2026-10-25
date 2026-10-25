"""Step 10: Post-Processing - Level-Info, De-Dup, Normalisierung."""

from __future__ import annotations

from .state import WorkflowState


def step_10_post(state: WorkflowState, verbose: bool = True) -> WorkflowState:
    if verbose:
        print("  [10/12] Post-Processing...")

    # De-Dup + Level-Info anreichern (wie in field.py implementiert)
    try:
        from apps.cli.commands.helpers.interpretation_helpers import (
            _rates_to_level_info,
        )

        dedup_index: dict[tuple[str, str], dict] = {}
        deduped = []
        for entry in state.matrix_results:
            label = str(entry.get("label", ""))
            group = str(entry.get("group", "") or "").strip()
            if not label:
                continue
            rates = entry.get("rates") or []
            key = (label.casefold(), group.casefold())
            if key in dedup_index:
                existing = dedup_index[key]
                if float(entry.get("score", 0)) > float(existing.get("score", 0)):
                    existing.update(entry)
                continue
            lvl_id, lvl_val, lvl_text, copen = _rates_to_level_info(rates, label)
            entry["level"] = lvl_text
            entry["copen_rate"] = copen
            entry["level_id"] = lvl_id
            deduped.append(entry)
            dedup_index[key] = entry

        deduped.sort(key=lambda e: float(e.get("score", 0)), reverse=True)
        state.matrix_results = deduped
        state.level_info = {
            "total": len(deduped),
            "levels": set(e.get("level", "?") for e in deduped),
        }
        if verbose:
            print(f"        Items nach De-Dup: {len(deduped)}")
    except Exception as exc:
        state.add_error(10, str(exc))
        if verbose:
            print(f"        [WARN] Post-Processing: {exc}")

    state.mark_step(10)
    return state
