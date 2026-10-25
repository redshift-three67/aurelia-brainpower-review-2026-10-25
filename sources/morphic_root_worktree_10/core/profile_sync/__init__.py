# -*- coding: utf-8 -*-
"""
ZENTRALE PROFIL-SYNCHRONISIERUNG - Morphic Engine V1
=====================================================
Erstellt: 01.12.2025

ZWECK:
Diese Datei ist die EINZIGE QUELLE DER WAHRHEIT für alle Profile.
Alle anderen Stellen (main.py, registry.py) müssen diese Datei importieren.

REGELN:
1. Neue Profile NUR hier hinzufügen
2. Profile löschen NUR hier
3. Gruppen-Zuordnungen NUR hier ändern
4. Aliase für Namens-Kompatibilität hier definieren
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


@dataclass
class ProfileDefinition:
    """Definition eines Analyse-Profils.

    Level-System (Version M):
        Level 1: Basis-Profile (5) - Schnellscan
        Level 2: Standard-Profile (35) - Bisheriger Standard
        Level 3: Erweitert (55) - Version K mit BAT/Frequenz
        Level 4: Komplett (100+) - Alle Fein-Profile
    """

    name: str  # Interner Name (z.B. "niere_detailliert")
    display_name: str  # Anzeigename (z.B. "Niere & Harnwege")
    groups: List[str]  # Zugeordnete Gruppen
    category: str  # Kategorie (organ, symptom, toxin, etc.)
    level: int = 2  # NEU: Level 1-4 (Standard: 2)
    aliases: List[str] = None  # Alternative Namen für Kompatibilität
    enabled: bool = True  # Aktiv/Inaktiv


# =============================================================================
# MASTER PROFIL-DEFINITIONEN
# =============================================================================
# WICHTIG: Dies ist die EINZIGE Stelle, an der Profile definiert werden!
# =============================================================================

MASTER_PROFILES: Dict[str, ProfileDefinition] = {}


def _register(
    name: str,
    display: str,
    groups: List[str],
    category: str,
    level: int = 2,  # NEU: Level 1-4
    aliases: List[str] = None,
    enabled: bool = True,
):
    """Registriert ein Profil im Master-Register.

    Args:
        name: Interner Profilname
        display: Anzeigename
        groups: Liste der zugeordneten Gruppen
        category: Kategorie (basis, organ, bat, etc.)
        level: Hierarchie-Level 1-4 (Standard: 2)
        aliases: Alternative Namen
        enabled: Aktiv/Inaktiv
    """
    MASTER_PROFILES[name] = ProfileDefinition(
        name=name,
        display_name=display,
        groups=groups,
        category=category,
        level=level,
        aliases=aliases or [],
        enabled=enabled,
    )
    # Aliase auch registrieren (zeigen auf das gleiche Profil)
    if aliases:
        for alias in aliases:
            MASTER_PROFILES[alias] = MASTER_PROFILES[name]


# =============================================================================
# KATEGORIE: BASIS-DIAGNOSE
# =============================================================================

_register(
    name="pathogen",
    display="Pathogene Erreger (Bakterien, Viren, Parasiten, Pilze)",
    category="basis",
    level=1,  # Basis-Profil für Schnellscan
    groups=[
        "bakterien",
        "viren",
        "parasiten",
        "pilze",
        "bakterien_fein",
        "viren_fein",
        "parasiten_fein",
        "pilze_fein",
        "bakterien_detailliert_fein",
        "viren_detailliert_fein",
        "parasiten_detailliert_fein",
        "pilze_detailliert_fein",
        "biofilme_fein",
        "infektions_symptome_fein",
        "immunsystem_angeboren_fein",
        "immunsystem_erworben_fein",
        "immunstaerkung_remedies_multiplex",
        "heel_remedies_multiplex",
        "nutramedix_remedies_multiplex",
        "oorep_homeopathy_multiplex",
    ],
)

_register(
    name="toxin",
    display="Toxine & Umweltbelastungen",
    category="basis",
    level=1,  # Basis-Profil für Schnellscan
    groups=[
        "schwermetalle",
        "schwermetalle_tox",
        "schwermetalle_detailliert_fein",
        "chemikalien_tox",
        "chemikalien_detailliert_fein",
        "pestizide_tox",
        "strahlung_tox",
        "strahlung_quellen_fein",
        "strahlung_symptome_fein",
        "emf_fein",
        "geopathie",
        "geopathie_fein",
        "umweltbelastungen_erweitert_fein",
        "wohnraumgifte_fein",
        "toxine_symptome_fein",
        "toxine_remedies_multiplex",
        "entgiftung_leber_phase1_fein",
        "entgiftung_leber_phase2_fein",
        "entgiftung_remedies_multiplex",
        "heel_remedies_multiplex",
        "nutramedix_remedies_multiplex",
        "oorep_homeopathy_multiplex",
    ],
)

_register(
    name="immune",
    display="Immunsystem",
    category="basis",
    level=1,  # Basis-Profil für Schnellscan
    groups=[
        "immunsystem_angeboren",
        "immunsystem_angeboren_fein",
        "immunsystem_erworben",
        "immunsystem_erworben_fein",
        "immunsystem_autoimmun_fein",
        "immunsystem_zytokine_fein",
        "entzuendung",
        "lymphsystem",
        "immunstaerkung_remedies_multiplex",
        "heel_remedies_multiplex",
        "nutramedix_remedies_multiplex",
    ],
)

_register(
    name="detox",
    display="Entgiftung",
    category="basis",
    level=1,  # Basis-Profil für Schnellscan
    groups=[
        "entgiftung_leber",
        "entgiftung_leber_phase1",
        "entgiftung_leber_phase1_fein",
        "entgiftung_leber_phase2",
        "entgiftung_leber_phase2_fein",
        "entgiftung_leber_phase3",
        "entgiftung_leber_phase3_fein",
        "entgiftung_niere",
        "entgiftung_darm",
        "entgiftung_haut",
        "entgiftung_lymphe",
        "entgiftung_organe_fein",
        "entgiftung_symptome_fein",
        "entgiftung_remedies_multiplex",
        "heel_remedies_multiplex",
        "nutramedix_remedies_multiplex",
    ],
)

_register(
    name="regulation",
    display="Energetische Regulation",
    category="basis",
    level=1,  # Basis-Profil für Schnellscan
    groups=[
        "chakren",
        "chakren_full",
        "chakren_detailliert_fein",
        "chakren_erweitert",
        "nebenchakren",
        "energetische_blockaden_fein",
        "meridiane",
        "meridiane_detailliert_fein",
        "tcm_punkte",
        "tcm_punkte_extended",
        "tcm_full",
        "extra_meridiane",
        "zahnorgane",
        "odontone",
        "nervensystem_vegetativ",
        "nervensystem_neurotransmitter_fein",
        "mikrozirkulation",
        "mitochondrien",
        "entzuendung",
        "endokrin",
        "hormone_symptome_fein",
        "heel_remedies_multiplex",
        "nutramedix_remedies_multiplex",
        "oorep_homeopathy_multiplex",
    ],
)

# =============================================================================
# KATEGORIE: ORGAN-SPEZIFISCH
# =============================================================================

_register(
    name="verdauung_detailliert",
    display="Verdauungssystem",
    category="organ",
    groups=[
        "verdauung_magen",
        "verdauung_duenndarm",
        "verdauung_dickdarm",
        "verdauung_mikrobiom",
        "verdauung_barriere",
        "verdauung_duenndarm_fein",
        "verdauung_dickdarm_fein",
        "verdauung_mikrobiom_fein",
        "verdauung_symptome_fein",
        "verdauung_pathologien_fein",
        "verdauung_galle",
        "bakterien",
        "parasiten",
        "pilze",
        "bakterien_detailliert_fein",
        "parasiten_detailliert_fein",
        "pilze_detailliert_fein",
        "verdauung_remedies_multiplex",
        "heel_remedies_multiplex",
        "nutramedix_remedies_multiplex",
    ],
)

_register(
    name="leber_detailliert",
    display="Leber & Gallensystem",
    category="organ",
    groups=[
        "entgiftung_leber_phase1",
        "entgiftung_leber_phase1_fein",
        "entgiftung_leber_phase2",
        "entgiftung_leber_phase2_fein",
        "entgiftung_leber_phase3",
        "entgiftung_leber_phase3_fein",
        "entgiftung_leber",
        "verdauung_galle",
        "leber_enzyme_fein",
        "leber_pathologien_fein",
        "schwermetalle",
        "schwermetalle_detailliert_fein",
        "chemikalien_detailliert_fein",
        "entgiftung_remedies_multiplex",
        "heel_remedies_multiplex",
        "nutramedix_remedies_multiplex",
    ],
)

_register(
    name="niere_detailliert",
    display="Niere & Harnwege",
    category="organ",
    aliases=["urogenital_detailliert"],
    groups=[
        "entgiftung_niere",
        "urogenitalsystem_fein",
        "niere_funktion_fein",
        "niere_pathologien_fein",
        "blase_harnwege_fein",
        "prostata_fein",
        "schwermetalle",
        "schwermetalle_detailliert_fein",
        "bakterien",
        "bakterien_detailliert_fein",
        "entgiftung_remedies_multiplex",
        "heel_remedies_multiplex",
        "nutramedix_remedies_multiplex",
    ],
)

_register(
    name="nervensystem_detailliert",
    display="Nervensystem",
    category="organ",
    groups=[
        "nervensystem_zns",
        "nervensystem_zns_fein",
        "nervensystem_hirnnerven",
        "nervensystem_hirnnerven_fein",
        "nervensystem_vegetativ",
        "nervensystem_plexus",
        "nervensystem_neurotransmitter",
        "nervensystem_neurotransmitter_fein",
        "nerven_symptome_fein",
        "nerven_pathologien_fein",
        "schwermetalle",
        "schwermetalle_detailliert_fein",
        "viren",
        "viren_detailliert_fein",
        "nerven_remedies_multiplex",
        "heel_remedies_multiplex",
        "nutramedix_remedies_multiplex",
    ],
)

_register(
    name="herz_kreislauf_fein",
    display="Herz-Kreislauf",
    category="organ",
    groups=[
        "herz_fein",
        "kreislauf",
        "kreislauf_fein",
        "blutdruck_fein",
        "gefaesse_fein",
        "herz_rhythmus_fein",
        "herz_pathologien_fein",
        "mikrozirkulation",
        "herz_remedies_multiplex",
        "heel_remedies_multiplex",
        "nutramedix_remedies_multiplex",
    ],
)

_register(
    name="atmung_lunge_detailliert",
    display="Atmung & Lunge",
    category="organ",
    groups=[
        "atmung_lunge",
        "atmung_lunge_fein",
        "lunge_funktion_fein",
        "lunge_pathologien_fein",
        "bronchien_fein",
        "atemwege_obere_fein",
        "bakterien",
        "viren",
        "pilze",
        "bakterien_detailliert_fein",
        "viren_detailliert_fein",
        "allergie_atemwege_fein",
        "atmung_remedies_multiplex",
        "heel_remedies_multiplex",
        "nutramedix_remedies_multiplex",
    ],
)

_register(
    name="endokrin_detailliert",
    display="Hormonsystem",
    category="organ",
    groups=[
        "endokrin",
        "endokrin_fein",
        "schilddruese",
        "schilddruese_fein",
        "nebenniere",
        "nebenniere_fein",
        "hypophyse_fein",
        "hypothalamus_fein",
        "hormone_symptome_fein",
        "hormone_pathologien_fein",
        "geschlechtshormone_fein",
        "endokrin_remedies_multiplex",
        "heel_remedies_multiplex",
        "nutramedix_remedies_multiplex",
    ],
)

_register(
    name="haut_detailliert",
    display="Haut",
    category="organ",
    groups=[
        "haut_detailliert_fein",
        "hautprobleme_fein",
        "haut_pathologien_fein",
        "haut_allergien_fein",
        "entgiftung_haut",
        "entgiftung_lymphe",
        "bakterien",
        "pilze",
        "bakterien_detailliert_fein",
        "pilze_detailliert_fein",
        "haut_remedies_multiplex",
        "heel_remedies_multiplex",
        "nutramedix_remedies_multiplex",
    ],
)

_register(
    name="lymphsystem_detailliert",
    display="Lymphsystem",
    category="organ",
    groups=[
        "entgiftung_lymphe",
        "lymphsystem",
        "lymphsystem_fein",
        "entgiftung_leber_phase1",
        "entgiftung_leber_phase1_fein",
        "entgiftung_leber_phase2",
        "entgiftung_leber_phase2_fein",
        "entgiftung_leber_phase3",
        "entgiftung_leber_phase3_fein",
        "entgiftung_leber",
        "entgiftung_niere",
        "entgiftung_darm",
        "entgiftung_haut",
        "entgiftung_organe_fein",
        "entgiftung_symptome_fein",
        "verdauung_magen",
        "verdauung_duenndarm",
        "verdauung_dickdarm",
        "verdauung_mikrobiom",
        "verdauung_barriere",
        "bakterien",
        "bakterien_detailliert_fein",
        "viren",
        "viren_detailliert_fein",
        "parasiten",
        "parasiten_detailliert_fein",
        "pilze",
        "pilze_detailliert_fein",
        "schwermetalle",
        "schwermetalle_detailliert_fein",
        "immunsystem_angeboren",
        "immunsystem_angeboren_fein",
        "immunsystem_erworben",
        "immunsystem_erworben_fein",
        "immunsystem_autoimmun_fein",
        "immunsystem_zytokine_fein",
        "entzuendung",
        "mikronaehrstoffe",
        "entgiftung_remedies_multiplex",
        "verdauung_remedies_multiplex",
        "anti_infektions_remedies_multiplex",
        "immunstaerkung_remedies_multiplex",
        "homoeopathie_klassisch",
        "homoeopathie_komplexmittel",
        "spagyrik",
        "spagyrik_multiplex",
        "bachblueten_multiplex",
    ],
)

_register(
    name="immunsystem_detailliert",
    display="Immunsystem detailliert",
    category="organ",
    groups=[
        "immunsystem_angeboren",
        "immunsystem_angeboren_fein",
        "immunsystem_erworben",
        "immunsystem_erworben_fein",
        "immunsystem_autoimmun_fein",
        "immunsystem_zytokine_fein",
        "entzuendung",
        "lymphsystem",
        "lymphsystem_fein",
        "bakterien",
        "viren",
        "parasiten",
        "pilze",
        "immunstaerkung_remedies_multiplex",
        "heel_remedies_multiplex",
        "nutramedix_remedies_multiplex",
    ],
)

_register(
    name="gehirn_detailliert",
    display="Gehirn & ZNS",
    category="organ",
    groups=[
        "nervensystem_zns",
        "nervensystem_zns_fein",
        "nervensystem_hirnnerven",
        "nervensystem_hirnnerven_fein",
        "nervensystem_vegetativ",
        "nervensystem_plexus",
        "nervensystem_neurotransmitter",
        "nervensystem_neurotransmitter_fein",
        "nerven_symptome_fein",
        "nerven_pathologien_fein",
        "wirbelsaeule",
        "wirbelsaeule_fein",
        "wirbelsaeule_hws",
        "schwindel_hws",
        "schwindel_kreislauf",
        "schwindel_medikament",
        "schwindel_vestibular",
        "schwindel_vestibular_fein",
        "schwindel_zentral",
        "schwindel_zentral_fein",
        "schmerz_kopf",
        "schmerz_kopf_fein",
        "schlafstoerungen",
        "schlafstoerungen_fein",
        "muedigkeit_chronisch",
        "konzentration",
        "schwermetalle",
        "schwermetalle_detailliert_fein",
        "bakterien",
        "bakterien_detailliert_fein",
        "viren",
        "viren_detailliert_fein",
        "nerven_remedies_multiplex",
        "energie_remedies_multiplex",
        "psyche_remedies_multiplex",
        "homoeopathie_klassisch",
        "spagyrik",
        "bachblueten_multiplex",
    ],
)

# =============================================================================
# KATEGORIE: STRUKTUR
# =============================================================================

_register(
    name="knochen_detailliert",
    display="Knochen & Gelenke",
    category="struktur",
    groups=[
        "knochen_gelenke",
        "knochen_gelenke_fein",
        "bewegungsapparat_muskeln",
        "bewegungsapparat_muskeln_fein",
        "bewegungsapparat_gelenke",
        "bewegungsapparat_gelenke_fein",
        "bewegungsapparat_sehnen",
        "bewegungsapparat_baender",
        "schmerz_gelenk",
        "schmerz_muskel",
        "entzuendung",
        "immunsystem_autoimmun_fein",
        "mikronaehrstoffe",
        "orthomolekular_mineralien_fein",
        "bewegung_remedies_multiplex",
        "schmerz_remedies_multiplex",
        "heel_remedies_multiplex",
        "nutramedix_remedies_multiplex",
    ],
)

_register(
    name="wirbelsaeule_detailliert",
    display="Wirbelsäule",
    category="struktur",
    groups=[
        "wirbelsaeule",
        "wirbelsaeule_fein",
        "wirbelsaeule_hws",
        "wirbelsaeule_bws",
        "wirbelsaeule_lws",
        "wirbelsaeule_symptome_fein",
        "wirbelsaeule_pathologien_fein",
        "nervensystem_plexus",
        "schmerz_ruecken",
        "bewegung_remedies_multiplex",
        "schmerz_remedies_multiplex",
        "heel_remedies_multiplex",
        "nutramedix_remedies_multiplex",
    ],
)

_register(
    name="zahn_detailliert",
    display="Zähne & Kiefer",
    category="struktur",
    aliases=["zaehne_kiefer_detailliert"],
    groups=[
        "zahnorgane",
        "zahnorgane_fein",
        "odontone",
        "odontone_fein",
        "zahn_herde_fein",
        "zahn_materialien_fein",
        "zahn_meridiane_fein",
        "kiefergelenk_fein",
        "bakterien",
        "bakterien_detailliert_fein",
        "schwermetalle",
        "schwermetalle_detailliert_fein",
        "zahn_remedies_multiplex",
        "heel_remedies_multiplex",
        "nutramedix_remedies_multiplex",
    ],
)

_register(
    name="tote_zaehne_detailliert",
    display="Tote Zähne & Herde",
    category="struktur",
    groups=[
        "zahnorgane",
        "zahnorgane_fein",
        "odontone",
        "odontone_fein",
        "zahn_herde_fein",
        "tote_zaehne_fein",
        "nico_fdok_fein",
        "kavitaeten_fein",
        "bakterien",
        "bakterien_detailliert_fein",
        "schwermetalle",
        "schwermetalle_detailliert_fein",
        "entzuendung",
        "immunsystem_autoimmun_fein",
        "zahn_remedies_multiplex",
        "heel_remedies_multiplex",
        "nutramedix_remedies_multiplex",
    ],
)

_register(
    name="bindegewebe_faszien",
    display="Bindegewebe & Faszien",
    category="struktur",
    groups=[
        "bewegungsapparat_muskeln",
        "bewegungsapparat_muskeln_fein",
        "bewegungsapparat_gelenke",
        "bewegungsapparat_gelenke_fein",
        "bewegungsapparat_sehnen",
        "bewegungsapparat_baender",
        "wirbelsaeule",
        "wirbelsaeule_fein",
        "wirbelsaeule_hws",
        "wirbelsaeule_bws",
        "wirbelsaeule_lws",
        "schmerz_muskel",
        "schmerz_gelenk",
        "schmerz_ruecken",
        "entgiftung_lymphe",
        "entgiftung_darm",
        "entgiftung_haut",
        "immunsystem_angeboren",
        "immunsystem_erworben",
        "immunsystem_autoimmun_fein",
        "entzuendung",
        "mikronaehrstoffe",
        "orthomolekular_vitamine_fein",
        "orthomolekular_mineralien_fein",
        "aminosaeuren_detailliert_fein",
        "bewegung_remedies_multiplex",
        "schmerz_remedies_multiplex",
        "homoeopathie_klassisch",
        "spagyrik",
    ],
)

# =============================================================================
# KATEGORIE: SYMPTOM-SPEZIFISCH
# =============================================================================

_register(
    name="schmerz_detailliert",
    display="Schmerz & Schlaf",
    category="symptom",
    groups=[
        "schmerz_kopf",
        "schmerz_kopf_fein",
        "schmerz_ruecken",
        "schmerz_muskel",
        "schmerz_gelenk",
        "schmerz_nerven_fein",
        "schmerz_chronisch_fein",
        "schlafstoerungen",
        "schlafstoerungen_fein",
        "nervensystem_neurotransmitter_fein",
        "schmerz_remedies_multiplex",
        "heel_remedies_multiplex",
        "nutramedix_remedies_multiplex",
    ],
)

_register(
    name="schwindel_detailliert",
    display="Schwindel",
    category="symptom",
    groups=[
        "schwindel_hws",
        "schwindel_kreislauf",
        "schwindel_medikament",
        "schwindel_vestibular",
        "schwindel_vestibular_fein",
        "schwindel_zentral",
        "schwindel_zentral_fein",
        "wirbelsaeule_hws",
        "kreislauf",
        "nervensystem_hirnnerven_fein",
        "schwindel_remedies_multiplex",
        "heel_remedies_multiplex",
        "nutramedix_remedies_multiplex",
    ],
)

_register(
    name="allergie_detailliert",
    display="Allergien & Unverträglichkeiten",
    category="symptom",
    groups=[
        "allergie_atemwege_fein",
        "allergie_haut_fein",
        "allergie_nahrung_fein",
        "histamin_fein",
        "immunsystem_erworben_fein",
        "immunsystem_zytokine_fein",
        "verdauung_barriere",
        "verdauung_mikrobiom_fein",
        "entgiftung_leber_phase1_fein",
        "entgiftung_leber_phase2_fein",
        "allergie_remedies_multiplex",
        "heel_remedies_multiplex",
        "nutramedix_remedies_multiplex",
    ],
)

# =============================================================================
# KATEGORIE: BELASTUNGEN & VERGIFTUNG
# =============================================================================

_register(
    name="schwermetalle",
    display="Schwermetalle",
    category="toxin",
    groups=[
        "schwermetalle",
        "schwermetalle_tox",
        "schwermetalle_detailliert_fein",
        "entgiftung_leber_phase1_fein",
        "entgiftung_leber_phase2_fein",
        "entgiftung_niere",
        "entgiftung_lymphe",
        "toxine_symptome_fein",
        "entgiftung_remedies_multiplex",
        "toxine_remedies_multiplex",
        "heel_remedies_multiplex",
        "nutramedix_remedies_multiplex",
    ],
)

_register(
    name="strahlung_detailliert",
    display="Strahlung & EMF",
    category="toxin",
    aliases=["emf_stoerfelder_detailliert"],
    groups=[
        "strahlung_tox",
        "strahlung_quellen_fein",
        "strahlung_symptome_fein",
        "emf_fein",
        "geopathie",
        "geopathie_fein",
        "energetische_blockaden_fein",
        "strahlung_remedies_multiplex",
        "heel_remedies_multiplex",
        "nutramedix_remedies_multiplex",
    ],
)

_register(
    name="stoerfelder_toxisch",
    display="Störfelder",
    category="toxin",
    groups=[
        "entgiftung_leber_phase1",
        "entgiftung_leber_phase1_fein",
        "entgiftung_leber_phase2",
        "entgiftung_leber_phase2_fein",
        "entgiftung_leber_phase3",
        "entgiftung_leber_phase3_fein",
        "zahn_herde_fein",
        "tote_zaehne_fein",
        "narben_stoerfelder_fein",
        "energetische_blockaden_fein",
        "geopathie",
        "geopathie_fein",
        "stoerfeld_remedies_multiplex",
        "heel_remedies_multiplex",
        "nutramedix_remedies_multiplex",
    ],
)

_register(
    name="vergiftung_komplett",
    display="Vergiftungserscheinungen (komplett)",
    category="toxin",
    groups=[
        "schwermetalle",
        "schwermetalle_detailliert_fein",
        "chemikalien_tox",
        "chemikalien_detailliert_fein",
        "pestizide_tox",
        "pestizide_detailliert_fein",
        "medikamente_tox",
        "medikamente_detailliert_fein",
        "toxine_symptome_fein",
        "entgiftung_leber_phase1_fein",
        "entgiftung_leber_phase2_fein",
        "entgiftung_leber_phase3_fein",
        "entgiftung_niere",
        "entgiftung_lymphe",
        "entgiftung_remedies_multiplex",
        "toxine_remedies_multiplex",
        "heel_remedies_multiplex",
        "nutramedix_remedies_multiplex",
    ],
)

_register(
    name="pestizide_herbizide",
    display="Pestizide & Herbizide",
    category="toxin",
    groups=[
        "pestizide_tox",
        "pestizide_detailliert_fein",
        "herbizide_fein",
        "insektizide_fein",
        "chemikalien_detailliert_fein",
        "entgiftung_leber_phase1_fein",
        "entgiftung_leber_phase2_fein",
        "toxine_symptome_fein",
        "entgiftung_remedies_multiplex",
        "heel_remedies_multiplex",
        "nutramedix_remedies_multiplex",
    ],
)

_register(
    name="medikamenten_toxizitaet",
    display="Medikamenten-Toxizität",
    category="toxin",
    groups=[
        "medikamente_tox",
        "medikamente_detailliert_fein",
        "medikamente_nebenwirkungen_fein",
        "entgiftung_leber_phase1_fein",
        "entgiftung_leber_phase2_fein",
        "toxine_symptome_fein",
        "entgiftung_remedies_multiplex",
        "heel_remedies_multiplex",
        "nutramedix_remedies_multiplex",
    ],
)

# =============================================================================
# KATEGORIE: INTOLERANZEN & STOFFWECHSEL
# =============================================================================

_register(
    name="nahrungsmittel_intoleranzen",
    display="Nahrungsmittel-Intoleranzen",
    category="stoffwechsel",
    groups=[
        "allergie_nahrung_fein",
        "histamin_fein",
        "laktose_fein",
        "gluten_fein",
        "fruktose_fein",
        "verdauung_barriere",
        "verdauung_mikrobiom_fein",
        "verdauung_symptome_fein",
        "entgiftung_leber_phase1_fein",
        "verdauung_remedies_multiplex",
        "heel_remedies_multiplex",
        "nutramedix_remedies_multiplex",
    ],
)

_register(
    name="mitochondrien_dysfunktion",
    display="Mitochondrien-Dysfunktion",
    category="stoffwechsel",
    groups=[
        "mitochondrien",
        "mitochondrien_fein",
        "energie_stoffwechsel_fein",
        "atp_produktion_fein",
        "oxidativer_stress_fein",
        "mikronaehrstoffe",
        "orthomolekular_vitamine_fein",
        "orthomolekular_mineralien_fein",
        "aminosaeuren_detailliert_fein",
        "muedigkeit_chronisch",
        "schlafstoerungen",
        "energie_remedies_multiplex",
        "orthomolekular_therapie_multiplex",
        "heel_remedies_multiplex",
        "nutramedix_remedies_multiplex",
    ],
)

# =============================================================================
# KATEGORIE: PSYCHE & ENERGIE
# =============================================================================

_register(
    name="psyche_detailliert",
    display="Psyche & Emotionen",
    category="psyche",
    aliases=["psyche_emotion_detailliert"],
    groups=[
        "psyche_emotion_fein",
        "psyche_stress_fein",
        "psyche_trauma_fein",
        "psyche_depression_fein",
        "psyche_angst_fein",
        "nervensystem_neurotransmitter_fein",
        "endokrin_fein",
        "nebenniere_fein",
        "schlafstoerungen",
        "schlafstoerungen_fein",
        "psyche_remedies_multiplex",
        "bachblueten_multiplex",
        "homoeopathie_klassisch",
        "spagyrik",
        "heel_remedies_multiplex",
        "nutramedix_remedies_multiplex",
    ],
)

_register(
    name="chakren_meridiane",
    display="Chakren & Meridiane",
    category="energie",
    aliases=["meridiane_tcm_detailliert"],
    groups=[
        "chakren",
        "chakren_full",
        "chakren_detailliert_fein",
        "chakren_erweitert",
        "nebenchakren",
        "meridiane",
        "meridiane_detailliert_fein",
        "tcm_punkte",
        "tcm_punkte_extended",
        "tcm_full",
        "extra_meridiane",
        "energetische_blockaden_fein",
        "energie_remedies_multiplex",
        "bachblueten_multiplex",
        "homoeopathie_klassisch",
        "spagyrik",
    ],
)

_register(
    name="miasma_detailliert",
    display="Miasmen & Erbbelastungen",
    category="energie",
    groups=[
        "miasma_psora",
        "miasma_sykose",
        "miasma_syphilinie",
        "miasma_tuberkulinie",
        "miasma_karzinogenie",
        "miasma_symptome_fein",
        "erbbelastungen_fein",
        "homoeopathie_nosoden",
        "homoeopathie_klassisch",
        "spagyrik",
        "bachblueten_multiplex",
    ],
)


# =============================================================================
# KATEGORIE: B-PROFILE (BAT-AKUT) - VERSION K
# Hinzugefügt: 2025-12-19 | 10 neue Profile
# =============================================================================

_register(
    name="b1_infektion_bakteriell",
    display="B1 Bakterielle Infektionen",
    category="bat",
    level=3,  # Version K - Erweitert
    groups=[
        "bat_a01_bakterien_abwehr_organunspezifisch",
        "bat_a02_bakterien_abwehr_augen____bindehaut",
        "bat_a03_bakterien_abwehr_bindegewebe__gekapselt",
        "bat_a04_bakterien_abwehr_blinddarm",
        "bat_a05_bakterien_abwehr_borreliose",
        "bat_a06_bakterien_abwehr_geb_rmutter",
        "bat_a07_bakterien_abwehr_gerstenkorn",
        "bat_a08_bakterien_abwehr_harnleiter___nieren___blase",
        "bat_a09_bakterien_abwehr_herzkranzgef__e",
        "bat_a10_bakterien_abwehr_kehlkopf___stimmb_nder",
        "bat_a11_bakterien_abwehr_keuchhusten",
        "bat_a12_bakterien_abwehr_lunge",
        "bat_a13_bakterien_abwehr_magen___darmtrakt",
        "bat_a14_bakterien_abwehr_nase___rachen___bronchien",
        "bat_a15_bakterien_abwehr_nervensystem",
        "bat_a16_bakterien_abwehr_ohren",
        "bat_a17_bakterien_abwehr_z_hne___zahnhalteapparat",
        "bakterien",
        "bakterien_fein",
        "bakterien_detailliert_fein",
        "immunstaerkung_remedies_multiplex",
    ],
)

_register(
    name="b2_infektion_viral",
    display="B2 Virale Infektionen",
    category="bat",
    level=3,  # Version K - Erweitert
    groups=[
        "bat_a21_viren_abwehr_organunspezifisch",
        "bat_a22_viren_abwehr_borna",
        "bat_a23_viren_abwehr_chikungunya",
        "bat_a24_viren_abwehr_hepatitis",
        "bat_a25_viren_abwehr_hpv_geb_rmutterhals",
        "bat_a26_viren_abwehr_kopf___muskulatur___bindegewebe",
        "bat_a27_viren_abwehr_lunge",
        "bat_a28_viren_abwehr_magen___darmtrakt",
        "bat_a29_viren_abwehr_mumps___masern",
        "bat_a30_viren_abwehr_nase___rachen___bronchien",
        "bat_a31_viren_abwehr_pankreas__diabetes_mellitus_",
        "bat_a32_viren_abwehr_perk",
        "bat_a33_viren_abwehr_psoriasis",
        "bat_a34_viren_abwehr_warzenbeseitigung",
        "bat_a35_viren_abwehr_fsme__dengue__gelbfieber",
        "bat_a36_viren_abwehr_r_teln___ringelr_teln",
        "viren",
        "viren_fein",
        "viren_detailliert_fein",
        "immunstaerkung_remedies_multiplex",
    ],
)

_register(
    name="b3_herpes_komplett",
    display="B3 Herpes-Viren",
    category="bat",
    level=3,  # Version K - Erweitert
    groups=[
        "bat_a41_herpes_viren_abwehr_allgemein__magen___darm_",
        "bat_a42_herpes_viren_abwehr_augen____bindehaut",
        "bat_a43_herpes_viren_abwehr_genitalis",
        "bat_a44_herpes_viren_abwehr_g_rtelrose",
        "bat_a45_herpes_viren_abwehr_pfeiffersches_dr_senfieber",
        "bat_a46_herpes_viren_abwehr_windpocken",
        "bat_a47_herpes_viren_abwehr_zytomegalie",
        "viren",
        "viren_fein",
        "viren_detailliert_fein",
        "immunstaerkung_remedies_multiplex",
        "heel_remedies_multiplex",
    ],
)

_register(
    name="b4_pilz_parasiten",
    display="B4 Pilze & Parasiten",
    category="bat",
    level=3,  # Version K - Erweitert
    groups=[
        "bat_a51_dermatophyten_abwehr_hautspezifisch",
        "bat_a52_dermatophyten_abwehr_nagelmykose",
        "bat_a53_dermatophyten_abwehr_unterleib",
        "bat_a54_hefepilz_abwehr_candida__darmtrakt_",
        "bat_a55_milben_abwehr__schwarze_milbe_",
        "bat_a56_parasiten_abwehr_darmtrakt",
        "bat_a57_parasiten_abwehr_harnleiter___blase",
        "bat_a58_parasiten_abwehr_leishmaniasen",
        "bat_a59_protozoen_abwehr__u_a__toxoplasmose_",
        "pilze",
        "pilze_fein",
        "pilze_detailliert_fein",
        "parasiten",
        "parasiten_fein",
        "parasiten_detailliert_fein",
        "immunstaerkung_remedies_multiplex",
    ],
)

_register(
    name="b5_akut_verletzung",
    display="B5 Akute Verletzungen",
    category="bat",
    level=3,  # Version K - Erweitert
    groups=[
        "bat_a60_b_nderdehnung____riss",
        "bat_a61_bluterguss___prellung",
        "bat_a62_brustentz_ndung___milchstau",
        "bat_a63_mittelhirnsyndrom___gehirnersch_tterung",
        "bat_a64_gelenkkapselreizung____entz_ndung",
        "bat_a65_h_morrhoiden",
        "bat_a66_karpaltunnel_syndrom",
        "bat_a67_knochenbruch__akut___nachsorge",
        "bat_a68_kopfschmerzen___migr_ne",
        "bat_a69_leistenbruch__akut___op_nachsorge",
        "bat_a70_muskelzerrung____verh_rtung____verspannung",
        "bat_a71_neurodermitis",
        "bat_a72_wundheilung__innere____u_ere",
        "bat_a73_prostata_beschwerden",
        "bat_a74_schleimbeutelreizung____entz_ndung",
        "bat_a75_sehnenscheidenreizung____entz_ndung",
        "bat_a76_zahnbildung__babys___schulkinder_",
        "schmerz_remedies_multiplex",
        "bewegung_remedies_multiplex",
    ],
)

_register(
    name="b6_schmerz_therapie",
    display="B6 Schmerztherapie",
    category="bat",
    level=3,  # Version K - Erweitert
    groups=[
        "bat_a78_schmerztherapie",
        "bat_a68_kopfschmerzen___migr_ne",
        "bat_a70_muskelzerrung____verh_rtung____verspannung",
        "schmerz_kopf",
        "schmerz_kopf_fein",
        "schmerz_ruecken",
        "schmerz_muskel",
        "schmerz_gelenk",
        "schmerz_remedies_multiplex",
        "heel_remedies_multiplex",
    ],
)

_register(
    name="b7_vitalstoff_energie",
    display="B7 Vitalstoffe & Energie",
    category="bat",
    level=3,  # Version K - Erweitert
    groups=[
        "bat_a80_vitalstoffe_gesamt__vitamine__mineralstoffe__s",
        "bat_a82_energieversorgung",
        "bat_a84_hb_werte_stabilisierung_und_blutqualit_t",
        "mikronaehrstoffe",
        "orthomolekular_vitamine",
        "orthomolekular_vitamine_fein",
        "orthomolekular_mineralien",
        "orthomolekular_mineralien_fein",
        "mitochondrien",
        "energie_remedies_multiplex",
    ],
)

_register(
    name="b8_hormon_psyche",
    display="B8 Hormone & Psyche",
    category="bat",
    level=3,  # Version K - Erweitert
    groups=[
        "bat_a85_hormon_regulation__w_",
        "bat_a87_psychosomatische_dysbalance___depressionen",
        "bat_a88_schlafregulation____f_rderung",
        "bat_a89_hormon_regulation__m_",
        "endokrin",
        "endokrin_fein",
        "hormone_symptome_fein",
        "hormone_geschlecht_fein",
        "psyche_emotion_fein",
        "psyche_stress_fein",
        "schlafstoerungen",
        "schlafstoerungen_fein",
        "psyche_remedies_multiplex",
        "hormone_remedies_multiplex",
    ],
)

_register(
    name="b9_entgiftung_reinigung",
    display="B9 Entgiftung & Reinigung",
    category="bat",
    level=3,  # Version K - Erweitert
    groups=[
        "bat_a83_gewebereinigung___entgiftung",
        "bat_a93_leberreinigung",
        "bat_a77_toxische_belastungen___insektengifte",
        "entgiftung_leber",
        "entgiftung_leber_phase1",
        "entgiftung_leber_phase2",
        "entgiftung_leber_phase1_fein",
        "entgiftung_leber_phase2_fein",
        "entgiftung_niere",
        "entgiftung_darm",
        "entgiftung_lymphe",
        "entgiftung_remedies_multiplex",
        "toxine_remedies_multiplex",
    ],
)

_register(
    name="b10_mikrozirkulation",
    display="B10 Mikrozirkulation & Kreislauf",
    category="bat",
    level=3,  # Version K - Erweitert
    groups=[
        "bat_a92_mikrozirkulation_blutgef__e",
        "bat_a86_kreislaufregulation____stabilisierung",
        "mikrozirkulation",
        "kreislauf",
        "kreislauf_fein",
        "herz_fein",
        "gefaesse_fein",
        "herz_remedies_multiplex",
    ],
)


# =============================================================================
# KATEGORIE: FREQUENZTHERAPIE - VERSION K
# Hinzugefügt: 2025-12-19 | 3 neue Profile
# =============================================================================

_register(
    name="frequenz_rife_clark",
    display="Frequenztherapie Rife/Clark",
    category="frequenz",
    level=3,  # Version K - Erweitert
    groups=[
        "frequenz_royal_rife",
        "frequenz_clark",
        "frequenz_rife_multiplex",
        "frequenz_clark_multiplex",
        "immunstaerkung_remedies_multiplex",
    ],
)

_register(
    name="frequenz_solfeggio",
    display="Solfeggio-Frequenzen",
    category="frequenz",
    level=3,  # Version K - Erweitert
    groups=[
        "frequenz_solfeggio",
        "frequenz_solfeggio_multiplex",
        "frequenz_binaural",
        "klang_therapie",
        "energie_remedies_multiplex",
    ],
)

_register(
    name="frequenz_komplett",
    display="Frequenztherapie Komplett",
    category="frequenz",
    level=3,  # Version K - Erweitert
    groups=[
        "frequenz_royal_rife",
        "frequenz_clark",
        "frequenz_solfeggio",
        "frequenz_binaural",
        "frequenz_rife_multiplex",
        "frequenz_clark_multiplex",
        "frequenz_solfeggio_multiplex",
        "klang_therapie",
        "energie_remedies_multiplex",
    ],
)


# =============================================================================
# KATEGORIE: THERAPIESYSTEME - VERSION K
# Hinzugefügt: 2025-12-19 | 5 neue Profile
# =============================================================================

_register(
    name="aromatherapie",
    display="Aromatherapie",
    category="therapie",
    level=3,  # Version K - Erweitert
    groups=[
        "aromatherapie_oele",
        "aromatherapie_mischungen",
        "aromatherapie_multiplex",
        "energie_remedies_multiplex",
    ],
)

_register(
    name="kristall_magnetfeld",
    display="Kristalle & Magnetfeld",
    category="therapie",
    level=3,  # Version K - Erweitert
    groups=[
        "kristalle_heilung",
        "magnetfeld",
        "edelsteine",
        "edelsteine_chakren",
        "edelsteine_schutz",
        "licht_farbe",
        "farbtherapie",
        "energie_remedies_multiplex",
    ],
)

_register(
    name="ayurveda",
    display="Ayurveda",
    category="therapie",
    level=3,  # Version K - Erweitert
    groups=[
        "ayurveda_dosha",
        "phytotherapie_ayurveda",
        "phytotherapie_extrakte",
        "phytotherapie_tinkturen",
        "energie_remedies_multiplex",
    ],
)

_register(
    name="tcm_erweitert",
    display="TCM Erweitert",
    category="therapie",
    level=3,  # Version K - Erweitert
    groups=[
        "tcm_full",
        "tcm_punkte",
        "tcm_punkte_extended",
        "tcm_rezepturen",
        "tcm_rezepturen_multiplex",
        "tcm_rezepturen_potenzen",
        "meridiane",
        "meridiane_detailliert_fein",
        "extra_meridiane",
    ],
)

_register(
    name="stammzellen_peptide",
    display="Regenerative Therapie",
    category="therapie",
    level=3,  # Version K - Erweitert
    groups=[
        "stammzellen_aktivierung",
        "peptide_bioregulator",
        "peptide_thymus",
        "nad_booster",
        "autophagie_aktivierung",
        "mitochondrien",
        "mitochondrien_fein",
        "energie_remedies_multiplex",
    ],
)


# =============================================================================
# KATEGORIE: SPEZIAL-PROFILE - VERSION K
# Hinzugefügt: 2025-12-19 | 2 neue Profile
# =============================================================================

_register(
    name="kinderkrankheiten",
    display="Pädiatrische Analyse",
    category="spezial",
    level=3,  # Version K - Erweitert
    groups=[
        "kinderkrankheiten_fein",
        "bakterien",
        "bakterien_fein",
        "viren",
        "viren_fein",
        "bat_a11_bakterien_abwehr_keuchhusten",
        "bat_a29_viren_abwehr_mumps___masern",
        "bat_a46_herpes_viren_abwehr_windpocken",
        "bat_a36_viren_abwehr_r_teln___ringelr_teln",
        "bat_a76_zahnbildung__babys___schulkinder_",
        "immunstaerkung_remedies_multiplex",
        "homoeopathie_klassisch",
    ],
)

_register(
    name="schwangerschaft_wechseljahre",
    display="Frauengesundheit",
    category="spezial",
    level=3,  # Version K - Erweitert
    groups=[
        "schwangerschaft_geburt_fein",
        "wechseljahre_detailliert_fein",
        "hormone_geschlecht_fein",
        "hormone_symptome_fein",
        "bat_a85_hormon_regulation__w_",
        "bat_a62_brustentz_ndung___milchstau",
        "endokrin",
        "endokrin_fein",
        "hormone_remedies_multiplex",
        "homoeopathie_klassisch",
        "bachblueten_multiplex",
    ],
)


# =============================================================================
# KATEGORIE: LEVEL 4 - AUTO-GENERIERTE FEIN-PROFILE (VERSION M)
# Automatisch generiert aus allen *_fein und *_detailliert Gruppen
# =============================================================================


def _humanize_group_name(group_name: str) -> str:
    """Konvertiert Gruppen-Namen zu lesbarem Display-Namen."""
    name = group_name.replace("_fein", "").replace("_detailliert", "")
    name = name.replace("_", " ").title()
    return f"{name} (Fein)"


def _detect_category_for_group(group_name: str) -> str:
    """Erkennt die Kategorie für eine Gruppe."""
    if any(
        x in group_name for x in ["bakterien", "viren", "parasiten", "pilze", "infekt"]
    ):
        return "pathogen_fein"
    if any(
        x in group_name
        for x in ["toxin", "schwermetall", "chemikalien", "pestizid", "strahlung"]
    ):
        return "toxin_fein"
    if any(x in group_name for x in ["immun", "entzuend", "autoimmun", "zytokine"]):
        return "immun_fein"
    if any(x in group_name for x in ["entgiftung", "leber", "niere", "lymph"]):
        return "detox_fein"
    if any(x in group_name for x in ["nerven", "gehirn", "neurotransmitter", "zns"]):
        return "neuro_fein"
    if any(x in group_name for x in ["herz", "kreislauf", "gefaess", "blut"]):
        return "kardio_fein"
    if any(x in group_name for x in ["verdauung", "magen", "darm", "mikrobiom"]):
        return "verdauung_fein"
    if any(x in group_name for x in ["hormon", "endokrin", "schilddruese"]):
        return "hormon_fein"
    if any(x in group_name for x in ["psyche", "emotion", "stress", "schlaf"]):
        return "psyche_fein"
    if any(x in group_name for x in ["chakren", "meridiane", "energie"]):
        return "energie_fein"
    if any(
        x in group_name for x in ["knochen", "gelenk", "muskel", "wirbel", "faszien"]
    ):
        return "bewegung_fein"
    if any(x in group_name for x in ["zahn", "kiefer", "odonton"]):
        return "dental_fein"
    if any(x in group_name for x in ["haut", "allergie"]):
        return "haut_fein"
    if any(x in group_name for x in ["atmung", "lunge", "bronch"]):
        return "atmung_fein"
    return "sonstige_fein"


def _get_related_remedy_groups(group_name: str) -> List[str]:
    """Gibt passende Remedy-Gruppen für eine Fein-Gruppe zurück."""
    remedies = ["heel_remedies_multiplex", "nutramedix_remedies_multiplex"]

    if any(
        x in group_name for x in ["bakterien", "viren", "parasiten", "pilze", "infekt"]
    ):
        remedies.append("immunstaerkung_remedies_multiplex")
    if any(x in group_name for x in ["entgiftung", "toxin", "schwermetall"]):
        remedies.extend(["entgiftung_remedies_multiplex", "toxine_remedies_multiplex"])
    if any(x in group_name for x in ["schmerz"]):
        remedies.append("schmerz_remedies_multiplex")
    if any(x in group_name for x in ["psyche", "emotion", "stress"]):
        remedies.extend(["psyche_remedies_multiplex", "bachblueten_multiplex"])
    if any(x in group_name for x in ["energie", "chakren", "meridiane"]):
        remedies.append("energie_remedies_multiplex")
    if any(x in group_name for x in ["verdauung", "magen", "darm"]):
        remedies.append("verdauung_remedies_multiplex")
    if any(x in group_name for x in ["hormon"]):
        remedies.append("hormone_remedies_multiplex")

    return remedies


def _auto_register_fein_profiles():
    """Registriert automatisch alle Fein-Gruppen als Level 4 Profile."""
    try:
        from core.subgroups.procedural_groups import list_groups

        all_groups = list_groups()
        fein_groups = [g for g in all_groups if "_fein" in g or "_detailliert" in g]

        # Bereits existierende Profile nicht überschreiben
        existing = set(MASTER_PROFILES.keys())

        registered_count = 0
        for group_name in sorted(fein_groups):
            # Profil-Name = Gruppen-Name
            profile_name = group_name.lower()

            if profile_name in existing:
                continue

            # Display-Name generieren
            display = _humanize_group_name(group_name)

            # Kategorie erkennen
            category = _detect_category_for_group(group_name)

            # Gruppen: Hauptgruppe + passende Remedies
            groups = [group_name] + _get_related_remedy_groups(group_name)

            # Registrieren als Level 4
            _register(
                name=profile_name,
                display=display,
                groups=groups,
                category=category,
                level=4,  # Level 4 = Komplett
            )
            registered_count += 1

        return registered_count
    except ImportError:
        # Falls procedural_groups nicht verfügbar
        return 0


# =============================================================================
# VERSION L: AUTO-GENERIERUNG ALLER 361 GRUPPEN ALS PROFILE
# =============================================================================


def _auto_register_all_groups_as_profiles():
    """
    VERSION L: Registriert automatisch ALLE 361 Gruppen als eigenständige Profile.

    Gruppen werden als Level 5 (Version L) Profile registriert.
    Bestehende Profile (Level 1-4) werden NICHT überschrieben.

    Returns:
        Anzahl der neu registrierten Profile
    """
    try:
        from core.subgroups.procedural_groups import list_groups

        all_groups = list_groups()

        # Bereits existierende Profile nicht überschreiben
        existing = set(MASTER_PROFILES.keys())

        registered_count = 0
        for group_name in sorted(all_groups):
            # Profil-Name = Gruppen-Name (lowercase)
            profile_name = group_name.lower().replace(" ", "_").replace("-", "_")

            if profile_name in existing:
                continue

            # Display-Name generieren
            display = _humanize_group_name(group_name)

            # Kategorie erkennen
            category = _detect_category_for_group(group_name)

            # Gruppen: Hauptgruppe + passende Remedies
            groups = [group_name] + _get_related_remedy_groups(group_name)

            # Registrieren als Level 5 (Version L - Alle Gruppen)
            _register(
                name=profile_name,
                display=f"[L] {display}",  # Kennzeichnung als Level-L-Profil
                groups=groups,
                category=category,
                level=5,  # Level 5 = Version L (alle Gruppen)
            )
            registered_count += 1

        return registered_count
    except ImportError:
        # Falls procedural_groups nicht verfügbar
        return 0


def get_all_available_groups() -> List[str]:
    """
    Gibt alle 361 verfügbaren Gruppen zurück (für dynamische Profil-Erstellung).

    Returns:
        Liste aller Gruppennamen
    """
    try:
        from core.subgroups.procedural_groups import list_groups

        return list_groups()
    except ImportError:
        return []


def create_dynamic_profile(
    name: str,
    groups: List[str],
    display_name: Optional[str] = None,
    category: str = "dynamisch",
) -> ProfileDefinition:
    """
    VERSION L: Erstellt ein dynamisches Profil aus beliebigen Gruppen.

    Ermöglicht Runtime-Erstellung von Custom-Profilen ohne Code-Änderung.

    Args:
        name: Eindeutiger Profilname
        groups: Liste der Gruppennnamen
        display_name: Optionaler Anzeigename
        category: Kategorie (Standard: "dynamisch")

    Returns:
        Das erstellte ProfileDefinition Objekt

    Example:
        >>> profile = create_dynamic_profile(
        ...     "mein_custom_profil",
        ...     ["leber", "galle", "detox"],
        ...     "Leber-Galle-Entgiftung"
        ... )
    """
    profile_name = name.lower().replace(" ", "_")

    if display_name is None:
        display_name = _humanize_group_name(name)

    # Registriere als Level 6 (Custom/Dynamisch)
    _register(
        name=profile_name,
        display=f"[D] {display_name}",  # D = Dynamisch
        groups=groups,
        category=category,
        level=6,  # Level 6 = Dynamisch/Custom
    )

    return MASTER_PROFILES[profile_name]


def get_profiles_version_l_full() -> List[ProfileDefinition]:
    """
    Gibt ALLE Profile für Version L zurück (Level 1-5, alle 361+ Profile).

    Inkludiert:
    - Level 1-4: Alle bisherigen Profile (153)
    - Level 5: Alle auto-generierten Gruppen-Profile

    Returns:
        Liste aller Profile inkl. Version-L-Profile
    """
    return [p for p in get_all_profiles() if p.level <= 5]


def get_group_profile_mapping() -> Dict[str, str]:
    """
    Gibt ein Mapping von Gruppen zu Profilen zurück.

    Nützlich für Symptom-zu-Profil-Empfehlungen.

    Returns:
        Dict: {gruppenname: profilname}
    """
    mapping = {}
    for profile in get_all_profiles():
        for group in profile.groups:
            if group not in mapping:
                mapping[group] = profile.name
    return mapping


# Auto-Registrierung beim Import ausführen
_AUTO_REGISTERED_COUNT = _auto_register_fein_profiles()

# VERSION L: Auto-Registrierung aller Gruppen als Profile
_VERSION_L_REGISTERED_COUNT = _auto_register_all_groups_as_profiles()


# =============================================================================
# API FUNKTIONEN
# =============================================================================


def get_profile(name: str) -> Optional[ProfileDefinition]:
    """Holt ein Profil nach Name oder Alias."""
    return MASTER_PROFILES.get(name.lower())


def get_groups_for_profile(name: str) -> Optional[List[str]]:
    """Gibt die Gruppen für ein Profil zurück."""
    profile = get_profile(name)
    if profile and profile.enabled:
        return profile.groups
    return None


def get_all_profiles() -> List[ProfileDefinition]:
    """Gibt alle aktiven Profile zurück (ohne Aliase)."""
    seen = set()
    result = []
    for profile in MASTER_PROFILES.values():
        if profile.name not in seen and profile.enabled:
            seen.add(profile.name)
            result.append(profile)
    return result


def get_profiles_for_category(category: str) -> List[ProfileDefinition]:
    """Gibt alle Profile einer Kategorie zurück."""
    return [p for p in get_all_profiles() if p.category == category]


def get_top3_analysis_profiles() -> List[Tuple[str, str]]:
    """Gibt die Profile für TOP-N Analyse zurück (Format für main.py)."""
    return [(p.name, p.display_name) for p in get_all_profiles()]


# =============================================================================
# LEVEL-BASIERTE API FUNKTIONEN (VERSION M)
# =============================================================================


def get_profiles_by_level(level: int) -> List[ProfileDefinition]:
    """Gibt alle Profile eines bestimmten Levels zurück.

    Args:
        level: Level 1-4

    Returns:
        Liste der Profile mit genau diesem Level
    """
    return [p for p in get_all_profiles() if p.level == level]


def get_profiles_up_to_level(max_level: int) -> List[ProfileDefinition]:
    """Gibt alle Profile bis einschließlich eines Levels zurück.

    Args:
        max_level: Maximales Level (1-4)

    Returns:
        Liste aller Profile mit Level <= max_level

    Level-Übersicht:
        Level 1: Basis-Profile (5) - pathogen, toxin, immune, detox, regulation
        Level 2: Standard-Profile (35) - Organ, Symptom, Toxin, etc.
        Level 3: Erweitert (55) - Version K (BAT, Frequenz, Therapie)
        Level 4: Komplett (100+) - Alle Fein-Profile
    """
    return [p for p in get_all_profiles() if p.level <= max_level]


def get_profiles_version_k() -> List[ProfileDefinition]:
    """Gibt alle Profile für Version K zurück (Level 1-3, 55 Profile)."""
    return get_profiles_up_to_level(3)


def get_profiles_version_m() -> List[ProfileDefinition]:
    """Gibt alle Profile für Version M zurück (Level 1-4, 100+ Profile)."""
    return get_profiles_up_to_level(4)


def get_profiles_version_l() -> List[ProfileDefinition]:
    """Gibt alle Profile für Version L zurück (Level 1-5, alle 361+ Profile)."""
    return [p for p in get_all_profiles() if p.level <= 5]


def get_top_n_analysis_profiles_by_level(
    max_level: int = 3,
) -> List[Tuple[str, str]]:
    """Gibt Profile für TOP-N Analyse nach Level zurück.

    Args:
        max_level: Maximales Level (1=Basis, 2=Standard, 3=Erweitert, 4=Komplett)

    Returns:
        Liste von (name, display_name) Tupeln für main.py
    """
    profiles = get_profiles_up_to_level(max_level)
    return [(p.name, p.display_name) for p in profiles]


def get_level_stats() -> Dict:
    """Gibt Statistiken über Profile nach Level zurück."""
    profiles = get_all_profiles()
    levels = {}
    for p in profiles:
        levels[p.level] = levels.get(p.level, 0) + 1

    return {
        "level_1_basis": levels.get(1, 0),
        "level_2_standard": levels.get(2, 0),
        "level_3_erweitert": levels.get(3, 0),
        "level_4_komplett": levels.get(4, 0),
        "level_5_version_l": levels.get(5, 0),
        "level_6_dynamisch": levels.get(6, 0),
        "total": len(profiles),
        "version_l_auto_registered": _VERSION_L_REGISTERED_COUNT,
    }


def validate_profile(name: str) -> Tuple[bool, str]:
    """Validiert ob ein Profil existiert und gibt Fehlerinfo zurück."""
    profile = get_profile(name)
    if profile is None:
        return False, f"Profil '{name}' nicht gefunden"
    if not profile.enabled:
        return False, f"Profil '{name}' ist deaktiviert"
    if not profile.groups:
        return False, f"Profil '{name}' hat keine Gruppen definiert"
    return True, "OK"


def get_profile_stats() -> Dict:
    """Gibt Statistiken über alle Profile zurück."""
    profiles = get_all_profiles()
    categories = {}
    levels = {}
    for p in profiles:
        categories[p.category] = categories.get(p.category, 0) + 1
        levels[p.level] = levels.get(p.level, 0) + 1

    return {
        "total_profiles": len(profiles),
        "total_aliases": len(MASTER_PROFILES) - len(profiles),
        "categories": categories,
        "levels": levels,  # NEU: Level-Statistiken
        "total_groups": len(set(g for p in profiles for g in p.groups)),
    }


# =============================================================================
# SELBST-TEST
# =============================================================================

if __name__ == "__main__":
    stats = get_profile_stats()
    level_stats = get_level_stats()
    print(f"=== PROFIL-SYNCHRONISIERUNG (VERSION L) ===")
    print(f"Gesamt-Profile: {stats['total_profiles']}")
    print(f"\n=== LEVEL-STATISTIKEN ===")
    print(f"Level 1 (Basis):      {level_stats['level_1_basis']}")
    print(f"Level 2 (Standard):   {level_stats['level_2_standard']}")
    print(f"Level 3 (Erweitert):  {level_stats['level_3_erweitert']}")
    print(f"Level 4 (Komplett):   {level_stats['level_4_komplett']}")
    print(f"Level 5 (Version L):  {level_stats['level_5_version_l']}")
    print(f"Level 6 (Dynamisch):  {level_stats['level_6_dynamisch']}")
    print(f"\nAuto-registriert (Version L): {level_stats['version_l_auto_registered']}")
    print(f"\n=== VERFÜGBARE GRUPPEN ===")
    all_groups = get_all_available_groups()
    print(f"Gesamt-Gruppen: {len(all_groups)}")
    print(f"Levels: {stats.get('levels', {})}")
    print()
    print("Profile nach Level:")
    print(f"  Level 1 (Basis):     {level_stats['level_1_basis']}")
    print(f"  Level 2 (Standard):  {level_stats['level_2_standard']}")
    print(f"  Level 3 (Erweitert): {level_stats['level_3_erweitert']}")
    print(f"  Level 4 (Komplett):  {level_stats['level_4_komplett']}")
    print(f"Aliase: {stats['total_aliases']}")
    print(f"Kategorien: {stats['categories']}")
    print(f"Eindeutige Gruppen: {stats['total_groups']}")
    print()
    print("Profile nach Kategorie:")
    for cat in sorted(stats["categories"].keys()):
        profiles = get_profiles_for_category(cat)
        print(f"  {cat}: {[p.name for p in profiles]}")
