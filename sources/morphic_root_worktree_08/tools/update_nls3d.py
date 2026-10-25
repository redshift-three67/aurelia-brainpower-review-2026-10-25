import os

# Der neue Inhalt fuer core/nls3d_points.py
NEW_CONTENT = r'''"""NLS 3D-Punkte: symbolisches Datenmodell fuer 3D-NLS-Exports.

Dieses Modul enthaelt keine Engine- oder DB-Logik. Es liefert nur
symbolische 3D-Punkte und ein einfaches Mapping von Items/Gruppen
auf logische 3D-Punkte fuer die *_3d_scan.json Exporte.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass(frozen=True)
class Nls3DPoint:
    """Definition eines logischen 3D-Punktes.

    coords sind vorerst symbolische Platzhalter (kein echtes Anatomie-Modell).
    Format: [x, y, z] wobei y=oben/unten, x=links/rechts, z=vorne/hinten
    """

    id: str
    label: str
    layer: str
    coords: List[float]
    group_hint: List[str]


NLS3D_POINTS: Dict[str, Nls3DPoint] = {
    # --- WIRBELSAEULE ---
    "SPINE_CERVICAL": Nls3DPoint(id="SPINE_CERVICAL", label="HWS (C0-C7)", layer="physisch", coords=[0.0, 0.35, -0.05], group_hint=["wirbelsaeule_hws"]),
    "SPINE_THORACIC": Nls3DPoint(id="SPINE_THORACIC", label="BWS (Th1-Th12)", layer="physisch", coords=[0.0, 0.15, -0.05], group_hint=["wirbelsaeule_bws"]),
    "SPINE_LUMBAR": Nls3DPoint(id="SPINE_LUMBAR", label="LWS (L1-L5)", layer="physisch", coords=[0.0, -0.05, -0.05], group_hint=["wirbelsaeule_lws"]),
    "SPINE_SACRAL": Nls3DPoint(id="SPINE_SACRAL", label="Kreuzbein", layer="physisch", coords=[0.0, -0.20, -0.05], group_hint=["wirbelsaeule_sakral"]),
    
    # Detail-Segmente (exemplarisch)
    "SPINE_CERVICAL_UPPER": Nls3DPoint(id="SPINE_CERVICAL_UPPER", label="Obere HWS (Atlas/Axis)", layer="physisch", coords=[0.0, 0.40, -0.05], group_hint=["wirbelsaeule_hws"]),
    "SPINE_CERVICAL_LOWER": Nls3DPoint(id="SPINE_CERVICAL_LOWER", label="Untere HWS", layer="physisch", coords=[0.0, 0.30, -0.05], group_hint=["wirbelsaeule_hws"]),

    # --- ORGANE (Grobausrichtung) ---
    "ORGAN_BRAIN": Nls3DPoint(id="ORGAN_BRAIN", label="Gehirn / ZNS", layer="physisch", coords=[0.0, 0.50, 0.0], group_hint=["nervensystem_zns"]),
    "ORGAN_EYES": Nls3DPoint(id="ORGAN_EYES", label="Augen", layer="physisch", coords=[0.0, 0.45, 0.1], group_hint=["auge_fein"]),
    "ORGAN_THYROID": Nls3DPoint(id="ORGAN_THYROID", label="Schilddruese", layer="physisch", coords=[0.0, 0.32, 0.05], group_hint=["hormone_schilddruese"]),
    
    "ORGAN_HEART": Nls3DPoint(id="ORGAN_HEART", label="Herz", layer="physisch", coords=[0.05, 0.20, 0.05], group_hint=["herz", "kreislauf"]),
    "ORGAN_LUNGS": Nls3DPoint(id="ORGAN_LUNGS", label="Lunge / Bronchien", layer="physisch", coords=[-0.10, 0.25, 0.05], group_hint=["atmung"]),
    
    "ORGAN_LIVER": Nls3DPoint(id="ORGAN_LIVER", label="Leber / Galle", layer="physisch", coords=[-0.15, 0.05, 0.05], group_hint=["entgiftung_leber"]),
    "ORGAN_STOMACH": Nls3DPoint(id="ORGAN_STOMACH", label="Magen", layer="physisch", coords=[0.10, 0.08, 0.08], group_hint=["verdauung_magen"]),
    "ORGAN_PANCREAS": Nls3DPoint(id="ORGAN_PANCREAS", label="Bauchspeicheldruese", layer="physisch", coords=[0.05, 0.05, 0.02], group_hint=["verdauung_pankreas"]),
    "ORGAN_SPLEEN": Nls3DPoint(id="ORGAN_SPLEEN", label="Milz", layer="physisch", coords=[0.20, 0.10, 0.05], group_hint=["immunsystem"]),
    
    "ORGAN_KIDNEY_L": Nls3DPoint(id="ORGAN_KIDNEY_L", label="Niere Links", layer="physisch", coords=[0.10, -0.02, -0.08], group_hint=["entgiftung_niere"]),
    "ORGAN_KIDNEY_R": Nls3DPoint(id="ORGAN_KIDNEY_R", label="Niere Rechts", layer="physisch", coords=[-0.10, -0.02, -0.08], group_hint=["entgiftung_niere"]),
    
    "ORGAN_INTESTINE": Nls3DPoint(id="ORGAN_INTESTINE", label="Darm", layer="physisch", coords=[0.0, -0.10, 0.10], group_hint=["verdauung_darm"]),
    "ORGAN_BLADDER": Nls3DPoint(id="ORGAN_BLADDER", label="Blase / Urogenital", layer="physisch", coords=[0.0, -0.25, 0.08], group_hint=["entgiftung_niere"]),

    # --- SYSTEME / PATHOGENE (Sammelpunkte) ---
    "SYSTEM_IMMUNE": Nls3DPoint(id="SYSTEM_IMMUNE", label="Immunsystem (Thymus)", layer="energetisch", coords=[0.0, 0.22, 0.06], group_hint=["immunsystem"]),
    "SYSTEM_BLOOD": Nls3DPoint(id="SYSTEM_BLOOD", label="Blut / Kreislauf", layer="physisch", coords=[0.0, 0.10, 0.0], group_hint=["blut"]),
    "SYSTEM_LYMPH": Nls3DPoint(id="SYSTEM_LYMPH", label="Lymphsystem", layer="physisch", coords=[0.20, 0.30, 0.0], group_hint=["entgiftung_lymphe"]),
    "SYSTEM_DETOX": Nls3DPoint(id="SYSTEM_DETOX", label="Entgiftung allgemein", layer="energetisch", coords=[-0.20, -0.10, 0.0], group_hint=["detox"]),

    # --- CHAKREN (Energiezentren) ---
    "CHAKRA_ROOT": Nls3DPoint(id="CHAKRA_ROOT", label="Wurzelchakra", layer="energetisch", coords=[0.0, -0.35, 0.0], group_hint=["chakren"]),
    "CHAKRA_SACRAL": Nls3DPoint(id="CHAKRA_SACRAL", label="Sakralchakra", layer="energetisch", coords=[0.0, -0.25, 0.05], group_hint=["chakren"]),
    "CHAKRA_SOLAR": Nls3DPoint(id="CHAKRA_SOLAR", label="Solarplexus", layer="energetisch", coords=[0.0, -0.05, 0.08], group_hint=["chakren"]),
    "CHAKRA_HEART": Nls3DPoint(id="CHAKRA_HEART", label="Herzchakra", layer="energetisch", coords=[0.0, 0.15, 0.10], group_hint=["chakren"]),
    "CHAKRA_THROAT": Nls3DPoint(id="CHAKRA_THROAT", label="Halschakra", layer="energetisch", coords=[0.0, 0.30, 0.05], group_hint=["chakren"]),
    "CHAKRA_THIRD_EYE": Nls3DPoint(id="CHAKRA_THIRD_EYE", label="Stirnchakra", layer="energetisch", coords=[0.0, 0.48, 0.08], group_hint=["chakren"]),
    "CHAKRA_CROWN": Nls3DPoint(id="CHAKRA_CROWN", label="Kronenchakra", layer="energetisch", coords=[0.0, 0.60, 0.0], group_hint=["chakren"]),

    # --- MERIDIANE (Exemplarisch) ---
    "MERIDIAN_LU": Nls3DPoint(id="MERIDIAN_LU", label="Lungenmeridian", layer="energetisch", coords=[-0.25, 0.30, 0.0], group_hint=["meridiane"]),
    "MERIDIAN_HE": Nls3DPoint(id="MERIDIAN_HE", label="Herzmeridian", layer="energetisch", coords=[0.25, 0.20, 0.0], group_hint=["meridiane"]),
    "MERIDIAN_KI": Nls3DPoint(id="MERIDIAN_KI", label="Nierenmeridian", layer="energetisch", coords=[0.0, -0.30, -0.05], group_hint=["meridiane"]),
}


def map_item_to_point(entry: Dict[str, object], group: Optional[str] = None) -> Optional[Nls3DPoint]:
    """Mappt ein Item auf einen 3D-Punkt.

    Argumente:
        entry: Das Item-Dictionary (muss 'label' enthalten, optional 'group').
        group: Optionaler Override für die Gruppe.
    """
    label_l = str(entry.get("label", "")).lower()
    group_l = str(entry.get("group", "") or group or "").lower()

    # --- 1. Direkte Gruppen-Zuordnung (Schnellste Methode) ---
    
    # Wirbelsaeule
    if "hws" in group_l: return NLS3D_POINTS["SPINE_CERVICAL"]
    if "bws" in group_l: return NLS3D_POINTS["SPINE_THORACIC"]
    if "lws" in group_l: return NLS3D_POINTS["SPINE_LUMBAR"]
    if "sakral" in group_l: return NLS3D_POINTS["SPINE_SACRAL"]
    
    # Organe (Entgiftung/Verdauung)
    if "leber" in group_l: return NLS3D_POINTS["ORGAN_LIVER"]
    if "niere" in group_l: return NLS3D_POINTS.get("ORGAN_KIDNEY_L")
    if "magen" in group_l: return NLS3D_POINTS["ORGAN_STOMACH"]
    if "darm" in group_l: return NLS3D_POINTS["ORGAN_INTESTINE"]
    if "pankreas" in group_l or "bauchspeichel" in group_l: return NLS3D_POINTS["ORGAN_PANCREAS"]
    if "lymphe" in group_l: return NLS3D_POINTS["SYSTEM_LYMPH"]
    if "herz" in group_l or "kreislauf" in group_l: return NLS3D_POINTS["ORGAN_HEART"]
    if "atmung" in group_l or "lunge" in group_l: return NLS3D_POINTS["ORGAN_LUNGS"]
    if "zns" in group_l or "gehirn" in group_l: return NLS3D_POINTS["ORGAN_BRAIN"]

    # Chakren
    if "chakra" in group_l:
        if "wurzel" in label_l or "root" in label_l: return NLS3D_POINTS["CHAKRA_ROOT"]
        if "sakral" in label_l or "sacral" in label_l: return NLS3D_POINTS["CHAKRA_SACRAL"]
        if "solar" in label_l: return NLS3D_POINTS["CHAKRA_SOLAR"]
        if "herz" in label_l or "heart" in label_l: return NLS3D_POINTS["CHAKRA_HEART"]
        if "hals" in label_l or "throat" in label_l: return NLS3D_POINTS["CHAKRA_THROAT"]
        if "stirn" in label_l or "third" in label_l: return NLS3D_POINTS["CHAKRA_THIRD_EYE"]
        if "krone" in label_l or "crown" in label_l: return NLS3D_POINTS["CHAKRA_CROWN"]
        return NLS3D_POINTS["CHAKRA_HEART"] # Fallback Chakra

    # --- 2. Label-Analyse (Fallback oder Verfeinerung) ---

    # Organe im Text
    if "leber" in label_l: return NLS3D_POINTS["ORGAN_LIVER"]
    if "niere" in label_l: return NLS3D_POINTS["ORGAN_KIDNEY_L"]
    if "herz" in label_l: return NLS3D_POINTS["ORGAN_HEART"]
    if "lunge" in label_l: return NLS3D_POINTS["ORGAN_LUNGS"]
    if "magen" in label_l: return NLS3D_POINTS["ORGAN_STOMACH"]
    if "darm" in label_l or "colon" in label_l: return NLS3D_POINTS["ORGAN_INTESTINE"]
    if "gehirn" in label_l: return NLS3D_POINTS["ORGAN_BRAIN"]
    if "schilddruese" in label_l: return NLS3D_POINTS["ORGAN_THYROID"]
    if "blase" in label_l: return NLS3D_POINTS["ORGAN_BLADDER"]

    # Pathogene -> Systeme
    # Bakterien/Viren/Pilze mappen wir auf das Immunsystem (Thymus), 
    # damit man sieht "Aha, hier ist Belastung".
    if any(x in group_l for x in ["bakterien", "viren", "parasiten", "pilze"]):
        return NLS3D_POINTS["SYSTEM_IMMUNE"]
    
    if "tox" in group_l or "schwer" in group_l:
        return NLS3D_POINTS["SYSTEM_DETOX"]

    # --- 3. Wirbelsäulen-Feinjustierung ---
    if "hws" in label_l or "c1" in label_l or "c2" in label_l: return NLS3D_POINTS["SPINE_CERVICAL"]
    if "bws" in label_l or "th" in label_l: return NLS3D_POINTS["SPINE_THORACIC"]
    if "lws" in label_l or "l1" in label_l: return NLS3D_POINTS["SPINE_LUMBAR"]

    return None
'''

target_path = r"c:\Users\Hubert111\CascadeProjects\Radialgo2\Morphic_Engine_V1\core\nls3d_points.py"
with open(target_path, 'w') as f:
    f.write(NEW_CONTENT)

print(f"File overwritten: {target_path}")
