from core.subgroups import procedural_groups as pg


def test_no_zero_candidates():
    """Jede Gruppe soll mindestens 1 Kandidaten liefern (k=3)."""
    for grp in pg._GROUP_LABELS:
        items = pg.generate_candidates_for_group(grp, seed="utest", k=3)
        assert items, f"{grp} erzeugt 0 Kandidaten"
