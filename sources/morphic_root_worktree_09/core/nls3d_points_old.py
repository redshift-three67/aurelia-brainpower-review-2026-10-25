"""NLS 3D-Punkte: symbolisches Datenmodell fuer 3D-NLS-Exports.

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
    """

    id: str
    label: str
    layer: str
    coords: List[float]
    group_hint: List[str]


# Symbolische Punktdefinitionen fuer zentrale Koerperachsen und Ebenen.
# Diese Koordinaten sind bewusst vereinfacht und dienen nur der
# spaeteren Verknuepfung mit echten 3D-Modellen.
NLS3D_POINTS: Dict[str, Nls3DPoint] = {
    # Wirbelsaeule – aggregierte Bereiche
    "SPINE_CERVICAL": Nls3DPoint(
        id="SPINE_CERVICAL",
        label="Halswirbelsaeule (C0-C7)",
        layer="physisch",
        coords=[0.0, 0.35, 0.0],
        group_hint=[
            "wirbelsaeule_hws",
            "wirbelsaeule_fein",
            "wirbelsaeule_bandscheiben_fein",
        ],
    ),
    "SPINE_THORACIC": Nls3DPoint(
        id="SPINE_THORACIC",
        label="Brustwirbelsaeule (Th1-Th12)",
        layer="physisch",
        coords=[0.0, 0.15, 0.0],
        group_hint=[
            "wirbelsaeule_bws",
            "wirbelsaeule_fein",
            "wirbelsaeule_bandscheiben_fein",
        ],
    ),
    "SPINE_LUMBAR": Nls3DPoint(
        id="SPINE_LUMBAR",
        label="Lendenwirbelsaeule (L1-L5)",
        layer="physisch",
        coords=[0.0, -0.05, 0.0],
        group_hint=[
            "wirbelsaeule_lws",
            "wirbelsaeule_fein",
            "wirbelsaeule_bandscheiben_fein",
        ],
    ),
    "SPINE_SACRAL": Nls3DPoint(
        id="SPINE_SACRAL",
        label="Kreuzbein / Sakralbereich",
        layer="physisch",
        coords=[0.0, -0.25, 0.0],
        group_hint=["wirbelsaeule_sakral"],
    ),
    "SPINE_CERVICAL_UPPER": Nls3DPoint(
        id="SPINE_CERVICAL_UPPER",
        label="Halswirbelsaeule (C0-C2, oberer Anteil)",
        layer="physisch",
        coords=[0.0, 0.4, 0.0],
        group_hint=[
            "wirbelsaeule_hws",
            "wirbelsaeule_fein",
            "wirbelsaeule_bandscheiben_fein",
        ],
    ),
    "SPINE_CERVICAL_LOWER": Nls3DPoint(
        id="SPINE_CERVICAL_LOWER",
        label="Halswirbelsaeule (C3-C7, unterer Anteil)",
        layer="physisch",
        coords=[0.0, 0.3, 0.0],
        group_hint=[
            "wirbelsaeule_hws",
            "wirbelsaeule_fein",
            "wirbelsaeule_bandscheiben_fein",
        ],
    ),
    "SPINE_THORACIC_UPPER": Nls3DPoint(
        id="SPINE_THORACIC_UPPER",
        label="Brustwirbelsaeule (Th1-Th4, oberer Anteil)",
        layer="physisch",
        coords=[0.0, 0.2, 0.0],
        group_hint=[
            "wirbelsaeule_bws",
            "wirbelsaeule_fein",
            "wirbelsaeule_bandscheiben_fein",
        ],
    ),
    "SPINE_THORACIC_MID": Nls3DPoint(
        id="SPINE_THORACIC_MID",
        label="Brustwirbelsaeule (Th5-Th8, mittlerer Anteil)",
        layer="physisch",
        coords=[0.0, 0.15, 0.0],
        group_hint=[
            "wirbelsaeule_bws",
            "wirbelsaeule_fein",
            "wirbelsaeule_bandscheiben_fein",
        ],
    ),
    "SPINE_THORACIC_LOWER": Nls3DPoint(
        id="SPINE_THORACIC_LOWER",
        label="Brustwirbelsaeule (Th9-Th12, unterer Anteil)",
        layer="physisch",
        coords=[0.0, 0.1, 0.0],
        group_hint=[
            "wirbelsaeule_bws",
            "wirbelsaeule_fein",
            "wirbelsaeule_bandscheiben_fein",
        ],
    ),
    "SPINE_LUMBAR_UPPER": Nls3DPoint(
        id="SPINE_LUMBAR_UPPER",
        label="Lendenwirbelsaeule (L1-L3, oberer Anteil)",
        layer="physisch",
        coords=[0.0, 0.0, 0.0],
        group_hint=[
            "wirbelsaeule_lws",
            "wirbelsaeule_fein",
            "wirbelsaeule_bandscheiben_fein",
        ],
    ),
    "SPINE_LUMBAR_LOWER": Nls3DPoint(
        id="SPINE_LUMBAR_LOWER",
        label="Lendenwirbelsaeule (L4-L5, unterer Anteil)",
        layer="physisch",
        coords=[0.0, -0.1, 0.0],
        group_hint=[
            "wirbelsaeule_lws",
            "wirbelsaeule_fein",
            "wirbelsaeule_bandscheiben_fein",
        ],
    ),
    # Meridiane – vereinfachte Hauptachsen
    "MERIDIAN_LU": Nls3DPoint(
        id="MERIDIAN_LU",
        label="Lungenmeridian (LU)",
        layer="energetisch",
        coords=[-0.15, 0.15, 0.0],
        group_hint=["meridiane", "meridiane_detailliert_fein"],
    ),
    "MERIDIAN_HE": Nls3DPoint(
        id="MERIDIAN_HE",
        label="Herzmeridian (HE)",
        layer="energetisch",
        coords=[0.1, 0.2, 0.0],
        group_hint=["meridiane", "meridiane_detailliert_fein"],
    ),
    "MERIDIAN_KI": Nls3DPoint(
        id="MERIDIAN_KI",
        label="Nierenmeridian (KI)",
        layer="energetisch",
        coords=[-0.1, -0.15, 0.0],
        group_hint=["meridiane", "meridiane_detailliert_fein"],
    ),
    "MERIDIAN_BL": Nls3DPoint(
        id="MERIDIAN_BL",
        label="Blasenmeridian (BL)",
        layer="energetisch",
        coords=[0.0, 0.0, -0.1],
        group_hint=["meridiane", "meridiane_detailliert_fein"],
    ),
    # Chakren – grobe vertikale Achse
    "CHAKRA_ROOT": Nls3DPoint(
        id="CHAKRA_ROOT",
        label="Wurzelchakra",
        layer="energetisch",
        coords=[0.0, -0.3, 0.0],
        group_hint=["chakren", "chakren_fein"],
    ),
    "CHAKRA_SOLAR": Nls3DPoint(
        id="CHAKRA_SOLAR",
        label="Solarplexus-Chakra",
        layer="energetisch",
        coords=[0.0, -0.05, 0.05],
        group_hint=["chakren", "chakren_fein"],
    ),
    "CHAKRA_HEART": Nls3DPoint(
        id="CHAKRA_HEART",
        label="Herzchakra",
        layer="energetisch",
        coords=[0.0, 0.1, 0.08],
        group_hint=["chakren", "chakren_fein"],
    ),
    "CHAKRA_THROAT": Nls3DPoint(
        id="CHAKRA_THROAT",
        label="Halschakra",
        layer="energetisch",
        coords=[0.0, 0.25, 0.05],
        group_hint=["chakren", "chakren_fein"],
    ),
    "CHAKRA_THIRD_EYE": Nls3DPoint(
        id="CHAKRA_THIRD_EYE",
        label="Stirnchakra / Drittes Auge",
        layer="energetisch",
        coords=[0.0, 0.35, 0.08],
        group_hint=["chakren", "chakren_fein"],
    ),
    "CHAKRA_CROWN": Nls3DPoint(
        id="CHAKRA_CROWN",
        label="Kronenchakra",
        layer="energetisch",
        coords=[0.0, 0.45, 0.0],
        group_hint=["chakren", "chakren_fein"],
    ),
}


def map_item_to_point(label: str, group: Optional[str] = None) -> Optional[str]:
    """Einfache Heuristik, um einen Item-Label/Group auf einen 3D-Punkt zu mappen.

    Diese Funktion ist bewusst konservativ: Sie gibt None zurueck, wenn
    kein plausibler Punkt gefunden wird. So bleibt das Mapping rein
    additiv und beeinflusst keine bestehende Engine-Logik.
    """

    label_l = (label or "").lower()
    group_l = (group or "").lower()

    is_spine_context = (
        group_l.startswith("wirbelsaeule")
        or "wirbel" in label_l
        or "bandscheib" in label_l
        or "hws" in label_l
        or "bws" in label_l
        or "lws" in label_l
    )

    if is_spine_context:
        if any(t in label_l for t in ("c1", "c2")):
            return "SPINE_CERVICAL_UPPER"
        if any(t in label_l for t in ("c3", "c4", "c5", "c6", "c7")):
            return "SPINE_CERVICAL_LOWER"
        if any(t in label_l for t in ("th1", "th2", "th3", "th4")):
            return "SPINE_THORACIC_UPPER"
        if any(t in label_l for t in ("th5", "th6", "th7", "th8")):
            return "SPINE_THORACIC_MID"
        if any(t in label_l for t in ("th9", "th10", "th11", "th12")):
            return "SPINE_THORACIC_LOWER"
        if any(t in label_l for t in ("l1", "l2", "l3")):
            return "SPINE_LUMBAR_UPPER"
        if any(t in label_l for t in ("l4", "l5")):
            return "SPINE_LUMBAR_LOWER"

    # Wirbelsaeule nach Gruppenname
    if group_l.startswith("wirbelsaeule_hws"):
        return "SPINE_CERVICAL"
    if group_l.startswith("wirbelsaeule_bws"):
        return "SPINE_THORACIC"
    if group_l.startswith("wirbelsaeule_lws"):
        return "SPINE_LUMBAR"
    if group_l.startswith("wirbelsaeule_sakral"):
        return "SPINE_SACRAL"

    # Wirbelsaeule nach Label-Text (Fallback, falls Gruppe fehlt)
    if "hws" in label_l or "halswirbel" in label_l:
        return "SPINE_CERVICAL"
    if "bws" in label_l or "brustwirbel" in label_l:
        return "SPINE_THORACIC"
    if "lws" in label_l or "lendenwirbel" in label_l:
        return "SPINE_LUMBAR"
    if "sakral" in label_l or "sakrum" in label_l or "kreuzbein" in label_l:
        return "SPINE_SACRAL"

    # Meridiane – einfache Zuordnung nach Label/Gruppe
    if "meridian" in label_l or group_l.startswith("meridiane"):
        combined = f"{label or ''} {group or ''}".upper()
        prefixes = (
            "LU",
            "HE",
            "KI",
            "BL",
            "ST",
            "SP",
            "GB",
            "LI",
            "SI",
            "PC",
            "SJ",
            "TB",
            "REN",
            "DU",
        )
        for prefix in prefixes:
            idx = combined.find(prefix)
            while idx != -1:
                j = idx + len(prefix)
                digits = []
                while j < len(combined) and combined[j].isdigit():
                    digits.append(combined[j])
                    j += 1
                if digits:
                    code = prefix + "".join(digits)
                    return code
                idx = combined.find(prefix, idx + 1)
        if "lu" in label_l or "lunge" in label_l:
            return "MERIDIAN_LU"
        if "he" in label_l or "herz" in label_l:
            return "MERIDIAN_HE"
        if "ki" in label_l or "niere" in label_l:
            return "MERIDIAN_KI"
        if "bl" in label_l or "blase" in label_l:
            return "MERIDIAN_BL"

    # Chakren
    if "chakra" in label_l or group_l.startswith("chakren"):
        if "wurzel" in label_l or "root" in label_l:
            return "CHAKRA_ROOT"
        if "solar" in label_l:
            return "CHAKRA_SOLAR"
        if "herz" in label_l or "heart" in label_l:
            return "CHAKRA_HEART"
        if "hals" in label_l or "throat" in label_l:
            return "CHAKRA_THROAT"
        if "stirn" in label_l or "third eye" in label_l:
            return "CHAKRA_THIRD_EYE"
        if "krone" in label_l or "crown" in label_l:
            return "CHAKRA_CROWN"

    return None
