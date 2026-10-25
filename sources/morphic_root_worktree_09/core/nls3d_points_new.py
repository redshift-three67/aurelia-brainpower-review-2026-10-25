"""NLS 3D-Punkte: symbolisches Datenmodell fuer 3D-NLS-Exports.

Dieses Modul enthaelt keine Engine- oder DB-Logik. Es liefert nur
symbolische 3D-Punkte und ein einfaches Mapping von Items/Gruppen
auf logische 3D-Punkte fuer die *_3d_scan.json Exporte.
"""

from __future__ import annotations

import re
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

    # --- MERIDIANE (12 Hauptmeridiane) ---
    "MERIDIAN_LU": Nls3DPoint(id="MERIDIAN_LU", label="Lungenmeridian (LU)", layer="energetisch", coords=[-0.30, 0.25, 0.05], group_hint=["meridiane"]),
    "MERIDIAN_LI": Nls3DPoint(id="MERIDIAN_LI", label="Dickdarmmeridian (LI)", layer="energetisch", coords=[-0.35, 0.20, 0.08], group_hint=["meridiane"]),
    "MERIDIAN_ST": Nls3DPoint(id="MERIDIAN_ST", label="Magenmeridian (ST)", layer="energetisch", coords=[0.15, 0.05, 0.12], group_hint=["meridiane"]),
    "MERIDIAN_SP": Nls3DPoint(id="MERIDIAN_SP", label="Milzmeridian (SP)", layer="energetisch", coords=[0.20, -0.05, 0.08], group_hint=["meridiane"]),
    "MERIDIAN_HE": Nls3DPoint(id="MERIDIAN_HE", label="Herzmeridian (HE)", layer="energetisch", coords=[0.30, 0.18, 0.05], group_hint=["meridiane"]),
    "MERIDIAN_SI": Nls3DPoint(id="MERIDIAN_SI", label="Duenndarmmeridian (SI)", layer="energetisch", coords=[0.35, 0.15, 0.0], group_hint=["meridiane"]),
    "MERIDIAN_BL": Nls3DPoint(id="MERIDIAN_BL", label="Blasenmeridian (BL)", layer="energetisch", coords=[0.08, 0.10, -0.15], group_hint=["meridiane"]),
    "MERIDIAN_KI": Nls3DPoint(id="MERIDIAN_KI", label="Nierenmeridian (KI)", layer="energetisch", coords=[0.12, -0.25, 0.05], group_hint=["meridiane"]),
    "MERIDIAN_PC": Nls3DPoint(id="MERIDIAN_PC", label="Perikardmeridian (PC)", layer="energetisch", coords=[0.28, 0.20, 0.08], group_hint=["meridiane"]),
    "MERIDIAN_TE": Nls3DPoint(id="MERIDIAN_TE", label="Dreifacher Erwaermer (TE)", layer="energetisch", coords=[-0.32, 0.22, 0.0], group_hint=["meridiane"]),
    "MERIDIAN_GB": Nls3DPoint(id="MERIDIAN_GB", label="Gallenblasenmeridian (GB)", layer="energetisch", coords=[-0.18, 0.08, 0.10], group_hint=["meridiane"]),
    "MERIDIAN_LV": Nls3DPoint(id="MERIDIAN_LV", label="Lebermeridian (LV)", layer="energetisch", coords=[0.18, -0.10, 0.08], group_hint=["meridiane"]),

    # --- SONDERMERIDIANE (8 Extraordinaere Gefaesse) ---
    "MERIDIAN_DU": Nls3DPoint(id="MERIDIAN_DU", label="Du Mai (Lenkergefaess)", layer="energetisch", coords=[0.0, 0.20, -0.12], group_hint=["meridiane", "sondermeridiane"]),
    "MERIDIAN_REN": Nls3DPoint(id="MERIDIAN_REN", label="Ren Mai (Konzeptionsgefaess)", layer="energetisch", coords=[0.0, 0.10, 0.12], group_hint=["meridiane", "sondermeridiane"]),
    "MERIDIAN_CHONG": Nls3DPoint(id="MERIDIAN_CHONG", label="Chong Mai (Meer des Blutes)", layer="energetisch", coords=[0.0, -0.05, 0.08], group_hint=["meridiane", "sondermeridiane"]),
    "MERIDIAN_DAI": Nls3DPoint(id="MERIDIAN_DAI", label="Dai Mai (Guertelgefaess)", layer="energetisch", coords=[0.0, -0.02, 0.0], group_hint=["meridiane", "sondermeridiane"]),
    "MERIDIAN_YINQIAO": Nls3DPoint(id="MERIDIAN_YINQIAO", label="Yin Qiao Mai", layer="energetisch", coords=[0.10, -0.35, 0.05], group_hint=["meridiane", "sondermeridiane"]),
    "MERIDIAN_YANGQIAO": Nls3DPoint(id="MERIDIAN_YANGQIAO", label="Yang Qiao Mai", layer="energetisch", coords=[-0.10, -0.35, -0.05], group_hint=["meridiane", "sondermeridiane"]),
    "MERIDIAN_YINWEI": Nls3DPoint(id="MERIDIAN_YINWEI", label="Yin Wei Mai", layer="energetisch", coords=[0.15, 0.00, 0.10], group_hint=["meridiane", "sondermeridiane"]),
    "MERIDIAN_YANGWEI": Nls3DPoint(id="MERIDIAN_YANGWEI", label="Yang Wei Mai", layer="energetisch", coords=[-0.15, 0.00, -0.10], group_hint=["meridiane", "sondermeridiane"]),

    # --- EMF-ZONEN (Elektromagnetische Belastungszonen) ---
    "EMF_HEAD": Nls3DPoint(id="EMF_HEAD", label="EMF Kopfbereich", layer="emf", coords=[0.0, 0.50, 0.05], group_hint=["emf", "strahlung"]),
    "EMF_THYROID": Nls3DPoint(id="EMF_THYROID", label="EMF Schilddruese (5G)", layer="emf", coords=[0.0, 0.32, 0.06], group_hint=["emf", "strahlung"]),
    "EMF_HEART": Nls3DPoint(id="EMF_HEART", label="EMF Herzbereich", layer="emf", coords=[0.05, 0.18, 0.08], group_hint=["emf", "strahlung"]),
    "EMF_PINEAL": Nls3DPoint(id="EMF_PINEAL", label="EMF Zirbeldruese", layer="emf", coords=[0.0, 0.48, -0.02], group_hint=["emf", "strahlung"]),
    "EMF_GONADS": Nls3DPoint(id="EMF_GONADS", label="EMF Genitalbereich", layer="emf", coords=[0.0, -0.30, 0.08], group_hint=["emf", "strahlung"]),
    "EMF_SPINE": Nls3DPoint(id="EMF_SPINE", label="EMF Wirbelsaeule", layer="emf", coords=[0.0, 0.05, -0.10], group_hint=["emf", "strahlung"]),

    # --- ZAEHNE (FDI-Schema: Quadrant + Zahn) ---
    # Oberkiefer rechts (1x)
    "TOOTH_11": Nls3DPoint(id="TOOTH_11", label="Zahn 11 (OK re Schneidezahn 1)", layer="dental", coords=[-0.02, 0.42, 0.12], group_hint=["zaehne", "odontone"]),
    "TOOTH_12": Nls3DPoint(id="TOOTH_12", label="Zahn 12 (OK re Schneidezahn 2)", layer="dental", coords=[-0.04, 0.42, 0.11], group_hint=["zaehne", "odontone"]),
    "TOOTH_13": Nls3DPoint(id="TOOTH_13", label="Zahn 13 (OK re Eckzahn)", layer="dental", coords=[-0.06, 0.42, 0.10], group_hint=["zaehne", "odontone"]),
    "TOOTH_14": Nls3DPoint(id="TOOTH_14", label="Zahn 14 (OK re Praemolar 1)", layer="dental", coords=[-0.08, 0.41, 0.08], group_hint=["zaehne", "odontone"]),
    "TOOTH_15": Nls3DPoint(id="TOOTH_15", label="Zahn 15 (OK re Praemolar 2)", layer="dental", coords=[-0.10, 0.41, 0.06], group_hint=["zaehne", "odontone"]),
    "TOOTH_16": Nls3DPoint(id="TOOTH_16", label="Zahn 16 (OK re Molar 1)", layer="dental", coords=[-0.12, 0.40, 0.04], group_hint=["zaehne", "odontone"]),
    "TOOTH_17": Nls3DPoint(id="TOOTH_17", label="Zahn 17 (OK re Molar 2)", layer="dental", coords=[-0.14, 0.40, 0.02], group_hint=["zaehne", "odontone"]),
    "TOOTH_18": Nls3DPoint(id="TOOTH_18", label="Zahn 18 (OK re Weisheitszahn)", layer="dental", coords=[-0.16, 0.39, 0.0], group_hint=["zaehne", "odontone"]),
    # Oberkiefer links (2x)
    "TOOTH_21": Nls3DPoint(id="TOOTH_21", label="Zahn 21 (OK li Schneidezahn 1)", layer="dental", coords=[0.02, 0.42, 0.12], group_hint=["zaehne", "odontone"]),
    "TOOTH_22": Nls3DPoint(id="TOOTH_22", label="Zahn 22 (OK li Schneidezahn 2)", layer="dental", coords=[0.04, 0.42, 0.11], group_hint=["zaehne", "odontone"]),
    "TOOTH_23": Nls3DPoint(id="TOOTH_23", label="Zahn 23 (OK li Eckzahn)", layer="dental", coords=[0.06, 0.42, 0.10], group_hint=["zaehne", "odontone"]),
    "TOOTH_24": Nls3DPoint(id="TOOTH_24", label="Zahn 24 (OK li Praemolar 1)", layer="dental", coords=[0.08, 0.41, 0.08], group_hint=["zaehne", "odontone"]),
    "TOOTH_25": Nls3DPoint(id="TOOTH_25", label="Zahn 25 (OK li Praemolar 2)", layer="dental", coords=[0.10, 0.41, 0.06], group_hint=["zaehne", "odontone"]),
    "TOOTH_26": Nls3DPoint(id="TOOTH_26", label="Zahn 26 (OK li Molar 1)", layer="dental", coords=[0.12, 0.40, 0.04], group_hint=["zaehne", "odontone"]),
    "TOOTH_27": Nls3DPoint(id="TOOTH_27", label="Zahn 27 (OK li Molar 2)", layer="dental", coords=[0.14, 0.40, 0.02], group_hint=["zaehne", "odontone"]),
    "TOOTH_28": Nls3DPoint(id="TOOTH_28", label="Zahn 28 (OK li Weisheitszahn)", layer="dental", coords=[0.16, 0.39, 0.0], group_hint=["zaehne", "odontone"]),
    # Unterkiefer links (3x)
    "TOOTH_31": Nls3DPoint(id="TOOTH_31", label="Zahn 31 (UK li Schneidezahn 1)", layer="dental", coords=[0.02, 0.38, 0.12], group_hint=["zaehne", "odontone"]),
    "TOOTH_32": Nls3DPoint(id="TOOTH_32", label="Zahn 32 (UK li Schneidezahn 2)", layer="dental", coords=[0.04, 0.38, 0.11], group_hint=["zaehne", "odontone"]),
    "TOOTH_33": Nls3DPoint(id="TOOTH_33", label="Zahn 33 (UK li Eckzahn)", layer="dental", coords=[0.06, 0.38, 0.10], group_hint=["zaehne", "odontone"]),
    "TOOTH_34": Nls3DPoint(id="TOOTH_34", label="Zahn 34 (UK li Praemolar 1)", layer="dental", coords=[0.08, 0.37, 0.08], group_hint=["zaehne", "odontone"]),
    "TOOTH_35": Nls3DPoint(id="TOOTH_35", label="Zahn 35 (UK li Praemolar 2)", layer="dental", coords=[0.10, 0.37, 0.06], group_hint=["zaehne", "odontone"]),
    "TOOTH_36": Nls3DPoint(id="TOOTH_36", label="Zahn 36 (UK li Molar 1)", layer="dental", coords=[0.12, 0.36, 0.04], group_hint=["zaehne", "odontone"]),
    "TOOTH_37": Nls3DPoint(id="TOOTH_37", label="Zahn 37 (UK li Molar 2)", layer="dental", coords=[0.14, 0.36, 0.02], group_hint=["zaehne", "odontone"]),
    "TOOTH_38": Nls3DPoint(id="TOOTH_38", label="Zahn 38 (UK li Weisheitszahn)", layer="dental", coords=[0.16, 0.35, 0.0], group_hint=["zaehne", "odontone"]),
    # Unterkiefer rechts (4x)
    "TOOTH_41": Nls3DPoint(id="TOOTH_41", label="Zahn 41 (UK re Schneidezahn 1)", layer="dental", coords=[-0.02, 0.38, 0.12], group_hint=["zaehne", "odontone"]),
    "TOOTH_42": Nls3DPoint(id="TOOTH_42", label="Zahn 42 (UK re Schneidezahn 2)", layer="dental", coords=[-0.04, 0.38, 0.11], group_hint=["zaehne", "odontone"]),
    "TOOTH_43": Nls3DPoint(id="TOOTH_43", label="Zahn 43 (UK re Eckzahn)", layer="dental", coords=[-0.06, 0.38, 0.10], group_hint=["zaehne", "odontone"]),
    "TOOTH_44": Nls3DPoint(id="TOOTH_44", label="Zahn 44 (UK re Praemolar 1)", layer="dental", coords=[-0.08, 0.37, 0.08], group_hint=["zaehne", "odontone"]),
    "TOOTH_45": Nls3DPoint(id="TOOTH_45", label="Zahn 45 (UK re Praemolar 2)", layer="dental", coords=[-0.10, 0.37, 0.06], group_hint=["zaehne", "odontone"]),
    "TOOTH_46": Nls3DPoint(id="TOOTH_46", label="Zahn 46 (UK re Molar 1)", layer="dental", coords=[-0.12, 0.36, 0.04], group_hint=["zaehne", "odontone"]),
    "TOOTH_47": Nls3DPoint(id="TOOTH_47", label="Zahn 47 (UK re Molar 2)", layer="dental", coords=[-0.14, 0.36, 0.02], group_hint=["zaehne", "odontone"]),
    "TOOTH_48": Nls3DPoint(id="TOOTH_48", label="Zahn 48 (UK re Weisheitszahn)", layer="dental", coords=[-0.16, 0.35, 0.0], group_hint=["zaehne", "odontone"]),

    # --- KIEFERGELENK ---
    "JAW_TMJ_L": Nls3DPoint(id="JAW_TMJ_L", label="Kiefergelenk links (TMJ)", layer="dental", coords=[0.12, 0.42, 0.02], group_hint=["kiefer", "zaehne"]),
    "JAW_TMJ_R": Nls3DPoint(id="JAW_TMJ_R", label="Kiefergelenk rechts (TMJ)", layer="dental", coords=[-0.12, 0.42, 0.02], group_hint=["kiefer", "zaehne"]),
    "JAW_MANDIBLE": Nls3DPoint(id="JAW_MANDIBLE", label="Unterkiefer (Mandibula)", layer="dental", coords=[0.0, 0.36, 0.10], group_hint=["kiefer", "zaehne"]),
    "JAW_MAXILLA": Nls3DPoint(id="JAW_MAXILLA", label="Oberkiefer (Maxilla)", layer="dental", coords=[0.0, 0.41, 0.10], group_hint=["kiefer", "zaehne"]),
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

    # --- 4. Meridiane (12 Haupt + 8 Sonder) ---
    if "meridian" in group_l or "meridian" in label_l:
        # Hauptmeridiane
        if "lunge" in label_l or "lu " in label_l or "lu1" in label_l: return NLS3D_POINTS["MERIDIAN_LU"]
        if "dickdarm" in label_l or "li " in label_l or "li4" in label_l: return NLS3D_POINTS["MERIDIAN_LI"]
        if "magen" in label_l or "st " in label_l or "st36" in label_l: return NLS3D_POINTS["MERIDIAN_ST"]
        if "milz" in label_l or "sp " in label_l or "sp6" in label_l: return NLS3D_POINTS["MERIDIAN_SP"]
        if "herz" in label_l or "he " in label_l or "ht7" in label_l: return NLS3D_POINTS["MERIDIAN_HE"]
        if "duenndarm" in label_l or "si " in label_l: return NLS3D_POINTS["MERIDIAN_SI"]
        if "blase" in label_l or "bl " in label_l: return NLS3D_POINTS["MERIDIAN_BL"]
        if "niere" in label_l or "ki " in label_l or "ki3" in label_l: return NLS3D_POINTS["MERIDIAN_KI"]
        if "perikard" in label_l or "pc " in label_l or "pc6" in label_l: return NLS3D_POINTS["MERIDIAN_PC"]
        if "dreifach" in label_l or "te " in label_l or "sanjiao" in label_l: return NLS3D_POINTS["MERIDIAN_TE"]
        if "gallenblase" in label_l or "gb " in label_l or "gb20" in label_l: return NLS3D_POINTS["MERIDIAN_GB"]
        if "leber" in label_l or "lv " in label_l or "lv3" in label_l: return NLS3D_POINTS["MERIDIAN_LV"]
        # Sondermeridiane
        if "du mai" in label_l or "lenker" in label_l or "governor" in label_l: return NLS3D_POINTS["MERIDIAN_DU"]
        if "ren mai" in label_l or "konzeption" in label_l or "conception" in label_l: return NLS3D_POINTS["MERIDIAN_REN"]
        if "chong" in label_l: return NLS3D_POINTS["MERIDIAN_CHONG"]
        if "dai mai" in label_l or "guertel" in label_l: return NLS3D_POINTS["MERIDIAN_DAI"]
        if "yin qiao" in label_l: return NLS3D_POINTS["MERIDIAN_YINQIAO"]
        if "yang qiao" in label_l: return NLS3D_POINTS["MERIDIAN_YANGQIAO"]
        if "yin wei" in label_l: return NLS3D_POINTS["MERIDIAN_YINWEI"]
        if "yang wei" in label_l: return NLS3D_POINTS["MERIDIAN_YANGWEI"]
        return NLS3D_POINTS["MERIDIAN_HE"]  # Fallback: Herzmeridian

    # --- 5. EMF-Zonen ---
    if "emf" in group_l or "strahlung" in group_l or "elektrosmog" in label_l:
        if "kopf" in label_l or "head" in label_l or "wlan" in label_l or "handy" in label_l: return NLS3D_POINTS["EMF_HEAD"]
        if "schilddruese" in label_l or "5g" in label_l: return NLS3D_POINTS["EMF_THYROID"]
        if "herz" in label_l or "heart" in label_l: return NLS3D_POINTS["EMF_HEART"]
        if "zirbel" in label_l or "pineal" in label_l or "melatonin" in label_l: return NLS3D_POINTS["EMF_PINEAL"]
        if "genital" in label_l or "hoden" in label_l or "ovar" in label_l: return NLS3D_POINTS["EMF_GONADS"]
        if "wirbel" in label_l or "spine" in label_l: return NLS3D_POINTS["EMF_SPINE"]
        return NLS3D_POINTS["EMF_HEAD"]  # Fallback: Kopfbereich

    # --- 6. Zähne (FDI-Schema) ---
    if "zahn" in group_l or "odonton" in group_l or "dental" in group_l:
        # Versuche Zahnnummer aus Label zu extrahieren
        match = re.search(r'\b([1-4][1-8])\b', label_l)
        if match:
            tooth_key = f"TOOTH_{match.group(1)}"
            if tooth_key in NLS3D_POINTS:
                return NLS3D_POINTS[tooth_key]
        # Fallback auf Quadranten
        if "oberkiefer" in label_l or "maxilla" in label_l: return NLS3D_POINTS["JAW_MAXILLA"]
        if "unterkiefer" in label_l or "mandibula" in label_l: return NLS3D_POINTS["JAW_MANDIBLE"]
        return NLS3D_POINTS["TOOTH_11"]  # Fallback: erster Schneidezahn

    # --- 7. Kiefergelenk ---
    if "kiefer" in group_l or "tmj" in label_l or "kiefergelenk" in label_l:
        if "links" in label_l or "left" in label_l: return NLS3D_POINTS["JAW_TMJ_L"]
        if "rechts" in label_l or "right" in label_l: return NLS3D_POINTS["JAW_TMJ_R"]
        return NLS3D_POINTS["JAW_TMJ_L"]  # Fallback

    return None
