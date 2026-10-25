from typing import List, Dict, Optional

"""
Profile Registry - Modularisierung Phase 1
============================================
WICHTIG: Diese Datei ist jetzt ein WRAPPER für die zentrale Profil-Synchronisierung!
Alle Profil-Definitionen sind in core/profile_sync/__init__.py

Änderungen an Profilen NUR in core/profile_sync/__init__.py vornehmen!
"""

# Import der zentralen Profil-Verwaltung
try:
    from core.profile_sync import (
        get_groups_for_profile as _sync_get_groups,
        get_profile,
        get_all_profiles,
        validate_profile,
        get_top3_analysis_profiles,
        MASTER_PROFILES,
    )
    _USE_SYNC = True
except ImportError:
    _USE_SYNC = False
    print("WARNUNG: core.profile_sync nicht verfügbar, nutze Legacy-Definitionen")

# Legacy-Definitionen (nur als Fallback, wenn profile_sync nicht verfügbar)
# Diese Listen wurden 1:1 aus der main.py übernommen.
_PROFILES_DATA: Dict[str, List[str]] = {
    "gehirn_detailliert": [
        "nervensystem_zns",
        "nervensystem_zns_fein",
        "nervensystem_hirnnerven",
        "nervensystem_hirnnerven_fein",
        "nervensystem_vegetativ",
        "nervensystem_neurotransmitter",
        "nervensystem_neurotransmitter_fein",
        "nervensystem_plexus",
        "nerven_symptome_fein",
        "nerven_pathologien_fein",
        "wirbelsaeule",
        "wirbelsaeule_fein",
        "wirbelsaeule_hws",
        "wirbelsaeule_symptome_fein",
        "wirbelsaeule_pathologien_fein",
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
        "umweltbelastungen_erweitert_fein",
        "wohnraumgifte_fein",
        "bakterien",
        "bakterien_detailliert_fein",
        "viren",
        "viren_detailliert_fein",
        "parasiten",
        "parasiten_detailliert_fein",
        "pilze",
        "pilze_detailliert_fein",
        "strahlung_tox",
        "strahlung_quellen_fein",
        "strahlung_symptome_fein",
        "immunsystem_angeboren",
        "immunsystem_angeboren_fein",
        "immunsystem_erworben",
        "immunsystem_erworben_fein",
        "entzuendung",
        "mikronaehrstoffe",
        "orthomolekular_vitamine_fein",
        "orthomolekular_mineralien_fein",
        "orthomolekular_aminosauren_fein",
        "vitamine_detailliert_fein",
        "mineralien_spurenelemente_detailliert_fein",
        "aminosaeuren_detailliert_fein",
        "fettsaeuren_detailliert_fein",
        "orthomolekular_therapie_multiplex",
        "nerven_remedies_multiplex",
        "energie_remedies_multiplex",
        "psyche_remedies_multiplex",
        "homoeopathie_klassisch",
        "homoeopathie_klassisch_potenzen",
        "homoeopathie_komplexmittel",
        "homoeopathie_isopathie",
        "homoeopathie_nosoden",
        "spagyrik",
        "spagyrik_multiplex",
        "bachblueten_multiplex",
        "frequenz_clark_multiplex",
        "frequenz_rife_multiplex",
        "frequenz_solfeggio_multiplex",
    ],
    "lymphsystem_detailliert": [
        "entgiftung_lymphe",
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
        "verdauung_duenndarm_fein",
        "verdauung_dickdarm_fein",
        "verdauung_mikrobiom_fein",
        "verdauung_symptome_fein",
        "verdauung_pathologien_fein",
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
        "chemikalien_detailliert_fein",
        "umweltbelastungen_erweitert_fein",
        "wohnraumgifte_fein",
        "toxine_symptome_fein",
        "toxine_remedies_multiplex",
        "immunsystem_angeboren",
        "immunsystem_angeboren_fein",
        "immunsystem_erworben",
        "immunsystem_erworben_fein",
        "immunsystem_autoimmun_fein",
        "immunsystem_zytokine_fein",
        "entzuendung",
        "mikronaehrstoffe",
        "orthomolekular_vitamine_fein",
        "orthomolekular_mineralien_fein",
        "orthomolekular_aminosauren_fein",
        "vitamine_detailliert_fein",
        "mineralien_spurenelemente_detailliert_fein",
        "aminosaeuren_detailliert_fein",
        "fettsaeuren_detailliert_fein",
        "orthomolekular_therapie_multiplex",
        "entgiftung_remedies_multiplex",
        "verdauung_remedies_multiplex",
        "anti_infektions_remedies_multiplex",
        "immunstaerkung_remedies_multiplex",
        "homoeopathie_klassisch",
        "homoeopathie_klassisch_potenzen",
        "homoeopathie_komplexmittel",
        "homoeopathie_isopathie",
        "homoeopathie_nosoden",
        "spagyrik",
        "spagyrik_multiplex",
        "bachblueten_multiplex",
    ],
    "immunsystem_detailliert": [
        "immunsystem_angeboren",
        "immunsystem_angeboren_fein",
        "immunsystem_erworben",
        "immunsystem_erworben_fein",
        "immunsystem_autoimmun_fein",
        "immunsystem_zytokine_fein",
        "entzuendung",
        "bakterien",
        "bakterien_detailliert_fein",
        "viren",
        "viren_detailliert_fein",
        "parasiten",
        "parasiten_detailliert_fein",
        "pilze",
        "pilze_detailliert_fein",
        "schwermetalle",
        "schwermetalle_tox",
        "schwermetalle_detailliert_fein",
        "chemikalien_detailliert_fein",
        "umweltbelastungen_erweitert_fein",
        "wohnraumgifte_fein",
        "strahlung_tox",
        "strahlung_quellen_fein",
        "strahlung_symptome_fein",
        "toxine_symptome_fein",
        "toxine_remedies_multiplex",
        "entgiftung_leber_phase1",
        "entgiftung_leber_phase1_fein",
        "entgiftung_leber_phase2",
        "entgiftung_leber_phase2_fein",
        "entgiftung_leber_phase3",
        "entgiftung_leber_phase3_fein",
        "entgiftung_leber",
        "entgiftung_niere",
        "entgiftung_lymphe",
        "entgiftung_darm",
        "entgiftung_organe_fein",
        "entgiftung_symptome_fein",
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
        "mikronaehrstoffe",
        "orthomolekular_vitamine_fein",
        "orthomolekular_mineralien_fein",
        "orthomolekular_aminosauren_fein",
        "vitamine_detailliert_fein",
        "mineralien_spurenelemente_detailliert_fein",
        "aminosaeuren_detailliert_fein",
        "fettsaeuren_detailliert_fein",
        "orthomolekular_therapie_multiplex",
        "anti_infektions_remedies_multiplex",
        "immunstaerkung_remedies_multiplex",
        "entgiftung_remedies_multiplex",
        "verdauung_remedies_multiplex",
        "homoeopathie_klassisch",
        "homoeopathie_klassisch_potenzen",
        "homoeopathie_komplexmittel",
        "homoeopathie_isopathie",
        "homoeopathie_nosoden",
        "spagyrik",
        "spagyrik_multiplex",
        "bachblueten_multiplex",
    ],

    # --- NEUE PROFILE (Phase 4 - 2025-11-26) ---

    "zaehne_kiefer_detailliert": [
        # Dental-Fokus mit Odonton-Bezügen
        "zahnorgane",
        "odontone",
        # Toxin-Bezüge (Amalgam, Wurzelfüllungen)
        "schwermetalle",
        "schwermetalle_tox",
        # Meridian-Bezüge (Zahn-Meridian-Verbindungen)
        "meridiane",
        "tcm_punkte",
        # Entzündungen
        "entzuendung",
        "bakterien",
        # Remedies (erweitert)
        "homoeopathie_klassisch",
        "homoeopathie_nosoden",
        "spagyrik",
        "spagyrik_multiplex",
        "frequenz_rife_multiplex",
    ],

    "meridiane_tcm_detailliert": [
        # Vollständiges TCM-Meridiansystem
        "meridiane",
        "tcm_punkte",
        "tcm_punkte_extended",
        "tcm_full",
        "tcm_rezepturen",
        "tcm_rezepturen_potenzen",
        "extra_meridiane",
        # Energetische Ebenen
        "chakren",
        "chakren_erweitert",
        "chakren_full",
        # Organbezüge
        "entgiftung_leber",
        "entgiftung_niere",
        "verdauung_magen",
        "verdauung_dickdarm",
        "verdauung_duenndarm",
        "atmung_lunge",
        "kreislauf",
        # Remedies (erweitert)
        "homoeopathie_klassisch",
        "bachblueten_multiplex",
        "spagyrik",
        "frequenz_solfeggio_multiplex",
    ],

    "emf_stoerfelder_detailliert": [
        # EMF und Strahlung
        "strahlung_quellen_fein",
        "strahlung_tox",
        # Geopathie
        "geopathie_fein",
        # Betroffene Systeme
        "nervensystem_zns",
        # Entgiftung
        "detox",
        "entgiftung_lymphe",
        # Energetisch
        "chakren",
        "meridiane",
        # Schutz-Remedies (erweitert)
        "homoeopathie_klassisch",
        "bachblueten_multiplex",
        "spagyrik",
        "frequenz_solfeggio_multiplex",
        "frequenz_rife_multiplex",
    ],

    "hormone_stoffwechsel_detailliert": [
        # Hormonsystem
        "endokrin",
        # Stoffwechsel
        "mitochondrien",
        "verdauung_pankreas",
        # Kreislauf
        "kreislauf",
        # Entgiftung
        "entgiftung_leber",
        "entgiftung_niere",
        # Remedies (erweitert)
        "homoeopathie_klassisch",
        "homoeopathie_isopathie",
        "orthomolekular_therapie_multiplex",
        "orthomolekular_vitamine_fein",
        "orthomolekular_mineralien_fein",
        "spagyrik",
        "energie_remedies_multiplex",
    ],

    "psyche_emotion_detailliert": [
        # Psychosomatik
        "psychosomatik_fein",
        # Nervensystem
        "nervensystem_zns",
        # Energetisch
        "chakren",
        "chakren_erweitert",
        "meridiane",
        # Schlaf
        "schlaf",
        # Remedies (erweitert)
        "bachblueten_multiplex",
        "homoeopathie_klassisch",
        "spagyrik",
        "psyche_remedies_multiplex",
        "nerven_remedies_multiplex",
        "frequenz_solfeggio_multiplex",
    ],

    # --- OOREP Klassische Homöopathie (2432 Einzelmittel) ---
    "homeopathy_classical": [
        # OOREP Homöopathie - 2432 klassische Einzelmittel aus Kent, Boericke, Hahnemann
        "oorep_homeopathy_multiplex",
        # Ergänzende homöopathische Gruppen
        "homoeopathie_klassisch",
        "homoeopathie_klassisch_potenzen",
        "homoeopathie_nosoden",
        "homoeopathie_isopathie",
        "homoeopathie_komplexmittel",
        # Spagyrik als verwandtes System
        "spagyrik",
        "spagyrik_multiplex",
        # Bachblüten
        "bachblueten_multiplex",
    ],
    
    # =========================================================================
    # VERGIFTUNG KOMPLETT - Umfassendes Toxikologie-Profil (NEU 30.11.2025)
    # =========================================================================
    "vergiftung_komplett": [
        # Schwermetalle
        "schwermetalle",
        "schwermetalle_detailliert_fein",
        # Chemikalien & Umweltgifte
        "chemikalien_detailliert_fein",
        "umweltbelastungen_erweitert_fein",
        "wohnraumgifte_fein",
        "toxine_symptome_fein",
        # Strahlung & EMF
        "strahlung_tox",
        "strahlung_quellen_fein",
        "strahlung_symptome_fein",
        # Entgiftungsorgane
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
        # Pathogene (oft mit Vergiftung assoziiert)
        "bakterien",
        "bakterien_detailliert_fein",
        "viren",
        "viren_detailliert_fein",
        "parasiten",
        "parasiten_detailliert_fein",
        "pilze",
        "pilze_detailliert_fein",
        # Immunsystem (Reaktion auf Toxine)
        "immunsystem_angeboren",
        "immunsystem_angeboren_fein",
        "immunsystem_erworben",
        "immunsystem_erworben_fein",
        "immunsystem_autoimmun_fein",
        "entzuendung",
        # Nervensystem (oft betroffen bei Vergiftung)
        "nervensystem_zns",
        "nervensystem_zns_fein",
        "nervensystem_vegetativ",
        "nervensystem_neurotransmitter",
        "nerven_symptome_fein",
        "nerven_pathologien_fein",
        # Nährstoffe (Entgiftungsunterstützung)
        "mikronaehrstoffe",
        "orthomolekular_vitamine_fein",
        "orthomolekular_mineralien_fein",
        "orthomolekular_aminosauren_fein",
        "vitamine_detailliert_fein",
        "mineralien_spurenelemente_detailliert_fein",
        "aminosaeuren_detailliert_fein",
        # Remedies für Entgiftung
        "toxine_remedies_multiplex",
        "entgiftung_remedies_multiplex",
        "orthomolekular_therapie_multiplex",
        "anti_infektions_remedies_multiplex",
        # Klassische Homöopathie & Nosoden
        "homoeopathie_klassisch",
        "homoeopathie_klassisch_potenzen",
        "homoeopathie_nosoden",
        "homoeopathie_isopathie",
        # Spagyrik & Frequenzen
        "spagyrik",
        "spagyrik_multiplex",
        "frequenz_clark_multiplex",
        "frequenz_rife_multiplex",
    ],
    
    # =========================================================================
    # PESTIZIDE & HERBIZIDE - Dediziertes Profil (NEU 30.11.2025)
    # =========================================================================
    "pestizide_herbizide": [
        # Chemikalien & Umweltgifte
        "chemikalien_detailliert_fein",
        "umweltbelastungen_erweitert_fein",
        "wohnraumgifte_fein",
        "toxine_symptome_fein",
        # Entgiftung
        "entgiftung_leber",
        "entgiftung_leber_phase1",
        "entgiftung_leber_phase1_fein",
        "entgiftung_leber_phase2",
        "entgiftung_leber_phase2_fein",
        "entgiftung_niere",
        "entgiftung_darm",
        "entgiftung_lymphe",
        "entgiftung_organe_fein",
        # Nervensystem (oft betroffen)
        "nervensystem_zns",
        "nervensystem_vegetativ",
        "nervensystem_neurotransmitter",
        # Immunsystem
        "immunsystem_angeboren",
        "immunsystem_erworben",
        "entzuendung",
        # Nährstoffe
        "mikronaehrstoffe",
        "orthomolekular_vitamine_fein",
        "orthomolekular_mineralien_fein",
        # Remedies
        "toxine_remedies_multiplex",
        "entgiftung_remedies_multiplex",
        "homoeopathie_klassisch",
        "homoeopathie_nosoden",
        "spagyrik",
        "frequenz_clark_multiplex",
    ],
    
    # =========================================================================
    # MEDIKAMENTEN-TOXIZITÄT - Nebenwirkungen & Interaktionen (NEU 30.11.2025)
    # =========================================================================
    "medikamenten_toxizitaet": [
        # Entgiftungsorgane
        "entgiftung_leber",
        "entgiftung_leber_phase1",
        "entgiftung_leber_phase1_fein",
        "entgiftung_leber_phase2",
        "entgiftung_leber_phase2_fein",
        "entgiftung_leber_phase3",
        "entgiftung_leber_phase3_fein",
        "entgiftung_niere",
        "entgiftung_darm",
        "entgiftung_organe_fein",
        "entgiftung_symptome_fein",
        # Toxine
        "chemikalien_detailliert_fein",
        "toxine_symptome_fein",
        # Nervensystem (Nebenwirkungen)
        "nervensystem_zns",
        "nervensystem_vegetativ",
        "nervensystem_neurotransmitter",
        "nerven_symptome_fein",
        # Verdauung (GI-Nebenwirkungen)
        "verdauung_magen",
        "verdauung_duenndarm",
        "verdauung_dickdarm",
        "verdauung_mikrobiom",
        "verdauung_symptome_fein",
        # Immunsystem
        "immunsystem_angeboren",
        "immunsystem_erworben",
        "immunsystem_autoimmun_fein",
        # Nährstoffe (oft durch Medikamente depletiert)
        "mikronaehrstoffe",
        "orthomolekular_vitamine_fein",
        "orthomolekular_mineralien_fein",
        "vitamine_detailliert_fein",
        "mineralien_spurenelemente_detailliert_fein",
        # Remedies
        "toxine_remedies_multiplex",
        "entgiftung_remedies_multiplex",
        "homoeopathie_klassisch",
        "homoeopathie_nosoden",
        "homoeopathie_isopathie",
    ],
    
    # =========================================================================
    # NAHRUNGSMITTEL-INTOLERANZEN - Histamin, Gluten, Laktose (NEU 30.11.2025)
    # =========================================================================
    "nahrungsmittel_intoleranzen": [
        # Verdauung
        "verdauung_magen",
        "verdauung_duenndarm",
        "verdauung_duenndarm_fein",
        "verdauung_dickdarm",
        "verdauung_dickdarm_fein",
        "verdauung_mikrobiom",
        "verdauung_mikrobiom_fein",
        "verdauung_barriere",
        "verdauung_symptome_fein",
        "verdauung_pathologien_fein",
        # Immunsystem & Allergien
        "immunsystem_angeboren",
        "immunsystem_angeboren_fein",
        "immunsystem_erworben",
        "immunsystem_erworben_fein",
        "immunsystem_autoimmun_fein",
        "entzuendung",
        # Entgiftung
        "entgiftung_leber",
        "entgiftung_darm",
        "entgiftung_lymphe",
        # Nervensystem (Histamin-Reaktionen)
        "nervensystem_vegetativ",
        "nervensystem_neurotransmitter",
        # Haut (oft betroffen)
        "haut_fein",
        "haut_symptome_fein",
        # Nährstoffe
        "mikronaehrstoffe",
        "orthomolekular_vitamine_fein",
        "orthomolekular_mineralien_fein",
        "aminosaeuren_detailliert_fein",
        # Remedies
        "verdauung_remedies_multiplex",
        "allergie_remedies_multiplex",
        "homoeopathie_klassisch",
        "homoeopathie_nosoden",
        "spagyrik",
    ],
    
    # =========================================================================
    # MITOCHONDRIEN-DYSFUNKTION - Chronische Erschöpfung (NEU 30.11.2025)
    # =========================================================================
    "mitochondrien_dysfunktion": [
        # Energie & Stoffwechsel
        "stoffwechsel_energie",
        "stoffwechsel_kohlenhydrate",
        "stoffwechsel_fett",
        "stoffwechsel_protein",
        # Entgiftung (Mitochondrien-Schutz)
        "entgiftung_leber",
        "entgiftung_leber_phase1",
        "entgiftung_leber_phase2",
        # Schwermetalle (Mitochondrien-Toxine)
        "schwermetalle",
        "schwermetalle_detailliert_fein",
        # Toxine
        "chemikalien_detailliert_fein",
        "umweltbelastungen_erweitert_fein",
        # Nervensystem
        "nervensystem_zns",
        "nervensystem_vegetativ",
        "nervensystem_neurotransmitter",
        # Immunsystem
        "immunsystem_angeboren",
        "immunsystem_erworben",
        "entzuendung",
        # Nährstoffe (Mitochondrien-Kofaktoren)
        "mikronaehrstoffe",
        "orthomolekular_vitamine_fein",
        "orthomolekular_mineralien_fein",
        "orthomolekular_aminosauren_fein",
        "vitamine_detailliert_fein",
        "mineralien_spurenelemente_detailliert_fein",
        "aminosaeuren_detailliert_fein",
        "fettsaeuren_detailliert_fein",
        # Müdigkeit & Schlaf
        "muedigkeit_chronisch",
        "schlafstoerungen",
        "schlafstoerungen_fein",
        # Remedies
        "orthomolekular_therapie_multiplex",
        "energie_remedies_multiplex",
        "homoeopathie_klassisch",
        "spagyrik",
    ],
    
    # =========================================================================
    # BINDEGEWEBE & FASZIEN - Systemische Belastungen (NEU 30.11.2025)
    # =========================================================================
    "bindegewebe_faszien": [
        # Bewegungsapparat
        "bewegungsapparat_muskeln",
        "bewegungsapparat_muskeln_fein",
        "bewegungsapparat_gelenke",
        "bewegungsapparat_gelenke_fein",
        "bewegungsapparat_sehnen",
        "bewegungsapparat_baender",
        # Wirbelsäule
        "wirbelsaeule",
        "wirbelsaeule_fein",
        "wirbelsaeule_hws",
        "wirbelsaeule_bws",
        "wirbelsaeule_lws",
        # Schmerz
        "schmerz_muskel",
        "schmerz_gelenk",
        "schmerz_ruecken",
        # Entgiftung (Matrix-Reinigung)
        "entgiftung_lymphe",
        "entgiftung_darm",
        "entgiftung_haut",
        # Immunsystem
        "immunsystem_angeboren",
        "immunsystem_erworben",
        "immunsystem_autoimmun_fein",
        "entzuendung",
        # Nährstoffe (Kollagen-Synthese)
        "mikronaehrstoffe",
        "orthomolekular_vitamine_fein",
        "orthomolekular_mineralien_fein",
        "aminosaeuren_detailliert_fein",
        # Remedies
        "bewegung_remedies_multiplex",
        "schmerz_remedies_multiplex",
        "homoeopathie_klassisch",
        "spagyrik",
    ],
}

def get_groups_for_profile(profile_name: str) -> Optional[List[str]]:
    """
    Gibt die Gruppenliste für ein Profil zurück, wenn es in der Registry existiert.
    Gibt None zurück, wenn das Profil hier nicht bekannt ist (dann Fallback auf main.py legacy).
    
    WICHTIG: Nutzt jetzt die zentrale Profil-Synchronisierung aus core/profile_sync!
    
    Unterstützt auch:
    - B.A.T.-Profile (bat_akut, bat_bakterien, etc.)
    - Remedy-Hersteller-Profile (heel_remedies, nutramedix_remedies)
    """
    # PRIORITÄT 1: Zentrale Profil-Synchronisierung (MASTER)
    if _USE_SYNC:
        sync_groups = _sync_get_groups(profile_name)
        if sync_groups:
            return sync_groups
    
    # PRIORITÄT 2: Legacy-Profile in dieser Datei (Fallback)
    if profile_name in _PROFILES_DATA:
        return _PROFILES_DATA.get(profile_name)
    
    # PRIORITÄT 3: B.A.T.-Profile
    if profile_name.startswith('bat_'):
        try:
            from core.subgroups.bat_groups import get_bat_profile_groups
            bat_groups = get_bat_profile_groups(profile_name)
            if bat_groups:
                return bat_groups
        except ImportError:
            pass
    
    # PRIORITÄT 4: Remedy-Hersteller-Profile
    if profile_name in ['heel_remedies', 'nutramedix_remedies']:
        # Diese Profile nutzen spezielle Marker-Gruppen für den Remedy-Service
        # Der Marker wird vom Remedy-Service erkannt und als Kategorie-Filter verwendet
        return [f'__remedy_category_{profile_name}__']
    
    return None


def validate_profile_groups(
    target_groups: List[str],
    available_groups: set[str]
) -> List[str]:
    """
    Prüft, ob alle Gruppen in target_groups auch in available_groups enthalten sind.
    Gibt eine Liste der fehlenden Gruppen zurück.
    """
    missing = []
    for g in target_groups:
        if g not in available_groups:
            missing.append(g)
    return missing
