"""Tests: AnalysisDraft-Statusmaschine und Promote-Pflicht (D18)."""

import pytest

from radiworks.core.analysis import AnalysisResult, RateObject
from radiworks.core.draft import DraftError, DraftStore
from radiworks.passport import Passport
from radiworks.entropy import EntropyProvider
from radiworks import manifest as manifest_module


def _passport() -> dict:
    entropy = EntropyProvider(seed=1)
    passport = Passport.create(
        kernel=manifest_module.KERNEL_ID,
        kernel_version=manifest_module.KERNEL_VERSION,
        kernel_hash="sha256:test",
        input_payload={"database": "HOMEOPATHY"},
        entropy=entropy,
    )
    data = passport.to_dict()
    data["kernel"] = manifest_module.KERNEL_ID
    data["kernel_version"] = manifest_module.KERNEL_VERSION
    return data


def _analysis(gv=100):
    result = AnalysisResult(
        general_vitality=gv,
        rate_objects=[
            RateObject(energetic_value=90, name_or_rate="Abrotanum", gv=600, url="http://x"),
            RateObject(energetic_value=40, name_or_rate="Absinthium", gv=50),
        ],
    )
    return result.to_dict()


def test_create_draft_runs_copyguard(tmp_path):
    store = DraftStore(tmp_path / "drafts")
    draft = store.create_from_analysis(
        analysis_dict=_analysis(), passport=_passport(), database="HOMEOPATHY"
    )
    assert draft["status"] == "draft"
    assert draft["copyguard_digest"]
    assert draft["copyguard_verdict"] == "allow"
    assert draft["client_editable_fields"] == ["practitioner_note"]


def test_copyguard_blocks_heil_claim(tmp_path):
    store = DraftStore(tmp_path / "drafts")
    analysis = _analysis()
    analysis["rateObjects"][0]["nameOrRate"] = "Mittel das Krebs heilt"
    draft = store.create_from_analysis(
        analysis_dict=analysis, passport=_passport(), database="HOMEOPATHY"
    )
    assert draft["copyguard_verdict"] == "block"
    assert draft["copyguard_findings"]


def test_transition_chain_valid(tmp_path):
    store = DraftStore(tmp_path / "drafts")
    draft = store.create_from_analysis(
        analysis_dict=_analysis(), passport=_passport(), database="HOMEOPATHY"
    )
    store.transition(draft["id"], "client_review")
    store.transition(draft["id"], "ready")
    promoted = store.transition(draft["id"], "promoted")
    assert promoted["status"] == "promoted"


def test_invalid_transition_rejected(tmp_path):
    store = DraftStore(tmp_path / "drafts")
    draft = store.create_from_analysis(
        analysis_dict=_analysis(), passport=_passport(), database="HOMEOPATHY"
    )
    with pytest.raises(DraftError):
        store.transition(draft["id"], "promoted")  # draft -> promoted ist verboten


def test_promote_returns_broadcast_entries_above_gv(tmp_path):
    """Original broadcastMix: nur Raten mit gv > caseGV, Sortierung gv desc,
    SEKUNDEN = GV-Differenz (Zeile 440)."""
    store = DraftStore(tmp_path / "drafts")
    draft = store.create_from_analysis(
        analysis_dict=_analysis(gv=100), passport=_passport(), database="HOMEOPATHY"
    )
    store.transition(draft["id"], "ready")
    entries = store.promote_to_broadcast_queue(draft["id"])
    # Nur Abrotanum (gv 600) ueber caseGV 100 -> Absinthium (gv 50) nicht.
    assert len(entries) == 1
    assert entries[0]["signature"].startswith("Abrotanum")
    assert entries[0]["seconds"] == 500  # 600 - 100 (GV-Differenz, Original Zeile 440)


def test_promote_blocked_by_copyguard(tmp_path):
    store = DraftStore(tmp_path / "drafts")
    analysis = _analysis()
    analysis["rateObjects"][0]["nameOrRate"] = "Wunderheilung garant"
    draft = store.create_from_analysis(
        analysis_dict=analysis, passport=_passport(), database="HOMEOPATHY"
    )
    store.transition(draft["id"], "ready")
    with pytest.raises(DraftError):
        store.promote_to_broadcast_queue(draft["id"])
